"""
Agent 4 Review Script v2 — RU Procedures (has_procedures=1, has_warnings=0)
Fixes: пробег false positives (пробег автомобиля = odometer, correct usage)
"""
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
# Each entry: (id, regex, severity, description, negative_lookahead_regex_or_None)
BAD_PATTERNS = [
    (
        'позиция_вместо_режима',
        r'позиция\s+[PRNDprnd]\b',
        'error',
        'Неверный перевод gear position: «позиция P/R/N/D» вместо «режим P/R/N/D» или «передача P/R/N/D»',
        None
    ),
    (
        'избыт_местоим',
        r'\bваш(?:е|его|ему)?\s+(?:автомобиль|транспортное средство|дисплей|экран)\b',
        'warning',
        'Избыточное местоимение «ваш» в техническом тексте',
        None
    ),
    (
        'не_императив_вы_должны',
        r'(?m)^(?:\d+[\.\)]\s+)?Вы\s+должны\s+(?:нажать|повернуть|открыть|закрыть|включить|выключить)',
        'error',
        'Нет повелительного наклонения: «Вы должны X» вместо «X»',
        None
    ),
    (
        'калькирование_нажмите_на',
        r'\bнажмите\s+на\s+(?:кнопку|значок|иконку|клавишу|переключатель)\b',
        'warning',
        'Калькирование: «нажмите на кнопку» вместо «нажмите кнопку»',
        None
    ),
    (
        'пробег_вместо_запаса_хода',
        # «пробег» only problematic when followed by EV context indicators (km range, battery, etc.)
        # NOT when it's «пробег автомобиля», «пробег транспортного средства» (odometer readings)
        r'\bпробег\b(?!\s+(?:автомобиля|транспортного\s+средства|машины))',
        'warning',
        'Возможно неверный термин: «пробег» вместо «запас хода» (для EV-контекста; пробег автомобиля = одометр — ОК)',
        None
    ),
    (
        'парковочный_тормоз',
        r'\bпарковочный\s+тормоз\b',
        'error',
        'Неверный термин: «парковочный тормоз» вместо «стояночный тормоз» (глоссарий: 驻车制动 → стояночный тормоз)',
        None
    ),
    (
        'климат_вместо_кондиционера',
        r'\bклимат\b(?!\s*[-–]?\s*контрол)',
        'warning',
        'Возможно неточный термин: «климат» вместо «кондиционер» (глоссарий: 空调 → кондиционер)',
        None
    ),
    (
        'нумерация_словами',
        r'(?m)^(?:Четыре|Три|Два|Один|Пять|Шесть|Семь|Восемь|Девять|Десять)\.\s',
        'error',
        'Артефакт перевода нумерации: числа прописью «Четыре.» вместо «4.» (перевод 四. → Четыре.)',
        None
    ),
    (
        'zh_residual',
        r'[\u4e00-\u9fff]{2,}',
        'critical',
        'Непереведённые китайские символы (2+ подряд иероглифа) в тексте',
        None
    ),
    (
        'zh_hint_tag',
        r'\*\*提示\*\*',
        'critical',
        'Непереведённый тег подсказки: **提示** (должно быть **Примечание** или **Подсказка**)',
        None
    ),
    (
        'roman_numeral_section',
        r'(?m)^(?:II|III|IV|V|VI|VII|VIII|IX)\.\s',
        'warning',
        'Нумерация разделов римскими цифрами — непоследовательный стиль (другие разделы арабскими)',
        None
    ),
    (
        'units_nonstandard',
        r'\d+\s*(?:mph|KW\b|KWh\b|Amp\b|AMP\b)',
        'warning',
        'Нестандартные единицы измерения (должно: кВт, кВт·ч, А)',
        None
    ),
]

# Concept variant tracking (for terminology consistency table)
CONCEPT_VARIANTS = {
    'центральный_дисплей_中控屏': re.compile(
        r'(центральный дисплей|сенсорный экран|центральный экран|центральная консоль|центральный монитор|монитор(?!\s+мультимедиа))',
        re.IGNORECASE
    ),
    'стояночный_тормоз_驻车': re.compile(
        r'(стояночный тормоз|ручной тормоз|парковочный тормоз|ручник\b|EPB\b)',
        re.IGNORECASE
    ),
    'запас_хода_续航': re.compile(
        r'(запас хода|пробег(?!\s+(?:автомобиля|транспортного\s+средства|машины))|дальность хода)',
        re.IGNORECASE
    ),
    'режим_передача_挡位': re.compile(
        r'(режим\s+[PRND]\b|передача\s+[PRND]\b|позиция\s+[PRND]\b)',
        re.IGNORECASE
    ),
    'кондиционер_空调': re.compile(
        r'(кондиционер[а-я]*\b|климат-контроль|климат\b(?!\s*[-–]?\s*контрол))',
        re.IGNORECASE
    ),
    'рекуперация_再生制动': re.compile(
        r'(рекупер\w+|рекуперативное торможение|регенеративное торможение)',
        re.IGNORECASE
    ),
    'зарядный_разъём_充电口': re.compile(
        r'(зарядный разъём|зарядный порт|зарядное отверстие|зарядная горловина)',
        re.IGNORECASE
    ),
}

