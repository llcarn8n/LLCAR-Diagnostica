$ErrorActionPreference = "Continue"
$IP = "192.168.50.2"

Write-Host "=== WORKSTATION SETUP ($IP) ===" -ForegroundColor Cyan

$a = Get-NetAdapter | Where-Object { $_.PhysicalMediaType -match "802.3" -and $_.InterfaceDescription -notmatch "Virtual|Hyper-V|VMware|WSL" } | Select-Object -First 1
if (-not $a) { Write-Host "ERROR: No Ethernet adapter!" -ForegroundColor Red; exit 1 }
Write-Host "[1/7] Adapter: $($a.Name) - $($a.Status)" -ForegroundColor Green

Get-NetIPAddress -InterfaceIndex $a.ifIndex -AddressFamily IPv4 -ErrorAction SilentlyContinue | Remove-NetIPAddress -Confirm:$false -ErrorAction SilentlyContinue
Set-NetIPInterface -InterfaceIndex $a.ifIndex -Dhcp Disabled -ErrorAction SilentlyContinue
Write-Host "[2/7] Old IP removed" -ForegroundColor Green

New-NetIPAddress -InterfaceIndex $a.ifIndex -IPAddress $IP -PrefixLength 24 | Out-Null
Write-Host "[3/7] IP $IP/24 set" -ForegroundColor Green

Set-NetConnectionProfile -InterfaceIndex $a.ifIndex -NetworkCategory Private -ErrorAction SilentlyContinue
Write-Host "[4/7] Profile: Private" -ForegroundColor Green

Remove-NetFirewallRule -DisplayName "LLCAR-Ethernet-In" -ErrorAction SilentlyContinue
Remove-NetFirewallRule -DisplayName "LLCAR-Ethernet-Out" -ErrorAction SilentlyContinue
Remove-NetFirewallRule -DisplayName "LLCAR-Ethernet-ICMP" -ErrorAction SilentlyContinue
Remove-NetFirewallRule -DisplayName "LLCAR-SSH" -ErrorAction SilentlyContinue
New-NetFirewallRule -DisplayName "LLCAR-Ethernet-In" -Direction Inbound -Action Allow -RemoteAddress 192.168.50.0/24 -Profile Any -Enabled True | Out-Null
New-NetFirewallRule -DisplayName "LLCAR-Ethernet-Out" -Direction Outbound -Action Allow -RemoteAddress 192.168.50.0/24 -Profile Any -Enabled True | Out-Null
New-NetFirewallRule -DisplayName "LLCAR-Ethernet-ICMP" -Protocol ICMPv4 -IcmpType 8 -Direction Inbound -Action Allow -Profile Any -Enabled True | Out-Null
Write-Host "[5/7] Firewall: allowed all for 192.168.50.0/24" -ForegroundColor Green

$ssh = Get-WindowsCapability -Online | Where-Object Name -like 'OpenSSH.Server*'
if ($ssh.State -ne 'Installed') {
    Write-Host "[6/7] Installing OpenSSH Server..." -ForegroundColor Yellow
    Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0 | Out-Null
}
Set-Service -Name sshd -StartupType Automatic -ErrorAction SilentlyContinue
Start-Service sshd -ErrorAction SilentlyContinue
New-NetFirewallRule -DisplayName "LLCAR-SSH" -Direction Inbound -Action Allow -Protocol TCP -LocalPort 22 -Profile Any -Enabled True -ErrorAction SilentlyContinue | Out-Null
Write-Host "[6/7] OpenSSH Server: running, port 22 open" -ForegroundColor Green

Start-Sleep -Seconds 3
$check = Get-NetIPAddress -InterfaceIndex $a.ifIndex -AddressFamily IPv4
Write-Host "[7/7] Current IP: $($check.IPAddress)" -ForegroundColor Cyan
Write-Host "=== DONE ===" -ForegroundColor Yellow
