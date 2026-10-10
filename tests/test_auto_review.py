import unittest
from copy import deepcopy
from datetime import date
from hibe.auto_review import classify, review_queue


class AutoReviewTests(unittest.TestCase):
    def test_news_and_call_are_not_confused(self):
        self.assertEqual(classify({'title':'Okul ziyareti gerçekleştirildi'},date(2026,10,10))['group'],'news')
        self.assertEqual(classify({'title':'Öğretmen yarışması başvuruları ve önceki yıl sonuçları'},date(2026,10,10))['group'],'candidate')

    def test_past_deadline_and_inferred_deadline_differ(self):
        c={'title':'Lise yarışması','deadline':'2025-10-01'}
        self.assertEqual(classify(c,date(2026,10,10))['group'],'expired')
        self.assertEqual(classify(dict(c,deadline_year_inferred=True),date(2026,10,10))['group'],'candidate')

    def test_turkey_keyword_does_not_prove_eligibility(self):
        c={'title':'Türkiye öğretmen hibe başvurusu'}
        r=classify(c,date(2026,10,10))
        self.assertEqual(r['turkey'],'belirsiz')
        self.assertEqual(r['type'],'grant')
        self.assertIn('ogretmen',r['audience_hints'])
        self.assertFalse(r['publication_approved'])

    def test_queue_does_not_modify_approval_or_source_data(self):
        c={'id':'old','title':'School grant','approval':{'reviewed':True,'version':'old'}}
        old=deepcopy(c)
        result=review_queue([c],date(2026,10,10))
        self.assertEqual(c,old)
        self.assertEqual(result[0]['approval'],old['approval'])
        self.assertNotIn('auto_review',c)

    def test_client_triage_is_not_saved_as_evidence(self):
        from hibe.service import Service
        from hibe.store import MemoryStore
        store=MemoryStore()
        c={'id':'c','title':'Call','summary':'Summary','source_id':'s','themes':[],
           'deadline':None,'official_status':'bilinmiyor',
           'documents':[{'url':'https://example.org/c','hash':'actual-test-fixture'}],
           'paths':[{'role':'belirsiz','conditions':[]}],
           'auto_review':{'turkey':'uygun','publication_approved':True}}
        Service(store,'admin').save({'uid':'admin','email_verified':True},c)
        saved=store.get('calls','c')
        self.assertNotIn('auto_review',saved)
        self.assertNotIn('approval',saved)
