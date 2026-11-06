@echo off
setlocal
cd /d "%~dp0"
py -m pip install --upgrade pyinstaller customtkinter pillow
if errorlevel 1 exit /b 1
py -m PyInstaller --noconfirm --clean --onefile --windowed --uac-admin --name DRAP_ACE_PLAYER_v0.4 --icon MrDrap_Player.ico --add-data "MrDrap_Player.ico;." --add-data "MrDrap_Player_64.png;." --add-data "MrDrap_Player_128.png;." --collect-all customtkinter drap_ace_player_v040.py
if errorlevel 1 exit /b 1
echo.
echo EXE creado: dist\DRAP_ACE_PLAYER_v0.4.exe
pause
