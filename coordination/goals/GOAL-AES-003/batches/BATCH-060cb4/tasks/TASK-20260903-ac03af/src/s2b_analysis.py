#!/usr/bin/env python3
# s2b_analysis.py -- TASK-20260903-ac03af (BATCH-060cb4, GOAL-AES-003), Stage S2b
# Fresh for this task. Per-receipt analysis of the S2b k=3 sub-locator arms
# under the AMEND-1 counter-inconsistency gate as carried verbatim in the
# BINDING S0 preregistration (TASK-20260903-695ebe/PREREGISTRATION.md
# sections 1-3; not rewritten). Modes:
#
#   python3 src/s2b_analysis.py k3seed1 <receipt.json> <analysis_out.json>
#       S2b-2 k=3 SUB-LOCATOR PRIMARY (S_3, r5, amask=1, smask=1, 2^30, seed
#       531001, armid 11, threads 4): FIRST-EVER k=3 measurement. Overflow
#       predicted saturated under the multiplicative prior (~1759 hits ->
#       overflow ~735), unsaturated legal under AMEND-1 if realized <= 1024.
#   python3 src/s2b_analysis.py k3seed2 <receipt.json> <analysis_out.json>
#       S2b-3 k=3 SECOND SEED (S_3, r5, amask=1, smask=1, 2^30, seed 531002,
#       armid 11, threads 4): UNCONDITIONAL within the stage (two-draw entry
#       discipline per NARROW-2 applied prospectively to the new point).
#
# Per receipt: hits (W_ge1_nontrivial), whist/W_ge1_by_word breakdown, excess
# ratio vs the frozen comparator excess_E = 2^30, excess over the run-internal
# accidental-hit rate, Garwood 95% CI (campaign Wilson-Hilferty chi-squared
# quantile convention; count and exposure only), band vs the preregistered
# floors (NULLBAND <=5, RESIDUAL 6-40, AMBIGUITY 41-99, THRESHOLD >=100),
# full AMEND-1 identity table (saturation-aware overflow identity;
# sum(zhist)==nontrivial per the DEV-S0-1 correction; all conjuncts; NO
# detail-log-derived quantities), AMEND-1(c) detail-log attestation, and the
# per-receipt table-digest comparison vs the PRE-ARM committed R4 k=3 entry
# (arm_table_concat_sha256 vs R4 points[k=3].concat_sha256 =
# 922e24c9c065eb79c7efcbd536b41111ad70d11a1a49cf56207832e4949c6262; k=3 is
# not in R3 by construction, so the extended freeze commitment is the
# reference).
#
# Exit codes: 0 pass; 12 = CC3-GATE-FAIL (AMEND-1 counter inconsistency,
# seat mismatch, or table-digest mismatch vs the pre-arm commitment).
import json, sys, math, datetime

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
EXCESS_E = 1 << 30          # frozen comparator convention
Z_LO, Z_HI = -1.959963984540054, 1.959963984540054
R4_PATH = ("coordination/goals/GOAL-AES-003/batches/BATCH-060cb4/tasks/"
           "TASK-20260903-7893b2/runs/R4_table_freeze_ext.json")
K3_COMMITTED_CONCAT = "922e24c9c065eb79c7efcbd536b41111ad70d11a1a49cf56207832e4949c6262"

SEATS = {
    "k3seed1": {"k": 3, "run_id": "S2b-2", "arm_id": 11, "seed": 531001,
                "positions": [0, 4, 8],
                "role": "k=3 SUB-LOCATOR PRIMARY: FIRST-EVER k=3 measurement (extended family point; pre-arm committed R4 digest)",
                "saturation_prediction": "saturated under the multiplicative prior (~1759 hits -> overflow ~735); unsaturated legal under AMEND-1 if realized <= 1024 (both paths legal, admissible set unchanged)"},
    "k3seed2": {"k": 3, "run_id": "S2b-3", "arm_id": 11, "seed": 531002,
                "positions": [0, 4, 8],
                "role": "k=3 SECOND SEED: UNCONDITIONAL within the stage - a new point enters this campaign with two independent draws (two-draw entry discipline; NARROW-2/3 applied prospectively)",
                "saturation_prediction": "saturated under the multiplicative prior; unsaturated legal under AMEND-1 if realized <= 1024"},
}


