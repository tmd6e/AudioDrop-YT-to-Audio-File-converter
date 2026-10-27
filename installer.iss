#define AppVersion "1.1.0"
[Setup]
AppId=AudioDrop.Desktop
AppName=AudioDrop
AppVersion={#AppVersion}
AppPublisher=tmd6e
AppPublisherURL=https://github.com/tmd6e/AudioDrop-YT-to-Audio-File-converter
DefaultDirName={localappdata}\Programs\AudioDrop
DefaultGroupName=AudioDrop
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
OutputDir=dist
OutputBaseFilename=AudioDrop-Setup-{#AppVersion}
SetupIconFile=assets\audiodrop.ico
UninstallDisplayIcon={app}\AudioDrop.exe
Compression=lzma2/fast
SolidCompression=yes
WizardStyle=modern
CloseApplications=yes

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; Flags: checkedonce

[Files]
Source: "dist\AudioDrop\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{userprograms}\AudioDrop"; Filename: "{app}\AudioDrop.exe"; AppUserModelID: "AudioDrop.Desktop"
Name: "{userdesktop}\AudioDrop"; Filename: "{app}\AudioDrop.exe"; Tasks: desktopicon; AppUserModelID: "AudioDrop.Desktop"

[Run]
Filename: "{app}\AudioDrop.exe"; Description: "Open AudioDrop"; Flags: nowait postinstall skipifsilent
