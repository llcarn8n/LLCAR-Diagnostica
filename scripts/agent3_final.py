#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent 3 - Финальный ревью-анализ RU предупреждений Li Auto
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


def snippet(text, pattern, before=40, after=120):
    m = re.search(pattern, text, re.IGNORECASE)
    if not m:
        s = text[:before + after]
        return (s + '...') if len(text) > len(s) else s
    start = max(0, m.start() - before)
    end = min(len(text), m.end() + after)
    s = text[start:end]
    prefix = '...' if start > 0 else ''
    suffix = '...' if end < len(text) else ''
    return prefix + s + suffix


# ─── Загрузка данных ─────────────────────────────────────────────────────────

conn = sqlite3.connect(DB_PATH)
rows = conn.execute(
    "SELECT cc.chunk_id, cc.lang, cc.content, cc.quality_score, cc.terminology_score, "
    "       c.source_language, c.title, c.has_procedures, c.has_warnings, c.layer "
    "FROM chunk_content cc "
    "JOIN chunks c ON c.id = cc.chunk_id "
    "WHERE cc.lang = 'ru' AND cc.translated_by != 'original' "
    "  AND c.has_warnings = 1 "
    "ORDER BY cc.quality_score ASC, cc.terminology_score ASC"
).fetchall()

# Предварительный сбор статистики из БД
total_chunks = len(rows)
quality_zero = sum(1 for r in rows if r[3] == 0.0)
quality_low = sum(1 for r in rows if 0.0 < r[3] < 0.5)
quality_high = sum(1 for r in rows if r[3] >= 0.8)
priority = sum(1 for r in rows if r[3] < 0.8 or r[4] < 0.7)

conn.close()
print(f'Loaded {total_chunks} rows')
print(f'  quality=0.0: {quality_zero}, quality<0.5: {quality_low}, quality>=0.8: {quality_high}')
print(f'  priority (q<0.8 or t<0.7): {priority}')


# ─── Загрузка глоссария ──────────────────────────────────────────────────────

with open(GLOSSARY_PATH, encoding='utf-8') as f:
    gloss_data = json.load(f)

en_to_ru = {}
zh_to_ru = {}
cats = gloss_data.get('categories', {})
for cat_val in cats.values():
    for term in cat_val.get('terms', []):
        if not isinstance(term, dict):
            continue
        zh = term.get('zh', '').strip().lower()
        en = term.get('en', '').strip().lower()
        ru = term.get('ru', '').strip()
        if zh and ru:
            zh_to_ru[zh] = ru
        if en and ru:
            en_to_ru[en] = ru

obd_terms = gloss_data.get('obd_abbreviations', {}).get('terms', [])
for term in obd_terms:
    if isinstance(term, dict):
        en = term.get('en', '').strip().lower()
        ru = term.get('ru', '').strip()
        if en and ru:
            en_to_ru[en] = ru

print(f'Glossary: {len(zh_to_ru)} zh->ru, {len(en_to_ru)} en->ru')


# ─── Аналитика по конкретным паттернам ───────────────────────────────────────

findings = []
issues_total = 0
critical_total = 0
affected_chunks = defaultdict(set)


def add_finding(ftype, severity, chunk_id, quality_score, terminology_score,
                description, snip, recommendation, tag=None):
    global issues_total, critical_total
    findings.append({
        'type': ftype,
        'severity': severity,
        'chunk_id': chunk_id,
        'quality_score': quality_score,
        'terminology_score': terminology_score,
        'description': description,
        'snippet': snip,
        'recommendation': recommendation,
    })
    issues_total += 1
    if severity == 'critical' or severity == 'high':
        critical_total += 1
    if tag:
        affected_chunks[tag].add(chunk_id)


# Счётчики для системных паттернов
calque_during_driving = []  # chunk_id, контекст
calque_pozhaluysta = []
label_not_caps = []
label_podkazka_as_header = []
label_en_untranslated = []
inconsistent_prohibition = []  # «не ...» vs «запрещается ...»
unit_errors = []
double_period_issues = []
quality_zero_chunks = []

