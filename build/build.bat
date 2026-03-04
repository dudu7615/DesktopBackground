@echo off

set "iscc=E:\Inno Setup 6\ISCC.exe"

cd /d "%~dp0"

if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

uv run pyinstaller --noconfirm --onedir --windowed --icon "../icon.ico" --add-data "../clock;clock/"  "../main.py"
copy "..\icon.ico" "dist\main\icon.ico"

"%iscc%" "build.iss"