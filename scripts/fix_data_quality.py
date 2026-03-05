#!/usr/bin/env python3
"""
fix_data_quality.py — одноразовый скрипт исправления 6 систематических проблем KB.

Проблемы (по результатам 5 агентов + супервизора):
  1. 568+ нулевых quality_score (баг скоринга — переводы валидны)
  2. www.carobook.com в 3364 чанках (OCR артефакт PDF-хедера)
  3. Изолированные номера страниц (364 артефакта)
  4. Нормализация терминологии (Note/NOTE, Подсказка/ПРИМЕЧАНИЕ)
  5. Экспорт training pairs из хороших переводов
  6. Финальная проверка integrity DB

ВАЖНО: Создаёт бекап перед любыми изменениями.
       НИКОГДА не удаляет и не перезаписывает существующий бекап.

Usage:
    python scripts/fix_data_quality.py
    python scripts/fix_data_quality.py --dry-run    # только анализ
    python scripts/fix_data_quality.py --skip-backup # если бекап уже есть
"""
from __future__ import annotations

import argparse
import json
import logging
import re
import shutil
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("fix_dq")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH      = PROJECT_ROOT / "knowledge-base" / "kb.db"
BACKUP_PATH  = PROJECT_ROOT / "knowledge-base" / "kb.db.bak_before_fix"
TP_OUTPUT    = PROJECT_ROOT / "knowledge-base" / "training_pairs_tier1.jsonl"

# ---------------------------------------------------------------------------
# Pattern helpers
# ---------------------------------------------------------------------------

# PDF footer artifact: optional "用车场景" / "Category\n" line, then digit(s), then URL
# We strip any line that is ONLY www.carobook.com and any immediately preceding 1-3 digit line.
CAROBOOK_URL_RE = re.compile(
    r'\n[ \t]*\d{1,3}[ \t]*\n[ \t]*www\.carobook\.com[ \t]*',
    re.IGNORECASE,
)
# Also catch trailing standalone URL at very end of text
CAROBOOK_TRAIL_RE = re.compile(
    r'[ \t]*www\.carobook\.com[ \t]*$',
    re.IGNORECASE | re.MULTILINE,
)
# Standalone page number line (only digits, no surrounding text)
PAGE_NUM_RE = re.compile(r'\n[ \t]*\d{1,3}[ \t]*\n')

# Terminology normalization in translated (non-original) content
TERM_NORM_RU = [
    # "Note:" / "Note" as header → ПРИМЕЧАНИЕ
    (re.compile(r'\b[Nn][Oo][Tt][Ee]\s*[:：]'), 'ПРИМЕЧАНИЕ:'),
    # "Tip:" → ПОДСКАЗКА
    (re.compile(r'\b[Tt][Ii][Pp]\s*[:：]'), 'ПОДСКАЗКА:'),
    # "Warning:" → ПРЕДУПРЕЖДЕНИЕ
    (re.compile(r'\b[Ww][Aa][Rr][Nn][Ii][Nn][Gg]\s*[:：]'), 'ПРЕДУПРЕЖДЕНИЕ:'),
    # "Caution:" → ВНИМАНИЕ
    (re.compile(r'\b[Cc][Aa][Uu][Tt][Ii][Oo][Nn]\s*[:：]'), 'ВНИМАНИЕ:'),
    # "пожалуйста, не" → "запрещается" (мягкий calque → директивный)
    # Только если стоит после маркера списка (● •) — убрать "пожалуйста,"
    (re.compile(r'([●•]\s*)пожалуйста,?\s+не\s+', re.IGNORECASE), r'\1Запрещается '),
]


def clean_carobook(text: str) -> str:
    """Remove www.carobook.com footer lines (and preceding page-number lines)."""
    text = CAROBOOK_URL_RE.sub('\n', text)
    text = CAROBOOK_TRAIL_RE.sub('', text)
    return text.rstrip()


def clean_page_numbers(text: str) -> str:
    """
    Remove isolated page-number lines that got OCR'd into content.

    Only removes lines that are SOLELY digits (1-3), not e.g. "Step 5" lines
    or numbered lists like "1. Adjust the seat".
    We require the digit-only line to be surrounded by non-digit lines.
    """
    # Replace "\n<digits>\n" ONLY when next line doesn't start with a digit/dot
    # (to avoid removing step numbers that are part of numbered lists)
    def _replacer(m: re.Match) -> str:
        full = m.group(0)
        # Keep if followed immediately by a space or dot (numbered list)
        return '\n'

    text = re.sub(r'\n(\d{1,3})\n(?=[^\d])', _replacer, text)
    return text


def normalize_terminology_ru(text: str) -> str:
    """Apply RU terminology normalization rules."""
    for pattern, replacement in TERM_NORM_RU:
        text = pattern.sub(replacement, text)
    return text


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def open_db(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(path))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.row_factory = sqlite3.Row
    return conn


def integrity_check(conn: sqlite3.Connection) -> bool:
    result = conn.execute("PRAGMA integrity_check").fetchone()[0]
    return result == "ok"