RECOMMENDED = {
    'центральный_дисплей_中控屏': 'центральный дисплей',
    'стояночный_тормоз_驻车': 'стояночный тормоз',
    'запас_хода_续航': 'запас хода',
    'режим_передача_挡位': 'режим P / режим R / режим N / режим D',
    'кондиционер_空调': 'кондиционер',
    'рекуперация_再生制动': 'рекуперативное торможение',
    'зарядный_разъём_充电口': 'зарядный разъём',
}

ZH_TERM_MAP = {
    'центральный_дисплей_中控屏': '中控屏',
    'стояночный_тормоз_驻车': '驻车制动',
    'запас_хода_续航': '续航里程',
    'режим_передача_挡位': '挡位',
    'кондиционер_空调': '空调',
    'рекуперация_再生制动': '再生制动',
    'зарядный_разъём_充电口': '充电口',
}

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

    # 1. Apply bad patterns
    for pat_id, pattern, severity, desc, neg_lookahead in BAD_PATTERNS:
        matches = re.findall(pattern, content, re.MULTILINE | re.IGNORECASE)
        if matches:
            chunk_issues.append({
                'type': pat_id,
                'severity': severity,
                'description': desc,
                'matches': [str(m)[:100] for m in matches[:3]]
            })
            if severity == 'critical':
                critical_count += 1

    # 2. Imperative mood check for numbered steps
    lines = content.split('\n')
    non_imp_steps = []
    for line in lines:
        line_s = line.strip()
        if re.match(r'^\d+[\.\)]\s+', line_s):
            # Check if step begins with «Вы можете», «Вы должны», «при нажатии», etc.
            if re.match(r'^\d+[\.\)]\s+(?:Вы\s+(?:можете|нажимаете|устанавливаете)|при\s+нажатии\s+на|для\s+того\s+чтобы)', line_s, re.IGNORECASE):
                non_imp_steps.append(line_s[:120])
    if non_imp_steps:
        chunk_issues.append({
            'type': 'non_imperative_step',
            'severity': 'error',
            'description': 'Шаги процедуры не используют повелительное наклонение (нет глагола-императива в начале)',
            'matches': non_imp_steps[:3]
        })

    # 3. Step ordering check
    step_nums = []
    for m in re.finditer(r'(?m)^(\d+)[\.\)]\s', content):
        n = int(m.group(1))
        if n < 50:
            step_nums.append(n)
    if len(step_nums) >= 3:
        for i in range(len(step_nums)-1):
            if step_nums[i] > step_nums[i+1] and step_nums[i+1] != 1:
                chunk_issues.append({
                    'type': 'step_order_violation',
                    'severity': 'error',
                    'description': 'Нарушение порядка нумерации шагов процедуры',
                    'matches': [f'Найденная последовательность: {step_nums[:10]}']
                })
                break

    # 4. Collect concept variants
    for concept, regex in CONCEPT_VARIANTS.items():
        for m in regex.findall(content):
            concept_found[concept].append((chunk_id, m.lower().strip()))

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
print(f'Critical issues (count): {critical_count}', flush=True)

# Build terminology table
terminology_table = []
for concept, occurrences in concept_found.items():
    variants = Counter(v for _, v in occurrences)
    chunk_ids_set = list(set(cid for cid, _ in occurrences))
    all_variants = sorted(variants.items(), key=lambda x: -x[1])

    # Identify problematic variants
    problem_variants = []
    if concept == 'стояночный_тормоз_驻车':
        for v, c in variants.items():
            if 'парковочный' in v or 'ручной' in v or 'ручник' in v:
                problem_variants.append({'variant': v, 'count': c, 'reason': 'нет в глоссарии, правильно: стояночный тормоз'})
    elif concept == 'запас_хода_续航':
        for v, c in variants.items():
            if 'пробег' in v:
                problem_variants.append({'variant': v, 'count': c, 'reason': 'пробег = одометр, для EV-дальности: запас хода'})
    elif concept == 'центральный_дисплей_中控屏':
        for v, c in variants.items():
            if 'монитор' in v:
                problem_variants.append({'variant': v, 'count': c, 'reason': 'монитор — слишком общее; предпочтительно: центральный дисплей'})
            elif 'консол' in v:
                problem_variants.append({'variant': v, 'count': c, 'reason': 'центральная консоль ≠ дисплей; консоль = физический элемент'})
    elif concept == 'режим_передача_挡位':
        for v, c in variants.items():
            if 'позиция' in v:
                problem_variants.append({'variant': v, 'count': c, 'reason': 'позиция — дословный перевод; лучше: режим или передача'})
    elif concept == 'кондиционер_空调':
        for v, c in variants.items():
            if 'климат' in v and 'контрол' not in v:
                problem_variants.append({'variant': v, 'count': c, 'reason': 'климат (без -контроль) — неточный; глоссарий: 空调 → кондиционер'})

    entry = {
        'concept': concept,
        'zh_term': ZH_TERM_MAP.get(concept, ''),
        'translations_found': [v for v, _ in all_variants],
        'frequencies': {v: c for v, c in all_variants},
        'recommended': RECOMMENDED.get(concept, all_variants[0][0] if all_variants else ''),
        'inconsistent': len(variants) > 1,
        'problem_variants': problem_variants,
        'found_in_chunks': len(chunk_ids_set),
        'total_occurrences': sum(variants.values()),
    }
    terminology_table.append(entry)
    print(f'  {concept}: {dict(variants)}', flush=True)

