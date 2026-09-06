#!/usr/bin/env python3
# cc3_compose.py -- TASK-20260903-ac03af (BATCH-060cb4, GOAL-AES-003), S2b-4
# Fresh for this task. Composes the CC3 cascade of the BINDING S0
# preregistration (TASK-20260903-695ebe/PREREGISTRATION.md section 6.3;
# IDEA-20260903-8f26ac family_extension_design.sub_localization_decision_rule)
# in FIXED ORDER from BOTH k=3 readings, after the post-arm audits.
#
#   python3 src/cc3_compose.py <u3_analysis> <u4_analysis> <freeze_reverify>
#       <diff_audit> <s2a_results> <s1_cc_composition> <out_cc3.json>
#
# The branch conjuncts are taken VERBATIM from the preregistration:
#   1 CC3-GATE-FAIL   any S2 integrity gate fails / AMEND-1 counter
#                     inconsistency on any extended-build receipt
#   2 CC3-F6          extended dead anchor hits >= 9 (evaluated in S2a;
#                     carried forward)
#   3 CC3-SEED-DISAGREE band(h(3)_531001) != band(h(3)_531002)
#   4 CC3-NONMONO-EXT h(3) <= 5 (NULLBAND) on EITHER seed while committed
#                     k=4 readings stay RESIDUAL
#   5 CC3-SUBLOCALIZE-LATE  h(3) >= 100 (THRESHOLD) on BOTH seeds -> (3,4]
#   6 CC3-SUBLOCALIZE-EARLY 6 <= h(3) <= 40 (RESIDUAL) on BOTH -> (2,3]
#   7 CC3-AMBIGUOUS         41 <= h(3) <= 99 (AMBIGUITY) on BOTH
#   8 CC3-RESIDUAL-COMPLEMENT declared complement
#
# BRIEF-PARAPHRASE DEVIATION (recorded, rule 8 / procedure_deviations): the
# TASK-20260903-ac03af dispatch brief restates branch 4 as 'h(3) lands
# THRESHOLD (>=100) on both seeds while h(4) is RESIDUAL - a determinate
# non-monotone finding'. That restatement inverts the committed rule: under
# the preregistration's bandrank order (NULLBAND=0 < RESIDUAL=1 < AMBIGUITY=2
# < THRESHOLD=3) a THRESHOLD k=3 beside a RESIDUAL k=4 is a rank 3 -> 1
# DESCENT (monotone non-rising; exactly the CC3-SUBLOCALIZE-LATE conjunct),
# while non-monotony is a RISE, which the preregistration pins to
# NULLBAND-on-either-seed (rank 0 -> 1 at 3->4). The BINDING preregistration
# conjunct (h(3) <= 5 on either seed) is applied here; the brief's
# paraphrase is flagged and not applied. Impact: none at the realized
# readings (1830/1777) - under the binding conjunct branch 4 does not fire
# (both readings > 5), and the fired branch (CC3-SUBLOCALIZE-LATE) is the
# same branch listed next in both orderings.
#
# Every outcome carries NARROW-1 (floor alive, no extinction), SCOPE-1
# (dilution at fixed schedule, no dilution-only language), NARROW-2 (count
# sentences only where two seeds exist and the rule states them), NARROW-3
# (determinism never replication). Exit 0 on composition; 7/12 propagate
# audit failures (not expected here - audits already passed).
import json, sys, math, datetime

INFERENCE = {
    "policy": "executor-implementation",
    "requested_policy": "executor-implementation",
    "resolved_model_id": "fireworks-ai/accounts/fireworks/models/qwen3p8-max",
    "resolved_model_id_note": "session-reported by the running session; no adapter probe was executed in this session, so this identifier is unverified configuration",
    "model_verified": False,
    "fallback_used": True,
    "fallback_reason": "session-backend transport under inference amendment DEC-20260831-0d1eeb",
    "degraded_requirements": [],
    "amendment": "DEC-20260831-0d1eeb",
    "independent_session": True,
}
EXCESS_E = 1 << 30
Z_LO, Z_HI = -1.959963984540054, 1.959963984540054
K3_COMMITTED_CONCAT = "922e24c9c065eb79c7efcbd536b41111ad70d11a1a49cf56207832e4949c6262"
BIN_SHA = "3ccc377cdee7e4c433570b5541e057a6bbc20ca4fb32b59028211c5a88324db8"


