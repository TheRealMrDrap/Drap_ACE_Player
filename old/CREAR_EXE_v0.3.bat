@echo off
setlocal
cd /d "%~dp0"
py -m pip install --upgrade pyinstaller
if errorlevel 1 exit /b 1
py -m PyInstaller --noconfirm --clean --onefile --windowed --uac-admin --name DRAP_ACE_PLAYER_v0.3 drap_ace_player_v03.py
if errorlevel 1 exit /b 1
echo.
echo EXE creado: dist\DRAP_ACE_PLAYER_v0.3.exe
pause
