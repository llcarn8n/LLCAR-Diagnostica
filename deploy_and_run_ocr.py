"""Deploy ocr_parts_tables.py to workstation and run it via SSH."""
import paramiko
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')

HOST = '192.168.50.2'
USER = 'baza'
PASS = 'Llcar2024!'
REMOTE_PROJECT = 'D:\\LLCAR-Transfer'

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=PASS, timeout=15,
                allow_agent=False, look_for_keys=False)
    print(f'Connected to {HOST}')

    # Upload ocr_parts_tables.py via SFTP
    sftp = ssh.open_sftp()
    local_script = 'scripts/ocr_parts_tables.py'
    remote_script = f'{REMOTE_PROJECT}\\scripts\\ocr_parts_tables.py'
    print(f'Uploading {local_script} -> {remote_script}')
    sftp.put(local_script, remote_script)
    sftp.close()
    print('Upload done')

    # Check if Qwen2.5-VL is cached
    print('\nChecking if Qwen2.5-VL-7B is cached...')
    stdin, stdout, stderr = ssh.exec_command(
        'dir /s /b C:\\Users\\BAZA\\.cache\\huggingface\\hub\\models--Qwen--Qwen2.5-VL-7B-Instruct 2>&1 | find /c "."',
        timeout=30
    )
    count = stdout.read().decode().strip()
    print(f'  Cached files: {count}')

    # Run with --limit 5 first as test
    print('\n=== Running OCR test (5 tables) ===')
    cmd = (
        f'cd /d {REMOTE_PROJECT} && '
        f'python scripts/ocr_parts_tables.py --limit 5 --dry-run --device cuda:0 -v'
    )
    print(f'CMD: {cmd}\n')

    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=600)

    # Stream output
    while True:
        line = stdout.readline()
        if not line:
            break
        print(line.rstrip())

    err = stderr.read().decode('utf-8', errors='replace')
    if err:
        print(f'\nSTDERR:\n{err}')

    exit_code = stdout.channel.recv_exit_status()
    print(f'\nExit code: {exit_code}')

    ssh.close()

if __name__ == '__main__':
    main()
