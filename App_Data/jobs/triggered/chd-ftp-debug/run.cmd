@echo off
echo ==== Starting WebJob ====
echo ==== Testing TCP connections ====

powershell -Command "`
$targets = @('210.73.54.91', 'github.com'); `
$ports = @(21, 22); `
foreach ($target in $targets) { `
    Write-Output ('Testing ' + $target); `
    foreach ($port in $ports) { `
        try { `
            $tcp = New-Object System.Net.Sockets.TcpClient; `
            $tcp.Connect($target, $port); `
            if ($tcp.Connected) { `
                Write-Output ('  Port ' + $port + ': Connection successful'); `
                $tcp.Close(); `
            } `
        } catch { `
            Write-Output ('  Port ' + $port + ': Connection failed'); `
        } `
    } `
}"

echo ==== WebJob completed ====