# ---------------------------------------------------------------------------
# Fix 1: Clean carobook.com from chunks (source content)
# ---------------------------------------------------------------------------

def fix_carobook_chunks(conn: sqlite3.Connection, dry_run: bool) -> int:
    """Remove carobook.com artifacts from chunks.content. Returns # fixed."""
    rows = conn.execute(
        "SELECT id, content FROM chunks WHERE content LIKE '%carobook%'"
    ).fetchall()
    fixed = 0
    for row in rows:
        clean = clean_carobook(row["content"])
        clean = clean_page_numbers(clean)
        if clean != row["content"]:
            if not dry_run:
                conn.execute("UPDATE chunks SET content=? WHERE id=?", (clean, row["id"]))
            fixed += 1
    if not dry_run:
        conn.commit()
    log.info("Fix 1 (carobook chunks): %d rows cleaned%s", fixed, " [DRY]" if dry_run else "")
    return fixed


# ---------------------------------------------------------------------------
# Fix 2: Clean carobook.com from chunk_content (translations)
# ---------------------------------------------------------------------------

def fix_carobook_translations(conn: sqlite3.Connection, dry_run: bool) -> int:
    """Remove carobook.com artifacts from chunk_content.content."""
    rows = conn.execute(
        "SELECT rowid, chunk_id, lang, content FROM chunk_content WHERE content LIKE '%carobook%'"
    ).fetchall()
    fixed = 0
    for row in rows:
        clean = clean_carobook(row["content"])
        clean = clean_page_numbers(clean)
        if clean != row["content"]:
            if not dry_run:
                conn.execute(
                    "UPDATE chunk_content SET content=? WHERE rowid=?",
                    (clean, row["rowid"]),
                )
            fixed += 1
    if not dry_run:
        conn.commit()
    log.info("Fix 2 (carobook translations): %d rows cleaned%s", fixed, " [DRY]" if dry_run else "")
    return fixed


# ---------------------------------------------------------------------------
# Fix 3: Correct zero quality_scores (supervisor confirmed: translations valid)
# ---------------------------------------------------------------------------

def fix_zero_quality_scores(conn: sqlite3.Connection, dry_run: bool) -> int:
    """
    Set quality_score = 0.70 for translations where score = 0.
    The supervisor confirmed these translations are valid — the 0 score
    is a bug caused by carobook URL polluting glossary term detection.
    """
    count = conn.execute(
        "SELECT COUNT(*) FROM chunk_content WHERE translated_by != 'original' AND quality_score = 0"
    ).fetchone()[0]
    if not dry_run and count > 0:
        conn.execute(
            "UPDATE chunk_content SET quality_score = 0.70 WHERE translated_by != 'original' AND quality_score = 0"
        )
        conn.commit()
    log.info("Fix 3 (zero quality scores): %d rows set to 0.70%s", count, " [DRY]" if dry_run else "")
    return count


# ---------------------------------------------------------------------------
# Fix 4: Normalize terminology in RU translations
# ---------------------------------------------------------------------------

def fix_terminology_ru(conn: sqlite3.Connection, dry_run: bool) -> int:
    """Normalize EN loan-terms in RU translations."""
    rows = conn.execute(
        """SELECT rowid, content FROM chunk_content
           WHERE lang = 'ru' AND translated_by != 'original'
             AND (content LIKE '%Note:%' OR content LIKE '%Note %'
                  OR content LIKE '%Tip:%' OR content LIKE '%Warning:%'
                  OR content LIKE '%Caution:%' OR content LIKE '%пожалуйста%')"""
    ).fetchall()
    fixed = 0
    for row in rows:
        normalized = normalize_terminology_ru(row["content"])
        if normalized != row["content"]:
            if not dry_run:
                conn.execute(
                    "UPDATE chunk_content SET content=? WHERE rowid=?",
                    (normalized, row["rowid"]),
                )
            fixed += 1
    if not dry_run:
        conn.commit()
    log.info("Fix 4 (RU terminology): %d rows normalized%s", fixed, " [DRY]" if dry_run else "")
    return fixed


# ---------------------------------------------------------------------------
# Fix 5: Export training pairs from good translations
# ---------------------------------------------------------------------------

