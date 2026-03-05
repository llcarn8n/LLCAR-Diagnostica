#!/usr/bin/env python3
"""Extract OCR text from all chunk_images using EasyOCR on dual-GPU.

Two parallel worker processes: GPU 0 handles even-indexed images, GPU 1 handles odd-indexed.
Saves extracted text into chunk_images.ocr_text column.

Usage:
  # Run both GPUs (spawns two worker processes):
  python scripts/ocr_images.py

  # Run as a single worker (called internally):
  python scripts/ocr_images.py --worker --gpu 0
  python scripts/ocr_images.py --worker --gpu 1

  # Other options:
  python scripts/ocr_images.py --force       # re-OCR already processed images
  python scripts/ocr_images.py --limit 10    # process only 10 images (for testing)
  python scripts/ocr_images.py --worker --gpu 0 --limit 5   # test on GPU 0 only
"""

import sqlite3
import sys
import io
import os
import time
import argparse
import subprocess
from pathlib import Path

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

DB_PATH = "knowledge-base/kb.db"
DB_COMMIT_EVERY = 5  # commit every 5 images to keep WAL short


def ensure_ocr_text_column(conn):
    c = conn.cursor()
    c.execute("PRAGMA table_info(chunk_images)")
    cols = [row[1] for row in c.fetchall()]
    if "ocr_text" not in cols:
        c.execute("ALTER TABLE chunk_images ADD COLUMN ocr_text TEXT")
        conn.commit()
        print("[DB] Added ocr_text column to chunk_images")
    else:
        print("[DB] ocr_text column exists")


def get_images_to_process(force=False, limit=0):
    conn = sqlite3.connect(DB_PATH, timeout=60)
    conn.execute("PRAGMA journal_mode=WAL")
    c = conn.cursor()
    ensure_ocr_text_column(conn)
    if force:
        c.execute("SELECT DISTINCT image_path FROM chunk_images ORDER BY image_path")
    else:
        c.execute(
            "SELECT DISTINCT image_path FROM chunk_images "
            "WHERE ocr_text IS NULL OR ocr_text = '' "
            "ORDER BY image_path"
        )
    images = [row[0] for row in c.fetchall()]
    conn.close()
    if limit > 0:
        images = images[:limit]
    return images


EASYOCR_LANGS = ["ch_sim", "en"]  # ch_sim is NOT compatible with ru


def init_easyocr(gpu_id):
    """Initialize EasyOCR on the specified GPU (zh+en)."""
    # EasyOCR uses CUDA_VISIBLE_DEVICES to select GPU
    os.environ["CUDA_VISIBLE_DEVICES"] = str(gpu_id)
    import easyocr
    reader = easyocr.Reader(
        EASYOCR_LANGS,
        gpu=True,
        verbose=False,
    )
    print(f"[GPU {gpu_id}] EasyOCR initialized ({'+'.join(EASYOCR_LANGS)})")
    return reader


def predownload_easyocr_models():
    """Download EasyOCR models once (CPU) before spawning parallel workers."""
    print("Pre-downloading EasyOCR models (CPU)...")
    import easyocr
    # CPU-only init just to trigger model download
    easyocr.Reader(EASYOCR_LANGS, gpu=False, verbose=True)
    print("Models ready.")


def ocr_image(reader, image_path):
    """Run EasyOCR on one image. Returns extracted text."""
    try:
        result = reader.readtext(str(image_path), detail=1)
        if not result:
            return ""
        lines = []
        for detection in result:
            text = detection[1]
            conf = detection[2]
            if conf >= 0.4 and text.strip():
                lines.append(text.strip())
        return "\n".join(lines)
    except Exception as e:
        print(f"  EasyOCR error on {image_path}: {e}")
        return None  # None = error, "" = no text found


def resolve_path(img_path):
    """Resolve image path relative to project root."""
    p = Path(img_path)
    if p.exists():
        return p
    p2 = Path("knowledge-base") / img_path
    if p2.exists():
        return p2
    return None


