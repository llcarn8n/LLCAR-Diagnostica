#!/usr/bin/env python3
"""
LLCAR Diagnostica — CLIP Image Embeddings (Phase 2).

Encodes all images in `chunk_images` (or those with captions) using
CLIP ViT-L/14 and stores the resulting 768-d vectors in a LanceDB table
`image_emb`.  Enables text-to-image search via the API.

Requirements:
  - transformers (CLIPModel / CLIPProcessor)  OR  open_clip_torch
  - torch (CUDA optional, falls back to CPU)
  - lancedb >= 0.5
  - Pillow

VRAM usage:
  - CLIP ViT-L/14: ~2 GB (fp32) / ~1 GB (fp16)
  - Runs on CPU if no GPU available (slower, ~0.5 img/s)

Usage:
    python scripts/embed_images.py \
        --db-path knowledge-base/kb.db \
        --lancedb-dir knowledge-base/lancedb \
        --device cuda:0

    # CPU fallback
    python scripts/embed_images.py --device cpu

    # Only images with a caption
    python scripts/embed_images.py --captioned-only

LanceDB table schema (image_emb):
  chunk_id    : string     — links to chunks.id
  image_id    : int        — links to chunk_images.id
  image_path  : string     — relative path to image file
  vector      : float[768] — CLIP ViT-L/14 embedding
  caption     : string     — caption text (empty if not yet captioned)
  source_lang : string     — source_language of the linked chunk
  layer       : string     — layer of the linked chunk
"""
from __future__ import annotations

import argparse
import logging
import sqlite3
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("embed_images")


# ===========================================================================
# Constants
# ===========================================================================

CLIP_MODEL_ID = "openai/clip-vit-large-patch14"   # 768-d, ~1.7 GB download
CLIP_DIM      = 768
BATCH_SIZE    = 32
TABLE_NAME    = "image_emb"


# ===========================================================================
# CLIP encoder
# ===========================================================================

class ClipImageEncoder:
    """
    Wraps CLIPModel (transformers) for image encoding.

    Returns L2-normalised float32 vectors of shape (N, 768).
    """

    def __init__(self, device: str = "cuda:0") -> None:
        import torch  # noqa: PLC0415
        from transformers import CLIPModel, CLIPProcessor  # noqa: PLC0415

        self.device = device
        log.info("Loading CLIP ViT-L/14 on %s …", device)
        t0 = time.time()
        self.processor = CLIPProcessor.from_pretrained(CLIP_MODEL_ID)
        self.model = CLIPModel.from_pretrained(
            CLIP_MODEL_ID,
            torch_dtype=torch.float16 if "cuda" in device else torch.float32,
        ).to(device)
        self.model.eval()
        log.info("CLIP loaded in %.1f s", time.time() - t0)
        self._torch = torch

    def encode(self, image_paths: list[Path]) -> np.ndarray:
        """
        Encode a batch of images.

        Returns float32 array of shape (N, CLIP_DIM), L2-normalised.
        Broken/missing images produce a zero vector.
        """
        from PIL import Image  # noqa: PLC0415

        pil_images: list[Any] = []
        valid_mask: list[bool] = []

        for p in image_paths:
            try:
                img = Image.open(p).convert("RGB")
                pil_images.append(img)
                valid_mask.append(True)
            except Exception as exc:
                log.debug("Cannot open %s: %s", p, exc)
                pil_images.append(None)
                valid_mask.append(False)

        valid_imgs = [img for img, ok in zip(pil_images, valid_mask) if ok]
        result = np.zeros((len(image_paths), CLIP_DIM), dtype=np.float32)

        if not valid_imgs:
            return result

        inputs = self.processor(images=valid_imgs, return_tensors="pt").to(self.device)
        with self._torch.no_grad():
            features = self.model.get_image_features(**inputs)
            # transformers >=5.x returns BaseModelOutputWithPooling, not a plain tensor
            if not isinstance(features, self._torch.Tensor):
                features = features.pooler_output
            features = features.float().cpu().numpy()

        # L2 normalise
        norms = np.linalg.norm(features, axis=1, keepdims=True)
        norms = np.where(norms > 0, norms, 1.0)
        features = features / norms

        # Place valid results back into correct positions
        valid_idx = 0
        for i, ok in enumerate(valid_mask):
            if ok:
                result[i] = features[valid_idx]
                valid_idx += 1

        return result