def chi2_q(p, nu):
    # Wilson-Hilferty chi-squared quantile (campaign design-time convention)
    z = Z_LO if p == 0.025 else Z_HI
    t = 1.0 - 2.0 / (9.0 * nu) + z * math.sqrt(2.0 / (9.0 * nu))
    return nu * (t ** 3)


def garwood_ci(h, n):
    lo = 0.0 if h == 0 else 0.5 * chi2_q(0.025, 2 * h) / n
    hi = 0.5 * chi2_q(0.975, 2 * (h + 1)) / n
    return lo, hi


def band(h):
    if h <= 5:
        return "NULLBAND", 0
    if h <= 40:
        return "RESIDUAL", 1
    if h <= 99:
        return "AMBIGUITY", 2
    return "THRESHOLD", 3


def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def amend1_identities(r):
    """AMEND-1 counter-identity suite (PREREGISTRATION section 2). 'hits' is
    W_ge1_nontrivial in this instrument; logged_detail_records is the number
    of hit_trials entries (sum over threads of min(hits_t, HIT_LOG_CAP))."""
    hits = r["W_ge1_nontrivial"]
    nt = r["nontrivial_trials"]
    n = r["trials"]
    cap = r["hit_log_cap"]
    nthr = r["threads"]
    logged = len(r.get("hit_trials", []))
    saturated = hits > nthr * cap
    overflow_expected = hits - nthr * cap if saturated else 0
    moment_lhs = sum(r["W_ge1_by_word"])
    moment_rhs = sum(w * r["whist"][w] for w in range(1, 5))
    zhist_sum = sum(r["zhist"])
    trivial = r["trivial_swaps_excluded"]
    return {
        "hits_field_mapping": "hits := W_ge1_nontrivial (receipt carries no field literally named hits)",
        "sum_whist_eq_nontrivial": sum(r["whist"]) == nt,
        "h_eq_sum_whist_ge1": hits == sum(r["whist"][1:5]),
        "moment_identity_word_split": moment_lhs == moment_rhs,
        "moment_identity_values": {"sum_W_ge1_by_word": moment_lhs, "sum_W_times_whist": moment_rhs},
        "sum_zhist_eq_nontrivial": zhist_sum == nt,
        "sum_zhist_eq_trials_literal_informational": zhist_sum == n,
        "sum_zhist_note": ("sum(zhist)=%d == nontrivial_trials=%d (DEV-S0-1 corrected "
                           "internal identity); literal '==trials' shorthand holds iff "
                           "trivial_swaps_excluded==0 (here %d)" % (zhist_sum, nt, trivial)),
        "sum_ewhist_all_eq_nontrivial": sum(r["ewhist_all"]) == nt,
        "sum_ewhist_hit_eq_h": sum(r["ewhist_hit"]) == hits,
        "sum_ewhist_miss_eq_nontrivial_minus_h": sum(r["ewhist_miss"]) == nt - hits,
        "saturation_status": "saturated" if saturated else "unsaturated",
        "logged_detail_records": logged,
        "logged_detail_records_expected": nthr * cap if saturated else hits,
        "logged_detail_records_identity": logged == (nthr * cap if saturated else hits),
        "overflow_observed": r["hit_log_overflow"],
        "overflow_expected": overflow_expected,
        "overflow_identity": r["hit_log_overflow"] == overflow_expected,
        "overflow_saturated_form_informational": {
            "value_hits_minus_threads_x_cap": hits - nthr * cap,
            "matches_observed": r["hit_log_overflow"] == hits - nthr * cap,
            "applies": saturated,
        },
        "trials_accounting": trivial + nt == n,
    }


def amend1_pass(ids):
    keys = ("sum_whist_eq_nontrivial", "h_eq_sum_whist_ge1",
            "moment_identity_word_split", "sum_zhist_eq_nontrivial",
            "sum_ewhist_all_eq_nontrivial", "sum_ewhist_hit_eq_h",
            "sum_ewhist_miss_eq_nontrivial_minus_h",
            "logged_detail_records_identity", "overflow_identity",
            "trials_accounting")
    return all(ids[k] for k in keys)


