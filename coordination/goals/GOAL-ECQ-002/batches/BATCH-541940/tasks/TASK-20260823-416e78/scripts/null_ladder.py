#!/usr/bin/env python3
"""
THE REQUIRED NULL -- owed since BATCH-f2341e and, until this run, never run.

The premise under three batches of this campaign is that generic rank buys
something on the size axis.  That premise has never had a control.  Here is
one, and it is as tight as the construction allows:

  q is a monic degree-6 polynomial with k RATIONAL roots and (6-k)/2
  IRREDUCIBLE quadratic factors, chosen to satisfy the SAME admissibility
  condition (deg_x r = 4).  Everything about the object is held fixed -- the
  construction, p = q(x-T)q(x+T), the quartic r, the surface degree, the
  T-box, the minimal-model height code -- except the number of RATIONAL
  sections, which is 2k.  So the ladder

        k = 6  ->  12 sections  (generic rank >= 11: the treatment)
        k = 4  ->   8 sections
        k = 2  ->   4 sections
        k = 0  ->   0 sections  (generic rank 0 by construction)

  varies EXACTLY the parameter the premise says matters, and nothing else.

Rungs are compared at matched coefficient content: P2, the sum of squares of
the centred roots, is translation-invariant and scale-covariant of weight 2,
and is recorded for every family on every rung, so the comparison is a
regression of envelope on log P2 within rung rather than a difference of two
unmatched populations.

usage: null_ladder.py OUT.json [--per-rung 120] [--root-max 40]
       [--seed 20260823] [--time-budget 420]
"""
import argparse
import json
import math
import random
import sys
import time
from fractions import Fraction as F

import cypari

import admissible as ad
import measure
import exact_certify as ec
from certify_candidates import to_minimal, naive_height
from mestre import MestreFamily, poly_from_roots_and_quadratics

pari = cypari.pari
pari.allocatemem(2 ** 31, silent=True)


def build(roots, quads, k, idx):
    q, rr = poly_from_roots_and_quadratics(roots, quads)
    name = 'NULL-k%d-%03d' % (k, idx)
    fam = MestreFamily(q, rr, name, tuple_entries=None,
                       kind='null_ladder_k%d' % k)
    return fam


def gen_rung(k, n_want, root_max, rng, time_budget, t_start):
    """Generate admissible families with exactly k rational roots."""
    out = []
    tries = 0
    while len(out) < n_want and tries < 400 * n_want:
        if time.time() - t_start > time_budget:
            break
        tries += 1
        n_quad = (6 - k) // 2
        roots = rng.sample(range(-root_max, root_max + 1), k) if k else []
        quads_fixed = []
        ok = True
        for _ in range(n_quad - 1):
            s = rng.randint(-2 * root_max, 2 * root_max)
            n = rng.randint(-root_max * root_max, root_max * root_max)
            if not ad.quad_is_irreducible(s, n):
                ok = False
                break
            quads_fixed.append((s, n))
        if not ok:
            continue
        s_last = rng.randint(-2 * root_max, 2 * root_max)
        for n_last in ad.solve_last_n(roots, quads_fixed, s_last):
            if not ad.quad_is_irreducible(s_last, n_last):
                continue
            quads = quads_fixed + [(s_last, n_last)]
            # the quadratics must be distinct and share no root with a rational
            if len(set(quads)) != len(quads):
                continue
            fam = build(roots, quads, k, len(out))
            if fam.deg_x_r != 4:
                continue
            if len(fam.rational_roots) != k:
                continue
            out.append(fam)
            break
    return out, tries


def certify_best(fam, res, alarm=20):
    """Exact certified rank at the family's envelope argmin, via ellrank search."""
    t0 = F(res['envelope_argmin_t'])
    quart = fam.quartic_at(t0)
    secs = fam.sections_at(t0)
    if secs:
        mp = measure.measure_points(t0, quart, secs)
        if mp is None:
            return None
        ai, pts = mp
        tm = to_minimal(ai, pts)
        if tm is None:
            return None
        mai, mpts, _ = tm
    else:
        mai = measure._jacobian_ai(quart)
        r = pari('my(v); E=ellminimalmodel(ellinit(%s),&v); E[1..5]' % (mai,))
        mai = [int(x) for x in r]
        mpts = []
    extra = []
    status = 'ok'
    try:
        r = pari('alarm(%d, ellrank(ellinit(%s)))' % (alarm, mai))
        rl, rh = int(r[0]), int(r[1])
        for P in r[3]:
            extra.append((F(str(pari('%s[1]' % P))), F(str(pari('%s[2]' % P)))))
    except BaseException as e:
        rl = rh = None
        status = 'infrastructure_outcome: %s' % type(e).__name__
    allpts = list(mpts) + [p for p in extra if p not in mpts]
    allpts = [p for p in allpts
              if ec.on_curve(ec.Qfield(), [F(a) for a in mai], p)]
    cert = ec.certify(mai, [[str(x), str(y)] for x, y in allpts],
                      max_prime=6000, max_good_primes=150,
                      l_candidates=(2, 3, 5, 7, 11, 13, 17, 19))
    h, c4, c6 = naive_height(mai)
    return {'t': str(t0), 'minimal_a_invariants': mai, 'naive_height': h,
            'certified_rank_lower_bound': cert['certified_rank_lower_bound'],
            'n_points_submitted': len(allpts),
            'pari_ellrank_r_low': rl, 'pari_ellrank_r_high': rh,
            'pari_ellrank_status': status}


