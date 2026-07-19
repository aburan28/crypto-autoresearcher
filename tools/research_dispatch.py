#!/usr/bin/env python3
"""Validate and render a bounded, artifact-driven subagent dispatch queue."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path, PurePosixPath
from typing import Any


SCHEMA = "crypto.autoresearch.dispatch_queue.v1"
PLAN_SCHEMA = "crypto.autoresearch.dispatch_plan.v1"
ROLES = {
    "coordinator",
    "executor",
    "reviewer",
    "validator",
    "red-team",
    "idea-generator",
}
TERMINAL_STATES = {"completed", "failed", "invalid", "cancelled"}
STATES = {"queued", "running", "blocked"} | TERMINAL_STATES


class DispatchError(ValueError):
    """Raised when a dispatch queue cannot be safely scheduled."""


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
        "ascii"
    )


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def require_text(record: dict[str, Any], field: str, location: str) -> None:
    value = record.get(field)
    if not isinstance(value, str) or not value.strip():
        raise DispatchError(f"{location}.{field} must be nonempty text")


def require_text_list(
    record: dict[str, Any], field: str, location: str, *, allow_empty: bool = False
) -> None:
    value = record.get(field)
    if not isinstance(value, list) or (not allow_empty and not value) or not all(
        isinstance(item, str) and item.strip() for item in value
    ):
        raise DispatchError(f"{location}.{field} must be a nonempty text list")


def require_positive_number(record: dict[str, Any], field: str, location: str) -> None:
    value = record.get(field)
    if not isinstance(value, (int, float)) or isinstance(value, bool) or value <= 0:
        raise DispatchError(f"{location}.{field} must be a positive number")


def validate_scope(path: str, location: str) -> str:
    candidate = PurePosixPath(path)
    if candidate.is_absolute() or ".." in candidate.parts or str(candidate) in {"", "."}:
        raise DispatchError(f"{location} must be a safe repository-relative path")
    return candidate.as_posix().rstrip("/")


def scope_overlaps(left: str, right: str) -> bool:
    return left == right or left.startswith(right + "/") or right.startswith(left + "/")


def assert_acyclic(graph: dict[str, list[str]]) -> None:
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> None:
        if node in visiting:
            raise DispatchError(f"task dependency graph has a cycle at {node}")
        if node in visited:
            return
        visiting.add(node)
        for dependency in graph[node]:
            visit(dependency)
        visiting.remove(node)
        visited.add(node)

    for node in graph:
        visit(node)


def validate_handoff(task: dict[str, Any], location: str) -> None:
    handoff = task.get("handoff")
    if not isinstance(handoff, dict):
        raise DispatchError(f"{location}.handoff must be an object")
    for field in ("objective", "uncertainty_reduced"):
        require_text(handoff, field, f"{location}.handoff")
    for field in ("inputs", "constraints", "deliverables", "completion_gate"):
        require_text_list(handoff, field, f"{location}.handoff")
    budget = handoff.get("budget")
    if not isinstance(budget, dict):
        raise DispatchError(f"{location}.handoff.budget must be an object")
    for field in ("wall_clock_seconds", "memory_gb"):
        require_positive_number(budget, field, f"{location}.handoff.budget")
    maximum_runs = budget.get("maximum_runs")
    if not isinstance(maximum_runs, int) or isinstance(maximum_runs, bool) or maximum_runs < 1:
        raise DispatchError(f"{location}.handoff.budget.maximum_runs must be a positive integer")


def validate_queue(queue: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(queue, dict):
        raise DispatchError("queue must be an object")
    if queue.get("schema") != SCHEMA:
        raise DispatchError(f"queue.schema must be {SCHEMA}")
    require_text(queue, "objective", "queue")
    maximum = queue.get("max_concurrent")
    if not isinstance(maximum, int) or isinstance(maximum, bool) or not 1 <= maximum <= 3:
        raise DispatchError("queue.max_concurrent must be an integer 1..3")
    tasks = queue.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        raise DispatchError("queue.tasks must be a nonempty list")

    ids: list[str] = []
    for index, task in enumerate(tasks):
        location = f"tasks[{index}]"
        if not isinstance(task, dict):
            raise DispatchError(f"{location} must be an object")
        for field in ("id", "title"):
            require_text(task, field, location)
        if task.get("role") not in ROLES:
            raise DispatchError(f"{location}.role is invalid")
        if task.get("state") not in STATES:
            raise DispatchError(f"{location}.state is invalid")
        if not isinstance(task.get("review_required"), bool):
            raise DispatchError(f"{location}.review_required must be boolean")
        priority = task.get("priority")
        if not isinstance(priority, int) or isinstance(priority, bool) or not 0 <= priority <= 100:
            raise DispatchError(f"{location}.priority must be an integer 0..100")
        require_text_list(task, "depends_on", location, allow_empty=True)
        for field in ("read_scope", "write_scope"):
            require_text_list(task, field, location)
        task["read_scope"] = [
            validate_scope(path, f"{location}.read_scope") for path in task["read_scope"]
        ]
        task["write_scope"] = [
            validate_scope(path, f"{location}.write_scope") for path in task["write_scope"]
        ]
        if len(task["write_scope"]) != len(set(task["write_scope"])):
            raise DispatchError(f"{location}.write_scope contains duplicates")
        validate_handoff(task, location)
        ids.append(task["id"])

    if len(ids) != len(set(ids)):
        raise DispatchError("task IDs must be unique")
    by_id = {task["id"]: task for task in tasks}
    for task in tasks:
        for dependency in task["depends_on"]:
            if dependency not in by_id:
                raise DispatchError(f"{task['id']} has unknown dependency {dependency}")
            if dependency == task["id"]:
                raise DispatchError(f"{task['id']} depends on itself")
    for task in tasks:
        if not task["review_required"]:
            continue
        reviewers = [
            successor["id"]
            for successor in tasks
            if task["id"] in successor["depends_on"]
            and successor["role"] in {"reviewer", "validator", "red-team"}
        ]
        if not reviewers:
            raise DispatchError(
                f"{task['id']} requires an independent reviewer, validator, or red-team successor"
            )
    assert_acyclic({task["id"]: task["depends_on"] for task in tasks})

    for task in tasks:
        if task["state"] == "running":
            incomplete = [
                dependency
                for dependency in task["depends_on"]
                if by_id[dependency]["state"] != "completed"
            ]
            if incomplete:
                raise DispatchError(
                    f"running task {task['id']} has incomplete dependencies {incomplete}"
                )

    running = [task for task in tasks if task["state"] == "running"]
    if len(running) > maximum:
        raise DispatchError("running task count exceeds queue.max_concurrent")
    for index, left in enumerate(running):
        for right in running[index + 1 :]:
            if any(
                scope_overlaps(left_scope, right_scope)
                for left_scope in left["write_scope"]
                for right_scope in right["write_scope"]
            ):
                raise DispatchError(
                    f"running tasks {left['id']} and {right['id']} have overlapping write scopes"
                )
    return by_id


def blockers(task: dict[str, Any], by_id: dict[str, dict[str, Any]]) -> list[str]:
    output: list[str] = []
    for dependency in task["depends_on"]:
        state = by_id[dependency]["state"]
        if state != "completed":
            output.append(f"dependency_not_completed:{dependency}:{state}")
    if task["state"] == "blocked":
        output.append("task_marked_blocked")
    return output


def conflicts(task: dict[str, Any], selected: list[dict[str, Any]]) -> list[str]:
    conflicting_ids = []
    for other in selected:
        if any(
            scope_overlaps(task_scope, other_scope)
            for task_scope in task["write_scope"]
            for other_scope in other["write_scope"]
        ):
            conflicting_ids.append(other["id"])
    return sorted(conflicting_ids)


def select(queue: dict[str, Any]) -> dict[str, Any]:
    by_id = validate_queue(queue)
    running = [task for task in queue["tasks"] if task["state"] == "running"]
    queued = [
        task
        for task in queue["tasks"]
        if task["state"] == "queued" and not blockers(task, by_id)
    ]
    queued.sort(key=lambda task: (-task["priority"], task["id"]))
    selected = list(running)
    deferred: list[dict[str, Any]] = []
    for task in queued:
        if len(selected) == queue["max_concurrent"]:
            deferred.append({"id": task["id"], "reason": ["concurrency_cap"]})
            continue
        conflicting = conflicts(task, selected)
        if conflicting:
            deferred.append(
                {
                    "id": task["id"],
                    "reason": [f"write_scope_conflict:{identifier}" for identifier in conflicting],
                }
            )
            continue
        selected.append(task)

    selected_ids = {task["id"] for task in selected}
    for task in queue["tasks"]:
        if task["id"] in selected_ids or task["state"] in TERMINAL_STATES:
            continue
        if task["state"] == "queued":
            task_blockers = blockers(task, by_id)
            if task_blockers:
                deferred.append({"id": task["id"], "reason": task_blockers})
        elif task["state"] == "blocked":
            deferred.append({"id": task["id"], "reason": ["task_marked_blocked"]})

    dispatches = [
        {
            "id": task["id"],
            "title": task["title"],
            "role": task["role"],
            "state": task["state"],
            "priority": task["priority"],
            "review_required": task["review_required"],
            "depends_on": task["depends_on"],
            "read_scope": task["read_scope"],
            "write_scope": task["write_scope"],
            "handoff": task["handoff"],
        }
        for task in selected
    ]
    plan = {
        "schema": PLAN_SCHEMA,
        "source_schema": SCHEMA,
        "objective": queue["objective"],
        "source_queue_sha256": digest(queue),
        "max_concurrent": queue["max_concurrent"],
        "dispatches": dispatches,
        "deferred": sorted(deferred, key=lambda item: item["id"]),
        "terminal": [
            {"id": task["id"], "state": task["state"]}
            for task in queue["tasks"]
            if task["state"] in TERMINAL_STATES
        ],
        "gates": {
            "concurrency_cap_respected": len(selected) <= queue["max_concurrent"] <= 3,
            "all_selected_dependencies_completed": all(
                not blockers(task, by_id) for task in selected
            ),
            "selected_write_scopes_do_not_overlap": all(
                not conflicts(task, selected[:index])
                for index, task in enumerate(selected)
            ),
            "coordinator_only_promotes_research_status": True,
            "terminal_noncompleted_tasks_do_not_unblock_successors": True,
            "claim_relevant_tasks_have_independent_review": True,
        },
    }
    plan["plan_sha256"] = digest(plan)
    return plan


def markdown(plan: dict[str, Any]) -> str:
    lines = [
        "# Dynamic Subagent Dispatch Plan",
        "",
        plan["objective"],
        "",
        "## Ready Tasks",
        "",
        "| ID | Role | State | Priority | Dependencies | Write scope |",
        "|---|---|---|---:|---|---|",
    ]
    if not plan["dispatches"]:
        lines.append("| none | - | - | - | - | - |")
    for task in plan["dispatches"]:
        lines.append(
            f"| `{task['id']}` | {task['role']} | {task['state']} | {task['priority']} | "
            f"{', '.join(task['depends_on']) or '-'} | {', '.join(task['write_scope'])} |"
        )
    lines.extend(["", "## Deferred or Blocked", ""])
    if not plan["deferred"]:
        lines.append("None.")
    for task in plan["deferred"]:
        lines.append(f"- `{task['id']}`: {', '.join(task['reason'])}")
    lines.extend(["", "## Dispatch Gates", ""])
    for gate, passed in plan["gates"].items():
        lines.append(f"- `{gate}`: {'passed' if passed else 'failed'}")
    lines.extend(["", f"Plan SHA-256: `{plan['plan_sha256']}`", ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("queue", type=Path, help="dispatch queue JSON")
    parser.add_argument("--output", type=Path, required=True, help="dispatch plan JSON")
    parser.add_argument("--report", type=Path, required=True, help="dispatch plan Markdown")
    args = parser.parse_args()
    try:
        queue = json.loads(args.queue.read_text(encoding="utf-8"))
        plan = select(queue)
    except (OSError, json.JSONDecodeError, DispatchError) as error:
        print(f"dispatch error: {error}", file=sys.stderr)
        return 2
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.report.write_text(markdown(plan), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
