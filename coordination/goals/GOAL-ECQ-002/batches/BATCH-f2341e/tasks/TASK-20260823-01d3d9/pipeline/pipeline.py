#!/usr/bin/env python3
"""
FAMILY-AGNOSTIC pipeline: Q(t) family + parameter box -> small, high-rank,
CERTIFIED curves over Q + ICARM-format submission records.

Stages
------
  1. specialise   families.Family.specialise at every parameter point of the box
  2. order        Mestre-Nagao statistic (HEURISTIC ORDERING ONLY -- it never
                  certifies anything; a random-sample control of the same size
                  is run beside it so its efficiency is measured, not assumed)
  3. search       PARI ellrank on the top-k candidates, under an alarm() guard,
                  to PRODUCE candidate points.  A timeout here is an
                  infrastructure outcome and is recorded as such, never as
                  evidence about the curve's rank.
  4. certify      exact_certify.certify -- stdlib-only, exact, independent of
                  stage 3: on-curve in Fractions, non-torsion by Mazur,
                  independence by mod-l reduction.  THE ONLY SOURCE OF A RANK
                  NUMBER IN THIS PIPELINE IS THIS STAGE.
  5. measure      minimal model, naive height, Faltings height, conductor
                  (icarm_invariants; definitions pinned by reproduce_icarm.py)
  6. emit         ICARM-format submission record.  NOTHING IS SENT ANYWHERE.
                  Submission is a Coordinator decision after review.

Entry point
-----------
    python3 pipeline.py --family FAMILY.json \
                        --box '{"t": {"num_min": -12, "num_max": 12, "den_max": 2}}' \
                        --top-k 12 --control 12 --seed 20260823 \
                        --out result.json

  --family   path to a family spec (see families.py docstring)
  --box      JSON parameter box; per parameter either
             {"num_min":a,"num_max":b,"den_max":d} or {"values":["1","3/2"]}
  --top-k    how many Mestre-Nagao-ranked candidates go to descent+certification
  --control  how many UNIFORMLY RANDOM candidates from the same box do too
  --seed     RNG seed for the control (recorded; the rest is deterministic)
  --rank-time-limit  PARI ellrank alarm, seconds (default 20)

Everything reported is either an exactly certified quantity or is explicitly
labelled heuristic / numerical.
"""
import argparse
import json
import math
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import cypari  # noqa: E402

import exact_certify  # noqa: E402
import icarm_invariants as inv  # noqa: E402
from families import Family, parameter_box  # noqa: E402

pari = cypari.pari
pari.allocatemem(2 ** 32, silent=True)

MN_PRIME_BOUND = 500


def mestre_nagao(a_invariants, bound=MN_PRIME_BOUND):
    """S(N) = sum_{good p <= N} -a_p log(p)/p.

    A HEURISTIC ORDERING STATISTIC.  Heuristically S(N) ~ rank * log N, so a
    larger S suggests a larger rank; it is never part of any certified claim.
    Returns (S, S/log N, n_primes_used).
    """
    ai = [int(a) for a in a_invariants]
    disc = exact_certify.discriminant(ai)
    E = pari('ellinit(%s)' % (ai,))
    s = 0.0
    n = 0
    for p in exact_certify.primes_upto(bound):
        if disc % p == 0:
            continue
        ap = int(pari('ellap(%s,%d)' % (E, p)))
        s += -ap * math.log(p) / p
        n += 1
    return s, s / math.log(bound), n


def ellrank_points(a_invariants, time_limit=20):
    """Candidate points from PARI ellrank.  Search only -- never a certificate.

    Returns dict with r_low, r_high, points (strings), timed_out.
    """
    ai = [int(a) for a in a_invariants]
    t0 = time.time()
    try:
        r = pari('alarm(%d,ellrank(ellinit(%s)))' % (time_limit, ai))
        out = {'pari_r_low': int(r[0]), 'pari_r_high': int(r[1]),
               'points': [[str(c) for c in pt] for pt in r[3]],
               'seconds': time.time() - t0}
    except BaseException as e:   # AlarmInterrupt is not an Exception
        out = {'pari_r_low': -1, 'pari_r_high': -1, 'points': [],
               'seconds': time.time() - t0,
               'guard': '%s: %s' % (type(e).__name__, e)}
    out['timed_out'] = out['pari_r_low'] < 0
    return out


