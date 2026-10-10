from datetime import date,datetime,timezone
from pathlib import Path
import json
from .domain import *
def now():return datetime.now(timezone.utc).isoformat()
class Service:
 def __init__(self,store,admin_uid,today=today_istanbul,approvals=None,demo=False):self.store=store;self.admin_uid=admin_uid;self.today=today;self.approvals=approvals;self.demo=demo
 def is_admin(self,u):return bool(self.admin_uid and u.get('uid')==self.admin_uid and u.get('email_verified') is True)
 def require_admin(self,u):
  if not self.is_admin(u):raise PermissionError('Yönetici yetkisi gerekli')
 def save(self,u,c):
  self.require_admin(u);c=dict(c)
  c.pop('auto_review',None)  # Derived queue hints are not editable call evidence.
  if self.demo:c['demo']=True
  validate(c)
  old=self.store.get('calls',c['id'])
  if old and old.get('demo'):c['demo']=True
  if old and old.get('from_aggregator'):
   if c.get('discovery_version')!=old['discovery_version']:raise ValueError('Keşif değişti; güncel kaydı yeniden inceleyin')
   c=dict(c,from_aggregator=True,reviewed_discovery_version=old['discovery_version'],discovery_changes_pending=False)
   c['description_short']=c['summary']
   if c.get('official_url_verified'):c['original_url']=c.get('official_url')
   from .eligibility import assess
   c['eligibility_assessment']=assess(c,self.today())
  c={k:v for k,v in c.items() if k not in {'approval','version'}};c['version']=version(c);self.store.put('calls',c['id'],c);return c
 def approve(self,u,i,v):
  self.require_admin(u);c=self.store.get('calls',i)
  if not c or version(c)!=v:raise ValueError('İçerik değişti; yeniden inceleyin')
  from .aggregator.bridge import review_ready
  if not review_ready(c):raise ValueError('Güncel keşif, özgün özet ve resmî URL incelemesi tamamlanmalı')
  if self.demo and not c.get('demo'):raise ValueError('Demo incelemesi için kaydı DEMO olarak yeniden kaydedin')
  c['approval']={'reviewed':True,'version':v,'uid':u['uid'],'at':now(),'demo':self.demo};self.store.put('calls',i,c)
  if self.approvals:
   p=Path(self.approvals);p.mkdir(exist_ok=True);(p/(i+'.json')).write_text(json.dumps(c['approval'],indent=2))
  return c
 def sources(self,config):
  settings_by_id={x['id']:x for x in self.store.all('source_settings')}
  health_by_id={x['id']:x for x in self.store.all('source_health')}
  result=[]
  for raw in config:
   row=dict(raw);settings=settings_by_id.get(row['id'],{})
   row['enabled']=settings.get('enabled',row.get('enabled',True))
   row['health']=[health_by_id[i] for i in row.get('connector_ids',[]) if i in health_by_id]
   row['alert']=any(h.get('health') not in ('success','disabled') for h in row['health'])
   if row['health']:
    row['last_success']=max((h.get('last_success') or '' for h in row['health']),default='') or None
    row['last_error']=[h.get('last_error') for h in row['health'] if h.get('last_error')]
    row['last_found_count']=sum(h.get('last_found_count') or 0 for h in row['health'])
    row['change_tracking']={'changed_count':sum(h.get('changed_count') or 0 for h in row['health'])}
   result.append(row)
  return result
 def set_source(self,u,ident,enabled,config):
  self.require_admin(u)
  source=next((s for s in config if s['id']==ident),None)
  if source is None or not isinstance(enabled,bool):raise ValueError('Kaynak veya açık/kapalı değeri geçersiz')
  if enabled and source.get('identity_status')=='missing':raise ValueError('Eksik kaynak kimliği açılamaz')
  value={'id':ident,'enabled':enabled,'connector_ids':source.get('connector_ids',[]),'updated_at':now(),'updated_by':u['uid']}
  self.store.put('source_settings',ident,value);return value
 def revoke(self,u,i):
  self.require_admin(u);c=self.store.get('calls',i)
  if not c:raise ValueError('Çağrı bulunamadı')
  c.pop('approval',None);self.store.put('calls',i,c);return c
 def preferences(self,u,d):
  if not u.get('uid') or u.get('email_verified') is not True:raise PermissionError('Doğrulanmış giriş gerekli')
  if not isinstance(d.get('subscribed'),bool) or not isinstance(d.get('themes'),list) or any(t not in THEMES for t in d['themes']):raise ValueError('Tercihler geçersiz')
  old=self.store.get('users',u['uid']) or {}
  r={'uid':u['uid'],'email':u['email'],'themes':list(set(d['themes'])),'subscribed':d['subscribed'],'tier':old.get('tier','free'),'created_at':old.get('created_at',now()),'updated_at':now(),'notice_version':'draft-1'}
  for key in ('membership_status','pro_expires_at'):
   if key in old:r[key]=old[key]
  self.store.put('users',u['uid'],r);return r
 def entitlements(self,u):
  if not u.get('uid') or u.get('email_verified') is not True:raise PermissionError('Doğrulanmış giriş gerekli')
  record=self.store.get('users',u['uid']) or {};pro=record.get('tier')=='pro' and record.get('membership_status')=='active'
  expires=record.get('pro_expires_at')
  if expires:
   try:
    expiry=datetime.fromisoformat(expires.replace('Z','+00:00'))
    pro=pro and expiry.tzinfo is not None and expiry>datetime.now(timezone.utc)
   except (ValueError,TypeError,AttributeError):pro=False
  return {'tier':'pro' if pro else 'free','features':{'browse':True,'calendar':True,'newsletter_preferences':True,'csv_export':pro},'payments_enabled':False}
 def export_csv(self,u):
  if not self.entitlements(u)['features']['csv_export']:raise PermissionError('Bu özellik için etkin Pro üyeliği gerekli')
  import csv,io
  stream=io.StringIO(newline='');writer=csv.writer(stream);writer.writerow(['Başlık','Son başvuru','Durum','Kaynak','DEMO'])
  def safe(value):
   value=str(value or '')
   return "'"+value if value.lstrip().startswith(('=','+','-','@')) or value.startswith(('\t','\r','\n')) else value
  for c in self.public():writer.writerow([safe(c['title']),c['deadline'] or 'Bilinmiyor',c['official_status'],safe(' | '.join(c['urls'])),'DEMO' if c.get('demo') else ''])
  return '\ufeff'+stream.getvalue()
 def public(self):return public_calls([c for c in self.store.all('calls') if self.demo or not (c.get('demo') or c.get('approval',{}).get('demo'))],self.today())
 def pending(self):
  from .pending_opportunities import pending_opportunities
  return pending_opportunities(self.store,self.today())
 def metrics(self,u):
  self.require_admin(u);us=self.store.all('users');return {'registered':len(us),'subscribed':sum(x.get('subscribed',False) is True for x in us),'calls':len(self.store.all('calls')),'published':len(self.public())}
