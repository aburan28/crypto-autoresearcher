#!/usr/bin/env python3
"""Exhaustive, certified search of a prime-field isogeny class for a curve
model whose point-decomposition presentation has a lower solving degree.

Question this instrument answers
--------------------------------
Fix an ordinary curve E / F_p.  Every F_p-rational isogeny of every degree
lands inside the F_p-isogeny class of E (Tate: same trace of Frobenius), and
on a prime-order curve every such isogeny is a BIJECTION on rational points.
So an isogeny cannot change WHICH decompositions R = P_1 + ... + P_m exist;
it can only change the polynomial PRESENTATION the solver sees: the Semaev
summation polynomial S_3 of the codomain model (a', b') and the pull-back of
the factor base through the x-coordinate map.  The search asks, for every
curve in the class, whether that presentation is cheaper to solve -- lower
first-fall degree, lower root-finding degree, a reducible fibre -- than on
the input curve and than on a matched random curve OUTSIDE the class.

Exhaustiveness is certified, not assumed.  The class is enumerated by a
breadth-first walk over rational ell-isogenies (found by factoring the
ell-division polynomial, with no modular polynomial needed), every codomain
is checked to carry the input trace, and the number of F_p-isomorphism
classes reached -- weighted by 2/|Aut| -- is compared with the exact
Hurwitz-Kronecker class number H(4p - t^2).  A census mismatch is reported as
`certified: false` and the search result is then a COVERAGE FRACTION, never
an "exhaustive" negative.

What "everything below 2^40" means here (see analysis/isogeny-dreg-search/):
the search is exhaustive over the WHOLE isogeny class -- all curves reachable
by any rational isogeny of any degree, which subsumes any degree bound -- for
fields where the class is enumerable (h ~ sqrt(p), so p up to about 2^40
with a compiled engine; this pure-Python reference engine is for p < 2^24).
Exhaustiveness over all PRIMES below 2^40 is impossible by counting and is
never claimed; see `--cost-model`.

Functionals measured on every class member (identical code on the null set):
  F1  monomial support of S_3(x1, x2, x3): 13 unless a'b' = 0 (j in {0,1728}).
  F2  first-fall degree of the prime-field PDP system
        { S_3(x1, x2, x_R), x1^h - 1, x2^h - 1 }
      i.e. a factor base of x-coordinates in the order-h subgroup of F_p^*,
      measured from the degree-graded Macaulay matrix over F_p.
  F3  fibre root statistic: for a factor base x = u^k, the number of
      F_p-roots in u2 of S_3(u1^k, u2^k, x_R) at random (R, u1); mean and
      maximum over N samples.  A reducible fibre curve or a degenerate model
      raises the mean above the random-polynomial value 1.

Nothing here supports any crypto-scale claim.  Claim tier: toy.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import sys
import time
from dataclasses import dataclass, field, asdict
from fractions import Fraction

# ---------------------------------------------------------------------------
# F_p[x] arithmetic.  A polynomial is a list of ints (low degree first) with
# no trailing zeros; the zero polynomial is [].
# ---------------------------------------------------------------------------


def _trim(f: list[int]) -> list[int]:
    while f and f[-1] == 0:
        f.pop()
    return f


def padd(f, g, p):
    n = max(len(f), len(g))
    out = [0] * n
    for i, c in enumerate(f):
        out[i] = c
    for i, c in enumerate(g):
        out[i] = (out[i] + c) % p
    return _trim(out)


def psub(f, g, p):
    n = max(len(f), len(g))
    out = [0] * n
    for i, c in enumerate(f):
        out[i] = c
    for i, c in enumerate(g):
        out[i] = (out[i] - c) % p
    return _trim(out)


def pscale(f, c, p):
    c %= p
    if c == 0:
        return []
    return _trim([x * c % p for x in f])


def pmul(f, g, p):
    if not f or not g:
        return []
    out = [0] * (len(f) + len(g) - 1)
    for i, a in enumerate(f):
        if a == 0:
            continue
        for j, b in enumerate(g):
            out[i + j] = (out[i + j] + a * b) % p
    return _trim(out)


def pdivmod(f, g, p):
    if not g:
        raise ZeroDivisionError("polynomial division by zero")
    f = list(f)
    dg = len(g) - 1
    inv = pow(g[-1], -1, p)
    if len(f) - 1 < dg:
        return [], _trim(f)
    q = [0] * (len(f) - dg)
    for i in range(len(f) - 1, dg - 1, -1):
        c = f[i]
        if c == 0:
            continue
        c = c * inv % p
        q[i - dg] = c
        for j in range(dg + 1):
            f[i - dg + j] = (f[i - dg + j] - c * g[j]) % p
    return _trim(q), _trim(f[:dg])


def pmod(f, g, p):
    return pdivmod(f, g, p)[1]


def pmonic(f, p):
    if not f:
        return f
    return pscale(f, pow(f[-1], -1, p), p)


def pgcd(f, g, p):
    while g:
        f, g = g, pmod(f, g, p)
    return pmonic(f, p)


def ppowmod(base, e, mod, p):
    result = [1]
    base = pmod(base, mod, p)
    while e:
        if e & 1:
            result = pmod(pmul(result, base, p), mod, p)
        e >>= 1
        if e:
            base = pmod(pmul(base, base, p), mod, p)
    return result


def pderiv(f, p):
    return _trim([(i * c) % p for i, c in enumerate(f)][1:])


def peval(f, x, p):
    r = 0
    for c in reversed(f):
        r = (r * x + c) % p
    return r


def px_pow_p_mod(f, p):
    """x^p mod f."""
    return ppowmod([0, 1], p, f, p)


def count_roots(f, p):
    """Number of distinct F_p-roots of f, via deg gcd(f, x^p - x)."""
    f = pmonic(f, p)
    if len(f) <= 1:
        return 0
    xp = px_pow_p_mod(f, p)
    g = pgcd(f, psub(xp, [0, 1], p), p)
    return len(g) - 1


# ---------------------------------------------------------------------------
# Factoring over F_p: squarefree distinct-degree + Cantor-Zassenhaus.
# ---------------------------------------------------------------------------


def distinct_degree_factor(f, p, max_degree=None):
    """[(d, g_d)] with g_d the product of the irreducible factors of degree d.

    f must be monic and squarefree.  Only degrees <= max_degree are extracted;
    the remaining cofactor is returned with degree tag None.
    """
    f = pmonic(f, p)
    out = []
    h = [0, 1]  # x^{p^i} mod f, starting at i = 0
    d = 0
    x = [0, 1]
    while len(f) - 1 >= 2 * (d + 1):
        d += 1
        if max_degree is not None and d > max_degree:
            break
        h = ppowmod(h, p, f, p)
        g = pgcd(f, psub(h, x, p), p)
        if len(g) > 1:
            out.append((d, g))
            f = pdivmod(f, g, p)[0]
            h = pmod(h, f, p)
    if len(f) > 1:
        deg = len(f) - 1
        if max_degree is None or deg <= max_degree:
            out.append((deg, f))
        else:
            out.append((None, f))
    return out


def equal_degree_factor(g, d, p, rng):
    """Split g (monic, squarefree, all irreducible factors of degree d)."""
    g = pmonic(g, p)
    n = len(g) - 1
    if n == d:
        return [g]
    if n % d:
        raise ValueError("degree mismatch in equal-degree factorization")
    e = (pow(p, d) - 1) // 2
    while True:
        a = [rng.randrange(p) for _ in range(n)]
        a = _trim(a)
        if len(a) < 2:
            continue
        b = ppowmod(a, e, g, p)
        b = psub(b, [1], p)
        h = pgcd(g, b, p)
        if 1 < len(h) < len(g):
            q = pdivmod(g, h, p)[0]
            return equal_degree_factor(h, d, p, rng) + equal_degree_factor(q, d, p, rng)


# ---------------------------------------------------------------------------
# F_{p^r} = F_p[t]/(q(t)) for kernel-polynomial generation.
# ---------------------------------------------------------------------------


class ExtField:
    def __init__(self, p: int, q: list[int]):
        self.p = p
        self.q = pmonic(q, p)
        self.r = len(self.q) - 1

    def red(self, f):
        return pmod(f, self.q, self.p)

    def mul(self, f, g):
        return self.red(pmul(f, g, self.p))

    def add(self, f, g):
        return padd(f, g, self.p)

    def sub(self, f, g):
        return psub(f, g, self.p)

    def inv(self, f):
        # extended Euclid in F_p[t]
        p = self.p
        r0, r1 = self.q, self.red(f)
        s0, s1 = [], [1]
        while r1:
            qq, rem = pdivmod(r0, r1, p)
            r0, r1 = r1, rem
            s0, s1 = s1, psub(s0, pmul(qq, s1, p), p)
        if len(r0) != 1:
            raise ZeroDivisionError("non-invertible element")
        return self.red(pscale(s0, pow(r0[0], -1, p), p))

    def const(self, c):
        return _trim([c % self.p])

    def is_const(self, f):
        return len(f) <= 1

    def gen(self):
        return [0, 1] if self.r > 1 else self.red([0, 1])


# ---------------------------------------------------------------------------
# Elliptic-curve helpers (short Weierstrass y^2 = x^3 + a x + b over F_p).
# ---------------------------------------------------------------------------


def legendre(a, p):
    a %= p
    if a == 0:
        return 0
    return 1 if pow(a, (p - 1) // 2, p) == 1 else -1


def sqrt_mod(a, p):
    """Tonelli-Shanks; None if a is a non-residue."""
    a %= p
    if a == 0:
        return 0
    if legendre(a, p) != 1:
        return None
    if p % 4 == 3:
        return pow(a, (p + 1) // 4, p)
    q, s = p - 1, 0
    while q % 2 == 0:
        q //= 2
        s += 1
    z = 2
    while legendre(z, p) != -1:
        z += 1
    m, c, t, r = s, pow(z, q, p), pow(a, q, p), pow(a, (q + 1) // 2, p)
    while t != 1:
        i, tt = 0, t
        while tt != 1:
            tt = tt * tt % p
            i += 1
        b = pow(c, 1 << (m - i - 1), p)
        m, c, t, r = i, b * b % p, t * b * b % p, r * b % p
    return r


def ec_add(P, Q, a, p):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2:
        if (y1 + y2) % p == 0:
            return None
        lam = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p
    else:
        lam = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (lam * lam - x1 - x2) % p
    return (x3, (lam * (x1 - x3) - y1) % p)


def ec_mul(k, P, a, p):
    R = None
    while k:
        if k & 1:
            R = ec_add(R, P, a, p)
        P = ec_add(P, P, a, p)
        k >>= 1
    return R


def is_singular(a, b, p):
    return (4 * a * a * a + 27 * b * b) % p == 0


def j_invariant(a, b, p):
    num = 1728 * 4 * pow(a, 3, p) % p
    den = (4 * pow(a, 3, p) + 27 * b * b) % p
    return num * pow(den, -1, p) % p


def aut_order(a, b, p):
    if a % p == 0:
        return 6 if p % 3 == 1 else 2
    if b % p == 0:
        return 4 if p % 4 == 1 else 2
    return 2


def iso_key(a, b, p):
    """Key of the F_p-isomorphism class of y^2 = x^3 + a x + b.

    For j not in {0, 1728} the class is determined by j together with the
    quadratic-twist class, and the isogeny class fixes the twist through the
    trace; keying on j alone is then exact within one trace class.  For j = 0
    and j = 1728 the sextic / quartic twists are separated explicitly.
    """
    a %= p
    b %= p
    if a == 0:
        g = math.gcd(6, p - 1)
        return (0, pow(b, (p - 1) // g, p))
    if b == 0:
        g = math.gcd(4, p - 1)
        return (1728, pow(a, (p - 1) // g, p))
    return (j_invariant(a, b, p), 0)


def random_point(a, b, p, rng):
    while True:
        x = rng.randrange(p)
        rhs = (pow(x, 3, p) + a * x + b) % p
        y = sqrt_mod(rhs, p)
        if y is not None:
            return (x, y)


def trace_exact(a, b, p):
    """t = p + 1 - #E(F_p) by the character sum. O(p); toy fields only."""
    s = 0
    for x in range(p):
        s += legendre((x * x % p * x + a * x + b) % p, p)
    return -s


