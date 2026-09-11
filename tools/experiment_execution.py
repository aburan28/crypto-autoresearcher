#!/usr/bin/env python3
"""Run frozen trial plans inside an already-authorized, claimed executor task.

This is an execution adapter, not another Coordinator or claim service. It
never approves work, releases claims, commits artifacts, or interprets results.
Every process launch reuses research_dispatch.py's current claim/authority view.
"""
from __future__ import annotations

import argparse
from collections import Counter
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import signal
import subprocess
import sys
import tempfile
import time
from typing import Any, Callable

import yaml

PLAN_SCHEMA = "crypto.autoresearch.trial_plan.v1"
RECEIPT_SCHEMA = "crypto.autoresearch.trial_receipt.v1"
REPO = Path(__file__).resolve().parents[1]
GENERATED = ("launch.json", "execution-receipt.json", "command.txt",
             "environment.json", "stdout.log", "stderr.log", "check.stdout.log",
             "check.stderr.log")
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
RUN_ID = re.compile(r"RUN-[A-Za-z0-9]+-[0-9a-f]{6}\Z")


class ExecutionError(ValueError):
    """An operational or protocol impediment; never negative scientific evidence."""


def sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ExecutionError(f"{path}: expected a JSON object")
    return value


def safe_path(root: Path, relative: str) -> Path:
    """Require canonical relative paths and reject symlinks in every component."""
    if not isinstance(relative, str) or not relative or any(c in relative for c in "\x00\n\r\t\\"):
        raise ExecutionError(f"unsafe path: {relative!r}")
    rel = PurePosixPath(relative)
    if (rel.is_absolute() or ".." in rel.parts or rel.as_posix() != relative
            or relative in (".", "")):
        raise ExecutionError(f"unsafe path: {relative!r}")
    current = root.resolve()
    for part in rel.parts:
        current = current / part
        if current.is_symlink():
            raise ExecutionError(f"symlink not allowed: {current}")
    return current


def write_once(path: Path, value: Any) -> None:
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


def positive(value: Any, field: str) -> None:
    if (isinstance(value, bool) or not isinstance(value, (int, float))
            or not math.isfinite(value) or value <= 0):
        raise ExecutionError(f"{field}: expected a finite positive number")


