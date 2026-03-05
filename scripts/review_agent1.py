import sqlite3, json, sys, io, re, os
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ─── 1. Load glossary ────────────────────────────────────────────────────────
GLOSS_PATH = 'C:/Diagnostica-KB-Package/дополнительно/полный глоссарий/полный глоссарий/automotive-glossary-5lang.json'
with open(GLOSS_PATH, encoding='utf-8') as f:
    glossary_data = json.load(f)

cats = glossary_data.get('categories', {})
zh_to_en = {}
ru_to_en = {}
canonical_en = set()

for cat_key, cat_val in cats.items():
    terms = cat_val.get('terms', []) if isinstance(cat_val, dict) else []
    for t in terms:
        en = t.get('en', '').strip().lower()
        zh = t.get('zh', '').strip()
        ru = t.get('ru', '').strip().lower()
        if en:
            canonical_en.add(en)
        if zh and en:
            zh_to_en[zh] = t['en']
        if ru and en:
            ru_to_en[ru] = t['en']

print(f"Glossary loaded: {len(zh_to_en)} ZH->EN, {len(ru_to_en)} RU->EN, {len(canonical_en)} canonical EN terms")

# ─── 2. Load chunks from DB ──────────────────────────────────────────────────
conn = sqlite3.connect('C:/Diagnostica-KB-Package/knowledge-base/kb.db')
rows = conn.execute('''
    SELECT cc.chunk_id, cc.lang, cc.content, cc.quality_score, cc.terminology_score,
           c.source_language, c.title, c.has_procedures, c.has_warnings,
           tc.source_text
    FROM chunk_content cc
    JOIN chunks c ON c.id = cc.chunk_id
    LEFT JOIN translation_cache tc ON tc.target_lang = cc.lang
        AND tc.translated_text = cc.content
    WHERE cc.lang = 'en' AND cc.translated_by != 'original'
      AND c.has_warnings = 1
    ORDER BY cc.quality_score ASC, cc.terminology_score ASC
    LIMIT 587
''').fetchall()
conn.close()

print(f"Loaded {len(rows)} chunks from DB")

# ─── 3. Review criteria ──────────────────────────────────────────────────────

TERM_CHECKS = [
    (r'\bair bag\b', 'airbag'),
    (r'\bAir Bag\b', 'airbag'),
    (r'\bbrake liquid\b', 'brake fluid'),
    (r'\bbrake oil\b', 'brake fluid'),
    (r'\bcharging interface\b', 'charging port'),
    (r'\bcharging socket\b', 'charging port'),
    (r'\bcharge port\b', 'charging port'),
    (r'\bdriving motor\b', 'drive motor'),
    (r'\bsteering wheel machine\b', 'steering column'),
    (r'\bpower battery\b', 'high-voltage battery'),
    (r'\banti-lock braking(?!\s+system)\b', 'anti-lock braking system (ABS)'),
    (r'\bchild lock\b', 'child safety lock'),
    (r'\bchildren lock\b', 'child safety lock'),
    (r'\bchildproof lock\b', 'child safety lock'),
    (r'\bhigh voltage(?![-\s]battery|[-\s]system|[-\s]component)', 'high-voltage'),
]

LITERAL_ARTIFACTS = [
    (r'\bplease do not\b', 'do not'),
    (r'\bplease make sure\b', 'ensure'),
    (r'\bplease check\b', 'check'),
    (r'\bplease use\b', 'use'),
    (r'\bplease note\b', 'NOTE'),
    (r'\bplease ensure\b', 'ensure'),
    (r'\bplease be\b', 'be'),
    (r'\bplease avoid\b', 'avoid'),
    (r'\bit is strictly forbidden to\b', 'do not'),
    (r'\bstrictly forbidden to\b', 'do not'),
    (r'\bforbidden to\b', 'do not'),
    (r'\bprohibited to\b', 'do not'),
]

NON_IMPERATIVE_PATTERNS = [
    (r'\byou should\b', 'Use imperative: "ensure/check" instead of "you should"'),
    (r'\bone should\b', 'Use imperative form directly'),
    (r'\bit is necessary to\b', 'Use imperative: "ensure/verify"'),
    (r'\bit is required to\b', 'Use imperative: direct imperative'),
    (r'\bthe user should\b', 'Use imperative: direct imperative'),
    (r'\bthe driver should\b', 'Use imperative: direct imperative'),
    (r'\boperator should\b', 'Use imperative: direct imperative'),
    (r'\buser should\b', 'Use imperative: direct imperative'),
]


def check_warning_caps(content):
    issues = []
    # Find warning keywords used as labels but not in CAPS
    for m in re.finditer(r'(?m)^[ \t]*(warning|caution|danger|note|important)[ \t]*[:\n]', content, re.IGNORECASE):
        word = m.group(1)
        if word != word.upper():
            issues.append({
                'type': 'warning_caps',
                'fragment': content[max(0, m.start()-10):m.end()+40],
                'word': word
            })
    return issues


