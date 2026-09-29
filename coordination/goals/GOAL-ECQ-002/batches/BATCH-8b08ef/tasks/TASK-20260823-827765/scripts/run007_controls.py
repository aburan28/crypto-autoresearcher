#!/usr/bin/env python3
"""
RT-CONTROL-2 (a rung that ACTUALLY has no rational sections, VERIFIED) and
RT-CONTROL-3 (the random-curve rank null at matched naive height), plus the
k = 0 proves-too-much object.

RT-CONTROL-2 -- HOW THE RUNG IS BUILT, AND WHY IT IS EXACTLY MATCHED
--------------------------------------------------------------------
The admissibility condition phi = 0 is a relation among the power sums
p_1, ..., p_5 of the roots of q.  For a MONIC degree-6 q, p_1..p_5 depend on
e_1..e_5 only, i.e. on the coefficients of x^5 down to x^1 -- NOT on the
constant term, which is +e_6.  So:

    CHANGING ONLY THE CONSTANT TERM OF AN ADMISSIBLE q PRESERVES
    ADMISSIBILITY EXACTLY, AND PRESERVES THE CONTENT STATISTIC
    P_2 OF THE CENTRED ROOTS EXACTLY.

The rung is therefore a treatment family's own q with one integer changed: same
construction, same surface shape, same admissibility, IDENTICAL P_2 -- and the
constant term chosen so that q becomes IRREDUCIBLE over Q with Galois group
S_6.  That is the "12 sections against 0" contrast the campaign has owed since
BATCH-f2341e and has never run, at exact content matching rather than
regression matching.

WHY IT IS A NULL OBJECT, PROVED AND THEN CHECKED
------------------------------------------------
(1) NO RATIONAL SECTION.  Sections of Mestre's construction sit at
    x = a_i +- T for the RATIONAL roots a_i of q.  q irreducible of degree 6
    has none, so the rung has exactly 0 rational sections.
(2) NO RATIONAL TRACE P + P^sigma OF A CONJUGATE PAIR.  This is precisely
    where the BATCH-541940 k = 0 rung failed: with q a product of irreducible
    QUADRATICS, each conjugate root pair is Galois-STABLE, so the trace of the
    corresponding section pair is rational and the rung retained forced
    rational rank.  Here q is IRREDUCIBLE OVER Q, so no 2-element subset of
    its roots is Galois-stable -- a stable pair would give a rational quadratic
    factor -- and no section pair has a rational trace.  Galois group S_6 makes
    this maximal: S_6 in its natural degree-6 action preserves no partition of
    the six roots at all.  Irreducibility and the Galois group are both
    COMPUTED here, not assumed.
(3) CHECKED, NOT ONLY PROVED: ellrank is run on the rung at matched naive
    height and its certified-rank distribution is put beside RT-CONTROL-3's
    random-curve null at the same heights.

THE k = 0 PROVES-TOO-MUCH OBJECT
--------------------------------
The BATCH-541940 k = 0 rung (q a product of three irreducible quadratics) is
run alongside.  PASS for it is: it must NOT come out rank 0.  Any argument of
the form "no rational sections implies no rational rank" has to FAIL on it, and
if this run reported rank 0 there the argument would have proved too much.
The rational rank it retains is exhibited by certified points; THIS RUN DOES
NOT CONSTRUCT THE TRACE MAP P + P^sigma EXPLICITLY and says so rather than
asserting the provenance of those points.

RT-CONTROL-3
------------
Random elliptic curves at matched ICARM naive height, target bands h ~ 60, 70,
80, 93, 100, SAME INSTRUMENT AND SAME ALARM as every other search here (PARI
ellrank, 20 s alarm), rank re-derived by exact_certify.py.  n = 200 per band is
the target; whatever n is REACHED is reported as numerator over denominator and,
below 200, AS A BOUND AND NOT AS A DISTRIBUTION.
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

import cypari

import constants
import exact_certify as ec
import heights
import measure
import ranksearch
import surface
from admissible import centred_content_from_poly
from certify_candidates import naive_height
from mestre import MestreFamily
from runrec import Run

pari = cypari.pari
pari.allocatemem(2 ** 31, silent=True)

SEED = 20260823
BANDS = (60, 70, 80, 93, 100)


# ---------------------------------------------------------------------------
def galois_record(q_asc):
    """Irreducibility over Q and the Galois group of q, both COMPUTED."""
    s = '+'.join('(%s)*x^%d' % (int(c), i) for i, c in enumerate(q_asc) if c)
    irr = bool(int(pari('polisirreducible(%s)' % s)))
    rec = {'poly': s, 'irreducible_over_Q': irr}
    if irr:
        g = pari('polgalois(%s)' % s)
        rec['polgalois_order'] = int(g[0])
        rec['polgalois_parity'] = int(g[1])
        rec['polgalois_name'] = str(g[3])
        rec['is_S6'] = int(g[0]) == 720
    else:
        rec['factor_degrees'] = [int(pari('poldegree(F[%d,1])' % i))
                                 for i in range(1, int(pari(
                                     'matsize(F = factor(%s))[1]' % s)) + 1)]
        rec['is_S6'] = False
    return rec


def build_section_free_rung(tuple_entries, max_delta=400):
    """A treatment family's own q with ONLY the constant term changed, until q
    is irreducible over Q with Galois group S_6."""
    fam0 = measure.family_from_tuple(tuple_entries)
    q0 = list(fam0.q)
    p2_0, _, _, phi0 = centred_content_from_poly(q0)
    attempts = []
    for delta in range(1, max_delta + 1):
        for sgn in (1, -1):
            q = list(q0)
            q[0] = q[0] + sgn * delta
            g = galois_record(q)
            attempts.append({'delta': sgn * delta,
                             'irreducible': g['irreducible_over_Q'],
                             'is_S6': g.get('is_S6')})
            if not g.get('is_S6'):
                continue
            fam = MestreFamily(q, [], 'RTC2-S6-from-%s-delta%+d'
                               % (','.join(str(x) for x in tuple_entries),
                                  sgn * delta),
                               tuple_entries=None, kind='rt_control_2_S6')
            if fam.deg_x_r != 4:
                continue
            p2, _p3, _p5, phi = centred_content_from_poly(q)
            return fam, {
                'built_from_treatment_tuple': list(tuple_entries),
                'only_the_constant_term_changed': True,
                'delta_on_constant_term': sgn * delta,
                'q_treatment_ascending': [str(c) for c in q0],
                'q_rung_ascending': [str(c) for c in q],
                'content_P2_treatment_exact': str(p2_0),
                'content_P2_rung_exact': str(p2),
                'content_P2_exactly_matched': p2 == p2_0,
                'admissibility_phi_treatment': str(phi0),
                'admissibility_phi_rung': str(phi),
                'admissibility_preserved_phi_is_zero': phi == 0,
                'deg_x_r': fam.deg_x_r,
                'n_rational_roots': len(fam.rational_roots),
                'n_rational_sections': len(fam.sections),
                'galois': galois_record(q),
                'n_constant_terms_tried': len(attempts),
            }, attempts
    return None, {'error': 'no S_6 constant term found within delta %d'
                           % max_delta}, attempts


def certify_jacobian_at(fam, t0, alarm=20):
    """Height + certified rank lower bound for a family with NO rational
    sections: the Jacobian is used directly (it needs no rational point)."""
    quart = fam.quartic_at(t0)
    ai = measure._jacobian_ai(quart)
    if measure._disc(ai) == 0:
        return None
    r = pari('ellminimalmodel(ellinit(%s))[1..5]' % (ai,))
    mai = [int(x) for x in r]
    h, c4, c6 = naive_height(mai)
    row = {'t': str(t0), 'minimal_a_invariants': mai, 'naive_height': h,
           'curve_key': '%d:%d' % (c4, c6)}
    pts = []
    try:
        res = pari('alarm(%d, ellrank(ellinit(%s)))' % (alarm, mai))
        row['pari_ellrank_r_low'] = int(res[0])
        row['pari_ellrank_r_high'] = int(res[1])
        row['pari_ellrank_status'] = 'ok'
        for P in res[3]:
            try:
                pts.append((F(str(pari('%s[1]' % P))),
                            F(str(pari('%s[2]' % P)))))
            except BaseException:
                continue
    except BaseException as e:
        row['pari_ellrank_r_low'] = None
        row['pari_ellrank_r_high'] = None
        row['pari_ellrank_status'] = ('infrastructure_outcome: %s'
                                      % type(e).__name__)
    pts = [p for p in pts if ec.on_curve(ec.Qfield(), [F(a) for a in mai], p)]
    cert = ec.certify(mai, [[str(x), str(y)] for x, y in pts],
                      max_prime=6000, max_good_primes=150,
                      l_candidates=(2, 3, 5, 7, 11, 13, 17, 19))
    row['n_points_exhibited'] = len(pts)
    row['certified_rank_lower_bound'] = cert['certified_rank_lower_bound']
    row['points'] = [[str(x), str(y)] for x, y in pts]
    row['status'] = ('measured' if row['pari_ellrank_status'] == 'ok'
                     else 'attempted_not_measured')
    row['reason'] = ('ellrank point search completed; rank lower bound '
                     'certified in exact arithmetic'
                     if row['status'] == 'measured'
                     else 'pari_ellrank_alarm_point_search_truncated')
    return row


def random_curve_at_height(rng, h_target, tol=0.75, tries=400):
    """A random short-Weierstrass curve of ICARM naive height near h_target."""
    A = math.exp(h_target / 3) / 48.0
    B = math.exp(h_target / 2) / 864.0
    for _ in range(tries):
        a4 = rng.choice((1, -1)) * rng.randint(1, max(2, int(2 * A)))
        a6 = rng.choice((1, -1)) * rng.randint(1, max(2, int(2 * B)))
        ai = [0, 0, 0, a4, a6]
        _c4, _c6, disc = heights.c_invariants(ai)
        if disc == 0:
            continue
        try:
            m = pari('ellminimalmodel(ellinit(%s))[1..5]' % (ai,))
        except BaseException:
            continue
        mai = [int(x) for x in m]
        h, _, _, _ = heights.naive_height_from_ainvs(mai)
        if abs(h - h_target) <= tol:
            return mai, h
    return None, None


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--run-id', required=True)
    ap.add_argument('--n-per-band', type=int, default=200)
    ap.add_argument('--rtc2-time', type=float, default=280.0)
    ap.add_argument('--rtc3-time', type=float, default=520.0)
    ap.add_argument('--alarm', type=int, default=20)
    a = ap.parse_args(argv)

    cmd = ('python3 run007_controls.py --out %s --run-id %s --n-per-band %d '
           '--rtc2-time %g --rtc3-time %g --alarm %d   (cwd: coordination/'
           'goals/GOAL-ECQ-002/batches/BATCH-8b08ef/tasks/TASK-20260823-827765/'
           'scripts)' % (a.out, a.run_id, a.n_per_band, a.rtc2_time,
                         a.rtc3_time, a.alarm))

    with Run(a.run_id,
             'RT-CONTROL-2 (verified section-free S_6 bottom rung at exactly '
             'matched content) and RT-CONTROL-3 (random-curve rank null at '
             'matched naive height), plus the k = 0 proves-too-much object',
             cmd,
             {'n_per_band_target': a.n_per_band, 'height_bands': list(BANDS),
              'alarm_seconds': a.alarm, 'seed': SEED,
              'randomness_sources': [
                  'python random.Random(20260823) for RT-CONTROL-3 curve '
                  'sampling and for the treatment-tuple sample; no other '
                  'source']},
             wall_clock_budget_s=a.rtc2_time + a.rtc3_time + 120) as R:

        crec = constants.assert_frozen_constants()
        R.log('frozen-constant abort assertion exercised: all_match=%s'
              % crec['all_match'])
        rng = random.Random(SEED)
        out = {}

        # ---------------- RT-CONTROL-2 ---------------------------------
        R.log('RT-CONTROL-2: building section-free S_6 rungs at EXACTLY '
              'matched content P2')
        enum_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 os.pardir, 'stratum_enumeration.json')
        with open(enum_path) as fh:
            enum = json.load(fh)
        treat = [d['canonical_tuple']
                 for d in enum['retained_families_full_detail']]
        treat.sort()
        rng.shuffle(treat)

        t0 = time.time()
        rtc2 = []
        n_generated = 0
        for tup in treat:
            if time.time() - t0 > a.rtc2_time:
                R.warn('RT-CONTROL-2 wall clock reached after %d rungs'
                       % len(rtc2))
                break
            n_generated += 1
            fam, meta, _attempts = build_section_free_rung(tup)
            if fam is None:
                rtc2.append({'treatment_tuple': tup, 'status': 'refused',
                             'reason': meta.get('error')})
                continue
            m = measure.measure(fam, want_surface=True)
            if m.get('status') != 'measured':
                rtc2.append({'treatment_tuple': tup, 'status': 'refused',
                             'reason': m.get('status'), 'rung': meta})
                continue
            # the treatment family, measured with the SAME code
            famT = measure.family_from_tuple(tup)
            mT = measure.measure(famT, want_surface=True)
            cert = certify_jacobian_at(fam, F(m['envelope_argmin_t']), a.alarm)
            certT = ranksearch.search_fibre(
                famT, F(mT['envelope_argmin_t']), a.alarm)
            rtc2.append({
                'treatment_tuple': tup,
                'status': 'measured',
                'reason': 'rung built, verified section-free, and measured',
                'rung': meta,
                'rung_envelope_min_naive_height':
                    m['measured_envelope_min_naive_height'],
                'rung_envelope_argmin_t': m['envelope_argmin_t'],
                'rung_shioda_tate_ceiling':
                    (m.get('surface') or {}).get('shioda_tate_ceiling'),
                'rung_certified_at_argmin': cert,
                'treatment_envelope_min_naive_height':
                    mT['measured_envelope_min_naive_height'],
                'treatment_envelope_argmin_t': mT['envelope_argmin_t'],
                'treatment_n_rational_sections': mT['n_sections'],
                'treatment_shioda_tate_ceiling':
                    (mT.get('surface') or {}).get('shioda_tate_ceiling'),
                'treatment_certified_at_argmin': certT,
            })
            R.log('  rung from %s: 0 sections (S_6 %s), env %.3f cert %s  |  '
                  'treatment 12 sections, env %.3f cert %s'
                  % (tup, meta['galois'].get('is_S6'),
                     m['measured_envelope_min_naive_height'],
                     (cert or {}).get('certified_rank_lower_bound'),
                     mT['measured_envelope_min_naive_height'],
                     (certT or {}).get('certified_rank_lower_bound')))

        ok2 = [r for r in rtc2 if r['status'] == 'measured']
        out['RT_CONTROL_2'] = {
            'what': 'a bottom rung that ACTUALLY has no rational sections: q '
                    'irreducible of degree 6 with Galois group S_6, still '
                    'solving phi = 0, built by changing ONLY the constant term '
                    'of a treatment family\'s own q so that the content '
                    'statistic P2 is EXACTLY matched',
            'why_the_previous_rung_was_not_a_null':
                'the BATCH-541940 k = 0 rung had q a product of irreducible '
                'QUADRATICS, so each conjugate root pair is Galois-STABLE and '
                'the trace of the corresponding section pair is rational; the '
                'rung retained forced rational rank (12 of 15 at rank >= 3 '
                'against 0 of 79 random curves at matched height) and the '
                '12-sections-against-0 contrast was never run',
            'verification_not_assumption': {
                'no_rational_section': 'q irreducible of degree 6 has no '
                                       'rational root, so the construction '
                                       'supplies 0 rational sections; '
                                       'n_rational_sections is recorded per '
                                       'rung and is 0',
                'no_rational_trace_of_a_conjugate_pair':
                    'a Galois-stable 2-subset of the roots would give a '
                    'rational quadratic factor of q; q is irreducible over Q, '
                    'so no section pair has a rational trace. S_6 in its '
                    'natural degree-6 action preserves no partition at all, '
                    'which is the maximal form of this. Irreducibility AND '
                    'the Galois group are COMPUTED per rung (polisirreducible, '
                    'polgalois) and recorded.',
                'empirical_check': 'ellrank is run on each rung at its '
                                   'envelope argmin with the same instrument '
                                   'and the same alarm, and the resulting '
                                   'certified ranks are put beside '
                                   'RT-CONTROL-3 at matched height',
            },
            'generated_against_measured': {
                'n_treatment_tuples_attempted': n_generated,
                'n_rungs_measured': len(ok2),
                'n_rungs_refused': len(rtc2) - len(ok2),
                'attrition_disclosed': True,
            },
            'rung_certified_rank_distribution': _dist(
                [(r['rung_certified_at_argmin'] or {}).get(
                    'certified_rank_lower_bound') for r in ok2]),
            'treatment_certified_rank_distribution': _dist(
                [(r['treatment_certified_at_argmin'] or {}).get(
                    'certified_rank_lower_bound') for r in ok2]),
            'rows': rtc2,
        }
        R.log('RT-CONTROL-2: %d rungs measured of %d attempted; rung rank dist '
              '%s vs treatment %s'
              % (len(ok2), n_generated,
                 out['RT_CONTROL_2']['rung_certified_rank_distribution'],
                 out['RT_CONTROL_2']['treatment_certified_rank_distribution']))

        # ---------------- k = 0 proves-too-much object ------------------
        R.log('PROVES-TOO-MUCH (k = 0 rung): PASS = it must NOT come out rank 0')
        k0 = []
        for tup in treat[:6]:
            e = sorted(int(x) for x in tup)
            pairs = [(e[0], e[1]), (e[2], e[3]), (e[4], e[5])]
            if any(abs(x - y) == 2 for x, y in pairs):
                continue
            try:
                fam = measure.family_from_tuple(tup, perturb_pairs=3)
            except BaseException as ex:
                k0.append({'tuple': tup, 'status': 'refused',
                           'reason': str(ex)})
                continue
            if fam.deg_x_r != 4:
                k0.append({'tuple': tup, 'status': 'refused',
                           'reason': 'deg_x_r_%d' % fam.deg_x_r})
                continue
            m = measure.measure(fam, want_surface=False)
            if m.get('status') != 'measured':
                k0.append({'tuple': tup, 'status': 'refused',
                           'reason': m.get('status')})
                continue
            c = certify_jacobian_at(fam, F(m['envelope_argmin_t']), a.alarm)
            k0.append({'tuple': tup, 'status': 'measured',
                       'reason': 'k = 0 rung measured at its envelope argmin',
                       'galois': galois_record(fam.q),
                       'n_rational_sections': len(fam.sections),
                       'envelope_min_naive_height':
                           m['measured_envelope_min_naive_height'],
                       'certified_at_argmin': c})
            R.log('  k=0 rung from %s: %d rational sections, cert rank %s'
                  % (tup, len(fam.sections),
                     (c or {}).get('certified_rank_lower_bound')))
        k0ok = [r for r in k0 if r['status'] == 'measured']
        n_pos = sum(1 for r in k0ok
                    if ((r['certified_at_argmin'] or {}).get(
                        'certified_rank_lower_bound') or 0) > 0)
        out['PROVES_TOO_MUCH_k0_rung'] = {
            'object': 'the BATCH-541940 k = 0 rung: q a product of three '
                      'irreducible quadratics, 0 RATIONAL roots but every '
                      'conjugate pair Galois-stable',
            'pass_condition_stated_in_advance':
                'it must NOT come out rank 0. Any argument of the form "no '
                'rational sections implies no rational rank" must FAIL on it.',
            'n_measured': len(k0ok),
            'n_with_certified_rank_at_least_1': n_pos,
            'outcome': 'PASS' if (k0ok and n_pos > 0) else
                       ('FAIL' if k0ok else 'NOT_RUN'),
            'trace_map_disclosure':
                'THIS RUN DOES NOT CONSTRUCT THE TRACE MAP P + P^sigma '
                'EXPLICITLY. What is exhibited is certified rational points of '
                'infinite order on the rung; their provenance as traces of '
                'Galois-conjugate section pairs is NOT established here and is '
                'not asserted.',
            'rows': k0,
        }
        R.log('  k=0 proves-too-much: %d of %d rungs carry certified rank >= 1 '
              '-> %s' % (n_pos, len(k0ok),
                         out['PROVES_TOO_MUCH_k0_rung']['outcome']))

        # ---------------- RT-CONTROL-3 ---------------------------------
        R.log('RT-CONTROL-3: random-curve rank null, target n = %d per band at '
              'h ~ %s, alarm %ds' % (a.n_per_band, list(BANDS), a.alarm))
        t0 = time.time()
        bands = {}
        for h in BANDS:
            rows = []
            n_gen = 0
            per_band_budget = a.rtc3_time / len(BANDS)
            tb = time.time()
            while len(rows) < a.n_per_band:
                if time.time() - tb > per_band_budget:
                    break
                n_gen += 1
                mai, hh = random_curve_at_height(rng, h)
                if mai is None:
                    rows.append({'status': 'refused',
                                 'reason': 'no curve within tolerance of the '
                                           'target height in 400 tries'})
                    continue
                r = {'minimal_a_invariants': mai, 'naive_height': hh}
                pts = []
                try:
                    res = pari('alarm(%d, ellrank(ellinit(%s)))'
                               % (a.alarm, mai))
                    r['pari_ellrank_r_low'] = int(res[0])
                    r['pari_ellrank_r_high'] = int(res[1])
                    r['pari_ellrank_status'] = 'ok'
                    for P in res[3]:
                        try:
                            pts.append((F(str(pari('%s[1]' % P))),
                                        F(str(pari('%s[2]' % P)))))
                        except BaseException:
                            continue
                except BaseException as ex:
                    r['pari_ellrank_r_low'] = None
                    r['pari_ellrank_r_high'] = None
                    r['pari_ellrank_status'] = ('infrastructure_outcome: %s'
                                                % type(ex).__name__)
                pts = [p for p in pts
                       if ec.on_curve(ec.Qfield(), [F(x) for x in mai], p)]
                cert = ec.certify(mai, [[str(x), str(y)] for x, y in pts],
                                  max_prime=6000, max_good_primes=150,
                                  l_candidates=(2, 3, 5, 7, 11, 13, 17, 19))
                r['n_points_exhibited'] = len(pts)
                r['certified_rank_lower_bound'] = \
                    cert['certified_rank_lower_bound']
                r['status'] = ('measured' if r['pari_ellrank_status'] == 'ok'
                               else 'attempted_not_measured')
                r['reason'] = ('certified in exact arithmetic'
                               if r['status'] == 'measured'
                               else 'pari_ellrank_alarm')
                rows.append(r)
            meas = [r for r in rows if r.get('status') == 'measured']
            bands[str(h)] = {
                'target_h': h,
                'n_target': a.n_per_band,
                'n_generated': n_gen,
                'n_rows_attempted': len(rows),
                'n_measured': len(meas),
                'coverage_as_written': '%d/%d' % (len(meas), a.n_per_band),
                'coverage_fraction': len(meas) / a.n_per_band,
                'is_a_bound_not_a_distribution': len(meas) < a.n_per_band,
                'certified_rank_distribution': _dist(
                    [r['certified_rank_lower_bound'] for r in meas]),
                'n_at_rank_ge_1': sum(
                    1 for r in meas if r['certified_rank_lower_bound'] >= 1),
                'n_at_rank_ge_3': sum(
                    1 for r in meas if r['certified_rank_lower_bound'] >= 3),
                'rows': rows,
            }
            R.log('  band h~%d: %s measured, rank dist %s'
                  % (h, bands[str(h)]['coverage_as_written'],
                     bands[str(h)]['certified_rank_distribution']))
        out['RT_CONTROL_3'] = {
            'what': 'random elliptic curves at matched ICARM naive height, '
                    'same instrument and same alarm as every other search in '
                    'this task',
            'target_n_per_band': a.n_per_band,
            'alarm_seconds': a.alarm,
            'sampling': 'short Weierstrass y^2 = x^3 + a4 x + a6, a4 and a6 '
                        'drawn uniformly with random signs at sizes set by the '
                        'target height, accepted when the MINIMAL model\'s '
                        'naive height is within 0.75 of the target',
            'reporting_rule': 'BELOW n = 200 THIS IS A BOUND AND NOT A '
                              'DISTRIBUTION, and every band below target says '
                              'so in its own row',
            'bands': bands,
            'wall_clock_seconds': time.time() - t0,
        }

        out['certificate'] = {'kind': 'none',
                              'why': 'null controls; no discrete log and no '
                                     'factor-base relation is claimed'}
        with open(a.out, 'w') as fh:
            json.dump(out, fh, indent=1)
        R.log('wrote %s (%.2f MiB)'
              % (a.out, os.path.getsize(a.out) / (1 << 20)))
        R.result.update({
            'rt_control_2_rungs_measured': len(ok2),
            'rt_control_2_rung_rank_distribution':
                out['RT_CONTROL_2']['rung_certified_rank_distribution'],
            'rt_control_2_treatment_rank_distribution':
                out['RT_CONTROL_2']['treatment_certified_rank_distribution'],
            'proves_too_much_k0_outcome':
                out['PROVES_TOO_MUCH_k0_rung']['outcome'],
            'rt_control_3_bands': {k: {kk: vv for kk, vv in v.items()
                                       if kk != 'rows'}
                                   for k, v in bands.items()},
            'deliverable': a.out,
            'certificate': out['certificate'],
        })
    return 0


def _dist(vals):
    d = {}
    for v in vals:
        d[str(v)] = d.get(str(v), 0) + 1
    return dict(sorted(d.items(), key=lambda kv: (kv[0] == 'None', kv[0])))


if __name__ == '__main__':
    sys.exit(main())
