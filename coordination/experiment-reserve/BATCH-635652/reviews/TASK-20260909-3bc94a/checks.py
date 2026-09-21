#!/usr/bin/env python3
"""Portable independent audit of one immutable local dependency image.

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


TASK = "TASK-20260909-3bc94a"
PRODUCER_TASK = "TASK-20260908-6e8eee"
IMAGE = "sha256:376f4a364f0b4cf1422b0f4ef1855b080e91ac858b47ef94dd8eee764d1eb3a7"
BASE = "sha256:c89921a0c7b42f27338ed8c279fb370e69e941c92460f91895d08304e844b0b4"
TAG = "crypto-autoresearcher/bsgs-deps:task-20260908-6e8eee"
SOCKET = "unix:///Users/adamburan/.docker/run/docker.sock"
DOCKER = ["/usr/local/bin/docker", "--host", SOCKET]
AUTHORITY = "1d8bb105fb3f951d71877ef9b07ae7b3b4f159c5"
CLAIM_COMMIT = "8164908fbe00db39bd078f9f3d010dce596c224d"
SOURCE_SNAPSHOT = "b65b8994463be8b9b04d82fce4b3a2bb01410bf2"
RETRY_AUTHORITY = "f40919ca2097099074d95180a8b16b430f31897a"
CLAIM_OWNER = "coordinator-reserve-admission-20260907"
CLAIM_SESSION = "01a07d92-d309-7620-9947-a358afc60883"
MAX_BYTES = 2 * 1024**3
BUFFER = 1024 * 1024
MAX_CONTROLS = 128
SUITE_SIZE = 48
WATCHDOG_INTERVAL_SECONDS = 0.02
WATCHDOG_MAX_CADENCE_SECONDS = 0.1
WATCHDOG_THRESHOLD_BYTES = 2 * 1024**3
WORKER_TIMEOUT_SECONDS = 900

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
HANDOFF = REPO / "ledger/handoffs/TASK-20260909-3bc94a.yaml"
CLAIM = REPO / "coordination/experiment-reserve/BATCH-635652/claims/TASK-20260909-3bc94a.1.claim.json"
PLAN = REPO / "coordination/experiment-reserve/BATCH-635652/review-plan-TASK-20260909-3bc94a.yaml"
METADATA = REPO / "coordination/experiment-reserve/BATCH-635652/runtime-bindings/DEC-20260908-f39556/dependencies.json"
APPROVAL = REPO / "ledger/decisions/DEC-20260908-f39556.yaml"
BINDING = REPO / "coordination/experiment-reserve/BATCH-635652/runtime/TASK-20260908-6e8eee/image-binding.json"
PREPARATION = REPO / "coordination/experiment-reserve/BATCH-635652/runtime/TASK-20260908-6e8eee/preparation-receipt.json"
ATTEMPT1 = REPO / "coordination/experiment-reserve/BATCH-635652/runtime-bindings/DEC-20260908-d687ab/attempt1.json"
SNAPSHOT = REPO / "coordination/experiment-reserve/BATCH-635652/archives/TASK-20260908-67e682/snapshot.json"
PREVIOUS_CHECKER = REPO / "coordination/experiment-reserve/BATCH-635652/reviews/TASK-20260909-d033ac/checks.py"
PREVIOUS_REVIEW = REPO / "coordination/experiment-reserve/BATCH-635652/reviews/TASK-20260909-d033ac/review.yaml"
PREVIOUS_RECEIPT = REPO / "coordination/experiment-reserve/BATCH-635652/reviews/TASK-20260909-d033ac/check-receipt.json"


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


def load_bound_checker():
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


def worker(inner_path: Path, export_path: Path, ready_path: Path, release_path: Path) -> int:
    global BASE_CHECKER
    started_utc = utc()
    wall_start = time.monotonic()
    cpu_start = time.process_time()
    ready = {
        "schema": "crypto.autoresearch.sampled_watchdog_barrier.v1",
        "task_id": TASK,
        "worker_pid": os.getpid(),
        "parent_pid": os.getppid(),
        "ready_at_UTC": utc(),
        "stage": "before_controls_source_checks_and_any_docker_call",
        "checker_sha256": sha_path(Path(__file__).resolve()),
    }
    with ready_path.open("x") as handle:
        json.dump(ready, handle, sort_keys=True)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    release_deadline = time.monotonic() + 30
    while not release_path.exists():
        if time.monotonic() >= release_deadline:
            raise TimeoutError("watchdog release barrier was not satisfied")
        time.sleep(0.01)
    release = json.loads(release_path.read_bytes())
    if release.get("worker_pid") != os.getpid() or release.get("watchdog_ready") is not True:
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
                "passed": actual == entry["sha256"],
            })
        audit.check("all_28_source_bindings", len(source_rows) == 28 and all(row["passed"] for row in source_rows))
        audit.check("inputs_equal_bindings", handoff_doc["inputs"] == [entry["path"] for entry in handoff_doc["source_bindings"]])

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
            ["git", "diff", "--quiet", AUTHORITY, "--", *handoff_doc["inputs"]],
            ["git", "diff", "--quiet", CLAIM_COMMIT, "--", str(CLAIM.relative_to(REPO))],
            ["git", "diff", "--quiet", SOURCE_SNAPSHOT, "--", *snapshot["source_path_sha256"].keys()],
        ]
        for index, argv in enumerate(git_commands, 1):
            row = BASE_CHECKER.command_record(argv, 30)
            git_rows.append(row)
            audit.check(f"git_binding_{index}", BASE_CHECKER.command_ok(row), {
                "argv": argv, "exit_code": row.get("exit_code"), "stderr": row.get("stderr")
            })
        audit.check("snapshot_source_hashes", all(sha_path(REPO / path) == digest for path, digest in snapshot["source_path_sha256"].items()))
        audit.check("exact_package_metadata_matches_approval", exact_package_protocol(metadata, approval))
        audit.check("metadata_retrieval_no_tls_bypass", "failed local issuer verification and was not weakened" in metadata["retrieval"] and metadata["provenance"] == "retrieved")

        audit.check("previous_failure_preserved", previous_review["verdict"] == "incomplete" and previous_review["failed_attempt"]["docker_inspect_invocations"] == 0 and previous_review["failed_attempt"]["docker_export_invocations"] == 0 and previous_review["failed_attempt"]["malformed_control_cases"] == 0 and previous_receipt["outer"]["exit_code"] == 1 and previous_receipt["inner"] is None and "current limit exceeds maximum limit" in previous_receipt["outer"]["stderr"])

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
        "schema": "crypto.autoresearch.dependency_image_portable_independent_audit.v1",
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
    with inner_path.open("x") as handle:
        json.dump(result, handle, indent=2, allow_nan=False)
        handle.write("\n")
    return 0 if result["status"] == "passed" else 1


class SampleUnavailable(RuntimeError):
    pass


class WorkerAlreadyTerminal(RuntimeError):
    pass


def monitor_command(argv: list[str], timeout: float = 1.0) -> dict:
    row = {"argv": argv, "started_at_UTC": utc(), "timeout_seconds": timeout}
    started = time.monotonic()
    try:
        completed = subprocess.run(argv, capture_output=True, text=True, timeout=timeout)
        row.update(exit_code=completed.returncode, stdout=completed.stdout, stderr=completed.stderr, timed_out=False)
    except subprocess.TimeoutExpired as exc:
        row.update(exit_code=None, stdout=exc.stdout or "", stderr=exc.stderr or "", timed_out=True)
    row.update(ended_at_UTC=utc(), wall_seconds=time.monotonic() - started, terminal_observed=True)
    return row


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
    attempt_path: Path,
    outer_results: list[dict],
    prelaunch_checker_path: Path | None,
    prelaunch_outer_results: list[dict] | None,
) -> int:
    if receipt_path.exists():
        raise FileExistsError(f"canonical receipt already exists: {receipt_path}")
    attempt = json.loads(attempt_path.read_bytes())
    attempt["external_tool_invocation"] = external_tool_record(outer_results)
    attempts = []
    if prelaunch_checker_path is not None or prelaunch_outer_results is not None:
        if prelaunch_checker_path is None or prelaunch_outer_results is None:
            raise ValueError("prelaunch failure requires both checker bytes and outer responses")
        attempts.append(prelaunch_failure_attempt(prelaunch_checker_path, prelaunch_outer_results))
    attempts.append(attempt)
    count_keys = set(attempt["counts"])
    counts = {key: sum(row["counts"][key] for row in attempts) for key in count_keys}
    final = {
        "schema": "crypto.autoresearch.dependency_image_portable_independent_audit_outer.v1",
        "task_id": TASK,
        "created_at_UTC": utc(),
        "canonical_receipt_created_after_all_attempts_terminated": True,
        "further_invocations_intended": False,
        "canonical_receipt_was_never_an_invocation_sink": True,
        "attempts": attempts,
        "previous_inconclusive_audit": {
            "task_id": "TASK-20260909-d033ac",
            "review_sha256": sha_path(PREVIOUS_REVIEW),
            "checks_sha256": sha_path(PREVIOUS_CHECKER),
            "receipt_sha256": sha_path(PREVIOUS_RECEIPT),
            "setup_failure": "RLIMIT_AS ValueError: current limit exceeds maximum limit",
            "docker_image_inspect_invocations": 0,
            "docker_image_export_invocations": 0,
            "malformed_control_cases": 0,
            "verdict": "inconclusive",
        },
        "cumulative_counts": counts,
        "remaining_authority": {
            "docker_image_exports": 2 - counts["docker_image_export_invocations"],
            "malformed_control_cases": 128 - counts["malformed_control_cases"],
            "watchdog_setup_attempts": 2 - counts["watchdog_setup_attempts"],
            "complete_48_case_suite_still_reserved": 128 - counts["malformed_control_cases"] >= 48,
        },
        "procedure_deviations": [row["procedure_deviation"] for row in attempts if row.get("procedure_deviation")],
        "status": attempt["status"],
        "joint_verdict": "inconclusive" if attempt["inner"] is None or attempt["watchdog"]["outcome"] != "passed" else attempt["inner"]["joint_verdict"],
        "receipt_self_hash": None,
    }
    final["receipt_self_hash"] = sha_bytes(canonical(final))
    with receipt_path.open("x") as handle:
        json.dump(final, handle, indent=2, allow_nan=False)
        handle.write("\n")
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
    parser.add_argument("--inner", type=Path)
    parser.add_argument("--export", type=Path)
    parser.add_argument("--ready", type=Path)
    parser.add_argument("--release", type=Path)
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--attempt", type=Path)
    parser.add_argument("--outer-chunk-id")
    parser.add_argument("--outer-wall-seconds", type=float)
    parser.add_argument("--outer-exit-code", type=int)
    parser.add_argument("--outer-original-token-count", type=int)
    parser.add_argument("--outer-output-base64")
    parser.add_argument("--outer-results-base64")
    parser.add_argument("--prelaunch-failure-checker", type=Path)
    parser.add_argument("--prelaunch-results-base64")
    args = parser.parse_args()
    modes = sum((args.worker, args.supervise, args.finalize))
    if modes != 1:
        parser.error("choose exactly one of --worker, --supervise, --finalize")
    if args.worker:
        if None in (args.inner, args.export, args.ready, args.release):
            parser.error("worker requires --inner, --export, --ready and --release")
        return worker(args.inner, args.export, args.ready, args.release)
    if args.supervise:
        return supervisor(args.attempt_number, args.setup_correction)
    if None in (args.receipt, args.attempt):
        parser.error("finalize requires canonical receipt and attempt paths")
    if args.outer_results_base64:
        outer_results = json.loads(base64.b64decode(args.outer_results_base64))
    else:
        if None in (args.outer_chunk_id, args.outer_wall_seconds, args.outer_exit_code, args.outer_original_token_count, args.outer_output_base64):
            parser.error("finalize requires exact outer response fields")
        outer_results = [{
            "chunk_id": args.outer_chunk_id,
            "wall_time_seconds": args.outer_wall_seconds,
            "exit_code": args.outer_exit_code,
            "original_token_count": args.outer_original_token_count,
            "output": base64.b64decode(args.outer_output_base64).decode(),
        }]
    if not isinstance(outer_results, list) or not all(isinstance(item, dict) for item in outer_results):
        raise ValueError("outer tool response payload must be a list of objects")
    prelaunch_results = None
    if args.prelaunch_results_base64:
        prelaunch_results = json.loads(base64.b64decode(args.prelaunch_results_base64))
        if not isinstance(prelaunch_results, list) or not all(isinstance(item, dict) for item in prelaunch_results):
            raise ValueError("prelaunch outer response payload must be a list of objects")
    return finalize(args.receipt, args.attempt, outer_results, args.prelaunch_failure_checker, prelaunch_results)


if __name__ == "__main__":
    raise SystemExit(main())
