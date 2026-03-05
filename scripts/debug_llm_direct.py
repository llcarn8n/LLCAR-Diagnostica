#!/usr/bin/env python3
"""Test LLM directly with deepseek format, no image features."""
import sys, io, torch
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

MODEL_PATH = "C:/Users/BAZA/.cache/huggingface/hub/models--deepseek-ai--DeepSeek-OCR-2/snapshots/aaa02f3811945a91062062994c5c4a3f4c0af2b0"

from transformers import AutoTokenizer, AutoModel
print("Loading...", flush=True)
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
model = AutoModel.from_pretrained(MODEL_PATH, trust_remote_code=True, torch_dtype='auto', device_map="cuda:0")
model.eval()

# Test 1: direct generate with deepseek format, NO images
# Prompt: "<|User|>: What is 2+2?\n\n<|Assistant|>:"
prompt_tokens = tokenizer.encode(
    "<|User|>: What is 2+2?\n\n<|Assistant|>:",
    add_special_tokens=False
)
# Add BOS manually
input_ids = torch.tensor([[0] + prompt_tokens], device='cuda:0')
print(f"Test 1: {len(prompt_tokens)+1} tokens", flush=True)
print(f"Prompt tail: {[tokenizer.decode([t]) for t in input_ids[0][-5:].tolist()]}", flush=True)

with torch.no_grad(), torch.autocast('cuda', dtype=torch.bfloat16):
    out_ids = model.generate(
        input_ids,
        images=[(torch.zeros(1, 3, 1024, 1024, device='cuda:0', dtype=torch.bfloat16),
                 torch.zeros(1, 3, 1024, 1024, device='cuda:0', dtype=torch.bfloat16))],
        images_seq_mask=torch.zeros(1, input_ids.shape[1], dtype=torch.bool, device='cuda:0'),
        images_spatial_crop=torch.zeros(1, 2, dtype=torch.long),
        do_sample=False,
        max_new_tokens=30,
        eos_token_id=tokenizer.eos_token_id,
    )
new_tokens = out_ids[0, input_ids.shape[1]:].tolist()
print(f"Generated: {[tokenizer.decode([t]) for t in new_tokens]}", flush=True)
print(f"Text: {repr(tokenizer.decode(new_tokens))}", flush=True)

# Test 2: What does the LLM predict after seeing an OCR prompt with ZERO image features?
# This tests if the PROMPT FORMAT itself is causing the looping behavior
prompt2 = "<|User|>: <image>\nFree OCR.\n\n<|Assistant|>:"
# Split on <image> and build token sequence manually
img_token_id = 128815
pre = tokenizer.encode("<|User|>: ", add_special_tokens=False)
post = tokenizer.encode("\nFree OCR.\n\n<|Assistant|>:", add_special_tokens=False)
img_tokens = [img_token_id] * 20  # Very small: 20 image tokens
all_tokens = [0] + pre + img_tokens + post
input_ids2 = torch.tensor([all_tokens], device='cuda:0')
images_seq_mask2 = torch.zeros(1, len(all_tokens), dtype=torch.bool, device='cuda:0')
images_seq_mask2[0, len(pre)+1:len(pre)+1+20] = True

print(f"\nTest 2: {len(all_tokens)} tokens, 20 image slots with ZERO features", flush=True)

with torch.no_grad(), torch.autocast('cuda', dtype=torch.bfloat16):
    out2 = model.generate(
        input_ids2,
        images=[(torch.zeros(1, 3, 640, 640, device='cuda:0', dtype=torch.bfloat16),
                 torch.zeros(1, 3, 1024, 1024, device='cuda:0', dtype=torch.bfloat16))],
        images_seq_mask=images_seq_mask2,
        images_spatial_crop=torch.tensor([[1, 1]], dtype=torch.long),
        do_sample=False,
        max_new_tokens=20,
        eos_token_id=tokenizer.eos_token_id,
    )
new2 = out2[0, input_ids2.shape[1]:].tolist()
print(f"Generated with zero image: {[tokenizer.decode([t]) for t in new2]}", flush=True)
print(f"Text: {repr(tokenizer.decode(new2))}", flush=True)
