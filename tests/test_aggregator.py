"""Toplayıcı testleri: ağ yok; httpx.MockTransport + gerçek yanıtlardan küçültülmüş fixture'lar."""
import json
import unittest
from datetime import date
from pathlib import Path

import httpx

from hibe.aggregator import collector, eu_ft, feeds, html_cards
from hibe.aggregator.models import GrantOpportunity, canonical_url, opportunity_id
from hibe.aggregator.net import FetchError, Fetcher
from hibe.aggregator.relevance import RelevanceFilter
from hibe.aggregator.textutil import find_deadline, fold, shorten

FIX = Path(__file__).resolve().parent / 'fixtures/aggregator'
TODAY = date(2026, 10, 9)


def fixture(name):
    return (FIX / name).read_bytes()


def transport(routes):
    """routes: {(method, url-başı): (status, bytes|str, content_type)}; ilk eşleşen kazanır."""
    seen = []

    def handler(request):
        seen.append(str(request.url))
        for (method, prefix), (status, body, ctype) in routes.items():
            if request.method == method and str(request.url).startswith(prefix):
                return httpx.Response(status, content=body if isinstance(body, bytes) else body.encode(),
                                      headers={'content-type': ctype})
        return httpx.Response(404, content=b'yok')
    mock = httpx.MockTransport(handler)
    mock.seen = seen
    return mock


def fetcher(hosts, routes, **kw):
    return Fetcher(hosts, transport=transport(routes), delay=0, **kw)


class TextUtilTests(unittest.TestCase):
    def test_deadline_needs_cue_word_in_three_languages(self):
        self.assertEqual(find_deadline('Frist ist der 06. Dezember 2026.', TODAY)[0], date(2026, 12, 6))
        self.assertEqual(find_deadline('Son başvuru tarihi 13 Kasım 2026 saat 17:30', TODAY)[0], date(2026, 11, 13))
        self.assertEqual(find_deadline('Deadline: November 15, 2026', TODAY)[0], date(2026, 11, 15))
        self.assertEqual(find_deadline('Başvurular 25.10.2026 tarihine kadar alınır', TODAY)[0], date(2026, 10, 25))

    def test_date_without_cue_is_not_a_deadline(self):
        self.assertEqual(find_deadline('Etkinlik 5 Mart 2027 tarihinde yapıldı', TODAY), (None, None))
        self.assertEqual(find_deadline('', TODAY), (None, None))

    def test_nearest_future_deadline_wins_and_past_only_returns_latest(self):
        text = 'Son başvuru 1 Ocak 2026. Son başvuru 5 Aralık 2026. Son başvuru 9 Ocak 2027.'
        self.assertEqual(find_deadline(text, TODAY)[0], date(2026, 12, 5))
        self.assertEqual(find_deadline('Son başvuru 1 Ocak 2025, deadline: 3 March 2026', TODAY)[0], date(2026, 3, 3))

    def test_fold_and_shorten(self):
        self.assertEqual(fold('İSTANBUL Işık Öğretmen Schüler'), 'istanbul isik ogretmen schuler')
        self.assertTrue(shorten('kelime ' * 100, 50).endswith('…'))

    def test_canonical_url_merges_variants(self):
        a = canonical_url('http://AB-ilan.com/x/?utm_source=a#frag')
        self.assertEqual(a, 'https://ab-ilan.com/x')
        self.assertEqual(opportunity_id('https://ab-ilan.com/x/'), opportunity_id('http://ab-ilan.com/x?utm_x=1'))


