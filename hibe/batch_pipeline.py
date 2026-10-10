"""Submit source-refresh candidates and finish discounted AI jobs without another scan."""
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from zoneinfo import ZoneInfo
from .aggregator.collector import ROOT
from .aggregator.net import Fetcher
from .aggregator.feeds import entry_detail_url
from .auto_review import classify
from .domain import version, publishable
from .review_batch import document_text, linked_pdf_urls, linked_document_roles, document_sections
from .scan import normalized_hash
from .gemini_batch import GeminiBatch, POLICY
from .batch_publication import publish_batch


def finish_batches(store, api=None, processing_owner=None):
    from .job_lease import processing_lease, owns_lease
    if processing_owner:
        if not owns_lease(store,'ai_batch_result_processing',processing_owner):raise ValueError('Geçerli iş sahipliği gerekli')
        return _finish_batches(store,api)
    with processing_lease(store,'ai_batch_result_processing') as acquired:
        if not acquired:
            return {'status':'processing_elsewhere','batches':[],
                'pending':sum(j.get('status') in ('submitted','submitting','submission_uncertain') for j in store.all('ai_batches'))}
        return _finish_batches(store,api)


def _finish_batches(store, api=None):
    api=api or GeminiBatch()
    results=[]
    for job in store.all('ai_batches'):
        if not job.get('name') or job.get('status')=='failed':continue
        if job.get('status')!='completed':job=api.poll(store,job['id'])
        if job.get('status')=='completed' and not job.get('publication_processed'):
            job['publication_results']=publish_batch(store,job)
            job['publication_processed']=True
            store.put('ai_batches',job['id'],job)
        results.append({k:job.get(k) for k in ('id','status','state','publication_results','missing_ids')})
    return {'batches':results,'pending':sum(r['status'] in ('submitted','submitting','submission_uncertain') for r in results)}


