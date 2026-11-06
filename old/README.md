# DRAP ACE PLAYER

Interfaz para Windows que envía un Content ID de AceStream al motor local y reproduce el flujo con MPV.

## Requisitos

1. AceStream Engine iniciado y escuchando en `127.0.0.1:6878`.
2. `mpv.exe` junto al programa, o dentro de una subcarpeta llamada `mpv`, o instalado en PATH.
3. Windows 10/11 para la integración VPN.

## Funciones

- Acepta `acestream://ID`, un ID de 40 caracteres o una URL que contenga `id=ID`.
- Caché configurable desde 60 hasta 900 segundos.
- Comprueba la versión del motor mediante su API local.
- Detecta perfiles VPN de Windows creados con `Add-VpnConnection` o Configuración de Windows.
- Conecta y desconecta mediante `rasdial`, sin almacenar usuario ni contraseña.
- Recuerda enlace, caché, perfil VPN y pantalla completa en `%APPDATA%\DRAP Ace Player\config.json`.

## Crear el EXE

Ejecuta `CREAR_EXE.bat`. El resultado queda en `dist\DRAP_ACE_PLAYER.exe`.

Copia después `mpv.exe` junto al EXE. Si tu distribución de MPV incluye DLL adicionales, conserva la distribución completa dentro de una carpeta `mpv` junto al EXE.

## Nota sobre la caché

`--cache-secs=60` configura el objetivo de caché de MPV, pero no garantiza que exista un minuto completo antes de comenzar. La cantidad real depende del flujo, del motor AceStream, de los pares y de la memoria disponible.

## VPN

El programa solo usa perfiles VPN ya configurados en Windows. Guarda las credenciales desde Windows; la aplicación no pide ni almacena contraseñas. La VPN es responsabilidad del usuario y debe utilizarse conforme a la ley y a las condiciones del servicio.
