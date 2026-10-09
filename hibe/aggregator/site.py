"""Toplayıcı raporundan statik site üretir (Firebase Hosting).

Görünüm: Lovable "HibeRadarı" prototipinin birebir işaretlemesi ve CSS'i (web/style.css = src/styles.css portu,
ikonlar lucide-static). Veri: gerçek toplanan duyurular. Lovable'daki kurgusal alanlar (başvuru rolü, destek tutarı,
eş finansman, "Uygun/Uygun değil" koşulları) gerçek veride bilinmediği için UYDURULMAZ; yerine süzgeç durumu,
son tarih kanıtı ve karar gerekçeleri gösterilir.

Kaynaktan gelen tüm metin güvenilmezdir: html.escape ile kaçışlanır, bağlantılar yalnız https ise verilir.
Betikler ve stil dış dosyadır (CSP: script-src 'self'; style-src 'self')."""
import html
import json
import re
from datetime import date, datetime, timedelta
from pathlib import Path
from urllib.parse import quote, urlsplit

from .icons import ICONS
from .textutil import fold

ROOT = Path(__file__).resolve().parents[2]
BASE = 'https://hibe-radari-tr.web.app'
MONTHS = ['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran', 'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık']
# rapor grubu → (rozet sınıfı, kısa etiket, süzgeç anahtarı, ikon)
KIND = {
    'accepted': ('role-direct', 'Uygun görünüyor', 'ok', 'check-check'),
    'review': ('role-partner', 'Kontrol et', 'check', 'circle-help'),
    'watch': ('role-venue', 'İzleme', 'watch', 'clock-3'),
    'general': ('role-individual', 'Genel hibe', 'general', 'info'),
}
KIND_BY_KEY = {v[2]: (k, v) for k, v in KIND.items()}
GROUPS = [
    ('Acil (14 gün)', 'Son tarih yaklaşırken, ilk buraya bak.'),
    ('Bu ay', 'Bu ay değerlendirebileceğin fırsatlar.'),
    ('Daha ileri', 'Plan yapmak için biraz daha zamanın var.'),
    ('Tarihi açıklanmadı', 'Son tarih bulunamadı; resmî sayfaya bak.'),
    ('İzleme listesi', 'Geçmiş veya kapanmış dönem: program yinelenirse yeni dönemi bekle.'),
    ('Genel hibe fırsatları', 'Okul eşleşmesi belirsiz açık çağrılar; okul aile birliği ya da dernek kanalıyla uygun olabilir.'),
]
TOPICS = [
    ('Bilim ve teknoloji', ['bilim', 'tubitak', 'stem', 'fen ', 'teknoloji', 'science', 'digital', 'dijital', 'matematik', 'research']),
    ('Çevre', ['cevre', 'iklim', 'doga', 'climate', 'environment', 'sifir atik', 'ekolo']),
    ('Kültür ve sanat', ['kultur', 'sanat', 'culture', 'festival', 'muzik', 'tiyatro']),
    ('Gençlik', ['genclik', 'youth', 'jugend', 'genc ', 'gencler']),
    ('Eğitim', ['egitim', 'okul', 'ogretmen', 'school', 'teacher', 'erasmus', 'etwinning', 'ogrenci', 'schule', 'bildung']),
]
PROGRAMS = [
    ('Erasmus+', ['erasmus']), ('eTwinning', ['etwinning']), ('TÜBİTAK', ['tubitak']),
    ('Gençlik Köprüsü', ['jugendbruecke', 'jugendbrucke', 'deutsch-turk']),
    ('Büyükelçilik fonları', ['buyukelcilik', 'embassy', 'dap', 'cfli', 'yerel girisimler']),
    ('Avrupa Birliği', ['avrupa komisyonu', 'horizon', 'funding & tenders', 'interreg']),
]
WEEKDAYS = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar']


def esc(value):
    return html.escape(str(value if value is not None else ''), quote=True)


def icon(name, size=None, cls='', stroke=None):
    attrs = f' width="{size}" height="{size}"' if size else ''
    klass = f' class="{cls}"' if cls else ''
    sw = stroke or 2
    return (f'<svg{klass}{attrs} xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>')


def safe_link(url):
    parts = urlsplit(url or '')
    return url if parts.scheme == 'https' and parts.hostname else None


def parse_date(value):
    try:
        return date.fromisoformat(value) if value else None
    except ValueError:
        return None


def long_date(d):
    return f'{d.day} {MONTHS[d.month - 1]} {d.year}'


def topic_of(o):
    text = fold(' '.join([o['title'], o.get('description_short') or '', ' '.join(o.get('categories') or [])]))
    for name, words in TOPICS:
        if any(w in text for w in words):
            return name
    return 'Diğer'


def program_of(o):
    text = fold(' '.join([o['title'], o.get('programme') or '', o.get('organization') or '', o.get('source_id') or '']))
    for name, words in PROGRAMS:
        if any(w in text for w in words):
            return name
    return 'Diğer'


def tab_of(o):
    a = set(o['relevance'].get('audience') or o.get('audience') or [])
    return 'me' if 'teacher' in a and 'school' not in a else 'school'


def group_of(o, key, today):
    if key == 'watch':
        return 'İzleme listesi'
    if key == 'general':
        return 'Genel hibe fırsatları'
    d = parse_date(o.get('deadline'))
    if not d:
        return 'Tarihi açıklanmadı'
    if (d - today).days <= 14:
        return 'Acil (14 gün)'
    return 'Bu ay' if (d.year, d.month) == (today.year, today.month) else 'Daha ileri'


