"""Grounded extraction proposals for existing calls, without approval or overwrite."""
from urllib.parse import urlsplit
import hashlib
import json
from .domain import version, validate
from .llm import extract_with_fallback
from .scan import normalized_hash


def prepare_proposal(store, ident, document_texts, extractor, profile, allowed_hosts):
    current = store.get('calls', ident)
    if not current:
        raise ValueError('Çağrı bulunamadı')
    baseline = version(current)
    texts = []
    documents = []
    for doc in document_texts:
        url = urlsplit(doc['url'])
        if url.scheme != 'https' or url.hostname not in allowed_hosts or url.username or url.password or url.port not in (None, 443):
            raise ValueError('İzinli resmî belge URL gerekli')
        text = doc.get('text')
        if not isinstance(text, str) or not text.strip():
            raise ValueError('Resmî belge metni eksik')
        texts.append(text)
        documents.append({'url': doc['url'], 'hash': normalized_hash(text)})
    if not documents:
        raise ValueError('Belge gerekli')
    inputs = {'documents': documents, 'profile': profile,
              'model': getattr(extractor, 'model', type(extractor).__name__),
              'evidence_policy': 1}
    fingerprint = hashlib.sha256(json.dumps(inputs, sort_keys=True,
        ensure_ascii=False, separators=(',', ':')).encode('utf-8')).hexdigest()
    previous = store.get('review_proposals', ident)
    if (previous and previous.get('input_fingerprint') == fingerprint
            and previous.get('base_version') == baseline
            and previous.get('status') == 'evidence_review_required'):
        validate(previous['draft'])
        return dict(previous, cached=True)
    source = {'id': current['source_id'], 'call_id': ident, 'title': current['title'],
              'documents': documents, 'document_texts': document_texts}
    draft = extract_with_fallback(extractor, '\n\n'.join(texts), source, profile)
    draft.pop('approval', None)
    draft.pop('version', None)
    # A failed model must not replace a successful proposal or curated call.
    if draft.get('ai_status') == 'unavailable':
        return {'status': 'unavailable', 'error_kind': draft.get('ai_error_kind')}
    validate(draft)
    latest = store.get('calls', ident)
    if not latest or version(latest) != baseline:
        return {'status': 'stale'}
    proposal = {'id': ident, 'base_version': baseline, 'draft': draft,
                'status': 'evidence_review_required', 'publication_approved': False,
                'input_fingerprint': fingerprint}
    store.put('review_proposals', ident, proposal)
    return proposal
