import unittest
from hibe.store import MemoryStore
from hibe.domain import version
from hibe.verified_review import commit_verified_review


class VerifiedReviewTests(unittest.TestCase):
    def setUp(self):
        self.store=MemoryStore()
        self.call={'id':'call','source_id':'source','title':'School competition','summary':'Summary',
            'themes':[],'paths':[{'role':'belirsiz','conditions':[]}],
            'documents':[{'url':'https://official.example/call','hash':'hash'}],
            'deadline':'2099-01-04','deadline_precision':'day','deadline_evidence':'4 January 2099',
            'deadline_source_url':'https://official.example/call','official_status':'acik',
            'official_source_verified':True}
        self.store.put('calls','call',self.call)
    def test_invented_date_cannot_be_approved(self):
        with self.assertRaises(ValueError):
            commit_verified_review(self.store,'call',self.call,version(self.call),{'https://official.example/call':'No deadline specified.'})
        self.assertNotIn('approval',self.store.get('calls','call'))
    def test_changed_version_is_rejected(self):
        with self.assertRaises(ValueError):
            commit_verified_review(self.store,'call',self.call,'old-version',{})
