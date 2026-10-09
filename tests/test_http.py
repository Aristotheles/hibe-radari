import unittest,threading,json,urllib.request,urllib.error
from http.server import ThreadingHTTPServer
from hibe.server import App,handler
from hibe.store import MemoryStore
from hibe.service import Service
class HTTPTests(unittest.TestCase):
 def setUp(self):
  self.app=object.__new__(App);self.app.demo=True;self.app.sessions={};self.app.lock=threading.Lock();self.app.service=Service(MemoryStore(),'demo-admin');self.server=ThreadingHTTPServer(('127.0.0.1',0),handler(self.app));self.t=threading.Thread(target=self.server.serve_forever,daemon=True);self.t.start();self.base='http://127.0.0.1:'+str(self.server.server_port)
 def tearDown(self):self.server.shutdown();self.server.server_close();self.t.join()
 def req(self,p,d=None,t='',origin=None):
  h={'Content-Type':'application/json'}
  if t:h['Authorization']='Bearer '+t
  if origin:h['Origin']=origin
  r=urllib.request.Request(self.base+p,data=json.dumps(d).encode() if d is not None else None,headers=h)
  try:
   with urllib.request.urlopen(r) as x:return x.status,json.load(x)
  except urllib.error.HTTPError as e:
   with e:return e.code,json.load(e)
 def test_unauthorized_admin(self):self.assertEqual(self.req('/api/admin')[0],403)
 def test_user_admin_blocked(self):
  _,r=self.req('/api/demo-login',{'role':'user'});self.assertEqual(self.req('/api/admin',t=r['token'])[0],403)
 def test_preferences_login(self):self.assertEqual(self.req('/api/preferences',{'themes':[],'subscribed':True})[0],403)
 def test_cross_origin(self):
  for _ in range(3):
   code,response=self.req('/api/demo-login',{'role':'admin'},origin='https://evil.org')
   self.assertEqual(code,403);self.assertEqual(response['error'],'Başka kaynaktan yazma engellendi')
  self.assertEqual(self.app.sessions,{})
 def test_demo_disabled(self):self.app.demo=False;self.assertEqual(self.req('/api/demo-login',{'role':'admin'})[0],403)
 def test_frontend_module_served_as_javascript(self):
  with urllib.request.urlopen(self.base+'/radar.mjs') as r:
   self.assertEqual(r.status,200);self.assertEqual(r.headers.get_content_type(),'text/javascript');self.assertIn(b'filterCalls',r.read())
 def test_admin_registry_turkish_names_and_placeholders(self):
  from pathlib import Path
  from unittest.mock import patch
  original=Path.read_text
  def explicit_encoding(path,*args,**kwargs):
   self.assertEqual(kwargs.get('encoding'),'utf-8')
   return original(path,*args,**kwargs)
  _,login=self.req('/api/demo-login',{'role':'admin'})
  with patch.object(Path,'read_text',explicit_encoding):
   code,data=self.req('/api/admin',t=login['token'])
  self.assertEqual(code,200);self.assertEqual(data['sources'][0]['name'],'Türkiye Ulusal Ajansı')
  self.assertEqual(len(data['sources']),30)
  self.assertEqual(sum('özgün liste bekleniyor' in s['name'] for s in data['sources']),11)
