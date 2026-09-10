"""Fixed source checks and bounded current-user POSIX custody fixtures.

No test calls Docker, opens a real cgroup/mount, changes credentials, migrates a
process, allocates pressure, or executes science.  Five sequential real child
fixtures exercise only the owned pipe/barrier/wait/signal/reap implementation.
"""
from __future__ import annotations

import argparse
from contextlib import ExitStack
from dataclasses import asdict, replace
from datetime import datetime, timezone
import ctypes
import hashlib
from io import BytesIO
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
from types import SimpleNamespace

import container as container_module
import host as host_module
import supervisor as supervisor_module


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
RECEIPT = HERE / "check-receipt.json"
PROTOCOL = HERE / "protocol-binding.json"
MAX_TOTAL_CASES = 512
MAX_SUITE_CASES = 128
MAX_BENIGN_STARTS = 32
MAX_FIXTURE_CHILDREN_CONCURRENT = 2
MAX_FIXTURE_LIFETIME_SECONDS = 3
MAX_FIXTURE_PAYLOAD_BYTES = 1024 * 1024
PER_CASE_SECONDS = 10
AGGREGATE_SECONDS = 1800
MEMORY_LIMIT_BYTES = 2 * 1024 * 1024 * 1024
FAKE_ID = "a" * 64
IMAGE_ID = container_module.PINNED_IMAGE_DIGEST


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class FixedClock:
    def __init__(self) -> None:
        self.value = 100.0

    def utc_now(self) -> str:
        self.value += 0.001
        return f"2026-09-09T00:00:{self.value % 60:09.6f}+00:00"

    def monotonic(self) -> float:
        self.value += 0.001
        return self.value


GOOD_FACTS = {
    "system": "Linux",
    "filesystem_type": "cgroup2",
    "magic": supervisor_module.CGROUP2_SUPER_MAGIC,
    "mount_point": "/host-cgroup",
    "read_write": True,
    "source": "cgroup2",
}


class SyntheticCgroups:
    def __init__(self, faults: set[str] | None = None) -> None:
        self.faults = faults or set()
        self.root = f"docker/{FAKE_ID}"
        self.supervisor = f"{self.root}/guard-supervisor"
        self.worker = f"{self.root}/guard-worker"
        self.files: dict[str, dict[str, str]] = {
            self.root: {
                "cgroup.type": "domain\n",
                "cgroup.controllers": "cpu memory pids\n",
                "cgroup.subtree_control": "",
                "cgroup.procs": "4242\n",
                "cgroup.events": "populated 1\n",
                "memory.events": "oom 0\noom_kill 0\noom_group_kill 0\n",
                "memory.current": "0\n",
                "memory.peak": "0\n",
                "cpu.stat": "usage_usec 0\n",
            }
        }
        self.children: dict[str, list[str]] = {self.root: []}
        self.members: dict[str, list[int]] = {self.root: [4242]}
        self.closed: list[str] = []
        self.polls = 0
        self.worker_terminal_observed = False
        self.trace: list[str] = []
        if "mount_not_linux" in self.faults:
            self.facts = {**GOOD_FACTS, "system": "Darwin"}
        elif "mount_not_cgroup2" in self.faults:
            self.facts = {**GOOD_FACTS, "filesystem_type": "tmpfs", "magic": 0x01021994}
        elif "mount_readonly" in self.faults:
            self.facts = {**GOOD_FACTS, "read_write": False}
        else:
            self.facts = dict(GOOD_FACTS)
        if "missing_memory" in self.faults:
            self.files[self.root]["cgroup.controllers"] = "cpu pids\n"
        if "nonempty_subtree" in self.faults:
            self.files[self.root]["cgroup.subtree_control"] = "memory\n"
        if "unexpected_members" in self.faults:
            self.members[self.root] = [4242, 9999]
        if "preexisting_child" in self.faults:
            self.children[self.root] = ["foreign"]

    def open_verified_container_root(self, expected_container_id: str) -> str:
        self.trace.append("open_root")
        if "wrong_path" in self.faults:
            return "docker"
        return self.root

    def relative_path(self, handle: str) -> str:
        return handle

    def mount_facts(self, handle: str) -> Mapping[str, Any]:
        return self.facts

    def read_text(self, directory: str, filename: str) -> str:
        self.trace.append(f"read:{directory}:{filename}")
        if "poll_failure" in self.faults and directory == self.worker and filename == "memory.events" and self.polls > 0:
            raise supervisor_module.GuardError("injected_counter_poll_failure")
        try:
            return self.files[directory][filename]
        except KeyError as exc:
            raise supervisor_module.GuardError("missing_cgroup_metric", filename) from exc

    def write_text(self, directory: str, filename: str, value: str) -> None:
        self.trace.append(f"write:{directory}:{filename}:{value}")
        if "profile_write_failure" in self.faults and filename == "memory.max":
            raise OSError("injected profile write failure")
        if filename == "cgroup.subtree_control":
            if value == "+memory" and self.members[directory]:
                raise supervisor_module.GuardError("synthetic_no_internal_processes")
            if value == "-memory" and "disable_failure" in self.faults:
                raise OSError("injected delegation disable failure")
            if value == "-memory" and "disable_ignored" in self.faults:
                return
            self.files[directory][filename] = "memory\n" if value == "+memory" else ""
        else:
            self.files[directory][filename] = value + "\n"

    def create_child(self, parent: str, name: str) -> str:
        self.trace.append(f"create:{name}")
        child = f"{parent}/{name}"
        self.children[parent].append(name)
        self.children[child] = []
        self.members[child] = []
        self.files[child] = {
            "cgroup.type": "domain\n",
            "cgroup.controllers": "memory\n",
            "cgroup.subtree_control": "",
            "cgroup.procs": "",
            "cgroup.events": "populated 0\n",
            "memory.events": "oom 5\noom_kill 7\noom_group_kill 3\n",
            "memory.current": "0\n",
            "memory.peak": "0\n",
            "cpu.stat": "usage_usec 0\n",
            "memory.max": "max\n",
            "memory.swap.max": "max\n",
            "memory.oom.group": "0\n",
        }
        return child

    def list_children(self, directory: str) -> Sequence[str]:
        return tuple(self.children[directory])

    def list_direct_members(self, directory: str) -> Sequence[int]:
        if directory == self.supervisor:
            if "supervisor_missing" in self.faults:
                return ()
            if "supervisor_foreign" in self.faults:
                return (4242, 9999)
            if "supervisor_final_missing" in self.faults and self.worker_terminal_observed:
                return ()
        if "membership_mismatch" in self.faults and directory == self.worker and len(self.members[directory]) > 1:
            return (4342,)
        return tuple(self.members[directory])

    def move_pid(self, directory: str, pid: int) -> None:
        self.trace.append(f"move:{pid}:{directory}")
        if "memory" in self.files[directory]["cgroup.subtree_control"].split():
            raise supervisor_module.GuardError("synthetic_no_internal_processes")
        if "migration_failure" in self.faults and directory == self.worker:
            raise supervisor_module.GuardError("injected_migration_failure")
        for members in self.members.values():
            while pid in members:
                members.remove(pid)
        self.members[directory].append(pid)
        self.files[directory]["cgroup.procs"] = "".join(f"{value}\n" for value in self.members[directory])
        self.files[directory]["cgroup.events"] = f"populated {int(bool(self.members[directory]))}\n"

    def child_is_populated(self, directory: str) -> bool:
        if "surviving_worker_member" in self.faults and directory == self.worker:
            return True
        return bool(self.members[directory])

    def remove_empty_child(self, parent: str, name: str) -> None:
        if f"cleanup_failure_{name}" in self.faults:
            raise OSError(f"injected {name} cleanup failure")
        child = f"{parent}/{name}"
        if self.members[child]:
            raise supervisor_module.GuardError("refuse_remove_populated_cgroup")
        self.children[parent].remove(name)
        self.children.pop(child, None)
        self.members.pop(child, None)
        self.files.pop(child, None)

    def close_handle(self, directory: str) -> None:
        self.closed.append(directory)

    def make_terminal(self, case_id: str) -> None:
        self.members[self.worker] = []
        self.files[self.worker]["cgroup.procs"] = ""
        self.files[self.worker]["cgroup.events"] = "populated 0\n"
        if case_id == "small_group_oom":
            if "stale_counters" in self.faults:
                return
            if "missing_counter_key" in self.faults:
                self.files[self.worker]["memory.events"] = "oom 7\noom_kill 9\n"
            elif "low_counter_delta" in self.faults:
                self.files[self.worker]["memory.events"] = "oom 6\noom_kill 8\noom_group_kill 3\n"
            else:
                self.files[self.worker]["memory.events"] = "oom 7\noom_kill 9\noom_group_kill 4\n"