def prepare(report, today):
    """Rapordaki yayınlanan gruplardan sıralı, zenginleştirilmiş öğe listesi."""
    items = []
    for key in ('accepted', 'review', 'watch', 'general'):
        for o in report.get(key, []):
            o = dict(o)
            o['key'] = key
            o['kind'] = KIND[key][2]
            o['topic'] = topic_of(o)
            o['program'] = program_of(o)
            o['tab'] = tab_of(o)
            o['group'] = group_of(o, key, today)
            items.append(o)
    far = '9999-12-31'
    items.sort(key=lambda o: (o.get('deadline') or far, o['title']))
    return items


def badge(o, size=14):
    cls, label, _, ic = KIND[o['key']]
    return f'<span class="role-badge {cls}">{icon(ic, size)}{esc(label)}</span>'


def when_html(o, today):
    d = parse_date(o.get('deadline'))
    if not d:
        return f'<span class="deadline-normal">{icon("circle-help", 14)}Tarih bekleniyor</span>'
    left = (d - today).days
    count = f'{left} gün kaldı' if left >= 0 else 'Süresi geçti'
    cls = 'deadline-urgent' if 0 <= left < 14 else 'deadline-normal'
    return (f'<span class="{cls}"><span class="deadline-dot"></span>{esc(count)}</span>'
            f'<time datetime="{d.isoformat()}" aria-label="{esc(long_date(d))}">{d.day} {MONTHS[d.month - 1]} {d.year}</time>')


def card(o, today):
    first = next((r for r in o['relevance']['reasons'] if r.startswith('+')), None)
    reason = o.get('description_short') or first or ''
    text = ' '.join([o['title'], o.get('organization') or '', reason, o['topic'], o['program']])
    return (f'<a class="opportunity-card" href="/ilan/{o["id"]}" data-tab="{o["tab"]}" data-kind="{o["kind"]}" '
            f'data-topic="{esc(o["topic"])}" data-program="{esc(o["program"])}" data-text="{esc(text.lower())}">'
            f'<div class="card-top">{badge(o)}<span class="program-label">{esc(o["program"])}</span></div>'
            f'<div class="card-title-row"><h3>{esc(o["title"])}</h3>{icon("arrow-up-right", 20, "card-arrow")}</div>'
            f'<p class="organization">{esc(o.get("organization"))}</p>'
            f'<div class="card-deadline">{when_html(o, today)}</div>'
            f'<div class="card-reason">{icon("check", 16)}<span>{esc(reason)}</span></div>'
            f'<div class="card-bottom"><span>{esc(o["topic"])}</span><span>{icon("check-check", 14)}Kaynak: {esc(o["source_id"])}</span></div></a>')


def header(active, report):
    def link(href, label, name):
        return f'<a href="{href}"{" class=active aria-current=page" if name == active else ""}>{label}</a>'
    gen = parse_date(report['generated_at'][:10])
    stamp = f'{gen.day} {MONTHS[gen.month - 1]}' if gen else ''
    return ('<a class="skip-link" href="#page-title">İçeriğe geç</a>'
            '<header class="site-header"><div class="header-inner">'
            f'<a class="brand" href="/" aria-label="HibeRadarı ana sayfa"><span class="brand-symbol">{icon("radar", None, "", 1.7)}</span>'
            '<span>hibe<span class="text-primary">radarı</span><span class="brand-subtitle">ÖĞRETMENLER İÇİN</span></span></a>'
            f'<nav aria-label="Ana gezinme">{link("/", "İlanlar", "list")}{link("/takvim", "Takvim", "calendar")}{link("/nasil-calisir", "Nasıl çalışır?", "how")}</nav>'
            f'<div class="header-actions"><span class="live-label"><span></span>{esc(stamp)}\'de güncellendi</span>'
            f'<button id="theme-toggle" class="theme-toggle" type="button" title="Karanlık görünüm" aria-label="Karanlık görünüm">'
            f'<span class="icon-moon">{icon("moon", 20)}</span><span class="icon-sun">{icon("sun", 20)}</span></button></div>'
            '</div></header>')


def footer(report):
    gen = esc(report['generated_at'][:10])
    return (f'<footer class="site-footer"><span>{icon("radar", 16)} Doğru fırsat, doğru zamanda.</span>'
            f'<span>Otomatik toplanan duyurular · {gen}<span class="footer-separator"> / </span>Hesap, form ve takip çerezi yok.</span></footer>')


def page(title, description, body, active, report, path='/', extra_head=''):
    v = ''.join(ch for ch in report['generated_at'] if ch.isdigit())
    return f'''<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} · HibeRadarı</title>
<meta name="description" content="{esc(description)}">
<meta property="og:title" content="{esc(title)} · HibeRadarı">
<meta property="og:description" content="{esc(description)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{esc(BASE + path)}">
<link rel="canonical" href="{esc(BASE + path)}">
<link rel="stylesheet" href="/style.css?v={v}">
<script src="/theme.js?v={v}"></script>
{extra_head}</head>
<body>
{header(active, report)}
<div class="environment">Beta · duyurular otomatik toplanır, insan onayından geçmemiştir. Son tarih ve uygunluğu resmî sayfadan doğrulayın.</div>
{body}
{footer(report)}
<script src="/app.js?v={v}" defer></script>
</body>
</html>
'''


def toggle(tab_attr):
    return (f'<div class="audience-toggle" aria-label="Başvuru yolu"><button type="button" class="selected" aria-pressed="true" {tab_attr}="school">{icon("building-2", 16)}Okulum</button>'
            f'<button type="button" aria-pressed="false" {tab_attr}="me">{icon("user-round", 16)}Ben</button></div>')


def select_field(sel_id, label, first, options, lead_icon=''):
    opts = ''.join(f'<option value="{esc(v)}">{esc(t)}</option>' for v, t in options)
    cls = 'select-field role-select' if lead_icon else 'select-field'
    return (f'<div class="{cls}">{lead_icon}<select id="{sel_id}" aria-label="{esc(label)}"><option value="">{esc(first)}</option>{opts}</select>'
            f'{icon("chevron-down", 16)}</div>')


