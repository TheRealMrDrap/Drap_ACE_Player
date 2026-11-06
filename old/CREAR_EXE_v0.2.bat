@echo off
setlocal
cd /d "%~dp0"
py -m pip install --upgrade pyinstaller
if errorlevel 1 exit /b 1
py -m PyInstaller --noconfirm --clean --onefile --windowed --name DRAP_ACE_PLAYER_v0.2 drap_ace_player.py
if errorlevel 1 exit /b 1
echo EXE creado en dist\DRAP_ACE_PLAYER_v0.2.exe
PAUSE
