#!/usr/bin/env python3
"""V2 independent recomputation for TASK-20260904-2bb29d (validator).

Written from the FROZEN formulas only:
  - H-PFDR-06fd60 statements (A), (B), (C)
  - experiments/EXP-PFDR-c04716/specification.yaml inputs.{cost_model,
    null_slice, bounded_slice, parameter_grid, hand_values_to_reproduce}
  - IDEA-20260903-dcf857 claim (A)-(D)
  - the attack plan of review_plan joint V2 in
    ledger/handoffs/TASK-20260904-2bb29d.yaml

NOTHING in experiments/EXP-PFDR-c04716/runs/STATIC-001/ was read before this
file was written and executed:  not cost_table.py, not the emitted YAML,
not execution-report.md.  Only the handoff's verbatim quotation of the
producer's observations (which the task card supplies) was seen.

Formulas implemented, verbatim from the plan:
  Ncols(n', D) = sum_{i <= D} binom(n', i)
  C(k)         = 2^k * Ncols(n - k, D(k))^omega
  null slice   D(k) = ceil((n - k + 2m)/2)
  bounded slice D(k) = min(D_0, d_reg(k))
  balance      s = (log2 m! + m + omega*log2 Ncols(n, D(0)) + log2 N)/(m+1)
               with n = round(m*s), iterated to a fixed point
  log2 T       = 1 + 2 s
  log2 memory  = s
  rho          = log2 0.886 + (log2 N)/2

Everything is exact integer arithmetic on binomials plus a real-valued
fixed-point iteration.  Standard library only.
"""

import json
import math
from fractions import Fraction

# ----------------------------------------------------------------- helpers


def ncols(nv, D):
    """sum_{i <= D} binom(nv, i); exact integer."""
    if D < 0:
        return 0
    D = min(D, nv)
    return sum(math.comb(nv, i) for i in range(D + 1))


def log2_int(x):
    if x <= 0:
        return float("-inf")
    return math.log2(x)