def transport_to_minimal(a_invariants, points, time_limit=30):
    """Move points onto the minimal model (PARI ellchangepoint)."""
    ai = [int(a) for a in a_invariants]
    try:
        r = pari('alarm(%d, my(v); my(F=ellminimalmodel(ellinit(%s),&v)); '
                 '[F[1],F[2],F[3],F[4],F[5],v])' % (time_limit, ai))
    except BaseException as e:   # AlarmInterrupt is not an Exception
        raise inv.InvariantTimeout('ellminimalmodel guard fired (%s: %s)'
                                   % (type(e).__name__, e))
    mai = [int(r[i]) for i in range(5)]
    v = r[5]
    mpts = []
    for x, y in points:
        q = pari.ellchangepoint(pari('[%s,%s]' % (x, y)), v)
        mpts.append([str(q[0]), str(q[1])])
    return mai, mpts


def numerical_regulator(a_invariants, points, precision=90):
    """NUMERICAL (not exact) height regulator.  Reported for the ICARM record
    only; the rank claim rests on exact_certify, never on this number."""
    if not points:
        return None
    pari('default(realprecision,%d)' % precision)
    E = pari('ellinit(%s)' % ([int(a) for a in a_invariants],))
    vec = '[' + ','.join('[%s,%s]' % (x, y) for x, y in points) + ']'
    try:
        return str(pari('matdet(ellheightmatrix(%s,%s))' % (E, vec)))
    except Exception as e:                                   # pragma: no cover
        return 'ERROR: %s' % e


def evaluate_candidate(fam, values, rank_time_limit=20, want_record=True):
    """Full stages 1,2,3,4,5 for one parameter point."""
    sp = fam.specialise(values)
    rec = {'params': {k: str(v) for k, v in values.items()}}
    if sp is None:
        rec['status'] = 'singular_specialisation'
        return rec
    ai = sp['a_invariants']
    if exact_certify.discriminant(ai) == 0:
        rec['status'] = 'singular_specialisation'
        return rec
    rec['integral_a_invariants'] = [str(a) for a in ai]
    rec['scale_u'] = sp['scale_u']
    s, sn, npr = mestre_nagao(ai)
    rec['mestre_nagao'] = {'S': s, 'S_over_logN': sn, 'prime_bound': MN_PRIME_BOUND,
                           'n_primes': npr, 'role': 'heuristic ordering only'}
    try:
        minv = inv.invariants(ai)
    except inv.InvariantTimeout as e:
        rec['status'] = 'infrastructure_timeout'
        rec['infrastructure_note'] = str(e)
        return rec
    rec['invariants'] = minv
    rec['status'] = 'measured'
    if not want_record:
        return rec

    # ---- stage 3: candidate points (search, never certification) --------
    er = ellrank_points(ai, rank_time_limit)
    rec['pari_search'] = er
    cand = {tuple(p) for p in er['points']}
    cand |= {tuple(p) for p in sp['points']}          # the family's own sections
    cand = [list(p) for p in sorted(cand)]
    if er['timed_out']:
        rec['infrastructure_note'] = ('PARI ellrank timed out after %ds -- '
                                      'infrastructure outcome, not evidence '
                                      'about the rank' % rank_time_limit)
    if not cand:
        rec['certificate'] = {'certified_rank_lower_bound': 0,
                              'note': 'no candidate points produced'}
        return rec

    # ---- stage 4: EXACT certification on the MINIMAL model ---------------
    try:
        mai, mpts = transport_to_minimal(ai, cand)
    except inv.InvariantTimeout as e:
        rec['status'] = 'infrastructure_timeout'
        rec['infrastructure_note'] = str(e)
        return rec
    cert = exact_certify.certify(mai, mpts)
    if 0 < cert['certified_rank_lower_bound'] < cert.get('n_points_non_torsion', 0):
        cert2 = exact_certify.certify(mai, mpts, max_prime=8000,
                                      max_good_primes=250,
                                      l_candidates=(2, 3, 5, 7, 11, 13, 17, 19))
        if cert2['certified_rank_lower_bound'] > cert['certified_rank_lower_bound']:
            cert = cert2
            cert['certifier_escalated'] = True
    rec['certificate'] = cert
    rec['certified_rank'] = cert['certified_rank_lower_bound']
    # the regulator is reported for the ICARM record only, and must be taken
    # over the CERTIFIED INDEPENDENT subset: over all exhibited points it is
    # ~0 whenever the search returned dependent points, which says nothing.
    ind = cert.get('independence', {}).get('independent_point_indices', [])
    cert_pts = [mpts[i] for i in ind] or mpts
    rec['numerical_regulator'] = numerical_regulator(mai, cert_pts)
    rec['numerical_regulator_over'] = 'certified independent subset'
    rec['submission_record'] = icarm_record(mai, mpts, cert, minv, fam, values,
                                            rec['numerical_regulator'])
    return rec


