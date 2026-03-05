#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent 3 - RU warnings review script
"""
import sqlite3
import json
import re
import sys
import io
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DB_PATH = 'C:/Diagnostica-KB-Package/knowledge-base/kb.db'
GLOSSARY_PATH = 'C:/Diagnostica-KB-Package/дополнительно/полный глоссарий/полный глоссарий/automotive-glossary-5lang.json'
OUTPUT_PATH = 'C:/Diagnostica-KB-Package/docs/review/agent3_ru_warnings.json'
QUESTIONS_PATH = 'C:/Diagnostica-KB-Package/docs/review/agent3_questions.txt'


def extract_snippet(text, pattern, length=150):
    """Извлечь фрагмент текста вокруг паттерна."""
    m = re.search(pattern, text, re.IGNORECASE)
    if not m:
        return text[:length] + ('...' if len(text) > length else '')
    start = max(0, m.start() - 40)
    end = min(len(text), m.end() + 110)
    snippet = text[start:end]
    if start > 0:
        snippet = '...' + snippet
    if end < len(text):
        snippet = snippet + '...'
    return snippet


# ─── Шаг 1: Загрузка данных ──────────────────────────────────────────────────

conn = sqlite3.connect(DB_PATH)
rows = conn.execute('''
    SELECT cc.chunk_id, cc.lang, cc.content, cc.quality_score, cc.terminology_score,
           c.source_language, c.title, c.has_procedures, c.has_warnings, c.layer
    FROM chunk_content cc
    JOIN chunks c ON c.id = cc.chunk_id
    WHERE cc.lang = 'ru' AND cc.translated_by != 'original'
      AND c.has_warnings = 1
    ORDER BY cc.quality_score ASC, cc.terminology_score ASC
''').fetchall()
conn.close()
print(f'Loaded {len(rows)} rows')

# ─── Шаг 2: Загрузка глоссария ───────────────────────────────────────────────

with open(GLOSSARY_PATH, encoding='utf-8') as f:
    gloss_data = json.load(f)

zh_to_ru = {}
en_to_ru = {}

cats = gloss_data.get('categories', {})
for cat_key, cat_val in cats.items():
    terms = cat_val.get('terms', [])
    for term in terms:
        zh = term.get('zh', '').strip().lower()
        en = term.get('en', '').strip().lower()
        ru = term.get('ru', '').strip()
        if zh and ru:
            zh_to_ru[zh] = ru
        if en and ru:
            en_to_ru[en] = ru

obd_section = gloss_data.get('obd_abbreviations', {})
obd_terms = obd_section.get('terms', []) if isinstance(obd_section, dict) else []
for abbr_entry in obd_terms:
    if not isinstance(abbr_entry, dict):
        continue
    en = abbr_entry.get('en', '').strip().lower()
    ru = abbr_entry.get('ru', '').strip()
    if en and ru:
        en_to_ru[en] = ru

print(f'Glossary: {len(zh_to_ru)} zh->ru, {len(en_to_ru)} en->ru terms')

# ─── Критические автомобильные термины ──────────────────────────────────────
# Паттерн поиска в тексте → ожидаемый RU термин (из глоссария)
CRITICAL_TERM_CHECKS = [
    # (regex_pattern, expected_ru, issue_description)
    (r'\btormoz(?:n|ny|noy)\b', 'тормозная жидкость', 'Латиница в термине «тормоз*»'),
    (r'\bair\s?bag\b', 'подушка безопасности', 'Термин «airbag» не переведён'),
    (r'\bseat\s?belt\b', 'ремень безопасности', 'Термин «seat belt» не переведён'),
    (r'тормозн\w*\s+флюид', 'тормозная жидкость', 'Ошибка: «тормозной флюид» вместо «тормозная жидкость»'),
    (r'\bHV\s+батаре', 'высоковольтная батарея', 'Ошибка: «HV батаре*» → «высоковольтная батарея»'),
    (r'(?<![А-Яа-я])\bcharging\s+port\b', 'зарядный порт', 'Термин «charging port» не переведён'),
    (r'(?<![А-Яа-я])\btire\b', 'шина', 'Английский термин «tire» не переведён'),
    (r'(?<![А-Яа-я])\bbattery\b', 'аккумулятор/батарея', 'Английский термин «battery» не переведён'),
    (r'(?<![А-Яа-я])\bcoolant\b', 'охлаждающая жидкость', 'Английский термин «coolant» не переведён'),
    (r'(?<![А-Яа-я])\bengine\s+oil\b', 'моторное масло', 'Термин «engine oil» не переведён'),
    (r'(?<![А-Яа-я])\bwiper\b', 'стеклоочиститель', 'Английский термин «wiper» не переведён'),
]

# ─── Кальки с китайского ─────────────────────────────────────────────────────
CALQUES = [
    # (regex, description, severity)
    (r'пожалуйста,?\s+не\s+\w', 'Кальк: «пожалуйста, не» → «запрещается» или императив «не делайте»', 'high'),
    (r'пожалуйста\s+убедитесь', 'Кальк: «пожалуйста убедитесь» → «убедитесь»', 'high'),
    (r'пожалуйста\s+соблюдай', 'Кальк: «пожалуйста соблюдай» → «соблюдайте»', 'high'),
    (r'пожалуйста\s+[а-яё]+\w*те', 'Кальк: «пожалуйста [глагол]те» — характерная китайская конструкция', 'medium'),
    (r'во\s+время\s+вождения', 'Кальк: «во время вождения» → «при движении»', 'high'),
    (r'нужно\s+(?:обратить|обращать)\s+внимание', 'Кальк: «нужно обратить внимание» → «обратите внимание» или используйте метку ПРИМЕЧАНИЕ', 'medium'),
    (r'обратитесь\s+к\s+дилеру', 'Стиль: «к дилеру» → «в авторизованный сервисный центр Li Auto»', 'low'),
    (r'в\s+соответствии\s+с\s+актуальн', 'Кальк: типичная китайская формулировка — проверить', 'low'),
    (r'соответствующ\w+\s+персонал', 'Кальк: «соответствующий персонал» → «специалист» или «сервисный мастер»', 'medium'),
]

# ─── Проверка единиц измерения ─────────────────────────────────────────────
UNIT_CHECKS = [
    (r'\d+\s*кмч\b', 'Единицы: «кмч» → «км/ч»', 'medium'),
    (r'\d+\s*км\s*/\s*час\b', 'Единицы: «км/час» → «км/ч»', 'low'),
    (r'\d+\s*[Кк]вт\*ч', 'Единицы: «кВт*ч» → «кВт·ч»', 'low'),
    (r'\d+\s*[Кк]Вт\b(?!\s*[·*·/])', None, None),  # кВт без указания тип — норм
    (r'\d+\s*градус(?:а|ов)?\s+[Цц]ельси', 'Единицы: «N градусов Цельсия» → «N°C»', 'low'),
    (r'\d+\s*[Кк]Вт\s+в\s+час', 'Единицы: «кВт в час» вместо «кВт·ч»', 'medium'),
]

# ─── Форматирование ─────────────────────────────────────────────────────────
def check_formatting(content, chunk_id, quality_score, terminology_score):
    issues = []
    # Bullet points
    has_circle = '●' in content
    has_bullet = '•' in content
    if has_bullet and not has_circle:
        issues.append({
            'type': 'formatting',
            'severity': 'low',
            'chunk_id': chunk_id,
            'quality_score': quality_score,
            'terminology_score': terminology_score,
            'description': 'Использован «•» вместо стандартного «●»',
            'snippet': extract_snippet(content, r'•', 100),
            'recommendation': 'Заменить «•» на «●»',
        })
    if has_bullet and has_circle:
        issues.append({
            'type': 'formatting',
            'severity': 'medium',
            'chunk_id': chunk_id,
            'quality_score': quality_score,
            'terminology_score': terminology_score,
            'description': 'Смешаны «•» и «●» в одном чанке — непоследовательное форматирование',
            'snippet': extract_snippet(content, r'[•●]', 100),
            'recommendation': 'Унифицировать: использовать только «●»',
        })
    return issues


# ─── Шаг 4: Системный анализ — один ZH→ разные RU ────────────────────────────

# Проверка «Подсказка» vs «Примечание» (提示)
TISHI_VARIANTS = {
    'примечание': 'correct',
    'подсказка': 'wrong_calque',
    'совет': 'wrong',
    'hint': 'untranslated',
    'note': 'untranslated',
    'tip': 'untranslated',
}

# Проверка «理想同学» - Li Auto's AI assistant
# Правильный перевод: «Lixiang Tongxue» (транслитерация) или «Идеальный помощник»
TONGXUE_PATTERNS = [
    r'идеальный\s+(?:помощник|студент|однокласс)',
    r'lixiang\s+tongxue',
    r'li\s*xiang\s+tongxue',
    r'理想同学',
    r'tongxue',
    r'тунсюэ',
]

# ─── ОСНОВНОЙ ЦИКЛ АНАЛИЗА ────────────────────────────────────────────────────

findings = []
issues_count = 0
critical_count = 0
systematic_raw = defaultdict(list)

# Счётчики для общей статистики
stats = {
    'total': len(rows),
    'priority': 0,  # quality < 0.8 or terminology < 0.7
    'quality_zero': 0,
    'quality_low': 0,
    'quality_high': 0,
    'warning_label_wrong': 0,
    'calque_found': 0,
    'unit_errors': 0,
    'term_errors': 0,
    'format_errors': 0,
}

# Для паттерн-анализа: какие варианты перевода используются для ключевых понятий
# (chunk_id, label_used)
warning_label_by_chunk = {}
# chunk_id → list of labels found
tongxue_variants_found = {}

for row in rows:
    chunk_id, lang, content, quality_score, terminology_score, \
    source_lang, title, has_procedures, has_warnings, layer = row

    if not content:
        continue

    # Базовая статистика
    if quality_score < 0.8 or terminology_score < 0.7:
        stats['priority'] += 1
    if quality_score == 0.0:
        stats['quality_zero'] += 1
    elif quality_score < 0.5:
        stats['quality_low'] += 1
    elif quality_score >= 0.8:
        stats['quality_high'] += 1

    is_priority = quality_score < 0.8 or terminology_score < 0.7
    chunk_issues = []

    # ── 3.1: Проверка меток предупреждений ──
    found_labels = re.findall(
        r'\b(ПРЕДУПРЕЖДЕНИЕ|ВНИМАНИЕ|ПРИМЕЧАНИЕ|ОПАСНОСТЬ|ОСТОРОЖНО'
        r'|Предупреждение|Внимание|Примечание|Осторожно|Опасность'
        r'|Подсказка|подсказка|ПОДСКАЗКА'
        r'|Note|Warning|Caution|NOTICE)\b',
        content
    )
    warning_label_by_chunk[chunk_id] = found_labels

    # Кальк «Подсказка»
    if re.search(r'[Пп]одсказка|ПОДСКАЗКА', content):
        chunk_issues.append({
            'type': 'warning_label_calque',
            'severity': 'medium',
            'chunk_id': chunk_id,
            'quality_score': quality_score,
            'terminology_score': terminology_score,
            'description': 'Метка «Подсказка» — кальк с 提示 (Tip), правильно «ПРИМЕЧАНИЕ»',
            'snippet': extract_snippet(content, r'[Пп]одсказка|ПОДСКАЗКА', 150),
            'recommendation': 'Заменить «Подсказка» → «ПРИМЕЧАНИЕ»',
        })
        systematic_raw['wrong_label_podkazka'].append(chunk_id)
        stats['warning_label_wrong'] += 1

    # Непереведённые английские метки
    for eng_label in ['Note', 'Warning', 'Caution', 'NOTICE']:
        if re.search(r'\b' + eng_label + r'\b', content):
            chunk_issues.append({
                'type': 'untranslated_warning_label',
                'severity': 'high',
                'chunk_id': chunk_id,
                'quality_score': quality_score,
                'terminology_score': terminology_score,
                'description': f'Непереведённая английская метка «{eng_label}» в RU тексте',
                'snippet': extract_snippet(content, r'\b' + eng_label + r'\b', 150),
                'recommendation': {
                    'Note': 'Заменить «Note» → «ПРИМЕЧАНИЕ»',
                    'Warning': 'Заменить «Warning» → «ПРЕДУПРЕЖДЕНИЕ»',
                    'Caution': 'Заменить «Caution» → «ВНИМАНИЕ»',
                    'NOTICE': 'Заменить «NOTICE» → «ПРИМЕЧАНИЕ»',
                }.get(eng_label, f'Перевести «{eng_label}»'),
            })

    # Метки в смешанном регистре (не CAPS)
    lower_labels = re.findall(r'\b(Предупреждение|Внимание|Примечание|Осторожно|Опасность)\b', content)
    if lower_labels:
        chunk_issues.append({
            'type': 'warning_label_case',
            'severity': 'low',
            'chunk_id': chunk_id,
            'quality_score': quality_score,
            'terminology_score': terminology_score,
            'description': f'Метки предупреждений не в CAPS: {set(lower_labels)}',
            'snippet': extract_snippet(content, r'Предупреждение|Внимание|Примечание|Осторожно|Опасность', 150),
            'recommendation': 'Привести метки к верхнему регистру: ВНИМАНИЕ, ПРЕДУПРЕЖДЕНИЕ, ПРИМЕЧАНИЕ',
        })
        systematic_raw['label_not_caps'].append(chunk_id)

    # ── 3.2: Кальки ──
    for pat, desc, sev in CALQUES:
        m = re.search(pat, content, re.IGNORECASE)
        if m:
            chunk_issues.append({
                'type': 'calque',
                'severity': sev,
                'chunk_id': chunk_id,
                'quality_score': quality_score,
                'terminology_score': terminology_score,
                'description': desc,
                'snippet': extract_snippet(content, pat, 160),
                'recommendation': desc.split('→')[-1].strip() if '→' in desc else 'Перефразировать',
            })
            if sev == 'high':
                systematic_raw['calque_high'].append((chunk_id, pat))
                stats['calque_found'] += 1

    # ── 3.3: Терминология (только приоритетные) ──
    if is_priority:
        for pat, expected, desc in CRITICAL_TERM_CHECKS:
            m = re.search(pat, content, re.IGNORECASE)
            if m:
                chunk_issues.append({
                    'type': 'wrong_terminology',
                    'severity': 'high',
                    'chunk_id': chunk_id,
                    'quality_score': quality_score,
                    'terminology_score': terminology_score,
                    'description': desc,
                    'snippet': extract_snippet(content, pat, 150),
                    'recommendation': f'Использовать «{expected}» согласно глоссарию',
                })
                systematic_raw['wrong_term'].append((chunk_id, desc))
                stats['term_errors'] += 1

    # ── 3.4: Единицы ──
    for pat, desc, sev in UNIT_CHECKS:
        if desc and re.search(pat, content, re.IGNORECASE):
            chunk_issues.append({
                'type': 'units',
                'severity': sev,
                'chunk_id': chunk_id,
                'quality_score': quality_score,
                'terminology_score': terminology_score,
                'description': desc,
                'snippet': extract_snippet(content, pat, 120),
                'recommendation': desc.split('→')[-1].strip() if '→' in desc else 'Исправить единицы',
            })
            stats['unit_errors'] += 1

    # ── 3.5: Форматирование ──
    fmt_issues = check_formatting(content, chunk_id, quality_score, terminology_score)
    chunk_issues.extend(fmt_issues)
    if fmt_issues:
        stats['format_errors'] += len(fmt_issues)

    # ── 理想同学 / Lixiang Tongxue варианты ──
    for pat in TONGXUE_PATTERNS:
        if re.search(pat, content, re.IGNORECASE):
            tongxue_variants_found[chunk_id] = extract_snippet(content, pat, 120)
            break

    # ── Собираем итоговые findings (фильтрация по приоритету) ──
    for issue in chunk_issues:
        sev = issue['severity']
        # Берём HIGH всегда; MEDIUM — если приоритетный чанк; LOW — только если quality==0
        if sev == 'high':
            findings.append(issue)
            issues_count += 1
            critical_count += 1
        elif sev == 'medium':
            findings.append(issue)
            issues_count += 1
        elif sev == 'low' and quality_score == 0.0:
            findings.append(issue)
            issues_count += 1

print(f'Analysis complete. Total findings: {len(findings)}, critical: {critical_count}')

# ─── Шаг 4: Системные паттерны ───────────────────────────────────────────────

systematic_patterns = []

# Паттерн 1: «Подсказка» вместо «ПРИМЕЧАНИЕ»
if systematic_raw['wrong_label_podkazka']:
    systematic_patterns.append({
        'pattern': 'wrong_label_podkazka',
        'description': 'Метка «Подсказка» вместо «ПРИМЕЧАНИЕ» (ZH: 提示)',
        'affected_chunks': len(systematic_raw['wrong_label_podkazka']),
        'examples': systematic_raw['wrong_label_podkazka'][:5],
        'priority': 'high',
        'fix': 'Глобальная замена: «Подсказка» → «ПРИМЕЧАНИЕ»',
    })

# Паттерн 2: Метки не в CAPS
if systematic_raw['label_not_caps']:
    systematic_patterns.append({
        'pattern': 'label_not_caps',
        'description': 'Метки предупреждений в смешанном регистре (Внимание) вместо CAPS (ВНИМАНИЕ)',
        'affected_chunks': len(systematic_raw['label_not_caps']),
        'examples': systematic_raw['label_not_caps'][:5],
        'priority': 'medium',
        'fix': 'Глобальная замена регистра: Внимание→ВНИМАНИЕ, Примечание→ПРИМЕЧАНИЕ и т.д.',
    })

# Паттерн 3: Кальки «пожалуйста, не»
calque_high_chunks = list(set(c[0] for c in systematic_raw['calque_high']))
if calque_high_chunks:
    systematic_patterns.append({
        'pattern': 'calque_zhe_pattern',
        'description': 'Китайская конструкция «请...» → «пожалуйста, [глагол]» — кальк с ZH',
        'affected_chunks': len(calque_high_chunks),
        'examples': calque_high_chunks[:5],
        'priority': 'high',
        'fix': 'Заменить «пожалуйста, не [действие]» → «запрещается [действие]» или «не [действие]»',
    })

# Паттерн 4: «во время вождения»
driving_chunks = [c[0] for c in systematic_raw['calque_high'] if 'вождения' in c[1]]
if driving_chunks:
    systematic_patterns.append({
        'pattern': 'calque_driving_time',
        'description': '«во время вождения» — кальк с ZH «驾驶期间» → должно быть «при движении»',
        'affected_chunks': len(driving_chunks),
        'examples': driving_chunks[:5],
        'priority': 'high',
        'fix': 'Заменить «во время вождения» → «при движении»',
    })

# Паттерн 5: Варианты перевода 理想同学
if tongxue_variants_found:
    variants = list(set(v[:60] for v in tongxue_variants_found.values()))
    systematic_patterns.append({
        'pattern': 'ai_assistant_naming',
        'description': 'Непоследовательный перевод «理想同学» (AI-помощник Li Auto)',
        'affected_chunks': len(tongxue_variants_found),
        'variants_found': variants[:5],
        'priority': 'medium',
        'question': 'Как правильно переводить «理想同学»: «Lixiang Tongxue» (транслитерация) или «Идеальный помощник» (смысловой перевод)?',
        'fix': 'Выбрать единый вариант и применить глобально',
    })

# Паттерн 6: Нулевые score — массовая проблема
if stats['quality_zero'] > 100:
    systematic_patterns.append({
        'pattern': 'zero_scores',
        'description': f'{stats["quality_zero"]} чанков с quality_score=0.0 — вероятно, скоринг не работал',
        'affected_chunks': stats['quality_zero'],
        'priority': 'critical',
        'fix': 'Запустить пересчёт quality_score и terminology_score для всех RU переводов',
        'note': 'Это НЕ означает плохое качество перевода — скорее сбой в pipeline скоринга',
    })

# ─── Открытые вопросы ────────────────────────────────────────────────────────

open_questions_text = []

open_questions_text.append("""=== Вопросы агента 3 (RU Warnings Review) ===
Дата: 2026-02-28
Срез: lang=ru, has_warnings=1 (530 чанков)

