"""Test: does the working debug_ocr_one.py pattern still work?
Then test progressively larger scripts to find what breaks."""
import paramiko, sys, time
sys.stdout.reconfigure(encoding='utf-8')

HOST = '192.168.50.2'
USER = 'baza'
PASS = 'Llcar2024!'
PROJECT = r'C:\LLCAR-Transfer'
PY311 = r'C:\Users\BAZA\AppData\Local\Programs\Python\Python311\python.exe'

# Test 1: Minimal model load (should work - same as debug_ocr_one.py)
MINIMAL_SCRIPT = r'''
import torch, sys, time
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

print("Test: minimal model load...", flush=True)
from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration

t0 = time.time()
processor = AutoProcessor.from_pretrained("Qwen/Qwen2.5-VL-7B-Instruct", use_fast=False)
model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
    "Qwen/Qwen2.5-VL-7B-Instruct",
    torch_dtype=torch.bfloat16,
    device_map="cuda:0",
    trust_remote_code=True,
    low_cpu_mem_usage=True,
    attn_implementation="eager",
)
model.eval()
vram = torch.cuda.memory_allocated(0) / 1024**3
print(f"SUCCESS: Model loaded in {time.time()-t0:.1f}s, VRAM: {vram:.1f} GB", flush=True)
print("PASSED", flush=True)
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

# Kill stale processes
print('Cleaning GPU...')
run_raw('taskkill /f /im python.exe 2>&1 & echo done', timeout=15)
time.sleep(5)
run_raw('nvidia-smi --query-gpu=index,memory.used,memory.free --format=csv,noheader', timeout=10)

# Test 1: Minimal
print('\n=== TEST 1: Minimal model load ===')
sftp = ssh.open_sftp()
with sftp.open(f'{PROJECT}\\test_load.py', 'w') as f:
    f.write(MINIMAL_SCRIPT)
sftp.close()

cmd = f'cd /d {PROJECT} && "{PY311}" -u test_load.py 2>&1'
code = run_raw(cmd, timeout=300)
print(f'Exit code: {code}')

if code != 0:
    print('\nMinimal load FAILED - system issue, not script issue')
    ssh.close()
    sys.exit(1)

print('\nMinimal load PASSED - model loads fine')
print('Waiting 10s for GPU cleanup...')
run_raw('taskkill /f /im python.exe 2>&1 & echo done', timeout=15)
time.sleep(10)

# Test 2: Model load + sqlite3 import + json import + re import
TEST2_SCRIPT = r'''
import torch, json, re, sqlite3, sys, time, os
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'
from pathlib import Path
from PIL import Image as PILImage

print("Test 2: model load with all imports...", flush=True)
from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration

t0 = time.time()
processor = AutoProcessor.from_pretrained("Qwen/Qwen2.5-VL-7B-Instruct", use_fast=False)
model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
    "Qwen/Qwen2.5-VL-7B-Instruct",
    torch_dtype=torch.bfloat16,
    device_map="cuda:0",
    trust_remote_code=True,
    low_cpu_mem_usage=True,
    attn_implementation="eager",
)
model.eval()
vram = torch.cuda.memory_allocated(0) / 1024**3
print(f"SUCCESS: {time.time()-t0:.1f}s, VRAM: {vram:.1f} GB", flush=True)
print("PASSED", flush=True)
'''

print('\n=== TEST 2: Model load with all imports ===')
sftp = ssh.open_sftp()
with sftp.open(f'{PROJECT}\\test_load.py', 'w') as f:
    f.write(TEST2_SCRIPT)
sftp.close()

cmd = f'cd /d {PROJECT} && "{PY311}" -u test_load.py 2>&1'
code = run_raw(cmd, timeout=300)
print(f'Exit code: {code}')

if code != 0:
    print('\nTest 2 FAILED - extra imports cause crash')
    ssh.close()
    sys.exit(1)

print('\nTest 2 PASSED')
print('Waiting 10s...')
run_raw('taskkill /f /im python.exe 2>&1 & echo done', timeout=15)
time.sleep(10)

# Test 3: Full script but only process 3 tables (like debug_ocr_one.py)
TEST3_SCRIPT = r'''
import torch, json, re, sqlite3, sys, time, os
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'
from pathlib import Path
from PIL import Image as PILImage
from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration

