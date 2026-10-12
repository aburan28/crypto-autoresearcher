"""Selected-goal health checks do not render every portfolio queue."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from types import SimpleNamespace

from tools import goal_portfolio_health as health


def test_goal_filter_skips_unselected_dispatches(tmp_path, monkeypatch, capsys):
    goals = [
        {"id": "GOAL-A-000001", "status": "active", "dispatch_queue_path": "a.json"},
        {"id": "GOAL-B-000001", "status": "active", "dispatch_queue_path": "b.json"},
    ]
    classified = []

    def classify(_repo: Path, goal: dict, _out: Path) -> dict:
        classified.append(goal["id"])
        return {"id": goal["id"], "bucket": "ready"}

    monkeypatch.setattr(health, "discover_active_goals", lambda _: goals)
    monkeypatch.setattr(health, "classify", classify)
    monkeypatch.setattr(health, "is_shallow_clone", lambda _: False)
    monkeypatch.setitem(sys.modules, "sparse_checkout",
                        SimpleNamespace(refuse_if_sparse=lambda *_: False))
    monkeypatch.setattr(sys, "argv", ["goal_portfolio_health.py", "--repo-root",
                                      str(tmp_path), "--goal", "GOAL-B-000001", "--json"])

    assert health.main() == 0
    assert classified == ["GOAL-B-000001"]
    assert [row["id"] for row in json.loads(capsys.readouterr().out)["goals"]] == [
        "GOAL-B-000001"]

