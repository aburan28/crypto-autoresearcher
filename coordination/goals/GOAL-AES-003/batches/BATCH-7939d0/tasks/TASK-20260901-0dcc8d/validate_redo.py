#!/usr/bin/env python3
"""Validator fresh-code re-derivation for BATCH-7939d0 (TASK-20260901-0dcc8d).

Independent of producer code: statistics are recomputed from the raw
runs/*.json files only, using the frozen decision rule as stated in the
producers' preregistrations (BATCH-009 matched-exposure comparator machinery).
Writes rederived_stats.json next to this script.
"""
import json
import math
import os
from fractions import Fraction

import numpy as np
import scipy.stats as st

def native(o):
    if isinstance(o, dict):
        return {k: native(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [native(v) for v in o]
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    return o

ROOT = "/Volumes/SSD990/crypto-autoresearcher/.worktrees/aes003-batch015-20260831"
B793 = "coordination/goals/GOAL-AES-003/batches/BATCH-7939d0"
TA = os.path.join(B793, "tasks/TASK-20260901-92672b")   # producer A (round-count)
TB = os.path.join(B793, "tasks/TASK-20260901-47b21f")   # producer B (second seed)
B014_RUNS = "coordination/goals/GOAL-AES-003/batches/BATCH-014/tasks/TASK-20260805-b95720/runs"
B015_RUNS = "coordination/goals/GOAL-AES-003/batches/BATCH-015/tasks/TASK-20260805-d408ac/runs"
B015_RESULTS = "coordination/goals/GOAL-AES-003/batches/BATCH-015/tasks/TASK-20260805-d408ac/RESULTS.json"

def load(path):
    with open(os.path.join(ROOT, path)) as f:
        return json.load(f)

# ---------------- machinery (written fresh, from the rule statement) ----------------

def m_of(nontriv):
    """Analytic null expectation m = nontrivial_trials * 4 / 2^32."""
    return nontriv * 4.0 / 2.0**32

def garwood_ci(x, m, alpha=0.05):
    """Exact Garwood 95% Poisson CI on rate x/m."""
    lo = 0.0 if x == 0 else 0.5 * st.chi2.ppf(alpha / 2, 2 * x) / m
    hi = 0.5 * st.chi2.ppf(1 - alpha / 2, 2 * (x + 1)) / m
    return [lo, hi]

def exact_cond_binom(x_aes, x_sub, nt_aes, nt_sub):
    """Two-sided exact conditional-binomial test in exact rationals.
    n = x_aes + x_sub, p0 = m_aes/(m_aes+m_sub) = nt_aes/(nt_aes+nt_sub).
    p = min(1, 2*min(P[X >= x_aes], P[X <= x_aes])), X ~ Bin(n, p0)."""
    p0 = Fraction(nt_aes, nt_aes + nt_sub)
    n = x_aes + x_sub
    def pmf(i):
        return Fraction(math.comb(n, i)) * p0**i * (1 - p0) ** (n - i)
    p_ge = sum(pmf(i) for i in range(x_aes, n + 1))
    p_le = sum(pmf(i) for i in range(0, x_aes + 1))
    p = min(Fraction(1), 2 * min(p_ge, p_le))
    return float(p), p0

def cp_ratio_ci(x_aes, x_sub, m_aes, m_sub, alpha=0.05):
    """Clopper-Pearson CI on the AES share mapped to the rate-ratio CI
    with scale m_sub/m_aes. Returns (ratio_ci, cp_p_ci)."""
    n = x_aes + x_sub
    pL = 0.0 if x_aes == 0 else float(st.beta.ppf(alpha / 2, x_aes, n - x_aes + 1))
    pU = 1.0 if x_aes == n else float(st.beta.ppf(1 - alpha / 2, x_aes + 1, n - x_aes))
    scale = m_sub / m_aes
    def map_r(p):
        if p <= 0.0:
            return 0.0
        if p >= 1.0:
            return float("inf")
        return (p / (1.0 - p)) * scale
    return [map_r(pL), map_r(pU)], [pL, pU]

def comparison(x_aes, nt_aes, x_sub, nt_sub):
    m_aes, m_sub = m_of(nt_aes), m_of(nt_sub)
    p_val, p0 = exact_cond_binom(x_aes, x_sub, nt_aes, nt_sub)
    ratio_ci, cp_ci = cp_ratio_ci(x_aes, x_sub, m_aes, m_sub)
    g = garwood_ci(x_sub, m_sub)
    return {
        "x_aes": x_aes, "x_sub": x_sub,
        "m_aes": m_aes, "m_sub": m_sub,
        "nontriv_aes": nt_aes, "nontriv_sub": nt_sub,
        "n": x_aes + x_sub,
        "p0_exact": f"{p0.numerator}/{p0.denominator}",
        "p0_float": float(p0),
        "p_value": p_val,
        "cp_p_ci": cp_ci,
        "ratio_point": (float("inf") if x_sub == 0 else (x_aes / m_aes) / (x_sub / m_sub)),
        "ratio_ci": ratio_ci,
        "R_sub_point": x_sub / m_sub,
        "R_sub_garwood_95ci": g,
        "R_ci_contains_1": bool(g[0] <= 1.0 <= g[1]),
        "R_ci_lower_gt_1": bool(g[0] > 1.0),
    }

def rel_close(a, b, tol=1e-6):
    if isinstance(a, str) and a == "Infinity":
        a = float("inf")
    if isinstance(b, str) and b == "Infinity":
        b = float("inf")
    if math.isinf(a) or math.isinf(b):
        return a == b
    if a == b:
        return True
    denom = max(abs(a), abs(b))
    if denom == 0:
        return True
    return abs(a - b) / denom <= tol

def cmp_blocks(mine, theirs, fields):
    """Compare re-derived block to producer block field by field."""
    out = {}
    for f in fields:
        m, t = mine[f], theirs.get(f)
        if isinstance(m, list):
            ok = isinstance(t, list) and len(m) == len(t) and all(rel_close(x, y) for x, y in zip(m, t))
        elif isinstance(m, float) or isinstance(t, (int, float)) or t == "Infinity":
            ok = rel_close(m, t)
        else:
            ok = m == t
        out[f] = {"mine": (str(m) if math.isinf(m) else m) if isinstance(m, float) and math.isinf(m) else m,
                  "theirs": t, "match": bool(ok)}
    return out

FLOATY = ["m_aes", "m_sub", "p0_float", "p_value", "ratio_point", "R_sub_point"]
FIELDS = ["x_aes", "x_sub", "nontriv_aes", "nontriv_sub", "n", "p0_exact",
          "p0_float", "p_value", "cp_p_ci", "ratio_ci", "R_sub_point",
          "R_sub_garwood_95ci", "R_ci_contains_1", "R_ci_lower_gt_1"]

report = {"producers": {}}

# ============================ PRODUCER A: round-count ============================

frozen_b015 = load(B015_RESULTS)["frozen_comparator"]
aes_live_A = load(os.path.join(TA, "runs/AES-P30.json"))
arms_A = {r: load(os.path.join(TA, f"runs/F-R{r}-P30.json")) for r in (4, 8, 16, 32)}

pa = {"raw_hit_counts": {}, "comparisons": {}, "outcome_per_arm": {}, "self_check_machinery": {}}

# machinery self-check against the frozen record's published figures (EV-AES-e4c091 / BATCH-015 / BATCH-014)
sc = {}
c141 = comparison(14, 1073741824, 1, 1073741824)
sc["14_vs_1_p"] = {"mine": c141["p_value"], "published": 0.0009765625, "match": rel_close(c141["p_value"], 0.0009765625)}
sc["14_vs_1_ratio_ci"] = {"mine": c141["ratio_ci"], "published": [2.1300416502432444, 591.9684937326185],
                          "match": all(rel_close(a, b) for a, b in zip(c141["ratio_ci"], [2.1300416502432444, 591.9684937326185]))}
c140 = comparison(14, 1073741824, 0, 1073741823)
sc["14_vs_0_p"] = {"mine": c140["p_value"], "published": 0.0001220703125, "match": rel_close(c140["p_value"], 0.0001220703125)}
g1 = garwood_ci(1, 1.0)
sc["garwood_x1_m1"] = {"mine": g1, "published": [0.025, 5.572], "match": all(rel_close(a, b) for a, b in zip(g1, [0.025, 5.572]))}
g68 = garwood_ci(6, 8.0)
sc["garwood_x6_m8"] = {"mine": g68, "published": [0.275, 1.632], "match": all(rel_close(a, b) for a, b in zip(g68, [0.275, 1.632]))}
sc["all_pass"] = all(v["match"] for v in sc.values() if isinstance(v, dict) and "match" in v)
pa["self_check_machinery"] = sc

for r in (4, 8, 16, 32):
    arm = arms_A[r]
    pa["raw_hit_counts"][f"r={r}"] = {
        "W_ge1_nontrivial_raw_json": arm["W_ge1_nontrivial"],
        "nontrivial_trials_raw_json": arm["nontrivial_trials"],
        "len_hit_trials": len(arm["hit_trials"]),
        "hit_count_consistent": arm["W_ge1_nontrivial"] == len(arm["hit_trials"]),
        "feistel_rounds_actual": arm["feistel_rounds_actual"],
    }
    # vs frozen comparator (values taken ONLY from BATCH-015's frozen_comparator block)
    mine_frozen = comparison(frozen_b015["W_ge1_nontrivial"], frozen_b015["nontrivial_trials"],
                             arm["W_ge1_nontrivial"], arm["nontrivial_trials"])
    # vs live AES arm (raw json)
    mine_live = comparison(aes_live_A["W_ge1_nontrivial"], aes_live_A["nontrivial_trials"],
                           arm["W_ge1_nontrivial"], arm["nontrivial_trials"])
    res_a = load(os.path.join(TA, "RESULTS.json"))["arms"][f"r={r}"]
    pa["comparisons"][f"r={r}"] = {
        "vs_frozen": cmp_blocks(mine_frozen, res_a["vs_frozen_r5_comparator"], FIELDS),
        "vs_live": cmp_blocks(mine_live, res_a["vs_live_AES-P30"], FIELDS),
        "R_point_raw_derived": mine_frozen["R_sub_point"],
        "R_point_results_json": res_a["vs_frozen_r5_comparator"]["R_sub_point"],
    }
    # preregistered per-arm rule: A' if CI contains 1 AND p < 0.01; B' if lower>1 AND p>=0.01; else C'
    g = mine_frozen["R_sub_garwood_95ci"]
    p = mine_frozen["p_value"]
    if g[0] <= 1.0 <= g[1] and p < 0.01:
        oc = "OUTCOME-A'"
    elif g[0] > 1.0 and p >= 0.01:
        oc = "OUTCOME-B'"
    else:
        oc = "OUTCOME-C'"
    pa["outcome_per_arm"][f"r={r}"] = {
        "rederved_outcome": oc,
        "results_json_outcome": res_a["per_arm_preregistered_outcome"],
        "match": oc == res_a["per_arm_preregistered_outcome"],
    }

xs = [arms_A[r]["W_ge1_nontrivial"] for r in (4, 8, 16, 32)]
Rs = [pa["comparisons"][f"r={r}"]["R_point_raw_derived"] for r in (4, 8, 16, 32)]
all_A = all(v["rederved_outcome"] == "OUTCOME-A'" for v in pa["outcome_per_arm"].values())
if all_A:
    task_outcome = "(a) ABSENCE-PERSISTS"   # preregistered edge-case rule: movement within absence reported, outcome stays (a)
elif (all(xs[i] <= xs[i + 1] for i in range(3)) or all(xs[i] >= xs[i + 1] for i in range(3))) and len(set(xs)) > 1:
    task_outcome = "(b) MONOTONIC-DECAY"
else:
    task_outcome = "(c) NON-MONOTONIC"
pa["task_level"] = {
    "x_sequence": xs, "R_sequence": Rs,
    "all_arms_outcome_A_prime": all_A,
    "task_outcome_rederved": task_outcome,
    "task_outcome_results_json": load(os.path.join(TA, "RESULTS.json"))["decision_rule_applied"]["task_level_outcome_realized"],
    "max_R": max(Rs), "argmax_R": f"r={[4,8,16,32][Rs.index(max(Rs))]}",
    "monotonic": all(xs[i] <= xs[i + 1] for i in range(3)) or all(xs[i] >= xs[i + 1] for i in range(3)),
}
report["producers"]["TASK-20260901-92672b"] = pa

# ============================ PRODUCER B: second seed ============================

aes_S2 = load(os.path.join(TB, "runs/AES-P30-S2.json"))
f16_S2 = load(os.path.join(TB, "runs/F16-P30-S2.json"))
res_b = load(os.path.join(TB, "RESULTS.json"))
pb = {"raw_hit_counts": {}, "comparisons": {}}

for name, arm in (("AES-P30-S2", aes_S2), ("F16-P30-S2", f16_S2)):
    pb["raw_hit_counts"][name] = {
        "W_ge1_nontrivial_raw_json": arm["W_ge1_nontrivial"],
        "nontrivial_trials_raw_json": arm["nontrivial_trials"],
        "len_hit_trials": len(arm["hit_trials"]),
        "hit_count_consistent": arm["W_ge1_nontrivial"] == len(arm["hit_trials"]),
        "seed": arm["seed"], "threads": arm["threads"],
    }
pb["thread_seeds_identical_across_arms"] = aes_S2["thread_seeds"] == f16_S2["thread_seeds"]
pb["thread_seeds"] = aes_S2["thread_seeds"]
pb["RESULTS_thread_seeds_claim"] = res_b["matched_stream_verification"]["thread_seeds"]
pb["thread_seeds_claim_match"] = aes_S2["thread_seeds"] == res_b["matched_stream_verification"]["thread_seeds"]

# primary matched comparison at S2
mine_match = comparison(aes_S2["W_ge1_nontrivial"], aes_S2["nontrivial_trials"],
                        f16_S2["W_ge1_nontrivial"], f16_S2["nontrivial_trials"])
theirs_match = res_b["primary_comparison_matched_2p30_at_S2"]
pb["comparisons"]["matched_S2"] = cmp_blocks(mine_match, theirs_match, FIELDS)

# secondary cross-anchor: frozen 531001 comparator vs F16-S2
mine_cross = comparison(frozen_b015["W_ge1_nontrivial"], frozen_b015["nontrivial_trials"],
                        f16_S2["W_ge1_nontrivial"], f16_S2["nontrivial_trials"])
theirs_cross = res_b["secondary_readings_non_decision"]["frozen_r5_531001_vs_F16_S2_cross_anchor"]
pb["comparisons"]["cross_anchor_frozen531001_vs_F16S2"] = cmp_blocks(
    mine_cross, {"x_aes": theirs_cross["x_frozen"], "x_sub": theirs_cross["x_sub"], "n": theirs_cross["n"],
                 "p0_exact": theirs_cross["p0_exact"], "p_value": theirs_cross["p_value"],
                 "cp_p_ci": theirs_cross["cp_p_ci"], "ratio_ci": theirs_cross["ratio_ci"],
                 "R_sub_garwood_95ci": theirs_cross["R_sub_garwood_95ci"],
                 "R_ci_contains_1": theirs_cross["R_sub_garwood_95ci_contains_1"]},
    ["x_aes", "x_sub", "n", "p0_exact", "p_value", "cp_p_ci", "ratio_ci", "R_sub_garwood_95ci", "R_ci_contains_1"])

# arms vs own analytic null
for name, arm in (("AES-P30-S2", aes_S2), ("F16-P30-S2", f16_S2)):
    m = m_of(arm["nontrivial_trials"])
    x = arm["W_ge1_nontrivial"]
    g = garwood_ci(x, m)
    key = "AES_S2_vs_own_null" if "AES" in name else "F16_S2_vs_own_null"
    theirs_own = res_b["secondary_readings_non_decision"][key]
    pb["comparisons"][f"own_null_{name}"] = {
        "x": {"mine": x, "theirs": theirs_own["x"], "match": x == theirs_own["x"]},
        "m_derived_from_nontriv": m, "m_theirs": theirs_own["m"],
        "m_match_rel1e-6": rel_close(m, theirs_own["m"]),
        "R_point_mine": x / m, "R_point_theirs": theirs_own["R_point"],
        "R_point_match": rel_close(x / m, theirs_own["R_point"]),
        "garwood_mine": g, "garwood_theirs": theirs_own["R_garwood_95ci"],
        "garwood_match": all(rel_close(a, b) for a, b in zip(g, theirs_own["R_garwood_95ci"])),
    }
# RESULTS.json null_reading blocks (headline claims)
for name, key in (("AES_P30_S2", "AES_P30_S2"), ("F16_P30_S2", "F16_P30_S2")):
    arm = aes_S2 if "AES" in name else f16_S2
    m = m_of(arm["nontrivial_trials"])
    x = arm["W_ge1_nontrivial"]
    g = garwood_ci(x, m)
    nr = res_b[key]["null_reading"]
    pb["comparisons"][f"results_null_reading_{name}"] = {
        "R_point_mine": x / m, "R_point_theirs": nr["rate_ratio_R_point"],
        "R_point_match": rel_close(x / m, nr["rate_ratio_R_point"]),
        "garwood_mine": g, "garwood_theirs": nr["R_garwood_95ci"],
        "garwood_match": all(rel_close(a, b) for a, b in zip(g, nr["R_garwood_95ci"])),
        "ci_contains_1_mine": g[0] <= 1.0 <= g[1], "ci_contains_1_theirs": nr["ci_contains_1"],
    }

# outcome under preregistered rule order (d)->(a)->(b)->(c); (d) not applicable (all arms completed)
gF = mine_match["R_sub_garwood_95ci"]
pM = mine_match["p_value"]
if gF[0] <= 1.0 <= gF[1] and pM < 0.01:
    oc_b = "(a) ABSENCE-PERSISTS at S2"
elif gF[0] > 1.0 and pM >= 0.01:
    oc_b = "(b) EXCESS-REAPPEARS at S2"
else:
    oc_b = "(c) MIXED/other"
pb["outcome"] = {
    "rederved": oc_b,
    "results_json": res_b["decision_rule_applied"]["result"],
    "match": oc_b.startswith("(a)") and res_b["decision_rule_applied"]["result"].startswith("OUTCOME (a)"),
    "rate_ratio_ci_lower_mine": mine_match["ratio_ci"][0],
    "rate_ratio_ci_lower_claimed": 4.667,
}
report["producers"]["TASK-20260901-47b21f"] = pb

report = native(report)
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "rederived_stats.json"), "w") as f:
    json.dump(report, f, indent=2)

# console summary
def allmatch(d):
    if isinstance(d, dict):
        if "match" in d and not isinstance(d["match"], dict):
            return [d["match"]]
        out = []
        for v in d.values():
            out.extend(allmatch(v))
        return out
    if isinstance(d, list):
        out = []
        for v in d:
            out.extend(allmatch(v))
        return out
    return []

for prod, blk in report["producers"].items():
    ms = allmatch(blk)
    print(prod, "checks:", len(ms), "mismatches:", ms.count(False))
print(json.dumps(report, indent=2)[:400])
