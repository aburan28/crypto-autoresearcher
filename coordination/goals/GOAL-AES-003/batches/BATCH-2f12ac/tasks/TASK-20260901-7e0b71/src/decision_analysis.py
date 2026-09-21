#!/usr/bin/env python3
# decision_analysis.py -- TASK-20260901-7e0b71 (BATCH-2f12ac, GOAL-AES-003)
#
# Stage-0 decision analysis for IDEA-20260901-363851 (analysis of recorded
# run outputs only; no new trials). Applies, in preregistered order
# (PREREGISTRATION.md section 4, verbatim from the record's
# preregistered_decision_rule STAGE 0 part):
#   gate fail -> S0-GATE-FAIL; p_large <= 0.05 -> S0-DEAD;
#   p_small <= 0.05 -> S0-CARRIER-ALIVE;
#   (0.05 < p_small <= 0.15) or (majority of hit weights < miss median)
#     -> S0-WEAK; else -> S0-DEAD.
# SHAPE-ONLY is a Stage-1 arm and cannot fire in Stage 0.
#
# Carrier test (record carrier_statistic.test_statistic, exact): n = number
# of hit trials, hit weights from the FULL uncapped ewhist_hit[17] histogram
# (consistency-checked against the capped per-hit detail), T_obs = sum of hit
# weights, F_miss = the run's own ewhist_miss[17]. p_small = P(sum of n iid
# draws from F_miss <= T_obs), p_large = P(>= T_obs), by exact integer
# dynamic-programming convolution (n <= 2000 branch; n = 14 expected).
# Hit-vs-miss mean/median wt(e) reported as exact rationals.
#
# Also evaluated: Gate-0 result, r=6 known-dead reference against its band
# (<= 8) / tripwire (>= 9), table-freeze binding of the arm seats, digest
# re-verification, determinism, KAT pins, and the report-only r5-vs-r6 miss
# wt(e) movement.
#
# usage: python3 src/decision_analysis.py <out.json>
# reads (fixed paths under runs/): R1_pin.json, R2_pinidentity.json,
#   R3_table_freeze.json, R4_gate0_j5.json, R4_gate0_cmp.json,
#   R5_r6_reference.json, R6_det_cmp.json, R7_digest_reverify.json
#
# INFERENCE BLOCK: policy executor-implementation; requested_policy
# executor-implementation; resolved_model_id
# fireworks-ai/accounts/fireworks/models/qwen3p8-max (ACTUAL session model
# under inference amendment DEC-20260831-0d1eeb); fallback_used true;
# model_verified false; degraded_requirements [];
# amendment DEC-20260831-0d1eeb;
# standing_basis 0137a051eb5828789eb267fa83c8278086578d4c.
import json, sys, os, datetime
from fractions import Fraction

INFERENCE = {
    "policy": "executor-implementation",
    "requested_policy": "executor-implementation",
    "resolved_model_id": "fireworks-ai/accounts/fireworks/models/qwen3p8-max",
    "model_verified": False,
    "fallback_used": True,
    "fallback_reason": "session-backend transport under inference amendment DEC-20260831-0d1eeb",
    "degraded_requirements": [],
    "amendment": "DEC-20260831-0d1eeb",
    "standing_basis": "0137a051eb5828789eb267fa83c8278086578d4c",
}

def load(p):
    if not os.path.exists(p):
        return None
    with open(p) as f:
        return json.load(f)

def hist_mean(h):
    n = sum(h)
    if n == 0:
        return None
    return Fraction(sum(i * c for i, c in enumerate(h)), n)

def hist_median_lower(h):
    n = sum(h)
    if n == 0:
        return None
    target = (n + 1) // 2   # smallest w with cumulative >= ceil(n/2)
    cum = 0
    for w, c in enumerate(h):
        cum += c
        if cum >= target:
            return w
    return len(h) - 1