def summarise(rows):
    import statistics as st
    e = [r['measured_envelope_min_naive_height'] for r in rows]
    if not e:
        return None
    xs = [math.log(float(r['content_P2'])) for r in rows if float(r['content_P2']) > 0]
    ys = [r['measured_envelope_min_naive_height'] for r in rows
          if float(r['content_P2']) > 0]
    return {
        'n': len(rows),
        'min_envelope': min(e), 'median_envelope': st.median(e),
        'mean_envelope': st.fmean(e),
        'max_envelope': max(e),
        'envelope_vs_log_content_P2_fit': measure.fit(xs, ys),
        'median_log_content_P2': st.median(xs) if xs else None,
        'median_shioda_tate_ceiling':
            st.median([r['surface']['shioda_tate_ceiling'] for r in rows
                       if r['surface'].get('shioda_tate_ceiling') is not None])
            if any(r['surface'].get('shioda_tate_ceiling') is not None for r in rows)
            else None,
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('out')
    ap.add_argument('--treatment-scan', default=None,
                    help='scan json; the k=6 rung is taken from it if given')
    ap.add_argument('--per-rung', type=int, default=120)
    ap.add_argument('--root-max', type=int, default=40)
    ap.add_argument('--n-certify', type=int, default=12)
    ap.add_argument('--seed', type=int, default=20260823)
    ap.add_argument('--time-budget', type=float, default=420.0)
    a = ap.parse_args(argv)
    rng = random.Random(a.seed)
    t_start = time.time()

    rungs = {}
    gen_stats = {}
    for k in (4, 2, 0):
        fams, tries = gen_rung(k, a.per_rung, a.root_max, rng,
                               a.time_budget * 0.5, t_start)
        gen_stats['k%d' % k] = {'n_generated': len(fams),
                                'n_parameter_draws': tries}
        rows = []
        for fam in fams:
            r = measure.measure(fam)
            if r.get('status') != 'measured':
                continue
            r['rung_k'] = k
            r['n_rational_roots'] = k
            rows.append(r)
        rungs['k%d' % k] = rows

    # treatment rung
    if a.treatment_scan:
        scan = json.load(open(a.treatment_scan))
        tr = [f for f in scan['families']]
        rng2 = random.Random(a.seed + 1)
        tr = rng2.sample(tr, min(a.per_rung, len(tr)))
        for r in tr:
            r['rung_k'] = 6
        rungs['k6'] = tr

    # exact certification of a sample from each rung, at its envelope argmin
    certs = {}
    for key, rows in rungs.items():
        k = int(key[1:])
        sel = sorted(rows, key=lambda r: r['measured_envelope_min_naive_height'])
        sel = sel[:a.n_certify]
        cs = []
        for r in sel:
            if time.time() - t_start > a.time_budget * 1.6:
                break
            if k == 6:
                fam = measure.family_from_tuple(r['tuple'], name=r['family'])
            else:
                fam = _rebuild_from_q(r)   # recovers the rational roots
            try:
                c = certify_best(fam, r)
            except BaseException as e:
                c = {'error': '%s: %s' % (type(e).__name__, e)}
            if c:
                c['family'] = r['family']
                c['measured_envelope_min_naive_height'] = \
                    r['measured_envelope_min_naive_height']
                c['content_P2'] = r['content_P2']
                c['shioda_tate_ceiling'] = r['surface'].get('shioda_tate_ceiling')
                cs.append(c)
        certs[key] = cs

    out = {
        'what': 'THE REQUIRED NULL: a rank ladder of Mestre-shape families '
                'differing only in the number of RATIONAL sections',
        'task_id': 'TASK-20260823-416e78',
        'seed': a.seed,
        't_box': measure.T_BOX_DESC,
        'generation': gen_stats,
        'rung_summary': {k: summarise(v) for k, v in rungs.items()},
        'certified_at_envelope_argmin': certs,
        'rungs': {k: [{kk: vv for kk, vv in r.items()
                       if kk != 'lower_envelope_points'} for r in v]
                  for k, v in rungs.items()},
    }
    json.dump(out, open(a.out, 'w'), indent=1)
    for k in ('k6', 'k4', 'k2', 'k0'):
        s = out['rung_summary'].get(k)
        if not s:
            continue
        f = s['envelope_vs_log_content_P2_fit'] or {}
        print('%s n=%4d  min env %8.3f  median %8.3f  fit env = %.2f + %.2f*log P2 '
              '(R2=%.3f)  median log P2 %.2f  median ST ceiling %s'
              % (k, s['n'], s['min_envelope'], s['median_envelope'],
                 f.get('intercept', float('nan')), f.get('slope', float('nan')),
                 f.get('r_squared') or float('nan'),
                 s['median_log_content_P2'], s['median_shioda_tate_ceiling']))
        cs = certs.get(k, [])
        if cs:
            best = [c for c in cs if 'certified_rank_lower_bound' in c]
            if best:
                print('     certified ranks at envelope argmin: %s'
                      % sorted((c['certified_rank_lower_bound'] for c in best),
                               reverse=True))
    return 0


def _rebuild_from_q(r):
    """Rebuild a null family from its recorded q, recovering rational roots."""
    q = [F(c) for c in r['q_coefficients_ascending']]
    roots = []
    # integer roots divide the constant term (q is monic with integer coeffs)
    c0 = q[0]
    if c0 == 0:
        roots.append(F(0))
    n0 = abs(int(c0)) if c0 != 0 else 0
    cands = set()
    if n0:
        for d in range(1, int(math.isqrt(n0)) + 1):
            if n0 % d == 0:
                cands |= {d, -d, n0 // d, -(n0 // d)}
    for c in sorted(cands):
        v = sum(q[i] * F(c) ** i for i in range(len(q)))
        if v == 0:
            roots.append(F(c))
    return MestreFamily(q, roots, r['family'], kind=r['kind'])


if __name__ == '__main__':
    sys.exit(main())