class SyntheticRuntime:
    def __init__(self, cgroups: SyntheticCgroups, report: Callable[[Mapping[str, Any]], None]) -> None:
        self.cgroups = cgroups
        self.report = report

    def bootstrap_after_migration(self) -> None:
        self.emit({"event": "privilege_drop_verified", "uid": 65534, "gid": 65534, "capabilities_cleared": True, "oom_score_adj": 0})

    def read_profile(self) -> Mapping[str, str]:
        return {name: self.cgroups.files[self.cgroups.worker][name].strip() for name in ("memory.max", "memory.swap.max", "memory.oom.group")}

    def read_membership(self) -> Sequence[int]:
        return (4342,)

    def emit(self, event: Mapping[str, Any]) -> None:
        self.report(dict(event))

    def await_membership_verification(self, auxiliary_pid: int) -> None:
        return None

    def run_fixed_small_group_oom(self) -> int:
        raise AssertionError("synthetic process transport owns the small case")


class SyntheticProcesses:
    def __init__(self, cgroups: SyntheticCgroups, case_id: str, faults: set[str] | None = None) -> None:
        self.cgroups = cgroups
        self.case_id = case_id
        self.faults = faults or set()
        self.child = supervisor_module.ChildHandle(4342, "synthetic-owned-worker")
        self.action: Callable[[Any], int] | None = None
        self.events: list[Mapping[str, Any]] = []
        self.released = False
        self.forked = False
        self.confirmed = False
        self.finalized = False
        self.custody: Mapping[str, Any] | None = None

    def supervisor_pid(self) -> int:
        return 4242

    def fork_paused(self, action: Callable[[Any], int], inherited_writable_dirs: Sequence[Any]) -> Any:
        self.action = action
        self.forked = True
        self.cgroups.members[self.cgroups.supervisor].append(self.child.pid)
        return self.child

    def release(self, child: Any) -> None:
        self.released = True

    def confirm_membership(self, child: Any, auxiliary_pid: int) -> None:
        if auxiliary_pid != 4343:
            raise supervisor_module.GuardError("bad_auxiliary")
        self.confirmed = True

    def _privilege(self) -> Mapping[str, Any]:
        return {"event": "privilege_drop_verified", "uid": 65534, "gid": 65534, "capabilities_cleared": True, "oom_score_adj": 0}

    def wait_terminal(self, child: Any, timeout_seconds: float, event_observer: Any = None, poll_observer: Any = None) -> Any:
        if not self.released:
            raise supervisor_module.GuardError("unknown_or_unreleased_child")
        if self.case_id in {"exact_profile", "group_zero_refused"}:
            runtime = SyntheticRuntime(self.cgroups, self.events.append)
            assert self.action is not None
            with mock.patch.object(supervisor_module.os, "getpid", return_value=self.child.pid):
                code = self.action(runtime)
            self.events.append({"event": "worker_exit", "exit_code": code})
            if event_observer:
                event_observer(tuple(self.events))
            exit_code, signal_name = code, None
        else:
            self.events.extend(
                [
                    self._privilege(),
                    {"event": "worker_membership_readback", "pid": 4342, "direct_members": [4342]},
                    {"event": "auxiliary_spawned", "pid": 4343},
                    {"event": "auxiliary_ready", "pid": 4343, "oom_score_adj": 0},
                ]
            )
            self.cgroups.members[self.cgroups.worker] = [4342, 4343]
            if event_observer:
                event_observer(tuple(self.events))
            if not self.confirmed:
                raise supervisor_module.GuardError("membership_not_confirmed")
            later = (
                {"event": "membership_acknowledged", "pid": 4343},
                {"event": "before_allocation", "requested_bytes": 128 * supervisor_module.MIB},
            )
            self.events.extend(later)
            if event_observer:
                event_observer(later)
            for _ in range(3):
                self.cgroups.polls += 1
                if poll_observer:
                    poll_observer()
            exit_code, signal_name = None, "SIGKILL"
        self.cgroups.make_terminal(self.case_id)
        if "bad_signal" in self.faults:
            signal_name = "SIGTERM"
        self.finalized = True
        self.custody = {"pid": child.pid, "reaped": True, "descriptors_closed": True, "report_complete": True, "parent_terminated": False}
        privilege = next((event for event in self.events if event.get("event") == "privilege_drop_verified"), {})
        self.cgroups.worker_terminal_observed = True
        return supervisor_module.WorkerTerminal(
            exit_code=exit_code,
            signal=signal_name,
            watchdog="watchdog" in self.faults,
            events=tuple(self.events),
            effective_uid=privilege.get("uid"),
            effective_gid=privilege.get("gid"),
            capabilities_cleared=privilege.get("capabilities_cleared"),
            oom_score_adj=privilege.get("oom_score_adj"),
            auxiliary_ready=any(row.get("event") == "auxiliary_ready" for row in self.events),
            auxiliary_children=sum(row.get("event") == "auxiliary_spawned" for row in self.events),
            allocations_started=sum(row.get("event") == "before_allocation" for row in self.events),
            report_complete="report_incomplete" not in self.faults,
            owned_pid=child.pid,
            reaped=True,
            descriptors_closed=True,
            parent_terminated="parent_kill" in self.faults,
            manual_kill="parent_kill" in self.faults,
        )

    def finalize_owned_child(self, child: Any, terminate: bool) -> Mapping[str, Any]:
        self.finalized = True
        for members in self.cgroups.members.values():
            while child.pid in members:
                members.remove(child.pid)
        self.custody = self.custody or {"pid": child.pid, "reaped": True, "descriptors_closed": True, "report_complete": True, "parent_terminated": terminate}
        return self.custody

    def custody_record(self, child: Any) -> Mapping[str, Any] | None:
        return self.custody

    def active_owned_children(self) -> Sequence[int]:
        return () if self.finalized or not self.forked else (self.child.pid,)


def run_supervisor(case_id: str, faults: set[str] | None = None) -> tuple[Any, SyntheticCgroups, SyntheticProcesses]:
    faults = faults or set()
    cgroups = SyntheticCgroups(faults)
    processes = SyntheticProcesses(cgroups, case_id, faults)
    outcome = supervisor_module.GroupOomSupervisor(cgroups, processes, FixedClock()).run(
        supervisor_module.SupervisorRequest.fixed(case_id, FAKE_ID)
    )
    return outcome, cgroups, processes


