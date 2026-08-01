#!/usr/bin/env python3
"""EXP-XEDN-002 arm A (closed form) + arm D (parameter-count tables).

Arm A: exact N_hit(p), N_slots(p), P_lift(p) as exact rationals for the frozen
family, the exact finite-size exponents alpha_eff, and the limiting alpha.

Arm D: the parameter-count tables that back the scoped codimension lemma in
derivation.md, plus the exact free-(non-monic)-x corroboration.

Every closed form printed here is checked against a direct enumeration
somewhere: the counting steps at small p in this script, the full slot space in
arm B, and the independent section fibering in arm C.

Usage (see implementation/run_arm.sh):
  python3 experiments/EXP-XEDN-002/implementation/arm_a_closed_form.py --run-id RUN-XEDN-002-A
"""
from __future__ import annotations

import argparse
import datetime as dt
import itertools
import json
import math
import os
import sys
import time
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import xedn2_lib as L                                            # noqa: E402

EXHAUSTIVE_SIZES = [5, 7, 11, 13]
CONTRACTED_SIZES = [101, 211, 431, 809]
ALL_SIZES = EXHAUSTIVE_SIZES + CONTRACTED_SIZES


def check_counting_steps(p: int, frozen) -> dict:
    """Direct verification of the two combinatorial steps of the derivation.

    Step 1 (bijection): for a fixed x, {x^3 + b : deg b = 6 exactly} equals
            {f : deg f <= 6, [t^6] f != 1}.
    Step 2 (squarefree census): # monic squarefree of degree n equals
            p^n - p^(n-1) for n >= 2 (brute force with an independent
            discriminant-based squarefree test).
    """
    out = {"p": p}
    # step 1, at two different x
    ok = True
    for (x0, x1) in [(0, 0), (3, 5)]:
        x3 = L.poly_cube_monic_quadratic(x0 % p, x1 % p, p, frozen)
        got = set()
        for b in L.enumerate_deg6_b(p):
            f = frozen.padd(x3, b, p)
            got.add(tuple(f))
        want = set()
        for coeffs in itertools.product(*([range(p)] * 6)):
            for f6 in range(p):
                if f6 == 1:
                    continue
                f = list(coeffs) + [f6]
                while len(f) > 1 and f[-1] == 0:
                    f.pop()
                want.add(tuple(f))
        ok = ok and (got == want)
    out["step1_bijection_holds"] = ok
    # step 2
    step2 = {}
    for n in range(0, 4):
        cnt = 0
        for tail in itertools.product(*([range(p)] * n)):
            y = list(tail) + [1]
            while len(y) > 1 and y[-1] == 0:
                y.pop()
            if len(y) - 1 != n:
                continue
            if L.ref_is_squarefree_disc(y, p):
                cnt += 1
        step2[n] = {"brute_force": cnt, "formula": L.monic_squarefree(n, p),
                    "agree": cnt == L.monic_squarefree(n, p)}
    out["step2_monic_squarefree"] = step2
    out["step2_all_agree"] = all(v["agree"] for v in step2.values())
    return out


def arm_a_table() -> list:
    rows = []
    for p in ALL_SIZES:
        pl = L.p_lift(p)
        rows.append({
            "p": p,
            "field_bits": p.bit_length(),
            "N_slots": L.n_slots(p),
            "N_hit": L.n_hit(p),
            "P_lift_exact": f"{pl.numerator}/{pl.denominator}",
            "P_lift_float": float(pl),
            "P_lift_times_2p3": float(pl) * 2 * p**3,
            "mean_hit_slots_per_surface": float(L.mean_sections_per_surface(p)),
            "N_hit_true_square": L.n_hit_true_square(p),
            "P_lift_true_square_float": float(L.p_lift_true_square(p)),
            "N_hit_with_y0_section": L.n_hit_including_zero_section(p),
            "P_lift_with_y0_float": float(L.p_lift_with_zero_section(p)),
            "frozen_false_negative_slots": p**2 * L.q_missed_by_frozen(p),
        })
    return rows


