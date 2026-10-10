import unittest,httpx
from unittest.mock import Mock
from datetime import date
from hibe.aggregator.grants_gov import collect,detail_text

class GrantsGovTests(unittest.TestCase):
    def test_public_text_keeps_paragraphs_as_evidence_instead_of_json_escapes(self):
        f=Mock();f.request.return_value.json.return_value={'errorcode':0,'data':{'id':123,'synopsis':{'applicantEligibilityDesc':'Foreign ("non-US") organizations\nare eligible to apply.'}}}
        text=detail_text({'detail_url':'https://api.grants.gov/v1/api/fetchOpportunity'},f,'123')
        self.assertIn('Foreign ("non-US") organizations are eligible to apply.',text)
        self.assertNotIn('\\"non-US\\"',text)
    def setUp(self):
        self.source={'id':'gov','queries':['school'],'page_size':1,'max_pages':3,'search_url':'https://api.grants.gov/v1/api/search2','detail_url':'https://api.grants.gov/v1/api/fetchOpportunity','entry_url_template':'https://www.grants.gov/search-results-detail/{entry_id}'}
    def response(self,data):return httpx.Response(200,json={'errorcode':0,'token':'secret-response-token','data':data})
    def test_pagination_and_real_id_date_without_copying_provider_token(self):
        f=Mock();f.request.side_effect=[self.response({'hitCount':2,'oppHits':[{'id':'1','title':'School grant','closeDate':'10/30/2026'}]}),self.response({'hitCount':2,'oppHits':[{'id':'2','title':'Teacher grant'}]})]
        rows=collect(self.source,f,date.today())
        self.assertEqual(len(rows),2);self.assertEqual(rows[0].deadline.isoformat(),'2026-10-30')
        self.assertNotIn('token',str(rows[0].to_dict()))
        self.assertEqual(f.request.call_args_list[1].kwargs['json']['startRecordNum'],1)
    def test_detail_strips_contacts_and_token_and_rejects_mismatched_id(self):
        f=Mock();f.request.return_value=self.response({'id':1,'synopsis':{'synopsisDesc':'<p>School projects</p>','agencyContactEmail':'private@example.org'}})
        text=detail_text(self.source,f,'1');self.assertIn('School projects',text);self.assertNotIn('private@example.org',text);self.assertNotIn('secret-response-token',text)
        with self.assertRaises(ValueError):detail_text(self.source,f,'2')
        with self.assertRaises(ValueError):detail_text(self.source,f,'../../evil')
