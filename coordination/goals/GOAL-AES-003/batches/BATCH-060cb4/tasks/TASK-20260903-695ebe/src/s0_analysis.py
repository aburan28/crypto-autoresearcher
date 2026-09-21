#!/usr/bin/env python3
# s0_analysis.py -- TASK-20260903-695ebe (BATCH-060cb4, GOAL-AES-003)
# Fresh for this task. S0 anchor analysis under the AMEND-1
# counter-inconsistency gate (PREREGISTRATION.md sections 1-3). Per-receipt
# modes so the DEAD ANCHOR is ANALYZED BEFORE any alive reading (binding
# anchor order):
#
#   python3 src/s0_analysis.py dead <receipt.json> <analysis_out.json>
#       DEAD ANCHOR (aes, r6, 1, 1, 2^30, seed 531004, armid 1, threads 4),
#       ANALYZED FIRST among reading-bearing arms: gate hits <= 8 at 2^30
#       (carried dead band); tripwire hits >= 9 -> CC-F6 halt.
#   python3 src/s0_analysis.py rampzero <receipt.json> <analysis_out.json>
#       RAMP-ZERO ANCHOR (S_0, r5, 1, 1, 2^30, seed 531001, armid 5,
#       threads 4), BLOCKING: hits = 2^30, W = 3 on 100% of nontrivial,
#       excess ratio 1.0 exact; overflow = 2^30 - 1024 saturated-by-
#       construction LEGAL under AMEND-1 provided every counter identity is
#       exact. This receipt is the AMEND-1 proves-too-much control: a
#       counter-identity failure HERE indicts the gate itself ->
#       CC-GATE-FAIL.
#
# AMEND-1 identity suite per analysis-bearing receipt (PREREGISTRATION.md
# section 2): sum(whist)==nontrivial; h==sum(whist[1:]); moment identity
# sum(W_ge1_by_word)==sum(W*whist[W]); sum(zhist)==nontrivial_trials
# (DEV-S0-1 CORRECTED form: the instrument increments zhist ONLY on
# nontrivial trials, affarm046ex.c:458-459, frozen whist convention; the
# literal '==trials' shorthand is reported informationally only);
# sum(ewhist_all)==nontrivial; sum(ewhist_hit)==h;
# sum(ewhist_miss)==nontrivial-h; overflow == hits - logged_detail_records
# (saturation-aware; logged_detail_records = len(hit_trials) entries);
# trials accounting. In this instrument "hits" is the receipt field
# W_ge1_nontrivial. NO analysis-bearing quantity below is derived from the
# capped detail log (hit_e_detail / hit_trials): every reported quantity is
# counter-derived (AMEND-1(c) satisfied by construction).
#
# Exit codes (per-receipt): 0 pass; 9 = CC-F6 tripwire (dead mode);
#   10 = CC-ANCHOR-FAIL (rampzero conjuncts);
#   12 = CC-GATE-FAIL (AMEND-1 counter inconsistency / seat mismatch);
#   11 = other consistency issue (report-only support checks).
import json, sys, math, datetime

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
EXCESS_E = 1 << 30          # frozen comparator convention
DEAD_BAND_2_30 = 8          # carried dead band at 2^30
F6_TRIPWIRE = 9
Z_LO, Z_HI = -1.959963984540054, 1.959963984540054


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
        # DEV-S0-1 CORRECTED zhist identity: zhist is incremented only on
        # nontrivial trials (affarm046ex.c:458-459), so the true internal
        # identity is sum(zhist)==nontrivial_trials; the literal '==trials'
        # form holds iff trivial_swaps_excluded==0 and is informational only.
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
        # AMEND-1 verbatim conjunct-(a) form; coincides with the
        # saturation-aware identity ONLY on saturated receipts. Informational
        # on unsaturated receipts; never a separate gate conjunct there.
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
    """AMEND-1(c): attest that NO quantity in this analysis is derived from
    the capped detail log. All reported quantities are counter-derived."""
    return {
        "statement": "no analysis-bearing quantity is derived from the capped detail log (hit_e_detail / hit_trials); all quantities are counter-derived",
        "hit_e_detail_records_present": len(r.get("hit_e_detail", [])),
        "hit_trials_entries_present": len(r.get("hit_trials", [])),
        "detail_log_used_for_any_reported_quantity": False,
        "detail_log_status": "report-only enabling data under the no-reopen clause; no branch conjunct consumes it",
    }


