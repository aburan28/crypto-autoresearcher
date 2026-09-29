#!/usr/bin/env python3
import json, subprocess, hashlib
base = 'coordination/goals/GOAL-ECQ-e72c0b/batches/BATCH-3d8863'
V5 = f'{base}/dispatch_queue.v5.json'
V6 = f'{base}/dispatch_queue.v6.json'
q = json.load(open(V5))

# ensure prior states all completed
for t in q['tasks']:
    if t.get('state') != 'completed':
        t['state'] = 'completed'

P = 'TASK-20260903-941021'   # producer
S = 'TASK-20260903-e4ff4c'   # snapshot archive
V = 'TASK-20260903-5b0033'   # approval validator
L = 'TASK-20260903-db7e7d'   # ledger archive

def hl(**kw):
    h = dict(
        id=kw['id'], from_='coordinator', to=kw['to'],
        objective=kw['obj'], uncertainty_reduced=kw['unc'],
        inputs=kw.get('inputs', []), constraints=kw.get('constraints', []),
        deliverables=kw['dels'], artifact_paths=kw['aps'],
        budget=kw.get('budget', {'wall_clock_seconds': 7200, 'memory_gb': 2, 'maximum_runs': 1}),
        completion_gate=kw.get('gate', []),
        archived_by=kw['archived_by'],
        inference=kw.get('inference', {}))
    return h

V_REP = f'{base}/reviews/{V}/report.yaml'

P_HANDOFF = json.loads(open('ledger/handoffs/TASK-20260903-941021.yaml').read().replace('from: coordinator', 'from_: coordinator')) if False else None

import yaml
p_yaml = yaml.safe_load(open('ledger/handoffs/TASK-20260903-941021.yaml'))['handoff']

