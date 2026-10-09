import unittest
from datetime import date
import httpx
from hibe.aggregator import eu_ft
from hibe.aggregator.net import Fetcher,FetchError

class EUPaginationTests(unittest.TestCase):
    def collect(self,pages,max_pages=3):
        self.requests=[]
        def response(request):
            page=int(request.url.params['pageNumber']);self.requests.append(page)
            return httpx.Response(200,json=pages[page-1])
        source={'id':'eu-ft','queries':[{'text':'school'}],'page_size':2,'max_pages':max_pages}
        fetcher=Fetcher(['api.tech.ec.europa.eu'],transport=httpx.MockTransport(response),delay=0)
        try:return eu_ft.collect(source,fetcher,date(2026,10,10))
        finally:fetcher.close()
    def row(self,identifier):
        return {'metadata':{'identifier':[identifier],'title':[identifier]}}
    def test_later_pages_and_string_total_are_collected(self):
        result=self.collect([{'totalResults':'3','results':[self.row('a'),self.row('b')]}, {'totalResults':3,'results':[self.row('c')]}])
        self.assertEqual([r.official_call_id for r in result],['a','b','c'])
        self.assertEqual(self.requests,[1,2])
    def test_repeated_capped_empty_and_bad_schema_fail(self):
        first={'totalResults':5,'results':[self.row('a'),self.row('b')]}
        cases=[([first,first],3),([first],1),([first,{'totalResults':5,'results':[]}],3),([{'totalResults':True,'results':[]}],3),([{}],3)]
        for pages,cap in cases:
            with self.subTest(pages=pages,cap=cap),self.assertRaises(FetchError):self.collect(pages,cap)
    def test_unknown_total_uses_short_final_page(self):
        rows=self.collect([{'results':[self.row('a'),self.row('b')]},{'results':[]}])
        self.assertEqual(len(rows),2)
    def test_explicit_zero_total_is_valid_but_missing_rows_is_not(self):
        self.assertEqual(self.collect([{'totalResults':0,'results':[]}]),[])
        with self.assertRaises(FetchError):self.collect([{'totalResults':2,'results':[]}])
