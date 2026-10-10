"""Stable review categories; missing evidence is never a negative eligibility claim."""

CRITICAL_FIELDS = {'country', 'target', 'deadline', 'openness'}


def add_conflict(draft, field):
    fields = set(draft.get('ai_conflict_fields') or [])
    fields.add(field)
    draft['ai_conflict_fields'] = sorted(fields)
    draft['ai_conflict'] = True  # Existing administration clients remain compatible.


def critical_conflict(draft):
    fields = draft.get('ai_conflict_fields')
    if fields is None:
        return bool(draft.get('ai_conflict'))  # Legacy unspecified conflict needs review.
    if not isinstance(fields, list) or any(f not in CRITICAL_FIELDS | {'personal_conditions'} for f in fields):
        return True
    return bool(CRITICAL_FIELDS.intersection(fields))


def decision_category(status):
    if status in ('eligible', 'published', 'already_published'):
        return 'verified_suitable'
    if status == 'out_of_scope':
        return 'explicitly_out_of_scope'
    if status == 'closed':
        return 'closed_or_past'
    if status in ('document_unavailable', 'missing_input'):
        return 'technical_document_error'
    return 'critical_evidence_missing'


def personal_conditions_pending(draft):
    return any(c.get('result') == 'bilinmiyor'
               for path in draft.get('paths', []) for c in path.get('conditions', []))
