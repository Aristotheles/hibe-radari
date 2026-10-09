import argparse,json,os,secrets,threading
from pathlib import Path
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from urllib.parse import urlsplit
from .store import SQLiteStore,FirestoreStore
from .service import Service
from .demo import seed
ROOT=Path(__file__).resolve().parent.parent
class App:
 def __init__(self,demo=False):
  self.demo=demo;self.sessions={};self.lock=threading.Lock()
  if demo:
   (ROOT/'data').mkdir(exist_ok=True);s=SQLiteStore(ROOT/'data/demo.db');seed(s);uid='demo-admin'
  else:
   import firebase_admin
   firebase_admin.initialize_app(options={'projectId':os.environ['FIREBASE_PROJECT_ID']});s=FirestoreStore();uid=os.environ.get('ADMIN_UID')
   if not uid:raise ValueError('ADMIN_UID gerekli')
  self.service=Service(s,uid,approvals=ROOT/'approvals' if demo else None)
 def user(self,t):
  if self.demo:
   if t not in self.sessions:raise PermissionError('Giriş gerekli')
   return self.sessions[t]
  from firebase_admin import auth
  try:u=auth.verify_id_token(t,check_revoked=True)
  except Exception:raise PermissionError('Oturum geçersiz') from None
  if u.get('firebase',{}).get('sign_in_provider')!='google.com' or not u.get('email_verified'):raise PermissionError('Doğrulanmış Google girişi gerekli')
  return u

def handler(app):
 class H(BaseHTTPRequestHandler):
  def log_message(self,*a):pass
  def send(self,status,value,mime='application/json; charset=utf-8'):
   b=json.dumps(value,ensure_ascii=False).encode() if mime.startswith('application/json') else value
   self.send_response(status);self.send_header('Content-Type',mime);self.send_header('Content-Length',str(len(b)));self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.send_header('Referrer-Policy','no-referrer');self.end_headers();self.wfile.write(b)
  def user(self):return app.user(self.headers.get('Authorization','').removeprefix('Bearer '))
  def do_GET(self):
   try:
    p=urlsplit(self.path).path
    if p=='/api/config':self.send(200,{'demo':app.demo,'firebase':{k:os.environ.get(v,'') for k,v in {'apiKey':'FIREBASE_WEB_API_KEY','authDomain':'FIREBASE_AUTH_DOMAIN','projectId':'FIREBASE_PROJECT_ID','appId':'FIREBASE_APP_ID'}.items()}});return
    if p=='/api/calls':self.send(200,app.service.public());return
    if p=='/api/me':
     u=self.user();self.send(200,{'email':u['email'],'admin':app.service.is_admin(u),'preferences':app.service.store.get('users',u['uid'])});return
    if p=='/api/admin':
     u=self.user();app.service.require_admin(u);self.send(200,{'calls':app.service.store.all('calls'),'sources':json.loads((ROOT/'config/sources.json').read_text(encoding='utf-8')),'metrics':app.service.metrics(u)});return
    files={'/':'index.html','/app.js':'app.js','/radar.mjs':'radar.mjs','/style.css':'style.css'}
    if p not in files:self.send(404,{'error':'Bulunamadı'});return
    f=ROOT/'web'/files[p];self.send(200,f.read_bytes(),{'html':'text/html','js':'text/javascript','mjs':'text/javascript','css':'text/css'}[f.suffix[1:]]+'; charset=utf-8')
   except PermissionError as e:self.send(403,{'error':str(e)})
   except Exception:self.send(500,{'error':'Sunucu işlemi tamamlayamadı'})
  def do_POST(self):
   try:
    o=self.headers.get('Origin')
    if o and urlsplit(o).netloc!=self.headers.get('Host'):raise PermissionError('Başka kaynaktan yazma engellendi')
    if self.headers.get('Content-Type','').split(';')[0]!='application/json':raise ValueError('JSON gerekli')
    n=int(self.headers.get('Content-Length','0'))
    if not 0<n<=150000:raise ValueError('İstek boyutu sınırı')
    d=json.loads(self.rfile.read(n));p=urlsplit(self.path).path
    with app.lock:
     if p=='/api/demo-login':
      if not app.demo:raise PermissionError('Demo kapalı')
      a=d.get('role')=='admin';t=secrets.token_urlsafe(32);app.sessions[t]={'uid':'demo-admin' if a else 'demo-user','email':'senoltemur@gmail.com' if a else 'demo@example.org','email_verified':True};self.send(200,{'token':t});return
     if p=='/api/unsubscribe':
      from .notifications import verify_unsubscribe
      uid=verify_unsubscribe(d['token'],os.environ.get('UNSUBSCRIBE_SECRET',''));record=app.service.store.get('users',uid)
      if record:record['subscribed']=False;app.service.store.put('users',uid,record)
      self.send(200,{'ok':True});return
     u=self.user()
     if p=='/api/preferences':self.send(200,app.service.preferences(u,d));return
     if p=='/api/call':self.send(200,app.service.save(u,d));return
     if p=='/api/approve':self.send(200,app.service.approve(u,d['id'],d['version']));return
     self.send(404,{'error':'Bulunamadı'})
   except PermissionError as e:self.send(403,{'error':str(e)})
   except (ValueError,KeyError,TypeError) as e:self.send(400,{'error':str(e)})
   except Exception:self.send(500,{'error':'İşlem tamamlanamadı'})
 return H

def main():
 p=argparse.ArgumentParser();p.add_argument('--demo',action='store_true');p.add_argument('--port',type=int,default=8000);a=p.parse_args();s=ThreadingHTTPServer(('127.0.0.1',a.port),handler(App(a.demo)));print(f'http://127.0.0.1:{a.port} — '+('YEREL DEMO' if a.demo else 'Firebase'));s.serve_forever()
if __name__=='__main__':main()