def curve_order_bsgs(a, b, p, rng, max_points=12):
    """#E(F_p) by baby-step giant-step on random points (Mestre-style).

    Returns the unique order in the Hasse interval killed by every sampled
    point; raises if the sampled points cannot pin it down.
    """
    lo = p + 1 - 2 * math.isqrt(p) - 1
    hi = p + 1 + 2 * math.isqrt(p) + 1
    candidates = None
    for _ in range(max_points):
        P = random_point(a, b, p, rng)
        m = math.isqrt(hi - lo) + 1
        baby = {}
        Q = None
        for j in range(m):
            baby.setdefault(Q, j)
            Q = ec_add(Q, P, a, p)
        # Q = [m]P
        mP = Q
        giant = ec_mul(lo, P, a, p)
        neg_mP = None if mP is None else (mP[0], (-mP[1]) % p)
        found = set()
        for i in range(m + 1):
            if giant in baby:
                n = lo + i * m - baby[giant]
                if lo <= n <= hi:
                    found.add(n)
            giant = ec_add(giant, mP, a, p)
        # `found` holds every n in the interval with [n]P = O only if the
        # baby table covers residues; verify each candidate explicitly.
        found = {n for n in found if ec_mul(n, P, a, p) is None}
        if not found:
            # fall back to a direct scan (should not happen)
            found = {n for n in range(lo, hi + 1) if ec_mul(n, P, a, p) is None}
        candidates = found if candidates is None else (candidates & found)
        if len(candidates) == 1:
            return next(iter(candidates))
        if not candidates:
            raise RuntimeError("inconsistent order candidates")
    raise RuntimeError("could not pin the curve order with random points")


