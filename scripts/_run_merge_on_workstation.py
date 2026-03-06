"""Upload merge + reindex scripts to workstation and run them."""
import paramiko
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")

HOST = "192.168.50.2"
USER = "baza"
PASS = "Llcar2024!"
PY = "C:/Users/BAZA/AppData/Local/Programs/Python/Python311/python.exe"
REMOTE_DIR = "C:/LLCAR-Transfer/scripts"

SCRIPTS = [
    "merge_fragments.py",
    "reindex_colbert.py",
]


def upload_scripts(sftp):
    import os
    local_dir = os.path.dirname(os.path.abspath(__file__))
    for script in SCRIPTS:
        local = os.path.join(local_dir, script)
        remote = f"{REMOTE_DIR}/{script}"
        print(f"Uploading {script}...")
        sftp.put(local, remote)
    print("Upload complete.\n")


def run_command(client, cmd, timeout=600):
    print(f"Running: {cmd}\n")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    # Read all output as bytes, decode with fallback
    out_bytes = stdout.read()
    err_bytes = stderr.read()
    out_text = out_bytes.decode("utf-8", errors="replace")
    err_text = err_bytes.decode("utf-8", errors="replace")
    if out_text.strip():
        print(out_text.rstrip())
    if err_text.strip():
        print("STDERR:", err_text[:1000])
    return stdout.channel.recv_exit_status()


def main():
    dry_run = "--dry-run" in sys.argv

    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"Connecting to {HOST}...")
    c.connect(HOST, username=USER, password=PASS)
    print("Connected.\n")

    # Upload scripts
    sftp = c.open_sftp()
    upload_scripts(sftp)
    sftp.close()

    # Step 1: Backup kb.db
    print("=== Step 1: Backup ===")
    run_command(c, 'cmd.exe /c copy "C:\\LLCAR-Transfer\\knowledge-base\\kb.db" "C:\\LLCAR-Transfer\\knowledge-base\\kb.db.backup-pre-merge" /Y')

    # Step 2: Add merged_from column if not exists
    print("\n=== Step 2: Ensure schema ===")
    add_col = f'{PY} -c "import sqlite3; c=sqlite3.connect(\'C:/LLCAR-Transfer/knowledge-base/kb.db\'); c.execute(\'ALTER TABLE chunks ADD COLUMN merged_from TEXT\'); c.commit(); print(\'Added merged_from column\')"'
    run_command(c, add_col)  # may fail if column exists — that's OK

    # Step 3: Run merge
    print("\n=== Step 3: Merge fragments ===")
    merge_flag = "--dry-run" if dry_run else ""
    merge_cmd = f"set KB_DB_PATH=C:/LLCAR-Transfer/knowledge-base/kb.db && {PY} {REMOTE_DIR}/merge_fragments.py {merge_flag}"
    rc = run_command(c, merge_cmd, timeout=300)
    if rc != 0:
        print(f"\nMerge failed with exit code {rc}")
        c.close()
        return

    if dry_run:
        print("\n(Dry run — skipping ColBERT re-encoding)")
        c.close()
        return

    # Step 4: ColBERT re-encoding
    print("\n=== Step 4: ColBERT re-encoding ===")
    reindex_cmd = f"set KB_DB_PATH=C:/LLCAR-Transfer/knowledge-base/kb.db && {PY} {REMOTE_DIR}/reindex_colbert.py --device cuda:0"
    rc = run_command(c, reindex_cmd, timeout=600)
    if rc != 0:
        print(f"\nReindex failed with exit code {rc}")

    print("\n=== Done! ===")
    c.close()


if __name__ == "__main__":
    main()