def alpha_table(sizes, prob) -> list:
    rows = []
    for p1, p2 in zip(sizes, sizes[1:]):
        rows.append({"p1": p1, "p2": p2,
                     "alpha_eff": L.alpha_eff(p1, p2, prob)})
    return rows


def ols_alpha(sizes, prob) -> dict:
    xs = [math.log(p) for p in sizes]
    ys = [math.log(float(prob(p))) for p in sizes]
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx)**2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    slope = sxy / sxx
    inter = my - slope * mx
    resid = [y - (inter + slope * x) for x, y in zip(xs, ys)]
    rss = sum(r * r for r in resid)
    return {"sizes": sizes, "alpha_ols": -slope, "log_C": inter,
            "residual_sum_squares": rss, "max_abs_residual": max(abs(r) for r in resid),
            "note": ("the inputs are EXACT rationals, so there is no sampling "
                     "uncertainty; the residuals measure only the deviation of the "
                     "exact law from a pure power law")}


def arm_d_grid() -> dict:
    """Parameter-count grid: c_slot, c_surf, rigorous exponent."""
    rows = []
    for has_a in (False, True):
        a_range = [0] if not has_a else [0, 1, 2, 3, 4]
        for A in a_range:
            for B in range(0, 9):
                for d in range(0, 4):
                    for e in range(0, 5):
                        cs = L.codim_slot(A, B, d, e, has_a)
                        rows.append({
                            "a_present": has_a, "A": (A if has_a else None),
                            "B": B, "d": d, "e": e,
                            "c_slot": cs,
                            "c_surf_monic_x": cs - d,
                            "c_surf_free_x": cs - (d + 1),
                            "rigorous_exponent_E_minus_B":
                                L.rigorous_upper_bound_exponent(A, B, d, e, has_a),
                        })
    zero_slot = [r for r in rows if r["c_slot"] == 0]
    zero_surf_monic = [r for r in rows if r["c_surf_monic_x"] == 0]
    zero_surf_free = [r for r in rows if r["c_surf_free_x"] == 0]
    neg_surf_free = [r for r in rows if r["c_surf_free_x"] < 0]
    # For each section shape (d, e): the largest surface family (max B) that still
    # has Theta(1) sections per surface, under each x convention.
    max_b = {}
    for d in range(0, 4):
        for e in range(0, 5):
            cand = [r for r in rows if r["d"] == d and r["e"] == e]
            free_ok = [r["B"] for r in cand if r["c_surf_free_x"] <= 0]
            monic_ok = [r["B"] for r in cand if r["c_surf_monic_x"] <= 0]
            slot_ok = [r["B"] for r in cand if r["c_slot"] <= 0]
            max_b[f"d={d},e={e}"] = {
                "max_B_c_surf_free_x_zero": max(free_ok) if free_ok else None,
                "max_B_c_surf_monic_x_zero": max(monic_ok) if monic_ok else None,
                "max_B_c_slot_zero": max(slot_ok) if slot_ok else None,
            }
    return {
        "max_B_at_codim_zero": max_b,
        "grid_size": len(rows),
        "grid": rows,
        "c_slot_zero_configs": zero_slot,
        "c_surf_zero_configs_monic_x": zero_surf_monic,
        "c_surf_zero_configs_free_x": zero_surf_free,
        "c_surf_negative_configs_free_x": neg_surf_free,
        "min_c_slot_with_nonconstant_section":
            min(r["c_slot"] for r in rows if r["e"] >= 1),
        "min_c_slot_overall": min(r["c_slot"] for r in rows),
    }