def run_worker(gpu_id, all_images, force=False):
    """
    Worker: process images assigned to this GPU.
    GPU 0 → images at even indices (0, 2, 4, ...)
    GPU 1 → images at odd indices (1, 3, 5, ...)
    """
    my_images = [img for i, img in enumerate(all_images) if i % 2 == gpu_id]
    total = len(my_images)
    print(f"\n[GPU {gpu_id}] Assigned {total} images")

    reader = init_easyocr(gpu_id)

    conn = sqlite3.connect(DB_PATH, timeout=60)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=60000")

    processed = 0
    skipped = 0
    errors = 0
    empty = 0
    total_chars = 0
    commit_count = 0
    start_time = time.time()

    for i, img_path in enumerate(my_images):
        full_path = resolve_path(img_path)
        if full_path is None:
            print(f"  [GPU {gpu_id}] [{i+1}/{total}] SKIP not found: {img_path}")
            skipped += 1
            continue

        ocr_text = ocr_image(reader, full_path)

        if ocr_text is None:
            # Error during OCR — skip, count as error
            errors += 1
            continue

        if not ocr_text:
            empty += 1

        conn.execute(
            "UPDATE chunk_images SET ocr_text = ? WHERE image_path = ?",
            (ocr_text, img_path),
        )
        processed += 1
        total_chars += len(ocr_text)
        commit_count += 1

        if commit_count >= DB_COMMIT_EVERY:
            conn.commit()
            commit_count = 0

        elapsed = time.time() - start_time
        rate = processed / elapsed if elapsed > 0 else 0
        eta = (total - i - 1) / rate if rate > 0 else 0
        preview = ocr_text[:50].replace("\n", " ") if ocr_text else "(no text)"
        print(
            f"  [GPU {gpu_id}] [{i+1}/{total}] {rate:.1f}img/s ETA {eta/60:.0f}m | "
            f"{len(ocr_text)}ch | {preview}"
        )

    conn.commit()
    conn.close()

    elapsed = time.time() - start_time
    print(f"\n[GPU {gpu_id}] DONE: {processed} processed, {empty} empty, "
          f"{skipped} skipped, {errors} errors | {total_chars:,} chars | "
          f"{elapsed/60:.1f}min ({elapsed/max(processed,1):.1f}s/img)")


def run_dual_gpu(force=False, limit=0):
    """Launch two worker processes (GPU 0 and GPU 1) in parallel."""
    all_images = get_images_to_process(force=force, limit=limit)
    total = len(all_images)
    if total == 0:
        print("No images to process. Use --force to re-process already completed images.")
        return

    print(f"Total images: {total}")
    print(f"GPU 0: {(total + 1) // 2} images (even indices)")
    print(f"GPU 1: {total // 2} images (odd indices)")
    print("Launching two worker processes...")

    script = os.path.abspath(__file__)
    base_cmd = [sys.executable, script, "--worker"]
    if force:
        base_cmd.append("--force")
    if limit > 0:
        base_cmd.extend(["--limit", str(limit)])

    p0 = subprocess.Popen(base_cmd + ["--gpu", "0"],
                          stdout=sys.stdout, stderr=sys.stderr)
    p1 = subprocess.Popen(base_cmd + ["--gpu", "1"],
                          stdout=sys.stdout, stderr=sys.stderr)

    p0.wait()
    p1.wait()

    # Final stats
    conn = sqlite3.connect(DB_PATH, timeout=30)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM chunk_images")
    total_imgs = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM chunk_images WHERE ocr_text IS NOT NULL AND ocr_text != ''")
    with_text = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM chunk_images WHERE ocr_text IS NULL OR ocr_text = ''")
    without_text = c.fetchone()[0]
    conn.close()

    print(f"\n{'='*50}")
    print(f"OCR COMPLETE (dual-GPU)")
    print(f"{'='*50}")
    print(f"Total images:  {total_imgs}")
    print(f"With text:     {with_text}")
    print(f"Empty/missing: {without_text}")


def main():
    parser = argparse.ArgumentParser(description="OCR chunk_images with EasyOCR on dual-GPU")
    parser.add_argument("--worker", action="store_true", help="Run as worker (internal use)")
    parser.add_argument("--gpu", type=int, default=0, help="GPU index for worker mode (0 or 1)")
    parser.add_argument("--force", action="store_true", help="Re-OCR images that already have text")
    parser.add_argument("--limit", type=int, default=0, help="Process only N images total (0=all)")
    args = parser.parse_args()

    if args.worker:
        # Worker mode: process images assigned to this GPU
        all_images = get_images_to_process(force=args.force, limit=args.limit)
        run_worker(gpu_id=args.gpu, all_images=all_images, force=args.force)
    else:
        # Coordinator mode: launch two workers
        run_dual_gpu(force=args.force, limit=args.limit)


if __name__ == "__main__":
    main()
