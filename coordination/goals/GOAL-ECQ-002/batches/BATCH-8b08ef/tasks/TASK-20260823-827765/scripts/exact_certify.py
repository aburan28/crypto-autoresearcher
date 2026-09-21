#!/usr/bin/env python3
"""
EXACT, stdlib-only certifier of a rank LOWER BOUND for E/Q from exhibited points.

No PARI, no floating point, no analytic rank, no Selmer bound, no regulator.
Every operation below is integer / Fraction arithmetic.  This file is the
verifier: it is deliberately independent of whatever produced the points
(PARI ellrank, a family specialisation, a leaderboard record), so that running
it re-proves the bound rather than restating it.  Same discipline as
experiments/EXP-ECRANK-e1e30e/source/verify_certificate.py, adapted from
multiquadratic fields to plain Q.

Certificate claim
-----------------
  E : y^2 + a1 x y + a3 y = x^3 + a2 x^2 + a4 x + a6   over Q, a_i in Z
  P_1, ..., P_r in E(Q) exhibited with exact rational coordinates
  =>  rank E(Q) >= r

Mathematical basis (reduction / mod-l independence)
---------------------------------------------------
(1) TORSION BOUND, exact.  For an odd prime p of good reduction the reduction
    map E(Q)_tors -> E(F_p) is injective (Silverman, VII.3.1 + VII.3.4).  Hence
    #E(Q)_tors divides gcd_p #E(F_p) over any set of such p.  #E(F_p) is
    counted naively (Legendre symbols, exact integer arithmetic).

(2) A HOMOMORPHISM KILLING l*E and killing torsion.  Fix a prime l not
    dividing the torsion bound of (1), and a good prime p with l | N_p where
    N_p = #E(F_p).  Define
        psi_p : E(F_p) -> E(F_p)[l],   psi_p(X) = (N_p / l) * X.
    Then psi_p(l * X) = N_p * X = O, so psi_p kills l*E(F_p).
    If T in E(Q)_tors then ord(T) is coprime to l (by choice of l), so
    T = l * ((l^{-1} mod ord T) * T) lies in l*E(Q), so psi_p(T bar) = O.

(3) INDEPENDENCE.  Suppose the P_i are Z-dependent modulo torsion: then there
    are n_i in Z, not all zero, with sum n_i P_i = T torsion.  Dividing by
    g = gcd(n_i) is legitimate: if g * S = T with S = sum (n_i/g) P_i then S is
    itself torsion, so we may assume gcd(n_i) = 1 and the right side torsion.
    Reducing mod p and applying psi_p gives
        sum n_i psi_p(P_i bar) = O   in E(F_p)[l],
    for EVERY admissible p, with (n_i mod l) not the zero vector (gcd is 1).
    So the vectors of psi_p(P_i bar), coordinatised in the F_l-vector space
    E(F_p)[l] and concatenated over the chosen primes p, are F_l-LINEARLY
    DEPENDENT.  Contrapositive: if that stacked matrix has F_l-rank r, the P_i
    are independent modulo torsion and rank E(Q) >= r.

Everything in (1)-(3) is a finite exact computation.  Non-torsion of each P_i
is implied by the same rank condition, and is additionally checked directly
against Mazur's theorem (a torsion point of E/Q has order in {1..10, 12}).

Entry point
-----------
    certify(a_invariants, points, ...) -> dict
    python3 exact_certify.py cert.json     # {"a_invariants": [...], "points": [[x,y],...]}
"""
from fractions import Fraction as F
from math import gcd
import json
import sys

O = None  # point at infinity

MAZUR_ORDERS = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12)


# --------------------------------------------------------------------------
# exact arithmetic on a general Weierstrass model over a field (Fraction or F_p)
# --------------------------------------------------------------------------
class Qfield:
    """Rational field with exact Fraction arithmetic."""
    def __init__(self):
        self.p = 0

    def el(self, v):
        return F(v)

    def inv(self, v):
        return 1 / v

    def is_zero(self, v):
        return v == 0