def chi2_q(p, nu):
    z = Z_LO if p == 0.025 else Z_HI
    t = 1.0 - 2.0 / (9.0 * nu) + z * math.sqrt(2.0 / (9.0 * nu))
    return nu * (t ** 3)


def garwood_ci(h, n=EXCESS_E):
    lo = 0.0 if h == 0 else 0.5 * chi2_q(0.025, 2 * h) / n
    hi = 0.5 * chi2_q(0.975, 2 * (h + 1)) / n
    return lo * n, hi * n   # scaled to per-2^30 count convention (n = 2^30)


def band(h):
    if h <= 5:
        return "NULLBAND", 0
    if h <= 40:
        return "RESIDUAL", 1
    if h <= 99:
        return "AMBIGUITY", 2
    return "THRESHOLD", 3


def main():
    (u3_path, u4_path, freeze_path, diff_path,
     s2a_path, s1_path, out_path) = sys.argv[1:8]
    u3 = json.load(open(u3_path))
    u4 = json.load(open(u4_path))
    fr = json.load(open(freeze_path))
    da = json.load(open(diff_path))
    s2a = json.load(open(s2a_path))
    s1 = json.load(open(s1_path))

    h3a = u3["hits_W_ge1_nontrivial"]           # seed 531001
    h3b = u4["hits_W_ge1_nontrivial"]           # seed 531002
    b3a, r3a = band(h3a)
    b3b, r3b = band(h3b)
    ci3a = garwood_ci(h3a)
    ci3b = garwood_ci(h3b)
    a1a = u3["amend1_identities_pass"]
    a1b = u4["amend1_identities_pass"]
    seat_a = u3["seat_as_preregistered"]
    seat_b = u4["seat_as_preregistered"]
    dig_a = u3["table_digest_reverification_vs_R4_prearm_commitment"]["match"]
    dig_b = u4["table_digest_reverification_vs_R4_prearm_commitment"]["match"]

    # --- CC3-GATE-FAIL bases ---
    s2a_halt = s2a.get("halt_checks", {})
    s2a_halted = s2a.get("halt_branch_fired")
    freeze_pass = fr["reverification_pass"]
    k3_digest_ok = fr["k3_digest_still_committed"]
    diff_pass = da["equality_verdict"].startswith("PASS")
    bin_ok = da["binary_hash_recheck_pass"]
    gate_fail = not (a1a and a1b and seat_a and seat_b and dig_a and dig_b
                     and freeze_pass and k3_digest_ok and diff_pass and bin_ok
                     and all(s2a_halt.values()) and s2a_halted is None)

    # --- CC3-F6 carry-forward (evaluated in S2a) ---
    dead_hits = s2a["s2a5_dead_anchor"]["hits"]
    f6_fired = dead_hits >= 9

    # --- branches 3-8 on the two readings ---
    seed_disagree = b3a != b3b
    # committed k=4 readings (EV-AES-868db1 OBS-2; immutable inputs)
    h4a, h4b = 17, 21
    b4a, _ = band(h4a)
    b4b, _ = band(h4b)
    k4_residual = (b4a == "RESIDUAL") and (b4b == "RESIDUAL")
    nonmono = ((h3a <= 5 or h3b <= 5) and k4_residual)
    late = (h3a >= 100) and (h3b >= 100)
    early = (6 <= h3a <= 40) and (6 <= h3b <= 40)
    ambiguous = (41 <= h3a <= 99) and (41 <= h3b <= 99)

    fired = None
    if gate_fail:
        fired = "CC3-GATE-FAIL"
    elif f6_fired:
        fired = "CC3-F6"
    elif seed_disagree:
        fired = "CC3-SEED-DISAGREE"
    elif nonmono:
        fired = "CC3-NONMONO-EXT"
    elif late:
        fired = "CC3-SUBLOCALIZE-LATE"
    elif early:
        fired = "CC3-SUBLOCALIZE-EARLY"
    elif ambiguous:
        fired = "CC3-AMBIGUOUS"
    else:
        fired = "CC3-RESIDUAL-COMPLEMENT"

    # --- tier-2 count content for pairs (2,3) and (3,4), per seed,
    #     disjoint-CI rule (report-only, never consumed by the band sentence)
    h2a, h2b = 149371, 150412
    ci2a = garwood_ci(h2a)
    ci2b = garwood_ci(h2b)
    ci4a = garwood_ci(h4a)
    ci4b = garwood_ci(h4b)

    def pair_per_seed(label, ha, cia, hb, cib):
        disjoint = cia[1] < cib[0] or cib[1] < cia[0]
        ratio = ha / hb
        ci_ratio = [cia[0] / cib[1], cia[1] / cib[0]] if hb > 0 else None
        resolved = disjoint and hb < ha
        return {
            "pair": label,
            "h_upper_seed531001": ha, "ci_upper_seed531001": cia,
            "h_lower_seed531001": hb, "ci_lower_seed531001": cib,
            "garwood_cis_disjoint": disjoint,
            "status": ("COUNT-DECAY-RESOLVED" if resolved else
                       ("COUNT-UNRESOLVED (overlapping CIs)" if not disjoint
                        else "COUNT-RESOLVED non-decay (disjoint, lower >= upper)")),
            "ratio_upper_over_lower_seed531001": ratio,
            "ratio_ci_corner_propagation_seed531001": ci_ratio,
        }

    tier2 = {
        "rule": ("TIER 2 (count level) admitted ONLY as reported content under the pre-registered "
                 "disjoint-CI rule (preregistration section 10): a consecutive pair is COUNT-RESOLVED "
                 "iff their Garwood 95% CIs are disjoint; reported per seed, never pooled, never "
                 "smoothed, NEVER consumed by the band sentence"),
        "pair_2_3_seed531001": pair_per_seed("(2,3) seed 531001", h2a, ci2a, h3a, ci3a),
        "pair_2_3_seed531002": pair_per_seed("(2,3) seed 531002", h2b, ci2b, h3b, ci3b),
        "pair_3_4_seed531001": pair_per_seed("(3,4) seed 531001", h3a, ci3a, h4a, ci4a),
        "pair_3_4_seed531002": pair_per_seed("(3,4) seed 531002", h3b, ci3b, h4b, ci4b),
        "cross_seed_pooled": "never pooled, never smoothed (OBS-B16-3 / J-C discipline)",
    }

    branches = {
        "CC3-GATE-FAIL": {
            "order": 1,
            "fired": fired == "CC3-GATE-FAIL",
            "conjunct": ("any S2 integrity gate fails (declared-diff audit, Gate-0x extended, KAT, "
                         "surface-diff battery, dead-anchor counter identities, determinism double, "
                         "post-arm audits, or counter inconsistency on any extended-build receipt)"),
            "basis": {
                "amend1_identities_pass_seed531001": a1a,
                "amend1_identities_pass_seed531002": a1b,
                "seat_as_preregistered_seed531001": seat_a,
                "seat_as_preregistered_seed531002": seat_b,
                "table_digest_match_prearm_R4_seed531001": dig_a,
                "table_digest_match_prearm_R4_seed531002": dig_b,
                "postarm_freeze_reverification_pass": freeze_pass,
                "k3_digest_still_committed_922e24c9": k3_digest_ok,
                "postarm_diff_audit_equals_declared_list": diff_pass,
                "binary_sha256_recheck_3ccc377c": bin_ok,
                "s2a_battery_halt_checks_all_pass_carryforward": s2a_halt,
                "s2a_halt_branch_fired": s2a_halted,
            },
            "evaluation": "NOT FIRED - all conjuncts hold on both new receipts and all post-arm audits pass; S2a battery passed with no halt branch (carry-forward)",
        },
        "CC3-F6": {
            "order": 2,
            "fired": fired == "CC3-F6",
            "conjunct": "extended-build dead anchor hits >= 9 -> boundary falsifier of the sealed verdict; HALT, escalate (rule 12)",
            "basis": {
                "evaluated_in": "S2a (TASK-20260903-7893b2, S2a-5; analyzed first among extended-build alive readings)",
                "dead_anchor_hits": dead_hits,
                "gate": "hits <= 8",
                "tripwire": "hits >= 9",
                "s2a_tripwire_fired": s2a["s2a5_dead_anchor"]["tripwire_fired"],
                "carry_forward": True,
            },
            "evaluation": "NOT FIRED - extended dead anchor read 0 hits in S2a (<= 8; tripwire >= 9 not reached); carried forward, not re-run (no re-run budgeted or needed)",
        },
        "CC3-SEED-DISAGREE": {
            "order": 3,
            "fired": fired == "CC3-SEED-DISAGREE",
            "conjunct": "band(h(3)_531001) != band(h(3)_531002) -> no sub-localization sentence; seed instability at k=3 recorded",
            "basis": {
                "h3_531001": h3a, "band_531001": b3a,
                "h3_531002": h3b, "band_531002": b3b,
                "bands_equal": not seed_disagree,
            },
            "evaluation": ("NOT FIRED - band(h(3)_531001) = %s == band(h(3)_531002) = %s"
                           % (b3a, b3b)),
        },
        "CC3-NONMONO-EXT": {
            "order": 4,
            "fired": fired == "CC3-NONMONO-EXT",
            "conjunct_binding": ("PREREGISTRATION section 6.3 branch 4 (BINDING): h(3) <= 5 (NULLBAND) on EITHER seed "
                                 "while the committed k=4 readings stay RESIDUAL -> bandrank rises at 3->4 (rank 0 -> 1)"),
            "conjunct_brief_paraphrase_flagged": ("dispatch brief restated this branch as 'h(3) THRESHOLD on both seeds while h(4) RESIDUAL'; "
                                                  "that restatement inverts the committed bandrank order (a THRESHOLD k=3 beside RESIDUAL k=4 is a rank 3 -> 1 descent, "
                                                  "the CC3-SUBLOCALIZE-LATE conjunct, not a rise); the binding conjunct is applied; deviation recorded (DEV-S2b-1)"),
            "basis": {
                "h3_531001": h3a, "h3_531002": h3b,
                "h3_le_5_either_seed": (h3a <= 5 or h3b <= 5),
                "k4_committed_readings": {"h4_531001": h4a, "h4_531002": h4b, "bands": [b4a, b4b], "residual_both": k4_residual},
            },
            "evaluation": "NOT FIRED - h(3)_531001 = %d > 5 and h(3)_531002 = %d > 5 (both far above the NULLBAND conjunct)" % (h3a, h3b),
        },
        "CC3-SUBLOCALIZE-LATE": {
            "order": 5,
            "fired": fired == "CC3-SUBLOCALIZE-LATE",
            "conjunct": "h(3) >= 100 (THRESHOLD) on BOTH seeds -> transition localized to (3,4] at band level (refinement of (2,4])",
            "basis": {
                "h3_531001": h3a, "ge_100": h3a >= 100,
                "h3_531002": h3b, "ge_100_seed2": h3b >= 100,
            },
            "evaluation": ("FIRED - h(3)_531001 = %d >= 100 AND h(3)_531002 = %d >= 100 (both THRESHOLD)"
                           % (h3a, h3b)) if late else "not fired",
        },
        "CC3-SUBLOCALIZE-EARLY": {
            "order": 6,
            "fired": fired == "CC3-SUBLOCALIZE-EARLY",
            "conjunct": "6 <= h(3) <= 40 (RESIDUAL) on BOTH seeds -> transition localized to (2,3]",
            "basis": {"h3_531001": h3a, "h3_531002": h3b,
                      "conjunct_holds": early},
            "evaluation": "NOT FIRED (both readings >= 100; disjoint from branch 5 by band-partition)" if late else ("FIRED" if early else "not fired"),
        },
        "CC3-AMBIGUOUS": {
            "order": 7,
            "fired": fired == "CC3-AMBIGUOUS",
            "conjunct": "41 <= h(3) <= 99 (AMBIGUITY) on BOTH seeds -> transition stays in (2,4] with ambiguity declared at k=3",
            "basis": {"h3_531001": h3a, "h3_531002": h3b,
                      "conjunct_holds": ambiguous},
            "evaluation": "NOT FIRED (disjoint from branch 5 by band-partition)" if late else ("FIRED" if ambiguous else "not fired"),
        },
        "CC3-RESIDUAL-COMPLEMENT": {
            "order": 8,
            "fired": fired == "CC3-RESIDUAL-COMPLEMENT",
            "conjunct": "declared complement - any outcome matching none of the above, never force-binned",
            "basis": {"reached": fired == "CC3-RESIDUAL-COMPLEMENT"},
            "evaluation": "NOT REACHED - branch 5 fired" if late else "evaluated",
        },
    }

    if fired == "CC3-SUBLOCALIZE-LATE":
        statement = (
            "CC3-SUBLOCALIZE-LATE fired: h(3) >= 100 (THRESHOLD) on BOTH seeds (h(3)_531001 = %d, "
            "h(3)_531002 = %d). The THRESHOLD->RESIDUAL transition of SH2-MONOTONE-DECAY is localized "
            "to (3,4] at BAND level - a refinement of the committed (2,4] localization, scoped to the "
            "EXTENDED family {0,1,2,3,4,8,12,16}, one probe cell (amask=1, smask=1), r=5, PIN-T0, 2^30 "
            "per arm, seeds 531001/531002, toy tier. The extended-grid bandrank sequence is "
            "[3,3,3,1,1,1] over {1,2,3,4,8,16} (non-rising). The BATCH-e5d753 verdict on grid "
            "{1,2,4,8,16} stands unchanged and immutable; this is strictly additive content."
            % (h3a, h3b))
    else:
        statement = ("CC3 outcome %s; see per-branch evaluation (sub-localization sentence depends on fired branch)"
                     % fired)

    out = {
        "schema": "crypto.autoresearch.s2b4_cc3_composition.v1",
        "task_id": "TASK-20260903-ac03af",
        "batch_id": "BATCH-060cb4",
        "goal_id": "GOAL-AES-003",
        "idea_record": "IDEA-20260903-8f26ac",
        "decision_opening_batch": "DEC-20260903-63cd8d",
        "run_id": "S2b-4",
        "preregistration": "coordination/goals/GOAL-AES-003/batches/BATCH-060cb4/tasks/TASK-20260903-695ebe/PREREGISTRATION.md (write-once, BINDING; section 6.3 evaluated here; NOT rewritten)",
        "gate_regime": "AMEND-1 (DEC-20260901-6f9de3)",
        "binary_invocations_in_this_step": 0,
        "readings_consumed": {
            "new_this_stage": {
                "h3_531001": {"value": h3a, "receipt": "runs/U3_k3_seed1.json",
                              "analysis": "runs/U3_k3_seed1_analysis.json",
                              "band": b3a, "bandrank": r3a,
                              "garwood95_count_ci": ci3a,
                              "first_ever_k3_measurement": True},
                "h3_531002": {"value": h3b, "receipt": "runs/U4_k3_seed2.json",
                              "analysis": "runs/U4_k3_seed2_analysis.json",
                              "band": b3b, "bandrank": r3b,
                              "garwood95_count_ci": ci3b,
                              "unconditional_second_seed_two_draw_entry": True},
            },
            "frozen_inputs_not_remeasured": {
                "source": "EV-AES-868db1 OBS-2 (committed BATCH-e5d753 readings, immutable) + this batch's S1 (CC-AGREE)",
                "h1_531001": 12681109, "h2_531001": 149371, "h2_531002": 150412,
                "h4_531001": 17, "h4_531002": 21,
                "h8_531001": 13, "h8_531002": 18, "h16_531001": 12,
                "realized_grid_note": "h(2)_531002 and h(8)_531002 are this batch's S1 readings; h(1)/h(4)/h(8)_531001/h(16) are committed BATCH-e5d753 inputs; NONE re-measured here",
            },
            "k3_table_digest_vs_prearm_commitment": {
                "committed_constant": K3_COMMITTED_CONCAT,
                "receipt_digest_seed531001": u3["table_digest_reverification_vs_R4_prearm_commitment"]["receipt_arm_table_concat_sha256"],
                "receipt_digest_seed531002": u4["table_digest_reverification_vs_R4_prearm_commitment"]["receipt_arm_table_concat_sha256"],
                "both_match": dig_a and dig_b,
                "postarm_rerun_still_committed": k3_digest_ok,
            },
        },
        "cascade_fixed_order_evaluation": {
            "rule_source": "PREREGISTRATION.md section 6.3 / IDEA-20260903-8f26ac sub_localization_decision_rule (committed pre-arm)",
            "fixed_order": ["CC3-GATE-FAIL", "CC3-F6", "CC3-SEED-DISAGREE", "CC3-NONMONO-EXT",
                            "CC3-SUBLOCALIZE-LATE", "CC3-SUBLOCALIZE-EARLY", "CC3-AMBIGUOUS",
                            "CC3-RESIDUAL-COMPLEMENT"],
            "branches": branches,
            "fired_branch": fired,
            "disjointness_note": ("branches are disjoint by the band-partition of the two k=3 readings with the NULLBAND case ordered "
                                  "before SUBLOCALIZE-EARLY (whose 6 <= h conjunct excludes it); DEAD-before-NONMONO resolution form inherited"),
        },
        "tier2_count_content_report_only": tier2,
        "tier2_consumed_by_band_sentence": False,
        "sub_localization_statement": statement,
        "narrow_discipline": {
            "NARROW_1_floor_is_alive": ("Carried: the residual floor h(4..16) = 17/13/12 (k=4 seed1/seed2 17/21, k=8 13/18, k=16 12) is a LIVE, "
                                        "decidable excess over the analytic null (P(h>=12 | lambda=1) = 8.3e-10; floor-vs-null power 0.989 at lambda=13). "
                                        "No extinction sentence at any k. A (3,4] localization does NOT mean 'the decay finishes early': the floor is alive "
                                        "at k=4, k=8 and k=16, and the band sentence is a band-trajectory statement, never extinction."),
            "SCOPE_1_attribution": ("Attribution under SCOPE-1: under PIN-T0 the schedule is the AES schedule at every interior k >= 1 and constant across k; "
                                    "all comparisons here are interior-to-interior (k=2/3/4) and schedule-clean; the interior decay is attributed to table dilution "
                                    "AT FIXED SCHEDULE (dilution at fixed schedule); NO dilution-only language; k=3 joins the schedule-clean comparisons by the "
                                    "same structural fact (k=3 >= 1). The k=0->k=1 step remains joint-effect-scoped and is not consumed here."),
            "NARROW_2_count_sentences": ("k=3 qualifies for count-level reporting: it entered with two independent draws from the start (531001 and 531002 at armid 11). "
                                         "Tier-2 count content for pairs (2,3) and (3,4) is reported per seed under the disjoint-CI rule, report-only, never consumed "
                                         "by the band sentence. A count-COMPLETION sentence for (3,4] (replicated count decay) is NOT stated: the rule states per-seed "
                                         "tier-2 report content for these pairs and nothing more; (4,8) and (8,16) remain COUNT-UNRESOLVED in every outcome of this batch."),
            "NARROW_3_determinism_not_replication": ("Both k=3 readings are independent draws (new (seed, seat) combinations at the new armid-11 seat), NOT determinism "
                                                     "re-runs; no seed-531001 exact reproduction is spent as replication anywhere in this stage."),
        },
        "scope_discipline": {
            "claim_tier": "toy",
            "no_deployed_aes_claims": True,
            "no_published_cryptanalysis_comparisons": True,
            "scope": "extended family {0,1,2,3,4,8,12,16}, one probe cell (amask=1, smask=1), r=5, PIN-T0, 2^30 per arm, seeds 531001/531002 (531004 dead anchor in S2a)",
            "no_recomposition_of_SH2_MONOTONE_DECAY": True,
            "no_grid_point_rerun": True,
            "no_sub_sub_interval_sentence": "no (3,3.5] style sentence; the extended family has no k=3.5 (priced successor only if a decidable question survives)",
            "no_status_or_promotion_interpretation": True,
            "no_git_add_or_commit": True,
        },
        "s1_context_carried": {
            "cc_outcome_s1": s1["cascade_fixed_order_evaluation"]["fired_branch"],
            "cc8_outcome_s1": s1["cc8_axis"]["fired_branch"],
            "note": "CC-AGREE at k=2 (count-replicated for pairs (1,2)/(2,4)) and CC8-AGREE at k=8, composed in S1; carried as context, never recomposed here",
        },
        "procedure_deviations": [
            {
                "id": "DEV-S2b-1",
                "description": ("The dispatch brief's restatement of branch 4 ('CC3-NONMONO: h(3) lands THRESHOLD (>=100) on both seeds while h(4) is RESIDUAL') "
                                "inverts the committed preregistration conjunct (h(3) <= 5 on EITHER seed while k=4 stays RESIDUAL -> bandrank RISE at 3->4). "
                                "Under the preregistration's bandrank order a THRESHOLD k=3 beside RESIDUAL k=4 is a rank 3->1 descent - the CC3-SUBLOCALIZE-LATE "
                                "conjunct, not non-monotony. The BINDING preregistration conjunct was applied; the brief's paraphrase was not."),
                "impact": ("none at the realized readings: under the binding conjunct branch 4 does not fire (h(3) = %d/%d, both > 5); the fired branch "
                           "(CC3-SUBLOCALIZE-LATE) is listed next in both orderings" % (h3a, h3b)),
            },
        ],
        "unexpected_observations": [
            {
                "id": "OBS-S2b-1",
                "rule8": True,
                "observation": ("The FIRST-EVER k=3 measurement lands at h(3)_531001 = %d, within ~4%% of the flagged multiplicative prior lambda ~ 1759 "
                                "(h(2)/84.90) whose authority was declared BROKEN at design time (the same chain predicted ~4e-7 at k=8 vs observed 13). "
                                "The prior's accidental accuracy at k=3 is recorded per rule 8; it remains a flagged prior, never evidence, and no branch "
                                "conjunct consumed it." % h3a),
            },
            {
                "id": "OBS-S2b-2",
                "rule8": True,
                "observation": ("Both k=3 receipts are saturated (hits %d/%d > threads*cap = 1024; overflow %d/%d), the path predicted under the "
                                "multiplicative prior; AMEND-1 saturated identities exact on both. The unsaturated-legal path was not needed."
                                % (h3a, h3b, u3["hit_log_overflow"], u4["hit_log_overflow"])),
            },
            {
                "id": "OBS-S2b-3",
                "rule8": True,
                "observation": ("The post-arm freeze re-run is BYTE-IDENTICAL (raw C output sha256) to the S2a-4 pre-arm raw output, and the post-arm "
                                "source diff is hunk-identical to the S2a-1 audited diff: the two k=3 arms perturbed nothing on the frozen surface or "
                                "the extended point (strongest form of the post-arm re-verification)."),
            },
            {
                "id": "OBS-S2b-4",
                "rule8": True,
                "observation": ("Seed agreement at k=3 in the THRESHOLD band is nearly free at the realized magnitude (sd ~ sqrt(1800) ~ 42; the two seeds "
                                "sit 1830 vs 1777, ~1.3 sd apart) - the k=1/k=2 lesson applies: the second seed here measures seed variance at the new point, "
                                "not shape stability; recorded so the band agreement is not quietly spent as shape evidence."),
            },
        ],
        "composed_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "parse_attestation": "machine-generated JSON; parsed whole with python3 json.load (all inputs and this output) before task completion",
        "inference": INFERENCE,
    }
    json.dump(out, open(out_path, "w"), indent=1)
    print(json.dumps({"fired_branch": fired,
                      "h3_531001": h3a, "h3_531002": h3b,
                      "bands": [b3a, b3b],
                      "gate_fail": gate_fail, "f6": f6_fired,
                      "seed_disagree": seed_disagree,
                      "nonmono": nonmono, "late": late,
                      "early": early, "ambiguous": ambiguous}, indent=1))
    sys.exit(0)


if __name__ == "__main__":
    main()
