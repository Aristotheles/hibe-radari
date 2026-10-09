"""Kaynakları çalıştırır, iki aşamalı süzer, tekilleştirir ve rapor üretir.

Aşama 1: liste bilgisiyle (başlık, kategori, kısa açıklama) puanla.
Aşama 2: elenmeyenlerden son tarihi olmayanların ayrıntı sayfasını çek (sınırlı), yeniden puanla.
Reddedilenler silinmez; gerekçeleriyle rapora yazılır ki süzgeç kuralı gözle ayarlanabilsin."""
import json
from datetime import datetime
from pathlib import Path

from . import eu_ft, feeds, html_cards
from .models import canonical_url, today as today_fn
from .net import Fetcher
from .relevance import RelevanceFilter

ROOT = Path(__file__).resolve().parents[2]
CONNECTORS = {'eu_ft': eu_ft.collect, 'feed': feeds.collect,
              'html_list': html_cards.collect_list, 'html_cards': html_cards.collect_cards,
              'html_crawl': html_cards.collect_crawl, 'page_watch': html_cards.collect_pages}
ORDER = {'accept': 0, 'review': 1, 'watch': 2, 'general': 3, 'reject': 4}
GROUPS = {'accept': 'accepted', 'review': 'review', 'watch': 'watch', 'general': 'general', 'reject': 'rejected'}


def load_config(path=None):
    return json.loads((path or ROOT / 'config/aggregator.json').read_text(encoding='utf-8'))


def run_source(source, config, rel, today, transport=None, sleep=None):
    """Tek kaynak: (öğeler, durum). Hata kaynağı düşürür, çalışmayı durdurmaz."""
    status = {'id': source['id'], 'organization': source.get('organization'), 'fetched': 0, 'enriched': 0, 'error': None}
    fetcher = Fetcher(source['allowed_hosts'], config.get('tls_relaxed_hosts', []), transport,
                      delay=0 if transport else config.get('delay_seconds', 1.0), **({'sleep': sleep} if sleep else {}))
    try:
        items = CONNECTORS[source['type']](source, fetcher, today)
        status['fetched'] = len(items)
        for item in items:
            item.aggregator = bool(source.get('aggregator'))
            item.organization = item.organization or source.get('organization')
            item.language = item.language or source.get('language')
            rel.evaluate(item, today, source.get('implied_programme'))
            if source.get('pinned'):
                pin(item, today)
        if source.get('detail'):
            budget = config.get('enrich_limit', 25)
            for item in items:
                if budget <= 0:
                    break
                if item.relevance.verdict not in ('accept', 'review', 'watch', 'general') or item.deadline:
                    continue
                budget -= 1
                try:
                    html_cards.enrich(item, fetcher, today, source.get('content_selector'))
                    status['enriched'] += 1
                except Exception as exc:                 # ayrıntı alınamazsa öğe listedeki haliyle kalır
                    item.relevance.reasons.append(f'not: ayrıntı sayfası alınamadı ({type(exc).__name__})')
                    continue
                rel.evaluate(item, today, source.get('implied_programme'))
        return items, status
    except Exception as exc:
        status['error'] = f'{type(exc).__name__}: {str(exc)[:200]}'
        return [], status
    finally:
        status['requests'] = fetcher.calls
        fetcher.close()


def pin(item, today):
    """Kullanıcının adıyla istediği program: puandan bağımsız listede tutulur.
    Kapalı/süresi dolmuş → watch (yeni dönemi bekle); aksi halde review (insan bakar)."""
    expired = bool(item.deadline and item.deadline < today)
    item.relevance.verdict = 'watch' if (expired or item.status_hint == 'kapalı') else 'review'
    item.relevance.reasons.append(f'sabit izleme: kullanıcı isteği (durum: {item.status_hint or "belirsiz"})')


def dedupe(items):
    """Aynı canonical URL'yi (ve derleme sitesinin işaret ettiği resmî sayfayı) tek kayda indirir.
    Resmî kaynak, derleme sitesinden önce gelir; diğer kaynak kimlikleri seen_in'e yazılır."""
    items = sorted(items, key=lambda i: (i.aggregator, ORDER[i.relevance.verdict]))
    kept, index = [], {}
    for item in items:
        keys = [canonical_url(item.source_url)] + ([canonical_url(item.original_url)] if item.original_url else [])
        twin = next((index[k] for k in keys if k in index), None)
        if twin:
            twin.seen_in.append(item.source_id)
            continue
        kept.append(item)
        for key in keys:
            index[key] = item
    return kept


def run(config=None, rules=None, today=None, only=None, transport=None, sleep=None):
    config = config or load_config()
    today = today or today_fn()
    rel = RelevanceFilter(rules)
    all_items, statuses = [], []
    for source in config['sources']:
        if only and source['id'] not in only:
            continue
        items, status = run_source(source, config, rel, today, transport, sleep)
        all_items.extend(items)
        statuses.append(status)
    items = dedupe(all_items)
    far = datetime(9999, 1, 1).date()
    items.sort(key=lambda i: (ORDER[i.relevance.verdict], i.deadline or far, i.title))
    groups = {v: [i.to_dict() for i in items if i.relevance.verdict == v] for v in ORDER}
    return {'generated_at': datetime.now().isoformat(timespec='seconds'), 'today': today.isoformat(),
            'counts': {v: len(groups[v]) for v in ORDER}, 'sources': statuses,
            **{GROUPS[v]: groups[v] for v in ORDER}}


def write_report(report, path=None):
    path = Path(path) if path else ROOT / 'data/aggregator/latest.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    return path
