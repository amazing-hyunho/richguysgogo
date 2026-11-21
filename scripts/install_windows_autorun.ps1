$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path $PSScriptRoot -Parent
$runtimeDir = Join-Path $env:LOCALAPPDATA 'richguysgogo\autorun'
New-Item -ItemType Directory -Path $runtimeDir -Force | Out-Null
$resultFile = Join-Path $runtimeDir 'install-result.json'
try {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent().Name
    $backupDir = Join-Path $runtimeDir ('backup-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
    $taskMap = [ordered]@{
        '뉴스 크롤링' = 'run_news_hourly.py'
        '아침발송' = 'send_morning.py'
        '주간sync' = 'sync_weekly.py'
        'ｎｉｇｈｔ＿ｒｕｎ' = 'sync_all.py'
    }
    $pythonWindowless = Join-Path $env:LOCALAPPDATA 'Microsoft\WindowsApps\pythonw.exe'
    if (-not (Test-Path -LiteralPath $pythonWindowless)) { throw 'Python launcher not found' }
    foreach ($taskName in $taskMap.Keys) {
        Export-ScheduledTask -TaskName $taskName |
            Set-Content -LiteralPath (Join-Path $backupDir ($taskName + '.xml')) -Encoding Unicode
    }
    $principal = New-ScheduledTaskPrincipal -UserId $identity -LogonType Interactive -RunLevel Limited
    foreach ($taskName in $taskMap.Keys) {
        $task = Get-ScheduledTask -TaskName $taskName
        $arguments = '-X utf8 "' + (Join-Path $PSScriptRoot 'run_scheduled.py') + '" ' + $taskMap[$taskName]
        $action = New-ScheduledTaskAction -Execute $pythonWindowless -Argument $arguments -WorkingDirectory $repoRoot
        $task.Settings.MultipleInstances = 'IgnoreNew'
        $triggers = @($task.Triggers)
        if ($taskMap[$taskName] -ne 'send_morning.py') {
            $task.Settings.StartWhenAvailable = $true
            $task.Settings.DisallowStartIfOnBatteries = $false
            $task.Settings.StopIfGoingOnBatteries = $false
        }
        if ($taskMap[$taskName] -eq 'sync_all.py') {
            $logon = New-ScheduledTaskTrigger -AtLogOn -User $identity
            $logon.Delay = 'PT1M'
            $triggers = @($triggers | Where-Object { $_.CimClass.CimClassName -ne 'MSFT_TaskLogonTrigger' }) + $logon
        }
        Set-ScheduledTask -TaskName $taskName -Action $action -Principal $principal -Settings $task.Settings -Trigger $triggers | Out-Null
    }
    # The scheduled logon trigger replaces the temporary Startup-folder entry.
    $startupLink = Join-Path ([Environment]::GetFolderPath('Startup')) 'richguysgogo-collector.lnk'
    if (Test-Path -LiteralPath $startupLink) { Remove-Item -LiteralPath $startupLink }
    @{success=$true; backup=$backupDir; finishedAt=(Get-Date -Format o)} |
        ConvertTo-Json | Set-Content -LiteralPath $resultFile -Encoding UTF8
} catch {
    @{success=$false; error=$_.Exception.Message; finishedAt=(Get-Date -Format o)} |
        ConvertTo-Json | Set-Content -LiteralPath $resultFile -Encoding UTF8
    exit 1
}