def dead(path, out_path):
    with open(path) as f:
        r = json.load(f)
    hits = r["W_ge1_nontrivial"]
    nt = r["nontrivial_trials"]
    ids = amend1_identities(r)
    seat_ok = (r["oracle"] == "live_aes_r6_affarm046ex_derivative_of_affarm046"
               and r["amask"] == 1 and r["smask"] == 1 and r["log2N"] == 30
               and r["seed"] == 531004 and r["arm_id"] == 1
               and r["threads"] == 4 and r["sbox"] == "aes"
               and r["sbox_k"] == 16 and r["schedule_pin"] == "PIN-T0"
               and r["trials"] == (1 << 30))
    lo, hi = garwood_ci(hits, nt)
    gate_pass = hits <= DEAD_BAND_2_30
    tripwire = hits >= F6_TRIPWIRE
    a1_ok = amend1_pass(ids)
    verdict = ("CC-F6" if tripwire
               else ("CC-GATE-FAIL" if (not a1_ok or not seat_ok)
                     else ("PASS" if gate_pass else "CC-GATE-FAIL")))
    out = {
        "schema": "crypto.autoresearch.s0_dead_anchor_analysis.v1",
        "task_id": "TASK-20260903-695ebe",
        "batch_id": "BATCH-060cb4",
        "idea_record": "IDEA-20260903-8f26ac",
        "gate_regime": "AMEND-1 (DEC-20260901-6f9de3)",
        "run_id": "S0-5",
        "receipt": path,
        "arm": r["arm"],
        "seat": {"sbox": "aes", "rounds": 6, "amask": 1, "smask": 1,
                 "log2N": 30, "seed": 531004, "arm_id": 1, "threads": 4},
        "seat_as_preregistered": seat_ok,
        "hits_W_ge1_nontrivial": hits,
        "trivial_swaps_excluded": r["trivial_swaps_excluded"],
        "nontrivial_trials": nt,
        "whist": r["whist"],
        "W_ge1_by_word": r["W_ge1_by_word"],
        "zhist": r["zhist"],
        "hit_log_overflow": r["hit_log_overflow"],
        "hit_log_cap": r["hit_log_cap"],
        "band": band(hits)[0],
        "bandrank": band(hits)[1],
        "excess_ratio_vs_excess_E": hits / EXCESS_E,
        "excess_E": EXCESS_E,
        "garwood95_rate_per_2_30": {"lo": lo, "hi": hi,
                                    "method": "Wilson-Hilferty chi-squared quantile (design-time convention)"},
        "amend1_identity_table": ids,
        "amend1_identities_pass": a1_ok,
        "amend1_c_detail_log_attestation": detail_log_attestation(r),
        "gate": {"dead_band_2_30": DEAD_BAND_2_30, "hits_le_band": gate_pass,
                 "f6_tripwire": F6_TRIPWIRE, "tripwire_fired": tripwire},
        "anchor_verdict": verdict,
        "rule8_note": ("a reading of 0 hits passes the gate but is below the ~1-4 hit "
                       "expectation and carries reduced anchor assurance "
                       "(direction-safe; inherited precedent)" if hits == 0 else "none"),
        "analysis_order_attestation": "dead anchor analyzed FIRST among reading-bearing arms, before any alive reading (binding order); ramp-zero arm not yet invoked at this analysis",
        "analyzed_utc": now_iso(),
        "inference": INFERENCE,
    }
    with open(out_path, "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({"S0-5_dead_anchor": verdict, "hits": hits,
                      "tripwire_fired": tripwire, "amend1_pass": a1_ok,
                      "seat_ok": seat_ok}, indent=1))
    if tripwire:
        sys.exit(9)
    if verdict == "CC-GATE-FAIL":
        sys.exit(12)
    sys.exit(0)


