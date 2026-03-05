"""
Clean up MADLAD-400 ZH translation artifacts and cross-check against Chinese manual.

Artifacts fixed:
1. Exact word repetition: "吸收吸收吸收" → "吸收"
2. Word repetition with spaces: "制动片 制动片" → "制动片"
3. English leakage: "about 关于 about 关于" → "关于"
4. Parenthesized duplication: "(液晶显示器)液晶显示器" → "液晶显示器"
5. Mixed repetition patterns
"""
import sys
import io
import json
import re
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

GLOSSARY_PATH = Path(__file__).parent.parent / "knowledge-base" / "glossary-unified-trilingual.json"
ZH_MANUAL_PATH = Path(__file__).parent.parent / "knowledge-base" / "manual-sections-l9-zh.json"
ZH_PARTS_PATH = Path(__file__).parent.parent / "knowledge-base" / "manual-sections-l9-zh-parts.json"


def is_abbreviation(word: str) -> bool:
    """Check if word is an abbreviation/number that should be preserved in ZH."""
    # Common automotive abbreviations, numbers like 12V, ABS, ACC, etc.
    return bool(re.match(r'^[A-Z]{2,}$|^\d+[A-Za-z]*$|^[A-Za-z]/[A-Za-z]$', word))


def clean_zh(zh: str, en: str) -> str:
    """Clean MADLAD-400 ZH translation artifacts."""
    zh = zh.strip()
    if not zh:
        return zh

    # 1. Remove trailing punctuation
    zh = zh.rstrip('。.，,')

    # 2. Remove English leakage mixed with Chinese, but KEEP abbreviations/numbers
    # Pattern: "about 关于 about 关于 about" → "关于"
    # But keep: "ABS(防抱死制动系统)" or "12V蓄电池"
    if re.search(r'[a-zA-Z]', zh) and re.search(r'[\u4e00-\u9fff]', zh):
        # Check if English words are repeated (leakage pattern)
        en_words = re.findall(r'[a-zA-Z]+', zh)
        has_leakage = False
        if len(en_words) >= 2:
            word_counts = {}
            for w in en_words:
                wl = w.lower()
                word_counts[wl] = word_counts.get(wl, 0) + 1
            has_leakage = any(c >= 2 for c in word_counts.values())

        # Also detect pattern like "word 中文 word 中文" or "access 访问权限"
        if not has_leakage:
            # Single English word at the start followed by Chinese: "access 访问权限"
            m = re.match(r'^([a-zA-Z]+)\s+([\u4e00-\u9fff].+)$', zh)
            if m and not is_abbreviation(m.group(1)):
                en_word = m.group(1).lower()
                en_lower = en.lower().split('(')[0].strip().split(';')[0].strip()
                # Only strip if the English word matches the EN term
                if en_word == en_lower or en_word in en_lower.split():
                    zh = m.group(2)

        if has_leakage:
            # Extract Chinese + abbreviations, remove leaked English
            parts = re.split(r'\s+', zh)
            kept = []
            for p in parts:
                if re.search(r'[\u4e00-\u9fff]', p):
                    # Contains Chinese — keep
                    if p not in kept:
                        kept.append(p)
                elif is_abbreviation(p):
                    # Abbreviation — keep
                    if p not in kept:
                        kept.append(p)
                # else: skip leaked English word
            if kept:
                zh = ''.join(kept)

    # 3. Fix word repetition with spaces: "制动片 制动片 制动片" → "制动片"
    space_parts = zh.split()
    if len(space_parts) >= 2:
        unique = []
        for p in space_parts:
            if p not in unique:
                unique.append(p)
        if len(unique) < len(space_parts):
            zh = ' '.join(unique) if any(c.isascii() and c.isalpha() for c in ''.join(unique)) else ''.join(unique)

    # 4. Fix exact character repetition without spaces: "吸收吸收吸收" → "吸收"
    if len(zh) >= 4:
        for seg_len in range(2, len(zh) // 2 + 1):
            seg = zh[:seg_len]
            if len(zh) % seg_len == 0:
                repeats = len(zh) // seg_len
                if seg * repeats == zh and repeats >= 2:
                    zh = seg
                    break

    # 5. Fix parenthesized duplication: "(液晶显示器)液晶显示器" → "液晶显示器"
    m = re.match(r'^[（(](.+?)[）)](.+)$', zh)
    if m:
        inside = m.group(1)
        after = m.group(2)
        if inside == after:
            zh = inside

    # 6. Fix near-duplication where second half ≈ first half
    half = len(zh) // 2
    if half >= 2 and zh[:half] == zh[half:half*2]:
        zh = zh[:half]

    # 7. Clean up empty parentheses and trailing/leading junk
    zh = re.sub(r'\(\s*\)', '', zh)
    zh = re.sub(r'（\s*）', '', zh)
    zh = zh.strip(' ;；,，')

    # 8. If result is pure ASCII (no Chinese at all), it's a failed translation
    if zh and not re.search(r'[\u4e00-\u9fff]', zh):
        return ''  # Mark as empty — needs re-translation

    return zh.strip()


def load_zh_corpus(*paths):
    """Load Chinese text corpus from manual JSONs for cross-checking."""
    corpus = ""
    for path in paths:
        if not path.exists():
            continue
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        sections = data.get('sections', []) if isinstance(data, dict) else data
        for section in sections:
            title = section.get('title', '')
            content = section.get('content', '')
            corpus += f" {title} {content}"

    return corpus


def cross_check_term(zh: str, corpus: str) -> dict:
    """Check if a ZH term appears in the Chinese manual corpus."""
    if not zh or not corpus:
        return {'found': False, 'context': ''}

    found = zh in corpus
    context = ''
    if found:
        idx = corpus.index(zh)
        start = max(0, idx - 20)
        end = min(len(corpus), idx + len(zh) + 20)
        context = corpus[start:end].strip()

    return {'found': found, 'context': context}


def retranslate_terms(terms_to_fix):
    """Re-translate terms that were damaged by cleanup, using MADLAD-400 CT2."""
    try:
        import ctranslate2
        import sentencepiece
    except ImportError:
        print("  [SKIP] ctranslate2/sentencepiece not available, skipping re-translation")
        return {}

    MODEL_DIR = "C:/tmp/madlad-ct2"
    if not Path(MODEL_DIR).exists():
        print(f"  [SKIP] Model not found at {MODEL_DIR}")
        return {}

    print(f"  Loading MADLAD-400 CT2 for {len(terms_to_fix)} terms...")
    translator = ctranslate2.Translator(MODEL_DIR, device='cuda', compute_type='int8')
    sp = sentencepiece.SentencePieceProcessor()
    sp.Load(f"{MODEL_DIR}/spiece.model")

    results = {}
    en_texts = [t['en'] for t in terms_to_fix]

    all_tokens = []
    for text in en_texts:
        tokens = sp.Encode(f"<2zh> {text}", out_type=str)
        all_tokens.append(tokens)

    batch_results = translator.translate_batch(
        all_tokens, max_batch_size=32, beam_size=4, max_decoding_length=128
    )

    for term, r in zip(terms_to_fix, batch_results):
        zh = sp.Decode(r.hypotheses[0])
        results[term['en']] = zh.strip()

    return results


def main():
    print("=" * 60)
    print("ZH Translation Cleanup & Cross-Check (v2)")
    print("=" * 60)

    # Load glossary
    with open(GLOSSARY_PATH, 'r', encoding='utf-8') as f:
        glossary = json.load(f)

    terms = glossary['terms']
    print(f"Total terms: {len(terms)}")

    # Load Chinese corpus
    print("\nLoading Chinese manual corpus...")
    corpus = load_zh_corpus(ZH_MANUAL_PATH, ZH_PARTS_PATH)
    print(f"Corpus size: {len(corpus)} chars")

    # Phase 1: Clean artifacts
    print("\n--- Phase 1: Cleaning ZH artifacts ---")
    cleaned = 0
    emptied = 0
    samples_cleaned = []
    terms_need_retranslation = []

    for term in terms:
        zh = term.get('zh', '')
        if not zh:
            continue

        cleaned_zh = clean_zh(zh, term.get('en', ''))
        if cleaned_zh != zh:
            samples_cleaned.append((term['en'], zh, cleaned_zh))
            term['zh'] = cleaned_zh
            cleaned += 1
            if not cleaned_zh:
                emptied += 1
                terms_need_retranslation.append(term)

    print(f"Cleaned: {cleaned} terms")
    print(f"Emptied (need re-translation): {emptied} terms")
    if samples_cleaned:
        print("\nSample cleanups (first 30):")
        for en, old, new in samples_cleaned[:30]:
            new_display = new if new else "[EMPTY - needs re-translation]"
            print(f"  EN: {en:35s} | {old} → {new_display}")

    # Phase 1b: Re-translate terms that became empty after cleanup
    if terms_need_retranslation:
        print(f"\n--- Phase 1b: Re-translating {len(terms_need_retranslation)} damaged terms ---")
        retranslated = retranslate_terms(terms_need_retranslation)
        fixed = 0
        for term in terms_need_retranslation:
            if term['en'] in retranslated:
                new_zh = retranslated[term['en']]
                # Apply cleanup to new translation too
                new_zh = clean_zh(new_zh, term['en'])
                if new_zh:
                    term['zh'] = new_zh
                    fixed += 1
        print(f"Re-translated and fixed: {fixed}/{len(terms_need_retranslation)}")

    # Phase 2: Cross-check against manual (min 2 chars for reliable match)
    print("\n--- Phase 2: Cross-checking against ZH manual ---")
    verified = 0
    not_found = 0
    too_short = 0
    samples_verified = []
    samples_not_found = []

    for term in terms:
        zh = term.get('zh', '')
        if not zh:
            continue

        # Require minimum 2 Chinese chars for reliable cross-check
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', zh))
        if chinese_chars < 2:
            too_short += 1
            continue

        check = cross_check_term(zh, corpus)
        if check['found']:
            verified += 1
            if len(samples_verified) < 20:
                samples_verified.append((term['en'], zh, check['context']))
        else:
            not_found += 1
            if len(samples_not_found) < 30:
                samples_not_found.append((term['en'], zh))

    total_with_zh = sum(1 for t in terms if t.get('zh'))
    checked = verified + not_found
    print(f"\nResults:")
    print(f"  Total with ZH: {total_with_zh}")
    print(f"  Checked (≥2 chars): {checked}")
    print(f"  Too short to check: {too_short}")
    print(f"  Verified in manual: {verified} ({verified/checked*100:.1f}% of checked)")
    print(f"  Not found in manual: {not_found}")

    print("\nVerified terms (sample):")
    for en, zh, ctx in samples_verified[:15]:
        print(f"  [OK] EN: {en:30s} ZH: {zh:15s} | ...{ctx}...")

    print("\nNot found in manual (sample):")
    for en, zh in samples_not_found[:20]:
        print(f"  [??] EN: {en:30s} ZH: {zh}")

    # Update stats
    glossary['stats']['with_zh'] = total_with_zh
    glossary['stats']['verified_zh'] = verified
    glossary['stats']['cleaned_zh'] = cleaned
    glossary['stats']['retranslated'] = len(terms_need_retranslation)

    # Save
    with open(GLOSSARY_PATH, 'w', encoding='utf-8') as f:
        json.dump(glossary, f, ensure_ascii=False, indent=2)
    print(f"\nSaved cleaned glossary: {GLOSSARY_PATH}")


if __name__ == '__main__':
    main()
