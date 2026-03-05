$key = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAINTS0u3kdyyyBPYO92f24uvR8AFj5v6ZRu0U2Y/PI8M/"
$file = "C:\ProgramData\ssh\administrators_authorized_keys"
[System.IO.File]::WriteAllText($file, $key)
$acl = New-Object System.Security.AccessControl.FileSecurity
$acl.SetAccessRuleProtection($true, $false)
$acl.AddAccessRule((New-Object System.Security.AccessControl.FileSystemAccessRule("SYSTEM","Read","Allow")))
$acl.AddAccessRule((New-Object System.Security.AccessControl.FileSystemAccessRule([System.Security.Principal.SecurityIdentifier]::new("S-1-5-32-544"),"Read","Allow")))
Set-Acl $file $acl
Restart-Service sshd
Write-Host "DONE" -ForegroundColor Green
