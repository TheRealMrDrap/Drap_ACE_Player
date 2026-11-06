import base64, csv, io, json, os, re, shutil, subprocess, sys, threading, time, urllib.request
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

APP='DRAP ACE PLAYER'; VERSION='0.4.0'; HOST='127.0.0.1'; PORT=6878
CFGDIR=Path(os.getenv('APPDATA',Path.home()))/'DRAP Ace Player'; CFG=CFGDIR/'config.json'; VPNCFG=CFGDIR/'vpngate.ovpn'; VPNLOG=CFGDIR/'openvpn.log'
VPNGATE_CSV='https://www.vpngate.net/api/iphone/'
MPV_RELEASE_API='https://api.github.com/repos/zhongfly/mpv-winbuild/releases/latest'
REGIONS={
 'Automático (mejor disponible)':None,
 'Europa':{'AD','AL','AT','BA','BE','BG','BY','CH','CY','CZ','DE','DK','EE','ES','FI','FR','GB','GR','HR','HU','IE','IS','IT','LI','LT','LU','LV','MC','MD','ME','MK','MT','NL','NO','PL','PT','RO','RS','RU','SE','SI','SK','SM','UA'},
 'Asia':{'AE','AF','AM','AZ','BD','BH','BN','BT','CN','GE','HK','ID','IL','IN','IQ','IR','JO','JP','KG','KH','KR','KW','KZ','LA','LB','LK','MM','MN','MO','MV','MY','NP','OM','PH','PK','PS','QA','SA','SG','SY','TH','TJ','TL','TM','TR','TW','UZ','VN','YE'},
 'África':{'AO','BF','BI','BJ','BW','CD','CF','CG','CI','CM','CV','DJ','DZ','EG','ER','ET','GA','GH','GM','GN','GQ','GW','KE','KM','LR','LS','LY','MA','MG','ML','MR','MU','MW','MZ','NA','NE','NG','RW','SC','SD','SL','SN','SO','SS','ST','SZ','TD','TG','TN','TZ','UG','ZA','ZM','ZW'},
 'Sudamérica':{'AR','BO','BR','CL','CO','EC','FK','GF','GY','PE','PY','SR','UY','VE'},
 'Norteamérica':{'AG','AI','AW','BB','BL','BM','BQ','BS','BZ','CA','CR','CU','CW','DM','DO','GD','GL','GP','GT','HN','HT','JM','KN','KY','LC','MF','MQ','MS','MX','NI','PA','PM','PR','SV','TC','TT','US','VC','VG','VI'} }

def adir(): return Path(sys.executable).resolve().parent if getattr(sys,'frozen',False) else Path(__file__).resolve().parent
def resource(name): return Path(getattr(sys,'_MEIPASS',Path(__file__).resolve().parent))/name
def hidden():
 s=subprocess.STARTUPINFO(); s.dwFlags|=subprocess.STARTF_USESHOWWINDOW; return s
def run(a,t=60): return subprocess.run(a,capture_output=True,text=True,timeout=t,startupinfo=hidden(),creationflags=0x08000000)

ctk.set_appearance_mode('dark'); ctk.set_default_color_theme('blue')
BG='#0b1018'; PANEL='#121a26'; PANEL2='#172231'; BLUE='#1689ff'; BLUE_H='#0871dc'; GREEN='#29c77d'; RED='#ff5d68'; TEXT='#f4f7fb'; MUTED='#98a7ba'; BORDER='#26364a'; ORANGE='#e9a23b'

