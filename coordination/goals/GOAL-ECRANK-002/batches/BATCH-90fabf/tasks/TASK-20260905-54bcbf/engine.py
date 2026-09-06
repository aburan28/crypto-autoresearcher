#!/usr/bin/env python3
"""
Delta-multiplier engine + descent-free certification for EXP-ECRANK-76a70d.

TASK-20260905-54bcbf / BATCH-90fabf / GOAL-ECRANK-002 / H-ECRANK-ee6e0e.

NEW module beside the committed machinery. Per EV-ECRANK-6695dc defect D4's
remedy rule this NEVER edits construct_highrank.py or coset_structure.py; the
pure-Python helpers it needs are copied here (they are committed and
re-verified, so copying is a reuse, not an edit).

STDLIB ONLY: fractions, math, random, json.  NO PARI, NO cypari, NO network,
NO descent (no ellrank, no 2-descent, no r_low, no root numbers).  Every
reported total is a LOWER BOUND from exhibited, verifier-checked points.

The engine implements the frozen contract's M2/M3:
  delta = Lagrange interpolant with delta(b_i) = d_i
  s     := delta * g^2 mod p,  p = prod(x - b_i)
  <=>   u = (r_i^2) lies in W'(b) = D^-1 W(b), the computable 5-dimensional
        subspace (left kernel of the 5 x n Vandermonde at b), and we search
        for a point of W'(b) whose every coordinate is a nonzero rational
        square.  The search is the frozen "seeded fibration": fix 5 of the n
        r-coordinates in a seeded sub-box, solve the (n-5) remaining
        coordinates from the (n-5) linear relations, check the rest are
        squares.  Bounded by the counted-op cap; NO box widening, NO early
        stop for "enough instances".
"""
from __future__ import annotations

import math
import random
from fractions import Fraction as Fr

SUPPORT_COMMITTED = [-1, 2, 3, 5, 7, 11, 13]

# ---------------------------------------------------------------------------
# 1. Polynomial arithmetic (copied verbatim from committed
#    construct_highrank.py; pure Python, no PARI).  polynomials are lists of
#    Fraction, index = degree.
# ---------------------------------------------------------------------------

