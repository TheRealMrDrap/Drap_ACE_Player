import base64,csv,io,json,os,re,shutil,subprocess,sys,threading,time,urllib.request,winreg
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
APP='DRAP ACE PLAYER';VERSION='0.5.0';HOST='127.0.0.1';PORT=6878
CFGDIR=Path(os.getenv('APPDATA',Path.home()))/'DRAP Ace Player';CFG=CFGDIR/'config.json';VPNCFG=CFGDIR/'vpngate.ovpn';VPNLOG=CFGDIR/'openvpn.log'
VPNGATE_CSV='https://www.vpngate.net/api/iphone/';MPV_API='https://api.github.com/repos/zhongfly/mpv-winbuild/releases/latest'
REGIONS={'Automático':None,'Europa':{'ES','FR','PT','DE','IT','NL','BE','GB','IE','CH','AT','PL','CZ','SE','NO','FI','DK','RO','GR','UA'},'Asia':{'JP','KR','SG','IN','TH','VN','MY','ID','PH','TW','HK','TR'},'África':{'ZA','MA','EG','TN','KE','NG','GH'},'Sudamérica':{'AR','BR','CL','CO','PE','UY','PY','BO','EC','VE'},'Norteamérica':{'US','CA','MX','CR','PA','DO','PR'}}
def adir():return Path(sys.executable).resolve().parent if getattr(sys,'frozen',False) else Path(__file__).resolve().parent
def res(n):return Path(getattr(sys,'_MEIPASS',Path(__file__).resolve().parent))/n
def si():
 s=subprocess.STARTUPINFO();s.dwFlags|=subprocess.STARTF_USESHOWWINDOW;return s
