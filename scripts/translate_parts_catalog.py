"""
Translate L9 parts catalog ZH→RU.
Only translates part names and section headers, keeps part numbers/IDs intact.
Uses MADLAD-400 CT2 int8 with glossary post-processing.
"""
import sys
import io
import json
import re
import time
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent
KB_DIR = BASE_DIR / "knowledge-base"
INPUT_PATH = KB_DIR / "manual-sections-l9-zh-parts.json"
OUTPUT_PATH = KB_DIR / "manual-sections-l9-ru-parts.json"
GLOSSARY_PATH = KB_DIR / "glossary-unified-trilingual.json"
MODEL_DIR = "C:/tmp/madlad-ct2"
BATCH_SIZE = 16


def load_glossary():
    """Load ZH→RU glossary."""
    glossary = {}
    if GLOSSARY_PATH.exists():
        with open(GLOSSARY_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        for term in data.get("terms", []):
            zh = term.get("zh", "").strip()
            ru = term.get("ru", "").strip()
            if zh and ru and len(zh) >= 2:
                glossary[zh] = ru
    return glossary


def extract_translatable_texts(data):
    """Extract all unique Chinese texts that need translation from parts catalog."""
    texts = set()
    sections = data.get("sections", [])

    for section in sections:
        content = section.get("content", "")

        # Extract section/subsystem headers from content
        # Pattern: Chinese text followed by newline, then 序号/热点ID/...
        lines = content.split("\n")
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # Skip pure numbers, part numbers, column headers like 序号/热点ID/零件号码/零件名称
            if re.match(r'^\d+$', line):
                continue
            if re.match(r'^[A-Z0-9][\w-]*$', line):
                continue
            if line in ('序号', '热点ID', '零件号码', '零件名称'):
                continue
            # Chinese text (section headers, part names)
            if re.search(r'[\u4e00-\u9fff]', line):
                texts.add(line)

        # Extract from structured tables
        for table in section.get("tables", []):
            for header in table.get("headers", []):
                if re.search(r'[\u4e00-\u9fff]', header):
                    texts.add(header)
            for row in table.get("rows", []):
                for cell in row:
                    if re.search(r'[\u4e00-\u9fff]', cell):
                        texts.add(cell)

    return list(texts)


def translate_batch_ct2(translator, sp, texts, batch_size=BATCH_SIZE):
    """Translate batch of texts ZH→RU."""
    results = {}
    texts_list = list(texts)

    for i in range(0, len(texts_list), batch_size):
        batch = texts_list[i:i + batch_size]
        all_tokens = []
        for text in batch:
            tokens = sp.Encode(f"<2ru> {text}", out_type=str)
            all_tokens.append(tokens)

        batch_results = translator.translate_batch(
            all_tokens,
            beam_size=4,
            max_decoding_length=128,
        )

        for text, r in zip(batch, batch_results):
            ru = sp.Decode(r.hypotheses[0]).strip()
            results[text] = ru

    return results


def apply_glossary(text, glossary):
    """Apply glossary replacements."""
    for zh_term in sorted(glossary.keys(), key=len, reverse=True):
        if zh_term in text:
            text = text.replace(zh_term, glossary[zh_term])
    return text


def apply_translations(data, translations, glossary):
    """Apply translations to the parts catalog."""
    sections = data.get("sections", [])

    for section in sections:
        content = section.get("content", "")
        if content:
            # Save original
            section["content_original_zh"] = content[:500]

            # Replace each Chinese text with its translation
            lines = content.split("\n")
            new_lines = []
            for line in lines:
                stripped = line.strip()
                if stripped in translations:
                    ru = translations[stripped]
                    # Apply glossary
                    ru = apply_glossary(ru, glossary)
                    new_lines.append(ru)
                else:
                    new_lines.append(line)
            section["content"] = "\n".join(new_lines)

        # Translate table contents
        for table in section.get("tables", []):
            headers = table.get("headers", [])
            for i, h in enumerate(headers):
                if h in translations:
                    headers[i] = translations[h]

            for row in table.get("rows", []):
                for i, cell in enumerate(row):
                    if cell in translations:
                        ru = translations[cell]
                        ru = apply_glossary(ru, glossary)
                        row[i] = ru

    return data


def main():
    print("=" * 60)
    print("Parts Catalog Translation (ZH→RU)")
    print("=" * 60)

    # Load input
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    sections = data.get("sections", [])
    print(f"Sections: {len(sections)}")

    # Extract unique texts
    print("\nExtracting translatable texts...")
    texts = extract_translatable_texts(data)
    print(f"Unique Chinese texts to translate: {len(texts)}")

    # Load glossary
    print("Loading glossary...")
    glossary = load_glossary()
    print(f"Glossary: {len(glossary)} terms")

    # Check if some texts already have glossary matches
    glossary_matched = 0
    translations = {}
    remaining = []
    for text in texts:
        if text in glossary:
            translations[text] = glossary[text]
            glossary_matched += 1
        else:
            remaining.append(text)
    print(f"Glossary direct matches: {glossary_matched}")
    print(f"Need NMT translation: {len(remaining)}")

    # Load MADLAD-400 CT2
    print(f"\nLoading MADLAD-400 CT2 from {MODEL_DIR}...")
    import ctranslate2
    import sentencepiece

    t0 = time.time()
    translator = ctranslate2.Translator(MODEL_DIR, device="cuda", compute_type="int8")
    sp = sentencepiece.SentencePieceProcessor()
    sp.Load(f"{MODEL_DIR}/spiece.model")
    print(f"Model ready in {time.time()-t0:.1f}s")

    # Translate
    print(f"\nTranslating {len(remaining)} texts (batch_size={BATCH_SIZE})...")
    t0 = time.time()
    nmt_translations = translate_batch_ct2(translator, sp, remaining)
    translations.update(nmt_translations)
    elapsed = time.time() - t0
    print(f"Translated in {elapsed:.1f}s ({len(remaining)/elapsed:.0f} texts/s)")

    # Apply translations
    print("\nApplying translations to catalog...")
    data = apply_translations(data, translations, glossary)

    # Update metadata
    data["language"] = "ru"
    data["title"] = data.get("title", "") + " (перевод)"
    data["translation"] = {
        "source_language": "zh",
        "target_language": "ru",
        "model": "madlad-400-ct2-int8",
        "date": str(time.strftime("%Y-%m-%d")),
        "unique_texts_translated": len(remaining),
        "glossary_matches": glossary_matched,
        "glossary_terms_available": len(glossary),
    }

    # Save
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\nSaved: {OUTPUT_PATH}")
    size_kb = OUTPUT_PATH.stat().st_size / 1024
    print(f"Size: {size_kb:.1f} KB")

    # Show samples
    print("\n" + "=" * 60)
    print("Sample translations:")
    print("=" * 60)
    for zh, ru in list(translations.items())[:30]:
        if re.search(r'[\u4e00-\u9fff]', zh):
            print(f"  ZH: {zh:40s} → RU: {ru}")


if __name__ == "__main__":
    main()
