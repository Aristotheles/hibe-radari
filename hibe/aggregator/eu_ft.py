"""AB Funding & Tenders portalının kamuya açık arama API'si (SEDIA).

Tarayıcıdaki portal aynı uç noktayı kullanır; kazıma yok, yapılandırılmış JSON gelir.
Not: Erasmus+ okul eğitimi KA1/KA2 çağrıları ulusal ajanslarda (Türkiye'de ua.gov.tr) yürür ve
bu portalda görünmez; burada yalnız merkezî eylemler ve okullara değen diğer AB programları çıkar."""
import json
from datetime import date

from .models import GrantOpportunity
from .textutil import shorten, strip_html
from .net import FetchError

API = 'https://api.tech.ec.europa.eu/search-api/prod/rest/search'
PORTAL = 'https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/opportunities/topic-details/'
FRAMEWORKS = {'43353764': 'Erasmus+'}
OPEN_STATUSES = ['31094501', '31094502']          # yaklaşan, açık
TYPES = ['1', '2', '8']                           # konu/çağrı türleri


def build_query(framework=None):
    must = [{'terms': {'type': TYPES}}, {'terms': {'status': OPEN_STATUSES}}]
    if framework:
        must.append({'terms': {'frameworkProgramme': [framework]}})
    return {'bool': {'must': must}}


def _first(meta, key, default=None):
    value = meta.get(key)
    if isinstance(value, list):
        return value[0] if value else default
    return value if value is not None else default


def _dates(meta):
    out = []
    for raw in meta.get('deadlineDate') or []:
        try:
            out.append(date.fromisoformat(raw[:10]))
        except ValueError:
            pass
    return out


def parse(payload, source, today):
    seen, items = set(), []
    for result in payload.get('results', []):
        meta = result.get('metadata', {})
        ident = _first(meta, 'identifier')
        if not ident or ident in seen:
            continue
        seen.add(ident)
        deadlines = _dates(meta)
        future = [d for d in deadlines if d >= today]
        deadline = min(future) if future else (max(deadlines) if deadlines else None)
        desc = strip_html(_first(meta, 'descriptionByte', '') or result.get('summary', '')).strip("[]' ")
        framework = _first(meta, 'frameworkProgramme')
        items.append(GrantOpportunity(
            title=_first(meta, 'title') or result.get('title') or ident,
            source_id=source['id'], source_url=PORTAL + ident,
            official_call_id=ident, identity_authority='eu-ft',
            organization=source.get('organization', 'Avrupa Komisyonu'),
            deadline=deadline,
            deadline_evidence=f"API deadlineDate: {', '.join(d.isoformat() for d in deadlines)}" if deadlines else None,
            deadline_candidates=[{'value': d.isoformat(), 'precision': 'day', 'evidence': 'API deadlineDate'} for d in deadlines],
            programme=FRAMEWORKS.get(framework), description_short=shorten(desc, 300),
            language='en', categories=[_first(meta, 'typesOfAction') or ''] if _first(meta, 'typesOfAction') else []))
    return items


def collect(source, fetcher, today):
    items = []
    page_size = source.get('page_size', 50)
    max_pages = source.get('max_pages', 10)
    if type(page_size) is not int or not 1 <= page_size <= 100 or type(max_pages) is not int or not 1 <= max_pages <= 50:
        raise FetchError('API sayfalama sınırı geçersiz', 'parser')
    for query in source['queries']:
        params = {'apiKey': 'SEDIA', 'text': query.get('text', '***'),
                  'pageSize': page_size}
        files = {'query': (None, json.dumps(build_query(query.get('framework'))), 'application/json'),
                 'languages': (None, '["en"]', 'application/json')}
        fetched = 0; fingerprints = set()
        for page in range(1, max_pages + 1):
            response = fetcher.request('POST', API, params=dict(params, pageNumber=page), files=files)
            payload = response.json()
            if not isinstance(payload, dict) or not isinstance(payload.get('results'), list):
                raise FetchError('API sonuç şeması değişti', 'parser')
            rows = payload['results']; total = payload.get('totalResults')
            if isinstance(total, str) and total.isdecimal(): total = int(total)
            if total is not None and (type(total) is not int or total < 0):
                raise FetchError('API toplam sonuç sayısı geçersiz', 'parser')
            fingerprint = json.dumps(rows, sort_keys=True)
            if rows and fingerprint in fingerprints:
                raise FetchError('API aynı sayfayı tekrar döndürdü; eksik toplama', 'parser')
            fingerprints.add(fingerprint); fetched += len(rows)
            if total is not None and fetched > total:
                raise FetchError('API toplamı sayfalarla çelişiyor', 'parser')
            items.extend(parse(payload, source, today))
            if total is not None and fetched >= total or total is None and len(rows) < page_size:
                break
            if not rows:
                raise FetchError('API beklenen sonuçlardan önce boş sayfa döndürdü', 'parser')
        else:
            raise FetchError('API sayfa tavanında tamamlanmadı; eksik toplama', 'parser')
    return items
