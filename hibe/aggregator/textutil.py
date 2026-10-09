"""Türkçe/İngilizce/Almanca metin katlama, HTML temizleme ve son tarih çıkarma."""
import re
from datetime import date
from bs4 import BeautifulSoup

# Uzunluğu koruyan 1:1 katlama; eşleşme konumları özgün metinle aynı kalır.
_FOLD = str.maketrans({'ı': 'i', 'ş': 's', 'ğ': 'g', 'ç': 'c', 'ö': 'o', 'ü': 'u', 'ä': 'a',
                       'é': 'e', 'è': 'e', 'á': 'a', 'à': 'a', 'â': 'a', 'î': 'i', 'ô': 'o',
                       'û': 'u', 'ñ': 'n', 'ß': 's', '’': "'", '‘': "'", '–': '-', '—': '-'})


def fold(text):
    return (text or '').replace('İ', 'i').replace('I', 'ı').lower().translate(_FOLD)


def strip_html(html):
    if not html:
        return ''
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
    (re.compile(rf'(?<!\d)(\d{{1,2}})(?:st|nd|rd|th)?\.?\s+({_MONTH_RE})[a-z]*\.?,?\s+(\d{{4}})'), 'dmy'),
    # November 15, 2026
    (re.compile(rf'({_MONTH_RE})[a-z]*\.?\s+(\d{{1,2}})(?:st|nd|rd|th)?,?\s+(\d{{4}})'), 'mdy'),
    # 15.11.2026 · 15/11/2026
    (re.compile(r'(?<!\d)(\d{1,2})[./](\d{1,2})[./](\d{4})(?!\d)'), 'num'),
]
# Tarih yalnız bu ipuçlarından biriyle birlikte "son tarih" sayılır.
CUES = ('son basvuru', 'son tarih', 'son gun', 'son teslim', 'kadar', 'basvurular', 'basvuru tarihi',
        'deadline', 'closing date', 'apply by', 'applications close', 'due', 'until', 'by ',
        'bis zum', 'frist', 'antragsfrist', 'einreichungsfrist', 'bewerbungsschluss', 'anmeldeschluss')


def _make_date(order, groups):
    try:
        if order == 'dmy':
            return date(int(groups[2]), MONTHS[groups[1]], int(groups[0]))
        if order == 'mdy':
            return date(int(groups[2]), MONTHS[groups[0]], int(groups[1]))
        return date(int(groups[2]), int(groups[1]), int(groups[0]))
    except (ValueError, KeyError):
        return None


def find_deadline(text, today_date):
    """(tarih, kanıt) döndürür. İpucu kelimesi olmayan tarih yok sayılır; hiçbiri yoksa (None, None).

    Gelecekteki ipuçlu tarihlerden en yakını seçilir; hepsi geçmişse en geç olan döner
    (süzgeç bunu 'süresi dolmuş' diye eler)."""
    folded = fold(text)
    found = []
    for pattern, order in _DATE_PATTERNS:
        for m in pattern.finditer(folded):
            value = _make_date(order, m.groups())
            if not value or not (2000 <= value.year <= 2100):
                continue
            window = folded[max(0, m.start() - 90):m.end() + 40]
            if any(cue in window for cue in CUES):
                snippet = re.sub(r'\s+', ' ', text[max(0, m.start() - 60):m.end() + 20]).strip()
                found.append((value, snippet))
    if not found:
        return None, None
    future = [f for f in found if f[0] >= today_date]
    return min(future) if future else max(found)