class Fp:
    """Prime field F_p with exact integer arithmetic."""
    def __init__(self, p):
        self.p = p

    def el(self, v):
        if isinstance(v, F):
            return (v.numerator % self.p) * pow(v.denominator % self.p, -1, self.p) % self.p
        return v % self.p

    def inv(self, v):
        return pow(v % self.p, -1, self.p)

    def is_zero(self, v):
        return v % self.p == 0


def _red(K, v):
    return v % K.p if K.p else v


def on_curve(K, ai, P):
    if P is O:
        return True
    a1, a2, a3, a4, a6 = ai
    x, y = P
    lhs = y * y + a1 * x * y + a3 * y
    rhs = x * x * x + a2 * x * x + a4 * x + a6
    return K.is_zero(lhs - rhs)


def neg(K, ai, P):
    if P is O:
        return O
    a1, a2, a3, a4, a6 = ai
    x, y = P
    return (x, _red(K, -y - a1 * x - a3))


def add(K, ai, P, Q):
    """Group law on y^2+a1xy+a3y = x^3+a2x^2+a4x+a6 (Silverman III.2.3)."""
    if P is O:
        return Q
    if Q is O:
        return P
    a1, a2, a3, a4, a6 = ai
    x1, y1 = P
    x2, y2 = Q
    if K.is_zero(x1 - x2):
        if K.is_zero(y1 + y2 + a1 * x2 + a3):
            return O
        num = 3 * x1 * x1 + 2 * a2 * x1 + a4 - a1 * y1
        den = 2 * y1 + a1 * x1 + a3
    else:
        num = y2 - y1
        den = x2 - x1
    lam = _red(K, num * K.inv(den))
    nu = _red(K, y1 - lam * x1)
    x3 = _red(K, lam * lam + a1 * lam - a2 - x1 - x2)
    y3 = _red(K, -(lam + a1) * x3 - nu - a3)
    return (x3, y3)


def mul(K, ai, n, P):
    R = O
    if n < 0:
        n, P = -n, neg(K, ai, P)
    Q = P
    while n:
        if n & 1:
            R = add(K, ai, R, Q)
        Q = add(K, ai, Q, Q)
        n >>= 1
    return R


# --------------------------------------------------------------------------
# discriminant of a general Weierstrass model (exact integers)
# --------------------------------------------------------------------------
def b_invariants(ai):
    a1, a2, a3, a4, a6 = ai
    b2 = a1 * a1 + 4 * a2
    b4 = 2 * a4 + a1 * a3
    b6 = a3 * a3 + 4 * a6
    b8 = a1 * a1 * a6 + 4 * a2 * a6 - a1 * a3 * a4 + a2 * a3 * a3 - a4 * a4
    return b2, b4, b6, b8


def discriminant(ai):
    b2, b4, b6, b8 = b_invariants(ai)
    return -b2 * b2 * b8 - 8 * b4 ** 3 - 27 * b6 * b6 + 9 * b2 * b4 * b6


def c_invariants(ai):
    b2, b4, b6, b8 = b_invariants(ai)
    return b2 * b2 - 24 * b4, -b2 ** 3 + 36 * b2 * b4 - 216 * b6


# --------------------------------------------------------------------------
# point counting over F_p, naive and exact
# --------------------------------------------------------------------------
def count_points(ai, p):
    """#E(F_p) by brute force over x, exact.  O(p) with p small."""
    a1, a2, a3, a4, a6 = [a % p for a in ai]
    # number of y with y^2 + (a1 x + a3) y - f(x) = 0, i.e. discriminant
    # D = (a1 x + a3)^2 + 4 f(x); solutions: 1 + legendre(D) unless p == 2.
    if p == 2:
        n = 1
        for x in range(2):
            for y in range(2):
                if (y * y + a1 * x * y + a3 * y - (x ** 3 + a2 * x * x + a4 * x + a6)) % 2 == 0:
                    n += 1
        return n
    n = 1
    e = (p - 1) // 2
    for x in range(p):
        f = (x * x * x + a2 * x * x + a4 * x + a6) % p
        b = (a1 * x + a3) % p
        D = (b * b + 4 * f) % p
        if D == 0:
            n += 1
        else:
            n += 2 if pow(D, e, p) == 1 else 0
    return n


