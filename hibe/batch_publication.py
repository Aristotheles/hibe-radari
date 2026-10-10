"""Automatic publication requires primary-source, country, audience and date evidence."""
import re
from copy import deepcopy
from datetime import date
from .aggregator.textutil import fold, deadline_details
from .domain import version
from .verified_review import commit_verified_review


def quote_present(quote,text):
    return isinstance(quote,str) and len(quote.strip())>=12 and ' '.join(fold(quote).split()) in ' '.join(fold(text).split())

def schedule_is_open(schedule,text):
    quote=schedule.get('evidence') or ''
    if not quote_present(quote,text):return False
    if schedule.get('kind')=='rolling':return bool(re.search(r'rolling basis|rolling applications|yil boyunca|surekli basvuru',fold(quote)))
    if schedule.get('kind')!='self_paced':return False
    return bool(re.search(r'open for self-paced learning|self-paced and open-ended|self-paced course is already available online',fold(quote))
        or ('self-paced course is already available online' in fold(text) and re.search(r'no deadlines|own pace|self-paced',fold(quote))))


def publication_decision(current, draft, item, today):
    text=item['text']
    if current.get('demo') or draft.get('demo'):
        return 'invalid_evidence'
    country=draft.get('country_scope') or {}
    target=draft.get('target_scope') or {}
    if not isinstance(country,dict) or not isinstance(target,dict):return 'invalid_evidence'
    if country.get('result')=='ineligible' or target.get('result')=='ineligible':
        rejected=country if country.get('result')=='ineligible' else target
        return 'out_of_scope' if quote_present(rejected.get('evidence'),text) else 'invalid_evidence'
    if draft.get('official_status') in ('kapandi','askida'):
        return 'closed'
    if draft.get('ai_conflict'):return 'invalid_evidence'
    if not current.get('official_source_verified'):
        return 'primary_source_required'
    if current.get('source_id')=='esep-courses':
        levels=re.search(r'Education levels:(.*?)Target audience type:',text,re.S|re.I)
        if not levels or 'upper secondary' not in fold(levels[1]):return 'audience_evidence_required'
    country_quote=country.get('evidence') or ''
    universal_course=(current.get('source_id')=='esep-courses' and draft.get('opportunity_type')=='training'
        and quote_present('This platform is free of charge for all users.',text)
        and 'free of charge for all users' in fold(country_quote))
    if (country.get('result')!='eligible' or not quote_present(country_quote,text)
            or not (universal_course or re.search(r'\b(?:turkey|turkiye|all countries|any country|every country|worldwide|anywhere in the world|around the world|tum ulkeler|her ulke)\b',fold(country_quote)))):
        return 'country_evidence_required'
    target_quote=target.get('evidence') or ''
    if (target.get('result')!='eligible' or not quote_present(target_quote,text)
            or not set(target.get('targets',[])) & {'school','teacher','student'}
            or not re.search(r'lise|secondary|high school|pupil|school education|teachers?|educators?|schools',fold(target_quote))):
        return 'audience_evidence_required'
    if not any(p.get('role') in ('dogrudan','ortak','ogretmen_birey','ogrenci_birey') for p in draft.get('paths',[])):
        return 'application_path_required'
    deadline=draft.get('deadline')
    schedule=draft.get('application_schedule') or {}
    if not deadline and schedule.get('kind') in ('rolling','self_paced'):
        quote=schedule.get('evidence') or ''
        return 'eligible' if draft.get('official_status')=='acik' and schedule_is_open(schedule,text) else 'current_deadline_required'
    if not deadline or date.fromisoformat(deadline)<today:
        return 'current_deadline_required'
    evidence=draft.get('deadline_evidence')
    if not quote_present(evidence,text):
        return 'deadline_evidence_required'
    parsed=deadline_details(evidence,today)
    if parsed['year_inferred'] or not any(c['value']==deadline for c in parsed['candidates']):
        return 'deadline_evidence_required'
    return 'eligible'


def publish_batch(store, job, today=None):
    today=today or date.today()
    results=[]
    for result in job.get('results',[]):
        if result['status']!='evidence_review_required':continue
        ident=result['id'];proposal=store.get('review_proposals',ident)
        current=store.get('calls',ident)
        item=store.get('ai_batch_inputs',job['id']+'-'+ident)
        if not proposal or proposal.get('batch_id')!=job['id'] or not current or not item:
            results.append({'id':ident,'status':'missing_input'});continue
        if version(current)!=proposal['base_version']:
            # A completed publication can be observed again without revocation or repetition.
            existing=current.get('approval',{})
            results.append({'id':ident,'status':'already_published' if existing.get('batch_id')==job['id'] and existing.get('version')==version(current) else 'stale'})
            continue
        draft=proposal['draft']
        decision=publication_decision(current,draft,item,today)
        if decision=='eligible':
            call=deepcopy(current);call.update(deepcopy(draft))
            for field in ('budget_max','currency'):
                if draft.get(field) is None and current.get(field) is not None:call[field]=current[field]
            url=item['documents'][0]['url']
            call.update(official_url=url,official_url_verified=True,deadline_precision='day',
                deadline_year_inferred=False,deadline_review_required=False,deadline_source_url=url,
                reviewed_discovery_version=current.get('discovery_version'),
                audience_tags=[t for t in draft['target_scope']['targets'] if t in ('school','teacher','student')])
            if not call.get('deadline'):
                call['deadline_precision']='not_applicable'
                call['application_schedule']['source_url']=url
            call.pop('discovery_changes_pending',None)
            try:
                commit_verified_review(store,ident,call,proposal['base_version'],
                    {d['url']:d['text'] for d in item['document_texts']},
                    approval_authority='verified_ai_batch_review',reviewer=job['model'],batch_id=job['id'])
                decision='published'
            except ValueError:
                decision='evidence_validation_failed'
        record={'id':ident,'status':decision,'batch_id':job['id'],'base_version':proposal['base_version'],'checked_on':today.isoformat()}
        store.put('publication_decisions',ident,record);results.append(record)
    return results
