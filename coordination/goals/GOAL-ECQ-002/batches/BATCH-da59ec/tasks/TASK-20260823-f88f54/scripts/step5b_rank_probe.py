#!/usr/bin/env python3
"""STEP 5 (SECONDARY) -- bounded rank PROBE on NAGAO-1994 fibres.

NOT a sieve: the admissible height box is empty at all three pre-declared
targets (step 3/4), so no candidate is eligible for submission and no ordering
step is run.  This probe exists only to inform review_plan prior P3 ("certified
rank >= 12 at small t") and falsification clause 2 of H-ECQ-a609f8.

DISCIPLINE, fixed before the numbers are read:
  * the only rank number reported is a CERTIFIED LOWER BOUND from exact_certify
    (exact, stdlib-only), from points exhibited by PARI ellrank;
  * a shortfall (fewer than 12 independent points found) is a SEARCH outcome
    and is NEVER reported as rank < 12;
  * an ellrank alarm is an INFRASTRUCTURE outcome.
"""
import json, os, sys
PIPE = ('/home/user/crypto-autoresearcher/coordination/goals/GOAL-ECQ-002/batches/'
        'BATCH-f2341e/tasks/TASK-20260823-01d3d9/pipeline')
sys.path.insert(0, PIPE)
from fractions import Fraction as F
import pipeline
from families import Family

def main(family_json, out_json, ts, tl):
    fam = Family.load(family_json)
    rows = []
    for t in ts:
        rec = pipeline.evaluate_candidate(fam, {'t': F(t)}, rank_time_limit=tl,
                                          want_record=True)
        cert = rec.get('certificate') or {}
        row = {'t': str(t),
               'certified_rank_lower_bound': cert.get('certified_rank_lower_bound'),
               'n_points_exhibited': cert.get('n_points_non_torsion'),
               'certificate_valid': cert.get('independence', {}).get('method'),
               'ellrank_status': (rec.get('pari_search') or {}).get('timed_out'),
               'infrastructure_note': rec.get('infrastructure_note'),
               'pari_search_r_low': (rec.get('pari_search') or {}).get('pari_r_low'),
               'pari_search_r_high': (rec.get('pari_search') or {}).get('pari_r_high'),
               'pari_search_seconds': (rec.get('pari_search') or {}).get('seconds'),
               'submission_record_not_submittable': True,
               'submission_record': rec.get('submission_record'),
               'naive_height': (rec.get('invariants') or {}).get('naive_height'),
               'curve_key': (rec.get('invariants') or {}).get('curve_key')}
        rows.append(row)
        print(row)
    out = {'step': '5b', 'kind': 'bounded rank probe (secondary; box already empty)',
           'rank_time_limit_seconds': tl,
           'discipline': 'certified lower bound only; a shortfall is a SEARCH outcome, '
                         'never rank < 12; an alarm is an INFRASTRUCTURE outcome',
           'supersedes_run': 'RUN-ECQNAG-f88f54-008 (implementation_error: want_record=False skipped the point search entirely)',
           'rows': rows}
    json.dump(out, open(out_json, 'w'), indent=1)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[4:], int(sys.argv[3]))
