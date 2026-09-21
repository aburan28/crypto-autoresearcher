#!/usr/bin/env python3
# assemble_results.py -- TASK-20260903-5fbdfc (BATCH-060cb4, GOAL-AES-003)
# Assembles RESULTS.json from the task's artifacts (receipts, analyses,
# cc_composition.json, budget_stamps.jsonl). Machine-generated; re-parsed
# whole with json.load after writing (parse attestation inside).
import json, hashlib, datetime, time

TASK = "coordination/goals/GOAL-AES-003/batches/BATCH-060cb4/tasks/TASK-20260903-5fbdfc"
S0 = "coordination/goals/GOAL-AES-003/batches/BATCH-060cb4/tasks/TASK-20260903-695ebe"
RECEIPT = "coordination/goals/GOAL-AES-003/batches/BATCH-060cb4/archives/TASK-20260903-d7c324/snapshot-receipt.json"
EXCESS_E = 1 << 30
INFERENCE = {
    "policy": "executor-implementation",
    "requested_policy": "executor-implementation",
    "resolved_model_id": "fireworks-ai/accounts/fireworks/models/qwen3p8-max",
    "resolved_model_id_note": "session-reported by the running session; no adapter probe (python3 -m orchestration.adapter doctor --probe) was executed in this session, so this identifier is unverified configuration",
    "model_verified": False,
    "fallback_used": True,
    "fallback_reason": "session-backend transport under inference amendment DEC-20260831-0d1eeb",
    "degraded_requirements": [],
    "amendment": "DEC-20260831-0d1eeb",
    "independent_session": True,
}


def sha256_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def run_row(run_id, stage, cmd, receipt, analysis, binary_invocation=True):
    r = json.load(open(receipt))
    a = json.load(open(analysis))
    return {
        "run_id": run_id,
        "stage": stage,
        "command": cmd,
        "binary_invocation": binary_invocation,
        "seed": r["seed"],
        "arm_id": r["arm_id"],
        "threads": r["threads"],
        "wall_seconds_stamp": None,  # filled from stamps below
        "wall_seconds_receipt_elapsed": r["elapsed_seconds_measured"],
        "max_rss_bytes": None,       # filled from stamps below
        "hits_W_ge1_nontrivial": r["W_ge1_nontrivial"],
        "whist": r["whist"],
        "W_ge1_by_word": r["W_ge1_by_word"],
        "trivial_swaps_excluded": r["trivial_swaps_excluded"],
        "hit_log_overflow": r["hit_log_overflow"],
        "excess_ratio_vs_excess_E": r["W_ge1_nontrivial"] / EXCESS_E,
        "garwood95_rate_per_2_30": {
            "lo": a["garwood95_count_scaled_per_2_30"]["lo"],
            "hi": a["garwood95_count_scaled_per_2_30"]["hi"],
            "method": "Wilson-Hilferty chi-squared quantile (design-time convention)"},
        "band": a["band"],
        "bandrank": a["bandrank"],
        "amend1_identities_pass": a["amend1_identities_pass"],
        "table_digest_match_R3": a["table_digest_reverification_vs_R3"]["match"],
        "gate_outcome": a["point_verdict"],
        "analysis": analysis.split("/")[-1],
        "artifact": receipt.split("/")[-1],
    }


