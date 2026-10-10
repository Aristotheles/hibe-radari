import unittest,json
from unittest.mock import patch,Mock
from datetime import date
from hibe.store import MemoryStore
from hibe.domain import version
from hibe.scan import normalized_hash
from hibe.batch_pipeline import submit_candidates
class BatchPipelineTests(unittest.TestCase):
 def test_metadata_rediscovery_reuses_identical_grounded_proposal_without_model(self):
  s=MemoryStore();body='Teachers in Turkey may apply. Secondary school teachers are eligible. Application deadline: 30 November 2026.'
  docs=[{'url':'https://example.org/call','hash':normalized_hash(body)}]
  c={'id':'c','title':'Teacher training','source_id':'s','source_url':docs[0]['url'],'summary':'','deadline':None,'themes':[],'official_status':'bilinmiyor','documents':docs,'paths':[],'discovery_changes_pending':True,'discovery_version':'a'*64,'from_aggregator':True,'official_source_verified':True}
  s.put('calls','c',c)
  draft=dict(c,summary='Teacher training in Turkey',deadline='2026-11-30',deadline_evidence='Application deadline: 30 November 2026.',official_status='acik',paths=[{'role':'ogretmen_birey','conditions':[{'text':'Teacher','result':'saglandi','evidence':'Secondary school teachers are eligible.'}]}],country_scope={'result':'eligible','evidence':'Teachers in Turkey may apply.'},target_scope={'result':'eligible','evidence':'Secondary school teachers are eligible.','targets':['teacher']})
  s.put('review_proposals','c',{'id':'c','batch_id':'b','base_version':'old','draft':draft})
  s.put('ai_batches','b',{'id':'b','status':'completed','model':'gemini-3.8-flash'})
  s.put('ai_batch_inputs','b-c',{'id':'c','batch_id':'b','text':body,'documents':docs,'document_texts':[{'url':docs[0]['url'],'text':body}]})
  config={'sources':[{'id':'s','allowed_hosts':['example.org'],'access_policy':{'terms_status':'allowed'}}]}
  api=Mock()
  with patch('hibe.batch_pipeline.Fetcher'),patch('hibe.batch_pipeline.document_text',return_value=body):
   result=submit_candidates(s,config,api)
  api.submit.assert_not_called()
  self.assertEqual(result['status'],'no_new_documents')
  self.assertEqual(s.get('calls','c')['approval']['authority'],'verified_ai_batch_review')
  self.assertEqual(s.get('calls','c')['reviewed_discovery_version'],'a'*64)