class RelevanceTests(unittest.TestCase):
    def setUp(self):
        self.filter = RelevanceFilter()

    def judge(self, title, categories=(), implied=None, **kw):
        item = GrantOpportunity(title, 's', 'https://x.org/a', categories=list(categories), **kw)
        return self.filter.evaluate(item, TODAY, implied), item

    def test_school_programmes_are_accepted(self):
        for title in ('4006-TÜBİTAK Bilim Fuarları Destekleme Programı 13. Dönem Çağrıları Yayınlandı',
                      '2204-A Lise Öğrencileri Araştırma Projeleri Yarışması 2027 Yılı Çağrıları',
                      'Erasmus+ KA122-SCH okul eğitimi akreditasyonlu hareketlilik çağrısı'):
            self.assertEqual(self.judge(title)[0].verdict, 'accept', title)

    def test_implied_source_programme_counts_and_is_explained(self):
        rel, _ = self.judge('Ausschreibung für schulischen Austausch in 2027/28', implied='bilateral-exchange')
        self.assertEqual(rel.verdict, 'accept')
        self.assertTrue(any('kaynağın kendi programı' in r for r in rel.reasons))

    def test_noise_is_rejected_with_reasons(self):
        cases = [('Savunma Sanayii Başkanlığı 22 Uzman Yardımcısı Alacak', ['Kamu İş İlanları']),
                 ('H. Orhan Argüden Yönetişim Bursu 2026-2027 Dönemi Başvuruları', ['Burs Duyuruları']),
                 ('Selanik Belgesel Festivali Docs in Progress Programı İçin Başvurular Açıldı', []),
                 ('Türkiye’de Çevresel Adalete Erişimi Artırmaya Yönelik Hibe Programı', ['AB Projeleri']),
                 ('EIT Culture & Creativity’den Startup ve Scaleuplara 500.000 Avro Destek', [])]
        for title, cats in cases:
            rel, _ = self.judge(title, cats)
            self.assertEqual(rel.verdict, 'reject', title)
            self.assertTrue(rel.reasons, title)

    def test_generic_education_word_alone_is_not_enough_for_review(self):
        rel, _ = self.judge('Eğitimde Eşitsizlikleri Azaltan Teknoloji Çözümlerine Destek')
        self.assertEqual(rel.verdict, 'general')               # yayına girmez ama genel listede kalır

    def test_youth_exchange_participant_call_is_accepted_for_scope(self):
        rel, _ = self.judge('Katılımcı Çağrısı: Polonya’da Erasmus+ Gençlik Projesi', ['Diğer Gençlik Haberleri'])
        self.assertEqual(rel.verdict, 'accept')

    def test_university_researcher_programmes_do_not_leak_into_review(self):
        rel, _ = self.judge('2247–A Ulusal Lider Araştırmacılar Programı ve 2247–D Ulusal Genç Liderler Programı Çağrıları')
        self.assertEqual(rel.verdict, 'reject')

    def test_expired_strong_match_goes_to_watchlist_not_trash(self):
        rel, _ = self.judge('4004 Doğa Eğitimi ve Bilim Okulları Çağrısı', deadline=date(2024, 12, 6))
        self.assertEqual(rel.verdict, 'watch')
        self.assertTrue(any('son tarih geçmiş' in r for r in rel.reasons))
        self.assertIn('izleme', rel.reasons[-1])

    def test_expired_irrelevant_item_is_noise(self):
        rel, _ = self.judge('Savunma Sanayii Uzman Yardımcısı Alacak', deadline=date(2024, 12, 6))
        self.assertEqual(rel.verdict, 'reject')

    def test_open_general_grant_without_school_match_is_kept_as_general(self):
        rel, _ = self.judge('Avustralya Büyükelçiliği Doğrudan Yardım Programı Başvuruları Açıldı')
        self.assertEqual(rel.verdict, 'general')
        self.assertIn('genel hibe', rel.reasons[-1])

    def test_penalised_noise_never_becomes_general(self):
        for title in ('Cold Noses Vakfı’ndan Hayvan Refahı Projelerine Hibe Desteği',
                      'Selanik Belgesel Festivali Programı İçin Başvurular Açıldı'):
            self.assertEqual(self.judge(title)[0].verdict, 'reject', title)

    def test_bilim_ve_toplum_programmes_match(self):
        rel, _ = self.judge('TÜBİTAK Bilim ve Toplum Destek Programları Proje Teşvik Ödülleri Başvuruları Açıldı')
        self.assertIn(rel.verdict, ('accept', 'review'))

    def test_old_announcement_without_deadline_goes_to_watch_but_recent_is_kept(self):
        old, _ = self.judge('Okul öğretmenlerine hibe çağrısı', published_at=date(2026, 3, 1))
        new, item = self.judge('Okul öğretmenlerine hibe çağrısı', published_at=date(2026, 10, 1))
        self.assertEqual(old.verdict, 'watch')
        self.assertEqual(new.verdict, 'accept')
        self.assertTrue(any('son tarih bulunamadı' in r for r in new.reasons))

    def test_title_match_outweighs_description_only_match(self):
        title_hit, _ = self.judge('Okul hibe çağrısı')
        body_hit, _ = self.judge('Genel çağrı', description_short='okul hibe')
        self.assertGreater(title_hit.score, body_hit.score)


