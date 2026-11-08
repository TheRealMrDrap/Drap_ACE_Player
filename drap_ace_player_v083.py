import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import urllib.request
from datetime import datetime
from pathlib import Path

import tkinter as tk
import customtkinter as ctk

APP = 'DRAP ACE PLAYER'
VERSION = '0.8.3'
HOST = '127.0.0.1'
PORT = 6878
CFGDIR = Path(os.getenv('APPDATA', Path.home())) / 'DRAP Ace Player'
CFG = CFGDIR / 'config.json'
MPV_API = 'https://api.github.com/repos/zhongfly/mpv-winbuild/releases/latest'

BG = '#0b1018'
PANEL = '#121a26'
PANEL2 = '#172231'
BLUE = '#1689ff'
GREEN = '#29c77d'
ORANGE = '#f0a23a'
RED = '#ef5350'
TEXT = '#f4f7fb'
MUTED = '#98a7ba'
BORDER = '#26364a'
STATUS_COLORS = {'ok': GREEN, 'medio': ORANGE, 'roto': RED}
STATUS_TEXT = {'ok': 'OK', 'medio': 'MEDIO', 'roto': 'ROTO'}


def adir():
    return Path(sys.executable).resolve().parent if getattr(sys, 'frozen', False) else Path(__file__).resolve().parent


def res(name):
    return Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent)) / name


def si():
    startup = subprocess.STARTUPINFO()
    startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    return startup


def run(args, timeout=60):
    return subprocess.run(
        args,
        capture_output=True,
        text=True,
        timeout=timeout,
        startupinfo=si(),
        creationflags=0x08000000,
    )


