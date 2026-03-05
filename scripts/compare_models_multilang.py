#!/usr/bin/env python3
"""
compare_models_multilang.py — Benchmark Base vs Round3/4/5/6 on each language pair.

Evaluates:  ZH->RU, ZH->EN, RU->EN, EN->RU
Extracts test samples from chunk_content (KB translations as reference).
"""
import json, sys, io, time, random, sqlite3
from pathlib import Path
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import torch
from transformers import M2M100ForConditionalGeneration, AutoTokenizer
import sacrebleu

DB_PATH          = "C:/Diagnostica-KB-Package/knowledge-base/kb.db"
BASE_MODEL       = "utrobinmv/m2m_translate_en_ru_zh_large_4096"
ROUND3           = "C:/tmp/m2m-finetune"
ROUND4           = "C:/tmp/m2m-finetune-r4/checkpoint-933"
ROUND5           = "C:/tmp/m2m-finetune-r5"
ROUND6           = "C:/tmp/m2m-finetune-r6"
SAMPLES_PER_PAIR = 20
OUTPUT_MD        = Path("C:/Diagnostica-KB-Package/logs/model_comparison_multilang_r6.md")

device = "cuda:1" if torch.cuda.is_available() else "cpu"
print(f"Device: {device}", flush=True)

# ---- Fetch test samples from chunk_content ----
def get_samples(db_path, src_lang, tgt_lang, n=20, seed=42):
    conn = sqlite3.connect(db_path)
    rows = conn.execute("""
        SELECT src.chunk_id, src.content, tgt.content
        FROM chunk_content src
        JOIN chunk_content tgt ON src.chunk_id = tgt.chunk_id
        JOIN chunks c ON c.id = src.chunk_id
        WHERE src.lang = ? AND tgt.lang = ?
          AND length(src.content) > 50
          AND length(tgt.content) > 50
        ORDER BY src.chunk_id
    """, (src_lang, tgt_lang)).fetchall()
    conn.close()
    random.seed(seed)
    sample = random.sample(rows, min(n, len(rows)))
    return [(r[1][:400], r[2][:400]) for r in sample]


def load_model_tok(repo_id):
    print(f"  Loading {repo_id} ...", flush=True)
    t0 = time.time()
    tok   = AutoTokenizer.from_pretrained(repo_id)
    model = M2M100ForConditionalGeneration.from_pretrained(
        repo_id, torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
    ).to(device)
    model.eval()
    print(f"  Loaded in {time.time()-t0:.1f}s", flush=True)
    return model, tok

LANG_CODES = {
    "zh": "zh",
    "ru": "ru",
    "en": "en",
    "ar": "ar",
    "es": "es",
}

def translate_batch(model, tok, texts, src_lang, tgt_lang, batch_size=8):
    results = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        prefixed = [f"translate to {tgt_lang}: {t}" for t in batch]
        enc = tok(prefixed, return_tensors="pt", padding=True, truncation=True,
                  max_length=512).to(device)
        with torch.no_grad():
            ids = model.generate(**enc, max_new_tokens=300, num_beams=4)
        results += [tok.decode(x, skip_special_tokens=True) for x in ids]
    return results


def bleu(hyps, refs):
    return round(sacrebleu.corpus_bleu(hyps, [refs]).score, 2)


