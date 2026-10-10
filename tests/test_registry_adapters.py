import json,unittest
from pathlib import Path
from hibe.registry import inventory_rows
from hibe.aggregator.collector import CONNECTORS

class RegistryAdapterTests(unittest.TestCase):
    def test_every_addressed_inventory_source_has_existing_supported_adapter(self):
        registry=json.loads(Path('config/sources.json').read_text('utf-8'))
        config=json.loads(Path('config/aggregator.json').read_text('utf-8'))
        connectors={s['id']:s for s in config['sources']}
        rows=[r for r in registry if r.get('record_kind')=='inventory']
        self.assertEqual({r['url'] for r in rows},{r['url'] for r in inventory_rows()})
        for row in rows:
            self.assertTrue(row['connector_ids'],row['name'])
            for ident in row['connector_ids']:
                self.assertIn(ident,connectors)
                self.assertIn(connectors[ident]['type'],CONNECTORS)
                self.assertTrue(connectors[ident]['allowed_hosts'])

    def test_explicit_extraction_bans_are_not_enabled_by_registry_expansion(self):
        config=json.loads(Path('config/aggregator.json').read_text('utf-8'))
        ids={'inventory-ea64d35ac8e8','inventory-5f24ee4171a5','inventory-a08149e86076','inventory-6fdcf036901c'}
        for source in config['sources']:
            if source.get('registry_id') in ids:
                self.assertEqual(source['access_policy']['terms_status'],'permission_required')