ctk.set_appearance_mode('dark')


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        CFGDIR.mkdir(parents=True, exist_ok=True)
        self.player = None
        self.engineproc = None
        self.active_cid = None
        self.player_started_at = None
        self.player_confirmed = False
        self.manual_stop = False

        self.title(f'{APP} v{VERSION}')
        self.geometry('1180x760')
        self.minsize(1100, 720)
        self.configure(fg_color=BG)

        try:
            self.iconbitmap(str(res('MrDrap_Player.ico')))
            self._ico = tk.PhotoImage(file=str(res('MrDrap_Player_64.png')))
            self.iconphoto(True, self._ico)
        except Exception:
            pass

        try:
            self.cfg = json.loads(CFG.read_text(encoding='utf8'))
        except Exception:
            self.cfg = {}

        self.history = self.cfg.get('history', [])
        if not isinstance(self.history, list):
            self.history = []

        self.ace = tk.StringVar(value=self.cfg.get('ace', ''))
        self.cache = tk.StringVar(value=str(max(60, int(self.cfg.get('cache', 60)))))
        self.fs = tk.BooleanVar(value=self.cfg.get('fs', False))
        self.engs = tk.StringVar(value='AceStream Engine: comprobando...')
        self.comps = tk.StringVar(value='MPV: comprobando...')
        self.engine_component = tk.StringVar(value='AceStream Engine: comprobando...')

        self.ui()
        self.after(350, self.refresh)
        self.protocol('WM_DELETE_WINDOW', self.close)

    def card(self, parent):
        return ctk.CTkFrame(parent, fg_color=PANEL, corner_radius=18, border_width=1, border_color=BORDER)

    def b(self, parent, text, command, color=BLUE, width=150):
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            width=width,
            height=38,
            corner_radius=12,
            fg_color=color,
            hover_color='#0871dc' if color == BLUE else '#213247',
            font=ctk.CTkFont('Segoe UI', 13, 'bold'),
        )

    def ui(self):
        root = ctk.CTkFrame(self, fg_color='transparent')
        root.pack(fill='both', expand=True, padx=26, pady=10)

        head = ctk.CTkFrame(root, fg_color='transparent')
        head.pack(fill='x')
        try:
            from PIL import Image
            self.logo = ctk.CTkImage(Image.open(res('MrDrap_Player_256.png')), size=(82, 82))
            ctk.CTkLabel(head, text='', image=self.logo).pack(anchor='center')
        except Exception:
            pass

        ctk.CTkLabel(head, text=APP, font=ctk.CTkFont('Segoe UI', 24, 'bold'), text_color=TEXT).pack(anchor='center')
        ctk.CTkLabel(head, text=f'v{VERSION}  •  AceStream + MPV', text_color=MUTED).pack(anchor='center')

        q = ctk.CTkFrame(root, fg_color='transparent')
        q.pack(fill='x', pady=(7, 7))
        ctk.CTkButton(
            q,
            text='▶  REPRODUCIR',
            command=self.play,
            height=46,
            corner_radius=14,
            fg_color=BLUE,
            font=ctk.CTkFont('Segoe UI', 15, 'bold'),
        ).pack(side='left', fill='x', expand=True)
        ctk.CTkButton(
            q,
            text='■  DETENER TODO',
            command=self.stop_all,
            width=210,
            height=46,
            corner_radius=14,
            fg_color='#1d2b3d',
            font=ctk.CTkFont('Segoe UI', 14, 'bold'),
        ).pack(side='left', padx=(10, 0))

        cols = ctk.CTkFrame(root, fg_color='transparent')
        cols.pack(fill='both', expand=True)
        left = ctk.CTkFrame(cols, fg_color='transparent')
        left.pack(side='left', fill='both', expand=True, padx=(0, 6))
        right = ctk.CTkFrame(cols, fg_color='transparent')
        right.pack(side='left', fill='both', expand=True, padx=(6, 0))

        x = self.card(left)
        x.pack(fill='x', pady=(0, 7))
        ctk.CTkLabel(x, text='Reproducción', font=ctk.CTkFont('Segoe UI', 15, 'bold'), text_color=TEXT).pack(anchor='w', padx=17, pady=(12, 6))
        ctk.CTkEntry(
            x,
            textvariable=self.ace,
            height=42,
            corner_radius=12,
            fg_color=PANEL2,
            border_color=BORDER,
            placeholder_text='acestream://ID o Content ID',
            font=ctk.CTkFont('Consolas', 12),
        ).pack(fill='x', padx=17)
        r = ctk.CTkFrame(x, fg_color='transparent')
        r.pack(fill='x', padx=17, pady=(9, 12))
        ctk.CTkLabel(r, text='Caché', text_color=MUTED).pack(side='left')
        ctk.CTkEntry(r, textvariable=self.cache, width=72, height=34, corner_radius=10, fg_color=PANEL2, border_color=BORDER, font=ctk.CTkFont('Segoe UI', 12)).pack(side='left', padx=7)
        ctk.CTkLabel(r, text='segundos', text_color=MUTED).pack(side='left')
        ctk.CTkCheckBox(r, text='Pantalla completa', variable=self.fs, corner_radius=6).pack(side='right')

        history_card = self.card(left)
        history_card.pack(fill='both', expand=True, pady=7)
        hh = ctk.CTkFrame(history_card, fg_color='transparent')
        hh.pack(fill='x', padx=17, pady=(12, 4))
        ctk.CTkLabel(hh, text='Últimos ID reproducidos', font=ctk.CTkFont('Segoe UI', 15, 'bold'), text_color=TEXT).pack(side='left')
        ctk.CTkLabel(hh, text='Clic derecho para cambiar estado o eliminar', text_color=MUTED, font=ctk.CTkFont('Segoe UI', 10)).pack(side='right')
        self.history_frame = ctk.CTkScrollableFrame(history_card, height=156, fg_color='#0d141f', corner_radius=12, border_width=1, border_color=BORDER)
        self.history_frame.pack(fill='both', expand=True, padx=17, pady=(0, 15))
        self.render_history()

        x = self.card(right)
        x.pack(fill='x', pady=(0, 7))
        ctk.CTkLabel(x, text='AceStream Engine', font=ctk.CTkFont('Segoe UI', 15, 'bold'), text_color=TEXT).pack(anchor='w', padx=17, pady=(12, 3))
        ctk.CTkLabel(x, textvariable=self.engs, text_color=MUTED).pack(anchor='w', padx=17)
        r = ctk.CTkFrame(x, fg_color='transparent')
        r.pack(fill='x', padx=17, pady=(8, 12))
        self.b(r, 'ARRANCAR ENGINE', self.start_engine, GREEN, 180).pack(side='left')
        self.b(r, 'DETENER ENGINE', self.stop_engine, '#1d2b3d', 180).pack(side='left', padx=8)

        x = self.card(right)
        x.pack(fill='x', pady=7)
        ctk.CTkLabel(x, text='Componentes (instala pulsando el botón si sale que no lo tienes)', font=ctk.CTkFont('Segoe UI', 14, 'bold'), text_color=TEXT).pack(anchor='w', padx=17, pady=(12, 3))
        self.mpv_component_label = ctk.CTkLabel(x, textvariable=self.comps, text_color=MUTED)
        self.mpv_component_label.pack(anchor='w', padx=17)
        self.engine_component_label = ctk.CTkLabel(x, textvariable=self.engine_component, text_color=MUTED)
        self.engine_component_label.pack(anchor='w', padx=17, pady=(2, 0))
        r = ctk.CTkFrame(x, fg_color='transparent')
        r.pack(fill='x', padx=17, pady=(8, 12))
        self.install_mpv_button = self.b(r, 'Instalar MPV', self.install_mpv)
        self.install_mpv_button.pack(side='left')

        x = self.card(right)
        x.pack(fill='both', expand=True, pady=(7, 0))
        h = ctk.CTkFrame(x, fg_color='transparent')
        h.pack(fill='x', padx=17, pady=(12, 6))
        ctk.CTkLabel(h, text='Registro de actividad', font=ctk.CTkFont('Segoe UI', 15, 'bold'), text_color=TEXT).pack(side='left')
        self.b(h, 'LIMPIAR', self.clear_log, '#1d2b3d', 90).pack(side='right')
        self.logbox = ctk.CTkTextbox(x, fg_color='#0d141f', border_width=1, border_color=BORDER, corner_radius=12, font=ctk.CTkFont('Consolas', 11), text_color='#dce7f5', wrap='word')
        self.logbox.pack(fill='both', expand=True, padx=17, pady=(0, 15))
        self.logbox.configure(state='disabled')
        self.log('DRAP ACE PLAYER iniciado.')

    def now_text(self):
        return datetime.now().strftime('%d/%m/%Y - %H:%M')

    def render_history(self):
        for widget in self.history_frame.winfo_children():
            widget.destroy()

        if not self.history:
            ctk.CTkLabel(self.history_frame, text='Todavía no hay ID reproducidos.', text_color=MUTED).pack(anchor='w', padx=5, pady=8)
            return

        for item in self.history:
            cid = item.get('id', '')
            status = item.get('status', 'roto')
            color = STATUS_COLORS.get(status, RED)
            row = ctk.CTkFrame(self.history_frame, fg_color=PANEL2, corner_radius=9, height=34)
            row.pack(fill='x', pady=3)
            row.pack_propagate(False)

            dot = ctk.CTkLabel(row, text='●', width=24, text_color=color, font=ctk.CTkFont('Segoe UI', 15, 'bold'))
            dot.pack(side='left', padx=(7, 0))
            label = ctk.CTkLabel(row, text=f'{cid}  ({item.get("last_used", "sin fecha")})', anchor='w', text_color=color, font=ctk.CTkFont('Consolas', 11, 'bold'))
            label.pack(side='left', fill='x', expand=True, padx=4)
            badge = ctk.CTkLabel(row, text=STATUS_TEXT.get(status, 'ROTO'), width=60, text_color=color, font=ctk.CTkFont('Segoe UI', 10, 'bold'))
            badge.pack(side='right', padx=7)

            for widget in (row, dot, label, badge):
                widget.bind('<Button-1>', lambda event, value=cid: self.load_history_id(value))
                widget.bind('<Button-3>', lambda event, value=cid: self.history_menu(event, value))

    def load_history_id(self, cid):
        self.ace.set(cid)
        self.log(f'ID cargado desde el historial: {cid}')

    def history_menu(self, event, cid):
        menu = tk.Menu(self, tearoff=0, bg='#172231', fg=TEXT, activebackground=BLUE, activeforeground='white')
        menu.add_command(label='Marcar verde · OK', command=lambda: self.set_history_status(cid, 'ok'))
        menu.add_command(label='Marcar naranja · Medio', command=lambda: self.set_history_status(cid, 'medio'))
        menu.add_command(label='Marcar rojo · Roto', command=lambda: self.set_history_status(cid, 'roto'))
        menu.add_separator()
        menu.add_command(label='Eliminar del listado', command=lambda: self.delete_history(cid))
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def update_history(self, cid, status):
        existing = next((x for x in self.history if x.get('id') == cid), None)
        if existing:
            self.history.remove(existing)
        self.history.insert(0, {'id': cid, 'status': status, 'last_used': self.now_text()})
        self.history = self.history[:100]
        self.render_history()
        self.save()

    def set_history_status(self, cid, status):
        existing = next((x for x in self.history if x.get('id') == cid), None)
        if existing:
            existing['status'] = status
            existing['last_used'] = self.now_text()
            self.history.remove(existing)
            self.history.insert(0, existing)
        else:
            self.history.insert(0, {'id': cid, 'status': status, 'last_used': self.now_text()})
        self.render_history()
        self.save()
        self.log(f'Historial: {cid} marcado como {STATUS_TEXT[status]}.')

    def delete_history(self, cid):
        self.history = [x for x in self.history if x.get('id') != cid]
        self.render_history()
        self.save()
        self.log(f'Historial: {cid} eliminado.')

    def log(self, msg):
        line = f'[{time.strftime("%H:%M:%S")}] {msg}\n'

        def put():
            self.logbox.configure(state='normal')
            self.logbox.insert('1.0', line)
            self.logbox.configure(state='disabled')
            self.logbox.yview_moveto(0)

        put() if threading.current_thread() is threading.main_thread() else self.after(0, put)

    def clear_log(self):
        self.logbox.configure(state='normal')
        self.logbox.delete('1.0', 'end')
        self.logbox.configure(state='disabled')
        self.log('Registro limpiado.')

    def engine_paths(self):
        paths = []
        for base in [os.getenv('APPDATA'), os.getenv('LOCALAPPDATA'), os.getenv('ProgramFiles'), os.getenv('ProgramFiles(x86)')]:
            if base:
                b = Path(base)
                paths += [
                    b / 'ACEStream' / 'engine' / 'ace_console.exe',
                    b / 'Ace Stream' / 'engine' / 'ace_console.exe',
                    b / 'ACEStream' / 'engine' / 'ace_engine.exe',
                    b / 'Ace Stream' / 'engine' / 'ace_engine.exe',
                    b / 'ACEStream' / 'ace_engine.exe',
                ]
        return paths

    def find_engine(self):
        for path in self.engine_paths():
            if path.exists():
                return path
        return None

    def engine_ok(self, log_stopped=True):
        try:
            urllib.request.urlopen(f'http://{HOST}:{PORT}/webui/api/service?method=get_version', timeout=2).read()
            self.engs.set('●  AceStream Engine conectado')
            return True
        except Exception:
            self.engs.set('○  AceStream Engine detenido')
            if log_stopped:
                self.log('AceStream Engine detenido.')
            return False

    def start_engine(self, automatic=False):
        if self.engine_ok():
            return True
        path = self.find_engine()
        if not path:
            self.log('ERROR: no encuentro AceStream Engine en las rutas habituales.')
            return False
        self.log(f'Arrancando AceStream Engine: {path}')
        args = [str(path), '--client-console'] if path.name.lower() == 'ace_console.exe' else [str(path)]
        self.engineproc = subprocess.Popen(args, cwd=str(path.parent), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL, creationflags=0x08000000)
        for _ in range(24):
            time.sleep(0.5)
            if self.engine_ok():
                self.log('AceStream Engine arrancado y API 6878 operativa.')
                return True
        self.log('ERROR: AceStream se inició pero no respondió en 127.0.0.1:6878.')
        return False

    def stop_engine(self):
        for name in ('ace_engine.exe', 'ace_console.exe'):
            try:
                run(['taskkill', '/F', '/T', '/IM', name], 15)
            except Exception:
                pass
        self.engs.set('○  AceStream Engine detenido')
        self.log('AceStream Engine detenido.')

    def mpv(self):
        for path in [adir() / 'mpv.exe', adir() / 'mpv' / 'mpv.exe']:
            if path.exists():
                return path
        found = shutil.which('mpv')
        return Path(found) if found else None

    def refresh(self):
        mpv_ok = self.mpv() is not None
        engine_path = self.find_engine()
        engine_installed = engine_path is not None
        engine_running = self.engine_ok(log_stopped=False)
        self.comps.set('●  MPV: instalado' if mpv_ok else '○  MPV: NO instalado')
        self.mpv_component_label.configure(text_color=GREEN if mpv_ok else RED)
        self.install_mpv_button.configure(state='disabled' if mpv_ok else 'normal', fg_color='#294236' if mpv_ok else BLUE)
        if engine_installed:
            self.engine_component.set('●  AceStream Engine: instalado' + (' · ejecutándose' if engine_running else ' · detenido'))
            self.engine_component_label.configure(text_color=GREEN)
        else:
            self.engine_component.set('○  AceStream Engine: NO instalado')
            self.engine_component_label.configure(text_color=RED)
        self.log('Comprobación de componentes: ' + self.comps.get() + ' · ' + self.engine_component.get())
        return mpv_ok, engine_installed
    def prerequisites_ok(self):
        mpv_ok = self.mpv() is not None
        engine_installed = self.find_engine() is not None or self.engine_ok(log_stopped=False)
        if not mpv_ok or not engine_installed:
            missing=[]
            if not engine_installed: missing.append('AceStream Engine')
            if not mpv_ok: missing.append('MPV')
            self.log('REPRODUCCIÓN BLOQUEADA: falta ' + ' y '.join(missing) + '.')
            self.refresh()
            return False
        return True
    def install_mpv(self):
        self.log('Consultando última versión de MPV...')
        threading.Thread(target=self._mpv, daemon=True).start()

    def _mpv(self):
        try:
            request = urllib.request.Request(MPV_API, headers={'User-Agent': APP})
            data = json.loads(urllib.request.urlopen(request, timeout=20).read())
            asset = next(x for x in data['assets'] if re.fullmatch(r'mpv-x86_64-[^/]+\.7z', x['name']))
            dest = adir() / 'mpv'
            dest.mkdir(exist_ok=True)
            archive = adir() / asset['name']
            urllib.request.urlretrieve(asset['browser_download_url'], archive)
            tool = shutil.which('tar') or shutil.which('7z')
            run([tool, '-xf', str(archive), '-C', str(dest)] if 'tar' in Path(tool).name.lower() else [tool, 'x', '-y', f'-o{dest}', str(archive)], 180)
            archive.unlink(missing_ok=True)
            found = next(dest.rglob('mpv.exe'))
            if found != dest / 'mpv.exe':
                shutil.copy2(found, dest / 'mpv.exe')
            self.after(0, self.refresh)
            self.log('MPV instalado correctamente.')
        except Exception as exc:
            self.log('ERROR instalando MPV: ' + str(exc))

    def cid(self):
        value = re.sub(r'^acestream://', '', self.ace.get().strip(), flags=re.I)
        match = re.search(r'[?&](?:id|content_id)=([0-9a-fA-F]{40})', value)
        value = match.group(1) if match else value
        if not re.fullmatch(r'[0-9a-fA-F]{40}', value):
            raise ValueError('El ACE debe contener un Content ID hexadecimal de 40 caracteres.')
        return value.lower()

    def stream_probe(self, url, timeout=30):
        self.log('Solicitando el stream al AceStream Engine...')
        try:
            request = urllib.request.Request(url, headers={'User-Agent': f'DRAP-ACE-PLAYER/{VERSION}'})
            response = urllib.request.urlopen(request, timeout=timeout)
            final_url = response.geturl()
            content_type = response.headers.get('Content-Type', 'desconocido')
            self.log(f'AceStream respondió. Content-Type: {content_type}')
            response.close()
            return final_url
        except Exception as exc:
            self.log('ERROR preparando stream AceStream: ' + str(exc))
            return None

    def play(self):
        # Antes de procesar el ID, todos los componentes obligatorios deben existir.
        if not self.prerequisites_ok():
            return
        try:
            cid = self.cid()
            cache = max(60, int(self.cache.get()))
        except Exception as exc:
            self.log('ERROR: ' + str(exc))
            return

        mpv = self.mpv()
        if not mpv:
            self.log('ERROR: falta MPV. Pulsa Instalar MPV.')
            self.update_history(cid, 'roto')
            return

        self.log('Preparando reproducción...')
        self.update_idletasks()
        if not self.start_engine(True):
            self.update_history(cid, 'roto')
            return

        url = f'http://{HOST}:{PORT}/ace/getstream?id={cid}'
        stream_url = self.stream_probe(url)
        if not stream_url:
            self.update_history(cid, 'roto')
            return

        self.stop_player(manual=True)
        log_path = CFGDIR / 'mpv_last.log'
        try:
            log_path.unlink(missing_ok=True)
        except Exception:
            pass

        args = [
            str(mpv), stream_url,
            '--force-window=immediate',
            '--cache=yes',
            f'--cache-secs={cache}',
            '--demuxer-max-bytes=256MiB',
            '--demuxer-readahead-secs=120',
            '--title=DRAP ACE PLAYER',
            '--osc=yes',
            '--input-default-bindings=yes',
            '--volume=100',
            f'--log-file={log_path}',
            '--msg-level=all=warn',
        ]
        if self.fs.get():
            args.append('--fullscreen')

        try:
            self.manual_stop = False
            self.active_cid = cid
            self.player_confirmed = False
            self.player_started_at = time.time()
            self.log(f'Abriendo MPV: {mpv}')
            self.player = subprocess.Popen(args, cwd=str(adir()), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.log(f'Proceso MPV creado. PID {self.player.pid}. Comprobando ventana/proceso...')
            self.after(1800, lambda: self.check_player_started(log_path, cid, cache))
            self.save()
        except Exception as exc:
            self.update_history(cid, 'roto')
            self.log('ERROR arrancando MPV: ' + str(exc))

    def check_player_started(self, log_path, cid, cache):
        if not self.player or self.active_cid != cid:
            self.log('ERROR: no existe proceso MPV para comprobar.')
            self.update_history(cid, 'roto')
            return

        return_code = self.player.poll()
        if return_code is None:
            self.player_confirmed = True
            self.update_history(cid, 'ok')
            self.log(f'MPV abierto correctamente (PID {self.player.pid}). Reproducción solicitada · caché {cache} s.')
            self.after(5000, lambda: self.monitor_player(cid))
            return

        detail = ''
        try:
            lines = log_path.read_text(encoding='utf8', errors='ignore').splitlines()
            useful = [x.strip() for x in lines if x.strip() and ('error' in x.lower() or 'failed' in x.lower() or 'cannot' in x.lower() or 'http' in x.lower())]
            if useful:
                detail = useful[-1][-600:]
        except Exception:
            pass
        self.update_history(cid, 'roto')
        self.log(f'ERROR: MPV terminó nada más arrancar (código {return_code}).' + (f' Detalle: {detail}' if detail else f' Revisa {log_path}'))

    def monitor_player(self, cid):
        if not self.player or self.active_cid != cid:
            return
        return_code = self.player.poll()
        if return_code is None:
            self.after(5000, lambda: self.monitor_player(cid))
            return

        seconds = int(time.time() - self.player_started_at) if self.player_started_at else 0
        if not self.manual_stop and self.player_confirmed:
            self.update_history(cid, 'medio')
            self.log(f'AVISO: MPV se cerró después de {seconds} segundos. ID marcado en naranja como MEDIO.')
        self.player = None
        self.active_cid = None
        self.player_started_at = None
        self.player_confirmed = False
        self.manual_stop = False

    def stop_player(self, manual=True):
        self.manual_stop = manual
        if self.player and self.player.poll() is None:
            try:
                self.player.terminate()
            except Exception:
                pass
        self.player = None
        self.active_cid = None
        self.player_started_at = None
        self.player_confirmed = False

    def stop_all(self):
        self.stop_player(manual=True)
        self.log('MPV detenido.')
        self.stop_engine()
        self.log('DETENER TODO completado.')

    def save(self):
        data = {
            'ace': self.ace.get(),
            'cache': max(60, int(self.cache.get())),
            'fs': self.fs.get(),
            'history': self.history,
        }
        CFG.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf8')

    def close(self):
        try:
            self.save()
        except Exception:
            pass
        self.stop_player(manual=True)
        self.stop_engine()
        self.destroy()


if __name__ == '__main__':
    App().mainloop()
