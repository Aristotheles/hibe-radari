import unittest
from datetime import date
from hibe.domain import *
from hibe.store import MemoryStore
from hibe.service import Service
from hibe.demo import seed
from hibe.scan import parse_listing,fetch
from hibe.llm import FakeExtractor
class CoreTests(unittest.TestCase):
 def setUp(self):
  self.db=MemoryStore();seed(self.db);self.s=Service(self.db,'admin',today=lambda:date(2026,10,9));self.admin={'uid':'admin','email':'senoltemur@gmail.com','email_verified':True};self.user={'uid':'user','email':'u@example.org','email_verified':True};self.c=self.db.get('calls','demo-cevre')
 def test_three_values(self):
  p={'conditions':[]};self.assertEqual(eligibility(p),'belirsiz');p['conditions']=[{'result':'saglandi','evidence':'s1'}];self.assertEqual(eligibility(p),'uygun');p['conditions'].append({'result':'bilinmiyor'});self.assertEqual(eligibility(p),'belirsiz');p['conditions'].append({'result':'saglanmadi'});self.assertEqual(eligibility(p),'uygun_degil')
 def test_stale_approval(self):
  self.s.approve(self.admin,self.c['id'],version(self.c));self.assertEqual(len(self.s.public()),2);self.c['title']='Değişti';self.s.save(self.admin,self.c);self.assertEqual(len(self.s.public()),1)
 def test_stale_screen(self):
  old=version(self.c);self.c['deadline']='2026-12-01';self.s.save(self.admin,self.c)
  with self.assertRaises(ValueError):self.s.approve(self.admin,self.c['id'],old)
 def test_user_cannot_admin(self):
  with self.assertRaises(PermissionError):self.s.approve(self.user,self.c['id'],version(self.c))
 def test_email_not_authority(self):self.assertFalse(self.s.is_admin(dict(self.admin,uid='other')))
 def test_unverified_admin(self):self.assertFalse(self.s.is_admin(dict(self.admin,email_verified=False)))
 def test_budget_null_zero(self):
  self.c['budget_max']=0;validate(self.c);self.c['budget_max']=None;validate(self.c);self.c['budget_max']=-1
  with self.assertRaises(ValueError):validate(self.c)
 def test_date_only(self):
  self.c['deadline']='2026-10-09';validate(self.c);self.assertEqual(calendar_status(self.c,date(2026,10,9)),'acik');self.assertEqual(calendar_status(self.c,date(2026,10,10)),'kapandi')
 def test_score_boundaries(self):
  p=self.c['paths'][0];self.c['deadline']='2026-10-23';self.assertEqual(rank(self.c,p,date(2026,10,9))['time'],25);self.c['deadline']='2026-10-22';self.assertTrue(rank(self.c,p,date(2026,10,9))['urgent']);self.c['deadline']='2026-10-08';self.assertIsNone(rank(self.c,p,date(2026,10,9)))
 def test_subscribe_optout_tier(self):
  r=self.s.preferences(self.user,{'subscribed':True,'themes':['bilim'],'tier':'pro'});self.assertEqual(r['tier'],'free');r=self.s.preferences(self.user,{'subscribed':False,'themes':[]});self.assertFalse(r['subscribed'])
 def test_empty_parser(self):
  with self.assertRaises(ValueError):parse_listing('marker','marker',[])
  self.assertEqual(parse_listing('marker boş','marker',[],'boş')['status'],'empty_confirmed')
 def test_ssrf(self):
  for u in ['http://127.0.0.1','https://evil.org','https://user:pass@example.org']:
   with self.assertRaises(ValueError):fetch(u,['example.org'])
 def test_official_status(self):
  c=self.db.get('calls','demo-bilim');c['official_status']='askida';c['approval']['version']=version(c);self.assertFalse(publishable(c,date(2026,10,9)))
 def test_fake_llm_offline(self):validate(FakeExtractor().extract('test',{'id':'demo','call_id':'test','documents':self.c['documents']},{}))
