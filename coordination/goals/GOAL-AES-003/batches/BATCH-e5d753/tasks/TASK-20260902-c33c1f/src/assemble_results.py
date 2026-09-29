#!/usr/bin/env python3
# assemble_results.py -- TASK-20260902-c33c1f (BATCH-e5d753, GOAL-AES-003)
#
# Assembles RESULTS.json from this task's artifacts. Run from the worktree
# root. Parses the whole file back with json.load after writing (parse
# attestation below).
#
# INFERENCE BLOCK: policy executor-implementation; resolved_model_id
# fireworks-ai/accounts/fireworks/models/qwen3p8-max (session-reported; no
# adapter probe run); fallback_used true; model_verified false;
# degraded_requirements []; amendment DEC-20260831-0d1eeb.
import json, re, datetime

TASK = "coordination/goals/GOAL-AES-003/batches/BATCH-e5d753/tasks/TASK-20260902-c33c1f"
S1_RESULTS = "coordination/goals/GOAL-AES-003/batches/BATCH-e5d753/tasks/TASK-20260902-525d16/RESULTS.json"

INFERENCE = {
    "policy": "executor-implementation",
    "requested_policy": "executor-implementation",
    "resolved_model_id": "fireworks-ai/accounts/fireworks/models/qwen3p8-max",
    "resolved_model_id_note": ("session-reported by the running session; no adapter probe "
                               "(python3 -m orchestration.adapter doctor --probe) was executed in this "
                               "session, so this identifier is unverified configuration"),
    "model_verified": False,
    "fallback_used": True,
    "fallback_reason": "session-backend transport under inference amendment DEC-20260831-0d1eeb",
    "degraded_requirements": [],
    "amendment": "DEC-20260831-0d1eeb",
    "independent_session": True,
}


def timing(path):
    txt = open(path).read()
    m = re.search(r"([\d.]+)\s+real", txt)
    rss = re.search(r"(\d+)\s+maximum resident set size", txt)
    return (float(m.group(1)) if m else None, int(rss.group(1)) if rss else None)


def run_row(run_id, k, seed, arm_id, label, cmd, receipt_path, timing_path, analysis):
    wall, rss = timing(timing_path)
    r = json.load(open(receipt_path))
    a = json.load(open(analysis))
    ids = a["amend1_identity_table"]
    return {
        "run_id": run_id,
        "k": k,
        "role": a["role"],
        "command": cmd,
        "binary_invocation": True,
        "arm_label": label,
        "seed": seed,
        "arm_id": arm_id,
        "threads": 4,
        "log2N": 30,
        "wall_seconds_time_l": wall,
        "max_rss_bytes": rss,
        "hits_W_ge1_nontrivial": a["hits_W_ge1_nontrivial"],
        "W_values_whist": a["whist"],
        "W_ge1_by_word": a["W_ge1_by_word"],
        "excess_ratio_vs_excess_E": a["excess_ratio_vs_excess_E"],
        "garwood95_rate_per_trial": a["garwood95_rate_per_trial"],
        "garwood95_count_scaled_per_2_30": a["garwood95_count_scaled_per_2_30"],
        "band": a["band"],
        "bandrank": a["bandrank"],
        "saturation_status": ids["saturation_status"],
        "hit_log_overflow": r["hit_log_overflow"],
        "outcome": "PASS" if a["point_verdict"] == "PASS" else a["point_verdict"],
        "amend1_identities_pass": a["amend1_identities_pass"],
        "seat_as_preregistered": a["seat_as_preregistered"],
        "elapsed_seconds_measured_receipt": r["elapsed_seconds_measured"],
        "analysis": analysis.split(TASK + "/")[1],
    }


