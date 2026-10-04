#!/usr/bin/env python3
"""EXP-MONO-7c653b run harness.

Machine-checks H-MONO-10ca08's Part B / HEUR-PARITY-3 hand derivation: on the
j=m-1 (all-non-residue) Semaev summation locus, the signed-sum point Q can be
computed via ordinary F_p group arithmetic on the quadratic twist E_delta,
reproducing the direct polynomial-root x(Q) exactly (Stage 3), while a
deliberately WRONG final rescaling constant fails to do so (Stage 4a). Stage 1
is a hard gate reproducing the m=4/p=211/j=0 fixture via `harness/semaev.py`'s
own `s4_expr`.

REUSES `harness/semaev.py`'s `s3_expr`/`s4_expr` and `harness/toycurve.py`'s
`EllipticCurve`/`_sqrt_mod` directly (imported, never reimplemented). A new
`s5_expr` function is defined LOCALLY in this file (see implementation.md for
the disclosed reasoning: the task instructions for this run restrict writes
to experiments/EXP-MONO-7c653b/, so extending the shared harness/semaev.py --
a file outside that scope -- was not viable for this run, not a stylistic
preference). It follows the identical resultant-elimination pattern
`s4_expr` already uses (S_5 = Res_U(S_4(x1,x2,x3,U), S_3(x4,T,U))), evaluated
NUMERICALLY (coordinates substituted before the resultant is taken), per
EXP-MONO-805a02's own Stage-2 precedent for tractability.

No modification to `EllipticCurve` is made or needed: E_delta is constructed
directly as `EllipticCurve(p, a*delta*delta % p, b*delta**3 % p)`.

Pure Python 3 stdlib + sympy only (matching the frozen contract's dependency
constraint).

Usage: python3 run_experiment.py <seed> <outdir>
Writes raw-result.json into <outdir>.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import signal
import sys
import time
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

import sympy  # noqa: E402

from harness.semaev import s3_expr, s4_expr, x1, x2, x3  # noqa: E402
from harness.toycurve import EllipticCurve, _sqrt_mod  # noqa: E402

DOMAIN_BASE = "EXP-MONO-7c653b/v1"

CURVES = {
    "p211": {"p": 211, "a": 37, "b": 57},
    "p1009": {"p": 1009, "a": 17, "b": 19},
}

STAGE1_FIXTURE_TRIPLES = 193
STAGE1_P = 211
STAGE1_A = 37
STAGE1_B = 57
STAGE1_M = 4

STAGE3_N_PER_CELL = {4: 500, 5: 200}
STAGE3_M_VALUES = [4, 5]

STAGE4A_M = 4
STAGE4A_P = 211
STAGE4A_A = 37
STAGE4A_B = 57
STAGE4A_N = 50

S5_TIMEOUT_SECONDS = 300


# --------------------------------------------------------------------------
# Deterministic seed-derivation rule (per contract `inputs.seed_derivation_rule`,
# identical formula to EXP-MONO-12ce1c's own rule). DISCLOSED PROTOCOL
# RESOLUTION: the contract's formula (domain|label|p|m|counter) does not
# itself include master_seed as a hash component, yet the same clause
# requires third-party reproduction "from (master_seed, domain, label, p, m,
# counter)". EXP-MONO-805a02 resolved the identical tension in its own
# domain string by folding the run's master_seed into a per-run domain
# suffix ("EXP-MONO-805a02/v1/run-20260830"); this run follows that same
# precedent: domain = f"{DOMAIN_BASE}/run-{seed}". This is what makes the
# two replication runs (seeds 20260905, 20260906) draw genuinely different
# samples, per this contract's own `replication.independent_instances: 2`.
# --------------------------------------------------------------------------

class SeedStream:
    """Deterministic SHA-256 draw stream with rejection sampling against
    modulo bias, per the frozen contract's own `seed_derivation_rule`.

    digest = SHA256(domain + "|" + label + "|" + decimal(p) + "|" +
                     decimal(m) + "|" + decimal(counter))
    Counter starts at 0 and advances once per digest CONSUMED (i.e. once per
    attempt, whether accepted or rejected), per label, per (p, m) cell.
    """

    def __init__(self, domain: str, label: str, p: int, m: int):
        self.domain = domain
        self.label = label
        self.p = p
        self.m = m
        self.counter = 0

    def next_int(self, modulus: int) -> int:
        if modulus <= 0:
            raise ValueError("modulus must be positive")
        limit = (2 ** 256 // modulus) * modulus
        while True:
            msg = f"{self.domain}|{self.label}|{self.p}|{self.m}|{self.counter}"
            digest = hashlib.sha256(msg.encode()).hexdigest()
            h = int(digest, 16)
            self.counter += 1
            if h < limit:
                return h % modulus


def draw_distinct(stream: SeedStream, base_list: list, k: int) -> list:
    """Draw k DISTINCT elements from base_list via sequential sampling
    without replacement (Fisher-Yates-style pop), fully determined by the
    stream's (domain, label, p, m, counter) state."""
    pool = list(base_list)
    chosen = []
    for _ in range(k):
        idx = stream.next_int(len(pool))
        chosen.append(pool.pop(idx))
    return chosen


