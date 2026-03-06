"""
Phase 1.1: Build chunk_quality side table.
Scores every chunk with quality_tier 1-5 based on heuristics.

Usage: python scripts/build_chunk_quality.py
"""

import sqlite3
import re
import sys
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "knowledge-base", "kb.db")


def compute_tier(content, content_type, has_procedures, has_warnings):
    length = len(content) if content else 0

    # Base tier by length
    if length < 50:
        tier = 1
    elif length < 150:
        tier = 2
    elif length < 500:
        tier = 3
    elif length < 2000:
        tier = 4
    else:
        tier = 5

    # Boost for procedures
    if has_procedures and length > 200:
        tier = max(tier, 4)

    # Boost for warnings (safety-relevant)
    if has_warnings and length > 100:
        tier = max(tier, 3)

    # DTC entries are always relevant
    if content_type == "dtc":
        tier = max(tier, 3)

    # Web-scraped articles tend to be good
    if content_type == "owner_review":
        tier = max(tier, 3)

    return tier


def compute_flags(content):
    is_stub = 1 if len(content or "") < 100 else 0

    # Image-only: starts with markdown image, very short
    is_image_only = 0
    if content and re.match(r"^\s*#*\s*!\[", content) and len(content) < 200:
        is_image_only = 1

    # OCR noise: page numbers, TOC artifacts
    has_ocr_noise = 0
    if content:
        stripped = content.strip()
        # Pure page numbers
        if re.match(r"^\d{1,3}\s*$", stripped):
            has_ocr_noise = 1
        # TOC-style entries with ".." page references
        if ".." in content and len(content) < 200:
            toc_pattern = re.findall(r"\.\.\s*\d+", content)
            if len(toc_pattern) >= 2:
                has_ocr_noise = 1

    return is_stub, is_image_only, has_ocr_noise


def main():
    db_path = os.path.abspath(DB_PATH)
    print(f"DB: {db_path}")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Create table
    cur.execute("DROP TABLE IF EXISTS chunk_quality")
    cur.execute("""
        CREATE TABLE chunk_quality (
            chunk_id TEXT PRIMARY KEY,
            content_length INTEGER NOT NULL,
            quality_tier INTEGER NOT NULL,
            is_stub INTEGER DEFAULT 0,
            is_image_only INTEGER DEFAULT 0,
            has_ocr_noise INTEGER DEFAULT 0
        )
    """)
    cur.execute("CREATE INDEX idx_cq_tier ON chunk_quality(quality_tier)")

    # Fetch all chunks
    rows = cur.execute("""
        SELECT id, content, content_type, has_procedures, has_warnings
        FROM chunks
    """).fetchall()

    print(f"Processing {len(rows)} chunks...")

    batch = []
    tier_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

    for row in rows:
        content = row["content"] or ""
        tier = compute_tier(
            content,
            row["content_type"],
            row["has_procedures"],
            row["has_warnings"],
        )
        is_stub, is_image_only, has_ocr_noise = compute_flags(content)

        tier_counts[tier] += 1
        batch.append((
            row["id"],
            len(content),
            tier,
            is_stub,
            is_image_only,
            has_ocr_noise,
        ))

    cur.executemany(
        "INSERT INTO chunk_quality VALUES (?, ?, ?, ?, ?, ?)",
        batch,
    )
    conn.commit()

    # Stats
    print("\n=== Quality Tier Distribution ===")
    for t in range(1, 6):
        labels = {1: "garbage", 2: "low", 3: "medium", 4: "good", 5: "excellent"}
        pct = tier_counts[t] * 100 / len(rows)
        print(f"  Tier {t} ({labels[t]}): {tier_counts[t]} ({pct:.1f}%)")

    stubs = sum(1 for b in batch if b[3])
    img_only = sum(1 for b in batch if b[4])
    ocr_noise = sum(1 for b in batch if b[5])
    print(f"\n  Stubs (<100 chars): {stubs}")
    print(f"  Image-only: {img_only}")
    print(f"  OCR noise: {ocr_noise}")

    conn.close()
    print("\nDone! chunk_quality table populated.")


if __name__ == "__main__":
    main()
