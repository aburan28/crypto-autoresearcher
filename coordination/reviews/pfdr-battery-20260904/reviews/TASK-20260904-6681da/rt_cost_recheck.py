#!/usr/bin/env python3
"""rt_cost_recheck.py -- RED TEAM derivation aid for TASK-20260904-6681da.

Re-derives, from the frozen formulas of H-PFDR-06fd60 (A)-(C) and the
contract inputs of EXP-PFDR-c04716, the quantities the review plan assigns to
joints R1-R4 and to the proves_too_much control, with the CORRECTED
digit-substituted generator degree

        delta(m, s) = m * min(2^(m-1), s)          (= m 2^(m-1) for s >= 2^(m-1))

measured independently in rt_degree_probe.py (total degree of S_{m+1} in the m
unknowns = 4, 12, 32, 80 at m = 2, 3, 4, 5) instead of the '2m' of
IDEA-20260830-84cdb7 claim (A) / H-PFDR-06fd60 (A).

Nothing here is an experiment.  Exact integer binomials plus the same
real-valued balance solver the package uses.  Standard library only.
Deterministic.
"""
import json
from math import comb, factorial, log2

OMEGAS = (2.0, 2.807)
MS = (3, 4, 5)
D0S = (4, 6, 8)
LOG2NS = (64, 128, 256)
RHO_CONST = 0.886


# ------------------------------------------------------------------ primitives
def ncols(nv, D):
    """# multilinear monomials of degree <= D in nv variables (0 if D < 0)."""
    if D < 0:
        return 0
    return sum(comb(nv, i) for i in range(0, min(D, nv) + 1))


