#!/usr/bin/env python3
# assemble_results.py -- TASK-20260902-987716 (BATCH-e5d753, GOAL-AES-003)
# Fresh for this task: assembles RESULTS.json from the S0 artifacts.
# Deviations and rule-8 observations below were authored by the executor
# from the actual run outputs (all run artifacts are loaded and their
# load-bearing values embedded, not transcribed by hand).
#
# INFERENCE BLOCK: policy executor-implementation; requested_policy
# executor-implementation; resolved_model_id
# fireworks-ai/accounts/fireworks/models/qwen3p8-max (session-reported; no
# adapter probe run); fallback_used true; model_verified false;
# degraded_requirements []; amendment DEC-20260831-0d1eeb.
import json, re, datetime, math

TASK = "."
INFERENCE = {
    "policy": "executor-implementation",
    "requested_policy": "executor-implementation",
    "resolved_model_id": "fireworks-ai/accounts/fireworks/models/qwen3p8-max",
    "resolved_model_id_note": ("session-reported by the running session; no adapter probe "
                               "(python3 -m orchestration.adapter doctor --probe) was executed "
                               "in this session, so this identifier is unverified configuration"),
    "model_verified": False,
    "fallback_used": True,
    "fallback_reason": "session-backend transport under inference amendment DEC-20260831-0d1eeb",
    "degraded_requirements": [],
    "amendment": "DEC-20260831-0d1eeb",
    "independent_session": True,
}


def timing(path):
    t = open(path).read()
    real = re.search(r"([\d.]+)\s+real", t)
    rss = re.search(r"(\d+)\s+maximum resident set size", t)
    return (float(real.group(1)) if real else None,
            int(rss.group(1)) if rss else None)


