#!/usr/bin/env python3
"""Runtime-bound independent audit of one immutable local dependency image.

The audit invokes only ``docker image inspect`` and ``docker image save`` for
the exact image ID.  A parent process samples RSS for its one owned worker and
the worker's observed descendants.  The sampled watchdog is machine protection;
it is not a kernel-enforced memory limit.  Archive members are read as data and
are never extracted or executed.
"""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import resource
import shutil
import signal
import subprocess
import sys
import tarfile
import tempfile
import time

import yaml


TASK = "TASK-20260910-f5b472"
PRODUCER_TASK = "TASK-20260908-6e8eee"
IMAGE = "sha256:376f4a364f0b4cf1422b0f4ef1855b080e91ac858b47ef94dd8eee764d1eb3a7"
BASE = "sha256:c89921a0c7b42f27338ed8c279fb370e69e941c92460f91895d08304e844b0b4"
TAG = "crypto-autoresearcher/bsgs-deps:task-20260908-6e8eee"
SOCKET = "unix:///Users/adamburan/.docker/run/docker.sock"
DOCKER = ["/usr/local/bin/docker", "--host", SOCKET]
AUTHORITY = "c41a91098fd89c85b8518a6b3f544a78cac77847"
CLAIM_COMMIT = "9b501eba7d22f7a9d30076a0fce718cdd0f90a39"
SOURCE_SNAPSHOT = "2b7ecb4ab3285174132eb37156676a6732952e95"
RETRY_AUTHORITY = "f40919ca2097099074d95180a8b16b430f31897a"
CLAIM_OWNER = "coordinator-reserve-admission-20260907"
CLAIM_SESSION = "01a07d92-d309-7620-9947-a358afc60883"
MAX_BYTES = 2 * 1024**3
BUFFER = 1024 * 1024
MAX_CONTROLS = 128
SUITE_SIZE = 48
WATCHDOG_INTERVAL_SECONDS = 0.05
WATCHDOG_MAX_CADENCE_SECONDS = 0.1
WATCHDOG_THRESHOLD_BYTES = 2 * 1024**3
WORKER_TIMEOUT_SECONDS = 900

# Every repository path is configured from explicit --repo after argument
# parsing.  No parent-depth inference or import-time repository lookup occurs.
REPO: Path | None = None
HANDOFF: Path | None = None
CLAIM: Path | None = None
PLAN: Path | None = None
METADATA: Path | None = None
APPROVAL: Path | None = None
BINDING: Path | None = None
PREPARATION: Path | None = None
ATTEMPT1: Path | None = None
SNAPSHOT: Path | None = None
PREVIOUS_CHECKER: Path | None = None
PREVIOUS_REVIEW: Path | None = None
PREVIOUS_RECEIPT: Path | None = None
PORTABLE_CHECKER: Path | None = None
PORTABLE_REVIEW: Path | None = None
PORTABLE_RECEIPT: Path | None = None
PORTABLE_SNAPSHOT: Path | None = None
PREFLIGHT: Path | None = None
CURRENT_JOURNAL_DIR: Path | None = None


def configure_repo(repo: Path) -> None:
    global REPO, HANDOFF, CLAIM, PLAN, METADATA, APPROVAL, BINDING
    global PREPARATION, ATTEMPT1, SNAPSHOT, PREVIOUS_CHECKER, PREVIOUS_REVIEW
    global PREVIOUS_RECEIPT, PORTABLE_CHECKER, PORTABLE_REVIEW
    global PORTABLE_RECEIPT, PORTABLE_SNAPSHOT, PREFLIGHT
    resolved = repo.resolve(strict=True)
    if not (resolved / "AGENTS.md").is_file():
        raise ValueError("explicit --repo does not identify the bound repository")
    REPO = resolved
    HANDOFF = REPO / "ledger/handoffs/TASK-20260910-f5b472.yaml"
    CLAIM = REPO / "coordination/experiment-reserve/BATCH-635652/claims/TASK-20260910-f5b472.1.claim.json"
    PLAN = REPO / "coordination/experiment-reserve/BATCH-635652/review-plan-TASK-20260910-f5b472.yaml"
    METADATA = REPO / "coordination/experiment-reserve/BATCH-635652/runtime-bindings/DEC-20260908-f39556/dependencies.json"
    APPROVAL = REPO / "ledger/decisions/DEC-20260908-f39556.yaml"
    BINDING = REPO / "coordination/experiment-reserve/BATCH-635652/runtime/TASK-20260908-6e8eee/image-binding.json"
    PREPARATION = REPO / "coordination/experiment-reserve/BATCH-635652/runtime/TASK-20260908-6e8eee/preparation-receipt.json"
    ATTEMPT1 = REPO / "coordination/experiment-reserve/BATCH-635652/runtime-bindings/DEC-20260908-d687ab/attempt1.json"
    SNAPSHOT = REPO / "coordination/experiment-reserve/BATCH-635652/archives/TASK-20260908-67e682/snapshot.json"
    PREVIOUS_CHECKER = REPO / "coordination/experiment-reserve/BATCH-635652/reviews/TASK-20260909-d033ac/checks.py"
    PREVIOUS_REVIEW = REPO / "coordination/experiment-reserve/BATCH-635652/reviews/TASK-20260909-d033ac/review.yaml"
    PREVIOUS_RECEIPT = REPO / "coordination/experiment-reserve/BATCH-635652/reviews/TASK-20260909-d033ac/check-receipt.json"
    PORTABLE_CHECKER = REPO / "coordination/experiment-reserve/BATCH-635652/reviews/TASK-20260909-3bc94a/checks.py"
    PORTABLE_REVIEW = REPO / "coordination/experiment-reserve/BATCH-635652/reviews/TASK-20260909-3bc94a/review.yaml"
    PORTABLE_RECEIPT = REPO / "coordination/experiment-reserve/BATCH-635652/reviews/TASK-20260909-3bc94a/check-receipt.json"
    PORTABLE_SNAPSHOT = REPO / "coordination/experiment-reserve/BATCH-635652/archives/TASK-20260909-876712/snapshot.json"
    PREFLIGHT = REPO / "coordination/experiment-reserve/admission-20260907/owned-process-sampling-preflight-20260909.json"


def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def canonical(value) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb", buffering=BUFFER) as handle:
        while True:
            chunk = handle.read(BUFFER)
            if not chunk:
                return digest.hexdigest()
            digest.update(chunk)


def write_json_exclusive(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, allow_nan=False)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())


def write_reserved_json(path: Path, value) -> None:
    """Fill one externally pre-reserved empty regular file exactly once."""
    info = path.lstat()
    if not path.is_file() or info.st_size != 0 or info.st_nlink != 1:
        raise ValueError(f"invalid pre-reserved sink: {path}")
    flags = os.O_WRONLY | os.O_TRUNC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags)
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, allow_nan=False)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())


def append_journal(path: Path, value) -> None:
    encoded = canonical(value)
    descriptor = os.open(path, os.O_WRONLY | os.O_APPEND)
    with os.fdopen(descriptor, "ab", buffering=0) as handle:
        handle.write(encoded)
        os.fsync(handle.fileno())


def raw_file_record(path: Path, include_base64: bool = True) -> dict:
    data = path.read_bytes()
    row = {"path": str(path), "bytes": len(data), "sha256": sha_bytes(data)}
    if include_base64:
        row["base64"] = base64.b64encode(data).decode("ascii")
        row["lossless_inline"] = True
    else:
        row["lossless_inline"] = False
        row["retention"] = "hash_and_size_after_owned_export_deletion"
    return row