def d_reg_pkg(nv, m):
    """the package's null degree: ceil((nv + 2m)/2)  [generator degree 2m]."""
    return -(-(nv + 2 * m) // 2)


def delta_true(m, s):
    """degree of the digit-substituted, multilinearly reduced generator."""
    return m * min(2 ** (m - 1), s)


def d_reg_corr(nv, m, s):
    """corrected null degree: ceil((nv + delta)/2)."""
    return -(-(nv + delta_true(m, s)) // 2)


def log2_rho(log2N):
    return log2(RHO_CONST) + log2N / 2.0


def balance(m, D0, omega, log2N, dreg, maxit=400):
    """s = (log2 m! + m + omega log2 Ncols(n, min(D0, dreg(n))) + log2 N)/(m+1),
    n = round(m s), iterated to a self-consistent fixed point (the package's
    solver, with the null degree function passed in)."""
    lm = log2(factorial(m))

    def s_of_n(n):
        D = min(D0, dreg(n, m, n // m if m else 1))
        return (lm + m + omega * log2(ncols(n, D)) + log2N) / (m + 1), D

    s = log2N / (m + 1)
    seen = set()
    for _ in range(maxit):
        n = int(round(m * s))
        if n in seen:
            break
        seen.add(n)
        s_new, D = s_of_n(n)
        if int(round(m * s_new)) == n:
            s = s_new
            break
        s = s_new
    n = int(round(m * s))
    s, D = s_of_n(n)
    return {"s": s, "n": n, "D_used": D, "log2T": 1.0 + 2.0 * s,
            "log2_mem": s, "log2_ncols": log2(ncols(n, D))}


def dreg_pkg_wrapper(n, m, s):
    return d_reg_pkg(n, m)


def dreg_corr_wrapper(n, m, s):
    # s here is n//m, the per-block digit count at the balanced point
    return -(-(n + delta_true(m, max(s, 1))) // 2)


out = {}

# =========================================================== R1
r1 = {"generator_degree_measured": {2: 4, 3: 12, 4: 32, 5: 80},
      "source": "rt_degree_probe.py (this task); m=3 value agrees with "
                "EXP-PFDR-5726af RUN-PFDR-5726af-htop (symbolic, sympy)",
      "package_degree_2m": {m: 2 * m for m in (2, 3, 4, 5)},
      "cells": [], "corrected_null_fixtures": [], "corrected_floor_cells": []}

# (a) reproduce the package's balanced cells, then report rows(D_0)
for log2N in LOG2NS:
    for m in MS:
        for D0 in D0S:
            for om in OMEGAS:
                b = balance(m, D0, om, log2N, dreg_pkg_wrapper)
                s_int = b["n"] / m
                dl = delta_true(m, int(round(s_int)))
                rows = ncols(b["n"], D0 - dl)
                r1["cells"].append({
                    "log2N": log2N, "m": m, "D_0": D0, "omega": om,
                    "s": round(b["s"], 4), "n": b["n"],
                    "log2T_package_model": round(b["log2T"], 4),
                    "rho": round(log2_rho(log2N), 4),
                    "delta_corrected": dl,
                    "D_0_minus_delta": D0 - dl,
                    "macaulay_rows_at_D_0": rows,
                    "columns_at_D_0": ncols(b["n"], D0),
                })

# (b) does F1 (null slice strictly decreasing, argmin at the leaf) survive the
#     corrected generator degree?
for (m, s) in ((3, 6), (4, 8), (5, 8)):
    for om in OMEGAS:
        n = m * s
        vals = []
        for k in range(0, n - s + 1):
            nv = n - k
            D = -(-(nv + delta_true(m, s)) // 2)
            vals.append(k + om * log2(ncols(nv, D)))
        ratios = [vals[i + 1] - vals[i] for i in range(len(vals) - 1)]
        leaf_rf = (n - s) + (m - 1)
        vals_leaf = vals[:-1] + [leaf_rf]
        r1["corrected_null_fixtures"].append({
            "m": m, "s": s, "n": n, "omega": om,
            "delta": delta_true(m, s),
            "strictly_decreasing": all(r < 0 for r in ratios),
            "argmin_formula_leaf": min(range(len(vals)), key=lambda i: vals[i]),
            "argmin_rootfinding_leaf": min(range(len(vals_leaf)),
                                           key=lambda i: vals_leaf[i]),
            "leaf_k": n - s,
            "max_log2_ratio": round(max(ratios), 4),
            "min_log2_ratio": round(min(ratios), 4),
        })

# (c) the corrected minimum admissible D_0.  Two floors:
#     F_A  D_0 = delta  (the smallest degree at which the Macaulay matrix has
#                        any row at all: exactly one, S~ itself)
#     F_B  D_0 = d_ff = m 2^(m-1) + floor((s - 2^(m-1))/2) + 1  (the first fall
#                        degree derived in IDEA-20260903-e1e38b (D4), i.e. the
#                        smallest degree at which the ideal acquires anything
#                        new at all)
for log2N in LOG2NS:
    for m in MS:
        for om in OMEGAS:
            e = 2 ** (m - 1)
            # F_A: D_0 = delta, self-consistent
            s = log2N / (m + 1)
            for _ in range(400):
                n = int(round(m * s))
                D0 = m * min(e, max(n // m, 1))
                s_new = (log2(factorial(m)) + m + om * log2(ncols(n, D0))
                         + log2N) / (m + 1)
                if abs(s_new - s) < 1e-9:
                    s = s_new
                    break
                s = s_new
            nA, sA = int(round(m * s)), s
            D0A = m * min(e, max(nA // m, 1))
            # F_B: D_0 = d_ff
            s = log2N / (m + 1)
            for _ in range(400):
                n = int(round(m * s))
                sb = max(n // m, 1)
                D0 = m * min(e, sb) + max((sb - e) // 2, 0) + 1
                s_new = (log2(factorial(m)) + m + om * log2(ncols(n, min(D0, -(-(n + m * min(e, sb)) // 2))))
                         + log2N) / (m + 1)
                if abs(s_new - s) < 1e-9:
                    s = s_new
                    break
                s = s_new
            nB, sB = int(round(m * s)), s
            sbB = max(nB // m, 1)
            D0B = m * min(e, sbB) + max((sbB - e) // 2, 0) + 1
            r1["corrected_floor_cells"].append({
                "log2N": log2N, "m": m, "omega": om,
                "rho": round(log2_rho(log2N), 4),
                "floor_A_D_0_equals_delta": {
                    "D_0": D0A, "n": nA, "s": round(sA, 3),
                    "log2T": round(1 + 2 * sA, 3),
                    "log2_ncols": round(log2(ncols(nA, D0A)), 3),
                    "rows_at_D_0": ncols(nA, D0A - D0A)},
                "floor_B_D_0_equals_d_ff": {
                    "D_0": D0B, "n": nB, "s": round(sB, 3),
                    "log2T": round(1 + 2 * sB, 3),
                    "log2_ncols": round(log2(ncols(nB, D0B)), 3),
                    "rows_at_D_0": ncols(nB, D0B - delta_true(m, sbB))},
            })
out["R1"] = r1

# =========================================================== R2
r2 = {"note": "rows(D) = Ncols(n, D - delta) is the count of multiples mu S~ "
              "whose reduced degree is guaranteed <= D; corank of that matrix "
              ">= Ncols(n, D) - Ncols(n, D - delta).",
      "cells": [], "min_D_for_determination": [], "closure_cost": []}
for (log2N, m, D0, om) in ((256, 5, 4, 2.0), (256, 5, 6, 2.0),
                           (256, 5, 8, 2.0), (256, 4, 4, 2.0),
                           (256, 3, 4, 2.0)):
    b = balance(m, D0, om, log2N, dreg_pkg_wrapper)
    n = b["n"]
    dl = delta_true(m, max(n // m, 1))
    r2["cells"].append({
        "log2N": log2N, "m": m, "D_0": D0, "omega": om, "n": n,
        "delta": dl,
        "cols": ncols(n, D0), "rows": ncols(n, D0 - dl),
        "corank_lower_bound": ncols(n, D0) - ncols(n, D0 - dl),
        "log2_corank_lower_bound": round(log2(max(ncols(n, D0)
                                                  - ncols(n, D0 - dl), 1)), 3),
    })
# smallest D with Ncols(n,D) - Ncols(n,D-delta) <= N_sol, for illustrative
# (n, delta) and N_sol in {1, m!, 2^m m!}
for (n, m) in ((30, 3), (60, 4), (100, 5), (269, 5)):
    dl = delta_true(m, max(n // m, 1))
    row = {"n": n, "m": m, "delta": dl}
    for nsol_name, nsol in (("1", 1), ("m!", factorial(m)),
                            ("2^m m!", 2 ** m * factorial(m))):
        D = 0
        while D <= n + dl + 2:
            if ncols(n, D) - ncols(n, D - dl) <= nsol:
                break
            D += 1
        row["min_D_for_N_sol_" + nsol_name] = D
    row["n_plus_delta_minus_1"] = n + dl - 1
    r2["min_D_for_determination"].append(row)
# closure reading: cost of ONE rank at the derived last fall degree
for (log2N, m) in ((256, 3), (256, 4), (256, 5)):
    for om in (2.0,):
        b = balance(m, 4, om, log2N, dreg_pkg_wrapper)  # package's balanced n
        n, s = b["n"], max(b["n"] // m, 1)
        e = 2 ** (m - 1)
        dff = m * min(e, s) + max((s - e) // 2, 0) + 1
        r2["closure_cost"].append({
            "log2N": log2N, "m": m, "omega": om,
            "n_at_package_balance": n, "s": s,
            "d_ff_derived_e1e38b": dff,
            "log2_Ncols_at_d_ff": round(log2(ncols(n, dff)), 2),
            "log2_cost_Ncols^omega": round(om * log2(ncols(n, dff)), 2),
            "log2_full_guessing_leaf_2^(n-s)": n - s,
            "log2_whole_cube_2^n": n,
        })
r2["m2_measured_d_lf"] = {
    "source": "EXP-PFDR-cbdefb analysis.md section C/H (m = 2, d = 2, "
              "p in {4099,16411,65537}, 40 draws/cell)",
    "s_to_d_lf": {1: None, 2: 5, 3: 5, 4: 6, 5: 6},
    "closed_form_4_plus_floor_s_over_2": {s: 4 + s // 2 for s in range(1, 7)},
    "delta_at_those_s": {s: delta_true(2, s) for s in range(1, 7)},
}
out["R2"] = r2

# =========================================================== R3
r3 = {"marginal_ratio": [], "interior_band": [], "A1_cells": []}
for D0 in D0S:
    for om in OMEGAS:
        cross = D0 / (1 - 2 ** (-1 / om))
        rows = []
        for nv in (int(cross) - 2, int(cross), int(cross) + 2, 100, 269):
            if nv <= D0:
                continue
            exact = log2(ncols(nv - 1, D0) ** 1) * om - om * log2(ncols(nv, D0)) + 1
            approx = 1 + om * log2(1 - D0 / nv)
            rows.append({"n_minus_k": nv,
                         "exact_log2_ratio": round(exact, 5),
                         "asymptotic_log2_ratio": round(approx, 5)})
        r3["marginal_ratio"].append({"D_0": D0, "omega": om,
                                     "predicted_crossing": round(cross, 3),
                                     "samples": rows})
for m in MS:
    for D0 in D0S:
        resid_pkg = 2 * (D0 - m)          # n - k_c with the package's delta=2m
        resid_corr = 2 * D0 - delta_true(m, 100)   # with the corrected delta
        r3["interior_band"].append({
            "m": m, "D_0": D0,
            "residual_vars_at_k_c_package_delta_2m": resid_pkg,
            "P5_top_binomial_binom(2(D_0-m),D_0)":
                (comb(resid_pkg, D0) if resid_pkg >= 0 else None),
            "correct_residual_column_count_Ncols(2(D_0-m),D_0)":
                (ncols(resid_pkg, D0) if resid_pkg >= 0 else None),
            "equals_2^(2(D_0-m))_when_D_0>=2(D_0-m)":
                (ncols(resid_pkg, D0) == 2 ** resid_pkg) if resid_pkg >= 0 else None,
            "residual_vars_at_k_c_corrected_delta": resid_corr,
            "k_c_in_range_corrected": resid_corr > 0,
        })
out["R3"] = r3

# =========================================================== proves_too_much
ptm = {"object_1_direct_presentation": [], "object_2_m2": [],
       "object_3_rows_zero": [], "object_4_D0_2": []}
# Object 1: the direct presentation (membership degree B) run through the SAME
# bounded-slice arithmetic.  Residual r = m - k variables, D(k) = D_0, dense
# column count binom(D_0 + r, r) (the package's own direct-presentation column
# count), leaf k = m-1 charged B^{m-1} 2^{m-1}; then the same balance.
for m in MS:
    for D0 in D0S:
        for om in OMEGAS:
            C0 = om * log2(comb(D0 + m, m))          # log2 C(0), k = 0
            for log2N in (256,):
                s = (log2(factorial(m)) + m + C0 + log2N) / (m + 1)
                ptm["object_1_direct_presentation"].append({
                    "log2N": log2N, "m": m, "D_0": D0, "omega": om,
                    "log2_C0": round(C0, 3),
                    "log2T": round(1 + 2 * s, 3),
                    "rho": round(log2_rho(log2N), 3),
                    "T_minus_rho": round(1 + 2 * s - log2_rho(log2N), 3),
                    "sub_rho_emitted": (1 + 2 * s) < log2_rho(log2N),
                    "B_at_balance_log2": round(s, 3),
                    "D_0_below_membership_degree_B": D0 < 2 ** s,
                })
# Object 2: m = 2, where the assembly exponent is 2/3 and 'beats rho' is known
# false
for D0 in D0S:
    for om in OMEGAS:
        for log2N in LOG2NS:
            b = balance(2, D0, om, log2N, dreg_pkg_wrapper)
            ptm["object_2_m2"].append({
                "log2N": log2N, "m": 2, "D_0": D0, "omega": om,
                "log2T": round(b["log2T"], 3),
                "rho": round(log2_rho(log2N), 3),
                "T_minus_rho": round(b["log2T"] - log2_rho(log2N), 3),
                "sub_rho_emitted": b["log2T"] < log2_rho(log2N),
                "delta": delta_true(2, max(b["n"] // 2, 1)),
                "rows_at_D_0": ncols(b["n"], D0 - delta_true(2, max(b["n"] // 2, 1))),
            })
# Object 3 / 4: cells whose Macaulay matrix has no rows, incl. D_0 = 2 at m = 4
for (log2N, m, D0, om) in ((256, 5, 4, 2.0), (256, 5, 6, 2.0),
                           (256, 5, 8, 2.0), (256, 4, 4, 2.0),
                           (256, 3, 4, 2.0)):
    b = balance(m, D0, om, log2N, dreg_pkg_wrapper)
    dl = delta_true(m, max(b["n"] // m, 1))
    ptm["object_3_rows_zero"].append({
        "log2N": log2N, "m": m, "D_0": D0, "omega": om,
        "delta": dl, "rows": ncols(b["n"], D0 - dl),
        "log2T_emitted": round(b["log2T"], 3),
        "rho": round(log2_rho(log2N), 3),
        "model_emitted_a_finite_cost_for_an_empty_matrix":
            ncols(b["n"], D0 - dl) == 0})
for m in (4, 5):
    for om in OMEGAS:
        b = balance(m, 2, om, 256, dreg_pkg_wrapper)
        dl = delta_true(m, max(b["n"] // m, 1))
        ptm["object_4_D0_2"].append({
            "log2N": 256, "m": m, "D_0": 2, "omega": om,
            "log2T": round(b["log2T"], 3), "rho": round(log2_rho(256), 3),
            "sub_rho": b["log2T"] < log2_rho(256),
            "delta": dl, "rows_at_D_0_2": ncols(b["n"], 2 - dl)})
out["proves_too_much"] = ptm

# =========================================================== R4
r4 = {"unit_conversion_flip": [], "solver_memory_vs_tabulated": []}
# any honest group-op -> field-op conversion factor 2^c with c >= 1 flips a cell
# whose T - rho is below c.
for (log2N, m, D0, om, Tminusrho) in ((256, 4, 4, 2.0, 0.9137),
                                      (256, 5, 6, 2.807, 0.2262),
                                      (128, 5, 4, 2.0, 0.2185),
                                      (256, 4, 6, 2.0, 10.248),
                                      (256, 4, 4, 2.807, 10.2189)):
    r4["unit_conversion_flip"].append({
        "log2N": log2N, "m": m, "D_0": D0, "omega": om,
        "T_minus_rho_as_tabulated": Tminusrho,
        "flips_if_group_op_costs_more_than_field_ops": round(2 ** Tminusrho, 3),
        "flips_under_any_conversion_ge_2_field_ops_per_group_op":
            2 ** Tminusrho <= 2.0,
    })
for (log2N, m, D0, om) in ((256, 5, 4, 2.0), (256, 5, 4, 2.807),
                           (256, 5, 6, 2.0), (256, 5, 8, 2.0)):
    b = balance(m, D0, om, log2N, dreg_pkg_wrapper)
    lc = log2(ncols(b["n"], min(D0, d_reg_pkg(b["n"], m))))
    r4["solver_memory_vs_tabulated"].append({
        "log2N": log2N, "m": m, "D_0": D0, "omega": om,
        "tabulated_memory_log2_B": round(b["log2_mem"], 3),
        "log2_Ncols_at_D_0": round(lc, 3),
        "dense_matrix_memory_log2_Ncols^2": round(2 * lc, 3),
        "matrix_exceeds_tabulated_memory": 2 * lc > b["log2_mem"],
    })
out["R4"] = r4

print(json.dumps(out, indent=1, default=str))
