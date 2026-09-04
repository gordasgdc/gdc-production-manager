; Instalator Windows pentru GDC Production Manager, cu Inno Setup (gratuit,
; https://jrsoftware.org/isinfo.php). Aceeasi structura ca DataMover/
; installer.iss si gdc-plugin-manager-win/installer.iss — instaleaza in
; Program Files, creeaza scurtaturi Start Menu + Desktop, apare corect in
; "Apps & Features" cu dezinstalare curata prin Inno Setup nativ.
;
; AUDIT 2026-08-26 (CLAUDE.md Partea 1, Regula 5): inlocuieste distributia
; "portabila" veche (exe rulat direct din orice folder, dezinstalat manual
; cu uninstall-windows.bat) - acel .bat ramane in repo doar ca fallback
; pentru cine a instalat deja versiunea veche, dar NU mai e livrat in
; arhiva noua (inlocuit de dezinstalarea nativa Inno Setup).
;
; Cum se compileaza (pe Windows, o data ai nevoie de Inno Setup Compiler
; instalat - gratuit, https://jrsoftware.org/isdl.php, sau
; `winget install JRSoftware.InnoSetup --source winget`):
;   1. Ruleaza pasii din .github/workflows/build-windows.yml local
;      (PyInstaller pentru GDCProductionManager.exe, rezultatul in dist\)
;   2. Copiaza dist\GDCProductionManager.exe si docs\guides\Instructiuni_Utilizare.pdf
;      in dist_release\ (acelasi tipar ca workflow-ul CI)
;   3. Compileaza acest fisier:
;      & "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe" installer.iss
;   4. Rezultatul apare in Output\GDCProductionManagerSetup.exe
;
; NU compila pe macOS/CI Mac — Inno Setup ruleaza doar pe Windows.

#define MyAppName "GDC Production Manager"
#define MyAppVersion "2.0.2"
#define MyAppPublisher "Cristi Gordas"
#define MyAppExeName "GDCProductionManager.exe"
#define MyAppURL "https://gordas.dev/gdc-production-manager"

[Setup]
AppId={{7C2A9E10-3B4D-4A6F-8E2C-GDCPRODMGRSETUP}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
; Cerinta explicita (Directiva finala 2026-08-26): C:\Program Files\GDC\GDC Production Manager\
DefaultDirName={autopf}\GDC\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=Output
OutputBaseFilename=GDCProductionManagerSetup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
SetupIconFile=icon\icon.ico
; Nu semnat cu certificat platit (acelasi caz ca celelalte instalatoare
; Windows din ecosistemul GDC) — SmartScreen poate arata un avertisment
; "Unrecognized app" la prima rulare; normal pentru distributie indie,
; se trece cu "More info" -> "Run anyway".
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist_release\GDCProductionManager.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist_release\Instructiuni_Utilizare.pdf"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Dezinstaleaza {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[UninstallDelete]
; Curatare completa la dezinstalare — datele aplicatiei (conturi, proiecte,
; licenta) stau in %APPDATA%\GDCProductionManager, in afara folderului de
; instalare din Program Files (Inno Setup nu le atinge implicit).
Type: filesandordirs; Name: "{userappdata}\GDCProductionManager"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent
