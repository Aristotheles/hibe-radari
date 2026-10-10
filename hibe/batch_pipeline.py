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
from .review_batch import document_text
from .scan import normalized_hash
from .gemini_batch import GeminiBatch
from .batch_publication import publish_batch


def finish_batches(store, api=None):
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
    settings={s['id']:s for s in store.all('source_settings')}
    clients={};locks={}
    for ident,source in sources.items():
        if (source.get('access_policy',{}).get('terms_status')=='allowed'
                and settings.get(ident,{}).get('enabled',source.get('enabled',True))):
            clients[ident]=Fetcher(source['allowed_hosts'],delay=config.get('delay_seconds',1),
                cache_dir=ROOT/'data/aggregator/http-cache',access_policy=source['access_policy'])
            locks[ident]=threading.Lock()
    def gather(call):
        approved=call.get('approval',{}).get('reviewed') is True and call.get('approval',{}).get('version')==version(call)
        if call.get('demo'):return None
        if call.get('source_id')!='esep-courses' and classify(call,today)['group']!='candidate':return None
        if call['source_id'] not in clients:return {'id':call['id'],'status':'permission_review_required'}
        source=sources[call['source_id']]
        url=call.get('official_url') or call.get('source_url')
        try:
            if source.get('entry_url_template') and call.get('source_entry_id') and not call.get('official_url'):
                url=entry_detail_url(source,call['source_entry_id'])
            with locks[call['source_id']]:text=document_text(clients[call['source_id']].get(url))
            documents=[{'url':url,'hash':normalized_hash(text)}]
            document_texts=[{'url':url,'text':text}]
            for support_url in source.get('review_support_urls',[]):
                with locks[call['source_id']]:support=document_text(clients[call['source_id']].get(support_url))
                documents.append({'url':support_url,'hash':normalized_hash(support)})
                document_texts.append({'url':support_url,'text':support})
            text='\n'.join(d['text'] for d in document_texts)
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
                    publish_batch(store,dict(job,results=[{'id':call['id'],'status':'evidence_review_required'}]),today)
                    return None
            pending=pending_inputs.get(call['id'])
            if pending and pending.get('baseline')==version(call) and pending.get('documents')==documents:return None
            if (previous and previous.get('batch_id') and previous.get('base_version')==version(call)
                    and previous['draft'].get('documents')==documents):return None
            return {'id':call['id'],'title':call['title'],'baseline':version(call),'text':text,
                    'documents':documents,'document_texts':document_texts}
        except Exception as exc:return {'id':call['id'],'status':'document_unavailable','error_kind':type(exc).__name__}
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
