#!/usr/bin/env python3
# s2_analysis.py -- TASK-20260902-c33c1f (BATCH-e5d753, GOAL-AES-003)
#
# S2 second-seed analysis under the AMEND-1 counter-inconsistency gate
# (fresh for this task). Mode:
#
#   python3 src/s2_analysis.py seed2 <k> <receipt.json> <analysis_out.json>
#       k=1: (S_1, r5, amask=1, smask=1, 2^30, seed 531002, armid 9,
#            threads 4) -- the frozen 363851 pre-specified replication seat.
#       k=4: (S_4, r5, amask=1, smask=1, 2^30, seed 531002, armid 4,
#            threads 4) -- seat-fixed armid convention per
#            IDEA-20260902-9e84ac stage_s2 / PREREGISTRATION.md section 6.
#
# AMEND-1 identity suite per analysis-bearing receipt (PREREGISTRATION.md
# section 2), SAME encoding as the S1 task's s1_analysis.py including the
# DEV-S0-1 corrected zhist convention (sum(zhist)==nontrivial_trials is the
# TRUE internal identity, affarm046ex.c:458-459; the literal '==trials'
# shorthand holds iff trivial_swaps_excluded==0). Seat expectations follow
# the corrected listing convention (DEV-S1-1): the receipt emits
# sbox_positions in ASCENDING order over the selected member set, so the
# expected listing == sorted(frozen-order prefix); seat MEMBERSHIP is the
# first k positions of the frozen row-major order.
#
# ADMISSIBLE quantities only (PREREGISTRATION section 3): everything here is
# counter-derived; NO analysis-bearing quantity is derived from the capped
# detail log (hit_trials / hit_e_detail are report-only enabling data; no
# branch conjunct consumes them; AMEND-1(c) satisfied by construction).
#
# Exit codes: 0 pass; 12 = SH2-GATE-FAIL (AMEND-1 counter inconsistency or
# seat mismatch on this receipt); 11 = other consistency issue; 2 = usage.
#
# INFERENCE BLOCK: policy executor-implementation; requested_policy
# executor-implementation; resolved_model_id
# fireworks-ai/accounts/fireworks/models/qwen3p8-max (session-reported; no
# adapter probe run); fallback_used true; model_verified false;
# degraded_requirements []; amendment DEC-20260831-0d1eeb.
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
    "independent_session": True,
}
EXCESS_E = 1 << 30          # frozen comparator convention (EV-AES-ec53f1)
NULL_DESIGN_RATE = 1.0      # analytic null lambda_0 = 1.0 hit per 2^30
Z_LO, Z_HI = -1.959963984540054, 1.959963984540054
FROZEN_ORDER = [0, 4, 8, 12, 1, 5, 9, 13, 2, 6, 10, 14, 3, 7, 11, 15]
ORACLE_R5 = "live_aes_r5_affarm046ex_derivative_of_affarm046"

SEATS = {
    1: {"arm_id": 9, "sbox": "aes", "sbox_k": 1,
        "positions": sorted(FROZEN_ORDER[:1]), "log2N": 30, "seed": 531002},
    4: {"arm_id": 4, "sbox": "aes", "sbox_k": 4,
        "positions": sorted(FROZEN_ORDER[:4]), "log2N": 30, "seed": 531002},
}
RUN_IDS = {1: "S2-1", 4: "S2-2"}


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
    """AMEND-1 counter-identity suite (PREREGISTRATION section 2), identical
    encoding to the S0/S1 task analysis scripts including the DEV-S0-1
    corrected zhist convention. 'hits' is W_ge1_nontrivial;
    logged_detail_records is the number of hit_trials entries."""
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
        "sum_zhist_eq_trials_literal": zhist_sum == n,
        "sum_zhist_note": ("sum(zhist)=%d == nontrivial_trials=%d (true internal "
                           "identity); literal '==trials' shorthand holds iff "
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
        "trials_accounting": r["trivial_swaps_excluded"] + nt == n,
    }


