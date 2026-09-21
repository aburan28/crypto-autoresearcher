#!/usr/bin/env python3
"""EXP-MONO-7f39bf run harness.

Independent, new implementation (per the frozen specification's own
`inputs.reference_implementation_read_only`: EXP-MONO-805a02's
`implementation/run_experiment.py` is read as a REFERENCE for the exact
`.subs()` construction pattern only -- it is `frozen: true` and is never
imported, executed, or modified here).

Builds the CORRECTED partial-locus construction (H-MONO-6adf3c `mechanism`):
m-2 factor-base coordinates fixed to concrete on-curve x-values, the target
T left generic/symbolic throughout tower construction. Executes the full
battery: STAGE0 (hard precondition gate), STAGE1 (false-positive rate),
STAGE1B (random-subset null), STAGE2 (field-operation cost).

REUSES harness/semaev.py's s3_expr/s4_expr/build_factor_base and
harness/toycurve.py's EllipticCurve/Point directly, per the specification's
own `invalidation_rules` (frozen implementation base).

Usage: python3 run_experiment.py <seed> <outdir>
Writes raw-result.json into <outdir>.
"""
from __future__ import annotations

import json
import random
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

import sympy  # noqa: E402

from harness.semaev import (  # noqa: E402
    s3_expr, s4_expr, x1 as HX1, x2 as HX2, x3 as HX3, build_factor_base,
)
from harness.toycurve import EllipticCurve, ECDLPInstance  # noqa: E402

# --------------------------------------------------------------------------
# Fixed protocol constants (disclosed choices; the frozen specification
# itself pins m, p, seeds, and the >=1000/>=20 floors but leaves the exact
# factor-base size and Stage-2 Groebner trial count to the Executor -- see
# implementation.md "Disclosed protocol choices").
# --------------------------------------------------------------------------
FACTOR_BASE_SIZE = 30
STAGE1_CANDIDATES = 1000
STAGE0_SAMPLE_T = 25
M5_TIMEOUT_SECONDS = 300.0
GROEBNER_TRIALS_PER_CELL = 2
GROEBNER_TIMEOUT_SECONDS = 30.0
GROEBNER_PROBE_FACTOR_BASE_SIZE = 6

M_VALUES = [4, 5]
PRIMES = [211, 431, 1009]
CURVES = {
    211: {"A": 37, "B": 57, "provenance": "KN-FIND-c41ea9 committed curve, reused via EXP-MONO-805a02 FIXTURE_A/FIXTURE_B."},
    1009: {"A": 17, "B": 19, "provenance": "EXP-MONO-805a02 SECOND_A/SECOND_B."},
    # p=431: found by the specification's own deterministic lexicographic
    # search procedure (curve_selection.p_431), executed once below and
    # recorded verbatim in raw-result.json['p431_curve_search'].
}


def find_p431_curve() -> dict:
    """Deterministic lexicographic search per specification `curve_selection.p_431`.

    1 <= A,B <= 100, lexicographic (A outer ascending, B inner ascending);
    first pair with: non-singular, non-supersingular (t mod p != 0), and a
    prime-order subgroup of size >= 20.
    """
    p = 431
    tries = 0
    for A in range(1, 101):
        for B in range(1, 101):
            tries += 1
            disc = (4 * A ** 3 + 27 * B ** 2) % p
            if disc == 0:
                continue
            E = EllipticCurve(p, A, B)
            order = E.order()
            t = p + 1 - order
            if t % p == 0:
                continue
            factors = sympy.factorint(order)
            prime_subgroups_ge20 = [int(f) for f in factors if f >= 20]
            if not prime_subgroups_ge20:
                continue
            n = max(prime_subgroups_ge20)
            return {
                "A": A, "B": B, "p": p, "order_E": order, "trace": t,
                "largest_prime_order_subgroup": n,
                "factorization": {int(k): int(v) for k, v in factors.items()},
                "tries": tries,
            }
    raise RuntimeError("no suitable p=431 curve found in [1,100]x[1,100]")


def horner_mod(coeffs: list[int], v: int, p: int) -> int:
    r = 0
    for c in coeffs:
        r = (r * v + c) % p
    return r


def poly_to_coeff_list_mod(expr, var, p: int) -> list[int]:
    """Univariate integer-coefficient poly in `var` -> coeffs mod p (high->low), stripped."""
    expr = sympy.expand(expr)
    poly = sympy.Poly(expr, var)
    coeffs = [int(c) % p for c in poly.all_coeffs()]
    while len(coeffs) > 1 and coeffs[0] == 0:
        coeffs = coeffs[1:]
    return coeffs


