#!/usr/bin/env python3
"""
LLCAR Diagnostica — Image Linker (Phase 2).

Parses MinerU content_list.json files and links extracted images to KB chunks
in the `chunk_images` table.  Creates 640px-wide thumbnail JPEG files alongside
the originals.

Usage:
    python scripts/link_images.py --db-path knowledge-base/kb.db \
        --mineru-dir mineru-output --verbose

The script is idempotent: duplicate image paths are skipped via INSERT OR IGNORE.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sqlite3
import sys
import time
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
log = logging.getLogger("link_images")


# ===========================================================================
# Configuration — MinerU folder → SQLite source mapping
# ===========================================================================

# Maps the MinerU document folder name to its corresponding SQLite source name.
# page_offset: add to MinerU 0-based page_idx to get SQLite 1-based page number.
MINERU_SOURCE_MAP: dict[str, dict[str, Any]] = {
    "Lixiang L9 Руководство пользователя": {
        "source": "pdf_l9_ru",
        "vehicle": "l9",
        "language": "ru",
        "content_dir": "auto",
        "page_offset": 1,   # MinerU 0-based → SQLite 1-based
    },
    "Lixiang L9 Owner's Manual": {
        "source": "mineru_l9_zh_owners",
        "vehicle": "l9",
        "language": "zh",
        "content_dir": "auto",
        "page_offset": 1,
    },
    "Lixiang L7 Owner's Manual": {
        # 'auto' dir has images; 'hybrid_auto' dir does not.
        "source": "mineru_l7_zh_owners",
        "vehicle": "l7",
        "language": "zh",
        "content_dir": "auto",
        "page_offset": 1,
    },
    "Li L9英文版": {
        "source": "mineru_l9_en",
        "vehicle": "l9",
        "language": "en",
        "content_dir": "auto",
        "page_offset": 1,
    },
    "240322-Li-L9-Configuration": {
        # English spec sheet (18 pages) not currently in kb.db — skip.
        "source": None,
        "vehicle": "l9",
        "language": "en",
        "content_dir": "auto",
        "page_offset": 1,
    },
}

THUMBNAIL_WIDTH = 640   # pixels; height auto-scales to keep aspect ratio


# ===========================================================================
# Thumbnail helper
# ===========================================================================

def make_thumbnail(src: Path, dst: Path, max_width: int = THUMBNAIL_WIDTH) -> bool:
    """
    Create a JPEG thumbnail at *dst* from *src* image.

    Returns True if successful, False if PIL is unavailable or image is broken.
    """
    try:
        from PIL import Image  # noqa: PLC0415
    except ImportError:
        log.debug("Pillow not installed — skipping thumbnail creation.")
        return False

    try:
        with Image.open(src) as img:
            w, h = img.size
            if w > max_width:
                scale = max_width / w
                new_h = int(h * scale)
                img = img.resize((max_width, new_h), Image.LANCZOS)
            dst.parent.mkdir(parents=True, exist_ok=True)
            img.save(dst, "JPEG", quality=80, optimize=True)
        return True
    except Exception as exc:
        log.debug("Thumbnail failed for %s: %s", src, exc)
        return False


def get_image_size(path: Path) -> tuple[int, int]:
    """Return (width, height) of image, or (0, 0) on failure."""
    try:
        from PIL import Image  # noqa: PLC0415
        with Image.open(path) as img:
            return img.size
    except Exception:
        return (0, 0)


# ===========================================================================
# SQLite helpers
# ===========================================================================

def find_chunks_for_page(
    conn: sqlite3.Connection,
    source: str,
    page_num: int,   # 1-based SQLite page number
) -> list[str]:
    """
    Return chunk IDs whose page range contains *page_num*.

    A chunk is matched when: page_start <= page_num <= page_end
    Chunks with page_end = 0 (unknown) are also matched if page_start = page_num.
    """
    cur = conn.execute(
        """SELECT id FROM chunks
           WHERE source = ?
             AND page_start <= ?
             AND (page_end >= ? OR (page_end = 0 AND page_start = ?))
        """,
        (source, page_num, page_num, page_num),
    )
    return [row[0] for row in cur.fetchall()]


def source_has_page_info(conn: sqlite3.Connection, source: str) -> bool:
    """
    Return True if the source has meaningful page ranges (i.e. not all page_start=1, page_end=1).

    Sources built from MinerU text without page tracking end up with all pages=1.
    """
    row = conn.execute(
        "SELECT MAX(page_start) FROM chunks WHERE source = ?",
        (source,),
    ).fetchone()
    return row is not None and row[0] is not None and row[0] > 1


def fetch_all_chunk_ids(conn: sqlite3.Connection, source: str) -> list[str]:
    """Return all chunk IDs for a source, ordered by rowid (creation order)."""
    cur = conn.execute(
        "SELECT id FROM chunks WHERE source = ? ORDER BY rowid",
        (source,),
    )
    return [row[0] for row in cur.fetchall()]


def insert_chunk_image(
    conn: sqlite3.Connection,
    chunk_id: str,
    image_path: str,
    thumbnail_path: str | None,
    caption: str | None,
    page_idx: int,
    width: int,
    height: int,
) -> bool:
    """
    Insert a chunk_images row.  Returns True if inserted, False if duplicate.

    Uses INSERT OR IGNORE so re-running is safe.
    """
    try:
        conn.execute(
            """INSERT OR IGNORE INTO chunk_images
               (chunk_id, image_path, thumbnail_path, caption, page_idx, width, height)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (chunk_id, image_path, thumbnail_path, caption, page_idx, width, height),
        )
        return conn.total_changes > 0
    except sqlite3.Error as exc:
        log.error("DB insert failed: %s", exc)
        return False


