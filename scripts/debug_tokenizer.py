#!/usr/bin/env python3
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

MODEL_PATH = 'C:/Users/BAZA/.cache/huggingface/hub/models--deepseek-ai--DeepSeek-OCR-2/snapshots/aaa02f3811945a91062062994c5c4a3f4c0af2b0'
from transformers import AutoTokenizer
tok = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)

print(f"BOS id: {tok.bos_token_id}, EOS id: {tok.eos_token_id}")
print(f"Special tokens: {tok.all_special_tokens[:20]}")
print()

tests = [
    '<|User|>: ',
    '<|Assistant|>:',
    '<|User|>',
    '<|Assistant|>',
    '<image>',
    '\nFree OCR.\n\n<|Assistant|>:',
    '<|User|>: <image>',
]
for t in tests:
    ids = tok.encode(t, add_special_tokens=False)
    dec = [tok.decode([i]) for i in ids]
    print(repr(t), '=>', ids, '=', dec)

# Show what the formatted prompt looks like
print()
sys.path.insert(0, MODEL_PATH)
from conversation import get_conv_template
conv = get_conv_template('deepseek')
conv.append_message('<|User|>', '<image>\nFree OCR.')
conv.append_message('<|Assistant|>', '')
prompt = conv.get_prompt().strip()
print("Formatted prompt:", repr(prompt))
