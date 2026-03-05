#!/usr/bin/env python3
"""
LLCAR Diagnostica — Image Captioning with Qwen2.5-VL-7B (Phase 2).

Reads images from the `chunk_images` table (populated by link_images.py),
generates detailed automotive captions using Qwen2.5-VL-7B, and writes them
back to the database.

Model requirements:
  - Qwen/Qwen2.5-VL-7B-Instruct (~17 GB VRAM)
  - Runs comfortably on a single RTX 3090 (24 GB) in BF16

Usage:
    python scripts/caption_images.py \
        --db-path knowledge-base/kb.db \
        --device cuda:0 \
        --batch-size 4 \
        --verbose

    # Dry run (show first N captions without writing)
    python scripts/caption_images.py --dry-run --limit 5

    # Process only un-captioned images from a specific document source
    python scripts/caption_images.py --source pdf_l9_ru

Outputs:
    - Updates chunk_images.caption in SQLite
    - Optional: writes captions to a JSONL log file (--output-log)

The script is idempotent: images with existing captions are skipped unless
--force is given.
"""
from __future__ import annotations

import argparse
import base64
import logging
import sqlite3
import sys
import time
from io import BytesIO
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("caption_images")


# ===========================================================================
# Configuration
# ===========================================================================

MODEL_ID = "Qwen/Qwen2.5-VL-7B-Instruct"

# Captioning prompt — tuned for automotive technical documentation
CAPTION_PROMPT = (
    "This image is from an automotive owner's manual or technical service document "
    "for a Li Auto (理想汽车) vehicle.\n\n"
    "Describe the image in detail. Include:\n"
    "- What type of image it is (diagram, photo, table, warning label, wiring schematic, etc.)\n"
    "- All visible text, part numbers, labels, and numerical values\n"
    "- Names of components, systems, or assemblies shown\n"
    "- Any procedures, warnings, or safety information depicted\n"
    "- Physical relationships between components if visible\n\n"
    "Respond in English. Be precise and technical."
)

# Max tokens per caption (can be overridden via --max-tokens CLI arg)
MAX_NEW_TOKENS = 512

# SQLite batch commit size — keep small to avoid locking DB for too long
# (with 20s inference per image, DB_COMMIT_EVERY=50 means ~16min lock → breaks concurrent writers)
DB_COMMIT_EVERY = 5


# ===========================================================================
# Model loading
# ===========================================================================

def load_model(device: str) -> tuple[Any, Any]:
    """
    Load Qwen2.5-VL-7B-Instruct and its processor.

    Uses BF16 precision and device_map for automatic placement.
    Returns (model, processor).
    """
    import torch  # noqa: PLC0415
    from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration  # noqa: PLC0415

    log.info("Loading Qwen2.5-VL-7B-Instruct on %s …", device)
    t0 = time.time()

    processor = AutoProcessor.from_pretrained(
        MODEL_ID,
        trust_remote_code=True,
        use_fast=False,  # fast processor can segfault on Windows with large batches
    )

    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        MODEL_ID,
        torch_dtype=torch.bfloat16,
        device_map=device,
        trust_remote_code=True,
        low_cpu_mem_usage=True,  # stream weights directly to GPU, avoids ~15GB CPU RAM spike
    )
    model.eval()

    elapsed = time.time() - t0
    vram = 0.0
    if torch.cuda.is_available():
        dev_idx = int(device.split(":")[-1]) if ":" in device else 0
        vram = torch.cuda.memory_allocated(dev_idx) / 1024 ** 3
    log.info(
        "Qwen2.5-VL-7B loaded in %.1f s  (VRAM used: %.1f GB)",
        elapsed, vram,
    )
    return model, processor


# ===========================================================================
# Inference helpers
# ===========================================================================

def image_to_base64(path: Path) -> str | None:
    """Read image from disk and encode as base64 data URL."""
    try:
        with open(path, "rb") as f:
            data = f.read()
        b64 = base64.b64encode(data).decode("ascii")
        # Detect JPEG vs PNG by magic bytes
        mime = "image/jpeg" if data[:2] == b"\xff\xd8" else "image/png"
        return f"data:{mime};base64,{b64}"
    except Exception as exc:
        log.warning("Could not read image %s: %s", path, exc)
        return None


