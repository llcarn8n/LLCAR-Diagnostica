"""
Translate glossary terms EN→ZH using MADLAD-400 CT2 int8.
Then cross-check against Chinese manual content.
"""
import sys
import io
import json
import re
import time
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import ctranslate2
import sentencepiece

GLOSSARY_PATH = Path(__file__).parent.parent / "knowledge-base" / "glossary-unified-trilingual.json"
ZH_MANUAL_PATH = Path(__file__).parent.parent / "knowledge-base" / "manual-sections-l9-zh.json"
MODEL_DIR = "C:/tmp/madlad-ct2"
BATCH_SIZE = 32


def clean_zh(text: str) -> str:
    """Clean MADLAD output: remove duplications and trailing punctuation."""
    text = text.strip()
    # Remove trailing periods
    text = text.rstrip('。.')
    # Remove exact duplication (e.g., "制动片 制动片" -> "制动片")
    parts = text.split()
    if len(parts) == 2 and parts[0] == parts[1]:
        text = parts[0]
    # Also check Chinese without spaces
    half = len(text) // 2
    if half > 1 and text[:half] == text[half:half*2]:
        text = text[:half]
    return text.strip()


def translate_batch(translator, sp, texts, target_lang="zh"):
    """Translate a batch of texts EN→ZH."""
    all_tokens = []
    for text in texts:
        tokens = sp.Encode(f"<2{target_lang}> {text}", out_type=str)
        all_tokens.append(tokens)

    results = translator.translate_batch(
        all_tokens,
        max_batch_size=BATCH_SIZE,
        beam_size=4,
        max_decoding_length=128
    )

    translations = []
    for r in results:
        zh = sp.Decode(r.hypotheses[0])
        zh = clean_zh(zh)
        translations.append(zh)

    return translations


def build_zh_index(zh_manual_path: Path) -> dict:
    """Build an index of Chinese terms from the manual for cross-checking."""
    if not zh_manual_path.exists():
        return {}

    with open(zh_manual_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    zh_text = ""
    sections = data if isinstance(data, list) else data.get('sections', [])
    for section in sections:
        title = section.get('title', '')
        content = section.get('content', '')
        zh_text += f" {title} {content}"

    return zh_text


def cross_check(term_en: str, translated_zh: str, zh_corpus: str) -> dict:
    """Check if the translated ZH term appears in the Chinese manual."""
    found = translated_zh in zh_corpus if zh_corpus else False
    return {
        'found_in_manual': found,
        'verified': found
    }


def main():
    print("=" * 60)
    print("Glossary EN→ZH Translation (MADLAD-400 CT2 int8)")
    print("=" * 60)

    # Load glossary
    with open(GLOSSARY_PATH, 'r', encoding='utf-8') as f:
        glossary = json.load(f)

    terms = glossary['terms']
    no_zh = [(i, t) for i, t in enumerate(terms) if not t['zh']]
    print(f"Total terms: {len(terms)}, need ZH: {len(no_zh)}")

    # Load translator
    print(f"\nLoading MADLAD-400 CT2 from {MODEL_DIR}...")
    t0 = time.time()
    translator = ctranslate2.Translator(MODEL_DIR, device='cuda', compute_type='int8')
    sp = sentencepiece.SentencePieceProcessor()
    sp.Load(f"{MODEL_DIR}/spiece.model")
    print(f"Model ready in {time.time()-t0:.1f}s")

    # Load ZH manual for cross-checking
    print("\nLoading ZH manual for cross-checking...")
    zh_corpus = build_zh_index(ZH_MANUAL_PATH)
    print(f"ZH corpus: {len(zh_corpus)} chars" if zh_corpus else "No ZH manual found")

    # Translate in batches
    print(f"\nTranslating {len(no_zh)} terms (batch size {BATCH_SIZE})...")
    t0 = time.time()
    translated = 0
    verified = 0

    for batch_start in range(0, len(no_zh), BATCH_SIZE):
        batch = no_zh[batch_start:batch_start + BATCH_SIZE]
        en_texts = [t['en'] for _, t in batch]

        zh_translations = translate_batch(translator, sp, en_texts)

        for (idx, term), zh in zip(batch, zh_translations):
            terms[idx]['zh'] = zh

            # Cross-check
            check = cross_check(term['en'], zh, zh_corpus)
            if check['verified']:
                verified += 1

            translated += 1

        pct = translated / len(no_zh) * 100
        elapsed = time.time() - t0
        rate = translated / elapsed if elapsed > 0 else 0
        print(f"  [{pct:5.1f}%] {translated}/{len(no_zh)} translated, "
              f"{verified} verified, {rate:.0f} terms/s")

    total_time = time.time() - t0
    print(f"\nTranslation complete in {total_time:.1f}s ({translated/total_time:.0f} terms/s)")
    print(f"  Translated: {translated}")
    print(f"  Verified in manual: {verified}")

    # Update stats
    glossary['stats']['with_zh'] = sum(1 for t in terms if t['zh'])
    glossary['stats']['machine_translated_zh'] = translated
    glossary['stats']['verified_zh'] = verified

    # Save
    with open(GLOSSARY_PATH, 'w', encoding='utf-8') as f:
        json.dump(glossary, f, ensure_ascii=False, indent=2)
    print(f"\nSaved updated glossary: {GLOSSARY_PATH}")

    # Show samples
    print("\n" + "=" * 60)
    print("Sample translations:")
    print("=" * 60)
    for _, t in no_zh[:25]:
        v = " [V]" if t['zh'] and t['zh'] in (zh_corpus or '') else ""
        print(f"  EN: {t['en']:35s} -> ZH: {t['zh']}{v}")


if __name__ == '__main__':
    main()
