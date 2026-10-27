param([switch]$SkipInstaller)
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
python -m pip install -r requirements-build.txt
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed' }
python bundle_tools.py
if ($LASTEXITCODE -ne 0) { throw 'Runtime download or checksum verification failed' }
python -m PyInstaller --noconfirm --clean --onedir --windowed --name AudioDrop --icon assets/audiodrop.ico --add-data 'assets;assets' --add-data 'vendor/licenses;licenses' --add-data 'vendor/manifest.json;.' --add-binary 'vendor/ffmpeg.exe;vendor' --add-binary 'vendor/ffprobe.exe;vendor' --add-binary 'vendor/node.exe;vendor' --collect-all yt_dlp --collect-all yt_dlp_ejs audio_drop.py
if ($LASTEXITCODE -ne 0) { throw 'Executable build failed' }
Copy-Item 'Create shortcuts.ps1', 'Create shortcuts.bat', 'README.md', 'LICENSE', 'THIRD_PARTY_NOTICES.txt' -Destination 'dist/AudioDrop'
$report = Join-Path $PSScriptRoot 'build/bundle-check.json'
if (Test-Path -LiteralPath $report) { Remove-Item -LiteralPath $report }
$check = Start-Process -FilePath 'dist/AudioDrop/AudioDrop.exe' -ArgumentList @('--self-test', ('"' + $report + '"')) -WindowStyle Hidden -Wait -PassThru
if ($check.ExitCode -ne 0 -or -not (Test-Path -LiteralPath $report)) { throw 'Bundled runtime smoke test failed' }
Get-Content $report
Compress-Archive -Path 'dist/AudioDrop' -DestinationPath 'dist/AudioDrop-Windows.zip' -Force
if (-not $SkipInstaller) {
    $compiler = $env:AUDIODROP_ISCC
    if (-not $compiler) { $compiler = "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe" }
    if (-not (Test-Path -LiteralPath $compiler)) { throw 'Install Inno Setup 6 or set AUDIODROP_ISCC to ISCC.exe.' }
    & $compiler installer.iss
    if ($LASTEXITCODE -ne 0) { throw 'Installer build failed' }
}
