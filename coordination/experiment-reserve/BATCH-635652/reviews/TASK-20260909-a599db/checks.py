#!/usr/bin/env python3
"""Independent fixed checks for TASK-20260909-a599db.

This checker is source-only.  It never invokes Docker, opens a live cgroup,
changes credentials, migrates a process, allocates pressure, or executes a
scientific workload.  Native effects are limited to five sequential current-
user POSIX children and ordinary temporary files.
"""
from __future__ import annotations

import argparse
import ast
from contextlib import ExitStack
import ctypes
from dataclasses import asdict
from datetime import datetime, timezone
from io import BytesIO
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import tarfile
import tempfile
import time
from typing import Any, Callable, Mapping, Sequence
from unittest import mock

import yaml


TASK_ID = "TASK-20260909-a599db"
SOURCE_TASK_ID = "TASK-20260909-e5f500"
AUTHORITY_COMMIT = "dd27e712dad31015d0ed30e0df83b6234676f273"
PUBLISHED_CLAIM_COMMIT = "36af919ba3870442014567bcde8337cfcdffae17"
SOURCE_SNAPSHOT = "f7c68d72d806b152c0fa1a8b8f943060baa69065"
REPO = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
SOURCE = REPO / "coordination/experiment-reserve/BATCH-635652/runtime/TASK-20260909-e5f500"
HANDOFF = REPO / "ledger/handoffs/TASK-20260909-a599db.yaml"
PRODUCER_RECEIPT = SOURCE / "check-receipt.json"
GAP_RECORD = REPO / "coordination/experiment-reserve/admission-20260907/group-oom-native-prior-custody-gap.json"
FAILURE_DECISION = REPO / "ledger/decisions/DEC-20260909-3508b9.yaml"
EXPECTED_RECEIPT = HERE / "check-receipt.json"
MAX_TOTAL_CASES = 384
MAX_SUITE_CASES = 128
PER_CASE_SECONDS = 10
AGGREGATE_SECONDS = 1800
MEMORY_LIMIT_BYTES = 2 * 1024 * 1024 * 1024
MAX_BENIGN_STARTS = 32
MAX_CONCURRENT_CHILDREN = 2
MAX_CHILD_LIFETIME_SECONDS = 3.0
MAX_FIXTURE_PAYLOAD_BYTES = 1024 * 1024
FAKE_ID = "a" * 64
IMAGE_ID = "sha256:" + "b" * 64
SUPERVISOR_PID = 5100
WORKER_PID = 5101


sys.path.insert(0, str(SOURCE))
import container as container_module  # noqa: E402
import host as host_module  # noqa: E402
import supervisor as supervisor_module  # noqa: E402


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, detail: str) -> None:
    if not condition:
        raise AssertionError(detail)


def expect_error(function: Callable[[], Any], error: type[BaseException], code: str | None = None) -> BaseException:
    try:
        function()
    except error as exc:
        if code is not None:
            require(getattr(exc, "code", None) == code, f"expected {code}, got {getattr(exc, 'code', None)}")
        return exc
    raise AssertionError(f"expected {error.__name__}")


def image_json() -> str:
    return json.dumps(
        [
            {
                "Id": IMAGE_ID,
                "RepoDigests": [f"python@{container_module.PINNED_IMAGE_DIGEST}"],
                "Os": "linux",
                "Architecture": "arm64",
            }
        ]
    )


def container_json(
    *,
    nonce: str = "1" * 12,
    container_id: str = FAKE_ID,
    cap_add: Sequence[str] = ("SETUID", "SETGID"),
    running: bool = False,
    exit_code: int = 0,
    oom_killed: bool = False,
) -> str:
    return json.dumps(
        [
            {
                "Id": container_id,
                "Image": IMAGE_ID,
                "Name": "/task-20260909-e5f500-exact-profile-" + nonce,
                "Config": {
                    "Image": container_module.PINNED_IMAGE,
                    "Labels": {
                        "crypto.autoresearch.task": container_module.TASK_ID,
                        "crypto.autoresearch.nonce": nonce,
                    },
                    "User": "0:0",
                    "OpenStdin": True,
                    "AttachStdin": True,
                    "Tty": False,
                    "Cmd": ["python3", "-B", "/opt/group-oom/container.py"],
                },
                "HostConfig": {
                    "NetworkMode": "none",
                    "ReadonlyRootfs": True,
                    "CapDrop": ["ALL"],
                    "CapAdd": list(cap_add),
                    "SecurityOpt": ["no-new-privileges:true"],
                    "CgroupnsMode": "host",
                    "PidMode": "private",
                    "PidsLimit": 32,
                    "NanoCpus": 1_000_000_000,
                    "Memory": 8 * 1024**3,
                    "MemorySwap": 8 * 1024**3,
                    "Tmpfs": {"/tmp": "rw,size=16m"},
                    "Privileged": False,
                    "AutoRemove": False,
                },
                "Mounts": [
                    {
                        "Type": "bind",
                        "Source": "/sys/fs/cgroup",
                        "Destination": "/host-cgroup",
                        "RW": True,
                    }
                ],
                "State": {"Running": running, "ExitCode": exit_code, "OOMKilled": oom_killed},
            }
        ]
    )


def inner_json(case_id: str, schema: str, clean: bool = True) -> str:
    classification = {
        "exact_profile": "profile_accepted",
        "group_zero_refused": "typed_refusal",
        "small_group_oom": "oom_observed_inner_pending_outer",
    }[case_id]
    return (
        json.dumps(
            {
                "schema": schema,
                "startup_identity": {
                    "task_id": container_module.TASK_ID,
                    "expected_container_id": FAKE_ID,
                    "case_id": case_id,
                },
                "outcome": {
                    "status": "inner_complete" if clean else "failed_custody",
                    "classification": classification,
                    "cleanup_complete": clean,
                    "failures": [] if clean else [{"code": "incomplete_required_cleanup"}],
                },
            },
            sort_keys=True,
        )
        + "\n"
    )


def command_result(
    argv: Sequence[str],
    stdin: bytes | None,
    *,
    stdout: str = "",
    stderr: str = "",
    exit_code: int = 0,
    timed_out: bool = False,
) -> host_module.CommandResult:
    return host_module.CommandResult(
        argv=tuple(argv),
        started_at_UTC="2026-09-09T00:00:00+00:00",
        ended_at_UTC="2026-09-09T00:00:00.001000+00:00",
        exit_code=exit_code,
        stdout=stdout,
        stderr=stderr,
        timed_out=timed_out,
        timeout_seconds=60.0,
        wall_seconds=0.001,
        stdin_bytes=len(stdin or b""),
        stdin_sha256=hashlib.sha256(stdin).hexdigest() if stdin is not None else None,
        process_pid=None,
        process_group_id=None,
        terminal_observed=True,
    )


