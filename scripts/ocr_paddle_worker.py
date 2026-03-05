#!/usr/bin/env python3
"""PaddleOCR worker for chunk_images. Runs under ocr_env (Python 3.11 + PaddlePaddle GPU).

Usage (from project root, using ocr_env):
  ocr_env/Scripts/python.exe scripts/ocr_paddle_worker.py --gpu 0
  ocr_env/Scripts/python.exe scripts/ocr_paddle_worker.py --gpu 1

Each worker processes images assigned to it by index parity:
  GPU 0 -> even-indexed images (0, 2, 4, ...)
  GPU 1 -> odd-indexed images (1, 3, 5, ...)

Both workers write to the same DB using WAL mode (safe for concurrent writes).
"""

import os
import sys
import io
import sqlite3
import json
import time
import argparse
from pathlib import Path

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Skip network check
os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"

DB_PATH = "knowledge-base/kb.db"
DB_COMMIT_EVERY = 5


def init_paddle_ocr(gpu_id):
    from paddleocr import PaddleOCR
    ocr = PaddleOCR(
        lang="ch",
        use_textline_orientation=True,
        device=f"gpu:{gpu_id}",
        text_det_thresh=0.3,
        text_det_box_thresh=0.5,
    )
    print(f"[GPU {gpu_id}] PaddleOCR initialized (lang=ch, gpu:{gpu_id})")
    return ocr


def ocr_image(ocr, image_path):
    """Run PaddleOCR on one image using predict(). Returns text string or None on error."""
    try:
        results = ocr.predict(str(image_path))
        lines = []
        for res in results:
            # res is a dict with 'rec_texts' and 'rec_scores'
            texts = res.get("rec_texts", [])
            scores = res.get("rec_scores", [])
            for text, score in zip(texts, scores):
                if score >= 0.5 and text.strip():
                    lines.append(text.strip())
        return "\n".join(lines)
    except Exception as e:
        print(f"  OCR error on {image_path}: {e}")
        return None


def resolve_path(img_path):
    p = Path(img_path)
    if p.exists():
        return p
    p2 = Path("knowledge-base") / img_path
    if p2.exists():
        return p2
    return None


def main():
    parser = argparse.ArgumentParser(description="PaddleOCR dual-GPU worker")
    parser.add_argument("--gpu", type=int, default=0, choices=[0, 1], help="GPU index (0 or 1)")
    parser.add_argument("--force", action="store_true", help="Re-OCR images that already have text")
    parser.add_argument("--limit", type=int, default=0, help="Limit total images (for testing)")
    args = parser.parse_args()

    gpu_id = args.gpu

    # Get image list
    conn = sqlite3.connect(DB_PATH, timeout=60)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=60000")

    # Ensure column exists
    c = conn.cursor()
    c.execute("PRAGMA table_info(chunk_images)")
    cols = [r[1] for r in c.fetchall()]
    if "ocr_text" not in cols:
        c.execute("ALTER TABLE chunk_images ADD COLUMN ocr_text TEXT")
        conn.commit()
        print("[DB] Added ocr_text column")

    if args.force:
        c.execute("SELECT DISTINCT image_path FROM chunk_images ORDER BY image_path")
    else:
        c.execute(
            "SELECT DISTINCT image_path FROM chunk_images "
            "WHERE ocr_text IS NULL OR ocr_text = '' "
            "ORDER BY image_path"
        )
    all_images = [row[0] for row in c.fetchall()]

    if args.limit > 0:
        all_images = all_images[:args.limit]

    # This worker's images: by index parity
    my_images = [img for i, img in enumerate(all_images) if i % 2 == gpu_id]
    total = len(my_images)

    if total == 0:
        print(f"[GPU {gpu_id}] No images to process.")
        conn.close()
        return

    print(f"[GPU {gpu_id}] Total images assigned: {total}")

    # Initialize OCR
    ocr = init_paddle_ocr(gpu_id)

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

        text = ocr_image(ocr, full_path)
        if text is None:
            errors += 1
            continue

        if not text:
            empty += 1

        conn.execute(
            "UPDATE chunk_images SET ocr_text = ? WHERE image_path = ?",
            (text, img_path),
        )
        processed += 1
        total_chars += len(text)
        commit_count += 1

        if commit_count >= DB_COMMIT_EVERY:
            conn.commit()
            commit_count = 0

        elapsed = time.time() - start_time
        rate = processed / elapsed if elapsed > 0 else 0
        eta = (total - i - 1) / rate if rate > 0 else 0
        preview = text[:50].replace("\n", " ") if text else "(no text)"
        print(
            f"  [GPU {gpu_id}] [{i+1}/{total}] {rate:.1f}img/s ETA {eta/60:.0f}m | "
            f"{len(text)}ch | {preview}"
        )

    conn.commit()
    conn.close()

    elapsed = time.time() - start_time
    print(f"\n[GPU {gpu_id}] DONE")
    print(f"  Processed: {processed}/{total}")
    print(f"  With text: {processed - empty}")
    print(f"  Empty:     {empty}")
    print(f"  Skipped:   {skipped}")
    print(f"  Errors:    {errors}")
    print(f"  Chars:     {total_chars:,}")
    print(f"  Time:      {elapsed/60:.1f}min ({elapsed/max(processed,1):.1f}s/img)")


if __name__ == "__main__":
    main()
