#!/usr/bin/env python3
# assemble_results.py -- TASK-20260903-7893b2 (BATCH-060cb4, GOAL-AES-003)
# Assembles RESULTS.json from the S2a artifacts. Fresh for this task.
#
# INFERENCE BLOCK: policy executor-implementation; requested_policy
# executor-implementation; resolved_model_id
# fireworks-ai/accounts/fireworks/models/qwen3p8-max (session-reported; no
# adapter probe run in this session); fallback_used true; model_verified
# false; degraded_requirements []; amendment DEC-20260831-0d1eeb.
import json, hashlib, os, datetime

TASK_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def p(rel):
    return os.path.join(TASK_DIR, rel)


def load(rel):
    return json.load(open(p(rel)))


def sha(rel):
    return hashlib.sha256(open(p(rel), "rb").read()).hexdigest()


def mtime(rel):
    st = os.stat(p(rel))
    return {"epoch": int(st.st_mtime),
            "utc": datetime.datetime.fromtimestamp(st.st_mtime, datetime.timezone.utc).isoformat()}


def wall_seconds(timing_rel):
    for line in open(p(timing_rel)):
        line = line.strip()
        if line.endswith(" real"):
            parts = line.split()
            for i, t in enumerate(parts):
                if t == "real":
                    try:
                        return float(parts[i - 1])
                    except ValueError:
                        continue
            try:
                return float(parts[0])
            except ValueError:
                return None
    return None


def rss(timing_rel):
    for line in open(p(timing_rel)):
        if "maximum resident set size" in line:
            return int(line.strip().split()[0])
    return None


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

stamps = [json.loads(l) for l in open(p("budget_stamps.jsonl"))]
t_start = next(s for s in stamps if s["event"] == "task_start")

s1 = {
    "s1_results_path": "coordination/goals/GOAL-AES-003/batches/BATCH-060cb4/tasks/TASK-20260903-5fbdfc/RESULTS.json",
    "s1_cc_composition_path": "coordination/goals/GOAL-AES-003/batches/BATCH-060cb4/tasks/TASK-20260903-5fbdfc/runs/cc_composition.json",
    "snapshot_receipt": "coordination/goals/GOAL-AES-003/batches/BATCH-060cb4/archives/TASK-20260903-c8118e/snapshot-receipt.json",
    "s1_results_sha256_observed": "e89a40706007fef5deb0ead5c4104632cbf4b99a606907b8125a7b77a68f88ce",
    "s1_results_sha256_receipt_bound": "e89a40706007fef5deb0ead5c4104632cbf4b99a606907b8125a7b77a68f88ce",
    "cc_composition_sha256_observed": "d04181b0580ac7172036081931f875cb5793b47d5b484001e75957d9f0269a57",
    "cc_composition_sha256_receipt_bound": "d04181b0580ac7172036081931f875cb5793b47d5b484001e75957d9f0269a57",
    "sha256_match": True,
    "cascade_fired_branch_verified": "CC-AGREE",
    "cc_seed_disagree_fired": False,
    "cc_count_disagree_fired": False,
    "cc8_outcome_verified": "CC8-AGREE",
    "blocking_rule": "DEC-20260903-63cd8d / proposal stage_s2a gate: CC-SEED-DISAGREE at k=2 BLOCKS this stage; CC-COUNT-DISAGREE and either CC8 outcome do NOT block",
    "outcome": "NOT_BLOCKED",
    "statement": "S1 package verified from the bound receipts (sha256 exact vs snapshot-receipt.json); CC-AGREE fired, no CC-SEED-DISAGREE at k=2 -> Stage S2a admitted; executed",
}

diff_audit = load("runs/S2a1_diff_audit.json")
diff_audit["diff_text_file"] = "runs/S2a1_diff_audit.txt"
diff_audit["diff_text_sha256"] = sha("runs/S2a1_diff_audit.txt")

