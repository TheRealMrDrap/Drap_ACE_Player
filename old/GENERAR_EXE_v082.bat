@echo off
setlocal
cd /d "%~dp0"
title DRAP ACE PLAYER v0.8.2 - Generador EXE

set "PY=drap_ace_player_v082.py"
set "NAME=DRAP ACE PLAYER v0.8.2"
set "ICON=MrDrap_Player.ico"
set "PNG64=MrDrap_Player_64.png"
set "PNG256=MrDrap_Player_256.png"

echo ============================================================
echo        DRAP ACE PLAYER v0.8.2 - GENERADOR DE EXE
echo ============================================================
echo.

if not exist "%PY%" (
  echo [ERROR] No existe %PY%
  pause
  exit /b 1
)

where py >nul 2>&1
if %errorlevel%==0 (
  set "PYCMD=py"
) else (
  where python >nul 2>&1
  if errorlevel 1 (
    echo [ERROR] Python no esta instalado o no esta en PATH.
    pause
    exit /b 1
  )
  set "PYCMD=python"
)

echo [1/4] Instalando/actualizando dependencias...
%PYCMD% -m pip install --upgrade pyinstaller customtkinter pillow
if errorlevel 1 goto :error

echo.
echo [2/4] Limpiando compilaciones anteriores...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist "%NAME%.spec" del /q "%NAME%.spec"

echo.
echo [3/4] Compilando...
set "ADDDATA="
if exist "%PNG64%" set "ADDDATA=%ADDDATA% --add-data "%PNG64%;.""
if exist "%PNG256%" set "ADDDATA=%ADDDATA% --add-data "%PNG256%;.""

set "ICONARG="
if exist "%ICON%" (
  set "ICONARG=--icon "%ICON%" --add-data "%ICON%;.""
) else (
  echo [AVISO] No se encuentra %ICON%. Se generara sin icono personalizado.
)

%PYCMD% -m PyInstaller --noconfirm --clean --onefile --windowed --name "%NAME%" %ICONARG% %ADDDATA% --collect-all customtkinter "%PY%"
if errorlevel 1 goto :error

echo.
echo [4/4] Finalizado.
echo.
echo EXE generado en:
echo "%~dp0dist\%NAME%.exe"
echo.
start "" "%~dp0dist"
pause
exit /b 0

:error
echo.
echo [ERROR] La compilacion ha fallado.
pause
exit /b 1
