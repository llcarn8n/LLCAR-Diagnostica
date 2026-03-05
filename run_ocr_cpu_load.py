"""Load model on CPU first, then move to GPU (bypasses device_map crash)."""
import paramiko, sys, time
sys.stdout.reconfigure(encoding='utf-8')

HOST = '192.168.50.2'
USER = 'baza'
PASS = 'Llcar2024!'
PROJECT = r'C:\LLCAR-Transfer'
PY311 = r'C:\Users\BAZA\AppData\Local\Programs\Python\Python311\python.exe'

# First try CPU-load approach
TEST_CPU_LOAD = r'''
import torch, sys, time
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

print("=== Approach: Load on CPU, then move to GPU ===", flush=True)
print(f"Free RAM before: ~{torch.cuda.mem_get_info(0)[0]/1024**3:.1f} GB GPU free", flush=True)

from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration

t0 = time.time()
print("Loading processor...", flush=True)
processor = AutoProcessor.from_pretrained("Qwen/Qwen2.5-VL-7B-Instruct", use_fast=False)
print(f"  Processor loaded in {time.time()-t0:.1f}s", flush=True)

print("Loading model to CPU (no device_map)...", flush=True)
t1 = time.time()
model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
    "Qwen/Qwen2.5-VL-7B-Instruct",
    torch_dtype=torch.bfloat16,
    trust_remote_code=True,
    low_cpu_mem_usage=True,
    attn_implementation="eager",
)
print(f"  CPU load done in {time.time()-t1:.1f}s", flush=True)

print("Moving model to cuda:0...", flush=True)
t2 = time.time()
model = model.to("cuda:0")
model.eval()
print(f"  GPU transfer done in {time.time()-t2:.1f}s", flush=True)

vram = torch.cuda.memory_allocated(0) / 1024**3
print(f"\nSUCCESS: Total {time.time()-t0:.1f}s, VRAM: {vram:.1f} GB", flush=True)

# Quick inference test
from PIL import Image as PILImage
import json
from pathlib import Path

base = Path(r"C:\LLCAR-Transfer")
cl_path = base / "mineru-output" / "941362155-2022-2023\u6b3e\u7406\u60f3L9\u96f6\u4ef6\u624b\u518c" / "ocr" / "941362155-2022-2023\u6b3e\u7406\u60f3L9\u96f6\u4ef6\u624b\u518c_content_list.json"
with open(cl_path, 'r', encoding='utf-8') as f:
    cl = json.load(f)
tables = [e for e in cl if e.get('type') == 'table']
print(f"\nTotal tables: {len(tables)}", flush=True)

# Test OCR on first table
entry = tables[0]
img_path = base / "mineru-output" / "941362155-2022-2023\u6b3e\u7406\u60f3L9\u96f6\u4ef6\u624b\u518c" / "ocr" / entry.get('img_path', '')
if not img_path.exists():
    img_path = base / entry.get('img_path', '')

if img_path.exists():
    print(f"Testing OCR on: {img_path.name}", flush=True)
    pil_img = PILImage.open(img_path).convert("RGB")
    w, h = pil_img.size
    if max(w, h) > 1024:
        scale = 1024 / max(w, h)
        pil_img = pil_img.resize((int(w*scale), int(h*scale)), PILImage.LANCZOS)

    OCR_PROMPT = """This image shows a parts catalog table from a Li Auto L9 vehicle manual.
Extract ALL rows from the table. Each row has 4 columns:
- \u5e8f\u53f7 (index number)
- \u70ed\u70b9ID (hotspot ID)
- \u96f6\u4ef6\u53f7\u7801 (part number)
- \u96f6\u4ef6\u540d\u79f0 (part name in Chinese)

Return ONLY a JSON array, no other text:
[{"idx": 1, "hotspot": "1", "part_number": "X01-12345678", "part_name": "\u96f6\u4ef6\u540d\u79f0"}]

If the image is not a parts table, return: []"""

    messages = [{"role": "user", "content": [{"type": "image"}, {"type": "text", "text": OCR_PROMPT}]}]
    text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = processor(text=[text], images=[pil_img], return_tensors="pt", padding=True).to("cuda:0")

    t3 = time.time()
    with torch.no_grad():
        output_ids = model.generate(**inputs, max_new_tokens=2048, do_sample=False)
    elapsed = time.time() - t3

    input_len = inputs["input_ids"].shape[1]
    generated = output_ids[0, input_len:]
    response = processor.decode(generated, skip_special_tokens=True).strip()

    print(f"  Inference: {elapsed:.1f}s, {len(generated)} tokens", flush=True)
    try:
        resp = response
        if resp.startswith('```'):
            lines = resp.split('\n')
            lines = [l for l in lines if not l.strip().startswith('```')]
            resp = '\n'.join(lines)
        data = json.loads(resp)
        print(f"  Result: {len(data)} parts extracted", flush=True)
        if data:
            print(f"  First: {data[0]}", flush=True)
    except:
        print(f"  Raw (first 200): {response[:200]}", flush=True)

    del inputs, output_ids
    torch.cuda.empty_cache()
else:
    print(f"  Image not found: {img_path}", flush=True)

print("\nPASSED", flush=True)
'''

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS, timeout=15,
            allow_agent=False, look_for_keys=False)
print(f'Connected to {HOST}')

def run_raw(cmd, timeout=600):
    print(f'\n>>> {cmd[:200]}', flush=True)
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    channel = stdout.channel
    buf = b''
    while not channel.exit_status_ready() or channel.recv_ready():
        if channel.recv_ready():
            data = channel.recv(4096)
            buf += data
            while b'\n' in buf:
                line_bytes, buf = buf.split(b'\n', 1)
                line = line_bytes.decode('utf-8', errors='replace').rstrip()
                if 'HTTP Request' in line or 'HTTP/1.1' in line:
                    continue
                if 'Loading weights' in line and 'it/s' in line:
                    if any(f' {p}%' in line for p in ['25', '50', '75', '100']):
                        print(line[:120], flush=True)
                    continue
                if 'Fetching' in line and 'files' in line:
                    continue
                print(line, flush=True)
        else:
            time.sleep(0.5)
    if buf:
        line = buf.decode('utf-8', errors='replace').rstrip()
        if line and 'HTTP' not in line:
            print(line, flush=True)
    code = channel.recv_exit_status()
    return code

# Kill any stale processes
run_raw('taskkill /f /im python.exe 2>&1 & echo done', timeout=15)
time.sleep(5)

# Write and run
sftp = ssh.open_sftp()
with sftp.open(f'{PROJECT}\\test_load.py', 'w') as f:
    f.write(TEST_CPU_LOAD)
sftp.close()

print('\n=== Testing CPU-first model loading ===')
cmd = f'cd /d {PROJECT} && "{PY311}" -u test_load.py 2>&1'
code = run_raw(cmd, timeout=600)
print(f'\nExit code: {code}')

ssh.close()
print('\nDone!')
