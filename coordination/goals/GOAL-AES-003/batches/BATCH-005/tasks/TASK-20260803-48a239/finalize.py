#!/usr/bin/env python3
"""TASK-20260803-48a239 -- merge core + extras + narrative into RESULTS.json,
then PARSE the result back and record that the parse happened."""
import hashlib
import json
import os
import subprocess
import sys

import stats_lib as S

D = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(D, "runs")


def j(p):
    return json.load(open(os.path.join(D, p)))


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


core = j("results_core.json")
extras = j("results_extras.json")

# ---- RC-7 verification: does the AES-NI dump match the software probe? ----
ni = j("runs/rc7_aesni_vec.json")
ref = j("runs/independent_reference_check.json")
sw_aes = ref["arms"]["aes"]["per_round"]
rc7 = {"per_round": {}, "all_rounds_match": True}
for r in map(str, range(1, 11)):
    a = ni["enc_by_round"][r]
    b = sw_aes[r]["c_probe"]
    c = sw_aes[r]["python_reference"]
    m = (a == b == c)
    rc7["per_round"][r] = {"aes_ni_BATCH002_path": a,
                           "software_T_table_probe": b,
                           "plain_python_no_T_table_reference": c,
                           "all_three_agree": m}
    rc7["all_rounds_match"] = rc7["all_rounds_match"] and m
rc7["r5_vector"] = ni["enc_by_round"]["5"]
rc7["aes_ni_roundtrip_failures_r1_to_r10"] = ni["roundtrip_failures_r1_to_r10"]

i1 = core["item_1_deconfound"]
T = i1["tests"]
pooled = i1["pooled_by_sbox"]
nblk = len(i1["completed_blocks"])
sd_done = all(r["THIS_TASK_at_2p31"] is not None
              for r in core["item_2_structure_destroyed_raised"]["side_by_side"])

t1p = T["T1_sbox_main_effect"]["p_value"]
t4p = T["T4_BATCH004_R1_vs_R2_contrast_retested"]["p_value_two_sided_exact"]
sign = T["T4_BATCH004_R1_vs_R2_contrast_retested"]["this_task_sign"]
power = extras["power_of_T4_at_this_exposure"]["power"]

survives = (t1p < 0.05) or (t4p < 0.05)

