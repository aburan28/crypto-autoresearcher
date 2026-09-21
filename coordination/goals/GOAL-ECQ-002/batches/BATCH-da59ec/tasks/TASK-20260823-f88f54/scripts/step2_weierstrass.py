#!/usr/bin/env python3
"""STEP 2 -- NAGAO-1994 quartic -> Weierstrass model over Q(t), exactly.

For the quartic  y^2 = a x^4 + b x^3 + c x^2 + d x + e  over Q(t), the classical
invariants are
    I = 12ae - 3bd + c^2
    J = 72ace + 9bcd - 27ad^2 - 27b^2 e - 2c^3
and the Jacobian is  Y^2 = X^3 - 27 I X - 27 J.  The quartic carries the
rational point verified in step 1, so it IS isomorphic to its Jacobian over Q(t).

Emits a pipeline family spec (families.py format) with
    a_invariants = [0, 0, 0, -27*I(t), -27*J(t)]
and reports coefficient sizes BEFORE minimalisation.  Minimalisation (PARI) is
measured separately in step 2b.
"""
import json, sys
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from step1_nagao_identity import parse_poly_in_t, padd, pmul, pscal, ppow, trim, SRC
from fractions import Fraction as F

def poly_str(p):
    terms = []
    for i, c in enumerate(p):
        if c == 0: continue
        c = int(c) if c.denominator == 1 else c
        terms.append(('%s' % c) if i == 0 else '%s*t^%d' % (c, i))
    return ' + '.join(reversed(terms)) if terms else '0'

def main(out_json, family_json):
    db = json.load(open(SRC))
    fam = next(x for x in db['families'] if x['id'] == 'NAGAO-1994')
    wc = fam['weierstrass_coefficients_in_t']
    a = parse_poly_in_t(wc['c4']); b = parse_poly_in_t(wc['c3'])
    c = parse_poly_in_t(wc['c2']); d = parse_poly_in_t(wc['c1'])
    e = parse_poly_in_t(wc['c0'])

    I = trim(padd(padd(pscal(pmul(a, e), F(12)), pscal(pmul(b, d), F(-3))), pmul(c, c)))
    J = trim(padd(padd(padd(padd(
            pscal(pmul(pmul(a, c), e), F(72)),
            pscal(pmul(pmul(b, c), d), F(9))),
            pscal(pmul(a, pmul(d, d)), F(-27))),
            pscal(pmul(pmul(b, b), e), F(-27))),
            pscal(pmul(c, pmul(c, c)), F(-2))))
    A = trim(pscal(I, F(-27)))     # a4
    B = trim(pscal(J, F(-27)))     # a6

    def sizes(p, name):
        nz = [(i, int(x)) for i, x in enumerate(p) if x != 0]
        mx = max(abs(v) for _, v in nz)
        return {'name': name, 'degree_in_t': len(p) - 1,
                'n_nonzero_coeffs': len(nz),
                'max_abs_coefficient': str(mx),
                'max_abs_coefficient_digits': len(str(mx)),
                'log10_max_abs_coefficient': len(str(mx)) - 1,
                'coefficients_by_power': {str(i): str(v) for i, v in nz}}

    quartic_sizes = [sizes(p, n) for p, n in
                     ((a, 'quartic_c4'), (b, 'quartic_c3'), (c, 'quartic_c2'),
                      (d, 'quartic_c1'), (e, 'quartic_c0'))]
    res = {
      'step': 2,
      'what': 'exact quartic -> Weierstrass (Jacobian) conversion over Q(t)',
      'method': 'I = 12ae-3bd+c^2 ; J = 72ace+9bcd-27ad^2-27b^2e-2c^3 ; Y^2 = X^3 - 27I X - 27J',
      'justified_by': 'step 1: the quartic has the rational point ((t+703)/15, 1248 N(t)/75), '
                      'so it is isomorphic over Q(t) to its Jacobian',
      'quartic_coefficient_sizes': quartic_sizes,
      'weierstrass_over_Qt': {'a1': '0', 'a2': '0', 'a3': '0',
                              'a4': poly_str(A), 'a6': poly_str(B)},
      'weierstrass_coefficient_sizes_before_minimalisation': [sizes(A, 'a4 = -27*I(t)'),
                                                              sizes(B, 'a6 = -27*J(t)')],
      'surface_degree_check': {
        'deg_a4_in_t': len(A) - 1, 'deg_a6_in_t': len(B) - 1,
        'note': 'd = max(ceil(deg a4 / 4), ceil(deg a6 / 6)) for the minimal Weierstrass '
                'model over P^1; deg (8,12) is consistent with an elliptic K3 (d=2), '
                'matching the unconditional d>=2 from geometric rank 13.'},
    }
    json.dump(res, open(out_json, 'w'), indent=1)
    spec = {
      'name': 'NAGAO-1994',
      'params': ['t'],
      'a_invariants': ['0', '0', '0', poly_str(A), poly_str(B)],
      'sections': [],
      'claimed_generic_rank': 12,
      'source': "Nagao 1994 (Proc. Japan Acad. 70(5) 152-153) via Scholten arXiv:math/9709235 eq.(1), "
                "transcribed in BATCH-f2341e candidate_families.json; Jacobian taken here. "
                "rank exactly 12 over Q(t), 13 over Qbar(t) (Scholten Thm 2 / Cor 1) -- CITED, NOT VERIFIED HERE.",
      'notes': 'a4=-27I, a6=-27J from the quartic; self-consistency of the transcription '
               're-verified symbolically at all 7 coefficients (ratio 1557504=1248^2).'
    }
    json.dump(spec, open(family_json, 'w'), indent=1)
    for s in res['weierstrass_coefficient_sizes_before_minimalisation']:
        print('%s: degree %d, max |coeff| has %d digits' %
              (s['name'], s['degree_in_t'], s['max_abs_coefficient_digits']))
    print('quartic max |coeff| digits:', [s['max_abs_coefficient_digits'] for s in quartic_sizes])

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