# ===========================================================================
# Per-document processing
# ===========================================================================

def process_document(
    doc_name: str,
    doc_cfg: dict[str, Any],
    mineru_dir: Path,
    db_path: Path,
    project_root: Path,
    verbose: bool,
) -> dict[str, int]:
    """
    Process one MinerU document folder.

    Returns stats dict with keys:
      images_found, images_linked, images_skipped,
      chunks_updated, thumbnails_created
    """
    stats = dict(
        images_found=0,
        images_linked=0,
        images_skipped=0,
        chunks_updated=0,
        thumbnails_created=0,
    )

    source = doc_cfg["source"]
    content_dir_name = doc_cfg["content_dir"]
    page_offset = doc_cfg["page_offset"]

    doc_dir = mineru_dir / doc_name
    content_dir = doc_dir / content_dir_name

    # Find content_list.json
    json_files = list(content_dir.glob("*_content_list.json"))
    if not json_files:
        log.warning("  No *_content_list.json in %s — skipping.", content_dir)
        return stats

    content_list_path = json_files[0]
    log.info("  Loading %s …", content_list_path.name)

    with open(content_list_path, encoding="utf-8") as f:
        items: list[dict] = json.load(f)

    images_dir = content_dir / "images"

    # Filter image and table entries (tables also have img_path)
    img_items = [
        it for it in items
        if it.get("type") in ("image", "table") and it.get("img_path")
    ]
    stats["images_found"] = len(img_items)

    if not img_items:
        log.info("  No image entries in content_list. Done.")
        return stats

    if source is None:
        log.info(
            "  Source mapping is None for '%s' — %d images found but not linked "
            "(document not in kb.db yet).",
            doc_name, len(img_items),
        )
        stats["images_skipped"] = len(img_items)
        return stats

    conn = sqlite3.connect(str(db_path), timeout=60)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")

    # Detect whether the source has usable page ranges.
    # If not (e.g. all chunks have page_start=page_end=1), fall back to positional mapping.
    use_positional = not source_has_page_info(conn, source)
    positional_chunk_ids: list[str] = []
    if use_positional:
        positional_chunk_ids = fetch_all_chunk_ids(conn, source)
        if not positional_chunk_ids:
            log.warning("  No chunks found for source '%s' — skipping.", source)
            conn.close()
            stats["images_skipped"] = len(img_items)
            return stats
        log.info(
            "  Source '%s' has no page info — using positional mapping "
            "(%d images → %d chunks).",
            source, len(img_items), len(positional_chunk_ids),
        )

    inserted_total = 0
    linked_total = 0
    thumb_total = 0

    for item_idx, item in enumerate(img_items):
        img_rel = item["img_path"]          # e.g. "images/HASH.jpg"
        page_idx = item["page_idx"]         # 0-based MinerU page
        page_num = page_idx + page_offset   # 1-based SQLite page

        # Get existing caption from MinerU (may be empty)
        caption_parts: list[str] = []
        if item.get("image_caption"):
            caption_parts.extend(
                c.strip() for c in item["image_caption"] if c.strip()
            )
        if item.get("table_caption"):
            caption_parts.extend(
                c.strip() for c in item["table_caption"] if c.strip()
            )
        raw_caption = " ".join(caption_parts) or None

        # Absolute paths
        img_abs = content_dir / img_rel
        if not img_abs.exists():
            log.debug("    Image missing on disk: %s", img_abs)
            stats["images_skipped"] += 1
            continue

        # Relative path from project root (for storage in DB)
        try:
            img_stored = str(img_abs.relative_to(project_root)).replace("\\", "/")
        except ValueError:
            img_stored = str(img_abs).replace("\\", "/")

        # Thumbnail
        thumb_rel_name = img_abs.stem + "_thumb.jpg"
        thumb_abs = content_dir / "thumbnails" / thumb_rel_name
        thumb_stored: str | None = None
        if make_thumbnail(img_abs, thumb_abs):
            try:
                thumb_stored = str(thumb_abs.relative_to(project_root)).replace("\\", "/")
            except ValueError:
                thumb_stored = str(thumb_abs).replace("\\", "/")
            thumb_total += 1

        # Image dimensions
        w, h = get_image_size(img_abs)

        # Find matching chunks: by page range (normal) or by position (fallback)
        if use_positional:
            # Map image proportionally to chunk list: image i → 1 chunk at position
            # (i * num_chunks) // num_images, so images spread evenly across chunks.
            num_imgs = len(img_items)
            num_cks = len(positional_chunk_ids)
            ck_idx = (item_idx * num_cks) // num_imgs
            chunk_ids = [positional_chunk_ids[ck_idx]]
        else:
            chunk_ids = find_chunks_for_page(conn, source, page_num)

        if not chunk_ids:
            if verbose:
                log.debug(
                    "    No chunks for source=%s page=%d (MinerU page_idx=%d)",
                    source, page_num, page_idx,
                )
            stats["images_skipped"] += 1
            continue

        for chunk_id in chunk_ids:
            if insert_chunk_image(
                conn,
                chunk_id=chunk_id,
                image_path=img_stored,
                thumbnail_path=thumb_stored,
                caption=raw_caption,
                page_idx=page_idx,
                width=w,
                height=h,
            ):
                inserted_total += 1

        linked_total += 1
        stats["images_linked"] += 1

    conn.commit()
    conn.close()

    stats["chunks_updated"] = inserted_total
    stats["thumbnails_created"] = thumb_total
    return stats


