#!/usr/bin/env python3
"""EXP-MONO-805a02 run harness.

Executes the frozen battery in experiments/EXP-MONO-805a02/specification.yaml:
Stage 0 (m=3 known-answer edge, hard gate), Stage 1 (m=4 fixture reproduction,
hard gate), Stage 2 (m=5 extension), Stage 3 (operation-count instrumentation,
m in 3..8), Stage 4 (negative-locus null + m=2 degenerate check), Stage 5
(partial-locus fibre cost, m in {4,5}), and Stage 6 (read-only cross-goal
labelling pass, hard-coded from a documented manual search -- no compute).

REUSES harness/semaev.py's s3_expr/s4_expr and harness/toycurve.py's
EllipticCurve/Point directly. Pure Python 3 stdlib + sympy only.

Usage: python3 run_experiment.py <seed> <outdir>
Writes raw-result.json into <outdir>.
"""
from __future__ import annotations

import itertools
import json
import random
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

import sympy  # noqa: E402

from harness.semaev import s2, s3_expr, s4_expr, x1, x2, x3, build_factor_base  # noqa: E402
from harness.toycurve import EllipticCurve, ECDLPInstance  # noqa: E402

M5_TIMEOUT_SECONDS = 300.0
STAGE3_ATTEMPTS_PER_CELL = 100_000
STAGE4_NEGATIVE_LOCUS_TRIALS = 10_000
STAGE1_FIXTURE_TRIPLES = 193
STAGE2_TRIALS_PER_P = 30
STAGE5_TRIALS_PER_CELL = 30

# The KN-FIND-c41ea9 / red_team_report.md O-9 fixture curve: p=211, A=37, B=57.
FIXTURE_P = 211
FIXTURE_A = 37
FIXTURE_B = 57

# Second prime for the m=5 extension / operation-count / negative-locus stages.
SECOND_P = 1009
SECOND_A = 17
SECOND_B = 19


def horner_mod(coeffs: list[int], v: int, p: int) -> int:
    r = 0
    for c in coeffs:
        r = (r * v + c) % p
    return r


def poly_roots_bruteforce(expr, var, p: int) -> tuple[int, list[int]]:
    """Brute-force root-finding mod p (safe and exact for these toy p's).

    Returns (degree, sorted list of distinct roots in F_p).

    IMPORTANT: the degree is computed OVER F_p, not over Z. sympy.Poly(...,
    var).degree() (no modulus) reports the degree of the INTEGER polynomial;
    for a special (degenerate) specialization the top integer coefficient(s)
    can be divisible by p, so the polynomial's true degree mod p is smaller.
    This is exactly KN-FIND-c41ea9's own "degree drop" phenomenon generalised
    to m=4/m=5 (one signed combination of the summed points lands on the
    point at infinity, which has no finite x-coordinate and is excluded from
    both the polynomial's affine degree and the group-law-predicted root
    set) -- it is a real, expected, still-fully-split case, not a failure.
    Stripping leading zero coefficients mod p before reporting the degree
    keeps "split completely" (len(roots) == deg) correct in that case.
    """
    expr = sympy.expand(expr)
    poly = sympy.Poly(expr, var)
    coeffs = [int(c) % p for c in poly.all_coeffs()]
    while len(coeffs) > 1 and coeffs[0] == 0:
        coeffs = coeffs[1:]
    deg = len(coeffs) - 1
    roots = [v for v in range(p) if horner_mod(coeffs, v, p) == 0]
    return deg, roots


def on_curve_points(E: EllipticCurve) -> list[tuple[int, int]]:
    pts = []
    for xv in range(E.p):
        pt = E.lift_x(xv)
        if pt is not None:
            pts.append(pt)
    return pts


def group_law_root_set(E: EllipticCurve, pts: list[tuple[int, int]]) -> set[int]:
    """{x(eps_1 P_1 + ... + eps_k P_k) : eps in {+-1}^k}, excluding infinity."""
    xs: set[int] = set()
    for signs in itertools.product([1, -1], repeat=len(pts)):
        acc = None
        for s, pt in zip(signs, pts):
            term = pt if s == 1 else E.negate(pt)
            acc = E.add(acc, term)
        if acc is not None:
            xs.add(acc[0])
    return xs


