import json
import unittest
from pathlib import Path
from datetime import date
import httpx
from hibe.aggregator.collector import run_source, dedupe
from hibe.aggregator.relevance import RelevanceFilter

ROOT = Path(__file__).resolve().parents[1]

class DiscoveredFeedTests(unittest.TestCase):
    def test_existing_identity_without_feed_guid_is_preserved(self):
        import hashlib
        from hibe.aggregator.models import GrantOpportunity, canonical_url
        item = GrantOpportunity('Existing 2026 call', 'baseline', 'https://example.org/call?id=1')
        expected = hashlib.sha256((canonical_url(item.source_url) + '|' + '||||' + '|2026').encode()).hexdigest()[:20]
        self.assertEqual(item.id, expected)

    def test_real_feed_identity_and_unknown_publication_date(self):
        cfg = json.loads((ROOT/'config/aggregator.json').read_text(encoding='utf-8'))
        for ident in ('eurodesk-finder', 'interreg-next-med', 'mercator', 'iki-small-grants', 'gef-sgp', 'regeneron-isef', 't4-education', 'global-schools', 'roots-shoots', 'opportunity-desk', 'opportunities-youth', 'eu-calls'):
            source = next(s for s in cfg['sources'] if s['id'] == ident)
            fixture = ROOT/'tests/fixtures/aggregator'/f'{ident}_rss_20261010.xml'
            rows, health = run_source(source, cfg, RelevanceFilter(), date(2026,10,10), transport=httpx.MockTransport(lambda r: httpx.Response(200, content=fixture.read_bytes())))
            self.assertEqual(health['health'], 'success')
            self.assertEqual(len(dedupe(rows+rows)), 0 if ident == 'gef-sgp' else 1 if ident == 'regeneron-isef' else 2)
            if ident == 'eurodesk-finder':
                self.assertEqual(len({r.source_url for r in rows}), 1)
                self.assertEqual(len({r.id for r in rows}), 2)
                self.assertTrue(all(r.published_at is None for r in rows))
                self.assertTrue(all(r.official_call_id is None for r in rows))

    def test_empty_and_broken_feed_fail_closed(self):
        cfg = json.loads((ROOT/'config/aggregator.json').read_text(encoding='utf-8'))
        for ident in ('eurodesk-finder', 'interreg-next-med', 'mercator', 'iki-small-grants', 'gef-sgp', 'regeneron-isef', 't4-education', 'global-schools', 'roots-shoots', 'opportunity-desk', 'opportunities-youth', 'eu-calls'):
            source = next(s for s in cfg['sources'] if s['id'] == ident)
            for body in ('<html>error</html>', '<rss version="2.0"><channel><title>empty</title></channel></rss>'):
                rows, health = run_source(source, cfg, RelevanceFilter(), date(2026,10,10), transport=httpx.MockTransport(lambda r: httpx.Response(200, text=body)))
                self.assertEqual(rows, [])
                if ident == 'gef-sgp' and body.startswith('<rss'):
                    self.assertEqual(health['health'], 'success')
                else:
                    self.assertNotEqual(health['health'], 'success')
