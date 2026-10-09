"""Açıklanabilir ilgililik süzgeci: her duyuruya kabul/inceleme/ret kararı ve gerekçe listesi verir.

Başlık + kategori 'baş' metindir (tam ağırlık); açıklama 'gövde' metnidir (yarım ağırlık).
Puan, terimlerin config/relevance.json'daki ağırlıklarının toplamıdır; hiçbir şey kara kutu değildir."""
import json
import re
from datetime import timedelta
from pathlib import Path

from .models import Relevance
from .textutil import fold

ROOT = Path(__file__).resolve().parents[2]


def _compile(term):
    exact = term.endswith('=')
    word = re.escape(fold(term.rstrip('=')))
    return re.compile(rf'(?<![a-z0-9]){word}' + (r'(?![a-z0-9])' if exact else r'[a-z]*'))


def _match(patterns, text):
    for pattern in patterns:
        m = pattern.search(text)
        if m:
            return m.group(0)
    return None


class RelevanceFilter:
    def __init__(self, rules=None):
        self.rules = rules or json.loads((ROOT / 'config/relevance.json').read_text(encoding='utf-8'))
        r = self.rules
        comp = lambda terms: [_compile(t) for t in terms]
        self.audience = {k: (v, comp(v['terms'])) for k, v in r['audience'].items()}
        self.audience_neg = {k: (v, comp(v['terms'])) for k, v in r.get('audience_negative', {}).items()}
        self.programmes = {k: (v, comp(v['terms'])) for k, v in r['programmes'].items()}
        self.call_words = comp(r['call_words']['terms'])
        self.exclude = {k: (v, comp(v['terms'])) for k, v in r['exclude'].items()}
        self.exclude_categories = [fold(c) for c in r.get('exclude_categories', [])]

    def evaluate(self, item, today, implied_programme=None):
        """item.relevance'ı doldurur ve döndürür. Zaman kuralları (süresi dolmuş/eski) dahil."""
        rules = self.rules
        head = fold(' '.join([item.title] + list(item.categories)))
        body = fold(item.description_short)
        score, reasons = 0, []
        audiences, programmes = [], []

        def hit(patterns):
            """(çarpan, eşleşen metin) ya da None; baş eşleşmesi 1.0, gövde 0.5."""
            found = _match(patterns, head)
            if found:
                return 1.0, found
            found = _match(patterns, body)
            return (0.5, found) if found else None

        audience_total, specific_audience = 0, 0
        for key, (spec, patterns) in self.audience.items():
            found = hit(patterns)
            if found:
                points = max(1, round(spec['weight'] * found[0]))
                audience_total += points
                if not spec.get('generic'):
                    specific_audience += points
                audiences.append(key)
                reasons.append(f"+{points} hedef kitle: {spec['label']} ('{found[1]}')")
        score += min(audience_total, 6)

        programme_total = 0
        for key, (spec, patterns) in self.programmes.items():
            found = hit(patterns)
            if found:
                points = max(1, round(spec['weight'] * found[0]))
                programme_total += points
                programmes.append(key)
                reasons.append(f"+{points} program: {spec['label']} ('{found[1]}')")
        if implied_programme and implied_programme not in programmes and implied_programme in self.programmes:
            spec = self.programmes[implied_programme][0]
            programme_total += spec['weight']
            programmes.append(implied_programme)
            reasons.append(f"+{spec['weight']} program: {spec['label']} (kaynağın kendi programı)")
        score += min(programme_total, 6)

        if hit(self.call_words):
            score += rules['call_words']['weight']
            reasons.append(f"+{rules['call_words']['weight']} çağrı/hibe dili")

        for key, (spec, patterns) in self.audience_neg.items():
            found = hit(patterns)
            if found:
                score -= spec['penalty']
                audiences.append('-' + key)
                reasons.append(f"-{spec['penalty']} hedef kitle dışı: {spec['label']} ('{found[1]}')")

        for key, (spec, patterns) in self.exclude.items():
            found = hit(patterns)
            if found:
                points = max(1, round(spec['penalty'] * found[0]))
                score -= points
                reasons.append(f"-{points} hariç: {spec['label']} ('{found[1]}')")

        category_text = ' | '.join(fold(c) for c in item.categories)
        for bad in self.exclude_categories:
            if bad in category_text:
                score -= rules['category_penalty']
                reasons.append(f"-{rules['category_penalty']} hariç kategori: {bad}")

        positive = specific_audience + programme_total > 0   # yalnız genel 'eğitim' kelimesi yetmez
        strong = bool({'school', 'teacher'} & set(audiences)) or any(
            self.programmes[p][0]['weight'] >= 3 for p in programmes)
        t = rules['thresholds']
        verdict = 'reject'
        if positive and score >= t['accept'] and strong:
            verdict = 'accept'
        elif positive and score >= t['review']:
            verdict = 'review'
        if verdict == 'reject':
            reasons.append('ret: okul/öğretmen/program ile eşleşme yok' if not positive
                           else f"ret: puan {score} < inceleme eşiği {t['review']}")

        # Zaman kuralları puandan bağımsız; ama elenen güçlü eşleşme çöpe gitmez, 'watch' olur.
        base = verdict
        expired = bool(item.deadline and item.deadline < today)
        stale = bool(not item.deadline and item.published_at
                     and today - item.published_at > timedelta(days=rules['max_age_days']))
        if expired:
            reasons.append(f'son tarih geçmiş ({item.deadline.isoformat()})')
        elif stale and base != 'reject':
            reasons.append(f"{rules['max_age_days']} günden eski ve son tarih yok")
        if (expired or stale) and base in ('accept', 'review'):
            verdict = 'watch'
            reasons.append('izleme: geçmiş dönem/örnek; program yinelenirse yeni dönemi bekle')
        elif expired:
            verdict = 'reject'
            reasons.append('ret: son tarih geçmiş')
        elif base == 'reject' and score >= 0 and (positive or hit(self.call_words)):
            verdict = 'general'
            reasons.append('genel hibe: okul eşleşmesi belirsiz, uygunluğu elle bak')
        if verdict in ('accept', 'review') and not item.deadline:
            reasons.append('not: son tarih bulunamadı (resmî sayfada doğrulayın)')

        item.audience = [a for a in audiences if not a.startswith('-')]
        if not item.programme and programmes:
            item.programme = self.programmes[programmes[0]][0]['label']
        item.relevance = Relevance(verdict, score, reasons, audiences, programmes)
        return item.relevance
