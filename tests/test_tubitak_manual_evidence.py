"""Real short excerpts; no live fetch, publication approval or invented terms."""
import json
import unittest
from datetime import date
from pathlib import Path

from hibe.aggregator.models import GrantOpportunity
from hibe.aggregator.feeds import collect
from hibe.eligibility import assess, UNKNOWN


class TubitakManualEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.evidence = json.loads((Path(__file__).parent / 'fixtures/aggregator/tubitak_manual_evidence_20261010.json').read_text('utf-8'))

    def test_official_dates_are_not_publication_or_start_dates(self):
        for call in self.evidence['calls']:
            with self.subTest(call=call['title']):
                item = GrantOpportunity(call['title'], 'tubitak-duyuru', call['official_url'])
                item.apply_deadline(call['deadline_quote'], date(2026, 10, 10))
                self.assertEqual(item.deadline.isoformat(), call['expected_deadline'])
                self.assertNotEqual(item.deadline.isoformat(), call.get('publication_date') or call['application_start'])
                self.assertEqual(item.deadline_source_url, call['official_url'])
                self.assertFalse(item.deadline_review_required)
                row = item.to_dict()
                row['official_source_verified'] = True
                row['description_short'] = call.get('eligibility_quote', '')
                eligibility = assess(row, date(2026, 10, 10))
                self.assertEqual(eligibility['targets']['student_14_18']['status'], UNKNOWN)

    def test_connection_challenge_is_not_a_valid_empty_feed(self):
        class Response:
            content = b'<html><title>Verifying your connection...</title></html>'
        class Fetcher:
            def get(self, url):
                return Response()
        with self.assertRaises(ValueError):
            collect({'id': 'tubitak-4000', 'url': self.evidence['rss_observation']['url']}, Fetcher(), date(2026, 10, 10))


if __name__ == '__main__':
    unittest.main()