def trace_of(a, b, p, rng, exact_limit=1 << 17):
    if p <= exact_limit:
        return trace_exact(a, b, p)
    return p + 1 - curve_order_bsgs(a, b, p, rng)


def verify_order(a, b, p, N, rng, samples=3):
    """Check [N]P = O for random P; with N prime and p > 16 this proves #E = N."""
    for _ in range(samples):
        P = random_point(a, b, p, rng)
        if ec_mul(N, P, a, p) is not None:
            return False
    return True


# ---------------------------------------------------------------------------
# Division polynomials.  psi_n = f_n(x) for n odd, psi_n = 2y g_n(x) for n even
# (y^2 = F = x^3 + a x + b, (2y)^2 = 4F).
# ---------------------------------------------------------------------------


class DivisionPolynomials:
    def __init__(self, a, b, p):
        self.a, self.b, self.p = a % p, b % p, p
        self.F = [b % p, a % p, 0, 1]
        self.F2 = pmul(self.F, self.F, p)
        a2 = a * a % p
        self.cache = {
            0: [],
            1: [1],
            2: [1],
            3: _trim([(-a2) % p, 12 * b % p, 6 * a % p, 0, 3]),
            4: _trim([(2 * (-8 * b * b - a * a * a)) % p,
                      (2 * (-4 * a * b)) % p,
                      (2 * (-5 * a2)) % p,
                      (2 * 20 * b) % p,
                      (2 * 5 * a) % p,
                      0, 2]),
        }

    def __call__(self, n):
        """f_n (n odd) or g_n (n even)."""
        p = self.p
        if n in self.cache:
            return self.cache[n]
        if n < 0:
            raise ValueError
        if n % 2 == 1:
            m = (n - 1) // 2
            if m % 2 == 1:
                val = psub(pmul(self(m + 2), pmul(self(m), pmul(self(m), self(m), p), p), p),
                           pscale(pmul(self.F2, pmul(self(m - 1),
                                                     pmul(self(m + 1), pmul(self(m + 1), self(m + 1), p), p), p), p),
                                  16, p), p)
            else:
                val = psub(pscale(pmul(self.F2, pmul(self(m + 2),
                                                     pmul(self(m), pmul(self(m), self(m), p), p), p), p), 16, p),
                           pmul(self(m - 1), pmul(self(m + 1), pmul(self(m + 1), self(m + 1), p), p), p), p)
        else:
            m = n // 2
            if m % 2 == 0:
                inner = psub(pmul(self(m + 2), pmul(self(m - 1), self(m - 1), p), p),
                             pmul(self(m - 2), pmul(self(m + 1), self(m + 1), p), p), p)
            else:
                inner = psub(pmul(self(m + 2), pmul(self(m - 1), self(m - 1), p), p),
                             pmul(self(m - 2), pmul(self(m + 1), self(m + 1), p), p), p)
            val = pmul(self(m), inner, p)
        self.cache[n] = val
        return val


