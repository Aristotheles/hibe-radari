"""Refresh permitted sources in the existing store; never approve or deploy."""
import json
from .aggregator.collector import load_config, due_sources, run, write_report, ROOT
from .aggregator.bridge import persist_report


def refresh(store):
    config = load_config()
    config = dict(config, sources=[s for s in config['sources']
        if s.get('access_policy', {}).get('terms_status') == 'allowed'])
    settings = store.all('source_settings')
    due = due_sources(config, store.all('source_health'), source_settings=settings)
    if not due:
        return {'status': 'not_due', 'sources': 0, 'changed': 0}
    report = run(config=config, only=due, source_settings=settings)
    report['audit_scope'] = 'scheduled_permitted_sources; no approval or publication'
    write_report(report, ROOT / 'data/aggregator/refresh-attempt.json')
    # General news and rejected noise are not opportunities in the review queue.
    # A verified first-party teacher course catalogue is already a discovery scope.
    # Weak title keywords must not suppress new courses before full-document review.
    courses=[row for group in ('general','rejected') for row in report.get(group,[])
        if row.get('source_id')=='esep-courses']
    candidates = dict(report, review=report.get('review',[])+courses,general=[], rejected=[])
    changed = persist_report(candidates, store)
    return {'status': report['run_status'], 'sources': len(report['sources']),
            'changed': changed, 'counts': report['counts'],
            'unhealthy': [s['id'] for s in report['sources'] if s['health'] != 'success']}


def main():
    from .server import App
    result = refresh(App(demo=False).service.store)
    path = ROOT / 'data/aggregator/refresh-status.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    from datetime import datetime, timezone
    result['finished_at'] = datetime.now(timezone.utc).isoformat()
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False))
    return 1 if result.get('unhealthy') else 0


if __name__ == '__main__':
    raise SystemExit(main())
