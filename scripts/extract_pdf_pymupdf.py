#!/usr/bin/env python3
"""
LLCAR Diagnostica — Извлечение контента из PDF через PyMuPDF.

Альтернатива MinerU для случаев когда MinerU недоступен/падает.
Извлекает текст постранично, определяет заголовки по размеру шрифта,
собирает секции, классифицирует и сохраняет в формате sections-*.json.

Вход:  PDF файлы из Diagnostica/
Выход: knowledge-base/sections-{vehicle}-{lang}.json
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

# ═══════════════════════════════════════════════════════════
# Конфигурация — какие PDF обрабатывать
# ═══════════════════════════════════════════════════════════

PDF_SOURCES = [
    {
        # Несмотря на английское название, содержимое на КИТАЙСКОМ
        'filename': "Lixiang L7 Owner's Manual.pdf",
        'vehicle': 'l7',
        'language': 'zh',
        'content_type': 'manual',
        'source': 'pdf_l7_zh',
        'output': 'sections-l7-zh-full.json',
    },
    {
        # Несмотря на английское название, содержимое на КИТАЙСКОМ
        'filename': "Lixiang L9 Owner's Manual.pdf",
        'subdir': 'Руководства пользователя Li Auto',
        'vehicle': 'l9',
        'language': 'zh',
        'content_type': 'manual',
        'source': 'pdf_l9_zh',
        'output': 'sections-l9-zh-full.json',
    },
    {
        # Этот файл реально на английском (конфигурация)
        'filename': "Li L9英文版.pdf",
        'subdir': 'Руководства пользователя Li Auto',
        'vehicle': 'l9',
        'language': 'en',
        'content_type': 'config',
        'source': 'pdf_l9_en',
        'output': 'sections-l9-en.json',
    },
]

# ═══════════════════════════════════════════════════════════
# Ключевые слова для классификации
# ═══════════════════════════════════════════════════════════

LAYER_KEYWORDS = {
    'engine': [
        'engine', 'fuel', 'exhaust', 'intake', 'oil', 'ignition', 'turbo',
        'range extender', 'generator', 'gasoline', 'coolant',
        '发动机', '燃油', '排气', '进气', '机油', '涡轮', '点火', '增程器',
        '加注燃油', '冷却液',
    ],
    'drivetrain': [
        'transmission', 'suspension', 'wheel', 'tire', 'differential',
        'axle', 'spring', 'shock', 'strut', 'alignment',
        '变速', '悬架', '减震', '轮胎', '车轮', '传动', '差速', '底盘',
        '胎压', '四轮',
    ],
    'ev': [
        'battery', 'charging', 'electric', 'DC-DC', '12V', 'BMS',
        'high voltage', 'inverter', 'motor', 'regenerat',
        '电池', '充电', '电动', '逆变', '高压', '动力电池', '能量回收',
        '纯电', '混合',
    ],
    'brakes': [
        'brake', 'ABS', 'ESC', 'ESP', 'caliper', 'pad', 'rotor',
        'steering', 'power steering', 'iBooster', 'EPB',
        '制动', '刹车', '转向', '助力转向', '驻车',
    ],
    'sensors': [
        'camera', 'radar', 'lidar', 'sensor', 'ADAS', 'airbag',
        'seatbelt', 'ultrasonic', 'parking', 'collision',
        '摄像头', '雷达', '传感器', '安全气囊', '超声波', '泊车',
        '辅助驾驶', '自动紧急', '碰撞',
    ],
    'hvac': [
        'air conditioning', 'climate', 'heating', 'ventilat', 'HVAC',
        'heat pump', 'refrigerant', 'defrost', 'temperature',
        '空调', '暖风', '制冷', '加热', '热泵', '出风口', '温度', '除霜',
    ],
    'interior': [
        'seat', 'door', 'trunk', 'mirror', 'dashboard', 'display',
        'multimedia', 'steering wheel', 'pedal', 'window', 'light',
        'lock', 'key', 'glove box', 'console', 'sunroof',
        '座椅', '门', '后备箱', '方向盘', '仪表', '屏幕', '钥匙', '照明',
        '多媒体', '导航', '音响', '天窗', '遮阳', '储物', '杯架', '车窗',
        '中控', '解锁',
    ],
    'body': [
        'body', 'bumper', 'fender', 'roof', 'hood', 'windshield',
        'wiper', 'headlight', 'taillight', 'antenna', 'paint',
        '车身', '保险杠', '车顶', '引擎盖', '挡风玻璃', '雨刷', '大灯',
        '尾灯', '车漆', '天线',
    ],
}

DTC_PATTERN = re.compile(r'\b([PCBU]\d{4})\b')
PROCEDURE_PATTERN = re.compile(r'(?:^|\n)\s*\d+[\.\)]\s', re.MULTILINE)
WARNING_MARKERS = ['warning', 'caution', 'danger', 'notice', 'attention']


def classify_layer(text):
    """Определить layer по ключевым словам."""
    text_lower = text.lower()
    scores = {}
    for layer, keywords in LAYER_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw.lower() in text_lower)
        if score > 0:
            scores[layer] = score
    return max(scores, key=scores.get) if scores else 'general'


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
        for lang in ['en', 'ru', 'zh']:
            term = translations.get(lang, '')
            if term and len(term) >= 3:
                index[term.lower()] = gid
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


def extract_sections_from_pdf(pdf_path, vehicle, language, content_type):
    """
    Извлечь секции из PDF используя PyMuPDF.

    Стратегия:
    1. Извлекаем текст по блокам (spans) с информацией о шрифте
    2. Определяем заголовки по размеру шрифта (>= медианный * 1.3)
    3. Группируем текст по заголовкам в секции
    """
    doc = fitz.open(pdf_path)
    print(f"  Страниц: {doc.page_count}")

    # Фаза 1: Собираем все текстовые блоки с размерами шрифтов
    all_blocks = []
    font_sizes = []

    for page_num in range(doc.page_count):
        page = doc[page_num]
        blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)["blocks"]

        for block in blocks:
            if block.get("type") != 0:  # Только текстовые блоки
                continue
            for line in block.get("lines", []):
                line_text = ""
                max_font_size = 0
                is_bold = False

                for span in line.get("spans", []):
                    text = span.get("text", "").strip()
                    if text:
                        line_text += text + " "
                        size = span.get("size", 10)
                        font_sizes.append(size)
                        max_font_size = max(max_font_size, size)
                        if "bold" in span.get("font", "").lower():
                            is_bold = True

                line_text = line_text.strip()
                if line_text and len(line_text) > 1:
                    all_blocks.append({
                        'text': line_text,
                        'font_size': max_font_size,
                        'is_bold': is_bold,
                        'page': page_num,
                    })

    doc.close()

    if not all_blocks:
        print(f"  [!] Текст не извлечён")
        return []

    # Фаза 2: Определяем порог для заголовков
    font_sizes.sort()
    if not font_sizes:
        return []

    # Медианный размер — это body text
    median_size = font_sizes[len(font_sizes) // 2]
    # Заголовки: >= медианный * 1.4 (строже — меньше ложных заголовков)
    # bold подзаголовки: >= медианный * 1.15
    heading_threshold = median_size * 1.4
    subheading_threshold = median_size * 1.15

    print(f"  Медианный шрифт: {median_size:.1f}, порог заголовка: {heading_threshold:.1f}")
    print(f"  Всего строк: {len(all_blocks)}")

    # Фаза 3: Сборка секций
    sections = []
    current_title = None
    current_texts = []
    current_page_start = 0
    current_page_end = 0
    section_counter = 0

    for block in all_blocks:
        text = block['text']
        size = block['font_size']
        is_bold = block['is_bold']
        page = block['page']

        # Определяем, является ли строка заголовком
        is_heading = (
            (size >= heading_threshold) or
            (is_bold and size >= subheading_threshold)
        )

        # Заголовок не должен быть слишком длинным
        if is_heading and len(text) > 200:
            is_heading = False

        # Заголовок не должен быть слишком коротким (один символ)
        if is_heading and len(text) < 3:
            is_heading = False

        if is_heading:
            # Закрываем предыдущую секцию
            if current_title and current_texts:
                section_counter += 1
                content = '\n'.join(current_texts)
                if len(content.strip()) >= 30:
                    sections.append(_make_section(
                        section_counter, current_title, content,
                        current_page_start, current_page_end,
                        vehicle, language, content_type,
                    ))

            current_title = text.strip()
            # Убираем номер секции
            current_title = re.sub(r'^\d+[-\.]\d*[-\.]?\s*', '', current_title).strip()
            current_texts = []
            current_page_start = page
            current_page_end = page
        else:
            current_texts.append(text)
            current_page_end = max(current_page_end, page)

    # Последняя секция
    if current_title and current_texts:
        section_counter += 1
        content = '\n'.join(current_texts)
        if len(content.strip()) >= 30:
            sections.append(_make_section(
                section_counter, current_title, content,
                current_page_start, current_page_end,
                vehicle, language, content_type,
            ))

    # Фаза 4: Объединение мелких секций (< 100 символов) с предыдущей
    merged = []
    for section in sections:
        if (merged and
                len(section['content']) < 100 and
                merged[-1]['language'] == section['language']):
            # Объединяем с предыдущей секцией
            merged[-1]['content'] += f"\n\n{section['title']}\n{section['content']}"
            merged[-1]['pageEnd'] = section['pageEnd']
        else:
            merged.append(section)

    # Пересчитываем layer для объединённых секций
    for section in merged:
        full_text = section['title'] + ' ' + section['content']
        section['layer'] = classify_layer(full_text)
        section['contentLength'] = len(section['content'])

    print(f"  Секций после объединения мелких: {len(merged)} (было {len(sections)})")
    return merged


def _make_section(section_id, title, content, page_start, page_end,
                  vehicle, language, content_type):
    """Создать объект секции с метаданными."""
    full_text = title + ' ' + content
    return {
        'sectionId': str(section_id),
        'title': title,
        'content': content,
        'pageStart': page_start + 1,
        'pageEnd': page_end + 1,
        'vehicle': vehicle,
        'language': language,
        'contentType': content_type,
        'layer': classify_layer(full_text),
        'dtcCodes': list(set(DTC_PATTERN.findall(full_text))),
        'glossaryIds': [],  # Заполнится позже
        'hasProcedures': len(PROCEDURE_PATTERN.findall(content)) >= 2,
        'hasWarnings': any(m in full_text.lower() for m in WARNING_MARKERS),
        'contentLength': len(content),
    }


def save_json(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    size_kb = os.path.getsize(path) / 1024
    print(f"  Сохранено: {path} ({size_kb:.1f} КБ)")


def main():
    print("=" * 60)
    print("LLCAR KB — Извлечение PDF через PyMuPDF")
    print("=" * 60)

    glossary_index = load_glossary()
    print(f"  Глоссарий: {len(glossary_index)} терминов")

    total_sections = 0

    for src in PDF_SOURCES:
        subdir = src.get('subdir', '')
        if subdir:
            pdf_path = os.path.join(BASE, subdir, src['filename'])
        else:
            pdf_path = os.path.join(BASE, src['filename'])

        if not os.path.exists(pdf_path):
            print(f"\n  [!] Файл не найден: {pdf_path}")
            continue

        print(f"\n{'─' * 60}")
        print(f"  PDF: {src['filename']}")
        print(f"  Модель: {src['vehicle']}, Язык: {src['language']}")

        sections = extract_sections_from_pdf(
            pdf_path, src['vehicle'], src['language'], src['content_type']
        )

        if not sections:
            continue

        # Заполняем glossary_ids
        for section in sections:
            full_text = section['title'] + ' ' + section['content']
            section['glossaryIds'] = match_glossary_ids(full_text, glossary_index)

        # Проверяем что не перезапишем лучший файл
        output_path = os.path.join(KB_DIR, src['output'])
        if os.path.exists(output_path):
            with open(output_path, 'r', encoding='utf-8') as f:
                existing = json.load(f)
            existing_count = existing.get('meta', {}).get('totalSections', 0)
            if existing_count >= len(sections):
                print(f"  Пропуск: существующий файл ({existing_count} секций) >= новый ({len(sections)})")
                continue

        output_data = {
            'meta': {
                'vehicle': src['vehicle'],
                'language': src['language'],
                'contentType': src['content_type'],
                'source': src['source'],
                'totalSections': len(sections),
                'sourceFile': src['filename'],
                'extractor': 'PyMuPDF',
            },
            'sections': sections,
        }
        save_json(output_data, output_path)
        total_sections += len(sections)

    print(f"\n{'=' * 60}")
    print(f"Итого извлечено: {total_sections} секций")
    print("=" * 60)


if __name__ == '__main__':
    main()
