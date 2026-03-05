"""Quick check: workstation files + Python 3.11 + torch."""
import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8')

HOST = '192.168.50.2'
USER = 'baza'
PASS = 'Llcar2024!'
PY311 = r'C:\Users\BAZA\AppData\Local\Programs\Python\Python311\python.exe'
PROJECT = r'C:\LLCAR-Transfer'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    ssh.connect(HOST, username=USER, password=PASS, timeout=10,
                allow_agent=False, look_for_keys=False)
    print('SSH OK')
except Exception as e:
    print(f'SSH FAILED: {e}')
    sys.exit(1)

cmds = [
    f'"{PY311}" --version',
    f'"{PY311}" -c "import torch; print(torch.__version__, torch.cuda.is_available())"',
    f'dir {PROJECT} /w',
    f'dir {PROJECT}\\scripts /w',
    f'if exist {PROJECT}\\knowledge-base\\kb.db (echo kb.db: YES) else (echo kb.db: NO)',
    f'dir /s /b {PROJECT}\\mineru-output\\*content_list.json 2>&1',
    f'dir /s /b {PROJECT}\\mineru-output\\*.jpg 2>&1 | find /c ".jpg"',
]

for cmd in cmds:
    print(f'\n>>> {cmd}')
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    if out:
        print(out)
    if err and not err.startswith('debug'):
        # Truncate long errors
        print(f'ERR: {err[:300]}')

ssh.close()
print('\nDone')
