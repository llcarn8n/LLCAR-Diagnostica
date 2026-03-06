"""
Phase 3: Merge fragmented mineru chunks into larger coherent articles.
Targets only mineru_l7_zh_owners (3913 chunks, avg 223 chars) and
mineru_l9_zh_owners (1401 chunks, avg 171 chars).

Algorithm: Title-chain aggregation
1. Group by (source, title)
2. Order by rowid within each group
3. Concatenate until MAX_MERGED_SIZE
4. Absorb header-only chunks (<80 chars)
5. Create new merged chunks with lineage tracking

Usage:
    python scripts/merge_fragments.py [--dry-run] [--db PATH]

Designed to run on workstation with GPU for subsequent ColBERT re-encoding.
"""

import sqlite3
import hashlib
import json
import re
import sys
import os
import unicodedata

# Config
MAX_MERGED_SIZE = 2500  # hard max chars per merged chunk
TARGET_SIZE = 1800      # start new chunk after this
MIN_USEFUL_SIZE = 80    # chunks smaller than this get absorbed
MERGE_SOURCES = [
    "mineru_l7_zh_owners",
    "mineru_l9_zh_owners",
]

# Generic titles that span entire manual — DON'T merge these
# (they contain unrelated topics from different sections)
SKIP_GENERIC_TITLES = {
    "提示", "警告", "注意", "www. carobook.com", "用户手册",
    "用车场景", "设置", "提示信息",
}

DB_PATH = os.environ.get(
    "KB_DB_PATH",
    os.path.join(os.path.dirname(__file__), "..", "knowledge-base", "kb.db"),
)


def normalize_title(title):
    """Normalize title for grouping."""
    if not title:
        return ""
    t = unicodedata.normalize("NFKC", title)
    t = t.strip().lower()
    # Remove trailing page numbers
    t = re.sub(r"\s*\.{2,}\s*\d+\s*$", "", t)
    return t


def make_chunk_id(brand, model, lang, content):
    """Generate a deterministic chunk ID from content hash."""
    h = hashlib.sha256(content.encode("utf-8")).hexdigest()[:8]
    return f"{brand}_{model}_{lang}_{h}"


