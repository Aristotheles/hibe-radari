import json
import unittest
from pathlib import Path
from hibe.registry import inventory_rows

ROOT=Path(__file__).resolve().parents[1]

class SourceAcceptanceTests(unittest.TestCase):
    def test_every_inventory_url_has_real_observation_and_honest_review_route(self):
        cards=json.loads((ROOT/'config/source_acceptance.json').read_text(encoding='utf-8'))
        self.assertEqual({c['official_url'] for c in cards},{r['url'] for r in inventory_rows()})
        self.assertEqual(len(cards),len({c['source_id'] for c in cards}))
        registry={r['id']:r for r in json.loads((ROOT/'config/sources.json').read_text(encoding='utf-8'))}
        for c in cards:
            self.assertIn('page_observation',c)
            self.assertTrue(c['method'])
            self.assertGreater(c['interval_hours'],0)
            self.assertTrue(c['reason'])
            self.assertEqual(registry[c['source_id']]['operational_status'],c['status'])
            self.assertEqual(registry[c['source_id']]['acceptance_reason'],c['reason'])
            self.assertNotEqual(c['status'],'connected')
            if c['list_fixture']:
                self.assertTrue((ROOT/c['list_fixture']).is_file())
            if c['detail_fixture']:
                self.assertTrue((ROOT/c['detail_fixture']).is_file())
            if c['status']=='metadata_fixture_verified':
                self.assertTrue(c['list_fixture'])
                self.assertTrue((ROOT/c['duplicate_test']).is_file())
                self.assertTrue((ROOT/c['empty_error_test']).is_file())
                self.assertTrue(c['detail_review_reason'])

    def test_priority_package_manual_reasons_and_closed_evidence_remain_visible(self):
        cards=json.loads((ROOT/'config/source_acceptance.json').read_text(encoding='utf-8'))
        by={c['source_id']:c for c in cards}
        self.assertEqual(by['inventory-1268ef989142']['status'],'permission_required')
        self.assertEqual(by['inventory-ec9ada7f2c10']['status'],'manual_pending')
        self.assertEqual(by['inventory-cfa03fdcd36b']['status'],'manual_pending')
        self.assertEqual(by['source-1']['deadline_evidence']['date'],'2026-10-07')