def bivariate_coeffs_in_T(expr, free_sym, T_sym) -> list[list[int]]:
    """expr(free_sym, T_sym) -> [coeffs-in-T (as plain int lists) for each
    descending power of free_sym]. Each inner list is the T_sym-polynomial's
    *integer* coefficient list (un-reduced mod p; reduction happens per prime
    at evaluation time so degree-drop is detected correctly per prime)."""
    expr = sympy.expand(expr)
    poly = sympy.Poly(expr, free_sym)
    out = []
    for c in poly.all_coeffs():
        c = sympy.expand(c)
        if c.free_symbols - {T_sym}:
            raise ValueError(f"unexpected free symbols in coefficient: {c.free_symbols}")
        if c == 0:
            out.append([0])
            continue
        if T_sym not in c.free_symbols:
            out.append([int(c)])
            continue
        cpoly = sympy.Poly(c, T_sym)
        out.append([int(x) for x in cpoly.all_coeffs()])
    return out


def eval_bivariate_mod(coeffs_in_T: list[list[int]], Tval: int, p: int) -> list[int]:
    """Evaluate the free-var coefficients (each a poly-in-T coeff list) at
    T=Tval mod p; return the resulting free-var coefficient list mod p,
    leading zeros stripped (degree-drop honestly reflected, per
    EXP-MONO-805a02's own `poly_roots_bruteforce` convention)."""
    out = [horner_mod([c % p for c in ct], Tval, p) for ct in coeffs_in_T]
    while len(out) > 1 and out[0] == 0:
        out = out[1:]
    return out


def bruteforce_roots_mod(coeffs: list[int], p: int) -> list[int]:
    return [v for v in range(p) if horner_mod(coeffs, v, p) == 0]