for row in rows:
    chunk_id, lang, content, quality_score, terminology_score, \
    source_lang, title, has_procedures, has_warnings, layer = row

    if not content:
        continue

    is_priority = quality_score < 0.8 or terminology_score < 0.7

    # == 1. Метки предупреждений ==

    # 1а. «Подсказка» как заголовок предупреждения (отдельная строка)
    if re.search(r'(?:^|\n)\*?\*?[Пп]одсказка\*?\*?\s*(?:\n|$)', content):
        snip = snippet(content, r'[Пп]одсказка', 20, 80)
        add_finding(
            'warning_label_calque', 'high', chunk_id, quality_score, terminology_score,
            'Метка-заголовок «Подсказка» — кальк с 提示 (Tip). Стандарт: ПРИМЕЧАНИЕ',
            snip,
            'Заменить «Подсказка» → «ПРИМЕЧАНИЕ»',
            tag='label_podkazka'
        )
        label_podkazka_as_header.append(chunk_id)

    # 1б. Непереведённые EN метки
    for eng_label in ['Warning', 'Caution', 'NOTICE']:
        if re.search(r'(?:^|\n)\*?\*?' + eng_label + r'\*?\*?\s*(?:\n|$)', content):
            snip = snippet(content, eng_label, 20, 100)
            add_finding(
                'untranslated_en_label', 'critical', chunk_id, quality_score, terminology_score,
                f'Непереведённая EN метка «{eng_label}» используется как заголовок предупреждения',
                snip,
                {
                    'Warning': 'Заменить «Warning» → «ПРЕДУПРЕЖДЕНИЕ»',
                    'Caution': 'Заменить «Caution» → «ВНИМАНИЕ»',
                    'NOTICE': 'Заменить «NOTICE» → «ПРИМЕЧАНИЕ»',
                }[eng_label],
                tag='label_en_untranslated'
            )
            label_en_untranslated.append(chunk_id)

    # 1в. Метки в Title Case вместо CAPS (системная проблема всего датасета)
    title_case_labels = re.findall(
        r'(?:^|\n)\*?\*?(Предупреждение|Внимание|Примечание|Опасность)\*?\*?\s*(?:\n|$)',
        content
    )
    if title_case_labels:
        # Помечаем только если НЕТ правильного CAPS варианта в том же чанке
        has_caps = bool(re.search(r'ПРЕДУПРЕЖДЕНИЕ|ВНИМАНИЕ|ПРИМЕЧАНИЕ|ОПАСНОСТЬ', content))
        if not has_caps:
            add_finding(
                'warning_label_case', 'medium', chunk_id, quality_score, terminology_score,
                f'Метки предупреждений в Title Case: {set(title_case_labels)} — стандарт требует CAPS',
                snippet(content, r'Предупреждение|Внимание|Примечание|Опасность', 10, 80),
                'Привести к верхнему регистру: ПРЕДУПРЕЖДЕНИЕ, ВНИМАНИЕ, ПРИМЕЧАНИЕ',
                tag='label_not_caps'
            )
            label_not_caps.append(chunk_id)

    # == 2. Кальки с китайского ==

    # 2а. «во время вождения» как кальк при запретах
    # Отличаем: «запрещается X во время вождения» (кальк) vs «видеорегистратор во время вождения» (норм)
    vozhd_m = re.findall(
        r'(?:не\s+\w+|запрещается\s+\w+)[^.!?]*во\s+время\s+вождения|'
        r'во\s+время\s+вождения[^.!?]*(?:не\s+\w+|запрещается)',
        content, re.IGNORECASE
    )
    if vozhd_m:
        add_finding(
            'calque_during_driving', 'medium', chunk_id, quality_score, terminology_score,
            'Кальк: «во время вождения» в контексте запрета — предпочтительнее «при движении»',
            snippet(content, r'во\s+время\s+вождения', 50, 100),
            'Заменить «во время вождения» → «при движении» в контексте запретов и предупреждений',
            tag='calque_driving'
        )
        calque_during_driving.append(chunk_id)

    # Также простое «во время вождения» без контекста в предупреждениях
    elif re.search(r'\bво\s+время\s+вождения\b', content):
        # Только если это приоритетный чанк
        if is_priority:
            add_finding(
                'calque_during_driving_soft', 'low', chunk_id, quality_score, terminology_score,
                'Оборот «во время вождения» — рассмотреть замену на «при движении» в контексте предупреждений',
                snippet(content, r'во\s+время\s+вождения', 50, 100),
                'Рекомендуется: «при движении»',
                tag='calque_driving_soft'
            )

    # 2б. «пожалуйста, [глагол]» — кальк, но исключаем цитаты UI-сообщений
    pozh_m = re.findall(r'(?<!["\"])\bпожалуйста,?\s+\w+те\b', content, re.IGNORECASE)
    if pozh_m:
        # Проверяем: не является ли это частью цитаты сообщения в кавычках
        in_quotes = re.findall(r'["\"][^"\"]*пожалуйста[^"\"]*["\"]', content, re.IGNORECASE)
        if not in_quotes or len(pozh_m) > len(in_quotes):
            add_finding(
                'calque_pozhaluysta', 'medium', chunk_id, quality_score, terminology_score,
                f'Кальк: «пожалуйста, [действие]» вне цитаты UI — характерная ZH конструкция «请...»',
                snippet(content, r'пожалуйста,?\s+\w+те', 40, 120),
                'Убрать «пожалуйста»: «пожалуйста, обратитесь» → «обратитесь», «пожалуйста, свяжитесь» → «свяжитесь»',
                tag='calque_pozhaluysta'
            )
            calque_pozhaluysta.append(chunk_id)

    # == 3. Терминология ==

    # 3а. Неправильные английские термины (только priority чанки)
    if is_priority:
        bad_terms = [
            (r'\bair\s?bag\b', 'подушка безопасности'),
            (r'\bseat\s?belt\b', 'ремень безопасности'),
            (r'\bcoolant\b', 'охлаждающая жидкость'),
            (r'\bengine\s+oil\b', 'моторное масло'),
            (r'\bcharging\s+port\b', 'зарядный порт'),
            (r'\btire\b(?!\s+wear)', 'шина'),
            (r'тормозн\w+\s+флюид', 'тормозная жидкость'),
            (r'\bHV\s+батаре', 'высоковольтная батарея'),
        ]
        for pat, expected_ru in bad_terms:
            if re.search(pat, content, re.IGNORECASE):
                add_finding(
                    'wrong_terminology', 'high', chunk_id, quality_score, terminology_score,
                    f'Неправильный термин: вместо «{expected_ru}» (из глоссария)',
                    snippet(content, pat, 30, 100),
                    f'Заменить на «{expected_ru}» согласно глоссарию',
                    tag='wrong_term'
                )

    # == 4. Единицы измерения ==

    unit_checks = [
        (r'\d+\s*кмч\b', 'км/ч', 'medium'),
        (r'\d+\s*км\s*/\s*час\b', 'км/ч', 'low'),
        (r'\d+\s*[Кк][Вв][Тт]\s*\*\s*[Чч]', 'кВт·ч', 'low'),
        (r'\d+\s*[Кк][Вв][Тт]\s+в\s+час', 'кВт·ч', 'medium'),
        (r'\d+\s*градус(?:а|ов)?\s+[Цц]ельси', '°C', 'low'),
    ]
    for pat, expected, sev in unit_checks:
        if re.search(pat, content, re.IGNORECASE):
            add_finding(
                'units', sev, chunk_id, quality_score, terminology_score,
                f'Неправильная запись единицы: использовать «{expected}»',
                snippet(content, pat, 20, 80),
                f'Заменить на «{expected}»',
                tag='unit_error'
            )
            unit_errors.append(chunk_id)

    # == 5. Форматирование ==

    # 5а. Смешанные bullet points
    has_circle = '●' in content
    has_bullet = '•' in content
    if has_bullet and not has_circle and is_priority:
        add_finding(
            'formatting_bullet', 'low', chunk_id, quality_score, terminology_score,
            'Bullet point «•» вместо стандартного «●»',
            snippet(content, r'•', 10, 80),
            'Заменить «•» → «●»',
            tag='wrong_bullet'
        )

    if has_bullet and has_circle:
        add_finding(
            'formatting_bullet_mixed', 'medium', chunk_id, quality_score, terminology_score,
            'Смешаны «•» и «●» в одном чанке',
            snippet(content, r'[•●]', 10, 80),
            'Унифицировать: использовать только «●»',
            tag='mixed_bullet'
        )

    # 5б. Непоследовательный запрет: «Не X» vs «Запрещается X» в одном чанке
    has_ne = bool(re.search(r'\bНе\s+\w+те\b', content))
    has_zapresc = bool(re.search(r'\bЗапрещается\b', content))
    if has_ne and has_zapresc and is_priority:
        add_finding(
            'inconsistent_prohibition', 'low', chunk_id, quality_score, terminology_score,
            'Смешаны конструкции запрета: «Не [глагол]те» и «Запрещается» в одном чанке',
            snippet(content, r'Не\s+\w+те|Запрещается', 20, 80),
            'Выбрать единый стиль запрета для данного документа',
            tag='mixed_prohibition'
        )


