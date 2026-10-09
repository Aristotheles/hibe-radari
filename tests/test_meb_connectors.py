import json
import unittest
from pathlib import Path
from datetime import date
import httpx
from hibe.aggregator.collector import run_source,dedupe
from hibe.aggregator.relevance import RelevanceFilter

ROOT=Path(__file__).resolve().parents[1]
class MebConnectorTests(unittest.TestCase):
    def test_real_metadata_fixture_and_duplicates(self):
        config=json.loads((ROOT/'config/aggregator.json').read_text(encoding='utf-8'))
        for ident in ('meb-abdigm','meb-yegitek','meb-ogm','meb-mtegm'):
            source=dict(next(s for s in config['sources'] if s['id']==ident),detail=False)
            fixture=ROOT/'tests/fixtures/aggregator'/((ident[4:])+'_rss_20261010.xml')
            transport=httpx.MockTransport(lambda request:httpx.Response(200,content=fixture.read_bytes(),headers={'content-type':'text/xml'}))
            rows,health=run_source(source,config,RelevanceFilter(),date(2026,10,10),transport=transport)
            self.assertEqual(health['health'],'success');self.assertEqual(len(rows),2)
            self.assertTrue(all(row.source_url.startswith('https://') for row in rows))
            self.assertEqual(len(dedupe(rows+rows)),2)
    def test_html_failure_and_empty_feed_are_not_success(self):
        config=json.loads((ROOT/'config/aggregator.json').read_text(encoding='utf-8'))
        source=next(s for s in config['sources'] if s['id']=='meb-abdigm')
        for content in ('<html>maintenance</html>','<rss version="2.0"><channel><title>Feed</title></channel></rss>'):
            rows,health=run_source(source,config,RelevanceFilter(),date(2026,10,10),transport=httpx.MockTransport(lambda r:httpx.Response(200,text=content)))
            self.assertEqual(rows,[]);self.assertNotEqual(health['health'],'success')

    def test_real_ogm_deadline_fixture(self):
        from hibe.aggregator.html_cards import enrich
        from hibe.aggregator.models import GrantOpportunity
        from hibe.aggregator.net import Fetcher
        fixture=ROOT/'tests/fixtures/aggregator/ogm_gencbizz_deadline_20261010.html'
        client=Fetcher(['ogm.meb.gov.tr'],delay=0,transport=httpx.MockTransport(lambda r:httpx.Response(200,text=fixture.read_text(encoding='utf-8'))))
        try:
            item=GrantOpportunity('GençBizz Lise Girişimcilik Programı','meb-ogm','https://ogm.meb.gov.tr/www/gencbizz-lise-girisimcilik-programi-basvurulari-devam-ediyor/icerik/2657')
            enrich(item,client,date(2026,10,10));self.assertEqual(item.deadline,date(2026,10,16))
            self.assertEqual(item.deadline_precision,'day');self.assertIn('16 Ekim 2026',item.deadline_evidence)
        finally:client.close()

    def test_unknown_deadline_in_real_detail_metadata_is_not_invented(self):
        from hibe.aggregator.html_cards import enrich
        from hibe.aggregator.models import GrantOpportunity
        from hibe.aggregator.net import Fetcher
        for short in ('abdigm','yegitek'):
            fixture=ROOT/('tests/fixtures/aggregator/'+short+'_detail_20261010.html')
            host=short+'.meb.gov.tr';client=Fetcher([host],delay=0,transport=httpx.MockTransport(lambda r:httpx.Response(200,text=fixture.read_text(encoding='utf-8'))))
            try:
                item=GrantOpportunity('Kaynak üstveri örneği','meb-'+short,'https://'+host+'/www/duyuru')
                enrich(item,client,date(2026,10,10));self.assertIsNone(item.deadline)
                self.assertEqual(item.deadline_precision,'unknown');self.assertTrue(item.deadline_review_required)
            finally:client.close()
