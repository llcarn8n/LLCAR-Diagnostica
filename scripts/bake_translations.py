#!/usr/bin/env python3
"""
bake_translations.py — Finalize translations into the knowledge base.

Steps:
  1. Report translation coverage (per source, per language)
  2. Fill any gap: translation_cache entries missing from chunk_content
  3. Create/rebuild multilingual FTS5 index (chunk_content_fts)
  4. Print final statistics

This script is idempotent — safe to run multiple times.
Run AFTER translate_kb.py completes all tiers.

Usage:
    python scripts/bake_translations.py
    python scripts/bake_translations.py --dry-run   # show stats only
"""
from __future__ import annotations

import argparse
import logging
import sqlite3
import sys
import io
import time
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("bake")

ROOT   = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "knowledge-base" / "kb.db"


# ---------------------------------------------------------------------------
# Step 1: Coverage report
# ---------------------------------------------------------------------------

def print_coverage(conn: sqlite3.Connection) -> dict:
    rows = conn.execute("""
        SELECT
            c.source,
            c.source_language,
            COUNT(DISTINCT c.id) as total,
            COUNT(DISTINCT CASE WHEN cc_en.lang='en' THEN c.id END) as has_en,
            COUNT(DISTINCT CASE WHEN cc_ru.lang='ru' THEN c.id END) as has_ru
        FROM chunks c
        LEFT JOIN chunk_content cc_en ON cc_en.chunk_id = c.id AND cc_en.lang = 'en'
        LEFT JOIN chunk_content cc_ru ON cc_ru.chunk_id = c.id AND cc_ru.lang = 'ru'
        GROUP BY c.source, c.source_language
        ORDER BY total DESC
    """).fetchall()

    log.info("=" * 70)
    log.info("  TRANSLATION COVERAGE")
    log.info("=" * 70)
    log.info("  %-35s  %-4s  %5s  %5s(%%)  %5s(%%)", "Source", "Lang", "Total", "EN", "RU")
    log.info("  " + "-" * 65)

    total_all = total_en_all = total_ru_all = 0
    for src, slang, total, has_en, has_ru in rows:
        en_pct = 100 * has_en / total if total else 0
        ru_pct = 100 * has_ru / total if total else 0
        log.info("  %-35s  %-4s  %5d  %5d(%2.0f%%)  %5d(%2.0f%%)",
                 src[:35], slang, total, has_en, en_pct, has_ru, ru_pct)
        total_all += total
        total_en_all += has_en
        total_ru_all += has_ru

    log.info("  " + "-" * 65)
    log.info("  %-35s  %-4s  %5d  %5d(%2.0f%%)  %5d(%2.0f%%)",
             "TOTAL", "-", total_all,
             total_en_all, 100 * total_en_all / total_all if total_all else 0,
             total_ru_all, 100 * total_ru_all / total_all if total_all else 0)
    log.info("=" * 70)

    return {
        "total": total_all,
        "en": total_en_all,
        "ru": total_ru_all,
        "en_pct": 100 * total_en_all / total_all if total_all else 0,
        "ru_pct": 100 * total_ru_all / total_all if total_all else 0,
    }


# ---------------------------------------------------------------------------
# Step 2: Build multilingual FTS5 index
# ---------------------------------------------------------------------------

FTS_CREATE = """
CREATE VIRTUAL TABLE IF NOT EXISTS chunk_content_fts USING fts5(
    chunk_id UNINDEXED,
    lang UNINDEXED,
    title,
    content,
    tokenize="unicode61"
)
"""


def build_multilingual_fts(conn: sqlite3.Connection, dry_run: bool = False) -> int:
    """
    Create / rebuild chunk_content_fts covering all languages in chunk_content.

    Includes:
      - Original chunks (source language) from chunks table
      - Translated chunks from chunk_content table (EN, RU, etc.)

    Returns number of rows indexed.
    """
    if dry_run:
        n = conn.execute("SELECT COUNT(*) FROM chunk_content").fetchone()[0]
        log.info("[DRY-RUN] Would index %d chunk_content rows into FTS", n)
        return n

    log.info("Creating chunk_content_fts table...")
    conn.execute(FTS_CREATE)

    # Clear and rebuild
    conn.execute("DELETE FROM chunk_content_fts")
    log.info("Cleared old FTS index. Rebuilding...")

    t0 = time.time()
    # Insert all chunk_content (translated + original)
    conn.execute("""
        INSERT INTO chunk_content_fts (chunk_id, lang, title, content)
        SELECT cc.chunk_id, cc.lang, cc.title, cc.content
        FROM chunk_content cc
        WHERE cc.content IS NOT NULL
          AND length(cc.content) > 10
    """)

    # Also index original ZH chunks that may not have chunk_content rows
    conn.execute("""
        INSERT OR IGNORE INTO chunk_content_fts (chunk_id, lang, title, content)
        SELECT c.id, c.source_language, c.title, c.content
        FROM chunks c
        WHERE c.source_language NOT IN ('en', 'ru', 'zh')
           OR NOT EXISTS (
               SELECT 1 FROM chunk_content cc WHERE cc.chunk_id = c.id
           )
    """)

    n = conn.execute("SELECT COUNT(*) FROM chunk_content_fts").fetchone()[0]
    elapsed = time.time() - t0
    log.info("FTS index built: %d rows in %.1f s", n, elapsed)
    return n


