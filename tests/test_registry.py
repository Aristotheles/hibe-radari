import copy
import json
import unittest
import subprocess
import sys
from pathlib import Path

from hibe.registry import audit_sources, valid_url, markdown_report, inventory_rows


class RegistryTests(unittest.TestCase):
    def setUp(self):
        self.sources = json.loads((Path(__file__).resolve().parents[1] / 'config/sources.json').read_text(encoding='utf-8'))

    def manual_fixture(self):
        # Kurgusal fixture: gerçek kaynak kimliği veya doğrulama kanıtı değildir.
        return {'id': 'demo-fixture', 'name': 'DEMO kaynak fixture', 'identity_status': 'verified',
                'identity_evidence': 'DEMO fixture belgesi', 'url': 'https://example.org',
                'method': 'manual', 'manual_check': {'url': 'https://example.org/calls', 'steps': 'DEMO manuel kontrol adımı'},
                'last_checked': '2026-10-09', 'status': 'ready'}

    def test_current_inventory_keeps_all_urls_and_legacy_ids(self):
        report = audit_sources(self.sources)
        self.assertEqual(report['scope_count'],135)
        self.assertEqual(report['count'],154)
        self.assertEqual(report['legacy_count'],19)
        self.assertEqual(report['candidate_names'],141)
        self.assertEqual(report['missing_identities'], 11)
        self.assertEqual(report['ready_controls'], 0)
        self.assertEqual(report['verified_identities'], 2)
        self.assertFalse(report['complete'])
        self.assertFalse(report['errors'])
        self.assertIn('Türkiye Ulusal Ajansı', markdown_report(report))

    def test_three_sources_cannot_satisfy_scope(self):
        report = audit_sources(self.sources[:3])
        self.assertFalse(report['complete'])
        self.assertIn('Tam 135 envanter URL kaydı gerekli', report['errors'][0])

    def test_duplicate_identity_and_invalid_shape_are_errors(self):
        values = copy.deepcopy(self.sources)
        values[1]['id'] = values[0]['id']
        self.assertTrue(audit_sources(values)['errors'])
        self.assertFalse(audit_sources({})['complete'])

    def test_ready_flag_alone_does_not_create_control_evidence(self):
        values = copy.deepcopy(self.sources)
        values[0]['status'] = 'ready'
        report = audit_sources(values)
        self.assertFalse(report['rows'][0]['control_ready'])
        self.assertIn('Kimlik özgün belgede doğrulanmadı', report['rows'][0]['gaps'])

    def test_manual_control_requires_both_url_and_steps(self):
        fixture = self.manual_fixture()
        self.assertTrue(audit_sources([fixture])['rows'][0]['control_ready'])
        fixture['manual_check']['steps'] = ''
        self.assertFalse(audit_sources([fixture])['rows'][0]['control_ready'])

    def test_automatic_control_rejects_foreign_document_hosts(self):
        fixture = self.manual_fixture()
        fixture.update(method='auto', type='official', allowed_hosts=['example.org'],
                       call_urls=[{'url': 'https://example.org/call', 'documents': ['https://other.example/doc.pdf']}])
        self.assertFalse(audit_sources([fixture])['rows'][0]['control_ready'])
        fixture['call_urls'][0]['documents'] = ['https://example.org/doc.pdf']
        self.assertTrue(audit_sources([fixture])['rows'][0]['control_ready'])

    def test_urls_reject_unsafe_protocol_credentials_and_ports(self):
        for value in [None, 'http://example.org', 'https://user:pass@example.org', 'https://example.org:9000', 'https://example.org:bad']:
            self.assertFalse(valid_url(value))
        self.assertTrue(valid_url('https://example.org/calls'))

    def test_cli_utf8_and_strict_failure_for_unready_inventory(self):
        result = subprocess.run([sys.executable, '-m', 'hibe.registry', '--strict'],
                                cwd=Path(__file__).resolve().parents[1],
                                capture_output=True, encoding='utf-8')
        self.assertEqual(result.returncode, 1)
        report = json.loads(result.stdout)
        self.assertEqual(report['rows'][0]['name'],self.sources[0]['name'])
        self.assertFalse(report['complete'])

    def test_pipeline_reads_registry_and_profile_in_utf8_without_services(self):
        from contextlib import redirect_stdout
        from io import StringIO
        from unittest.mock import patch, MagicMock
        from hibe.pipeline import main
        original = Path.read_text
        read_files = []

        def explicit_encoding(path, *args, **kwargs):
            self.assertEqual(kwargs.get('encoding'), 'utf-8')
            read_files.append(path.name)
            return original(path, *args, **kwargs)

        with patch.object(Path, 'read_text', explicit_encoding), \
                patch('sys.argv', ['pipeline', '--fake']), \
                patch('hibe.server.App', return_value=MagicMock()), \
                patch('hibe.pipeline.scan_source', return_value={}) as scan, \
                redirect_stdout(StringIO()):
            main()
        self.assertEqual(read_files, ['sources.json', 'profile.json'])
        self.assertEqual(scan.call_count,len(self.sources))
        self.assertEqual(scan.call_args_list[0].args[0]['name'],self.sources[0]['name'])


if __name__ == '__main__':
    unittest.main()


class InventoryPreservationTests(unittest.TestCase):
    def test_every_url_and_old_identity_is_preserved(self):
        root=Path(__file__).resolve().parents[1]
        sources=json.loads((root/'config/sources.json').read_text(encoding='utf-8'))
        old=json.loads((root/'config/sources.legacy-stage0.json').read_text(encoding='utf-8'))
        self.assertEqual({r['url'] for r in inventory_rows()},{r['url'] for r in sources if r.get('record_kind')=='inventory'})
        self.assertTrue({r['id'] for r in old}.issubset({r['id'] for r in sources}))
        config=json.loads((root/'config/aggregator.json').read_text(encoding='utf-8'))
        self.assertEqual(len(config['baseline_source_ids']),13)
        self.assertTrue(set(config['baseline_source_ids']).issubset({c['id'] for c in config['sources']}))
        self.assertFalse(any(r.get('operational_status')=='connected' for r in sources))


class SourceControlTests(unittest.TestCase):
    def test_disabled_connector_never_fetches_and_empty_scope_is_unsafe(self):
        from hibe.aggregator.collector import run
        from unittest.mock import patch
        config={'sources':[{'id':'s','type':'feed','url':'https://x.org','allowed_hosts':['x.org']}]}
        with patch('hibe.aggregator.collector.run_source') as fetch:
            report=run(config=config,source_settings=[{'id':'registry-s','enabled':False,'connector_ids':['s']}])
        fetch.assert_not_called();self.assertEqual(report['run_status'],'suspicious_empty')
    def test_all_connectors_have_visible_registry_mapping(self):
        root=Path(__file__).resolve().parents[1]
        rows=json.loads((root/'config/sources.json').read_text(encoding='utf-8'))
        connectors=json.loads((root/'config/aggregator.json').read_text(encoding='utf-8'))['sources']
        self.assertTrue({c['id'] for c in connectors}.issubset({i for r in rows for i in r.get('connector_ids',[])}))