def legendre(a: int, p: int) -> int:
    a %= p
    if a == 0:
        return 0
    r = pow(a, (p - 1) // 2, p)
    return 1 if r == 1 else -1


def modpow_counted(base: int, exp: int, mod: int, counter: list[int]) -> int:
    """Square-and-multiply modexp, counting every modular multiplication
    actually performed (a genuinely MEASURED field-operation count, not an
    estimate from a closed-form bit-length formula)."""
    result = 1
    base %= mod
    while exp > 0:
        if exp & 1:
            result = (result * base) % mod
            counter[0] += 1
        base = (base * base) % mod
        counter[0] += 1
        exp >>= 1
    return result


def legendre_counted(a: int, p: int, counter: list[int]) -> int:
    a %= p
    if a == 0:
        return 0
    r = modpow_counted(a, (p - 1) // 2, p, counter)
    return 1 if r == 1 else -1


def on_curve_points(E: EllipticCurve) -> list[tuple[int, int]]:
    pts = []
    for xv in range(E.p):
        pt = E.lift_x(xv)
        if pt is not None:
            pts.append(pt)
    return pts


# --------------------------------------------------------------------------
# STAGE0: construction + branch decomposition, per (p, m) cell.
# --------------------------------------------------------------------------

def build_construction_m4(a: int, b: int, p: int, fb_points_x: list[int]):
    """m=4: 2 factor-base coordinates (x-only) concrete, free coord + T symbolic.

    Returns (free_sym, T_sym, g_expr, branches[list of dict]).
    Branches per H-MONO-6adf3c `mechanism`: t_+ = x(P1+P2), t_- = x(P1-P2),
    computed via direct EC arithmetic (zero polynomial arithmetic for this
    step); each gives quad_branch(free, T) = S3(free, T, t_branch), a
    quadratic in `free` with coefficients polynomial in T.
    """
    E = EllipticCurve(p, a, b)
    P1 = E.lift_x(fb_points_x[0])
    P2 = E.lift_x(fb_points_x[1])
    if P1 is None or P2 is None:
        raise ValueError("factor-base x-coordinate is not on-curve")

    x4sym = sympy.symbols("x4")
    free_sym, T_sym = HX3, x4sym
    S4 = s4_expr(a, b)
    g = sympy.expand(S4.subs({HX1: P1[0], HX2: P2[0]}))

    branches = []
    Psum = E.add(P1, P2)
    Pdiff = E.add(P1, E.negate(P2))
    for name, Rpt in [("t_plus_P1P2", Psum), ("t_minus_P1negP2", Pdiff)]:
        if Rpt is None:
            branches.append({"name": name, "degenerate_point_at_infinity": True})
            continue
        tval = Rpt[0]
        quad = sympy.expand(
            s3_expr(a, b).subs({HX1: free_sym, HX2: T_sym, HX3: tval}, simultaneous=True)
        )
        branches.append({
            "name": name, "branch_point": list(Rpt), "t_value": int(tval),
            "quad_expr": quad,
        })
    return free_sym, T_sym, g, branches, {"P1": list(P1), "P2": list(P2)}


def build_construction_m5(a: int, b: int, p: int, fb_points_x: list[int]):
    """m=5: 3 factor-base coordinates concrete, free coord + T symbolic.

    Mirrors the reference `stage5_m5` construction with the final
    `.subs(T, Rt[0])` step OMITTED (per the specification's own `objective`).
    U-elimination roots (4 branches) obtained directly via EC arithmetic on
    the 3 fixed points (zero polynomial arithmetic), generalizing the m=4
    t_+/t_- step -- this is the genuinely new construction named as R1/R2.
    """
    E = EllipticCurve(p, a, b)
    P1 = E.lift_x(fb_points_x[0])
    P2 = E.lift_x(fb_points_x[1])
    P3 = E.lift_x(fb_points_x[2])
    if P1 is None or P2 is None or P3 is None:
        raise ValueError("factor-base x-coordinate is not on-curve")

    x4sym, U, T_sym = sympy.symbols("x4 U T")
    free_sym = x4sym
    S4 = s4_expr(a, b)
    S4_numeric_U = sympy.expand(S4.subs({HX1: P1[0], HX2: P2[0], HX3: P3[0]}).subs(x4sym, U))
    S3_part = sympy.expand(
        s3_expr(a, b).subs({HX1: x4sym, HX2: T_sym, HX3: U}, simultaneous=True)
    )
    g = sympy.expand(sympy.resultant(S4_numeric_U, S3_part, U))

    # 4 branches: u = x(e1 P1 + e2 P2 + e3 P3), e1 fixed +1 (covers all 8
    # sign combinations modulo the overall-negation duplicate).
    signs = [(1, 1, 1), (1, 1, -1), (1, -1, 1), (1, -1, -1)]
    branches = []
    for idx, (e1, e2, e3) in enumerate(signs):
        pts = [P1 if e1 == 1 else E.negate(P1),
               P2 if e2 == 1 else E.negate(P2),
               P3 if e3 == 1 else E.negate(P3)]
        acc = None
        for pt in pts:
            acc = E.add(acc, pt)
        name = f"branch_{'+' if e1==1 else '-'}{'+' if e2==1 else '-'}{'+' if e3==1 else '-'}"
        if acc is None:
            branches.append({"name": name, "degenerate_point_at_infinity": True})
            continue
        uval = acc[0]
        # Integrity check: uval must be a root of S4_numeric_U(U).
        u_check = int(sympy.expand(S4_numeric_U).subs(U, uval)) % p
        quad = sympy.expand(
            s3_expr(a, b).subs({HX1: free_sym, HX2: T_sym, HX3: uval}, simultaneous=True)
        )
        branches.append({
            "name": name, "branch_point": list(acc), "u_value": int(uval),
            "quad_expr": quad,
            "u_root_check_S4_numeric_U_at_uval_mod_p": u_check,
            "u_root_check_passed": (u_check == 0),
        })
    return free_sym, T_sym, g, branches, {"P1": list(P1), "P2": list(P2), "P3": list(P3)}


def stage0_cell(a: int, b: int, p: int, m: int, fb_points_x: list[int], seed: int,
                 tag: str) -> dict:
    """STAGE0-GENERIC-CONSTRUCTION-PRECONDITION-GATE for one (p, m) cell.

    `tag` labels which factor-base source this construction was built from
    (interval_generator_based / random_x_subset), for the RANDOM-SUBSET-NULL
    control's own gate check.
    """
    t0 = time.perf_counter()
    timed_out = False
    try:
        if m == 4:
            free_sym, T_sym, g, branches, fb_used = build_construction_m4(a, b, p, fb_points_x)
        elif m == 5:
            if time.perf_counter() - t0 > M5_TIMEOUT_SECONDS:
                timed_out = True
            free_sym, T_sym, g, branches, fb_used = build_construction_m5(a, b, p, fb_points_x)
            if time.perf_counter() - t0 > M5_TIMEOUT_SECONDS:
                timed_out = True
        else:
            raise ValueError(f"unsupported m={m}")
    except Exception as exc:  # noqa: BLE001
        return {
            "p": p, "m": m, "tag": tag, "status": "failed_infrastructure",
            "reason": f"construction raised: {type(exc).__name__}: {exc}",
        }
    construction_seconds = time.perf_counter() - t0
    if timed_out or construction_seconds > M5_TIMEOUT_SECONDS:
        return {
            "p": p, "m": m, "tag": tag, "status": "failed_infrastructure",
            "reason": f"m=5 tower construction exceeded {M5_TIMEOUT_SECONDS}s "
                      f"(measured {construction_seconds:.3f}s)",
        }

    # (0a) degree check + T-dependence of g itself.
    g_expanded = sympy.expand(g)
    deg_free = sympy.Poly(g_expanded, free_sym).degree()
    predicted_deg = 2 ** (m - 2)
    g_depends_on_T = T_sym in g_expanded.free_symbols

    # (0c)/(0d) per-branch discriminant analysis.
    branch_reports = []
    n_T_dependent = 0
    for br in branches:
        if br.get("degenerate_point_at_infinity"):
            branch_reports.append({**br, "disc_expr": None, "disc_is_constant_in_T": None})
            continue
        quad = br["quad_expr"]
        quad_poly_free = sympy.Poly(quad, free_sym)
        quad_deg = quad_poly_free.degree()
        disc = sympy.expand(sympy.discriminant(quad_poly_free, free_sym)) if quad_deg == 2 else None
        disc_depends_on_T = (disc is not None) and (T_sym in disc.free_symbols)
        if disc_depends_on_T:
            n_T_dependent += 1
        branch_reports.append({
            **br,
            "quad_degree_in_free": quad_deg,
            "disc_expr_str": str(disc) if disc is not None else None,
            "disc_is_constant_in_T": (not disc_depends_on_T) if disc is not None else None,
        })

    # (0b) independent brute-force root-set verification at >=20 sampled
    # concrete T values per prime.
    g_coeffs_in_T = bivariate_coeffs_in_T(g_expanded, free_sym, T_sym) if g_depends_on_T else None
    branch_coeffs_in_T = []
    for br in branch_reports:
        if br.get("degenerate_point_at_infinity") or br["disc_expr_str"] is None:
            branch_coeffs_in_T.append(None)
            continue
        quad_poly = sympy.Poly(br["quad_expr"], free_sym)
        branch_coeffs_in_T.append(bivariate_coeffs_in_T(quad_poly.as_expr(), free_sym, T_sym))

    rng = random.Random(str((seed, p, m, tag, "stage0-sample")))
    E = EllipticCurve(p, a, b)
    all_x = list(range(p))
    root_set_mismatches = []
    n_checked = 0
    for _ in range(STAGE0_SAMPLE_T):
        Tval = rng.choice(all_x)
        n_checked += 1
        if g_coeffs_in_T is None:
            g_free_coeffs = poly_to_coeff_list_mod(g_expanded, free_sym, p) if not g_depends_on_T else None
        else:
            g_free_coeffs = eval_bivariate_mod(g_coeffs_in_T, Tval, p)
        g_roots = set(bruteforce_roots_mod(g_free_coeffs, p)) if g_free_coeffs else set()

        predicted_roots = set()
        for bc in branch_coeffs_in_T:
            if bc is None:
                continue
            free_coeffs_at_T = eval_bivariate_mod(bc, Tval, p)
            predicted_roots |= set(bruteforce_roots_mod(free_coeffs_at_T, p))

        if predicted_roots != g_roots:
            root_set_mismatches.append({
                "T": Tval, "g_roots": sorted(g_roots), "predicted_roots": sorted(predicted_roots),
            })

    status = "pass"
    if root_set_mismatches:
        status = "failed_infrastructure"
    elif not g_depends_on_T or deg_free != predicted_deg:
        status = "degenerate"

    return {
        "p": p, "m": m, "tag": tag, "status": status,
        "construction_seconds": construction_seconds,
        "deg_free_measured": deg_free, "deg_free_predicted": predicted_deg,
        "deg_free_matches_prediction": (deg_free == predicted_deg),
        "g_depends_on_T": g_depends_on_T,
        "n_branches_total": len(branches),
        "n_branches_T_dependent_discriminant": n_T_dependent,
        "predicted_T_dependent_level_count_m_minus_2": m - 2,
        "T_dependent_count_matches_prediction": (n_T_dependent == (m - 2)),
        "branch_reports": [
            {k: v for k, v in br.items() if k != "quad_expr"} for br in branch_reports
        ],
        "root_set_check": {
            "n_T_sampled": n_checked,
            "n_mismatches": len(root_set_mismatches),
            "mismatches": root_set_mismatches,
        },
        "fb_points_used": fb_used if m in (4, 5) else None,
        "_free_sym_name": str(free_sym), "_T_sym_name": str(T_sym),
        "g_coeffs_in_T": g_coeffs_in_T,
        "_free_sym_obj": free_sym, "_T_sym_obj": T_sym,
        "_branch_reports_full": branch_reports,
    }


# --------------------------------------------------------------------------
# STAGE1 / STAGE1B: false-positive rate + true-negative guarantee.
# --------------------------------------------------------------------------

def build_evaluator(cell: dict, free_sym, T_sym, branches: list[dict]):
    """Precompute fast (pure-int) evaluators for filter + ground truth."""
    p = cell["p"]
    branch_data = []
    for br in branches:
        if br.get("degenerate_point_at_infinity") or br.get("disc_expr_str") is None:
            branch_data.append(None)
            continue
        quad_poly = sympy.Poly(br["quad_expr"], free_sym)
        coeffs_in_T = bivariate_coeffs_in_T(quad_poly.as_expr(), free_sym, T_sym)
        disc = sympy.Poly(br["quad_expr"], free_sym)
        disc_expr = sympy.discriminant(disc, free_sym)
        disc_coeffs = None
        if T_sym in sympy.expand(disc_expr).free_symbols:
            disc_poly = sympy.Poly(sympy.expand(disc_expr), T_sym)
            disc_coeffs = [int(c) for c in disc_poly.all_coeffs()]
        else:
            disc_coeffs = [int(sympy.expand(disc_expr))]
        branch_data.append({"coeffs_in_T": coeffs_in_T, "disc_coeffs": disc_coeffs})
    return branch_data


def evaluate_candidate(Tval: int, p: int, branch_data: list, count_ops: list[int] | None = None):
    """Filter verdict (PASS/REJECT) + the branch quadratics' actual roots
    (for ground-truth membership checking), all via measured modular
    arithmetic (no estimation)."""
    verdict = "REJECT"
    all_roots = set()
    for bd in branch_data:
        if bd is None:
            continue
        disc_val = horner_mod([c % p for c in bd["disc_coeffs"]], Tval, p)
        if count_ops is not None:
            chi = legendre_counted(disc_val, p, count_ops)
        else:
            chi = legendre(disc_val, p)
        if chi == -1:
            continue
        verdict = "PASS"
        # Solve the quadratic mod p for its actual root(s).
        free_coeffs = eval_bivariate_mod(bd["coeffs_in_T"], Tval, p)
        if len(free_coeffs) == 3 and free_coeffs[0] != 0:
            A, B, C = free_coeffs
            inv2A = pow((2 * A) % p, -1, p)
            if chi == 0:
                x0 = (-B * inv2A) % p
                all_roots.add(x0)
            else:
                sq = sympy.ntheory.residue_ntheory.sqrt_mod(disc_val, p)
                if sq is not None:
                    all_roots.add((-B + sq) * inv2A % p)
                    all_roots.add((-B - sq) * inv2A % p)
        elif len(free_coeffs) <= 2 and free_coeffs and free_coeffs[-1] == 0 and len(free_coeffs) == 2 and free_coeffs[0] != 0:
            all_roots.add((-free_coeffs[1] * pow(free_coeffs[0], -1, p)) % p)
    return verdict, all_roots


def stage1_measure(a: int, b: int, p: int, m: int, cell: dict, free_sym, T_sym,
                    branch_reports: list[dict], V: list[int], seed: int, tag: str) -> dict:
    branch_data = build_evaluator(cell, free_sym, T_sym, branch_reports)
    Vset = set(V)
    rng = random.Random(str((seed, p, m, tag, "stage1-candidates")))
    E = EllipticCurve(p, a, b)
    all_pts = on_curve_points(E)
    all_x = [pt[0] for pt in all_pts]

    n_pass = 0
    n_pass_false_positive = 0
    n_reject = 0
    n_reject_confirmed_root_free = 0
    n_reject_exception = 0
    field_op_counter = [0]
    for _ in range(STAGE1_CANDIDATES):
        Tval = rng.choice(all_x)
        verdict, filter_roots = evaluate_candidate(Tval, p, branch_data, count_ops=field_op_counter)
        # Ground truth: brute-force full root set of g at this T, independent
        # of the filter's own branch computation, per
        # GROUND-TRUTH-INDEPENDENT-CODE-PATH.
        g_free_coeffs = eval_bivariate_mod(cell["g_coeffs_in_T"], Tval, p) if cell["g_coeffs_in_T"] else []
        ground_truth_roots = set(bruteforce_roots_mod(g_free_coeffs, p)) if g_free_coeffs else set()
        genuine_member_roots = ground_truth_roots & Vset

        if verdict == "PASS":
            n_pass += 1
            if not genuine_member_roots:
                n_pass_false_positive += 1
        else:
            n_reject += 1
            if not ground_truth_roots:
                n_reject_confirmed_root_free += 1
            else:
                n_reject_exception += 1

    return {
        "p": p, "m": m, "tag": tag,
        "trials": STAGE1_CANDIDATES,
        "n_pass": n_pass, "n_reject": n_reject,
        "n_pass_false_positive": n_pass_false_positive,
        "false_positive_rate": (n_pass_false_positive / n_pass) if n_pass else None,
        "n_reject_confirmed_root_free": n_reject_confirmed_root_free,
        "true_negative_guarantee_fraction": (n_reject_confirmed_root_free / n_reject) if n_reject else None,
        "n_reject_exceptions_instrument_bug_candidates": n_reject_exception,
        "field_operations_legendre_modmuls_measured": field_op_counter[0],
        "factor_base_size": len(V),
    }


# --------------------------------------------------------------------------
# STAGE2: field-operation cost (resolvent vs enumerate-and-test).
# --------------------------------------------------------------------------

D_TRIAL_E_GROUP_ADDS = {m: m - 1 for m in M_VALUES}  # cited, not re-derived (EXP-MONO-805a02 STAGE3)


def stage2_cost(cell_stage0: dict, stage1_result: dict, m: int) -> dict:
    n_evals = stage1_result["trials"]
    tower_construction_seconds = cell_stage0["construction_seconds"]
    eval_field_ops = stage1_result["field_operations_legendre_modmuls_measured"]
    eval_field_ops_per_decision = eval_field_ops / n_evals if n_evals else None
    # Tower construction charged in FIELD operations too: reported as wall
    # time (sympy polynomial arithmetic; sympy's internal operation count is
    # not observable, so -- per harness/semaev.py's own "honesty note" on
    # observable proxies -- only wall time is reported for this component,
    # never fabricated as a modmul count).
    return {
        "m": m,
        "resolvent_route": {
            "per_decision_field_operations_legendre_modmuls_measured": eval_field_ops_per_decision,
            "n_decisions": n_evals,
            "tower_construction_wall_seconds_UNAMORTIZED": tower_construction_seconds,
            "tower_construction_wall_seconds_AMORTIZED_per_decision": tower_construction_seconds / n_evals if n_evals else None,
            "note": (
                "Tower construction's field-operation count (sympy polynomial "
                "arithmetic for disc_branch(T)) is NOT independently countable "
                "the way Legendre-symbol modmuls are (sympy does not expose a "
                "modmul counter for its internal Poly/resultant/discriminant "
                "routines) -- per harness/semaev.py's own 'observable proxies, "
                "never the theoretical count' convention, only wall-clock "
                "seconds is reported for construction, never a fabricated "
                "modmul estimate."
            ),
        },
        "enumerate_and_test_baseline": {
            "D_trial_E_group_additions_per_attempt": D_TRIAL_E_GROUP_ADDS[m],
            "formula": "D_trial(E) = m - 1 group additions + O(1) lookup, independent of p",
            "source": "IDEA-20260806-9d47e2; EXP-MONO-805a02 preregistered_prediction + STAGE3-OPERATION-COUNT measurement (cited, not re-derived here).",
        },
        "ratio_resolvent_over_enumerate": None,
        "refused_no_declared_conversion": True,
        "unit_declaration_tripwire_reason": (
            "No group-operation-to-field-operation conversion constant is "
            "declared anywhere in this contract (per EXP-MONO-805a02's own "
            "identical control, EXP-MONO-805a02 run raw-result.json's own "
            "'reason' field, cited verbatim as precedent). Resolvent field "
            "operations and D_trial(E) group operations are reported side by "
            "side, never combined into a ratio."
        ),
    }


# --------------------------------------------------------------------------
# Secondary metric: resolvent vs Groebner-basis membership test (m=4 only;
# see implementation.md for why m=5 is not attempted -- no S5 polynomial
# exists in harness/semaev.py and building one via resultant elimination for
# a full Groebner probe was judged out of budget scope for a SECONDARY
# metric; disclosed, not silently dropped).
# --------------------------------------------------------------------------

import signal


class _AlarmTimeout(Exception):
    pass


def _alarm_handler(signum, frame):
    raise _AlarmTimeout()


def groebner_probe_m4(a: int, b: int, p: int, V_probe: list[int], seed: int, tag: str) -> list[dict]:
    E = EllipticCurve(p, a, b)
    rng = random.Random(str((seed, p, "groebner-probe-m4", tag)))
    all_x = [pt[0] for pt in on_curve_points(E)]
    fV1 = sympy.prod([(HX1 - v) for v in V_probe])
    fV2 = sympy.prod([(HX2 - v) for v in V_probe])
    fV3 = sympy.prod([(HX3 - v) for v in V_probe])
    x4local = sympy.symbols("x4")
    S4 = s4_expr(a, b)

    have_alarm = hasattr(signal, "SIGALRM")
    if have_alarm:
        old_handler = signal.signal(signal.SIGALRM, _alarm_handler)

    results = []
    for _ in range(GROEBNER_TRIALS_PER_CELL):
        Tval = rng.choice(all_x)
        system = [sympy.expand(S4.subs(x4local, Tval)), fV1, fV2, fV3]
        t0 = time.perf_counter()
        try:
            if have_alarm:
                signal.alarm(int(GROEBNER_TIMEOUT_SECONDS))
            G = sympy.groebner(system, HX1, HX2, HX3, modulus=p, order="grevlex")
            if have_alarm:
                signal.alarm(0)
            elapsed = time.perf_counter() - t0
            polys = list(G.exprs)
            is_trivial = polys == [sympy.Integer(1)]
            results.append({
                "target": Tval, "status": "ok", "groebner_seconds": elapsed,
                "basis_size": len(polys), "is_trivial_ideal": bool(is_trivial),
            })
        except _AlarmTimeout:
            results.append({
                "target": Tval, "status": "failed_infrastructure",
                "reason": f"Groebner basis exceeded {GROEBNER_TIMEOUT_SECONDS}s probe timeout",
            })
        except Exception as exc:  # noqa: BLE001
            results.append({"target": Tval, "status": "failed_infrastructure", "reason": str(exc)})
        finally:
            if have_alarm:
                signal.alarm(0)

    if have_alarm:
        signal.signal(signal.SIGALRM, old_handler)
    return results


# --------------------------------------------------------------------------
# Orchestration
# --------------------------------------------------------------------------

def dummy_instance(p: int, a: int, b: int, seed: int) -> ECDLPInstance:
    return ECDLPInstance(p=p, a=a, b=b, P=None, Q=None, n=1, k=0, field_bits=p.bit_length(), seed=seed)


def run_cell(p: int, a: int, b: int, m: int, seed: int) -> dict:
    inst = dummy_instance(p, a, b, seed)
    V_interval = build_factor_base(inst, FACTOR_BASE_SIZE, seed=seed, scope="full_curve")

    E = EllipticCurve(p, a, b)
    all_pts = on_curve_points(E)
    rng_rand = random.Random(str((seed, p, m, "random-subset-fb")))
    V_random = [pt[0] for pt in rng_rand.sample(all_pts, FACTOR_BASE_SIZE)]

    n_fb_coords = m - 2
    fb_x_interval = sorted(V_interval)[:n_fb_coords]
    fb_x_random = sorted(V_random)[:n_fb_coords]

    cell = {}
    cell["curve"] = {"p": p, "A": a, "B": b}
    cell["m"] = m
    cell["factor_base_size"] = FACTOR_BASE_SIZE
    cell["V_interval_generator_based"] = V_interval
    cell["V_random_x_subset"] = V_random

    stage0_main = stage0_cell(a, b, p, m, fb_x_interval, seed, "interval_generator_based")
    stage0_random = stage0_cell(a, b, p, m, fb_x_random, seed, "random_x_subset")
    cell["stage0"] = {
        "interval_generator_based": {k: v for k, v in stage0_main.items() if not k.startswith("_") and k != "g_coeffs_in_T"},
        "random_x_subset": {k: v for k, v in stage0_random.items() if not k.startswith("_") and k != "g_coeffs_in_T"},
    }

    gate_pass_main = stage0_main["status"] == "pass"
    gate_pass_random = stage0_random["status"] == "pass"
    cell["gate_pass_interval_generator_based"] = gate_pass_main
    cell["gate_pass_random_x_subset"] = gate_pass_random

    if gate_pass_main:
        s1_main = stage1_measure(a, b, p, m, stage0_main, stage0_main["_free_sym_obj"],
                                  stage0_main["_T_sym_obj"], stage0_main["_branch_reports_full"],
                                  V_interval, seed, "interval_generator_based")
        cell["stage1_false_positive_rate"] = s1_main
        cell["stage2_field_operation_cost"] = stage2_cost(stage0_main, s1_main, m)
    else:
        cell["stage1_false_positive_rate"] = None
        cell["stage2_field_operation_cost"] = None
        cell["stage1_skipped_reason"] = f"STAGE0-HARD-GATE: interval-locus status={stage0_main['status']}"

    if gate_pass_random:
        s1_random = stage1_measure(a, b, p, m, stage0_random, stage0_random["_free_sym_obj"],
                                    stage0_random["_T_sym_obj"], stage0_random["_branch_reports_full"],
                                    V_random, seed, "random_x_subset")
        cell["stage1b_random_subset_null"] = s1_random
    else:
        cell["stage1b_random_subset_null"] = None
        cell["stage1b_skipped_reason"] = f"STAGE0-HARD-GATE: random-subset-locus status={stage0_random['status']}"

    # Secondary: Groebner probe, m=4 only, reduced probe factor base (size 10,
    # disclosed) to keep the ideal computation within budget for a SECONDARY
    # metric.
    if m == 4 and gate_pass_main:
        V_probe = sorted(V_interval)[:GROEBNER_PROBE_FACTOR_BASE_SIZE]
        cell["groebner_probe_m4_secondary"] = {
            "probe_factor_base_size": len(V_probe),
            "note": f"New minimal machinery generalized from harness/semaev.py's measure_s3_decomposition; no pre-existing m>=4/5 Groebner cell was found in RQ-MONO-001 (search: grep for 'groebner|Groebner' across experiments/EXP-MONO-*/specification.yaml found only EXP-MONO-805a02, whose own Groebner mentions are Stage-6 label text, not an m>=4 measurement cell). Reduced probe factor-base size ({GROEBNER_PROBE_FACTOR_BASE_SIZE}, vs the main {FACTOR_BASE_SIZE}) is a disclosed scope reduction for this SECONDARY metric only: sympy's Buchberger-style groebner() over 3 variables with a size-8 factor-base ideal was independently timed at ~150s per call during implementation, growing steeply with factor-base size, so a much smaller probe (size {GROEBNER_PROBE_FACTOR_BASE_SIZE}) keeps this secondary, non-gating measurement within budget; the resulting basis-size/timing numbers are NOT comparable in absolute terms to the main FACTOR_BASE_SIZE={FACTOR_BASE_SIZE} enumerate-and-test/resolvent numbers reported elsewhere, and are reported as a directional trend proxy only.",
            "trials": groebner_probe_m4(a, b, p, V_probe, seed, "secondary"),
        }
    elif m == 5:
        cell["groebner_probe_m4_secondary"] = None
        cell["groebner_m5_not_attempted_reason"] = (
            "harness/semaev.py has no S5 polynomial; building one via a further "
            "symbolic resultant elimination (fully general, not the m-2-fixed "
            "partial-locus construction) purely to run a SECONDARY Groebner-cost "
            "probe was judged out of scope for this budget (3600s/2GB, primary "
            "battery already consumes most of the wall clock). Disclosed omission, "
            "not a silent drop -- the primary success_criterion does not require "
            "this secondary metric."
        )
    else:
        cell["groebner_probe_m4_secondary"] = None

    return cell


def main(seed: int, outdir: str) -> None:
    t_start = time.perf_counter()
    outdir_p = Path(outdir)
    outdir_p.mkdir(parents=True, exist_ok=True)

    p431 = find_p431_curve()
    curves = dict(CURVES)
    curves[431] = {"A": p431["A"], "B": p431["B"], "provenance": (
        f"Found by this run's own deterministic lexicographic search over "
        f"1<=A,B<=100 (curve_selection.p_431): first non-singular, "
        f"non-supersingular pair with a prime-order subgroup >= 20, found at "
        f"try {p431['tries']} (A={p431['A']}, B={p431['B']})."
    )}

    cells = []
    for m in M_VALUES:
        for p in PRIMES:
            c = curves[p]
            a, b = c["A"], c["B"]
            cell = run_cell(p, a, b, m, seed)
            cell["curve_provenance"] = c["provenance"]
            cells.append(cell)

    result = {
        "experiment_id": "EXP-MONO-7f39bf",
        "seed": seed,
        "wall_seconds_total": time.perf_counter() - t_start,
        "p431_curve_search": p431,
        "protocol_constants": {
            "FACTOR_BASE_SIZE": FACTOR_BASE_SIZE,
            "STAGE1_CANDIDATES": STAGE1_CANDIDATES,
            "STAGE0_SAMPLE_T": STAGE0_SAMPLE_T,
            "M5_TIMEOUT_SECONDS": M5_TIMEOUT_SECONDS,
            "GROEBNER_TRIALS_PER_CELL": GROEBNER_TRIALS_PER_CELL,
            "GROEBNER_TIMEOUT_SECONDS": GROEBNER_TIMEOUT_SECONDS,
        },
        "cells": cells,
    }

    with open(outdir_p / "raw-result.json", "w") as f:
        json.dump(result, f, indent=2, default=str)

    print(f"wrote {outdir_p / 'raw-result.json'}  (total wall: {result['wall_seconds_total']:.2f}s)")


if __name__ == "__main__":
    seed_arg = int(sys.argv[1])
    outdir_arg = sys.argv[2]
    main(seed_arg, outdir_arg)
