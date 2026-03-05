#!/usr/bin/env python3
"""
fix_zh_residuals.py — Re-translate ZH residuals in EN/RU chunk_content rows.

Problem: 228 chunks (EN=74, RU=154) have Chinese characters embedded in
their translations, meaning the original Claude Haiku translation failed
and returned the source ZH text instead of a translated version.

Solution: Re-translate these chunks locally using Utrobin M2M
(A/B test winner: BLEU 63.3 on RU→EN, 34.1 EN→RU, 30.5 ZH→RU).
No Anthropic API key required.

Usage:
    python scripts/fix_zh_residuals.py --device cuda:0
    python scripts/fix_zh_residuals.py --device cpu --limit 20
    python scripts/fix_zh_residuals.py --dry-run
"""
from __future__ import annotations

import argparse
import logging
import re
import sqlite3
import sys
import time
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("fix_zh")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "knowledge-base" / "kb.db"

UTROBIN_MODEL_ID = "utrobinmv/m2m_translate_en_ru_zh_large_4096"

# Detect CJK characters (covers common CJK ranges)
ZH_RE = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf\u20000-\u2a6df]')


def has_chinese(text: str) -> bool:
    return bool(ZH_RE.search(text))


def chinese_ratio(text: str) -> float:
    if not text:
        return 0.0
    zh_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff' or '\u3400' <= c <= '\u4dbf')
    return zh_chars / len(text)


def load_model(device: str):
    """Load Utrobin M2M model and tokenizer."""
    import torch
    from transformers import AutoTokenizer, M2M100ForConditionalGeneration

    log.info("Loading Utrobin M2M from %s …", UTROBIN_MODEL_ID)
    t0 = time.time()

    # Utrobin uses M2M100ForConditionalGeneration with AutoTokenizer (T5Tokenizer internally)
    tokenizer = AutoTokenizer.from_pretrained(UTROBIN_MODEL_ID)
    model = M2M100ForConditionalGeneration.from_pretrained(
        UTROBIN_MODEL_ID,
        torch_dtype=torch.float16 if "cuda" in device else torch.float32,
    )
    model.to(device)
    model.eval()
    log.info("Model loaded in %.1f s", time.time() - t0)
    return model, tokenizer


def translate_chunk(
    model,
    tokenizer,
    text: str,
    src_lang: str,    # "zh", "en", "ru"
    tgt_lang: str,    # "en", "ru"
    device: str,
    max_length: int = 512,
) -> str:
    """
    Translate text with Utrobin M2M using T5-style prefix.
    Model card: prefix "translate to {lang}: " where lang is "ru", "en", "zh".
    NO forced_bos_token_id needed.
    """
    import torch

    # T5-style prefix as specified in Utrobin model card
    input_text = f"translate to {tgt_lang}: " + text.strip()

    inputs = tokenizer(
        input_text,
        return_tensors="pt",
        max_length=max_length,
        truncation=True,
        padding=True,
    )
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=max_length,
            num_beams=4,
            early_stopping=True,
        )

    result = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    return result.strip()


def open_db(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(path))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.row_factory = sqlite3.Row
    return conn


def fetch_zh_residuals(
    conn: sqlite3.Connection,
    limit: int | None = None,
    min_zh_ratio: float = 0.10,
) -> list[sqlite3.Row]:
    """
    Fetch chunk_content rows (EN or RU translations) that contain significant
    Chinese text (>= min_zh_ratio of content is CJK characters).
    """
    sql = """
        SELECT cc.rowid, cc.chunk_id, cc.lang, cc.content, cc.title,
               c.source_language
        FROM chunk_content cc
        JOIN chunks c ON c.id = cc.chunk_id
        WHERE cc.lang IN ('en', 'ru')
          AND cc.translated_by != 'original'
        ORDER BY cc.chunk_id, cc.lang
    """
    if limit:
        sql += f" LIMIT {limit}"

    rows = conn.execute(sql).fetchall()
    # Filter by Chinese ratio in Python (SQLite can't detect Unicode CJK)
    result = [r for r in rows if chinese_ratio(r["content"]) >= min_zh_ratio]
    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Re-translate ZH residuals using Utrobin M2M.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--db-path", default=str(DB_PATH))
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--min-zh-ratio", type=float, default=0.10,
                        help="Minimum fraction of CJK chars to trigger re-translation.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    db_path = Path(args.db_path)
    if not db_path.exists():
        log.error("DB not found: %s", db_path)
        sys.exit(1)

    log.info("=" * 60)
    log.info("  ZH Residuals Fix — Utrobin M2M")
    log.info("  DB:     %s", db_path)
    log.info("  Device: %s", args.device)
    log.info("  Mode:   %s", "DRY-RUN" if args.dry_run else "LIVE")
    log.info("=" * 60)

    conn = open_db(db_path)

    rows = fetch_zh_residuals(conn, args.limit, args.min_zh_ratio)
    log.info("Found %d chunk_content rows with ZH residuals (min_ratio=%.2f)",
             len(rows), args.min_zh_ratio)

    if not rows:
        log.info("Nothing to fix.")
        conn.close()
        return

    # Language distribution
    by_lang = {}
    for r in rows:
        by_lang[r["lang"]] = by_lang.get(r["lang"], 0) + 1
    for lang, count in sorted(by_lang.items()):
        log.info("  → %s: %d rows", lang, count)

    if args.dry_run:
        log.info("DRY RUN — not loading model, not writing to DB.")
        # Show samples
        for r in rows[:5]:
            log.info("Sample [%s→%s]: %s", r["source_language"], r["lang"],
                     r["content"][:80].replace('\n', ' '))
        conn.close()
        return

    # Load model
    model, tokenizer = load_model(args.device)

    t_start = time.time()
    fixed = 0
    failed = 0

    for i, row in enumerate(rows):
        src_lang = row["source_language"] or "zh"
        tgt_lang = row["lang"]

        # Get clean source text: prefer the original chunk_content in source lang
        original_row = conn.execute(
            "SELECT content FROM chunk_content WHERE chunk_id=? AND translated_by='original' AND lang=?",
            (row["chunk_id"], src_lang),
        ).fetchone()

        if original_row:
            source_text = original_row["content"]
        else:
            # Fallback: use the ZH-contaminated content and hope it's mostly ZH
            source_text = row["content"]

        if not source_text or len(source_text.strip()) < 10:
            log.debug("Skip %s — source too short", row["chunk_id"])
            failed += 1
            continue

        try:
            translated = translate_chunk(
                model, tokenizer,
                source_text, src_lang, tgt_lang,
                args.device,
            )
        except Exception as exc:
            log.error("Translation failed for %s (%s→%s): %s",
                      row["chunk_id"], src_lang, tgt_lang, exc)
            failed += 1
            continue

        if not translated or len(translated.strip()) < 5:
            log.warning("Empty translation for %s", row["chunk_id"])
            failed += 1
            continue

        # Update chunk_content
        conn.execute(
            """UPDATE chunk_content
               SET content=?, translated_by=?, quality_score=0.75
               WHERE rowid=?""",
            (translated, f"utrobin_m2m_fix", row["rowid"]),
        )
        fixed += 1

        if fixed % 10 == 0:
            conn.commit()
            elapsed = time.time() - t_start
            log.info("  %d/%d fixed  (%.1f s)  failed=%d",
                     fixed, len(rows), elapsed, failed)

    conn.commit()
    conn.close()

    elapsed_total = time.time() - t_start
    log.info("Done: fixed=%d  failed=%d  time=%.1f s", fixed, failed, elapsed_total)


if __name__ == "__main__":
    main()
