#!/usr/bin/env python3
"""
Independent exact verifier for a quadratic-lift certificate (quadratic_lift.py).

Re-derives everything from the certificate alone, in exact rational arithmetic,
with no PARI and no reuse of the builder's code path:

  1. the short model (A, B) really is the short model of the stated a-invariants;
  2. every supplied base point lies on the short model exactly;
  3. for each added twist, d really equals f(x0), the exhibited point really lies
     on E^(d), and the point is non-torsion by Mazur (m*P != O for m = 1..12);
  4. every non-empty subset product of the d_i is a non-square, so [K:Q] = 2^m;
  5. the reported bound equals base_rank + m.

What it does NOT check, and says so: the value of base_rank itself.  That is an
input with a named provenance, and the certificate is a statement of the form
"rank E(K) >= rank E(Q) + m", which is what this verifier confirms.
"""
import json
import math
import sys
from fractions import Fraction as F

O = None
MAZUR_ORDERS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12]


def is_square(n):
    return n >= 0 and math.isqrt(n) ** 2 == n


def add(P, Q, a4):
    if P is O: return Q
    if Q is O: return P
    x1, y1 = P; x2, y2 = Q
    if x1 == x2:
        if y1 != y2 or y1 == 0: return O
        lam = (3 * x1 * x1 + a4) / (2 * y1)
    else:
        lam = (y2 - y1) / (x2 - x1)
    x3 = lam * lam - x1 - x2
    return (x3, lam * (x1 - x3) - y1)


def mul(n, P, a4):
    R = O; Q = P
    while n:
        if n & 1: R = add(R, Q, a4)
        Q = add(Q, Q, a4); n >>= 1
    return R


def verify(c):
    errs = []
    a1, a2, a3, a4, a6 = [int(v) for v in c['base_curve']['a_invariants']]
    A = int(c['base_curve']['short_model_A'])
    B = int(c['base_curve']['short_model_B'])

    b2 = a1 * a1 + 4 * a2
    b4 = 2 * a4 + a1 * a3
    b6 = a3 * a3 + 4 * a6
    c4 = b2 * b2 - 24 * b4
    c6 = -b2 ** 3 + 36 * b2 * b4 - 216 * b6
    if (A, B) != (-27 * c4, -54 * c6):
        errs.append('short model (A,B) does not match the stated a-invariants')

    n_base = 0
    for xs, ys in c['base_rank'].get('points_short_model', []):
        X, Y = F(xs), F(ys)
        if Y * Y != X ** 3 + A * X + B:
            errs.append('base point %s off the short model' % xs)
        else:
            n_base += 1

    ds = []
    for t in c['added_twists']:
        x0 = F(t['x0']); d = int(t['d'])
        if F(d) != x0 ** 3 + A * x0 + B:
            errs.append('d != f(x0) for x0=%s' % t['x0']); continue
        if is_square(d):
            errs.append('d is a perfect square for x0=%s: Q(sqrt d) = Q' % t['x0']); continue
        X, Y = F(t['point'][0]), F(t['point'][1])
        a4t = F(A) * d * d; a6t = F(B) * d ** 3
        if Y * Y != X ** 3 + a4t * X + a6t:
            errs.append('twist point off E^(d) for x0=%s' % t['x0']); continue
        tors = next((m for m in MAZUR_ORDERS if mul(m, (X, Y), a4t) is O), None)
        if tors is not None:
            errs.append('twist point for x0=%s is torsion of order %d' % (t['x0'], tors)); continue
        ds.append(d)

    m = len(ds)
    for mask in range(1, 1 << m):
        prod = 1
        for i in range(m):
            if mask >> i & 1: prod *= ds[i]
        if is_square(prod):
            errs.append('subset product is a square: [K:Q] < 2^%d' % m); break

    base_rank = c['base_rank']['value']
    bound = base_rank + m
    if c.get('certified_rank_lower_bound') != bound:
        errs.append('reported bound %s != base_rank + m = %d'
                    % (c.get('certified_rank_lower_bound'), bound))

    print('short model verified    : A,B consistent with the stated a-invariants')
    print('base points on curve    : %d / %d'
          % (n_base, len(c['base_rank'].get('points_short_model', []))))
    print('added twists verified   : %d  (d = f(x0), point on E^(d), non-torsion by Mazur)' % m)
    print('[K:Q]                   : 2^%d = %d  (all subset products non-square)' % (m, 2 ** m))
    print('base_rank INPUT         : %d  <- NOT verified by this script; provenance:' % base_rank)
    print('                          %s' % c['base_rank']['provenance'])
    print('CERTIFIED               : rank E(K) >= rank E(Q) + %d = %d' % (m, bound))
    print('errors: %d' % len(errs))
    for e in errs[:20]: print('   !', e)
    return errs


if __name__ == '__main__':
    errs = verify(json.load(open(sys.argv[1])))
    sys.exit(1 if errs else 0)
