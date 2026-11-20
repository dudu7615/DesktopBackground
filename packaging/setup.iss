; DesktopBackground 安装脚本（Inno Setup 6+）。
;
; 编译（Windows 上）：
;     ISCC.exe /DAppVersion=1.1.0 packaging\setup.iss
; 产物在 dist\installer\DesktopBackground-Setup-<版本>.exe
;
; 安装范围只针对当前用户（PrivilegesRequired=lowest），不弹 UAC，装到
; %LOCALAPPDATA% 下，并且**不允许**临时提升为管理员安装（见下方
; PrivilegesRequired 附近的说明）。
;
; 程序运行时往用户数据目录 %LOCALAPPDATA%\DesktopBackground\runtime 里写合成后
; 的图片——不写安装目录，是为了让程序目录保持只读也不影响运行（比方说便携版
; 解压进了 Program Files）。安装目录放 %LOCALAPPDATA% 仍然合适：免 UAC、
; 卸载干净。
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
; 刻意不设 PrivilegesRequiredOverridesAllowed：安装目录在 %LOCALAPPDATA% 下、
; 用户可写，而卸载时会经 powershell 执行 {app} 里的 killapp.ps1。一旦允许
; 临时改成管理员安装/卸载，就等于给任何能写这个目录的人一个提权执行点。
; 只允许当前用户安装就没有这个问题。
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
; 这里只清确定可以提前删的东西。**不要在这里删 main.exe**：Inno 会先处理
; [InstallDelete]、再复制 [Files]，而新的启动器叫 DesktopBackground.exe，
; 万一复制阶段失败或被中断，旧安装就既没有 main.exe 也没有新 exe，彻底起不来。
; 旧 main.exe 改在 [Code] 里安装成功后删除（见 RemoveOldLauncher）。
;
; 旧 main.exe 由 [Code] 在安装成功后删除（见 RemoveOldLauncher）。
; 不在这里删 _internal：用户的 clock/config.yml 就在里面，而且先删后装，
; 安装中途失败旧程序会残缺。旧文件靠 [Files] 的 ignoreversion 覆盖。
Type: files; Name: "{app}\icon.ico"

