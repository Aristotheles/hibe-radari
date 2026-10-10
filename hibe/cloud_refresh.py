"""Cloud job entry point using service identity, without web/admin credentials."""
import json
import os
from datetime import datetime, timezone
from .refresh import refresh
from .store import FirestoreStore


def main():
    project = os.environ.get('FIREBASE_PROJECT_ID')
    if not project:
        raise ValueError('FIREBASE_PROJECT_ID gerekli')
    import firebase_admin
    firebase_admin.initialize_app(options={'projectId': project})
    store = FirestoreStore()
    started = datetime.now(timezone.utc).isoformat()
    try:
        collect_only=os.environ.get('AI_BATCH_COLLECT_ONLY')=='true'
        result = {'status':'batch_collection_only'} if collect_only else refresh(store)
        if os.environ.get('AI_REVIEW_ENABLED') == 'true':
            from .batch_pipeline import finish_batches, submit_candidates
            from .aggregator.collector import load_config
            result['document_review'] = finish_batches(store)
            if not collect_only:
                result['document_review_submission'] = submit_candidates(store,load_config())
    except Exception as exc:
        # Keep credentials, fetched content and exception messages out of logs.
        result = {'status': 'failed', 'error_kind': type(exc).__name__}
    result.update(started_at=started, finished_at=datetime.now(timezone.utc).isoformat())
    store.put('automation_runs', 'batch_collection_latest' if os.environ.get('AI_BATCH_COLLECT_ONLY')=='true' else 'source_refresh_latest', result)
    print(json.dumps(result, ensure_ascii=False))
    return 1 if result.get('status') == 'failed' or result.get('unhealthy') else 0


if __name__ == '__main__':
    raise SystemExit(main())