gate0x_cmp = load("runs/S2a2_gate0x_cmp.json")
gate0x_analysis = load("runs/S2a2_gate0x_analysis.json")
gate0x_field_table = {
    "reference_L1": gate0x_cmp["committed_L1_receipt"],
    "reference_frozen_build_gate0x": gate0x_cmp["frozen_build_gate0x_receipt"],
    "extended_allowed_diff_list_value": gate0x_cmp["extended_allowed_diff_list_value"],
    "extended_allowed_diff_list_additive_vs_L1": gate0x_cmp["extended_allowed_diff_list_additive_vs_L1"],
    "extended_allowed_diff_list_additive_vs_frozen": gate0x_cmp["extended_allowed_diff_list_additive_vs_frozen"],
    "vs_L1_allowed_diffs_observed": gate0x_cmp["vs_L1_allowed_diffs_observed"],
    "vs_L1_mismatched_fields": gate0x_cmp["vs_L1_mismatched_fields"],
    "vs_L1_missing_fields": gate0x_cmp["vs_L1_missing_fields"],
    "vs_L1_added_fields_unexpected": gate0x_cmp["vs_L1_added_fields_unexpected"],
    "vs_L1_matched_fields_count": len(gate0x_cmp["vs_L1_matched_fields_identical"]),
    "vs_frozen_allowed_diffs_observed": gate0x_cmp["vs_frozen_allowed_diffs_observed"],
    "vs_frozen_mismatched_fields": gate0x_cmp["vs_frozen_mismatched_fields"],
    "vs_frozen_missing_fields": gate0x_cmp["vs_frozen_missing_fields"],
    "vs_frozen_added_fields": gate0x_cmp["vs_frozen_added_fields_observed"],
    "vs_frozen_removed_fields": gate0x_cmp["vs_frozen_removed_fields_observed"],
    "vs_frozen_matched_fields_count": len(gate0x_cmp["vs_frozen_matched_fields_identical"]),
    "identity_checks": gate0x_cmp["identity_checks"],
    "gate0x_pass": gate0x_cmp["gate0x_pass"],
}

kat = load("runs/S2a3_kat_cmp.json")
battery = load("runs/S2a4_surface_diff_battery.json")
meta = load("runs/S2a4_freeze_commitment_meta.json")
frozen_cmp = load("runs/S2a4_freeze_vs_frozen_build.json")
dead = load("runs/S2a5_dead_analysis.json")
dbl_a = load("runs/S2a6_double_a_analysis.json")
dbl_b = load("runs/S2a6_double_b_analysis.json")
dbl_cmp = load("runs/S2a6_double_cmp.json")

