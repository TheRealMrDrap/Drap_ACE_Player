import base64,csv,io,json,os,re,shutil,subprocess,sys,threading,time,urllib.request,winreg,socket
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
APP='DRAP ACE PLAYER';VERSION='0.6.0';HOST='127.0.0.1';PORT=6878
CFGDIR=Path(os.getenv('APPDATA',Path.home()))/'DRAP Ace Player';CFG=CFGDIR/'config.json';VPNCFG=CFGDIR/'vpngate.ovpn';VPNLOG=CFGDIR/'openvpn.log';VPNAUTH=CFGDIR/'vpngate.auth'
VPNGATE_CSV='https://www.vpngate.net/api/iphone/';MPV_API='https://api.github.com/repos/zhongfly/mpv-winbuild/releases/latest'
REGIONS={'Automático':None,'Europa':{'ES','FR','PT','DE','IT','NL','BE','GB','IE','CH','AT','PL','CZ','SE','NO','FI','DK','RO','GR','UA'},'Asia':{'JP','KR','SG','IN','TH','VN','MY','ID','PH','TW','HK','TR'},'África':{'ZA','MA','EG','TN','KE','NG','GH'},'Sudamérica':{'AR','BR','CL','CO','PE','UY','PY','BO','EC','VE'},'Norteamérica':{'US','CA','MX','CR','PA','DO','PR'}}
def adir():return Path(sys.executable).resolve().parent if getattr(sys,'frozen',False) else Path(__file__).resolve().parent
def res(n):return Path(getattr(sys,'_MEIPASS',Path(__file__).resolve().parent))/n
def si():
 s=subprocess.STARTUPINFO();s.dwFlags|=subprocess.STARTF_USESHOWWINDOW;return s
