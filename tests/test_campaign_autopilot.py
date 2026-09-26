"""Exercise the actual idle-to-design path and bounded-action continuation."""
from __future__ import annotations

import json
import hashlib
import subprocess
from pathlib import Path

from orchestration.campaign import autopilot


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_empty_execution_queue_selects_open_ecc_idea(tmp_path: Path) -> None:
    _write(tmp_path / "orchestration/research-priority.yaml", "ecc_areas: [ICEX]\n")
    _write(tmp_path / "ledger/proposals/IDEA-20260926-abcdef.yaml",
           "idea:\n  id: IDEA-20260926-abcdef\n  status: proposed\n"
           "  question_id: RQ-ICEX-abcdef\n  recommended_priority: high\n")
    action = autopilot.select_next(tmp_path)
    assert action is not None
    assert (action.kind, action.target, action.role) == (
        "design", "IDEA-20260926-abcdef", "coordinator")
    assert autopilot.select_next(tmp_path, excluded={action.key}).kind == "portfolio"


def test_design_to_approved_plan_then_partial_run_needs_reconciliation(tmp_path: Path) -> None:
    _write(tmp_path / "orchestration/research-priority.yaml", "ecc_areas: [ICEX]\n")
    idea = "IDEA-20260926-abcdef"
    exp = "EXP-ICEX-abcdef"
    _write(tmp_path / "ledger/proposals/idea.yaml",
           f"idea:\n  id: {idea}\n  status: proposed\n"
           "  question_id: RQ-ICEX-abcdef\n")
    assert autopilot.select_next(tmp_path).kind == "design"

    _write(tmp_path / "ledger/hypotheses/H-ICEX-abcdef.yaml",
           f"hypothesis:\n  id: H-ICEX-abcdef\n  idea_id: {idea}\n")
    spec_rel = f"experiments/{exp}/specification.yaml"
    spec = tmp_path / spec_rel
    _write(spec, f"experiment:\n  id: {exp}\n  status: approved\n"
                 "  approved_by: coordinator\n  frozen: true\n")
    source = tmp_path / "driver.py"
    _write(source, "print('toy')\n")
    _write(tmp_path / "queue.json", "{}\n")
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    plan = {"schema": "crypto.autoresearch.trial_plan.v1", "frozen": True,
            "experiment_id": exp, "task_id": "TASK-20260926-abcdef",
            "approved_by": "coordinator", "specification": spec_rel,
            "specification_sha256": sha(spec), "queue": "queue.json",
            "source_sha256": {"driver.py": sha(source)},
            "trials": [{"id": "trial-1", "run_id": "RUN-ICEX-abcdef",
                        "argv": ["python3", "driver.py"],
                        "check_argv": ["python3", "driver.py"],
                        "artifacts": ["manifest.yaml", "raw-result.json"],
                        "memory_mb": 128}]}
    _write(tmp_path / f"experiments/{exp}/trial-plan.json", json.dumps(plan))
    assert (autopilot.select_next(tmp_path).kind,
            autopilot.select_next(tmp_path).target) == ("run", exp)

    (tmp_path / f"experiments/{exp}/runs/RUN-ICEX-abcdef").mkdir(parents=True)
    # An existing attempt without a verified receipt is not safe to rerun.
    assert autopilot.select_next(tmp_path).kind == "repair"


