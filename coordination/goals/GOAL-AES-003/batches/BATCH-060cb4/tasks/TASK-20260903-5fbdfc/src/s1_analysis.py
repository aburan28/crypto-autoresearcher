#!/usr/bin/env python3
# s1_analysis.py -- TASK-20260903-5fbdfc (BATCH-060cb4, GOAL-AES-003), Stage S1
# Fresh for this task. Per-receipt analysis of the S1 second-seed arms under
# the AMEND-1 counter-inconsistency gate as carried verbatim in the BINDING
# S0 preregistration (TASK-20260903-695ebe/PREREGISTRATION.md sections 1-3;
# do not rewrite). Modes:
#
#   python3 src/s1_analysis.py k2 <receipt.json> <analysis_out.json>
#       S1-1 CORE MANDATORY second seed k=2 (S_2, r5, amask=1, smask=1, 2^30,
#       seed 531002, armid 3, threads 4); overflow predicted saturated (~148k).
#   python3 src/s1_analysis.py k8 <receipt.json> <analysis_out.json>
#       S1-2 second seed k=8 (S_8, r5, amask=1, smask=1, 2^30, seed 531002,
#       armid 6, threads 4); overflow predicted unsaturated.
#
# Per receipt: hits (W_ge1_nontrivial), whist/W_ge1_by_word breakdown, excess
# ratio vs the frozen comparator excess_E = 2^30, excess over the run-internal
# accidental-hit rate, Garwood 95% CI (campaign Wilson-Hilferty chi-squared
# quantile convention; count and exposure only), band vs the preregistered
# floors (NULLBAND <=5, RESIDUAL 6-40, AMBIGUITY 41-99, THRESHOLD >=100),
# full AMEND-1 identity table (saturation-aware overflow identity;
# sum(zhist)==nontrivial per the DEV-S0-1 correction; all conjuncts; NO
# detail-log-derived quantities), AMEND-1(c) detail-log attestation, and the
# per-receipt table-digest comparison vs the committed R3 k entry
# (arm_table_concat_sha256 vs points[k].concat_sha256).
#
# Exit codes: 0 pass; 12 = CC-GATE-FAIL (AMEND-1 counter inconsistency or
# seat mismatch); 11 = report-only support issue.
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
R3_PATH = "coordination/goals/GOAL-AES-003/batches/BATCH-2f12ac/tasks/TASK-20260901-7e0b71/runs/R3_table_freeze.json"

