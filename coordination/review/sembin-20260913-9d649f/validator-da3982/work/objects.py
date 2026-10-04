#!/usr/bin/env python3
"""The four proves-too-much objects of REVIEW-SEMBIN-20260913-9d649f.

Objects 1 and 2 re-execute the producer's machinery on objects whose answer is
known false in advance, plus an independent re-derivation for object 2.
Objects 3 and 4 are NEW: neither has been run in this form.

Nothing under experiments/ is modified.  Object 3 defines its own free-yield
time function; object 4 rebinds joint_balance.log2_solve_cost in memory only.
"""
import importlib.util
import json
import math
import sys

ROOT = "/workspace"


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


mc = load(f"{ROOT}/experiments/EXP-SEMBIN-f4a17b/code/memory_charged_cost.py",
          "mc")
jb = load(f"{ROOT}/experiments/EXP-SEMBIN-81dc96/code/joint_balance.py", "jb")

out = {}

# =========================================================================
# OBJECT 1 -- n = 163.  KNOWN FALSE: "the chained algorithm beats rho".
# Table 3 puts stage 1 far above 2^{n/2} for every printed n below 300.
# Required signature: Semaev LOSES under every metric and both readings.
# =========================================================================
o1 = {"object": "n = 163 (K-163/B-163)",
      "known_false_conclusion": "the chained algorithm beats parallel rho",
      "required_signature": "semaev_wins == False under all 4 metrics x 2 "
                            "storage readings",
      "cells": []}
for metric in mc.METRICS:
    for storage in ("dense", "semaev_sparse"):
        r = mc.compare_at(163, metric, storage)
        o1["cells"].append({"metric": metric, "storage": storage,
                            "semaev_wins": r["semaev_wins"],
                            "margin_bits": r["margin_bits"],
                            "m_optimal": r["m_optimal"]})
# and the same at every printed Table 3 n below 300, stage-1 only
o1["table3_below_300_stage1_vs_rho"] = []
for n, m, _rho, s1, _s2 in [(r[0], r[1], r[2], r[3], r[4]) for r in mc.TABLE3
                            if r[0] < 300]:
    o1["table3_below_300_stage1_vs_rho"].append(
        {"n": n, "printed_m": m,
         "log2_stage1_printed": round(math.log2(s1), 3),
         "log2_rho": n / 2.0,
         "semaev_loses_on_time_alone": math.log2(s1) > n / 2.0})
o1["passed"] = (all(not c["semaev_wins"] for c in o1["cells"])
                and all(r["semaev_loses_on_time_alone"]
                        for r in o1["table3_below_300_stage1_vs_rho"]))
out["object_1_n163"] = o1

# =========================================================================
# OBJECT 2 -- eq. (4), the unchained S_{m+1}.  KNOWN FALSE: "competitive".
# Independent derivation from the frozen text (Section 4.5): eq. (4) Weil-
# descends to n Boolean equations in m*k variables of total degree <= m(m-1),
# with first fall degree bounded by m^2 + 1 ([11], quoted in S4.5).  The chain
# solves at degree <= 4 in (m-2)n + km variables (Assumption 1).
# Required signature: eq. (4) catastrophically worse.
# =========================================================================
def width_log2(N, D):
    D = min(D, N)
    return math.log2(sum(math.comb(N, d) for d in range(D + 1)))


o2 = {"object": "eq. (4), the unchained single summation polynomial S_{m+1}",
      "known_false_conclusion": "eq. (4) is competitive with the chain",
      "required_signature": "eq. (4) far worse under the same machinery",
      "textual_basis": "S4.5: eq. (4) -> n Boolean equations in m*k variables, "
                       "total degree <= m(m-1), first fall degree <= m^2+1; "
                       "S2: S_m has degree 2^{m-2} in each variable",
      "independent_rows": []}