def caption_single(
    model: Any,
    processor: Any,
    image_path: Path,
    device: str,
    max_side: int = 1536,
    max_new_tokens: int = MAX_NEW_TOKENS,
) -> str | None:
    """
    Generate a caption for a single image.

    Returns caption string, or None on failure.
    max_side: resize image so longest side <= this value before inference.
    """
    import torch  # noqa: PLC0415
    from PIL import Image as PILImage  # noqa: PLC0415

    try:
        pil_image = PILImage.open(image_path).convert("RGB")
    except Exception as exc:
        log.warning("Could not read image %s: %s", image_path, exc)
        return None

    # Downscale large images to avoid OOM (full-page scans can be 3K×4K+)
    w, h = pil_image.size
    if max(w, h) > max_side:
        scale = max_side / max(w, h)
        pil_image = pil_image.resize(
            (int(w * scale), int(h * scale)),
            PILImage.LANCZOS,
        )

    # Use a simple image placeholder in messages — the actual image pixels
    # come from the images= argument to processor(), not from a base64 URL.
    # Passing base64 of a 3K×4K image would consume ~50 MB RAM unnecessarily.
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image"},
                {"type": "text", "text": CAPTION_PROMPT},
            ],
        }
    ]

    try:
        text = processor.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )

        inputs = processor(
            text=[text],
            images=[pil_image],
            return_tensors="pt",
            padding=True,
        ).to(device)

        with torch.no_grad():
            output_ids = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=False,
            )

        # Decode only newly generated tokens
        input_len = inputs["input_ids"].shape[1]
        generated = output_ids[0, input_len:]
        caption = processor.decode(generated, skip_special_tokens=True).strip()
        return caption or None

    except Exception as exc:
        log.error("Inference failed for %s: %s", image_path, exc)
        return None


def caption_batch(
    model: Any,
    processor: Any,
    rows: list[tuple[int, str]],  # [(chunk_image_id, image_path), ...]
    project_root: Path,
    device: str,
    max_new_tokens: int = MAX_NEW_TOKENS,
) -> list[tuple[int, str | None]]:
    """
    Caption a batch of images.

    Returns list of (chunk_image_id, caption_or_none).
    Falls back to per-image inference if batch fails.
    """
    results: list[tuple[int, str | None]] = []

    for row_id, img_rel_path in rows:
        img_abs = project_root / img_rel_path
        if not img_abs.exists():
            log.warning("Image not found on disk: %s", img_abs)
            results.append((row_id, None))
            continue

        caption = caption_single(model, processor, img_abs, device,
                                 max_new_tokens=max_new_tokens)
        results.append((row_id, caption))

    return results


# ===========================================================================
# Database helpers
# ===========================================================================

def fetch_uncaptioned(
    conn: sqlite3.Connection,
    source_filter: list[str] | None,
    limit: int | None,
    force: bool,
) -> list[tuple[int, str, str, str, str]]:
    """
    Return (id, image_path, chunk_id, chunk_title, chunk_source) rows that need captioning.

    If force=False: only rows with caption IS NULL.
    If source_filter is given: only images for chunks from those sources.
    """
    sql = """
        SELECT ci.id, ci.image_path, ci.chunk_id,
               COALESCE(c.title, '') AS chunk_title,
               COALESCE(c.source, '') AS chunk_source
        FROM chunk_images ci
        LEFT JOIN chunks c ON c.id = ci.chunk_id
    """
    params: list[Any] = []

    where: list[str] = []
    if not force:
        where.append("ci.caption IS NULL")
    if source_filter:
        placeholders = ",".join("?" * len(source_filter))
        where.append(f"c.source IN ({placeholders})")
        params.extend(source_filter)

    if where:
        sql += " WHERE " + " AND ".join(where)

    sql += " ORDER BY ci.id"

    if limit:
        sql += f" LIMIT {limit}"

    cur = conn.execute(sql, params)
    return cur.fetchall()


