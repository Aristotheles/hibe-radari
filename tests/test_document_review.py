import unittest
from unittest.mock import Mock
from hibe.document_review import prepare_proposal
from hibe.store import MemoryStore
from hibe.llm import UnavailableExtractor


class DocumentReviewTests(unittest.TestCase):
    def setUp(self):
        self.store = MemoryStore()
        self.call = {'id':'c','source_id':'s','title':'Original','approval':{'reviewed':True}}
        self.store.put('calls','c',self.call)
        self.docs = [{'url':'https://official.example/c','text':'Teachers may apply individually.'}]

    def prepare(self, extractor):
        return prepare_proposal(self.store,'c',self.docs,extractor,{},['official.example'])

    def test_failure_preserves_previous_proposal_and_call(self):
        old={'id':'c','draft':{'summary':'Correct previous summary'}}
        self.store.put('review_proposals','c',old)
        self.assertEqual(self.prepare(UnavailableExtractor())['status'],'unavailable')
        self.assertEqual(self.store.get('calls','c'),self.call)
        self.assertEqual(self.store.get('review_proposals','c'),old)

    def test_untrusted_quote_does_not_become_eligibility(self):
        class Extractor:
            def extract(_, text, source, profile):
                return {'id':'c','source_id':'s','title':'Extracted','summary':'Own summary',
                    'themes':[],'deadline':None,'official_status':'bilinmiyor',
                    'documents':source['documents'],'approval':{'reviewed':True},
                    'paths':[{'role':'ogretmen_birey','conditions':[{'text':'Country',
                      'result':'saglandi','evidence':'Turkey is eligible for this grant.'}]}]}
        result=self.prepare(Extractor())
        self.assertEqual(result['draft']['paths'][0]['conditions'][0]['result'],'bilinmiyor')
        self.assertNotIn('approval',result['draft'])
        self.assertFalse(result['publication_approved'])
        self.assertEqual(self.store.get('calls','c'),self.call)

    def test_changed_call_during_extraction_discards_proposal(self):
        store=self.store
        class Extractor:
            def extract(_,text,source,profile):
                store.put('calls','c',{'id':'c','title':'New version','source_id':'s'})
                return {'id':'c','source_id':'s','title':'Extracted','summary':'Summary',
                    'themes':[],'deadline':None,'official_status':'bilinmiyor',
                    'documents':source['documents'],'paths':[{'role':'belirsiz','conditions':[]}]}
        self.assertEqual(self.prepare(Extractor())['status'],'stale')
        self.assertIsNone(self.store.get('review_proposals','c'))

    def test_other_host_is_rejected_before_extraction(self):
        self.docs[0]['url']='https://other.example/c'
        with self.assertRaises(ValueError):
            self.prepare(UnavailableExtractor())

    def extractor(self):
        return Mock(model='test-model', extract=Mock(return_value={
            'id':'c','source_id':'s','title':'Extracted','summary':'Summary',
            'themes':[],'deadline':None,'official_status':'bilinmiyor',
            'documents':[{'url':'https://official.example/c','hash':'placeholder'}],
            'paths':[{'role':'belirsiz','conditions':[]}]}))

    def test_unchanged_inputs_reuse_proposal_without_model_call(self):
        extractor = self.extractor()
        self.prepare(extractor)
        self.assertTrue(self.prepare(extractor)['cached'])
        self.assertEqual(extractor.extract.call_count, 1)
        self.assertEqual(self.store.get('calls','c'), self.call)

    def test_document_model_and_call_changes_require_new_extraction(self):
        extractor = self.extractor()
        self.prepare(extractor)
        self.docs[0]['text'] += ' New conditions.'
        self.prepare(extractor)
        extractor.model = 'new-model'
        self.prepare(extractor)
        self.call['title'] = 'Updated'
        self.store.put('calls','c',self.call)
        self.prepare(extractor)
        self.assertEqual(extractor.extract.call_count, 4)

    def test_profile_change_requires_new_extraction(self):
        extractor = self.extractor()
        self.prepare(extractor)
        prepare_proposal(self.store,'c',self.docs,extractor,{'country':'TR'},['official.example'])
        self.assertEqual(extractor.extract.call_count, 2)
