"""Toplayıcının ortak veri modeli. Bilinmeyen alan None kalır; tahmin edilmez."""
import hashlib
from dataclasses import dataclass, field, asdict
from datetime import date, datetime
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

TRACKING = ('utm_', 'fbclid', 'gclid')


def canonical_url(url):
    """Aynı sayfanın http/https, #parça ve izleme parametresi farklarını eşitler."""
    u = urlsplit(url.strip())
    query = urlencode([(k, v) for k, v in parse_qsl(u.query) if not k.startswith(TRACKING)])
    path = u.path.rstrip('/') or '/'
    return urlunsplit(('https', (u.hostname or '').lower(), path, query, ''))


def opportunity_id(url):
    return hashlib.sha256(canonical_url(url).encode()).hexdigest()[:20]


@dataclass
class Relevance:
    verdict: str = 'review'                     # accept | review | reject
    score: int = 0
    reasons: list = field(default_factory=list)  # her puan değişiminin gerekçesi
    audience: list = field(default_factory=list)
    programmes: list = field(default_factory=list)


@dataclass
class GrantOpportunity:
    title: str
    source_id: str                  # config/aggregator.json kaynak kimliği
    source_url: str                 # duyurunun bulunduğu sayfa (kaynak linki)
    organization: str | None = None
    deadline: date | None = None
    deadline_evidence: str | None = None   # son tarihin çıkarıldığı metin parçası
    audience: list = field(default_factory=list)
    programme: str | None = None
    description_short: str = ''
    language: str | None = None
    published_at: date | None = None
    original_url: str | None = None        # derleme sitelerinde resmî sayfa adayı (sezgisel)
    status_hint: str | None = None         # sabit izleme sayfalarında metne göre: açık | kapalı | belirsiz
    aggregator: bool = False
    categories: list = field(default_factory=list)
    seen_in: list = field(default_factory=list)   # aynı duyurunun göründüğü diğer kaynaklar
    relevance: Relevance = field(default_factory=Relevance)

    @property
    def id(self):
        return opportunity_id(self.source_url)

    def to_dict(self):
        data = asdict(self)
        data['id'] = self.id
        for key in ('deadline', 'published_at'):
            data[key] = data[key].isoformat() if data[key] else None
        return data


def today():
    return datetime.now().date()