class FetcherTests(unittest.TestCase):
    def test_non_allowed_host_scheme_and_port_are_blocked(self):
        f = fetcher(['ab-ilan.com'], {('GET', 'https://ab-ilan.com'): (200, 'ok', 'text/html')})
        for url in ('https://evil.org/', 'http://ab-ilan.com/', 'https://ab-ilan.com:8443/', 'https://u:p@ab-ilan.com/'):
            with self.assertRaises(FetchError, msg=url):
                f.get(url)
        self.assertEqual(f.get_text('https://ab-ilan.com/'), 'ok')

    def test_http_error_status_raises(self):
        f = fetcher(['ab-ilan.com'], {('GET', 'https://ab-ilan.com'): (500, 'x', 'text/html')})
        with self.assertRaises(FetchError):
            f.get('https://ab-ilan.com/')

    def test_tls_failure_retries_unverified_only_for_listed_host(self):
        calls = []

        def handler(request):
            calls.append(request)
            if len(calls) == 1:
                raise httpx.ConnectError('[SSL: CERTIFICATE_VERIFY_FAILED] unable to get local issuer certificate')
            return httpx.Response(200, content=b'ok')
        strict = Fetcher(['site.gov.tr'], transport=httpx.MockTransport(handler), delay=0)
        with self.assertRaises(FetchError):
            strict.get('https://site.gov.tr/')
        calls.clear()
        relaxed = Fetcher(['site.gov.tr'], relaxed_tls_hosts=['site.gov.tr'],
                          transport=httpx.MockTransport(handler), delay=0)
        self.assertEqual(relaxed.get_text('https://site.gov.tr/'), 'ok')
        self.assertEqual(len(calls), 2)

    def test_polite_delay_between_requests(self):
        slept = []
        f = Fetcher(['a.org'], transport=transport({('GET', 'https://a.org'): (200, 'x', 'text/html')}),
                    delay=2.0, sleep=slept.append)
        f.get('https://a.org/1')
        f.get('https://a.org/2')
        self.assertEqual(len(slept), 1)
        self.assertGreater(slept[0], 0)


