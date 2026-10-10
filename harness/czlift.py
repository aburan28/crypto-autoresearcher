"""Characteristic-zero lifting instruments for GOAL-CZLIFT-1516d5.

NEW MODULE. Exact arithmetic on a short-Weierstrass curve over the truncated
ring Z/p^k (a model of E(Z_p) at precision k), the Hensel and Teichmuller point
lifts, the prime-to-p TORSION SECTION of E(Q_p) -> E(F_p), the formal-group
parameter z = -X/Y, and Smart's anomalous-curve ratio. Reuses
harness/toycurve.py (F_p arithmetic and exact point counting) unmodified.

Mathematical conventions, stated once:

* A point of E(Z/p^k) is a projective triple (X, Y, Z) mod p^k with at least one
  unit coordinate. O is (0, 1, 0). The group law is the COMPLETE formula of
  Renes, Costello and Batina (EUROCRYPT 2016, Algorithm 1, general a), which is
  a polynomial map without division. Over a field of characteristic not 2, 3 it
  is exception-free on pairs whose difference is not a rational point of exact
  order 2; every instrument here keeps its points in a subgroup of odd order, so
  that exception never arises, and the reduction mod p of every output is a
  valid F_p point, hence never (0, 0, 0): the triple is determined mod p^k.
* A point reducing to O mod p has X = Z = 0 mod p and Y a unit; its formal
  parameter is z = -X/Y, with v_p(z) >= 1. The formal logarithm satisfies
  log_F(z) = z + O(z^2), so for two parameters of EQUAL valuation v >= 1 the
  leading p-adic digit of log_F(z_Q)/log_F(z_P) equals that of z_Q/z_P. Smart's
  attack reads exactly that digit, so this module divides z-values and never
  needs the series.
* v_p(x) for x in Z/p^k is reported as k ("at least k") when x = 0 mod p^k.

Nothing here is an attack on a deployed curve; every prime is small.
"""
from __future__ import annotations

import random
from dataclasses import dataclass

from harness.toycurve import EllipticCurve

# ---------------------------------------------------------------------------
# Class-number-one CM curves over Q (integral short-Weierstrass models) and the
# j-invariants they must reproduce. The models are CHECKED against the j list
# in cm_self_test(); the j list is the standard one (Heegner-Stark).
# ---------------------------------------------------------------------------
# Short models y^2 = x^3 - 27 c4 x - 54 c6 of the standard minimal models
# (Cremona 27a3, 32a2, 49a1, 256a1, 121b1, 361a1, 1849a1, 4489a1, 26569a1;
# recalled, not retrieved). Any integral model with the CM j-invariant is the
# canonical lift at every prime of good reduction, and cm_self_test() checks
# the j of each model exactly, so a misremembered model cannot pass silently.
# D = -3 and -4 use the simplest j = 0 and j = 1728 models directly.
CM_MODELS: dict[int, tuple[int, int]] = {
    -3: (0, 1),
    -4: (1, 0),
    -7: (-2835, -71442),
    -8: (-4320, 96768),
    -11: (-9504, 365904),
    -19: (-49248, 4210704),
    -43: (-1114560, 452901456),
    -67: (-9551520, 11362054032),
    -163: (-2818048320, 57579881513616),
}
CM_J: dict[int, int] = {
    -3: 0,
    -4: 1728,
    -7: -3375,
    -8: 8000,
    -11: -32768,
    -19: -884736,
    -43: -884736000,
    -67: -147197952000,
    -163: -262537412640768000,
}


def j_invariant_q(a: int, b: int):
    """j of y^2 = x^3 + a x + b over Q as an exact Fraction."""
    from fractions import Fraction
    return Fraction(1728 * 4 * a ** 3, 4 * a ** 3 + 27 * b ** 2)


def cm_self_test() -> None:
    for d, (a, b) in CM_MODELS.items():
        j = j_invariant_q(a, b)
        if j != CM_J[d]:
            raise AssertionError(f"CM model for D={d} has j={j}, expected {CM_J[d]}")


def ramification_index(j: int) -> int:
    """Ramification index of the j-map at the CM point: 3 at j=0, 2 at 1728."""
    if j == 0:
        return 3
    if j == 1728:
        return 2
    return 1