class App(ctk.CTk):
 def __init__(self):
  super().__init__(); CFGDIR.mkdir(parents=True,exist_ok=True); self.player=None; self.vpnproc=None
  self.title(f'{APP} v{VERSION}'); self.geometry('850x650'); self.minsize(790,610); self.configure(fg_color=BG)
  try:
   self.iconbitmap(str(resource('MrDrap_Player.ico')))
   self._iconimg=tk.PhotoImage(file=str(resource('MrDrap_Player_64.png'))); self.iconphoto(True,self._iconimg)
  except: pass
  try:self.cfg=json.loads(CFG.read_text(encoding='utf8'))
  except:self.cfg={}
  self.ace=tk.StringVar(value=self.cfg.get('ace','')); self.cache=tk.StringVar(value=str(max(60,int(self.cfg.get('cache',60))))); self.fs=tk.BooleanVar(value=self.cfg.get('fs',False)); self.region=tk.StringVar(value=self.cfg.get('region','Europa'))
  self.status=tk.StringVar(value='Preparado'); self.engine_s=tk.StringVar(value='AceStream: comprobando...'); self.comp_s=tk.StringVar(value='Comprobando componentes...'); self.vpn_s=tk.StringVar(value='VPN: desconectada')
  self.ui(); self.after(350,self.refresh); self.protocol('WM_DELETE_WINDOW',self.close)
 def card(self,parent): return ctk.CTkFrame(parent,fg_color=PANEL,corner_radius=18,border_width=1,border_color=BORDER)
 def titlelabel(self,p,t): return ctk.CTkLabel(p,text=t,font=ctk.CTkFont('Segoe UI',15,'bold'),text_color=TEXT)
 def btn(self,p,text,cmd,color=BLUE,width=150): return ctk.CTkButton(p,text=text,command=cmd,width=width,height=38,corner_radius=12,fg_color=color,hover_color=BLUE_H if color==BLUE else '#213247',border_width=0,font=ctk.CTkFont('Segoe UI',13,'bold'))
 def ui(self):
  root=ctk.CTkScrollableFrame(self,fg_color='transparent',corner_radius=0); root.pack(fill='both',expand=True,padx=24,pady=20)
  head=ctk.CTkFrame(root,fg_color='transparent');head.pack(fill='x',pady=(0,14))
  try:
   from PIL import Image
   logo=ctk.CTkImage(Image.open(resource('MrDrap_Player_128.png')),size=(68,68)); self.logo=logo; ctk.CTkLabel(head,text='',image=logo).pack(side='left',padx=(0,14))
  except:pass
  htxt=ctk.CTkFrame(head,fg_color='transparent');htxt.pack(side='left',fill='x',expand=True);ctk.CTkLabel(htxt,text=APP,font=ctk.CTkFont('Segoe UI',25,'bold'),text_color=TEXT).pack(anchor='w');ctk.CTkLabel(htxt,text=f'v{VERSION}  •  AceStream + MPV + VPN opcional',font=ctk.CTkFont('Segoe UI',13),text_color=MUTED).pack(anchor='w')
  x=self.card(root);x.pack(fill='x',pady=7,padx=2);self.titlelabel(x,'Reproducción').pack(anchor='w',padx=18,pady=(15,8));ctk.CTkEntry(x,textvariable=self.ace,height=43,corner_radius=12,fg_color=PANEL2,border_color=BORDER,placeholder_text='acestream://ID o Content ID de 40 caracteres',font=ctk.CTkFont('Consolas',12)).pack(fill='x',padx=18)
  r=ctk.CTkFrame(x,fg_color='transparent');r.pack(fill='x',padx=18,pady=(12,15));ctk.CTkLabel(r,text='Caché',text_color=MUTED).pack(side='left');ctk.CTkEntry(r,textvariable=self.cache,width=76,height=36,corner_radius=10,fg_color=PANEL2,border_color=BORDER).pack(side='left',padx=(8,5));ctk.CTkLabel(r,text='segundos (mín. 60)',text_color=MUTED).pack(side='left');ctk.CTkCheckBox(r,text='Pantalla completa',variable=self.fs,corner_radius=6,fg_color=BLUE,hover_color=BLUE_H).pack(side='right')
  x=self.card(root);x.pack(fill='x',pady=7,padx=2);self.titlelabel(x,'Componentes').pack(anchor='w',padx=18,pady=(15,4));ctk.CTkLabel(x,textvariable=self.comp_s,text_color=MUTED).pack(anchor='w',padx=18,pady=(0,10));r=ctk.CTkFrame(x,fg_color='transparent');r.pack(fill='x',padx=18,pady=(0,15));self.btn(r,'Instalar MPV',self.install_mpv).pack(side='left');self.btn(r,'Instalar OpenVPN',self.install_openvpn,color='#1d2b3d',width=170).pack(side='left',padx=10)
  x=self.card(root);x.pack(fill='x',pady=7,padx=2);self.titlelabel(x,'VPN pública VPN Gate  ·  opcional').pack(anchor='w',padx=18,pady=(15,9));r=ctk.CTkFrame(x,fg_color='transparent');r.pack(fill='x',padx=18);ctk.CTkLabel(r,text='Región',text_color=MUTED).pack(side='left');ctk.CTkOptionMenu(r,variable=self.region,values=list(REGIONS),width=270,height=38,corner_radius=12,fg_color=PANEL2,button_color='#253b55',button_hover_color='#315172').pack(side='left',padx=8);self.btn(r,'CONECTAR',self.connect_vpn,color=GREEN,width=125).pack(side='left',padx=(6,8));self.btn(r,'DESCONECTAR',self.disconnect_vpn,color='#1d2b3d',width=140).pack(side='left');ctk.CTkLabel(x,textvariable=self.vpn_s,text_color=TEXT).pack(anchor='w',padx=18,pady=(10,2));ctk.CTkLabel(x,text='Servidores voluntarios: no uses esta VPN para credenciales o información sensible.',text_color=ORANGE,font=ctk.CTkFont('Segoe UI',11)).pack(anchor='w',padx=18,pady=(0,15))
  st=ctk.CTkFrame(root,fg_color='transparent');st.pack(fill='x',padx=4,pady=(10,9));ctk.CTkLabel(st,textvariable=self.engine_s,text_color=MUTED).pack(anchor='w');ctk.CTkLabel(st,textvariable=self.status,text_color=TEXT).pack(anchor='w')
  r=ctk.CTkFrame(root,fg_color='transparent');r.pack(fill='x',pady=(4,14));ctk.CTkButton(r,text='▶  REPRODUCIR',command=self.play,height=50,corner_radius=15,fg_color=BLUE,hover_color=BLUE_H,font=ctk.CTkFont('Segoe UI',15,'bold')).pack(side='left',fill='x',expand=True);ctk.CTkButton(r,text='■  DETENER',command=self.stop_player,width=160,height=50,corner_radius=15,fg_color='#1d2b3d',hover_color='#293d55',font=ctk.CTkFont('Segoe UI',14,'bold')).pack(side='left',padx=(10,0))
 def mpv(self):
  for p in [adir()/'mpv.exe',adir()/'mpv'/'mpv.exe']:
   if p.exists(): return p
  w=shutil.which('mpv'); return Path(w) if w else None
 def openvpn(self):
  p=Path(os.getenv('ProgramFiles','C:/Program Files'))/'OpenVPN'/'bin'/'openvpn.exe'
  if p.exists():return p
  w=shutil.which('openvpn');return Path(w) if w else None
 def refresh(self): self.comp_s.set(('MPV: instalado' if self.mpv() else 'MPV: falta')+'    •    '+('OpenVPN: instalado' if self.openvpn() else 'OpenVPN: falta')); self.check_engine()
 def install_mpv(self): self.status.set('Consultando última versión de MPV...');threading.Thread(target=self._mpv,daemon=True).start()
 def _mpv(self):
  try:
   req=urllib.request.Request(MPV_RELEASE_API,headers={'User-Agent':APP,'Accept':'application/vnd.github+json'});data=json.loads(urllib.request.urlopen(req,timeout=20).read().decode());assets=data.get('assets',[]);choices=[a for a in assets if re.fullmatch(r'mpv-x86_64-[^/]+\.7z',a.get('name',''))]
   if not choices:raise RuntimeError('No se encontró un paquete MPV x86_64 compatible.')
   a=choices[0];d=adir()/'mpv';d.mkdir(exist_ok=True);archive=adir()/a['name'];self.after(0,lambda:self.status.set('Descargando MPV...'));urllib.request.urlretrieve(a['browser_download_url'],archive);tar=shutil.which('tar');seven=shutil.which('7z') or shutil.which('7z.exe')
   if tar:x=run([tar,'-xf',str(archive),'-C',str(d)],180)
   elif seven:x=run([seven,'x','-y',f'-o{d}',str(archive)],180)
   else:raise RuntimeError('No encuentro tar.exe ni 7z.exe para extraer MPV.')
   archive.unlink(missing_ok=True);found=list(d.rglob('mpv.exe'))
   if x.returncode or not found:raise RuntimeError('No se pudo extraer mpv.exe. '+(x.stderr or x.stdout)[-400:])
   if found[0]!=d/'mpv.exe':shutil.copy2(found[0],d/'mpv.exe')
   self.after(0,self.refresh);self.after(0,lambda:self.status.set('MPV instalado correctamente'))
  except Exception as e:self.after(0,lambda m=str(e) or repr(e):messagebox.showerror(APP,f'Error instalando MPV:\n{m}'))
 def install_openvpn(self):
  if not shutil.which('winget'):messagebox.showerror(APP,'Winget no está disponible.');return
  self.status.set('Instalando OpenVPN...');threading.Thread(target=self._ovpn,daemon=True).start()
 def _ovpn(self):
  x=run(['winget','install','-e','--id','OpenVPNTechnologies.OpenVPN','--accept-package-agreements','--accept-source-agreements'],600);self.after(0,self.refresh);self.after(0,lambda:self.status.set('OpenVPN instalado' if x.returncode==0 else 'OpenVPN no terminó correctamente'))
 def check_engine(self):
  try:urllib.request.urlopen(f'http://{HOST}:{PORT}/webui/api/service?method=get_version',timeout=3).read();self.engine_s.set('●  AceStream Engine conectado');return True
  except:self.engine_s.set('○  AceStream Engine no responde en 127.0.0.1:6878');return False
 def servers(self):
  raw=urllib.request.urlopen(urllib.request.Request(VPNGATE_CSV,headers={'User-Agent':APP}),timeout=20).read().decode('utf-8-sig',errors='replace');lines=[x for x in raw.splitlines() if x and not x.startswith('*') and not x.startswith('#')];rows=list(csv.DictReader(io.StringIO('\n'.join(lines))));allowed=REGIONS[self.region.get()];out=[]
  for r in rows:
   if not r.get('OpenVPN_ConfigData_Base64') or (allowed and r.get('CountryShort','').upper() not in allowed):continue
   try:r['_score']=int(r.get('Score') or 0);r['_speed']=int(r.get('Speed') or 0);base64.b64decode(r['OpenVPN_ConfigData_Base64'],validate=True);out.append(r)
   except:pass
  return sorted(out,key=lambda z:(z['_score'],z['_speed']),reverse=True)
 def connect_vpn(self):
  if not self.openvpn():messagebox.showerror(APP,'Falta OpenVPN. Pulsa «Instalar OpenVPN».');return
  self.disconnect_vpn();self.vpn_s.set('VPN: buscando servidor...');threading.Thread(target=self._connect,daemon=True).start()
 def _connect(self):
  try:
   ss=self.servers()
   if not ss:raise RuntimeError('No hay servidores OpenVPN disponibles en la región seleccionada.')
   for s in ss[:5]:
    VPNCFG.write_bytes(base64.b64decode(s['OpenVPN_ConfigData_Base64']));VPNLOG.write_text('',encoding='utf8');self.vpnproc=subprocess.Popen([str(self.openvpn()),'--config',str(VPNCFG),'--auth-nocache','--connect-retry-max','1','--connect-timeout','12','--log',str(VPNLOG)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=0x08000000)
    for _ in range(25):
     time.sleep(1);log=VPNLOG.read_text(encoding='utf8',errors='ignore') if VPNLOG.exists() else ''
     if 'Initialization Sequence Completed' in log:
      name=s.get('CountryLong') or s.get('CountryShort');ip=s.get('IP','');self.after(0,lambda:self.vpn_s.set(f'VPN: conectada · {name} · {ip}'));self.after(0,lambda:self.status.set('VPN lista'));return
     if self.vpnproc.poll() is not None:break
    self.disconnect_vpn()
   raise RuntimeError('No fue posible conectar con los primeros servidores disponibles.')
  except Exception as e:self.after(0,lambda m=str(e):messagebox.showerror(APP,f'Error de VPN:\n{m}'));self.after(0,lambda:self.vpn_s.set('VPN: desconectada'))
 def disconnect_vpn(self):
  if self.vpnproc and self.vpnproc.poll() is None:
   self.vpnproc.terminate()
   try:self.vpnproc.wait(5)
   except:self.vpnproc.kill()
  self.vpnproc=None;self.vpn_s.set('VPN: desconectada')
 def cid(self):
  s=re.sub(r'^acestream://','',self.ace.get().strip(),flags=re.I);m=re.search(r'[?&](?:id|content_id)=([0-9a-fA-F]{40})',s);s=m.group(1) if m else s
  if not re.fullmatch(r'[0-9a-fA-F]{40}',s):raise ValueError('El ACE debe contener un Content ID hexadecimal de 40 caracteres.')
  return s.lower()
 def play(self):
  try:c=self.cid();cache=max(60,int(self.cache.get()))
  except Exception as e:messagebox.showerror(APP,str(e));return
  if not self.mpv():messagebox.showerror(APP,'Falta MPV. Pulsa «Instalar MPV».');return
  if not self.check_engine():messagebox.showerror(APP,'Arranca AceStream Engine.');return
  self.stop_player();a=[str(self.mpv()),f'http://{HOST}:{PORT}/ace/getstream?id={c}','--force-window=yes','--cache=yes',f'--cache-secs={cache}','--demuxer-max-bytes=256MiB','--demuxer-readahead-secs=120','--title=DRAP ACE PLAYER'];a+=['--fullscreen'] if self.fs.get() else [];self.player=subprocess.Popen(a,cwd=str(adir()));self.status.set(f'Reproduciendo · caché {cache} s');self.save()
 def stop_player(self):
  if self.player and self.player.poll() is None:self.player.terminate()
  self.player=None
 def save(self): CFG.write_text(json.dumps({'ace':self.ace.get(),'cache':max(60,int(self.cache.get())),'fs':self.fs.get(),'region':self.region.get()},ensure_ascii=False,indent=2),encoding='utf8')
 def close(self):
  try:self.save()
  except:pass
  self.stop_player();self.disconnect_vpn();self.destroy()
if __name__=='__main__':App().mainloop()
