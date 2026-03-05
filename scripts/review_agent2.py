import sqlite3, json, sys, io, re, collections

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

conn = sqlite3.connect('C:/Diagnostica-KB-Package/knowledge-base/kb.db')
rows = conn.execute("""
    SELECT cc.chunk_id, cc.lang, cc.content, cc.quality_score, cc.terminology_score,
           c.source_language, c.title, c.layer, c.content_type
    FROM chunk_content cc
    JOIN chunks c ON c.id = cc.chunk_id
    WHERE cc.lang = 'en' AND cc.translated_by != 'original'
      AND c.has_procedures = 1 AND c.has_warnings = 0
    ORDER BY cc.quality_score ASC
""").fetchall()
conn.close()
print(f'Loaded {len(rows)} rows')

# Build glossary lookup
with open('C:/Diagnostica-KB-Package/дополнительно/полный глоссарий/полный глоссарий/automotive-glossary-5lang.json', 'r', encoding='utf-8') as f:
    glos = json.load(f)

zh_to_en = {}
ru_to_en = {}
en_terms = set()
for cat in glos['categories'].values():
    for term in cat.get('terms', []):
        if 'zh' in term and 'en' in term:
            zh_to_en[term['zh'].strip().lower()] = term['en'].strip()
        if 'ru' in term and 'en' in term:
            ru_to_en[term['ru'].strip().lower()] = term['en'].strip()
        if 'en' in term:
            en_terms.add(term['en'].strip().lower())

print(f'ZH->EN: {len(zh_to_en)} terms, RU->EN: {len(ru_to_en)} terms, EN set: {len(en_terms)}')


def check_step_numbering(text):
    steps = re.findall(r'^(\d+)[.。]\s+(.+)', text, re.MULTILINE)
    if not steps:
        return None
    nums = [int(s[0]) for s in steps]
    if len(nums) < 2:
        return None
    expected = list(range(nums[0], nums[0]+len(nums)))
    if nums != expected:
        return f'Step numbers: expected {expected[:5]}, got {nums[:5]}'
    return None


def check_imperative(text):
    bad_patterns = [
        (r'\bYou (should|need to|must|have to)\b', 'you-should pattern'),
        (r'\bIt is (necessary|required|needed) to\b', 'it-is-necessary pattern'),
        (r'\bThe user (should|needs to|must)\b', 'the-user pattern'),
        (r'\bPlease\b', 'please artifact'),
    ]
    found = []
    for pat, desc in bad_patterns:
        if re.search(pat, text, re.IGNORECASE):
            m = re.search(pat, text, re.IGNORECASE)
            found.append((desc, m.group(0)))
    return found


def check_chinese_artifacts(text):
    patterns = [
        (r'please\s+(press|tap|turn|open|close|pull|push|check|ensure|make sure)', 'please+verb'),
        (r'operate\s+as\s+follows', 'operate as follows (literal ZH)'),
        (r'the\s+specific\s+(operational\s+)?steps\s+are\s+as\s+follows', 'specific steps as follows (literal ZH)'),
        (r'operation\s+steps\s+are\s+as\s+follows', 'operation steps as follows (literal ZH)'),
        (r'specific\s+operational\s+steps', 'specific operational steps (literal ZH)'),
        (r'\bkindy\b', 'kindy (typo)'),
    ]
    found = []
    for pat, desc in patterns:
        if re.search(pat, text, re.IGNORECASE):
            m = re.search(pat, text, re.IGNORECASE)
            found.append((desc, m.group(0)))
    return found


def check_units(text):
    issues_list = []
    if re.search(r'\d+\s*\u2103', text):  # ℃
        issues_list.append('℃ should be °C')
    zh_nums = re.findall(r'[\u4e00-\u9fff]{2,}', text)
    if zh_nums:
        issues_list.append(f'Chinese chars found: {zh_nums[:3]}')
    return issues_list


def check_term_consistency_inchunk(text):
    component_pairs = [
        (['center console', 'central console'], 'center console'),
        (['charging port', 'charge port'], 'charging port'),
        (['gear shift', 'gearshift', 'gear lever'], 'gear shift'),
        (['touchscreen', 'touch screen', 'touch-screen'], 'touchscreen'),
        (['rear view mirror', 'rearview mirror', 'rear-view mirror'], 'rearview mirror'),
        (['seatbelt', 'seat belt', 'safety belt'], 'seat belt'),
        (['parking brake', 'hand brake', 'handbrake', 'emergency brake'], 'parking brake'),
    ]
    problems = []
    for variants, canonical in component_pairs:
        found = [v for v in variants if re.search(r'\b' + re.escape(v) + r'\b', text, re.IGNORECASE)]
        if len(found) > 1:
            problems.append(f'Inconsistent: {found} (canonical: {canonical})')
    return problems


