#!/usr/bin/env python3
"""Deep OCR test: examine raw token output for large images."""
import sys, io, os, time, torch
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

MODEL_PATH = "C:/Users/BAZA/.cache/huggingface/hub/models--deepseek-ai--DeepSeek-OCR-2/snapshots/aaa02f3811945a91062062994c5c4a3f4c0af2b0"
# Use the LARGEST image (most likely to have text)
TEST_IMG = "C:/Diagnostica-KB-Package/mineru-output/240322-Li-L9-Configuration/auto/images/8e5b99b7f4b16f0f68d130296400b48afb22a10c26448d8e64669db7220906a9.jpg"

from transformers import AutoTokenizer, AutoModel
print("Loading...", flush=True)
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
model = AutoModel.from_pretrained(MODEL_PATH, trust_remote_code=True, torch_dtype='auto', device_map="cuda:0")
model.eval()
print("Loaded.", flush=True)

# Patch generate to capture raw output_ids before decoding
_orig_generate = model.generate
def _patched_generate(*args, **kwargs):
    output = _orig_generate(*args, **kwargs)
    new_tokens = output[0, args[0].shape[1]:]
    print(f"  raw new tokens: {new_tokens.tolist()}", flush=True)
    for tok_id in new_tokens.tolist():
        print(f"    id={tok_id} => {tokenizer.decode([tok_id])!r}", flush=True)
    return output
model.generate = _patched_generate

import tempfile
tmp = tempfile.mkdtemp(prefix='ocr_deep_')

print(f"\n=== Largest image (365KB, 2190x2914) ===", flush=True)
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
    print(f"RESULT: {repr(result[:500]) if result else '(empty)'}", flush=True)
except Exception as e:
    import traceback
    print(f"ERROR: {e}", flush=True)
    traceback.print_exc()

# Also test without no_repeat_ngram_size
print(f"\n=== Same image, no ngram filter ===", flush=True)
sys.path.insert(0, MODEL_PATH)
import torch.nn.functional as F

# Rebuild input manually
from transformers import AutoTokenizer
from modeling_deepseekocr2 import format_messages, text_encode, load_image, BasicImageTransform, dynamic_preprocess
import math
from PIL import ImageOps

img_path = TEST_IMG
prompt_str = "<image>\nFree OCR."
conversation = [
    {"role": "<|User|>", "content": prompt_str, "images": [img_path]},
    {"role": "<|Assistant|>", "content": ""},
]
prompt = format_messages(conversations=conversation, sft_format='deepseek', system_prompt='')
print(f"Formatted prompt: {repr(prompt)}", flush=True)
