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
LicenseFile=license-for-win-installer.rtf

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
; Desktop icons are now created automatically - no task needed

[Files]
Source: "dist\Thonny\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "Python\*"; DestDir: "{app}\Python"; Flags: ignoreversion recursesubdirs createallsubdirs

; Conditionally include Qt Designer if it exists (for local builds and CI with Qt Designer uploaded)
#ifexist "Qt Designer\designer.exe"
Source: "Qt Designer\*"; DestDir: "{app}\Qt Designer"; Flags: ignoreversion recursesubdirs createallsubdirs
#endif

; Conditionally include wheels if folder exists
#ifexist "wheels\*"
Source: "wheels\*"; DestDir: "{app}\wheels"; Flags: ignoreversion recursesubdirs createallsubdirs
#endif

[Icons]
; Start Menu shortcuts
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Qt Designer"; Filename: "{app}\Python\Lib\site-packages\qt5_applications\Qt\bin\designer.exe"
; Desktop shortcuts
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\Qt Designer"; Filename: "{app}\Python\Lib\site-packages\qt5_applications\Qt\bin\designer.exe"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
