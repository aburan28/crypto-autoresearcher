#!/usr/bin/env python3
"""STEP 2b -- independent cross-check of the quartic->Weierstrass conversion, and
measurement of what MINIMALISATION strips.

(1) CROSS-CHECK: for each t0, build the specialised quartic and let PARI's
    ellfromeqn produce a Weierstrass model of it, independently of step 2's
    I/J computation.  Compare minimal models (c4:c6 curve_key) with the
    specialisation of step 2's a_invariants.  Agreement on the curve_key is the
    check; it is the same invariant the BATCH-f2341e reproduction gate used.
(2) MINIMALISATION: report a-invariant / c4 / c6 sizes BEFORE and AFTER
    ellminimalmodel, plus the naive height of both, for a range of t0.
"""
import json, math, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
PIPE = ('/home/user/crypto-autoresearcher/coordination/goals/GOAL-ECQ-002/batches/'
        'BATCH-f2341e/tasks/TASK-20260823-01d3d9/pipeline')
sys.path.insert(0, PIPE); sys.path.insert(0, HERE)
from fractions import Fraction as F
import cypari
from families import Family
import icarm_invariants as inv
from step1_nagao_identity import parse_poly_in_t, SRC
import json as _json

pari = cypari.pari

def peval(p, t):
    return sum(c * F(t) ** i for i, c in enumerate(p))

def digits(n):
    return len(str(abs(int(n))))

def main(family_json, out_json, ts):
    db = _json.load(open(SRC))
    fam_rec = next(x for x in db['families'] if x['id'] == 'NAGAO-1994')
    wc = fam_rec['weierstrass_coefficients_in_t']
    Q = {k: parse_poly_in_t(wc[k]) for k in ('c4', 'c3', 'c2', 'c1', 'c0')}
    fam = Family.load(family_json)

    rows = []
    for t0 in ts:
        t0 = F(t0)
        sp = fam.specialise({'t': t0})
        ai = sp['a_invariants']
        # naive height of the NON-minimal integral model
        E0 = pari('ellinit(%s)' % (ai,))
        c4_0, c6_0 = int(pari('%s.c4' % E0)), int(pari('%s.c6' % E0))
        naive_before = math.log(max(abs(c4_0) ** 3, c6_0 * c6_0))
        try:
            m = inv.invariants(ai, time_limit=25, want_conductor=False)
        except inv.InvariantTimeout as ex:
            rows.append({'t': str(t0), 'status': 'infrastructure_timeout', 'note': str(ex)})
            continue
        # independent route: PARI ellfromeqn on the specialised quartic
        a, b, c, d, e = (peval(Q[k], t0) for k in ('c4', 'c3', 'c2', 'c1', 'c0'))
        L = 1
        for v in (a, b, c, d, e):
            L = L * v.denominator // math.gcd(L, v.denominator)
        # scale y^2 = q(x) by L^2 : (L^2 y)^2 = L^2 * ... -> use exact ints via L^4 substitution
        # y^2 = q(x); put x -> x/L, y -> y/L^2 : y^2 = L^4 q(x/L) has integer coeffs
        A4 = int(a * L ** 0); # a * L^4 / L^4
        coeffs = [int(a), int(b * L), int(c * L ** 2), int(d * L ** 3), int(e * L ** 4)]
        eq = "y^2 - (%d*x^4 + %d*x^3 + %d*x^2 + %d*x + %d)" % tuple(coeffs)
        try:
            ai2 = [int(x) for x in pari('ellfromeqn(%s)' % eq)]
            m2 = inv.invariants(ai2, time_limit=25, want_conductor=False)
            key2, ok2 = m2['curve_key'], (m2['curve_key'] == m['curve_key'])
        except BaseException as ex:
            key2, ok2 = None, None
        rows.append({
            't': str(t0), 'status': 'measured',
            'a_invariants_before_minimalisation': [str(x) for x in ai],
            'a_invariant_digits_before': [digits(x) for x in ai],
            'c4_digits_before': digits(c4_0), 'c6_digits_before': digits(c6_0),
            'naive_height_before_minimalisation': naive_before,
            'minimal_a_invariants': [str(x) for x in m['minimal_a_invariants']],
            'c4_digits_after': digits(int(m['c4'])), 'c6_digits_after': digits(int(m['c6'])),
            'curve_key': m['curve_key'],
            'naive_height_after_minimalisation': m['naive_height'],
            'naive_height_stripped_by_minimalisation': naive_before - m['naive_height'],
            'faltings_height': m['faltings_height'],
            'discriminant_digits': digits(int(m['discriminant'])),
            'pari_ellfromeqn_curve_key': key2,
            'crosscheck_agrees': ok2,
        })
        print('t=%-6s  h_before=%9.3f  h_after=%9.3f  stripped=%8.3f  xcheck=%s'
              % (t0, naive_before, m['naive_height'],
                 naive_before - m['naive_height'], ok2))
    ok = [r for r in rows if r['status'] == 'measured']
    out = {'step': '2b', 'family_spec': family_json,
           'n_t_values': len(ts), 'n_measured': len(ok),
           'crosscheck_agreements': sum(1 for r in ok if r['crosscheck_agrees'] is True),
           'crosscheck_disagreements': sum(1 for r in ok if r['crosscheck_agrees'] is False),
           'crosscheck_unavailable': sum(1 for r in ok if r['crosscheck_agrees'] is None),
           'min_naive_height_after_minimalisation': min((r['naive_height_after_minimalisation'] for r in ok), default=None),
           'median_stripped': (sorted(r['naive_height_stripped_by_minimalisation'] for r in ok)[len(ok)//2] if ok else None),
           'rows': rows}
    json.dump(out, open(out_json, 'w'), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != 'rows'}, indent=1))

if __name__ == '__main__':
    ts = sys.argv[3:] or ['0', '1', '-1', '2', '-2', '3', '1/2', '5', '10', '703']
    main(sys.argv[1], sys.argv[2], ts)
