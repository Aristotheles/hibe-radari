from datetime import date,datetime,timezone
from pathlib import Path
import json
from .domain import *
def now():return datetime.now(timezone.utc).isoformat()
class Service:
 def __init__(self,store,admin_uid,today=date.today,approvals=None):self.store=store;self.admin_uid=admin_uid;self.today=today;self.approvals=approvals
 def is_admin(self,u):return bool(self.admin_uid and u.get('uid')==self.admin_uid and u.get('email_verified') is True)
 def require_admin(self,u):
  if not self.is_admin(u):raise PermissionError('Yönetici yetkisi gerekli')
 def save(self,u,c):
  self.require_admin(u);validate(c);c={k:v for k,v in c.items() if k not in {'approval','version'}};c['version']=version(c);self.store.put('calls',c['id'],c);return c
 def approve(self,u,i,v):
  self.require_admin(u);c=self.store.get('calls',i)
  if not c or version(c)!=v:raise ValueError('İçerik değişti; yeniden inceleyin')
  c['approval']={'reviewed':True,'version':v,'uid':u['uid'],'at':now()};self.store.put('calls',i,c)
  if self.approvals:
   p=Path(self.approvals);p.mkdir(exist_ok=True);(p/(i+'.json')).write_text(json.dumps(c['approval'],indent=2))
  return c
 def preferences(self,u,d):
  if not u.get('uid') or u.get('email_verified') is not True:raise PermissionError('Doğrulanmış giriş gerekli')
  if not isinstance(d.get('subscribed'),bool) or not isinstance(d.get('themes'),list) or any(t not in THEMES for t in d['themes']):raise ValueError('Tercihler geçersiz')
  old=self.store.get('users',u['uid']) or {}
  r={'uid':u['uid'],'email':u['email'],'themes':list(set(d['themes'])),'subscribed':d['subscribed'],'tier':old.get('tier','free'),'created_at':old.get('created_at',now()),'updated_at':now(),'notice_version':'draft-1'}
  self.store.put('users',u['uid'],r);return r
 def public(self):return public_calls(self.store.all('calls'),self.today())
 def metrics(self,u):
  self.require_admin(u);us=self.store.all('users');return {'registered':len(us),'subscribed':sum(x['subscribed'] for x in us),'calls':len(self.store.all('calls')),'published':len(self.public())}