def load_plan(root: Path, path: Path) -> dict[str, Any]:
    path = path.absolute()
    try:
        safe_path(root, path.relative_to(root.resolve()).as_posix())
    except ValueError as error:
        raise ExecutionError("trial plan must be inside the checkout") from error
    plan = read_json(path)
    if plan.get("schema") != PLAN_SCHEMA or plan.get("frozen") is not True:
        raise ExecutionError("trial plan must use the supported schema and be frozen")
    for field in ("experiment_id", "task_id", "approved_by", "specification", "queue"):
        if not isinstance(plan.get(field), str) or not plan[field].strip():
            raise ExecutionError(f"missing {field}")
    spec_path = safe_path(root, plan["specification"])
    if spec_path.parent.name != plan["experiment_id"]:
        raise ExecutionError("specification/experiment ID mismatch")
    if not SHA256.fullmatch(str(plan.get("specification_sha256", ""))):
        raise ExecutionError("missing specification_sha256")
    if sha256(spec_path) != plan["specification_sha256"]:
        raise ExecutionError("specification hash changed; use an additive amendment")
    try:
        document = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as error:
        raise ExecutionError(f"malformed specification: {error}") from error
    if not isinstance(document, dict):
        raise ExecutionError("specification is not a mapping")
    spec = document.get("experiment", document)
    if (not isinstance(spec, dict) or spec.get("id") != plan["experiment_id"]
            or spec.get("status") != "approved" or spec.get("frozen") is not True
            or not spec.get("approved_by") or spec.get("execution_authorized") is False):
        raise ExecutionError("specification is not approved, frozen and execution-authorized")
    safe_path(root, plan["queue"])
    sources = plan.get("source_sha256")
    if not isinstance(sources, dict) or not sources:
        raise ExecutionError("source_sha256 must bind the driver, checker and dependencies")
    for source, digest in sources.items():
        safe_path(root, source)
        if not isinstance(digest, str) or not SHA256.fullmatch(digest):
            raise ExecutionError(f"invalid source hash: {source}")
    trials = plan.get("trials")
    if not isinstance(trials, list) or not trials:
        raise ExecutionError("trials must explicitly enumerate the frozen protocol; no empty plans")
    ids: set[str] = set()
    runs: set[str] = set()
    for trial in trials:
        if not isinstance(trial, dict):
            raise ExecutionError("trial must be an object")
        tid, rid = trial.get("id"), trial.get("run_id")
        if not isinstance(tid, str) or not tid.strip() or tid in ids:
            raise ExecutionError("trial IDs must be nonempty and unique")
        if not isinstance(rid, str) or not RUN_ID.fullmatch(rid) or rid in runs:
            raise ExecutionError("run IDs must be unique, allocated random-suffix RUN IDs")
        ids.add(tid)
        runs.add(rid)
        for field in ("argv", "check_argv"):
            argv = trial.get(field)
            if (not isinstance(argv, list) or not argv or not all(
                    isinstance(arg, str) and arg and "\x00" not in arg for arg in argv)):
                raise ExecutionError(f"{tid}.{field}: expected argv array, never a shell string")
            # A hash-bound source must occur literally in both commands. Commands
            # and the complete source closure are still reviewed as part of the plan.
            if any("bedrock" in arg.lower() for arg in argv):
                raise ExecutionError("Bedrock is prohibited")
            if not any(source in argv for source in sources):
                raise ExecutionError(f"{tid}.{field}: no hash-bound source")
        artifacts = trial.get("artifacts")
        if (not isinstance(artifacts, list) or not artifacts
                or not all(isinstance(name, str) and name for name in artifacts)
                or len(set(artifacts)) != len(artifacts)
                or "manifest.yaml" not in artifacts or "raw-result.json" not in artifacts):
            raise ExecutionError(f"{tid}: require manifest.yaml and raw-result.json artifacts")
        for name in artifacts:
            safe_path(run_root(root, plan, trial), name)
            if name in GENERATED:
                raise ExecutionError(f"{tid}: reserved artifact name {name}")
        allow_empty = trial.get("allow_empty_artifacts", [])
        if (not isinstance(allow_empty, list)
                or not all(isinstance(name, str) and name for name in allow_empty)
                or len(set(allow_empty)) != len(allow_empty)):
            raise ExecutionError(f"{tid}.allow_empty_artifacts: expected unique artifact names")
        for name in allow_empty:
            safe_path(run_root(root, plan, trial), name)
            if name in GENERATED or name not in artifacts:
                raise ExecutionError(f"{tid}.allow_empty_artifacts: undeclared or reserved artifact {name}")
        positive(trial.get("memory_mb"), f"{tid}.memory_mb")
        watchdog = trial.get("watchdog_seconds")
        if watchdog is not None:
            positive(watchdog, f"{tid}.watchdog_seconds")
            if not isinstance(trial.get("watchdog_reason"), str) or not trial["watchdog_reason"].strip():
                raise ExecutionError("watchdog requires an explicit machine-protection reason")
    # Dependencies must refer to earlier declared trials: this is a frozen,
    # deterministic topological order, not an adaptive search/stopping policy.
    earlier: set[str] = set()
    for trial in trials:
        dependencies = trial.get("depends_on", [])
        if (not isinstance(dependencies, list) or not all(isinstance(x, str) for x in dependencies)
                or len(set(dependencies)) != len(dependencies) or not set(dependencies) <= earlier):
            raise ExecutionError("trial dependencies must be unique IDs of earlier trials")
        earlier.add(trial["id"])
    return plan


def run_root(root: Path, plan: dict[str, Any], trial: dict[str, Any]) -> Path:
    parent = PurePosixPath(plan["specification"]).parent
    return safe_path(root, f"{parent}/runs/{trial['run_id']}")


def trial_state(root: Path, plan: dict[str, Any], trial: dict[str, Any], plan_hash: str) -> str:
    directory = run_root(root, plan, trial)
    if not directory.exists():
        return "planned"
    # Mere existence is NOT completion and is NOT permission to launch again.
    try:
        receipt = read_json(safe_path(directory, "execution-receipt.json"))
        if (receipt.get("schema") != RECEIPT_SCHEMA or receipt.get("plan_sha256") != plan_hash
                or receipt.get("trial_id") != trial["id"] or receipt.get("run_id") != trial["run_id"]):
            return "needs_reconciliation"
        if (receipt.get("status") != "output_validated" or receipt.get("returncode") != 0
                or receipt.get("check_returncode") != 0):
            return "needs_reconciliation"
        expected = set(trial["artifacts"]) | (set(GENERATED) - {"execution-receipt.json"})
        hashes = receipt.get("artifact_sha256")
        if not isinstance(hashes, dict) or set(hashes) != expected:
            return "needs_reconciliation"
        if any(sha256(safe_path(directory, name)) != digest for name, digest in hashes.items()):
            return "needs_reconciliation"
        return "output_validated"
    except (OSError, ValueError, TypeError):
        return "needs_reconciliation"