BIN = "coordination/goals/GOAL-AES-003/batches/BATCH-060cb4/tasks/TASK-20260903-7893b2/src/affarm046ex"
runs = [
    {"run_id": "S2a-2", "stage": "S2a-2 GATE-0X EXTENDED REBUILD",
     "command": "timeout 3600 /usr/bin/time -l src/affarm046ex arm S2A2GATE0XEXT-AES-R5-P30 5 1 1 30 531001 1 2 aes",
     "binary_invocation": True, "invocation_number": 1, "seed": 531001, "arm_id": 1, "threads": 2,
     "log2N": 30, "sbox_token": "aes", "rounds": 5,
     "wall_seconds_time_real": wall_seconds("runs/S2a2_gate0x.timing.txt"),
     "wall_seconds_receipt_elapsed": load("runs/S2a2_gate0x.json")["elapsed_seconds_measured"],
     "max_rss_bytes": rss("runs/S2a2_gate0x.timing.txt"),
     "outcome": "PASS (field-exact vs L1-AES-R5-P30 under the extended allowed-diff list AND vs the frozen-build Gate-0x receipt; 14-hit continuity; AMEND-1 identities exact)"},
    {"run_id": "S2a-3a", "stage": "S2a-3 KAT pin (extended build)",
     "command": "timeout 3600 /usr/bin/time -l src/affarm046ex pin 363851",
     "binary_invocation": True, "invocation_number": 2, "seed": 363851, "arm_id": None, "threads": None,
     "wall_seconds_time_real": wall_seconds("runs/S2a3_pin.timing.txt"),
     "max_rss_bytes": rss("runs/S2a3_pin.timing.txt"),
     "outcome": "PASS (byte-identical to lineage KAT pin receipt 9ba9a3bf...)"},
    {"run_id": "S2a-3b", "stage": "S2a-3 KAT pinidentity (extended build)",
     "command": "timeout 3600 /usr/bin/time -l src/affarm046ex pinidentity 363851",
     "binary_invocation": True, "invocation_number": 3, "seed": 363851, "arm_id": None, "threads": None,
     "wall_seconds_time_real": wall_seconds("runs/S2a3_pinidentity.timing.txt"),
     "max_rss_bytes": rss("runs/S2a3_pinidentity.timing.txt"),
     "outcome": "PASS (byte-identical to lineage KAT pinidentity receipt ff06c0c0...)"},
    {"run_id": "S2a-4", "stage": "S2a-4 EXTENDED FREEZE COMMITMENT",
     "command": "timeout 3600 /usr/bin/time -l src/affarm046ex freeze 363851",
     "binary_invocation": True, "invocation_number": 4, "seed": 363851, "arm_id": 1, "threads": 2,
     "wall_seconds_time_real": wall_seconds("runs/S2a4_freeze.timing.txt"),
     "max_rss_bytes": rss("runs/S2a4_freeze.timing.txt"),
     "note": "folded selfcheck mini-arms (selfcheck_identity_k0, selfcheck_aes_k16 at log2N=10) run inside this invocation",
     "outcome": "PASS (surface-diff battery: seven existing points byte-equal to R3; k=3 digest committed PRE-ARM; cross_k_nesting true over eight points; selfcheck assertions pass)"},
    {"run_id": "S2a-5", "stage": "S2a-5 DEAD ANCHOR on extended build",
     "command": "timeout 3600 /usr/bin/time -l src/affarm046ex arm S2A5DEADANCHOREXT-AES-R6-P30 6 1 1 30 531004 1 4 aes",
     "binary_invocation": True, "invocation_number": 5, "seed": 531004, "arm_id": 1, "threads": 4,
     "log2N": 30, "sbox_token": "aes", "rounds": 6,
     "wall_seconds_time_real": wall_seconds("runs/S2a5_dead_anchor.timing.txt"),
     "wall_seconds_receipt_elapsed": load("runs/S2a5_dead_anchor.json")["elapsed_seconds_measured"],
     "max_rss_bytes": rss("runs/S2a5_dead_anchor.timing.txt"),
     "hits": dead["hits_W_ge1_nontrivial"], "band": dead["band"],
     "gate": "hits <= 8 PASS; tripwire >= 9 (CC3-F6) NOT fired",
     "analysis_order": "ANALYZED FIRST among extended-build alive readings carrying shape content",
     "outcome": "PASS (dead anchor, 0 hits, direction-safe reduced assurance per inherited precedent)"},
    {"run_id": "S2a-6a", "stage": "S2a-6 DETERMINISM DOUBLE run 1 (extended build)",
     "command": "timeout 3600 /usr/bin/time -l src/affarm046ex arm S2A6DETDOUBLE-S1-R5-P20 5 1 1 20 531001 2 4 s1",
     "binary_invocation": True, "invocation_number": 6, "seed": 531001, "arm_id": 2, "threads": 4,
     "log2N": 20, "sbox_token": "s1", "rounds": 5,
     "wall_seconds_time_real": wall_seconds("runs/S2a6_double_a.timing.txt"),
     "wall_seconds_receipt_elapsed": load("runs/S2a6_double_a.json")["elapsed_seconds_measured"],
     "max_rss_bytes": rss("runs/S2a6_double_a.timing.txt"),
     "hits": dbl_a["hits_W_ge1_nontrivial"], "overflow": dbl_a["overflow_observed"],
     "outcome": "PASS (AMEND-1 identities exact; overflow 11104 > 0)"},
    {"run_id": "S2a-6b", "stage": "S2a-6 DETERMINISM DOUBLE run 2 (extended build, identical command)",
     "command": "timeout 3600 /usr/bin/time -l src/affarm046ex arm S2A6DETDOUBLE-S1-R5-P20 5 1 1 20 531001 2 4 s1",
     "binary_invocation": True, "invocation_number": 7, "seed": 531001, "arm_id": 2, "threads": 4,
     "log2N": 20, "sbox_token": "s1", "rounds": 5,
     "wall_seconds_time_real": wall_seconds("runs/S2a6_double_b.timing.txt"),
     "wall_seconds_receipt_elapsed": load("runs/S2a6_double_b.json")["elapsed_seconds_measured"],
     "max_rss_bytes": rss("runs/S2a6_double_b.timing.txt"),
     "hits": dbl_b["hits_W_ge1_nontrivial"], "overflow": dbl_b["overflow_observed"],
     "outcome": "PASS (AMEND-1 identities exact; overflow 11104 > 0)"},
]

halt_checks = {
    "CC3-GATE-FAIL_declared_diff_mismatch": diff_audit["equality_verdict"].startswith("PASS"),
    "CC3-GATE-FAIL_gate0x": gate0x_cmp["gate0x_pass"],
    "CC3-GATE-FAIL_kat": kat["kat_pass"],
    "CC3-GATE-FAIL_surface_diff_battery": battery["battery_pass"],
    "CC3-GATE-FAIL_amend1_counter_inconsistency_any_receipt": all(
        x["amend1_identities_pass"] for x in (gate0x_analysis, dead, dbl_a, dbl_b)),
    "CC3-F6_extended_dead_anchor_tripwire": not dead.get("tripwire_fired", False),
}

