"""Statik HTML kaynakları (BeautifulSoup): bağlantı listesi, küçük tarama ve ayrıntı sayfası zenginleştirme.

JavaScript çalıştırılmaz; yalnız sunucunun gönderdiği HTML okunur."""
import re
from datetime import date
from urllib.parse import urljoin, urlsplit

from bs4 import BeautifulSoup

from .models import GrantOpportunity, canonical_url
from .textutil import find_deadline, shorten

NOISE_HOSTS = ('facebook.com', 'twitter.com', 'x.com', 'instagram.com', 'linkedin.com', 'youtube.com',
               'youtu.be', 'whatsapp.com', 't.me', 'telegram.me', 'google.com', 'pinterest.com', 'wa.me')
HINT = re.compile(r'basvur|başvur|apply|application|official|resm|detay|detail|ayrinti|ayrıntı|kaynak|link|web|website|click|tikla|tıkla|antrag', re.I)


def _soup(html):
    return BeautifulSoup(html, 'html.parser')


def _page_title(soup):
    for selector in ('h1', 'h2', 'h3'):
        node = soup.select_one(selector)
        if node and len(node.get_text(strip=True)) > 8:
            return re.sub(r'\s+', ' ', node.get_text(' ', strip=True))
    return re.sub(r'\s+[|–—-]\s+[^|–—]*$', '', soup.title.get_text(strip=True)) if soup.title else ''


def collect_list(source, fetcher, today):
    """Liste sayfasındaki duyuru bağlantıları (href deseni config'ten). Tarih ayrıntıdan gelir."""
    pattern = re.compile(source['link_pattern'])
    items, seen = [], set()
    for base in source.get('urls') or [source['url']]:
        for a in _soup(fetcher.get_text(base)).find_all('a', href=True):
            parts = urlsplit(urljoin(base, a['href']))
            title = re.sub(r'\s+', ' ', a.get_text(' ', strip=True))
            identity = canonical_url(urljoin(base, a['href']))
            if not pattern.search(parts.path) or len(title) < 15 or identity in seen:
                continue
            seen.add(identity)
            items.append(GrantOpportunity(
                title=title, source_id=source['id'], source_url=urljoin(base, a['href']),
                organization=source.get('organization'), language=source.get('language')))
            if len(items) >= source.get('max_items', 40):
                return items
    return items


def collect_cards(source, fetcher, today):
    """Liste sayfasında kart başına başlık/özet/kategori/son tarih bulunan kaynaklar (STGM).

    CSS seçicileri config'ten gelir. `date_format` günü.ay.yıl; kart tarihi son başvuru tarihidir
    (STGM'de TAP kartı 25.10.2026, ayrıntı sayfası '25 Ekim 2026'ya kadar' ile doğrulandı)."""
    sel = source['selectors']
    base = source['url']
    items, seen = [], set()
    for card in _soup(fetcher.get_text(base)).select(sel['card']):
        if source.get('require_class') and source['require_class'] not in card.get('class', []):
            continue                                       # kapalı duyuru
        title_node, link_node = card.select_one(sel['title']), card.select_one(sel['link'])
        if not title_node or not link_node or not link_node.get('href'):
            continue
        parts = urlsplit(urljoin(base, link_node['href']))
        url = urljoin(base, link_node['href'])
        if url in seen:
            continue
        seen.add(url)
        deadline, evidence = None, None
        date_node = card.select_one(sel.get('date', '')) if sel.get('date') else None
        if date_node:
            m = re.search(r'(\d{1,2})\.(\d{1,2})\.(\d{4})', date_node.get_text(' ', strip=True))
            if m:
                try:
                    deadline = date(int(m[3]), int(m[2]), int(m[1]))
                    evidence = f'Liste kartı tarihi: {m[0]}'
                except ValueError:
                    pass
        summary = card.select_one(sel['summary']) if sel.get('summary') else None
        category = card.select_one(sel['category']) if sel.get('category') else None
        items.append(GrantOpportunity(
            title=re.sub(r'\s+', ' ', title_node.get_text(' ', strip=True)), source_id=source['id'],
            source_url=url, organization=source.get('organization'), deadline=deadline,
            deadline_evidence=evidence, language=source.get('language'),
            description_short=shorten(summary.get_text(' ', strip=True), 300) if summary else '',
            categories=[category.get_text(' ', strip=True)] if category and category.get_text(strip=True) else []))
        if len(items) >= source.get('max_items', 40):
            break
    return items


