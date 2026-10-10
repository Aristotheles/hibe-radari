"""Public, escaped HTML fallback; no network or private user data."""
import calendar
import json
import re
from datetime import date, datetime
from zoneinfo import ZoneInfo
from html import escape
from urllib.parse import urlsplit, parse_qs

MONTHS = ['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran', 'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık']
WEEKDAYS = ['Pazartesi','Salı','Çarşamba','Perşembe','Cuma','Cumartesi','Pazar']
ROLES = {'dogrudan': 'Doğrudan başvuru', 'ortak': 'Ortaklık', 'ogretmen_birey': 'Öğretmen bireysel', 'ogrenci_birey': 'Lise öğrencisi başvurusu', 'uygulama_yeri': 'Uygulama yeri', 'belirsiz': 'Rol belirsiz'}
RESULTS = {'uygun': 'Uygun', 'uygun_degil': 'Uygun değil', 'belirsiz': 'Uygunluk belirsiz'}
CONDITIONS = {'saglandi': 'Koşul sağlandı', 'saglanmadi': 'Koşul sağlanmadı', 'bilinmiyor': 'Koşul bilinmiyor'}
THEMES = {'engelli_kapsayicilik':'Kapsayıcılık','cevre_su':'Çevre ve su','bilim':'Bilim','dil_kultur':'Dil ve kültür','dijital':'Dijital'}

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

def full_date(value):
    try:return date_label(value)+' '+WEEKDAYS[date.fromisoformat(value).weekday()]
    except (ValueError,TypeError):return 'Bilinmiyor'

def listing(calls,today=None):
    today=today or datetime.now(ZoneInfo('Europe/Istanbul')).date()
    training=[c for c in calls if c.get('opportunity_type') in ('training','teacher_training')]
    announcements=[c for c in calls if c not in training]
    groups={}
    for c in announcements:
        try:days=(date.fromisoformat(c['deadline'])-today).days
        except (ValueError,TypeError,KeyError):days=None
        group='Sürekli açık fırsatlar' if (c.get('application_schedule') or {}).get('kind') in ('rolling','self_paced') else 'Tarihi açıklanmadı' if days is None else 'Süresi geçti' if days<0 else 'Acil (14 günden az)' if days<14 else 'Bu ay' if c['deadline'][:7]==today.isoformat()[:7] else 'Daha ileri'
        groups.setdefault(group,[]).append(c)
    content=''
    for group in ('Acil (14 günden az)','Bu ay','Daha ileri','Sürekli açık fırsatlar','Tarihi açıklanmadı','Süresi geçti'):
        items=groups.get(group,[])
        if not items:continue
        content+=f'<section class="opportunity-section"><div class="section-heading"><h2>{text(group)}<span class="group-count">{len(items)}</span></h2><span>Son tarihe göre değerlendirin.</span></div><div class="opportunity-grid">'
        for c in sorted(items,key=lambda c:c.get('deadline') or '9999'):
            path=next(iter(c.get('paths') or []),{})
            kind={'grant':'Hibe','project':'Proje','scholarship':'Burs','competition':'Yarışma / ödül','exchange':'Değişim'}.get(c.get('opportunity_type'),'Proje fırsatı')
            schedule=c.get('application_schedule') or {}
            try:days=(date.fromisoformat(c['deadline'])-today).days
            except (KeyError,ValueError,TypeError):days=None
            label='Sürekli başvuru' if schedule.get('kind')=='rolling' else 'Tarih bekleniyor' if days is None else 'Süresi geçti' if days<0 else 'Son başvuru günü' if days==0 else f'{days} gün kaldı'
            arrow='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><path d="M6 18 18 6M6 6h12v12"/></svg>'
            check='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><path d="m5 12 4 4 10-10"/></svg>'
            reason=c.get('audience_summary') or (', '.join(THEMES.get(t,t) for t in c.get('themes',[]))+' konusuyla ilgili. Başvuru koşullarını ayrıca inceleyin.' if c.get('themes') else 'İlgili başvuru yolunu ve koşulları inceleyin.')
            role_class={'dogrudan':'role-direct','ortak':'role-partner','ogretmen_birey':'role-individual'}.get(path.get('role'),'role-venue')
            content+=f'<a class="opportunity-card" href="{text(call_link(c))}"><div class="card-top"><span class="role-badge {role_class}">{text(ROLES.get(path.get("role"),"Rol belirsiz"))}</span><span class="program-label">{text(kind)}</span></div><div class="card-title-row"><h3>{text(c["title"])}</h3>{arrow}</div><div class="card-deadline"><span class="deadline-normal">{label}</span><time>{text(full_date(c.get("deadline"))) if c.get("deadline") else "Sabit son başvuru tarihi yok" if schedule else "Son tarih bilinmiyor"}</time></div><div class="card-reason">{check}<span>{text(reason)}</span></div><div class="card-bottom"><span>Kişisel ve proje koşullarını kontrol edin</span><span>Son kontrol: {text(full_date(str(c.get("last_checked") or "")[:10]))}</span></div></a>'
        content+='</div></section>'
    if training:
        content+=f'<details class="training-section"><summary>Öğretmen eğitimleri · {len(training)}</summary><p class="muted">Çevrimiçi kurslar ve mesleki gelişim fırsatları. Başvuru koşulları her eğitimde ayrıdır.</p><div class="training-list">'
        for c in training:content+=f'<a class="training-row" href="{text(call_link(c))}"><div><h3>{text(c["title"])}</h3><p>{"Kendi hızında eğitim" if (c.get("application_schedule") or {}).get("kind")=="self_paced" else text(date_label(c.get("deadline")))}</p></div></a>'
        content+='</div></details>'
    return content or '<p>Henüz yayımlanmış fırsat yok.</p>'

