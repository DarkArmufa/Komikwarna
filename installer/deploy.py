#!/usr/bin/env python3
"""Restricted Pterodactyl deployment recipes. Ubuntu 24.04 / systemd only.
Commands use argv (never shell=True). Secrets travel over stdin or private files.
"""
import contextlib
import hashlib
import ipaddress
import json
import os
from pathlib import Path
import platform
import re
import selectors
import shutil
import signal
import socket
import subprocess
import tarfile
import tempfile
import time
import urllib.request
import uuid
from license_gate import require_license, LICENSE_MODES

BASE = Path(__file__).resolve().parent.parent
PANEL = Path('/var/www/pterodactyl')
STATE = Path('/var/lib/comic-ptero-installer')
BACKUPS = STATE / 'backups'
MANAGED = STATE / 'installed.json'
PANEL_VERSION = 'v1.15.1'
WINGS_VERSION = 'v1.13.3'
PANEL_HASH = '62c88c035b3e0f3c3ddd06bc3ef12249d087af0e765f49878b6327a066ed860b'
WINGS_HASH = {'amd64':'010d894a895fe4f914e3f1c1e75fb2fda4ebe50cc249e7e456887ea5b422c8fa', 'arm64':'8e3114cb0ee5ec617831d5ec35097b1096c6c972f05ef80c683a9f396d0fe9f5'}
MODES = {'both','panel','wings','update','repair','backup','restore'}
DOMAIN = re.compile(r'(?=.{4,253}\Z)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}\Z')


def private_write(path, data, mode=0o600):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as f:
            os.fchmod(f.fileno(), mode)
            f.write(data)
        os.replace(temp, path)
    finally:
        if os.path.exists(temp): os.unlink(temp)


def validate(mode, raw):
    if mode not in MODES or not isinstance(raw, dict):
        raise ValueError('Pilihan operasi tidak valid.')
    keys = {'license_key','domain','email','username','password','db_password','location','wings_config','backup','brand','acme_agree'}
    c = {k: str(v) for k,v in raw.items() if k in keys and k != 'acme_agree'}
    c['acme_agree'] = raw.get('acme_agree') is True
    if mode in LICENSE_MODES:
        c['license_key'] = require_license(raw.get('license_key'))
    for k,v in c.items():
        if isinstance(v,str) and (len(v)>32768 or '\x00' in v): raise ValueError('Input terlalu panjang atau tidak valid.')
    if mode in {'panel','both'}:
        c['domain'] = c.get('domain','').strip().lower()
        if not DOMAIN.fullmatch(c['domain']): raise ValueError('Domain harus hostname lengkap tanpa URL/path.')
        if not re.fullmatch(r'[A-Za-z0-9_.-]{3,32}',c.get('username','')): raise ValueError('Username tidak valid.')
        if not re.fullmatch(r'[A-Za-z0-9.!#$%&*+/=?^_`{|}~-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,63}',c.get('email','')): raise ValueError('Email tidak valid.')
        for name,minimum in [('password',16),('db_password',20)]:
            p = c.get(name,'')
            if not minimum <= len(p) <= 128 or not re.fullmatch(r'[A-Za-z0-9!@#%^*_+=.,:?-]+',p):
                raise ValueError(f'{name}: {minimum}–128 karakter, huruf/angka atau !@#%^*_+=.,:?-')
            if not all(re.search(pat,p) for pat in ['[a-z]','[A-Z]','[0-9]']): raise ValueError('Password perlu huruf besar, kecil dan angka.')
        if c['password']==c['db_password']: raise ValueError('Password admin dan database harus berbeda.')
        if not c['acme_agree']: raise ValueError('Persetujuan ketentuan sertifikat diperlukan.')
        if not re.fullmatch(r'[A-Za-z0-9_.-]{1,60}',c.get('location','Jakarta-01')): raise ValueError('Nama lokasi tidak valid.')
        if not re.fullmatch(r'[A-Za-z0-9 ._-]{1,40}',c.get('brand','BOLT HOST')): raise ValueError('Nama hosting: 1–40 huruf/angka/spasi.')
    if mode=='wings' and not 50 <= len(c.get('wings_config','')) <= 32768: raise ValueError('Konfigurasi Wings belum lengkap.')
    if mode=='restore' and not re.fullmatch(r'backup-[0-9T-]+-[a-f0-9]{8}\.tar\.gz',c.get('backup','')): raise ValueError('Nama backup tidak valid.')
    if mode=='wings':return {'license_key':c['license_key'],'wings_config':c['wings_config']}
    if mode=='restore':return {'backup':c['backup']}
    if mode in {'update','repair'}:return {'license_key':c['license_key']}
    if mode not in {'panel','both'}:return {}
    return c