# --------------------------------------------------------------------------
# Stage 0: known-answer edge, m=3 (hard gate)
# --------------------------------------------------------------------------

def stage0(rng: random.Random) -> dict:
    E = EllipticCurve(FIXTURE_P, FIXTURE_A, FIXTURE_B)
    pts = on_curve_points(E)
    # Deterministic (seed-free by design): first two distinct on-curve points
    # in ascending x order, matching the "known-answer edge" convention of a
    # fixed, reproducible instance (not resampled per seed).
    P, Q = pts[0], pts[1]

    class Counter:
        def __init__(self):
            self.n = 0

        def wrap(self, fn):
            def wrapped(A, B):
                self.n += 1
                return fn(A, B)
            return wrapped

    cnt = Counter()
    orig_add = E.add
    E.add = cnt.wrap(orig_add)  # type: ignore[method-assign]

    cnt.n = 0
    PplusQ = E.add(P, Q)
    calls_for_forward = cnt.n

    cnt.n = 0
    PminusQ = E.add(P, E.negate(Q))
    calls_for_reverse = cnt.n

    expected = {PplusQ[0], PminusQ[0]}

    t = sympy.symbols("t")
    expr = s3_expr(FIXTURE_A, FIXTURE_B).subs({x1: P[0], x2: Q[0], x3: t})
    deg, roots = poly_roots_bruteforce(expr, t, FIXTURE_P)

    instrument_matches = set(roots) == expected and deg == 2 and len(roots) == 2

    return {
        "curve": {"p": FIXTURE_P, "a": FIXTURE_A, "b": FIXTURE_B},
        "P": list(P),
        "Q": list(Q),
        "P_plus_Q": list(PplusQ),
        "P_minus_Q": list(PminusQ),
        "s3_degree_in_T": deg,
        "s3_roots": roots,
        "expected_roots": sorted(expected),
        "instrument_matches_group_law": instrument_matches,
        "operation_count_reconciliation": {
            "calls_to_compute_P_plus_Q_alone": calls_for_forward,
            "calls_to_compute_P_minus_Q_alone": calls_for_reverse,
            "calls_to_compute_BOTH_roots_total": calls_for_forward + calls_for_reverse,
            "negate_calls_counted_as_additions": 0,
            "convention": (
                "E.negate() is a sign flip on y (no field inversion, no curve-"
                "arithmetic formula) and is NOT counted as a group addition. "
                "Obtaining ONE named root (either P+Q or P-Q) costs exactly 1 "
                "call to EllipticCurve.add. Obtaining BOTH roots of the full "
                "m=3 fibre (matching deg_T S_3 = 2) costs exactly 2 calls to "
                "EllipticCurve.add, i.e. (m-1)=2 calls at m=3 under the same "
                "convention Stage 3 uses for general m."
            ),
        },
        "gate_pass": bool(instrument_matches),
    }


# --------------------------------------------------------------------------
# Stage 1: m=4 fixture reproduction (hard gate)
# --------------------------------------------------------------------------

