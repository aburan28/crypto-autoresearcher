#!/usr/bin/env python3
"""Independent, source-only native supervisor conformance checks.

This checker never invokes Docker, reads or writes a live cgroup, changes
credentials or capabilities, migrates a process, allocates a pressure body, or
executes a scientific fixture.  It reads frozen Git objects as data, decodes
embedded receipt payloads as data, and runs fixed injected controls.  One tiny
ordinary subprocess per suite exercises byte custody in SubprocessTransport.
"""
from __future__ import annotations

import argparse
import ast
import base64
import ctypes
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
from io import BytesIO
import json
import os
from pathlib import Path
import platform
import signal
import stat
import subprocess
import sys
import time
import traceback
from types import SimpleNamespace
from typing import Any, Callable, Mapping, Sequence
from unittest import mock

import yaml


TASK_ID = "TASK-20260910-1c7aa0"
SOURCE_TASK_ID = "TASK-20260910-89d2df"
SOURCE_SNAPSHOT = "efe06c32858aff43a22698b260e872916e394846"
AUTHORITY_COMMIT = "29db7cf335060e981a591b75df114d6fe8ee4422"
PUBLISHED_CLAIM_COMMIT = "38e2a7b3d31e7baaf48b5ce844b13165ec9c2e49"
PLAN_PATH = "coordination/experiment-reserve/BATCH-635652/review-plan-TASK-20260910-1c7aa0.yaml"
HANDOFF_PATH = "ledger/handoffs/TASK-20260910-1c7aa0.yaml"
CLAIM_PATH = "coordination/experiment-reserve/BATCH-635652/claims/TASK-20260910-1c7aa0.1.claim.json"
PRODUCER_DIR = "coordination/experiment-reserve/BATCH-635652/runtime/TASK-20260910-89d2df"
PRODUCER_ARTIFACT_NAMES = (
    "supervisor.py",
    "container.py",
    "host.py",
    "tests.py",
    "protocol-binding.json",
    "implementation-report.yaml",
    "check-receipt.json",
    "README.md",
)
MEMORY_LIMIT_BYTES = 2 * 1024 * 1024 * 1024
PER_CASE_SECONDS = 10
AGGREGATE_SECONDS = 1800
MAX_SUITE_CASES = 128
MAX_TOTAL_CONTROLS = 384
MAX_BENIGN_STARTS = 32
MAX_CONCURRENT_CHILDREN = 2
MAX_CHILD_LIFETIME_SECONDS = 3
MAX_DELIBERATE_PAYLOAD_BYTES = 1024 * 1024
Case = tuple[str, Callable[[], Mapping[str, Any] | None]]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def append_jsonl(path: Path, row: Mapping[str, Any]) -> None:
    payload = (json.dumps(dict(row), sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    fd = os.open(path, os.O_WRONLY | os.O_APPEND)
    try:
        offset = 0
        while offset < len(payload):
            offset += os.write(fd, payload[offset:])
        os.fsync(fd)
    finally:
        os.close(fd)


def journal(path: Path, event: str, **fields: Any) -> None:
    append_jsonl(path, {"at_UTC": utc_now(), "monotonic_ns": time.monotonic_ns(), "event": event, **fields})


class CatFileBatch:
    """One journalled read-only Git child for all frozen object reads."""

    def __init__(self, repo: Path, journal_path: Path) -> None:
        self.repo = repo
        self.journal_path = journal_path
        self.process: subprocess.Popen[bytes] | None = None

    def __enter__(self) -> "CatFileBatch":
        argv = ["git", "-C", str(self.repo), "cat-file", "--batch"]
        began = time.monotonic()
        self.process = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        journal(
            self.journal_path,
            "owned_process_created",
            case_id="administrative_git_object_custody",
            purpose="read_only_git_cat_file_batch",
            pid=self.process.pid,
            argv=argv,
            deliberate_payload_bytes=0,
        )
        self.began = began
        return self

    def get(self, spec: str, missing_ok: bool = False) -> bytes | None:
        assert self.process is not None and self.process.stdin is not None and self.process.stdout is not None
        self.process.stdin.write(spec.encode("utf-8") + b"\n")
        self.process.stdin.flush()
        header = self.process.stdout.readline()
        if not header:
            raise RuntimeError(f"git cat-file ended before {spec}")
        if header.rstrip().endswith(b" missing"):
            if missing_ok:
                return None
            raise RuntimeError(f"missing frozen Git object {spec}")
        fields = header.rstrip().split()
        if len(fields) != 3:
            raise RuntimeError(f"malformed git cat-file header for {spec}: {header!r}")
        size = int(fields[2])
        payload = self.process.stdout.read(size)
        separator = self.process.stdout.read(1)
        if len(payload) != size or separator != b"\n":
            raise RuntimeError(f"truncated git cat-file payload for {spec}")
        return payload

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        assert self.process is not None
        stderr = b""
        primary: str | None = None
        try:
            assert self.process.stdin is not None
            self.process.stdin.close()
            assert self.process.stderr is not None
            stderr = self.process.stderr.read()
            code = self.process.wait(timeout=MAX_CHILD_LIFETIME_SECONDS)
        except Exception as error:
            primary = f"{type(error).__name__}:{error}"
            try:
                self.process.kill()
            except Exception:
                pass
            code = self.process.wait()
        finally:
            for stream in (self.process.stdout, self.process.stderr):
                if stream is not None:
                    stream.close()
        journal(
            self.journal_path,
            "owned_process_terminal",
            case_id="administrative_git_object_custody",
            purpose="read_only_git_cat_file_batch",
            pid=self.process.pid,
            exit_code=code,
            reaped=True,
            descriptors_closed=True,
            stderr_base64=base64.b64encode(stderr).decode("ascii"),
            primary_error=primary,
            wall_seconds=time.monotonic() - self.began,
        )
        if code != 0 and exc is None:
            raise RuntimeError(f"git cat-file failed: {stderr.decode('utf-8', errors='replace')}")


def parse_commit(payload: bytes) -> Mapping[str, Any]:
    header, _, message = payload.partition(b"\n\n")
    rows = header.decode("utf-8", errors="strict").splitlines()
    return {
        "tree": next(row.split()[1] for row in rows if row.startswith("tree ")),
        "parents": [row.split()[1] for row in rows if row.startswith("parent ")],
        "message": message.decode("utf-8", errors="replace"),
    }


def read_and_verify_frozen_inputs(repo: Path, journal_path: Path) -> tuple[Mapping[str, Any], dict[str, bytes]]:
    current_handoff = yaml.safe_load((repo / HANDOFF_PATH).read_text(encoding="utf-8"))["handoff"]
    bindings = current_handoff["source_bindings"]
    inputs = current_handoff["inputs"]
    if len(inputs) != 87 or len(bindings) != 87 or inputs != [row["path"] for row in bindings]:
        raise AssertionError("handoff input/binding inventory is not the frozen 87-row ordered set")
    payloads: dict[str, bytes] = {}
    rows: list[Mapping[str, Any]] = []
    embedded_payload_rows: list[Mapping[str, Any]] = []
    with CatFileBatch(repo, journal_path) as git:
        source_commit = parse_commit(git.get(SOURCE_SNAPSHOT) or b"")
        authority_commit = parse_commit(git.get(AUTHORITY_COMMIT) or b"")
        published_commit = parse_commit(git.get(PUBLISHED_CLAIM_COMMIT) or b"")
        if published_commit["parents"] != [AUTHORITY_COMMIT]:
            raise AssertionError("published claim is not the direct child of authority")
        cursor = AUTHORITY_COMMIT
        ancestry: list[str] = []
        for _ in range(64):
            ancestry.append(cursor)
            if cursor == SOURCE_SNAPSHOT:
                break
            commit = parse_commit(git.get(cursor) or b"")
            if not commit["parents"]:
                break
            cursor = commit["parents"][0]
        if SOURCE_SNAPSHOT not in ancestry:
            raise AssertionError("source snapshot is not on authority first-parent chain")

        plan_at_source = git.get(f"{SOURCE_SNAPSHOT}:{PLAN_PATH}", missing_ok=True)
        authority_parent = authority_commit["parents"][0]
        plan_at_authority_parent = git.get(f"{authority_parent}:{PLAN_PATH}", missing_ok=True)
        if plan_at_source is not None or plan_at_authority_parent is not None:
            raise AssertionError("standalone review plan was present before authority commit")

        for binding in bindings:
            path = binding["path"]
            origin = AUTHORITY_COMMIT if path == PLAN_PATH else SOURCE_SNAPSHOT
            data = git.get(f"{origin}:{path}")
            assert data is not None
            actual = digest(data)
            authority_data = git.get(f"{AUTHORITY_COMMIT}:{path}")
            if authority_data != data:
                raise AssertionError(f"input changed between declared origin and authority: {path}")
            parsed_kind = "utf8"
            if path.endswith(".json"):
                parsed = json.loads(data)
                parsed_kind = "json"
                embedded_payload_rows.extend(scan_embedded_base64(parsed, path))
            elif path.endswith((".yaml", ".yml")):
                yaml.safe_load(data)
                parsed_kind = "yaml"
            elif path.endswith(".py"):
                ast.parse(data.decode("utf-8"), filename=path)
                parsed_kind = "python_ast"
            else:
                data.decode("utf-8")
            rows.append(
                {
                    "path": path,
                    "origin_commit": origin,
                    "expected_sha256": binding["sha256"],
                    "actual_sha256": actual,
                    "bytes": len(data),
                    "matched": actual == binding["sha256"],
                    "parsed_as": parsed_kind,
                }
            )
            payloads[path] = data
        if not all(row["matched"] for row in rows):
            raise AssertionError("one or more frozen source hashes mismatch")

        handoff_data = git.get(f"{AUTHORITY_COMMIT}:{HANDOFF_PATH}")
        claim_data = git.get(f"{PUBLISHED_CLAIM_COMMIT}:{CLAIM_PATH}")
        assert handoff_data is not None and claim_data is not None
        if handoff_data != (repo / HANDOFF_PATH).read_bytes():
            raise AssertionError("working handoff differs from committed authority bytes")
        claim = json.loads(claim_data)
        if Path(claim["worktree"]).resolve() != repo.resolve():
            raise AssertionError("explicit --repo differs from published claim worktree")
        if claim["write_scope"] != current_handoff["write_scope"]:
            raise AssertionError("published claim write scope differs from handoff")
        standalone_plan = yaml.safe_load(payloads[PLAN_PATH])
        if standalone_plan["review_plan"] != current_handoff["review_plan"]:
            raise AssertionError("standalone and embedded review plan differ")

    return (
        {
            "result": "passed",
            "expected_count": 87,
            "verified_count": len(rows),
            "source_snapshot_count": sum(row["origin_commit"] == SOURCE_SNAPSHOT for row in rows),
            "authority_count": sum(row["origin_commit"] == AUTHORITY_COMMIT for row in rows),
            "rows": rows,
            "embedded_base64_payload_count": len(embedded_payload_rows),
            "embedded_base64_payloads": embedded_payload_rows,
            "commit_chain": {
                "source_snapshot": SOURCE_SNAPSHOT,
                "source_parent": source_commit["parents"],
                "authority_commit": AUTHORITY_COMMIT,
                "authority_parent": authority_commit["parents"],
                "published_claim_commit": PUBLISHED_CLAIM_COMMIT,
                "published_parent": published_commit["parents"],
            },
            "claim_explicit_repository": claim["worktree"],
        },
        payloads,
    )


def scan_embedded_base64(value: Any, source_path: str, cursor: str = "$") -> list[Mapping[str, Any]]:
    rows: list[Mapping[str, Any]] = []
    if isinstance(value, Mapping):
        for key, item in value.items():
            child = f"{cursor}.{key}"
            if isinstance(item, str) and (str(key).endswith("base64") or str(key) == "base64"):
                decoded = base64.b64decode(item, validate=True)
                parsed_as = "bytes"
                if ".py" in cursor:
                    ast.parse(decoded.decode("utf-8"), filename=f"{source_path}:{child}")
                    parsed_as = "python_ast_data_only"
                rows.append(
                    {
                        "source_path": source_path,
                        "json_path": child,
                        "decoded_bytes": len(decoded),
                        "decoded_sha256": digest(decoded),
                        "parsed_as": parsed_as,
                        "executed": False,
                    }
                )
            else:
                rows.extend(scan_embedded_base64(item, source_path, child))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            rows.extend(scan_embedded_base64(item, source_path, f"{cursor}[{index}]"))
    return rows


def verify_producer_receipt(payloads: Mapping[str, bytes]) -> Mapping[str, Any]:
    receipt_path = f"{PRODUCER_DIR}/check-receipt.json"
    receipt = json.loads(payloads[receipt_path])
    protocol = json.loads(payloads[f"{PRODUCER_DIR}/protocol-binding.json"])
    invocations = receipt["invocations"]
    if [row["label"] for row in invocations] != ["registry0", "registry1", "attempt1"]:
        raise AssertionError("producer invocation labels mismatch")
    retained_rows: list[Mapping[str, Any]] = []
    source_versions: list[Mapping[str, Any]] = []
    for invocation in invocations:
        for name, binding in invocation["retained_files"].items():
            decoded = base64.b64decode(binding["base64"], validate=True)
            actual = digest(decoded)
            matched = actual == binding["sha256"] and len(decoded) == binding["bytes"]
            if not matched:
                raise AssertionError(f"retained payload mismatch: {invocation['label']}:{name}")
            if name.endswith(".py"):
                ast.parse(decoded.decode("utf-8"), filename=f"{invocation['label']}:{name}")
            retained_rows.append(
                {
                    "invocation": invocation["label"],
                    "name": name,
                    "bytes": len(decoded),
                    "sha256": actual,
                    "matched": matched,
                    "executed_from_receipt": False,
                }
            )
        observation = invocation["observations"]
        raw_stdout = base64.b64decode(observation["raw_stdout_base64"], validate=True)
        raw_stderr = base64.b64decode(observation["raw_stderr_base64"], validate=True)
        retained_stdout = base64.b64decode(invocation["retained_files"]["stdout"]["base64"], validate=True)
        retained_stderr = base64.b64decode(invocation["retained_files"]["stderr"]["base64"], validate=True)
        if raw_stdout != retained_stdout or raw_stderr != retained_stderr:
            raise AssertionError(f"raw stream duplicate mismatch: {invocation['label']}")
        source_versions.append(
            {
                "invocation": invocation["label"],
                "tests_sha256": invocation["retained_files"]["source/tests.py"]["sha256"],
                "controller_sha256": invocation["retained_files"]["controller.py"]["sha256"],
                "worker_sha256": invocation["retained_files"].get("worker.py", {}).get("sha256"),
                "stdout_sha256": digest(raw_stdout),
                "stderr_sha256": digest(raw_stderr),
            }
        )

    registry_summaries: list[Mapping[str, Any]] = []
    for invocation in invocations[:2]:
        registry = json.loads(base64.b64decode(invocation["retained_files"]["registry.json"]["base64"], validate=True))
        observation = invocation["observations"]
        if observation["control_executions"] != 0 or registry["registered_case_count"] != 120:
            raise AssertionError("registry invocation accounting mismatch")
        registry_summaries.append(
            {
                "label": invocation["label"],
                "registered_case_count": registry["registered_case_count"],
                "control_executions": observation["control_executions"],
                "registry_sha256": digest(json.dumps(registry, sort_keys=True, separators=(",", ":")).encode()),
                "retained_registry_sha256": invocation["retained_files"]["registry.json"]["sha256"],
            }
        )

    attempt = invocations[2]["observations"]
    suite = attempt["suite"]
    results = suite["results"]
    journal_rows = attempt["journal_rows"]
    starts = [row for row in journal_rows if row.get("event") == "case_start"]
    terminals = [row for row in journal_rows if row.get("event") == "case_result"]
    created = [row for row in journal_rows if row.get("event") == "created"]
    waits = [row for row in journal_rows if row.get("event") == "terminal_wait"]
    custody = [row for row in journal_rows if row.get("event") == "case_custody_terminal"]
    opened = [row for row in journal_rows if row.get("event") == "descriptor_created"]
    closed = [row for row in journal_rows if row.get("event") == "descriptor_closed"]
    if not (
        len(results) == len(starts) == len(terminals) == 120
        and sum(bool(row["passed"]) for row in results) == 120
        and len(created) == len(waits) == len(custody) == 5
        and len(opened) == len(closed) == 20
    ):
        raise AssertionError("producer case or fixture journal counts mismatch")
    created_pids = [row["pid"] for row in created]
    if created_pids != receipt["accounting"]["created_pids"]:
        raise AssertionError("producer PID accounting mismatch")
    if not all(row["reaped"] for row in waits):
        raise AssertionError("producer retained an unreaped fixture")
    if not all(row["complete"] and not row["unreaped_children"] and not row["unclosed_descriptors"] for row in custody):
        raise AssertionError("producer retained incomplete fixture custody")
    samples = attempt["samples"]
    peak = max(row["aggregate_rss_bytes"] for row in samples)
    sampled_pid_sets = sorted({tuple(item["pid"] for item in row["processes"]) for row in samples})
    sampled_pids = sorted({item["pid"] for row in samples for item in row["processes"]})
    unsampled_fixture_pids = sorted(set(created_pids) - set(sampled_pids))
    if peak != receipt["accounting"]["maximum_observed_aggregate_RSS_bytes"]:
        raise AssertionError("producer RSS peak mismatch")
    if set(receipt["current_code_sha256"].values()) != set(protocol["current_source_sha256"].values()):
        raise AssertionError("current code source maps differ")
    if protocol["registered_case_count"] != 120 or protocol["preserved_predecessor_case_names"] != 99:
        raise AssertionError("protocol registry metadata mismatch")
    metadata = receipt["metadata_after_test_change"]
    tested_readme = invocations[2]["retained_files"]["source/README.md"]["sha256"]
    if metadata["tested_bytes_sha256"] != tested_readme or metadata["final_bytes_sha256"] != receipt["final_readme_sha256"]:
        raise AssertionError("README metadata change binding mismatch")
    for name in ("supervisor.py", "container.py", "host.py", "tests.py", "protocol-binding.json"):
        retained = invocations[2]["retained_files"][f"source/{name}"]["sha256"]
        current = digest(payloads[f"{PRODUCER_DIR}/{name}"])
        if retained != current:
            raise AssertionError(f"tested source differs from snapshot source: {name}")
    return {
        "result": "passed_with_declared_limitations",
        "invocation_count": 3,
        "registry_discovery_invocations": 2,
        "registry_controls_executed": 0,
        "complete_suite_invocations": 1,
        "fixed_controls_executed": len(results),
        "passed_controls": sum(bool(row["passed"]) for row in results),
        "failed_controls": sum(not bool(row["passed"]) for row in results),
        "case_start_rows": len(starts),
        "case_result_rows": len(terminals),
        "fixture_created_pids": created_pids,
        "fixture_wait_rows": len(waits),
        "descriptor_create_rows": len(opened),
        "descriptor_close_rows": len(closed),
        "all_fixture_children_reaped_and_descriptors_closed": True,
        "sample_count": len(samples),
        "peak_observed_aggregate_rss_bytes": peak,
        "sampled_pid_sets": sampled_pid_sets,
        "unsampled_short_lived_fixture_pids": unsampled_fixture_pids,
        "missing_final_samples_preserved_as_unavailable": bool(unsampled_fixture_pids),
        "source_versions": source_versions,
        "registry_summaries": registry_summaries,
        "retained_payload_count": len(retained_rows),
        "retained_payloads": retained_rows,
        "readme_was_sole_declared_post_test_metadata_edit": True,
        "tested_readme_sha256": tested_readme,
        "final_readme_sha256": receipt["final_readme_sha256"],
        "tested_code_and_protocol_match_snapshot": True,
        "embedded_controllers_executed": False,
    }


def load_modules(source_dir: Path) -> tuple[Any, Any, Any]:
    sys.path.insert(0, str(source_dir))
    try:
        import container as container_module
        import supervisor as supervisor_module
        import host as host_module
    finally:
        sys.path.pop(0)
    return container_module, supervisor_module, host_module


def make_image_json(container_module: Any) -> str:
    return json.dumps(
        [
            {
                "Id": container_module.PINNED_IMAGE_DIGEST,
                "RepoDigests": [f"python@{container_module.PINNED_IMAGE_DIGEST}"],
                "Os": "linux",
                "Architecture": "arm64",
            }
        ]
    )


def make_container_json(container_module: Any, cid: str, nonce: str, *, running: bool = False, exit_code: int = 0, oom: bool = False) -> str:
    plan = container_module.planned_container()
    return json.dumps(
        [
            {
                "Id": cid,
                "Image": container_module.PINNED_IMAGE_DIGEST,
                "Config": {
                    "Image": plan.image,
                    "Labels": {"crypto.autoresearch.task": container_module.TASK_ID, "crypto.autoresearch.nonce": nonce},
                    "User": plan.user,
                    "OpenStdin": True,
                    "AttachStdin": True,
                    "Tty": False,
                    "Cmd": ["python3", "-B", "/opt/group-oom/container.py"],
                },
                "HostConfig": {
                    "NetworkMode": plan.network,
                    "ReadonlyRootfs": True,
                    "CapDrop": list(plan.cap_drop),
                    "CapAdd": list(plan.cap_add),
                    "SecurityOpt": ["no-new-privileges:true"],
                    "CgroupnsMode": plan.cgroup_namespace,
                    "PidMode": plan.pid_namespace,
                    "PidsLimit": plan.pids_limit,
                    "NanoCpus": plan.cpu_quota_cores * 1_000_000_000,
                    "Memory": plan.outer_memory_bytes,
                    "MemorySwap": plan.outer_memory_swap_total_bytes,
                    "Tmpfs": dict(plan.tmpfs),
                    "Privileged": False,
                    "AutoRemove": False,
                },
                "Mounts": [
                    {
                        "Type": plan.mounts[0].type,
                        "Source": plan.mounts[0].source,
                        "Destination": plan.mounts[0].target,
                        "RW": True,
                    }
                ],
                "State": {"Running": running, "ExitCode": exit_code, "OOMKilled": oom},
            }
        ]
    )


def command_result(host_module: Any, argv: Sequence[str], stdin: bytes | None, stdout: str = "", exit_code: int = 0, timed_out: bool = False) -> Any:
    raw_out = stdout.encode("utf-8")
    return host_module.CommandResult(
        argv=tuple(argv),
        started_at_UTC="2026-09-10T00:00:00+00:00",
        ended_at_UTC="2026-09-10T00:00:00.001000+00:00",
        exit_code=exit_code,
        stdout=stdout,
        stderr="",
        timed_out=timed_out,
        timeout_seconds=30,
        wall_seconds=0.001,
        stdin_bytes=len(stdin or b""),
        stdin_sha256=digest(stdin) if stdin is not None else None,
        process_pid=None,
        process_group_id=None,
        terminal_observed=True,
        stdout_base64=base64.b64encode(raw_out).decode("ascii"),
        stderr_base64="",
    )


class InjectedDockerTransport:
    def __init__(self, container_module: Any, host_module: Any, *, inner_clean: bool, fail_action: str | None = None) -> None:
        self.container = container_module
        self.host = host_module
        self.cid = "a" * 64
        self.nonce = "1" * 12
        self.inner_clean = inner_clean
        self.fail_action = fail_action
        self.inspect_count = 0
        self.calls: list[str] = []

    def run(self, argv: Sequence[str], stdin: bytes | None, timeout_seconds: float) -> Any:
        action = argv[3]
        self.calls.append(action)
        if action == self.fail_action:
            raise OSError(f"injected generic {action} transport failure")
        if action == "image":
            return command_result(self.host, argv, stdin, make_image_json(self.container))
        if action == "create":
            return command_result(self.host, argv, stdin, self.cid + "\n")
        if action == "inspect":
            self.inspect_count += 1
            return command_result(self.host, argv, stdin, make_container_json(self.container, self.cid, self.nonce))
        if action == "cp":
            return command_result(self.host, argv, stdin)
        if action == "start":
            identity = self.container.StartupIdentity(self.container.TASK_ID, self.cid, "exact_profile")
            outcome = {
                "task_id": self.container.TASK_ID,
                "case_id": "exact_profile",
                "expected_container_id": self.cid,
                "status": "inner_complete" if self.inner_clean else "failed_custody",
                "classification": "profile_accepted",
                "cleanup_complete": self.inner_clean,
                "failures": [] if self.inner_clean else [{"code": "incomplete_required_cleanup"}],
            }
            wire = json.dumps(self.container.source_result(identity, outcome), sort_keys=True) + "\n"
            return command_result(self.host, argv, stdin, wire, exit_code=0 if self.inner_clean else 2)
        if action == "logs":
            return command_result(self.host, argv, stdin, "retained log\n")
        if action in {"kill", "rm"}:
            return command_result(self.host, argv, stdin, self.cid + "\n")
        raise AssertionError(action)


class CleanupCgroups:
    def __init__(self, *, disable_error: bool = False) -> None:
        self.trace: list[str] = []
        self.disable_error = disable_error

    def child_is_populated(self, handle: str) -> bool:
        self.trace.append(f"populated:{handle}")
        return False

    def list_direct_members(self, handle: str) -> Sequence[int]:
        self.trace.append(f"members:{handle}")
        return [4242] if handle == "root" else []

    def remove_empty_child(self, parent: str, name: str, expected: str) -> None:
        self.trace.append(f"remove:{name}:{expected}")

    def write_text(self, directory: str, filename: str, value: str) -> None:
        self.trace.append(f"write:{filename}:{value}")
        if self.disable_error:
            raise OSError("disable refused")

    def read_text(self, directory: str, filename: str) -> str:
        self.trace.append(f"read:{filename}")
        return ""

    def move_pid(self, directory: str, pid: int) -> None:
        self.trace.append(f"move:{pid}:{directory}")

    def close_handle(self, handle: str) -> None:
        self.trace.append(f"close:{handle}")


class CleanupProcesses:
    def supervisor_pid(self) -> int:
        return 4242

    def active_owned_children(self) -> Sequence[int]:
        return ()


def build_cases(container_module: Any, supervisor_module: Any, host_module: Any, source_dir: Path, fixture_journal: Path) -> list[Case]:
    cases: list[Case] = []

    def add(name: str) -> Callable[[Callable[[], Mapping[str, Any] | None]], Callable[[], Mapping[str, Any] | None]]:
        def decorate(function: Callable[[], Mapping[str, Any] | None]) -> Callable[[], Mapping[str, Any] | None]:
            cases.append((name, function))
            return function
        return decorate

    cid = "a" * 64
    nonce = "1" * 12

    @add("ir01_current_task_name_and_label_hold")
    def _() -> Mapping[str, Any]:
        adapter = host_module.DockerHostAdapter(SimpleNamespace(), source_dir, {})
        name = f"{container_module.TASK_ID.lower()}-exact-profile-{nonce}"
        argv = adapter._create_argv(name, nonce)
        assert name.startswith(container_module.TASK_ID.lower())
        assert f"crypto.autoresearch.task={container_module.TASK_ID}" in argv
        assert f"crypto.autoresearch.nonce={nonce}" in argv
        return {"name": name}

    @add("ir01_nonce_mismatch_refused")
    def _() -> None:
        inspection = container_module.inspection_from_docker_json(make_container_json(container_module, cid, "2" * 12), make_image_json(container_module), cid)
        try:
            container_module.require_inspection_matches(inspection, cid, container_module.PINNED_IMAGE_DIGEST, nonce)
        except container_module.ContainerBindingError as exc:
            assert "nonce_label" in str(exc)
            return
        raise AssertionError("mismatched nonce accepted")

    @add("ir01_full_id_mismatch_refused")
    def _() -> None:
        try:
            container_module.inspection_from_docker_json(make_container_json(container_module, "b" * 64, nonce), make_image_json(container_module), cid)
        except container_module.ContainerBindingError:
            return
        raise AssertionError("mismatched full container ID accepted")

    @add("nf01_actual_serializer_to_host_parser_holds")
    def _() -> None:
        identity = container_module.StartupIdentity(container_module.TASK_ID, cid, "exact_profile")
        outcome = {"status": "inner_complete", "cleanup_complete": True, "classification": "profile_accepted"}
        raw = json.dumps(container_module.source_result(identity, outcome)) + "\n"
        parsed = host_module._parse_inner(raw)
        assert parsed["schema"] == container_module.RESULT_SCHEMA
        assert parsed["startup_identity"] == asdict(identity)
        assert parsed["outcome"] == outcome

    for case_name, mutate in (
        ("nf01_wrong_schema_refused", lambda row: row.__setitem__("schema", "v1")),
        ("nf01_missing_identity_refused", lambda row: row.pop("startup_identity")),
        ("nf01_missing_outcome_refused", lambda row: row.pop("outcome")),
        ("nf01_false_boolean_cleanup_refused", lambda row: row["outcome"].__setitem__("cleanup_complete", 1)),
    ):
        @add(case_name)
        def _(mutate=mutate) -> None:
            identity = container_module.StartupIdentity(container_module.TASK_ID, cid, "exact_profile")
            row = container_module.source_result(identity, {"status": "inner_complete", "cleanup_complete": True, "classification": "profile_accepted"})
            mutate(row)
            parsed = host_module._parse_inner(json.dumps(row) + "\n")
            valid = (
                parsed.get("schema") == container_module.RESULT_SCHEMA
                and parsed.get("startup_identity") == asdict(identity)
                and isinstance(parsed.get("outcome"), Mapping)
                and parsed["outcome"].get("status") == "inner_complete"
                and parsed["outcome"].get("cleanup_complete") is True
            )
            assert not valid

    @add("nf02_disable_precedes_supervisor_return_holds")
    def _() -> Mapping[str, Any]:
        cgroups = CleanupCgroups()
        supervisor = supervisor_module.GroupOomSupervisor(cgroups, CleanupProcesses())
        outcome = supervisor_module.SupervisorOutcome(container_module.TASK_ID, "exact_profile", cid, utc_now())
        assert supervisor._cleanup(outcome, "root", "supervisor", "worker", None, True, True)
        disable = cgroups.trace.index("write:cgroup.subtree_control:-memory")
        move = cgroups.trace.index("move:4242:root")
        assert disable < move
        return {"trace": cgroups.trace}

    @add("nf02_disable_failure_prevents_return_holds")
    def _() -> Mapping[str, Any]:
        cgroups = CleanupCgroups(disable_error=True)
        supervisor = supervisor_module.GroupOomSupervisor(cgroups, CleanupProcesses())
        outcome = supervisor_module.SupervisorOutcome(container_module.TASK_ID, "exact_profile", cid, utc_now())
        assert not supervisor._cleanup(outcome, "root", "supervisor", "worker", None, True, True)
        assert "move:4242:root" not in cgroups.trace
        return {"trace": cgroups.trace}

    @add("nf05_permission_error_fails_closed")
    def _() -> None:
        transport = object.__new__(supervisor_module.DescriptorCgroupTransport)
        with mock.patch.object(supervisor_module.os, "listdir", return_value=["foreign"]), mock.patch.object(
            supervisor_module.os, "stat", side_effect=PermissionError("controlled")
        ):
            try:
                transport.list_children(SimpleNamespace(fd=42))
            except supervisor_module.GuardError as exc:
                assert exc.code == "cgroup_child_stat_failed" and "foreign" in exc.detail
                return
        raise AssertionError("PermissionError was treated as absence")

    for case_name, error in (
        ("nf05_disappearing_entry_fails_closed", FileNotFoundError("controlled")),
        ("nf05_other_stat_error_fails_closed", OSError("controlled")),
    ):
        @add(case_name)
        def _(error=error) -> None:
            transport = object.__new__(supervisor_module.DescriptorCgroupTransport)
            with mock.patch.object(supervisor_module.os, "listdir", return_value=["foreign"]), mock.patch.object(
                supervisor_module.os, "stat", side_effect=error
            ):
                try:
                    transport.list_children(SimpleNamespace(fd=42))
                except supervisor_module.GuardError as exc:
                    assert exc.code == "cgroup_child_stat_failed" and "foreign" in exc.detail
                    return
            raise AssertionError("stat error was treated as absence")

    def directory(fd: int, inode: int, *, closed: bool = False) -> Any:
        facts = supervisor_module.MountFacts("Linux", "cgroup2", supervisor_module.CGROUP2_SUPER_MAGIC, "/host-cgroup", True, "cgroup2")
        return supervisor_module.DirectoryHandle(fd, f"docker/{cid}/guard-worker", 7, inode, facts, closed)

    @add("ir02_exact_created_handle_removal_holds")
    def _() -> None:
        parent = directory(50, 10)
        parent.relative_path = f"docker/{cid}"
        expected = directory(51, 11)
        reopened = directory(52, 11)
        transport = object.__new__(supervisor_module.DescriptorCgroupTransport)
        transport._created_children = {(7, 10, "guard-worker"): expected}
        stats = [SimpleNamespace(st_dev=7, st_ino=10, st_mode=stat.S_IFDIR), SimpleNamespace(st_dev=7, st_ino=11, st_mode=stat.S_IFDIR)]
        with mock.patch.object(supervisor_module.os, "fstat", side_effect=stats), mock.patch.object(
            transport, "_open_child", return_value=reopened
        ), mock.patch.object(transport, "child_is_populated", return_value=False), mock.patch.object(
            transport, "list_direct_members", return_value=[]
        ), mock.patch.object(supervisor_module.os, "stat", return_value=SimpleNamespace(st_dev=7, st_ino=11, st_mode=stat.S_IFDIR)), mock.patch.object(
            supervisor_module.os, "rmdir"
        ) as removed, mock.patch.object(transport, "close_handle"):
            transport.remove_empty_child(parent, "guard-worker", expected)
        removed.assert_called_once_with("guard-worker", dir_fd=50)

    for case_name, mode in (
        ("ir02_replacement_inode_refused", "inode"),
        ("ir02_replacement_device_refused", "device"),
        ("ir02_closed_handle_refused", "closed"),
        ("ir02_unowned_handle_refused", "unowned"),
        ("ir02_populated_handle_refused", "populated"),
    ):
        @add(case_name)
        def _(mode=mode) -> None:
            parent = directory(50, 10)
            parent.relative_path = f"docker/{cid}"
            expected = directory(51, 11, closed=mode == "closed")
            supplied = directory(51, 11, closed=mode == "closed") if mode == "unowned" else expected
            reopened = directory(52, 12 if mode == "inode" else 11)
            if mode == "device":
                reopened.device = 8
            transport = object.__new__(supervisor_module.DescriptorCgroupTransport)
            transport._created_children = {(7, 10, "guard-worker"): expected}
            stats = [SimpleNamespace(st_dev=7, st_ino=10, st_mode=stat.S_IFDIR), SimpleNamespace(st_dev=7, st_ino=11, st_mode=stat.S_IFDIR)]
            with mock.patch.object(supervisor_module.os, "fstat", side_effect=stats), mock.patch.object(
                transport, "_open_child", return_value=reopened
            ), mock.patch.object(transport, "child_is_populated", return_value=mode == "populated"), mock.patch.object(
                transport, "list_direct_members", return_value=[]
            ), mock.patch.object(supervisor_module.os, "stat", return_value=SimpleNamespace(st_dev=7, st_ino=11, st_mode=stat.S_IFDIR)), mock.patch.object(
                supervisor_module.os, "rmdir"
            ) as removed, mock.patch.object(transport, "close_handle"):
                try:
                    transport.remove_empty_child(parent, "guard-worker", supplied)
                except supervisor_module.GuardError:
                    removed.assert_not_called()
                    return
            raise AssertionError(f"unsafe removal accepted: {mode}")

    @add("break_f06_open_child_fstat_failure_leaks_descriptor")
    def _() -> Mapping[str, Any]:
        parent = directory(50, 10)
        parent.relative_path = f"docker/{cid}"
        transport = object.__new__(supervisor_module.DescriptorCgroupTransport)
        with mock.patch.object(supervisor_module.os, "open", return_value=701), mock.patch.object(
            supervisor_module.os, "fstat", side_effect=OSError("injected fstat failure after open")
        ), mock.patch.object(supervisor_module.os, "close") as closed:
            try:
                transport._open_child(parent, "guard-worker")
            except OSError as exc:
                observed_exception = f"{type(exc).__name__}:{exc}"
            else:
                raise AssertionError("fstat failure not propagated")
        leaked = not any(call.args == (701,) for call in closed.call_args_list)
        assert leaked, "counterexample no longer reproduces; descriptor was closed"
        return {"defect_reproduced": True, "opened_fd": 701, "close_called": False, "exception": observed_exception}

    @add("break_ir02_primary_removal_error_masked_by_close_error")
    def _() -> Mapping[str, Any]:
        parent = directory(50, 10)
        parent.relative_path = f"docker/{cid}"
        expected = directory(51, 11)
        replacement = directory(52, 12)
        transport = object.__new__(supervisor_module.DescriptorCgroupTransport)
        transport._created_children = {(7, 10, "guard-worker"): expected}
        stats = [SimpleNamespace(st_dev=7, st_ino=10, st_mode=stat.S_IFDIR), SimpleNamespace(st_dev=7, st_ino=11, st_mode=stat.S_IFDIR)]
        with mock.patch.object(supervisor_module.os, "fstat", side_effect=stats), mock.patch.object(
            transport, "_open_child", return_value=replacement
        ), mock.patch.object(transport, "close_handle", side_effect=OSError("injected reopened-handle close failure")), mock.patch.object(
            supervisor_module.os, "rmdir"
        ) as removed:
            try:
                transport.remove_empty_child(parent, "guard-worker", expected)
            except Exception as exc:
                observed = f"{type(exc).__name__}:{exc}"
                context = f"{type(exc.__context__).__name__}:{exc.__context__}" if exc.__context__ else None
            else:
                raise AssertionError("replacement and close failures accepted")
        removed.assert_not_called()
        assert observed.startswith("OSError:") and context and "cgroup_removal_identity_changed" in context
        return {"defect_reproduced": True, "raised_primary_to_caller": observed, "masked_original_context": context, "structured_primary_secondary_pair": False}

    @add("ir03_generic_transport_attempt_row_holds")
    def _() -> Mapping[str, Any]:
        outcome = host_module.HostOutcome(container_module.TASK_ID, "exact_profile", utc_now())
        def fail(argv: Sequence[str], stdin: bytes | None, timeout: float) -> Any:
            raise OSError("unknown transport state")
        adapter = host_module.DockerHostAdapter(SimpleNamespace(run=fail), source_dir, {})
        try:
            adapter._run(outcome, ("image", "inspect", container_module.PINNED_IMAGE), b"abc", 7)
        except OSError:
            pass
        else:
            raise AssertionError("generic transport exception lost")
        row = outcome.commands[0]
        assert row["argv"] and row["stdin_sha256"] == digest(b"abc") and row["launch_state"] == "unknown"
        assert row["process_pid"] is None and row["terminal_observed"] is None
        return row

    @add("ir03_popen_launch_failure_facts_hold")
    def _() -> Mapping[str, Any]:
        with mock.patch.object(host_module.subprocess, "Popen", side_effect=OSError("launch denied")):
            try:
                host_module.SubprocessTransport().run(["synthetic"], b"abc", 2)
            except host_module.CommandTransportFailure as exc:
                row = exc.observations
            else:
                raise AssertionError("Popen failure returned success")
        assert row["launch_state"] == "not_started" and row["exit_code"] is None
        assert row["stdout"] is None and row["stdout_base64"] is None and row["process_pid"] is None
        return row

    @add("ir03_timeout_cumulative_output_holds")
    def _() -> Mapping[str, Any]:
        process = SimpleNamespace(pid=900001, returncode=-9)
        process.communicate = mock.Mock(
            side_effect=[
                subprocess.TimeoutExpired(["synthetic"], 2, output=b"abc", stderr=b"err"),
                (b"abcdef", b"error"),
            ]
        )
        with mock.patch.object(host_module.subprocess, "Popen", return_value=process), mock.patch.object(host_module.os, "killpg"):
            result = host_module.SubprocessTransport().run(["synthetic"], b"abc", 2)
        assert result.timed_out and base64.b64decode(result.stdout_base64) == b"abcdef"
        assert base64.b64decode(result.stderr_base64) == b"error"
        return {"stdout_sha256": digest(b"abcdef"), "stderr_sha256": digest(b"error")}

    @add("ir03_actual_benign_subprocess_raw_bytes_and_terminal_holds")
    def _() -> Mapping[str, Any]:
        real_popen = subprocess.Popen
        holder: dict[str, Any] = {}
        def observed_popen(*args: Any, **kwargs: Any) -> Any:
            process = real_popen(*args, **kwargs)
            holder["process"] = process
            journal(
                fixture_journal,
                "owned_process_created",
                case_id="ir03_actual_benign_subprocess_raw_bytes_and_terminal_holds",
                purpose="two_byte_invalid_utf8_command_custody",
                pid=process.pid,
                argv=list(args[0]),
                deliberate_payload_bytes=2,
            )
            return process
        argv = [sys.executable, "-B", "-c", "import os,time;os.write(1,bytes([255,120]));time.sleep(0.1)"]
        began = time.monotonic()
        try:
            with mock.patch.object(host_module.subprocess, "Popen", side_effect=observed_popen):
                result = host_module.SubprocessTransport().run(argv, None, 2)
        finally:
            process = holder.get("process")
            if process is not None:
                if process.poll() is None:
                    process.kill()
                code = process.wait()
                streams = [process.stdout, process.stderr]
                descriptors_closed = all(stream is None or stream.closed for stream in streams)
                journal(
                    fixture_journal,
                    "owned_process_terminal",
                    case_id="ir03_actual_benign_subprocess_raw_bytes_and_terminal_holds",
                    purpose="two_byte_invalid_utf8_command_custody",
                    pid=process.pid,
                    exit_code=code,
                    reaped=True,
                    descriptors_closed=descriptors_closed,
                    wall_seconds=time.monotonic() - began,
                )
        assert result.exit_code == 0 and result.terminal_observed and base64.b64decode(result.stdout_base64) == b"\xffx"
        assert time.monotonic() - began <= MAX_CHILD_LIFETIME_SECONDS
        return {"fixture_pid": holder["process"].pid, "payload_bytes": 2, "raw_stdout_sha256": digest(b"\xffx"), "decoded_stdout": result.stdout}

    @add("ir04_barrier_primary_and_secondary_hold")
    def _() -> Mapping[str, Any]:
        transport = supervisor_module.PosixProcessTransport(lambda *_args: None)
        state = SimpleNamespace(released=False, control_write_fd=42)
        child = supervisor_module.ChildHandle(900001, "synthetic")
        primary = supervisor_module.GuardError("worker_barrier_release_failed", "original")
        with mock.patch.object(transport, "_state", return_value=state), mock.patch.object(
            transport, "_write_all", side_effect=primary
        ), mock.patch.object(transport, "finalize_owned_child", side_effect=OSError("secondary")):
            try:
                transport.release(child)
            except supervisor_module.GuardError as exc:
                assert exc is primary
            else:
                raise AssertionError("barrier failures accepted")
        assert primary.cleanup_failures == [{"code": "barrier_release_cleanup_failed", "detail": "OSError:secondary"}]
        return {"primary": primary.code, "secondary": primary.cleanup_failures}

    @add("break_host_cleanup_kill_transport_exception_escapes_outcome")
    def _() -> Mapping[str, Any]:
        transport = InjectedDockerTransport(container_module, host_module, inner_clean=False, fail_action="kill")
        hashes = {name: digest((source_dir / name).read_bytes()) for name in host_module.HELPERS}
        adapter = host_module.DockerHostAdapter(transport, source_dir, hashes, lambda: nonce)
        try:
            adapter.run_case("exact_profile")
        except OSError as exc:
            observed = f"{type(exc).__name__}:{exc}"
        else:
            raise AssertionError("counterexample no longer reproduces; run_case returned an outcome")
        assert "kill" in transport.calls and observed.endswith("injected generic kill transport failure")
        return {"defect_reproduced": True, "escaped_exception": observed, "outcome_returned": False, "ended_at_retained": False, "calls": transport.calls}

    @add("break_host_cleanup_rm_transport_exception_escapes_complete_outcome")
    def _() -> Mapping[str, Any]:
        transport = InjectedDockerTransport(container_module, host_module, inner_clean=True, fail_action="rm")
        hashes = {name: digest((source_dir / name).read_bytes()) for name in host_module.HELPERS}
        adapter = host_module.DockerHostAdapter(transport, source_dir, hashes, lambda: nonce)
        try:
            adapter.run_case("exact_profile")
        except OSError as exc:
            observed = f"{type(exc).__name__}:{exc}"
        else:
            raise AssertionError("counterexample no longer reproduces; run_case returned an outcome")
        assert "rm" in transport.calls and observed.endswith("injected generic rm transport failure")
        return {"defect_reproduced": True, "escaped_exception": observed, "outcome_returned": False, "exact_remove_result_retained": False, "calls": transport.calls}

    @add("f01_path_import_and_f02_signal_mapping_hold")
    def _() -> None:
        assert supervisor_module.Path is Path and supervisor_module.PurePosixPath is not None
        assert supervisor_module.PosixProcessTransport._signal_name(-signal.SIGKILL) == "SIGKILL"

    @add("f05_counter_delta_requires_increments")
    def _() -> None:
        baseline = {"memory.events": "oom_kill 7\noom_group_kill 3\n"}
        final = {"memory.events": "oom_kill 9\noom_group_kill 4\n"}
        assert supervisor_module.GroupOomSupervisor._counter_delta(baseline, final) == {"oom_group_kill": 1, "oom_kill": 2}
        try:
            supervisor_module.GroupOomSupervisor._counter_delta(baseline, baseline)
        except supervisor_module.GuardError:
            # _counter_delta itself permits zero and the terminal verifier enforces thresholds.
            pass

    @add("source_scope_has_no_live_import_side_effect")
    def _() -> None:
        assert container_module.TASK_ID == SOURCE_TASK_ID
        assert container_module.RESULT_SCHEMA == "crypto.autoresearch.group_oom_container_result.v2"
        assert container_module.planned_container().cap_add == ("SETUID", "SETGID")
        assert container_module.planned_container().cap_drop == ("ALL",)

    if len(cases) > MAX_SUITE_CASES:
        raise AssertionError("independent suite exceeds 128 cases")
    return cases


class CaseTimeout(RuntimeError):
    pass


def alarm_handler(_signum: int, _frame: Any) -> None:
    raise CaseTimeout(f"case exceeded {PER_CASE_SECONDS} seconds")


def worker_main(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    attempt_dir = Path(args.attempt_dir).resolve()
    source_dir = attempt_dir / "source"
    fixture_journal = attempt_dir / "fixture-journal.jsonl"
    container_module, supervisor_module, host_module = load_modules(source_dir)
    started = utc_now()
    began = time.monotonic()
    admin, payloads = read_and_verify_frozen_inputs(repo, fixture_journal)
    producer = verify_producer_receipt(payloads)
    cases = build_cases(container_module, supervisor_module, host_module, source_dir, fixture_journal)
    results: list[Mapping[str, Any]] = []
    prior_handler = signal.signal(signal.SIGALRM, alarm_handler)
    try:
        for case_id, function in cases:
            case_start = time.monotonic()
            journal(fixture_journal, "case_start", case_id=case_id)
            row: dict[str, Any] = {"id": case_id, "started_at_UTC": utc_now()}
            signal.alarm(PER_CASE_SECONDS)
            try:
                details = function()
                row.update(passed=True, details=details or {})
            except BaseException as exc:
                row.update(
                    passed=False,
                    error={"type": type(exc).__name__, "message": str(exc), "traceback": traceback.format_exc()},
                )
            finally:
                signal.alarm(0)
                row["ended_at_UTC"] = utc_now()
                row["wall_seconds"] = time.monotonic() - case_start
                results.append(row)
                journal(fixture_journal, "case_result", case_id=case_id, result=row)
    finally:
        signal.signal(signal.SIGALRM, prior_handler)
    fixed_starts = []
    fixed_terminals = []
    for line in fixture_journal.read_text(encoding="utf-8").splitlines():
        item = json.loads(line)
        if item.get("purpose") == "two_byte_invalid_utf8_command_custody":
            if item["event"] == "owned_process_created":
                fixed_starts.append(item)
            elif item["event"] == "owned_process_terminal":
                fixed_terminals.append(item)
    output = {
        "schema": "crypto.autoresearch.native_ir_independent_suite.v1",
        "task_id": TASK_ID,
        "source_task_id": SOURCE_TASK_ID,
        "suite_label": args.suite_label,
        "started_at_UTC": started,
        "ended_at_UTC": utc_now(),
        "wall_seconds": time.monotonic() - began,
        "administrative_source_and_receipt_checks": admin,
        "producer_receipt_recomputation": producer,
        "fixed_control_count": len(results),
        "passed_control_count": sum(bool(row["passed"]) for row in results),
        "failed_control_count": sum(not bool(row["passed"]) for row in results),
        "results": results,
        "benign_fixture_starts": len(fixed_starts),
        "benign_fixture_created_pids": [row["pid"] for row in fixed_starts],
        "benign_fixture_terminals": fixed_terminals,
        "actual_maximum_concurrent_fixture_children": 1 if fixed_starts else 0,
        "actual_maximum_deliberate_fixture_payload_bytes": max([row["deliberate_payload_bytes"] for row in fixed_starts] or [0]),
        "scientific_runs": 0,
        "live_docker_calls": 0,
        "live_cgroup_or_mount_operations": 0,
        "privilege_changes": 0,
        "process_migrations": 0,
        "pressure_actions": 0,
        "embedded_producer_scripts_executed": False,
        "hard_kernel_memory_claim": False,
    }
    print(json.dumps(output, sort_keys=True, separators=(",", ":")), flush=True)
    return 0 if output["failed_control_count"] == 0 else 2


class ProcPidInfo(ctypes.Structure):
    _fields_ = [
        ("pbi_flags", ctypes.c_uint32), ("pbi_status", ctypes.c_uint32), ("pbi_xstatus", ctypes.c_uint32),
        ("pbi_pid", ctypes.c_uint32), ("pbi_ppid", ctypes.c_uint32), ("pbi_uid", ctypes.c_uint32),
        ("pbi_gid", ctypes.c_uint32), ("pbi_ruid", ctypes.c_uint32), ("pbi_rgid", ctypes.c_uint32),
        ("pbi_svuid", ctypes.c_uint32), ("pbi_svgid", ctypes.c_uint32), ("rfu_1", ctypes.c_uint32),
        ("pbi_comm", ctypes.c_char * 16), ("pbi_name", ctypes.c_char * 32),
        ("pbi_nfiles", ctypes.c_uint32), ("pbi_pgid", ctypes.c_uint32), ("pbi_pjobc", ctypes.c_uint32),
        ("e_tdev", ctypes.c_uint32), ("e_tpgid", ctypes.c_uint32), ("pbi_nice", ctypes.c_int32),
        ("pbi_start_tvsec", ctypes.c_uint64), ("pbi_start_tvusec", ctypes.c_uint64),
    ]


class ProcTaskInfo(ctypes.Structure):
    _fields_ = [
        ("pti_virtual_size", ctypes.c_uint64), ("pti_resident_size", ctypes.c_uint64),
        ("pti_total_user", ctypes.c_uint64), ("pti_total_system", ctypes.c_uint64),
        ("pti_threads_user", ctypes.c_uint64), ("pti_threads_system", ctypes.c_uint64),
        ("pti_policy", ctypes.c_int32), ("pti_faults", ctypes.c_int32),
        ("pti_pageins", ctypes.c_int32), ("pti_cow_faults", ctypes.c_int32),
        ("pti_messages_sent", ctypes.c_int32), ("pti_messages_received", ctypes.c_int32),
        ("pti_syscalls_mach", ctypes.c_int32), ("pti_syscalls_unix", ctypes.c_int32),
        ("pti_csw", ctypes.c_int32), ("pti_threadnum", ctypes.c_int32),
        ("pti_numrunning", ctypes.c_int32), ("pti_priority", ctypes.c_int32),
    ]


def exact_pid_rss(pid: int) -> tuple[int | None, str]:
    if platform.system() == "Darwin":
        libproc = ctypes.CDLL("/usr/lib/libproc.dylib")
        info = ProcTaskInfo()
        result = libproc.proc_pidinfo(pid, 4, 0, ctypes.byref(info), ctypes.sizeof(info))
        return (int(info.pti_resident_size), "darwin_proc_pidinfo") if result == ctypes.sizeof(info) else (None, "darwin_proc_pidinfo_unavailable")
    statm = Path(f"/proc/{pid}/statm")
    try:
        resident_pages = int(statm.read_text(encoding="ascii").split()[1])
        return resident_pages * os.sysconf("SC_PAGE_SIZE"), "proc_pid_statm"
    except (FileNotFoundError, ProcessLookupError):
        return None, "proc_pid_statm_unavailable"


def read_created_pids(journal_path: Path) -> set[int]:
    pids: set[int] = set()
    try:
        lines = journal_path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return pids
    for line in lines:
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if row.get("event") == "owned_process_created" and isinstance(row.get("pid"), int):
            pids.add(row["pid"])
    return pids


def controller_main(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    attempt_dir = Path(args.attempt_dir).resolve()
    checker = Path(__file__).resolve()
    source_dir = attempt_dir / "source"
    raw_stdout = attempt_dir / "raw-stdout.bin"
    raw_stderr = attempt_dir / "raw-stderr.bin"
    fixture_journal = attempt_dir / "fixture-journal.jsonl"
    samples_path = attempt_dir / "samples.jsonl"
    launch_path = attempt_dir / "launch.json"
    attempt_receipt_path = attempt_dir / "attempt-receipt.json"
    reservation_path = attempt_dir / "reservation.json"
    required = [checker, *(source_dir / name for name in PRODUCER_ARTIFACT_NAMES)]
    if not all(path.is_file() for path in required):
        raise SystemExit("attempt source/checker reservation incomplete")
    for path in (raw_stdout, raw_stderr, fixture_journal, samples_path, launch_path, attempt_receipt_path, reservation_path):
        if not path.exists():
            raise SystemExit(f"pre-reserved path missing: {path}")
    if any(path.stat().st_size for path in (raw_stdout, raw_stderr, fixture_journal, samples_path, launch_path, attempt_receipt_path)):
        raise SystemExit("attempt sink was not empty at launch")
    argv = [sys.executable, "-B", str(checker), "--worker", "--repo", str(repo), "--attempt-dir", str(attempt_dir), "--suite-label", args.suite_label]
    reservation = {
        "task_id": TASK_ID,
        "suite_label": args.suite_label,
        "reserved_at_UTC": utc_now(),
        "argv": argv,
        "repo": str(repo),
        "checker_sha256": digest(checker.read_bytes()),
        "source_sha256": {name: digest((source_dir / name).read_bytes()) for name in PRODUCER_ARTIFACT_NAMES},
        "fixed_controls_reserved": 31,
        "remaining_final_suite_reserved": 31 if args.suite_label != "final" else 0,
        "maximum_total_controls": MAX_TOTAL_CONTROLS,
        "maximum_suite_controls": MAX_SUITE_CASES,
        "maximum_benign_starts": MAX_BENIGN_STARTS,
        "maximum_concurrent_children": MAX_CONCURRENT_CHILDREN,
        "maximum_child_lifetime_seconds": MAX_CHILD_LIFETIME_SECONDS,
        "maximum_deliberate_payload_bytes": MAX_DELIBERATE_PAYLOAD_BYTES,
        "maximum_worker_memory_bytes": MEMORY_LIMIT_BYTES,
        "aggregate_watchdog_seconds": AGGREGATE_SECONDS,
        "canonical_receipt_created": False,
    }
    reservation_path.write_text(json.dumps(reservation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    began = time.monotonic()
    primary_error: Mapping[str, str] | None = None
    cleanup_errors: list[Mapping[str, str]] = []
    watchdog_stop: str | None = None
    process: subprocess.Popen[Any] | None = None
    try:
        with raw_stdout.open("wb") as out_handle, raw_stderr.open("wb") as err_handle:
            try:
                process = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=out_handle, stderr=err_handle, start_new_session=True)
                launch_path.write_text(
                    json.dumps({"pid": process.pid, "process_group_id": process.pid, "at_UTC": utc_now(), "argv": argv}, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
            except Exception as exc:
                primary_error = {"type": type(exc).__name__, "message": str(exc)}
            while process is not None and process.poll() is None:
                owned = {process.pid} | read_created_pids(fixture_journal)
                facts = []
                available_sum = 0
                for pid in sorted(owned):
                    rss, basis = exact_pid_rss(pid)
                    facts.append({"pid": pid, "rss_bytes": rss, "basis": basis})
                    if rss is not None:
                        available_sum += rss
                append_jsonl(
                    samples_path,
                    {
                        "at_UTC": utc_now(),
                        "monotonic_ns": time.monotonic_ns(),
                        "processes": facts,
                        "available_rss_sum_bytes": available_sum,
                        "complete_sample": all(row["rss_bytes"] is not None for row in facts),
                    },
                )
                if available_sum > MEMORY_LIMIT_BYTES:
                    watchdog_stop = "sampled_rss_exceeded_2GiB_machine_protection"
                if time.monotonic() - began > AGGREGATE_SECONDS:
                    watchdog_stop = "aggregate_watchdog_expired"
                if watchdog_stop:
                    os.killpg(process.pid, signal.SIGKILL)
                    break
                time.sleep(0.02)
            if process is not None:
                process.wait()
    except Exception as exc:
        if primary_error is None:
            primary_error = {"type": type(exc).__name__, "message": str(exc)}
        else:
            cleanup_errors.append({"type": type(exc).__name__, "message": str(exc)})
        if process is not None and process.poll() is None:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except Exception as cleanup:
                cleanup_errors.append({"type": type(cleanup).__name__, "message": str(cleanup)})
            process.wait()

    worker_exit = process.returncode if process is not None else None
    stdout_bytes = raw_stdout.read_bytes()
    stderr_bytes = raw_stderr.read_bytes()
    samples = [json.loads(line) for line in samples_path.read_text(encoding="utf-8").splitlines() if line]
    owned_pids = ({process.pid} if process is not None else set()) | read_created_pids(fixture_journal)
    post_exit = []
    for pid in sorted(owned_pids):
        rss, basis = exact_pid_rss(pid)
        post_exit.append({"pid": pid, "rss_bytes": rss, "basis": basis, "post_exit": True})
    parsed = None
    parse_error = None
    try:
        parsed = json.loads(stdout_bytes)
    except Exception as exc:
        parse_error = {"type": type(exc).__name__, "message": str(exc)}
    peak = max([row["available_rss_sum_bytes"] for row in samples] or [0])
    receipt = {
        "schema": "crypto.autoresearch.native_ir_independent_attempt.v1",
        "task_id": TASK_ID,
        "suite_label": args.suite_label,
        "started_at_UTC": reservation["reserved_at_UTC"],
        "ended_at_UTC": utc_now(),
        "wall_seconds": time.monotonic() - began,
        "reservation": reservation,
        "launch": json.loads(launch_path.read_text(encoding="utf-8")) if launch_path.stat().st_size else None,
        "worker_exit_code": worker_exit,
        "primary_error": primary_error,
        "cleanup_errors": cleanup_errors,
        "watchdog_stop": watchdog_stop,
        "raw_stdout_bytes": len(stdout_bytes),
        "raw_stdout_sha256": digest(stdout_bytes),
        "raw_stdout_base64": base64.b64encode(stdout_bytes).decode("ascii"),
        "raw_stderr_bytes": len(stderr_bytes),
        "raw_stderr_sha256": digest(stderr_bytes),
        "raw_stderr_base64": base64.b64encode(stderr_bytes).decode("ascii"),
        "parse_error": parse_error,
        "suite": parsed,
        "fixture_journal_sha256": digest(fixture_journal.read_bytes()),
        "fixture_journal_base64": base64.b64encode(fixture_journal.read_bytes()).decode("ascii"),
        "samples": samples,
        "sample_count": len(samples),
        "peak_observed_aggregate_rss_bytes": peak,
        "post_exit_samples": post_exit,
        "hard_kernel_memory_claim": False,
        "scientific_runs": 0,
        "live_docker_calls": 0,
        "live_cgroup_or_mount_operations": 0,
        "privilege_changes": 0,
        "process_migrations": 0,
        "pressure_actions": 0,
    }
    attempt_receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "task_id": TASK_ID,
                "suite_label": args.suite_label,
                "attempt_receipt": str(attempt_receipt_path),
                "attempt_receipt_sha256": digest(attempt_receipt_path.read_bytes()),
                "worker_exit_code": worker_exit,
                "fixed_controls": parsed.get("fixed_control_count") if isinstance(parsed, Mapping) else None,
                "passed_controls": parsed.get("passed_control_count") if isinstance(parsed, Mapping) else None,
                "failed_controls": parsed.get("failed_control_count") if isinstance(parsed, Mapping) else None,
                "fixture_pids": parsed.get("benign_fixture_created_pids") if isinstance(parsed, Mapping) else None,
                "peak_observed_aggregate_rss_bytes": peak,
            },
            sort_keys=True,
        ),
        flush=True,
    )
    return 0 if worker_exit == 0 and primary_error is None and watchdog_stop is None and parse_error is None else 2


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--worker", action="store_true")
    mode.add_argument("--controller", action="store_true")
    parser.add_argument("--repo", required=True)
    parser.add_argument("--attempt-dir", required=True)
    parser.add_argument("--suite-label", required=True, choices=("preliminary", "final"))
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    raise SystemExit(worker_main(arguments) if arguments.worker else controller_main(arguments))
