"""Fix GPU state: reset GPU, try cuda:1, check system RAM."""
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

def run_raw(cmd, timeout=600):
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
                if 'Loading weights' in line and 'it/s' in line:
                    if any(f' {p}%' in line for p in ['25', '50', '75', '100']):
                        print(line[:120], flush=True)
                    continue
                if 'Fetching' in line and 'files' in line:
                    continue
                if 'HTTP Request' in line or 'HTTP/1.1' in line:
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

# Step 1: Check system state
print('=== Checking system state ===')
run_raw('taskkill /f /im python.exe 2>&1 & echo done', timeout=15)
time.sleep(3)

# Full nvidia-smi
run_raw('nvidia-smi', timeout=10)

# System RAM
run_raw('wmic OS get FreePhysicalMemory,TotalVisibleMemorySize /format:list 2>&1', timeout=10)

# Try GPU reset
print('\n=== Attempting GPU reset ===')
run_raw('nvidia-smi --gpu-reset -i 0 2>&1', timeout=30)
time.sleep(5)
run_raw('nvidia-smi --gpu-reset -i 1 2>&1', timeout=30)
time.sleep(5)
run_raw('nvidia-smi --query-gpu=index,memory.used,memory.free,gpu_bus_id --format=csv,noheader', timeout=10)

# Step 2: Try loading on cuda:1 instead
print('\n=== TEST: Load model on cuda:1 ===')
CUDA1_SCRIPT = r'''
import torch, sys, time
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

print(f"Python: {sys.version}", flush=True)
print(f"Torch: {torch.__version__}", flush=True)
print(f"CUDA available: {torch.cuda.is_available()}", flush=True)
print(f"GPU count: {torch.cuda.device_count()}", flush=True)
for i in range(torch.cuda.device_count()):
    print(f"  GPU {i}: {torch.cuda.get_device_name(i)}", flush=True)

# Quick CUDA test on both GPUs
for dev in ['cuda:0', 'cuda:1']:
    try:
        x = torch.randn(1000, 1000, device=dev)
        y = x @ x.T
        print(f"  CUDA test {dev}: OK (result shape {y.shape})", flush=True)
        del x, y
        torch.cuda.empty_cache()
    except Exception as e:
        print(f"  CUDA test {dev}: FAIL - {e}", flush=True)

# System RAM
import os
import ctypes

class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [
        ("dwLength", ctypes.c_ulong),
        ("dwMemoryLoad", ctypes.c_ulong),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]

stat = MEMORYSTATUSEX()
stat.dwLength = ctypes.sizeof(stat)
ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
print(f"\nSystem RAM: {stat.ullTotalPhys / (1024**3):.1f} GB total, {stat.ullAvailPhys / (1024**3):.1f} GB free", flush=True)
print(f"Page file: {stat.ullTotalPageFile / (1024**3):.1f} GB total, {stat.ullAvailPageFile / (1024**3):.1f} GB free", flush=True)
print(f"Memory load: {stat.dwMemoryLoad}%", flush=True)

# Try model load on cuda:1
print("\nLoading model on cuda:1...", flush=True)
from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration

t0 = time.time()
processor = AutoProcessor.from_pretrained("Qwen/Qwen2.5-VL-7B-Instruct", use_fast=False)
model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
    "Qwen/Qwen2.5-VL-7B-Instruct",
    torch_dtype=torch.bfloat16,
    device_map="cuda:1",
    trust_remote_code=True,
    low_cpu_mem_usage=True,
    attn_implementation="eager",
)
model.eval()
vram = torch.cuda.memory_allocated(1) / 1024**3
print(f"SUCCESS on cuda:1: {time.time()-t0:.1f}s, VRAM: {vram:.1f} GB", flush=True)
print("PASSED", flush=True)
'''

sftp = ssh.open_sftp()
with sftp.open(f'{PROJECT}\\test_load.py', 'w') as f:
    f.write(CUDA1_SCRIPT)
sftp.close()

time.sleep(3)
cmd = f'cd /d {PROJECT} && "{PY311}" -u test_load.py 2>&1'
code = run_raw(cmd, timeout=300)
print(f'Exit code: {code}')

ssh.close()
print('\nDone!')
