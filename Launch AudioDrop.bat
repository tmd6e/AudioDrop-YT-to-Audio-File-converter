@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\pythonw.exe" (
    python -m venv .venv
)
".venv\Scripts\python.exe" -c "import yt_dlp" >nul 2>&1
if errorlevel 1 (
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 (
        echo Setup failed. Check your internet connection and launch again.
        pause
        exit /b 1
    )
)
start "" ".venv\Scripts\pythonw.exe" "audio_drop.py"