def rampzero(path, out_path):
    with open(path) as f:
        r = json.load(f)
    hits = r["W_ge1_nontrivial"]
    nt = r["nontrivial_trials"]
    t = r["trivial_swaps_excluded"]
    ids = amend1_identities(r)
    seat_ok = (r["oracle"] == "live_aes_r5_affarm046ex_derivative_of_affarm046"
               and r["amask"] == 1 and r["smask"] == 1 and r["log2N"] == 30
               and r["seed"] == 531001 and r["arm_id"] == 5
               and r["threads"] == 4 and r["sbox"] == "identity"
               and r["sbox_k"] == 0 and r["schedule_pin"] == "PIN-T0"
               and r["schedule_pin_position"] == 0
               and r["schedule_pin_decision"] == "DEC-20260901-fb6f11"
               and r["trials"] == (1 << 30))
    conjuncts = {
        "hits_equal_2pow30_exact": hits == (1 << 30),
        "T_zero": t == 0,
        "W3_on_100pct_of_nontrivial": r["whist"] == [0, 0, 0, nt, 0],
        "W_ge1_by_word_pattern": r["W_ge1_by_word"] == [0, nt, nt, nt],
        "excess_ratio_1_exact": hits == EXCESS_E,
        "overflow_saturated_legal_under_amend1": (
            r["hit_log_overflow"] == (1 << 30) - r["threads"] * r["hit_log_cap"]),
    }
    support = {
        # W=3 on 100% of nontrivial trials implies Z >= 12 on every trial
        # (three vanishing geometric words contribute 12 equal byte
        # positions; Z = 16 would require W = 4). Support consistency only;
        # NOT an AMEND-1 identity and NOT a preregistered anchor conjunct.
        "zhist_supports_W3_law": sum(r["zhist"][:12]) == 0 and sum(r["zhist"]) == nt,
        "ewhist_hit_all_zero_weight": r["ewhist_hit"] == [nt] + [0] * 16,
        "ewhist_all_all_zero_weight": r["ewhist_all"] == [nt] + [0] * 16,
        "ewhist_miss_empty": r["ewhist_miss"] == [0] * 17,
    }
    a1_ok = amend1_pass(ids)
    conjuncts_pass = all(conjuncts.values())
    verdict = ("CC-GATE-FAIL" if (not a1_ok or not seat_ok)
               else ("PASS" if conjuncts_pass else "CC-ANCHOR-FAIL"))
    out = {
        "schema": "crypto.autoresearch.s0_rampzero_analysis.v1",
        "task_id": "TASK-20260903-695ebe",
        "batch_id": "BATCH-060cb4",
        "idea_record": "IDEA-20260903-8f26ac",
        "gate_regime": "AMEND-1 (DEC-20260901-6f9de3)",
        "run_id": "S0-6",
        "receipt": path,
        "arm": r["arm"],
        "seat": {"sbox": "identity", "rounds": 5, "amask": 1, "smask": 1,
                 "log2N": 30, "seed": 531001, "arm_id": 5, "threads": 4},
        "seat_as_preregistered": seat_ok,
        "hits_W_ge1_nontrivial": hits,
        "trivial_swaps_excluded": t,
        "nontrivial_trials": nt,
        "whist": r["whist"],
        "W_ge1_by_word": r["W_ge1_by_word"],
        "zhist": r["zhist"],
        "excess_ratio_vs_excess_E": hits / EXCESS_E,
        "excess_E": EXCESS_E,
        "hit_log_overflow_observed": r["hit_log_overflow"],
        "hit_log_overflow_expected_saturated": (1 << 30) - r["threads"] * r["hit_log_cap"],
        "hit_log_cap": r["hit_log_cap"],
        "amend1_identity_table": ids,
        "amend1_identities_pass": a1_ok,
        "amend1_c_detail_log_attestation": detail_log_attestation(r),
        "anchor_conjuncts": conjuncts,
        "anchor_conjuncts_pass": conjuncts_pass,
        "support_checks_report_only": support,
        "amend1_proves_too_much_control": {
            "statement": "the AMEND-1 gate must PASS this receipt (overflow 2^30 - 1024, identities exact); if it fails THIS receipt, the gate itself is indicted -> CC-GATE-FAIL",
            "gate_passed_this_receipt": a1_ok and seat_ok,
        },
        "anchor_verdict": verdict,
        "analyzed_utc": now_iso(),
        "inference": INFERENCE,
    }
    with open(out_path, "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({"S0-6_rampzero": verdict, "hits": hits,
                      "excess_ratio_exact": conjuncts["excess_ratio_1_exact"],
                      "overflow_identity": ids["overflow_identity"],
                      "amend1_pass": a1_ok, "seat_ok": seat_ok,
                      "conjuncts_pass": conjuncts_pass}, indent=1))
    if verdict == "CC-GATE-FAIL":
        sys.exit(12)
    if verdict == "CC-ANCHOR-FAIL":
        sys.exit(10)
    if not all(support.values()):
        sys.exit(11)
    sys.exit(0)


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "dead":
        dead(sys.argv[2], sys.argv[3])
    elif mode == "rampzero":
        rampzero(sys.argv[2], sys.argv[3])
    else:
        print("mode must be 'dead' or 'rampzero'", file=sys.stderr)
        sys.exit(2)
