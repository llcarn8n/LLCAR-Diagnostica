"""Check retry progress on workstation."""
import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("192.168.50.2", username="baza", password="Llcar2024!")

PY = r"C:\Users\BAZA\AppData\Local\Programs\Python\Python311\python.exe"

# Check if reocr process is running
stdin, stdout, stderr = ssh.exec_command('tasklist /fi "imagename eq python.exe" /fo csv')
out = stdout.read().decode("utf-8", errors="replace")
python_procs = [l for l in out.strip().split("\n") if "python" in l.lower()]
print(f"Python processes running: {len(python_procs)}")
for p in python_procs:
    print(f"  {p}")

# Check retry log
stdin, stdout, stderr = ssh.exec_command(
    f'"{PY}" -c "'
    'import json, os; '
    'p = r\"C:\\LLCAR-Transfer\\reocr_retry.jsonl\"; '
    'exists = os.path.exists(p); '
    'print(f\"Log exists: {exists}\"); '
    'lines = open(p, encoding=\"utf-8\").readlines() if exists else []; '
    'print(f\"Entries: {len(lines)}\"); '
    'succ = sum(1 for l in lines if json.loads(l).get(\"ocr_count\", 0) > 0); '
    'total_new = sum(json.loads(l).get(\"new_count\", 0) for l in lines); '
    'print(f\"Successful: {succ}\"); '
    'print(f\"New parts: {total_new}\"); '
    '"'
)
out = stdout.read().decode("utf-8", errors="replace")
err = stderr.read().decode("utf-8", errors="replace")
print(out)
if err:
    print("ERR:", err[:300])

ssh.close()
