; Inno Setup Script for ThonnySc
; This creates a Windows installer that bundles Thonny and all dependencies

#define MyAppName "ThonnySc"
#define MyAppPublisher "ThonnySc Team"
#define MyAppURL "https://github.com/walidroid/thonnysc"
#define MyAppExeName "Thonny.exe"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=output
OutputBaseFilename=ThonnySc_v{#MyAppVersion}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
SetupIconFile=thonny\res\thonny.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
LicenseFile=license-for-win-installer.txt

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
; Desktop icons are now created automatically - no task needed

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "wheels\*"; DestDir: "{app}\wheels"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Start Menu shortcut
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
; Desktop shortcuts - created automatically
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\Qt Designer"; Filename: "{app}\Scripts\pyqt5_qt5_designer.exe"; IconFilename: "{app}\Lib\site-packages\thonnycontrib\tunisiaschools\res\designer_16.png"; Check: FileExists(ExpandConstant('{app}\Scripts\pyqt5_qt5_designer.exe'))

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
