$ErrorActionPreference = "Continue"

# 1. Set password for BAZA
net user BAZA baza
Write-Host "[1] Password set" -ForegroundColor Green

# 2. Write key file
$keyFile = "C:\ProgramData\ssh\administrators_authorized_keys"
$key = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAINTS0u3kdyyyBPYO92f24uvR8AFj5v6ZRu0U2Y/PI8M/"
[System.IO.File]::WriteAllText($keyFile, $key + "`n")
Write-Host "[2] Key written" -ForegroundColor Green

# 3. Fix permissions using takeown + icacls with SIDs
takeown /F $keyFile
icacls $keyFile /reset
icacls $keyFile /inheritance:r
icacls $keyFile /grant "*S-1-5-18:(R)"
icacls $keyFile /grant "*S-1-5-32-544:(R)"
icacls $keyFile /remove "Everyone"
icacls $keyFile /remove "Users"
icacls $keyFile /remove "Authenticated Users"
Write-Host "[3] Permissions fixed" -ForegroundColor Green

# 4. Show result
Write-Host "File contents:" -ForegroundColor Cyan
Get-Content $keyFile
Write-Host "Permissions:" -ForegroundColor Cyan
icacls $keyFile

# 5. Restart sshd
Restart-Service sshd
Write-Host "[5] sshd restarted" -ForegroundColor Green
Write-Host "ALL DONE" -ForegroundColor Yellow