item1_answer = {
    "QUESTION": "Does the S-box-to-S-box difference measured in BATCH-004 survive when key and stream are controlled, or does it vanish into key-to-key variation?",
    "DESIGN_CHOSEN": "BOTH options the card offers at once: a fully crossed 3 S-box x %d seed factorial with the SAME seed set across all three S-boxes." % nblk,
    "WHY_THIS_DESIGN": (
        "In this instrument the seed alone fixes the master key "
        "(key = splitmix(seed ^ 0xA5A5A5A5A5A5A5A5)) and the plaintext/swap stream "
        "(thread_seed = seed ^ armid*C1 ^ (t+1)*C2), and neither draw reads the S-box. "
        "So holding seed and armid fixed and varying only the S-box spec makes the key "
        "and the entire p0/p1 draw sequence IDENTICAL across the three arms of a block: "
        "exact pairing, not merely balance. Running several such blocks then supplies the "
        "key-to-key variance BATCH-004 had no estimate of. Choosing only one of the two "
        "options would have answered only half the question."),
    "PAIRING_VERIFIED_NOT_ASSUMED": i1["design_audit"]["PAIRING_HOLDS"],
    "pairing_evidence": "Within every completed block the three arms report the same key_hex and the same thread_seeds; see item_1_deconfound.design_audit.",
    "ANSWER": (
        "IT DOES NOT SURVIVE. With key and stream held exactly fixed, the S-box main "
        "effect is not detectable (preregistered T1: p = %.3f) and BATCH-004's specific "
        "R1-vs-R2 difference does not replicate (preregistered T4: p = %.3f, and the sign "
        "is REVERSED -- %s here against R2 > R1 in BATCH-004)."
        % (t1p, t4p, sign)) if not survives else (
        "IT SURVIVES: T1 p = %.3f, T4 p = %.3f, sign %s." % (t1p, t4p, sign)),
    "WHAT_A_NULL_MEANS_HERE_stated_in_the_preregistration_before_measuring": (
        "This null STRENGTHENS the S-box-independence reading rather than weakening it. "
        "BATCH-004's apparent S-box effect was key and stream variation (or chance) all "
        "along, not a property of the S-box, so the one piece of evidence that pointed "
        "AWAY from S-box independence has been removed. `EV-AES-c66a80` records the "
        "confound as unresolved and `DEC-20260803-baae70` repeats it as a limitation; "
        "this task resolves it in the direction of independence FOR THE THREE S-BOXES "
        "ACTUALLY DRAWN."),
    "THE_NULL_IS_NOT_MERELY_UNDERPOWERED": (
        "Post-hoc sensitivity, changing no preregistered test: had the BATCH-004 rates "
        "(R1 11.0x, R2 20.5x, ratio 1.86) been the true S-box-specific rates, the "
        "preregistered T4 would have rejected with probability %.3f at alpha = 0.05. "
        "The smallest rate ratio this design detects with 80%% power is about %.2f."
        % (power, extras["power_of_T4_at_this_exposure"]["rate_ratio_detectable_with_80pct_power"])),
    "HONEST_LIMIT_ON_THE_WORD_VANISH": (
        "The 9-cell table is consistent with a SINGLE common Poisson rate (T3 p = %.3f), "
        "and the key main effect is ALSO not significant (T2 p = %.3f). So the correct "
        "statement is that the BATCH-004 difference is NOT ATTRIBUTABLE TO THE S-BOX; "
        "this task cannot positively attribute it to the key either, as opposed to chance. "
        "BATCH-004's p = 0.023 was a single uncorrected contrast among three arms."
        % (T["T3_full_cell_homogeneity"]["p_value"], T["T2_key_main_effect"]["p_value"])),
    "SPREAD_COMPARISON": (
        "Within-S-box, key-to-key counts ranged R1 %d..%d and AES %d..%d across blocks, "
        "a spread as large as anything between S-boxes once exposure is matched; the "
        "per-S-box indices of dispersion are R1 %.2f, AES %.2f, R2 %.3f, i.e. unstable "
        "in both directions at this count level."
        % (extras["within_sbox_key_to_key_heterogeneity"]["R1"]["min"],
           extras["within_sbox_key_to_key_heterogeneity"]["R1"]["max"],
           extras["within_sbox_key_to_key_heterogeneity"]["AES"]["min"],
           extras["within_sbox_key_to_key_heterogeneity"]["AES"]["max"],
           extras["scaled_spread_comparison"]["within_R1"]["index_of_dispersion_var_over_mean"],
           extras["scaled_spread_comparison"]["within_AES"]["index_of_dispersion_var_over_mean"],
           extras["scaled_spread_comparison"]["within_R2"]["index_of_dispersion_var_over_mean"])),
    "ALL_ARMS_STILL_ALIVE": T["T5_per_arm_liveness"]["verdicts"],
    "pooled_excess_factors_this_task": {k: round(v / float(nblk), 3) for k, v in pooled.items()},
    "BATCH_004_excess_factors_for_comparison": {"AES": 13.5, "R1": 11.0, "R2": 20.5},
    "WHAT_THIS_DOES_NOT_LICENSE": [
        "It does NOT revive the retired headline 'nothing this campaign has found is specific to AES'. CORR-20260803-791ca7 scoped that down and this task does not widen it: three drawn S-boxes still bound the preserving fraction only at 0.224 (95% lower, two draws) as recorded in EV-AES-c66a80 OBS-B4-3.",
        "It says nothing about S-boxes not drawn. The red team's RC-8 (27 further draws) remains unrun.",
        "It says nothing about round counts other than r=5, nothing about byte-width mechanisms not measured here, and nothing about full-round or deployed AES.",
        "It is not a claim that key has no effect; T2 is a null at this exposure, not a demonstration of absence.",
    ],
}

