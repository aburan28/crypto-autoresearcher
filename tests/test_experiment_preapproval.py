"""The preapproval probe must never turn a draft into executable work."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import pytest
import yaml

from tools import experiment_preapproval as probe
from tools import experiment_execution as execution
from tools import newest_experiments as selector


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def _git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args], text=True,
                                   stderr=subprocess.DEVNULL).strip()


def fixture(root: Path) -> tuple[dict, dict]:
    exp = "EXP-ECDLP-aabbcc"
    goal = "GOAL-ECDLP-aabbcc"
    batch = "BATCH-aabbcc"
    decision = "DEC-20261017-aabbcc"
    task_id = "TASK-20261017-aabbcc"
    archive_id = "TASK-20261017-bbccdd"
    spec_rel = f"experiments/{exp}/specification.yaml"
    plan_rel = f"experiments/{exp}/trial-plan.json"
    queue_rel = f"coordination/goals/{goal}/batches/{batch}/dispatch_queue.json"
    handoff_rel = f"ledger/handoffs/{task_id}.yaml"
    source = root / "driver.py"
    source.write_text("# sealed fixture driver; never executed by this test\n")
    digest = _sha(source.read_bytes())
    (root / "orchestration").mkdir()
    (root / "orchestration/research-priority.yaml").write_text("ecc_areas: [ECDLP]\n")
    _write(root / "ledger" / "goals" / goal / "goal.yaml",
           {"research_goal": {"id": goal, "campaign_budget": {"max_concurrent": 2}}})
    lane = {"schema": "crypto.autoresearch.goal_lane.v1", "goal_id": goal,
            "batch_id": batch, "dispatch_queue_path": queue_rel, "opened_by": "coordinator-test"}
    _write(root / "coordination" / "goals" / goal / "lanes" / f"{batch}.lane.json", lane)
    scientific = {"id": exp, "goal_id": goal, "hypothesis_id": "H-ECDLP-aabbcc",
                  "version": 1, "metrics": ["valid certificate"], "budget": {"maximum_runs": 1},
                  "controls": ["planted positive"], "stopping_rules": ["one bounded call"],
                  "invalidation_rules": ["checker mismatch invalidates"],
                  "success_criterion": "a checked relation", "falsification_criterion": "no checked relation",
                  "decision_impact": {"on_positive": "extend", "on_negative": "redesign"},
                  "input_bindings": {"driver": {"path": "driver.py", "sha256": digest}}}
    _write(root / spec_rel, {"experiment": {**scientific, "status": "review_required",
                                            "approved_by": None, "frozen": False,
                                            "execution_authorized": False}})
    preview_dir = root / "preview"
    preview_dir.mkdir()
    spec_preview = preview_dir / "specification.yaml"
    _write(spec_preview, {"experiment": {**scientific, "status": "approved",
                                          "approved_by": decision, "frozen": True,
                                          "execution_authorized": True}})
    trial = {"id": "seed-1", "run_id": "RUN-ECDLP-a1b2c3", "depends_on": [],
             "argv": ["python3", "driver.py", "measure", "{run_dir}"],
             "check_argv": ["python3", "driver.py", "check", "{run_dir}"],
             "memory_mb": 256, "watchdog_seconds": 30,
             "watchdog_reason": "test machine guard",
             "artifacts": ["manifest.yaml", "raw-result.json", "calls-manifest.json", "calls.tar.gz"]}
    plan = {"schema": execution.PLAN_SCHEMA, "experiment_id": exp,
            "task_id": task_id, "approved_by": decision, "frozen": True,
            "specification": spec_rel, "specification_sha256": _sha(spec_preview.read_bytes()),
            "queue": queue_rel, "source_sha256": {"driver.py": digest},
            "input_sha256": {"driver.py": digest}, "trials": [trial]}
    _write(root / plan_rel, {**plan, "frozen": False, "approved_by": None,
                             "task_id": None, "queue": None})
    plan_preview = preview_dir / "trial-plan.json"
    _write(plan_preview, plan)
    binding = {"mode": "experiments", "kind": "run", "experiment_id": exp,
               "trial_plan": plan_rel, "trial_plan_sha256": _sha(plan_preview.read_bytes()),
               "approved_by": decision}
    handoff = {"id": task_id, "role": "executor", "archived_by": archive_id,
               "objective": "Check one sealed fixture", "uncertainty_reduced": "whether it checks",
               "inputs": [spec_rel], "constraints": ["run only after approval"],
               "deliverables": [f"experiments/{exp}/runs/{trial['run_id']}/manifest.yaml"],
               "completion_gate": ["certificate verified"],
               "budget": {"maximum_runs": 1, "memory_gb": 1, "wall_clock_seconds": 120},
               "inference": {"policy": "executor-implementation", "delivery": "interactive"},
               "execution": binding}
    handoff_preview = preview_dir / "handoff.yaml"
    _write(handoff_preview, {"handoff": handoff})
    run_base = f"experiments/{exp}/runs/{trial['run_id']}"
    required = [f"{run_base}/{name}" for name in (*execution.GENERATED, *trial["artifacts"])]
    producer = {"id": task_id, "title": "fixture producer", "role": "executor",
                "state": "queued", "priority": 90, "review_required": False,
                "depends_on": [], "read_scope": [spec_rel],
                "write_scope": [f"experiments/{exp}/runs/"],
                "artifact_paths": required, "archived_by": archive_id, "handoff": handoff}
    archive_receipt = f"coordination/goals/{goal}/batches/{batch}/archives/{archive_id}/snapshot-receipt.json"
    archive_handoff = {"id": archive_id, "role": "coordinator", "objective": "archive fixture",
                       "uncertainty_reduced": "custody", "inputs": [spec_rel],
                       "constraints": ["exact bytes"], "deliverables": [archive_receipt],
                       "completion_gate": ["receipt checked"], "budget": {"maximum_runs": 0}}
    archive = {"id": archive_id, "title": "fixture archive", "role": "coordinator",
               "state": "queued", "priority": 80, "review_required": False,
               "depends_on": [task_id], "read_scope": [f"experiments/{exp}/runs/"],
               "write_scope": [f"coordination/goals/{goal}/batches/{batch}/archives/{archive_id}/"],
               "artifact_paths": [archive_receipt], "archived_by": archive_id,
               "handoff": archive_handoff,
               "archive": {"kind": "snapshot", "source_task_ids": [task_id],
                           "commit_sha": None, "parent_sha": None,
                           "path_sha256": {}, "record_ids": [exp]}}
    queue_preview = preview_dir / "queue.json"
    _write(queue_preview, {"schema": "crypto.autoresearch.dispatch_queue.v1",
                           "goal_id": goal, "objective": "fixture queue", "max_concurrent": 1,
                           "tasks": [producer, archive]})
    _git(root, "init", "-q")
    _git(root, "config", "user.name", "Fixture")
    _git(root, "config", "user.email", "fixture@example.invalid")
    _git(root, "config", "gc.auto", "0")
    _git(root, "add", "driver.py", spec_rel, plan_rel,
         f"ledger/goals/{goal}/goal.yaml",
         f"coordination/goals/{goal}/lanes/{batch}.lane.json",
         "orchestration/research-priority.yaml")
    _git(root, "commit", "-qm", "sealed input fixture")
    _git(root, "update-ref", "refs/remotes/origin/main", "HEAD")
    packet = {"schema": probe.SCHEMA, "experiment_id": exp,
              "approval_decision_id": decision, "specification": spec_rel,
              "trial_plan": plan_rel, "queue": queue_rel, "handoff": handoff_rel,
              "preview": {"specification": str(spec_preview), "trial_plan": str(plan_preview),
                          "queue": str(queue_preview), "handoff": str(handoff_preview)},
              "source_ref": "origin/main", "lane_id": batch,
              "execution_route": {"kind": "implementation", "reason": "fixture requires a checked driver"}}
    return packet, {"root": root, "plan": plan, "trial": trial, "queue": queue_preview,
                    "spec": spec_preview, "plan_preview": plan_preview}


def test_complete_packet_is_only_approvable_until_exact_bytes_are_committed(tmp_path):
    packet, files = fixture(tmp_path)
    before = sorted(str(p.relative_to(tmp_path)) for p in tmp_path.rglob("*") if p.is_file())
    result = probe.assess(tmp_path, packet)
    after = sorted(str(p.relative_to(tmp_path)) for p in tmp_path.rglob("*") if p.is_file())
    assert before == after
    assert result["approvable"], result["blockers"]
    assert "execution_state" not in result
    assert selector.newest_runnable(tmp_path) == []
    with pytest.raises(execution.ExecutionError):
        execution.load_plan(tmp_path, tmp_path / packet["trial_plan"])
    for key in ("specification", "trial_plan", "queue", "handoff"):
        target = tmp_path / packet[key]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(Path(packet["preview"][key]).read_bytes())
    assert selector.execution_progress(tmp_path / "experiments" / packet["experiment_id"], tmp_path)["execution_state"] == "ready"
    with pytest.raises(execution.ExecutionError):
        execution.authorize(tmp_path, tmp_path / packet["trial_plan"],
                            files["plan"], "unclaimed-owner", 1)
    canonical_plan = tmp_path / packet["trial_plan"]
    canonical_plan.write_bytes(canonical_plan.read_bytes() + b" ")
    assert selector.execution_progress(tmp_path / "experiments" / packet["experiment_id"], tmp_path)["execution_state"] != "ready"


@pytest.mark.parametrize("damage,fragment", [
    ("missing_raw_bundle", "executor archive coverage missing"),
    ("missing_supervisor", "executor archive coverage missing"),
    ("stale_source", "SHA-256 mismatch"),
    ("stale_queue_binding", "binding mismatch"),
    ("missing_lane", "no lawful open lane"),
    ("uncommitted_lane", "goal lane is not committed"),
    ("uncommitted_draft", "canonical draft specification is not committed"),
    ("prewritten_outcome", "outcome field outcome is prewritten"),
    ("missing_route", "implementation route requires reason"),
])
def test_prospective_packet_refuses_broken_bindings(tmp_path, damage, fragment):
    packet, files = fixture(tmp_path)
    queue = json.loads(files["queue"].read_text())
    if damage == "missing_raw_bundle":
        queue["tasks"][0]["artifact_paths"].remove(next(p for p in queue["tasks"][0]["artifact_paths"] if p.endswith("calls.tar.gz")))
    elif damage == "missing_supervisor":
        queue["tasks"][0]["artifact_paths"].remove(next(p for p in queue["tasks"][0]["artifact_paths"] if p.endswith("launch.json")))
    elif damage == "stale_source":
        (tmp_path / "driver.py").write_text("changed\n")
    elif damage == "stale_queue_binding":
        queue["tasks"][0]["handoff"]["execution"]["trial_plan_sha256"] = "0" * 64
    elif damage == "missing_lane":
        packet["lane_id"] = "BATCH-ffffff"
    elif damage == "uncommitted_lane":
        lane = tmp_path / "coordination/goals/GOAL-ECDLP-aabbcc/lanes/BATCH-aabbcc.lane.json"
        lane.write_bytes(lane.read_bytes() + b" ")
    elif damage == "uncommitted_draft":
        draft = tmp_path / packet["specification"]
        draft.write_bytes(draft.read_bytes() + b" ")
    elif damage == "prewritten_outcome":
        candidate = json.loads(files["spec"].read_text())
        candidate["experiment"]["outcome"] = "claimed success"
        _write(files["spec"], candidate)
    else:
        packet["execution_route"]["reason"] = ""
    if damage in ("missing_raw_bundle", "missing_supervisor", "stale_queue_binding"):
        _write(files["queue"], queue)
    result = probe.assess(tmp_path, packet)
    assert not result["approvable"]
    assert any(fragment in item for item in result["blockers"]), result["blockers"]
