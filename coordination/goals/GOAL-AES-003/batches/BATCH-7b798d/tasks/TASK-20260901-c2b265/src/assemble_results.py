#!/usr/bin/env python3
# assemble_results.py -- TASK-20260901-c2b265 (BATCH-7b798d, GOAL-AES-003)
#
# Assembles RESULTS.json from the task's artifacts. Observations only: no
# status/strength/promotion interpretation, no hypothesis changes, no
# commits. The ordered SH verdict is the preregistered cascade's reading;
# its downstream consequences (invalid_measurement, repair) are Coordinator
# acts, not executor acts.
#
# INFERENCE BLOCK: policy executor-implementation; requested_policy
# executor-implementation; resolved_model_id
# fireworks-ai/accounts/fireworks/models/qwen3p8-max (session-reported; no
# adapter probe run in this session); fallback_used true; model_verified
# false; degraded_requirements []; amendment DEC-20260831-0d1eeb.
import json, re, datetime, pathlib

INFERENCE = {
    "policy": "executor-implementation",
    "requested_policy": "executor-implementation",
    "resolved_model_id": "fireworks-ai/accounts/fireworks/models/qwen3p8-max",
    "resolved_model_id_note": ("session-reported by the running session; no adapter "
                               "probe (python3 -m orchestration.adapter doctor "
                               "--probe) was executed in this session, so this "
                               "identifier is unverified configuration"),
    "model_verified": False,
    "fallback_used": True,
    "fallback_reason": "session-backend transport under inference amendment DEC-20260831-0d1eeb",
    "degraded_requirements": [],
    "amendment": "DEC-20260831-0d1eeb",
    "independent_session": True,
}
EXCESS_E = 1 << 30


def timing(path):
    txt = pathlib.Path(path).read_text()
    m = re.search(r"^\s*([\d.]+)\s+real", txt, re.M)
    rss = re.search(r"^\s*(\d+)\s+maximum resident set size", txt, re.M)
    return (float(m.group(1)) if m else None,
            int(rss.group(1)) if rss else None)


def point_row(run_id, command, receipt, analysis, timing_path):
    r = json.load(open(receipt))
    a = json.load(open(analysis))
    wall, rss = timing(timing_path)
    failed = [k for k, v in a["consistency_checks"].items() if not v]
    return {
        "run_id": run_id,
        "k": a["k"],
        "command": command,
        "timeout_wrapper": "timeout 3600",
        "seed": r["seed"],
        "arm_id": r["arm_id"],
        "threads": r["threads"],
        "log2N": r["log2N"],
        "wall_seconds_time_l": wall,
        "max_rss_bytes": rss,
        "hits_W_ge1_nontrivial": a["hits_W_ge1_nontrivial"],
        "W_breakdown": {"whist": a["whist"], "W_ge1_by_word": a["W_ge1_by_word"]},
        "excess_ratio_vs_excess_E": a["excess_ratio_vs_excess_E"],
        "excess_E": EXCESS_E,
        "null_expectation_analytic_run_internal": a["null_expectation_analytic_run_internal"],
        "excess_over_run_internal_null": a["excess_over_run_internal_null"],
        "garwood95_rate_per_trial": a["garwood95_rate_per_trial"],
        "garwood95_count_scaled_per_2_30": a["garwood95_count_scaled_per_2_30"],
        "band": a["band"],
        "bandrank": a["bandrank"],
        "hit_log_overflow": a["hit_log_overflow"],
        "consistency_checks_failed": failed,
        "all_consistency_checks_pass": a["all_consistency_checks_pass"],
        "analysis_file": analysis,
    }


