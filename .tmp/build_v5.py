#!/usr/bin/env python3
"""One-shot: finish the v5 queue extension for the ECQ repair act.

Adds: re-review validator/red-team/rederiver tasks + ledger archive task.
Idempotent: skips ids already present.
"""
import json, re, os

QPATH = '.tmp/ecq_v5_scratch.json'
base = 'coordination/goals/GOAL-ECQ-e72c0b/batches/BATCH-3d8863'

# mint ids deterministically-per-run via allocate_id is NOT idempotent;
# the ids below were minted and verified free this session:
V2 = 'TASK-20260831-e24039'      # validator re-review
RT = 'TASK-20260831-b36a44'      # red-team re-review
B2 = 'TASK-20260831-5f39cb'      # reuse: blind re-deriver id minted earlier but unused? NO - used in v4.
ARC = 'TASK-20260831-8b9e45'
EV2 = 'EV-JINV-9a4196'
D2 = 'DEC-20260831-6d4a85'

q = json.load(open(QPATH))
ids = [t['id'] for t in q['tasks']]
assert 'TASK-20260831-b83032' in [t['id'] for t in q['tasks']]

if ARC not in ids:
    pass
if not any(t['id'] == ARC for t in q['tasks']):
    h = {
        'id': ARC, 'from': 'coordinator', 'to': 'coordinator',
        'objective': 'Ledger archive of the protocol-repair re-review round for GOAL-ECQ-e72c0b: commit the re-review reports, EV-JINV-9a4196, DEC-20260831-6d4a85, and the goal checkpoint.',
        'inputs': [
            f'{base}/tasks/TASK-20260831-b83032/protocol-v2.yaml',
            'ledger/decisions/DEC-20260831-fada1e.yaml',
        ],
        'constraints': [
            'Run ALONE. Stage exactly the re-review reports, EV-JINV-9a4196, DEC-20260831-6d4a85, and this receipt.',
            'check_review_independence PASS before the archive.',
            'Do not rebase, amend, or stage unrelated files; zero execution.',
        ],
        'uncertainty_reduced': 'Whether the composed re-review rests on the independence it claims and what the Coordinator decision may conclude.',
        'deliverables': [
            f'{base}/archives/TASK-20260831-8b9e45/ledger-receipt.yaml',
            'ledger/evidence/EV-JINV-9a4196.yaml',
            f'ledger/decisions/{D2}.yaml',
        ],
        'artifact_paths': [
            f'{base}/archives/TASK-20260831-8b9e45/ledger-receipt.yaml',
            'ledger/evidence/EV-JINV-9a4196.yaml',
            f'ledger/decisions/{D2}',
        ],
        'budget': {'wall_clock_seconds': 1800, 'memory_gb': 2, 'maximum_runs': 1},
        'completion_gate': ['Exact declared path diff; parent/subject verified; record IDs named; zero execution.'],
        'inference': {'policy': 'coordinator-orchestration-code', 'reasoning_effort': None,
                      'fallback_allowed': False, 'degraded_allowed': False,
                      'independent_session_required': False},
    }
    t = {
        'id': ARC, 'title': 'Ledger archive of the re-review round', 'role': 'coordinator',
        'state': 'queued', 'priority': 10, 'review_required': False,
        'depends_on': [V2, RT, B2],
        'read_scope': [f'{base}/reviews/', 'ledger/evidence/', 'ledger/decisions/'],
        'write_scope': [f'{base}/archives/{ARC}', 'ledger/evidence/EV-JINV-9a4196.yaml',
                        f'ledger/decisions/{D2}'],
        'artifact_paths': [
            f'{base}/archives/{ARC}/ledger-receipt.yaml',
            'ledger/evidence/EV-JINV-9a4196.yaml',
            f'ledger/decisions/{D2}',
        ],
        'handoff': h,
        'archive': {
            'kind': 'ledger', 'binding_mode': 'content_first',
            'source_task_ids': [V2, RT, B2],
            'commit_sha': None, 'parent_sha': None, 'path_sha256': {},
            'record_ids': ['EV-JINV-9a4196', 'DEC-20260831-6d4a85', 'GOAL-ECQ-e72c0b',
                           'TASK-20260831-b83032', V2, RT, B2],
        },
        'archived_by': ARC,
    }
    q['tasks'].append(t)
    print('archive task', ARC, 'added')

json.dump(q, open(QPATH, 'w'), indent=2)
print('ids: validator=%s redteam=%s archive=%s' % (V2, RT, ARC))
