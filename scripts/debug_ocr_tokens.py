#!/usr/bin/env python3
"""Show raw generated tokens for one image."""
import sys, io, os, time, torch
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

MODEL_PATH = "C:/Users/BAZA/.cache/huggingface/hub/models--deepseek-ai--DeepSeek-OCR-2/snapshots/aaa02f3811945a91062062994c5c4a3f4c0af2b0"
IMG_DIR = "C:/Diagnostica-KB-Package/mineru-output/Lixiang L9 Руководство пользователя/auto/images"

# Use the smallest "large" image for speed
TEST_IMG = os.path.join(IMG_DIR, "7a9df6c1a26d49137b39e1ff283b97f7e45f68775887bfa2a3e681dd31d76956.jpg")  # ~167KB 947x1236

from transformers import AutoTokenizer, AutoModel
print("Loading...", flush=True)
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
model = AutoModel.from_pretrained(MODEL_PATH, trust_remote_code=True, torch_dtype='auto', device_map="cuda:0")
model.eval()

# Patch generate to show first 50 tokens
_orig_generate = model.generate
def _patched_generate(*args, **kwargs):
    # Limit to 50 new tokens for diagnosis
    kwargs['max_new_tokens'] = 50
    kwargs['no_repeat_ngram_size'] = 0  # Disable to see raw patterns
    output = _orig_generate(*args, **kwargs)
    new_tokens = output[0, args[0].shape[1]:].tolist()
    print(f"\n  Generated {len(new_tokens)} tokens:", flush=True)
    for i, tok_id in enumerate(new_tokens):
        print(f"    [{i+1}] id={tok_id:6d} => {tokenizer.decode([tok_id])!r}", flush=True)
    return output
model.generate = _patched_generate

import tempfile
tmp = tempfile.mkdtemp()

print(f"\nTest image: 167KB 947x1236", flush=True)
result = model.infer(
    tokenizer=tokenizer,
    prompt="<image>\nFree OCR.",
    image_file=TEST_IMG,
    output_path=tmp,
    eval_mode=True,
    image_size=768,
    base_size=1024,
)
print(f"\nFinal result: {repr(result[:300]) if result else '(empty)'}", flush=True)