def quick(argv):
    try:
        return subprocess.run(argv,capture_output=True,text=True,timeout=8,check=False).stdout.strip()
    except (OSError, subprocess.TimeoutExpired): return ''


def system_info():
    release={}
    if Path('/etc/os-release').exists():
        for line in Path('/etc/os-release').read_text().splitlines():
            if '=' in line:
                k,v=line.split('=',1);release[k]=v.strip('"')
    total_mem=0
    if Path('/proc/meminfo').exists():
        total_mem=int(re.search(r'MemTotal:\s+(\d+)',Path('/proc/meminfo').read_text()).group(1))*1024
    disk=shutil.disk_usage('/var' if Path('/var').exists() else '/').free
    ips=[]
    for value in quick(['hostname','-I']).split():
        with contextlib.suppress(ValueError):
            addr=ipaddress.ip_address(value)
            if addr.version==4 and not addr.is_loopback: ips.append(value)
    public=''
    try:
        with urllib.request.urlopen('https://api.ipify.org',timeout=4) as r: public=str(ipaddress.ip_address(r.read(64).decode().strip()))
    except Exception: pass
    errors=[]
    if release.get('ID')!='ubuntu' or release.get('VERSION_ID')!='24.04': errors.append('Installer nyata hanya mendukung Ubuntu 24.04 LTS.')
    if os.geteuid()!=0: errors.append('Launcher perlu dijalankan sebagai root/sudo.')
    if not Path('/run/systemd/system').exists(): errors.append('Systemd tidak tersedia; gunakan VPS/VM, bukan container biasa.')
    if platform.machine() not in {'x86_64','aarch64'}: errors.append('Arsitektur harus amd64 atau arm64.')
    if disk<5*1024**3: errors.append('Butuh minimal 5 GB ruang kosong.')
    if total_mem<1024**3: errors.append('Butuh minimal 1 GB RAM; 2 GB atau lebih disarankan.')
    return {'os':release.get('PRETTY_NAME',platform.system()),'arch':platform.machine(),'ip':public or (ips[0] if ips else 'Tidak terdeteksi'),'local_ips':ips,'disk':f'{disk/1024**3:.1f} GB','disk_bytes':disk,'memory':f'{total_mem/1024**3:.1f} GB','memory_bytes':total_mem,'root':os.geteuid()==0,'errors':errors,'backups':list_backups()}


def list_backups():
    if not BACKUPS.exists(): return []
    return [{'name':p.name,'size':p.stat().st_size} for p in sorted(BACKUPS.glob('backup-*.tar.gz'),reverse=True) if p.with_suffix(p.suffix+'.sha256').exists() and not p.is_symlink()]


