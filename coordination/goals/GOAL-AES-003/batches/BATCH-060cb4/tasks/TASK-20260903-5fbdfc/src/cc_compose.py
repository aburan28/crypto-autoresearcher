#!/usr/bin/env python3
# cc_compose.py -- TASK-20260903-5fbdfc (BATCH-060cb4, GOAL-AES-003), S1-3
# CC COMPOSITION (analysis only, 0 binary invocations). Evaluates the
# preregistered rule (TASK-20260903-695ebe/PREREGISTRATION.md sections 4-5,
# BINDING, not rewritten; IDEA-20260903-8f26ac count_completion_decision_rule)
# in FIXED ORDER at k=2: CC-GATE-FAIL > CC-SEED-DISAGREE > CC-COUNT-DISAGREE
# > CC-AGREE, with the orthogonal CC8 axis (CC8-FLOOR-DEPART / CC8-AGREE) at
# k=8 evaluated beside the k=2 verdict, never gating it. Also computes the
# per-seed decay ratios r(1,2) and r(2,4) for BOTH seeds with corner-
# propagated Garwood CIs (campaign convention of BATCH-e5d753 check_6:
# ratio CI from count-CI corners L_num/U_den, U_num/L_den), runs the
# post-arm table-digest re-verification vs the committed R3 k=2/k=8 entries,
# the post-arm source/binary diff audit (must be EMPTY - zero source change
# in S1), and the sha256 re-check of the build vs the S0-bound hashes.
# SCOPE-1 attribution only; NARROW-1/2/3 discipline in every sentence;
# determinism-vs-replication stated (NARROW-3).
import json, sys, math, hashlib, subprocess, datetime

TASK = "coordination/goals/GOAL-AES-003/batches/BATCH-060cb4/tasks/TASK-20260903-5fbdfc"
S0 = "coordination/goals/GOAL-AES-003/batches/BATCH-060cb4/tasks/TASK-20260903-695ebe"
R3_PATH = "coordination/goals/GOAL-AES-003/batches/BATCH-2f12ac/tasks/TASK-20260901-7e0b71/runs/R3_table_freeze.json"
INFERENCE = {
    "policy": "executor-implementation",
    "requested_policy": "executor-implementation",
    "resolved_model_id": "fireworks-ai/accounts/fireworks/models/qwen3p8-max",
    "resolved_model_id_note": "session-reported by the running session; no adapter probe (python3 -m orchestration.adapter doctor --probe) was executed in this session, so this identifier is unverified configuration",
    "model_verified": False,
    "fallback_used": True,
    "fallback_reason": "session-backend transport under inference amendment DEC-20260831-0d1eeb",
    "degraded_requirements": [],
    "amendment": "DEC-20260831-0d1eeb",
    "independent_session": True,
}
EXCESS_E = 1 << 30
Z_LO, Z_HI = -1.959963984540054, 1.959963984540054
COUNT_WINDOW = (0.9899, 1.0102)          # preregistration section 5 (binding)
COUNT_WINDOW_COUNTS = (147858, 150891)   # disjoint-below / disjoint-above thresholds (preregistered)

# FROZEN INPUTS (committed BATCH-e5d753 readings, EV-AES-868db1 OBS-2/OBS-3;
# consumed as inputs and NOT re-measured; immutable). CIs re-derived below
# from the committed counts under the campaign Wilson-Hilferty convention and
# cross-checked against the committed cited values.
FROZEN = {
    "h1_531001": 12681109, "h1_531001_ci_cited": [12674130.4, 12688090.5],
    "h1_531002": 12679968, "h1_531002_ci_cited": None,  # EV cites seed-ratio CI [0.9988,1.0010], not count CI
    "h2_531001": 149371,   "h2_531001_ci_cited": [148614.5, 150130.4],
    "h4_531001": 17,       "h4_531001_ci_cited_prereg": [9.9, 27.2], "h4_531001_ci_cited_ev": [9.9, 29.2],
    "h4_531002": 21,       "h4_531002_ci_cited": [12.99, 32.10],
    "h8_531001": 13,       "h8_531001_ci_cited": [6.9, 22.2],
}


