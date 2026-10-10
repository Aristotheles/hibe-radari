"""Türkçe/İngilizce/Almanca metin katlama, HTML temizleme ve son tarih çıkarma."""
import re
from datetime import date
from html import unescape
from bs4 import BeautifulSoup

# Uzunluğu koruyan 1:1 katlama; eşleşme konumları özgün metinle aynı kalır.
_FOLD = str.maketrans({'ı': 'i', 'ş': 's', 'ğ': 'g', 'ç': 'c', 'ö': 'o', 'ü': 'u', 'ä': 'a',
                       'é': 'e', 'è': 'e', 'á': 'a', 'à': 'a', 'â': 'a', 'î': 'i', 'ô': 'o',
                       'û': 'u', 'ñ': 'n', 'ß': 's', '’': "'", '‘': "'", '–': '-', '—': '-'})


def fold(text):
    return (text or '').replace('İ', 'i').replace('I', 'ı').lower().replace('i\u0307', 'i').translate(_FOLD)


def strip_html(html):
    if not html:
        return ''
    if '<' not in html:
        return re.sub(r'\s+', ' ', unescape(html)).strip()
    soup = BeautifulSoup(html, 'html.parser')
    for tag in soup(['script', 'style']):
        tag.decompose()
    return re.sub(r'\s+', ' ', soup.get_text(' ', strip=True)).strip()


def shorten(text, limit=280):
    text = re.sub(r'\s+', ' ', text or '').strip()
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(' ', 1)[0].rstrip(' ,;:.') + '…'


MONTHS = {
    'ocak': 1, 'subat': 2, 'mart': 3, 'nisan': 4, 'mayis': 5, 'haziran': 6, 'temmuz': 7,
    'agustos': 8, 'eylul': 9, 'ekim': 10, 'kasim': 11, 'aralik': 12,
    'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6, 'july': 7,
    'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12,
    'januar': 1, 'februar': 2, 'marz': 3, 'maerz': 3, 'mai': 5, 'juni': 6, 'juli': 7,
    'oktober': 10, 'dezember': 12,
}
_MONTH_RE = '|'.join(sorted(MONTHS, key=len, reverse=True))
_DATE_PATTERNS = [
    # 6. Dezember 2026 · 15 Kasım 2026 · 15th November 2026
    (re.compile(rf'(?<!\d)(\d{{1,2}})(?:st|nd|rd|th)?\.?(?:\s+of)?\s+({_MONTH_RE})[a-z]*\.?,?\s+(\d{{4}})'), 'dmy'),
    # November 15, 2026
    (re.compile(rf'({_MONTH_RE})[a-z]*\.?\s+(\d{{1,2}})(?:st|nd|rd|th)?,?\s+(\d{{4}})'), 'mdy'),
    (re.compile(r'(?<!\d)(\d{4})-(\d{2})-(\d{2})(?!\d)'), 'iso'),
    # 15.11.2026 · 15/11/2026
    (re.compile(r'(?<!\d)(\d{1,2})[./](\d{1,2})[./](\d{4})(?!\d)'), 'num'),
]
# Tarih yalnız bu ipuçlarından biriyle birlikte "son tarih" sayılır.
CUES = ('son basvuru', 'son tarih', 'son gun', 'son teslim', 'kadar', 'basvurular', 'basvuru tarihi',
        'deadline', 'closing date', 'apply by', 'applications close', 'due', 'until', 'by ',
        'bis zum', 'frist', 'antragsfrist', 'einreichungsfrist', 'bewerbungsschluss', 'anmeldeschluss')


def _make_date(order, groups):
    try:
        if order == 'iso': return date(int(groups[0]), int(groups[1]), int(groups[2]))
        if order == 'dmy':
            return date(int(groups[2]), MONTHS[groups[1]], int(groups[0]))
        if order == 'mdy':
            return date(int(groups[2]), MONTHS[groups[0]], int(groups[1]))
        return date(int(groups[2]), int(groups[1]), int(groups[0]))
    except (ValueError, KeyError):
        return None


