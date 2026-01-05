@echo off
REM Show Python version
py -3 -c "import sys; print(sys.version)"

REM Install dependencies
py -3 -m pip install --user --upgrade pip
py -3 -m pip install --user --no-warn-script-location -r D:\home\site\wwwroot\pipeline_requirements.txt

REM Run the script
set PYTHONWARNINGS=ignore
py -3 D:\home\site\wwwroot\pipelines\download_all_files.py
