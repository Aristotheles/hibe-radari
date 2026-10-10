"""Bounded document review through the existing permitted-source fetcher."""
from datetime import date, datetime, timezone
from io import BytesIO
from urllib.parse import urlsplit, urljoin, urldefrag
from bs4 import BeautifulSoup
from .aggregator.net import Fetcher
from .auto_review import classify
from .document_review import prepare_proposal


class DailyExtractor:
    def __init__(self, store, extractor, limit=30):
        self.store, self.extractor, self.limit = store, extractor, limit
        self.model = extractor.model

    def extract(self, text, source, profile):
        day = datetime.now(timezone.utc).date().isoformat()
        if hasattr(self.store, 'db') and hasattr(self.store.db, 'collection'):
            from google.cloud import firestore
            ref = self.store.db.collection('ai_usage').document(day)
            @firestore.transactional
            def reserve(transaction):
                previous = ref.get(transaction=transaction).to_dict() or {}
                count = previous.get('reserved_calls', 0)
                if count >= self.limit:
                    raise ValueError('Günlük AI çağrı tavanı doldu')
                transaction.set(ref, dict(previous, id=day, reserved_calls=count+1))
            reserve(self.store.db.transaction())
        else:
            previous = self.store.get('ai_usage', day) or {}
            count = previous.get('reserved_calls', 0)
            if count >= self.limit:
                raise ValueError('Günlük AI çağrı tavanı doldu')
            self.store.put('ai_usage', day, dict(previous, id=day, reserved_calls=count+1))
        result = self.extractor.extract(text, source, profile)
        usage = getattr(self.extractor, 'last_usage', None)
        if isinstance(usage, dict):
            self.store.put('ai_usage_events', source['call_id'] + '-' + datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f'),
                {'id':source['call_id'], 'day':day, 'model':self.model, 'tokens':usage})
        return result


def document_text(response, max_chars=48000):
    if response.content.startswith(b'%PDF'):
        from pypdf import PdfReader
        pdf = PdfReader(BytesIO(response.content))
        if len(pdf.pages) > 100:
            raise ValueError('PDF sayfa sınırı')
        text = '\n'.join(p.extract_text() or '' for p in pdf.pages)
    elif 'html' in response.headers.get('content-type', ''):
        soup = BeautifulSoup(response.content, 'html.parser')
        for tag in soup(['script','style','nav','header','footer']):
            tag.decompose()
        text = (soup.find('main') or soup.find('article') or soup).get_text(' ', strip=True)
    else:
        raise ValueError('Çağrı belgesi HTML/PDF olmalı; liste akışı yeterli değil')
    if not text.strip() or len(text) > max_chars:
        raise ValueError('Tam metin yok veya model metin sınırını aşıyor')
    return text


def document_sections(text):
    """Bounded full coverage: retain every character, including exclusions at the end."""
    if not text.strip() or len(text)>144000:raise ValueError('Belge bölüm kapsam sınırı')
    sections=[text[start:start+24000] for start in range(0,len(text),24000)]
    assert ''.join(sections)==text
    return sections


def linked_pdf_urls(response, allowed_hosts):
    """Only PDFs actually linked in the call body, on permitted source hosts."""
    if 'html' not in response.headers.get('content-type',''):return []
    soup=BeautifulSoup(response.content,'html.parser')
    for tag in soup(['script','style','nav','header','footer']):tag.decompose()
    body=soup.find('main') or soup.find('article') or soup
    found=[]
    for anchor in body.find_all('a',href=True):
        url=urldefrag(urljoin(str(response.request.url),anchor['href']))[0]
        parts=urlsplit(url)
        try:safe=parts.scheme=='https' and parts.hostname in allowed_hosts and not parts.username and not parts.password and parts.port in (None,443)
        except ValueError:safe=False
        if safe and parts.path.lower().endswith('.pdf') and url not in found:found.append(url)
    if len(found)>10:raise ValueError('Bağlı PDF sınırı; eksik belge incelemesi başarılı sayılmadı')
    return found


def linked_document_roles(response, allowed_hosts):
    """Classify only real, already validated links; unknown attachments stay essential."""
    from .aggregator.textutil import fold
    import re
    urls=linked_pdf_urls(response,allowed_hosts)
    soup=BeautifulSoup(response.content,'html.parser')
    roles={}
    for anchor in soup.find_all('a',href=True):
        url=urldefrag(urljoin(str(response.request.url),anchor['href']))[0]
        if url not in urls:continue
        label=fold(anchor.get_text(' ',strip=True)+' '+urlsplit(url).path)
        role='unknown'
        if re.search(r'guideline|rehber|eligibility|uygunluk|criteria|kriter|terms|sartname|conditions|kosul',label):role='eligibility'
        elif re.search(r'deadline|calendar|takvim|son.basvuru',label):role='deadline'
        elif re.search(r'application|basvuru|form',label):role='application_form'
        elif re.search(r'privacy|kvkk|gizlilik|logo|poster|afis|annual.report|faaliyet.raporu',label):role='unrelated'
        roles[url]=role
    return roles


def review_batch(store, config, extractor, profile, limit=30, fetcher_factory=Fetcher):
    sources = {s['id']: s for s in config['sources']}
    settings = {s['id']: s for s in store.all('source_settings')}
    results = []
    processed = 0
    bounded = DailyExtractor(store, extractor)
    attempts = {a['id']:a for a in store.all('review_attempts')}
    for call in sorted(store.all('calls'), key=lambda c: (attempts.get(c['id'],{}).get('checked_at',''), not c.get('official_source_verified'), c['id'])):
        if classify(call, date.today())['group'] != 'candidate':
            continue
        source = sources.get(call['source_id'])
        if not source or source.get('access_policy', {}).get('terms_status') != 'allowed':
            results.append({'id':call['id'], 'status':'permission_review_required'})
            continue
        if not settings.get(call['source_id'], {}).get('enabled', source.get('enabled', True)):
            continue
        if processed >= limit:
            break
        url = call.get('official_url') or call.get('source_url')
        if not url:
            continue
        processed += 1
        hosts = source.get('allowed_hosts') or [urlsplit(source.get('url') or url).hostname]
        client = fetcher_factory(hosts, access_policy=source['access_policy'])
        try:
            if source.get('entry_url_template') and call.get('source_entry_id') and not call.get('official_url'):
                from .aggregator.feeds import entry_detail_url
                url = entry_detail_url(source, call['source_entry_id'])
            text = document_text(client.get(url))
            result = prepare_proposal(store,call['id'],[{'url':url,'text':text}],bounded,profile,hosts)
            results.append({'id':call['id'], 'status':result['status'], 'cached':result.get('cached',False)})
        except Exception as exc:
            results.append({'id':call['id'], 'status':'failed', 'error_kind':type(exc).__name__})
        finally:
            client.close()
        attempt = dict(results[-1], checked_at=datetime.now(timezone.utc).isoformat())
        store.put('review_attempts',call['id'],attempt)
    return {'results':results, 'processed':processed, 'publication_approved':False}
