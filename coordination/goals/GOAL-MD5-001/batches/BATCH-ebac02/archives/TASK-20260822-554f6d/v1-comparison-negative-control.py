#!/usr/bin/env python3
"""Negative control for VAL-20260822-7f5ed3's comparison (compare_v1.py).

The V1 completion pass reported 7600/7600 exact agreement between the
archived production runs and a cold re-run. A comparison that cannot
disagree proves nothing, so this control points the SAME comparison logic
at two archived runs of the SAME seeds but DIFFERENT objects
(primary-md4 vs null-md4, 100 shared seeds, 17 common per-seed fields each)
and REQUIRES mismatches. If the control reports zero mismatches, the
comparison is vacuous and the V1 PASSED verdict must be withdrawn.

Run by the coordinator (driving session) as part of the TASK-20260822-554f6d
close; disclosed as coordinator-performed, not reviewer-performed.
"""
import json

base = ('coordination/goals/GOAL-MD5-001/batches/BATCH-ebac02/tasks/'
        'TASK-20260822-767bb1/runs')
a = json.load(open(f'{base}/RUN-MDFIVE-b6-primary-md4-prod/raw-result.json'))
b = json.load(open(f'{base}/RUN-MDFIVE-b6-null-md4-prod/raw-result.json'))

assert [s['seed'] for s in a['per_seed']] == [s['seed'] for s in b['per_seed']]

FWD = ['distinct_fwd_32bit', 'distinct_fwd_12bit']
BWD = ['distinct_bwd_32bit', 'distinct_bwd_12bit']

compared = matched = 0
mismatch_examples = []
for sa, sb in zip(a['per_seed'], b['per_seed']):
    for ra, rb in zip(sa['direction_A_rows'], sb['direction_A_rows']):
        for f in FWD:
            compared += 1
            if ra[f] == rb[f]:
                matched += 1
            elif len(mismatch_examples) < 5:
                mismatch_examples.append(
                    (sa['seed'], 'A.' + f, ra[f], rb[f]))
    for ra, rb in zip(sa['direction_B_rows'], sb['direction_B_rows']):
        for f in BWD:
            compared += 1
            if ra[f] == rb[f]:
                matched += 1
            elif len(mismatch_examples) < 10:
                mismatch_examples.append(
                    (sa['seed'], 'B.' + f, ra[f], rb[f]))
    ca = sa.get('ctl_po5_k1_k2_6', {}).get('raw_candidate_count')
    cb = sb.get('ctl_po5_k1_k2_6', {}).get('raw_candidate_count')
    compared += 1
    if ca == cb:
        matched += 1
    elif len(mismatch_examples) < 15:
        mismatch_examples.append((sa['seed'], 'ctl_po5.raw', ca, cb))

result = {
    'control': 'v1_comparison_negative_control',
    'compared': compared,
    'matched': matched,
    'mismatches': compared - matched,
    'requirement': 'mismatches > 0 (a different object must disagree)',
    'status': 'PASS' if compared - matched > 0 else 'FAIL',
    'mismatch_examples': mismatch_examples,
}
out = ('coordination/goals/GOAL-MD5-001/batches/BATCH-ebac02/archives/'
       'TASK-20260822-554f6d/v1-comparison-negative-control-result.json')
json.dump(result, open(out, 'w'), indent=1)
print(json.dumps({k: result[k] for k in
                  ('compared', 'matched', 'mismatches', 'status')}))
