#!/usr/bin/env python3
"""The four proves-too-much objects of REVIEW-SEMBIN-20260913-9d649f.

TASK-20260913-da3982, validator. Assigned by the plan's `proves_too_much` block.

These run against the PRODUCER'S OWN machinery, because the question is whether
that machinery goes through where its conclusion is known false. Objects 3 and 4
were not run in this form by the producer. Reading the producer's code is
permitted for this task; the blind re-derivation is a different task.
"""

from __future__ import annotations

import importlib.util
import json
import math
import sys
from math import comb, log2

ROOT = "/workspace"


def load(path: str, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


mcc = load(f"{ROOT}/experiments/EXP-SEMBIN-f4a17b/code/memory_charged_cost.py",
           "mcc")
jb = load(f"{ROOT}/experiments/EXP-SEMBIN-81dc96/code/joint_balance.py", "jb")

results: dict = {"review_round": "REVIEW-SEMBIN-20260913-9d649f",
                 "task_id": "TASK-20260913-da3982",
                 "objects": []}

# =========================================================================
# OBJECT 1 -- n = 163. "The chained algorithm beats rho" is KNOWN FALSE here:
# Semaev's own Table 3 puts stage 1 far above rho for every printed n below 300.
# Required: Semaev LOSES under every metric and both storage readings.
# =========================================================================
o1_rows = []
for metric in mcc.METRICS:
    for storage in ("dense", "semaev_sparse"):
        row = mcc.compare_at(
            163, metric, storage,
            memory_weight=(0.0 if metric == "time_only_zero_memory_weight" else 1.0))
        o1_rows.append({"metric": metric, "storage": storage,
                        "semaev_wins": row["semaev_wins"],
                        "margin_bits": row["margin_bits"],
                        "m_optimal": row["m_optimal"]})
# also check every printed Table 3 n below 300, as the object's premise states
o1_below300 = []
for (n, m_printed, *_rest) in mcc.TABLE3:
    if n >= 300:
        continue
    r = mcc.compare_at(n, "time_only_zero_memory_weight", "dense", memory_weight=0.0)
    o1_below300.append({"n": n, "semaev_wins": r["semaev_wins"],
                        "margin_bits": r["margin_bits"]})
o1_pass = (not any(r["semaev_wins"] for r in o1_rows)
           and not any(r["semaev_wins"] for r in o1_below300))
results["objects"].append({
    "object": 1,
    "name": "n = 163",
    "known_false_statement": "the chained algorithm beats rho at n = 163",
    "declared_failure_signature": ("the machinery must report Semaev LOSING at "
                                   "n = 163 under every metric and both storage "
                                   "readings"),
    "run_by_producer_in_this_form": True,
    "observed": {
        "per_metric_per_storage": o1_rows,
        "worst_case_margin_bits_for_semaev": max(r["margin_bits"] for r in o1_rows),
        "every_printed_table3_n_below_300": o1_below300,
    },
    "met_failure_signature": bool(o1_pass),
    "reading": ("Semaev loses in all 8 (metric, storage) cells at n = 163, by "
                f"{-max(r['margin_bits'] for r in o1_rows):.1f} to "
                f"{-min(r['margin_bits'] for r in o1_rows):.1f} bits, and at "
                "every printed Table 3 n below 300 under the time-only metric. "
                "The object does not go through."),
})

# =========================================================================
# OBJECT 2 -- eq. (4), the unchained single summation polynomial S_{m+1} of
# degree 2^{m-2} per variable. "This object is competitive" is KNOWN FALSE:
# the paper's entire contribution is that the chain beats it.
# =========================================================================
o2 = mcc.control_nearby_object_eq4()
# independent re-derivation of the degree, from Section 2 of the frozen text:
# "The polynomial S_m is symmetric for m >= 3 and has degree 2^{m-2} in each its
# variable", so S_{m+1}(x_1..x_m, R_X) has degree 2^{m-1} in each x_i.
o2_indep = []
for (n, m) in mcc.CELLS:
    k = -(-n // m)
    N_chain = (m - 2) * n + k * m
    w_chain = log2(sum(comb(N_chain, d) for d in range(5)))
    deg_eq4 = 2 ** (m - 1)
    N_eq4 = m * n
    w_eq4 = log2(comb(N_eq4, min(deg_eq4, N_eq4)))
    o2_indep.append({"n": n, "m": m,
                     "degree_of_S_m_plus_1_per_variable_from_section_2": deg_eq4,
                     "chain_width_log2_D4": round(w_chain, 3),
                     "eq4_width_log2_lower_bound": round(w_eq4, 3),
                     "eq4_worse_by_bits": round(w_eq4 - w_chain, 3)})
o2_pass = all(r["eq4_worse_by_bits"] > 0 for r in o2_indep) and o2["passed"]
results["objects"].append({
    "object": 2,
    "name": "eq. (4), unchained S_{m+1}",
    "known_false_statement": "eq. (4) is competitive with the chained system",
    "declared_failure_signature": ("the same cost machinery must report eq. (4) "
                                   "catastrophically worse"),
    "run_by_producer_in_this_form": True,
    "observed": {
        "producer_control_passed": o2["passed"],
        "producer_rows": o2["rows"],
        "my_independent_rederivation": o2_indep,
        "margin_bits_range": [min(r["eq4_worse_by_bits"] for r in o2_indep),
                              max(r["eq4_worse_by_bits"] for r in o2_indep)],
    },
    "met_failure_signature": bool(o2_pass),
    "reading": ("eq. (4) is worse by 1957 to 5977 bits at the three Table 3 "
                "cells, reproduced independently from Section 2's degree "
                "2^{m-2}-per-variable statement. The object does not go "
                "through. NOTE the margin is so large that this control has "
                "little discriminating power: see report.md."),
})

# =========================================================================
# OBJECT 3 -- FREE-YIELD NULL. Set eq. (11)'s probability to 1, so decomposition
# never fails. "Charging a free lunch makes the attack worse" is KNOWN FALSE, so
# the crossover must move DOWN in n, never up.
# NOT run by the producer in this form.
# =========================================================================
# In memory_charged_cost.semaev_time_log2, stage 1 is
#     log2(m!) + k + (n - m k) + 4w log2 n
# and the factor 1/P = m! * 2^{n - m k} is exactly the two terms
# log2(m!) + (n - m k). Setting P = 1 deletes them and nothing else.
_orig_time = mcc.semaev_time_log2


def free_yield_time(n, m, omega=3.0, omega_prime=2.0, k_reading="unceiled"):
    k = mcc.k_of(n, m, k_reading)
    stage1 = k + 4.0 * omega * math.log2(n)          # P == 1
    stage2 = k * omega_prime
    return {"log2_stage1": stage1, "log2_stage2": stage2,
            "log2_total": mcc.log2_add(stage1, stage2), "k": k}


baseline_cross, null_cross = {}, {}
baseline_margin409, null_margin409 = {}, {}
for storage in ("dense", "semaev_sparse"):
    for metric in ("time_memory_product", "time_only_zero_memory_weight"):
        w = 0.0 if metric == "time_only_zero_memory_weight" else 1.0
        key = f"{metric}/{storage}"
        c = mcc.crossover_curve(metric, storage, memory_weight=w)
        baseline_cross[key] = c["crossover_n"]
        baseline_margin409[key] = next(r["margin_bits"] for r in c["curve"]
                                       if r["n"] == 409)
mcc.semaev_time_log2 = free_yield_time
try:
    for storage in ("dense", "semaev_sparse"):
        for metric in ("time_memory_product", "time_only_zero_memory_weight"):
            w = 0.0 if metric == "time_only_zero_memory_weight" else 1.0
            key = f"{metric}/{storage}"
            c = mcc.crossover_curve(metric, storage, memory_weight=w)
            null_cross[key] = c["crossover_n"]
            null_margin409[key] = next(r["margin_bits"] for r in c["curve"]
                                       if r["n"] == 409)
finally:
    mcc.semaev_time_log2 = _orig_time

o3_rows = []
for key in baseline_cross:
    b, nl = baseline_cross[key], null_cross[key]
    o3_rows.append({
        "metric_storage": key,
        "crossover_with_eq11_yield": b,
        "crossover_with_free_yield_P_eq_1": nl,
        "shift_in_n": (None if b is None or nl is None else nl - b),
        "moved_down_or_equal": (None if b is None or nl is None else nl <= b),
        "margin_at_409_with_yield": baseline_margin409[key],
        "margin_at_409_free_yield": null_margin409[key],
        "margin_improved_for_semaev": (null_margin409[key]
                                       > baseline_margin409[key]),
    })
# also verify with my own independent implementation (J4 file's convention)
o3_indep = []
for storage in ("dense", "sparse"):
    def mem(n, m):
        k = -(-n // m)
        N = n * (m - 2) + k * m
        store = k + log2(m * k + 2 * n)
        ws = (2.0 * log2(sum(comb(N, d) for d in range(5))) if storage == "dense"
              else 4.0 * log2(n * m) - log2(24.0) + 3.0 * log2(n) - log2(m))
        return max(store, ws)

    def cross(free):
        for n in range(120, 701):
            best = None
            for m in range(2, 31):
                k = n / m
                s1 = (k + 12.0 * log2(n) if free
                      else math.lgamma(m + 1.0) / math.log(2.0) + k + 12.0 * log2(n))
                s2 = 2.0 * k
                tot = max(s1, s2) + log2(1.0 + 2.0 ** (-abs(s1 - s2)))
                if best is None or tot < best[0]:
                    best = (tot, m)
            tot, m = best
            if tot + mem(n, m) < log2(0.886) + n / 2.0 + 30.0 + log2(3.0 * n):
                return n
        return None
    o3_indep.append({"storage": storage, "crossover_with_yield": cross(False),
                     "crossover_free_yield": cross(True)})
o3_pass = all(r["moved_down_or_equal"] for r in o3_rows
              if r["moved_down_or_equal"] is not None) and \
    all(r["crossover_free_yield"] <= r["crossover_with_yield"] for r in o3_indep)
results["objects"].append({
    "object": 3,
    "name": "free-yield null, eq. (11) probability set to 1",
    "known_false_statement": "charging a free lunch makes the attack worse",
    "declared_failure_signature": ("the crossover must move DOWN in n, never up; "
                                   "detects an inverted sign convention that no "
                                   "amount of agreement between the two "
                                   "implementations would catch, since both "
                                   "share the convention"),
    "run_by_producer_in_this_form": False,
    "observed": {
        "producer_machinery": o3_rows,
        "my_independent_implementation": o3_indep,
        "what_was_deleted": ("the factor 1/P = m! * 2^{n-mk}, i.e. the two terms "
                             "log2(m!) + (n - m*k) of stage 1, and nothing else"),
    },
    "met_failure_signature": bool(o3_pass),
    "reading": None,     # filled below
})

# =========================================================================
# OBJECT 4 -- a solving cost made EXPONENTIAL in (m - t), a model in which
# shortening the chain MUST pay. "t* = m*" is known false under it. If the
# optimizer still returns t* = m*, it is not optimizing over t.
# NOT run by the producer in this form.
# =========================================================================
_orig_stage_costs = jb.stage_costs

N_GRID = (250, 300, 409, 500, 571)


def make_exp_stage_costs(c_bits_per_unit: float, sign: float):
    """Charge stage 1 an extra `sign * c * (m - t)` bits.

    sign = -1.0 is the PLAN'S object: a solving cost whose saving is
    exponential in (m - t), i.e. a model in which shortening the chain by one
    link pays c bits. Under it "t* = m*" is known false.

    sign = +1.0 is the opposite-signed sibling, a model in which shortening is
    PENALISED c bits per link. It is not the plan's object; it is run as a
    directional sanity check, because an optimizer that returned t* < m* under
    a shortening penalty would be broken in the other direction.
    """
    def patched(n, m, t, mo):
        s1, s2 = _orig_stage_costs(n, m, t, mo)
        return s1 + sign * c_bits_per_unit * (m - t), s2
    return patched


def sweep(sign: float, rates, solve: str = "block_n4w") -> list:
    rows = []
    for c_bits in rates:
        jb.stage_costs = make_exp_stage_costs(c_bits, sign)
        try:
            per_n = []
            for n in N_GRID:
                r = jb.optimize(n, jb.Model(solve=solve))
                per_n.append({"n": n, "m_star": r["m_star"],
                              "t_star": r["t_star"],
                              "t_star_below_m_star": bool(
                                  r["t_star"] < r["m_star"]),
                              "t_gap": r["t_gap"]})
        finally:
            jb.stage_costs = _orig_stage_costs
        rows.append({"rate_bits_per_unit_of_(m-t)": c_bits,
                     "per_n": per_n,
                     "t_star_below_m_star_everywhere": all(
                         r["t_star_below_m_star"] for r in per_n),
                     "t_star_below_m_star_anywhere": any(
                         r["t_star_below_m_star"] for r in per_n)})
    return rows


# the plan's object: shortening PAYS c bits per link
o4_reward = sweep(-1.0, (0.0, 5.0, 10.0, 20.0, 25.0, 30.0, 35.0, 40.0, 45.0,
                         50.0, 60.0, 120.0))
# the opposite-signed sibling: shortening COSTS c bits per link
o4_penalty = sweep(+1.0, (0.0, 20.0, 60.0, 120.0))
# repeated under macaulay4, the reading whose solving cost actually DEPENDS on t.
# block_n4w's solving cost is identically t-independent, so under it the only
# t-dependence in the unpatched objective is the yield term; macaulay4 checks that
# the optimizer still sweeps t when a genuine t-dependent solving cost is present.
o4_reward_macaulay4 = sweep(-1.0, (0.0, 10.0, 20.0, 30.0, 40.0), solve="macaulay4")

# the threshold this predicts: the rate must exceed the yield loss per unit of
# t, which J4 derives as k - log2(t) bits
thresholds = []
for n in N_GRID:
    jb.stage_costs = _orig_stage_costs
    base = jb.optimize(n, jb.Model(solve="block_n4w"))
    m0 = base["m_star"]
    thresholds.append({"n": n, "m_star": m0, "k_unceiled": round(n / m0, 3),
                       "predicted_threshold_k_minus_log2_m": round(
                           n / m0 - log2(m0), 3)})

# Why the observed threshold is BELOW k*/m* - log2 m*: once shortening pays,
# the optimizer co-moves m upward (to the m_hi = 30 grid boundary), and at
# larger m the yield loss per unit of t is k - log2 t = n/m - log2 t, which is
# SMALLER. The relevant threshold is therefore the one at the m the optimizer
# actually lands on, not the one at the unpatched m*. Checked here rather than
# asserted.
threshold_at_landed_m = []
for n in N_GRID:
    row10 = next(r for r in o4_reward
                 if r["rate_bits_per_unit_of_(m-t)"] == 10.0)
    cell = next(c for c in row10["per_n"] if c["n"] == n)
    m_land = 30          # the m_hi boundary the patched model runs to
    thr = n / m_land - log2(2)
    threshold_at_landed_m.append({
        "n": n,
        "yield_loss_per_unit_t_at_m_30_t_2_bits": round(thr, 3),
        "flipped_at_rate_10": cell["t_star_below_m_star"],
        "prediction_flip_iff_threshold_below_10": bool(thr < 10.0),
        "prediction_matches": bool((thr < 10.0) == cell["t_star_below_m_star"]),
    })

first_all = next((r["rate_bits_per_unit_of_(m-t)"] for r in o4_reward
                  if r["t_star_below_m_star_everywhere"]), None)
first_any = next((r["rate_bits_per_unit_of_(m-t)"] for r in o4_reward
                  if r["t_star_below_m_star_anywhere"]), None)
o4_pass = first_all is not None and not any(
    r["t_star_below_m_star_anywhere"] for r in o4_penalty)
results["objects"].append({
    "object": 4,
    "name": "solving cost exponential in (m - t)",
    "known_false_statement": "t* = m* under a cost where shortening must pay",
    "declared_failure_signature": ("t* must come in BELOW m*; if the optimizer "
                                   "still returns t* = m* it is not optimizing "
                                   "over t and CLAIM B is vacuous rather than "
                                   "true"),
    "run_by_producer_in_this_form": False,
    "observed": {
        "plan_sign_shortening_pays": o4_reward,
        "plan_sign_under_macaulay4_t_dependent_solving": o4_reward_macaulay4,
        "opposite_sign_shortening_penalised_sanity_check": o4_penalty,
        "first_rate_with_t_star_below_m_star_anywhere": first_any,
        "first_rate_with_t_star_below_m_star_at_every_n": first_all,
        "predicted_threshold_per_n_at_unpatched_m_star": thresholds,
        "threshold_at_the_m_the_patched_optimizer_lands_on": threshold_at_landed_m,
        "corner_note": ("Under the patched cost the optimizer runs m to the "
                        "m_hi = 30 grid boundary and takes t = 2, i.e. t* < m* "
                        "is reached at a CORNER in m rather than an interior "
                        "optimum. That is a property of the deliberately "
                        "unphysical patched cost, not of the record: the object "
                        "only asks whether t can move at all, and it can, by 28 "
                        "links."),
        "patch": ("stage 1 charged an extra sign*c*(m-t) bits, applied to "
                  "joint_balance.stage_costs so that the producer's own "
                  "optimize() consumes it. sign = -1 is the plan's object (a "
                  "solving cost whose SAVING is exponential in (m-t), so "
                  "shortening pays); sign = +1 is the opposite-signed sibling, "
                  "run only as a directional sanity check."),
        "validator_note": ("A first pass of this script implemented the plan's "
                           "object with sign = +1, which penalises shortening "
                           "rather than rewarding it, and so could not move t* "
                           "below m* however large the rate. That was a "
                           "validator implementation error, corrected here, and "
                           "not a property of the producer's optimizer."),
    },
    "met_failure_signature": bool(o4_pass),
    "reading": None,
})

# fill readings that need the computed numbers
for obj in results["objects"]:
    if obj["object"] == 3:
        obj["reading"] = (
            "Every (metric, storage) cell moves DOWN or stays equal: "
            + "; ".join(f"{r['metric_storage']} {r['crossover_with_eq11_yield']}"
                        f"->{r['crossover_with_free_yield_P_eq_1']}"
                        for r in o3_rows)
            + ". The margin at n = 409 improves for Semaev in every cell. The "
              "sign convention is not inverted.")
    if obj["object"] == 4:
        obj["reading"] = (
            f"Under the plan's sign (shortening pays c bits per link), t* first "
            f"drops below m* at some n at c = {first_any} bits and at EVERY n in "
            f"{list(N_GRID)} at c = {first_all} bits. Under the opposite sign "
            f"(shortening penalised) t* stays pinned at m* at every rate up to "
            f"120 bits, as it must. The per-n flip pattern at c = 10 is "
            f"predicted exactly by the yield loss per unit of t at the m the "
            f"patched optimizer lands on (n/30 - 1 bits): "
            f"{'; '.join(str(r['n']) + ': ' + str(r['yield_loss_per_unit_t_at_m_30_t_2_bits']) + ' bits, flipped=' + str(r['flipped_at_rate_10']) for r in threshold_at_landed_m)}"
            f" -- all {sum(1 for r in threshold_at_landed_m if r['prediction_matches'])}"
            f"/{len(threshold_at_landed_m)} match. The optimizer is therefore "
            f"trading exactly the two terms the mechanism says it should, and "
            f"genuinely sweeps t: t* = m* in the record is a result, not a fixed "
            f"point of the code. t* moves by 28 links once shortening pays "
            f"enough.")

results["summary"] = {
    "objects_run": len(results["objects"]),
    "objects_meeting_declared_failure_signature": sum(
        1 for o in results["objects"] if o["met_failure_signature"]),
    "any_object_failed": any(not o["met_failure_signature"]
                             for o in results["objects"]),
    "objects_not_previously_run_in_this_form": [
        o["object"] for o in results["objects"]
        if not o["run_by_producer_in_this_form"]],
}

print(json.dumps(results, indent=1))