# ===========================================================================
# SQLite helpers
# ===========================================================================

def fetch_images(
    conn: sqlite3.Connection,
    captioned_only: bool,
    limit: int | None,
) -> list[tuple[int, str, str, str, str]]:
    """
    Fetch (id, image_path, chunk_id, caption, source_language, layer) from chunk_images.

    If captioned_only=True, only rows with a non-NULL caption are returned.
    """
    sql = """
        SELECT ci.id, ci.image_path, ci.chunk_id,
               COALESCE(ci.caption, ''),
               COALESCE(c.source_language, ''),
               COALESCE(c.layer, '')
        FROM chunk_images ci
        JOIN chunks c ON c.id = ci.chunk_id
    """
    if captioned_only:
        sql += " WHERE ci.caption IS NOT NULL"
    sql += " ORDER BY ci.id"
    if limit:
        sql += f" LIMIT {limit}"

    return conn.execute(sql).fetchall()


def get_existing_image_ids(lancedb_dir: Path) -> set[int]:
    """Return set of image_ids already in LanceDB image_emb table."""
    try:
        import lancedb  # noqa: PLC0415
        db = lancedb.connect(str(lancedb_dir))
        if TABLE_NAME not in db.table_names():
            return set()
        tbl = db.open_table(TABLE_NAME)
        ids = tbl.to_pandas()["image_id"].tolist()
        return set(int(i) for i in ids)
    except Exception as exc:
        log.debug("Could not read existing image_emb IDs: %s", exc)
        return set()


# ===========================================================================
# LanceDB helpers
# ===========================================================================

def create_or_append_lancedb(
    lancedb_dir: Path,
    data: list[dict],
    overwrite: bool = False,
) -> None:
    """Write *data* (list of dicts) to the image_emb LanceDB table."""
    import lancedb  # noqa: PLC0415
    import pyarrow as pa  # noqa: PLC0415

    schema = pa.schema([
        pa.field("chunk_id",    pa.string()),
        pa.field("image_id",    pa.int32()),
        pa.field("image_path",  pa.string()),
        pa.field("vector",      pa.list_(pa.float32(), CLIP_DIM)),
        pa.field("caption",     pa.string()),
        pa.field("source_lang", pa.string()),
        pa.field("layer",       pa.string()),
    ])

    db = lancedb.connect(str(lancedb_dir))
    mode = "overwrite" if overwrite else "append"

    if TABLE_NAME not in db.table_names():
        mode = "create"

    if mode == "create":
        tbl = db.create_table(TABLE_NAME, schema=schema)
    elif mode == "overwrite":
        db.drop_table(TABLE_NAME, ignore_missing=True)
        tbl = db.create_table(TABLE_NAME, schema=schema)
    else:
        tbl = db.open_table(TABLE_NAME)

    if data:
        tbl.add(data)
        log.info("LanceDB image_emb: added %d rows (mode=%s)", len(data), mode)


def build_ann_index(lancedb_dir: Path) -> None:
    """Build IVF-PQ ANN index on image_emb.vector."""
    try:
        import lancedb  # noqa: PLC0415
        db = lancedb.connect(str(lancedb_dir))
        if TABLE_NAME not in db.table_names():
            return
        tbl = db.open_table(TABLE_NAME)
        n = tbl.count_rows()
        if n < 256:
            log.info("Too few rows (%d) for IVF index — skipping.", n)
            return
        num_partitions = min(max(int(n ** 0.5), 4), 64)
        # LanceDB 0.29.x API: first positional arg is metric, use vector_column_name kwarg
        tbl.create_index(
            metric="cosine",
            vector_column_name="vector",
            num_partitions=num_partitions,
            num_sub_vectors=24,   # 768 / 24 = 32-dim subvectors
            replace=True,
        )
        log.info("IVF-PQ index built on image_emb (partitions=%d)", num_partitions)
    except Exception as exc:
        log.warning("Index build failed: %s", exc)


