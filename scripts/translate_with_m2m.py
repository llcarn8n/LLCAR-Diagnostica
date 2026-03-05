#!/usr/bin/env python3
"""
translate_with_m2m.py
Translates remaining batches using local fine-tuned M2M model.
Handles: batch_184 (ZH→EN+RU), batch_206 (EN→RU + ZH→EN+RU), batch_207 (EN→RU + ZH→EN+RU)
"""
import io, sys, json, sqlite3, os
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import torch
from transformers import T5Tokenizer, M2M100ForConditionalGeneration

MODEL_NAME = "Petr117/m2m-diagnostica-automotive"
BATCH_DIR = "knowledge-base/translate_batches"
DB_PATH = "knowledge-base/kb.db"

# Language codes for the model
LANG_CODES = {"zh": "zh", "en": "en", "ru": "ru"}

print("Loading M2M tokenizer and model...", flush=True)
tokenizer = T5Tokenizer.from_pretrained(MODEL_NAME)
device = "cuda:0" if torch.cuda.is_available() else "cpu"
model = M2M100ForConditionalGeneration.from_pretrained(MODEL_NAME, torch_dtype=torch.float16 if device != "cpu" else torch.float32)
model = model.to(device)
model.eval()
print(f"Model loaded on {device}", flush=True)


def translate_text(text: str, src_lang: str, tgt_lang: str, max_new_tokens: int = 1024) -> str:
    if not text or not text.strip():
        return text

    # The model uses specific language prefix tokens
    prefix = f">>{tgt_lang}<< "
    input_text = prefix + text.strip()

    inputs = tokenizer(
        input_text,
        return_tensors="pt",
        max_length=2048,
        truncation=True,
        padding=True
    ).to(device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            num_beams=4,
            length_penalty=1.0,
            early_stopping=True,
        )

    result = tokenizer.decode(outputs[0], skip_special_tokens=True)
    # Remove any prefix artifacts
    for prefix_token in [f">>{tgt_lang}<< ", f">>{tgt_lang}<<"]:
        if result.startswith(prefix_token):
            result = result[len(prefix_token):]
    return result.strip()


def translate_chunk(text: str, src_lang: str, tgt_lang: str) -> str:
    """Translate long text in chunks to avoid token limits."""
    # Split by paragraphs/sections
    MAX_CHARS = 1000  # conservative limit

    if len(text) <= MAX_CHARS:
        return translate_text(text, src_lang, tgt_lang)

    # Split by double newlines
    paragraphs = text.split('\n\n')
    results = []
    current_chunk = []
    current_len = 0

    for para in paragraphs:
        if current_len + len(para) > MAX_CHARS and current_chunk:
            chunk_text = '\n\n'.join(current_chunk)
            translated = translate_text(chunk_text, src_lang, tgt_lang)
            results.append(translated)
            current_chunk = [para]
            current_len = len(para)
        else:
            current_chunk.append(para)
            current_len += len(para)

    if current_chunk:
        chunk_text = '\n\n'.join(current_chunk)
        translated = translate_text(chunk_text, src_lang, tgt_lang)
        results.append(translated)

    return '\n\n'.join(results)


def translate_title(title: str, src_lang: str, tgt_lang: str) -> str:
    if not title or title.strip() in ("www.carobook.com", ""):
        return title
    return translate_text(title, src_lang, tgt_lang, max_new_tokens=100)


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
    print("\n=== BATCH 206 ===", flush=True)
    out = []
    en_items = extract_complete_items(f"{BATCH_DIR}/batch_206_en_raw.txt")
    print(f"  {len(en_items)} complete EN items from en_raw.txt", flush=True)

    for item in en_items:
        cid = item["id"]
        en_title, en_content = item["title"], item["content"]
        out.append({"id": cid, "lang": "en", "title": en_title, "content": en_content})

        print(f"  EN→RU: {cid} [{en_title[:35]}] ({len(en_content)} chars)", flush=True)
        ru_title = translate_title(en_title, "en", "ru")
        ru_content = translate_chunk(en_content, "en", "ru")
        out.append({"id": cid, "lang": "ru", "title": ru_title, "content": ru_content})
        print(f"    ✓ {len(ru_content)} chars", flush=True)

    # Truncated item f6315ec3
    trunc_id = "li_auto_l9_zh_f6315ec3"
    chunk = get_chunk_from_db(trunc_id)
    if chunk:
        print(f"  ZH→EN: {trunc_id} ({len(chunk['content'])} chars)", flush=True)
        en_title = translate_title(chunk["title"], "zh", "en")
        en_content = translate_chunk(chunk["content"], "zh", "en")
        out.append({"id": trunc_id, "lang": "en", "title": en_title, "content": en_content})
        print(f"    ✓ EN {len(en_content)} chars", flush=True)

        print(f"  ZH→RU: {trunc_id}", flush=True)
        ru_title = translate_title(chunk["title"], "zh", "ru")
        ru_content = translate_chunk(chunk["content"], "zh", "ru")
        out.append({"id": trunc_id, "lang": "ru", "title": ru_title, "content": ru_content})
        print(f"    ✓ RU {len(ru_content)} chars", flush=True)

    out_path = f"{BATCH_DIR}/batch_206_out.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"  Saved {len(out)} records → {out_path}", flush=True)