# Cross-chunk term tracking
term_cross = collections.defaultdict(lambda: collections.defaultdict(list))

issues = []
please_count = 0
url_artifact_count = 0
page_artifact_count = 0
literal_zh_count = 0
non_imperative_count = 0

for i, row in enumerate(rows):
    chunk_id, lang, content, quality, term_score, src_lang, title, layer, content_type = row

    is_priority = (quality < 0.8 or term_score < 0.7)
    is_sampled = (not is_priority and i % 8 == 0)

    if not (is_priority or is_sampled):
        continue

    chunk_issues = []

    # Step numbering
    step_issue = check_step_numbering(content)
    if step_issue:
        chunk_issues.append({'type': 'step_numbering', 'severity': 'medium', 'detail': step_issue})

    # Imperative check
    for desc, example in check_imperative(content):
        sev = 'medium' if 'please' in desc else 'low'
        chunk_issues.append({'type': 'non_imperative', 'severity': sev, 'detail': desc, 'example': example})
        if 'please' in desc.lower():
            please_count += 1
        non_imperative_count += 1

    # Chinese artifacts
    for desc, example in check_chinese_artifacts(content):
        chunk_issues.append({'type': 'chinese_artifact', 'severity': 'medium', 'detail': desc, 'example': example})
        if 'please' not in desc.lower():
            literal_zh_count += 1

    # Unit checks
    for u in check_units(content):
        chunk_issues.append({'type': 'unit_issue', 'severity': 'high', 'detail': u})

    # Term consistency within chunk
    for t in check_term_consistency_inchunk(content):
        chunk_issues.append({'type': 'term_inconsistency_inchunk', 'severity': 'medium', 'detail': t})

    # URL artifact
    if 'www.carobook.com' in content:
        chunk_issues.append({'type': 'url_artifact', 'severity': 'high', 'detail': 'www.carobook.com present in content'})
        url_artifact_count += 1

    # Page number artifacts
    page_nums = re.findall(r'\n\s*(\d{3,4})\s*\n', content)
    if page_nums:
        chunk_issues.append({'type': 'page_artifact', 'severity': 'medium', 'detail': f'Bare page numbers: {page_nums[:3]}'})
        page_artifact_count += 1

    # Cross-chunk term tracking
    variants_map = {
        'console': ['center console', 'central console'],
        'charging_port': ['charging port', 'charge port'],
        'touchscreen': ['touchscreen', 'touch screen'],
        'seatbelt': ['seatbelt', 'seat belt'],
        'parking_brake': ['parking brake', 'handbrake', 'hand brake'],
        'cruise_control': ['cruise control', 'adaptive cruise'],
        'gear_selector': ['gear shift', 'gear lever', 'gear selector', 'shift lever'],
    }
    for concept, variants in variants_map.items():
        for variant in variants:
            if re.search(r'\b' + re.escape(variant) + r'\b', content, re.IGNORECASE):
                term_cross[concept][variant.lower()].append(chunk_id)

    if chunk_issues:
        severity = 'critical' if (quality < 0.5 and len(chunk_issues) >= 2) or any(x['severity'] == 'high' for x in chunk_issues) else 'medium' if quality < 0.8 else 'low'
        issues.append({
            'chunk_id': chunk_id,
            'quality_score': quality,
            'terminology_score': term_score,
            'title': title,
            'severity': severity,
            'issues': chunk_issues,
            'content_preview': content[:300]
        })

# Build systematic patterns
systematic_patterns = []

# 1. URL artifacts
if url_artifact_count > 0:
    systematic_patterns.append({
        'pattern': 'url_artifact_in_content',
        'description': f'www.carobook.com present in {url_artifact_count} chunks — OCR artifact from source PDF header/footer',
        'affected_count': url_artifact_count,
        'severity': 'high',
        'fix': 'Strip www.carobook.com from content during OCR post-processing'
    })

# 2. Page number artifacts
if page_artifact_count > 0:
    systematic_patterns.append({
        'pattern': 'page_number_artifact',
        'description': f'Bare page numbers ({page_artifact_count} chunks) — PDF page numbers embedded in content, break procedure continuity',
        'affected_count': page_artifact_count,
        'severity': 'medium',
        'fix': 'Filter standalone 3-4 digit numbers on their own lines during chunking'
    })

# 3. Please artifacts
if please_count > 0:
    systematic_patterns.append({
        'pattern': 'please_artifact',
        'description': f'"Please" used {please_count} times — ZH manuals use 请 which is polite but EN technical manuals use imperative',
        'affected_count': please_count,
        'severity': 'medium',
        'fix': 'Post-process: strip "Please " prefix from imperative steps'
    })