def write_caption(
    conn: sqlite3.Connection,
    row_id: int,
    caption: str,
    model_id: str,
) -> None:
    """Update caption for a chunk_images row."""
    conn.execute(
        "UPDATE chunk_images SET caption = ? WHERE id = ?",
        (caption, row_id),
    )


# ===========================================================================
# Main processing loop
# ===========================================================================

def run_captioning(
    db_path: Path,
    project_root: Path,
    device: str,
    batch_size: int,
    source_filter: list[str] | None,
    limit: int | None,
    force: bool,
    dry_run: bool,
    output_log: Path | None,
    output_md: Path | None,
    verbose: bool,
    max_new_tokens: int = MAX_NEW_TOKENS,
) -> dict[str, int]:
    """
    Main captioning pipeline.

    Returns stats dict.
    """
    import json  # noqa: PLC0415

    stats = dict(
        total_rows=0,
        captioned=0,
        failed=0,
        skipped=0,
    )

    conn = sqlite3.connect(str(db_path), timeout=120, isolation_level=None)  # autocommit
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")

    rows = fetch_uncaptioned(conn, source_filter, limit, force)
    stats["total_rows"] = len(rows)

    if not rows:
        log.info("No uncaptioned images to process.")
        conn.close()
        return stats

    log.info("Images to caption: %d", len(rows))

    if dry_run:
        log.info("DRY RUN — loading model but not writing to DB.")

    # Load model
    model, processor = load_model(device)

    log_fh = None
    if output_log:
        log_fh = open(output_log, "a", encoding="utf-8")

    # Collect (image_path, chunk_title, chunk_source, caption) for markdown report
    md_entries: list[tuple[str, str, str, str]] = []

    t_start = time.time()

    for i in range(0, len(rows), batch_size):
        batch = rows[i : i + batch_size]
        # batch: list of (id, image_path, chunk_id, chunk_title, chunk_source)

        # Skip rows already captioned by a concurrent process
        fresh_batch = []
        for r in batch:
            existing = conn.execute(
                "SELECT caption FROM chunk_images WHERE id = ?", (r[0],)
            ).fetchone()
            if existing and existing[0] is not None:
                stats["skipped"] += 1
            else:
                fresh_batch.append(r)

        if not fresh_batch:
            done = min(i + batch_size, len(rows))
            elapsed = time.time() - t_start
            rate = (stats["captioned"] + stats["skipped"]) / elapsed if elapsed > 0 else 0
            eta = (len(rows) - done) / rate if rate > 0 else 0
            log.info(
                "  %d/%d  captioned=%d  skipped=%d  failed=%d  %.2f img/s  ETA %.0fs",
                done, len(rows), stats["captioned"], stats["skipped"], stats["failed"], rate, eta,
            )
            continue

        batch_pairs = [(r[0], r[1]) for r in fresh_batch]
        results = caption_batch(model, processor, batch_pairs, project_root, device,
                                max_new_tokens=max_new_tokens)

        for (row_id, caption) in results:
            row_meta = next((r for r in fresh_batch if r[0] == row_id), None)
            img_path = row_meta[1] if row_meta else ""
            chunk_id = row_meta[2] if row_meta else ""
            chunk_title = row_meta[3] if row_meta else ""
            chunk_source = row_meta[4] if row_meta else ""

            if caption:
                if not dry_run:
                    write_caption(conn, row_id, caption, MODEL_ID)
                stats["captioned"] += 1

                if log_fh:
                    log_fh.write(json.dumps({
                        "id": row_id,
                        "chunk_id": chunk_id,
                        "image_path": img_path,
                        "caption": caption,
                    }, ensure_ascii=False) + "\n")

                if output_md:
                    md_entries.append((img_path, chunk_title, chunk_source, caption))
            else:
                stats["failed"] += 1

        # autocommit mode: no explicit commit needed (isolation_level=None)

        done = min(i + batch_size, len(rows))
        elapsed = time.time() - t_start
        rate = done / elapsed if elapsed > 0 else 0
        eta = (len(rows) - done) / rate if rate > 0 else 0
        log.info(
            "  %d/%d  captioned=%d  skipped=%d  failed=%d  %.2f img/s  ETA %.0fs",
            done, len(rows), stats["captioned"], stats["skipped"], stats["failed"], rate, eta,
        )

    conn.close()
    if log_fh:
        log_fh.close()

    # Write markdown report
    if output_md and md_entries:
        import datetime  # noqa: PLC0415
        output_md.parent.mkdir(parents=True, exist_ok=True)
        with open(output_md, "w", encoding="utf-8") as mf:
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            mf.write(f"# Image Caption Report\n\n")
            mf.write(f"Generated: {now}  \n")
            mf.write(f"Model: `{MODEL_ID}`  \n")
            mf.write(f"Total captioned: {len(md_entries)}\n\n")
            mf.write("---\n\n")
            for idx, (img_path, title, source, cap) in enumerate(md_entries, 1):
                mf.write(f"## {idx}. {title or img_path}\n\n")
                if source:
                    mf.write(f"**Source**: `{source}`  \n")
                mf.write(f"**Image**: `{img_path}`  \n\n")
                mf.write(f"{cap}\n\n")
                mf.write("---\n\n")
        log.info("Markdown report written: %s (%d entries)", output_md, len(md_entries))

    elapsed_total = time.time() - t_start
    log.info("Done. Total: %.1f s  (%.2f img/s)", elapsed_total,
             stats["captioned"] / elapsed_total if elapsed_total > 0 else 0)

    return stats


