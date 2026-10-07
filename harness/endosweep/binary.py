"""Binary-field curves for the endomorphism sweep: the NIST K- and B-curves.

The prime-field pipeline (``corpus.py``, ``curvesweep.py``) skips the ten
NIST curves over F_{2^m}.  This module covers them with the same discipline:
nothing is taken from the database that is not re-derived or checked.

* ``Field``: F_{2^m} in the polynomial basis of the curve's own reduction
  polynomial, with counters for multiplications and squarings.  An inversion
  is Itoh-Tsujii and is counted as the squarings and multiplications it
  performs (and as one inversion, for the record).
* ``BinaryCurve``: y^2 + xy = x^3 + a x^2 + b with a in {0, 1}; affine
  arithmetic as the reference, and Lopez-Dahab coordinates (x = X/Z,
  y = Y/Z^2) for the counted scalar multiplications: doubling 3M + 5S
  (4M + 5S unless b = 1), mixed addition 8M + 5S, Frobenius 3S.
* ``verify``: the group order from the constants alone -- n prime, h*n in the
  Hasse interval, n > 4 sqrt(q), a point killed by h*n and not by h -- and,
  on a Koblitz curve, independently from the Lucas sequence of its Frobenius.
* ``koblitz``: on a curve defined over F_2 (a, b in {0, 1}, b = 1) the
  Frobenius tau(x, y) = (x^2, y^2) is an endomorphism with
  tau^2 - mu tau + 2 = 0, mu = (-1)^(1-a): CM by Z[tau], D_K = -7.  It is
  verified on points, together with its eigenvalue on the order-n subgroup.
* counted scalar multiplication: the width-w NAF against Solinas' width-w
  tau-adic NAF of the partially reduced scalar, in which the m doublings
  become m Frobenius maps.  Every count is of the arithmetic actually
  executed, and every result is checked against an independent computation.

    python -m harness.endosweep.nist --std-curves STD_CURVES --out-dir OUT
"""
from __future__ import annotations

import random
from dataclasses import dataclass
from fractions import Fraction
from math import floor

# ---------------------------------------------------------------------------
# F_{2^m}
# ---------------------------------------------------------------------------

_SPREAD = []
for _i in range(256):
    _v = 0
    for _j in range(8):
        if _i >> _j & 1:
            _v |= 1 << (2 * _j)
    _SPREAD.append(_v)


def _spread(a: int) -> int:
    """The square of a in F_2[x]: bit i moves to bit 2i."""
    r = 0
    shift = 0
    while a:
        r |= _SPREAD[a & 255] << shift
        a >>= 8
        shift += 16
    return r