# ---------------------------------------------------------------------------
# Rational ell-subgroups, kernel polynomials, and Velu / Kohel codomains.
# ---------------------------------------------------------------------------


def x_only_multiples(K: ExtField, a, b, x1, n):
    """[x(Q), x(2Q), ..., x(nQ)] in K for a point Q with x(Q) = x1, using
    differential addition.  Requires n <= ord(Q) - 2 and ord(Q) odd."""
    p = K.p
    xs = [x1]
    if n == 1:
        return xs
    A = K.const(a)
    B = K.const(b)
    # doubling: x(2Q) = ((x^2 - a)^2 - 8 b x) / (4 (x^3 + a x + b))
    x1sq = K.mul(x1, x1)
    num = K.sub(K.mul(K.sub(x1sq, A), K.sub(x1sq, A)), K.mul(K.const(8 * b), x1))
    den = K.mul(K.const(4), K.add(K.add(K.mul(x1sq, x1), K.mul(A, x1)), B))
    x2 = K.mul(num, K.inv(den))
    xs.append(x2)
    for i in range(2, n):
        xi, xim1 = xs[-1], xs[-2]
        # x((i+1)Q) = 2((x_i x_1 + a)(x_i + x_1) + 2b)/(x_i - x_1)^2 - x((i-1)Q)
        num = K.mul(K.const(2), K.add(K.mul(K.add(K.mul(xi, x1), A), K.add(xi, x1)), K.const(2 * b)))
        diff = K.sub(xi, x1)
        den = K.mul(diff, diff)
        xs.append(K.sub(K.mul(num, K.inv(den)), xim1))
    return xs


def rational_subgroups(a, b, p, ell, rng):
    """Kernel polynomials (monic, in F_p[x], degree (ell-1)/2, or degree 1 for
    ell = 2) of every F_p-rational cyclic subgroup of order ell."""
    if ell == 2:
        cubic = [b % p, a % p, 0, 1]
        xp = px_pow_p_mod(cubic, p)
        g = pgcd(cubic, psub(xp, [0, 1], p), p)
        roots = []
        if len(g) - 1 >= 1:
            # explicit roots of a degree <= 3 polynomial
            for f in equal_degree_factor(g, 1, p, rng):
                roots.append((-f[0]) % p)
        return [_trim([(-r) % p, 1]) for r in sorted(roots)]
    n = (ell - 1) // 2
    dp = DivisionPolynomials(a, b, p)
    psi = pmonic(dp(ell), p)
    if len(psi) - 1 != (ell * ell - 1) // 2:
        raise RuntimeError(f"psi_{ell} has wrong degree {len(psi) - 1}")
    kernels = {}
    for d, g in distinct_degree_factor(psi, p, max_degree=n):
        if d is None or n % d:
            continue
        for q in equal_degree_factor(g, d, p, rng):
            K = ExtField(p, q)
            x1 = K.red([0, 1]) if K.r > 1 else K.const((-q[0]) % p)
            xs = x_only_multiples(K, a, b, x1, n)
            # kernel polynomial prod (x - x_i), expanded over K
            h = [K.const(1)]
            for xi in xs:
                newh = [K.const(0)] * (len(h) + 1)
                for i, c in enumerate(h):
                    newh[i + 1] = K.add(newh[i + 1], c)
                    newh[i] = K.sub(newh[i], K.mul(c, xi))
                h = newh
            if all(K.is_const(c) for c in h):
                hp = _trim([(c[0] if c else 0) for c in h])
                kernels[tuple(hp)] = hp
    return [list(k) for k in sorted(kernels)]


def velu_from_kernel_polynomial(a, b, p, h):
    """Codomain (a', b') of the separable isogeny with kernel polynomial h."""
    n = len(h) - 1
    if n == 1 and peval([b % p, a % p, 0, 1], (-h[0]) % p, p) == 0:
        # 2-isogeny: kernel {O, (x0, 0)}
        x0 = (-h[0]) % p
        v = (3 * x0 * x0 + a) % p
        w = x0 * v % p
        return (a - 5 * v) % p, (b - 7 * w) % p
    # sigma_k = (-1)^k * coeff of x^{n-k}
    sig = [0] * 4
    for k in range(1, 4):
        if n - k >= 0:
            sig[k] = ((-1) ** k * h[n - k]) % p
    p1 = sig[1]
    p2 = (sig[1] * p1 - 2 * sig[2]) % p
    p3 = (sig[1] * p2 - sig[2] * p1 + 3 * sig[3]) % p
    v = (6 * p2 + 2 * a * n) % p
    w = (10 * p3 + 6 * a * p1 + 4 * b * n) % p
    return (a - 5 * v) % p, (b - 7 * w) % p


def phi2(X, Y, p):
    return (pow(X, 3, p) + pow(Y, 3, p) - X * X % p * (Y * Y % p)
            + 1488 * (X * X % p * Y + X * (Y * Y % p))
            - 162000 * (X * X + Y * Y) + 40773375 * X * Y
            + 8748000000 * (X + Y) - 157464000000000) % p