def amend1_pass(ids):
    keys = ("sum_whist_eq_nontrivial", "h_eq_sum_whist_ge1",
            "moment_identity_word_split", "sum_zhist_eq_nontrivial",
            "sum_ewhist_all_eq_nontrivial", "sum_ewhist_hit_eq_h",
            "sum_ewhist_miss_eq_nontrivial_minus_h",
            "logged_detail_records_identity", "overflow_identity",
            "trials_accounting")
    return all(ids[k] for k in keys)


def seat_check(r, k):
    s = SEATS[k]
    return {
        "oracle_r5": r["oracle"] == ORACLE_R5,
        "amask_1": r["amask"] == 1,
        "smask_1": r["smask"] == 1,
        "log2N": r["log2N"] == s["log2N"],
        "trials_eq_2pow_log2N": r["trials"] == (1 << s["log2N"]),
        "seed": r["seed"] == s["seed"],
        "arm_id": r["arm_id"] == s["arm_id"],
        "threads_4": r["threads"] == 4,
        "sbox_label": r["sbox"] == s["sbox"],
        "sbox_k": r["sbox_k"] == s["sbox_k"],
        "sbox_positions_as_preregistered_seat": r["sbox_positions"] == s["positions"],
        "sbox_positions_expected": s["positions"],
        "schedule_pin_T0": r["schedule_pin"] == "PIN-T0",
        "schedule_pin_position_0": r["schedule_pin_position"] == 0,
        "schedule_pin_decision": r["schedule_pin_decision"] == "DEC-20260901-fb6f11",
        "hit_log_cap_256": r["hit_log_cap"] == 256,
    }


def point_quantities(r):
    hits = r["W_ge1_nontrivial"]
    nt = r["nontrivial_trials"]
    lo, hi = garwood_ci(hits, nt)
    b, br = band(hits)
    null_run_internal = r.get("null_expectation_analytic")
    return {
        "hits_W_ge1_nontrivial": hits,
        "trivial_swaps_excluded": r["trivial_swaps_excluded"],
        "nontrivial_trials": nt,
        "whist": r["whist"],
        "W_ge1_by_word": r["W_ge1_by_word"],
        "band": b,
        "bandrank": br,
        "excess_E": EXCESS_E,
        "excess_ratio_vs_excess_E": hits / EXCESS_E,
        "null_design_rate_value": NULL_DESIGN_RATE,
        "null_expectation_analytic_run_internal": null_run_internal,
        "excess_over_run_internal_null": (hits - null_run_internal) if null_run_internal is not None else None,
        "garwood95_rate_per_trial": {"lo": lo, "hi": hi,
                                     "method": "Wilson-Hilferty chi-squared quantile (design-time convention)"},
        "garwood95_count_scaled_per_2_30": {"lo": lo * EXCESS_E, "hi": hi * EXCESS_E,
                                            "note": "rate CI scaled by excess_E = 2^30 for readability; nt = 2^30 here"},
        "sensitivity_floors_per_point": {
            "lambda_80_hits_per_2_30": 8.0,
            "lambda_95_hits_per_2_30": 10.5,
            "statement": ("a point reading NULLBAND excludes a per-point hit-rate excess >= ~8-10.5 "
                          "at 80-95% power, and excludes NOTHING below that; within-residual-band "
                          "trends are NOT resolvable at 2^30 (preregistration section 9)")},
    }


