#!/usr/bin/env python3
"""
Measure one Mestre-shape family: the lower envelope of minimal-model naive
height over a declared T-box, a SEPARATE least-squares fit on each of the two
arms of the envelope, the crossover, and the family's own surface degree and
Shioda-Tate ceiling.

The two arms are fitted SEPARATELY and never with one line across the V.
Fitting a single line across a piecewise-linear envelope was the BATCH-da59ec
producer's error (the resulting vertex sat on its own box edge); the
BATCH-da59ec red team's structural reading -- flat small-|t| arm set by the
family's coefficient content, steep large-|t| arm of slope 12d forced by
Shioda-Tate -- is the law being measured here, not assumed.
"""
import math
from fractions import Fraction as F

import cypari

import surface
from admissible import centred_content_from_poly
from mestre import (MestreFamily, quartic_IJ, quartic_to_weierstrass,
                    integral_model, on_weierstrass, poly_from_roots_and_quadratics)

pari = cypari.pari
pari.allocatemem(2 ** 31, silent=True)

# ---------------------------------------------------------------------------
# THE DECLARED T-BOX.  Frozen here before any tuple is scanned.
# r(x,T) is even in T (p = q(x-T)q(x+T) is), so h(-t) = h(t) exactly and only
# t > 0 is enumerated.  The large integers are present ONLY so that the steep
# arm of the envelope is inside the box: without them the fitted vertex would
# again sit on the box edge.
# ---------------------------------------------------------------------------
SMALL_T = [F(n, d) for d in (1, 2, 3) for n in range(1, 31)
           if math.gcd(n, d) == 1]
LARGE_T = [F(n) for n in (40, 60, 90, 130, 200, 300, 500, 800)]
T_BOX = sorted(set(SMALL_T + LARGE_T))
T_BOX_DESC = ('t = n/d, 1<=n<=30, d in {1,2,3}, gcd(n,d)=1, plus '
              't in {40,60,90,130,200,300,500,800}; t>0 only because '
              'h(-t)=h(t) identically (r is even in T)')


def _jacobian_ai(quart):
    I, J = quartic_IJ(quart)
    den = 1
    for z in (I, J):
        den = den * z.denominator // math.gcd(den, z.denominator)
    return [0, 0, 0, int(-27 * I * den ** 4), int(-27 * J * den ** 6)]


def _disc(ai):
    a1, a2, a3, a4, a6 = [int(x) for x in ai]
    b2 = a1 * a1 + 4 * a2
    b4 = 2 * a4 + a1 * a3
    b6 = a3 * a3 + 4 * a6
    b8 = a1 * a1 * a6 + 4 * a2 * a6 - a1 * a3 * a4 + a2 * a3 * a3 - a4 * a4
    return -b2 * b2 * b8 - 8 * b4 ** 3 - 27 * b6 * b6 + 9 * b2 * b4 * b6


def minimal_invariants(ai):
    """(c4, c6, naive_height, minimal a-invariants) via PARI ellminimalmodel."""
    r = pari('ellminimalmodel(ellinit(%s))[1..5]' % ([int(x) for x in ai],))
    mai = [int(x) for x in r]
    E = pari('ellinit(%s)' % (mai,))
    c4 = int(pari('%s.c4' % E))
    c6 = int(pari('%s.c6' % E))
    h = math.log(max(abs(c4) ** 3, c6 * c6))
    return c4, c6, h, mai


def measure_points(t0, quart, secs):
    """Weierstrass model carrying the sections, plus the mapped points."""
    base = None
    for i, (u0, v0) in enumerate(secs):
        if v0 != 0:
            base = i
            break
    if base is None:
        return None
    u0, v0 = secs[base]
    ai, mp = quartic_to_weierstrass(quart, u0, v0)
    pts = []
    seen = set()
    for j, (u, v) in enumerate(secs):
        if j == base:
            continue
        P = mp(u, v)
        if P is None:
            continue
        if not on_weierstrass(ai, P):
            return None
        k = (P[0], P[1])
        if k in seen:
            continue
        seen.add(k)
        pts.append(P)
    aint, ipts = integral_model(ai, pts)
    if _disc(aint) == 0:
        return None
    return aint, ipts


def fit(xs, ys):
    n = len(xs)
    if n < 2:
        return None
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx == 0:
        return None
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    a = my - b * mx
    sst = sum((y - my) ** 2 for y in ys)
    ssr = sum((y - (a + b * x)) ** 2 for x, y in zip(xs, ys))
    return {'intercept': a, 'slope': b, 'n': n, 'sse': ssr,
            'r_squared': (1 - ssr / sst) if sst else None}


def two_arm_fit(env):
    """env: list of (X, Y) lower-envelope points, sorted by X.

    Segmented least squares with a free breakpoint: the two arms are fitted
    INDEPENDENTLY and the breakpoint minimises the total SSE.
    """
    if len(env) < 6:
        return None
    xs = [p[0] for p in env]
    ys = [p[1] for p in env]
    best = None
    for k in range(3, len(env) - 2):
        f1 = fit(xs[:k], ys[:k])
        f2 = fit(xs[k:], ys[k:])
        if not f1 or not f2:
            continue
        sse = f1['sse'] + f2['sse']
        if best is None or sse < best[0]:
            best = (sse, k, f1, f2)
    if best is None:
        return None
    sse, k, f1, f2 = best
    cross = None
    if f2['slope'] != f1['slope']:
        cross = (f1['intercept'] - f2['intercept']) / (f2['slope'] - f1['slope'])
    return {
        'breakpoint_index': k,
        'breakpoint_log_param_size_between': [xs[k - 1], xs[k]],
        'flat_arm': {'intercept': f1['intercept'], 'slope': f1['slope'],
                     'n': f1['n'], 'r_squared': f1['r_squared']},
        'steep_arm': {'intercept': f2['intercept'], 'slope': f2['slope'],
                      'n': f2['n'], 'r_squared': f2['r_squared']},
        'crossover_log_param_size': cross,
        'total_sse': sse,
    }


