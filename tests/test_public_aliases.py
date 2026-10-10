import copy
import unittest
from datetime import date
from hibe.domain import public_calls,version

class PublicAliasTests(unittest.TestCase):
 def call(self,ident,url,**changes):
  c={'id':ident,'title':'Scholarship','summary':'', 'source_id':'official','source_url':url,'themes':[],
   'deadline':'2026-11-30','official_status':'acik','opportunity_type':'scholarship','paths':[],
   'documents':[{'url':'https://www.ab.gov.tr/application-form.pdf','hash':'a'},{'url':'https://www.ab.gov.tr/basvuru-form.pdf','hash':'b'}]}
  c.update(changes);c['approval']={'reviewed':True,'version':version(c)};return c
 def test_verified_aliases_show_once_without_deleting_records(self):
  calls=[self.call('a','https://www.ab.gov.tr/123.html'),self.call('b','https://www.ab.gov.tr/scholarship_123.html')]
  before=copy.deepcopy(calls)
  self.assertEqual(len(public_calls(calls,date(2026,10,10))),1)
  self.assertEqual(calls,before)
 def test_different_periods_phases_and_documents_do_not_merge(self):
  a=self.call('a','https://www.ab.gov.tr/123.html')
  for changes in ({'deadline':'2027-11-30'},{'application_path':'Second phase'},
    {'documents':[{'url':'https://www.ab.gov.tr/application-form.pdf','hash':'different'},{'url':'https://www.ab.gov.tr/basvuru-form.pdf','hash':'b'}]}):
   b=self.call('b','https://www.ab.gov.tr/scholarship_123.html',**changes)
   self.assertEqual(len(public_calls([a,b],date(2026,10,10))),2)
