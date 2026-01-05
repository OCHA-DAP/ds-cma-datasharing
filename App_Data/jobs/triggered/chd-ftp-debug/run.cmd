@echo off
echo ==== Starting WebJob ====
echo ==== Testing TCP connections ====

powershell -Command " \
  $targets = @('210.73.54.91', 'github.com'); \
  $ports = @(21, 22); \
  foreach ($target in $targets) { \
    Write-Output \"Testing $target\"; \
    foreach ($port in $ports) { \
      $tcp = New-Object Net.Sockets.TcpClient; \
      try { \
        $tcp.Connect($target, $port); \
        if ($tcp.Connected) { \
          Write-Output \"  Port $port: Connection successful\"; \
        } else { \
          Write-Output \"  Port $port: Connection failed\"; \
        } \
      } catch { \
        Write-Output \"  Port $port: Error - $($_.Exception.Message)\"; \
      } finally { \
        $tcp.Close(); \
      } \
    } \
  }"

echo ==== WebJob completed ====
