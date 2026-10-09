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
        for ident in ('meb-abdigm','meb-yegitek'):
            source=next(s for s in config['sources'] if s['id']==ident)
            fixture=ROOT/'tests/fixtures/aggregator'/((ident[4:])+'_rss_20261010.xml')
            transport=httpx.MockTransport(lambda request:httpx.Response(200,content=fixture.read_bytes(),headers={'content-type':'text/xml'}))
            rows,health=run_source(source,config,RelevanceFilter(),date(2026,10,10),transport=transport)
            self.assertEqual(health['health'],'success');self.assertEqual(len(rows),2)
            self.assertTrue(all(row.source_url.startswith('https://') for row in rows))
            self.assertLessEqual(len(dedupe(rows+rows)),2)
    def test_html_failure_and_empty_feed_are_not_success(self):
        config=json.loads((ROOT/'config/aggregator.json').read_text(encoding='utf-8'))
        source=next(s for s in config['sources'] if s['id']=='meb-abdigm')
        for content in ('<html>maintenance</html>','<rss version="2.0"><channel><title>Feed</title></channel></rss>'):
            rows,health=run_source(source,config,RelevanceFilter(),date(2026,10,10),transport=httpx.MockTransport(lambda r:httpx.Response(200,text=content)))
            self.assertEqual(rows,[]);self.assertNotEqual(health['health'],'success')