# ===========================================================================
# Main
# ===========================================================================

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build CLIP image embeddings for KB images.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--db-path",      default="knowledge-base/kb.db")
    parser.add_argument("--lancedb-dir",  default="knowledge-base/lancedb")
    parser.add_argument("--device",       default="cuda:0",
                        help="CUDA device or 'cpu'.")
    parser.add_argument("--batch-size",   type=int, default=BATCH_SIZE)
    parser.add_argument("--captioned-only", action="store_true",
                        help="Only embed images that already have captions.")
    parser.add_argument("--limit",        type=int, default=None)
    parser.add_argument("--overwrite",    action="store_true",
                        help="Drop and recreate image_emb table.")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    project_root = Path(__file__).resolve().parent.parent
    db_path    = project_root / args.db_path
    lancedb_dir = project_root / args.lancedb_dir

    if not db_path.exists():
        log.error("kb.db not found: %s", db_path)
        sys.exit(1)

    log.info("=" * 60)
    log.info("  LLCAR CLIP Image Embedder")
    log.info("  Model:   %s", CLIP_MODEL_ID)
    log.info("  Device:  %s", args.device)
    log.info("  DB:      %s", db_path)
    log.info("  LanceDB: %s", lancedb_dir)
    log.info("=" * 60)

    conn = sqlite3.connect(str(db_path), timeout=60)
    rows = fetch_images(conn, args.captioned_only, args.limit)
    conn.close()

    if not rows:
        log.info("No images to embed.")
        return

    # Skip already-encoded images
    existing_ids = get_existing_image_ids(lancedb_dir) if not args.overwrite else set()
    to_embed = [r for r in rows if r[0] not in existing_ids]
    log.info("Images: total=%d  already_encoded=%d  to_encode=%d",
             len(rows), len(existing_ids), len(to_embed))

    if not to_embed:
        log.info("All images already encoded.")
        build_ann_index(lancedb_dir)
        return

    encoder = ClipImageEncoder(device=args.device)

    t_start = time.time()
    all_records: list[dict] = []
    # Track whether we've done the initial overwrite flush (only first flush overwrites)
    first_flush_done = False

    for i in range(0, len(to_embed), args.batch_size):
        batch = to_embed[i : i + args.batch_size]
        # batch: (id, image_path, chunk_id, caption, source_lang, layer)

        image_abs_paths = [project_root / r[1] for r in batch]
        vectors = encoder.encode(image_abs_paths)   # (batch, 768)

        for j, row in enumerate(batch):
            row_id, img_path, chunk_id, caption, src_lang, layer = row
            vec = vectors[j].tolist()
            all_records.append({
                "chunk_id":   chunk_id,
                "image_id":   row_id,
                "image_path": img_path,
                "vector":     vec,
                "caption":    caption,
                "source_lang": src_lang,
                "layer":      layer,
            })

        done = min(i + args.batch_size, len(to_embed))
        elapsed = time.time() - t_start
        rate = done / elapsed if elapsed > 0 else 0
        log.info("  %d/%d  %.2f img/s", done, len(to_embed), rate)

        # Flush to LanceDB every 500 records to save memory
        if len(all_records) >= 500:
            do_overwrite = args.overwrite and not first_flush_done
            create_or_append_lancedb(lancedb_dir, all_records, overwrite=do_overwrite)
            all_records = []
            first_flush_done = True

    # Flush remainder
    if all_records:
        do_overwrite = args.overwrite and not first_flush_done
        create_or_append_lancedb(lancedb_dir, all_records, overwrite=do_overwrite)

    build_ann_index(lancedb_dir)

    elapsed_total = time.time() - t_start
    log.info("Done in %.1f s  (%.2f img/s)", elapsed_total,
             len(to_embed) / elapsed_total if elapsed_total > 0 else 0)


if __name__ == "__main__":
    main()
