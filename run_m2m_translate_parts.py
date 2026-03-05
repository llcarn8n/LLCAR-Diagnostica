"""Translate remaining part names ZH→EN using M2M model on workstation GPU."""
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
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer

BASE = Path(r"C:\LLCAR-Transfer")

# Load parts to translate
with open(BASE / "parts_to_translate.json", "r", encoding="utf-8") as f:
    parts_zh = json.load(f)
print(f"Parts to translate: {len(parts_zh)}", flush=True)

# Try fine-tuned model first, fall back to base
model_name = "Petr117/m2m-diagnostica-automotive"
try:
    print(f"Loading {model_name}...", flush=True)
    tokenizer = M2M100Tokenizer.from_pretrained(model_name)
    model = M2M100ForConditionalGeneration.from_pretrained(model_name)
except Exception as e:
    print(f"Fine-tuned model failed: {e}", flush=True)
    model_name = "utrobinmv/m2m_translate_en_ru_zh_large_4096"
    print(f"Falling back to {model_name}...", flush=True)
    tokenizer = M2M100Tokenizer.from_pretrained(model_name)
    model = M2M100ForConditionalGeneration.from_pretrained(model_name)

model = model.to("cuda:0")
model.eval()
print(f"Model loaded on GPU", flush=True)

# Translate in batches
tokenizer.src_lang = "zh"
BATCH_SIZE = 16
results = {}
t0 = time.time()

for i in range(0, len(parts_zh), BATCH_SIZE):
    batch = parts_zh[i:i+BATCH_SIZE]
    inputs = tokenizer(batch, return_tensors="pt", padding=True, truncation=True, max_length=128).to("cuda:0")

    with torch.no_grad():
        generated = model.generate(
            **inputs,
            forced_bos_token_id=tokenizer.get_lang_id("en"),
            max_new_tokens=64,
            num_beams=4,
            do_sample=False,
        )

    translations = tokenizer.batch_decode(generated, skip_special_tokens=True)
    for zh, en in zip(batch, translations):
        results[zh] = en.strip()

    if (i // BATCH_SIZE + 1) % 10 == 0 or i + BATCH_SIZE >= len(parts_zh):
        elapsed = time.time() - t0
        done = min(i + BATCH_SIZE, len(parts_zh))
        rate = done / elapsed if elapsed > 0 else 0
        eta = (len(parts_zh) - done) / rate if rate > 0 else 0
        print(f"  {done}/{len(parts_zh)}  {rate:.1f} parts/s  ETA {eta:.0f}s", flush=True)

# Save results
with open(BASE / "parts_translations.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\nDone! Translated {len(results)} parts in {time.time()-t0:.1f}s", flush=True)
# Show samples
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

# Upload translate script
with sftp.open(f'{PROJECT}\\translate_parts.py', 'w') as f:
    f.write(TRANSLATE_SCRIPT)

# Upload parts list
with sftp.open(f'{PROJECT}\\parts_to_translate.json', 'w') as f:
    f.write(json.dumps(parts_zh, ensure_ascii=False, indent=2))

sftp.close()
print('Files uploaded')

# Run translation
print('\n=== M2M Translation (802 unique parts, ZH→EN) ===')
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

    # Apply to DB
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
