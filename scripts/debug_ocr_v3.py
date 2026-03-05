#!/usr/bin/env python3
"""
DeepSeek-OCR-2 diagnostic v4:
- Patches forward() to print image feature injection stats
- Tests both eval_mode and streaming mode
- Checks text-only result via manual decode (bypasses infer() None bug)
"""
import sys, io, os, time, math, torch
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

MODEL_PATH = "C:/Users/BAZA/.cache/huggingface/hub/models--deepseek-ai--DeepSeek-OCR-2/snapshots/aaa02f3811945a91062062994c5c4a3f4c0af2b0"
TEST_IMAGE = "C:/Diagnostica-KB-Package/logs/test_zh_page.jpg"  # ZH L7 config page 2

print("Loading tokenizer...", flush=True)
from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
print(f"EOS id={tokenizer.eos_token_id}, BOS id={tokenizer.bos_token_id}", flush=True)

print("\nLoading model...", flush=True)
from transformers import AutoModel
model = AutoModel.from_pretrained(
    MODEL_PATH, trust_remote_code=True, torch_dtype='auto', device_map="cuda:0",
)
model.eval()
print(f"use_mla={model.config.use_mla}, hidden_size={model.config.hidden_size}", flush=True)

# ---- Patch masked_scatter_ ----
_orig_ms = torch.Tensor.masked_scatter_
def _patched_ms(self, mask, source):
    n_true = int(mask.sum().item())
    n_src_rows = source.shape[0] if source.dim() > 1 else source.numel()
    print(f"  [masked_scatter_] mask_true={n_true}, src_rows={n_src_rows}, "
          f"src_stats: mean={source.float().mean():.4f} std={source.float().std():.4f} "
          f"min={source.float().min():.4f} max={source.float().max():.4f}", flush=True)
    return _orig_ms(self, mask, source)
torch.Tensor.masked_scatter_ = _patched_ms

# ---- Patch lm_head to capture first 5 steps ----
_orig_lmh = model.lm_head.forward
_step = [0]
_all_top1 = []

def _patched_lmh(x):
    logits = _orig_lmh(x)
    step = _step[0]
    last = logits[0, -1].float()
    hs_norm = x[0, -1].float().norm().item()  # hidden state norm at last position
    top5 = last.topk(5)
    ids = top5.indices.tolist()
    scores = top5.values.tolist()
    decoded = [tokenizer.decode([i]) for i in ids]
    _all_top1.append(ids[0])
    if step < 25:  # print all steps for short sequences
        eos_logit = last[tokenizer.eos_token_id].item()
        print(f"  LM step {step+1}: hs_norm={hs_norm:.1f} top5={[(i,repr(d),f'{s:.2f}') for i,d,s in zip(ids,decoded,scores)]} "
              f"EOS={eos_logit:.2f}", flush=True)
    _step[0] += 1
    return logits
model.lm_head.forward = _patched_lmh

import tempfile
tmp = tempfile.mkdtemp(prefix='deepseek_v4_')

# ===== TEST 1: Minimal direct generate (no infer(), text-only) =====
print("\n=== TEST 1: Direct generate text-only ===", flush=True)
_step[0] = 0
_all_top1.clear()

# Build prompt manually
prompt_text = "<|User|>: What is 2+2?\n\n<|Assistant|>:"
input_ids = torch.LongTensor([0] + tokenizer.encode(prompt_text, add_special_tokens=False)).unsqueeze(0).cuda()
print(f"  input_ids shape: {input_ids.shape}, last 5 tokens: {input_ids[0,-5:].tolist()}", flush=True)

# Create zero images (no image)
image_size, base_size = 640, 1024
images_crop = torch.zeros((1, 3, base_size, base_size), dtype=torch.bfloat16).cuda()
images_ori = torch.zeros((1, 3, base_size, base_size), dtype=torch.bfloat16).cuda()
images_seq_mask = torch.zeros(1, input_ids.shape[1], dtype=torch.bool).cuda()
images_spatial_crop = torch.zeros((1, 2), dtype=torch.long)

