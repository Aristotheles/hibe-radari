"""Public, escaped HTML fallback; no network or private user data."""
import calendar
import re
from datetime import date, datetime
from zoneinfo import ZoneInfo
from html import escape
from urllib.parse import urlsplit, parse_qs

MONTHS = ['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran', 'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık']
ROLES = {'dogrudan': 'Doğrudan başvuru', 'ortak': 'Ortaklık', 'ogretmen_birey': 'Öğretmen bireysel', 'uygulama_yeri': 'Uygulama yeri', 'belirsiz': 'Rol belirsiz'}
RESULTS = {'uygun': 'Uygun', 'uygun_degil': 'Uygun değil', 'belirsiz': 'Uygunluk belirsiz'}
CONDITIONS = {'saglandi': 'Koşul sağlandı', 'saglanmadi': 'Koşul sağlanmadı', 'bilinmiyor': 'Koşul bilinmiyor'}

def text(value):
    return escape(str(value if value is not None else ''), quote=True)

def date_label(value):
    try:
        d = date.fromisoformat(value)
        return f'{d.day} {MONTHS[d.month-1]} {d.year}'
    except (ValueError, TypeError):
        return 'Bilinmiyor'

def call_link(call):
    return '/ilan/' + call['id']

def listing(calls):
    content = '<h1 id="page-title">Okulun için bir sonraki fırsat.</h1><p>Başvuru yolunu bul, koşulları ve kanıtı incele.</p><div class="server-list">'
    for call in calls:
        content += f'<article><h2><a href="{text(call_link(call))}">{text(call["title"])}</a></h2><p>{text(call["summary"])}</p><p>{"DEMO · Kurgusal örnek" if call.get("demo") else "Yayımlanmış kayıt"}</p><p>Son başvuru: {text(date_label(call.get("deadline")))}</p>'
        for path in call.get('paths', []):
            content += f'<p>{text(ROLES.get(path["role"], "Rol belirsiz"))} · {text(RESULTS.get(path.get("eligibility"), "Uygunluk belirsiz"))}</p>'
        content += '<p>Son kontrol: Bilinmiyor</p></article>'
    return content + ('<p>Henüz yayımlanmış fırsat yok.</p>' if not calls else '') + '</div>'

def detail(call):
    out = '<a href="/" class="back-link">Tüm ilanlar</a>'
    out += f'<h1 id="page-title">{text(call["title"])}</h1><p>{text(call["summary"])}</p>'
    if call.get('demo'):
        out += '<p class="demo-notice">DEMO · Kurgusal örnek; gerçek başvuruya dayanak değildir.</p>'
    out += f'<p>Son başvuru: {text(date_label(call.get("deadline")))} · Kapanış saati bilinmiyor</p>'
    for path in call.get('paths', []):
        out += f'<section class="how-section"><h2>{text(ROLES.get(path["role"], "Rol belirsiz"))} · {text(RESULTS.get(path.get("eligibility"), "Uygunluk belirsiz"))}</h2>'
        for c in path.get('conditions', []):
            out += f'<div class="condition"><strong>{text(c["text"])}</strong><p>{text(CONDITIONS.get(c.get("result"), "Koşul bilinmiyor"))}</p><p>Kanıt: {text(c.get("evidence") or "Kanıt kaydı eksik.")}</p></div>'
        out += '</section>'
    if not call.get('demo'):
        for url in call.get('urls', []):
            try:
                parsed = urlsplit(url)
                if parsed.scheme == 'https' and parsed.hostname and not parsed.username and not parsed.password:
                    out += f'<p><a class="official-button" href="{text(url)}" rel="noopener noreferrer" target="_blank">Resmî sayfada doğrula</a></p>'
            except ValueError:
                pass
    return out + '<p class="final-warning">Başvurmadan önce resmî metni okuyun.</p>'

def how(sources):
    out = '<h1 id="page-title">Kaynaklar açık. Karar senin.</h1><p>Kaynak metni → insan incelemesi → sürüme bağlı onay. Değişen metin yeniden inceleme gerektirir.</p><p>Kaynak envanteri. Kayıt durumu tarama başarısı değildir. Son tarama: bilinmiyor.</p><div class="server-list">'
    for source in sources:
        out += f'<article><h2>{text(source["name"])}</h2><p>{"Kimlik bekleniyor" if source.get("identity_status") == "missing" else "Doğrulama bekleniyor"}</p><p>Son kontrol: {text(source.get("last_checked") or "Bilinmiyor")}</p></article>'
    return out + '</div>'

