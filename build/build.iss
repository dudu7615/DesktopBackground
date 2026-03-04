; ########### 基础配置（版本号需递增，AppId固定！）###########
#define AppName "桌面时钟背景"       ; 应用名称（可不变）
#define AppDir "DesktopBackground"
#define AppVersion "1.0.3"            ; 升级版本（必须>旧版本，如旧版1.0.0 → 新版1.0.1）
#define AppPublisher "dudu7615"   ; 发布者（可不变）
#define ExeDir "dist/main"        ; 新版本的可执行文件目录
#define MainExe "main.exe"        ; 主可执行文件
#define OutputDir "relaese"        ; MSI输出目录
#define OutputName "桌面时钟背景" ; MSI文件名
#define AppIcon "dist/main/icon.ico"

#define AppId "{{24d4202b-ba13-4415-a5cc-2e277060c47c}}"

; ########### 升级核心配置 ###########
[Setup]
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
; 核心1：固定AppId（升级的关键，绝对不能改！）
AppId={#AppId}
; 安装路径（仍为%localappdata%，可不变）
DefaultDirName={localappdata}\{#AppDir}
DefaultGroupName={#AppName}
OutputDir={#OutputDir}
OutputBaseFilename={#OutputName}-{#AppVersion}
Compression=lzma2
SolidCompression=yes
;MSIOutput=yes                       ; 强制生成MSI
LanguageDetectionMethod=uilanguage


; 设置安装包（EXE）的图标（MSI本身无图标，Windows会用系统默认，EXE安装包显示此图标）
SetupIconFile={#AppIcon}
; 设置卸载程序在系统「添加/删除程序」中显示的图标
UninstallDisplayIcon={app}\{#AppIcon}

; 打包新版本文件
[Files]
Source: "{#ExeDir}\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs

; 快捷方式配置（不变）
[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#MainExe}"; IconFilename: "{app}\{#MainExe}"
Name: "{commondesktop}\{#AppName}"; Filename: "{app}\{#MainExe}"; IconFilename: "{app}\{#MainExe}"; Flags: createonlyiffileexists
Name: "{group}\卸载 {#AppName}"; Filename: "{uninstallexe}"
Name: "{userstartup}\{#AppName}"; Filename: "{app}\{#MainExe}"; IconFilename: "{app}\{#MainExe}"; Flags: createonlyiffileexists

; 卸载清理（不变）
[UninstallDelete]
Type: filesandordirs; Name: "{app}"