def durable_command_record(argv: list[str], timeout: int, stdout_path: Path | None = None) -> dict:
    """Run one bounded command with durable raw custody before interpretation."""
    if CURRENT_JOURNAL_DIR is None:
        raise RuntimeError("durable command journal is not configured")
    if any("bedrock" in str(value).lower() for value in argv):
        raise ValueError("prohibited provider token in command")
    if argv and argv[0] == "/usr/local/bin/docker":
        if argv[: len(DOCKER)] != DOCKER or argv[len(DOCKER):] not in (
            ["image", "inspect", IMAGE],
            ["image", "save", IMAGE],
        ):
            raise ValueError("Docker command is outside exact read-only inspect/save allow-list")
    journal = CURRENT_JOURNAL_DIR
    journal.mkdir(parents=True, exist_ok=True)
    index = len(list(journal.glob("command-*.start.json")))
    prefix = journal / f"command-{index:04d}"
    out_path = stdout_path if stdout_path is not None else prefix.with_suffix(".stdout.bin")
    err_path = prefix.with_suffix(".stderr.bin")
    if stdout_path is None and out_path.exists():
        raise FileExistsError(f"command stdout path exists: {out_path}")
    if stdout_path is not None and out_path.exists():
        raise FileExistsError(f"exclusive export path already exists: {out_path}")
    if err_path.exists():
        raise FileExistsError(f"command stderr path exists: {err_path}")
    start_row = {
        "sequence": index,
        "argv": argv,
        "command_sha256": sha_bytes(canonical(argv)),
        "started_at_UTC": utc(),
        "timeout_seconds": timeout,
        "stdout_path": str(out_path),
        "stderr_path": str(err_path),
        "redirection_before_launch": True,
    }
    write_json_exclusive(prefix.with_suffix(".start.json"), start_row)
    append_journal(journal.parent / "supervisor.journal.jsonl", {"phase": "command_start", **start_row})
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    started = time.monotonic()
    timed_out = False
    terminal_observed = False
    exit_code = None
    pid = None
    launch_exception = None
    timeout_termination = []
    out_descriptor = os.open(out_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    err_descriptor = os.open(err_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(out_descriptor, "wb", buffering=BUFFER) as out_handle, os.fdopen(
            err_descriptor, "wb", buffering=BUFFER
        ) as err_handle:
            try:
                proc = subprocess.Popen(
                    argv,
                    stdout=out_handle,
                    stderr=err_handle,
                    start_new_session=True,
                )
                pid = proc.pid
                try:
                    exit_code = proc.wait(timeout=timeout)
                    terminal_observed = True
                except subprocess.TimeoutExpired:
                    timed_out = True
                    try:
                        os.killpg(proc.pid, signal.SIGTERM)
                        timeout_termination.append({"signal": signal.SIGTERM, "sent": True})
                    except BaseException as cleanup_exc:
                        timeout_termination.append({"signal": signal.SIGTERM, "sent": False, "error": repr(cleanup_exc)})
                    try:
                        exit_code = proc.wait(timeout=2)
                        terminal_observed = True
                    except subprocess.TimeoutExpired:
                        try:
                            os.killpg(proc.pid, signal.SIGKILL)
                            timeout_termination.append({"signal": signal.SIGKILL, "sent": True})
                        except BaseException as cleanup_exc:
                            timeout_termination.append({"signal": signal.SIGKILL, "sent": False, "error": repr(cleanup_exc)})
                        try:
                            exit_code = proc.wait(timeout=5)
                            terminal_observed = True
                        except BaseException as cleanup_exc:
                            timeout_termination.append({"reap_error": repr(cleanup_exc)})
            except BaseException as exc:
                launch_exception = {"type": type(exc).__name__, "message": str(exc), "repr": repr(exc)}
    finally:
        after = resource.getrusage(resource.RUSAGE_CHILDREN)
        raw_row = {
            **start_row,
            "pid": pid,
            "ended_at_UTC": utc(),
            "wall_seconds": time.monotonic() - started,
            "host_child_cpu_seconds": (after.ru_utime + after.ru_stime) - (before.ru_utime + before.ru_stime),
            "exit_code": exit_code,
            "timed_out": timed_out,
            "terminal_observed": terminal_observed,
            "launch_exception": launch_exception,
            "timeout_termination": timeout_termination,
            "stdout_raw": raw_file_record(out_path, include_base64=stdout_path is None),
            "stderr_raw": raw_file_record(err_path, include_base64=True),
        }
        write_json_exclusive(prefix.with_suffix(".result.raw.json"), raw_row)
        append_journal(journal.parent / "supervisor.journal.jsonl", {"phase": "command_raw_terminal", **raw_row})
    # Decoding happens only after the lossless raw result is fsync'd.
    row = dict(raw_row)
    if stdout_path is None:
        out_bytes = out_path.read_bytes()
        row["stdout"] = out_bytes.decode("utf-8", errors="replace")
        row["stdout_decoding"] = "utf-8-errors-replace-supplementary"
    err_bytes = err_path.read_bytes()
    row["stderr"] = err_bytes.decode("utf-8", errors="replace")
    row["stderr_decoding"] = "utf-8-errors-replace-supplementary"
    write_json_exclusive(prefix.with_suffix(".result.parsed.json"), row)
    append_journal(journal.parent / "supervisor.journal.jsonl", {"phase": "command_parsed_terminal", **row})
    return row


def load_bound_checker():
    if PREVIOUS_CHECKER is None:
        raise RuntimeError("explicit repository configuration is missing")
    spec = importlib.util.spec_from_file_location("bound_predecessor_checker", PREVIOUS_CHECKER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load bound predecessor checker source")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.TASK = TASK
    module.PRODUCER_TASK = PRODUCER_TASK
    module.IMAGE = IMAGE
    module.BASE = BASE
    module.TAG = TAG
    module.SOCKET = SOCKET
    module.DOCKER = DOCKER
    module.AUTHORITY = AUTHORITY
    module.CLAIM_COMMIT = CLAIM_COMMIT
    module.SOURCE_SNAPSHOT = SOURCE_SNAPSHOT
    module.RETRY_AUTHORITY = RETRY_AUTHORITY
    module.CLAIM_OWNER = CLAIM_OWNER
    module.CLAIM_SESSION = CLAIM_SESSION
    module.MAX_BYTES = MAX_BYTES
    module.BUFFER = BUFFER
    module.MAX_CONTROLS = MAX_CONTROLS
    module.SUITE_SIZE = SUITE_SIZE
    module.REPO = REPO
    module.HANDOFF = HANDOFF
    module.CLAIM = CLAIM
    module.METADATA = METADATA
    module.BINDING = BINDING
    module.PREPARATION = PREPARATION
    module.ATTEMPT1 = ATTEMPT1
    module.SNAPSHOT = SNAPSHOT
    module.PLAN = PLAN
    module.command_record = durable_command_record
    return module


BASE_CHECKER = None


def docker_command_count(commands: list[dict], verb: str) -> int:
    return sum(
        row.get("argv", [])[: len(DOCKER)] == DOCKER
        and row.get("argv", [None] * (len(DOCKER) + 2))[len(DOCKER):len(DOCKER) + 2] == ["image", verb]
        for row in commands
    )


def audit_actual_owned_path_set(export: Path, binding: dict, prior_processed: int) -> dict:
    """Enumerate package-owned image paths, including undeclared extras.

    This is a second pass over the same export.  Its uncompressed member count
    is added to the predecessor pass before enforcing the cumulative 2 GiB cap.
    """
    inventory = binding["inventory"]
    expected = {
        BASE_CHECKER.inventory_absolute(row["path"])
        for package in inventory["packages"].values()
        for row in package["files"]
    }
    site = "usr/local/lib/python3.13/site-packages/"
    roots = {
        site + "sympy",
        site + "sympy-1.14.0.dist-info",
        site + "mpmath",
        site + "mpmath-1.3.0.dist-info",
    }
    exact_nonpackage = {
        path for path in expected
        if not any(path == root or path.startswith(root + "/") for root in roots)
    }

    def targeted(path: str) -> bool:
        return path in exact_nonpackage or any(path == root or path.startswith(root + "/") for root in roots)

    state: dict[str, str] = {}
    nested_declared_bytes = 0
    nested_members = 0
    spools = []
    try:
        with tarfile.open(export, mode="r:") as outer:
            members = {}
            for member in outer:
                name = BASE_CHECKER.safe_archive_name(member.name)
                if name in members:
                    raise ValueError(f"duplicate outer member in extra-path pass: {name}")
                members[name] = member
            legacy = json.loads(BASE_CHECKER.read_tar_bytes(outer, members["manifest.json"]))
            index = json.loads(BASE_CHECKER.read_tar_bytes(outer, members["index.json"]))
            descriptor = index["manifests"][0]
            manifest_path = "blobs/sha256/" + descriptor["digest"].split(":", 1)[1]
            manifest = json.loads(BASE_CHECKER.read_tar_bytes(outer, members[manifest_path]))
            legacy_layers = [BASE_CHECKER.safe_archive_name(name) for name in legacy[0]["Layers"]]
            if len(legacy_layers) != len(manifest["layers"]):
                raise ValueError("extra-path pass layer count mismatch")
            for layer_index, (legacy_path, layer_descriptor) in enumerate(zip(legacy_layers, manifest["layers"])):
                spool, _, _ = BASE_CHECKER.spool_tar_member(outer, members[legacy_path])
                spools.append(spool)
                media = layer_descriptor["mediaType"]
                if media.endswith(".tar"):
                    layer_file = spool
                elif media.endswith(".tar+gzip"):
                    expanded = tempfile.SpooledTemporaryFile(max_size=BUFFER, mode="w+b")
                    spools.append(expanded)
                    spool.seek(0)
                    expanded_size = 0
                    with gzip.GzipFile(fileobj=spool, mode="rb") as source:
                        while True:
                            chunk = source.read(BUFFER)
                            if not chunk:
                                break
                            expanded_size += len(chunk)
                            if prior_processed + expanded_size > MAX_BYTES:
                                raise ValueError("cumulative data exceeds 2 GiB during extra-path expansion")
                            expanded.write(chunk)
                    expanded.seek(0)
                    layer_file = expanded
                else:
                    raise RuntimeError(f"unsupported layer media type in extra-path pass: {media}")
                layer_file.seek(0)
                with tarfile.open(fileobj=layer_file, mode="r:") as nested:
                    seen = set()
                    for member in nested:
                        path = BASE_CHECKER.safe_archive_name(member.name)
                        if path in seen:
                            raise ValueError(f"duplicate nested member in extra-path pass layer {layer_index}: {path}")
                        seen.add(path)
                        nested_members += 1
                        nested_declared_bytes += member.size
                        if prior_processed + nested_declared_bytes > MAX_BYTES:
                            raise ValueError("cumulative processed archive data exceeds 2 GiB")
                        parent, name = os.path.split(path)
                        if name == ".wh..wh..opq":
                            prefix = parent.rstrip("/") + "/"
                            for existing in list(state):
                                if existing.startswith(prefix):
                                    state.pop(existing, None)
                            continue
                        if name.startswith(".wh."):
                            target = (parent.rstrip("/") + "/" + name[4:]).lstrip("/")
                            prefix = target.rstrip("/") + "/"
                            state.pop(target, None)
                            for existing in list(state):
                                if existing.startswith(prefix):
                                    state.pop(existing, None)
                            continue
                        if not targeted(path) or member.isdir():
                            continue
                        if member.isfile():
                            kind = "file"
                        elif member.issym():
                            kind = "symlink"
                        elif member.islnk():
                            kind = "hardlink"
                        else:
                            kind = "special"
                        state[path] = kind
        actual = set(state)
        return {
            "expected_paths": len(expected),
            "actual_owned_paths": len(actual),
            "missing": sorted(expected - actual),
            "extra": sorted(actual - expected),
            "expected_nonregular": sorted(path for path in expected if state.get(path) != "file"),
            "extra_nonregular": sorted(path for path in actual - expected if state[path] != "file"),
            "nested_members_revisited": nested_members,
            "declared_uncompressed_file_bytes_revisited": nested_declared_bytes,
            "cumulative_processed_data_bytes": prior_processed + nested_declared_bytes,
        }
    finally:
        for spool in spools:
            try:
                spool.close()
            except Exception:
                pass


def exact_package_protocol(metadata: dict, approval: dict) -> bool:
    approved = approval["coordinator_decision"]["approved_protocol"]["packages"]
    observed = []
    for package in metadata["packages"]:
        wheel = package["wheel"]
        observed.append({
            "name": package["name"],
            "version": package["version"],
            "filename": wheel["filename"],
            "url": wheel["url"],
            "sha256": wheel["digests"]["sha256"],
            "size": wheel["size"],
        })
    return observed == approved


def classify_error(exc: BaseException) -> str:
    message = str(exc).lower()
    if isinstance(exc, RuntimeError) and (
        "read-only image" in message or "unsupported layer media type" in message
    ):
        return "operational_inconclusive"
    return "evidence_mismatch"


def worker(
    inner_path: Path,
    export_path: Path,
    ready_path: Path,
    release_path: Path,
    attempt_dir: Path,
    nonce: str,
) -> int:
    global BASE_CHECKER, CURRENT_JOURNAL_DIR
    CURRENT_JOURNAL_DIR = attempt_dir / "worker-commands"
    started_utc = utc()
    wall_start = time.monotonic()
    cpu_start = time.process_time()
    ready = {
        "schema": "crypto.autoresearch.sampled_watchdog_barrier.v1",
        "task_id": TASK,
        "worker_pid": os.getpid(),
        "parent_pid": os.getppid(),
        "nonce": nonce,
        "repo": str(REPO),
        "ready_at_UTC": utc(),
        "stage": "before_controls_source_checks_and_any_docker_call",
        "checker_sha256": sha_path(Path(__file__).resolve()),
    }
    write_json_exclusive(ready_path, ready)
    release_deadline = time.monotonic() + 30
    while not release_path.exists():
        if time.monotonic() >= release_deadline:
            raise TimeoutError("watchdog release barrier was not satisfied")
        time.sleep(0.01)
    release = json.loads(release_path.read_bytes())
    if (
        release.get("worker_pid") != os.getpid()
        or release.get("parent_pid") != os.getppid()
        or release.get("watchdog_ready") is not True
        or release.get("nonce") != nonce
        or release.get("checker_sha256") != ready["checker_sha256"]
        or release.get("readiness_record_sha256") != sha_path(attempt_dir / "watchdog-readiness.json")
    ):
        raise ValueError("malformed watchdog release")
    BASE_CHECKER = load_bound_checker()

    audit = BASE_CHECKER.Audit()
    commands = []
    git_rows = []
    source_rows = []
    export_invocations = 0
    export_deleted = False
    preparation_result = None
    archive_result = None
    extra_inventory_result = None
    controls = []
    control_wall = 0.0
    control_cpu = 0.0
    error = None
    error_class = None
    try:
        handoff_doc = yaml.safe_load(HANDOFF.read_text())["handoff"]
        plan_doc = yaml.safe_load(PLAN.read_text())["review_plan"]
        binding = json.loads(BINDING.read_bytes())
        receipt = json.loads(PREPARATION.read_bytes())
        attempt1 = json.loads(ATTEMPT1.read_bytes())
        metadata = json.loads(METADATA.read_bytes())
        approval = yaml.safe_load(APPROVAL.read_text())
        snapshot = json.loads(SNAPSHOT.read_bytes())
        previous_review = yaml.safe_load(PREVIOUS_REVIEW.read_text())["validation_report"]
        previous_receipt = json.loads(PREVIOUS_RECEIPT.read_bytes())
        portable_review = yaml.safe_load(PORTABLE_REVIEW.read_text())["validation_report"]
        portable_receipt = json.loads(PORTABLE_RECEIPT.read_bytes())
        preflight = json.loads(PREFLIGHT.read_bytes())

        audit.check("handoff_task", handoff_doc["id"] == TASK and handoff_doc["to"] == "validator")
        audit.check("review_plan_exact", handoff_doc["review_plan"] == plan_doc)
        audit.check("one_joint_owned", [j["assigned_to"] for j in plan_doc["joints"]] == [TASK])
        audit.check("review_plan_prior_recorded", plan_doc["recorded_before_reviewers"] is True and plan_doc["source_snapshot"] == SOURCE_SNAPSHOT)
        audit.check("inference_policy", handoff_doc["inference"] == {
            "policy": "review-adversarial", "reasoning_effort": "xhigh",
            "fallback_allowed": False, "degraded_allowed": False,
            "independent_session_required": True,
        })
        audit.check("bounded_zero_execution_budget", handoff_doc["budget"]["memory_gb"] == 2 and handoff_doc["budget"]["maximum_workers"] == 1 and handoff_doc["budget"]["maximum_runs"] == 0 and handoff_doc["budget"]["maximum_operational_containers"] == 0 and handoff_doc["budget"]["maximum_watchdog_setup_attempts"] == 2)
        audit.check("exact_three_path_scope", handoff_doc["deliverables"] == handoff_doc["artifact_paths"] == handoff_doc["write_scope"] and len(handoff_doc["write_scope"]) == 3)

        for entry in handoff_doc["source_bindings"]:
            data = (REPO / entry["path"]).read_bytes()
            actual = sha_bytes(data)
            source_rows.append({
                "path": entry["path"], "expected_sha256": entry["sha256"],
                "actual_sha256": actual, "bytes_read": len(data),
                "origin": "post_source_anchor_review_plan" if entry["path"] == str(PLAN.relative_to(REPO)) else "source_anchor_tree",
                "passed": actual == entry["sha256"],
            })
        audit.check("all_34_source_bindings", len(source_rows) == 34 and all(row["passed"] for row in source_rows))
        audit.check("inputs_equal_bindings", handoff_doc["inputs"] == [entry["path"] for entry in handoff_doc["source_bindings"]])
        audit.check(
            "source_anchor_origin_partition",
            sum(row["origin"] == "source_anchor_tree" for row in source_rows) == 33
            and sum(row["origin"] == "post_source_anchor_review_plan" for row in source_rows) == 1,
        )

        claim = json.loads(CLAIM.read_bytes())
        audit.check("claim_identity", claim["task_id"] == TASK and claim["owner"] == CLAIM_OWNER and claim["session"] == CLAIM_SESSION and claim["epoch"] == 1)
        audit.check("claim_location", claim["branch"] == "codex/reserve-control-work-20260908" and claim["worktree"] == str(REPO))
        audit.check("claim_scope", claim["write_scope"] == handoff_doc["write_scope"])
        audit.check("claim_not_forced", claim["forced"] is False and claim["supersedes"] is None)

        git_commands = [
            ["git", "cat-file", "-e", AUTHORITY + "^{commit}"],
            ["git", "cat-file", "-e", CLAIM_COMMIT + "^{commit}"],
            ["git", "merge-base", "--is-ancestor", AUTHORITY, CLAIM_COMMIT],
            ["git", "merge-base", "--is-ancestor", SOURCE_SNAPSHOT, AUTHORITY],
            ["git", "merge-base", "--is-ancestor", RETRY_AUTHORITY, SOURCE_SNAPSHOT],
            ["git", "diff", "--quiet", SOURCE_SNAPSHOT, "--", *handoff_doc["inputs"][:-1]],
            ["git", "diff", "--quiet", AUTHORITY, "--", *handoff_doc["inputs"]],
            ["git", "diff", "--quiet", CLAIM_COMMIT, "--", str(CLAIM.relative_to(REPO))],
            ["git", "rev-parse", CLAIM_COMMIT + "^"],
            ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", CLAIM_COMMIT],
            ["git", "diff", "--quiet", AUTHORITY, "--", str(HANDOFF.relative_to(REPO))],
            ["git", "diff", "--quiet", SOURCE_SNAPSHOT, "--", *snapshot["source_path_sha256"].keys()],
        ]
        for index, argv in enumerate(git_commands, 1):
            row = BASE_CHECKER.command_record(argv, 30)
            git_rows.append(row)
            audit.check(f"git_binding_{index}", BASE_CHECKER.command_ok(row), {
                "argv": argv, "exit_code": row.get("exit_code"), "stderr": row.get("stderr")
            })
        audit.check("claim_immediate_parent_authority", git_rows[8]["stdout"].strip() == AUTHORITY)
        audit.check("published_claim_changes_exactly_one_claim_path", git_rows[9]["stdout"].splitlines() == [str(CLAIM.relative_to(REPO))])
        audit.check("snapshot_source_hashes", all(sha_path(REPO / path) == digest for path, digest in snapshot["source_path_sha256"].items()))
        audit.check("exact_package_metadata_matches_approval", exact_package_protocol(metadata, approval))
        audit.check("metadata_retrieval_no_tls_bypass", "failed local issuer verification and was not weakened" in metadata["retrieval"] and metadata["provenance"] == "retrieved")

        audit.check("previous_rlimit_failure_preserved", previous_review["verdict"] == "incomplete" and previous_review["failed_attempt"]["docker_inspect_invocations"] == 0 and previous_review["failed_attempt"]["docker_export_invocations"] == 0 and previous_review["failed_attempt"]["malformed_control_cases"] == 0 and previous_receipt["outer"]["exit_code"] == 1 and previous_receipt["inner"] is None and "current limit exceeds maximum limit" in previous_receipt["outer"]["stderr"])
        portable_attempts = portable_receipt["attempts"]
        audit.check(
            "two_portable_setup_failures_preserved",
            portable_review["verdict"] == "incomplete"
            and len(portable_attempts) == 2
            and portable_receipt["cumulative_counts"]["watchdog_setup_attempts"] == 2
            and portable_receipt["cumulative_counts"]["docker_image_inspect_invocations"] == 0
            and portable_receipt["cumulative_counts"]["docker_image_export_invocations"] == 0
            and portable_receipt["cumulative_counts"]["malformed_control_cases"] == 0
            and portable_attempts[0]["reservation"]["available"] is False
            and portable_attempts[1]["watchdog"]["outcome"] == "setup_failed",
        )
        prior_checker_bytes_ok = True
        for prior in portable_attempts:
            checker = prior["reservation"]["checker"]
            encoded = checker.get("content_base64")
            if not isinstance(encoded, str):
                prior_checker_bytes_ok = False
                continue
            decoded = base64.b64decode(encoded, validate=True)
            prior_checker_bytes_ok &= len(decoded) == checker["bytes"] and sha_bytes(decoded) == checker["sha256"]
        audit.check("portable_checker_bytes_losslessly_bound", prior_checker_bytes_ok)
        audit.check(
            "escalated_process_preflight_preserved",
            preflight["escalated_environment"]["retained_report"]["commands"][0]["exit_code"] == 1
            and preflight["escalated_environment"]["retained_report"]["commands"][1]["exit_code"] == 0
            and preflight["default_environment"]["retained_command_report"]["commands"][0]["exit_code"] == 3,
        )

        preparation_result = BASE_CHECKER.audit_preparation(audit, handoff_doc, binding, receipt, attempt1, metadata)
        producer_commands = [row for attempt in receipt["attempts"] for row in attempt["inner"]["commands"]]
        curl_urls = [row["argv"][-1] for row in producer_commands if row["argv"][0] == "/usr/bin/curl"]
        expected_urls = sorted(package["wheel"]["url"] for package in metadata["packages"] for _ in range(2))
        audit.check("exact_four_approved_wheel_urls", sorted(curl_urls) == expected_urls)
        start_ids = [row["argv"][-1] for row in producer_commands if row["argv"][:len(DOCKER)] == DOCKER and row["argv"][len(DOCKER):len(DOCKER)+1] == ["start"]]
        removed_ids = [row["argv"][-1] for row in producer_commands if row["argv"][:len(DOCKER)] == DOCKER and row["argv"][len(DOCKER):len(DOCKER)+1] == ["rm"] and row["exit_code"] == 0]
        created_ids = [cid for attempt in receipt["attempts"] for cid in attempt["inner"]["created_containers"]]
        audit.check("three_actual_unique_start_commands", len(start_ids) == 3 and len(set(start_ids)) == 3 and set(start_ids) == set(created_ids))
        audit.check("three_actual_exact_remove_commands", len(removed_ids) == 3 and set(removed_ids) == set(start_ids))

        base_observations = []
        for attempt in receipt["attempts"]:
            base_row = attempt["inner"]["commands"][1]
            parsed = json.loads(base_row["stdout"])
            if not isinstance(parsed, list) or len(parsed) != 1:
                raise ValueError("producer base image inspect output malformed")
            base_observations.append(parsed[0])
        base_layers = base_observations[0]["RootFS"]["Layers"]
        audit.check("retained_base_inspections_exact", all(item["Id"] == BASE and item["Os"] == "linux" and item["Architecture"] == "arm64" and item["RootFS"]["Layers"] == base_layers for item in base_observations))
        audit.check("recorded_prepared_base_layer_prefix", binding["inspection"]["RootFS"]["Layers"][:len(base_layers)] == base_layers and len(binding["inspection"]["RootFS"]["Layers"]) == len(base_layers) + 1)
        preparation_result["retained_base_layer_diff_ids"] = base_layers

        controls, control_wall, control_cpu = BASE_CHECKER.malformed_controls()
        audit.check("all_48_malformed_controls_rejected", len(controls) == SUITE_SIZE and all(row["passed"] for row in controls))
        audit.check("malformed_control_budget", len(controls) <= 48 and len(controls) <= MAX_CONTROLS and MAX_CONTROLS - len(controls) >= SUITE_SIZE)
        audit.check("malformed_case_watchdogs", all(row["wall_seconds"] <= 10 for row in controls) and control_wall <= 1800 and control_cpu <= 1800)

        inspect = BASE_CHECKER.command_record(DOCKER + ["image", "inspect", IMAGE], 30)
        commands.append(inspect)
        audit.check("live_image_inspect_succeeded", BASE_CHECKER.command_ok(inspect))
        if not BASE_CHECKER.command_ok(inspect):
            raise RuntimeError("read-only image inspect failed")
        inspected = json.loads(inspect["stdout"])
        if not isinstance(inspected, list) or len(inspected) != 1:
            raise ValueError("image inspect did not return exactly one object")
        live = inspected[0]
        recorded = binding["inspection"]
        audit.check("live_image_id", live["Id"] == IMAGE)
        audit.check("live_platform", live["Os"] == "linux" and live["Architecture"] == "arm64")
        audit.check("live_config_exact", live["Config"] == recorded["Config"] and live["Config"].get("User") == "65534:65534" and live["Config"].get("Cmd") == ["python3"] and live["Config"].get("WorkingDir") == "/tmp")
        audit.check("live_required_environment", all(value in live["Config"].get("Env", []) for value in ("PYTHONDONTWRITEBYTECODE=1", "PYTHONHASHSEED=0", "SYMPY_GROUND_TYPES=python")))
        audit.check("live_immutable_inspection_core", all(live.get(key) == recorded.get(key) for key in ("Architecture", "Created", "Descriptor", "Id", "Os", "Parent", "RootFS", "Size")))
        audit.check("live_local_tag", TAG in (live.get("RepoTags") or []))

        if export_path.exists():
            raise FileExistsError(f"exclusive export path already exists: {export_path}")
        export_invocations += 1
        saved = BASE_CHECKER.command_record(DOCKER + ["image", "save", IMAGE], 180, export_path)
        commands.append(saved)
        audit.check("single_image_export_succeeded", BASE_CHECKER.command_ok(saved))
        audit.check("export_under_2gib", export_path.exists() and export_path.stat().st_size <= MAX_BYTES)
        if not BASE_CHECKER.command_ok(saved):
            raise RuntimeError("read-only image save failed")
        archive_result = BASE_CHECKER.archive_audit(audit, export_path, live, binding, metadata)
        audit.check("archive_base_layer_prefix_matches_retained_base", archive_result["oci"]["base_layer_prefix"] == base_layers)
        extra_inventory_result = audit_actual_owned_path_set(export_path, binding, archive_result["cumulative_uncompressed_data_bytes"])
        audit.check("actual_owned_path_set_exact", extra_inventory_result["actual_owned_paths"] == 1667 and not extra_inventory_result["missing"] and not extra_inventory_result["extra"])
        audit.check("actual_owned_paths_regular", not extra_inventory_result["expected_nonregular"] and not extra_inventory_result["extra_nonregular"])
        audit.check("two_pass_cumulative_data_under_2gib", extra_inventory_result["cumulative_processed_data_bytes"] <= MAX_BYTES)
    except BaseException as exc:
        error = {"type": type(exc).__name__, "message": str(exc)}
        error_class = classify_error(exc)
    finally:
        if export_path.exists():
            try:
                export_path.unlink()
                export_deleted = not export_path.exists()
            except Exception as exc:
                audit.check("owned_export_deleted", False, repr(exc))
        else:
            export_deleted = True
        audit.check("owned_export_deleted", export_deleted)

    failures = list(audit.failures)
    if error_class == "operational_inconclusive":
        joint_verdict = "inconclusive"
    elif failures or error is not None:
        joint_verdict = "breaks"
    else:
        joint_verdict = "holds"
    own = resource.getrusage(resource.RUSAGE_SELF)
    result = {
        "schema": "crypto.autoresearch.dependency_image_runtime_bound_independent_audit.v1",
        "task_id": TASK,
        "started_at_UTC": started_utc,
        "ended_at_UTC": utc(),
        "status": "passed" if joint_verdict == "holds" else "failed",
        "joint": "dependency_image_byte_identity_and_operational_custody",
        "joint_verdict": joint_verdict,
        "authority": {
            "handoff_commit": AUTHORITY,
            "claim_commit": CLAIM_COMMIT,
            "source_snapshot": SOURCE_SNAPSHOT,
            "retry_authority_commit": RETRY_AUTHORITY,
            "claim_owner": CLAIM_OWNER,
            "claim_session": CLAIM_SESSION,
        },
        "watchdog_barrier_release": release,
        "source_bindings": source_rows,
        "git_commands": git_rows,
        "commands": commands,
        "export_attempts": export_invocations,
        "maximum_export_attempts": 2,
        "export_deleted_after_custody": export_deleted,
        "archive_audit": archive_result,
        "extra_owned_path_audit": extra_inventory_result,
        "preparation_custody": preparation_result,
        "checks": audit.checks,
        "failed_checks": failures,
        "malformed_controls": {
            "cases": controls,
            "cases_executed": len(controls),
            "maximum_cases": MAX_CONTROLS,
            "remaining_case_budget": MAX_CONTROLS - len(controls),
            "complete_suite_limit": 48,
            "complete_suite_reserved_after_this_run": MAX_CONTROLS - len(controls) >= SUITE_SIZE,
            "aggregate_wall_seconds": control_wall,
            "aggregate_cpu_seconds": control_cpu,
        },
        "metrics": {
            "wall_seconds": time.monotonic() - wall_start,
            "process_cpu_seconds": time.process_time() - cpu_start,
            "process_peak_rss_bytes": own.ru_maxrss if sys.platform == "darwin" else own.ru_maxrss * 1024,
            "sampled_watchdog_threshold_bytes": WATCHDOG_THRESHOLD_BYTES,
            "hard_kernel_memory_limit_enforced": False,
            "maximum_workers": 1,
            "stream_buffer_bytes": BUFFER,
            "source_file_comparisons": len(source_rows),
            "scientific_runs": 0,
            "container_creates_or_starts": 0,
            "image_code_executions": 0,
            "docker_image_inspect_invocations": docker_command_count(commands, "inspect"),
            "docker_image_export_invocations": docker_command_count(commands, "save"),
        },
        "error": error,
        "error_class": error_class,
        "limitations": [
            "This verifies the exact local image/archive, wheel, installed-file, configuration and retained preparation custody only.",
            "No container was created or started and no image code or library import was executed by this audit.",
            "Retained import/version outputs are prior operational observations and were not reproduced by image execution.",
            "Coordinator-added image-binding annotations are source statements, not container-emitted measurements.",
            "Repository solver/generator exclusion applies only to copied /opt/reserve-inputs; SymPy contains mathematical solver and generator functions.",
            "The parent watchdog is sampled process observation and can overshoot or miss activity between samples; it is not a kernel-enforced hard 2 GiB limit.",
            "No scientific result, 8 GiB group guard, whole-runtime admission, fixture validity, or launch admission is established.",
        ],
    }
    write_reserved_json(inner_path, result)
    return 0 if result["status"] == "passed" else 1


def worker_retry(
    inner_path: Path,
    export_path: Path,
    ready_path: Path,
    release_path: Path,
    attempt_dir: Path,
    nonce: str,
    prior_attempt_path: Path,
    prior_attempt_sha256: str,
) -> int:
    """Corrected worker: retain attempt-1 successes and retry only image custody."""
    global BASE_CHECKER, CURRENT_JOURNAL_DIR
    CURRENT_JOURNAL_DIR = attempt_dir / "worker-commands"
    started_utc = utc()
    wall_start = time.monotonic()
    cpu_start = time.process_time()
    checker_sha = sha_path(Path(__file__).resolve())
    ready = {
        "schema": "crypto.autoresearch.sampled_watchdog_barrier.v1",
        "task_id": TASK,
        "worker_pid": os.getpid(),
        "parent_pid": os.getppid(),
        "nonce": nonce,
        "repo": str(REPO),
        "ready_at_UTC": utc(),
        "stage": "before_controls_source_checks_and_any_docker_call",
        "checker_sha256": checker_sha,
        "prior_attempt_path": str(prior_attempt_path),
        "prior_attempt_sha256": prior_attempt_sha256,
    }
    write_json_exclusive(ready_path, ready)
    release_deadline = time.monotonic() + 30
    while not release_path.exists():
        if time.monotonic() >= release_deadline:
            raise TimeoutError("watchdog release barrier was not satisfied")
        time.sleep(0.01)
    release = json.loads(release_path.read_bytes())
    if (
        release.get("worker_pid") != os.getpid()
        or release.get("parent_pid") != os.getppid()
        or release.get("watchdog_ready") is not True
        or release.get("nonce") != nonce
        or release.get("checker_sha256") != checker_sha
        or release.get("readiness_record_sha256") != sha_path(attempt_dir / "watchdog-readiness.json")
    ):
        raise ValueError("malformed watchdog release")
    BASE_CHECKER = load_bound_checker()

    audit = BASE_CHECKER.Audit()
    commands = []
    source_rows = []
    export_invocations = 0
    export_deleted = False
    archive_result = None
    extra_inventory_result = None
    error = None
    error_class = None
    prior = None
    prior_inner = None
    controls = []
    try:
        actual_prior_sha = sha_path(prior_attempt_path)
        if actual_prior_sha != prior_attempt_sha256:
            raise ValueError("prior attempt receipt hash mismatch")
        prior = json.loads(prior_attempt_path.read_bytes())
        prior_inner = prior.get("inner")
        if not (
            prior.get("task_id") == TASK
            and prior.get("attempt_number") == 1
            and prior.get("status") == "failed"
            and prior.get("counts", {}).get("docker_image_inspect_invocations") == 1
            and prior.get("counts", {}).get("docker_image_export_invocations") == 0
            and prior.get("counts", {}).get("malformed_control_cases") == 48
            and prior_inner
            and prior_inner.get("joint_verdict") == "inconclusive"
            and prior_inner.get("error", {}).get("message") == "read-only image inspect failed"
            and set(prior_inner.get("failed_checks", [])) == {"offline_pip_commands", "live_image_inspect_succeeded"}
        ):
            raise ValueError("prior attempt is not the exact retained retry basis")
        audit.check(
            "attempt1_exact_hash_and_terminal_retry_basis",
            True,
            {"path": str(prior_attempt_path), "sha256": actual_prior_sha},
        )
        for previous in prior_inner["checks"]:
            if previous["id"] in {"offline_pip_commands", "live_image_inspect_succeeded"}:
                continue
            audit.check(
                "retained_attempt1__" + previous["id"],
                previous["passed"] is True,
                {"reused_without_rerun": True, "prior_detail": previous.get("detail")},
            )
        controls = prior_inner["malformed_controls"]["cases"]
        audit.check(
            "retained_48_malformed_controls_without_rerun",
            len(controls) == 48 and all(row["passed"] for row in controls),
            {"prior_attempt_sha256": actual_prior_sha, "executed_this_attempt": 0},
        )

        handoff_doc = yaml.safe_load(HANDOFF.read_text())["handoff"]
        plan_doc = yaml.safe_load(PLAN.read_text())["review_plan"]
        binding = json.loads(BINDING.read_bytes())
        receipt = json.loads(PREPARATION.read_bytes())
        metadata = json.loads(METADATA.read_bytes())
        approval = yaml.safe_load(APPROVAL.read_text())
        audit.check("review_plan_still_exact", handoff_doc["review_plan"] == plan_doc)
        for entry in handoff_doc["source_bindings"]:
            data = (REPO / entry["path"]).read_bytes()
            actual = sha_bytes(data)
            source_rows.append({
                "path": entry["path"],
                "expected_sha256": entry["sha256"],
                "actual_sha256": actual,
                "bytes_read": len(data),
                "origin": "post_source_anchor_review_plan" if entry["path"] == str(PLAN.relative_to(REPO)) else "source_anchor_tree",
                "passed": actual == entry["sha256"],
            })
        audit.check("all_34_source_bindings_still_exact", len(source_rows) == 34 and all(row["passed"] for row in source_rows))
        audit.check("source_anchor_origin_partition_still_exact", sum(row["origin"] == "source_anchor_tree" for row in source_rows) == 33 and sum(row["origin"] == "post_source_anchor_review_plan" for row in source_rows) == 1)
        audit.check("exact_package_metadata_still_matches_approval", exact_package_protocol(metadata, approval))

        second_install = json.loads(receipt["attempts"][1]["inner"]["commands"][7]["stdout"])
        expected_pip_check = [
            "/usr/local/bin/python3",
            "-m",
            "pip",
            "--disable-pip-version-check",
            "check",
        ]
        audit.check(
            "offline_pip_commands_corrected_predicate",
            len(second_install["commands"]) == 2
            and [row["exit_code"] for row in second_install["commands"]] == [0, 0]
            and all(flag in second_install["commands"][0]["argv"] for flag in ("--no-index", "--no-deps", "--no-compile", "--no-cache-dir", "--require-hashes"))
            and second_install["commands"][1]["argv"] == expected_pip_check
            and second_install["commands"][1]["stdout"] == "No broken requirements found.\n",
            {"attempt1_false_negative_replaced": True, "retained_argv": second_install["commands"][1]["argv"]},
        )

        base_observations = []
        for producer_attempt in receipt["attempts"]:
            base_row = producer_attempt["inner"]["commands"][1]
            parsed = json.loads(base_row["stdout"])
            if not isinstance(parsed, list) or len(parsed) != 1:
                raise ValueError("producer base image inspect output malformed")
            base_observations.append(parsed[0])
        base_layers = base_observations[0]["RootFS"]["Layers"]
        audit.check("retained_base_inspections_exact", all(item["Id"] == BASE and item["Os"] == "linux" and item["Architecture"] == "arm64" and item["RootFS"]["Layers"] == base_layers for item in base_observations))
        audit.check("recorded_prepared_base_layer_prefix", binding["inspection"]["RootFS"]["Layers"][:len(base_layers)] == base_layers and len(binding["inspection"]["RootFS"]["Layers"]) == len(base_layers) + 1)

        inspect = BASE_CHECKER.command_record(DOCKER + ["image", "inspect", IMAGE], 180)
        commands.append(inspect)
        audit.check("live_image_inspect_succeeded", BASE_CHECKER.command_ok(inspect))
        if not BASE_CHECKER.command_ok(inspect):
            raise RuntimeError("read-only image inspect failed")
        inspected = json.loads(inspect["stdout"])
        if not isinstance(inspected, list) or len(inspected) != 1:
            raise ValueError("image inspect did not return exactly one object")
        live = inspected[0]
        recorded = binding["inspection"]
        audit.check("live_image_id", live["Id"] == IMAGE)
        audit.check("live_platform", live["Os"] == "linux" and live["Architecture"] == "arm64")
        audit.check("live_config_exact", live["Config"] == recorded["Config"] and live["Config"].get("User") == "65534:65534" and live["Config"].get("Cmd") == ["python3"] and live["Config"].get("WorkingDir") == "/tmp")
        audit.check("live_required_environment", all(value in live["Config"].get("Env", []) for value in ("PYTHONDONTWRITEBYTECODE=1", "PYTHONHASHSEED=0", "SYMPY_GROUND_TYPES=python")))
        audit.check("live_immutable_inspection_core", all(live.get(key) == recorded.get(key) for key in ("Architecture", "Created", "Descriptor", "Id", "Os", "Parent", "RootFS", "Size")))
        audit.check("live_local_tag", TAG in (live.get("RepoTags") or []))

        if export_path.exists():
            raise FileExistsError(f"exclusive export path already exists: {export_path}")
        export_invocations += 1
        saved = BASE_CHECKER.command_record(DOCKER + ["image", "save", IMAGE], 180, export_path)
        commands.append(saved)
        audit.check("single_image_export_succeeded", BASE_CHECKER.command_ok(saved))
        audit.check("export_under_2gib", export_path.exists() and export_path.stat().st_size <= MAX_BYTES)
        if not BASE_CHECKER.command_ok(saved):
            raise RuntimeError("read-only image save failed")
        archive_result = BASE_CHECKER.archive_audit(audit, export_path, live, binding, metadata)
        audit.check("archive_base_layer_prefix_matches_retained_base", archive_result["oci"]["base_layer_prefix"] == base_layers)
        extra_inventory_result = audit_actual_owned_path_set(export_path, binding, archive_result["cumulative_uncompressed_data_bytes"])
        audit.check("actual_owned_path_set_exact", extra_inventory_result["actual_owned_paths"] == 1667 and not extra_inventory_result["missing"] and not extra_inventory_result["extra"])
        audit.check("actual_owned_paths_regular", not extra_inventory_result["expected_nonregular"] and not extra_inventory_result["extra_nonregular"])
        audit.check("two_pass_cumulative_data_under_2gib", extra_inventory_result["cumulative_processed_data_bytes"] <= MAX_BYTES)
    except BaseException as exc:
        error = {"type": type(exc).__name__, "message": str(exc), "repr": repr(exc)}
        error_class = classify_error(exc)
    finally:
        if export_path.exists():
            try:
                export_hash = sha_path(export_path)
                export_size = export_path.stat().st_size
                export_path.unlink()
                export_deleted = not export_path.exists()
                audit.check("owned_export_deleted", export_deleted, {"bytes": export_size, "sha256": export_hash})
            except BaseException as exc:
                audit.check("owned_export_deleted", False, {"type": type(exc).__name__, "message": str(exc), "repr": repr(exc)})
        else:
            export_deleted = True
            audit.check("owned_export_deleted", True, {"export_was_created": False})

    failures = list(audit.failures)
    if error_class == "operational_inconclusive":
        joint_verdict = "inconclusive"
    elif failures or error is not None:
        joint_verdict = "breaks"
    else:
        joint_verdict = "holds"
    own = resource.getrusage(resource.RUSAGE_SELF)
    result = {
        "schema": "crypto.autoresearch.dependency_image_runtime_bound_independent_audit.v2",
        "task_id": TASK,
        "started_at_UTC": started_utc,
        "ended_at_UTC": utc(),
        "status": "passed" if joint_verdict == "holds" else "failed",
        "joint": "dependency_image_byte_identity_and_operational_custody",
        "joint_verdict": joint_verdict,
        "setup_correction": "reuse-attempt1-source-custody-controls-fix-pip-check-and-inspect-timeout-30-to-180",
        "authority": {
            "handoff_commit": AUTHORITY,
            "claim_commit": CLAIM_COMMIT,
            "source_snapshot": SOURCE_SNAPSHOT,
            "retry_authority_commit": RETRY_AUTHORITY,
            "claim_owner": CLAIM_OWNER,
            "claim_session": CLAIM_SESSION,
        },
        "watchdog_barrier_release": release,
        "prior_attempt": {"path": str(prior_attempt_path), "sha256": prior_attempt_sha256},
        "source_bindings": source_rows,
        "source_and_git_observations_reused_from_attempt1": True,
        "git_commands": [] if prior_inner is None else prior_inner["git_commands"],
        "commands": commands,
        "export_attempts": export_invocations,
        "maximum_export_attempts": 2,
        "export_deleted_after_custody": export_deleted,
        "archive_audit": archive_result,
        "extra_owned_path_audit": extra_inventory_result,
        "preparation_custody": None if prior_inner is None else prior_inner["preparation_custody"],
        "checks": audit.checks,
        "failed_checks": failures,
        "malformed_controls": {
            "cases": controls,
            "cases_executed": 0,
            "cases_reused_from_attempt1": len(controls),
            "prior_attempt_sha256": prior_attempt_sha256,
            "maximum_cases": MAX_CONTROLS,
            "cumulative_cases_after_this_attempt": len(controls),
            "remaining_case_budget": MAX_CONTROLS - len(controls),
            "complete_suite_limit": 48,
        },
        "metrics": {
            "wall_seconds": time.monotonic() - wall_start,
            "process_cpu_seconds": time.process_time() - cpu_start,
            "process_peak_rss_bytes": own.ru_maxrss if sys.platform == "darwin" else own.ru_maxrss * 1024,
            "sampled_watchdog_threshold_bytes": WATCHDOG_THRESHOLD_BYTES,
            "hard_kernel_memory_limit_enforced": False,
            "maximum_workers": 1,
            "stream_buffer_bytes": BUFFER,
            "source_file_comparisons": len(source_rows),
            "source_observation_rows_reused": 34,
            "scientific_runs": 0,
            "container_creates_or_starts": 0,
            "image_code_executions": 0,
            "docker_image_inspect_invocations": docker_command_count(commands, "inspect"),
            "docker_image_export_invocations": docker_command_count(commands, "save"),
        },
        "error": error,
        "error_class": error_class,
        "limitations": [
            "This verifies exact local image/archive, wheel, installed-file, configuration and retained preparation custody only.",
            "No container was created or started and no image code or library import was executed by this audit.",
            "Retained import/version outputs are prior operational observations and were not reproduced by image execution.",
            "Coordinator-added image-binding annotations are source statements, not container-emitted measurements.",
            "Repository solver/generator exclusion applies only to copied /opt/reserve-inputs; SymPy contains mathematical solver and generator functions.",
            "The parent watchdog is sampled process observation and can overshoot or miss activity between samples; it is not a kernel-enforced hard 2 GiB limit.",
            "No scientific result, 8 GiB group guard, whole-runtime admission, fixture validity, or launch admission is established.",
        ],
    }
    write_reserved_json(inner_path, result)
    return 0 if result["status"] == "passed" else 1


class SampleUnavailable(RuntimeError):
    pass


class WorkerAlreadyTerminal(RuntimeError):
    pass


def monitor_command(argv: list[str], timeout: float = 1.0) -> dict:
    return durable_command_record(argv, timeout)


def process_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError as exc:
        raise SampleUnavailable(f"cannot observe owned pid {pid}: {exc}") from exc


def discover_owned_descendants(root_pid: int) -> tuple[list[int], list[dict]]:
    owned = {root_pid}
    queue = [root_pid]
    commands = []
    while queue:
        parent = queue.pop(0)
        row = monitor_command(["/usr/bin/pgrep", "-P", str(parent)])
        commands.append(row)
        if row["timed_out"] or row["exit_code"] not in (0, 1):
            raise SampleUnavailable(f"scoped descendant discovery failed for owned pid {parent}")
        if row["exit_code"] == 1:
            continue
        try:
            children = [int(line.strip()) for line in row["stdout"].splitlines() if line.strip()]
        except ValueError as exc:
            raise SampleUnavailable("malformed scoped pgrep output") from exc
        for child in children:
            if child <= 0:
                raise SampleUnavailable("malformed nonpositive child pid")
            if child not in owned:
                owned.add(child)
                queue.append(child)
        if len(owned) > 64:
            raise SampleUnavailable("owned descendant set exceeded 64 pids")
    return sorted(owned), commands


def sample_owned_tree(root_pid: int, previous_started: float | None) -> tuple[dict, list[dict]]:
    sample_started = time.monotonic()
    if not process_alive(root_pid):
        raise WorkerAlreadyTerminal("owned worker was terminal before sample")
    discovered, commands = discover_owned_descendants(root_pid)
    ps = monitor_command(["/bin/ps", "-o", "pid=,ppid=,rss=", "-p", ",".join(map(str, discovered))])
    commands.append(ps)
    if ps["timed_out"] or ps["exit_code"] != 0:
        if not process_alive(root_pid):
            raise WorkerAlreadyTerminal("owned worker became terminal during sample")
        raise SampleUnavailable("scoped ps RSS observation failed")
    rows = []
    for line in ps["stdout"].splitlines():
        fields = line.split()
        if len(fields) != 3:
            raise SampleUnavailable("malformed scoped ps RSS row")
        try:
            pid, ppid, rss_kib = map(int, fields)
        except ValueError as exc:
            raise SampleUnavailable("nonnumeric scoped ps RSS row") from exc
        if pid not in discovered or rss_kib < 0:
            raise SampleUnavailable("out-of-scope or negative scoped ps RSS row")
        rows.append({"pid": pid, "ppid": ppid, "rss_kib": rss_kib, "rss_bytes": rss_kib * 1024})
    sampled = {row["pid"] for row in rows}
    if root_pid not in sampled:
        if not process_alive(root_pid):
            raise WorkerAlreadyTerminal("owned worker became terminal before RSS row")
        raise SampleUnavailable("owned worker missing from scoped ps RSS output")
    vanished = sorted(set(discovered) - sampled)
    sample = {
        "started_at_UTC": utc(),
        "monotonic_started_seconds": sample_started,
        "interval_from_previous_sample_seconds": None if previous_started is None else sample_started - previous_started,
        "discovered_owned_pids": discovered,
        "sampled_rows": rows,
        "vanished_before_rss_observation": vanished,
        "aggregate_sampled_rss_bytes": sum(row["rss_bytes"] for row in rows),
        "ended_at_UTC": utc(),
        "wall_seconds": time.monotonic() - sample_started,
    }
    return sample, commands


def signal_owned_tree(root_pid: int, sig: int) -> dict:
    try:
        pids, commands = discover_owned_descendants(root_pid)
    except Exception as exc:
        pids, commands = [root_pid], []
        discovery_error = {"type": type(exc).__name__, "message": str(exc)}
    else:
        discovery_error = None
    outcomes = []
    for pid in reversed(pids):
        try:
            os.kill(pid, sig)
            outcomes.append({"pid": pid, "signal": sig, "sent": True})
        except ProcessLookupError:
            outcomes.append({"pid": pid, "signal": sig, "sent": False, "reason": "already_terminal"})
    return {"owned_pids": pids, "discovery_commands": commands, "discovery_error": discovery_error, "outcomes": outcomes}


def supervisor(attempt_number: int, setup_correction: str | None) -> int:
    if attempt_number not in (1, 2):
        raise ValueError("attempt number must be 1 or 2")
    if attempt_number == 2 and not setup_correction:
        raise ValueError("second watchdog setup attempt requires a concrete documented correction")
    scratch = Path(tempfile.mkdtemp(prefix=TASK.lower() + f"-attempt{attempt_number}-", dir="/private/tmp"))
    paths = {
        "reservation": scratch / "reservation.json",
        "inner": scratch / "inner.json",
        "export": scratch / "image-export.tar",
        "stdout": scratch / "worker.stdout",
        "stderr": scratch / "worker.stderr",
        "ready": scratch / "worker.ready.json",
        "release": scratch / "worker.release.json",
        "attempt_receipt": scratch / "attempt-receipt.json",
    }
    for path in paths.values():
        if path.exists():
            raise FileExistsError(f"exclusive attempt path already exists: {path}")
    argv = [
        sys.executable, "-B", str(Path(__file__).resolve()), "--worker",
        "--inner", str(paths["inner"]), "--export", str(paths["export"]),
        "--ready", str(paths["ready"]), "--release", str(paths["release"]),
    ]
    checker_bytes = Path(__file__).read_bytes()
    reservation = {
        "schema": "crypto.autoresearch.dependency_image_audit_reservation.v1",
        "task_id": TASK,
        "attempt_number": attempt_number,
        "setup_correction": setup_correction,
        "reserved_at_UTC": utc(),
        "cwd": str(Path.cwd()),
        "argv": argv,
        "command_sha256": sha_bytes(canonical(argv)),
        "checker": {
            "path": str(Path(__file__).resolve()),
            "bytes": len(checker_bytes),
            "sha256": sha_bytes(checker_bytes),
            "content_base64": base64.b64encode(checker_bytes).decode(),
        },
        "bound_helper": {"path": str(PREVIOUS_CHECKER), "sha256": sha_path(PREVIOUS_CHECKER)},
        "output_paths": {name: str(path) for name, path in paths.items()},
        "prelaunch_nonexistence_verified": True,
        "canonical_receipt_used_as_sink": False,
    }
    with paths["reservation"].open("x") as handle:
        json.dump(reservation, handle, indent=2)
        handle.write("\n")

    outer = {
        "argv": argv,
        "command_sha256": reservation["command_sha256"],
        "cwd": str(Path.cwd()),
        "started_at_UTC": utc(),
        "stdout_path": str(paths["stdout"]),
        "stderr_path": str(paths["stderr"]),
        "redirection_before_launch": True,
        "timeout_seconds": WORKER_TIMEOUT_SECONDS,
    }
    watchdog = {
        "kind": "parent_sampled_owned_process_rss",
        "threshold_bytes": WATCHDOG_THRESHOLD_BYTES,
        "sample_interval_target_seconds": WATCHDOG_INTERVAL_SECONDS,
        "maximum_sample_cadence_seconds": WATCHDOG_MAX_CADENCE_SECONDS,
        "hard_kernel_limit": False,
        "scope": "one owned checker child and descendants discovered only by scoped parent-pid queries",
        "samples": [],
        "sampling_commands": [],
        "readiness_barrier": None,
        "release": None,
        "peak_sampled_aggregate_rss_bytes": 0,
        "outcome": "setup_pending",
        "termination": [],
        "limitations": [
            "Sampling may overshoot the threshold or miss activity between observations.",
            "A vanished process receives no fabricated zero-RSS observation.",
        ],
    }
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    started = time.monotonic()
    descriptor_out = os.open(paths["stdout"], os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    descriptor_err = os.open(paths["stderr"], os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    proc = None
    setup_failure = None
    try:
        with os.fdopen(descriptor_out, "wb", buffering=BUFFER) as out, os.fdopen(descriptor_err, "wb", buffering=BUFFER) as err:
            proc = subprocess.Popen(argv, stdout=out, stderr=err)
            outer["pid"] = proc.pid
            barrier_deadline = time.monotonic() + 10
            while not paths["ready"].exists() and proc.poll() is None and time.monotonic() < barrier_deadline:
                time.sleep(0.01)
            if proc.poll() is not None:
                setup_failure = "worker_terminal_before_readiness_barrier"
                watchdog["outcome"] = "setup_failed"
            elif not paths["ready"].exists():
                setup_failure = "readiness_barrier_timeout"
                watchdog["outcome"] = "setup_failed"
            else:
                barrier = json.loads(paths["ready"].read_bytes())
                watchdog["readiness_barrier"] = barrier
                if barrier.get("worker_pid") != proc.pid or barrier.get("stage") != "before_controls_source_checks_and_any_docker_call":
                    raise SampleUnavailable("malformed worker readiness barrier")
                sample, sample_commands = sample_owned_tree(proc.pid, None)
                watchdog["samples"].append(sample)
                watchdog["sampling_commands"].extend(sample_commands)
                watchdog["peak_sampled_aggregate_rss_bytes"] = sample["aggregate_sampled_rss_bytes"]
                if sample["aggregate_sampled_rss_bytes"] > WATCHDOG_THRESHOLD_BYTES:
                    raise SampleUnavailable("readiness sample already exceeds sampled RSS threshold")
                release = {
                    "task_id": TASK,
                    "worker_pid": proc.pid,
                    "watchdog_ready": True,
                    "released_at_UTC": utc(),
                    "readiness_sample_index": 0,
                }
                with paths["release"].open("x") as handle:
                    json.dump(release, handle, sort_keys=True)
                    handle.write("\n")
                    handle.flush()
                    os.fsync(handle.fileno())
                watchdog["release"] = release
                watchdog["outcome"] = "monitoring"
                previous_started = sample["monotonic_started_seconds"]
                deadline = time.monotonic() + WORKER_TIMEOUT_SECONDS
                while proc.poll() is None:
                    if time.monotonic() >= deadline:
                        watchdog["outcome"] = "worker_timeout"
                        break
                    target = previous_started + WATCHDOG_INTERVAL_SECONDS
                    delay = target - time.monotonic()
                    if delay > 0:
                        time.sleep(delay)
                    if proc.poll() is not None:
                        break
                    try:
                        sample, sample_commands = sample_owned_tree(proc.pid, previous_started)
                    except WorkerAlreadyTerminal as exc:
                        watchdog["terminal_during_sample"] = str(exc)
                        break
                    watchdog["samples"].append(sample)
                    watchdog["sampling_commands"].extend(sample_commands)
                    previous_started = sample["monotonic_started_seconds"]
                    watchdog["peak_sampled_aggregate_rss_bytes"] = max(
                        watchdog["peak_sampled_aggregate_rss_bytes"], sample["aggregate_sampled_rss_bytes"]
                    )
                    interval = sample["interval_from_previous_sample_seconds"]
                    if interval is not None and interval > WATCHDOG_MAX_CADENCE_SECONDS:
                        watchdog["outcome"] = "cadence_breach"
                        break
                    if sample["aggregate_sampled_rss_bytes"] > WATCHDOG_THRESHOLD_BYTES:
                        watchdog["outcome"] = "sampled_rss_threshold_breach"
                        break
                if watchdog["outcome"] == "monitoring":
                    watchdog["outcome"] = "passed"
            if watchdog["outcome"] != "passed" and proc.poll() is None:
                watchdog["termination"].append(signal_owned_tree(proc.pid, signal.SIGTERM))
                try:
                    proc.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    watchdog["termination"].append(signal_owned_tree(proc.pid, signal.SIGKILL))
            if proc.poll() is None:
                proc.wait(timeout=5)
            outer.update(exit_code=proc.returncode, terminal_observed=True, timed_out=watchdog["outcome"] == "worker_timeout")
    except (SampleUnavailable, WorkerAlreadyTerminal) as exc:
        setup_failure = str(exc)
        watchdog["outcome"] = "setup_failed" if watchdog["release"] is None else "sampling_failed"
        if proc is not None and proc.poll() is None:
            watchdog["termination"].append(signal_owned_tree(proc.pid, signal.SIGTERM))
            try:
                proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                watchdog["termination"].append(signal_owned_tree(proc.pid, signal.SIGKILL))
                proc.wait(timeout=5)
        outer.update(exit_code=None if proc is None else proc.returncode, terminal_observed=proc is not None and proc.poll() is not None, timed_out=False)
    finally:
        after = resource.getrusage(resource.RUSAGE_CHILDREN)
        outer.update(
            ended_at_UTC=utc(),
            wall_seconds=time.monotonic() - started,
            parent_all_children_cpu_seconds=(after.ru_utime + after.ru_stime) - (before.ru_utime + before.ru_stime),
            stdout=paths["stdout"].read_text(errors="replace") if paths["stdout"].exists() else "",
            stderr=paths["stderr"].read_text(errors="replace") if paths["stderr"].exists() else "",
        )

    inner = json.loads(paths["inner"].read_bytes()) if paths["inner"].exists() else None
    export_deleted = not paths["export"].exists()
    status = "passed" if outer.get("exit_code") == 0 and watchdog["outcome"] == "passed" and inner and inner.get("status") == "passed" and export_deleted else "failed"
    attempt = {
        "schema": "crypto.autoresearch.dependency_image_portable_audit_attempt.v1",
        "task_id": TASK,
        "attempt_number": attempt_number,
        "setup_correction": setup_correction,
        "reservation": reservation,
        "outer": outer,
        "watchdog": watchdog,
        "inner": inner,
        "setup_failure": setup_failure,
        "counts": {
            "watchdog_setup_attempts": 1,
            "docker_image_inspect_invocations": 0 if inner is None else inner["metrics"]["docker_image_inspect_invocations"],
            "docker_image_export_invocations": 0 if inner is None else inner["metrics"]["docker_image_export_invocations"],
            "malformed_control_cases": 0 if inner is None else inner["malformed_controls"]["cases_executed"],
            "scientific_runs": 0,
            "operational_container_creates_or_starts": 0,
            "image_code_executions": 0,
        },
        "temporary_export_deleted": export_deleted,
        "status": status,
        "attempt_receipt_self_hash": None,
    }
    attempt["attempt_receipt_self_hash"] = sha_bytes(canonical(attempt))
    with paths["attempt_receipt"].open("x") as handle:
        json.dump(attempt, handle, indent=2, allow_nan=False)
        handle.write("\n")
    print(json.dumps({
        "status": status,
        "attempt_receipt": str(paths["attempt_receipt"]),
        "outer_exit_code": outer.get("exit_code"),
        "inner_status": None if inner is None else inner.get("status"),
        "watchdog_outcome": watchdog["outcome"],
        "export_invocations": attempt["counts"]["docker_image_export_invocations"],
        "control_cases": attempt["counts"]["malformed_control_cases"],
    }, sort_keys=True))
    return 0 if status == "passed" else 1


def _open_reserved_binary(path: Path):
    info = path.lstat()
    if not path.is_file() or info.st_size != 0 or info.st_nlink != 1:
        raise ValueError(f"invalid pre-reserved binary sink: {path}")
    flags = os.O_WRONLY | os.O_TRUNC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    return os.fdopen(os.open(path, flags), "wb", buffering=BUFFER)


def _terminate_and_reap_owned(proc: subprocess.Popen, reason: str) -> list[dict]:
    rows = []
    if proc.poll() is not None:
        return [{"reason": reason, "already_terminal": True, "exit_code": proc.returncode}]
    for sig, wait_seconds in ((signal.SIGTERM, 2), (signal.SIGKILL, 5)):
        row = {"reason": reason, "signal": sig, "owned_process_group": proc.pid}
        try:
            os.killpg(proc.pid, sig)
            row["sent"] = True
        except BaseException as exc:
            row.update(sent=False, cleanup_error={"type": type(exc).__name__, "message": str(exc), "repr": repr(exc)})
        rows.append(row)
        try:
            proc.wait(timeout=wait_seconds)
            row["reaped"] = True
            row["exit_code"] = proc.returncode
            break
        except subprocess.TimeoutExpired:
            row["reaped"] = False
        except BaseException as exc:
            row.update(reaped=False, reap_error={"type": type(exc).__name__, "message": str(exc), "repr": repr(exc)})
    return rows


def supervisor(
    attempt_number: int,
    setup_correction: str | None,
    attempt_dir: Path,
    nonce: str,
    prior_attempt_path: Path | None,
    prior_attempt_sha256: str | None,
) -> int:
    """Supervise the one pre-reserved worker and never create a container."""
    global CURRENT_JOURNAL_DIR
    if REPO is None:
        raise RuntimeError("explicit --repo is required")
    if attempt_number not in (1, 2):
        raise ValueError("attempt number must be 1 or 2")
    if attempt_number == 2 and not setup_correction:
        raise ValueError("second watchdog setup attempt requires a concrete documented correction")
    if attempt_number == 2 and (prior_attempt_path is None or prior_attempt_sha256 is None):
        raise ValueError("second attempt requires the exact prior-attempt path and SHA-256")
    if attempt_number == 1 and (prior_attempt_path is not None or prior_attempt_sha256 is not None):
        raise ValueError("first attempt cannot claim a prior-attempt basis")
    attempt_dir = attempt_dir.resolve(strict=True)
    expected_parent = Path("/private/tmp").resolve()
    if attempt_dir.parent.parent != expected_parent or not attempt_dir.name.startswith("attempt-"):
        raise ValueError("attempt directory is outside the unique owned /private/tmp reservation")
    paths = {
        "checker_reserved": attempt_dir / "checker-source.reserved",
        "command_reserved": attempt_dir / "command.reserved",
        "outer_stdout": attempt_dir / "outer.stdout.bin",
        "outer_stderr": attempt_dir / "outer.stderr.bin",
        "outer_response": attempt_dir / "outer.response.jsonl",
        "journal": attempt_dir / "supervisor.journal.jsonl",
        "readiness": attempt_dir / "watchdog-readiness.json",
        "inner": attempt_dir / "result.json",
        "ready": attempt_dir / "worker.ready.json",
        "release": attempt_dir / "worker.release.json",
        "export": attempt_dir / "image-export.tar",
        "attempt_receipt": attempt_dir / "attempt-receipt.json",
        "outer_raw": attempt_dir / "outer-terminal.raw.json",
        "outer_parsed": attempt_dir / "outer-terminal.parsed.json",
    }
    for name in ("checker_reserved", "command_reserved", "outer_stdout", "outer_stderr", "outer_response", "journal", "readiness", "inner"):
        info = paths[name].lstat()
        if not paths[name].is_file() or info.st_nlink != 1:
            raise ValueError(f"missing exclusive pre-reserved path: {paths[name]}")
    for name in ("ready", "release", "export", "attempt_receipt", "outer_raw", "outer_parsed"):
        if paths[name].exists():
            raise FileExistsError(f"unreserved result path already exists: {paths[name]}")
    checker_path = Path(__file__).resolve()
    checker_bytes = checker_path.read_bytes()
    if paths["checker_reserved"].read_bytes() != checker_bytes:
        raise ValueError("pre-reserved checker bytes do not match invoked checker")
    reserved_command = json.loads(paths["command_reserved"].read_bytes())
    expected_outer_argv = [
        sys.executable,
        "-B",
        str(checker_path),
        "--supervise",
        "--repo",
        str(REPO),
        "--attempt-dir",
        str(attempt_dir),
        "--attempt-number",
        str(attempt_number),
        "--nonce",
        nonce,
    ]
    if setup_correction is not None:
        expected_outer_argv.extend(["--setup-correction", setup_correction])
    if prior_attempt_path is not None:
        expected_outer_argv.extend(["--prior-attempt", str(prior_attempt_path), "--prior-attempt-sha256", prior_attempt_sha256])
    if (
        reserved_command.get("schema") != "crypto.autoresearch.runtime_bound_audit_prelaunch_reservation.v1"
        or reserved_command.get("outer_argv") != expected_outer_argv
        or reserved_command.get("cwd") != str(REPO)
        or reserved_command.get("nonce") != nonce
        or reserved_command.get("checker_sha256") != sha_bytes(checker_bytes)
        or reserved_command.get("attempt_number") != attempt_number
    ):
        raise ValueError("pre-reserved command/source binding does not match invocation")

    CURRENT_JOURNAL_DIR = attempt_dir / "monitor-commands"
    worker_argv = [
        sys.executable,
        "-B",
        str(checker_path),
        "--worker",
        "--repo",
        str(REPO),
        "--attempt-dir",
        str(attempt_dir),
        "--inner",
        str(paths["inner"]),
        "--export",
        str(paths["export"]),
        "--ready",
        str(paths["ready"]),
        "--release",
        str(paths["release"]),
        "--nonce",
        nonce,
    ]
    if prior_attempt_path is not None:
        worker_argv.extend(["--prior-attempt", str(prior_attempt_path), "--prior-attempt-sha256", prior_attempt_sha256])
    reservation = {
        "schema": "crypto.autoresearch.runtime_bound_audit_reservation.v1",
        "task_id": TASK,
        "attempt_number": attempt_number,
        "setup_correction": setup_correction,
        "reserved_before_supervisor_invocation": True,
        "external_reservation": reserved_command,
        "checker": {
            "invoked_path": str(checker_path),
            "reserved_path": str(paths["checker_reserved"]),
            "bytes": len(checker_bytes),
            "sha256": sha_bytes(checker_bytes),
            "content_base64": base64.b64encode(checker_bytes).decode("ascii"),
        },
        "worker_argv": worker_argv,
        "worker_command_sha256": sha_bytes(canonical(worker_argv)),
        "output_paths": {name: str(path) for name, path in paths.items()},
        "canonical_receipt_used_as_attempt_sink": False,
    }
    append_journal(paths["journal"], {"phase": "supervisor_started", "at_UTC": utc(), "reservation": reservation})
    outer = {
        "argv": worker_argv,
        "command_sha256": reservation["worker_command_sha256"],
        "cwd": str(REPO),
        "started_at_UTC": utc(),
        "stdout_path": str(paths["outer_stdout"]),
        "stderr_path": str(paths["outer_stderr"]),
        "redirection_before_launch": True,
        "timeout_seconds": WORKER_TIMEOUT_SECONDS,
    }
    watchdog = {
        "kind": "parent_sampled_owned_process_rss",
        "threshold_bytes": WATCHDOG_THRESHOLD_BYTES,
        "sample_interval_target_seconds": WATCHDOG_INTERVAL_SECONDS,
        "maximum_nominal_cadence_seconds": WATCHDOG_MAX_CADENCE_SECONDS,
        "hard_kernel_limit": False,
        "scope": "one exact owned checker process group; descendants discovered only by scoped pgrep -P and ps -p",
        "samples": [],
        "sampling_commands": [],
        "readiness_barrier": None,
        "readiness_record": None,
        "release": None,
        "peak_sampled_aggregate_rss_bytes": None,
        "maximum_observed_start_cadence_seconds": None,
        "cadence_overshoots": [],
        "outcome": "setup_pending",
        "termination": [],
        "limitations": [
            "Sampling may overshoot the threshold or miss activity between observations.",
            "Known-terminal children have unavailable final samples; no zero RSS is fabricated.",
        ],
    }
    proc = None
    primary_failure = None
    cleanup_failures = []
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    started = time.monotonic()
    try:
        with _open_reserved_binary(paths["outer_stdout"]) as out_handle, _open_reserved_binary(paths["outer_stderr"]) as err_handle:
            proc = subprocess.Popen(
                worker_argv,
                stdout=out_handle,
                stderr=err_handle,
                cwd=REPO,
                start_new_session=True,
            )
            outer["pid"] = proc.pid
            outer["process_group_id"] = proc.pid
            append_journal(paths["journal"], {"phase": "worker_launched", "at_UTC": utc(), "pid": proc.pid, "process_group_id": proc.pid})
            barrier_deadline = time.monotonic() + 10
            while not paths["ready"].exists() and proc.poll() is None and time.monotonic() < barrier_deadline:
                time.sleep(0.01)
            if proc.poll() is not None:
                raise WorkerAlreadyTerminal("worker terminal before readiness barrier")
            if not paths["ready"].exists():
                raise SampleUnavailable("readiness barrier timeout")
            barrier_raw = raw_file_record(paths["ready"], include_base64=True)
            barrier = json.loads(paths["ready"].read_bytes())
            watchdog["readiness_barrier"] = {"raw": barrier_raw, "parsed": barrier}
            expected_checker_sha = sha_bytes(checker_bytes)
            if not (
                barrier.get("task_id") == TASK
                and barrier.get("worker_pid") == proc.pid
                and barrier.get("parent_pid") == os.getpid()
                and barrier.get("nonce") == nonce
                and barrier.get("checker_sha256") == expected_checker_sha
                and barrier.get("repo") == str(REPO)
                and barrier.get("stage") == "before_controls_source_checks_and_any_docker_call"
                and (prior_attempt_path is None or (
                    barrier.get("prior_attempt_path") == str(prior_attempt_path)
                    and barrier.get("prior_attempt_sha256") == prior_attempt_sha256
                ))
            ):
                raise SampleUnavailable("nonce/hash/PID/repository startup barrier mismatch")
            previous_started = None
            for readiness_index in range(2):
                if readiness_index:
                    target = previous_started + WATCHDOG_INTERVAL_SECONDS
                    delay = target - time.monotonic()
                    if delay > 0:
                        time.sleep(delay)
                sample, rows = sample_owned_tree(proc.pid, previous_started)
                sample["phase"] = "pre_release_readiness"
                sample["readiness_index"] = readiness_index
                watchdog["samples"].append(sample)
                watchdog["sampling_commands"].extend(rows)
                previous_started = sample["monotonic_started_seconds"]
                aggregate = sample["aggregate_sampled_rss_bytes"]
                watchdog["peak_sampled_aggregate_rss_bytes"] = aggregate if watchdog["peak_sampled_aggregate_rss_bytes"] is None else max(watchdog["peak_sampled_aggregate_rss_bytes"], aggregate)
                if aggregate > WATCHDOG_THRESHOLD_BYTES:
                    raise SampleUnavailable("readiness aggregate sampled RSS exceeds threshold")
            readiness_cadence = watchdog["samples"][1]["interval_from_previous_sample_seconds"]
            readiness_record = {
                "schema": "crypto.autoresearch.runtime_bound_watchdog_readiness.v1",
                "task_id": TASK,
                "attempt_number": attempt_number,
                "recorded_at_UTC": utc(),
                "nonce": nonce,
                "checker_sha256": expected_checker_sha,
                "parent_pid": os.getpid(),
                "worker_pid": proc.pid,
                "barrier": watchdog["readiness_barrier"],
                "samples": list(watchdog["samples"]),
                "sampling_commands": list(watchdog["sampling_commands"]),
                "valid_aggregate_rss_samples": 2,
                "readiness_sample_start_cadence_seconds": readiness_cadence,
                "nominal_cadence_limit_seconds": WATCHDOG_MAX_CADENCE_SECONDS,
                "threshold_bytes": WATCHDOG_THRESHOLD_BYTES,
                "hard_kernel_limit": False,
                "outcome": "passed" if readiness_cadence <= WATCHDOG_MAX_CADENCE_SECONDS else "failed_cadence",
                "docker_actions_before_record": 0,
            }
            if readiness_record["outcome"] != "passed":
                write_reserved_json(paths["readiness"], readiness_record)
                raise SampleUnavailable("readiness sample cadence exceeded nominal maximum")
            write_reserved_json(paths["readiness"], readiness_record)
            readiness_hash = sha_path(paths["readiness"])
            watchdog["readiness_record"] = {"path": str(paths["readiness"]), "sha256": readiness_hash, "value": readiness_record}
            release = {
                "schema": "crypto.autoresearch.runtime_bound_watchdog_release.v1",
                "task_id": TASK,
                "parent_pid": os.getpid(),
                "worker_pid": proc.pid,
                "nonce": nonce,
                "checker_sha256": expected_checker_sha,
                "readiness_record_sha256": readiness_hash,
                "watchdog_ready": True,
                "released_at_UTC": utc(),
            }
            write_json_exclusive(paths["release"], release)
            watchdog["release"] = release
            watchdog["outcome"] = "monitoring"
            deadline = time.monotonic() + WORKER_TIMEOUT_SECONDS
            while proc.poll() is None:
                if time.monotonic() >= deadline:
                    watchdog["outcome"] = "worker_timeout"
                    break
                target = previous_started + WATCHDOG_INTERVAL_SECONDS
                delay = target - time.monotonic()
                if delay > 0:
                    time.sleep(delay)
                if proc.poll() is not None:
                    break
                try:
                    sample, rows = sample_owned_tree(proc.pid, previous_started)
                except WorkerAlreadyTerminal as exc:
                    watchdog["terminal_during_sample"] = str(exc)
                    break
                sample["phase"] = "post_release_monitoring"
                watchdog["samples"].append(sample)
                watchdog["sampling_commands"].extend(rows)
                previous_started = sample["monotonic_started_seconds"]
                aggregate = sample["aggregate_sampled_rss_bytes"]
                watchdog["peak_sampled_aggregate_rss_bytes"] = max(watchdog["peak_sampled_aggregate_rss_bytes"], aggregate)
                interval = sample["interval_from_previous_sample_seconds"]
                if interval is not None:
                    current_max = watchdog["maximum_observed_start_cadence_seconds"]
                    watchdog["maximum_observed_start_cadence_seconds"] = interval if current_max is None else max(current_max, interval)
                    if interval > WATCHDOG_MAX_CADENCE_SECONDS:
                        watchdog["cadence_overshoots"].append({"sample_index": len(watchdog["samples"]) - 1, "seconds": interval})
                if aggregate > WATCHDOG_THRESHOLD_BYTES:
                    watchdog["outcome"] = "sampled_rss_threshold_breach"
                    break
            if watchdog["outcome"] == "monitoring":
                watchdog["outcome"] = "passed"
            if watchdog["outcome"] != "passed" and proc.poll() is None:
                watchdog["termination"].extend(_terminate_and_reap_owned(proc, watchdog["outcome"]))
            if proc.poll() is None:
                try:
                    proc.wait(timeout=5)
                except BaseException as exc:
                    cleanup_failures.append({"phase": "final_reap", "type": type(exc).__name__, "message": str(exc), "repr": repr(exc)})
            outer.update(exit_code=proc.returncode, terminal_observed=proc.poll() is not None, timed_out=watchdog["outcome"] == "worker_timeout")
    except BaseException as exc:
        primary_failure = {"type": type(exc).__name__, "message": str(exc), "repr": repr(exc)}
        watchdog["outcome"] = "setup_failed" if watchdog["release"] is None else "monitoring_failed"
        if proc is not None and proc.poll() is None:
            watchdog["termination"].extend(_terminate_and_reap_owned(proc, "primary_failure"))
        outer.update(
            exit_code=None if proc is None else proc.returncode,
            terminal_observed=proc is not None and proc.poll() is not None,
            timed_out=False,
            launch_exception=primary_failure if proc is None else None,
        )
        if paths["readiness"].stat().st_size == 0:
            failed_readiness = {
                "schema": "crypto.autoresearch.runtime_bound_watchdog_readiness.v1",
                "task_id": TASK,
                "attempt_number": attempt_number,
                "recorded_at_UTC": utc(),
                "nonce": nonce,
                "checker_sha256": sha_bytes(checker_bytes),
                "parent_pid": os.getpid(),
                "worker_pid": None if proc is None else proc.pid,
                "barrier": watchdog["readiness_barrier"],
                "samples": list(watchdog["samples"]),
                "sampling_commands": list(watchdog["sampling_commands"]),
                "valid_aggregate_rss_samples": len(watchdog["samples"]),
                "outcome": "failed",
                "failure": primary_failure,
                "docker_actions_before_record": 0,
            }
            try:
                write_reserved_json(paths["readiness"], failed_readiness)
                watchdog["readiness_record"] = {"path": str(paths["readiness"]), "sha256": sha_path(paths["readiness"]), "value": failed_readiness}
            except BaseException as cleanup_exc:
                cleanup_failures.append({"phase": "persist_failed_readiness", "type": type(cleanup_exc).__name__, "message": str(cleanup_exc), "repr": repr(cleanup_exc)})
    finally:
        after = resource.getrusage(resource.RUSAGE_CHILDREN)
        outer.update(
            ended_at_UTC=utc(),
            wall_seconds=time.monotonic() - started,
            parent_all_children_cpu_seconds=(after.ru_utime + after.ru_stime) - (before.ru_utime + before.ru_stime),
        )
        try:
            raw_outer = {
                **outer,
                "stdout_raw": raw_file_record(paths["outer_stdout"], include_base64=True),
                "stderr_raw": raw_file_record(paths["outer_stderr"], include_base64=True),
            }
            write_json_exclusive(paths["outer_raw"], raw_outer)
            outer.update(
                stdout=paths["outer_stdout"].read_bytes().decode("utf-8", errors="replace"),
                stderr=paths["outer_stderr"].read_bytes().decode("utf-8", errors="replace"),
                stdout_decoding="utf-8-errors-replace-supplementary",
                stderr_decoding="utf-8-errors-replace-supplementary",
                raw_terminal_record={"path": str(paths["outer_raw"]), "sha256": sha_path(paths["outer_raw"])},
            )
            write_json_exclusive(paths["outer_parsed"], outer)
        except BaseException as cleanup_exc:
            cleanup_failures.append({"phase": "persist_outer_terminal", "type": type(cleanup_exc).__name__, "message": str(cleanup_exc), "repr": repr(cleanup_exc)})
        if paths["export"].exists():
            try:
                export_before_delete = raw_file_record(paths["export"], include_base64=False)
                paths["export"].unlink()
                export_cleanup = {"deleted": not paths["export"].exists(), "before_delete": export_before_delete}
            except BaseException as cleanup_exc:
                export_cleanup = {"deleted": False, "error": {"type": type(cleanup_exc).__name__, "message": str(cleanup_exc), "repr": repr(cleanup_exc)}}
                cleanup_failures.append({"phase": "delete_owned_export", **export_cleanup["error"]})
        else:
            export_cleanup = {"deleted": True, "before_delete": None}

    inner_raw = raw_file_record(paths["inner"], include_base64=True) if paths["inner"].stat().st_size else None
    inner = None
    inner_parse_error = None
    if inner_raw is not None:
        try:
            inner = json.loads(paths["inner"].read_bytes())
        except BaseException as exc:
            inner_parse_error = {"type": type(exc).__name__, "message": str(exc), "repr": repr(exc)}
    counts = {
        "watchdog_setup_attempts": 1,
        "docker_image_inspect_invocations": 0 if inner is None else inner["metrics"]["docker_image_inspect_invocations"],
        "docker_image_export_invocations": 0 if inner is None else inner["metrics"]["docker_image_export_invocations"],
        "malformed_control_cases": 0 if inner is None else inner["malformed_controls"]["cases_executed"],
        "scientific_runs": 0,
        "operational_container_creates_or_starts": 0,
        "image_code_executions": 0,
    }
    status = "passed" if (
        primary_failure is None
        and not cleanup_failures
        and outer.get("exit_code") == 0
        and watchdog["outcome"] == "passed"
        and inner is not None
        and inner.get("status") == "passed"
        and export_cleanup["deleted"]
    ) else "failed"
    attempt = {
        "schema": "crypto.autoresearch.dependency_image_runtime_bound_audit_attempt.v1",
        "task_id": TASK,
        "attempt_number": attempt_number,
        "setup_correction": setup_correction,
        "reservation": reservation,
        "outer": outer,
        "watchdog": watchdog,
        "inner_raw": inner_raw,
        "inner": inner,
        "inner_parse_error": inner_parse_error,
        "primary_failure": primary_failure,
        "cleanup_failures": cleanup_failures,
        "counts": counts,
        "temporary_export_cleanup": export_cleanup,
        "status": status,
        "attempt_receipt_self_hash": None,
    }
    attempt["attempt_receipt_self_hash"] = sha_bytes(canonical(attempt))
    write_json_exclusive(paths["attempt_receipt"], attempt)
    append_journal(paths["journal"], {"phase": "attempt_terminal", "at_UTC": utc(), "attempt_receipt_sha256": sha_path(paths["attempt_receipt"]), "status": status})
    print(json.dumps({
        "status": status,
        "attempt_receipt": str(paths["attempt_receipt"]),
        "attempt_receipt_sha256": sha_path(paths["attempt_receipt"]),
        "outer_exit_code": outer.get("exit_code"),
        "inner_status": None if inner is None else inner.get("status"),
        "joint_verdict": None if inner is None else inner.get("joint_verdict"),
        "watchdog_outcome": watchdog["outcome"],
        "valid_readiness_samples": 0 if watchdog["readiness_record"] is None else watchdog["readiness_record"]["value"].get("valid_aggregate_rss_samples"),
        "export_invocations": counts["docker_image_export_invocations"],
        "control_cases": counts["malformed_control_cases"],
    }, sort_keys=True))
    return 0 if status == "passed" else 1


def external_tool_record(outer_results: list[dict]) -> dict:
    if not outer_results:
        raise ValueError("at least one exact outer tool response is required")
    initial = outer_results[0]
    terminal = outer_results[-1]
    return {
        "all_tool_results_in_order": outer_results,
        "initial_tool_result": initial,
        "session_id": initial.get("session_id"),
        "session_id_available": "session_id" in initial,
        "polls": outer_results[1:],
        "terminal_result": terminal,
        "terminal_result_was_initial_result": len(outer_results) == 1,
    }


def prelaunch_failure_attempt(checker_path: Path, outer_results: list[dict]) -> dict:
    checker_bytes = checker_path.read_bytes()
    external = external_tool_record(outer_results)
    terminal = outer_results[-1]
    return {
        "schema": "crypto.autoresearch.dependency_image_portable_audit_prelaunch_failure.v1",
        "task_id": TASK,
        "attempt_number": 1,
        "setup_correction": None,
        "reservation": {
            "available": False,
            "reason": "module-level repository-root resolution failed before supervisor reservation",
            "reconstructed_command_text": "python3 -B coordination/experiment-reserve/BATCH-635652/reviews/TASK-20260909-3bc94a/checks.py --supervise --attempt-number 1",
            "reconstructed_command_is_exact_tool_input": True,
            "checker": {
                "preserved_path": str(checker_path),
                "bytes": len(checker_bytes),
                "sha256": sha_bytes(checker_bytes),
                "content_base64": base64.b64encode(checker_bytes).decode(),
            },
            "prelaunch_nonexistence_verified": None,
            "canonical_receipt_used_as_sink": False,
        },
        "outer": {
            "started_at_UTC": None,
            "ended_at_UTC": None,
            "wall_seconds": terminal.get("wall_time_seconds"),
            "exit_code": terminal.get("exit_code"),
            "terminal_observed": terminal.get("exit_code") is not None,
            "stdout": "",
            "stderr": terminal.get("output", ""),
            "timestamp_limitation": "The outer tool response did not expose absolute UTC timestamps; none are invented.",
        },
        "watchdog": {
            "kind": "parent_sampled_owned_process_rss",
            "outcome": "not_started",
            "readiness_barrier": None,
            "samples": [],
            "peak_sampled_aggregate_rss_bytes": None,
            "hard_kernel_limit": False,
        },
        "inner": None,
        "external_tool_invocation": external,
        "setup_failure": "FileNotFoundError from off-by-one repository-root calculation before supervisor startup",
        "counts": {
            "watchdog_setup_attempts": 1,
            "docker_image_inspect_invocations": 0,
            "docker_image_export_invocations": 0,
            "malformed_control_cases": 0,
            "scientific_runs": 0,
            "operational_container_creates_or_starts": 0,
            "image_code_executions": 0,
        },
        "temporary_export_deleted": True,
        "status": "failed",
        "procedure_deviation": "The first invocation failed before creating its required exclusive temporary attempt directory and prelaunch reservation; exact checker bytes and the complete outer response were preserved immediately afterward in an exclusive owned temporary directory.",
    }


def finalize(
    receipt_path: Path,
    attempt_paths: list[Path],
    outer_results_sets: list[list[dict]],
    outer_results_files: list[Path],
) -> int:
    if receipt_path.exists():
        raise FileExistsError(f"canonical receipt already exists: {receipt_path}")
    if not attempt_paths or len(attempt_paths) != len(outer_results_sets) or len(attempt_paths) != len(outer_results_files):
        raise ValueError("attempt and outer-response cardinalities differ")
    attempts = []
    outer_file_rows = []
    for attempt_path, outer_results, outer_results_file in zip(attempt_paths, outer_results_sets, outer_results_files):
        attempt = json.loads(attempt_path.read_bytes())
        attempt["external_tool_invocation"] = external_tool_record(outer_results)
        attempts.append(attempt)
        outer_file_rows.append({
            "path": str(outer_results_file),
            "sha256": sha_path(outer_results_file),
            "bytes": outer_results_file.stat().st_size,
            "content_base64": base64.b64encode(outer_results_file.read_bytes()).decode("ascii"),
        })
    terminal_attempt = attempts[-1]
    count_keys = set(terminal_attempt["counts"])
    counts = {key: sum(row["counts"][key] for row in attempts) for key in count_keys}
    final = {
        "schema": "crypto.autoresearch.dependency_image_runtime_bound_independent_audit_outer.v1",
        "task_id": TASK,
        "created_at_UTC": utc(),
        "canonical_receipt_created_after_all_attempts_terminated": True,
        "further_invocations_intended": False,
        "canonical_receipt_was_never_an_invocation_sink": True,
        "checks_source_sha256": sha_path(Path(__file__).resolve()),
        "outer_results_files": outer_file_rows,
        "attempts": attempts,
        "historical_inconclusive_audits": [
            {
                "task_id": "TASK-20260909-d033ac",
                "review_sha256": sha_path(PREVIOUS_REVIEW),
                "checks_sha256": sha_path(PREVIOUS_CHECKER),
                "receipt_sha256": sha_path(PREVIOUS_RECEIPT),
                "setup_attempts": 1,
                "setup_failure": "RLIMIT_AS ValueError: current limit exceeds maximum limit",
                "docker_image_inspect_invocations": 0,
                "docker_image_export_invocations": 0,
                "malformed_control_cases": 0,
                "verdict": "inconclusive",
            },
            {
                "task_id": "TASK-20260909-3bc94a",
                "review_sha256": sha_path(PORTABLE_REVIEW),
                "checks_sha256": sha_path(PORTABLE_CHECKER),
                "receipt_sha256": sha_path(PORTABLE_RECEIPT),
                "snapshot_sha256": sha_path(PORTABLE_SNAPSHOT),
                "setup_attempts": 2,
                "setup_failures": [
                    "module-level repository-root resolution before reservation",
                    "scoped descendant-discovery result bytes unavailable before exception",
                ],
                "docker_image_inspect_invocations": 0,
                "docker_image_export_invocations": 0,
                "malformed_control_cases": 0,
                "verdict": "inconclusive",
            },
        ],
        "historical_count_boundary": "One original supervised invocation and two portable setup attempts remain historical. This successor does not reset, consume, or rewrite those counts.",
        "cumulative_counts": counts,
        "remaining_authority": {
            "docker_image_exports": 2 - counts["docker_image_export_invocations"],
            "malformed_control_cases": 128 - counts["malformed_control_cases"],
            "watchdog_setup_attempts": 2 - counts["watchdog_setup_attempts"],
            "complete_48_case_suite_still_reserved": 128 - counts["malformed_control_cases"] >= 48,
        },
        "procedure_deviations": [],
        "status": terminal_attempt["status"],
        "joint_verdict": "inconclusive" if terminal_attempt["inner"] is None or terminal_attempt["watchdog"]["outcome"] != "passed" else terminal_attempt["inner"]["joint_verdict"],
        "receipt_self_hash": None,
    }
    final["receipt_self_hash"] = sha_bytes(canonical(final))
    write_json_exclusive(receipt_path, final)
    print(json.dumps({
        "status": final["status"], "joint_verdict": final["joint_verdict"],
        "receipt": str(receipt_path), "receipt_self_hash": final["receipt_self_hash"]
    }, sort_keys=True))
    return 0 if final["status"] == "passed" else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("--supervise", action="store_true")
    parser.add_argument("--finalize", action="store_true")
    parser.add_argument("--attempt-number", type=int, default=1)
    parser.add_argument("--setup-correction")
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--attempt-dir", type=Path)
    parser.add_argument("--nonce")
    parser.add_argument("--prior-attempt", type=Path)
    parser.add_argument("--prior-attempt-sha256")
    parser.add_argument("--inner", type=Path)
    parser.add_argument("--export", type=Path)
    parser.add_argument("--ready", type=Path)
    parser.add_argument("--release", type=Path)
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--attempt", type=Path, action="append")
    parser.add_argument("--outer-chunk-id")
    parser.add_argument("--outer-wall-seconds", type=float)
    parser.add_argument("--outer-exit-code", type=int)
    parser.add_argument("--outer-original-token-count", type=int)
    parser.add_argument("--outer-output-base64")
    parser.add_argument("--outer-results-base64")
    parser.add_argument("--outer-results-file", type=Path, action="append")
    parser.add_argument("--prelaunch-failure-checker", type=Path)
    parser.add_argument("--prelaunch-results-base64")
    args = parser.parse_args()
    configure_repo(args.repo)
    modes = sum((args.worker, args.supervise, args.finalize))
    if modes != 1:
        parser.error("choose exactly one of --worker, --supervise, --finalize")
    if args.worker:
        if None in (args.inner, args.export, args.ready, args.release, args.attempt_dir, args.nonce):
            parser.error("worker requires --inner,--export,--ready,--release,--attempt-dir and --nonce")
        if args.prior_attempt is not None or args.prior_attempt_sha256 is not None:
            if args.prior_attempt is None or args.prior_attempt_sha256 is None:
                parser.error("retry worker requires both --prior-attempt and --prior-attempt-sha256")
            return worker_retry(
                args.inner,
                args.export,
                args.ready,
                args.release,
                args.attempt_dir,
                args.nonce,
                args.prior_attempt,
                args.prior_attempt_sha256,
            )
        return worker(args.inner, args.export, args.ready, args.release, args.attempt_dir, args.nonce)
    if args.supervise:
        if args.attempt_dir is None or args.nonce is None:
            parser.error("supervisor requires --attempt-dir and --nonce")
        return supervisor(
            args.attempt_number,
            args.setup_correction,
            args.attempt_dir,
            args.nonce,
            args.prior_attempt,
            args.prior_attempt_sha256,
        )
    if args.receipt is None or not args.attempt:
        parser.error("finalize requires canonical receipt and attempt paths")
    if not args.outer_results_file:
        parser.error("finalize requires --outer-results-file for durable exact outer custody")
    outer_results_sets = [json.loads(path.read_bytes()) for path in args.outer_results_file]
    if not all(isinstance(rows, list) and all(isinstance(item, dict) for item in rows) for rows in outer_results_sets):
        raise ValueError("outer tool response payload must be a list of objects")
    return finalize(args.receipt, args.attempt, outer_results_sets, args.outer_results_file)


if __name__ == "__main__":
    raise SystemExit(main())
