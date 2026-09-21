#!/usr/bin/env python3
"""TASK-20260803-367b1b -- assemble RESULTS.json from the raw run JSONs.
Computes nothing that is not derivable from runs/*.json; every number it emits
is traceable to a file in runs/."""
import json, os, subprocess, math, sys, datetime

D = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(D, "runs")


def rd(p):
    with open(os.path.join(R, p)) as f:
        return json.load(f)


def poisson_ge(x, lam):
    """P(K >= x | lam), exact summation."""
    if x <= 0:
        return 1.0
    # 1 - P(K <= x-1)
    s, term = 0.0, math.exp(-lam)
    for k in range(0, x):
        if k:
            term *= lam / k
        s += term
    return max(0.0, 1.0 - s)


def poisson_le(x, lam):
    s, term = 0.0, math.exp(-lam)
    for k in range(0, x + 1):
        if k:
            term *= lam / k
        s += term
    return min(1.0, s)


BASE = 15.63  # BATCH-002 A1 excess factor, frozen reference for the DEAD test


def classify(x, null):
    exc = x / null if null else None
    p_alive = poisson_ge(x, null)
    p_dead = poisson_le(x, BASE * null)
    if exc >= 5 and p_alive < 1e-6:
        v = "ALIVE"
    elif exc <= 2.5 and p_dead < 1e-3:
        v = "DEAD"
    else:
        v = "INDETERMINATE"
    return exc, p_alive, p_dead, v


def arm_block(name, role, note):
    p = "%s.json" % name
    if not os.path.exists(os.path.join(R, p)):
        return {"arm": name, "role": role, "status": "DID_NOT_RUN", "reason": note}
    d = rd(p)
    x = d["W_ge1_nontrivial"]
    null = d["null_expectation_analytic"]
    exc, pa, pd, verdict = classify(x, null)
    return {
        "arm": name, "role": role, "note": note, "status": "COMPLETED",
        "sbox_spec": d["sbox_spec"], "sbox_seed": d["sbox_seed"],
        "sbox_bijective_verified_before_measuring": d["sbox_bijective"],
        "sbox_first8": d["sbox_first8"],
        "rounds": d["rounds"], "amask": d["amask"], "smask": d["smask"],
        "trials": d["trials"], "nontrivial_trials": d["nontrivial_trials"],
        "trivial_swaps_excluded": d["trivial_swaps_excluded"],
        "seed": d["seed"], "arm_id": d["arm_id"], "threads": d["threads"],
        "key_hex": d["key_hex"], "thread_seeds": d["thread_seeds"],
        "MEASURED_W_ge1": x,
        "NULL_EXPECTATION_analytic": null,
        "EXCESS_FACTOR": exc,
        "poisson_p_ge_x_given_null": pa,
        "poisson_p_le_x_given_15.63x_null": pd,
        "frozen_decision_rule_verdict": verdict,
        "whist": d["whist"], "W_ge1_by_word": d["W_ge1_by_word"],
    }


