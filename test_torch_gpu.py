"""Test torch GPU on workstation, then try model loading with different configs."""
import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8')

HOST = '192.168.50.2'
USER = 'baza'
PASS = 'Llcar2024!'
PY311 = r'C:\Users\BAZA\AppData\Local\Programs\Python\Python311\python.exe'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS, timeout=15,
            allow_agent=False, look_for_keys=False)
print('Connected')

def run(cmd, timeout=300):
    print(f'\n>>> {cmd[:200]}')
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    while True:
        line = stdout.readline()
        if not line:
            break
        print(line.rstrip())
    err = stderr.read().decode('utf-8', errors='replace').strip()
    if err:
        lines = [l for l in err.split('\n')
                 if l.strip() and 'HTTP' not in l and 'debug' not in l.lower()]
        if lines:
            print('STDERR:')
            for l in lines[:20]:
                print(f'  {l}')
    code = stdout.channel.recv_exit_status()
    print(f'Exit: {code}')
    return code

# Test 1: Basic CUDA
print('=== Test 1: Basic CUDA ===')
run(f'"{PY311}" -c "import torch; x=torch.randn(1000,1000,device=\'cuda:0\'); print(\'CUDA OK\', x.sum().item())"')

# Test 2: Check model cache
print('\n=== Test 2: Model cache ===')
run(r'dir /s /b C:\Users\BAZA\.cache\huggingface\hub\models--Qwen--Qwen2.5-VL-7B-Instruct\*.safetensors 2>&1 | find /c "."')

# Test 3: Try loading processor only (no GPU, fast)
print('\n=== Test 3: Load processor only ===')
run(f'"{PY311}" -c "from transformers import AutoProcessor; p=AutoProcessor.from_pretrained(\'Qwen/Qwen2.5-VL-7B-Instruct\', use_fast=False); print(\'Processor OK\')"', timeout=120)

# Test 4: Try loading model with float16 + eager attention
print('\n=== Test 4: Model load (float16, eager) ===')
script = r"""
import torch
from transformers import Qwen2_5_VLForConditionalGeneration
print('Loading model...')
model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
    'Qwen/Qwen2.5-VL-7B-Instruct',
    torch_dtype=torch.float16,
    device_map='cuda:0',
    trust_remote_code=True,
    low_cpu_mem_usage=True,
    attn_implementation='eager',
)
model.eval()
print(f'Model loaded! VRAM: {torch.cuda.memory_allocated(0)/1024**3:.1f} GB')
"""

# Write script to workstation
sftp = ssh.open_sftp()
with sftp.open(r'C:\LLCAR-Transfer\test_model_load.py', 'w') as f:
    f.write(script)
sftp.close()

run(f'"{PY311}" C:\\LLCAR-Transfer\\test_model_load.py', timeout=300)

ssh.close()
print('\nDone')