class FixedDockerTransport:
    """Injected Docker command results; no command reaches a subprocess."""

    def __init__(self, case_id: str, schema: str, *, nonce: str = "1" * 12, malformed: bool = False) -> None:
        self.case_id = case_id
        self.schema = schema
        self.nonce = nonce
        self.malformed = malformed
        self.inspect_count = 0
        self.calls: list[tuple[tuple[str, ...], bytes | None]] = []

    def run(self, argv: Sequence[str], stdin: bytes | None, timeout_seconds: float) -> host_module.CommandResult:
        argv = tuple(argv)
        self.calls.append((argv, stdin))
        action = argv[3]
        if action == "image":
            return command_result(argv, stdin, stdout=image_json())
        if action == "create":
            return command_result(argv, stdin, stdout=FAKE_ID + "\n")
        if action == "cp":
            require(stdin is not None, "helper archive missing")
            return command_result(argv, stdin)
        if action == "inspect":
            self.inspect_count += 1
            return command_result(argv, stdin, stdout=container_json(nonce=self.nonce))
        if action == "start":
            text = "{" if self.malformed else inner_json(self.case_id, self.schema)
            return command_result(argv, stdin, stdout=text)
        if action == "logs":
            return command_result(argv, stdin, stdout=inner_json(self.case_id, self.schema))
        if action == "kill":
            return command_result(argv, stdin, stdout=FAKE_ID + "\n")
        if action == "rm":
            return command_result(argv, stdin, stdout=FAKE_ID + "\n")
        raise AssertionError(argv)


class ModelCgroups:
    """A deterministic cgroup-v2 semantic model, never a live cgroup adapter."""

    def __init__(self, *, strict_cleanup_order: bool = False, lose_supervisor_membership: bool = False) -> None:
        self.root = f"docker/{FAKE_ID}"
        self.supervisor = f"{self.root}/guard-supervisor"
        self.worker = f"{self.root}/guard-worker"
        self.strict_cleanup_order = strict_cleanup_order
        self.lose_supervisor_membership = lose_supervisor_membership
        self.children: dict[str, list[str]] = {self.root: []}
        self.members: dict[str, list[int]] = {self.root: [SUPERVISOR_PID]}
        self.files: dict[str, dict[str, str]] = {
            self.root: {
                "cgroup.type": "domain",
                "cgroup.controllers": "memory",
                "cgroup.subtree_control": "",
                "cgroup.procs": str(SUPERVISOR_PID),
                "cgroup.events": "populated 1",
                "memory.events": "oom 0\noom_kill 0\noom_group_kill 0",
                "memory.current": "0",
                "memory.peak": "0",
                "cpu.stat": "usage_usec 0",
            }
        }
        self.operations: list[str] = []

    def open_verified_container_root(self, expected_container_id: str) -> str:
        require(expected_container_id == FAKE_ID, "wrong id")
        return self.root

    def relative_path(self, handle: str) -> str:
        return handle

    def mount_facts(self, handle: str) -> Mapping[str, Any]:
        return {
            "system": "Linux",
            "filesystem_type": "cgroup2",
            "magic": supervisor_module.CGROUP2_SUPER_MAGIC,
            "mount_point": "/host-cgroup",
            "read_write": True,
            "source": "cgroup2",
        }

    def read_text(self, directory: str, filename: str) -> str:
        if filename == "cgroup.procs":
            return "\n".join(str(pid) for pid in self.members.get(directory, []))
        if filename == "cgroup.events":
            return f"populated {int(self.child_is_populated(directory))}"
        return self.files[directory][filename]

    def write_text(self, directory: str, filename: str, value: str) -> None:
        self.operations.append(f"write:{directory}:{filename}:{value}")
        if filename == "cgroup.subtree_control":
            self.files[directory][filename] = "memory" if value == "+memory" else ""
        else:
            self.files[directory][filename] = value

    def create_child(self, parent: str, name: str) -> str:
        child = f"{parent}/{name}"
        self.operations.append(f"create:{child}")
        self.children[parent].append(name)
        self.children[child] = []
        self.members[child] = []
        self.files[child] = {
            "cgroup.type": "domain",
            "cgroup.controllers": "memory",
            "cgroup.subtree_control": "",
            "cgroup.procs": "",
            "cgroup.events": "populated 0",
            "memory.events": "oom 0\noom_kill 0\noom_group_kill 0",
            "memory.current": "0",
            "memory.peak": "0",
            "cpu.stat": "usage_usec 0",
            "memory.max": "max",
            "memory.swap.max": "max",
            "memory.oom.group": "0",
        }
        return child

    def list_children(self, directory: str) -> Sequence[str]:
        return tuple(self.children.get(directory, ()))

    def list_direct_members(self, directory: str) -> Sequence[int]:
        return tuple(self.members.get(directory, ()))

    def move_pid(self, directory: str, pid: int) -> None:
        self.operations.append(f"move:{pid}:{directory}")
        if (
            self.strict_cleanup_order
            and directory == self.root
            and self.files[self.root]["cgroup.subtree_control"] == "memory"
        ):
            raise supervisor_module.GuardError("cgroup_no_internal_process", "memory delegated")
        for values in self.members.values():
            while pid in values:
                values.remove(pid)
        if self.lose_supervisor_membership and directory == self.supervisor and pid == SUPERVISOR_PID:
            return
        self.members[directory].append(pid)

    def child_is_populated(self, directory: str) -> bool:
        if self.members.get(directory):
            return True
        prefix = directory + "/"
        return any(values for path, values in self.members.items() if path.startswith(prefix))

    def remove_empty_child(self, parent: str, name: str) -> None:
        child = f"{parent}/{name}"
        self.operations.append(f"remove:{child}")
        if self.child_is_populated(child):
            raise supervisor_module.GuardError("refuse_remove_populated_cgroup", name)
        self.children[parent].remove(name)
        self.children.pop(child, None)
        self.members.pop(child, None)
        self.files.pop(child, None)

    def close_handle(self, directory: str) -> None:
        self.operations.append(f"close:{directory}")


class FixedClock:
    def __init__(self) -> None:
        self.value = 0.0

    def utc_now(self) -> str:
        self.value += 0.001
        return f"2026-09-09T00:00:{self.value:06.3f}+00:00"

    def monotonic(self) -> float:
        self.value += 0.001
        return self.value


class ModelProcesses:
    def __init__(self, cgroups: ModelCgroups, *, migration_failure: bool = False) -> None:
        self.cgroups = cgroups
        self.child = supervisor_module.ChildHandle(WORKER_PID, "owned-worker")
        self.forked = False
        self.released = False
        self.finalized = False
        self.finalize_calls = 0
        self.migration_failure = migration_failure

    def supervisor_pid(self) -> int:
        return SUPERVISOR_PID

    def fork_paused(self, action: Any, inherited_writable_dirs: Sequence[Any]) -> Any:
        self.forked = True
        self.cgroups.members[self.cgroups.supervisor].append(WORKER_PID)
        return self.child

    def release(self, child: Any) -> None:
        self.released = True

    def confirm_membership(self, child: Any, auxiliary_pid: int) -> None:
        raise AssertionError("not used in exact-profile model")

    def wait_terminal(self, child: Any, timeout_seconds: float, event_observer: Any = None, poll_observer: Any = None) -> Any:
        require(self.released, "worker not released")
        for values in self.cgroups.members.values():
            while WORKER_PID in values:
                values.remove(WORKER_PID)
        self.finalized = True
        events = (
            {"event": "privilege_drop_verified", "uid": 65534, "gid": 65534, "capabilities_cleared": True, "oom_score_adj": 0},
            {"event": "worker_membership_readback", "pid": WORKER_PID, "direct_members": [WORKER_PID]},
            {"event": "profile_accepted", "profile": {"memory.max": str(8 * 1024**3), "memory.swap.max": "0", "memory.oom.group": "1"}},
        )
        return supervisor_module.WorkerTerminal(
            exit_code=0,
            signal=None,
            watchdog=False,
            events=events,
            effective_uid=65534,
            effective_gid=65534,
            capabilities_cleared=True,
            oom_score_adj=0,
            auxiliary_ready=False,
            auxiliary_children=0,
            allocations_started=0,
            report_complete=True,
            owned_pid=WORKER_PID,
            reaped=True,
            descriptors_closed=True,
        )

    def finalize_owned_child(self, child: Any, terminate: bool) -> Mapping[str, Any]:
        self.finalize_calls += 1
        for values in self.cgroups.members.values():
            while WORKER_PID in values:
                values.remove(WORKER_PID)
        self.finalized = True
        return {"pid": WORKER_PID, "reaped": True, "descriptors_closed": True, "report_complete": True}

    def custody_record(self, child: Any) -> Mapping[str, Any] | None:
        return None

    def active_owned_children(self) -> Sequence[int]:
        return () if self.finalized or not self.forked else (WORKER_PID,)


