#!/usr/bin/env python3
"""Fail-closed static validation for RECON-20260802-001 generated artifacts."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

RECON = "RECON-20260802-001"
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PHASE = ROOT / "coordination/reconciliation/RECON-20260802-001/tasks/TASK-20260802-991/generated_artifact_phase_table.yaml"
DEFAULT_INVENTORY = ROOT / "coordination/reconciliation/RECON-20260802-001/reported_conflict_inventory.draft.yaml"
DEFAULT_SUCCESSOR = ROOT / "coordination/reconciliation/RECON-20260802-001/tasks/TASK-20260802-950/successor_map.yaml"
KINDS = {"queue_json", "plan_json", "plan_markdown"}
PHASES = ["preserve_local_parent_blob", "preserve_reanchor_parent_blob",
          "resolve_inherited_path_to_reanchor_intermediate",
          "record_parent_variants_non_authorizing",
          "regenerate_one_final_output_in_place", "validate_regenerated_trio"]
MARKER_STORAGE = "coordination/reconciliation/RECON-20260802-001/tasks/TASK-20260802-955/generated_artifact_phase_manifest.yaml"
SCOPE_ADDITIONS = [MARKER_STORAGE,
                   "coordination/reconciliation/RECON-20260802-001/tasks/TASK-20260802-955/generated_artifact_static_check.json"]
EXPECTED_BATCHES = {f"BATCH-0{number}" for number in range(20, 25)}
KIND_PATHS = {"queue_json": "dispatch_queue.json", "plan_json": "dispatch_plan.json",
              "plan_markdown": "dispatch_plan.md"}
FINAL_VALIDATION = [
    "every batch has exactly one queue, one JSON plan, and one Markdown plan",
    "each regenerated plan is derived from its regenerated queue",
    "each final output is inside TASK-20260802-955 exact write scope",
    "no final output equals a preservation target",
    "both parent variants remain byte-exact and non-authorizing",
    "regenerated queues and plans cite only reconciled receipt or successor IDs",
]


def load(path: Path):
    if yaml is None:
        raise ValueError("PyYAML unavailable")
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"not a mapping: {path}")
    return value


def blob(parent: str, path: str, runner=subprocess.run) -> str:
    process = runner(["git", "rev-parse", f"{parent}:{path}"], cwd=ROOT,
                     check=False, capture_output=True, text=True)
    if process.returncode:
        raise ValueError(f"unavailable parent object: {parent}:{path}")
    return process.stdout.strip()


def object_type(parent: str, path: str, runner=subprocess.run) -> str:
    process = runner(["git", "cat-file", "-t", f"{parent}:{path}"], cwd=ROOT,
                     check=False, capture_output=True, text=True)
    if process.returncode:
        raise ValueError(f"unavailable parent object: {parent}:{path}")
    return process.stdout.strip()


def scope_overlaps(path: str, scope: str) -> bool:
    return path == scope or (scope.endswith("/**") and path.startswith(scope[:-3]))


def check(phase_path=DEFAULT_PHASE, inventory_path=DEFAULT_INVENTORY,
          successor_path=DEFAULT_SUCCESSOR, runner=subprocess.run):
    findings = []
    def fail(code, detail):
        findings.append({"code": code, "detail": detail})
    try:
        phase, inventory, successor = map(load, (Path(phase_path), Path(inventory_path), Path(successor_path)))
    except (OSError, ValueError) as exc:
        return {"schema": "crypto.autoresearch.generated_artifact_static_check.v1", "pass": False,
                "findings": [{"code": "input_invalid", "detail": str(exc)}]}
    rows = phase.get("rows") if isinstance(phase.get("rows"), list) else []
    envelope = {"schema": "crypto.autoresearch.reconciliation_generated_artifact_phase_table.v1",
                "reconciliation_id": RECON, "task_id": "TASK-20260802-991",
                "status": "coordinator_approved_for_snapshot",
                "authoritative_research_evidence": False, "merge_authorized": False}
    for key, value in envelope.items():
        if phase.get(key) != value: fail("phase_envelope_mismatch", key)
    expected = {x.get("path"): x for x in inventory.get("conflicts", [])
                if isinstance(x, dict) and x.get("class") == "dispatch_artifact_collision"}
    actual = {x.get("inherited_path"): x for x in rows if isinstance(x, dict)}
    if set(actual) != set(expected): fail("generated_path_set_mismatch", "missing or extra generated path")
    if len(rows) != 15 or len(actual) != 15: fail("generated_path_cardinality", "expected exactly 15 unique rows")
    parents = inventory.get("heads", {})
    local_parent = parents.get("local_ecdlp", {}).get("commit")
    reanchor_parent = parents.get("audited_reanchor", {}).get("commit")
    roots = phase.get("roots", {})
    preservation = successor.get("preservation_namespaces", {})
    if roots.get("local") != preservation.get("local_root") or roots.get("reanchor") != preservation.get("reanchor_root"):
        fail("preservation_root_mismatch", "phase roots must bind successor namespaces")
    contract = phase.get("phase_contract", {})
    exact_contract = {
        "ordered_phases": PHASES, "inherited_reanchor_equality": "intermediate_only",
        "final_action_cardinality_per_path": 1, "final_action": "regenerate_in_place",
        "final_output_rule": "final_output_path_must_equal_inherited_path",
        "preservation_rule": "preserved_bytes_must_equal_named_parent_blobs",
        "marker_storage": MARKER_STORAGE, "marker_mutates_preserved_blob": False,
        "queue_regenerator": "coordinator_authors_reconciled_queue_from_preserved_receipts_and_reference_rewrite_manifest",
        "plan_regenerator": "python3 tools/research_dispatch.py <queue_path> --output <plan_json_path> --report <plan_md_path>",
        "final_validation": FINAL_VALIDATION,
    }
    for key, value in exact_contract.items():
        if contract.get(key) != value: fail("phase_contract_mismatch", key)
    additions = phase.get("task_955_scope_additions")
    if additions != SCOPE_ADDITIONS: fail("task_955_scope_additions_mismatch", "exact additions required")
    for task, task_data in successor.get("task_scope_map", {}).items():
        if task == "TASK-20260802-955" or not isinstance(task_data, dict): continue
        for addition in SCOPE_ADDITIONS:
            if any(scope_overlaps(addition, candidate) for candidate in task_data.get("write_scope", [])):
                fail("task_955_scope_additions_overlap", f"{task}:{addition}")
    scope = successor.get("task_scope_map", {}).get("TASK-20260802-955", {}).get("write_scope", [])
    marker_seen = set(); final_seen = set(); batches = {}
    blob_checks = 0; object_type_checks = 0
    for row in rows:
        path = row.get("inherited_path"); expected_row = expected.get(path, {})
        if row.get("local_blob") != expected_row.get("local_blob") or row.get("reanchor_blob") != expected_row.get("reanchor_blob"):
            fail("parent_blob_or_preservation_mismatch", str(path))
        for side, parent in (("local", local_parent), ("reanchor", reanchor_parent)):
            target = row.get(f"{side}_preservation_target")
            required = f"{roots.get(side, '')}/{path}"
            if target != required: fail("parent_blob_or_preservation_mismatch", f"{side} target {path}")
            try:
                observed = blob(parent, path, runner)
                blob_checks += 1
                if observed != row.get(f"{side}_blob"): fail("parent_blob_or_preservation_mismatch", f"{side} blob {path}")
                if object_type(parent, path, runner) != "blob": fail("parent_object_type_invalid", f"{side} {path}")
                object_type_checks += 1
            except ValueError as exc: fail("parent_object_unavailable", str(exc))
            marker = row.get(f"{side}_non_authorizing_marker")
            required_marker = f"{RECON}:NONAUT:{roots.get(side, '').rsplit('/', 1)[-1]}:{path}"
            if marker != required_marker or marker in marker_seen: fail("marker_mismatch_or_duplicate", f"{side} {path}")
            marker_seen.add(marker)
        if row.get("intermediate_action") != "retain_reanchor_blob_at_inherited_path" or contract.get("inherited_reanchor_equality") != "intermediate_only":
            fail("non_intermediate_reanchor_equality", str(path))
        if row.get("final_action") != "regenerate_in_place": fail("final_action_cardinality", str(path))
        output = row.get("final_output_path")
        if output in final_seen: fail("final_action_cardinality", f"duplicate {output}")
        final_seen.add(output)
        if output != path or output not in scope: fail("final_output_outside_task_955_scope", str(path))
        if output in (row.get("local_preservation_target"), row.get("reanchor_preservation_target")):
            fail("final_output_equals_preservation_target", str(path))
        expected_suffix = KIND_PATHS.get(row.get("artifact_kind"))
        if not expected_suffix or not path.endswith(f"/{row.get('batch')}/{expected_suffix}"):
            fail("artifact_kind_path_mismatch", str(path))
        batches.setdefault(row.get("batch"), set()).add(row.get("artifact_kind"))
    if len(final_seen) != len(rows): fail("final_action_cardinality", "zero or multiple final actions")
    for batch, kinds in batches.items():
        if kinds != KINDS: fail("incomplete_batch_trio", str(batch))
    if set(batches) != EXPECTED_BATCHES: fail("batch_id_set_mismatch", "expected BATCH-020 through BATCH-024")
    if len(batches) != 5: fail("incomplete_batch_trio", "expected five batches")
    return {"schema": "crypto.autoresearch.generated_artifact_static_check.v1", "reconciliation_id": RECON,
            "pass": not findings, "row_count": len(rows), "blob_check_count": blob_checks,
            "object_type_check_count": object_type_checks,
            "batch_trio_count": sum(k == KINDS for k in batches.values()), "findings": findings}


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", type=Path, default=DEFAULT_PHASE)
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    parser.add_argument("--successor-map", type=Path, default=DEFAULT_SUCCESSOR)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args(argv)
    report = check(args.phase, args.inventory, args.successor_map)
    encoded = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.report: args.report.write_text(encoded, encoding="utf-8")
    else: sys.stdout.write(encoded)
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
