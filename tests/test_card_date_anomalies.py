import unittest
import json
from pathlib import Path
from datetime import date
import httpx
from hibe.aggregator.html_cards import collect_cards
from hibe.aggregator.net import Fetcher

class CardDateAnomalyTests(unittest.TestCase):
    def card(self,raw):
        html=f'<article><h2>Duyuru başlığı</h2><a href="/call">Çağrı</a><time>{raw}</time></article>'
        fetcher=Fetcher(['www.stgm.org.tr'],transport=httpx.MockTransport(lambda r:httpx.Response(200,text=html)),delay=0)
        try:
            return collect_cards({'id':'stgm','url':'https://www.stgm.org.tr/hibe-duyurulari','selectors':{'card':'article','title':'h2','link':'a','date':'time'}},fetcher,date(2026,10,10))[0]
        finally:fetcher.close()
    def test_observed_2926_is_reviewed_without_guessing_2026(self):
        item=self.card('07.10.2926')
        self.assertIsNone(item.deadline)
        self.assertEqual(item.deadline_precision,'unknown')
        self.assertTrue(item.deadline_review_required)
        self.assertEqual(item.deadline_candidates[0]['value'],'2926-10-07')
        self.assertIn('07.10.2926',item.deadline_evidence)
        self.assertEqual(item.deadline_source_url,'https://www.stgm.org.tr/hibe-duyurulari')
    def test_invalid_day_keeps_evidence_but_valid_multiyear_call_survives(self):
        invalid=self.card('31.02.2026')
        self.assertIsNone(invalid.deadline)
        self.assertTrue(invalid.deadline_review_required)
        self.assertEqual(invalid.deadline_candidates[0]['raw'],'31.02.2026')
        valid=self.card('31.05.2028')
        self.assertEqual(valid.deadline,date(2028,5,31))
        self.assertFalse(valid.deadline_review_required)
    def test_real_official_evidence_resolves_list_anomaly_to_past_date(self):
        evidence=json.loads((Path(__file__).parent/'fixtures/aggregator/stgm_agora_date_evidence_20261010.json').read_text('utf-8'))
        item=self.card(evidence['list_display_date'])
        self.assertIsNone(item.deadline)
        item.apply_deadline(evidence['official_deadline_quote'],date(2026,10,10),evidence['official_url'])
        self.assertEqual(item.deadline,date(2026,10,7))
        self.assertEqual(item.deadline_source_url,evidence['official_url'])
        self.assertLess(item.deadline,date(2026,10,10))
        self.assertNotEqual(item.deadline.year,2926)
