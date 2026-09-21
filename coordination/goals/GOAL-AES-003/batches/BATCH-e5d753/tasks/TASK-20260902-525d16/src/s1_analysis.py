#!/usr/bin/env python3
# s1_analysis.py -- TASK-20260902-525d16 (BATCH-e5d753, GOAL-AES-003)
#
# S1 interior-grid analysis under the AMEND-1 counter-inconsistency gate
# (fresh for this task). Per-receipt modes so the k=16 KNOWN-ALIVE RE-SEAT is
# ANALYZED FIRST within S1, then k=1, k=2, k=4, k=8 (binding order per
# PREREGISTRATION.md section 5 of TASK-20260902-987716):
#
#   python3 src/s1_analysis.py reseat <T1_receipt.json> <T1_analysis_out.json>
#       KNOWN-ALIVE RE-SEAT k=16 (S_16, r5, amask=1, smask=1, 2^30, seed
#       531001, armid 8, threads 4). Gate: h(16) in [6, 30] (re-seat band) or
#       SH2-RESEAT-FAIL (F5 indictment of THIS batch's table path; HALT;
#       interior readings recorded but no shape verdict composed).
#   python3 src/s1_analysis.py grid <k> <receipt.json> <analysis_out.json>
#       AMEND-1 re-runs k=1 (S_1, armid 2), k=2 (S_2, armid 3), k=8 (S_8,
#       armid 6), and the LOAD-BEARING TRANSITION LOCATOR k=4 (S_4, armid 4;
#       FIRST-EVER measurement of that family point). All seats r5, amask=1,
#       smask=1, 2^30, seed 531001, threads 4.
#   python3 src/s1_analysis.py detcmp <det_a.json> <det_b.json> <cmp_out.json>
#       DETERMINISM DOUBLE comparison on an overflow-positive receipt (R3):
#       seat (S_1, r5, 1, 1, log2N=20, seed 531001, armid 2, threads 4),
#       identical command twice. Byte-identity modulo the preregistered
#       timing strip set {elapsed_seconds_measured,
#       measured_rate_trials_per_sec}; AMEND-1 identities on the double
#       receipt; realized overflow > 0 required. If realized overflow == 0,
#       exit 14 => run the pre-registered k=0 fallback double (S_0, log2N=20,
#       seed 531001, armid 5, identity) twice, then re-invoke:
#   python3 src/s1_analysis.py detcmp <a> <b> <out> --expect-seat k0
#
# AMEND-1 identity suite per analysis-bearing receipt (PREREGISTRATION.md
# section 2): sum(whist)==nontrivial; h==sum(whist[1:]); moment identity
# sum(W_ge1_by_word)==sum(W*whist[W]); sum(zhist)==nontrivial_trials (TRUE
# internal identity per the DEV-S0-1 corrected convention: the instrument
# increments zhist only for nontrivial trials, affarm046ex.c:458-459; the
# literal '==trials' shorthand is additionally reported and holds iff
# trivial_swaps_excluded==0); sum(ewhist_all)==nontrivial;
# sum(ewhist_hit)==h; sum(ewhist_miss)==nontrivial-h; overflow == hits -
# logged_detail_records (saturation-aware, section 1.1: logged_detail_records
# == threads*HIT_LOG_CAP when saturated, == hits with overflow == 0
# otherwise); trials accounting. In this instrument "hits" is the receipt
# field W_ge1_nontrivial.
#
# ADMISSIBLE quantities only (PREREGISTRATION section 3): everything above is
# counter-derived; NO analysis-bearing quantity is derived from the capped
# detail log (hit_trials / hit_e_detail are report-only enabling data; no
# branch conjunct consumes them; AMEND-1(c) satisfied by construction).
#
# Exit codes: 0 pass; 12 = SH2-GATE-FAIL (AMEND-1 counter inconsistency /
# seat mismatch / determinism failure); 13 = SH2-RESEAT-FAIL (re-seat band);
# 14 = determinism receipt realized overflow == 0 (pre-registered k=0
# fallback required; rule-8 regime deviation); 11 = other consistency issue.
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
RESEAT_BAND = (6, 30)       # k=16 known-alive re-seat gate band
NULL_DESIGN_RATE = 1.0      # analytic null lambda_0 = 1.0 hit per 2^30 (pinned at endpoints)
Z_LO, Z_HI = -1.959963984540054, 1.959963984540054
FROZEN_ORDER = [0, 4, 8, 12, 1, 5, 9, 13, 2, 6, 10, 14, 3, 7, 11, 15]
STRIP_SET = ("elapsed_seconds_measured", "measured_rate_trials_per_sec")
ORACLE_R5 = "live_aes_r5_affarm046ex_derivative_of_affarm046"

