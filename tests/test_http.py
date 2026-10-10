import unittest,threading,json,urllib.request,urllib.error
from http.server import ThreadingHTTPServer
from hibe.server import App,handler
from hibe.store import MemoryStore
from hibe.service import Service
class HTTPTests(unittest.TestCase):
 def setUp(self):
  self.app=object.__new__(App);self.app.demo=True;self.app.sessions={};self.app.lock=threading.Lock();self.app.service=Service(MemoryStore(),'demo-admin',demo=True);self.server=ThreadingHTTPServer(('127.0.0.1',0),handler(self.app));self.t=threading.Thread(target=self.server.serve_forever,daemon=True);self.t.start();self.base='http://127.0.0.1:'+str(self.server.server_port)
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
  self.assertEqual(code,200);self.assertEqual(data['sources'][0]['name'],'EU Funding & Tenders Portal')
  self.assertEqual(len(data['sources']),154)
  self.assertEqual(sum('özgün liste bekleniyor' in s['name'] for s in data['sources']),11)
 def test_public_routes_are_readable_without_javascript(self):
  from hibe.demo import seed
  seed(self.app.service.store)
  for path in ['/','/ilan/demo-bilim','/takvim','/nasil-calisir','/aboneligim','/yonetim']:
   with urllib.request.urlopen(self.base+path) as response:
    body=response.read().decode('utf-8');self.assertEqual(response.status,200)
    self.assertIn('id="server-content"',body);self.assertIn('id="radar-title"' if path=='/' else 'id="page-title"',body)
    if path=='/':self.assertIn('id="public-data"',body);self.assertIn('class="opportunity-card"',body);self.assertNotIn('<div id="app-shell" hidden>',body)
    self.assertNotIn('<!--SERVER_CONTENT-->',body)
  with urllib.request.urlopen(self.base+'/ilan/demo-bilim') as response:
   self.assertIn('Uygunluk belirsiz',response.read().decode('utf-8'))
 def test_unpublished_call_is_not_a_public_detail(self):
  from hibe.demo import seed
  seed(self.app.service.store)
  with self.assertRaises(urllib.error.HTTPError) as error:urllib.request.urlopen(self.base+'/ilan/demo-cevre')
  with error.exception as response:self.assertEqual(response.code,404);self.assertIn('İlan bulunamadı',response.read().decode('utf-8'))
 def test_source_toggle_requires_admin_and_is_visible_with_health(self):
  code,rows=self.req('/api/sources');ident=rows[0]['id']
  _,user=self.req('/api/demo-login',{'role':'user'})
  self.assertEqual(self.req('/api/source-settings',{'id':ident,'enabled':False},t=user['token'])[0],403)
  _,admin=self.req('/api/demo-login',{'role':'admin'})
  self.assertEqual(self.req('/api/source-settings',{'id':ident,'enabled':False},t=admin['token'])[0],200)
  self.app.service.store.put('source_health','eu-ft',{'id':'eu-ft','health':'failed','error':'Fixture: parser error','fetched':0})
  _,data=self.req('/api/admin',t=admin['token']);source=data['sources'][0]
  self.assertFalse(source['enabled']);self.assertTrue(source['alert']);self.assertEqual(source['health'][0]['health'],'failed')
  self.assertEqual(self.req('/api/source-settings',{'id':ident,'enabled':'yes'},t=admin['token'])[0],400)
 def test_sources_public_and_frontend_modules_mime(self):
  code,data=self.req('/api/sources');self.assertEqual(code,200);self.assertEqual(len(data),154)
  for path in ['/views.mjs','/decision.mjs']:
   with urllib.request.urlopen(self.base+path) as response:self.assertEqual(response.headers.get_content_type(),'text/javascript')
 def test_pro_export_checked_at_http_boundary(self):
  self.assertEqual(self.req('/api/pro/export')[0],403)
  _,login=self.req('/api/demo-login',{'role':'user'});token=login['token']
  self.assertEqual(self.req('/api/pro/export',t=token)[0],403)
  self.req('/api/preferences',{'themes':[],'subscribed':False,'tier':'pro','membership_status':'active'},t=token)
  self.assertEqual(self.req('/api/pro/export',t=token)[0],403)
  self.app.service.store.put('users','demo-user',{'tier':'pro','membership_status':'active'})
  request=urllib.request.Request(self.base+'/api/pro/export',headers={'Authorization':'Bearer '+token})
  with urllib.request.urlopen(request) as response:
   self.assertEqual(response.status,200);self.assertEqual(response.headers.get_content_type(),'text/csv');self.assertIn('Başlık',response.read().decode('utf-8'))
