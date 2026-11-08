# DRAP ACE PLAYER

Interfaz para Windows que envía un Content ID de AceStream al motor local y reproduce el flujo con MPV.

## Requisitos

1. AceStream Engine iniciado y escuchando en `127.0.0.1:6878`.
2. `mpv.exe` junto al programa, o dentro de una subcarpeta llamada `mpv`, o instalado en PATH. El propio programa lo chequea y te permite instalarlo en la misma carpeta que donde dejes el exe.
3. Windows 7/10/11 compatible.

## Funciones

- Acepta `acestream://ID`, un ID de 40 caracteres o una URL que contenga `id=ID`.
- Caché configurable desde 60 hasta 900 segundos.
- Comprueba la versión del motor mediante su API local.
- Recuerda enlace, caché y pantalla completa en `%APPDATA%\DRAP Ace Player\config.json`.
- Tenemos listado de chequeo de salud del ID visto, si abre y está encendido un tiempo, marca en verde, si no arranca marca ROTO y la fecha de prueba, se puede revisar, editar o marcar como queramos para su futuro uso.

## Nota sobre la caché

`--cache-secs=60` configura el objetivo de caché de MPV, pero no garantiza que exista un minuto completo antes de comenzar. La cantidad real depende del flujo, del motor AceStream, de los pares y de la memoria disponible.

## VPN ** Hasta la versión 0.7

Puse una OpenVPN que sacaba un listado de VPNs Gratuitas globales, pero solo conseguí que conectara a Japón un par de veces, la velocidad era muy lenta, en el futuro no descarto probar en futuras versiones.