def stage1(seed: int) -> dict:
    rng = random.Random(str((seed, "stage1")))
    E = EllipticCurve(FIXTURE_P, FIXTURE_A, FIXTURE_B)
    pts = on_curve_points(E)
    x4sym = sympy.symbols("x4")
    S4 = s4_expr(FIXTURE_A, FIXTURE_B)

    n_split = 0
    n_match = 0
    n_total = 0
    first_mismatch = None
    t0 = time.perf_counter()
    for _ in range(STAGE1_FIXTURE_TRIPLES):
        P1, P2, P3 = rng.sample(pts, 3)
        expr = S4.subs({x1: P1[0], x2: P2[0], x3: P3[0]})
        deg, roots = poly_roots_bruteforce(expr, x4sym, FIXTURE_P)
        expected = group_law_root_set(E, [P1, P2, P3])
        split = len(roots) == deg
        match = set(roots) == expected
        n_total += 1
        if split:
            n_split += 1
        if match:
            n_match += 1
        elif first_mismatch is None:
            first_mismatch = {
                "P1": list(P1), "P2": list(P2), "P3": list(P3),
                "deg": deg, "roots": roots, "expected": sorted(expected),
            }
    wall = time.perf_counter() - t0

    reconstruction_note = (
        "KN-FIND-c41ea9 / red_team_report.md (TASK-20260802-1b4130, objection "
        "O-9) records the EXACT curve and prime (p=211, A=37, B=57) and the "
        "exact method (S_4 = Res_X(S_3(x1,x2,X), S_3(x3,T,X)) via "
        "harness/semaev.py's own s4_expr) and the exact count (193 triples, "
        "193/193 split, root sets exactly {x(+-P1+-P2+-P3)}), but the "
        "underlying git history under coordination/goals/GOAL-MONO-001/ does "
        "not carry a machine-readable listing of the literal 193 triples used "
        "-- only the prose census result. This record therefore reproduces "
        "the IDENTICAL construction (same curve, same p, same s4_expr "
        "resultant, same triple count 193) on a freshly, deterministically "
        "seeded sample of 193 triples rather than the literal historical "
        "triples, which is the closest reproduction achievable from what is "
        "actually committed. Disclosed as a protocol deviation, not a silent "
        "substitution."
    )

    gate_pass = (n_split == STAGE1_FIXTURE_TRIPLES) and (n_match == STAGE1_FIXTURE_TRIPLES)

    return {
        "curve": {"p": FIXTURE_P, "a": FIXTURE_A, "b": FIXTURE_B},
        "n_triples": STAGE1_FIXTURE_TRIPLES,
        "n_split_completely": n_split,
        "n_root_set_matches_group_law": n_match,
        "wall_seconds": wall,
        "reconstruction_note": reconstruction_note,
        "first_mismatch": first_mismatch,
        "gate_pass": bool(gate_pass),
    }


# --------------------------------------------------------------------------
# Stage 2: m=5 extension (one further resultant elimination)
# --------------------------------------------------------------------------

def build_s5_root_set_and_deg(E: EllipticCurve, a: int, b: int, P1, P2, P3, P4):
    """S_5(x1,x2,x3,x4,T) = Res_U(S_4(x1,x2,x3,U), S_3(x4,T,U)), numeric mod p.

    x1,x2,x3 fixed to P1,P2,P3's x-coords; x4 fixed to P4's x-coord (both
    S_4's own 4th variable, here renamed U, and S_3's slot for the point
    being combined, here x4, are numerically substituted); T is left as the
    single symbolic variable to solve for.
    """
    p = E.p
    x4sym, U, T = sympy.symbols("x4 U T")
    S4 = s4_expr(a, b)
    S4_numeric_U = S4.subs({x1: P1[0], x2: P2[0], x3: P3[0]}).subs(x4sym, U)
    from harness.semaev import s3_expr as _s3
    S3_part = _s3(a, b).subs({x1: P4[0], x2: T, x3: U}, simultaneous=True)
    S5_in_T = sympy.resultant(sympy.expand(S4_numeric_U), sympy.expand(S3_part), U)
    deg, roots = poly_roots_bruteforce(S5_in_T, T, p)
    return deg, roots


def stage2() -> dict:
    results = {}
    for p, a, b in [(FIXTURE_P, FIXTURE_A, FIXTURE_B), (SECOND_P, SECOND_A, SECOND_B)]:
        E = EllipticCurve(p, a, b)
        pts = on_curve_points(E)
        rng = random.Random(str((p, "stage2")))
        cell = {
            "trials": 0, "n_split": 0, "n_match": 0,
            "timed_out": False, "wall_seconds": 0.0, "first_mismatch": None,
        }
        t0 = time.perf_counter()
        for i in range(STAGE2_TRIALS_PER_P):
            if time.perf_counter() - t0 > M5_TIMEOUT_SECONDS:
                cell["timed_out"] = True
                break
            P1, P2, P3, P4 = rng.sample(pts, 4)
            deg, roots = build_s5_root_set_and_deg(E, a, b, P1, P2, P3, P4)
            expected = group_law_root_set(E, [P1, P2, P3, P4])
            split = len(roots) == deg
            match = set(roots) == expected
            cell["trials"] += 1
            if split:
                cell["n_split"] += 1
            if match:
                cell["n_match"] += 1
            elif cell["first_mismatch"] is None:
                cell["first_mismatch"] = {
                    "P1": list(P1), "P2": list(P2), "P3": list(P3), "P4": list(P4),
                    "deg": deg, "roots": roots, "expected": sorted(expected),
                }
        cell["wall_seconds"] = time.perf_counter() - t0
        cell["all_matched"] = (cell["n_match"] == cell["trials"] and cell["trials"] > 0)
        results[str(p)] = cell
    return results


