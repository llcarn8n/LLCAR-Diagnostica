#!/usr/bin/env python3
"""
translate_remaining_batches.py
Translates remaining 3 batches (184, 206, 207) using Anthropic Claude API.
- batch_184: 10 items ZH→EN+RU
- batch_206: 5 items EN→RU + 1 item ZH→EN+RU (f6315ec3)
- batch_207: 8 items EN→RU + 1 item ZH→EN+RU (facfd8d4)
"""
import io, sys, json, sqlite3, os, re, time
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import anthropic

DB_PATH = "knowledge-base/kb.db"
BATCH_DIR = "knowledge-base/translate_batches"

client = anthropic.Anthropic()

SYSTEM_PROMPT = """You are an expert automotive technical translator for Li Auto (理想汽车) vehicles.
Translate the given text accurately, preserving:
- Technical terminology (exact part names, system names)
- Warning/caution/note labels
- Numbered lists and structure
- Chinese automotive terms should be translated consistently

Respond with ONLY the translated text, no explanations."""

def translate(text: str, src_lang: str, tgt_lang: str) -> str:
    lang_names = {"zh": "Chinese", "en": "English", "ru": "Russian"}
    prompt = f"Translate from {lang_names[src_lang]} to {lang_names[tgt_lang]}:\n\n{text}"

    for attempt in range(3):
        try:
            msg = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}]
            )
            return msg.content[0].text.strip()
        except Exception as e:
            print(f"  Attempt {attempt+1} failed: {e}")
            time.sleep(2 ** attempt)
    return ""


def translate_title(title: str, src_lang: str, tgt_lang: str) -> str:
    if not title or title.strip() in ("www.carobook.com",):
        return title
    return translate(title, src_lang, tgt_lang)


def extract_complete_items(filepath: str):
    with open(filepath, encoding="utf-8") as f:
        text = f.read()
    items = []
    decoder = json.JSONDecoder()
    pos = text.find('[') + 1
    while pos < len(text):
        while pos < len(text) and text[pos] in ' \n\r\t,':
            pos += 1
        if pos >= len(text) or text[pos] == ']':
            break
        try:
            obj, end = decoder.raw_decode(text, pos)
            items.append(obj)
            pos = end
        except json.JSONDecodeError:
            break
    return items


def get_chunk_from_db(chunk_id: str):
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute(
        "SELECT id, title, content, source_language FROM chunks WHERE id=?", (chunk_id,)
    ).fetchone()
    conn.close()
    if row:
        return {"id": row[0], "title": row[1], "content": row[2], "src_lang": row[3]}
    return None


def process_batch_206():
    print("\n=== BATCH 206 ===")
    out = []

    # 5 complete EN items from en_raw.txt
    en_items = extract_complete_items(f"{BATCH_DIR}/batch_206_en_raw.txt")
    print(f"  Found {len(en_items)} complete EN items")

    for item in en_items:
        chunk_id = item["id"]
        en_title = item["title"]
        en_content = item["content"]

        # Add EN record
        out.append({"id": chunk_id, "lang": "en", "title": en_title, "content": en_content})

        # Translate EN→RU
        print(f"  Translating EN→RU: {chunk_id} [{en_title[:40]}]")
        ru_title = translate_title(en_title, "en", "ru")
        ru_content = translate(en_content, "en", "ru")
        out.append({"id": chunk_id, "lang": "ru", "title": ru_title, "content": ru_content})
        print(f"    ✓ RU done ({len(ru_content)} chars)")

    # Truncated item f6315ec3 — translate from Chinese source
    trunc_id = "li_auto_l9_zh_f6315ec3"
    chunk = get_chunk_from_db(trunc_id)
    if chunk:
        print(f"  Translating ZH→EN: {trunc_id}")
        en_title = translate_title(chunk["title"], "zh", "en")
        en_content = translate(chunk["content"], "zh", "en")
        out.append({"id": trunc_id, "lang": "en", "title": en_title, "content": en_content})
        print(f"    ✓ EN done ({len(en_content)} chars)")

        print(f"  Translating ZH→RU: {trunc_id}")
        ru_title = translate_title(chunk["title"], "zh", "ru")
        ru_content = translate(chunk["content"], "zh", "ru")
        out.append({"id": trunc_id, "lang": "ru", "title": ru_title, "content": ru_content})
        print(f"    ✓ RU done ({len(ru_content)} chars)")

    out_path = f"{BATCH_DIR}/batch_206_out.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"  Saved {len(out)} records to {out_path}")
    return out