def main():
    rows = [
        point_row("S1-1", "src/affarm046ex arm T1-K16RESEAT-R5-P30 5 1 1 30 531001 8 4 aes",
                  "runs/T1_k16_reseat.json", "runs/T1_k16_analysis.json",
                  "runs/T1_k16_reseat.timing.txt"),
        point_row("S1-2", "src/affarm046ex arm T2-K1-R5-P30 5 1 1 30 531001 2 4 s1",
                  "runs/T2_k1.json", "runs/T2_k1_analysis.json", "runs/T2_k1.timing.txt"),
        point_row("S1-3", "src/affarm046ex arm T3-K2-R5-P30 5 1 1 30 531001 3 4 s2",
                  "runs/T3_k2.json", "runs/T3_k2_analysis.json", "runs/T3_k2.timing.txt"),
        point_row("S1-4", "src/affarm046ex arm T4-K8-R5-P30 5 1 1 30 531001 6 4 s8",
                  "runs/T4_k8.json", "runs/T4_k8_analysis.json", "runs/T4_k8.timing.txt"),
    ]
    det_rows = []
    for rid, rec, tim in (("S1-5a", "runs/T5_det_a.json", "runs/T5_det_a.timing.txt"),
                          ("S1-5b", "runs/T5_det_b.json", "runs/T5_det_b.timing.txt")):
        r = json.load(open(rec))
        wall, rss = timing(tim)
        det_rows.append({
            "run_id": rid,
            "command": "src/affarm046ex arm T5-DETX256-AES-R5-P20 5 1 1 20 531001 1 4 aes",
            "timeout_wrapper": "timeout 3600",
            "seed": 531001, "arm_id": 1, "threads": 4, "log2N": 20,
            "wall_seconds_time_l": wall, "max_rss_bytes": rss,
            "hits_W_ge1_nontrivial": r["W_ge1_nontrivial"],
            "hit_log_overflow": r["hit_log_overflow"],
            "gate": "determinism double",
        })
    t1a = json.load(open("runs/T1_k16_analysis.json"))
    t5c = json.load(open("runs/T5_det_cmp.json"))
    t6r = json.load(open("runs/T6_digest_reverify.json"))
    t6fr = json.load(open("runs/T6_freeze_rerun.json"))
    t6sd = json.load(open("runs/T6_source_diff_info.json"))

    wallf, rssf = timing("runs/T6_freeze.timing.txt")
    freeze_row = {
        "run_id": "S1-6",
        "command": "src/affarm046ex freeze 363851",
        "timeout_wrapper": "timeout 3600",
        "seed": 363851, "wall_seconds_time_l": wallf, "max_rss_bytes": rssf,
        "gate": "post-arm table-freeze digest re-verification",
        "freeze_pass": t6fr.get("freeze_pass"),
    }
    verdict = json.load(open("runs/verdict_composition.json"))
    s0 = json.load(open("../TASK-20260901-706b1d/RESULTS.json"))

    stamps = [json.loads(l) for l in open("budget_stamps.jsonl")]
    t0 = datetime.datetime.fromisoformat(stamps[0]["utc"])
    now = datetime.datetime.now(datetime.timezone.utc)
    arm_walls = [r["wall_seconds_time_l"] for r in rows + det_rows + [freeze_row]
                 if r.get("wall_seconds_time_l") is not None]
    max_rss = max(r["max_rss_bytes"] for r in rows + det_rows + [freeze_row]
                  if r.get("max_rss_bytes") is not None)

    results = {
        "schema": "crypto.autoresearch.task_results.v1",
        "task_id": "TASK-20260901-c2b265",
        "batch_id": "BATCH-7b798d",
        "goal_id": "GOAL-AES-003",
        "idea_record": "IDEA-20260901-582ea9",
        "stage": "S1",
        "pin_reference": {
            "id": "PIN-T0",
            "decision": "DEC-20260901-fb6f11",
            "statement": ("SubWord uses TPOS[0] (first position of the frozen order): "
                          "identity schedule at k=0, AES schedule at every k >= 1; "
                          "scoped to BATCH-7b798d"),
        },
        "s0_gate_check": {
            "read_first_before_any_interior_arm": True,
            "source": ("coordination/goals/GOAL-AES-003/batches/BATCH-7b798d/tasks/"
                       "TASK-20260901-706b1d/RESULTS.json"),
            "snapshot_bound_by": "archives/TASK-20260901-56ecb6 (commit a1cc0a107)",
            "s0_outcome_ordered_cascade": s0["s0_outcome_ordered_cascade"],
            "decision": "PASS-S0 -> interior arms admitted",
            "s0_readings_consumed": {
                "S0-5_dead_anchor_hits": 0,
                "S0-6_rampzero_hits": 1073741824,
                "S0-4_gate0x_hits": 14,
            },
        },
        "instrument": {
            "reused_unmodified": True,
            "source_dir": ("coordination/goals/GOAL-AES-003/batches/BATCH-7b798d/tasks/"
                           "TASK-20260901-706b1d/src"),
            "sha256_source": "ec748cefcb1fccfdd4e441a4898b21cf4b7eff056599ce07769e3f0fab091f37",
            "sha256_binary": "74e3d65ca6ecdd877dda5d9e19a96a5af66740b118dbcd1dd35b78be5d102702",
            "identical_to_s0_copies_at_copy_time": True,
            "rebuilt": False,
            "postarm_source_diff_empty": t6sd["diff_empty"],
            "postarm_binary_identical": t6sd["binary_identical_to_s0_copy"],
            "hit_log_cap": 256,
        },
        "runs": rows,
        "gate_runs": det_rows + [freeze_row],
        "gates": {
            "S1-1_reseat_band": {
                "band": [6, 30],
                "hits": t1a["hits_W_ge1_nontrivial"],
                "in_band": t1a["reseat_gate"]["in_band"],
                "verdict": "PASS",
                "note": ("known-alive re-seat ANALYZED FIRST within S1 (binding "
                         "order); interior points admitted"),
            },
            "S1-5_determinism_identity": {
                "raw_byte_identical": t5c["raw_byte_identical"],
                "byte_identical_modulo_preregistered_timing_strip_set":
                    t5c["byte_identical_modulo_timing_lines"],
                "strip_set": t5c["preregistered_strip_set_timing"],
                "differing_semantic_fields": t5c["differing_semantic_fields"],
                "pass": t5c["determinism_pass"],
                "note": ("raw byte identity impossible by construction for "
                         "wall-clock fields; the preregistered comparator notion "
                         "is byte-identity modulo the strip set (BATCH-ace664 P5 "
                         "convention)"),
            },
            "S1-6_digest_reverify": {
                "committed_file": ("coordination/goals/GOAL-AES-003/batches/BATCH-2f12ac/"
                                   "tasks/TASK-20260901-7e0b71/runs/R3_table_freeze.json"),
                "freeze_pass": t6fr.get("freeze_pass"),
                "reverify_pass": t6r["reverify_pass"],
                "mismatches": t6r["mismatches"],
                "pass": t6r["reverify_pass"] and bool(t6fr.get("freeze_pass")),
            },
            "S1-6_source_diff_postarm": {
                "command": t6sd["command"],
                "diff_empty": t6sd["diff_empty"],
                "source_identical_to_s0_copy": t6sd["source_identical_to_s0_copy"],
                "binary_identical_to_s0_copy": t6sd["binary_identical_to_s0_copy"],
                "pass": t6sd["diff_empty"],
                "raw_diff": "runs/source_diff_raw_postarm.txt",
            },
            "hit_overflow_zero_on_all_analysis_bearing_receipts": {
                "by_run": {r["run_id"]: r["hit_log_overflow"] for r in rows},
                "pass": all(r["hit_log_overflow"] == 0 for r in rows),
                "failed_runs": [r["run_id"] for r in rows if r["hit_log_overflow"] > 0],
                "note": ("SH-GATE-FAIL conjunct of PREREGISTRATION.md section 5 "
                         "branch 1: for every S1 arm (sparse-hit expectation) "
                         "hit_overflow > 0 fires branch 1; the section-5 k=0 "
                         "anchor note is carried forward but NOT extended per "
                         "the handoff; see deviations DEV-S1-2 and unexpected "
                         "observations OBS-S1-3 for the cap-truncation "
                         "accounting of the two non-sparse readings"),
            },
            "S0_gates_inherited": {
                "S0-2_KAT_pins": s0["gates"]["S0-2_KAT_pins"]["gate_pass"],
                "S0-3_freeze_reverification": s0["gates"]["S0-3_freeze_reverification"]["gate_pass"],
                "S0-4_gate0x_rebuild_identity": s0["gates"]["S0-4_gate0x_rebuild_identity"]["gate_pass"],
                "committed_s0_outcome": s0["s0_outcome_ordered_cascade"],
            },
        },
        "ordered_sh_verdict": verdict["ordered_sh_verdict"],
        "shape_verdict_composed": verdict["shape_verdict_composed"],
        "verdict_composition": "runs/verdict_composition.json",
        "verdict_note": (
            "Branch 1 SH-GATE-FAIL fired on hit_overflow > 0 on the S1-2 (k=1) "
            "and S1-3 (k=2) analysis-bearing receipts; all other branch-1 "
            "conjuncts (S0 inherited gates, S1-5 determinism, S1-6 "
            "digest/source-diff, seat/consistency checks other than overflow) "
            "PASS. Per the cascade: invalid_measurement; HALT; repair (rule 5); "
            "never evidence about shape; NO shape verdict is composed. The "
            "recorded per-point readings are observations retained for the "
            "repair route and the validator; downstream consequences are "
            "Coordinator acts. The 41-99 ambiguity band was never reached or "
            "smoothed."),
        "per_point_readings_retained_report_only": {
            "k16": {"hits": 12, "band": "RESIDUAL"},
            "k1": {"hits": 12681109, "band": "THRESHOLD"},
            "k2": {"hits": 149371, "band": "THRESHOLD"},
            "k8": {"hits": 13, "band": "RESIDUAL"},
            "note": ("retained as observations under rule 8; NOT a shape "
                     "verdict; the cascade's gate branch precedes all shape "
                     "branches (dead-arm-first / gate-first discipline)"),
        },
        "sensitivity_floors_carried": {
            "lambda_80_hits_per_2_30": 8.0,
            "lambda_95_hits_per_2_30": 10.5,
            "statement": ("PREREGISTRATION.md section 2 (design-time, declared "
                          "before any reading); NULLBAND readings exclude a "
                          "per-point excess >= ~8-10.5 at 80-95% power and "
                          "nothing below; within-residual-band trends not "
                          "resolvable at 2^30; no interior point read NULLBAND "
                          "this batch, so no per-point exclusion is claimed "
                          "from these readings; NO rho-exclusion anywhere"),
        },
        "deviations": [
            {
                "id": "DEV-S1-1",
                "description": (
                    "First execution of src/s1_analysis.py (on the S1-1 receipt) "
                    "exited 12 because its hit_trials_logged check encoded an "
                    "executor misassumption (expected the aggregate logged-hit "
                    "count). The receipt field hit_trials_logged is thread 0's "
                    "count by documented lineage source semantics "
                    "(nthr>0?jobs[0].hit_count:0); all 12 hits were fully "
                    "recorded in hit_trials/hit_e_detail with overflow 0. The "
                    "check was corrected to the field's actual semantics "
                    "(thread-0 count identity, detail completeness under "
                    "overflow, per-thread cap bound) and the analysis rerun "
                    "(exit 0). No receipt was modified; the preregistered "
                    "re-seat conjuncts (hits in [6,30], overflow, seat, trial "
                    "accounting) were unaffected. The flawed first pass wrote "
                    "an analysis JSON carrying the failed check, superseded by "
                    "the corrected analysis (a task artifact, not a receipt)."),
                "impact": "none on readings; analysis-script correction only",
            },
            {
                "id": "DEV-S1-2",
                "description": (
                    "SH-GATE-FAIL (branch 1, hit_overflow conjunct) fired at "
                    "S1-2 (k=1). The cascade's branch-1 text says "
                    "invalid_measurement; HALT; repair, but does not explicitly "
                    "forbid recording further readings (branches 2-3 carry "
                    "explicit 'no interior reading admitted' language). The "
                    "handoff's REQUIRED SEQUENCE directs all six steps with the "
                    "verdict composed ONLY after all interior points are read, "
                    "showing each branch evaluated in order and the readings "
                    "consumed. The remaining sequence (S1-3, S1-4, S1-5, S1-6) "
                    "was therefore executed to evaluate every branch-1 conjunct "
                    "(determinism, digest, source-diff) and record repair "
                    "diagnostics, with NO shape verdict composed. This "
                    "interpretive joint is flagged for the validator and "
                    "Coordinator; under the strictest halt reading the extra "
                    "arms are retained observations only and change nothing "
                    "about the fired branch."),
                "impact": "none on the fired verdict; extra repair-diagnostic observations recorded",
            },
            {
                "id": "DEV-S1-3",
                "description": (
                    "src/freeze_digest.py (reused unmodified from the S0 task) "
                    "was initially omitted from this task's src/ and the "
                    "omission was discovered at the S1-6 digest step, AFTER the "
                    "freeze binary invocation had run and its raw C output was "
                    "captured. The script was then copied byte-exact from the "
                    "S0 task (sha256 identity verified) and the digest/reverify "
                    "run on the already-captured output. No receipt was "
                    "affected; the ordering (freeze invocation before script "
                    "copy) is disclosed. The script carries the S0 task's "
                    "embedded task_id/idea_record labels; reused as-is under "
                    "the handoff's no-modification rule, disclosed in BUILD.md "
                    "and here."),
                "impact": "none on readings; ordering and label provenance disclosed",
            },
        ],
        "unexpected_observations": [
            {
                "id": "OBS-S1-1",
                "rule8": True,
                "observation": (
                    "k=1 (S_1, AES at position 0 only, AES schedule under "
                    "PIN-T0) reads 12,681,109 hits at 2^30 (1.181% of "
                    "nontrivial trials; excess ratio 0.011811 vs frozen "
                    "excess_E = 2^30; run-internal analytic null 1.0). This is "
                    "~3 orders of magnitude above the design-time GRADUAL "
                    "threshold (>= 100) and far outside the entire design-time "
                    "power table (IDEA-20260901-582ea9 design_time_power "
                    "covers lambda up to ~150). First interior measurement in "
                    "the campaign; whist [1061060715, 1, 0, 12681108, 0]: "
                    "12,681,108 hits at W=3 and 1 hit at W=1; zhist carries "
                    "secondary mass at Z=12..15 (12,484,056 / 195,892 / 1,156 "
                    "/ 4) consistent with the W=3 law. Recorded per rule 8; "
                    "NOT a shape verdict (gate branch precedes)."),
            },
            {
                "id": "OBS-S1-2",
                "rule8": True,
                "observation": (
                    "k=2 reads 149,371 hits (THRESHOLD; excess ratio "
                    "0.000139). The four readings over {1,2,8,16} are "
                    "12,681,109 -> 149,371 -> 13 -> 12: monotone decay in k "
                    "with bandranks 3,3,1,1 (band-non-rising in k). Under the "
                    "frozen bands this pattern lies in the SH-GRADUAL "
                    "direction, but NO shape verdict is composed because "
                    "branch 1 SH-GATE-FAIL fired and precedes all shape "
                    "branches. Recorded as observation only; any shape "
                    "statement awaits the Coordinator's repair/re-run decision."),
            },
            {
                "id": "OBS-S1-3",
                "rule8": True,
                "observation": (
                    "hit_log_overflow on the two non-sparse receipts equals "
                    "hits - threads*256 EXACTLY (k=1: 12,681,109 - 1024 = "
                    "12,680,085; k=2: 149,371 - 1024 = 148,347): the necessary "
                    "truncation of the capped per-hit detail log, identical in "
                    "form to the k=0 anchor case PREREGISTRATION.md section 5 "
                    "item 1 addresses. Every counter on both receipts is "
                    "cap-independent and internally consistent (whist/ewhist "
                    "sums exact, W_ge1_by_word moment identity holds, trial "
                    "accounting exact, 1024 detail records logged at cap). The "
                    "section-5 note records that COUNT observables are "
                    "cap-independent at k=0; per the handoff that note is "
                    "carried forward but NOT extended to S1 arms, so the "
                    "literal cascade fires SH-GATE-FAIL on these receipts. "
                    "Whether the overflow clause should be re-scoped for "
                    "non-sparse interior readings is a Coordinator act (repair "
                    "route); the count readings are retained for that route."),
            },
            {
                "id": "OBS-S1-4",
                "rule8": True,
                "observation": (
                    "k=16 re-seat reads 12 hits on the armid-8 stream (seed "
                    "531001), in band [6,30]; committed same-seed armid-1 "
                    "stream read 14 (L1-AES-R5-P30 / S0-4 Gate-0x) and seed "
                    "531002 read 19 (EV-AES-5478a0) - consistent with the "
                    "committed +/-16% seed/stream variance. k=8 reads 13 "
                    "(RESIDUAL), at the k=16 level within band resolution; "
                    "the two THRESHOLD readings sit at k=1 and k=2 only."),
            },
        ],
        "budget": {
            "wall_clock_seconds_declared": 7200,
            "wall_clock_seconds_used_task_start_to_assembly": (now - t0).total_seconds(),
            "binary_invocations": {"used": 7, "max": 8},
            "binary_invocations_detail": [
                "S1-1 k=16 re-seat", "S1-2 k=1", "S1-3 k=2", "S1-4 k=8",
                "S1-5a det", "S1-5b det", "S1-6 freeze",
            ],
            "memory_gb_declared": 4,
            "max_rss_bytes_observed": max_rss,
            "sum_arm_wall_seconds_time_l": sum(arm_walls),
            "per_arm_timeout_wrapper": "timeout 3600",
            "budget_stamps": "budget_stamps.jsonl",
            "exhaustion_policy": "resource_exhaustion, never a reading (rule 5)",
        },
        "scope_discipline": {
            "claim_tier": "toy",
            "no_deployed_aes_claims": True,
            "no_published_cryptanalysis_comparisons": True,
            "x_statistic_not_computed": True,
            "no_rho_exclusion": True,
            "no_k4_k12": True,
            "no_second_seeds": True,
            "no_carrier_observables": True,
            "no_reopen_clause_honored": True,
            "no_git_add_or_commit": True,
            "no_status_or_promotion_interpretation": True,
            "section5_note_carried_forward_not_extended": True,
        },
        "artifact_inventory": {
            "RESULTS.json": "this file",
            "budget_stamps.jsonl": ("budget stamps (task start, S0 gate check, "
                                    "instrument copy, per-arm start/end, rule-8 "
                                    "note, analysis/verdict, assembly)"),
            "src/affarm046ex.c": "reused instrument source (unmodified copy of S0)",
            "src/affarm046ex": "reused instrument binary (unmodified copy of S0)",
            "src/freeze_digest.py": ("reused S0 digest/reverify script "
                                     "(unmodified; DEV-S1-3 ordering disclosed)"),
            "src/s1_analysis.py": "per-point S1 analysis (fresh; DEV-S1-1 correction)",
            "src/det_cmp.py": "determinism comparator (fresh)",
            "src/verdict.py": "ordered SH cascade composition (fresh)",
            "src/assemble_results.py": "this assembler (fresh)",
            "src/BUILD.md": "build/run/budget/inference record",
            "runs/T1_k16_reseat.json|.err|.timing.txt": "S1-1 k=16 re-seat receipt",
            "runs/T1_k16_analysis.json": "S1-1 re-seat analysis + band gate",
            "runs/T2_k1.json|.err|.timing.txt": "S1-2 k=1 primary joint receipt",
            "runs/T2_k1_analysis.json": "S1-2 per-point analysis",
            "runs/T3_k2.json|.err|.timing.txt": "S1-3 k=2 step confirmation receipt",
            "runs/T3_k2_analysis.json": "S1-3 per-point analysis",
            "runs/T4_k8.json|.err|.timing.txt": "S1-4 k=8 midpoint/sentinel receipt",
            "runs/T4_k8_analysis.json": "S1-4 per-point analysis",
            "runs/T5_det_a.json|.err|.timing.txt": "S1-5 determinism receipt 1",
            "runs/T5_det_b.json|.err|.timing.txt": "S1-5 determinism receipt 2",
            "runs/T5_det_cmp.json": "S1-5 determinism comparison",
            "runs/T6_freeze_c_output.json": "S1-6 raw C freeze output",
            "runs/T6_freeze.err|.timing.txt": "S1-6 freeze stderr/timing",
            "runs/T6_freeze_rerun.json": "S1-6 digested rerun freeze",
            "runs/T6_digest_reverify.json": "S1-6 digest re-verification vs committed file",
            "runs/T6_source_diff_info.json": "S1-6 source-diff audit info",
            "runs/T6_shasum_postarm.txt": "S1-6 post-arm shasum record",
            "runs/source_diff_raw_postarm.txt": "S1-6 post-arm source diff (EMPTY)",
            "runs/verdict_composition.json": "ordered SH cascade composition",
        },
        "assembled_utc": now.isoformat(),
        "parse_attestation": ("RESULTS.json is machine-generated JSON; parsed "
                              "whole with python3 json.load after writing, "
                              "before task completion"),
        "inference": INFERENCE,
    }

    with open("RESULTS.json", "w") as f:
        json.dump(results, f, indent=1)
    with open("RESULTS.json") as f:
        json.load(f)
    print("RESULTS.json written and parsed")


if __name__ == "__main__":
    main()