# ---------------------------------------------------------------------------
# Valuations and Teichmuller representatives
# ---------------------------------------------------------------------------

def val_p(x: int, p: int, k: int) -> int:
    x %= p ** k
    if x == 0:
        return k
    v = 0
    while x % p == 0:
        x //= p
        v += 1
    return v


def teichmuller(x0: int, p: int, k: int) -> int:
    """The Teichmuller representative of x0 mod p in Z/p^k (fixed by x -> x^p)."""
    M = p ** k
    x = x0 % M
    for _ in range(k + 1):
        x = pow(x, p, M)
    return x


# ---------------------------------------------------------------------------
# E(Z/p^k) with complete projective formulas
# ---------------------------------------------------------------------------

Proj = tuple[int, int, int]


@dataclass(frozen=True)
class ZpCurve:
    p: int
    k: int
    a: int
    b: int

    @property
    def M(self) -> int:
        return self.p ** self.k

    def __post_init__(self):
        M = self.p ** self.k
        object.__setattr__(self, "a", self.a % M)
        object.__setattr__(self, "b", self.b % M)
        if (4 * self.a ** 3 + 27 * self.b ** 2) % self.p == 0:
            raise ValueError("bad reduction: discriminant is 0 mod p")

    # -- basic predicates ------------------------------------------------
    def zero(self) -> Proj:
        return (0, 1, 0)

    def is_unit(self, x: int) -> bool:
        return x % self.p != 0

    def on_curve(self, P: Proj) -> bool:
        X, Y, Z = P
        M = self.M
        return (Y * Y * Z - (X ** 3 + self.a * X * Z * Z + self.b * Z ** 3)) % M == 0

    def is_zero(self, P: Proj, prec: int | None = None) -> bool:
        """P = O at precision `prec` (default k): X = Z = 0 mod p^prec, Y unit."""
        prec = self.k if prec is None else prec
        m = self.p ** prec
        X, Y, Z = P
        return X % m == 0 and Z % m == 0 and self.is_unit(Y)

    def eq(self, P: Proj, Q: Proj, prec: int | None = None) -> bool:
        prec = self.k if prec is None else prec
        m = self.p ** prec
        X1, Y1, Z1 = P
        X2, Y2, Z2 = Q
        return ((X1 * Y2 - X2 * Y1) % m == 0 and (X1 * Z2 - X2 * Z1) % m == 0
                and (Y1 * Z2 - Y2 * Z1) % m == 0)

    def neg(self, P: Proj) -> Proj:
        X, Y, Z = P
        return (X, (-Y) % self.M, Z)

    # -- Renes-Costello-Batina complete addition, Algorithm 1 (general a) --
    def add(self, P: Proj, Q: Proj) -> Proj:
        M = self.M
        a = self.a
        b3 = 3 * self.b % M
        X1, Y1, Z1 = P
        X2, Y2, Z2 = Q
        t0 = X1 * X2 % M
        t1 = Y1 * Y2 % M
        t2 = Z1 * Z2 % M
        t3 = (X1 + Y1) * (X2 + Y2) % M
        t4 = (t0 + t1) % M
        t3 = (t3 - t4) % M
        t4 = (X1 + Z1) * (X2 + Z2) % M
        t5 = (t0 + t2) % M
        t4 = (t4 - t5) % M
        t5 = (Y1 + Z1) * (Y2 + Z2) % M
        X3 = (t1 + t2) % M
        t5 = (t5 - X3) % M
        Z3 = a * t4 % M
        X3 = b3 * t2 % M
        Z3 = (X3 + Z3) % M
        X3 = (t1 - Z3) % M
        Z3 = (t1 + Z3) % M
        Y3 = X3 * Z3 % M
        t1 = (t0 + t0 + t0) % M
        t2 = a * t2 % M
        t4 = b3 * t4 % M
        t1 = (t1 + t2) % M
        t2 = (t0 - t2) % M
        t2 = a * t2 % M
        t4 = (t4 + t2) % M
        t0 = t1 * t4 % M
        Y3 = (Y3 + t0) % M
        t0 = t5 * t4 % M
        X3 = t3 * X3 % M
        X3 = (X3 - t0) % M
        t0 = t3 * t1 % M
        Z3 = t5 * Z3 % M
        Z3 = (Z3 + t0) % M
        if not (self.is_unit(X3) or self.is_unit(Y3) or self.is_unit(Z3)):
            raise ArithmeticError("addition produced a non-unit triple (exceptional pair)")
        return (X3, Y3, Z3)

    def sub(self, P: Proj, Q: Proj) -> Proj:
        return self.add(P, self.neg(Q))

    def mul(self, n: int, P: Proj) -> Proj:
        """[n]P by double-and-add with the complete formula; counts additions."""
        if n < 0:
            return self.mul(-n, self.neg(P))
        R = self.zero()
        A = P
        while n:
            if n & 1:
                R = self.add(R, A)
            n >>= 1
            if n:
                A = self.add(A, A)
        return R

    def mul_count(self, n: int) -> int:
        """Number of complete additions mul() spends on the scalar n."""
        if n < 0:
            n = -n
        return bin(n).count("1") + max(n.bit_length() - 1, 0)

    # -- coordinates -----------------------------------------------------
    def affine(self, P: Proj) -> tuple[int, int] | None:
        X, Y, Z = P
        if not self.is_unit(Z):
            return None
        zi = pow(Z, -1, self.M)
        return (X * zi % self.M, Y * zi % self.M)

    def reduce(self, P: Proj):
        """Reduction to E(F_p): affine pair, or None for O."""
        X, Y, Z = P
        p = self.p
        if Z % p == 0:
            return None
        zi = pow(Z % p, -1, p)
        return (X * zi % p, Y * zi % p)

    def z_param(self, P: Proj) -> int:
        """Formal parameter z = -X/Y of a point reducing to O (Y must be a unit)."""
        X, Y, Z = P
        if not self.is_unit(Y) or Z % self.p != 0:
            raise ValueError("z_param needs a point in the formal group (Z = 0 mod p, Y unit)")
        return (-X) * pow(Y, -1, self.M) % self.M

    def j_invariant(self) -> int:
        """j mod p^k; requires 4a^3 + 27b^2 to be a unit (good reduction)."""
        M = self.M
        den = (4 * self.a ** 3 + 27 * self.b ** 2) % M
        return 1728 * 4 * self.a ** 3 * pow(den, -1, M) % M

    def fp_curve(self) -> EllipticCurve:
        return EllipticCurve(self.p, self.a % self.p, self.b % self.p)

    # -- lifts -----------------------------------------------------------
    def hensel_lift(self, x0: int, y0: int, eps: int = 0, x_override: int | None = None) -> Proj:
        """A lift of (x0, y0) in E(F_p), y0 != 0: x = x0 + p*eps, y by Newton."""
        M = self.M
        p = self.p
        if y0 % p == 0:
            raise ValueError("Hensel lift needs y0 != 0 (no 2-torsion)")
        x = (x0 + p * eps) % M if x_override is None else x_override % M
        if x % p != x0 % p:
            raise ValueError("x_override must reduce to x0")
        f = (x ** 3 + self.a * x + self.b) % M
        y = y0 % M
        for _ in range(self.k + 1):
            y = (y - (y * y - f) * pow(2 * y, -1, M)) % M
        if (y * y - f) % M != 0:
            raise ArithmeticError("Newton iteration did not converge")
        return (x, y, 1)

    def teichmuller_lift(self, x0: int, y0: int) -> Proj:
        return self.hensel_lift(x0, y0, x_override=teichmuller(x0, self.p, self.k))

    def torsion_section(self, Phat: Proj, n: int) -> tuple[Proj, int]:
        """The unique lift of red(Phat) in E(Z/p^k)[n] (needs gcd(n, p) = 1).

        T = [n]Phat lies in the formal group; U = [n^{-1} mod p^k]T is the unique
        formal-group point with [n]U = T; Phat - U is n-torsion. Returns the
        point and the number of complete additions spent.
        """
        if n % self.p == 0:
            raise ValueError("torsion_section needs n prime to p")
        T = self.mul(n, Phat)
        m = pow(n, -1, self.M)
        U = self.mul(m, T)
        Pt = self.sub(Phat, U)
        cost = self.mul_count(n) + self.mul_count(m) + 1
        return Pt, cost


