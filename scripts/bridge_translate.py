#!/usr/bin/env python3
"""
bridge_translate.py — Bridge-translate EN chunk_content to AR and ES.

Strategy:
  1. Read EN translations from chunk_content (translated by Claude Haiku)
  2. Translate EN→AR and EN→ES using NLLB-200-distilled-600M (local, fast)
  3. Write results to chunk_content (translated_by='nllb-200-distilled-600m')
  4. Generate training pairs for AR/ES fine-tuning

Why NLLB-200:
  - Supports 200 languages (AR + ES natively)
  - 600M params → ~3GB VRAM, runs on GPU 0 in parallel with Qwen on GPU 1
  - ~0.3s per translation at FP16

Usage:
    python scripts/bridge_translate.py --device cuda:0
    python scripts/bridge_translate.py --device cuda:0 --limit 100  # test run
    python scripts/bridge_translate.py --device cuda:0 --source pdf_l9_ru  # one doc
"""
from __future__ import annotations

import argparse
import io
import json
import logging
import sqlite3
import sys
import time
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("bridge")

ROOT   = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "knowledge-base" / "kb.db"

NLLB_MODEL_ID = "facebook/nllb-200-distilled-600M"
MODEL_TAG = "nllb-200-distilled-600m"

# NLLB language codes
NLLB_LANG = {
    "en": "eng_Latn",
    "ru": "rus_Cyrl",
    "zh": "zho_Hans",
    "ar": "arb_Arab",
    "es": "spa_Latn",
}

TARGET_LANGS = ["ar", "es"]  # bridge from EN to these

DB_COMMIT_EVERY = 50


# ---------------------------------------------------------------------------
# Model loading
# ---------------------------------------------------------------------------

def load_nllb(device: str):
    import torch
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

    log.info("Loading %s on %s ...", NLLB_MODEL_ID, device)
    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(NLLB_MODEL_ID)
    model = AutoModelForSeq2SeqLM.from_pretrained(
        NLLB_MODEL_ID,
        torch_dtype=torch.float16 if "cuda" in device else torch.float32,
    ).to(device)
    model.eval()
    log.info("Loaded in %.1f s", time.time() - t0)
    return model, tok


# ---------------------------------------------------------------------------
# Translation
# ---------------------------------------------------------------------------

def translate_batch(
    model,
    tok,
    texts: list[str],
    src_lang: str,
    tgt_lang: str,
    device: str,
    max_len: int = 512,
) -> list[str]:
    """Translate a batch of texts with NLLB."""
    import torch

    src_code = NLLB_LANG[src_lang]
    tgt_code = NLLB_LANG[tgt_lang]

    tok.src_lang = src_code
    enc = tok(
        texts,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=max_len,
    ).to(device)

    forced_bos = tok.convert_tokens_to_ids(tgt_code)
    with torch.no_grad():
        out = model.generate(
            **enc,
            forced_bos_token_id=forced_bos,
            max_new_tokens=max_len,
            num_beams=4,
        )

    return [tok.decode(ids, skip_special_tokens=True) for ids in out]


# ---------------------------------------------------------------------------
# DB helpers
# ---------------------------------------------------------------------------

def fetch_en_chunks(
    conn: sqlite3.Connection,
    tgt_lang: str,
    source_filter: str | None,
    limit: int | None,
) -> list[tuple[str, str, str, str]]:
    """
    Return (chunk_id, en_title, en_content, source) rows that have EN
    translation but NOT tgt_lang translation yet.
    """
    source_clause = f"AND c.source = '{source_filter}'" if source_filter else ""
    limit_clause  = f"LIMIT {limit}" if limit else ""

    rows = conn.execute(f"""
        SELECT cc_en.chunk_id, cc_en.title, cc_en.content, c.source
        FROM chunk_content cc_en
        JOIN chunks c ON c.id = cc_en.chunk_id
        WHERE cc_en.lang = 'en'
          AND length(cc_en.content) > 20
          AND NOT EXISTS (
              SELECT 1 FROM chunk_content cc2
              WHERE cc2.chunk_id = cc_en.chunk_id
                AND cc2.lang = '{tgt_lang}'
          )
          {source_clause}
        ORDER BY cc_en.chunk_id
        {limit_clause}
    """).fetchall()
    return rows


def write_translation(
    conn: sqlite3.Connection,
    chunk_id: str,
    lang: str,
    title: str,
    content: str,
) -> None:
    conn.execute(
        """
        INSERT OR REPLACE INTO chunk_content
          (chunk_id, lang, title, content, translated_by, quality_score,
           terminology_score, glossary_version, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """,
        (chunk_id, lang, title, content, MODEL_TAG, 0.7, 0.5, "v1.0"),
    )


