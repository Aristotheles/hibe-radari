"""Kaynakları çalıştırır, iki aşamalı süzer, tekilleştirir ve rapor üretir.

Aşama 1: liste bilgisiyle (başlık, kategori, kısa açıklama) puanla.
Aşama 2: elenmeyenlerden son tarihi olmayanların ayrıntı sayfasını çek (sınırlı), yeniden puanla.
Reddedilenler silinmez; gerekçeleriyle rapora yazılır ki süzgeç kuralı gözle ayarlanabilsin."""
import json
from datetime import datetime, timezone
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
    status = {'id': source['id'], 'organization': source.get('organization'), 'fetched': 0,
              'enriched': 0, 'detail_errors': 0, 'error': None, 'health': 'success'}
    fetcher = Fetcher(source['allowed_hosts'], config.get('tls_relaxed_hosts', []), transport,
                      delay=0 if transport else config.get('delay_seconds', 1.0),
                      cache_dir=None if transport else ROOT / 'data/aggregator/http-cache',
                      access_policy=None if transport else source.get('access_policy'), **({'sleep': sleep} if sleep else {}))
    try:
        items = CONNECTORS[source['type']](source, fetcher, today)
        status['fetched'] = len(items)
        if not items and not source.get('allow_empty', False):
            status['health'] = 'suspicious_empty'
            status['error'] = 'Şüpheli boş sonuç; kaynak yapılandırmasında allow_empty açıkça doğrulanmalı'
            return [], status
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
                    status['detail_errors'] += 1
                    continue
                rel.evaluate(item, today, source.get('implied_programme'))
        return items, status
    except Exception as exc:
        status['error'] = f'{type(exc).__name__}: {str(exc)[:200]}'
        status['health'] = 'failed'
        status['error_kind'] = getattr(exc, 'kind', 'parser')
        return [], status
    finally:
        status['requests'] = fetcher.calls
        fetcher.close()
        if status['health'] == 'success' and status['detail_errors']:
            status['health'] = 'partial'


def pin(item, today):
    """Kullanıcının adıyla istediği program: puandan bağımsız listede tutulur.
    Kapalı/süresi dolmuş → watch (yeni dönemi bekle); aksi halde review (insan bakar)."""
    expired = bool(item.deadline and item.deadline_precision == 'day' and not item.deadline_year_inferred and item.deadline < today)
    item.relevance.verdict = 'watch' if (expired or item.status_hint == 'kapalı') else 'review'
    item.relevance.reasons.append(f'sabit izleme: kullanıcı isteği (durum: {item.status_hint or "belirsiz"})')


