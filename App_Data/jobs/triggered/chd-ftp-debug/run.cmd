@echo off
echo ==== Starting WebJob ====
echo ==== Testing TCP connections ====

powershell -Command "try { (New-Object Net.Sockets.TcpClient).Connect('210.73.54.91',21); Write-Output '210.73.54.91:21 OK' } catch { Write-Output '210.73.54.91:21 FAIL' }"
powershell -Command "try { (New-Object Net.Sockets.TcpClient).Connect('210.73.54.91',22); Write-Output '210.73.54.91:22 OK' } catch { Write-Output '210.73.54.91:22 FAIL' }"
powershell -Command "try { (New-Object Net.Sockets.TcpClient).Connect('github.com',21); Write-Output 'github.com:21 OK' } catch { Write-Output 'github.com:21 FAIL' }"
powershell -Command "try { (New-Object Net.Sockets.TcpClient).Connect('github.com',22); Write-Output 'github.com:22 OK' } catch { Write-Output 'github.com:22 FAIL' }"

echo ==== WebJob completed ====
