#!/usr/bin/env python3
"""
LLCAR Diagnostica — Конвертер MinerU → KB секции.

Читает _content_list.json из MinerU-вывода, собирает секции по заголовкам,
классифицирует по layer, извлекает DTC коды, маппит glossary_ids.

Вход:  mineru-output/*/auto/*_content_list.json
Выход: knowledge-base/sections-{vehicle}-{lang}.json
"""

import json
import os
import re
import sys
import glob
from difflib import SequenceMatcher

# Базовая директория (Diagnostica/)
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, 'api'))
from config import KB_DIR, ARCHITECTURE_DIR, MINERU_OUTPUT_DIR

# ═══════════════════════════════════════════════════════════
# Ключевые слова для классификации по слоям
# ═══════════════════════════════════════════════════════════

LAYER_KEYWORDS = {
    'engine': [
        'двигатель', 'мотор', 'топлив', 'бензин', 'дизель', 'впуск', 'выхлоп',
        'глушитель', 'турбо', 'масл', 'зажиган', 'свеч', 'engine', 'fuel',
        'exhaust', 'intake', 'oil', 'ignition', 'turbo', 'генератор',
        'range extender', 'увеличитель хода', '发动机', '燃油', '排气',
        '进气', '机油', '涡轮', '点火',
    ],
    'drivetrain': [
        'трансмисс', 'привод', 'подвеск', 'амортизатор', 'пружин', 'рычаг',
        'колес', 'шин', 'transmission', 'suspension', 'wheel', 'tire',
        'differential', 'дифференциал', 'карданн', 'ШРУС', 'ступиц', 'рессор',
        '变速', '悬架', '减震', '轮胎', '车轮', '传动',
    ],
    'ev': [
        'аккумулятор', 'батаре', 'зарядк', 'зарядн', 'электрич', 'инвертор',
        'battery', 'charging', 'electric', 'DC-DC', '12В', '12V', 'BMS',
        'высоковольтн', '电池', '充电', '电动', '逆变', '高压',
    ],
    'brakes': [
        'тормоз', 'ABS', 'ESC', 'ESP', 'brake', 'суппорт', 'колодк',
        'рулев', 'электроусилитель', 'steering', '制动', '刹车', '转向',
        'iBooster', 'EPB',
    ],
    'sensors': [
        'камер', 'радар', 'лидар', 'lidar', 'датчик', 'ADAS', 'sensor',
        'подушк', 'airbag', 'ремень безопасн', 'ультразвук', 'парков',
        '摄像头', '雷达', '传感器', '安全气囊', '超声波',
    ],
    'hvac': [
        'кондиционер', 'климат', 'отоплен', 'вентиляц', 'печк', 'HVAC',
        'тепловой насос', 'хладагент', 'охлажден', 'обогрев', 'температур',
        '空调', '暖风', '制冷', '加热', '热泵',
    ],
    'interior': [
        'сиден', 'двер', 'багажник', 'зеркал', 'панел', 'приборн', 'экран',
        'мультимедиа', 'seat', 'door', 'trunk', 'mirror', 'dashboard',
        'рул', 'педал', 'окн', 'стекл', 'освещ', 'свет', 'подсветк',
        'замок', 'ключ', '座椅', '门', '后备箱', '方向盘', '仪表',
    ],
    'body': [
        'кузов', 'бампер', 'крыл', 'крыш', 'стойк', 'капот', 'лобов',
        'body', 'bumper', 'fender', 'roof', 'hood', 'windshield',
        'стеклоочистител', 'дворник', 'фар', 'фонар',
        '车身', '保险杠', '车顶', '引擎盖', '挡风玻璃',
    ],
}

# Regex для DTC кодов
DTC_PATTERN = re.compile(r'\b([PCBU]\d{4})\b')

# Regex для процедурных шагов
PROCEDURE_PATTERN = re.compile(r'(?:^|\n)\s*\d+[\.\)]\s', re.MULTILINE)

