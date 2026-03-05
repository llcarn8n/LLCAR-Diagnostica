#!/usr/bin/env python3
"""
DeepSeek-OCR-2 diagnostic v3: check image mask vs feature count, text-only test.
"""
import sys, io, os, time, torch
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

MODEL_PATH = "C:/Users/BAZA/.cache/huggingface/hub/models--deepseek-ai--DeepSeek-OCR-2/snapshots/aaa02f3811945a91062062994c5c4a3f4c0af2b0"
TEST_IMAGE = "C:/Diagnostica-KB-Package/mineru-output/240322-Li-L9-Configuration/auto/images/0249e4187f921691aeb0efeed3bb018a122f22a38955e8e109c294745a4c7c15.jpg"

print("Loading tokenizer...", flush=True)
from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
print(f"EOS token: {tokenizer.eos_token!r} (id={tokenizer.eos_token_id})", flush=True)

print("\nLoading model...", flush=True)
from transformers import AutoModel
model = AutoModel.from_pretrained(
    MODEL_PATH,
    trust_remote_code=True,
    torch_dtype='auto',
    device_map="cuda:0",
)
model.eval()
print(f"_attn_implementation: {getattr(model.config, '_attn_implementation', 'N/A')}", flush=True)

# Patch masked_scatter_ to report token count match
_orig_masked_scatter = torch.Tensor.masked_scatter_
def _patched_masked_scatter(self, mask, source):
    n_true = mask.sum().item()
    n_src = source.numel() // (source.shape[-1] if source.dim() > 1 else 1)
    print(f"  [masked_scatter_] mask_true={int(n_true)}, source_tokens={n_src}, match={int(n_true)==n_src}", flush=True)
    return _orig_masked_scatter(self, mask, source)
torch.Tensor.masked_scatter_ = _patched_masked_scatter

# Patch lm_head to capture first 10 steps
_orig_lm_head = model.lm_head.forward
_step = [0]

def _patched_lm_head(x):
    logits = _orig_lm_head(x)
    if _step[0] < 10:
        last = logits[0, -1]
        top5 = last.topk(5)
        ids = top5.indices.tolist()
        decoded = [tokenizer.decode([i]) for i in ids]
        is_nan = torch.isnan(last).any().item()
        is_inf = torch.isinf(last).any().item()
        print(f"  LM_HEAD step {_step[0]+1}: top5={list(zip(ids,decoded))} nan={is_nan} inf={is_inf}", flush=True)
    _step[0] += 1
    return logits

model.lm_head.forward = _patched_lm_head

import tempfile
tmp = tempfile.mkdtemp(prefix='deepseek_diag_')

# ===== TEST 1: Text-only (no image) =====
print("\n=== TEST 1: Text-only (no image) ===", flush=True)
_step[0] = 0
try:
    result = model.infer(
        tokenizer=tokenizer,
        prompt="What is 2+2?",
        image_file='',
        output_path=tmp,
        eval_mode=True,
    )
    print(f"Result: {result!r}", flush=True)
except Exception as e:
    print(f"ERROR: {e}", flush=True)
    import traceback; traceback.print_exc()

# ===== TEST 2: With image =====
print(f"\n=== TEST 2: OCR with image ===", flush=True)
_step[0] = 0
try:
    result2 = model.infer(
        tokenizer=tokenizer,
        prompt="<image>\nFree OCR.",
        image_file=TEST_IMAGE,
        output_path=tmp,
        eval_mode=True,
        image_size=768,   # dynamic_preprocess uses 768 internally — must match!
        base_size=1024,
    )
    print(f"Result (first 300): {result2[:300] if result2 else '(empty)'}", flush=True)
except Exception as e:
    print(f"ERROR: {e}", flush=True)
    import traceback; traceback.print_exc()
