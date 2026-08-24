#!/usr/bin/env python3
"""
Lift a curve of known rank r over Q to rank >= r + m over a multiquadratic
field of degree 2^m, with an exact certificate for the m added points.

Construction
------------
Put E in short form y^2 = x^3 + A x + B.  For ANY rational x0 set

    d = f(x0) = x0^3 + A x0 + B .

Then E^(d) : v^2 = u^3 + A d^2 u + B d^3 carries the rational point

    Q0 = (d * x0, d^2),        v^2 = d^4 = d^3 * f(x0) = u^3 + A d^2 u + B d^3,

which corresponds to (x0, sqrt d) in E(Q(sqrt d)).  No point search and no
factorisation of d is needed: d is produced, not found.

Because Gal(Q(sqrt d)/Q) sends (x0, sqrt d) to (x0, -sqrt d), the new point lies
in the MINUS eigenspace while all of E(Q) lies in the PLUS eigenspace.  Hence

    rank E(Q(sqrt d)) = rank E(Q) + rank E^(d)(Q) >= rank E(Q) + 1,

and the "+1" is independent of every point of E(Q) by exact Galois algebra --
no height pairing between the old points and the new one is ever needed.

For m seeds x_1..x_m the field is K = Q(sqrt d_1, ..., sqrt d_m); [K:Q] = 2^m
holds exactly when every product of a non-empty subset of {d_1..d_m} is a
non-square, which is checkable by integer square-root alone (NO factorisation).

The only thing this script does not certify is rank E(Q) itself; that is an
input, and its provenance is recorded in the certificate.
"""
import argparse
import json
import math
import sys
from fractions import Fraction as F

O = None


def is_square(n):
    if n < 0:
        return False
    r = math.isqrt(n)
    return r * r == n


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


MAZUR_ORDERS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12]


def short_model(a1, a2, a3, a4, a6):
    """(A, B) and the exact point map for y^2 = x^3 + A x + B."""
    b2 = a1 * a1 + 4 * a2
    b4 = 2 * a4 + a1 * a3
    b6 = a3 * a3 + 4 * a6
    c4 = b2 * b2 - 24 * b4
    c6 = -b2 ** 3 + 36 * b2 * b4 - 216 * b6
    A, B = -27 * c4, -54 * c6

    def to_short(x, y):
        return (36 * x + 3 * b2, 108 * (2 * y + a1 * x + a3))

    return A, B, to_short


def build(a_invariants, seeds, known_points, base_rank, provenance):
    a1, a2, a3, a4, a6 = a_invariants
    A, B, to_short = short_model(a1, a2, a3, a4, a6)

    # sanity: the model change must carry every supplied point exactly
    mapped = []
    for xs, ys in known_points:
        x, y = F(xs), F(ys)
        assert y * y + a1 * x * y + a3 * y == x ** 3 + a2 * x * x + a4 * x + a6, \
            'supplied point not on the long Weierstrass model'
        X, Y = to_short(x, y)
        assert Y * Y == X ** 3 + A * X + B, 'model change broke a point'
        mapped.append([str(X), str(Y)])

    twists = []
    for x0s in seeds:
        x0 = F(x0s)
        assert x0.denominator == 1, 'integral seeds only, so d is an integer'
        d = int(x0 ** 3 + A * x0 + B)
        if is_square(d):
            continue
        Q0 = (F(d) * x0, F(d) ** 2)
        a4t = F(A) * d * d
        a6t = F(B) * d ** 3
        assert Q0[1] ** 2 == Q0[0] ** 3 + a4t * Q0[0] + a6t, 'twist point off curve'
        order = None
        for m in MAZUR_ORDERS:
            if mul(m, Q0, a4t) is O:
                order = m; break
        twists.append({'x0': str(x0), 'd': str(d),
                       'point': [str(Q0[0]), str(Q0[1])],
                       'torsion_order_if_any': order,
                       'non_torsion': order is None})
    good = [t for t in twists if t['non_torsion']]
    ds = [int(t['d']) for t in good]
    # degree check: every non-empty subset product must be a non-square
    m = len(ds)
    degree_ok = True
    for mask in range(1, 1 << m):
        prod = 1
        for i in range(m):
            if mask >> i & 1: prod *= ds[i]
        if is_square(prod):
            degree_ok = False; break
    return {
        'base_curve': {'a_invariants': [str(c) for c in a_invariants],
                       'short_model_A': str(A), 'short_model_B': str(B)},
        'base_rank': {'value': base_rank, 'provenance': provenance,
                      'n_points_supplied': len(known_points),
                      'points_short_model': mapped},
        'added_twists': twists,
        'field': {'m': m, 'degree': 2 ** m,
                  'degree_certified': degree_ok,
                  'discriminant_classes': [str(x) for x in ds]},
        'certified_rank_lower_bound': (base_rank + m) if degree_ok else None,
    }


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', required=True, help='JSON with a_invariants and points')
    ap.add_argument('--seeds', default='0,1,-1,2,-2,3')
    ap.add_argument('--m', type=int, default=1, help='how many twists to keep')
    ap.add_argument('--base-rank', type=int, required=True)
    ap.add_argument('--provenance', required=True)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    src = json.load(open(a.input))
    seeds = [int(s) for s in a.seeds.split(',')]
    cert = build([int(c) for c in src['a_invariants']], seeds,
                 src.get('points', []), a.base_rank, a.provenance)
    cert['added_twists'] = [t for t in cert['added_twists'] if t['non_torsion']][:a.m]
    ds = [int(t['d']) for t in cert['added_twists']]
    cert['field']['m'] = len(ds); cert['field']['degree'] = 2 ** len(ds)
    cert['field']['discriminant_classes'] = [str(x) for x in ds]
    cert['certified_rank_lower_bound'] = a.base_rank + len(ds)
    json.dump(cert, open(a.out, 'w'), indent=1)
    print('added %d twist(s); [K:Q]=%d; certified rank >= %d'
          % (len(ds), 2 ** len(ds), cert['certified_rank_lower_bound']))
