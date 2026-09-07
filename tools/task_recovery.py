#!/usr/bin/env python3
"""Read-only orphan-task assessment and opt-in isolated-successor admission.

Never releases a claim, infers process termination, writes a queue, or launches
a worker. The dispatcher calls verify() for every recovery-bearing task.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path

import yaml

try:
    from . import goal_lanes as lanes, research_dispatch as dispatch
except ImportError:
    import goal_lanes as lanes
    import research_dispatch as dispatch


class UniqueLoader(yaml.SafeLoader):
    """Approval/source ambiguity must not be resolved by last-key-wins."""


def _unique_mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in result:
            raise ValueError(f"duplicate mapping key: {key}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _unique_mapping)


def _parse(raw):
    try:
        value = yaml.load(raw, Loader=UniqueLoader)
        if not isinstance(value, dict):
            raise ValueError("document must be an object")
        return value
    except (yaml.YAMLError, ValueError, TypeError) as error:
        raise dispatch.DispatchError(f"invalid recovery document: {error}") from error


def contract_sha256(task: dict) -> str:
    """Bind approval to the task contract, excluding runtime/receipt state."""
    contract = {k: v for k, v in task.items() if k not in
                {"recovery", "state", "lease", "receipt"}}
    for field in ("read_scope", "write_scope"):
        contract[field] = [dispatch.validate_scope(s, field) for s in task[field]]
    return dispatch.digest(contract)


def assess(queue: dict, task_id: str, claim: dict | None, *, now: datetime) -> dict:
    """One bounded observation, not an authorization or a process probe."""
    matches = [t for t in queue.get("tasks", []) if t.get("id") == task_id]
    if len(matches) != 1:
        raise dispatch.DispatchError("recovery requires exactly one predecessor task")
    task = matches[0]
    try:
        dispatch.validate_queue(copy.deepcopy(queue))
        diagnostic = None
    except dispatch.DispatchError as error:
        diagnostic = str(error)
    status = (claim or {}).get("status", "missing")
    completed = task.get("state") == "completed" or (
        status == "released" and (claim.get("release") or {}).get("outcome") == "completed")
    if completed:
        action = "verify_existing_outputs"
    elif status == "live":
        action = "preserve_live_lease"
    elif status == "expired":
        action = "request_isolated_successor_decision"
    else:
        action = "request_coordinator_disposition"
    return {
        "schema": "crypto.autoresearch.recovery_assessment.v1",
        "task_id": task_id, "observed_at": now.isoformat(),
        "lease_status": status, "runtime_status": "unknown",
        "runtime_handle_hint": (claim or {}).get("session"),
        "queue_diagnostic": diagnostic, "next_action": action,
        "dispatch_authorized": False, "release_required": False,
        "inspection_limit": {"maximum_passes": 1, "wall_clock_seconds": 600},
        "repeat_only_when": "new claim, output, runtime evidence, or Coordinator decision",
    }


def _pinned_document(verifier, binding: dict):
    if not isinstance(binding, dict):
        raise dispatch.DispatchError("recovery binding must be an object")
    path = dispatch.validate_artifact_path(binding.get("path"), "recovery binding path")
    commit = binding.get("commit", "")
    sha = binding.get("sha256", "")
    if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise dispatch.DispatchError("recovery binding requires a full commit SHA")
    if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{64}", sha):
        raise dispatch.DispatchError("recovery binding requires SHA-256")
    verifier._run(["merge-base", "--is-ancestor", commit, "HEAD"])
    mode = verifier._run(["ls-tree", commit, "--", path]).decode().split()[0:1]
    if mode not in (["100644"], ["100755"]):
        raise dispatch.DispatchError("recovery binding must be a regular Git blob")
    raw = verifier._run(["show", f"{commit}:{path}"])
    if hashlib.sha256(raw).hexdigest() != sha:
        raise dispatch.DispatchError("recovery binding hash mismatch")
    live = verifier.repo_root / path
    if not live.resolve().is_relative_to(verifier.repo_root) or live.is_symlink() or not live.is_file() or live.read_bytes() != raw:
        raise dispatch.DispatchError("recovery binding differs from current worktree")
    return _parse(raw)


def verify(queue: dict, task: dict, verifier, *, now: datetime | None) -> None:
    """Fail closed on missing authority/isolation; keep old history untouched."""
    r = task["recovery"]
    if not isinstance(r, dict) or r.get("mode") != "isolated_successor_v1":
        raise dispatch.DispatchError("recovery.mode must be isolated_successor_v1")
    if now is None or now.tzinfo is None:
        raise dispatch.DispatchError("recovery requires an explicit timezone-aware clock")
    if verifier is None or not isinstance(getattr(verifier, "repo_root", None), Path) or not callable(getattr(verifier, "_run", None)):
        raise dispatch.DispatchError("recovery requires GitRepositoryVerifier")
    predecessor = _pinned_document(verifier, r.get("predecessor_queue"))
    old_id = r.get("predecessor_task_id")
    predecessor_tasks = predecessor.get("tasks")
    if not isinstance(predecessor_tasks, list) or not all(isinstance(t, dict) for t in predecessor_tasks):
        raise dispatch.DispatchError("predecessor queue requires a task list")
    old_tasks = [t for t in predecessor_tasks if t.get("id") == old_id]
    if len(old_tasks) != 1 or old_id == task["id"]:
        raise dispatch.DispatchError("recovery requires a distinct, unique predecessor task")
    old = old_tasks[0]
    if old_id in {t["id"] for t in queue["tasks"]}:
        raise dispatch.DispatchError("predecessor must not be rerun in the successor queue")
    dispatch.require_text_list(old, "write_scope", "predecessor")
    dispatch.require_text_list(old, "artifact_paths", "predecessor")
    scopes = [dispatch.validate_scope(s, "predecessor.write_scope") for s in old["write_scope"]]
    # Check archives too: a safe producer followed by an overlapping archive
    # would still overwrite the unknown worker's namespace.
    for candidate in queue["tasks"]:
        for scope in candidate["write_scope"]:
            if any(dispatch.scope_overlaps(scope, previous) for previous in scopes):
                raise dispatch.DispatchError("recovery queue overlaps predecessor write_scope")
            resolved = (verifier.repo_root / scope).resolve()
            if not resolved.is_relative_to(verifier.repo_root):
                raise dispatch.DispatchError("recovery scope escapes worktree through a symlink")
            if any(dispatch.scope_overlaps(resolved.relative_to(verifier.repo_root).as_posix(), s) for s in scopes):
                raise dispatch.DispatchError("recovery scope aliases predecessor write_scope")
    session = r.get("session")
    if not isinstance(session, str) or not session.strip():
        raise dispatch.DispatchError("recovery requires a recorded successor session")
    original_root = r.get("predecessor_worktree")
    successor_root = r.get("successor_worktree")
    if not all(isinstance(p, str) and Path(p).is_absolute() for p in (original_root, successor_root)):
        raise dispatch.DispatchError("recovery worktrees must be absolute paths")
    original_root, successor_root = Path(original_root).resolve(), Path(successor_root).resolve()
    if original_root == successor_root or (
        task.get("state") in {"queued", "running"} and successor_root != verifier.repo_root
    ):
        raise dispatch.DispatchError("recovery requires a distinct actual successor worktree")
    # Nested worktrees remain acceptable only because output namespaces are
    # disjoint and path escape is rejected; this is not process sandboxing.
    for field in ("wall_clock_seconds", "memory_gb"):
        value = task["handoff"]["budget"].get(field)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
            raise dispatch.DispatchError(f"recovery requires finite positive {field}")
    decision = _pinned_document(verifier, r.get("decision"))
    decision = decision.get("coordinator_decision", {})
    if not isinstance(decision, dict):
        raise dispatch.DispatchError("recovery decision must contain a Coordinator object")
    decision_id = decision.get("id")
    if not isinstance(decision_id, str) or not re.fullmatch(r"DEC-\d{8}-(?:[0-9a-f]{6}|\d{3})", decision_id):
        raise dispatch.DispatchError("recovery decision requires a valid DEC identifier")
    if r["decision"]["path"] != f"ledger/decisions/{decision_id}.yaml":
        raise dispatch.DispatchError("recovery approval must be a matching ledger decision")
    dispatch.require_text_list(decision, "target_ids", "recovery decision")
    if not {old_id, task["id"]}.issubset(set(decision["target_ids"])):
        raise dispatch.DispatchError("recovery decision must target both attempts")
    approval = decision.get("recovery_authorization", {})
    if not isinstance(approval, dict):
        raise dispatch.DispatchError("recovery_authorization must be an object")
    expected = {
        "predecessor_task_id": old_id,
        "successor_task_id": task["id"],
        "predecessor_queue_sha256": r["predecessor_queue"]["sha256"],
        "successor_contract_sha256": contract_sha256(task),
        "allow_unknown_runtime": True,
        "predecessor_worktree": str(original_root),
        "successor_worktree": str(successor_root),
        "session": session,
        "predecessor_epoch": r.get("predecessor_epoch"),
        "predecessor_owner": r.get("predecessor_owner"),
    }
    if decision.get("decided_by") != "coordinator" or decision.get("decision") not in {"approve", "revise"}:
        raise dispatch.DispatchError("recovery requires a Coordinator approval decision")
    if any(approval.get(k) != v for k, v in expected.items()):
        raise dispatch.DispatchError("recovery approval does not bind this exact successor")
    if r.get("supersedes_decision_ids", []) != approval.get("supersedes_decision_ids", []):
        raise dispatch.DispatchError("recovery decision supersession mismatch")
    if task.get("state") not in {"queued", "running"}:
        return  # Historical verification must not depend on a later lease clock.
    if task.get("state") == "queued" and any(
        (verifier.repo_root / p).exists() or (verifier.repo_root / p).is_symlink()
        for p in task["artifact_paths"]
    ):
        raise dispatch.DispatchError("successor output exists; reconcile before relaunch")
    path = verifier.repo_root / r["predecessor_queue"]["path"]
    claim = lanes.claim_summary(verifier.repo_root, path, include_refs=True, now=now).get(old_id)
    if not claim or claim.get("status") != "expired" or old.get("state") == "completed":
        raise dispatch.DispatchError("recovery requires a currently expired, noncompleted predecessor")
    for name, expected_value in (("epoch", r.get("predecessor_epoch")), ("owner", r.get("predecessor_owner"))):
        if claim.get(name) != expected_value:
            raise dispatch.DispatchError("predecessor claim changed; reassess recovery")
    # The old claim's path is not runtime proof, but it binds the place to check
    # for late files. A caller cannot substitute an empty directory unnoticed.
    history = lanes.load_claims(verifier.repo_root, path, include_refs=True).get(old_id, [])
    raw_claim = next((h.get("claim") for h in history if h["epoch"] == claim["epoch"]), None)
    recorded_root = (raw_claim or {}).get("worktree")
    if not isinstance(recorded_root, str) or Path(recorded_root).resolve() != original_root:
        raise dispatch.DispatchError("predecessor worktree does not match its claim")
    if not original_root.is_dir():
        raise dispatch.DispatchError("predecessor worktree unavailable; explicit disposition required")
    # Never silently replace an attempt whose output arrived after assessment.
    for artifact in old.get("artifact_paths", []):
        artifact = dispatch.validate_artifact_path(artifact, "predecessor artifact")
        if any((base / artifact).exists() or (base / artifact).is_symlink()
               for base in (original_root, verifier.repo_root)):
            raise dispatch.DispatchError("predecessor output exists; reconcile before recovery")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("queue", type=Path)
    parser.add_argument("task_id")
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    args = parser.parse_args()
    try:
        now = datetime.now(timezone.utc)
        root = args.repo.resolve()
        path = args.queue.resolve()
        claims = lanes.claim_summary(root, path, include_refs=True, now=now)
        print(json.dumps(assess(_parse(path.read_text()), args.task_id,
                               claims.get(args.task_id), now=now), indent=2))
    except (OSError, ValueError, lanes.LaneError) as error:
        parser.exit(2, f"recovery assessment error: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
