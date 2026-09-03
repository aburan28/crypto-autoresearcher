#!/usr/bin/env python3
# s1_analysis.py -- TASK-20260901-c2b265 (BATCH-7b798d, GOAL-AES-003)
#
# Per-point S1 analysis (fresh for this task). Consumes ONE interior/re-seat
# receipt and writes its preregistered per-point analysis:
#   hits = W_ge1_nontrivial; W breakdown = whist + W_ge1_by_word; excess
#   ratio vs the frozen excess_E = 2^30 comparator convention
#   (EV-AES-ec53f1); run-internal analytic null (receipt field
#   null_expectation_analytic = (N - trivial)*4/2^32, recomputed from the
#   arm's own class counters) reported beside the design-rate value 1.0;
#   exact Garwood 95% CI under the design-time Wilson-Hilferty chi-squared
#   quantile convention (IDEA-20260901-582ea9 design_time_power); frozen
#   bands of PREREGISTRATION.md section 1 (NULLBAND <=5, RESIDUAL 6-40,
#   AMBIGUITY 41-99, THRESHOLD >=100; bandrank 0/1/2/3).
#
# For k=16 (S1-1 KNOWN-ALIVE RE-SEAT, ANALYZED FIRST within S1) the gate is
# h(16) in [6,30] inclusive; outside -> SH-RESEAT-FAIL (F5 indictment of the
# widened table path; committed measurements stand; HALT, interior readings
# recorded but NO shape verdict composed).
#
# For EVERY analysis-bearing receipt: hit_log_overflow MUST be 0 (all S1
# arms are sparse-hit arms; PREREGISTRATION.md section 5 item 1 note: for
# every arm where hits are expected sparse, hit_overflow > 0 remains
# SH-GATE-FAIL). The k=0 anchor overflow note of section 5 does NOT extend
# to any S1 arm (carried forward, not extended).
#
# usage: python3 src/s1_analysis.py <receipt.json> <analysis_out.json> <run_id> <k>
# Exit: 0 analysis written (gate state inside the JSON); 12 = receipt failed
# a consistency/overflow check or the seat does not match the preregistered
# tuple (SH-GATE-FAIL input); 13 = re-seat band failure (SH-RESEAT-FAIL).
#
# NO-REOPEN CLAUSE: every e field the instrument logs (ewhist_*, ewbithist_*,
# ezdiag_*, ezoff_*, hit_e_detail with zero_mask_e) is retained as
# report-only enabling data; no X statistic is computed, tested, or reported
# as a reading here or anywhere in this task; no rho-exclusion is claimed.
#
# INFERENCE BLOCK: policy executor-implementation; requested_policy
# executor-implementation; resolved_model_id
# fireworks-ai/accounts/fireworks/models/qwen3p8-max (session-reported; no
# adapter probe run in this session); fallback_used true; model_verified
# false; degraded_requirements []; amendment DEC-20260831-0d1eeb.
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
EXCESS_E = 1 << 30          # frozen comparator convention (EV-AES-ec53f1)
Z_LO, Z_HI = -1.959963984540054, 1.959963984540054
SEATS = {  # PREREGISTRATION.md section 3 (armid reuse per 363851/582ea9)
    16: {"token": "aes", "arm_id": 8},
    1:  {"token": "s1",  "arm_id": 2},
    2:  {"token": "s2",  "arm_id": 3},
    8:  {"token": "s8",  "arm_id": 6},
}
POS_ORDER = [0, 4, 8, 12, 1, 5, 9, 13, 2, 6, 10, 14, 3, 7, 11, 15]
RESEAT_BAND = (6, 30)       # PR-S3: h(16) in [6,30]
SENSITIVITY_FLOORS = {      # PREREGISTRATION.md section 2 (design-time)
    "lambda_80_hits_per_2_30": 8.0,
    "lambda_95_hits_per_2_30": 10.5,
    "statement": ("a point reading NULLBAND excludes a per-point hit-rate excess "
                  ">= ~8-10.5 at 80-95% power, and excludes NOTHING below that; "
                  "within-residual-band trends are NOT resolvable at 2^30"),
}


def chi2_q(p, nu):
    # Wilson-Hilferty approximation to the chi-squared quantile (design-time
    # convention of the proposal's power computation; identical to the S0
    # task's s0_analysis.py).
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


def _per_thread_logged(r):
    counts = {}
    for e in r["hit_trials"]:
        counts[e[0]] = counts.get(e[0], 0) + 1
    return [counts.get(t, 0) for t in range(r["threads"])]


