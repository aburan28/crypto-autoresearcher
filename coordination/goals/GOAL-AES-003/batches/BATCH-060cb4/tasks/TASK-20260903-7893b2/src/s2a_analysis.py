#!/usr/bin/env python3
# s2a_analysis.py -- TASK-20260903-7893b2 (BATCH-060cb4, GOAL-AES-003), Stage S2a
# Fresh for this task. Per-receipt analysis of the extended-build battery
# receipts under the AMEND-1 counter-inconsistency gate as carried verbatim
# in the BINDING S0 preregistration (TASK-20260903-695ebe/PREREGISTRATION.md
# sections 1-3; not rewritten). Modes:
#
#   python3 src/s2a_analysis.py gate0x <receipt.json> <analysis_out.json>
#       S2a-2 Gate-0x extended rebuild (aes, r5, 1, 1, 2^30, seed 531001,
#       armid 1, threads 2). Gate receipt + 14-hit continuity reading.
#   python3 src/s2a_analysis.py dead <receipt.json> <analysis_out.json>
#       S2a-5 DEAD ANCHOR on the extended build (aes, r6, 1, 1, 2^30, seed
#       531004, armid 1, threads 4). Gate hits <= 8; tripwire hits >= 9 is
#       CC3-F6. ANALYZED FIRST among extended-build alive readings.
#   python3 src/s2a_analysis.py double <receipt.json> <analysis_out.json>
#       S2a-6 determinism-double receipt (S_1, r5, 1, 1, log2N=20, seed
#       531001, armid 2, threads 4). Realized overflow > 0 required
#       (predicted ~11,104); k=0 log2N=20 fallback pre-registered if
#       realized overflow = 0 (fallback NOT exercised here unless recorded).
#       NARROW-3: determinism of the new binary, NEVER replication.
#
# Per receipt: hits (W_ge1_nontrivial), whist/W_ge1_by_word breakdown, excess
# ratio vs the frozen comparator excess_E = 2^30, excess over the run-internal
# accidental-hit rate, Garwood 95% CI (campaign Wilson-Hilferty chi-squared
# quantile convention; count and exposure only), band vs the preregistered
# floors (NULLBAND <=5, RESIDUAL 6-40, AMBIGUITY 41-99, THRESHOLD >=100),
# full AMEND-1 identity table (saturation-aware overflow identity;
# sum(zhist)==nontrivial per the DEV-S0-1 correction; all conjuncts; NO
# detail-log-derived quantities), AMEND-1(c) detail-log attestation.
#
# Exit codes: 0 pass; 9 = CC3-F6 (dead-anchor tripwire); 12 = CC3-GATE-FAIL
# (AMEND-1 counter inconsistency or seat mismatch); 11 = report-only support
# issue (double overflow = 0 -> fallback required, recorded).
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
EXCESS_E = 1 << 30
Z_LO, Z_HI = -1.959963984540054, 1.959963984540054
R3_PATH = "coordination/goals/GOAL-AES-003/batches/BATCH-2f12ac/tasks/TASK-20260901-7e0b71/runs/R3_table_freeze.json"


def chi2_q(p, nu):
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


def common(r, ids):
    hits = r["W_ge1_nontrivial"]
    nt = r["nontrivial_trials"]
    lo, hi = garwood_ci(hits, nt)
    b, br = band(hits)
    return {
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
        "garwood95_rate_per_2_30": {"lo": lo * EXCESS_E, "hi": hi * EXCESS_E,
                                    "note": "per-trial rate CI scaled by 2^30 (lineage convention; on exposure nt this equals the count CI scaled to per-2^30 exposure)"},
        "amend1_identity_table": ids,
        "amend1_identities_pass": amend1_pass(ids),
        "amend1_c_detail_log_attestation": detail_log_attestation(r),
    }


