#!/usr/bin/env python3
"""Loopback-only privileged installer. Never expose this port to a public network."""
import argparse
import contextlib
import fcntl
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import mimetypes
import os
from pathlib import Path
import secrets
import threading
import time
from urllib.parse import urlsplit
from deploy import BASE, STATE, Deployment, private_write, system_info, validate

JOB = {'status':'idle','mode':'','tasks':[],'logs':[],'progress':0}
LOCK = threading.RLock()
AUTH = secrets.token_urlsafe(40)
ROOT = (BASE/'web').resolve()
PORT = 8787
LIVE = False


def persist():
    if LIVE: private_write(STATE/'job.json',json.dumps(JOB))


def report(kind,value):
    with LOCK:
        if kind=='log':
            JOB['logs'].append(time.strftime('[%H:%M:%S] ')+value)
            JOB['logs']=JOB['logs'][-1500:]
        elif kind=='tasks':JOB['tasks']=value
        elif kind=='start':
            JOB['current']=value['label'];JOB['step']=value['step'];JOB['progress']=value['progress'];JOB['tasks'][value['index']]['status']='running'
        elif kind=='done':
            JOB['tasks'][value['index']]['status']='done';JOB['progress']=value['progress']
        persist()


def run_job(mode,config):
    global JOB
    worker=None
    try:
        worker=Deployment(mode,config,report)
        result=worker.execute()
        with LOCK:JOB.update(result,status='success',progress=100,step=8);persist()
    except Exception as e:
        # Exceptions must pass through the same redactor as subprocess output.
        if worker:worker.log('ERROR: '+str(e))
        else:report('log','Input tidak valid.')
        with LOCK:
            JOB.update(status='failed',error='Proses dihentikan. Periksa log. Langkah yang sudah selesai tidak diulang otomatis.')
            for t in JOB['tasks']:
                if t['status']=='running':t['status']='failed'
            persist()


class Handler(BaseHTTPRequestHandler):
    server_version='ComicInstaller/1.0'
    def log_message(self,*args):pass  # No request URLs, tokens or credentials in access logs.
    def headers_common(self):
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Referrer-Policy','no-referrer')
        self.send_header('X-Frame-Options','DENY')
        self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; font-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
    def respond(self,status,data):
        content=json.dumps(data).encode();self.send_response(status);self.headers_common();self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(content)));self.end_headers();self.wfile.write(content)
    def valid_host(self):
        return self.headers.get('Host') in {f'127.0.0.1:{PORT}',f'localhost:{PORT}'}
    def authorized(self):
        provided=self.headers.get('Authorization','')
        return self.valid_host() and secrets.compare_digest(provided,'Bearer '+AUTH)
    def do_GET(self):
        if not self.valid_host():self.respond(403,{'error':'Hostname ditolak. Gunakan localhost via SSH tunnel.'});return
        path=urlsplit(self.path).path
        if path.startswith('/api/'):
            if not self.authorized():self.respond(401,{'error':'Token sesi dibutuhkan. Buka tautan launcher.'});return
            if path=='/api/state':
                with LOCK:self.respond(200,JOB)
            elif path=='/api/system':self.respond(200,system_info())
            else:self.respond(404,{'error':'Endpoint tidak tersedia.'})
            return
        # Only compiled preview assets. The installer source and backups are outside ROOT.
        target=(ROOT/('index.html' if path=='/' else path.lstrip('/'))).resolve()
        if not target.is_relative_to(ROOT) or target.is_symlink() or not target.is_file():self.respond(404,{'error':'File tidak ditemukan.'});return
        if target.suffix not in {'.html','.js','.css','.svg','.ttf','.txt','.png'}:self.respond(404,{'error':'File tidak tersedia.'});return
        content=target.read_bytes();self.send_response(200);self.headers_common();self.send_header('Content-Type',mimetypes.guess_type(target)[0] or 'application/octet-stream');self.send_header('Content-Length',str(len(content)));self.end_headers();self.wfile.write(content)
    def do_POST(self):
        global JOB
        if not self.authorized():self.respond(401,{'error':'Akses ditolak.'});return
        origin=self.headers.get('Origin')
        if origin != 'http://'+self.headers.get('Host',''):self.respond(403,{'error':'Origin tidak cocok.'});return
        if self.headers.get('Content-Type')!='application/json':self.respond(415,{'error':'JSON diperlukan.'});return
        if not LIVE:self.respond(403,{'error':'Server preview tidak bisa mengubah VPS.'});return
        try:
            length=int(self.headers.get('Content-Length','0'))
            if length<=0 or length>65536:raise ValueError('Ukuran permintaan tidak valid.')
            data=json.loads(self.rfile.read(length))
            if urlsplit(self.path).path!='/api/run':self.respond(404,{'error':'Endpoint tidak tersedia.'});return
            if not isinstance(data,dict) or data.get('confirmed') is not True:raise ValueError('Konfirmasi diperlukan.')
            mode=data.get('mode');config=validate(mode,data.get('config'))
            with LOCK:
                if JOB['status']=='running':self.respond(409,{'error':'Masih ada pekerjaan berjalan.'});return
                JOB={'status':'running','mode':mode,'tasks':[],'logs':[],'progress':0,'step':1,'current':'Preparing installation'};persist()
                threading.Thread(target=run_job,args=(mode,config),daemon=False).start()
                self.respond(202,JOB)
        except (ValueError,TypeError,KeyError,json.JSONDecodeError) as e:self.respond(400,{'error':str(e)})
    def handle(self):
        self.connection.settimeout(15)
        with contextlib.suppress(BrokenPipeError,ConnectionResetError,TimeoutError):super().handle()


