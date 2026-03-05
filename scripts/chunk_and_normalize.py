#!/usr/bin/env python3
"""
LLCAR Diagnostica — Чанкинг, нормализация и дедупликация.

Объединяет ВСЕ секции из конвертеров и скраперов в единый файл чанков.
Разбивает длинные секции на чанки ~500 токенов с overlap.
Дедупликация web vs PDF по fuzzy title match.

Вход:  knowledge-base/sections-*.json, web-sections-*.json, dtc-database.json
Выход: knowledge-base/chunks-unified.json
"""

import json
import os
import re
import sys
import glob
from difflib import SequenceMatcher

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, 'api'))
from config import KB_DIR, CHUNK_SIZE_CHARS, CHUNK_OVERLAP_CHARS

# Допустимые значения
VALID_VEHICLES = {'l7', 'l9', 'both'}
VALID_LAYERS = {'engine', 'drivetrain', 'ev', 'brakes', 'sensors', 'hvac', 'interior', 'body', 'general'}
VALID_CONTENT_TYPES = {'manual', 'parts', 'dtc', 'procedure', 'config'}
VALID_LANGUAGES = {'ru', 'en', 'zh'}


def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    size_mb = os.path.getsize(path) / (1024 * 1024)
    print(f"  Сохранено: {path} ({size_mb:.2f} МБ)")