def check_literal_artifacts(content):
    issues = []
    for pattern, suggestion in LITERAL_ARTIFACTS:
        for m in re.finditer(pattern, content, re.IGNORECASE):
            issues.append({
                'type': 'literal_artifact',
                'fragment': content[max(0, m.start()-30):m.end()+50],
                'matched': m.group(0),
                'suggestion': suggestion
            })
    return issues


def check_terminology(content):
    issues = []
    for pattern, correct in TERM_CHECKS:
        for m in re.finditer(pattern, content, re.IGNORECASE):
            matched = m.group(0)
            if matched.lower().strip() != correct.lower().strip():
                issues.append({
                    'type': 'wrong_terminology',
                    'fragment': content[max(0, m.start()-30):m.end()+50],
                    'matched': matched,
                    'correct': correct
                })
    return issues


def check_completeness(content):
    issues = []
    stripped = content.strip()
    if len(stripped) < 5:
        issues.append({
            'type': 'incomplete',
            'fragment': repr(stripped),
            'reason': 'Content is nearly empty'
        })
        return issues
    last_char = stripped[-1]
    if last_char not in '.!?;:)\'"\\]}>':
        last_line = stripped.split('\n')[-1].strip()
        if len(last_line) > 40 and last_char not in '.!?;:)':
            issues.append({
                'type': 'incomplete',
                'fragment': stripped[-120:],
                'reason': f'Content ends abruptly (last char: {repr(last_char)})'
            })
    return issues


def check_imperative_mood(content):
    issues = []
    for pattern, msg in NON_IMPERATIVE_PATTERNS:
        for m in re.finditer(pattern, content, re.IGNORECASE):
            issues.append({
                'type': 'wrong_register',
                'fragment': content[max(0, m.start()-30):m.end()+60],
                'matched': m.group(0),
                'suggestion': msg
            })
    return issues


# ─── 4. Run review ────────────────────────────────────────────────────────────

findings = []
term_tracker = defaultdict(set)
reviewed_count = 0
priority_count = 0
sampled_count = 0

for i, row in enumerate(rows):
    (chunk_id, lang, content, quality_score, terminology_score,
     source_language, title, has_procedures, has_warnings, source_text) = row

    if content is None:
        content = ''

    is_priority = (quality_score is None or quality_score < 0.8 or
                   terminology_score is None or terminology_score < 0.7)
    is_sample = (i % 10 == 0)

    if not is_priority and not is_sample:
        continue

    reviewed_count += 1
    if is_priority:
        priority_count += 1
    else:
        sampled_count += 1

    src_fragment = (source_text[:200] if source_text else f'[source_lang={source_language}, no cache]')

    caps_issues = check_warning_caps(content)
    artifact_issues = check_literal_artifacts(content)
    term_issues = check_terminology(content)
    complete_issues = check_completeness(content)
    register_issues = check_imperative_mood(content)

    # Track terminology variants for consistency
    for pattern, canonical in TERM_CHECKS:
        for m in re.finditer(pattern, content, re.IGNORECASE):
            term_tracker[canonical].add(m.group(0).lower().strip())

    for issue in caps_issues:
        findings.append({
            'chunk_id': chunk_id,
            'issue_type': 'wrong_terminology',
            'severity': 'medium',
            'source_text_fragment': src_fragment,
            'current_translation': issue['fragment'][:200],
            'suggested_fix': f'Capitalize label: {issue["word"].upper()}',
            'reason': f'Warning keyword "{issue["word"]}" used as section label but not in CAPS'
        })

    for issue in artifact_issues:
        findings.append({
            'chunk_id': chunk_id,
            'issue_type': 'literal_artifact',
            'severity': 'high',
            'source_text_fragment': src_fragment,
            'current_translation': issue['fragment'][:200],
            'suggested_fix': f'Replace "{issue["matched"]}" with "{issue["suggestion"]}"',
            'reason': f'Literal translation artifact from ZH/RU: polite form not standard in EN automotive warnings'
        })

    for issue in term_issues:
        findings.append({
            'chunk_id': chunk_id,
            'issue_type': 'wrong_terminology',
            'severity': 'high',
            'source_text_fragment': src_fragment,
            'current_translation': issue['fragment'][:200],
            'suggested_fix': f'Replace "{issue["matched"]}" with glossary canonical: "{issue["correct"]}"',
            'reason': f'Term mismatch: "{issue["matched"]}" != glossary canonical "{issue["correct"]}"'
        })

    for issue in complete_issues:
        findings.append({
            'chunk_id': chunk_id,
            'issue_type': 'incomplete',
            'severity': 'high',
            'source_text_fragment': src_fragment,
            'current_translation': issue['fragment'][:200],
            'suggested_fix': 'Re-translate or verify completeness against source text',
            'reason': issue['reason']
        })

    for issue in register_issues:
        findings.append({
            'chunk_id': chunk_id,
            'issue_type': 'wrong_register',
            'severity': 'medium',
            'source_text_fragment': src_fragment,
            'current_translation': issue['fragment'][:200],
            'suggested_fix': issue['suggestion'],
            'reason': f'Non-imperative register: "{issue["matched"]}" in warning/instruction context'
        })

