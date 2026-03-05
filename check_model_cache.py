"""Check model cache integrity and optionally re-download."""
import paramiko, sys, time
sys.stdout.reconfigure(encoding='utf-8')

HOST = '192.168.50.2'
USER = 'baza'
PASS = 'Llcar2024!'
PROJECT = r'C:\LLCAR-Transfer'
PY311 = r'C:\Users\BAZA\AppData\Local\Programs\Python\Python311\python.exe'

CHECK_SCRIPT = r'''
import sys, os, hashlib
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
from pathlib import Path

# Find model cache
cache_base = Path(os.path.expanduser("~")) / ".cache" / "huggingface" / "hub"
model_dir = cache_base / "models--Qwen--Qwen2.5-VL-7B-Instruct"

print(f"Cache base: {cache_base}", flush=True)
print(f"Model dir: {model_dir}", flush=True)
print(f"Exists: {model_dir.exists()}", flush=True)

if not model_dir.exists():
    print("ERROR: Model not cached!", flush=True)
    exit(1)

# List snapshots
snapshots = model_dir / "snapshots"
if snapshots.exists():
    for snap in sorted(snapshots.iterdir()):
        print(f"\nSnapshot: {snap.name}", flush=True)
        safetensors = sorted(snap.glob("*.safetensors"))
        print(f"  Safetensors files: {len(safetensors)}", flush=True)
        for st in safetensors:
            size_mb = st.stat().st_size / (1024**2)
            print(f"    {st.name}: {size_mb:.1f} MB", flush=True)

        # Check all important files
        for f in sorted(snap.iterdir()):
            if f.is_file():
                size = f.stat().st_size
                if size < 1024*1024:
                    print(f"    {f.name}: {size} bytes", flush=True)

# Also check blobs
blobs = model_dir / "blobs"
if blobs.exists():
    blob_files = sorted(blobs.iterdir())
    print(f"\nBlobs: {len(blob_files)} files", flush=True)
    total = sum(b.stat().st_size for b in blob_files if b.is_file())
    print(f"  Total size: {total / (1024**3):.2f} GB", flush=True)

# Try to validate safetensors files by loading headers
print("\n=== Validating safetensors files ===", flush=True)
try:
    from safetensors import safe_open
    for snap in sorted(snapshots.iterdir()):
        safetensors = sorted(snap.glob("*.safetensors"))
        for st in safetensors:
            try:
                with safe_open(str(st), framework="pt") as f:
                    keys = f.keys()
                    print(f"  {st.name}: OK ({len(keys)} tensors)", flush=True)
            except Exception as e:
                print(f"  {st.name}: CORRUPT - {e}", flush=True)
except ImportError:
    print("  safetensors package not installed, trying manual check...", flush=True)
    import json, struct
    for snap in sorted(snapshots.iterdir()):
        safetensors_files = sorted(snap.glob("*.safetensors"))
        for st in safetensors_files:
            try:
                with open(st, 'rb') as f:
                    # Read header length (first 8 bytes, little-endian uint64)
                    header_len_bytes = f.read(8)
                    header_len = struct.unpack('<Q', header_len_bytes)[0]
                    if header_len > 100_000_000:  # >100MB header = corrupt
                        print(f"  {st.name}: CORRUPT (header_len={header_len})", flush=True)
                        continue
                    header_bytes = f.read(header_len)
                    header = json.loads(header_bytes)
                    # Count tensor entries (exclude __metadata__)
                    tensors = {k: v for k, v in header.items() if k != '__metadata__'}
                    print(f"  {st.name}: OK ({len(tensors)} tensors, header={header_len} bytes)", flush=True)
            except Exception as e:
                print(f"  {st.name}: ERROR - {e}", flush=True)

# Check transformers version
print("\n=== Package versions ===", flush=True)
import torch
print(f"torch: {torch.__version__}", flush=True)
try:
    import transformers
    print(f"transformers: {transformers.__version__}", flush=True)
except:
    print("transformers: NOT INSTALLED", flush=True)
try:
    import accelerate
    print(f"accelerate: {accelerate.__version__}", flush=True)
except:
    print("accelerate: NOT INSTALLED", flush=True)

print("\nDONE", flush=True)
'''

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS, timeout=15,
            allow_agent=False, look_for_keys=False)
print(f'Connected to {HOST}')

def run_raw(cmd, timeout=120):
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
                print(line, flush=True)
        else:
            time.sleep(0.3)
    if buf:
        print(buf.decode('utf-8', errors='replace').rstrip(), flush=True)
    return channel.recv_exit_status()

sftp = ssh.open_sftp()
with sftp.open(f'{PROJECT}\\check_cache.py', 'w') as f:
    f.write(CHECK_SCRIPT)
sftp.close()

cmd = f'cd /d {PROJECT} && "{PY311}" -u check_cache.py 2>&1'
run_raw(cmd, timeout=120)

ssh.close()
print('\nDone!')