# ===========================================================================
# Main
# ===========================================================================

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Caption KB images using Qwen2.5-VL-7B-Instruct.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--db-path",
        default="knowledge-base/kb.db",
        help="Path to kb.db.",
    )
    parser.add_argument(
        "--device",
        default="cuda:0",
        help="CUDA device for Qwen2.5-VL-7B.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=1,
        help="Images per inference pass (keep at 1 to avoid OOM).",
    )
    parser.add_argument(
        "--source",
        action="append",
        dest="sources",
        default=None,
        metavar="SOURCE",
        help="Process only images from this source. Repeat for multiple: --source a --source b.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Max images to process (useful for testing).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-caption images that already have a caption.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run inference but do not write captions to DB.",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=MAX_NEW_TOKENS,
        help="Max new tokens per caption (default 512; use 128 for ~4x speed).",
    )
    parser.add_argument(
        "--output-log",
        default=None,
        help="Optional JSONL file to append generated captions.",
    )
    parser.add_argument(
        "--output-md",
        default=None,
        help="Optional Markdown file to write caption report (image + chunk + caption).",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Debug logging.",
    )
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    project_root = Path(__file__).resolve().parent.parent
    db_path = project_root / args.db_path

    if not db_path.exists():
        log.error("kb.db not found at %s — run build_kb.py first.", db_path)
        sys.exit(1)

    log.info("=" * 60)
    log.info("  LLCAR Image Captioning — Qwen2.5-VL-7B")
    log.info("  DB:     %s", db_path)
    log.info("  Device: %s", args.device)
    log.info("  Model:  %s", MODEL_ID)
    if args.dry_run:
        log.info("  *** DRY RUN — no DB writes ***")
    log.info("=" * 60)

    output_log = Path(args.output_log) if args.output_log else None
    output_md = Path(args.output_md) if args.output_md else None

    stats = run_captioning(
        db_path=db_path,
        project_root=project_root,
        device=args.device,
        batch_size=args.batch_size,
        source_filter=args.sources,  # list or None
        limit=args.limit,
        force=args.force,
        dry_run=args.dry_run,
        output_log=output_log,
        output_md=output_md,
        verbose=args.verbose,
        max_new_tokens=args.max_tokens,
    )

    log.info(
        "Results: total=%d captioned=%d failed=%d",
        stats["total_rows"], stats["captioned"], stats["failed"],
    )


if __name__ == "__main__":
    main()
