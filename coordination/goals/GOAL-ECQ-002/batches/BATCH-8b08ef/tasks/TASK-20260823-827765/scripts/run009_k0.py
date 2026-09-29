#!/usr/bin/env python3
"""
THE k = 0 PROVES-TOO-MUCH OBJECT, run on its own.

RUN-ECQSTR-827765-007 reported this control as NOT_RUN: its candidate loop
required all three root pairs of a treatment tuple to satisfy |a - b| != 2 and
drew only from the first six shuffled tuples, and every one of those six failed
the guard.  THAT IS A DEFECT IN THAT RUN AND IT IS RECORDED AS ONE, not
overwritten -- RUN-ECQSTR-827765-007 stands as written and this run supplies
the control it missed.

THE OBJECT.  q a product of three IRREDUCIBLE QUADRATICS: zero RATIONAL roots,
so zero rational sections, but every conjugate root pair is Galois-STABLE.
PASS CONDITION, STATED BEFORE THE OBJECT IS RUN: it must NOT come out rank 0.
Any argument of the form "no rational sections implies no rational rank" has to
FAIL here.  If this run reported rank 0 on the k = 0 rung, that argument would
have proved too much and would be wrong somewhere.

WHAT IS NOT ESTABLISHED HERE.  The trace map P + P^sigma of a Galois-conjugate
section pair is NOT constructed.  Certified rational points of infinite order
are exhibited; their provenance as such traces is not established by this run
and is not asserted by it.
"""
import argparse
import json
import os
import sys
import time
from fractions import Fraction as F

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import constants
import measure
from run007_controls import certify_jacobian_at, galois_record
from runrec import Run


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--run-id', required=True)
    ap.add_argument('--n-want', type=int, default=6)
    ap.add_argument('--alarm', type=int, default=20)
    ap.add_argument('--time-budget', type=float, default=200.0)
    a = ap.parse_args(argv)

    cmd = ('python3 run009_k0.py --out %s --run-id %s --n-want %d --alarm %d '
           '--time-budget %g   (cwd: coordination/goals/GOAL-ECQ-002/batches/'
           'BATCH-8b08ef/tasks/TASK-20260823-827765/scripts)'
           % (a.out, a.run_id, a.n_want, a.alarm, a.time_budget))

    with Run(a.run_id,
             'the k = 0 proves-too-much object, run on its own after '
             'RUN-ECQSTR-827765-007 reported it NOT_RUN',
             cmd,
             {'n_want': a.n_want, 'alarm_seconds': a.alarm,
              'supersedes_nothing': 'RUN-ECQSTR-827765-007 stands as written; '
                                    'this run supplies the control it missed',
              'randomness_sources': ['none: candidates are taken in the '
                                     'enumeration\'s own order']},
             wall_clock_budget_s=a.time_budget) as R:

        crec = constants.assert_frozen_constants()
        R.log('frozen-constant abort assertion exercised: all_match=%s'
              % crec['all_match'])
        R.log('PASS CONDITION, STATED IN ADVANCE: the k = 0 rung must NOT come '
              'out rank 0')

        enum_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 os.pardir, 'stratum_enumeration.json')
        with open(enum_path) as fh:
            enum = json.load(fh)
        cands = [d['canonical_tuple']
                 for d in enum['retained_families_full_detail']]
        cands.sort()

        rows = []
        n_skipped = 0
        t0 = time.time()
        for tup in cands:
            if len([r for r in rows if r['status'] == 'measured']) >= a.n_want \
                    or R.budget_reached():
                break
            e = sorted(int(x) for x in tup)
            pairs = [(e[0], e[1]), (e[2], e[3]), (e[4], e[5])]
            if any(abs(x - y) == 2 for x, y in pairs):
                n_skipped += 1
                rows.append({'tuple': tup, 'status': 'refused',
                             'reason': 'a root pair has |a - b| = 2, so the '
                                       'perturbed quadratic would stay '
                                       'reducible and the rung would not be '
                                       'k = 0'})
                continue
            try:
                fam = measure.family_from_tuple(tup, perturb_pairs=3)
            except BaseException as ex:
                rows.append({'tuple': tup, 'status': 'refused',
                             'reason': '%s: %s' % (type(ex).__name__, ex)})
                continue
            if fam.deg_x_r != 4:
                rows.append({'tuple': tup, 'status': 'refused',
                             'reason': 'deg_x_r = %d, not a genus-1 quartic'
                                       % fam.deg_x_r})
                continue
            m = measure.measure(fam, want_surface=False)
            if m.get('status') != 'measured':
                rows.append({'tuple': tup, 'status': 'refused',
                             'reason': m.get('status')})
                continue
            c = certify_jacobian_at(fam, F(m['envelope_argmin_t']), a.alarm)
            g = galois_record(fam.q)
            rows.append({
                'tuple': tup, 'status': 'measured',
                'reason': 'k = 0 rung built and measured at its envelope argmin',
                'q_ascending': [str(x) for x in fam.q],
                'galois': g,
                'n_rational_roots': len(fam.rational_roots),
                'n_rational_sections': len(fam.sections),
                'every_conjugate_pair_is_galois_stable':
                    (not g['irreducible_over_Q']),
                'envelope_min_naive_height':
                    m['measured_envelope_min_naive_height'],
                'envelope_argmin_t': m['envelope_argmin_t'],
                'certified_at_argmin': c,
            })
            R.log('  k=0 rung from %s: %d rational sections, q factor degrees '
                  '%s, env %.3f, certified rank %s'
                  % (tup, len(fam.sections), g.get('factor_degrees'),
                     m['measured_envelope_min_naive_height'],
                     (c or {}).get('certified_rank_lower_bound')))

        ok = [r for r in rows if r['status'] == 'measured']
        n_pos = sum(1 for r in ok
                    if ((r['certified_at_argmin'] or {}).get(
                        'certified_rank_lower_bound') or 0) > 0)
        outcome = 'PASS' if (ok and n_pos > 0) else ('FAIL' if ok else 'NOT_RUN')
        R.log('k = 0 proves-too-much: %d of %d measured rungs carry certified '
              'rank >= 1 -> %s' % (n_pos, len(ok), outcome))

        out = {
            'object': 'the BATCH-541940 k = 0 rung: q a product of three '
                      'irreducible quadratics, 0 RATIONAL roots and therefore '
                      '0 rational sections, but every conjugate root pair '
                      'Galois-STABLE',
            'pass_condition_stated_in_advance':
                'it must NOT come out rank 0; any "no rational sections '
                'implies no rational rank" argument must FAIL on it',
            'run_id': a.run_id,
            'generated_against_measured': {
                'n_candidates_visited': len(rows),
                'n_measured': len(ok),
                'n_refused': len(rows) - len(ok),
                'n_refused_for_the_pair_distance_guard': n_skipped,
                'attrition_disclosed': True,
            },
            'n_with_certified_rank_at_least_1': n_pos,
            'outcome': outcome,
            'trace_map_disclosure':
                'THE TRACE MAP P + P^sigma IS NOT CONSTRUCTED HERE. Certified '
                'rational points of infinite order are exhibited; their '
                'provenance as traces of Galois-conjugate section pairs is not '
                'established by this run and is not asserted by it.',
            'defect_in_RUN_ECQSTR_827765_007':
                'that run reported this control NOT_RUN because its candidate '
                'loop drew from only six shuffled tuples and every one failed '
                'the |a - b| = 2 guard. The run record stands as written; this '
                'run supplies the control.',
            'rows': rows,
            'certificate': {'kind': 'none',
                            'why': 'a control; no discrete log and no '
                                   'factor-base relation is claimed'},
        }
        with open(a.out, 'w') as fh:
            json.dump(out, fh, indent=1)
        R.log('wrote %s' % a.out)
        R.result.update({'outcome': outcome, 'n_measured': len(ok),
                         'n_with_certified_rank_at_least_1': n_pos,
                         'deliverable': a.out,
                         'certificate': out['certificate']})
    return 0


if __name__ == '__main__':
    sys.exit(main())
