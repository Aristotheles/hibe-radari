import unittest
import httpx
from hibe.aggregator.net import Fetcher, FetchError

class NetworkSafetyTests(unittest.TestCase):
    def test_documented_public_api_permission_does_not_exempt_other_routes(self):
        calls=[]
        def handler(r):
            calls.append(str(r.url))
            return httpx.Response(403)
        policy={'terms_status':'allowed','checked_at':'2026-10-10',
            'evidence_url':'https://www.grants.gov/api/terms-conditions',
            'documented_api':'grants_gov_public'}
        f=Fetcher(['api.grants.gov'],transport=httpx.MockTransport(handler),delay=0,access_policy=policy)
        self.addCleanup(f.close)
        f._permission('https://api.grants.gov/v1/api/search2')
        self.assertEqual(calls,[])
        with self.assertRaises(FetchError):f._permission('https://api.grants.gov/private')
        self.assertEqual(calls,['https://api.grants.gov/robots.txt'])

    def client(self, handler, **kwargs):
        f = Fetcher(['safe.org', 'other.org'], transport=httpx.MockTransport(handler), delay=0, **kwargs)
        self.addCleanup(f.close)
        return f

    def test_foreign_redirect_receives_no_request(self):
        calls=[]
        def handler(r):
            calls.append(str(r.url)); return httpx.Response(302, headers={'location':'https://evil.org/x'})
        f=self.client(handler)
        with self.assertRaises(FetchError): f.get('https://safe.org/')
        self.assertEqual(calls,['https://safe.org/'])

    def test_private_dns_is_blocked_before_request(self):
        calls=[]
        f=self.client(lambda r:calls.append(r), resolver=lambda *a,**k:[(2,1,6,'',('127.0.0.1',443))])
        with self.assertRaises(FetchError): f.get('https://safe.org/')
        self.assertEqual(calls,[])

    def test_dns_is_pinned_with_correct_tls_name(self):
        requests=[]
        def handler(r): requests.append(r); return httpx.Response(200,content=b'ok')
        f=self.client(handler,resolver=lambda *a,**k:[(2,1,6,'',('8.8.8.8',443))])
        self.assertEqual(f.get_text('https://safe.org/path?id=1'),'ok')
        self.assertEqual(str(requests[0].url),'https://8.8.8.8/path?id=1')
        self.assertEqual(requests[0].headers['host'],'safe.org')
        self.assertEqual(requests[0].extensions['sni_hostname'],'safe.org')

    def test_429_waits_once_and_403_does_not_retry(self):
        calls=[]; sleeps=[]
        def handler(r):
            calls.append(r); return httpx.Response(429,headers={'Retry-After':'2'}) if len(calls)==1 else httpx.Response(200,content=b'ok')
        f=self.client(handler,sleep=sleeps.append)
        self.assertEqual(f.get_text('https://safe.org/'),'ok'); self.assertEqual(sleeps,[2])
        calls.clear()
        f=self.client(lambda r:(calls.append(r) or httpx.Response(403)))
        with self.assertRaises(FetchError): f.get('https://safe.org/')
        self.assertEqual(len(calls),1)

    def test_304_reuses_cached_bytes_and_condition_headers(self):
        requests=[]
        def handler(r):
            requests.append(r)
            return httpx.Response(200,content=b'old',headers={'ETag':'"v1"','Last-Modified':'Wed, 01 Oct 2025 00:00:00 GMT'}) if len(requests)==1 else httpx.Response(304)
        f=self.client(handler)
        self.assertEqual(f.get_text('https://safe.org/'),'old')
        self.assertEqual(f.get_text('https://safe.org/'),'old')
        self.assertEqual(requests[1].headers['if-none-match'],'"v1"')
        self.assertIn('if-modified-since',requests[1].headers)

    def test_redirect_base_is_preserved_after_conditional_cache_and_restart(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            def initial(r):
                return httpx.Response(302,headers={'Location':'/V2/default.aspx'}) if r.url.path=='/' else httpx.Response(200,text='<a href="call.aspx">Teacher grant application</a>',headers={'ETag':'"v1"'})
            f=self.client(initial,cache_dir=tmp)
            self.assertEqual(str(f.get('https://safe.org/').request.url),'https://safe.org/V2/default.aspx')
            g=self.client(lambda r:httpx.Response(304),cache_dir=tmp)
            response=g.get('https://safe.org/')
            self.assertEqual(str(response.request.url),'https://safe.org/V2/default.aspx')

    def test_stream_size_limit_stops_before_whole_download(self):
        reads=[]
        class Stream(httpx.SyncByteStream):
            def __iter__(self):
                for i in range(100):
                    reads.append(i); yield b'x'*16384
        f=self.client(lambda r:httpx.Response(200,stream=Stream()),max_bytes=20000)
        with self.assertRaises(FetchError): f.get('https://safe.org/')
        self.assertLess(len(reads),100)

    def test_declared_size_rejected_without_reading(self):
        class Stream(httpx.SyncByteStream):
            def __iter__(self): raise AssertionError('must not read')
        f=self.client(lambda r:httpx.Response(200,headers={'Content-Length':'999'},stream=Stream()),max_bytes=50)
        with self.assertRaises(FetchError): f.get('https://safe.org/')


    def test_cache_survives_fetcher_restart(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            f=self.client(lambda r:httpx.Response(200,content=b'saved',headers={'ETag':'"v"'}), cache_dir=tmp)
            f.get('https://safe.org/')
            seen=[]
            def handler(r): seen.append(r); return httpx.Response(304)
            g=self.client(handler,cache_dir=tmp)
            self.assertEqual(g.get_text('https://safe.org/'),'saved')
            self.assertEqual(seen[0].headers['if-none-match'],'"v"')

    def test_unreviewed_permission_makes_no_request(self):
        seen=[]
        f=self.client(lambda r:seen.append(r),access_policy={'terms_status':'unreviewed'})
        with self.assertRaises(FetchError) as cm:f.get('https://safe.org/')
        self.assertEqual(cm.exception.kind,'permission');self.assertEqual(seen,[])

    def test_robots_blocks_resource_and_respects_crawl_delay(self):
        seen=[]; sleeps=[]
        def handler(r):
            seen.append(str(r.url))
            return httpx.Response(200,content=b'User-agent: *\nDisallow: /private\nCrawl-delay: 3\n' if r.url.path=='/robots.txt' else b'ok')
        policy={'terms_status':'allowed','evidence_url':'https://safe.org/terms','checked_at':'2026-10-10'}
        f=self.client(handler,access_policy=policy,sleep=sleeps.append)
        with self.assertRaises(FetchError):f.get('https://safe.org/private')
        self.assertEqual(seen,['https://safe.org/robots.txt'])
        self.assertEqual(f.get_text('https://safe.org/public'),'ok')
        self.assertGreaterEqual(f.delay,3)
        self.assertTrue(sleeps)


    def test_compressed_response_is_not_decoded_twice(self):
        import gzip
        f=self.client(lambda r:httpx.Response(200,content=gzip.compress(b'hello'),headers={'Content-Encoding':'gzip'}))
        self.assertEqual(f.get_text('https://safe.org/'),'hello')


class RobotsLiveRegressionTests(unittest.TestCase):
    def client(self,body,mime='text/plain'):
        import httpx
        from hibe.aggregator.net import Fetcher
        transport=httpx.MockTransport(lambda r:httpx.Response(200,text=body if r.url.path=='/robots.txt' else 'ok',headers={'content-type':mime}))
        return Fetcher(['x.org'],transport=transport,delay=0,access_policy={'terms_status':'allowed','evidence_url':'https://x.org/terms','checked_at':'2026-10-10'})
    def test_html_200_robots_is_not_permission(self):
        from hibe.aggregator.net import FetchError
        client=self.client('<html>404</html>','text/html')
        try:
            with self.assertRaises(FetchError):client.get('https://x.org/call')
            self.assertEqual(client.calls,1)
        finally:client.close()
    def test_wildcard_query_disallow_blocks_before_fetch(self):
        from hibe.aggregator.net import FetchError
        client=self.client('User-agent: *\nDisallow: /*?*b_offset*')
        try:
            with self.assertRaises(FetchError):client.get('https://x.org/browse?b_offset=10')
            self.assertEqual(client.calls,1)
        finally:client.close()

    def test_percent_encoded_query_cannot_bypass_robots(self):
        from hibe.aggregator.net import FetchError
        client=self.client('User-agent: *\nDisallow: /*?*b_offset*')
        try:
            with self.assertRaises(FetchError):client.get('https://x.org/browse?%62_offset=10')
            self.assertEqual(client.calls,1)
        finally:client.close()
