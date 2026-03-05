#!/usr/bin/env python3
"""Test different generation params for DeepSeek-OCR-2."""
import sys, io, os, torch
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

MODEL_PATH = "C:/Users/BAZA/.cache/huggingface/hub/models--deepseek-ai--DeepSeek-OCR-2/snapshots/aaa02f3811945a91062062994c5c4a3f4c0af2b0"
IMG_DIR = "C:/Diagnostica-KB-Package/mineru-output/Lixiang L9 Руководство пользователя/auto/images"
TEST_IMG = os.path.join(IMG_DIR, "7a9df6c1a26d49137b39e1ff283b97f7e45f68775887bfa2a3e681dd31d76956.jpg")

from transformers import AutoTokenizer, AutoModel
print("Loading model...", flush=True)
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
model = AutoModel.from_pretrained(MODEL_PATH, trust_remote_code=True, torch_dtype='auto', device_map="cuda:0")
model.eval()

import tempfile

# Test various parameter combinations
test_configs = [
    {"rep_pen": 1.1, "ngram": 10, "label": "rep=1.1 ngram=10"},
    {"rep_pen": 1.05, "ngram": 20, "label": "rep=1.05 ngram=20"},
    {"rep_pen": 1.15, "ngram": 5, "label": "rep=1.15 ngram=5"},
]

# Patch the generate call to test params
original_generate = model.generate
def make_patched_generate(rep_pen, ngram):
    def patched_generate(input_ids, **kwargs):
        kwargs['repetition_penalty'] = rep_pen
        kwargs['no_repeat_ngram_size'] = ngram
        return original_generate(input_ids, **kwargs)
    return patched_generate

for cfg in test_configs:
    tmp = tempfile.mkdtemp()
    model.generate = make_patched_generate(cfg["rep_pen"], cfg["ngram"])

    print(f"\n=== Config: {cfg['label']} ===", flush=True)
    try:
        result = model.infer(
            tokenizer=tokenizer,
            prompt="<image>\nFree OCR.",
            image_file=TEST_IMG,
            output_path=tmp,
            eval_mode=True,
            image_size=768,
            base_size=1024,
        )
        print(f"Result ({len(result) if result else 0} chars): {repr(result[:300]) if result else '(empty)'}", flush=True)
    except Exception as e:
        print(f"ERROR: {e}", flush=True)

model.generate = original_generate
