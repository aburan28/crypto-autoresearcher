"""Descriptive record trails; references never imply validation or promotion."""
from collections import Counter


def experiment_trail(index, experiment):
    seeds = {experiment.record_id, *(r['id'] for r in experiment.runs)}
    related = set()
    # Directed inbound citations only. Never fan out through shared hypotheses/goals.
    frontier = seeds
    for _ in range(3):
        next_ids = set()
        for record_id in frontier:
            for ref in index.backlinks.get(record_id, ()):
                record = index.records.get(ref)
                if record and (record.kind in ('EV', 'DEC', 'CORR') or ref.startswith('KN-FIND-')):
                    if ref not in related:
                        next_ids.add(ref)
        related.update(next_ids)
        frontier = next_ids
    records = [index.records[r] for r in sorted(related)]
    events = [{'id': experiment.record_id, 'kind': 'EXP', 'status': experiment.status or 'unknown',
               'date': experiment.dated or None, 'path': experiment.path,
               'basis': 'contract declaration', 'via': []}]
    for run in experiment.runs:
        events.append({'id': run['id'], 'kind': 'RUN', 'status': run['status'] or 'unknown',
                       'date': run.get('finished') or run.get('started') or None,
                       'path': run.get('manifest_path') or run.get('path'),
                       'basis': 'run manifest declaration', 'via': [experiment.record_id]})
    for record in records:
        events.append({'id': record.record_id, 'kind': record.kind, 'status': record.status or 'unknown',
                       'date': record.date or None, 'path': record.path,
                       'basis': 'record declaration; citation is not endorsement',
                       'via': sorted(record.refs & (seeds | related))})
    events.sort(key=lambda r: (r['date'] is None, r['date'] or '', r['id']))
    gaps = []
    if not experiment.contract:
        gaps.append('missing_contract')
    if not experiment.runs:
        gaps.append('no_runs_recorded')
    if any(r['status'] in ('no-manifest', 'unreadable', 'unstated', '') for r in experiment.runs):
        gaps.append('missing_or_unreadable_manifest')
    if any(r['status'] in ('running', 'incomplete', 'timeout', 'failed', 'failed_infrastructure', 'invalid') for r in experiment.runs):
        gaps.append('incomplete_or_failed_run')
    if experiment.runs and not any(r.kind == 'EV' for r in records):
        gaps.append('no_linked_evidence')
    if experiment.runs and not any(r.kind == 'DEC' for r in records):
        gaps.append('no_linked_decision')
    return {'id': experiment.record_id, 'title': experiment.title, 'path': experiment.path,
            'declared_status': experiment.status or 'unknown', 'gaps': gaps,
            'archive_state': 'declared_archived' if experiment.status == 'archived' else 'unknown',
            'events': events}


def payload(index):
    experiments = [experiment_trail(index, e) for e in index.experiments]
    return {'schema': 1, 'experiments': experiments,
            'gap_counts': dict(sorted(Counter(g for e in experiments for g in e['gaps']).items())),
            'needs_follow_up': sum(bool(e['gaps']) for e in experiments),
            'coverage': 'Indexed experiment contracts, run manifests and up to three inbound citation steps. '
                        'Dates and statuses are source declarations. Archive receipts and coordination queues are not ingested; '
                        'a missing link is a coverage gap, not proof that review or archival did not happen.'}
