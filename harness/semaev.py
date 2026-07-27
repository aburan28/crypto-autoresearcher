"""Semaev summation polynomials and a Groebner-basis decomposition measurement.

Implements S_2, S_3, S_4 (KN-TECH-002) and the point-decomposition test
(KN-TECH-003): given a target point R and a factor base of small x-coordinates,
does R decompose as a sum of factor-base points? The *cost* of the associated
Groebner-basis computation is the measured quantity for EXP-SEMAEV experiments
(KN-OPEN-002).

Honesty note on metrics: sympy uses a Buchberger/F5-style routine, not an
optimized F4, and does not expose the true degree of regularity reached during
computation. We therefore report *observable* proxies -- the size and maximum
total degree of the reduced Groebner basis, and wall time -- and label them as
implementation-bound proxies, never as the theoretical degree of regularity.
Only trends versus parameters are interpreted; absolute timings are not
crypto-scale claims.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field

import sympy

from .toycurve import ECDLPInstance, EllipticCurve, Point, _seed_int

x1, x2, x3, _t = sympy.symbols("x1 x2 x3 t")


def s2(a, b):
    return x1 - x2


def s3_expr(a: int, b: int):
    """Third summation polynomial for y^2 = x^3 + a*x + b, in x1, x2, x3."""
    return (
        (x1 - x2) ** 2 * x3 ** 2
        - 2 * ((x1 + x2) * (x1 * x2 + a) + 2 * b) * x3
        + ((x1 * x2 - a) ** 2 - 4 * b * (x1 + x2))
    )


def s3_eval(a: int, b: int, v1: int, v2: int, v3: int, p: int) -> int:
    """S_3(v1, v2, v3) mod p, evaluated directly (no symbolic overhead)."""
    term = (
        (v1 - v2) ** 2 * v3 ** 2
        - 2 * ((v1 + v2) * (v1 * v2 + a) + 2 * b) * v3
        + ((v1 * v2 - a) ** 2 - 4 * b * (v1 + v2))
    )
    return term % p


def s4_expr(a: int, b: int):
    """Fourth summation polynomial via resultant S4 = Res_t(S3(x1,x2,t), S3(x3,x4,t))."""
    x4 = sympy.symbols("x4")
    left = s3_expr(a, b).subs(x3, _t)
    right = s3_expr(a, b).subs({x1: x3, x2: x4, x3: _t})
    return sympy.resultant(left, right, _t)


def build_factor_base(inst: ECDLPInstance, size: int, seed: int = 0) -> list[int]:
    """Deterministic factor base: `size` distinct on-curve x-coordinates."""
    E = inst.curve()
    p = E.p
    xs: list[int] = []
    j = 0
    while len(xs) < size and j < 50 * size + 1000:
        x = _seed_int(seed if seed else inst.seed, f"fb{j}") % p
        j += 1
        if x in xs:
            continue
        if E.lift_x(x) is not None:
            xs.append(x)
    return xs


@dataclass
class DecompositionMeasurement:
    field_bits: int
    p: int
    factor_base_size: int
    decomposition_length: int          # m (= 2 for S_3)
    target_x: int
    groebner_seconds: float
    groebner_basis_size: int
    groebner_basis_max_degree: int     # proxy, NOT degree of regularity
    is_trivial_ideal: bool             # basis == [1] -> no decomposition
    decomposition_found: bool
    summand_x: list[int] = field(default_factory=list)
    certificate: dict | None = None


def measure_s3_decomposition(inst: ECDLPInstance, factor_base_size: int,
                             target: Point | None = None,
                             seed: int = 0,
                             factor_base: list[int] | None = None) -> DecompositionMeasurement:
    """Measure the S_3 (length-2) decomposition test for a target point.

    Builds the ideal <S3(x1,x2,xR), fV(x1), fV(x2)> over F_p where fV forces
    each variable into the factor base V, times its Groebner basis, and -- by
    direct enumeration over the small V -- reports whether R decomposes, with a
    verifiable certificate when it does.
    """
    E = inst.curve()
    p, a, b = E.p, E.a, E.b
    R = inst.Q if target is None else target
    if R is None:
        raise ValueError("target point must be affine")
    xR = R[0]

    if factor_base is None:
        V = build_factor_base(inst, factor_base_size, seed)
    else:
        V = list(factor_base)
        if factor_base_size is None or factor_base_size <= 0:
            factor_base_size = len(V)
    fV1 = sympy.prod([(x1 - v) for v in V])
    fV2 = sympy.prod([(x2 - v) for v in V])
    system = [s3_expr(a, b).subs(x3, xR), fV1, fV2]

    t0 = time.perf_counter()
    G = sympy.groebner(system, x1, x2, modulus=p, order="grevlex")
    gb_seconds = time.perf_counter() - t0

    polys = list(G.exprs)
    max_deg = 0
    for g in polys:
        try:
            d = sympy.Poly(g, x1, x2, modulus=p).total_degree()
        except sympy.PolynomialError:
            d = 0
        max_deg = max(max_deg, d)
    is_trivial = polys == [sympy.Integer(1)] or (len(polys) == 1 and polys[0] == 1)

    # Certificate: enumerate the (small) factor base for an exact decomposition.
    found, summands, cert = _find_decomposition(E, V, R, a, b, p)

    return DecompositionMeasurement(
        field_bits=inst.field_bits, p=p, factor_base_size=len(V),
        decomposition_length=2, target_x=xR,
        groebner_seconds=gb_seconds, groebner_basis_size=len(polys),
        groebner_basis_max_degree=max_deg, is_trivial_ideal=bool(is_trivial),
        decomposition_found=found, summand_x=[s[0] for s in summands] if found else [],
        certificate=cert,
    )


def _find_decomposition(E: EllipticCurve, V: list[int], R: Point,
                        a: int, b: int, p: int):
    """Search V x V for factor-base points A, B with A + B == R (verifiable)."""
    xR = R[0]
    for i, v1 in enumerate(V):
        for v2 in V[i:]:
            if s3_eval(a, b, v1, v2, xR, p) != 0:
                continue
            A = E.lift_x(v1)
            B = E.lift_x(v2)
            if A is None or B is None:
                continue
            for sA in (A, E.negate(A)):
                for sB in (B, E.negate(B)):
                    if E.add(sA, sB) == R:
                        cert = {
                            "kind": "decomposition",
                            "statement": {
                                "target": list(R),
                                "summands": [list(sA), list(sB)],
                                "curve": {"p": p, "a": a, "b": b},
                            },
                        }
                        return True, [sA, sB], cert
    return False, [], None


def verify_decomposition_certificate(cert: dict) -> bool:
    """Independent check: do the summands lie on E and sum to the target?"""
    if not cert or cert.get("kind") != "decomposition":
        return False
    st = cert["statement"]
    c = st["curve"]
    E = EllipticCurve(c["p"], c["a"], c["b"])
    target = tuple(st["target"])
    acc: Point = None
    for s in st["summands"]:
        pt = tuple(s)
        if not E.is_on_curve(pt):
            return False
        acc = E.add(acc, pt)
    return acc == target
