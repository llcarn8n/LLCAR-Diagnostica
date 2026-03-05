#!/usr/bin/env python3
"""Check weight loading for DeepSeek-OCR-2."""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

MODEL_PATH = "C:/Users/BAZA/.cache/huggingface/hub/models--deepseek-ai--DeepSeek-OCR-2/snapshots/aaa02f3811945a91062062994c5c4a3f4c0af2b0"

from transformers import AutoTokenizer, AutoModel
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)

# Load with verbose to capture missing/unexpected keys
import logging
logging.disable(logging.CRITICAL)

model = AutoModel.from_pretrained(MODEL_PATH, trust_remote_code=True, torch_dtype='auto', device_map="cuda:0")
model.eval()

# Check sub-model weights
import torch
print("sam_model type:", type(model.model.sam_model).__name__, flush=True)
print("qwen2_model type:", type(model.model.qwen2_model).__name__, flush=True)
print("projector type:", type(model.model.projector).__name__, flush=True)

# Check if sam_model has any parameters
sam_params = list(model.model.sam_model.parameters())
print(f"sam_model: {len(sam_params)} params, first param dtype: {sam_params[0].dtype if sam_params else 'N/A'}", flush=True)
print(f"sam_model: first param mean: {sam_params[0].float().mean().item():.4f} std: {sam_params[0].float().std().item():.4f}", flush=True)

qwen_params = list(model.model.qwen2_model.parameters())
print(f"qwen2_model: {len(qwen_params)} params, first param dtype: {qwen_params[0].dtype if qwen_params else 'N/A'}", flush=True)
print(f"qwen2_model: first param mean: {qwen_params[0].float().mean().item():.4f} std: {qwen_params[0].float().std().item():.4f}", flush=True)

proj_params = list(model.model.projector.parameters())
print(f"projector: {len(proj_params)} params, first param: mean={proj_params[0].float().mean().item():.4f}", flush=True)

# Check embedding weights
emb = model.model.embed_tokens.weight
print(f"embed_tokens: shape={emb.shape}, mean={emb.float().mean().item():.4f}, std={emb.float().std().item():.4f}", flush=True)

# Now do a quick forward pass with zero image (pure text) to verify LLM works
import torch
input_ids = torch.tensor([[0, 128825, 28, 223, 128826, 28]], device='cuda:0')  # BOS <|User|>: <|Assistant|>:
with torch.no_grad(), torch.autocast('cuda', dtype=torch.bfloat16):
    out = model(input_ids=input_ids, use_cache=False)
print(f"Text-only forward: logits shape={out.logits.shape}", flush=True)
top5 = out.logits[0, -1].topk(5)
decoded = [tokenizer.decode([i]) for i in top5.indices.tolist()]
print(f"Top 5 next tokens: {list(zip(top5.indices.tolist(), decoded, top5.values.tolist()))}", flush=True)
