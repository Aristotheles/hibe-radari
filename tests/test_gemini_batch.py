import json
import unittest
from unittest.mock import Mock
from hibe.gemini_batch import GeminiBatch, request_payload
from hibe.store import MemoryStore
from hibe.domain import version


class GeminiBatchTests(unittest.TestCase):
    def test_incomplete_section_coverage_cannot_create_review_proposal(self):
        item=dict(self.item,text='A'*24000+' Only university graduates may apply.',sections=['A'*24000,' Only university graduates may apply.'])
        job=self.api.submit(self.store,[item],'2026-10-10')
        draft=dict(self.call,reviewed_sections=[1])
        self.api.api.return_value={'state':'JOB_STATE_SUCCEEDED','dest':{'inlinedResponses':[
            {'metadata':{'key':'c'},'response':{'candidates':[{'content':{'parts':[{'text':json.dumps(draft)}]}}]}}]}}
        result=self.api.poll(self.store,job['id'])
        self.assertEqual(result['results'][0]['status'],'invalid_response')
        self.assertIsNone(self.store.get('review_proposals','c'))
    def setUp(self):
        self.store=MemoryStore()
        self.call={'id':'c','source_id':'s','title':'Lise yarışması','summary':'','documents':[],
                   'themes':[],'deadline':None,'official_status':'bilinmiyor','paths':[]}
        self.store.put('calls','c',self.call)
        self.item={'id':'c','title':self.call['title'],'baseline':version(self.call),
            'text':'Secondary school students from all countries may apply.',
            'documents':[{'url':'https://example.org/call','hash':'abc'}],
            'document_texts':[{'url':'https://example.org/call','text':'Secondary school students from all countries may apply.'}]}
        self.api=GeminiBatch(key='test-key')
        self.api.api=Mock(return_value={'name':'batches/test'})

    def test_submit_once_and_preserve_ambiguous_submission(self):
        job=self.api.submit(self.store,[self.item],'2026-10-10')
        self.assertEqual(self.api.submit(self.store,[self.item],'2026-10-10'),job)
        self.assertEqual(self.api.api.call_count,1)
        self.api.api.side_effect=TimeoutError()
        item=dict(self.item,baseline='changed')
        with self.assertRaises(TimeoutError):self.api.submit(self.store,[item],'2026-10-10')
        result=self.api.submit(self.store,[item],'2026-10-10')
        self.assertEqual(result['status'],'submission_uncertain')
        self.assertEqual(self.api.api.call_count,2)

    def test_result_is_proposal_not_approval_and_unquoted_condition_is_unknown(self):
        job=self.api.submit(self.store,[self.item],'2026-10-10')
        draft=dict(self.call,summary='Lise öğrencileri için yarışma',approval={'reviewed':True},
            paths=[{'role':'ogrenci_birey','conditions':[{'text':'Öğrenci','result':'saglandi','evidence':'fabricated condition'}]}])
        self.api.api.return_value={'metadata':{'state':'JOB_STATE_SUCCEEDED'},'response':{
            'inlinedResponses':{'inlinedResponses':[{'metadata':{'key':'c'},'response':{
                'candidates':[{'content':{'parts':[{'text':json.dumps(draft)}]}}],
                'usageMetadata':{'totalTokenCount':20}}}]}}}
        result=self.api.poll(self.store,job['id'])
        self.assertEqual(result['status'],'completed')
        proposal=self.store.get('review_proposals','c')
        self.assertFalse(proposal['publication_approved'])
        self.assertNotIn('approval',proposal['draft'])
        self.assertEqual(proposal['draft']['paths'][0]['conditions'][0]['result'],'bilinmiyor')
        self.assertEqual(self.store.get('calls','c'),self.call)

    def test_stale_and_foreign_output_cannot_change_call(self):
        job=self.api.submit(self.store,[self.item],'2026-10-10')
        self.store.put('calls','c',dict(self.call,title='Updated'))
        self.api.api.return_value={'state':'JOB_STATE_SUCCEEDED','dest':{'inlinedResponses':[
            {'metadata':{'key':'c'},'response':{}}]}}
        self.assertEqual(self.api.poll(self.store,job['id'])['results'][0]['status'],'stale')
        self.api.api.return_value['dest']['inlinedResponses'][0]['metadata']['key']='foreign'
        with self.assertRaises(ValueError):self.api.poll(self.store,job['id'])

    def test_limit_and_no_silent_truncation(self):
        with self.assertRaises(ValueError):request_payload('a'*48001,'Title','2026-10-10')
        with self.assertRaises(ValueError):self.api.submit(self.store,[self.item,self.item],'2026-10-10')

    def test_rest_state_and_empty_closed_paths_are_valid_proposals(self):
        job=self.api.submit(self.store,[self.item],'2026-10-10')
        draft=dict(self.call,paths=[],official_status='kapandi',deadline='2025-11-30')
        item=self.store.get('ai_batch_inputs',job['id']+'-c');item['text']='Applications closed on 30 November 2025.';self.store.put('ai_batch_inputs',job['id']+'-c',item)
        self.api.api.return_value={'metadata':{'state':'BATCH_STATE_SUCCEEDED'},'response':{'inlinedResponses':{'inlinedResponses':[
            {'metadata':{'key':'c'},'response':{'candidates':[{'content':{'parts':[{'text':json.dumps(draft)}]}}]}}]}}}
        result=self.api.poll(self.store,job['id'])
        self.assertEqual(result['results'][0]['status'],'evidence_review_required')
        self.assertEqual(self.store.get('review_proposals','c')['draft']['official_status'],'kapandi')
