import unittest,json,httpx
from unittest.mock import patch,Mock
from datetime import date
from hibe.store import MemoryStore
from hibe.domain import version
from hibe.scan import normalized_hash
from hibe.batch_pipeline import submit_candidates
class BatchPipelineTests(unittest.TestCase):
 def test_recovered_document_retires_error_with_history_without_new_model_charge(self):
  from hibe.gemini_batch import POLICY
  store=MemoryStore();body='Teacher conditions.'
  call={'id':'c','title':'Teacher grant','source_id':'s','source_url':'https://example.org/call'}
  docs=[{'url':call['source_url'],'hash':normalized_hash(body)}]
  store.put('calls','c',call)
  store.put('review_document_errors','c',{'id':'c','documents':[{'url':'https://example.org/sidebar.pdf','role':'unknown'}]})
  store.put('ai_batches','b',{'id':'b','policy':POLICY,'status':'completed'})
  store.put('ai_batch_inputs','b-c',{'id':'c','batch_id':'b','baseline':version(call),'documents':docs})
  store.put('review_proposals','c',{'id':'c','batch_id':'b','base_version':version(call),'draft':{'documents':docs}})
  source={'id':'s','type':'source_discovery','review_body_selector':'section.article','allowed_hosts':['example.org'],'access_policy':{'terms_status':'allowed'}}
  response=httpx.Response(200,headers={'content-type':'text/html'},text='<aside><a href="/sidebar.pdf">old</a></aside><section class="article">'+body+'</section>',request=httpx.Request('GET',call['source_url']))
  api=Mock()
  with patch('hibe.batch_pipeline.Fetcher') as fetcher,patch('hibe.batch_pipeline.publish_batch') as publish:
   fetcher.return_value.get.return_value=response
   result=submit_candidates(store,{'sources':[source]},api)
  self.assertEqual(result['status'],'no_new_documents');api.submit.assert_not_called();publish.assert_called_once()
  record=store.get('review_document_errors','c')
  self.assertEqual(record['status'],'resolved');self.assertEqual(record['documents'],[])
  self.assertEqual(len(record['previous_errors']),1)
 def test_new_policy_rechecks_same_document_once(self):
  from hibe.gemini_batch import POLICY
  for policy,expected in [(POLICY-1,True),(POLICY,False)]:
   store=MemoryStore();body='Applications for teacher training are open.'
   docs=[{'url':'https://example.org/call','hash':normalized_hash(body)}]
   c={'id':'c','title':'Teacher grant','source_id':'s','source_url':docs[0]['url']}
   store.put('calls','c',c)
   store.put('review_proposals','c',{'id':'c','batch_id':'b','base_version':version(c),'draft':{'documents':docs}})
   store.put('ai_batches','b',{'id':'b','policy':policy,'status':'completed'})
   store.put('publication_decisions','c',{'id':'c','status':'country_evidence_required'})
   api=Mock();api.submit.return_value={'id':'new'}
   source={'id':'s','type':'source_discovery','allowed_hosts':['example.org'],'access_policy':{'terms_status':'allowed'}}
   response=httpx.Response(200,headers={'content-type':'text/html'},text='<main>'+body+'</main>',request=httpx.Request('GET',docs[0]['url']))
   with patch('hibe.batch_pipeline.Fetcher') as fetcher:
    fetcher.return_value.get.return_value=response
    submit_candidates(store,{'sources':[source]},api)
   self.assertEqual(api.submit.called,expected)
 def test_failed_irrelevant_pdf_does_not_block_but_missing_guideline_does(self):
  for label,expected in [('Privacy policy',True),('Application guidelines',False)]:
   store=MemoryStore();store.put('calls','c',{'id':'c','source_id':'s','title':'Teacher grant','source_url':'https://example.org/call'})
   source={'id':'s','type':'source_discovery','allowed_hosts':['example.org'],'access_policy':{'terms_status':'allowed'}}
   api=Mock();api.submit.return_value={'id':'batch'}
   response=httpx.Response(200,headers={'content-type':'text/html'},text='<main>Applications are open.<a href="/doc.pdf">'+label+'</a></main>',request=httpx.Request('GET','https://example.org/call'))
   with patch('hibe.batch_pipeline.Fetcher') as fetcher:
    fetcher.return_value.get.side_effect=[response,ValueError('PDF unavailable')]
    result=submit_candidates(store,{'sources':[source]},api)
   self.assertEqual(api.submit.called,expected)
   if not expected:self.assertEqual(store.get('review_document_errors','c')['category'],'technical_document_error')
 def test_documented_grants_api_uses_numeric_detail_and_public_url(self):
  store=MemoryStore();url='https://www.grants.gov/search-results-detail/363913'
  store.put('calls','c',{'id':'c','source_id':'s','source_entry_id':'363913','title':'Teacher grant','source_url':url})
  source={'id':'s','type':'grants_gov','allowed_hosts':['api.grants.gov','www.grants.gov'],
   'entry_url_template':'https://www.grants.gov/search-results-detail/{entry_id}',
   'access_policy':{'terms_status':'allowed'}}
  api=Mock();api.submit.return_value={'id':'batch'}
  with patch('hibe.batch_pipeline.Fetcher'),patch('hibe.aggregator.grants_gov.detail_text',return_value='Actual public API evidence.') as detail:
   result=submit_candidates(store,{'sources':[source]},api)
  self.assertEqual(result['submitted'],1);self.assertEqual(result['errors'],[])
  self.assertEqual(detail.call_args.args[2],'363913')
  self.assertEqual(api.submit.call_args.args[1][0]['documents'][0]['url'],url)

 def test_disabled_registry_mapping_does_not_fetch_or_charge(self):
  store=MemoryStore();store.put('source_settings','registry',{'id':'registry','enabled':False,'connector_ids':['s']})
  store.put('calls','c',{'id':'c','source_id':'s','title':'Teacher grant','source_url':'https://example.org/call'})
  api=Mock()
  config={'sources':[{'id':'s','type':'source_discovery','allowed_hosts':['example.org'],'access_policy':{'terms_status':'allowed'}}]}
  with patch('hibe.batch_pipeline.Fetcher') as fetcher:
   result=submit_candidates(store,config,api)
  fetcher.assert_not_called();api.submit.assert_not_called()
  self.assertEqual(result['status'],'no_new_documents')
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
  with patch('hibe.batch_pipeline.Fetcher') as fetcher,patch('hibe.batch_pipeline.document_text',return_value=body):
   fetcher.return_value.get.return_value=httpx.Response(200,headers={'content-type':'text/html'},text='<main>Evidence</main>',request=httpx.Request('GET','https://example.org/call'))
   result=submit_candidates(s,config,api)
  api.submit.assert_not_called()
  self.assertEqual(result['status'],'no_new_documents')
  self.assertEqual(s.get('calls','c')['approval']['authority'],'verified_ai_batch_review')
  self.assertEqual(s.get('calls','c')['reviewed_discovery_version'],'a'*64)
