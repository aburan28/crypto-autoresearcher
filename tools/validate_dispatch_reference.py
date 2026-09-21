#!/usr/bin/env python3
"""CI validation for a runnable queue or a source-bound forwarding record.

Forwarding records have no runnable tasks or independent claim namespace. The
dispatcher CLI and this CI entry point verify their custody/routing bindings
before resolving the sole canonical queue. Unknown schemas are refused.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

import yaml
import validate_ledger as ledger

QUEUE_SCHEMA = "crypto.autoresearch.dispatch_queue.v1"
FORWARD_SCHEMA = "crypto.autoresearch.dispatch_queue_forward.v1"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def inside(root: Path, relative: str) -> Path:
    require(isinstance(relative, str) and bool(relative), "missing relative path")
    path = Path(relative)
    require(not path.is_absolute() and ".." not in path.parts, "unsafe relative path")
    resolved = (root / path).resolve()
    require(resolved.is_relative_to(root), "path escapes repository")
    return resolved


def canonical_queue(queue: Path, root: Path) -> Path:
    root = root.resolve()
    queue = queue.resolve()
    require(queue.is_relative_to(root), "queue escapes repository")
    document = json.loads(queue.read_text())
    require(isinstance(document, dict), "queue reference must be an object")
    if document.get("schema") == QUEUE_SCHEMA:
        return queue
    require(document.get("schema") == FORWARD_SCHEMA, "unknown queue reference schema")
    require("tasks" not in document, "forwarding record must not contain runnable tasks")
    goal, batch = document.get("goal_id"), document.get("batch_id")
    require(isinstance(goal, str) and ledger.ID_PATTERNS["goal"].fullmatch(goal) is not None,
            "invalid forwarding goal")
    require(isinstance(batch, str) and ledger.ID_PATTERNS["batch"].fullmatch(batch) is not None,
            "invalid forwarding batch")
    expected = f"coordination/goals/{goal}/batches/{batch}/dispatch_queue.json"
    require(document.get("canonical_queue_path") == expected, "noncanonical forwarding target")
    target = inside(root, expected)
    current = json.loads(target.read_text())
    require(isinstance(current, dict) and current.get("schema") == QUEUE_SCHEMA,
            "forward target must be a runnable queue, never another forwarding record")
    require(current.get("goal_id") == goal and current.get("batch_id") == batch,
            "forward target goal/batch mismatch")
    source_commit = document.get("source_commit", "")
    digest = document.get("source_queue_sha256", "")
    decision_id = document.get("routing_decision", "")
    require(isinstance(source_commit, str) and re.fullmatch(r"[0-9a-f]{40}", source_commit) is not None,
            "source commit must be a full Git SHA")
    require(isinstance(digest, str) and re.fullmatch(r"[0-9a-f]{64}", digest) is not None,
            "source queue SHA256 is malformed")
    require(isinstance(decision_id, str) and re.fullmatch(r"DEC-\d{8}-(?:\d{3}|[0-9a-f]{6})", decision_id) is not None,
            "routing decision ID is malformed")
    source_path = queue.relative_to(root).as_posix()
    result = subprocess.run(["git", "-C", str(root), "show", f"{source_commit}:{source_path}"],
                            capture_output=True, check=True)
    require(hashlib.sha256(result.stdout).hexdigest() == digest, "source queue hash mismatch")
    original = json.loads(result.stdout)
    require(isinstance(original, dict) and original.get("schema") == QUEUE_SCHEMA,
            "source was not a runnable queue")
    require(original.get("batch_id") == batch, "source batch mismatch")
    require(document.get("historical_task_cards") == original.get("tasks"),
            "historical task cards differ from source")
    metadata = document.get("historical_queue_metadata")
    require(isinstance(metadata, dict), "historical queue metadata missing")
    require(metadata == {key: value for key, value in original.items() if key != "tasks"},
            "historical queue metadata differs from source")
    old_tasks, current_tasks = original.get("tasks"), current.get("tasks")
    require(isinstance(old_tasks, list) and isinstance(current_tasks, list)
            and all(isinstance(task, dict) and isinstance(task.get("id"), str)
                    for task in old_tasks + current_tasks), "task identities missing")
    require({task["id"] for task in old_tasks} <= {task["id"] for task in current_tasks},
            "canonical queue dropped historical task identities")
    amendment = current.get("routing_amendment", {})
    require(isinstance(amendment, dict), "canonical routing amendment missing")
    for key, value in {"decision_id": decision_id, "source_queue_path": source_path,
                       "source_queue_commit": source_commit, "source_queue_sha256": digest,
                       "sole_runnable_route": expected}.items():
        require(amendment.get(key) == value, f"canonical routing amendment mismatch: {key}")
    decision = yaml.safe_load(inside(root, f"ledger/decisions/{decision_id}.yaml").read_text())
    require(isinstance(decision, dict), "routing decision must be an object")
    body = decision.get("coordinator_decision", {})
    require(isinstance(body, dict) and body.get("id") == decision_id
            and body.get("decided_by") == "coordinator", "routing decision identity/authority mismatch")
    require(body.get("source_commit") == source_commit and body.get("source_queue_sha256") == digest,
            "routing decision source binding mismatch")
    references = body.get("basis_refs")
    require(isinstance(references, list) and all(isinstance(item, str) for item in references)
            and source_path in references and expected in references,
            "routing decision does not name both routes")
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("queue", type=Path)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    try:
        target = canonical_queue(args.queue, args.repo_root)
    except (OSError, ValueError, subprocess.CalledProcessError, yaml.YAMLError) as error:
        print(f"queue reference error: {error}", file=sys.stderr)
        return 2
    return subprocess.run([sys.executable, str(Path(__file__).with_name("research_dispatch.py")),
                           str(target), "--repo-root", str(args.repo_root),
                           "--output", str(args.output), "--report", str(args.report)]).returncode


if __name__ == "__main__":
    raise SystemExit(main())