def seed2(k, path, out_path):
    k = int(k)
    if k not in (1, 4):
        print("seed2 mode: k must be 1 or 4", file=sys.stderr)
        sys.exit(2)
    with open(path) as f:
        r = json.load(f)
    ids = amend1_identities(r)
    seat = seat_check(r, k)
    q = point_quantities(r)
    a1_ok = amend1_pass(ids)
    seat_ok = all(seat.values())
    verdict = "SH2-GATE-FAIL" if (not a1_ok or not seat_ok) else "PASS"
    role = {
        1: ("SECOND SEED k=1 (R6) - the frozen 363851 pre-specified replication seat "
            "(not data-dependent); seed-variance measurement at the largest reading; "
            "band agreement with the primary seed is the pre-registered verdict-stability "
            "condition (PREREGISTRATION section 11)"),
        4: ("SECOND SEED k=4 - pre-registered by IDEA-20260902-9e84ac at the seat-fixed "
            "armid convention (seat armid fixed, seed family varies; no frozen "
            "pre-specification exists for that seat; no Coordinator relabel was issued); "
            "verdict-stability condition at the load-bearing transition locator"),
    }[k]
    out = {
        "schema": "crypto.autoresearch.s2_seed2_analysis.v1",
        "task_id": "TASK-20260902-c33c1f",
        "batch_id": "BATCH-e5d753",
        "goal_id": "GOAL-AES-003",
        "idea_record": "IDEA-20260902-9e84ac",
        "decision_opening_batch": "DEC-20260902-38227b",
        "gate_regime": "AMEND-1 (DEC-20260901-6f9de3)",
        "preregistration": "coordination/goals/GOAL-AES-003/batches/BATCH-e5d753/tasks/TASK-20260902-987716/PREREGISTRATION.md (write-once, BINDING)",
        "pin_reference": "PIN-T0 (DEC-20260901-fb6f11)",
        "run_id": RUN_IDS[k],
        "receipt": path,
        "arm": r["arm"],
        "k": k,
        "role": role,
        "seat": {"sbox": "S_%d diluted table set" % k, "rounds": 5, "amask": 1, "smask": 1,
                 "log2N": 30, "seed": 531002, "arm_id": SEATS[k]["arm_id"], "threads": 4},
        "seat_checks": seat,
        "seat_as_preregistered": seat_ok,
        "scope_note": ("k=1 statements are JOINT-EFFECT-scoped (SCOPE-1, DEC-20260902-38227b): the k=0->k=1 step "
                       "co-varies the first dilution step with the identity->AES schedule switch; all "
                       "interior-to-interior comparisons are schedule-clean under PIN-T0") if k == 1 else
                      "interior-to-interior comparison, schedule-clean under PIN-T0 (SCOPE-1)",
        "scope_discipline": {
            "claim_tier": "toy",
            "no_deployed_aes_claims": True,
            "no_published_cryptanalysis_comparisons": True,
            "x_statistic_not_computed": True,
            "no_rho_exclusion": True,
            "no_reopen_clause_attestation": ("the X statistic is not tested, decided, or reported as a reading; "
                                             "e fields ride as enabling artifacts only; no branch conjunct consumes them"),
        },
    }
    out.update(q)
    out.update({
        "hit_log_overflow": r["hit_log_overflow"],
        "hit_log_cap": r["hit_log_cap"],
        "amend1_identity_table": ids,
        "amend1_identities_pass": a1_ok,
        "point_verdict": verdict,
        "seed_agreement_note": ("per-seed reading, NEVER pooled; band agreement with the seed-531001 counterpart "
                                "is evaluated in the SH2 cascade branch 5 (SH2-SEED-DISAGREE) at verdict "
                                "composition, per PREREGISTRATION section 11; the verdict is composed only "
                                "after BOTH second seeds are read"),
        "analyzed_utc": now_iso(),
        "inference": INFERENCE,
    })
    with open(out_path, "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({"%s_seed2_k%d" % (RUN_IDS[k], k): verdict, "hits": q["hits_W_ge1_nontrivial"],
                      "band": q["band"], "saturation": ids["saturation_status"],
                      "amend1_pass": a1_ok, "seat_ok": seat_ok}, indent=1))
    if verdict == "SH2-GATE-FAIL":
        sys.exit(12)
    sys.exit(0)


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "seed2":
        seed2(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        print("mode must be 'seed2'", file=sys.stderr)
        sys.exit(2)
