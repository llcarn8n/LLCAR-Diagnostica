#!/usr/bin/env python3
"""
debug_ocr_hstrack.py — Track hidden state norms + all logits during OCR generation.
Goal: see if hidden states degrade after generating <table>.
"""
import sys, io, os, time, math, torch, warnings
warnings.filterwarnings('ignore')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

MODEL_PATH = "C:/Users/BAZA/.cache/huggingface/hub/models--deepseek-ai--DeepSeek-OCR-2/snapshots/aaa02f3811945a91062062994c5c4a3f4c0af2b0"
TEST_IMAGE = "C:/Diagnostica-KB-Package/logs/test_zh_page.jpg"  # ZH L7 config page 2

print("Loading tokenizer...", flush=True)
from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)

print("Loading model...", flush=True)
from transformers import AutoModel
model = AutoModel.from_pretrained(
    MODEL_PATH, trust_remote_code=True, torch_dtype='auto', device_map="cuda:0",
)
model.eval()

# ---- Patch lm_head to track ALL steps ----
_orig_lmh = model.lm_head.forward
_step = [0]
_all_top1 = []
_hs_norms = []

def _patched_lmh(x):
    logits = _orig_lmh(x)
    step = _step[0]
    last = logits[0, -1].float()
    hs_norm = x[0, -1].float().norm().item()
    top5 = last.topk(5)
    ids = top5.indices.tolist()
    scores = top5.values.tolist()
    decoded = [tokenizer.decode([i]) for i in ids]
    eos_logit = last[tokenizer.eos_token_id].item()
    _all_top1.append(ids[0])
    _hs_norms.append(round(hs_norm, 2))
    print(f"  step {step+1}: hs_norm={hs_norm:.1f} EOS={eos_logit:.2f} "
          f"top3={[(repr(d),f'{s:.2f}') for d,s in zip(decoded[:3],scores[:3])]}", flush=True)
    _step[0] += 1
    return logits

model.lm_head.forward = _patched_lmh

import tempfile
tmp = tempfile.mkdtemp(prefix='ocr_hs_')

print("\n=== OCR with grounding + repPenalty=1.3, max_new_tokens=50 ===", flush=True)
_step[0] = 0; _all_top1.clear(); _hs_norms.clear()

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

print(f"\nTotal steps: {_step[0]}", flush=True)
print(f"HS norms: {_hs_norms}", flush=True)
print(f"Top1 decoded: {[tokenizer.decode([t]) for t in _all_top1]}", flush=True)
print(f"Result ({len(result) if result else 0} chars): {repr(result[:500]) if result else '(None)'}", flush=True)
