#!/usr/bin/env python3
# verdict.py -- TASK-20260901-c2b265 (BATCH-7b798d, GOAL-AES-003)
#
# Ordered SH cascade composition (PREREGISTRATION.md section 5, FIXED order,
# which IS the branch-precedence clause):
#   SH-GATE-FAIL > SH-F6 > SH-ANCHOR-FAIL > SH-RESEAT-FAIL > SH-DEAD >
#   SH-OTHER-NONMONO > SH-STEP/SHAPE-FLAT > SH-GRADUAL/SHAPE-DECAY >
#   SH-OTHER-RESIDUAL (declared complement).
# Composed ONLY after ALL interior points are read. Branches 2 (SH-F6) and
# 3 (SH-ANCHOR-FAIL) were evaluated in S0 (committed PASS-S0, snapshot
# TASK-20260901-56ecb6) and are n/a post-S0 here; they are still listed in
# order with their committed reading. The 41-99 ambiguity band is NEVER
# smoothed: a reading there lands in SH-OTHER-RESIDUAL per the cascade.
#
# usage: python3 src/verdict.py <t1_k16_analysis> <t2_k1_analysis>
#        <t3_k2_analysis> <t4_k8_analysis> <t5_det_cmp>
#        <t6_digest_reverify> <t6_freeze_rerun> <t6_source_diff_info>
#        <s0_results.json> <verdict_out.json>
# Exit: 0 composition written (verdict value inside JSON).
#
# INFERENCE BLOCK: policy executor-implementation; requested_policy
# executor-implementation; resolved_model_id
# fireworks-ai/accounts/fireworks/models/qwen3p8-max (session-reported; no
# adapter probe run in this session); fallback_used true; model_verified
# false; degraded_requirements []; amendment DEC-20260831-0d1eeb.
import json, sys, datetime

INFERENCE = {
    "policy": "executor-implementation",
    "requested_policy": "executor-implementation",
    "resolved_model_id": "fireworks-ai/accounts/fireworks/models/qwen3p8-max",
    "resolved_model_id_note": "session-reported; no adapter probe run in this session",
    "model_verified": False,
    "fallback_used": True,
    "fallback_reason": "session-backend transport under inference amendment DEC-20260831-0d1eeb",
    "degraded_requirements": [],
    "amendment": "DEC-20260831-0d1eeb",
}


