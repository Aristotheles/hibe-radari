import unittest
from datetime import date
from hibe.eligibility import assess, YES, NO, UNKNOWN
from hibe.llm import extract_with_fallback, validate_evidence

TODAY=date(2026,10,10)
class EligibilitySafetyTests(unittest.TestCase):
    def row(self, text, verified=True):
        return {'title':'Çevre yarışması','description_short':text,'source_url':'https://official.org/call','official_source_verified':verified,'deadline':'2026-11-30','deadline_precision':'day','deadline_evidence':'Son başvuru 30 Kasım 2026'}
    def test_school_student_environment_competition_with_evidence(self):
        text='Türkiye başvuruları uygundur. Lise öğrencileri başvurabilir. 14-18 yaş. Ortak zorunluluğu yoktur. Bireysel başvuru yapılır.'
        a=assess(self.row(text),TODAY)
        self.assertEqual(a['type'],'competition');self.assertEqual(a['targets']['student_14_18']['status'],YES)
        self.assertTrue(a['targets']['student_14_18']['checks']['country']['evidence'])
    def test_university_only_and_ngo_only_are_not_school_eligible(self):
        for text in ['Yalnızca üniversite öğrencileri başvurabilir.','Yalnızca STK başvurabilir.']:
            a=assess(self.row(text),TODAY)
            self.assertEqual(a['targets']['school']['status'],NO)
            self.assertEqual(a['targets']['student_14_18']['status'],NO)
    def test_unverified_or_missing_country_never_becomes_definite(self):
        text='Lise öğrencileri başvurabilir. 14-18 yaş. Ortak zorunluluğu yoktur. Bireysel başvuru yapılır.'
        self.assertEqual(assess(self.row(text),TODAY)['targets']['student_14_18']['status'],UNKNOWN)
        self.assertEqual(assess(self.row('Türkiye başvuruları uygundur. '+text,False),TODAY)['targets']['student_14_18']['status'],UNKNOWN)
    def test_partial_age_and_conflicting_country_require_review(self):
        text='Türkiye başvuruları uygundur. Türkiye hariç. Lise öğrencileri başvurabilir. 16-18 yaş. Ortak zorunluluğu yoktur. Bireysel başvuru yapılır.'
        a=assess(self.row(text),TODAY);self.assertEqual(a['targets']['student_14_18']['status'],UNKNOWN)
    def test_date_uncertainty_and_deadline_evidence(self):
        r=self.row('Türkiye başvuruları uygundur. Devlet liseleri başvurabilir. Ortak zorunluluğu yoktur. Okul adına başvuru yapılır.')
        self.assertEqual(assess(r,TODAY)['targets']['school']['status'],YES)
        r['deadline_precision']='month';self.assertEqual(assess(r,TODAY)['targets']['school']['status'],UNKNOWN)
    def test_ai_fabricated_quote_is_unknown_and_failure_falls_back(self):
        src={'id':'s','call_id':'c','documents':[{'url':'https://official.org','hash':'h'}]}
        out={'paths':[{'conditions':[{'result':'saglandi','evidence':'Uydurma lise uygunluğu kanıtı'}]}]}
        self.assertEqual(validate_evidence(out,'Gerçek kaynak metni',src)['paths'][0]['conditions'][0]['result'],'bilinmiyor')
        class Broken:
            def extract(self,*args):raise ValueError('unavailable')
        result=extract_with_fallback(Broken(),'Gerçek duyuru başlığı',src,{})
        self.assertEqual(result['title'],'Gerçek duyuru başlığı');self.assertEqual(result['ai_status'],'unavailable')
        self.assertEqual(result['paths'][0]['conditions'][0]['result'],'bilinmiyor')

    def test_model_contradicts_quoted_exclusion_and_unknown_closure(self):
        src={'documents':[{'url':'https://official.org','hash':'h'}]}
        out={'official_status':'kapandi','paths':[{'conditions':[{'result':'saglandi','evidence':'Yalnızca üniversite öğrencileri başvurabilir'}]}]}
        result=validate_evidence(out,'Yalnızca üniversite öğrencileri başvurabilir',src)
        self.assertEqual(result['paths'][0]['conditions'][0]['result'],'bilinmiyor')
        self.assertEqual(result['official_status'],'bilinmiyor');self.assertTrue(result['ai_conflict'])
    def test_unproven_negative_condition_is_unknown(self):
        from hibe.domain import eligibility
        self.assertEqual(eligibility({'conditions':[{'result':'saglanmadi','evidence':None}]}),'belirsiz')

    def test_assessment_check_time_is_not_semantic_content_change(self):
        from hibe.aggregator.bridge import discovery_version
        r=self.row('Lise öğrencileri başvurabilir.');r['eligibility_assessment']=assess(r,TODAY)
        v=discovery_version(r)
        r['eligibility_assessment']['checked_at']='tomorrow'
        r['eligibility_assessment']['targets']['school']['checked_at']='tomorrow'
        self.assertEqual(v,discovery_version(r))

    def test_verified_url_alone_is_not_verified_conditions(self):
        r=self.row('Türkiye başvuruları uygundur. Devlet liseleri başvurabilir. Ortak zorunluluğu yoktur. Okul adına başvuru yapılır.',False)
        r['official_url_verified']=True
        self.assertEqual(assess(r,TODAY)['targets']['school']['status'],UNKNOWN)
    def test_ai_quote_is_attributed_to_the_actual_document(self):
        src={'documents':[{'url':'https://x.org/html','hash':'a'},{'url':'https://x.org/doc.pdf','hash':'b'}], 'document_texts':[{'url':'https://x.org/html','text':'Başlık'},{'url':'https://x.org/doc.pdf','text':'Devlet liseleri başvurabilir.'}]}
        out={'paths':[{'conditions':[{'result':'saglandi','evidence':'Devlet liseleri başvurabilir.'}]}]}
        self.assertEqual(validate_evidence(out,'Devlet liseleri başvurabilir.',src)['paths'][0]['conditions'][0]['evidence_url'],'https://x.org/doc.pdf')
