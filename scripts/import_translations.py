#!/usr/bin/env python3
"""Import agent-translated batches into kb.db chunk_content table."""

import sqlite3
import json
import os
import sys
import glob
from datetime import datetime, timezone

DB_PATH = "knowledge-base/kb.db"
OUTPUT_DIR = "knowledge-base/translate_batches"
TRAINING_PAIRS_FILE = "knowledge-base/training_pairs_tier1.jsonl"


def main():
    sys.stdout = open(sys.stdout.fileno(), mode="w", encoding="utf-8", buffering=1)

    conn = sqlite3.connect(DB_PATH, timeout=60)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=60000")
    c = conn.cursor()

    # Find all output files
    output_files = sorted(glob.glob(os.path.join(OUTPUT_DIR, "batch_*_out.json")))
    if not output_files:
        print("No output files found!")
        return

    total_inserted = 0
    total_pairs = 0
    skipped = 0
    errors = 0
    now = datetime.now(timezone.utc).isoformat()

    # Open training pairs file for append
    tp_file = open(TRAINING_PAIRS_FILE, "a", encoding="utf-8")

    for fpath in output_files:
        batch_name = os.path.basename(fpath)
        try:
            with open(fpath, encoding="utf-8") as f:
                results = json.load(f)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            print(f"ERROR reading {batch_name}: {e}")
            errors += 1
            continue

        batch_inserted = 0
        for item in results:
            chunk_id = item.get("id")
            lang = item.get("lang")
            title = item.get("title", "")
            content = item.get("content", "")

            if not chunk_id or not lang or not content:
                skipped += 1
                continue

            # Check if already exists
            c.execute(
                "SELECT 1 FROM chunk_content WHERE chunk_id=? AND lang=?",
                (chunk_id, lang),
            )
            if c.fetchone():
                skipped += 1
                continue

            # Insert
            c.execute(
                """INSERT INTO chunk_content
                   (chunk_id, lang, title, content, translated_by, quality_score, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (chunk_id, lang, title, content, "claude-sonnet-4-6", 0.85, now),
            )
            batch_inserted += 1

            # Get source text for training pair
            c.execute("SELECT title, content, source_language FROM chunks WHERE id=?", (chunk_id,))
            row = c.fetchone()
            if row:
                src_title, src_content, src_lang = row
                pair = {
                    "source_lang": src_lang,
                    "target_lang": lang,
                    "source_text": f"{src_title}\n{src_content}" if src_title else src_content,
                    "target_text": f"{title}\n{content}" if title else content,
                    "chunk_id": chunk_id,
                    "translator": "claude-sonnet-4-6",
                }
                tp_file.write(json.dumps(pair, ensure_ascii=False) + "\n")
                total_pairs += 1

        conn.commit()
        total_inserted += batch_inserted
        print(f"  {batch_name}: +{batch_inserted} translations")

    tp_file.close()
    conn.close()

    print(f"\n=== Import Summary ===")
    print(f"Files processed: {len(output_files)}")
    print(f"Translations inserted: {total_inserted}")
    print(f"Training pairs added: {total_pairs}")
    print(f"Skipped (existing/empty): {skipped}")
    print(f"Errors: {errors}")


if __name__ == "__main__":
    main()
