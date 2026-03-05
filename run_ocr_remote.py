"""Run OCR on workstation via SSH using Python 3.11."""
import paramiko
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')

HOST = '192.168.50.2'
USER = 'baza'
PASS = 'Llcar2024!'
PROJECT = 'C:\\LLCAR-Transfer'
PY311 = 'C:\\Users\\BAZA\\AppData\\Local\\Programs\\Python\\Python311\\python.exe'

def run_cmd(ssh, cmd, timeout=600):
    print(f'\n>>> {cmd}')
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    while True:
        line = stdout.readline()
        if not line:
            break
        print(line.rstrip())
    err = stderr.read().decode('utf-8', errors='replace').strip()
    if err:
        # Filter out debug HTTP noise
        lines = [l for l in err.split('\n') if not l.strip().startswith('debug')]
        important = [l for l in lines if l.strip()]
        if important:
            print('STDERR:', '\n'.join(important[:20]))
    return stdout.channel.recv_exit_status()

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=PASS, timeout=15,
                allow_agent=False, look_for_keys=False)
    print(f'Connected to {HOST}')

    # Upload script
    sftp = ssh.open_sftp()
    sftp.put('scripts/ocr_parts_tables.py',
             f'{PROJECT}\\scripts\\ocr_parts_tables.py')
    sftp.close()
    print('Script uploaded')

    # Check Python 3.11 + torch
    run_cmd(ssh, f'"{PY311}" --version')
    run_cmd(ssh, f'"{PY311}" -c "import torch; print(torch.__version__, torch.cuda.is_available())"')

    # Install deps if needed
    run_cmd(ssh, f'"{PY311}" -m pip install Pillow qwen-vl-utils 2>&1 | findstr -v "already satisfied"', timeout=120)

    # Test run: 3 tables, dry-run
    print('\n=== OCR TEST (3 tables, dry-run) ===')
    code = run_cmd(ssh,
        f'cd /d {PROJECT} && "{PY311}" scripts/ocr_parts_tables.py --limit 3 --dry-run --device cuda:0',
        timeout=300
    )
    print(f'\nTest exit code: {code}')

    if code == 0:
        print('\n=== Test passed! Ready for full run. ===')
        answer = input('Run full OCR (351 tables)? [y/N]: ').strip().lower()
        if answer == 'y':
            print('\n=== FULL OCR RUN ===')
            code = run_cmd(ssh,
                f'cd /d {PROJECT} && "{PY311}" scripts/ocr_parts_tables.py --device cuda:0 --resume --output-log ocr_log.jsonl',
                timeout=7200  # 2 hours max
            )
            print(f'\nFull run exit code: {code}')

            # Download updated kb.db
            if code == 0:
                print('\nDownloading kb.db...')
                sftp = ssh.open_sftp()
                sftp.get(f'{PROJECT}\\knowledge-base\\kb.db',
                         'knowledge-base/kb.db')
                sftp.close()
                print('kb.db downloaded!')
    else:
        print(f'\nTest failed with code {code}. Check errors above.')

    ssh.close()

if __name__ == '__main__':
    main()