def index_body(items, report, today):
    by_group = {}
    for o in items:
        by_group.setdefault(o['group'], []).append(o)
    sections = ''
    for idx, (name, note) in enumerate(GROUPS):
        rows = by_group.get(name, [])
        if not rows:
            continue
        sections += (f'<section class="opportunity-section" data-group="{esc(name)}"><div class="section-heading"><h2>'
                     f'{"<span class=urgent-indicator></span>" if idx == 0 else ""}{esc(name)} <span class="group-count">{len(rows)}</span></h2>'
                     f'<span>{esc(note)}</span></div><div class="opportunity-grid">{"".join(card(o, today) for o in rows)}</div></section>')
    topics = sorted({o['topic'] for o in items})
    programs = sorted({o['program'] for o in items})
    filt = (f'<div class="filter-bar"><label class="search-field">{icon("search", 20)}<input id="search" type="search" aria-label="İlan ara" '
            f'placeholder="İlan, kurum veya anahtar kelime ara…" autocomplete="off"></label>'
            + select_field('f-topic', 'Konu', 'Tüm konular', [(t, t) for t in topics])
            + select_field('f-program', 'Program', 'Tüm programlar', [(p, p) for p in programs])
            + select_field('f-kind', 'Durum', 'Tüm durumlar', [(k[2], k[1]) for k in KIND.values()], icon('list-filter', 16)) + '</div>')
    legend = ''.join(f'<span class="{c}">{icon(ic, 14)}{esc(l)}</span>' for c, l, _, ic in KIND.values())
    return ('<main class="page-container listing-page">'
            f'<div class="page-eyebrow"><span class="tiny-line"></span> FIRSATLARI KEŞFET</div>'
            f'<div class="page-heading"><div><h1 id="page-title" tabindex="-1" data-school="Okulun için bir sonraki fırsat." data-me="Senin için bir sonraki fırsat.">Okulun için bir sonraki fırsat.</h1>'
            f'<p id="lead" data-school="Hibeler, projeler ve iş birlikleri. Okuluna uyanı bul, zamanında harekete geç." data-me="Eğitimler, mesleki gelişim ve öğretmen fırsatları. Sana uyanı bul, zamanında harekete geç.">'
            f'Hibeler, projeler ve iş birlikleri. Okuluna uyanı bul, zamanında harekete geç.</p></div>{toggle("data-tab-btn")}</div>'
            f'{filt}'
            f'<div class="results-meta"><span aria-live="polite" aria-atomic="true"><strong id="count">{len(items)} fırsat</strong> <span id="count-for">okulun için listeleniyor</span>'
            f'<button id="clear-filters" class="quiet-link" type="button" hidden>Filtreleri temizle {icon("x", 14)}</button></span>'
            f'<span>{icon("arrow-down", 14)}Son tarihe göre</span></div>'
            f'<div id="cards">{sections}</div>'
            f'<div id="empty" class="empty-state" hidden>{icon("radar", 64, "", 1)}<h2>Bu filtrelere uyan fırsat yok.</h2><p>Başka bir anahtar kelime veya durum dene.</p></div>'
            f'<div class="trust-strip"><div>{icon("check-check", 20)}<span>Her fırsatın arkasında bir kaynak var.<small>Kaynak bağlantısı açık, gerekçe görünür. Son karar senin.</small></span></div>'
            f'<div class="role-legend">{legend}</div></div></main>')


def reason_rows(o):
    rows = ''
    for r in o['relevance']['reasons']:
        if r.startswith('+'):
            ic, cls, state = 'check', 'condition-yes', 'Artı'
        elif r.startswith('-'):
            ic, cls, state = 'x', 'condition-no', 'Eksi'
        else:
            ic, cls, state = 'circle-help', 'condition-maybe', 'Not'
        rows += (f'<div class="condition-row"><span class="condition-icon {cls}">{icon(ic, 18)}</span>'
                 f'<div><strong>{esc(re.sub(r"^[+-]\d+\s*", "", r))}</strong></div><span class="condition-state">{state}</span></div>')
    return rows


def ics(o, stamp):
    d = parse_date(o['deadline'])
    end = d + timedelta(days=1)
    esc_ics = lambda s: s.replace('\\', '\\\\').replace('\n', '\\n').replace(',', '\\,').replace(';', '\\;')
    url = safe_link(o.get('original_url')) or safe_link(o.get('source_url')) or ''
    lines = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//HibeRadari//TR', 'BEGIN:VEVENT', f'UID:{o["id"]}@hibe-radari-tr.web.app',
             f'DTSTAMP:{stamp}', f'DTSTART;VALUE=DATE:{d:%Y%m%d}', f'DTEND;VALUE=DATE:{end:%Y%m%d}',
             f'SUMMARY:{esc_ics(o["title"] + " — Son başvuru")}',
             f'DESCRIPTION:{esc_ics("Otomatik toplanan duyuru; saati ve uygunluğu resmî metinden doğrulayın. " + url)}',
             'BEGIN:VALARM', 'TRIGGER:-P1D', 'ACTION:DISPLAY', 'DESCRIPTION:Son başvuru yarın', 'END:VALARM', 'END:VEVENT', 'END:VCALENDAR']
    return '\r\n'.join(lines) + '\r\n'


BANNER = {
    'ok': ('Bu fırsat okulun için uygun mu?', 'Uygun görünüyor — resmî metinde doğrulayın.'),
    'check': ('Bu fırsat okulun için uygun mu?', 'Henüz belli değil — koşulları elle kontrol edin.'),
    'watch': ('Şu an açık mı?', 'Geçmiş veya kapanmış dönem — yeni dönemi izleyin.'),
    'general': ('Bu fırsat okulun için uygun mu?', 'Okul eşleşmesi belirsiz — uygunluğa bakın.'),
}


