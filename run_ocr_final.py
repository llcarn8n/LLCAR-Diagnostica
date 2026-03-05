"""Run full OCR on both GPUs (device_map=auto, bfloat16, eager)."""
import paramiko, sys, time
sys.stdout.reconfigure(encoding='utf-8')

HOST = '192.168.50.2'
USER = 'baza'
PASS = 'Llcar2024!'
PROJECT = r'C:\LLCAR-Transfer'
PY311 = r'C:\Users\BAZA\AppData\Local\Programs\Python\Python311\python.exe'

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
time.sleep(2)
run_raw('nvidia-smi --query-gpu=index,memory.used,memory.free --format=csv,noheader', timeout=10)

# Upload new simple script
sftp = ssh.open_sftp()
sftp.put('scripts/ocr_simple.py', f'{PROJECT}\\scripts\\ocr_simple.py')
sftp.close()
print('Script uploaded (ocr_simple.py - bfloat16, eager, max_side=1024)')

# Run full OCR
print('\n=== FULL OCR (351 tables, RTX 3090 cuda:0, ~65 min) ===')
t0 = time.time()
cmd = f'cd /d {PROJECT} && "{PY311}" -u scripts/ocr_simple.py --device cuda:0 --resume 2>&1'
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
