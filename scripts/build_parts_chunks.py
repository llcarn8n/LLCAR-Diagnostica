"""
Phase 1.4: Build parts↔chunks bridge table.
Links parts to KB chunks via FTS5 name matching and system matching.

Usage: python scripts/build_parts_chunks.py [--dry-run]
"""

import sqlite3
import sys
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "knowledge-base", "kb.db")

# Map part system_en → chunk layer
SYSTEM_TO_LAYER = {
    "Power Battery System": "battery",
    "Drive Motor System": "ev",
    "Range Extender System": "engine",
    "Charging System": "ev",
    "Thermal Management System": "hvac",
    "Service Brake System": "brakes",
    "Parking Brake System": "brakes",
    "Steering System": "chassis",
    "Suspension System": "chassis",
    "Front Suspension": "chassis",
    "Rear Suspension": "chassis",
    "Wheel & Tire": "chassis",
    "Body Exterior": "body",
    "Body Interior": "interior",
    "Seat System": "interior",
    "Restraint System": "body",
    "Lighting System": "lighting",
    "Exterior Lighting": "lighting",
    "Interior Lighting": "lighting",
    "HVAC System": "hvac",
    "Infotainment System": "infotainment",
    "ADAS System": "adas",
    "Wiper System": "body",
    "Door System": "body",
    "Trunk System": "body",
    "Glass System": "body",
    "Sensor System": "sensors",
    "Drivetrain System": "drivetrain",
}


def main():
    dry_run = "--dry-run" in sys.argv
    db_path = os.path.abspath(DB_PATH)
    print(f"DB: {db_path}")
    if dry_run:
        print("=== DRY RUN ===\n")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Create table
    if not dry_run:
        cur.execute("DROP TABLE IF EXISTS parts_chunks")
        cur.execute("""
            CREATE TABLE parts_chunks (
                part_id INTEGER NOT NULL,
                chunk_id TEXT NOT NULL,
                match_type TEXT NOT NULL,
                confidence REAL DEFAULT 0.5,
                PRIMARY KEY (part_id, chunk_id)
            )
        """)
        cur.execute("CREATE INDEX idx_pc_chunk ON parts_chunks(chunk_id)")
        cur.execute("CREATE INDEX idx_pc_part ON parts_chunks(part_id)")

    # Fetch all parts
    parts = cur.execute("SELECT * FROM parts WHERE is_fastener = 0").fetchall()
    print(f"Parts (non-fastener): {len(parts)}")

    total_links = 0
    name_matches = 0
    system_matches = 0

    for part in parts:
        part_id = part["id"]
        name_zh = part["part_name_zh"] or ""
        name_en = part["part_name_en"] or ""
        name_ru = part["part_name_ru"] or ""
        system_en = part["system_en"] or ""

        matched_chunks = set()

        # 1. FTS5 name match (search part name in chunks)
        for name in [name_en, name_ru]:
            if not name or len(name) < 4:
                continue
            # Clean name for FTS5
            words = name.replace("/", " ").replace("-", " ").split()
            words = [w for w in words if len(w) >= 3 and w.lower() not in {
                "the", "and", "for", "with", "system", "assembly", "assy",
                "left", "right", "upper", "lower", "front", "rear",
                "в", "для", "или", "сборе", "левый", "правый",
            }]
            if not words:
                continue

            # Search with OR between words
            fts_query = " OR ".join(f'"{w}"' for w in words[:3])
            try:
                hits = cur.execute("""
                    SELECT c.id FROM chunks_fts fts
                    JOIN chunks c ON c.rowid = fts.rowid
                    WHERE chunks_fts MATCH ?
                    AND (c.is_current IS NULL OR c.is_current = 1)
                    LIMIT 5
                """, (fts_query,)).fetchall()
                for h in hits:
                    if h[0] not in matched_chunks:
                        matched_chunks.add(h[0])
                        if not dry_run:
                            cur.execute(
                                "INSERT OR IGNORE INTO parts_chunks VALUES (?, ?, ?, ?)",
                                (part_id, h[0], "name_match", 0.5),
                            )
                        name_matches += 1
            except Exception:
                pass

        # 2. System/layer match — find chunks in same system
        layer = SYSTEM_TO_LAYER.get(system_en)
        if layer and len(matched_chunks) < 3:
            system_hits = cur.execute("""
                SELECT id FROM chunks
                WHERE layer = ?
                AND (is_current IS NULL OR is_current = 1)
                AND id NOT IN (SELECT chunk_id FROM chunk_quality WHERE quality_tier <= 1)
                ORDER BY (has_procedures + has_warnings) DESC
                LIMIT 3
            """, (layer,)).fetchall()
            for h in system_hits:
                if h[0] not in matched_chunks:
                    matched_chunks.add(h[0])
                    if not dry_run:
                        cur.execute(
                            "INSERT OR IGNORE INTO parts_chunks VALUES (?, ?, ?, ?)",
                            (part_id, h[0], "system_match", 0.3),
                        )
                    system_matches += 1

        total_links += len(matched_chunks)

    if not dry_run:
        conn.commit()

    # Stats
    unique_parts = cur.execute(
        "SELECT COUNT(DISTINCT part_id) FROM parts_chunks"
    ).fetchone()[0] if not dry_run else "N/A"
    unique_chunks = cur.execute(
        "SELECT COUNT(DISTINCT chunk_id) FROM parts_chunks"
    ).fetchone()[0] if not dry_run else "N/A"

    print(f"\n=== Summary ===")
    print(f"  Total links: {total_links}")
    print(f"  Name matches: {name_matches}")
    print(f"  System matches: {system_matches}")
    print(f"  Parts with links: {unique_parts}")
    print(f"  Unique chunks linked: {unique_chunks}")

    if dry_run:
        print("\n(Dry run — no changes made)")

    conn.close()
    print("\nDone!")


if __name__ == "__main__":
    main()
