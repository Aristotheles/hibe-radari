"""Internetsiz kaynak envanteri denetimi; kaynak veya çağrı keşfetmez."""

import argparse
import json
import sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
REQUESTED_TARGET = 127



def inventory_rows(path=None):
    """Araştırma tablosunu kayıpsız okur; erişim ölçümünü çalışma izni saymaz."""
    rows=[];group=None
    for line_number,line in enumerate((path or ROOT/'docs/KAYNAK_ENVANTERI.md').read_text(encoding='utf-8').splitlines(),1):
        if line.startswith('## '): group=line[3:]
        if not line.startswith('| '): continue
        parts=[cell.strip() for cell in line.strip().strip('|').split('|')]
        if len(parts)!=5 or not parts[1].startswith('https://'): continue
        rows.append({'name':parts[0],'url':parts[1],'measured_access':parts[2],
                     'suggested_method':parts[3],'note':parts[4],'group':group,
                     'inventory_line':line_number,'identity_evidence':f'docs/KAYNAK_ENVANTERI.md:{line_number}'})
    if len({r['url'] for r in rows}) != len(rows):raise ValueError('Envanterde tekrarlanan URL')
    return rows

def valid_url(value, allowed_hosts=None):
    if not isinstance(value, str):
        return False
    try:
        url = urlsplit(value)
        return bool(url.scheme == 'https' and url.hostname and not url.username
                    and not url.password and url.port in (None, 443)
                    and (allowed_hosts is None or url.hostname in allowed_hosts))
    except ValueError:
        return False


def audit_sources(sources):
    inventory = inventory_rows()
    target = len(inventory)
    errors = []
    rows = []
    ids = set()
    if not isinstance(sources, list):
        return {'target': target, 'count': 0, 'candidate_names': 0,
                'missing_identities': 0, 'verified_identities': 0,
                'ready_controls': 0, 'complete': False,
                'errors': ['Envanter bir liste olmalı'], 'rows': []}
    scope = [s for s in sources if isinstance(s,dict) and s.get('record_kind') not in ('legacy_placeholder','legacy_source')]
    if len(scope) != target:
        errors.append(f'Tam {target} envanter URL kaydı gerekli; mevcut: {len(scope)}')
    if any(s.get('record_kind')=='inventory' for s in scope):
        missing={r['url'] for r in inventory}-{s.get('url') for s in scope}
        if missing:errors.append(f'Envanterde olup kayıtta olmayan URL: {len(missing)}')
    for index, source in enumerate(sources, 1):
        if not isinstance(source, dict):
            errors.append(f'{index}. kayıt nesne olmalı')
            continue
        key = source.get('id')
        if not isinstance(key, str) or not key:
            errors.append(f'{index}. kayıt kimliği eksik')
        elif key in ids:
            errors.append(f'Tekrarlanan kaynak kimliği: {key}')
        else:
            ids.add(key)
        name = source.get('name')
        missing = not isinstance(name, str) or not name.strip() or 'özgün liste bekleniyor' in name
        identity = source.get('identity_status', 'missing' if missing else 'candidate')
        gaps = []
        if identity == 'verified' and not missing and source.get('identity_evidence'):
            identity_ok = True
        else:
            identity_ok = False
            gaps.append('Özgün kaynak kimliği eksik' if missing or identity == 'missing' else 'Kimlik özgün belgede doğrulanmadı')
        if identity not in ('candidate', 'missing', 'verified'):
            errors.append(f'{key}: geçersiz kimlik durumu')
        if not valid_url(source.get('url')):
            gaps.append('Doğrulanmış HTTPS kaynak URL’si eksik')
        method = source.get('method')
        if method == 'manual':
            check = source.get('manual_check')
            if not isinstance(check, dict) or not valid_url(check.get('url')) or not isinstance(check.get('steps'), str) or not check['steps'].strip():
                gaps.append('Görünür manuel kontrol URL’si ve adımları eksik')
        elif method == 'auto':
            hosts = source.get('allowed_hosts')
            calls = source.get('call_urls')
            if source.get('type') != 'official':
                gaps.append('Otomatik kaynak resmî türde değil')
            if not isinstance(hosts, list) or not hosts or not all(isinstance(h, str) and h for h in hosts):
                gaps.append('İzinli host listesi eksik')
                hosts = []
            if not isinstance(calls, list) or not calls:
                gaps.append('Doğrulanmış çağrı URL’leri eksik')
            else:
                for call in calls:
                    documents = call.get('documents', []) if isinstance(call, dict) else None
                    if not isinstance(call, dict) or not valid_url(call.get('url'), hosts) or not isinstance(documents, list) or any(not valid_url(url, hosts) for url in documents):
                        gaps.append('Çağrı / belge URL’si izinli HTTPS host ile uyuşmuyor')
                        break
        else:
            gaps.append('Kontrol yöntemi manual veya auto olmalı')
        if not source.get('last_checked'):
            gaps.append('Gerçek kontrol kanıtı/tarihi yok')
        if source.get('status') != 'ready':
            gaps.append('Kaynak hazır durumda değil')
        rows.append({'in_scope':source.get('record_kind') not in ('legacy_placeholder','legacy_source'),'id': key, 'name': name or 'Kimlik eksik',
                     'identity_status': 'missing' if missing else identity,
                     'identity_verified': identity_ok, 'method': method,
                     'control_ready': not gaps, 'gaps': gaps})
    return {'target': target, 'requested_target':REQUESTED_TARGET,'scope_count':len(scope),'legacy_count':len(sources)-len(scope),'count': len(sources),
            'candidate_names': sum(r['identity_status'] == 'candidate' for r in rows),
            'missing_identities': sum(r['identity_status'] == 'missing' for r in rows),
            'verified_identities': sum(r['identity_verified'] for r in rows),
            'ready_controls': sum(r['control_ready'] for r in rows),
            'complete': not errors and len(scope) == target and all(r['control_ready'] for r in rows if r['in_scope']),
            'errors': errors, 'rows': rows}


