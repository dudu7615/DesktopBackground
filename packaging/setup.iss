; DesktopBackground 安装脚本（Inno Setup 6+）。
;
; 编译（Windows 上）：
;     ISCC.exe /DAppVersion=1.1.0 packaging\setup.iss
; 产物在 dist\installer\DesktopBackground-Setup-<版本>.exe
;
; 安装范围只针对当前用户（PrivilegesRequired=lowest），不弹 UAC，装到
; %LOCALAPPDATA% 下。这是刻意为之：程序运行时会往 clock/ 里写合成后的
; result.png，装进 Program Files 反而会因为没有写权限而画不出壁纸。
;
; 注意：本文件里所有相对路径都相对**本文件所在目录**（packaging/）解析。
;
; 版本号：CI 会用 /DAppVersion=<pyproject.toml 的 version> 传进来；本机手打时
; 不传则用下面的默认值。

#define AppName "DesktopBackground"
#define AppExeName "DesktopBackground.exe"

#ifndef AppVersion
  #define AppVersion "1.1.0"
#endif

; spec 生成的目录名与仓库根同级，即 <仓库>/dist/DesktopBackground
#define BuildDir "..\dist\DesktopBackground"

[Setup]
; AppId 唯一标识本软件。**一旦发布就不要再改**，否则新版本会被当成另一个
; 程序，覆盖安装与卸载都会错乱。这里的值沿用旧版安装包（当时 MyAppName
; 为 DesktopBackground），所以从 V1.0.x 升级上来仍然是同一个程序。
AppId={{24d4202b-ba13-4415-a5cc-2e277060c47c}}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
; 与旧版一致的安装目录，保证 UsePreviousAppDir 能原地升级到同一位置
DefaultDirName={localappdata}\{#AppName}
DisableDirPage=yes
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
OutputDir=..\dist\installer
OutputBaseFilename={#AppName}-Setup-{#AppVersion}
Compression=lzma2/ultra
SolidCompression=yes
WizardStyle=modern
; 托盘程序只有 Windows 版 exe
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
; 图标沿用仓库根的 icon.ico（已是多尺寸 ico，见 packaging/README.md）
SetupIconFile=..\icon.ico
UninstallDisplayIcon={app}\{#AppExeName}

; 界面语言：Inno 官方不带简体中文语言文件，choco 装出来的 Inno 里没有
; ChineseSimplified.isl。直接启用会让 ISCC 报 "Could not read language file"
; 而构建失败，所以默认只用英文向导。想要全中文向导，把社区版
; ChineseSimplified.isl 放进 Inno 的 Languages\ 目录后再取消下面那行注释。
[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
; Name: "chinesesimplified"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "快捷方式："; Flags: checkedonce
; 默认勾选：这是个常驻托盘的壁纸程序，装了就是要它开机自己跑起来。
Name: "startupicon"; Description: "添加到开机启动"; GroupDescription: "快捷方式："; Flags: checkedonce

[InstallDelete]
; 覆盖升级时先清掉旧版本的 exe 与 _internal，避免残留旧 DLL。
; V1.0.x 的产物叫 main.exe，一并删掉——否则升级后会留下两个 exe，
; 开机启动项指的还是旧的那个。
Type: files; Name: "{app}\main.exe"
Type: files; Name: "{app}\icon.ico"
Type: filesandordirs; Name: "{app}\_internal"

[Files]
Source: "{#BuildDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{userprograms}\{#AppName}\{#AppName}"; Filename: "{app}\{#AppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\{#AppExeName}"
Name: "{userprograms}\{#AppName}\卸载 {#AppName}"; Filename: "{uninstallexe}"; IconFilename: "{app}\{#AppExeName}"
Name: "{userdesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon; IconFilename: "{app}\{#AppExeName}"
; 开机自启走"启动"文件夹的快捷方式而不是注册表 Run 键：用户能直接在
; "启动"里看到并删掉它，卸载时 Inno 也会自动清理。
Name: "{userstartup}\{#AppName}"; Filename: "{app}\{#AppExeName}"; WorkingDir: "{app}"; Tasks: startupicon; IconFilename: "{app}\{#AppExeName}"

[Run]
Filename: "{app}\{#AppExeName}"; Description: "立即运行 {#AppName}"; Flags: postinstall nowait skipifsilent unchecked

[UninstallRun]
Filename: "{sys}\taskkill.exe"; Parameters: "/f /im {#AppExeName}"; Flags: runhidden

[Code]
{ 这是无窗口的托盘程序，Inno 的 Restart Manager 认不出它，不主动杀进程就会
  因为 exe 被占用而装不上。没在跑时 taskkill 返回非零，忽略即可。 }
procedure KillRunningApp;
var
  ResultCode: Integer;
begin
  Exec(ExpandConstant('{sys}\taskkill.exe'), '/f /im {#AppExeName}', '',
       SW_HIDE, ewWaitUntilTerminated, ResultCode);
  { 顺手清掉旧版进程名，覆盖升级时才不会留下正在运行的 main.exe }
  Exec(ExpandConstant('{sys}\taskkill.exe'), '/f /im main.exe', '',
       SW_HIDE, ewWaitUntilTerminated, ResultCode);
end;

function PrepareToInstall(var NeedsRestart: Boolean): String;
begin
  KillRunningApp;
  Result := '';
end;