# 4. Cross-chunk term inconsistency
cross_inconsistencies = {}
for concept, variants_dict in term_cross.items():
    if len(variants_dict) > 1:
        cross_inconsistencies[concept] = {v: len(chunks) for v, chunks in variants_dict.items()}

if cross_inconsistencies:
    systematic_patterns.append({
        'pattern': 'cross_chunk_term_inconsistency',
        'description': 'Same component referred to by multiple names across chunks',
        'affected_concepts': cross_inconsistencies,
        'severity': 'high',
        'fix': 'Apply glossary normalization pass: replace non-canonical variants with canonical forms'
    })

# 5. Literal ZH procedural headers
if literal_zh_count > 0:
    systematic_patterns.append({
        'pattern': 'literal_zh_procedural_headers',
        'description': f'{literal_zh_count} chunks with literal ZH procedural phrasing (e.g. "Specific operational steps are as follows", "Operate as follows")',
        'affected_count': literal_zh_count,
        'severity': 'medium',
        'fix': 'Replace with EN-native phrasing: "Procedure:", "Steps:", or simply start numbered list'
    })

# 6. Zero-score chunks analysis
zero_score = [r for r in rows if r[3] == 0.0 and r[4] == 0.0]
systematic_patterns.append({
    'pattern': 'zero_quality_score_chunks',
    'description': f'{len(zero_score)} chunks have quality_score=0 AND terminology_score=0 — likely scoring bug or untested translation path',
    'affected_count': len(zero_score),
    'severity': 'critical',
    'fix': 'Re-run scoring pipeline on these chunks; verify quality_score computation in build_kb.py'
})

# Summary
total_checked = sum(1 for i, r in enumerate(rows) if r[3] < 0.8 or r[4] < 0.7 or i % 8 == 0)
total_issues = len(issues)
critical_issues = sum(1 for x in issues if x['severity'] == 'critical')
medium_issues = sum(1 for x in issues if x['severity'] == 'medium')
low_issues = sum(1 for x in issues if x['severity'] == 'low')

# Issue type breakdown
issue_type_counts = collections.Counter()
for item in issues:
    for iss in item['issues']:
        issue_type_counts[iss['type']] += 1

summary = (
    f"Reviewed {total_checked} of 386 EN procedure chunks (152 priority low-score + sampled). "
    f"Found {total_issues} chunks with issues ({critical_issues} critical, {medium_issues} medium, {low_issues} low). "
    f"Primary problems: {url_artifact_count} URL artifacts, {page_artifact_count} page-number artifacts, "
    f"{please_count} 'please' insertions from ZH politeness register, "
    f"{literal_zh_count} literal ZH procedural headers. "
    f"Cross-chunk: {len(cross_inconsistencies)} concept terms inconsistently named. "
    f"CRITICAL: {len(zero_score)} chunks with quality_score=0.0 suggest scoring pipeline failure."
)

print('\n' + summary)
print(f'\nIssue type breakdown:')
for t, c in issue_type_counts.most_common():
    print(f'  {t}: {c}')
print(f'\nCross-chunk inconsistencies:')
for concept, variants in cross_inconsistencies.items():
    print(f'  {concept}: {variants}')

report = {
    "agent": "agent2_en_procedures",
    "reviewed": total_checked,
    "total_in_scope": 386,
    "issues_found": total_issues,
    "critical": critical_issues,
    "medium": medium_issues,
    "low": low_issues,
    "issue_type_breakdown": dict(issue_type_counts),
    "summary": summary,
    "findings": issues,
    "systematic_patterns": systematic_patterns,
    "status": "complete"
}

import os
os.makedirs('C:/Diagnostica-KB-Package/docs/review', exist_ok=True)
with open('C:/Diagnostica-KB-Package/docs/review/agent2_en_procedures.json', 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print('\nReport saved to docs/review/agent2_en_procedures.json')

# Also save questions file
questions = []
if cross_inconsistencies:
    for concept, variants in cross_inconsistencies.items():
        questions.append(f"Q: Term '{concept}' used as: {', '.join(f'{v}({c})' for v,c in variants.items())} — which is canonical?")

if len(zero_score) > 0:
    questions.append(f"Q: {len(zero_score)} chunks have quality_score=0.0 and terminology_score=0.0. Is this a scoring bug or were they not scored at all?")

questions.append("Q: Should 'please' be stripped from all procedural steps, or only from numbered steps?")
questions.append("Q: Should 'www.carobook.com' URL artifacts be stripped in build_kb.py or in a post-processing step?")
questions.append("Q: Are bare page numbers (e.g. 926, 3045) between sections intentional markers or OCR artifacts to strip?")

with open('C:/Diagnostica-KB-Package/docs/review/agent2_questions.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(questions))

print(f'Questions saved: {len(questions)} questions')