item2 = core["item_2_structure_destroyed_raised"]
sd_rows = item2["side_by_side"]
item2_answer = {
    "WHAT_WAS_RAISED": "Structure-destroyed controls re-run at 2^31 (2x BATCH-004's 2^30), reported BESIDE the 2^30 readings and also pooled.",
    "WHY_NOT_2p32": "2^32 per arm is about 620 s per arm by BATCH-004's own calibration; three arms would be about 1860 s and would not fit inside 3600 s alongside ITEM 1, which the card names as the priority. 2^31 was preregistered before measuring, not chosen after seeing a number.",
    "TIGHTER_THAN_BATCH_004": "These arms use seed 531001 / armid 1, the same as main block K1, so each sd arm carries the SAME master key as its K1 main arm and differs from it in amask alone. BATCH-004 used separate seeds 431004-431006 for its sd arms, so key varied there too.",
    "BATCH_004_DEFECT_BEING_REPAIRED": "Y-R2-sd read 4.0x at 2^30 and breached its preregistered <=2.5x band; the producer flagged that as a reason not to lean on these controls, and the validator ruled it an ordinary fluctuation (exact tail 0.0190, look-elsewhere across three sd arms 0.056). My stats_lib independently reproduces both of those numbers (0.018988 and 0.02257 for the R1-vs-R2 contrast) as a cross-check on my own arithmetic.",
    "PREREGISTERED_BAND": "excess <= 2.5x is within band; >= 5x is the P5 falsifier.",
    "PRESTATED_LOOK_ELSEWHERE": "Stated in the preregistration before measuring: under a true null, P(X >= 6 | 2.0) = 0.0166 per arm, so one breach among three arms is a ~4.9% a priori event and would not by itself be surprising.",
}
if sd_done:
    breaches = [r["sbox"] for r in sd_rows if not r["THIS_TASK_at_2p31"]["within_prereg_band_2.5x"]]
    fals = [r["sbox"] for r in sd_rows if r["THIS_TASK_at_2p31"]["exceeds_P5_falsifier_5x"]]
    item2_answer["RESULT"] = {
        "arms_within_band": [r["sbox"] for r in sd_rows if r["THIS_TASK_at_2p31"]["within_prereg_band_2.5x"]],
        "arms_breaching_band": breaches,
        "arms_triggering_P5_falsifier_5x": fals,
        "P4_prediction_all_within_band_held": (len(breaches) == 0),
        "P5_falsifier_fired": (len(fals) > 0),
    }
    item2_answer["READING"] = (
        "At the raised count every structure-destroyed arm is %s the preregistered band, "
        "and the P5 falsifier %s. The BATCH-004 Y-R2-sd breach at 2^30 %s at 2^31."
        % ("inside" if not breaches else "NOT all inside",
           "did not fire" if not fals else "FIRED",
           "did not recur" if "R2" not in breaches else "recurred"))
else:
    item2_answer["RESULT"] = "NOT COMPLETED -- see checks_that_did_not_run"

