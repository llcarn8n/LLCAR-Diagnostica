#!/usr/bin/env python3
"""
LLCAR Diagnostica — Скрапер manuals.lixiang.com.

Загружает структурированный контент с онлайн-мануалов Li Auto.
Сайт — SPA: навигация через data-content атрибуты, контент подгружается
из отдельных topic-*.html файлов.

Выход: knowledge-base/web-sections-{vehicle}-zh.json
"""

import json
import os
import re
import sys
import time
from urllib.parse import urljoin

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, 'api'))
from config import KB_DIR, ARCHITECTURE_DIR

try:
    import httpx
except ImportError:
    print("Требуется: pip install httpx")
    sys.exit(1)

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("Требуется: pip install beautifulsoup4")
    sys.exit(1)

# ═══════════════════════════════════════════════════════════
# Конфигурация
# ═══════════════════════════════════════════════════════════

MODELS = {
    'l7': {
        'base_url': 'https://manuals.lixiang.com/zh-cn/X032024MAX/20251031174920/',
        'name': 'Li L7',
    },
    # L9 URL пока не найден — сайт возвращает 404
}

# Задержка между запросами (секунды)
REQUEST_DELAY = 0.8

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}

# Ключевые слова для классификации по слоям (китайский)
LAYER_KEYWORDS_ZH = {
    'engine': ['发动机', '燃油', '排气', '进气', '机油', '涡轮', '点火', '增程器', '加注燃油'],
    'drivetrain': ['变速', '悬架', '减震', '轮胎', '车轮', '传动', '差速', '底盘'],
    'ev': ['电池', '充电', '电动', '逆变', '高压', '12V', 'BMS', 'DC-DC', '动力电池'],
    'brakes': ['制动', '刹车', '转向', 'ABS', 'ESC', 'ESP', 'iBooster', 'EPB'],
    'sensors': ['摄像头', '雷达', '传感器', '安全气囊', '超声波', 'ADAS', '激光', '泊车'],
    'hvac': ['空调', '暖风', '制冷', '加热', '热泵', '出风口', '温度', '除霜'],
    'interior': ['座椅', '门', '后备箱', '方向盘', '仪表', '屏幕', '钥匙', '照明',
                 '多媒体', '导航', '音响', '天窗', '遮阳', '储物', '杯架'],
    'body': ['车身', '保险杠', '车顶', '引擎盖', '挡风玻璃', '雨刷', '大灯', '尾灯',
             '车漆', '天线'],
}


def classify_layer_zh(text):
    """Классифицировать текст по слою (китайский)."""
    scores = {}
    for layer, keywords in LAYER_KEYWORDS_ZH.items():
        score = sum(1 for kw in keywords if kw in text)
        if score > 0:
            scores[layer] = score
    return max(scores, key=scores.get) if scores else 'general'


def load_glossary():
    """Загрузить i18n глоссарий для маппинга glossary_ids."""
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


def fetch_page(client, url, retries=2):
    """Загрузить страницу с задержкой и ретраями."""
    for attempt in range(retries + 1):
        time.sleep(REQUEST_DELAY)
        try:
            resp = client.get(url, follow_redirects=True, timeout=20)
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            if attempt < retries:
                time.sleep(2)
                continue
            print(f"  [!] Ошибка загрузки {url}: {e}")
            return None


def extract_nav_topics(soup):
    """
    Извлечь все темы из sidebar навигации.
    Каждая тема — это <a> с data-content="topic-*.html".
    Иерархия: level-1 → level-2 → level-3 (leaves).
    """
    topics = []

    # Собираем структуру: level-1 = главы, level-2 = разделы, level-3 = статьи
    current_chapter = ''
    current_section = ''

    for li in soup.select('.sidebar li.nav-item'):
        classes = li.get('class', [])
        a_tag = li.find('a', recursive=False)
        if not a_tag:
            continue

        text = a_tag.get_text(strip=True)
        data_content = a_tag.get('data-content', '')

        if 'level-1' in classes:
            current_chapter = text
            current_section = ''
        elif 'level-2' in classes:
            current_section = text
        elif 'level-3' in classes and data_content:
            topics.append({
                'chapter': current_chapter,
                'section': current_section,
                'title': text,
                'data_content': data_content,
            })

    return topics


def extract_topic_content(soup):
    """
    Извлечь текстовый контент из topic HTML.
    Возвращает чистый текст с сохранением структуры.
    """
    # Удаляем ненужное
    for tag in soup.select('script, style, nav, .sidebar, .menu'):
        tag.decompose()

    # Собираем контент по секциям
    parts = []

    # Заголовки и параграфы
    for el in soup.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'li', 'td', 'th', 'div']):
        text = el.get_text(strip=True)
        if not text or len(text) < 2:
            continue

        if el.name in ('h1', 'h2'):
            parts.append(f"\n## {text}\n")
        elif el.name in ('h3', 'h4'):
            parts.append(f"\n### {text}\n")
        elif el.name == 'li':
            parts.append(f"• {text}")
        elif el.name in ('td', 'th'):
            continue  # Обработаем таблицы отдельно
        elif el.name == 'p':
            parts.append(text)
        elif el.name == 'div' and not el.find(['p', 'h1', 'h2', 'h3', 'li']):
            # Только "листовые" div-ы с текстом
            if len(text) > 10:
                parts.append(text)

    # Таблицы
    for table in soup.find_all('table'):
        rows = []
        for tr in table.find_all('tr'):
            cells = [td.get_text(strip=True) for td in tr.find_all(['td', 'th'])]
            if cells and any(cells):
                rows.append(' | '.join(cells))
        if rows:
            parts.append('\n' + '\n'.join(rows) + '\n')

    content = '\n'.join(parts)
    # Убираем множественные пустые строки
    content = re.sub(r'\n{3,}', '\n\n', content)
    return content.strip()