def detail_page(o, report, today, stamp):
    d = parse_date(o.get('deadline'))
    left = (d - today).days if d else None
    q, a = BANNER[o['kind']]
    official = safe_link(o.get('original_url')) or safe_link(o.get('source_url'))
    src = safe_link(o.get('source_url'))
    page_url = f'{BASE}/ilan/{o["id"]}'
    share_text = f'{o["title"]}\n{"Tarih bekleniyor" if left is None else str(left) + " gün kaldı"} · {page_url}'
    can_ics = bool(d and left is not None and left >= 0)
    evidence = o.get('deadline_evidence')
    first = next((r for r in o['relevance']['reasons'] if r.startswith('+')), None)
    desc = o.get('description_short') or ''
    side_links = ''
    if can_ics:
        side_links += f'<a class="outline-button" href="/ics/{o["id"]}.ics" download>{icon("calendar-plus", 16)}Takvime ekle (.ics)</a>'
    else:
        side_links += f'<span class="outline-button disabled" aria-disabled="true">{icon("calendar-plus", 16)}Takvime ekle (.ics)</span>'
    side_links += (f'<a class="outline-button" href="https://wa.me/?text={quote(share_text)}" target="_blank" rel="noopener noreferrer">'
                   f'{icon("message-circle", 16)}WhatsApp’ta paylaş</a>')
    body = (
        '<main class="page-container detail-page">'
        f'<a class="back-link" href="/">{icon("arrow-left", 16)}Tüm ilanlar</a>'
        f'<div class="eligibility-banner"><span class="eligibility-check">{icon("check", 20)}</span><div><span>{esc(q)}</span><strong>{esc(a)}</strong></div>{badge(o)}</div>'
        '<div class="detail-layout"><article>'
        f'<div class="detail-heading"><span class="page-eyebrow">{esc(o["program"])} / {esc(o["topic"])}</span><h1 id="page-title" tabindex="-1">{esc(o["title"])}</h1>'
        f'<p>{esc(o.get("organization"))}</p><span class="verification">{icon("check-check", 16)}Güncelleme: {esc(report["generated_at"][:10])}</span></div>'
        '<div class="facts-grid">'
        f'<div>{icon("clock-3", 16)}<span>Son başvuru</span><strong>{esc(long_date(d)) if d else "Tarihi açıklanmadı"}</strong><small>{"Saat yok · resmî metinden doğrula" if d else "Resmî sayfaya bakın"}</small></div>'
        f'<div>{icon("info", 16)}<span>Kurum</span><strong>{esc(o.get("organization"))}</strong><small>Kaynak: {esc(o["source_id"])}</small></div>'
        f'<div>{icon("wallet", 16)}<span>Program</span><strong>{esc(o["program"])}</strong><small>Konu: {esc(o["topic"])}</small></div>'
        f'<div>{icon("users", 16)}<span>Dil</span><strong>{esc((o.get("language") or "—").upper())}</strong><small>Orijinal duyuru dili</small></div></div>'
        '<section class="detail-section"><h2>Bu fırsat neden listelendi?</h2>'
        + (f'<p class="reason-highlight">{icon("check", 20)}{esc(re.sub(r"^[+-]\d+\s*", "", first))}</p>' if first else '')
        + f'<p>{esc(desc)}</p>'
        + (f'<p class="muted">Tarih kanıtı: {esc(evidence)}</p>' if evidence else '') + '</section>'
        '<section class="detail-section"><div class="section-heading"><h2>Süzgeç gerekçeleri</h2><span>Her puan değişimi açıklanır.</span></div>'
        f'{reason_rows(o)}</section>'
        f'<div class="source-note">{icon("info", 16)}<span>Yönetici tarafından içerik sürümü onaylanmıştır. Tarihleri, tutarları ve koşulları resmî sayfadan doğrulayın.</span></div>'
        '</article><aside class="decision-sidebar"><div class="decision-box">'
        f'<span class="page-eyebrow">BİR SONRAKİ ADIM</span><h2>{"Planını hazırlamaya başla." if left is None else (f"{left} günün var." if left >= 0 else "Bu dönemin süresi geçti.")}</h2>'
        '<p>Şimdi güncel bilgiyi asıl kaynağından doğrula.</p>'
        + (f'<a class="official-button" href="{esc(official)}" target="_blank" rel="noopener noreferrer nofollow">Resmî sayfada doğrula{icon("arrow-up-right", 16)}</a>'
           f'<span class="external-note">{icon("external-link", 12)}Yeni sekmede açılır</span>' if official else '')
        + (f'<p class="muted">Bulunduğu sayfa: <a href="{esc(src)}" target="_blank" rel="noopener noreferrer nofollow">kaynak duyuru</a></p>' if src and src != official else '')
        + f'<div class="secondary-actions">{side_links}</div><p class="privacy-note">Üyelik yok. Kişisel veri yok.</p></div>'
        f'<div class="sidebar-tip">{icon("circle-help", 20)}<p>Bir noktadan emin değil misin?<br><a href="/nasil-calisir">Duyuruları nasıl değerlendirdiğimizi gör {icon("arrow-up-right", 14)}</a></p></div>'
        '</aside></div><p class="final-warning">Başvurmadan önce resmî metni okuyun.</p></main>')
    return page(o['title'], f'{"Tarih bekleniyor" if left is None else str(left) + " gün kaldı"}. {desc}'[:300], body, 'list', report, f'/ilan/{o["id"]}'), \
        (ics(o, stamp) if can_ics else None)