for n, m in [(163, 7), (233, 9), (283, 9), (310, 10), (409, 11), (571, 12)]:
    k = -(-n // m)
    N_chain = (m - 2) * n + k * m
    w_chain = width_log2(N_chain, 4)
    N_eq4 = m * k
    d_eq4 = m * m + 1                       # first fall degree bound from S4.5
    w_eq4 = width_log2(N_eq4, d_eq4)
    o2["independent_rows"].append({
        "n": n, "m": m, "chain_N": N_chain, "chain_width_log2": round(w_chain, 3),
        "eq4_N": N_eq4, "eq4_first_fall_degree_bound": d_eq4,
        "eq4_width_log2": round(w_eq4, 3),
        "eq4_minus_chain_width_log2_bits": round(w_eq4 - w_chain, 3),
        "eq4_time_minus_chain_time_bits_at_omega_3":
            round(3.0 * (w_eq4 - w_chain), 3),
        "eq4_dense_memory_minus_chain_bits": round(2.0 * (w_eq4 - w_chain), 3)})
o2["producer_control_reexecuted"] = mc.control_nearby_object_eq4()
o2["passed"] = all(r["eq4_minus_chain_width_log2_bits"] > 0
                   for r in o2["independent_rows"])
out["object_2_eq4"] = o2

# =========================================================================
# OBJECT 3 -- FREE-YIELD NULL.  NEW.  Set eq. (11)'s P to 1.
# KNOWN FALSE: "charging a free lunch makes the attack worse".
# Required signature: the crossover must move DOWN in n, never up.
#
# In eq. (15) the factor 1/P is exactly m! * 2^{n - mk} (S4.5.2 substitutes
# P ~ 2^{mk-n}/m!).  Deleting it leaves stage 1 = 2^k n^{4w}.
# =========================================================================
def free_yield_time_log2(n, m, omega=3.0, omega_prime=2.0,
                         k_reading="unceiled"):
    k = mc.k_of(n, m, k_reading)
    stage1 = k + 4.0 * omega * math.log2(n)          # 1/P removed
    stage2 = k * omega_prime
    return {"log2_stage1": stage1, "log2_stage2": stage2,
            "log2_total": mc.log2_add(stage1, stage2), "k": k}


def crossover_free_yield(metric, storage, m_policy, n_lo=150, n_hi=900):
    for n in range(n_lo, n_hi + 1):
        if m_policy == "reoptimised":
            m = min(range(2, min(30, n) + 1),
                    key=lambda mm: free_yield_time_log2(n, mm)["log2_stage1"])
        else:
            m = mc.semaev_optimal_m(n)               # eq. (11)'s own argmin
        t = free_yield_time_log2(n, m)
        mem = mc.semaev_memory_log2(n, m, 4, storage, "ceiled")
        base = mc.vow_log2(n)
        s = mc.metric_value(t["log2_total"], mem["log2_total_bits"], metric)
        b = mc.metric_value(base["log2_time_parallel"],
                            base["log2_memory_bits"], metric)
        if s < b:
            return n, m
    return None, None


o3 = {"object": "free-yield null: eq. (11)'s P set to 1 (decomposition never "
                "fails)",
      "known_false_conclusion": "charging a free lunch makes the attack worse",
      "required_signature": "crossover_n must DECREASE (or stay equal), never "
                            "increase, relative to the eq. (11) crossover",
      "detects": "an inverted sign convention shared by both implementations",
      "rows": []}
baseline_cross = {}
for metric in mc.METRICS:
    for storage in ("dense", "semaev_sparse"):
        ref = mc.crossover_curve(metric, storage, n_lo=150, n_hi=900)
        baseline_cross[(metric, storage)] = ref["crossover_n"]
        for pol in ("reoptimised", "eq11_argmin"):
            fn, fm = crossover_free_yield(metric, storage, pol)
            o3["rows"].append({
                "metric": metric, "storage": storage, "m_policy": pol,
                "crossover_eq11": ref["crossover_n"],
                "crossover_free_yield": fn,
                "moved_down_or_equal": (fn is not None
                                        and ref["crossover_n"] is not None
                                        and fn <= ref["crossover_n"]),
                "shift_in_n": (None if fn is None or ref["crossover_n"] is None
                               else fn - ref["crossover_n"]),
                "m_at_free_yield_crossover": fm})
o3["passed_claim_A"] = all(r["moved_down_or_equal"] for r in o3["rows"])

# the same null on the CLAIM B machinery, via its own yield_law switch
o3["claim_B"] = {}
for solve in ("macaulay4", "f4_std", "block_n4w"):
    eq11 = jb.crossover(jb.Model(solve=solve), n_lo=150, n_hi=900,
                        use_stage1_only=True)
    none = jb.crossover(jb.Model(solve=solve, yield_law="none"), n_lo=150,
                        n_hi=900, use_stage1_only=True)
    o3["claim_B"][solve] = {
        "crossover_eq11": eq11["crossover_n"],
        "crossover_free_yield": none["crossover_n"],
        "moved_down_or_equal": (none["crossover_n"] is not None
                               and eq11["crossover_n"] is not None
                               and none["crossover_n"] <= eq11["crossover_n"])}
o3["passed_claim_B"] = all(v["moved_down_or_equal"]
                           for v in o3["claim_B"].values())
o3["passed"] = o3["passed_claim_A"] and o3["passed_claim_B"]
out["object_3_free_yield"] = o3

# =========================================================================
# OBJECT 4 -- solving cost EXPONENTIAL in (m - t).  NEW.
# KNOWN FALSE under it: "t* = m*".  If the optimizer still returns t* = m* it
# is not optimizing over t and CLAIM B is vacuous.
# =========================================================================
o4 = {"object": "solving cost made exponential in (m - t)",
      "known_false_conclusion": "t* = m*",
      "required_signature": "t_star < m_star once the exponential rate exceeds "
                            "the yield loss per unit of t (~k - log2 t bits)",
      "rows": []}
_orig_solve = jb.log2_solve_cost


M_REF = {n: jb.optimize(n, jb.Model(solve="macaulay4"),
                        constrain_t_eq_m=True)["m_star"]
         for n in (283, 409, 571)}
o4["m_reference_from_t_eq_m_optimum"] = M_REF


def make_exp_solve(rate_multiplier):
    """log2 solve = base(t=m_ref) - rate*k*(m_ref - t): exponential in (m-t)."""
    def f(n, t, k, model, omega, degree=4):
        mr = M_REF.get(n, max(t, 2))
        base = _orig_solve(n, mr, k, model, omega, degree)
        return base - rate_multiplier * k * (mr - t)
    return f


for rate in (0.0, 0.25, 0.5, 0.9, 1.0, 1.5, 2.0):
    jb.log2_solve_cost = make_exp_solve(rate)
    try:
        rows = []
        for n in (283, 409, 571):
            r = jb.optimize(n, jb.Model(solve="macaulay4"))
            rows.append({"n": n, "m_star": r["m_star"], "t_star": r["t_star"],
                         "interior": r["is_optimum_interior"],
                         "t_gap": r["t_gap"]})
        o4["rows"].append({"exponential_rate_bits_per_unit_t":
                           f"{rate} * k", "results": rows,
                           "any_interior": any(x["interior"] for x in rows)})
    finally:
        jb.log2_solve_cost = _orig_solve
o4["optimizer_genuinely_sweeps_t"] = any(r["any_interior"] for r in o4["rows"])
o4["passed"] = o4["optimizer_genuinely_sweeps_t"]
out["object_4_exponential_solve"] = o4

# extra J4(c) evidence: the surface must actually vary with t
probe = jb.optimize(409, jb.Model(solve="macaulay4"))
srf = probe["surface"]
m0 = probe["m_star"]
o4["t_slice_at_m_star_n409"] = {f"t={t}": srf.get(f"{m0},{t}")
                               for t in range(2, m0 + 1)}
o4["distinct_costs_in_t_slice"] = len({srf.get(f"{m0},{t}")
                                       for t in range(2, m0 + 1)})

# extra: does the model reproduce the SIGN of the paper's own measured
# short-chain tradeoff at the Table 2 parameters where it was measured?
o4["table2_parameter_sanity"] = []
for n, m in ((15, 4), (15, 5), (16, 4), (19, 3), (21, 3)):
    mo = jb.Model(solve="macaulay4")
    costs = {t: jb.total_cost(n, m, t, mo) for t in range(2, m + 1)}
    best = min(costs, key=costs.get)
    o4["table2_parameter_sanity"].append(
        {"n": n, "m": m, "model_argmin_t": best,
         "model_says_short_chain_pays": best < m,
         "costs_log2": {t: round(c, 3) for t, c in costs.items()}})

print(json.dumps(out, indent=1))
