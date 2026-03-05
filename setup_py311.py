"""Setup pip for Python 3.11, then install torch + deps on workstation."""
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
        if 'already satisfied' in text.lower():
            continue
        print(text)
    err = stderr.read().decode('utf-8', errors='replace').strip()
    if err:
        lines = [l for l in err.split('\n') if l.strip() and 'already satisfied' not in l.lower()]
        if lines:
            print('STDERR:', '\n'.join(lines[:15]))
    code = stdout.channel.recv_exit_status()
    print(f'Exit: {code}')
    return code

# Step 1: Install pip via ensurepip
print('=== Step 1: Install pip ===')
run(f'"{PY311}" -m ensurepip --upgrade')

# Verify pip
run(f'"{PY311}" -m pip --version')

# Step 2: Upgrade pip
print('\n=== Step 2: Upgrade pip ===')
run(f'"{PY311}" -m pip install --upgrade pip', timeout=120)

# Step 3: Install torch with CUDA 12.4
print('\n=== Step 3: Install PyTorch (cu124) ===')
code = run(
    f'"{PY311}" -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124',
    timeout=600
)
if code != 0:
    print('cu124 failed, trying cu121...')
    code = run(
        f'"{PY311}" -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121',
        timeout=600
    )

# Step 4: Install transformers + deps for OCR
print('\n=== Step 4: Install transformers + deps ===')
run(
    f'"{PY311}" -m pip install transformers accelerate Pillow qwen-vl-utils',
    timeout=300
)

# Step 5: Verify
print('\n=== Step 5: Verify ===')
run(f'"{PY311}" -c "import torch; print(torch.__version__, torch.cuda.is_available())"')
run(f'"{PY311}" -c "import transformers; print(transformers.__version__)"')

ssh.close()
print('\nDone')
