@echo off

cd /d "%~dp0"

if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

uv run pyinstaller --noconfirm "main.spec"
copy "..\icon.ico" "dist\main\_internal\icon.ico"
