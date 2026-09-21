#!/usr/bin/env python3
# s0_analysis.py -- TASK-20260901-706b1d (BATCH-7b798d, GOAL-AES-003)
#
# S0 anchor analysis (fresh for this task). Consumes the two reading-bearing
# S0 receipts and writes the preregistered gate analyses:
#   runs/S4_dead_anchor.json  -> runs/S4_dead_analysis.json
#       DEAD ANCHOR, ANALYZED FIRST among reading-bearing arms (PREREGISTRATION
#       section 4/7): gate hits <= 8 at 2^30 (carried dead band); tripwire
#       hits >= 9 -> SH-F6 halt, no interior surface admitted.
#   runs/S5_rampzero.json     -> runs/S5_rampzero_analysis.json
#       RAMP-ZERO ANCHOR (BLOCKING; PREREGISTRATION section 7): hits = 2^30,
#       W = 3 on 100% of nontrivial trials, excess ratio 1.0 exact against the
#       frozen excess_E = 2^30 comparator convention (EV-AES-ec53f1); any
#       departure -> SH-ANCHOR-FAIL (F3) halt.
# Garwood 95% CIs by the design-time Wilson-Hilferty chi-squared quantile
# convention (IDEA-20260901-582ea9 design_time_power computation_provenance).
# Exit: 0 both anchors pass; 9 = dead-anchor tripwire (SH-F6);
#       10 = ramp-zero anchor failure (SH-ANCHOR-FAIL); 11 = other gate issue.
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
DEAD_BAND_2_30 = 8          # carried dead band at 2^30
F6_TRIPWIRE = 9
Z_LO, Z_HI = -1.959963984540054, 1.959963984540054


def chi2_q(p, nu):
    # Wilson-Hilferty approximation to the chi-squared quantile (design-time
    # convention of the proposal's power computation).
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


