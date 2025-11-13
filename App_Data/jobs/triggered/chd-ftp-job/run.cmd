@echo off

REM Move from this folder (/App_Data/jobs/triggered/chd-ftp-job)
REM back to the site root (wwwroot)
cd /d "%~dp0..\..\.."

echo [WebJob] Running from: %CD%

REM Execute the script inside pipelines/
python pipelines\test_simple_chd_ftp.py
