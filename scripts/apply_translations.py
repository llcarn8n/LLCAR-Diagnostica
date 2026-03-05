#!/usr/bin/env python3
"""Apply Claude translations from parts_translations_claude.json to the SQLite database."""

import json
import sqlite3
import os

TRANSLATIONS_FILE = os.path.join(os.path.dirname(__file__), "parts_translations_claude.json")
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "knowledge-base", "kb.db")

def main():
    # Load translations
    with open(TRANSLATIONS_FILE, "r", encoding="utf-8") as f:
        translations = json.load(f)

    print(f"Loaded {len(translations)} translations from JSON.")

    # Connect to DB
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check that the parts table and required columns exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='parts'")
    if not cursor.fetchone():
        print("ERROR: Table 'parts' does not exist in the database.")
        conn.close()
        return

    cursor.execute("PRAGMA table_info(parts)")
    columns = {row[1] for row in cursor.fetchall()}
    print(f"Columns in 'parts' table: {columns}")

    if "part_name_zh" not in columns or "part_name_en" not in columns:
        print("ERROR: Required columns 'part_name_zh' or 'part_name_en' not found.")
        conn.close()
        return

    # Stats before
    cursor.execute("SELECT COUNT(*) FROM parts")
    total_parts = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM parts WHERE part_name_en IS NOT NULL AND part_name_en != ''")
    before_with_en = cursor.fetchone()[0]

    print(f"\nBefore update:")
    print(f"  Total parts: {total_parts}")
    print(f"  Parts with English names: {before_with_en}")
    print(f"  Parts without English names: {total_parts - before_with_en}")

    # Apply translations
    updated = 0
    skipped_no_match = 0
    skipped_already_translated = 0

    for zh_name, en_name in translations.items():
        # Only update rows where part_name_en is NULL or empty
        cursor.execute(
            "UPDATE parts SET part_name_en = ? WHERE part_name_zh = ? AND (part_name_en IS NULL OR part_name_en = '')",
            (en_name, zh_name)
        )
        rows_affected = cursor.rowcount
        if rows_affected > 0:
            updated += rows_affected
        else:
            # Check if it exists at all
            cursor.execute("SELECT COUNT(*) FROM parts WHERE part_name_zh = ?", (zh_name,))
            count = cursor.fetchone()[0]
            if count == 0:
                skipped_no_match += 1
            else:
                skipped_already_translated += count

    conn.commit()

    # Stats after
    cursor.execute("SELECT COUNT(*) FROM parts WHERE part_name_en IS NOT NULL AND part_name_en != ''")
    after_with_en = cursor.fetchone()[0]

    print(f"\nUpdate complete:")
    print(f"  Rows updated: {updated}")
    print(f"  Translations with no DB match: {skipped_no_match}")
    print(f"  Already had English translation: {skipped_already_translated}")

    print(f"\nAfter update:")
    print(f"  Total parts: {total_parts}")
    print(f"  Parts with English names: {after_with_en}")
    print(f"  Parts without English names: {total_parts - after_with_en}")
    print(f"  Coverage: {after_with_en / total_parts * 100:.1f}%")

    # Show sample of remaining untranslated parts
    cursor.execute(
        "SELECT part_name_zh FROM parts WHERE (part_name_en IS NULL OR part_name_en = '') LIMIT 20"
    )
    remaining = cursor.fetchall()
    if remaining:
        print(f"\nSample of remaining untranslated parts (up to 20):")
        for row in remaining:
            print(f"  {row[0]}")

    conn.close()

if __name__ == "__main__":
    main()