# Слова-маркеры предупреждений
WARNING_MARKERS = [
    'внимание', 'warning', 'caution', 'danger', 'опасно', 'осторожно',
    '注意', '警告', '危险', 'предупреждение',
]


def load_json(path):
    """Загрузка JSON файла."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(data, path):
    """Сохранение JSON файла."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  Сохранено: {path} ({os.path.getsize(path) / 1024:.1f} КБ)")


def classify_layer(text):
    """Определить layer по ключевым словам."""
    text_lower = text.lower()
    scores = {}
    for layer, keywords in LAYER_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw.lower() in text_lower)
        if score > 0:
            scores[layer] = score
    if not scores:
        return 'general'
    return max(scores, key=scores.get)


def extract_dtc_codes(text):
    """Извлечь DTC коды из текста."""
    return list(set(DTC_PATTERN.findall(text)))


def has_procedures(text):
    """Проверить наличие пошаговых инструкций."""
    matches = PROCEDURE_PATTERN.findall(text)
    return len(matches) >= 2


def has_warnings(text):
    """Проверить наличие предупреждений."""
    text_lower = text.lower()
    return any(marker in text_lower for marker in WARNING_MARKERS)


def load_glossary():
    """Загрузить i18n глоссарий для маппинга glossary_ids."""
    path = os.path.join(ARCHITECTURE_DIR, 'i18n-glossary-data.json')
    if not os.path.exists(path):
        print(f"  [!] Глоссарий не найден: {path}")
        return {}
    data = load_json(path)
    components = data.get('components', {})
    # Строим обратный индекс: term_lower → glossary_id
    index = {}
    for gid, translations in components.items():
        for lang in ['en', 'ru', 'zh']:
            term = translations.get(lang, '')
            if term and len(term) >= 3:
                index[term.lower()] = gid
    print(f"  Глоссарий: {len(components)} компонентов, {len(index)} терминов в индексе")
    return index


def match_glossary_ids(text, glossary_index, max_matches=10):
    """Найти glossary_ids по содержимому текста."""
    text_lower = text.lower()
    matches = []
    for term, gid in glossary_index.items():
        if term in text_lower and gid not in matches:
            matches.append(gid)
            if len(matches) >= max_matches:
                break
    return matches


def detect_language(filename):
    """Определить язык по имени файла."""
    fn_lower = filename.lower()
    if 'руководство' in fn_lower or any(c in fn_lower for c in 'абвгдежзиклмноп'):
        return 'ru'
    if '手册' in fn_lower or '理想' in fn_lower or '零件' in fn_lower:
        return 'zh'
    return 'en'


def detect_vehicle(filename):
    """Определить модель авто по имени файла."""
    fn_lower = filename.lower()
    if 'l7' in fn_lower:
        return 'l7'
    if 'l9' in fn_lower:
        return 'l9'
    return 'both'


def detect_content_type(filename):
    """Определить тип контента по имени файла."""
    fn_lower = filename.lower()
    if '零件' in fn_lower or 'parts' in fn_lower:
        return 'parts'
    if 'configuration' in fn_lower or 'config' in fn_lower or '配置' in fn_lower:
        return 'config'
    return 'manual'


