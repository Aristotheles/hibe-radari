"""RSS/Atom okuyucu (feedparser): ab-ilan.com, TÜBİTAK 4000 gibi kaynaklar."""
from datetime import date

import feedparser
from urllib.parse import urlsplit

from .models import GrantOpportunity
from .textutil import find_deadline, shorten, strip_html


def collect(source, fetcher, today):
    parsed = feedparser.parse(fetcher.get(source['url']).content)
    if parsed.bozo:
        raise ValueError(f'Bozuk RSS/Atom: {type(parsed.bozo_exception).__name__}')
    if not parsed.version:
        raise ValueError('RSS/Atom biçimi tanınmadı')
    items = []
    for entry in parsed.entries:
        link = (entry.get('link') or '').strip()
        guid = (entry.get('id') or '').strip()
        if source.get('entry_identity') == 'guid_url':
            parts = urlsplit(guid)
            if parts.scheme != 'https' or parts.hostname not in source['allowed_hosts'] or parts.username or parts.password or parts.port not in (None, 443):
                raise ValueError('RSS GUID izinli ayrıntı URL şemasına uymuyor')
            link = guid
        title = strip_html(entry.get('title', ''))
        if not link or not title:
            continue
        if source.get('upgrade_http') and link.startswith('http://'):
            link = 'https://' + link[len('http://'):]
        text = strip_html(entry.get('summary') or entry.get('description') or '')
        published = entry.get('published_parsed') or entry.get('updated_parsed')
        items.append(GrantOpportunity(
            title=title, source_id=source['id'], source_url=link,
            organization=source.get('organization'),
            source_entry_id=guid if source.get('entry_identity') else None,
            identity_authority=source['id'] if source.get('entry_identity') else None,
            description_short=shorten(text, 300), language=source.get('language'),
            published_at=date(*published[:3]) if published and not source.get('ignore_published') else None,
            categories=[t.term for t in entry.get('tags', []) if t.get('term')]))
        items[-1].apply_deadline(f'{title}. {text}', today)
    return items