class ConnectorTests(unittest.TestCase):
    def test_eu_ft_parses_real_response_shape_and_picks_nearest_future_deadline(self):
        payload = json.loads(fixture('eu_search.json'))
        items = eu_ft.parse(payload, {'id': 'eu-ft'}, TODAY)
        by_id = {i.source_url.rsplit('/', 1)[-1]: i for i in items}
        eche = by_id['ERASMUS-EDU-2022-ECHE-CERT-FP']
        self.assertEqual(eche.deadline, date(2027, 1, 26))           # çoklu kesim tarihinden en yakın gelecek
        self.assertEqual(eche.programme, 'Erasmus+')
        self.assertTrue(eche.source_url.startswith('https://ec.europa.eu/info/funding-tenders/'))
        self.assertIn('API deadlineDate', eche.deadline_evidence)
        self.assertEqual(by_id['ERASMUS-EDU-2023-PEX-COVE'].deadline, date(2023, 6, 8))

    def test_eu_ft_posts_multipart_query_with_framework_filter(self):
        mock = transport({('POST', eu_ft.API): (200, fixture('eu_search.json'), 'application/json')})
        f = Fetcher(['api.tech.ec.europa.eu'], transport=mock, delay=0)
        source = {'id': 'eu-ft', 'queries': [{'framework': '43353764', 'text': '***'}, {'framework': None, 'text': 'school'}]}
        items = eu_ft.collect(source, f, TODAY)
        self.assertEqual(len(mock.seen), 2)
        self.assertIn('text=school', mock.seen[1])
        self.assertGreaterEqual(len(items), 4)                        # iki sorgu, tekilleştirme sonradan

    def test_feed_maps_real_abilan_items(self):
        f = fetcher(['ab-ilan.com'], {('GET', 'https://ab-ilan.com/feed/'): (200, fixture('abilan_feed.xml'), 'application/rss+xml')})
        items = feeds.collect({'id': 'ab', 'url': 'https://ab-ilan.com/feed/', 'organization': 'ab-ilan (derleme)'}, f, TODAY)
        self.assertEqual(len(items), 6)
        first = items[0]
        self.assertTrue(first.source_url.startswith('https://ab-ilan.com/'))
        self.assertTrue(first.categories)
        self.assertEqual(first.published_at, date(2026, 10, 9))
        self.assertLessEqual(len(first.description_short), 301)
        self.assertNotIn('<', first.description_short)

    def test_feed_upgrades_http_links_when_configured(self):
        xml = ('<?xml version="1.0"?><rss version="2.0"><channel><item><title>4004 çağrısı</title>'
               '<link>http://4000.tubitak.gov.tr/node/472</link><description>x</description></item></channel></rss>')
        f = fetcher(['4000.tubitak.gov.tr'], {('GET', 'https://4000.tubitak.gov.tr/rss.xml'): (200, xml, 'application/rss+xml')})
        items = feeds.collect({'id': 't', 'url': 'https://4000.tubitak.gov.tr/rss.xml', 'upgrade_http': True}, f, TODAY)
        self.assertEqual(items[0].source_url, 'https://4000.tubitak.gov.tr/node/472')

    def test_cards_parser_reads_title_category_deadline_and_skips_closed(self):
        f = fetcher(['www.stgm.org.tr'], {('GET', 'https://www.stgm.org.tr/hibe-duyurulari'): (200, fixture('stgm_list.html'), 'text/html')})
        source = {'id': 'stgm', 'url': 'https://www.stgm.org.tr/hibe-duyurulari', 'require_class': 'acik',
                  'selectors': {'card': 'div.anasayfa-icerikler.hibe-duyurulari', 'title': '.anasayfa-icerikler-baslik',
                                'summary': '.anasayfa-icerikler-ozet', 'link': '.anasayfa-icerikler-hover a',
                                'date': '.hibe-duyurulari-tarih time', 'category': '.hibe-duyurulari-konu'}}
        items = html_cards.collect_cards(source, f, TODAY)
        titles = [i.title for i in items]
        self.assertEqual(len(items), 4)
        self.assertFalse(any(t.startswith('KAPALI') for t in titles))
        tap = next(i for i in items if i.title.startswith('TAP Vakfı'))
        self.assertEqual(tap.deadline, date(2026, 10, 25))
        self.assertEqual(tap.categories, ['Gençlik'])
        self.assertEqual(tap.source_url, 'https://www.stgm.org.tr/tap-vakfi-11-donem-1-aralik-genclik-fonu-basvurulari-acildi')

    def test_link_list_filters_by_pattern_and_title_length(self):
        html = ('<a href="/tr/duyuru/4006-bilim-fuarlari-13-donem-cagrilari">4006 Bilim Fuarları 13. Dönem Çağrıları</a>'
                '<a href="/tr/duyuru/4006-bilim-fuarlari-13-donem-cagrilari">Devamını oku</a>'
                '<a href="/tr/hakkimizda-bolumu-sayfasi">Hakkımızda ve kurumsal bilgiler</a>')
        f = fetcher(['tubitak.gov.tr'], {('GET', 'https://tubitak.gov.tr/tr/duyuru'): (200, html, 'text/html')})
        items = html_cards.collect_list({'id': 't', 'url': 'https://tubitak.gov.tr/tr/duyuru',
                                         'link_pattern': '^/tr/duyuru/[a-z0-9-]{12,}$'}, f, TODAY)
        self.assertEqual([i.source_url for i in items], ['https://tubitak.gov.tr/tr/duyuru/4006-bilim-fuarlari-13-donem-cagrilari'])

    def test_crawl_finds_call_pages_one_level_down_and_extracts_german_deadline(self):
        root = '<a href="/foerderung/schulischer-austausch/">Schulisch</a><a href="/ueber-uns/">Über uns</a>'
        program = '<a href="/foerderung/ausschreibung-schulaustausch-2027-28/">Ausschreibung</a>'
        call = ('<html><head><title>Ausschreibung Schulaustausch 2027/28 – Jugendbrücke</title></head><body>'
                '<h3>AUSSCHREIBUNG FÜR SCHULISCHEN AUSTAUSCH IN 2027/28</h3>'
                '<p>Die Frist für die Einreichung ist der 06. Dezember 2026.</p></body></html>')
        h = 'https://www.jugendbruecke.de'
        f = fetcher(['www.jugendbruecke.de'], {
            ('GET', f'{h}/foerderung/ausschreibung-schulaustausch-2027-28/'): (200, call, 'text/html'),
            ('GET', f'{h}/foerderung/schulischer-austausch/'): (200, program, 'text/html'),
            ('GET', f'{h}/foerderung/'): (200, root, 'text/html')})
        source = {'id': 'jb', 'url': f'{h}/foerderung/', 'follow': '/foerderung/', 'call_pattern': 'ausschreibung', 'max_pages': 5}
        items = html_cards.collect_crawl(source, f, TODAY)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].title, 'AUSSCHREIBUNG FÜR SCHULISCHEN AUSTAUSCH IN 2027/28')
        self.assertEqual(items[0].deadline, date(2026, 12, 6))

    def test_enrich_adds_deadline_and_original_link_but_skips_social_links(self):
        page = ('<article><p>Başvurular 25 Ekim 2026’ya kadar alınır.</p>'
                '<a href="https://www.facebook.com/x">Paylaş</a>'
                '<a href="https://www.example-vakif.org/basvuru/gençlik-fonu">Başvuru sayfası</a></article>')
        f = fetcher(['ab-ilan.com'], {('GET', 'https://ab-ilan.com/tap'): (200, page, 'text/html')})
        item = GrantOpportunity('TAP Vakfı Gençlik Fonu', 'ab', 'https://ab-ilan.com/tap')
        html_cards.enrich(item, f, TODAY)
        self.assertEqual(item.deadline, date(2026, 10, 25))
        self.assertTrue(item.original_url.startswith('https://www.example-vakif.org/basvuru/'))