def calendar_body(items, today):
    data = [{'id': o['id'], 'title': o['title'], 'org': o.get('organization') or '', 'deadline': o['deadline'], 'tab': o['tab'],
             'kind': o['kind'], 'label': KIND[o['key']][1], 'cls': KIND[o['key']][0]} for o in items if o.get('deadline') and o['key'] != 'watch']
    fallback = ''
    upcoming = [o for o in items if o.get('deadline') and o['key'] != 'watch' and parse_date(o['deadline']) >= today]
    for o in upcoming:
        d = parse_date(o['deadline'])
        fallback += (f'<a class="agenda-row" href="/ilan/{o["id"]}"><time datetime="{d.isoformat()}"><strong>{d.day}</strong>{MONTHS[d.month - 1][:3]}</time>'
                     f'<div><h3>{esc(o["title"])}</h3><p>{esc(o.get("organization"))}</p></div>{badge(o)}</a>')
    blob = json.dumps({'today': today.isoformat(), 'items': data}, ensure_ascii=False).replace('<', '\\u003c')
    wd = ''.join(f'<div class="weekday"><span>{d}</span><abbr title="{d}">{d[:3]}</abbr></div>' for d in WEEKDAYS)
    return ('<main class="page-container calendar-page">'
            '<div class="page-eyebrow"><span class="tiny-line"></span> SON TARİHLER</div>'
            f'<div class="page-heading"><div><h1 id="page-title" tabindex="-1">Hiçbir fırsat son güne kalmasın.</h1><p>Başvuru tarihlerini bir arada gör, bir sonraki adımını planla.</p></div>{toggle("data-cal-tab")}</div>'
            f'<div class="calendar-toolbar"><h2>{icon("calendar-days", 20)}<span id="cal-title"></span></h2><div>'
            f'<button type="button" id="cal-today" class="outline-button">Bugün</button>'
            f'<button type="button" id="cal-prev" class="icon-button" aria-label="Önceki ay">{icon("chevron-left", 18)}</button>'
            f'<button type="button" id="cal-next" class="icon-button" aria-label="Sonraki ay">{icon("chevron-right", 18)}</button></div></div>'
            f'<div class="calendar-grid" id="cal-grid">{wd}</div>'
            f'<section class="calendar-agenda"><div class="section-heading"><h2>Bu ayın son tarihleri <span class="group-count" id="cal-count">0</span></h2><span>Yaklaşan tüm tarihler aşağıdadır.</span></div>'
            f'<div id="cal-agenda"></div><p class="calendar-empty" id="cal-empty" hidden>Bu ay için açıklanmış bir son tarih yok.</p></section>'
            f'<noscript><section class="calendar-agenda"><div class="section-heading"><h2>Yaklaşan son tarihler</h2></div>{fallback}</section></noscript>'
            f'<script type="application/json" id="cal-data">{blob}</script></main>')


def how_body(report):
    c = report['counts']
    steps = [
        ('file-search', '01 / KAYNAK', 'Resmî kaynağa bakarız.', 'Resmî API, RSS ve herkese açık sayfalardan yalnız başlık, kurum, son tarih ve bağlantı alınır. Her kayıt kaynağına bağlanır.'),
        ('user-check', '02 / SÜZGEÇ', 'Alakasızı ayırırız.', 'Okul, öğretmen ve program eşleşmesi puanlanır; iş ilanı, burs, sanat gibi alakasızlar ayrılır. Her kararın gerekçesi ilan sayfasında görünür.'),
        ('check-check', '03 / KARAR', 'Kararı sen verirsin.', 'Belirsizlik saklanmaz. Güncel resmî metni okuyarak başvuru kararını sen verirsin; insan onayı henüz uygulanmıyor.'),
    ]
    proc = ''.join(f'<div><span class="process-icon">{icon(i, 20)}</span><span class="step-number">{n}</span><h3>{esc(t)}</h3><p>{esc(p)}</p></div>' for i, n, t, p in steps)
    rows = ''
    for s in report['sources']:
        status = f'Hata: {esc(s["error"])}' if s['error'] else f'{s["fetched"]} duyuru okundu'
        rows += (f'<div class="source-row"><div><strong>{esc(s.get("organization") or s["id"])}</strong><span>{esc(s["id"])} · {status}</span></div>'
                 f'{icon("check" if not s["error"] else "x", 18)}</div>')
    explain = {'role-direct': 'Okul/öğretmen ya da listelenen programla güçlü eşleşme. Yine de resmî sayfada doğrulayın.',
               'role-partner': 'Olası eşleşme ya da sabit izlenen program; uygunluğa elle bakın.',
               'role-venue': 'Geçmiş veya kapanmış dönem; program yinelenirse yeni dönemi bekleyin, proje fikri olarak da işe yarar.',
               'role-individual': 'Açık ama okul eşleşmesi belirsiz; okul aile birliği veya dernek kanalıyla uygun olabilir.'}
    roles = ''.join(f'<div class="role-explanation"><span class="role-explanation-icon {cls}">{icon(ic, 20)}</span><div><strong>{esc(label)}</strong><p>{esc(explain[cls])}</p></div></div>'
                    for cls, label, _, ic in KIND.values())
    return ('<main class="page-container how-page">'
            '<div class="page-eyebrow"><span class="tiny-line"></span> ŞEFFAFLIK & GÜVEN</div>'
            f'<div class="page-heading"><div><h1 id="page-title" tabindex="-1">Kaynaklar açık. Karar senin.</h1><p>HibeRadarı bir başvuru kaynağı değil, doğru kaynağa giden kısa yol.</p></div>{icon("radar", None, "how-radar", 1)}</div>'
            f'<div class="demo-notice">{icon("shield-check", 20)}<div><strong>Beta sürüm: duyurular otomatik toplanıyor.</strong><p>İçerik insan onayından geçmemiştir. Tarihleri, tutarları ve koşulları her zaman resmî sayfadan doğrulayın.</p></div></div>'
            f'<section class="how-section"><h2>Bir ilan, listeye nasıl gelir?</h2><div class="process-grid">{proc}</div></section>'
            f'<div class="how-columns"><section class="how-section"><h2>İzlenen kaynaklar</h2><p class="section-intro">Şu an {len(report["sources"])} kaynak taranıyor.</p>{rows}</section>'
            f'<section class="how-section"><h2>Renk değil, durum.</h2><p class="section-intro">Süzgecin her kayda verdiği karar:</p>{roles}'
            f'<p class="section-intro">Şu an: {c["accept"]} uygun, {c["review"]} kontrol, {c["watch"]} izleme, {c["general"]} genel.</p></section></div>'
            f'<section class="freshness-band">{icon("radar", 32, "", 1.5)}<div><h2>Son güncelleme bilgisi, her ilanda.</h2><p>Son toplama: {esc(report["generated_at"].replace("T", " "))}. Otomatik günlük güncelleme henüz kurulu değil.</p></div>'
            f'<a href="/">Fırsatlara dön {icon("arrow-up-right", 16)}</a></section>'
            '<p class="final-warning">Hesap, form veya takip çerezi yok. Başvurmadan önce resmî metni okuyun.</p></main>')


