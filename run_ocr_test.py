"""Test OCR: upload script, run 3 tables dry-run on workstation."""
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

# Upload latest ocr_parts_tables.py
sftp = ssh.open_sftp()
sftp.put('scripts/ocr_parts_tables.py',
         f'{PROJECT}\\scripts\\ocr_parts_tables.py')
sftp.close()
print('Script uploaded')

# Run test: 3 tables, dry-run
print('\n=== OCR TEST (3 tables, dry-run) ===')
cmd = f'cd /d {PROJECT} && "{PY311}" scripts/ocr_parts_tables.py --limit 3 --dry-run --device cuda:0'
print(f'CMD: {cmd}\n')

stdin, stdout, stderr = ssh.exec_command(cmd, timeout=600)

# Stream stdout
while True:
    line = stdout.readline()
    if not line:
        break
    print(line.rstrip())

err = stderr.read().decode('utf-8', errors='replace').strip()
if err:
    # Filter noise
    lines = [l for l in err.split('\n')
             if l.strip() and not l.strip().startswith('debug')]
    if lines:
        print('\nSTDERR (filtered):')
        for l in lines[:30]:
            print(f'  {l}')

exit_code = stdout.channel.recv_exit_status()
print(f'\nExit code: {exit_code}')

ssh.close()
