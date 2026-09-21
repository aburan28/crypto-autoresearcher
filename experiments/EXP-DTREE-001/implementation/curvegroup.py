"""Exact, solver-independent decomposition testing via elliptic-curve group
law (not Semaev/Groebner).

Why this module exists (recorded here, restated in implementation.md):
EXP-DTREE-001's specification names sympy Buchberger (harness/semaev.py-style
S3/S4 systems) as the solver whose *wall-clock cost* is C_solve(k) -- that
measurement is in gb_isolated.py/semaev3.py. But the decomposition
*probability* P(m, B') is a logically separate quantity, and a calibration
(recorded in implementation.md) shows sympy's Buchberger routine on a
degree-B' indicator-polynomial system exceeds the 20s per-solve cap well
before B' reaches the values this experiment's grid can produce -- so gating
"does this target decompose" on whether Buchberger *finishes* would make P
degenerate (near-zero, dominated by censoring) rather than measuring the
actual combinatorial quantity HEUR-001 and the birthday model make
predictions about. This module measures P directly and exactly via the
curve's own group law, which is self-verifying (every witness it returns is
checked by the SAME independent-certificate machinery as everything else) and
decoupled from Buchberger's performance.

Complexity, stated plainly:
  - arity 2 (m'=2) existence test: O(B') per target, always.
  - arity 3 (m=3 or m'=3) existence test: needs a one-time O(B'^2) pairwise-
    sum index per (curve, base); after that, O(B') per target. The one-time
    build is gated by build_pairsum_index_or_skip's estimated-time check
    against MAX_PRECOMPUTE_SECONDS -- a cell whose estimate exceeds that is
    marked infeasible_within_budget rather than silently attempted or
    silently faked.
"""
from __future__ import annotations

import itertools
import time
from dataclasses import dataclass

from harness.toycurve import EllipticCurve, Point

# Calibrated once (implementation.md records the raw benchmark): a
# deliberately conservative point-addition throughput used only to DECIDE
# whether a pairsum precompute is worth attempting, never to fabricate a
# result. See implementation.md "Calibration" for the measured rate
# (~1.58M add/s on the execution host); this constant is set below that
# measurement to leave headroom.
CALIBRATED_ADD_RATE = 1_000_000.0  # additions/second, conservative
MAX_PRECOMPUTE_SECONDS = 300.0     # skip arity-3 exact testing above this


def signed_variants(E: EllipticCurve, v: int) -> list[Point]:
    """The 1 or 2 distinct points on E with x-coordinate v."""
    P = E.lift_x(v)
    if P is None:
        return []
    Pneg = E.negate(P)
    return [P] if P == Pneg else [P, Pneg]


# --------------------------------------------------------------------------
# Arity-2 (existence + witness), O(B') per target -- always feasible.
# --------------------------------------------------------------------------

def decompose_arity2(E: EllipticCurve, V: list[int], R: Point):
    """Does R = s1*P(v1) + s2*P(v2) for some distinct v1,v2 in V? O(|V|).

    rem = R - p1 satisfies p1 + rem == R by construction (not re-derived or
    re-verified below -- that would be redundant, since it is an algebraic
    identity of the subtraction just performed). rem is therefore itself a
    valid witness for v2 = x(rem) the instant x(rem) is confirmed to be a
    DISTINCT member of V.
    """
    Vset = set(V)
    for v1 in V:
        for p1 in signed_variants(E, v1):
            rem = E.add(R, E.negate(p1))          # rem = R - p1, so p1+rem=R
            if rem is None:
                continue          # rem = O means v2 would have to be O, not a factor-base element
            x2 = rem[0]
            if x2 in Vset and x2 != v1:
                return True, [p1, rem]
    return False, []


# --------------------------------------------------------------------------
# Arity-3 (existence + witness) via a one-time pairwise-sum index.
# --------------------------------------------------------------------------

def estimate_pairsum_seconds(base_size: int) -> float:
    pairs = base_size * (base_size - 1) / 2.0
    additions = pairs * 2.0  # x(P(v1)+P(v2)) and x(P(v1)-P(v2)) per pair
    return additions / CALIBRATED_ADD_RATE


MAX_WITNESSES_PER_KEY = 4  # bounded list per x-coordinate; see docstring below


@dataclass
class PairsumIndex:
    base_size: int
    build_seconds: float
    index: dict  # x-coordinate of a 2-sum -> list[(v_a, v_b)] (up to MAX_WITNESSES_PER_KEY)


