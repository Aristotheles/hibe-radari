import unittest
from hibe.review_decisions import add_conflict, critical_conflict, decision_category
from tests import test_batch_publication
from hibe.batch_publication import publication_decision


class ReviewDecisionTests(unittest.TestCase):
    def test_long_document_retains_tail_and_cannot_claim_partial_coverage(self):
        from hibe.review_batch import document_sections
        from hibe.gemini_batch import request_payload
        text='Application conditions. '*3000+' Only university graduates may apply.'
        sections=document_sections(text)
        self.assertEqual(''.join(sections),text)
        payload=request_payload(text,'Actual call','2026-10-10',sections)
        self.assertIn('Only university graduates may apply.',payload['contents'][0]['parts'][-1]['text'])
        with self.assertRaises(ValueError):request_payload(text,'Actual call','2026-10-10',sections[:-1])
        with self.assertRaises(ValueError):document_sections('x'*144001)
    def test_missing_evidence_and_document_error_are_not_rejections(self):
        self.assertEqual(decision_category('invalid_evidence'), 'critical_evidence_missing')
        self.assertEqual(decision_category('document_unavailable'), 'technical_document_error')
        self.assertEqual(decision_category('out_of_scope'), 'explicitly_out_of_scope')

    def test_personal_conflict_does_not_block_verified_access(self):
        fixture = test_batch_publication.BatchPublicationTests(); fixture.setUp()
        add_conflict(fixture.draft, 'personal_conditions')
        self.assertEqual(publication_decision(fixture.current, fixture.draft, fixture.item, fixture.today), 'eligible')
        add_conflict(fixture.draft, 'country')
        self.assertEqual(publication_decision(fixture.current, fixture.draft, fixture.item, fixture.today), 'invalid_evidence')

    def test_legacy_and_unknown_conflicts_fail_closed(self):
        self.assertTrue(critical_conflict({'ai_conflict': True}))
        self.assertTrue(critical_conflict({'ai_conflict_fields': ['unrecognized']}))
        self.assertFalse(critical_conflict({'ai_conflict_fields': ['personal_conditions']}))

    def test_short_country_list_and_unrelated_country_mention(self):
        fixture = test_batch_publication.BatchPublicationTests(); fixture.setUp()
        fixture.draft['country_scope']['evidence']='Türkiye'
        fixture.item['text'] += '\nEligible countries:\nFrance, Türkiye, Italy\n\nApplication conditions follow.'
        self.assertEqual(publication_decision(fixture.current, fixture.draft, fixture.item, fixture.today),'eligible')
        fixture.item['text']=fixture.text+' Our foundation supports education in Türkiye.'
        self.assertEqual(publication_decision(fixture.current, fixture.draft, fixture.item, fixture.today),'country_evidence_required')

    def test_country_list_survives_html_whitespace_and_adjacent_country_quote(self):
        fixture=test_batch_publication.BatchPublicationTests();fixture.setUp()
        fixture.draft['country_scope']['evidence']='Tunisia Türkiye Turkmenistan'
        fixture.item['text']+=' Eligible Countries Projects in the following countries qualify for support. Tunisia Türkiye Turkmenistan Uganda'
        self.assertEqual(publication_decision(fixture.current,fixture.draft,fixture.item,fixture.today),'eligible')
        fixture.draft['country_scope']['evidence']='Our foundation supports education in Türkiye.'
        self.assertEqual(publication_decision(fixture.current, fixture.draft, fixture.item, fixture.today),'country_evidence_required')

    def test_literal_unrelated_quote_cannot_prove_exclusion(self):
        fixture = test_batch_publication.BatchPublicationTests(); fixture.setUp()
        fixture.draft['country_scope']={'result':'ineligible','evidence':'Secondary school teachers are eligible.'}
        self.assertEqual(publication_decision(fixture.current,fixture.draft,fixture.item,fixture.today),'invalid_evidence')
        fixture.draft['country_scope']['evidence']='Only residents of the United States are eligible.'
        fixture.item['text']+=' Only residents of the United States are eligible.'
        self.assertEqual(publication_decision(fixture.current,fixture.draft,fixture.item,fixture.today),'out_of_scope')
