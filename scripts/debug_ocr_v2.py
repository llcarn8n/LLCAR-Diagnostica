#!/usr/bin/env python3
"""Test DeepSeek-OCR-2 after 3 bug fixes:
1. Feature ordering: [global, sep, local] (was [local, global, sep])
2. repetition_penalty=1.3 + no_repeat_ngram_size=5
3. token_type_ids device fix in Qwen2Decoder2Encoder
"""
import sys, io, os, torch
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

MODEL_PATH = "C:/Users/BAZA/.cache/huggingface/hub/models--deepseek-ai--DeepSeek-OCR-2/snapshots/aaa02f3811945a91062062994c5c4a3f4c0af2b0"
IMG_DIR = "C:/Diagnostica-KB-Package/mineru-output/Lixiang L9 Руководство пользователя/auto/images"

# Test with the problematic 947x1236 image
TEST_IMG = os.path.join(IMG_DIR, "7a9df6c1a26d49137b39e1ff283b97f7e45f68775887bfa2a3e681dd31d76956.jpg")

from transformers import AutoTokenizer, AutoModel
print("Loading model...", flush=True)
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
model = AutoModel.from_pretrained(MODEL_PATH, trust_remote_code=True, torch_dtype='auto', device_map="cuda:0")
model.eval()

import tempfile
tmp = tempfile.mkdtemp()

print(f"\n=== Test: 947x1236 Owner's Manual image ===", flush=True)
result = model.infer(
    tokenizer=tokenizer,
    prompt="<image>\nFree OCR.",
    image_file=TEST_IMG,
    output_path=tmp,
    eval_mode=True,
    image_size=768,
    base_size=1024,
)
print(f"\nResult ({len(result) if result else 0} chars):", flush=True)
if result:
    print(repr(result[:500]), flush=True)
    if len(result) > 500:
        print(f"... ({len(result)} total chars)", flush=True)
else:
    print("(empty)", flush=True)

# Test a second image to see if results vary
print(f"\n=== Test 2: another image ===", flush=True)
# find a different large image
import glob
imgs = sorted(glob.glob(os.path.join(IMG_DIR, "*.jpg")), key=os.path.getsize, reverse=True)
TEST_IMG2 = imgs[1] if len(imgs) > 1 else imgs[0]
print(f"Image: {os.path.basename(TEST_IMG2)} ({os.path.getsize(TEST_IMG2)//1024}KB)", flush=True)

result2 = model.infer(
    tokenizer=tokenizer,
    prompt="<image>\nFree OCR.",
    image_file=TEST_IMG2,
    output_path=tmp,
    eval_mode=True,
    image_size=768,
    base_size=1024,
)
print(f"\nResult ({len(result2) if result2 else 0} chars):", flush=True)
if result2:
    print(repr(result2[:500]), flush=True)
else:
    print("(empty)", flush=True)
