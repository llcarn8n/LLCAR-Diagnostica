#!/usr/bin/env python3
"""
LLCAR Diagnostica — Извлечение каталога деталей L9.

Парсит 941362155-2022-2023款理想L9零件手册.pdf (415 стр.)
Формат: таблицы с колонками [序号, 热点ID, 零件号码, 零件名称]
Каждая страница — отдельная система/подсистема.

Выход: knowledge-base/sections-l9-parts-zh.json
"""

import json
import os
import re
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, 'api'))
from config import KB_DIR, ARCHITECTURE_DIR

try:
    import fitz  # PyMuPDF
except ImportError:
    print("Требуется: pip install PyMuPDF")
    sys.exit(1)

# Маппинг названий систем → layer
SYSTEM_LAYER_MAP = {
    '动力电池': 'ev',
    '电驱动': 'ev',
    '驱动轴': 'drivetrain',
    '驱动电机': 'ev',
    '充电': 'ev',
    '增程器': 'engine',
    '发动机': 'engine',
    '排气': 'engine',
    '进气': 'engine',
    '制动': 'brakes',
    '刹车': 'brakes',
    '转向': 'brakes',
    '悬架': 'drivetrain',
    '减震': 'drivetrain',
    '轮胎': 'drivetrain',
    '车轮': 'drivetrain',
    '空调': 'hvac',
    '暖风': 'hvac',
    '冷却': 'hvac',
    '加热': 'hvac',
    '座椅': 'interior',
    '门': 'interior',
    '后备': 'interior',
    '仪表': 'interior',
    '方向盘': 'interior',
    '屏幕': 'interior',
    '多媒体': 'interior',
    '车身': 'body',
    '保险杠': 'body',
    '车顶': 'body',
    '引擎盖': 'body',
    '大灯': 'body',
    '尾灯': 'body',
    '雨刷': 'body',
    '挡风': 'body',
    '摄像头': 'sensors',
    '雷达': 'sensors',
    '传感器': 'sensors',
    '安全气囊': 'sensors',
    '线束': 'sensors',
    '油箱': 'engine',
    '燃油': 'engine',
    '散热': 'hvac',
    '冷凝': 'hvac',
    '蒸发': 'hvac',
    '压缩机': 'hvac',
}


def classify_layer_parts(title):
    """Классифицировать систему по layer."""
    for keyword, layer in SYSTEM_LAYER_MAP.items():
        if keyword in title:
            return layer
    return 'general'


def load_glossary():
    """Загрузить i18n глоссарий."""
    path = os.path.join(ARCHITECTURE_DIR, 'i18n-glossary-data.json')
    if not os.path.exists(path):
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    components = data.get('components', {})
    index = {}
    for gid, translations in components.items():
        term = translations.get('zh', '')
        if term and len(term) >= 2:
            index[term] = gid
    return index


def match_glossary_ids(text, glossary_index, max_matches=10):
    """Найти glossary_ids по содержимому текста."""
    matches = []
    for term, gid in glossary_index.items():
        if term in text and gid not in matches:
            matches.append(gid)
            if len(matches) >= max_matches:
                break
    return matches