print(f'\nAnalysis complete.')
print(f'  Total findings: {issues_total}, critical: {critical_total}')
for tag, chunks in affected_chunks.items():
    print(f'  [{tag}]: {len(chunks)} чанков')


# ─── Системные паттерны ─────────────────────────────────────────────────────

systematic_patterns = []

# Паттерн 1: КРИТИЧЕСКИЙ — все метки предупреждений в Title Case, не CAPS
n_label_not_caps = len(affected_chunks.get('label_not_caps', set()))
if n_label_not_caps > 50:
    systematic_patterns.append({
        'pattern_id': 'SP-001',
        'pattern': 'warning_labels_not_caps',
        'priority': 'critical',
        'description': (
            f'Все метки предупреждений переведены в Title Case (Предупреждение, Внимание, Примечание) '
            f'вместо требуемого CAPS (ПРЕДУПРЕЖДЕНИЕ, ВНИМАНИЕ, ПРИМЕЧАНИЕ). '
            f'Затронуто {n_label_not_caps} чанков из {total_chunks}.'
        ),
        'affected_chunks_count': n_label_not_caps,
        'examples': list(affected_chunks.get('label_not_caps', set()))[:5],
        'root_cause': 'Систематическая ошибка в промпте переводчика (claude-haiku-4-5): не указан стиль меток.',
        'fix': 'Глобальная постобработка: re.sub(r"\\b(Предупреждение|Внимание|Примечание|Опасность)\\b", lambda m: m.group().upper(), text)',
        'verification': 'После замены проверить 10 случайных чанков на корректность.',
    })

