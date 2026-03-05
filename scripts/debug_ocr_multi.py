#!/usr/bin/env python3
"""Test OCR on multiple images to verify fix quality."""
import sys, io, os, time, torch, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

MODEL_PATH = "C:/Users/BAZA/.cache/huggingface/hub/models--deepseek-ai--DeepSeek-OCR-2/snapshots/aaa02f3811945a91062062994c5c4a3f4c0af2b0"
IMG_DIR = "C:/Diagnostica-KB-Package/mineru-output/240322-Li-L9-Configuration/auto/images"

# Pick a few images of different sizes
images = [
    "047df9faf583a9aafa47c8fc72c30fd0c22c446b960d8071255c0733331a6056.jpg",
    "0ab8640ab866a625bfdb6c2efc99802c700ac1f90aa9b835bb44ed30fcb83d0c.jpg",
    "3590133c502a4f3f8ed5978082f4f39911930a1546695c3202c456545949c29d.jpg",
    "7094f4bc995590220c2b924de8af353f959720f7f5c3fa9e3962ab866712694c.jpg",
    "c2c8699f66bf43ec94c50005bccad6cde9d8c199bfbb30f74b3352d41cd46eaa.jpg",
]

print("Loading model...", flush=True)
from transformers import AutoTokenizer, AutoModel
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
model = AutoModel.from_pretrained(MODEL_PATH, trust_remote_code=True, torch_dtype='auto', device_map="cuda:0")
model.eval()
print("Model loaded.", flush=True)

import tempfile
tmp = tempfile.mkdtemp(prefix='ocr_multi_')

for img_name in images:
    img_path = os.path.join(IMG_DIR, img_name)
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
        print(f"[{elapsed:.1f}s] {img_name[:20]}... => {len(text)}ch: {repr(text[:150])}", flush=True)
    except Exception as e:
        print(f"ERROR {img_name[:20]}...: {e}", flush=True)
        import traceback; traceback.print_exc()
