"""İlgililik puanından bağımsız, resmî alıntılara dayalı üç değerli uygunluk."""
import re
from datetime import datetime, timezone, date
from hibe.aggregator.textutil import fold

UNKNOWN='DOĞRULAMA_GEREKLİ'
YES='UYGUN'
NO='UYGUN_DEĞİL'
TARGETS=('school','teacher','student_14_18','school_partner','ngo_channel')

PATTERNS={
 'country':[(YES,r'(?:turkiye|turkey).{0,50}(?:basvurabilir|uygundur|eligible|may apply)'),(NO,r'(?:turkiye|turkey).{0,30}(?:haric|excluded|not eligible)')],
 'school':[(YES,r'devlet liseleri.{0,40}basvurabilir'),(NO,r'(?:yalnizca|only).{0,30}(?:universite|universities|dernek|stk|ngo)')],
 'teacher':[(YES,r'ogretmenler.{0,40}(?:bireysel )?basvurabilir'),(NO,r'(?:yalnizca|only).{0,30}(?:universite ogrencileri|university students)')],
 'student_14_18':[(YES,r'lise ogrencileri.{0,40}basvurabilir'),(NO,r'(?:yalnizca|only).{0,30}(?:universite ogrencileri|university students|doktora|phd)')],
 'school_partner':[(YES,r'okullar.{0,40}ortak.{0,20}(?:olabilir|katilabilir)')],
 'ngo_channel':[(YES,r'(?:dernek|stk).{0,40}(?:uzerinden|basvurabilir)')],
 'partner':[(YES,r'(?:ortak zorunlulugu yok|partner not required)'),(UNKNOWN,r'(?:ortak zorunlu(?:dur)?\b|partner required)')],
 'application_path':[(YES,r'(?:bireysel basvuru|okul adina basvuru|dernek uzerinden basvuru)')],
}

def opportunity_type(text):
    t=fold(text)
    for kind,pattern in [('scholarship',r'burs|scholarship'),('competition',r'yarisma|prize|competition'),('teacher_training',r'ogretmen.{0,30}(?:kurs|egitim)|teacher training'),('partner_search',r'ortak bulma|partner search'),('eu_project',r'erasmus|horizon|interreg'),('annual_programme',r'yillik program|annual programme')]:
        if re.search(pattern,t):return kind
    return 'unknown'

def assess(row, today):
    text=' '.join([row.get('title',''),row.get('description_short','')])
    checked=datetime.now(timezone.utc).isoformat()
    url=row.get('official_url') or row.get('source_url')
    verified=row.get('official_source_verified') is True
    clauses=re.split(r'(?<=[.!?;])\s+',text)
    facts={}
    for field,rules in PATTERNS.items():
        hits=[{'result':result,'quote':clause,'url':url,'checked_at':checked,'verified':verified}
              for clause in clauses for result,pattern in rules if re.search(pattern,fold(clause))]
        outcomes={h['result'] for h in hits}
        result=next(iter(outcomes)) if len(outcomes)==1 and verified else UNKNOWN
        facts[field]={'result':result,'evidence':hits,'checked_at':checked}
    age_hits=[]
    for clause in clauses:
        m=re.search(r'(\d{1,2})\s*[-–]\s*(\d{1,2})\s*(?:yas|years)',fold(clause))
        if m:
            low,high=map(int,m.groups())
            result=YES if low<=14 and high>=18 else NO if high<14 or low>18 else UNKNOWN
            age_hits.append({'result':result,'min':low,'max':high,'quote':clause,'url':url,'verified':verified})
    outcomes={h['result'] for h in age_hits}
    facts['age']={'result':next(iter(outcomes)) if len(outcomes)==1 and verified else UNKNOWN,'evidence':age_hits,'checked_at':checked}
    exact=row.get('deadline_precision')=='day' and not row.get('deadline_year_inferred') and not row.get('deadline_review_required')
    d=None
    try:d=date.fromisoformat(row.get('deadline') or '')
    except (ValueError,TypeError):pass
    proven=verified and exact and bool(row.get('deadline_evidence')) and d is not None
    facts['deadline']={'result':NO if proven and d<today else YES if proven else UNKNOWN,
        'evidence':[{'quote':row.get('deadline_evidence'),'url':row.get('deadline_source_url') or url,'value':row.get('deadline')}], 'checked_at':checked}
    targets={}
    for target in TARGETS:
        keys=['country',target,'partner','application_path','deadline'] + (['age'] if target=='student_14_18' else [])
        results=[facts[k]['result'] for k in keys]
        ngo_only = verified and any(re.search(r'(?:yalnizca|only).{0,25}(?:stk|dernek|ngo)',fold(c)) for c in clauses)
        if ngo_only and target in ('school','teacher','student_14_18'): results.append(NO)
        status=NO if NO in results else YES if all(r==YES for r in results) else UNKNOWN
        checks={k:facts[k] for k in keys}
        checks['applicant_type']={'result':NO if ngo_only and target in ('school','teacher','student_14_18') else facts[target]['result'],
            'evidence':[{'quote':c,'url':url,'checked_at':checked} for c in clauses if re.search(r'(?:yalnizca|only).{0,25}(?:stk|dernek|ngo)',fold(c))] if ngo_only else facts[target]['evidence'],'checked_at':checked}
        targets[target]={'status':status,'checks':checks,'checked_at':checked}
    return {'type':opportunity_type(text),'targets':targets,'checked_at':checked,'authority':'official_reviewed' if verified else 'unverified_source'}
