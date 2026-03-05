"""Run full OCR on all 351 tables on workstation, then download kb.db."""
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

# Upload latest script
sftp = ssh.open_sftp()
sftp.put('scripts/ocr_parts_tables.py',
         f'{PROJECT}\\scripts\\ocr_parts_tables.py')
sftp.close()
print('Script uploaded')

# Run full OCR with --resume (skip already processed)
print('\n=== FULL OCR RUN (351 tables) ===')
t0 = time.time()
cmd = f'cd /d {PROJECT} && "{PY311}" -u scripts/ocr_parts_tables.py --device cuda:0 --resume 2>&1'
print(f'CMD: {cmd}\n')

stdin, stdout, stderr = ssh.exec_command(cmd, timeout=7200)

# Read raw bytes from channel to avoid encoding issues
channel = stdout.channel
buf = b''
last_status = time.time()
while not channel.exit_status_ready() or channel.recv_ready():
    if channel.recv_ready():
        data = channel.recv(4096)
        buf += data
        # Process complete lines
        while b'\n' in buf:
            line_bytes, buf = buf.split(b'\n', 1)
            line = line_bytes.decode('utf-8', errors='replace').rstrip()
            # Filter HTTP noise
            if 'HTTP Request' in line or 'HTTP/1.1' in line:
                continue
            print(line, flush=True)
    else:
        time.sleep(0.5)
        # Print elapsed every 5 min
        now = time.time()
        if now - last_status > 300:
            elapsed = now - t0
            print(f'  [{elapsed/60:.0f} min elapsed]', flush=True)
            last_status = now

# Flush remaining buffer
if buf:
    line = buf.decode('utf-8', errors='replace').rstrip()
    if line and 'HTTP' not in line:
        print(line, flush=True)

exit_code = channel.recv_exit_status()
elapsed = time.time() - t0
print(f'\nExit code: {exit_code}')
print(f'Total time: {elapsed/60:.1f} minutes')

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
    print(f'  kb.db downloaded to {local_db}!')
else:
    print(f'\nOCR failed with code {exit_code}')

ssh.close()
print('\nDone!')