tasks_to_add = [
  # producer
  {'id': P, 'title': 'Third scoped design-touch: protocol-v3 (R2a/R2b/R2c)', 'role': 'idea-generator',
   'state': 'queued', 'priority': 90, 'review_required': True, 'depends_on': ['TASK-20260831-8b9e45'],
   'read_scope': [f'{base}/tasks/TASK-20260831-b83032/protocol-v2.yaml', 'ledger/decisions/DEC-20260831-6d4a85.yaml', f'{base}/reviews/', 'coordination/goals/GOAL-ECQ-e72c0b/baseline/icarm_curve_302_20260824.json', 'AGENTS.md'],
   'write_scope': [f'{base}/tasks/{P}'],
   'artifact_paths': [f'{base}/tasks/{P}/protocol-v3.yaml', f'{base}/tasks/{P}/task-report.yaml'],
   'handoff': p_yaml, 'archived_by': S},
  # snapshot archive
  {'id': S, 'title': 'Snapshot protocol-v3', 'role': 'coordinator', 'state': 'queued',
   'priority': 10, 'review_required': False, 'depends_on': [P],
   'read_scope': [f'{base}/tasks/{P}/'], 'write_scope': [f'{base}/archives/{S}'],
   'artifact_paths': [f'{base}/archives/{S}/snapshot-receipt.yaml'],
   'handoff': hl(id=S, to='coordinator', obj='Content-first snapshot of the three design-touch artifacts before the approval review reads them.',
       unc='Whether the three artifacts are durably archived and verified before review.', dels=[f'{base}/tasks/{P}/protocol-v3.yaml', f'{base}/tasks/{P}/task-report.yaml', f'{base}/archives/{S}/snapshot-receipt.yaml'], aps=[f'{base}/archives/{S}/snapshot-receipt.yaml'], archived_by=L,
       budget={'wall_clock_seconds': 1800, 'memory_gb': 2, 'maximum_runs': 1},
       constraints=['Run ALONE after the producer completes; stage exactly the two producer artifacts plus the receipt; bind the then-current HEAD as parent.'], gate=['Exact 3-path diff; subject and parent verified; zero execution.'], inference={'policy': 'coordinator-orchestration-code', 'reasoning_effort': None, 'fallback_allowed': False, 'degraded_allowed': False, 'independent_session_required': False}),
   'archive': {'kind': 'snapshot', 'binding_mode': 'content_first', 'source_task_ids': [P],
       'commit_sha': None, 'parent_sha': None, 'path_sha256': {}, 'record_ids': [P, S]},
   'archived_by': S},
  # approval validator
  {'id': V, 'title': 'Approval-focused re-review of R2a/R2b/R2c', 'role': 'validator', 'state': 'queued',
   'priority': 90, 'review_required': False, 'depends_on': [P, S],
   'read_scope': [f'{base}/tasks/{P}/', 'ledger/decisions/DEC-20260831-6d4a85.yaml', f'{base}/review-plan-v3.yaml', 'coordination/goals/GOAL-ECQ-e72c0b/baseline/icarm_curve_302_20260824.json'],
   'write_scope': [f'{base}/reviews/{V}'], 'artifact_paths': [V_REP],
   'handoff': hl(id=V, to='validator', obj='Approval-focused re-review: do R2a/R2b/R2c each close in protocol-v3, with no regression of the corroborated rule.',
       unc='Whether the three residuals are closed and the design is approval-ready, reviewed adversarially.',
       inputs=[f'{base}/tasks/{P}/protocol-v3.yaml', f'{base}/tasks/{P}/task-report.yaml', f'{base}/review-plan-v3.yaml', 'ledger/decisions/DEC-20260831-6d4a85.yaml'],
       constraints=['Own ONLY R2a/R2b/R2c per review-plan-v3.yaml; no whole-claim verdict.', 'Blindness: read no other reviewer report; attest files read.', 'ZERO-EXECUTION REVIEW - analytic only.', 'Record requested policy review-adversarial and the model that answered; disclose the effort dial.'],
       dels=[V_REP], aps=[V_REP], archived_by=L,
       budget={'wall_clock_seconds': 7200, 'memory_gb': 2, 'maximum_runs': 1},
       gate=['CONCUR or DISSENT per residual R2a/R2b/R2c with worked evidence; files-read attestation.'],
       inference={'policy': 'review-adversarial', 'reasoning_effort': 'xhigh', 'fallback_allowed': False, 'degraded_allowed': False, 'independent_session_required': True}),
   'archived_by': L},
  # ledger archive
  {'id': L, 'title': 'Ledger archive of the approval round', 'role': 'coordinator', 'state': 'queued',
   'priority': 10, 'review_required': False, 'depends_on': [V],
   'read_scope': [f'{base}/reviews/', 'ledger/evidence/', 'ledger/decisions/'],
   'write_scope': [f'{base}/archives/{L}', 'ledger/evidence/EV-JINV-66978b.yaml', 'ledger/decisions/DEC-20260903-0ab045.yaml'],
   'artifact_paths': [f'{base}/archives/{L}/ledger-receipt.yaml', 'ledger/evidence/EV-JINV-66978b.yaml', 'ledger/decisions/DEC-20260903-0ab045.yaml'],
   'handoff': hl(id=L, to='coordinator', obj='Ledger archive of the approval re-review: commit the validator report, EV-JINV-66978b, DEC-20260903-0ab045, and the goal checkpoint.',
       unc='Whether the composed approval round rests on verified independence and what the terminal decision concludes.',
       inputs=[f'{base}/review-plan-v3.yaml', V_REP], dels=[f'{base}/archives/{L}/ledger-receipt.yaml', 'ledger/evidence/EV-JINV-66978b.yaml', 'ledger/decisions/DEC-20260903-0ab045.yaml'], aps=[f'{base}/archives/{L}/ledger-receipt.yaml', 'ledger/evidence/EV-JINV-66978b.yaml', 'ledger/decisions/DEC-20260903-0ab045.yaml'], archived_by=L,
       budget={'wall_clock_seconds': 1800, 'memory_gb': 2, 'maximum_runs': 1},
       constraints=['Run ALONE; stage exactly the review report, EV-JINV-66978b, DEC-20260903-0ab045, and the receipt; post-commit verify.'], gate=['Exact declared path diff; parent/subject verified; record IDs named; zero execution.'],
       inference={'policy': 'coordinator-orchestration-code', 'reasoning_effort': None, 'fallback_allowed': False, 'degraded_allowed': False, 'independent_session_required': False}),
   'archive': {'kind': 'ledger', 'binding_mode': 'content_first', 'source_task_ids': [V],
       'commit_sha': None, 'parent_sha': None, 'path_sha256': {}, 'record_ids': ['EV-JINV-66978b', 'DEC-20260903-0ab045', 'GOAL-ECQ-e72c0b', V, L]},
   'archived_by': L},
]

# fix flow-keys the queue schema wants (depends_on as list, no 'from_' key)
for t in tasks_to_add:
    q['tasks'].append(t)
q['design_touch3_note'] = 'Third scoped design-touch (R2a/R2b/R2c per DEC-20260831-6d4a85) + approval-focused single-validator re-review + ledger archive. review-plan-v3.yaml to be pre-recorded before the validator runs.'

json.dump(q, open(V6, 'w'), indent=2)
json.dump(q, open('.tmp/ecq_v6_scratch.json', 'w'), indent=2)
print('v6 written with', len(q['tasks']), 'tasks')