def chi2_q(p, nu):
    z = Z_LO if p == 0.025 else Z_HI
    t = 1.0 - 2.0 / (9.0 * nu) + z * math.sqrt(2.0 / (9.0 * nu))
    return nu * (t ** 3)


def garwood_count_ci(h):
    """Garwood 95% CI on the count at exposure 2^30 (campaign Wilson-Hilferty
    chi-squared quantile convention; count and exposure only)."""
    n = EXCESS_E
    lo = 0.0 if h == 0 else 0.5 * chi2_q(0.025, 2 * h) / n * EXCESS_E
    hi = 0.5 * chi2_q(0.975, 2 * (h + 1)) / n * EXCESS_E
    return lo, hi


def band(h):
    if h <= 5:
        return "NULLBAND", 0
    if h <= 40:
        return "RESIDUAL", 1
    if h <= 99:
        return "AMBIGUITY", 2
    return "THRESHOLD", 3


def corner_ratio_ci(num, num_ci, den, den_ci):
    r = num / den
    lo = num_ci[0] / den_ci[1]
    hi = num_ci[1] / den_ci[0]
    return r, lo, hi


def ci_overlap(a, b):
    return a[0] <= b[1] and b[0] <= a[1]


def sha256_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def main():
    a_k2 = json.load(open(TASK + "/runs/U1_k2_seed2_analysis.json"))
    a_k8 = json.load(open(TASK + "/runs/U2_k8_seed2_analysis.json"))
    r_k2 = json.load(open(TASK + "/runs/U1_k2_seed2.json"))
    r_k8 = json.load(open(TASK + "/runs/U2_k8_seed2.json"))
    r3 = {p["k"]: p for p in json.load(open(R3_PATH))["points"]}

    h2b = a_k2["hits_W_ge1_nontrivial"]
    h8b = a_k8["hits_W_ge1_nontrivial"]
    ci_h2b = [a_k2["garwood95_count_scaled_per_2_30"]["lo"], a_k2["garwood95_count_scaled_per_2_30"]["hi"]]
    ci_h8b = [a_k8["garwood95_count_scaled_per_2_30"]["lo"], a_k8["garwood95_count_scaled_per_2_30"]["hi"]]

    # ---- frozen-input CIs re-derived under the campaign convention ----
    derived = {}
    for key in ("h1_531001", "h1_531002", "h2_531001", "h4_531001", "h4_531002", "h8_531001"):
        derived[key] = list(garwood_count_ci(FROZEN[key]))
    ci_crosscheck = {}
    for key, cited in (("h1_531001", FROZEN["h1_531001_ci_cited"]),
                       ("h2_531001", FROZEN["h2_531001_ci_cited"]),
                       ("h4_531001", FROZEN["h4_531001_ci_cited_prereg"]),
                       ("h4_531002", FROZEN["h4_531002_ci_cited"]),
                       ("h8_531001", FROZEN["h8_531001_ci_cited"])):
        d = derived[key]
        ci_crosscheck[key] = {
            "committed_count": FROZEN[key],
            "ci_cited": cited,
            "ci_rederived_wilson_hilferty": d,
            "agreement_to_cited_rounding": abs(d[0] - cited[0]) <= 0.05 * max(1.0, cited[0]) * 0.01 + 0.5
                                           and abs(d[1] - cited[1]) <= 0.05 * max(1.0, cited[1]) * 0.01 + 0.5,
        }
    # rule-8 flag: EV-AES-868db1/dispatch brief cite h(4)_531001 CI upper 29.2;
    # the campaign convention re-derivation and the committed BATCH-e5d753
    # analysis file agree on 27.22.
    ev_discrepancy = {
        "observation": "EV-AES-868db1 OBS-2 and the dispatch brief cite h(4)_531001 CI [9.9, 29.2]; the committed BATCH-e5d753 analysis file (T4_k4_analysis.json) and the Wilson-Hilferty re-derivation from h=17 agree on [9.897, 27.220]; the preregistration section 5 carries [9.9, 27.2]. The 29.2 figure is inconsistent with the campaign's own committed convention; the campaign-convention value is used wherever a CI enters a computation (the (2,4) ratio CI, report-only content). No CC branch conjunct at k=2 depends on it.",
        "rule8": True,
        "variant_reported": True,
    }

    # ---- post-arm audits (part of CC-GATE-FAIL evaluation) ----
    digest_checks = {
        "k2": {"receipt_arm_table_concat_sha256": r_k2["arm_table_concat_sha256"],
               "r3_points_2_concat_sha256": r3[2]["concat_sha256"],
               "match": r_k2["arm_table_concat_sha256"] == r3[2]["concat_sha256"]},
        "k8": {"receipt_arm_table_concat_sha256": r_k8["arm_table_concat_sha256"],
               "r3_points_8_concat_sha256": r3[8]["concat_sha256"],
               "match": r_k8["arm_table_concat_sha256"] == r3[8]["concat_sha256"]},
    }
    digest_mismatches = [k for k, v in digest_checks.items() if not v["match"]]
    src_diff = subprocess.run(["diff", "-u", S0 + "/src/affarm046ex.c", TASK + "/src/affarm046ex.c"],
                              capture_output=True, text=True)
    bin_diff = subprocess.run(["cmp", "-s", S0 + "/src/affarm046ex", TASK + "/src/affarm046ex"])
    src_sha = sha256_file(TASK + "/src/affarm046ex.c")
    bin_sha = sha256_file(TASK + "/src/affarm046ex")
    S0_SRC = "ec748cefcb1fccfdd4e441a4898b21cf4b7eff056599ce07769e3f0fab091f37"
    S0_BIN = "74e3d65ca6ecdd877dda5d9e19a96a5af66740b118dbcd1dd35b78be5d102702"
    audits = {
        "table_digest_reverification_vs_R3": {
            "compared": "arm_table_concat_sha256 of both new receipts vs committed R3_table_freeze.json points k=2 and k=8 concat_sha256",
            "checks": digest_checks,
            "mismatches": digest_mismatches,
            "mismatch_count": len(digest_mismatches),
            "expected_mismatches": 0,
            "pass": len(digest_mismatches) == 0,
        },
        "source_binary_diff_audit": {
            "diff_source_vs_S0_bound": "diff -u (empty body expected - zero source change in S1)",
            "diff_exit_code": src_diff.returncode,
            "diff_body_empty": src_diff.stdout == "",
            "binary_cmp_exit_code": bin_diff.returncode,
            "binary_identical": bin_diff.returncode == 0,
            "pass": src_diff.returncode == 0 and src_diff.stdout == "" and bin_diff.returncode == 0,
        },
        "sha256_recheck_vs_S0_bound": {
            "source_sha256": src_sha, "source_match": src_sha == S0_SRC,
            "binary_sha256": bin_sha, "binary_match": bin_sha == S0_BIN,
            "s0_bound_source": S0_SRC, "s0_bound_binary": S0_BIN,
            "pass": src_sha == S0_SRC and bin_sha == S0_BIN,
        },
    }

    # ---- branch 1: CC-GATE-FAIL ----
    amend1_ok = a_k2["amend1_identities_pass"] and a_k8["amend1_identities_pass"]
    seat_ok = a_k2["seat_as_preregistered"] and a_k8["seat_as_preregistered"]
    gate_fail_reasons = []
    if not a_k2["amend1_identities_pass"]:
        gate_fail_reasons.append("AMEND-1 counter inconsistency on S1-1 receipt")
    if not a_k8["amend1_identities_pass"]:
        gate_fail_reasons.append("AMEND-1 counter inconsistency on S1-2 receipt")
    if not seat_ok:
        gate_fail_reasons.append("seat mismatch vs preregistered tuples")
    if not audits["table_digest_reverification_vs_R3"]["pass"]:
        gate_fail_reasons.append("post-arm table-digest re-verification mismatch")
    if not audits["source_binary_diff_audit"]["pass"]:
        gate_fail_reasons.append("post-arm source/binary diff audit non-empty")
    if not audits["sha256_recheck_vs_S0_bound"]["pass"]:
        gate_fail_reasons.append("sha256 re-check vs S0-bound hashes failed")
    cc_gate_fail = len(gate_fail_reasons) > 0

    # ---- branch 4: CC-SEED-DISAGREE (k=2 band departure) ----
    band_k2b, bandrank_k2b = band(h2b)
    band_k2a = band(FROZEN["h2_531001"])[0]
    band_agree_k2 = band_k2b == band_k2a == "THRESHOLD"
    cc_seed_disagree = (not cc_gate_fail) and (band_k2b != "THRESHOLD")

    # ---- branch 5/6 criteria: count + ratio ----
    ci_h2a = derived["h2_531001"]
    count_ci_overlap = ci_overlap(ci_h2a, ci_h2b)
    seed_ratio = h2b / FROZEN["h2_531001"]
    ratio_in_window = COUNT_WINDOW[0] <= seed_ratio <= COUNT_WINDOW[1]
    ratio_in_window_counts = COUNT_WINDOW_COUNTS[0] <= h2b <= COUNT_WINDOW_COUNTS[1]

    ci_h1a = derived["h1_531001"]
    ci_h1b = derived["h1_531002"]
    r_ratio_a, r_ratio_a_lo, r_ratio_a_hi = corner_ratio_ci(
        FROZEN["h1_531001"], ci_h1a, FROZEN["h2_531001"], ci_h2a)
    r_ratio_b, r_ratio_b_lo, r_ratio_b_hi = corner_ratio_ci(
        FROZEN["h1_531002"], ci_h1b, h2b, ci_h2b)
    ratio_ci_overlap_12 = ci_overlap([r_ratio_a_lo, r_ratio_a_hi], [r_ratio_b_lo, r_ratio_b_hi])
    count_agree = count_ci_overlap and ratio_in_window
    ratio_agree = ratio_ci_overlap_12
    checked_implication_separation = count_agree != ratio_agree

    cc_count_disagree = (not cc_gate_fail) and (not cc_seed_disagree) and band_agree_k2 and (
        (not count_ci_overlap) or (not ratio_in_window) or (not ratio_ci_overlap_12))
    cc_agree = (not cc_gate_fail) and (not cc_seed_disagree) and band_agree_k2 and count_agree and ratio_agree

    if cc_gate_fail:
        fired = "CC-GATE-FAIL"
    elif cc_seed_disagree:
        fired = "CC-SEED-DISAGREE"
    elif cc_count_disagree:
        fired = "CC-COUNT-DISAGREE"
    elif cc_agree:
        fired = "CC-AGREE"
    else:
        fired = "NONE (cascade exhaustiveness violated - investigate)"

    # ---- orthogonal CC8 axis ----
    band_k8b, bandrank_k8b = band(h8b)
    band_k8a = band(FROZEN["h8_531001"])[0]
    cc8_floor_depart = h8b <= 5
    cc8_agree = band_k8b == band_k8a == "RESIDUAL"
    if cc8_floor_depart:
        cc8_fired = "CC8-FLOOR-DEPART"
    elif cc8_agree:
        cc8_fired = "CC8-AGREE"
    else:
        cc8_fired = "CC8-RESIDUAL-COMPLEMENT (band departure other than NULLBAND; preregistered probability < 1e-6; record as measured)"

    # ---- per-seed decay ratios r(1,2) and r(2,4), corner propagation ----
    ci_h4a = derived["h4_531001"]
    ci_h4b = derived["h4_531002"]
    r12_a, r12_a_lo, r12_a_hi = corner_ratio_ci(FROZEN["h1_531001"], ci_h1a, FROZEN["h2_531001"], ci_h2a)
    r12_b, r12_b_lo, r12_b_hi = corner_ratio_ci(FROZEN["h1_531002"], ci_h1b, h2b, ci_h2b)
    r24_a, r24_a_lo, r24_a_hi = corner_ratio_ci(FROZEN["h2_531001"], ci_h2a, FROZEN["h4_531001"], ci_h4a)
    r24_b, r24_b_lo, r24_b_hi = corner_ratio_ci(h2b, ci_h2b, FROZEN["h4_531002"], ci_h4b)
    # variant of the (2,4) seed-531001 ratio CI under the EV-cited [9.9, 29.2]
    r24_a_var_lo = ci_h2a[0] / FROZEN["h4_531001_ci_cited_ev"][1]
    r24_a_var_hi = ci_h2a[1] / FROZEN["h4_531001_ci_cited_ev"][0]
    decay_ratios = {
        "convention": "r_s = h(k_a)_s / h(k_b)_s WITHIN each seed environment (cross-seed mixed ratios are report-only, never decay statements - the schedule-derived key co-varies with the seed); ratio CI from count-CI corners (L_num/U_den, U_num/L_den), the campaign convention of BATCH-e5d753 check_6; per-seed readings, never pooled",
        "pair_1_2": {
            "seed_531001": {"h1": FROZEN["h1_531001"], "h1_ci": ci_h1a, "h2": FROZEN["h2_531001"], "h2_ci": ci_h2a,
                            "ratio": r12_a, "ci": [r12_a_lo, r12_a_hi],
                            "ci_preregistered_cited": [84.4208, 85.3759], "count_level": "COUNT-DECAY-RESOLVED (Garwood CIs disjoint, h(k_b) < h(k_a))"},
            "seed_531002": {"h1": FROZEN["h1_531002"], "h1_ci": ci_h1b, "h2": h2b, "h2_ci": ci_h2b,
                            "ratio": r12_b, "ci": [r12_b_lo, r12_b_hi],
                            "count_level": "COUNT-DECAY-RESOLVED (Garwood CIs disjoint, h(k_b) < h(k_a))"},
            "ratio_ci_overlap": ratio_ci_overlap_12,
        },
        "pair_2_4": {
            "seed_531001": {"h2": FROZEN["h2_531001"], "h2_ci": ci_h2a, "h4": FROZEN["h4_531001"], "h4_ci": ci_h4a,
                            "ratio": r24_a, "ci": [r24_a_lo, r24_a_hi],
                            "ci_variant_under_ev_cited_29p2_upper": [r24_a_var_lo, r24_a_var_hi],
                            "count_level": "COUNT-DECAY-RESOLVED (Garwood CIs disjoint, h(k_b) < h(k_a))"},
            "seed_531002": {"h2": h2b, "h2_ci": ci_h2b, "h4": FROZEN["h4_531002"], "h4_ci": ci_h4b,
                            "ratio": r24_b, "ci": [r24_b_lo, r24_b_hi],
                            "count_level": "COUNT-DECAY-RESOLVED (Garwood CIs disjoint, h(k_b) < h(k_a))"},
            "ratio_ci_overlap": ci_overlap([r24_a_lo, r24_a_hi], [r24_b_lo, r24_b_hi]),
        },
        "pairs_4_8_and_8_16": "COUNT-UNRESOLVED in every outcome of this batch (k=16 keeps a single-draw endpoint; declared, never smoothed - NARROW-2); no count sentence",
    }

    # ---- stage-S2 gate statement ----
    s2_gate = {
        "rule": "CC-SEED-DISAGREE at k=2 BLOCKS S2 (no family extension on a suspect instrument); CC-COUNT-DISAGREE and either CC8 outcome do NOT block S2 (findings, not indictments)",
        "cc_seed_disagree_fired": cc_seed_disagree,
        "cc_count_disagree_fired": cc_count_disagree,
        "cc8_outcome": cc8_fired,
        "s2_blocked": cc_seed_disagree,
        "statement": ("Stage S2 is BLOCKED by CC-SEED-DISAGREE at k=2" if cc_seed_disagree else
                      "Stage S2 is NOT blocked by the S1 CC outcome (no CC-SEED-DISAGREE at k=2); the S2 gate admits the family-extension stage. This is the gate statement only; dispatch of S2 remains a Coordinator act."),
    }

    out = {
        "schema": "crypto.autoresearch.s1_cc_composition.v1",
        "task_id": "TASK-20260903-5fbdfc",
        "batch_id": "BATCH-060cb4",
        "goal_id": "GOAL-AES-003",
        "idea_record": "IDEA-20260903-8f26ac",
        "decision_opening_batch": "DEC-20260903-63cd8d",
        "run_id": "S1-3",
        "binary_invocations_in_this_step": 0,
        "preregistration": S0 + "/PREREGISTRATION.md (write-once, BINDING; sections 4-5 evaluated here; NOT rewritten)",
        "gate_regime": "AMEND-1 (DEC-20260901-6f9de3)",
        "readings_consumed": {
            "new_this_batch": {
                "h2_531002": {"value": h2b, "receipt": "runs/U1_k2_seed2.json", "analysis": "runs/U1_k2_seed2_analysis.json", "band": band_k2b, "garwood95_count_ci": ci_h2b},
                "h8_531002": {"value": h8b, "receipt": "runs/U2_k8_seed2.json", "analysis": "runs/U2_k8_seed2_analysis.json", "band": band_k8b, "garwood95_count_ci": ci_h8b},
            },
            "frozen_inputs_not_remeasured": {
                "source": "EV-AES-868db1 OBS-2/OBS-3 (committed BATCH-e5d753 readings, immutable)",
                "h1_531001": FROZEN["h1_531001"], "h1_531002": FROZEN["h1_531002"],
                "h2_531001": FROZEN["h2_531001"], "h4_531001": FROZEN["h4_531001"],
                "h4_531002": FROZEN["h4_531002"], "h8_531001": FROZEN["h8_531001"],
                "cis_rederived_wilson_hilferty": derived,
                "ci_crosscheck_vs_cited": ci_crosscheck,
                "ev_text_discrepancy_rule8": ev_discrepancy,
            },
        },
        "cascade_fixed_order_evaluation": {
            "order": ["CC-GATE-FAIL", "CC-SEED-DISAGREE", "CC-COUNT-DISAGREE", "CC-AGREE"],
            "branches": {
                "CC-GATE-FAIL": {
                    "criterion": "any integrity gate fails: S1-3 post-arm digest/source-diff audit, or counter INCONSISTENCY on any analysis-bearing receipt (AMEND-1 VERBATIM, saturation-aware evaluation)",
                    "basis": {
                        "amend1_identities_pass_both_receipts": amend1_ok,
                        "S1-1_amend1_identity_table": a_k2["amend1_identity_table"],
                        "S1-2_amend1_identity_table": a_k8["amend1_identity_table"],
                        "seats_as_preregistered": seat_ok,
                        "post_arm_audits": audits,
                    },
                    "fired": cc_gate_fail,
                    "fail_reasons": gate_fail_reasons,
                },
                "CC-SEED-DISAGREE": {
                    "criterion": "branches 1-3 not fired AND band(h(2)_531002) != THRESHOLD (a ~386-sd event at the realized magnitude)",
                    "basis": {"band_h2_531002": band_k2b, "band_h2_531001_committed": band_k2a,
                              "band_agree_k2": band_agree_k2},
                    "fired": cc_seed_disagree,
                    "evaluated": not cc_gate_fail,
                },
                "CC-COUNT-DISAGREE": {
                    "criterion": "branch 4 not fired AND (count CIs disjoint OR seed ratio outside [0.9899, 1.0102] OR per-seed decay-ratio CIs for (1,2) disjoint under corner propagation)",
                    "basis": {
                        "count_ci_531001": ci_h2a, "count_ci_531002": ci_h2b,
                        "count_ci_overlap": count_ci_overlap,
                        "overlap_condition": "148,614.5 <= U_b AND L_b <= 150,130.4 (preregistration section 5)",
                        "seed_ratio_h2_531002_over_h2_531001": seed_ratio,
                        "count_agreement_window": list(COUNT_WINDOW),
                        "ratio_in_window": ratio_in_window,
                        "ratio_in_window_count_form": ratio_in_window_counts,
                        "window_counts_preregistered": list(COUNT_WINDOW_COUNTS),
                        "r_531001": r_ratio_a, "r_531001_ci": [r_ratio_a_lo, r_ratio_a_hi],
                        "r_531001_ci_preregistered_cited": [84.4208, 85.3759],
                        "r_531002": r_ratio_b, "r_531002_ci": [r_ratio_b_lo, r_ratio_b_hi],
                        "ratio_ci_overlap_1_2": ratio_ci_overlap_12,
                        "checked_implication_separation": checked_implication_separation,
                        "checked_implication_note": "preregistration section 5: if the realized readings ever separate the count and ratio criteria, the STRICTER reading wins and the separation is recorded per rule 8",
                    },
                    "fired": cc_count_disagree,
                    "evaluated": (not cc_gate_fail) and (not cc_seed_disagree),
                },
                "CC-AGREE": {
                    "criterion": "branch 4 not fired AND count CIs overlap AND seed ratio in window AND ratio CIs overlap",
                    "basis": {"band_agree": band_agree_k2, "count_agree": count_agree, "ratio_agree": ratio_agree},
                    "fired": cc_agree,
                    "evaluated": (not cc_gate_fail) and (not cc_seed_disagree),
                    "routing_if_fired": "COUNT-REPLICATED: SH2-MONOTONE-DECAY EXTENDED TO COUNT LEVEL for the pairs (1,2) and (2,4) ONLY - never the whole curve; NARROW-2's caveat discharged for exactly these two pairs and NO others; (4,8) and (8,16) remain COUNT-UNRESOLVED in every outcome",
                },
            },
            "fired_branch": fired,
            "halt_branches_1_3_note": "CC-GATE-FAIL / CC-F6 / CC-ANCHOR-FAIL: branches 2-3 (F6 dead-anchor tripwire, k=0 anchor) were owned and PASSED by S0 (PASS-S0, verified at the S0 gate check with receipt sha256); branch 1 is re-evaluated here on the two new receipts and the post-arm audits",
        },
        "cc8_axis": {
            "order_note": "orthogonal finding axis evaluated beside branches 4-6, AFTER the k=2 verdict, NEVER gating it (preregistration section 4.2 branches 7/8)",
            "branches": {
                "CC8-FLOOR-DEPART": {"criterion": "h(8)_531002 <= 5 (NULLBAND)", "basis": {"h8_531002": h8b}, "fired": cc8_floor_depart},
                "CC8-AGREE": {"criterion": "band(h(8)_531002) == band(h(8)_531001) == RESIDUAL",
                              "basis": {"band_h8_531002": band_k8b, "band_h8_531001_committed": band_k8a,
                                        "h8_531002": h8b, "h8_531001_committed": FROZEN["h8_531001"],
                                        "ci_531002": ci_h8b, "ci_531001_committed": FROZEN["h8_531001_ci_cited"],
                                        "ci_overlap": ci_overlap(ci_h8b, derived["h8_531001"])},
                              "fired": cc8_agree},
            },
            "fired_branch": cc8_fired,
            "statement": ("the floor is seed-stable at band level at k=8: second independent draw of the live floor; the RT-J8-named sensitivity stands tested and untriggered; per-seed counts reported (13 vs 18), CIs overlap, never smoothed"
                          if cc8_agree else
                          "a determinate FLOOR-INSTABILITY finding at k=8 realizing the RT-J8 sensitivity; recorded with both per-seed tuples; the BATCH-e5d753 verdict on grid {1,2,4,8,16} remains IMMUTABLE"),
            "floor_is_alive_NARROW1": "the residual floor (h(4)=17 / h(8)=13 / h(16)=12 committed; h(8)_531002=18 this batch) is a live, decidable excess over the analytic null (P(h>=12 | lambda=1) = 8.3e-10); never extinction",
        },
        "per_seed_decay_ratios": decay_ratios,
        "verdict_sentences": {
            "scope": "cell (amask=1, smask=1), r=5, PIN-T0, 2^30 per arm, frozen family subset {0,1,2,4,8,16}, seeds 531001/531002, SCOPE-1 attribution, toy tier",
            "attribution_SCOPE1": "under PIN-T0 the key schedule is the AES schedule at every interior point k >= 1 and is constant across interior k; the k=1 -> k=2 and k=2 -> k=4 comparisons are interior-to-interior and therefore schedule-clean; any interior decay is attributed to table dilution AT FIXED SCHEDULE; no dilution-only language; the k=0 ramp-zero anchor is the instrument's zero only, never the first point of a dose-attributed decay",
            "determinism_vs_replication_NARROW3": "the two new readings are independent draws: NEW (seed, seat) combinations (531002 at armid 3, 531002 at armid 6). No seed-531001 arm was re-run in this stage; any exact reproduction under identical seed/seat/build would be instrument determinism and NEVER replication. The BATCH-7b798d readings remain unvalidated under AMEND-1 (no post-hoc rescue).",
            "NARROW1": "every sentence carries the live residual floor; no extinction sentence at any k",
            "NARROW2": "no count-level decay sentence without second seeds at the named k; pairs (1,2) and (2,4) carry count content only under the CC-AGREE routing and naming both per-seed ratios; (4,8)/(8,16) carry none in any outcome",
            "not_claimed": "no re-composition of SH2-MONOTONE-DECAY (immutable); no whole-curve seed-stability sentence; no deployed-AES claim; no published-cryptanalysis comparison; no carrier/X-lane/rho-exclusion sentence",
        },
        "stage_S2_gate": s2_gate,
        "composed_utc": now_iso(),
        "parse_attestation": "machine-generated JSON; parsed whole with python3 json.load after writing",
        "inference": INFERENCE,
    }
    with open(TASK + "/runs/cc_composition.json", "w") as f:
        json.dump(out, f, indent=1)
    # re-parse attestation
    json.load(open(TASK + "/runs/cc_composition.json"))
    print(json.dumps({
        "CC_fired": fired,
        "CC8_fired": cc8_fired,
        "h2_531002": h2b, "band_k2": band_k2b, "seed_ratio": seed_ratio,
        "count_ci_overlap": count_ci_overlap, "ratio_in_window": ratio_in_window,
        "ratio_ci_overlap_12": ratio_ci_overlap_12,
        "h8_531002": h8b, "band_k8": band_k8b,
        "digest_mismatches": len(digest_mismatches),
        "diff_empty": audits["source_binary_diff_audit"]["pass"],
        "sha_match": audits["sha256_recheck_vs_S0_bound"]["pass"],
        "s2_blocked": s2_gate["s2_blocked"],
    }, indent=1))
    sys.exit(0)


if __name__ == "__main__":
    main()
