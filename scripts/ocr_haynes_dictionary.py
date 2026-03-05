"""
OCR Haynes Anglo-Russian Automotive Technical Dictionary
Processes scanned PDF pages using EasyOCR, extracts EN→RU term pairs,
and builds a structured glossary JSON.
"""

import sys
import io
import os
import json
import re
from pathlib import Path

# Fix Windows cp1251 encoding for easyocr progress bars
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import numpy as np
from PIL import Image
import easyocr

PAGES_DIR = Path(__file__).parent.parent / "haynes-ocr" / "pages"
OUTPUT_DIR = Path(__file__).parent.parent / "knowledge-base"


def is_cyrillic(text: str) -> bool:
    """Check if text contains mostly Cyrillic characters."""
    cyrillic = sum(1 for c in text if '\u0400' <= c <= '\u04FF')
    latin = sum(1 for c in text if 'A' <= c.upper() <= 'Z')
    return cyrillic > latin


def is_section_header(text: str) -> bool:
    """Check if text is a single letter section header (A, B, C...)."""
    return bool(re.match(r'^[A-Z]$', text.strip()))


def clean_text(text: str) -> str:
    """Clean OCR artifacts from text."""
    text = text.strip()
    # Fix common OCR errors
    text = text.replace('  ', ' ')
    text = re.sub(r'\s+', ' ', text)
    return text


def pair_entries(regions: list) -> list:
    """
    Pair English terms with Russian translations based on spatial layout.
    English terms are on the left (lower x), Russian on the right (higher x).
    They are matched by y-coordinate proximity.
    """
    entries = []

    # Separate into left (EN) and right (RU) columns based on x position
    # and whether text is Cyrillic
    en_items = []
    ru_items = []

    for bbox, text, conf in regions:
        text = clean_text(text)
        if not text or len(text) < 2:
            continue

        y_center = (bbox[0][1] + bbox[2][1]) / 2
        x_center = (bbox[0][0] + bbox[2][0]) / 2
        x_left = bbox[0][0]

        if is_section_header(text):
            continue

        if is_cyrillic(text):
            ru_items.append({'y': y_center, 'x': x_center, 'text': text, 'conf': conf})
        else:
            en_items.append({'y': y_center, 'x': x_center, 'x_left': x_left, 'text': text, 'conf': conf})

    # Match EN terms with RU translations by closest y-coordinate
    used_ru = set()
    for en in en_items:
        best_ru = None
        best_dist = float('inf')

        for j, ru in enumerate(ru_items):
            if j in used_ru:
                continue
            dist = abs(en['y'] - ru['y'])
            if dist < best_dist and dist < 30:  # Max 30px vertical distance
                best_dist = dist
                best_ru = (j, ru)

        if best_ru is not None:
            j, ru = best_ru
            used_ru.add(j)
            entries.append({
                'en': en['text'],
                'ru': ru['text'],
                'conf_en': round(en['conf'], 3),
                'conf_ru': round(ru['conf'], 3)
            })

    return entries


def process_all_pages():
    """Process all page images with EasyOCR and extract term pairs."""
    print("Initializing EasyOCR (CPU mode)...")
    reader = easyocr.Reader(['en', 'ru'], gpu=False, verbose=False)
    print("EasyOCR ready.\n")

    all_entries = []
    page_files = sorted(PAGES_DIR.glob("page_*.png"))
    total = len(page_files)

    for idx, page_file in enumerate(page_files):
        page_num = int(page_file.stem.split('_')[1])
        print(f"Processing page {page_num + 1}/{total} ({page_file.name})...", end=' ')

        # Read via PIL to avoid OpenCV Cyrillic path issues
        img = np.array(Image.open(page_file))
        result = reader.readtext(img)
        entries = pair_entries(result)
        all_entries.extend(entries)

        print(f"{len(entries)} pairs ({len(result)} regions)")

    return all_entries