def markdown_report(report):
    lines = [f"# {report['target']} envanter URL'si — eksik ve kabul kontrol listesi", '',
             'Bu rapor internetsiz olarak config/sources.json üzerinden üretilir. URL doğrulaması yalnız biçim/host denetimidir; canlı erişim, parser fixture veya belge doğruluğu testi değildir.', '',
             f"Hedef: {report['target']} · Kayıt yeri: {report['count']} · Doğrulanmamış isim: {report['candidate_names']} · Eksik kimlik: {report['missing_identities']} · Kontrol bilgisi tam: {report['ready_controls']}", '',
             'Özgün kaynak belgesi eşleşmesi, gerçek kontrol ve otomatik kaynaklara özgü fixture testleri olmadan canlı kaynak kabulü tamamlandı sayılamaz.', '',
             '| ID | Mevcut isim / yer | Eksikler |', '|---|---|---|']
    for row in report['rows']:
        clean = lambda s: str(s).replace('|', '\\|').replace('\n', ' ')
        lines.append(f"| {clean(row['id'])} | {clean(row['name'])} | {clean('; '.join(row['gaps']) or 'Kayıt alanları tam; canlı/fixture kabulü ayrıca gerekli')} |")
    if report['errors']:
        lines += ['', 'Envanter hataları: ' + '; '.join(report['errors'])]
    return '\n'.join(lines) + '\n'


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--strict', action='store_true', help='Eksik kontrol varsa çıkış kodu 1')
    parser.add_argument('--markdown', action='store_true', help='Markdown kontrol listesi yazdır')
    args = parser.parse_args()
    sources = json.loads((ROOT / 'config/sources.json').read_text(encoding='utf-8'))
    report = audit_sources(sources)
    print(markdown_report(report) if args.markdown else json.dumps(report, ensure_ascii=False, indent=2))
    if args.strict and not report['complete']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
