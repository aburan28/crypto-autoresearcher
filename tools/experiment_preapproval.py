#!/usr/bin/env python3
"""Read-only check of a proposed, still-unapproved experiment packet.

The packet points to preview copies of the *exact* final specification, trial
plan, dispatch queue and executor handoff. The canonical experiment remains
review_required. This tool only reports whether those bytes could be archived
and considered for approval; it grants no execution permission. Runtime
admission remains in newest_experiments.py and experiment_execution.authorize.

Packet schema ``crypto.autoresearch.preapproval_packet.v1``::

  {"experiment_id": "EXP-...", "approval_decision_id": "DEC-...",
   "specification": "experiments/EXP-.../specification.yaml",
   "trial_plan": "experiments/EXP-.../trial-plan.json",
   "queue": "coordination/goals/GOAL-.../batches/BATCH-.../queue.json",
   "handoff": "ledger/handoffs/TASK-....yaml",
   "preview": {"specification": "/path/to/spec.yaml", "trial_plan": "...",
               "queue": "...", "handoff": "..."},
   "source_ref": "origin/main", "lane_id": "BATCH-...",
   "execution_route": {"kind": "implementation", "reason": "..."}}

The preview paths may be temporary files. Their SHA-256 values appear in the
report and must match the later canonical archive exactly. Source and input
paths must already have the same bytes in ``source_ref``; external binaries
are checked by local digest. No shell, solver, trial, claim or write occurs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from experiment_execution import GENERATED, RUN_ID, safe_path  # noqa: E402
from goal_lanes import load_lanes  # noqa: E402
from research_dispatch import DispatchError, GitRepositoryVerifier, paths_within_scopes, validate_queue  # noqa: E402

SCHEMA = "crypto.autoresearch.preapproval_packet.v1"
PLAN_SCHEMA = "crypto.autoresearch.trial_plan.v1"
DEC_ID = re.compile(r"DEC-\d{8}-[0-9a-f]{6}\Z")
SHA = re.compile(r"[0-9a-f]{64}\Z")


def _hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _read(path: str, label: str, blockers: list[str]) -> bytes | None:
    try:
        return Path(path).read_bytes()
    except (OSError, TypeError, ValueError) as error:
        blockers.append(f"{label}: unreadable preview: {error}")
        return None


def _mapping(data: bytes | None, label: str, blockers: list[str], *, kind: str) -> dict[str, Any]:
    if data is None:
        return {}
    try:
        obj = json.loads(data) if kind == "json" else yaml.safe_load(data)
    except (ValueError, yaml.YAMLError) as error:
        blockers.append(f"{label}: invalid {kind}: {error}")
        return {}
    if not isinstance(obj, dict):
        blockers.append(f"{label}: expected mapping")
        return {}
    return obj


def _git_blob(root: Path, ref: str, relative: str) -> bytes | None:
    try:
        return subprocess.check_output(
            ["git", "show", f"{ref}:{relative}"], cwd=root, stderr=subprocess.DEVNULL)
    except (OSError, subprocess.CalledProcessError):
        return None


def _bound_file(root: Path, path: str, digest: Any, ref: str, blockers: list[str], label: str) -> None:
    if not isinstance(digest, str) or not SHA.fullmatch(digest):
        blockers.append(f"{label}: invalid or missing SHA-256 for {path}")
        return
    try:
        if Path(path).is_absolute():
            actual = _hash(Path(path).read_bytes())
        else:
            actual = _hash(safe_path(root, path).read_bytes())
            remote = _git_blob(root, ref, path)
            if remote is None or _hash(remote) != digest:
                blockers.append(f"{label}: {path} is not committed with these bytes at {ref}")
    except (OSError, ValueError, TypeError) as error:
        blockers.append(f"{label}: unavailable {path}: {error}")
        return
    if actual != digest:
        blockers.append(f"{label}: SHA-256 mismatch for {path}")


def _source_bindings(spec: dict[str, Any], plan: dict[str, Any], root: Path,
                     ref: str, blockers: list[str]) -> None:
    for name in ("source_sha256", "input_sha256"):
        bindings = plan.get(name)
        if not isinstance(bindings, dict) or not bindings:
            blockers.append(f"trial plan: {name} must be a nonempty path-to-SHA-256 mapping")
            continue
        for path, digest in bindings.items():
            if not isinstance(path, str):
                blockers.append(f"trial plan: {name} contains a non-path key")
                continue
            _bound_file(root, path, digest, ref, blockers, name)
    def walk(value: Any, trail: str) -> None:
        if isinstance(value, dict):
            if "path" in value and "sha256" in value:
                path = value["path"]
                if isinstance(path, str):
                    _bound_file(root, path, value["sha256"], ref, blockers, trail)
                else:
                    blockers.append(f"{trail}: invalid path")
            else:
                for key, item in value.items():
                    walk(item, f"{trail}.{key}")
        elif isinstance(value, list):
            for index, item in enumerate(value):
                walk(item, f"{trail}[{index}]")
    bindings = spec.get("input_bindings")
    if not isinstance(bindings, dict) or not bindings:
        blockers.append("specification: input_bindings missing")
    else:
        walk(bindings, "specification.input_bindings")


def _trials(plan: dict[str, Any], root: Path, blockers: list[str]) -> set[str]:
    trials = plan.get("trials")
    if not isinstance(trials, list) or not trials:
        blockers.append("trial plan: nonempty trials required")
        return set()
    required: set[str] = set()
    ids: set[str] = set()
    runs: set[str] = set()
    source_map = plan.get("source_sha256")
    sources = set(source_map) if isinstance(source_map, dict) else set()
    exp = plan.get("experiment_id")
    for index, trial in enumerate(trials):
        label = f"trial[{index}]"
        if not isinstance(trial, dict):
            blockers.append(f"{label}: expected mapping")
            continue
        tid, rid = trial.get("id"), trial.get("run_id")
        if not isinstance(tid, str) or not tid or tid in ids:
            blockers.append(f"{label}: nonempty unique trial ID required")
        else:
            ids.add(tid)
        if not isinstance(rid, str) or not RUN_ID.fullmatch(rid) or rid in runs:
            blockers.append(f"{label}: unique random-suffix RUN ID required")
            continue
        runs.add(rid)
        deps = trial.get("depends_on", [])
        if not isinstance(deps, list) or not all(isinstance(x, str) for x in deps) or not set(deps) <= ids - {tid}:
            blockers.append(f"{label}: dependencies must name earlier trials")
        for command in ("argv", "check_argv"):
            args = trial.get(command)
            if not isinstance(args, list) or not args or not all(isinstance(x, str) and x and "\x00" not in x for x in args):
                blockers.append(f"{label}: {command} must be an argv array")
            elif any("bedrock" in arg.lower() for arg in args) or not sources.intersection(args):
                blockers.append(f"{label}: {command} must name a bound source and exclude Bedrock")
        artifacts = trial.get("artifacts")
        if (not isinstance(artifacts, list)
                or any(not isinstance(x, str) or not x or x in GENERATED for x in artifacts)
                or len(artifacts) != len(set(artifacts))
                or not {"manifest.yaml", "raw-result.json"} <= set(artifacts)):
            blockers.append(f"{label}: invalid declared trial artifacts")
            continue
        if isinstance(trial.get("memory_mb"), bool) or not isinstance(trial.get("memory_mb"), (int, float)) or trial["memory_mb"] <= 0:
            blockers.append(f"{label}: positive memory_mb required")
        if trial.get("watchdog_seconds") is not None and (not isinstance(trial["watchdog_seconds"], (int, float)) or trial["watchdog_seconds"] <= 0 or not trial.get("watchdog_reason")):
            blockers.append(f"{label}: watchdog needs a positive limit and reason")
        if not isinstance(exp, str):
            continue
        parent = f"experiments/{exp}/runs/{rid}"
        try:
            # Use the supervisor's canonical-path and symlink checks, including
            # nested certificate/log paths, before counting archive coverage.
            directory = safe_path(root, parent)
            for name in artifacts:
                safe_path(directory, name)
        except (ValueError, OSError) as error:
            blockers.append(f"{label}: invalid declared trial artifacts: {error}")
            continue
        for name in (*GENERATED, *artifacts):
            required.add(f"{parent}/{name}")
    return required


def assess(root: Path, packet: dict[str, Any]) -> dict[str, Any]:
    """Check projected approval bytes without changing the checkout."""
    blockers: list[str] = []
    report: dict[str, Any] = {"schema": SCHEMA, "approvable": False, "blockers": blockers,
                              "prospective_sha256": {}}
    if packet.get("schema") != SCHEMA:
        blockers.append(f"packet: schema must be {SCHEMA}")
    exp_id = packet.get("experiment_id")
    decision = packet.get("approval_decision_id")
    if not isinstance(exp_id, str) or not re.fullmatch(r"EXP-[A-Za-z0-9]+-[0-9a-f]{6}", exp_id):
        blockers.append("packet: valid experiment_id required")
        return report
    if not isinstance(decision, str) or not DEC_ID.fullmatch(decision):
        blockers.append("packet: reserved approval_decision_id required")
    canonical = {name: packet.get(name) for name in ("specification", "trial_plan", "queue", "handoff")}
    report["canonical_paths"] = canonical
    expected_spec = f"experiments/{exp_id}/specification.yaml"
    expected_plan = f"experiments/{exp_id}/trial-plan.json"
    if canonical["specification"] != expected_spec or canonical["trial_plan"] != expected_plan:
        blockers.append("packet: canonical specification/trial-plan paths do not match experiment")
    preview = packet.get("preview") if isinstance(packet.get("preview"), dict) else {}
    raw: dict[str, bytes | None] = {}
    for name in canonical:
        p = preview.get(name)
        raw[name] = _read(p, name, blockers) if p else None
        if raw[name] is None and not p:
            blockers.append(f"packet: prospective {name} preview missing")
        if raw[name] is not None:
            report["prospective_sha256"][name] = _hash(raw[name])
    spec_doc = _mapping(raw["specification"], "specification", blockers, kind="yaml")
    spec = spec_doc.get("experiment") if isinstance(spec_doc.get("experiment"), dict) else spec_doc
    plan = _mapping(raw["trial_plan"], "trial plan", blockers, kind="json")
    queue = _mapping(raw["queue"], "queue", blockers, kind="json")
    handoff_doc = _mapping(raw["handoff"], "handoff", blockers, kind="yaml")
    handoff = handoff_doc.get("handoff") if isinstance(handoff_doc.get("handoff"), dict) else handoff_doc
    canonical_spec = root / expected_spec
    try:
        current = yaml.safe_load(canonical_spec.read_text())
        current = current.get("experiment", current)
        if current.get("status") not in ("review_required", "specified") or current.get("approved_by"):
            blockers.append("canonical experiment is already approved or not in a preapproval state")
        ref = packet.get("source_ref")
        if isinstance(ref, str) and ref.startswith("origin/"):
            remote = _git_blob(root, ref, expected_spec)
            if remote is None or remote != canonical_spec.read_bytes():
                blockers.append("canonical draft specification is not committed with these bytes at source_ref")
    except (OSError, ValueError, yaml.YAMLError, AttributeError):
        blockers.append("canonical review_required specification is unreadable")
    if spec.get("id") != exp_id or spec.get("status") != "approved" or spec.get("frozen") is not True or spec.get("approved_by") != decision or spec.get("execution_authorized") is not True:
        blockers.append("prospective specification must bind this ID, approval decision, frozen and authorized state")
    for field in ("hypothesis_id", "version", "budget", "controls", "stopping_rules",
                  "invalidation_rules", "success_criterion", "falsification_criterion"):
        if spec.get(field) in (None, "", [], {}):
            blockers.append(f"prospective specification: {field} missing")
    for field in ("outcome", "result", "observed_result", "conclusion", "verdict"):
        if spec.get(field) not in (None, "", [], {}):
            blockers.append(f"prospective specification: outcome field {field} is prewritten")
    if spec.get("metrics", spec.get("primary_metrics")) in (None, "", [], {}):
        blockers.append("prospective specification: metrics missing")
    impact = spec.get("decision_impact")
    if not isinstance(impact, dict) or not impact.get("on_positive") or not impact.get("on_negative") or impact["on_positive"] == impact["on_negative"]:
        blockers.append("prospective specification: distinct decision_impact outcomes required")
    if plan.get("schema") != PLAN_SCHEMA or plan.get("experiment_id") != exp_id or plan.get("frozen") is not True or plan.get("approved_by") != decision:
        blockers.append("prospective trial plan must bind schema, experiment, frozen state and approval decision")
    if plan.get("specification") != canonical["specification"] or plan.get("specification_sha256") != report["prospective_sha256"].get("specification"):
        blockers.append("prospective trial plan specification SHA-256 binding mismatch")
    task_id = plan.get("task_id")
    if not isinstance(task_id, str) or not re.fullmatch(r"TASK-\d{8}-[0-9a-f]{6}", task_id):
        blockers.append("prospective trial plan: reserved task_id required")
    if not canonical["queue"] or plan.get("queue") != canonical["queue"]:
        blockers.append("prospective trial plan: canonical queue binding missing")
    source_ref = packet.get("source_ref")
    if not isinstance(source_ref, str) or not source_ref.startswith("origin/") or not re.fullmatch(r"origin/[A-Za-z0-9_./-]+", source_ref):
        blockers.append("packet: pushed origin source_ref required")
    else:
        _source_bindings(spec, plan, root, source_ref, blockers)
    required = _trials(plan, root, blockers)
    if queue.get("schema") != "crypto.autoresearch.dispatch_queue.v1" or queue.get("goal_id") != spec.get("goal_id"):
        blockers.append("prospective queue schema or goal binding mismatch")
    tasks = queue.get("tasks") if isinstance(queue.get("tasks"), list) else []
    if tasks:
        try:
            validate_queue(queue, repository_verifier=GitRepositoryVerifier(root))
        except (DispatchError, ValueError, TypeError) as error:
            blockers.append(f"prospective queue: dispatcher structural validation refused: {error}")
    task = next((t for t in tasks if isinstance(t, dict) and t.get("id") == task_id), None)
    if task is None or task.get("role") != "executor":
        blockers.append("prospective queue: executor task missing")
    else:
        binding = {"mode": "experiments", "kind": "run", "experiment_id": exp_id,
                   "trial_plan": canonical["trial_plan"],
                   "trial_plan_sha256": report["prospective_sha256"].get("trial_plan"),
                   "approved_by": decision}
        embedded = task.get("handoff") if isinstance(task.get("handoff"), dict) else {}
        if embedded.get("execution") != binding or handoff.get("execution") != binding:
            blockers.append("prospective queue/handoff: exact trial-plan and approval binding mismatch")
        if handoff.get("id") != task_id or handoff.get("role") != "executor" or task.get("archived_by") != handoff.get("archived_by"):
            blockers.append("prospective queue/handoff: task identity or archive owner mismatch")
        declared = task.get("artifact_paths") if isinstance(task.get("artifact_paths"), list) else []
        missing = sorted(required - set(declared))
        if missing:
            blockers.append(f"prospective executor archive coverage missing: {', '.join(missing[:3])}" + (f" (+{len(missing)-3} more)" if len(missing) > 3 else ""))
        archive = next((t for t in tasks if isinstance(t, dict) and t.get("id") == task.get("archived_by") and t.get("role") == "coordinator"), None)
        archive_binding = archive.get("archive") if isinstance(archive, dict) and isinstance(archive.get("archive"), dict) else {}
        if (archive is None or task_id not in (archive_binding.get("source_task_ids") or [])
                or not paths_within_scopes(sorted(required), archive.get("read_scope") or [])):
            blockers.append("prospective Coordinator archive task does not bind every supervisor and trial artifact path")
    route = packet.get("execution_route")
    if not isinstance(route, dict) or route.get("kind") not in ("implementation", "runbook"):
        blockers.append("packet: lintable runbook or implementation-tier route required")
    elif route["kind"] == "implementation":
        inference = handoff.get("inference") if isinstance(handoff.get("inference"), dict) else {}
        if not isinstance(route.get("reason"), str) or not route["reason"].strip() or inference.get("policy") != "executor-implementation":
            blockers.append("packet: implementation route requires reason and executor-implementation handoff")
    else:
        lint_path, lint_digest = route.get("lint_receipt"), route.get("lint_receipt_sha256")
        lint_bytes = _read(lint_path, "runbook lint receipt", blockers) if lint_path else None
        if (lint_bytes is None or not isinstance(lint_digest, str)
                or not SHA.fullmatch(lint_digest) or _hash(lint_bytes) != lint_digest
                or b"LINT OK" not in lint_bytes):
            blockers.append("packet: runbook route requires an exact LINT OK receipt")
        elif isinstance(source_ref, str) and source_ref.startswith("origin/"):
            if not isinstance(lint_path, str) or Path(lint_path).is_absolute():
                blockers.append("packet: runbook lint receipt must have a committed relative path")
            elif _git_blob(root, source_ref, lint_path) != lint_bytes:
                blockers.append("packet: runbook lint receipt is not committed at source_ref")
    goal_id, lane_id = spec.get("goal_id"), packet.get("lane_id")
    try:
        lanes = load_lanes(root, goal_id, include_refs=False)
        lane = lanes.get(lane_id) if isinstance(lane_id, str) else None
        goal_path = f"ledger/goals/{goal_id}/goal.yaml"
        goal_bytes = (root / goal_path).read_bytes()
        goal = yaml.safe_load(goal_bytes)
        goal = goal.get("research_goal", goal.get("goal", goal))
        if isinstance(source_ref, str) and source_ref.startswith("origin/"):
            remote_goal = _git_blob(root, source_ref, goal_path)
            if remote_goal is None or remote_goal != goal_bytes:
                blockers.append("packet: goal concurrency record is not committed at source_ref")
        cap = goal.get("campaign_budget", {}).get("max_concurrent")
        if (not isinstance(cap, int) or cap < 1 or len([x for x in lanes.values() if x["status"] == "open"]) > cap
                or lane is None or lane["status"] != "open"
                or lane["lane"].get("dispatch_queue_path") != canonical["queue"]):
            blockers.append("packet: no lawful open lane for this queue within goal concurrency")
        elif isinstance(source_ref, str) and source_ref.startswith("origin/"):
            lane_path = f"coordination/goals/{goal_id}/lanes/{lane_id}.lane.json"
            local = (root / lane_path).read_bytes()
            remote = _git_blob(root, source_ref, lane_path)
            if remote is None or local != remote:
                blockers.append("packet: goal lane is not committed with these bytes at source_ref")
    except (OSError, ValueError, TypeError, AttributeError) as error:
        blockers.append(f"packet: goal lane cannot be verified: {error}")
    report["approvable"] = not blockers
    report["blockers"] = sorted(set(blockers))
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, help="JSON packet pointing to prospective final bytes")
    parser.add_argument("--experiment", help="diagnose a current draft without a prospective packet")
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    if bool(args.packet) == bool(args.experiment):
        parser.error("choose exactly one of --packet or --experiment")
    root = args.repo_root.resolve()
    if args.packet:
        packet = json.loads(args.packet.read_text())
    else:
        eid = args.experiment
        packet = {"schema": SCHEMA, "experiment_id": eid,
                  "specification": f"experiments/{eid}/specification.yaml",
                  "trial_plan": f"experiments/{eid}/trial-plan.json",
                  "preview": {"specification": str(root / "experiments" / eid / "specification.yaml"),
                              "trial_plan": str(root / "experiments" / eid / "trial-plan.json")}}
    result = assess(root, packet)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["approvable"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
