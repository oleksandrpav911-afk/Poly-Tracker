# Script for automatic startup configuration with Task Scheduler
# Run as Administrator

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Auto-start Setup - Polymarket Monitors" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonPath = (Get-Command python).Source
$monitorPositions = Join-Path $scriptPath "monitor_positions.py"
$monitorTrades = Join-Path $scriptPath "telegram_monitor.py"

Write-Host "Python Path: $pythonPath" -ForegroundColor Yellow
Write-Host "Scripts Path: $scriptPath" -ForegroundColor Yellow
Write-Host ""

# Create Task for monitor_positions
Write-Host "Creating Task for Monitor Positions..." -ForegroundColor Green
$action1 = New-ScheduledTaskAction -Execute $pythonPath -Argument "`"$monitorPositions`"" -WorkingDirectory $scriptPath
$trigger1 = New-ScheduledTaskTrigger -AtStartup
$principal1 = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Highest
$settings1 = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)

Register-ScheduledTask -TaskName "Polymarket Monitor Positions" `
    -Action $action1 `
    -Trigger $trigger1 `
    -Principal $principal1 `
    -Settings $settings1 `
    -Description "Auto-monitor Polymarket position changes" `
    -Force

Write-Host "Task created successfully!" -ForegroundColor Green
Write-Host ""

# Create Task for telegram_monitor
Write-Host "Creating Task for Monitor Trades..." -ForegroundColor Green
$action2 = New-ScheduledTaskAction -Execute $pythonPath -Argument "`"$monitorTrades`"" -WorkingDirectory $scriptPath
$trigger2 = New-ScheduledTaskTrigger -AtStartup
$principal2 = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Highest
$settings2 = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)

Register-ScheduledTask -TaskName "Polymarket Monitor Trades" `
    -Action $action2 `
    -Trigger $trigger2 `
    -Principal $principal2 `
    -Settings $settings2 `
    -Description "Auto-monitor Polymarket trades" `
    -Force

Write-Host "Task created successfully!" -ForegroundColor Green
Write-Host ""

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "All Tasks created successfully!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "The monitors will start automatically on every computer startup." -ForegroundColor Yellow
Write-Host ""
Write-Host "To verify:" -ForegroundColor Yellow
Write-Host "1. Open Task Scheduler (taskschd.msc)" -ForegroundColor White
Write-Host "2. Look for tasks: Polymarket Monitor Positions and Polymarket Monitor Trades" -ForegroundColor White
Write-Host "3. Restart your computer to test" -ForegroundColor White
Write-Host ""