EXTRA_CSS = """
/* Statik site eklentileri (Lovable portuna ek) */
[hidden]{display:none!important}
.text-primary{color:var(--primary)}
.tiny-line{display:inline-block;width:18px;height:2px;background:var(--primary)}
.live-label{display:flex;align-items:center;gap:7px;font-size:11px;color:var(--muted-foreground)}
.live-label>span{width:6px;height:6px;border-radius:50%;background:var(--primary)}
.theme-toggle{background:transparent;color:var(--foreground);border:0;width:44px;height:44px;display:inline-grid;place-items:center;cursor:pointer;border-radius:6px}
.theme-toggle .icon-sun{display:none}.dark .theme-toggle .icon-sun{display:inline-flex}.dark .theme-toggle .icon-moon{display:none}
.opportunity-card{text-decoration:none;color:inherit}
.quiet-link{background:transparent;border:0;color:var(--primary);cursor:pointer;font-size:12px;margin-left:10px;min-height:32px;display:inline-flex;align-items:center;gap:4px}
.search-field>svg,.select-field>svg{flex-shrink:0}
.outline-button,.icon-button{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:44px;padding:0 14px;border:1px solid var(--border);border-radius:6px;background:var(--card);color:var(--foreground);font-size:12px;text-decoration:none;cursor:pointer}
.icon-button{padding:0;min-width:44px;background:transparent;border-color:transparent}
.outline-button.disabled{opacity:.5;cursor:not-allowed}
.secondary-actions .outline-button{height:44px}
.official-button{display:flex;align-items:center;justify-content:center;gap:8px;text-decoration:none;background:var(--primary);color:var(--primary-foreground);border-radius:6px;font-weight:600}
.muted{color:var(--muted-foreground);font-size:12px}
.audience-toggle svg{margin-right:6px;vertical-align:-3px}
.today-day{background:var(--primary);color:var(--primary-foreground);border-radius:50%}
.calendar-event{text-decoration:none}
.process-grid{list-style:none}
.audience-toggle button{display:inline-flex;align-items:center;justify-content:center;gap:6px;padding:0 20px;border:0;border-radius:5px;background:transparent;cursor:pointer;font-size:14px}
.audience-toggle button.selected{background:var(--card)}
.environment{padding:8px 24px;background:var(--success-surface);color:var(--success);text-align:center;font-size:12px}
.skip-link{position:absolute;left:16px;top:-100px;padding:12px;z-index:10;background:var(--card);color:var(--foreground)}.skip-link:focus{top:12px}
.quiet-link svg{vertical-align:-2px}
"""

THEME_JS = """(function(){var d=false;try{var s=localStorage.getItem('hibe-theme');d=s?s==='dark':matchMedia('(prefers-color-scheme: dark)').matches;}catch(e){d=matchMedia('(prefers-color-scheme: dark)').matches;}document.documentElement.classList.toggle('dark',d);})();
"""

