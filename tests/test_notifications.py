import unittest,time
from hibe.notifications import *
from hibe.service import Service
from hibe.store import MemoryStore
class MailTests(unittest.TestCase):
 def test_membership_without_explicit_optin_is_skipped(self):
  s=Service(MemoryStore(),'admin')
  for index,subscribed in enumerate((None,'true',1,False)):
   user={'uid':str(index),'tier':'pro','membership_status':'active'}
   if subscribed is not None:user['subscribed']=subscribed
   s.store.put('users',user['uid'],user)
  s.store.put('users','yes',{'uid':'yes','email':'test@example.org','themes':[],'subscribed':True})
  self.assertEqual(prepare(s,'https://example.org','x'*32),1)
  self.assertEqual([m['uid'] for m in s.store.all('outbox')],['yes'])
 def test_missing_optin_cancels_prepared_message_without_sending(self):
  from unittest.mock import patch
  s=Service(MemoryStore(),'admin')
  s.store.put('users','u',{'uid':'u','tier':'pro'})
  s.store.put('outbox','m',{'id':'m','uid':'u','status':'prepared'})
  with patch.dict(os.environ,{'NEWSLETTER_ENABLED':'true','SMTP_HOST':'smtp.example.org','SMTP_FROM':'test@example.org'}),patch('hibe.notifications.smtplib.SMTP') as smtp:
   self.assertEqual(send_pending(s),0)
   smtp.return_value.__enter__.return_value.send_message.assert_not_called()
   context=smtp.return_value.__enter__.return_value.starttls.call_args.kwargs['context']
   self.assertTrue(context.check_hostname)
   self.assertEqual(context.verify_mode,ssl.CERT_REQUIRED)
  self.assertEqual(s.store.get('outbox','m')['status'],'cancelled')
 def test_signature_and_expiry(self):
  secret='x'*32;t=unsubscribe_token('uid',secret);self.assertEqual(verify_unsubscribe(t,secret),'uid')
  with self.assertRaises(ValueError):verify_unsubscribe(t+'a',secret)
  with self.assertRaises(ValueError):verify_unsubscribe(unsubscribe_token('uid',secret,int(time.time())-1),secret)
 def test_week_idempotent_and_optout(self):
  s=Service(MemoryStore(),'admin');s.store.put('users','u',{'uid':'u','email':'x@example.org','themes':[],'subscribed':True})
  self.assertEqual(prepare(s,'https://example.org','x'*32),1);self.assertEqual(prepare(s,'https://example.org','x'*32),0)
  s.store.put('users','v',{'uid':'v','email':'v@example.org','themes':[],'subscribed':False});self.assertEqual(prepare(s,'https://example.org','x'*32),0)
 def test_sending_disabled(self):
  with self.assertRaises(ValueError):send_pending(Service(MemoryStore(),'admin'))
 def test_html_newsletter_contains_same_signed_optout_as_text(self):
  from bs4 import BeautifulSoup
  from urllib.parse import urlsplit,parse_qs
  s=Service(MemoryStore(),'admin');s.store.put('users','u',{'uid':'u','email':'u@example.org','themes':[],'subscribed':True})
  prepare(s,'https://example.org','x'*32);message=s.store.all('outbox')[0]
  link=BeautifulSoup(message['html'],'html.parser').select_one('footer a')
  self.assertEqual(link['href'],message['unsubscribe_url']);self.assertIn(link['href'],message['text'])
  token=parse_qs(urlsplit(link['href']).query)['unsubscribe'][0]
  self.assertEqual(verify_unsubscribe(token,'x'*32),'u')
  unsafe=render([],unsubscribe_url='https://example.org/?x="<script>')
  self.assertNotIn('<script>',unsafe)
  self.assertNotIn('<footer>',render([],unsubscribe_url='javascript:alert(1)'))
 def test_demo_send_fails_before_smtp_connection(self):
  from unittest.mock import patch
  s=Service(MemoryStore(),'admin',demo=True)
  with patch.dict(os.environ,{'NEWSLETTER_ENABLED':'true'}),patch('hibe.notifications.smtplib.SMTP') as smtp:
   with self.assertRaisesRegex(ValueError,'DEMO'):send_pending(s)
   smtp.assert_not_called()
 def test_revoked_changed_and_legacy_prepared_content_is_not_sent(self):
  from unittest.mock import patch
  from hibe.domain import version
  for change in ('revoked','changed','reapproved','legacy','fresh'):
   with self.subTest(change=change):
    s=Service(MemoryStore(),'admin')
    call={'id':'c','title':'Resmî çağrı','summary':'Editör açıklaması','themes':[],'deadline':None,'official_status':'bilinmiyor','documents':[{'url':'https://example.org','hash':'evidence'}],'paths':[]}
    call['approval']={'version':version(call),'reviewed':True};s.store.put('calls','c',call)
    s.store.put('users','u',{'uid':'u','email':'u@example.org','themes':[],'subscribed':True})
    prepare(s,'https://example.org','x'*32)
    message=s.store.all('outbox')[0]
    if change=='revoked':call.pop('approval');s.store.put('calls','c',call)
    if change=='changed':call['summary']='Yeni açıklama';s.store.put('calls','c',call)
    if change=='reapproved':call['summary']='Yeni onaylı açıklama';call['approval']={'version':version(call),'reviewed':True};s.store.put('calls','c',call)
    if change=='legacy':message.pop('call_versions');s.store.put('outbox',message['id'],message)
    with patch.dict(os.environ,{'NEWSLETTER_ENABLED':'true','SMTP_HOST':'smtp.example.org','SMTP_FROM':'sender@example.org'}),patch('hibe.notifications.smtplib.SMTP') as smtp:
     self.assertEqual(send_pending(s),1 if change=='fresh' else 0)
     self.assertEqual(smtp.return_value.__enter__.return_value.send_message.call_count,1 if change=='fresh' else 0)
    self.assertEqual(s.store.get('outbox',message['id'])['status'],'sent' if change=='fresh' else 'stale')
