@echo off
echo ==== Starting WebJob ====

REM Optional: run a system-level traceroute (works without raw sockets)
echo ==== Traceroute to github.com ====
tracert github.com

REM Traceroute to specific IP address
echo ==== Traceroute to 210.73.54.91 ====
tracert 210.73.54.91

echo ==== WebJob completed ====