APP_JS = r"""(function(){
  var root=document.documentElement,tb=document.getElementById('theme-toggle');
  function label(){var dk=root.classList.contains('dark');if(tb){tb.title=dk?'Açık görünüm':'Karanlık görünüm';tb.setAttribute('aria-label',tb.title);}}
  if(tb){tb.addEventListener('click',function(){root.classList.toggle('dark');try{localStorage.setItem('hibe-theme',root.classList.contains('dark')?'dark':'light');}catch(e){}label();});}
  label();
  function norm(s){return (s||'').toLowerCase().replace(/ı/g,'i').replace(/ş/g,'s').replace(/ğ/g,'g').replace(/ç/g,'c').replace(/ö/g,'o').replace(/ü/g,'u');}
  function setToggle(attr,tab){[].forEach.call(document.querySelectorAll('['+attr+']'),function(b){var on=b.getAttribute(attr)===tab;b.classList.toggle('selected',on);b.setAttribute('aria-pressed',on?'true':'false');});}

  /* Liste */
  var search=document.getElementById('search');
  if(search){
    var tab='school',f={topic:document.getElementById('f-topic'),program:document.getElementById('f-program'),kind:document.getElementById('f-kind')};
    var cards=[].slice.call(document.querySelectorAll('.opportunity-card')),secs=[].slice.call(document.querySelectorAll('.opportunity-section'));
    var count=document.getElementById('count'),forEl=document.getElementById('count-for'),clear=document.getElementById('clear-filters'),empty=document.getElementById('empty');
    var h1=document.getElementById('page-title'),lead=document.getElementById('lead');
    cards.forEach(function(c){c._t=norm(c.getAttribute('data-text'));});
    function apply(){
      var term=norm(search.value.trim()),shown=0;
      cards.forEach(function(c){
        var ok=c.getAttribute('data-tab')===tab&&(!term||c._t.indexOf(term)>-1)&&(!f.topic.value||c.getAttribute('data-topic')===f.topic.value)
          &&(!f.program.value||c.getAttribute('data-program')===f.program.value)&&(!f.kind.value||c.getAttribute('data-kind')===f.kind.value);
        c.hidden=!ok;if(ok)shown++;
      });
      secs.forEach(function(s){var n=s.querySelectorAll('.opportunity-card:not([hidden])').length;s.hidden=n===0;s.querySelector('.group-count').textContent=n;});
      count.textContent=shown+' fırsat';forEl.textContent=tab==='school'?'okulun için listeleniyor':'senin için listeleniyor';
      clear.hidden=!(term||f.topic.value||f.program.value||f.kind.value);empty.hidden=shown>0;
      h1.textContent=h1.getAttribute('data-'+tab);lead.textContent=lead.getAttribute('data-'+tab);
    }
    search.addEventListener('input',apply);
    Object.keys(f).forEach(function(k){f[k].addEventListener('change',apply);});
    clear.addEventListener('click',function(){search.value='';Object.keys(f).forEach(function(k){f[k].value='';});apply();});
    [].forEach.call(document.querySelectorAll('[data-tab-btn]'),function(b){b.addEventListener('click',function(){tab=b.getAttribute('data-tab-btn');setToggle('data-tab-btn',tab);apply();});});
    apply();
  }

  /* Takvim */
  var grid=document.getElementById('cal-grid');
  if(grid){
    var data=JSON.parse(document.getElementById('cal-data').textContent),today=new Date(data.today+'T12:00:00'),ctab='school';
    var year=today.getFullYear(),month=today.getMonth();
    var MONTHS=['Ocak','Şubat','Mart','Nisan','Mayıs','Haziran','Temmuz','Ağustos','Eylül','Ekim','Kasım','Aralık'];
    var base=grid.innerHTML;
    function el(tag,cls,text){var e=document.createElement(tag);if(cls)e.className=cls;if(text!=null)e.textContent=text;return e;}
    function link(it,cls){var a=el('a',cls);a.href='/ilan/'+it.id;return a;}
    function draw(){
      var first=new Date(year,month,1),offset=(first.getDay()+6)%7,days=new Date(year,month+1,0).getDate();
      var cur=data.items.filter(function(i){var d=new Date(i.deadline+'T12:00:00');return i.tab===ctab&&d.getMonth()===month&&d.getFullYear()===year;}).sort(function(a,b){return a.deadline<b.deadline?-1:1;});
      grid.innerHTML=base;
      var total=Math.ceil((offset+days)/7)*7;
      for(var i=0;i<total;i++){
        var day=i-offset+1,valid=day>0&&day<=days;
        var cell=el('div','calendar-cell'+(valid?'':' outside')+(i%7>=5?' weekend':''));
        var num=el('span',valid&&day===today.getDate()&&month===today.getMonth()&&year===today.getFullYear()?'today-day':'',valid?String(day):'');cell.appendChild(num);
        if(valid){cur.filter(function(it){return Number(it.deadline.slice(-2))===day;}).forEach(function(it){var a=link(it,'calendar-event '+it.cls);a.appendChild(el('span'));a.appendChild(document.createTextNode(it.title));cell.appendChild(a);});}
        grid.appendChild(cell);
      }
      document.getElementById('cal-title').textContent=MONTHS[month]+' '+year;
      document.getElementById('cal-count').textContent=cur.length;
      var ag=document.getElementById('cal-agenda');ag.innerHTML='';
      cur.forEach(function(it){
        var a=link(it,'agenda-row'),t=el('time');t.dateTime=it.deadline;var s=el('strong',null,it.deadline.slice(-2));t.appendChild(s);t.appendChild(document.createTextNode(MONTHS[month].slice(0,3)));
        var d=el('div');d.appendChild(el('h3',null,it.title));d.appendChild(el('p',null,it.org));
        var b=el('span','role-badge '+it.cls,it.label);a.appendChild(t);a.appendChild(d);a.appendChild(b);ag.appendChild(a);
      });
      document.getElementById('cal-empty').hidden=cur.length>0;
    }
    function move(n){var d=new Date(year,month+n,1);year=d.getFullYear();month=d.getMonth();draw();}
    document.getElementById('cal-prev').addEventListener('click',function(){move(-1);});
    document.getElementById('cal-next').addEventListener('click',function(){move(1);});
    document.getElementById('cal-today').addEventListener('click',function(){year=today.getFullYear();month=today.getMonth();draw();});
    [].forEach.call(document.querySelectorAll('[data-cal-tab]'),function(b){b.addEventListener('click',function(){ctab=b.getAttribute('data-cal-tab');setToggle('data-cal-tab',ctab);draw();});});
    draw();
  }
})();
"""

NOT_FOUND = """<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sayfa bulunamadı · HibeRadarı</title><link rel="stylesheet" href="/style.css"><script src="/theme.js"></script></head>
<body><main class="page-container"><div class="page-heading"><div><h1>Sayfa bulunamadı</h1><p><a class="back-link" href="/">HibeRadarı ana sayfasına dön</a></p></div></div></main></body></html>
"""


