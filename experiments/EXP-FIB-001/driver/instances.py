"""Instance / factor-base / target freezing for EXP-FIB-001 (RUN-FIB-001 role).

All curves come from harness.toycurve.generate_instance (public data only).
The subgroup order actually produced by that function (the largest prime
factor of #E) is NOT guaranteed to be close to 2**field_bits -- it depends on
the curve found for the given (seed, field_bits). This is recorded honestly
(see implementation.md, "actual subgroup order" note) rather than assumed.

Factor-base construction -- documented deviation from a literal call to
harness.semaev.build_factor_base (see implementation.md "factor base must
share the target's subgroup" note): that shared helper draws x-coordinates
from anywhere on the *full* curve E(F_p) (order ~p), while targets
R = a*P + b*Q are confined to the cyclic subgroup <P> of order N = inst.n.
Since N is frequently orders of magnitude smaller than p for the curves this
generate_instance() implementation actually returns (verified empirically:
N in {23, 733, 87281, 4271} for the four main curves, not ~2**field_bits),
sampling the factor base from the full curve makes almost every 3-subset sum
land outside <P> by construction (probability ~ N/p of landing back inside),
producing a near-total-zero n_R regardless of any real fiber-invariant
signal -- a structural artifact of the group mismatch, not a measurement of
decomposition difficulty. HEUR-001's birthday model ("lambda = C(B,3)/N")
is only a coherent, testable claim if the C(B,3) tuple sums and the N
possible targets are quasirandom draws from the *same* group. This module
therefore draws the factor base from <P> itself (x-coordinates of B distinct
seeded scalar multiples of P), matching the group R actually lives in. This
is new EXP-FIB-001-local glue, not an edit to the shared harness module.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from harness.toycurve import ECDLPInstance, EllipticCurve, generate_instance

from .common import canon_lift, seeded_rng, sha256_of


def build_factor_base_in_subgroup(inst: ECDLPInstance, size: int, seed: int) -> list[int]:
    """B distinct x-coordinates of scalar multiples of P (i.e. elements of
    <P>, order N = inst.n) -- see module docstring for why this, not
    harness.semaev.build_factor_base, is used here.
    """
    E = inst.curve()
    N = inst.n
    rng = seeded_rng(seed, "factor_base_subgroup")
    xs: list[int] = []
    seen_x = set()
    tried = 0
    max_tries = 200 * size + 2000
    while len(xs) < size and tried < max_tries and len(xs) < N - 1:
        c = rng.randrange(1, N)
        tried += 1
        pt = E.mul(c, inst.P)
        if pt is None:
            continue
        x = pt[0]
        if x in seen_x:
            continue
        seen_x.add(x)
        xs.append(x)
    return xs

MAIN_CURVES = [
    {"id": "C16-1", "field_bits": 16, "seed": 1},
    {"id": "C16-2", "field_bits": 16, "seed": 2},
    {"id": "C20-1", "field_bits": 20, "seed": 1},
    {"id": "C20-2", "field_bits": 20, "seed": 2},
]

TRUTH_CURVES = [
    {"id": "C8-1", "field_bits": 8, "seed": 1},
    {"id": "C10-1", "field_bits": 10, "seed": 1},
    {"id": "C12-1", "field_bits": 12, "seed": 1},
]


@dataclass
class CurveContext:
    spec: dict
    inst: ECDLPInstance
    E: EllipticCurve
    N: int                 # subgroup order actually produced
    B: int                 # factor base size = ceil(sqrt(N))
    V: list[int]            # factor base x-coordinates
    V_canon: list           # canonical (x,y) points, same order as V


def build_curve(spec: dict) -> CurveContext:
    inst = generate_instance(seed=spec["seed"], field_bits=spec["field_bits"])
    E = inst.curve()
    N = inst.n
    B = math.isqrt(N) + 1
    V = build_factor_base_in_subgroup(inst, B, seed=spec["seed"])
    V_canon = [canon_lift(E, x) for x in V]
    # Every factor-base element is on-curve by construction (build_factor_base
    # uses lift_x internally), so canon_lift should never return None here.
    assert all(p is not None for p in V_canon), "factor-base element off-curve"
    return CurveContext(spec=spec, inst=inst, E=E, N=N, B=B, V=V, V_canon=V_canon)


def generate_targets(ctx: CurveContext, count: int, tag: str = "targets") -> list[dict]:
    """count targets R_i = a_i*P + b_i*Q, a,b uniform in [1, N-1] (seeded).

    Scalars are recorded (for the rho control and certificate verification)
    but never fed to the n_R predictor.
    """
    rng = seeded_rng(ctx.spec["seed"], f"{ctx.spec['id']}:{tag}")
    E, P, Q, N = ctx.E, ctx.inst.P, ctx.inst.Q, ctx.N
    out = []
    for i in range(count):
        a = rng.randrange(1, N)
        b = rng.randrange(1, N)
        R = E.add(E.mul(a, P), E.mul(b, Q))
        if R is None:
            # O has no x-coordinate; redraw deterministically once.
            a = (a + 1) % N or 1
            R = E.add(E.mul(a, P), E.mul(b, Q))
        out.append({"index": i, "a": a, "b": b, "Rx": R[0] if R else None,
                     "Ry": R[1] if R else None})
    return out


def curve_fingerprint(ctx: CurveContext) -> dict:
    payload = {
        "p": ctx.E.p, "a": ctx.E.a, "b": ctx.E.b,
        "P": list(ctx.inst.P), "Q": list(ctx.inst.Q),
        "N": ctx.N, "field_bits": ctx.spec["field_bits"], "seed": ctx.spec["seed"],
        "factor_base": ctx.V,
    }
    return {"sha256": sha256_of(payload), "B": ctx.B, "N": ctx.N,
            "p": ctx.E.p, "a": ctx.E.a, "b": ctx.E.b}
