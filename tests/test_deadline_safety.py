import unittest
from datetime import date
from hibe.aggregator.textutil import deadline_details, find_deadline, fold

class DeadlineSafetyTests(unittest.TestCase):
    def test_start_is_not_deadline(self):
        text="Başvurular 1 Kasım'da başlar, son başvuru 30 Kasım'dır"
        self.assertEqual(find_deadline(text,date(2026,10,10))[0],date(2026,11,30))
        self.assertIsNone(find_deadline('Başvurular 1 Kasım 2026 tarihinde başlar',date(2026,10,10))[0])
    def test_iso_and_closing_after_date(self):
        for text in ['Son başvuru: 2026-11-30','Başvurular 05.11.2026 tarihinde kapanacaktır']:
            self.assertIsNotNone(find_deadline(text,date(2026,10,10))[0])
    def test_month_is_not_invented_day(self):
        d=deadline_details('Son başvuru Kasım 2026',date(2026,10,10))
        self.assertIsNone(d['value']);self.assertEqual(d['precision'],'month');self.assertEqual(d['month'],'2026-11')
    def test_all_turkish_months(self):
        for i,month in enumerate(['Ocak','Şubat','Mart','Nisan','Mayıs','Haziran','Temmuz','Ağustos','Eylül','Ekim','Kasım','Aralık'],1):
            self.assertEqual(find_deadline('Son başvuru 15 '+month+' 2027',date(2026,10,10))[0],date(2027,i,15))
    def test_decomposed_turkish_i(self):
        self.assertEqual(fold('İ I i\u0307'),'i i i')

    def test_missing_or_month_only_does_not_erase_exact_date(self):
        from hibe.aggregator.models import GrantOpportunity
        item=GrantOpportunity('Okul','s','https://x.org',deadline=date(2026,11,30),deadline_evidence='Son başvuru 30 Kasım 2026')
        item.apply_deadline('Son başvuru Aralık 2026',date(2026,10,10))
        self.assertEqual(item.deadline,date(2026,11,30))
        item.apply_deadline('Bilgi bulunamadı',date(2026,10,10))
        self.assertEqual(item.deadline,date(2026,11,30))
    def test_explicit_revision_preserves_history(self):
        from hibe.aggregator.models import GrantOpportunity
        item=GrantOpportunity('Okul','s','https://x.org',deadline=date(2026,11,30),deadline_evidence='Son başvuru 30 Kasım 2026')
        item.apply_deadline('Son başvuru 15 Aralık 2026',date(2026,10,10))
        self.assertEqual(item.deadline,date(2026,12,15));self.assertEqual(item.deadline_history[0]['value'],'2026-11-30')
    def test_month_metadata_and_inferred_year_are_not_exact_dates(self):
        from hibe.aggregator.models import GrantOpportunity
        item=GrantOpportunity('Okul','s','https://x.org')
        item.apply_deadline('Son başvuru Kasım 2026',date(2026,10,10))
        self.assertIsNone(item.deadline);self.assertEqual(item.deadline_precision,'month')
        self.assertEqual(item.deadline_month,'2026-11')
        item.apply_deadline('Son başvuru 30 Kasım',date(2026,10,10))
        self.assertIsNone(item.deadline);self.assertTrue(item.deadline_year_inferred)

    def test_feed_does_not_promote_missing_year(self):
        from hibe.aggregator.feeds import collect
        class Response: content=b'<rss version="2.0"><channel><title>Feed</title><link>https://x.org</link><description>Calls</description><item><title>School grant</title><link>https://x.org/a</link><description>Deadline: 30 November</description></item></channel></rss>'
        class Fetcher:
            def get(self, url): return Response()
        item=collect({'id':'s','url':'https://x.org/rss'},Fetcher(),date(2026,10,10))[0]
        self.assertIsNone(item.deadline);self.assertTrue(item.deadline_year_inferred)

    def test_uncertain_date_has_no_countdown_or_calendar(self):
        from hibe.aggregator.site import prepare, when_html, ics
        row={'id':'x','title':'School grant','deadline':'2026-11-01','deadline_precision':'month','deadline_month':'2026-11','relevance':{'audience':[]}}
        item=prepare({'accepted':[row]},date(2026,10,10))[0]
        self.assertIsNone(item['deadline']);self.assertIn('gün bilinmiyor',when_html(item,date(2026,10,10)))
        with self.assertRaises(ValueError):ics(row,'20261010T000000Z')

    def test_decomposed_text_evidence_keeps_original_date(self):
        text='İi\u0307 '*40+'Son başvuru 30 Kasım 2026'
        details=deadline_details(text,date(2026,10,10))
        self.assertIn('30 Kasım 2026',details['evidence'])

    def test_utc_stamp_respects_offset_and_daylight_savings(self):
        from hibe.aggregator.site import utc_stamp
        self.assertEqual(utc_stamp('2026-10-10T17:00:00'),'20261010T140000Z')
        self.assertEqual(utc_stamp('2026-03-29T03:30:00+02:00'),'20260329T013000Z')
        self.assertEqual(utc_stamp('2026-03-29T01:30:00Z'),'20260329T013000Z')

    def test_old_unknown_date_is_review_not_archived(self):
        from hibe.aggregator.models import GrantOpportunity
        from hibe.aggregator.relevance import RelevanceFilter
        item=GrantOpportunity('4004 Doğa Eğitimi ve Bilim Okulları Çağrısı','s','https://x.org/a',published_at=date(2024,1,1))
        self.assertEqual(RelevanceFilter().evaluate(item,date(2026,10,10)).verdict,'review')

    def test_multiple_phases_preserve_candidates_and_need_review(self):
        from hibe.aggregator.models import GrantOpportunity
        item=GrantOpportunity('Okul','s','https://x.org/a')
        item.apply_deadline('Birinci aşama son başvuru 30 Kasım 2026. İkinci aşama son başvuru 15 Aralık 2026.',date(2026,10,10))
        self.assertEqual(item.deadline,date(2026,11,30));self.assertEqual(len(item.deadline_candidates),2)
        self.assertTrue(item.deadline_review_required)
