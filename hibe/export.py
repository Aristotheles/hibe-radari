"""İnsan onaylı çağrılardan indekslenebilir statik HTML + bülten önizlemesi."""
import argparse,json,html
from pathlib import Path
from .server import App,ROOT

def render(calls):
 cards=[]
 for c in calls:
  e=html.escape;links=' '.join('<a href="'+e(u,quote=True)+'">Kaynak</a>' for u in c['urls'] if u.startswith('https://'))
  cards.append('<article><h2>'+e(c['title'])+'</h2><p>'+e(c['summary'])+'</p><p>Son tarih: '+e(c['deadline'] or 'Bilinmiyor')+'</p>'+links+'</article>')
 return '<!doctype html><html lang="tr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Hibe Radarı — Haftalık fırsatlar</title><style>body{max-width:900px;margin:40px auto;padding:20px;font-family:system-ui;background:#f5f6f0;color:#14382f}article{padding:24px;background:white;border:1px solid #dfe5da;margin:20px 0;border-radius:12px}</style><h1>Hibe Radarı</h1><p>İnsan onaylı fırsatlar. Başvuru koşullarını resmî kaynaktan kontrol edin.</p>'+''.join(cards)+'</html>'
def main():
 p=argparse.ArgumentParser();p.add_argument('--firebase',action='store_true');p.add_argument('--out',default='data/export');a=p.parse_args();calls=App(demo=not a.firebase).service.public();out=Path(a.out);out.mkdir(parents=True,exist_ok=True);(out/'index.html').write_text(render(calls));(out/'calls.json').write_text(json.dumps(calls,ensure_ascii=False,indent=2));print('Statik HTML ve JSON üretildi; e-posta gönderilmedi.')
if __name__=='__main__':main()
