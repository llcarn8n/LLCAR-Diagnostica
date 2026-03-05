#!/usr/bin/env python3
"""
Build a lightweight knowledge-base index for the Diagnostica app.
Reads manual-sections JSON files and the glossary, creates a searchable
index with section metadata + tag links to glossary_ids.

Output: examples/diagnostica/data/knowledge-base/kb-index.json
"""

import json
import re
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KB_DIR = os.path.join(BASE, 'knowledge-base')
GLOSSARY_PATH = os.path.join(BASE, 'architecture', 'i18n-glossary-data.json')
LAYERS_PATH = os.path.join(BASE, 'architecture', 'layer-definitions.json')
OUTPUT = os.path.join(BASE, '..', 'examples', 'diagnostica', 'data', 'knowledge-base', 'kb-index.json')

# Category keywords for classifying sections into automotive categories
CATEGORY_KEYWORDS = {
    'engine': [
        'двигатель', 'мотор', 'топлив', 'бензин', 'дизель', 'впуск', 'выхлоп',
        'глушитель', 'турбо', 'масл', 'зажиган', 'свеч', 'engine', 'fuel',
        'exhaust', 'intake', 'oil', 'ignition', 'turbo', 'генератор', 'усилитель',
        'range extender', 'увеличитель хода'
    ],
    'drivetrain': [
        'трансмисс', 'привод', 'подвеск', 'амортизатор', 'пружин', 'рычаг',
        'колес', 'шин', 'transmission', 'suspension', 'wheel', 'tire', 'differential',
        'дифференциал', 'карданн', 'ШРУС', 'ступиц', 'рессор'
    ],
    'ev': [
        'аккумулятор', 'батаре', 'зарядк', 'зарядн', 'электрич', 'инвертор',
        'battery', 'charging', 'electric', 'ev', 'DC-DC', '12В', '12V', 'проводк',
        'предохранитель', 'реле', 'ЭБУ', 'ECU', 'BMS', 'высоковольтн'
    ],
    'brakes': [
        'тормоз', 'руле', 'ABS', 'ESC', 'ESP', 'brake', 'steering',
        'суппорт', 'колодк', 'рулевой', 'электроусилитель'
    ],
    'sensors': [
        'камер', 'радар', 'лидар', 'lidar', 'датчик', 'ADAS', 'sensor',
        'подушк', 'airbag', 'ремень безопасн', 'seatbelt', 'ультразвук',
        'парков', 'помощ', 'предупрежден', 'распознаван'
    ],
    'hvac': [
        'кондиционер', 'климат', 'отоплен', 'вентиляц', 'печк', 'HVAC',
        'тепловой насос', 'хладагент', 'фильтр салон', 'охлажден',
        'обогрев', 'температур'
    ],
    'interior': [
        'сиден', 'двер', 'багажник', 'зеркал', 'панел', 'приборн', 'экран',
        'мультимедиа', 'seat', 'door', 'trunk', 'mirror', 'dashboard', 'infotainment',
        'рул', 'педал', 'окн', 'стекл', 'освещ', 'свет', 'подсветк', 'замок',
        'ключ', 'карточк', 'интерьер', 'обивк', 'ковр'
    ],
    'body': [
        'кузов', 'бампер', 'крыл', 'крыш', 'стойк', 'капот', 'лобов',
        'body', 'bumper', 'fender', 'roof', 'pillar', 'hood', 'windshield',
        'стеклоочистител', 'дворник', 'фар', 'фонар', 'наружн'
    ]
}

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def classify_section(title, content_preview):
    """Classify a section into a layer category based on keywords."""
    text = (title + ' ' + content_preview).lower()
    scores = {}
    for layer, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw.lower() in text)
        if score > 0:
            scores[layer] = score
    if not scores:
        return 'general'
    return max(scores, key=scores.get)


def find_glossary_matches(title, content_preview, glossary_components):
    """Find glossary_ids whose names appear in the section text."""
    text = (title + ' ' + content_preview).lower()
    matches = []
    for gid, names in glossary_components.items():
        for lang_code in ['ru', 'en', 'zh']:
            name = names.get(lang_code, '')
            if name and len(name) >= 3 and name.lower() in text:
                matches.append(gid)
                break
    return matches[:10]  # limit to 10 most relevant


def process_manual(manual_path, vehicle, glossary_components):
    """Process a manual-sections JSON into index entries."""
    data = load_json(manual_path)
    sections = data.get('sections', [])
    entries = []

    for sec in sections:
        sid = sec.get('sectionId', '')
        title = sec.get('title', '').strip()
        content = sec.get('content', '')
        page_start = sec.get('pageStart', 0)
        page_end = sec.get('pageEnd', 0)
        level = sec.get('level', 1)

        if not title or not content:
            continue

        # Content preview (first 300 chars for search and classification)
        preview = content[:300].replace('\n', ' ').strip()
        # Clean up OCR artifacts
        preview = re.sub(r'\s+', ' ', preview)

        # Classify into layer
        layer = classify_section(title, content[:500])

        # Find glossary matches
        tags = find_glossary_matches(title, content[:1000], glossary_components)

        # Detect if section has procedures/steps
        has_procedures = bool(sec.get('procedures'))
        has_warnings = bool(sec.get('warnings'))
        has_tables = bool(sec.get('tables'))

        # Content type
        content_type = 'manual'

        entry = {
            'id': f'{vehicle}_{sid}',
            'sectionId': sid,
            'vehicle': vehicle,
            'title': title,
            'preview': preview[:200],
            'pageStart': page_start,
            'pageEnd': page_end,
            'layer': layer,
            'tags': tags,
            'contentLength': len(content),
            'contentType': content_type,
            'hasProcedures': has_procedures,
            'hasWarnings': has_warnings,
            'hasTables': has_tables,
        }
        entries.append(entry)

    return entries


def main():
    print('Loading glossary...')
    glossary = load_json(GLOSSARY_PATH)
    glossary_components = glossary.get('components', {})
    print(f'  {len(glossary_components)} component translations')

    print('Loading layer definitions...')
    layers = load_json(LAYERS_PATH)

    all_entries = []

    # Process L9 manual (Russian)
    l9_ru_path = os.path.join(KB_DIR, 'manual-sections-l9-ru.json')
    if os.path.exists(l9_ru_path):
        print('Processing L9 Russian manual...')
        entries = process_manual(l9_ru_path, 'l9', glossary_components)
        all_entries.extend(entries)
        print(f'  {len(entries)} sections indexed')

    # Process L7 manual (Russian)
    l7_ru_path = os.path.join(KB_DIR, 'manual-sections-l7-ru.json')
    if os.path.exists(l7_ru_path):
        print('Processing L7 Russian manual...')
        entries = process_manual(l7_ru_path, 'l7', glossary_components)
        all_entries.extend(entries)
        print(f'  {len(entries)} sections indexed')

    # Layer stats
    layer_counts = {}
    for e in all_entries:
        layer_counts[e['layer']] = layer_counts.get(e['layer'], 0) + 1

    # Build output
    index = {
        'meta': {
            'version': '1.0',
            'generated': '2026-02-27',
            'totalEntries': len(all_entries),
            'vehicles': ['l7', 'l9'],
            'layerCounts': layer_counts
        },
        'entries': all_entries
    }

    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    print(f'\nOutput: {OUTPUT}')
    print(f'Total entries: {len(all_entries)}')
    print(f'Layer distribution: {json.dumps(layer_counts, indent=2)}')
    print('Done!')


if __name__ == '__main__':
    main()
