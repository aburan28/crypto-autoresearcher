#!/usr/bin/env python3
"""Tests for the artifact-driven subagent dispatch planner."""

from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import research_dispatch as dispatch


def task(
    identifier: str,
    priority: int,
    *,
    state: str = "queued",
    role: str = "executor",
    review_required: bool = False,
    depends_on: list[str] | None = None,
    write_scope: list[str] | None = None,
) -> dict:
    return {
        "id": identifier,
        "title": identifier,
        "role": role,
        "state": state,
        "priority": priority,
        "review_required": review_required,
        "depends_on": depends_on or [],
        "read_scope": ["experiments/EXP-TEST-001/specification.yaml"],
        "write_scope": write_scope or [f"coordination/tasks/{identifier}/"],
        "handoff": {
            "objective": "Reduce one bounded uncertainty.",
            "uncertainty_reduced": "Whether the frozen task completed correctly.",
            "inputs": ["experiments/EXP-TEST-001/specification.yaml"],
            "constraints": ["Preserve raw evidence."],
            "deliverables": ["report.json"],
            "budget": {
                "wall_clock_seconds": 60,
                "memory_gb": 1,
                "maximum_runs": 1,
            },
            "completion_gate": ["A machine-checkable report exists."],
        },
    }


def queue(*tasks: dict, maximum: int = 2) -> dict:
    return {
        "schema": dispatch.SCHEMA,
        "objective": "Reduce a bounded ECDLP research uncertainty.",
        "max_concurrent": maximum,
        "tasks": list(tasks),
    }


class DispatchPlannerTests(unittest.TestCase):
    def test_selects_highest_priority_ready_tasks_under_cap(self) -> None:
        plan = dispatch.select(queue(task("LOW", 10), task("HIGH", 90), task("MID", 50)))
        self.assertEqual([item["id"] for item in plan["dispatches"]], ["HIGH", "MID"])
        self.assertEqual(plan["deferred"], [{"id": "LOW", "reason": ["concurrency_cap"]}])
        self.assertTrue(plan["gates"]["concurrency_cap_respected"])

    def test_completed_dependency_unblocks_successor(self) -> None:
        parent = task("PARENT", 1, state="completed")
        child = task("CHILD", 90, depends_on=["PARENT"], role="validator")
        plan = dispatch.select(queue(parent, child, maximum=1))
        self.assertEqual([item["id"] for item in plan["dispatches"]], ["CHILD"])

    def test_failed_dependency_blocks_successor(self) -> None:
        parent = task("PARENT", 1, state="failed")
        child = task("CHILD", 90, depends_on=["PARENT"], role="validator")
        plan = dispatch.select(queue(parent, child, maximum=1))
        self.assertEqual(plan["dispatches"], [])
        self.assertEqual(
            plan["deferred"],
            [{"id": "CHILD", "reason": ["dependency_not_completed:PARENT:failed"]}],
        )

    def test_running_task_consumes_a_slot(self) -> None:
        running = task("RUNNING", 1, state="running")
        ready = task("READY", 90)
        plan = dispatch.select(queue(running, ready, maximum=1))
        self.assertEqual([item["id"] for item in plan["dispatches"]], ["RUNNING"])
        self.assertEqual(plan["deferred"], [{"id": "READY", "reason": ["concurrency_cap"]}])

    def test_overlapping_write_scope_defers_lower_priority_task(self) -> None:
        first = task("FIRST", 90, write_scope=["experiments/EXP-TEST-001/runs/"])
        second = task("SECOND", 80, write_scope=["experiments/EXP-TEST-001/runs/RUN-2/"])
        plan = dispatch.select(queue(first, second, maximum=2))
        self.assertEqual([item["id"] for item in plan["dispatches"]], ["FIRST"])
        self.assertEqual(plan["deferred"], [{"id": "SECOND", "reason": ["write_scope_conflict:FIRST"]}])

    def test_rejects_unsafe_write_scope(self) -> None:
        source = queue(task("BAD", 1, write_scope=["../outside/"]))
        with self.assertRaisesRegex(dispatch.DispatchError, "safe repository-relative"):
            dispatch.validate_queue(source)

    def test_rejects_running_write_scope_conflict(self) -> None:
        first = task("FIRST", 1, state="running", write_scope=["coordination/live/"])
        second = task("SECOND", 1, state="running", write_scope=["coordination/live/report/"])
        with self.assertRaisesRegex(dispatch.DispatchError, "overlapping write scopes"):
            dispatch.validate_queue(queue(first, second))

    def test_claim_relevant_task_requires_independent_reviewer(self) -> None:
        source = queue(task("EXEC", 1, review_required=True))
        with self.assertRaisesRegex(dispatch.DispatchError, "requires an independent"):
            dispatch.validate_queue(source)

    def test_claim_relevant_task_accepts_independent_reviewer(self) -> None:
        executor = task("EXEC", 1, review_required=True)
        validator = task("VAL", 1, role="validator", depends_on=["EXEC"])
        dispatch.validate_queue(queue(executor, validator))

    def test_plan_is_stable_for_identical_input(self) -> None:
        source = queue(task("ONE", 10), task("TWO", 20))
        first = dispatch.select(copy.deepcopy(source))
        second = dispatch.select(copy.deepcopy(source))
        self.assertEqual(first["plan_sha256"], second["plan_sha256"])


if __name__ == "__main__":
    unittest.main()
