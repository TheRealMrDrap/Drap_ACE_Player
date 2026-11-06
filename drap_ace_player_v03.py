import base64, csv, io, json, os, re, shutil, subprocess, sys, threading, time, tkinter as tk, urllib.request, zipfile
from pathlib import Path
from tkinter import ttk, messagebox

APP='DRAP ACE PLAYER'; VERSION='0.3'
HOST='127.0.0.1'; PORT=6878
CFGDIR=Path(os.getenv('APPDATA',Path.home()))/'DRAP Ace Player'; CFG=CFGDIR/'config.json'; VPNCFG=CFGDIR/'vpngate.ovpn'; VPNLOG=CFGDIR/'openvpn.log'
VPNGATE_CSV='https://www.vpngate.net/api/iphone/'
MPV_URL='https://github.com/shinchiro/mpv-winbuild-cmake/releases/latest/download/mpv-x86_64-gcc.zip'
REGIONS={
 'Automático (mejor disponible)':None,
 'Europa':{'AD','AL','AT','BA','BE','BG','BY','CH','CY','CZ','DE','DK','EE','ES','FI','FR','GB','GR','HR','HU','IE','IS','IT','LI','LT','LU','LV','MC','MD','ME','MK','MT','NL','NO','PL','PT','RO','RS','RU','SE','SI','SK','SM','UA'},
 'Asia':{'AE','AF','AM','AZ','BD','BH','BN','BT','CN','GE','HK','ID','IL','IN','IQ','IR','JO','JP','KG','KH','KR','KW','KZ','LA','LB','LK','MM','MN','MO','MV','MY','NP','OM','PH','PK','PS','QA','SA','SG','SY','TH','TJ','TL','TM','TR','TW','UZ','VN','YE'},
 'África':{'AO','BF','BI','BJ','BW','CD','CF','CG','CI','CM','CV','DJ','DZ','EG','ER','ET','GA','GH','GM','GN','GQ','GW','KE','KM','LR','LS','LY','MA','MG','ML','MR','MU','MW','MZ','NA','NE','NG','RW','SC','SD','SL','SN','SO','SS','ST','SZ','TD','TG','TN','TZ','UG','ZA','ZM','ZW'},
 'Sudamérica':{'AR','BO','BR','CL','CO','EC','FK','GF','GY','PE','PY','SR','UY','VE'},
 'Norteamérica':{'AG','AI','AW','BB','BL','BM','BQ','BS','BZ','CA','CR','CU','CW','DM','DO','GD','GL','GP','GT','HN','HT','JM','KN','KY','LC','MF','MQ','MS','MX','NI','PA','PM','PR','SV','TC','TT','US','VC','VG','VI'} }

def adir(): return Path(sys.executable).resolve().parent if getattr(sys,'frozen',False) else Path(__file__).resolve().parent

def hidden():
 s=subprocess.STARTUPINFO(); s.dwFlags|=subprocess.STARTF_USESHOWWINDOW; return s

def run(a,t=60): return subprocess.run(a,capture_output=True,text=True,timeout=t,startupinfo=hidden(),creationflags=0x08000000)

