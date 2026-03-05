#!/usr/bin/env python3
"""
translate_m2m_batch.py — Batch translation of missing KB chunks using M2M model on GPU.

Uses fine-tuned M2M model (Petr117/m2m-diagnostica-automotive-r10) to translate
chunks that are missing translations in chunk_content table.

Translation gaps (as of 2026-03-05):
  ZH → RU: 5,314 chunks (manual)     ← PRIORITY
  ZH → EN: 5,314 chunks (manual)
  RU → EN: 1,059 chunks (manual)
  + ~77 minor (parts, config, description)

Usage:
    # Dry run — show what needs translating
    python scripts/translate_m2m_batch.py --dry-run

    # Translate ZH→RU (highest priority)
    python scripts/translate_m2m_batch.py --source zh --target ru

    # Translate ZH→EN
    python scripts/translate_m2m_batch.py --source zh --target en

    # Translate RU→EN
    python scripts/translate_m2m_batch.py --source ru --target en

    # Limit to N chunks (for testing)
    python scripts/translate_m2m_batch.py --source zh --target ru --limit 10

    # Resume from where you left off (default behavior — skips already translated)
    python scripts/translate_m2m_batch.py --source zh --target ru

    # Use specific GPU
    python scripts/translate_m2m_batch.py --source zh --target ru --device cuda:1

    # All directions at once
    python scripts/translate_m2m_batch.py --all

Dependencies:
    pip install transformers torch sentencepiece tqdm

Environment:
    GPU recommended (2x RTX 3090 on workstation)
    CPU works but ~10x slower
"""
from __future__ import annotations

import argparse
import io
import logging
import sqlite3
import sys
import time
from pathlib import Path

# Windows UTF-8
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("m2m_translate")

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "knowledge-base" / "kb.db"

MODEL_ID = "Petr117/m2m-diagnostica-automotive-r10"

# Max tokens for M2M generation (title vs content)
MAX_TITLE_TOKENS = 128
MAX_CONTENT_TOKENS = 512

# Batch size for GPU inference (adjust based on VRAM)
# RTX 3090 24GB: batch_size=8 should be safe for content, 16 for titles
DEFAULT_BATCH_SIZE = 8


def get_missing_chunks(db_path: Path, src_lang: str, tgt_lang: str, limit: int = 0) -> list[dict]:
    """Find chunks that need translation: source_language=src_lang, no chunk_content for tgt_lang."""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row

    sql = """
        SELECT c.id, c.title, c.content, c.content_type, c.layer
        FROM chunks c
        WHERE c.source_language = ?
          AND c.id NOT IN (
              SELECT chunk_id FROM chunk_content WHERE lang = ?
          )
        ORDER BY
            CASE c.content_type
                WHEN 'manual' THEN 1
                WHEN 'dtc' THEN 2
                WHEN 'parts' THEN 3
                ELSE 4
            END,
            c.id
    """
    params = [src_lang, tgt_lang]
    if limit > 0:
        sql += " LIMIT ?"
        params.append(limit)

    rows = conn.execute(sql, params).fetchall()
    chunks = [dict(r) for r in rows]
    conn.close()
    return chunks


def count_gaps(db_path: Path) -> list[tuple[str, str, int]]:
    """Count translation gaps for all language pairs."""
    conn = sqlite3.connect(str(db_path))
    gaps = []
    for src, tgt in [("zh", "ru"), ("zh", "en"), ("ru", "en"), ("en", "ru"), ("en", "zh")]:
        n = conn.execute("""
            SELECT count(*) FROM chunks c
            WHERE c.source_language = ?
              AND c.id NOT IN (SELECT chunk_id FROM chunk_content WHERE lang = ?)
        """, (src, tgt)).fetchone()[0]
        if n > 0:
            gaps.append((src, tgt, n))
    conn.close()
    return gaps