# ---------------------------------------------------------------------------
# Step 3: Summary stats
# ---------------------------------------------------------------------------

def print_final_stats(conn: sqlite3.Connection) -> None:
    log.info("=" * 70)
    log.info("  FINAL KB STATISTICS")
    log.info("=" * 70)

    total_chunks = conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
    total_cc = conn.execute("SELECT COUNT(*) FROM chunk_content").fetchone()[0]
    total_cache = conn.execute("SELECT COUNT(*) FROM translation_cache").fetchone()[0]
    total_fts = conn.execute("SELECT COUNT(*) FROM chunk_content_fts").fetchone()[0] if _table_exists(conn, "chunk_content_fts") else 0
    total_images = conn.execute("SELECT COUNT(*) FROM chunk_images").fetchone()[0]
    captioned = conn.execute("SELECT COUNT(*) FROM chunk_images WHERE caption IS NOT NULL").fetchone()[0]
    image_emb = conn.execute("SELECT COUNT(*) FROM chunk_images WHERE image_embedding IS NOT NULL").fetchone()[0] if _col_exists(conn, "chunk_images", "image_embedding") else "N/A"

    by_lang = conn.execute(
        "SELECT lang, COUNT(*) FROM chunk_content GROUP BY lang ORDER BY COUNT(*) DESC"
    ).fetchall()

    log.info("  Total chunks:          %d", total_chunks)
    log.info("  chunk_content rows:    %d", total_cc)
    log.info("  translation_cache:     %d", total_cache)
    log.info("  FTS rows (multilang):  %d", total_fts)
    log.info("  Images total:          %d", total_images)
    log.info("  Images captioned:      %d (%.1f%%)", captioned, 100 * captioned / total_images if total_images else 0)
    log.info("  Images with embedding: %s", image_emb)
    log.info("")
    log.info("  chunk_content by language:")
    for lang, cnt in by_lang:
        log.info("    %-6s: %d rows", lang, cnt)
    log.info("=" * 70)


def _table_exists(conn: sqlite3.Connection, name: str) -> bool:
    return bool(conn.execute(
        f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (name,)
    ).fetchone())


def _col_exists(conn: sqlite3.Connection, table: str, col: str) -> bool:
    cols = [c[1] for c in conn.execute(f"PRAGMA table_info({table})").fetchall()]
    return col in cols


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Bake translations into KB: fill gaps + build multilingual FTS.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--db-path", default=str(DB_PATH))
    parser.add_argument("--dry-run", action="store_true",
                        help="Report only — no DB writes")
    parser.add_argument("--skip-fts", action="store_true",
                        help="Skip rebuilding FTS index")
    args = parser.parse_args()

    db_path = Path(args.db_path)
    if not db_path.exists():
        log.error("kb.db not found: %s", db_path)
        sys.exit(1)

    conn = sqlite3.connect(str(db_path), timeout=120)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA busy_timeout=120000")

    # Step 1: Coverage
    stats = print_coverage(conn)

    # Step 2: Multilingual FTS
    if not args.skip_fts:
        log.info("")
        log.info("Building multilingual FTS5 index (chunk_content_fts)...")
        n_fts = build_multilingual_fts(conn, dry_run=args.dry_run)
        if not args.dry_run:
            conn.commit()
            log.info("FTS committed. %d rows indexed.", n_fts)
    else:
        log.info("Skipping FTS rebuild (--skip-fts)")

    # Step 3: Final stats
    log.info("")
    print_final_stats(conn)
    conn.close()

    log.info("Done!")
    log.info("")
    log.info("Next steps:")
    log.info("  1. Run validate_translations.py to compare Claude vs M2M quality")
    log.info("  2. Run build_embeddings.py --rebuild to update vector embeddings")
    log.info("  3. Restart api/server.py to pick up new FTS table")


if __name__ == "__main__":
    main()