END_CUES = ('son basvuru', 'son tarih', 'son gun', 'son teslim', 'deadline', 'closing date',
            'apply by', 'applications close', 'due', 'until', 'bis zum', 'frist',
            'bewerbungsschluss', 'anmeldeschluss', 'kadar', 'kapan', 'sona er')
START_CUES = ('baslar', 'baslangic', 'acilis', 'opens', 'start', 'begin')


def deadline_details(text, today_date):
    """Son tarih adayları ve day/month/unknown kesinliği; başlangıç günü son tarih değildir."""
    text = text or ''
    # Katlama uzunluğu değişebilir; kanıt dilimini özgün karakter konumlarına eşleriz.
    folded_parts, offsets = [], []
    for index, char in enumerate(text):
        part = fold(char) if char != '\u0307' else ''
        folded_parts.append(part)
        offsets.extend([index] * len(part))
    folded = ''.join(folded_parts)
    def evidence_slice(start, end):
        if not offsets: return ''
        return text[offsets[max(0, start)]:offsets[min(len(offsets)-1, end-1)]+1]
    found = []
    patterns = list(_DATE_PATTERNS) + [(re.compile(rf'(?<!\d)(\d{{1,2}})\s+({_MONTH_RE})(?![a-z])(?!\s+\d{{4}})'), 'no_year')]
    for pattern, order in patterns:
        for m in pattern.finditer(folded):
            if order == 'no_year':
                try: value = date(today_date.year, MONTHS[m.group(2)], int(m.group(1)))
                except ValueError: continue
            else: value = _make_date(order, m.groups())
            if not value or not 2000 <= value.year <= 2100: continue
            before = folded[max(0,m.start()-90):m.start()]
            after = folded[m.end():m.end()+45]
            # Sonraki tarihin ipucunu önceki başlangıca taşımayız.
            next_date = re.search(r'\d{1,4}[./-]|\d{1,2}\s+(?:'+_MONTH_RE+')', after)
            if next_date: after = after[:next_date.start()]
            if any(cue in after[:24] for cue in START_CUES): continue
            latest_end = max((before.rfind(c) for c in END_CUES), default=-1)
            latest_start = max((before.rfind(c) for c in START_CUES), default=-1)
            tail_end = any(cue in after[:35] for cue in ('kadar','kapan','sona er','deadline'))
            if latest_end < 0 and not tail_end: continue
            if latest_start > latest_end and not tail_end: continue
            evidence = re.sub(r'\s+', ' ', evidence_slice(m.start()-60,m.end()+35)).strip()
            found.append({'value':value,'precision':'day','evidence':evidence,
                          'year_inferred': order=='no_year'})
    # Aynı gün ikinci desenle/yıl eksik desenle yinelenmez.
    found = list({x['value']: x for x in reversed(found)}.values())
    if found:
        future = [x for x in found if x['value'] >= today_date]
        chosen = min(future,key=lambda x:x['value']) if future else max(found,key=lambda x:x['value'])
        return dict(chosen, candidates=[dict(x,value=x['value'].isoformat()) for x in sorted(found,key=lambda x:x['value'])])
    for m in re.finditer(rf'({_MONTH_RE})\s+(\d{{4}})',folded):
        window=folded[max(0,m.start()-60):m.end()+20]
        if any(cue in window for cue in END_CUES):
            return {'value':None,'precision':'month','month':f'{m.group(2)}-{MONTHS[m.group(1)]:02d}',
                    'evidence':evidence_slice(m.start()-60,m.end()+20).strip(),'year_inferred':False,'candidates':[]}
    return {'value':None,'precision':'unknown','evidence':None,'year_inferred':False,'candidates':[]}


def find_deadline(text, today_date):
    details = deadline_details(text,today_date)
    return details['value'], details['evidence']