def load_model(device: str = "cuda:0"):
    """Load M2M model and tokenizer."""
    import torch
    from transformers import M2M100ForConditionalGeneration, T5Tokenizer

    log.info("Loading model %s ...", MODEL_ID)
    t0 = time.perf_counter()

    tokenizer = T5Tokenizer.from_pretrained(MODEL_ID)

    # Load on CPU first, then move to device (safer for CUDA)
    model = M2M100ForConditionalGeneration.from_pretrained(
        MODEL_ID,
        torch_dtype=torch.float16 if "cuda" in device else torch.float32,
    )
    model = model.to(device)
    model.eval()

    dt = time.perf_counter() - t0
    log.info("Model loaded in %.1fs on %s", dt, device)
    return model, tokenizer, device


def translate_batch(
    model, tokenizer, device: str,
    texts: list[str], tgt_lang: str,
    max_new_tokens: int = MAX_CONTENT_TOKENS,
) -> list[str]:
    """Translate a batch of texts to target language."""
    import torch

    # Format: "translate to ru: ..."
    prompts = [f"translate to {tgt_lang}: {t}" for t in texts]

    inputs = tokenizer(
        prompts,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=1024,
    ).to(device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            num_beams=4,
            early_stopping=True,
            no_repeat_ngram_size=3,
        )

    results = tokenizer.batch_decode(outputs, skip_special_tokens=True)
    return results


def save_translation(conn: sqlite3.Connection, chunk_id: str, lang: str, title: str, content: str):
    """Insert or update translation in chunk_content."""
    existing = conn.execute(
        "SELECT 1 FROM chunk_content WHERE chunk_id = ? AND lang = ?",
        (chunk_id, lang),
    ).fetchone()

    if existing:
        conn.execute(
            "UPDATE chunk_content SET title = ?, content = ?, translated_by = ? WHERE chunk_id = ? AND lang = ?",
            (title, content, "m2m-r10", chunk_id, lang),
        )
    else:
        conn.execute(
            "INSERT INTO chunk_content (chunk_id, lang, title, content, translated_by) VALUES (?, ?, ?, ?, ?)",
            (chunk_id, lang, title, content, "m2m-r10"),
        )


