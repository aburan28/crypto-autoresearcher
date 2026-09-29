#!/usr/bin/env python3
"""
REPLICATION OF THE FLAT-ARM INTERCEPT REGRESSION BY A SECOND IMPLEMENTATION.

The result under replication (DEC-20260823-ee9162 R3(g)): regressing the
measured envelope minimum on the FLAT-ARM INTERCEPT of the two-arm envelope fit
gives slope 0.8132, R^2 0.7732, n 13391.  It is the campaign's best positive
result and it currently rests on ONE reviewer's unarchived code with NO RUN
RECORD.  H-ECQ-0ed5c8 falsification: R^2 materially below 0.7232 on a second
implementation WITHDRAWS it.

TWO PASSES, AND WHAT IS AND IS NOT REUSED IS STATED FOR EACH.

  PASS 1 -- FULL POPULATION, n = 13391.  Reuses the flat-arm intercepts as
  recorded in the committed BATCH-541940 deliverable; the REGRESSION is
  recomputed here by an independent least-squares implementation that solves
  the normal equations in EXACT RATIONAL ARITHMETIC (fractions.Fraction) and
  converts to float only at the end -- no numpy, no reuse of measure.fit.
  What is reused: the per-family flat_arm_intercept and envelope values.
  What is not: any regression code.

  PASS 2 -- INDEPENDENT RE-DERIVATION ON A SAMPLE.  Recomputes, from the
  canonical tuple alone, the whole chain for a declared random sample: the
  73-value T-box heights, the lower envelope, a SEGMENTED two-arm fit written
  here from scratch, and the flat-arm intercept -- then regresses.  What is
  reused: the Mestre construction and the minimal-model height code, which two
  blind reviewers already re-derived and found correct, and which is the
  instrument rather than the result.  What is not: the envelope extraction, the
  breakpoint search, both arm fits and the regression.

usage: run008_intercept.py --out intercept_replication.json --run-id RUN-...
"""
import argparse
import json
import math
import os
import random
import sys
import time
from fractions import Fraction as F

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import constants
import measure
from runrec import Run

SEED = 20260823
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                    *([os.pardir] * 8)))
CENSUS = os.path.join(ROOT, 'coordination/goals/GOAL-ECQ-002/batches/'
                            'BATCH-541940/tasks/TASK-20260823-416e78/'
                            'tuple_envelope_scan.json')
REPORTED = {'slope': 0.8132, 'r_squared': 0.7732, 'n': 13391,
            'withdrawal_threshold_r_squared': 0.7232}


def ols_exact(xs, ys):
    """Simple least squares solved in EXACT rational arithmetic.

    Independent of measure.fit: the normal equations are formed and solved
    over Q, and the float conversion happens only on the way out.
    """
    n = len(xs)
    X = [F(x) for x in xs]          # EXACT binary fraction of the float:
                                    # denominators are powers of two, so the
                                    # running lcm is just the largest of them
    Y = [F(y) for y in ys]
    sx = sum(X)
    sy = sum(Y)
    sxx = sum(x * x for x in X)
    sxy = sum(x * y for x, y in zip(X, Y))
    den = n * sxx - sx * sx
    if den == 0:
        return None
    b = (n * sxy - sx * sy) / den
    a = (sy - b * sx) / n
    ybar = sy / F(n)
    sst = sum((y - ybar) ** 2 for y in Y)
    ssr = sum((y - (a + b * x)) ** 2 for x, y in zip(X, Y))
    return {'n': n, 'intercept': float(a), 'slope': float(b),
            'r_squared': (float(1 - ssr / sst) if sst else None),
            'sse': float(ssr), 'sst': float(sst),
            'solver': 'normal equations over Q (fractions.Fraction), '
                      'independent of measure.fit and of numpy'}


