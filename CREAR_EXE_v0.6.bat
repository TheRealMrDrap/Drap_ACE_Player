@echo off
setlocal
cd /d "%~dp0"
py -m pip install --upgrade pyinstaller customtkinter pillow
if errorlevel 1 exit /b 1
py -m PyInstaller --noconfirm --clean --onefile --windowed --uac-admin --name DRAP_ACE_PLAYER_v0.6 --icon MrDrap_Player.ico --add-data "MrDrap_Player.ico;." --add-data "MrDrap_Player_64.png;." --add-data "MrDrap_Player_256.png;." --collect-all customtkinter drap_ace_player_v060.py
if errorlevel 1 exit /b 1
echo EXE creado: dist\DRAP_ACE_PLAYER_v0.6.exe
pause