def process_batch_207():
    print("\n=== BATCH 207 ===", flush=True)
    out = []
    en_items = extract_complete_items(f"{BATCH_DIR}/batch_207_en_raw.txt")
    print(f"  {len(en_items)} complete EN items from en_raw.txt", flush=True)

    for item in en_items:
        cid = item["id"]
        en_title, en_content = item["title"], item["content"]
        out.append({"id": cid, "lang": "en", "title": en_title, "content": en_content})

        print(f"  EN→RU: {cid} [{en_title[:35]}] ({len(en_content)} chars)", flush=True)
        ru_title = translate_title(en_title, "en", "ru")
        ru_content = translate_chunk(en_content, "en", "ru")
        out.append({"id": cid, "lang": "ru", "title": ru_title, "content": ru_content})
        print(f"    ✓ {len(ru_content)} chars", flush=True)

    # Truncated item facfd8d4
    trunc_id = "li_auto_l9_zh_facfd8d4"
    chunk = get_chunk_from_db(trunc_id)
    if chunk:
        print(f"  ZH→EN: {trunc_id} ({len(chunk['content'])} chars)", flush=True)
        en_title = translate_title(chunk["title"], "zh", "en")
        en_content = translate_chunk(chunk["content"], "zh", "en")
        out.append({"id": trunc_id, "lang": "en", "title": en_title, "content": en_content})
        print(f"    ✓ EN {len(en_content)} chars", flush=True)

        print(f"  ZH→RU: {trunc_id}", flush=True)
        ru_title = translate_title(chunk["title"], "zh", "ru")
        ru_content = translate_chunk(chunk["content"], "zh", "ru")
        out.append({"id": trunc_id, "lang": "ru", "title": ru_title, "content": ru_content})
        print(f"    ✓ RU {len(ru_content)} chars", flush=True)

    out_path = f"{BATCH_DIR}/batch_207_out.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"  Saved {len(out)} records → {out_path}", flush=True)


def process_batch_184():
    print("\n=== BATCH 184 ===", flush=True)
    out = []

    with open(f"{BATCH_DIR}/batch_184.json", encoding="utf-8") as f:
        items = json.load(f)
    print(f"  {len(items)} items to translate", flush=True)

    for item in items:
        cid = item["id"]
        zh_title, zh_content = item["title"], item["content"]

        print(f"  ZH→EN: {cid} [{zh_title[:35]}] ({len(zh_content)} chars)", flush=True)
        en_title = translate_title(zh_title, "zh", "en")
        en_content = translate_chunk(zh_content, "zh", "en")
        out.append({"id": cid, "lang": "en", "title": en_title, "content": en_content})
        print(f"    ✓ EN {len(en_content)} chars", flush=True)

        print(f"  ZH→RU: {cid}", flush=True)
        ru_title = translate_title(zh_title, "zh", "ru")
        ru_content = translate_chunk(zh_content, "zh", "ru")
        out.append({"id": cid, "lang": "ru", "title": ru_title, "content": ru_content})
        print(f"    ✓ RU {len(ru_content)} chars", flush=True)

    out_path = f"{BATCH_DIR}/batch_184_out.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"  Saved {len(out)} records → {out_path}", flush=True)


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

    print("\n=== DONE ===", flush=True)
    import glob
    count = len(glob.glob(f"{BATCH_DIR}/batch_*_out.json"))
    print(f"Total _out.json files: {count}/209", flush=True)
