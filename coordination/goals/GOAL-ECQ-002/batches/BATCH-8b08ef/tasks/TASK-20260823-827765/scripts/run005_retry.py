#!/usr/bin/env python3
"""
BOUNDED RETRY of the fibres a previous rank-search run left
ATTEMPTED-NOT-MEASURED because the 20 s PARI alarm fired.

This is EXP-ECQ-0e0cbb priority (2) -- full coverage of the target stratum --
and not a rerun-until-favourable: it re-attempts EVERY alarmed pair of the
input run, in the input run's own order, and every attempt is persisted with
its status and its reason whatever the outcome.  The previous run record stays
exactly as it is; this run supplements it and both are reported.

THE INSTRUMENT CHANGES AND THAT IS DISCLOSED.  The alarm is raised from 20 s to
--alarm seconds here.  The 20 s figure is the one the pre-registered reference
rate table was measured under, so the RATE COMPARISON continues to use the 20 s
pass only; this pass is used for COVERAGE and for the certified-rank-versus-
height curve, where a longer point search can only add points and never removes
one.  Rows carry `alarm_seconds` so the two passes are never conflated.

usage: run005_retry.py --in rows.json --out rows_retry.json --run-id RUN-...
                       --alarm 60 --time-budget 400
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
import ranksearch
from runrec import Run


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--in', dest='inp', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--run-id', required=True)
    ap.add_argument('--alarm', type=int, default=60)
    ap.add_argument('--time-budget', type=float, default=400.0)
    a = ap.parse_args(argv)

    with open(a.inp) as fh:
        prev = json.load(fh)
    todo = [r for r in prev['rows'] if r['status'] == 'attempted_not_measured']

    cmd = ('python3 run005_retry.py --in %s --out %s --run-id %s --alarm %d '
           '--time-budget %g   (cwd: coordination/goals/GOAL-ECQ-002/batches/'
           'BATCH-8b08ef/tasks/TASK-20260823-827765/scripts)'
           % (a.inp, a.out, a.run_id, a.alarm, a.time_budget))

    with Run(a.run_id,
             'bounded retry of the ATTEMPTED-NOT-MEASURED fibres of %s at a '
             'longer PARI alarm, to close coverage of SET %s'
             % (prev.get('run_id'), prev.get('set')),
             cmd,
             {'input_run': prev.get('run_id'), 'set': prev.get('set'),
              'alarm_seconds': a.alarm,
              'previous_alarm_seconds': prev.get('alarm_seconds'),
              'n_pairs_to_retry': len(todo),
              'randomness_sources': ['none: deterministic retry in the input '
                                     'run\'s own order']},
             wall_clock_budget_s=a.time_budget) as R:

        crec = constants.assert_frozen_constants()
        R.log('frozen-constant abort assertion exercised: all_match=%s'
              % crec['all_match'])
        R.log('retrying %d attempted-not-measured pairs of %s at alarm %ds '
              '(was %ss)' % (len(todo), prev.get('run_id'), a.alarm,
                             prev.get('alarm_seconds')))

        rows = []
        budget_hit = False
        t0 = time.time()
        for i, w in enumerate(todo):
            if R.budget_reached():
                budget_hit = True
                R.warn('WALL CLOCK REACHED after %d of %d retries; the rest '
                       'stay ATTEMPTED-NOT-MEASURED. INFRASTRUCTURE OUTCOME '
                       'that BOUNDS COVERAGE.' % (i, len(todo)))
                for w2 in todo[i:]:
                    rows.append(dict(w2, alarm_seconds=a.alarm,
                                     status='attempted_not_measured',
                                     reason='wall_clock_stop_before_retry'))
                break
            fam = measure.family_from_tuple(w['tuple'], name=w['family'])
            try:
                row = ranksearch.search_fibre(fam, F(w['t']), alarm=a.alarm)
            except BaseException as e:
                row = {'t': w['t'], 'status': 'attempted_not_measured',
                       'reason': 'exception: %s: %s' % (type(e).__name__, e)}
            row.update({k: w[k] for k in ('set', 'family', 'tuple',
                                          'shioda_tate_ceiling',
                                          'log_content_P2') if k in w})
            row['alarm_seconds'] = a.alarm
            row['retry_of'] = prev.get('run_id')
            rows.append(row)
            R.log('  %s t=%s -> %s (%s)  [%.0fs]'
                  % (w['family'], w['t'], row['status'],
                     row.get('reason', '')[:60], time.time() - t0))

        gained = [r for r in rows if r['status'] == 'measured']
        R.log('retry gained %d newly MEASURED fibres of %d retried'
              % (len(gained), len(rows)))

        # combined coverage over the input run's denominator
        prev_meas = sum(1 for r in prev['rows'] if r['status'] == 'measured')
        den = len(prev['rows'])
        combined = {'numerator': prev_meas + len(gained), 'denominator': den,
                    'fraction': (prev_meas + len(gained)) / den,
                    'as_written': '%d/%d' % (prev_meas + len(gained), den),
                    'from_first_pass': prev_meas,
                    'from_retry_pass': len(gained)}
        R.log('COMBINED COVERAGE SET %s: %s = %.4f'
              % (prev.get('set'), combined['as_written'],
                 combined['fraction']))

        doc = {'retry_of': prev.get('run_id'), 'set': prev.get('set'),
               'run_id': a.run_id, 'alarm_seconds': a.alarm,
               'combined_coverage': combined,
               'time_budget_reached': budget_hit, 'rows': rows}
        with open(a.out, 'w') as fh:
            json.dump(doc, fh, indent=1)
        R.log('wrote %s' % a.out)

        R.result.update({
            'set': prev.get('set'), 'retry_of': prev.get('run_id'),
            'n_retried': len(rows), 'n_newly_measured': len(gained),
            'combined_coverage': combined,
            'time_budget_reached': budget_hit,
            'rows_file': a.out,
            'certificate': {'kind': 'none',
                            'why': 'rank lower bounds from exhibited points; '
                                   'no discrete log and no factor-base '
                                   'relation is claimed'},
        })
        if budget_hit:
            R.deviations.append('wall clock reached during retry; remaining '
                                'pairs stay attempted_not_measured. '
                                'INFRASTRUCTURE OUTCOME.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
