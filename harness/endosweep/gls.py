"""Binary GLS curves with lambda coordinates: the "GLS-lambda" setting, built, verified and counted.

Oliveira, Lopez, Aranha and Rodriguez-Henriquez (CHES 2013, Section 3.2)
work on E~ : y^2 + xy = x^3 + a' x^2 + b over F_{q^2}, q = 2^m, m = 127, with
F_q = F_2[x]/(x^127 + x^63 + 1), F_{q^2} = F_q[u]/(u^2 + u + 1), a' = u
(trace 1 over F_{q^2}) and b in F_q.  E~ is the quadratic twist over F_{q^2}
of E : y^2 + xy = x^3 + a x^2 + b over F_q, so #E~(F_{q^2}) = (q - 1)^2 + t^2
with t the trace of E over F_q, and psi = phi o pi o phi^{-1} is

    psi(x, y) = (x^q, y^q + u x^q),     in lambda-affine (x^q, lambda^q + u),

a conjugation and two additions in F_q.  The paper does not print its b;
this module finds its own.

* ``Fq2``: F_{q^2} on top of a counted F_q (elements packed x0 + x1 * 2^m so
  that addition is still XOR), Karatsuba multiplication 3M, squaring 2S,
  inversion 1I + 3M + 1S, multiplication by u free, by an F_q constant 2M;
  counts at both levels.
* ``agm_trace``: the trace of y^2 + xy = x^3 + c over F_{2^m} by Mestre's AGM
  in the unramified extension Z_q (Kronecker-packed polynomial arithmetic mod
  2^W, Newton square roots, the norm as a determinant).  It is a black box
  as far as this module is concerned: it is validated against brute-force
  point counts on toy fields, and every order it produces is then *proven* by
  ``binary.verify`` (r prime, r > 4q, a point killed by 2r and not by 2).
* ``gls_instance``: the first b (from a seeded stream) for which
  (q - 1)^2 + t^2 = 2 r with r prime; the twist formula is checked by brute
  force on toy fields; psi^2 = -1 and psi(P + Q) = psi(P) + psi(Q) on random
  points, psi(G) = [delta] G with delta^2 = -1 (mod r), delta t = +-(q - 1),
  and the 2-GLV lattice from ``lattice.py``.
* ``scalar_counts``: counted 1-D wNAF and 2-GLV interleaved wNAF, lambda
  (with and without Theorem 3's doubling-and-addition) and Lopez-Dahab, on
  the same scalars, every result cross-checked and the first two against the
  affine reference.

    python -m harness.endosweep.gls --m 127 --out-dir OUT
"""
from __future__ import annotations

import argparse
import json
import math
import os
import random
import time

from . import binary as BI
from . import lattice as LA
from . import lambdacoord as LC
from .binary import INF

# ---------------------------------------------------------------------------
# F_{q^2} = F_q[u]/(u^2 + u + 1), m odd
# ---------------------------------------------------------------------------