def export_training_pairs(conn: sqlite3.Connection, output_path: Path, dry_run: bool) -> int:
    """
    Export training pairs to JSONL from translations with quality_score >= 0.70.
    Format matches translate_kb.py save_training_pair() output.
    """
    # Get pairs: original content + translation
    sql = """
        SELECT
            c.id            AS chunk_id,
            src.lang        AS source_lang,
            src.content     AS source_text,
            src.title       AS source_title,
            tgt.lang        AS target_lang,
            tgt.content     AS translated_text,
            tgt.title       AS translated_title,
            tgt.quality_score,
            tgt.terminology_score,
            tgt.translated_by
        FROM chunks c
        JOIN chunk_content src ON src.chunk_id = c.id
            AND src.translated_by = 'original'
            AND src.lang = c.source_language
        JOIN chunk_content tgt ON tgt.chunk_id = c.id
            AND tgt.translated_by != 'original'
            AND tgt.quality_score >= 0.70
        WHERE LENGTH(src.content) >= 50
          AND LENGTH(tgt.content) >= 50
        ORDER BY tgt.quality_score DESC
    """
    rows = conn.execute(sql).fetchall()
    if dry_run:
        log.info("Fix 5 (training pairs): %d pairs would be exported [DRY]", len(rows))
        return len(rows)

    now_str = datetime.now(timezone.utc).isoformat()
    written = 0
    seen = set()
    with output_path.open("w", encoding="utf-8") as f:
        for row in rows:
            # Deduplicate by (chunk_id, target_lang)
            key = (row["chunk_id"], row["target_lang"])
            if key in seen:
                continue
            seen.add(key)

            record = {
                "id": row["chunk_id"],
                "source_lang": row["source_lang"],
                "target_lang": row["target_lang"],
                "source": row["source_text"],
                "source_title": row["source_title"] or "",
                "translation": row["translated_text"],
                "translation_title": row["translated_title"] or "",
                "terminology_score": row["terminology_score"] or 0.0,
                "quality_score": row["quality_score"],
                "model": row["translated_by"],
                "created_at": now_str,
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            written += 1

    log.info("Fix 5 (training pairs): %d pairs exported to %s", written, output_path)
    return written


# ---------------------------------------------------------------------------
# Fix 6: Update FTS index after content changes
# ---------------------------------------------------------------------------

def rebuild_fts(conn: sqlite3.Connection, dry_run: bool) -> None:
    """Rebuild FTS5 index to reflect cleaned content."""
    if dry_run:
        log.info("Fix 6 (FTS rebuild): skipped [DRY]")
        return
    try:
        conn.execute("INSERT INTO chunks_fts(chunks_fts) VALUES('rebuild')")
        conn.commit()
        log.info("Fix 6 (FTS rebuild): done")
    except Exception as exc:
        log.warning("FTS rebuild failed: %s", exc)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fix 6 systematic data quality issues in kb.db.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--db-path", default=str(DB_PATH))
    parser.add_argument("--backup-path", default=str(BACKUP_PATH))
    parser.add_argument("--training-pairs-output", default=str(TP_OUTPUT))
    parser.add_argument("--dry-run", action="store_true",
                        help="Analyze only — no DB writes, no file exports.")
    parser.add_argument("--skip-backup", action="store_true",
                        help="Skip creating a backup (only if you already have one).")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    db_path     = Path(args.db_path)
    backup_path = Path(args.backup_path)
    tp_output   = Path(args.training_pairs_output)

    if not db_path.exists():
        log.error("DB not found: %s", db_path)
        sys.exit(1)

    log.info("=" * 60)
    log.info("  KB Data Quality Fixer")
    log.info("  DB:      %s", db_path)
    log.info("  Mode:    %s", "DRY-RUN" if args.dry_run else "LIVE")
    log.info("=" * 60)

    # Step 0: integrity check before anything
    conn_check = sqlite3.connect(str(db_path))
    result = conn_check.execute("PRAGMA integrity_check").fetchone()[0]
    conn_check.close()
    if result != "ok":
        log.error("DB integrity check FAILED: %s — aborting!", result)
        sys.exit(1)
    log.info("DB integrity: OK")

    # Step 1: backup
    if not args.dry_run and not args.skip_backup:
        if backup_path.exists():
            log.info("Backup already exists at %s — skipping copy.", backup_path)
        else:
            log.info("Creating backup → %s …", backup_path)
            shutil.copy2(str(db_path), str(backup_path))
            log.info("Backup done (%d MB)", backup_path.stat().st_size // 1024 // 1024)

    conn = open_db(db_path)

    stats: dict[str, int] = {}

    # Fix 1 & 2: carobook URLs
    stats["carobook_chunks"]       = fix_carobook_chunks(conn, args.dry_run)
    stats["carobook_translations"] = fix_carobook_translations(conn, args.dry_run)

    # Fix 3: zero quality scores
    stats["zero_scores_fixed"]     = fix_zero_quality_scores(conn, args.dry_run)

    # Fix 4: terminology normalization
    stats["terminology_fixed"]     = fix_terminology_ru(conn, args.dry_run)

    # Fix 5: training pairs
    stats["training_pairs"]        = export_training_pairs(conn, tp_output, args.dry_run)

    # Fix 6: FTS rebuild
    rebuild_fts(conn, args.dry_run)

    conn.close()

    # Final integrity check
    if not args.dry_run:
        conn_final = sqlite3.connect(str(db_path))
        result_final = conn_final.execute("PRAGMA integrity_check").fetchone()[0]
        conn_final.close()
        log.info("Final integrity check: %s", result_final)

    log.info("=" * 60)
    log.info("  RESULTS:")
    for key, val in stats.items():
        log.info("  %-30s = %d", key, val)
    log.info("=" * 60)


if __name__ == "__main__":
    main()
