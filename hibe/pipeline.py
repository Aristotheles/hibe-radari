"""Manuel kaydedilmiş çağrı URL'lerini sıralı tara; yeni çağrı keşfi ayrı adaptör işi."""
import argparse,json,hashlib
from pathlib import Path
from .scan import fetch
from .llm import GeminiExtractor,FakeExtractor,extract_with_fallback,UnavailableExtractor
from .domain import version,validate
from .service import now

def scan_source(source,store,extractor,profile,fetcher=fetch):
 run={'id':hashlib.sha256((source['id']+now()).encode()).hexdigest()[:20],'source_id':source['id'],'at':now(),'status':'pending','changed':0,'errors':[]}
 if source.get('enabled') is False or source.get('status')=='registry_pending' or not source.get('allowed_hosts') or not source.get('call_urls'):
  run['status']='manual_pending';store.put('runs',run['id'],run);return run
 for item in source['call_urls']:
  try:
   # Her çağrı URL'si bağlı PDF listesiyle birlikte açıkça kaydedilir.
   urls=[item['url']]+item.get('documents',[]);texts=[];docs=[]
   for url in urls:
    text,hash_value=fetcher(url,source['allowed_hosts']);texts.append(text);docs.append({'url':url,'hash':hash_value})
   ident=hashlib.sha256(item['url'].encode()).hexdigest()[:24];old=store.get('calls',ident)
   if old and old['documents']==docs and old.get('ai_status')!='unavailable':continue
   # Eski onaylı çağrı, LLM hata verse bile belge değişince geri çekilir.
   if old:
    old['documents']=docs;old.pop('approval',None);old['version']=version(old);store.put('calls',ident,old)
   if source.get('type')=='discovery':
    run['errors'].append('Keşif kaynağı: resmî belge incelemesi gerekli');continue
   c=extract_with_fallback(extractor,'\n\n'.join(texts),{'id':source['id'],'call_id':ident,'documents':docs,'title':item.get('title'),'document_texts':[{'url':d['url'],'text':t} for d,t in zip(docs,texts)]},profile);validate(c)
   if old and c.get('ai_status')=='unavailable':
    old.update(ai_status='unavailable',ai_error_kind=c.get('ai_error_kind'));c=old
   c['version']=version(c);store.put('calls',ident,c);run['changed']+=1
  except Exception as e:run['errors'].append(type(e).__name__+': '+str(e)[:180])
 run['status']='partial' if run['errors'] else 'ok';store.put('runs',run['id'],run);return run

def main():
 p=argparse.ArgumentParser();p.add_argument('--fake',action='store_true');p.add_argument('--firebase',action='store_true');a=p.parse_args()
 from .server import ROOT,App
 app=App(demo=not a.firebase);sources=json.loads((ROOT/'config/sources.json').read_text(encoding='utf-8'));profile=json.loads((ROOT/'config/profile.json').read_text(encoding='utf-8'));extractor=FakeExtractor() if a.fake else None
 if extractor is None:
  try:extractor=GeminiExtractor()
  except ValueError:extractor=UnavailableExtractor()
 settings={r['id']:r for r in app.service.store.all('source_settings')}
 for s in sources:
  current=dict(s,enabled=settings.get(s['id'],{}).get('enabled',s.get('enabled',True)))
  print(json.dumps(scan_source(current,app.service.store,extractor,profile),ensure_ascii=False))
if __name__=='__main__':main()