def primes_upto(n):
    sieve = [True] * (n + 1)
    sieve[0:2] = [False, False]
    for i in range(2, int(n ** 0.5) + 1):
        if sieve[i]:
            sieve[i * i::i] = [False] * len(sieve[i * i::i])
    return [i for i, b in enumerate(sieve) if b]


# --------------------------------------------------------------------------
# certification
# --------------------------------------------------------------------------
def _reducible(P, p):
    """Point has p-integral coordinates (so it reduces to the affine part)."""
    x, y = P
    return x.denominator % p != 0 and y.denominator % p != 0


def _independent_rows(rows, l):
    """Greedy maximal F_l-independent subset of the rows; returns index list."""
    basis = []
    chosen = []
    for i, r in enumerate(rows):
        cand = basis + [list(r)]
        if _fl_rank(cand, l) > len(basis):
            basis = cand
            chosen.append(i)
    return chosen


def _fl_rank(rows, l):
    """Rank over F_l of a list of row vectors (Gaussian elimination, exact)."""
    rows = [list(r) for r in rows]
    m = len(rows[0]) if rows else 0
    rank = 0
    col = 0
    while col < m and rank < len(rows):
        piv = None
        for i in range(rank, len(rows)):
            if rows[i][col] % l:
                piv = i
                break
        if piv is None:
            col += 1
            continue
        rows[rank], rows[piv] = rows[piv], rows[rank]
        inv = pow(rows[rank][col], -1, l)
        rows[rank] = [(v * inv) % l for v in rows[rank]]
        for i in range(len(rows)):
            if i != rank and rows[i][col] % l:
                f = rows[i][col]
                rows[i] = [(a - f * b) % l for a, b in zip(rows[i], rows[rank])]
        rank += 1
        col += 1
    return rank


def _coords_in_l_torsion(K, ai, elems, l):
    """Coordinatise elements of E(F_p)[l] (exponent-l group of rank <= 2).

    Returns a list of 2-vectors over F_l, or None if some element is not in the
    span found (cannot happen: E[l](F_p) has rank <= 2).
    """
    basis = []
    coords = []
    for g in elems:
        span = {}
        # enumerate span of current basis
        if len(basis) == 0:
            span = {O: (0, 0)}
        elif len(basis) == 1:
            X = O
            for a in range(l):
                span[X] = (a, 0)
                X = add(K, ai, X, basis[0])
        else:
            X = O
            for a in range(l):
                Y = X
                for b in range(l):
                    span[Y] = (a, b)
                    Y = add(K, ai, Y, basis[1])
                X = add(K, ai, X, basis[0])
        if g in span:
            coords.append(span[g])
        else:
            if len(basis) >= 2:
                return None  # rank > 2 in E[l]: impossible
            basis.append(g)
            coords.append((1, 0) if len(basis) == 1 else (0, 1))
    return coords