print(f"\nReview done: reviewed={reviewed_count}, findings={len(findings)}")

# ─── 5. Terminology inconsistencies ──────────────────────────────────────────
terminology_inconsistencies = []
for canonical, variants in term_tracker.items():
    if len(variants) > 1:
        terminology_inconsistencies.append({
            'canonical_term': canonical,
            'variants_found': sorted(variants),
            'recommendation': f'Standardize all variants to: "{canonical}"'
        })

# ─── 6. Severity counts ───────────────────────────────────────────────────────
high_count = sum(1 for f in findings if f['severity'] == 'high')
medium_count = sum(1 for f in findings if f['severity'] == 'medium')
low_count = sum(1 for f in findings if f['severity'] == 'low')

issue_type_counts = defaultdict(int)
for f in findings:
    issue_type_counts[f['issue_type']] += 1

# ─── 7. Summary ──────────────────────────────────────────────────────────────
summary = (
    f"Reviewed {reviewed_count} of 587 EN warning chunks "
    f"({priority_count} priority [quality<0.8 or term<0.7] + {sampled_count} sampled every-10th). "
    f"Found {len(findings)} issues: {high_count} HIGH, {medium_count} MEDIUM, {low_count} LOW. "
    f"By type: {dict(issue_type_counts)}. "
    f"Terminology inconsistencies across corpus: {len(terminology_inconsistencies)}."
)

# ─── 8. Save report ──────────────────────────────────────────────────────────
os.makedirs('C:/Diagnostica-KB-Package/docs/review', exist_ok=True)

report = {
    "agent": "agent1_en_warnings",
    "reviewed": reviewed_count,
    "total_in_scope": len(rows),
    "priority_reviewed": priority_count,
    "sampled_reviewed": sampled_count,
    "issues_found": len(findings),
    "critical": high_count,
    "medium": medium_count,
    "low": low_count,
    "issue_type_breakdown": dict(issue_type_counts),
    "summary": summary,
    "findings": findings,
    "terminology_inconsistencies": terminology_inconsistencies,
    "status": "complete"
}

with open('C:/Diagnostica-KB-Package/docs/review/agent1_en_warnings.json', 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print(f"Report saved: docs/review/agent1_en_warnings.json")
print(f"Summary: {summary}")

# ─── 9. Supervisor questions ──────────────────────────────────────────────────
questions_lines = [
    "AGENT1 OPEN QUESTIONS FOR SUPERVISOR",
    "=" * 60,
    "",
    "1. CAPS for NOTE in informal context:",
    "   Some chunks use 'Note:' (sentence case) in informational notes, not safety warnings.",
    "   Q: Should ALL instances of 'note' be capitalized (NOTE), or only formal safety labels?",
    "   Recommendation: Capitalize only when used as a standalone label preceding safety-relevant info.",
    "",
    "2. 'must not' vs 'do not':",
    "   Both forms appear in safety instructions.",
    "   Q: Is 'must not' acceptable for emphatic prohibition, or must all use 'do not'?",
    "   Recommendation: Allow 'must not'; flag only 'please do not' as literal artifact.",
    "",
    "3. 'high voltage' vs 'high-voltage':",
    "   Hyphenation varies: adjective form needs hyphen ('high-voltage system'),",
    "   predicate form does not ('voltage is high'). Current detection is approximate.",
    "   Q: Should we enforce hyphenation for all pre-nominal 'high voltage' occurrences?",
    "",
    "4. 'child safety lock' vs 'childproof lock':",
    "   Both appear in corpus. Q: Which is the approved Li Auto EN term?",
    "   Recommendation: 'child safety lock' (global standard).",
    "",
    "5. Zero-score chunks (quality_score=0.0, terminology_score=0.0):",
    "   Q: Are these failed translations or auto-generated placeholders?",
    "   If failed, they should be re-translated rather than reviewed.",
    "",
    "6. Missing source_text in translation_cache:",
    "   For chunks where source_text is NULL, source-to-translation comparison is impossible.",
    "   Q: Is source_text always expected, or only for batch-translated chunks?",
    "",
    "7. 'charging port' vs 'charging interface':",
    "   Li Auto official documents may use 'charging interface' as a product-specific term.",
    "   Q: Confirm which EN term Li Auto uses in their official EN documentation.",
]

with open('C:/Diagnostica-KB-Package/docs/review/agent1_questions.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(questions_lines))

print(f"Questions saved: docs/review/agent1_questions.txt")