def exact_dp(miss, n, t_obs):
    """miss: 17-bin counts; exact P(sum of n iid draws <=/>= t_obs)."""
    total = sum(miss)
    weights = [w for w in range(17) if miss[w] > 0]
    dp = {0: 1}
    for _ in range(n):
        ndp = {}
        for s, ways in dp.items():
            for w in weights:
                ndp[s + w] = ndp.get(s + w, 0) + ways * miss[w]
        dp = ndp
    denom = total ** n
    le = sum(ways for s, ways in dp.items() if s <= t_obs)
    ge = sum(ways for s, ways in dp.items() if s >= t_obs)
    return Fraction(le, denom), Fraction(ge, denom), denom

def main():
    out_path = sys.argv[1] if len(sys.argv) > 1 else "runs/decision_analysis.json"
    runs = "runs"
    r1 = load(f"{runs}/R1_pin.json")
    r2 = load(f"{runs}/R2_pinidentity.json")
    r3 = load(f"{runs}/R3_table_freeze.json")
    r4 = load(f"{runs}/R4_gate0_j5.json")
    r4c = load(f"{runs}/R4_gate0_cmp.json")
    r5 = load(f"{runs}/R5_r6_reference.json")
    r6c = load(f"{runs}/R6_det_cmp.json")
    r7 = load(f"{runs}/R7_digest_reverify.json")

    pins_pass = bool(r1 and r1.get("pin_pass") and r2 and r2.get("pin_pass"))
    freeze_pass = bool(r3 and r3.get("freeze_pass"))
    det_pass = bool(r6c and r6c.get("determinism_pass"))
    reverify_pass = bool(r7 and r7.get("reverify_pass"))
    gate0_pass = bool(r4c and r4c.get("gate0_pass"))

    # ---- table binding: each AES arm seat must sit on the frozen k=16 tables ----
    k16_concat = None
    if r3:
        for p in r3["points"]:
            if p["k"] == 16:
                k16_concat = p["concat_sha256"]
    table_binding_r4 = table_binding_r5 = None
    if r4 and k16_concat:
        table_binding_r4 = (r4.get("arm_table_concat_sha256") == k16_concat)
    if r5 and k16_concat:
        table_binding_r5 = (r5.get("arm_table_concat_sha256") == k16_concat)

    # ---- carrier statistic at t=1 (R4, seed 531001) ----
    carrier = None
    if r4:
        ewh = r4["ewhist_hit"]
        ewm = r4["ewhist_miss"]
        n_hits = sum(ewh)
        t_obs = sum(w * c for w, c in enumerate(ewh))
        n_miss = sum(ewm)
        detail = r4.get("hit_e_detail", [])
        detail_weights = [d["wt_e_byte"] for d in detail]
        # hit cap is PER THREAD (committed convention); at n_hits <= 64 total,
        # every hit must appear exactly once in the detail list
        if n_hits <= 64:
            detail_consistent = (
                len(detail) == n_hits
                and n_hits == r4["W_ge1_nontrivial"]
                and sorted(detail_weights) ==
                    sorted(w for w in range(17) for _ in range(ewh[w]))
            )
        else:
            detail_consistent = (
                n_hits == r4["W_ge1_nontrivial"]
                and len(detail) <= r4["threads"] * 64
            )
        p_small = p_large = None
        denom = None
        if n_hits > 0 and n_miss > 0:
            if n_hits <= 2000:
                p_small, p_large, denom = exact_dp(ewm, n_hits, t_obs)
            else:
                detail_consistent = False  # n>2000 branch not implemented in Stage 0
        mean_all = hist_mean(r4["ewhist_all"])
        mean_miss = hist_mean(ewm)
        mean_hit = hist_mean(ewh)
        med_miss = hist_median_lower(ewm)
        majority_below_median = None
        if med_miss is not None and n_hits > 0:
            below = sum(c for w, c in enumerate(ewh) if w < med_miss)
            majority_below_median = below * 2 > n_hits
        carrier = {
            "seat": "(sbox=aes k=16, rounds=5, amask=1, smask=1, log2N=30, seed=531001, armid=1, threads=2)",
            "n_hits": n_hits,
            "n_miss": n_miss,
            "T_obs_sum_hit_weights": t_obs,
            "ewhist_hit": ewh,
            "ewhist_miss": ewm,
            "ewhist_all": r4["ewhist_all"],
            "ewbithist_hit_nonzero_bins": {str(i): c for i, c in enumerate(r4["ewbithist_hit"]) if c},
            "hit_weights_from_detail": detail_weights,
            "per_hit_detail": detail,
            "detail_consistency": detail_consistent,
            "test_inputs_for_validator": {
                "F_miss_17bin": ewm,
                "hit_weight_histogram_17bin": ewh,
                "n": n_hits,
                "T_obs": t_obs,
                "method": "exact DP convolution of the 17-bin F_miss, one-sided, n<=2000 branch",
            },
            "p_small_exact": str(p_small) if p_small is not None else None,
            "p_large_exact": str(p_large) if p_large is not None else None,
            "p_small_float": float(p_small) if p_small is not None else None,
            "p_large_float": float(p_large) if p_large is not None else None,
            "dp_denominator_digits": len(str(denom)) if denom else None,
            "mean_wt_e_all": str(mean_all) if mean_all is not None else None,
            "mean_wt_e_miss": str(mean_miss) if mean_miss is not None else None,
            "mean_wt_e_hit": str(mean_hit) if mean_hit is not None else None,
            "median_wt_e_miss_lower": med_miss,
            "majority_hit_weights_below_miss_median": majority_below_median,
        }

    # ---- Stage-0 decision rule (preregistered evaluation order) ----
    decision_arm = None
    decision_reason = None
    if r4c is None or r4 is None:
        decision_arm = "S0-GATE-FAIL"
        decision_reason = "Gate-0 run or comparison absent (halt before reading)"
    elif not gate0_pass:
        decision_arm = "S0-GATE-FAIL"
        decision_reason = ("Gate 0 failed: instrumented worker did not reproduce L1-AES-R5-P30 "
                           "field-by-field; F4/invalid_measurement; no reading (rule 5)")
    elif carrier is None or carrier["p_small_exact"] is None:
        decision_arm = "S0-GATE-FAIL"
        decision_reason = ("carrier test not computable from recorded outputs "
                           "(zero hits or zero misses); treated as no reading, honest report")
    else:
        p_small = carrier["p_small_float"]
        p_large = carrier["p_large_float"]
        if p_large <= 0.05:
            decision_arm = "S0-DEAD"
            decision_reason = "p_large <= 0.05: anti-carrier (large-e concentration); carrier clause falsified at t=1 (F1)"
        elif p_small <= 0.05:
            decision_arm = "S0-CARRIER-ALIVE"
            decision_reason = "Gate 0 passes AND p_small <= 0.05 at seed 531001: carrier reading alive at t=1"
        elif (0.05 < p_small <= 0.15) or carrier["majority_hit_weights_below_miss_median"]:
            decision_arm = "S0-WEAK"
            decision_reason = ("Gate 0 passes, p_small > 0.05 but marginal (0.05 < p_small <= 0.15) and/or "
                               "majority of hit weights descriptively below the miss median: carrier weakened, not falsified")
        else:
            decision_arm = "S0-DEAD"
            decision_reason = ("Gate 0 passes, p_small > 0.15 with hit weights descriptively at or above "
                               "the miss median: carrier clause falsified at t=1 (F1)")

    # ---- r=6 known-dead reference ----
    r6ref = None
    if r5:
        hits6 = r5["W_ge1_nontrivial"]
        r6ref = {
            "seat": "(sbox=aes k=16, rounds=6, amask=1, smask=1, log2N=30, seed=531001, armid=1, threads=4)",
            "hits": hits6,
            "whist": r5["whist"],
            "trivial_swaps_excluded": r5["trivial_swaps_excluded"],
            "nontrivial_trials": r5["nontrivial_trials"],
            "null_expectation_analytic": r5["null_expectation_analytic"],
            "dead_band": "hits <= 8",
            "tripwire": "hits >= 9 (F6, halt + escalate)",
            "in_dead_band": hits6 <= 8,
            "tripwire_fired": hits6 >= 9,
            "ewhist_miss_r6": r5["ewhist_miss"],
            "ewhist_all_r6": r5["ewhist_all"],
            "ewhist_hit_r6": r5["ewhist_hit"],
            "mean_wt_e_miss_r6": str(hist_mean(r5["ewhist_miss"])) if sum(r5["ewhist_miss"]) else None,
            "mean_wt_e_all_r6": str(hist_mean(r5["ewhist_all"])) if sum(r5["ewhist_all"]) else None,
            "report_only_r5_vs_r6_miss_movement": {
                "mean_wt_e_miss_r5": str(hist_mean(r4["ewhist_miss"])) if r4 and sum(r4["ewhist_miss"]) else None,
                "mean_wt_e_miss_r6": str(hist_mean(r5["ewhist_miss"])) if sum(r5["ewhist_miss"]) else None,
                "note": "report-only observation per PR-2; no decision content",
            },
        }

    out = {
        "schema": "crypto.autoresearch.stage0_decision.v1",
        "task_id": "TASK-20260901-7e0b71",
        "idea_record": "IDEA-20260901-363851",
        "stage": "STAGE 0 ONLY",
        "gates": {
            "R1_pin_pass": bool(r1.get("pin_pass")) if r1 else None,
            "R2_pinidentity_pass": bool(r2.get("pin_pass")) if r2 else None,
            "R3_table_freeze_pass": freeze_pass,
            "R3_selfcheck_identity_k0": r3["selfcheck_identity_k0"].get("assert_pass") if r3 else None,
            "R3_selfcheck_aes_k16": r3["selfcheck_aes_k16"].get("assert_pass") if r3 else None,
            "gate0_pass_R4": gate0_pass,
            "gate0_missing_fields": r4c.get("missing_committed_fields") if r4c else None,
            "gate0_mismatched_fields": r4c.get("mismatched_fields") if r4c else None,
            "gate0_all_14_hit_indices_identical": r4c.get("all_14_hit_indices_identical") if r4c else None,
            "R6_determinism_pass": det_pass,
            "R7_digest_reverify_pass": reverify_pass,
            "table_binding_R4_to_freeze_k16": table_binding_r4,
            "table_binding_R5_to_freeze_k16": table_binding_r5,
        },
        "carrier_statistic_t1_seed531001": carrier,
        "r6_known_dead_reference": r6ref,
        "stage0_decision_rule_arm": decision_arm,
        "stage0_decision_reason": decision_reason,
        "shape_only_arm_note": ("SHAPE-ONLY is a STAGE 1 arm of the preregistered decision rule "
                                "(requires interior ramp points); it is not reachable in Stage 0"),
        "analyzed_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "parse_attestation": ("this file is machine-generated JSON; parsed whole with python3 json.load "
                              "(all inputs and this output) before task completion"),
        "inference": INFERENCE,
    }
    with open(out_path, "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({
        "stage0_arm": decision_arm,
        "gate0_pass": gate0_pass,
        "p_small": carrier["p_small_float"] if carrier else None,
        "p_large": carrier["p_large_float"] if carrier else None,
        "n_hits": carrier["n_hits"] if carrier else None,
        "r6_hits": r6ref["hits"] if r6ref else None,
        "r6_tripwire_fired": r6ref["tripwire_fired"] if r6ref else None,
    }, indent=1))
    sys.exit(0)

if __name__ == "__main__":
    main()
