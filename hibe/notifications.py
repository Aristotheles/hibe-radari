"""Haftalık bülten outbox'ı; SMTP gönderimi yalnızca açık --send seçimiyle."""
import argparse,base64,hashlib,hmac,json,os,smtplib,ssl,time
from datetime import date
from email.message import EmailMessage
from urllib.parse import quote
from .export import render
from .service import now

def unsubscribe_token(uid,secret,expires=None):
 if len(secret)<32:raise ValueError('UNSUBSCRIBE_SECRET en az 32 karakter olmalı')
 body=base64.urlsafe_b64encode(json.dumps({'uid':uid,'expires':expires or int(time.time())+90*86400},separators=(',',':')).encode()).decode().rstrip('=')
 sig=hmac.new(secret.encode(),body.encode(),hashlib.sha256).hexdigest();return body+'.'+sig

def verify_unsubscribe(token,secret):
 if len(secret)<32:raise ValueError('Çıkış servisi yapılandırılmadı')
 try:
  body,sig=token.split('.');expected=hmac.new(secret.encode(),body.encode(),hashlib.sha256).hexdigest()
  if not hmac.compare_digest(sig,expected):raise ValueError()
  d=json.loads(base64.urlsafe_b64decode(body+'='*(-len(body)%4)))
  if d['expires']<time.time():raise ValueError()
  return d['uid']
 except Exception:raise ValueError('Çıkış bağlantısı geçersiz veya süresi dolmuş') from None

def prepare(service,base_url,secret):
 if not base_url.startswith('https://'):raise ValueError('PUBLIC_BASE_URL HTTPS olmalı')
 week=date.today().strftime('%G-W%V');count=0;calls=service.public()
 for u in service.store.all('users'):
  if u.get('subscribed') is not True:continue
  key=hashlib.sha256((week+u['uid']).encode()).hexdigest();old=service.store.get('outbox',key)
  if old:continue
  selected=[c for c in calls if not u['themes'] or set(c['themes'])&set(u['themes'])]
  link=base_url.rstrip('/')+'/?unsubscribe='+quote(unsubscribe_token(u['uid'],secret))
  text='Hibe Radarı · '+week+'\n\n'+'\n\n'.join(c['title']+'\n'+c['summary'] for c in selected)+'\n\nAbonelikten çık: '+link
  service.store.put('outbox',key,{'id':key,'uid':u['uid'],'week':week,'status':'prepared','subject':'Hibe Radarı · '+week,'text':text,'html':render(selected),'unsubscribe_url':link,'created_at':now()});count+=1
 return count

def send_pending(service):
 if os.environ.get('NEWSLETTER_ENABLED')!='true':raise ValueError('Canlı bülten gönderimi kapalı')
 host=os.environ['SMTP_HOST'];port=int(os.environ.get('SMTP_PORT','587'));sender=os.environ['SMTP_FROM']
 sent=0
 with smtplib.SMTP(host,port,timeout=30) as smtp:
  smtp.starttls(context=ssl.create_default_context())
  if os.environ.get('SMTP_USER'):smtp.login(os.environ['SMTP_USER'],os.environ['SMTP_PASSWORD'])
  for message in service.store.all('outbox'):
   if message['status']!='prepared':continue
   u=service.store.get('users',message['uid'])
   if not u or u.get('subscribed') is not True:message['status']='cancelled';service.store.put('outbox',message['id'],message);continue
   mail=EmailMessage();mail['From']=sender;mail['To']=u['email'];mail['Subject']=message['subject'];mail['Message-ID']='<'+message['id']+'@'+sender.split('@')[-1]+'>';mail.set_content(message['text']);mail.add_alternative(message['html'],'html')
   # Gönderim öncesi işaretle: crash sonrası belirsiz kayıt otomatik tekrar gönderilmez.
   message['status']='sending';service.store.put('outbox',message['id'],message)
   try:smtp.send_message(mail)
   except Exception:message['status']='uncertain';service.store.put('outbox',message['id'],message);raise
   message['status']='sent';message['sent_at']=now();service.store.put('outbox',message['id'],message);sent+=1
 return sent

def main():
 from .server import App
 p=argparse.ArgumentParser();p.add_argument('--firebase',action='store_true');p.add_argument('--send',action='store_true');a=p.parse_args();s=App(demo=not a.firebase).service
 if a.send:print('Gönderilen:',send_pending(s))
 else:print('Hazırlanan:',prepare(s,os.environ['PUBLIC_BASE_URL'],os.environ['UNSUBSCRIBE_SECRET']))
if __name__=='__main__':main()
