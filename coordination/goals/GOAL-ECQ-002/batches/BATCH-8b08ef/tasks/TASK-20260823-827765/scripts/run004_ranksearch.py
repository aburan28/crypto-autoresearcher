#!/usr/bin/env python3
"""
RANK-SEARCH RUN.  --set A is the target stratum; --set B is the BATCH-541940
unfinished set.  Both write per-(family, t) rows with a status and a reason,
and coverage is reported as NUMERATOR OVER DENOMINATOR overall and per ceiling
class.

usage: run004_ranksearch.py --set A --run-id RUN-... --out rows_A.json
"""
import argparse
import json
import math
import os
import sys
import time
from fractions import Fraction as F

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import constants
import measure
import ranksearch
from runrec import Run

TARGET_CEILING = 13
TARGET_LOG_P2 = 6.0
SCRATCH = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir,
                       'results')


def load_enumeration():
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir,
                     'stratum_enumeration.json')
    with open(p) as fh:
        return json.load(fh)


def build_set_A():
    enum = load_enumeration()
    fams = enum['target_stratum_families_full_detail']
    fams.sort(key=lambda f: f['log_content_P2'])
    work = []
    for f in fams:
        for t in ranksearch.t_box_strings():
            work.append({'set': 'A', 'family': 'MESTRE-%s'
                         % ','.join(str(x) for x in f['canonical_tuple']),
                         'tuple': f['canonical_tuple'], 't': t,
                         'shioda_tate_ceiling':
                             f['shioda_tate_ceiling_from_own_fibre_configuration'],
                         'log_content_P2': f['log_content_P2']})
    return work, {'n_families': len(fams),
                  'n_t_values': len(ranksearch.t_box_strings()),
                  'order': 'log P2 ascending, then t ascending'}


