@echo off
REM 本机快速打包：只出可运行的 exe 目录（dist\DesktopBackground\），不封安装包。
REM 需要安装包请用 packaging\build_installer.bat 或 CI，见 packaging\README.md。

cd /d "%~dp0.."

if exist build rmdir /s /q build
if exist dist\DesktopBackground rmdir /s /q dist\DesktopBackground

REM --group build 让 uv 顺带装上 PyInstaller（它不在默认依赖里）
uv run --group build pyinstaller packaging\main.spec --noconfirm
if %ERRORLEVEL% neq 0 (
    echo [错误] PyInstaller 打包失败
    pause
    exit /b 1
)

echo.
echo 打包完成: %~dp0..\dist\DesktopBackground\
pause