def _clmul(a: int, b: int) -> int:
    """Carry-less product in F_2[x], 4-bit windows of b."""
    if a == 0 or b == 0:
        return 0
    tab = [0, a] + [0] * 14
    for i in range(2, 16):
        tab[i] = tab[i >> 1] << 1 if i % 2 == 0 else tab[i - 1] ^ a
    r = 0
    for j in range((b.bit_length() + 3) // 4 - 1, -1, -1):
        r = (r << 4) ^ tab[(b >> (4 * j)) & 15]
    return r


class Field:
    """F_2[x]/(x^m + sum_{k in low} x^k), elements as Python ints (bit i = coefficient of x^i)."""

    def __init__(self, m: int, low: tuple[int, ...]):
        if 0 not in low or any(k >= m or k < 0 for k in low):
            raise ValueError("the reduction polynomial needs a constant term and lower terms below x^m")
        self.m = m
        self.low = tuple(sorted(set(low), reverse=True))
        self.mask = (1 << m) - 1
        self.reset()

    @property
    def q(self) -> int:
        return 1 << self.m

    def reset(self) -> None:
        self.M = self.S = self.I = 0

    def counts(self) -> dict:
        return {"M": self.M, "S": self.S, "I": self.I}

    def reduce(self, a: int) -> int:
        m = self.m
        while a >> m:
            hi = a >> m
            a &= self.mask
            for k in self.low:
                a ^= hi << k
        return a

    def mul(self, a: int, b: int) -> int:
        self.M += 1
        return self.reduce(_clmul(a, b))

    def sqr(self, a: int) -> int:
        self.S += 1
        return self.reduce(_spread(a))

    def inv(self, a: int) -> int:
        """Itoh-Tsujii: a^(2^m - 2) through beta_k = a^(2^k - 1), beta_(2k) = beta_k^(2^k) beta_k."""
        if a == 0:
            raise ZeroDivisionError("0 has no inverse")
        self.I += 1
        bits = bin(self.m - 1)[2:]
        b, k = a, 1
        for bit in bits[1:]:
            t = b
            for _ in range(k):
                t = self.sqr(t)
            b, k = self.mul(t, b), 2 * k
            if bit == "1":
                b, k = self.mul(self.sqr(b), a), k + 1
        return self.sqr(b)

    def trace(self, a: int) -> int:
        t, s = a, a
        for _ in range(self.m - 1):
            s = self.reduce(_spread(s))
            t ^= s
        return t

    def half_trace(self, c: int) -> int:
        """z with z^2 + z = c when m is odd and Tr(c) = 0."""
        if self.m % 2 == 0:
            raise ValueError("the half-trace needs odd m")
        z, s = c, c
        for _ in range((self.m - 1) // 2):
            s = self.reduce(_spread(self.reduce(_spread(s))))
            z ^= s
        return z

    def sqrt(self, a: int) -> int:
        for _ in range(self.m - 1):
            a = self.reduce(_spread(a))
        return a


# ---------------------------------------------------------------------------
# y^2 + xy = x^3 + a x^2 + b
# ---------------------------------------------------------------------------

INF = None   # the point at infinity, in every coordinate system


class BinaryCurve:
    def __init__(self, F: Field, a: int, b: int):
        if a not in (0, 1):
            raise ValueError("a must be 0 or 1 (every NIST binary curve has one of these)")
        if b == 0:
            raise ValueError("b = 0 is singular")
        self.F, self.a, self.b = F, a, b

    # --- affine reference -------------------------------------------------
    def on_curve(self, P) -> bool:
        if P is INF:
            return True
        F = self.F
        x, y = P
        lhs = F.sqr(y) ^ F.mul(x, y)
        x2 = F.sqr(x)
        rhs = F.mul(x2, x) ^ (x2 if self.a else 0) ^ self.b
        return lhs == rhs

    def neg(self, P):
        return INF if P is INF else (P[0], P[0] ^ P[1])

    def add(self, P, Q):
        F = self.F
        if P is INF:
            return Q
        if Q is INF:
            return P
        if P[0] == Q[0]:
            return self.dbl(P) if P[1] == Q[1] else INF
        lam = F.mul(P[1] ^ Q[1], F.inv(P[0] ^ Q[0]))
        x3 = F.sqr(lam) ^ lam ^ P[0] ^ Q[0] ^ self.a
        return (x3, F.mul(lam, P[0] ^ x3) ^ x3 ^ P[1])

    def dbl(self, P):
        F = self.F
        if P is INF or P[0] == 0:
            return INF
        lam = P[0] ^ F.mul(P[1], F.inv(P[0]))
        x3 = F.sqr(lam) ^ lam ^ self.a
        return (x3, F.sqr(P[0]) ^ F.mul(lam, x3) ^ x3)

    def mul_affine(self, k: int, P):
        """Left-to-right double-and-add in affine coordinates: the reference."""
        if k < 0:
            return self.mul_affine(-k, self.neg(P))
        R = INF
        for bit in bin(k)[2:]:
            R = self.dbl(R)
            if bit == "1":
                R = self.add(R, P)
        return R

    def lift_x(self, x: int):
        """A point with abscissa x, or None when x is not one."""
        F = self.F
        if x == 0:
            return (0, F.sqrt(self.b))
        x2 = F.sqr(x)
        c = x ^ self.a ^ F.mul(self.b, F.inv(x2))          # (x^3 + a x^2 + b) / x^2
        if F.trace(c):
            return None
        return (x, F.mul(x, F.half_trace(c)))

    def random_point(self, rng: random.Random):
        while True:
            P = self.lift_x(rng.getrandbits(self.F.m))
            if P is not None:
                return P

    def frobenius(self, P):
        return INF if P is INF else (self.F.sqr(P[0]), self.F.sqr(P[1]))

    # --- Lopez-Dahab, counted ---------------------------------------------
    def ld(self, P):
        return INF if P is INF else (P[0], P[1], 1)

    def ld_dbl(self, P):
        """2(X, Y, Z): Z3 = X^2 Z^2, X3 = X^4 + b Z^4, Y3 = b Z^4 Z3 + X3 (a Z3 + Y^2 + b Z^4)."""
        F = self.F
        if P is INF or P[0] == 0:
            return INF
        X, Y, Z = P
        X2, Z2 = F.sqr(X), F.sqr(Z)
        Z3 = F.mul(X2, Z2)
        Z4 = F.sqr(Z2)
        bZ4 = Z4 if self.b == 1 else F.mul(self.b, Z4)
        X3 = F.sqr(X2) ^ bZ4
        inner = (Z3 if self.a else 0) ^ F.sqr(Y) ^ bZ4
        return (X3, F.mul(bZ4, Z3) ^ F.mul(X3, inner), Z3)

    def ld_madd(self, P, Q):
        """(X1, Y1, Z1) + (x2, y2): 8M + 5S for a in {0, 1}."""
        F = self.F
        if P is INF:
            return self.ld(Q)
        if Q is INF:
            return P
        X1, Y1, Z1 = P
        x2, y2 = Q
        Z1s = F.sqr(Z1)
        A = F.mul(y2, Z1s) ^ Y1
        B = F.mul(x2, Z1) ^ X1
        if B == 0:
            return self.ld_dbl(self.ld(Q)) if A == 0 else INF
        C = F.mul(Z1, B)
        D = F.mul(F.sqr(B), C ^ (Z1s if self.a else 0))
        Z3 = F.sqr(C)
        E = F.mul(A, C)
        X3 = F.sqr(A) ^ D ^ E
        Fv = X3 ^ F.mul(x2, Z3)
        G = F.mul(x2 ^ y2, F.sqr(Z3))
        return (X3, F.mul(E ^ Z3, Fv) ^ G, Z3)

    def ld_frobenius(self, P):
        return INF if P is INF else (self.F.sqr(P[0]), self.F.sqr(P[1]), self.F.sqr(P[2]))

    def ld_to_affine(self, P):
        if P is INF:
            return INF
        F = self.F
        zi = F.inv(P[2])
        return (F.mul(P[0], zi), F.mul(P[1], F.sqr(zi)))

    def batch_to_affine(self, Ps: list):
        """Montgomery's simultaneous inversion: 3(k-1) M + 1 I, then 2M + 1S per point."""
        F = self.F
        pts = [P for P in Ps if P is not INF]
        if not pts:
            return list(Ps)
        prods = [pts[0][2]]
        for P in pts[1:]:
            prods.append(F.mul(prods[-1], P[2]))
        inv = F.inv(prods[-1])
        zinv = [0] * len(pts)
        for i in range(len(pts) - 1, 0, -1):
            zinv[i] = F.mul(inv, prods[i - 1])
            inv = F.mul(inv, pts[i][2])
        zinv[0] = inv
        out = iter([(F.mul(P[0], zi), F.mul(P[1], F.sqr(zi))) for P, zi in zip(pts, zinv)])
        return [INF if P is INF else next(out) for P in Ps]

    def mul_ld(self, k: int, P):
        """Uncounted-intent binary double-and-add in Lopez-Dahab (verification only)."""
        if k < 0:
            return self.mul_ld(-k, self.neg(P))
        R = INF
        for bit in bin(k)[2:]:
            R = self.ld_dbl(R)
            if bit == "1":
                R = self.ld_madd(R, P)
        return self.ld_to_affine(R)


# ---------------------------------------------------------------------------
# verification
# ---------------------------------------------------------------------------

@dataclass
class Verification:
    ok: bool
    note: str
    trace: int | None = None


def verify(E: BinaryCurve, n: int, h: int, G=None, seed: int = 20261006) -> Verification:
    """#E = h n from the constants alone (and G of order n, when given)."""
    from sympy import isprime
    F = E.F
    q = F.q
    try:
        if not isprime(n):
            raise ValueError("n is not prime")
        N = h * n
        if (q + 1 - N) ** 2 > 4 * q:
            raise ValueError("h*n is outside the Hasse interval")
        if n * n <= 16 * q:
            raise ValueError("n <= 4 sqrt(q): one point cannot pin the order")
        rng = random.Random(seed)
        for _ in range(64):
            P = E.random_point(rng)
            if not E.on_curve(P):
                raise ValueError("lift_x produced a point off the curve")
            hP = E.mul_ld(h, P)
            if hP is INF:
                continue
            if E.mul_ld(n, hP) is not INF:
                raise ValueError("a point is not killed by h*n")
            break
        else:
            raise ValueError("no point with h*P != O in 64 tries")
        if G is not None:
            if not E.on_curve(G):
                raise ValueError("the generator is not on the curve")
            if E.mul_ld(n, G) is not INF:
                raise ValueError("the generator is not killed by n")
        t = q + 1 - N
        return Verification(True, "n prime, n > 4 sqrt(q), a point P with h*P != O is killed by h*n, so #E = h*n"
                            + ("; the generator is on the curve and has order n" if G is not None else ""), t)
    except ValueError as e:
        return Verification(False, f"VERIFICATION FAILED: {e}")


# ---------------------------------------------------------------------------
# Koblitz curves: Z[tau]
# ---------------------------------------------------------------------------

def is_koblitz(E: BinaryCurve) -> bool:
    return E.b == 1


def lucas_trace(mu: int, m: int) -> int:
    """V_m = tau^m + conj(tau)^m: V_0 = 2, V_1 = mu, V_(k+1) = mu V_k - 2 V_(k-1)."""
    v0, v1 = 2, mu
    for _ in range(m - 1):
        v0, v1 = v1, mu * v1 - 2 * v0
    return v1 if m >= 1 else v0


class Ztau:
    """Arithmetic in Z[tau], tau^2 = mu tau - 2; elements are pairs (a, b) = a + b tau."""

    def __init__(self, mu: int):
        if mu not in (1, -1):
            raise ValueError("mu must be +-1")
        self.mu = mu

    def mul(self, x, y):
        a, b = x
        c, d = y
        return (a * c - 2 * b * d, a * d + b * c + self.mu * b * d)

    def conj(self, x):
        a, b = x
        return (a + self.mu * b, -b)

    def norm(self, x):
        a, b = x
        return a * a + self.mu * a * b + 2 * b * b

    def power(self, x, e):
        r = (1, 0)
        for bit in bin(e)[2:]:
            r = self.mul(r, r)
            if bit == "1":
                r = self.mul(r, x)
        return r

    def _qnorm(self, x0: Fraction, x1: Fraction) -> Fraction:
        return x0 * x0 + self.mu * x0 * x1 + 2 * x1 * x1

    def round(self, l0: Fraction, l1: Fraction):
        """The element of Z[tau] nearest to l0 + l1 tau in the norm (searched among the 9 points around it)."""
        f0, f1 = floor(l0 + Fraction(1, 2)), floor(l1 + Fraction(1, 2))
        best = None
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                c = (f0 + i, f1 + j)
                d = self._qnorm(l0 - c[0], l1 - c[1])
                if best is None or d < best[0]:
                    best = (d, c)
        return best[1]

    def reduce_mod(self, x, delta):
        """x - round(x / delta) * delta: a small representative of x modulo delta."""
        num = self.mul(x, self.conj(delta))
        N = self.norm(delta)
        k = self.round(Fraction(num[0], N), Fraction(num[1], N))
        kd = self.mul(k, delta)
        return (x[0] - kd[0], x[1] - kd[1])


@dataclass
class Koblitz:
    """Everything the tau-adic method needs on one Koblitz curve."""
    m: int
    mu: int
    n: int
    h: int
    delta: tuple[int, int]        # (tau^m - 1) / (tau - 1)
    lam: int                      # tau acts as [lam] on the order-n subgroup

    @property
    def Z(self) -> Ztau:
        return Ztau(self.mu)


def koblitz(E: BinaryCurve, n: int, h: int, G) -> tuple[Koblitz, dict]:
    """Derive tau's data and verify it on points: tau^2 - mu tau + 2 = 0, #E from V_m, tau(G) = [lam] G."""
    from sympy.ntheory import sqrt_mod
    F = E.F
    mu = 1 if E.a == 1 else -1
    m = F.m
    Z = Ztau(mu)
    checks = {}
    # the group order from the characteristic polynomial of Frobenius alone
    order = F.q + 1 - lucas_trace(mu, m)
    checks["order_from_lucas_sequence"] = order == h * n
    checks["h_equals_E(F_2)"] = h == 2 + 1 - mu
    # tau^2 + 2 = mu tau on random points (any point, cofactor part included)
    rng = random.Random(7)
    ok = True
    for _ in range(4):
        P = E.random_point(rng)
        tP = E.frobenius(P)
        lhs = E.add(E.frobenius(tP), E.dbl(P))
        rhs = tP if mu == 1 else E.neg(tP)
        ok &= lhs == rhs
    checks["tau^2-mu*tau+2=0_on_points"] = ok
    # eigenvalue on <G>: a root of lam^2 - mu lam + 2 (mod n), i.e. (mu + s)/2 with s^2 = -7
    roots = sqrt_mod((-7) % n, n, all_roots=True) or []
    inv2 = pow(2, -1, n)
    lams = sorted({(mu + int(s)) * inv2 % n for s in roots})
    tG = E.frobenius(G)
    lam = next((L for L in lams if E.mul_ld(L, G) == tG), None)
    checks["tau(G)=[lambda]G"] = lam is not None
    tm = Z.power((0, 1), m)
    delta_num = Z.mul((tm[0] - 1, tm[1]), Z.conj((-1, 1)))      # (tau^m - 1) * conj(tau - 1)
    Nt1 = Z.norm((-1, 1))
    if delta_num[0] % Nt1 or delta_num[1] % Nt1:
        raise ArithmeticError("tau - 1 does not divide tau^m - 1")
    delta = (delta_num[0] // Nt1, delta_num[1] // Nt1)
    checks["N(delta)=n"] = Z.norm(delta) == n
    kob = Koblitz(m, mu, n, h, delta, lam if lam is not None else 0)
    return kob, checks


def tnaf_constants(kob: Koblitz, w: int):
    """t_w (tau = t_w mod tau^w) and alpha_u = u mods tau^w for odd 0 < u < 2^(w-1)."""
    Z = kob.Z
    U0, U1 = 0, 1
    for _ in range(w - 1):
        U0, U1 = U1, kob.mu * U1 - 2 * U0
    # U1 = U_w, U0 = U_(w-1)
    tw = 2 * U0 * pow(U1, -1, 1 << w) % (1 << w)
    tauw = Z.power((0, 1), w)
    alpha = {u: Z.reduce_mod((u, 0), tauw) for u in range(1, 1 << (w - 1), 2)}
    return tw, alpha


def tnaf(rho, kob: Koblitz, w: int, tw: int, alpha: dict) -> list:
    """Width-w tau-adic NAF of rho (Solinas): digits 0 or (sign, u), least significant first."""
    r0, r1 = rho
    mu = kob.mu
    mod = 1 << w
    out = []
    while r0 or r1:
        if r0 & 1:
            u = (r0 + r1 * tw) % mod
            if u >= mod // 2:
                u -= mod
            sign = 1 if u > 0 else -1
            u = abs(u)
            b, g = alpha[u]
            r0, r1 = r0 - sign * b, r1 - sign * g
            out.append((sign, u))
        else:
            out.append(0)
        t = r0
        r0, r1 = r1 + mu * (r0 // 2), -(t // 2)
    return out


def wnaf(k: int, w: int) -> list[int]:
    out = []
    mod = 1 << w
    while k:
        if k & 1:
            u = k % mod
            if u >= mod // 2:
                u -= mod
            k -= u
        else:
            u = 0
        out.append(u)
        k >>= 1
    return out


# ---------------------------------------------------------------------------
# counted scalar multiplications
# ---------------------------------------------------------------------------

def _phase(F: Field, before: dict) -> dict:
    return {k: F.counts()[k] - before[k] for k in before}


def mul_wnaf_counted(E: BinaryCurve, k: int, P, w: int):
    """Width-w NAF, odd multiples in affine (one batched conversion), Lopez-Dahab accumulator."""
    F = E.F
    F.reset()
    table = {1: P}
    if w > 2:
        # jP = 2(j/2 P) or (j-1)P + P in Lopez-Dahab: no inversion before the one batched conversion
        mult = {1: E.ld(P)}
        for j in range(2, 1 << (w - 1)):
            mult[j] = E.ld_dbl(mult[j // 2]) if j % 2 == 0 else E.ld_madd(mult[j - 1], P)
        us = list(range(3, 1 << (w - 1), 2))
        lds = [mult[u] for u in us]
        for u, A in zip(us, E.batch_to_affine(lds)):
            table[u] = A
    pre = F.counts()
    Q = INF
    for d in reversed(wnaf(k, w)):
        if Q is not INF:
            Q = E.ld_dbl(Q)
        if d:
            T = table[d] if d > 0 else E.neg(table[-d])
            Q = E.ld_madd(Q, T)
    main = _phase(F, pre)
    before = F.counts()
    R = E.ld_to_affine(Q)
    return R, {"precompute": pre, "main": main, "final": _phase(F, before), "total": F.counts()}


def mul_tnaf_counted(E: BinaryCurve, kob: Koblitz, k: int, P, w: int, consts=None):
    """Width-w TNAF of k partmod delta; alpha_u P in affine (one batched conversion); Frobenius accumulator."""
    F = E.F
    tw, alpha = consts or tnaf_constants(kob, w)
    F.reset()
    table = {1: P}
    us = [u for u in alpha if u != 1]
    if us:
        lds = []
        for u in us:
            Q = INF
            for d in reversed(tnaf(alpha[u], kob, 2, 2, {1: (1, 0)})):
                if Q is not INF:
                    Q = E.ld_frobenius(Q)
                if d:
                    Q = E.ld_madd(Q, P if d[0] > 0 else E.neg(P))
            lds.append(Q)
        for u, A in zip(us, E.batch_to_affine(lds)):
            table[u] = A
    pre = F.counts()
    rho = kob.Z.reduce_mod((k, 0), kob.delta)
    Q = INF
    for d in reversed(tnaf(rho, kob, w, tw, alpha)):
        if Q is not INF:
            Q = E.ld_frobenius(Q)
        if d:
            T = table[d[1]] if d[0] > 0 else E.neg(table[d[1]])
            Q = E.ld_madd(Q, T)
    main = _phase(F, pre)
    before = F.counts()
    R = E.ld_to_affine(Q)
    return R, {"precompute": pre, "main": main, "final": _phase(F, before), "total": F.counts(),
               "rho": [int(rho[0]), int(rho[1])]}


def scalar_counts(E: BinaryCurve, G, n: int, *, kob: Koblitz | None, widths=(2, 3, 4, 5, 6, 7), scalars: int = 32,
                  references: int = 2, seed: int = 20261006) -> dict:
    """Mean counted M and S of k*G over random k for every width, for wNAF and (on a Koblitz curve) TNAF.

    Every result is compared with the other algorithms' results for the same
    scalar, and the first ``references`` scalars also with the affine
    double-and-add reference.
    """
    rng = random.Random(seed)
    ks = [rng.randrange(1, n) for _ in range(scalars)]
    algos = [("wnaf", w) for w in widths] + ([("tnaf", w) for w in widths] if kob else [])
    consts = {w: tnaf_constants(kob, w) for w in widths} if kob else {}
    sums: dict = {a: {"M": 0, "S": 0, "I": 0, "precompute_M": 0, "precompute_S": 0, "M2": 0} for a in algos}
    agree = True
    ref_ok = True
    for i, k in enumerate(ks):
        results = set()
        for a in algos:
            if a[0] == "wnaf":
                R, c = mul_wnaf_counted(E, k, G, a[1])
            else:
                R, c = mul_tnaf_counted(E, kob, k, G, a[1], consts[a[1]])
            results.add(R)
            s = sums[a]
            for key in ("M", "S", "I"):
                s[key] += c["total"][key]
            s["precompute_M"] += c["precompute"]["M"]
            s["precompute_S"] += c["precompute"]["S"]
            s["M2"] += c["total"]["M"] ** 2
        agree &= len(results) == 1
        if i < references:
            ref_ok &= results == {E.mul_affine(k, G)}
    out = {}
    for a, s in sums.items():
        mean = {key: s[key] / scalars for key in ("M", "S", "I", "precompute_M", "precompute_S")}
        mean["M_sd"] = round(max(0.0, s["M2"] / scalars - mean["M"] ** 2) ** 0.5, 2)
        out[f"{a[0]}/w{a[1]}"] = {k2: round(v, 2) if isinstance(v, float) else v for k2, v in mean.items()}
    return {"scalars": scalars, "references_checked": min(references, scalars), "all_algorithms_agree": agree,
            "reference_agrees": ref_ok, "configs": out}


def best(configs: dict, prefix: str, s_weight: float) -> tuple[str, float]:
    """The configuration with the fewest M + s_weight * S among those starting with prefix."""
    cands = [(v["M"] + s_weight * v["S"], k) for k, v in configs.items() if k.startswith(prefix)]
    cost, k = min(cands)
    return k, round(cost, 1)


def field_from_entry(entry: dict) -> Field:
    """The std-curves 'field' block of a binary curve."""
    powers = sorted(int(t["power"]) for t in entry["poly"])
    m = powers[-1]
    if m != int(entry["bits"]):
        raise ValueError("the reduction polynomial's degree is not the field size")
    return Field(m, tuple(powers[:-1]))


