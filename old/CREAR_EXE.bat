@echo off
setlocal
cd /d "%~dp0"
py -m pip install --upgrade pyinstaller
if errorlevel 1 exit /b 1
py -m PyInstaller --noconfirm --clean --onefile --windowed --name DRAP_ACE_PLAYER drap_ace_player.py
if errorlevel 1 exit /b 1
echo.
echo EXE creado en: %CD%\dist\DRAP_ACE_PLAYER.exe
pause