def icarm_record(mai, mpts, cert, minv, fam, values, regulator):
    """ICARM-format submission record.  PRODUCED ONLY -- never transmitted."""
    return {
        'ainvs': [str(a) for a in mai],
        'curve_key': minv['curve_key'],
        'rank_lower_bound': cert['certified_rank_lower_bound'],
        'naive_height': minv['naive_height'],
        'faltings_height': minv['faltings_height'],
        'conductor': minv.get('conductor'),
        'discriminant': minv['discriminant'],
        'regulator': regulator,
        'regulator_is_numerical': True,
        'points': [mpts[i] for i in
                   cert.get('independence', {}).get('independent_point_indices', [])]
                  or mpts,
        'all_exhibited_points': mpts,
        'provenance': {
            'family': fam.name,
            'family_source': fam.source,
            'parameters': {k: str(v) for k, v in values.items()},
            'rank_certified_by': 'exact_certify.py (exact, stdlib-only, '
                                 'mod-l reduction independence)',
            'not_submitted': True,
        },
    }


def run(family_path, box, top_k, control, seed, rank_time_limit, out_path,
        measure_all=True):
    fam = Family.load(family_path)
    pts = parameter_box(box)
    t0 = time.time()

    # ---- stage 1+2 over the whole box (cheap: no descent) ---------------
    screened = []
    for v in pts:
        rec = evaluate_candidate(fam, v, want_record=False)
        screened.append(rec)
    ok = [r for r in screened if r['status'] == 'measured']
    ranked = sorted(ok, key=lambda r: -r['mestre_nagao']['S'])

    rng = random.Random(seed)
    ctrl_idx = rng.sample(range(len(ok)), min(control, len(ok)))
    ctrl = [ok[i] for i in ctrl_idx]

    def full(recs, arm):
        out = []
        for r in recs:
            vals = {k: r['params'][k] for k in r['params']}
            fr = evaluate_candidate(fam, vals, rank_time_limit)
            fr['arm'] = arm
            out.append(fr)
        return out

    mn_arm = full(ranked[:top_k], 'mestre_nagao_top')
    ct_arm = full(ctrl, 'uniform_random_control')

    def summarise(arm):
        rr = [a.get('certified_rank', 0) for a in arm]
        hh = [a['invariants']['naive_height'] for a in arm if 'invariants' in a]
        return {
            'n': len(arm),
            'certified_ranks': rr,
            'max_certified_rank': max(rr) if rr else None,
            'mean_certified_rank': (sum(rr) / len(rr)) if rr else None,
            'min_naive_height': min(hh) if hh else None,
            'n_infrastructure_timeouts': sum(1 for a in arm
                                             if a.get('status') == 'infrastructure_timeout'
                                             or a.get('pari_search', {}).get('timed_out')),
        }

    result = {
        'family': {'name': fam.name, 'source': fam.source,
                   'claimed_generic_rank': fam.claimed_generic_rank,
                   'spec': fam.spec},
        'box': box,
        'seed': seed,
        'rank_time_limit_seconds': rank_time_limit,
        'n_parameter_points': len(pts),
        'n_nonsingular': len(ok),
        'screening': [{'params': r['params'],
                       'S': r.get('mestre_nagao', {}).get('S'),
                       'naive_height': r.get('invariants', {}).get('naive_height'),
                       'status': r['status']} for r in screened],
        'arms': {'mestre_nagao_top': mn_arm, 'uniform_random_control': ct_arm},
        'arm_summary': {'mestre_nagao_top': summarise(mn_arm),
                        'uniform_random_control': summarise(ct_arm)},
        'wall_clock_seconds': time.time() - t0,
        'nothing_submitted': True,
    }
    if out_path:
        json.dump(result, open(out_path, 'w'), indent=1)
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--family', required=True)
    ap.add_argument('--box', required=True)
    ap.add_argument('--top-k', type=int, default=10)
    ap.add_argument('--control', type=int, default=10)
    ap.add_argument('--seed', type=int, default=20260823)
    ap.add_argument('--rank-time-limit', type=int, default=20)
    ap.add_argument('--out', default=None)
    a = ap.parse_args(argv)
    res = run(a.family, json.loads(a.box), a.top_k, a.control, a.seed,
              a.rank_time_limit, a.out)
    s = res['arm_summary']
    print('family              : %s (claimed generic rank %s)'
          % (res['family']['name'], res['family']['claimed_generic_rank']))
    print('parameter points    : %d (%d non-singular)'
          % (res['n_parameter_points'], res['n_nonsingular']))
    for arm in ('mestre_nagao_top', 'uniform_random_control'):
        print('%-22s: n=%d  max certified rank=%s  mean=%.3f  min naive height=%.4f'
              % (arm, s[arm]['n'], s[arm]['max_certified_rank'],
                 s[arm]['mean_certified_rank'] or 0.0,
                 s[arm]['min_naive_height'] or float('nan')))
    print('wall clock          : %.1fs' % res['wall_clock_seconds'])
    return res


if __name__ == '__main__':
    main()