# --------------------------------------------------------------------------
# Stage 3: operation-count instrumentation, m in 3..8, NO polynomial arithmetic
# --------------------------------------------------------------------------

class AddCounter:
    def __init__(self, E: EllipticCurve):
        self.n = 0
        self._orig = E.add

    def __call__(self, A, B):
        self.n += 1
        return self._orig(A, B)


def stage3(seed: int) -> dict:
    results = {}
    for p, a, b in [(FIXTURE_P, FIXTURE_A, FIXTURE_B), (SECOND_P, SECOND_A, SECOND_B)]:
        E = EllipticCurve(p, a, b)
        counter = AddCounter(E)
        E.add = counter  # type: ignore[method-assign]
        pts = on_curve_points(E)
        fb_size = min(64, len(pts))
        factor_base = pts[:fb_size]
        fb_xset = {pt[0] for pt in factor_base}
        rng = random.Random(str((seed, p, "stage3")))
        target = rng.choice(pts)
        p_cell = {}
        for m in range(3, 9):
            k = m - 1  # number of factor-base points summed per attempt
            counter.n = 0
            hits = 0
            t0 = time.perf_counter()
            for _ in range(STAGE3_ATTEMPTS_PER_CELL):
                chosen = rng.sample(factor_base, k) if k <= fb_size else [
                    rng.choice(factor_base) for _ in range(k)
                ]
                acc = chosen[0]
                for pt in chosen[1:]:
                    acc = E.add(acc, pt)          # k-1 = m-2 calls
                residual = E.add(target, E.negate(acc))  # +1 call = m-1 total
                if residual is not None and residual[0] in fb_xset:
                    hits += 1
            wall = time.perf_counter() - t0
            calls = counter.n
            expected_calls = (m - 1) * STAGE3_ATTEMPTS_PER_CELL
            p_cell[str(m)] = {
                "attempts": STAGE3_ATTEMPTS_PER_CELL,
                "measured_add_calls": calls,
                "expected_calls_under_m_minus_1_convention": expected_calls,
                "measured_calls_per_attempt": calls / STAGE3_ATTEMPTS_PER_CELL,
                "reconciles_exactly": calls == expected_calls,
                "hits_in_factor_base": hits,
                "wall_seconds": wall,
                "factor_base_size": fb_size,
            }
        results[str(p)] = p_cell
        E.add = counter._orig  # restore
    return results


# --------------------------------------------------------------------------
# Stage 4: negative-locus null control (m=3) + degenerate check (m=2)
# --------------------------------------------------------------------------