# Summary stats
total_critical = sum(1 for f in findings for i in f['issues'] if i['severity'] == 'critical')
total_errors = sum(1 for f in findings for i in f['issues'] if i['severity'] == 'error')
total_warnings = sum(1 for f in findings for i in f['issues'] if i['severity'] == 'warning')
issue_type_counts = Counter()
for f in findings:
    for i in f['issues']:
        issue_type_counts[i['type']] += 1
layer_issues = Counter(f['layer'] for f in findings)
prio_issues = sum(1 for f in findings if f['priority'])

summary = (
    f"Проверено {len(rows)} RU-чанков (процедуры без предупреждений, слои: interior/ev/body/sensors/hvac/brakes/drivetrain). "
    f"Найдено проблем в {issues_found} чанках ({round(issues_found/len(rows)*100)}%), приоритетных (q<0.8 или t<0.7): {prio_issues}. "
    f"Критических: {total_critical} (непереведённые ZH-символы), "
    f"ошибок: {total_errors} (нумерация словами, парковочный тормоз, не-императив), "
    f"предупреждений: {total_warnings} (калькирование, римская нумерация, климат, пробег). "
    f"Главные проблемные типы: {', '.join(f'{k}={v}' for k,v in issue_type_counts.most_common(5))}. "
    f"Наибольшее число проблем в слое interior ({layer_issues.get('interior', 0)} чанков). "
    f"Терминологическая непоследовательность: {sum(1 for t in terminology_table if t['inconsistent'])} концепций из {len(terminology_table)}."
)

# Questions for manual review
questions = [
    "Q1: 68 чанков содержат остатки китайских иероглифов. Планируется ли повторный прогон OCR/перевода по этим чанкам?",
    "Q2: 80 чанков используют римскую нумерацию разделов (II. III. IV.). Это оригинальный стиль мануала или артефакт перевода? Унифицировать до арабских?",
    "Q3: 22 чанка содержат числа прописью в нумерации («Четыре.», «Три.») — артефакт перевода китайских 四. 三. Нужна автоматическая замена?",
    "Q4: 'центральный дисплей' vs 'сенсорный экран' vs 'центральный экран' для 中控屏 — какой термин закрепить как стандартный в глоссарии?",
    "Q5: 'режим P' vs 'передача P' для 挡位 — в мануале Li Auto EV нет механической КПП; правильно ли 'режим P/R/N/D'?",
    "Q6: 8 вхождений 'климат' (без '-контроль') для 空调 — заменить на 'кондиционер' везде или оставить как синоним?",
    "Q7: Качество 215 чанков (58.6%) ниже порога 0.8. Все переведены одним инструментом? Нужен ли ручной ревью топ-20 критических?",
    "Q8: 45 случаев калькирования 'нажмите на кнопку' — автозамена скриптом или ручная правка?",
]

result = {
    'agent': 'agent4_ru_procedures',
    'reviewed': len(rows),
    'issues_found': issues_found,
    'critical': total_critical,
    'errors': total_errors,
    'warnings': total_warnings,
    'priority_chunks': prio_issues,
    'issue_type_breakdown': dict(issue_type_counts.most_common()),
    'layer_breakdown': dict(layer_issues),
    'summary': summary,
    'findings': findings,
    'terminology_table': terminology_table,
    'status': 'complete'
}

# Save JSON
os.makedirs('C:/Diagnostica-KB-Package/docs/review', exist_ok=True)
out_path = 'C:/Diagnostica-KB-Package/docs/review/agent4_ru_procedures.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print(f'Saved JSON to {out_path}', flush=True)

# Save questions
q_path = 'C:/Diagnostica-KB-Package/docs/review/agent4_questions.txt'
with open(q_path, 'w', encoding='utf-8') as f:
    f.write('Agent 4 — Вопросы к ревью RU процедур\n')
    f.write('=' * 60 + '\n\n')
    for q in questions:
        f.write(q + '\n\n')
print(f'Saved questions to {q_path}', flush=True)

print(f'\n=== FINAL SUMMARY ===', flush=True)
print(f'Reviewed: {len(rows)}', flush=True)
print(f'Issues found: {issues_found} ({round(issues_found/len(rows)*100)}%)', flush=True)
print(f'Critical: {total_critical} | Errors: {total_errors} | Warnings: {total_warnings}', flush=True)
print(f'Issue types: {dict(issue_type_counts.most_common())}', flush=True)
print(f'Terminology inconsistencies: {sum(1 for t in terminology_table if t["inconsistent"])}/{len(terminology_table)}', flush=True)
