import unittest,time
from hibe.notifications import *
from hibe.service import Service
from hibe.store import MemoryStore
class MailTests(unittest.TestCase):
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