SEATS = {
    "gate0x": {"run_id": "S2a-2", "oracle": "live_aes_r5_affarm046ex_derivative_of_affarm046",
               "rounds": 5, "log2N": 30, "seed": 531001, "arm_id": 1, "threads": 2,
               "sbox": "aes", "sbox_k": 16,
               "positions": list(range(16)),
               "role": "GATE-0X EXTENDED REBUILD: aes-seat field-exact reproduction of the lineage Gate-0x reading (14 hits) on the extended build"},
    "dead": {"run_id": "S2a-5", "oracle": "live_aes_r6_affarm046ex_derivative_of_affarm046",
             "rounds": 6, "log2N": 30, "seed": 531004, "arm_id": 1, "threads": 4,
             "sbox": "aes", "sbox_k": 16,
             "positions": list(range(16)),
             "role": "DEAD ANCHOR on the extended build (r6 known-dead reference): ANALYZED FIRST among extended-build alive readings; gate hits <= 8; tripwire >= 9 -> CC3-F6"},
    "double": {"run_id": "S2a-6", "oracle": "live_aes_r5_affarm046ex_derivative_of_affarm046",
               "rounds": 5, "log2N": 20, "seed": 531001, "arm_id": 2, "threads": 4,
               "sbox": "aes", "sbox_k": 1,
               "positions": [0],
               "role": "DETERMINISM DOUBLE on the extended build (S_1, log2N=20): overflow-positive receipt; NARROW-3 - determinism of the new binary, NEVER replication"},
}


def seat_checks(r, seat):
    n = 1 << seat["log2N"]
    return {
        "oracle": r["oracle"] == seat["oracle"],
        "amask_1": r["amask"] == 1,
        "smask_1": r["smask"] == 1,
        "log2N": r["log2N"] == seat["log2N"],
        "trials_eq_2pow_log2N": r["trials"] == n,
        "seed": r["seed"] == seat["seed"],
        "arm_id": r["arm_id"] == seat["arm_id"],
        "threads": r["threads"] == seat["threads"],
        "sbox_label": r["sbox"] == seat["sbox"],
        "sbox_k": r["sbox_k"] == seat["sbox_k"],
        "sbox_positions_as_preregistered_seat": r["sbox_positions"] == seat["positions"],
        "schedule_pin_T0": r["schedule_pin"] == "PIN-T0",
        "schedule_pin_position_0": r["schedule_pin_position"] == 0,
        "schedule_pin_decision": r["schedule_pin_decision"] == "DEC-20260901-fb6f11",
        "hit_log_cap_256": r["hit_log_cap"] == 256,
    }


