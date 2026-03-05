"""Debug: OCR one table image and show full model response."""
import paramiko, sys, time
sys.stdout.reconfigure(encoding='utf-8')

HOST = '192.168.50.2'
USER = 'baza'
PASS = 'Llcar2024!'
PROJECT = r'C:\LLCAR-Transfer'
PY311 = r'C:\Users\BAZA\AppData\Local\Programs\Python\Python311\python.exe'

# Write debug script to workstation
DEBUG_SCRIPT = r'''
import torch, json, sys, time, os
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'
from pathlib import Path
from PIL import Image as PILImage

# Find first table image
base = Path(r"C:\LLCAR-Transfer")
cl_path = base / "mineru-output" / "941362155-2022-2023\u6b3e\u7406\u60f3L9\u96f6\u4ef6\u624b\u518c" / "ocr" / "941362155-2022-2023\u6b3e\u7406\u60f3L9\u96f6\u4ef6\u624b\u518c_content_list.json"

with open(cl_path, 'r', encoding='utf-8') as f:
    cl = json.load(f)

# Get first 3 table entries
tables = [e for e in cl if e.get('type') == 'table']
print(f"Total tables: {len(tables)}")

# Load model
from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration
print("Loading model...")
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
print(f"Model loaded, VRAM: {torch.cuda.memory_allocated(0)/1024**3:.1f} GB")

# OCR prompt
OCR_PROMPT = """This image shows a parts catalog table from a Li Auto L9 vehicle manual.
Extract ALL rows from the table. Each row has 4 columns:
- 序号 (index number)
- 热点ID (hotspot ID)
- 零件号码 (part number)
- 零件名称 (part name in Chinese)

Return ONLY a JSON array, no other text:
[{"idx": 1, "hotspot": "1", "part_number": "X01-12345678", "part_name": "零件名称"}]

If the image is not a parts table, return: []"""

# Process first 3 tables
for i, entry in enumerate(tables[:3]):
    img_path_str = entry.get('img_path', '')
    img_path = base / "mineru-output" / "941362155-2022-2023\u6b3e\u7406\u60f3L9\u96f6\u4ef6\u624b\u518c" / "ocr" / img_path_str

    if not img_path.exists():
        # Try relative from base
        img_path = base / img_path_str

    print(f"\n{'='*60}")
    print(f"Table {i+1}: {img_path}")
    print(f"  Exists: {img_path.exists()}")
    print(f"  Page: {entry.get('page_idx', '?')}")

    if not img_path.exists():
        print(f"  SKIP - file not found")
        print(f"  img_path from json: {img_path_str}")
        continue

    pil_img = PILImage.open(img_path).convert("RGB")
    w, h = pil_img.size
    print(f"  Original size: {w}x{h}")

    # Resize
    max_side = 1024
    if max(w, h) > max_side:
        scale = max_side / max(w, h)
        pil_img = pil_img.resize((int(w*scale), int(h*scale)), PILImage.LANCZOS)
        print(f"  Resized to: {pil_img.size}")

    messages = [{"role": "user", "content": [{"type": "image"}, {"type": "text", "text": OCR_PROMPT}]}]
    text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = processor(text=[text], images=[pil_img], return_tensors="pt", padding=True).to("cuda:0")

    print(f"  Input tokens: {inputs['input_ids'].shape[1]}")
    print(f"  VRAM before: {torch.cuda.memory_allocated(0)/1024**3:.1f} GB")

    t0 = time.time()
    with torch.no_grad():
        output_ids = model.generate(**inputs, max_new_tokens=2048, do_sample=False)
    elapsed = time.time() - t0

    input_len = inputs["input_ids"].shape[1]
    generated = output_ids[0, input_len:]
    response = processor.decode(generated, skip_special_tokens=True).strip()

    print(f"  Inference time: {elapsed:.1f}s")
    print(f"  Output tokens: {len(generated)}")
    print(f"  VRAM after: {torch.cuda.memory_allocated(0)/1024**3:.1f} GB")
    print(f"  Response ({len(response)} chars):")
    print(response[:2000])

    # Try parse
    try:
        data = json.loads(response)
        print(f"\n  Parsed OK: {len(data)} rows")
        if data:
            print(f"  First row: {data[0]}")
    except json.JSONDecodeError as e:
        print(f"\n  JSON parse error: {e}")

    del inputs, output_ids
    torch.cuda.empty_cache()

print("\nDone!")
'''

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS, timeout=15,
            allow_agent=False, look_for_keys=False)
print('Connected')

# Kill stale processes
stdin, stdout, stderr = ssh.exec_command('taskkill /f /im python.exe 2>&1', timeout=10)
stdout.read()
time.sleep(2)

# Upload debug script
sftp = ssh.open_sftp()
with sftp.open(f'{PROJECT}\\debug_ocr_one.py', 'w') as f:
    f.write(DEBUG_SCRIPT)
sftp.close()
print('Debug script uploaded')

# Run it
print('\n=== Running debug OCR ===')
cmd = f'cd /d {PROJECT} && "{PY311}" -u debug_ocr_one.py 2>&1'
stdin, stdout, stderr = ssh.exec_command(cmd, timeout=600)

channel = stdout.channel
buf = b''
while not channel.exit_status_ready() or channel.recv_ready():
    if channel.recv_ready():
        data = channel.recv(4096)
        buf += data
        while b'\n' in buf:
            line_bytes, buf = buf.split(b'\n', 1)
            line = line_bytes.decode('utf-8', errors='replace').rstrip()
            if 'HTTP' in line and ('Request' in line or '1.1' in line):
                continue
            if 'Loading weights' in line and 'it/s' in line:
                continue
            if 'Fetching' in line and 'files' in line:
                continue
            print(line, flush=True)
    else:
        time.sleep(0.3)

if buf:
    print(buf.decode('utf-8', errors='replace').rstrip(), flush=True)

code = channel.recv_exit_status()
print(f'\nExit code: {code}')
ssh.close()