def build_set_B():
    census = ranksearch.prior_census()
    hi = [f for f in census
          if (f.get('shioda_tate_ceiling_own_fibre_configuration') or 0)
          >= ranksearch.PRIOR_CEILING]
    done = ranksearch.prior_searched_pairs()
    tb = ranksearch.t_box_strings()
    hi.sort(key=lambda f: (-f['shioda_tate_ceiling_own_fibre_configuration'],
                           tuple(f['tuple'])))
    work, n_done = [], 0
    for f in hi:
        d = done.get(f['family'], set())
        for t in tb:
            if t in d:
                n_done += 1
                continue
            work.append({'set': 'B', 'family': f['family'],
                         'tuple': f['tuple'], 't': t,
                         'shioda_tate_ceiling':
                             f['shioda_tate_ceiling_own_fibre_configuration'],
                         'log_content_P2': f['log_content_P2']})
    meta = {
        'n_families_ceiling_ge_%d_in_prior_census' % ranksearch.PRIOR_CEILING:
            len(hi),
        'n_t_values': len(tb),
        'denominator_family_times_tbox': len(hi) * len(tb),
        'n_pairs_already_searched_in_BATCH_541940': n_done,
        'n_pairs_unsearched_at_the_start_of_this_run': len(work),
        'n_distinct_families_with_any_prior_search': len(
            [f for f in hi if f['family'] in done]),
        'order': 'ceiling descending, then canonical tuple lexicographic, '
                 'then t ascending -- fixed in advance and independent of '
                 'height, so the searched subset is not selected on the '
                 'quantity under study',
        'reviewer_figure_disclosure':
            'DEC-20260823-ee9162 R4(f) records 46 load-bearing families and '
            '2114 unsearched fibres at 37.0 percent coverage. That exact '
            'partition could not be reproduced from the committed BATCH-541940 '
            'artifacts by this producer; SET B is the reproducible SUPERSET '
            'described in ranksearch.py and contains any such 46-family set. '
            'The discrepancy is reported, not resolved by assumption.',
    }
    return work, meta


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--set', dest='which', choices=('A', 'B'), required=True)
    ap.add_argument('--run-id', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--time-budget', type=float, default=600.0)
    a = ap.parse_args(argv)

    cmd = ('python3 run004_ranksearch.py --set %s --run-id %s --out %s '
           '--time-budget %g   (cwd: coordination/goals/GOAL-ECQ-002/batches/'
           'BATCH-8b08ef/tasks/TASK-20260823-827765/scripts)'
           % (a.which, a.run_id, a.out, a.time_budget))

    work, meta = (build_set_A() if a.which == 'A' else build_set_B())

    with Run(a.run_id,
             'rank search with EXACT certification over SET %s, full 73-value '
             'T-box, no height cap and no family cap' % a.which,
             cmd,
             {'set': a.which, 'alarm_seconds': ranksearch.ALARM_SECONDS,
              'height_cap': None, 'family_cap': None,
              't_box': measure.T_BOX_DESC,
              'n_t_values': len(measure.T_BOX),
              'denominator_pairs': len(work),
              'set_definition': meta,
              'randomness_sources': ['none: the search order is deterministic '
                                     'and declared in advance']},
             wall_clock_budget_s=a.time_budget) as R:

        crec = constants.assert_frozen_constants()
        R.log('frozen-constant abort assertion exercised: all_match=%s'
              % crec['all_match'])
        R.log('SET %s: %d (family, t) pairs in the denominator, alarm %ds, '
              'NO height cap, NO family cap'
              % (a.which, len(work), ranksearch.ALARM_SECONDS))

        rows = []
        fam_cache = {}
        n_alarm = 0
        budget_hit = False
        t0 = time.time()
        for i, w in enumerate(work):
            if R.budget_reached():
                budget_hit = True
                R.warn('WALL CLOCK REACHED after %d of %d pairs; the remaining '
                       '%d pairs are ATTEMPTED-NOT-MEASURED. INFRASTRUCTURE '
                       'OUTCOME: it BOUNDS COVERAGE and is never negative '
                       'mathematical evidence.'
                       % (i, len(work), len(work) - i))
                for w2 in work[i:]:
                    rows.append(dict(w2, status='attempted_not_measured',
                                     reason='wall_clock_stop_before_this_pair'))
                break
            key = tuple(w['tuple'])
            if key not in fam_cache:
                fam_cache = {key: measure.family_from_tuple(w['tuple'],
                                                            name=w['family'])}
            fam = fam_cache[key]
            try:
                row = ranksearch.search_fibre(fam, F(w['t']))
            except BaseException as e:
                row = {'t': w['t'], 'status': 'attempted_not_measured',
                       'reason': 'exception: %s: %s' % (type(e).__name__, e)}
            row.update({k: w[k] for k in ('set', 'family', 'tuple',
                                          'shioda_tate_ceiling',
                                          'log_content_P2')})
            if 'alarm' in row.get('reason', ''):
                n_alarm += 1
            rows.append(row)
            if (i + 1) % 25 == 0:
                R.log('  ... %d/%d pairs (%.0fs, %d alarms)'
                      % (i + 1, len(work), time.time() - t0, n_alarm))

        measured = [r for r in rows if r['status'] == 'measured']
        anm = [r for r in rows if r['status'] == 'attempted_not_measured']
        assert len(measured) + len(anm) == len(rows) == len(work), \
            'attempted/measured arithmetic gap in the rank search'

        def cov(sub_rows, sub_work):
            n = sum(1 for r in sub_rows if r['status'] == 'measured')
            d = len(sub_work)
            return {'numerator': n, 'denominator': d,
                    'fraction': (n / d) if d else None,
                    'as_written': '%d/%d' % (n, d)}

        by_ceiling = {}
        for c in sorted({w['shioda_tate_ceiling'] for w in work}):
            sw = [w for w in work if w['shioda_tate_ceiling'] == c]
            sr = [r for r in rows if r['shioda_tate_ceiling'] == c]
            by_ceiling[str(c)] = cov(sr, sw)

        overall = cov(rows, work)
        R.log('COVERAGE SET %s: %s = %.4f' % (a.which, overall['as_written'],
                                              overall['fraction']))
        for c, v in by_ceiling.items():
            R.log('  ceiling %s: %s = %.4f' % (c, v['as_written'],
                                               v['fraction']))
        R.log('%d PARI alarms (infrastructure outcomes, counted as '
              'attempted-not-measured)' % n_alarm)

        best = {}
        for k in range(1, 16):
            c = [r for r in measured
                 if (r.get('certified_rank_lower_bound') or 0) >= k]
            if c:
                b = min(c, key=lambda r: r['naive_height'])
                best[str(k)] = {'min_naive_height': b['naive_height'],
                                'family': b['family'], 't': b['t'],
                                'curve_key': b['curve_key'],
                                'n_curves_at_or_above': len(c)}
        for k in sorted(best, key=int):
            R.log('  certified rank >= %2s : min naive height %.6f (%s, t=%s, '
                  'n=%d)' % (k, best[k]['min_naive_height'], best[k]['family'],
                             best[k]['t'], best[k]['n_curves_at_or_above']))

        max_rank = max((r.get('certified_rank_lower_bound') or 0)
                       for r in measured) if measured else None
        R.log('max certified rank lower bound over MEASURED fibres: %s'
              % max_rank)

        doc = {'set': a.which, 'set_definition': meta,
               'run_id': a.run_id,
               'alarm_seconds': ranksearch.ALARM_SECONDS,
               'height_cap': None, 'family_cap': None,
               'coverage_overall': overall,
               'coverage_by_ceiling_class': by_ceiling,
               'n_pari_alarms': n_alarm,
               'time_budget_reached': budget_hit,
               'certified_rank_vs_height_pareto': best,
               'max_certified_rank_over_measured_fibres': max_rank,
               'rows': rows}
        os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
        with open(a.out, 'w') as fh:
            json.dump(doc, fh, indent=1)
        R.log('wrote %s (%.2f MiB)'
              % (a.out, os.path.getsize(a.out) / (1 << 20)))

        R.result.update({
            'set': a.which,
            'coverage_overall': overall,
            'coverage_by_ceiling_class': by_ceiling,
            'n_pairs_attempted': len(rows),
            'n_pairs_measured': len(measured),
            'n_pairs_attempted_not_measured': len(anm),
            'n_pari_alarms': n_alarm,
            'max_certified_rank_over_measured_fibres': max_rank,
            'certified_rank_vs_height_pareto': best,
            'time_budget_reached': budget_hit,
            'rows_file': a.out,
            'certificate': {'kind': 'none',
                            'why': 'rank lower bounds from exhibited points; '
                                   'no discrete log and no factor-base '
                                   'relation is claimed. The exact-arithmetic '
                                   'point verification is recorded per fibre.'},
        })
        if budget_hit:
            R.deviations.append(
                'wall clock reached; remaining pairs persisted as '
                'attempted_not_measured. INFRASTRUCTURE OUTCOME that BOUNDS '
                'COVERAGE and is never negative mathematical evidence.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
