import copy
import tempfile
import unittest
from pathlib import Path
from datetime import date
from hibe.store import MemoryStore, SQLiteStore
from hibe.service import Service
from hibe.domain import version
from hibe.aggregator.bridge import persist_report, publication_report

ADMIN={'uid':'admin','email_verified':True}
TODAY=date(2026,10,10)

class DiscoveryBridgeTests(unittest.TestCase):
    def test_corrected_detail_route_keeps_same_entry_without_duplicate_call(self):
        self.row.update(source_entry_id='https://x.org/123', identity_authority='s')
        persist_report(self.report, self.store)
        updated = copy.deepcopy(self.report)
        updated['accepted'][0].update(id='new-route', source_url='https://x.org/en/programme/123/eu')
        persist_report(updated, self.store)
        self.assertEqual(len(self.store.all('calls')), 1)
        self.assertEqual(self.store.get('discoveries','new-route')['call_id'], 'abc')
        different = copy.deepcopy(updated)
        different['accepted'][0].update(id='different-entry', source_entry_id='https://x.org/456')
        persist_report(different, self.store)
        self.assertEqual(len(self.store.all('calls')), 2)

    def setUp(self):
        self.store=MemoryStore();self.service=Service(self.store,'admin',today=lambda:TODAY)
        self.row={'id':'abc','title':'Okul çevre yarışması','source_id':'s','source_url':'https://x.org/call/1','organization':'Kurum','description_short':'Kaynak açıklaması','deadline':'2026-11-30','deadline_precision':'day','deadline_evidence':'Son başvuru 30 Kasım 2026','relevance':{'verdict':'accept','reasons':[],'audience':['school']}}
        self.report={'generated_at':'2026-10-10T00:00:00Z','today':str(TODAY),'run_status':'success','sources':[{'id':'s','organization':'Kurum','health':'success','error':None,'fetched':1,'enriched':0,'requests':1}],'accepted':[self.row],'counts':{}}
    def reviewed(self):
        c=self.store.get('calls','abc');c.update(summary='Okullar için çevre yarışması. Başvuru koşullarını resmî duyurudan inceleyin.',official_url='https://x.org/call/1',official_url_verified=True)
        return self.service.save(ADMIN,c)
    def test_unapproved_then_current_approval_publishes(self):
        persist_report(self.report,self.store)
        self.assertFalse(self.service.public());self.assertFalse(publication_report(self.report,self.store,TODAY)['accepted'])
        c=self.store.get('calls','abc')
        with self.assertRaises(ValueError):self.service.approve(ADMIN,'abc',version(c))
        c=self.reviewed();self.service.approve(ADMIN,'abc',c['version'])
        self.assertEqual(len(self.service.public()),1)
        self.assertEqual(len(publication_report(self.report,self.store,TODAY)['review']),1)
    def test_identical_rescan_keeps_approval_but_change_revokes(self):
        persist_report(self.report,self.store);c=self.reviewed();self.service.approve(ADMIN,'abc',c['version'])
        r=copy.deepcopy(self.report);r['accepted'][0]['deadline_checked_at']='new';persist_report(r,self.store)
        self.assertEqual(len(self.service.public()),1)
        r['accepted'][0]['deadline']='2026-12-01';persist_report(r,self.store)
        self.assertFalse(self.service.public());self.assertTrue(self.store.get('calls','abc')['discovery_changes_pending'])
        with self.assertRaises(ValueError):self.service.approve(ADMIN,'abc',version(self.store.get('calls','abc')))
        with self.assertRaises(ValueError):self.service.save(ADMIN,c)
    def test_verified_manual_call_is_included_without_aggregator_flag(self):
        persist_report(self.report,self.store)
        c=self.reviewed()
        c.pop('from_aggregator',None)
        self.store.put('calls','abc',c)
        self.service.approve(ADMIN,'abc',version(c))
        published=publication_report(self.report,self.store,TODAY)
        self.assertEqual([row['id'] for row in published['review']],['abc'])
    def test_missing_data_and_empty_rescan_do_not_delete(self):
        persist_report(self.report,self.store)
        r=copy.deepcopy(self.report);r['accepted'][0]['deadline']=None;r['accepted'][0]['deadline_precision']='unknown';r['accepted'][0]['deadline_evidence']=None
        persist_report(r,self.store)
        self.assertEqual(self.store.get('discoveries','abc')['observation']['deadline'],'2026-11-30')
        persist_report(dict(self.report,accepted=[],run_status='failed'),self.store)
        self.assertEqual(len(self.store.all('calls')),1)
    def test_revocation_and_authorization(self):
        persist_report(self.report,self.store);c=self.reviewed();self.service.approve(ADMIN,'abc',c['version'])
        with self.assertRaises(PermissionError):self.service.revoke({'uid':'other','email_verified':True},'abc')
        self.service.revoke(ADMIN,'abc');self.assertFalse(self.service.public())
    def test_sqlite_survives_reopen_and_history_is_retained(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'existing.db';store=SQLiteStore(path);persist_report(self.report,store);store.db.close()
            store=SQLiteStore(path);self.assertEqual(len(store.all('discoveries')),1)
            r=copy.deepcopy(self.report);r['accepted'][0]['title']='Değişen çağrı';persist_report(r,store)
            self.assertEqual(len(store.get('discoveries','abc')['history']),1);store.db.close()

    def test_publication_uses_curated_summary_and_verified_official_link(self):
        from hibe.aggregator.site import build
        persist_report(self.report,self.store)
        c=self.store.get('calls','abc');c.update(summary='Editörün özgün kısa açıklaması',official_url='https://official.org/call/1',official_url_verified=True,documents=[{'url':'https://official.org/call/1','hash':'reviewed-evidence'}],original_url='https://unverified.org/apply')
        c=self.service.save(ADMIN,c);self.service.approve(ADMIN,'abc',c['version'])
        report=publication_report(self.report,self.store,TODAY)
        self.assertEqual(report['review'][0]['description_short'],c['summary'])
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'public';build(report,out,TODAY)
            html=(out/'ilan/abc.html').read_text(encoding='utf-8')
            self.assertIn('https://official.org/call/1',html);self.assertNotIn('https://unverified.org/apply',html)
    def test_reject_invalid_batch_before_any_write(self):
        r=copy.deepcopy(self.report);r['accepted'].append({'title':'bad'})
        with self.assertRaises(ValueError):persist_report(r,self.store)
        self.assertFalse(self.store.all('discoveries'))

    def test_later_manual_id_collision_keeps_earlier_approval_and_store_unchanged(self):
        persist_report(self.report,self.store);c=self.reviewed();self.service.approve(ADMIN,'abc',c['version'])
        self.store.put('calls','manual-id',{'id':'manual-id','title':'Manuel kayıt','summary':'Editör verisi'})
        before=copy.deepcopy(self.store.data)
        r=copy.deepcopy(self.report);r['accepted'][0]['deadline']='2026-12-01'
        r['accepted'].append(dict(self.row,id='manual-id',source_url='https://x.org/call/2'))
        with self.assertRaises(ValueError):persist_report(r,self.store)
        self.assertEqual(self.store.data,before)
        self.assertTrue(self.store.get('calls','abc')['approval'])

    def test_duplicate_batch_id_and_bad_health_fail_before_any_write(self):
        duplicate=copy.deepcopy(self.report);duplicate['accepted'].append(dict(self.row,title='Farklı çağrı'))
        invalid_health=copy.deepcopy(self.report);invalid_health['sources']=[{'health':'failed'}]
        for report in (duplicate,invalid_health):
            with self.subTest(report=report):
                with self.assertRaises(ValueError):persist_report(report,self.store)
                self.assertEqual(self.store.data,{})

    def test_legacy_call_id_and_curated_fields_are_kept(self):
        old=dict(self.row,id='old-call',summary='Eski editör özeti',themes=[],paths=[],documents=[{'url':self.row['source_url'],'hash':'document-hash'}],official_status='bilinmiyor')
        self.store.put('calls','old-call',old)
        persist_report(self.report,self.store)
        self.assertEqual(len(self.store.all('calls')),1)
        call=self.store.get('calls','old-call');self.assertEqual(call['summary'],'Eski editör özeti')
        self.assertEqual(self.store.get('discoveries','abc')['call_id'],'old-call')

    def test_batch_does_not_rescan_all_calls_for_every_new_record(self):
        class CountingStore(MemoryStore):
            scans=0
            def all(self,kind):
                if kind=='calls':self.scans+=1
                return super().all(kind)
        store=CountingStore();report=copy.deepcopy(self.report)
        report['accepted']=[dict(self.row,id=f'new-{i}',title=f'Ayrı çağrı {i}',source_url=f'https://x.org/call/{i}') for i in range(80)]
        persist_report(report,store)
        self.assertEqual(store.scans,1)
        self.assertEqual(len(store.all('discoveries')),80)
        self.assertEqual(len(store.all('calls')),80)

    def test_distinct_feed_guids_are_not_remerged_by_legacy_title_url_matching(self):
        report=copy.deepcopy(self.report)
        report['accepted']=[dict(self.row,id=ident,source_url='https://x.org/rss',source_entry_id=guid,identity_authority='source') for ident,guid in (('abc','guid-1'),('def','guid-2'))]
        persist_report(report,self.store)
        self.assertEqual(len(self.store.all('calls')),2)
        self.assertEqual(self.store.get('discoveries','abc')['call_id'],'abc')
        self.assertEqual(self.store.get('discoveries','def')['call_id'],'def')

    def test_live_feed_same_title_url_guid_evidence_keeps_both_records(self):
        import json
        from hibe.aggregator.models import GrantOpportunity
        fixture=json.loads((Path(__file__).parent/'fixtures/aggregator/duplicate_guid_live_evidence_20261010.json').read_text('utf-8'))
        report=copy.deepcopy(self.report);report['accepted']=[]
        for entry in fixture['entries']:
            row=dict(entry,title=fixture['title'])
            fields={k:v for k,v in row.items() if k!='id'}
            self.assertEqual(GrantOpportunity(**fields).id,row['id'])
            report['accepted'].append(row)
        persist_report(report,self.store)
        self.assertEqual(len(self.store.all('calls')),len(fixture['entries']))
        for entry in fixture['entries']:
            self.assertEqual(self.store.get('discoveries',entry['id'])['call_id'],entry['id'])

    def test_legacy_alias_candidates_use_current_record_not_stale_index_copy(self):
        old=dict(self.row,id='old-call',summary='Eski editör özeti',themes=[],paths=[],documents=[{'url':self.row['source_url'],'hash':'hash'}],official_status='bilinmiyor')
        class UpdatingStore(MemoryStore):
            def all(self,kind):
                rows=super().all(kind)
                if kind=='calls':
                    current=self.get('calls','old-call');current['summary']='Güncel editör özeti';self.put('calls','old-call',current)
                return rows
        store=UpdatingStore();store.put('calls','old-call',old)
        persist_report(self.report,store)
        self.assertEqual(store.get('calls','old-call')['summary'],'Güncel editör özeti')

    def test_source_health_preserves_last_success_during_parser_failure(self):
        persist_report(self.report,self.store)
        before=self.store.get('source_health','s');self.assertEqual(before['last_found_count'],1)
        r=dict(self.report,accepted=[],sources=[{'id':'s','health':'failed','error':'Fixture parser failure','fetched':0}],generated_at='2026-10-11T00:00:00Z')
        persist_report(r,self.store);after=self.store.get('source_health','s')
        self.assertEqual(after['last_success'],before['last_success']);self.assertEqual(after['last_found_count'],1)
        self.assertEqual(after['last_error'],'Fixture parser failure')
    def test_demo_approval_never_enters_production_publication(self):
        self.service.demo=True
        persist_report(self.report,self.store)
        c=self.reviewed();self.service.approve(ADMIN,'abc',c['version'])
        self.assertTrue(self.store.get('calls','abc')['demo'])
        self.assertTrue(self.store.get('calls','abc')['approval']['demo'])
        result=publication_report(self.report,self.store,TODAY)
        self.assertEqual(result['accepted'],[]);self.assertEqual(result['review'],[])
    def test_review_rejects_credentials_and_nonstandard_ports(self):
        from hibe.aggregator.bridge import review_ready
        persist_report(self.report,self.store);c=self.reviewed()
        for url in ('https://:secret@x.org/call','https://x.org:9443/call','https://x.org:bad/call'):
            unsafe=dict(c,official_url=url,documents=[{'url':url,'hash':'hash'}])
            self.assertFalse(review_ready(unsafe))
