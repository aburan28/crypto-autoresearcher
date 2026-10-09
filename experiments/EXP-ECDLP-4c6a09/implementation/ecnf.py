"""Elliptic curves over a number field K = Q[t]/(g): bounded point search, residues at
degree-one primes, torsion bounds and the Galois trace relation. Pure Python 3 stdlib.
Byte-identical copies live in every SNFS-G implementation directory.

E: y^2 = x^3 + A x + B with A, B rational (a curve over Q base-changed to K).
"""
from __future__ import annotations

import itertools
import math
import random
from fractions import Fraction

import nfield

# ----------------------------------------------------------------------------
# finite-field curve arithmetic (affine)
# ----------------------------------------------------------------------------


def fp_add(P, Q, a, p):
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


def fp_mul(k, P, a, p):
    R = None
    while k:
        if k & 1:
            R = fp_add(R, P, a, p)
        P = fp_add(P, P, a, p)
        k >>= 1
    return R


def fp_count(p, a, b):
    """Exact point count by Legendre sums (p < ~2^21)."""
    table = bytearray(p)
    for y in range(p):
        table[y * y % p] = 1
    n = p + 1
    for x in range(p):
        v = (x * x * x + a * x + b) % p
        if v == 0:
            continue
        n += 1 if table[v] else -1
    return n


