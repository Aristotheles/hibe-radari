"""Grants.gov's documented, unauthenticated public opportunity API."""
import json,re
from datetime import datetime
from .models import GrantOpportunity
from .textutil import strip_html

def opportunity_id(value):
    value=str(value)
    if not re.fullmatch(r'[1-9][0-9]{0,9}',value):raise ValueError('Geçersiz Grants.gov fırsat kimliği')
    return value

def read_data(response):
    payload=response.json()
    if payload.get('errorcode')!=0 or not isinstance(payload.get('data'),dict):
        raise ValueError('Grants.gov API yanıtı başarısız/geçersiz')
    # Provider response tokens and contacts are never copied into discovery rows.
    return payload['data']

def collect(source,fetcher,today):
    rows={};size=source.get('page_size',100)
    for keyword in source['queries']:
        for page in range(source.get('max_pages',10)):
            data=read_data(fetcher.request('POST',source['search_url'],json={'rows':size,'keyword':keyword,'oppStatuses':'posted','startRecordNum':page*size}))
            hits=data.get('oppHits')
            if not isinstance(hits,list):raise ValueError('Grants.gov fırsat listesi eksik')
            for hit in hits:
                ident=opportunity_id(hit['id']);title=hit.get('title')
                if not isinstance(title,str) or not title.strip():raise ValueError('Grants.gov başlığı eksik')
                deadline=None
                if hit.get('closeDate'):
                    deadline=datetime.strptime(hit['closeDate'],'%m/%d/%Y').date()
                rows.setdefault(ident,GrantOpportunity(title=title,source_id=source['id'],
                    source_url=source['entry_url_template'].format(entry_id=ident),
                    source_entry_id=ident,identity_authority='api.grants.gov',official_call_id=hit.get('number'),
                    organization=hit.get('agency') or hit.get('agencyName'),deadline=deadline,
                    deadline_evidence=f"API closeDate: {hit['closeDate']}" if deadline else None,
                    deadline_source_url=source['search_url'],language='en',status_hint='açık'))
            if (page+1)*size>=data.get('hitCount',0) or not hits:break
        else:
            raise ValueError('Grants.gov sayfa sınırı; eksik tarama başarılı sayılmadı')
    return list(rows.values())

def detail_text(source,fetcher,ident):
    ident=opportunity_id(ident)
    data=read_data(fetcher.request('POST',source['detail_url'],json={'opportunityId':int(ident)}))
    if str(data.get('id'))!=ident:raise ValueError('Grants.gov ayrıntı kimliği uyuşmuyor')
    synopsis=data.get('synopsis') or {}
    fields={'opportunityId':ident,'opportunityTitle':data.get('opportunityTitle'),'opportunityNumber':data.get('opportunityNumber')}
    for key in ('agencyName','synopsisDesc','applicantEligibilityDesc','responseDateStr','responseDate','awardCeiling','awardFloor','costSharing','fundingDescLinkUrl'):
        value=synopsis.get(key)
        fields[key]=strip_html(value) if isinstance(value,str) else value
    fields['applicantTypes']=[x.get('description') for x in synopsis.get('applicantTypes',[])]
    fields['fundingActivityCategories']=[x.get('description') for x in synopsis.get('fundingActivityCategories',[])]
    # Preserve public field values as readable evidence. JSON string escaping
    # must not turn real paragraph breaks into literal backslash-n in quotes.
    text='\n\n'.join(key+':\n'+('\n'.join(str(x) for x in value) if isinstance(value,list)
        else str(value)) for key,value in fields.items() if value is not None)
    if len(text)>48000:raise ValueError('Grants.gov belgesi fazla büyük; sessiz kırpılmadı')
    return text