def pmul(a, b):
    r = [Fr(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x == 0:
            continue
        for j, y in enumerate(b):
            r[i + j] += x * y
    return r


def psub(a, b):
    n = max(len(a), len(b))
    r = [Fr(0)] * n
    for i, x in enumerate(a):
        r[i] += x
    for i, y in enumerate(b):
        r[i] -= y
    while len(r) > 1 and r[-1] == 0:
        r.pop()
    return r


def peval(p, x):
    s = Fr(0)
    for c in reversed(p):
        s = s * x + c
    return s


def prod_linear(A):
    p = [Fr(1)]
    for a in A:
        p = pmul(p, [Fr(-a), Fr(1)])
    return p


def pshift(p, c):
    """return p(t + c)"""
    out = [Fr(0)]
    base = [Fr(1)]
    for i, co in enumerate(p):
        if i > 0:
            base = pmul(base, [c, Fr(1)])
        out = psub(out, [-co * b for b in base])
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return out


def polysqrt_trunc(p, k):
    """p monic of degree 2k -> monic g of degree k with deg(p - g^2) <= k-1."""
    g = [Fr(0)] * (k + 1)
    g[k] = Fr(1)
    for j in range(k - 1, -1, -1):
        S = Fr(0)
        for u in range(j + 1, k + 1):
            v = k + j - u
            if 0 <= v <= k and v > j:
                S += g[u] * g[v]
        g[j] = (p[k + j] - S) / 2
    return g


def mestre_polys(A):
    """A: list of 2k distinct rationals. returns p, g, s = g^2 - p."""
    n = len(A)
    assert n % 2 == 0
    k = n // 2
    p = prod_linear([Fr(a) for a in A])
    g = polysqrt_trunc(p, k)
    s = psub(pmul(g, g), p)
    for a in A:
        if peval(s, Fr(a)) != peval(g, Fr(a)) ** 2:
            raise AssertionError("square condition failed at a=%s" % a)
    return p, g, s


# ---------------------------------------------------------------------------
# 2. Exact linear algebra over Q (Fractions).
# ---------------------------------------------------------------------------

def _rref(rows):
    """Reduced row echelon form over Q. Returns (rref_rows, pivot_cols)."""
    M = [list(r) for r in rows]
    if not M:
        return M, []
    ncols = max(len(r) for r in M)
    M = [r + [Fr(0)] * (ncols - len(r)) for r in M]
    pivots = []
    r = 0
    for col in range(ncols):
        if r >= len(M):
            break
        piv = None
        for i in range(r, len(M)):
            if M[i][col] != 0:
                piv = i
                break
        if piv is None:
            continue
        M[r], M[piv] = M[piv], M[r]
        inv = 1 / M[r][col]
        M[r] = [v * inv for v in M[r]]
        for i in range(len(M)):
            if i != r and M[i][col] != 0:
                f = M[i][col]
                M[i] = [a - f * b for a, b in zip(M[i], M[r])]
        pivots.append(col)
        r += 1
    return M, pivots


def gauss_solve(A, bvec):
    """Solve A x = bvec over Q. A is a list of rows (square). Returns x or None
    if singular / inconsistent."""
    n = len(A)
    if len(bvec) != n or any(len(row) != n for row in A):
        return None
    M = [list(row) + [Fr(bvec[i])] for i, row in enumerate(A)]
    M, pivots = _rref(M)
    if len(pivots) != n:
        return None
    x = [Fr(0)] * n
    for i, pc in enumerate(pivots):
        x[pc] = M[i][n]
    return x


def null_space(rows):
    """Basis of the null space of the matrix `rows` (list of row vectors).
    Returns a list of column vectors (lists) spanning {x : rows . x = 0}."""
    M = [list(r) for r in rows]
    if not M:
        return []
    ncols = max(len(r) for r in M)
    M = [r + [Fr(0)] * (ncols - len(r)) for r in M]
    M, pivots = _rref(M)
    pivot_set = set(pivots)
    free = [c for c in range(ncols) if c not in pivot_set]
    basis = []
    for f in free:
        v = [Fr(0)] * ncols
        v[f] = Fr(1)
        for i, pc in enumerate(pivots):
            if f != pc:
                v[pc] = -M[i][f]
        basis.append(v)
    return basis


# ---------------------------------------------------------------------------
# 3. Rational-square tests
# ---------------------------------------------------------------------------

def is_rational_square(x):
    """x (Fraction) is a nonzero rational square?"""
    if x <= 0:
        return False
    n, dd = x.numerator, x.denominator
    rn = math.isqrt(n)
    rd = math.isqrt(dd)
    return rn * rn == n and rd * rd == dd


def sqrt_rational(x):
    """Principal (nonnegative) rational square root; caller checks is_rational_square."""
    n, dd = x.numerator, x.denominator
    return Fr(math.isqrt(n), math.isqrt(dd))


# ---------------------------------------------------------------------------
# 4. Delta-multiplier engine (M2/M3)
# ---------------------------------------------------------------------------

def lagrange_interpolant(b, d):
    """delta(x) with delta(b_i) = d_i, degree <= n-1. b, d lists of Fr/int."""
    n = len(b)
    delta = [Fr(0)] * n
    for i in range(n):
        # L_i(x) = prod_{j != i} (x - b_j) / (b_i - b_j)
        num = [Fr(1)]
        den = Fr(1)
        for j in range(n):
            if j == i:
                continue
            num = pmul(num, [Fr(-b[j]), Fr(1)])
            den *= (b[i] - b[j])
        delta = psub(delta, [Fr(d[i]) / den * c for c in num])
    while len(delta) > 1 and delta[-1] == 0:
        delta.pop()
    return delta


def wprime_equations(b, d):
    """The (n-5) row vectors (D c_k) defining W'(b) = {u : (D c_k).u = 0}.

    c_k span the left kernel of the 5 x n Vandermonde V[j][i] = b_i^j.
    Returns a list of (n-5) row vectors of length n over Q.
    """
    n = len(b)
    V = [[Fr(b[i] ** j) for i in range(n)] for j in range(5)]
    # left kernel of V (5 x n): c (length n) with c.V = 0  <=>  null space of V
    kernel = null_space(V)
    assert len(kernel) == n - 5, "expected n-5 left-kernel relations, got %d" % len(kernel)
    eqs = []
    for c in kernel:
        eqs.append([Fr(d[i]) * c[i] for i in range(n)])
    return eqs


def interpolate_quartic(b, v):
    """The unique quartic s with s(b_i) = v_i (v in W(b)). Solves on the first
    5 points; verifies against all n as a consistency check."""
    n = len(b)
    M = [[Fr(b[i] ** j) for j in range(5)] for i in range(5)]
    c = gauss_solve(M, [Fr(v[i]) for i in range(5)])
    if c is None:
        return None
    s = c
    for i in range(n):
        if peval(s, Fr(b[i])) != Fr(v[i]):
            return None  # v not in W(b): inconsistent
    return s


def sample_rational(H, rng):
    """A rational of height <= H (height = max(|num|, den) in lowest terms),
    nonzero, from a seeded deterministic source. Denominators kept small so the
    solved coordinates stay in a controlled range."""
    while True:
        num = rng.randint(-H, H)
        if num == 0:
            continue
        den = rng.randint(1, max(2, min(H, 50)))
        g = math.gcd(abs(num), den)
        num //= g
        den //= g
        if max(abs(num), den) <= H:
            return Fr(num, den)


def fibration_search(b, d, H, rng, max_draws, ops, draw_cost=824):
    """Frozen seeded fibration: fix 5 r-coordinates in a seeded sub-box of
    height <= H, solve the (n-5) remaining coordinates from the W'(b)
    relations, check the rest are nonzero rational squares.

    Returns a list of dicts, one per candidate u found (all coords squares):
      {'u': [...], 'r': [...], 's': quartic or None, 'draw': k}
    Bounded by max_draws and the op cap; NO widening, NO early stop.
    """
    n = len(b)
    eqs = wprime_equations(b, d)
    ops.add(512)  # Vandermonde left kernel (declared cost)
    # choose 5 coordinates to fix such that the free sub-system is invertible
    fix = None
    free = None
    A = None
    for fix_try in ([list(range(5)),
                     list(range(n - 5, n)),
                     [0, 1, 2, 3, n - 1],
                     [0, 1, n - 3, n - 2, n - 1]]):
        free_try = [i for i in range(n) if i not in fix_try]
        A_try = [[eqs[e][free_try[f]] for f in range(len(free_try))]
                 for e in range(len(eqs))]
        # test invertibility
        test = gauss_solve(A_try, [Fr(1)] * len(eqs))
        if test is not None:
            fix, free, A = fix_try, free_try, A_try
            break
    if fix is None:
        return []  # degenerate b: no invertible fibration chart
    out = []
    for draw in range(max_draws):
        if ops.exhausted():
            break
        u = [Fr(0)] * n
        for i in fix:
            r = sample_rational(H, rng)
            u[i] = r * r
        rhs = [Fr(0)] * len(eqs)
        for e in range(len(eqs)):
            s = Fr(0)
            for i in fix:
                s += eqs[e][i] * u[i]
            rhs[e] = -s
        sol = gauss_solve(A, rhs)
        if sol is None:
            ops.add(draw_cost)
            continue
        for f, val in zip(free, sol):
            u[f] = val
        ops.add(draw_cost)
        if all(is_rational_square(u[i]) for i in range(n)):
            v = [Fr(d[i]) * u[i] for i in range(n)]
            s = interpolate_quartic(b, v)
            r = [sqrt_rational(u[i]) for i in range(n)]
            out.append({'u': u, 'r': r, 's': s, 'draw': draw})
    return out


def degeneracy_filter(s, b, r):
    """C4 exact nondegeneracy filter. Returns (ok, reasons).
    deg s in {3,4}; s nonsingular (quartic/cubic discriminant != 0);
    g(b_i) = r_i != 0 for all i."""
    reasons = []
    if s is None:
        return False, ['no quartic (v not in W(b))']
    deg = len(s) - 1
    while deg > 0 and s[deg] == 0:
        deg -= 1
    if deg not in (3, 4):
        reasons.append('deg s = %d not in {3,4}' % deg)
    for i in range(len(b)):
        if r[i] == 0:
            reasons.append('r_%d = 0' % i)
    # nonsingularity: discriminant of the (cubic or quartic) model != 0
    if deg == 3:
        # y^2 = cubic: singular iff cubic has a repeated root
        if _cubic_has_repeated_root(s):
            reasons.append('cubic model singular')
    elif deg == 4:
        if _quartic_has_repeated_root(s):
            reasons.append('quartic model singular')
    return (len(reasons) == 0), reasons


def _poly_roots_repeated(s):
    """True iff the polynomial s (list, index=degree) has a repeated root over
    C, i.e. gcd(s, s') has positive degree. Exact, via Euclidean algorithm."""
    def deriv(p):
        d = [Fr(0)] * len(p)
        for i in range(1, len(p)):
            d[i - 1] = p[i] * i
        while len(d) > 1 and d[-1] == 0:
            d.pop()
        return d
    def pgcd(a, b):
        while b:
            while len(b) > 1 and b[-1] == 0:
                b.pop()
            if not b or (len(b) == 1 and b[0] == 0):
                break
            # pseudo-remainder to stay in Q is fine (we only need degree)
            a, b = b, _pmod(a, b)
        while len(a) > 1 and a[-1] == 0:
            a.pop()
        return a
    def _pmod(a, b):
        # polynomial mod over Q
        if len(b) == 0 or (len(b) == 1 and b[0] == 0):
            raise ZeroDivisionError
        lead = b[-1]
        r = list(a)
        diff = len(r) - len(b)
        if diff < 0:
            return r
        for k in range(diff, -1, -1):
            coef = r[k + len(b) - 1] / lead
            if coef == 0:
                continue
            for j in range(len(b)):
                r[k + j] -= coef * b[j]
        while len(r) > 1 and r[-1] == 0:
            r.pop()
        return r
    d = deriv(s)
    if not d or (len(d) == 1 and d[0] == 0):
        return False
    g = pgcd(s, d)
    while len(g) > 1 and g[-1] == 0:
        g.pop()
    return len(g) > 1


def _cubic_has_repeated_root(s):
    return _poly_roots_repeated(s)


def _quartic_has_repeated_root(s):
    return _poly_roots_repeated(s)


# ---------------------------------------------------------------------------
# 5. Quartic -> cubic -> Weierstrass reduction (copied from committed
#    construct_highrank.py; pure Python, no PARI).
# ---------------------------------------------------------------------------

def quartic_reduction(s, a0, e):
    """s quartic with s(a0) = e^2 (e != 0). Return (D, coef)."""
    st = pshift(s, Fr(a0))
    st = st + [Fr(0)] * (5 - len(st))
    c0, d, c, b, a = st[0], st[1], st[2], st[3], st[4]
    if c0 != e * e:
        raise AssertionError("shift did not produce e^2 constant term")
    cp = c - d * d / (4 * e * e)
    P1 = psub([b], [Fr(0), d / e])
    P2 = psub([a], [Fr(0), Fr(0), Fr(1)])
    P3 = psub([cp], [Fr(0), 2 * e])
    D = psub(pmul(P1, P1), [4 * x for x in pmul(P2, P3)])
    return D, (a, b, c, d, e)


def quartic_point_to_cubic(t, v, coef):
    a, b, c, d, e = coef
    m = (v - e - (d / (2 * e)) * t) / (t * t)
    w = 2 * (a - m * m) * t + (b - (d / e) * m)
    return m, w


def cubic_to_weierstrass(D, pts):
    """w^2 = D(m), deg D = 3 -> Y^2 = X^3 + a2 X^2 + a4 X + a6 (integral)."""
    if len(D) != 4 or D[3] == 0:
        raise AssertionError("D is not a genuine cubic")
    A0, A1, A2, A3 = D[0], D[1], D[2], D[3]
    a2, a4, a6 = A2, A1 * A3, A0 * A3 * A3
    P = [(A3 * m, A3 * w) for m, w in pts]
    u = math.lcm(a2.denominator, a4.denominator, a6.denominator)
    a2, a4, a6 = a2 * u * u, a4 * u ** 4, a6 * u ** 6
    P = [(x * u * u, y * u ** 3) for x, y in P]
    ainv = [Fr(0), a2, Fr(0), a4, a6]
    for x, y in P:
        if y * y != x ** 3 + a2 * x * x + a4 * x + a6:
            raise AssertionError("weierstrass image point off curve")
    return [int(z) for z in ainv], P


def cubic_model_to_weierstrass(s, pts):
    """s a cubic (y^2 = s(x)) with pts = [(x, y)] on it -> integral Weierstrass
    [a1,a2,a3,a4,a6] and the points. Clears denominators exactly."""
    if len(s) != 4 or s[3] == 0:
        raise AssertionError("s is not a genuine cubic")
    c0, c1, c2, c3 = s[0], s[1], s[2], s[3]
    # y^2 = c3 x^3 + c2 x^2 + c1 x + c0.  Put X = c3 x, Y = c3 y (c3 != 0):
    # Y^2 = c3^2 y^2 = c3^2 (c3 x^3 + c2 x^2 + c1 x + c0)
    #     = X^3 + c2 X^2 + c3 c1 X + c3^2 c0.   (matches committed cubic_to_weierstrass)
    a2, a4, a6 = c2, c1 * c3, c0 * c3 ** 2
    P = [(c3 * x, c3 * y) for x, y in pts]
    u = math.lcm(a2.denominator, a4.denominator, a6.denominator)
    a2, a4, a6 = a2 * u * u, a4 * u ** 4, a6 * u ** 6
    P = [(x * u * u, y * u ** 3) for x, y in P]
    ainv = [Fr(0), a2, Fr(0), a4, a6]
    for x, y in P:
        if y * y != x ** 3 + a2 * x * x + a4 * x + a6:
            raise AssertionError("weierstrass image point off curve")
    return [int(z) for z in ainv], P


def verify_on_curve(ainv, x, y):
    """EXACT check of y^2 + a1 x y + a3 y = x^3 + a2 x^2 + a4 x + a6."""
    a1, a2, a3, a4, a6 = [Fr(z) for z in ainv]
    x = Fr(x)
    y = Fr(y)
    return y * y + a1 * x * y + a3 * y == x ** 3 + a2 * x * x + a4 * x + a6


def disc_from_ainv(ainv):
    a1, a2, a3, a4, a6 = [Fr(z) for z in ainv]
    b2 = a1 * a1 + 4 * a2
    b4 = 2 * a4 + a1 * a3
    b6 = a3 * a3 + 4 * a6
    b8 = a1 * a1 * a6 + 4 * a2 * a6 - a1 * a3 * a4 + a2 * a3 * a3 - a4 * a4
    return -b2 * b2 * b8 - 8 * b4 ** 3 - 27 * b6 * b6 + 9 * b2 * b4 * b6


# ---------------------------------------------------------------------------
# 6. F_l-reduction within-class independence certifier (copied from committed
#    exact_certify.py; stdlib only, exact, descent-free).  One-sided sound:
#    rank_{F_l} M = m implies independence; it may under-report, never
#    over-report.
# ---------------------------------------------------------------------------

O = None  # point at infinity
MAZUR_ORDERS = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12)


class Qfield:
    def __init__(self):
        self.p = 0

    def el(self, v):
        return Fr(v)

    def inv(self, v):
        return 1 / v

    def is_zero(self, v):
        return v == 0


class Fp:
    def __init__(self, p):
        self.p = p

    def el(self, v):
        if isinstance(v, Fr):
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


def count_points(ai, p):
    a1, a2, a3, a4, a6 = [a % p for a in ai]
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


def _reducible(P, p):
    x, y = P
    return x.denominator % p != 0 and y.denominator % p != 0


def _fl_rank(rows, l):
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


def _independent_rows(rows, l):
    basis = []
    chosen = []
    for i, r in enumerate(rows):
        cand = basis + [list(r)]
        if _fl_rank(cand, l) > len(basis):
            basis = cand
            chosen.append(i)
    return chosen


def _coords_in_l_torsion(K, ai, elems, l):
    basis = []
    coords = []
    for g in elems:
        if len(basis) == 0:
            span = {O: (0, 0)}
        elif len(basis) == 1:
            span = {}
            X = O
            for a in range(l):
                span[X] = (a, 0)
                X = add(K, ai, X, basis[0])
        else:
            span = {}
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
                return None
            basis.append(g)
            coords.append((1, 0) if len(basis) == 1 else (0, 1))
    return coords


def fl_certify(a_invariants, points, max_prime=1500, torsion_primes=8,
               l_candidates=(2, 3, 5, 7, 11, 13), max_good_primes=60):
    """Certify a rank LOWER BOUND for E/Q from exhibited points, exact only.
    Returns dict with 'certified_rank_lower_bound' (= max F_l rank achieved)."""
    ai = [int(a) for a in a_invariants]
    K = Qfield()
    aiF = [Fr(a) for a in ai]
    disc = discriminant(ai)
    result = {
        'a_invariants': ai,
        'discriminant': str(disc),
        'n_points_submitted': len(points),
        'exact_arithmetic_only': True,
        'method': 'reduction mod l (committed exact_certify.py, copied)',
        'errors': [],
    }
    if disc == 0:
        result['errors'].append('singular model: discriminant is zero')
        result['certified_rank_lower_bound'] = 0
        return result
    P = []
    idx = []
    on_curve_fail = []
    for i, (xs, ys) in enumerate(points):
        pt = (Fr(xs), Fr(ys))
        if not on_curve(K, aiF, pt):
            on_curve_fail.append(i)
        else:
            P.append(pt)
            idx.append(i)
    result['on_curve_failures'] = on_curve_fail
    if on_curve_fail:
        result['errors'].append('points not on curve: %s' % on_curve_fail)
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
        tb = math.gcd(tb, card[p])
    result['torsion_bound'] = tb
    result['torsion_bound_primes'] = good[:torsion_primes]
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
        }
    if best['rank'] < r:
        result['errors'].append(
            'only %d of %d submitted non-torsion points certified independent '
            '(under-report, one-sided sound; NOT evidence of low rank)'
            % (best['rank'], r))
    return result


