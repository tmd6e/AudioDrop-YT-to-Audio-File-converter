$ErrorActionPreference = 'Stop'
$appPath = Join-Path $PSScriptRoot 'AudioDrop.exe'
if (-not (Test-Path -LiteralPath $appPath)) {
    $appPath = Join-Path $PSScriptRoot 'dist\AudioDrop.exe'
}
if (-not (Test-Path -LiteralPath $appPath)) {
    throw 'AudioDrop.exe is missing. Extract the release ZIP or build the app first.'
}
$appPath = (Resolve-Path -LiteralPath $appPath).Path
$shell = New-Object -ComObject WScript.Shell
foreach ($folder in @([Environment]::GetFolderPath('Desktop'), [Environment]::GetFolderPath('Programs'))) {
    $shortcut = $shell.CreateShortcut((Join-Path $folder 'AudioDrop.lnk'))
    $shortcut.TargetPath = $appPath
    $shortcut.WorkingDirectory = Split-Path $appPath
    $shortcut.IconLocation = "$appPath,0"
    $shortcut.Description = 'Search YouTube and download audio with AudioDrop'
    $shortcut.Save()
}
Write-Host 'Desktop and Start menu shortcuts created. Right-click AudioDrop to pin it to Start, or launch it and right-click its taskbar icon to pin it.'