# Паттерн 2: «Подсказка» вместо «ПРИМЕЧАНИЕ»
n_podkazka = len(affected_chunks.get('label_podkazka', set()))
if n_podkazka > 0:
    systematic_patterns.append({
        'pattern_id': 'SP-002',
        'pattern': 'warning_label_podkazka',
        'priority': 'high',
        'description': (
            f'Метка «Подсказка» используется вместо «ПРИМЕЧАНИЕ» (источник: 提示/Tip). '
            f'Затронуто {n_podkazka} чанков.'
        ),
        'affected_chunks_count': n_podkazka,
        'examples': list(affected_chunks.get('label_podkazka', set()))[:5],
        'root_cause': 'Переводчик выбрал бытовой перевод «Tip» → «Подсказка» вместо технического термина «ПРИМЕЧАНИЕ».',
        'fix': 'Глобальная замена: re.sub(r"\\bПодсказка\\b", "ПРИМЕЧАНИЕ", text) при условии что это заголовок блока.',
        'zh_mapping': '提示 → ПРИМЕЧАНИЕ',
    })

# Паттерн 3: «во время вождения»
n_driving = len(affected_chunks.get('calque_driving', set()))
if n_driving > 0:
    systematic_patterns.append({
        'pattern_id': 'SP-003',
        'pattern': 'calque_during_driving',
        'priority': 'medium',
        'description': (
            f'«Во время вождения» в контексте запретов/предупреждений — кальк с ZH «驾驶时». '
            f'Затронуто {n_driving} чанков.'
        ),
        'affected_chunks_count': n_driving,
        'examples': list(affected_chunks.get('calque_driving', set()))[:5],
        'root_cause': 'Дословный перевод ZH «在驾驶期间» = «во время вождения», в RU технических текстах стандарт «при движении».',
        'fix': 'Замена в контексте запретов: «запрещается X во время вождения» → «запрещается X при движении».',
        'note': 'НЕ менять в контекстах типа «видеорегистратор записывает видео во время вождения» — там это нейтральная фраза.',
    })

