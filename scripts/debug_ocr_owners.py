#!/usr/bin/env python3
"""Test OCR on Owner's Manual images."""
import sys, io, os, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

MODEL_PATH = "C:/Users/BAZA/.cache/huggingface/hub/models--deepseek-ai--DeepSeek-OCR-2/snapshots/aaa02f3811945a91062062994c5c4a3f4c0af2b0"
IMG_DIR = "C:/Diagnostica-KB-Package/mineru-output/Lixiang L9 Руководство пользователя/auto/images"

# Pick images of various sizes
from PIL import Image
all_imgs = []
for fn in sorted(os.listdir(IMG_DIR)):
    fp = os.path.join(IMG_DIR, fn)
    sz = os.path.getsize(fp)
    with Image.open(fp) as img:
        w, h = img.size
    all_imgs.append((sz, fn, w, h))

# Sort by size descending, take top 8
all_imgs.sort(reverse=True)
test_imgs = [(fn, w, h, sz) for sz, fn, w, h in all_imgs[:8]]

print("Loading model...", flush=True)
from transformers import AutoTokenizer, AutoModel
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
model = AutoModel.from_pretrained(MODEL_PATH, trust_remote_code=True, torch_dtype='auto', device_map="cuda:0")
model.eval()
print("Loaded.", flush=True)

import tempfile
tmp = tempfile.mkdtemp(prefix='ocr_owners_')

for fn, w, h, sz in test_imgs:
    img_path = os.path.join(IMG_DIR, fn)
    t0 = time.time()
    try:
        result = model.infer(
            tokenizer=tokenizer,
            prompt="<image>\nFree OCR.",
            image_file=img_path,
            output_path=tmp,
            eval_mode=True,
            image_size=768,
            base_size=1024,
        )
        elapsed = time.time() - t0
        text = str(result).strip() if result else ''
        print(f"[{elapsed:.1f}s] {sz//1024}KB {w}x{h} {fn[:20]}... => {len(text)}ch: {repr(text[:200])}", flush=True)
    except Exception as e:
        print(f"ERROR {fn[:20]}...: {e}", flush=True)
