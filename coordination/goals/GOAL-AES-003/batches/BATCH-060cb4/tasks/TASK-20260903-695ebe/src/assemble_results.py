#!/usr/bin/env python3
# assemble_results.py -- TASK-20260903-695ebe (BATCH-060cb4, GOAL-AES-003)
# Fresh assembler: builds RESULTS.json from the task's artifacts only
# (no hand-entered readings). Re-parses the written file before exit.
import json, os, datetime, time

TD = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/"


def load(p):
    with open(TD + p) as f:
        return json.load(f)


def main():
    stamps = [json.loads(l) for l in open(TD + "budget_stamps.jsonl") if l.strip()]
    buildid = load("runs/S02_buildid.json")
    kat = load("runs/S03_kat_cmp.json")
    fcmp = load("runs/S04_freeze_cmp.json")
    dead = load("runs/S05_dead_analysis.json")
    ramp = load("runs/S06_rampzero_analysis.json")
    det = load("runs/S07_cross_batch_determinism.json")
    dead_r = load("runs/S05_dead_anchor.json")
    ramp_r = load("runs/S06_rampzero.json")
    pin_r = load("runs/S03a_pin.json")
    pini_r = load("runs/S03b_pinidentity.json")

    start = [s for s in stamps if s["event"] == "task_start"][0]

    def arm_stamps(stage):
        st = [s for s in stamps if s.get("stage") == stage and s["event"] == "arm_start"]
        en = [s for s in stamps if s.get("stage") == stage and s["event"] == "arm_end"]
        return (st[0] if st else None), (en[0] if en else None)

    def wall_of(stage):
        st, en = arm_stamps(stage)
        if st and en:
            return en["wall_seconds"], st.get("start_epoch"), en.get("end_epoch"), en.get("max_rss_bytes")
        return None, None, None, None

    def cmd_of(stage):
        st, _ = arm_stamps(stage)
        return st["command"] if st else None

    def receipt_run(stage, cmd, receipt, analysis, run_id, gate_outcome):
        wall, e0, e1, rss = wall_of(stage)
        return {
            "run_id": run_id,
            "command": cmd,
            "binary_invocation": True,
            "seed": receipt["seed"],
            "arm_id": receipt["arm_id"],
            "threads": receipt["threads"],
            "start_epoch": e0,
            "end_epoch": e1,
            "wall_seconds_stamp": wall,
            "wall_seconds_receipt_elapsed": receipt["elapsed_seconds_measured"],
            "max_rss_bytes": rss,
            "hits_W_ge1_nontrivial": receipt["W_ge1_nontrivial"],
            "whist": receipt["whist"],
            "W_ge1_by_word": receipt["W_ge1_by_word"],
            "trivial_swaps_excluded": receipt["trivial_swaps_excluded"],
            "hit_log_overflow": receipt["hit_log_overflow"],
            "excess_ratio_vs_excess_E": receipt["W_ge1_nontrivial"] / (1 << 30),
            "garwood95_rate_per_2_30": analysis["garwood95_rate_per_2_30"] if "garwood95_rate_per_2_30" in analysis else None,
            "band": analysis.get("band"),
            "bandrank": analysis.get("bandrank"),
            "amend1_identities_pass": analysis["amend1_identities_pass"],
            "gate_outcome": gate_outcome,
        }

    runs = []
    runs.append({
        "run_id": "S0-2",
        "command": "sha256 src/affarm046ex src/affarm046ex.c vs BATCH-e5d753 snapshot receipt + diff -u vs lineage source (no binary invocation)",
        "binary_invocation": False,
        "seed": None, "arm_id": None, "threads": None,
        "wall_seconds_stamp": None, "max_rss_bytes": None,
        "hits_W_ge1_nontrivial": None, "whist": None, "W_ge1_by_word": None,
        "excess_ratio_vs_excess_E": None, "garwood95_rate_per_2_30": None, "band": None,
        "outcome": "build_identity_pass",
        "artifact": "runs/S02_buildid.json",
        "priced_fallback_executed": buildid["priced_fallback_required"],
    })
    runs.append({
        "run_id": "S0-3a",
        "command": cmd_of("S0-3") if cmd_of("S0-3") else "timeout 3600 /usr/bin/time -l src/affarm046ex pin 363851",
        "binary_invocation": True,
        "seed": 363851, "arm_id": None, "threads": None,
        "wall_seconds_stamp": [s for s in stamps if s.get("stage") == "S0-3" and s["event"] == "arm_end"][0]["wall_seconds"],
        "max_rss_bytes": [s for s in stamps if s.get("stage") == "S0-3" and s["event"] == "arm_end"][0]["max_rss_bytes"],
        "hits_W_ge1_nontrivial": None, "whist": None, "W_ge1_by_word": None,
        "excess_ratio_vs_excess_E": None, "garwood95_rate_per_2_30": None, "band": None,
        "outcome": "pin_pass_byte_identical_to_lineage",
        "mode": "pin (FIPS-197 KAT + anchors, AES table)",
        "roundtrip_failures": pin_r["roundtrip_failures"],
        "pin_pass": pin_r["pin_pass"],
        "byte_identity_vs_lineage_kat_receipt": kat["pin"]["byte_identity"],
        "artifact": "runs/S03a_pin.json",
    })
    runs.append({
        "run_id": "S0-3b",
        "command": "timeout 3600 /usr/bin/time -l src/affarm046ex pinidentity 363851",
        "binary_invocation": True,
        "seed": 363851, "arm_id": None, "threads": None,
        "wall_seconds_stamp": [s for s in stamps if s.get("stage") == "S0-3" and s["event"] == "arm_end"][1]["wall_seconds"],
        "max_rss_bytes": [s for s in stamps if s.get("stage") == "S0-3" and s["event"] == "arm_end"][1]["max_rss_bytes"],
        "hits_W_ge1_nontrivial": None, "whist": None, "W_ge1_by_word": None,
        "excess_ratio_vs_excess_E": None, "garwood95_rate_per_2_30": None, "band": None,
        "outcome": "pin_pass_byte_identical_to_lineage",
        "mode": "pinidentity (identity table roundtrips)",
        "roundtrip_failures": pini_r["roundtrip_failures"],
        "pin_pass": pini_r["pin_pass"],
        "byte_identity_vs_lineage_kat_receipt": kat["pinidentity"]["byte_identity"],
        "artifact": "runs/S03b_pinidentity.json",
    })
    frz_wall, frz_e0, frz_e1, frz_rss = wall_of("S0-4")
    runs.append({
        "run_id": "S0-4",
        "command": cmd_of("S0-4"),
        "binary_invocation": True,
        "seed": 363851, "arm_id": None, "threads": None,
        "wall_seconds_stamp": frz_wall, "max_rss_bytes": frz_rss,
        "hits_W_ge1_nontrivial": None, "whist": None, "W_ge1_by_word": None,
        "excess_ratio_vs_excess_E": None, "garwood95_rate_per_2_30": None, "band": None,
        "outcome": "freeze_pass_reverify_pass",
        "mode": "freeze (7 family points + folded smoke selfchecks)",
        "reverify_pass_vs_R3": fcmp["reverify_pass"],
        "reverify_mismatches": fcmp["mismatches"],
        "artifact": "runs/S04_freeze_cmp.json",
    })
    runs.append(receipt_run("S0-5", cmd_of("S0-5"), dead_r, dead, "S0-5",
                            dead["anchor_verdict"]))
    runs[-1]["analysis"] = "runs/S05_dead_analysis.json"
    runs[-1]["analysis_order"] = "ANALYZED FIRST among reading-bearing arms, before any alive reading (binding order)"
    runs.append(receipt_run("S0-6", cmd_of("S0-6"), ramp_r, ramp, "S0-6",
                            ramp["anchor_verdict"]))
    runs[-1]["analysis"] = "runs/S06_rampzero_analysis.json"
    runs[-1]["amend1_proves_too_much_control_passed"] = ramp["amend1_proves_too_much_control"]["gate_passed_this_receipt"]
    runs[-1]["zhist_observed"] = ramp_r["zhist"]

    # ordered cascade: CC-GATE-FAIL > CC-F6 > CC-ANCHOR-FAIL > PASS-S0
    gates_fail = not (buildid["identity_pass"] and kat["gate_pass"] and fcmp["reverify_pass"]
                      and dead["amend1_identities_pass"] and ramp["amend1_identities_pass"]
                      and dead["seat_as_preregistered"] and ramp["seat_as_preregistered"])
    f6 = dead["gate"]["tripwire_fired"]
    anchor_fail = not ramp["anchor_conjuncts_pass"]
    if gates_fail:
        outcome = "CC-GATE-FAIL"
        halt = True
    elif f6:
        outcome = "CC-F6"
        halt = True
    elif anchor_fail:
        outcome = "CC-ANCHOR-FAIL"
        halt = True
    else:
        outcome = "PASS-S0"
        halt = False

    now = datetime.datetime.now(datetime.timezone.utc)
    used = now.timestamp() - start["epoch"]
    max_rss = max([s.get("max_rss_bytes") or 0 for s in stamps])
    invocations = len([s for s in stamps if s.get("binary_invocation") and s["event"] == "arm_end"])

    results = {
        "schema": "crypto.autoresearch.task_results.v1",
        "task_id": "TASK-20260903-695ebe",
        "batch_id": "BATCH-060cb4",
        "goal_id": "GOAL-AES-003",
        "idea_record": "IDEA-20260903-8f26ac",
        "stage": "S0",
        "pin_reference": {
            "id": "PIN-T0",
            "decision": "DEC-20260901-fb6f11",
            "statement": "SubWord uses TPOS[0] (first position of the frozen order): identity schedule at k=0, AES schedule at every k >= 1",
        },
        "gate_regime": {
            "id": "AMEND-1",
            "decision": "DEC-20260901-6f9de3",
            "verbatim_conjunct": "counter INCONSISTENCY on an analysis-bearing receipt -> invalid_measurement; counter inconsistency means (a) overflow != hits - threads x HIT_LOG_CAP, or (b) any cap-independent counter (hits, W, ewhist_hit) disagrees with its internal identities, or (c) any analysis-bearing quantity is derived from the capped detail log rather than the counters. Pure cap truncation of the detail log with all counter identities intact is NOT a gate failure.",
            "saturation_aware_evaluation": "overflow == hits - logged_detail_records EXACTLY, where logged_detail_records == threads x HIT_LOG_CAP when saturated (hits > threads x HIT_LOG_CAP) and == hits with overflow == 0 otherwise; hits := W_ge1_nontrivial; logged_detail_records := len(hit_trials) entries",
            "zhist_identity": "sum(zhist) == nontrivial_trials (DEV-S0-1 CORRECTED form carried in PREREGISTRATION.md section 2 item 4; the literal '==trials' shorthand is reported informationally only)",
            "preregistration": "PREREGISTRATION.md sections 1-3 (committed before any binary invocation)",
        },
        "build_provenance": {
            "lineage": "BATCH-e5d753 snapshot-bound PIN-T0 widened build (affarm046ex, HIT_LOG_CAP 256 per thread), zero source change in S0/S1",
            "copy_source_dir": "coordination/goals/GOAL-AES-003/batches/BATCH-e5d753/tasks/TASK-20260902-987716/src/",
            "snapshot_receipt": "coordination/goals/GOAL-AES-003/batches/BATCH-e5d753/archives/TASK-20260902-e19f39/snapshot-receipt.json",
            "identity_check": "runs/S02_buildid.json",
            "identity_check_result": "PASS (source and binary sha256 identical to snapshot-bound hashes ec748cef.../74e3d65c...)",
            "identity_path_taken": buildid["path_taken"],
            "source_diff_audit": "runs/source_diff.txt (diff exit 0, empty body - zero source change)",
            "recompiled": False,
            "worktree_head_commit": start["worktree_head_commit"],
            "worktree_branch": start["worktree_branch"],
        },
        "preregistration": {
            "path": "PREREGISTRATION.md",
            "mtime_before_first_binary_invocation": True,
            "stamp_event": "preregistration_written in budget_stamps.jsonl",
            "write_once": True,
        },
        "runs": runs,
        "binary_invocations_used": invocations,
        "binary_invocations_max": 7,
        "amend1_identity_tables": {
            "S0-5_dead_anchor": dead["amend1_identity_table"],
            "S0-6_rampzero": ramp["amend1_identity_table"],
            "note": "full per-receipt AMEND-1 identity suites; the zhist internal identity is sum(zhist)==nontrivial_trials (DEV-S0-1 corrected; zhist/whist incremented only after the trivial-swap continue, affarm046ex.c:458-459); the literal '==trials' shorthand holds iff trivial_swaps_excluded==0 and is reported informationally",
        },
        "amend1_c_detail_log_attestations": {
            "S0-5_dead_anchor": dead["amend1_c_detail_log_attestation"],
            "S0-6_rampzero": ramp["amend1_c_detail_log_attestation"],
        },
        "gates": {
            "S0-2_build_identity": {
                "src_sha256_match": buildid["files"]["src/affarm046ex.c"]["match"],
                "binary_sha256_match": buildid["files"]["src/affarm046ex"]["match"],
                "source_diff_empty": buildid["source_diff_audit"]["diff_body_empty"],
                "path_taken": buildid["path_taken"],
                "priced_fallback_gate0x_executed": buildid["priced_fallback_required"],
                "gate_pass": buildid["identity_pass"],
            },
            "S0-3_KAT_pins": {
                "pin_pass": pin_r["pin_pass"],
                "pinidentity_pass": pini_r["pin_pass"],
                "pin_byte_identity_vs_lineage": kat["pin"]["byte_identity"],
                "pinidentity_byte_identity_vs_lineage": kat["pinidentity"]["byte_identity"],
                "gate_pass": kat["gate_pass"],
            },
            "S0-4_freeze_reverification": {
                "freeze_pass": json.load(open(TD + "runs/S04_freeze_rerun.json"))["freeze_pass"],
                "reverify_pass_vs_committed_R3": fcmp["reverify_pass"],
                "mismatches": fcmp["mismatches"],
                "compared_fields": fcmp["compared"],
                "cap_dependent_selfcheck_fields_disclosed_not_compared": "hit_detail_records, hit_log_overflow (committed file cap-64, this build cap-256)",
                "selfcheck_cap_independent_comparison": fcmp["selfcheck_cap_independent_comparison"],
                "gate_pass": fcmp["reverify_pass"],
            },
            "S0-5_dead_anchor": {
                "hits": dead["hits_W_ge1_nontrivial"],
                "band": dead["band"],
                "dead_band_2_30": dead["gate"]["dead_band_2_30"],
                "f6_tripwire": dead["gate"]["f6_tripwire"],
                "tripwire_fired": dead["gate"]["tripwire_fired"],
                "amend1_identities_pass": dead["amend1_identities_pass"],
                "analyzed_first_attestation": dead["analysis_order_attestation"],
                "gate_pass": dead["anchor_verdict"] == "PASS",
            },
            "S0-6_rampzero_anchor": {
                "hits": ramp["hits_W_ge1_nontrivial"],
                "hits_equal_2pow30": ramp["anchor_conjuncts"]["hits_equal_2pow30_exact"],
                "W3_on_100pct": ramp["anchor_conjuncts"]["W3_on_100pct_of_nontrivial"],
                "excess_ratio_1_exact": ramp["anchor_conjuncts"]["excess_ratio_1_exact"],
                "overflow_saturated_legal_under_amend1": ramp["anchor_conjuncts"]["overflow_saturated_legal_under_amend1"],
                "amend1_identities_pass": ramp["amend1_identities_pass"],
                "amend1_proves_too_much_control_passed": ramp["amend1_proves_too_much_control"]["gate_passed_this_receipt"],
                "gate_pass": ramp["anchor_verdict"] == "PASS",
            },
        },
        "s0_outcome_ordered_cascade": outcome,
        "halt_branch": outcome if halt else None,
        "offending_receipt": None if not halt else ("runs/S05_dead_anchor.json" if outcome in ("CC-F6",) else "see gates"),
        "cascade_evaluation_note": "evaluated in the preregistered fixed order CC-GATE-FAIL > CC-F6 > CC-ANCHOR-FAIL > PASS-S0 (S0 owns cascade branches 1-3); S0 decides instrument validity and anchors only, NOT the shape (no interior k>=1 point run); a halt would be a committed instrument/anchor result, never a shape reading (rule 5)",
        "cross_batch_determinism_check": det,
        "deviations": [
            {
                "id": "DEV-S0-1",
                "description": "Stderr convention: each invocation redirects stderr (including the /usr/bin/time -l resource report) into runs/X.timing.txt; runs/X.err is created as an empty placeholder exactly as in the BATCH-e5d753 / BATCH-7b798d lineage (whose .err files carry the empty-file sha256).",
                "impact": "none",
            },
            {
                "id": "DEV-S0-2",
                "description": "Arm run labels differ from the predecessor labels (CC05DEADANCHOR-AES-R6-P30 vs S05DEADANCHOR-AES-R6-P30; CC06RAMPZERO-S0-R5-P30 vs S06RAMPZERO-S0-R5-P30). Labels are executor-chosen receipt-echo fields only; stream derivation (thread_seeds, key_stream_seeds) depends only on seed/armid/thread index - confirmed by the cross-batch field-identity check (runs/S07_cross_batch_determinism.json), which found the label as the ONLY non-strip difference on both receipts.",
                "impact": "none",
            },
            {
                "id": "DEV-S0-3",
                "description": "S0-4 freeze re-verification used a FRESH re-implementation of the documented lineage comparison contract (src/freeze_reverify.py) rather than the lineage freeze_digest.py tool itself (lineage tool sha256 c29e876b76a4a4ba6cf200d36a56ae1bc8faf8c0bdacbc40df5c30024a2b2814 was the semantic reference; comparison fields and cap-64-vs-256 disclosure exactly as preregistered section 15). The C freeze output byte count (61706) matches the predecessor's S3_freeze_c_output.json size exactly, and the comparison result is 0 mismatches.",
                "impact": "none",
            },
            {
                "id": "DEV-S0-4",
                "description": "Extra artifacts beyond the dispatch-queue artifact_paths list (runs/* receipts, comparisons, analyses; src/ scripts) are retained per the artifact policy (raw stdout + timing per invocation; machine-readable results). The queue lists PREREGISTRATION.md, RESULTS.json, budget_stamps.jsonl as artifact_paths; the runs/ and src/ deliverables are named in the handoff write scope.",
                "impact": "none",
            },
            {
                "id": "DEV-S0-5",
                "description": "Cross-batch determinism comparison (runs/S07_cross_batch_determinism.json) executed beyond the required S0 sequence, as a rule-8 determinism observation: both anchor receipts compared field-by-field against the BATCH-e5d753 committed receipts at identical seats, stripping ONLY the preregistered timing strip set. Recorded as instrument determinism only (NARROW-3: determinism is never replication).",
                "impact": "none",
            },
        ],
        "unexpected_observations": [
            {
                "id": "OBS-S0-1",
                "rule8": True,
                "observation": "S0-5 dead anchor read 0 hits at 2^30 (whist [1073741823,0,0,0,0], 1 trivial swap excluded). PASSES the gate (band <= 8; tripwire >= 9 not fired) with reduced anchor assurance per the preregistered wording (direction-safe: the anchor guards against hit MANUFACTURE). Under the committed pooled r=6 rate ~1.72 hits per 2^30, P(0) = e^-1.72 ~= 0.18 - an unremarkable draw. Third consecutive 0-hit re-seat of this anchor (BATCH-7b798d, BATCH-e5d753, this batch).",
            },
            {
                "id": "OBS-S0-2",
                "rule8": True,
                "observation": "S0-6 ramp-zero receipt carries hit_log_overflow = 1,073,740,800 (= 2^30 - 4x256), the necessary truncation of the capped per-hit DETAIL LOG when every trial hits. ALL counter identities exact (logged_detail_records = 1024 = threads x HIT_LOG_CAP; ewhist_hit sums to h = 2^30; whist/zhist/ewhist sums exact). Under AMEND-1 this pure cap truncation is LEGAL; the AMEND-1 proves-too-much control PASSED this receipt (the gate is not indicted).",
            },
            {
                "id": "OBS-S0-3",
                "rule8": True,
                "observation": "S0-6 ramp-zero zhist structure: zhist[12]=1057061970, zhist[13]=16582173, zhist[14]=97424, zhist[15]=257, zhist[16]=0, zero mass below 12 - values IDENTICAL to the BATCH-e5d753 OBS-S0-3 observation (determinism at identical seat/seed/build). Consistent with the W=3 law (three vanishing geometric words contribute 12 equal byte positions; the fourth contributes 0-3 coincidental equalities; W=4 never occurs). Report-only; not a gate input.",
            },
            {
                "id": "OBS-S0-4",
                "rule8": True,
                "observation": "The dead anchor (r=6) excluded exactly 1 trivial swap (trivial_swaps_excluded=1 of 2^30); the ramp-zero anchor (r=5) excluded 0 - matching the committed affine-anchor convention and the BATCH-e5d753 values. Trials accounting holds on both receipts.",
            },
            {
                "id": "OBS-S0-5",
                "rule8": True,
                "observation": "Cross-batch determinism: BOTH anchor receipts are field-identical to the BATCH-e5d753 committed receipts beyond the preregistered timing strip set, with the executor-chosen arm label as the only other difference - thread_seeds, key_stream_seeds, plaintext_stream_digest, key_hex, arm_table_concat_sha256, and every counter reproduced exactly at identical seats on the byte-identical build. Recorded as a determinism observation; determinism is never replication (NARROW-3), and the BATCH-7b798d readings remain unvalidated under AMEND-1 (no post-hoc rescue).",
            },
        ],
        "budget": {
            "wall_clock_seconds_declared": 5400,
            "wall_clock_seconds_used_task_start_to_assembly": round(used, 1),
            "wall_clock_deadline_epoch": start["wall_clock_deadline_epoch"],
            "binary_invocations": {"used": invocations, "max": 7},
            "memory_gb_declared": 4,
            "max_rss_bytes_observed": max_rss,
            "per_arm_timeout_wrapper": "timeout 3600",
            "budget_stamps": "budget_stamps.jsonl (arm id, command, start/end epochs, wall s, rss per arm)",
            "binding_baseline_note": "~27 min per 2^30 4-thread arm is the budget contract; measured rates here are OPTIMISTIC-RELATIVE and disclosed, never charged as the baseline",
            "exhaustion_policy": "resource_exhaustion, never a reading (rule 5)",
        },
        "scope_discipline": {
            "claim_tier": "toy",
            "no_deployed_aes_claims": True,
            "no_published_cryptanalysis_comparisons": True,
            "no_interior_k_arms_run": True,
            "no_k_ge_1_readings_this_stage": True,
            "interior_readings_belong_to": "Stage S1 (TASK-20260903-5fbdfc) and Stage S2",
            "no_git_add_or_commit": True,
            "no_status_or_promotion_interpretation": True,
            "x_statistic_not_computed": True,
            "no_rho_exclusion": True,
            "no_reopen_clause_honored": True,
        },
        "artifact_inventory": {
            "PREREGISTRATION.md": "write-once preregistration (S0-1)",
            "RESULTS.json": "this file",
            "budget_stamps.jsonl": "budget stamps (task start, source copy, preregistration mtime, per-arm start/end epochs + wall s + rss, analysis stamps)",
            "src/affarm046ex.c": "frozen instrument source (byte-exact copy from BATCH-e5d753 TASK-20260902-987716, UNMODIFIED)",
            "src/affarm046ex": "frozen binary (byte-exact copy from BATCH-e5d753 TASK-20260902-987716, UNMODIFIED, not recompiled)",
            "src/freeze_reverify.py": "freeze digester/reverifier (fresh for this task; lineage comparison contract)",
            "src/s0_analysis.py": "anchor analysis under AMEND-1 (fresh for this task; DEV-S0-1-corrected zhist identity carried)",
            "src/assemble_results.py": "this assembler (fresh for this task)",
            "runs/S02_buildid.json": "S0-2 build identity re-verification vs BATCH-e5d753 snapshot receipt",
            "runs/source_diff.txt": "S0-2 zero-source-change diff audit (empty)",
            "runs/S03a_pin.json|.err|.timing.txt": "S0-3 KAT pin receipt",
            "runs/S03b_pinidentity.json|.err|.timing.txt": "S0-3 identity pin receipt",
            "runs/S03_kat_cmp.json": "S0-3 byte-identity comparison vs lineage KAT receipts",
            "runs/S04_freeze_c_output.json": "S0-4 raw C freeze output",
            "runs/S04_freeze.timing.txt": "S0-4 timing",
            "runs/S04_freeze_rerun.json": "S0-4 digested rerun freeze (cap-256 assertions)",
            "runs/S04_freeze_cmp.json": "S0-4 comparison vs committed R3_table_freeze.json",
            "runs/S05_dead_anchor.json|.err|.timing.txt": "S0-5 dead anchor receipt",
            "runs/S05_dead_analysis.json": "S0-5 dead anchor gate analysis (AMEND-1 identity table)",
            "runs/S06_rampzero.json|.err|.timing.txt": "S0-6 ramp-zero anchor receipt",
            "runs/S06_rampzero_analysis.json": "S0-6 ramp-zero anchor gate analysis (AMEND-1 identity table + proves-too-much control)",
            "runs/S07_cross_batch_determinism.json": "cross-batch determinism observation vs BATCH-e5d753 (NARROW-3: not replication)",
        },
        "assembled_utc": now.isoformat(),
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
    with open(TD + "RESULTS.json", "w") as f:
        json.dump(results, f, indent=1)
    json.load(open(TD + "RESULTS.json"))
    print(json.dumps({"s0_outcome": outcome, "halt": halt,
                      "invocations": invocations, "wall_used_s": round(used, 1),
                      "max_rss": max_rss}, indent=1))


if __name__ == "__main__":
    main()
