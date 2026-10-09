"""python -m hibe.aggregator [--only ID ...] [--out DOSYA] [--rejected]

Canlı kaynaklardan duyuru toplar, süzer ve data/aggregator/latest.json dosyasına yazar.
Firebase/Gemini/SMTP kullanmaz; yayın yapmaz."""
import argparse
import sys

from . import run, write_report


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--only', nargs='*', help='yalnız bu kaynak kimlikleri')
    ap.add_argument('--out', help='çıktı JSON yolu (varsayılan data/aggregator/latest.json)')
    ap.add_argument('--rejected', action='store_true', help='gürültü olarak elenenleri gerekçeleriyle yazdır')
    ap.add_argument('--site', metavar='KLASÖR', help='statik siteyi bu klasöre üret (Firebase Hosting için public/)')
    args = ap.parse_args(argv)
    sys.stdout.reconfigure(encoding='utf-8')
    report = run(only=args.only)
    from pathlib import Path
    from .collector import ROOT
    canonical = ROOT / 'data/aggregator/latest.json'
    target = Path(args.out).resolve() if args.out else canonical
    unsafe = report.get('run_status') != 'success' or args.only is not None
    if unsafe:
        if target == canonical.resolve():
            target = canonical.with_name('last-attempt.json')
        write_report(report, target)
        print('Eksik/şüpheli koşu: son sağlam rapor ve site korunuyor')
        return 1
    if args.site:
        from .site import check_publication, PublicationBlocked
        try:
            check_publication(report)
        except PublicationBlocked as exc:
            write_report(report, canonical.with_name('last-attempt.json'))
            print(f'Yayın engellendi: {exc}')
            return 1
    if args.site:
        from .site import build
        print(f'Statik site: {build(report, args.site)}')
    path = write_report(report, target)
    c = report['counts']
    print(f"Tarih {report['today']} · kabul {c['accept']} · inceleme {c['review']} · izleme {c['watch']} · "
          f"genel {c['general']} · gürültü {c['reject']}")
    for s in report['sources']:
        print(f"  {s['id']:<15} çekilen {s['fetched']:>3} · ayrıntı {s['enriched']:>2} · istek {s['requests']:>2}"
              + (f" · HATA {s['error']}" if s['error'] else ''))
    for label, key in (('KABUL', 'accepted'), ('İNCELEME', 'review')):
        for o in report[key]:
            print(f"[{label}] {o['deadline'] or 'tarih yok':<10} {o['title'][:80]}\n          {o['source_url']}")
    for label, key in (('İZLEME', 'watch'), ('GENEL', 'general')):
        for o in report[key]:
            print(f"[{label}] {o['deadline'] or '-':<10} {o['title'][:80]}")
    if args.rejected:
        for o in report['rejected']:
            print(f"[RET] {o['title'][:70]} :: {o['relevance']['reasons'][-1]}")
    print(f'Rapor: {path}')
    return 1 if any(s['error'] for s in report['sources']) else 0


if __name__ == '__main__':
    raise SystemExit(main())
