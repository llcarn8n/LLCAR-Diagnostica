"""Run reocr_missing_parts.py on workstation via SSH."""
import paramiko
import sys

HOST = "192.168.50.2"
USER = "baza"
PASS = "Llcar2024!"
PY311 = r"C:\Users\BAZA\AppData\Local\Programs\Python\Python311\python.exe"
PROJECT = r"C:\LLCAR-Transfer"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS)

cmd = f'cd /d {PROJECT} && "{PY311}" -u scripts/reocr_missing_parts.py --device cuda:0 --output-log reocr_full.jsonl'
print(f"Running on {HOST}: {cmd}")
print("=" * 70)

transport = ssh.get_transport()
channel = transport.open_session()
channel.set_combine_stderr(True)
channel.exec_command(cmd)

while True:
    if channel.recv_ready():
        data = channel.recv(4096)
        if not data:
            break
        sys.stdout.buffer.write(data)
        sys.stdout.buffer.flush()
    elif channel.exit_status_ready():
        # Drain remaining
        while channel.recv_ready():
            data = channel.recv(4096)
            sys.stdout.buffer.write(data)
            sys.stdout.buffer.flush()
        break

exit_code = channel.recv_exit_status()
print(f"\nExit code: {exit_code}")
ssh.close()