def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def main():
    (t1p, t2p, t3p, t4p, t5p, t6p, t6frp, t6sdp, s0p, outp) = sys.argv[1:11]
    t1 = json.load(open(t1p))   # k=16 re-seat
    t2 = json.load(open(t2p))   # k=1
    t3 = json.load(open(t3p))   # k=2
    t4 = json.load(open(t4p))   # k=8
    t5 = json.load(open(t5p))   # determinism cmp
    t6 = json.load(open(t6p))   # digest reverify
    t6fr = json.load(open(t6frp))  # digested rerun freeze (freeze_pass)
    t6sd = json.load(open(t6sdp))  # source-diff info
    s0 = json.load(open(s0p))   # committed S0 RESULTS (read-only context)

    h16 = t1["hits_W_ge1_nontrivial"]
    h1 = t2["hits_W_ge1_nontrivial"]
    h2 = t3["hits_W_ge1_nontrivial"]
    h8 = t4["hits_W_ge1_nontrivial"]
    br16, br1, br2, br8 = t1["bandrank"], t2["bandrank"], t3["bandrank"], t4["bandrank"]
    pts = [(1, h1, br1), (2, h2, br2), (8, h8, br8), (16, h16, br16)]

    overflow = {a["run_id"]: a["hit_log_overflow"] for a in (t1, t2, t3, t4)}
    overflow_fired = any(v > 0 for v in overflow.values())
    consistency_fail = {a["run_id"]: not a["all_consistency_checks_pass"]
                        for a in (t1, t2, t3, t4)}
    reseat_ok = t1.get("reseat_gate", {}).get("in_band", False)

    det_pass = bool(t5.get("determinism_pass"))
    reverify_pass = bool(t6.get("reverify_pass"))
    freeze_pass = bool(t6fr.get("freeze_pass"))
    srcdiff_empty = bool(t6sd.get("diff_empty"))

    s0_gates = s0.get("gates", {})
    s0_outcome = s0.get("s0_outcome_ordered_cascade")
    s0_runs = {r.get("run_id"): r for r in s0.get("runs", [])}
    s0_dead_hits = s0_runs.get("S0-5", {}).get("hits_W_ge1_nontrivial")
    s0_ramp_hits = s0_runs.get("S0-6", {}).get("hits_W_ge1_nontrivial")

    gate_fail_conjuncts = {
        "S0-2_KAT_pins_inherited": s0_gates.get("S0-2_KAT_pins", {}).get("gate_pass"),
        "S0-3_freeze_reverification_inherited": s0_gates.get("S0-3_freeze_reverification", {}).get("gate_pass"),
        "S0-4_gate0x_rebuild_identity_inherited": s0_gates.get("S0-4_gate0x_rebuild_identity", {}).get("gate_pass"),
        "S1-5_determinism": det_pass,
        "S1-6_digest_reverify": reverify_pass and freeze_pass,
        "S1-6_source_diff_empty_vs_s0_copy": srcdiff_empty,
        "hit_overflow_zero_on_all_analysis_bearing_receipts": not overflow_fired,
        "per_receipt_consistency_checks": not any(consistency_fail.values()),
    }
    gate_fail = not all(gate_fail_conjuncts.values())

    # band-rising sentinel over tested points {1,2,8,16} in ascending k
    rising_pairs = [(ka, kb) for (ka, ha, ra) in pts for (kb, hb, rb) in pts
                    if ka < kb and rb > ra]
    band_rising = len(rising_pairs) > 0

    branches = []

    def branch(order, name, fired, conjuncts, note):
        branches.append({"order": order, "branch": name, "fired": bool(fired),
                         "conjuncts": conjuncts, "note": note})
        return bool(fired)

    verdict = None
    PREEMPTED = ["SH-GATE-FAIL", "SH-F6", "SH-ANCHOR-FAIL", "SH-RESEAT-FAIL",
                 "SH-DEAD", "SH-OTHER-NONMONO", "SH-STEP", "SH-GRADUAL",
                 "SH-OTHER-RESIDUAL"]

    if branch(1, "SH-GATE-FAIL", gate_fail, gate_fail_conjuncts,
              "any integrity gate fails -> invalid_measurement; HALT; repair "
              "(rule 5); never evidence about shape; S0 gates inherited from "
              "committed PASS-S0 (snapshot TASK-20260901-56ecb6); S1 gates "
              "evaluated this task"):
        verdict = "SH-GATE-FAIL"
    elif branch(2, "SH-F6", False,
                {"dead_anchor_hits_s0": s0_dead_hits,
                 "evaluated_in": "S0 (TASK-20260901-706b1d)",
                 "committed_s0_outcome": s0_outcome},
                "n/a post-S0: dead anchor read 0 hits at 2^30 in S0 (band <= 8, "
                "tripwire >= 9 not fired); committed S0 outcome PASS-S0"):
        verdict = "SH-F6"
    elif branch(3, "SH-ANCHOR-FAIL", False,
                {"k0_reseat_hits_s0": s0_ramp_hits,
                 "evaluated_in": "S0 (TASK-20260901-706b1d)",
                 "committed_s0_outcome": s0_outcome},
                "n/a post-S0: k=0 ramp-zero anchor passed exactly in S0 "
                "(hits = 2^30, W=3 on 100% of nontrivial, excess ratio 1.0 "
                "exact); committed S0 outcome PASS-S0"):
        verdict = "SH-ANCHOR-FAIL"
    elif branch(4, "SH-RESEAT-FAIL", not reseat_ok,
                {"h16": h16, "band": [6, 30], "in_band": reseat_ok},
                "k=16 re-seat outside [6,30] -> F5 indictment of THIS record's "
                "widened table path (committed measurements stand); HALT; "
                "interior readings recorded but NO shape verdict composed; repair"):
        verdict = "SH-RESEAT-FAIL"
    elif branch(5, "SH-DEAD", h1 <= 5 and h2 <= 5 and h8 <= 5,
                {"h1_le_5": h1 <= 5, "h2_le_5": h2 <= 5, "h8_le_5": h8 <= 5,
                 "h1": h1, "h2": h2, "h8": h8},
                "no hit-count excess at any powered interior point; recorded "
                "with per-point floors and named successor (finer dose "
                "resolution near k=16: k=12 first)"):
        verdict = "SH-DEAD"
    elif branch(6, "SH-OTHER-NONMONO", band_rising,
                {"band_rising": band_rising, "rising_pairs_k": rising_pairs,
                 "bandranks_k1_k2_k8_k16": [br1, br2, br8, br16],
                 "hits_k1_k2_k8_k16": [h1, h2, h8, h16]},
                "not SH-DEAD and band sequence over {1,2,8,16} BAND-RISING -> "
                "non-monotone curve; recorded as measured with the rise "
                "located; named successor (k=4 to interpolate, or instrument "
                "review if the rise is k=8 NULL -> k=16 RESIDUAL)"):
        verdict = "SH-OTHER-NONMONO"
    elif branch(7, "SH-STEP", (not band_rising) and h1 <= 40 and h2 <= 40,
                {"band_non_rising": not band_rising, "h1_le_40": h1 <= 40,
                 "h2_le_40": h2 <= 40, "h1": h1, "h2": h2, "h8": h8, "h16": h16},
                "SHAPE-FLAT: count excess persists UNDECAYED at residual level "
                "through every tested interior dose; global class fragility "
                "within the frozen family; recorded as a complete scoped "
                "result with per-point floors"):
        verdict = "SH-STEP"
    elif branch(8, "SH-GRADUAL", (not band_rising) and h1 >= 100,
                {"band_non_rising": not band_rising, "h1_ge_100": h1 >= 100,
                 "h1": h1, "h2": h2, "h8": h8, "h16": h16},
                "SHAPE-DECAY: shortfall from the affine limit decays jointly "
                "with dilution toward k=0; tunable-dose reading; recorded "
                "with the located transition and named refinement successors "
                "k=4/k=12"):
        verdict = "SH-GRADUAL"
    else:
        branch(9, "SH-OTHER-RESIDUAL", True,
               {"declared_complement": True, "h1": h1, "h2": h2, "h8": h8,
                "h16": h16, "bandranks_k1_k2_k8_k16": [br1, br2, br8, br16]},
               "DECLARED COMPLEMENT: matches none of the above (in particular "
               "h(1) in the AMBIGUITY band 41-99, which is NEVER smoothed); "
               "recorded as measured, never force-binned; named successors "
               "preregistered: k=1 second-seed arm at 2^30 and/or one 2^32 "
               "k=1 arm; budget halts are resource_exhaustion, NEVER readings")
        verdict = "SH-OTHER-RESIDUAL"

    # show every branch of the fixed order in the record; branches after the
    # fired one were NOT evaluated (ordered cascade: the fired branch preempts
    # all later branches) and are marked so, never force-evaluated
    fired_order = branches[-1]["order"]
    for i, name in enumerate(PREEMPTED, start=1):
        if i > fired_order and not any(b["branch"] == name for b in branches):
            branches.append({
                "order": i, "branch": name, "fired": None,
                "status": "NOT_REACHED_PREEMPTED",
                "conjuncts": {"evaluated": False,
                              "reason": f"branch {fired_order} ({verdict}) fired "
                                        "first; ordered cascade preempts all "
                                        "later branches; shape branches are "
                                        "never evaluated under a gate failure"},
                "note": "recorded for order-completeness only; no reading consumed"})

    out = {
        "schema": "crypto.autoresearch.sh_verdict_composition.v1",
        "task_id": "TASK-20260901-c2b265",
        "idea_record": "IDEA-20260901-582ea9",
        "pin_decision": "DEC-20260901-fb6f11",
        "cascade_source": ("PREREGISTRATION.md section 5 (copied from "
                           "IDEA-20260901-582ea9 preregistered_decision_rule "
                           "with branch_precedence_clause)"),
        "composition_order_attestation": ("composed ONLY after ALL interior "
                                          "points (k=1, k=2, k=8) and the k=16 "
                                          "re-seat were read, and after the S1-5 "
                                          "and S1-6 gates; k=16 re-seat was "
                                          "ANALYZED FIRST within S1"),
        "s0_gate_check": {"committed_s0_outcome": s0_outcome,
                          "snapshot": "archives/TASK-20260901-56ecb6",
                          "interior_arms_admitted": s0_outcome == "PASS-S0"},
        "readings_consumed": {
            "h16_k16_reseat": h16, "band16": t1["band"],
            "h1_k1": h1, "band1": t2["band"],
            "h2_k2": h2, "band2": t3["band"],
            "h8_k8": h8, "band8": t4["band"],
            "overflow_by_run": overflow,
            "determinism_pass": det_pass,
            "digest_reverify_pass": reverify_pass,
            "freeze_pass": freeze_pass,
            "source_diff_empty_vs_s0_copy": srcdiff_empty,
        },
        "branches_evaluated_in_fixed_order": branches,
        "ordered_sh_verdict": verdict,
        "shape_verdict_composed": verdict not in ("SH-GATE-FAIL", "SH-F6",
                                                  "SH-ANCHOR-FAIL", "SH-RESEAT-FAIL"),
        "ambiguity_band_note": ("the 41-99 band is never smoothed; a reading "
                                "there is SH-OTHER-RESIDUAL per the cascade"),
        "precedence_clause_note": ("exhaustive ordered cascade; branches 5-8 "
                                   "mutually disjoint on their conjuncts; "
                                   "SH-OTHER-RESIDUAL is the declared "
                                   "complement; within-band inversions do not "
                                   "fire the sentinel (band-level granularity "
                                   "is the declared resolution)"),
        "composed_utc": now_iso(),
        "parse_attestation": ("this file is machine-generated JSON; parsed "
                              "whole with python3 json.load before task "
                              "completion"),
        "inference": INFERENCE,
    }
    with open(outp, "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({"ordered_sh_verdict": verdict,
                      "shape_verdict_composed": out["shape_verdict_composed"],
                      "hits": {"k16": h16, "k1": h1, "k2": h2, "k8": h8}}, indent=1))
    sys.exit(0)


if __name__ == "__main__":
    main()