with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16):
    out = model.generate(
        input_ids,
        images=[(images_crop, images_ori)],
        images_seq_mask=images_seq_mask,
        images_spatial_crop=images_spatial_crop,
        do_sample=False,
        max_new_tokens=50,
        eos_token_id=tokenizer.eos_token_id,
        use_cache=True,
    )

decoded = tokenizer.decode(out[0, input_ids.shape[1]:], skip_special_tokens=False)
print(f"  Generated: {repr(decoded[:200])}", flush=True)
print(f"  Top1 tokens at each step: {_all_top1[:10]}", flush=True)

# ===== TEST 2: infer() with image (eval_mode=True) =====
print(f"\n=== TEST 2: model.infer() with image ===", flush=True)
_step[0] = 0
_all_top1.clear()

try:
    result = model.infer(
        tokenizer=tokenizer,
        prompt="<image>\nFree OCR.",
        image_file=TEST_IMAGE,
        output_path=tmp,
        eval_mode=True,
        image_size=768,
        base_size=1024,
    )
    print(f"  Result ({len(result) if result else 0} chars): {repr(result[:400]) if result else '(empty)'}", flush=True)
except Exception as e:
    print(f"  ERROR: {e}", flush=True)
    import traceback; traceback.print_exc()

print(f"\n  Top1 tokens at each step: {_all_top1[:10]}", flush=True)
print(f"  EOS token id = {tokenizer.eos_token_id}", flush=True)
print("  (EOS at step 1 = empty generation problem)", flush=True)

# ===== TEST 3: infer() with NO repetition_penalty =====
print(f"\n=== TEST 3: infer() NO repetition_penalty ===", flush=True)
_step[0] = 0
_all_top1.clear()

# Patch generate() to strip repetition_penalty
_orig_generate = model.generate
def _patched_generate(*args, **kwargs):
    kwargs.pop('repetition_penalty', None)
    kwargs.pop('no_repeat_ngram_size', None)
    print(f"  generate() kwargs keys: {list(kwargs.keys())}", flush=True)
    return _orig_generate(*args, **kwargs)
model.generate = _patched_generate

try:
    result3 = model.infer(
        tokenizer=tokenizer,
        prompt="<image>\nOCR所有文字。",
        image_file=TEST_IMAGE,
        output_path=tmp,
        eval_mode=True,
        image_size=768,
        base_size=1024,
    )
    print(f"  Result ({len(result3) if result3 else 0} chars): {repr(result3[:600]) if result3 else '(empty)'}", flush=True)
except Exception as e:
    print(f"  ERROR: {e}", flush=True)
    import traceback; traceback.print_exc()

model.generate = _orig_generate  # restore
print(f"\n  Top1 tokens at each step: {_all_top1[:20]}", flush=True)

# ===== TEST 4: Official prompt with <|grounding|> token =====
print(f"\n=== TEST 4: Official grounding prompt ===", flush=True)
_step[0] = 0
_all_top1.clear()

