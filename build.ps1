$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
python -m pip install -r requirements-build.txt
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed' }
python -m PyInstaller --noconfirm --clean --onefile --windowed --name AudioDrop --collect-all yt_dlp --collect-all yt_dlp_ejs audio_drop.py
if ($LASTEXITCODE -ne 0) { throw 'Executable build failed' }