class CollectorTests(unittest.TestCase):
    CONFIG = {
        'delay_seconds': 0, 'enrich_limit': 5, 'tls_relaxed_hosts': [],
        'sources': [
            {'id': 'official', 'type': 'feed', 'url': 'https://tubitak.gov.tr/feed', 'allowed_hosts': ['tubitak.gov.tr'],
             'organization': 'TÜBİTAK', 'language': 'tr'},
            {'id': 'aggregator', 'type': 'feed', 'url': 'https://ab-ilan.com/feed/', 'allowed_hosts': ['ab-ilan.com'],
             'organization': 'ab-ilan (derleme)', 'aggregator': True, 'detail': True},
            {'id': 'broken', 'type': 'feed', 'url': 'https://down.example.org/feed', 'allowed_hosts': ['down.example.org']},
        ]}

    def rss(self, *entries):
        items = ''.join(f'<item><title>{t}</title><link>{l}</link><description>{d}</description>'
                        f'<pubDate>Thu, 08 Oct 2026 10:00:00 +0000</pubDate></item>' for t, l, d in entries)
        return f'<?xml version="1.0"?><rss version="2.0"><channel>{items}</channel></rss>'

    def routes(self):
        official = self.rss(('4006 Bilim Fuarları 13. Dönem Çağrıları Açıldı', 'https://tubitak.gov.tr/duyuru/4006',
                             'Son başvuru 13 Kasım 2026'),
                            ('Personel alım ilanı: uzman yardımcısı alacak', 'https://tubitak.gov.tr/duyuru/is', 'x'))
        agg = self.rss(('4006 Bilim Fuarları 13. Dönem Çağrıları Açıldı', 'https://ab-ilan.com/4006-fuar', 'kopya haber'),
                       ('Lise öğretmenlerine hibe çağrısı', 'https://ab-ilan.com/lise-hibe', 'Ayrıntı sayfasında'),
                       ('Doktora bursu başvuruları', 'https://ab-ilan.com/burs', 'x'))
        detail = ('<article><p>Başvurular 30 Kasım 2026 tarihine kadar alınır.</p>'
                  '<a href="https://hibe.example.org/apply">Resmî başvuru</a></article>')
        dup = '<article><a href="https://tubitak.gov.tr/duyuru/4006">Resmî</a></article>'
        return {('GET', 'https://tubitak.gov.tr/feed'): (200, official, 'application/rss+xml'),
                ('GET', 'https://ab-ilan.com/feed/'): (200, agg, 'application/rss+xml'),
                ('GET', 'https://ab-ilan.com/lise-hibe'): (200, detail, 'text/html'),
                ('GET', 'https://ab-ilan.com/4006-fuar'): (200, dup, 'text/html'),
                ('GET', 'https://down.example.org'): (500, 'hata', 'text/html')}

    def run_all(self):
        return collector.run(self.CONFIG, today=TODAY, transport=transport(self.routes()))

    def test_end_to_end_filters_enriches_dedupes_and_isolates_failures(self):
        report = self.run_all()
        accepted = {o['title']: o for o in report['accepted']}
        self.assertEqual(report['counts']['accept'], 2)
        self.assertEqual(set(accepted), {'4006 Bilim Fuarları 13. Dönem Çağrıları Açıldı', 'Lise öğretmenlerine hibe çağrısı'})
        # resmî kaynak kazanır, derleme kopyası seen_in'e yazılır
        fair = accepted['4006 Bilim Fuarları 13. Dönem Çağrıları Açıldı']
        self.assertEqual(fair['source_id'], 'official')
        self.assertEqual(fair['seen_in'], ['aggregator'])
        self.assertEqual(fair['deadline'], '2026-11-13')
        # ayrıntı sayfasından son tarih + resmî link adayı
        lise = accepted['Lise öğretmenlerine hibe çağrısı']
        self.assertEqual(lise['deadline'], '2026-11-30')
        self.assertEqual(lise['original_url'], 'https://hibe.example.org/apply')
        self.assertTrue(lise['aggregator'])
        # elenenler gerekçesiyle saklanır
        rejected = {o['title']: o for o in report['rejected']}
        self.assertIn('Personel alım ilanı: uzman yardımcısı alacak', rejected)
        self.assertTrue(any('iş/personel' in r for r in rejected['Doktora bursu başvuruları']['relevance']['reasons'] + rejected['Personel alım ilanı: uzman yardımcısı alacak']['relevance']['reasons']))
        # bozuk kaynak diğerlerini durdurmaz
        status = {s['id']: s for s in report['sources']}
        self.assertIn('FetchError', status['broken']['error'])
        self.assertIsNone(status['official']['error'])

    def test_every_output_row_carries_source_link_and_decision_reasons(self):
        report = self.run_all()
        total = 0
        for group, verdict in collector.GROUPS.items() and {v: k for k, v in collector.GROUPS.items()}.items():
            for row in report[group]:
                total += 1
                self.assertTrue(row['source_url'].startswith('https://'))
                self.assertTrue(row['relevance']['reasons'])
                self.assertEqual(row['relevance']['verdict'], verdict)
        self.assertEqual(total, sum(report['counts'].values()))

    def test_only_option_limits_sources(self):
        report = collector.run(self.CONFIG, today=TODAY, only=['official'], transport=transport(self.routes()))
        self.assertEqual([s['id'] for s in report['sources']], ['official'])

    def test_report_written_as_utf8_json(self):
        import tempfile
        report = self.run_all()
        with tempfile.TemporaryDirectory() as tmp:
            path = collector.write_report(report, Path(tmp) / 'out/latest.json')
            data = json.loads(path.read_text(encoding='utf-8'))
        self.assertEqual(data['counts'], report['counts'])
        self.assertIn('Bilim Fuarları', json.dumps(data, ensure_ascii=False))


