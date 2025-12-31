@echo off
REM Show Python version
py -3 -c "import sys; print(sys.version)"

REM Install dependencies
py -3 -m pip install --user --upgrade pip
py -3 -m pip install --user -r D:\home\site\wwwroot\requirements.txt

REM Run the script
py -3 D:\home\site\wwwroot\pipelines\test_sftp.py
