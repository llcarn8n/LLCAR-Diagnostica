"""Upload kb.db to workstation."""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("192.168.50.2", username="baza", password="Llcar2024!")
sftp = ssh.open_sftp()
print("Uploading kb.db...")
sftp.put("knowledge-base/kb.db", "C:/LLCAR-Transfer/knowledge-base/kb.db")
print("Done")
sftp.close()
ssh.close()