rc = {
    "order_source": "coordination/goals/GOAL-AES-003/batches/BATCH-004/tasks/TASK-20260803-cc92f0/red_team_report.yaml, RC-1..RC-7 in its stated order, taken after ITEMS 1 and 2 as the card directs.",
    "RC-1": {
        "control": "r=6 yoyo arms under R1 and R2 -- the missing decay control for the S-box arm (OBJ-5).",
        "status": "NOT REACHED BY ME, and already measured elsewhere.",
        "what_it_would_have_settled": "Whether the r=5 random-S-box excess is round-limited, i.e. a yoyo, rather than an arm-level baseline offset in the software probe.",
        "why_not_reached": "BATCH-004 segment 2 measured all three r=6 arms (AES 0.50x, R1 1.00x, R2 0.00x) after its reviewers were dispatched. Those readings are UNREVIEWED and are BATCH-005 rank 1, assigned to another task. Re-running them here at 2^31 would have cost about 1200 s, which the budget could not carry alongside ITEMS 1 and 2. I ran no r=6 arm and I assert nothing about those readings in either direction.",
    },
    "RC-2": {
        "control": "GF(2^8) M0 and M1 arms at r=6 -- the only queued measurement that can falsify the round-split rule at byte width.",
        "status": "NOT REACHED.",
        "what_it_would_have_settled": "Whether the round-split scoping rule holds at byte width rather than in the GF(2^4) analogue, which is the exact gap DEC-20260803-baae70 gives as the reason knowledge promotion is still not warranted.",
        "why_not_reached": "The red team costs it at hours per arm at a 2^32 coset; it cannot fit in a 3600 s budget. It is BATCH-005 rank 2 and is assigned to another task.",
    },
    "RC-3": {
        "control": "AES S-box re-run under arm seeds 431002 and 431003, to separate key and stream variance from S-box variance (OBJ-6).",
        "status": "REACHED AND EXCEEDED -- this is ITEM 1.",
        "how_exceeded": "RC-3 asked for one S-box under two extra seeds. ITEM 1 ran all three S-boxes under three shared seeds in a fully crossed, exactly paired design, which additionally supplies the within-S-box key-to-key variance and a direct re-test of the R1-vs-R2 contrast. Fresh seeds 531001-531003 were used rather than RC-3's 431002/431003 because at 2^30 the 431xxx thread seeds would have reproduced an exact PREFIX of the BATCH-004 trial stream rather than an independent measurement.",
    },
    "RC-4": {
        "control": "Null-object control for the mod-8 statistic: the identical projection and statistic applied to a uniformly random bijection and to a uniformly random function, 400 trials each (OBJ-4).",
        "status": "NOT REACHED.",
        "what_it_would_have_settled": "Whether the mod-8 statistic reads a structure at all under a null object, i.e. whether the OBS-B3-4 / decay-control readings clear an object-first null baseline as docs/inventor-protocol.md requires before belief.",
        "why_not_reached": "It runs on a DIFFERENT instrument (the GF(2^4) nibble SPN in another task directory), not on yoyo_sbox_v2. Standing it up and pinning it is not a seconds-scale act inside this task's write scope even though the red team correctly costs the compute itself at seconds. ITEMS 1 and 2 consumed the budget.",
    },
    "RC-5": {
        "control": "400 trials per decayed nibble cell rather than 40, with the paired McNemar comparison the design already pays for (OBJ-3).",
        "status": "NOT REACHED.",
        "what_it_would_have_settled": "Whether the r=6/r=7 decay cells, which currently rest on 40 trials each and disagreed numerically between the producer's engine (4/9/7) and the validator's (7/3/5), are separated by more than counting noise.",
        "why_not_reached": "Same reason as RC-4: different instrument, and the budget was spent on ITEMS 1 and 2.",
    },
    "RC-6": {
        "control": "Structure-destroyed controls at 2^32, plus the measured-PRP null that was declared and skipped (OBJ-8).",
        "status": "PARTIALLY REACHED -- this is ITEM 2, at 2^31 rather than 2^32, and WITHOUT the measured-PRP null.",
        "what_the_unreached_part_would_have_settled": "The 2^32 half would shrink the sd confidence interval by a further factor of sqrt(2) and make a single-arm band breach a much stronger signal. The measured-PRP null would replace the ANALYTIC null of 4*2^-32 with a MEASURED one, settling whether the null expectation the ALIVE/DEAD rule divides by is itself correct for this probe -- which no arm run in this campaign has ever checked.",
        "why_not_reached": "2^32 per arm is about 620 s; three arms would have displaced ITEM 1, which the card names as the priority.",
    },
    "RC-7": {
        "control": "One 16-byte enc_5 vector compared between the software probe and BATCH-002's AES-NI probe, and one non-T-table reference check of enc_5 under a random S-box (OBJ-9).",
        "status": "REACHED IN FULL, both halves.",
        "result": rc7,
        "half_1": "rc7_aesni_vec.c reproduces BATCH-002's AES-NI code path verbatim (build_sbox, key_expand, sched_init, enc_r copied from probe.c) and its enc_5 vector on key 101112...1f / pt a0a1...af is %s, which agrees with the software T-table probe and with the plain-Python reference on all ten round counts, not just r=5." % rc7["r5_vector"],
        "half_2": "ref_aes.py, the plain-Python no-T-table implementation, matched enc_r for r = 1..10 under BOTH random S-boxes as well as under AES, and independently re-drew both random S-box tables (ANCHOR_PASS = True).",
        "what_it_settles": "The '13.5x reproduction of BATCH-002' rests on the two probes computing the SAME function, not on two similar-looking numbers. It removes the arm-level-implementation-offset explanation from the AES arm specifically.",
    },
    "RC-8": {
        "control": "27 further random bijective S-box draws at r=5 (OBJ-7).",
        "status": "NOT REACHED. Outside RC-1..RC-7 and outside this budget.",
        "what_it_would_have_settled": "It is what a real S-box-independence claim would require: 29 consecutive preserving draws give a 95% lower bound of 0.90 on the preserving fraction, against the 0.224 that two draws give. ITEM 1 removes an objection to S-box independence; it does not supply this.",
        "why_not_reached": "About 75 minutes at 2^30 per arm by the red team's costing, i.e. many times this task's entire budget.",
    },
}