def main():
    PAIRS = [
        ("zh", "ru", "ZH→RU"),
        ("zh", "en", "ZH→EN"),
        ("ru", "en", "RU→EN"),
        ("en", "ru", "EN→RU"),
    ]

    MODELS = [
        ("Base",   BASE_MODEL),
        ("Round3", ROUND3),
        ("Round4", ROUND4),
        ("Round5", ROUND5),
        ("Round6", ROUND6),
    ]

    print("\n=== Extracting test samples from KB ===", flush=True)
    pair_data = {}
    for src, tgt, label in PAIRS:
        samples = get_samples(DB_PATH, src, tgt, n=SAMPLES_PER_PAIR)
        pair_data[(src, tgt)] = (label, samples)
        print(f"  {label}: {len(samples)} samples", flush=True)

    results = {}

    for model_name, model_path in MODELS:
        print(f"\n{'='*50}", flush=True)
        print(f"Evaluating: {model_name} ({model_path})", flush=True)
        try:
            model, tok = load_model_tok(model_path)
        except Exception as e:
            print(f"  ERROR loading {model_name}: {e}", flush=True)
            results[model_name] = {}
            continue

        results[model_name] = {}
        for (src, tgt), (label, samples) in pair_data.items():
            if not samples:
                results[model_name][label] = None
                continue
            src_texts = [s[0] for s in samples]
            ref_texts = [s[1] for s in samples]

            t0 = time.time()
            hyps = translate_batch(model, tok, src_texts, src, tgt)
            elapsed = time.time() - t0
            score = bleu(hyps, ref_texts)
            results[model_name][label] = {"bleu": score, "time": elapsed,
                                          "hyps": hyps, "refs": ref_texts,
                                          "srcs": src_texts}
            print(f"  {label}: BLEU={score} ({elapsed:.1f}s)", flush=True)

        del model
        torch.cuda.empty_cache()

    # Build report
    model_names = [m[0] for m in MODELS if m[0] in results]
    print("\n\n=== RESULTS ===", flush=True)

    header_cols = " | ".join(f"{n} BLEU" for n in model_names)
    sep_cols    = " | ".join("----------" for _ in model_names)
    lines = [
        "# Model Comparison: Base vs Round3/4/5/6 (Multi-Language)\n",
        f"**Samples per pair**: {SAMPLES_PER_PAIR}  ",
        f"**Reference**: chunk_content KB translations  \n",
        "## BLEU Summary\n",
        f"| Language Pair | {header_cols} | vs Base |",
        f"|---------------|{sep_cols}|---------|",
    ]

    for (src, tgt), (label, _) in pair_data.items():
        base_r = results.get("Base", {}).get(label)
        base_b = base_r["bleu"] if base_r else 0.0
        best_b = max((results.get(n, {}).get(label) or {}).get("bleu", 0) for n in model_names if n != "Base")
        delta  = best_b - base_b

        col_vals = []
        for n in model_names:
            r = results.get(n, {}).get(label)
            col_vals.append(str(r["bleu"]) if r else "N/A")

        cols_str = " | ".join(col_vals)
        lines.append(f"| {label} | {cols_str} | {delta:+.2f} |")
        print(f"  {label}: Base={base_b} → best={best_b} ({delta:+.2f})", flush=True)

    # Sample details
    lines += ["", "## Sample Translations\n"]
    for (src, tgt), (label, _) in pair_data.items():
        lines.append(f"### {label}\n")
        # collect all model results for this pair
        model_results_for_pair = {n: results.get(n, {}).get(label) for n in model_names}
        any_result = next((r for r in model_results_for_pair.values() if r), None)
        if not any_result:
            continue
        n_samples = min(3, len(any_result["srcs"]))
        for i in range(n_samples):
            lines.append(f"**Source**: {any_result['srcs'][i][:200]}")
            lines.append("")
            lines.append(f"**Reference**: {any_result['refs'][i][:200]}")
            lines.append("")
            for n in model_names:
                r = model_results_for_pair.get(n)
                if r and r.get("hyps") and i < len(r["hyps"]):
                    lines.append(f"**{n}**: {r['hyps'][i][:200]}")
                    lines.append("")
            lines += ["---", ""]

    OUTPUT_MD.parent.mkdir(exist_ok=True)
    OUTPUT_MD.write_text("\n".join(lines), encoding='utf-8')
    print(f"\nReport saved: {OUTPUT_MD}", flush=True)


if __name__ == "__main__":
    main()