class FixtureRuntime:
    def __init__(self, report: Any, await_membership: Any) -> None:
        self._report = report
        self._await_membership = await_membership

    def emit(self, event: Mapping[str, Any]) -> None:
        self._report(event)

    def await_membership_verification(self, pid: int) -> None:
        self._await_membership(pid)


def fixture_factory(report: Any, inherited: Any, await_membership: Any, close_in_auxiliary: Any) -> FixtureRuntime:
    return FixtureRuntime(report, await_membership)


Case = tuple[str, Callable[[], Mapping[str, Any] | None]]


def cases() -> list[Case]:
    result: list[Case] = []

    def add(name: str) -> Callable[[Callable[[], Mapping[str, Any] | None]], Callable[[], Mapping[str, Any] | None]]:
        def decorate(function: Callable[[], Mapping[str, Any] | None]) -> Callable[[], Mapping[str, Any] | None]:
            result.append((name, function))
            return function
        return decorate

    @add("all_three_production_sources_parse")
    def _() -> Mapping[str, Any]:
        paths = [SOURCE / name for name in ("supervisor.py", "container.py", "host.py")]
        for path in paths:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        return {"source_sha256": {path.name: sha256(path) for path in paths}}

    @add("frozen_capability_profile_has_no_kill")
    def _() -> Mapping[str, Any]:
        plan = container_module.planned_container()
        require(plan.cap_drop == ("ALL",), "cap-drop changed")
        require(plan.cap_add == ("SETUID", "SETGID"), "cap-add changed")
        require("KILL" not in plan.cap_add and "CAP_KILL" not in plan.cap_add, "kill capability added")
        argv = host_module.DockerHostAdapter._create_argv(object(), "task-name", "1" * 12)
        require(argv.count("--cap-add") == 2 and "KILL" not in argv and "CAP_KILL" not in argv, "host argv adds kill")
        return {"cap_drop": list(plan.cap_drop), "cap_add": list(plan.cap_add)}

    @add("container_and_host_schema_literals_diverge")
    def _() -> Mapping[str, Any]:
        container_text = (SOURCE / "container.py").read_text(encoding="utf-8")
        host_text = (SOURCE / "host.py").read_text(encoding="utf-8")
        emitted = "crypto.autoresearch.group_oom_container_result.v2"
        required_schema = "crypto.autoresearch.group_oom_native_container_result.v1"
        require(emitted in container_text and required_schema in host_text and emitted != required_schema, "schema break absent")
        return {"observation": "breaking_counterexample", "container_emits": emitted, "host_requires": required_schema}

    @add("production_container_schema_is_rejected_by_host")
    def _() -> Mapping[str, Any]:
        schema = "crypto.autoresearch.group_oom_container_result.v2"
        transport = FixedDockerTransport("exact_profile", schema)
        hashes = {name: sha256(SOURCE / name) for name in host_module.HELPERS}
        outcome = host_module.DockerHostAdapter(transport, SOURCE, hashes, lambda: "1" * 12).run_case("exact_profile")
        actions = [argv[3] for argv, _ in transport.calls]
        require(outcome.status == "failed", "mismatched schema accepted")
        require(outcome.primary_failure and outcome.primary_failure["code"] == "inner_report_schema_mismatch", "wrong failure")
        require(outcome.exact_container_removed and "kill" in actions and "rm" in actions, "outer containment incomplete")
        return {"observation": "breaking_counterexample", "primary_failure": outcome.primary_failure, "actions": actions}

    @add("producer_fixture_schema_masks_host_break")
    def _() -> Mapping[str, Any]:
        schema = "crypto.autoresearch.group_oom_native_container_result.v1"
        transport = FixedDockerTransport("exact_profile", schema)
        hashes = {name: sha256(SOURCE / name) for name in host_module.HELPERS}
        outcome = host_module.DockerHostAdapter(transport, SOURCE, hashes, lambda: "1" * 12).run_case("exact_profile")
        require(outcome.status == "complete", "legacy fixture no longer accepted")
        return {"observation": "proves_too_much_control", "accepted_fixture_schema": schema}

    @add("wrong_nonce_inspection_is_accepted")
    def _() -> Mapping[str, Any]:
        observed = container_module.inspection_from_docker_json(
            container_json(nonce="2" * 12), image_json(), FAKE_ID
        )
        container_module.require_inspection_matches(observed, FAKE_ID, IMAGE_ID)
        require(observed.labels.get("crypto.autoresearch.nonce") == "2" * 12, "wrong fixture")
        return {"observation": "breaking_counterexample", "generated_nonce": "1" * 12, "accepted_nonce": "2" * 12}

    @add("wrong_container_id_is_rejected")
    def _() -> None:
        expect_error(
            lambda: container_module.inspection_from_docker_json(
                container_json(container_id="c" * 64), image_json(), FAKE_ID
            ),
            container_module.ContainerBindingError,
        )

    @add("missing_setgid_is_rejected")
    def _() -> None:
        inspection = container_module.inspection_from_docker_json(
            container_json(cap_add=("SETUID",)), image_json(), FAKE_ID
        )
        expect_error(
            lambda: container_module.require_inspection_matches(inspection, FAKE_ID, IMAGE_ID),
            container_module.ContainerBindingError,
        )

    @add("helper_archive_contains_only_two_pinned_sources")
    def _() -> Mapping[str, Any]:
        archive, hashes = host_module._tar_helpers(
            SOURCE, {name: sha256(SOURCE / name) for name in host_module.HELPERS}
        )
        with tarfile.open(fileobj=BytesIO(archive), mode="r:") as handle:
            members = sorted(handle.getnames())
        require(members == ["group-oom/container.py", "group-oom/supervisor.py"], "unexpected helper member")
        return {"members": members, "hashes": hashes, "archive_sha256": hashlib.sha256(archive).hexdigest()}

    @add("malformed_inner_report_triggers_exact_outer_cleanup")
    def _() -> Mapping[str, Any]:
        transport = FixedDockerTransport("small_group_oom", "unused", malformed=True)
        hashes = {name: sha256(SOURCE / name) for name in host_module.HELPERS}
        outcome = host_module.DockerHostAdapter(transport, SOURCE, hashes, lambda: "1" * 12).run_case("small_group_oom")
        actions = [argv[3] for argv, _ in transport.calls]
        require(outcome.status == "failed" and outcome.exact_container_removed, "malformed report cleanup failed")
        require(outcome.primary_failure and outcome.primary_failure["code"] == "inner_report_malformed_or_truncated", "primary lost")
        require("kill" in actions and "inspect" in actions and "logs" in actions and "rm" in actions, "cleanup transcript incomplete")
        require(all(row.get("container_id") == FAKE_ID for row in outcome.cleanup), "cleanup escaped exact ID")
        return {"primary_failure": outcome.primary_failure, "actions": actions}

    @add("cgroup_v2_cleanup_order_refuses_move_before_disable")
    def _() -> Mapping[str, Any]:
        cgroups = ModelCgroups(strict_cleanup_order=True)
        processes = ModelProcesses(cgroups)
        outcome = supervisor_module.GroupOomSupervisor(cgroups, processes, FixedClock()).run(
            supervisor_module.SupervisorRequest.fixed("exact_profile", FAKE_ID)
        )
        move = f"move:{SUPERVISOR_PID}:{cgroups.root}"
        disable = f"write:{cgroups.root}:cgroup.subtree_control:-memory"
        require(move in cgroups.operations and disable in cgroups.operations, "cleanup actions absent")
        require(cgroups.operations.index(move) < cgroups.operations.index(disable), "source ordering changed")
        require(outcome.status == "failed_custody" and not outcome.cleanup_complete, "kernel-faithful refusal not retained")
        return {
            "observation": "breaking_counterexample",
            "primary_classification_before_cleanup": outcome.classification,
            "final_status": outcome.status,
            "cleanup_order": [move, disable],
            "cleanup_failures": [row for row in outcome.cleanup if not row["ok"]],
        }

    @add("missing_supervisor_membership_readback_can_complete")
    def _() -> Mapping[str, Any]:
        cgroups = ModelCgroups(lose_supervisor_membership=True)
        processes = ModelProcesses(cgroups)
        outcome = supervisor_module.GroupOomSupervisor(cgroups, processes, FixedClock()).run(
            supervisor_module.SupervisorRequest.fixed("exact_profile", FAKE_ID)
        )
        require(outcome.status == "inner_complete" and outcome.cleanup_complete, "known-invalid object did not pass")
        require(not any(row.get("step") == "supervisor_membership_readback" for row in outcome.transcript), "readback now exists")
        return {
            "observation": "breaking_counterexample",
            "accepted_without_supervisor_membership": True,
            "inner_supervisor_evidence": outcome.inner_supervisor_evidence,
        }

    @add("migration_failure_finalizes_known_worker")
    def _() -> Mapping[str, Any]:
        cgroups = ModelCgroups()
        processes = ModelProcesses(cgroups)
        original = cgroups.move_pid
        def move(directory: str, pid: int) -> None:
            if directory == cgroups.worker and pid == WORKER_PID:
                raise supervisor_module.GuardError("injected_migration_failure")
            original(directory, pid)
        cgroups.move_pid = move  # type: ignore[method-assign]
        outcome = supervisor_module.GroupOomSupervisor(cgroups, processes, FixedClock()).run(
            supervisor_module.SupervisorRequest.fixed("exact_profile", FAKE_ID)
        )
        require(outcome.failure_code == "injected_migration_failure", "primary migration failure lost")
        require(processes.finalize_calls == 1 and not processes.active_owned_children(), "worker not finalized")
        return {"historical_finding": "F-03", "finalize_calls": processes.finalize_calls}

    @add("list_children_stat_error_is_silently_skipped")
    def _() -> Mapping[str, Any]:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            (base / "foreign").mkdir()
            fd = os.open(base, os.O_RDONLY | os.O_DIRECTORY)
            handle = supervisor_module.DirectoryHandle(
                fd, f"docker/{FAKE_ID}", 1, 1,
                supervisor_module.MountFacts("Linux", "cgroup2", supervisor_module.CGROUP2_SUPER_MAGIC, td, True, "cgroup2")
            )
            original_stat = supervisor_module.os.stat
            def failing_stat(path: Any, *args: Any, **kwargs: Any) -> Any:
                if path == "foreign":
                    raise PermissionError("injected unreadable child")
                return original_stat(path, *args, **kwargs)
            try:
                with mock.patch.object(supervisor_module.os, "stat", side_effect=failing_stat):
                    children = supervisor_module.DescriptorCgroupTransport.list_children(object(), handle)
            finally:
                os.close(fd)
        require(children == [], "stat error no longer skipped")
        return {"observation": "breaking_counterexample", "existing_child": "foreign", "reported_children": children}

    @add("descriptor_symlink_component_is_refused")
    def _() -> None:
        class MountVerifier:
            def verify(self, fd: int, mount: str) -> Any:
                return supervisor_module.MountFacts("Linux", "cgroup2", supervisor_module.CGROUP2_SUPER_MAGIC, mount, True, "cgroup2")
        class Membership:
            def own_relative_path(self, expected: str) -> str:
                return f"docker/{FAKE_ID}"
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            target = base / "target"
            target.mkdir()
            (base / "docker").symlink_to(target, target_is_directory=True)
            transport = supervisor_module.DescriptorCgroupTransport(td, MountVerifier(), Membership())
            expect_error(lambda: transport.open_verified_container_root(FAKE_ID), OSError)

    @add("descriptor_create_open_failure_rolls_back")
    def _() -> None:
        with tempfile.TemporaryDirectory() as td:
            fd = os.open(td, os.O_RDONLY | os.O_DIRECTORY)
            handle = supervisor_module.DirectoryHandle(
                fd, f"docker/{FAKE_ID}", 1, 1,
                supervisor_module.MountFacts("Linux", "cgroup2", supervisor_module.CGROUP2_SUPER_MAGIC, td, True, "cgroup2")
            )
            transport = supervisor_module.DescriptorCgroupTransport(td)
            try:
                with mock.patch.object(transport, "_open_child", side_effect=OSError("injected")):
                    expect_error(lambda: transport.create_child(handle, "guard-worker"), OSError)
                require(not (Path(td) / "guard-worker").exists(), "partial child remains")
            finally:
                os.close(fd)

    @add("descriptor_partial_and_interrupted_write_completes")
    def _() -> None:
        read_fd, write_fd = os.pipe()
        original = os.write
        calls = 0
        def partial(fd: int, payload: bytes) -> int:
            nonlocal calls
            calls += 1
            if calls == 1:
                raise InterruptedError()
            if calls == 2:
                return original(fd, payload[:1])
            return original(fd, payload)
        try:
            with mock.patch.object(supervisor_module.os, "write", side_effect=partial):
                supervisor_module.DescriptorCgroupTransport._write_all(write_fd, b"abc", "partial")
            os.close(write_fd)
            write_fd = -1
            require(os.read(read_fd, 3) == b"abc" and calls >= 3, "partial write not completed")
        finally:
            if write_fd >= 0:
                os.close(write_fd)
            os.close(read_fd)

    @add("counter_parser_rejects_duplicate_and_negative")
    def _() -> None:
        expect_error(lambda: supervisor_module._parse_events("oom 1\noom 2"), supervisor_module.GuardError, "malformed_counter_file")
        expect_error(lambda: supervisor_module._parse_events("oom -1"), supervisor_module.GuardError, "negative_counter_value")

    @add("counter_delta_rejects_decrease_and_missing")
    def _() -> None:
        expect_error(
            lambda: supervisor_module.GroupOomSupervisor._counter_delta(
                {"memory.events": "oom_kill 3\noom_group_kill 2"},
                {"memory.events": "oom_kill 2\noom_group_kill 2"},
            ),
            supervisor_module.GuardError,
            "oom_counter_decreased",
        )
        expect_error(
            lambda: supervisor_module.GroupOomSupervisor._counter_delta(
                {"memory.events": "oom_kill 0"}, {"memory.events": "oom_kill 1"}
            ),
            supervisor_module.GuardError,
            "missing_required_oom_counter",
        )

    @add("group_zero_control_refuses_before_stress")
    def _() -> Mapping[str, Any]:
        events: list[Mapping[str, Any]] = []
        class Runtime:
            def bootstrap_after_migration(self) -> None: pass
            def read_profile(self) -> Mapping[str, str]:
                return {"memory.max": str(8 * 1024**3), "memory.swap.max": "0", "memory.oom.group": "0"}
            def read_membership(self) -> Sequence[int]: return (WORKER_PID,)
            def emit(self, event: Mapping[str, Any]) -> None: events.append(dict(event))
            def run_fixed_small_group_oom(self) -> int: raise AssertionError("stress reached")
        with mock.patch.object(supervisor_module.os, "getpid", return_value=WORKER_PID):
            code = supervisor_module._worker_action(
                "group_zero_refused", supervisor_module.GuardProfile(8 * 1024**3, 0, 1)
            )(Runtime())
        require(code == 42 and not any(row.get("event") == "before_allocation" for row in events), "group-zero did not refuse")
        return {"exit_code": code, "events": events}

    @add("worker_membership_mismatch_blocks_body")
    def _() -> None:
        class Runtime:
            def bootstrap_after_migration(self) -> None: pass
            def read_profile(self) -> Mapping[str, str]: return {"memory.max": "1", "memory.swap.max": "0", "memory.oom.group": "1"}
            def read_membership(self) -> Sequence[int]: return (WORKER_PID, WORKER_PID + 1)
            def emit(self, event: Mapping[str, Any]) -> None: pass
            def run_fixed_small_group_oom(self) -> int: raise AssertionError("body reached")
        with mock.patch.object(supervisor_module.os, "getpid", return_value=WORKER_PID):
            expect_error(
                lambda: supervisor_module._worker_action(
                    "exact_profile", supervisor_module.GuardProfile(8 * 1024**3, 0, 1)
                )(Runtime()),
                supervisor_module.GuardError,
                "worker_membership_readback_mismatch",
            )

    @add("canonical_sigkill_name")
    def _() -> Mapping[str, Any]:
        observed = supervisor_module.PosixProcessTransport._signal_name(-signal.SIGKILL)
        require(observed == "SIGKILL", "numeric signal name retained")
        return {"historical_finding": "F-02", "observed": observed}

    @add("fork_setup_failure_closes_all_descriptors")
    def _() -> Mapping[str, Any]:
        transport = supervisor_module.PosixProcessTransport(fixture_factory)
        with ExitStack() as stack:
            stack.enter_context(mock.patch.object(supervisor_module.os, "pipe", side_effect=[(10, 11), (12, 13)]))
            stack.enter_context(mock.patch.object(supervisor_module.os, "fork", side_effect=OSError("fork")))
            closed = stack.enter_context(mock.patch.object(supervisor_module.PosixProcessTransport, "_close_quiet"))
            expect_error(lambda: transport.fork_paused(lambda runtime: 0, ()), OSError)
        values = sorted(call.args[0] for call in closed.call_args_list)
        require(values == [10, 11, 12, 13], "fork descriptors leaked")
        return {"historical_finding": "F-07", "closed_descriptors": values}

    @add("malformed_and_truncated_reports_refused")
    def _() -> None:
        expect_error(lambda: supervisor_module.PosixProcessTransport._decode_line(b"{"), supervisor_module.GuardError, "malformed_worker_report_line")
        read_fd, write_fd = os.pipe()
        transport = supervisor_module.PosixProcessTransport(fixture_factory)
        child = supervisor_module.ChildHandle(999999, "truncated")
        state = supervisor_module._PosixChildState(
            write_fd, read_fd, child.pid, released=True, buffer=bytearray(b"{"), report_eof=True, wait_status=0, reaped=True
        )
        transport._children[child.token] = state
        expect_error(lambda: transport._finish_state(child, state), supervisor_module.GuardError, "truncated_worker_report")
        custody = transport.custody_record(child)
        require(custody and custody["descriptors_closed"] and child.token not in transport._children, "truncated report state leaked")

    @add("real_posix_large_report_drain_and_reap")
    def _() -> Mapping[str, Any]:
        started = time.monotonic()
        payload = "x" * 131072
        transport = supervisor_module.PosixProcessTransport(fixture_factory)
        child = transport.fork_paused(lambda runtime: (runtime.emit({"event": "fixture", "payload": payload}) or 0), ())
        transport.release(child)
        terminal = transport.wait_terminal(child, 2.0)
        lifetime = time.monotonic() - started
        require(terminal.exit_code == 0 and terminal.reaped and terminal.descriptors_closed and terminal.report_complete, "large report custody failed")
        require(not transport.active_owned_children() and lifetime <= MAX_CHILD_LIFETIME_SECONDS, "large report child escaped")
        return {
            "process_starts": 1,
            "fixture_pids": [child.pid],
            "terminal_statuses": [asdict(terminal)],
            "payload_bytes": len(payload),
            "max_concurrent": 1,
            "child_lifetime_seconds": lifetime,
        }

    @add("real_posix_membership_barrier")
    def _() -> Mapping[str, Any]:
        started = time.monotonic()
        transport = supervisor_module.PosixProcessTransport(fixture_factory)
        def action(runtime: Any) -> int:
            auxiliary = os.getpid() + 100000
            runtime.emit({"event": "auxiliary_ready", "pid": auxiliary})
            runtime.await_membership_verification(auxiliary)
            return 0
        child = transport.fork_paused(action, ())
        transport.release(child)
        def observer(events: tuple[Mapping[str, Any], ...]) -> None:
            for event in events:
                if event.get("event") == "auxiliary_ready":
                    transport.confirm_membership(child, int(event["pid"]))
        terminal = transport.wait_terminal(child, 2.0, observer)
        lifetime = time.monotonic() - started
        names = [row["event"] for row in terminal.events]
        require(names.index("auxiliary_ready") < names.index("membership_acknowledged"), "barrier order failed")
        require(terminal.reaped and terminal.descriptors_closed and lifetime <= MAX_CHILD_LIFETIME_SECONDS, "barrier custody failed")
        return {"process_starts": 1, "fixture_pids": [child.pid], "terminal_statuses": [asdict(terminal)], "payload_bytes": 0, "max_concurrent": 1, "child_lifetime_seconds": lifetime}

    @add("real_posix_watchdog_signal_and_reap")
    def _() -> Mapping[str, Any]:
        started = time.monotonic()
        transport = supervisor_module.PosixProcessTransport(fixture_factory)
        child = transport.fork_paused(lambda runtime: (time.sleep(1.0) or 0), ())
        transport.release(child)
        terminal = transport.wait_terminal(child, 0.05)
        lifetime = time.monotonic() - started
        require(terminal.watchdog and terminal.signal == "SIGKILL", "watchdog terminal wrong")
        require(terminal.reaped and terminal.descriptors_closed and lifetime <= MAX_CHILD_LIFETIME_SECONDS, "watchdog custody failed")
        return {"process_starts": 1, "fixture_pids": [child.pid], "terminal_statuses": [asdict(terminal)], "payload_bytes": 0, "max_concurrent": 1, "child_lifetime_seconds": lifetime}

    @add("real_posix_report_read_failure_reaps")
    def _() -> Mapping[str, Any]:
        started = time.monotonic()
        transport = supervisor_module.PosixProcessTransport(fixture_factory)
        child = transport.fork_paused(lambda runtime: (time.sleep(0.2) or 0), ())
        transport.release(child)
        os.close(transport._children[child.token].report_read_fd)
        expect_error(lambda: transport.wait_terminal(child, 1.0), supervisor_module.GuardError, "worker_report_read_failed")
        lifetime = time.monotonic() - started
        custody = transport.custody_record(child)
        require(custody and custody["reaped"] and custody["descriptors_closed"], "report failure custody incomplete")
        require(not transport.active_owned_children() and lifetime <= MAX_CHILD_LIFETIME_SECONDS, "report failure child escaped")
        return {"process_starts": 1, "fixture_pids": [child.pid], "terminal_statuses": [custody], "payload_bytes": 0, "max_concurrent": 1, "child_lifetime_seconds": lifetime}

    @add("real_posix_release_failure_reaps")
    def _() -> Mapping[str, Any]:
        started = time.monotonic()
        transport = supervisor_module.PosixProcessTransport(fixture_factory)
        child = transport.fork_paused(lambda runtime: 0, ())
        os.close(transport._children[child.token].control_write_fd)
        expect_error(lambda: transport.release(child), OSError)
        lifetime = time.monotonic() - started
        custody = transport.custody_record(child)
        require(custody and custody["reaped"] and custody["descriptors_closed"], "release failure custody incomplete")
        require(not transport.active_owned_children() and lifetime <= MAX_CHILD_LIFETIME_SECONDS, "release failure child escaped")
        return {"process_starts": 1, "fixture_pids": [child.pid], "terminal_statuses": [custody], "payload_bytes": 0, "max_concurrent": 1, "child_lifetime_seconds": lifetime}

    @add("producer_final_receipt_has_complete_final_81_only")
    def _() -> Mapping[str, Any]:
        receipt = json.loads(PRODUCER_RECEIPT.read_text(encoding="utf-8"))
        suite = receipt["suite"]
        nested = json.loads(receipt["nested_process_receipt"]["stdout"])
        require(nested == suite, "nested stdout and suite diverge")
        require(suite["fixed_case_execution_count"] == 81 and suite["passed_case_count"] == 81, "final count mismatch")
        require(len(suite["results"]) == 81 and all(row["passed"] for row in suite["results"]), "final rows incomplete")
        outer = receipt["outer_tool_response"]
        require(outer["capture_status"] == "captured_after_terminal_tool_return" and outer["exit_code"] == 0, "outer result incomplete")
        require(receipt["nested_process_receipt"]["terminal_exit_code"] == 0, "nested terminal incomplete")
        children = suite["benign_process_accounting"]
        require(children["actual_starts"] == 5 and len(children["created_pids"]) == 5, "final child count mismatch")
        require(all(row.get("reaped") and row.get("descriptors_closed") for row in children["terminal_statuses"]), "final child custody incomplete")
        return {
            "producer_receipt_sha256": sha256(PRODUCER_RECEIPT),
            "final_cases": 81,
            "final_passes": 81,
            "final_benign_starts": 5,
            "outer_chunk_id": outer["chunk_id"],
            "outer_exit": outer["exit_code"],
            "nested_exit": receipt["nested_process_receipt"]["terminal_exit_code"],
        }

    @add("producer_source_hashes_match_final_snapshot")
    def _() -> Mapping[str, Any]:
        receipt = json.loads(PRODUCER_RECEIPT.read_text(encoding="utf-8"))
        matches = {
            name: sha256(SOURCE / name) == digest
            for name, digest in receipt["source_sha256"].items()
        }
        require(all(matches.values()), "producer final source hash mismatch")
        return {"matches": matches}

    @add("failed_producer_history_remains_incomplete")
    def _() -> Mapping[str, Any]:
        receipt = json.loads(PRODUCER_RECEIPT.read_text(encoding="utf-8"))
        gap = json.loads(GAP_RECORD.read_text(encoding="utf-8"))
        decision = yaml.safe_load(FAILURE_DECISION.read_text(encoding="utf-8"))["coordinator_decision"]
        prior_cases = sum(int(row["fixed_cases"]) for row in receipt["prior_check_attempts"])
        prior_starts = sum(int(row.get("benign_process_starts", 0)) for row in receipt["prior_check_attempts"])
        source_states = decision["terminal_snapshot_authorizations"][0]["source_tasks"]
        require(prior_cases == gap["prior_cases_summary_only"] == 251, "prior case accounting mismatch")
        require(prior_starts == gap["prior_benign_children_summary_only"] == 15, "prior child accounting mismatch")
        require(source_states == [{
            "task_id": SOURCE_TASK_ID,
            "state": "failed",
            "artifact_paths": source_states[0]["artifact_paths"],
            "write_scope": source_states[0]["write_scope"],
        }], "producer not retained failed")
        require(len(gap["missing"]) == 3 and gap["live_guard_or_scientific_executions"] == 0, "gap scope changed")
        return {
            "producer_state": source_states[0]["state"],
            "prior_cases_summary_only": prior_cases,
            "prior_children_summary_only": prior_starts,
            "missing": gap["missing"],
        }

    @add("native_membership_reader_accepts_only_exact_bound_paths")
    def _() -> None:
        class FakePath:
            def __init__(self, value: str) -> None: self.value = value
            def read_text(self, encoding: str) -> str: return f"0::/docker/{FAKE_ID}\n"
        with mock.patch.object(supervisor_module, "Path", FakePath):
            require(supervisor_module.NativeMembershipReader().own_relative_path(FAKE_ID) == f"docker/{FAKE_ID}", "exact membership refused")
        class WrongPath(FakePath):
            def read_text(self, encoding: str) -> str: return "0::/docker/not-the-id\n"
        with mock.patch.object(supervisor_module, "Path", WrongPath):
            expect_error(lambda: supervisor_module.NativeMembershipReader().own_relative_path(FAKE_ID), supervisor_module.GuardError, "own_cgroup_membership_not_exact_container")

    @add("native_mount_verifier_requires_linux")
    def _() -> None:
        with mock.patch.object(supervisor_module.platform, "system", return_value="Darwin"):
            expect_error(lambda: supervisor_module.NativeMountVerifier().verify(7, "/host-cgroup"), supervisor_module.GuardError, "native_linux_required")

    @add("default_imports_and_constructors_are_inert")
    def _() -> None:
        with ExitStack() as stack:
            popen = stack.enter_context(mock.patch.object(subprocess, "Popen", side_effect=AssertionError("process")))
            opened = stack.enter_context(mock.patch.object(supervisor_module.os, "open", side_effect=AssertionError("open")))
            supervisor_module.DescriptorCgroupTransport()
            host_module.SubprocessTransport()
            container_module.planned_container()
        require(not popen.called and not opened.called, "constructor side effect")

    return result


