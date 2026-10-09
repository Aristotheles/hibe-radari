"""Internetsiz kaynak envanteri denetimi; kaynak veya çağrı keşfetmez."""

import argparse
import json
import sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
TARGET = 30


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
    errors = []
    rows = []
    ids = set()
    if not isinstance(sources, list):
        return {'target': TARGET, 'count': 0, 'candidate_names': 0,
                'missing_identities': 0, 'verified_identities': 0,
                'ready_controls': 0, 'complete': False,
                'errors': ['Envanter bir liste olmalı'], 'rows': []}
    if len(sources) != TARGET:
        errors.append(f'Tam {TARGET} kayıt gerekli; mevcut: {len(sources)}')
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
        rows.append({'id': key, 'name': name or 'Kimlik eksik',
                     'identity_status': 'missing' if missing else identity,
                     'identity_verified': identity_ok, 'method': method,
                     'control_ready': not gaps, 'gaps': gaps})
    return {'target': TARGET, 'count': len(sources),
            'candidate_names': sum(r['identity_status'] == 'candidate' for r in rows),
            'missing_identities': sum(r['identity_status'] == 'missing' for r in rows),
            'verified_identities': sum(r['identity_verified'] for r in rows),
            'ready_controls': sum(r['control_ready'] for r in rows),
            'complete': not errors and len(rows) == TARGET and all(r['control_ready'] for r in rows),
            'errors': errors, 'rows': rows}


def markdown_report(report):
    lines = ['# 30 kaynak — eksik ve kabul kontrol listesi', '',
             'Bu rapor internetsiz olarak config/sources.json üzerinden üretilir. URL doğrulaması yalnız biçim/host denetimidir; canlı erişim, parser fixture veya belge doğruluğu testi değildir.', '',
             f"Hedef: {report['target']} · Kayıt yeri: {report['count']} · Doğrulanmamış isim: {report['candidate_names']} · Eksik kimlik: {report['missing_identities']} · Kontrol bilgisi tam: {report['ready_controls']}", '',
             'Özgün kaynak belgesi eşleşmesi, gerçek kontrol ve otomatik kaynaklara özgü fixture testleri olmadan MVP aşama 3 tamamlandı sayılamaz.', '',
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
