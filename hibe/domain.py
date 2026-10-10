from datetime import date
import hashlib,json,re
THEMES={'engelli_kapsayicilik':3,'cevre_su':3,'bilim':2,'dil_kultur':2,'dijital':1}
ROLES={'dogrudan':40,'ortak':25,'ogretmen_birey':40,'uygulama_yeri':15,'belirsiz':10}
def version(c):
 return hashlib.sha256(json.dumps({k:v for k,v in c.items() if k not in {'approval','version'}},sort_keys=True,ensure_ascii=False).encode()).hexdigest()
def eligibility(p):
 cs=p.get('conditions',[])
 if not cs:return 'belirsiz'
 if any(c['result']=='saglanmadi' and c.get('evidence') for c in cs):return 'uygun_degil'
 if any(c['result']=='bilinmiyor' or not c.get('evidence') for c in cs):return 'belirsiz'
 return 'uygun'
def validate(c):
 for k in ('id','title','summary','source_id','documents','paths','themes','deadline','official_status'):
  if k not in c:raise ValueError('Eksik alan: '+k)
 if not isinstance(c['id'],str) or not re.fullmatch(r'[a-zA-Z0-9_-]{1,100}',c['id']):raise ValueError('Geçersiz kimlik')
 if not isinstance(c['title'],str) or not c['title'].strip():raise ValueError('Başlık gerekli')
 if c['deadline'] is not None:date.fromisoformat(c['deadline'])
 b=c.get('budget_max')
 if b is not None and (isinstance(b,bool) or not isinstance(b,(float,int)) or b<0):raise ValueError('Bütçe geçersiz')
 if c['official_status'] not in {'acik','kapandi','askida','bilinmiyor'}:raise ValueError('Durum geçersiz')
 if not isinstance(c['themes'],list) or any(t not in THEMES for t in c['themes']):raise ValueError('Tema geçersiz')
 if not isinstance(c['documents'],list) or not c['documents']:raise ValueError('Belge gerekli')
 for d in c['documents']:
  if not all(isinstance(d.get(k),str) and d[k] for k in ('url','hash')):raise ValueError('Belge URL/hash gerekli')
 if not isinstance(c['paths'],list) or not c['paths']:raise ValueError('Başvuru yolu gerekli')
 for p in c['paths']:
  if p.get('role') not in ROLES or not isinstance(p.get('conditions'),list):raise ValueError('Yol geçersiz')
  for x in p['conditions']:
   if x.get('result') not in {'saglandi','saglanmadi','bilinmiyor'} or not isinstance(x.get('text'),str):raise ValueError('Koşul geçersiz')
 return c
def calendar_status(c,today):
 return 'kapandi' if c['deadline'] and date.fromisoformat(c['deadline'])<today else 'acik' if c['deadline'] else 'bilinmiyor'
def publishable(c,today):
 if c.get('from_aggregator'):
  from .aggregator.bridge import review_ready
  if not review_ready(c):return False
 a=c.get('approval',{})
 return a.get('version')==version(c) and a.get('reviewed') is True and c['official_status'] not in {'kapandi','askida'} and calendar_status(c,today)!='kapandi'
def rank(c,p,today):
 if eligibility(p)=='uygun_degil':return None
 days=(date.fromisoformat(c['deadline'])-today).days if c['deadline'] else None
 if days is not None and days<0:return None
 tm=5 if days is None else 15 if days<14 else 25 if days<=90 else 10
 th=min(35,sum(THEMES[t] for t in set(c['themes']))*5)
 return {'total':ROLES[p['role']]+th+tm,'urgent':days is not None and days<14,'time':tm}
def public_calls(calls,today):
 out=[]
 for c in calls:
  if publishable(c,today):
   d={k:c.get(k) for k in ('id','title','summary','themes','deadline','official_status','budget_max','currency','demo','source_id','source_url','organization','deadline_precision','deadline_evidence','deadline_checked_at','eligibility_assessment')}
   d['last_checked']=c.get('last_verified_at') or c.get('approval',{}).get('at')
   d['version']=version(c)
   d['paths']=[dict(p,eligibility=eligibility(p),ranking=rank(c,p,today)) for p in c['paths']]
   d['urls']=[d['url'] for d in c['documents']];out.append(d)
 return out