def submit_candidates(store, config, api=None):
    api=api or GeminiBatch()
    today=datetime.now(ZoneInfo('Europe/Istanbul')).date()
    sources={s['id']:s for s in config['sources']}
    pending_jobs={j['id'] for j in store.all('ai_batches') if j.get('status') in ('submitted','submitting','submission_uncertain')}
    pending_inputs={i['id']:i for i in store.all('ai_batch_inputs') if i.get('batch_id') in pending_jobs}
    reviewed_jobs={j['id'] for j in store.all('ai_batches') if j.get('policy',0)>=POLICY}
    reviewed_inputs={}
    for item in store.all('ai_batch_inputs'):
        if item.get('batch_id') in reviewed_jobs:reviewed_inputs.setdefault(item['id'],[]).append(item)
    settings={s['id']:s for s in store.all('source_settings')}
    disabled={ident for setting in settings.values() if setting.get('enabled') is False
        for ident in setting.get('connector_ids',[])}
    clients={};locks={}
    for ident,source in sources.items():
        if (source.get('access_policy',{}).get('terms_status')=='allowed'
                and ident not in disabled
                and settings.get(ident,{}).get('enabled',source.get('enabled',True))):
            clients[ident]=Fetcher(source['allowed_hosts'],delay=config.get('delay_seconds',1),
                cache_dir=ROOT/'data/aggregator/http-cache',access_policy=source['access_policy'])
            locks[ident]=threading.Lock()
    def gather(call):
        approved=call.get('approval',{}).get('reviewed') is True and call.get('approval',{}).get('version')==version(call)
        if call.get('demo'):return None
        scoped_discovery=sources.get(call.get('source_id'),{}).get('type') in ('source_discovery','grants_gov')
        if call.get('source_id')!='esep-courses' and not scoped_discovery and classify(call,today)['group']!='candidate':return None
        if call['source_id'] not in clients:return {'id':call['id'],'status':'permission_review_required'}
        source=sources[call['source_id']]
        url=call.get('official_url') or call.get('source_url')
        try:
            if source.get('type')!='grants_gov' and source.get('entry_url_template') and call.get('source_entry_id') and not call.get('official_url'):
                url=entry_detail_url(source,call['source_entry_id'])
            with locks[call['source_id']]:
                pdf_urls=[];document_roles={};document_errors=[]
                if source.get('type')=='grants_gov':
                    from .aggregator.grants_gov import detail_text
                    text=detail_text(source,clients[call['source_id']],call['source_entry_id'])
                else:
                    response=clients[call['source_id']].get(url)
                    selector=source.get('review_body_selector')
                    text=document_text(response,max_chars=144000,selector=selector)
                    pdf_urls=linked_pdf_urls(response,source['allowed_hosts'],selector=selector)
                    document_roles=linked_document_roles(response,source['allowed_hosts'],selector=selector)
            documents=[{'url':url,'hash':normalized_hash(text)}]
            document_texts=[{'url':url,'text':text}]
            support_urls=source.get('review_support_urls',[])+source.get('review_support_pages',{}).get(url,[])
            for support_url in dict.fromkeys(pdf_urls+support_urls):
                if support_url==url:continue
                try:
                    with locks[call['source_id']]:support=document_text(clients[call['source_id']].get(support_url),max_chars=144000)
                except Exception as exc:
                    role=document_roles.get(support_url,'eligibility')
                    document_errors.append({'url':support_url,'role':role,'error_kind':type(exc).__name__})
                    if role!='unrelated':
                        store.put('review_document_errors',call['id'],{'id':call['id'],
                            'category':'technical_document_error','missing_fields':['country','target','deadline'],
                            'documents':document_errors,'checked_on':today.isoformat()})
                        raise
                    continue
                documents.append({'url':support_url,'hash':normalized_hash(support)})
                document_texts.append({'url':support_url,'text':support})
            text='\n'.join(d['text'] for d in document_texts)
            sections=document_sections(text)
            previous_error=store.get('review_document_errors',call['id'])
            if previous_error:
                # Keep the audit trail, but a sidebar attachment removed from the
                # observed article is not an outstanding application requirement.
                store.put('review_document_errors',call['id'],{
                    'id':call['id'],'status':'resolved','checked_on':today.isoformat(),
                    'base_version':version(call),'documents':document_errors,
                    'resolved_documents':documents,'previous_errors':previous_error.get('previous_errors',[])+previous_error.get('documents',[])})
            if approved and call.get('documents')==documents:
                from .verified_review import commit_verified_review
                approval=call['approval']
                commit_verified_review(store,call['id'],call,version(call),{d['url']:d['text'] for d in document_texts},
                    approval_authority=approval['authority'],reviewer=approval.get('agent','Codex'),batch_id=approval.get('batch_id'))
                return None
            if approved:
                call['document_changes_pending']=True
                call.pop('approval',None)
                store.put('calls',call['id'],call)
            previous=store.get('review_proposals',call['id'])
            # Metadata-only rediscovery must not charge for an identical, already reviewed document.
            if (previous and previous.get('batch_id') and call.get('discovery_changes_pending')
                    and call.get('documents')==documents and previous['draft'].get('documents')==documents
                    and previous['draft'].get('title')==call.get('title')
                    and previous['draft'].get('source_id')==call['source_id']):
                previous['base_version']=version(call)
                store.put('review_proposals',call['id'],previous)
                job=store.get('ai_batches',previous['batch_id'])
                if job:
                    decisions=publish_batch(store,dict(job,results=[{'id':call['id'],'status':'evidence_review_required'}]),today)
                    if job.get('policy',0)>=POLICY or any(r['status'] in ('published','closed','out_of_scope') for r in decisions):return None
            pending=pending_inputs.get(call['id'])
            if pending and pending.get('baseline')==version(call) and pending.get('documents')==documents:return None
            if any(i.get('baseline')==version(call) and i.get('documents')==documents for i in reviewed_inputs.get(call['id'],[])):
                if previous_error and previous and previous.get('base_version')==version(call):
                    job=store.get('ai_batches',previous.get('batch_id'))
                    if job:publish_batch(store,dict(job,results=[{'id':call['id'],'status':'evidence_review_required'}]),today)
                return None
            if (previous and previous.get('batch_id') and previous.get('base_version')==version(call)
                    and previous['draft'].get('documents')==documents):
                decision=store.get('publication_decisions',call['id']) or {}
                old_job=store.get('ai_batches',previous['batch_id']) or {}
                if old_job.get('policy',0)>=POLICY or decision.get('status') in ('published','closed','out_of_scope'):return None
            return {'id':call['id'],'title':call['title'],'baseline':version(call),'text':text,
                    'documents':documents,'document_texts':document_texts,'document_errors':document_errors,
                    'sections':sections if len(text)>48000 else None}
        except Exception as exc:
            error={'id':call['id'],'status':'document_unavailable','category':'technical_document_error',
                'error_kind':type(exc).__name__,'checked_on':today.isoformat()}
            store.put('review_document_errors',call['id'],dict(store.get('review_document_errors',call['id']) or {},**error))
            return error
    inputs=[];errors=[]
    try:
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures=[executor.submit(gather,c) for c in store.all('calls')]
            for future in as_completed(futures):
                result=future.result()
                if result:(inputs if 'text' in result else errors).append(result)
    finally:
        for client in clients.values():client.close()
    if not inputs:return {'status':'no_new_documents','errors':errors}
    # Never silently discard excess candidates or resubmit an ambiguous job.
    inputs.sort(key=lambda item:item['id'])
    jobs=[api.submit(store,inputs[start:start+250],today.isoformat()) for start in range(0,len(inputs),250)]
    return {'status':'submitted','batch_ids':[job['id'] for job in jobs],'submitted':len(inputs),'errors':errors}
