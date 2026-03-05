$key = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAINTS0u3kdyyyBPYO92f24uvR8AFj5v6ZRu0U2Y/PI8M/"
$file = "C:\ProgramData\ssh\administrators_authorized_keys"
Set-Content -Path $file -Value $key -Encoding ASCII
icacls $file /inheritance:r /grant "SYSTEM:(R)" /grant "Administrators:(R)"
Restart-Service sshd
Write-Host "SSH key installed, sshd restarted" -ForegroundColor Green