# ===========================================================================
# Main
# ===========================================================================

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Link MinerU images to KB chunks in chunk_images table.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--db-path",
        default="knowledge-base/kb.db",
        help="Path to kb.db SQLite database.",
    )
    parser.add_argument(
        "--mineru-dir",
        default="mineru-output",
        help="Root directory of MinerU output.",
    )
    parser.add_argument(
        "--doc",
        default=None,
        help="Process only this specific document name (default: all).",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable debug-level output.",
    )
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    project_root = Path(__file__).resolve().parent.parent
    db_path = project_root / args.db_path
    mineru_dir = project_root / args.mineru_dir

    if not db_path.exists():
        log.error("kb.db not found at %s — run build_kb.py first.", db_path)
        sys.exit(1)

    if not mineru_dir.exists():
        log.error("MinerU output directory not found: %s", mineru_dir)
        sys.exit(1)

    log.info("=" * 60)
    log.info("  LLCAR Image Linker")
    log.info("  DB:      %s", db_path)
    log.info("  MinerU:  %s", mineru_dir)
    log.info("=" * 60)

    t0 = time.time()
    totals = dict(images_found=0, images_linked=0, images_skipped=0,
                  chunks_updated=0, thumbnails_created=0)

    docs_to_process = (
        {args.doc: MINERU_SOURCE_MAP[args.doc]}
        if args.doc and args.doc in MINERU_SOURCE_MAP
        else MINERU_SOURCE_MAP
    )

    for doc_name, doc_cfg in docs_to_process.items():
        doc_dir = mineru_dir / doc_name
        if not doc_dir.exists():
            log.info("Skipping '%s' — directory not found.", doc_name)
            continue

        log.info("Processing: %s", doc_name)
        stats = process_document(
            doc_name=doc_name,
            doc_cfg=doc_cfg,
            mineru_dir=mineru_dir,
            db_path=db_path,
            project_root=project_root,
            verbose=args.verbose,
        )
        log.info(
            "  → found=%d linked=%d skipped=%d inserted_rows=%d thumbs=%d",
            stats["images_found"], stats["images_linked"], stats["images_skipped"],
            stats["chunks_updated"], stats["thumbnails_created"],
        )
        for k, v in stats.items():
            totals[k] += v

    elapsed = time.time() - t0
    log.info("-" * 60)
    log.info("TOTAL: found=%d linked=%d skipped=%d rows=%d thumbs=%d  (%.1f s)",
             totals["images_found"], totals["images_linked"], totals["images_skipped"],
             totals["chunks_updated"], totals["thumbnails_created"], elapsed)

    # Final DB count
    conn = sqlite3.connect(str(db_path), timeout=30)
    total_db = conn.execute("SELECT COUNT(*) FROM chunk_images").fetchone()[0]
    conn.close()
    log.info("chunk_images table now has %d rows.", total_db)


if __name__ == "__main__":
    main()
