"""Run full OCR: load model FIRST (like working debug_ocr_one.py), then setup DB/data."""
import paramiko, sys, time
sys.stdout.reconfigure(encoding='utf-8')

HOST = '192.168.50.2'
USER = 'baza'
PASS = 'Llcar2024!'
PROJECT = r'C:\LLCAR-Transfer'
PY311 = r'C:\Users\BAZA\AppData\Local\Programs\Python\Python311\python.exe'

# The script loads model FIRST before any other work (proven working pattern)
FULL_OCR_SCRIPT = r'''
import torch, json, re, sys, time, os
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'
from pathlib import Path
from PIL import Image as PILImage

# ===== STEP 1: Load model FIRST (exact same pattern as working debug_ocr_one.py) =====
from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration
print("Loading Qwen2.5-VL-7B on cuda:0 (bfloat16, eager)...", flush=True)
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
print(f"Model loaded in {time.time()-t0:.1f}s, VRAM: {vram:.1f} GB", flush=True)

# ===== STEP 2: Now load data and setup DB (AFTER model is loaded) =====
import sqlite3

BASE = Path(r"C:\LLCAR-Transfer")
KB_DB = BASE / "knowledge-base" / "kb.db"
CL_DIR = BASE / "mineru-output" / "941362155-2022-2023\u6b3e\u7406\u60f3L9\u96f6\u4ef6\u624b\u518c"
CL_PATH = CL_DIR / "ocr" / "941362155-2022-2023\u6b3e\u7406\u60f3L9\u96f6\u4ef6\u624b\u518c_content_list.json"
IMG_BASE = CL_DIR / "ocr"

SYSTEMS = {
    '\u52a8\u529b\u7535\u6c60\u7cfb\u7edf': 'Power Battery System',
    '\u52a8\u529b\u9a71\u52a8\u7cfb\u7edf': 'Power Drive System',
    '\u8fdb\u6c14\u88c5\u7f6e': 'Intake System',
    '\u6392\u6c14\u88c5\u7f6e': 'Exhaust System',
    '\u71c3\u6cb9\u4f9b\u7ed9\u88c5\u7f6e': 'Fuel Supply System',
    '\u53d1\u52a8\u673a\u88c5\u7f6e': 'Engine Assembly',
    '\u60ac\u7f6e\u88c5\u7f6e': 'Engine/Drivetrain Mounts',
    '\u524d\u60ac\u67b6\u88c5\u7f6e': 'Front Suspension',
    '\u540e\u60ac\u67b6\u88c5\u7f6e': 'Rear Suspension',
    '\u8f6c\u5411\u88c5\u7f6e': 'Steering System',
    '\u884c\u8f66\u5236\u52a8\u88c5\u7f6e': 'Service Brake System',
    '\u7a7a\u8c03\u70ed\u7ba1\u7406\u7cfb\u7edf': 'HVAC & Thermal Management',
    '\u7535\u5668\u9644\u4ef6\u7cfb\u7edf': 'Electrical Accessories',
    '\u5185\u9970\u7cfb\u7edf': 'Interior Trim System',
    '\u7535\u6e90\u548c\u4fe1\u53f7\u5206\u914d\u7cfb\u7edf': 'Power & Signal Distribution',
    '\u706f\u5177\u7cfb\u7edf': 'Lighting System',
    '\u5ea7\u6905\u7cfb\u7edf': 'Seat System',
    '\u88ab\u52a8\u5b89\u5168\u7cfb\u7edf': 'Passive Safety System',
    '\u5916\u9970\u7cfb\u7edf': 'Exterior Trim System',
    '\u81ea\u52a8\u9a7e\u9a76\u7cfb\u7edf': 'Autonomous Driving System',
    '\u667a\u80fd\u7a7a\u95f4\u7cfb\u7edf': 'Smart Cabin / Infotainment',
    '\u5f00\u95ed\u4ef6\u7cfb\u7edf': 'Closures (Doors, Hood, Tailgate)',
    '\u8f66\u8eab\u88c5\u7f6e': 'Body Structure',
    '\u6574\u8f66\u9644\u4ef6\u88c5\u7f6e': 'Vehicle Accessories & Consumables',
}

OCR_PROMPT = """This image shows a parts catalog table from a Li Auto L9 vehicle manual.
Extract ALL rows from the table. Each row has 4 columns:
- \u5e8f\u53f7 (index number)
- \u70ed\u70b9ID (hotspot ID)
- \u96f6\u4ef6\u53f7\u7801 (part number)
- \u96f6\u4ef6\u540d\u79f0 (part name in Chinese)

Return ONLY a JSON array, no other text:
[{"idx": 1, "hotspot": "1", "part_number": "X01-12345678", "part_name": "\u96f6\u4ef6\u540d\u79f0"}]

If the image is not a parts table, return: []"""

print("\nLoading content_list.json...", flush=True)
with open(CL_PATH, 'r', encoding='utf-8') as f:
    cl = json.load(f)

tables = [{'img_path': e.get('img_path', ''), 'page_idx': e.get('page_idx', 0)}
          for e in cl if e.get('type') == 'table']
print(f"  Found {len(tables)} tables", flush=True)

# Build page->system map
page_map = {}
cur_zh = ''
cur_en = ''
for entry in cl:
    if entry.get('type') != 'text':
        continue
    text = entry.get('text', '').strip()
    page = entry.get('page_idx', 0)
    for zh, en in SYSTEMS.items():
        if zh in text:
            cur_zh = zh
            cur_en = en
            break
    page_map[page] = {'system_zh': cur_zh, 'system_en': cur_en}
del cl  # free memory
print(f"  Page->system mapping: {len(page_map)} pages", flush=True)

# Setup DB
conn = sqlite3.connect(str(KB_DB))
conn.execute("""CREATE TABLE IF NOT EXISTS parts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    part_number TEXT NOT NULL,
    part_name_zh TEXT NOT NULL,
    part_name_en TEXT,
    hotspot_id TEXT,
    system_zh TEXT,
    system_en TEXT,
    subsystem_zh TEXT,
    subsystem_en TEXT,
    page_idx INTEGER,
    source_image TEXT,
    confidence REAL DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)""")
conn.execute("CREATE INDEX IF NOT EXISTS idx_parts_number ON parts(part_number)")
conn.execute("CREATE INDEX IF NOT EXISTS idx_parts_system ON parts(system_zh)")
conn.commit()

# Resume support
try:
    rows = conn.execute("SELECT DISTINCT source_image FROM parts").fetchall()
    processed = {r[0] for r in rows}
except:
    processed = set()
if processed:
    print(f"  Already processed: {len(processed)} images (resume)", flush=True)

pending = [t for t in tables if t['img_path'] not in processed]
print(f"  Tables to process: {len(pending)}", flush=True)

if not pending:
    print("Nothing to do!")
    conn.close()
    exit(0)

# ===== STEP 3: Process all tables =====
total_parts = 0
total_ok = 0
total_empty = 0
total_error = 0
t_start = time.time()

for i, entry in enumerate(pending):
    img_rel = entry['img_path']
    page_idx = entry['page_idx']

    img_path = IMG_BASE / img_rel
    if not img_path.exists():
        img_path = BASE / img_rel
    if not img_path.exists():
        print(f"  {i+1}/{len(pending)}  SKIP (not found): {img_rel}", flush=True)
        total_error += 1
        continue

    sys_info = page_map.get(page_idx, {'system_zh': '', 'system_en': ''})

    try:
        pil_img = PILImage.open(img_path).convert("RGB")
        w, h = pil_img.size
        if max(w, h) > 1024:
            scale = 1024 / max(w, h)
            pil_img = pil_img.resize((int(w*scale), int(h*scale)), PILImage.LANCZOS)

        messages = [{"role": "user", "content": [
            {"type": "image"}, {"type": "text", "text": OCR_PROMPT}
        ]}]
        text = processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        inputs = processor(
            text=[text], images=[pil_img], return_tensors="pt", padding=True
        ).to("cuda:0")

        with torch.no_grad():
            output_ids = model.generate(**inputs, max_new_tokens=2048, do_sample=False)

        input_len = inputs["input_ids"].shape[1]
        generated = output_ids[0, input_len:]
        response = processor.decode(generated, skip_special_tokens=True).strip()

        del inputs, output_ids, pil_img
        torch.cuda.empty_cache()

        # Parse JSON response
        resp = response
        if resp.startswith('```'):
            lines = resp.split('\n')
            lines = [l for l in lines if not l.strip().startswith('```')]
            resp = '\n'.join(lines)
        parsed = None
        try:
            parsed = json.loads(resp)
        except:
            match = re.search(r'\[.*\]', resp, re.DOTALL)
            if match:
                try:
                    parsed = json.loads(match.group())
                except:
                    pass
        if parsed is None:
            parsed = []
            for line in resp.split('\n'):
                line = line.strip().rstrip(',')
                if line.startswith('{'):
                    try:
                        parsed.append(json.loads(line))
                    except:
                        continue
        if not isinstance(parsed, list):
            parsed = []

        if parsed:
            total_ok += 1
            for row in parsed:
                pn = str(row.get('part_number', '')).strip()
                pname = str(row.get('part_name', '')).strip()
                hotspot = str(row.get('hotspot', '')).strip()
                if pn and pname:
                    total_parts += 1
                    conn.execute(
                        """INSERT INTO parts (part_number, part_name_zh, hotspot_id,
                           system_zh, system_en, subsystem_zh, subsystem_en,
                           page_idx, source_image) VALUES (?,?,?,?,?,?,?,?,?)""",
                        (pn, pname, hotspot, sys_info['system_zh'], sys_info['system_en'],
                         '', '', page_idx, img_rel)
                    )
        else:
            total_empty += 1

        if (i + 1) % 10 == 0:
            conn.commit()

    except Exception as exc:
        total_error += 1
        print(f"  {i+1}/{len(pending)}  ERROR: {exc}", flush=True)
        torch.cuda.empty_cache()
        continue

    elapsed = time.time() - t_start
    rate = (i + 1) / elapsed if elapsed > 0 else 0
    eta = (len(pending) - i - 1) / rate if rate > 0 else 0
    print(
        f"  {i+1}/{len(pending)}  parts={total_parts}  ok={total_ok}  "
        f"empty={total_empty}  err={total_error}  "
        f"{rate:.2f} tbl/s  ETA {eta:.0f}s  [{sys_info['system_en']}]",
        flush=True
    )

conn.commit()
conn.close()

elapsed_total = time.time() - t_start
print(f"\n{'='*60}", flush=True)
print(f"  Done in {elapsed_total:.1f}s ({elapsed_total/60:.1f} min)", flush=True)
print(f"  Tables: {len(pending)} (ok={total_ok}, empty={total_empty}, err={total_error})", flush=True)
print(f"  Parts extracted: {total_parts}", flush=True)
print(f"{'='*60}", flush=True)
'''

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS, timeout=15,
            allow_agent=False, look_for_keys=False)
