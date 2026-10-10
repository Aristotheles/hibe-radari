import unittest
from unittest.mock import Mock
import httpx
from hibe.review_batch import DailyExtractor, document_text, review_batch
from hibe.store import MemoryStore


class ReviewBatchTests(unittest.TestCase):
    def test_daily_limit_survives_new_wrapper_and_failure(self):
        store = MemoryStore()
        model = Mock(model='model', extract=Mock(side_effect=RuntimeError('failed')))
        with self.assertRaises(RuntimeError):
            DailyExtractor(store, model, limit=1).extract('text',{}, {})
        with self.assertRaises(ValueError):
            DailyExtractor(store, model, limit=1).extract('text',{}, {})
        self.assertEqual(model.extract.call_count,1)

    def test_feed_is_not_accepted_as_call_document(self):
        with self.assertRaises(ValueError):
            document_text(httpx.Response(200,headers={'content-type':'application/rss+xml'},content=b'<rss/>'))

    def test_document_limit_does_not_silently_truncate(self):
        with self.assertRaises(ValueError):
            document_text(httpx.Response(200,headers={'content-type':'text/html'},text='<main>'+('a'*48001)+'</main>'))

    def test_unreviewed_source_never_fetches(self):
        store=MemoryStore()
        store.put('calls','c',{'id':'c','title':'Teacher grant','source_id':'s'})
        factory=Mock()
        result=review_batch(store,{'sources':[{'id':'s','access_policy':{'terms_status':'unreviewed'}}]},Mock(model='model'),{},fetcher_factory=factory)
        factory.assert_not_called()
        self.assertEqual(result['results'][0]['status'],'permission_review_required')
        self.assertFalse(result['publication_approved'])
