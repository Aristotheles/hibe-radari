import unittest
from datetime import date
from hibe.presentation import page, detail, month_view

class PresentationTests(unittest.TestCase):
    def call(self):
        return {'id': 'demo-test', 'title': '<img src=x onerror=alert(1)>', 'summary': 'Kurgusal & örnek', 'deadline': '2026-12-31', 'demo': True, 'urls': ['https://example.org'], 'paths': [{'role': 'dogrudan', 'eligibility': 'belirsiz', 'conditions': [{'text': '<script>', 'result': 'bilinmiyor', 'evidence': 'A & B'}]}]}

    def test_escape_and_no_fabricated_eligibility(self):
        rendered = detail(self.call())
        self.assertNotIn('<img', rendered); self.assertNotIn('<script>', rendered)
        self.assertIn('&lt;img', rendered); self.assertIn('Uygunluk belirsiz', rendered)
        self.assertNotIn('Resmî sayfada doğrula', rendered)

    def test_real_source_unsafe_urls_are_not_linked(self):
        c = self.call(); c['demo'] = False
        c['urls'] = ['javascript:alert(1)', 'https://user:secret@example.org', 'https://example.org/ok']
        rendered = detail(c)
        self.assertNotIn('href="javascript:', rendered); self.assertNotIn('user:secret', rendered)
        self.assertIn('href="https://example.org/ok"', rendered)

    def test_only_public_call_gets_detail_and_metadata_escaped(self):
        template = '<title>Old</title><!--SERVER_META--><!--SERVER_CONTENT--><!--SERVER_MODE-->'
        status, body = page(template, '/ilan/demo-test', '', [self.call()], [], True)
        self.assertEqual(status, 200); self.assertIn(b'og:title', body); self.assertNotIn(b'<img', body)
        self.assertEqual(page(template, '/ilan/private', '', [], [], True)[0], 404)
        self.assertIsNone(page(template, '/ilan/../../secret', '', [], [], True))

    def test_calendar_handles_invalid_query_and_year_boundary(self):
        self.assertIn('Aralık 2026', month_view([self.call()], 'month=12&year=2026', date(2026,10,9)))
        self.assertIn('Ekim 2026', month_view([], 'month=999&year=abc', date(2026,10,9)))
        self.assertIn('31 Aralık 2026', month_view([self.call()], 'month=12&year=2026', date(2026,10,9)))

    def test_management_html_has_no_call_data(self):
        _, body = page('<!--SERVER_CONTENT-->', '/yonetim', '', [self.call()], [], True)
        self.assertNotIn(b'demo-test', body); self.assertIn('Yönetici oturumu gerekli'.encode(), body)