def d_reg_null(nv, m):
    """ceil((nv + 2m)/2) with nv = n - k residual variables."""
    return -((-(nv + 2 * m)) // 2)


def logC_null(n, k, m, omega):
    nv = n - k
    D = d_reg_null(nv, m)
    return k + omega * log2_int(ncols(nv, D))


def logC_bounded(n, k, m, omega, D0):
    nv = n - k
    D = min(D0, d_reg_null(nv, m))
    return k + omega * log2_int(ncols(nv, D))


def rho_log2(log2N):
    return math.log2(0.886) + log2N / 2.0


# ------------------------------------------------- (balance fixed point)


def balance(m, D0, omega, log2N, n_round="round", max_iter=200):
    """Iterate s = (log2 m! + m + omega log2 Ncols(n, D(0)) + log2N)/(m+1),
    n = round(m s), to a fixed point.  Returns (s, n, log2C, iters, cycle)."""
    const = math.log2(math.factorial(m)) + m + log2N
    s = log2N / (m + 1.0)          # C = 1 seed
    seen = {}
    for it in range(1, max_iter + 1):
        if n_round == "round":
            n = int(round(m * s))
        elif n_round == "ceil":
            n = math.ceil(m * s)
        else:
            n = int(m * s)
        D = min(D0, d_reg_null(n, m))
        logC = omega * log2_int(ncols(n, D))
        s_new = (const + logC) / (m + 1.0)
        if n in seen and abs(s_new - s) < 1e-12:
            return s_new, n, logC, it, False
        seen[n] = s_new
        if abs(s_new - s) < 1e-12:
            n2 = int(round(m * s_new))
            return s_new, n2, logC, it, False
        s = s_new
    # detect a 2-cycle in n
    n_a = int(round(m * s))
    return s, n_a, logC, max_iter, True


def cell(m, D0, omega, log2N):
    s, n, logC, iters, cyc = balance(m, D0, omega, log2N)
    return {
        "m": m, "D_0": D0, "omega": omega, "log2_N": log2N,
        "s": s, "n": n, "log2_C": logC,
        "log2_T": 1.0 + 2.0 * s, "log2_memory": s,
        "log2_rho": rho_log2(log2N),
        "gap_T_minus_rho": 1.0 + 2.0 * s - rho_log2(log2N),
        "iterations": iters, "cycled": cyc,
    }


# =========================================================== (a) null slice
out = {}

null_fixtures = []
for (m, s) in [(3, 6), (4, 8), (5, 8)]:
    n = m * s
    for omega in (2.0, 2.807):
        curve = [logC_null(n, k, m, omega) for k in range(0, n - s + 1)]
        diffs = [curve[i + 1] - curve[i] for i in range(len(curve) - 1)]
        argmin = min(range(len(curve)), key=lambda i: curve[i])
        # leaf charge per spec assumptions: B^{m-1} * 2^{m-1} roots
        leaf_charge = (m - 1) * s + (m - 1)
        null_fixtures.append({
            "m": m, "s": s, "n": n, "omega": omega,
            "k_max": n - s,
            "strictly_decreasing": all(d < 0 for d in diffs),
            "argmin_k": argmin,
            "argmin_is_leaf": argmin == n - s,
            "logC_at_0": curve[0], "logC_at_leaf": curve[-1],
            "max_step": max(diffs), "min_step": min(diffs),
            "leaf_root_finding_charge_log2": leaf_charge,
        })
out["a_null_slice_fixtures"] = null_fixtures

# enumerative balance exponent: C = B^{m-1} 2^{m-1}  -> slope of log2 T in log2 N
enum_slopes = []
for m in (3, 4, 5):
    pts = []
    for log2N in (128.0, 256.0, 512.0):
        # s = (log2 m! + m + (m-1)s + (m-1) + log2N)/(m+1)  -> closed form
        s = (math.log2(math.factorial(m)) + m + (m - 1) + log2N) / 2.0
        pts.append((log2N, 1.0 + 2.0 * s))
    slope = (pts[-1][1] - pts[0][1]) / (pts[-1][0] - pts[0][0])
    enum_slopes.append({"m": m, "slope_log2T_vs_log2N": slope, "points": pts})
out["a_enumerative_balance_slope"] = enum_slopes

# ================================================ (b) direct presentation
# residual degree ceil((r (B-1) + D_S)/2), D_S = m 2^{m-1}, dense columns
# binom(D + r, r); guessing one variable costs a factor B.
def direct_logC(m, k, B, omega):
    r = m - k
    D_S = m * 2 ** (m - 1)
    D = -((-(r * (B - 1) + D_S)) // 2)
    cols = math.comb(D + r, r)
    return k * math.log2(B) + omega * log2_int(cols)


direct = []
for m in (3, 4, 5):
    for omega in (2.0, 2.807):
        # argmin over k = 0..m-1 as a function of B
        argmins = {}
        for e in range(1, 9):
            B = 2 ** e
            vals = [direct_logC(m, k, B, omega) for k in range(0, m)]
            argmins[B] = min(range(len(vals)), key=lambda i: vals[i])
        # ratio C(m-2)/C(m-1) and its slope in log2 B around B = 2^20
        def logratio(e):
            return direct_logC(m, m - 2, 2 ** e, omega) - direct_logC(m, m - 1, 2 ** e, omega)
        lr20 = logratio(20)
        slope_central = (logratio(21) - logratio(19)) / 2.0
        slope_secant = lr20 / 20.0
        direct.append({
            "m": m, "omega": omega,
            "argmin_k_by_B": argmins,
            "argmin_k_at_B16": argmins[16],
            "log2_ratio_at_B_2e20": lr20,
            "slope_central_diff_at_2e20": slope_central,
            "slope_secant_over_log2B": slope_secant,
            "predicted_2omega_minus_1": 2 * omega - 1,
            "predicted_omega_minus_1": omega - 1,
        })
out["b_direct_presentation"] = direct

# =============================================== (c) balance limits C=1 / enum
limits = []
for m in (3, 4, 5):
    pts_c1 = []
    for log2N in (128.0, 256.0, 512.0):
        s = (math.log2(math.factorial(m)) + m + 0.0 + log2N) / (m + 1.0)
        pts_c1.append((log2N, 1.0 + 2.0 * s))
    slope_c1 = (pts_c1[-1][1] - pts_c1[0][1]) / (pts_c1[-1][0] - pts_c1[0][0])
    limits.append({
        "m": m,
        "C_eq_1_slope": slope_c1,
        "C_eq_1_predicted": 2.0 / (m + 1),
        "C_eq_Bm1_slope": [d["slope_log2T_vs_log2N"] for d in enum_slopes if d["m"] == m][0],
        "C_eq_Bm1_predicted": 1.0,
    })
out["c_balance_limits"] = limits

# ============================================ (d) the contract-listed cells
hand = [
    # (log2N, m, D_0, omega, hand log2 T, hand log2 memory or None, source)
    (256, 5, 4, 2.0, 108.7, 53.8, "spec inputs + H(D) + dcf857(D)"),
    (256, 5, 6, 2.0, 116.6, None, "spec inputs + H(D) + dcf857(D)"),
    (256, 5, 8, 2.0, 124.1, None, "spec inputs + H(D) + dcf857(D)"),
    (256, 5, 6, 2.807, 127.9, None, "spec inputs + H(D) + dcf857(D)"),
    (256, 4, 4, 2.0, 128.6, 63.8, "spec inputs + H(D) + dcf857(D)"),
    (256, 4, 8, 2.0, 146.8, None, "spec inputs + H(D) + dcf857(D)"),
    (128, 5, 4, 2.0, 64.0, None, "spec inputs + H(D) + dcf857(D)"),
    (64, 5, 4, 2.0, 40.9, None, "spec inputs + H(D) + dcf857(D)"),
]
hand_extra_H = [
    (256, 4, 4, 2.807, 138.0, None, "H(D) only"),
    (256, 4, 8, 2.807, 164.4, None, "H(D) only"),
    (256, 5, 4, 2.807, 116.6, 57.8, "H(D) only"),
    (256, 5, 8, 2.807, 139.0, None, "H(D) only"),
    (128, 5, 4, 2.807, 71.1, None, "H(D) only"),
]
hand_dcf_only = [
    (256, 4, 6, 2.0, 138.0, None, "dcf857(D) only"),
    (256, 4, 6, 2.807, 150.0, None, "dcf857(D) only, 'about 2^150'"),
    (128, 4, 4, 2.0, 75.0, None, "dcf857(D) only"),
    (128, 5, 8, 2.0, 77.7, None, "dcf857(D) only"),
]

def compare(rows):
    res = []
    for (log2N, m, D0, omega, hT, hM, src) in rows:
        c = cell(m, D0, omega, float(log2N))
        res.append({
            "log2_N": log2N, "m": m, "D_0": D0, "omega": omega,
            "hand_log2_T": hT, "my_log2_T": round(c["log2_T"], 4),
            "signed_disc_mine_minus_hand": round(c["log2_T"] - hT, 4),
            "hand_log2_memory": hM, "my_log2_memory": round(c["log2_memory"], 4),
            "my_log2_C": round(c["log2_C"], 4), "my_n": c["n"],
            "my_log2_rho": round(c["log2_rho"], 4),
            "beats_rho": c["log2_T"] < c["log2_rho"],
            "source_of_hand_value": src,
            "cycled": c["cycled"],
        })
    return res

out["d_contract_listed_cells"] = compare(hand)
out["d_hypothesis_D_extra_cells"] = compare(hand_extra_H)
out["d_dcf857_only_cells"] = compare(hand_dcf_only)

# the four claimed 'T < rho' cells
tlt = [(256, 5, 4, 2.0), (256, 5, 4, 2.807), (256, 5, 6, 2.0), (256, 5, 8, 2.0)]
out["d_T_lt_rho_claimed"] = [
    {**{k: v for k, v in cell(m, D0, om, float(N)).items()},
     "log2_T_rounded": round(cell(m, D0, om, float(N))["log2_T"], 4)}
    for (N, m, D0, om) in tlt
]

# ================================================== full 54-cell table
table = []
for log2N in (64.0, 128.0, 256.0):
    for m in (3, 4, 5):
        for D0 in (4, 6, 8):
            for omega in (2.0, 2.807):
                c = cell(m, D0, omega, log2N)
                c["beats_rho"] = c["log2_T"] < c["log2_rho"]
                # argmin of the bounded curve at the balanced (m, n)
                n = c["n"]
                curve = [logC_bounded(n, k, m, omega, D0) for k in range(0, n - int(round(c["s"])) + 1)]
                amin = min(range(len(curve)), key=lambda i: curve[i])
                c["bounded_argmin_k"] = amin
                c["bounded_k_max"] = len(curve) - 1
                c["bounded_logC_at_0"] = curve[0]
                c["bounded_logC_at_leaf"] = curve[-1]
                # leaf root-finding charge for comparison
                c["leaf_root_finding_charge_log2"] = (m - 1) * c["s"] + (m - 1)
                # null curve at this (m, n): monotone?
                ncurve = [logC_null(n, k, m, omega) for k in range(0, len(curve))]
                nd = [ncurve[i + 1] - ncurve[i] for i in range(len(ncurve) - 1)]
                c["null_curve_strictly_decreasing"] = all(d < 0 for d in nd)
                c["null_curve_argmin_is_leaf"] = (
                    min(range(len(ncurve)), key=lambda i: ncurve[i]) == len(ncurve) - 1)
                table.append(c)
out["table_54"] = table
out["table_54_summary"] = {
    "n_cells": len(table),
    "n_beats_rho": sum(1 for c in table if c["beats_rho"]),
    "beats_rho_cells": [
        {"log2_N": c["log2_N"], "m": c["m"], "D_0": c["D_0"], "omega": c["omega"],
         "log2_T": round(c["log2_T"], 4), "log2_rho": round(c["log2_rho"], 4),
         "log2_memory": round(c["log2_memory"], 4)}
        for c in table if c["beats_rho"]],
    "n_null_curves_strictly_decreasing": sum(
        1 for c in table if c["null_curve_strictly_decreasing"]),
    "n_null_argmin_leaf": sum(1 for c in table if c["null_curve_argmin_is_leaf"]),
    "n_bounded_argmin_0": sum(1 for c in table if c["bounded_argmin_k"] == 0),
    "bounded_argmin_not_0": [
        {"log2_N": c["log2_N"], "m": c["m"], "D_0": c["D_0"], "omega": c["omega"],
         "argmin_k": c["bounded_argmin_k"], "k_max": c["bounded_k_max"],
         "logC0": round(c["bounded_logC_at_0"], 4),
         "logCleaf": round(c["bounded_logC_at_leaf"], 4)}
        for c in table if c["bounded_argmin_k"] != 0],
}

# ================================================== (e) D_0 thresholds at 256
thresholds = []
for (m, omega) in [(5, 2.0), (5, 2.807), (4, 2.0)]:
    row = []
    for D0 in (2, 4, 6, 8, 10, 12, 14):
        c = cell(m, D0, omega, 256.0)
        row.append({"D_0": D0, "log2_T": round(c["log2_T"], 4),
                    "log2_rho": round(c["log2_rho"], 4),
                    "T_lt_rho": c["log2_T"] < c["log2_rho"]})
    # bracket: last D_0 with T < rho, first with T >= rho
    below = [r["D_0"] for r in row if r["T_lt_rho"]]
    above = [r["D_0"] for r in row if not r["T_lt_rho"]]
    thresholds.append({
        "m": m, "omega": omega, "rows": row,
        "largest_D0_below_rho": max(below) if below else None,
        "smallest_D0_at_or_above_rho": min(above) if above else None,
    })
out["e_thresholds_256"] = thresholds

# ================================================== (f) 18 bounded cells at 64
cells64 = []
for m in (3, 4, 5):
    for D0 in (4, 6, 8):
        for omega in (2.0, 2.807):
            c = cell(m, D0, omega, 64.0)
            cells64.append({
                "m": m, "D_0": D0, "omega": omega,
                "log2_T": round(c["log2_T"], 4),
                "log2_rho": round(c["log2_rho"], 4),
                "gap": round(c["log2_T"] - c["log2_rho"], 4),
                "n": c["n"], "s": round(c["s"], 4),
            })
out["f_64bit_cells"] = cells64
out["f_64bit_min_gap"] = min(cells64, key=lambda c: c["gap"])

# ================================================== P5 interior band
p5 = []
for m in (3, 4, 5):
    for D0 in (4, 6, 8):
        top = math.comb(2 * (D0 - m), D0) if 2 * (D0 - m) >= 0 else 0
        p5.append({
            "m": m, "D_0": D0,
            "residual_count_2_D0_minus_m": 2 * (D0 - m),
            "binom_2(D0-m)_D0": top,
            "is_zero": top == 0,
            "ncols_residual_full": ncols(max(2 * (D0 - m), 0), D0),
        })
out["p5_interior_band"] = p5
out["p5_zero_pairs"] = sum(1 for r in p5 if r["is_zero"])

# ================================================== k_c vs guessing range
kc = []
for c in table:
    n = c["n"]
    k_c = n - 2 * (c["D_0"] - c["m"])
    kmax = c["bounded_k_max"]
    kc.append({"log2_N": c["log2_N"], "m": c["m"], "D_0": c["D_0"],
               "omega": c["omega"], "n": n, "k_c": k_c, "k_max": kmax,
               "in_range": 0 <= k_c <= kmax})
out["p5_kc_in_range_count"] = sum(1 for r in kc if r["in_range"])
out["p5_kc_total"] = len(kc)

# ================================================== rounding sensitivity
sens = []
for (N, m, D0, om) in [(256, 5, 4, 2.0), (256, 5, 6, 2.0), (256, 4, 4, 2.0),
                       (256, 5, 8, 2.0), (256, 4, 6, 2.807)]:
    variants = {}
    for mode in ("round", "ceil", "floor"):
        s, n, logC, it, cyc = balance(m, D0, om, float(N), n_round=mode)
        variants[mode] = {"s": round(s, 4), "n": n,
                          "log2_T": round(1 + 2 * s, 4), "cycled": cyc}
    # 2^m filter placed inside C instead of in the balance constant:
    # identical by construction (both are additive in the numerator), record it
    sens.append({"log2_N": N, "m": m, "D_0": D0, "omega": om,
                 "n_rounding_variants": variants,
                 "spread_log2_T": round(
                     max(v["log2_T"] for v in variants.values())
                     - min(v["log2_T"] for v in variants.values()), 4)})
out["rounding_sensitivity"] = sens

print(json.dumps(out, indent=1, default=str))