def coverage(root: Path, path: Path) -> dict[str, Any]:
    plan = load_plan(root, path)
    digest = sha256(path)
    states = {t["id"]: trial_state(root, plan, t, digest) for t in plan["trials"]}
    for trial in plan["trials"]:
        if states[trial["id"]] == "planned" and any(
                states[dep] != "output_validated" for dep in trial.get("depends_on", [])):
            states[trial["id"]] = "waiting_on_dependencies"
    counts = Counter(states.values())
    return {"experiment_id": plan["experiment_id"], "plan_sha256": digest,
            "required": len(states), "output_validated": counts["output_validated"],
            "remaining": len(states) - counts["output_validated"],
            "planned": counts["planned"], "waiting_on_dependencies": counts["waiting_on_dependencies"],
            "needs_reconciliation": counts["needs_reconciliation"],
            "measurement_complete": counts["output_validated"] == len(states),
            "publication_verified": False, "scientific_review_verified": False,
            "trials": states}


def git(root: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=False)
    if result.returncode:
        raise ExecutionError(f"git {args[0]} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def committed(root: Path, path: Path) -> None:
    relative = path.relative_to(root.resolve()).as_posix()
    result = subprocess.run(["git", "-C", str(root), "show", f"HEAD:{relative}"],
                            capture_output=True, check=False)
    if result.returncode or result.stdout != path.read_bytes():
        raise ExecutionError(f"uncommitted or changed input: {relative}")


def authorize(root: Path, path: Path, plan: dict[str, Any], owner: str, epoch: int) -> dict[str, Any]:
    """Re-render the existing dispatcher, including its archive and claims gates."""
    for relative in (plan["specification"], plan["queue"], *plan["source_sha256"]):
        file = safe_path(root, relative)
        committed(root, file)
        if relative in plan["source_sha256"] and sha256(file) != plan["source_sha256"][relative]:
            raise ExecutionError(f"source hash changed: {relative}")
    committed(root, path)
    committed(root, root / "tools/research_dispatch.py")
    # Recheck authorization fields immediately before launching, not just on selection.
    load_plan(root, path)
    with tempfile.TemporaryDirectory(prefix="execution-dispatch-") as temporary:
        output, report = Path(temporary) / "plan.json", Path(temporary) / "plan.md"
        result = subprocess.run(
            [sys.executable, str(root / "tools/research_dispatch.py"), str(root / plan["queue"]),
             "--repo-root", str(root), "--claims", "refs", "--now", datetime.now(timezone.utc).isoformat(),
             "--output", str(output), "--report", str(report)],
            cwd=root, capture_output=True, text=True, check=False)
        if result.returncode:
            raise ExecutionError(f"dispatcher refused execution: {result.stderr.strip()}")
        dispatch = read_json(output)
    gates = dispatch.get("gates")
    if (dispatch.get("schema") != "crypto.autoresearch.dispatch_plan.v1"
            or not isinstance(gates, dict) or not gates or any(v is not True for v in gates.values())):
        raise ExecutionError("dispatcher gates failed")
    task = next((t for t in dispatch.get("dispatches", []) if t.get("id") == plan["task_id"]), None)
    if not task or task.get("role") != "executor" or task.get("state") != "running":
        raise ExecutionError("execution mode requires an admitted, claimed executor task")
    claim = task.get("claim") or {}
    if claim.get("status") != "live" or claim.get("owner") != owner or claim.get("epoch") != epoch:
        raise ExecutionError("missing live claim or wrong owner/epoch; claim through goal_lanes.py")
    expires = datetime.fromisoformat(claim["expires_at"].replace("Z", "+00:00"))
    if expires.tzinfo is None or expires <= datetime.now(timezone.utc):
        raise ExecutionError("claim is expired or has no timezone")
    claim_file = safe_path(root, str(PurePosixPath(plan["queue"]).parent /
                                   "claims" / f"{plan['task_id']}.{epoch}.claim.json"))
    committed(root, claim_file)
    claim_relative = claim_file.relative_to(root).as_posix()
    claim_commit = git(root, "log", "-1", "--format=%H", "--", claim_relative)
    if not claim_commit or not git(root, "for-each-ref", f"--contains={claim_commit}",
                                   "--format=%(refname)", "refs/remotes/origin/"):
        raise ExecutionError("claim is not visible in origin tracking refs; publish/fetch before launch")
    handoff = task.get("handoff") or {}
    binding = handoff.get("execution") or {}
    required_binding = {"mode": "experiments", "kind": "run", "experiment_id": plan["experiment_id"],
                        "trial_plan": path.relative_to(root).as_posix(), "trial_plan_sha256": sha256(path),
                        "approved_by": plan["approved_by"]}
    if binding != required_binding:
        raise ExecutionError("handoff must bind this exact execution-only plan and approval")
    budget = handoff.get("budget") or {}
    if any(budget.get(key) == 0 for key in ("maximum_runs", "experiment_maximum_runs")):
        raise ExecutionError("zero-run task cannot execute trials")
    paths = set(task.get("artifact_paths") or [])
    for trial in plan["trials"]:
        directory = run_root(root, plan, trial)
        for name in (*GENERATED, *trial["artifacts"]):
            relative = (directory / name).relative_to(root).as_posix()
            if relative not in paths:
                raise ExecutionError(f"handoff archive coverage missing: {relative}")
        # This is a per-process address-space ceiling, not an aggregate cgroup limit.
        if budget.get("memory_gb") is not None and trial["memory_mb"] > float(budget["memory_gb"]) * 1024:
            raise ExecutionError("trial memory exceeds handoff protection")
    return {"owner": owner, "epoch": epoch, "expires_at": expires.isoformat(),
            "dispatch_plan_sha256": dispatch.get("plan_sha256"), "commit": git(root, "rev-parse", "HEAD")}


@contextmanager
def task_lock(root: Path, task_id: str):
    """Same-host, cross-worktree exclusion; claims remain the cross-host authority."""
    import fcntl
    common = Path(git(root, "rev-parse", "--git-common-dir"))
    if not common.is_absolute():
        common = root / common
    directory = common / "experiment-execution-locks"
    directory.mkdir(exist_ok=True)
    name = hashlib.sha256(task_id.encode()).hexdigest() + ".lock"
    with (directory / name).open("a+") as stream:
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise ExecutionError(f"task already has a local supervisor: {task_id}") from error
        yield stream.fileno()


def terminate_group(process: subprocess.Popen) -> None:
    # Kill the group even if the leader exited; detached descendants are forbidden.
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    process.wait()


def run_process(argv: list[str], root: Path, directory: Path, prefix: str, trial: dict[str, Any],
                authority: dict[str, Any], lock_fd: int) -> tuple[str, int | None]:
    import resource
    def limits() -> None:
        ceiling = int(trial["memory_mb"] * 1024 * 1024)
        resource.setrlimit(resource.RLIMIT_AS, (ceiling, ceiling))
    started = time.monotonic()
    expiry = datetime.fromisoformat(authority["expires_at"])
    watchdog = trial.get("watchdog_seconds")
    process = None
    with (directory / f"{prefix}stdout.log").open("xb") as stdout, (directory / f"{prefix}stderr.log").open("xb") as stderr:
        try:
            process = subprocess.Popen(argv, cwd=root, stdin=subprocess.DEVNULL, stdout=stdout,
                                       stderr=stderr, start_new_session=True, preexec_fn=limits,
                                       pass_fds=(lock_fd,))
            while process.poll() is None:
                if datetime.now(timezone.utc) >= expiry:
                    return "claim_expired", None
                if watchdog is not None and time.monotonic() - started >= watchdog:
                    return "watchdog_expired", None
                time.sleep(0.05)
            return "exited", process.returncode
        finally:
            if process is not None:
                terminate_group(process)


def execute_trial(root: Path, path: Path, plan: dict[str, Any], trial: dict[str, Any],
                  authority: dict[str, Any], lock_fd: int) -> str:
    directory = run_root(root, plan, trial)
    directory.parent.mkdir(parents=True, exist_ok=True)
    directory.mkdir()  # exclusive; even an empty interrupted attempt is never reused
    digest = sha256(path)
    argv = [arg.replace("{run_dir}", str(directory)) for arg in trial["argv"]]
    checker = [arg.replace("{run_dir}", str(directory)) for arg in trial["check_argv"]]
    started = datetime.now(timezone.utc).isoformat()
    write_once(directory / "launch.json", {"plan_sha256": digest, "trial_id": trial["id"],
               "run_id": trial["run_id"], "started_at": started, "authority": authority,
               "argv": argv, "check_argv": checker, "supervisor_pid": os.getpid()})
    with (directory / "command.txt").open("x") as stream:
        stream.write(json.dumps(argv) + "\n")
    write_once(directory / "environment.json", {"python": sys.version, "platform": sys.platform,
               "source_sha256": plan["source_sha256"], "specification_sha256": plan["specification_sha256"],
               "commit": authority["commit"]})  # never dump credential-bearing environment variables
    status, returncode, check_returncode = "infrastructure_error", None, None
    detail = None
    interrupted = False
    try:
        state, returncode = run_process(argv, root, directory, "", trial, authority, lock_fd)
        if state != "exited":
            status = state
        elif returncode != 0:
            status = "infrastructure_error"
        else:
            state, check_returncode = run_process(checker, root, directory, "check.", trial, authority, lock_fd)
            status = (state if state != "exited" else
                      "output_validated" if check_returncode == 0 else "invalid_output")
        if status == "output_validated":
            allow_empty = set(trial.get("allow_empty_artifacts", []))
            for name in trial["artifacts"]:
                file = safe_path(directory, name)
                if not file.is_file() or (file.stat().st_size == 0 and name not in allow_empty):
                    raise ExecutionError(f"missing/empty required artifact: {name}")
    except KeyboardInterrupt:
        status, interrupted = "interrupted", True
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        status, detail = "invalid_output" if returncode == 0 else "infrastructure_error", str(error)
    # Failed launches/checks still get all declared log paths, never invented output.
    for name in ("stdout.log", "stderr.log", "check.stdout.log", "check.stderr.log"):
        target = safe_path(directory, name)
        if not target.exists():
            target.touch(exist_ok=False)
    artifacts = {}
    for name in (*trial["artifacts"], *(n for n in GENERATED if n != "execution-receipt.json")):
        try:
            file = safe_path(directory, name)
            if file.is_file():
                artifacts[name] = sha256(file)
        except (OSError, ValueError):
            status = "invalid_output"
    write_once(directory / "execution-receipt.json", {
        "schema": RECEIPT_SCHEMA, "plan_sha256": digest, "trial_id": trial["id"],
        "run_id": trial["run_id"], "status": status, "returncode": returncode,
        "check_returncode": check_returncode, "started_at": started,
        "finished_at": datetime.now(timezone.utc).isoformat(), "detail": detail,
        "artifact_sha256": artifacts, "authority": authority,
        "scientific_conclusion": None, "published": False})
    if interrupted:
        raise KeyboardInterrupt
    return status


def run_plan(root: Path, path: Path, owner: str, epoch: int, *,
             gate: Callable[..., dict[str, Any]] = authorize) -> dict[str, Any]:
    root, path = root.resolve(), path.absolute()
    if os.name != "posix":
        raise ExecutionError("process-group and address-space guards require POSIX")
    plan = load_plan(root, path)
    with task_lock(root, plan["task_id"]) as fd:
        digest = sha256(path)
        for trial in plan["trials"]:
            if coverage(root, path)["trials"][trial["id"]] != "planned":
                continue
            authority = gate(root, path, plan, owner, epoch)
            if sha256(path) != digest:
                raise ExecutionError("trial plan changed during execution")
            execute_trial(root, path, plan, trial, authority, fd)
    return coverage(root, path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("status", "run"))
    parser.add_argument("--repo", type=Path, default=REPO)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--owner")
    parser.add_argument("--epoch", type=int)
    args = parser.parse_args(argv)
    root = args.repo.resolve()
    path = args.plan if args.plan.is_absolute() else root / args.plan
    def interrupt(*_: Any) -> None:
        raise KeyboardInterrupt
    previous = signal.signal(signal.SIGTERM, interrupt)
    try:
        if args.command == "status":
            report = coverage(root, path)
        else:
            if not args.owner or not args.epoch or args.epoch < 1:
                raise ExecutionError("run requires the published claim's --owner and positive --epoch")
            report = run_plan(root, path, args.owner, args.epoch)
        print(json.dumps(report, indent=2))
        return 0 if report["measurement_complete"] or args.command == "status" else 3
    except KeyboardInterrupt:
        print("execution interrupted; preserve attempts and reconcile ownership", file=sys.stderr)
        return 130
    except (OSError, ValueError, TypeError) as error:
        print(f"execution impediment: {error}", file=sys.stderr)
        return 2
    finally:
        signal.signal(signal.SIGTERM, previous)


if __name__ == "__main__":
    raise SystemExit(main())