class ProjectConfigTests(unittest.TestCase):
    def test_shipped_configs_are_consistent(self):
        root = Path(__file__).resolve().parents[1]
        config = json.loads((root / 'config/aggregator.json').read_text(encoding='utf-8'))
        rules = json.loads((root / 'config/relevance.json').read_text(encoding='utf-8'))
        ids = [s['id'] for s in config['sources']]
        self.assertEqual(len(ids), len(set(ids)))
        for s in config['sources']:
            self.assertIn(s['type'], collector.CONNECTORS)
            self.assertTrue(s['allowed_hosts'])
            if s.get('implied_programme'):
                self.assertIn(s['implied_programme'], rules['programmes'])
            from urllib.parse import urlsplit
            if s.get('url'):
                self.assertIn(urlsplit(s['url']).hostname, s['allowed_hosts'])
        RelevanceFilter(rules)             # tüm terimler derlenir


if __name__ == '__main__':
    unittest.main()


class SiteTests(unittest.TestCase):
    def report(self):
        evil = {'id': 'a' * 20, 'title': '<script>alert(1)</script> Okul hibesi', 'source_id': 's', 'source_url': 'javascript:alert(1)',
                'organization': '"><img src=x onerror=alert(1)>', 'deadline': '2026-10-20', 'deadline_evidence': '<b>x</b>',
                'description_short': 'açıklama <i>', 'language': 'tr', 'programme': 'Erasmus+', 'categories': ['k'],
                'original_url': 'http://insecure.example.org/x', 'seen_in': [], 'audience': ['school'],
                'relevance': {'verdict': 'accept', 'score': 9, 'reasons': ['+3 <b>gerekçe</b>', '-2 hariç: x', 'not: tarih'], 'audience': ['school']}}
        good = dict(evil, id='b' * 20, title='Güvenli kayıt', source_url='https://tubitak.gov.tr/x', original_url=None, deadline=None,
                    deadline_evidence=None, audience=['teacher'], relevance={'verdict': 'accept', 'score': 5, 'reasons': ['+3 ok'], 'audience': ['teacher']})
        from hibe.domain import version
        for row in (evil, good):
            row.update(summary=row['description_short'], documents=[{'url': 'https://tubitak.gov.tr/x', 'hash': 'test'}],
                       paths=[{'role': 'dogrudan', 'conditions': []}], themes=['bilim'], official_status='acik')
            row['approval'] = {'reviewed': True, 'version': version(row)}
        return {'generated_at': '2026-10-09T17:00:00', 'today': '2026-10-09',
                'counts': {'accept': 2, 'review': 0, 'watch': 0, 'general': 0, 'reject': 0},
                'run_status': 'success', 'sources': [{'id': 's', 'health': 'success', 'organization': 'Kurum', 'fetched': 2, 'error': None}], 'accepted': [evil, good], 'review': [],
                'watch': [], 'general': [], 'rejected': [{'title': 'GİZLİ-GÜRÜLTÜ'}]}

    def build(self):
        import tempfile
        from hibe.aggregator import site
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        out = site.build(self.report(), tmp.name, today=date(2026, 10, 9))
        return out, {p.relative_to(out).as_posix(): p.read_text(encoding='utf-8') for p in out.rglob('*') if p.is_file()}

    def test_site_has_lovable_pages_detail_pages_and_ics(self):
        _, files = self.build()
        for name in ('index.html', 'takvim.html', 'nasil-calisir.html', 'style.css', 'app.js', 'theme.js', '404.html', 'data.json', 'robots.txt', 'sitemap.xml'):
            self.assertIn(name, files)
        self.assertIn('ilan/' + 'a' * 20 + '.html', files)
        self.assertIn('ics/' + 'a' * 20 + '.ics', files)               # tarihli kayıt için takvim dosyası
        self.assertNotIn('ics/' + 'b' * 20 + '.ics', files)            # tarihsiz kayıt için yok
        index = files['index.html']
        for marker in ('class="brand-symbol"', 'audience-toggle', 'filter-bar', 'opportunity-card', 'trust-strip', 'Okulun için bir sonraki fırsat.'):
            self.assertIn(marker, index)
        self.assertIn('data-tab="me"', index)                           # öğretmen kaydı "Ben" sekmesinde
        self.assertIn('BEGIN:VCALENDAR', files['ics/' + 'a' * 20 + '.ics'])
        self.assertIn('DTSTART;VALUE=DATE:20261020', files['ics/' + 'a' * 20 + '.ics'])

    def test_untrusted_text_is_escaped_and_unsafe_links_dropped(self):
        _, files = self.build()
        for name in ('index.html', 'ilan/' + 'a' * 20 + '.html', 'takvim.html'):
            page = files[name]
            self.assertNotIn('<script>alert', page, name)
            self.assertNotIn('<img src=x', page, name)
            self.assertNotIn('javascript:', page, name)
            self.assertNotIn('http://insecure', page, name)
        self.assertIn('&lt;script&gt;', files['index.html'])
        self.assertIn('11 gün kaldı', files['index.html'])
        self.assertIn('Tarih bekleniyor', files['index.html'])
        self.assertIn('https://tubitak.gov.tr/x', files['ilan/' + 'b' * 20 + '.html'])
        self.assertIn('Resmî sayfada doğrula', files['ilan/' + 'b' * 20 + '.html'])

    def test_only_published_groups_leave_the_report(self):
        _, files = self.build()
        data = json.loads(files['data.json'])
        self.assertEqual(len(data['items']), 2)
        self.assertNotIn('GİZLİ-GÜRÜLTÜ', json.dumps(data, ensure_ascii=False))
        self.assertNotIn('GİZLİ-GÜRÜLTÜ', files['index.html'])

    def test_every_page_is_csp_clean_no_inline_script_style_or_handlers(self):
        import re
        _, files = self.build()
        for name, page in files.items():
            if not name.endswith('.html'):
                continue
            self.assertNotRegex(page, r'<script(?![^>]* src=)(?![^>]*application/json)', name)
            self.assertNotIn('<style', page, name)
            self.assertNotRegex(page, r'\sstyle=', name)
            bare = re.sub(r'"[^"]*"', '""', page)                       # tırnaklı değerler kaçışlanmış veri
            self.assertNotRegex(bare, r'<[a-zA-Z][^>]*\son\w+\s*=', name)
            self.assertNotIn('<img', page, name)

    def test_calendar_data_block_cannot_break_out_of_script(self):
        _, files = self.build()
        blob = files['takvim.html'].split('id="cal-data">', 1)[1].split('</script>', 1)[0]
        self.assertNotIn('<', blob)
        self.assertEqual(json.loads(blob)['today'], '2026-10-09')