class Fq2:
    """F_{q^2} over a CountedField F_q (m odd, so u^2 + u + 1 is irreducible over F_q)."""

    def __init__(self, F: LC.CountedField):
        if F.m % 2 == 0:
            raise ValueError("u^2 + u + 1 is irreducible over F_{2^m} only for odd m")
        self.F = F
        self.m = F.m
        self.mask = F.mask
        self.u = 1 << F.m
        self.reset()

    @property
    def q(self) -> int:
        return 1 << (2 * self.m)

    @property
    def bits(self) -> int:
        return 2 * self.m

    def split(self, a: int):
        return a & self.mask, a >> self.m

    def join(self, a0: int, a1: int) -> int:
        return a0 | (a1 << self.m)

    def reset(self) -> None:
        self.M = self.S = self.I = self.Mc = self.Mc_base = 0
        self.F.reset()

    def counts(self) -> dict:
        F = self.F
        return {"M": self.M, "S": self.S, "I": self.I, "Mc": self.Mc, "Mc_base": self.Mc_base,
                "base_M": F.M + F.Mc, "base_S": F.S, "base_I": F.I}

    # --- counted -------------------------------------------------------------
    def mul(self, a: int, b: int) -> int:
        """Karatsuba: (a0 + a1 u)(b0 + b1 u) = (t0 + t1) + (t2 + t0) u, t2 = (a0 + a1)(b0 + b1); 3M."""
        self.M += 1
        F = self.F
        a0, a1 = self.split(a)
        b0, b1 = self.split(b)
        t0, t1, t2 = F.mul(a0, b0), F.mul(a1, b1), F.mul(a0 ^ a1, b0 ^ b1)
        return self.join(t0 ^ t1, t2 ^ t0)

    def sqr(self, a: int) -> int:
        """(a0 + a1 u)^2 = (a0^2 + a1^2) + a1^2 u: 2S."""
        self.S += 1
        a0, a1 = self.split(a)
        s1 = self.F.sqr(a1)
        return self.join(self.F.sqr(a0) ^ s1, s1)

    def inv(self, a: int) -> int:
        """t = a0 (a0 + a1) + a1^2, (a0 + a1 u)^-1 = ((a0 + a1) + a1 u) / t: 1I + 3M + 1S."""
        if a == 0:
            raise ZeroDivisionError("0 has no inverse")
        self.I += 1
        F = self.F
        a0, a1 = self.split(a)
        ti = F.inv(F.mul(a0, a0 ^ a1) ^ F.sqr(a1))
        return self.join(F.mul(a0 ^ a1, ti), F.mul(a1, ti))

    def mul_u(self, a: int) -> int:
        """u (a0 + a1 u) = a1 + (a0 + a1) u: additions only."""
        a0, a1 = self.split(a)
        return self.join(a1, a0 ^ a1)

    def const_base_cost(self, c: int) -> int:
        """F_q multiplications a multiplication by the constant c = c0 + c1 u costs (c = -1: a general one)."""
        if c == -1:
            return 3
        c0, c1 = self.split(c)
        return (0 if c0 in (0, 1) else 2) + (0 if c1 in (0, 1) else 2)

    def const_cost(self, c: int) -> float:
        return self.const_base_cost(c) / 3

    def mul_const(self, c: int, z: int) -> int:
        """z * c for a curve constant: c0 z + c1 (u z), each 0, free (c_i = 1) or 2 F_q multiplications."""
        self.Mc += 1
        F = self.F
        c0, c1 = self.split(c)
        out = 0
        for ci, v in ((c0, z), (c1, self.mul_u(z) if c1 else 0)):
            if ci == 0:
                continue
            if ci == 1:
                out ^= v
            else:
                self.Mc_base += 2
                v0, v1 = self.split(v)
                out ^= self.join(F.mul(ci, v0), F.mul(ci, v1))
        return out

    # --- uncounted ---------------------------------------------------------
    def conj(self, a: int) -> int:
        """The q-power Frobenius sigma: u^q = u^2 = u + 1 for odd m, so (a0 + a1) + a1 u."""
        a0, a1 = self.split(a)
        return self.join(a0 ^ a1, a1)

    def mul_raw(self, a: int, b: int) -> int:
        F = self.F
        a0, a1 = self.split(a)
        b0, b1 = self.split(b)
        t0, t1, t2 = F.mul_raw(a0, b0), F.mul_raw(a1, b1), F.mul_raw(a0 ^ a1, b0 ^ b1)
        return self.join(t0 ^ t1, t2 ^ t0)

    def sqr_raw(self, a: int) -> int:
        a0, a1 = self.split(a)
        s1 = self.F.sqr_raw(a1)
        return self.join(self.F.sqr_raw(a0) ^ s1, s1)

    def trace(self, a: int) -> int:
        """Tr_{F_q^2 / F_2}(a) = Tr_{F_q / F_2}(a + a^q) = Tr_q(a1)."""
        return self.F.trace(self.split(a)[1])

    def solve_quadratic(self, c: int):
        """z with z^2 + z = c: z1^2 + z1 = c1, then z0^2 + z0 = c0 + z1^2 (z1 -> z1 + 1 flips Tr_q, m odd)."""
        F = self.F
        c0, c1 = self.split(c)
        if F.trace(c1):
            return None
        z1 = F.half_trace(c1)
        r = c0 ^ F.sqr_raw(z1)
        if F.trace(r):
            z1 ^= 1
            r ^= 1
        return self.join(F.half_trace(r), z1)

    def sqrt(self, a: int) -> int:
        a0, a1 = self.split(a)
        return self.join(self.F.sqrt(a0 ^ a1), self.F.sqrt(a1))

    def random(self, rng: random.Random) -> int:
        return rng.getrandbits(2 * self.m)


# ---------------------------------------------------------------------------
# Z_q = W(F_{2^m}) mod 2^W and Mestre's AGM
# ---------------------------------------------------------------------------