class App(tk.Tk):
 def __init__(self):
  super().__init__(); self.title(f'{APP} v{VERSION}'); self.geometry('780x545'); self.minsize(720,510); self.player=None; self.vpnproc=None; CFGDIR.mkdir(parents=True,exist_ok=True)
  try:self.cfg=json.loads(CFG.read_text(encoding='utf8'))
  except:self.cfg={}
  self.ace=tk.StringVar(value=self.cfg.get('ace','')); self.cache=tk.IntVar(value=max(60,int(self.cfg.get('cache',60)))); self.fs=tk.BooleanVar(value=self.cfg.get('fs',False)); self.region=tk.StringVar(value=self.cfg.get('region','Europa')); self.status=tk.StringVar(value='Preparado'); self.engine_s=tk.StringVar(value='AceStream: comprobando...'); self.mpv_s=tk.StringVar(value='MPV: comprobando...'); self.vpn_s=tk.StringVar(value='VPN: desconectada')
  self.ui(); self.after(300,self.refresh); self.protocol('WM_DELETE_WINDOW',self.close)
 def ui(self):
  f=ttk.Frame(self,padding=18);f.pack(fill='both',expand=True);ttk.Label(f,text=f'{APP}  v{VERSION}',font=('Segoe UI',20,'bold')).pack(anchor='w');ttk.Label(f,text='AceStream + MPV + VPN pública opcional por región').pack(anchor='w',pady=(0,12))
  x=ttk.LabelFrame(f,text='Reproducción',padding=11);x.pack(fill='x');ttk.Entry(x,textvariable=self.ace,font=('Consolas',10)).pack(fill='x',pady=(0,8));r=ttk.Frame(x);r.pack(fill='x');ttk.Label(r,text='Caché:').pack(side='left');ttk.Spinbox(r,from_=60,to=900,increment=30,textvariable=self.cache,width=7).pack(side='left',padx=5);ttk.Label(r,text='segundos').pack(side='left');ttk.Checkbutton(r,text='Pantalla completa',variable=self.fs).pack(side='right')
  x=ttk.LabelFrame(f,text='Componentes',padding=10);x.pack(fill='x',pady=(10,0));ttk.Label(x,textvariable=self.mpv_s).pack(side='left',fill='x',expand=True);ttk.Button(x,text='Instalar MPV',command=self.install_mpv).pack(side='right');ttk.Button(x,text='Instalar OpenVPN',command=self.install_openvpn).pack(side='right',padx=6)
  x=ttk.LabelFrame(f,text='VPN pública VPN Gate (opcional)',padding=10);x.pack(fill='x',pady=10);r=ttk.Frame(x);r.pack(fill='x');ttk.Label(r,text='Región:').pack(side='left');ttk.Combobox(r,textvariable=self.region,values=list(REGIONS),state='readonly',width=31).pack(side='left',padx=6);ttk.Button(r,text='CONECTAR',command=self.connect_vpn).pack(side='left');ttk.Button(r,text='DESCONECTAR',command=self.disconnect_vpn).pack(side='left',padx=6);ttk.Label(x,textvariable=self.vpn_s).pack(anchor='w',pady=(7,0));ttk.Label(x,text='Aviso: servidores voluntarios; pueden registrar tráfico y no garantizan privacidad ni disponibilidad.',foreground='#9a5500').pack(anchor='w',pady=(4,0))
  ttk.Label(f,textvariable=self.engine_s).pack(anchor='w');ttk.Label(f,textvariable=self.status).pack(anchor='w',pady=(4,11));r=ttk.Frame(f);r.pack(fill='x');ttk.Button(r,text='REPRODUCIR',command=self.play).pack(side='left',fill='x',expand=True,ipady=8);ttk.Button(r,text='DETENER',command=self.stop_player).pack(side='left',padx=(8,0),ipady=8)
 def mpv(self):
  for p in [adir()/'mpv.exe',adir()/'mpv'/'mpv.exe']:
   if p.exists():return p
  w=shutil.which('mpv'); return Path(w) if w else None
 def openvpn(self):
  for p in [Path(os.getenv('ProgramFiles','C:/Program Files'))/'OpenVPN'/'bin'/'openvpn.exe',Path(os.getenv('ProgramFiles','C:/Program Files'))/'OpenVPN Connect'/'OpenVPNConnect.exe']:
   if p.exists() and p.name.lower()=='openvpn.exe':return p
  w=shutil.which('openvpn');return Path(w) if w else None
 def refresh(self):
  self.mpv_s.set(('MPV: instalado' if self.mpv() else 'MPV: falta')+' | '+('OpenVPN: instalado' if self.openvpn() else 'OpenVPN: falta'));self.check_engine()
 def install_mpv(self):self.status.set('Descargando MPV...');threading.Thread(target=self._mpv,daemon=True).start()
 def _mpv(self):
  try:
   d=adir()/'mpv';d.mkdir(exist_ok=True);z=adir()/'mpv.zip';urllib.request.urlretrieve(MPV_URL,z)
   with zipfile.ZipFile(z) as q:q.extractall(d)
   z.unlink(missing_ok=True);p=next(d.rglob('mpv.exe'));shutil.copy2(p,d/'mpv.exe') if p!=d/'mpv.exe' else None;self.after(0,self.refresh);self.after(0,lambda:self.status.set('MPV instalado'))
  except Exception as e:self.after(0,lambda:messagebox.showerror(APP,f'Error instalando MPV:\n{e}'))
 def install_openvpn(self):
  if not shutil.which('winget'):messagebox.showerror(APP,'Winget no está disponible. Instala OpenVPN Community manualmente.');return
  self.status.set('Abriendo el instalador de OpenVPN...');threading.Thread(target=self._ovpn_install,daemon=True).start()
 def _ovpn_install(self):
  x=run(['winget','install','-e','--id','OpenVPNTechnologies.OpenVPN','--accept-package-agreements','--accept-source-agreements'],600)
  self.after(0,self.refresh);self.after(0,lambda:self.status.set('OpenVPN instalado' if x.returncode==0 else 'La instalación de OpenVPN no terminó correctamente'))
 def check_engine(self):
  try:
   urllib.request.urlopen(f'http://{HOST}:{PORT}/webui/api/service?method=get_version',timeout=3).read();self.engine_s.set('AceStream Engine: conectado');return True
  except:self.engine_s.set('AceStream Engine: no responde en 127.0.0.1:6878');return False
 def servers(self):
  req=urllib.request.Request(VPNGATE_CSV,headers={'User-Agent':APP});raw=urllib.request.urlopen(req,timeout=20).read().decode('utf-8-sig',errors='replace');lines=[x for x in raw.splitlines() if x and not x.startswith('*') and not x.startswith('#')];rows=list(csv.DictReader(io.StringIO('\n'.join(lines))));allowed=REGIONS[self.region.get()];out=[]
  for r in rows:
   if not r.get('OpenVPN_ConfigData_Base64'):continue
   if allowed and r.get('CountryShort','').upper() not in allowed:continue
   try:r['_score']=int(r.get('Score') or 0);r['_speed']=int(r.get('Speed') or 0);base64.b64decode(r['OpenVPN_ConfigData_Base64'],validate=True)
   except:continue
   out.append(r)
  return sorted(out,key=lambda z:(z['_score'],z['_speed']),reverse=True)
 def connect_vpn(self):
  if not self.openvpn():messagebox.showerror(APP,'Falta OpenVPN Community. Pulsa «Instalar OpenVPN».');return
  self.disconnect_vpn();self.vpn_s.set('VPN: buscando servidor...');threading.Thread(target=self._connect,daemon=True).start()
 def _connect(self):
  try:
   ss=self.servers()
   if not ss:raise RuntimeError('No hay servidores OpenVPN disponibles en la región seleccionada.')
   last=''
   for s in ss[:5]:
    VPNCFG.write_bytes(base64.b64decode(s['OpenVPN_ConfigData_Base64']));VPNLOG.write_text('',encoding='utf8');cmd=[str(self.openvpn()),'--config',str(VPNCFG),'--auth-nocache','--connect-retry-max','1','--connect-timeout','12','--log',str(VPNLOG)]
    self.vpnproc=subprocess.Popen(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=0x08000000)
    for _ in range(25):
     time.sleep(1);last=VPNLOG.read_text(encoding='utf8',errors='ignore') if VPNLOG.exists() else ''
     if 'Initialization Sequence Completed' in last:
      name=s.get('CountryLong') or s.get('CountryShort');ip=s.get('IP','');self.after(0,lambda n=name,i=ip:self.vpn_s.set(f'VPN: conectada - {n} ({i})'));self.after(0,lambda:self.status.set('VPN lista'));return
     if self.vpnproc.poll() is not None:break
    self.disconnect_vpn()
   raise RuntimeError('No fue posible conectar con los primeros servidores disponibles.')
  except Exception as e:self.after(0,lambda:messagebox.showerror(APP,f'Error de VPN:\n{e}'));self.after(0,lambda:self.vpn_s.set('VPN: desconectada'))
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
  self.stop_player();a=[str(self.mpv()),f'http://{HOST}:{PORT}/ace/getstream?id={c}','--force-window=yes','--cache=yes',f'--cache-secs={cache}','--demuxer-max-bytes=256MiB','--demuxer-readahead-secs=120','--title=DRAP ACE PLAYER'];a+=['--fullscreen'] if self.fs.get() else [];self.player=subprocess.Popen(a,cwd=str(adir()));self.status.set(f'Reproduciendo - caché {cache} s');self.save()
 def stop_player(self):
  if self.player and self.player.poll() is None:self.player.terminate()
  self.player=None
 def save(self):
  CFG.write_text(json.dumps({'ace':self.ace.get(),'cache':max(60,int(self.cache.get())),'fs':self.fs.get(),'region':self.region.get()},ensure_ascii=False,indent=2),encoding='utf8')
 def close(self):
  try:self.save()
  except:pass
  self.stop_player();self.disconnect_vpn();self.destroy()
if __name__=='__main__':App().mainloop()