def test_model_failover_only_before_tools_or_checkout_effects(
        tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(autopilot.shutil, "which", lambda _: "/bin/opencode")
    monkeypatch.setattr(autopilot, "_git_state", lambda _: "same checkout")
    monkeypatch.setattr(autopilot, "candidates", lambda *_: [
        ("first", "first/cheap", {"policy": "coordinator-orchestration-code",
                                   "verified_model": False}),
        ("second", "second/strong", {"policy": "coordinator-orchestration-code",
                                     "verified_model": True})])
    calls = []

    def run(command, **kwargs):
        assert command[5] == "build"  # top-level dispatcher can invoke the subagent
        calls.append(command[7])
        kwargs["stdout"].write(json.dumps({"part": {"type": "step-finish",
            "tokens": {"input": 100, "output": 20}, "cost": 0.001}}) + "\n")
        return subprocess.CompletedProcess(command, 1 if len(calls) == 1 else 0)

    action = autopilot.Action("design", "IDEA-TEST", "design it", "coordinator")
    result = autopilot.invoke_opencode(action, tmp_path, tmp_path,
        backends=["first", "second"], timeout=10, run_command=run)
    assert result["ok"] is True
    assert calls == ["first/cheap", "second/strong"]
    assert result["attempts"][1]["fallback_used"] is True
    assert result["attempts"][1]["input_tokens"] == 100

    def partial(command, **kwargs):
        kwargs["stdout"].write(json.dumps({"part": {"type": "tool"}}) + "\n")
        return subprocess.CompletedProcess(command, 1)

    calls.clear()
    stopped = autopilot.invoke_opencode(action, tmp_path, tmp_path,
        backends=["first", "second"], timeout=10, run_command=partial)
    assert stopped["ok"] is False
    assert len(stopped["attempts"]) == 1
    assert "reconcile" in stopped["reason"]


def test_one_invocation_designs_runs_and_reconciles(tmp_path: Path) -> None:
    observed = []
    phase = [0]

    def select(_repo, *, excluded):
        if phase[0] == 0:
            return autopilot.Action("design", "IDEA-1", "design", "coordinator")
        if phase[0] == 1:
            return autopilot.Action("run", "EXP-1", "run", "executor")
        return None

    def invoke(action, _repo, _dir, **_kwargs):
        observed.append(action.kind)
        phase[0] += 1
        return {"ok": True, "reason": "worker returned", "attempts": [
            {"cost_usd": 0.002, "input_tokens": 120, "output_tokens": 20,
             "fallback_used": False}]}

    state = autopilot.supervise(tmp_path, tmp_path / "state", backends=["test"],
        max_actions=3, selector=select, invoke=invoke)
    assert observed == ["design", "run", "review"]
    assert state["attempts"] == state["completed_actions"] == 3
    assert state["pending_reconcile"] is None
    metrics = autopilot.report(tmp_path / "state")
    assert metrics["actions_attempted"] == 3
    assert metrics["measured_cost_usd"] == 0.006
    assert metrics["verified_discoveries"] is None


def test_restart_reconciles_interrupted_action(tmp_path: Path) -> None:
    state_dir = tmp_path / "state"
    state_dir.mkdir()
    _write(state_dir / "state.json", json.dumps({
        "attempts": 0, "completed_actions": 0, "cooldowns": {},
        "inflight": {"kind": "run", "target": "EXP-1", "key": "run:EXP-1",
                     "attempt_id": "old"}}))
    seen = []
    autopilot.supervise(tmp_path, state_dir, backends=[], max_actions=1,
        selector=lambda *_args, **_kwargs: None,
        invoke=lambda action, *_args, **_kwargs: (seen.append(action.kind) or
            {"ok": True, "attempts": []}))
    assert seen == ["review"]
    assert autopilot.report(state_dir)["verified_discoveries"] is None


def test_unchanged_portfolio_pass_does_not_repeat_every_five_minutes(tmp_path: Path) -> None:
    action = autopilot.Action("portfolio", "ecdlp", "rank", "coordinator")
    state = autopilot.supervise(tmp_path, tmp_path / "state", backends=[],
        max_actions=2, retry_seconds=300,
        selector=lambda _repo, *, excluded: None if action.key in excluded else action,
        invoke=lambda *_args, **_kwargs: {"ok": True, "attempts": []},
        clock=lambda: 1000.0)
    assert state["attempts"] == 1
    assert state["cooldowns"][action.key] == 1000 + 86400
    assert autopilot.report(tmp_path / "state")["no_progress_actions"] == 1


def test_new_verified_trial_coverage_can_continue_after_review(
        tmp_path: Path, monkeypatch) -> None:
    stage = [0]
    monkeypatch.setattr(autopilot, "_execution_snapshot",
                        lambda *_args: "new" if stage[0] else "old")

    def select(_repo, *, excluded):
        return autopilot.Action("run", "EXP-ICEX-abcdef", "run", "executor")

    def invoke(action, *_args, **_kwargs):
        if action.kind == "run":
            stage[0] = 1
        return {"ok": True, "attempts": []}

    state = autopilot.supervise(tmp_path, tmp_path / "state", backends=[],
        max_actions=2, selector=select, invoke=invoke)
    assert state["pending_reconcile"] is None
    assert "run:EXP-ICEX-abcdef" not in state["cooldowns"]
