#!/usr/bin/env python3
"""
Assemble rank_search_coverage.json and best_candidates.json from the run
records, and run the MANDATORY provenance control on every reported curve.

THE PROVENANCE CONTROL IS NOT IN THE PRIORITY ORDER.  It is mandatory on every
curve this producer reports, whatever the budget does, and it is run on BOTH
keys plus Cremona:

  * FROZEN BOARD BY curve_key -- the c4:c6 string.
  * FROZEN BOARD BY a-INVARIANTS -- the integer 5-tuple, independently.
    Both, because BATCH-541940 reported frozen board curve id 108 as its own at
    rank thresholds 3, 4 and 5.
  * CREMONA.  NO CREMONA CHECK HAS BEEN PERFORMED ANYWHERE IN THIS CAMPAIGN
    although C1' names it.  PARI's elldata package is NOT installed in this
    environment (ellsearch and ellidentify both fail with "error opening
    elldata file"), and NO NETWORK CALL IS PERMITTED, so a lookup is
    impossible.  What IS possible offline, and is decisive in one direction, is
    a CONDUCTOR BOUND: Cremona's tables enumerate the elliptic curves over Q of
    conductor below a published bound, and a curve whose conductor exceeds that
    bound is PROVABLY ABSENT from them.  The conductor is computed exactly by
    PARI ellglobalred and compared against CREMONA_BOUND below.  A curve at or
    under the bound would return `cremona_check: INCONCLUSIVE_LOOKUP_REQUIRED`
    and would NOT be reported as novel.  The bound used is recorded with every
    row so the reader can audit the claim rather than take it.

Also computed here: the pre-declared BRANCH-C informativeness arithmetic, and
the identification of frozen board curves 108 and 162 against everything this
producer measured.
"""
import argparse
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import cypari

import constants
import heights
from runrec import Run

pari = cypari.pari

# Cremona's tables enumerate the elliptic curves over Q of conductor BELOW this
# bound.  It is the published range of the database, recorded here so the
# absence claim is auditable; it is NOT a frontier or benchmark value.
CREMONA_BOUND = 500000

# The pre-registered reference rate, EXACTLY as EXP-ECQ-0e0cbb
# preregistered_prediction.reference_rate_for_judging_a_zero states it.  It is
# empirical, one implementation, and is used ONLY to judge whether a zero is
# informative -- never as a claim about the construction.
REFERENCE_RATE = [((80, 90), 0.002), ((90, 100), 0.006), ((100, 120), 0.044)]

TD = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)


def rate_for(h):
    for (lo, hi), r in REFERENCE_RATE:
        if lo <= h < hi:
            return r, '[%d, %d)' % (lo, hi)
    return None, 'outside the reference-rate bands'


