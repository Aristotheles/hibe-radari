from .domain import version
from .service import now

def seed(store):
 if store.all('calls'):return
 for i,title,role,theme in [('demo-bilim','Okul bilim atölyesi','dogrudan','bilim'),('demo-cevre','Yerel çevre ortaklığı','ortak','cevre_su')]:
  c={'id':i,'title':title+' · DEMO','summary':'Kurgusal örnek. Gerçek hibe ilanı değildir.','source_id':'demo','deadline':None,'official_status':'bilinmiyor','budget_max':None,'currency':None,'themes':[theme],'documents':[{'url':'https://example.org','hash':i}],'paths':[{'role':role,'conditions':[{'text':'Kurumsal uygunluk','result':'bilinmiyor','evidence':'Demo belge — kanıt değildir'}]}],'demo':True};c['version']=version(c)
  if i=='demo-bilim':c['approval']={'version':version(c),'reviewed':True,'uid':'demo-admin','at':now()}
  store.put('calls',i,c)