def parse_content_list(content_list_path, glossary_index):
    """
    Распарсить _content_list.json из MinerU в секции.

    MinerU формат: массив объектов с type, text, text_level, page_idx.
    Заголовки: text_level == 1.
    """
    data = load_json(content_list_path)
    filename = os.path.basename(content_list_path).replace('_content_list.json', '')

    vehicle = detect_vehicle(filename)
    language = detect_language(filename)
    content_type = detect_content_type(filename)

    print(f"\n  Файл: {filename}")
    print(f"  Блоков: {len(data)}, Язык: {language}, Модель: {vehicle}, Тип: {content_type}")

    # Собираем секции по заголовкам
    sections = []
    current_title = None
    current_texts = []
    current_page_start = 0
    current_page_end = 0
    section_counter = 0

    for block in data:
        block_type = block.get('type', 'text')
        text = block.get('text', '').strip()
        text_level = block.get('text_level', 0)
        page_idx = block.get('page_idx', 0)

        if not text:
            continue

        # Новый заголовок — закрываем предыдущую секцию
        if text_level == 1 and len(text) > 2:
            if current_title and current_texts:
                section_counter += 1
                content = '\n'.join(current_texts)
                sections.append(_make_section(
                    section_id=f"{section_counter}",
                    title=current_title,
                    content=content,
                    page_start=current_page_start,
                    page_end=current_page_end,
                    vehicle=vehicle,
                    language=language,
                    content_type=content_type,
                    glossary_index=glossary_index,
                ))

            current_title = text.strip()
            # Убираем номер секции из заголовка (например "1-1. Карты в автомобиле")
            current_title = re.sub(r'^\d+[-\.]\d*[-\.]?\s*', '', current_title).strip()
            current_texts = []
            current_page_start = page_idx
            current_page_end = page_idx
        else:
            current_texts.append(text)
            current_page_end = max(current_page_end, page_idx)

    # Последняя секция
    if current_title and current_texts:
        section_counter += 1
        content = '\n'.join(current_texts)
        sections.append(_make_section(
            section_id=f"{section_counter}",
            title=current_title,
            content=content,
            page_start=current_page_start,
            page_end=current_page_end,
            vehicle=vehicle,
            language=language,
            content_type=content_type,
            glossary_index=glossary_index,
        ))

    print(f"  Секций: {section_counter}")
    return sections, vehicle, language, content_type


def _make_section(section_id, title, content, page_start, page_end,
                  vehicle, language, content_type, glossary_index):
    """Создать объект секции с метаданными."""
    full_text = title + ' ' + content
    dtc_codes = extract_dtc_codes(full_text)
    glossary_ids = match_glossary_ids(full_text, glossary_index)

    return {
        'sectionId': section_id,
        'title': title,
        'content': content,
        'pageStart': page_start + 1,  # MinerU: 0-indexed → 1-indexed
        'pageEnd': page_end + 1,
        'vehicle': vehicle,
        'language': language,
        'contentType': content_type,
        'layer': classify_layer(full_text),
        'dtcCodes': dtc_codes,
        'glossaryIds': glossary_ids,
        'hasProcedures': has_procedures(content),
        'hasWarnings': has_warnings(content),
        'contentLength': len(content),
    }


def find_content_lists():
    """Найти все _content_list.json в mineru-output."""
    pattern = os.path.join(MINERU_OUTPUT_DIR, '**', '*_content_list.json')
    files = glob.glob(pattern, recursive=True)
    return files


def convert_existing_sections():
    """
    Конвертировать уже существующие manual-sections-*.json в новый формат.
    Это для L9 RU мануала, который уже был извлечён через PyMuPDF.
    """
    existing = [
        ('manual-sections-l9-ru.json', 'l9', 'ru', 'manual', 'pdf_l9_ru'),
        ('manual-sections-l7-ru.json', 'l7', 'ru', 'manual', 'pdf_l7_ru'),
        ('manual-sections-l7-zh.json', 'l7', 'zh', 'manual', 'pdf_l7_zh'),
        ('manual-sections-l9-zh.json', 'l9', 'zh', 'manual', 'pdf_l9_zh'),
    ]

    glossary_index = load_glossary()
    results = []

    for filename, vehicle, lang, ctype, source in existing:
        path = os.path.join(KB_DIR, filename)
        if not os.path.exists(path):
            continue

        print(f"\n  Конвертация существующего: {filename}")
        data = load_json(path)

        # Формат: {sections: [...], documentId, title, ...}
        raw_sections = data.get('sections', [])
        if not raw_sections:
            print(f"    Нет секций, пропуск")
            continue

        sections = []
        for s in raw_sections:
            content = s.get('content', '')
            title = s.get('title', 'Без названия')
            full_text = title + ' ' + content
            sections.append({
                'sectionId': s.get('sectionId', ''),
                'title': title,
                'content': content,
                'pageStart': s.get('pageStart', 0),
                'pageEnd': s.get('pageEnd', 0),
                'vehicle': vehicle,
                'language': lang,
                'contentType': ctype,
                'layer': classify_layer(full_text),
                'dtcCodes': extract_dtc_codes(full_text),
                'glossaryIds': match_glossary_ids(full_text, glossary_index),
                'hasProcedures': has_procedures(content),
                'hasWarnings': has_warnings(content),
                'contentLength': len(content),
            })

        output_name = f"sections-{vehicle}-{lang}.json"
        output_path = os.path.join(KB_DIR, output_name)
        output_data = {
            'meta': {
                'vehicle': vehicle,
                'language': lang,
                'contentType': ctype,
                'source': source,
                'totalSections': len(sections),
                'sourceFile': filename,
            },
            'sections': sections,
        }
        save_json(output_data, output_path)
        results.append((output_name, len(sections)))

    return results


