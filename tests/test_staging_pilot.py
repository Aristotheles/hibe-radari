"""Offline whole-pipeline pilot for all 22 verified RSS fixture interfaces.

This is not a live run of the 29-source production configuration.
"""
import copy
import hashlib
import json
import tempfile
import unittest
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path
import httpx
from hibe.aggregator.collector import run,write_report
from hibe.aggregator.bridge import persist_report,publication_report
from hibe.aggregator.site import build,PublicationBlocked
from hibe.service import Service
from hibe.store import SQLiteStore

ROOT=Path(__file__).resolve().parents[1]
TODAY=date(2026,10,10)

def manifest(path):
    return {p.relative_to(path).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in path.rglob('*') if p.is_file()}

class StagingPilotTests(unittest.TestCase):
    def test_two_complete_fixture_runs_error_broken_only_and_real_rollback(self):
        config=json.loads((ROOT/'config/aggregator.json').read_text(encoding='utf-8'))
        sources=[];routes={}
        for source in config['sources']:
            ident=source['id'];name=ident[4:] if ident.startswith('meb-') else ident
            fixture=ROOT/'tests/fixtures/aggregator'/f'{name}_rss_20261010.xml'
            if source['type']!='feed' or not fixture.exists():continue
            source=copy.deepcopy(source);source['detail']=ident=='meb-ogm';sources.append(source)
            body=fixture.read_bytes()
            if ident=='meb-ogm':
                tree=ET.fromstring(body);channel=tree.find('channel')
                for item in channel.findall('item')[1:]:channel.remove(item)
                body=ET.tostring(tree)
            routes[source['url']]=body
        self.assertEqual(len(sources),22)
        config=dict(config,sources=sources)
        detail_url='https://ogm.meb.gov.tr/www/gencbizz-lise-girisimcilik-programi-basvurulari-devam-ediyor/icerik/2657'
        routes[detail_url]=(ROOT/'tests/fixtures/aggregator/ogm_gencbizz_deadline_20261010.html').read_bytes()
        bad_source=sources[0]['url'];failure=None
        def response(request):
            url=str(request.url)
            if url==bad_source and failure=='http':return httpx.Response(503,text='temporary error')
            if url==bad_source and failure=='rss':return httpx.Response(200,text='<html>maintenance</html>')
            return httpx.Response(200,content=routes[url]) if url in routes else httpx.Response(404,text='No fixture')
        transport=httpx.MockTransport(response)
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);store=SQLiteStore(root/'pilot.db');service=Service(store,'test-admin',today=lambda:TODAY)
            try:
                report=run(config=config,today=TODAY,transport=transport)
                self.assertEqual(report['run_status'],'success');self.assertEqual(len(report['sources']),22)
                persist_report(report,store)
                call=next(c for c in store.all('calls') if c['source_url']==detail_url)
                self.assertEqual(call['deadline'],'2026-10-16')
                call.update(summary='GençBizz başvuru koşullarını ve okul katılımını resmî duyurudan inceleyin.',official_url=detail_url,official_url_verified=True)
                call=service.save({'uid':'test-admin','email_verified':True},call)
                service.approve({'uid':'test-admin','email_verified':True},call['id'],call['version'])
                out=root/'public';latest=root/'latest.json'
                published=publication_report(report,store,TODAY)
                build(published,out,TODAY,commit_report=lambda:write_report(report,latest),report_target=latest)
                first=manifest(out);first_report=latest.read_bytes()
                second=run(config=config,today=TODAY,transport=transport);persist_report(second,store)
                self.assertEqual(second['run_status'],'success')
                self.assertEqual(len(service.public()),1)
                build(publication_report(second,store,TODAY),out,TODAY,commit_report=lambda:write_report(second,latest),report_target=latest)
                before=manifest(out);before_report=latest.read_bytes()
                for failure in ('http','rss'):
                    failed=run(config=config,today=TODAY,transport=transport);persist_report(failed,store)
                    self.assertNotEqual(failed['run_status'],'success')
                    with self.assertRaises(PublicationBlocked):build(publication_report(failed,store,TODAY),out,TODAY)
                    self.assertEqual(manifest(out),before);self.assertEqual(latest.read_bytes(),before_report)
                failure=None
                partial=run(config=config,today=TODAY,transport=transport,only=['meb-ogm']);persist_report(partial,store)
                self.assertEqual(partial['run_status'],'partial')
                with self.assertRaises(PublicationBlocked):build(publication_report(partial,store,TODAY),out,TODAY)
                self.assertEqual(manifest(out),before)
                # Exercise the retained backup in this disposable directory.
                import os
                backups=list(root.glob('.public.backup-*'));self.assertTrue(backups)
                os.replace(out,root/'second-public');os.replace(backups[-1],out);latest.write_bytes(first_report)
                self.assertEqual(manifest(out),first)
                self.assertEqual(latest.read_bytes(),first_report)
            finally:store.db.close()
