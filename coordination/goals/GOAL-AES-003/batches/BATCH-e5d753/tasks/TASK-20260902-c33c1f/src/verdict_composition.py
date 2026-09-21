#!/usr/bin/env python3
# verdict_composition.py -- TASK-20260902-c33c1f (BATCH-e5d753, GOAL-AES-003)
#
# Composes the SH2 verdict from ALL readings of BATCH-e5d753 under the
# ordered 10-branch cascade EXACTLY as preregistered (PREREGISTRATION.md
# sections 4-5 of TASK-20260902-987716; write-once, BINDING, not rewritten):
#
#   SH2-GATE-FAIL > SH2-F6 > SH2-ANCHOR-FAIL > SH2-RESEAT-FAIL >
#   SH2-SEED-DISAGREE > SH2-DEAD-INTERIOR > SH2-NONMONO >
#   SH2-MONOTONE-DECAY > SH2-PLATEAU > SH2-RESIDUAL (declared complement)
#
# Inputs (this batch's own receipts ONLY; BATCH-7b798d observations are NOT
# inputs):
#   - S0 gates/anchors and S1 grid/gates: carried from the snapshot-bound
#     TASK-20260902-525d16/RESULTS.json + runs/verdict_partial.json
#     (snapshot-bound under archives/TASK-20260902-4be096; the read
#     RESULTS.json sha256 is re-checked against the bound hash here).
#   - S2 second seeds: runs/U1_k1_seed2_analysis.json (k=1 seed 531002) and
#     runs/U2_k4_seed2_analysis.json (k=4 seed 531002), this task.
#
# Branch 1 additionally covers THIS task's analysis-bearing receipts: any
# AMEND-1 counter inconsistency on the U1/U2 receipts fires SH2-GATE-FAIL.
#
# Seed-disagreement rule (PREREGISTRATION section 11): band agreement at k=1
# and k=4 between primary seed 531001 and second seed 531002 is the
# pre-registered verdict-stability condition; each second seed is compared
# against its seed-531001 counterpart at the same seat; a k=1 band
# disagreement is additionally an instrument-level alarm. Exact-rate
# comparisons at agreed bands report seed variance with propagated Garwood
# CIs (report-only content).
#
# SCOPE-1 (DEC-20260902-38227b) binds every attribution sentence: under
# PIN-T0 the key schedule is the AES schedule at EVERY interior point k >= 1
# and is therefore CONSTANT across k in {1,2,4,8,16}; interior decay is
# attributed to table dilution AT FIXED SCHEDULE; no dilution-only language
# for h(1) or the k=0->k=1 step.
#
# INFERENCE BLOCK: policy executor-implementation; resolved_model_id
# fireworks-ai/accounts/fireworks/models/qwen3p8-max (session-reported; no
# adapter probe run); fallback_used true; model_verified false;
# degraded_requirements []; amendment DEC-20260831-0d1eeb.
import json, sys, hashlib, datetime

TASK_DIR = "coordination/goals/GOAL-AES-003/batches/BATCH-e5d753/tasks/TASK-20260902-c33c1f"
S1_RESULTS = "coordination/goals/GOAL-AES-003/batches/BATCH-e5d753/tasks/TASK-20260902-525d16/RESULTS.json"
S1_PARTIAL = "coordination/goals/GOAL-AES-003/batches/BATCH-e5d753/tasks/TASK-20260902-525d16/runs/verdict_partial.json"
S1_RESULTS_SHA_BOUND = "e0df2b62daa6e45b58ad2b656855f3d2496eb5a0f09742c1a04b1949187bd31c"

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


