"""
Translate missing chunks to RU/EN using M2M100 on GPU.
Finds active chunks without RU or EN translations and translates them.

Usage:
    python scripts/_translate_missing.py [--device cuda:0] [--dry-run] [--lang ru,en]
"""

import sqlite3
import sys
import os
import time

DB_PATH = os.environ.get(
    "KB_DB_PATH",
    os.path.join(os.path.dirname(__file__), "..", "knowledge-base", "kb.db"),
)


def load_m2m(device="cuda:0"):
    """Load M2M100 translation model."""
    from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer

    # Try fine-tuned model first, fall back to base
    model_names = [
        "Petr117/m2m-diagnostica-automotive",
        "utrobinmv/m2m_translate_en_ru_zh_large_4096",
        "facebook/m2m100_418M",
    ]

    for model_name in model_names:
        try:
            print(f"Loading {model_name}...")
            tokenizer = M2M100Tokenizer.from_pretrained(model_name)
            model = M2M100ForConditionalGeneration.from_pretrained(model_name)
            model = model.to(device)
            model.eval()
            print(f"  Loaded on {device}")
            return model, tokenizer, model_name
        except Exception as e:
            print(f"  Failed: {e}")
            continue

    raise RuntimeError("No M2M model available")


# M2M language codes
LANG_MAP = {
    "zh": "zh",
    "ru": "ru",
    "en": "en",
    "ar": "ar",
    "es": "es",
}


def translate_text(model, tokenizer, text, src_lang, tgt_lang, device="cuda:0", max_length=512):
    """Translate text using M2M100."""
    import torch

    tokenizer.src_lang = LANG_MAP.get(src_lang, src_lang)

    # Truncate long texts
    if len(text) > 2000:
        text = text[:2000]

    inputs = tokenizer(text, return_tensors="pt", max_length=max_length, truncation=True)
    inputs = {k: v.to(device) for k, v in inputs.items()}

    tgt_lang_code = LANG_MAP.get(tgt_lang, tgt_lang)
    forced_bos = tokenizer.get_lang_id(tgt_lang_code)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            forced_bos_token_id=forced_bos,
            max_new_tokens=max_length,
            num_beams=4,
        )

    result = tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
    return result


def main():
    dry_run = "--dry-run" in sys.argv
    device = "cuda:0"
    target_langs = ["ru", "en"]

    for i, arg in enumerate(sys.argv):
        if arg == "--device" and i + 1 < len(sys.argv):
            device = sys.argv[i + 1]
        if arg == "--lang" and i + 1 < len(sys.argv):
            target_langs = sys.argv[i + 1].split(",")

    db_path = os.path.abspath(DB_PATH)
    print(f"DB: {db_path}")
    print(f"Target langs: {target_langs}")
    print(f"Device: {device}")
    if dry_run:
        print("=== DRY RUN ===")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Find active chunks missing translations
    missing = []
    for tgt_lang in target_langs:
        rows = cur.execute("""
            SELECT c.id, c.title, c.content, c.source_language
            FROM chunks c
            WHERE (c.is_current IS NULL OR c.is_current = 1)
            AND c.source_language != ?
            AND c.id NOT IN (SELECT chunk_id FROM chunk_content WHERE lang = ?)
            ORDER BY c.id
        """, (tgt_lang, tgt_lang)).fetchall()

        for r in rows:
            missing.append({
                "chunk_id": r["id"],
                "title": r["title"] or "",
                "content": r["content"] or "",
                "src_lang": r["source_language"],
                "tgt_lang": tgt_lang,
            })

    print(f"\nFound {len(missing)} missing translations")

    # Breakdown
    from collections import Counter
    lang_counts = Counter(m["tgt_lang"] for m in missing)
    for lang, cnt in lang_counts.most_common():
        print(f"  {lang}: {cnt}")

    if dry_run or not missing:
        conn.close()
        return

    # Load model
    model, tokenizer, model_name = load_m2m(device)

    # Translate
    t0 = time.time()
    translated = 0
    errors = 0

    for i, item in enumerate(missing):
        try:
            # Translate title
            title_tr = ""
            if item["title"]:
                title_tr = translate_text(
                    model, tokenizer, item["title"],
                    item["src_lang"], item["tgt_lang"], device, max_length=128
                )

            # Translate content
            content_tr = ""
            if item["content"]:
                content_tr = translate_text(
                    model, tokenizer, item["content"],
                    item["src_lang"], item["tgt_lang"], device, max_length=512
                )

            # Insert
            cur.execute("""
                INSERT OR REPLACE INTO chunk_content
                (chunk_id, lang, title, content, translated_by)
                VALUES (?, ?, ?, ?, ?)
            """, (
                item["chunk_id"], item["tgt_lang"],
                title_tr, content_tr, f"m2m100_{model_name.split('/')[-1]}"
            ))

            translated += 1

            if (i + 1) % 50 == 0:
                conn.commit()
                elapsed = time.time() - t0
                rate = translated / elapsed
                remaining = (len(missing) - i - 1) / rate if rate > 0 else 0
                print(f"  {i+1}/{len(missing)} ({translated} ok, {errors} err) "
                      f"[{rate:.1f}/s, ~{remaining/60:.0f}m left]")

        except Exception as e:
            errors += 1
            if errors <= 5:
                print(f"  Error on {item['chunk_id']}: {e}")

    conn.commit()
    elapsed = time.time() - t0

    print(f"\n=== Done! ===")
    print(f"Translated: {translated}/{len(missing)} ({errors} errors)")
    print(f"Time: {elapsed:.1f}s ({translated/elapsed:.1f} chunks/sec)")

    # Verify
    for tgt_lang in target_langs:
        cnt = cur.execute("""
            SELECT COUNT(*) FROM chunks c
            WHERE (c.is_current IS NULL OR c.is_current = 1)
            AND c.source_language != ?
            AND c.id NOT IN (SELECT chunk_id FROM chunk_content WHERE lang = ?)
        """, (tgt_lang, tgt_lang)).fetchone()[0]
        print(f"  Still missing {tgt_lang}: {cnt}")

    conn.close()


if __name__ == "__main__":
    main()
