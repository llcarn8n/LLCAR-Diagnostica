"""Upload CLAUDE.md to workstation."""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("192.168.50.2", username="baza", password="Llcar2024!")
sftp = ssh.open_sftp()
print("Uploading CLAUDE.md...")
sftp.put("CLAUDE.md", "C:/LLCAR-Transfer/CLAUDE.md")
print("Done")
sftp.close()
ssh.close()