def merge_with_existing(haynes_entries: list) -> dict:
    """
    Merge Haynes dictionary with existing glossaries to create
    a unified trilingual glossary (EN-RU-ZH).
    """
    # Load existing glossaries
    glossary_alignment_path = OUTPUT_DIR / "glossary-alignment.json"
    trilingual_path = OUTPUT_DIR / "automotive-glossary-trilingual.json"

    existing_en_ru = {}  # en_lower -> ru
    existing_en_zh = {}  # en_lower -> zh
    existing_ru_zh = {}  # ru_lower -> zh

    # automotive-glossary-trilingual.json: {categories: {cat: {terms: [{en,ru,zh}]}}}
    if trilingual_path.exists():
        with open(trilingual_path, 'r', encoding='utf-8') as f:
            trilingual = json.load(f)
        count = 0
        for cat_name, cat_data in trilingual.get('categories', {}).items():
            terms = cat_data.get('terms', []) if isinstance(cat_data, dict) else []
            for entry in terms:
                en = entry.get('en', '').lower()
                ru = entry.get('ru', '')
                zh = entry.get('zh', '')
                if en:
                    if ru:
                        existing_en_ru[en] = ru
                    if zh:
                        existing_en_zh[en] = zh
                    count += 1
                if ru and zh:
                    existing_ru_zh[ru.lower()] = zh
        print(f"Loaded {count} terms from trilingual glossary")

    # glossary-alignment.json: {terms: [{ru, zh, en, source, category}]}
    if glossary_alignment_path.exists():
        with open(glossary_alignment_path, 'r', encoding='utf-8') as f:
            alignment = json.load(f)
        for pair in alignment.get('terms', []):
            ru = pair.get('ru', '')
            zh = pair.get('zh', '')
            en = pair.get('en', '')
            if ru and zh:
                existing_ru_zh[ru.lower()] = zh
            if en:
                if ru:
                    existing_en_ru[en.lower()] = ru
                if zh:
                    existing_en_zh[en.lower()] = zh
        print(f"Loaded alignment data ({len(existing_ru_zh)} RU↔ZH pairs)")

    # Build unified glossary
    unified = {}

    # Add Haynes entries (EN→RU)
    for entry in haynes_entries:
        en_lower = entry['en'].lower()
        if en_lower not in unified:
            unified[en_lower] = {
                'en': entry['en'],
                'ru': entry['ru'],
                'zh': '',
                'source': 'haynes'
            }

    # Enrich with ZH from existing glossaries
    enriched = 0
    for en_lower, data in unified.items():
        if en_lower in existing_en_zh:
            data['zh'] = existing_en_zh[en_lower]
            enriched += 1
        elif data['ru'].lower() in existing_ru_zh:
            data['zh'] = existing_ru_zh[data['ru'].lower()]
            enriched += 1

    # Add terms from existing glossaries that aren't in Haynes
    for en_lower, ru in existing_en_ru.items():
        if en_lower not in unified:
            zh = existing_en_zh.get(en_lower, '')
            if not zh and ru.lower() in existing_ru_zh:
                zh = existing_ru_zh[ru.lower()]
            unified[en_lower] = {
                'en': en_lower,
                'ru': ru,
                'zh': zh,
                'source': 'alignment'
            }

    print(f"\nUnified glossary: {len(unified)} total terms")
    print(f"  From Haynes: {sum(1 for v in unified.values() if v['source'] == 'haynes')}")
    print(f"  From alignment: {sum(1 for v in unified.values() if v['source'] == 'alignment')}")
    print(f"  With ZH translation: {sum(1 for v in unified.values() if v['zh'])}")
    print(f"  Enriched with ZH: {enriched}")

    # Sort by English term
    sorted_terms = sorted(unified.values(), key=lambda x: x['en'].lower())

    return {
        'version': '1.0',
        'description': 'Unified trilingual automotive glossary (EN-RU-ZH)',
        'sources': [
            'Haynes Anglo-Russian Automotive Technical Dictionary',
            'L9 RU↔ZH glossary alignment',
            'Automotive glossary trilingual'
        ],
        'stats': {
            'total': len(sorted_terms),
            'with_en': sum(1 for t in sorted_terms if t['en']),
            'with_ru': sum(1 for t in sorted_terms if t['ru']),
            'with_zh': sum(1 for t in sorted_terms if t['zh']),
            'from_haynes': sum(1 for t in sorted_terms if t['source'] == 'haynes'),
            'from_alignment': sum(1 for t in sorted_terms if t['source'] == 'alignment')
        },
        'terms': sorted_terms
    }


def main():
    print("=" * 60)
    print("Haynes Anglo-Russian Automotive Dictionary OCR")
    print("=" * 60)
    print()

    # Step 1: OCR all pages
    haynes_entries = process_all_pages()
    print(f"\nTotal Haynes entries extracted: {len(haynes_entries)}")

    # Save raw Haynes data
    raw_output = OUTPUT_DIR / "haynes-dictionary-raw.json"
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(raw_output, 'w', encoding='utf-8') as f:
        json.dump({
            'source': 'Haynes Anglo-Russian Automotive Technical Dictionary',
            'total_pairs': len(haynes_entries),
            'entries': haynes_entries
        }, f, ensure_ascii=False, indent=2)
    print(f"Saved raw dictionary: {raw_output}")

    # Step 2: Merge with existing glossaries
    unified = merge_with_existing(haynes_entries)

    # Save unified trilingual glossary
    unified_output = OUTPUT_DIR / "glossary-unified-trilingual.json"
    with open(unified_output, 'w', encoding='utf-8') as f:
        json.dump(unified, f, ensure_ascii=False, indent=2)
    print(f"Saved unified glossary: {unified_output}")

    # Print sample
    print("\n" + "=" * 60)
    print("Sample entries:")
    print("=" * 60)
    for term in unified['terms'][:20]:
        zh_part = f" | ZH: {term['zh']}" if term['zh'] else ""
        print(f"  EN: {term['en']:30s} | RU: {term['ru']:35s}{zh_part}")


if __name__ == '__main__':
    main()
