@echo off
@REM set VENV_NAME=myenv
@REM set REQUIREMENTS=requirements.txt

python checkver.py
if %errorlevel% neq 0 (
    echo "Python 3.11 or later is required. Installing..."
    powershell.exe -Command "Start-Process cmd -ArgumentList '/c', 'python -m ensurepip && python -m pip install --upgrade pip && python -m venv %VENV_NAME% && exit' -Verb RunAs"
    echo "Press any key..."
    pause >nul
)

@REM if not exist %VENV_NAME%\Scripts\activate.bat (
@REM     python -m venv %VENV_NAME%
@REM )
@REM call %VENV_NAME%\Scripts\activate.bat
@REM python -m pip install --upgrade pip
@REM python -m pip install -r %REQUIREMENTS%

python process_log.py

@REM pause.
