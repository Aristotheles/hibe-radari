"""Periyot hesabı canlı ağ veya mevcut veritabanına dokunmaz."""
import unittest
import tempfile
import io
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch
from datetime import datetime, timezone
from hibe.aggregator.collector import due_sources

class SourceScheduleTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 10, 10, 12, tzinfo=timezone.utc)
        self.config = {'sources': [{'id': 'a'}, {'id': 'b', 'interval_hours': 6}]}

    def test_first_run_and_exact_boundary(self):
        self.assertEqual(due_sources(self.config, [], self.now), ['a', 'b'])
        health = [{'id': 'a', 'checked_at': '2026-10-09T12:00:00+00:00'},
                  {'id': 'b', 'checked_at': '2026-10-10T06:00:01+00:00'}]
        self.assertEqual(due_sources(self.config, health, self.now), ['a'])

    def test_failed_attempt_does_not_retry_before_period(self):
        health = [{'id': ident, 'health': 'failed', 'checked_at': self.now.isoformat()} for ident in ('a', 'b')]
        self.assertEqual(due_sources(self.config, health, self.now), [])

    def test_invalid_clock_does_not_hide_source(self):
        for timestamp in ('bad', None, '2026-10-10T12:00:00', '2026-10-11T12:00:00+00:00'):
            with self.subTest(timestamp=timestamp):
                self.assertIn('a', due_sources(self.config, [{'id': 'a', 'checked_at': timestamp}], self.now))

    def test_disabled_and_bad_intervals(self):
        self.assertEqual(due_sources(self.config, [], self.now, [{'enabled': False, 'connector_ids': ['a']}]), ['b'])
        for interval in (True, 0, -1, 169, float('nan'), '24'):
            with self.subTest(interval=interval), self.assertRaises(ValueError):
                due_sources({'sources': [{'id': 'a', 'interval_hours': interval}]}, [], self.now)

    def test_cli_no_due_does_not_collect_or_write(self):
        from hibe.store import SQLiteStore
        from hibe.aggregator.__main__ import main
        from hibe.aggregator.collector import load_config
        with tempfile.TemporaryDirectory() as directory:
            db = Path(directory)/'test.db'
            store = SQLiteStore(db)
            for source in load_config()['sources']:
                store.put('source_health', source['id'], {'id': source['id'], 'checked_at': datetime.now(timezone.utc).isoformat()})
            store.db.close()
            class Output(io.StringIO):
                def reconfigure(self, **kwargs): pass
            with redirect_stdout(Output()), patch('hibe.aggregator.__main__.run') as collect, patch('hibe.aggregator.__main__.write_report') as write:
                self.assertEqual(main(['--scheduled', '--store-db', str(db)]), 0)
                collect.assert_not_called()
                write.assert_not_called()

if __name__ == '__main__':
    unittest.main()