def convert_mineru_outputs():
    """Конвертировать все MinerU выводы в секции."""
    glossary_index = load_glossary()
    content_lists = find_content_lists()

    if not content_lists:
        print("  [!] MinerU выводы не найдены")
        return []

    print(f"  Найдено {len(content_lists)} content_list файлов")

    results = []
    for cl_path in content_lists:
        sections, vehicle, language, content_type = parse_content_list(cl_path, glossary_index)

        if not sections:
            print(f"    Нет секций, пропуск")
            continue

        # Определяем имя выходного файла
        suffix = 'parts' if content_type == 'parts' else language
        output_name = f"sections-{vehicle}-{suffix}.json"

        # Источник
        source_map = {
            ('l9', 'ru', 'manual'): 'pdf_l9_ru',
            ('l9', 'zh', 'manual'): 'pdf_l9_zh',
            ('l9', 'zh', 'parts'): 'parts_zh',
            ('l7', 'en', 'manual'): 'pdf_l7_en',
            ('l7', 'zh', 'manual'): 'pdf_l7_zh',
        }
        source = source_map.get((vehicle, language, content_type), f'pdf_{vehicle}_{language}')

        output_path = os.path.join(KB_DIR, output_name)
        output_data = {
            'meta': {
                'vehicle': vehicle,
                'language': language,
                'contentType': content_type,
                'source': source,
                'totalSections': len(sections),
                'sourceFile': os.path.basename(cl_path),
            },
            'sections': sections,
        }

        # Не перезаписываем файл от convert_existing_sections если он уже лучше
        if os.path.exists(output_path):
            existing = load_json(output_path)
            existing_count = existing.get('meta', {}).get('totalSections', 0)
            if existing_count > len(sections):
                print(f"    Пропуск {output_name}: существующий файл ({existing_count} секций) больше ({len(sections)})")
                continue

        save_json(output_data, output_path)
        results.append((output_name, len(sections)))

    return results


def main():
    print("=" * 60)
    print("LLCAR KB — Конвертация MinerU → секции")
    print("=" * 60)

    os.makedirs(KB_DIR, exist_ok=True)

    # Шаг 1: конвертация существующих manual-sections
    print("\n--- Конвертация существующих manual-sections ---")
    existing_results = convert_existing_sections()

    # Шаг 2: конвертация MinerU выводов
    print("\n--- Конвертация MinerU выводов ---")
    mineru_results = convert_mineru_outputs()

    # Итоги
    print("\n" + "=" * 60)
    print("Итоги:")
    all_results = existing_results + mineru_results
    total_sections = 0
    for name, count in all_results:
        print(f"  {name}: {count} секций")
        total_sections += count
    print(f"  ВСЕГО: {total_sections} секций")
    print("=" * 60)


if __name__ == '__main__':
    main()