SEATS = {
    "k2": {"k": 2, "run_id": "S1-1", "arm_id": 3, "seed": 531002,
           "positions": [0, 4], "saturation_prediction": "saturated (~148k hits, overflow ~148k)"},
    "k8": {"k": 8, "run_id": "S1-2", "arm_id": 6, "seed": 531002,
           "positions": [0, 1, 4, 5, 8, 9, 12, 13], "saturation_prediction": "unsaturated"},
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
    seat_ok = (r["oracle"] == "live_aes_r5_affarm046ex_derivative_of_affarm046"
               and r["amask"] == 1 and r["smask"] == 1 and r["log2N"] == 30
               and r["seed"] == seat["seed"] and r["arm_id"] == seat["arm_id"]
               and r["threads"] == 4 and r["sbox"] == "aes"
               and r["sbox_k"] == seat["k"]
               and r["sbox_positions"] == seat["positions"]
               and r["schedule_pin"] == "PIN-T0"
               and r["schedule_pin_position"] == 0
               and r["schedule_pin_decision"] == "DEC-20260901-fb6f11"
               and r["hit_log_cap"] == 256
               and r["trials"] == (1 << 30))
    lo, hi = garwood_ci(hits, nt)
    b, br = band(hits)
    a1_ok = amend1_pass(ids)
    with open(R3_PATH) as f:
        r3 = json.load(f)
    r3_entry = {p["k"]: p for p in r3["points"]}[seat["k"]]
    digest_ok = r["arm_table_concat_sha256"] == r3_entry["concat_sha256"]
    verdict = "PASS" if (a1_ok and seat_ok and digest_ok) else "CC-GATE-FAIL"
    out = {
        "schema": "crypto.autoresearch.s1_second_seed_analysis.v1",
        "task_id": "TASK-20260903-5fbdfc",
        "batch_id": "BATCH-060cb4",
        "goal_id": "GOAL-AES-003",
        "idea_record": "IDEA-20260903-8f26ac",
        "decision_opening_batch": "DEC-20260903-63cd8d",
        "gate_regime": "AMEND-1 (DEC-20260901-6f9de3)",
        "preregistration": "coordination/goals/GOAL-AES-003/batches/BATCH-060cb4/tasks/TASK-20260903-695ebe/PREREGISTRATION.md (write-once, BINDING)",
        "pin_reference": "PIN-T0 (DEC-20260901-fb6f11)",
        "run_id": seat["run_id"],
        "receipt": path,
        "arm": r["arm"],
        "k": seat["k"],
        "role": ("CORE MANDATORY second seed k=2 (seat-fixed armid convention)" if mode == "k2"
                 else "second seed k=8 (seat-fixed armid convention; RT-J8 floor guard)"),
        "seat": {"sbox": "S_%d diluted table set" % seat["k"], "rounds": 5,
                 "amask": 1, "smask": 1, "log2N": 30, "seed": seat["seed"],
                 "arm_id": seat["arm_id"], "threads": 4},
        "seat_checks": {
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
            "sbox_positions_expected": seat["positions"],
            "schedule_pin_T0": r["schedule_pin"] == "PIN-T0",
            "schedule_pin_position_0": r["schedule_pin_position"] == 0,
            "schedule_pin_decision": r["schedule_pin_decision"] == "DEC-20260901-fb6f11",
            "hit_log_cap_256": r["hit_log_cap"] == 256,
        },
        "seat_as_preregistered": seat_ok,
        "scope_note": "interior-to-interior comparison, schedule-clean under PIN-T0 (SCOPE-1); per-seed reading, never pooled; this is an independent draw (new (seed, seat) combination), NOT determinism (NARROW-3)",
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
            "note": "prediction from the committed VALIDATED BATCH-e5d753 readings (preregistration section 1.1); realization governs",
        },
        "amend1_identity_table": ids,
        "amend1_identities_pass": a1_ok,
        "amend1_c_detail_log_attestation": detail_log_attestation(r),
        "table_digest_reverification_vs_R3": {
            "committed_freeze_file": R3_PATH,
            "k": seat["k"],
            "receipt_arm_table_concat_sha256": r["arm_table_concat_sha256"],
            "r3_points_k_concat_sha256": r3_entry["concat_sha256"],
            "match": digest_ok,
            "r3_positions": r3_entry["positions"],
            "r3_bijective_all_positions": r3_entry["bijective_all_positions"],
            "r3_nestedness_check": r3_entry["nestedness_check"],
        },
        "point_verdict": verdict,
        "analyzed_utc": now_iso(),
        "inference": INFERENCE,
    }
    with open(out_path, "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({seat["run_id"]: verdict, "k": seat["k"], "hits": hits,
                      "band": b, "amend1_pass": a1_ok, "seat_ok": seat_ok,
                      "digest_match_R3": digest_ok,
                      "garwood95_count": [lo * EXCESS_E, hi * EXCESS_E]}, indent=1))
    if verdict == "CC-GATE-FAIL":
        sys.exit(12)
    sys.exit(0)


if __name__ == "__main__":
    if len(sys.argv) != 4 or sys.argv[1] not in SEATS:
        print("usage: s1_analysis.py k2|k8 <receipt.json> <analysis_out.json>", file=sys.stderr)
        sys.exit(2)
    analyze(sys.argv[1], sys.argv[2], sys.argv[3])
