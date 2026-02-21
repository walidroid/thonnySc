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
PrivilegesRequired=admin
SetupIconFile=thonny\res\thonny.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
LicenseFile=license-for-win-installer.txt

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: InstallESP32Driver; Description: "Installer les pilotes ESP32 (Optionnel)";

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

; ESP32 Auto-Flasher files (Firmware and Drivers)
#ifexist "firmware\esp32-20210902-v1.17.bin"
Source: "firmware\*"; DestDir: "{app}\firmware"; Flags: ignoreversion recursesubdirs createallsubdirs
#endif
#ifexist "drivers\CP210xVCPInstaller_x64.exe"
Source: "drivers\*"; DestDir: "{app}\drivers"; Flags: ignoreversion recursesubdirs createallsubdirs
#endif

[Icons]
; Start Menu shortcuts
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Qt Designer"; Filename: "{app}\Python\Lib\site-packages\qt5_applications\Qt\bin\designer.exe"
; Desktop shortcuts
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\Qt Designer"; Filename: "{app}\Python\Lib\site-packages\qt5_applications\Qt\bin\designer.exe"

[Run]
Filename: "{app}\drivers\CP210xVCPInstaller_x64.exe"; Parameters: "/quiet /qn /se /q"; WorkingDir: "{app}\drivers"; StatusMsg: "Installation des pilotes ESP32 ..."; Tasks:InstallESP32Driver; Check: Is64BitInstallMode; Flags: skipifdoesntexist
Filename: "{app}\drivers\CP210xVCPInstaller_x86.exe"; Parameters: "/quiet /qn /se /q"; WorkingDir: "{app}\drivers"; StatusMsg: "Installation des pilotes ESP32 ..."; Tasks:InstallESP32Driver; Check: not Is64BitInstallMode; Flags: skipifdoesntexist
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]

var
  ESP32Page : TOutputProgressWizardPage;

procedure InitializeWizard;
begin
end;

function NextButtonClick(CurPageID: Integer): Boolean;
var rpt: Boolean;
TmpFileName,Command: string;
ExecStdout :AnsiString;
ResultCode : Integer;
begin
  if CurPageID = wpFinished then 
  begin
        ESP32Page := CreateOutputProgressPage('Firmware Micropython ESP32', 'Vous pouvez maintenant installer le firmware pour programmer la carte ESP32 en MicroPython');
        ESP32Page.Show;

        TmpFileName := ExpandConstant('{tmp}') + '\~flash_results.txt';
        
        repeat
          rpt:=MsgBox('Voulez vous installer le firmware Micropython(v1.17) sur votre carte ESP32 ?'+#13#10+'NB: Branchez la carte puis appuiez sur le bouton EN (ou BOOT) 2 secondes puis cliquez sur Oui' , mbConfirmation, MB_YESNO) = idYes;
          
          if rpt  then
          begin
              ESP32Page.SetText(' Formatage de la memoire ... (environ 13 secondes)' ,'Veuillez patienter') ;
              ESP32Page.SetProgress(1,103);
              Command :=Format('"%s" /S /C ""%s" %s > "%s""', [ExpandConstant('{cmd}'),ExpandConstant('{app}')+'\Python\python.exe', '-m esptool erase_flash', TmpFilename]);
              if(Exec(ExpandConstant('{cmd}'), Command, '', SW_HIDE, ewWaitUntilTerminated , ResultCode) and LoadStringFromFile(TmpFileName, ExecStdout) )   then
              begin
                  if (pos('Chip erase completed successfully',String(ExecStdout))<> 0)   then 
                  begin
                     ESP32Page.SetText('Formatage Termine. Flashage en cours... (environ 90 secondes)' ,'Veuillez patienter') ;
                     ESP32Page.SetProgress(14,103);
                     Command :=Format('"%s" /S /C ""%s" %s > "%s""', [ExpandConstant('{cmd}'), ExpandConstant('{app}')+'\Python\python.exe', '-m esptool write_flash --flash_mode keep --flash_size detect 0x1000 "'+ ExpandConstant('{app}')+'\firmware\esp32-20210902-v1.17.bin"', TmpFilename]);
                     if ( Exec(ExpandConstant('{cmd}'), Command, '', SW_HIDE, ewWaitUntilTerminated , ResultCode) and LoadStringFromFile(TmpFileName, ExecStdout))   then
                     begin
                          if (pos('Hash of data verified.',String(ExecStdout))<> 0)   then 
                          begin
                              ESP32Page.SetText('Le firmware est bien installe !' ,'Vous pouvez brancher une autre carte ou fermer l''assistant.') ;
                              ESP32Page.SetProgress(103,103);
                          end
                          else 
                              ESP32Page.SetText('Erreur' ,'Probleme de flashage. Veuillez reessayer.' ) ;
                     end;   
                  end
                  else
                       ESP32Page.SetText('Erreur de formatage , appuyez sur le bouton EN ou BOOT sur la carte.' ,'Veuillez reessayez') ;
                  
                  DeleteFile(TmpFileName);
              end
              else MsgBox('Erreur ' +  SysErrorMessage(ResultCode) , mbInformation, MB_OK);  

          end;
        until rpt  = False;
       
      ESP32Page.Hide;
    end;
 
    Result := True
end;
