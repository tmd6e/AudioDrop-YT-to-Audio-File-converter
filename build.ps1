$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
python -m pip install -r requirements-build.txt
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed' }
python -m PyInstaller --noconfirm --clean --onefile --windowed --name AudioDrop --icon assets/audiodrop.ico --add-data "assets;assets" --collect-all yt_dlp --collect-all yt_dlp_ejs audio_drop.py
if ($LASTEXITCODE -ne 0) { throw 'Executable build failed' }
Compress-Archive -Path 'dist/AudioDrop.exe', 'Create shortcuts.ps1', 'Create shortcuts.bat', 'README.md', 'LICENSE' -DestinationPath 'dist/AudioDrop-Windows.zip' -Force