def translate_direction(
    model, tokenizer, device: str,
    db_path: Path,
    src_lang: str, tgt_lang: str,
    batch_size: int = DEFAULT_BATCH_SIZE,
    limit: int = 0,
    commit_every: int = 50,
):
    """Translate all missing chunks for a given language pair."""
    try:
        from tqdm import tqdm
    except ImportError:
        tqdm = None

    chunks = get_missing_chunks(db_path, src_lang, tgt_lang, limit=limit)
    total = len(chunks)
    if total == 0:
        log.info("  %s → %s: nothing to translate", src_lang, tgt_lang)
        return 0

    log.info("  %s → %s: %d chunks to translate (batch_size=%d)", src_lang, tgt_lang, total, batch_size)

    conn = sqlite3.connect(str(db_path))
    translated = 0
    errors = 0
    t0 = time.perf_counter()

    iterator = range(0, total, batch_size)
    if tqdm:
        iterator = tqdm(iterator, desc=f"{src_lang}→{tgt_lang}", total=(total + batch_size - 1) // batch_size)

    for batch_start in iterator:
        batch = chunks[batch_start:batch_start + batch_size]

        # Translate titles
        titles_src = [c["title"] or "" for c in batch]
        titles_nonempty = [(i, t) for i, t in enumerate(titles_src) if t.strip()]

        title_results = [""] * len(batch)
        if titles_nonempty:
            try:
                indices, texts = zip(*titles_nonempty)
                tr = translate_batch(model, tokenizer, device, list(texts), tgt_lang, MAX_TITLE_TOKENS)
                for idx, translated_text in zip(indices, tr):
                    title_results[idx] = translated_text
            except Exception as e:
                log.warning("Title batch error: %s", e)
                errors += len(titles_nonempty)

        # Translate content (may be long — truncate if needed)
        contents_src = [c["content"] or "" for c in batch]
        contents_nonempty = [(i, t) for i, t in enumerate(contents_src) if t.strip()]

        content_results = [""] * len(batch)
        if contents_nonempty:
            try:
                indices, texts = zip(*contents_nonempty)
                # Truncate very long content to avoid OOM
                texts_truncated = [t[:3000] for t in texts]
                tr = translate_batch(model, tokenizer, device, list(texts_truncated), tgt_lang, MAX_CONTENT_TOKENS)
                for idx, translated_text in zip(indices, tr):
                    content_results[idx] = translated_text
            except Exception as e:
                log.warning("Content batch error at chunk %d: %s", batch_start, e)
                # Fallback: translate one by one
                for i, text in contents_nonempty:
                    try:
                        tr = translate_batch(model, tokenizer, device, [text[:2000]], tgt_lang, MAX_CONTENT_TOKENS)
                        content_results[i] = tr[0]
                    except Exception as e2:
                        log.warning("  Single chunk error %s: %s", batch[i]["id"], e2)
                        content_results[i] = ""
                        errors += 1

        # Save to DB
        for i, chunk in enumerate(batch):
            title_tr = title_results[i].strip()
            content_tr = content_results[i].strip()
            if title_tr or content_tr:
                save_translation(conn, chunk["id"], tgt_lang, title_tr, content_tr)
                translated += 1

        # Periodic commit
        if translated % commit_every < batch_size:
            conn.commit()

    conn.commit()
    conn.close()

    dt = time.perf_counter() - t0
    speed = translated / dt if dt > 0 else 0
    log.info(
        "  %s → %s: done. %d/%d translated, %d errors, %.1fs (%.1f chunks/s)",
        src_lang, tgt_lang, translated, total, errors, dt, speed,
    )
    return translated


def main():
    parser = argparse.ArgumentParser(description="Translate missing KB chunks using M2M model")
    parser.add_argument("--db-path", type=Path, default=DB_PATH, help="Path to kb.db")
    parser.add_argument("--source", "-s", type=str, help="Source language (zh, ru, en)")
    parser.add_argument("--target", "-t", type=str, help="Target language (ru, en, zh)")
    parser.add_argument("--all", action="store_true", help="Translate all missing directions")
    parser.add_argument("--limit", type=int, default=0, help="Limit chunks per direction (0=all)")
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE, help="GPU batch size")
    parser.add_argument("--device", type=str, default="cuda:0", help="Device (cuda:0, cuda:1, cpu)")
    parser.add_argument("--commit-every", type=int, default=50, help="Commit to DB every N chunks")
    parser.add_argument("--dry-run", action="store_true", help="Only show gaps, don't translate")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if not args.db_path.exists():
        log.error("DB not found: %s", args.db_path)
        sys.exit(1)

    # Show gaps
    gaps = count_gaps(args.db_path)
    log.info("=== Translation gaps in %s ===", args.db_path.name)
    total_missing = 0
    for src, tgt, n in gaps:
        log.info("  %s → %s: %d chunks missing", src, tgt, n)
        total_missing += n
    log.info("  Total: %d missing translations", total_missing)

    if args.dry_run:
        return

    if not args.all and (not args.source or not args.target):
        log.error("Specify --source and --target, or use --all")
        sys.exit(1)

    # Determine directions
    if args.all:
        # Priority order: ZH→RU, ZH→EN, RU→EN, then rest
        directions = [(s, t) for s, t, n in gaps if n > 0]
    else:
        directions = [(args.source, args.target)]

    # Load model
    model, tokenizer, device = load_model(args.device)

    # Translate each direction
    grand_total = 0
    for src, tgt in directions:
        n = translate_direction(
            model, tokenizer, device,
            args.db_path, src, tgt,
            batch_size=args.batch_size,
            limit=args.limit,
            commit_every=args.commit_every,
        )
        grand_total += n

    log.info("=== DONE. Total translated: %d ===", grand_total)


if __name__ == "__main__":
    main()
