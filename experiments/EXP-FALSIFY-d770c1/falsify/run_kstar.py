"""F-10 probe: exact-rational recomputation of the BATCH-121 K* crossover tables.

    python3 experiments/EXP-FALSIFY-d770c1/falsify/run_kstar.py

KN-FIND-ac28ed carries confidence: proved, evidence_level: theorem, and asserts
that the as-committed BATCH-121 tables contain exactly two errors, both IEEE
float ceil artifacts:

    K*(standard)  2001 -> 2000
    m=4 cell       126 -> 125
    K*(BKK)=96     correct as committed

It is a correction record, so the interesting failure mode is not that its two
corrections are wrong but that its audit is INCOMPLETE -- a third bad cell it
did not catch. This probe recomputes all 18 cells in exact rational arithmetic
and, as a control, reproduces what IEEE double arithmetic would have produced,
so the stated cause can be checked rather than taken on trust.

    K*(std) = ceil( s / (1 - t) )
    K*(BKK) = ceil( s*beta / (1 - t*beta) ),   beta = 2/(m+1)

Formulas are NOT in KN-FIND-c7d31e, which the finding cites for them and which
contains zero occurrences of "K*". They are in
coordination/goals/GOAL-ECDLP-001/batches/BATCH-121/tasks/TASK-20260805-005/
closure_and_multi_target.md sections B.2 and B.3.
"""

import json
import math
import os
import subprocess
import sys
from datetime import datetime, timezone
from fractions import Fraction

# (s, t, K*(std), K*(BKK), ratio) exactly as committed in BATCH-121 B.4
COMMITTED = {
    3: [(50, '0.3', 72, 30), (50, '0.7', 167, 39), (100, '0.3', 143, 59),
        (100, '0.7', 334, 77), (200, '0.5', 400, 134), (200, '0.9', 2001, 182)],
    4: [(50, '0.3', 72, 23), (50, '0.7', 167, 28), (100, '0.3', 143, 46),
        (100, '0.7', 334, 56), (200, '0.5', 400, 100), (200, '0.9', 2001, 126)],
    5: [(50, '0.3', 72, 19), (50, '0.7', 167, 22), (100, '0.3', 143, 38),
        (100, '0.7', 334, 44), (200, '0.5', 400, 80), (200, '0.9', 2001, 96)],
}
CLAIMED_CORRECTIONS = {'K*(standard) 2001 -> 2000', 'm=4 cell 126 -> 125'}


def ceil_exact(fr):
    return -((-fr.numerator) // fr.denominator)


def main():
    print('F-10  exact-rational recomputation of the BATCH-121 K* tables')
    print('      target: KN-FIND-ac28ed (confidence: proved, evidence_level: theorem)\n')
    print(f"{'m':>2}{'s':>5}{'t':>6}{'Kstd cmt':>10}{'Kstd exact':>12}"
          f"{'Kbkk cmt':>10}{'Kbkk exact':>12}{'float std':>11}{'float bkk':>11}")
    rows, disagreements = [], []
    for m, cells in COMMITTED.items():
        beta = Fraction(2, m + 1)
        for s, ts, kstd_c, kbkk_c in cells:
            t = Fraction(ts)
            kstd = ceil_exact(Fraction(s) / (1 - t))
            kbkk = ceil_exact(Fraction(s) * beta / (1 - t * beta))
            # control: what IEEE double arithmetic yields, to test the stated cause
            fb = float(beta)
            fstd = math.ceil(s / (1 - float(t)))
            fbkk = math.ceil(s * fb / (1 - float(t) * fb))
            row = {'m': m, 's': s, 't': ts,
                   'kstd_committed': kstd_c, 'kstd_exact': kstd,
                   'kbkk_committed': kbkk_c, 'kbkk_exact': kbkk,
                   'kstd_float': fstd, 'kbkk_float': fbkk}
            rows.append(row)
            if kstd != kstd_c or kbkk != kbkk_c:
                disagreements.append(row)
            print(f"{m:>2}{s:>5}{ts:>6}{kstd_c:>10}{kstd:>12}{kbkk_c:>10}{kbkk:>12}"
                  f"{fstd:>11}{fbkk:>11}")

    distinct = set()
    for d in disagreements:
        if d['kstd_exact'] != d['kstd_committed']:
            distinct.add(f"K*(standard) {d['kstd_committed']} -> {d['kstd_exact']}")
        if d['kbkk_exact'] != d['kbkk_committed']:
            distinct.add(f"m={d['m']} cell {d['kbkk_committed']} -> {d['kbkk_exact']}")

    print(f"\n  cells disagreeing with as-committed : {len(disagreements)}")
    print(f"  DISTINCT corrections found          : {len(distinct)}")
    for c in sorted(distinct):
        print(f"      {c}")
    print(f"  KN-FIND-ac28ed claims               : {len(CLAIMED_CORRECTIONS)}")
    for c in sorted(CLAIMED_CORRECTIONS):
        print(f"      {c}")

    complete = distinct == CLAIMED_CORRECTIONS
    print(f"\n  audit complete and exact: {complete}")

    # cause control: float reproduces the committed value at every disagreement
    cause_ok = all(d['kstd_float'] == d['kstd_committed']
                   and d['kbkk_float'] == d['kbkk_committed'] for d in disagreements)
    print(f"  stated cause (IEEE ceil artifact) reproduces every committed value: {cause_ok}")
    exact_t = [r for r in rows if r['t'] == '0.5']
    print(f"  control: t=0.5 is binary-exact and all {len(exact_t)} such cells were "
          f"committed correctly ({', '.join(str(r['kbkk_exact']) for r in exact_t)});")
    print(f"           the artifact strikes only at t=0.9, where 0.9 and 0.1 are not "
          f"representable.")

    out = {'experiment_id': 'EXP-FALSIFY-d770c1',
           'run_id': 'RUN-FALSIFY-d770c1-004',
           'probe': 'kstar_exact_recomputation_f10',
           'target_finding': 'KN-FIND-ac28ed',
           'cells': rows,
           'distinct_corrections_found': sorted(distinct),
           'corrections_claimed': sorted(CLAIMED_CORRECTIONS),
           'audit_complete_and_exact': complete,
           'stated_cause_reproduced': cause_ok,
           'citation_defect': ('KN-FIND-ac28ed cites KN-FIND-c7d31e for the K* '
                               'formulas; that record contains zero occurrences of '
                               '"K*". The formulas are in BATCH-121 '
                               'TASK-20260805-005 sections B.2/B.3.'),
           'timestamp_utc': datetime.now(timezone.utc).isoformat(),
           'git_commit': subprocess.run(['git', 'rev-parse', 'HEAD'],
                                        capture_output=True, text=True).stdout.strip()}
    dest = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        'runs', 'RUN-FALSIFY-d770c1-004', 'raw-result.json')
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, 'w') as fh:
        json.dump(out, fh, indent=2, sort_keys=True)
    print(f'\nresults written to {dest}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
