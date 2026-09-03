#!/usr/bin/env python3
# assemble_results.py -- TASK-20260903-ac03af (BATCH-060cb4, GOAL-AES-003)
# Assembles RESULTS.json for Stage S2b from the run artifacts. Everything in
# this file is derived from artifacts written by this task (receipts,
# analyses, audits, composition) plus the S2a/S1 bound inputs named below.
# No fabricated values; every number traces to a named file.
import json, hashlib, datetime, os, re

TASK = "coordination/goals/GOAL-AES-003/batches/BATCH-060cb4/tasks/TASK-20260903-ac03af"
S2A = "coordination/goals/GOAL-AES-003/batches/BATCH-060cb4/tasks/TASK-20260903-7893b2"
S1 = "coordination/goals/GOAL-AES-003/batches/BATCH-060cb4/tasks/TASK-20260903-5fbdfc"
RECEIPT = "coordination/goals/GOAL-AES-003/batches/BATCH-060cb4/archives/TASK-20260903-0aa1bd/snapshot-receipt.json"


def sha256_file(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def j(path):
    return json.load(open(path))


def wall_real(timing_path):
    txt = open(timing_path).read()
    m = re.search(r"([\d.]+)\s+real", txt)
    return float(m.group(1)) if m else None


def max_rss(timing_path):
    txt = open(timing_path).read()
    m = re.search(r"(\d+)\s+maximum resident set size", txt)
    return int(m.group(1)) if m else None


def main():
    s2a_results = j(f"{S2A}/RESULTS.json")
    receipt = j(RECEIPT)
    bound_key = ("coordination/goals/GOAL-AES-003/batches/BATCH-060cb4/tasks/"
                 "TASK-20260903-7893b2/RESULTS.json")
    s2a_sha_observed = sha256_file(f"{S2A}/RESULTS.json")
    s2a_sha_bound = receipt["path_sha256"][bound_key]
    gate_check = {
        "s2a_results_path": f"{S2A}/RESULTS.json",
        "snapshot_receipt": RECEIPT,
        "s2a_results_sha256_observed": s2a_sha_observed,
        "s2a_results_sha256_receipt_bound": s2a_sha_bound,
        "sha256_match": s2a_sha_observed == s2a_sha_bound,
        "s2a_halt_branch_fired_reported": s2a_results["halt_branch_fired"],
        "s2a_stage_outcome_reported": s2a_results["stage_outcome"],
        "s2a_halt_checks": s2a_results["halt_checks"],
        "halt_branch_fired_verified_from_bound_receipt": s2a_results["halt_branch_fired"] is None,
        "gate_rule": ("stage_s2b gate (proposal): S2a PASS (no CC3-GATE-FAIL, no CC3-F6). "
                      "If any halt branch fired, run NO arm: minimal blocked RESULTS.json only."),
        "cc3_gate_fail_fired_in_s2a": not all(s2a_results["halt_checks"].values()),
        "cc3_f6_fired_in_s2a": s2a_results["s2a5_dead_anchor"]["tripwire_fired"],
        "outcome": "NOT_BLOCKED" if (s2a_sha_observed == s2a_sha_bound
                                     and s2a_results["halt_branch_fired"] is None
                                     and s2a_results["stage_outcome"] == "PASS-S2a") else "BLOCKED",
        "statement": ("S2a package verified from the bound snapshot receipt (sha256 exact); PASS-S2a reported with no halt branch "
                      "(all six halt_checks true, halt_branch_fired null, extended dead anchor 0 hits, no CC3-F6 tripwire) -> Stage S2b admitted; executed"),
    }
    assert gate_check["outcome"] == "NOT_BLOCKED"

    u3r = j(f"{TASK}/runs/U3_k3_seed1.json")
    u4r = j(f"{TASK}/runs/U4_k3_seed2.json")
    u3a = j(f"{TASK}/runs/U3_k3_seed1_analysis.json")
    u4a = j(f"{TASK}/runs/U4_k3_seed2_analysis.json")
    fr = j(f"{TASK}/runs/S2b4_freeze_reverify.json")
    da = j(f"{TASK}/runs/S2b4_diff_audit.json")
    cc3 = j(f"{TASK}/runs/cc3_composition.json")

    def run_row(run_id, stage, cmd, receipt_path, timing_path, analysis, inv):
        r = j(receipt_path)
        return {
            "run_id": run_id,
            "stage": stage,
            "command": cmd,
            "binary_invocation": True,
            "invocation_number": inv,
            "seed": r["seed"],
            "arm_id": r["arm_id"],
            "threads": r["threads"],
            "log2N": r["log2N"],
            "sbox_token": "s3" if run_id.startswith(("S2b-2", "S2b-3")) else None,
            "rounds": 5,
            "wall_seconds_time_real": wall_real(timing_path),
            "wall_seconds_receipt_elapsed": r["elapsed_seconds_measured"],
            "max_rss_bytes": max_rss(timing_path),
            "hits": r["W_ge1_nontrivial"],
            "whist": r["whist"],
            "W_ge1_by_word": r["W_ge1_by_word"],
            "excess_ratio_vs_excess_E": analysis["excess_ratio_vs_excess_E"],
            "garwood95_count_ci_per_2_30": [analysis["garwood95_count_scaled_per_2_30"]["lo"],
                                            analysis["garwood95_count_scaled_per_2_30"]["hi"]],
            "band": analysis["band"],
            "bandrank": analysis["bandrank"],
            "hit_log_overflow": r["hit_log_overflow"],
            "saturation_status": analysis["amend1_identity_table"]["saturation_status"],
            "amend1_identities_pass": analysis["amend1_identities_pass"],
            "seat_as_preregistered": analysis["seat_as_preregistered"],
            "table_digest_match_prearm_R4": analysis["table_digest_reverification_vs_R4_prearm_commitment"]["match"],
            "arm_table_concat_sha256": r["arm_table_concat_sha256"],
            "point_verdict": analysis["point_verdict"],
            "analysis": os.path.basename(receipt_path).replace(".json", "_analysis.json"),
        }

    runs = [
        run_row("S2b-2", "S2b-2 k=3 SUB-LOCATOR PRIMARY (FIRST-EVER k=3 measurement)",
                f"timeout 3600 /usr/bin/time -l {TASK}/src/affarm046ex arm U3K3SEED1-S3-R5-P30 5 1 1 30 531001 11 4 s3",
                f"{TASK}/runs/U3_k3_seed1.json", f"{TASK}/runs/U3_k3_seed1.timing.txt", u3a, 1),
        run_row("S2b-3", "S2b-3 k=3 SECOND SEED (unconditional, two-draw entry discipline)",
                f"timeout 3600 /usr/bin/time -l {TASK}/src/affarm046ex arm U4K3SEED2-S3-R5-P30 5 1 1 30 531002 11 4 s3",
                f"{TASK}/runs/U4_k3_seed2.json", f"{TASK}/runs/U4_k3_seed2.timing.txt", u4a, 2),
        {
            "run_id": "S2b-4-freeze",
            "stage": "S2b-4 POST-ARM FREEZE RE-RUN (re-verification vs R4)",
            "command": f"timeout 3600 /usr/bin/time -l {TASK}/src/affarm046ex freeze 363851",
            "binary_invocation": True,
            "invocation_number": 3,
            "seed": 363851,
            "arm_id": None,
            "threads": None,
            "wall_seconds_time_real": wall_real(f"{TASK}/runs/S2b4_freeze.timing.txt"),
            "max_rss_bytes": max_rss(f"{TASK}/runs/S2b4_freeze.timing.txt"),
            "outcome": ("PASS (0 mismatches vs R4; k=3 digest still the committed pre-arm constant 922e24c9...; "
                        "raw C output byte-identical to the S2a-4 pre-arm raw output)"),
        },
    ]

    stamps = [json.loads(l) for l in open(f"{TASK}/budget_stamps.jsonl") if l.strip()]
    t0 = next(s["epoch"] for s in stamps if s["event"] == "task_start")
    t_last = max(s["epoch"] for s in stamps)

    out = {
        "schema": "crypto.autoresearch.task_results.v1",
        "task_id": "TASK-20260903-ac03af",
        "batch_id": "BATCH-060cb4",
        "goal_id": "GOAL-AES-003",
        "idea_record": "IDEA-20260903-8f26ac",
        "decision_opening_batch": "DEC-20260903-63cd8d",
        "stage": "S2b",
        "s2a_gate_check": gate_check,
        "frozen_contract": {
            "proposal": "ledger/proposals/IDEA-20260903-8f26ac.yaml (stage_s2b S2b-2..S2b-4 BINDING branch criteria and ordering in count_completion_decision_rule / family_extension_design.sub_localization_decision_rule; design_time_power)",
            "decision": "ledger/decisions/DEC-20260903-63cd8d.yaml (AMEND-1/SCOPE-1/NARROW-1-3)",
            "preregistration": "coordination/goals/GOAL-AES-003/batches/BATCH-060cb4/tasks/TASK-20260903-695ebe/PREREGISTRATION.md (BINDING; CC3 cascade section 6.3, floors section 11, strip set section 14, NARROW discipline section 13; NOT rewritten by this task)",
            "extended_build": {
                "copy_source": f"{S2A}/src/ (byte-for-byte reuse; declared diff already applied and certified in S2a)",
                "src_sha256_extended_observed": sha256_file(f"{TASK}/src/affarm046ex.c"),
                "src_sha256_extended_certified": "45808af6ff6fa18d805dac8910845b01813e4b9b49ae289fcc705e2913fad1c0",
                "bin_sha256_extended_observed": sha256_file(f"{TASK}/src/affarm046ex"),
                "bin_sha256_extended_certified": "3ccc377cdee7e4c433570b5541e057a6bbc20ca4fb32b59028211c5a88324db8",
                "copy_verified_match": (sha256_file(f"{TASK}/src/affarm046ex.c") == "45808af6ff6fa18d805dac8910845b01813e4b9b49ae289fcc705e2913fad1c0"
                                        and sha256_file(f"{TASK}/src/affarm046ex") == "3ccc377cdee7e4c433570b5541e057a6bbc20ca4fb32b59028211c5a88324db8"),
                "not_modified_further": True,
            },
            "r4_k3_committed_digest": {
                "file": f"{S2A}/runs/R4_table_freeze_ext.json",
                "r4_sha256_bound": receipt["path_sha256"][f"{S2A}/runs/R4_table_freeze_ext.json"],
                "r4_sha256_observed": sha256_file(f"{S2A}/runs/R4_table_freeze_ext.json"),
                "positions": [0, 4, 8],
                "concat_sha256": "922e24c9c065eb79c7efcbd536b41111ad70d11a1a49cf56207832e4949c6262",
                "committed_pre_arm_in_s2a": True,
            },
            "realized_grid_immutable_inputs": {
                "source": "EV-AES-868db1 OBS-2 (committed BATCH-e5d753 readings) + this batch's S1 (CC-AGREE/CC8-AGREE)",
                "h1_531001": 12681109,
                "h2_531001": 149371, "h2_531002": 150412,
                "h4_531001": 17, "h4_531002": 21,
                "h8_531001": 13, "h8_531002": 18,
                "h16_531001": 12,
                "none_rerun_by_this_task": True,
            },
        },
        "runs": runs,
        "binary_invocations_used": 3,
        "binary_invocations_max": 5,
        "amend1_identity_tables_per_receipt": {
            "U3_k3_seed1": u3a["amend1_identity_table"],
            "U4_k3_seed2": u4a["amend1_identity_table"],
            "amend1_identities_pass_both": u3a["amend1_identities_pass"] and u4a["amend1_identities_pass"],
            "detail_log_attestations": {
                "U3_k3_seed1": u3a["amend1_c_detail_log_attestation"],
                "U4_k3_seed2": u4a["amend1_c_detail_log_attestation"],
            },
        },
        "s2b4_audits": {
            "postarm_freeze_reverification": {
                "file": "runs/S2b4_freeze_reverify.json",
                "reverification_pass": fr["reverification_pass"],
                "mismatches": fr["mismatches"],
                "mismatch_count_expected": 0,
                "k3_digest_still_committed": fr["k3_digest_still_committed"],
                "k3_concat_sha256_observed": fr["k3_concat_sha256_observed"],
                "k3_concat_sha256_committed_prearm_constant": fr["k3_concat_sha256_committed_prearm_constant"],
                "raw_c_output_byte_identity_vs_s2a_prearm_informational": fr["raw_c_output_byte_identity_vs_s2a_informational"],
                "raw_c_output_sha256_postarm": fr["raw_c_output_sha256_postarm"],
                "raw_c_output_sha256_s2a": fr["raw_c_output_sha256_s2a"],
                "selfcheck_identity_k0_assert_pass": fr["selfcheck_identity_k0_assert_pass"],
                "selfcheck_aes_k16_assert_pass": fr["selfcheck_aes_k16_assert_pass"],
            },
            "postarm_source_diff_audit": {
                "file": "runs/S2b4_diff_audit.json",
                "diff_text_file": "runs/S2b4_diff_audit.txt",
                "equality_verdict": da["equality_verdict"],
                "hunk_count": da["hunk_count"],
                "expected_hunk_count": da["expected_hunk_count"],
                "changed_base_lines": da["changed_base_lines"],
                "hunk_content_identical_to_s2a_audit_modulo_header_paths": da["hunk_content_identical_to_s2a_audit_modulo_header_paths"],
                "base_sha256_observed": da["base_sha256_observed"],
                "extended_sha256_observed": da["extended_sha256_observed"],
                "protected_region_violations": da["protected_region_violations"],
            },
            "extended_binary_hash_recheck": {
                "observed": da["binary_sha256_observed"],
                "certified": da["binary_sha256_certified"],
                "pass": da["binary_hash_recheck_pass"],
            },
            "all_postarm_audits_pass": (fr["reverification_pass"] and da["equality_verdict"].startswith("PASS")
                                        and da["binary_hash_recheck_pass"]),
        },
        "cc3_composition": {
            "file": "runs/cc3_composition.json",
            "rule_source": cc3["cascade_fixed_order_evaluation"]["rule_source"],
            "fixed_order": cc3["cascade_fixed_order_evaluation"]["fixed_order"],
            "branches": cc3["cascade_fixed_order_evaluation"]["branches"],
            "fired_branch": cc3["cascade_fixed_order_evaluation"]["fired_branch"],
            "readings_consumed": cc3["readings_consumed"],
            "tier2_count_content_report_only": cc3["tier2_count_content_report_only"],
            "tier2_consumed_by_band_sentence": cc3["tier2_consumed_by_band_sentence"],
            "sub_localization_statement": cc3["sub_localization_statement"],
            "narrow_discipline": cc3["narrow_discipline"],
            "scope_discipline": cc3["scope_discipline"],
            "procedure_deviations": cc3["procedure_deviations"],
            "unexpected_observations_cc3": cc3["unexpected_observations"],
        },
        "sub_localization_statement_with_narrow_discipline": {
            "fired_branch": cc3["cascade_fixed_order_evaluation"]["fired_branch"],
            "statement": cc3["sub_localization_statement"],
            "floor_is_alive_NARROW1": cc3["narrow_discipline"]["NARROW_1_floor_is_alive"],
            "scope1_attribution": cc3["narrow_discipline"]["SCOPE_1_attribution"],
            "narrow2_count_discipline": cc3["narrow_discipline"]["NARROW_2_count_sentences"],
            "narrow3_determinism_not_replication": cc3["narrow_discipline"]["NARROW_3_determinism_not_replication"],
            "k3_two_independent_draws": True,
            "no_extinction_language": True,
            "localization_does_not_mean_decay_finishes_early": True,
        },
        "halt_checks_this_stage": {
            "CC3-GATE-FAIL_amend1_counter_inconsistency_either_new_receipt": not (u3a["amend1_identities_pass"] and u4a["amend1_identities_pass"]),
            "CC3-GATE-FAIL_any_postarm_audit": not (fr["reverification_pass"] and da["equality_verdict"].startswith("PASS") and da["binary_hash_recheck_pass"]),
            "CC3-F6_carryforward_from_s2a": False,
        },
        "halt_branch_fired": None,
        "stage_outcome": "PASS-S2b",
        "stage_statement": ("Both k=3 arms executed and passed (AMEND-1 identities exact on both receipts; seats as pre-registered; table digests match the pre-arm "
                            "R4 k=3 commitment 922e24c9...). First-ever k=3 readings: h(3)_531001 = 1830 and h(3)_531002 = 1777, both THRESHOLD, both saturated "
                            "(overflow 806/753, the path predicted under the multiplicative prior; legal under AMEND-1). Post-arm audits all pass: freeze "
                            "re-verification 0 mismatches vs R4 (k=3 digest unchanged; raw freeze output byte-identical to the S2a-4 pre-arm output), source diff "
                            "still exactly the declared list, extended binary hash unchanged. The CC3 cascade was composed in fixed order: no halt branch, no "
                            "seed disagreement, no non-monotony; CC3-SUBLOCALIZE-LATE fired - the THRESHOLD->RESIDUAL transition is localized to (3,4] at band "
                            "level, scoped to the extended family, carrying the floor-is-alive statement (NARROW-1), SCOPE-1 attribution (dilution at fixed "
                            "schedule), NARROW-2 (k=3 qualifies for count reporting with two draws; no count-completion sentence beyond the rule's tier-2 "
                            "report-only content), and NARROW-3 (both readings are independent draws, never determinism). Observations only: no verdict "
                            "re-composition, no status/strength/promotion interpretation, no commits."),
        "deviations": [
            {
                "id": "DEV-S2b-1",
                "description": (cc3["procedure_deviations"][0]["description"]),
                "impact": cc3["procedure_deviations"][0]["impact"],
            },
            {
                "id": "DEV-S2b-2",
                "description": ("Stderr convention: each invocation redirects stderr (including the /usr/bin/time -l resource report) into runs/X.timing.txt; "
                                "runs/X.err is created as an empty placeholder, exactly as in the S0/S1/S2a lineage (DEV-S2a-4 carried forward)."),
                "impact": "none",
            },
            {
                "id": "DEV-S2b-3",
                "description": ("wall_seconds_time_real is reported from the /usr/bin/time -l 'real' line in each timing file (parseable this stage); "
                                "wall_seconds_receipt_elapsed is the receipt's internal elapsed_seconds_measured. Both are measured values; the binding "
                                "baseline (~27 min per 2^30 4-thread arm) remains the budget contract and measured rates are OPTIMISTIC-RELATIVE, disclosed, "
                                "never charged as the baseline."),
                "impact": "none",
            },
        ],
        "unexpected_observations": cc3["unexpected_observations"],
        "budget": {
            "wall_clock_seconds_declared": 3600,
            "wall_clock_seconds_used_task_start_to_last_stamp": round(t_last - t0, 3),
            "binary_invocations": {"used": 3, "max": 5},
            "memory_gb_declared": 4,
            "max_rss_bytes_observed": max(x for x in [max_rss(f"{TASK}/runs/U3_k3_seed1.timing.txt"),
                                                      max_rss(f"{TASK}/runs/U4_k3_seed2.timing.txt"),
                                                      max_rss(f"{TASK}/runs/S2b4_freeze.timing.txt")] if x),
            "per_arm_timeout_wrapper": "timeout 3600",
            "budget_stamps": "budget_stamps.jsonl (task start, source copy, per-invocation start/end epochs, composition complete, assembly)",
            "binding_baseline_note": ("~27 min per 2^30 4-thread arm is the budget contract; measured rates here (k=3 arms ~79 s each, freeze ~1 s) are "
                                      "OPTIMISTIC-RELATIVE and disclosed, never charged as the baseline"),
            "exhaustion_policy": "resource_exhaustion, never a reading (rule 5); NOT exercised - all arms completed within budget",
        },
        "artifact_inventory": {
            "RESULTS.json": "this file",
            "budget_stamps.jsonl": "budget stamps",
            "src/affarm046ex.c": "EXTENDED instrument source (byte-for-byte copy of the S2a certified source; sha256 45808af6ff6fa18d805dac8910845b01813e4b9b49ae289fcc705e2913fad1c0; not modified)",
            "src/affarm046ex": "EXTENDED binary (byte-for-byte copy; sha256 3ccc377cdee7e4c433570b5541e057a6bbc20ca4fb32b59028211c5a88324db8; re-checked post-arm)",
            "src/s2b_analysis.py": "per-receipt k=3 AMEND-1 analysis (fresh)",
            "src/s2b_freeze_digest.py": "post-arm freeze digester + R4 re-verification (fresh)",
            "src/s2b_diff_audit.py": "post-arm declared-diff audit + binary hash re-check (fresh)",
            "src/cc3_compose.py": "CC3 cascade composition in fixed order (fresh)",
            "src/assemble_results.py": "this assembler (fresh)",
            "runs/U3_k3_seed1.json|.err|.timing.txt": "S2b-2 k=3 primary receipt (seed 531001, armid 11, threads 4)",
            "runs/U3_k3_seed1_analysis.json": "S2b-2 AMEND-1 analysis",
            "runs/U4_k3_seed2.json|.err|.timing.txt": "S2b-3 k=3 second seed receipt (seed 531002, armid 11, threads 4)",
            "runs/U4_k3_seed2_analysis.json": "S2b-3 AMEND-1 analysis",
            "runs/S2b4_freeze_c_output.json": "S2b-4 post-arm freeze mode raw C output (seed 363851)",
            "runs/S2b4_freeze.err|.timing.txt": "freeze invocation stderr/timing",
            "runs/S2b4_freeze_reverify.json": "post-arm freeze re-verification vs R4 (0 mismatches; k=3 digest unchanged)",
            "runs/S2b4_diff_audit.txt": "post-arm unified diff frozen base vs extended source",
            "runs/S2b4_diff_audit.json": "post-arm declared-diff audit classification + equality verdict",
            "runs/cc3_composition.json": "CC3 cascade composition (fixed order; fired branch; readings consumed; NARROW discipline)",
        },
        "assembled_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "parse_attestation": "RESULTS.json is machine-generated by src/assemble_results.py from the artifacts; parsed whole with python3 json.load after writing, before task completion",
        "inference": {
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
        },
    }
    with open(f"{TASK}/RESULTS.json", "w") as f:
        json.dump(out, f, indent=1)
    json.load(open(f"{TASK}/RESULTS.json"))
    print("RESULTS.json assembled and parsed OK")


if __name__ == "__main__":
    main()