def sha256(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()


def safe_extract(archive,destination):
    with tarfile.open(archive,'r:gz') as tf:
        members=tf.getmembers()
        if sum(m.size for m in members)>8*1024**3: raise ValueError('Archive terlalu besar untuk panel.')
        for m in members:
            if m.name.startswith('/') or '..' in Path(m.name).parts or m.isdev(): raise ValueError('Archive mengandung path tidak aman.')
        tf.extractall(destination,filter='data')


class Deployment:
    def __init__(self, mode, config, report):
        self.mode=mode; self.c=validate(mode,config); self.report=report
        self.secrets=[self.c.get(k,'') for k in ['license_key','password','db_password','wings_config']]
        self.meta={}; self.info={}; self.maintenance=False

    def log(self,text):
        text=re.sub(r'\x1b\[[0-9;]*[A-Za-z]','',str(text))
        for secret in self.secrets:
            if secret: text=text.replace(secret,'[REDACTED]')
        text=re.sub(r'(?i)(APP_KEY|DB_PASSWORD|token_id|token|password)([\s=:]+)\S+',r'\1\2[REDACTED]',text)
        self.report('log',text[:3000])

    def run(self,argv,*,cwd=None,input_text=None,quiet=False,timeout=1800):
        env=os.environ.copy();env.update(DEBIAN_FRONTEND='noninteractive',COMPOSER_ALLOW_SUPERUSER='1',LC_ALL='C.UTF-8')
        # Never emit full argv, stdin, or environment: they can contain credentials.
        with tempfile.TemporaryFile() as inp:
            if input_text is not None: inp.write(input_text.encode());inp.seek(0)
            p=subprocess.Popen([str(x) for x in argv],cwd=cwd,env=env,stdin=inp,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,start_new_session=True)
            deadline=time.monotonic()+timeout;parts=[];carry=''
            sel=selectors.DefaultSelector();sel.register(p.stdout,selectors.EVENT_READ)
            try:
                while sel.get_map():
                    if time.monotonic()>deadline: raise TimeoutError('Langkah melebihi batas waktu.')
                    for key,_ in sel.select(.25):
                        chunk=os.read(key.fd,65536)
                        if not chunk:
                            sel.unregister(key.fileobj);continue
                        txt=chunk.decode(errors='replace')
                        if quiet: parts.append(txt)
                        else:
                            carry+=txt
                            lines=carry.split('\n');carry=lines.pop()
                            for line in lines:
                                if line.strip(): self.log(line)
                p.wait(timeout=max(1,deadline-time.monotonic()))
                if carry and not quiet: self.log(carry)
                if p.returncode: raise RuntimeError(f'{Path(argv[0]).name} gagal (exit {p.returncode}). '+('Output dirahasiakan karena dapat memuat credential.' if quiet else 'Lihat log di atas.'))
                return ''.join(parts)
            finally:
                sel.close();p.stdout.close()
                if p.poll() is None:
                    os.killpg(p.pid,signal.SIGTERM)
                    try:p.wait(timeout=5)
                    except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()

    def php(self,action,data=None):
        return self.run(['php',BASE/'installer/bridge.php',action],cwd=PANEL,input_text=json.dumps(data or {}),quiet=True)

    def artisan(self,*args): return self.run(['php','artisan',*args,'--no-interaction'],cwd=PANEL)

    def check(self):
        self.info=system_info()
        if self.info['errors']: raise RuntimeError(' '.join(self.info['errors']))
        if self.mode in {'panel','both','wings'} and not quick(['/usr/sbin/sshd','-T']): raise RuntimeError('Tidak bisa mendeteksi konfigurasi SSH. Perbaiki openssh-server sebelum instalasi.')
        if self.mode in {'both','wings'} and quick(['systemd-detect-virt']) in {'openvz','lxc','docker'}: raise RuntimeError('Wings memerlukan VPS yang mendukung Docker; virtualisasi ini belum didukung installer.')
        if self.mode in {'panel','both'}:
            if PANEL.exists() and any(PANEL.iterdir()): raise RuntimeError('Folder Panel sudah berisi data. Instalasi baru dibatalkan agar tidak menimpa instalasi lama.')
            if Path('/etc/nginx/sites-available/comic-pterodactyl.conf').exists(): raise RuntimeError('Konfigurasi Nginx lama ditemukan. Periksa instalasi sebelumnya.')
            if self.mode=='both' and (Path('/etc/pterodactyl/config.yml').exists() or Path('/usr/local/bin/wings').exists()): raise RuntimeError('Wings sudah ada. Gunakan Panel Only atau rawat instalasi lama.')
            resolved={x[4][0] for x in socket.getaddrinfo(self.c['domain'],80,type=socket.SOCK_STREAM)}
            permitted=set(self.info['local_ips'])|{self.info['ip']}
            if not resolved & permitted: raise RuntimeError('DNS domain belum mengarah ke VPS. Gunakan DNS-only saat menerbitkan SSL.')
            if shutil.which('mariadb') and quick(['mariadb','--protocol=socket','-u','root','--batch','--skip-column-names','-e',"SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME='panel';"]): raise RuntimeError('Database panel sudah ada; instalasi baru dibatalkan.')
            if quick(['systemctl','is-active','apache2'])=='active': raise RuntimeError('Apache sudah aktif. Gunakan VPS bersih untuk installer ini.')
        elif self.mode=='wings':
            if Path('/usr/local/bin/wings').exists() or Path('/etc/pterodactyl/config.yml').exists(): raise RuntimeError('Wings sudah ada. Installer baru tidak menimpanya.')
        else:
            if not MANAGED.exists() or not (PANEL/'.env').exists(): raise RuntimeError('Operasi ini hanya tersedia untuk Panel yang dibuat installer ini.')
            self.meta=json.loads(MANAGED.read_text())
            if self.meta.get('panel_path')!=str(PANEL): raise RuntimeError('Metadata instalasi tidak valid.')
            if self.mode=='update':
                current=self.php('version').strip()
                if not re.fullmatch(r'v?1\.\d+\.\d+',current): raise RuntimeError('Versi Panel tidak dikenali; update otomatis ditolak.')
                ver=lambda s:tuple(map(int,s.lstrip('v').split('.')))
                if ver(current)>ver(PANEL_VERSION): raise RuntimeError('Panel lebih baru daripada paket ini; downgrade ditolak.')
                if Path('/usr/local/bin/wings').exists():
                    wing=quick(['/usr/local/bin/wings','version'])
                    match=re.search(r'v?(1\.\d+\.\d+)',wing)
                    if not match or ver(match.group(1))>ver(WINGS_VERSION): raise RuntimeError('Versi Wings tidak dikenal atau lebih baru; downgrade ditolak.')
        if self.mode=='restore': self.verify_backup(self.c['backup'])
        self.log('System check lulus. Tidak ada credential dicetak ke log.')

    def apt_index(self): self.run(['apt-get','update'])
    def base_dependencies(self): self.run(['apt-get','install','-y','curl','ca-certificates','tar','unzip','git','nginx','ufw','certbot','python3-certbot-nginx','cron'])
    def php_dependencies(self): self.run(['apt-get','install','-y','php8.3-cli','php8.3-common','php8.3-fpm','php8.3-gd','php8.3-mysql','php8.3-mbstring','php8.3-bcmath','php8.3-xml','php8.3-curl','php8.3-zip','composer'])
    def mariadb(self):
        self.run(['apt-get','install','-y','mariadb-server','mariadb-client'])
        self.run(['systemctl','enable','--now','mariadb'])
    def redis(self):
        self.run(['apt-get','install','-y','redis-server'])
        self.run(['systemctl','enable','--now','redis-server'])

    def download(self,url,dest,digest):
        self.run(['curl','--fail','--location','--proto','=https','--tlsv1.2','--retry','3','--connect-timeout','20','--max-time','900',url,'-o',dest])
        if sha256(dest)!=digest: raise RuntimeError('SHA-256 rilis tidak cocok. Unduhan tidak akan dijalankan.')
        self.log('SHA-256 rilis resmi terverifikasi.')

    def panel(self):
        PANEL.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='comic-panel-') as t:
            a=Path(t)/'panel.tar.gz'
            self.download(f'https://github.com/pterodactyl/panel/releases/download/{PANEL_VERSION}/panel.tar.gz',a,PANEL_HASH)
            safe_extract(a,PANEL)
        if self.mode!='update':
            if (PANEL/'.env').exists(): raise RuntimeError('.env tidak boleh tertimpa pada instalasi baru.')
            private_write(PANEL/'.env',(PANEL/'.env.example').read_text())
        self.run(['composer','install','--no-dev','--optimize-autoloader','--no-interaction','--no-progress'],cwd=PANEL,timeout=1800)
        if self.mode!='update': self.artisan('key:generate','--force')

    def wings(self):
        if not shutil.which('docker'):
            # Signed Ubuntu repository; no remote shell installer.
            self.run(['apt-get','install','-y','docker.io'])
        self.run(['systemctl','enable','--now','docker'])
        arch='amd64' if platform.machine()=='x86_64' else 'arm64'
        with tempfile.TemporaryDirectory(prefix='comic-wings-') as t:
            dest=Path(t)/'wings'; self.download(f'https://github.com/pterodactyl/wings/releases/download/{WINGS_VERSION}/wings_linux_{arch}',dest,WINGS_HASH[arch])
            if self.mode=='update':self.run(['systemctl','stop','wings'])
            new=Path('/usr/local/bin/wings.comic-new');shutil.copyfile(dest,new);os.chmod(new,0o755);new.replace('/usr/local/bin/wings')
        Path('/etc/pterodactyl').mkdir(mode=0o700,exist_ok=True)
        private_write('/etc/systemd/system/wings.service','''[Unit]
Description=Pterodactyl Wings
After=docker.service network-online.target
Requires=docker.service
PartOf=docker.service
[Service]
User=root
WorkingDirectory=/etc/pterodactyl
LimitNOFILE=4096
ExecStart=/usr/local/bin/wings
Restart=on-failure
RestartSec=5
[Install]
WantedBy=multi-user.target
''',0o644)
        if self.mode=='wings':
            private_write('/etc/pterodactyl/config.yml',self.c['wings_config'])
            self.log('Konfigurasi Wings ditulis dengan permission 0600.')
        self.run(['systemctl','daemon-reload'])

    def database(self):
        # Fresh install only, deliberately no IF NOT EXISTS / ALTER USER.
        sql="CREATE DATABASE panel;\nCREATE USER 'pterodactyl'@'127.0.0.1' IDENTIFIED BY '"+self.c['db_password']+"';\nGRANT ALL PRIVILEGES ON panel.* TO 'pterodactyl'@'127.0.0.1';\n"
        self.run(['mariadb','--protocol=socket','-u','root'],input_text=sql,quiet=True)
        values={'APP_NAME':self.c.get('brand','BOLT HOST'),'APP_URL':'https://'+self.c['domain'],'APP_TIMEZONE':'Asia/Jakarta','APP_ENVIRONMENT_ONLY':'true','APP_DEBUG':'false','DB_HOST':'127.0.0.1','DB_DATABASE':'panel','DB_USERNAME':'pterodactyl','DB_PASSWORD':self.c['db_password'],'CACHE_STORE':'redis','CACHE_DRIVER':'redis','SESSION_DRIVER':'redis','QUEUE_CONNECTION':'redis','MAIL_MAILER':'log','MAIL_FROM_ADDRESS':self.c['email'],'PTERODACTYL_TELEMETRY_ENABLED':'false','LOG_LEVEL':'warning'}
        self.env_update(values)
        self.artisan('config:clear');self.artisan('migrate','--seed','--force')
        self.permissions()

    def env_update(self,values):
        p=PANEL/'.env';lines=p.read_text().splitlines()
        for key,value in values.items():
            line=key+'='+json.dumps(value)
            matches=[i for i,s in enumerate(lines) if s.startswith(key+'=')]
            if matches:lines[matches[0]]=line
            else:lines.append(line)
        private_write(p,'\n'.join(lines)+'\n',0o640)

    def permissions(self):
        self.run(['chown','-R','www-data:www-data',PANEL])
        self.run(['chmod','-R','u+rwX,g+rX',PANEL/'storage',PANEL/'bootstrap/cache'])
        os.chmod(PANEL/'.env',0o640)

    def firewall(self):
        # Keep all discovered SSH ports before enabling; never reset existing rules.
        ssh=quick(['/usr/sbin/sshd','-T'])
        ports={int(m) for m in re.findall(r'^port (\d+)$',ssh,re.M)}
        connection=os.environ.get('SSH_CONNECTION','').split()
        if len(connection)==4 and connection[3].isdigit():ports.add(int(connection[3]))
        if not ports:raise RuntimeError('Port SSH tidak terdeteksi; firewall tidak diaktifkan. Pastikan openssh-server tersedia.')
        for p in sorted(ports):self.run(['ufw','allow',f'{p}/tcp'])
        service_ports=[80,443]
        if self.mode in {'both','wings'}:service_ports.extend([8443,8080,2022])
        for p in service_ports:self.run(['ufw','allow',f'{p}/tcp'])
        self.run(['ufw','--force','enable'])

    def nginx(self):
        d=self.c['domain']
        conf='''server {
    listen 80;
    server_name DOMAIN;
    root /var/www/pterodactyl/public;
    index index.php;
    client_max_body_size 100m;
    client_body_timeout 120s;
    sendfile off;
    location / { try_files $uri $uri/ /index.php?$query_string; }
    location ~ \\.php$ {
        include fastcgi_params;
        fastcgi_pass unix:/run/php/php8.3-fpm.sock;
        fastcgi_index index.php;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        fastcgi_param HTTP_PROXY "";
        fastcgi_read_timeout 300;
    }
    location ~ /\\.ht { deny all; }
    location ~ /\\.(?!well-known).* { deny all; }
}
'''.replace('DOMAIN',d)
        p=Path('/etc/nginx/sites-available/comic-pterodactyl.conf');private_write(p,conf,0o644)
        link=Path('/etc/nginx/sites-enabled/comic-pterodactyl.conf')
        if not link.exists():link.symlink_to(p)
        self.run(['nginx','-t']);self.run(['systemctl','enable','--now','nginx','php8.3-fpm','cron']);self.run(['systemctl','reload','nginx'])

    def ssl(self):
        self.run(['certbot','--nginx','--non-interactive','--agree-tos','--email',self.c['email'],'--redirect','-d',self.c['domain']],timeout=600)
        self.run(['systemctl','enable','--now','certbot.timer'])
        Path('/etc/letsencrypt/renewal-hooks/deploy').mkdir(parents=True,exist_ok=True)
        private_write('/etc/letsencrypt/renewal-hooks/deploy/comic-services.sh','#!/bin/sh\nset -eu\nnginx -t\nsystemctl reload nginx\nif systemctl is-active --quiet wings; then systemctl restart wings; fi\n',0o755)

    def admin(self):
        self.php('admin',self.c)
        if self.mode=='both':
            c=dict(self.c,memory=max(512,int(self.info['memory_bytes']/1024**2)-1024),disk=max(1024,int(self.info['disk_bytes']/1024**2)-2048))
            self.php('node',c)
        self.log('Administrator dibuat.'+(' Lokasi, node, dan konfigurasi Wings dibuat otomatis.' if self.mode=='both' else ''))

    def services(self):
        private_write('/etc/cron.d/comic-pterodactyl','* * * * * www-data /usr/bin/php /var/www/pterodactyl/artisan schedule:run >> /dev/null 2>&1\n',0o644)
        private_write('/etc/systemd/system/pteroq.service','''[Unit]
Description=Pterodactyl Queue Worker
After=redis-server.service
[Service]
User=www-data
Group=www-data
Restart=always
RestartSec=5
ExecStart=/usr/bin/php /var/www/pterodactyl/artisan queue:work --queue=high,standard,low --sleep=3 --tries=3
[Install]
WantedBy=multi-user.target
''',0o644)
        self.permissions();self.run(['systemctl','daemon-reload']);self.run(['systemctl','enable','--now','pteroq'])
        if self.mode=='both':self.run(['systemctl','enable','--now','wings'])

    def theme(self):
        license_key=self.c.get('license_key','')
        self.run(['python3',BASE/'theme/install-theme.py','--panel',PANEL,'--license-stdin'],input_text=license_key+'\n')
        self.artisan('route:clear')
        self.artisan('view:clear')

    def verify(self):
        services=['docker','wings'] if self.mode=='wings' else ['nginx','php8.3-fpm','mariadb','redis-server','pteroq']
        if self.mode=='both' or self.meta.get('wings'): services+=['docker','wings']
        if self.mode=='wings':self.run(['systemctl','enable','--now','wings'])
        # Wait for startup; repeated checks avoid reporting a briefly-active crashing service as success.
        for _ in range(3):
            time.sleep(2)
            for service in set(services):self.run(['systemctl','is-active','--quiet',service],quiet=True,timeout=15)
        if self.mode!='wings':
            domain=self.c.get('domain') or self.meta.get('domain')
            self.run(['curl','--fail','--silent','--show-error','--output','/dev/null','--connect-timeout','15','--max-time','40','--resolve',domain+':443:127.0.0.1','https://'+domain+'/auth/login'],timeout=45)
        self.log('Layanan aktif dan pemeriksaan selesai.')

    def save_meta(self):
        if self.mode in {'panel','both'}:
            self.meta={'panel_path':str(PANEL),'domain':self.c['domain'],'wings':self.mode=='both','panel_version':PANEL_VERSION,'wings_version':WINGS_VERSION if self.mode=='both' else None}
        elif self.mode=='update':self.meta.update(panel_version=PANEL_VERSION,wings_version=WINGS_VERSION if self.meta.get('wings') else None)
        private_write(MANAGED,json.dumps(self.meta,indent=2))

    def maintenance_on(self):
        self.artisan('down');self.maintenance=True;self.run(['systemctl','stop','pteroq'])
    def maintenance_off(self):
        self.artisan('up');self.run(['systemctl','restart','pteroq']);self.maintenance=False

    def backup(self):
        BACKUPS.mkdir(parents=True,exist_ok=True,mode=0o700);os.chmod(BACKUPS,0o700)
        # Scope known database and APP_KEY together, no password appears in argv.
        name=time.strftime('backup-%Y-%m-%dT%H-%M-%S-')+uuid.uuid4().hex[:8]+'.tar.gz';dest=BACKUPS/name
        already=self.maintenance
        if not already:self.maintenance_on()
        try:
            required=max(100*1024**2, sum(p.stat().st_size for p in PANEL.rglob('*') if p.is_file() and not p.is_symlink()))
            if shutil.disk_usage(BACKUPS).free<required*2:raise RuntimeError('Ruang backup kurang. Butuh setidaknya 2× ukuran Panel.')
            with tempfile.TemporaryDirectory(dir=STATE,prefix='backup-stage-') as t:
                stage=Path(t)
                dump=stage/'database.sql'
                # Dump to file instead of memory. Root socket is the installer-supported DB configuration.
                with dump.open('wb') as output:
                    result=subprocess.run(['mariadb-dump','--protocol=socket','-u','root','--single-transaction','--quick','--routines','--triggers','panel'],stdout=output,stderr=subprocess.PIPE,timeout=600)
                if result.returncode:raise RuntimeError('Database dump gagal; backup tidak dibuat.')
                (stage/'metadata.json').write_text(json.dumps(self.meta))
                with tarfile.open(dest,'w:gz') as tar:
                    tar.add(PANEL,arcname='panel');tar.add(dump,arcname='database.sql');tar.add(stage/'metadata.json',arcname='metadata.json')
                    for path,label in [('/etc/pterodactyl/config.yml','wings-config.yml'),('/etc/nginx/sites-available/comic-pterodactyl.conf','nginx.conf')]:
                        if Path(path).exists():tar.add(path,arcname=label)
            os.chmod(dest,0o600);private_write(str(dest)+'.sha256',sha256(dest))
            self.log('Backup tersimpan: '+name+' (tidak termasuk volume game).')
        except Exception:
            dest.unlink(missing_ok=True);raise
        finally:
            if not already:self.maintenance_off()
        return name

    def verify_backup(self,name):
        p=BACKUPS/name
        if p.is_symlink() or not p.is_file() or p.parent.resolve()!=BACKUPS.resolve():raise RuntimeError('Backup tidak ditemukan.')
        if not p.with_suffix(p.suffix+'.sha256').exists() or sha256(p)!=p.with_suffix(p.suffix+'.sha256').read_text().strip():raise RuntimeError('Integritas backup gagal.')
        return p

    def restore(self):
        backup=self.verify_backup(self.c['backup'])
        with tempfile.TemporaryDirectory(dir=STATE,prefix='restore-') as t:
            stage=Path(t);safe_extract(backup,stage)
            if not (stage/'panel/.env').is_file() or not (stage/'database.sql').is_file():raise RuntimeError('Backup tidak lengkap.')
            meta=json.loads((stage/'metadata.json').read_text())
            if meta.get('domain')!=self.meta.get('domain') or meta.get('wings')!=self.meta.get('wings'):raise RuntimeError('Restore hanya didukung pada instalasi asal yang sama.')
            self.maintenance_on()
            # Preserve the exact old tree until a successful restoration, rather than deleting it.
            old=PANEL.with_name('pterodactyl-before-restore-'+uuid.uuid4().hex[:8])
            PANEL.rename(old);(stage/'panel').rename(PANEL)
            try:
                self.run(['mariadb','--protocol=socket','-u','root'],input_text='DROP DATABASE panel; CREATE DATABASE panel; GRANT ALL PRIVILEGES ON panel.* TO \'pterodactyl\'@\'127.0.0.1\';',quiet=True)
                with (stage/'database.sql').open('rb') as sql:
                    p=subprocess.run(['mariadb','--protocol=socket','-u','root','panel'],stdin=sql,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,timeout=600)
                if p.returncode:raise RuntimeError('Pemulihan SQL gagal. Panel tetap maintenance; gunakan backup pengaman.')
                for name,dest in [('nginx.conf','/etc/nginx/sites-available/comic-pterodactyl.conf'),('wings-config.yml','/etc/pterodactyl/config.yml')]:
                    if (stage/name).exists():private_write(dest,(stage/name).read_text(),0o600 if name.startswith('wings') else 0o644)
                self.meta=meta;private_write(MANAGED,json.dumps(meta));self.permissions();self.artisan('optimize:clear');self.run(['nginx','-t']);self.run(['systemctl','reload','nginx'])
                if meta.get('wings'):self.run(['systemctl','restart','wings'])
                self.maintenance_off();self.log('Folder sebelum restore dipertahankan: '+str(old))
            except Exception:
                self.log('Restore terhenti. Folder lama dipertahankan: '+str(old));raise

    def repair(self):
        self.permissions();self.artisan('optimize:clear');self.theme();self.run(['nginx','-t'])
        services=['nginx','php8.3-fpm','redis-server','mariadb','pteroq']
        if self.meta.get('wings'):services+=['docker','wings']
        self.run(['systemctl','restart',*services])

    def update_after(self):
        self.artisan('migrate','--seed','--force');self.artisan('optimize:clear');self.permissions();self.theme();self.artisan('queue:restart')
        if self.meta.get('wings'):self.wings();self.run(['systemctl','restart','wings'])
        self.maintenance_off();self.save_meta()

    def plan(self):
        p=[('Check system',1,self.check)]
        if self.mode in {'both','panel'}:
            p += [('Update system package index',2,self.apt_index),('Install dependencies',2,self.base_dependencies),('Install PHP',2,self.php_dependencies),('Install MariaDB',2,self.mariadb),('Install Redis',2,self.redis),('Download Pterodactyl',3,self.panel)]
            if self.mode=='both':p += [('Install Wings',4,self.wings)]
            p += [('Configure database',5,self.database),('Configure firewall',6,self.firewall),('Configure Nginx',6,self.nginx),('Install SSL',6,self.ssl),('Create administrator'+(' & node' if self.mode=='both' else ''),7,self.admin),('Enable services',7,self.services),('Apply comic theme',7,self.theme),('Verify services',8,self.verify),('Save installation metadata',8,self.save_meta)]
        elif self.mode=='wings':p += [('Update system package index',2,self.apt_index),('Install dependencies',2,lambda:self.run(['apt-get','install','-y','curl','ca-certificates','ufw'])),('Install Wings',4,self.wings),('Configure firewall',6,self.firewall),('Verify Wings',8,self.verify)]
        elif self.mode=='backup':p += [('Backup Panel & database',5,self.backup)]
        elif self.mode=='restore':p += [('Create safety backup',5,self.backup),('Restore selected backup',5,self.restore),('Verify services',8,self.verify)]
        elif self.mode=='repair':p += [('Create safety backup',5,self.backup),('Repair services & theme',6,self.repair),('Verify services',8,self.verify)]
        elif self.mode=='update':p += [('Create safety backup',5,self.backup),('Enter maintenance',3,self.maintenance_on),('Update Panel release',3,self.panel),('Migrate & update Wings',5,self.update_after),('Verify services',8,self.verify)]
        return p

    def execute(self):
        tasks=self.plan();self.report('tasks',[{'label':label,'status':'pending'} for label,_,_ in tasks])
        for i,(label,step,fn) in enumerate(tasks):
            self.report('start',{'index':i,'label':label,'step':step,'progress':round(i/len(tasks)*100)})
            self.log('→ '+label);fn();self.log('✓ '+label)
            self.report('done',{'index':i,'progress':round((i+1)/len(tasks)*100)})
        messages={'backup':'Backup panel dan database tersimpan. Volume game tidak termasuk.','restore':'Backup dipulihkan. Folder Panel sebelumnya tetap disimpan.','repair':'Layanan dan theme diperiksa serta dipulihkan.','update':'Panel dan Wings terpasang diperbarui ke versi paket.','wings':'Wings aktif memakai konfigurasi yang diberikan. Tambahkan allocation dari Panel.','panel':'Panel dan theme siap. SMTP dapat diatur melalui Admin → Settings.','both':'Panel, Wings, lokasi, node, dan theme siap. Tambahkan allocation dan server game dari Admin.'}
        domain=self.c.get('domain') or self.meta.get('domain')
        return {'panel_url':'https://'+domain if domain else '', 'message':messages[self.mode]}
