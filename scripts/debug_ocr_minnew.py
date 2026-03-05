#!/usr/bin/env python3
"""
debug_ocr_minnew.py — Force generation with min_new_tokens=100 to bypass early EOS.
Goal: see what the model actually "knows" about the image even if EOS wins early.
"""
import sys, io, os, warnings
warnings.filterwarnings('ignore')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

MODEL_PATH = "C:/Users/BAZA/.cache/huggingface/hub/models--deepseek-ai--DeepSeek-OCR-2/snapshots/aaa02f3811945a91062062994c5c4a3f4c0af2b0"
TEST_IMAGE = "C:/Diagnostica-KB-Package/logs/test_zh_page.jpg"

print("Loading tokenizer...", flush=True)
from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)

print("Loading model...", flush=True)
import torch
from transformers import AutoModel
model = AutoModel.from_pretrained(
    MODEL_PATH, trust_remote_code=True, torch_dtype='auto', device_map="cuda:0",
)
model.eval()

import tempfile
tmp = tempfile.mkdtemp(prefix='ocr_minnew_')

# ===== TEST A: min_new_tokens=100, grounding prompt =====
print("\n=== TEST A: min_new_tokens=100, repPenalty=1.3 ===", flush=True)

_orig_generate = model.generate
def _patched_generate_A(*args, **kwargs):
    kwargs['min_new_tokens'] = 100
    kwargs['max_new_tokens'] = 512
    kwargs['repetition_penalty'] = 1.3
    kwargs.pop('no_repeat_ngram_size', None)
    print(f"  generate() min_new_tokens=100 max_new_tokens=512", flush=True)
    return _orig_generate(*args, **kwargs)
model.generate = _patched_generate_A

try:
    result = model.infer(
        tokenizer=tokenizer,
        prompt="<image>\n<|grounding|>Convert the document to markdown. ",
        image_file=TEST_IMAGE,
        output_path=tmp,
        eval_mode=True,
        image_size=768,
        base_size=1024,
        crop_mode=True,
        save_results=False,
    )
    n = len(result) if result else 0
    print(f"  Result ({n} chars):", flush=True)
    if result:
        print(result[:1500], flush=True)
except Exception as e:
    print(f"  ERROR: {e}", flush=True)
    import traceback; traceback.print_exc()

model.generate = _orig_generate

# ===== TEST B: min_new_tokens=50, Chinese prompt =====
print("\n=== TEST B: min_new_tokens=50, Chinese OCR prompt ===", flush=True)

def _patched_generate_B(*args, **kwargs):
    kwargs['min_new_tokens'] = 50
    kwargs['max_new_tokens'] = 512
    kwargs['repetition_penalty'] = 1.3
    kwargs.pop('no_repeat_ngram_size', None)
    print(f"  generate() min_new_tokens=50 max_new_tokens=512", flush=True)
    return _orig_generate(*args, **kwargs)
model.generate = _patched_generate_B

try:
    result2 = model.infer(
        tokenizer=tokenizer,
        prompt="<image>\n请将此图片中的所有文字转换为markdown格式。",
        image_file=TEST_IMAGE,
        output_path=tmp,
        eval_mode=True,
        image_size=768,
        base_size=1024,
        crop_mode=True,
        save_results=False,
    )
    n2 = len(result2) if result2 else 0
    print(f"  Result ({n2} chars):", flush=True)
    if result2:
        print(result2[:1500], flush=True)
except Exception as e:
    print(f"  ERROR: {e}", flush=True)
    import traceback; traceback.print_exc()

model.generate = _orig_generate

# ===== TEST C: Patch EOS score — multiply EOS logit by 0.01 before sampling =====
print("\n=== TEST C: EOS suppressed (×0.01), grounding prompt, max=200 ===", flush=True)

# Patch lm_head to suppress EOS
_orig_lmh = model.lm_head.forward
def _patched_lmh_eos_suppress(x):
    logits = _orig_lmh(x)
    # Aggressively suppress EOS token
    logits[:, :, tokenizer.eos_token_id] = logits[:, :, tokenizer.eos_token_id] - 50.0
    return logits
model.lm_head.forward = _patched_lmh_eos_suppress

def _patched_generate_C(*args, **kwargs):
    kwargs['max_new_tokens'] = 200
    kwargs['repetition_penalty'] = 1.3
    kwargs.pop('no_repeat_ngram_size', None)
    return _orig_generate(*args, **kwargs)
model.generate = _patched_generate_C

try:
    result3 = model.infer(
        tokenizer=tokenizer,
        prompt="<image>\n<|grounding|>Convert the document to markdown. ",
        image_file=TEST_IMAGE,
        output_path=tmp,
        eval_mode=True,
        image_size=768,
        base_size=1024,
        crop_mode=True,
        save_results=False,
    )
    n3 = len(result3) if result3 else 0
    print(f"  Result ({n3} chars):", flush=True)
    if result3:
        print(result3[:2000], flush=True)
except Exception as e:
    print(f"  ERROR: {e}", flush=True)
    import traceback; traceback.print_exc()

model.lm_head.forward = _orig_lmh
model.generate = _orig_generate

print("\nDone.", flush=True)