def image_json() -> str:
    return json.dumps([{"Id": IMAGE_ID, "RepoDigests": [f"python@{container_module.PINNED_IMAGE_DIGEST}"], "Os": "linux", "Architecture": "arm64"}])


def container_inspect(running: bool = False, exit_code: int = 0, oom: bool = False, mismatch: str | None = None) -> str:
    cid = FAKE_ID if mismatch != "id" else "b" * 64
    host = {
        "NetworkMode": "none",
        "ReadonlyRootfs": True,
        "CapDrop": ["ALL"],
        "CapAdd": ["SETUID", "SETGID"],
        "SecurityOpt": ["no-new-privileges:true"],
        "CgroupnsMode": "host",
        "PidMode": "private",
        "PidsLimit": 32,
        "NanoCpus": 1000000000,
        "Memory": 8 * 1024**3,
        "MemorySwap": 8 * 1024**3,
        "Tmpfs": {"/tmp": "rw,size=16m"},
        "Privileged": False,
        "AutoRemove": False,
    }
    if mismatch == "cap":
        host["CapAdd"] = ["SETUID"]
    raw = {
        "Id": cid,
        "Image": IMAGE_ID,
        "Config": {
            "Image": container_module.PINNED_IMAGE,
            "Labels": {"crypto.autoresearch.task": container_module.TASK_ID, "crypto.autoresearch.nonce": "1" * 12},
            "User": "0:0",
            "OpenStdin": True,
            "AttachStdin": True,
            "Tty": False,
            "Cmd": ["python3", "-B", "/opt/group-oom/container.py"],
        },
        "HostConfig": host,
        "Mounts": [{"Type": "bind", "Source": "/sys/fs/cgroup", "Destination": "/host-cgroup", "RW": True}],
        "State": {"Running": running, "ExitCode": exit_code, "OOMKilled": oom},
    }
    if mismatch == "nonce":
        raw["Config"]["Labels"]["crypto.autoresearch.nonce"] = "2" * 12
    elif mismatch == "nonce_missing":
        raw["Config"]["Labels"].pop("crypto.autoresearch.nonce")
    return json.dumps([raw])


def inner_json(case_id: str, clean: bool = True) -> str:
    # Use the actual supervisor result and production serializer, not a hand-written wire envelope.
    outcome, _, _ = run_supervisor(case_id)
    data = outcome.as_dict()
    if not clean:
        data["status"] = "failed_custody"
        data["cleanup_complete"] = False
        data["failures"] = [{"code": "incomplete_required_cleanup"}]
    identity = container_module.StartupIdentity(container_module.TASK_ID, FAKE_ID, case_id)
    return json.dumps(container_module.source_result(identity, data), sort_keys=True) + "\n"


def command_result(argv: Sequence[str], stdin: bytes | None, stdout: str = "", stderr: str = "", exit_code: int = 0, timed_out: bool = False) -> Any:
    return host_module.CommandResult(
        argv=tuple(argv),
        started_at_UTC="2026-09-09T00:00:00+00:00",
        ended_at_UTC="2026-09-09T00:00:00.001000+00:00",
        exit_code=exit_code,
        stdout=stdout,
        stderr=stderr,
        timed_out=timed_out,
        timeout_seconds=60,
        wall_seconds=0.001,
        stdin_bytes=len(stdin or b""),
        stdin_sha256=hashlib.sha256(stdin).hexdigest() if stdin is not None else None,
        process_pid=None,
        process_group_id=None,
        terminal_observed=True,
    )


class FixedDockerTransport:
    def __init__(self, case_id: str, fault: str | None = None) -> None:
        self.case_id = case_id
        self.fault = fault
        self.inspect_count = 0
        self.calls: list[tuple[tuple[str, ...], bytes | None]] = []
        self.tar_members: list[str] = []
        self.emitted_stdout: str | None = None

    def run(self, argv: Sequence[str], stdin: bytes | None, timeout_seconds: float) -> Any:
        argv = tuple(argv)
        self.calls.append((argv, stdin))
        action = argv[3]
        if action == "image":
            return command_result(argv, stdin, image_json())
        if action == "create":
            if self.fault == "create":
                return command_result(argv, stdin, stderr="create failed", exit_code=1)
            return command_result(argv, stdin, FAKE_ID + "\n")
        if action == "cp":
            assert stdin is not None
            with tarfile.open(fileobj=BytesIO(stdin), mode="r:") as archive:
                self.tar_members = sorted(archive.getnames())
            return command_result(argv, stdin)
        if action == "inspect":
            self.inspect_count += 1
            if self.inspect_count == 1:
                mismatch = {"inspection": "cap", "nonce": "nonce", "nonce_missing": "nonce_missing"}.get(self.fault)
                return command_result(argv, stdin, container_inspect(mismatch=mismatch))
            if self.fault == "outer_oom" and self.inspect_count == 2:
                return command_result(argv, stdin, container_inspect(False, 137, True))
            return command_result(argv, stdin, container_inspect(False, 0, False))
        if action == "start":
            code, timed_out = 0, False
            if self.fault == "startup_failure":
                self.emitted_stdout = json.dumps(container_module.source_startup_failure(ValueError("controlled startup failure")))
                code = 2
            elif self.fault == "malformed_inner":
                self.emitted_stdout = "{"
            elif self.fault == "attach_timeout":
                self.emitted_stdout = "partial"
                code, timed_out = -9, True
            else:
                data = json.loads(inner_json(self.case_id, clean=self.fault != "inner_cleanup"))
                if self.fault == "wrong_schema":
                    data["schema"] = "crypto.autoresearch.group_oom_native_container_result.v1"
                elif self.fault == "missing_identity":
                    data.pop("startup_identity")
                elif self.fault == "missing_outcome":
                    data.pop("outcome")
                elif self.fault == "false_cleanup":
                    data["outcome"]["cleanup_complete"] = 1
                self.emitted_stdout = json.dumps(data)
            return command_result(argv, stdin, self.emitted_stdout, exit_code=code, timed_out=timed_out)
        if action == "logs":
            if self.fault == "logs":
                return command_result(argv, stdin, stderr="logs failed", exit_code=1)
            # Docker logs replays the producer's emitted bytes; it does not rerun it.
            return command_result(argv, stdin, self.emitted_stdout or "")
        if action == "kill":
            return command_result(argv, stdin, FAKE_ID + "\n")
        if action == "rm":
            if self.fault == "rm":
                return command_result(argv, stdin, stderr="rm failed", exit_code=1)
            return command_result(argv, stdin, FAKE_ID + "\n")
        raise AssertionError(argv)


class FakeMountVerifier:
    def __init__(self, facts: Mapping[str, Any] | None = None) -> None:
        self.facts = facts or GOOD_FACTS
        self.calls = 0

    def verify(self, fd: int, mount: str) -> Any:
        self.calls += 1
        return supervisor_module.MountFacts(**self.facts)


class FakeMembership:
    def __init__(self, path: str = f"docker/{FAKE_ID}") -> None:
        self.path = path

    def own_relative_path(self, expected_container_id: str) -> str:
        return container_module.require_exact_cgroup_relative_path(expected_container_id, self.path)


