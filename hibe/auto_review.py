"""Automatic queue triage; relevance hints never become publication approval."""
import re
from datetime import date
from .aggregator.textutil import fold
from .domain import version
from .eligibility import opportunity_type


def classify(call, today):
    title = fold(call.get('title', ''))
    text = fold(' '.join(str(call.get(k) or '') for k in ('title', 'summary', 'description_short')))
    audience = [label for label, pattern in (
        ('lise', r'lise|high school|secondary school'),
        ('ogretmen', r'ogretmen|teacher|teaching'),
        ('okul', r'okul|school|education|egitim|erasmus')) if re.search(pattern, text)]
    kind = opportunity_type(text)
    if kind == 'unknown' and re.search(r'\b(?:hibe|grant|funding|fon|fund)\b', text):
        kind = 'grant'
    assessment = call.get('eligibility_assessment') or {}
    country_results = {v.get('checks', {}).get('country', {}).get('result')
        for v in assessment.get('targets', {}).values()}
    verified = assessment.get('authority') == 'official_reviewed'
    country = ('uygun' if country_results == {'UYGUN'} else
               'uygun_degil' if country_results == {'UYGUN_DEĞİL'} else 'belirsiz') if verified else 'belirsiz'
    reasons = []
    end = None
    try:
        end = date.fromisoformat(call.get('deadline') or '')
    except (ValueError, TypeError):
        pass
    if call.get('deadline_year_inferred') or call.get('deadline_review_required'):
        end = None
    if call.get('official_status') in ('kapandi', 'askida') or (end and end < today):
        group = 'expired'
        reasons.append('Başvuru süresi geçmiş veya çağrı kapalı/askıda.')
    elif country == 'uygun_degil':
        group = 'out_of_scope'
        reasons.append('Mevcut resmî uygunluk kanıtında Türkiye uygun değil.')
    elif re.search(r'ziyaret|katildi|gerceklestirildi|duzenlendi|sonuclari|kazanan|winners|results announced', title) and not re.search(r'basvuru|cagri|apply|applications|call for|hibe|grant', title):
        group = 'news'
        reasons.append('Başlıkta faaliyet/sonuç haberi sinyali var; açık çağrı olarak seçilmedi.')
    elif audience or kind != 'unknown':
        group = 'candidate'
        reasons.append('Hedef kitle veya fırsat türü sinyali bulundu.')
    else:
        group = 'uncertain'
        reasons.append('Mevcut metin hedef kitle ve fırsat türünü belirlemeye yetmiyor.')
    if country == 'belirsiz':
        reasons.append('Türkiye başvuru uygunluğu kanıtı eksik veya çelişkili.')
    if not end:
        reasons.append('Kesin son başvuru tarihi yok.')
    return {'group': group, 'audience_hints': audience, 'type': kind, 'turkey': country,
            'reasons': reasons, 'input_version': version(call),
            'authority': 'automatic_triage', 'publication_approved': False}


def review_queue(calls, today, decisions=None):
    decisions={d['id']:d for d in decisions or []}
    result=[]
    from .domain import publishable
    for call in calls:
        review=classify(call,today)
        if publishable(call,today):
            review['group']='published';review['reasons']=['Bu sürüm doğrulanarak yayına alındı.']
        else:
            decision=decisions.get(call['id'])
            if decision and decision.get('base_version')==version(call):
                status=decision['status']
                review['group']={'closed':'expired','out_of_scope':'out_of_scope'}.get(status,'uncertain')
                review['reasons']=['Toplu belge incelemesi: '+status+'. İncelenen kaynak sürümü kayıtlı; yayın onayı değildir.']
        result.append(dict(call,auto_review=review))
    return result
