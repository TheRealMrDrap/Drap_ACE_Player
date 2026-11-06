DRAP ACE PLAYER v0.8.1
Cambios importantes
- Espera respuesta del stream de AceStream antes de lanzar MPV.
- MPV arranca con --force-window=immediate, por lo que la ventana debe aparecer incluso mientras está cargando.
- Comprueba 1,8 segundos después que mpv.exe sigue vivo.
- Registra el PID de MPV.
- Genera un diagnóstico real en:

%APPDATA%\DRAP Ace Player\mpv_last.log