class CaseTimeout(RuntimeError):
    pass


def _alarm(_signum: int, _frame: Any) -> None:
    raise CaseTimeout(f"case exceeded {PER_CASE_SECONDS} seconds")


def verify_bindings() -> list[Mapping[str, Any]]:
    handoff = yaml.safe_load(HANDOFF.read_text(encoding="utf-8"))["handoff"]
    rows = []
    for binding in handoff["source_bindings"]:
        path = REPO / binding["path"]
        actual = sha256(path)
        rows.append({"path": binding["path"], "expected": binding["sha256"], "actual": actual, "matched": actual == binding["sha256"]})
    return rows


def run_suite() -> Mapping[str, Any]:
    began = time.monotonic()
    child_before = resource.getrusage(resource.RUSAGE_CHILDREN)
    definitions = cases()
    require(len(definitions) <= MAX_SUITE_CASES, "suite exceeds 128")
    results: list[Mapping[str, Any]] = []
    signal.signal(signal.SIGALRM, _alarm)
    for case_id, function in definitions:
        started = time.monotonic()
        signal.setitimer(signal.ITIMER_REAL, PER_CASE_SECONDS)
        try:
            detail = function() or {}
            results.append({"id": case_id, "checker_passed": True, "wall_seconds": time.monotonic() - started, **detail})
        except BaseException as exc:
            results.append({"id": case_id, "checker_passed": False, "wall_seconds": time.monotonic() - started, "error_type": type(exc).__name__, "error": str(exc)})
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
        require(time.monotonic() - began <= AGGREGATE_SECONDS, "aggregate wall bound exceeded")
    child_after = resource.getrusage(resource.RUSAGE_CHILDREN)
    bindings = verify_bindings()
    fixture_rows = [row for row in results if row.get("process_starts")]
    starts = sum(int(row.get("process_starts", 0)) for row in fixture_rows)
    pids = [pid for row in fixture_rows for pid in row.get("fixture_pids", [])]
    terminal = [item for row in fixture_rows for item in row.get("terminal_statuses", [])]
    max_concurrent = max([int(row.get("max_concurrent", 0)) for row in fixture_rows] or [0])
    max_payload = max([int(row.get("payload_bytes", 0)) for row in fixture_rows] or [0])
    max_lifetime = max([float(row.get("child_lifetime_seconds", 0.0)) for row in fixture_rows] or [0.0])
    passed = (
        all(row["checker_passed"] for row in results)
        and len(bindings) == 51
        and all(row["matched"] for row in bindings)
        and starts == len(pids) == len(terminal)
        and len(set(pids)) == len(pids)
        and starts <= MAX_BENIGN_STARTS
        and max_concurrent <= MAX_CONCURRENT_CHILDREN
        and max_payload <= MAX_FIXTURE_PAYLOAD_BYTES
        and max_lifetime <= MAX_CHILD_LIFETIME_SECONDS
        and all(row.get("reaped") and row.get("descriptors_closed") for row in terminal)
    )
    return {
        "schema": "crypto.autoresearch.group_oom_native_independent_review_suite.v1",
        "task_id": TASK_ID,
        "source_task_id": SOURCE_TASK_ID,
        "source_only": True,
        "assigned_joint_verdict": "breaks",
        "fixed_case_execution_count": len(results),
        "checker_pass_count": sum(bool(row["checker_passed"]) for row in results),
        "results": results,
        "administrative_source_binding_checks": bindings,
        "benign_process_accounting": {
            "maximum_starts": MAX_BENIGN_STARTS,
            "actual_starts": starts,
            "maximum_concurrent": MAX_CONCURRENT_CHILDREN,
            "actual_maximum_concurrent": max_concurrent,
            "maximum_child_lifetime_seconds": MAX_CHILD_LIFETIME_SECONDS,
            "actual_maximum_child_lifetime_seconds": max_lifetime,
            "maximum_deliberate_payload_bytes": MAX_FIXTURE_PAYLOAD_BYTES,
            "actual_maximum_deliberate_payload_bytes": max_payload,
            "created_pids": pids,
            "terminal_statuses": terminal,
            "all_unique": len(set(pids)) == len(pids),
            "all_reaped": all(row.get("reaped") for row in terminal),
            "all_descriptors_closed": all(row.get("descriptors_closed") for row in terminal),
        },
        "actual_metrics": {
            "suite_wall_seconds": time.monotonic() - began,
            "fixture_child_user_cpu_seconds": child_after.ru_utime - child_before.ru_utime,
            "fixture_child_system_cpu_seconds": child_after.ru_stime - child_before.ru_stime,
            "host_process_peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * (1 if sys.platform == "darwin" else 1024),
        },
        "prohibited_action_accounting": {
            "live_docker_calls": 0,
            "operational_containers_started": 0,
            "live_cgroup_or_mount_accesses": 0,
            "privilege_changes": 0,
            "process_migrations": 0,
            "memory_pressure_actions": 0,
            "scientific_runs": 0,
        },
        "passed": passed,
    }


