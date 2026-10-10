import unittest
from hibe.store import MemoryStore
from hibe.domain import version
from hibe.pending_opportunities import pending_opportunities,pending_preview
from datetime import date


class PendingOpportunityTests(unittest.TestCase):
    def setUp(self):
        self.store=MemoryStore();self.today=date(2026,10,10)
        self.call={'id':'c','title':'Actual grant','source_id':'s','source_url':'https://example.org/call',
            'official_source_verified':True,'deadline':None,'official_status':'bilinmiyor'}
        self.store.put('calls','c',self.call)
        self.draft={'title':'Actual grant','summary':'Application information', 'opportunity_type':'grant',
            'open_evidence':'Applications are now open.', 'official_status':'acik',
            'paths':[{'role':'ogretmen_birey','conditions':[]}],'country_scope':{'result':'unknown'}}
        self.store.put('review_proposals','c',{'id':'c','batch_id':'b','base_version':version(self.call),'draft':self.draft})
        self.store.put('ai_batches','b',{'id':'b','status':'completed'})
        self.store.put('ai_batch_inputs','b-c',{'id':'c','batch_id':'b','text':'Applications are now open.'})
        self.store.put('publication_decisions','c',{'id':'c','status':'country_evidence_required','base_version':version(self.call),'checked_on':'2026-10-10',
            'public_preview':pending_preview(self.call,self.draft,{'text':'Applications are now open.'},'country_evidence_required',self.today)})

    def test_actual_application_is_separate_and_has_no_fictitious_date_or_private_data(self):
        rows=pending_opportunities(self.store,self.today)
        self.assertEqual(len(rows),1);self.assertEqual(rows[0]['publication_status'],'verification_pending')
        self.assertIsNone(rows[0]['deadline']);self.assertNotIn('approval',rows[0]);self.assertNotIn('documents',rows[0])
        self.assertEqual(rows[0]['paths'][0]['conditions'],[])

    def test_openness_conflict_blocks_preview_but_personal_unknown_does_not(self):
        self.draft.update(ai_conflict=True,ai_conflict_fields=['openness'])
        self.assertIsNone(pending_preview(self.call,self.draft,{'text':'Applications are now open.'},'invalid_evidence',self.today))
        self.draft['ai_conflict_fields']=['personal_conditions']
        self.assertIsNotNone(pending_preview(self.call,self.draft,{'text':'Applications are now open.'},'invalid_evidence',self.today))

    def test_server_default_day_is_istanbul_even_when_host_day_is_utc(self):
        from hibe.domain import today_istanbul
        from datetime import datetime,timezone
        from unittest.mock import patch
        instant=datetime(2026,10,10,22,30,tzinfo=timezone.utc)
        with patch('hibe.domain.datetime') as clock:
            clock.now.side_effect=lambda zone:instant.astimezone(zone)
            self.assertEqual(today_istanbul(),date(2026,10,11))

    def test_old_dated_announcement_is_not_a_current_pending_opportunity(self):
        self.call['source_url']='https://example.org/news/2024/10/15/awards'
        self.assertIsNone(pending_preview(self.call,self.draft,{'text':'Applications are now open.'},'country_evidence_required',self.today))
        self.store.put('calls','c',self.call)
        decision=self.store.get('publication_decisions','c')
        decision['base_version']=version(self.call)
        decision['public_preview']['source_url']=self.call['source_url']
        self.store.put('publication_decisions','c',decision)
        self.assertEqual(pending_opportunities(self.store,self.today),[])

    def test_rejection_technical_error_stale_or_news_never_become_pending_calls(self):
        for status in ('closed','out_of_scope','document_unavailable','published'):
            self.store.put('publication_decisions','c',{'id':'c','status':status})
            self.assertEqual(pending_opportunities(self.store,self.today),[])
        self.store.put('publication_decisions','c',{'id':'c','status':'invalid_evidence'})
        self.draft['open_evidence']='Our foundation supports teachers.'
        self.store.put('review_proposals','c',{'id':'c','batch_id':'b','base_version':version(self.call),'draft':self.draft})
        self.assertEqual(pending_opportunities(self.store,self.today),[])