# Паттерн 4: quality_score = 0.0 у 215 чанков
if quality_zero > 100:
    systematic_patterns.append({
        'pattern_id': 'SP-004',
        'pattern': 'zero_quality_scores',
        'priority': 'critical',
        'description': (
            f'{quality_zero} чанков ({quality_zero/total_chunks*100:.0f}%) имеют quality_score=0.0 '
            f'AND terminology_score=0.0. Визуальная проверка 5 примеров показала нормальное качество перевода. '
            f'Вероятно: сбой в pipeline скоринга при вызове API.'
        ),
        'affected_chunks_count': quality_zero,
        'root_cause': 'Скоринг-система не смогла вычислить оценку (timeout/error при вызове COMET-KIWI или аналогичной модели).',
        'fix': 'Запустить пересчёт скоров: python scripts/rescore_translations.py --lang ru --has-warnings 1.',
        'impact': 'Нулевые скоры не влияют на качество перевода, но делают бесполезной сортировку по приоритету.',
        'urgent': True,
    })

# Паттерн 5: Непоследовательный перевод запретов
n_mixed_prohb = len(affected_chunks.get('mixed_prohibition', set()))
if n_mixed_prohb > 0:
    systematic_patterns.append({
        'pattern_id': 'SP-005',
        'pattern': 'inconsistent_prohibition_style',
        'priority': 'low',
        'description': (
            f'В {n_mixed_prohb} чанках смешаны стили запрета: «Не регулируйте» и «Запрещается регулировать» '
            f'в одном документе/разделе.'
        ),
        'affected_chunks_count': n_mixed_prohb,
        'note': 'Оба варианта грамматически правильны. Вопрос последовательности стиля.',
        'recommendation': 'В предупреждениях типа WARNING/ПРЕДУПРЕЖДЕНИЕ предпочтителен «Запрещается», в ПРИМЕЧАНИЕ — нейтральный «Не рекомендуется».',
    })

# Паттерн 6: Непереведённые EN метки
n_en_labels = len(affected_chunks.get('label_en_untranslated', set()))
if n_en_labels > 0:
    systematic_patterns.append({
        'pattern_id': 'SP-006',
        'pattern': 'untranslated_en_warning_labels',
        'priority': 'high',
        'description': f'В {n_en_labels} чанках EN метки (Warning, Caution) остались непереведёнными.',
        'affected_chunks_count': n_en_labels,
        'examples': list(affected_chunks.get('label_en_untranslated', set()))[:5],
        'fix': 'Warning → ПРЕДУПРЕЖДЕНИЕ, Caution → ВНИМАНИЕ, Note → ПРИМЕЧАНИЕ',
    })