def analyze(mode, path, out_path):
    seat = SEATS[mode]
    r = json.load(open(path))
    ids = amend1_identities(r)
    cmn = common(r, ids)
    checks = seat_checks(r, seat)
    seat_ok = all(checks.values())
    a1_ok = cmn["amend1_identities_pass"]

    extra = {}
    if mode == "gate0x":
        r3 = json.load(open(R3_PATH))
        r3_k16 = {p["k"]: p for p in r3["points"]}[16]
        digest_ok = r["arm_table_concat_sha256"] == r3_k16["concat_sha256"]
        extra = {
            "gate": "hits <= any departure is a gate issue; continuity reading 14 expected (committed L1-AES-R5-P30)",
            "continuity_14_hits": r["W_ge1_nontrivial"] == 14,
            "table_digest_match_R3_k16": digest_ok,
            "r3_k16_concat_sha256": r3_k16["concat_sha256"],
            "receipt_arm_table_concat_sha256": r["arm_table_concat_sha256"],
        }
        verdict = "PASS" if (a1_ok and seat_ok and digest_ok and extra["continuity_14_hits"]) else "CC3-GATE-FAIL"
        code = 0 if verdict == "PASS" else 12
    elif mode == "dead":
        hits = r["W_ge1_nontrivial"]
        tripwire = hits >= 9
        gate_ok = hits <= 8
        extra = {
            "gate_rule": "hits <= 8 (carried dead band at 2^30); tripwire hits >= 9 -> CC3-F6 (boundary falsifier of the sealed verdict; HALT, escalate to claim-changing review, rule 12)",
            "gate_pass": gate_ok,
            "tripwire_fired": tripwire,
            "anchor_verdict": ("CC3-F6" if tripwire else
                               ("PASS (dead anchor, hits <= 8)" if gate_ok else "CC3-GATE-FAIL")),
            "rule8_note": ("a 0-hit anchor passes with reduced assurance (direction-safe; inherited precedent)"
                           if hits == 0 else "nonzero hit count within the dead band"),
            "analysis_order_attestation": "this receipt is ANALYZED FIRST among extended-build alive readings (preregistration section 7; S2a ordering)",
        }
        verdict = extra["anchor_verdict"]
        code = 9 if tripwire else (0 if (gate_ok and a1_ok and seat_ok) else 12)
    else:  # double
        hits = r["W_ge1_nontrivial"]
        overflow = r["hit_log_overflow"]
        extra = {
            "overflow_positive_required": True,
            "overflow_observed": overflow,
            "overflow_positive": overflow > 0,
            "predicted_hits_design_time": 12128,
            "predicted_overflow_design_time": 11104,
            "k0_log2N20_fallback_preregistered_if_overflow_zero": True,
            "k0_fallback_exercised": False if overflow > 0 else "REQUIRED (recorded; not exercised by this analysis)",
            "narrow3_note": "NARROW-3: this receipt is one half of a determinism double on the NEW extended binary; identical seed/seat/build reproduction is instrument determinism, NEVER an independent replication",
        }
        verdict = "PASS" if (a1_ok and seat_ok and overflow > 0) else ("CC3-GATE-FAIL" if (not a1_ok or not seat_ok) else "OVERFLOW-ZERO-FALLBACK")
        code = 0 if verdict == "PASS" else (12 if verdict == "CC3-GATE-FAIL" else 11)

    out = {
        "schema": "crypto.autoresearch.s2a_receipt_analysis.v1",
        "task_id": "TASK-20260903-7893b2",
        "batch_id": "BATCH-060cb4",
        "goal_id": "GOAL-AES-003",
        "idea_record": "IDEA-20260903-8f26ac",
        "decision_opening_batch": "DEC-20260903-63cd8d",
        "gate_regime": "AMEND-1 (DEC-20260901-6f9de3)",
        "preregistration": "coordination/goals/GOAL-AES-003/batches/BATCH-060cb4/tasks/TASK-20260903-695ebe/PREREGISTRATION.md (write-once, BINDING)",
        "pin_reference": "PIN-T0 (DEC-20260901-fb6f11)",
        "run_id": seat["run_id"],
        "build": "EXTENDED (frozen build + declared k=3 surface extension; source 45808af6..., binary 3ccc377c...)",
        "receipt": path,
        "arm": r["arm"],
        "role": seat["role"],
        "seat": {"sbox_token": ("aes" if mode != "double" else "s1"),
                 "rounds": seat["rounds"], "amask": 1, "smask": 1,
                 "log2N": seat["log2N"], "seed": seat["seed"],
                 "arm_id": seat["arm_id"], "threads": seat["threads"]},
        "seat_checks": checks,
        "seat_as_preregistered": seat_ok,
        **cmn,
        **extra,
        "outcome": verdict,
        "analyzed_utc": now_iso(),
        "inference": INFERENCE,
    }
    json.dump(out, open(out_path, "w"), indent=1)
    print(json.dumps({"run_id": seat["run_id"], "outcome": verdict,
                      "hits": cmn["hits_W_ge1_nontrivial"],
                      "amend1_pass": a1_ok, "seat_ok": seat_ok,
                      **{k: v for k, v in extra.items() if k in ("tripwire_fired", "overflow_observed", "continuity_14_hits", "table_digest_match_R3_k16")}}, indent=1))
    return code


if __name__ == "__main__":
    sys.exit(analyze(sys.argv[1], sys.argv[2], sys.argv[3]))
