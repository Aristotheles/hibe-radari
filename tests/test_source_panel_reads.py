import unittest
from hibe.service import Service
from hibe.store import MemoryStore


class SourcePanelReads(unittest.TestCase):
    def test_large_registry_uses_two_collection_reads_and_preserves_settings(self):
        class CountingStore(MemoryStore):
            def __init__(self):
                super().__init__()
                self.reads = []

            def all(self, kind):
                self.reads.append(kind)
                return super().all(kind)

            def get(self, kind, ident):
                raise AssertionError('Panel must not issue per-source remote reads')

        store = CountingStore()
        store.put('source_settings', 's0', {'id': 's0', 'enabled': False})
        store.put('source_health', 'shared', {'id': 'shared', 'health': 'failed', 'last_found_count': 3})
        config = [{'id': f's{i}', 'enabled': True, 'connector_ids': ['shared', 'missing']} for i in range(170)]
        rows = Service(store, 'admin').sources(config)
        self.assertEqual(store.reads, ['source_settings', 'source_health'])
        self.assertEqual(len(rows), 170)
        self.assertFalse(rows[0]['enabled'])
        self.assertTrue(rows[1]['enabled'])
        self.assertTrue(all(r['alert'] and r['last_found_count'] == 3 for r in rows))
        self.assertTrue(config[0]['enabled'])