def certify(a_invariants, points, max_prime=1500, torsion_primes=8,
            l_candidates=(2, 3, 5, 7, 11, 13), max_good_primes=60):
    """Certify rank E(Q) >= len(points), entirely in exact arithmetic.

    a_invariants : five integers [a1,a2,a3,a4,a6]
    points       : list of [x, y] as int/str/Fraction rationals
    Returns a dict with the full certificate and 'certified_rank_lower_bound'.
    """
    ai = [int(a) for a in a_invariants]
    K = Qfield()
    aiF = [F(a) for a in ai]
    disc = discriminant(ai)
    result = {
        'a_invariants': ai,
        'discriminant': str(disc),
        'n_points_submitted': len(points),
        'exact_arithmetic_only': True,
        'method': 'reduction mod l (see exact_certify.py docstring)',
        'errors': [],
    }
    if disc == 0:
        result['errors'].append('singular model: discriminant is zero')
        result['certified_rank_lower_bound'] = 0
        return result

    # ---- (0) exact on-curve check --------------------------------------
    P = []
    idx = []          # index of each surviving point in the submitted list
    on_curve_fail = []
    for i, (xs, ys) in enumerate(points):
        pt = (F(xs), F(ys))
        if not on_curve(K, aiF, pt):
            on_curve_fail.append(i)
        else:
            P.append(pt)
            idx.append(i)
    result['on_curve_failures'] = on_curve_fail
    if on_curve_fail:
        result['errors'].append('points not on curve: %s' % on_curve_fail)

    # ---- (0b) exact non-torsion check (Mazur) --------------------------
    torsion_points = []
    keep = []
    keep_idx = []
    for j, pt in enumerate(P):
        if any(mul(K, aiF, m, pt) is O for m in MAZUR_ORDERS):
            torsion_points.append(idx[j])
        else:
            keep.append(pt)
            keep_idx.append(idx[j])
    result['torsion_points_rejected'] = torsion_points
    P = keep
    idx = keep_idx
    r = len(P)
    result['n_points_non_torsion'] = r
    if r == 0:
        result['certified_rank_lower_bound'] = 0
        return result

    # ---- (1) exact torsion bound ---------------------------------------
    good = []
    for p in primes_upto(max_prime):
        if p == 2 or disc % p == 0:
            continue
        if all(_reducible(pt, p) for pt in P):
            good.append(p)
        if len(good) >= max_good_primes:
            break
    if not good:
        result['errors'].append('no usable good prime found below %d' % max_prime)
        result['certified_rank_lower_bound'] = 0
        return result
    card = {}
    tb = 0
    for p in good[:torsion_primes]:
        card[p] = count_points(ai, p)
        tb = gcd(tb, card[p])
    result['torsion_bound'] = tb
    result['torsion_bound_primes'] = good[:torsion_primes]

    # ---- (2)-(3) mod-l independence ------------------------------------
    best = {'rank': 0}
    attempts = []
    for l in l_candidates:
        if tb % l == 0:
            continue
        rows = [[] for _ in range(r)]
        used = []
        rank_l = 0
        for p in good:
            if p not in card:
                card[p] = count_points(ai, p)
            N = card[p]
            if N % l:
                continue
            Kp = Fp(p)
            aip = [a % p for a in ai]
            imgs = []
            ok = True
            for pt in P:
                Q = (Kp.el(pt[0]), Kp.el(pt[1]))
                if not on_curve(Kp, aip, Q):
                    ok = False
                    break
                imgs.append(mul(Kp, aip, N // l, Q))
            if not ok:
                continue
            co = _coords_in_l_torsion(Kp, aip, imgs, l)
            if co is None:
                continue
            used.append(p)
            for i in range(r):
                rows[i].extend(co[i])
            rank_l = _fl_rank(rows, l)
            if rank_l == r:
                break
        attempts.append({'l': l, 'n_primes_used': len(used), 'Fl_rank_reached': rank_l})
        if rank_l > best['rank']:
            best = {'rank': rank_l, 'l': l, 'primes_used': used,
                    'independent_point_indices': [idx[j] for j in
                                                  _independent_rows(rows, l)]}
        if best['rank'] == r:
            break
    result['independence_attempts'] = attempts
    result['certified_rank_lower_bound'] = best['rank']
    if best['rank']:
        result['independence'] = {
            'l': best['l'], 'primes_used': best['primes_used'],
            'stacked_matrix_Fl_rank': best['rank'],
            'independent_point_indices': best['independent_point_indices'],
            'argument': 'psi_p(X)=(N_p/l)X kills l*E(F_p) and the torsion of '
                        'E(Q) (l coprime to the torsion bound); an F_l-rank-k '
                        'set of stacked images admits no primitive Z-relation '
                        'modulo torsion, so those k points are independent',
        }
    if best['rank'] < r:
        result['errors'].append(
            'only %d of %d submitted non-torsion points were certified '
            'independent with l in %s below prime bound %d; the remainder are '
            'INCONCLUSIVE (they may be dependent, or the search bound may be '
            'too small) -- this is not evidence of low rank'
            % (best['rank'], r, list(l_candidates), max_prime))
    return result


if __name__ == '__main__':
    src = json.load(open(sys.argv[1]))
    out = certify(src['a_invariants'], src['points'])
    print(json.dumps(out, indent=1))
    sys.exit(0 if out['certified_rank_lower_bound'] == len(src['points']) else 1)
