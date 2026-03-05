#!/usr/bin/env python3
"""Test DeepSeek-OCR-2 on English-language images."""
import sys, io, os, torch
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

MODEL_PATH = "C:/Users/BAZA/.cache/huggingface/hub/models--deepseek-ai--DeepSeek-OCR-2/snapshots/aaa02f3811945a91062062994c5c4a3f4c0af2b0"
# English-language Configuration document images
IMG_DIR = "C:/Diagnostica-KB-Package/mineru-output/240322-Li-L9-Configuration/auto/images"

from transformers import AutoTokenizer, AutoModel
print("Loading model...", flush=True)
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
model = AutoModel.from_pretrained(MODEL_PATH, trust_remote_code=True, torch_dtype='auto', device_map="cuda:0")
model.eval()

import glob, tempfile

# Test on first 3 largest English images
imgs = sorted(glob.glob(IMG_DIR + "/*.jpg"), key=os.path.getsize, reverse=True)[:3]
tmp = tempfile.mkdtemp()

for i, img_path in enumerate(imgs):
    size_kb = os.path.getsize(img_path) // 1024
    from PIL import Image
    w, h = Image.open(img_path).size
    print(f"\n=== Image {i+1}: {os.path.basename(img_path)[:30]}... ({w}x{h}, {size_kb}KB) ===", flush=True)

    result = model.infer(
        tokenizer=tokenizer,
        prompt="<image>\nFree OCR.",
        image_file=img_path,
        output_path=tmp,
        eval_mode=True,
        image_size=768,
        base_size=1024,
    )
    print(f"Result ({len(result) if result else 0} chars): {repr(result[:400]) if result else '(empty)'}", flush=True)