def main():
    s1 = json.load(open(S1_RESULTS))
    u1_cmd = "timeout 3600 /usr/bin/time -l src/affarm046ex arm U1K1-SS-R5-P30 5 1 1 30 531002 9 4 s1"
    u2_cmd = "timeout 3600 /usr/bin/time -l src/affarm046ex arm U2K4-SS-R5-P30 5 1 1 30 531002 4 4 s4"
    u1 = run_row("S2-1", 1, 531002, 9, "U1K1-SS-R5-P30", u1_cmd,
                 TASK + "/runs/U1_k1_seed2.json", TASK + "/runs/U1_k1_seed2.timing.txt",
                 TASK + "/runs/U1_k1_seed2_analysis.json")
    u2 = run_row("S2-2", 4, 531002, 4, "U2K4-SS-R5-P30", u2_cmd,
                 TASK + "/runs/U2_k4_seed2.json", TASK + "/runs/U2_k4_seed2.timing.txt",
                 TASK + "/runs/U2_k4_seed2_analysis.json")
    verdict = json.load(open(TASK + "/runs/verdict_composition.json"))
    u1a = json.load(open(TASK + "/runs/U1_k1_seed2_analysis.json"))
    u2a = json.load(open(TASK + "/runs/U2_k4_seed2_analysis.json"))

    stamps = [json.loads(l) for l in open(TASK + "/budget_stamps.jsonl") if l.strip()]
    start_utc = stamps[0]["utc"]
    t0 = datetime.datetime.fromisoformat(start_utc)
    t1 = datetime.datetime.now(datetime.timezone.utc)
    wall_used = (t1 - t0).total_seconds()

    out = {
        "schema": "crypto.autoresearch.task_results.v1",
        "task_id": "TASK-20260902-c33c1f",
        "batch_id": "BATCH-e5d753",
        "goal_id": "GOAL-AES-003",
        "idea_record": "IDEA-20260902-9e84ac",
        "stage": "S2 (second seeds + SH2 verdict composition)",
        "pin_reference": {
            "id": "PIN-T0",
            "decision": "DEC-20260901-fb6f11",
            "statement": "SubWord uses TPOS[0] (first position of the frozen order): identity schedule at k=0, AES schedule at every k >= 1",
        },
        "gate_regime": {
            "id": "AMEND-1",
            "decision": "DEC-20260901-6f9de3",
            "preregistration": "coordination/goals/GOAL-AES-003/batches/BATCH-e5d753/tasks/TASK-20260902-987716/PREREGISTRATION.md (write-once, BINDING for this task, not rewritten; DEV-S0-1 corrected zhist convention adopted: sum(zhist)==nontrivial_trials, affarm046ex.c:458-459)",
        },
        "scope1_joint_effect_scoping": {
            "id": "SCOPE-1",
            "decision": "DEC-20260902-38227b",
            "statement": "under PIN-T0 the key schedule is the AES schedule at EVERY interior point k >= 1 and is therefore CONSTANT across k in {1,2,4,8,16}; all interior-to-interior comparisons in this batch are schedule-clean; the schedule-vs-dilution confound attaches only to identity-schedule counterfactuals, which this batch does not make. Every h(1) statement is joint-effect-scoped; every interior decay statement is attributed to table dilution AT FIXED SCHEDULE.",
        },
        "s1_gate_check": {
            "source": "coordination/goals/GOAL-AES-003/batches/BATCH-e5d753/tasks/TASK-20260902-525d16/RESULTS.json + runs/verdict_partial.json (snapshot-bound under archives/TASK-20260902-4be096)",
            "results_sha256_read": "e0df2b62daa6e45b58ad2b656855f3d2496eb5a0f09742c1a04b1949187bd31c",
            "results_sha256_snapshot_bound": "e0df2b62daa6e45b58ad2b656855f3d2496eb5a0f09742c1a04b1949187bd31c",
            "sha256_match": True,
            "verdict_partial_sha256_read": "fcf7db065d001899c0f5cf133d1d8668184df59efdafaa7f44b2e8a3dfb173bc",
            "s0_outcome_ordered_cascade": "PASS-S0",
            "s1_branches_1_4_status": {
                "branch_1_SH2-GATE-FAIL": "NOT_FIRED",
                "branch_2_SH2-F6": "NOT_FIRED",
                "branch_3_SH2-ANCHOR-FAIL": "NOT_FIRED",
                "branch_4_SH2-RESEAT-FAIL": "NOT_FIRED",
            },
            "halt_or_indictment_fired": False,
            "decision": "PROCEED to S2 arms",
        },
        "build_provenance": {
            "lineage": "re-verified frozen build (affarm046ex, HIT_LOG_CAP 256 per thread), copied byte-exact from TASK-20260902-987716/src/ (the S0 re-verified build whose hashes matched the BATCH-7b798d snapshot receipts); zero source change, not recompiled, instrument UNMODIFIED",
            "copy_time_sha256": {
                "src/affarm046ex.c": "ec748cefcb1fccfdd4e441a4898b21cf4b7eff056599ce07769e3f0fab091f37",
                "src/affarm046ex": "74e3d65ca6ecdd877dda5d9e19a96a5af66740b118dbcd1dd35b78be5d102702",
                "src/freeze_digest.py": "c29e876b76a4a4ba6cf200d36a56ae1bc8faf8c0bdacbc40df5c30024a2b2814",
            },
            "matches_snapshot_bound_hashes": True,
            "postarm_sha256_match": True,
            "worktree_branch": "aes003-shape2-batch-20260902",
        },
        "runs": [u1, u2],
        "binary_invocations_used": 2,
        "binary_invocations_max": 4,
        "amend1_identity_tables": {
            "U1_k1_seed2": u1a["amend1_identity_table"],
            "U2_k4_seed2": u2a["amend1_identity_table"],
            "note": "full per-receipt AMEND-1 identity suites; the zhist internal identity is sum(zhist)==nontrivial_trials per the frozen whist convention (affarm046ex.c:458-459; DEV-S0-1 corrected convention adopted per this task's handoff); the literal '==trials' shorthand holds iff trivial_swaps_excluded==0 (true for BOTH S2 receipts: 0 trivial swaps excluded)",
        },
        "amend1_counter_identities_all_analysis_bearing_receipts": {
            "U1_k1_seed2": True,
            "U2_k4_seed2": True,
            "gate_pass": True,
        },
        "seed_agreement_table": {
            "preregistered_criterion": "band agreement between primary seed 531001 and second seed 531002 at each load-bearing point (PREREGISTRATION section 11); per-seed readings, never pooled; exact-rate comparisons at agreed bands report seed variance with propagated Garwood CIs (report-only)",
            "k1_seed531001_vs_seed531002": verdict["seed_agreement_table"]["k1_seed531001_vs_seed531002"],
            "k4_seed531001_vs_seed531002": verdict["seed_agreement_table"]["k4_seed531001_vs_seed531002"],
            "outcome": {
                "k1_band_agreement": True,
                "k4_band_agreement": True,
                "verdict_stability_condition_satisfied": True,
                "instrument_level_alarm_k1": False,
            },
        },
        "sh2_verdict_ordered": {
            "artifact": "runs/verdict_composition.json",
            "composed_after_all_readings_including_second_seeds": True,
            "cascade_evaluation_ordered": verdict["cascade_evaluation_ordered"],
            "branch_fired": verdict["verdict"]["branch_fired"],
            "statement": verdict["verdict"]["statement"],
            "transition_localization": verdict["verdict"]["transition_localization"],
            "tier2_count_resolution_primary_seed": verdict["verdict"]["tier2_count_resolution_primary_seed"],
            "named_successors_preregistered": verdict["verdict"]["named_successors_preregistered"],
            "inputs_this_batch_only": verdict["inputs_this_batch_only"],
        },
        "deviations": [
            {
                "id": "DEV-S2-1",
                "description": "Stderr convention (lineage DEV-S0-3 / DEV-S1-2): each invocation redirects stderr (including the /usr/bin/time -l resource report) into runs/X.timing.txt; runs/X.err is created as an empty placeholder file exactly as in the BATCH-7b798d / S0 / S1 lineage.",
                "impact": "none",
            },
            {
                "id": "DEV-S2-2",
                "description": "Arm run labels (U1K1-SS-R5-P30, U2K4-SS-R5-P30) are executor-chosen receipt-echo fields only (lineage DEV-S1-4); stream derivation (thread_seeds, key_stream_seeds) depends only on seed/armid/thread index.",
                "impact": "none",
            },
            {
                "id": "DEV-S2-3",
                "description": "The first execution of src/verdict_composition.py wrote runs/verdict_composition.json with a cosmetic label defect in the verdict.branch_fired field ('8_SH2-MONOTONE-DECAY' instead of 'SH2-MONOTONE-DECAY'; a string-split slip in the assembler-side label, no reading affected). The script was corrected and the file regenerated before assembly; no snapshot had bound the draft; no reading, conjunct evaluation, or branch status changed between the two passes.",
                "impact": "none (cosmetic label only; regenerated pre-snapshot)",
            },
            {
                "id": "DEV-S2-4",
                "description": "src/verdict_composition.py and this assembler are written to be run from the worktree root (their input paths are worktree-root-relative); the first verdict invocation from the task directory exited 1 on a path error before writing anything and was re-invoked from the root. No output was produced by the failed invocation.",
                "impact": "none",
            },
        ],
        "unexpected_observations": [
            {
                "id": "OBS-S2-1",
                "rule8": True,
                "observation": "Second-seed k=1 reading (frozen 363851 armid-9 replication seat, seed 531002): h(1; 531002) = 12,679,968 vs h(1; 531001) = 12,681,109 - a difference of -1,141 hits (relative -0.0090%), ratio second/primary 0.99991 with overlapping Garwood 95% CIs. The saturated receipt carries overflow 12,678,944 = 12,679,968 - 4x256 with all AMEND-1 counter identities exact (pure cap truncation, legal under AMEND-1). Band agreement THRESHOLD==THRESHOLD; the seed-variance measurement at the largest reading shows sub-0.01% relative variation at matched exposure, consistent with the design-time expectation that a band departure at k=1 would be a many-thousand-sd event. No instrument-level alarm.",
            },
            {
                "id": "OBS-S2-2",
                "rule8": True,
                "observation": "Second-seed k=4 reading (seed 531002, seat-fixed armid 4): h(4; 531002) = 21 vs h(4; 531001) = 17, both RESIDUAL (band agreement). The between-seed count difference (+4, ratio 1.235) is within-band and below the 2^30 per-point resolution: the Garwood 95% CIs overlap heavily, so the seed comparison at k=4 is declared COUNT-UNRESOLVED, never smoothed. Word split: whist [1073741803, 2, 0, 19, 0] - two W=1 hits plus 19 W=3 hits, the same W=1+W=3 motif the primary-seed k=4 observation carries (1x W=1 + 16x W=3) and the k=1/k=2 observations carry (report-only enabling data; no branch conjunct consumes it; no carrier sentence drawn). Unsaturated (overflow 0).",
            },
            {
                "id": "OBS-S2-3",
                "rule8": True,
                "observation": "Composed SH2 verdict: SH2-MONOTONE-DECAY with transition localized to (2,4] (h(2) = 149,371 >= 100). The verdict-stability condition is satisfied at BOTH load-bearing points (k=1 and k=4 band-agree across seeds 531001/531002). Under SCOPE-1 this interior decay is attributed to table dilution AT FIXED SCHEDULE (AES schedule constant across all interior k >= 1 under PIN-T0); h(1) itself and the k=0->k=1 step remain joint-effect-scoped. Count-level (tier-2, primary seed, reported only): (1,2) and (2,4) COUNT-DECAY-RESOLVED (ratios 84.90 and 8,786.5 with propagated CIs); (4,8) and (8,16) COUNT-UNRESOLVED (overlapping Garwood 95% CIs). First composed shape verdict of the AMEND-1 era for this family; every statement scoped to the frozen family subset {0,1,2,4,8,16}, cell (amask=1, smask=1), r=5, PIN-T0, 2^30 per point, toy tier.",
            },
        ],
        "budget": {
            "wall_clock_seconds_declared": 4400,
            "wall_clock_seconds_used_task_start_to_assembly": wall_used,
            "binary_invocations": {"used": 2, "max": 4},
            "memory_gb_declared": 4,
            "max_rss_bytes_observed": max(u1["max_rss_bytes"] or 0, u2["max_rss_bytes"] or 0),
            "per_arm_timeout_wrapper": "timeout 3600",
            "budget_stamps": "budget_stamps.jsonl",
            "arm_wall_seconds": {"S2-1": u1["wall_seconds_time_l"], "S2-2": u2["wall_seconds_time_l"]},
            "binding_baseline_note": "~27 min per 2^30 4-thread arm is the budget contract; measured rates here (%.2f s and %.2f s per 2^30 arm) are OPTIMISTIC-RELATIVE and disclosed, never charged as the baseline" % (u1["wall_seconds_time_l"], u2["wall_seconds_time_l"]),
            "exhaustion_policy": "resource_exhaustion, never a reading (rule 5)",
            "resource_exhaustion_occurred": False,
        },
        "scope_discipline": {
            "claim_tier": "toy",
            "no_deployed_aes_claims": True,
            "no_published_cryptanalysis_comparisons": True,
            "no_new_points_beyond_second_seeds": True,
            "no_third_seeds": True,
            "no_k_3_5_6": True,
            "no_k_12": True,
            "no_2pow32_arms": True,
            "x_statistic_not_computed": True,
            "no_rho_exclusion": True,
            "no_git_add_or_commit": True,
            "no_status_or_promotion_interpretation": True,
            "joint_effect_scoping_honored": True,
            "no_reopen_clause_honored": True,
            "batch_7b798d_observations_not_inputs": True,
        },
        "artifact_inventory": {
            "RESULTS.json": "this file",
            "budget_stamps.jsonl": "budget stamps (task start, S1 gate check + instrument copy, preregistration consult, support scripts, per-arm start/end, post-arm instrument re-verification, verdict composition, assembly)",
            "src/affarm046ex.c": "frozen instrument source (byte-exact copy of the S0 re-verified build, UNMODIFIED)",
            "src/affarm046ex": "frozen binary (byte-exact copy of the S0 re-verified build, UNMODIFIED, not recompiled)",
            "src/freeze_digest.py": "freeze digester/reverifier (copied UNMODIFIED from TASK-20260902-987716/src/)",
            "src/BUILD.md": "build/run/budget/inference record",
            "src/s2_analysis.py": "S2 second-seed analysis under AMEND-1 (fresh)",
            "src/verdict_composition.py": "ordered 10-branch SH2 cascade composer (fresh)",
            "src/assemble_results.py": "this assembler (fresh)",
            "runs/U1_k1_seed2.json|.err|.timing.txt": "S2-1 second-seed k=1 receipt (seed 531002, armid 9, saturated)",
            "runs/U1_k1_seed2_analysis.json": "S2-1 analysis (hits, W breakdown, excess ratio, Garwood CI, band, AMEND-1 identity table, seat checks)",
            "runs/U2_k4_seed2.json|.err|.timing.txt": "S2-2 second-seed k=4 receipt (seed 531002, armid 4, unsaturated)",
            "runs/U2_k4_seed2_analysis.json": "S2-2 analysis (same set)",
            "runs/verdict_composition.json": "full ordered SH2 cascade evaluation from ALL readings (S0 gates/anchors, S1 grid + gates, S2 second seeds): branches 1-7 NOT_FIRED with reasons, branch 8 SH2-MONOTONE-DECAY FIRED, branches 9-10 NOT_REACHED; seed-agreement table; SCOPE-1 attribution; tier-2 pair declarations",
        },
        "assembled_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "parse_attestation": "RESULTS.json is machine-generated JSON; parsed whole with python3 json.load after writing, before task completion",
        "inference": INFERENCE,
    }
    path = TASK + "/RESULTS.json"
    with open(path, "w") as f:
        json.dump(out, f, indent=1)
    json.load(open(path))
    print("RESULTS.json written and re-parsed OK; verdict:", out["sh2_verdict_ordered"]["branch_fired"])


if __name__ == "__main__":
    main()
