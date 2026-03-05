#!/usr/bin/env python3
"""
LLCAR Diagnostica — Phase 2: Glossary Alignment Builder.

Compares parallel L9 RU↔ZH manual sections to extract aligned term pairs.
Merges with existing automotive-glossary-trilingual.json.

Output: glossary-alignment.json

Usage:
    python build_glossary.py
"""

import sys
import io
import json
import re
from pathlib import Path
from datetime import date
from collections import defaultdict

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ============================================================
# Paths
# ============================================================
BASE_DIR = Path(__file__).resolve().parent.parent
KB_DIR = BASE_DIR / "knowledge-base"

L9_RU = KB_DIR / "manual-sections-l9-ru.json"
L9_ZH = KB_DIR / "manual-sections-l9-zh.json"
GLOSSARY = KB_DIR / "automotive-glossary-trilingual.json"
OUTPUT = KB_DIR / "glossary-alignment.json"


# ============================================================
# Title alignment
# ============================================================
def align_section_titles(ru_sections, zh_sections):
    """Align section titles by sectionId to create RU↔ZH title pairs."""
    ru_map = {s["sectionId"]: s for s in ru_sections}
    zh_map = {s["sectionId"]: s for s in zh_sections}

    pairs = []
    for sid in sorted(ru_map.keys(), key=lambda x: (int(x.split("-")[0]), int(x.split("-")[1]))):
        if sid not in zh_map:
            continue
        ru_title = ru_map[sid]["title"].strip()
        zh_title = zh_map[sid]["title"].strip()
        if ru_title and zh_title and ru_title != zh_title:
            pairs.append({
                "sectionId": sid,
                "ru": ru_title,
                "zh": zh_title,
                "source": "section_title",
            })

    return pairs


# ============================================================
# Table header alignment
# ============================================================
def align_table_headers(ru_sections, zh_sections):
    """Align table headers from parallel sections."""
    ru_map = {s["sectionId"]: s for s in ru_sections}
    zh_map = {s["sectionId"]: s for s in zh_sections}

    pairs = []
    for sid, ru_sec in ru_map.items():
        zh_sec = zh_map.get(sid)
        if not zh_sec:
            continue

        ru_tables = ru_sec.get("tables", [])
        zh_tables = zh_sec.get("tables", [])

        # Align tables by position (same index = same table)
        for i in range(min(len(ru_tables), len(zh_tables))):
            ru_headers = ru_tables[i].get("headers", [])
            zh_headers = zh_tables[i].get("headers", [])

            for j in range(min(len(ru_headers), len(zh_headers))):
                ru_h = ru_headers[j].strip()
                zh_h = zh_headers[j].strip()
                if ru_h and zh_h and ru_h != zh_h and len(ru_h) > 1 and len(zh_h) > 1:
                    pairs.append({
                        "ru": ru_h,
                        "zh": zh_h,
                        "source": "table_header",
                        "sectionId": sid,
                    })

    return pairs


# ============================================================
# Content term extraction
# ============================================================
def extract_key_terms_from_content(ru_sections, zh_sections):
    """Extract potential term pairs from parallel content using patterns."""
    ru_map = {s["sectionId"]: s for s in ru_sections}
    zh_map = {s["sectionId"]: s for s in zh_sections}

    pairs = []

    # Pattern: look for warning/note headers
    warning_terms = {
        "ВНИМАНИЕ": "警告",
        "ОСТОРОЖНО": "注意",
        "ОПАСНОСТЬ": "危险",
        "ПРИМЕЧАНИЕ": "说明",
    }

    for ru_term, zh_term in warning_terms.items():
        pairs.append({
            "ru": ru_term,
            "zh": zh_term,
            "source": "warning_pattern",
        })

    # Pattern: extract bold/emphasized terms (lines that are short and capitalized)
    for sid, ru_sec in ru_map.items():
        zh_sec = zh_map.get(sid)
        if not zh_sec:
            continue

        ru_content = ru_sec.get("content", "")
        zh_content = zh_sec.get("content", "")

        # Extract short lines (likely subsection headers) from both
        ru_headers = extract_short_headers(ru_content, "ru")
        zh_headers = extract_short_headers(zh_content, "zh")

        # If similar count, try positional alignment
        if ru_headers and zh_headers and 0.5 < len(ru_headers) / max(len(zh_headers), 1) < 2:
            for i in range(min(len(ru_headers), len(zh_headers))):
                if ru_headers[i] != zh_headers[i]:
                    pairs.append({
                        "ru": ru_headers[i],
                        "zh": zh_headers[i],
                        "source": "content_header",
                        "sectionId": sid,
                    })

    return pairs


def extract_short_headers(text, lang):
    """Extract short lines that look like subsection headers."""
    headers = []
    for line in text.split("\n"):
        line = line.strip()
        if not line or len(line) < 2:
            continue

        # Skip numbered steps
        if re.match(r"^\d+[\.\)]\s", line):
            continue
        # Skip very long lines (paragraphs)
        if len(line) > 60:
            continue

        # For Russian: lines that start with capital letter, short
        if lang == "ru" and re.match(r"^[А-ЯA-Z]", line) and len(line) < 50:
            headers.append(line)
        # For Chinese: short lines (likely headers)
        elif lang == "zh" and len(line) < 30 and not re.match(r"^[\d\s●•\-]", line):
            headers.append(line)

    return headers[:50]  # Limit