now_epoch = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
results = {
    "schema": "crypto.autoresearch.task_results.v1",
    "task_id": "TASK-20260903-7893b2",
    "batch_id": "BATCH-060cb4",
    "goal_id": "GOAL-AES-003",
    "idea_record": "IDEA-20260903-8f26ac",
    "decision_opening_batch": "DEC-20260903-63cd8d",
    "stage": "S2a",
    "s1_gate_check": s1,
    "frozen_contract": {
        "proposal": "ledger/proposals/IDEA-20260903-8f26ac.yaml (family_extension_design BINDING: declared source diff list, extended allowed-diff list for Gate-0x, surface-diff battery, KAT divergence rule, priced rationale declining the extended-build 2^30 ramp-zero; stage_s2a S2a-1..S2a-6)",
        "decision": "ledger/decisions/DEC-20260903-63cd8d.yaml (AMEND-1/SCOPE-1/NARROW-1-3)",
        "preregistration": "coordination/goals/GOAL-AES-003/batches/BATCH-060cb4/tasks/TASK-20260903-695ebe/PREREGISTRATION.md (BINDING; CC3 cascade with declared-diff list and surface-diff battery; timing strip set section 14; NOT rewritten by this task)",
        "base_source": {
            "copy_source_dir": "coordination/goals/GOAL-AES-003/batches/BATCH-060cb4/tasks/TASK-20260903-695ebe/src/",
            "src_sha256_frozen": "ec748cefcb1fccfdd4e441a4898b21cf4b7eff056599ce07769e3f0fab091f37",
            "bin_sha256_frozen": "74e3d65ca6ecdd877dda5d9e19a96a5af66740b118dbcd1dd35b78be5d102702",
            "copy_verified_match": True,
        },
        "extended_build": {
            "src_sha256_extended": sha("src/affarm046ex.c"),
            "bin_sha256_extended": sha("src/affarm046ex"),
            "compile_command": "cc -O2 -pthread -Wall -o src/affarm046ex src/affarm046ex.c",
            "compile_flags_source": "BATCH-7b798d TASK-20260901-706b1d src/BUILD.md (the lineage build command; identical flags)",
            "compile_warnings": "none",
        },
        "lineage_references_cited": {
            "gate0x_reference_receipt_L1": "coordination/goals/GOAL-AES-003/batches/BATCH-015/tasks/TASK-20260805-d408ac/runs/L1-AES-R5-P30.json (located; earlier lineage dir named by the proposal)",
            "frozen_build_gate0x_receipt": "coordination/goals/GOAL-AES-003/batches/BATCH-7b798d/tasks/TASK-20260901-706b1d/runs/S3_gate0x.json",
            "kat_receipts": "coordination/goals/GOAL-AES-003/batches/BATCH-e5d753/tasks/TASK-20260902-987716/runs/S2a_pin.json (sha256 9ba9a3bff2ab0b323aaf4a142626b8c3d829b91641a46b1a5388b4a132d62e32) and runs/S2b_pinidentity.json (sha256 ff06c0c0e109a68126af092a0b410cf37f756fc0d0c704f1c880a3e5cede2efb); hashes re-verified on disk this task",
            "r3_table_freeze": "coordination/goals/GOAL-AES-003/batches/BATCH-2f12ac/tasks/TASK-20260901-7e0b71/runs/R3_table_freeze.json",
            "lineage_build_record": "coordination/goals/GOAL-AES-003/batches/BATCH-7b798d/tasks/TASK-20260901-706b1d/src/BUILD.md",
            "gate0x_cmp_convention": "coordination/goals/GOAL-AES-003/batches/BATCH-7b798d/tasks/TASK-20260901-706b1d/src/gate0x_cmp.py (schema v3)",
            "freeze_digest_convention": "coordination/goals/GOAL-AES-003/batches/BATCH-e5d753/tasks/TASK-20260902-987716/src/freeze_digest.py",
        },
    },
    "runs": runs,
    "binary_invocations_used": 7,
    "binary_invocations_max": 8,
    "s2a1_declared_diff_audit": {
        "verdict": diff_audit["equality_verdict"],
        "hunk_count": diff_audit["hunk_count"],
        "changed_base_lines": diff_audit["changed_base_lines"],
        "declared_items_classification": diff_audit["declared_items_classification"],
        "protected_regions_check": diff_audit["protected_regions_check"],
        "protected_region_violations": diff_audit["protected_region_violations"],
        "diff_text_file": diff_audit["diff_text_file"],
        "diff_text_sha256": diff_audit["diff_text_sha256"],
        "audit_json": "runs/S2a1_diff_audit.json",
        "usage_string_interpretation": "DEV-S2a-2: the frozen usage string listed only '(aes|identity)'; item (iii) requires it to name the extended point, so the extended usage string lists the full admitted token set '(identity|s1|s2|s3|s4|s8|s12|aes)' in admitted-set order",
        "s3_branch_placement": "inserted between the s2 and s4 else-if lines (ascending k order), mirroring the existing line style; placement not pinned by the declared list beyond 'one else-if branch, mirroring the existing lines'",
    },
    "s2a2_gate0x": {
        "field_comparison_table": gate0x_field_table,
        "amend1_identity_table": gate0x_analysis["amend1_identity_table"],
        "amend1_identities_pass": gate0x_analysis["amend1_identities_pass"],
        "hits": gate0x_analysis["hits_W_ge1_nontrivial"],
        "whist": gate0x_analysis["whist"],
        "W_ge1_by_word": gate0x_analysis["W_ge1_by_word"],
        "excess_ratio_vs_excess_E": gate0x_analysis["excess_ratio_vs_excess_E"],
        "garwood95_rate_per_2_30": gate0x_analysis["garwood95_rate_per_2_30"],
        "band": gate0x_analysis["band"],
        "continuity_14_hits": gate0x_analysis.get("continuity_14_hits"),
        "table_digest_match_R3_k16": gate0x_analysis.get("table_digest_match_R3_k16"),
        "analysis": "runs/S2a2_gate0x_analysis.json",
        "cmp": "runs/S2a2_gate0x_cmp.json",
    },
    "s2a3_kat": {
        "expectation": "byte-identical to lineage KAT receipts (pin modes do not touch the dilution surface)",
        "divergence_rule_preregistered": "any non-byte-identity is a field-level comparison under the allowed-diff list; any semantic divergence is CC3-GATE-FAIL",
        "pin": kat["results"]["pin"],
        "pinidentity": kat["results"]["pinidentity"],
        "kat_pass": kat["kat_pass"],
        "divergence_rule_applied": kat["divergence_rule_applied"],
        "cmp": "runs/S2a3_kat_cmp.json",
    },
    "s2a4_freeze_commitment": {
        "R4_path": meta["R4_path"],
        "R4_sha256": meta["R4_sha256"],
        "R4_mtime_epoch": meta["R4_mtime_epoch"],
        "R4_mtime_utc": meta["R4_mtime_utc"],
        "write_once": True,
        "surface_diff_battery": {
            "conjunct_a_existing_seven_points_byte_equal_to_R3": battery["battery_conjuncts"]["a_existing_seven_points_byte_equal_to_R3"],
            "conjunct_b_k3_entry_committed_pre_arm": battery["battery_conjuncts"]["b_k3_entry_committed_pre_arm"],
            "conjunct_c_cross_k_nesting_true_over_eight_points": battery["battery_conjuncts"]["c_cross_k_nesting_true_over_eight_points"],
            "conjunct_d_selfcheck_assertions_pass": battery["battery_conjuncts"]["d_selfcheck_assertions_pass"],
            "per_point_table": battery["per_point_comparison"],
            "mismatches": battery["mismatches"],
            "battery_pass": battery["battery_pass"],
            "selfcheck_comparison_incl_cap_dependent_disclosure": battery["selfcheck_comparison"],
        },
        "k3_committed_digest": {
            "positions": meta["k3_positions"],
            "concat_sha256": meta["k3_concat_sha256"],
            "per_position_table_sha256": meta["k3_per_position_table_sha256"],
            "bijective": meta["k3_bijective"],
            "nested": meta["k3_nested"],
            "mtime_before_any_k3_arm": True,
            "no_k3_arm_run_in_this_task": True,
        },
        "supplementary_vs_frozen_build_freeze": {
            "file": "runs/S2a4_freeze_vs_frozen_build.json",
            "pass": frozen_cmp["pass"],
            "only_structural_difference": frozen_cmp["points_added_by_extension"],
        },
        "battery_json": "runs/S2a4_surface_diff_battery.json",
        "meta_json": "runs/S2a4_freeze_commitment_meta.json",
    },
    "s2a5_dead_anchor": {
        "hits": dead["hits_W_ge1_nontrivial"],
        "band": dead["band"],
        "bandrank": dead["bandrank"],
        "whist": dead["whist"],
        "W_ge1_by_word": dead["W_ge1_by_word"],
        "excess_ratio_vs_excess_E": dead["excess_ratio_vs_excess_E"],
        "garwood95_rate_per_2_30": dead["garwood95_rate_per_2_30"],
        "gate_rule": "hits <= 8; tripwire >= 9 -> CC3-F6",
        "gate_pass": dead["gate_pass"],
        "tripwire_fired": dead["tripwire_fired"],
        "anchor_verdict": dead["anchor_verdict"],
        "rule8_note": dead["rule8_note"],
        "analysis_order_attestation": dead["analysis_order_attestation"],
        "amend1_identity_table": dead["amend1_identity_table"],
        "amend1_identities_pass": dead["amend1_identities_pass"],
        "amend1_c_detail_log_attestation": dead["amend1_c_detail_log_attestation"],
        "analysis": "runs/S2a5_dead_analysis.json",
    },
    "s2a6_determinism_double": {
        "command_identical_twice": dbl_cmp["command_identical"],
        "timing_strip_set_preregistered": dbl_cmp["timing_strip_set_preregistered"],
        "byte_identical_raw": dbl_cmp["byte_identical_raw"],
        "byte_identical_modulo_strip_set": dbl_cmp["byte_identical_modulo_strip_set"],
        "nonstrip_field_diffs": dbl_cmp["nonstrip_field_diffs"],
        "stripped_field_values": dbl_cmp["stripped_field_values"],
        "hits_a": dbl_cmp["hits_a"], "hits_b": dbl_cmp["hits_b"],
        "overflow_a": dbl_cmp["overflow_a"], "overflow_b": dbl_cmp["overflow_b"],
        "overflow_positive_required": True,
        "overflow_positive_satisfied": dbl_cmp["overflow_positive_satisfied"],
        "predicted_hits_design_time": dbl_cmp["predicted_hits_design_time"],
        "predicted_overflow_design_time": dbl_cmp["predicted_overflow_design_time"],
        "realized_matches_prediction": dbl_cmp["realized_matches_prediction"],
        "k0_log2N20_fallback": dbl_cmp["k0_log2N20_fallback"],
        "narrow3_record": dbl_cmp["narrow3_record"],
        "amend1_identity_tables": {"run_a": dbl_a["amend1_identity_table"], "run_b": dbl_b["amend1_identity_table"]},
        "amend1_identities_pass_both": dbl_a["amend1_identities_pass"] and dbl_b["amend1_identities_pass"],
        "double_pass": dbl_cmp["double_pass"],
        "cmp": "runs/S2a6_double_cmp.json",
    },
    "halt_checks": halt_checks,
    "halt_branch_fired": None,
    "stage_outcome": "PASS-S2a",
    "stage_statement": ("All six S2a battery elements passed with no halt branch: declared-diff audit exact; "
                        "Gate-0x field-exact vs L1-AES-R5-P30 (and vs the frozen-build Gate-0x receipt); KAT "
                        "byte-identical; surface-diff battery byte-equal on all seven existing points with the k=3 "
                        "digest committed pre-arm; extended dead anchor 0 hits (no tripwire); determinism double "
                        "byte-identical modulo the strip set with overflow 11,104 > 0. The extended build is "
                        "certified (observation) as frozen-build-plus-declared-extension; Stage S2b dispatch remains "
                        "a Coordinator act. No k=3 reading was made (S2b's job); no verdict composition; no "
                        "status/strength/promotion interpretation."),
    "scope_discipline": {
        "claim_tier": "toy",
        "no_deployed_aes_claims": True,
        "no_published_cryptanalysis_comparisons": True,
        "no_k3_reading": True,
        "no_verdict_composition": True,
        "no_git_add_or_commit": True,
        "no_status_or_promotion_interpretation": True,
        "narrow3_determinism_not_replication": True,
        "extended_build_rampzero_2_30_declined_per_proposal": "the selfcheck_identity_k0 mini-arm doubles as the extended build's identity-seat behavioral check (priced rationale in family_extension_design; the declared diff leaves the identity path untouched)",
        "attribution": "SCOPE-1 (interior-to-interior comparisons schedule-clean under PIN-T0; extended to k=3 by the same structural fact)",
        "floor_is_alive_NARROW1": "the residual floor is a live, decidable excess over the analytic null; no extinction sentence at any k",
    },
    "deviations": [
        {"id": "DEV-S2a-1",
         "description": "Proposal/preregistration line-number citations are off by one against the frozen source in places (s1/s2/s4/s8/s12 whitelist cited at :843-847, actually :842-846; point-emission loop cited at :744 with header at :743; cross-k-nesting loop cited at :776 with header at :775; FREEZE_KS :679 exact). The BINDING semantic content of every cited region is satisfied exactly; the diff audit classifies hunks semantically and all protected regions are untouched.",
         "impact": "none"},
        {"id": "DEV-S2a-2",
         "description": "Declared-diff item (iii) usage-string interpretation: the frozen usage string lists only '(aes|identity)' as the sbox token choices; item (iii) requires the usage string to name the extended point, so the extended usage string lists the full admitted set '(identity|s1|s2|s3|s4|s8|s12|aes)' in admitted-set order. This is the ONLY discretion exercised inside item (iii); recorded here and in the audit so the exact-diff verdict remains checkable.",
         "impact": "none (usage string is not a receipt field and not on any code path)"},
        {"id": "DEV-S2a-3",
         "description": "s3 else-if branch placement: inserted between the s2 and s4 lines (ascending k order), mirroring the existing line style. The declared list pins 'one else-if branch, mirroring the existing s1/s2/s4/s8/s12 lines' but not the exact slot; ascending order chosen and disclosed.",
         "impact": "none"},
        {"id": "DEV-S2a-4",
         "description": "Stderr convention: each invocation redirects stderr (including the /usr/bin/time -l resource report) into runs/X.timing.txt; runs/X.err is created as an empty placeholder exactly as in the S0/S1/BATCH-e5d753 lineage (whose .err files carry the empty-file sha256).",
         "impact": "none"},
        {"id": "DEV-S2a-5",
         "description": "Ordering note: the S2a battery ran in the committed order S2a-1..S2a-6. The Gate-0x rebuild (S2a-2) is a committed battery gate with a known committed expected value (14-hit continuity) and precedes the dead anchor, mirroring the lineage precedent (BATCH-7b798d ran Gate-0x before its dead anchor). The dead anchor was ANALYZED FIRST among extended-build alive readings carrying shape content (before the S2a-6 determinism-double alive reading), per the preregistration ordering rule.",
         "impact": "none"},
        {"id": "DEV-S2a-6",
         "description": "Extra artifacts beyond the minimal deliverable list are retained per the artifact policy: per-receipt analyses, comparison JSONs (S2a2_gate0x_cmp.json, S2a3_kat_cmp.json, S2a4_surface_diff_battery.json, S2a4_freeze_vs_frozen_build.json, S2a4_freeze_commitment_meta.json, S2a6_double_cmp.json) and src/ scripts (s2a_gate0x_cmp.py, s2a_analysis.py, s2a_freeze_digest.py, assemble_results.py) alongside the extended build in src/.",
         "impact": "none"},
    ],
    "unexpected_observations": [
        {"id": "OBS-S2a-1", "rule8": True,
         "observation": "The extended-build Gate-0x receipt is FIELD-EXACT against the frozen build's own certified Gate-0x receipt (zero mismatched fields, zero added fields, zero removed fields; only the value-list arm/timing fields differ) and reproduces the committed 14-hit L1 continuity reading with identical hit_trials, hit_e_detail, stream digests, and table digests. The declared k=3 diff adds NO receipt fields, exactly as the structural no-perturbation argument predicted."},
        {"id": "OBS-S2a-2", "rule8": True,
         "observation": "The determinism double realized readings EQUAL the design-time predictions exactly (hits 12,128; overflow 11,104 at k=1 log2N=20 seed 531001 armid 2 threads 4) on the extended build; the k=1 seat's small-scale behavior carries over unchanged, and the truncation path fires as predicted on the new binary."},
        {"id": "OBS-S2a-3", "rule8": True,
         "observation": "The extended-build dead anchor re-seats 0 hits (seed 531004, r=6, 2^30), matching both predecessor re-seats (BATCH-e5d753 and BATCH-7b798d also read 0); P(0 | pooled r=6 rate ~1.72) ~ 0.18. Passes direction-safe with reduced assurance per the inherited precedent; the CC3-F6 tripwire (>= 9) was never close."},
        {"id": "OBS-S2a-4", "rule8": True,
         "observation": "The k=3 freeze point commits cleanly: positions [0,4,8] (first three of the frozen order), all 16 per-position tables bijective, nestedness check true (AES on P_3, identity elsewhere), concat digest 922e24c9c065eb79c7efcbd536b41111ad70d11a1a49cf56207832e4949c6262, and cross_k_nesting holds over all eight points (P_3 subset P_4 structural). This is a table-construction observation only - no k=3 arm reading exists yet (Stage S2b)."},
        {"id": "OBS-S2a-5", "rule8": True,
         "observation": "The freeze folded selfchecks on the extended build are IDENTICAL to the frozen build's (same seed 363851, same cap-256) on ALL fields including the cap-dependent ones, and the digested extended freeze differs from the digested frozen-build freeze ONLY by the inserted k=3 point entry - a stronger non-perturbation check than the battery's seven-point requirement."},
    ],
    "budget": {
        "wall_clock_seconds_declared": 7200,
        "wall_clock_deadline_epoch": t_start["deadline_epoch"],
        "wall_clock_seconds_used_task_start_to_assembly": now_epoch - t_start["epoch"],
        "binary_invocations": {"used": 7, "max": 8},
        "memory_gb_declared": 4,
        "max_rss_bytes_observed": max(r["max_rss_bytes"] for r in runs if r.get("max_rss_bytes")),
        "per_arm_timeout_wrapper": "timeout 3600 (/opt/homebrew/bin/timeout)",
        "budget_stamps": "budget_stamps.jsonl (task start, S1 gate check, source copy, compile, per-invocation start/end epochs)",
        "binding_baseline_note": "~27 min per 2^30 4-thread arm and ~54 min Gate-0x (2 threads) is the budget contract; measured rates here (Gate-0x 156.5 s, dead anchor 95.0 s, doubles ~0.07-0.08 s) are OPTIMISTIC-RELATIVE and disclosed, never charged as the baseline",
        "exhaustion_policy": "resource_exhaustion, never a reading (rule 5)",
    },
    "artifact_inventory": {
        "RESULTS.json": "this file",
        "budget_stamps.jsonl": "budget stamps",
        "src/affarm046ex.c": "EXTENDED instrument source (frozen copy + declared diff only; sha256 " + sha("src/affarm046ex.c") + ")",
        "src/affarm046ex": "EXTENDED binary (compiled with identical lineage flags; sha256 " + sha("src/affarm046ex") + ")",
        "src/s2a_gate0x_cmp.py": "Gate-0x field comparison under the extended allowed-diff list (fresh)",
        "src/s2a_analysis.py": "per-receipt AMEND-1 analysis: gate0x/dead/double modes (fresh)",
        "src/s2a_freeze_digest.py": "extended freeze digester + surface-diff battery (fresh; lineage convention, EXPECTED_KS extended)",
        "src/assemble_results.py": "this assembler (fresh)",
        "runs/S2a1_diff_audit.txt": "raw unified diff base vs extended source",
        "runs/S2a1_diff_audit.json": "declared-diff audit classification + equality verdict",
        "runs/S2a2_gate0x.json|.err|.timing.txt": "Gate-0x extended rebuild receipt (seed 531001, armid 1, threads 2)",
        "runs/S2a2_gate0x_cmp.json": "Gate-0x field comparison (vs L1 + frozen-build receipt)",
        "runs/S2a2_gate0x_analysis.json": "Gate-0x AMEND-1 analysis",
        "runs/S2a3_pin.json|.err|.timing.txt": "KAT pin receipt on extended build",
        "runs/S2a3_pinidentity.json|.err|.timing.txt": "KAT pinidentity receipt on extended build",
        "runs/S2a3_kat_cmp.json": "KAT byte-identity comparison vs lineage KAT receipts",
        "runs/S2a4_freeze_c_output.json": "extended freeze mode raw C output (seed 363851)",
        "runs/S2a4_freeze.err|.timing.txt": "freeze invocation stderr/timing",
        "runs/R4_table_freeze_ext.json": "EXTENDED FREEZE COMMITMENT (write-once; 8 points; k=3 digest committed pre-arm)",
        "runs/S2a4_surface_diff_battery.json": "surface-diff battery vs committed R3",
        "runs/S2a4_freeze_commitment_meta.json": "R4 sha256/mtime + k=3 digest metadata",
        "runs/S2a4_freeze_vs_frozen_build.json": "supplementary digested-freeze comparison vs frozen build",
        "runs/S2a5_dead_anchor.json|.err|.timing.txt": "extended-build dead anchor receipt (seed 531004, armid 1, threads 4)",
        "runs/S2a5_dead_analysis.json": "dead-anchor analysis (gate/tripwire + AMEND-1 table)",
        "runs/S2a6_double_a.json|.err|.timing.txt": "determinism double receipt run 1 (seed 531001, armid 2, threads 4, log2N=20)",
        "runs/S2a6_double_b.json|.err|.timing.txt": "determinism double receipt run 2 (identical command)",
        "runs/S2a6_double_a_analysis.json": "double run 1 AMEND-1 analysis",
        "runs/S2a6_double_b_analysis.json": "double run 2 AMEND-1 analysis",
        "runs/S2a6_double_cmp.json": "strip-set byte comparison + overflow result",
    },
    "assembled_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "parse_attestation": "RESULTS.json is machine-generated by src/assemble_results.py from the artifacts; parsed whole with python3 json.load after writing, before task completion",
    "inference": INFERENCE,
}

out_path = p("RESULTS.json")
json.dump(results, open(out_path, "w"), indent=1)
json.load(open(out_path))
print("RESULTS.json written and re-parsed OK;", len(json.dumps(results)), "bytes")