def main():
    dry_run = "--dry-run" in sys.argv
    db_path = os.path.abspath(DB_PATH)
    print(f"DB: {db_path}")
    if dry_run:
        print("=== DRY RUN ===\n")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Create merge map table
    if not dry_run:
        cur.execute("DROP TABLE IF EXISTS chunk_merge_map")
        cur.execute("""
            CREATE TABLE chunk_merge_map (
                original_chunk_id TEXT NOT NULL,
                merged_chunk_id TEXT NOT NULL,
                merge_batch TEXT NOT NULL,
                PRIMARY KEY (original_chunk_id)
            )
        """)

    merge_batch = "merge_" + hashlib.md5(str(os.getpid()).encode()).hexdigest()[:8]

    total_original = 0
    total_merged = 0
    total_absorbed = 0
    all_merged_chunks = []
    all_merge_maps = []
    all_translations = []  # (merged_id, lang, title, content)
    all_glossary = []      # (merged_id, glossary_id)

    for source in MERGE_SOURCES:
        print(f"\n=== Processing: {source} ===")

        # Fetch all chunks for this source, ordered by rowid
        chunks = cur.execute("""
            SELECT id, title, content, brand, model, source_language, layer,
                   content_type, has_procedures, has_warnings, page_start,
                   rowid as rw
            FROM chunks
            WHERE source = ? AND (is_current IS NULL OR is_current = 1)
            ORDER BY rowid
        """, (source,)).fetchall()

        print(f"  Found {len(chunks)} chunks")
        total_original += len(chunks)

        # Group by normalized title
        groups = {}
        for chunk in chunks:
            key = normalize_title(chunk["title"])
            if key not in groups:
                groups[key] = []
            groups[key].append(chunk)

        print(f"  {len(groups)} unique title groups")

        # Process each group
        skipped_generic = 0
        for title_key, group_chunks in groups.items():
            # Skip generic titles that span entire manual
            raw_title = group_chunks[0]["title"] or ""
            if raw_title.strip() in SKIP_GENERIC_TITLES:
                skipped_generic += len(group_chunks)
                continue

            # Skip single-chunk groups (no merge benefit)
            if len(group_chunks) < 2:
                continue

            # Sort by rowid (should already be, but be safe)
            group_chunks.sort(key=lambda c: c["rw"])

            # Greedy merge
            buffer_chunks = []
            buffer_content = ""

            def finalize_buffer():
                nonlocal total_merged
                if not buffer_chunks:
                    return
                if len(buffer_content.strip()) < 10:
                    return

                first = buffer_chunks[0]
                # Merged chunk metadata: inherit from first, union flags
                brand = first["brand"] or "li_auto"
                model_name = first["model"] or "l7"
                lang = first["source_language"] or "zh"
                layer = first["layer"] or "body"
                has_proc = any(c["has_procedures"] for c in buffer_chunks)
                has_warn = any(c["has_warnings"] for c in buffer_chunks)
                merged_title = first["title"] or ""

                merged_id = make_chunk_id(brand, model_name, lang, buffer_content)
                original_ids = [c["id"] for c in buffer_chunks]

                all_merged_chunks.append({
                    "id": merged_id,
                    "brand": brand,
                    "model": model_name,
                    "source": source + "_merged",
                    "source_language": lang,
                    "layer": layer,
                    "content_type": first["content_type"],
                    "title": merged_title,
                    "content": buffer_content.strip(),
                    "page_start": first["page_start"],
                    "has_procedures": 1 if has_proc else 0,
                    "has_warnings": 1 if has_warn else 0,
                    "merged_from": json.dumps(original_ids),
                })

                for oid in original_ids:
                    all_merge_maps.append((oid, merged_id, merge_batch))

                # Collect translations from original chunks
                for lang_code in ("ru", "en", "es", "ar", "zh"):
                    trans_parts = []
                    for oc in buffer_chunks:
                        t = cur.execute(
                            "SELECT title, content FROM chunk_content WHERE chunk_id=? AND lang=?",
                            (oc["id"], lang_code),
                        ).fetchone()
                        if t and t[1]:
                            trans_parts.append(t[1])
                    if trans_parts:
                        merged_trans = "\n\n".join(trans_parts)
                        # Use first chunk's translated title
                        first_trans = cur.execute(
                            "SELECT title FROM chunk_content WHERE chunk_id=? AND lang=?",
                            (buffer_chunks[0]["id"], lang_code),
                        ).fetchone()
                        trans_title = first_trans[0] if first_trans else merged_title
                        all_translations.append((merged_id, lang_code, trans_title, merged_trans))

                # Collect glossary links (deduplicated)
                seen_gl = set()
                for oc in buffer_chunks:
                    for gl in cur.execute(
                        "SELECT glossary_id FROM chunk_glossary WHERE chunk_id=?",
                        (oc["id"],),
                    ).fetchall():
                        if gl[0] not in seen_gl:
                            seen_gl.add(gl[0])
                            all_glossary.append((merged_id, gl[0]))

                total_merged += 1

            for chunk in group_chunks:
                content = chunk["content"] or ""

                # Absorb tiny headers into buffer
                if len(content) < MIN_USEFUL_SIZE:
                    total_absorbed += 1
                    if buffer_content:
                        buffer_content += "\n\n" + content
                        buffer_chunks.append(chunk)
                    else:
                        buffer_content = content
                        buffer_chunks.append(chunk)
                    continue

                # Check if adding this chunk exceeds max
                if buffer_content and len(buffer_content) + len(content) + 2 > MAX_MERGED_SIZE:
                    finalize_buffer()
                    buffer_chunks = []
                    buffer_content = ""

                # Check if buffer already reached target
                if buffer_content and len(buffer_content) >= TARGET_SIZE:
                    finalize_buffer()
                    buffer_chunks = []
                    buffer_content = ""

                # Add to buffer
                if buffer_content:
                    buffer_content += "\n\n" + content
                else:
                    buffer_content = content
                buffer_chunks.append(chunk)

            # Finalize remaining buffer
            finalize_buffer()

        print(f"  Skipped (generic titles): {skipped_generic}")

    # Summary
    print(f"\n=== Merge Summary ===")
    print(f"  Original chunks: {total_original}")
    print(f"  Merged chunks: {total_merged}")
    print(f"  Absorbed headers: {total_absorbed}")
    print(f"  Reduction: {total_original} -> {total_merged} ({(1 - total_merged/total_original)*100:.1f}%)")

    # Size distribution of merged chunks
    sizes = [len(mc["content"]) for mc in all_merged_chunks]
    if sizes:
        avg_size = sum(sizes) / len(sizes)
        print(f"  Avg merged size: {avg_size:.0f} chars")
        print(f"  Min: {min(sizes)}, Max: {max(sizes)}")
        print(f"  Translations to create: {len(all_translations)}")
        print(f"  Glossary links to create: {len(all_glossary)}")

    if dry_run:
        print("\n(Dry run — no changes made)")
        conn.close()
        return

    # Write to DB
    print("\nWriting to DB...")

    # Insert merged chunks
    for mc in all_merged_chunks:
        content_hash = hashlib.sha256(mc["content"].encode("utf-8")).hexdigest()
        cur.execute("""
            INSERT OR REPLACE INTO chunks
            (id, brand, model, source, source_language, layer, content_type,
             title, content, page_start, has_procedures, has_warnings,
             merged_from, content_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            mc["id"], mc["brand"], mc["model"], mc["source"],
            mc["source_language"], mc["layer"], mc["content_type"],
            mc["title"], mc["content"], mc["page_start"],
            mc["has_procedures"], mc["has_warnings"], mc["merged_from"],
            content_hash,
        ))

    # Insert merge map
    cur.executemany(
        "INSERT INTO chunk_merge_map VALUES (?, ?, ?)",
        all_merge_maps,
    )

    # Insert translations
    for mid, lang, title, content in all_translations:
        cur.execute("""
            INSERT OR REPLACE INTO chunk_content (chunk_id, lang, title, content)
            VALUES (?, ?, ?, ?)
        """, (mid, lang, title, content))

    # Insert glossary links
    cur.executemany(
        "INSERT OR IGNORE INTO chunk_glossary (chunk_id, glossary_id) VALUES (?, ?)",
        all_glossary,
    )

    # Soft-delete originals
    original_ids = [m[0] for m in all_merge_maps]
    for oid in original_ids:
        cur.execute("UPDATE chunks SET is_current = 0 WHERE id = ?", (oid,))

    conn.commit()
    print(f"  Inserted {len(all_merged_chunks)} merged chunks")
    print(f"  Soft-deleted {len(original_ids)} originals (is_current=0)")
    print(f"  Created {len(all_translations)} translations")
    print(f"  Created {len(all_glossary)} glossary links")

    # Verify
    active = cur.execute("SELECT COUNT(*) FROM chunks WHERE is_current IS NULL OR is_current = 1").fetchone()[0]
    print(f"\n  Active chunks now: {active}")

    conn.close()
    print("\nDone! Next step: run ColBERT re-encoding for merged chunks.")


if __name__ == "__main__":
    main()
