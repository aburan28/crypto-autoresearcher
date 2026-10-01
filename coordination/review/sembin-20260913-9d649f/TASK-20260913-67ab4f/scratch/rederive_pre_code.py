#!/usr/bin/env python3
"""Validator TASK-20260913-67ab4f -- re-derivations M1(1), M4(1), M5(4).

WRITTEN AND EXECUTED BEFORE OPENING code/surface_cost.py, code/sparse_independent.py
or experiments/EXP-SEMBIN-f4a17b/code/memory_charged_cost.py.

Sources used for the statements (all records, no code):
  - H-SEMBIN-97ea23 HEUR-VOW-CURVE: W = 0.886 * 2^{n/2}; T = W(1/M + 1/w);
    Mem = 3n max(w, M) bits.
  - inputs/SEMAEV-2015-310/tables.yaml Table 3 column formulas:
    stage1 = m! 2^{n/m} n^12 (omega = 3), stage2 = 2^{2n/m}; un-ceiled k = n/m
    in the exponents ("the paper's use of a non-integer n/m in place of
    k = ceil(n/m)"), which is the truncation convention I adopt for the time side.
  - COST-SEMBIN-8d123b: time = stage1 + stage2, baseline charged 0.886 * 2^{n/2};
    relation store 2^{ceil(n/m)} rows; memory readings dense (row-echelon,
    width^2 of the degree-<=4 Macaulay matrix) and sparse ((nm)^4/24 columns
    at n^3/m nonzeros per row, KN-LIT-e77232 comment 1).
  - tables.yaml derived_checks.f4_working_set: N = (m-2)n + km Boolean variables.
The per-row bit width of the relation store is NOT stated in any record I have
read; I evaluate three conventions (0, 2^k bits, 3n*2^k bits) and report which
reproduces the parent's published cells, so the choice is disclosed rather than
silently made.
"""
import json
import math
import os
from math import comb, factorial, log2

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rederive_pre_code.json")
LABELS = [163, 233, 283, 409, 571]
M_RANGE = range(2, 31)


def logadd2(a, b):
    if a == -math.inf:
        return b
    if b == -math.inf:
        return a
    hi, lo = max(a, b), min(a, b)
    return hi + log2(1.0 + 2.0 ** (lo - hi))


# ---------------------------------------------------------------- Semaev side
def stage1_log2(n, m, omega=3.0):
    return log2(factorial(m)) + n / m + 4 * omega * log2(n)


def stage2_log2(n, m):
    return 2.0 * n / m


def semaev_time_log2(n, m):
    return logadd2(stage1_log2(n, m), stage2_log2(n, m))


def stage1_argmin(n):
    return min(M_RANGE, key=lambda m: stage1_log2(n, m))


