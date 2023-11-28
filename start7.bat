@echo off
@set VENV_NAME=myenv
@set REQUIREMENTS=requirements.txt

python checkver.py
if 
    echo "Python 3.11 or later is required. Installing..."
    powershell.exe -Command "Start-Process cmd -ArgumentList '/c', 'python -m ensurepip        python -m pip install –upgrade pip        python -m venv 
    echo "Press any key..."
    pause >nul
)

if not exist 
    python -m venv 
)
call 
python -m pip install –upgrade pip
python -m pip install -r 

python process_log.py

pause.