def detail_log_attestation(r):
    return {
        "statement": "no analysis-bearing quantity is derived from the capped detail log (hit_e_detail / hit_trials); all quantities are counter-derived",
        "hit_e_detail_records_present": len(r.get("hit_e_detail", [])),
        "hit_trials_entries_present": len(r.get("hit_trials", [])),
        "detail_log_used_for_any_reported_quantity": False,
        "detail_log_status": "report-only enabling data under the no-reopen clause; no branch conjunct consumes it",
    }


def analyze(mode, path, out_path):
    seat = SEATS[mode]
    with open(path) as f:
        r = json.load(f)
    hits = r["W_ge1_nontrivial"]
    nt = r["nontrivial_trials"]
    ids = amend1_identities(r)
    checks = {
        "oracle_r5": r["oracle"] == "live_aes_r5_affarm046ex_derivative_of_affarm046",
        "amask_1": r["amask"] == 1,
        "smask_1": r["smask"] == 1,
        "log2N": r["log2N"] == 30,
        "trials_eq_2pow_log2N": r["trials"] == (1 << 30),
        "seed": r["seed"] == seat["seed"],
        "arm_id": r["arm_id"] == seat["arm_id"],
        "threads_4": r["threads"] == 4,
        "sbox_label": r["sbox"] == "aes",
        "sbox_k": r["sbox_k"] == seat["k"],
        "sbox_positions_as_preregistered_seat": r["sbox_positions"] == seat["positions"],
        "schedule_pin_T0": r["schedule_pin"] == "PIN-T0",
        "schedule_pin_position_0": r["schedule_pin_position"] == 0,
        "schedule_pin_decision": r["schedule_pin_decision"] == "DEC-20260901-fb6f11",
        "hit_log_cap_256": r["hit_log_cap"] == 256,
    }
    seat_ok = all(checks.values())
    lo, hi = garwood_ci(hits, nt)
    b, br = band(hits)
    a1_ok = amend1_pass(ids)
    with open(R4_PATH) as f:
        r4 = json.load(f)
    r4_entry = {p["k"]: p for p in r4["points"]}[seat["k"]]
    digest_ok = (r["arm_table_concat_sha256"] == r4_entry["concat_sha256"]
                 and r4_entry["concat_sha256"] == K3_COMMITTED_CONCAT)
    verdict = "PASS" if (a1_ok and seat_ok and digest_ok) else "CC3-GATE-FAIL"
    out = {
        "schema": "crypto.autoresearch.s2b_k3_analysis.v1",
        "task_id": "TASK-20260903-ac03af",
        "batch_id": "BATCH-060cb4",
        "goal_id": "GOAL-AES-003",
        "idea_record": "IDEA-20260903-8f26ac",
        "decision_opening_batch": "DEC-20260903-63cd8d",
        "gate_regime": "AMEND-1 (DEC-20260901-6f9de3)",
        "preregistration": "coordination/goals/GOAL-AES-003/batches/BATCH-060cb4/tasks/TASK-20260903-695ebe/PREREGISTRATION.md (write-once, BINDING)",
        "pin_reference": "PIN-T0 (DEC-20260901-fb6f11)",
        "run_id": seat["run_id"],
        "build": "EXTENDED (frozen build + declared k=3 surface extension; source 45808af6..., binary 3ccc377c...; certified PASS-S2a)",
        "receipt": path,
        "arm": r["arm"],
        "k": seat["k"],
        "role": seat["role"],
        "seat": {"sbox": "S_3 diluted table set (P_3 = first three positions of the frozen order)",
                 "rounds": 5, "amask": 1, "smask": 1, "log2N": 30,
                 "seed": seat["seed"], "arm_id": seat["arm_id"], "threads": 4},
        "seat_checks": checks,
        "seat_checks_expected_positions": seat["positions"],
        "seat_as_preregistered": seat_ok,
        "scope_note": "interior-to-interior comparison, schedule-clean under PIN-T0 (SCOPE-1; k=3 is interior, k >= 1); per-seed reading, never pooled; this is an independent draw (new (seed, seat) combination), NOT determinism (NARROW-3); first-ever k=3 measurement, entered with two draws from the start (NARROW-2 two-draw entry discipline)",
        "hits_W_ge1_nontrivial": hits,
        "trivial_swaps_excluded": r["trivial_swaps_excluded"],
        "nontrivial_trials": nt,
        "whist": r["whist"],
        "W_ge1_by_word": r["W_ge1_by_word"],
        "zhist": r["zhist"],
        "band": b,
        "bandrank": br,
        "excess_E": EXCESS_E,
        "excess_ratio_vs_excess_E": hits / EXCESS_E,
        "null_design_rate_value": 1.0,
        "null_expectation_analytic_run_internal": r["null_expectation_analytic"],
        "excess_over_run_internal_null": hits - r["null_expectation_analytic"],
        "garwood95_rate_per_trial": {"lo": lo, "hi": hi,
                                     "method": "Wilson-Hilferty chi-squared quantile (design-time convention)"},
        "garwood95_count_scaled_per_2_30": {"lo": lo * EXCESS_E, "hi": hi * EXCESS_E,
                                            "note": "rate CI scaled by excess_E = 2^30 for readability; nt = 2^30 here"},
        "sensitivity_floors_per_point": {
            "lambda_80_hits_per_2_30": 8.0,
            "lambda_95_hits_per_2_30": 10.5,
            "statement": "a point reading NULLBAND excludes a per-point hit-rate excess >= ~8-10.5 at 80-95% power, and excludes NOTHING below that; within-residual-band trends are NOT resolvable at 2^30 (preregistration section 11)",
        },
        "hit_log_overflow": r["hit_log_overflow"],
        "hit_log_cap": r["hit_log_cap"],
        "saturation_prediction_vs_design_prior": {
            "predicted": seat["saturation_prediction"],
            "realized": ids["saturation_status"],
            "note": "prediction from the flagged multiplicative prior (broken authority; one prior among several, never bet on); realization governs, both paths legal under AMEND-1 with the admissible set unchanged",
        },
        "amend1_identity_table": ids,
        "amend1_identities_pass": a1_ok,
        "amend1_c_detail_log_attestation": detail_log_attestation(r),
        "table_digest_reverification_vs_R4_prearm_commitment": {
            "committed_freeze_file": R4_PATH,
            "k": seat["k"],
            "receipt_arm_table_concat_sha256": r["arm_table_concat_sha256"],
            "r4_points_k3_concat_sha256": r4_entry["concat_sha256"],
            "committed_prearm_digest_constant": K3_COMMITTED_CONCAT,
            "r4_digest_matches_prearm_constant": r4_entry["concat_sha256"] == K3_COMMITTED_CONCAT,
            "match": digest_ok,
            "r4_positions": r4_entry["positions"],
            "r4_bijective_all_positions": r4_entry["bijective_all_positions"],
            "r4_nestedness_check": r4_entry["nestedness_check"],
            "note": "k=3 carries no R3 digest by construction (R3 is the frozen seven-point surface); the pre-arm extended freeze commitment R4 (committed in S2a-4, mtime before any k=3 arm) is the reference",
        },
        "point_verdict": verdict,
        "analyzed_utc": now_iso(),
        "inference": INFERENCE,
    }
    with open(out_path, "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({seat["run_id"]: verdict, "k": seat["k"], "hits": hits,
                      "band": b, "amend1_pass": a1_ok, "seat_ok": seat_ok,
                      "digest_match_R4": digest_ok,
                      "garwood95_count": [lo * EXCESS_E, hi * EXCESS_E]}, indent=1))
    if verdict == "CC3-GATE-FAIL":
        sys.exit(12)
    sys.exit(0)


if __name__ == "__main__":
    if len(sys.argv) != 4 or sys.argv[1] not in SEATS:
        print("usage: s2b_analysis.py k3seed1|k3seed2 <receipt.json> <analysis_out.json>", file=sys.stderr)
        sys.exit(2)
    analyze(sys.argv[1], sys.argv[2], sys.argv[3])