def detail(call):
    out = '<a href="/" class="back-link">Tüm ilanlar</a>'
    out += f'<h1 id="page-title">{text(call["title"])}</h1><p>{text(call["summary"])}</p>'
    if call.get('demo'):
        out += '<p class="demo-notice">DEMO · Kurgusal örnek; gerçek başvuruya dayanak değildir.</p>'
    if call.get('publication_status')=='verification_pending':
        out += '<p class="verification">Doğrulama bekleyen fırsat: '+text(call.get('verification_reason'))+'. Başvuru uygunluğu henüz doğrulanmadı.</p>'
    out += f'<p>Son başvuru: {text(date_label(call.get("deadline")))} · Kapanış saati bilinmiyor</p>'
    out += f'<p>Kaynak: {text(call.get("organization") or call.get("source_id") or "Bilgi kaydı yok")}</p><p>Son kontrol: {text(date_label(str(call.get("last_checked") or "")[:10]))}</p>'
    if call.get('deadline_evidence'):
        out += f'<p>Son tarih kanıtı: {text(call["deadline_evidence"])}</p>'
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
        audience = parse_qs(query).get('audience', ['all'])[0]
        selected = []
        for call in calls:
            tag={'me':'teacher','student':'student','school':'school'}.get(audience)
            paths = [p for p in call.get('paths', []) if (audience == 'all' or tag in call.get('audience_tags',[]) or (p['role'] == 'ogretmen_birey' if audience == 'me' else p['role'] == 'ogrenci_birey' if audience == 'student' else p['role'] not in ('ogretmen_birey','ogrenci_birey')))]
            if paths:
                selected.append(dict(call, paths=paths))
        body = listing(selected,today)
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
    if path=='/' and '<div id="app-shell" hidden>' in html:
        heading={'all':'Türkiye için proje ve eğitim fırsatları.','school':'Okulun için bir sonraki fırsat.','student':'Lise öğrencileri için fırsatlar.','me':'Öğretmenler için fırsatlar.'}.get(audience,'Türkiye için proje ve eğitim fırsatları.')
        html=html.replace('Okulun için bir sonraki fırsat.',heading,1)
        html=html.replace('<div id="app-shell" hidden>','<div id="app-shell">',1)
        html=html.replace('<div id="server-content">'+body+'</div>','<div id="server-content" hidden></div>',1)
        html=html.replace('<div id="cards" aria-busy="true"></div>','<div id="cards" aria-busy="false">'+body+'</div>',1)
        courses=sum(c.get('opportunity_type') in ('training','teacher_training') for c in selected)
        html=html.replace('Fırsatlar yükleniyor…',f'{len(selected)-courses} duyuru · {courses} eğitim')
        bootstrap=json.dumps(calls,ensure_ascii=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
        html=html.replace('</body>','<script id="public-data" type="application/json">'+bootstrap+'</script></body>')
    return status, html.encode('utf-8')
