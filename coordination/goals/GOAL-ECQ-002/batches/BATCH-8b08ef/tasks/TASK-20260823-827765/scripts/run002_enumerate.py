#!/usr/bin/env python3
"""
RUN-ECQSTR-827765-002 -- PRE-FILTERED ENUMERATION over the declared box.

THE BOX, ITS ORDER AND ITS CANONICALISATION ARE DECLARED HERE, IN CODE, BEFORE
ANY COUNT IS READ (EXP-ECQ-0e0cbb step_2_enumeration_box):

  B1  EXHAUSTIVE.  Every canonical primitive integer 6-tuple of spread
      5 <= m <= 80.  This is ENLARGED beyond the spread <= 74 exhaustive census
      of BATCH-541940.  Enumeration order: m ascending, then the middle
      4-subset in lexicographic order.
  B2  SAMPLED.  Spread drawn uniformly in [81, 3000], N_TESTED tuples,
      random.Random(20260823).  This is the only source of randomness.

  Canonicalisation (reused unchanged from BATCH-541940 tuple_scan_v2.py):
  translate min to 0, divide out the gcd, and reflect a -> max - a whenever
  that is lexicographically smaller.

THE ORDER OF OPERATIONS IS THE POINT.  For each admissible tuple:
  (1) THE PRE-FILTER, first, timed -- one squarefreeness test on the degree-20
      finite discriminant.  No height is evaluated, nothing is ordered by
      Mestre-Nagao, and no rank is searched before it.
  (2) the FULL fibre census, computed for EVERY enumerated family and not only
      for survivors, so that CTL-PREFILTER-SOUNDNESS is checked over the whole
      exhaustive box rather than a sub-box.
  (3) the content statistic P2, exact.

LEMMA L1, WHICH MAKES THE ENUMERATION COMPLETE FOR THE TARGET STRATUM.
For six reals with spread m = max - min,
    P2 = sum_i (a_i - abar)^2 = (1/6) sum_{i<j} (a_i - a_j)^2 >= m^2 / 6,
the inequality by keeping only the pair realising the spread.  Hence
    log P2 < 6  =>  m^2 < 6 e^6 = 2420.57...  =>  m <= 49.
B1 runs to spread 80 > 49, so B1 CONTAINS EVERY admissible canonical integer
6-tuple with log P2 < 6 -- not a sample of them, all of them, over all of Z^6
up to the construction's exact translation, scaling and reflection symmetries.
The identity and the bound are both CHECKED numerically in this run, not
asserted.

usage: run002_enumerate.py [--exhaustive-max 80] [--n-sampled-tested 3000000]
"""
import argparse
import itertools
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
import prefilter
import surface
from admissible import phi_int, centred_content_from_poly
from runrec import Run

TARGET_CEILING = 13          # frozen in H-ECQ-0ed5c8; NOT adjustable here
TARGET_LOG_P2 = 6.0          # frozen in H-ECQ-0ed5c8; NOT adjustable here
SEED = 20260823

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir,
                   'stratum_enumeration.json')


