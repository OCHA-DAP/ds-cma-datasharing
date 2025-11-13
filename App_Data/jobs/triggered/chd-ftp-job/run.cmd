@echo off
REM Show which Python version we’re using (will appear in logs)
py -3 -c "import sys; print(sys.version)"

REM Run your script with Python 3
py -3 D:\home\site\wwwroot\pipelines\test_simple_chd_ftp.py
