import unittest
from hibe.llm import redact_contacts

class ContactRedactionTests(unittest.TestCase):
    def test_dates_and_age_evidence_survive_contacts(self):
        original='Son başvuru 2026-11-30, etkinlik 30.11.2026; yaş 14-18. +90 532 123 45 67; test@example.org'
        result=redact_contacts(original)
        for evidence in ('2026-11-30', '30.11.2026', '14-18'):
            self.assertIn(evidence,result)
        self.assertNotIn('532',result)
        self.assertNotIn('test@example.org',result)
        self.assertIn('[PHONE]',result)
        self.assertIn('[EMAIL]',result)

    def test_adjacent_date_and_phone_do_not_swallow_each_other(self):
        for text in ('2026-11-30 +90 532 123 45 67', '+90 532 123 45 67 2026-11-30'):
            self.assertIn('2026-11-30',redact_contacts(text))
            self.assertNotIn('532',redact_contacts(text))

    def test_invalid_date_is_not_an_exemption(self):
        self.assertEqual(redact_contacts('2026-99-99'),'[PHONE]')
