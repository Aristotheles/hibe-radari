import unittest
from datetime import date
from hibe.aggregator.models import GrantOpportunity, canonical_url
from hibe.aggregator.collector import dedupe

class IdentitySafetyTests(unittest.TestCase):
    def item(self, title='Okul hibesi 2026', url='https://x.org/call?id=1', source='s', **kw):
        return GrantOpportunity(title,source,url,**kw)
    def test_query_ids_and_ref_are_preserved(self):
        a=self.item();b=self.item(url='https://x.org/call?id=2')
        self.assertEqual(len(dedupe([a,b])),2);self.assertNotEqual(a.id,b.id)
        self.assertEqual(canonical_url('https://x.org/call?ref=2&id=1&utm_x=3&empty='),'https://x.org/call?empty=&id=1&ref=2')
    def test_homepage_periods_and_titles_stay_separate(self):
        rows=[self.item(url='https://x.org/'),self.item('Okul hibesi 2027',url='https://x.org/'),self.item('Öğretmen kursu 2026',url='https://x.org/')]
        self.assertEqual(len(dedupe(rows)),3);self.assertEqual(len({x.id for x in rows}),3)
    def test_alias_chain_keeps_three_sources_and_date(self):
        a=self.item(source='official',url='https://x.org/call/1')
        b=self.item(source='b',url='https://b.org/news/1',original_url=a.source_url,original_url_evidence='Resmî başvuru',aggregator=True)
        c=self.item(source='c',url='https://c.org/news/1',original_url=b.source_url,original_url_evidence='Kaynak',aggregator=True,deadline=date(2026,11,30),deadline_evidence='Son başvuru 30 Kasım 2026')
        rows=dedupe([a,c,b]);self.assertEqual(len(rows),1)
        self.assertEqual(set(rows[0].seen_in),{'b','c'});self.assertEqual(len(rows[0].provenance),3)
        self.assertEqual(rows[0].deadline,date(2026,11,30));self.assertIn('30 Kasım',rows[0].deadline_evidence)
    def test_generic_alias_and_unverified_link_do_not_merge(self):
        a=self.item(url='https://x.org/');b=self.item(source='b',url='https://b.org/news/1',original_url=a.source_url,original_url_evidence='Resmî')
        self.assertEqual(len(dedupe([a,b])),2)
        a=self.item();b=self.item(source='b',url='https://b.org/news/1',original_url=a.source_url)
        self.assertEqual(len(dedupe([a,b])),2)
    def test_title_similarity_is_only_signal(self):
        a=self.item();b=self.item(url='https://y.org/call/1')
        rows=dedupe([a,b]);self.assertEqual(len(rows),2);self.assertTrue(rows[0].duplicate_candidates)
    def test_conflicting_dates_require_review_without_evidence_loss(self):
        a=self.item(deadline=date(2026,11,30),deadline_evidence='deadline 30 November 2026')
        b=self.item(source='b',deadline=date(2026,12,15),deadline_evidence='deadline 15 December 2026')
        row=dedupe([a,b])[0];self.assertTrue(row.deadline_review_required);self.assertEqual(row.relevance.verdict,'review')
        self.assertEqual({x['deadline'] for x in row.provenance},{'2026-11-30','2026-12-15'})
    def test_official_identity_and_application_paths(self):
        a=self.item(official_call_id='C1',identity_authority='authority',programme='p',application_path='school')
        b=self.item(url='https://y.org/call',source='b',official_call_id='C1',identity_authority='authority',programme='p',application_path='school')
        self.assertEqual(len(dedupe([a,b])),1)
        a=self.item(official_call_id='C1',identity_authority='authority',application_path='school')
        b=self.item(official_call_id='C1',identity_authority='authority',application_path='student')
        self.assertEqual(len(dedupe([a,b])),2);self.assertNotEqual(a.id,b.id)
    def test_missing_period_cannot_bridge_distinct_periods(self):
        a=self.item('Okul hibesi 2026',url='https://x.org/call/1')
        b=self.item('Okul hibesi',url=a.source_url,source='b')
        c=self.item('Okul hibesi 2027',url=a.source_url,source='c')
        self.assertEqual(len(dedupe([a,b,c])),2)

    def test_html_list_keeps_query_identity(self):
        from hibe.aggregator.html_cards import collect_list
        class Fetcher:
            def get_text(self, url):return '<a href="/call?id=1">Okul hibesi birinci çağrı</a><a href="/call?id=2">Okul hibesi ikinci çağrı</a>'
        rows=collect_list({'id':'s','url':'https://x.org/','link_pattern':'/call'},Fetcher(),date(2026,10,10))
        self.assertEqual(len(rows),2);self.assertEqual({x.source_url for x in rows},{'https://x.org/call?id=1','https://x.org/call?id=2'})
