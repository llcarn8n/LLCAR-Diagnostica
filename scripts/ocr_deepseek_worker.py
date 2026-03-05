#!/usr/bin/env python3
"""Engine D: DeepSeek-OCR-2 local model for OCR.

Run with: python.exe scripts/ocr_deepseek_worker.py <json_image_list>
(Uses main Python 3.14 env with torch+CUDA - NOT venv311 which has CPU-only torch)

Model: deepseek-ai/DeepSeek-OCR-2 (6.4GB, DeepSeekVL2 architecture)
API: model.infer(tokenizer, prompt, image_file, output_path, eval_mode=True)
"""
import os, sys, io, json, time, tempfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from pathlib import Path

MODEL_PATH = "C:/Users/BAZA/.cache/huggingface/hub/models--deepseek-ai--DeepSeek-OCR-2/snapshots/aaa02f3811945a91062062994c5c4a3f4c0af2b0"
OCR_PROMPT = "<image>\nFree OCR."


def resolve(p):
    path = Path(p)
    if path.exists(): return path
    path2 = Path('knowledge-base') / p
    if path2.exists(): return path2
    return None


def load_model():
    import torch
    from transformers import AutoModel, AutoTokenizer

    print(f'Loading DeepSeek-OCR-2 tokenizer...', flush=True)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)

    print(f'Loading DeepSeek-OCR-2 model (6.4GB)...', flush=True)
    model = AutoModel.from_pretrained(
        MODEL_PATH,
        trust_remote_code=True,
        torch_dtype='auto',
        device_map="cuda:0",
    )
    model.eval()
    print('DeepSeek-OCR-2 loaded on cuda:0', flush=True)
    return tokenizer, model


def ocr_one(tokenizer, model, image_path, tmp_dir):
    """Run DeepSeek-OCR-2 on one image using model.infer(). Returns extracted text."""
    try:
        result = model.infer(
            tokenizer=tokenizer,
            prompt=OCR_PROMPT,
            image_file=str(image_path),
            output_path=tmp_dir,
            eval_mode=True,
            image_size=768,
            base_size=1024,
        )
        if result is None:
            return ''
        text = str(result).strip()
        if text.upper() == 'EMPTY' or not text:
            return ''
        return text
    except Exception as e:
        print(f'  DeepSeek OCR error: {e}', flush=True)
        return ''


def main():
    images = json.loads(sys.argv[1])
    tokenizer, model = load_model()

    tmp_dir = tempfile.mkdtemp(prefix='deepseek_ocr_')
    results = {}

    for i, img_path in enumerate(images):
        full = resolve(img_path)
        if full is None:
            results[img_path] = ''
            print(f'  [{i+1}/{len(images)}] SKIP not found: {img_path[-40:]}', flush=True)
            continue

        t0 = time.time()
        text = ocr_one(tokenizer, model, full, tmp_dir)
        elapsed = time.time() - t0
        results[img_path] = text
        print(f'  [{i+1}/{len(images)}] {elapsed:.1f}s | {len(text)}ch | {img_path[-40:]}', flush=True)

    # Output JSON (last line of stdout)
    print(json.dumps(results, ensure_ascii=False))


if __name__ == '__main__':
    main()