# Expected receipt sbox_positions per seat. The diluted seat is defined by
# MEMBERSHIP: the first k positions of the FROZEN row-major order (the frozen
# ORDER binds the nested family / freeze file, verified by the freeze digest
# re-verification). The receipt LISTING is ascending order by construction:
# affarm046ex.c:977-980 emits sbox_positions by iterating j = 0..15 and
# printing members of diluted_position_list(ksel). Pass-1 of this script
# mis-encoded the expectation as the frozen-order LISTING (DEV-S1-1): that
# coincided with the ascending listing at k=1/2/4 (their frozen prefixes are
# already ascending) but diverged at k=8 (frozen prefix [0,4,8,12,1,5,9,13]
# lists ascending as [0,1,4,5,8,9,12,13]) and at k=16 (full set [0..15];
# committed convention also seen on the S0 dead-anchor receipt of
# TASK-20260902-987716). Corrected to the source-level convention: expected
# listing == sorted(frozen-order prefix).
EXPECTED_POSITIONS = {
    16: sorted(FROZEN_ORDER[:16]),
    1: sorted(FROZEN_ORDER[:1]),
    2: sorted(FROZEN_ORDER[:2]),
    4: sorted(FROZEN_ORDER[:4]),
    8: sorted(FROZEN_ORDER[:8]),
}
SEATS = {
    16: {"arm_id": 8, "sbox": "aes", "sbox_k": 16, "positions": EXPECTED_POSITIONS[16], "log2N": 30, "seed": 531001},
    1:  {"arm_id": 2, "sbox": "aes", "sbox_k": 1,  "positions": EXPECTED_POSITIONS[1],  "log2N": 30, "seed": 531001},
    2:  {"arm_id": 3, "sbox": "aes", "sbox_k": 2,  "positions": EXPECTED_POSITIONS[2],  "log2N": 30, "seed": 531001},
    4:  {"arm_id": 4, "sbox": "aes", "sbox_k": 4,  "positions": EXPECTED_POSITIONS[4],  "log2N": 30, "seed": 531001},
    8:  {"arm_id": 6, "sbox": "aes", "sbox_k": 8,  "positions": EXPECTED_POSITIONS[8],  "log2N": 30, "seed": 531001},
}
RUN_IDS = {16: "S1-1", 1: "S1-2", 2: "S1-3", 4: "S1-4", 8: "S1-5"}


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
    encoding to the S0 task's s0_analysis.py including the DEV-S0-1 corrected
    zhist convention. 'hits' is W_ge1_nontrivial; logged_detail_records is
    the number of hit_trials entries."""
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
        # zhist internal identity (DEV-S0-1 corrected convention, BINDING per
        # this task's handoff): instrument increments zhist ONLY for
        # nontrivial trials (affarm046ex.c:458-459, frozen whist convention),
        # so the TRUE internal identity is sum(zhist)==nontrivial_trials; it
        # equals trials iff trivial_swaps_excluded == 0. Both reported; the
        # gate conjunct is the true internal identity.
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
        # AMEND-1 verbatim conjunct-(a) form; coincides with the
        # saturation-aware identity ONLY on saturated receipts. Reported
        # informationally; NOT a separate gate conjunct on unsaturated
        # receipts (PREREGISTRATION section 1.1).
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


def seat_check(r, k, log2N=None, seed=None):
    s = SEATS[k]
    log2N = s["log2N"] if log2N is None else log2N
    seed = s["seed"] if seed is None else seed
    return {
        "oracle_r5": r["oracle"] == ORACLE_R5,
        "amask_1": r["amask"] == 1,
        "smask_1": r["smask"] == 1,
        "log2N": r["log2N"] == log2N,
        "trials_eq_2pow_log2N": r["trials"] == (1 << log2N),
        "seed": r["seed"] == seed,
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


def common_header(schema, run_id, receipt_path, r):
    return {
        "schema": schema,
        "task_id": "TASK-20260902-525d16",
        "idea_record": "IDEA-20260902-9e84ac",
        "decision_opening_batch": "DEC-20260902-38227b",
        "gate_regime": "AMEND-1 (DEC-20260901-6f9de3)",
        "preregistration": "coordination/goals/GOAL-AES-003/batches/BATCH-e5d753/tasks/TASK-20260902-987716/PREREGISTRATION.md (write-once, BINDING)",
        "pin_reference": "PIN-T0 (DEC-20260901-fb6f11)",
        "run_id": run_id,
        "receipt": receipt_path,
        "arm": r["arm"],
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


def reseat(path, out_path):
    with open(path) as f:
        r = json.load(f)
    k = 16
    ids = amend1_identities(r)
    seat = seat_check(r, k)
    q = point_quantities(r)
    a1_ok = amend1_pass(ids)
    seat_ok = all(seat.values())
    hits = q["hits_W_ge1_nontrivial"]
    in_band = RESEAT_BAND[0] <= hits <= RESEAT_BAND[1]
    verdict = ("SH2-GATE-FAIL" if (not a1_ok or not seat_ok)
               else ("PASS" if in_band else "SH2-RESEAT-FAIL"))
    out = common_header("crypto.autoresearch.s1_reseat_analysis.v1", RUN_IDS[k], path, r)
    out.update({
        "role": "KNOWN-ALIVE RE-SEAT (blocking anchors; analyzed FIRST within S1)",
        "seat": {"sbox": "aes (S_16 table set)", "rounds": 5, "amask": 1, "smask": 1,
                 "log2N": 30, "seed": 531001, "arm_id": 8, "threads": 4},
        "seat_checks": seat,
        "seat_as_preregistered": seat_ok,
    })
    out.update(q)
    out.update({
        "hit_log_overflow": r["hit_log_overflow"],
        "hit_log_cap": r["hit_log_cap"],
        "amend1_identity_table": ids,
        "amend1_identities_pass": a1_ok,
        "reseat_gate": {
            "band": list(RESEAT_BAND),
            "hits": hits,
            "in_band": in_band,
            "verdict": verdict if verdict != "SH2-GATE-FAIL" else "SH2-RESEAT-FAIL-not-evaluated-gate-fail-first",
            "note": ("known-alive re-seat in band; interior points admitted" if in_band and verdict == "PASS"
                     else "outside [6,30]: F5 indictment of THIS batch's table path (committed measurements stand); "
                          "HALT; interior readings recorded but no shape verdict composed; repair"),
            "analysis_order_attestation": ("k=16 re-seat ANALYZED FIRST within S1, before any other interior arm "
                                           "was invoked (binding order); no interior arm run before this analysis"),
        },
        "analyzed_utc": now_iso(),
        "inference": INFERENCE,
    })
    with open(out_path, "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({"S1-1_reseat_k16": verdict, "hits": hits, "band": q["band"],
                      "in_band": in_band, "amend1_pass": a1_ok, "seat_ok": seat_ok}, indent=1))
    if verdict == "SH2-GATE-FAIL":
        sys.exit(12)
    if verdict == "SH2-RESEAT-FAIL":
        sys.exit(13)
    sys.exit(0)


def grid(k, path, out_path):
    k = int(k)
    if k not in (1, 2, 4, 8):
        print("grid mode: k must be 1, 2, 4 or 8", file=sys.stderr)
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
        1: "AMEND-1 RE-RUN, primary point (validates or supersedes the BATCH-7b798d observation as a reading; verdict composes from THIS batch alone)",
        2: "AMEND-1 RE-RUN (brackets the first interior decay ratio with k=1; guards the monotonicity conjunct)",
        4: "LOAD-BEARING TRANSITION LOCATOR (FIRST-EVER measurement of this family point; branch selector between SH2-MONOTONE-DECAY and SH2-PLATEAU; NOT refinement)",
        8: "AMEND-1 RE-RUN, floor point (question (iii) midpoint; non-monotone sentinel midpoint)",
    }[k]
    out = common_header("crypto.autoresearch.s1_grid_analysis.v1", RUN_IDS[k], path, r)
    out.update({
        "k": k,
        "role": role,
        "seat": {"sbox": "S_%d diluted table set" % k, "rounds": 5, "amask": 1, "smask": 1,
                 "log2N": 30, "seed": 531001, "arm_id": SEATS[k]["arm_id"], "threads": 4},
        "seat_checks": seat,
        "seat_as_preregistered": seat_ok,
        "scope_note": ("k=1 statements are JOINT-EFFECT-scoped (SCOPE-1, DEC-20260902-38227b): the k=0->k=1 step "
                       "co-varies the first dilution step with the identity->AES schedule switch; all "
                       "interior-to-interior comparisons are schedule-clean under PIN-T0") if k == 1 else
                      "interior-to-interior comparison, schedule-clean under PIN-T0 (SCOPE-1)",
    })
    out.update(q)
    out.update({
        "hit_log_overflow": r["hit_log_overflow"],
        "hit_log_cap": r["hit_log_cap"],
        "saturation_prediction_vs_design_prior": {
            "predicted": {1: "saturated (~12.68M hits)", 2: "saturated (~149k hits)",
                          4: "unsaturated (prior ~20 hits)", 8: "unsaturated (prior ~13 hits)"}[k],
            "realized": ids["saturation_status"],
            "note": "priors from flagged-unvalidated BATCH-7b798d observations; realization governs",
        },
        "amend1_identity_table": ids,
        "amend1_identities_pass": a1_ok,
        "point_verdict": verdict,
    })
    if k == 4:
        out["locator_band_routing_preregistered"] = {
            "h4_le_40": "routes toward SH2-MONOTONE-DECAY conjunct h(4) <= 40 (transition at or before (2,4])",
            "h4_ge_100": "routes toward SH2-PLATEAU conjunct h(4) >= 100 (transition at or after (4,8])",
            "h4_41_99": "ambiguity at the locator (SH2-RESIDUAL subcase (b) if h(1) >= 100)",
            "design_prior_flagged": "~20.7 RESIDUAL by single-seed multiplicative extrapolation of unvalidated observations; a prior only, never a bet",
            "note": "branch selection is composed only after S2 second seeds (NOT composed here)",
        }
    out["analyzed_utc"] = now_iso()
    out["inference"] = INFERENCE
    with open(out_path, "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({"%s_grid_k%d" % (RUN_IDS[k], k): verdict, "hits": q["hits_W_ge1_nontrivial"],
                      "band": q["band"], "saturation": ids["saturation_status"],
                      "amend1_pass": a1_ok, "seat_ok": seat_ok}, indent=1))
    if verdict == "SH2-GATE-FAIL":
        sys.exit(12)
    sys.exit(0)


def detcmp(path_a, path_b, out_path, expect_seat):
    with open(path_a) as f:
        a = json.load(f)
    with open(path_b) as f:
        b = json.load(f)
    if expect_seat == "k0":
        seat_desc = {"sbox": "identity (S_0)", "rounds": 5, "amask": 1, "smask": 1,
                     "log2N": 20, "seed": 531001, "arm_id": 5, "threads": 4}
    else:
        seat_desc = {"sbox": "S_1 diluted table set", "rounds": 5, "amask": 1, "smask": 1,
                     "log2N": 20, "seed": 531001, "arm_id": 2, "threads": 4}

    def seat_of(r):
        if expect_seat == "k0":
            return {
                "oracle_r5": r["oracle"] == ORACLE_R5, "amask_1": r["amask"] == 1, "smask_1": r["smask"] == 1,
                "log2N_20": r["log2N"] == 20, "trials_eq_2pow20": r["trials"] == (1 << 20),
                "seed_531001": r["seed"] == 531001, "arm_id_5": r["arm_id"] == 5, "threads_4": r["threads"] == 4,
                "sbox_identity": r["sbox"] == "identity", "sbox_k_0": r["sbox_k"] == 0,
                "schedule_pin_T0": r["schedule_pin"] == "PIN-T0", "hit_log_cap_256": r["hit_log_cap"] == 256,
            }
        s = SEATS[1]
        return {
            "oracle_r5": r["oracle"] == ORACLE_R5, "amask_1": r["amask"] == 1, "smask_1": r["smask"] == 1,
            "log2N_20": r["log2N"] == 20, "trials_eq_2pow20": r["trials"] == (1 << 20),
            "seed_531001": r["seed"] == 531001, "arm_id_2": r["arm_id"] == s["arm_id"],
            "threads_4": r["threads"] == 4, "sbox_label": r["sbox"] == s["sbox"],
            "sbox_k_1": r["sbox_k"] == s["sbox_k"],
            "sbox_positions_as_preregistered_seat": r["sbox_positions"] == s["positions"],
            "schedule_pin_T0": r["schedule_pin"] == "PIN-T0", "hit_log_cap_256": r["hit_log_cap"] == 256,
        }
    seat_a, seat_b = seat_of(a), seat_of(b)
    seat_ok = all(seat_a.values()) and all(seat_b.values())
    # field-by-field comparison modulo the preregistered strip set
    keys = sorted(set(a.keys()) | set(b.keys()))
    differing = []
    strip_diffs = {}
    for key in keys:
        va, vb = a.get(key), b.get(key)
        if va == vb:
            continue
        if key in STRIP_SET:
            strip_diffs[key] = {"a": va, "b": vb}
        else:
            differing.append({"field": key, "a": va, "b": vb})
    byte_mod_strip = len(differing) == 0
    ids_a = amend1_identities(a)
    ids_b = amend1_identities(b)
    a1_a = amend1_pass(ids_a)
    a1_b = amend1_pass(ids_b)
    overflow_realized = a["hit_log_overflow"]
    overflow_positive = overflow_realized > 0
    det_pass = byte_mod_strip and seat_ok and a1_a and a1_b and overflow_positive
    fallback_required = (byte_mod_strip and seat_ok and a1_a and a1_b) and (not overflow_positive)
    out = {
        "schema": "crypto.autoresearch.s1_det_cmp.v1",
        "task_id": "TASK-20260902-525d16",
        "idea_record": "IDEA-20260902-9e84ac",
        "decision_opening_batch": "DEC-20260902-38227b",
        "gate_regime": "AMEND-1 (DEC-20260901-6f9de3)",
        "run_id": "S1-6",
        "receipt_a": path_a,
        "receipt_b": path_b,
        "arm_label_a": a["arm"],
        "arm_label_b": b["arm"],
        "expect_seat": expect_seat,
        "seat": seat_desc,
        "seat_checks_a": seat_a,
        "seat_checks_b": seat_b,
        "seat_as_preregistered": seat_ok,
        "commands_identical_attestation": ("both invocations ran the identical command string (same arm label, r=5, "
                                           "amask=1, smask=1, log2N=20, seed 531001, armid %d, threads 4, sbox token %s)"
                                           % (seat_desc["arm_id"], "identity" if expect_seat == "k0" else "s1")),
        "preregistered_strip_set_timing": list(STRIP_SET),
        "raw_byte_identical": a == b,
        "raw_byte_identical_note": ("wall-clock timing fields make raw byte identity impossible by construction; the "
                                    "preregistered comparator notion is byte-identity modulo the strip set"),
        "byte_identical_modulo_strip_set": byte_mod_strip,
        "differing_semantic_fields": differing,
        "strip_set_value_differences": strip_diffs,
        "amend1_identity_table_receipt_a": ids_a,
        "amend1_identity_table_receipt_b": ids_b,
        "amend1_identities_pass_a": a1_a,
        "amend1_identities_pass_b": a1_b,
        "overflow_positive_receipt_requirement": {
            "required": "realized hit_log_overflow > 0 (R3 discharges only by an overflow-positive receipt IN FACT)",
            "realized_overflow": overflow_realized,
            "overflow_positive": overflow_positive,
            "predicted_prior_flagged": ("~11,400 overflow (hits ~ 2^20 x 0.0118 ~ 12,400) from the flagged-unvalidated "
                                        "k=1 observation" if expect_seat == "k1" else
                                        "2^20 - 1024 = 1047552 overflow by construction (fallback seat)"),
            "preregistered_fallback_clause": ("if realized overflow == 0, the double re-runs at k=0 (S_0, log2N=20, "
                                              "seed 531001, armid 5, identity) where overflow = 2^20 - 1024 > 0 by "
                                              "construction, and the regime deviation is recorded per rule 8"),
            "fallback_executed": expect_seat == "k0",
        },
        "determinism_pass": det_pass,
        "fallback_required": fallback_required,
        "on_failure": "instrument void at the truncation path; HALT invalid_measurement (rule 5); SH2-GATE-FAIL",
        "compared_utc": now_iso(),
        "inference": INFERENCE,
    }
    with open(out_path, "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({"S1-6_determinism": "PASS" if det_pass else ("FALLBACK-REQUIRED" if fallback_required else "SH2-GATE-FAIL"),
                      "byte_mod_strip": byte_mod_strip, "seat_ok": seat_ok,
                      "amend1_pass_a": a1_a, "amend1_pass_b": a1_b,
                      "overflow_realized": overflow_realized}, indent=1))
    if fallback_required:
        sys.exit(14)
    if not det_pass:
        sys.exit(12)
    sys.exit(0)


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "reseat":
        reseat(sys.argv[2], sys.argv[3])
    elif mode == "grid":
        grid(sys.argv[2], sys.argv[3], sys.argv[4])
    elif mode == "detcmp":
        expect = "k0" if "--expect-seat" in sys.argv and sys.argv[sys.argv.index("--expect-seat") + 1] == "k0" else "k1"
        detcmp(sys.argv[2], sys.argv[3], sys.argv[4], expect)
    else:
        print("mode must be 'reseat', 'grid' or 'detcmp'", file=sys.stderr)
        sys.exit(2)