CLOSED = re.compile(r"(?:has|have|is|are|now)\s+(?:now\s+)?closed|applications?\s+(?:are\s+|is\s+)?closed|"
                    r"status of the call[^.]{0,50}closed|call for bids[^.]{0,40}closed|basvurular[^.]{0,25}(?:sona erdi|kapandi)|"
                    r"basvuru donemi sona erdi|(?:are|is) not (?:currently )?(?:open|accepting)")
OPEN = re.compile(r"(?:applications?|call for (?:proposals|bids))\s+(?:are\s+|is\s+)?(?:now\s+)?open|"
                  r"status of the call[^.]{0,50}open|basvurular[^.]{0,20}(?:basladi|acildi|devam)")


def collect_pages(source, fetcher, today):
    """Sabit izleme: kullanıcının adıyla istediği tek sayfalık programlar (büyükelçilik fonları vb.).
    Sayfa metninden son tarih ve açık/kapalı ipucu çıkarılır; ipucu sezgiseldir, 'belirsiz' kalabilir."""
    from .textutil import fold
    items = []
    for page in source['pages']:
        soup = _soup(fetcher.get_text(page['url']))
        main = soup.select_one('main') or soup.select_one('article') or soup.body or soup
        text = re.sub(r'\s+', ' ', main.get_text(' ', strip=True))
        folded = fold(text)
        status = 'kapalı' if CLOSED.search(folded) else ('açık' if OPEN.search(folded) else 'belirsiz')
        items.append(GrantOpportunity(
            title=page['title'], source_id=source['id'], source_url=page['url'],
            organization=page.get('organization') or source.get('organization'),
            status_hint=status,
            programme=page.get('programme'), language=page.get('language') or source.get('language'),
            description_short=shorten(f"Sayfa metnine göre durum: {status}. " + (page.get('note') or text[:400]), 300),
            categories=[page['country']] if page.get('country') else []))
        if not page.get('no_deadline'): items[-1].apply_deadline(text, today)
    return items


def collect_crawl(source, fetcher, today):
    """Başlangıç sayfasından aynı host içinde bir seviye in; yolunda `call_pattern` geçen sayfalar çağrıdır."""
    start = source['url']
    host = urlsplit(start).hostname
    follow, call_pattern = source['follow'], source['call_pattern']
    max_pages = source.get('max_pages', 12)

    def links(html, base):
        for a in _soup(html).find_all('a', href=True):
            parts = urlsplit(urljoin(base, a['href']))
            if parts.hostname == host and parts.scheme == 'https' and parts.path.startswith(follow):
                yield urljoin(base, a['href'])

    start_html = fetcher.get_text(start)
    pages = [u for u in dict.fromkeys(links(start_html, start)) if u.rstrip('/') != start.rstrip('/')]
    calls = {u for u in pages if call_pattern in u}
    for page in [u for u in pages if call_pattern not in u][:max_pages]:
        calls.update(u for u in links(fetcher.get_text(page), page) if call_pattern in u)
    items = []
    for url in sorted(calls)[:max_pages]:
        soup = _soup(fetcher.get_text(url))
        text = re.sub(r'\s+', ' ', soup.get_text(' ', strip=True))
        items.append(GrantOpportunity(
            title=_page_title(soup), source_id=source['id'], source_url=url,
            organization=source.get('organization'),
            description_short=shorten(text[:600], 300), language=source.get('language')))
        items[-1].apply_deadline(text, today)
    return items


def enrich(item, fetcher, today, content_selector=None):
    """Ayrıntı sayfasından son tarih, kısa açıklama ve (derleme sitelerinde) resmî sayfa adayı ekler."""
    soup = _soup(fetcher.get_text(item.source_url))
    main = soup.select_one(content_selector) if content_selector else None
    main = main or soup.select_one('article') or soup.select_one('main') or soup.body or soup
    text = re.sub(r'\s+', ' ', main.get_text(' ', strip=True))
    item.apply_deadline(text[:8000], today)
    if len(item.description_short) < 60:
        item.description_short = shorten(text, 300)
    own = urlsplit(item.source_url).hostname
    best = None
    for a in main.find_all('a', href=True):
        parts = urlsplit(urljoin(item.source_url, a['href']))
        if parts.scheme != 'https' or not parts.hostname or parts.hostname == own \
                or any(parts.hostname.endswith(n) for n in NOISE_HOSTS):
            continue
        candidate = f'https://{parts.hostname}{parts.path}' + (f'?{parts.query}' if parts.query else '')
        if HINT.search(a.get_text(' ', strip=True)):
            best = candidate
            item.original_url_evidence = a.get_text(' ', strip=True)
            break
        best = best or candidate
    item.original_url = best
    return item
