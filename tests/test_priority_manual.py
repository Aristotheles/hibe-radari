import unittest
from pathlib import Path
from datetime import date
import httpx
from hibe.aggregator.html_cards import collect_list, enrich
from hibe.aggregator.net import Fetcher
from hibe.aggregator.collector import dedupe
from hibe.aggregator.models import GrantOpportunity

ROOT = Path(__file__).resolve().parents[1]

class PriorityManualTests(unittest.TestCase):
    def test_ulusal_ajans_real_list_and_closed_registration_deadline(self):
        fixture = ROOT/'tests/fixtures/aggregator/ua_list_manual_20261010.html'
        source = {'id':'ua-manual-research', 'url':'https://www.ua.gov.tr/', 'link_pattern':r'^/haber/[^/]+/?$', 'max_items':20}
        f = Fetcher(['www.ua.gov.tr'], delay=0, transport=httpx.MockTransport(lambda r:httpx.Response(200,content=fixture.read_bytes())))
        try:
            rows = collect_list(source, f, date(2026,10,10))
            self.assertEqual(len(rows), 2)
            self.assertEqual(len(dedupe(rows+rows)), 2)
            self.assertTrue(all(r.deadline is None for r in rows))
        finally:
            f.close()
        detail = ROOT/'tests/fixtures/aggregator/ua_detail_manual_20261010.html'
        f = Fetcher(['www.ua.gov.tr'], delay=0, transport=httpx.MockTransport(lambda r:httpx.Response(200,content=detail.read_bytes())))
        try:
            item = GrantOpportunity('2026 Yılı Ülke Merkezli Projeler Çevrim İçi Bilgilendirme Toplantısı','ua-manual-research','https://www.ua.gov.tr/haber/2026-yili-ulke-merkezli-projeler-cevrim-ici-bilgilendirme-toplantisi/')
            enrich(item, f, date(2026,10,10))
            self.assertEqual(item.deadline, date(2026,10,7))
            self.assertEqual(item.deadline_precision, 'day')
            self.assertLess(item.deadline, date(2026,10,10))
        finally:
            f.close()

    def test_missing_listing_is_empty_requiring_review(self):
        f = Fetcher(['www.ua.gov.tr'], delay=0, transport=httpx.MockTransport(lambda r:httpx.Response(200,text='<html>maintenance</html>')))
        try:
            self.assertEqual(collect_list({'id':'ua-manual-research','url':'https://www.ua.gov.tr/','link_pattern':r'^/haber/'},f,date(2026,10,10)),[])
        finally:
            f.close()