def month_view(calls, query, today):
    params = parse_qs(query)
    try:
        year = int(params.get('year', [today.year])[0]); month = int(params.get('month', [today.month])[0])
        if not 1970 <= year <= 2100 or not 1 <= month <= 12:
            raise ValueError
    except (ValueError, TypeError):
        year, month = today.year, today.month
    out = f'<h1 id="page-title">Son başvuru takvimi</h1><h2>{MONTHS[month-1]} {year}</h2><div class="calendar-grid">'
    for label in ['Pzt', 'Sal', 'Çar', 'Per', 'Cum', 'Cmt', 'Paz']:
        out += f'<div class="weekday">{label}</div>'
    for week in calendar.Calendar().monthdayscalendar(year, month):
        for day in week:
            out += '<div class="calendar-cell">'
            if day:
                iso = date(year, month, day).isoformat(); out += f'<span>{day}</span>'
                for c in calls:
                    if c.get('deadline') == iso:
                        out += f'<a class="calendar-event role-direct" href="{text(call_link(c))}">{text(c["title"])}</a>'
            out += '</div>'
    items = [c for c in calls if (c.get('deadline') or '').startswith(f'{year}-{month:02}')]
    out += '</div><div class="server-list">'
    for c in items:
        out += f'<article><a href="{text(call_link(c))}">{text(date_label(c["deadline"]))} · {text(c["title"])}</a></article>'
    return out + ('<p>Bu ay için açıklanmış bir son tarih yok.</p>' if not items else '') + '</div>'

def page(template, path, query, calls, sources, demo, today=None):
    today = today or datetime.now(ZoneInfo('Europe/Istanbul')).date()
    status, title = 200, 'Hibe Radarı | İlanlar'
    description = 'DEMO — Kurgusal örnekler; gerçek başvuruya dayanak değildir.' if demo else 'Başvuru yollarını ve kanıtı inceleyin.'
    if path == '/':
        audience = parse_qs(query).get('audience', ['school'])[0]
        selected = []
        for call in calls:
            paths = [p for p in call.get('paths', []) if (p['role'] == 'ogretmen_birey' if audience == 'me' else p['role'] != 'ogretmen_birey')]
            if paths:
                selected.append(dict(call, paths=paths))
        body = '<p><a href="/?audience=school">Okulum</a> / <a href="/?audience=me">Ben</a></p>' + listing(selected)
    elif path == '/takvim':
        title = 'Son başvuru takvimi | Hibe Radarı'; body = month_view(calls, query, today)
    elif path == '/nasil-calisir':
        title = 'Nasıl çalışır? | Hibe Radarı'; body = how(sources)
    elif path == '/aboneligim':
        title = 'Abonelik tercihlerim | Hibe Radarı'; body = '<h1 id="page-title">Abonelik tercihlerim</h1><p>Tercihler için giriş ve JavaScript gerekir. Giriş abonelik oluşturmaz.</p>'
    elif path == '/yonetim':
        title = 'Yönetim | Hibe Radarı'; body = '<h1 id="page-title">Yönetici oturumu gerekli</h1><p>Giriş olmadan yönetici verileri gösterilmez.</p>'
    elif re.fullmatch(r'/ilan/[a-zA-Z0-9_-]{1,100}', path):
        call = next((c for c in calls if call_link(c) == path), None)
        if call:
            title = call['title'] + ' | Hibe Radarı'; body = detail(call)
            description = ('DEMO · ' if call.get('demo') else '') + 'Son başvuru: ' + date_label(call.get('deadline')) + '. Koşulları ve kanıtı inceleyin.'
        else:
            status = 404; title = 'İlan bulunamadı | Hibe Radarı'; body = '<h1 id="page-title">İlan bulunamadı</h1><a href="/">İlanlara dön</a>'
    else:
        return None
    meta = f'<meta property="og:title" content="{text(title)}"><meta property="og:description" content="{text(description)}">'
    html = re.sub(r'<title>.*?</title>', lambda _: '<title>' + text(title) + '</title>', template, count=1)
    html = html.replace('<!--SERVER_META-->', meta).replace('<!--SERVER_CONTENT-->', body).replace('<!--SERVER_MODE-->', 'Yerel DEMO · Gerçek hizmet bağlantısı ve e-posta gönderimi yok.' if demo else 'Başvurmadan önce resmî metni okuyun.')
    return status, html.encode('utf-8')
