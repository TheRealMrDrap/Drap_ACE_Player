@echo off
setlocal
cd /d "%~dp0"
py -m pip install --upgrade pyinstaller customtkinter pillow
if errorlevel 1 exit /b 1
REM Seguridad: NO se usa --uac-admin. El reproductor se ejecuta con privilegios normales.
py -m PyInstaller --noconfirm --clean --onefile --windowed --name DRAP_ACE_PLAYER_v0.8.4 --icon MrDrap_Player.ico --add-data "MrDrap_Player.ico;." --add-data "MrDrap_Player_64.png;." --add-data "MrDrap_Player_256.png;." --collect-all customtkinter drap_ace_player_v084.py
if errorlevel 1 exit /b 1
echo EXE creado sin elevacion UAC: dist\DRAP_ACE_PLAYER_v0.8.4.exe
pause
