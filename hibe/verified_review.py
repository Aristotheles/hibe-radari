"""Commit a verified, version-bound review without impersonating a human admin."""
from copy import deepcopy
from datetime import date
import re
from .domain import version, validate
from .service import now


def commit_verified_review(store, ident, reviewed_call, baseline, evidence_texts,
                           approval_authority='verified_agent_review', reviewer='Codex', batch_id=None):
    if approval_authority not in ('verified_agent_review','verified_ai_batch_review') or (approval_authority=='verified_ai_batch_review' and not batch_id):
        raise ValueError('Doğrulanmış inceleme yetkisi gerekli')
    current = store.get('calls', ident)
    if not current or version(current) != baseline:
        raise ValueError('İnceleme sırasında çağrı değişti')
    call = deepcopy(reviewed_call)
    validate(call)
    if call['id'] != ident or call.get('demo') or not call.get('official_source_verified'):
        raise ValueError('Doğrulanmış resmî çağrı gerekli')
    schedule=call.get('application_schedule') or {}
    rolling=not call.get('deadline') and schedule.get('kind') in ('rolling','self_paced')
    if rolling:
        from .batch_publication import schedule_is_open
        quote=schedule.get('evidence') or ''
        text=evidence_texts.get(schedule.get('source_url'),'')
        if (call['official_status']!='acik' or not schedule_is_open(schedule,text)
                or schedule.get('source_url') not in [d['url'] for d in call['documents']]
                ):
            raise ValueError('Sürekli açık başvuru kanıtı gerekli')
    else:
        if not call.get('deadline') or date.fromisoformat(call['deadline']) < date.today():
            raise ValueError('Güncel kesin son tarih gerekli')
        if call.get('deadline_precision') != 'day' or call.get('deadline_year_inferred') or not call.get('deadline_evidence'):
            raise ValueError('Tarih kanıtı gerekli')
        if not evidence_texts or call.get('deadline_source_url') not in evidence_texts:
            raise ValueError('Resmî tarih belgesi gerekli')
    from .llm import validate_evidence
    source={'documents':call['documents'], 'document_texts':[{'url':url,'text':text} for url,text in evidence_texts.items()]}
    expected_deadline=call['deadline']
    checked=validate_evidence(call,'\n'.join(evidence_texts.values()),source)
    if checked.get('deadline') != expected_deadline:
        raise ValueError('Son tarih belgeyle uyuşmuyor')
    call.pop('approval',None)
    call['last_verified_at']=now()
    call['version']=version(call)
    call['approval']={'reviewed':True,'version':call['version'],'at':now(),
        'authority':approval_authority,'agent':reviewer,'demo':False}
    if batch_id:call['approval']['batch_id']=batch_id
    store.put('calls',ident,call)
    return call
