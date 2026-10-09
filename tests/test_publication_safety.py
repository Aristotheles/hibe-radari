import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from datetime import date
import test_aggregator
from hibe.aggregator import site
from hibe.aggregator import __main__ as cli


def manifest(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}


class PublicationSafetyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.out = self.root / 'public'
        self.report = test_aggregator.SiteTests().report()
        site.build(self.report, self.out, date(2026, 10, 9))
        self.before = manifest(self.out)

    def test_unapproved_stale_partial_failed_and_empty_keep_existing_site(self):
        cases = []
        for status in ('partial', 'failed', 'suspicious_empty'):
            r = copy.deepcopy(self.report); r['run_status'] = status; cases.append(r)
        r = copy.deepcopy(self.report); r['accepted'][0].pop('approval'); cases.append(r)
        r = copy.deepcopy(self.report); r['accepted'][0]['title'] = 'DeÃ„Å¸iÃ…Å¸miÃ…Å¸ iÃƒÂ§erik'; cases.append(r)
        r = copy.deepcopy(self.report); r['accepted'] = []; cases.append(r)
        for r in cases:
            with self.subTest(status=r.get('run_status')):
                with self.assertRaises(site.PublicationBlocked):
                    site.build(r, self.out, date(2026, 10, 9))
                self.assertEqual(manifest(self.out), self.before)

    def test_render_failure_keeps_html_json_ics(self):
        with patch.object(site, 'detail_page', side_effect=OSError('disk failure')):
            with self.assertRaises(OSError):
                site.build(self.report, self.out, date(2026, 10, 9))
        self.assertEqual(manifest(self.out), self.before)

    def test_swap_failure_restores_previous_tree(self):
        import os
        original = os.replace
        def replace(src, dst):
            if '.stage-' in str(src):
                raise OSError('swap failure')
            return original(src, dst)
        with patch('os.replace', side_effect=replace):
            with self.assertRaises(OSError):
                site.build(self.report, self.out, date(2026, 10, 9))
        self.assertEqual(manifest(self.out), self.before)

    def test_success_retains_rollback_copy(self):
        site.build(self.report, self.out, date(2026, 10, 9))
        backups = list(self.root.glob('.public.backup-*'))
        self.assertTrue(backups)
        self.assertEqual(manifest(backups[-1]), self.before)

    def test_partial_and_only_cli_keep_latest(self):
        from hibe.aggregator import collector
        latest = self.root / 'data/aggregator/latest.json'
        latest.parent.mkdir(parents=True); latest.write_bytes(b'last good')
        for args in ([], ['--only', 's']):
            r = copy.deepcopy(self.report); r['run_status'] = 'partial'
            with patch.object(collector, 'ROOT', self.root), patch.object(cli, 'run', return_value=r):
                self.assertEqual(cli.main(args), 1)
            self.assertEqual(latest.read_bytes(), b'last good')
            self.assertTrue(latest.with_name('last-attempt.json').is_file())

    def test_cli_unapproved_publication_keeps_latest_and_site(self):
        from hibe.aggregator import collector
        latest = self.root / 'data/aggregator/latest.json'
        latest.parent.mkdir(parents=True); latest.write_bytes(b'last good')
        r = copy.deepcopy(self.report); r['accepted'][0].pop('approval')
        with patch.object(collector, 'ROOT', self.root), patch.object(cli, 'run', return_value=r):
            self.assertEqual(cli.main(['--site', str(self.out)]), 1)
        self.assertEqual(latest.read_bytes(), b'last good')
        self.assertEqual(manifest(self.out), self.before)


class SourceSafetyTests(unittest.TestCase):
    def test_maintenance_html_is_not_a_successful_feed(self):
        from hibe.aggregator import feeds
        from types import SimpleNamespace
        fetcher = SimpleNamespace(get=lambda url: SimpleNamespace(content=b'<html>Maintenance</html>'))
        with self.assertRaises(ValueError):
            feeds.collect({'url': 'https://example.org/feed'}, fetcher, date(2026, 10, 9))

    def test_503_source_marks_failed(self):
        from hibe.aggregator import collector
        from types import SimpleNamespace
        fetcher = SimpleNamespace(calls=1, close=lambda: None)
        source = {'id': 'bad', 'type': 'feed', 'allowed_hosts': ['example.org']}
        with patch.object(collector, 'Fetcher', return_value=fetcher), patch.dict(collector.CONNECTORS, {'feed': lambda *args: (_ for _ in ()).throw(ValueError('HTTP 503'))}):
            items, status = collector.run_source(source, {}, None, date(2026, 10, 9))
        self.assertEqual(items, [])
        self.assertEqual(status['health'], 'failed')
        self.assertIn('503', status['error'])

    def test_atomic_report_failure_keeps_old_json(self):
        from hibe.aggregator import collector
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'latest.json'; path.write_bytes(b'old report')
            with patch('os.replace', side_effect=OSError('disk full')):
                with self.assertRaises(OSError):
                    collector.write_report({'test': True}, path)
            self.assertEqual(path.read_bytes(), b'old report')
            self.assertEqual(list(Path(tmp).iterdir()), [path])