def run(a,t=60):return subprocess.run(a,capture_output=True,text=True,timeout=t,startupinfo=si(),creationflags=0x08000000)
ctk.set_appearance_mode('dark');BG='#0b1018';PANEL='#121a26';PANEL2='#172231';BLUE='#1689ff';GREEN='#29c77d';TEXT='#f4f7fb';MUTED='#98a7ba';BORDER='#26364a';ORANGE='#e9a23b'
class App(ctk.CTk):
 def __init__(self):
  super().__init__();CFGDIR.mkdir(parents=True,exist_ok=True);self.player=None;self.vpnproc=None;self.engineproc=None
  self.title(f'{APP} v{VERSION}');self.geometry('1180x700');self.minsize(1100,680);self.configure(fg_color=BG)
  try:self.iconbitmap(str(res('MrDrap_Player.ico')));self._ico=tk.PhotoImage(file=str(res('MrDrap_Player_64.png')));self.iconphoto(True,self._ico)
  except:pass
  try:self.cfg=json.loads(CFG.read_text(encoding='utf8'))
  except:self.cfg={}
  self.ace=tk.StringVar(value=self.cfg.get('ace',''));self.cache=tk.StringVar(value=str(max(60,int(self.cfg.get('cache',60)))));self.fs=tk.BooleanVar(value=self.cfg.get('fs',False));self.region=tk.StringVar(value=self.cfg.get('region','Europa'));self.status=tk.StringVar(value='Preparado');self.engs=tk.StringVar(value='AceStream Engine: comprobando...');self.comps=tk.StringVar(value='Comprobando componentes...');self.vpns=tk.StringVar(value='VPN: desconectada')
  self.ui();self.after(400,self.refresh);self.protocol('WM_DELETE_WINDOW',self.close)
 def card(self,p):return ctk.CTkFrame(p,fg_color=PANEL,corner_radius=18,border_width=1,border_color=BORDER)
 def button(self,p,t,c,color=BLUE,w=160):return ctk.CTkButton(p,text=t,command=c,width=w,height=38,corner_radius=12,fg_color=color,hover_color='#0871dc' if color==BLUE else '#213247',font=ctk.CTkFont('Segoe UI',13,'bold'))
 def ui(self):
  root=ctk.CTkFrame(self,fg_color='transparent');root.pack(fill='both',expand=True,padx=28,pady=14)
  head=ctk.CTkFrame(root,fg_color='transparent');head.pack(fill='x',pady=(0,8))
  try:
   from PIL import Image
   self.logo=ctk.CTkImage(Image.open(res('MrDrap_Player_256.png')),size=(112,112));ctk.CTkLabel(head,text='',image=self.logo).pack(anchor='center')
  except:pass
  ctk.CTkLabel(head,text=APP,font=ctk.CTkFont('Segoe UI',25,'bold'),text_color=TEXT).pack(anchor='center',pady=(0,1));ctk.CTkLabel(head,text=f'v{VERSION}  •  AceStream + MPV + VPN opcional',text_color=MUTED).pack(anchor='center')
  cols=ctk.CTkFrame(root,fg_color='transparent');cols.pack(fill='both',expand=True,pady=(8,5));left=ctk.CTkFrame(cols,fg_color='transparent');left.pack(side='left',fill='both',expand=True,padx=(0,6));right=ctk.CTkFrame(cols,fg_color='transparent');right.pack(side='left',fill='both',expand=True,padx=(6,0))
  x=self.card(left);x.pack(fill='x',pady=(0,8));ctk.CTkLabel(x,text='Reproducción',font=ctk.CTkFont('Segoe UI',15,'bold'),text_color=TEXT).pack(anchor='w',padx=17,pady=(13,7));ctk.CTkEntry(x,textvariable=self.ace,height=41,corner_radius=12,fg_color=PANEL2,border_color=BORDER,placeholder_text='acestream://ID o Content ID',font=ctk.CTkFont('Consolas',11)).pack(fill='x',padx=17);r=ctk.CTkFrame(x,fg_color='transparent');r.pack(fill='x',padx=17,pady=(10,13));ctk.CTkLabel(r,text='Caché',text_color=MUTED).pack(side='left');ctk.CTkEntry(r,textvariable=self.cache,width=72,height=34,corner_radius=10,fg_color=PANEL2,border_color=BORDER).pack(side='left',padx=7);ctk.CTkLabel(r,text='segundos',text_color=MUTED).pack(side='left');ctk.CTkCheckBox(r,text='Pantalla completa',variable=self.fs,corner_radius=6).pack(side='right')
  x=self.card(left);x.pack(fill='x',pady=8);ctk.CTkLabel(x,text='AceStream Engine',font=ctk.CTkFont('Segoe UI',15,'bold'),text_color=TEXT).pack(anchor='w',padx=17,pady=(13,4));ctk.CTkLabel(x,textvariable=self.engs,text_color=MUTED).pack(anchor='w',padx=17);r=ctk.CTkFrame(x,fg_color='transparent');r.pack(fill='x',padx=17,pady=(9,13));self.button(r,'ARRANCAR ENGINE',self.start_engine,GREEN,180).pack(side='left');self.button(r,'DETENER ENGINE',self.stop_engine,'#1d2b3d',180).pack(side='left',padx=8)
  x=self.card(left);x.pack(fill='x',pady=8);ctk.CTkLabel(x,text='Componentes',font=ctk.CTkFont('Segoe UI',15,'bold'),text_color=TEXT).pack(anchor='w',padx=17,pady=(13,4));ctk.CTkLabel(x,textvariable=self.comps,text_color=MUTED).pack(anchor='w',padx=17);r=ctk.CTkFrame(x,fg_color='transparent');r.pack(fill='x',padx=17,pady=(9,13));self.button(r,'Instalar MPV',self.install_mpv).pack(side='left');self.button(r,'Instalar OpenVPN',self.install_openvpn,'#1d2b3d',180).pack(side='left',padx=8)
  x=self.card(right);x.pack(fill='x');ctk.CTkLabel(x,text='VPN pública VPN Gate  ·  opcional',font=ctk.CTkFont('Segoe UI',15,'bold'),text_color=TEXT).pack(anchor='w',padx=17,pady=(13,9));r=ctk.CTkFrame(x,fg_color='transparent');r.pack(fill='x',padx=17);ctk.CTkOptionMenu(r,variable=self.region,values=list(REGIONS),width=210,height=38,corner_radius=12,fg_color=PANEL2).pack(side='left');self.button(r,'CONECTAR',self.connect_vpn,GREEN,120).pack(side='left',padx=8);self.button(r,'DESCONECTAR',self.disconnect_vpn,'#1d2b3d',135).pack(side='left');ctk.CTkLabel(x,textvariable=self.vpns,text_color=TEXT).pack(anchor='w',padx=17,pady=(10,2));ctk.CTkLabel(x,text='Servidores voluntarios: no uses credenciales ni información sensible.',text_color=ORANGE,font=ctk.CTkFont('Segoe UI',11)).pack(anchor='w',padx=17,pady=(0,13))
  x=self.card(right);x.pack(fill='both',expand=True,pady=(12,0));ctk.CTkLabel(x,text='Estado',font=ctk.CTkFont('Segoe UI',15,'bold'),text_color=TEXT).pack(anchor='w',padx=17,pady=(13,6));ctk.CTkLabel(x,textvariable=self.status,text_color=TEXT,wraplength=500,justify='left').pack(anchor='w',padx=17)
  r=ctk.CTkFrame(root,fg_color='transparent');r.pack(fill='x',pady=(8,0));ctk.CTkButton(r,text='▶  REPRODUCIR',command=self.play,height=48,corner_radius=15,fg_color=BLUE,font=ctk.CTkFont('Segoe UI',15,'bold')).pack(side='left',fill='x',expand=True);ctk.CTkButton(r,text='■  DETENER TODO',command=self.stop_all,width=205,height=48,corner_radius=15,fg_color='#1d2b3d',font=ctk.CTkFont('Segoe UI',14,'bold')).pack(side='left',padx=(10,0))
 def engine_paths(self):
  e=[]
  for base in [os.getenv('APPDATA'),os.getenv('LOCALAPPDATA'),os.getenv('ProgramFiles'),os.getenv('ProgramFiles(x86)')]:
   if base:
    b=Path(base);e += [b/'ACEStream'/'engine'/'ace_engine.exe',b/'Ace Stream'/'engine'/'ace_engine.exe',b/'ACEStream'/'ace_engine.exe']
  for root in (winreg.HKEY_CURRENT_USER,winreg.HKEY_LOCAL_MACHINE):
   for key in (r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall',r'SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall'):
    try:
     k=winreg.OpenKey(root,key)
     for i in range(winreg.QueryInfoKey(k)[0]):
      try:
       s=winreg.OpenKey(k,winreg.EnumKey(k,i));name=str(winreg.QueryValueEx(s,'DisplayName')[0])
       if 'ace stream' in name.lower() or 'acestream' in name.lower():
        loc=Path(winreg.QueryValueEx(s,'InstallLocation')[0]);e += [loc/'engine'/'ace_engine.exe',loc/'ace_engine.exe']
      except OSError:pass
    except OSError:pass
  seen=[]
  for p in e:
   if p not in seen:seen.append(p)
  return seen
 def find_engine(self):
  for p in self.engine_paths():
   if p.exists():return p
  return None
 def engine_ok(self):
  try:urllib.request.urlopen(f'http://{HOST}:{PORT}/webui/api/service?method=get_version',timeout=2).read();self.engs.set('●  AceStream Engine conectado');return True
  except:self.engs.set('○  AceStream Engine detenido o sin respuesta');return False
 def start_engine(self,automatic=False):
  if self.engine_ok():return True
  p=self.find_engine()
  if not p:
   if not automatic:messagebox.showerror(APP,'No encuentro ace_engine.exe. Comprueba que AceStream Engine esté instalado.')
   self.status.set('No se encontró AceStream Engine en las rutas de instalación habituales.');return False
  try:
   self.status.set(f'Arrancando AceStream Engine desde {p}...');self.engineproc=subprocess.Popen([str(p)],cwd=str(p.parent),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=0x08000000)
   for _ in range(20):
    time.sleep(.5)
    if self.engine_ok():self.status.set('AceStream Engine arrancado correctamente.');return True
   self.status.set('AceStream Engine se abrió, pero la API no respondió en el puerto 6878.');return False
  except Exception as e:self.status.set(f'No se pudo arrancar AceStream Engine: {e}');return False
 def stop_engine(self):
  for n in ('ace_engine.exe','ace_console.exe'):
   try:run(['taskkill','/F','/T','/IM',n],15)
   except:pass
  self.engineproc=None;self.engs.set('○  AceStream Engine detenido');self.status.set('AceStream Engine detenido.')
 def mpv(self):
  for p in [adir()/'mpv.exe',adir()/'mpv'/'mpv.exe']:
   if p.exists():return p
  w=shutil.which('mpv');return Path(w) if w else None
 def openvpn(self):
  p=Path(os.getenv('ProgramFiles','C:/Program Files'))/'OpenVPN'/'bin'/'openvpn.exe';return p if p.exists() else (Path(shutil.which('openvpn')) if shutil.which('openvpn') else None)
 def refresh(self):self.comps.set(('MPV: instalado' if self.mpv() else 'MPV: falta')+'    •    '+('OpenVPN: instalado' if self.openvpn() else 'OpenVPN: falta'));self.engine_ok()
 def install_mpv(self):self.status.set('Consultando MPV...');threading.Thread(target=self._mpv,daemon=True).start()
 def _mpv(self):
  try:
   d=json.loads(urllib.request.urlopen(urllib.request.Request(MPV_API,headers={'User-Agent':APP}),timeout=20).read());a=next(x for x in d['assets'] if re.fullmatch(r'mpv-x86_64-[^/]+\.7z',x['name']));dest=adir()/'mpv';dest.mkdir(exist_ok=True);arc=adir()/a['name'];urllib.request.urlretrieve(a['browser_download_url'],arc);tool=shutil.which('tar') or shutil.which('7z');x=run([tool,'-xf',str(arc),'-C',str(dest)] if Path(tool).name.lower().startswith('tar') else [tool,'x','-y',f'-o{dest}',str(arc)],180);arc.unlink(missing_ok=True);p=next(dest.rglob('mpv.exe'));shutil.copy2(p,dest/'mpv.exe') if p!=dest/'mpv.exe' else None;self.after(0,self.refresh);self.after(0,lambda:self.status.set('MPV instalado correctamente.'))
  except Exception as e:self.after(0,lambda m=str(e):messagebox.showerror(APP,f'Error instalando MPV:\n{m}'))
 def install_openvpn(self):
  if not shutil.which('winget'):messagebox.showerror(APP,'Winget no está disponible.');return
  threading.Thread(target=lambda:(run(['winget','install','-e','--id','OpenVPNTechnologies.OpenVPN','--accept-package-agreements','--accept-source-agreements'],600),self.after(0,self.refresh)),daemon=True).start()
 def servers(self):
  raw=urllib.request.urlopen(urllib.request.Request(VPNGATE_CSV,headers={'User-Agent':APP}),timeout=20).read().decode('utf-8-sig',errors='replace');rows=list(csv.DictReader(io.StringIO('\n'.join(x for x in raw.splitlines() if x and not x.startswith(('*','#'))))));allow=REGIONS[self.region.get()];out=[]
  for r in rows:
   if r.get('OpenVPN_ConfigData_Base64') and (not allow or r.get('CountryShort') in allow):
    try:r['_s']=int(r.get('Score') or 0);base64.b64decode(r['OpenVPN_ConfigData_Base64'],validate=True);out.append(r)
    except:pass
  return sorted(out,key=lambda x:x['_s'],reverse=True)
 def connect_vpn(self):
  if not self.openvpn():messagebox.showerror(APP,'Falta OpenVPN.');return
  self.disconnect_vpn();self.vpns.set('VPN: buscando servidor...');threading.Thread(target=self._vpn,daemon=True).start()
 def _vpn(self):
  try:
   for s in self.servers()[:5]:
    VPNCFG.write_bytes(base64.b64decode(s['OpenVPN_ConfigData_Base64']));VPNLOG.write_text('',encoding='utf8');self.vpnproc=subprocess.Popen([str(self.openvpn()),'--config',str(VPNCFG),'--auth-nocache','--connect-retry-max','1','--connect-timeout','12','--log',str(VPNLOG)],creationflags=0x08000000)
    for _ in range(25):
     time.sleep(1);log=VPNLOG.read_text(encoding='utf8',errors='ignore')
     if 'Initialization Sequence Completed' in log:self.after(0,lambda n=s.get('CountryLong'):self.vpns.set(f'VPN: conectada · {n}'));return
     if self.vpnproc.poll() is not None:break
    self.disconnect_vpn()
   raise RuntimeError('No se pudo conectar con los servidores disponibles.')
  except Exception as e:self.after(0,lambda m=str(e):messagebox.showerror(APP,f'Error VPN:\n{m}'))
 def disconnect_vpn(self):
  if self.vpnproc and self.vpnproc.poll() is None:self.vpnproc.terminate()
  self.vpnproc=None;self.vpns.set('VPN: desconectada')
 def cid(self):
  s=re.sub(r'^acestream://','',self.ace.get().strip(),flags=re.I);m=re.search(r'[?&](?:id|content_id)=([0-9a-fA-F]{40})',s);s=m.group(1) if m else s
  if not re.fullmatch(r'[0-9a-fA-F]{40}',s):raise ValueError('El ACE debe contener un Content ID hexadecimal de 40 caracteres.')
  return s.lower()
 def play(self):
  try:c=self.cid();cache=max(60,int(self.cache.get()))
  except Exception as e:messagebox.showerror(APP,str(e));return
  if not self.mpv():messagebox.showerror(APP,'Falta MPV. Pulsa Instalar MPV.');return
  self.status.set('Preparando AceStream Engine...');self.update_idletasks()
  if not self.start_engine(True):messagebox.showerror(APP,'No se pudo arrancar AceStream Engine automáticamente.');return
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