# ---------------------------------------------------------------------------
# 7. Coset / mask machinery (copied from committed coset_structure.py).
# ---------------------------------------------------------------------------

def squarefree_part(n):
    if n == 0:
        raise ValueError("zero has no squarefree part")
    s = -1 if n < 0 else 1
    n = abs(n)
    out = 1
    p = 2
    while p * p <= n:
        e = 0
        while n % p == 0:
            n //= p
            e += 1
        if e % 2:
            out *= p
        p += 1 if p == 2 else 2
    return s * out * n


def mask_of(d, support):
    m = 0
    v = d
    if v < 0:
        if -1 not in support:
            return None
        m |= 1 << support.index(-1)
        v = -v
    for i, g in enumerate(support):
        if g > 0 and v % g == 0:
            v //= g
            m |= 1 << i
    return m if v == 1 else None


def class_value(mask, support):
    d = 1
    for i, g in enumerate(support):
        if mask >> i & 1:
            d *= g
    return d


def subspaces(n, k):
    import itertools
    out = []
    for pivots in itertools.combinations(range(n), k):
        free = [j for j in range(n) if j not in pivots]
        slots = [[j for j in free if j > piv] for piv in pivots]
        grids = [list(itertools.product([0, 1], repeat=len(s))) for s in slots]
        for choice in itertools.product(*grids):
            basis = []
            for i, piv in enumerate(pivots):
                v = 1 << piv
                for bit, j in zip(choice[i], slots[i]):
                    if bit:
                        v |= 1 << j
                basis.append(v)
            span = [0]
            for b in basis:
                span += [x ^ b for x in span]
            out.append(sorted(span))
    return out