def make_ordinary_root(base: Path) -> Path:
    root = base / "docker" / FAKE_ID
    root.mkdir(parents=True)
    values = {
        "cgroup.type": "domain\n",
        "cgroup.controllers": "memory\n",
        "cgroup.subtree_control": "",
        "cgroup.procs": "1\n",
        "cgroup.events": "populated 0\n",
        "memory.events": "oom 0\noom_kill 0\noom_group_kill 0\n",
        "memory.current": "0\n",
        "memory.peak": "0\n",
        "cpu.stat": "usage_usec 0\n",
        "memory.max": "max\n",
        "memory.swap.max": "max\n",
        "memory.oom.group": "0\n",
    }
    for name, value in values.items():
        (root / name).write_text(value, encoding="ascii")
    return root


class FixtureRuntime:
    def __init__(self, report: Any, await_membership: Any) -> None:
        self.report = report
        self.await_membership_callback = await_membership

    def emit(self, event: Mapping[str, Any]) -> None:
        self.report(event)

    def await_membership_verification(self, pid: int) -> None:
        self.await_membership_callback(pid)


def fixture_factory(report: Any, inherited: Any, await_membership: Any, close_in_auxiliary: Any) -> Any:
    return FixtureRuntime(report, await_membership)


Case = tuple[str, Callable[[], Mapping[str, Any] | None]]