def fp_order_bsgs(p, a, b, rng, tries=6):
    """Group order for larger p: BSGS order candidates intersected over random points."""
    from math import isqrt

    def random_point():
        while True:
            x = rng.randrange(p)
            v = (x * x * x + a * x + b) % p
            if v == 0:
                continue
            if pow(v, (p - 1) // 2, p) == 1:
                return (x, nfield._sqrt_mod_prime(v, p))

    w = isqrt(p)
    lo = p + 1 - 2 * w - 1
    width = 4 * w + 3
    m = isqrt(width) + 1
    cands = None
    for _ in range(tries):
        P = random_point()
        baby = {}
        R = None
        for j in range(m):
            baby.setdefault(R, j)
            R = fp_add(R, P, a, p)
        mP = R
        base = fp_mul(lo, P, a, p)
        c = set()
        for i in range(m + 2):
            if base in baby:
                c.add(lo + i * m - baby[base])
            neg = None if base is None else (base[0], (-base[1]) % p)
            if neg in baby:
                c.add(lo + i * m + baby[neg])
            base = fp_add(base, mP, a, p)
        c = {N for N in c if lo <= N <= lo + width and fp_mul(N, P, a, p) is None}
        cands = c if cands is None else cands & c
        if len(cands) == 1:
            return next(iter(cands))
    return None


# ----------------------------------------------------------------------------
# curves over K
# ----------------------------------------------------------------------------


class CurveNF:
    """y^2 = x^3 + a2 x^2 + a4 x + a6 over K with rational coefficients. The search runs on this
    model (so a curve given by a small b-model keeps its torsion in small shells); every finite-field
    computation uses the short model x' = x + a2/3: y^2 = x'^3 + A x' + B."""

    def __init__(self, K: nfield.NumberField, A, B, a2=0):
        self.K = K
        self.a2 = Fraction(a2)
        self.a4 = Fraction(A)
        self.a6 = Fraction(B)
        self.shift = self.a2 / 3
        self.A = self.a4 - self.a2 ** 2 / 3
        self.B = self.a6 - self.a2 * self.a4 / 3 + 2 * self.a2 ** 3 / 27
        self.a2_elt = K.from_rational(self.a2)
        self.a4_elt = K.from_rational(self.a4)
        self.a6_elt = K.from_rational(self.a6)
        assert 4 * self.A ** 3 + 27 * self.B ** 2 != 0

    def rhs(self, x):
        K = self.K
        x2 = K.mul(x, x)
        return K.add(K.add(K.add(K.mul(x2, x), K.mul(self.a2_elt, x2)), K.mul(self.a4_elt, x)), self.a6_elt)

    def rhs_embed(self, x_num, e_inv, q, roots):
        """Embeddings of x^3 + a2 x^2 + a4 x + a6 at each root mod q, for x = x_num / e (integer coeffs)."""
        a2 = self.a2.numerator * pow(self.a2.denominator, -1, q) % q
        a4 = self.a4.numerator * pow(self.a4.denominator, -1, q) % q
        a6 = self.a6.numerator * pow(self.a6.denominator, -1, q) % q
        out = []
        for r in roots:
            xv = 0
            pw = 1
            for c in x_num:
                if c:
                    xv = (xv + c * pw) % q
                pw = pw * r % q
            xv = xv * e_inv % q
            out.append(((xv + a2) * xv % q * xv + a4 * xv + a6) % q)
        return out

    def reduce_point(self, P, q, root):
        """Reduction of a K-point at the degree-one prime (t - root, q), in short-model coordinates;
        None if the point is not integral there."""
        try:
            x = self.K.embed(P[0], q, root)
            y = self.K.embed(P[1], q, root)
        except ValueError:
            return None
        s = self.shift.numerator * pow(self.shift.denominator, -1, q) % q
        return ((x + s) % q, y)

    # --- bounded point search --------------------------------------------
    def iter_search(self, aux_primes, max_work, denominators=(1, 2, 3, 4), checkpoints=(), seed=0):
        """Lazily enumerate x = a(t)/e with coefficient vectors in increasing sup-norm shells.
        Yields ("point", tried, shells_completed, P) for each point found,
        ("shell", tried, shells_completed, None) after each completed shell, and
        ("checkpoint", tried, shells_completed, None) the moment `tried` reaches each value in
        `checkpoints`; stops once `max_work` candidates have been tried.
        A shell that fits in the remaining budget (at most twice it) is enumerated exhaustively in a
        seeded random order; a larger shell is sampled uniformly without replacement, so a partial
        shell is never biased towards one corner of the coefficient box. Deterministic for a given
        (seed, max_work, checkpoints)."""
        K = self.K
        d = K.d
        aux = aux_primes
        aux_roots = {q: K.roots_mod(q) for q in aux}
        e_inv = {e: {q: pow(e, -1, q) for q in aux} for e in denominators}
        rng = random.Random(f"ecnf-search:{seed}:{d}")
        checkpoints = sorted(set(int(c) for c in checkpoints))
        cp_i = 0
        tried = 0
        shells_done = 0
        seen_x = set()
        X = 0
        while tried < max_work:
            for e in denominators:
                for vec in _shell_order(d, X, max_work - tried, rng):
                    if tried >= max_work:
                        return
                    if e > 1 and any(vec) and math.gcd(e, *[abs(v) for v in vec if v]) != 1:
                        continue  # not in lowest terms
                    if not any(vec) and e > 1:
                        continue
                    tried += 1
                    while cp_i < len(checkpoints) and tried >= checkpoints[cp_i]:
                        yield ("checkpoint", tried, shells_done, None)
                        cp_i += 1
                    ok = True
                    for q in aux:
                        for v in self.rhs_embed(vec, e_inv[e][q], q, aux_roots[q]):
                            if v == 0:
                                ok = None
                                break
                            if pow(v, (q - 1) // 2, q) != 1:
                                ok = False
                                break
                        if ok is not True:
                            break
                    if ok is False:
                        continue
                    x = K.elt([Fraction(v, e) for v in vec])
                    if x in seen_x:
                        continue
                    seen_x.add(x)
                    z = self.rhs(x)
                    if K.is_zero(z):
                        yield ("point", tried, shells_done, (x, K.from_rational(0)))
                        continue
                    y = K.sqrt(z, aux)
                    if y is None:
                        continue
                    yield ("point", tried, shells_done, (x, y))
                    yield ("point", tried, shells_done, (x, K.neg(y)))
            shells_done = X + 1
            X += 1
            yield ("shell", tried, shells_done, None)

    def search(self, work, aux_primes, denominators=(1, 2, 3, 4), seed=0):
        """Eager wrapper: (points found, candidates tried, shells completed) after `work` tries."""
        points, tried, shells = [], 0, 0
        for kind, tried, shells, P in self.iter_search(aux_primes, work, denominators, seed=seed):
            if kind == "point":
                points.append(P)
        return points, tried, shells


def _shell_size(d, X):
    return 1 if X == 0 else (2 * X + 1) ** d - (2 * X - 1) ** d


def _shell_order(d, X, budget, rng):
    """Vectors of sup-norm exactly X: exhaustive in seeded random order when the shell is at most
    twice the remaining budget, otherwise uniform samples without replacement (rejection from the
    box [-X, X]^d; the shell is then much larger than the sample so rejections are cheap)."""
    size = _shell_size(d, X)
    if size <= 2 * budget:
        vecs = list(_shell(d, X))
        rng.shuffle(vecs)
        yield from vecs
        return
    seen = set()
    while len(seen) < budget:
        vec = tuple(rng.randint(-X, X) for _ in range(d))
        if max(abs(v) for v in vec) != X or vec in seen:
            continue
        seen.add(vec)
        yield vec


def _shell(d, X):
    """Integer vectors of length d with sup-norm exactly X, deterministic order, O(size) work:
    split on the first coordinate i with |v_i| = X (earlier coordinates lie in [-(X-1), X-1])."""
    if X == 0:
        yield tuple([0] * d)
        return
    inner = range(-(X - 1), X)
    full = range(-X, X + 1)
    for i in range(d):
        for head in itertools.product(inner, repeat=i):
            for s in (-X, X):
                for tail in itertools.product(full, repeat=d - i - 1):
                    yield head + (s,) + tail


# ----------------------------------------------------------------------------
# torsion bound and the trace relation
# ----------------------------------------------------------------------------


def torsion_bound(curve: CurveNF, primes, order_fn):
    """gcd of #E(F_q) over completely split primes q bounds |E(K)_tors| (and |E(Q)_tors|)."""
    g = 0
    for q in primes:
        a = curve.A.numerator * pow(curve.A.denominator, -1, q) % q
        b = curve.B.numerator * pow(curve.B.denominator, -1, q) % q
        g = math.gcd(g, order_fn(q, a, b))
    return g


def point_order_mod(P, a, p, T):
    """Smallest divisor n of T with [n]P = O, or None if no divisor works."""
    for n in sorted(_divisors(T)):
        if fp_mul(n, P, a, p) is None:
            return n
    return None


def _divisors(n):
    out = {1}
    q = 2
    m = n
    while q * q <= m:
        while m % q == 0:
            out |= {x * q for x in out}
            m //= q
        q += 1
    if m > 1:
        out |= {x * m for x in out}
    return out


def is_torsion_candidate(curve: CurveNF, P, split_primes, T):
    """True if P could be torsion: at every split prime the reduction's order divides T.
    A False is a proof that P is not torsion (torsion injects into E(F_q) for q not dividing it)."""
    for q in split_primes:
        a = curve.A.numerator * pow(curve.A.denominator, -1, q) % q
        for root in curve.K.roots_mod(q):
            R = curve.reduce_point(P, q, root)
            if R is None:
                continue
            if fp_mul(T, R, a, q) is not None:
                return False
    return True


def residues_at_p(curve: CurveNF, P, p):
    """Residues of P at every degree-one prime above p (one per root of g mod p)."""
    out = []
    for root in curve.K.roots_mod(p):
        R = curve.reduce_point(P, p, root)
        out.append(R)
    return out


def trace_relation_holds(curve: CurveNF, residues, p, T):
    """sum of residues is a torsion point mod p: [T] * sum = O. For rank-0 E/Q this must hold
    for every K-point (the sum is Tr_{K/Q}(P) mod p)."""
    a = curve.A.numerator * pow(curve.A.denominator, -1, p) % p
    S = None
    for R in residues:
        if R is None:
            return None
        S = fp_add(S, R, a, p)
    return fp_mul(T, S, a, p) is None