def lovable_css():
    """web/style.css = Lovable src/styles.css portu (ilk bölüm) + Codex'in yerel uygulama için eklediği büyütme/yerleşim
    ezmeleri (sonraki bölüm). Siteye yalnız Lovable bölümü ve gövde/seçim kuralları alınır; ezmeler görünümü bozar."""
    lines = (ROOT / 'web/style.css').read_text(encoding='utf-8').splitlines()
    cut = next(i for i, l in enumerate(lines) if l.startswith('.header-actions{gap:8px;flex-wrap:wrap;}'))
    keep = [l for l in lines[:cut] if l.strip()]
    return '\n'.join(keep) + '\n'


def _render(report, outdir, today=None):
    today = today or datetime.now().date()
    out = Path(outdir)
    (out / 'ilan').mkdir(parents=True, exist_ok=True)
    (out / 'ics').mkdir(parents=True, exist_ok=True)
    items = prepare(report, today)
    stamp = re.sub(r'\D', '', report['generated_at'])[:14]
    stamp = f'{stamp[:8]}T{stamp[8:14]}Z'
    for old in list((out / 'ilan').glob('*.html')) + list((out / 'ics').glob('*.ics')):
        old.unlink()                                       # eski kayıtların sayfaları kalmasın
    for o in items:
        html_text, calendar = detail_page(o, report, today, stamp)
        (out / 'ilan' / f'{o["id"]}.html').write_text(html_text, encoding='utf-8')
        if calendar:
            (out / 'ics' / f'{o["id"]}.ics').write_text(calendar, encoding='utf-8', newline='')
    published = [{k: v for k, v in o.items() if k not in ('group',)} for o in items]
    data = {'generated_at': report['generated_at'], 'counts': report['counts'], 'disclaimer':
            'Yönetici tarafından içerik sürümü onaylanmıştır. Son tarih ve uygunluğu resmî sayfadan doğrulayın.', 'items': published}
    files = {
        'index.html': page('Okulun için bir sonraki fırsat', 'Öğretmenler için hibe, eğitim ve proje fırsatları; her kayıt resmî kaynağına bağlanır. Türkiye, AB, TÜBİTAK, büyükelçilik ve vakıf duyuruları.', index_body(items, report, today), 'list', report, '/'),
        'takvim.html': page('Son başvuru takvimi', 'Okul ve öğretmen fırsatlarının son başvuru tarihlerini aylık takvimde görün.', calendar_body(items, today), 'calendar', report, '/takvim'),
        'nasil-calisir.html': page('Nasıl çalışır?', 'HibeRadarı kaynakları, süzgeci, durum etiketleri ve güncellik bilgisi.', how_body(report), 'how', report, '/nasil-calisir'),
        'style.css': lovable_css() + EXTRA_CSS,
        'app.js': APP_JS, 'theme.js': THEME_JS, '404.html': NOT_FOUND,
        'data.json': json.dumps(data, ensure_ascii=False, indent=1),
        'robots.txt': f'User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n',
        'sitemap.xml': ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                        + ''.join(f'<url><loc>{BASE}{p}</loc></url>' for p in ['/', '/takvim', '/nasil-calisir'] + [f'/ilan/{o["id"]}' for o in items])
                        + '</urlset>\n'),
    }
    for name, content in files.items():
        (out / name).write_text(content, encoding='utf-8')
    return out


class PublicationBlocked(ValueError):
    """Güvenlik kapısı geçilmedi; mevcut yayın korunur."""


def check_publication(report, today=None):
    from hibe.domain import validate, publishable
    today = today or datetime.now().date()
    if report.get('run_status') != 'success' or not report.get('sources'):
        raise PublicationBlocked('Tam ve başarılı kaynak koşusu gerekli')
    if any(s.get('health') != 'success' or s.get('error') for s in report['sources']):
        raise PublicationBlocked('Kaynak hatası veya kısmi sonuç var')
    rows = [row for group in KIND for row in report.get(group, [])]
    if not rows:
        raise PublicationBlocked('Boş yayın ayrıca incelenmeli')
    for row in rows:
        try:
            validate(row)
            if not publishable(row, today):
                raise ValueError('Güncel içerik sürümü için yönetici onayı yok')
        except (ValueError, TypeError, KeyError) as exc:
            raise PublicationBlocked(f'Yayın onayı geçersiz: {exc}') from exc


def build(report, outdir, today=None):
    """Onay kapısı, ayrı staging, kontrollü geçiş ve hata halinde geri dönüş."""
    import os
    import shutil
    import tempfile
    check_publication(report, today)
    out = Path(outdir).resolve()
    if out.is_symlink() or out == Path(out.anchor):
        raise PublicationBlocked('Güvensiz çıktı klasörü')
    out.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f'.{out.name}.stage-', dir=out.parent))
    backup = None
    try:
        _render(report, stage, today)
        data = json.loads((stage / 'data.json').read_text(encoding='utf-8'))
        if not data.get('items') or not (stage / 'index.html').is_file():
            raise PublicationBlocked('Eksik staging çıktısı')
        for item in data['items']:
            if not (stage / 'ilan' / f"{item['id']}.html").is_file():
                raise PublicationBlocked('Eksik ilan çıktısı')
            if item.get('deadline') and not (stage / 'ics' / f"{item['id']}.ics").is_file():
                raise PublicationBlocked('Eksik ICS çıktısı')
        if out.exists():
            backup = Path(tempfile.mkdtemp(prefix=f'.{out.name}.backup-', dir=out.parent))
            backup.rmdir()
            os.replace(out, backup)
        try:
            os.replace(stage, out)
        except BaseException:
            if backup is not None:
                os.replace(backup, out)
            raise
        # Başarılı geçişin önceki yayını da geri dönüş için tutulur.
        return out
    finally:
        if stage.exists():
            shutil.rmtree(stage)
