import unittest
from unittest.mock import Mock
import httpx
from hibe.review_batch import DailyExtractor, document_text, review_batch
from hibe.store import MemoryStore


class ReviewBatchTests(unittest.TestCase):
    def test_existing_feed_record_reviews_detail_without_mutating_identity(self):
        from unittest.mock import patch
        store = MemoryStore()
        call = {'id':'existing', 'title':'Teacher opportunity', 'source_id':'eurodesk',
                'source_url':'https://programmes.eurodesk.eu/rss',
                'source_entry_id':'https://programmes.eurodesk.eu/19776'}
        store.put('calls', 'existing', call)
        source = {'id':'eurodesk', 'allowed_hosts':['programmes.eurodesk.eu'],
                  'entry_url_template':'https://programmes.eurodesk.eu/en/programme/{entry_id}/eu',
                  'access_policy':{'terms_status':'allowed'}}
        client = Mock()
        client.get.return_value = httpx.Response(200, headers={'content-type':'text/html'}, text='<main>Teacher conditions</main>')
        with patch('hibe.review_batch.classify', return_value={'group':'candidate'}), patch('hibe.review_batch.prepare_proposal', return_value={'status':'evidence_review_required'}) as prepare:
            review_batch(store, {'sources':[source]}, Mock(model='model'), {}, fetcher_factory=Mock(return_value=client))
        client.get.assert_called_once_with('https://programmes.eurodesk.eu/en/programme/19776/eu')
        self.assertEqual(prepare.call_args.args[2][0]['url'], client.get.call_args.args[0])
        self.assertEqual(store.get('calls','existing'), call)

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