def affine_subspaces(n, k):
    out = []
    for V in subspaces(n, k):
        reps = {min(m ^ v for v in V) for m in range(1 << n)}
        for m0 in sorted(reps):
            out.append((m0, V))
    return out


def eligible_cosets(support=SUPPORT_COMMITTED, k=3):
    """All affine k-cosets of the support whose direction space contains the
    -1 class (mixed signs => real solvability guaranteed). Returns a list of
    (m0, V) with the -1 bit in V."""
    n = len(support)
    neg_bit = 1 << support.index(-1)
    out = []
    for m0, V in affine_subspaces(n, k):
        if any(v & neg_bit for v in V):
            out.append((m0, V))
    return out


# ---------------------------------------------------------------------------
# 8. Certification pipeline (descent-free, certificate-kind split).
# ---------------------------------------------------------------------------

def _reduce_twist(s, d, pts):
    """Reduce the twist E^(d): v^2 = s(u)/d to an integral Weierstrass model
    using pts (a nonempty list of (b, r) with s(b) = d r^2) as the base point.
    Returns (ainv, weierstrass_points) or raises."""
    f = [c / Fr(d) for c in s]
    base = pts[0]
    b0, r0 = base
    deg = len(f) - 1
    while deg > 0 and f[deg] == 0:
        deg -= 1
    if deg == 4:
        D, coef = quartic_reduction(f, b0, r0)
        cub = []
        for (b, r) in pts[1:]:
            t = Fr(b) - Fr(b0)
            if t == 0:
                continue
            m, w = quartic_point_to_cubic(t, r, coef)
            if w * w != peval(D, m):
                raise AssertionError("cubic image point off cubic")
            cub.append((m, w))
        if len(set(m for m, _ in cub)) != len(cub):
            raise AssertionError("image points collide")
        return cubic_to_weierstrass(D, cub)
    elif deg == 3:
        return cubic_model_to_weierstrass(f, pts)
    else:
        raise AssertionError("twist model degree %d not in {3,4}" % deg)