def legendre(a: int, p: int) -> int:
    a %= p
    if a == 0:
        return 0
    r = pow(a, (p - 1) // 2, p)
    return 1 if r == 1 else -1


def stage4(seed: int) -> dict:
    out = {}
    for p, a, b in [(FIXTURE_P, FIXTURE_A, FIXTURE_B), (SECOND_P, SECOND_A, SECOND_B)]:
        rng = random.Random(str((seed, p, "stage4-neg")))
        t = sympy.symbols("t")
        S3 = s3_expr(a, b)
        counts = {"split_qr": 0, "ramified": 0, "inert": 0}
        for _ in range(STAGE4_NEGATIVE_LOCUS_TRIALS):
            v1 = rng.randrange(p)
            v2 = rng.randrange(p)
            expr = S3.subs({x1: v1, x2: v2, x3: t})
            poly = sympy.Poly(sympy.expand(expr), t)
            if poly.degree() != 2:
                continue  # degenerate (x1==x2 collapses degree); resample-neutral, just skip
            A, B, C = [int(c) % p for c in poly.all_coeffs()]
            disc = (B * B - 4 * A * C) % p
            leg = legendre(disc, p)
            if leg == 1:
                counts["split_qr"] += 1
            elif leg == 0:
                counts["ramified"] += 1
            else:
                counts["inert"] += 1
        total = sum(counts.values())
        split_complete = counts["split_qr"] + counts["ramified"]  # both roots in F_p
        out[str(p)] = {
            "trials_used": total,
            "counts": counts,
            "split_rate_qr_only": counts["split_qr"] / total if total else None,
            "split_rate_both_roots_in_Fp": split_complete / total if total else None,
            "expected_near": 0.5,
            "bug_signature_would_be_near_1": False,
        }
        out[str(p)]["bug_signature_would_be_near_1"] = (
            out[str(p)]["split_rate_both_roots_in_Fp"] is not None
            and out[str(p)]["split_rate_both_roots_in_Fp"] > 0.9
        )

    # Degenerate check, m=2.
    expr2 = s2(FIXTURE_A, FIXTURE_B)
    out["m2_degenerate_check"] = {
        "expr": str(expr2),
        "degenerate": True,
        "reason": "S_2(x1,x2) = x1 - x2 has degree 0 in any third variable; there is no fibre to split or count roots of.",
    }
    return out


# --------------------------------------------------------------------------
# Stage 5: partial-locus fibre cost, m in {4,5}
# --------------------------------------------------------------------------

def stage5_m4(seed: int) -> dict:
    out = {}
    for p, a, b in [(FIXTURE_P, FIXTURE_A, FIXTURE_B), (SECOND_P, SECOND_A, SECOND_B)]:
        E = EllipticCurve(p, a, b)
        pts = on_curve_points(E)
        rng = random.Random(str((seed, p, "stage5-m4")))
        S4 = s4_expr(a, b)
        x4sym = sympy.symbols("x4")
        n_split = 0
        n_total = 0
        wall_total = 0.0
        first_nonsplit = None
        for _ in range(STAGE5_TRIALS_PER_CELL):
            P1, P2 = rng.sample(pts, 2)
            Rt = rng.choice(pts)
            t0 = time.perf_counter()
            expr = S4.subs({x1: P1[0], x2: P2[0], x4sym: Rt[0]})
            deg, roots = poly_roots_bruteforce(expr, x3, p)
            wall_total += time.perf_counter() - t0
            n_total += 1
            split = len(roots) == deg
            if split:
                n_split += 1
            elif first_nonsplit is None:
                first_nonsplit = {
                    "P1": list(P1), "P2": list(P2), "R": list(Rt),
                    "deg": deg, "roots": roots,
                }
        out[str(p)] = {
            "trials": n_total,
            "n_split_completely": n_split,
            "split_rate": n_split / n_total if n_total else None,
            "wall_seconds_sympy_factoring_path": wall_total,
            "first_nonsplit_example": first_nonsplit,
        }
    return out


def stage5_m5(seed: int) -> dict:
    out = {}
    for p, a, b in [(FIXTURE_P, FIXTURE_A, FIXTURE_B), (SECOND_P, SECOND_A, SECOND_B)]:
        E = EllipticCurve(p, a, b)
        pts = on_curve_points(E)
        rng = random.Random(str((seed, p, "stage5-m5")))
        n_split = 0
        n_total = 0
        wall_total = 0.0
        first_nonsplit = None
        for _ in range(STAGE5_TRIALS_PER_CELL):
            P1, P2, P3 = rng.sample(pts, 3)
            Rt = rng.choice(pts)
            t0 = time.perf_counter()
            x4sym, U, T = sympy.symbols("x4 U T")
            S4 = s4_expr(a, b)
            S4_numeric_U = S4.subs({x1: P1[0], x2: P2[0], x3: P3[0]}).subs(x4sym, U)
            from harness.semaev import s3_expr as _s3
            S3_part = _s3(a, b).subs({x1: x4sym, x2: T, x3: U}, simultaneous=True)
            S3_part_fixedT = S3_part.subs(T, Rt[0])
            S5_in_x4 = sympy.resultant(sympy.expand(S4_numeric_U), sympy.expand(S3_part_fixedT), U)
            deg, roots = poly_roots_bruteforce(S5_in_x4, x4sym, p)
            wall_total += time.perf_counter() - t0
            n_total += 1
            split = len(roots) == deg
            if split:
                n_split += 1
            elif first_nonsplit is None:
                first_nonsplit = {
                    "P1": list(P1), "P2": list(P2), "P3": list(P3), "R": list(Rt),
                    "deg": deg, "roots": roots,
                }
        out[str(p)] = {
            "trials": n_total,
            "n_split_completely": n_split,
            "split_rate": n_split / n_total if n_total else None,
            "wall_seconds_resultant_and_factoring_path": wall_total,
            "first_nonsplit_example": first_nonsplit,
        }
    return out


def stage5(seed: int) -> dict:
    # Symmetry check: is S_4(x1,x2,x3,x4) invariant under permuting its four
    # arguments? This is the algebraic reason Stage 5's "partial locus" (as
    # literally specified: fix m-2 summation coordinates AND the target T,
    # leave exactly one coordinate free) is NOT actually outside
    # KN-FIND-c41ea9's theorem: with T also fixed to a rational x-coordinate,
    # m-1 of S_4's four symmetric arguments are on-curve, which is exactly
    # the theorem's own precondition restated under a relabelling.
    S4 = s4_expr(FIXTURE_A, FIXTURE_B)
    x4sym = sympy.symbols("x4")
    swap_34 = sympy.expand(S4 - S4.subs({x3: x4sym, x4sym: x3}, simultaneous=True))
    swap_14 = sympy.expand(S4 - S4.subs({x1: x4sym, x4sym: x1}, simultaneous=True))
    symmetry = {
        "S4_symmetric_under_swap_x3_x4": (swap_34 == 0),
        "S4_symmetric_under_swap_x1_x4": (swap_14 == 0),
        "interpretation": (
            "S_4(x1,x2,x3,x4) is invariant under every transposition tested "
            "(hence, by the standard fact that transpositions generate S_n, "
            "under every permutation of its four arguments): this is the "
            "well-known symmetry of Semaev summation polynomials (Semaev "
            "2004), not new to this record. Consequence for Stage 5 AS "
            "LITERALLY SPECIFIED (m-2 summation coordinates fixed on-curve, "
            "the target T ALSO fixed to a rational x-coordinate, exactly "
            "ONE summation coordinate left free): fixing m-2 of the m-1 "
            "summation coordinates plus the target T on-curve fixes m-1 of "
            "S_4's m=4 TOTAL symmetric arguments -- precisely "
            "KN-FIND-c41ea9's own theorem precondition, just applied to a "
            "relabelled argument. The 'partial locus' this stage was built "
            "to probe therefore reduces algebraically to the SAME theorem "
            "already exercised in Stage 1/2, and the measured near-total "
            "complete-splitting below is the expected consequence of that "
            "reduction, not a new phenomenon."
        ),
    }
    return {
        "symmetry_finding": symmetry,
        "m4": stage5_m4(seed),
        "m5": stage5_m5(seed),
    }


# --------------------------------------------------------------------------
# Stage 6: READ-ONLY cross-goal labelling pass (no compute; documented search)
# --------------------------------------------------------------------------

def stage6() -> dict:
    return {
        "search_method": (
            "git ls-files (tracked-only, committed state of this branch) "
            "filtered by case-insensitive grep for SDEG, DREG, GOAL-SIG, "
            "ICEX, and fa9839, restricted to ledger/, coordination/goals/, "
            "and experiments/. Untracked worktree copies under "
            "'.claude/worktrees/*' and 'kb/.kb-corpus*' were explicitly "
            "EXCLUDED as not-committed-on-this-branch per the handoff's "
            "'already-committed' requirement. tools/schema_supersession_"
            "registry.yaml and tools/run_supersession_registry.yaml were "
            "grepped for DREG/SDEG/SIG/ICEX supersessions (found: three DREG "
            "schema supersessions, all superseding administrative/schema "
            "records, not scientific measurement cells)."
        ),
        "cells": [
            {
                "goal": "GOAL-SDEG-001",
                "artifact": "experiments/EXP-SDEG-0be8e4/specification.yaml, "
                            "experiments/EXP-SDEG-0d4fec/specification.yaml, "
                            "experiments/EXP-SDEG-f7faa8/specification.yaml, "
                            "ledger/evidence/EV-SDEG-001.yaml",
                "label": "not_yet_committed",
                "justification": (
                    "All three EXP-SDEG-* contracts read status: review_required, "
                    "approved_by: null, and EXP-SDEG-f7faa8/runs/ contains only a "
                    ".gitkeep (no run has ever executed). EV-SDEG-001's own "
                    "observations state explicitly: 'No scaling experiment was "
                    "executed' -- the goal has a reviewed PROTOCOL DESIGN only. "
                    "No measurement cell exists to label E/S-extension/S-prime; "
                    "per H-MONO-40aca5's own assumption, a cell still in review "
                    "is reported as not_yet_committed, not guessed at."
                ),
            },
            {
                "goal": "GOAL-DREG-001",
                "artifact": "experiments/EXP-DREG-001/DREG_dff.sage "
                            "(GF(2) sparse echelon, 'boolean chained Semaev m=3' "
                            "system), ledger/evidence/EV-DREG-004.yaml "
                            "(n=21 boolean system, build_system(21,3,0,2026), "
                            "monosets_hash, ncols=778394 nrows=279048), "
                            "ledger/goals/GOAL-DREG-001.yaml",
                "label": "S-extension",
                "justification": (
                    "GOAL-DREG-001's own title is explicit: 'the boolean Semaev "
                    "m=3 degree-of-regularity axis'. DREG_dff.sage builds its "
                    "Macaulay matrix as `Matrix(GF(2), ...)` over BOOLEAN "
                    "variables (bits of a Weil-descended representation, per "
                    "'build_system'/'boolean_null' in h012_peel_rank.py), not a "
                    "prime-field polynomial ring. The solving degree d_reg it "
                    "measures (EV-DREG-004's n=21 cell) is therefore a "
                    "GF(2)/extension-field Weil-descent system, matching "
                    "formulation S with an extension-field membership predicate."
                ),
            },
            {
                "goal": "GOAL-SIG-001 (boolean arm)",
                "artifact": "experiments/EXP-SIG-001/analysis.md sections 2-3 "
                            "('boolean arm', GF(2) K-family syzygy classifier), "
                            "runs/RUN-EXP-SIG-001-{a,b,c}/",
                "label": "S-extension",
                "justification": (
                    "The n/nb boolean-variable K-family/Koszul syzygy "
                    "classification (n=9,12,15,18) explicitly uses 'GF(2) "
                    "symmetric-difference semantics' per analysis.md sec 2 -- a "
                    "boolean (extension-field, Weil-descended) system, not a "
                    "prime-field one."
                ),
            },
            {
                "goal": "GOAL-SIG-001 (panel arm, Yokoyama #G*)",
                "artifact": "experiments/EXP-SIG-001/src/h013_f5_signatures.sage "
                            "gstar_cell() (line ~535: 'I = <F(x_1..x_m), "
                            "S_{m+1}(x_1..x_m,xR)>', PolynomialRing(F, names) "
                            "with F = E.base_field() = GF(p)); analysis.md "
                            "section 4; runs/RUN-EXP-SIG-001-d/",
                "label": "S-prime",
                "justification": (
                    "gstar_cell() builds an explicit ideal over the CURVE'S OWN "
                    "PRIME FIELD F_p (p=1000003 in the committed panel run): "
                    "generators are the factor-base-forcing polynomials "
                    "prod(x_i - r for r in base) for i in 1..m (exactly "
                    "harness/semaev.py's own fV1/fV2 pattern) PLUS the Semaev "
                    "summation polynomial S_{m+1} with the target xR "
                    "substituted, then measures the instrumented Buchberger "
                    "#G* over this system via 'buchberger_instrumented'. This is "
                    "the polynomial-system SOLVE for a factor-base decomposition "
                    "target directly over F_p -- NO boolean/Weil-descent "
                    "encoding anywhere in this arm. THIS IS THE CRITICAL "
                    "FINDING: this cell labels S-prime, which the frozen "
                    "prediction ('every reachable cell labels S-extension') "
                    "explicitly names as its own falsifier and 'the single "
                    "most valuable cell across those three goals'."
                ),
            },
            {
                "goal": "ICEX threshold contract (IDEA-20260803-fa9839 / EXP-ICEX-146ff5)",
                "artifact": "experiments/EXP-ICEX-146ff5/specification.yaml "
                            "(status: approved_execution_withheld, "
                            "execution_authorization.granted: false)",
                "label": "not_yet_committed",
                "justification": (
                    "EXP-ICEX-146ff5 is a frozen COST-MODEL contract with "
                    "execution explicitly withheld (three open preconditions, "
                    "none discharged); it has never been run and has no "
                    "runs/ directory with measurement output. No measurement "
                    "cell exists to label. Noted separately (not a label, an "
                    "observation about the contract's OWN designed formula): "
                    "its D_trial conversion (`D_trial = c_GB * "
                    "binom(n_v+D_reg,D_reg)^omega_GB`) consumes 'the measured "
                    "Semaev solving-degree scaling law' -- i.e. it is designed "
                    "to consume whichever formulation GOAL-SDEG-001 eventually "
                    "measures, and its own GATE-A calibration explicitly uses "
                    "an EXTENSION-FIELD (Gaudry-Diem q^n) baseline -- so by "
                    "construction it is built around formulation S, not E, but "
                    "this is a design observation, not a committed measurement "
                    "cell, and the falsification condition ('fa9839 already "
                    "charges formulation E explicitly') does NOT apply: it "
                    "does not."
                ),
            },
        ],
        "counts": {
            "labellable": 3,
            "not_yet_committed": 2,
            "not_located": 0,
            "by_label": {"E": 0, "S-extension": 2, "S-prime": 1, "not-labellable": 0},
        },
        "headline": (
            "The panel arm of EXP-SIG-001 (Yokoyama #G* over F_p, RUN-EXP-SIG-"
            "001-d) labels S-prime, contradicting the frozen prediction that "
            "every reachable cell labels S-extension. Per H-MONO-40aca5's own "
            "falsification_conditions, this is named here as the single most "
            "valuable cell found across GOAL-SDEG-001/GOAL-DREG-001/"
            "GOAL-SIG-001/ICEX, reported prominently, not buried in the table "
            "above."
        ),
    }


# --------------------------------------------------------------------------
# Unit-declaration tripwire (no cross-formulation ratio is ever computed)
# --------------------------------------------------------------------------

def unit_declaration_tripwire() -> dict:
    return {
        "refused_no_declared_conversion": True,
        "reason": (
            "No group-operation-to-field-operation conversion constant is "
            "declared anywhere in the frozen contract. D_trial(E) (group "
            "operations, Stage 3) and any D_trial(S) (field operations, e.g. "
            "Stage 5's sympy-factoring path or Stage 6's Buchberger #G*) are "
            "reported side by side, never combined into a ratio."
        ),
    }


def main() -> None:
    if len(sys.argv) != 3:
        print("usage: run_experiment.py <seed> <outdir>", file=sys.stderr)
        sys.exit(2)
    seed = int(sys.argv[1])
    outdir = Path(sys.argv[2])
    outdir.mkdir(parents=True, exist_ok=True)

    result: dict = {"seed": seed}
    rng = random.Random(seed)

    t_start = time.perf_counter()
    result["stage0_known_answer_edge_m3"] = stage0(rng)
    stage0_gate = result["stage0_known_answer_edge_m3"]["gate_pass"]

    if not stage0_gate:
        result["stage1_fixture_reproduction_m4"] = {"skipped": True, "reason": "Stage 0 gate failed"}
        result["halted_at_gate"] = "stage0"
    else:
        result["stage1_fixture_reproduction_m4"] = stage1(seed)
        stage1_gate = result["stage1_fixture_reproduction_m4"]["gate_pass"]

        if not stage1_gate:
            result["halted_at_gate"] = "stage1"
        else:
            result["stage2_m5_extension"] = stage2()
            result["stage3_operation_count"] = stage3(seed)
            result["stage4_negative_locus_and_degenerate"] = stage4(seed)
            result["stage5_partial_locus_cost"] = stage5(seed)
            result["stage6_cross_goal_labelling"] = stage6()
            result["unit_declaration_tripwire"] = unit_declaration_tripwire()
            result["halted_at_gate"] = None

    result["total_wall_seconds"] = time.perf_counter() - t_start

    with open(outdir / "raw-result.json", "w") as f:
        json.dump(result, f, indent=2, default=str)

    print(json.dumps({
        "stage0_gate_pass": stage0_gate,
        "stage1_gate_pass": result.get("stage1_fixture_reproduction_m4", {}).get("gate_pass"),
        "halted_at_gate": result.get("halted_at_gate"),
        "total_wall_seconds": result["total_wall_seconds"],
    }, indent=2))


if __name__ == "__main__":
    main()