try:
    result4 = model.infer(
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
    n = len(result4) if result4 else 0
    preview = repr(result4[:800]) if result4 else '(None/empty)'
    print(f"  Result ({n} chars): {preview}", flush=True)
except Exception as e:
    print(f"  ERROR: {e}", flush=True)
    import traceback; traceback.print_exc()

print(f"\n  Total steps: {_step[0]}", flush=True)
print(f"  Top1 tokens (first 30): {_all_top1[:30]}", flush=True)
decoded_preview = [tokenizer.decode([t]) for t in _all_top1[:30]]
print(f"  Decoded: {decoded_preview}", flush=True)

# ===== TEST 5: Grounding prompt, no penalties, extended generation =====
print(f"\n=== TEST 5: Grounding + no penalties ===", flush=True)
_step[0] = 0
_all_top1.clear()

_orig_generate2 = model.generate
def _patched_generate2(*args, **kwargs):
    kwargs.pop('repetition_penalty', None)
    kwargs.pop('no_repeat_ngram_size', None)
    kwargs['max_new_tokens'] = 200  # show more output
    return _orig_generate2(*args, **kwargs)
model.generate = _patched_generate2

try:
    result5 = model.infer(
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
    n = len(result5) if result5 else 0
    preview = repr(result5[:1000]) if result5 else '(None/empty)'
    print(f"  Result ({n} chars): {preview}", flush=True)
except Exception as e:
    print(f"  ERROR: {e}", flush=True)
    import traceback; traceback.print_exc()

model.generate = _orig_generate2  # restore
print(f"\n  Total steps: {_step[0]}", flush=True)
decoded_preview5 = [tokenizer.decode([t]) for t in _all_top1[:50]]
print(f"  Decoded (first 50): {decoded_preview5}", flush=True)

# ===== TEST 6: non-eval mode params (README default), grounding prompt =====
print(f"\n=== TEST 6: non-eval params (no_repeat=20, no repPenalty) ===", flush=True)
_step[0] = 0
_all_top1.clear()

# Mirror non-eval path: no repetition_penalty, no_repeat_ngram_size=20
_orig_generate3 = model.generate
def _patched_generate3(*args, **kwargs):
    kwargs.pop('repetition_penalty', None)
    kwargs.pop('no_repeat_ngram_size', None)
    kwargs['no_repeat_ngram_size'] = 20
    kwargs['max_new_tokens'] = 300
    return _orig_generate3(*args, **kwargs)
model.generate = _patched_generate3

try:
    result6 = model.infer(
        tokenizer=tokenizer,
        prompt="<image>\n<|grounding|>Convert the document to markdown. ",
        image_file=TEST_IMAGE,
        output_path=tmp,
        eval_mode=True,   # still need eval_mode for return value
        image_size=768,
        base_size=1024,
        crop_mode=True,
        save_results=False,
    )
    n = len(result6) if result6 else 0
    print(f"  Result ({n} chars):", flush=True)
    if result6:
        print(result6[:1000], flush=True)
except Exception as e:
    print(f"  ERROR: {e}", flush=True)
    import traceback; traceback.print_exc()

model.generate = _orig_generate3  # restore
print(f"\n  Total steps: {_step[0]}", flush=True)

# ===== TEST 7: use_cache=False to rule out KV cache bug =====
print(f"\n=== TEST 7: use_cache=False ===", flush=True)
_step[0] = 0
_all_top1.clear()

_orig_generate4 = model.generate
def _patched_generate4(*args, **kwargs):
    kwargs['use_cache'] = False
    kwargs['max_new_tokens'] = 20
    kwargs['repetition_penalty'] = 1.3
    kwargs['no_repeat_ngram_size'] = 5
    print(f"  generate() use_cache=False", flush=True)
    return _orig_generate4(*args, **kwargs)
model.generate = _patched_generate4

try:
    result7 = model.infer(
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
    n = len(result7) if result7 else 0
    print(f"  Result ({n} chars): {repr(result7[:400]) if result7 else '(None)'}", flush=True)
except Exception as e:
    print(f"  ERROR: {e}", flush=True)
    import traceback; traceback.print_exc()

model.generate = _orig_generate4  # restore
print(f"\n  Total steps TEST7: {_step[0]}", flush=True)
decoded7 = [tokenizer.decode([t]) for t in _all_top1[:20]]
print(f"  Decoded: {decoded7}", flush=True)

# ===== TEST 8: grounding + repPenalty, NO no_repeat_ngram_size =====
print(f"\n=== TEST 8: grounding + repPenalty=1.3 + NO no_repeat ===", flush=True)
_step[0] = 0
_all_top1.clear()

_orig_generate5 = model.generate
def _patched_generate5(*args, **kwargs):
    kwargs['repetition_penalty'] = 1.3
    kwargs.pop('no_repeat_ngram_size', None)  # remove ngram blocking
    kwargs['max_new_tokens'] = 200
    return _orig_generate5(*args, **kwargs)
model.generate = _patched_generate5

try:
    result8 = model.infer(
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
    n = len(result8) if result8 else 0
    print(f"  Result ({n} chars):", flush=True)
    if result8:
        print(result8[:800], flush=True)
except Exception as e:
    print(f"  ERROR: {e}", flush=True)
    import traceback; traceback.print_exc()

model.generate = _orig_generate5  # restore
print(f"\n  Total steps TEST8: {_step[0]}", flush=True)
decoded8 = [tokenizer.decode([t]) for t in _all_top1[:50]]
print(f"  Decoded (first 50): {decoded8}", flush=True)