def main():
    s4_path, s5_path, s4_out, s5_out = sys.argv[1:5]
    with open(s4_path) as f:
        s4 = json.load(f)
    with open(s5_path) as f:
        s5 = json.load(f)

    # ---------------- S4: dead anchor ----------------
    hits4 = s4["W_ge1_nontrivial"]
    nt4 = s4["nontrivial_trials"]
    n4 = s4["trials"]
    lo4, hi4 = garwood_ci(hits4, nt4)
    s4_checks = {
        "seat_as_preregistered": (s4["oracle"] == "live_aes_r6_affarm046ex_derivative_of_affarm046"
                                  and s4["amask"] == 1
                                  and s4["smask"] == 1 and s4["log2N"] == 30
                                  and s4["seed"] == 531004 and s4["arm_id"] == 1
                                  and s4["threads"] == 4 and s4["sbox"] == "aes"
                                  and s4["sbox_k"] == 16
                                  and s4["schedule_pin"] == "PIN-T0"),
        "trials_accounting": s4["trivial_swaps_excluded"] + nt4 == n4 == (1 << 30),
        "whist_sums_to_nontrivial": sum(s4["whist"]) == nt4,
        "wge1_consistent": hits4 == sum(s4["whist"][1:5]),
        "ewhist_all_sums_to_nontrivial": sum(s4["ewhist_all"]) == nt4,
        "ewhist_hit_sums_to_hits": sum(s4["ewhist_hit"]) == hits4,
        "ewhist_miss_sums_to_nonhits": sum(s4["ewhist_miss"]) == nt4 - hits4,
        "hit_log_overflow_zero": s4["hit_log_overflow"] == 0,
    }
    gate_pass4 = hits4 <= DEAD_BAND_2_30
    tripwire4 = hits4 >= F6_TRIPWIRE
    s4_analysis = {
        "schema": "crypto.autoresearch.s0_dead_anchor_analysis.v1",
        "task_id": "TASK-20260901-706b1d",
        "idea_record": "IDEA-20260901-582ea9",
        "pin_decision": "DEC-20260901-fb6f11",
        "run_id": "S0-5",
        "receipt": s4_path,
        "arm": s4["arm"],
        "seat": {"sbox": "aes", "rounds": 6, "amask": 1, "smask": 1,
                 "log2N": 30, "seed": 531004, "arm_id": 1, "threads": 4},
        "hits_W_ge1_nontrivial": hits4,
        "trivial_swaps_excluded": s4["trivial_swaps_excluded"],
        "nontrivial_trials": nt4,
        "whist": s4["whist"],
        "W_ge1_by_word": s4["W_ge1_by_word"],
        "hit_log_overflow": s4["hit_log_overflow"],
        "hit_log_cap": s4["hit_log_cap"],
        "band": band(hits4)[0],
        "bandrank": band(hits4)[1],
        "excess_ratio_vs_excess_E": hits4 / EXCESS_E,
        "excess_E": EXCESS_E,
        "garwood95_rate_per_2_30": {"lo": lo4, "hi": hi4,
                                    "method": "Wilson-Hilferty chi-squared quantile (design-time convention)"},
        "gate": {"dead_band_2_30": DEAD_BAND_2_30, "hits_le_band": gate_pass4,
                 "f6_tripwire": F6_TRIPWIRE, "tripwire_fired": tripwire4},
        "consistency_checks": s4_checks,
        "all_consistency_checks_pass": all(s4_checks.values()),
        "anchor_verdict": ("SH-F6" if tripwire4
                           else ("PASS" if (gate_pass4 and all(s4_checks.values()))
                                 else "GATE-FAIL")),
        "rule8_note": ("a reading of 0 hits passes the gate but is below the ~1-4 hit "
                       "expectation and carries reduced anchor assurance "
                       "(direction-safe; EV-AES-896ef2 n=4 precedent)" if hits4 == 0
                       else "none"),
        "analyzed_utc": now_iso(),
        "analysis_order_attestation": "dead anchor analyzed FIRST among reading-bearing arms, before any alive reading (binding order)",
        "inference": INFERENCE,
    }

    # ---------------- S5: ramp-zero anchor ----------------
    hits5 = s5["W_ge1_nontrivial"]
    nt5 = s5["nontrivial_trials"]
    t5 = s5["trivial_swaps_excluded"]
    n5 = s5["trials"]
    expected_overflow = nt5 - s5["threads"] * min(nt5 // s5["threads"], s5["hit_log_cap"]) \
        if t5 == 0 else None
    s5_checks = {
        "seat_as_preregistered": (s5["oracle"] == "live_aes_r5_affarm046ex_derivative_of_affarm046"
                                  and s5["amask"] == 1
                                  and s5["smask"] == 1 and s5["log2N"] == 30
                                  and s5["seed"] == 531001 and s5["arm_id"] == 5
                                  and s5["threads"] == 4 and s5["sbox"] == "identity"
                                  and s5["sbox_k"] == 0
                                  and s5["schedule_pin"] == "PIN-T0"),
        "trials_accounting": t5 + nt5 == n5 == (1 << 30),
        "hits_equal_2pow30_exact": hits5 == (1 << 30),
        "T_zero": t5 == 0,
        "W3_on_100pct_of_nontrivial": s5["whist"] == [0, 0, 0, nt5, 0],
        "W_ge1_by_word_pattern": s5["W_ge1_by_word"] == [0, nt5, nt5, nt5],
        "excess_ratio_1_exact": hits5 == EXCESS_E,
        "ewhist_hit_all_zero_weight": s5["ewhist_hit"] == [nt5] + [0] * 16,
        "ewhist_all_all_zero_weight": s5["ewhist_all"] == [nt5] + [0] * 16,
        "ewhist_miss_empty": s5["ewhist_miss"] == [0] * 17,
        # W=3 on 100% of nontrivial trials implies Z >= 12 on every trial
        # (three vanishing geometric words contribute 12 equal byte
        # positions); Z = 16 would require W = 4. zhist is NOT part of the
        # preregistered anchor conjuncts; this is a support consistency check.
        "zhist_supports_W3_law": (sum(s5["zhist"][:12]) == 0
                                  and sum(s5["zhist"]) == nt5),
        "pin_t0_identity_schedule_fields": (s5["sbox"] == "identity"
                                            and s5["sbox_k"] == 0
                                            and s5["schedule_pin"] == "PIN-T0"
                                            and s5["schedule_pin_position"] == 0
                                            and s5["schedule_pin_decision"] == "DEC-20260901-fb6f11"),
        "hit_detail_log_truncation_accounting": (expected_overflow is not None
                                                  and s5["hit_log_overflow"] == expected_overflow),
    }
    anchor_pass5 = all(s5_checks.values())
    s5_analysis = {
        "schema": "crypto.autoresearch.s0_rampzero_analysis.v1",
        "task_id": "TASK-20260901-706b1d",
        "idea_record": "IDEA-20260901-582ea9",
        "pin_decision": "DEC-20260901-fb6f11",
        "run_id": "S0-6",
        "receipt": s5_path,
        "arm": s5["arm"],
        "seat": {"sbox": "identity", "rounds": 5, "amask": 1, "smask": 1,
                 "log2N": 30, "seed": 531001, "arm_id": 5, "threads": 4},
        "hits_W_ge1_nontrivial": hits5,
        "trivial_swaps_excluded": t5,
        "nontrivial_trials": nt5,
        "whist": s5["whist"],
        "W_ge1_by_word": s5["W_ge1_by_word"],
        "zhist_16": s5["zhist"][16],
        "excess_ratio_vs_excess_E": hits5 / EXCESS_E,
        "excess_ratio_exact_integer_check": hits5 == EXCESS_E,
        "excess_E": EXCESS_E,
        "hit_log_overflow_observed": s5["hit_log_overflow"],
        "hit_log_overflow_expected_under_cap_convention": expected_overflow,
        "hit_log_cap": s5["hit_log_cap"],
        "hit_log_overflow_note": (
            "At k=0 every nontrivial trial hits, so the capped per-hit DETAIL LOG "
            "necessarily overflows (2^30 hits vs threads x 256 slots). This is the "
            "campaign's frozen cap convention (the committed selfcheck_identity_k0 "
            "assertion pattern expects overflow = nontrivial - threads*min(per_thread, "
            "cap); here per_thread = 2^30/4 > 256). The COUNT observable "
            "(W_ge1_nontrivial, whist, W_ge1_by_word) is cap-independent and is the "
            "anchor gate. Recorded and flagged for the validator per rule 8 because "
            "the cascade's literal 'hit_overflow > 0 on any analysis-bearing receipt' "
            "wording cannot hold at a k=0 anchor under any capped build; see "
            "PREREGISTRATION.md section 5 item 1 note."),
        "consistency_checks": s5_checks,
        "all_consistency_checks_pass": all(s5_checks.values()),
        "anchor_verdict": "PASS" if anchor_pass5 else "SH-ANCHOR-FAIL",
        "analyzed_utc": now_iso(),
        "inference": INFERENCE,
    }

    with open(s4_out, "w") as f:
        json.dump(s4_analysis, f, indent=1)
    with open(s5_out, "w") as f:
        json.dump(s5_analysis, f, indent=1)
    print(json.dumps({"S4_dead_anchor": s4_analysis["anchor_verdict"],
                      "S4_hits": hits4,
                      "S4_tripwire_fired": tripwire4,
                      "S5_rampzero": s5_analysis["anchor_verdict"],
                      "S5_hits": hits5,
                      "S5_excess_ratio_exact": s5_checks["excess_ratio_1_exact"],
                      "S5_all_checks_pass": all(s5_checks.values())}, indent=1))
    if tripwire4:
        sys.exit(9)
    if not anchor_pass5:
        sys.exit(10)
    if not (gate_pass4 and all(s4_checks.values())):
        sys.exit(11)
    sys.exit(0)


if __name__ == "__main__":
    main()
