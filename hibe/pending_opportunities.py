"""Public discovery view, separate from verified publication and notifications."""
import re
from .domain import version, publishable
from .evidence_context import literal_quote
from .aggregator.textutil import fold
from .llm import redact_contacts
from .review_decisions import critical_conflict
from urllib.parse import urlsplit

REASONS={'country_evidence_required':'Türkiye başvuru hakkı doğrulanmalı',
    'audience_evidence_required':'Lise, öğretmen veya okul erişimi doğrulanmalı',
    'current_deadline_required':'Güncel başvuru dönemi doğrulanmalı',
    'deadline_evidence_required':'Son başvuru tarihi doğrulanmalı',
    'application_path_required':'Başvuru yolu doğrulanmalı',
    'invalid_evidence':'Kaynak kanıtı yeniden kontrol edilmeli',
    'evidence_validation_failed':'Kaynak kanıtı yeniden kontrol edilmeli'}

def historical_announcement(url,today):
    # A dated old announcement is not evidence of a current application period.
    dated=re.search(r'/(20\d{2})/(?:0?[1-9]|1[0-2])/(?:0?[1-9]|[12]\d|3[01])(?:/|$)',urlsplit(url).path)
    return bool(dated and int(dated[1])<today.year)


def pending_preview(call,draft,item,status,today):
    if call.get('demo') or not call.get('official_source_verified') or status not in REASONS:return None
    if critical_conflict(draft):return None
    country=draft.get('country_scope') or {};target=draft.get('target_scope') or {}
    if country.get('result')=='ineligible' or target.get('result')=='ineligible':return None
    if draft.get('official_status') in ('kapandi','askida') or draft.get('opportunity_type') not in ('grant','competition','scholarship','training','exchange','project'):return None
    if draft.get('deadline') and draft['deadline']<today.isoformat():return None
    quote=draft.get('open_evidence') or ''
    if not literal_quote(quote,item['text']) or not re.search(r'(?:applications?.{0,60}(?:open|invited|accepted)|apply now|call for (?:proposals|applications)|basvur.{0,60}(?:acik|basladi|alin|davet)|(?:enrol|register).{0,60}(?:now|open))',fold(quote)):return None
    if re.search(r'closed|not open|kapandi|sona erdi',fold(quote)):return None
    years=[int(y) for y in re.findall(r'\b20\d{2}\b',quote)]
    if years and max(years)<today.year:return None
    url=call.get('official_url') or call.get('source_url') or ''
    if historical_announcement(url,today):return None
    if urlsplit(url).scheme!='https' or urlsplit(url).username or urlsplit(url).password:return None
    roles=[p.get('role') for p in draft.get('paths',[]) if p.get('role') in ('dogrudan','ortak','ogretmen_birey','ogrenci_birey')]
    if not roles:return None
    row={k:draft.get(k) for k in ('title','themes','opportunity_type')}
    row['title']=redact_contacts(row.get('title') or call['title'])
    row.update(id=call['id'],summary=redact_contacts(draft.get('summary') or ''),source_id=call['source_id'],
        source_url=url,urls=[url],deadline=None,official_status='bilinmiyor',
        publication_status='verification_pending',verification_reason=REASONS[status],
        last_checked=today.isoformat(),audience_tags=[],
        paths=[{'role':role,'conditions':[],'eligibility':'belirsiz','ranking':None} for role in dict.fromkeys(roles)])
    return row


def pending_opportunities(store,today):
    # Raw documents never need to be loaded for this public request.
    calls={c['id']:c for c in store.all('calls')};rows=[]
    for decision in store.all('publication_decisions'):
        call=calls.get(decision['id']);row=decision.get('public_preview')
        if not call or not row or decision.get('base_version')!=version(call) or publishable(call,today):continue
        if call.get('demo') or not call.get('official_source_verified') or decision.get('status') not in REASONS:continue
        if critical_conflict({'ai_conflict_fields':decision.get('conflict_fields',[])}):continue
        if historical_announcement(row.get('source_url') or '',today):continue
        if call.get('deadline') and call['deadline']<today.isoformat():continue
        rows.append(row)
    return rows
