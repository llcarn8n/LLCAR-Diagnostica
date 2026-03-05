#!/usr/bin/env python3
"""Engine B worker: PaddleOCR with lang=ru+ch combined.
Run with: ocr_env/Scripts/python.exe scripts/ocr_b_worker_fixed.py <json_image_list>
"""
import os, sys, io, json, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = 'True'

from pathlib import Path
from paddleocr import PaddleOCR

def extract(ocr, image_path):
    try:
        res = ocr.predict(str(image_path))
        lines = []
        for r in res:
            for txt, sc in zip(r.get('rec_texts', []), r.get('rec_scores', [])):
                if sc >= 0.4 and txt.strip():
                    lines.append(txt.strip())
        return '\n'.join(lines)
    except Exception as e:
        return ''

def resolve(p):
    path = Path(p)
    if path.exists(): return path
    path2 = Path('knowledge-base') / p
    if path2.exists(): return path2
    return None

images = json.loads(sys.argv[1])

print('Initializing PaddleOCR lang=ru (GPU 0)...', flush=True)
ocr_ru = PaddleOCR(lang='ru', use_textline_orientation=True, device='gpu:0',
                   text_det_thresh=0.3, text_det_box_thresh=0.5)
print('Initializing PaddleOCR lang=ch (GPU 0)...', flush=True)
ocr_ch = PaddleOCR(lang='ch', use_textline_orientation=True, device='gpu:0',
                   text_det_thresh=0.3, text_det_box_thresh=0.5)

results = {}
for i, img_path in enumerate(images):
    full = resolve(img_path)
    if full is None:
        results[img_path] = ''
        continue
    t0 = time.time()
    ru_text = extract(ocr_ru, full)
    ch_text = extract(ocr_ch, full)
    # Merge: use both, deduplicate
    ru_lines = set(ru_text.split('\n')) if ru_text else set()
    ch_lines = ch_text.split('\n') if ch_text else []
    extra = [l for l in ch_lines if l and l not in ru_lines]
    merged = ru_text + ('\n' + '\n'.join(extra) if extra else '') if ru_text else ch_text
    results[img_path] = merged.strip()
    elapsed = time.time() - t0
    print(f'  [{i+1}/{len(images)}] {elapsed:.1f}s ru={len(ru_text)}ch ch={len(ch_text)}ch merged={len(merged)}ch | {img_path[-35:]}', flush=True)

print(json.dumps(results, ensure_ascii=False))
