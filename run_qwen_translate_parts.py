"""Translate remaining part names ZH→EN using Qwen2.5-VL-7B (already cached on workstation).
Uses text-only mode (no images) for translation via prompt."""
import paramiko, sys, time, json
sys.stdout.reconfigure(encoding='utf-8')

HOST = '192.168.50.2'
USER = 'baza'
PASS = 'Llcar2024!'
PROJECT = r'C:\LLCAR-Transfer'
PY311 = r'C:\Users\BAZA\AppData\Local\Programs\Python\Python311\python.exe'

# Load parts to translate
with open('scripts/parts_to_translate.json', 'r', encoding='utf-8') as f:
    parts_zh = json.load(f)
print(f'Parts to translate: {len(parts_zh)}')

TRANSLATE_SCRIPT = r'''
import torch, json, sys, time
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
from pathlib import Path

# Load Qwen2.5-VL-7B (already cached, CPU-first load pattern)
from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration

print("Loading Qwen2.5-VL-7B (CPU -> cuda:0)...", flush=True)
t0 = time.time()
processor = AutoProcessor.from_pretrained("Qwen/Qwen2.5-VL-7B-Instruct", use_fast=False)
model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
    "Qwen/Qwen2.5-VL-7B-Instruct",
    torch_dtype=torch.bfloat16,
    trust_remote_code=True,
    low_cpu_mem_usage=True,
    attn_implementation="eager",
)
model = model.to("cuda:0")
model.eval()
print(f"Model loaded in {time.time()-t0:.1f}s, VRAM: {torch.cuda.memory_allocated(0)/1024**3:.1f} GB", flush=True)

BASE = Path(r"C:\LLCAR-Transfer")
with open(BASE / "parts_to_translate.json", "r", encoding="utf-8") as f:
    parts_zh = json.load(f)
print(f"Parts to translate: {len(parts_zh)}", flush=True)

# Translate in batches of 20 names per prompt
BATCH = 20
results = {}
t_start = time.time()

for i in range(0, len(parts_zh), BATCH):
    batch = parts_zh[i:i+BATCH]
    numbered = "\n".join(f"{j+1}. {name}" for j, name in enumerate(batch))

    prompt = f"""Translate these Chinese automotive part names to English. Return ONLY numbered translations, one per line.

{numbered}"""

    messages = [{"role": "user", "content": [{"type": "text", "text": prompt}]}]
    text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = processor(text=[text], return_tensors="pt", padding=True).to("cuda:0")

    with torch.no_grad():
        output_ids = model.generate(**inputs, max_new_tokens=512, do_sample=False)

    input_len = inputs["input_ids"].shape[1]
    generated = output_ids[0, input_len:]
    response = processor.decode(generated, skip_special_tokens=True).strip()

    del inputs, output_ids
    torch.cuda.empty_cache()

    # Parse numbered responses
    lines = response.split("\n")
    for j, name_zh in enumerate(batch):
        # Try to find matching line
        for line in lines:
            line = line.strip()
            # Match "1. Translation" or "1) Translation"
            prefix = f"{j+1}."
            prefix2 = f"{j+1})"
            if line.startswith(prefix):
                en = line[len(prefix):].strip()
                if en:
                    results[name_zh] = en
                break
            elif line.startswith(prefix2):
                en = line[len(prefix2):].strip()
                if en:
                    results[name_zh] = en
                break

    done = min(i + BATCH, len(parts_zh))
    elapsed = time.time() - t_start
    rate = done / elapsed if elapsed > 0 else 0
    eta = (len(parts_zh) - done) / rate if rate > 0 else 0

    if (done // BATCH) % 5 == 0 or done >= len(parts_zh):
        print(f"  {done}/{len(parts_zh)}  translated={len(results)}  {rate:.1f} parts/s  ETA {eta:.0f}s", flush=True)

# Save
with open(BASE / "parts_translations.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\nDone! {len(results)}/{len(parts_zh)} translated in {time.time()-t_start:.1f}s", flush=True)
for zh, en in list(results.items())[:10]:
    print(f"  {zh} → {en}", flush=True)
'''

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS, timeout=15,
            allow_agent=False, look_for_keys=False)
print(f'Connected to {HOST}')

def run_raw(cmd, timeout=3600):
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
                if 'generation flags' in line:
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
time.sleep(3)

# Upload files
print('\nUploading...')
sftp = ssh.open_sftp()
with sftp.open(f'{PROJECT}\\translate_parts.py', 'w') as f:
    f.write(TRANSLATE_SCRIPT)
with sftp.open(f'{PROJECT}\\parts_to_translate.json', 'w') as f:
    f.write(json.dumps(parts_zh, ensure_ascii=False, indent=2))
sftp.close()
print('Files uploaded')

# Run
print('\n=== Qwen2.5-VL Translation (802 parts, ZH→EN) ===')
t0 = time.time()
cmd = f'cd /d {PROJECT} && "{PY311}" -u translate_parts.py 2>&1'
exit_code = run_raw(cmd, timeout=3600)

elapsed = time.time() - t0
print(f'\nExit code: {exit_code}')
print(f'Time: {elapsed:.0f}s ({elapsed/60:.1f} min)')

if exit_code == 0:
    print('\nDownloading translations...')
    sftp = ssh.open_sftp()
    sftp.get(f'{PROJECT}\\parts_translations.json', 'scripts/parts_translations.json')
    sftp.close()

    with open('scripts/parts_translations.json', 'r', encoding='utf-8') as f:
        translations = json.load(f)
    print(f'Got {len(translations)} translations')

    import sqlite3
    conn = sqlite3.connect('knowledge-base/kb.db')
    c = conn.cursor()
    updated = 0
    for zh, en in translations.items():
        if en and en.strip():
            c.execute("UPDATE parts SET part_name_en = ? WHERE part_name_zh = ? AND (part_name_en IS NULL OR part_name_en = '')",
                      (en.strip(), zh))
            updated += c.rowcount
    conn.commit()

    c.execute("SELECT COUNT(*) FROM parts WHERE part_name_en IS NOT NULL AND part_name_en != ''")
    total_en = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM parts")
    total = c.fetchone()[0]
    conn.close()

    print(f'Updated {updated} rows')
    print(f'Final coverage: {total_en}/{total} ({total_en*100//total}%)')
else:
    print(f'Failed with code {exit_code}')

ssh.close()
print('\nDone!')