BASE = Path(r"C:\LLCAR-Transfer")
CL_DIR = BASE / "mineru-output" / "941362155-2022-2023\u6b3e\u7406\u60f3L9\u96f6\u4ef6\u624b\u518c"
CL_PATH = CL_DIR / "ocr" / "941362155-2022-2023\u6b3e\u7406\u60f3L9\u96f6\u4ef6\u624b\u518c_content_list.json"
IMG_BASE = CL_DIR / "ocr"

with open(CL_PATH, 'r', encoding='utf-8') as f:
    cl = json.load(f)
tables = [e for e in cl if e.get('type') == 'table']
print(f"Total tables: {len(tables)}", flush=True)

print("Loading model...", flush=True)
processor = AutoProcessor.from_pretrained("Qwen/Qwen2.5-VL-7B-Instruct", use_fast=False)
model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
    "Qwen/Qwen2.5-VL-7B-Instruct",
    torch_dtype=torch.bfloat16,
    device_map="cuda:0",
    trust_remote_code=True,
    low_cpu_mem_usage=True,
    attn_implementation="eager",
)
model.eval()
print(f"Model loaded, VRAM: {torch.cuda.memory_allocated(0)/1024**3:.1f} GB", flush=True)

OCR_PROMPT = """This image shows a parts catalog table from a Li Auto L9 vehicle manual.
Extract ALL rows from the table. Each row has 4 columns:
- \u5e8f\u53f7 (index number)
- \u70ed\u70b9ID (hotspot ID)
- \u96f6\u4ef6\u53f7\u7801 (part number)
- \u96f6\u4ef6\u540d\u79f0 (part name in Chinese)

Return ONLY a JSON array, no other text:
[{"idx": 1, "hotspot": "1", "part_number": "X01-12345678", "part_name": "\u96f6\u4ef6\u540d\u79f0"}]

If the image is not a parts table, return: []"""

for i, entry in enumerate(tables[:3]):
    img_path_str = entry.get('img_path', '')
    img_path = IMG_BASE / img_path_str
    if not img_path.exists():
        img_path = BASE / img_path_str
    if not img_path.exists():
        print(f"  SKIP: {img_path_str}", flush=True)
        continue

    pil_img = PILImage.open(img_path).convert("RGB")
    w, h = pil_img.size
    if max(w, h) > 1024:
        scale = 1024 / max(w, h)
        pil_img = pil_img.resize((int(w*scale), int(h*scale)), PILImage.LANCZOS)

    messages = [{"role": "user", "content": [{"type": "image"}, {"type": "text", "text": OCR_PROMPT}]}]
    text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = processor(text=[text], images=[pil_img], return_tensors="pt", padding=True).to("cuda:0")

    t0 = time.time()
    with torch.no_grad():
        output_ids = model.generate(**inputs, max_new_tokens=2048, do_sample=False)
    elapsed = time.time() - t0

    input_len = inputs["input_ids"].shape[1]
    generated = output_ids[0, input_len:]
    response = processor.decode(generated, skip_special_tokens=True).strip()

    try:
        if response.startswith('```'):
            lines = response.split('\n')
            lines = [l for l in lines if not l.strip().startswith('```')]
            response = '\n'.join(lines)
        data = json.loads(response)
        print(f"  Table {i+1}: {len(data)} parts in {elapsed:.1f}s", flush=True)
    except:
        match = re.search(r'\[.*\]', response, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group())
                print(f"  Table {i+1}: {len(data)} parts in {elapsed:.1f}s (regex)", flush=True)
            except:
                print(f"  Table {i+1}: parse error in {elapsed:.1f}s", flush=True)
        else:
            print(f"  Table {i+1}: no JSON in {elapsed:.1f}s", flush=True)

    del inputs, output_ids
    torch.cuda.empty_cache()

print("PASSED", flush=True)
'''

print('\n=== TEST 3: Model + 3 tables (like debug_ocr_one.py) ===')
sftp = ssh.open_sftp()
with sftp.open(f'{PROJECT}\\test_load.py', 'w') as f:
    f.write(TEST3_SCRIPT)
sftp.close()

cmd = f'cd /d {PROJECT} && "{PY311}" -u test_load.py 2>&1'
code = run_raw(cmd, timeout=600)
print(f'Exit code: {code}')

ssh.close()
print('\nDone!')
