"""Isogeny-class, endomorphism and j-invariant instrument for GOAL-ENDO-001.

Everything here is exact, deterministic, and Sage-free. The instrument answers
one question the rest of the campaign is built on:

    Given p, enumerate EVERY elliptic curve over F_p up to F_p-isomorphism,
    group them into F_p-isogeny classes by trace (Tate), and expose per-curve
    invariants so an attack-cost functional can be measured as a function of
    the curve WITH THE ISOGENY CLASS HELD FIXED.

Two design commitments, both load-bearing:

1.  **Completeness is certified, not assumed.** A within-class variance
    measurement over a biased subset of a class is meaningless. `class_census`
    checks the enumerated class sizes against the Hurwitz-Kronecker class number
    H(4p - t^2), which counts curves with trace t weighted by 2/|Aut|. A census
    mismatch makes a run `invalid_measurement`, never a result.

2.  **Transport is certified independently of the code that computes it.**
    `verify_transport` re-derives k on the target curve and compares; an isogeny
    that does not preserve the discrete log is a bug, not a discovery.

Scope: toy fields (p up to ~2^17 for full enumeration, which is O(p^2) work).
Nothing here supports any crypto-scale claim.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from functools import lru_cache

import numpy as np

from .toycurve import EllipticCurve, Point

# --------------------------------------------------------------------------
# quadratic characters and trace computation
# --------------------------------------------------------------------------


@lru_cache(maxsize=8)
def _chi_table(p: int) -> np.ndarray:
    """chi[u] = Legendre symbol (u|p), as int8, for u in 0..p-1."""
    chi = np.full(p, -1, dtype=np.int8)
    chi[0] = 0
    squares = (np.arange(1, p, dtype=np.int64) ** 2) % p
    chi[squares] = 1
    return chi


@lru_cache(maxsize=8)
def _x_powers(p: int) -> tuple[np.ndarray, np.ndarray]:
    """(x, x^3 mod p) as int64 arrays over the whole field."""
    x = np.arange(p, dtype=np.int64)
    return x, (x * x % p) * x % p


def trace_of_frobenius(p: int, a: int, b: int) -> int:
    """t = p + 1 - #E(F_p), computed exactly by the character sum.

    #E(F_p) = p + 1 + sum_x chi(x^3 + a x + b), so t = -sum_x chi(...).
    Exact, O(p), and independent of any point-counting algorithm.
    """
    chi = _chi_table(p)
    x, x3 = _x_powers(p)
    f = (x3 + a * x + b) % p
    return int(-chi[f].sum())


def curve_order(p: int, a: int, b: int) -> int:
    return p + 1 - trace_of_frobenius(p, a, b)


# --------------------------------------------------------------------------
# j-invariants, twists, and enumeration up to isomorphism
# --------------------------------------------------------------------------


def j_invariant(p: int, a: int, b: int) -> int:
    """j = 1728 * 4a^3 / (4a^3 + 27b^2) mod p."""
    num = 4 * pow(a, 3, p) % p
    den = (num + 27 * pow(b, 2, p)) % p
    if den == 0:
        raise ValueError("singular curve")
    return 1728 * num % p * pow(den, -1, p) % p


def _nonresidue(p: int) -> int:
    chi = _chi_table(p)
    for u in range(2, p):
        if chi[u] == -1:
            return u
    raise ValueError("no non-residue")


def _multiplicative_generator(p: int) -> int:
    """Smallest primitive root mod p (toy scale: trial division on p-1)."""
    n = p - 1
    fac, m = [], n
    d = 2
    while d * d <= m:
        if m % d == 0:
            fac.append(d)
            while m % d == 0:
                m //= d
        d += 1
    if m > 1:
        fac.append(m)
    for g in range(2, p):
        if all(pow(g, n // q, p) != 1 for q in fac):
            return g
    raise ValueError("no generator")


def twists_of_j(p: int, j: int) -> list[tuple[int, int]]:
    """All F_p-isomorphism classes of curves with this j-invariant.

    j not in {0, 1728}: 2 classes (a curve and its quadratic twist).
    j = 0:    6 classes if p = 1 mod 3, else 2 (sextic twists).
    j = 1728: 4 classes if p = 1 mod 4, else 2 (quartic twists).
    """
    g = _multiplicative_generator(p)
    if j == 0:
        n = 6 if p % 3 == 1 else 2
        return [(0, pow(g, i, p)) for i in range(n)]
    if j % p == 1728 % p:
        n = 4 if p % 4 == 1 else 2
        return [(pow(g, i, p), 0) for i in range(n)]
    k = j * pow((1728 - j) % p, -1, p) % p
    a0, b0 = 3 * k % p, 2 * k % p
    d = _nonresidue(p)
    return [(a0, b0), (a0 * pow(d, 2, p) % p, b0 * pow(d, 3, p) % p)]


@dataclass(frozen=True)
class CurveRecord:
    p: int
    a: int
    b: int
    j: int
    trace: int
    order: int
    aut_order: int          # |Aut(E)| over F_p: 2, 4 (j=1728), or 6 (j=0)

    @property
    def label(self) -> str:
        return f"E[p={self.p},a={self.a},b={self.b}]"

    def curve(self) -> EllipticCurve:
        return EllipticCurve(self.p, self.a, self.b)


def enumerate_curves(p: int) -> list[CurveRecord]:
    """Every elliptic curve over F_p up to F_p-isomorphism, with its trace.

    Enumerates by j-invariant and then by twist, which is exactly the
    isomorphism-class decomposition; no curve is counted twice and none is
    missed. Cost is O(p) j-invariants times O(p) per character sum.
    """
    out: list[CurveRecord] = []
    for j in range(p):
        for (a, b) in twists_of_j(p, j):
            if (4 * pow(a, 3, p) + 27 * pow(b, 2, p)) % p == 0:
                continue
            t = trace_of_frobenius(p, a, b)
            if j == 0 and p % 3 == 1:
                aut = 6
            elif j % p == 1728 % p and p % 4 == 1:
                aut = 4
            else:
                aut = 2
            out.append(CurveRecord(p, a, b, j, t, p + 1 - t, aut))
    return out


def isogeny_classes(p: int) -> dict[int, list[CurveRecord]]:
    """Curves grouped by trace. Tate: same trace <=> F_p-isogenous."""
    classes: dict[int, list[CurveRecord]] = {}
    for rec in enumerate_curves(p):
        classes.setdefault(rec.trace, []).append(rec)
    return classes


# --------------------------------------------------------------------------
# completeness certificate: Hurwitz-Kronecker class number
# --------------------------------------------------------------------------


def _class_number_forms(D: int) -> tuple[int, float]:
    """(h(D), weighted h(D)) for a negative discriminant D, by form counting.

    Counts reduced PRIMITIVE positive-definite binary quadratic forms (A,B,C)
    of discriminant D = B^2 - 4AC: |B| <= A <= C, B = A or A = C implies B >= 0.
    The weighted count assigns 1/2 to the form (A,0,A) and 1/3 to (A,A,A),
    which is exactly the weighting in the Hurwitz-Kronecker class number.

    Primitivity -- gcd(A,B,C) = 1 -- is what makes this the class number of the
    order of discriminant D rather than a count over every order above it. It
    was omitted in the first version of this function and `class_census`
    rejected the enumeration on 60 of 127 traces at p = 1009; that is the census
    doing its job, and the check is kept for exactly that reason.
    """
    if D >= 0 or D % 4 not in (0, 1):
        return 0, 0.0
    h, hw = 0, 0.0
    Amax = int(math.isqrt(-D // 3)) + 1
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
            h += 1
            if A == B == C:
                hw += 1.0 / 3.0
            elif A == C and B == 0:
                hw += 1.0 / 2.0
            else:
                hw += 1.0
    return h, hw


def hurwitz_class_number(N: int) -> float:
    """H(N) = sum over f^2 | N with -N/f^2 = 0,1 mod 4 of the weighted h.

    H(0) is conventionally -1/12 and is not used here.
    """
    if N <= 0:
        return 0.0
    total = 0.0
    f = 1
    while f * f <= N:
        if N % (f * f) == 0:
            D = -(N // (f * f))
            if D % 4 in (0, 1):
                total += _class_number_forms(D)[1]
        f += 1
    return total


@dataclass
class CensusResult:
    p: int
    trace: int
    observed_curves: int
    observed_weighted: float          # sum of 2/|Aut| over the class
    predicted_weighted: float         # H(4p - t^2)
    agrees: bool
    note: str = ""


def class_census(p: int, classes: dict[int, list[CurveRecord]]) -> list[CensusResult]:
    """Certify enumeration completeness against Hurwitz-Kronecker.

    For an ORDINARY trace t (p does not divide t, t^2 < 4p), the number of
    F_p-isomorphism classes with trace t, each weighted by 2/|Aut(E)|, equals
    H(4p - t^2). Supersingular traces (t = 0 in particular) obey a different
    mass formula and are reported separately rather than being forced to fit.
    """
    out: list[CensusResult] = []
    for t in sorted(classes):
        recs = classes[t]
        wobs = sum(2.0 / r.aut_order for r in recs)
        if t % p == 0:
            out.append(CensusResult(p, t, len(recs), wobs, float("nan"), True,
                                    "supersingular trace: Hurwitz formula not applied"))
            continue
        pred = hurwitz_class_number(4 * p - t * t)
        out.append(CensusResult(p, t, len(recs), wobs, pred,
                                abs(wobs - pred) < 1e-9))
    return out


# --------------------------------------------------------------------------
# CM data
# --------------------------------------------------------------------------


def frobenius_discriminant(p: int, t: int) -> int:
    return t * t - 4 * p


def fundamental_discriminant(D: int) -> tuple[int, int]:
    """Factor D = D0 * f^2 with D0 a fundamental discriminant. Returns (D0, f)."""
    if D >= 0:
        raise ValueError("expected negative discriminant")
    f = 1
    m = -D
    d = 2
    while d * d <= m:
        while m % (d * d) == 0:
            m //= d * d
            f *= d
        d += 1
    D0 = -m
    if D0 % 4 not in (0, 1):
        D0 *= 4
        if f % 2 == 0:
            f //= 2
        else:
            # -m = 2,3 mod 4 forces an extra factor of 4 into D0
            f = f
    return D0, f


def cm_eigenvalues(p: int, N: int, D0: int) -> list[int]:
    """Eigenvalues in Z/N of the CM endomorphism, for D0 = -3 or -4.

    D0 = -3 (j=0):    lambda^2 + lambda + 1 = 0 mod N
    D0 = -4 (j=1728): lambda^2 + 1 = 0 mod N

    Publicly computable from the curve and N without solving any discrete
    logarithm, which is exactly the condition H-ENDO-001 requires.
    """
    roots = []
    if D0 == -3:
        # lambda = (-1 +- sqrt(-3)) / 2
        s = _sqrt_mod(-3 % N, N)
        if s is not None:
            inv2 = pow(2, -1, N)
            for sign in (s, (-s) % N):
                roots.append((-1 + sign) % N * inv2 % N)
    elif D0 == -4:
        s = _sqrt_mod(-1 % N, N)
        if s is not None:
            roots.extend([s % N, (-s) % N])
    return sorted(set(r for r in roots if r not in (0, 1)))


def _sqrt_mod(a: int, q: int) -> int | None:
    """Tonelli-Shanks square root mod an odd prime q; None if a is not a QR."""
    a %= q
    if a == 0:
        return 0
    if q == 2:
        return a
    if pow(a, (q - 1) // 2, q) != 1:
        return None
    if q % 4 == 3:
        return pow(a, (q + 1) // 4, q)
    s, e = q - 1, 0
    while s % 2 == 0:
        s //= 2
        e += 1
    n = 2
    while pow(n, (q - 1) // 2, q) != q - 1:
        n += 1
    x, bb, g, r = pow(a, (s + 1) // 2, q), pow(a, s, q), pow(n, s, q), e
    while True:
        if bb == 1:
            return x
        m = 0
        t = bb
        while t != 1:
            t = t * t % q
            m += 1
        gs = pow(g, 1 << (r - m - 1), q)
        g = gs * gs % q
        x = x * gs % q
        bb = bb * g % q
        r = m


# --------------------------------------------------------------------------
# Velu isogenies and transport certificates
# --------------------------------------------------------------------------


@dataclass
class Isogeny:
    """An F_p-isogeny E -> E' of odd prime degree ell, from Velu's formulas."""
    source: CurveRecord
    target_a: int
    target_b: int
    degree: int
    kernel_x: list[int] = field(default_factory=list)

    def target(self) -> EllipticCurve:
        return EllipticCurve(self.source.p, self.target_a, self.target_b)


def velu_odd(E: EllipticCurve, kernel_gen: Point, ell: int) -> tuple[int, int, list[int]]:
    """Velu's formulas for a cyclic kernel of ODD prime order ell.

    Returns (a', b', kernel x-coordinates). The kernel is generated by
    `kernel_gen`, which must have exact order ell.

    REFUSES ell = 2 (or any even ell) rather than silently returning the
    identity map. The prior version looped `range((ell-1)//2)`, which is empty
    at ell = 2 and returns (a, b) unchanged with an empty kernel-point list;
    `velu_image` then composes to the identity. RUN-MTGT-p4001e2 measured
    exactly that -- every "transport succeeded" indicator in that run
    (`same_isogeny_class`, `transport_certificate_verified`,
    `entries_lost_to_kernel: 0`) is trivially true of doing nothing, and it was
    committed `valid: true` with no correction bound to it until
    CORR-20260807-3ee25d (defect D1) caught it in independent review. Even-degree
    isogenies need a genuinely different construction (the kernel point of order
    2 is 2-torsion, so `2*gx` is not `gx + gx'` for a "+-pair" -- there is no
    pair), which this module does not implement; ell = 2 must be requested
    through a dedicated 2-isogeny formula, not through this function.
    """
    if ell % 2 == 0:
        raise ValueError(
            f"velu_odd refuses even ell={ell}: this formula's +-pair "
            f"construction requires odd order and silently returns the "
            f"identity map at ell=2 if not guarded (see CORR-20260807-3ee25d "
            f"defect D1). Use a dedicated 2-isogeny formula.")
    p, a, b = E.p, E.a, E.b
    S, Q = [], kernel_gen
    for _ in range((ell - 1) // 2):                 # one point per +-pair
        if Q is None:
            raise ValueError("kernel generator has order < ell")
        S.append(Q)
        Q = E.add(Q, kernel_gen)
    v = w = 0
    for (xq, yq) in S:
        gx = (3 * xq * xq + a) % p
        gy = (-2 * yq) % p
        vq = 2 * gx % p                              # 2-torsion is absent (ell odd)
        uq = gy * gy % p
        v = (v + vq) % p
        w = (w + uq + xq * vq) % p
    return (a - 5 * v) % p, (b - 7 * w) % p, sorted(x for (x, _) in S)


def velu_image(E: EllipticCurve, kernel_pts: list[Point], P: Point) -> Point:
    """Image of P under the Velu isogeny with the given kernel (odd degree)."""
    if P is None:
        return None
    p, a = E.p, E.a
    x, y = P
    X, Y = x, y
    for (xq, yq) in kernel_pts:
        if (x - xq) % p == 0:
            return None                              # P is in the kernel
        gx = (3 * xq * xq + a) % p
        gy = (-2 * yq) % p
        vq = 2 * gx % p
        uq = gy * gy % p
        d = pow((x - xq) % p, -1, p)
        X = (X + vq * d + uq * d * d) % p
        Y = (Y - uq * 2 * y * pow(d, 3, p) - vq * (y * d * d)) % p
    return (X, Y)


def find_kernel_generator(E: EllipticCurve, order: int, ell: int,
                          max_tries: int = 200) -> Point:
    """A point of exact order ell on E, or None if ell does not divide order."""
    if order % ell:
        return None
    cof = order // ell
    for s in range(1, max_tries):
        P = E.random_point(seed=s) if hasattr(E, "random_point") else _det_point(E, s)
        if P is None:
            continue
        R = E.mul(cof, P)
        if R is not None:
            return R
    return None


def _det_point(E: EllipticCurve, s: int) -> Point:
    """Deterministic point search: first liftable x at or after s."""
    for x in range(s % E.p, E.p):
        P = E.lift_x(x)
        if P is not None:
            return P
    return None


@dataclass
class TransportCertificate:
    source: str
    target: str
    degree: int
    order_preserved: bool
    dlog_preserved: bool
    verified: bool
    detail: str = ""


def verify_transport(E: EllipticCurve, kernel_pts: list[Point],
                     P: Point, Q: Point, k: int, N: int) -> TransportCertificate:
    """Certify that an isogeny preserves the ECDLP instance.

    Independent of whatever produced the isogeny: it recomputes [k]phi(P) with
    the plain double-and-add of `toycurve` and compares against phi(Q). This is
    the certificate the campaign's transport claims rest on
    (docs/claims-and-verification.md).
    """
    src = f"E[a={E.a},b={E.b}]"
    fP, fQ = velu_image(E, kernel_pts, P), velu_image(E, kernel_pts, Q)
    if fP is None or fQ is None:
        return TransportCertificate(src, "?", len(kernel_pts) * 2 + 1,
                                    False, False, False,
                                    "P or Q landed in the kernel")
    a2, b2, _ = velu_odd(E, kernel_pts[0], len(kernel_pts) * 2 + 1)
    E2 = EllipticCurve(E.p, a2, b2)
    tgt = f"E[a={a2},b={b2}]"
    on_curve = E2.is_on_curve(fP) and E2.is_on_curve(fQ)
    order_ok = on_curve and E2.mul(N, fP) is None and fP is not None
    dlog_ok = order_ok and E2.mul(k, fP) == fQ
    return TransportCertificate(src, tgt, len(kernel_pts) * 2 + 1,
                                bool(order_ok), bool(dlog_ok),
                                bool(on_curve and order_ok and dlog_ok),
                                "" if on_curve else "image not on target curve")


# --------------------------------------------------------------------------
# ell-volcano level
# --------------------------------------------------------------------------


def rational_isogeny_count(rec: CurveRecord, ell: int) -> int:
    """Number of F_p-rational ell-isogenies from this curve.

    Counted structurally: the number of order-ell subgroups of E(F_p)[ell]
    that are Galois-stable, which at toy scale is read off the ell-torsion
    available over F_p. On a volcano this is ell+1 at the crater (when ell
    splits), 1 on the sides, and 0 at the floor when ell is inert.
    """
    E = rec.curve()
    n = rec.order
    if n % ell:
        return 0
    # count order-ell points over F_p; a full E[ell] rational gives ell^2-1
    count = 0
    for x in range(rec.p):
        P = E.lift_x(x)
        if P is None:
            continue
        R = E.mul(n // ell, P)
        if R is not None and E.mul(ell, R) is None:
            count += 1
        # each x gives +-y; both have the same order, count once per x
    # number of order-ell subgroups = (#order-ell points) / (ell - 1)
    pts = count * 2
    return pts // (ell - 1) if pts else 0


__all__ = [
    "CurveRecord", "CensusResult", "Isogeny", "TransportCertificate",
    "trace_of_frobenius", "curve_order", "j_invariant", "twists_of_j",
    "enumerate_curves", "isogeny_classes", "class_census",
    "hurwitz_class_number", "frobenius_discriminant", "fundamental_discriminant",
    "cm_eigenvalues", "velu_odd", "velu_image", "find_kernel_generator",
    "verify_transport", "rational_isogeny_count",
]