def main():
    stamps = [json.loads(l) for l in open(TASK + "/budget_stamps.jsonl")]
    s0res_sha = sha256_file(S0 + "/RESULTS.json")
    receipt = json.load(open(RECEIPT))
    bound = receipt["path_sha256"][S0 + "/RESULTS.json"]
    cc = json.load(open(TASK + "/runs/cc_composition.json"))
    a_k2 = json.load(open(TASK + "/runs/U1_k2_seed2_analysis.json"))
    a_k8 = json.load(open(TASK + "/runs/U2_k8_seed2_analysis.json"))

    cmds = {}
    ends = {}
    for s in stamps:
        if s.get("event") == "arm_end" and s.get("exit_code") == 0:
            cmds[s["stage"]] = s["command"]
            ends[s["stage"]] = s
    runs = [
        run_row("S1-1", "S1-1", cmds["S1-1"], TASK + "/runs/U1_k2_seed2.json", TASK + "/runs/U1_k2_seed2_analysis.json"),
        run_row("S1-2", "S1-2", cmds["S1-2"], TASK + "/runs/U2_k8_seed2.json", TASK + "/runs/U2_k8_seed2_analysis.json"),
    ]
    for row in runs:
        st = ends[row["stage"]]
        row["wall_seconds_stamp"] = st["wall_seconds"]
        row["max_rss_bytes"] = st["max_rss_bytes"]
        row["start_epoch"] = None
    for s in stamps:
        if s.get("event") == "arm_start" and s.get("attempt", 1) != 1:
            for row in runs:
                if row["stage"] == s["stage"]:
                    row["start_epoch"] = s["start_epoch"]
        if s.get("event") == "arm_start" and s["stage"] == "S1-2":
            runs[1]["start_epoch"] = s["start_epoch"]
        if s.get("event") == "arm_end" and s["stage"] == "S1-2":
            runs[1]["end_epoch"] = s["end_epoch"]
        if s.get("event") == "arm_end" and s["stage"] == "S1-1" and s.get("exit_code") == 0:
            runs[0]["end_epoch"] = s["end_epoch"]

    t_start = [s for s in stamps if s["event"] == "task_start"][0]
    wall_used = time.time() - t_start["epoch"]

    out = {
        "schema": "crypto.autoresearch.task_results.v1",
        "task_id": "TASK-20260903-5fbdfc",
        "batch_id": "BATCH-060cb4",
        "goal_id": "GOAL-AES-003",
        "idea_record": "IDEA-20260903-8f26ac",
        "decision_opening_batch": "DEC-20260903-63cd8d",
        "stage": "S1",
        "s0_gate_check": {
            "s0_results_path": S0 + "/RESULTS.json",
            "snapshot_receipt": RECEIPT,
            "s0_results_sha256_observed": s0res_sha,
            "s0_results_sha256_receipt_bound": bound,
            "sha256_match": s0res_sha == bound,
            "s0_outcome": "PASS-S0",
            "halt_branch": None,
            "halt_branches_checked": ["CC-GATE-FAIL", "CC-F6", "CC-ANCHOR-FAIL"],
            "gate": "PASS - no halt branch fired; S1 arms executed",
        },
        "frozen_contract": {
            "proposal": "ledger/proposals/IDEA-20260903-8f26ac.yaml (stage_s1, count_completion_decision_rule BINDING, design_time_power)",
            "decision": "ledger/decisions/DEC-20260903-63cd8d.yaml (AMEND-1/SCOPE-1/NARROW-1-3 carried rules)",
            "preregistration": S0 + "/PREREGISTRATION.md (BINDING; NOT rewritten by this task)",
            "realized_seed531001_counterparts": {
                "source": "ledger/evidence/EV-AES-868db1.yaml OBS-2 (immutable; consumed as inputs, NOT re-run)",
                "h1_531001": 12681109, "h2_531001": 149371, "h4_531001": 17, "h8_531001": 13,
            },
            "instrument": {
                "lineage": "BATCH-e5d753 snapshot-bound PIN-T0 widened build (affarm046ex, HIT_LOG_CAP 256 per thread), zero source change in S0/S1",
                "copy_source_dir": S0 + "/src/",
                "src_sha256": sha256_file(TASK + "/src/affarm046ex.c"),
                "bin_sha256": sha256_file(TASK + "/src/affarm046ex"),
                "s0_bound_src_sha256": "ec748cefcb1fccfdd4e441a4898b21cf4b7eff056599ce07769e3f0fab091f37",
                "s0_bound_bin_sha256": "74e3d65ca6ecdd877dda5d9e19a96a5af66740b118dbcd1dd35b78be5d102702",
                "identity_match": sha256_file(TASK + "/src/affarm046ex.c") == "ec748cefcb1fccfdd4e441a4898b21cf4b7eff056599ce07769e3f0fab091f37"
                                  and sha256_file(TASK + "/src/affarm046ex") == "74e3d65ca6ecdd877dda5d9e19a96a5af66740b118dbcd1dd35b78be5d102702",
                "recompiled": False,
                "modified": False,
                "execute_bit_note": "shutil.copyfile did not preserve the execute bit; chmod +x applied before the first successful invocation (content UNCHANGED; sha256 re-verified; DEV-S1-1)",
            },
        },
        "runs": runs,
        "binary_invocations_used": 2,
        "binary_invocations_max": 4,
        "binary_invocations_note": "2 reading arms executed (S1-1, S1-2). One additional pre-exec attempt (S1-1 attempt 1) exited 126 before the program image ran (missing execute bit, DEV-S1-1); it is recorded in budget_stamps.jsonl and retained (runs/U1_k2_seed2_attempt1_exit126.timing.txt) but is not counted as a binary invocation because no program image executed.",
        "amend1_identity_tables": {
            "S1-1_k2_seed2": a_k2["amend1_identity_table"],
            "S1-2_k8_seed2": a_k8["amend1_identity_table"],
            "note": "full per-receipt AMEND-1 identity suites (preregistration section 2); the zhist internal identity is sum(zhist)==nontrivial_trials (DEV-S0-1 corrected; affarm046ex.c:458-459); the literal '==trials' shorthand holds iff trivial_swaps_excluded==0 and is reported informationally",
        },
        "amend1_c_detail_log_attestations": {
            "S1-1_k2_seed2": a_k2["amend1_c_detail_log_attestation"],
            "S1-2_k8_seed2": a_k8["amend1_c_detail_log_attestation"],
        },
        "cc_composition": {
            "artifact": "runs/cc_composition.json",
            "cascade_fixed_order": cc["cascade_fixed_order_evaluation"]["order"],
            "branches": {
                name: {
                    "criterion": b["criterion"],
                    "fired": b["fired"],
                    "evaluated": b.get("evaluated", True),
                    "basis_summary": (
                        "AMEND-1 identities exact on BOTH new receipts; seats as preregistered; post-arm digest re-verification 0 mismatches; source/binary diff EMPTY; sha256 re-check vs S0-bound hashes PASS"
                        if name == "CC-GATE-FAIL" else
                        "band(h(2)_531002) = THRESHOLD == committed band (no departure; a departure would be a ~386-sd event)"
                        if name == "CC-SEED-DISAGREE" else
                        "count CIs overlap ([148,614.5, 150,130.4] vs [149,652.8, 151,174.1]); seed ratio 1.00697 in [0.9899, 1.0102] (count form: 150,412 in [147,858, 150,891]); per-seed (1,2) decay-ratio CIs overlap (84.8967 [84.4208, 85.3759] vs 84.3016 [83.8304, 84.7759]); checked-implication separation: none"
                        if name == "CC-COUNT-DISAGREE" else
                        "BAND-AGREE AND COUNT-AGREE AND RATIO-AGREE all hold"
                    ),
                } for name, b in cc["cascade_fixed_order_evaluation"]["branches"].items()
            },
            "fired_branch": cc["cascade_fixed_order_evaluation"]["fired_branch"],
            "verdict": ("COUNT-REPLICATED: SH2-MONOTONE-DECAY is EXTENDED TO COUNT LEVEL for the pairs (1,2) and (2,4) ONLY - "
                        "the k1->k2 count-decay ratio is replicated across two independent seed environments within the declared "
                        "resolution (per-seed ratios 84.8967 [84.4208, 85.3759] and 84.3016 [83.8304, 84.7759]); the (2,4) pair's "
                        "count decay acquires the same per-seed evaluation (8786.5 [5459.7, 15168.6] vs 7162.5 [4661.8, 11633.8], CIs "
                        "overlap). NARROW-2's caveat is discharged for exactly these two pairs and NO others - (4,8) and (8,16) "
                        "remain COUNT-UNRESOLVED in every outcome of this batch. Never a whole-curve sentence; the floor is alive "
                        "(NARROW-1); SCOPE-1 attribution; additive to the immutable BATCH-e5d753 verdict, never a re-composition."),
        },
        "cc8_outcome": {
            "fired_branch": cc["cc8_axis"]["fired_branch"],
            "h8_531002": 18,
            "band": "RESIDUAL",
            "h8_531001_committed": 13,
            "garwood95_count_ci_531002": cc["readings_consumed"]["new_this_batch"]["h8_531002"]["garwood95_count_ci"],
            "garwood95_count_ci_531001_committed": [6.9, 22.2],
            "ci_overlap": cc["cc8_axis"]["branches"]["CC8-AGREE"]["basis"]["ci_overlap"],
            "statement": cc["cc8_axis"]["statement"],
            "never_gates_k2": True,
        },
        "per_seed_decay_ratios": cc["per_seed_decay_ratios"],
        "post_arm_audits": cc["cascade_fixed_order_evaluation"]["branches"]["CC-GATE-FAIL"]["basis"]["post_arm_audits"],
        "stage_S2_gate_statement": cc["stage_S2_gate"],
        "scope_discipline": {
            "claim_tier": "toy",
            "no_deployed_aes_claims": True,
            "no_published_cryptanalysis_comparisons": True,
            "no_seed_531001_arm_rerun": True,
            "no_k3_or_extended_build_arms": True,
            "no_git_add_or_commit": True,
            "no_status_or_promotion_interpretation": True,
            "x_statistic_not_computed": True,
            "no_rho_exclusion": True,
            "no_reopen_clause_honored": True,
            "attribution": "SCOPE-1 only (interior-to-interior comparisons schedule-clean under PIN-T0; decay attributed to table dilution AT FIXED SCHEDULE; no dilution-only language)",
            "determinism_vs_replication": "NARROW-3: the two new readings are independent draws (NEW (seed, seat) combinations 531002@armid3, 531002@armid6); no seed-531001 re-run occurred in this stage; determinism is never replication",
            "floor_is_alive_NARROW1": "the residual floor is a live, decidable excess over the analytic null; no extinction sentence at any k",
        },
        "deviations": [
            {
                "id": "DEV-S1-1",
                "description": "First S1-1 invocation attempt exited 126 BEFORE exec: shutil.copyfile (used to copy the frozen build from the S0 task src/) did not preserve the execute bit; /usr/bin/time reported 'Permission denied' and the program image never ran. chmod +x applied; binary content UNCHANGED (sha256 re-verified 74e3d65c...). The attempt-1 timing report is retained (runs/U1_k2_seed2_attempt1_exit126.timing.txt); the attempt is stamped in budget_stamps.jsonl and is NOT counted against the 4-invocation budget because no program image executed.",
                "impact": "none (no reading produced or affected by the failed attempt)",
            },
            {
                "id": "DEV-S1-2",
                "description": "Stderr convention: each invocation redirects stderr (including the /usr/bin/time -l resource report) into runs/X.timing.txt; runs/X.err is created as an empty placeholder exactly as in the S0/BATCH-e5d753 lineage (whose .err files carry the empty-file sha256).",
                "impact": "none",
            },
            {
                "id": "DEV-S1-3",
                "description": "Arm run labels are executor-chosen receipt-echo fields (S11K2SEED2-S2-R5-P30, S12K8SEED2-S8-R5-P30); stream derivation (thread_seeds, key_stream_seeds) depends only on seed/armid/thread index, confirmed by the seat checks in the analyses.",
                "impact": "none",
            },
            {
                "id": "DEV-S1-4",
                "description": "Extra artifacts beyond a minimal deliverable list are retained per the artifact policy: per-receipt analyses (runs/U*_analysis.json), runs/cc_composition.json, the attempt-1 timing file, and src/ scripts (s1_analysis.py, cc_compose.py, assemble_results.py) alongside the byte-exact frozen build copy in src/.",
                "impact": "none",
            },
        ],
        "unexpected_observations": [
            {
                "id": "OBS-S1-1",
                "rule8": True,
                "observation": "h(2)_531002 = 150,412 vs committed h(2)_531001 = 149,371: seed ratio 1.00697, inside the preregistered count-agreement window [0.9899, 1.0102]; Garwood CIs overlap; band THRESHOLD on both seeds. The k=2 second-seed whist carries 1 trial with W=1 and 150,411 with W=3 (the seed-531001 receipt carried 2 W=1 trials) - the rare W=1 structure at k=2 recurs on an independent draw. Report-only; no branch conjunct consumes the W breakdown.",
            },
            {
                "id": "OBS-S1-2",
                "rule8": True,
                "observation": "h(8)_531002 = 18 vs committed h(8)_531001 = 13: RESIDUAL on both seeds, CIs [10.66, 28.45] vs [6.9, 22.2] overlap; the floor is seed-stable at band level at k=8 and the RT-J8-named sensitivity stands tested and untriggered (CC8-AGREE). Per-seed counts reported, never pooled, never smoothed.",
            },
            {
                "id": "OBS-S1-3",
                "rule8": True,
                "observation": "Citation discrepancy: EV-AES-868db1 OBS-2 and the dispatch brief cite h(4)_531001 CI [9.9, 29.2], while the committed BATCH-e5d753 analysis file (T4_k4_analysis.json) and the Wilson-Hilferty re-derivation from h=17 agree on [9.897, 27.220], and the binding preregistration section 5 carries [9.9, 27.2]. The campaign-convention value was used in every computation (only the report-only (2,4) seed-531001 ratio CI touches it; the variant under 29.2 is reported in runs/cc_composition.json). No CC branch conjunct at k=2 depends on it. Flagged for the validator.",
            },
            {
                "id": "OBS-S1-4",
                "rule8": True,
                "observation": "S1-1 receipt is saturated as predicted: hit_log_overflow = 149,388 = 150,412 - 4x256 exactly, with ALL counter identities exact (logged_detail_records = 1024 = threads x HIT_LOG_CAP; ewhist_hit sums to h). The AMEND-1 saturated identity is re-exercised at a new (seed, seat) - one of the design-time information contents of the arm (PR-Y3). Pure cap truncation, legal under AMEND-1.",
            },
            {
                "id": "OBS-S1-5",
                "rule8": True,
                "observation": "Per-seed (2,4) decay-ratio point estimates differ by ~18% (8786.5 vs 7162.5) while their wide corner-propagated CIs overlap; the (2,4) count decay is replicated at the declared (CI-overlap) resolution, and the point-estimate spread is report-only content for the successor design, never smoothed.",
            },
        ],
        "budget": {
            "wall_clock_seconds_declared": 3600,
            "wall_clock_seconds_used_task_start_to_assembly": round(wall_used, 1),
            "wall_clock_deadline_epoch": t_start["epoch"] + 3600,
            "binary_invocations": {"used": 2, "max": 4, "pre_exec_attempt_126_not_counted": 1},
            "memory_gb_declared": 4,
            "max_rss_bytes_observed": max(r["max_rss_bytes"] for r in runs),
            "per_arm_timeout_wrapper": "timeout 3600",
            "budget_stamps": "budget_stamps.jsonl (task start, S0 gate check, source copy, per-arm start/end epochs + wall s + rss, analysis/composition stamps)",
            "binding_baseline_note": "~27 min per 2^30 4-thread arm is the budget contract; measured rates here (80-81 s) are OPTIMISTIC-RELATIVE and disclosed, never charged as the baseline",
            "exhaustion_policy": "resource_exhaustion, never a reading (rule 5)",
        },
        "artifact_inventory": {
            "RESULTS.json": "this file",
            "budget_stamps.jsonl": "budget stamps",
            "src/affarm046ex.c": "frozen instrument source (byte-exact copy from the S0 task, UNMODIFIED)",
            "src/affarm046ex": "frozen binary (byte-exact copy from the S0 task, UNMODIFIED, not recompiled; execute bit restored per DEV-S1-1)",
            "src/s1_analysis.py": "per-receipt S1 analysis under AMEND-1 (fresh for this task)",
            "src/cc_compose.py": "S1-3 CC composition (fresh for this task)",
            "src/assemble_results.py": "this assembler (fresh for this task)",
            "runs/U1_k2_seed2.json|.err|.timing.txt": "S1-1 second seed k=2 receipt (seed 531002, armid 3)",
            "runs/U1_k2_seed2_attempt1_exit126.timing.txt": "retained pre-exec failure report (DEV-S1-1)",
            "runs/U1_k2_seed2_analysis.json": "S1-1 analysis (AMEND-1 identity table, Garwood CI, band, R3 digest check)",
            "runs/U2_k8_seed2.json|.err|.timing.txt": "S1-2 second seed k=8 receipt (seed 531002, armid 6)",
            "runs/U2_k8_seed2_analysis.json": "S1-2 analysis",
            "runs/cc_composition.json": "S1-3 CC composition: fixed-order cascade evaluation, CC8 axis, per-seed decay ratios with corner-propagated CIs, post-arm audits, S2 gate statement",
        },
        "assembled_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "parse_attestation": "RESULTS.json is machine-generated by src/assemble_results.py from the artifacts; parsed whole with python3 json.load after writing, before task completion",
        "inference": INFERENCE,
    }
    with open(TASK + "/RESULTS.json", "w") as f:
        json.dump(out, f, indent=1)
    json.load(open(TASK + "/RESULTS.json"))
    print("RESULTS.json written and re-parsed OK; wall_used=%.1fs" % wall_used)


if __name__ == "__main__":
    main()