def k_ceil(n, m):
    return -(-n // m)


def n_vars(n, m):
    return (m - 2) * n + k_ceil(n, m) * m


def width_log2(n, m):
    N = n_vars(n, m)
    return log2(sum(comb(N, d) for d in range(0, 5)))


def relation_store_log2(n, m, conv):
    k = k_ceil(n, m)
    if conv == "none":
        return -math.inf
    if conv == "2^k_bits":
        return float(k)
    if conv == "3n_x_2^k_bits":
        return k + log2(3 * n)
    raise ValueError(conv)


def mem_dense_log2(n, m, conv):
    return logadd2(relation_store_log2(n, m, conv), 2.0 * width_log2(n, m))


def sparse_cols_log2(n, m):
    return 4 * log2(n * m) - log2(24)


def sparse_nnz_per_row_log2(n, m):
    return 3 * log2(n) - log2(m)


def mem_sparse_log2(n, m, conv):
    ws = sparse_cols_log2(n, m) + sparse_nnz_per_row_log2(n, m)
    return logadd2(relation_store_log2(n, m, conv), ws)


# ---------------------------------------------------------------- vOW side
LOG2_0886 = log2(0.886)


def vow_W_log2(n):
    return LOG2_0886 + n / 2.0


def vow_time_log2(n, M_log2, w_log2):
    # T = W (1/M + 1/w)
    return vow_W_log2(n) + logadd2(-M_log2, -w_log2)


def vow_mem_log2(n, M_log2, w_log2):
    return log2(3 * n) + max(M_log2, w_log2)


def vow_product_log2(n, M_log2, w_log2):
    return vow_time_log2(n, M_log2, w_log2) + vow_mem_log2(n, M_log2, w_log2)


def vow_product_min_log2(n):
    # 6 n W on the ray w = M
    return log2(6 * n) + vow_W_log2(n)


# ---------------------------------------------------------------- margins & crossovers
def margin(n, metric, reading, mode, conv, m_sel="stage1_argmin"):
    """Signed bits: baseline cost - Semaev cost. Positive = Semaev cheaper."""
    if m_sel == "stage1_argmin":
        m = stage1_argmin(n)
        t_s = semaev_time_log2(n, m)
        mem_s = (mem_dense_log2 if reading == "dense" else mem_sparse_log2)(n, m, conv)
    else:
        raise ValueError(m_sel)
    if mode == "record_point_M1_w30":
        M_log2, w_log2 = 0.0, 30.0
    elif mode == "own_curve_w_eq_M_eq_1":
        M_log2, w_log2 = 0.0, 0.0
    else:
        raise ValueError(mode)
    t_v = vow_time_log2(n, M_log2, w_log2)
    mem_v = vow_mem_log2(n, M_log2, w_log2)
    if metric == "time_only":
        return t_v - t_s
    if metric == "product":
        return (t_v + mem_v) - (t_s + mem_s)
    raise ValueError(metric)


def crossovers(margin_fn, n_lo=3, n_hi=700):
    """first crossing: smallest n with margin >= 0.
    persistent: smallest n such that margin >= 0 for every n' >= n in [n_lo, n_hi]."""
    ms = {n: margin_fn(n) for n in range(n_lo, n_hi + 1)}
    first = next((n for n in range(n_lo, n_hi + 1) if ms[n] >= 0), None)
    persistent = None
    for n in range(n_hi, n_lo - 1, -1):
        if ms[n] >= 0:
            persistent = n
        else:
            break
    # intervals where Semaev is cheaper
    intervals, start = [], None
    for n in range(n_lo, n_hi + 1):
        if ms[n] >= 0 and start is None:
            start = n
        if ms[n] < 0 and start is not None:
            intervals.append([start, n - 1])
            start = None
    if start is not None:
        intervals.append([start, n_hi])
    return {"first_crossing_n": first, "persistent_crossover_n": persistent,
            "semaev_cheaper_intervals": intervals}


out = {"note": __doc__}

# --- which relation-store convention reproduces the parent's published memory cells?
parent_cells = {163: (70.3526, 55.2782, 7), 233: (77.7467, 59.9741, 9), 283: (80.0103, 61.9374, 9),
                409: (86.8371, 66.5250, 11), 571: (91.7726, 70.2718, 12)}
conv_table = {}
for conv in ["none", "2^k_bits", "3n_x_2^k_bits"]:
    rows = {}
    for n, (pd, ps, pm) in parent_cells.items():
        m = stage1_argmin(n)
        rows[n] = {"argmin_m": m, "parent_m": pm,
                   "dense": round(mem_dense_log2(n, m, conv), 4), "parent_dense": pd,
                   "dense_delta": round(mem_dense_log2(n, m, conv) - pd, 5),
                   "sparse": round(mem_sparse_log2(n, m, conv), 4), "parent_sparse": ps,
                   "sparse_delta": round(mem_sparse_log2(n, m, conv) - ps, 5),
                   "semaev_time": round(semaev_time_log2(n, m), 4)}
    conv_table[conv] = rows
out["relation_store_convention_vs_parent_cells"] = conv_table
out["parent_semaev_time_log2"] = {163: 123.7697, 233: 138.7283, 283: 147.6495, 409: 166.5438, 571: 186.3070}

CONV = "3n_x_2^k_bits"  # decided from the table above; all label cells are width-dominated anyway

# --- M1(1): gate at record point, coherent crossovers, excess
gate = {}
for reading in ["dense", "sparse"]:
    for metric in ["time_only", "product"]:
        for mode in ["record_point_M1_w30", "own_curve_w_eq_M_eq_1"]:
            key = f"{metric}|{reading}|{mode}"
            fn = lambda n, metric=metric, reading=reading, mode=mode: margin(n, metric, reading, mode, CONV)
            c = crossovers(fn)
            c["margin_at_409_bits"] = round(fn(409), 4)
            c["margins_at_labels"] = {n: round(fn(n), 4) for n in LABELS}
            gate[key] = c
out["M1_gate_and_coherent"] = gate
out["M1_expected"] = {"record": {"time_only": 303, "product_dense": 435, "product_sparse": 375,
                                 "margins_409": {"time_only": 37.78, "dense": -8.79, "sparse": 11.52}},
                      "coherent": {"product_dense": 520, "product_sparse": 460,
                                   "margins_409": {"dense": -37.79, "sparse": -17.48}, "shift": 85}}

# excess of record charge over 6nW at labels, plus product invariance check
excess = {}
for n in LABELS:
    rec = vow_product_log2(n, 0.0, 30.0)
    mn = vow_product_min_log2(n)
    excess[n] = {"record_product_log2": round(rec, 6), "min_6nW_log2": round(mn, 6),
                 "excess_bits": round(rec - mn, 6)}
# invariance along w = M: check product equals 6nW for several M
inv = {M: round(vow_product_log2(409, M, M) - vow_product_min_log2(409), 12) for M in [0, 10, 13.3, 20, 30, 40]}
# and that the product is >= 6nW off the ray
off = {f"M=2^{M},w=2^{w}": round(vow_product_log2(409, M, w) - vow_product_min_log2(409), 6)
       for M, w in [(0, 30), (30, 0), (20, 30), (30, 20), (10, 40)]}
out["M1_vow_excess_and_invariance"] = {"excess_at_labels": excess, "product_minus_6nW_on_ray_w_eq_M": inv,
                                       "product_minus_6nW_off_ray": off}

# --- M4(1): Semaev cheapest memory over m at n = 409, both readings, each convention
m4 = {}
for conv in ["none", "2^k_bits", "3n_x_2^k_bits"]:
    tab = {}
    for reading, fn in [("dense", mem_dense_log2), ("sparse", mem_sparse_log2)]:
        vals = {m: round(fn(409, m, conv), 4) for m in M_RANGE}
        mstar = min(vals, key=vals.get)
        tab[reading] = {"cheapest_m": mstar, "cheapest_mem_log2": vals[mstar], "by_m": vals,
                        "semaev_time_at_cheapest_m": round(semaev_time_log2(409, mstar), 4)}
    m4[conv] = tab
out["M4_cheapest_memory_over_m_at_409"] = m4
out["M4_expected"] = {"band": [65.33, 80.07], "contract_predicted_cheapest_m": {"sparse": 8, "dense": 6},
                      "plan_mentions": "62.31 bits at m = 4 sparse (to be checked against the arm JSON)"}

# --- M4(2): hard-budget verdict at n = 409 as a function of budget b (bits), processors = 1.
# Baseline: w <= B/(3n), M = 1  -> T = W (1 + 1/w).  Two variants of the baseline time are
# reported: (i) w = B/(3n) (uses the whole budget); (ii) w = M = 1 (the coherent point), which
# always fits for B >= 3n.  Semaev: cheapest TIME over m subject to Mem(m) <= B; infeasible if none.
def hard_budget_verdict(n, b, reading, conv, baseline_variant):
    memf = mem_dense_log2 if reading == "dense" else mem_sparse_log2
    feas = [m for m in M_RANGE if memf(n, m, conv) <= b]
    if baseline_variant == "w_fills_budget":
        w_log2 = b - log2(3 * n)
        t_v = vow_time_log2(n, 0.0, max(w_log2, 0.0))
    elif baseline_variant == "w_eq_M_eq_1":
        t_v = vow_time_log2(n, 0.0, 0.0)
    elif baseline_variant == "M_eq_w_fills_budget":
        Mw = b - log2(3 * n)
        t_v = vow_time_log2(n, Mw, Mw)
    if not feas:
        return {"semaev_feasible": False, "verdict": "baseline", "t_v": round(t_v, 3)}
    m = min(feas, key=lambda m: semaev_time_log2(n, m))
    t_s = semaev_time_log2(n, m)
    return {"semaev_feasible": True, "m": m, "t_s": round(t_s, 3), "t_v": round(t_v, 3),
            "verdict": "semaev" if t_v - t_s >= 0 else "baseline"}


def flip_budget(n, reading, conv, variant, lo=20.0, hi=120.0, step=0.01):
    prev = None
    flips = []
    b = lo
    while b <= hi + 1e-9:
        v = hard_budget_verdict(n, b, reading, conv, variant)["verdict"]
        if prev is not None and v != prev:
            flips.append((round(b, 2), f"{prev}->{v}"))
        prev = v
        b += step
    return flips


hb = {}
for variant in ["w_fills_budget", "w_eq_M_eq_1", "M_eq_w_fills_budget"]:
    hb[variant] = {}
    for reading in ["dense", "sparse"]:
        hb[variant][reading] = {"flips_bits": flip_budget(409, reading, CONV, variant),
                               "at_grid": {b: hard_budget_verdict(409, b, reading, CONV, variant)["verdict"]
                                           for b in [30, 40, 50, 60, 64, 65, 70, 80, 89, 90]}}
out["M4_hard_budget_flips_at_409"] = hb

# --- M4(4): alpha flips at n = 409, record point, stage1 argmin
m = stage1_argmin(409)
t_s = semaev_time_log2(409, m)
t_v = vow_time_log2(409, 0.0, 30.0)
mem_v = vow_mem_log2(409, 0.0, 30.0)
alpha = {}
for reading, fn in [("dense", mem_dense_log2), ("sparse", mem_sparse_log2)]:
    mem_s = fn(409, m, CONV)
    # margin(alpha) = (t_v + alpha mem_v) - (t_s + alpha mem_s) = 0
    a = (t_v - t_s) / (mem_s - mem_v)
    alpha[reading] = {"alpha_flip": round(a, 4), "t_v": round(t_v, 4), "t_s": round(t_s, 4),
                      "mem_v": round(mem_v, 4), "mem_s": round(mem_s, 4), "in_0_1": 0 <= a <= 1}
# also at the coherent point (w = M = 1)
t_v1 = vow_time_log2(409, 0.0, 0.0)
mem_v1 = vow_mem_log2(409, 0.0, 0.0)
for reading, fn in [("dense", mem_dense_log2), ("sparse", mem_sparse_log2)]:
    mem_s = fn(409, m, CONV)
    a = (t_v1 - t_s) / (mem_s - mem_v1)
    alpha[reading + "_at_own_curve_w_eq_M_eq_1"] = {"alpha_flip": round(a, 4), "in_0_1": 0 <= a <= 1}
out["M4_alpha_flips_at_409"] = alpha
out["M4_alpha_expected"] = {"dense": 0.811, "sparse": 1.44}

# --- M5(4): sparse working set at n = 571, m = 12 from KN-LIT-e77232's statement
n, mm = 571, 12
cols = (n * mm) ** 4 / 24
nnz = n ** 3 / mm
out["M5_sparse_working_set_571_12"] = {
    "columns_(nm)^4/24": {"value": cols, "log2": round(log2(cols), 4)},
    "nonzeros_per_row_n^3/m": {"value": nnz, "log2": round(log2(nnz), 4)},
    "total_log2": round(log2(cols) + log2(nnz), 4),
    "exact_rational_check": {"cols_num_den": [(n * mm) ** 4, 24], "nnz_num_den": [n ** 3, mm],
                             "total_log2_exact": round(log2((n * mm) ** 4 * n ** 3) - log2(24 * mm), 6)},
    "expected": {"columns": 46.38, "nonzeros": 23.89, "total": 70.3, "parent_record_total": 70.2718},
    "also_at_labels_argmin_m": {nn: {"m": stage1_argmin(nn),
                                     "cols_log2": round(sparse_cols_log2(nn, stage1_argmin(nn)), 4),
                                     "nnz_log2": round(sparse_nnz_per_row_log2(nn, stage1_argmin(nn)), 4),
                                     "total_log2": round(sparse_cols_log2(nn, stage1_argmin(nn)) + sparse_nnz_per_row_log2(nn, stage1_argmin(nn)), 4)}
                                for nn in LABELS},
}

# --- Table 3 reproduction sanity (contract C2 target): argmin m at 310/409/571 and cell agreement
t3 = [(100, 6, 7.49e31, 1.08e10), (150, 7, 1.84e36, 7.96e12), (200, 8, 5.54e39, 1.12e15), (250, 9, 4.97e42, 5.29e16),
      (300, 10, 2.07e45, 1.15e18), (310, 10, 6.13e45, 4.61e18), (350, 10, 4.21e47, 1.18e21), (400, 11, 5.92e49, 7.81e21),
      (409, 11, 1.36e50, 2.43e22), (450, 11, 5.68e51, 4.26e24), (500, 12, 4.08e53, 1.21e25), (571, 12, 1.21e56, 4.44e28)]
t3out = []
worst = 0.0
for nn, mrow, s1, s2 in t3:
    mine1 = 2 ** stage1_log2(nn, mrow)
    mine2 = 2 ** stage2_log2(nn, mrow)
    r1, r2 = mine1 / s1 - 1, mine2 / s2 - 1
    worst = max(worst, abs(r1), abs(r2))
    t3out.append({"n": nn, "m": mrow, "argmin_m_mine": stage1_argmin(nn), "stage1_rel_err": round(r1, 5), "stage2_rel_err": round(r2, 5)})
out["table3_reproduction"] = {"rows": t3out, "worst_rel_err": round(worst, 5),
                              "time_only_stage1_vs_bare_2^(n/2)_crossover":
                                  crossovers(lambda n: n / 2 - stage1_log2(n, stage1_argmin(n)))}

with open(OUT, "w") as f:
    json.dump(out, f, indent=1, default=str)
print(json.dumps({k: out[k] for k in ["relation_store_convention_vs_parent_cells", "M1_gate_and_coherent",
                                      "M1_vow_excess_and_invariance", "M4_alpha_flips_at_409",
                                      "M5_sparse_working_set_571_12", "table3_reproduction"]}, indent=1, default=str))
print("M4 cheapest:", json.dumps({c: {r: {k: v for k, v in m4[c][r].items() if k != "by_m"} for r in m4[c]} for c in m4}, indent=1))
print("M4 hard budget flips:", json.dumps({v: {r: hb[v][r]["flips_bits"] for r in hb[v]} for v in hb}, indent=1))
print("wrote", OUT)