def run(a,t=60):return subprocess.run(a,capture_output=True,text=True,timeout=t,startupinfo=si(),creationflags=0x08000000)
ctk.set_appearance_mode('dark');BG='#0b1018';PANEL='#121a26';PANEL2='#172231';BLUE='#1689ff';GREEN='#29c77d';TEXT='#f4f7fb';MUTED='#98a7ba';BORDER='#26364a';ORANGE='#e9a23b';RED='#ff5d68'
class App(ctk.CTk):
 def __init__(self):
  super().__init__();CFGDIR.mkdir(parents=True,exist_ok=True);self.player=self.vpnproc=self.engineproc=None
  self.title(f'{APP} v{VERSION}');self.geometry('1180x700');self.minsize(1100,680);self.configure(fg_color=BG)
  try:self.iconbitmap(str(res('MrDrap_Player.ico')));self._ico=tk.PhotoImage(file=str(res('MrDrap_Player_64.png')));self.iconphoto(True,self._ico)
  except:pass
  try:self.cfg=json.loads(CFG.read_text(encoding='utf8'))
  except:self.cfg={}
  self.ace=tk.StringVar(value=self.cfg.get('ace',''));self.cache=tk.StringVar(value=str(max(60,int(self.cfg.get('cache',60)))));self.fs=tk.BooleanVar(value=self.cfg.get('fs',False));self.region=tk.StringVar(value=self.cfg.get('region','Europa'));self.status=tk.StringVar(value='Preparado');self.engs=tk.StringVar(value='AceStream Engine: comprobando...');self.comps=tk.StringVar(value='Comprobando componentes...');self.vpns=tk.StringVar(value='VPN: desconectada')
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
  ctk.CTkLabel(head,text=APP,font=ctk.CTkFont('Segoe UI',24,'bold'),text_color=TEXT).pack(anchor='center');ctk.CTkLabel(head,text=f'v{VERSION}  •  AceStream + MPV + VPN opcional',text_color=MUTED).pack(anchor='center')
  quick=ctk.CTkFrame(root,fg_color='transparent');quick.pack(fill='x',pady=(7,7));ctk.CTkButton(quick,text='▶  REPRODUCIR',command=self.play,height=46,corner_radius=14,fg_color=BLUE,font=ctk.CTkFont('Segoe UI',15,'bold')).pack(side='left',fill='x',expand=True);ctk.CTkButton(quick,text='■  DETENER TODO',command=self.stop_all,width=210,height=46,corner_radius=14,fg_color='#1d2b3d',font=ctk.CTkFont('Segoe UI',14,'bold')).pack(side='left',padx=(10,0))
  cols=ctk.CTkFrame(root,fg_color='transparent');cols.pack(fill='both',expand=True);L=ctk.CTkFrame(cols,fg_color='transparent');L.pack(side='left',fill='both',expand=True,padx=(0,6));R=ctk.CTkFrame(cols,fg_color='transparent');R.pack(side='left',fill='both',expand=True,padx=(6,0))
  x=self.card(L);x.pack(fill='x',pady=(0,7));ctk.CTkLabel(x,text='Reproducción',font=ctk.CTkFont('Segoe UI',15,'bold'),text_color=TEXT).pack(anchor='w',padx=17,pady=(12,6));ctk.CTkEntry(x,textvariable=self.ace,height=42,corner_radius=12,fg_color=PANEL2,border_color=BORDER,placeholder_text='acestream://ID o Content ID',font=ctk.CTkFont('Consolas',12)).pack(fill='x',padx=17);r=ctk.CTkFrame(x,fg_color='transparent');r.pack(fill='x',padx=17,pady=(9,12));ctk.CTkLabel(r,text='Caché',text_color=MUTED).pack(side='left');ctk.CTkEntry(r,textvariable=self.cache,width=72,height=34,corner_radius=10,fg_color=PANEL2,border_color=BORDER,font=ctk.CTkFont('Segoe UI',12)).pack(side='left',padx=7);ctk.CTkLabel(r,text='segundos',text_color=MUTED).pack(side='left');ctk.CTkCheckBox(r,text='Pantalla completa',variable=self.fs,corner_radius=6).pack(side='right')
  x=self.card(L);x.pack(fill='x',pady=7);ctk.CTkLabel(x,text='AceStream Engine',font=ctk.CTkFont('Segoe UI',15,'bold'),text_color=TEXT).pack(anchor='w',padx=17,pady=(12,3));ctk.CTkLabel(x,textvariable=self.engs,text_color=MUTED).pack(anchor='w',padx=17);r=ctk.CTkFrame(x,fg_color='transparent');r.pack(fill='x',padx=17,pady=(8,12));self.b(r,'ARRANCAR ENGINE',self.start_engine,GREEN,180).pack(side='left');self.b(r,'DETENER ENGINE',self.stop_engine,'#1d2b3d',180).pack(side='left',padx=8)
  x=self.card(L);x.pack(fill='x',pady=7);ctk.CTkLabel(x,text='Componentes',font=ctk.CTkFont('Segoe UI',15,'bold'),text_color=TEXT).pack(anchor='w',padx=17,pady=(12,3));ctk.CTkLabel(x,textvariable=self.comps,text_color=MUTED).pack(anchor='w',padx=17);r=ctk.CTkFrame(x,fg_color='transparent');r.pack(fill='x',padx=17,pady=(8,12));self.b(r,'Instalar MPV',self.install_mpv).pack(side='left');self.b(r,'Instalar OpenVPN',self.install_openvpn,'#1d2b3d',180).pack(side='left',padx=8)
  x=self.card(R);x.pack(fill='x');ctk.CTkLabel(x,text='VPN pública VPN Gate  ·  opcional',font=ctk.CTkFont('Segoe UI',15,'bold'),text_color=TEXT).pack(anchor='w',padx=17,pady=(12,7));r=ctk.CTkFrame(x,fg_color='transparent');r.pack(fill='x',padx=17);ctk.CTkOptionMenu(r,variable=self.region,values=list(REGIONS),width=205,height=38,corner_radius=12,fg_color=PANEL2).pack(side='left');self.b(r,'CONECTAR',self.connect_vpn,GREEN,120).pack(side='left',padx=8);self.b(r,'DESCONECTAR',self.disconnect_vpn,'#1d2b3d',135).pack(side='left');ctk.CTkLabel(x,textvariable=self.vpns,text_color=TEXT).pack(anchor='w',padx=17,pady=(8,1));ctk.CTkLabel(x,text='VPN Gate usa servidores voluntarios. No uses credenciales ni información sensible.',text_color=ORANGE,font=ctk.CTkFont('Segoe UI',11)).pack(anchor='w',padx=17,pady=(0,11))
  x=self.card(R);x.pack(fill='both',expand=True,pady=(10,0));ctk.CTkLabel(x,text='Estado / diagnóstico',font=ctk.CTkFont('Segoe UI',15,'bold'),text_color=TEXT).pack(anchor='w',padx=17,pady=(12,6));ctk.CTkLabel(x,textvariable=self.status,text_color=TEXT,wraplength=505,justify='left').pack(anchor='w',padx=17)
 def engine_paths(self):
  e=[]
  for base in [os.getenv('APPDATA'),os.getenv('LOCALAPPDATA'),os.getenv('ProgramFiles'),os.getenv('ProgramFiles(x86)')]:
   if base:
    b=Path(base);e += [b/'ACEStream'/'engine'/'ace_engine.exe',b/'Ace Stream'/'engine'/'ace_engine.exe',b/'ACEStream'/'ace_engine.exe']
  return e
 def find_engine(self):
  for p in self.engine_paths():
   if p.exists():return p
 def engine_ok(self):
  try:urllib.request.urlopen(f'http://{HOST}:{PORT}/webui/api/service?method=get_version',timeout=2).read();self.engs.set('●  AceStream Engine conectado');return True
  except:self.engs.set('○  AceStream Engine detenido');return False
 def start_engine(self,automatic=False):
  if self.engine_ok():return True
  p=self.find_engine()
  if not p:self.status.set('No encuentro ace_engine.exe en las rutas habituales.');return False
  self.status.set(f'Arrancando AceStream Engine: {p}');self.engineproc=subprocess.Popen([str(p)],cwd=str(p.parent),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=0x08000000)
  for _ in range(24):
   time.sleep(.5)
   if self.engine_ok():self.status.set('AceStream Engine arrancado.');return True
  self.status.set('AceStream se inició pero no respondió en 6878.');return False
 def stop_engine(self):
  for n in ('ace_engine.exe','ace_console.exe'):
   try:run(['taskkill','/F','/T','/IM',n],15)
   except:pass
  self.engs.set('○  AceStream Engine detenido')
 def mpv(self):
  for p in [adir()/'mpv.exe',adir()/'mpv'/'mpv.exe']:
   if p.exists():return p
  w=shutil.which('mpv');return Path(w) if w else None
 def openvpn(self):
  paths=[Path(os.getenv('ProgramFiles','C:/Program Files'))/'OpenVPN'/'bin'/'openvpn.exe',Path(os.getenv('ProgramFiles(x86)','C:/Program Files (x86)'))/'OpenVPN'/'bin'/'openvpn.exe']
  for p in paths:
   if p.exists():return p
  w=shutil.which('openvpn');return Path(w) if w else None
 def refresh(self):self.comps.set(('MPV: instalado' if self.mpv() else 'MPV: falta')+'    •    '+('OpenVPN: instalado' if self.openvpn() else 'OpenVPN: falta'));self.engine_ok()
 def install_mpv(self):self.status.set('Consultando MPV...');threading.Thread(target=self._mpv,daemon=True).start()
 def _mpv(self):
  try:
   d=json.loads(urllib.request.urlopen(urllib.request.Request(MPV_API,headers={'User-Agent':APP}),timeout=20).read());a=next(x for x in d['assets'] if re.fullmatch(r'mpv-x86_64-[^/]+\.7z',x['name']));dest=adir()/'mpv';dest.mkdir(exist_ok=True);arc=adir()/a['name'];urllib.request.urlretrieve(a['browser_download_url'],arc);tool=shutil.which('tar') or shutil.which('7z');x=run([tool,'-xf',str(arc),'-C',str(dest)] if 'tar' in Path(tool).name.lower() else [tool,'x','-y',f'-o{dest}',str(arc)],180);arc.unlink(missing_ok=True);p=next(dest.rglob('mpv.exe'));shutil.copy2(p,dest/'mpv.exe') if p!=dest/'mpv.exe' else None;self.after(0,self.refresh);self.after(0,lambda:self.status.set('MPV instalado correctamente.'))
  except Exception as e:self.after(0,lambda m=str(e):self.status.set('Error MPV: '+m))
 def install_openvpn(self):
  if not shutil.which('winget'):self.status.set('Winget no disponible para instalar OpenVPN.');return
  self.status.set('Instalando OpenVPN Community...');threading.Thread(target=lambda:(run(['winget','install','-e','--id','OpenVPNTechnologies.OpenVPN','--accept-package-agreements','--accept-source-agreements'],600),self.after(0,self.refresh)),daemon=True).start()
 def servers(self):
  raw=urllib.request.urlopen(urllib.request.Request(VPNGATE_CSV,headers={'User-Agent':'Mozilla/5.0 DRAP-ACE-PLAYER'}),timeout=25).read().decode('utf-8-sig',errors='replace');lines=[x for x in raw.splitlines() if x and not x.startswith('*')]
  # Header de VPN Gate empieza por #HostName: se normaliza antes de DictReader.
  if lines and lines[0].startswith('#'):lines[0]=lines[0][1:]
  rows=list(csv.DictReader(io.StringIO('\n'.join(lines))));allow=REGIONS[self.region.get()];out=[]
  for r in rows:
   b64=r.get('OpenVPN_ConfigData_Base64','');cc=(r.get('CountryShort') or '').upper()
   if not b64 or (allow and cc not in allow):continue
   try:r['_score']=int(r.get('Score') or 0);r['_speed']=int(r.get('Speed') or 0);base64.b64decode(b64,validate=True);out.append(r)
   except:pass
  return sorted(out,key=lambda x:(x['_score'],x['_speed']),reverse=True)
 def internet_ip(self):
  try:return urllib.request.urlopen('https://api.ipify.org',timeout=8).read().decode().strip()
  except:return 'desconocida'
 def connect_vpn(self):
  if not self.openvpn():self.status.set('OpenVPN no está instalado o no se encuentra openvpn.exe.');return
  self.disconnect_vpn();self.vpns.set('VPN: buscando servidores...');self.status.set('Descargando lista VPN Gate...');threading.Thread(target=self._vpn,daemon=True).start()
 def _vpn(self):
  try:
   ss=self.servers();self.after(0,lambda n=len(ss):self.status.set(f'VPN Gate: {n} servidores candidatos. Probando conexión...'))
   if not ss:raise RuntimeError('No hay servidores OpenVPN para la región elegida.')
   VPNAUTH.write_text('vpn\nvpn\n',encoding='ascii')
   errors=[]
   for idx,s in enumerate(ss[:8],1):
    name=s.get('CountryLong') or s.get('CountryShort') or 'Servidor';self.after(0,lambda i=idx,n=name:self.vpns.set(f'VPN: probando {i}/8 · {n}...'))
    cfg=base64.b64decode(s['OpenVPN_ConfigData_Base64']).decode('utf-8',errors='replace')
    # Algunas configuraciones de VPN Gate piden usuario/clave. VPN Gate publica vpn/vpn para esos perfiles.
    if re.search(r'^auth-user-pass\s*$',cfg,re.M):cfg=re.sub(r'^auth-user-pass\s*$',f'auth-user-pass "{VPNAUTH}"',cfg,flags=re.M)
    VPNCFG.write_text(cfg,encoding='utf-8');VPNLOG.write_text('',encoding='utf-8')
    cmd=[str(self.openvpn()),'--config',str(VPNCFG),'--auth-nocache','--connect-retry-max','1','--connect-timeout','10','--verb','3','--log',str(VPNLOG)]
    self.vpnproc=subprocess.Popen(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=0x08000000)
    ok=False
    for _ in range(22):
     time.sleep(1);log=VPNLOG.read_text(encoding='utf-8',errors='ignore') if VPNLOG.exists() else ''
     if 'Initialization Sequence Completed' in log:ok=True;break
     if self.vpnproc.poll() is not None:break
    if ok:
     ip=self.internet_ip();self.after(0,lambda n=name,i=ip:self.vpns.set(f'VPN: CONECTADA · {n} · IP {i}'));self.after(0,lambda:self.status.set('VPN conectada y OpenVPN completó la inicialización.'));return
    log=VPNLOG.read_text(encoding='utf-8',errors='ignore') if VPNLOG.exists() else '';errors.append(next((z for z in reversed(log.splitlines()) if 'ERROR' in z.upper() or 'AUTH_FAILED' in z or 'TLS Error' in z), 'sin detalle'))
    self.disconnect_vpn(silent=True)
   raise RuntimeError('Fallaron los servidores probados. Último error OpenVPN: '+errors[-1])
  except Exception as e:self.after(0,lambda m=str(e):self.status.set('VPN ERROR: '+m));self.after(0,lambda:self.vpns.set('VPN: desconectada'))
 def disconnect_vpn(self,silent=False):
  if self.vpnproc and self.vpnproc.poll() is None:
   try:self.vpnproc.terminate();self.vpnproc.wait(5)
   except:
    try:self.vpnproc.kill()
    except:pass
  self.vpnproc=None
  if not silent:self.vpns.set('VPN: desconectada')
 def cid(self):
  s=re.sub(r'^acestream://','',self.ace.get().strip(),flags=re.I);m=re.search(r'[?&](?:id|content_id)=([0-9a-fA-F]{40})',s);s=m.group(1) if m else s
  if not re.fullmatch(r'[0-9a-fA-F]{40}',s):raise ValueError('El ACE debe contener un Content ID hexadecimal de 40 caracteres.')
  return s.lower()
 def play(self):
  try:c=self.cid();cache=max(60,int(self.cache.get()))
  except Exception as e:self.status.set(str(e));return
  if not self.mpv():self.status.set('Falta MPV. Pulsa Instalar MPV.');return
  self.status.set('Preparando AceStream Engine...');self.update_idletasks()
  if not self.start_engine(True):return
  self.stop_player();a=[str(self.mpv()),f'http://{HOST}:{PORT}/ace/getstream?id={c}','--force-window=yes','--cache=yes',f'--cache-secs={cache}','--demuxer-max-bytes=256MiB','--demuxer-readahead-secs=120','--title=DRAP ACE PLAYER'];a+=['--fullscreen'] if self.fs.get() else [];self.player=subprocess.Popen(a,cwd=str(adir()));self.status.set(f'Reproduciendo · caché {cache} s');self.save()
 def stop_player(self):
  if self.player and self.player.poll() is None:self.player.terminate()
  self.player=None
 def stop_all(self):self.stop_player();self.stop_engine();self.status.set('Reproducción y AceStream Engine detenidos.')
 def save(self):CFG.write_text(json.dumps({'ace':self.ace.get(),'cache':max(60,int(self.cache.get())),'fs':self.fs.get(),'region':self.region.get()},ensure_ascii=False,indent=2),encoding='utf8')
 def close(self):
  try:self.save()
  except:pass
  self.stop_player();self.stop_engine();self.disconnect_vpn();self.destroy()
if __name__=='__main__':App().mainloop()
