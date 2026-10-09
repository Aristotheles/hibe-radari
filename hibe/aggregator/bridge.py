"""Keşif üstverisini mevcut records/calls deposuna taşır; yayın için Service onayı gerekir."""
import copy
import hashlib
import json
from urllib.parse import urlsplit
from hibe.domain import version, publishable
from hibe.service import now

GROUPS = ('accepted', 'review', 'watch', 'general', 'rejected')
VOLATILE = {'deadline_checked_at', 'deadline_history', 'duplicate_candidates', 'provenance', 'seen_in', 'relevance'}

def discovery_version(row):
    def semantic(value):
        if isinstance(value,dict): return {k:semantic(v) for k,v in value.items() if k not in ('checked_at','deadline_checked_at')}
        if isinstance(value,list): return [semantic(v) for v in value]
        return value
    content = semantic({k:v for k,v in row.items() if k not in VOLATILE})
    return hashlib.sha256(json.dumps(content,sort_keys=True,ensure_ascii=False).encode()).hexdigest()

def persist_report(report, store):
    """Başarısız/kısmi koşudaki bulunan kayıtları da saklar; yokluk silme değildir."""
    # Önce tüm gözlemleri doğrula; bozuk satır ilk kayıtları kısmen yazmasın.
    import re
    for group in GROUPS:
        for row in report.get(group, []):
            if not isinstance(row.get('id'),str) or not re.fullmatch(r'[a-zA-Z0-9_-]{1,100}',row['id']):
                raise ValueError('Geçersiz keşif kimliği')
            if not row.get('title') or not row.get('source_id') or not row.get('source_url'):
                raise ValueError('Keşif başlık/kaynak/URL alanı eksik')
    changed = 0
    source_changes = {}
    for group in GROUPS:
        for raw in report.get(group, []):
            row = copy.deepcopy(raw); ident = row['id']; digest = discovery_version(row)
            old = store.get('discoveries', ident)
            # Eksik bilgi mevcut kesin tarih/kanıtı silemez.
            if old:
                prior = old['observation']
                for key in ('deadline','deadline_evidence','deadline_source_url','deadline_month','organization','description_short','original_url'):
                    if not row.get(key) and prior.get(key): row[key] = prior[key]
                if row.get('deadline') and not raw.get('deadline'):
                    row['deadline_precision'] = prior.get('deadline_precision','day')
                    row['deadline_year_inferred'] = prior.get('deadline_year_inferred',False)
                digest = discovery_version(row)
            if not old or old['version'] != digest:
                source_changes[row['source_id']] = source_changes.get(row['source_id'],0) + 1
            history = (old or {}).get('history', [])
            if old and old['version'] != digest:
                history = history + [{'version':old['version'],'observation':old['observation'],'at':old['last_seen_at']}]
            call = store.get('calls',ident)
            if call and not call.get('from_aggregator'):
                raise ValueError('Keşif kimliği mevcut manuel çağrı ile çakışıyor')
            if not call:
                from .models import canonical_url
                from .textutil import fold
                # Önceden elle/pipeline ile kaydedilmiş aynı çağrı yeni kimlikle çoğalmasın.
                matches=[]
                for candidate in store.all('calls'):
                    urls=[candidate.get('source_url')] + [d.get('url') for d in candidate.get('documents',[])]
                    if fold(candidate.get('title','')) != fold(row['title']): continue
                    if any(row.get(k) and candidate.get(k) and row[k]!=candidate[k] for k in ('official_call_id','call_period','application_path')): continue
                    if any(url and canonical_url(url)==canonical_url(row['source_url']) for url in urls): matches.append(candidate)
                if len(matches)==1: call=matches[0]
            record = {'id':ident,'version':digest,'observation':row,'group':group,
                'first_seen_at':(old or {}).get('first_seen_at',now()),'last_seen_at':now(),'history':history,'call_id':call['id'] if call else ident}
            store.put('discoveries',ident,record)
            if not call:
                call = dict(row, from_aggregator=True, discovery_version=digest,
                    reviewed_discovery_version=None, official_url_verified=False,
                    summary='', themes=[], official_status='bilinmiyor',
                    documents=[{'url':row['source_url'],'hash':digest,'kind':'discovery_metadata'}],
                    paths=[{'role':'belirsiz','conditions':[{'text':'Resmî başvuru koşulları editör tarafından incelenmeli','result':'bilinmiyor','evidence':None}]}])
                call['deadline'] = row.get('deadline') if row.get('deadline_precision') == 'day' and not row.get('deadline_year_inferred') else None
            elif call.get('discovery_version') != digest:
                call['from_aggregator'] = True
                for key, value in row.items():
                    if key not in call: call[key] = value
                call['discovery_version'] = digest
                call.pop('approval',None)
                call['discovery_changes_pending'] = True
            else:
                continue
            call['version'] = version(call)
            store.put('calls',call['id'],call); changed += 1
    for health in report.get('sources',[]):
        prior=store.get('source_health',health['id']) or {}
        successful=health.get('health')=='success'
        store.put('source_health',health['id'],dict(health,checked_at=report.get('generated_at'),
            last_success=report.get('generated_at') if successful else prior.get('last_success'),
            last_error=health.get('error') or prior.get('last_error'),
            last_found_count=health.get('fetched') if successful else prior.get('last_found_count'),
            changed_count=source_changes.get(health['id'],0)))
    return changed

def review_ready(call):
    if not call.get('from_aggregator'): return True
    import re
    if not re.fullmatch(r'[a-f0-9]{64}',call.get('discovery_version') or ''): return False
    if call.get('discovery_version') != call.get('reviewed_discovery_version'): return False
    if not call.get('official_url_verified') or not call.get('summary','').strip(): return False
    url = call.get('official_url',''); parts=urlsplit(url)
    return bool(parts.scheme == 'https' and parts.hostname and not parts.username and
                any(doc.get('url') == url for doc in call.get('documents',[])))

def publication_report(report, store, today):
    result = {k:copy.deepcopy(v) for k,v in report.items() if k not in GROUPS}
    result.update({g:[] for g in GROUPS})
    for call in store.all('calls'):
        if call.get('from_aggregator') and review_ready(call) and publishable(call,today):
            targets=call.get('eligibility_assessment',{}).get('targets',{})
            statuses=[targets.get(k,{}).get('status') for k in ('school','teacher','student_14_18','school_partner')]
            group='accepted' if 'UYGUN' in statuses else 'review'
            result[group].append(call)
    result['counts'] = dict(report.get('counts',{}),accept=len(result['accepted']),review=len(result['review']),watch=0,general=0,reject=0)
    return result