class Zq:
    """Z_2[X]/(X^d + sum_{k in low} X^k) modulo 2^W; elements are lists of d ints in [0, 2^W)."""

    def __init__(self, d: int, low: tuple[int, ...], W: int):
        self.d, self.low, self.W = d, tuple(low), W
        self.mask = (1 << W) - 1
        self.slot = 2 * W + d.bit_length() + 2

    def one(self) -> list:
        return [1] + [0] * (self.d - 1)

    def from_f2(self, c: int) -> list:
        return [(c >> i) & 1 for i in range(self.d)]

    def add(self, a, b):
        return [(x + y) & self.mask for x, y in zip(a, b)]

    def sub(self, a, b):
        return [(x - y) & self.mask for x, y in zip(a, b)]

    def scal(self, k: int, a):
        return [(k * x) & self.mask for x in a]

    def half(self, a):
        if any(x & 1 for x in a):
            raise ArithmeticError("not divisible by 2")
        return [x >> 1 for x in a]

    def _pack(self, a) -> int:
        r = 0
        for x in reversed(a):
            r = (r << self.slot) | x
        return r

    def mul(self, a, b):
        d, slot = self.d, self.slot
        C = self._pack(a) * self._pack(b)
        smask = (1 << slot) - 1
        c = [(C >> (slot * i)) & smask for i in range(2 * d - 1)]
        for i in range(2 * d - 2, d - 1, -1):
            v = c[i]
            if v:
                for k in self.low:
                    c[i - d + k] -= v
        return [x & self.mask for x in c[:d]]

    def inv(self, a):
        """Newton, y <- y (2 - a y), from y = 1: a must be 1 mod 2."""
        if a[0] & 1 == 0 or any(x & 1 for x in a[1:]):
            raise ArithmeticError("Newton inversion here needs a = 1 (mod 2)")
        y = self.one()
        two = [2] + [0] * (self.d - 1)
        for _ in range(self.W.bit_length() + 1):
            y = self.mul(y, self.sub(two, self.mul(a, y)))
        return y

    def sqrt(self, z):
        """The square root = 1 (mod 4) of z = 1 (mod 8), by Newton on the inverse root (one bit lost per step)."""
        y = self.one()
        three = [3] + [0] * (self.d - 1)
        for _ in range(self.W.bit_length() + 2):
            y = self.mul(y, self.half(self.sub(three, self.mul(z, self.mul(y, y)))))
        return self.mul(z, y)

    def norm(self, a, N: int) -> int:
        """N_{Q_q/Q_2}(a) mod 2^N: the determinant of multiplication by a (a = 1 mod 2, so every pivot is a unit)."""
        d, mod = self.d, 1 << N
        rows = []
        v = [x % mod for x in a]
        for _ in range(d):
            rows.append(v)
            top = v[-1]
            v = [0] + v[:-1]
            for k in self.low:
                v[k] = (v[k] - top) % mod
        det = 1
        for col in range(d):
            piv = rows[col][col]
            if piv % 2 == 0:
                raise ArithmeticError("a pivot is not a unit")
            det = det * piv % mod
            inv = pow(piv, -1, mod)
            prow = rows[col]
            for r in range(col + 1, d):
                f = rows[r][col] * inv % mod
                if f:
                    row = rows[r]
                    rows[r] = [(x - f * y) % mod for x, y in zip(row, prow)]
        return det


def agm_trace(m: int, low: tuple[int, ...], c: int, extra: int = 8) -> int:
    """The trace t = q + 1 - #E of E : y^2 + xy = x^3 + c over F_2[x]/(x^m + sum x^low), by Mestre's AGM.

    (a, b) <- ((a + b)/2, sqrt(a b)) from (1 + 8 gamma, 1), gamma a lift of c,
    converges to the canonical-lift cycle; then t = N(a / a') (mod 2^N),
    a' the next AGM value, N = ceil(m/2) + 2.  Needs c not in F_4.
    """
    if c in (0, 1):
        raise ValueError("c must not lie in F_4 (j in F_4)")
    N = (m + 1) // 2 + 2
    K = N + extra
    W = N + K + 32
    Z = Zq(m, low, W)
    a = Z.add(Z.one(), Z.scal(8, Z.from_f2(c)))
    b = Z.one()
    for _ in range(K):
        a, b = Z.half(Z.add(a, b)), Z.sqrt(Z.mul(a, b))
    a1 = Z.half(Z.add(a, b))
    t = Z.norm(Z.mul(a, Z.inv(a1)), N)
    if t >= 1 << (N - 1):
        t -= 1 << N
    if t * t > 4 * (1 << m):
        raise ArithmeticError("AGM result outside the Hasse interval")
    return t


def brute_trace(F, a: int, b: int) -> int:
    """q + 1 - #E for y^2 + xy = x^3 + a x^2 + b over a small field F (CountedField or Fq2), by counting x."""
    q = F.q
    count = 2                                  # O and (0, sqrt b)
    for x in range(1, q):
        xi = F.inv(x)
        c = x ^ a ^ F.mul(b, F.sqr(xi))
        if F.trace(c) == 0:
            count += 2
    return q + 1 - count


def is_irreducible(m: int, low: tuple[int, ...]) -> bool:
    """x^m + sum x^low over F_2, for prime m: x^(2^m) = x mod f and no root."""
    from sympy import isprime
    if not isprime(m):
        raise ValueError("this test is for prime degree")
    F = LC.CountedField(m, low)
    s = 2                                       # the element x
    for _ in range(m):
        s = F.sqr_raw(s)
    return s == 2 and 0 in low and len(low) % 2 == 0     # an odd number of terms: f(1) = 1, and f(0) = 1


# ---------------------------------------------------------------------------
# the GLS curve and psi
# ---------------------------------------------------------------------------

