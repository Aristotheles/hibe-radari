import unittest
from hibe.aggregator.site import footer


class FreshnessTests(unittest.TestCase):
    def test_report_timestamp_is_converted_to_turkey_time(self):
        value = footer({'generated_at': '2026-10-10T12:30:00Z'})
        self.assertIn('Son güncelleme:', value)
        self.assertIn('10.10.2026 15:30', value)
        self.assertIn('datetime="2026-10-10T12:30:00Z"', value)

    def test_timezone_conversion_preserves_next_day(self):
        self.assertIn('11.10.2026 01:30', footer({'generated_at': '2026-10-10T22:30:00+00:00'}))