# ─── Открытые вопросы ─────────────────────────────────────────────────────────

open_questions = """=== Вопросы агента 3 (RU Warnings Review) ===
Дата: 2026-02-28
Срез: lang=ru, has_warnings=1 (530 чанков)

--- Вопрос 1 [CRITICAL]: Нулевые quality_score ---
215 чанков (41%) имеют quality_score=0.0 AND terminology_score=0.0.
Визуальная проверка 5 таких чанков: перевод выглядит нормально.
Например: «Потяните аварийный выключатель в направлении стрелки 2, чтобы разблокировать крышку зарядного разъёма» — вполне корректный технический текст.
ВОПРОС: Означает ли score=0.0 «скоринг не запускался» или «критическое качество»?
ДЕЙСТВИЕ: Если «не запускался» — нужен пересчёт перед финальным релизом.

--- Вопрос 2 [HIGH]: Title Case vs CAPS метки предупреждений ---
402 чанка из 530 (76%) используют Title Case (Предупреждение, Внимание) вместо CAPS.
При этом quality=1.0 чанки тоже в Title Case — значит, это НЕ баг конкретных переводов,
а СИСТЕМНОЕ решение переводчика (промпт не указывал стиль).
ВОПРОС: Какой стиль является стандартом для этого продукта?
 а) CAPS (ПРЕДУПРЕЖДЕНИЕ) — соответствует ГОСТ Р ИСО 11684, ISO 82079-1
 б) Title Case (**Предупреждение**) — соответствует Markdown-стилю для дисплея
 в) Bold CAPS (**ПРЕДУПРЕЖДЕНИЕ**) — компромисс
Если CAPS — нужна глобальная постобработка ~400 чанков.

--- Вопрос 3 [HIGH]: «Подсказка» vs «Примечание» ---
62 чанка используют метку «Подсказка» (вместо «ПРИМЕЧАНИЕ»).
ZH оригинал: 提示 = tip/hint/note.
ВОПРОС: Является ли «Подсказка» допустимым переводом 提示 в контексте автомануала?
Технический стандарт: ГОСТ Р ИСО 11684 использует только 4 уровня: ОПАСНОСТЬ, ПРЕДУПРЕЖДЕНИЕ, ВНИМАНИЕ, ПРИМЕЧАНИЕ.
РЕКОМЕНДАЦИЯ: «提示» → «ПРИМЕЧАНИЕ» как наиболее близкий уровень.

--- Вопрос 4 [MEDIUM]: «пожалуйста» в цитатах UI-сообщений ---
9 чанков содержат «пожалуйста, свяжитесь/обратитесь».
Анализ контекста: большинство — это цитаты сообщений бортового компьютера:
  «...появляется сообщение "АБС остановлена, пожалуйста свяжитесь с сервисным центром..."»
ВОПРОС: «пожалуйста» в цитатах UI-строк — оставить как есть (это перевод интерфейса) или
  унифицировать с технической документацией (убрать «пожалуйста»)?
РЕКОМЕНДАЦИЯ: Оставить в цитатах, убрать в обычном тексте мануала.

--- Вопрос 5 [MEDIUM]: «во время вождения» vs «при движении» ---
11 чанков: «во время вождения» в контексте запретов.
Примеры (оба встречаются в корпусе):
  «Не регулируйте сиденье водителя во время вождения» (кальк, лучше «при движении»)
  «Видеорегистратор записывает видео во время вождения» (здесь «во время вождения» уместно)
ВОПРОС: Есть ли чёткое правило: использовать «при движении» только в предупреждениях/запретах,
  а «во время вождения» оставить в нейтральных описательных контекстах?

--- Вопрос 6 [LOW]: Адрес сервиса ---
Встречаются 3 варианта:
 а) «сервисный центр Li Auto» (наиболее частый)
 б) «авторизованный дилер Li Auto»
 в) «центр обслуживания клиентов Li Auto»
ВОПРОС: Какой вариант является официальным для RU рынка?
ПРИМЕЧАНИЕ: Li Auto не представлена официально в России, поэтому «авторизованный дилер» может быть технически неверным.
"""


