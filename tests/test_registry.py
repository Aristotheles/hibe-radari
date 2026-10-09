import copy
import json
import unittest
import subprocess
import sys
from pathlib import Path

from hibe.registry import audit_sources, valid_url, markdown_report


class RegistryTests(unittest.TestCase):
    def setUp(self):
        self.sources = json.loads((Path(__file__).resolve().parents[1] / 'config/sources.json').read_text(encoding='utf-8'))

    def manual_fixture(self):
        # Kurgusal fixture: gerçek kaynak kimliği veya doğrulama kanıtı değildir.
        return {'id': 'demo-fixture', 'name': 'DEMO kaynak fixture', 'identity_status': 'verified',
                'identity_evidence': 'DEMO fixture belgesi', 'url': 'https://example.org',
                'method': 'manual', 'manual_check': {'url': 'https://example.org/calls', 'steps': 'DEMO manuel kontrol adımı'},
                'last_checked': '2026-10-09', 'status': 'ready'}

    def test_current_inventory_keeps_thirty_and_explicit_gaps(self):
        report = audit_sources(self.sources)
        self.assertEqual(report['count'], 30)
        self.assertEqual(report['candidate_names'], 19)
        self.assertEqual(report['missing_identities'], 11)
        self.assertEqual(report['ready_controls'], 0)
        self.assertEqual(report['verified_identities'], 0)
        self.assertFalse(report['complete'])
        self.assertFalse(report['errors'])
        self.assertIn('Türkiye Ulusal Ajansı', markdown_report(report))

    def test_three_sources_cannot_satisfy_scope(self):
        report = audit_sources(self.sources[:3])
        self.assertFalse(report['complete'])
        self.assertIn('Tam 30 kayıt gerekli', report['errors'][0])

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
        self.assertEqual(report['rows'][0]['name'], 'Türkiye Ulusal Ajansı')
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
        self.assertEqual(scan.call_count, 30)
        self.assertEqual(scan.call_args_list[0].args[0]['name'], 'Türkiye Ulusal Ajansı')


if __name__ == '__main__':
    unittest.main()
