"""Install torch + transformers for Python 3.11 on workstation."""
import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8')

HOST = '192.168.50.2'
USER = 'baza'
PASS = 'Llcar2024!'
PY311 = r'C:\Users\BAZA\AppData\Local\Programs\Python\Python311\python.exe'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS, timeout=10,
            allow_agent=False, look_for_keys=False)
print('Connected')

def run(cmd, timeout=600):
    print(f'\n>>> {cmd}')
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    while True:
        line = stdout.readline()
        if not line:
            break
        text = line.rstrip()
        # Skip "already satisfied" spam
        if 'already satisfied' in text.lower():
            continue
        print(text)
    err = stderr.read().decode('utf-8', errors='replace').strip()
    if err:
        lines = [l for l in err.split('\n') if l.strip() and 'already satisfied' not in l.lower()]
        if lines:
            print('STDERR:', '\n'.join(lines[:10]))
    code = stdout.channel.recv_exit_status()
    print(f'Exit: {code}')
    return code

# Check nvidia-smi for CUDA version
run('nvidia-smi --query-gpu=name,driver_version --format=csv,noheader')

# Install torch with CUDA (use same cu130 as Python 3.14 had)
# First check what pip index URLs are available
run(f'"{PY311}" -m pip install --upgrade pip', timeout=120)

# Install torch - try cu124 first (more stable), then cu130
# RTX 3090 needs at least CUDA 11.1, but cu124 is safest for 3.11
print('\n=== Installing PyTorch ===')
code = run(
    f'"{PY311}" -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124',
    timeout=600
)

if code != 0:
    print('\ncu124 failed, trying cu121...')
    code = run(
        f'"{PY311}" -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121',
        timeout=600
    )

# Install transformers + other deps
print('\n=== Installing transformers + deps ===')
run(
    f'"{PY311}" -m pip install transformers accelerate Pillow qwen-vl-utils',
    timeout=300
)

# Verify
print('\n=== Verification ===')
run(f'"{PY311}" -c "import torch; print(f\'torch={{torch.__version__}}, cuda={{torch.cuda.is_available()}}\')"')
run(f'"{PY311}" -c "import transformers; print(f\'transformers={{transformers.__version__}}\')"')

ssh.close()
print('\nDone')
