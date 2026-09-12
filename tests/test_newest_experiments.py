from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "newest_experiments", ROOT / "tools/newest_experiments.py")
mod = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(mod)


def _write_exp(root: Path, exp_id: str, *, designed_at: str,
               approved: bool = True, report: bool = False,
               has_runs: bool = False, supersedes: str | None = None,
               goal_id: str | None = None) -> None:
    d = root / "experiments" / exp_id
    d.mkdir(parents=True)
    body = {"experiment": {
        "id": exp_id,
        "status": "approved" if approved else "proposed",
        "approved_by": "coordinator" if approved else None,
        "frozen": approved,
        "execution_authorized": approved,
        "designed_at": designed_at,
        "supersedes": supersedes,
        "goal_id": goal_id,
    }}
    (d / "specification.yaml").write_text(yaml.safe_dump(body))
    if report:
        (d / "execution-report.yaml").write_text("execution_report: {}\n")
    if has_runs:
        # Legacy activity is insufficient to establish coverage. It must not
        # be blindly re-executed, but must remain visible for reconciliation.
        run_dir = d / "runs" / f"RUN-{exp_id.split('-', 1)[1]}-001"
        run_dir.mkdir(parents=True)
        (run_dir / "manifest.yaml").write_text("run: {}\n")


def test_newest_runnable_excludes_unreconciled_activity_and_orders_newest(tmp_path):
    (tmp_path / "orchestration").mkdir()
    (tmp_path / "orchestration/research-priority.yaml").write_text(
        "ecc_areas: [ECDLP]\n")
    _write_exp(tmp_path, "EXP-ECDLP-old111", designed_at="2026-09-01")
    _write_exp(tmp_path, "EXP-ECDLP-new222", designed_at="2026-09-07")
    _write_exp(tmp_path, "EXP-ECDLP-done33", designed_at="2026-09-08", report=True)
    _write_exp(tmp_path, "EXP-AES-new444", designed_at="2026-09-09")
    _write_exp(tmp_path, "EXP-ECDLP-no555", designed_at="2026-09-10", approved=False)
    _write_exp(tmp_path, "EXP-ECDLP-ran666", designed_at="2026-09-11", has_runs=True)

    rows = mod.newest_runnable(tmp_path)
    assert [r["id"] for r in rows] == [
        "EXP-ECDLP-new222", "EXP-ECDLP-old111", "EXP-AES-new444"]
    assert all("specification.yaml" in r["specification"] for r in rows)
    diagnostic = mod.newest_runnable(tmp_path, include_blocked=True)
    unresolved = {r["id"] for r in diagnostic if r["execution_state"] == "needs_reconciliation"}
    assert unresolved == {"EXP-ECDLP-done33", "EXP-ECDLP-ran666"}


def test_populated_runs_dir_is_neither_completion_nor_permission_to_rerun(tmp_path):
    (tmp_path / "orchestration").mkdir()
    (tmp_path / "orchestration/research-priority.yaml").write_text(
        "ecc_areas: [ECDLP]\n")
    _write_exp(tmp_path, "EXP-ECDLP-ran777", designed_at="2026-09-12", has_runs=True)

    assert mod.newest_runnable(tmp_path) == []
    assert not mod._completed(tmp_path / "experiments/EXP-ECDLP-ran777")
    rows = mod.newest_runnable(tmp_path, include_blocked=True)
    assert rows[0]["execution_state"] == "needs_reconciliation"


def test_newest_runnable_skips_an_experiment_superseded_before_it_ran(tmp_path):
    """Superseded immutable history is not a candidate for belated execution."""
    (tmp_path / "orchestration").mkdir()
    (tmp_path / "orchestration/research-priority.yaml").write_text(
        "ecc_areas: [ECDLP]\n")
    _write_exp(tmp_path, "EXP-ECDLP-9d04ba", designed_at="2026-08-03")
    _write_exp(tmp_path, "EXP-ECDLP-c83476", designed_at="2026-09-01",
               supersedes="EXP-ECDLP-9d04ba")

    rows = mod.newest_runnable(tmp_path)
    assert [r["id"] for r in rows] == ["EXP-ECDLP-c83476"]


def test_goal_filter_excludes_other_goals_and_unassigned_experiments(tmp_path):
    (tmp_path / "orchestration").mkdir()
    (tmp_path / "orchestration/research-priority.yaml").write_text(
        "ecc_areas: [ECDLP]\n")
    _write_exp(tmp_path, "EXP-ECDLP-aa1111", designed_at="2026-09-01",
               goal_id="GOAL-ECDLP-aa1111")
    _write_exp(tmp_path, "EXP-ECDLP-bb2222", designed_at="2026-09-10",
               goal_id="GOAL-ECDLP-bb2222")
    _write_exp(tmp_path, "EXP-ECDLP-cc3333", designed_at="2026-09-11")

    rows = mod.newest_runnable(tmp_path, goal="GOAL-ECDLP-aa1111")
    assert [row["id"] for row in rows] == ["EXP-ECDLP-aa1111"]
    assert rows[0]["goal_id"] == "GOAL-ECDLP-aa1111"
    assert mod.newest_runnable(tmp_path, goal="GOAL-ECDLP-dd4444") == []


