import sqlite3, json, sys, io, re, os
from collections import defaultdict, Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Load DB
conn = sqlite3.connect('C:/Diagnostica-KB-Package/knowledge-base/kb.db')
rows = conn.execute('''
    SELECT cc.chunk_id, cc.lang, cc.content, cc.quality_score, cc.terminology_score,
           c.source_language, c.title, c.layer, c.content_type
    FROM chunk_content cc
    JOIN chunks c ON c.id = cc.chunk_id
    WHERE cc.lang = 'ru' AND cc.translated_by != 'original'
      AND c.has_procedures = 1 AND c.has_warnings = 0
    ORDER BY cc.quality_score ASC
''').fetchall()
conn.close()
print(f'Loaded {len(rows)} rows', flush=True)

# Load glossary
gloss_path = 'C:/Diagnostica-KB-Package/дополнительно/полный глоссарий/полный глоссарий/automotive-glossary-5lang.json'
with open(gloss_path, 'r', encoding='utf-8') as f:
    gloss = json.load(f)
cats = gloss['categories']
zh_ru = {}
en_ru = {}
for cat_name, cat_data in cats.items():
    for term in cat_data.get('terms', []):
        zh = term.get('zh', '').strip()
        ru = term.get('ru', '').strip()
        en = term.get('en', '').strip()
        if zh and ru:
            zh_ru[zh] = ru
        if en and ru:
            en_ru[en] = ru

print(f'Glossary: {len(zh_ru)} zh->ru, {len(en_ru)} en->ru', flush=True)

# BAD translation patterns
BAD_PATTERNS = [
    ('позиция_режим', r'позиция\s+[PRNDprnd]\b', 'error', 'Неверный перевод gear position: «позиция P/R/N/D» вместо «режим P/R/N/D»'),
    ('избыт_местоим', r'\bваш(?:е|его|ему|его|его)?\s+(?:автомобиль|транспортное средство|дисплей|экран)\b', 'warning', 'Избыточное местоимение «ваш» в техническом тексте'),
    ('не_императив', r'(?m)^(?:\d+[\.\)]\s+)?Вы должны\s+(?:нажать|повернуть|открыть|закрыть|включить|выключить)', 'error', 'Нет повелительного наклонения: «Вы должны X» вместо «X»'),
    ('калькирование', r'\bнажмите\s+на\s+(?:кнопку|значок|иконку|клавишу|переключатель)\b', 'warning', 'Калькирование: «нажмите на кнопку» вместо «нажмите кнопку»'),
    ('пробег_вместо_зх', r'\bпробег\b(?!\s+(?:до|с|в\s+год))', 'warning', 'Возможно неверный термин: «пробег» вместо «запас хода» (для EV)'),
    ('парковка_тормоз', r'\bпарковочный\s+тормоз\b', 'error', 'Неверный термин: «парковочный тормоз» вместо «стояночный тормоз»'),
    ('климат_вместо_кондиц', r'\bклимат\b(?!\s*[-–]?\s*контрол)', 'warning', 'Возможно неточный термин: «климат» вместо «кондиционер»'),
    ('нумерация_словами', r'(?m)^(?:Четыре|Три|Два|Один|Пять|Шесть|Семь|Восемь|Девять|Десять)\.\s', 'error', 'Артефакт перевода: числа прописью «Четыре.» вместо «4.»'),
    ('zh_residual', r'[\u4e00-\u9fff]{2,}', 'critical', 'Непереведённые китайские символы'),
    ('zh_hint_tag', r'\*\*提示\*\*', 'critical', 'Непереведённый тег подсказки: **提示**'),
    ('roman_numeral', r'(?m)^(?:II|III|IV|V|VI|VII|VIII|IX)\.\s', 'warning', 'Нумерация римскими цифрами (непоследовательный стиль)'),
    ('units_nonstandard', r'\d+\s*(?:mph|KW\b|KWh\b|Amp\b|AMP\b)', 'warning', 'Нестандартные единицы измерения'),
]

