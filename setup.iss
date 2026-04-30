; setup.iss - Script do Inno Setup para criar instalador automático
; 
; Este instalador:
; 1. Instala Python automaticamente se não existir
; 2. Instala todas as dependências automáticamente
; 3. Cria atalhos no Desktop e Menu Iniciar
; 4. O cliente NÃO precisa instalar nada manualmente!
;
; Como usar:
; 1. Baixe e instale Inno Setup: https://jrsoftware.org/isdl.php
; 2. Compile este script: iscc setup.iss
; 3. Gere o instalador .exe

#define MyAppName "Servidor Agenda"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Seu Nome"
#define MyAppURL "https://seusite.com"
#define MyAppExeName "ServidorAgenda.exe"

[Setup]
; NOTE: O valor AppId precisa ser único para este aplicativo.
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
; Saída do instalador
OutputDir=installer
OutputBaseFilename=ServidorAgenda-Setup-{#MyAppVersion}
; Configurações de compressão
Compression=lzma2
SolidCompression=yes
; Appearance
WizardStyle=modern
; Privileges
PrivilegesRequired=admin
; Desinstalar
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Fonte principal - Replace with your actual .exe after building
Source: "dist\ServidorAgenda.exe"; DestDir: "{app}"; Flags: ignoreversion
; Banco de dados (se existir)
Source: "db.sqlite3"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; Executa o servidor após instalação
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
// Código Pascal para instalar Python automaticamente

var
  PythonPath: string;
  PythonVersion: string;
  PythonNeeded: boolean;

function IsPythonInstalled(): Boolean;
var
  s: String;
begin
  Result := False;
  // Tenta executar python --version
  if Exec('python.exe', '--version', '', SW_HIDE, ewWaitUntilTerminated, s) then
  begin
    if Pos('Python', s) > 0 then
      Result := True;
  end;
end;

function GetPythonVersion(): String;
var
  s: String;
begin
  Result := '';
  if Exec('python.exe', '--version', '', SW_HIDE, ewWaitUntilTerminated, s) then
  begin
    // Extrai versão
    Result := s;
  end;
end;

function DownloadFile(URL, FileName: String): Boolean;
var
  WinHttpReq: Variant;
  WinHttp: Variant;
begin
  Result := False;
  try
    WinHttpReq := CreateOleObject('WinHttp.WinHttpRequest.5.1');
    WinHttpReq.Open('GET', URL, False);
    WinHttpReq.Send('');
    if WinHttpReq.Status = 200 then
    begin
      // Salva o arquivo
      WinHttp := CreateOleObject('ADODB.Stream');
      WinHttp.Type := 1; // binary
      WinHttp.Open();
      WinHttp.Write(WinHttpReq.ResponseBody);
      WinHttp.SaveToFile(FileName, 2); // 2 = adSaveCreateOverWrite
      WinHttp.Close();
      Result := True;
    end;
  except
    // Erro ao baixar