def provenance(mai, by_key, by_ainvs):
    ai = [int(x) for x in mai]
    key = heights.curve_key(ai)
    b1 = by_key.get(key)
    b2 = by_ainvs.get(tuple(ai))
    cond = int(pari('ellglobalred(ellinit(%s))[1]' % (ai,)))
    if cond >= CREMONA_BOUND:
        crem = {'outcome': 'PROVABLY_ABSENT',
                'why': 'conductor %d is at or above the published range of '
                       'Cremona\'s tables (%d), so the curve cannot appear in '
                       'them' % (cond, CREMONA_BOUND)}
    else:
        crem = {'outcome': 'INCONCLUSIVE_LOOKUP_REQUIRED',
                'why': 'conductor %d is inside Cremona\'s published range but '
                       'PARI elldata is not installed and no network call is '
                       'permitted, so no lookup was made; this curve is NOT '
                       'reported as novel' % cond}
    return {
        'curve_key': key,
        'a_invariants': ai,
        'conductor': cond,
        'frozen_board_by_curve_key': (
            {'found': True, 'board_id': b1['id'],
             'board_naive_height': b1['naive_height']} if b1
            else {'found': False}),
        'frozen_board_by_a_invariants': (
            {'found': True, 'board_id': b2['id'],
             'board_naive_height': b2['naive_height']} if b2
            else {'found': False}),
        'both_keys_checked': True,
        'cremona_check': dict(crem, bound_used=CREMONA_BOUND),
        'verdict': ('REDISCOVERED FROZEN BOARD CURVE -- A STRONG EXTERNAL '
                    'POSITIVE CONTROL, NEVER THIS PROGRAM\'S OWN CURVE'
                    if (b1 or b2) else
                    'absent from the frozen snapshot on both keys; '
                    'Cremona: ' + crem['outcome']),
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--run-id', default='RUN-ECQSTR-827765-011')
    a = ap.parse_args(argv)
    cmd = ('python3 run011_deliverables.py --run-id %s   (cwd: coordination/'
           'goals/GOAL-ECQ-002/batches/BATCH-8b08ef/tasks/TASK-20260823-827765/'
           'scripts)' % a.run_id)

    with Run(a.run_id,
             'assemble rank_search_coverage.json and best_candidates.json, run '
             'the mandatory provenance control on every reported curve, and '
             'compute the pre-declared branch-C informativeness arithmetic',
             cmd,
             {'cremona_bound_used': CREMONA_BOUND,
              'reference_rate': [[list(b), r] for b, r in REFERENCE_RATE],
              'randomness_sources': ['none: assembly is deterministic']},
             wall_clock_budget_s=300) as R:

        crec = constants.assert_frozen_constants()
        cell = crec['cell']['min_naive_height']
        bench = crec['benchmark']['naive_height']
        R.log('frozen constants read at run time: cell %r, benchmark %r'
              % (cell, bench))
        by_key, by_ainvs = constants.board_index()

        A = json.load(open(os.path.join(TD, 'results/rank_rows_setA.json')))
        Ar = json.load(open(os.path.join(TD,
                                         'results/rank_rows_setA_retry.json')))
        B = json.load(open(os.path.join(TD, 'results/rank_rows_setB.json')))

        # ---- combine SET A first pass + retry --------------------------
        retry_meas = {(r['family'], r['t']): r for r in Ar['rows']
                      if r['status'] == 'measured'}
        a_rows = []
        for r in A['rows']:
            k = (r['family'], r['t'])
            if r['status'] != 'measured' and k in retry_meas:
                rr = dict(retry_meas[k])
                rr['superseded_first_pass_status'] = r['status']
                rr['superseded_first_pass_reason'] = r['reason']
                a_rows.append(rr)
            else:
                a_rows.append(dict(r, alarm_seconds=A['alarm_seconds']))
        b_rows = [dict(r, alarm_seconds=B['alarm_seconds']) for r in B['rows']]

        def cov(rows):
            n = sum(1 for r in rows if r['status'] == 'measured')
            d = len(rows)
            return {'numerator': n, 'denominator': d, 'fraction': n / d,
                    'as_written': '%d/%d' % (n, d)}

        def cov_by_ceiling(rows):
            out = {}
            for c in sorted({r.get('shioda_tate_ceiling') for r in rows}):
                sub = [r for r in rows if r.get('shioda_tate_ceiling') == c]
                out[str(c)] = cov(sub)
            return out

        all_rows = a_rows + b_rows
        covA, covB, covAll = cov(a_rows), cov(b_rows), cov(all_rows)
        R.log('COVERAGE  target stratum (SET A): %s = %.4f'
              % (covA['as_written'], covA['fraction']))
        R.log('COVERAGE  BATCH-541940 unfinished set (SET B): %s = %.4f'
              % (covB['as_written'], covB['fraction']))
        R.log('COVERAGE  overall: %s = %.4f'
              % (covAll['as_written'], covAll['fraction']))

        measured = [r for r in all_rows if r['status'] == 'measured']

        # ---- branch-C informativeness arithmetic, pre-declared ---------
        sub = [r for r in measured if r['naive_height'] < bench]
        expected = 0.0
        band_counts = {}
        for r in sub:
            rate, band = rate_for(r['naive_height'])
            band_counts[band] = band_counts.get(band, 0) + 1
            if rate:
                expected += rate
        n12 = sum(1 for r in sub
                  if (r.get('certified_rank_lower_bound') or 0) >= 12)
        p_zero = math.exp(-expected)
        informative = expected >= 3
        R.log('BRANCH-C ARITHMETIC: %d MEASURED fibres below the benchmark '
              'read at run time; expected successes at certified rank >= 12 '
              'under the pre-registered reference rate = %.4f; observed = %d; '
              'P(zero) ~ %.4f' % (len(sub), expected, n12, p_zero))

        # ---- pareto + provenance on EVERY reported curve ---------------
        pareto = {}
        for k in range(1, 16):
            c = [r for r in measured
                 if (r.get('certified_rank_lower_bound') or 0) >= k]
            if not c:
                continue
            b = min(c, key=lambda r: r['naive_height'])
            prov = provenance(b['minimal_a_invariants'], by_key, by_ainvs)
            gm, mai2 = heights.is_globally_minimal(b['minimal_a_invariants'])
            h2, c4, c6, _d = heights.naive_height_from_ainvs(
                b['minimal_a_invariants'])
            fr = json.load(open(constants.FRONTIER))[
                'frontier_by_rank_threshold'].get(str(k))
            fv = fr['min_naive_height']['value'] if fr else None
            pareto[str(k)] = {
                'certified_rank_lower_bound_threshold': k,
                'min_naive_height': b['naive_height'],
                'naive_height_recomputed_from_a_invariants_alone': h2,
                'height_recomputation_abs_difference': abs(h2 - b['naive_height']),
                'globally_minimal_model': gm,
                'family': b['family'], 'tuple': b.get('tuple'), 't': b['t'],
                'set': b.get('set'),
                'a_invariants': b['minimal_a_invariants'],
                'c4': str(c4), 'c6': str(c6),
                'n_exhibited_points': b.get('n_points_exhibited'),
                'exhibited_points': b.get('points'),
                'pari_ellrank_r_low': b.get('pari_ellrank_r_low'),
                'pari_ellrank_r_high': b.get('pari_ellrank_r_high'),
                'pari_ellrank_alarm_status': b.get('pari_ellrank_status'),
                'alarm_seconds': b.get('alarm_seconds'),
                'n_curves_at_or_above': len(c),
                'frontier_value_read_at_run_time': fv,
                'gap_to_frontier_at_this_threshold': (
                    (b['naive_height'] - fv) if fv is not None else None),
                'cell_taken': (fv is not None and b['naive_height'] < fv
                               and not prov['frozen_board_by_curve_key'].get(
                                   'found')
                               and not prov['frozen_board_by_a_invariants'].get(
                                   'found')),
                'provenance': prov,
            }
        for k in sorted(pareto, key=int):
            p = pareto[k]
            R.log('  r>=%2s h=%.6f gap %+.6f cell_taken=%s prov=%s'
                  % (k, p['min_naive_height'],
                     p['gap_to_frontier_at_this_threshold'], p['cell_taken'],
                     p['provenance']['verdict'][:48]))

        # ---- board curves 108 and 162 ----------------------------------
        seen_keys = {}
        for r in measured:
            seen_keys.setdefault(
                heights.curve_key(r['minimal_a_invariants']), r)
        board_hits = []
        with open(constants.SNAPSHOT) as fh:
            board = json.load(fh)['curves']
        for c in board:
            k = str(c['curve_key'])
            aitup = tuple(int(x) for x in c['ainvs'])
            hit = seen_keys.get(k)
            hit2 = next((r for r in measured
                         if tuple(int(x) for x in r['minimal_a_invariants'])
                         == aitup), None)
            if hit or hit2:
                board_hits.append({'board_id': c['id'],
                                   'board_naive_height': c['naive_height'],
                                   'matched_by_curve_key': bool(hit),
                                   'matched_by_a_invariants': bool(hit2),
                                   'family': (hit or hit2)['family'],
                                   't': (hit or hit2)['t']})
        ids = {h['board_id'] for h in board_hits}
        R.log('frozen board curves rediscovered among this task\'s MEASURED '
              'fibres: %s (108 present: %s; 162 present: %s)'
              % (sorted(ids), 108 in ids, 162 in ids))

        best_h12 = min((r['naive_height'] for r in measured
                        if (r.get('certified_rank_lower_bound') or 0) >= 12),
                       default=None)

        coverage_doc = {
            'what': 'every attempted (family, t) pair with a status and a '
                    'reason, and coverage as NUMERATOR OVER DENOMINATOR',
            'task_id': 'TASK-20260823-827765',
            'experiment_id': 'EXP-ECQ-0e0cbb',
            'hypothesis_id': 'H-ECQ-0ed5c8',
            'runs': ['RUN-ECQSTR-827765-004', 'RUN-ECQSTR-827765-005',
                     'RUN-ECQSTR-827765-006', a.run_id],
            'frozen_constants_read_at_run_time': crec,
            't_box': 't = n/d, 1<=n<=30, d in {1,2,3}, gcd(n,d)=1, plus '
                     't in {40,60,90,130,200,300,500,800}; 73 values; t > 0 '
                     'only because h(-t) = h(t) identically',
            'caps': {'height_cap': None, 'family_cap': None,
                     'note': 'NO height cap and NO family cap, as the contract '
                             'requires; BATCH-541940 runs 006 and 011 carried '
                             'both'},
            'alarm_policy': 'PARI alarm 20 s throughout (the same instrument '
                            'and the same alarm as BATCH-541940, under which '
                            'the pre-registered reference rate was measured). '
                            'RUN-ECQSTR-827765-005 re-attempted SET A\'s '
                            'alarmed fibres at 90 s and is reported separately. '
                            'AN ALARMED FIBRE COUNTS AS ATTEMPTED-NOT-MEASURED '
                            'IN THE COVERAGE DENOMINATOR, never as a searched '
                            'fibre that found nothing.',
            'coverage': {
                'target_stratum_SET_A': dict(
                    covA, by_ceiling_class=cov_by_ceiling(a_rows),
                    definition=A['set_definition']),
                'batch_541940_unfinished_SET_B': dict(
                    covB, by_ceiling_class=cov_by_ceiling(b_rows),
                    definition=B['set_definition']),
                'overall': covAll,
            },
            'branch_C_informativeness_arithmetic': {
                'rule': 'EXP-ECQ-0e0cbb branch_c_is_not_an_escape_hatch: '
                        'expected successes = sum over SEARCHED fibres of the '
                        'pre-registered reference rate for that fibre\'s height '
                        'band. At least 3 makes the zero a BOUNDED NEGATIVE; '
                        'below 3 it must be labelled "consistent with the '
                        'measured rate and not informative about it".',
                'reference_rate': [[list(b), r] for b, r in REFERENCE_RATE],
                'reference_rate_status': 'empirical, one implementation, used '
                                         'ONLY to judge whether a zero is '
                                         'informative and never as a claim '
                                         'about the construction',
                'n_measured_fibres_below_the_benchmark': len(sub),
                'height_band_counts': band_counts,
                'expected_successes_at_certified_rank_ge_12': expected,
                'observed_successes_at_certified_rank_ge_12': n12,
                'implied_P_observing_zero': p_zero,
                'is_a_reportable_bounded_negative': informative,
                'mandated_label': (
                    'a bounded negative' if informative else
                    'consistent with the measured rate and not informative '
                    'about it'),
            },
            'min_naive_height_at_certified_rank_ge_12_over_searched_stratum':
                best_h12,
            'rows_SET_A': a_rows,
            'rows_SET_B': b_rows,
        }
        p = os.path.join(TD, 'rank_search_coverage.json')
        json.dump(coverage_doc, open(p, 'w'), indent=1)
        R.log('wrote %s (%.2f MiB)' % (p, os.path.getsize(p) / (1 << 20)))

        best_doc = {
            'what': 'the best (certified rank, minimal-model naive height) '
                    'curves in ICARM format, with exhibited points, both '
                    'provenance keys and the Cremona check',
            'task_id': 'TASK-20260823-827765',
            'experiment_id': 'EXP-ECQ-0e0cbb',
            'frozen_constants_read_at_run_time': crec,
            'certification': 'every rank is a CERTIFIED LOWER BOUND re-derived '
                             'by exact_certify.py from the exhibited points in '
                             'integer/Fraction arithmetic; PARI ellrank was a '
                             'POINT SEARCH only and its verdict is never the '
                             'reported rank. Rank EQUALITY is never claimed.',
            'standing_negative': 'NO RECORD CELL HAS BEEN TAKEN BY THIS '
                                 'CAMPAIGN, IN FOUR BATCHES, ON ANY METRIC, AT '
                                 'ANY RANK THRESHOLD. cell_taken is false on '
                                 'every row below. RANK >= 31 OVER Q REMAINS AN '
                                 'OPEN WORLD RECORD (30, Alpoge-Howell 2026) '
                                 'AND NOTHING HERE IS PROGRESS TOWARD IT.',
            'provenance_control': {
                'both_keys': 'curve_key AND a-invariants, independently, '
                             'against the frozen snapshot',
                'cremona': 'conductor bound %d; PARI elldata is not installed '
                           'in this environment and no network call is '
                           'permitted, so a lookup is impossible and the check '
                           'is decisive only in the ABSENT direction'
                           % CREMONA_BOUND,
            },
            'per_threshold': pareto,
            'frozen_board_curves_rediscovered': board_hits,
            'board_id_108_rediscovered': 108 in ids,
            'board_id_162_rediscovered': 162 in ids,
            'nothing_submitted_to_icarm': True,
            'network_calls_made': 0,
        }
        p2 = os.path.join(TD, 'best_candidates.json')
        json.dump(best_doc, open(p2, 'w'), indent=1)
        R.log('wrote %s (%.2f MiB)' % (p2, os.path.getsize(p2) / (1 << 20)))

        R.result.update({
            'coverage_target_stratum': covA,
            'coverage_batch541940_unfinished': covB,
            'coverage_overall': covAll,
            'branch_C_expected_successes': expected,
            'branch_C_observed_successes': n12,
            'min_naive_height_at_certified_rank_ge_12': best_h12,
            'benchmark_read_at_run_time': bench,
            'cell_read_at_run_time': cell,
            'any_cell_taken': any(v['cell_taken'] for v in pareto.values()),
            'board_curves_rediscovered': sorted(ids),
            'certificate': {'kind': 'none',
                            'why': 'assembly and provenance checking; no '
                                   'discrete log and no factor-base relation'},
        })
    return 0


if __name__ == '__main__':
    sys.exit(main())