print(f'Connected to {HOST}')

def run_raw(cmd, timeout=7200):
    """Run command, stream output with raw byte handling."""
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

# Write script inline
print('\nUploading OCR script (inline write, model-first pattern)...')
sftp = ssh.open_sftp()
with sftp.open(f'{PROJECT}\\run_full_ocr.py', 'w') as f:
    f.write(FULL_OCR_SCRIPT)
sftp.close()
print('Script uploaded')

# Run
print('\n=== FULL OCR (352 tables, cuda:0, bfloat16+eager, model-first) ===')
t0 = time.time()
cmd = f'cd /d {PROJECT} && "{PY311}" -u run_full_ocr.py 2>&1'
exit_code = run_raw(cmd, timeout=7200)

elapsed = time.time() - t0
print(f'\nExit code: {exit_code}')
print(f'Total time: {elapsed/60:.1f} minutes')

if exit_code == 0:
    print('\nDownloading kb.db...')
    sftp = ssh.open_sftp()
    remote_db = f'{PROJECT}\\knowledge-base\\kb.db'
    local_db = 'knowledge-base/kb.db'
    stat = sftp.stat(remote_db)
    print(f'  Size: {stat.st_size / (1024**3):.2f} GB')
    sftp.get(remote_db, local_db)
    sftp.close()
    print('  Downloaded!')
else:
    print(f'\nFailed with code {exit_code}')

ssh.close()
print('\nDone!')
