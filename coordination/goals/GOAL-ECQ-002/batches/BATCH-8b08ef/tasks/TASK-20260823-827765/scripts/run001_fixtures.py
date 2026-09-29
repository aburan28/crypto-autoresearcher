#!/usr/bin/env python3
"""
RUN-ECQSTR-827765-001 -- INSTRUMENT CHECK.  Nothing else may run first.

Four things, and every PASS CONDITION IS STATED BEFORE THE OBJECT IS RUN, so
that the control can actually fail (review_plan proves_too_much.failure_signature).

  1. CONSTANTS.  Read the r >= 12 cell and the construction-class benchmark
     from the frozen files and ABORT if either differs from the audit value
     parsed out of H-ECQ-0ed5c8.  Exercised, not merely present.
  2. CTL-BASELINE-FIXTURE.  Mestre's published tuple A must reproduce its
     envelope 79.6237719007 at t = 4, and five frozen board curves must
     reproduce their recorded ICARM naive height from a-invariants ALONE to
     0.0 absolute difference.
     PASS = |envelope - 79.6237719007| <= 5e-10 at argmin t = 4, and all five
     board deltas exactly 0.0.
  3. CTL-PROVES-TOO-MUCH-A.  Tuple A (-17,-16,10,11,14,17), published rank
     >= 11 over Q(T).
     PASS = ceiling assigned >= 11 (expected 15) AND the pre-filter RETAINS it.
     A ceiling below 11 falsifies the ceiling computation.
  4. CTL-PROVES-TOO-MUCH-B.  A generic ceiling-9 family with six finite I_2
     fibres, of the class holding 13257 of 13391 census families.
     PASS = the pre-filter DISCARDS it.  A filter that keeps this filters
     nothing and the cost argument collapses.

Also run here: the resultant/gcd cross-check that the filter's stated predicate
is the one the code decides.
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import constants
import heights
import measure
import prefilter
import surface
from runrec import Run

TUPLE_A = (-17, -16, 10, 11, 14, 17)
FIXTURE_A_ENVELOPE = 79.6237719007          # frozen regression fixture, not a
FIXTURE_A_T = '4'                           # frontier or benchmark value
FIXTURE_TOL = 5e-10

CMD = ('python3 run001_fixtures.py   '
       '(cwd: coordination/goals/GOAL-ECQ-002/batches/BATCH-8b08ef/tasks/'
       'TASK-20260823-827765/scripts)')


def main():
    with Run('RUN-ECQSTR-827765-001',
             'instrument check: frozen-constant abort assertion, baseline '
             'fixture, and both proves-too-much objects with PASS conditions '
             'stated in advance',
             CMD,
             {'tuple_A': list(TUPLE_A),
              'fixture_envelope': FIXTURE_A_ENVELOPE,
              'fixture_tolerance': FIXTURE_TOL,
              'n_board_curves_checked': 5,
              'randomness_sources': ['none: this run is deterministic']},
             wall_clock_budget_s=180) as R:

        res = {'controls': {}}

        # --- 1. constants, abort on mismatch --------------------------------
        R.log('CTL-CONSTANTS: reading frozen files and asserting vs audit values')
        try:
            crec = constants.assert_frozen_constants()
        except constants.FrozenConstantMismatch as e:
            R.status = 'invalid_measurement'
            R.result['failure_class'] = 'invalid_measurement'
            R.result['frozen_constant_mismatch'] = str(e)
            raise
        res['frozen_constants'] = crec
        R.log('  cell r>=%d read = %r (curve_id %s, %s)'
              % (crec['cell']['rank_threshold'], crec['cell']['min_naive_height'],
                 crec['cell']['curve_id'], crec['cell']['submitter']))
        R.log('  benchmark board id %s read = %r'
              % (crec['benchmark']['board_id'], crec['benchmark']['naive_height']))
        R.log('  abort-on-mismatch assertion exercised over %d checks: all_match=%s'
              % (crec['n_checks'], crec['all_match']))

        # --- 2. baseline fixture -------------------------------------------
        R.log('CTL-BASELINE-FIXTURE: PASS = tuple A envelope within %g of '
              '%.10f at t=%s, and five board heights to 0.0'
              % (FIXTURE_TOL, FIXTURE_A_ENVELOPE, FIXTURE_A_T))
        famA = measure.family_from_tuple(TUPLE_A, name='MESTRE-PUBLISHED-A')
        idc = famA.identity_checks()
        mA = measure.measure(famA)
        env = mA['measured_envelope_min_naive_height']
        fixture_env_ok = (abs(env - FIXTURE_A_ENVELOPE) <= FIXTURE_TOL
                          and mA['envelope_argmin_t'] == FIXTURE_A_T)

        with open(constants.SNAPSHOT) as fh:
            board = json.load(fh)['curves']
        board_rows = []
        for c in sorted(board, key=lambda c: c['id'])[:5]:
            ai = [int(a) for a in c['ainvs']]
            h, c4, c6, _ = heights.naive_height_from_ainvs(ai)
            board_rows.append({
                'board_id': c['id'],
                'recorded_naive_height': c['naive_height'],
                'recomputed_from_ainvs_alone': h,
                'absolute_difference': abs(h - c['naive_height']),
                'curve_key_recorded': str(c['curve_key']),
                'curve_key_recomputed': '%d:%d' % (c4, c6),
                'curve_key_matches': str(c['curve_key']) == '%d:%d' % (c4, c6),
            })
        board_ok = all(r['absolute_difference'] == 0.0
                       and r['curve_key_matches'] for r in board_rows)
        res['controls']['CTL-BASELINE-FIXTURE'] = {
            'pass_condition_stated_in_advance':
                'tuple A envelope within %g of %.10f at argmin t = %s, and all '
                'five board naive heights recomputed from a-invariants alone '
                'to absolute difference 0.0 with matching curve_key'
                % (FIXTURE_TOL, FIXTURE_A_ENVELOPE, FIXTURE_A_T),
            'tuple_A_envelope_measured': env,
            'tuple_A_envelope_fixture': FIXTURE_A_ENVELOPE,
            'tuple_A_envelope_abs_difference': abs(env - FIXTURE_A_ENVELOPE),
            'tuple_A_envelope_argmin_t': mA['envelope_argmin_t'],
            'construction_identity_checks': idc,
            'board_height_recomputation': board_rows,
            'outcome': 'PASS' if (fixture_env_ok and board_ok) else 'FAIL',
        }
        R.log('  tuple A envelope %r at t=%s (fixture %.10f, |diff| %.3g) -> %s'
              % (env, mA['envelope_argmin_t'], FIXTURE_A_ENVELOPE,
                 abs(env - FIXTURE_A_ENVELOPE), 'ok' if fixture_env_ok else 'FAIL'))
        R.log('  five board heights from a-invariants alone: max |diff| = %r -> %s'
              % (max(r['absolute_difference'] for r in board_rows),
                 'ok' if board_ok else 'FAIL'))

        # --- 3. CTL-PROVES-TOO-MUCH-A ---------------------------------------
        R.log('CTL-PROVES-TOO-MUCH-A: PASS = ceiling >= 11 AND pre-filter RETAINS')
        sA = surface.analyse(famA.r_coeff_polys())
        pA = prefilter.prefilter(famA.r_coeff_polys())
        okA = (sA['shioda_tate_ceiling'] is not None
               and sA['shioda_tate_ceiling'] >= 11
               and pA['decision'] == 'retained')
        res['controls']['CTL-PROVES-TOO-MUCH-A'] = {
            'object': 'Mestre published tuple A %s, rank >= 11 over Q(T)'
                      % (list(TUPLE_A),),
            'pass_condition_stated_in_advance':
                'ceiling assigned >= 11 (expected 15) and the pre-filter does '
                'NOT discard it',
            'ceiling_from_own_fibre_configuration': sA['shioda_tate_ceiling'],
            'sum_m_v_minus_1': sA['sum_m_v_minus_1'],
            'euler_check': sA['euler_number_check'],
            'fibres': sA['fibres'],
            'prefilter': pA,
            'outcome': 'PASS' if okA else 'FAIL',
        }
        R.log('  tuple A ceiling = %s, prefilter = %s (%s) -> %s'
              % (sA['shioda_tate_ceiling'], pA['decision'], pA['reason'],
                 'PASS' if okA else 'FAIL'))

        # --- 4. CTL-PROVES-TOO-MUCH-B ---------------------------------------
        R.log('CTL-PROVES-TOO-MUCH-B: PASS = pre-filter DISCARDS a generic '
              'ceiling-9 family with six finite I_2 fibres')
        # a representative of the exhaustive census class holding 13257 of
        # 13391 families -- ceiling 9, SIX finite I_2 fibres.  Its fibre census
        # is RE-DERIVED here from its own discriminant, never read from the
        # census file; the census is used only to name the representative.
        gen_tuple = (0, 1, 2, 3, 4, 5)
        famB = measure.family_from_tuple(gen_tuple)
        sB = surface.analyse(famB.r_coeff_polys())
        pB = prefilter.prefilter(famB.r_coeff_polys())
        n_finite_I2 = sum(1 for f in sB['fibres']
                          if f['place'] != 'infinity' and f['type'] == 'I_2')
        okB = pB['decision'] == 'discarded'
        res['controls']['CTL-PROVES-TOO-MUCH-B'] = {
            'object': 'generic family %s' % (list(gen_tuple),),
            'pass_condition_stated_in_advance':
                'the pre-filter DISCARDS it; a filter that keeps this filters '
                'nothing',
            'ceiling_from_own_fibre_configuration': sB['shioda_tate_ceiling'],
            'n_finite_I2_fibres': n_finite_I2,
            'n_reducible_finite_fibres': sum(
                1 for f in sB['fibres']
                if f['place'] != 'infinity' and (f['m_v'] or 1) > 1),
            'fibre_at_infinity': [f for f in sB['fibres']
                                  if f['place'] == 'infinity'],
            'euler_check': sB['euler_number_check'],
            'prefilter': pB,
            'outcome': 'PASS' if okB else 'FAIL',
        }
        R.log('  generic family ceiling = %s, %d finite I_2 fibres, prefilter '
              '= %s (%s) -> %s'
              % (sB['shioda_tate_ceiling'], n_finite_I2, pB['decision'],
                 pB['reason'], 'PASS' if okB else 'FAIL'))

        # --- 5. resultant / gcd cross-check ---------------------------------
        xchecks = []
        for tup in (TUPLE_A, gen_tuple, (0, 2, 8, 9, 11, 14)):
            fam = measure.family_from_tuple(tup)
            x = prefilter.resultant_cross_check(fam.r_coeff_polys())
            x['tuple'] = list(tup)
            xchecks.append(x)
        res['resultant_gcd_cross_check'] = {
            'why': 'the filter DECIDES Res(DD, DD_prime) != 0 by a gcd; this '
                   'forms the resultant explicitly and confirms the two agree',
            'rows': xchecks,
            'all_agree': all(x['agree'] for x in xchecks),
        }
        R.log('  resultant/gcd cross-check on %d families: all_agree=%s'
              % (len(xchecks), res['resultant_gcd_cross_check']['all_agree']))

        allpass = (res['controls']['CTL-BASELINE-FIXTURE']['outcome'] == 'PASS'
                   and okA and okB
                   and res['resultant_gcd_cross_check']['all_agree'])
        res['all_controls_pass'] = allpass
        res['certificate'] = {'kind': 'none',
                              'why': 'instrument check; no discrete log and no '
                                     'factor-base relation is claimed'}
        R.result.update(res)
        R.status = 'completed_valid' if allpass else 'invalid_measurement'
        R.log('ALL CONTROLS PASS = %s' % allpass)
        if not allpass:
            R.warn('an instrument control FAILED; per CTL-BASELINE-FIXTURE an '
                   'implementation that fails the fixture is not measured with')
    return 0


if __name__ == '__main__':
    sys.exit(main())