FIELDS = {7: (1, 0), 11: (2, 0), 13: (4, 3, 1, 0), 17: (3, 0), 31: (3, 0), 61: (5, 2, 1, 0), 127: (63, 0)}


def psi_affine(K: Fq2, P):
    """psi(x, y) = (x^q, y^q + u x^q)."""
    if P is INF:
        return INF
    x = K.conj(P[0])
    return (x, K.conj(P[1]) ^ K.mul_u(x))


def psi_lambda_affine(K: Fq2, P):
    """In lambda-affine: (x^q, lambda^q + u)."""
    return INF if P is INF else (K.conj(P[0]), K.conj(P[1]) ^ K.u)


def psi_lambda(K: Fq2, P):
    """In lambda-projective: (X^q, L^q + u Z^q, Z^q)."""
    if P is INF:
        return INF
    Z = K.conj(P[2])
    return (K.conj(P[0]), K.conj(P[1]) ^ K.mul_u(Z), Z)


def find_gls(m: int, low: tuple[int, ...], seed: int = 20261008, max_tries: int = 2000, trace_fn=None) -> dict:
    """The first b in F_q from a seeded stream with (q - 1)^2 + t^2 = 2 r, r prime (t by AGM unless given)."""
    from sympy import isprime
    rng = random.Random(seed)
    q = 1 << m
    tries = []
    for i in range(max_tries):
        b = rng.getrandbits(m)
        if b in (0, 1):
            continue
        t = trace_fn(b) if trace_fn else agm_trace(m, low, b)
        N2 = (q - 1) ** 2 + t * t
        ok = N2 % 2 == 0 and isprime(N2 // 2)
        tries.append(b)
        if ok:
            return {"b": b, "t": t, "r": N2 // 2, "h": 2, "candidates_tried": len(tries)}
    raise RuntimeError("no prime-order GLS curve found")


def build(m: int, low: tuple[int, ...], b: int, t: int, r: int, seed: int = 1) -> dict:
    """Construct E~ over F_{q^2}, prove #E~ = 2r, find psi's eigenvalue, check psi on points, reduce the lattice."""
    from sympy.ntheory import sqrt_mod
    F = LC.CountedField(m, low)
    K = Fq2(F)
    q = 1 << m
    checks = {}
    # E over F_q: the AGM trace kills points (q + 1 - t) and the twist's (q + 1 + t)
    Eq = LC.GeneralCurve(F, 0, b)
    rng = random.Random(seed)
    ok = True
    for _ in range(3):
        P = Eq.random_point(rng)
        ok &= Eq.mul_ld(q + 1 - t, P) is INF
    Eq1 = LC.GeneralCurve(F, 1, b)
    for _ in range(3):
        ok &= Eq1.mul_ld(q + 1 + t, Eq1.random_point(rng)) is INF
    checks["E(F_q)_order_q+1-t_and_twist_q+1+t_kill_points"] = ok
    E = LC.GeneralCurve(K, K.u, b)
    checks["trace_of_a'=u_is_1"] = K.trace(K.u) == 1
    G = None
    while G is None or G is INF:
        G = E.dbl(E.random_point(rng))
    v = BI.verify(E, r, 2, G, seed=seed)
    checks["order_2r_proven"] = v.ok
    checks["order_equals_(q-1)^2+t^2"] = 2 * r == (q - 1) ** 2 + t * t
    # psi
    ok_sq = ok_hom = ok_lam = True
    for _ in range(4):
        P, Q = E.random_point(rng), E.random_point(rng)
        ok_sq &= psi_affine(K, psi_affine(K, P)) == E.neg(P)
        ok_hom &= psi_affine(K, E.add(P, Q)) == E.add(psi_affine(K, P), psi_affine(K, Q))
        C = LC.LambdaCurve(K, K.u, b)
        Pl = C.to_lambda_affine(P)
        ok_lam &= C.from_lambda_affine(psi_lambda_affine(K, Pl)) == psi_affine(K, P)
        ok_lam &= C.to_affine(psi_lambda(K, LC._rand_proj(K, rng, Pl))) == psi_affine(K, P)
    checks["psi^2=-1_on_points"] = ok_sq
    checks["psi_is_additive"] = ok_hom
    checks["psi_lambda_forms_agree_with_affine"] = ok_lam
    roots = sorted(int(s) for s in (sqrt_mod(r - 1, r, all_roots=True) or []))
    psiG = psi_affine(K, G)
    delta = next((d for d in roots if E.mul_ld(d, G) == psiG), None)
    checks["psi(G)=[delta]G,delta^2=-1"] = delta is not None
    sign = None
    if delta is not None:
        sign = 1 if delta * t % r == (q - 1) % r else (-1 if delta * t % r == (1 - q) % r else 0)
    checks["delta*t=+-(q-1)_mod_r"] = sign in (1, -1)
    red = LA.reduce([1, delta or 1], r)
    bits = LA.coefficient_bits(red, samples=256, seed=seed)
    return {"m": m, "low": list(low), "q_bits": m, "b": hex(b), "t": t, "r": r, "log2_r": round(math.log2(r), 3),
            "G": [hex(G[0]), hex(G[1])], "delta": delta, "delta_t_sign": sign, "checks": checks,
            "verification": v.note, "lattice_basis": red.basis, "coefficient_bits": bits,
            "_objects": (F, K, E, G, red)}


# ---------------------------------------------------------------------------
# counted scalar multiplication on the GLS curve
# ---------------------------------------------------------------------------


class LambdaArith:
    name = "lambda"

    def __init__(self, K: Fq2, C: LC.LambdaCurve):
        self.K, self.C = K, C
        self.convert = C.to_lambda_affine
        self.lift, self.dbl, self.madd, self.dbl_add = C.lift, C.dbl, C.madd, C.dbl_add
        self.batch, self.neg_aff, self.to_affine = C.batch_to_lambda_affine, C.neg_aff, C.to_affine

    def psi_aff(self, T):
        return psi_lambda_affine(self.K, T)

    def reset(self):
        self.C.reset()


class LDArith:
    name = "ld"

    def __init__(self, K: Fq2, E: LC.GeneralCurve):
        self.K, self.E = K, E
        self.lift, self.dbl, self.madd, self.dbl_add = E.ld, E.ld_dbl, E.ld_madd, None
        self.batch, self.neg_aff, self.to_affine = E.batch_to_affine, E.neg, E.ld_to_affine

    @staticmethod
    def convert(P):
        return P

    def psi_aff(self, T):
        return psi_affine(self.K, T)

    def reset(self):
        self.K.reset()


def _table(ar, Pa, w: int) -> dict:
    table = {1: Pa}
    if w > 2:
        mult = {1: ar.lift(Pa)}
        for j in range(2, 1 << (w - 1)):
            mult[j] = ar.dbl(mult[j // 2]) if j % 2 == 0 else ar.madd(mult[j - 1], Pa)
        us = list(range(3, 1 << (w - 1), 2))
        for u, A in zip(us, ar.batch([mult[u] for u in us])):
            table[u] = A
    return table


def mul_counted(ar, K: Fq2, k: int, P, w: int, *, red=None, da: bool = False):
    """1-D (red=None) or 2-GLV interleaved width-w NAF; da fuses the doubling with the first addition."""
    ar.reset()
    Pa = ar.convert(P)
    conv = K.counts()
    table = _table(ar, Pa, w)
    if red is None:
        streams = [(BI.wnaf(k, w), table)]
        parts = [k]
    else:
        k1, k2 = red.decompose(k)
        parts = [k1, k2]
        t2 = {u: ar.psi_aff(T) for u, T in table.items()}
        streams = []
        for kk, tab in ((k1, table), (k2, t2)):
            if kk < 0:
                tab = {u: ar.neg_aff(T) for u, T in tab.items()}
            streams.append((BI.wnaf(abs(kk), w), tab))
    pre = LC._phase(K, conv)
    before = K.counts()
    L = max(len(s[0]) for s in streams)
    Q = INF
    for i in range(L - 1, -1, -1):
        adds = []
        for ds, tab in streams:
            d = ds[i] if i < len(ds) else 0
            if d:
                adds.append(tab[d] if d > 0 else ar.neg_aff(tab[-d]))
        if Q is INF:
            for T in adds:
                Q = ar.madd(Q, T)
            continue
        if da and adds:
            Q = ar.dbl_add(Q, adds[0])
            adds = adds[1:]
        else:
            Q = ar.dbl(Q)
        for T in adds:
            Q = ar.madd(Q, T)
    main = LC._phase(K, before)
    before = K.counts()
    R = ar.to_affine(Q)
    return R, {"convert": conv, "precompute": pre, "main": main, "final": LC._phase(K, before),
               "total": K.counts(), "parts": parts}


def scalar_counts(inst: dict, widths=(2, 3, 4, 5, 6, 7), scalars: int = 32, references: int = 2,
                  seed: int = 20261008) -> dict:
    F, K, E, G, red = inst["_objects"]
    C = LC.LambdaCurve(K, K.u, E.b)
    lam, ld = LambdaArith(K, C), LDArith(K, E)
    r = inst["r"]
    rng = random.Random(seed)
    ks = [rng.randrange(1, r) for _ in range(scalars)]
    algos = []
    for w in widths:
        algos += [("ld", "1d", w), ("lambda", "1d", w), ("lambda", "1d-da", w),
                  ("ld", "glv", w), ("lambda", "glv", w), ("lambda", "glv-da", w)]
    keys = ("M", "S", "I", "Mc", "Mc_base", "base_M", "base_S", "base_I")
    sums = {a: {**{f"total_{k}": 0 for k in keys}, **{f"conv_{k}": 0 for k in keys},
                **{f"main_{k}": 0 for k in keys}, **{f"pre_{k}": 0 for k in keys}} for a in algos}
    agree = ref_ok = True
    maxbits = 0
    for i, k in enumerate(ks):
        results = set()
        for a in algos:
            coord, alg, w = a
            ar = lam if coord == "lambda" else ld
            R, c = mul_counted(ar, K, k, G, w, red=red if alg.startswith("glv") else None, da=alg.endswith("-da"))
            if alg.startswith("glv"):
                maxbits = max(maxbits, *(abs(x).bit_length() for x in c["parts"]))
            results.add(R)
            s = sums[a]
            for key in keys:
                s[f"total_{key}"] += c["total"][key]
                s[f"conv_{key}"] += c["convert"][key]
                s[f"main_{key}"] += c["main"][key]
                s[f"pre_{key}"] += c["precompute"][key]
        agree &= len(results) == 1
        if i < references:
            ref_ok &= results == {E.mul_affine(k, G)}
    out = {}
    for (coord, alg, w), s in sums.items():
        mean = {key: round(v / scalars, 2) for key, v in s.items()}
        # primary: input already in the method's representation (lambda-affine / affine), base-field operations
        bm = mean["total_base_M"] - mean["conv_base_M"]
        bs = mean["total_base_S"] - mean["conv_base_S"]
        mean["S_free"] = round(bm, 1)
        mean["S_eq_M"] = round(bm + bs, 1)
        mean["S_free_conv"] = round(mean["total_base_M"], 1)
        mean["S_eq_M_conv"] = round(mean["total_base_M"] + mean["total_base_S"], 1)
        # the paper's Table-4 style main-loop count over F_{q^2} (constant multiplications at their F_q cost / 3)
        mean["main_mtilde"] = round(mean["main_M"] + mean["main_Mc_base"] / 3, 1)
        mean["main_stilde"] = mean["main_S"]
        out[f"{coord}/{alg}/w{w}"] = mean
    return {"scalars": scalars, "references_checked": min(references, scalars), "all_algorithms_agree": agree,
            "reference_agrees": ref_ok, "glv_max_coefficient_bits": maxbits, "dbl_formula": C.dbl_formula,
            "configs": out}


def op_counts_gls(inst: dict) -> dict:
    F, K, E, G, red = inst["_objects"]
    C = LC.LambdaCurve(K, K.u, E.b)
    oc = LC.op_counts(E, C)
    # the same formulas in F_q operations
    rng = random.Random(3)
    P, Q = E.random_point(rng), E.random_point(rng)
    Pl, Ql = C.to_lambda_affine(P), C.to_lambda_affine(Q)
    Pp = LC._rand_proj(K, rng, Pl)
    Qp = LC._rand_proj(K, rng, Ql)
    Pd = (K.mul_raw(P[0], Pp[2]), K.mul_raw(P[1], K.sqr_raw(Pp[2])), Pp[2])
    base = {}
    for name, fn in (("lambda doubling_main", lambda: C.dbl(Pp, "main")), ("lambda doubling_alt", lambda: C.dbl(Pp, "alt")),
                     ("lambda full_addition", lambda: C.add(Pp, Qp)), ("lambda mixed_addition", lambda: C.madd(Pp, Ql)),
                     ("lambda doubling_and_addition", lambda: C.dbl_add(Pp, Ql)),
                     ("lambda psi", lambda: psi_lambda(K, Pp)),
                     ("LD doubling", lambda: E.ld_dbl(Pd)), ("LD mixed_addition", lambda: E.ld_madd(Pd, Q))):
        C.reset()
        fn()
        c = K.counts()
        base[name] = {"Fq2": f"{c['M']}M + {c['Mc']}m_c + {c['S']}S", "Fq": f"{c['base_M']}M + {c['base_S']}S"}
    C.reset()
    return {"Fq2_level": oc, "Fq_level": base}


def per_bit(cost: float, log2_order: float) -> float:
    return round(cost / log2_order, 3)


def summarise(inst: dict, sc: dict, nist_json: str | None) -> dict:
    cf = sc["configs"]
    summ = {}
    for col in ("S_free", "S_eq_M", "S_free_conv", "S_eq_M_conv"):
        row = {}
        for pre in ("ld/1d", "lambda/1d", "lambda/1d-da", "ld/glv", "lambda/glv", "lambda/glv-da"):
            w, cost = LC.best(cf, pre, col)
            row[pre] = {"w": w, "cost": cost, "per_bit": per_bit(cost, inst["log2_r"])}
        row["glv_vs_1d_lambda_da"] = round(row["lambda/1d-da"]["cost"] / row["lambda/glv-da"]["cost"], 3)
        row["glv_vs_1d_ld"] = round(row["ld/1d"]["cost"] / row["ld/glv"]["cost"], 3)
        row["lambda_da_vs_ld_glv"] = round(1 - row["lambda/glv-da"]["cost"] / row["ld/glv"]["cost"], 4)
        summ[col] = row
    comp = {}
    if nist_json and os.path.exists(nist_json):
        doc = json.load(open(nist_json))
        for name, r in doc["curves"].items():
            if not r.get("koblitz") or "summary" not in r:
                continue
            comp[name] = {}
            for col in ("S_free", "S_eq_M"):
                s = r["summary"][col]
                comp[name][col] = {
                    "log2_n": r["log2_n"],
                    "ld_tnaf": {"cost": s["ld/tnaf"]["cost"], "per_bit": per_bit(s["ld/tnaf"]["cost"], r["log2_n"])},
                    "lambda_tnaf": {"cost": s["lambda/tnaf"]["cost"],
                                    "per_bit": per_bit(s["lambda/tnaf"]["cost"], r["log2_n"])},
                    "field_bits": r["m"]}
    return {"summary": summ, "koblitz_comparison": comp}


def word_model(bits: int) -> float:
    """MODELLED relative cost of one F_{2^bits} multiplication: Karatsuba on 64-bit words, (ceil(bits/64))^log2(3)."""
    return math.ceil(bits / 64) ** math.log2(3)


def markdown(doc: dict) -> str:
    ins = doc["instance"]
    L = ["# Binary GLS curve with lambda coordinates (counted)", ""]
    poly = " + ".join([f"x^{ins['m']}"] + [f"x^{k}" if k else "1" for k in ins["low"]])
    L.append(f"F_q = F_2[x]/({poly}), F_q2 = F_q[u]/(u^2 + u + 1); E~: y^2 + xy = x^3 + u x^2 + b, b = {ins['b']}.")
    L.append("")
    L.append(f"* trace of E: y^2 + xy = x^3 + b over F_q (AGM): t = {ins['t']}")
    L.append(f"* #E~(F_q2) = (q - 1)^2 + t^2 = 2 r, r prime, log2 r = {ins['log2_r']} "
             f"(found after {doc['search']['candidates_tried']} candidate b)")
    L.append(f"* psi(x, y) = (x^q, y^q + u x^q) acts on <G> as delta, delta^2 = -1 (mod r), "
             f"delta t = {'+' if ins['delta_t_sign'] == 1 else '-'}(q - 1) (mod r)")
    L.append("* checks: " + ", ".join(f"{k}: {v}" for k, v in ins["checks"].items()))
    cb = ins["coefficient_bits"]
    L.append(f"* 2-GLV lattice: Babai bound {cb['bound_bits']} bits, empirical max {cb['empirical_max_bits']} bits "
             f"over 256 scalars (balanced: {cb['balanced_bits']:.1f})")
    L.append("")
    L.append("## Per-operation counts on E~ (measured)")
    L.append("")
    L.append("| formula | F_q2 operations | F_q operations |")
    L.append("|:--|:--|:--|")
    for k, v in doc["op_counts"]["Fq_level"].items():
        L.append(f"| {k} | {v['Fq2']} | {v['Fq']} |")
    L.append("")
    sc = doc["scalar_multiplication"]
    L.append(f"## k*G, mean F_q operations over {sc['scalars']} scalars (best width), input in the method's own form")
    L.append("")
    L.append("| method | S free (M) | per bit of r | S = M (M + S) | per bit of r |")
    L.append("|:--|--:|--:|--:|--:|")
    s = doc["summary"]["summary"]
    for pre in ("ld/1d", "lambda/1d", "lambda/1d-da", "ld/glv", "lambda/glv", "lambda/glv-da"):
        a, b = s["S_free"][pre], s["S_eq_M"][pre]
        L.append(f"| {pre} | {a['cost']:.0f} ({a['w']}) | {a['per_bit']} | {b['cost']:.0f} ({b['w']}) | {b['per_bit']} |")
    L.append("")
    L.append("## Against the Koblitz curves' TNAF (per bit of group order, each in its own field's multiplications)")
    L.append("")
    L.append("| curve | field | log2 order | S free per bit | S = M per bit | modelled F_2^127-mult-equivalents per bit "
             "(S = M) |")
    L.append("|:--|--:|--:|--:|--:|--:|")
    g = s["S_eq_M"]["lambda/glv-da"]
    L.append(f"| GLS-lambda 2-GLV (this curve) | 2^{ins['m']} (F_q ops) | {ins['log2_r']} | {s['S_free']['lambda/glv-da']['per_bit']}"
             f" | {g['per_bit']} | {g['per_bit']:.2f} |")
    for name, r in doc["summary"]["koblitz_comparison"].items():
        lt = r["S_eq_M"]["lambda_tnaf"]
        f = word_model(r["S_eq_M"]["field_bits"]) / word_model(ins["m"])
        L.append(f"| {name[5:]} lambda TNAF | 2^{r['S_eq_M']['field_bits']} | {r['S_eq_M']['log2_n']} | "
                 f"{r['S_free']['lambda_tnaf']['per_bit']} | {lt['per_bit']} | {lt['per_bit'] * f:.2f} |")
        lt = r["S_eq_M"]["ld_tnaf"]
        L.append(f"| {name[5:]} LD TNAF | 2^{r['S_eq_M']['field_bits']} | {r['S_eq_M']['log2_n']} | "
                 f"{r['S_free']['ld_tnaf']['per_bit']} | {lt['per_bit']} | {lt['per_bit'] * f:.2f} |")
    L.append("")
    L.append("The last column is MODELLED: a multiplication in F_2^n is weighted (ceil(n/64))^log2(3) relative to")
    L.append("F_2^127 (Karatsuba on 64-bit words), and a squaring like a multiplication.  It is an assumption, not")
    L.append("a measurement; the per-bit columns before it are measured counts in each curve's own field.")
    L.append("")
    L.append("## Every configuration (F_q operations; main loop also in F_q2 operations)")
    L.append("")
    L.append("| config | S free | S = M | S free, conv. incl. | S = M, conv. incl. | main loop m~ + s~ |")
    L.append("|:--|--:|--:|--:|--:|:--|")
    for k, v in sc["configs"].items():
        L.append(f"| {k} | {v['S_free']} | {v['S_eq_M']} | {v['S_free_conv']} | {v['S_eq_M_conv']} | "
                 f"{v['main_mtilde']} m~ + {v['main_stilde']} s~ |")
    L.append("")
    return "\n".join(L)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="binary GLS curve with lambda coordinates, built and counted")
    ap.add_argument("--m", type=int, default=127)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--scalars", type=int, default=32)
    ap.add_argument("--widths", default="2,3,4,5,6,7")
    ap.add_argument("--seed", type=int, default=20261008)
    ap.add_argument("--nist-json", default=None, help="lambdacoord's lambda.json, for the Koblitz comparison")
    ap.add_argument("--toy-validation", default="7,11,13", help="field sizes for the brute-force AGM checks")
    args = ap.parse_args(argv)
    m = args.m
    low = FIELDS[m]
    doc: dict = {"m": m, "low": list(low), "irreducible": is_irreducible(m, low)}
    # 1. the AGM against brute force on toy fields, and the twist formula on the smallest
    toy = []
    rng = random.Random(args.seed)
    for tm in (int(x) for x in args.toy_validation.split(",") if x):
        F = LC.CountedField(tm, FIELDS[tm])
        for _ in range(3):
            c = rng.getrandbits(tm)
            if c in (0, 1):
                continue
            ta, tb = agm_trace(tm, FIELDS[tm], c), brute_trace(F, 0, c)
            toy.append({"m": tm, "c": c, "agm": ta, "brute_force": tb, "agree": ta == tb})
    twist = []
    for tm in (5, 7):
        F = LC.CountedField(tm, {5: (2, 0), 7: (1, 0)}[tm])
        K = Fq2(F)
        for c in (3, 5):
            t = brute_trace(F, 0, c)
            tt = brute_trace(K, K.u, c)
            q = 1 << tm
            twist.append({"m": tm, "b": c, "t": t, "count_E~": q * q + 1 - tt, "formula": (q - 1) ** 2 + t * t,
                          "agree": q * q + 1 - tt == (q - 1) ** 2 + t * t})
    doc["agm_validation"] = toy
    doc["twist_formula_validation"] = twist
    print("AGM toy validation:", all(x["agree"] for x in toy), " twist formula:", all(x["agree"] for x in twist),
          flush=True)
    # 2. the curve
    t0 = time.time()
    search = find_gls(m, low, seed=args.seed)
    doc["search"] = {k: v for k, v in search.items() if k != "r"} | {"seconds": round(time.time() - t0, 1)}
    print("found", doc["search"], flush=True)
    inst = build(m, low, search["b"], search["t"], search["r"], seed=args.seed)
    doc["instance"] = {k: v for k, v in inst.items() if not k.startswith("_")}
    print("checks", inst["checks"], flush=True)
    doc["op_counts"] = op_counts_gls(inst)
    t0 = time.time()
    widths = tuple(int(w) for w in args.widths.split(","))
    sc = scalar_counts(inst, widths=widths, scalars=args.scalars, seed=args.seed)
    sc["seconds"] = round(time.time() - t0, 1)
    doc["scalar_multiplication"] = sc
    doc["summary"] = summarise(inst, sc, args.nist_json)
    os.makedirs(args.out_dir, exist_ok=True)
    with open(os.path.join(args.out_dir, "gls.json"), "w") as f:
        json.dump(doc, f, indent=1, default=str)
        f.write("\n")
    with open(os.path.join(args.out_dir, "gls.md"), "w") as f:
        f.write(markdown(doc))
    ok = (doc["irreducible"] and all(x["agree"] for x in toy) and all(x["agree"] for x in twist)
          and all(inst["checks"].values()) and sc["all_algorithms_agree"] and sc["reference_agrees"])
    print("all checks pass:", ok)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
