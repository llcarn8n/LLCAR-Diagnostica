#!/usr/bin/env python3
"""
compare_models.py — Compare Base vs Round 3 vs Round 4 M2M fine-tuned models.

Uses ZH->RU and ZH->EN pairs from training_pairs_tier1.jsonl (Claude reference).
Saves comparison to logs/model_comparison.md.
"""
import json, sys, io, time, random
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import torch
from transformers import M2M100ForConditionalGeneration, AutoTokenizer
import sacrebleu

BASE_MODEL = "utrobinmv/m2m_translate_en_ru_zh_large_4096"
ROUND3     = "C:/tmp/m2m-finetune"                    # Round 3 local
ROUND4     = "C:/tmp/m2m-finetune-r4/checkpoint-933"  # Round 4 local
ROUND5     = "C:/tmp/m2m-finetune-r5"                 # Round 5 local (best = epoch 2)

PAIRS_FILE = Path("C:/Diagnostica-KB-Package/knowledge-base/training_pairs_tier1.jsonl")
OUTPUT_MD  = Path("C:/Diagnostica-KB-Package/logs/model_comparison_r5.md")
N_SAMPLES  = 200  # per language pair

device = "cuda:1" if torch.cuda.is_available() else "cpu"
print(f"Device: {device}")


def load_model_and_tok(path):
    print(f"  Loading {path} ...")
    t0 = time.time()
    tok   = AutoTokenizer.from_pretrained(path)
    model = M2M100ForConditionalGeneration.from_pretrained(
        path, torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
    ).to(device)
    model.eval()
    print(f"  Loaded in {time.time()-t0:.1f}s")
    return model, tok


def translate_batch(model, tok, texts, tgt_lang, batch_size=16):
    results = []
    prefixed = [f"translate to {tgt_lang}: {t}" for t in texts]
    for i in range(0, len(prefixed), batch_size):
        batch = prefixed[i:i+batch_size]
        enc = tok(batch, return_tensors="pt", padding=True, truncation=True,
                  max_length=256).to(device)
        with torch.no_grad():
            ids = model.generate(**enc, max_new_tokens=128, num_beams=2)
        results += [tok.decode(x, skip_special_tokens=True) for x in ids]
        print(f"    {min(i+batch_size, len(prefixed))}/{len(prefixed)}", end='\r')
    print()
    return results


def corpus_bleu(hyps, refs):
    return round(sacrebleu.corpus_bleu(hyps, [refs]).score, 2)


def load_pairs(src_lang, tgt_lang, n):
    all_pairs = [json.loads(l) for l in PAIRS_FILE.read_text(encoding='utf-8').splitlines() if l.strip()]
    filtered = [p for p in all_pairs
                if p.get('source_lang') == src_lang
                and p.get('target_lang') == tgt_lang
                and p.get('source') and p.get('translation')]
    random.seed(42)
    sample = random.sample(filtered, min(n, len(filtered)))
    return [p['source'] for p in sample], [p['translation'] for p in sample]


def eval_pair(model, tok, srcs, refs, tgt_lang, label):
    t0 = time.time()
    hyps = translate_batch(model, tok, srcs, tgt_lang)
    elapsed = time.time() - t0
    score = corpus_bleu(hyps, refs)
    print(f"  {label}: BLEU={score}  ({elapsed:.1f}s)")
    return score, hyps, elapsed


def main():
    # Language pairs to evaluate
    test_pairs = [
        ("zh", "ru", "ZH->RU"),
        ("zh", "en", "ZH->EN"),
    ]

    results = {}  # {pair_label: {model_name: (bleu, hyps, time)}}
    sample_data = {}  # {pair_label: (srcs, refs)}

    for src_lang, tgt_lang, label in test_pairs:
        srcs, refs = load_pairs(src_lang, tgt_lang, N_SAMPLES)
        sample_data[label] = (srcs, refs)
        print(f"\n=== {label} ({len(srcs)} samples) ===")
        results[label] = {}

        models = [
            ("Base", BASE_MODEL),
            ("Round3", ROUND3),
            ("Round4", ROUND4),
            ("Round5", ROUND5),
        ]
        for name, path in models:
            print(f"\n-- {name} --")
            try:
                model, tok = load_model_and_tok(path)
                score, hyps, elapsed = eval_pair(model, tok, srcs, refs, tgt_lang, name)
                results[label][name] = (score, hyps, elapsed)
                del model
                torch.cuda.empty_cache()
            except Exception as e:
                print(f"  ERROR: {e}")
                results[label][name] = (0.0, [], 0)

    # Build report
    lines = ["# Model Comparison: Base vs Round3 vs Round4 vs Round5\n",
             f"**Samples per pair**: {N_SAMPLES}  ",
             f"**Reference**: Claude Haiku translations from KB  \n"]

    for label in results:
        srcs, refs = sample_data[label]
        r = results[label]
        lines += [f"\n## {label}\n",
                  "| Model | BLEU | Time (s) |",
                  "|-------|------|----------|"]
        base_bleu = r.get('Base', (0,))[0]
        for name in ['Base', 'Round3', 'Round4', 'Round5']:
            if name in r:
                b, _, t = r[name]
                delta = f" (+{b-base_bleu:.2f})" if name != 'Base' else ""
                lines.append(f"| {name} | {b}{delta} | {t:.1f} |")

        # 5 sample translations
        lines.append("\n### Samples\n")
        for i in range(min(5, len(srcs))):
            lines.append(f"**[{i+1}] SRC**: {srcs[i][:150]}")
            lines.append(f"**REF**: {refs[i][:150]}")
            for name in ['Base', 'Round3', 'Round4', 'Round5']:
                if name in r and r[name][1]:
                    lines.append(f"**{name}**: {r[name][1][i][:150]}")
            lines.append("")

    output = "\n".join(lines)
    OUTPUT_MD.write_text(output, encoding='utf-8')

    # Summary print
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    for label in results:
        print(f"\n{label}:")
        r = results[label]
        base_b = r.get('Base', (0,))[0]
        for name in ['Base', 'Round3', 'Round4', 'Round5']:
            if name in r:
                b = r[name][0]
                delta = f" ({b-base_b:+.2f})" if name != 'Base' else ""
                print(f"  {name:<10} BLEU={b}{delta}")
    print(f"\nReport: {OUTPUT_MD}")


if __name__ == "__main__":
    main()
