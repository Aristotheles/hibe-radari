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
  except urllib.error.HTTPError as e:return e.code,json.load(e)
 def test_unauthorized_admin(self):self.assertEqual(self.req('/api/admin')[0],403)
 def test_user_admin_blocked(self):
  _,r=self.req('/api/demo-login',{'role':'user'});self.assertEqual(self.req('/api/admin',t=r['token'])[0],403)
 def test_preferences_login(self):self.assertEqual(self.req('/api/preferences',{'themes':[],'subscribed':True})[0],403)
 def test_cross_origin(self):self.assertEqual(self.req('/api/demo-login',{'role':'admin'},origin='https://evil.org')[0],403)
 def test_demo_disabled(self):self.app.demo=False;self.assertEqual(self.req('/api/demo-login',{'role':'admin'})[0],403)