def test_goal_filter_includes_pointer_bound_experiments(tmp_path):
    (tmp_path / "orchestration").mkdir()
    (tmp_path / "orchestration/research-priority.yaml").write_text(
        "ecc_areas: [ECDLP]\n")
    _write_exp(tmp_path, "EXP-ECDLP-cc0001", designed_at="2026-09-01")
    _write_exp(tmp_path, "EXP-ECDLP-cc0002", designed_at="2026-09-02")
    _write_exp(tmp_path, "EXP-ECDLP-cc0003", designed_at="2026-09-03")
    _write_exp(tmp_path, "EXP-ECDLP-cc0004", designed_at="2026-09-04")
    _write_exp(tmp_path, "EXP-ECDLP-dd0001", designed_at="2026-09-05",
               goal_id="GOAL-ECDLP-bb2222")
    _write_exp(tmp_path, "EXP-ECDLP-aa1111", designed_at="2026-09-06",
               goal_id="GOAL-ECDLP-aa1111")

    goal_dir = tmp_path / "ledger" / "goals" / "GOAL-ECDLP-aa1111"
    (goal_dir / "checkpoints").mkdir(parents=True)
    (goal_dir / "goal.yaml").write_text(yaml.safe_dump({
        "research_goal": {
            "id": "GOAL-ECDLP-aa1111",
            "status": "active",
            "active_experiment_ids": ["EXP-ECDLP-cc0003"],
            "dispatch_queue_path": (
                "coordination/goals/GOAL-ECDLP-aa1111/batches/BATCH-1/"
                "dispatch_queue.json"),
        }
    }))
    (goal_dir / "checkpoints" / "BATCH-1.yaml").write_text(yaml.safe_dump({
        "batch_checkpoint": {
            "goal_id": "GOAL-ECDLP-aa1111",
            "experiment_ids": ["EXP-ECDLP-cc0001", "EXP-ECDLP-dd0001"],
        }
    }))
    queue_dir = (tmp_path / "coordination" / "goals" / "GOAL-ECDLP-aa1111"
                 / "batches" / "BATCH-1")
    queue_dir.mkdir(parents=True)
    (queue_dir / "dispatch_queue.json").write_text(json.dumps({
        "goal_id": "GOAL-ECDLP-aa1111",
        "experiment_id": "EXP-ECDLP-cc0002",
    }))

    rows = mod.newest_runnable(tmp_path, goal="GOAL-ECDLP-aa1111")
    assert [row["id"] for row in rows] == [
        "EXP-ECDLP-aa1111", "EXP-ECDLP-cc0003", "EXP-ECDLP-cc0002",
        "EXP-ECDLP-cc0001"]
    assert mod.newest_runnable(tmp_path, goal="GOAL-ECDLP-dd4444") == []


def test_cli_keeps_goal_scope_for_all_selected_rows_and_blockers(tmp_path, monkeypatch, capsys):
    (tmp_path / "orchestration").mkdir()
    (tmp_path / "orchestration/research-priority.yaml").write_text(
        "ecc_areas: [ECDLP]\n")
    for index in range(4):
        _write_exp(tmp_path, f"EXP-ECDLP-aa000{index}", designed_at="2026-09-01",
                   goal_id="GOAL-ECDLP-aa1111")
    _write_exp(tmp_path, "EXP-ECDLP-aa0004", designed_at="2026-09-02",
               goal_id="GOAL-ECDLP-aa1111", has_runs=True)
    _write_exp(tmp_path, "EXP-ECDLP-bb0000", designed_at="2026-09-10",
               goal_id="GOAL-ECDLP-bb2222", has_runs=True)

    # Use real fixture discovery behind the CLI, changing only its checkout.
    select = mod.newest_runnable
    monkeypatch.setattr(mod, "newest_runnable", lambda **kwargs: select(tmp_path, **kwargs))
    assert mod.main(["--goal", "GOAL-ECDLP-aa1111", "--limit", "0", "--json"]) == 0
    rows = json.loads(capsys.readouterr().out)
    assert len(rows) == 4
    assert {row["goal_id"] for row in rows} == {"GOAL-ECDLP-aa1111"}

    assert mod.main(["--goal", "GOAL-ECDLP-aa1111", "--limit", "0",
                     "--include-blocked", "--json"]) == 0
    rows = json.loads(capsys.readouterr().out)
    assert len(rows) == 5
    assert {row["goal_id"] for row in rows} == {"GOAL-ECDLP-aa1111"}
    assert {row["id"] for row in rows if row["execution_state"] == "needs_reconciliation"} == {
        "EXP-ECDLP-aa0004"}

    assert mod.main(["--goal", "GOAL-ECDLP-ff0000", "--limit", "0", "--json"]) == 0
    assert json.loads(capsys.readouterr().out) == []
