@echo off
REM 本机构建安装包：PyInstaller → Inno Setup，产物在 dist\installer\。
REM 版本号从 pyproject.toml 读，和 CI 的行为一致。

chcp 65001 >nul
title DesktopBackground 安装包构建

cd /d "%~dp0.."

where uv >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [错误] 未找到 uv，请先安装: https://docs.astral.sh/uv/
    pause
    exit /b 1
)

REM ---------- 读版本号 ----------
for /f "tokens=2 delims== " %%v in ('findstr /b /c:"version" pyproject.toml') do set APPVER=%%v
set APPVER=%APPVER:"=%
echo 版本: %APPVER%

echo [1/3] PyInstaller 打包...
if exist build rmdir /s /q build
if exist dist\DesktopBackground rmdir /s /q dist\DesktopBackground
uv run --group build pyinstaller packaging\main.spec --noconfirm
if %ERRORLEVEL% neq 0 (
    echo [错误] PyInstaller 打包失败
    pause
    exit /b 1
)

echo [2/3] 查找 Inno Setup...
set ISCC_CMD=
for %%p in (
    "%ProgramW6432%\Inno Setup 6\ISCC.exe"
    "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
    "%LocalAppData%\Programs\Inno Setup 6\ISCC.exe"
) do (
    if exist %%p (
        set ISCC_CMD=%%p
        goto :FOUND
    )
)
where ISCC.exe >nul 2>nul && set ISCC_CMD=ISCC.exe

:FOUND
if not defined ISCC_CMD (
    echo [错误] 未找到 Inno Setup，请安装: https://jrsoftware.org/isdl.php
    pause
    exit /b 1
)

echo [3/3] 编译安装包...
"%ISCC_CMD%" /DAppVersion=%APPVER% packaging\setup.iss
if %ERRORLEVEL% neq 0 (
    echo [错误] 安装包编译失败
    pause
    exit /b 1
)

echo.
echo 构建成功: dist\installer\DesktopBackground-Setup-%APPVER%.exe
pause