def resident_bytes(pid: int) -> tuple[int | None, str]:
    if sys.platform.startswith("linux"):
        try:
            for line in Path(f"/proc/{pid}/status").read_text(encoding="ascii").splitlines():
                if line.startswith("VmRSS:"):
                    return int(line.split()[1]) * 1024, "proc_status_vmrss"
        except (FileNotFoundError, ProcessLookupError):
            pass
        return None, "proc_status_unavailable"
    if sys.platform == "darwin":
        class ProcTaskInfo(ctypes.Structure):
            _fields_ = [
                ("virtual_size", ctypes.c_uint64), ("resident_size", ctypes.c_uint64),
                ("total_user", ctypes.c_uint64), ("total_system", ctypes.c_uint64),
                ("threads_user", ctypes.c_uint64), ("threads_system", ctypes.c_uint64),
                ("policy", ctypes.c_int32), ("faults", ctypes.c_int32),
                ("pageins", ctypes.c_int32), ("cow_faults", ctypes.c_int32),
                ("messages_sent", ctypes.c_int32), ("messages_received", ctypes.c_int32),
                ("syscalls_mach", ctypes.c_int32), ("syscalls_unix", ctypes.c_int32),
                ("csw", ctypes.c_int32), ("threadnum", ctypes.c_int32),
                ("numrunning", ctypes.c_int32), ("priority", ctypes.c_int32),
            ]
        info = ProcTaskInfo()
        try:
            libproc = ctypes.CDLL("/usr/lib/libproc.dylib")
            size = libproc.proc_pidinfo(pid, 4, 0, ctypes.byref(info), ctypes.sizeof(info))
            if size == ctypes.sizeof(info):
                return int(info.resident_size), "darwin_proc_pidinfo_resident_size"
        except OSError:
            pass
        return None, "darwin_proc_pidinfo_unavailable"
    return None, "unsupported_platform"