# Concept variant tracking
CONCEPT_VARIANTS = {
    'центральный_дисплей_中控屏': re.compile(
        r'(центральный дисплей|сенсорный экран|центральный экран|монитор(?!\s+мультимедиа)|центральная консоль|центральный монитор)',
        re.IGNORECASE
    ),
    'стояночный_тормоз_驻车': re.compile(
        r'(стояночный тормоз|ручной тормоз|парковочный тормоз|ручник\b|EPB)',
        re.IGNORECASE
    ),
    'запас_хода_续航': re.compile(
        r'(запас хода|пробег(?!\s+(?:до|за|в\s+год))|дальность хода|км пробега|километровый ресурс)',
        re.IGNORECASE
    ),
    'режим_передача_挡位': re.compile(
        r'(режим\s+[PRND]\b|передача\s+[PRND]\b|позиция\s+[PRND]\b|режим\s+P\b|P[\- ]режим|режим\s+парковки|режим\s+заднего хода)',
        re.IGNORECASE
    ),
    'кондиционер_空调': re.compile(
        r'(кондиционер(?:а|у|ом|е)?\b|климат-контроль|система климата|климат\b|воздух кондиционирования)',
        re.IGNORECASE
    ),
    'рекуперация_再生制动': re.compile(
        r'(рекупер\w+|рекуперативное торможение|регенеративное торможение|торможение батареей)',
        re.IGNORECASE
    ),
    'зарядный_разъём_充电口': re.compile(
        r'(зарядный разъём|зарядный порт|разъём зарядки|порт зарядки|зарядное отверстие|зарядная горловина)',
        re.IGNORECASE
    ),
}

NON_IMPERATIVE_STEP = re.compile(
    r'(?m)^(\d+[\.\)]\s+)(?:Вы\s+(?:должны|можете|нажимаете|устанавливаете)|для того чтобы|при нажатии|при установке\s+автомобиля)',
    re.IGNORECASE
)

findings = []
issues_found = 0
critical_count = 0
concept_found = defaultdict(list)

for row in rows:
    chunk_id, lang, content, quality_score, terminology_score, source_lang, title, layer, content_type = row
    if not content:
        continue

    chunk_issues = []
    priority = (quality_score < 0.8) or (terminology_score < 0.7)

    # 1. Bad patterns
    for pat_id, pattern, severity, desc in BAD_PATTERNS:
        matches = re.findall(pattern, content, re.MULTILINE | re.IGNORECASE)
        if matches:
            chunk_issues.append({
                'type': pat_id,
                'severity': severity,
                'description': desc,
                'matches': [str(m)[:80] for m in matches[:3]]
            })
            if severity == 'critical':
                critical_count += 1

    # 2. Non-imperative numbered steps (additional check)
    ni_matches = NON_IMPERATIVE_STEP.findall(content)
    if ni_matches:
        chunk_issues.append({
            'type': 'non_imperative_step',
            'severity': 'error',
            'description': 'Шаги с «Вы должны/можете» вместо повелительного наклонения',
            'matches': [str(m)[:80] for m in ni_matches[:3]]
        })

    # 3. Step ordering check
    step_nums = [int(m) for m in re.findall(r'(?m)^(\d+)[\.\)]\s', content) if m.isdigit() and int(m) < 100]
    if len(step_nums) >= 3:
        for i in range(len(step_nums)-1):
            if step_nums[i] > step_nums[i+1] and step_nums[i+1] != 1:
                chunk_issues.append({
                    'type': 'step_order',
                    'severity': 'error',
                    'description': f'Нарушение порядка нумерации шагов',
                    'matches': [f'Последовательность: {step_nums}']
                })
                break

    # 4. Collect concept variants
    for concept, regex in CONCEPT_VARIANTS.items():
        for m in regex.findall(content):
            concept_found[concept].append((chunk_id, m.lower()))

    if chunk_issues:
        issues_found += 1
        findings.append({
            'chunk_id': chunk_id,
            'quality_score': round(float(quality_score), 3),
            'terminology_score': round(float(terminology_score), 3),
            'layer': layer or '',
            'title': (title or '')[:120],
            'priority': priority,
            'issues': chunk_issues,
            'content_preview': content[:400]
        })

print(f'Chunks with issues: {issues_found}', flush=True)
print(f'Critical issues: {critical_count}', flush=True)