def cases() -> list[Case]:
    result: list[Case] = []

    def add(name: str) -> Callable[[Callable[[], Mapping[str, Any] | None]], Callable[[], Mapping[str, Any] | None]]:
        def decorate(function: Callable[[], Mapping[str, Any] | None]) -> Callable[[], Mapping[str, Any] | None]:
            result.append((name, function))
            return function
        return decorate

    @add("frozen_profile_exact")
    def _() -> None:
        plan = container_module.planned_container()
        assert plan.image == container_module.PINNED_IMAGE and plan.platform == "linux/arm64"
        assert plan.cap_drop == ("ALL",) and plan.cap_add == ("SETUID", "SETGID")
        assert plan.pid_namespace == "private" and plan.cgroup_namespace == "host"
        assert plan.outer_memory_bytes == plan.outer_memory_swap_total_bytes == 8 * 1024**3

    for name, value in [
        ("id_short", "a" * 63),
        ("id_upper", "A" * 64),
        ("id_bad_char", "a" * 63 + "z"),
        ("id_nonstr", 7),
    ]:
        @add(name)
        def _(value=value) -> None:
            try:
                container_module.require_full_container_id(value)
            except container_module.ContainerBindingError:
                return
            raise AssertionError("unsafe ID accepted")

    for name, path in [
        ("path_absolute", f"/docker/{FAKE_ID}"),
        ("path_parent", "docker"),
        ("path_traversal", f"docker/../{FAKE_ID}"),
        ("path_wrong_root", f"other/{FAKE_ID}"),
        ("path_backslash", f"docker\\{FAKE_ID}"),
    ]:
        @add(name)
        def _(path=path) -> None:
            try:
                container_module.require_exact_cgroup_relative_path(FAKE_ID, path)
            except container_module.ContainerBindingError:
                return
            raise AssertionError("unsafe path accepted")

    @add("inspection_from_actual_json")
    def _() -> None:
        value = container_module.inspection_from_docker_json(container_inspect(), image_json(), FAKE_ID)
        container_module.require_inspection_matches(value, FAKE_ID, IMAGE_ID, "1" * 12)
        assert value.source == "actual_docker_inspect_json"

    for name, changed in [
        ("inspection_id_mismatch", "id"),
        ("inspection_capability_mismatch", "cap"),
    ]:
        @add(name)
        def _(changed=changed) -> None:
            try:
                value = container_module.inspection_from_docker_json(container_inspect(mismatch=changed), image_json(), FAKE_ID)
                container_module.require_inspection_matches(value, FAKE_ID, IMAGE_ID, "1" * 12)
            except container_module.ContainerBindingError:
                return
            raise AssertionError("mismatched inspection accepted")

    for name, raw in [
        ("inspection_malformed_container", "{"),
        ("inspection_ambiguous_container", "[]"),
        ("inspection_malformed_image", "{"),
    ]:
        @add(name)
        def _(name=name, raw=raw) -> None:
            try:
                container_module.inspection_from_docker_json(raw if "container" in name else container_inspect(), raw if "image" in name else image_json(), FAKE_ID)
            except container_module.ContainerBindingError:
                return
            raise AssertionError("malformed inspection accepted")

    @add("startup_identity_exact")
    def _() -> None:
        raw = (json.dumps({"task_id": container_module.TASK_ID, "expected_container_id": FAKE_ID, "case_id": "exact_profile"}) + "\n").encode()
        parsed = container_module.parse_startup_stdin(BytesIO(raw))
        assert parsed.expected_container_id == FAKE_ID

    for name, raw in [
        ("startup_wrong_task", {"task_id": "wrong", "expected_container_id": FAKE_ID, "case_id": "exact_profile"}),
        ("startup_wrong_case", {"task_id": container_module.TASK_ID, "expected_container_id": FAKE_ID, "case_id": "other"}),
        ("startup_extra_field", {"task_id": container_module.TASK_ID, "expected_container_id": FAKE_ID, "case_id": "exact_profile", "extra": 1}),
    ]:
        @add(name)
        def _(raw=raw) -> None:
            try:
                container_module.parse_startup_stdin(BytesIO((json.dumps(raw) + "\n").encode()))
            except container_module.ContainerBindingError:
                return
            raise AssertionError("bad startup accepted")

    @add("startup_truncated")
    def _() -> None:
        try:
            container_module.parse_startup_stdin(BytesIO(b"{}"))
        except container_module.ContainerBindingError:
            return
        raise AssertionError("truncated startup accepted")

    for case_id, classification in [
        ("exact_profile", "profile_accepted"),
        ("group_zero_refused", "typed_refusal"),
        ("small_group_oom", "oom_observed_inner_pending_outer"),
    ]:
        @add(f"supervisor_{case_id}_complete")
        def _(case_id=case_id, classification=classification) -> Mapping[str, Any]:
            outcome, cgroups, processes = run_supervisor(case_id)
            assert outcome.status == "inner_complete" and outcome.classification == classification
            assert outcome.cleanup_complete and processes.finalized and not processes.active_owned_children()
            return {"ordering": [row["step"] for row in outcome.transcript], "counter_polls": len(outcome.counter_polls)}

    @add("supervisor_ordering")
    def _() -> None:
        outcome, _, _ = run_supervisor("exact_profile")
        steps = [row["step"] for row in outcome.transcript]
        wanted = ["worker_profile_written_and_read_before_fork", "worker_forked_behind_barrier", "worker_migrated_before_release", "worker_released_after_profile_and_migration"]
        assert [steps.index(value) for value in wanted] == sorted(steps.index(value) for value in wanted)

    @add("small_membership_before_allocation")
    def _() -> None:
        outcome, _, _ = run_supervisor("small_group_oom")
        steps = [row["step"] for row in outcome.transcript]
        assert steps.index("both_worker_members_verified_before_pressure") < steps.index("worker_terminal_observed")
        events = [row["event"] for row in outcome.terminal["events"]]
        assert events.index("membership_acknowledged") < events.index("before_allocation")

    @add("small_counter_delta_exact")
    def _() -> None:
        outcome, _, _ = run_supervisor("small_group_oom")
        assert outcome.counter_deltas == {"oom_group_kill": 1, "oom_kill": 2}
        assert len(outcome.counter_polls) == 3

    supervisor_failures = [
        ("wrong_path", "exact_profile", {"wrong_path"}, "cgroup_path_refused"),
        ("mount_not_linux", "exact_profile", {"mount_not_linux"}, "cgroup2_mount_not_verified"),
        ("mount_not_cgroup2", "exact_profile", {"mount_not_cgroup2"}, "cgroup2_mount_not_verified"),
        ("mount_readonly", "exact_profile", {"mount_readonly"}, "cgroup_delegation_mount_readonly"),
        ("missing_memory", "exact_profile", {"missing_memory"}, "memory_controller_unavailable"),
        ("nonempty_subtree", "exact_profile", {"nonempty_subtree"}, "subtree_control_not_initially_empty"),
        ("unexpected_members", "exact_profile", {"unexpected_members"}, "unexpected_container_root_members"),
        ("preexisting_child", "exact_profile", {"preexisting_child"}, "preexisting_guard_subgroup"),
        ("migration_cleanup", "exact_profile", {"migration_failure"}, "injected_migration_failure"),
        ("stale_counters", "small_group_oom", {"stale_counters"}, "small_oom_counter_increment_not_met"),
        ("low_counter_delta", "small_group_oom", {"low_counter_delta"}, "small_oom_counter_increment_not_met"),
        ("missing_counter_key", "small_group_oom", {"missing_counter_key"}, "missing_required_oom_counter"),
        ("membership_mismatch", "small_group_oom", {"membership_mismatch"}, "worker_auxiliary_membership_mismatch"),
        ("bad_signal", "small_group_oom", {"bad_signal"}, "small_oom_terminal_not_sigkill"),
        ("watchdog", "small_group_oom", {"watchdog"}, "worker_watchdog"),
        ("parent_kill", "small_group_oom", {"parent_kill"}, "manual_or_watchdog_kill_not_oom"),
        ("report_incomplete", "exact_profile", {"report_incomplete"}, "worker_terminal_custody_incomplete"),
        ("counter_poll_failure", "small_group_oom", {"poll_failure"}, "injected_counter_poll_failure"),
        ("surviving_worker_member", "small_group_oom", {"surviving_worker_member"}, "worker_subtree_still_populated"),
    ]
    for name, case_id, faults, code in supervisor_failures:
        @add(f"supervisor_failure_{name}")
        def _(case_id=case_id, faults=faults, code=code) -> None:
            outcome, _, processes = run_supervisor(case_id, faults)
            assert outcome.failure_code == code and outcome.status != "inner_complete"
            assert (processes.finalized or not processes.forked) and not processes.active_owned_children()

    for name in ("guard-worker", "guard-supervisor"):
        @add(f"cleanup_failure_{name}_prevents_complete")
        def _(name=name) -> None:
            outcome, _, _ = run_supervisor("exact_profile", {f"cleanup_failure_{name}"})
            assert outcome.status == "failed_custody" and not outcome.cleanup_complete
            assert outcome.classification == "profile_accepted"
            assert any(row["code"] == "incomplete_required_cleanup" for row in outcome.failures)

    @add("profile_write_primary_and_cleanup_retained")
    def _() -> None:
        outcome, _, _ = run_supervisor("exact_profile", {"profile_write_failure"})
        assert outcome.failure_code == "unexpected_transport_error"
        assert outcome.cleanup and outcome.failures[0]["phase"] == "primary"

    @add("descriptor_exact_membership_and_mount_verifier")
    def _() -> None:
        with tempfile.TemporaryDirectory() as td:
            make_ordinary_root(Path(td))
            verifier = FakeMountVerifier()
            transport = supervisor_module.DescriptorCgroupTransport(td, verifier, FakeMembership())
            handle = transport.open_verified_container_root(FAKE_ID)
            try:
                assert handle.relative_path == f"docker/{FAKE_ID}" and verifier.calls == 1
            finally:
                transport.close_handle(handle)

    @add("descriptor_membership_wrong_root_refused")
    def _() -> None:
        with tempfile.TemporaryDirectory() as td:
            make_ordinary_root(Path(td))
            transport = supervisor_module.DescriptorCgroupTransport(td, FakeMountVerifier(), FakeMembership("docker"))
            try:
                transport.open_verified_container_root(FAKE_ID)
            except container_module.ContainerBindingError:
                return
            raise AssertionError("wrong membership accepted")

    @add("descriptor_symlink_component_refused")
    def _() -> None:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            target = base / "target"
            target.mkdir()
            (base / "docker").symlink_to(target, target_is_directory=True)
            transport = supervisor_module.DescriptorCgroupTransport(td, FakeMountVerifier(), FakeMembership())
            try:
                transport.open_verified_container_root(FAKE_ID)
            except OSError:
                return
            raise AssertionError("symlink accepted")

    @add("descriptor_allowlisted_partial_write_loop")
    def _() -> None:
        read_fd, write_fd = os.pipe()
        try:
            original = os.write
            first = True
            def partial(fd: int, payload: bytes) -> int:
                nonlocal first
                if first:
                    first = False
                    return original(fd, payload[:1])
                return original(fd, payload)
            with mock.patch.object(supervisor_module.os, "write", side_effect=partial):
                supervisor_module.DescriptorCgroupTransport._write_all(write_fd, b"abc", "partial")
            os.close(write_fd)
            write_fd = -1
            assert os.read(read_fd, 3) == b"abc"
        finally:
            if write_fd >= 0:
                os.close(write_fd)
            os.close(read_fd)

    @add("descriptor_create_open_failure_rolls_back")
    def _() -> None:
        with tempfile.TemporaryDirectory() as td:
            root = make_ordinary_root(Path(td))
            transport = supervisor_module.DescriptorCgroupTransport(td, FakeMountVerifier(), FakeMembership())
            parent = transport.open_verified_container_root(FAKE_ID)
            try:
                with mock.patch.object(transport, "_open_child", side_effect=OSError("injected")):
                    try:
                        transport.create_child(parent, "guard-worker")
                    except OSError:
                        pass
                assert not (root / "guard-worker").exists()
            finally:
                transport.close_handle(parent)

    @add("descriptor_create_rollback_failure_typed")
    def _() -> None:
        with tempfile.TemporaryDirectory() as td:
            make_ordinary_root(Path(td))
            transport = supervisor_module.DescriptorCgroupTransport(td, FakeMountVerifier(), FakeMembership())
            parent = transport.open_verified_container_root(FAKE_ID)
            try:
                with ExitStack() as stack:
                    stack.enter_context(mock.patch.object(transport, "_open_child", side_effect=OSError("open")))
                    stack.enter_context(mock.patch.object(supervisor_module.os, "rmdir", side_effect=OSError("rmdir")))
                    try:
                        transport.create_child(parent, "guard-worker")
                    except supervisor_module.GuardError as exc:
                        assert exc.code == "cgroup_child_create_rollback_failed" and "primary=" in exc.detail and "cleanup=" in exc.detail
                    else:
                        raise AssertionError("rollback failure not typed")
            finally:
                transport.close_handle(parent)

    @add("event_partial_and_interrupted_writes_complete")
    def _() -> None:
        read_fd, write_fd = os.pipe()
        event = {"event": "x", "payload": "abc"}
        original = os.write
        calls = 0
        def interrupted_partial(fd: int, payload: bytes) -> int:
            nonlocal calls
            calls += 1
            if calls == 1:
                raise InterruptedError()
            if calls == 2:
                return original(fd, payload[:2])
            return original(fd, payload)
        try:
            with mock.patch.object(supervisor_module.os, "write", side_effect=interrupted_partial):
                supervisor_module.PosixProcessTransport._write_event(write_fd, event)
            os.close(write_fd)
            write_fd = -1
            parsed = json.loads(os.read(read_fd, 4096))
            assert parsed == event and calls >= 3
        finally:
            if write_fd >= 0:
                os.close(write_fd)
            os.close(read_fd)

    @add("fork_failure_closes_all_pipe_descriptors")
    def _() -> None:
        transport = supervisor_module.PosixProcessTransport(fixture_factory)
        with ExitStack() as stack:
            stack.enter_context(mock.patch.object(supervisor_module.os, "pipe", side_effect=[(10, 11), (12, 13)]))
            stack.enter_context(mock.patch.object(supervisor_module.os, "fork", side_effect=OSError("fork")))
            closed = stack.enter_context(mock.patch.object(supervisor_module.PosixProcessTransport, "_close_quiet"))
            try:
                transport.fork_paused(lambda runtime: 0, ())
            except OSError:
                pass
            else:
                raise AssertionError("fork failure accepted")
        assert {call.args[0] for call in closed.call_args_list} == {10, 11, 12, 13}

    @add("truncated_report_closes_state")
    def _() -> None:
        read_fd, write_fd = os.pipe()
        transport = supervisor_module.PosixProcessTransport(fixture_factory)
        child = supervisor_module.ChildHandle(999999, "fixed-truncated")
        state = supervisor_module._PosixChildState(write_fd, read_fd, child.pid, released=True, buffer=bytearray(b"{"), report_eof=True, wait_status=0, reaped=True)
        transport._children[child.token] = state
        try:
            transport._finish_state(child, state)
        except supervisor_module.GuardError as exc:
            assert exc.code == "truncated_worker_report"
        else:
            raise AssertionError("truncated report accepted")
        assert child.token not in transport._children and transport.custody_record(child)["descriptors_closed"]

    @add("mocked_worker_bootstrap_import_and_order")
    def _() -> None:
        calls: list[str] = []
        emitted: list[Mapping[str, Any]] = []
        class FakePath:
            def __init__(self, value: str) -> None:
                self.value = value
            def read_text(self, encoding: str) -> str:
                return "CapEff:\t0000000000000000\n" if self.value.endswith("status") else "0\n"
        handle = supervisor_module.DirectoryHandle(10, "x", 1, 1, supervisor_module.MountFacts(**GOOD_FACTS))
        runtime = supervisor_module.PosixWorkerRuntime(lambda: {}, lambda: [123], [handle], emitted.append, lambda pid: None, lambda: None)
        with ExitStack() as stack:
            stack.enter_context(mock.patch.object(supervisor_module, "Path", FakePath))
            stack.enter_context(mock.patch.object(supervisor_module.os, "close", side_effect=lambda fd: calls.append("close")))
            stack.enter_context(mock.patch.object(supervisor_module.os, "setgroups", side_effect=lambda groups: calls.append("groups")))
            stack.enter_context(mock.patch.object(supervisor_module.os, "setgid", side_effect=lambda gid: calls.append("gid")))
            stack.enter_context(mock.patch.object(supervisor_module.os, "setuid", side_effect=lambda uid: calls.append("uid")))
            stack.enter_context(mock.patch.object(supervisor_module.os, "geteuid", return_value=65534))
            stack.enter_context(mock.patch.object(supervisor_module.os, "getegid", return_value=65534))
            runtime.bootstrap_after_migration()
        assert calls == ["close", "groups", "gid", "uid"] and emitted[0]["capabilities_cleared"]

    @add("fixed_small_malformed_ready_kills_and_reaps_exact_auxiliary")
    def _() -> None:
        reports: list[Mapping[str, Any]] = []
        with ExitStack() as stack:
            stack.enter_context(mock.patch.object(supervisor_module.os, "pipe", side_effect=[(10, 11), (12, 13)]))
            stack.enter_context(mock.patch.object(supervisor_module.os, "fork", return_value=9002))
            stack.enter_context(mock.patch.object(supervisor_module.PosixProcessTransport, "_close_quiet"))
            stack.enter_context(mock.patch.object(supervisor_module.select, "select", return_value=([10], [], [])))
            stack.enter_context(mock.patch.object(supervisor_module.os, "read", side_effect=[b"{", b""]))
            killed = stack.enter_context(mock.patch.object(supervisor_module.os, "kill"))
            waited = stack.enter_context(mock.patch.object(supervisor_module, "_waitpid_exact", return_value=signal.SIGKILL))
            try:
                supervisor_module.fixed_small_group_oom_body(reports.append, lambda pid: None, lambda: None)
            except supervisor_module.GuardError as exc:
                assert exc.code == "auxiliary_readiness_missing_or_truncated"
            else:
                raise AssertionError("malformed readiness accepted")
        killed.assert_called_once_with(9002, signal.SIGKILL)
        waited.assert_called_once_with(9002)
        assert [row["event"] for row in reports] == ["auxiliary_spawned", "auxiliary_terminal"]

    for name, raw, code in [
        ("report_malformed_json", b"{", "malformed_worker_report_line"),
        ("report_not_mapping", b"[]", "malformed_worker_report_event"),
        ("report_missing_event", b"{}", "malformed_worker_report_event"),
    ]:
        @add(name)
        def _(raw=raw, code=code) -> None:
            try:
                supervisor_module.PosixProcessTransport._decode_line(raw)
            except supervisor_module.GuardError as exc:
                assert exc.code == code
                return
            raise AssertionError("malformed report accepted")

    @add("canonical_sigkill_name")
    def _() -> None:
        assert supervisor_module.PosixProcessTransport._signal_name(-signal.SIGKILL) == "SIGKILL"

    @add("real_posix_large_event_drain_and_reap")
    def _() -> Mapping[str, Any]:
        transport = supervisor_module.PosixProcessTransport(fixture_factory)
        child = transport.fork_paused(lambda runtime: (runtime.emit({"event": "fixture", "payload": "x" * 131072}) or 0), ())
        transport.release(child)
        terminal = transport.wait_terminal(child, 2.0)
        assert terminal.exit_code == 0 and terminal.reaped and terminal.descriptors_closed and terminal.report_complete
        assert not transport.active_owned_children()
        return {"process_starts": 1, "fixture_pids": [child.pid], "terminal_statuses": [asdict(terminal)], "payload_bytes": 131072, "max_concurrent": 1}

    @add("real_posix_membership_barrier")
    def _() -> Mapping[str, Any]:
        transport = supervisor_module.PosixProcessTransport(fixture_factory)
        def action(runtime: Any) -> int:
            runtime.emit({"event": "auxiliary_ready", "pid": os.getpid() + 1000})
            runtime.await_membership_verification(os.getpid() + 1000)
            return 0
        child = transport.fork_paused(action, ())
        transport.release(child)
        def observe(events: tuple[Mapping[str, Any], ...]) -> None:
            for event in events:
                if event.get("event") == "auxiliary_ready":
                    transport.confirm_membership(child, int(event["pid"]))
        terminal = transport.wait_terminal(child, 2.0, observe)
        names = [event["event"] for event in terminal.events]
        assert names.index("auxiliary_ready") < names.index("membership_acknowledged")
        return {"process_starts": 1, "fixture_pids": [child.pid], "terminal_statuses": [asdict(terminal)], "payload_bytes": 0, "max_concurrent": 1}

    @add("real_posix_watchdog_signal_reap")
    def _() -> Mapping[str, Any]:
        transport = supervisor_module.PosixProcessTransport(fixture_factory)
        child = transport.fork_paused(lambda runtime: (time.sleep(1.0) or 0), ())
        transport.release(child)
        terminal = transport.wait_terminal(child, 0.1)
        assert terminal.watchdog and terminal.signal == "SIGKILL" and terminal.reaped and terminal.descriptors_closed
        return {"process_starts": 1, "fixture_pids": [child.pid], "terminal_statuses": [asdict(terminal)], "payload_bytes": 0, "max_concurrent": 1}

    @add("real_posix_report_read_failure_still_reaps")
    def _() -> Mapping[str, Any]:
        transport = supervisor_module.PosixProcessTransport(fixture_factory)
        child = transport.fork_paused(lambda runtime: (time.sleep(0.5) or 0), ())
        transport.release(child)
        os.close(transport._children[child.token].report_read_fd)
        try:
            transport.wait_terminal(child, 1.0)
        except supervisor_module.GuardError as exc:
            assert exc.code == "worker_report_read_failed"
        else:
            raise AssertionError("closed report descriptor accepted")
        custody = transport.custody_record(child)
        assert custody and custody["reaped"] and custody["descriptors_closed"] and not transport.active_owned_children()
        return {"process_starts": 1, "fixture_pids": [child.pid], "terminal_statuses": [custody], "payload_bytes": 0, "max_concurrent": 1}

    @add("real_posix_release_failure_still_reaps")
    def _() -> Mapping[str, Any]:
        transport = supervisor_module.PosixProcessTransport(fixture_factory)
        child = transport.fork_paused(lambda runtime: 0, ())
        os.close(transport._children[child.token].control_write_fd)
        try:
            transport.release(child)
        except OSError:
            pass
        else:
            raise AssertionError("closed control descriptor accepted")
        custody = transport.custody_record(child)
        assert custody and custody["reaped"] and custody["descriptors_closed"] and not transport.active_owned_children()
        return {"process_starts": 1, "fixture_pids": [child.pid], "terminal_statuses": [custody], "payload_bytes": 0, "max_concurrent": 1}

    @add("host_exact_success_all_cases")
    def _() -> Mapping[str, Any]:
        summaries = []
        for case_id in container_module.CASES:
            transport = FixedDockerTransport(case_id)
            hashes = {name: sha256(HERE / name) for name in host_module.HELPERS}
            outcome = host_module.DockerHostAdapter(transport, HERE, hashes, lambda: "1" * 12).run_case(case_id)
            assert outcome.status == "complete" and outcome.exact_container_removed
            assert transport.tar_members == ["group-oom/container.py", "group-oom/supervisor.py"]
            create = next(argv for argv, _ in transport.calls if argv[3] == "create")
            assert "--pull" in create and create[create.index("--pull") + 1] == "never"
            assert not any(argv[3] == "pull" for argv, _ in transport.calls)
            assert all(any(FAKE_ID in item for item in argv) for argv, _ in transport.calls if argv[3] in {"cp", "inspect", "start", "logs", "kill", "rm"})
            summaries.append({"case": case_id, "commands": len(outcome.commands), "classification": outcome.classification})
        return {"injected_host_cases": 3, "summaries": summaries}

    for fault, expected in [
        ("create", "container_create_failed"),
        ("inspection", "container_binding_refused"),
        ("inner_cleanup", "inner_cleanup_or_report_incomplete"),
        ("malformed_inner", "inner_report_malformed_or_truncated"),
        ("attach_timeout", "inner_report_malformed_or_truncated"),
        ("outer_oom", "outer_container_terminal_not_clean"),
        ("logs", "complete_container_logs_unavailable"),
        ("rm", "exact_container_remove_failed"),
    ]:
        @add(f"host_failure_{fault}")
        def _(fault=fault, expected=expected) -> None:
            transport = FixedDockerTransport("small_group_oom", fault)
            hashes = {name: sha256(HERE / name) for name in host_module.HELPERS}
            outcome = host_module.DockerHostAdapter(transport, HERE, hashes, lambda: "1" * 12).run_case("small_group_oom")
            assert outcome.status == "failed" and outcome.primary_failure["code"] == expected
            if outcome.container_id:
                assert outcome.exact_container_removed is (fault not in {"rm", "inspection"})
                if fault == "inspection":
                    assert not any(argv[3] in {"cp", "start", "kill", "rm"} for argv, _ in transport.calls)
                assert all(row["container_id"] == FAKE_ID for row in outcome.cleanup)

    @add("host_helper_hash_mismatch_before_docker")
    def _() -> None:
        transport = FixedDockerTransport("exact_profile")
        outcome = host_module.DockerHostAdapter(transport, HERE, {"container.py": "0" * 64, "supervisor.py": "0" * 64}, lambda: "1" * 12).run_case("exact_profile")
        assert outcome.status == "failed" and not transport.calls

    @add("host_no_host_code_in_archive")
    def _() -> None:
        payload, _ = host_module._tar_helpers(HERE, {name: sha256(HERE / name) for name in host_module.HELPERS})
        with tarfile.open(fileobj=BytesIO(payload), mode="r:") as archive:
            assert set(archive.getnames()) == {"group-oom/container.py", "group-oom/supervisor.py"}

    @add("static_findings_all_mapped")
    def _() -> None:
        supervisor = (HERE / "supervisor.py").read_text()
        host = (HERE / "host.py").read_text()
        assert "from pathlib import Path, PurePosixPath" in supervisor
        assert "signal.Signals" in supervisor and "supervisor_alive" not in supervisor
        assert "CGROUP2_SUPER_MAGIC" in supervisor and "fstatfs" in supervisor
        assert "counter_deltas" in supervisor and "confirm_membership" in supervisor
        assert '"--pull",\n            "never"' in host and '("kill", "--signal", "KILL", cid)' in host

    @add("nf02_cleanup_obeys_kernel_order")
    def _() -> None:
        outcome, cg, _ = run_supervisor("exact_profile")
        assert outcome.status == "inner_complete" and outcome.cleanup_complete
        disable = cg.trace.index(f"write:{cg.root}:cgroup.subtree_control:-memory")
        back = cg.trace.index(f"move:4242:{cg.root}")
        assert disable < back
        assert outcome.inner_supervisor_evidence["supervisor_subgroup_members"] == [4242]
        assert outcome.inner_supervisor_evidence["container_root_members"] == []
        assert outcome.inner_supervisor_evidence["supervisor_membership_verified"] is True

    for fault in ["disable_failure", "disable_ignored"]:
        @add("nf02_" + fault)
        def _(fault=fault) -> None:
            outcome, cg, _ = run_supervisor("exact_profile", {fault})
            assert outcome.status != "inner_complete" and not outcome.cleanup_complete
            assert f"move:4242:{cg.root}" not in cg.trace

    for fault in ["supervisor_missing", "supervisor_foreign", "supervisor_final_missing"]:
        @add("nf04_" + fault)
        def _(fault=fault) -> None:
            outcome, cg, processes = run_supervisor("exact_profile", {fault})
            assert outcome.status != "inner_complete"
            if fault != "supervisor_final_missing":
                assert not processes.forked
                assert f"write:{cg.root}:cgroup.subtree_control:+memory" not in cg.trace
            else:
                assert outcome.failure_code == "final_supervisor_membership_mismatch"

    for fault in ["nonce", "nonce_missing"]:
        @add("nf03_" + fault)
        def _(fault=fault) -> None:
            transport = FixedDockerTransport("exact_profile", fault)
            hashes = {name: sha256(HERE / name) for name in host_module.HELPERS}
            outcome = host_module.DockerHostAdapter(transport, HERE, hashes, lambda: "1" * 12).run_case("exact_profile")
            assert outcome.status == "failed" and not outcome.exact_container_removed
            assert not any(argv[3] in {"cp", "start", "kill", "rm"} for argv, _ in transport.calls)
            assert "nonce_label" in outcome.primary_failure["detail"]

    @add("nf03_verified_identity_before_payload")
    def _() -> None:
        transport = FixedDockerTransport("exact_profile")
        hashes = {name: sha256(HERE / name) for name in host_module.HELPERS}
        outcome = host_module.DockerHostAdapter(transport, HERE, hashes, lambda: "1" * 12).run_case("exact_profile")
        actions = [argv[3] for argv, _ in transport.calls]
        assert outcome.status == "complete" and actions.index("inspect") < actions.index("cp") < actions.index("start")

    for fault in ["wrong_schema", "missing_identity", "missing_outcome", "false_cleanup", "startup_failure"]:
        @add("nf01_" + fault)
        def _(fault=fault) -> None:
            transport = FixedDockerTransport("exact_profile", fault)
            hashes = {name: sha256(HERE / name) for name in host_module.HELPERS}
            outcome = host_module.DockerHostAdapter(transport, HERE, hashes, lambda: "1" * 12).run_case("exact_profile")
            assert outcome.status == "failed" and outcome.exact_container_removed
            if fault == "startup_failure":
                assert outcome.primary_failure["code"] == "inner_startup_failure"
                assert outcome.inner_report["startup_failure"]["message"] == "controlled startup failure"

    for error_type in [PermissionError, FileNotFoundError, OSError]:
        @add("nf05_stat_" + error_type.__name__)
        def _(error_type=error_type) -> None:
            transport = object.__new__(supervisor_module.DescriptorCgroupTransport)
            handle = SimpleNamespace(fd=42)
            with mock.patch.object(supervisor_module.os, "listdir", return_value=["foreign"]), mock.patch.object(supervisor_module.os, "stat", side_effect=error_type("controlled stat failure")):
                try:
                    transport.list_children(handle)
                except supervisor_module.GuardError as exc:
                    assert exc.code == "cgroup_child_stat_failed" and "foreign" in exc.detail
                else:
                    raise AssertionError("uninspectable child treated as absent")

    @add("nf05_valid_enumeration_preserved")
    def _() -> None:
        transport = object.__new__(supervisor_module.DescriptorCgroupTransport)
        handle = SimpleNamespace(fd=42)
        def mode(name, **_kwargs):
            return SimpleNamespace(st_mode=supervisor_module.stat.S_IFREG if name == "cgroup.procs" else supervisor_module.stat.S_IFDIR)
        with mock.patch.object(supervisor_module.os, "listdir", return_value=["z", "cgroup.procs", "a"]), mock.patch.object(supervisor_module.os, "stat", side_effect=mode):
            assert transport.list_children(handle) == ["a", "z"]

    return result


