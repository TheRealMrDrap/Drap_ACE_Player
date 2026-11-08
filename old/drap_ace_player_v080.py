import json,os,re,shutil,subprocess,sys,threading,time,urllib.request
from pathlib import Path
import tkinter as tk
import customtkinter as ctk
APP='DRAP ACE PLAYER';VERSION='0.8.0';HOST='127.0.0.1';PORT=6878
CFGDIR=Path(os.getenv('APPDATA',Path.home()))/'DRAP Ace Player';CFG=CFGDIR/'config.json';MPV_API='https://api.github.com/repos/zhongfly/mpv-winbuild/releases/latest'
def adir():return Path(sys.executable).resolve().parent if getattr(sys,'frozen',False) else Path(__file__).resolve().parent
def res(n):return Path(getattr(sys,'_MEIPASS',Path(__file__).resolve().parent))/n
def si():
 s=subprocess.STARTUPINFO();s.dwFlags|=subprocess.STARTF_USESHOWWINDOW;return s
def run(a,t=60):return subprocess.run(a,capture_output=True,text=True,timeout=t,startupinfo=si(),creationflags=0x08000000)
ctk.set_appearance_mode('dark');BG='#0b1018';PANEL='#121a26';PANEL2='#172231';BLUE='#1689ff';GREEN='#29c77d';TEXT='#f4f7fb';MUTED='#98a7ba';BORDER='#26364a'
class App(ctk.CTk):
 def __init__(self):
  super().__init__();CFGDIR.mkdir(parents=True,exist_ok=True);self.player=self.engineproc=None
  self.title(f'{APP} v{VERSION}');self.geometry('1180x700');self.minsize(1100,680);self.configure(fg_color=BG)
  try:self.iconbitmap(str(res('MrDrap_Player.ico')));self._ico=tk.PhotoImage(file=str(res('MrDrap_Player_64.png')));self.iconphoto(True,self._ico)
  except:pass
  try:self.cfg=json.loads(CFG.read_text(encoding='utf8'))
  except:self.cfg={}
  self.ace=tk.StringVar(value=self.cfg.get('ace',''));self.cache=tk.StringVar(value=str(max(60,int(self.cfg.get('cache',60)))));self.fs=tk.BooleanVar(value=self.cfg.get('fs',False));self.engs=tk.StringVar(value='AceStream Engine: comprobando...');self.comps=tk.StringVar(value='MPV: comprobando...')
  self.ui();self.after(350,self.refresh);self.protocol('WM_DELETE_WINDOW',self.close)
 def card(self,p):return ctk.CTkFrame(p,fg_color=PANEL,corner_radius=18,border_width=1,border_color=BORDER)
 def b(self,p,t,cmd,color=BLUE,w=150):return ctk.CTkButton(p,text=t,command=cmd,width=w,height=38,corner_radius=12,fg_color=color,hover_color='#0871dc' if color==BLUE else '#213247',font=ctk.CTkFont('Segoe UI',13,'bold'))
 def ui(self):
  root=ctk.CTkFrame(self,fg_color='transparent');root.pack(fill='both',expand=True,padx=26,pady=10)
  head=ctk.CTkFrame(root,fg_color='transparent');head.pack(fill='x')
  try:
   from PIL import Image
   self.logo=ctk.CTkImage(Image.open(res('MrDrap_Player_256.png')),size=(95,95));ctk.CTkLabel(head,text='',image=self.logo).pack(anchor='center')
  except:pass
  ctk.CTkLabel(head,text=APP,font=ctk.CTkFont('Segoe UI',24,'bold'),text_color=TEXT).pack(anchor='center');ctk.CTkLabel(head,text=f'v{VERSION}  •  AceStream + MPV',text_color=MUTED).pack(anchor='center')
  q=ctk.CTkFrame(root,fg_color='transparent');q.pack(fill='x',pady=(7,7));ctk.CTkButton(q,text='▶  REPRODUCIR',command=self.play,height=46,corner_radius=14,fg_color=BLUE,font=ctk.CTkFont('Segoe UI',15,'bold')).pack(side='left',fill='x',expand=True);ctk.CTkButton(q,text='■  DETENER TODO',command=self.stop_all,width=210,height=46,corner_radius=14,fg_color='#1d2b3d',font=ctk.CTkFont('Segoe UI',14,'bold')).pack(side='left',padx=(10,0))
  cols=ctk.CTkFrame(root,fg_color='transparent');cols.pack(fill='both',expand=True);L=ctk.CTkFrame(cols,fg_color='transparent');L.pack(side='left',fill='both',expand=True,padx=(0,6));R=ctk.CTkFrame(cols,fg_color='transparent');R.pack(side='left',fill='both',expand=True,padx=(6,0))
  x=self.card(L);x.pack(fill='x',pady=(0,7));ctk.CTkLabel(x,text='Reproducción',font=ctk.CTkFont('Segoe UI',15,'bold'),text_color=TEXT).pack(anchor='w',padx=17,pady=(12,6));ctk.CTkEntry(x,textvariable=self.ace,height=42,corner_radius=12,fg_color=PANEL2,border_color=BORDER,placeholder_text='acestream://ID o Content ID',font=ctk.CTkFont('Consolas',12)).pack(fill='x',padx=17);r=ctk.CTkFrame(x,fg_color='transparent');r.pack(fill='x',padx=17,pady=(9,12));ctk.CTkLabel(r,text='Caché',text_color=MUTED).pack(side='left');ctk.CTkEntry(r,textvariable=self.cache,width=72,height=34,corner_radius=10,fg_color=PANEL2,border_color=BORDER,font=ctk.CTkFont('Segoe UI',12)).pack(side='left',padx=7);ctk.CTkLabel(r,text='segundos',text_color=MUTED).pack(side='left');ctk.CTkCheckBox(r,text='Pantalla completa',variable=self.fs,corner_radius=6).pack(side='right')
  x=self.card(L);x.pack(fill='x',pady=7);ctk.CTkLabel(x,text='AceStream Engine',font=ctk.CTkFont('Segoe UI',15,'bold'),text_color=TEXT).pack(anchor='w',padx=17,pady=(12,3));ctk.CTkLabel(x,textvariable=self.engs,text_color=MUTED).pack(anchor='w',padx=17);r=ctk.CTkFrame(x,fg_color='transparent');r.pack(fill='x',padx=17,pady=(8,12));self.b(r,'ARRANCAR ENGINE',self.start_engine,GREEN,180).pack(side='left');self.b(r,'DETENER ENGINE',self.stop_engine,'#1d2b3d',180).pack(side='left',padx=8)
  x=self.card(L);x.pack(fill='x',pady=7);ctk.CTkLabel(x,text='Componentes',font=ctk.CTkFont('Segoe UI',15,'bold'),text_color=TEXT).pack(anchor='w',padx=17,pady=(12,3));ctk.CTkLabel(x,textvariable=self.comps,text_color=MUTED).pack(anchor='w',padx=17);r=ctk.CTkFrame(x,fg_color='transparent');r.pack(fill='x',padx=17,pady=(8,12));self.b(r,'Instalar MPV',self.install_mpv).pack(side='left')
  x=self.card(R);x.pack(fill='both',expand=True);h=ctk.CTkFrame(x,fg_color='transparent');h.pack(fill='x',padx=17,pady=(12,6));ctk.CTkLabel(h,text='Registro de actividad',font=ctk.CTkFont('Segoe UI',15,'bold'),text_color=TEXT).pack(side='left');self.b(h,'LIMPIAR',self.clear_log,'#1d2b3d',90).pack(side='right')
  self.logbox=ctk.CTkTextbox(x,fg_color='#0d141f',border_width=1,border_color=BORDER,corner_radius=12,font=ctk.CTkFont('Consolas',11),text_color='#dce7f5',wrap='word');self.logbox.pack(fill='both',expand=True,padx=17,pady=(0,15));self.logbox.configure(state='disabled');self.log('DRAP ACE PLAYER iniciado.')
 def log(self,msg):
  line=f'[{time.strftime("%H:%M:%S")}] {msg}\n'
  def put():self.logbox.configure(state='normal');self.logbox.insert('1.0',line);self.logbox.configure(state='disabled');self.logbox.yview_moveto(0)
  put() if threading.current_thread() is threading.main_thread() else self.after(0,put)
 def clear_log(self):self.logbox.configure(state='normal');self.logbox.delete('1.0','end');self.logbox.configure(state='disabled');self.log('Registro limpiado.')
 def engine_paths(self):
  e=[]
  for base in [os.getenv('APPDATA'),os.getenv('LOCALAPPDATA'),os.getenv('ProgramFiles'),os.getenv('ProgramFiles(x86)')]:
   if base:
    b=Path(base);e += [b/'ACEStream'/'engine'/'ace_console.exe',b/'Ace Stream'/'engine'/'ace_console.exe',b/'ACEStream'/'engine'/'ace_engine.exe',b/'Ace Stream'/'engine'/'ace_engine.exe',b/'ACEStream'/'ace_engine.exe']
  return e
 def find_engine(self):
  for p in self.engine_paths():
   if p.exists():return p
 def engine_ok(self):
  try:urllib.request.urlopen(f'http://{HOST}:{PORT}/webui/api/service?method=get_version',timeout=2).read();self.engs.set('●  AceStream Engine conectado');return True
  except:self.engs.set('○  AceStream Engine detenido');self.log('AceStream Engine detenido.');return False
 def start_engine(self,automatic=False):
  if self.engine_ok():return True
  p=self.find_engine()
  if not p:self.log('ERROR: no encuentro AceStream Engine en las rutas habituales.');return False
  self.log(f'Arrancando AceStream Engine: {p}');args=[str(p),'--client-console'] if p.name.lower()=='ace_console.exe' else [str(p)];self.engineproc=subprocess.Popen(args,cwd=str(p.parent),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,stdin=subprocess.DEVNULL,creationflags=0x08000000)
  for _ in range(24):
   time.sleep(.5)
   if self.engine_ok():self.log('AceStream Engine arrancado y API 6878 operativa.');return True
  self.log('ERROR: AceStream se inició pero no respondió en 127.0.0.1:6878.');return False
 def stop_engine(self):
  for n in ('ace_engine.exe','ace_console.exe'):
   try:run(['taskkill','/F','/T','/IM',n],15)
   except:pass
  self.engs.set('○  AceStream Engine detenido');self.log('AceStream Engine detenido.')
 def mpv(self):
  for p in [adir()/'mpv.exe',adir()/'mpv'/'mpv.exe']:
   if p.exists():return p
  w=shutil.which('mpv');return Path(w) if w else None
 def refresh(self):
  self.comps.set('MPV: instalado' if self.mpv() else 'MPV: falta');self.log('Comprobación de componentes: '+self.comps.get());self.engine_ok()
 def install_mpv(self):self.log('Consultando última versión de MPV...');threading.Thread(target=self._mpv,daemon=True).start()
 def _mpv(self):
  try:
   d=json.loads(urllib.request.urlopen(urllib.request.Request(MPV_API,headers={'User-Agent':APP}),timeout=20).read());a=next(x for x in d['assets'] if re.fullmatch(r'mpv-x86_64-[^/]+\.7z',x['name']));dest=adir()/'mpv';dest.mkdir(exist_ok=True);arc=adir()/a['name'];urllib.request.urlretrieve(a['browser_download_url'],arc);tool=shutil.which('tar') or shutil.which('7z');x=run([tool,'-xf',str(arc),'-C',str(dest)] if 'tar' in Path(tool).name.lower() else [tool,'x','-y',f'-o{dest}',str(arc)],180);arc.unlink(missing_ok=True);p=next(dest.rglob('mpv.exe'));shutil.copy2(p,dest/'mpv.exe') if p!=dest/'mpv.exe' else None;self.after(0,self.refresh);self.log('MPV instalado correctamente.')
  except Exception as e:self.log('ERROR instalando MPV: '+str(e))
 def cid(self):
  s=re.sub(r'^acestream://','',self.ace.get().strip(),flags=re.I);m=re.search(r'[?&](?:id|content_id)=([0-9a-fA-F]{40})',s);s=m.group(1) if m else s
  if not re.fullmatch(r'[0-9a-fA-F]{40}',s):raise ValueError('El ACE debe contener un Content ID hexadecimal de 40 caracteres.')
  return s.lower()
 def play(self):
  try:c=self.cid();cache=max(60,int(self.cache.get()))
  except Exception as e:self.log('ERROR: '+str(e));return
  if not self.mpv():self.log('ERROR: falta MPV. Pulsa Instalar MPV.');return
  self.log('Preparando AceStream Engine...');self.update_idletasks()
  if not self.start_engine(True):return
  self.stop_player();a=[str(self.mpv()),f'http://{HOST}:{PORT}/ace/getstream?id={c}','--force-window=yes','--cache=yes',f'--cache-secs={cache}','--demuxer-max-bytes=256MiB','--demuxer-readahead-secs=120','--title=DRAP ACE PLAYER'];a+=['--fullscreen'] if self.fs.get() else [];self.player=subprocess.Popen(a,cwd=str(adir()));self.log(f'Reproducción iniciada. Content ID: {c} · caché configurada: {cache} s');self.save()
 def stop_player(self):
  if self.player and self.player.poll() is None:self.player.terminate()
  self.player=None
 def stop_all(self):
  self.stop_player();self.log('MPV detenido.');self.stop_engine();self.log('DETENER TODO completado.')
 def save(self):
  CFG.write_text(json.dumps({'ace':self.ace.get(),'cache':max(60,int(self.cache.get())),'fs':self.fs.get()},ensure_ascii=False,indent=2),encoding='utf8')
 def close(self):
  try:self.save()
  except:pass
  self.stop_player();self.stop_engine();self.destroy()
if __name__=='__main__':App().mainloop()