def measure(fam, t_box=None, want_surface=True, keep_rows=False):
    """Measure one family.  Returns a dict of OBSERVATIONS only."""
    t_box = t_box or T_BOX
    rows = []
    for t0 in t_box:
        quart = fam.quartic_at(t0)
        ai = _jacobian_ai(quart)
        if _disc(ai) == 0:
            continue
        try:
            c4, c6, h, mai = minimal_invariants(ai)
        except BaseException as e:                     # PARI failure
            rows.append({'t': str(t0), 'status': 'infrastructure_error',
                         'note': '%s: %s' % (type(e).__name__, e)})
            continue
        H = max(abs(t0.numerator), t0.denominator)
        rows.append({'t': str(t0), 'status': 'measured',
                     'param_size_H': H, 'log_param_size': math.log(H),
                     'naive_height': h, 'curve_key': '%d:%d' % (c4, c6)})
    ok = [r for r in rows if r['status'] == 'measured']
    if not ok:
        return {'family': fam.name, 'status': 'no_measurable_fibre',
                'n_rows': len(rows)}
    env = {}
    for r in ok:
        x = r['log_param_size']
        if x not in env or r['naive_height'] < env[x][0]:
            env[x] = (r['naive_height'], r['t'])
    envpts = sorted((x, v[0], v[1]) for x, v in env.items())
    _c2, _c3, _c5, _phi = centred_content_from_poly(fam.q)
    best = min(ok, key=lambda r: r['naive_height'])
    out = {
        'family': fam.name,
        'kind': fam.kind,
        'tuple': fam.tuple_entries,
        'q_coefficients_ascending': [str(c) for c in fam.q],
        'n_rational_roots': len(fam.rational_roots),
        'n_sections': len(fam.sections),
        'generic_rank_lower_bound_claimed': max(0, len(fam.sections) - 1),
        'deg_x_r': fam.deg_x_r,
        'content_P2': float(_c2),
        'content_P2_exact': str(_c2),
        'admissibility_phi': str(_phi),
        'status': 'measured',
        'n_measured': len(ok),
        'n_infrastructure_errors': len(rows) - len(ok),
        'measured_envelope_min_naive_height': best['naive_height'],
        'envelope_argmin_t': best['t'],
        'envelope_argmin_curve_key': best['curve_key'],
        'median_naive_height': sorted(r['naive_height'] for r in ok)[len(ok) // 2],
        'max_naive_height': max(r['naive_height'] for r in ok),
        'lower_envelope_points': [{'log_param_size': x, 'naive_height': y,
                                   't': t} for x, y, t in envpts],
        'two_arm_fit': two_arm_fit([(x, y) for x, y, _ in envpts]),
    }
    if keep_rows:
        out['rows'] = rows
    if want_surface:
        try:
            out['surface'] = surface.analyse(fam.r_coeff_polys())
        except BaseException as e:
            out['surface'] = {'error': '%s: %s' % (type(e).__name__, e)}
        s = out['surface']
        f = out['two_arm_fit']
        if f and s.get('surface_degree_d'):
            out['steep_slope_vs_12d'] = {
                'measured_steep_slope': f['steep_arm']['slope'],
                'forced_12d': 12 * s['surface_degree_d'],
                'ratio': f['steep_arm']['slope'] / (12 * s['surface_degree_d']),
            }
    return out


def family_from_tuple(entries, name=None, perturb_pairs=0):
    """Mestre family from six integers.

    perturb_pairs = k replaces the k lowest disjoint pairs (a_{2i}, a_{2i+1})
    of the sorted tuple by the monic quadratic x^2 - (a+b)x + (ab+1), whose
    discriminant (a-b)^2 - 4 is a perfect square only for |a-b| = 2.  This is
    the NULL LADDER: the coefficient content of q moves by 1 in one product
    while two rational sections are destroyed, so generic rank drops by 2 with
    the shape and the coefficient content held essentially fixed.
    """
    e = sorted(int(x) for x in entries)
    assert len(e) == 6 and len(set(e)) == 6
    pairs = [(e[0], e[1]), (e[2], e[3]), (e[4], e[5])]
    quads, roots = [], []
    for i, (a, b) in enumerate(pairs):
        if i < perturb_pairs:
            assert abs(a - b) != 2, 'pair would stay reducible'
            quads.append((a + b, a * b + 1))
        else:
            roots += [a, b]
    q, rr = poly_from_roots_and_quadratics(roots, quads)
    nm = name or ('MESTRE-%s' % ','.join(str(x) for x in e))
    if perturb_pairs:
        nm += '/NULL%d' % (6 - 2 * perturb_pairs)
    return MestreFamily(q, rr, nm, tuple_entries=e,
                        kind='mestre' if perturb_pairs == 0
                        else 'null_ladder_k%d' % (6 - 2 * perturb_pairs))