def main():
    receipt_path, out_path, run_id, k = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
    seat = SEATS[k]
    with open(receipt_path) as f:
        r = json.load(f)

    hits = r["W_ge1_nontrivial"]
    nt = r["nontrivial_trials"]
    t = r["trivial_swaps_excluded"]
    n = r["trials"]
    wh = r["whist"]
    by_word = r["W_ge1_by_word"]
    b, br = band(hits)
    lo, hi = garwood_ci(hits, nt)
    null_analytic = r["null_expectation_analytic"]

    checks = {
        "seat_as_preregistered": (
            r["oracle"] == "live_aes_r5_affarm046ex_derivative_of_affarm046"
            and r["amask"] == 1 and r["smask"] == 1 and r["log2N"] == 30
            and r["seed"] == 531001 and r["arm_id"] == seat["arm_id"]
            and r["threads"] == 4
            and r["sbox_k"] == k
            and r["sbox"] == ("identity" if k == 0 else "aes")
            and r["sbox_is_aes"] == (k == 16)
            and r["sbox_positions"] == sorted(POS_ORDER[:k])
            and r["schedule_pin"] == "PIN-T0"
            and r["schedule_pin_position"] == 0
            and r["schedule_pin_decision"] == "DEC-20260901-fb6f11"
            and r["hit_log_cap"] == 256),
        "trials_accounting": t + nt == n == EXCESS_E,
        "whist_sums_to_nontrivial": sum(wh) == nt,
        "wge1_consistent": hits == sum(wh[1:5]),
        "W_ge1_by_word_moment_consistent": sum(by_word) == sum(w * wh[w] for w in range(5)),
        "W_ge1_by_word_bounded": all(0 <= c <= hits for c in by_word),
        "ewhist_all_sums_to_nontrivial": sum(r["ewhist_all"]) == nt,
        "ewhist_hit_sums_to_hits": sum(r["ewhist_hit"]) == hits,
        "ewhist_miss_sums_to_nonhits": sum(r["ewhist_miss"]) == nt - hits,
        "null_expectation_analytic_matches_class_counters":
            abs(null_analytic - nt * 4.0 / 4294967296.0) < 1e-9,
        "hit_trials_logged_is_thread0_count":
            r["hit_trials_logged"] == sum(1 for e in r["hit_trials"] if e[0] == 0),
        "hit_detail_complete_under_overflow_zero":
            len(r["hit_trials"]) == len(r["hit_e_detail"]) == hits - r["hit_log_overflow"],
        "per_thread_logged_within_cap":
            all(c <= r["hit_log_cap"] for c in _per_thread_logged(r)),
        "hit_log_overflow_zero": r["hit_log_overflow"] == 0,
    }
    all_checks = all(checks.values())

    out = {
        "schema": "crypto.autoresearch.s1_point_analysis.v1",
        "task_id": "TASK-20260901-c2b265",
        "idea_record": "IDEA-20260901-582ea9",
        "pin_decision": "DEC-20260901-fb6f11",
        "run_id": run_id,
        "receipt": receipt_path,
        "arm": r["arm"],
        "k": k,
        "seat": {"sbox_token": seat["token"], "sbox_k": k, "rounds": 5,
                 "amask": 1, "smask": 1, "log2N": 30, "seed": 531001,
                 "arm_id": seat["arm_id"], "threads": 4},
        "hits_W_ge1_nontrivial": hits,
        "trivial_swaps_excluded": t,
        "nontrivial_trials": nt,
        "whist": wh,
        "W_ge1_by_word": by_word,
        "band": b,
        "bandrank": br,
        "excess_ratio_vs_excess_E": hits / EXCESS_E,
        "excess_E": EXCESS_E,
        "null_expectation_analytic_run_internal": null_analytic,
        "null_design_rate_value": 1.0,
        "excess_over_run_internal_null": hits - null_analytic,
        "garwood95_rate_per_trial": {
            "lo": lo, "hi": hi,
            "method": "Wilson-Hilferty chi-squared quantile (design-time convention)"},
        "garwood95_count_scaled_per_2_30": {
            "lo": lo * EXCESS_E, "hi": hi * EXCESS_E,
            "note": "rate CI scaled by excess_E = 2^30 for readability; nt = 2^30 here"},
        "hit_log_overflow": r["hit_log_overflow"],
        "hit_log_cap": r["hit_log_cap"],
        "hit_log_overflow_gate": {
            "required": 0,
            "observed": r["hit_log_overflow"],
            "pass": r["hit_log_overflow"] == 0,
            "note": ("all S1 arms are sparse-hit arms; hit_overflow > 0 here is "
                     "SH-GATE-FAIL per PREREGISTRATION.md section 5 item 1 note; "
                     "the k=0 anchor overflow note is carried forward but NOT "
                     "extended to any S1 arm")},
        "sensitivity_floors_per_point": SENSITIVITY_FLOORS,
        "consistency_checks": checks,
        "all_consistency_checks_pass": all_checks,
        "no_reopen_clause_attestation": (
            "e fields (ewhist_*, ewbithist_*, ezdiag_*, ezoff_*, hit_e_detail) "
            "retained report-only; no X statistic computed, tested, or reported; "
            "no rho-exclusion claimed; no carrier reading"),
        "analyzed_utc": now_iso(),
        "inference": INFERENCE,
    }

    if k == 16:
        in_band = RESEAT_BAND[0] <= hits <= RESEAT_BAND[1]
        out["reseat_gate"] = {
            "band": list(RESEAT_BAND),
            "hits": hits,
            "in_band": in_band,
            "verdict": ("PASS" if (in_band and all_checks) else
                        ("SH-RESEAT-FAIL" if not in_band else "GATE-FAIL")),
            "note": ("F5: indict THIS record's widened table path, not the "
                     "committed measurements; HALT; interior readings recorded "
                     "but NO shape verdict composed" if not in_band else
                     "known-alive re-seat in band; interior points admitted"),
            "analysis_order_attestation": ("k=16 re-seat ANALYZED FIRST within S1, "
                                           "before any interior reading enters the "
                                           "verdict (binding order)"),
            "second_stream_note": ("this arm also re-measures the t=1 seat's hit "
                                   "count on a second stream (seed-variance control "
                                   "reading, report-only; per seed, never pooled)"),
        }

    with open(out_path, "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({"run_id": run_id, "k": k, "hits": hits, "band": b,
                      "bandrank": br, "excess_ratio": hits / EXCESS_E,
                      "garwood95_lo": lo, "garwood95_hi": hi,
                      "all_checks_pass": all_checks,
                      "overflow": r["hit_log_overflow"]}, indent=1))
    if not all_checks:
        sys.exit(12)
    if k == 16 and not (RESEAT_BAND[0] <= hits <= RESEAT_BAND[1]):
        sys.exit(13)
    sys.exit(0)


if __name__ == "__main__":
    main()
