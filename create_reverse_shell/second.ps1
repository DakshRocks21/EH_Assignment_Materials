$RemoteUser       = 'eh'
$RemoteHost       = '135.235.193.119'

$tunnels = @(
    @{ RemotePort = 2222; Local = '10.10.1.6:22' },
    @{ RemotePort = 2223; Local = 'localhost:22' }
)

$RArgs = foreach ($t in $tunnels) {
    "-R", "$($t.RemotePort):$($t.Local)"
}

$sshArgs = @(
    "-i", $KeyPath,
    "-o", "ServerAliveInterval=60",
    "-o", "ServerAliveCountMax=3",
    "-N"
) + $RArgs + @("$RemoteUser@$RemoteHost")

Write-Host "Running: ssh $($sshArgs -join ' ')"
Start-Process -FilePath "ssh.exe" -ArgumentList $sshArgs -WindowStyle Hidden | Out-Null