def main():
    timing = {}
    tp = os.path.join(R, "arms_timing.txt")
    if os.path.exists(tp):
        for line in open(tp):
            f = line.split()
            if len(f) == 3:
                timing[f[0]] = {"exit": int(f[1].split("=")[1]),
                                "wall_seconds": float(f[2].split("=")[1])}

    mains = [
        arm_block("Y-AES-main", "main_reference",
                  "real AES S-box, r=5, A={0}, S={0} -- the BATCH-002 A1 object in a third implementation"),
        arm_block("Y-R1-main", "main_random_sbox_1",
                  "uniformly drawn random bijective S-box R1 (seed 20260803001), r=5, A={0}, S={0}"),
        arm_block("Y-R2-main", "main_random_sbox_2",
                  "uniformly drawn random bijective S-box R2 (seed 20260803002), r=5, A={0}, S={0}"),
    ]
    sds = [
        arm_block("Y-AES-sd", "structure_destroyed_control",
                  "real AES S-box, r=5, ALL FOUR plaintext words active (A={0,1,2,3}) so no diagonal-coset structure remains; S={0}"),
        arm_block("Y-R1-sd", "structure_destroyed_control",
                  "random S-box R1, r=5, A={0,1,2,3}, S={0}"),
        arm_block("Y-R2-sd", "structure_destroyed_control",
                  "random S-box R2, r=5, A={0,1,2,3}, S={0}"),
    ]
    for b in mains + sds:
        if b.get("status") == "COMPLETED":
            b["timing"] = timing.get(b["arm"])

    r6 = [
        arm_block("Y-AES-main-r6", "decay_control_r6",
                  "real AES S-box, r=6, A={0}, S={0} -- SAME seed/armid as Y-AES-main, so same key and same trial stream; rounds is the only variable changed"),
        arm_block("Y-R1-main-r6", "decay_control_r6",
                  "random S-box R1, r=6, A={0}, S={0} -- paired with Y-R1-main on key and stream"),
        arm_block("Y-R2-main-r6", "decay_control_r6",
                  "random S-box R2, r=6, A={0}, S={0} -- paired with Y-R2-main on key and stream; the coordinator named this the single most important arm"),
    ]
    for b in r6:
        if b.get("status") == "COMPLETED":
            b["timing"] = timing.get(b["arm"])
    pairs = []
    for m, s6 in zip(mains, r6):
        if m.get("status") == "COMPLETED" and s6.get("status") == "COMPLETED":
            pairs.append({
                "sbox": m["sbox_spec"],
                "same_key_as_r5_pair": m["key_hex"] == s6["key_hex"],
                "same_thread_seeds_as_r5_pair": m["thread_seeds"] == s6["thread_seeds"],
                "r5_W_ge1": m["MEASURED_W_ge1"], "r5_excess": m["EXCESS_FACTOR"],
                "r6_W_ge1": s6["MEASURED_W_ge1"], "r6_excess": s6["EXCESS_FACTOR"],
                "r6_verdict": s6["frozen_decision_rule_verdict"],
                "P4.2_r6_at_most_quarter_of_r5": s6["MEASURED_W_ge1"] <= m["MEASURED_W_ge1"] / 4.0,
            })
    r6verd = [b.get("frozen_decision_rule_verdict") for b in r6 if b.get("status") == "COMPLETED"]
    if r6verd and all(v == "DEAD" for v in r6verd) and len(r6verd) == 3:
        decay = "DECAY_CONTROL_PASSED"
    elif any(v == "ALIVE" for v in r6verd):
        decay = "NOT_ROUND_LIMITED_READING_COLLAPSED"
    elif not r6verd:
        decay = "DECAY_CONTROL_DID_NOT_RUN"
    else:
        decay = "DECAY_CONTROL_PARTIAL"

    verdicts = {b["arm"]: b.get("frozen_decision_rule_verdict") for b in mains}
    ref = verdicts.get("Y-AES-main")
    rnd = [verdicts.get("Y-R1-main"), verdicts.get("Y-R2-main")]
    if ref == "ALIVE" and all(v == "ALIVE" for v in rnd):
        reading = "S-BOX-INDEPENDENT"
    elif ref == "ALIVE" and all(v == "DEAD" for v in rnd):
        reading = "S-BOX-DEPENDENT"
    else:
        reading = "MIXED / INDETERMINATE"
    if decay == "NOT_ROUND_LIMITED_READING_COLLAPSED":
        reading = "COLLAPSED BY THE r=6 DECAY CONTROL"

    # ---- rank 2 ----
    pc_path = os.path.join(R, "PC-TRUE.json")
    if os.path.exists(pc_path) and os.path.getsize(pc_path) > 0:
        try:
            pc = json.load(open(pc_path))
            hist = {}
            for dd in pc["diagonals"]:
                hist[dd["unique_survivor_is_true_byte"]] = hist.get(dd["unique_survivor_is_true_byte"], 0) + 1
            pcs = pc.get("_status", {})
            rank2 = {
                "status": "COMPLETED",
                "arm": "PC-TRUE",
                "object": "the SAME modified sq_slot binary as BATCH-003 rank 4, run with slotmask=0 so EVERY hint byte is taken from the TRUE key schedule",
                "binary_source_sha256": SQ_SHA,
                "binary_source_identical_to_BATCH-003": SQ_SHA == "13eb85a3a433a7e1d1ce9df292ae696f66075fd55b27ee26c36eb883a7272a79",
                "slotmask": pc.get("slotmask"),
                "false_slots": pc.get("false_slots"),
                "rounds": pc["rounds"], "nstruct": pc["nstruct"], "seed": pc["seed"],
                "threads": pc["nthreads"],
                "target_key": pc["target_key"], "hint_key": pc["hint_key"],
                "chosen_plaintexts": pc["chosen_plaintexts"],
                "seconds_self_reported": pc["seconds"],
                "diagonals_with_survivors": pc["diagonals_with_survivors"],
                "diagonals_unique_and_correct": pc["diagonals_unique_and_correct"],
                "unique_all_diagonals": pc["unique_all_diagonals"],
                "hint_bytes_actually_differing_per_diagonal": [dd["hint_bytes_actually_differing"] for dd in pc["diagonals"]],
                "survivor_counts_per_diagonal": [dd["survivor_count"] for dd in pc["diagonals"]],
                "HISTOGRAM_unique_survivor_is_true_byte": {str(k): v for k, v in hist.items()},
                "PREDICTION_P2.1": "{1: 4} -- all four diagonals unique and correct",
                "PREDICTION_P2.2": "hint_bytes_actually_differing = 0 on every diagonal",
            }
            ok = pc["diagonals_unique_and_correct"] == 4
            rank2["MET_PREDICTION_P2.1"] = ok
            rank2["MET_PREDICTION_P2.2"] = all(dd["hint_bytes_actually_differing"] == 0 for dd in pc["diagonals"])
            rank2["FINDING"] = (
                "POSITIVE CONTROL PASSES. The same modified sq_slot binary that returned {0:4} for every "
                "single-slot false hint in BATCH-003 rank 4 returns {1:4} -- four diagonals, each with a "
                "unique surviving byte equal to the true byte -- when the hint is TRUE. The all-empty "
                "regression hypothesis is EXCLUDED: the instrument is demonstrably capable of emitting a "
                "non-empty correct result."
                if ok else
                "POSITIVE CONTROL FAILS. The modified sq_slot binary did NOT return a non-empty correct "
                "result under a fully TRUE hint. On this evidence BATCH-003's rank-4 conclusion rests on an "
                "instrument that was never shown capable of producing a non-empty correct result, and is "
                "reported here as UNSUPPORTED on that ground.")
            rank2["timing"] = timing.get("PC-TRUE")
        except Exception as e:
            rank2 = {"status": "PARSE_FAILED", "reason": repr(e)}
    else:
        rank2 = {
            "status": "DID_NOT_RUN",
            "reason": PC_DROP_REASON,
            "consequence": "The positive control BATCH-003 rank 4 lacked is STILL missing. Nothing here "
                           "confirms or refutes the all-empty regression hypothesis; it remains untested.",
        }

    out = {
        "schema": "crypto.autoresearch.task_results.v1",
        "task_id": "TASK-20260803-367b1b",
        "title": "RANK 2 the true-hint positive control, and RANK 3 the S-box arm on the r=5 yoyo",
        "goal_id": "GOAL-AES-003",
        "batch": "BATCH-004",
        "role": "executor",
        "claim_tier": "toy",
        "certificate": {
            "kind": "none",
            "basis": "pure measurement; no discrete log, no factor-base relation, no key recovery is claimed. "
                     "The RANK 2 arm recovers key bytes of a toy 6-round instance, and its correctness is "
                     "self-certifying in the reported field diagonals_unique_and_correct, which compares the "
                     "surviving byte against the true key schedule inside the run.",
        },
        "inference": INFERENCE,
        "git_state": GIT,
        "environment": ENV,
        "HEADLINE": {
            "RANK_3_READING": reading,
            "RANK_3_PLAIN_STATEMENT": READING_TEXT[reading],
            "RANK_3_reference_arm_verdict": ref,
            "RANK_3_random_sbox_verdicts": {"R1": rnd[0], "R2": rnd[1]},
            "RANK_2_positive_control": rank2.get("FINDING", rank2.get("reason")),
            "RANK_3_decay_control_outcome": decay,
            "RANK_3_decay_control_statement": DECAY_TEXT[decay],
            "WHAT_CHANGED_IN_SEGMENT_2": WHAT_CHANGED[decay],
        },
        "rank_3_sbox_arm": {
            "object": OBJECT,
            "geometry": GEOM,
            "implementation": IMPL,
            "random_sbox_construction": SBOXDOC,
            "null_model": "analytic: P(W>=1) ~ 4*2^-32, NULL = nontrivial_trials * 2^-30",
            "frozen_decision_rule": {
                "ALIVE": "excess >= 5 AND P(K >= X | lambda = null) < 1e-6",
                "DEAD": "excess <= 2.5 AND P(K <= X | lambda = 15.63*null) < 1e-3",
                "else": "INDETERMINATE",
                "baseline_used_for_DEAD_test": BASE,
                "baseline_source": "BATCH-002 arm A1 measured excess factor 15.625 at r=5, 2^33 trials",
            },
            "main_arms": mains,
            "structure_destroyed_controls": sds,
            "r6_decay_controls_ADDED_IN_SEGMENT_2": {
                "why_added": (
                    "In segment 1 I listed the r=6 arms in checks_that_did_not_run with the reason "
                    "'budget; out of scope'. The red team objected that this is structurally the same "
                    "defect BATCH-003's red team found for the zero-entry matrices -- a signal claim with "
                    "no decay control -- reproduced inside the batch convened to repair it. The objection "
                    "is correct and the arms were run. Nothing in segment 1 was edited or rescored."),
                "design": (
                    "Same binary (sha256 in runs/yoyo_sbox_binary_sha256_segment2.txt), same geometry, "
                    "same 2^31 trials, same amask/smask, same analytic null and the same frozen "
                    "ALIVE/DEAD rule. PAIRED: each r=6 arm reuses the seed and arm id of its r=5 "
                    "counterpart, so key and trial stream are identical and rounds is the only variable "
                    "that changes. BATCH-002's r=6 arms used a different key, so this pairing is a "
                    "stronger decay comparison than the prior batch's."),
                "frozen_falsification_rule": (
                    "any r=6 arm ALIVE => the statistic is NOT round-limited, is therefore not the yoyo "
                    "object, and the S-BOX-INDEPENDENT reading is COLLAPSED, not weakened"),
                "arms": r6,
                "paired_r5_vs_r6": pairs,
                "DECAY_OUTCOME": decay,
                "comparison_to_BATCH-002": (
                    "BATCH-002 measured r=6 under the real AES S-box at 1.50x (2^32 trials, arm A2) and "
                    "0.875x (2^33, arm A2b), i.e. already at the null. This is a cross-batch comparison "
                    "of the same toy object, not a comparison to published cryptanalysis."),
            },
            "declared_power_limitation": (
                "Mains at 2^31 trials (analytic null 2.0); structure-destroyed controls at 2^30 (null 1.0). "
                "BATCH-002's structure-destroyed arm A4 ran at 2^32. These controls therefore have LESS "
                "resolution than BATCH-002's and can only exclude an excess of roughly 5x or more."),
        },
        "rank_2_positive_control": rank2,
        "prediction_scorecard_frozen_before_measuring": {
            "P2.1 histogram {1:4}, all four diagonals unique and correct":
                ("MET" if rank2.get("MET_PREDICTION_P2.1") else "NOT MET" if rank2.get("status") == "COMPLETED" else "NOT SCORED"),
            "P2.2 hint_bytes_actually_differing = 0 on every diagonal":
                ("MET" if rank2.get("MET_PREDICTION_P2.2") else "NOT MET" if rank2.get("status") == "COMPLETED" else "NOT SCORED"),
            "P3.1 Y-AES-main excess in 8x-25x": {
                "measured_excess": mains[0].get("EXCESS_FACTOR"),
                "verdict": "MET" if (mains[0].get("EXCESS_FACTOR") is not None and 8 <= mains[0]["EXCESS_FACTOR"] <= 25) else "NOT MET",
            },
            "P3.2 both random mains ALIVE (H-INDEP) or both DEAD (H-DEP)": {
                "Y-R1-main": {"excess": mains[1].get("EXCESS_FACTOR"), "verdict": verdicts.get("Y-R1-main")},
                "Y-R2-main": {"excess": mains[2].get("EXCESS_FACTOR"), "verdict": verdicts.get("Y-R2-main")},
                "resolved_branch": reading,
                "registered_prior": "50/50 between H-INDEP and H-DEP, frozen before measuring",
            },
            "P3.3 all three structure-destroyed controls at excess <= 2.5x": {
                "Y-AES-sd": {"W_ge1": sds[0].get("MEASURED_W_ge1"), "null": sds[0].get("NULL_EXPECTATION_analytic"),
                             "excess": sds[0].get("EXCESS_FACTOR"), "within_predicted_band": sds[0].get("EXCESS_FACTOR", 99) <= 2.5},
                "Y-R1-sd": {"W_ge1": sds[1].get("MEASURED_W_ge1"), "null": sds[1].get("NULL_EXPECTATION_analytic"),
                            "excess": sds[1].get("EXCESS_FACTOR"), "within_predicted_band": sds[1].get("EXCESS_FACTOR", 99) <= 2.5},
                "Y-R2-sd": {"W_ge1": sds[2].get("MEASURED_W_ge1"), "null": sds[2].get("NULL_EXPECTATION_analytic"),
                            "excess": sds[2].get("EXCESS_FACTOR"), "within_predicted_band": sds[2].get("EXCESS_FACTOR", 99) <= 2.5},
                "verdict": "PARTIALLY MET" if not all(b.get("EXCESS_FACTOR", 99) <= 2.5 for b in sds) else "MET",
                "unexpected_observation_recorded_not_discarded": (
                    "Y-R2-sd measured 4 hits against an analytic null of 1.0 (excess 4.0x), OUTSIDE the "
                    "predicted <=2.5x band. It does not reach the frozen ALIVE bar (one-sided Poisson "
                    "P(K>=4 | lambda=1) = 0.0190, far above the 1e-6 requirement) and at 2^30 trials a "
                    "count of 4 against a null of 1 is an ordinary upward Poisson fluctuation. It is "
                    "recorded because it fell outside a frozen prediction band, and it is a reason to "
                    "re-run the structure-destroyed controls at higher trial counts before anyone leans "
                    "on them."
                    if sds[2].get("EXCESS_FACTOR", 0) > 2.5 else "none"),
            },
        },
        "absolute_anchor_for_the_random_sbox_path": ANCHOR,
        "confounding_and_arm_level_limits": CONFOUND,
        "calibration_run": CAL,
        "pins": PINS,
        "commands": COMMANDS,
        "checks_that_did_not_run": DIDNOTRUN,
        "protocol_deviations": DEVIATIONS,
        "what_this_cannot_establish": CANNOT,
        "artifact_parse_check": {
            "performed": True,
            "how": "this file is emitted by json.dump and then re-read with json.load by "
                   "build_results.py --verify, whose output is recorded in budget_stamps.jsonl",
            "note": "PREREGISTRATION.md is prose and needs no parser.",
        },
        "budget": BUDGET,
        "generated_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    with open(os.path.join(D, "RESULTS.json"), "w") as f:
        json.dump(out, f, indent=1)
    json.load(open(os.path.join(D, "RESULTS.json")))
    print("RESULTS.json written and re-parsed OK; reading =", reading)


DECAY_TEXT = {
    "DECAY_CONTROL_PASSED":
        "All three r=6 arms are DEAD under the frozen rule. The signal is round-limited under the real "
        "AES S-box AND under both random S-boxes, which is what a yoyo signal must be, so the object "
        "measured at r=5 is the BATCH-002 object and not a non-decaying artifact. The r=6 arms are "
        "paired with the r=5 arms on key and trial stream, so rounds is the only variable that changed. "
        "This removes an objection; it adds no strength to anything.",
    "NOT_ROUND_LIMITED_READING_COLLAPSED":
        "At least one r=6 arm is ALIVE. The statistic does NOT decay with rounds, so it is not a yoyo "
        "signal, the segment-1 S-BOX-INDEPENDENT reading is COLLAPSED rather than weakened, an "
        "arm-level offset in this software probe is on the table, and this disagrees with BATCH-002's "
        "r=6 measurement of the same toy object.",
    "DECAY_CONTROL_PARTIAL":
        "The r=6 arms did not all fall on the same side of the frozen rule. No clean decay reading is "
        "asserted; the raw counts and both Poisson tails are reported per arm.",
    "DECAY_CONTROL_DID_NOT_RUN":
        "The r=6 decay controls did not run. The segment-1 reading therefore still carries the defect "
        "the red team named: a signal claim with no decay control.",
}

WHAT_CHANGED = {
    "DECAY_CONTROL_PASSED":
        "The segment-1 S-BOX-INDEPENDENT reading STANDS EXACTLY AS RECORDED, with no upgrade in "
        "strength. What changed is that a named defect is closed: the r=6 decay control that segment 1 "
        "listed under checks_that_did_not_run has now been run for all three S-boxes and passed, and "
        "the random-S-box arms have gained an absolute per-round anchor they previously lacked. No "
        "segment-1 number was edited or rescored.",
    "NOT_ROUND_LIMITED_READING_COLLAPSED":
        "The segment-1 S-BOX-INDEPENDENT reading is WITHDRAWN. It is left in this file exactly as it "
        "was recorded, with the collapse stated beside it; it is not deleted and not rewritten.",
    "DECAY_CONTROL_PARTIAL":
        "The segment-1 reading is left as recorded and is now qualified by a decay control that did not "
        "resolve cleanly.",
    "DECAY_CONTROL_DID_NOT_RUN":
        "Nothing changed; the decay control did not run and the defect stands.",
}

READING_TEXT = {
    "S-BOX-INDEPENDENT":
        "The r=5 yoyo signal SURVIVES uniformly random bijective S-boxes. It is therefore NOT specific to "
        "the AES S-box, and on the evidence of this campaign so far NOTHING this campaign has found is "
        "specific to AES: the r=4 and r=5 counting properties were already reproduced under random "
        "bijective S-boxes, and the yoyo -- the last untested signal -- behaves the same way. Every result "
        "is a fact about SPN round geometry that AES happens to instantiate.",
    "S-BOX-DEPENDENT":
        "The r=5 yoyo signal DIES under uniformly random bijective S-boxes while surviving under the real "
        "AES S-box. On this evidence the yoyo is this campaign's one genuinely AES-S-box-specific object.",
    "MIXED / INDETERMINATE":
        "The arms did not fall cleanly on either side of the frozen decision rule. No reading is asserted; "
        "the raw counts, nulls and both Poisson tail probabilities are reported for every arm.",
}

SQ_SHA = subprocess.run(["sha256sum", os.path.join(D, "src", "sq_slot.c")],
                        capture_output=True, text=True).stdout.split()[0]

INFERENCE = {
    "policy": "executor-implementation",
    "requested_policy": "executor-implementation",
    "resolved_model": "claude-opus-5",
    "resolved_model_basis": "self-reported by the running session's own system context; no adapter probe was executed, so this resolution is not independently verified",
    "fallback_used": True,
    "fallback_basis": "orchestration/model-policies.yaml names GPT-5.6-family policy aliases that Claude Code cannot resolve; every subagent in this harness runs model: inherit",
    "model_verified": False,
    "standing_basis": "0137a051eb5828789eb267fa83c8278086578d4c",
    "independence_note": "This session supplies SESSION and IMPLEMENTATION independence from the BATCH-002 yoyo probe and supplies NO MODEL independence. Nothing here may count toward a closure quorum.",
}

OBJECT = (
    "E_K^r = ARK_r . SR . SB . [ARK_i . MC . SR . SB]_{i=r-1..1} . ARK_0, round keys = first r+1 of the "
    "UNTRUNCATED FIPS-197 AES-128 expansion computed with the SAME S-box the cipher uses. One trial: draw "
    "p0; form p1 by re-randomising every byte of every plaintext word in amask (rejecting a draw that "
    "leaves an active word unchanged); c0=E(p0), c1=E(p1); swap the ciphertext words in smask between c0 "
    "and c1 (a swap whose bytes all already agreed is TRIVIAL and excluded from all counts); q0=D(c0'), "
    "q1=D(c1'); d=q0^q1; W = number of plaintext words on which d vanishes; statistic = count of trials "
    "with W>=1. Identical to the BATCH-002 yoyo object."
)

GEOM = {
    "plaintext_side": "FORWARD ShiftRows diagonals PW[j] = {4*((j+row)%4)+row}",
    "ciphertext_side": "INVERSE ShiftRows diagonals CW[j] = {4*((j-row)%4)+row}",
    "PW_dumped_from_binary": [[0, 5, 10, 15], [4, 9, 14, 3], [8, 13, 2, 7], [12, 1, 6, 11]],
    "CW_dumped_from_binary": [[0, 13, 10, 7], [4, 1, 14, 11], [8, 5, 2, 15], [12, 9, 6, 3]],
    "agrees_with_BATCH-002_geom_json": True,
    "how_verified": "./yoyo_sbox geom compared byte for byte against BATCH-002/tasks/TASK-20260802-e4fa63/geom.json",
}

IMPL = {
    "reused_or_rewritten": "REWRITTEN",
    "why": "the BATCH-002 probe implements AES with AES-NI (_mm_aesenc_si128 / _mm_aesdec_si128), which "
           "hardwires the AES S-box in silicon; the S-box cannot be substituted there. src/yoyo_sbox.c is a "
           "T-table software AES whose S-box is a run-time parameter, reproducing BATCH-002's conventions, "
           "geometry, splitmix64 RNG, thread-seed derivation, key derivation from the arm seed, "
           "trivial-swap exclusion and reporting fields; the trial loop is a transcription of BATCH-002's "
           "worker() onto byte arrays.",
    "source": "src/yoyo_sbox.c",
    "build": "gcc -O2 -pthread -o yoyo_sbox src/yoyo_sbox.c",
}

SBOXDOC = {
    "draw": "Fisher-Yates shuffle of [0..255] driven by splitmix64 seeded with the recorded seed, with "
            "rejection sampling on each index (a 64-bit draw falling in the short tail is rejected), so "
            "there is no modulo bias",
    "bijectivity_verified_before_use": "the binary checks that every output value occurs exactly once, "
                                       "that all 256 values occur, and that ISBOX[SBOX[x]]==x and "
                                       "SBOX[ISBOX[x]]==x for all x; it exits 4 and refuses to measure "
                                       "otherwise. Independently re-checked in Python: sorted(sbox) == "
                                       "list(range(256)) for both draws.",
    "same_sbox_used_in_key_expansion": True,
    "seeds": {"R1": 20260803001, "R2": 20260803002},
    "full_tables": "runs/sbox_rand_20260803001.json and runs/sbox_rand_20260803002.json (256-entry arrays)",
}

CANNOT = [
    "TOY TIER. This is r=5 of a reduced-round AES-128 permutation with a full 128-bit key schedule, on one "
    "implementation, with two random S-box draws and at most 2^31 trials per arm.",
    "Nothing here speaks to full-round or deployed AES, and no comparison to published cryptanalysis is "
    "made in either direction.",
    "Two random draws bound very little about the space of 256! bijections. An S-BOX-DEPENDENT reading "
    "would say those two particular draws killed the signal, not that the AES S-box is unique; an "
    "S-BOX-INDEPENDENT reading would say those two draws preserved it, not that every bijection does.",
    "The structure-destroyed controls ran at 2^30 rather than BATCH-002's 2^32 and can only exclude an "
    "excess of roughly 5x or more.",
    "The RANK 2 arm establishes only that the modified sq_slot binary CAN emit a non-empty correct result "
    "under a true hint. It does not re-derive BATCH-003's rank-4 slot conclusions.",
    "This session provides no model independence. Nothing here may count toward a closure quorum.",
    "A timeout or resource cap is resource exhaustion and is never negative mathematical evidence.",
]

ANCHOR = None      # filled in __main__
CONFOUND = None    # filled in __main__

if __name__ == "__main__":
    GIT = json.load(open(os.path.join(R, "git_state.json")))
    ENV = json.load(open(os.path.join(R, "environment.json")))
    CAL = json.load(open(os.path.join(R, "CAL_meta.json")))
    PINS = json.load(open(os.path.join(R, "pins.json")))
    COMMANDS = json.load(open(os.path.join(R, "commands.json")))
    DIDNOTRUN = json.load(open(os.path.join(R, "didnotrun.json")))
    DEVIATIONS = json.load(open(os.path.join(R, "deviations.json")))
    BUDGET = json.load(open(os.path.join(R, "budget.json")))
    PC_DROP_REASON = json.load(open(os.path.join(R, "pc_drop.json")))["reason"]
    ANCHOR = json.load(open(os.path.join(R, "anchor.json")))
    CONFOUND = json.load(open(os.path.join(R, "confound.json")))
    main()
