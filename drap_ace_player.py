import json
import os
import re
import subprocess
import sys
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import ttk, messagebox
from urllib.parse import quote
from urllib.request import urlopen, Request

APP_NAME = "DRAP ACE PLAYER"
ENGINE_HOST = "127.0.0.1"
ENGINE_PORT = 6878
CONFIG_DIR = Path(os.getenv("APPDATA", Path.home())) / "DRAP Ace Player"
CONFIG_FILE = CONFIG_DIR / "config.json"


def app_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def hidden_startupinfo():
    if os.name != "nt":
        return None
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    return si


def run_hidden(args, timeout=15):
    return subprocess.run(args, capture_output=True, text=True, timeout=timeout,
                          startupinfo=hidden_startupinfo(), creationflags=0x08000000 if os.name == "nt" else 0)


class DrapAcePlayer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("720x430")
        self.minsize(650, 400)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.mpv_process = None
        self.config_data = self.load_config()
        self.ace_var = tk.StringVar(value=self.config_data.get("last_ace", ""))
        self.cache_var = tk.IntVar(value=max(60, int(self.config_data.get("cache_seconds", 60))))
        self.vpn_var = tk.StringVar(value=self.config_data.get("vpn_profile", ""))
        self.fullscreen_var = tk.BooleanVar(value=self.config_data.get("fullscreen", False))
        self.status_var = tk.StringVar(value="Preparado")
        self.engine_var = tk.StringVar(value="Motor AceStream: comprobando...")
        self.vpn_status_var = tk.StringVar(value="VPN: sin comprobar")
        self.build_ui()
        self.after(250, self.refresh_all)

    def build_ui(self):
        style = ttk.Style(self)
        try:
            style.theme_use("vista")
        except tk.TclError:
            pass
        root = ttk.Frame(self, padding=18)
        root.pack(fill="both", expand=True)
        ttk.Label(root, text=APP_NAME, font=("Segoe UI", 20, "bold")).pack(anchor="w")
        ttk.Label(root, text="AceStream Engine + MPV, con caché configurable y VPN de Windows opcional").pack(anchor="w", pady=(0, 16))

        stream = ttk.LabelFrame(root, text="Enlace AceStream", padding=12)
        stream.pack(fill="x")
        self.ace_entry = ttk.Entry(stream, textvariable=self.ace_var, font=("Consolas", 10))
        self.ace_entry.pack(fill="x", pady=(0, 10))
        opts = ttk.Frame(stream)
        opts.pack(fill="x")
        ttk.Label(opts, text="Caché previa:").pack(side="left")
        self.cache_spin = ttk.Spinbox(opts, from_=60, to=900, increment=30, textvariable=self.cache_var, width=7)
        self.cache_spin.pack(side="left", padx=(6, 4))
        ttk.Label(opts, text="segundos (mínimo 60)").pack(side="left")
        ttk.Checkbutton(opts, text="Pantalla completa", variable=self.fullscreen_var).pack(side="right")

        vpn = ttk.LabelFrame(root, text="VPN de Windows (opcional)", padding=12)
        vpn.pack(fill="x", pady=12)
        row = ttk.Frame(vpn)
        row.pack(fill="x")
        self.vpn_combo = ttk.Combobox(row, textvariable=self.vpn_var, state="readonly")
        self.vpn_combo.pack(side="left", fill="x", expand=True)
        ttk.Button(row, text="Actualizar", command=self.load_vpn_profiles).pack(side="left", padx=6)
        ttk.Button(row, text="Conectar", command=self.connect_vpn).pack(side="left")
        ttk.Button(row, text="Desconectar", command=self.disconnect_vpn).pack(side="left", padx=(6, 0))
        ttk.Label(vpn, textvariable=self.vpn_status_var).pack(anchor="w", pady=(8, 0))

        state = ttk.Frame(root)
        state.pack(fill="x", pady=(2, 12))
        ttk.Label(state, textvariable=self.engine_var).pack(anchor="w")
        ttk.Label(state, textvariable=self.status_var).pack(anchor="w", pady=(4, 0))

        buttons = ttk.Frame(root)
        buttons.pack(fill="x")
        self.play_btn = ttk.Button(buttons, text="REPRODUCIR", command=self.play)
        self.play_btn.pack(side="left", fill="x", expand=True, ipady=7)
        ttk.Button(buttons, text="DETENER", command=self.stop_player).pack(side="left", padx=(8, 0), ipady=7)
        ttk.Button(buttons, text="Comprobar motor", command=self.check_engine_async).pack(side="left", padx=(8, 0), ipady=7)

    def load_config(self):
        try:
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def save_config(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        data = {"last_ace": self.ace_var.get().strip(), "cache_seconds": max(60, int(self.cache_var.get())),
                "vpn_profile": self.vpn_var.get(), "fullscreen": self.fullscreen_var.get()}
        CONFIG_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def refresh_all(self):
        self.load_vpn_profiles()
        self.check_engine_async()

    def check_engine(self):
        url = f"http://{ENGINE_HOST}:{ENGINE_PORT}/webui/api/service?method=get_version"
        try:
            req = Request(url, headers={"User-Agent": APP_NAME})
            with urlopen(req, timeout=3) as res:
                data = json.loads(res.read().decode("utf-8", errors="replace"))
            version = data.get("result", {}).get("version", "desconocida")
            self.after(0, lambda: self.engine_var.set(f"Motor AceStream: conectado, versión {version}"))
            return True
        except Exception:
            self.after(0, lambda: self.engine_var.set("Motor AceStream: no disponible en 127.0.0.1:6878"))
            return False

    def check_engine_async(self):
        threading.Thread(target=self.check_engine, daemon=True).start()

    def find_mpv(self):
        candidates = [app_dir() / "mpv.exe", app_dir() / "mpv" / "mpv.exe"]
        for item in candidates:
            if item.exists():
                return str(item)
        from shutil import which
        return which("mpv")

    def normalize_ace(self, value):
        value = value.strip()
        if value.lower().startswith("acestream://"):
            value = value[len("acestream://"):]
        match = re.search(r"(?:[?&](?:id|content_id)=)([0-9a-fA-F]{40})", value)
        if match:
            value = match.group(1)
        if not re.fullmatch(r"[0-9a-fA-F]{40}", value):
            raise ValueError("Introduce un enlace acestream:// seguido de un ID hexadecimal de 40 caracteres.")
        return value.lower()

    def play(self):
        try:
            content_id = self.normalize_ace(self.ace_var.get())
            cache = max(60, int(self.cache_var.get()))
        except Exception as exc:
            messagebox.showerror(APP_NAME, str(exc))
            return
        mpv = self.find_mpv()
        if not mpv:
            messagebox.showerror(APP_NAME, "No encuentro mpv.exe. Ponlo junto a DRAP_ACE_PLAYER.exe o en la carpeta mpv.")
            return
        if not self.check_engine():
            messagebox.showerror(APP_NAME, "AceStream Engine no responde. Inícialo y vuelve a intentarlo.")
            return
        self.stop_player()
        stream_url = f"http://{ENGINE_HOST}:{ENGINE_PORT}/ace/getstream?id={quote(content_id)}"
        args = [mpv, stream_url, "--force-window=yes", "--cache=yes", f"--cache-secs={cache}",
                "--demuxer-max-bytes=256MiB", "--demuxer-readahead-secs=120", "--keep-open=no",
                "--title=DRAP ACE PLAYER"]
        if self.fullscreen_var.get():
            args.append("--fullscreen")
        try:
            self.mpv_process = subprocess.Popen(args, cwd=str(app_dir()))
            self.status_var.set(f"Reproduciendo con {cache} segundos de caché configurada")
            self.save_config()
        except Exception as exc:
            messagebox.showerror(APP_NAME, f"No se pudo iniciar MPV:\n{exc}")

    def stop_player(self):
        if self.mpv_process and self.mpv_process.poll() is None:
            self.mpv_process.terminate()
            try:
                self.mpv_process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.mpv_process.kill()
        self.mpv_process = None
        self.status_var.set("Reproducción detenida")

    def load_vpn_profiles(self):
        if os.name != "nt":
            return
        ps = "Get-VpnConnection -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Name; Get-VpnConnection -AllUserConnection -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Name"
        try:
            result = run_hidden(["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps])
            profiles = sorted(set(x.strip() for x in result.stdout.splitlines() if x.strip()))
            current = self.vpn_var.get()
            self.vpn_combo["values"] = profiles
            if current in profiles:
                self.vpn_var.set(current)
            elif profiles:
                self.vpn_var.set(profiles[0])
            self.update_vpn_status()
        except Exception as exc:
            self.vpn_status_var.set(f"VPN: no se pudieron leer los perfiles ({exc})")

    def update_vpn_status(self):
        name = self.vpn_var.get().strip()
        if not name:
            self.vpn_status_var.set("VPN: no hay perfiles configurados")
            return
        try:
            result = run_hidden(["rasdial"])
            connected = name.lower() in result.stdout.lower()
            self.vpn_status_var.set(f"VPN: {'conectada' if connected else 'desconectada'} ({name})")
        except Exception:
            self.vpn_status_var.set(f"VPN: estado desconocido ({name})")

    def connect_vpn(self):
        name = self.vpn_var.get().strip()
        if not name:
            messagebox.showwarning(APP_NAME, "No hay ningún perfil VPN de Windows seleccionado.")
            return
        def worker():
            self.after(0, lambda: self.vpn_status_var.set(f"VPN: conectando ({name})..."))
            result = run_hidden(["rasdial", name], timeout=45)
            self.after(0, self.update_vpn_status)
            if result.returncode != 0:
                msg = (result.stdout + "\n" + result.stderr).strip()
                self.after(0, lambda: messagebox.showerror(APP_NAME, "Windows no pudo conectar la VPN. Comprueba que el perfil tenga credenciales guardadas.\n\n" + msg))
        threading.Thread(target=worker, daemon=True).start()

    def disconnect_vpn(self):
        name = self.vpn_var.get().strip()
        if not name:
            return
        def worker():
            run_hidden(["rasdial", name, "/disconnect"], timeout=20)
            self.after(0, self.update_vpn_status)
        threading.Thread(target=worker, daemon=True).start()

    def on_close(self):
        try:
            self.save_config()
        except Exception:
            pass
        self.stop_player()
        self.destroy()


if __name__ == "__main__":
    DrapAcePlayer().mainloop()
