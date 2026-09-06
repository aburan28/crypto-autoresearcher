#!/usr/bin/env python3
"""Read-only queue observations from the existing verified research dispatcher."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import tempfile

SCHEMA = "crypto.autoresearch.harness_checkpoint.v1"


def observe(plan: dict, *, repo: Path, queue: Path, mode: str,
            observed_at: str, previous: dict | None = None,
            leases: dict | None = None) -> dict:
    if plan.get("schema") != "crypto.autoresearch.dispatch_plan.v1":
        raise ValueError("unsupported dispatcher plan schema")
    gates = plan.get("gates")
    if not isinstance(gates, dict) or not gates or any(v is not True for v in gates.values()):
        raise ValueError("dispatcher gates are missing or failed")
    identity = {"repo": str(repo), "queue": str(queue), "mode": mode,
                "goal_id": plan.get("goal_id")}
    ready, running = [], []
    for task in plan["dispatches"]:
        item = {key: task[key] for key in ("id", "role", "state")}
        item["claim"] = task.get("claim")
        item["lease"] = (leases or {}).get(task["id"])
        if task["state"] == "running" or task.get("claim") is not None:
            running.append(item)
        else:
            ready.append(item)
    # Receipts are supplied separately by main after the dispatcher verified the
    # same queue bytes. A projection alone never fabricates archive receipts.
    states = {item["id"]: item["state"] for item in plan["terminal"]}
    for item in plan["dispatches"]:
        states[item["id"]] = item["state"]
    projection = {
        "ready": ready, "running": running, "deferred": plan["deferred"],
        "terminal": plan["terminal"], "claims": plan.get("claims", {}),
        "expired_leases": plan.get("expired_leases", []),
    }
    delta = {"kind": "baseline", "newly_completed": [], "newly_failed": []}
    if previous is not None:
        if previous.get("schema") != SCHEMA or previous.get("identity") != identity:
            raise ValueError("previous checkpoint belongs to a different checkout, queue or mode")
        before = previous["task_states"]
        delta = {
            "kind": "unchanged" if previous["projection"] == projection else "changed",
            "newly_completed": sorted(k for k, v in states.items()
                                      if v == "completed" and before.get(k) != v),
            "newly_failed": sorted(k for k, v in states.items()
                                   if v in ("failed", "invalid") and before.get(k) != v),
        }
    return {
        "schema": SCHEMA, "identity": identity, "observed_at": observed_at,
        "source_queue_sha256": plan["source_queue_sha256"],
        "plan_sha256": plan["plan_sha256"], "task_states": states,
        "projection": projection, "delta": delta,
        "authority": "derived observation only; next_action comes from the committed goal/lane",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--queue", type=Path, required=True)
    parser.add_argument("--mode", choices=("status", "goal", "portfolio", "task", "ideas", "design"),
                        required=True)
    parser.add_argument("--previous", type=Path)
    args = parser.parse_args()
    repo = args.repo.resolve()
    queue = (repo / args.queue).resolve()
    if not queue.is_relative_to(repo):
        parser.error("queue must belong to the declared checkout")
    now = datetime.now(timezone.utc).isoformat()
    try:
        # Outputs are temporary; the dispatcher never mutates the input queue.
        original = queue.read_bytes()
        with tempfile.TemporaryDirectory(prefix="harness-checkpoint-") as directory:
            plan_path = Path(directory) / "plan.json"
            command = [
                sys.executable, str(repo / "tools/research_dispatch.py"), str(queue),
                "--repo-root", str(repo), "--claims", "refs", "--now", now,
                "--output", str(plan_path), "--report", str(Path(directory) / "plan.md"),
            ]
            result = subprocess.run(command, cwd=repo, text=True, capture_output=True, check=False)
            if result.returncode:
                raise ValueError("dispatcher refused checkpoint: " +
                                 (result.stderr or result.stdout).strip())
            if queue.read_bytes() != original:
                raise ValueError("queue changed during observation; re-render before reporting")
            plan = json.loads(plan_path.read_text())
        previous = json.loads(args.previous.read_text()) if args.previous else None
        source = json.loads(original)
        leases = {t["id"]: t["lease"] for t in source["tasks"] if "lease" in t}
        output = observe(plan, repo=repo, queue=queue, mode=args.mode,
                         observed_at=now, previous=previous, leases=leases)
        output["verified_archives"] = [
            {"id": task["id"], "commit_sha": task["archive"]["commit_sha"],
             "kind": task["archive"]["kind"]}
            for task in source["tasks"]
            if task["state"] == "completed" and "archive" in task
        ]
        print(json.dumps(output, indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"checkpoint error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