def canonical(tup):
    """Unchanged from BATCH-541940 tuple_scan_v2.canonical."""
    e = sorted(tup)
    e = [x - e[0] for x in e]
    g = 0
    for x in e:
        g = math.gcd(g, x)
    if g > 1:
        e = [x // g for x in e]
    m = e[-1]
    return tuple(min(e, sorted(m - x for x in e)))


def spread_bound_for_log_p2(limit):
    """The largest spread compatible with log P2 < limit, by Lemma L1."""
    return int(math.isqrt(int(6 * math.exp(limit))))


def check_lemma_L1(rng, n=2000):
    """CHECK the identity and the bound rather than assert them."""
    worst_ident = 0.0
    viol = 0
    for _ in range(n):
        a = sorted(rng.sample(range(-500, 501), 6))
        p2, _, _, _ = centred_content_from_poly(
            _monic_from_roots(a))
        pair = F(sum((x - y) ** 2 for i, x in enumerate(a)
                     for y in a[i + 1:]), 6)
        worst_ident = max(worst_ident, abs(float(p2 - pair)))
        m = a[-1] - a[0]
        if p2 < F(m * m, 6):
            viol += 1
    return {'n_sampled_tuples': n,
            'identity_P2_equals_pairsum_over_6_max_abs_error': worst_ident,
            'n_violations_of_P2_ge_spread_sq_over_6': viol,
            'checked_not_asserted': True}


def _monic_from_roots(roots):
    q = [F(1)]
    for a in roots:
        n = [F(0)] * (len(q) + 1)
        for i, c in enumerate(q):
            n[i] += c * F(-a)
            n[i + 1] += c
        q = n
    return q


_LEGEND_CACHE = {}


def _legend(rows, field):
    key = id(rows), field
    if key not in _LEGEND_CACHE:
        vals = []
        seen = set()
        for r in rows:
            v = r.get(field)
            if v not in seen:
                seen.add(v)
                vals.append(v)
        _LEGEND_CACHE[key] = {str(i): v for i, v in enumerate(vals)}
        _LEGEND_CACHE[key, 'inv'] = {v: i for i, v in enumerate(vals)}
    return _LEGEND_CACHE[key]


def _code(rows, field, value):
    _legend(rows, field)
    return _LEGEND_CACHE[(id(rows), field), 'inv'][value]


def analyse_tuple(tup):
    """Pre-filter FIRST, then the full census, then the content statistic."""
    row = {'canonical_tuple': list(tup),
           'spread': max(tup) - min(tup)}
    try:
        fam = measure.family_from_tuple(tup)
    except BaseException as e:
        row.update(status='refused', reason='family_construction_failed: %s: %s'
                                            % (type(e).__name__, e))
        return row, None
    if fam.deg_x_r != 4:
        row.update(status='refused', reason='deg_x_r_%d_not_a_genus_1_quartic'
                                            % fam.deg_x_r, deg_x_r=fam.deg_x_r)
        return row, None
    rc = fam.r_coeff_polys()
    # ---- (1) THE PRE-FILTER, BEFORE ANYTHING ELSE ----------------------
    try:
        pf = prefilter.prefilter(rc, TARGET_CEILING)
    except BaseException as e:
        row.update(status='refused', reason='prefilter_failed: %s: %s'
                                            % (type(e).__name__, e))
        return row, None
    if pf['decision'] == 'discarded' and pf['reason'] == \
            'degenerate_zero_discriminant':
        # NOT a filter discard and NOT an elliptic surface: the Jacobian
        # discriminant vanishes identically in T, so the family has no fibre
        # census, no ceiling and no Euler check.  Persisted with its own
        # status so it can never be confused with a filtered-out family nor
        # counted as a failed Euler check.
        row.update(status='degenerate',
                   reason='discriminant_vanishes_identically_in_T_not_an_'
                          'elliptic_surface',
                   prefilter_seconds=pf['prefilter_seconds'])
        return row, None
    # ---- (2) the full fibre census, for EVERY family (soundness control)
    try:
        s = surface.analyse(rc)
    except BaseException as e:
        s = {'error': '%s: %s' % (type(e).__name__, e)}
    # ---- (3) the content statistic -------------------------------------
    p2, _p3, _p5, phi = centred_content_from_poly(fam.q)
    logp2 = math.log(float(p2)) if p2 > 0 else float('-inf')
    ceil_true = s.get('shioda_tate_ceiling')
    row.update({
        'status': 'enumerated',
        'reason': 'admissible, pre-filtered and censused',
        'prefilter_decision': pf['decision'],
        'prefilter_reason': pf['reason'],
        'prefilter_seconds': pf['prefilter_seconds'],
        'deg_gcd_DD_DDprime': pf.get('resultant_test', {}).get(
            'deg_gcd_DD_DDprime'),
        'finite_discriminant_squarefree': pf.get('resultant_test', {}).get(
            'finite_discriminant_squarefree'),
        'cheap_ceiling': pf.get('cheap_ceiling'),
        'shioda_tate_ceiling': ceil_true,
        'sum_m_v_minus_1': s.get('sum_m_v_minus_1'),
        'surface_degree_d': s.get('surface_degree_d'),
        'euler_check_ok': (s.get('euler_number_check') or {}).get('ok'),
        'n_reducible_finite_fibres': (
            sum(1 for f in s.get('fibres', [])
                if f['place'] != 'infinity' and (f.get('m_v') or 1) > 1)
            if 'fibres' in s else None),
        'fibre_type_at_infinity': next(
            (f['type'] for f in s.get('fibres', [])
             if f['place'] == 'infinity'), None),
        'content_P2_exact': str(p2),
        'log_content_P2': logp2,
        'admissibility_phi': str(phi),
        'in_target_stratum': bool(ceil_true is not None
                                  and ceil_true >= TARGET_CEILING
                                  and logp2 < TARGET_LOG_P2),
    })
    detail = {
        'canonical_tuple': list(tup),
        'spread': row['spread'],
        'content_P2_exact': str(p2),
        'log_content_P2': logp2,
        'surface_degree_d': s.get('surface_degree_d'),
        'fibres_including_place_at_infinity': s.get('fibres'),
        'sum_m_v_minus_1': s.get('sum_m_v_minus_1'),
        'n_reducible_finite_fibres': row['n_reducible_finite_fibres'],
        'fibre_type_at_infinity': row['fibre_type_at_infinity'],
        'shioda_tate_ceiling_from_own_fibre_configuration': ceil_true,
        'shioda_tate_ceiling_formula': '(10d - 2) - sum_v deg(v)(m_v - 1) over '
                                       'ALL places including T = infinity',
        'euler_check': s.get('euler_number_check'),
        'generic_K3_bound_NOT_READ': s.get('generic_K3_bound_NOT_USED'),
        'prefilter': pf,
        'in_target_stratum': row['in_target_stratum'],
    }
    return row, detail


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--exhaustive-max', type=int, default=80)
    ap.add_argument('--exhaustive-min', type=int, default=5)
    ap.add_argument('--sampled-lo', type=int, default=81)
    ap.add_argument('--sampled-hi', type=int, default=3000)
    ap.add_argument('--n-sampled-tested', type=int, default=3000000)
    ap.add_argument('--time-budget', type=float, default=900.0)
    ap.add_argument('--run-id', default='RUN-ECQSTR-827765-002')
    ap.add_argument('--out', default=OUT)
    a = ap.parse_args(argv)

    cmd = ('python3 run002_enumerate.py --exhaustive-max %d --exhaustive-min %d '
           '--sampled-lo %d --sampled-hi %d --n-sampled-tested %d '
           '--time-budget %g --run-id %s --out %s   (cwd: coordination/goals/GOAL-ECQ-002/batches/'
           'BATCH-8b08ef/tasks/TASK-20260823-827765/scripts)'
           % (a.exhaustive_max, a.exhaustive_min, a.sampled_lo, a.sampled_hi,
              a.n_sampled_tested, a.time_budget, a.run_id,
              os.path.relpath(a.out)))

    with Run(a.run_id,
             'squarefree-discriminant pre-filtered enumeration of admissible '
             'canonical 6-tuples over the declared enlarged box, pre-filter '
             'applied before any height evaluation',
             cmd,
             {'box_B1_exhaustive_spread': [a.exhaustive_min, a.exhaustive_max],
              'box_B2_sampled_spread': [a.sampled_lo, a.sampled_hi],
              'n_sampled_tested': a.n_sampled_tested,
              'target_ceiling_frozen': TARGET_CEILING,
              'target_log_P2_frozen': TARGET_LOG_P2,
              'seed': SEED,
              'randomness_sources': [
                  'python random.Random(20260823) for box B2 tuple sampling '
                  'and for the Lemma L1 numerical check; no other source']},
             wall_clock_budget_s=a.time_budget) as R:

        crec = constants.assert_frozen_constants()
        R.log('frozen-constant abort assertion exercised: all_match=%s '
              '(%d checks)' % (crec['all_match'], crec['n_checks']))

        rng = random.Random(SEED)
        lemma = check_lemma_L1(rng)
        m_bound = spread_bound_for_log_p2(TARGET_LOG_P2)
        lemma['spread_bound_for_log_P2_below_%g' % TARGET_LOG_P2] = m_bound
        lemma['exhaustive_box_max_spread'] = a.exhaustive_max
        lemma['exhaustive_box_contains_whole_target_stratum'] = (
            a.exhaustive_max >= m_bound)
        R.log('LEMMA L1 checked: identity max error %.3g, %d violations; '
              'log P2 < %g forces spread <= %d; exhaustive box runs to %d -> '
              'target stratum fully contained = %s'
              % (lemma['identity_P2_equals_pairsum_over_6_max_abs_error'],
                 lemma['n_violations_of_P2_ge_spread_sq_over_6'],
                 TARGET_LOG_P2, m_bound, a.exhaustive_max,
                 lemma['exhaustive_box_contains_whole_target_stratum']))

        # ---------------- B1 enumeration -------------------------------
        t_enum = time.time()
        seen = set()
        b1 = []
        n_tested = n_nonprimitive = n_phi = n_dup = 0
        for m in range(a.exhaustive_min, a.exhaustive_max + 1):
            for mid in itertools.combinations(range(1, m), 4):
                n_tested += 1
                t = (0,) + mid + (m,)
                if math.gcd(math.gcd(math.gcd(math.gcd(mid[0], mid[1]),
                                              mid[2]), mid[3]), m) != 1:
                    n_nonprimitive += 1
                    continue
                if phi_int(t):
                    n_phi += 1
                    continue
                c = canonical(t)
                if c in seen:
                    n_dup += 1
                    continue
                seen.add(c)
                b1.append(c)
        t_b1 = time.time() - t_enum
        R.log('B1 exhaustive spread %d..%d: %d tuples tested, %d not primitive, '
              '%d phi != 0 (inadmissible), %d duplicate canonical, %d admissible '
              'canonical, %.1fs'
              % (a.exhaustive_min, a.exhaustive_max, n_tested, n_nonprimitive,
                 n_phi, n_dup, len(b1), t_b1))
        assert n_tested == n_nonprimitive + n_phi + n_dup + len(b1), \
            'attempted/measured arithmetic gap in B1'

        # ---------------- B2 sampling ----------------------------------
        t0 = time.time()
        b2 = []
        s_tested = s_nonprim = s_phi = s_dup = 0
        for _ in range(a.n_sampled_tested):
            s_tested += 1
            m = rng.randint(a.sampled_lo, a.sampled_hi)
            mid = tuple(sorted(rng.sample(range(1, m), 4)))
            t = (0,) + mid + (m,)
            if math.gcd(math.gcd(math.gcd(math.gcd(mid[0], mid[1]), mid[2]),
                                 mid[3]), m) != 1:
                s_nonprim += 1
                continue
            if phi_int(t):
                s_phi += 1
                continue
            c = canonical(t)
            if c in seen:
                s_dup += 1
                continue
            seen.add(c)
            b2.append(c)
        t_b2 = time.time() - t0
        R.log('B2 sampled spread %d..%d: %d tested, %d admissible canonical, '
              '%.1fs' % (a.sampled_lo, a.sampled_hi, s_tested, len(b2), t_b2))
        assert s_tested == s_nonprim + s_phi + s_dup + len(b2), \
            'attempted/measured arithmetic gap in B2'

        # ---------------- pre-filter then census -----------------------
        rows, details = [], []
        pf_seconds = 0.0
        budget_hit = False
        work = [('B1_exhaustive_spread_%d_%d' % (a.exhaustive_min,
                                                 a.exhaustive_max), t)
                for t in b1]
        work += [('B2_sampled_spread_%d_%d' % (a.sampled_lo, a.sampled_hi), t)
                 for t in b2]
        t0 = time.time()
        for i, (box, t) in enumerate(work):
            if R.budget_reached():
                budget_hit = True
                R.warn('WALL CLOCK REACHED after %d of %d enumerated tuples; '
                       'remaining tuples are ATTEMPTED-NOT-MEASURED'
                       % (i, len(work)))
                for box2, t2 in work[i:]:
                    rows.append({'canonical_tuple': list(t2),
                                 'spread': max(t2) - min(t2), 'box': box2,
                                 'status': 'attempted_not_measured',
                                 'reason': 'wall_clock_stop_infrastructure_'
                                           'outcome_bounds_coverage'})
                break
            row, detail = analyse_tuple(t)
            row['box'] = box
            pf_seconds += row.get('prefilter_seconds') or 0.0
            rows.append(row)
            if detail is not None:
                detail['box'] = box
                details.append(detail)
            if (i + 1) % 2000 == 0:
                R.log('  ... %d/%d censused (%.1fs)'
                      % (i + 1, len(work), time.time() - t0))
        t_census = time.time() - t0

        # ---------------- counts ---------------------------------------
        enum = [r for r in rows if r['status'] == 'enumerated']
        retained = [r for r in enum if r['prefilter_decision'] == 'retained']
        discarded = [r for r in enum if r['prefilter_decision'] == 'discarded']
        target = [r for r in enum if r['in_target_stratum']]
        hi_ceiling = [r for r in enum if (r['shioda_tate_ceiling'] or 0)
                      >= TARGET_CEILING]

        # CTL-PREFILTER-SOUNDNESS over the WHOLE enumeration, not a sub-box
        false_negatives = [r for r in discarded
                           if (r['shioda_tate_ceiling'] or 0) >= TARGET_CEILING]
        cheap_exact = [r for r in enum if r['cheap_ceiling'] is not None]
        cheap_mismatch = [r for r in cheap_exact
                          if r['cheap_ceiling'] != r['shioda_tate_ceiling']]
        euler_bad = [r for r in enum if r['euler_check_ok'] is not True]

        max_spread_low_content = max(
            [r['spread'] for r in enum if r['log_content_P2'] < TARGET_LOG_P2],
            default=None)

        R.log('PRE-FILTER: %d enumerated, %d retained, %d discarded '
              '(cost %.4f s total, %.3f ms per tuple)'
              % (len(enum), len(retained), len(discarded), pf_seconds,
                 1000 * pf_seconds / max(1, len(enum))))
        R.log('CTL-PREFILTER-SOUNDNESS over the whole enumeration: %d families '
              'of ceiling >= %d, %d of them discarded by the filter '
              '(FALSE NEGATIVES)'
              % (len(hi_ceiling), TARGET_CEILING, len(false_negatives)))
        R.log('cheap ceiling exact on %d/%d decided families, %d mismatches'
              % (len(cheap_exact) - len(cheap_mismatch), len(cheap_exact),
                 len(cheap_mismatch)))
        R.log('Euler check sum(deg * v_disc) = 24 = 12d: %d failures of %d'
              % (len(euler_bad), len(enum)))
        R.log('TARGET STRATUM POPULATION (ceiling >= %d AND log P2 < %g) = %d'
              % (TARGET_CEILING, TARGET_LOG_P2, len(target)))
        R.log('largest spread observed with log P2 < %g = %s (Lemma L1 bound %d)'
              % (TARGET_LOG_P2, max_spread_low_content, m_bound))
        for r in sorted(target, key=lambda r: r['log_content_P2']):
            R.log('   TARGET %s ceiling %s log P2 %.4f spread %d'
                  % (r['canonical_tuple'], r['shioda_tate_ceiling'],
                     r['log_content_P2'], r['spread']))

        headline = {
            'tuples_tested_B1_exhaustive': n_tested,
            'tuples_tested_B2_sampled': s_tested,
            'tuples_tested_total': n_tested + s_tested,
            'rejected_not_primitive': n_nonprimitive + s_nonprim,
            'rejected_phi_nonzero_inadmissible': n_phi + s_phi,
            'rejected_duplicate_canonical': n_dup + s_dup,
            'admissible_canonical_tuples': len(b1) + len(b2),
            'admissible_and_enumerated': len(enum),
            'admissible_refused_deg_x_r_not_4': sum(
                1 for r in rows if r['status'] == 'refused'),
            'admissible_degenerate_zero_discriminant': sum(
                1 for r in rows if r['status'] == 'degenerate'),
            'attempted_not_measured_wall_clock': sum(
                1 for r in rows if r['status'] == 'attempted_not_measured'),
            'prefilter_retained': len(retained),
            'prefilter_discarded': len(discarded),
            'population_count_ceiling_ge_%d_and_log_P2_lt_%g'
            % (TARGET_CEILING, TARGET_LOG_P2): len(target),
            'families_of_ceiling_ge_%d_any_content' % TARGET_CEILING:
                len(hi_ceiling),
            'families_with_log_P2_lt_%g_any_ceiling' % TARGET_LOG_P2: sum(
                1 for r in enum if r['log_content_P2'] < TARGET_LOG_P2),
        }
        assert (headline['tuples_tested_total']
                == headline['rejected_not_primitive']
                + headline['rejected_phi_nonzero_inadmissible']
                + headline['rejected_duplicate_canonical']
                + headline['admissible_canonical_tuples']), \
            'attempted/measured arithmetic gap in the headline accounting'
        assert (headline['admissible_canonical_tuples']
                == headline['admissible_and_enumerated']
                + headline['admissible_refused_deg_x_r_not_4']
                + headline['admissible_degenerate_zero_discriminant']
                + headline['attempted_not_measured_wall_clock']), \
            'attempted/measured arithmetic gap in the census accounting'

        ceiling_hist = {}
        for r in enum:
            k = str(r['shioda_tate_ceiling'])
            ceiling_hist[k] = ceiling_hist.get(k, 0) + 1

        doc = {
            'what': 'squarefree-discriminant PRE-FILTERED enumeration of '
                    'admissible canonical integer 6-tuples of Mestre\'s '
                    'rank-12 quartic construction, over the declared enlarged '
                    'box; the pre-filter is applied BEFORE any height '
                    'evaluation, any Mestre-Nagao ordering and any rank search',
            'task_id': 'TASK-20260823-827765',
            'experiment_id': 'EXP-ECQ-0e0cbb',
            'hypothesis_id': 'H-ECQ-0ed5c8',
            'run_id': a.run_id,
            'run_record': 'experiments/EXP-ECQ-0e0cbb/runs/' + a.run_id,
            'frozen_constants_read_at_run_time': crec,
            'thresholds_are_frozen': {
                'target_ceiling': TARGET_CEILING,
                'target_log_P2': TARGET_LOG_P2,
                'source': 'H-ECQ-0ed5c8 predictions; NOT adjusted after the '
                          'enumeration was read; no protocol_amendment was '
                          'made or is claimed',
            },
            'box_declared_before_counts_were_read': {
                'B1_exhaustive': {'spread_min': a.exhaustive_min,
                                  'spread_max': a.exhaustive_max,
                                  'enlarged_beyond_prior_census_spread_74': True,
                                  'order': 'spread ascending, then the middle '
                                           '4-subset lexicographically'},
                'B2_sampled': {'spread_min': a.sampled_lo,
                               'spread_max': a.sampled_hi,
                               'n_tested': a.n_sampled_tested,
                               'rng': 'random.Random(%d)' % SEED},
                'canonicalisation': 'translate min to 0, divide out the gcd, '
                                    'reflect a -> max - a when lexicographically '
                                    'smaller (unchanged from BATCH-541940 '
                                    'tuple_scan_v2.canonical)',
            },
            'lemma_L1_completeness_of_the_target_stratum': dict(
                lemma,
                statement='P2 = (1/6) sum_{i<j}(a_i - a_j)^2 >= spread^2/6, so '
                          'log P2 < %g forces spread <= %d. B1 runs to spread '
                          '%d, so B1 contains EVERY admissible canonical '
                          'integer 6-tuple of the target stratum, over all of '
                          'Z^6 up to the construction\'s exact symmetries.'
                          % (TARGET_LOG_P2, m_bound, a.exhaustive_max),
                largest_spread_observed_with_log_P2_below_target=(
                    max_spread_low_content),
            ),
            'prefilter': {
                'what': 'ONE squarefreeness test on the degree-20 finite '
                        'discriminant: Res(DD, DD_prime) != 0, decided as '
                        'deg gcd(DD, DD_prime) == 0',
                'applied_before_any_height_evaluation': True,
                'applied_before_any_mestre_nagao_ordering': True,
                'applied_before_any_rank_search': True,
                'total_seconds': pf_seconds,
                'seconds_per_tuple': pf_seconds / max(1, len(enum)),
                'retained': len(retained),
                'discarded': len(discarded),
                'status': 'AN EFFICIENCY HEURISTIC WITH MEASURED SUPPORT, '
                          'NEVER AN IMPOSSIBILITY CLAIM. The Shioda-Tate '
                          'ceiling bounds the GENERIC rank over Qbar(T); a '
                          'specialisation over Q is at least the generic rank '
                          'and CAN EXCEED IT (KN-FIND-6b3e17). No claim '
                          'whatever is made that a discarded family cannot '
                          'host a rank-12 specialisation over Q.',
                'soundness_argument': prefilter.__doc__,
            },
            'CTL_PREFILTER_SOUNDNESS': {
                'scope': 'checked over the WHOLE enumeration, not a sub-box: '
                         'the full fibre census was computed for every '
                         'enumerated family, discarded ones included',
                'n_families_censused': len(enum),
                'n_families_ceiling_ge_target': len(hi_ceiling),
                'n_false_negatives_ceiling_ge_target_but_discarded':
                    len(false_negatives),
                'false_negative_examples': false_negatives[:20],
                'cheap_ceiling_decided_exactly': len(cheap_exact),
                'cheap_ceiling_mismatches_against_full_census':
                    len(cheap_mismatch),
                'cheap_ceiling_mismatch_examples': cheap_mismatch[:20],
                'outcome': 'PASS' if not false_negatives and not cheap_mismatch
                           else 'FAIL',
            },
            'euler_check': {
                'formula': 'sum_v deg(v) * v_disc(v) = 24 = 12d over all places '
                           'including T = infinity',
                'n_families_checked': len(enum),
                'denominator_note': 'families with an identically vanishing '
                                    'discriminant are NOT elliptic surfaces, '
                                    'carry no fibre census and are excluded '
                                    'from this denominator with their own '
                                    'status "degenerate"; their count is in '
                                    'headline_counts',
                'n_failures': len(euler_bad),
                'failures': euler_bad[:20],
            },
            'ceiling_histogram_from_own_fibre_configuration': ceiling_hist,
            'headline_counts': headline,
            'timing': {'b1_enumeration_seconds': t_b1,
                       'b2_sampling_seconds': t_b2,
                       'prefilter_and_census_seconds': t_census,
                       'time_budget_reached': budget_hit},
            'target_stratum_families_full_detail': [
                d for d in details if d['in_target_stratum']],
            'retained_families_full_detail': [
                d for d in details
                if d['prefilter']['decision'] == 'retained'],
            'attempted_rows_every_admissible_tuple_with_status_and_reason': {
                'reduced_at_source': 'COLUMNAR, per DEC-20260823-ee9162 R15 '
                                     'and the declared artifact_size_budget '
                                     '(per_file_mib 5). EVERY admissible '
                                     'canonical tuple appears as one row with '
                                     'its status and its reason; nothing is '
                                     'dropped and nothing is truncated. The '
                                     'verbose per-row dict form of the same '
                                     'rows is in the run record at '
                                     'experiments/EXP-ECQ-0e0cbb/runs/'
                                     + a.run_id + '/raw-result.json for the '
                                     'subset carrying full detail below.',
                'columns': ['canonical_tuple', 'spread', 'box_code',
                            'status_code',
                            'reason_code', 'prefilter_decision_code',
                            'prefilter_reason_code',
                            'deg_gcd_DD_DDprime',
                            'finite_discriminant_squarefree',
                            'cheap_ceiling', 'shioda_tate_ceiling',
                            'sum_m_v_minus_1', 'n_reducible_finite_fibres',
                            'fibre_type_at_infinity', 'euler_check_ok',
                            'log_content_P2', 'in_target_stratum'],
                'n_rows': len(rows),
                'code_legend': {
                    'box_code': _legend(rows, 'box'),
                    'status_code': _legend(rows, 'status'),
                    'reason_code': _legend(rows, 'reason'),
                    'prefilter_decision_code': _legend(rows,
                                                       'prefilter_decision'),
                    'prefilter_reason_code': _legend(rows, 'prefilter_reason'),
                },
                'code_legend_note': 'the five *_code columns are integer keys '
                                    'into code_legend; each row therefore still '
                                    'carries its own status and its own reason '
                                    'in full, encoded rather than repeated. '
                                    'This is the REDUCTION AT SOURCE the '
                                    'artifact_size_budget requires; no row and '
                                    'no field is dropped.',
                'rows': [[r.get('canonical_tuple'), r.get('spread'),
                          _code(rows, 'box', r.get('box')),
                          _code(rows, 'status', r.get('status')),
                          _code(rows, 'reason', r.get('reason')),
                          _code(rows, 'prefilter_decision',
                                r.get('prefilter_decision')),
                          _code(rows, 'prefilter_reason',
                                r.get('prefilter_reason')),
                          r.get('deg_gcd_DD_DDprime'),
                          r.get('finite_discriminant_squarefree'),
                          r.get('cheap_ceiling'), r.get('shioda_tate_ceiling'),
                          r.get('sum_m_v_minus_1'),
                          r.get('n_reducible_finite_fibres'),
                          r.get('fibre_type_at_infinity'),
                          r.get('euler_check_ok'),
                          (round(r['log_content_P2'], 6)
                           if isinstance(r.get('log_content_P2'), float)
                           else None),
                          r.get('in_target_stratum')] for r in rows],
            },
            'attempted_rows_full_detail_for_the_load_bearing_subset': [
                {k: v for k, v in r.items() if k != 'prefilter_seconds'}
                for r in rows
                if r.get('in_target_stratum')
                or r.get('prefilter_decision') == 'retained'
                or (r.get('shioda_tate_ceiling') or 0) >= 12
                or r.get('status') in ('refused', 'attempted_not_measured')
                or (isinstance(r.get('log_content_P2'), float)
                    and r['log_content_P2'] < TARGET_LOG_P2)],
            'attempted_row_accounting_note':
                'Every ADMISSIBLE canonical tuple is persisted individually '
                'above with a status and a reason. Tuples rejected before '
                'admissibility are accounted by exact bucket counts in '
                'headline_counts (not primitive / phi != 0 / duplicate '
                'canonical), and the two assertions in this run require '
                'tested = sum(buckets) and admissible = enumerated + refused + '
                'attempted-not-measured, so no row can be lost to an '
                'arithmetic difference.',
        }
        with open(a.out, 'w') as fh:
            json.dump(doc, fh, indent=1)
        sz = os.path.getsize(a.out) / (1 << 20)
        R.log('wrote %s (%.2f MiB)' % (os.path.relpath(a.out), sz))
        if sz > 5.0:
            R.warn('ARTIFACT SIZE BUDGET: stratum_enumeration.json is %.2f MiB, '
                   'above the declared per_file_mib of 5' % sz)

        R.result.update({
            'headline_counts': headline,
            'target_stratum_population': len(target),
            'target_stratum_tuples': [r['canonical_tuple'] for r in target],
            'prefilter_seconds_total': pf_seconds,
            'prefilter_seconds_per_tuple': pf_seconds / max(1, len(enum)),
            'prefilter_retained': len(retained),
            'prefilter_discarded': len(discarded),
            'ctl_prefilter_soundness_false_negatives': len(false_negatives),
            'euler_check_failures': len(euler_bad),
            'lemma_L1': lemma,
            'deliverable': 'coordination/goals/GOAL-ECQ-002/batches/'
                           'BATCH-8b08ef/tasks/TASK-20260823-827765/'
                           'stratum_enumeration.json',
            'deliverable_mib': sz,
            'time_budget_reached': budget_hit,
            'certificate': {'kind': 'none',
                            'why': 'enumeration and fibre bookkeeping; no '
                                   'discrete log and no factor-base relation'},
        })
        if budget_hit:
            R.status = 'completed_valid'
            R.deviations.append(
                'wall clock reached during the census; remaining tuples are '
                'persisted as attempted_not_measured. INFRASTRUCTURE OUTCOME, '
                'never negative mathematical evidence.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
