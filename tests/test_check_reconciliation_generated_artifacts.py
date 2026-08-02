"""Mutation coverage for the generated-artifact static checker."""
from __future__ import annotations
from pathlib import Path
import yaml
from tools import check_reconciliation_generated_artifacts as checker

ROOT = Path(__file__).resolve().parents[1]
PHASE = ROOT / "coordination/reconciliation/RECON-20260802-001/tasks/TASK-20260802-991/generated_artifact_phase_table.yaml"
INV = ROOT / "coordination/reconciliation/RECON-20260802-001/reported_conflict_inventory.draft.yaml"
SUC = ROOT / "coordination/reconciliation/RECON-20260802-001/tasks/TASK-20260802-950/successor_map.yaml"

def fake_git(argv, **kwargs):
    parent, path = argv[-1].split(":", 1)
    inv = yaml.safe_load(INV.read_text())
    side = "local_blob" if parent == inv["heads"]["local_ecdlp"]["commit"] else "reanchor_blob"
    if argv[1:4] == ["cat-file", "-t", argv[-1]]:
        return type("P", (), {"returncode": 0, "stdout": "blob\n"})()
    value = next(x[side] for x in inv["conflicts"] if x["path"] == path)
    return type("P", (), {"returncode": 0, "stdout": value + "\n"})()

def base(): return yaml.safe_load(PHASE.read_text())
def run(tmp_path, phase, successor=None, runner=fake_git):
    p = tmp_path / "phase.yaml"; p.write_text(yaml.safe_dump(phase))
    s = SUC
    if successor is not None:
        s = tmp_path / "successor.yaml"; s.write_text(yaml.safe_dump(successor))
    return checker.check(p, INV, s, runner)

def test_immutable_inputs_pass_with_thirty_blob_checks():
    report = checker.check(PHASE, INV, SUC, fake_git)
    assert report["pass"] and report["row_count"] == 15 and report["blob_check_count"] == 30 and report["object_type_check_count"] == 30 and report["batch_trio_count"] == 5

def test_missing_or_extra_generated_path_fails(tmp_path):
    phase = base(); phase["rows"].pop(); assert "generated_path_set_mismatch" in {x["code"] for x in run(tmp_path, phase)["findings"]}

def test_wrong_parent_blob_or_preservation_target_fails(tmp_path):
    phase = base(); phase["rows"][0]["local_blob"] = "0" * 40; assert "parent_blob_or_preservation_mismatch" in {x["code"] for x in run(tmp_path, phase)["findings"]}

def test_coordinated_preservation_root_drift_fails(tmp_path):
    phase = base(); phase["roots"]["local"] = "coordinated-drift"
    phase["rows"][0]["local_preservation_target"] = "coordinated-drift/" + phase["rows"][0]["inherited_path"]
    phase["rows"][0]["local_non_authorizing_marker"] = "RECON-20260802-001:NONAUT:coordinated-drift:" + phase["rows"][0]["inherited_path"]
    assert "preservation_root_mismatch" in {x["code"] for x in run(tmp_path, phase)["findings"]}

def test_marker_mismatch_or_duplicate_fails(tmp_path):
    phase = base(); phase["rows"][0]["local_non_authorizing_marker"] = "bad"; assert "marker_mismatch_or_duplicate" in {x["code"] for x in run(tmp_path, phase)["findings"]}

def test_zero_or_multiple_final_actions_fails(tmp_path):
    phase = base(); phase["rows"][1]["final_output_path"] = phase["rows"][0]["final_output_path"]; assert "final_action_cardinality" in {x["code"] for x in run(tmp_path, phase)["findings"]}

def test_final_output_outside_task_955_scope_fails(tmp_path):
    phase = base(); phase["rows"][0]["final_output_path"] = "elsewhere"; assert "final_output_outside_task_955_scope" in {x["code"] for x in run(tmp_path, phase)["findings"]}

def test_non_intermediate_reanchor_equality_fails(tmp_path):
    phase = base(); phase["phase_contract"]["inherited_reanchor_equality"] = "final"; assert "non_intermediate_reanchor_equality" in {x["code"] for x in run(tmp_path, phase)["findings"]}

def test_incomplete_batch_trio_fails(tmp_path):
    phase = base(); phase["rows"][0]["artifact_kind"] = "wrong"; assert "incomplete_batch_trio" in {x["code"] for x in run(tmp_path, phase)["findings"]}

def test_phase_contract_mismatch_fails(tmp_path):
    phase = base(); phase["phase_contract"]["marker_mutates_preserved_blob"] = True; assert "phase_contract_mismatch" in {x["code"] for x in run(tmp_path, phase)["findings"]}

def test_phase_envelope_and_final_validation_drift_fail(tmp_path):
    phase = base(); phase["status"] = "wrong"; assert "phase_envelope_mismatch" in {x["code"] for x in run(tmp_path, phase)["findings"]}
    phase = base(); phase["phase_contract"]["final_validation"].pop(); assert "phase_contract_mismatch" in {x["code"] for x in run(tmp_path, phase)["findings"]}

def test_scope_addition_mismatch_and_overlap_fail(tmp_path):
    phase = base(); phase["task_955_scope_additions"] = ["wrong"]; assert "task_955_scope_additions_mismatch" in {x["code"] for x in run(tmp_path, phase)["findings"]}

    phase = base(); successor = yaml.safe_load(SUC.read_text())
    successor["task_scope_map"]["TASK-20260802-951"]["write_scope"].append(
        "coordination/reconciliation/RECON-20260802-001/tasks/TASK-20260802-955/**")
    assert "task_955_scope_additions_overlap" in {x["code"] for x in run(tmp_path, phase, successor)["findings"]}

def test_non_blob_parent_object_type_fails(tmp_path):
    def tree_git(argv, **kwargs):
        result = fake_git(argv, **kwargs)
        if argv[1:3] == ["cat-file", "-t"]:
            return type("P", (), {"returncode": 0, "stdout": "tree\n"})()
        return result
    assert "parent_object_type_invalid" in {x["code"] for x in run(tmp_path, base(), runner=tree_git)["findings"]}