def envelope_and_two_arm(fam):
    """Envelope + segmented two-arm fit, written here from scratch."""
    pts = {}
    for t0 in measure.T_BOX:
        quart = fam.quartic_at(t0)
        ai = measure._jacobian_ai(quart)
        if measure._disc(ai) == 0:
            continue
        try:
            _c4, _c6, h, _mai = measure.minimal_invariants(ai)
        except BaseException:
            continue
        H = max(abs(t0.numerator), t0.denominator)
        x = math.log(H)
        if x not in pts or h < pts[x]:
            pts[x] = h
    env = sorted(pts.items())
    if len(env) < 6:
        return None
    xs = [p[0] for p in env]
    ys = [p[1] for p in env]
    best = None
    for k in range(3, len(env) - 2):
        f1 = ols_exact(xs[:k], ys[:k])
        f2 = ols_exact(xs[k:], ys[k:])
        if not f1 or not f2:
            continue
        sse = f1['sse'] + f2['sse']
        if best is None or sse < best[0]:
            best = (sse, k, f1, f2)
    if best is None:
        return None
    _sse, k, f1, f2 = best
    return {'flat_arm_intercept': f1['intercept'],
            'flat_arm_slope': f1['slope'],
            'steep_arm_slope': f2['slope'],
            'breakpoint_index': k,
            'envelope_min_naive_height': min(ys)}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--run-id', required=True)
    ap.add_argument('--sample-n', type=int, default=900)
    ap.add_argument('--time-budget', type=float, default=300.0)
    a = ap.parse_args(argv)

    cmd = ('python3 run008_intercept.py --out %s --run-id %s --sample-n %d '
           '--time-budget %g   (cwd: coordination/goals/GOAL-ECQ-002/batches/'
           'BATCH-8b08ef/tasks/TASK-20260823-827765/scripts)'
           % (a.out, a.run_id, a.sample_n, a.time_budget))

    with Run(a.run_id,
             'replication of the flat-arm intercept regression by a second '
             'implementation, with a run record',
             cmd,
             {'sample_n': a.sample_n, 'seed': SEED,
              'reported_result_under_replication': REPORTED,
              'randomness_sources': ['python random.Random(20260823) for the '
                                     'PASS 2 family sample; no other source']},
             wall_clock_budget_s=a.time_budget) as R:

        crec = constants.assert_frozen_constants()
        R.log('frozen-constant abort assertion exercised: all_match=%s'
              % crec['all_match'])

        with open(CENSUS) as fh:
            fams = json.load(fh)['families']
        R.log('census carries %d families' % len(fams))

        # -------- PASS 1: full population, independent regression --------
        rows = [(f['flat_arm_intercept'],
                 f['measured_envelope_min_naive_height'])
                for f in fams
                if f.get('flat_arm_intercept') is not None
                and f.get('measured_envelope_min_naive_height') is not None]
        p1 = ols_exact([r[0] for r in rows], [r[1] for r in rows])
        R.log('PASS 1 (n=%d, intercepts reused, regression independent): '
              'slope %.6f  R^2 %.6f' % (p1['n'], p1['slope'], p1['r_squared']))

        # a size-matched comparison the contract asks be kept beside it
        rows_c = [(f['log_content_P2'],
                   f['measured_envelope_min_naive_height'])
                  for f in fams if f.get('log_content_P2') is not None]
        pc = ols_exact([r[0] for r in rows_c], [r[1] for r in rows_c])
        R.log('  comparison: envelope on log content P2 -> slope %.6f R^2 %.6f'
              % (pc['slope'], pc['r_squared']))

        # -------- PASS 2: independent re-derivation on a sample ----------
        rng = random.Random(SEED)
        pool = [f for f in fams if f.get('tuple')]
        rng.shuffle(pool)
        t0 = time.time()
        redone, failed = [], []
        for f in pool:
            if time.time() - t0 > a.time_budget * 0.7 \
                    or len(redone) >= a.sample_n:
                break
            try:
                fam = measure.family_from_tuple(f['tuple'])
                e = envelope_and_two_arm(fam)
            except BaseException as ex:
                failed.append({'tuple': f['tuple'], 'status': 'refused',
                               'reason': '%s: %s' % (type(ex).__name__, ex)})
                continue
            if e is None:
                failed.append({'tuple': f['tuple'], 'status': 'refused',
                               'reason': 'fewer than 6 envelope points'})
                continue
            redone.append({'tuple': f['tuple'],
                           'rederived_flat_arm_intercept':
                               e['flat_arm_intercept'],
                           'rederived_envelope_min':
                               e['envelope_min_naive_height'],
                           'census_flat_arm_intercept':
                               f.get('flat_arm_intercept'),
                           'census_envelope_min':
                               f.get('measured_envelope_min_naive_height')})
        p2 = ols_exact([r['rederived_flat_arm_intercept'] for r in redone],
                       [r['rederived_envelope_min'] for r in redone]) \
            if len(redone) >= 3 else None
        agree = [abs(r['rederived_envelope_min'] - r['census_envelope_min'])
                 for r in redone if r['census_envelope_min'] is not None]
        R.log('PASS 2 (n=%d re-derived from the tuple alone, %d refused): '
              'slope %s  R^2 %s ; max |envelope difference| vs census %.3g'
              % (len(redone), len(failed),
                 ('%.6f' % p2['slope']) if p2 else None,
                 ('%.6f' % p2['r_squared']) if p2 else None,
                 max(agree) if agree else float('nan')))

        def verdict(p):
            if p is None:
                return 'NOT_RUN'
            if p['r_squared'] < REPORTED['withdrawal_threshold_r_squared']:
                return ('WITHDRAWN: R^2 materially below the declared '
                        'withdrawal threshold')
            if abs(p['r_squared'] - REPORTED['r_squared']) <= 0.05:
                return 'REPLICATES: R^2 within 0.05 of the reported value'
            return ('AMBIGUOUS: above the withdrawal threshold but more than '
                    '0.05 from the reported value')

        out = {
            'what': 'flat-arm intercept regression recomputed by a SECOND '
                    'implementation, with a run record',
            'run_id': a.run_id,
            'run_record': 'experiments/EXP-ECQ-0e0cbb/runs/' + a.run_id,
            'result_under_replication': REPORTED,
            'pass_1_full_population': {
                'n': p1['n'],
                'slope': p1['slope'],
                'r_squared': p1['r_squared'],
                'intercept': p1['intercept'],
                'code_reused': 'the per-family flat_arm_intercept and envelope '
                               'minimum as recorded in the committed '
                               'BATCH-541940 deliverable',
                'code_not_reused': 'the regression itself: normal equations '
                                   'solved in exact rational arithmetic here, '
                                   'sharing no code with measure.fit and using '
                                   'no numpy',
                'verdict': verdict(p1),
            },
            'pass_2_independent_rederivation_on_a_sample': {
                'n_generated': len(redone) + len(failed),
                'n_measured': len(redone),
                'n_refused': len(failed),
                'attrition_disclosed': True,
                'refusals': failed[:20],
                'slope': p2['slope'] if p2 else None,
                'r_squared': p2['r_squared'] if p2 else None,
                'max_abs_envelope_difference_against_census':
                    max(agree) if agree else None,
                'code_reused': 'the Mestre construction and the minimal-model '
                               'height code -- the instrument, already '
                               're-derived from scratch by two blind reviewers',
                'code_not_reused': 'envelope extraction, breakpoint search, '
                                   'both arm fits and the regression, all '
                                   'written independently in this file',
                'verdict': verdict(p2),
                'scope': 'a random sample of the same population, not the full '
                         '13391; reported as a sample and never as the full '
                         'population figure',
            },
            'comparison_envelope_on_log_content_P2': {
                'n': pc['n'], 'slope': pc['slope'],
                'r_squared': pc['r_squared'],
                'why_here': 'the statistic H-ECQ-8b600d named as the mechanism, '
                            'kept beside the intercept so the two are read '
                            'together rather than one at a time',
            },
            'certificate': {'kind': 'none',
                            'why': 'a regression; no discrete log and no '
                                   'factor-base relation is claimed'},
        }
        with open(a.out, 'w') as fh:
            json.dump(out, fh, indent=1)
        R.log('wrote %s' % a.out)
        R.result.update({k: v for k, v in out.items() if k != 'certificate'})
        R.result['certificate'] = out['certificate']
    return 0


if __name__ == '__main__':
    sys.exit(main())
