import paramiko, sys, os
sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.50.2', username='baza', password='Llcar2024!',
            timeout=10, allow_agent=False, look_for_keys=False)

cmds = [
    'whoami',
    'hostname',
    'nvidia-smi --query-gpu=name,memory.total --format=csv,noheader',
    'dir D:\\LLCAR',
    'python --version',
]
for cmd in cmds:
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=15)
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    print(f'=== {cmd} ===')
    if out: print(out)
    if err: print(f'ERR: {err}')
    print()

ssh.close()
print('SSH OK!')
