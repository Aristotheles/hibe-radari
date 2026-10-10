"""Bounded discovery on observed source pages; never manufacture a call or deadline."""
import re
from urllib.parse import urljoin,urlsplit
from bs4 import BeautifulSoup
from .models import GrantOpportunity,canonical_url
from .textutil import fold,shorten
from .feeds import collect as collect_feed

CALL=re.compile(r'\b(?:grants?|funding|funds?|calls?|opportunities|awards?|prizes?|competitions?|scholarships?|fellowships?|proposals?|training|workshops?|courses?|applications?|apply|basvur\w*|hib\w*|fon\w*|cagri\w*|burs\w*|yarisma\w*|destek\w*|egitim\w*|seminer\w*)\b')
NAV=re.compile(r'news|announcement|duyuru|haber|opportunit|grant|fund|call|burs|hibe|destek|competition|award|prize|training|course|egitim|apply|application|basvuru')
GENERIC={'','news','haberler','haber','duyurular','duyuru','announcements','opportunities','grants','funding','calls','awards','prizes','competitions','scholarships','training','courses','apply','basvuru','destekler','egitimler'}
GENERIC_TITLES={'funding opportunities','calls for proposals','call for proposals','open calls','current opportunities','news and events','latest news','hibe cagrilari','basvuru cagrilari'}

def observed_links(html,base,hosts):
    soup=BeautifulSoup(html,'html.parser')
    # ASP.NET wraps legitimate public news links in a form; never submit it,
    # but retaining its anchors is necessary to read that source.
    for n in soup.select('script,style'):n.decompose()
    for a in soup.find_all('a',href=True):
        url=urljoin(base,a['href']);parts=urlsplit(url)
        if parts.scheme!='https' or parts.hostname not in hosts or parts.username or parts.password or parts.port not in (None,443):continue
        title=re.sub(r'\s+',' ',a.get_text(' ',strip=True))
        if not title:
            title=next((n.get('alt','') for n in a.select('img[alt]') if n.get('alt')), '')
        yield canonical_url(url),title

def collect(source,fetcher,today):
    hosts=set(source['allowed_hosts']);items={};pages=[]
    fetcher.discovery_errors=[]
    # Dedicated public application pages, observed and verified at acceptance.
    # They are programme metadata, not invented dated calls or private forms.
    for programme in source.get('programme_pages',[]):
        url=programme['url'];response=fetcher.get(url)
        soup=BeautifulSoup(response.content,'html.parser')
        text=soup.get_text(' ',strip=True)
        title=programme['title']
        if fold(title) not in fold(text):raise ValueError('Program adı resmî sayfada doğrulanamadı')
        items[(canonical_url(url),programme.get('application_path'))]=GrantOpportunity(title=title,source_id=source['id'],source_url=url,
            source_entry_id=url,identity_authority=urlsplit(url).hostname,
            application_path=programme.get('application_path'),organization=source.get('organization'),
            categories=['programme_overview'])
    # Feed routes are advertised by the source and verified during acceptance.
    for url in source.get('feed_urls',[]):
        try:
            for item in collect_feed(dict(source,url=url),fetcher,today):
                parts=urlsplit(item.source_url)
                if parts.scheme=='http' and parts.hostname in hosts:
                    item.source_url='https://'+item.source_url[len('http://'):]
                    parts=urlsplit(item.source_url)
                if parts.scheme!='https' or parts.hostname not in hosts or parts.username or parts.password or parts.port not in (None,443):
                    fetcher.discovery_errors.append({'url':url,'error_kind':'unsafe_feed_entry'})
                    continue
                if CALL.search(fold(item.title+' '+item.description_short)):
                    items.setdefault(canonical_url(item.source_url),item)
                    if len(items)>=source.get('max_items',100):return list(items.values())
        except Exception as exc:
            fetcher.discovery_errors.append({'url':url,'error_kind':getattr(exc,'kind','parser')})
    queue=list(dict.fromkeys(source.get('urls') or [source['url']]))
    while queue and len(pages)<source.get('max_pages',4):
        base=queue.pop(0)
        if base in pages:continue
        pages.append(base)
        try:
            response=fetcher.get(base)
            html=response.content
            resolved=str(response.request.url)
        except Exception as exc:
            if len(pages)==1 and not items:raise
            fetcher.discovery_errors.append({'url':base,'error_kind':getattr(exc,'kind','network')})
            continue
        if 'select-language' in urlsplit(resolved).path:
            for a in BeautifulSoup(html,'html.parser').select('a[hreflang="en"][href]'):
                locale=urljoin(resolved,a['href'])
                if urlsplit(locale).hostname in hosts and urlsplit(locale).scheme=='https' and locale not in pages and locale not in queue:
                    queue.insert(0,locale)
        for url,title in observed_links(html,resolved,hosts):
            path=urlsplit(url).path.rstrip('/');leaf=fold(path.rsplit('/',1)[-1])
            nav=bool(NAV.search(fold(title+' '+path)))
            if nav and (leaf in GENERIC or len(title)<15 or fold(title) in GENERIC_TITLES):
                if url not in pages and url not in queue:queue.append(url)
                continue
            if len(title)<15 or len(title)>400 or leaf in GENERIC or not CALL.search(fold(title)):continue
            if url==canonical_url(base) or re.search(r'\.(?:jpg|jpeg|png|svg|gif|zip|mp4)$',path,re.I):continue
            if url not in items:
                items[url]=GrantOpportunity(title=title,source_id=source['id'],source_url=url,
                    organization=source.get('organization'),language=source.get('language'),
                    source_entry_id=url,identity_authority=urlsplit(url).hostname)
            if len(items)>=source.get('max_items',100):return list(items.values())
    return list(items.values())
