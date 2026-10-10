import copy
import unittest
from datetime import date
from hibe.batch_publication import publication_decision, publish_batch
from hibe.domain import version, publishable
from hibe.store import MemoryStore


class BatchPublicationTests(unittest.TestCase):
    def setUp(self):
        self.today=date(2026,10,10)
        self.text='Teachers in Turkey may apply. Secondary school teachers are eligible. Application deadline: 30 November 2026.'
        self.current={'id':'c','title':'Teacher training','source_id':'official', 'source_url':'https://example.org/call',
            'official_source_verified':True,'summary':'','deadline':None,'official_status':'bilinmiyor','themes':[],
            'paths':[],'documents':[],'from_aggregator':True,'discovery_version':'a'*64}
        self.draft={'id':'c','source_id':'official','title':'Öğretmen eğitimi','summary':'Türkiye’den lise öğretmenleri başvurabilir.',
            'deadline':'2026-11-30','deadline_evidence':'Application deadline: 30 November 2026.', 'official_status':'acik',
            'themes':['bilim'],'documents':[{'url':'https://example.org/call','hash':'abc'}],
            'country_scope':{'result':'eligible','evidence':'Teachers in Turkey may apply.'},
            'target_scope':{'result':'eligible','evidence':'Secondary school teachers are eligible.','targets':['teacher']},
            'paths':[{'role':'ogretmen_birey','conditions':[{'text':'Öğretmen','result':'saglandi','evidence':'Secondary school teachers are eligible.'},
                {'text':'Kişisel başvuru belgeleri','result':'bilinmiyor','evidence':None}]}]}
        self.item={'text':self.text,'documents':self.draft['documents'],'document_texts':[{'url':'https://example.org/call','text':self.text}]}

    def test_personal_unknown_does_not_erase_verified_audience(self):
        self.assertEqual(publication_decision(self.current,self.draft,self.item,self.today),'eligible')

    def test_official_school_letter_and_public_employee_path_have_real_context(self):
        draft=copy.deepcopy(self.draft);draft['country_scope']['evidence']='T.C. Millî Eğitim Bakanlığı'
        text=self.text+' T.C. Millî Eğitim Bakanlığı iş birliği kapsamında yürütülen program: katılmak isteyen öğretmenlerin okullara gönderilen resmî yazı üzerinden başvurması gerekir.'
        current=dict(self.current,source_url='https://ogm.meb.gov.tr/call')
        self.assertEqual(publication_decision(current,draft,dict(self.item,text=text),self.today),'eligible')
        self.assertEqual(publication_decision(current,draft,dict(self.item,text=text.replace('okullara gönderilen','basında görülen')),self.today),'country_evidence_required')
        draft['country_scope']['evidence']='Başvurusu kabul edilen Türk katılımcıların seyahat masrafları karşılanır.'
        draft['target_scope']['evidence']='Kamu çalışanları ve özel sektör çalışanları başvurabilir.'
        self.assertEqual(publication_decision(self.current,draft,dict(self.item,text=self.text+' '+draft['country_scope']['evidence']+' '+draft['target_scope']['evidence']),self.today),'eligible')

    def test_turkish_teacher_evidence_is_recognized_without_country_guessing(self):
        draft=copy.deepcopy(self.draft)
        draft['target_scope']['evidence']='Lise öğretmenlerine yönelik eğitim programı.'
        item=dict(self.item,text=self.text+' Lise öğretmenlerine yönelik eğitim programı.')
        self.assertEqual(publication_decision(self.current,draft,item,self.today),'eligible')
        draft['country_scope']['evidence']='T.C. Millî Eğitim Bakanlığı'
        item['text']+=' T.C. Millî Eğitim Bakanlığı Bakanlığımıza bağlı okul ve kurumlarda görev yapan tüm öğretmenlere yönelik.'
        current=dict(self.current,source_url='https://ogm.meb.gov.tr/www/egitim/icerik/1')
        self.assertEqual(publication_decision(current,draft,item,self.today),'eligible')
        self.assertEqual(publication_decision(self.current,draft,item,self.today),'country_evidence_required')
        item['text']=item['text'].replace('Bakanlığımıza bağlı okul ve kurumlarda görev yapan tüm öğretmenlere yönelik.','')
        self.assertEqual(publication_decision(current,draft,item,self.today),'country_evidence_required')

    def test_individual_eligibility_does_not_create_school_entity_rights(self):
        draft=copy.deepcopy(self.draft)
        draft['target_scope']={'result':'eligible','targets':['teacher'],'evidence':'Individuals may apply for this grant.'}
        item=dict(self.item,text=self.text+' Individuals may apply for this grant.')
        self.assertEqual(publication_decision(self.current,draft,item,self.today),'eligible')
        draft['target_scope']['targets']=['school']
        self.assertEqual(publication_decision(self.current,draft,item,self.today),'audience_evidence_required')

    def test_aggregator_and_invented_or_unrelated_country_cannot_publish(self):
        self.assertEqual(publication_decision(dict(self.current,official_source_verified=False),self.draft,self.item,self.today),'primary_source_required')
        draft=copy.deepcopy(self.draft);draft['country_scope']['evidence']='All countries may apply.'
        self.assertEqual(publication_decision(self.current,draft,self.item,self.today),'country_evidence_required')
        draft['country_scope']['evidence']='Secondary school teachers are eligible.'
        self.assertEqual(publication_decision(self.current,draft,self.item,self.today),'country_evidence_required')
        draft['country_scope']['result']='ineligible'
        self.assertEqual(publication_decision(self.current,draft,self.item,self.today),'out_of_scope')

    def test_expired_or_unquoted_deadline_does_not_publish(self):
        draft=dict(self.draft,deadline='2025-11-30')
        self.assertEqual(publication_decision(self.current,draft,self.item,self.today),'current_deadline_required')
        draft=dict(self.draft,deadline_evidence='Application deadline: 31 December 2026.')
        self.assertEqual(publication_decision(self.current,draft,self.item,self.today),'deadline_evidence_required')

    def test_publication_is_version_bound_and_batch_authority_is_explicit(self):
        store=MemoryStore();store.put('calls','c',self.current)
        store.put('review_proposals','c',{'batch_id':'batch','base_version':version(self.current),'draft':self.draft})
        store.put('ai_batch_inputs','batch-c',self.item)
        job={'id':'batch','model':'gemini-3.8-flash','results':[{'id':'c','status':'evidence_review_required'}]}
        results=publish_batch(store,job,self.today)
        self.assertEqual(results[0]['status'],'published')
        call=store.get('calls','c')
        self.assertEqual(call['approval']['authority'],'verified_ai_batch_review')
        self.assertTrue(publishable(call,self.today))
        self.assertEqual(publish_batch(store,job,self.today)[0]['status'],'already_published')
        store.put('calls','c',dict(call,title='Changed'))
        self.assertEqual(publish_batch(store,job,self.today)[0]['status'],'stale')

    def test_no_deadline_requires_explicit_open_schedule_and_fresh_review(self):
        draft=copy.deepcopy(self.draft);draft['deadline']=None
        self.assertEqual(publication_decision(self.current,draft,self.item,self.today),'current_deadline_required')
        quote='Applications are accepted on a rolling basis.'
        draft['application_schedule']={'kind':'rolling','evidence':quote}
        item=dict(self.item,text=self.text+' '+quote)
        self.assertEqual(publication_decision(self.current,draft,item,self.today),'eligible')
        draft['application_schedule']['evidence']='Applications are always available.'
        self.assertEqual(publication_decision(self.current,draft,item,self.today),'current_deadline_required')
        call=dict(self.current,application_schedule={'kind':'rolling'},last_verified_at='2026-09-01T00:00:00Z')
        call['approval']={'reviewed':True,'version':version(call)}
        self.assertFalse(publishable(call,self.today))
        draft['application_schedule']={'kind':'rolling','evidence':'There are no deadlines – you can apply at any time of year.'}
        self.assertEqual(publication_decision(self.current,draft,dict(self.item,text=self.text+' '+draft['application_schedule']['evidence']),self.today),'eligible')

    def test_deadline_provenance_points_to_the_pdf_that_contains_the_quote(self):
        store=MemoryStore();store.put('calls','c',self.current)
        draft=copy.deepcopy(self.draft)
        pdf_url='https://example.org/rules.pdf'
        draft['documents'].append({'url':pdf_url,'hash':'def'})
        item=dict(self.item,documents=draft['documents'],document_texts=[
            {'url':'https://example.org/call','text':'Teachers in Turkey may apply. Secondary school teachers are eligible.'},
            {'url':pdf_url,'text':'Application deadline: 30 November 2026.'}])
        store.put('review_proposals','c',{'batch_id':'batch','base_version':version(self.current),'draft':draft})
        store.put('ai_batch_inputs','batch-c',item)
        job={'id':'batch','model':'gemini-3.8-flash','results':[{'id':'c','status':'evidence_review_required'}]}
        self.assertEqual(publish_batch(store,job,self.today)[0]['status'],'published')
        self.assertEqual(store.get('calls','c')['deadline_source_url'],pdf_url)
        self.assertEqual(store.get('calls','c')['official_url'],'https://example.org/call')

    def test_platform_access_does_not_make_grants_universally_eligible(self):
        draft=copy.deepcopy(self.draft);draft['country_scope']={'result':'eligible','evidence':'This platform is free of charge for all users.'}
        item=dict(self.item,text=self.text+' This platform is free of charge for all users. Education levels: Upper secondary - School education Target audience type: Teacher')
        current=dict(self.current,source_id='esep-courses')
        draft['opportunity_type']='training'
        self.assertEqual(publication_decision(current,draft,item,self.today),'eligible')
        draft['opportunity_type']='grant'
        self.assertEqual(publication_decision(current,draft,item,self.today),'country_evidence_required')