# Build terminology table
terminology_table = []
for concept, occurrences in concept_found.items():
    variants = Counter(v for _, v in occurrences)
    chunk_ids = list(set(cid for cid, _ in occurrences))[:5]
    # Determine recommended
    zh_key_map = {
        'центральный_дисплей_中控屏': '中控屏',
        'стояночный_тормоз_驻车': '驻车制动',
        'запас_хода_续航': '续航里程',
        'режим_передача_挡位': '挡位',
        'кондиционер_空调': '空调',
        'рекуперация_再生制动': '再生制动',
        'зарядный_разъём_充电口': '充电口',
    }
    recommended_map = {
        'центральный_дисплей_中控屏': 'центральный дисплей',
        'стояночный_тормоз_驻车': 'стояночный тормоз',
        'запас_хода_续航': 'запас хода',
        'режим_передача_挡位': 'режим P/R/N/D',
        'кондиционер_空调': 'кондиционер',
        'рекуперация_再生制动': 'рекуперативное торможение',
        'зарядный_разъём_充电口': 'зарядный разъём',
    }
    all_variants = sorted(variants.items(), key=lambda x: -x[1])
    is_inconsistent = len(variants) > 1
    # Detect problem cases
    problem_variants = []
    if concept == 'стояночный_тормоз_驻车':
        for v, c in variants.items():
            if 'парковочный' in v or 'ручной' in v or 'ручник' in v:
                problem_variants.append(v)
    elif concept == 'запас_хода_续航':
        for v, c in variants.items():
            if 'пробег' in v:
                problem_variants.append(v)
    elif concept == 'центральный_дисплей_中控屏':
        for v, c in variants.items():
            if 'монитор' in v and 'мультимедиа' not in v:
                problem_variants.append(v)
    elif concept == 'режим_передача_挡位':
        for v, c in variants.items():
            if 'позиция' in v:
                problem_variants.append(v)

    entry = {
        'concept': concept,
        'zh_term': zh_key_map.get(concept, ''),
        'translations_found': [v for v, _ in all_variants],
        'frequencies': {v: c for v, c in all_variants},
        'recommended': recommended_map.get(concept, all_variants[0][0] if all_variants else ''),
        'inconsistent': is_inconsistent,
        'problem_variants': problem_variants,
        'found_in_chunks': len(chunk_ids),
        'total_occurrences': sum(variants.values()),
    }
    terminology_table.append(entry)
    print(f'  {concept}: {dict(variants)}', flush=True)

# Build summary
total_critical = sum(1 for f in findings for i in f['issues'] if i['severity'] == 'critical')
total_errors = sum(1 for f in findings for i in f['issues'] if i['severity'] == 'error')
total_warnings = sum(1 for f in findings for i in f['issues'] if i['severity'] == 'warning')

# Top issue types
issue_type_counts = Counter()
for f in findings:
    for i in f['issues']:
        issue_type_counts[i['type']] += 1

# Layer breakdown
layer_issues = Counter(f['layer'] for f in findings)

summary = (
    f"Проверено 367 RU-чанков (категория: процедуры без предупреждений, слой: interior/ev/body/sensors/hvac/brakes/drivetrain). "
    f"Найдено проблем в {issues_found} чанках ({round(issues_found/367*100)}%). "
    f"Критических: {total_critical}, ошибок: {total_errors}, предупреждений: {total_warnings}. "
    f"Топ-3 проблемы: {issue_type_counts.most_common(3)}. "
    f"Слои с наибольшим числом проблем: {layer_issues.most_common(3)}. "
    f"Обнаружена терминологическая непоследовательность в {sum(1 for t in terminology_table if t['inconsistent'])} концепциях."
)

result = {
    'agent': 'agent4_ru_procedures',
    'reviewed': len(rows),
    'issues_found': issues_found,
    'critical': total_critical,
    'errors': total_errors,
    'warnings': total_warnings,
    'issue_type_breakdown': dict(issue_type_counts.most_common()),
    'layer_breakdown': dict(layer_issues),
    'summary': summary,
    'findings': findings,
    'terminology_table': terminology_table,
    'status': 'complete'
}

# Ensure output directory exists
os.makedirs('C:/Diagnostica-KB-Package/docs/review', exist_ok=True)

out_path = 'C:/Diagnostica-KB-Package/docs/review/agent4_ru_procedures.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f'\nSaved to {out_path}', flush=True)
print(f'Total: reviewed={len(rows)}, issues_found={issues_found}, critical={total_critical}, errors={total_errors}, warnings={total_warnings}', flush=True)
print(f'Issue type breakdown: {dict(issue_type_counts.most_common())}', flush=True)