# ============================================================
# Merge with existing glossary
# ============================================================
def merge_with_glossary(pairs, glossary_path):
    """Merge extracted pairs with existing trilingual glossary."""
    if not glossary_path.exists():
        return pairs, {}

    with open(glossary_path, "r", encoding="utf-8") as f:
        glossary = json.load(f)

    # Build lookup from existing glossary
    existing_ru = {}
    existing_zh = {}
    categories = glossary.get("categories", {})

    for cat_key, cat_data in categories.items():
        for term in cat_data.get("terms", []):
            ru = term.get("ru", "").lower()
            zh = term.get("zh", "")
            en = term.get("en", "")
            if ru:
                existing_ru[ru] = {"en": en, "zh": zh, "category": cat_key}
            if zh:
                existing_zh[zh] = {"en": en, "ru": term.get("ru", ""), "category": cat_key}

    # Enrich pairs with EN from glossary
    enriched = []
    new_terms = []

    for pair in pairs:
        ru_lower = pair["ru"].lower()
        zh = pair["zh"]

        en = ""
        category = "uncategorized"

        if ru_lower in existing_ru:
            en = existing_ru[ru_lower]["en"]
            category = existing_ru[ru_lower]["category"]
        elif zh in existing_zh:
            en = existing_zh[zh]["en"]
            category = existing_zh[zh]["category"]

        entry = {
            "ru": pair["ru"],
            "zh": zh,
            "en": en,
            "source": pair["source"],
            "category": category,
        }
        if "sectionId" in pair:
            entry["sectionId"] = pair["sectionId"]

        enriched.append(entry)

        if ru_lower not in existing_ru and zh not in existing_zh:
            new_terms.append(entry)

    return enriched, {
        "total_existing": sum(len(cat.get("terms", [])) for cat in categories.values()),
        "total_extracted": len(pairs),
        "enriched_with_en": sum(1 for e in enriched if e["en"]),
        "new_terms": len(new_terms),
    }


# ============================================================
# Deduplication
# ============================================================
def deduplicate_pairs(pairs):
    """Remove duplicate pairs, keeping first occurrence."""
    seen = set()
    unique = []
    for p in pairs:
        key = (p["ru"].lower(), p["zh"])
        if key not in seen:
            seen.add(key)
            unique.append(p)
    return unique


# ============================================================
# Main
# ============================================================
def main():
    print("=" * 60)
    print("LLCAR Diagnostica — Phase 2: Glossary Alignment")
    print("=" * 60)

    # Load parallel sections
    if not L9_RU.exists() or not L9_ZH.exists():
        print("ERROR: Need both manual-sections-l9-ru.json and manual-sections-l9-zh.json")
        return

    with open(L9_RU, "r", encoding="utf-8") as f:
        ru_data = json.load(f)
    with open(L9_ZH, "r", encoding="utf-8") as f:
        zh_data = json.load(f)

    ru_sections = ru_data["sections"]
    zh_sections = zh_data["sections"]
    print(f"  L9 RU: {len(ru_sections)} sections")
    print(f"  L9 ZH: {len(zh_sections)} sections")

    # Step 1: Title alignment
    print("\n--- Step 1: Section Title Alignment ---")
    title_pairs = align_section_titles(ru_sections, zh_sections)
    print(f"  Title pairs: {len(title_pairs)}")

    # Step 2: Table header alignment
    print("\n--- Step 2: Table Header Alignment ---")
    table_pairs = align_table_headers(ru_sections, zh_sections)
    print(f"  Table header pairs: {len(table_pairs)}")

    # Step 3: Content term extraction
    print("\n--- Step 3: Content Term Extraction ---")
    content_pairs = extract_key_terms_from_content(ru_sections, zh_sections)
    print(f"  Content pairs: {len(content_pairs)}")

    # Combine and deduplicate
    all_pairs = title_pairs + table_pairs + content_pairs
    all_pairs = deduplicate_pairs(all_pairs)
    print(f"\n  Combined unique pairs: {len(all_pairs)}")

    # Step 4: Merge with existing glossary
    print("\n--- Step 4: Merge with Trilingual Glossary ---")
    enriched, stats = merge_with_glossary(all_pairs, GLOSSARY)
    print(f"  Existing glossary terms: {stats.get('total_existing', 0)}")
    print(f"  Extracted pairs: {stats.get('total_extracted', 0)}")
    print(f"  Enriched with EN: {stats.get('enriched_with_en', 0)}")
    print(f"  New terms (not in glossary): {stats.get('new_terms', 0)}")

    # Group by source
    by_source = defaultdict(int)
    for e in enriched:
        by_source[e["source"]] += 1
    print(f"\n  By source: {dict(by_source)}")

    # Build output
    output = {
        "documentId": "glossary_alignment_l9_ru_zh",
        "title": "Li Auto L9 RU↔ZH Glossary Alignment",
        "extraction_date": str(date.today()),
        "stats": stats,
        "terms": enriched,
    }

    # Save
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n  Saved: {OUTPUT}")
    print(f"  Size: {OUTPUT.stat().st_size / 1024:.1f}KB")

    # Show sample terms
    print("\n--- Sample Aligned Terms ---")
    for term in enriched[:20]:
        en_str = f" | EN: {term['en']}" if term["en"] else ""
        print(f"  RU: {term['ru'][:30]:32s} ZH: {term['zh'][:20]:22s}{en_str}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