def process_batch_207():
    print("\n=== BATCH 207 ===")
    out = []

    en_items = extract_complete_items(f"{BATCH_DIR}/batch_207_en_raw.txt")
    print(f"  Found {len(en_items)} complete EN items")

    for item in en_items:
        chunk_id = item["id"]
        en_title = item["title"]
        en_content = item["content"]

        out.append({"id": chunk_id, "lang": "en", "title": en_title, "content": en_content})

        print(f"  Translating EN→RU: {chunk_id} [{en_title[:40]}]")
        ru_title = translate_title(en_title, "en", "ru")
        ru_content = translate(en_content, "en", "ru")
        out.append({"id": chunk_id, "lang": "ru", "title": ru_title, "content": ru_content})
        print(f"    ✓ RU done ({len(ru_content)} chars)")

    # Truncated item facfd8d4 — translate from Chinese
    trunc_id = "li_auto_l9_zh_facfd8d4"
    chunk = get_chunk_from_db(trunc_id)
    if chunk:
        print(f"  Translating ZH→EN: {trunc_id}")
        en_title = translate_title(chunk["title"], "zh", "en")
        en_content = translate(chunk["content"], "zh", "en")
        out.append({"id": trunc_id, "lang": "en", "title": en_title, "content": en_content})
        print(f"    ✓ EN done ({len(en_content)} chars)")

        print(f"  Translating ZH→RU: {trunc_id}")
        ru_title = translate_title(chunk["title"], "zh", "ru")
        ru_content = translate(chunk["content"], "zh", "ru")
        out.append({"id": trunc_id, "lang": "ru", "title": ru_title, "content": ru_content})
        print(f"    ✓ RU done ({len(ru_content)} chars)")

    out_path = f"{BATCH_DIR}/batch_207_out.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"  Saved {len(out)} records to {out_path}")
    return out


def process_batch_184():
    print("\n=== BATCH 184 ===")
    out = []

    with open("knowledge-base/translate_batches/batch_184.json", encoding="utf-8") as f:
        items = json.load(f)

    print(f"  Found {len(items)} items to translate")

    for item in items:
        chunk_id = item["id"]
        zh_title = item["title"]
        zh_content = item["content"]

        print(f"  ZH→EN: {chunk_id} [{zh_title[:40]}]")
        en_title = translate_title(zh_title, "zh", "en")
        en_content = translate(zh_content, "zh", "en")
        out.append({"id": chunk_id, "lang": "en", "title": en_title, "content": en_content})
        print(f"    ✓ EN ({len(en_content)} chars)")

        print(f"  ZH→RU: {chunk_id}")
        ru_title = translate_title(zh_title, "zh", "ru")
        ru_content = translate(zh_content, "zh", "ru")
        out.append({"id": chunk_id, "lang": "ru", "title": ru_title, "content": ru_content})
        print(f"    ✓ RU ({len(ru_content)} chars)")

    out_path = f"{BATCH_DIR}/batch_184_out.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"  Saved {len(out)} records to {out_path}")
    return out


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", choices=["184", "206", "207", "all"], default="all")
    args = parser.parse_args()

    if args.batch in ("206", "all"):
        process_batch_206()
    if args.batch in ("207", "all"):
        process_batch_207()
    if args.batch in ("184", "all"):
        process_batch_184()

    print("\n=== DONE ===")
    # Show final count
    import glob
    count = len(glob.glob(f"{BATCH_DIR}/batch_*_out.json"))
    print(f"Total _out.json files: {count}/209")