git = j("runs/git_state.json")
env = j("runs/environment.json")
commands = [ln.strip() for ln in open(os.path.join(R, "commands.txt"))] if os.path.exists(os.path.join(R, "commands.txt")) else []
timing_raw = open(os.path.join(R, "timing.txt")).read().splitlines() if os.path.exists(os.path.join(R, "timing.txt")) else []

out = {
    "task_id": core["task_id"],
    "goal_id": core["goal_id"],
    "batch": core["batch"],
    "role": core["role"],
    "task_kind": core["task_kind"],
    "produced_at_utc": subprocess.check_output(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"], text=True).strip(),
    "claim_tier": core["claim_tier"],
    "claim_tier_basis": core["claim_tier_basis"],
    "certificate": core["certificate"],
    "scope_statement": (
        "TOY TIER. Every statement here is about r=5 of a reduced-round AES-128 "
        "permutation measured on one machine at 2^30-2^31 trials under three specific "
        "S-boxes. Nothing here is a statement about full-round or deployed AES, and no "
        "comparison to published cryptanalysis is made in either direction. No "
        "recollection is used to promote or to dismiss anything."),
    "preregistration": {
        "path": "PREREGISTRATION.md",
        "frozen_before_measurement": True,
        "what_ran_before_it": "verification only -- geometry dump, FIPS-197 C.1 pin under my own fresh pin seed 90210, two random-S-box pins, and the plain-Python reference anchor. No measurement arm was launched before the preregistration was written.",
        "sha256": None,
    },
    "instrument_REUSED_NOT_REWRITTEN": {
        "statement": (
            "I REUSED BATCH-004's instrument. I did not rewrite it. Rewriting would have "
            "been the wrong act for a control task whose whole point is to change ONE "
            "factor against a fixed key and stream: a new implementation would have added "
            "a second uncontrolled factor to the very comparison being deconfounded."),
        "binary_executed": "yoyo_sbox_v2 (byte-identical copy of BATCH-004 TASK-20260803-367b1b/yoyo_sbox_v2)",
        "sha256": {},
        "copied_rather_than_run_in_place_because": "ref_aes.py writes its output beside itself; running it in the BATCH-004 directory would have overwritten a prior-batch artifact, which this task is forbidden to do. No prior-batch file was read-modified or written.",
        "verification_I_performed_myself_before_measuring": {
            "geometry": j("runs/geom.json"),
            "geometry_check": "PW is the FORWARD ShiftRows diagonals and CW is the INVERSE ShiftRows diagonals 4*((j-r)%4)+r, giving CW[0] = [0,13,10,7]. This is the geometry the campaign requires; a replication in this campaign once got it wrong and read no signal.",
            "fips197_pin": None,
            "random_sbox_pins": {},
            "independent_reference_anchor": {
                "ANCHOR_PASS": ref["ANCHOR_PASS"],
                "what_it_is": "ref_aes.py, BATCH-004's plain-Python FIPS-197 implementation with no T-tables, no equivalent-inverse-cipher and no shared code path; byte-identical copy, sha256 recorded below.",
                "covers": "enc_r for r = 1..10 under aes, rand:20260803001 and rand:20260803002, plus independent re-drawing of both random S-box tables.",
            },
        },
    },
    "ITEM_1_deconfound_the_yoyo_arms": item1_answer,
    "ITEM_2_structure_destroyed_controls_raised": item2_answer,
    "ITEM_3_red_team_control_set": rc,
    "measurements": {
        "item_1_arms": core["arms"],
        "item_2_sd_arms": core["sd_arms"],
        "item_1_analysis": core["item_1_deconfound"],
        "item_2_side_by_side": core["item_2_structure_destroyed_raised"],
        "supplementary_post_hoc": extras,
    },
    "measured_vs_modeled": {
        "measured": "Every W_ge1 count, every trials count, every key_hex, every thread_seed, every wall_seconds, every enc_r vector, and every pin/anchor outcome.",
        "modeled": "The analytic null expectation trials*4*2^-32, which the binary computes rather than measures. The red team's RC-6 measured-PRP null, which would replace it with a measurement, was NOT run (see ITEM_3.RC-6). Every p-value, G^2, excess factor, index of dispersion and power figure is DERIVED from measured counts by stats_lib.py, not measured.",
        "optimistic_assumptions_carried": [
            "The null expectation P(W>=1) ~ 4*2^-32 is analytic and unverified by measurement in this campaign; every excess factor and every ALIVE/DEAD verdict divides by it.",
            "splitmix64 is treated as an adequate source for plaintext draws and key draws; no randomness quality test was run here.",
        ],
    },
    "statistics": {
        "library": "stats_lib.py in this directory -- self-contained because neither numpy nor scipy is installed (both raise ModuleNotFoundError; recorded in runs/environment.json).",
        "self_test": S.self_test(),
        "independent_cross_check": "The library reproduces two numbers recorded by others before it existed: BATCH-004's R1-vs-R2 two-sided p = 0.023 (computed 0.022575) and the validator's Y-R2-sd exact tail 0.0190 (computed 0.018988).",
    },
    "reproduction": {
        "git_state": git,
        "origin_main_check": {
            "fetched": True,
            "origin_main_at_fetch": "fdf3a9fba1dcace5b366c61ea9fed87580f0f822",
            "branch_head": git["commit"],
            "branch_behind_origin_main_commits": 172,
            "branch_ahead_commits": 105,
            "action_taken": "NONE. I did not merge and I committed nothing; this task directory is gitignored on purpose and syncing the branch with main is the Coordinator's act, not the Executor's. Recorded here so the Coordinator has the base commit that was checked.",
        },
        "environment": env,
        "exact_commands": commands,
        "timing_log_verbatim": timing_raw,
        "seeds": {
            "sbox_draw_seeds": {"AES": "not seeded -- algebraic S-box", "R1": 20260803001, "R2": 20260803002},
            "arm_seeds_item1": {"K1": 531001, "K2": 531002, "K3": 531003, "K4": "531004 -- NOT RUN"},
            "arm_seeds_item2": {"SD31-AES/R1/R2": 531001},
            "armids": {"K1": 1, "K2": 2, "K3": 3, "SD31": 1},
            "pin_seed": 90210,
            "randomness_sources": "splitmix64 only, inside the binary; the master key, the plaintext draws, the re-randomisation draws and the S-box Fisher-Yates shuffle all consume it. Thread seeds are printed per arm and recorded above, so every arm is exactly reproducible.",
        },
        "how_to_reproduce": "From this directory: ./run_item1.sh then ./run_item2.sh, then python3 build_results.py && python3 extras.py && python3 finalize.py. The binary is not rebuilt; it is the recorded sha256.",
    },
    "checks_that_did_not_run": [
        {"check": "ITEM 1 block K4 (seeds 531004, three arms at 2^30)",
         "reason": "budget -- ITEM 2 was still running at 03:42 and a fourth block costs about 465 s, which would not leave time to write and parse this artifact before the binding stop at 03:57:59Z. It was preregistered as contingent, and blocks were ordered so that a halt leaves the design BALANCED, which it does at 3 blocks.",
         "what_it_would_have_added": "a fourth key per S-box, tightening T2 and lowering the 80%-power detectable rate ratio below its current ~1.73."},
        {"check": "Structure-destroyed controls at 2^32 (the red team's RC-6 as literally stated)",
         "reason": "budget; 2^31 was preregistered instead and ITEM 1 was the stated priority.",
         "what_it_would_have_added": "a further sqrt(2) tightening of the sd interval."},
        {"check": "The measured-PRP null (declared and skipped in BATCH-004, RC-6 second half)",
         "reason": "budget.",
         "what_it_would_have_added": "a MEASURED null to replace the analytic 4*2^-32 that every excess factor in this campaign divides by."},
        {"check": "RC-1 r=6 yoyo arms under R1 and R2",
         "reason": "already measured in BATCH-004 segment 2 and assigned to BATCH-005 rank 1 for review; re-running at 2^31 costs about 1200 s.",
         "what_it_would_have_added": "an independent replication of the decay control for the random-S-box arms."},
        {"check": "RC-2 GF(2^8) M0/M1 at r=6", "reason": "hours of compute; assigned to another BATCH-005 task.",
         "what_it_would_have_added": "the byte-width falsification of the round-split rule that DEC-20260803-baae70 names as the reason knowledge promotion is not warranted."},
        {"check": "RC-4 null-object control for the mod-8 statistic", "reason": "different instrument, and budget.",
         "what_it_would_have_added": "an object-first null baseline for the decay statistic."},
        {"check": "RC-5 400 trials per decayed nibble cell", "reason": "different instrument, and budget.",
         "what_it_would_have_added": "separation of the r=6/r=7 decay cells from counting noise."},
        {"check": "RC-8 27 further random S-box draws", "reason": "about 75 minutes per arm; far outside this budget.",
         "what_it_would_have_added": "a real S-box-independence claim (95% lower bound 0.90) rather than removal of an objection."},
        {"check": "Adapter probe of the resolved inference model",
         "reason": "no adapter exists in this harness; Claude Code cannot resolve the GPT-5.6-family policy aliases in orchestration/model-policies.yaml.",
         "what_it_would_have_added": "model_verified: true instead of false."},
        {"check": "Independent randomness-quality test of splitmix64 as used here",
         "reason": "not in scope and not budgeted.",
         "what_it_would_have_added": "assurance that the paired design's identical streams are also well-distributed streams."},
    ],
    "protocol_deviations": [
        {"deviation": "The binary and ref_aes.py were COPIED into this task directory before execution rather than executed in place.",
         "why": "ref_aes.py writes runs/independent_reference_check.json beside itself; executing it in BATCH-004's directory would have overwritten a prior-batch artifact, which the card forbids. sha256 of both copies is recorded and matches the originals byte for byte.",
         "effect_on_results": "none -- identical bytes, identical binary."},
        {"deviation": "ITEM 2 used 2^31 rather than the red team's stated 2^32 for RC-6.",
         "why": "budget; ITEM 1 is the card's stated priority. The choice was preregistered before measuring.",
         "effect_on_results": "the sd interval is sqrt(2) wider than RC-6 asked for; stated beside every sd number."},
        {"deviation": "ITEM 1 used fresh seeds 531001-531003 rather than RC-3's 431002/431003.",
         "why": "at 2^30 the 431xxx thread seeds would have replayed an exact PREFIX of the BATCH-004 trial stream, since thread_seed depends only on seed, armid and thread index. That would have been a subsample of an existing run, not an independent measurement.",
         "effect_on_results": "makes the arms independent of BATCH-004's; this is the intended effect."},
        {"deviation": "ITEM 2's sd arms share seed 531001/armid 1 with main block K1.",
         "why": "deliberate -- it makes each sd arm carry the same master key as its K1 main arm so that amask is the only difference. BATCH-004 varied the key there too.",
         "effect_on_results": "the sd arms' p0 sequences diverge from K1's after the first trial anyway, because a 4-word re-randomisation consumes the stream differently from a 1-word one; the key does not diverge. The sd arms are therefore not statistically independent of K1 in their first draws, which is noted rather than hidden."},
        {"deviation": "Post-hoc power and dispersion statistics were computed (extras.py).",
         "why": "to make the preregistered null interpretable rather than merely absent.",
         "effect_on_results": "none on any preregistered test; labelled post_hoc in the artifact and no completed run was re-scored."},
    ],
    "unexpected_observations": [
        "The T4 sign REVERSED relative to BATCH-004: R1 pooled %d against R2 pooled %d here, where BATCH-004 read R1 22 against R2 41. A reversal is stronger evidence against an S-box explanation than a mere attenuation would be, and it is recorded as observed rather than interpreted further." % (pooled["R1"], pooled["R2"]),
        "The three S-boxes' per-arm dispersion indices are wildly unequal (R2 0.023, AES 1.00, R1 2.06) on three points each. With 3 observations per cell this is what Poisson noise looks like, and no weight is placed on it; it is recorded because it was not expected.",
        "The exact pairing held perfectly: identical key_hex AND identical thread_seeds across the three S-boxes in every block, so the design audit passed rather than merely being asserted.",
    ],
    "budget": {
        "declared_wall_clock_seconds": 3600,
        "start_utc": "2026-08-03T02:57:59Z",
        "binding_stop_utc": "2026-08-03T03:57:59Z",
        "memory_gb_limit": 8,
        "max_threads_used": 2,
        "concurrency_note": "one other producer runs concurrently; every arm used exactly 2 threads and arms were serialised, never overlapped.",
        "maximum_runs_allowed": 24,
        "measurement_arms_run": 12,
        "verification_invocations": 8,
        "halted_on_budget": None,
        "dropped_work_named": ["ITEM 1 block K4", "RC-6 at 2^32", "RC-6 measured-PRP null", "RC-1", "RC-2", "RC-4", "RC-5", "RC-8"],
        "stamps": "budget_stamps.jsonl in this directory",
    },
    "artifact_paths": [
        "coordination/goals/GOAL-AES-003/batches/BATCH-005/tasks/TASK-20260803-48a239/RESULTS.json",
        "coordination/goals/GOAL-AES-003/batches/BATCH-005/tasks/TASK-20260803-48a239/PREREGISTRATION.md",
        "coordination/goals/GOAL-AES-003/batches/BATCH-005/tasks/TASK-20260803-48a239/budget_stamps.jsonl",
    ],
    "inference": {
        "policy": "executor-implementation",
        "requested_policy": "executor-implementation",
        "resolved_model": "claude-opus-5",
        "fallback_used": True,
        "fallback_reason": "orchestration/model-policies.yaml routes this role to a GPT-5.6-family policy alias that Claude Code cannot resolve; subagent frontmatter supports only Claude models.",
        "model_verified": False,
        "model_verified_reason": "no adapter probe available in this harness",
        "standing_basis": "0137a051eb5828789eb267fa83c8278086578d4c",
    },
}

# fill verification detail
pa = j("runs/pin_aes.json")
out["instrument_REUSED_NOT_REWRITTEN"]["verification_I_performed_myself_before_measuring"]["fips197_pin"] = {
    k: v for k, v in pa.items() if k != "sbox"}
for s in ("20260803001", "20260803002"):
    p = j("runs/pin_rand_%s.json" % s)
    out["instrument_REUSED_NOT_REWRITTEN"]["verification_I_performed_myself_before_measuring"]["random_sbox_pins"][s] = {
        k: v for k, v in p.items() if k != "sbox"}
for f in ("yoyo_sbox_v2", "ref_aes.py", "rc7_aesni_vec.c", "stats_lib.py",
          "build_results.py", "extras.py", "finalize.py", "run_item1.sh",
          "run_item2.sh", "PREREGISTRATION.md"):
    fp = os.path.join(D, f)
    if os.path.exists(fp):
        out["instrument_REUSED_NOT_REWRITTEN"]["sha256"][f] = sha(fp)
out["preregistration"]["sha256"] = out["instrument_REUSED_NOT_REWRITTEN"]["sha256"].get("PREREGISTRATION.md")
out["instrument_REUSED_NOT_REWRITTEN"]["sha256"]["BATCH004_src_yoyo_sbox_v2.c_read_not_rebuilt"] = "6bda2ab7f3c8e6dee358d3fcba52803e4e43f794f963bafabc51cc0de379bc9c"

halted = (sys.argv[1] == "halted") if len(sys.argv) > 1 else False
out["budget"]["halted_on_budget"] = halted
out["budget"]["measurement_arms_run"] = sum(
    1 for a in list(core["arms"].values()) + list(core["sd_arms"].values())
    if a["status"] == "COMPLETED")

p = os.path.join(D, "RESULTS.json")
json.dump(out, open(p, "w"), indent=1)

# ---- PARSE IT BACK ----
reparsed = json.load(open(p))
ok = isinstance(reparsed, dict) and reparsed["task_id"] == "TASK-20260803-48a239"
reparsed["parser_confirmation"] = {
    "statement": "I ran a parser on this file. RESULTS.json was written, then read back with python3 json.load, and the reparse succeeded; the stanza you are reading was added by that same step and the file was then re-parsed a second time to confirm it still parses with the stanza present.",
    "parser": "python3 %s json.load" % ".".join(map(str, sys.version_info[:3])),
    "first_parse_ok": ok,
    "second_parse_ok": None,
    "also_parsed": ["PREREGISTRATION.md is markdown, not structured", "budget_stamps.jsonl parsed line by line as JSON"],
}
json.dump(reparsed, open(p, "w"), indent=1)
again = json.load(open(p))
again["parser_confirmation"]["second_parse_ok"] = True
json.dump(again, open(p, "w"), indent=1)
final = json.load(open(p))
# jsonl parse check
nl = 0
for ln in open(os.path.join(D, "budget_stamps.jsonl")):
    if ln.strip():
        json.loads(ln)
        nl += 1
print("RESULTS.json parses:", final["task_id"], "| budget_stamps.jsonl lines parsed:", nl)
print("halted_on_budget:", final["budget"]["halted_on_budget"],
      "| arms:", final["budget"]["measurement_arms_run"])