# ---------------------------------------------------------------------------
# Smart-style ratio
# ---------------------------------------------------------------------------

def smart_ratio(E: ZpCurve, Phat: Proj, Qhat: Proj, n: int):
    """Leading digit of z([n]Qhat) / z([n]Phat), with both valuations.

    Returns (ratio or None, vP, vQ). The ratio is defined only when the two
    valuations are equal and strictly below the precision; it is read at
    precision vP + 1, i.e. mod p.
    """
    p, k = E.p, E.k
    zP = E.z_param(E.mul(n, Phat))
    zQ = E.z_param(E.mul(n, Qhat))
    vP, vQ = val_p(zP, p, k), val_p(zQ, p, k)
    if vP >= k or vQ < vP:
        return None, vP, vQ
    if vQ > vP:
        return 0, vP, vQ
    uP = (zP // p ** vP) % p
    uQ = (zQ // p ** vQ) % p
    return uQ * pow(uP, -1, p) % p, vP, vQ


# ---------------------------------------------------------------------------
# F_p side helpers (toycurve reused)
# ---------------------------------------------------------------------------

def is_prime(n: int) -> bool:
    import sympy
    return bool(sympy.isprime(n))


def largest_prime_factor(n: int) -> int:
    import sympy
    return max(sympy.factorint(n))


def random_point(E: EllipticCurve, rng: random.Random):
    while True:
        x = rng.randrange(E.p)
        P = E.lift_x(x)
        if P is not None and P[1] != 0:
            if rng.random() < 0.5:
                P = E.negate(P)
            return P


def point_of_order(E: EllipticCurve, n: int, cofactor: int, rng: random.Random):
    """A point of exact prime order n in E(F_p), #E = n * cofactor."""
    while True:
        P = E.mul(cofactor, random_point(E, rng))
        if P is not None and P[1] != 0 and E.mul(n, P) is None:
            return P


def anomalous_cm_curves(pmax: int, discriminants=(-3, -11, -19, -43, -67, -163)):
    """Class-number-one CM curves E/F_p with #E(F_p) = p, p <= pmax.

    4p = 1 + |D| v^2 with v odd makes p a norm from O_K, so one twist of the
    CM curve has trace exactly 1. Yields (D, p, A, B, j_D) with (A, B) the
    INTEGRAL CM model (twisted) whose reduction is the anomalous curve and
    whose j is the CM j, i.e. the canonical lift as an explicit curve over Z.
    """
    cm_self_test()
    out = []
    for D in discriminants:
        A0, B0 = CM_MODELS[D]
        disc = 4 * A0 ** 3 + 27 * B0 ** 2
        v = 1
        while True:
            num = 1 + abs(D) * v * v
            if num % 4 == 0:
                p = num // 4
                if p > pmax:
                    break
                if p > 5 and is_prime(p) and disc % p != 0 and (6 * D) % p != 0:
                    for A, B in _twists(D, A0, B0, p):
                        if EllipticCurve(p, A % p, B % p).order() == p:
                            out.append((D, p, A, B, CM_J[D]))
                            break
            v += 2
    return out


def _twists(D: int, A0: int, B0: int, p: int):
    """Integral twist models of the CM curve: sextic for D=-3, quadratic else."""
    if D == -3:
        reps = []
        seen = set()
        for t in range(1, p):
            c = pow(t, (p - 1) // 6, p)  # class of t in F_p^*/(F_p^*)^6 is encoded by t^((p-1)/6)... only for p = 1 mod 6
            key = c if (p - 1) % 6 == 0 else t
            if key in seen:
                continue
            seen.add(key)
            reps.append(t)
            if len(reps) == (6 if (p - 1) % 6 == 0 else 2):
                break
        return [(0, B0 * t) for t in reps]
    nonres = next(t for t in range(2, p) if pow(t, (p - 1) // 2, p) == p - 1)
    return [(A0, B0), (A0 * nonres ** 2, B0 * nonres ** 3)]


def cm_curves_with_prime_subgroup(pmin: int, pmax: int, nmin: int,
                                  discriminants=(-3, -7, -8, -11, -19, -43, -67, -163),
                                  rng: random.Random | None = None):
    """Non-anomalous CM reductions with a prime-order subgroup n != p, n >= nmin."""
    import sympy
    cm_self_test()
    rng = rng or random.Random(0)
    out = []
    for p in sympy.primerange(pmin, pmax + 1):
        for D in discriminants:
            A0, B0 = CM_MODELS[D]
            if (6 * D * (4 * A0 ** 3 + 27 * B0 ** 2)) % p == 0:
                continue
            for A, B in _twists(D, A0, B0, p):
                N = EllipticCurve(p, A % p, B % p).order()
                n = largest_prime_factor(N)
                if n >= nmin and n != p and N % 2 == 1:
                    out.append((D, p, A, B, N, n))
    return out


def random_curves_with_prime_subgroup(p_list, nmin: int, rng: random.Random, tries: int = 200):
    out = []
    for p in p_list:
        for _ in range(tries):
            a, b = rng.randrange(p), rng.randrange(p)
            if (4 * a ** 3 + 27 * b * b) % p == 0:
                continue
            N = EllipticCurve(p, a, b).order()
            n = largest_prime_factor(N)
            if n >= nmin and n != p and N % 2 == 1:
                out.append((p, a, b, N, n))
                break
    return out


# ---------------------------------------------------------------------------
# Self-test: complete formula vs affine F_p arithmetic and vs Q
# ---------------------------------------------------------------------------

def self_test(seed: int = 1) -> dict:
    cm_self_test()
    rng = random.Random(seed)
    checks = 0
    # 1. mod p agreement with the affine toy model on random odd-order subgroups
    for p in (11, 101, 1009):
        for _ in range(5):
            a, b = rng.randrange(p), rng.randrange(p)
            if (4 * a ** 3 + 27 * b * b) % p == 0:
                continue
            Efp = EllipticCurve(p, a, b)
            N = Efp.order()
            n = largest_prime_factor(N)
            if n < 5 or N % 2 == 0 or n == p:
                continue
            E = ZpCurve(p, 3, a, b)
            P = point_of_order(Efp, n, N // n, rng)
            Ph = E.hensel_lift(*P, eps=rng.randrange(p))
            assert E.on_curve(Ph)
            for _ in range(20):
                i, j = rng.randrange(n), rng.randrange(n)
                S = E.add(E.mul(i, Ph), E.mul(j, Ph))
                assert E.reduce(S) == Efp.mul((i + j) % n, P)
                assert E.eq(S, E.mul((i + j), Ph), prec=1)
                checks += 1
            # the torsion section is n-torsion and reduces correctly
            Pt, _ = E.torsion_section(Ph, n)
            assert E.is_zero(E.mul(n, Pt)) and E.reduce(Pt) == P
            checks += 1
    # 2. agreement with exact rational arithmetic on a global curve
    from fractions import Fraction

    def q_add(P, Q, a):
        if P is None:
            return Q
        if Q is None:
            return P
        x1, y1 = P
        x2, y2 = Q
        if x1 == x2 and y1 == -y2:
            return None
        lam = (3 * x1 * x1 + a) / (2 * y1) if P == Q else (y2 - y1) / (x2 - x1)
        x3 = lam * lam - x1 - x2
        return (x3, lam * (x1 - x3) - y1)

    # y^2 = x^3 - 2 has the rational point (3, 5) and no rational 2-torsion;
    # 2 is not a cube mod 7 or mod 13, so E(F_p) has no 2-torsion there either
    # and the complete formula meets no exceptional pair along the chain.
    a, b = 0, -2
    P0 = (Fraction(3), Fraction(5))
    for p, k in ((7, 4), (13, 3)):
        E = ZpCurve(p, k, a, b)
        M = p ** k
        Pz = (3, 5, 1)
        R = None
        for m in range(1, 9):
            R = q_add(R, P0, a)
            Rz = E.mul(m, Pz)
            if R is None:
                assert E.is_zero(Rz)
            else:
                x, y = R
                if x.denominator % p == 0:
                    assert not E.is_unit(Rz[2])
                else:
                    aff = E.affine(Rz)
                    assert aff is not None
                    assert aff[0] == x.numerator * pow(x.denominator, -1, M) % M
                    assert aff[1] == y.numerator * pow(y.denominator, -1, M) % M
            checks += 1
    return {"checks": checks, "ok": True}


if __name__ == "__main__":
    print(self_test())
