# Find both NVIDIA GPUs and disable/enable GPU 0 to recover from "lost" state
$gpus = Get-PnpDevice | Where-Object { $_.FriendlyName -like "*GeForce RTX 3090*" }
$gpu0 = $gpus | Select-Object -First 1  # first found = lower bus ID = GPU 0

Write-Host "Resetting: $($gpu0.FriendlyName) [$($gpu0.InstanceId)]"
Write-Host "Status before: $($gpu0.Status)"

Disable-PnpDevice -InstanceId $gpu0.InstanceId -Confirm:$false
Start-Sleep -Seconds 3
Enable-PnpDevice -InstanceId $gpu0.InstanceId -Confirm:$false
Start-Sleep -Seconds 5

$after = (Get-PnpDevice -InstanceId $gpu0.InstanceId).Status
Write-Host "Status after: $after"