[Files]
; 结束进程用的小脚本（见下方 KillApp）。以 dontcopy 编进安装器本体，安装时
; 解压到临时目录用。必须放在 [Files] 最前面：SolidCompression 下，取靠后的
; 文件要先把前面的全部解压到内存，安装会卡一下。
Source: "killapp.ps1"; Flags: dontcopy noencryption
; 用户改过的 _internal\clock\config.yml 不能被新版本的默认配置覆盖，
; 所以先把它从通配里排除，再用 onlyifdoesntexist 单独装：文件已存在就跳过。
Source: "{#BuildDir}\*"; DestDir: "{app}"; Excludes: "_internal\clock\config.yml"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#BuildDir}\_internal\clock\config.yml"; DestDir: "{app}\_internal\clock"; Flags: onlyifdoesntexist
; 再装一份到 {app}，卸载器要用它结束本程序的进程（见 CurUninstallStepChanged）
Source: "killapp.ps1"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{userprograms}\{#AppName}\{#AppName}"; Filename: "{app}\{#AppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\{#AppExeName}"
Name: "{userprograms}\{#AppName}\卸载 {#AppName}"; Filename: "{uninstallexe}"; IconFilename: "{app}\{#AppExeName}"
Name: "{userdesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon; IconFilename: "{app}\{#AppExeName}"
; 开机自启走"启动"文件夹的快捷方式而不是注册表 Run 键：用户能直接在
; "启动"里看到并删掉它，卸载时 Inno 也会自动清理。
Name: "{userstartup}\{#AppName}"; Filename: "{app}\{#AppExeName}"; WorkingDir: "{app}"; Tasks: startupicon; IconFilename: "{app}\{#AppExeName}"

[Run]
Filename: "{app}\{#AppExeName}"; Description: "立即运行 {#AppName}"; Flags: postinstall nowait skipifsilent unchecked

[UninstallDelete]
; 运行时生成的图片与日志由主程序写在 %LOCALAPPDATA%\DesktopBackground\ 下，
; 不是安装器装的，不显式删就会留在用户目录里。这里**只删本安装对应的那个
; 子目录**（规则见下方 InstanceKey，与 modules/paths.py 的 instanceKey 一致）。
; 不能删整个 runtime/logs 根——便携版用的是另一个子目录，删根会把它正在用的
; 图一起清掉。
Type: filesandordirs; Name: "{localappdata}\{#AppName}\runtime\{code:InstanceKey}"
Type: filesandordirs; Name: "{localappdata}\{#AppName}\logs\{code:InstanceKey}"

[Code]
{ 这是无窗口的托盘程序，Inno 的 Restart Manager 认不出它，不主动杀进程就会
  因为 exe 被占用而装不上。

  不能用 taskkill /im：它按进程映像名匹配，机器上任何叫
  DesktopBackground.exe / main.exe 的程序都会被一起强杀，可能丢掉别人没保存
  的工作。killapp.ps1 按可执行文件的完整路径过滤，只结束本安装目录下的那个
  进程；没在跑时什么也不做，返回码忽略。 }
procedure KillApp(const ExePath: String);
var
  ResultCode: Integer;
begin
  ExtractTemporaryFile('killapp.ps1');
  Exec('powershell.exe',
       '-NoProfile -NonInteractive -ExecutionPolicy Bypass -File "' +
       ExpandConstant('{tmp}\killapp.ps1') + '" -ExePath "' + ExePath + '"',
       '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
end;

procedure KillRunningApp;
begin
  KillApp(ExpandConstant('{app}\{#AppExeName}'));
  { 顺手清掉旧版进程名，覆盖升级时才不会留下正在运行的 main.exe }
  KillApp(ExpandConstant('{app}\main.exe'));
end;

{ 安装成功后再删旧版 main.exe。放在 [InstallDelete] 里的话，它会在新文件
  复制之前就被删掉——复制一旦失败，用户就两个 exe 都没有了。 }
procedure RemoveOldLauncher;
var
  OldExe: String;
begin
  OldExe := ExpandConstant('{app}\main.exe');
  if FileExists(OldExe) then
    DeleteFile(OldExe);
end;

function PrepareToInstall(var NeedsRestart: Boolean): String;
begin
  KillRunningApp;
  Result := '';
end;

{ 与 modules/paths.py 的 instanceKey() 完全一致：
  djb2 校验和（h = h*33 + 码点，按 32 位回绕）取 8 位十六进制，接 `_`，
  再接 {app} 转小写、非 ASCII 字母数字换成下划线、取末 72 个字符。
  两边算法不同步的话，卸载就清不到自己的运行期数据（或误删便携版的数据）。 }
function InstanceKey(Param: String): String;
var
  S, Readable: String;
  I: Integer;
  H: Int64;
begin
  S := Lowercase(ExpandConstant('{app}'));

  { 用 Int64 再取低 32 位：Cardinal 上 H*33 会先溢出报错 }
  H := 5381;
  for I := 1 to Length(S) do
    H := (H * 33 + Ord(S[I])) and $FFFFFFFF;

  Readable := '';
  for I := 1 to Length(S) do
  begin
    if ((S[I] >= 'a') and (S[I] <= 'z')) or ((S[I] >= '0') and (S[I] <= '9')) then
      Readable := Readable + S[I]
    else
      Readable := Readable + '_';
  end;
  if Length(Readable) > 72 then
    Readable := Copy(Readable, Length(Readable) - 72 + 1, 72);

  Result := Lowercase(IntToHex(H, 8)) + '_' + Readable;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
    RemoveOldLauncher;
end;

{ 卸载时结束本程序的进程。走 CurUninstallStepChanged 而不是 [UninstallRun]：
  [UninstallRun] 没法按条件跳过，而这里必须能判断"当前是否提权"。

  killapp.ps1 装在 {app} 下，用户可写。正常情况下卸载器以当前用户运行，替换
  它没有任何收益；但如果用户手动右键"以管理员身份运行"卸载器，执行用户可写
  的脚本就成了提权执行点，所以提权时直接跳过——文件被占用时 Inno 会提示重启。 }
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  ResultCode: Integer;
  Script: String;
begin
  if CurUninstallStep <> usUninstall then
    Exit;
  if IsAdmin then
    Exit;
  Script := ExpandConstant('{app}\killapp.ps1');
  if not FileExists(Script) then
    Exit;
  Exec('powershell.exe',
       '-NoProfile -NonInteractive -ExecutionPolicy Bypass -File "' + Script +
       '" -ExePath "' + ExpandConstant('{app}\{#AppExeName}') + '"',
       '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  { 顺带清掉旧版的 main.exe——从 V1.0.x 升级上来的机器上可能还开着它 }
  Exec('powershell.exe',
       '-NoProfile -NonInteractive -ExecutionPolicy Bypass -File "' + Script +
       '" -ExePath "' + ExpandConstant('{app}\main.exe') + '"',
       '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
end;
