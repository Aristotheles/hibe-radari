import unittest
from datetime import date
from unittest.mock import Mock
import httpx
from hibe.aggregator.discovery import collect

class SourceDiscoveryTests(unittest.TestCase):
    def test_separate_real_programme_phases_on_same_page_are_not_merged(self):
        pages=[{'url':'https://example.org/apply','title':title,'application_path':title} for title in ('First Grant','Second Grant')]
        f=self.fetcher();f.get_text.return_value='<h1>First Grant</h1><h2>Second Grant</h2>'
        items=collect(dict(self.source(),programme_pages=pages),f,date.today())
        self.assertEqual(len(items),2)
        self.assertEqual({i.application_path for i in items},{'First Grant','Second Grant'})
    def test_dedicated_programme_name_requires_real_public_page_evidence(self):
        source=dict(self.source(),programme_pages=[{'url':'https://example.org/apply','title':'First Conservation Grant','application_path':'First Conservation Grant'}])
        f=self.fetcher();f.get_text.return_value='<h1>First Conservation Grant</h1><p>Applications may be submitted at any time.</p>'
        items=collect(source,f,date.today())
        self.assertEqual(len(items),1);self.assertIsNone(items[0].deadline)
        self.assertEqual(items[0].categories,['programme_overview'])
        f.get_text.return_value='<h1>No such programme</h1>'
        with self.assertRaises(ValueError):collect(source,f,date.today())
    def fetcher(self):
        f=Mock()
        f.get.side_effect=lambda url:httpx.Response(200,text=f.get_text(url),request=httpx.Request('GET',url))
        return f
    def source(self):
        return {'id':'official','url':'https://example.org/','allowed_hosts':['example.org'],'max_pages':3}

    def test_observed_navigation_reaches_calls_without_inventing_routes(self):
        f=self.fetcher();f.get_text.side_effect=[
            '<a href="/grants">Grants</a><a href="/about">About our organisation</a>',
            '<a href="/grants/teachers-2027">Teacher innovation grant 2027</a><a href="/grants/teachers-2027#apply">Teacher innovation grant 2027</a>']
        items=collect(self.source(),f,date.today())
        self.assertEqual(len(items),1)
        self.assertEqual(items[0].source_url,'https://example.org/grants/teachers-2027')
        self.assertIsNone(items[0].deadline)
        self.assertEqual(items[0].source_entry_id,items[0].source_url)
        self.assertEqual(f.get_text.call_count,2)

    def test_foreign_and_unsafe_links_and_generic_navigation_do_not_become_calls(self):
        f=self.fetcher();f.get_text.return_value='<a href="https://other.org/call">Teacher grant open for applications</a><a href="javascript:alert(1)">Teacher competition 2027</a><a href="https://u:p@example.org/c">Teacher competition 2027</a><a href="/news">Current announcements</a>'
        self.assertEqual(collect(dict(self.source(),max_pages=1),f,date.today()),[])

    def test_same_title_different_calls_remain_distinct_and_empty_is_empty(self):
        f=self.fetcher();f.get_text.return_value='<a href="/c1">Teacher innovation grant</a><a href="/c2">Teacher innovation grant</a>'
        self.assertEqual(len(collect(self.source(),f,date.today())),2)
        f.get_text.return_value='<h1>Service temporarily unavailable</h1>'
        self.assertEqual(collect(self.source(),f,date.today()),[])

    def test_page_and_item_budget_are_bounded(self):
        f=self.fetcher();f.get_text.return_value='<a href="/c1">School competition 2027</a><a href="/c2">School competition 2028</a>'
        self.assertEqual(len(collect(dict(self.source(),max_items=1),f,date.today())),1)
        self.assertEqual(f.get_text.call_count,1)

    def test_webforms_and_redirect_relative_paths_preserve_public_announcements(self):
        f=Mock();f.get.return_value=httpx.Response(200,text='<form action="/login"><input name="password"><a href="call.aspx?id=1">Öğretmen eğitimi başvuruları</a></form>',request=httpx.Request('GET','https://example.org/V2/default.aspx'))
        items=collect(dict(self.source(),max_pages=1),f,date.today())
        self.assertEqual(items[0].source_url,'https://example.org/V2/call.aspx?id=1')
        self.assertEqual(f.get.call_count,1)
        f.post.assert_not_called()

    def test_official_language_selector_follows_observed_english_link(self):
        f=Mock()
        f.get.side_effect=[httpx.Response(200,text='<a href="/index_en" hreflang="en">en English</a>',request=httpx.Request('GET','https://example.org/select-language')),
            httpx.Response(200,text='<a href="/call">Call for school proposals 2027</a>',request=httpx.Request('GET','https://example.org/index_en'))]
        items=collect(self.source(),f,date.today())
        self.assertEqual(len(items),1)
        self.assertEqual(f.get.call_args_list[1].args[0],'https://example.org/index_en')
