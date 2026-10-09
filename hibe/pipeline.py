"""Manuel kaydedilmiş çağrı URL'lerini sıralı tara; yeni çağrı keşfi ayrı adaptör işi."""
import argparse,json,hashlib
from pathlib import Path
from .scan import fetch
from .llm import GeminiExtractor,FakeExtractor
from .domain import version,validate
from .service import now

def scan_source(source,store,extractor,profile,fetcher=fetch):
 run={'id':hashlib.sha256((source['id']+now()).encode()).hexdigest()[:20],'source_id':source['id'],'at':now(),'status':'pending','changed':0,'errors':[]}
 if source.get('status')=='registry_pending' or not source.get('allowed_hosts') or not source.get('call_urls'):
  run['status']='manual_pending';store.put('runs',run['id'],run);return run
 for item in source['call_urls']:
  try:
   # Her çağrı URL'si bağlı PDF listesiyle birlikte açıkça kaydedilir.
   urls=[item['url']]+item.get('documents',[]);texts=[];docs=[]
   for url in urls:
    text,hash_value=fetcher(url,source['allowed_hosts']);texts.append(text);docs.append({'url':url,'hash':hash_value})
   ident=hashlib.sha256(item['url'].encode()).hexdigest()[:24];old=store.get('calls',ident)
   if old and old['documents']==docs:continue
   # Eski onaylı çağrı, LLM hata verse bile belge değişince geri çekilir.
   if old:
    old['documents']=docs;old.pop('approval',None);old['version']=version(old);store.put('calls',ident,old)
   if source.get('type')=='discovery':
    run['errors'].append('Keşif kaynağı: resmî belge incelemesi gerekli');continue
   c=extractor.extract('\n\n'.join(texts),{'id':source['id'],'call_id':ident,'documents':docs},profile);validate(c)
   c['version']=version(c);store.put('calls',ident,c);run['changed']+=1
  except Exception as e:run['errors'].append(type(e).__name__+': '+str(e)[:180])
 run['status']='partial' if run['errors'] else 'ok';store.put('runs',run['id'],run);return run

def main():
 p=argparse.ArgumentParser();p.add_argument('--fake',action='store_true');p.add_argument('--firebase',action='store_true');a=p.parse_args()
 from .server import ROOT,App
 app=App(demo=not a.firebase);sources=json.loads((ROOT/'config/sources.json').read_text());profile=json.loads((ROOT/'config/profile.json').read_text());extractor=FakeExtractor() if a.fake else GeminiExtractor()
 for s in sources:print(json.dumps(scan_source(s,app.service.store,extractor,profile),ensure_ascii=False))
if __name__=='__main__':main()