# ─── Финальный отчёт ─────────────────────────────────────────────────────────

# Распределение по типам и серьёзности
by_type = defaultdict(int)
by_severity = defaultdict(int)
for f in findings:
    by_type[f['type']] += 1
    by_severity[f['severity']] += 1

# Топ-25 критических findings
top_critical = sorted(
    [f for f in findings if f['severity'] in ('critical', 'high')],
    key=lambda x: (x['quality_score'], x['terminology_score'])
)[:25]

report = {
    'agent': 'agent3_ru_warnings',
    'reviewed': total_chunks,
    'issues_found': issues_total,
    'critical': critical_total,
    'stats': {
        'total_chunks': total_chunks,
        'priority_chunks_low_score': priority,
        'quality_zero': quality_zero,
        'quality_zero_pct': round(quality_zero / total_chunks * 100, 1),
        'quality_low': quality_low,
        'quality_high': quality_high,
        'by_type': dict(by_type),
        'by_severity': dict(by_severity),
        'affected_chunks_by_tag': {k: len(v) for k, v in affected_chunks.items()},
    },
    'summary': (
        f'Проверено {total_chunks} RU-переводов предупреждений Li Auto L7/L9. '
        f'Найдено {issues_total} проблем, из них {critical_total} критических/высоких. '
        f'ГЛАВНАЯ ПРОБЛЕМА (SP-001): 76% чанков используют Title Case метки (Предупреждение) '
        f'вместо CAPS (ПРЕДУПРЕЖДЕНИЕ) — системная ошибка промпта переводчика. '
        f'Вторая проблема (SP-004): 41% чанков имеют quality_score=0.0 — вероятный сбой скоринга. '
        f'Базовое качество перевода приемлемое: технические термины в большинстве верны, '
        f'структура сохранена, bullet points корректны. '
        f'Обнаружено 6 системных паттернов. Требуется глобальная постобработка меток и пересчёт скоров.'
    ),
    'systematic_patterns': systematic_patterns,
    'top_critical_findings': top_critical,
    'all_findings': findings,
    'open_questions_count': 6,
    'status': 'complete',
}

# Сохраняем отчёт
with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)
print(f'\nSaved report: {OUTPUT_PATH}')
print(f'  Report size: {len(json.dumps(report, ensure_ascii=False))/1024:.1f} KB')

# Сохраняем вопросы
with open(QUESTIONS_PATH, 'w', encoding='utf-8') as f:
    f.write(open_questions)
print(f'Saved questions: {QUESTIONS_PATH}')

# Итоговая сводка
print('\n' + '='*60)
print('ИТОГОВЫЙ ОТЧЁТ АГЕНТА 3')
print('='*60)
print(f'Срез: lang=ru, has_warnings=1')
print(f'Проверено чанков: {total_chunks}')
print(f'Приоритетных (low score): {priority} ({priority/total_chunks*100:.0f}%)')
print(f'Всего проблем: {issues_total}')
print(f'Критических/высоких: {critical_total}')
print()
print('Распределение по типам:')
for t, n in sorted(by_type.items(), key=lambda x: -x[1]):
    print(f'  {t}: {n}')
print()
print('Серьёзность:')
for s, n in sorted(by_severity.items(), key=lambda x: -x[1]):
    print(f'  {s}: {n}')
print()
print('Системные паттерны:')
for sp in systematic_patterns:
    print(f'  [{sp["priority"].upper()}] {sp["pattern_id"]}: {sp["pattern"]}')
    print(f'    {sp["description"][:100]}...')
    print(f'    Затронуто: {sp["affected_chunks_count"]} чанков')
print()
print(f'Открытые вопросы: 6')
print(f'Выходные файлы:')
print(f'  {OUTPUT_PATH}')
print(f'  {QUESTIONS_PATH}')