def build_pairsum_index_or_skip(E: EllipticCurve, V: list[int]) -> tuple[PairsumIndex | None, dict]:
    """Build the exact 2-sum x-coordinate index, unless the estimated build
    time exceeds MAX_PRECOMPUTE_SECONDS, in which case return (None, info)
    with info explaining why -- never a partially-built or fabricated index.

    Stores up to MAX_WITNESSES_PER_KEY distinct-pair witnesses per achieved
    x-coordinate (not just the first). A single-witness index would be wrong
    for existence testing: decompose_arity3 additionally requires the pair
    to avoid whatever v1 the outer loop is currently trying, and the first
    (v_a, v_b) pair stored for a given x-coordinate could coincide with that
    v1 even when a DIFFERENT valid pair for the same x-coordinate exists.
    """
    est = estimate_pairsum_seconds(len(V))
    info = {"base_size": len(V), "estimated_seconds": est,
            "threshold_seconds": MAX_PRECOMPUTE_SECONDS}
    if est > MAX_PRECOMPUTE_SECONDS:
        info["skipped"] = True
        info["reason"] = (f"estimated pairsum-index build time {est:.1f}s exceeds "
                           f"the {MAX_PRECOMPUTE_SECONDS:.0f}s feasibility threshold "
                           f"at |V|={len(V)}")
        return None, info
    t0 = time.perf_counter()
    idx: dict = {}
    n = len(V)
    for i in range(n):
        va = V[i]
        pa = E.lift_x(va)
        for j in range(i + 1, n):
            vb = V[j]
            pb = E.lift_x(vb)
            s_plus = E.add(pa, pb)
            s_minus = E.add(pa, E.negate(pb))
            for s in (s_plus, s_minus):
                if s is None:
                    continue
                x = s[0]
                bucket = idx.setdefault(x, [])
                if len(bucket) < MAX_WITNESSES_PER_KEY and (va, vb) not in bucket:
                    bucket.append((va, vb))
    build_seconds = time.perf_counter() - t0
    info["skipped"] = False
    info["actual_build_seconds"] = build_seconds
    return PairsumIndex(len(V), build_seconds, idx), info


def decompose_arity3(E: EllipticCurve, V: list[int], R: Point, pairsum: PairsumIndex):
    """Does R = s1*P(v1)+s2*P(v2)+s3*P(v3) for distinct v1,v2,v3 in V?
    O(|V| * MAX_WITNESSES_PER_KEY) given a prebuilt PairsumIndex -- still
    O(|V|) since MAX_WITNESSES_PER_KEY is a fixed constant.
    """
    for v1 in V:
        for p1 in signed_variants(E, v1):
            rem = E.add(R, E.negate(p1))          # rem = p2 + p3 target, rem = R - p1
            if rem is None:
                continue
            for v2, v3 in pairsum.index.get(rem[0], ()):
                if v2 == v1 or v3 == v1:
                    continue  # need 3 DISTINCT base elements
                p2, p3 = E.lift_x(v2), E.lift_x(v3)
                for s2 in ((p2, E.negate(p2)) if p2 != E.negate(p2) else (p2,)):
                    for s3 in ((p3, E.negate(p3)) if p3 != E.negate(p3) else (p3,)):
                        if E.add(E.add(p1, s2), s3) == R:
                            return True, [p1, s2, s3]
    return False, []


# --------------------------------------------------------------------------
# Full-group exact enumeration (tiny 8-12 bit curves; the C1 slope claim).
# Zero sampling error: every element of the whole subgroup is examined by
# construction rather than by sampling.
# --------------------------------------------------------------------------

def enumerate_decomposable_arity3(E: EllipticCurve, V: list[int]) -> set:
    """Every group element reachable as a signed sum of 3 DISTINCT elements
    of V (C(|V|, 3) combinations x up to 8 sign choices). Returns the set of
    achieved points (None represents the identity O). Pure curve arithmetic,
    self-verifying by construction -- there is no separate "solver" whose
    output could be wrong independent of this computation.
    """
    achieved = set()
    for v1, v2, v3 in itertools.combinations(V, 3):
        for p1 in signed_variants(E, v1):
            for p2 in signed_variants(E, v2):
                s12 = E.add(p1, p2)
                for p3 in signed_variants(E, v3):
                    achieved.add(E.add(s12, p3))
    return achieved


def enumerate_decomposable_arity3_via_semaev(a: int, b: int, p: int, V: list[int],
                                              universe_x: list[int]) -> set:
    """INDEPENDENT audit code path for CTRL-ENUMERATION-AUDIT: instead of
    constructing sums via curve addition (enumerate_decomposable_arity3),
    test each universe element algebraically via the Semaev S4 identity
    S4(v1, v2, v3, x_T) = 0, which holds iff SOME sign choice of the four
    points sums to O -- i.e. iff x_T is reachable as a signed 3-sum of V.
    Different mathematics (a resultant-derived symmetric-function identity)
    and different control flow (target-first, not sum-first) from
    enumerate_decomposable_arity3, so a bug in one is unlikely to reproduce
    identically in the other.

    Returns the set of universe X-COORDINATES confirmed reachable (not
    points -- S4 cannot distinguish R from -R by construction, which is
    mathematically consistent: Section "Audit parity" in implementation.md
    shows decomposability is invariant under negation, so the point-set and
    x-coordinate-set counts have an exact, checked 2-to-1 relationship
    away from the identity).
    """
    import sympy
    from semaev_fix import s4_expr_fixed  # harness.semaev.s4_expr has a confirmed
                                           # variable-collision bug -- see semaev_fix.py

    x1, x2, x3, x4 = sympy.symbols("x1 x2 x3 x4")
    S4 = s4_expr_fixed(a, b)
    f = sympy.lambdify((x1, x2, x3, x4), S4, modules="math")
    reachable_x = set()
    combos = list(itertools.combinations(V, 3))
    for xT in universe_x:
        for v1, v2, v3 in combos:
            val = f(v1, v2, v3, xT) % p
            if val == 0:
                reachable_x.add(xT)
                break
    return reachable_x
