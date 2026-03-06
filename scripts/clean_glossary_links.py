"""
Phase 1.3: Clean noise glossary links.
Removes over-linked terms (>30% of chunks) and short generic terms.

Usage: python scripts/clean_glossary_links.py [--dry-run]
"""

import sqlite3
import sys
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "knowledge-base", "kb.db")

# Explicit noise terms to always remove
STOP_TERMS = {
    "car", "auto", "vehicle", "manual", "owner", "system", "component",
    "part", "assembly", "unit", "device", "module", "element",
    "age", "ang", "output", "wander", "detect", "tracc", "sensing",
    "automatically", "warning", "hour", "part",
    "owner_s_manual", "li_auto",
}


def main():
    dry_run = "--dry-run" in sys.argv
    db_path = os.path.abspath(DB_PATH)
    print(f"DB: {db_path}")
    if dry_run:
        print("=== DRY RUN MODE ===\n")

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    total_links = cur.execute("SELECT COUNT(*) FROM chunk_glossary").fetchone()[0]
    total_chunks = cur.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
    threshold = int(total_chunks * 0.3)
    print(f"Total glossary links: {total_links}")
    print(f"Total chunks: {total_chunks}")
    print(f"Frequency threshold (30%): {threshold}\n")

    # 1. Find over-linked terms
    overlinked = cur.execute("""
        SELECT glossary_id, COUNT(*) as cnt
        FROM chunk_glossary
        GROUP BY glossary_id
        HAVING cnt > ?
        ORDER BY cnt DESC
    """, (threshold,)).fetchall()

    print(f"=== Over-linked terms (>{threshold} chunks) ===")
    overlinked_ids = set()
    overlinked_count = 0
    for gid, cnt in overlinked:
        # Strip @layer suffix for display
        print(f"  {gid}: {cnt} links")
        overlinked_ids.add(gid)
        overlinked_count += cnt

    # 2. Stop-list terms (including with @layer suffix)
    stop_links = cur.execute("""
        SELECT glossary_id, COUNT(*) as cnt
        FROM chunk_glossary
        GROUP BY glossary_id
    """).fetchall()

    stoplist_ids = set()
    stoplist_count = 0
    for gid, cnt in stop_links:
        base = gid.split("@")[0].lower().strip()
        if base in STOP_TERMS and gid not in overlinked_ids:
            stoplist_ids.add(gid)
            stoplist_count += cnt

    print(f"\n=== Stop-list terms (not already caught by frequency) ===")
    for gid in sorted(stoplist_ids)[:20]:
        print(f"  {gid}")
    if len(stoplist_ids) > 20:
        print(f"  ... and {len(stoplist_ids) - 20} more")
    print(f"  Total links from stop-list: {stoplist_count}")

    # 3. Short generic terms (< 3 chars base, not already caught)
    # Keep technical abbreviations: abs, ecu, esp, hud, led, obd, etc.
    KEEP_SHORT = {
        "abs", "ecu", "esp", "hud", "led", "obd", "can", "air", "key",
        "vin", "usb", "gps", "ota", "bms", "eps", "tcs", "drl", "acc",
    }
    short_ids = set()
    short_count = 0
    for gid, cnt in stop_links:
        if gid in overlinked_ids or gid in stoplist_ids:
            continue
        base = gid.split("@")[0].lower()
        if len(base) < 3 and base not in KEEP_SHORT:
            short_ids.add(gid)
            short_count += cnt

    print(f"\n=== Short terms (<4 chars base) ===")
    for gid in sorted(short_ids)[:20]:
        print(f"  {gid}")
    print(f"  Total links from short terms: {short_count}")

    # Total to remove
    all_remove = overlinked_ids | stoplist_ids | short_ids
    total_remove = overlinked_count + stoplist_count + short_count
    remaining = total_links - total_remove

    print(f"\n=== Summary ===")
    print(f"  Terms to remove: {len(all_remove)}")
    print(f"  Links to remove: {total_remove} ({total_remove*100/total_links:.1f}%)")
    print(f"  Links remaining: {remaining} ({remaining*100/total_links:.1f}%)")

    if dry_run:
        print("\n(Dry run — no changes made)")
        conn.close()
        return

    # Execute deletion
    print("\nDeleting...")
    for gid in all_remove:
        cur.execute("DELETE FROM chunk_glossary WHERE glossary_id = ?", (gid,))

    conn.commit()
    final = cur.execute("SELECT COUNT(*) FROM chunk_glossary").fetchone()[0]
    print(f"Done! Links: {total_links} -> {final}")

    conn.close()


if __name__ == "__main__":
    main()