def main():
    global PORT,LIVE,JOB
    parser=argparse.ArgumentParser();parser.add_argument('--live',action='store_true');parser.add_argument('--port',type=int,default=8787);args=parser.parse_args()
    if not 1024<=args.port<=65535:parser.error('Port 1024–65535 diperlukan.')
    PORT=args.port;LIVE=args.live
    handle=None
    if LIVE:
        if os.geteuid()!=0:parser.error('Gunakan sudo untuk installer nyata.')
        os.umask(0o077);STATE.mkdir(parents=True,exist_ok=True,mode=0o700);os.chmod(STATE,0o700)
        handle=(STATE/'installer.lock').open('w')
        try:fcntl.flock(handle,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:parser.error('Launcher lain sedang berjalan.')
        if (STATE/'job.json').exists():
            try:JOB=json.loads((STATE/'job.json').read_text())
            except json.JSONDecodeError:pass
            if JOB.get('status')=='running':JOB.update(status='interrupted',error='Launcher sebelumnya terputus. Periksa kondisi VPS sebelum mencoba lagi.');persist()
    print('\nCOMIC PTERO • '+('LIVE VPS INSTALLER' if LIVE else 'SAFE PREVIEW SERVER'),flush=True)
    if LIVE:
        print(f'Buka SSH local forwarding: localhost:{PORT} → VPS 127.0.0.1:{PORT}',flush=True)
        print(f'URL: http://127.0.0.1:{PORT}/#token={AUTH}',flush=True)
        print('Token hanya untuk sesi ini. Jangan bagikan. Port tidak perlu dibuka di firewall.',flush=True)
    else:print(f'Preview URL: http://127.0.0.1:{PORT}/',flush=True)
    print('Biarkan launcher tetap berjalan sampai selesai. Ctrl+C untuk menutup.',flush=True)
    server=ThreadingHTTPServer(('127.0.0.1',PORT),Handler)
    try:server.serve_forever()
    except KeyboardInterrupt:
        with LOCK:busy=JOB.get('status')=='running'
        print('Menutup UI; menunggu pekerjaan selesai.' if busy else 'Sesi ditutup.',flush=True)
    finally:server.server_close()

if __name__=='__main__':main()