def save_training_pair(
    pairs_file: Path,
    source_lang: str,
    target_lang: str,
    source_text: str,
    translated_text: str,
    chunk_id: str,
) -> None:
    pairs_file.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "id": f"{chunk_id}_{source_lang}_{target_lang}",
        "source_lang": source_lang,
        "target_lang": target_lang,
        "source": source_text[:1000],
        "translation": translated_text[:1000],
        "source_title": "",
        "quality_score": 0.7,
    }
    with open(pairs_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def run_bridge(
    db_path: Path,
    device: str,
    tgt_langs: list[str],
    source_filter: str | None,
    limit: int | None,
    batch_size: int,
    training_pairs_file: Path | None,
) -> dict:
    stats: dict[str, int] = {}

    conn = sqlite3.connect(str(db_path), timeout=120, isolation_level=None)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA busy_timeout=120000")

    model, tok = load_nllb(device)

    for tgt_lang in tgt_langs:
        rows = fetch_en_chunks(conn, tgt_lang, source_filter, limit)
        log.info("EN→%s: %d chunks to translate", tgt_lang.upper(), len(rows))
        if not rows:
            stats[tgt_lang] = 0
            continue

        done = 0
        t0 = time.time()

        for i in range(0, len(rows), batch_size):
            batch = rows[i : i + batch_size]
            chunk_ids  = [r[0] for r in batch]
            titles_en  = [r[1] or "" for r in batch]
            contents_en = [r[2] for r in batch]

            # Translate content
            try:
                contents_tgt = translate_batch(model, tok, contents_en, "en", tgt_lang, device)
            except Exception as e:
                log.error("Batch %d failed: %s", i // batch_size, e)
                continue

            # Translate titles (short, can be batched)
            try:
                titles_tgt = translate_batch(model, tok, titles_en, "en", tgt_lang, device)
            except Exception:
                titles_tgt = [""] * len(batch)

            for chunk_id, title_tgt, content_tgt, row in zip(
                chunk_ids, titles_tgt, contents_tgt, batch
            ):
                write_translation(conn, chunk_id, tgt_lang, title_tgt, content_tgt)
                done += 1

                if training_pairs_file:
                    save_training_pair(
                        training_pairs_file,
                        source_lang="en",
                        target_lang=tgt_lang,
                        source_text=row[2],
                        translated_text=content_tgt,
                        chunk_id=chunk_id,
                    )

            elapsed = time.time() - t0
            rate = done / elapsed if elapsed else 0
            eta = (len(rows) - done) / rate if rate else 0
            log.info(
                "  EN→%s  %d/%d  %.2f chunk/s  ETA %.0fs",
                tgt_lang.upper(), done, len(rows), rate, eta,
            )

        stats[tgt_lang] = done
        log.info("EN→%s done: %d chunks translated", tgt_lang.upper(), done)

    conn.close()
    return stats


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Bridge-translate EN chunk_content → AR + ES using NLLB-200.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--db-path", default=str(DB_PATH))
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--target-langs", default="ar,es",
                        help="Target languages (comma-separated)")
    parser.add_argument("--source", default=None,
                        help="Filter to specific chunk source")
    parser.add_argument("--limit", type=int, default=None,
                        help="Max chunks per language (for testing)")
    parser.add_argument("--batch-size", type=int, default=8,
                        help="Inference batch size")
    parser.add_argument("--training-pairs",
                        default="knowledge-base/training_pairs_bridge.jsonl",
                        help="Output JSONL for training pairs")
    args = parser.parse_args()

    db_path = Path(args.db_path)
    if not db_path.exists():
        log.error("kb.db not found: %s", db_path)
        sys.exit(1)

    tgt_langs = [l.strip() for l in args.target_langs.split(",")]
    pairs_file = ROOT / args.training_pairs if args.training_pairs else None

    log.info("=" * 60)
    log.info("  Bridge Translation: EN → %s", " + ".join(tgt_langs))
    log.info("  Model: %s", NLLB_MODEL_ID)
    log.info("  Device: %s", args.device)
    log.info("=" * 60)

    stats = run_bridge(
        db_path=db_path,
        device=args.device,
        tgt_langs=tgt_langs,
        source_filter=args.source,
        limit=args.limit,
        batch_size=args.batch_size,
        training_pairs_file=pairs_file,
    )

    log.info("=" * 60)
    for lang, n in stats.items():
        log.info("  EN→%s: %d chunks translated", lang.upper(), n)
    log.info("=" * 60)

    if pairs_file and pairs_file.exists():
        n_pairs = sum(1 for _ in open(pairs_file, encoding="utf-8"))
        log.info("Training pairs written: %d → %s", n_pairs, pairs_file)


if __name__ == "__main__":
    main()
