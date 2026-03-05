$out = "C:\diag.txt"
"=== DIAGNOSTICS ===" | Out-File $out

# Username
"USERNAME: $env:USERNAME" | Out-File $out -Append
whoami | Out-File $out -Append

# Set password (complex to meet policy)
$r = net user $env:USERNAME "Llcar2024!" 2>&1
"PASSWORD SET: $r" | Out-File $out -Append

# Key file
$kf = "C:\ProgramData\ssh\administrators_authorized_keys"
"KEY FILE EXISTS: $(Test-Path $kf)" | Out-File $out -Append
"KEY CONTENT:" | Out-File $out -Append
Get-Content $kf 2>&1 | Out-File $out -Append
"KEY PERMS:" | Out-File $out -Append
icacls $kf 2>&1 | Out-File $out -Append

# sshd config
"SSHD CONFIG:" | Out-File $out -Append
Get-Content C:\ProgramData\ssh\sshd_config 2>&1 | Out-File $out -Append

# sshd log
"SSHD LOG:" | Out-File $out -Append
Get-WinEvent -LogName OpenSSH/Operational -MaxEvents 10 2>&1 | Format-List | Out-File $out -Append

# Restart sshd
Restart-Service sshd
"SSHD RESTARTED" | Out-File $out -Append

# Serve it
Write-Host "Diagnostics at C:\diag.txt" -ForegroundColor Green
Get-Content $out