def save_json(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    size_kb = os.path.getsize(path) / 1024
    print(f"  Сохранено: {path} ({size_kb:.1f} КБ)")


def extract_parts_catalog(pdf_path, glossary_index):
    """
    Извлечь каталог деталей из PDF.

    Стратегия:
    - Каждая страница имеет заголовок системы (первая строка, крупный шрифт)
    - Далее таблица: [序号, 热点ID, 零件号码, 零件名称]
    - Группируем детали по системам
    """
    doc = fitz.open(pdf_path)
    print(f"  Страниц: {doc.page_count}")

    # Собираем все системы и их детали
    systems = {}  # title → list of parts
    current_system = None

    for page_num in range(doc.page_count):
        page = doc[page_num]
        text = page.get_text()

        if not text.strip():
            continue

        lines = [l.strip() for l in text.split('\n') if l.strip()]
        if not lines:
            continue

        # Первая строка страницы — обычно заголовок системы
        first_line = lines[0]

        # Определяем, является ли это заголовком системы
        # (содержит китайские символы и не является строкой заголовков таблицы / числом)
        if (re.search(r'[\u4e00-\u9fff]', first_line) and
                first_line not in ('序号', '热点ID', '零件号码', '零件名称') and
                not re.match(r'^\d+$', first_line)):
            # Убираем дату в скобках
            system_title = re.sub(r'[（(]\d{4}[-/]?\d{0,2}[-/]?\d{0,2}[）)]', '', first_line).strip()
            system_title = re.sub(r'[（(]\d{8}[）)]', '', system_title).strip()

            if system_title and len(system_title) >= 2:
                current_system = system_title
                if current_system not in systems:
                    systems[current_system] = {
                        'parts': [],
                        'page_start': page_num + 1,
                        'page_end': page_num + 1,
                    }

        if current_system:
            systems[current_system]['page_end'] = page_num + 1

        # Парсим строки таблицы
        # Формат: данные идут по отдельным строкам, каждая запись — 4 строки:
        # [序号], [热点ID], [零件号码], [零件名称]
        # Пропускаем заголовки таблицы
        skip_headers = {'序号', '热点ID', '零件号码', '零件名称'}
        data_lines = [l for l in lines if l not in skip_headers and l != first_line]

        i = 0
        while i < len(data_lines) - 3:
            # Ищем паттерн: число, число, код детали, название
            line1 = data_lines[i]
            line2 = data_lines[i + 1]
            line3 = data_lines[i + 2]
            line4 = data_lines[i + 3]

            # Строка 1: порядковый номер (только цифры)
            # Строка 2: hotspot ID (только цифры)
            # Строка 3: код детали (буквы, цифры, дефисы)
            # Строка 4: название (китайские символы)
            if (re.match(r'^\d+$', line1) and
                    re.match(r'^\d+$', line2) and
                    re.match(r'^[A-Za-z0-9]', line3) and
                    re.search(r'[\u4e00-\u9fff]', line4)):
                if current_system:
                    # Название может продолжаться на следующей строке
                    part_name = line4
                    # Проверяем не является ли следующая строка продолжением названия
                    if (i + 4 < len(data_lines) and
                            re.search(r'[\u4e00-\u9fff]', data_lines[i + 4]) and
                            not re.match(r'^\d+$', data_lines[i + 4])):
                        # Следующая строка — продолжение, только если после неё идёт число
                        if (i + 5 < len(data_lines) and re.match(r'^\d+$', data_lines[i + 5])):
                            part_name += data_lines[i + 4]
                            i += 1

                    systems[current_system]['parts'].append({
                        'idx': int(line1),
                        'hotspot_id': line2,
                        'part_number': line3.strip(),
                        'part_name': part_name.strip(),
                    })
                i += 4
            else:
                i += 1

    doc.close()

    print(f"  Систем найдено: {len(systems)}")

    # Формируем секции
    sections = []
    section_counter = 0

    for system_title, system_data in systems.items():
        parts = system_data['parts']
        if not parts:
            continue

        section_counter += 1

        # Формируем контент: список деталей
        content_parts = [f"Система: {system_title}\n"]
        content_parts.append(f"Деталей: {len(parts)}\n")

        # Уникальные номера деталей
        unique_parts = {}
        for p in parts:
            key = p['part_number']
            if key not in unique_parts:
                unique_parts[key] = p['part_name']

        content_parts.append("\n零件清单 (Parts List):\n")
        for pn, name in unique_parts.items():
            content_parts.append(f"  {pn} — {name}")

        content = '\n'.join(content_parts)
        full_text = system_title + ' ' + content

        sections.append({
            'sectionId': str(section_counter),
            'title': system_title,
            'content': content,
            'pageStart': system_data['page_start'],
            'pageEnd': system_data['page_end'],
            'vehicle': 'l9',
            'language': 'zh',
            'contentType': 'parts',
            'layer': classify_layer_parts(system_title),
            'source': 'parts_zh',
            'dtcCodes': [],
            'glossaryIds': match_glossary_ids(full_text, glossary_index),
            'hasProcedures': False,
            'hasWarnings': False,
            'partsCount': len(unique_parts),
            'contentLength': len(content),
        })

    print(f"  Секций создано: {len(sections)}")
    total_parts = sum(s.get('partsCount', 0) for s in sections)
    print(f"  Уникальных деталей: {total_parts}")

    # Статистика по слоям
    layers = {}
    for s in sections:
        layers[s['layer']] = layers.get(s['layer'], 0) + 1
    print(f"  По слоям:")
    for layer, count in sorted(layers.items(), key=lambda x: -x[1]):
        print(f"    {layer}: {count}")

    return sections


def main():
    print("=" * 60)
    print("LLCAR KB — Извлечение каталога деталей L9")
    print("=" * 60)

    pdf_path = os.path.join(BASE, '941362155-2022-2023款理想L9零件手册.pdf')
    if not os.path.exists(pdf_path):
        print(f"  [!] Файл не найден: {pdf_path}")
        sys.exit(1)

    glossary_index = load_glossary()
    print(f"  Глоссарий: {len(glossary_index)} терминов (ZH)")

    sections = extract_parts_catalog(pdf_path, glossary_index)

    if not sections:
        print("  [!] Секции не извлечены")
        sys.exit(1)

    output_path = os.path.join(KB_DIR, 'sections-l9-parts-zh.json')
    output_data = {
        'meta': {
            'vehicle': 'l9',
            'language': 'zh',
            'contentType': 'parts',
            'source': 'parts_zh',
            'totalSections': len(sections),
            'sourceFile': '941362155-2022-2023款理想L9零件手册.pdf',
            'extractor': 'PyMuPDF',
        },
        'sections': sections,
    }
    save_json(output_data, output_path)

    print(f"\n{'=' * 60}")
    print(f"Итого: {len(sections)} секций каталога деталей")
    print("=" * 60)


if __name__ == '__main__':
    main()
