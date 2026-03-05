"""Run OCR v2: kill stale GPU processes, use device_map=auto for both GPUs."""
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

def run_raw(cmd, timeout=300):
    """Run command, read raw bytes, return (output_str, exit_code)."""
    print(f'\n>>> {cmd[:150]}')
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    channel = stdout.channel
    buf = b''
    lines_out = []
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
                    # Print loading progress every 10%
                    if any(f'{p}%' in line for p in ['10', '20', '30', '40', '50', '60', '70', '80', '90', '100']):
                        print(line[:100], flush=True)
                    continue
                print(line, flush=True)
                lines_out.append(line)
        else:
            time.sleep(0.3)
    if buf:
        line = buf.decode('utf-8', errors='replace').rstrip()
        if line:
            print(line, flush=True)
            lines_out.append(line)
    code = channel.recv_exit_status()
    print(f'Exit: {code}')
    return '\n'.join(lines_out), code

# Step 1: Kill any stale Python processes on GPU
print('=== Step 1: Clean GPU ===')
run_raw('taskkill /f /im python.exe 2>&1 & taskkill /f /im python3.exe 2>&1 & echo cleanup_done', timeout=15)
time.sleep(2)

# Check GPU memory
run_raw('nvidia-smi --query-gpu=index,memory.used,memory.free --format=csv,noheader', timeout=10)

# Step 2: Upload latest script
sftp = ssh.open_sftp()
sftp.put('scripts/ocr_parts_tables.py',
         f'{PROJECT}\\scripts\\ocr_parts_tables.py')
sftp.close()
print('Script uploaded')

# Step 3: Try loading model first as a standalone test
print('\n=== Step 2: Test model load ===')
_, code = run_raw(f'"{PY311}" {PROJECT}\\test_model_load.py', timeout=300)

if code != 0:
    print('Model load test failed! Trying to fix...')
    # Maybe need to clear GPU cache
    run_raw('nvidia-smi --gpu-reset -i 0 2>&1', timeout=15)
    time.sleep(3)
    _, code = run_raw(f'"{PY311}" {PROJECT}\\test_model_load.py', timeout=300)
    if code != 0:
        print('FATAL: Model cannot load. Aborting.')
        ssh.close()
        sys.exit(1)

# Step 4: Run full OCR
print('\n=== Step 3: Full OCR ===')
t0 = time.time()
cmd = f'cd /d {PROJECT} && "{PY311}" -u scripts/ocr_parts_tables.py --device cuda:0 --resume 2>&1'
_, exit_code = run_raw(cmd, timeout=7200)

elapsed = time.time() - t0
print(f'\nTotal time: {elapsed/60:.1f} minutes')

# Download kb.db if successful
if exit_code == 0:
    print('\nDownloading updated kb.db...')
    sftp = ssh.open_sftp()
    remote_db = f'{PROJECT}\\knowledge-base\\kb.db'
    local_db = 'knowledge-base/kb.db'
    stat = sftp.stat(remote_db)
    size_gb = stat.st_size / (1024**3)
    print(f'  Remote kb.db size: {size_gb:.2f} GB')
    sftp.get(remote_db, local_db)
    sftp.close()
    print(f'  kb.db downloaded!')
else:
    print(f'\nOCR failed with code {exit_code}')

ssh.close()
print('\nDone!')