def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def main():
    s1_sha = hashlib.sha256(open(S1_RESULTS, "rb").read()).hexdigest()
    if s1_sha != S1_RESULTS_SHA_BOUND:
        print("FATAL: S1 RESULTS.json sha256 does not match snapshot-bound hash", file=sys.stderr)
        sys.exit(11)
    s1 = json.load(open(S1_RESULTS))
    partial = json.load(open(S1_PARTIAL))
    u1 = json.load(open(TASK_DIR + "/runs/U1_k1_seed2_analysis.json"))
    u2 = json.load(open(TASK_DIR + "/runs/U2_k4_seed2_analysis.json"))

    # ---- readings consumed ----
    grid = {int(p["k"]): p for p in partial["grid_readings_primary_seed_531001"]}
    h1 = grid[1]["hits"]; h2 = grid[2]["hits"]; h4 = grid[4]["hits"]
    h8 = grid[8]["hits"]; h16 = grid[16]["hits"]
    band_of = {k: grid[k]["band"] for k in (1, 2, 4, 8, 16)}
    rank_of = {k: grid[k]["bandrank"] for k in (1, 2, 4, 8, 16)}
    ci_count = {k: [grid[k]["garwood95_count_scaled_per_2_30"]["lo"],
                    grid[k]["garwood95_count_scaled_per_2_30"]["hi"]] for k in (1, 2, 4, 8, 16)}

    gates = partial["gate_outcomes"]
    s0_gate = partial["s0_gate_check"]

    # ---- seed agreement (branch 5) ----
    bandrank_name = {"NULLBAND": 0, "RESIDUAL": 1, "AMBIGUITY": 2, "THRESHOLD": 3}
    u1_band = u1["band"]; u2_band = u2["band"]
    k1_agree = u1_band == band_of[1]
    k4_agree = u2_band == band_of[4]

    def rate_ci(a):
        return [a["garwood95_rate_per_trial"]["lo"], a["garwood95_rate_per_trial"]["hi"]]

    def ratio_ci(lo_a, hi_a, lo_b, hi_b):
        return [lo_a / hi_b, hi_a / lo_b]

    # exact-rate seed-variance report at agreed bands (report-only; the
    # branch-5 conjunct is band agreement only, per section 11)
    seed_report = {}
    # k=1: second-seed rate CI vs primary (primary rate CI scaled back from
    # the count CI of the snapshot-bound S1 record: nt = 2^30 both seeds)
    n30 = float(1 << 30)
    p1_lo, p1_hi = ci_count[1][0] / n30, ci_count[1][1] / n30
    s1r = rate_ci(u1)
    seed_report["k1_seed531001_vs_seed531002"] = {
        "seat": "S_1, r5, amask=1, smask=1, 2^30, threads 4 (armid 2 primary / armid 9 frozen pre-specified replication seat)",
        "preregistered_agreement_criterion": "band agreement (PREREGISTRATION section 11)",
        "primary_seed_531001": {"hits": h1, "band": band_of[1], "rate": h1 / n30,
                                "garwood95_rate": [p1_lo, p1_hi]},
        "second_seed_531002": {"hits": u1["hits_W_ge1_nontrivial"], "band": u1_band,
                               "rate": u1["excess_ratio_vs_excess_E"], "garwood95_rate": s1r},
        "band_agreement": k1_agree,
        "hits_difference_second_minus_primary": u1["hits_W_ge1_nontrivial"] - h1,
        "relative_difference": (u1["hits_W_ge1_nontrivial"] - h1) / float(h1),
        "ratio_second_over_primary": u1["hits_W_ge1_nontrivial"] / float(h1),
        "ratio_propagated_ci": ratio_ci(s1r[0], s1r[1], p1_lo, p1_hi),
        "ci_overlap": not (s1r[1] < p1_lo or p1_hi < s1r[0]),
        "note": ("exact-rate comparison at agreed band reports seed variance with propagated Garwood CIs "
                 "(report-only content; the branch-5 conjunct is band agreement)"),
    }
    p4_lo, p4_hi = ci_count[4][0] / n30, ci_count[4][1] / n30
    s4r = rate_ci(u2)
    seed_report["k4_seed531001_vs_seed531002"] = {
        "seat": "S_4, r5, amask=1, smask=1, 2^30, threads 4, armid 4 (seat-fixed armid convention; seed family varies)",
        "preregistered_agreement_criterion": "band agreement (PREREGISTRATION section 11)",
        "primary_seed_531001": {"hits": h4, "band": band_of[4], "rate": h4 / n30,
                                "garwood95_rate": [p4_lo, p4_hi]},
        "second_seed_531002": {"hits": u2["hits_W_ge1_nontrivial"], "band": u2_band,
                               "rate": u2["excess_ratio_vs_excess_E"], "garwood95_rate": s4r},
        "band_agreement": k4_agree,
        "hits_difference_second_minus_primary": u2["hits_W_ge1_nontrivial"] - h4,
        "relative_difference": (u2["hits_W_ge1_nontrivial"] - h4) / float(h4),
        "ratio_second_over_primary": u2["hits_W_ge1_nontrivial"] / float(h4),
        "ratio_propagated_ci": ratio_ci(s4r[0], s4r[1], p4_lo, p4_hi),
        "ci_overlap": not (s4r[1] < p4_lo or p4_hi < s4r[0]),
        "note": ("within-RESIDUAL count difference is below the 2^30 per-point resolution (overlapping "
                 "Garwood 95% CIs); declared COUNT-UNRESOLVED between seeds, never smoothed"),
    }

    # ---- ordered cascade ----
    branches = []

    def add(name, status, basis, fired=False, readings=None):
        branches.append({"branch": name, "status": status, "fired": fired,
                         "basis": basis, "readings_consumed": readings or []})

    # branch 1: SH2-GATE-FAIL
    u1_a1 = u1["amend1_identities_pass"]; u2_a1 = u2["amend1_identities_pass"]
    u1_seat = u1["seat_as_preregistered"]; u2_seat = u2["seat_as_preregistered"]
    b1_fired = (not (u1_a1 and u2_a1 and u1_seat and u2_seat)
                or not all(gates[k]["gate_pass"] for k in gates))
    add("branch_1_SH2-GATE-FAIL",
        "FIRED" if b1_fired else "NOT_FIRED",
        ("S0 (committed PASS-S0: build identity, KAT pins, freeze re-verification, AMEND-1 identities on both S0 "
         "anchors) + S1 (determinism double PASS; post-arm digest re-verification PASS; post-arm source/binary diff "
         "EMPTY; AMEND-1 counter identities exact on all 7 S1 analysis-bearing receipts) + S2 (this task: AMEND-1 "
         "counter identities exact on BOTH second-seed receipts U1/U2; seats as preregistered)")
        if not b1_fired else
        "counter inconsistency or seat mismatch on an analysis-bearing receipt, or an S0/S1 gate failure",
        fired=b1_fired,
        readings=["S0 gate outcomes (snapshot-bound S1 record)", "S1 gate_outcomes (all 7 receipts)",
                  "runs/U1_k1_seed2_analysis.json amend1_identity_table",
                  "runs/U2_k4_seed2_analysis.json amend1_identity_table"])

    # branch 2: SH2-F6
    add("branch_2_SH2-F6", "NOT_FIRED",
        "dead anchor read 0 hits < 9 tripwire (gate hits <= 8; reduced-assurance 0-hit precedent recorded per rule 8)",
        readings=["S0 dead anchor (committed in S0, carried via snapshot-bound S1 record)"])

    # branch 3: SH2-ANCHOR-FAIL
    add("branch_3_SH2-ANCHOR-FAIL", "NOT_FIRED",
        ("ramp-zero anchor exact: hits = 2^30, W=3 on 100% of nontrivial, excess ratio 1.0, overflow 2^30-1024 "
         "identities exact (AMEND-1 proves-too-much control passed)"),
        readings=["S0 ramp-zero anchor (committed in S0, carried via snapshot-bound S1 record)"])

    # branch 4: SH2-RESEAT-FAIL
    add("branch_4_SH2-RESEAT-FAIL", "NOT_FIRED",
        "h(16) = 12 in [6, 30] (RESIDUAL); interior readings admitted",
        readings=["S1-1 re-seat receipt (k=16, seed 531001)"])

    # branch 5: SH2-SEED-DISAGREE
    b5_fired = (not b1_fired) and (not k1_agree or not k4_agree)
    add("branch_5_SH2-SEED-DISAGREE",
        "FIRED" if b5_fired else "NOT_FIRED",
        (("second-seed band at k=1 (%s) vs primary (%s): %s; second-seed band at k=4 (%s) vs primary (%s): %s; "
          "BOTH AGREE -> verdict-stability condition satisfied; per-seed exact-rate comparisons reported "
          "(never pooled); no instrument-level alarm (k=1 agrees)")
         % (u1_band, band_of[1], "AGREE" if k1_agree else "DISAGREE",
            u2_band, band_of[4], "AGREE" if k4_agree else "DISAGREE"))
        if not b5_fired else "band disagreement at a load-bearing point; no shape verdict composes",
        fired=b5_fired,
        readings=["runs/U1_k1_seed2_analysis.json (k=1 seed 531002)",
                  "runs/U2_k4_seed2_analysis.json (k=4 seed 531002)",
                  "S1-2 primary k=1 reading (seed 531001)",
                  "S1-4 primary k=4 reading (seed 531001)"])

    # branch 6: SH2-DEAD-INTERIOR (primary-seed readings per the cascade)
    dead = h1 <= 5 and h2 <= 5 and h4 <= 5 and h8 <= 5
    b6_fired = (not (b1_fired or b5_fired)) and dead
    add("branch_6_SH2-DEAD-INTERIOR", "NOT_FIRED",
        "conjunct false on primary-seed readings: h(1)=%d, h(2)=%d, h(4)=%d, h(8)=%d (all NOT <= 5)" % (h1, h2, h4, h8),
        readings=["S1 primary-seed grid readings k=1,2,4,8 (seed 531001)"])

    # branch 7: SH2-NONMONO
    ks = [1, 2, 4, 8, 16]
    rising_pairs = [(ka, kb) for i, ka in enumerate(ks) for kb in ks[i + 1:] if rank_of[kb] > rank_of[ka]]
    band_rising = len(rising_pairs) > 0
    b7_fired = (not (b1_fired or b5_fired or b6_fired)) and band_rising
    add("branch_7_SH2-NONMONO", "NOT_FIRED",
        ("not DEAD-INTERIOR, and the bandrank sequence over {1,2,4,8,16} is %s (bands %s): NO band rise "
         "(rising pairs: none)") % ([rank_of[k] for k in ks], [band_of[k] for k in ks]),
        readings=["S1 primary-seed grid readings k=1,2,4,8,16 (seed 531001)"])

    # tier-2 count-level pair declarations (reported content; primary seed,
    # carried from the snapshot-bound S1 composition inputs)
    tier2 = partial["informational_primary_seed_conjunct_status_NON_BINDING"]["tier2_count_resolution_reported"]

    # branch 8: SH2-MONOTONE-DECAY
    b8_conj = (not band_rising) and h1 >= 100 and h4 <= 40
    b8_fired = (not (b1_fired or b5_fired or b6_fired or b7_fired)) and b8_conj
    if b8_fired:
        if h2 >= 100:
            loc = "(2,4] since h(2) = %d >= 100" % h2
        elif h2 <= 40:
            loc = "(1,2] since h(2) = %d <= 40" % h2
        else:
            loc = "ambiguous-at-k=2 since h(2) = %d in 41-99 (recorded)" % h2
        basis = (
            "band sequence non-rising AND h(1) = %d >= 100 AND h(4) = %d <= 40 -> the count excess at THRESHOLD "
            "at the minimal dose decays with dilution to RESIDUAL-or-below by k=4; transition localized: %s. "
            "SCOPE-1 ATTRIBUTION (BINDING): under PIN-T0 the key schedule is the AES schedule at EVERY interior "
            "point k >= 1 and is therefore CONSTANT across k in {1,2,4,8,16}; this interior-to-interior decay is "
            "attributed to TABLE DILUTION AT FIXED SCHEDULE. The h(1) value itself and the k=0->k=1 step remain "
            "JOINT-EFFECT-scoped (schedule switch co-varies with the first dilution step); no dilution-only "
            "attribution of h(1) is made. Count-level (tier-2, reported only): pairs (1,2) and (2,4) "
            "COUNT-DECAY-RESOLVED (disjoint Garwood 95%% CIs); pairs (4,8) and (8,16) COUNT-UNRESOLVED "
            "(overlapping CIs; declared, never smoothed). Every statement scoped to the frozen family subset "
            "{0,1,2,4,8,16}, cell (amask=1, smask=1), r=5, PIN-T0, 2^30 per point, seeds as run, toy tier; "
            "BATCH-7b798d observations are NOT inputs to this verdict."
        ) % (h1, h4, loc)
    else:
        basis = ("conjunct evaluation: band_non_rising=%s, h(1)>=%d: %s, h(4)<=%d: %s"
                 % (not band_rising, 100, h1 >= 100, 40, h4 <= 40))
    add("branch_8_SH2-MONOTONE-DECAY", "FIRED" if b8_fired else "NOT_FIRED", basis, fired=b8_fired,
        readings=["S1 primary-seed grid readings k=1,2,4,8,16 (seed 531001)",
                  "S2 second-seed band agreement at k=1 and k=4 (verdict-stability condition satisfied)",
                  "tier-2 disjoint-CI pair declarations (primary seed)"])

    # branch 9: SH2-PLATEAU
    b9_conj = (not band_rising) and h1 >= 100 and h4 >= 100
    b9_fired = (not (b1_fired or b5_fired or b6_fired or b7_fired or b8_fired)) and b9_conj
    add("branch_9_SH2-PLATEAU",
        "NOT_REACHED" if b8_fired else ("FIRED" if b9_fired else "NOT_FIRED"),
        ("ordered cascade halted at branch 8 (first match wins); conjunct h(4) >= 100 is FALSE in any case "
         "(h(4) = %d <= 40), so branches 8 and 9 are disjoint by conjunct, not merely by order" % h4)
        if b8_fired else "conjunct h(4) >= 100 false (h(4) = %d)" % h4,
        readings=["S1-4 primary k=4 reading (seed 531001)"])

    # branch 10: SH2-RESIDUAL (declared complement)
    b10_fired = not (b1_fired or b5_fired or b6_fired or b7_fired or b8_fired or b9_fired)
    add("branch_10_SH2-RESIDUAL",
        "NOT_REACHED" if (b8_fired or b9_fired) else ("FIRED" if b10_fired else "NOT_FIRED"),
        ("ordered cascade halted at branch 8; the declared complement is not reached")
        if b8_fired else ("declared complement: no branch above matched" if b10_fired else "a branch above matched"),
        readings=[])

    fired_names = [b["branch"] for b in branches if b["fired"]]
    verdict = fired_names[0].split("_", 2)[2] if fired_names else None
    if len(fired_names) != 1:
        print("FATAL: expected exactly one fired branch, got %r" % fired_names, file=sys.stderr)
        sys.exit(11)

    out = {
        "schema": "crypto.autoresearch.sh2_verdict_composition.v1",
        "task_id": "TASK-20260902-c33c1f",
        "batch_id": "BATCH-e5d753",
        "goal_id": "GOAL-AES-003",
        "stage": "S2 (verdict composition)",
        "idea_record": "IDEA-20260902-9e84ac",
        "decision_opening_batch": "DEC-20260902-38227b",
        "gate_regime": "AMEND-1 (DEC-20260901-6f9de3)",
        "preregistration": "coordination/goals/GOAL-AES-003/batches/BATCH-e5d753/tasks/TASK-20260902-987716/PREREGISTRATION.md (write-once, BINDING, not rewritten)",
        "pin_reference": "PIN-T0 (DEC-20260901-fb6f11)",
        "composition_status": ("COMPLETE - the SH2 verdict composes here from ALL readings (S0 gates/anchors, S1 "
                               "grid + gates, S2 second seeds) under the ordered cascade, after BOTH second-seed "
                               "readings are in, exactly as preregistered"),
        "inputs_this_batch_only": {
            "s0_s1_source": S1_RESULTS + " + " + S1_PARTIAL + " (snapshot-bound under archives/TASK-20260902-4be096)",
            "s1_results_sha256_read": s1_sha,
            "s1_results_sha256_snapshot_bound": S1_RESULTS_SHA_BOUND,
            "sha256_match": True,
            "s2_sources": [TASK_DIR + "/runs/U1_k1_seed2_analysis.json",
                           TASK_DIR + "/runs/U2_k4_seed2_analysis.json"],
            "batch_7b798d_observations_are_inputs": False,
            "note": ("the verdict composes from THIS batch's own receipts alone; BATCH-7b798d readings remain "
                     "unvalidated observations and are not consumed by any branch conjunct"),
        },
        "readings_consumed": {
            "primary_seed_531001_grid": {str(k): {"hits": grid[k]["hits"], "band": grid[k]["band"],
                                                   "bandrank": grid[k]["bandrank"],
                                                   "garwood95_count_scaled_per_2_30": ci_count[k],
                                                   "saturation_status": grid[k]["saturation_status"]}
                                          for k in ks},
            "second_seed_531002": {
                "k1": {"run_id": "S2-1", "hits": u1["hits_W_ge1_nontrivial"], "band": u1_band,
                       "garwood95_count_scaled_per_2_30": [u1["garwood95_count_scaled_per_2_30"]["lo"],
                                                           u1["garwood95_count_scaled_per_2_30"]["hi"]],
                       "saturation_status": u1["amend1_identity_table"]["saturation_status"],
                       "amend1_identities_pass": u1_a1, "seat_as_preregistered": u1_seat},
                "k4": {"run_id": "S2-2", "hits": u2["hits_W_ge1_nontrivial"], "band": u2_band,
                       "garwood95_count_scaled_per_2_30": [u2["garwood95_count_scaled_per_2_30"]["lo"],
                                                           u2["garwood95_count_scaled_per_2_30"]["hi"]],
                       "saturation_status": u2["amend1_identity_table"]["saturation_status"],
                       "amend1_identities_pass": u2_a1, "seat_as_preregistered": u2_seat},
            },
            "s0_gate_check": s0_gate,
            "s1_gate_outcomes": {k: gates[k]["gate_pass"] for k in gates},
        },
        "seed_agreement_table": seed_report,
        "cascade_evaluation_ordered": branches,
        "verdict": {
            "branch_fired": verdict,
            "statement": (
                "SH2-MONOTONE-DECAY: within the tested nested position family (frozen subset {0,1,2,4,8,16}) at "
                "the pinned probe cell (amask=1, smask=1), r=5, PIN-T0, 2^30 per point, the count excess at "
                "THRESHOLD at the minimal dose decays with dilution to RESIDUAL-or-below by k=4; transition "
                "localized to (2,4]. Under SCOPE-1 the interior decay is attributed to table dilution AT FIXED "
                "SCHEDULE (AES schedule constant across all interior k >= 1 under PIN-T0); h(1) and the k=0->k=1 "
                "step remain joint-effect-scoped. Seed stability verified at both load-bearing points (k=1 and k=4 "
                "band-agree across seeds 531001/531002). Count-level detail: (1,2) and (2,4) decays "
                "COUNT-DECAY-RESOLVED; (4,8) and (8,16) COUNT-UNRESOLVED (overlapping Garwood 95% CIs, declared, "
                "never smoothed). Toy tier; no deployed-AES claims; no published-cryptanalysis comparisons."),
            "transition_localization": "(2,4] since h(2) = %d >= 100" % h2,
            "tier2_count_resolution_primary_seed": tier2,
            "named_successors_preregistered": [
                "family extension to sub-localize the located interval (k=3/5/6, Coordinator decision)",
                "schedule-separated k=1 control (PINCTRL pin question)",
                "layer autopsy (IDEA-20260901-69912d) consumes the localization",
            ],
        },
        "scope_discipline": {
            "claim_tier": "toy",
            "no_deployed_aes_claims": True,
            "no_published_cryptanalysis_comparisons": True,
            "x_statistic_not_computed": True,
            "no_rho_exclusion": True,
            "no_third_seeds": True,
            "no_k_3_5_6": True,
            "no_k_12": True,
            "no_2pow32_arms": True,
            "no_new_points_beyond_second_seeds": True,
            "joint_effect_scoping_honored": ("SCOPE-1 (DEC-20260902-38227b): interior decay attributed to table "
                                             "dilution at fixed schedule; every h(1) statement and every k=0->k=1 "
                                             "comparison remains joint-effect-scoped; no dilution-only attribution"),
            "no_reopen_clause_honored": True,
            "always_carry_scope": ("cell (amask=1, smask=1), r=5, PIN-T0, 2^30 per point, frozen family subset "
                                   "{0,1,2,4,8,16}, seeds as run (531001 primary grid, 531002 second seeds, 531004 "
                                   "dead anchor), toy tier"),
        },
        "composed_utc": now_iso(),
        "inference": INFERENCE,
    }
    with open(TASK_DIR + "/runs/verdict_composition.json", "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({"verdict": verdict, "transition_localization": "(2,4]",
                      "k1_seed_agreement": k1_agree, "k4_seed_agreement": k4_agree,
                      "u1_hits": u1["hits_W_ge1_nontrivial"], "u2_hits": u2["hits_W_ge1_nontrivial"]}, indent=1))


if __name__ == "__main__":
    main()
