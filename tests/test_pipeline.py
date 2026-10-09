import unittest
from hibe.pipeline import scan_source
from hibe.store import MemoryStore
from hibe.llm import FakeExtractor
from hibe.domain import version
from hibe.export import render
class PipelineTests(unittest.TestCase):
 def setUp(self):self.db=MemoryStore();self.source={'id':'s','status':'ready','type':'official','allowed_hosts':['example.org'],'call_urls':[{'url':'https://example.org/call','documents':['https://example.org/doc.pdf']}]}
 def test_unknown_source_not_success(self):
  r=scan_source({'id':'s','status':'registry_pending'},self.db,FakeExtractor(),{});self.assertEqual(r['status'],'manual_pending')
 def test_skip_unchanged_and_invalidate_pdf(self):
  def fetch(u,a):return 'text','hash1'
  r=scan_source(self.source,self.db,FakeExtractor(),{},fetch);self.assertEqual(r['changed'],1)
  c=self.db.all('calls')[0];c['approval']={'reviewed':True,'version':version(c)};self.db.put('calls',c['id'],c)
  self.assertEqual(scan_source(self.source,self.db,FakeExtractor(),{},fetch)['changed'],0)
  class Failing:
   def extract(self,*a):raise ValueError('LLM failed')
  scan_source(self.source,self.db,Failing(),{},lambda u,a:('text','hash2' if u.endswith('pdf') else 'hash1'))
  self.assertNotIn('approval',self.db.get('calls',c['id']));self.assertEqual(self.db.get('calls',c['id'])['title'],c['title']);self.assertEqual(self.db.get('calls',c['id'])['ai_status'],'unavailable')
 def test_discovery_no_llm(self):
  self.source['type']='discovery';scan_source(self.source,self.db,FakeExtractor(),{},lambda u,a:('text','hash'));self.assertEqual(self.db.all('calls'),[])
 def test_export_escapes(self):
  s=render([{'title':'<script>bad</script>','summary':'test','deadline':None,'urls':['javascript:bad']}]);self.assertNotIn('<script>',s);self.assertNotIn('javascript:',s)
