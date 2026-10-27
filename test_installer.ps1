$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$testDirectory = Join-Path $PSScriptRoot 'build/installer-test'
if (Test-Path -LiteralPath $testDirectory) { throw 'Installer test directory already exists; use a fresh build workspace.' }
$installer = (Resolve-Path 'dist/AudioDrop-Setup-1.1.0.exe').Path
$install = Start-Process -FilePath $installer -ArgumentList @('/VERYSILENT', '/SUPPRESSMSGBOXES', '/NORESTART', '/NOICONS', '/TASKS=', ('/DIR="' + $testDirectory + '"')) -WindowStyle Hidden -Wait -PassThru
if ($install.ExitCode -ne 0) { throw 'Installer failed' }
try {
    $report = Join-Path $PSScriptRoot 'build/installed-check.json'
    if (Test-Path -LiteralPath $report) { Remove-Item -LiteralPath $report }
    $check = Start-Process -FilePath (Join-Path $testDirectory 'AudioDrop.exe') -ArgumentList @('--self-test', ('"' + $report + '"')) -WindowStyle Hidden -Wait -PassThru
    if ($check.ExitCode -ne 0 -or -not (Test-Path -LiteralPath $report)) { throw 'Installed application self-test failed' }
    Get-Content $report
} finally {
    $uninstaller = Join-Path $testDirectory 'unins000.exe'
    if (Test-Path -LiteralPath $uninstaller) {
        $uninstall = Start-Process -FilePath $uninstaller -ArgumentList '/VERYSILENT /SUPPRESSMSGBOXES /NORESTART' -WindowStyle Hidden -Wait -PassThru
        if ($uninstall.ExitCode -ne 0) { throw 'Uninstall failed' }
    }
}
Write-Host 'Install, bundled runtime checks, and uninstall passed.'