def chunk_text(text, chunk_size=CHUNK_SIZE_CHARS, overlap=CHUNK_OVERLAP_CHARS):
    """
    Разбить текст на чанки с overlap.
    Пытается разбить по абзацам/предложениям для сохранения контекста.
    """
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        if end >= len(text):
            chunks.append(text[start:])
            break

        # Ищем хорошую точку разрыва (конец абзаца или предложения)
        best_break = end
        # Абзац
        newline_pos = text.rfind('\n\n', start + chunk_size // 2, end + 200)
        if newline_pos != -1:
            best_break = newline_pos + 2
        else:
            # Конец предложения
            sentence_end = -1
            for sep in ['. ', '。', '! ', '？', '? ', '.\n']:
                pos = text.rfind(sep, start + chunk_size // 2, end + 100)
                if pos > sentence_end:
                    sentence_end = pos + len(sep)
            if sentence_end > start + chunk_size // 2:
                best_break = sentence_end

        chunks.append(text[start:best_break])
        start = best_break - overlap

    return chunks


def normalize_section(section, source_file):
    """Нормализовать метаданные секции."""
    vehicle = section.get('vehicle', 'both')
    if vehicle not in VALID_VEHICLES:
        vehicle = 'both'

    layer = section.get('layer', 'general')
    if layer not in VALID_LAYERS:
        layer = 'general'

    content_type = section.get('contentType', 'manual')
    if content_type not in VALID_CONTENT_TYPES:
        content_type = 'manual'

    language = section.get('language', 'ru')
    if language not in VALID_LANGUAGES:
        language = 'ru'

    # Определяем source
    source = section.get('source', '')
    if not source:
        if 'web-sections' in source_file:
            source = 'web'
        elif 'parts' in source_file:
            source = f'parts_{language}'
        else:
            source = f'pdf_{vehicle}_{language}'

    return {
        'vehicle': vehicle,
        'layer': layer,
        'contentType': content_type,
        'language': language,
        'source': source,
        'title': section.get('title', 'Без названия'),
        'content': section.get('content', ''),
        'pageStart': section.get('pageStart', 0),
        'pageEnd': section.get('pageEnd', 0),
        'sourceUrl': section.get('sourceUrl', ''),
        'glossaryIds': section.get('glossaryIds', []),
        'dtcCodes': section.get('dtcCodes', []),
        'hasProcedures': section.get('hasProcedures', False),
        'hasWarnings': section.get('hasWarnings', False),
        'sectionId': section.get('sectionId', ''),
    }


def load_all_sections():
    """Загрузить все секции из всех файлов."""
    patterns = [
        os.path.join(KB_DIR, 'sections-*.json'),
        os.path.join(KB_DIR, 'web-sections-*.json'),
    ]

    all_sections = []
    for pattern in patterns:
        for filepath in sorted(glob.glob(pattern)):
            filename = os.path.basename(filepath)
            data = load_json(filepath)

            meta = data.get('meta', {})
            source = meta.get('source', '')
            sections = data.get('sections', [])

            for section in sections:
                if not source:
                    section['source'] = source
                normalized = normalize_section(section, filename)
                normalized['_sourceFile'] = filename
                all_sections.append(normalized)

            print(f"  {filename}: {len(sections)} секций")

    return all_sections


def load_dtc_as_sections():
    """Загрузить DTC базу как секции для индексации."""
    dtc_path = os.path.join(KB_DIR, 'dtc-database.json')
    if not os.path.exists(dtc_path):
        print(f"  [!] dtc-database.json не найден")
        return []

    data = load_json(dtc_path)
    codes = data.get('codes', {})
    sections = []

    for code, info in codes.items():
        title_parts = [f"DTC {code}"]
        if info.get('title_en'):
            title_parts.append(info['title_en'])
        if info.get('title_ru'):
            title_parts.append(info['title_ru'])
        title = ' — '.join(title_parts[:2])

        content_parts = []
        if info.get('title_ru'):
            content_parts.append(f"Описание: {info['title_ru']}")
        if info.get('title_en'):
            content_parts.append(f"Description: {info['title_en']}")
        if info.get('title_zh'):
            content_parts.append(f"描述: {info['title_zh']}")
        if info.get('severity'):
            sev_labels = {1: 'Информация', 2: 'Низкая', 3: 'Средняя', 4: 'Высокая', 5: 'Критическая'}
            content_parts.append(f"Критичность: {sev_labels.get(info['severity'], info['severity'])}")
        if info.get('can_drive'):
            drive_labels = {'yes': 'Можно ехать', 'yes_limited': 'Можно с ограничениями', 'no': 'Нельзя ехать'}
            content_parts.append(f"Можно ехать: {drive_labels.get(info['can_drive'], info['can_drive'])}")
        if info.get('probable_causes'):
            content_parts.append(f"Вероятные причины: {', '.join(info['probable_causes'])}")

        content = '\n'.join(content_parts)

        sections.append({
            'vehicle': 'both',
            'layer': info.get('system', 'general'),
            'contentType': 'dtc',
            'language': 'ru',  # мультиязычный
            'source': 'dtc_db',
            'title': title,
            'content': content,
            'pageStart': 0,
            'pageEnd': 0,
            'sourceUrl': '',
            'glossaryIds': info.get('related_components', []),
            'dtcCodes': [code],
            'hasProcedures': False,
            'hasWarnings': info.get('severity', 0) >= 4,
            'sectionId': code,
            '_sourceFile': 'dtc-database.json',
        })

    print(f"  dtc-database.json: {len(sections)} DTC записей")
    return sections


def deduplicate(chunks, similarity_threshold=0.85):
    """
    Дедупликация чанков.
    Приоритет: web > pdf (web контент чище).
    Сравнение по fuzzy title match.
    """
    print(f"\n--- Дедупликация (порог: {similarity_threshold}) ---")
    print(f"  До дедупликации: {len(chunks)} чанков")

    # Группируем по vehicle+layer для сравнения только в рамках одной группы
    groups = {}
    for chunk in chunks:
        key = f"{chunk['vehicle']}_{chunk['layer']}"
        if key not in groups:
            groups[key] = []
        groups[key].append(chunk)

    kept = []
    duplicates = 0

    for key, group in groups.items():
        # Внутри группы сравниваем titles
        seen_titles = []
        for chunk in group:
            title = chunk['title']
            is_dup = False

            for existing_title, existing_chunk in seen_titles:
                ratio = SequenceMatcher(None, title.lower(), existing_title.lower()).ratio()
                if ratio >= similarity_threshold:
                    # Дубликат найден — оставляем web версию
                    if chunk['source'] == 'web' and existing_chunk['source'] != 'web':
                        # Заменяем PDF на web
                        idx = kept.index(existing_chunk)
                        kept[idx] = chunk
                        seen_titles = [(t, c) for t, c in seen_titles if c != existing_chunk]
                        seen_titles.append((title, chunk))
                    is_dup = True
                    duplicates += 1
                    break

            if not is_dup:
                seen_titles.append((title, chunk))
                kept.append(chunk)

    print(f"  Дубликатов найдено: {duplicates}")
    print(f"  После дедупликации: {len(kept)} чанков")
    return kept


def process_chunks(sections):
    """Разбить секции на чанки."""
    print(f"\n--- Чанкинг ({CHUNK_SIZE_CHARS} символов, overlap {CHUNK_OVERLAP_CHARS}) ---")

    chunks = []
    for section in sections:
        content = section['content']
        title = section['title']

        if not content or len(content.strip()) < 20:
            continue

        text_chunks = chunk_text(content)

        for i, chunk_text_part in enumerate(text_chunks):
            chunk_id = f"{section['source']}_{section['vehicle']}_{section['sectionId']}_c{i}"

            # Добавляем заголовок в начало каждого чанка для контекста
            if i > 0:
                chunk_content = f"[{title}]\n\n{chunk_text_part}"
            else:
                chunk_content = chunk_text_part

            chunks.append({
                'id': chunk_id,
                'title': title,
                'content': chunk_content,
                'vehicle': section['vehicle'],
                'layer': section['layer'],
                'contentType': section['contentType'],
                'language': section['language'],
                'source': section['source'],
                'pageStart': section['pageStart'],
                'pageEnd': section['pageEnd'],
                'sourceUrl': section.get('sourceUrl', ''),
                'glossaryIds': section.get('glossaryIds', []),
                'dtcCodes': section.get('dtcCodes', []),
                'hasProcedures': section.get('hasProcedures', False),
                'hasWarnings': section.get('hasWarnings', False),
            })

    print(f"  Чанков создано: {len(chunks)}")
    return chunks


def print_stats(chunks):
    """Вывести статистику по чанкам."""
    print(f"\n{'=' * 60}")
    print(f"СТАТИСТИКА")
    print(f"{'=' * 60}")
    print(f"  Всего чанков: {len(chunks)}")

    # По vehicle
    vehicles = {}
    for c in chunks:
        vehicles[c['vehicle']] = vehicles.get(c['vehicle'], 0) + 1
    print(f"\n  По модели:")
    for v, count in sorted(vehicles.items()):
        print(f"    {v}: {count}")

    # По language
    langs = {}
    for c in chunks:
        langs[c['language']] = langs.get(c['language'], 0) + 1
    print(f"\n  По языку:")
    for l, count in sorted(langs.items()):
        print(f"    {l}: {count}")

    # По layer
    layers = {}
    for c in chunks:
        layers[c['layer']] = layers.get(c['layer'], 0) + 1
    print(f"\n  По слою:")
    for l, count in sorted(layers.items(), key=lambda x: -x[1]):
        print(f"    {l}: {count}")

    # По source
    sources = {}
    for c in chunks:
        sources[c['source']] = sources.get(c['source'], 0) + 1
    print(f"\n  По источнику:")
    for s, count in sorted(sources.items(), key=lambda x: -x[1]):
        print(f"    {s}: {count}")

    # По contentType
    types = {}
    for c in chunks:
        types[c['contentType']] = types.get(c['contentType'], 0) + 1
    print(f"\n  По типу контента:")
    for t, count in sorted(types.items(), key=lambda x: -x[1]):
        print(f"    {t}: {count}")

    # Средний размер чанка
    avg_len = sum(len(c['content']) for c in chunks) / max(len(chunks), 1)
    print(f"\n  Средний размер чанка: {avg_len:.0f} символов")
    print(f"{'=' * 60}")


def main():
    print("=" * 60)
    print("LLCAR KB — Чанкинг и нормализация")
    print("=" * 60)

    # 1. Загружаем все секции
    print("\n--- Загрузка секций ---")
    sections = load_all_sections()

    # 2. Загружаем DTC как секции
    print("\n--- Загрузка DTC ---")
    dtc_sections = load_dtc_as_sections()
    sections.extend(dtc_sections)

    print(f"\n  ВСЕГО секций: {len(sections)}")

    if not sections:
        print("[!] Нет секций для обработки. Запустите convert_mineru_to_sections.py сначала.")
        sys.exit(1)

    # 3. Чанкинг
    chunks = process_chunks(sections)

    # 4. Дедупликация
    chunks = deduplicate(chunks)

    # 5. Сортировка по ID для стабильного порядка
    chunks.sort(key=lambda c: c['id'])

    # 6. Статистика
    print_stats(chunks)

    # 7. Сохранение
    output_path = os.path.join(KB_DIR, 'chunks-unified.json')
    output_data = {
        'meta': {
            'version': '1.0',
            'totalChunks': len(chunks),
            'chunkSize': CHUNK_SIZE_CHARS,
            'chunkOverlap': CHUNK_OVERLAP_CHARS,
        },
        'chunks': chunks,
    }
    save_json(output_data, output_path)


if __name__ == '__main__':
    main()
