import json
import unittest
from pathlib import Path
from datetime import date
import httpx
from hibe.aggregator.collector import run_source,dedupe
from hibe.aggregator.relevance import RelevanceFilter

ROOT=Path(__file__).resolve().parents[1]
IDS=('ab-ilan-hibe','ab-ilan-genel','etwinning-tr','ifturquie','tusev','sivilsayfalar')
class BaselineFeedTests(unittest.TestCase):
    def test_observed_interfaces_parse_and_duplicates_do_not_grow(self):
        cfg=json.loads((ROOT/'config/aggregator.json').read_text(encoding='utf-8'))
        for ident in IDS:
            source=dict(next(s for s in cfg['sources'] if s['id']==ident),detail=False)
            fixture=ROOT/('tests/fixtures/aggregator/'+ident+'_rss_20261010.xml')
            rows,health=run_source(source,cfg,RelevanceFilter(),date(2026,10,10),transport=httpx.MockTransport(lambda r:httpx.Response(200,content=fixture.read_bytes())))
            self.assertEqual(health['health'],'success',ident)
            self.assertEqual(len(rows),0 if ident=='tusev' else 1,ident)
            self.assertEqual(len(dedupe(rows+rows)),len(rows),ident)
    def test_html_is_failure_even_for_source_with_verified_empty_feed(self):
        cfg=json.loads((ROOT/'config/aggregator.json').read_text(encoding='utf-8'));source=next(s for s in cfg['sources'] if s['id']=='tusev')
        rows,health=run_source(source,cfg,RelevanceFilter(),date(2026,10,10),transport=httpx.MockTransport(lambda r:httpx.Response(200,text='<html>maintenance</html>')))
        self.assertEqual(rows,[]);self.assertEqual(health['health'],'failed')
