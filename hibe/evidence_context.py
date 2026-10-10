"""Literal evidence plus narrow source context, without arbitrary quote lengths."""
import re
from .aggregator.textutil import fold


def literal_quote(quote, text):
    return isinstance(quote, str) and bool(quote.strip()) and ' '.join(fold(quote).split()) in ' '.join(fold(text).split())


def country_list_entry(quote, text):
    if not literal_quote(quote, text) or not re.search(r'\b(?:turkiye|turkey)\b',fold(quote)):
        return False
    # A named eligibility list, not a mission statement or an isolated country mention.
    normalized = fold(text)
    for heading in re.finditer(r'(?:eligible countries|countries eligible to apply|uygun ulkeler|basvurabilecek ulkeler)\b\s*[:\n]?', normalized):
        section = normalized[heading.end():].split('\n\n', 1)[0][:4000]
        if ' '.join(fold(quote).split()) in ' '.join(section.split()) and re.search(r'\b(?:turkiye|turkey)\b', section):
            return True
    return False


def condition_quote(quote, text):
    # Short field values need a typed list context; headings alone are insufficient.
    if not literal_quote(quote,text):return False
    if country_list_entry(quote,text):return True
    # A sentence can be short ("May apply."); headings alone cannot prove a condition.
    return bool(re.search(r'apply|eligible|participants?|teachers?|students?|schools?|citizens?|must|not |may |only |required|years?|basvur|uygun|ogretmen|ogrenci|okul|vatandas|zorunlu|yas|gerek|yalniz',fold(quote)))


def country_application_clause(quote):
    value=fold(quote)
    return bool(re.search(r'apply|applicants?|eligible|participants?|citizens?|applications?|basvur|katilimci|vatandas|uygun|eligibility',value))