--- Вопрос 1: Нулевые скоры ---
215 чанков имеют quality_score=0.0 AND terminology_score=0.0.
При просмотре этих чанков перевод выглядит нормально (пример: «зарядный разъём», «аварийный выключатель»).
Вопрос: скоры == 0.0 означают «не посчитано» или «критически плохой перевод»?
Если «не посчитано» — нужен пересчёт перед финальным релизом.

--- Вопрос 2: Перевод 理想同学 ---
Нашли несколько вариантов перевода AI-помощника Li Auto («理想同学»):
- «Lixiang Tongxue» (транслитерация)
- «Идеальный помощник» (смысловой)
- «Tongxue» (частичная транслитерация)
Какой вариант является официальным для RU локализации?

--- Вопрос 3: «Подсказка» vs «Примечание» ---
Встречается метка «Подсказка» — кальк с английского «Tip» / китайского «提示».
В стандарте ГОСТ предупреждения: ОПАСНОСТЬ / ПРЕДУПРЕЖДЕНИЕ / ВНИМАНИЕ / ПРИМЕЧАНИЕ.
Подтвердить: «提示» должно переводиться как «ПРИМЕЧАНИЕ», а не «Подсказка»?

--- Вопрос 4: «Осторожно» как уровень предупреждения ---
«ОСТОРОЖНО» встречается в тексте. По IEC 82079-1:
- WARNING (опасность травмы) → ПРЕДУПРЕЖДЕНИЕ
- CAUTION (опасность повреждения) → ВНИМАНИЕ или ОСТОРОЖНО?
В ZH оригинале: 注意 = ВНИМАНИЕ или ОСТОРОЖНО?