def run_final(receipt_path: Path) -> int:
    expected = EXPECTED_RECEIPT.resolve()
    require(receipt_path.resolve() == expected, "receipt path outside declared output")
    stat_before = os.lstat(receipt_path)
    require(stat_before.st_size == 0 and stat_before.st_nlink == 1, "receipt was not uniquely pre-reserved empty")
    require(not Path(receipt_path).is_symlink(), "receipt reservation is symlink")
    checker_hash = sha256(Path(__file__))
    command = [sys.executable, "-B", str(Path(__file__).resolve()), "--suite-json"]
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    started_at = utc_now()
    began = time.monotonic()
    child_before = resource.getrusage(resource.RUSAGE_CHILDREN)
    peak_worker_rss = 0
    rss_basis = "not_observed"
    memory_watchdog = False
    aggregate_watchdog = False
    polls: list[Mapping[str, Any]] = []
    with tempfile.TemporaryFile() as stdout_file, tempfile.TemporaryFile() as stderr_file:
        process = subprocess.Popen(
            command,
            cwd=str(HERE),
            env=environment,
            stdout=stdout_file,
            stderr=stderr_file,
            start_new_session=True,
        )
        deadline = time.monotonic() + AGGREGATE_SECONDS
        while process.poll() is None:
            rss, basis = resident_bytes(process.pid)
            rss_basis = basis
            if rss is not None:
                peak_worker_rss = max(peak_worker_rss, rss)
                if rss > MEMORY_LIMIT_BYTES:
                    memory_watchdog = True
                    os.killpg(process.pid, signal.SIGKILL)
                    break
            polls.append({"at_UTC": utc_now(), "worker_pid": process.pid, "resident_bytes": rss, "basis": basis, "terminal": False})
            if time.monotonic() >= deadline:
                aggregate_watchdog = True
                os.killpg(process.pid, signal.SIGKILL)
                break
            time.sleep(0.01)
        exit_code = process.wait()
        polls.append({"at_UTC": utc_now(), "worker_pid": process.pid, "resident_bytes": resident_bytes(process.pid)[0], "basis": resident_bytes(process.pid)[1], "terminal": True, "exit_code": exit_code})
        stdout_file.seek(0)
        stderr_file.seek(0)
        stdout = stdout_file.read().decode("utf-8", errors="replace")
        stderr = stderr_file.read().decode("utf-8", errors="replace")
    child_after = resource.getrusage(resource.RUSAGE_CHILDREN)
    ended_at = utc_now()
    try:
        suite = json.loads(stdout)
    except json.JSONDecodeError:
        suite = {"passed": False, "parse_error": True, "stdout": stdout}
    fixed_cases = int(suite.get("fixed_case_execution_count", 0))
    receipt = {
        "schema": "crypto.autoresearch.group_oom_native_independent_review_receipt.v1",
        "task_id": TASK_ID,
        "source_task_id": SOURCE_TASK_ID,
        "status": "review_checks_completed" if exit_code == 0 and suite.get("passed") and not memory_watchdog and not aggregate_watchdog else "review_checks_failed",
        "assigned_joint_verdict": "breaks",
        "source_only": True,
        "authority_commit": AUTHORITY_COMMIT,
        "published_claim_commit": PUBLISHED_CLAIM_COMMIT,
        "source_snapshot": SOURCE_SNAPSHOT,
        "receipt_reservation": {
            "reserved_before_invocation": True,
            "path": str(expected),
            "device": stat_before.st_dev,
            "inode": stat_before.st_ino,
            "link_count": stat_before.st_nlink,
            "size_before_bytes": stat_before.st_size,
        },
        "checker_sha256": checker_hash,
        "source_sha256": {name: sha256(SOURCE / name) for name in ("supervisor.py", "container.py", "host.py")},
        "reservation": {
            "maximum_total_fixed_case_executions": MAX_TOTAL_CASES,
            "prior_fixed_case_executions": 0,
            "complete_suite_maximum_cases": MAX_SUITE_CASES,
            "complete_final_suite_reserved_before_execution": len(cases()),
            "executed_final_suite_case_count": fixed_cases,
            "cumulative_fixed_case_executions": fixed_cases,
            "remaining_fixed_case_capacity": MAX_TOTAL_CASES - fixed_cases,
            "per_case_wall_limit_seconds": PER_CASE_SECONDS,
            "aggregate_executed_check_wall_and_cpu_limit_seconds": AGGREGATE_SECONDS,
            "maximum_workers": 1,
            "memory_limit_bytes": MEMORY_LIMIT_BYTES,
            "maximum_benign_child_starts": MAX_BENIGN_STARTS,
            "maximum_concurrent_benign_children": MAX_CONCURRENT_CHILDREN,
            "maximum_benign_child_lifetime_seconds": MAX_CHILD_LIFETIME_SECONDS,
            "maximum_fixture_payload_bytes": MAX_FIXTURE_PAYLOAD_BYTES,
            "reserved_at_UTC": started_at,
        },
        "nested_process_receipt": {
            "argv": command,
            "cwd": str(HERE),
            "environment": {"PYTHONDONTWRITEBYTECODE": "1"},
            "started_at_UTC": started_at,
            "ended_at_UTC": ended_at,
            "process_pid": process.pid,
            "process_group_id": process.pid,
            "terminal_exit_code": exit_code,
            "terminal_session_id": None,
            "yielded_session_ids": [],
            "stdout_redirected_before_invocation": True,
            "stderr_redirected_before_invocation": True,
            "stdout": stdout,
            "stderr": stderr,
            "timed_out": aggregate_watchdog,
            "memory_watchdog_exceeded": memory_watchdog,
            "timeout_seconds": AGGREGATE_SECONDS,
            "polls": polls,
        },
        "outer_tool_response": {
            "capture_status": "pending_parent_tool_return_patch",
            "chunk_id": None,
            "exit_code": None,
            "session_id": None,
            "wall_time_seconds": None,
            "original_token_count": None,
            "output": None,
            "polls": [],
        },
        "actual_metrics": {
            "wall_seconds": time.monotonic() - began,
            "child_user_cpu_seconds": child_after.ru_utime - child_before.ru_utime,
            "child_system_cpu_seconds": child_after.ru_stime - child_before.ru_stime,
            "nested_worker_peak_rss_bytes": peak_worker_rss,
            "nested_worker_peak_rss_basis": rss_basis,
            "memory_watchdog_exceeded": memory_watchdog,
            "aggregate_watchdog_exceeded": aggregate_watchdog,
            "host_process_peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * (1 if sys.platform == "darwin" else 1024),
        },
        "prohibited_action_accounting": {
            "live_docker_calls": 0,
            "operational_containers_started": 0,
            "live_cgroup_or_mount_accesses": 0,
            "privilege_changes": 0,
            "process_migrations": 0,
            "memory_pressure_actions": 0,
            "scientific_runs": 0,
        },
        "suite": suite,
        "limitations": [
            "The suite uses injected Docker, cgroup, mount and privilege observations; it does not establish live platform behavior.",
            "The current host does not supply a hard 2 GiB address-space sandbox here; the parent-enforced 2 GiB resident-memory watchdog and observed peak are retained.",
            "The producer final 81-case receipt is complete, while the preceding 251 cases and 15 child starts remain summary-only and are not reconstructed.",
        ],
    }
    with receipt_path.open("r+", encoding="utf-8") as output:
        require(output.read() == "", "reserved receipt changed before fill")
        output.seek(0)
        json.dump(receipt, output, indent=2, sort_keys=True, allow_nan=False)
        output.write("\n")
        output.truncate()
    print(
        json.dumps(
            {
                "receipt_path": str(expected),
                "status": receipt["status"],
                "assigned_joint_verdict": "breaks",
                "fixed_case_execution_count": fixed_cases,
                "benign_process_starts": suite.get("benign_process_accounting", {}).get("actual_starts"),
                "nested_terminal_exit_code": exit_code,
            },
            sort_keys=True,
        )
    )
    return 0 if receipt["status"] == "review_checks_completed" else 2


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite-json", action="store_true")
    parser.add_argument("--run-final", action="store_true")
    parser.add_argument("--receipt", type=Path, default=EXPECTED_RECEIPT)
    args = parser.parse_args()
    if args.suite_json == args.run_final:
        parser.error("choose exactly one mode")
    if args.suite_json:
        suite = run_suite()
        print(json.dumps(suite, sort_keys=True, allow_nan=False))
        return 0 if suite["passed"] else 2
    return run_final(args.receipt)


if __name__ == "__main__":
    raise SystemExit(main())