def scrape_model(model_id, model_config, glossary_index):
    """Скрапить мануал для одной модели."""
    base_url = model_config['base_url']
    model_name = model_config['name']

    print(f"\n{'=' * 60}")
    print(f"Скрапинг: {model_name}")
    print(f"URL: {base_url}")
    print(f"{'=' * 60}")

    sections = []

    with httpx.Client(headers=HEADERS, verify=False) as client:
        # 1. Загружаем главную страницу — получаем навигацию
        print(f"  Загрузка навигации...")
        html = fetch_page(client, base_url)
        if not html:
            print(f"  [!] Не удалось загрузить главную страницу")
            return sections

        soup = BeautifulSoup(html, 'html.parser')

        # 2. Извлекаем все темы из sidebar
        topics = extract_nav_topics(soup)
        print(f"  Найдено тем: {len(topics)}")

        if not topics:
            print(f"  [!] Темы не найдены в навигации")
            return sections

        # Выводим структуру глав
        chapters = {}
        for t in topics:
            ch = t['chapter']
            if ch not in chapters:
                chapters[ch] = 0
            chapters[ch] += 1
        print(f"  Глав: {len(chapters)}")
        for ch, count in chapters.items():
            print(f"    {ch}: {count} тем")

        # 3. Загружаем каждую тему
        failed = 0
        empty = 0

        for i, topic in enumerate(topics, 1):
            topic_url = urljoin(base_url, topic['data_content'])
            title = topic['title']

            if i % 20 == 0 or i == 1:
                print(f"  [{i}/{len(topics)}] {title[:40]}...")

            html = fetch_page(client, topic_url)
            if not html:
                failed += 1
                continue

            topic_soup = BeautifulSoup(html, 'html.parser')
            content = extract_topic_content(topic_soup)

            # Пропускаем пустые или слишком короткие
            if not content or len(content) < 30:
                empty += 1
                continue

            full_text = title + ' ' + content[:1000]
            section = {
                'sectionId': str(i),
                'title': title,
                'content': content,
                'vehicle': model_id,
                'language': 'zh',
                'contentType': 'manual',
                'layer': classify_layer_zh(full_text),
                'source': 'web',
                'sourceUrl': topic_url,
                'chapter': topic['chapter'],
                'section': topic['section'],
                'glossaryIds': match_glossary_ids(full_text, glossary_index),
                'dtcCodes': list(set(re.findall(r'\b([PCBU]\d{4})\b', content))),
                'hasProcedures': bool(re.search(r'\d+[\.\)]\s', content)),
                'hasWarnings': any(w in content for w in ['注意', '警告', '危险']),
                'contentLength': len(content),
            }
            sections.append(section)

        print(f"\n  Результат:")
        print(f"    Секций получено: {len(sections)}")
        print(f"    Ошибок загрузки: {failed}")
        print(f"    Пустых страниц: {empty}")

        # Статистика по слоям
        layer_counts = {}
        for s in sections:
            layer_counts[s['layer']] = layer_counts.get(s['layer'], 0) + 1
        print(f"  По слоям:")
        for layer, count in sorted(layer_counts.items(), key=lambda x: -x[1]):
            print(f"    {layer}: {count}")

    return sections


def main():
    print("=" * 60)
    print("LLCAR KB — Скрапинг manuals.lixiang.com")
    print("=" * 60)

    os.makedirs(KB_DIR, exist_ok=True)

    glossary_index = load_glossary()
    print(f"  Глоссарий: {len(glossary_index)} терминов (ZH)")

    total_sections = 0
    for model_id, config in MODELS.items():
        sections = scrape_model(model_id, config, glossary_index)
        if not sections:
            print(f"\n  [!] Нет секций для {model_id}")
            continue

        output_name = f"web-sections-{model_id}-zh.json"
        output_path = os.path.join(KB_DIR, output_name)
        output_data = {
            'meta': {
                'vehicle': model_id,
                'language': 'zh',
                'contentType': 'manual',
                'source': 'web',
                'baseUrl': config['base_url'],
                'totalSections': len(sections),
            },
            'sections': sections,
        }
        save_json(output_data, output_path)
        total_sections += len(sections)

    print(f"\n{'=' * 60}")
    print(f"Итого web-секций: {total_sections}")
    print("=" * 60)


if __name__ == '__main__':
    main()