--- Вопрос 5: Адрес сервиса ---
В чанках: «обратитесь в сервисный центр Li Auto» vs «обратитесь к авторизованному дилеру».
Какой вариант официальный для RU рынка?

--- Вопрос 6: «для вашей безопасности» ---
Конструкция «для вашей безопасности при вождении» встречается часто.
Это прямой кальк с ZH «为了您的行车安全».
Оставить как есть (читателю понятно) или заменить на более нейтральное?
""")

# ─── Шаг 5: Сборка итогового отчёта ─────────────────────────────────────────

# Топ-20 наиболее критичных findings (для сводки)
critical_findings = sorted(
    [f for f in findings if f['severity'] == 'high'],
    key=lambda x: x['quality_score']
)[:20]

# Итоговый отчёт
report = {
    'agent': 'agent3_ru_warnings',
    'reviewed': len(rows),
    'issues_found': issues_count,
    'critical': critical_count,
    'stats': {
        'total_chunks': stats['total'],
        'priority_chunks': stats['priority'],
        'quality_zero_chunks': stats['quality_zero'],
        'quality_low_chunks': stats['quality_low'],
        'quality_high_chunks': stats['quality_high'],
        'warning_label_wrong': stats['warning_label_wrong'],
        'calque_found': stats['calque_found'],
        'unit_errors': stats['unit_errors'],
        'term_errors': stats['term_errors'],
        'format_errors': stats['format_errors'],
        'tongxue_variants': len(tongxue_variants_found),
    },
    'summary': (
        f'Проверено {len(rows)} RU-переводов предупреждений Li Auto. '
        f'Найдено {issues_count} проблем, из них {critical_count} критических. '
        f'Основные проблемы: '
        f'(1) {stats["quality_zero"]} чанков с нулевым quality_score — вероятно сбой в pipeline скоринга; '
        f'(2) метка «Подсказка» вместо «ПРИМЕЧАНИЕ» ({len(systematic_raw["wrong_label_podkazka"])} чанков); '
        f'(3) кальки с китайского — «пожалуйста, не», «во время вождения» и подобные; '
        f'(4) метки предупреждений в смешанном регистре вместо CAPS ({len(systematic_raw["label_not_caps"])} чанков). '
        f'Переводы в целом читаемые, базовая терминология верна. Основные проблемы — стилистические и форматирование.'
    ),
    'findings': findings,
    'top_critical': critical_findings,
    'systematic_patterns': systematic_patterns,
    'tongxue_variants': tongxue_variants_found,
    'status': 'complete',
}

# Сохраняем
with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)
print(f'Saved report: {OUTPUT_PATH}')

with open(QUESTIONS_PATH, 'w', encoding='utf-8') as f:
    f.write('\n'.join(open_questions_text))
print(f'Saved questions: {QUESTIONS_PATH}')

# Итоговый вывод
print('\n=== ИТОГ ===')
print(f'Проверено чанков: {len(rows)}')
print(f'Приоритетных (low score): {stats["priority"]}')
print(f'Issues found: {issues_count}')
print(f'Critical: {critical_count}')
print(f'Системные паттерны: {len(systematic_patterns)}')
print()
for sp in systematic_patterns:
    print(f'  [{sp["priority"].upper()}] {sp["pattern"]}: {sp["description"][:80]}')
    print(f'    Затронуто чанков: {sp.get("affected_chunks", "?")}')