def dedupe(items):
    """Kanıtlı kimlik/ayrıntı alias eşleşmesi; benzer başlık yalnız inceleme sinyalidir."""
    import re
    from urllib.parse import urlsplit
    from difflib import SequenceMatcher
    from .textutil import fold
    items = sorted(items, key=lambda i: (i.aggregator, ORDER[i.relevance.verdict]))
    def periods(item):
        return item.call_period or tuple(re.findall(r'\b20\d{2}\b', item.title))
    def compatible(a, b):
        for field in ('official_call_id', 'identity_authority', 'programme', 'application_path'):
            x, y = getattr(a, field), getattr(b, field)
            if x and y and x != y: return False
        return not (periods(a) and periods(b) and periods(a) != periods(b))
    def generic(url):
        u = urlsplit(url)
        return u.path.rstrip('/') in ('', '/apply', '/grants', '/funding', '/calls') and not u.query
    def keys(item):
        out = [canonical_url(item.source_url)]
        if item.original_url and (item.original_url_confirmed or item.original_url_evidence):
            alias = canonical_url(item.original_url)
            if not generic(alias): out.append(alias)
        return out
    def same(a, b):
        if not compatible(a, b): return False
        if a.official_call_id and b.official_call_id:
            return bool(a.identity_authority and a.identity_authority == b.identity_authority and a.official_call_id == b.official_call_id)
        common = set(keys(a)) & set(keys(b))
        if not common: return False
        if canonical_url(a.source_url) == canonical_url(b.source_url):
            return not generic(canonical_url(a.source_url)) or fold(a.title) == fold(b.title)
        return fold(a.title) == fold(b.title) or (a.original_url_confirmed and b.original_url_confirmed)
    groups = []
    for item in items:
        matches = [g for g in groups if all(compatible(item, member) for member in g) and any(same(item, member) for member in g)]
        if matches:
            group = matches[0]
            group.append(item)
            for other in matches[1:]:
                if all(compatible(a, b) for a in group for b in other):
                    group.extend(other); groups.remove(other)
        else: groups.append([item])
    kept = []
    for group in groups:
        target = group[0]
        for other in group:
            observation = {'source_id': other.source_id, 'source_url': other.source_url,
                'original_url': other.original_url, 'deadline': other.deadline.isoformat() if other.deadline else None,
                'deadline_evidence': other.deadline_evidence, 'deadline_source_url': other.deadline_source_url,
                'deadline_precision': other.deadline_precision, 'deadline_checked_at': other.deadline_checked_at}
            if observation not in target.provenance: target.provenance.append(observation)
            if other is target: continue
            target.seen_in = list(dict.fromkeys(target.seen_in + [other.source_id] + other.seen_in))
            for field in ('organization','programme','official_call_id','identity_authority','call_period','application_path','description_short'):
                if not getattr(target, field) and getattr(other, field): setattr(target, field, getattr(other, field))
            if not target.deadline and other.deadline and other.deadline_precision == 'day':
                for field in ('deadline','deadline_evidence','deadline_precision','deadline_month','deadline_source_url','deadline_checked_at','deadline_year_inferred'):
                    setattr(target, field, getattr(other, field))
            elif target.deadline and other.deadline and target.deadline != other.deadline:
                target.deadline_review_required = True
                target.relevance.verdict = 'review'
                target.relevance.reasons.append('doğrulama gerekli: kaynak son tarihleri çelişiyor')
            for candidate in other.deadline_candidates:
                if candidate not in target.deadline_candidates: target.deadline_candidates.append(candidate)
            for historic in other.deadline_history:
                if historic not in target.deadline_history: target.deadline_history.append(historic)
            target.deadline_review_required |= other.deadline_review_required
        target.seen_in = [x for x in target.seen_in if x != target.source_id]
        kept.append(target)
    for pos, a in enumerate(kept):
        for b in kept[pos+1:]:
            if SequenceMatcher(None, fold(a.title), fold(b.title)).ratio() >= .9:
                for x, y in ((a,b),(b,a)):
                    candidate = {'id':y.id,'reason':'Benzer başlık; otomatik birleştirilmedi'}
                    if candidate not in x.duplicate_candidates: x.duplicate_candidates.append(candidate)
    return kept


def run(config=None, rules=None, today=None, only=None, transport=None, sleep=None):
    config = config or load_config()
    today = today or today_fn()
    rel = RelevanceFilter(rules)
    all_items, statuses = [], []
    for source in config['sources']:
        if only is not None and source['id'] not in only:
            continue
        items, status = run_source(source, config, rel, today, transport, sleep)
        all_items.extend(items)
        statuses.append(status)
    items = dedupe(all_items)
    far = datetime(9999, 1, 1).date()
    items.sort(key=lambda i: (ORDER[i.relevance.verdict], i.deadline or far, i.title))
    groups = {v: [i.to_dict() for i in items if i.relevance.verdict == v] for v in ORDER}
    selected_all = len(statuses) == len(config['sources']) and all(
        status['id'] == source['id'] for status, source in zip(statuses, config['sources']))
    health = [status['health'] for status in statuses]
    if only is not None or not selected_all:
        run_status = 'partial'
    elif health and all(value == 'failed' for value in health):
        run_status = 'failed'
    elif 'suspicious_empty' in health and all(value in ('success', 'suspicious_empty') for value in health):
        run_status = 'suspicious_empty'
    elif any(value != 'success' for value in health):
        run_status = 'partial'
    else:
        run_status = 'success'
    return {'generated_at': datetime.now(timezone.utc).isoformat(timespec='seconds'), 'today': today.isoformat(),
            'run_status': run_status,
            'counts': {v: len(groups[v]) for v in ORDER}, 'sources': statuses,
            **{GROUPS[v]: groups[v] for v in ORDER}}


def write_report(report, path=None):
    """Raporu aynı dosya sistemindeki geçici dosyadan atomik olarak değiştir."""
    import os
    import tempfile

    path = Path(path) if path else ROOT / 'data/aggregator/latest.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(report, ensure_ascii=False, indent=2).encode('utf-8')
    fd, temp_name = tempfile.mkstemp(prefix=f'.{path.name}.', suffix='.tmp', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, path)
    except BaseException:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise
    return path


def write_health(report, path=None):
    """Her koşunun durumunu geçmişi silmeden yerel JSONL dosyasına ekle."""
    path = Path(path) if path else ROOT / 'data/aggregator/health.jsonl'
    path.parent.mkdir(parents=True, exist_ok=True)
    entry = {k: report.get(k) for k in ('generated_at', 'run_status', 'counts', 'sources')}
    with path.open('a', encoding='utf-8') as stream:
        stream.write(json.dumps(entry, ensure_ascii=False) + '\n')
    return path