def arm_d_free_x_exact() -> list:
    rows = []
    for p in EXHAUSTIVE_SIZES + [101]:
        nh = L.n_hit_free_x(p)
        ns = L.n_slots_free_x(p)
        surfaces = (p - 1) * p**6
        rows.append({
            "p": p,
            "N_hit_free_x": nh,
            "N_slots_free_x": ns,
            "P_slot_free_x_float": nh / ns,
            "P_slot_free_x_times_2p3": nh / ns * 2 * p**3,
            "mean_hit_slots_per_surface_free_x": nh / surfaces,
        })
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", default="RUN-XEDN-002-A")
    args = ap.parse_args()

    started = dt.datetime.now(dt.timezone.utc).isoformat()
    t0 = time.time()
    frozen, digest = L.load_frozen()
    print(f"EXP-XEDN-002 arm A + arm D tables, run {args.run_id}")
    print(f"frozen predicate: experiments/EXP-XEDN-001/xedni_sections.py "
          f"sha256={digest}")
    print()

    print("== derivation self-checks (direct enumeration of the counting steps) ==")
    checks = [check_counting_steps(p, frozen) for p in (5, 7)]
    for c in checks:
        print(f"  p={c['p']}: step1 bijection {c['step1_bijection_holds']}, "
              f"step2 squarefree census {c['step2_all_agree']} "
              f"{ {k: v['brute_force'] for k, v in c['step2_monic_squarefree'].items()} }")
    all_checks_ok = all(c["step1_bijection_holds"] and c["step2_all_agree"]
                        for c in checks)
    print(f"  all derivation self-checks pass: {all_checks_ok}")
    print()

    print("== arm A: q_pred(p) assembled from strata vs closed form ==")
    strata = {}
    for p in ALL_SIZES:
        parts = L.q_pred_by_parts(p)
        strata[p] = parts
        assert parts["total_f"] == L.q_pred(p), p
        print(f"  p={p:4d} strata_total_f={parts['total_f']:>18d} "
              f"closed_form={L.q_pred(p):>18d} agree=True")
    print()

    rows = arm_a_table()
    print("== arm A: exact P_lift (frozen predicate semantics) ==")
    print(f"{'p':>5} {'N_slots':>22} {'N_hit':>18} {'P_lift (exact)':>34} "
          f"{'P_lift':>12} {'2p^3*P':>8}")
    for r in rows:
        print(f"{r['p']:>5} {r['N_slots']:>22} {r['N_hit']:>18} "
              f"{r['P_lift_exact']:>34} {r['P_lift_float']:>12.6e} "
              f"{r['P_lift_times_2p3']:>8.5f}")
    print()

    a_all = alpha_table(ALL_SIZES, L.p_lift)
    a_con = alpha_table(CONTRACTED_SIZES, L.p_lift)
    print("== arm A: exact finite-size alpha_eff = -log(P2/P1)/log(p2/p1) ==")
    for r in a_all:
        tag = "contracted" if r["p1"] in CONTRACTED_SIZES else "exhaustive"
        print(f"  p={r['p1']:>4} -> {r['p2']:>4}  alpha_eff = {r['alpha_eff']:.6f} "
              f"({tag})")
    print(f"  limiting alpha (p -> infinity) = 3 exactly; "
          f"P_lift = (1/(2p^3))*(1 - 2/p + 0/p^2 + 1/p^3 + ...)")
    print()
    ols_con = ols_alpha(CONTRACTED_SIZES, L.p_lift)
    ols_all = ols_alpha(ALL_SIZES, L.p_lift)
    print(f"  OLS alpha over contracted sizes {CONTRACTED_SIZES}: "
          f"{ols_con['alpha_ols']:.6f} (max |resid| {ols_con['max_abs_residual']:.2e})")
    print(f"  OLS alpha over all sizes:        {ols_all['alpha_ols']:.6f} "
          f"(max |resid| {ols_all['max_abs_residual']:.2e})")
    print()

    print("== arm A variants (semantics differences, exact) ==")
    for r in rows:
        print(f"  p={r['p']:>4} frozen={r['P_lift_float']:.6e} "
              f"true_square={r['P_lift_true_square_float']:.6e} "
              f"with_y0={r['P_lift_with_y0_float']:.6e} "
              f"frozen_false_negative_slots={r['frozen_false_negative_slots']}")
    print()

    print("== arm D: exact free-(non-monic)-x corroboration (OUTSIDE frozen slots) ==")
    freex = arm_d_free_x_exact()
    for r in freex:
        print(f"  p={r['p']:>4} P_slot={r['P_slot_free_x_float']:.6e} "
              f"2p^3*P_slot={r['P_slot_free_x_times_2p3']:.5f} "
              f"mean_sections_per_surface={r['mean_hit_slots_per_surface_free_x']:.6f}")
    print()

    grid = arm_d_grid()
    print("== arm D: parameter-count grid ==")
    print(f"  configurations examined: {grid['grid_size']}")
    print(f"  min c_slot over all configurations: {grid['min_c_slot_overall']}")
    print(f"  min c_slot with a non-constant section (e >= 1): "
          f"{grid['min_c_slot_with_nonconstant_section']}")
    print(f"  c_slot = 0 configurations ({len(grid['c_slot_zero_configs'])}):")
    for r in grid["c_slot_zero_configs"]:
        print(f"    a_present={r['a_present']} A={r['A']} B={r['B']} d={r['d']} "
              f"e={r['e']}")
    print(f"  c_surf = 0 with MONIC x ({len(grid['c_surf_zero_configs_monic_x'])}):")
    for r in grid["c_surf_zero_configs_monic_x"]:
        print(f"    a_present={r['a_present']} A={r['A']} B={r['B']} d={r['d']} "
              f"e={r['e']}")
    print(f"  c_surf = 0 with FREE x of degree <= d "
          f"({len(grid['c_surf_zero_configs_free_x'])} configs); "
          f"minimal-B examples:")
    seen = set()
    for r in sorted(grid["c_surf_zero_configs_free_x"],
                    key=lambda r: (r["d"], r["e"], r["B"])):
        key = (r["d"], r["e"])
        if key in seen:
            continue
        seen.add(key)
        print(f"    a_present={r['a_present']} A={r['A']} B={r['B']} d={r['d']} "
              f"e={r['e']}  (c_slot={r['c_slot']})")
    print("  largest surface family (max B) still at codimension 0, by section shape:")
    print(f"    {'shape':>12} {'max B: c_slot=0':>16} {'c_surf monic x':>16} "
          f"{'c_surf free x':>15}")
    for shape, v in grid["max_B_at_codim_zero"].items():
        print(f"    {shape:>12} {str(v['max_B_c_slot_zero']):>16} "
              f"{str(v['max_B_c_surf_monic_x_zero']):>16} "
              f"{str(v['max_B_c_surf_free_x_zero']):>15}")
    print()
    frozen_cfg = {
        "a_present": False, "B": 6, "d": 2, "e": 3,
        "c_slot": L.codim_slot(0, 6, 2, 3, has_a=False),
        "c_surf_monic_x": L.codim_surface(0, 6, 2, 3, 2, has_a=False),
        "c_surf_free_x": L.codim_surface(0, 6, 2, 3, 3, has_a=False),
        "rigorous_exponent": L.rigorous_upper_bound_exponent(0, 6, 2, 3, has_a=False),
    }
    full_res_cfg = {
        "a_present": True, "A": 4, "B": 6, "d": 2, "e": 3,
        "c_slot": L.codim_slot(4, 6, 2, 3, has_a=True),
        "c_surf_monic_x": L.codim_surface(4, 6, 2, 3, 2, has_a=True),
        "c_surf_free_x": L.codim_surface(4, 6, 2, 3, 3, has_a=True),
    }
    const_cfg = {
        "a_present": True, "A": 1, "B": 1, "d": 0, "e": 0,
        "c_slot": L.codim_slot(1, 1, 0, 0, has_a=True),
        "c_surf_free_x": L.codim_surface(1, 1, 0, 0, 1, has_a=True),
    }
    print(f"  frozen configuration (a=0, B=6, monic d=2, e=3): {frozen_cfg}")
    print(f"  full rational-elliptic-surface shape (A=4, B=6, d=2, e=3): "
          f"{full_res_cfg}")
    print(f"  EXP-XEDN-001 part-1 constant-section shape (A=1,B=1,d=0,e=0): "
          f"{const_cfg}  [harness measured rate 0.4915 ~ 1/2 = Theta(p^0)]")
    print()

    finished = dt.datetime.now(dt.timezone.utc).isoformat()
    wall = time.time() - t0

    raw = {
        "arm": "A+D",
        "frozen_predicate_sha256": digest,
        "predicate_semantics": (
            "frozen is_square_poly accepts f iff f is a nonzero perfect square of "
            "even degree whose square root is squarefree; f = 0 (the y = 0 section) "
            "is rejected"),
        "derivation_self_checks": checks,
        "derivation_self_checks_all_pass": all_checks_ok,
        "closed_forms": {
            "N_slots": "(p-1)*p^8",
            "N_hit": "p^2 * (p^4 - 3p^3 + 2p^2 + p - 1)/2",
            "P_lift": "(p^4 - 3p^3 + 2p^2 + p - 1) / (2*p^6*(p-1))",
            "N_hit_true_square": "p^2 * (p^4 - 2p^3 - 1)/2",
            "frozen_false_negatives": "p^2 * (p^3 - 2p^2 - p)/2",
            "N_hit_with_y0_section": "p^2 * ((p^4 - 3p^3 + 2p^2 + p - 1)/2 + 1)",
            "asymptotics": "P_lift = (1/(2 p^3)) * (1 - 2/p + 0/p^2 + 1/p^3 + O(p^-4))",
            "limiting_alpha": 3,
        },
        "strata_counts": {str(p): strata[p] for p in ALL_SIZES},
        "arm_a_table": rows,
        "alpha_eff_consecutive_all_sizes": a_all,
        "alpha_eff_consecutive_contracted": a_con,
        "alpha_ols_contracted": ols_con,
        "alpha_ols_all_sizes": ols_all,
        "limiting_alpha": 3,
        "arm_d_free_x_exact": freex,
        "arm_d_parameter_grid": grid,
        "arm_d_reference_configurations": {
            "frozen": frozen_cfg,
            "full_rational_elliptic_surface": full_res_cfg,
            "xedn001_part1_constant_sections": const_cfg,
        },
    }
    L.write_run_record(
        run_id=args.run_id,
        purpose=("Arm A closed-form exact lift-probability census for the frozen "
                 "EXP-XEDN-002 family plus the arm-D parameter-count tables"),
        entrypoint="experiments/EXP-XEDN-002/implementation/arm_a_closed_form.py",
        parameters={
            "field_bits": max(ALL_SIZES).bit_length(),
            "primes": ALL_SIZES,
            "surface_family": "y^2 = x^3 + b(t), deg b = 6",
            "section_shape": "x monic deg 2, y deg <= 3",
            "predicate": "EXP-XEDN-001 is_square_poly",
            "arms": ["A", "D"],
            "deterministic": True,
        },
        started_at=started, finished_at=finished, wall=wall,
        validity="valid",
        validity_reason=("deterministic exact arithmetic; both combinatorial steps of "
                         "the derivation were re-verified by direct enumeration at "
                         "p in {5,7}. This run supersedes RUN-XEDN-002-A, whose "
                         "measurements are identical (the script is deterministic and "
                         "unchanged) but whose manifest recorded an UNVERIFIED "
                         "inference.resolved_model string; the identifier here is "
                         "verified from the harness. RUN-XEDN-002-A is left in place, "
                         "unedited, and is marked invalid_record_metadata in "
                         "execution-report.yaml."),
        summary=(f"N_hit(p) = p^2*(p^4-3p^3+2p^2+p-1)/2 over N_slots(p) = (p-1)p^8; "
                 f"P_lift(101) = {float(L.p_lift(101)):.6e}, "
                 f"P_lift(809) = {float(L.p_lift(809)):.6e}, "
                 f"alpha_eff in [{min(r['alpha_eff'] for r in a_all):.4f}, "
                 f"{max(r['alpha_eff'] for r in a_all):.4f}], limiting alpha = 3"),
        raw=raw,
    )
    print(f"arm A/D complete in {wall:.2f}s; "
          f"peak_memory_mb={L.peak_memory_mb()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