# --------------------------------------------------------------------------
# Factor-base construction (deterministic, no randomness: sequential scan)
# --------------------------------------------------------------------------

def f_val(a: int, b: int, xv: int, p: int) -> int:
    return (xv * xv * xv + a * xv + b) % p


def on_curve_factor_base(p: int, a: int, b: int) -> list[int]:
    """x-coordinates with f(x) a nonzero QUADRATIC RESIDUE mod p (on-curve,
    non-ramified). Deterministic ascending-x scan, analogous in construction
    to `non_residue_and_delta_construction`'s twisted-factor-base scan, but
    selecting residues instead of non-residues, per this record's own
    Stage-1 fixture requirement ("drawn from the on-curve factor base")."""
    xs = []
    for xv in range(p):
        fv = f_val(a, b, xv, p)
        if fv != 0 and pow(fv, (p - 1) // 2, p) == 1:
            xs.append(xv)
    return xs


def twisted_factor_base(p: int, a: int, b: int) -> dict:
    """Per contract `inputs.non_residue_and_delta_construction`: ascending-x
    scan for f(x) a STRICT Euler-criterion non-residue (never 0). The first
    accepted x is DELTA_SOURCE; delta = f(DELTA_SOURCE) mod p. The full
    ordered list of all such x's is the twisted factor base."""
    xs = []
    for xv in range(p):
        fv = f_val(a, b, xv, p)
        if fv != 0 and pow(fv, (p - 1) // 2, p) == p - 1:
            xs.append(xv)
    if not xs:
        raise RuntimeError(f"no non-residue x found for p={p} (unexpected)")
    delta_source = xs[0]
    delta = f_val(a, b, delta_source, p)
    digest_input = "\n".join(str(v) for v in xs).encode()
    digest = hashlib.sha256(digest_input).hexdigest()
    return {
        "xs": xs,
        "delta_source": delta_source,
        "delta": delta,
        "size": len(xs),
        "sha256_digest": digest,
    }


# --------------------------------------------------------------------------
# s5_expr: one further resultant elimination, IDENTICAL pattern to s4_expr,
# evaluated NUMERICALLY (coordinates substituted before the resultant).
# S_5 = Res_U(S_4(x1,x2,x3,U), S_3(x4,T,U))
# --------------------------------------------------------------------------

_x4sym, _U, _T = sympy.symbols("x4 U T")


def s5_expr(a: int, b: int, v1: int, v2: int, v3: int, v4: int):
    """S_5(v1, v2, v3, v4, T) via one further resultant elimination in the
    identical pattern s4_expr already uses, evaluated numerically (v1..v4
    substituted before the resultant is taken)."""
    S4 = s4_expr(a, b)                       # symbolic in x1, x2, x3, x4
    S4_numeric_U = S4.subs({x1: v1, x2: v2, x3: v3}).subs(_x4sym, _U)
    S3_part = s3_expr(a, b).subs({x1: v4, x2: _T, x3: _U}, simultaneous=True)
    return sympy.resultant(sympy.expand(S4_numeric_U), sympy.expand(S3_part), _U)


class _S5Timeout(Exception):
    pass


def _s5_timeout_handler(signum, frame):
    raise _S5Timeout("s5_expr resultant elimination exceeded 300s")


def s5_expr_with_timeout(a: int, b: int, v1: int, v2: int, v3: int, v4: int,
                         timeout_seconds: int = S5_TIMEOUT_SECONDS):
    """s5_expr guarded by a hard SIGALRM timeout (Unix only), per the
    frozen contract's own stopping rule: 'If the s5_expr resultant
    elimination fails to terminate within 300 seconds ... abort that cell
    as failed_infrastructure.'"""
    old_handler = signal.signal(signal.SIGALRM, _s5_timeout_handler)
    signal.alarm(timeout_seconds)
    try:
        return s5_expr(a, b, v1, v2, v3, v4)
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)


# --------------------------------------------------------------------------
# Polynomial split analysis: multiplicity-aware AND distinct, separately.
# --------------------------------------------------------------------------

def poly_split_analysis(expr, var, p: int) -> dict:
    """Factor expr mod p and report BOTH split_with_multiplicity and
    split_distinct SEPARATELY (never pooled), plus the distinct root set and
    the full factor-degree multiset."""
    expr = sympy.expand(expr)
    poly = sympy.Poly(expr, var, modulus=p)   # over GF(p): degree already
                                                # correctly reflects mod-p
                                                # reduction (no manual
                                                # degree-drop fix needed).
    deg = poly.degree()
    coeffs = [int(c) % p for c in poly.all_coeffs()]

    def horner(v: int) -> int:
        r = 0
        for c in coeffs:
            r = (r * v + c) % p
        return r

    distinct_roots = [v for v in range(p) if horner(v) == 0]

    _, factors = poly.factor_list()
    factor_degrees = []
    lin_mult_sum = 0
    for fac, mult in factors:
        d = fac.degree()
        factor_degrees.extend([d] * mult)
        if d == 1:
            lin_mult_sum += mult

    split_with_multiplicity = (deg > 0 and lin_mult_sum == deg)
    split_distinct = (deg > 0 and len(distinct_roots) == deg)

    return {
        "degree": deg,
        "distinct_roots": sorted(distinct_roots),
        "split_with_multiplicity": bool(split_with_multiplicity),
        "split_distinct": bool(split_distinct),
        "factor_degree_multiset": sorted(factor_degrees),
    }


# --------------------------------------------------------------------------
# Group-law helpers
# --------------------------------------------------------------------------

def group_law_root_set(E: EllipticCurve, pts: list) -> set:
    """{x(eps_1 P_1 + ... + eps_k P_k) : eps in {+-1}^k}, excluding infinity.
    ALL 2^k sign combinations (no global-sign reduction), matching
    KN-FIND-c41ea9's own fixture convention for Stage 1."""
    xs = set()
    for signs in itertools.product([1, -1], repeat=len(pts)):
        acc = None
        for s, pt in zip(signs, pts):
            term = pt if s == 1 else E.negate(pt)
            acc = E.add(acc, term)
        if acc is not None:
            xs.add(acc[0])
    return xs


class AddCounter:
    def __init__(self, E: EllipticCurve):
        self.n = 0
        self._orig = E.add

    def __call__(self, A, B):
        self.n += 1
        return self._orig(A, B)


def twist_route_xset(E_delta: EllipticCurve, delta: int, p: int,
                     points_delta: list, add_counter: AddCounter) -> set:
    """R = sum eps_i*(delta*x_i, delta^2*y_i') over E_delta, for every
    eps in {+1,-1}^{m-1} up to global sign (fix eps_0 = +1: 2^{m-2} distinct
    sign classes), x(Q) := X(R) * inverse(delta) mod p. Per attempt: acc
    starts at None (point at infinity) and every one of the m-1 signed terms
    is folded in via EllipticCurve.add -- exactly m-1 add() calls per
    attempt, reconciled against the contract's own declared operation count
    (m-1 additions + 1 multiplication)."""
    inv_delta = pow(delta, -1, p)
    k = len(points_delta)
    xs = set()
    for rest_signs in itertools.product([1, -1], repeat=k - 1):
        signs = (1,) + rest_signs
        acc = None
        for s, pt in zip(signs, points_delta):
            term = pt if s == 1 else E_delta.negate(pt)
            acc = add_counter(acc, term)
        if acc is not None:
            xQ = (acc[0] * inv_delta) % p
            xs.add(xQ)
    return xs


def mutant_twist_route_xset(E_delta: EllipticCurve, delta_prime: int, p: int,
                            points_delta: list, add_counter: AddCounter) -> set:
    """IDENTICAL construction to twist_route_xset (correct delta throughout
    the sum), except the FINAL rescaling uses delta' != delta instead of
    delta -- the Stage-4a wrong-rescaling-constant mutant."""
    inv_delta_prime = pow(delta_prime, -1, p)
    k = len(points_delta)
    xs = set()
    for rest_signs in itertools.product([1, -1], repeat=k - 1):
        signs = (1,) + rest_signs
        acc = None
        for s, pt in zip(signs, points_delta):
            term = pt if s == 1 else E_delta.negate(pt)
            acc = add_counter(acc, term)
        if acc is not None:
            xQ = (acc[0] * inv_delta_prime) % p
            xs.add(xQ)
    return xs


def build_points_delta(a: int, b: int, p: int, delta: int, xs: list) -> list:
    """For each x_i (a j=m-1 non-residue x-coordinate), y_i' in F_p with
    (y_i')^2 = f(x_i) * inverse(delta) mod p, then map to E_delta's
    coordinates (delta*x_i, delta^2*y_i')."""
    inv_delta = pow(delta, -1, p)
    pts = []
    for xv in xs:
        fv = f_val(a, b, xv, p)
        rhs = (fv * inv_delta) % p
        y_prime = _sqrt_mod(rhs, p)
        if y_prime is None:
            raise RuntimeError(
                f"f(x)*inverse(delta) mod p is not a QR for x={xv}, p={p} "
                f"(should be impossible on the j=m-1 locus with a "
                f"non-residue delta: product of two non-residues is a "
                f"residue)"
            )
        pts.append(((delta * xv) % p, (delta * delta * y_prime) % p))
    return pts


# --------------------------------------------------------------------------
# Stage 1: hard gate, m=4/p=211/j=0 fixture reproduction
# --------------------------------------------------------------------------

def stage1(domain: str) -> dict:
    p, a, b = STAGE1_P, STAGE1_A, STAGE1_B
    E = EllipticCurve(p, a, b)
    fb = on_curve_factor_base(p, a, b)
    stream = SeedStream(domain, "fixture-triple", p, STAGE1_M)

    x4sym = sympy.symbols("x4")
    S4 = s4_expr(a, b)

    n_split_mult = 0
    n_split_distinct = 0
    n_match = 0
    first_mismatch = None
    t0 = time.perf_counter()
    triples_used = []
    for _ in range(STAGE1_FIXTURE_TRIPLES):
        triple_x = draw_distinct(stream, fb, 3)
        triples_used.append(triple_x)
        pts = [E.lift_x(xv) for xv in triple_x]
        expr = S4.subs({x1: triple_x[0], x2: triple_x[1], x3: triple_x[2]})
        analysis = poly_split_analysis(expr, x4sym, p)
        expected = group_law_root_set(E, pts)
        match = set(analysis["distinct_roots"]) == expected
        if analysis["split_with_multiplicity"]:
            n_split_mult += 1
        if analysis["split_distinct"]:
            n_split_distinct += 1
        if match:
            n_match += 1
        elif first_mismatch is None:
            first_mismatch = {
                "triple_x": triple_x,
                "analysis": analysis,
                "expected": sorted(expected),
            }
    wall = time.perf_counter() - t0

    gate_pass = (n_split_mult == STAGE1_FIXTURE_TRIPLES
                 and n_match == STAGE1_FIXTURE_TRIPLES)

    return {
        "curve": {"p": p, "a": a, "b": b},
        "n_triples": STAGE1_FIXTURE_TRIPLES,
        "n_split_with_multiplicity": n_split_mult,
        "n_split_distinct": n_split_distinct,
        "n_root_set_matches_group_law": n_match,
        "wall_seconds": wall,
        "reconstruction_note": (
            "Per EXP-MONO-805a02's own disclosed protocol deviation, the "
            "literal historical 193 triples from KN-FIND-c41ea9's census "
            "are not committed anywhere machine-readable; this run "
            "reproduces the IDENTICAL construction (same curve p=211 "
            "a=37 b=57, same s4_expr resultant, same triple count 193) on "
            "a freshly, deterministically seeded sample of 193 triples "
            "drawn from the on-curve factor base under label "
            "'fixture-triple', per this contract's own "
            "seed_derivation_rule, rather than the literal historical "
            "triples."
        ),
        "first_mismatch": first_mismatch,
        "gate_pass": bool(gate_pass),
        "forced_output_check": (
            "193/193 complete splitting; root sets exactly "
            "{x(+-P1+-P2+-P3)}."
        ),
    }


# --------------------------------------------------------------------------
# Stage 3: twist-cost-identity, j=m-1, m in {4,5}, p in {211,1009}
# --------------------------------------------------------------------------

def stage3_cell(domain: str, m: int, p: int, a: int, b: int, n: int) -> dict:
    E = EllipticCurve(p, a, b)
    tfb = twisted_factor_base(p, a, b)
    delta = tfb["delta"]
    E_delta = EllipticCurve(p, (a * delta * delta) % p, (b * delta ** 3) % p)
    add_counter = AddCounter(E_delta)
    E_delta.add = add_counter  # type: ignore[method-assign]

    stream = SeedStream(domain, "twisted-fb-tuple", p, m)

    k = m - 1
    n_exact_match = 0
    n_split_mult = 0
    n_split_distinct = 0
    factor_degree_multiset_all: list[int] = []
    first_mismatch = None
    timed_out = False
    trials_completed = 0

    xsym = sympy.symbols("x4") if m == 4 else _T  # only used for m=4 direct route

    t0 = time.perf_counter()
    for i in range(n):
        tuple_x = draw_distinct(stream, tfb["xs"], k)
        # (a) DIRECT ROUTE
        if m == 4:
            expr = s4_expr(a, b).subs(
                {x1: tuple_x[0], x2: tuple_x[1], x3: tuple_x[2]}
            )
            var = sympy.symbols("x4")
            analysis = poly_split_analysis(expr, var, p)
        elif m == 5:
            try:
                expr = s5_expr_with_timeout(
                    a, b, tuple_x[0], tuple_x[1], tuple_x[2], tuple_x[3]
                )
            except _S5Timeout:
                timed_out = True
                break
            analysis = poly_split_analysis(expr, _T, p)
        else:
            raise ValueError(f"unsupported m={m}")

        if analysis["split_with_multiplicity"]:
            n_split_mult += 1
        if analysis["split_distinct"]:
            n_split_distinct += 1
        factor_degree_multiset_all.extend(analysis["factor_degree_multiset"])

        # (b) TWIST ROUTE
        points_delta = build_points_delta(a, b, p, delta, tuple_x)
        twist_xs = twist_route_xset(E_delta, delta, p, points_delta, add_counter)

        direct_set = set(analysis["distinct_roots"])
        match = (twist_xs == direct_set)
        if match:
            n_exact_match += 1
        elif first_mismatch is None:
            first_mismatch = {
                "tuple_x": tuple_x,
                "direct_route_xset": sorted(direct_set),
                "twist_route_xset": sorted(twist_xs),
                "poly_analysis": analysis,
            }
        trials_completed += 1
        if time.perf_counter() - t0 > 1700:
            # global soft guard well under the 1800s per-run budget cap;
            # never silently discarded, reported as a stopping-rule event.
            timed_out = True
            break

    wall = time.perf_counter() - t0
    n_attempts = trials_completed * (2 ** (k - 1))  # sign classes per tuple
    expected_add_calls = n_attempts * k

    return {
        "m": m,
        "p": p,
        "a": a,
        "b": b,
        "n_requested": n,
        "n_completed": trials_completed,
        "timed_out": timed_out,
        "twisted_factor_base_size": tfb["size"],
        "twisted_factor_base_sha256": tfb["sha256_digest"],
        "delta_source": tfb["delta_source"],
        "delta": delta,
        "n_exact_match": n_exact_match,
        "exact_match_rate": (n_exact_match / trials_completed) if trials_completed else None,
        "n_split_with_multiplicity": n_split_mult,
        "split_with_multiplicity_rate": (n_split_mult / trials_completed) if trials_completed else None,
        "n_split_distinct": n_split_distinct,
        "split_distinct_rate": (n_split_distinct / trials_completed) if trials_completed else None,
        "factor_degree_multiset": dict(Counter(factor_degree_multiset_all)),
        "first_mismatch": first_mismatch,
        "wall_seconds": wall,
        "operation_count": {
            "add_calls_measured": add_counter.n,
            "add_calls_expected_m_minus_1_per_attempt": expected_add_calls,
            "reconciles_exactly": (add_counter.n - expected_add_calls) if trials_completed else None,
            "n_attempts_2_pow_m_minus_2_per_tuple": n_attempts,
            "multiplications_per_attempt": 1,
            "note": (
                "Per attempt: exactly m-1 EllipticCurve.add calls (acc "
                "starts at the point at infinity / None, folding in each "
                "of the m-1 signed twist points via one add() call each) "
                "plus one final F_p multiplication (X(R)*inverse(delta)). "
                "Reported HERE, beside (never folded into) H-MONO-40aca5's "
                "own D_trial(E)=m-1 count for the j=0 branch."
            ),
        },
    }


def stage3_factor_base_build_timing() -> dict:
    """Twisted-factor-base build wall time per p, reported SEPARATELY from
    per-attempt operation cost, per H-MONO-40aca5's own H2 convention."""
    out = {}
    for name, c in CURVES.items():
        t0 = time.perf_counter()
        tfb = twisted_factor_base(c["p"], c["a"], c["b"])
        wall = time.perf_counter() - t0
        out[name] = {
            "p": c["p"],
            "size": tfb["size"],
            "sha256_digest": tfb["sha256_digest"],
            "delta_source": tfb["delta_source"],
            "delta": tfb["delta"],
            "wall_seconds": wall,
        }
    return out


def stage3(domain: str) -> dict:
    fb_timing = stage3_factor_base_build_timing()
    cells = {}
    for m in STAGE3_M_VALUES:
        n = STAGE3_N_PER_CELL[m]
        for name, c in CURVES.items():
            key = f"m{m}_{name}"
            cells[key] = stage3_cell(domain, m, c["p"], c["a"], c["b"], n)
    return {
        "twisted_factor_base_build": fb_timing,
        "cells": cells,
    }


# --------------------------------------------------------------------------
# Stage 4a: wrong-rescaling-constant mutant control
# --------------------------------------------------------------------------

def stage4a(domain: str) -> dict:
    m, p, a, b = STAGE4A_M, STAGE4A_P, STAGE4A_A, STAGE4A_B
    k = m - 1
    tfb = twisted_factor_base(p, a, b)
    delta = tfb["delta"]
    E_delta = EllipticCurve(p, (a * delta * delta) % p, (b * delta ** 3) % p)
    add_counter = AddCounter(E_delta)
    E_delta.add = add_counter  # type: ignore[method-assign]

    # Independently drawn delta' != delta, from the SAME twisted-factor-base
    # construction's non-residue values, via f(x) at a distinct non-residue
    # x. DISCLOSED CHOICE: delta' is drawn ONCE for the whole Stage 4a
    # (a single deliberately-wrong rescaling constant, matching the
    # contract's own singular phrasing "a deliberately wrong final
    # rescaling constant"), not redrawn per trial -- the spec text does not
    # unambiguously require per-trial redraw and this is the simpler,
    # equally-valid reading; see implementation.md.
    dp_stream = SeedStream(domain, "mutant-delta-prime", p, m)
    remaining_non_residues = [x for x in tfb["xs"] if x != tfb["delta_source"]]
    if not remaining_non_residues:
        raise RuntimeError("twisted factor base has only one non-residue x; "
                            "cannot draw a distinct delta'")
    dp_source = draw_distinct(dp_stream, remaining_non_residues, 1)[0]
    delta_prime = f_val(a, b, dp_source, p)
    if delta_prime == delta:
        raise RuntimeError("delta' collided with delta despite distinct x "
                            "source (should be impossible for distinct x "
                            "under this construction)")

    tuple_stream = SeedStream(domain, "mutant-tuple", p, m)

    n_mutant_match = 0
    trials = []
    first_mutant_hit = None
    t0 = time.perf_counter()
    for i in range(STAGE4A_N):
        tuple_x = draw_distinct(tuple_stream, tfb["xs"], k)
        expr = s4_expr(a, b).subs(
            {x1: tuple_x[0], x2: tuple_x[1], x3: tuple_x[2]}
        )
        var = sympy.symbols("x4")
        analysis = poly_split_analysis(expr, var, p)
        direct_set = set(analysis["distinct_roots"])

        points_delta = build_points_delta(a, b, p, delta, tuple_x)
        mutant_xs = mutant_twist_route_xset(
            E_delta, delta_prime, p, points_delta, add_counter
        )

        match = (mutant_xs == direct_set)
        if match:
            n_mutant_match += 1
            if first_mutant_hit is None:
                first_mutant_hit = {
                    "tuple_x": tuple_x,
                    "direct_route_xset": sorted(direct_set),
                    "mutant_twist_route_xset": sorted(mutant_xs),
                }
        trials.append({
            "tuple_x": tuple_x,
            "direct_route_xset": sorted(direct_set),
            "mutant_twist_route_xset": sorted(mutant_xs),
            "match": match,
        })
    wall = time.perf_counter() - t0

    return {
        "m": m, "p": p, "a": a, "b": b,
        "j": m - 1,
        "n_trials": STAGE4A_N,
        "delta": delta,
        "delta_prime": delta_prime,
        "delta_prime_source_x": dp_source,
        "n_mutant_reproduces_direct_route": n_mutant_match,
        "mutant_agreement_rate": n_mutant_match / STAGE4A_N,
        "control_holds_discriminating_power": bool(
            n_mutant_match / STAGE4A_N < 0.5
        ),
        "first_mutant_hit": first_mutant_hit,
        "trials": trials,
        "wall_seconds": wall,
        "excluded_mutants_note": (
            "Per the frozen contract's own explicit exclusion, NEITHER a "
            "sign flip on y_i' NOR a rebuild of both the twist and the "
            "rescaling with the same delta' is used here (both provably "
            "cannot fail and would give the control no discriminating "
            "power). This is exactly and only the final-rescaling-constant "
            "mutation: the twist sum R uses the CORRECT delta throughout, "
            "only the final X(R)*inverse(delta_or_prime) step is mutated."
        ),
    }


def independent_sample_check(domain: str) -> dict:
    """Explicit disclosure check: Stage 4a's 50 mutant-tuple draws must not
    reuse Stage 3's own m=4/p=211 twisted-fb-tuple sample. Both streams use
    DIFFERENT labels (independent SHA-256 draw streams by construction), but
    this is verified directly by recomputing both tuple sets and checking
    for overlap, per the contract's own INDEPENDENT-CONTROL-SAMPLE control."""
    p, a, b, m = STAGE4A_P, STAGE4A_A, STAGE4A_B, STAGE4A_M
    tfb = twisted_factor_base(p, a, b)
    k = m - 1

    s3_stream = SeedStream(domain, "twisted-fb-tuple", p, m)
    s3_tuples = set()
    for _ in range(STAGE3_N_PER_CELL[m]):
        s3_tuples.add(tuple(sorted(draw_distinct(s3_stream, tfb["xs"], k))))

    s4a_stream = SeedStream(domain, "mutant-tuple", p, m)
    s4a_tuples = set()
    for _ in range(STAGE4A_N):
        s4a_tuples.add(tuple(sorted(draw_distinct(s4a_stream, tfb["xs"], k))))

    overlap = s3_tuples & s4a_tuples
    return {
        "stage3_m4_p211_tuple_count": len(s3_tuples),
        "stage4a_tuple_count": len(s4a_tuples),
        "overlap_count": len(overlap),
        "overlap_tuples": sorted(overlap),
        "independent_by_construction": True,
        "note": (
            "Stage 3's 'twisted-fb-tuple' stream and Stage 4a's "
            "'mutant-tuple' stream use different SHA-256 labels, hence "
            "independent digest sequences by construction (per the "
            "contract's own seed_derivation_rule). overlap_count is "
            "reported directly as an empirical check, not assumed."
        ),
    }


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main():
    if len(sys.argv) != 3:
        print("usage: run_experiment.py <seed> <outdir>", file=sys.stderr)
        sys.exit(2)
    seed = int(sys.argv[1])
    outdir = Path(sys.argv[2])
    outdir.mkdir(parents=True, exist_ok=True)

    domain = f"{DOMAIN_BASE}/run-{seed}"

    t_start = time.perf_counter()
    result = {"seed": seed, "domain": domain}

    s1 = stage1(domain)
    result["stage1"] = s1

    halted_at_gate = None
    if not s1["gate_pass"]:
        halted_at_gate = "STAGE1-HARD-GATE-FIXTURE"
        result["stage3"] = None
        result["stage4a"] = None
        result["independent_sample_check"] = None
    else:
        s3 = stage3(domain)
        result["stage3"] = s3
        s4a = stage4a(domain)
        result["stage4a"] = s4a
        result["independent_sample_check"] = independent_sample_check(domain)

    result["halted_at_gate"] = halted_at_gate
    result["total_wall_seconds"] = time.perf_counter() - t_start

    with open(outdir / "raw-result.json", "w") as f:
        json.dump(result, f, indent=2, default=str)

    print(json.dumps({
        "seed": seed,
        "stage1_gate_pass": s1["gate_pass"],
        "halted_at_gate": halted_at_gate,
        "total_wall_seconds": result["total_wall_seconds"],
    }, indent=2))


if __name__ == "__main__":
    main()