class CaseTimeout(RuntimeError):
    pass


def _case_alarm(_signum: int, _frame: Any) -> None:
    raise CaseTimeout(f"case exceeded {PER_CASE_SECONDS} seconds")


def verify_protocol_bindings() -> list[Mapping[str, Any]]:
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    rows = []
    for binding in protocol["frozen_source_bindings_verified"]:
        actual = sha256(REPO / binding["path"])
        rows.append({"path": binding["path"], "expected": binding["sha256"], "actual": actual, "matched": actual == binding["sha256"]})
    return rows


def run_suite() -> Mapping[str, Any]:
    started = time.monotonic()
    definitions = cases()
    if len(definitions) > MAX_SUITE_CASES:
        raise RuntimeError("complete suite case reservation exceeds 128")
    results = []
    signal.signal(signal.SIGALRM, _case_alarm)
    for case_id, function in definitions:
        began = time.monotonic()
        signal.setitimer(signal.ITIMER_REAL, PER_CASE_SECONDS)
        try:
            detail = function() or {}
            results.append({"id": case_id, "passed": True, "wall_seconds": time.monotonic() - began, **detail})
        except BaseException as exc:
            results.append({"id": case_id, "passed": False, "wall_seconds": time.monotonic() - began, "error_type": type(exc).__name__, "error": str(exc)})
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
        if time.monotonic() - started > AGGREGATE_SECONDS:
            raise RuntimeError("aggregate suite wall bound exceeded")
    bindings = verify_protocol_bindings()
    fixture_rows = [row for row in results if row.get("process_starts")]
    process_starts = sum(int(row.get("process_starts", 0)) for row in fixture_rows)
    fixture_pids = [pid for row in fixture_rows for pid in row.get("fixture_pids", [])]
    terminal_statuses = [status for row in fixture_rows for status in row.get("terminal_statuses", [])]
    max_concurrent = max([int(row.get("max_concurrent", 0)) for row in fixture_rows] or [0])
    payload_max = max([int(row.get("payload_bytes", 0)) for row in fixture_rows] or [0])
    passed = (
        all(row["passed"] for row in results)
        and all(row["matched"] for row in bindings)
        and process_starts <= MAX_BENIGN_STARTS
        and max_concurrent <= MAX_FIXTURE_CHILDREN_CONCURRENT
        and payload_max <= MAX_FIXTURE_PAYLOAD_BYTES
        and len(fixture_pids) == process_starts == len(terminal_statuses)
    )
    return {
        "schema": "crypto.autoresearch.group_oom_native_source_suite.v1",
        "task_id": container_module.TASK_ID,
        "source_only": True,
        "scientific_runs": 0,
        "live_docker_calls": 0,
        "live_cgroup_or_mount_accesses": 0,
        "privilege_changes": 0,
        "process_migrations": 0,
        "memory_pressure_actions": 0,
        "fixed_case_execution_count": len(results),
        "passed_case_count": sum(row["passed"] for row in results),
        "results": results,
        "input_binding_checks": bindings,
        "benign_process_accounting": {
            "maximum_starts": MAX_BENIGN_STARTS,
            "actual_starts": process_starts,
            "maximum_concurrent": MAX_FIXTURE_CHILDREN_CONCURRENT,
            "actual_maximum_concurrent": max_concurrent,
            "maximum_child_lifetime_seconds": MAX_FIXTURE_LIFETIME_SECONDS,
            "maximum_deliberate_payload_bytes": MAX_FIXTURE_PAYLOAD_BYTES,
            "actual_maximum_deliberate_payload_bytes": payload_max,
            "created_pids": fixture_pids,
            "terminal_statuses": terminal_statuses,
        },
        "passed": passed,
        "wall_seconds": time.monotonic() - started,
    }


def resident_bytes(pid: int) -> tuple[int | None, str]:
    if sys.platform.startswith("linux"):
        try:
            for line in Path(f"/proc/{pid}/status").read_text().splitlines():
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite-json", action="store_true", required=True)
    parser.parse_args()
    suite = run_suite()
    print(json.dumps(suite, sort_keys=True, allow_nan=False))
    return 0 if suite["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