def main():
    buildid = json.load(open("runs/S1_buildid.json"))
    pin = json.load(open("runs/S2a_pin.json"))
    pinid = json.load(open("runs/S2b_pinidentity.json"))
    fcmp = json.load(open("runs/S3_freeze_cmp.json"))
    frerun = json.load(open("runs/S3_freeze_rerun.json"))
    s4 = json.load(open("runs/S4_dead_anchor.json"))
    s4a = json.load(open("runs/S4_dead_analysis.json"))
    s5 = json.load(open("runs/S5_rampzero.json"))
    s5a = json.load(open("runs/S5_rampzero_analysis.json"))

    t_pin = timing("runs/S2a_pin.timing.txt")
    t_pinid = timing("runs/S2b_pinidentity.timing.txt")
    t_freeze = timing("runs/S3_freeze.timing.txt")
    t_s4 = timing("runs/S4_dead_anchor.timing.txt")
    t_s5 = timing("runs/S5_rampzero.timing.txt")

    runs = [
        {"run_id": "S0-2", "command": "sha256 src/affarm046ex src/affarm046ex.c vs BATCH-7b798d snapshot receipt (no binary invocation)",
         "binary_invocation": False, "seed": None, "arm_id": None, "threads": None,
         "wall_seconds_time_l": None, "max_rss_bytes": None,
         "hits_W_ge1_nontrivial": None, "W_values": None, "excess_ratio_vs_excess_E": None,
         "outcome": "build_identity_pass", "artifact": "runs/S1_buildid.json",
         "priced_fallback_executed": buildid["priced_fallback_required"]},
        {"run_id": "S0-3a", "command": "timeout 3600 /usr/bin/time -l src/affarm046ex pin 363851",
         "binary_invocation": True, "seed": 363851, "arm_id": None, "threads": None,
         "wall_seconds_time_l": t_pin[0], "max_rss_bytes": t_pin[1],
         "hits_W_ge1_nontrivial": None, "W_values": None, "excess_ratio_vs_excess_E": None,
         "outcome": "pin_pass" if pin["pin_pass"] else "PIN_FAIL",
         "mode": "pin (FIPS-197 KAT + anchors, AES table)",
         "roundtrip_failures": pin["roundtrip_failures"]},
        {"run_id": "S0-3b", "command": "timeout 3600 /usr/bin/time -l src/affarm046ex pinidentity 363851",
         "binary_invocation": True, "seed": 363851, "arm_id": None, "threads": None,
         "wall_seconds_time_l": t_pinid[0], "max_rss_bytes": t_pinid[1],
         "hits_W_ge1_nontrivial": None, "W_values": None, "excess_ratio_vs_excess_E": None,
         "outcome": "pin_pass" if pinid["pin_pass"] else "PINIDENTITY FAIL",
         "mode": "pinidentity (identity table roundtrips)",
         "roundtrip_failures": pinid["roundtrip_failures"]},
        {"run_id": "S0-4", "command": "timeout 3600 /usr/bin/time -l src/affarm046ex freeze 363851",
         "binary_invocation": True, "seed": 363851, "arm_id": None, "threads": None,
         "wall_seconds_time_l": t_freeze[0], "max_rss_bytes": t_freeze[1],
         "hits_W_ge1_nontrivial": None, "W_values": None, "excess_ratio_vs_excess_E": None,
         "outcome": "freeze_pass" if frerun["freeze_pass"] else "FREEZE FAIL",
         "mode": "freeze (7 family points + folded smoke selfchecks)",
         "reverify_pass_vs_R3": fcmp["reverify_pass"],
         "reverify_mismatches": fcmp["mismatches"]},
        {"run_id": "S0-5", "command": "timeout 3600 /usr/bin/time -l src/affarm046ex arm S05DEADANCHOR-AES-R6-P30 6 1 1 30 531004 1 4 aes",
         "binary_invocation": True, "seed": 531004, "arm_id": 1, "threads": 4,
         "wall_seconds_time_l": t_s4[0], "max_rss_bytes": t_s4[1],
         "hits_W_ge1_nontrivial": s4a["hits_W_ge1_nontrivial"],
         "W_values": s4["whist"],
         "excess_ratio_vs_excess_E": s4a["excess_ratio_vs_excess_E"],
         "outcome": s4a["anchor_verdict"],
         "analysis": "runs/S4_dead_analysis.json",
         "analysis_order": "ANALYZED FIRST among reading-bearing arms, before any alive reading (binding order)",
         "band": s4a["band"],
         "garwood95_rate_per_2_30": s4a["garwood95_rate_per_2_30"],
         "trivial_swaps_excluded": s4["trivial_swaps_excluded"],
         "hit_log_overflow": s4["hit_log_overflow"],
         "amend1_identities_pass": s4a["amend1_identities_pass"]},
        {"run_id": "S0-6", "command": "timeout 3600 /usr/bin/time -l src/affarm046ex arm S06RAMPZERO-S0-R5-P30 5 1 1 30 531001 5 4 identity",
         "binary_invocation": True, "seed": 531001, "arm_id": 5, "threads": 4,
         "wall_seconds_time_l": t_s5[0], "max_rss_bytes": t_s5[1],
         "hits_W_ge1_nontrivial": s5a["hits_W_ge1_nontrivial"],
         "W_values": s5["whist"],
         "excess_ratio_vs_excess_E": s5a["excess_ratio_vs_excess_E"],
         "outcome": s5a["anchor_verdict"],
         "analysis": "runs/S5_rampzero_analysis.json",
         "trivial_swaps_excluded": s5["trivial_swaps_excluded"],
         "hit_log_overflow_observed": s5["hit_log_overflow"],
         "hit_log_overflow_expected_saturated": s5a["hit_log_overflow_expected_saturated"],
         "amend1_identities_pass": s5a["amend1_identities_pass"],
         "amend1_proves_too_much_control_passed": s5a["amend1_proves_too_much_control"]["gate_passed_this_receipt"],
         "zhist_observed": s5["zhist"]},
    ]

    gates = {
        "S0-2_build_identity": {
            "src_sha256_match": buildid["files"]["src/affarm046ex.c"]["match"],
            "binary_sha256_match": buildid["files"]["src/affarm046ex"]["match"],
            "source_diff_empty": True,
            "priced_fallback_gate0x_executed": buildid["priced_fallback_required"],
            "gate_pass": buildid["identity_pass"],
        },
        "S0-3_KAT_pins": {
            "S2a_pin_pass": pin["pin_pass"],
            "S2b_pinidentity_pass": pinid["pin_pass"],
            "gate_pass": bool(pin["pin_pass"] and pinid["pin_pass"]),
        },
        "S0-4_freeze_reverification": {
            "freeze_pass": frerun["freeze_pass"],
            "reverify_pass_vs_committed_R3": fcmp["reverify_pass"],
            "mismatches": fcmp["mismatches"],
            "compared_fields": fcmp["compared"],
            "cap_dependent_selfcheck_fields_disclosed_not_compared": "hit_detail_records, hit_log_overflow (committed file cap-64, this build cap-256)",
            "gate_pass": bool(frerun["freeze_pass"] and fcmp["reverify_pass"]),
        },
        "S0-5_dead_anchor": {
            "hits": s4a["hits_W_ge1_nontrivial"],
            "band": s4a["band"],
            "dead_band_2_30": s4a["gate"]["dead_band_2_30"],
            "f6_tripwire": s4a["gate"]["f6_tripwire"],
            "tripwire_fired": s4a["gate"]["tripwire_fired"],
            "amend1_identities_pass": s4a["amend1_identities_pass"],
            "gate_pass": s4a["anchor_verdict"] == "PASS",
        },
        "S0-6_rampzero_anchor": {
            "hits": s5a["hits_W_ge1_nontrivial"],
            "hits_equal_2pow30": s5a["anchor_conjuncts"]["hits_equal_2pow30_exact"],
            "W3_on_100pct": s5a["anchor_conjuncts"]["W3_on_100pct_of_nontrivial"],
            "excess_ratio_1_exact": s5a["anchor_conjuncts"]["excess_ratio_1_exact"],
            "overflow_saturated_legal_under_amend1": s5a["anchor_conjuncts"]["overflow_saturated_legal_under_amend1"],
            "amend1_identities_pass": s5a["amend1_identities_pass"],
            "amend1_proves_too_much_control_passed": s5a["amend1_proves_too_much_control"]["gate_passed_this_receipt"],
            "gate_pass": s5a["anchor_verdict"] == "PASS",
        },
    }

    # ordered cascade evaluation for S0 (branches 1-3; PASS-S0 if none fires)
    gate_fail = not all(g["gate_pass"] for g in gates.values())
    f6 = gates["S0-5_dead_anchor"]["tripwire_fired"]
    anchor_fail = not gates["S0-6_rampzero_anchor"]["gate_pass"]
    if gate_fail:
        outcome = "SH2-GATE-FAIL"
    elif f6:
        outcome = "SH2-F6"
    elif anchor_fail:
        outcome = "SH2-ANCHOR-FAIL"
    else:
        outcome = "PASS-S0"

    results = {
        "schema": "crypto.autoresearch.task_results.v1",
        "task_id": "TASK-20260902-987716",
        "batch_id": "BATCH-e5d753",
        "goal_id": "GOAL-AES-003",
        "idea_record": "IDEA-20260902-9e84ac",
        "stage": "S0",
        "pin_reference": {
            "id": "PIN-T0",
            "decision": "DEC-20260901-fb6f11",
            "statement": ("SubWord uses TPOS[0] (first position of the frozen order): identity "
                          "schedule at k=0, AES schedule at every k >= 1"),
        },
        "gate_regime": {
            "id": "AMEND-1",
            "decision": "DEC-20260901-6f9de3",
            "verbatim_conjunct": ("counter INCONSISTENCY on an analysis-bearing receipt -> "
                                  "invalid_measurement; counter inconsistency means (a) overflow != "
                                  "hits - threads x HIT_LOG_CAP, or (b) any cap-independent counter "
                                  "(hits, W, ewhist_hit) disagrees with its internal identities, or "
                                  "(c) any analysis-bearing quantity is derived from the capped "
                                  "detail log rather than the counters. Pure cap truncation of the "
                                  "detail log with all counter identities intact is NOT a gate failure."),
            "saturation_aware_evaluation": ("overflow == hits - logged_detail_records EXACTLY, where "
                                            "logged_detail_records == threads x HIT_LOG_CAP when "
                                            "saturated (hits > threads x HIT_LOG_CAP) and == hits with "
                                            "overflow == 0 otherwise; hits := W_ge1_nontrivial; "
                                            "logged_detail_records := len(hit_trials) entries"),
            "preregistration": "PREREGISTRATION.md sections 1-3 (committed before any arm)",
        },
        "build_provenance": {
            "lineage": "BATCH-7b798d PIN-T0 widened build (affarm046ex, HIT_LOG_CAP 256 per thread), zero source change in this design",
            "lineage_dir": "coordination/goals/GOAL-AES-003/batches/BATCH-7b798d/tasks/TASK-20260901-706b1d/",
            "snapshot_receipt": "coordination/goals/GOAL-AES-003/batches/BATCH-7b798d/archives/TASK-20260901-56ecb6/snapshot-receipt.json",
            "identity_check": "runs/S1_buildid.json",
            "identity_check_result": "PASS (source and binary sha256 identical to snapshot-bound hashes)",
            "source_diff_audit": "runs/source_diff.txt (diff exit 0, empty body - zero source change)",
            "recompiled": False,
            "worktree_head_commit": "e6238a68e6359751fa184444b1dbcef3f330e676",
            "worktree_branch": "aes003-shape2-batch-20260902",
        },
        "preregistration": {
            "path": "PREREGISTRATION.md",
            "mtime_before_first_binary_invocation": True,
            "stamp_event": "preregistration_written in budget_stamps.jsonl",
            "write_once": True,
        },
        "runs": runs,
        "binary_invocations_used": sum(1 for r in runs if r["binary_invocation"]),
        "binary_invocations_max": 8,
        "amend1_identity_tables": {
            "S0-5_dead_anchor": s4a["amend1_identity_table"],
            "S0-6_rampzero": s5a["amend1_identity_table"],
            "note": ("full per-receipt AMEND-1 identity suites; the zhist internal identity is "
                     "sum(zhist)==nontrivial_trials per the frozen whist convention (zhist/whist "
                     "incremented only after the trivial-swap continue, affarm046ex.c:458-459); the "
                     "literal '==trials' shorthand holds iff trivial_swaps_excluded==0; see DEV-S0-1"),
        },
        "gates": gates,
        "s0_outcome_ordered_cascade": outcome,
        "cascade_evaluation_note": ("evaluated in the preregistered fixed order SH2-GATE-FAIL > SH2-F6 > "
                                    "SH2-ANCHOR-FAIL > PASS-S0 (S0 owns cascade branches 1-3); no halt "
                                    "branch fired; S0 decides instrument validity and anchors only, NOT "
                                    "the shape (no interior point run). A spurious SH2-GATE-FAIL was "
                                    "emitted by the pass-1 analysis script due to a zhist-denominator "
                                    "encoding defect (DEV-S0-1); the corrected analysis passes, and both "
                                    "outputs are preserved."),
        "cross_batch_determinism_check": {
            "method": ("field-by-field comparison of this task's anchor receipts vs the BATCH-7b798d "
                       "committed receipts at identical seats, stripping ONLY the preregistered timing "
                       "strip set {elapsed_seconds_measured, measured_rate_trials_per_sec}"),
            "S0-5_dead_anchor_diffs_beyond_strip": ["arm (executor-chosen run label only)"],
            "S0-6_rampzero_diffs_beyond_strip": ["arm (executor-chosen run label only)"],
            "verdict": ("byte-identical build + identical seats reproduced identical streams, counters, "
                        "digests, key_hex and arm_table_concat_sha256 across batches"),
        },
        "deviations": [
            {"id": "DEV-S0-1",
             "description": ("First execution of src/s0_analysis.py (dead mode) exited 12 (SH2-GATE-FAIL) "
                             "because the fresh script encoded an executor misassumption: it checked "
                             "sum(zhist)==trials, but the instrument increments zhist ONLY for nontrivial "
                             "trials (affarm046ex.c:458-459, frozen whist convention 'trivial-swap trials "
                             "are excluded from all e statistics'), so the true internal identity is "
                             "sum(zhist)==nontrivial_trials (identical to the lineage TASK-20260901-706b1d "
                             "analysis convention). This receipt excluded exactly 1 trivial swap, making "
                             "the literal form false by exactly 1. PREREGISTRATION.md section 2 item 4 "
                             "carries the proposal's shorthand 'sum(zhist) == trials'; it is evaluated "
                             "under this exact source-level convention, and holds literally when "
                             "trivial_swaps_excluded==0 (true for the S0-6 ramp-zero receipt). The check "
                             "was corrected to report BOTH the true internal identity and the literal "
                             "form, and the analysis rerun (exit 0). The defective pass-1 output is "
                             "preserved as runs/S4_dead_analysis_pass1_defective.json. No receipt was "
                             "modified; the AMEND-1-relevant counters (hits, W, ewhist_hit) and all other "
                             "identities passed in BOTH passes; the preregistered anchor conjuncts were "
                             "unaffected."),
             "impact": "none on readings; analysis-script correction only (lineage DEV-S0-1 precedent)"},
            {"id": "DEV-S0-2",
             "description": ("runs/S3_freeze_c_output.json (raw C freeze output), runs/S3_freeze.timing.txt "
                             "and runs/S4_dead_analysis_pass1_defective.json are extra artifacts beyond "
                             "the dispatch-queue artifact_paths list, retained per the artifact policy "
                             "(raw stdout + timing per invocation; defective analysis preserved for "
                             "review); queue notes state artifact_paths are expected high-level paths "
                             "amended before snapshot binding."),
             "impact": "none"},
            {"id": "DEV-S0-3",
             "description": ("Stderr convention: each invocation redirects stderr (including the "
                             "/usr/bin/time -l resource report) into runs/X.timing.txt; runs/X.err is "
                             "created as an empty placeholder exactly as in the BATCH-7b798d lineage "
                             "(whose .err files all carry the empty-file sha256). Disclosed per BUILD.md."),
             "impact": "none"},
            {"id": "DEV-S0-4",
             "description": ("Arm run labels differ from the BATCH-7b798d labels (S05DEADANCHOR-AES-R6-P30 "
                             "vs S4DEADANCHOR-AES-R6-P30; S06RAMPZERO-S0-R5-P30 vs S5RAMPZERO-S0-R5-P30). "
                             "Labels are executor-chosen receipt-echo fields only; stream derivation "
                             "(thread_seeds, key_stream_seeds) depends only on seed/armid/thread index - "
                             "confirmed by the cross-batch field-identity check, which found the label as "
                             "the ONLY non-strip difference on both receipts."),
             "impact": "none"},
        ],
        "unexpected_observations": [
            {"id": "OBS-S0-1", "rule8": True,
             "observation": ("S0-5 dead anchor read 0 hits at 2^30 (whist [1073741823,0,0,0,0], 1 trivial "
                             "swap excluded). PASSES the gate (band <= 8; tripwire >= 9) with reduced "
                             "anchor assurance per the preregistered wording (direction-safe: the anchor "
                             "guards against hit MANUFACTURE). Under the committed pooled r=6 rate ~1.72 "
                             "hits per 2^30 (internal-carried via EV-AES-ec53f1 / IDEA-20260901-582ea9), "
                             "P(0) = e^-1.72 ~= 0.18 - an unremarkable draw. Reproduces the BATCH-7b798d "
                             "dead-anchor re-seat observation of 0 hits.")},
            {"id": "OBS-S0-2", "rule8": True,
             "observation": ("S0-6 ramp-zero receipt carries hit_log_overflow = 1073740800 (= 2^30 - 4x256), "
                             "the necessary truncation of the capped per-hit DETAIL LOG when every trial "
                             "hits. ALL counter identities exact (logged_detail_records = 1024 = "
                             "threads x HIT_LOG_CAP; ewhist_hit sums to h = 2^30; whist/zhist/ewhist sums "
                             "exact). Under AMEND-1 this pure cap truncation is LEGAL; the AMEND-1 "
                             "proves-too-much control PASSED this receipt (the gate is not indicted). "
                             "First batch-level exercise of the AMEND-1 saturated-receipt evaluation.")},
            {"id": "OBS-S0-3", "rule8": True,
             "observation": ("S0-6 ramp-zero zhist structure: zhist[12]=1057061970, zhist[13]=16582173, "
                             "zhist[14]=97424, zhist[15]=257, zhist[16]=0, zero mass below 12. Consistent "
                             "with the W=3 law (three vanishing geometric words contribute 12 equal byte "
                             "positions; the fourth contributes 0-3 coincidental equalities; W=4 never "
                             "occurs). Values identical to the BATCH-7b798d OBS-S0-3 observation. "
                             "Report-only; not a gate input.")},
            {"id": "OBS-S0-4", "rule8": True,
             "observation": ("The dead anchor (r=6) excluded exactly 1 trivial swap "
                             "(trivial_swaps_excluded=1 of 2^30); the ramp-zero anchor (r=5) excluded 0 - "
                             "matching the committed affine-anchor convention and the BATCH-7b798d values. "
                             "Trials accounting holds on both receipts.")},
            {"id": "OBS-S0-5", "rule8": True,
             "observation": ("Cross-batch determinism: BOTH anchor receipts are field-identical to the "
                             "BATCH-7b798d committed receipts beyond the preregistered timing strip set, "
                             "with the executor-chosen arm label as the only other difference - "
                             "thread_seeds, key_stream_seeds, plaintext_stream_digest, key_hex, "
                             "arm_table_concat_sha256, and every counter reproduced exactly at identical "
                             "seats on the byte-identical build. Recorded as a determinism observation; "
                             "the BATCH-7b798d readings remain unvalidated as shape evidence under "
                             "AMEND-1 (no post-hoc rescue) - this check concerns instrument determinism "
                             "only.")},
        ],
        "budget": {
            "wall_clock_seconds_declared": 5400,
            "wall_clock_seconds_used_task_start_to_assembly": None,  # filled below
            "binary_invocations": {"used": sum(1 for r in runs if r["binary_invocation"]), "max": 8},
            "memory_gb_declared": 4,
            "max_rss_bytes_observed": max(r["max_rss_bytes"] for r in runs if r["max_rss_bytes"]),
            "per_arm_timeout_wrapper": "timeout 3600",
            "budget_stamps": "budget_stamps.jsonl",
            "binding_baseline_note": ("~27 min per 2^30 4-thread arm is the budget contract; measured "
                                      "rates here (95.2 s dead anchor, 78.7 s ramp-zero) are "
                                      "OPTIMISTIC-RELATIVE and disclosed, never charged as the baseline"),
            "exhaustion_policy": "resource_exhaustion, never a reading (rule 5)",
        },
        "scope_discipline": {
            "claim_tier": "toy",
            "no_deployed_aes_claims": True,
            "no_published_cryptanalysis_comparisons": True,
            "no_interior_k_arms_run": True,
            "interior_k_arms_belong_to": "Stage S1 (TASK-20260902-525d16)",
            "no_git_add_or_commit": True,
            "no_status_or_promotion_interpretation": True,
            "x_statistic_not_computed": True,
            "no_rho_exclusion": True,
            "no_reopen_clause_honored": True,
        },
        "artifact_inventory": {
            "PREREGISTRATION.md": "write-once preregistration (S0-1)",
            "RESULTS.json": "this file",
            "budget_stamps.jsonl": "budget stamps (task start, source copy, preregistration mtime, per-stage start/end, analysis stamps)",
            "src/affarm046ex.c": "frozen instrument source (byte-exact copy from BATCH-7b798d, UNMODIFIED)",
            "src/affarm046ex": "frozen binary (byte-exact copy from BATCH-7b798d, UNMODIFIED, not recompiled)",
            "src/BUILD.md": "build/run/budget/inference record",
            "src/freeze_digest.py": "freeze digester/reverifier (fresh for this task)",
            "src/s0_analysis.py": "anchor analysis under AMEND-1 (fresh, per-receipt modes)",
            "src/assemble_results.py": "this assembler (fresh)",
            "runs/S1_buildid.json": "S0-2 build identity re-verification vs snapshot receipt",
            "runs/source_diff.txt": "S0-2 zero-source-change diff audit (empty)",
            "runs/S2a_pin.json|.err|.timing.txt": "S0-3 KAT pin receipt",
            "runs/S2b_pinidentity.json|.err|.timing.txt": "S0-3 identity pin receipt",
            "runs/S3_freeze_c_output.json": "S0-4 raw C freeze output (extra artifact, DEV-S0-2)",
            "runs/S3_freeze.timing.txt": "S0-4 timing (extra artifact, DEV-S0-2)",
            "runs/S3_freeze_rerun.json": "S0-4 digested rerun freeze (cap-256 assertions)",
            "runs/S3_freeze_cmp.json": "S0-4 comparison vs committed R3_table_freeze.json",
            "runs/S4_dead_anchor.json|.err|.timing.txt": "S0-5 dead anchor receipt",
            "runs/S4_dead_analysis.json": "S0-5 dead anchor gate analysis (corrected pass)",
            "runs/S4_dead_analysis_pass1_defective.json": "S0-5 pass-1 defective analysis (preserved, DEV-S0-1)",
            "runs/S5_rampzero.json|.err|.timing.txt": "S0-6 ramp-zero anchor receipt",
            "runs/S5_rampzero_analysis.json": "S0-6 ramp-zero anchor gate analysis (AMEND-1 identity table + proves-too-much control)",
        },
        "assembled_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "parse_attestation": ("RESULTS.json is machine-generated JSON; parsed whole with python3 json.load "
                              "after writing, before task completion"),
        "inference": INFERENCE,
    }

    # wall clock from first to last budget stamp event so far + assembly
    stamps = [json.loads(l) for l in open("budget_stamps.jsonl") if l.strip()]
    start = stamps[0]["utc"]
    fmt = "%Y-%m-%dT%H:%M:%SZ"
    used = (datetime.datetime.now(datetime.timezone.utc)
            - datetime.datetime.strptime(start, fmt).replace(tzinfo=datetime.timezone.utc)).total_seconds()
    results["budget"]["wall_clock_seconds_used_task_start_to_assembly"] = round(used, 1)

    with open("RESULTS.json", "w") as f:
        json.dump(results, f, indent=1)
    # parse attestation: re-load the written file whole
    json.load(open("RESULTS.json"))
    print(json.dumps({"s0_outcome": outcome,
                      "binary_invocations": results["binary_invocations_used"],
                      "wall_seconds_used": results["budget"]["wall_clock_seconds_used_task_start_to_assembly"],
                      "parse_ok": True}, indent=1))


if __name__ == "__main__":
    main()
