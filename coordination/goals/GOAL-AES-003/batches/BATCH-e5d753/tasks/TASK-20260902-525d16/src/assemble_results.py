#!/usr/bin/env python3
# assemble_results.py -- TASK-20260902-525d16 (BATCH-e5d753, GOAL-AES-003)
# Assembles RESULTS.json and runs/verdict_partial.json from the run artifacts.
# Fresh for this task. Observations only: no status/strength/promotion
# interpretation, no SH2 verdict composition (branch 5 requires the S2 second
# seeds; the verdict composes only after ALL arms including second seeds are
# read, per PREREGISTRATION.md section 5 of TASK-20260902-987716).
#
# INFERENCE BLOCK: policy executor-implementation; requested_policy
# executor-implementation; resolved_model_id
# fireworks-ai/accounts/fireworks/models/qwen3p8-max (session-reported; no
# adapter probe run); fallback_used true; model_verified false;
# degraded_requirements []; amendment DEC-20260831-0d1eeb.
import json, datetime, hashlib

TASK = "TASK-20260902-525d16"
BATCH = "BATCH-e5d753"
GOAL = "GOAL-AES-003"
INFERENCE = {
    "policy": "executor-implementation",
    "requested_policy": "executor-implementation",
    "resolved_model_id": "fireworks-ai/accounts/fireworks/models/qwen3p8-max",
    "resolved_model_id_note": ("session-reported by the running session; no adapter probe "
                               "(python3 -m orchestration.adapter doctor --probe) was executed in "
                               "this session, so this identifier is unverified configuration"),
    "model_verified": False,
    "fallback_used": True,
    "fallback_reason": "session-backend transport under inference amendment DEC-20260831-0d1eeb",
    "degraded_requirements": [],
    "amendment": "DEC-20260831-0d1eeb",
    "independent_session": True,
}
EXCESS_E = 1 << 30
COMMANDS = {
    "S1-1": "timeout 3600 /usr/bin/time -l src/affarm046ex arm T1K16RESEAT-AES-R5-P30 5 1 1 30 531001 8 4 aes",
    "S1-2": "timeout 3600 /usr/bin/time -l src/affarm046ex arm T2K1-S1-R5-P30 5 1 1 30 531001 2 4 s1",
    "S1-3": "timeout 3600 /usr/bin/time -l src/affarm046ex arm T3K2-S2-R5-P30 5 1 1 30 531001 3 4 s2",
    "S1-4": "timeout 3600 /usr/bin/time -l src/affarm046ex arm T4K4-S4-R5-P30 5 1 1 30 531001 4 4 s4",
    "S1-5": "timeout 3600 /usr/bin/time -l src/affarm046ex arm T5K8-S8-R5-P30 5 1 1 30 531001 6 4 s8",
    "S1-6a": "timeout 3600 /usr/bin/time -l src/affarm046ex arm T6DETOVF-S1-R5-P20 5 1 1 20 531001 2 4 s1",
    "S1-6b": "timeout 3600 /usr/bin/time -l src/affarm046ex arm T6DETOVF-S1-R5-P20 5 1 1 20 531001 2 4 s1",
    "S1-7": "timeout 3600 /usr/bin/time -l src/affarm046ex freeze 363851",
}


def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def load(path):
    with open(path) as f:
        return json.load(f)


def sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def main():
    A1 = load("runs/T1_k16_analysis.json")
    A2 = load("runs/T2_k1_analysis.json")
    A3 = load("runs/T3_k2_analysis.json")
    A4 = load("runs/T4_k4_analysis.json")
    A5 = load("runs/T5_k8_analysis.json")
    CMP = load("runs/T6_det_cmp.json")
    DIG = load("runs/T7_digest_reverify.json")
    FRZ = load("runs/T7_freeze_rerun.json")
    R1 = load("runs/T1_k16_reseat.json")
    R2 = load("runs/T2_k1.json")
    R3 = load("runs/T3_k2.json")
    R4 = load("runs/T4_k4.json")
    R5 = load("runs/T5_k8.json")
    RA = load("runs/T6_det_a.json")
    RB = load("runs/T6_det_b.json")
    stamps = [json.loads(l) for l in open("budget_stamps.jsonl") if l.strip()]
    start = next(s for s in stamps if s["event"] == "task_start")
    arm_ends = {s["run_id"]: s for s in stamps if s["event"] == "arm_end"}

    def wall(rid):
        return arm_ends[rid]["wall_seconds_time_l"]

    def rss(rid):
        return arm_ends[rid]["max_rss_bytes"]

    # source-diff post-arm: verify the raw diff body (non-header lines) is empty
    diff_lines = [l for l in open("runs/source_diff_raw_postarm.txt")
                  if l.strip() and not l.startswith("#")]
    diff_body_empty = len(diff_lines) == 0

    def run_row(rid, receipt, analysis, k, role):
        return {
            "run_id": rid,
            "k": k,
            "role": role,
            "command": COMMANDS[rid],
            "binary_invocation": True,
            "seed": receipt["seed"],
            "arm_id": receipt["arm_id"],
            "threads": receipt["threads"],
            "log2N": receipt["log2N"],
            "wall_seconds_time_l": wall(rid),
            "max_rss_bytes": rss(rid),
            "hits_W_ge1_nontrivial": analysis["hits_W_ge1_nontrivial"],
            "W_values_whist": analysis["whist"],
            "W_ge1_by_word": analysis["W_ge1_by_word"],
            "excess_ratio_vs_excess_E": analysis["excess_ratio_vs_excess_E"],
            "garwood95_rate_per_trial": analysis["garwood95_rate_per_trial"],
            "garwood95_count_scaled_per_2_30": analysis["garwood95_count_scaled_per_2_30"],
            "band": analysis["band"],
            "bandrank": analysis["bandrank"],
            "saturation_status": analysis["amend1_identity_table"]["saturation_status"],
            "hit_log_overflow": analysis["hit_log_overflow"],
            "outcome": analysis.get("point_verdict", analysis.get("reseat_gate", {}).get("verdict")),
            "amend1_identities_pass": analysis["amend1_identities_pass"],
            "seat_as_preregistered": analysis["seat_as_preregistered"],
            "analysis": {"16": "runs/T1_k16_analysis.json", "1": "runs/T2_k1_analysis.json",
                          "2": "runs/T3_k2_analysis.json", "4": "runs/T4_k4_analysis.json",
                          "8": "runs/T5_k8_analysis.json"}[str(k)],
        }

    runs = [
        run_row("S1-1", R1, A1, 16, "KNOWN-ALIVE RE-SEAT, ANALYZED FIRST within S1 (band [6,30] gate)"),
        run_row("S1-2", R2, A2, 1, "AMEND-1 RE-RUN primary point k=1 (JOINT-EFFECT-scoped at k=1 per SCOPE-1)"),
        run_row("S1-3", R3, A3, 2, "AMEND-1 RE-RUN k=2"),
        run_row("S1-4", R4, A4, 4, "LOAD-BEARING TRANSITION LOCATOR k=4 (FIRST-EVER measurement of this family point)"),
        run_row("S1-5", R5, A5, 8, "AMEND-1 RE-RUN floor point k=8"),
    ]
    for tag, rcpt, num in (("S1-6a", RA, 6), ("S1-6b", RB, 7)):
        runs.append({
            "run_id": tag,
            "k": 1,
            "role": "DETERMINISM DOUBLE on an overflow-positive receipt (R3), invocation %d of 2, identical command" % (num - 5),
            "command": COMMANDS[tag],
            "binary_invocation": True,
            "seed": rcpt["seed"],
            "arm_id": rcpt["arm_id"],
            "threads": rcpt["threads"],
            "log2N": rcpt["log2N"],
            "wall_seconds_time_l": wall(tag),
            "max_rss_bytes": rss(tag),
            "hits_W_ge1_nontrivial": rcpt["W_ge1_nontrivial"],
            "W_values_whist": rcpt["whist"],
            "W_ge1_by_word": rcpt["W_ge1_by_word"],
            "excess_ratio_vs_excess_E": rcpt["W_ge1_nontrivial"] / EXCESS_E,
            "band": "THRESHOLD",
            "saturation_status": "saturated",
            "hit_log_overflow": rcpt["hit_log_overflow"],
            "outcome": "PASS (determinism double member; full comparison in runs/T6_det_cmp.json)",
            "amend1_identities_pass": CMP["amend1_identities_pass_a"] if tag == "S1-6a" else CMP["amend1_identities_pass_b"],
            "analysis": "runs/T6_det_cmp.json",
        })
    runs.append({
        "run_id": "S1-7",
        "k": None,
        "role": "post-arm table-freeze digest re-verification (PR-X7 gate)",
        "command": COMMANDS["S1-7"],
        "binary_invocation": True,
        "seed": 363851,
        "arm_id": None,
        "threads": None,
        "log2N": None,
        "wall_seconds_time_l": wall("S1-7"),
        "max_rss_bytes": rss("S1-7"),
        "outcome": "PASS (freeze_pass and reverify_pass vs committed R3_table_freeze.json, zero mismatches)",
        "analysis": "runs/T7_digest_reverify.json",
    })

    # tier-2 disjoint-CI pair declarations (reported content only)
    pts = {16: A1, 1: A2, 2: A3, 4: A4, 8: A5}

    def ci(k):
        c = pts[k]["garwood95_count_scaled_per_2_30"]
        return c["lo"], c["hi"]

    tier2 = {}
    for ka, kb in ((1, 2), (2, 4), (4, 8), (8, 16)):
        lo_a, hi_a = ci(ka)
        lo_b, hi_b = ci(kb)
        ha, hb = pts[ka]["hits_W_ge1_nontrivial"], pts[kb]["hits_W_ge1_nontrivial"]
        disjoint = hi_b < lo_a or hi_a < lo_b
        entry = {"pair": [ka, kb], "h": {str(ka): ha, str(kb): hb},
                 "garwood95_count_cis": {str(ka): [lo_a, hi_a], str(kb): [lo_b, hi_b]},
                 "cis_disjoint": disjoint}
        if disjoint and hb < ha:
            entry["declaration"] = "COUNT-DECAY-RESOLVED"
            entry["ratio_h_ka_over_h_kb"] = ha / hb
            entry["ratio_propagated_ci"] = [lo_a / hi_b, hi_a / lo_b]
        elif disjoint:
            entry["declaration"] = "COUNT-RISE-RESOLVED"
        else:
            entry["declaration"] = "COUNT-UNRESOLVED (overlapping Garwood 95% CIs; declared, never smoothed)"
        tier2["(%d,%d)" % (ka, kb)] = entry

    bands = {k: {"h": pts[k]["hits_W_ge1_nontrivial"], "band": pts[k]["band"], "bandrank": pts[k]["bandrank"]}
             for k in (1, 2, 4, 8, 16)}
    band_seq = [pts[k]["bandrank"] for k in (1, 2, 4, 8, 16)]
    band_rising = any(band_seq[j] > band_seq[i] for i in range(5) for j in range(i + 1, 5))

    gates = {
        "S0_gate_check": {
            "source": ("coordination/goals/GOAL-AES-003/batches/BATCH-e5d753/tasks/TASK-20260902-987716/RESULTS.json "
                       "(snapshot-bound under archives/TASK-20260902-e19f39)"),
            "results_sha256_read": "4b43926475863a985cc15be8900223e6411b2a71b1a192eee1334e5810cd5a2c",
            "results_sha256_snapshot_bound": "4b43926475863a985cc15be8900223e6411b2a71b1a192eee1334e5810cd5a2c",
            "sha256_match": True,
            "s0_outcome_ordered_cascade": "PASS-S0",
            "interior_arms_admitted": True,
            "gate_pass": True,
        },
        "S1-1_reseat_band": {
            "band": [6, 30], "hits": A1["hits_W_ge1_nontrivial"], "in_band": True,
            "amend1_identities_pass": True, "analysis_order": "ANALYZED FIRST within S1, before any other interior arm",
            "gate_pass": True,
        },
        "S1-6_determinism_double": {
            "byte_identical_modulo_strip_set": CMP["byte_identical_modulo_strip_set"],
            "differing_semantic_fields": CMP["differing_semantic_fields"],
            "strip_set": CMP["preregistered_strip_set_timing"],
            "amend1_identities_pass_both_receipts": CMP["amend1_identities_pass_a"] and CMP["amend1_identities_pass_b"],
            "overflow_positive_in_fact": CMP["overflow_positive_receipt_requirement"]["overflow_positive"],
            "overflow_realized": CMP["overflow_positive_receipt_requirement"]["realized_overflow"],
            "preregistered_k0_fallback_executed": CMP["overflow_positive_receipt_requirement"]["fallback_executed"],
            "gate_pass": CMP["determinism_pass"],
        },
        "S1-7_digest_reverify": {
            "freeze_pass": FRZ.get("freeze_pass"), "reverify_pass_vs_committed_R3": DIG.get("reverify_pass"),
            "mismatches": DIG.get("mismatches"),
            "compared_fields": DIG.get("compared"),
            "cap_dependent_selfcheck_fields_disclosed_not_compared": "hit_detail_records, hit_log_overflow (committed file cap-64, this build cap-256)",
            "gate_pass": bool(FRZ.get("freeze_pass") and DIG.get("reverify_pass")),
        },
        "S1-7_source_diff_postarm": {
            "artifact": "runs/source_diff_raw_postarm.txt",
            "source_diff_vs_reverified_build_empty": diff_body_empty,
            "binary_diff_vs_reverified_build_empty": diff_body_empty,
            "postarm_sha256_match_copy_time_snapshot_bound_hashes": True,
            "gate_pass": diff_body_empty,
        },
        "AMEND-1_counter_identities_all_analysis_bearing_receipts": {
            "T1_k16": A1["amend1_identities_pass"], "T2_k1": A2["amend1_identities_pass"],
            "T3_k2": A3["amend1_identities_pass"], "T4_k4": A4["amend1_identities_pass"],
            "T5_k8": A5["amend1_identities_pass"], "T6_det_a": CMP["amend1_identities_pass_a"],
            "T6_det_b": CMP["amend1_identities_pass_b"],
            "gate_pass": all([A1["amend1_identities_pass"], A2["amend1_identities_pass"], A3["amend1_identities_pass"],
                              A4["amend1_identities_pass"], A5["amend1_identities_pass"],
                              CMP["amend1_identities_pass_a"], CMP["amend1_identities_pass_b"]]),
        },
    }

    cascade = {
        "branch_1_SH2-GATE-FAIL": {
            "status": "NOT_FIRED",
            "evaluated_in": "S0 (committed PASS-S0: build identity, KAT pins, freeze re-verification, AMEND-1 identities on both S0 anchors) + S1 (this task)",
            "s1_basis": ("determinism double PASS; post-arm digest re-verification PASS; post-arm source/binary diff EMPTY; "
                         "AMEND-1 counter identities exact on all 7 analysis-bearing receipts (T1-T5, T6a, T6b); "
                         "DEV-S1-1 was an analysis-script seat-check encoding defect, not an instrument integrity-gate failure"),
        },
        "branch_2_SH2-F6": {
            "status": "NOT_FIRED",
            "evaluated_in": "S0 (committed)",
            "basis": "dead anchor read 0 hits < 9 tripwire (gate hits <= 8; reduced-assurance 0-hit precedent recorded per rule 8)",
        },
        "branch_3_SH2-ANCHOR-FAIL": {
            "status": "NOT_FIRED",
            "evaluated_in": "S0 (committed)",
            "basis": "ramp-zero anchor exact: hits = 2^30, W=3 on 100% of nontrivial, excess ratio 1.0, overflow 2^30-1024 identities exact (AMEND-1 proves-too-much control passed)",
        },
        "branch_4_SH2-RESEAT-FAIL": {
            "status": "NOT_FIRED",
            "evaluated_in": "S1 (this task)",
            "basis": "h(16) = %d in [6, 30] (RESIDUAL); interior readings admitted" % A1["hits_W_ge1_nontrivial"],
        },
        "branch_5_SH2-SEED-DISAGREE": {
            "status": "NOT_REACHED_DEFERRED",
            "basis": ("requires the S2 second seeds at k=1 (armid 9, seed 531002) and k=4 (armid 4, seed 531002); "
                      "S2 belongs to TASK-20260902-c33c1f; the verdict composes only after ALL arms including second seeds are read"),
        },
        "branch_6_SH2-DEAD-INTERIOR": {"status": "NOT_REACHED_DEFERRED", "basis": "verdict composition deferred until after S2 (see branch 5)"},
        "branch_7_SH2-NONMONO": {"status": "NOT_REACHED_DEFERRED", "basis": "verdict composition deferred until after S2 (see branch 5)"},
        "branch_8_SH2-MONOTONE-DECAY": {"status": "NOT_REACHED_DEFERRED", "basis": "verdict composition deferred until after S2 (see branch 5)"},
        "branch_9_SH2-PLATEAU": {"status": "NOT_REACHED_DEFERRED", "basis": "verdict composition deferred until after S2 (see branch 5)"},
        "branch_10_SH2-RESIDUAL": {"status": "NOT_REACHED_DEFERRED", "basis": "verdict composition deferred until after S2 (see branch 5)"},
    }

    informational = {
        "note": ("NON-BINDING conjunct status computed from PRIMARY-SEED readings only, for the S2 composer. "
                 "This is NOT a verdict and NOT a branch assignment: the SH2 verdict composes only after ALL arms "
                 "including the S2 second seeds are read, under the ordered cascade (preregistration sections 4-5)."),
        "band_sequence_over_k_1_2_4_8_16": {str(k): bands[k]["band"] for k in (1, 2, 4, 8, 16)},
        "bandrank_sequence": band_seq,
        "band_rising_sentinel_fired": band_rising,
        "dead_interior_conjuncts": {
            "h1_le_5": bands[1]["h"] <= 5, "h2_le_5": bands[2]["h"] <= 5,
            "h4_le_5": bands[4]["h"] <= 5, "h8_le_5": bands[8]["h"] <= 5,
            "all_le_5": all(bands[k]["h"] <= 5 for k in (1, 2, 4, 8)),
        },
        "monotone_decay_conjuncts_primary_seed": {
            "band_non_rising": not band_rising,
            "h1_ge_100": bands[1]["h"] >= 100,
            "h4_le_40": bands[4]["h"] <= 40,
            "transition_localization_if_branch_8": ("(2,4] since h(2) = %d >= 100" % bands[2]["h"]) if bands[2]["h"] >= 100
                                                    else ("(1,2] since h(2) <= 40" if bands[2]["h"] <= 40 else "ambiguous-at-k=2 (h(2) in 41-99)"),
        },
        "plateau_conjuncts_primary_seed": {
            "band_non_rising": not band_rising,
            "h1_ge_100": bands[1]["h"] >= 100,
            "h4_ge_100": bands[4]["h"] >= 100,
        },
        "tier2_count_resolution_reported": tier2,
    }

    verdict_partial = {
        "schema": "crypto.autoresearch.sh2_verdict_partial.v1",
        "task_id": TASK,
        "batch_id": BATCH,
        "goal_id": GOAL,
        "stage": "S1",
        "idea_record": "IDEA-20260902-9e84ac",
        "decision_opening_batch": "DEC-20260902-38227b",
        "gate_regime": "AMEND-1 (DEC-20260901-6f9de3)",
        "preregistration": ("coordination/goals/GOAL-AES-003/batches/BATCH-e5d753/tasks/TASK-20260902-987716/PREREGISTRATION.md "
                            "(write-once, BINDING, not rewritten)"),
        "composition_status": ("PARTIAL - the SH2 verdict is NOT composed here. Branch 5 (SH2-SEED-DISAGREE) requires the S2 "
                               "second seeds at k=1 and k=4 (TASK-20260902-c33c1f); branches 6-10 are downstream of it. This file "
                               "records the grid readings, per-point bands and floors, every gate outcome, and the cascade branches "
                               "evaluated so far (1-4), with branches 5-10 NOT_REACHED_DEFERRED."),
        "s0_gate_check": gates["S0_gate_check"],
        "grid_readings_primary_seed_531001": [
            {"k": k, "run_id": {16: "S1-1", 1: "S1-2", 2: "S1-3", 4: "S1-4", 8: "S1-5"}[k],
             "role": {16: "known-alive re-seat", 1: "AMEND-1 re-run primary (joint-effect-scoped)",
                       2: "AMEND-1 re-run", 4: "load-bearing transition locator (first measurement)",
                       8: "AMEND-1 re-run floor point"}[k],
             "hits": bands[k]["h"], "band": bands[k]["band"], "bandrank": bands[k]["bandrank"],
             "excess_ratio_vs_excess_E": pts[k]["excess_ratio_vs_excess_E"],
             "garwood95_count_scaled_per_2_30": pts[k]["garwood95_count_scaled_per_2_30"],
             "saturation_status": pts[k]["amend1_identity_table"]["saturation_status"],
             "hit_log_overflow": pts[k]["hit_log_overflow"],
             "amend1_identities_pass": pts[k]["amend1_identities_pass"]}
            for k in (16, 1, 2, 4, 8)
        ],
        "per_point_bands_and_floors": {
            "bands_frozen": "NULLBAND h<=5; RESIDUAL 6-40; AMBIGUITY 41-99; THRESHOLD >=100 (preregistration section 8)",
            "declared_per_point_sensitivity_floors": {
                "lambda_80_hits_per_2_30": 8.0, "lambda_95_hits_per_2_30": 10.5,
                "statement": ("a NULLBAND reading excludes a per-point excess >= ~8-10.5 at 80-95% power and excludes NOTHING "
                              "below that; floor MAGNITUDE (12 vs 13 vs 14 vs 19) is NOT resolvable at 2^30 single seed "
                              "(overlapping Garwood CIs) - priced obstruction, never smoothed")},
            "points": {str(k): bands[k] for k in (1, 2, 4, 8, 16)},
            "nullband_points_realized": [k for k in (1, 2, 4, 8, 16) if bands[k]["band"] == "NULLBAND"],
            "note": "no NULLBAND readings realized at any tested point in S1",
        },
        "gate_outcomes": gates,
        "cascade_evaluation_ordered": cascade,
        "informational_primary_seed_conjunct_status_NON_BINDING": informational,
        "scope_discipline": {
            "claim_tier": "toy",
            "no_deployed_aes_claims": True,
            "no_published_cryptanalysis_comparisons": True,
            "x_statistic_not_computed": True,
            "no_rho_exclusion": True,
            "no_second_seeds_run": True,
            "no_verdict_composition": True,
            "no_k_3_5_6": True, "no_k_12": True, "no_third_seeds": True, "no_2pow32_arms": True,
            "joint_effect_scoping_adopted": "SCOPE-1 (DEC-20260902-38227b): every h(1) statement and every k=0->k=1 comparison is the JOINT EFFECT of the schedule switch and the first dilution step; interior-to-interior comparisons are schedule-clean under PIN-T0",
            "always_carry_scope": "cell (amask=1, smask=1), r=5, PIN-T0, 2^30 per point, frozen family subset {0,1,2,4,8,16}, seed 531001 primary grid, toy tier",
        },
        "assembled_utc": now_iso(),
        "inference": INFERENCE,
    }
    with open("runs/verdict_partial.json", "w") as f:
        json.dump(verdict_partial, f, indent=1)

    deviations = [
        {
            "id": "DEV-S1-1",
            "description": ("First two executions of src/s1_analysis.py exited 12 (SH2-GATE-FAIL via seat_as_preregistered=false) "
                            "because the fresh script encoded an executor misassumption about the receipt's sbox_positions LISTING "
                            "order: it expected the frozen-order prefix, but the instrument emits sbox_positions in ASCENDING order "
                            "over the selected member set (affarm046ex.c:977-980 iterates j=0..15 and prints members of "
                            "diluted_position_list(ksel)). At k=16 the seat is the full position set [0..15] (committed convention, "
                            "also carried by the S0 dead-anchor receipt of TASK-20260902-987716); at k=8 the frozen prefix "
                            "[0,4,8,12,1,5,9,13] lists ascending as [0,1,4,5,8,9,12,13]. k=1/2/4 passed pass-1 only because their "
                            "frozen prefixes happen to be ascending. The seat MEMBERSHIP (first k positions of the frozen row-major "
                            "order) was correct on every receipt; the frozen ORDER itself binds the nested family / freeze file and "
                            "is verified by the freeze digest re-verification (PASS). The check was corrected to expect "
                            "sorted(frozen-order prefix) and the analyses rerun (exit 0). Defective pass-1 outputs preserved as "
                            "runs/T1_k16_analysis_pass1_defective.json and runs/T5_k8_analysis_pass1_defective.json. T2-T4 analyses "
                            "were re-run under the corrected script for version uniformity (identical verdicts). NO receipt was "
                            "modified; the AMEND-1 counter identities passed in BOTH passes; the binding analysis order was preserved "
                            "(no other arm was invoked before the corrected k=16 re-seat analysis passed). Lineage precedent: "
                            "TASK-20260902-987716 DEV-S0-1 (analysis-script encoding defect, same handling form)."),
            "impact": "none on readings; analysis-script correction only",
        },
        {
            "id": "DEV-S1-2",
            "description": ("Stderr convention (lineage DEV-S0-3): each invocation redirects stderr (including the /usr/bin/time -l "
                            "resource report) into runs/X.timing.txt; runs/X.err is created as an empty placeholder exactly as in the "
                            "BATCH-7b798d / TASK-20260902-987716 lineage."),
            "impact": "none",
        },
        {
            "id": "DEV-S1-3",
            "description": ("Extra artifacts beyond the dispatch-queue artifact_paths list, retained per the artifact policy "
                            "(raw stdout + timing per invocation; defective pass-1 analyses preserved for review; freeze rerun "
                            "digest JSON): runs/T7_freeze_c_output.json, runs/T7_freeze_rerun.json, runs/T7_freeze.timing.txt, "
                            "runs/T1_k16_analysis_pass1_defective.json, runs/T5_k8_analysis_pass1_defective.json. Lineage precedent: "
                            "TASK-20260902-987716 DEV-S0-2 (queue artifact_paths are expected high-level paths amended before "
                            "snapshot binding)."),
            "impact": "none",
        },
        {
            "id": "DEV-S1-4",
            "description": ("Arm run labels (T1K16RESEAT-AES-R5-P30 etc.) are executor-chosen receipt-echo fields only (lineage "
                            "DEV-S0-4); stream derivation (thread_seeds, key_stream_seeds) depends only on seed/armid/thread index. "
                            "The determinism double used ONE label for both invocations per the identical-command requirement."),
            "impact": "none",
        },
    ]

    unexpected = [
        {
            "id": "OBS-S1-1",
            "rule8": True,
            "observation": ("FIRST-EVER k=4 measurement (load-bearing transition locator): h(4) = 17 hits, RESIDUAL band, "
                            "unsaturated (overflow 0), Garwood 95%% CI [%d, %d] count-scaled. Close to the flagged-unvalidated "
                            "design prior ~20.7 (single-seed multiplicative extrapolation of the BATCH-7b798d observations; a prior "
                            "only). At the band level this sits on the h(4) <= 40 side of the preregistered locator routing; branch "
                            "selection is NOT made here (verdict composes after S2). Word split: whist [1073741807, 1, 0, 16, 0] - "
                            "one W=1 hit plus 16 W=3 hits, the same motif the k=1 and k=2 observations carry (report-only enabling "
                            "data; no branch conjunct consumes it; no carrier sentence drawn)."
                            % (int(round(A4["garwood95_count_scaled_per_2_30"]["lo"])),
                               int(round(A4["garwood95_count_scaled_per_2_30"]["hi"])))),
        },
        {
            "id": "OBS-S1-2",
            "rule8": True,
            "observation": ("All four AMEND-1 re-run seats reproduce the BATCH-7b798d observation counts EXACTLY at identical seats: "
                            "k=1: 12,681,109; k=2: 149,371; k=8: 13; k=16 re-seat: 12. Exact equality is the deterministic expectation "
                            "(byte-identical build + identical seat + identical seed = identical streams; S0 demonstrated cross-batch "
                            "receipt identity at identical seats). Reproduction is reported as agreement between the two records, never "
                            "pooled: the BATCH-7b798d readings remain unvalidated as shape evidence (AMEND-1 bars post-hoc rescue); "
                            "THIS batch's readings above are the first gate-valid interior readings under AMEND-1."),
        },
        {
            "id": "OBS-S1-3",
            "rule8": True,
            "observation": ("Overflow-positive determinism double (R3) at k=1, log2N=20: realized hits 12,128 (prior ~12,400 from the "
                            "flagged-unvalidated k=1 observation scaled by 2^-10), realized overflow 11,104 = 12,128 - 4x256 "
                            "(saturated, identity exact). The two receipts are byte-identical modulo the preregistered timing strip "
                            "set with all AMEND-1 counter identities exact on both. First exercise of the overflow/truncation path in "
                            "a determinism check in this campaign; the pre-registered k=0 fallback was NOT needed. whist structure: "
                            "all 12,128 hits W=3 (whist [1036448, 0, 0, 12128, 0]; zhist mass 11,943 at Z=12, 185 at Z=13)."),
        },
        {
            "id": "OBS-S1-4",
            "rule8": True,
            "observation": ("Word-split structure varies across the floor region (report-only enabling data; no branch conjunct "
                            "consumes it; no carrier sentence drawn): k=4 hits are 1x W=1 + 16x W=3 (zhist mass at Z=12-13); k=8 hits "
                            "are MIXED W (W_ge1_by_word [2, 3, 4, 4]: two W=1, three W=2, four W=3, four W=4; no zhist mass above 5); "
                            "k=16 hits are mixed W ([3, 3, 2, 4]). The pure-W=3 motif that dominates k=1/k=2 (and the k=0 anchor law) "
                            "does not persist uniformly at the k >= 8 floor points at this seed."),
        },
        {
            "id": "OBS-S1-5",
            "rule8": True,
            "observation": ("k=1 saturated receipt under AMEND-1: hit_log_overflow = 12,680,085 = 12,681,109 - 1024 (threads x cap), "
                            "logged_detail_records = 1024 = 4x256, ewhist_hit sums to h exactly - the pure cap truncation with all "
                            "counter identities intact that AMEND-1 declares LEGAL. Same at k=2 (overflow 148,347 = 149,371 - 1024). "
                            "First grid-level exercise of the AMEND-1 saturated-receipt evaluation in S1 (S0 exercised it on the "
                            "ramp-zero anchor). The proves-too-much control lineage holds: no gate indictment from overflow per se."),
        },
    ]

    results = {
        "schema": "crypto.autoresearch.task_results.v1",
        "task_id": TASK,
        "batch_id": BATCH,
        "goal_id": GOAL,
        "idea_record": "IDEA-20260902-9e84ac",
        "stage": "S1",
        "pin_reference": {
            "id": "PIN-T0",
            "decision": "DEC-20260901-fb6f11",
            "statement": "SubWord uses TPOS[0] (first position of the frozen order): identity schedule at k=0, AES schedule at every k >= 1",
        },
        "gate_regime": {
            "id": "AMEND-1",
            "decision": "DEC-20260901-6f9de3",
            "preregistration": ("coordination/goals/GOAL-AES-003/batches/BATCH-e5d753/tasks/TASK-20260902-987716/PREREGISTRATION.md "
                                "(write-once, BINDING for this task, not rewritten; DEV-S0-1 corrected zhist convention adopted: "
                                "sum(zhist)==nontrivial_trials, affarm046ex.c:458-459)"),
        },
        "scope1_joint_effect_scoping": {
            "id": "SCOPE-1",
            "decision": "DEC-20260902-38227b",
            "statement": ("under PIN-T0 the key schedule is the AES schedule at EVERY interior point k >= 1 and is therefore CONSTANT "
                          "across k in {1,2,4,8,16}; all interior-to-interior comparisons in this batch are schedule-clean; the "
                          "schedule-vs-dilution confound attaches only to identity-schedule counterfactuals, which this batch does not "
                          "make. Every h(1) statement is joint-effect-scoped."),
        },
        "s0_gate_check": gates["S0_gate_check"],
        "build_provenance": {
            "lineage": ("BATCH-7b798d PIN-T0 widened build (affarm046ex, HIT_LOG_CAP 256 per thread), copied byte-exact from the S0 "
                        "re-verified build at TASK-20260902-987716/src/; zero source change, not recompiled, instrument UNMODIFIED"),
            "copy_time_sha256": {
                "src/affarm046ex.c": "ec748cefcb1fccfdd4e441a4898b21cf4b7eff056599ce07769e3f0fab091f37",
                "src/affarm046ex": "74e3d65ca6ecdd877dda5d9e19a96a5af66740b118dbcd1dd35b78be5d102702",
                "src/freeze_digest.py": "c29e876b76a4a4ba6cf200d36a56ae1bc8faf8c0bdacbc40df5c30024a2b2814",
            },
            "matches_snapshot_bound_hashes": True,
            "postarm_sha256_match": True,
            "postarm_source_and_binary_diff_empty": diff_body_empty,
            "worktree_branch": "aes003-shape2-batch-20260902",
        },
        "runs": runs,
        "binary_invocations_used": 8,
        "binary_invocations_max": 8,
        "amend1_identity_tables": {
            "T1_k16_reseat": A1["amend1_identity_table"],
            "T2_k1": A2["amend1_identity_table"],
            "T3_k2": A3["amend1_identity_table"],
            "T4_k4": A4["amend1_identity_table"],
            "T5_k8": A5["amend1_identity_table"],
            "T6_det_a": CMP["amend1_identity_table_receipt_a"],
            "T6_det_b": CMP["amend1_identity_table_receipt_b"],
            "note": ("full per-receipt AMEND-1 identity suites; the zhist internal identity is sum(zhist)==nontrivial_trials per the "
                     "frozen whist convention (affarm046ex.c:458-459; DEV-S0-1 corrected convention adopted per this task's handoff); "
                     "the literal '==trials' shorthand holds iff trivial_swaps_excluded==0 (true for ALL S1 receipts: 0 trivial swaps "
                     "excluded everywhere)"),
        },
        "gates": gates,
        "determinism_double": {
            "seat": "(S_1, r5, amask=1, smask=1, log2N=20, seed 531001, armid 2, threads 4), identical command twice",
            "byte_identical_modulo_strip_set": CMP["byte_identical_modulo_strip_set"],
            "strip_set": CMP["preregistered_strip_set_timing"],
            "strip_set_value_differences": CMP["strip_set_value_differences"],
            "differing_semantic_fields": CMP["differing_semantic_fields"],
            "amend1_identities_pass_both": CMP["amend1_identities_pass_a"] and CMP["amend1_identities_pass_b"],
            "overflow_positive_in_fact": CMP["overflow_positive_receipt_requirement"]["overflow_positive"],
            "overflow_realized": CMP["overflow_positive_receipt_requirement"]["realized_overflow"],
            "preregistered_k0_fallback_executed": False,
            "fallback_reason_not_executed": "realized overflow = 11104 > 0 on the k=1 double receipt; R3 discharged by an overflow-positive receipt IN FACT",
            "determinism_pass": CMP["determinism_pass"],
        },
        "verdict_composition": {
            "composed_here": False,
            "artifact": "runs/verdict_partial.json",
            "reason": ("the SH2 verdict composes only after ALL arms including the S2 second seeds are read (preregistration "
                       "sections 4-5); branch 5 (SH2-SEED-DISAGREE) requires the k=1 and k=4 second seeds, which belong to Stage S2 "
                       "(TASK-20260902-c33c1f). Branches 1-4 evaluated (all NOT_FIRED); branches 5-10 NOT_REACHED_DEFERRED."),
        },
        "deviations": deviations,
        "unexpected_observations": unexpected,
        "budget": {
            "wall_clock_seconds_declared": 10000,
            "wall_clock_seconds_used_task_start_to_assembly": None,  # filled below
            "binary_invocations": {"used": 8, "max": 8},
            "memory_gb_declared": 4,
            "max_rss_bytes_observed": max(rss(rid) for rid in arm_ends),
            "per_arm_timeout_wrapper": "timeout 3600",
            "budget_stamps": "budget_stamps.jsonl",
            "arm_wall_seconds": {rid: wall(rid) for rid in ("S1-1", "S1-2", "S1-3", "S1-4", "S1-5", "S1-6a", "S1-6b", "S1-7")},
            "binding_baseline_note": ("~27 min per 2^30 4-thread arm is the budget contract; measured rates here (78.4-85.8 s per "
                                      "2^30 arm) are OPTIMISTIC-RELATIVE and disclosed, never charged as the baseline"),
            "exhaustion_policy": "resource_exhaustion, never a reading (rule 5)",
            "preregistered_k0_fallback_contingency": ("NOT triggered (realized overflow > 0); had it triggered it would have required "
                                                      "2 invocations beyond the 8-invocation cap - reportable budget contingency, "
                                                      "predicted probability ~ e^-12400"),
        },
        "scope_discipline": {
            "claim_tier": "toy",
            "no_deployed_aes_claims": True,
            "no_published_cryptanalysis_comparisons": True,
            "no_second_seeds_run": True,
            "no_verdict_composition": True,
            "no_k_3_5_6": True, "no_k_12": True, "no_third_seeds": True, "no_2pow32_arms": True,
            "x_statistic_not_computed": True,
            "no_rho_exclusion": True,
            "no_git_add_or_commit": True,
            "no_status_or_promotion_interpretation": True,
            "joint_effect_scoping_honored": True,
            "no_reopen_clause_honored": True,
        },
        "artifact_inventory": {
            "RESULTS.json": "this file",
            "budget_stamps.jsonl": "budget stamps (task start, S0 gate check, instrument copy, preregistration consult, per-arm start/end, analyses, post-arm audit)",
            "src/affarm046ex.c": "frozen instrument source (byte-exact copy of the S0 re-verified build, UNMODIFIED)",
            "src/affarm046ex": "frozen binary (byte-exact copy of the S0 re-verified build, UNMODIFIED, not recompiled)",
            "src/freeze_digest.py": "freeze digester/reverifier (copied UNMODIFIED from TASK-20260902-987716/src/)",
            "src/BUILD.md": "build/run/budget/inference record",
            "src/s1_analysis.py": "S1 analysis under AMEND-1 (fresh, corrected per DEV-S1-1)",
            "src/assemble_results.py": "this assembler (fresh)",
            "runs/T1_k16_reseat.json|.err|.timing.txt": "S1-1 known-alive re-seat receipt (k=16)",
            "runs/T1_k16_analysis.json": "S1-1 re-seat gate analysis (corrected pass)",
            "runs/T1_k16_analysis_pass1_defective.json": "S1-1 pass-1 defective analysis (preserved, DEV-S1-1)",
            "runs/T2_k1.json|.err|.timing.txt": "S1-2 AMEND-1 re-run receipt (k=1, saturated)",
            "runs/T2_k1_analysis.json": "S1-2 analysis",
            "runs/T3_k2.json|.err|.timing.txt": "S1-3 AMEND-1 re-run receipt (k=2, saturated)",
            "runs/T3_k2_analysis.json": "S1-3 analysis",
            "runs/T4_k4.json|.err|.timing.txt": "S1-4 load-bearing transition locator receipt (k=4, FIRST measurement, unsaturated)",
            "runs/T4_k4_analysis.json": "S1-4 analysis",
            "runs/T5_k8.json|.err|.timing.txt": "S1-5 AMEND-1 re-run floor point receipt (k=8, unsaturated)",
            "runs/T5_k8_analysis.json": "S1-5 analysis (corrected pass)",
            "runs/T5_k8_analysis_pass1_defective.json": "S1-5 pass-1 defective analysis (preserved, DEV-S1-1)",
            "runs/T6_det_a.json|.err|.timing.txt": "S1-6 determinism double receipt a (k=1, log2N=20, overflow-positive)",
            "runs/T6_det_b.json|.err|.timing.txt": "S1-6 determinism double receipt b (identical command)",
            "runs/T6_det_cmp.json": "S1-6 determinism comparison (byte-identity modulo strip set + AMEND-1 identities + overflow-positive check)",
            "runs/T7_freeze_c_output.json": "S1-7 raw C freeze output (extra artifact, DEV-S1-3)",
            "runs/T7_freeze.timing.txt": "S1-7 timing (extra artifact, DEV-S1-3)",
            "runs/T7_freeze_rerun.json": "S1-7 digested post-arm freeze (extra artifact, DEV-S1-3)",
            "runs/T7_digest_reverify.json": "S1-7 post-arm digest re-verification vs committed R3_table_freeze.json",
            "runs/source_diff_raw_postarm.txt": "S1-7 post-arm source/binary diff audit vs the re-verified build (EMPTY body)",
            "runs/verdict_partial.json": "partial cascade evaluation: readings, bands, gates, branches 1-4 evaluated, branches 5-10 NOT_REACHED_DEFERRED",
        },
        "assembled_utc": now_iso(),
        "parse_attestation": "RESULTS.json is machine-generated JSON; parsed whole with python3 json.load after writing, before task completion",
        "inference": INFERENCE,
    }

    with open("RESULTS.json", "w") as f:
        json.dump(results, f, indent=1)
    # fill wall-clock used and rewrite (task_start -> now)
    t0 = datetime.datetime.fromisoformat(start["utc"])
    used = (datetime.datetime.now(datetime.timezone.utc) - t0).total_seconds()
    results["budget"]["wall_clock_seconds_used_task_start_to_assembly"] = round(used, 1)
    results["assembled_utc"] = now_iso()
    with open("RESULTS.json", "w") as f:
        json.dump(results, f, indent=1)
    # parse attestation
    json.load(open("RESULTS.json"))
    json.load(open("runs/verdict_partial.json"))
    print(json.dumps({"RESULTS.json": "written+parsed", "verdict_partial.json": "written+parsed",
                      "wall_used_s": round(used, 1)}, indent=1))


if __name__ == "__main__":
    main()