def phi3(X, Y, p):
    X2, X3, X4 = X * X % p, pow(X, 3, p), pow(X, 4, p)
    Y2, Y3, Y4 = Y * Y % p, pow(Y, 3, p), pow(Y, 4, p)
    return (X4 + Y4 - X3 * Y3 + 2232 * (X3 * Y2 + X2 * Y3)
            - 1069956 * (X3 * Y + X * Y3) + 36864000 * (X3 + Y3)
            + 2587918086 * X2 * Y2 + 8900222976000 * (X2 * Y + X * Y2)
            + 452984832000000 * (X2 + Y2) - 770845966336000000 * X * Y
            + 1855425871872000000000 * (X + Y)) % p


MODULAR = {2: phi2, 3: phi3}

# generating primes tried in order; inert ones are skipped, larger ones are
# admitted only when the smaller ones cannot close the class
DEFAULT_PRIMES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47)


# ---------------------------------------------------------------------------
# Class-number certificate (binary quadratic forms; no numpy).
# ---------------------------------------------------------------------------


def class_number_weighted(D: int) -> Fraction:
    """Weighted h(D): reduced primitive forms, 1/2 for (A,0,A), 1/3 for (A,A,A)."""
    if D >= 0 or D % 4 not in (0, 1):
        return Fraction(0)
    hw = Fraction(0)
    Amax = math.isqrt(-D // 3) + 1
    for A in range(1, Amax + 1):
        for B in range(-A + 1, A + 1):
            num = B * B - D
            if num % (4 * A):
                continue
            C = num // (4 * A)
            if C < A:
                continue
            if (A == C or B == A) and B < 0:
                continue
            if math.gcd(math.gcd(A, abs(B)), C) != 1:
                continue
            if A == B == C:
                hw += Fraction(1, 3)
            elif A == C and B == 0:
                hw += Fraction(1, 2)
            else:
                hw += 1
    return hw


def hurwitz_class_number(N: int) -> Fraction:
    total = Fraction(0)
    f = 1
    while f * f <= N:
        if N % (f * f) == 0:
            D = -(N // (f * f))
            if D % 4 in (0, 1):
                total += class_number_weighted(D)
        f += 1
    return total


def fundamental_discriminant(D: int) -> tuple[int, int]:
    f, m, d = 1, -D, 2
    while d * d <= m:
        while m % (d * d) == 0:
            m //= d * d
            f *= d
        d += 1
    D0 = -m
    if D0 % 4 not in (0, 1):
        D0 *= 4
        f //= 2
    return D0, f


# ---------------------------------------------------------------------------
# Isogeny-class enumeration with certificate.
# ---------------------------------------------------------------------------


@dataclass
class ClassMember:
    a: int
    b: int
    j: int
    aut: int
    depth: int          # BFS depth from the input curve (in isogeny steps)
    via: str            # "input" or "ell=<l> from j=<j>"


@dataclass
class ClassEnumeration:
    p: int
    trace: int
    order: int
    discriminant: int
    fundamental_discriminant: int
    conductor: int
    primes_used: list[int]
    members: list[ClassMember]
    observed_weighted: str
    predicted_weighted: str
    certified: bool
    coverage_fraction: float
    order_checks_passed: int
    modular_checks_passed: int
    seconds: float


def enumerate_isogeny_class(a, b, p, rng, primes=DEFAULT_PRIMES,
                            max_members=None, exact_trace_limit=1 << 17,
                            verbose=False) -> ClassEnumeration:
    t0 = time.time()
    a %= p
    b %= p
    if is_singular(a, b, p):
        raise ValueError("singular input curve")
    t = trace_of(a, b, p, rng, exact_trace_limit)
    if t % p == 0:
        raise ValueError("supersingular input curve: out of scope")
    N = p + 1 - t
    D = t * t - 4 * p
    D0, f = fundamental_discriminant(D)
    predicted = hurwitz_class_number(4 * p - t * t)

    members: dict = {}
    key0 = iso_key(a, b, p)
    members[key0] = ClassMember(a, b, j_invariant(a, b, p), aut_order(a, b, p), 0, "input")
    frontier = [key0]
    used = []
    order_ok = 0
    mod_ok = 0
    n_prime = all(N % q for q in range(2, min(1000, math.isqrt(N) + 1)))

    explored: set = set()

    def expand(ell):
        """One pass over every member not yet explored at this ell."""
        nonlocal order_ok, mod_ok
        new_any = False
        queue = [k for k in members if (k, ell) not in explored]
        while queue:
            key = queue.pop()
            if (key, ell) in explored:
                continue
            explored.add((key, ell))
            m = members[key]
            for h in rational_subgroups(m.a, m.b, p, ell, rng):
                a2, b2 = velu_from_kernel_polynomial(m.a, m.b, p, h)
                if is_singular(a2, b2, p):
                    raise RuntimeError("Velu produced a singular curve")
                if not verify_order(a2, b2, p, N, rng):
                    raise RuntimeError(f"codomain of {ell}-isogeny does not have order {N}")
                order_ok += 1
                if ell in MODULAR:
                    if MODULAR[ell](m.j, j_invariant(a2, b2, p), p) != 0:
                        raise RuntimeError(f"Phi_{ell}(j, j') != 0")
                    mod_ok += 1
                k2 = iso_key(a2, b2, p)
                if k2 not in members:
                    members[k2] = ClassMember(a2, b2, j_invariant(a2, b2, p), aut_order(a2, b2, p),
                                              m.depth + 1, f"ell={ell} from j={m.j}")
                    queue.append(k2)
                    new_any = True
                    if max_members and len(members) >= max_members:
                        return new_any
        return new_any

    def observed():
        return sum(Fraction(2, m.aut) for m in members.values())

    def has_rational_isogenies(ell):
        # ell inert in Q(sqrt(D)) and coprime to D: no rational ell-isogeny in the class
        if ell == p or (D % ell == 0):
            return ell != p
        return legendre(D, ell) == 1 if ell != 2 else (D % 8 == 1)

    active = [ell for ell in primes if has_rational_isogenies(ell)]
    # Close the class under the SMALLEST primes first: a prime is admitted to
    # the generating set only when the primes below it have reached a fixed
    # point short of the census.  Factoring psi_ell costs O(ell^4 log p) per
    # member, so this keeps ell = 13 off the table when {2, 3, 5} suffice.
    for idx in range(len(active)):
        gens_now = active[:idx + 1]
        while observed() != predicted:
            changed = False
            for ell in gens_now:
                if observed() == predicted:
                    break
                if ell not in used:
                    used.append(ell)
                if expand(ell):
                    changed = True
                if verbose:
                    print(f"  ell={ell}: {len(members)} members, weighted {observed()} / {predicted}",
                          file=sys.stderr)
                if max_members and len(members) >= max_members:
                    changed = False
                    break
            if not changed:
                break
        if observed() == predicted or (max_members and len(members) >= max_members):
            break
    obs = observed()
    if obs > predicted:
        raise RuntimeError("enumeration exceeds the class number: isomorphism key or Velu bug")
    certified = (obs == predicted)
    return ClassEnumeration(
        p=p, trace=t, order=N, discriminant=D, fundamental_discriminant=D0, conductor=f,
        primes_used=used, members=list(members.values()),
        observed_weighted=str(obs), predicted_weighted=str(predicted),
        certified=certified, coverage_fraction=float(obs / predicted) if predicted else 0.0,
        order_checks_passed=order_ok, modular_checks_passed=mod_ok,
        seconds=time.time() - t0)


# ---------------------------------------------------------------------------
# Functionals.
# ---------------------------------------------------------------------------


def s3_coeffs(a, b, p):
    """S_3(x1, x2, x3) as {(e1, e2, e3): coeff} for y^2 = x^3 + a x + b."""
    a %= p
    b %= p
    terms = {}

    def add(mono, c):
        c %= p
        if c:
            terms[mono] = (terms.get(mono, 0) + c) % p
            if terms[mono] == 0:
                del terms[mono]

    # (x1 - x2)^2 x3^2
    add((2, 0, 2), 1)
    add((1, 1, 2), -2)
    add((0, 2, 2), 1)
    # -2((x1 + x2)(x1 x2 + a) + 2b) x3
    add((2, 1, 1), -2)
    add((1, 2, 1), -2)
    add((1, 0, 1), -2 * a)
    add((0, 1, 1), -2 * a)
    add((0, 0, 1), -4 * b)
    # (x1 x2 - a)^2 - 4b(x1 + x2)
    add((2, 2, 0), 1)
    add((1, 1, 0), -2 * a)
    add((0, 0, 0), a * a)
    add((1, 0, 0), -4 * b)
    add((0, 1, 0), -4 * b)
    return terms


def f1_support(a, b, p) -> int:
    return len(s3_coeffs(a, b, p))


def s3_specialize(a, b, p, x3):
    """S_3(x1, x2, x3) with x3 fixed: {(e1, e2): coeff}."""
    out = {}
    for (e1, e2, e3), c in s3_coeffs(a, b, p).items():
        v = c * pow(x3, e3, p) % p
        if v:
            k = (e1, e2)
            out[k] = (out.get(k, 0) + v) % p
            if out[k] == 0:
                del out[k]
    return out


def s3_fibre_poly(a, b, p, x1, x3):
    """S_3(x1, X, x3) as a univariate polynomial in X."""
    out = [0] * 3
    for (e1, e2, e3), c in s3_coeffs(a, b, p).items():
        out[e2] = (out[e2] + c * pow(x1, e1, p) * pow(x3, e3, p)) % p
    return _trim(out)


def f3_fibre_roots(a, b, p, k, samples, rng):
    """Mean / max number of F_p-roots in u2 of S_3(u1^k, u2^k, x_R)."""
    total = 0
    mx = 0
    hist = {}
    for _ in range(samples):
        R = random_point(a, b, p, rng)
        u1 = rng.randrange(1, p)
        x1 = pow(u1, k, p)
        g = s3_fibre_poly(a, b, p, x1, R[0])       # polynomial in X = u2^k
        f = [0] * (2 * k + 1)
        for e, c in enumerate(g):
            f[e * k] = c
        f = _trim(f)
        r = count_roots(f, p) if len(f) > 1 else 0
        total += r
        mx = max(mx, r)
        hist[r] = hist.get(r, 0) + 1
    return {"mean": total / samples, "max": mx, "histogram": dict(sorted(hist.items()))}


def _monomials_upto(D):
    return [(i, d - i) for d in range(D + 1) for i in range(d + 1)]


def f2_first_fall_degree(a, b, p, h, x_R, D_max):
    """First-fall degree of { S_3(x1, x2, x_R), x1^h - 1, x2^h - 1 } over F_p.

    Degree-graded Macaulay matrices in two variables; the first D at which the
    echelon form of M_D holds more polynomials of degree < D than M_{D-1}
    does is the first fall.  Returns None if no fall occurs up to D_max.
    """
    gens = [dict(s3_specialize(a, b, p, x_R)),
            {(h, 0): 1, (0, 0): p - 1},
            {(0, h): 1, (0, 0): p - 1}]
    gdeg = [max(i + j for (i, j) in g) for g in gens]

    def order_key(m):
        # degree-compatible (grevlex on 2 variables): degree, then x1 exponent
        return (m[0] + m[1], m[0])

    pivots: dict = {}   # leading monomial -> reduced row (dict)

    def reduce_insert(row):
        # standard sparse Gaussian elimination with a fixed pivot set
        while row:
            lead = max(row, key=order_key)
            if lead in pivots:
                prow = pivots[lead]
                c = row[lead]
                for m, v in prow.items():
                    nv = (row.get(m, 0) - c * v) % p
                    if nv:
                        row[m] = nv
                    else:
                        row.pop(m, None)
            else:
                inv = pow(row[lead], -1, p)
                pivots[lead] = {m: v * inv % p for m, v in row.items()}
                return True
        return False

    rank_prev = 0
    for D in range(min(gdeg), D_max + 1):
        for g, dg in zip(gens, gdeg):
            if D < dg:
                continue
            for (i, j) in _monomials_upto(D - dg):
                if i + j != D - dg:
                    continue        # exact degree D rows only; lower ones are already in
                row = {}
                for (e1, e2), c in g.items():
                    row[(e1 + i, e2 + j)] = c
                reduce_insert(row)
        low = sum(1 for m in pivots if m[0] + m[1] < D)
        if low > rank_prev:
            return D
        rank_prev = len(pivots)
    return None


# ---------------------------------------------------------------------------
# Driver: measure every class member and a matched null set.
# ---------------------------------------------------------------------------


def random_curve_with_other_trace(p, t, rng, exact_trace_limit):
    while True:
        a, b = rng.randrange(p), rng.randrange(p)
        if is_singular(a, b, p) or a == 0 or b == 0:
            continue
        tt = trace_of(a, b, p, rng, exact_trace_limit)
        if tt % p and tt != t and tt != -t:
            return a, b, tt


def measure(a, b, p, k, h, samples, D_max, rng, with_f2=True):
    out = {"F1_support": f1_support(a, b, p)}
    out["F3"] = f3_fibre_roots(a, b, p, k, samples, rng)
    if with_f2 and h:
        R = random_point(a, b, p, rng)
        out["F2_dff"] = f2_first_fall_degree(a, b, p, h, R[0], D_max)
    return out


def choose_subgroup_order(p, target=8):
    """Largest divisor h of p-1 with 2 <= h <= target (F2 factor-base size)."""
    best = None
    for h in range(2, target + 1):
        if (p - 1) % h == 0:
            best = h
    return best


def search(p, a, b, seed=1, k=4, h=None, samples=64, D_max=None, nulls=8,
           primes=DEFAULT_PRIMES, with_f2=True, exact_trace_limit=1 << 17,
           verbose=False):
    rng = random.Random(seed)
    if h is None:
        h = choose_subgroup_order(p)
    if D_max is None:
        D_max = (h or 0) + 8
    enum = enumerate_isogeny_class(a, b, p, rng, primes=primes,
                                   exact_trace_limit=exact_trace_limit, verbose=verbose)
    t1 = time.time()
    rows = []
    for m in enum.members:
        mrng = random.Random(f"{seed}:member:{m.a}:{m.b}")
        val = measure(m.a, m.b, p, k, h, samples, D_max, mrng, with_f2)
        rows.append({"a": m.a, "b": m.b, "j": m.j, "aut": m.aut, "depth": m.depth,
                     "via": m.via, **val})
    null_rows = []
    for i in range(nulls):
        na, nb, nt = random_curve_with_other_trace(p, enum.trace, rng, exact_trace_limit)
        nrng = random.Random(f"{seed}:null:{na}:{nb}")
        val = measure(na, nb, p, k, h, samples, D_max, nrng, with_f2)
        null_rows.append({"a": na, "b": nb, "trace": nt, "j": j_invariant(na, nb, p), **val})
    t2 = time.time()

    def band(vals):
        vals = [v for v in vals if v is not None]
        if not vals:
            return None
        mu = sum(vals) / len(vals)
        sd = (sum((v - mu) ** 2 for v in vals) / max(1, len(vals) - 1)) ** 0.5
        return {"min": min(vals), "max": max(vals), "mean": mu, "sd": sd, "n": len(vals)}

    f3_null = band([r["F3"]["mean"] for r in null_rows])
    # pooled per-sample variance of the root count on the null set; roots in
    # u2 come in orbits of the k-th roots of unity, so the count takes values
    # in {0, k, 2k} and its variance is of order k, not 1
    n_tot = sum(sum(r["F3"]["histogram"].values()) for r in null_rows) or 1
    mean_tot = sum(int(v) * c for r in null_rows for v, c in r["F3"]["histogram"].items()) / n_tot
    var_tot = sum((int(v) - mean_tot) ** 2 * c for r in null_rows
                  for v, c in r["F3"]["histogram"].items()) / max(1, n_tot - 1)
    se = (max(var_tot, float(k)) / samples) ** 0.5
    thresh = 4 * max(se, f3_null["sd"] if f3_null and f3_null["sd"] else se)
    survivors = []
    for r in rows:
        flags = []
        if r["F1_support"] != 13:
            flags.append(f"F1 support {r['F1_support']} != 13")
        if f3_null and abs(r["F3"]["mean"] - f3_null["mean"]) > thresh:
            flags.append(f"F3 mean {r['F3']['mean']:.3f} outside null band {f3_null['mean']:.3f}+-{thresh:.3f}")
        null_dff = {x["F2_dff"] for x in null_rows if "F2_dff" in x}
        if with_f2 and h and r.get("F2_dff") not in null_dff:
            flags.append(f"F2 d_ff {r.get('F2_dff')} not in null set {sorted(x for x in null_dff if x is not None)}")
        if flags:
            survivors.append({"j": r["j"], "a": r["a"], "b": r["b"], "flags": flags})

    report = {
        "instrument": "tools/isogeny_dreg_search.py",
        "claim_tier": "toy",
        "input": {"p": p, "a": a % p, "b": b % p, "seed": seed, "k": k, "h": h,
                  "samples": samples, "D_max": D_max, "nulls": nulls,
                  "primes": list(primes), "with_f2": with_f2},
        "class": {kk: vv for kk, vv in asdict(enum).items() if kk != "members"},
        "class_size": len(enum.members),
        "exhaustive": enum.certified,
        "exhaustive_note": ("every F_p-isomorphism class with this trace was reached and the "
                            "weighted count equals H(4p - t^2)" if enum.certified else
                            f"NOT exhaustive: coverage {enum.coverage_fraction:.4f} of the class; "
                            "add primes or raise max_members before any negative is claimed"),
        "members": rows,
        "null": null_rows,
        "summary": {
            "F1_support": band([r["F1_support"] for r in rows]),
            "F1_support_null": band([r["F1_support"] for r in null_rows]),
            "F2_dff": band([r.get("F2_dff") for r in rows]) if with_f2 else None,
            "F2_dff_null": band([r.get("F2_dff") for r in null_rows]) if with_f2 else None,
            "F3_mean": band([r["F3"]["mean"] for r in rows]),
            "F3_mean_null": f3_null,
            "F3_max_over_class": max(r["F3"]["max"] for r in rows),
            "F3_max_over_null": max(r["F3"]["max"] for r in null_rows) if null_rows else None,
            "F3_flag_threshold": thresh,
        },
        "survivors": survivors,
        "timing_seconds": {"enumeration": enum.seconds, "measurement": t2 - t1},
        "controls": {
            "order_checks_passed": enum.order_checks_passed,
            "modular_polynomial_checks_passed": enum.modular_checks_passed,
            "structural_tell": ("F3 must vary BETWEEN classes (null curves) at least as much as "
                                "within; a within-class spread below the null spread is an "
                                "instrument constant, not a finding"),
        },
    }
    return report


# ---------------------------------------------------------------------------
# Cost model for the 2^40 plan.
# ---------------------------------------------------------------------------


def cost_model(bits_list):
    rows = []
    for bits in bits_list:
        p = 2 ** bits
        # h(D) ~ sqrt(|D|) L(1,chi) / pi with |D| ~ 4p, L(1,chi) taken as 1
        h = (2 * math.sqrt(p)) / math.pi
        primes = p / (bits * math.log(2))
        rows.append({
            "log2_p": bits,
            "class_size_estimate": h,
            "log2_class_size": math.log2(h),
            "primes_below_estimate": primes,
            "log2_curves_all_primes": math.log2(primes * h) if primes * h > 0 else 0,
            "reference_engine_seconds_per_member": 0.05,
            "reference_engine_class_hours": h * 0.05 / 3600,
        })
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--p", type=int)
    ap.add_argument("--a", type=int)
    ap.add_argument("--b", type=int)
    ap.add_argument("--bits", type=int, help="random generic curve at a random prime of this size")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--k", type=int, default=4, help="factor base x = u^k for F3")
    ap.add_argument("--h", type=int, help="subgroup order for F2 (divides p-1)")
    ap.add_argument("--samples", type=int, default=64)
    ap.add_argument("--D-max", type=int)
    ap.add_argument("--nulls", type=int, default=8)
    ap.add_argument("--primes", default=",".join(str(x) for x in DEFAULT_PRIMES))
    ap.add_argument("--no-f2", action="store_true")
    ap.add_argument("--exact-trace-limit", type=int, default=1 << 17)
    ap.add_argument("--out")
    ap.add_argument("--cost-model", action="store_true")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args(argv)

    if args.cost_model:
        print(json.dumps(cost_model([16, 20, 24, 28, 32, 36, 40]), indent=2))
        return 0

    rng = random.Random(args.seed)
    if args.bits:
        while True:
            p = rng.randrange(2 ** (args.bits - 1), 2 ** args.bits) | 1
            if all(p % q for q in range(3, math.isqrt(p) + 1, 2)) and p > 3:
                break
        while True:
            a, b = rng.randrange(1, p), rng.randrange(1, p)
            if not is_singular(a, b, p):
                break
    else:
        p, a, b = args.p, args.a, args.b
        if p is None or a is None or b is None:
            ap.error("give --p --a --b or --bits")
    primes = tuple(int(x) for x in args.primes.split(","))
    report = search(p, a, b, seed=args.seed, k=args.k, h=args.h, samples=args.samples,
                    D_max=args.D_max, nulls=args.nulls, primes=primes, with_f2=not args.no_f2,
                    exact_trace_limit=args.exact_trace_limit, verbose=args.verbose)
    text = json.dumps(report, indent=2)
    if args.out:
        with open(args.out, "w") as fh:
            fh.write(text + "\n")
        s = report["summary"]
        print(f"p={p} a={a} b={b} trace={report['class']['trace']} class_size={report['class_size']} "
              f"exhaustive={report['exhaustive']} survivors={len(report['survivors'])}")
        print(f"F1 class {s['F1_support']} | F3 mean class {s['F3_mean']} | null {s['F3_mean_null']}")
        if s["F2_dff"]:
            print(f"F2 d_ff class {s['F2_dff']} | null {s['F2_dff_null']}")
        print(f"written {args.out}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