def certify_instance(s, b, r, d, support=SUPPORT_COMMITTED, max_prime=1500):
    """Descent-free certification of a constructed instance.

    s: quartic/cubic (list, index=degree); b, r, d: length-n lists with
    s(b_i) = d_i r_i^2.  Groups the forced points by squarefree class, reduces
    each populated twist to Weierstrass, and certifies within-class
    independence by the exact F_l certifier.  Cross-class independence is exact
    by the committed eigenspace (character) argument, so each populated class
    contributes one exact eigenspace unit plus (m_d - 1) exact F_l units.

    Returns a dict with the certificate-kind split and per-class detail.
    """
    # group indices by squarefree class
    by_class = {}
    for i in range(len(b)):
        ds = squarefree_part(int(d[i]))
        by_class.setdefault(ds, []).append(i)
    per_class = []
    eigenspace_units = 0
    fl_units = 0
    total = 0
    verifier_errors = 0
    for ds in sorted(by_class):
        idxs = by_class[ds]
        pts = [(b[i], r[i]) for i in idxs]
        try:
            ainv, wpts = _reduce_twist(s, ds, pts)
        except Exception as ex:
            per_class.append({'d': ds, 'n_points': len(idxs), 'error': repr(ex)[:200],
                              'fl_rank': 0})
            verifier_errors += 1
            continue
        if disc_from_ainv(ainv) == 0:
            per_class.append({'d': ds, 'n_points': len(idxs), 'error': 'singular',
                              'fl_rank': 0})
            verifier_errors += 1
            continue
        cert = fl_certify(ainv, wpts, max_prime=max_prime)
        m_d = cert['certified_rank_lower_bound']
        if cert['on_curve_failures']:
            verifier_errors += 1
        if ds != 1:
            eigenspace_units += 1 if m_d >= 1 else 0
            fl_units += max(0, m_d - 1)
        else:
            # class 1: the whole within-class multiplicity is F_l-certified;
            # the eigenspace unit for class 1 is the trivial character and is
            # NOT counted as a distinct-class unit (it is the base curve).
            fl_units += m_d
        total += m_d
        per_class.append({'d': ds, 'n_points': len(idxs), 'fl_rank': m_d,
                          'ainv': ainv,
                          'weierstrass_points': [[str(x), str(y)] for x, y in wpts],
                          'fl_errors': cert['errors']})
    return {
        'per_class': per_class,
        'eigenspace_units': eigenspace_units,
        'fl_within_class_units': fl_units,
        'certified_total': total,
        'verifier_errors': verifier_errors,
        'n_classes_populated': len(by_class),
    }


# ---------------------------------------------------------------------------
# 9. Op counter (counted exact rational operations, checkpointed every 10^7).
# ---------------------------------------------------------------------------

class OpCounter:
    CHECKPOINT = 10 ** 7

    def __init__(self, cap):
        self.cap = cap
        self.count = 0
        self.checkpoints = []
        self._next = self.CHECKPOINT

    def add(self, n):
        self.count += n
        while self.count >= self._next:
            self.checkpoints.append(self._next)
            self._next += self.CHECKPOINT

    def exhausted(self):
        return self.count >= self.cap


def frs(x):
    x = Fr(x)
    return "%d/%d" % (x.numerator, x.denominator)


def poly_str(p):
    return "[" + ", ".join(frs(c) for c in p) + "]"
