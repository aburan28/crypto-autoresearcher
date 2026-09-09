"""Independent source-only checks for TASK-20260908-101548.

The suite imports the snapshotted production modules and exercises them through
fixed objects, mocked syscalls, and ordinary temporary directories.  It never
contacts Docker, opens /sys or a real cgroup, changes credentials, forks, sends
a real signal, allocates pressure, or invokes an experiment pipeline.
"""
from __future__ import annotations

import argparse
import ast
from contextlib import ExitStack
from dataclasses import asdict, replace
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import tempfile
import time
from typing import Any, Callable, Mapping, Sequence
from unittest import mock

import yaml


TASK_ID = "TASK-20260908-101548"
SOURCE_TASK_ID = "TASK-20260908-692ab6"
ARCHIVE_TASK_ID = "TASK-20260908-6e7845"
AUTHORITY_COMMIT = "e71fd04df21d46271e30fc3822454f0204b69c93"
PUBLISHED_CLAIM_COMMIT = "5a2b8f65d476513dbf684fd38bdd2731bebbf0ea"
SOURCE_SNAPSHOT = "ae1e0ffd286ce70ed781b923554a75a5faf375d0"
MAXIMUM_CASES = 320
PER_CASE_SECONDS = 10
AGGREGATE_SECONDS = 1800
MEMORY_LIMIT_BYTES = 2 * 1024 * 1024 * 1024
MAXIMUM_WORKERS = 1
REPO = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
SOURCE_DIR = REPO / "coordination/experiment-reserve/BATCH-635652/runtime/TASK-20260908-692ab6"
HANDOFF = REPO / "ledger/handoffs/TASK-20260908-101548.yaml"
FAKE_ID = "a" * 64

sys.path.insert(0, str(SOURCE_DIR))
import container as container_module  # noqa: E402
import supervisor as supervisor_module  # noqa: E402


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exact_inspection(container_id: str = FAKE_ID) -> Any:
    plan = container_module.planned_container()
    return container_module.ContainerInspection(
        container_id=container_id,
        image=plan.image,
        platform=plan.platform,
        labels=dict(plan.labels),
        user=plan.user,
        network=plan.network,
        read_only_root=plan.read_only_root,
        cap_drop=plan.cap_drop,
        cap_add=plan.cap_add,
        no_new_privileges=plan.no_new_privileges,
        cgroup_namespace=plan.cgroup_namespace,
        pid_namespace=plan.pid_namespace,
        pids_limit=plan.pids_limit,
        cpu_quota_cores=plan.cpu_quota_cores,
        outer_memory_bytes=plan.outer_memory_bytes,
        outer_memory_swap_total_bytes=plan.outer_memory_swap_total_bytes,
        tmpfs=dict(plan.tmpfs),
        mounts=tuple(plan.mounts),
        privileged=False,
    )


def expect_raises(error: type[BaseException], action: Callable[[], Any], contains: str | None = None) -> BaseException:
    try:
        action()
    except error as exc:
        if contains is not None:
            assert contains in str(exc), (contains, str(exc))
        return exc
    raise AssertionError(f"expected {error.__name__}")


class FixedClock:
    def __init__(self) -> None:
        self.tick = 0

    def utc_now(self) -> str:
        self.tick += 1
        return f"2026-09-09T06:00:{self.tick:02d}+00:00"

    def monotonic(self) -> float:
        self.tick += 1
        return float(self.tick)


class IndependentRuntime:
    def __init__(self, cgroups: "IndependentCgroups", case_id: str) -> None:
        self.cgroups = cgroups
        self.case_id = case_id
        self.events: list[dict[str, Any]] = []

    def bootstrap_after_migration(self) -> None:
        self.cgroups.trace.append("runtime:bootstrap")
        self.emit({
            "event": "privilege_drop_verified",
            "uid": 65534,
            "gid": 65534,
            "capabilities_cleared": True,
            "oom_score_adj": 0,
        })

    def read_profile(self) -> Mapping[str, str]:
        self.cgroups.trace.append("runtime:read_profile")
        return {
            name: self.cgroups.files[self.cgroups.worker][name].strip()
            for name in ("memory.max", "memory.swap.max", "memory.oom.group")
        }

    def emit(self, event: Mapping[str, Any]) -> None:
        self.events.append(dict(event))

    def run_fixed_small_group_oom(self) -> int:
        self.emit({"event": "auxiliary_ready", "pid": 4343, "oom_score_adj": 0})
        self.emit({"event": "before_allocation", "requested_bytes": 128 * 1024 * 1024})
        return 137


class IndependentCgroups:
    """Independent in-memory state; it does not reuse producer test doubles."""

    def __init__(self, *, stale_oom_counters: bool = False, cleanup_failure: str | None = None,
                 migration_failure: bool = False) -> None:
        self.root = f"docker/{FAKE_ID}"
        self.supervisor = f"{self.root}/guard-supervisor"
        self.worker = f"{self.root}/guard-worker"
        baseline = "oom 1\noom_kill 2\noom_group_kill 1\n" if stale_oom_counters else "oom 0\noom_kill 0\noom_group_kill 0\n"
        self.files: dict[str, dict[str, str]] = {
            self.root: {
                "cgroup.type": "domain\n",
                "cgroup.controllers": "cpu memory pids\n",
                "cgroup.subtree_control": "\n",
                "cgroup.procs": "4242\n",
                "cgroup.events": "populated 1\n",
                "memory.events": baseline,
                "memory.current": "0\n",
                "memory.peak": "0\n",
                "cpu.stat": "usage_usec 0\n",
            }
        }
        self.children: dict[str, list[str]] = {self.root: []}
        self.members: dict[str, list[int]] = {self.root: [4242]}
        self.trace: list[str] = []
        self.stale_oom_counters = stale_oom_counters
        self.cleanup_failure = cleanup_failure
        self.migration_failure = migration_failure

    def open_verified_container_root(self, expected_container_id: str) -> str:
        assert expected_container_id == FAKE_ID
        self.trace.append("cgroup:open_root")
        return self.root

    def relative_path(self, handle: str) -> str:
        return handle

    def read_text(self, directory: str, filename: str) -> str:
        self.trace.append(f"read:{directory.rsplit('/', 1)[-1]}:{filename}")
        return self.files[directory][filename]

    def write_text(self, directory: str, filename: str, value: str) -> None:
        self.trace.append(f"write:{directory.rsplit('/', 1)[-1]}:{filename}:{value}")
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
            "cgroup.subtree_control": "\n",
            "cgroup.procs": "\n",
            "cgroup.events": "populated 0\n",
            "memory.events": self.files[self.root]["memory.events"],
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
        return tuple(self.members[directory])

    def move_pid(self, directory: str, pid: int) -> None:
        self.trace.append(f"move:{directory.rsplit('/', 1)[-1]}:{pid}")
        if directory == self.worker and self.migration_failure:
            raise supervisor_module.GuardError("injected_migration_failure")
        for members in self.members.values():
            if pid in members:
                members.remove(pid)
        self.members[directory].append(pid)
        self.files[directory]["cgroup.procs"] = f"{pid}\n"
        self.files[directory]["cgroup.events"] = "populated 1\n"

    def child_is_populated(self, directory: str) -> bool:
        return bool(self.members[directory])

    def remove_empty_child(self, parent: str, name: str) -> None:
        self.trace.append(f"remove:{name}")
        if self.cleanup_failure == name:
            raise OSError("injected cleanup refusal")
        child = f"{parent}/{name}"
        if self.members[child]:
            raise supervisor_module.GuardError("refuse_remove_populated_cgroup")
        self.children[parent].remove(name)

    def close_in_child(self, directory: str) -> None:
        self.trace.append(f"close_in_child:{directory}")


class IndependentProcesses:
    def __init__(self, cgroups: IndependentCgroups, case_id: str) -> None:
        self.cgroups = cgroups
        self.case_id = case_id
        self.action: Callable[[Any], int] | None = None
        self.runtime = IndependentRuntime(cgroups, case_id)
        self.released = False
        self.killed = False
        self.child = supervisor_module.ChildHandle(4342, "independent-owned")

    def supervisor_pid(self) -> int:
        return 4242

    def fork_paused(self, action: Callable[[Any], int], inherited_writable_dirs: Sequence[Any]) -> Any:
        self.cgroups.trace.append("process:fork_paused")
        self.action = action
        # A real fork inherits the parent's current cgroup: guard-supervisor.
        self.cgroups.members[self.cgroups.supervisor].append(self.child.pid)
        return self.child

    def release(self, child: Any) -> None:
        assert child == self.child and self.action is not None
        self.cgroups.trace.append("process:release")
        self.released = True
        self.action(self.runtime)

    def wait_terminal(self, child: Any, timeout_seconds: float) -> Any:
        assert child == self.child and self.released and timeout_seconds <= 45
        self.cgroups.trace.append("process:wait_terminal")
        self.cgroups.members[self.cgroups.worker].clear()
        self.cgroups.files[self.cgroups.worker]["cgroup.procs"] = "\n"
        self.cgroups.files[self.cgroups.worker]["cgroup.events"] = "populated 0\n"
        if self.case_id == "small_group_oom" and not self.cgroups.stale_oom_counters:
            self.cgroups.files[self.cgroups.worker]["memory.events"] = "oom 1\noom_kill 2\noom_group_kill 1\n"
        privilege = next(event for event in self.runtime.events if event.get("event") == "privilege_drop_verified")
        if self.case_id == "exact_profile":
            exit_code, terminal_signal = 0, None
        elif self.case_id == "group_zero_refused":
            exit_code, terminal_signal = 42, None
        else:
            exit_code, terminal_signal = None, "SIGKILL"
        return supervisor_module.WorkerTerminal(
            exit_code=exit_code,
            signal=terminal_signal,
            watchdog=False,
            events=tuple(self.runtime.events),
            effective_uid=privilege["uid"],
            effective_gid=privilege["gid"],
            capabilities_cleared=privilege["capabilities_cleared"],
            oom_score_adj=privilege["oom_score_adj"],
            auxiliary_ready=any(e.get("event") == "auxiliary_ready" for e in self.runtime.events),
            auxiliary_children=sum(e.get("event") == "auxiliary_ready" for e in self.runtime.events),
            allocations_started=sum(e.get("event") == "before_allocation" for e in self.runtime.events),
        )

    def kill_owned_child(self, child: Any) -> None:
        assert child == self.child
        self.killed = True
        for members in self.cgroups.members.values():
            if child.pid in members:
                members.remove(child.pid)

    def supervisor_alive(self) -> bool:
        return True


def run_independent_supervisor(case_id: str, **kwargs: Any) -> tuple[Any, IndependentCgroups, IndependentProcesses]:
    cgroups = IndependentCgroups(**kwargs)
    processes = IndependentProcesses(cgroups, case_id)
    request = supervisor_module.SupervisorRequest.fixed(case_id, FAKE_ID, exact_inspection())
    outcome = supervisor_module.GroupOomSupervisor(cgroups, processes, FixedClock()).run(request)
    return outcome, cgroups, processes


def make_ordinary_root(base: Path, relative: str = f"docker/{FAKE_ID}") -> Path:
    root = base / relative
    root.mkdir(parents=True)
    values = {
        "cgroup.type": "domain\n",
        "cgroup.controllers": "cpu memory pids\n",
        "cgroup.subtree_control": "\n",
        "cgroup.procs": "4242\n",
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


def close_handle(handle: Any) -> None:
    try:
        os.close(handle.fd)
    except OSError:
        pass


def preload_process(events: Sequence[Mapping[str, Any]] = ()) -> tuple[Any, Any, bytes]:
    process = supervisor_module.PosixProcessTransport(lambda report, inherited: None)
    child = supervisor_module.ChildHandle(9001, "fixed-token")
    process._children[child.token] = supervisor_module._PosixChildState(11, 12, child.pid, True)
    raw = b"".join((json.dumps(dict(event), sort_keys=True) + "\n").encode() for event in events)
    return process, child, raw


def wait_with_mocked_status(status: int, events: Sequence[Mapping[str, Any]]) -> Any:
    process, child, raw = preload_process(events)
    with ExitStack() as stack:
        stack.enter_context(mock.patch.object(supervisor_module.time, "monotonic", side_effect=[100.0, 100.0]))
        stack.enter_context(mock.patch.object(supervisor_module.os, "waitpid", return_value=(child.pid, status)))
        stack.enter_context(mock.patch.object(supervisor_module.os, "read", side_effect=[raw, b""]))
        stack.enter_context(mock.patch.object(supervisor_module.os, "close"))
        return process.wait_terminal(child, 1.0)


def cases() -> list[tuple[str, Callable[[], Mapping[str, Any] | None]]]:
    result: list[tuple[str, Callable[[], Mapping[str, Any] | None]]] = []

    def add(name: str):
        def decorator(fn: Callable[[], Mapping[str, Any] | None]):
            result.append((name, fn))
            return fn
        return decorator

    @add("container_planned_profile_exact")
    def _() -> Mapping[str, Any]:
        p = container_module.planned_container()
        assert p.image == container_module.PINNED_IMAGE and p.user == "0:0"
        assert p.network == "none" and p.read_only_root and p.cap_drop == ("ALL",)
        assert p.cap_add == ("SETUID", "SETGID") and p.no_new_privileges
        assert p.cgroup_namespace == "host" and p.pid_namespace == "private"
        assert p.outer_memory_bytes == 8 * 1024**3 and p.outer_memory_swap_total_bytes == 8 * 1024**3
        return {"conformance": True}

    @add("container_wrong_task_refused")
    def _() -> None:
        expect_raises(container_module.ContainerBindingError, lambda: container_module.planned_container("TASK-wrong"), "wrong_task_id")

    for name, value in [
        ("container_id_short", "a" * 63),
        ("container_id_uppercase", "A" * 64),
        ("container_id_suffix", "a" * 63 + "z"),
        ("container_id_nonstr", 7),
    ]:
        @add(name)
        def _(value=value) -> None:
            expect_raises(container_module.ContainerBindingError, lambda: container_module.require_full_container_id(value))

    @add("container_allowed_paths_exact")
    def _() -> None:
        assert container_module.allowed_cgroup_relative_paths(FAKE_ID) == (
            f"docker/{FAKE_ID}", f"system.slice/docker-{FAKE_ID}.scope")

    for name, path in [
        ("path_absolute_refused", f"/docker/{FAKE_ID}"),
        ("path_parent_refused", "docker"),
        ("path_traversal_refused", f"docker/../{FAKE_ID}"),
        ("path_wrong_parent_refused", f"other/{FAKE_ID}"),
        ("path_correct_suffix_wrong_root_refused", f"prefix/docker/{FAKE_ID}"),
        ("path_backslash_refused", f"docker\\{FAKE_ID}"),
    ]:
        @add(name)
        def _(path=path) -> None:
            expect_raises(container_module.ContainerBindingError, lambda: container_module.require_exact_cgroup_relative_path(FAKE_ID, path))

    @add("inspection_exact_accepted")
    def _() -> None:
        container_module.require_inspection_matches(exact_inspection(), FAKE_ID)

    inspection_mutations = [
        ("inspection_identity_mismatch", {"container_id": "b" * 64}),
        ("inspection_label_mismatch", {"labels": {"crypto.autoresearch.task": "TASK-wrong"}}),
        ("inspection_image_mismatch", {"image": "sha256:wrong"}),
        ("inspection_platform_mismatch", {"platform": "linux/amd64"}),
        ("inspection_privileged_refused", {"privileged": True}),
        ("inspection_mount_mismatch", {"mounts": ()}),
        ("inspection_capability_mismatch", {"cap_add": ("SETUID",)}),
        ("inspection_outer_memory_mismatch", {"outer_memory_bytes": 64 * 1024**2}),
    ]
    for name, changes in inspection_mutations:
        @add(name)
        def _(changes=changes) -> None:
            altered = replace(exact_inspection(), **changes)
            expect_raises(container_module.ContainerBindingError, lambda: container_module.require_inspection_matches(altered, FAKE_ID))

    for case_id, expected in [
        ("exact_profile", "profile_accepted"),
        ("group_zero_refused", "typed_refusal"),
        ("small_group_oom", "oom_observed"),
    ]:
        @add(f"supervisor_independent_{case_id}")
        def _(case_id=case_id, expected=expected) -> Mapping[str, Any]:
            outcome, cgroups, _processes = run_independent_supervisor(case_id)
            assert outcome.status == "complete" and outcome.classification == expected
            return {"conformance": True, "ordering": [x["step"] for x in outcome.transcript], "trace": cgroups.trace}

    @add("supervisor_order_profile_fork_migrate_release")
    def _() -> Mapping[str, Any]:
        outcome, _cgroups, _processes = run_independent_supervisor("exact_profile")
        order = [x["step"] for x in outcome.transcript]
        required = [
            "worker_profile_written_and_read_before_fork",
            "worker_forked_behind_barrier",
            "worker_migrated_before_release",
            "worker_released_after_profile_and_migration",
        ]
        positions = [order.index(x) for x in required]
        assert positions == sorted(positions)
        return {"conformance": True, "positions": positions}

    @add("supervisor_request_wrong_task_refused_before_open")
    def _() -> None:
        cgroups = IndependentCgroups()
        processes = IndependentProcesses(cgroups, "exact_profile")
        req = replace(supervisor_module.SupervisorRequest.fixed("exact_profile", FAKE_ID, exact_inspection()), task_id="TASK-wrong")
        out = supervisor_module.GroupOomSupervisor(cgroups, processes, FixedClock()).run(req)
        assert out.failure_code == "wrong_task_id" and "cgroup:open_root" not in cgroups.trace

    @add("supervisor_group_zero_refuses_before_allocation")
    def _() -> None:
        outcome, _cgroups, _processes = run_independent_supervisor("group_zero_refused")
        assert outcome.classification == "typed_refusal"
        assert outcome.terminal["allocations_started"] == 0 and outcome.terminal["auxiliary_children"] == 0

    @add("supervisor_stale_absolute_oom_counters_false_pass")
    def _() -> Mapping[str, Any]:
        outcome, _cgroups, _processes = run_independent_supervisor("small_group_oom", stale_oom_counters=True)
        assert outcome.status == "complete" and outcome.classification == "oom_observed"
        assert outcome.baseline_metrics["memory.events"] == outcome.final_metrics["memory.events"]
        return {"conformance": False, "finding": "F-05", "counterexample": "unchanged baseline and final OOM counters pass because absolute values, not increments, are checked"}

    @add("supervisor_cleanup_failure_false_complete")
    def _() -> Mapping[str, Any]:
        outcome, _cgroups, _processes = run_independent_supervisor("exact_profile", cleanup_failure="guard-worker")
        assert outcome.status == "complete" and any(not row["ok"] for row in outcome.cleanup)
        return {"conformance": False, "finding": "F-04", "counterexample": "failed guard-worker removal leaves status complete"}

    @add("supervisor_migration_failure_strands_paused_child")
    def _() -> Mapping[str, Any]:
        outcome, cgroups, processes = run_independent_supervisor("exact_profile", migration_failure=True)
        assert outcome.failure_code == "injected_migration_failure"
        assert not processes.killed and processes.child.pid in cgroups.members[cgroups.supervisor]
        return {"conformance": False, "finding": "F-03", "counterexample": "worker is empty, so cleanup never kills paused child inherited in guard-supervisor"}

    @add("supervisor_counter_parser_missing_key_defaults_zero")
    def _() -> None:
        parsed = supervisor_module._parse_events("oom 1\n")
        assert parsed.get("oom_kill", 0) == 0

    @add("descriptor_open_exact_ordinary_directory")
    def _() -> None:
        with tempfile.TemporaryDirectory() as td:
            make_ordinary_root(Path(td))
            transport = supervisor_module.DescriptorCgroupTransport(td)
            handle = transport.open_verified_container_root(FAKE_ID)
            try:
                assert handle.relative_path == f"docker/{FAKE_ID}"
            finally:
                close_handle(handle)

    @add("descriptor_open_systemd_alternative")
    def _() -> None:
        with tempfile.TemporaryDirectory() as td:
            make_ordinary_root(Path(td), f"system.slice/docker-{FAKE_ID}.scope")
            transport = supervisor_module.DescriptorCgroupTransport(td)
            handle = transport.open_verified_container_root(FAKE_ID)
            try:
                assert handle.relative_path.startswith("system.slice/")
            finally:
                close_handle(handle)

    @add("descriptor_component_symlink_refused")
    def _() -> None:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            target = base / "target"
            target.mkdir()
            (base / "docker").symlink_to(target, target_is_directory=True)
            transport = supervisor_module.DescriptorCgroupTransport(td)
            expect_raises(OSError, lambda: transport._open_relative_dir(f"docker/{FAKE_ID}"))

    @add("descriptor_traversal_refused")
    def _() -> None:
        with tempfile.TemporaryDirectory() as td:
            transport = supervisor_module.DescriptorCgroupTransport(td)
            expect_raises(supervisor_module.GuardError, lambda: transport._open_relative_dir("docker/../other"))

    @add("descriptor_root_refused")
    def _() -> None:
        with tempfile.TemporaryDirectory() as td:
            transport = supervisor_module.DescriptorCgroupTransport(td)
            expect_raises(supervisor_module.GuardError, lambda: transport._open_relative_dir(""))

    @add("descriptor_allowlisted_read_write")
    def _() -> None:
        with tempfile.TemporaryDirectory() as td:
            root = make_ordinary_root(Path(td))
            transport = supervisor_module.DescriptorCgroupTransport(td)
            handle = transport._open_relative_dir(str(root.relative_to(td)))
            try:
                transport.write_text(handle, "memory.max", "123")
                assert transport.read_text(handle, "memory.max").strip() == "123"
            finally:
                close_handle(handle)

    @add("descriptor_unallowlisted_file_refused")
    def _() -> None:
        with tempfile.TemporaryDirectory() as td:
            root = make_ordinary_root(Path(td))
            transport = supervisor_module.DescriptorCgroupTransport(td)
            handle = transport._open_relative_dir(str(root.relative_to(td)))
            try:
                expect_raises(supervisor_module.GuardError, lambda: transport.write_text(handle, "../../escape", "1"))
            finally:
                close_handle(handle)

    @add("descriptor_symlink_file_refused")
    def _() -> None:
        with tempfile.TemporaryDirectory() as td:
            root = make_ordinary_root(Path(td))
            (root / "memory.max").unlink()
            (root / "memory.max").symlink_to(root / "memory.current")
            transport = supervisor_module.DescriptorCgroupTransport(td)
            handle = transport._open_relative_dir(str(root.relative_to(td)))
            try:
                expect_raises(OSError, lambda: transport.read_text(handle, "memory.max"))
            finally:
                close_handle(handle)

    @add("descriptor_partial_write_refused")
    def _() -> None:
        with tempfile.TemporaryDirectory() as td:
            root = make_ordinary_root(Path(td))
            transport = supervisor_module.DescriptorCgroupTransport(td)
            handle = transport._open_relative_dir(str(root.relative_to(td)))
            try:
                with mock.patch.object(supervisor_module.os, "write", side_effect=lambda fd, data: len(data) - 1):
                    expect_raises(supervisor_module.GuardError, lambda: transport.write_text(handle, "memory.max", "123"), "partial_cgroup_write")
            finally:
                close_handle(handle)

    @add("descriptor_existing_child_refused")
    def _() -> None:
        with tempfile.TemporaryDirectory() as td:
            root = make_ordinary_root(Path(td))
            (root / "guard-worker").mkdir()
            transport = supervisor_module.DescriptorCgroupTransport(td)
            handle = transport._open_relative_dir(str(root.relative_to(td)))
            try:
                expect_raises(FileExistsError, lambda: transport.create_child(handle, "guard-worker"))
            finally:
                close_handle(handle)

    @add("descriptor_partial_create_not_rolled_back")
    def _() -> Mapping[str, Any]:
        with tempfile.TemporaryDirectory() as td:
            root = make_ordinary_root(Path(td))
            transport = supervisor_module.DescriptorCgroupTransport(td)
            handle = transport._open_relative_dir(str(root.relative_to(td)))
            try:
                with mock.patch.object(transport, "_open_child", side_effect=OSError("injected open failure")):
                    expect_raises(OSError, lambda: transport.create_child(handle, "guard-worker"))
                assert (root / "guard-worker").is_dir()
            finally:
                close_handle(handle)
            return {"conformance": False, "finding": "F-06", "counterexample": "mkdir succeeds, descriptor open fails, created path remains untracked"}

    @add("descriptor_worker_readonly_exact_descendant")
    def _() -> None:
        with tempfile.TemporaryDirectory() as td:
            root = make_ordinary_root(Path(td))
            worker = root / "guard-worker"
            worker.mkdir()
            transport = supervisor_module.DescriptorCgroupTransport(td)
            handle = transport.open_verified_worker_readonly(FAKE_ID, f"docker/{FAKE_ID}/guard-worker")
            close_handle(handle)

    @add("descriptor_worker_wrong_descendant_refused")
    def _() -> None:
        with tempfile.TemporaryDirectory() as td:
            transport = supervisor_module.DescriptorCgroupTransport(td)
            expect_raises(supervisor_module.GuardError, lambda: transport.open_verified_worker_readonly(FAKE_ID, f"docker/{FAKE_ID}/other"))

    @add("descriptor_populated_remove_refused")
    def _() -> None:
        with tempfile.TemporaryDirectory() as td:
            root = make_ordinary_root(Path(td))
            worker = root / "guard-worker"
            worker.mkdir()
            (worker / "cgroup.events").write_text("populated 1\n", encoding="ascii")
            transport = supervisor_module.DescriptorCgroupTransport(td)
            parent = transport._open_relative_dir(str(root.relative_to(td)))
            try:
                expect_raises(supervisor_module.GuardError, lambda: transport.remove_empty_child(parent, "guard-worker"))
            finally:
                close_handle(parent)

    @add("process_fork_parent_path_mocked")
    def _() -> None:
        process = supervisor_module.PosixProcessTransport(lambda report, inherited: None)
        with ExitStack() as stack:
            stack.enter_context(mock.patch.object(supervisor_module.os, "pipe", side_effect=[(10, 11), (12, 13)]))
            stack.enter_context(mock.patch.object(supervisor_module.os, "urandom", return_value=b"x" * 16))
            stack.enter_context(mock.patch.object(supervisor_module.os, "fork", return_value=9001))
            close = stack.enter_context(mock.patch.object(supervisor_module.os, "close"))
            child = process.fork_paused(lambda runtime: 0, ())
        assert child.pid == 9001 and close.call_args_list == [mock.call(10), mock.call(13)]

    @add("process_fork_failure_leaks_pipe_fds")
    def _() -> Mapping[str, Any]:
        process = supervisor_module.PosixProcessTransport(lambda report, inherited: None)
        with ExitStack() as stack:
            stack.enter_context(mock.patch.object(supervisor_module.os, "pipe", side_effect=[(10, 11), (12, 13)]))
            stack.enter_context(mock.patch.object(supervisor_module.os, "urandom", return_value=b"x" * 16))
            stack.enter_context(mock.patch.object(supervisor_module.os, "fork", side_effect=OSError("injected fork failure")))
            close = stack.enter_context(mock.patch.object(supervisor_module.os, "close"))
            expect_raises(OSError, lambda: process.fork_paused(lambda runtime: 0, ()))
        assert close.call_count == 0
        return {"conformance": False, "finding": "F-07", "counterexample": "fork failure closes none of four created pipe descriptors"}

    @add("process_release_partial_write_refused")
    def _() -> None:
        process, child, _raw = preload_process()
        process._children[child.token].released = False
        with mock.patch.object(supervisor_module.os, "write", return_value=0):
            expect_raises(supervisor_module.GuardError, lambda: process.release(child), "worker_barrier_release_failed")
        assert not process._children[child.token].released

    @add("process_wait_exact_exit_and_events")
    def _() -> None:
        events = [{"event": "privilege_drop_verified", "uid": 65534, "gid": 65534, "capabilities_cleared": True, "oom_score_adj": 0}, {"event": "profile_accepted"}]
        terminal = wait_with_mocked_status(0, events)
        assert terminal.exit_code == 0 and terminal.signal is None and len(terminal.events) == 2

    @add("process_sigkill_numeric_name_breaks_classifier")
    def _() -> Mapping[str, Any]:
        events = [
            {"event": "privilege_drop_verified", "uid": 65534, "gid": 65534, "capabilities_cleared": True, "oom_score_adj": 0},
            {"event": "auxiliary_ready", "pid": 9002, "oom_score_adj": 0},
            {"event": "before_allocation", "requested_bytes": 128 * 1024 * 1024},
        ]
        terminal = wait_with_mocked_status(signal.SIGKILL, events)
        assert terminal.exit_code is None and terminal.signal == "SIG9"
        cgroups = IndependentCgroups()
        cgroups.files[cgroups.worker] = {
            "memory.events": "oom 1\noom_kill 2\noom_group_kill 1\n",
            "cgroup.events": "populated 0\n",
        }
        cgroups.members[cgroups.worker] = []
        processes = IndependentProcesses(cgroups, "small_group_oom")
        req = supervisor_module.SupervisorRequest.fixed("small_group_oom", FAKE_ID, exact_inspection())
        verifier = supervisor_module.GroupOomSupervisor(cgroups, processes, FixedClock())
        exc = expect_raises(supervisor_module.GuardError, lambda: verifier._verify_worker_terminal(req, processes.child, cgroups.worker, terminal, {"memory.events": "oom 1\noom_kill 2\noom_group_kill 1\n"}))
        assert exc.code == "small_oom_terminal_not_sigkill"
        return {"conformance": False, "finding": "F-02", "counterexample": "native wait status for SIGKILL is rendered SIG9 while verifier requires SIGKILL"}

    @add("process_watchdog_mocked_is_manual")
    def _() -> None:
        process, child, _raw = preload_process()
        with ExitStack() as stack:
            stack.enter_context(mock.patch.object(supervisor_module.time, "monotonic", side_effect=[100.0, 102.0]))
            stack.enter_context(mock.patch.object(supervisor_module.os, "kill"))
            stack.enter_context(mock.patch.object(supervisor_module.os, "waitpid", return_value=(child.pid, signal.SIGKILL)))
            stack.enter_context(mock.patch.object(supervisor_module.os, "read", return_value=b""))
            stack.enter_context(mock.patch.object(supervisor_module.os, "close"))
            terminal = process.wait_terminal(child, 1.0)
        assert terminal.watchdog and terminal.manual_kill

    @add("process_partial_event_sink_not_detected")
    def _() -> Mapping[str, Any]:
        event = {"event": "profile_accepted"}
        encoded = (json.dumps(event, sort_keys=True, separators=(",", ":")) + "\n").encode()
        with mock.patch.object(supervisor_module.os, "write", return_value=len(encoded) - 1):
            assert supervisor_module.PosixProcessTransport._write_event(12, event) is None
        return {"conformance": False, "finding": "F-08", "counterexample": "short event-pipe write is silently accepted"}

    @add("process_report_read_failure_leaves_state")
    def _() -> Mapping[str, Any]:
        process, child, _raw = preload_process()
        with ExitStack() as stack:
            stack.enter_context(mock.patch.object(supervisor_module.time, "monotonic", side_effect=[100.0, 100.0]))
            stack.enter_context(mock.patch.object(supervisor_module.os, "waitpid", return_value=(child.pid, 0)))
            stack.enter_context(mock.patch.object(supervisor_module.os, "read", side_effect=OSError("injected read failure")))
            close = stack.enter_context(mock.patch.object(supervisor_module.os, "close"))
            expect_raises(OSError, lambda: process.wait_terminal(child, 1.0))
        assert child.token in process._children and mock.call(12) not in close.call_args_list
        return {"conformance": False, "finding": "F-07", "counterexample": "report read failure retains child state and report descriptor"}

    @add("process_kill_unknown_refused")
    def _() -> None:
        process = supervisor_module.PosixProcessTransport(lambda report, inherited: None)
        expect_raises(supervisor_module.GuardError, lambda: process.kill_owned_child(supervisor_module.ChildHandle(4, "foreign")))

    @add("process_supervisor_alive_is_constant")
    def _() -> Mapping[str, Any]:
        process = supervisor_module.PosixProcessTransport(lambda report, inherited: None)
        assert process.supervisor_alive() is True
        return {"conformance": False, "finding": "F-09", "counterexample": "native adapter returns a constant and supplies no external outer-container survival receipt"}

    @add("runtime_missing_path_name_blocks_native_bootstrap")
    def _() -> Mapping[str, Any]:
        assert "Path" not in supervisor_module.__dict__
        runtime = supervisor_module.PosixWorkerRuntime(lambda: {}, [supervisor_module.DirectoryHandle(10, "x")], lambda event: None, lambda: 0)
        with ExitStack() as stack:
            stack.enter_context(mock.patch.object(supervisor_module.os, "close"))
            stack.enter_context(mock.patch.object(supervisor_module.os, "setgroups"))
            stack.enter_context(mock.patch.object(supervisor_module.os, "setgid"))
            stack.enter_context(mock.patch.object(supervisor_module.os, "setuid"))
            expect_raises(NameError, runtime.bootstrap_after_migration, "Path")
        return {"conformance": False, "finding": "F-01", "counterexample": "actual bootstrap reaches an unresolved global Path before emitting its privilege receipt"}

    @add("runtime_bootstrap_order_with_fixed_path_injection")
    def _() -> Mapping[str, Any]:
        calls: list[str] = []
        emitted: list[Mapping[str, Any]] = []

        class FakePath:
            def __init__(self, value: str) -> None:
                self.value = value

            def read_text(self, encoding: str) -> str:
                return "CapEff:\t0000000000000000\n" if self.value.endswith("status") else "0\n"

        runtime = supervisor_module.PosixWorkerRuntime(lambda: {}, [supervisor_module.DirectoryHandle(10, "x")], emitted.append, lambda: 0)
        with ExitStack() as stack:
            stack.enter_context(mock.patch.object(supervisor_module, "Path", FakePath, create=True))
            stack.enter_context(mock.patch.object(supervisor_module.os, "close", side_effect=lambda fd: calls.append("close")))
            stack.enter_context(mock.patch.object(supervisor_module.os, "setgroups", side_effect=lambda groups: calls.append("groups")))
            stack.enter_context(mock.patch.object(supervisor_module.os, "setgid", side_effect=lambda gid: calls.append("gid")))
            stack.enter_context(mock.patch.object(supervisor_module.os, "setuid", side_effect=lambda uid: calls.append("uid")))
            stack.enter_context(mock.patch.object(supervisor_module.os, "geteuid", return_value=65534))
            stack.enter_context(mock.patch.object(supervisor_module.os, "getegid", return_value=65534))
            runtime.bootstrap_after_migration()
        assert calls == ["close", "groups", "gid", "uid"] and emitted[0]["capabilities_cleared"]
        return {"conformance": True, "qualification": "requires injecting the missing Path symbol", "calls": calls}

    @add("runtime_close_failure_prevents_drop")
    def _() -> None:
        runtime = supervisor_module.PosixWorkerRuntime(lambda: {}, [supervisor_module.DirectoryHandle(10, "x")], lambda event: None, lambda: 0)
        with ExitStack() as stack:
            stack.enter_context(mock.patch.object(supervisor_module.os, "close", side_effect=OSError("injected close")))
            groups = stack.enter_context(mock.patch.object(supervisor_module.os, "setgroups"))
            expect_raises(OSError, runtime.bootstrap_after_migration)
        groups.assert_not_called()

    @add("runtime_fixed_body_parent_path_without_pressure")
    def _() -> None:
        reports: list[Mapping[str, Any]] = []
        requested: list[int] = []

        class EmptyBuffer:
            def __init__(self, size: int) -> None:
                requested.append(size)
            def __len__(self) -> int:
                return 0
            def __setitem__(self, key: int, value: int) -> None:
                raise AssertionError("no page touch allowed")

        with ExitStack() as stack:
            stack.enter_context(mock.patch.object(supervisor_module, "bytearray", EmptyBuffer, create=True))
            stack.enter_context(mock.patch.object(supervisor_module.os, "pipe", side_effect=[(10, 11), (12, 13)]))
            stack.enter_context(mock.patch.object(supervisor_module.os, "fork", return_value=9002))
            stack.enter_context(mock.patch.object(supervisor_module.os, "close"))
            stack.enter_context(mock.patch.object(supervisor_module.os, "read", return_value=b'{"pid":9002,"oom_score_adj":0}'))
            stack.enter_context(mock.patch.object(supervisor_module.os, "write", return_value=1))
            stack.enter_context(mock.patch.object(supervisor_module.os, "waitpid", return_value=(9002, 0)))
            rc = supervisor_module.fixed_small_group_oom_body(reports.append)
        assert rc == 73 and requested == [128 * 1024 * 1024]
        assert [r["event"] for r in reports] == ["auxiliary_ready", "before_allocation", "unexpected_allocation_survival"]

    @add("runtime_fixed_body_malformed_ready_strands_helper")
    def _() -> Mapping[str, Any]:
        with ExitStack() as stack:
            stack.enter_context(mock.patch.object(supervisor_module.os, "pipe", side_effect=[(10, 11), (12, 13)]))
            stack.enter_context(mock.patch.object(supervisor_module.os, "fork", return_value=9002))
            stack.enter_context(mock.patch.object(supervisor_module.os, "close"))
            stack.enter_context(mock.patch.object(supervisor_module.os, "read", return_value=b"{"))
            wait = stack.enter_context(mock.patch.object(supervisor_module.os, "waitpid"))
            kill = stack.enter_context(mock.patch.object(supervisor_module.os, "kill"))
            expect_raises(supervisor_module.GuardError, lambda: supervisor_module.fixed_small_group_oom_body(lambda event: None), "auxiliary_readiness_missing")
        wait.assert_not_called(); kill.assert_not_called()
        return {"conformance": False, "finding": "F-03", "counterexample": "malformed readiness exits without reaping or killing the forked auxiliary"}

    @add("static_unresolved_path_loads")
    def _() -> Mapping[str, Any]:
        tree = ast.parse((SOURCE_DIR / "supervisor.py").read_text(encoding="utf-8"))
        imported = {alias.asname or alias.name for node in tree.body if isinstance(node, ast.Import) for alias in node.names}
        for node in tree.body:
            if isinstance(node, ast.ImportFrom):
                imported.update(alias.asname or alias.name for alias in node.names)
        path_loads = [node.lineno for node in ast.walk(tree) if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load) and node.id == "Path"]
        assert sorted(path_loads) == [884, 956, 958] and "Path" not in imported
        return {"conformance": False, "finding": "F-01", "lines": sorted(path_loads)}

    @add("static_no_native_container_host_adapter")
    def _() -> Mapping[str, Any]:
        container_text = (SOURCE_DIR / "container.py").read_text(encoding="utf-8")
        assert "import subprocess" not in container_text
        names = {node.name for node in ast.walk(ast.parse(container_text)) if isinstance(node, (ast.FunctionDef, ast.ClassDef))}
        assert not any(name in names for name in {"create_container", "inspect_container", "start_container", "collect_outer_receipt"})
        return {"conformance": False, "finding": "F-10", "missing": ["exact Docker create/inspect/start adapter", "stdin task/ID binding", "external terminal transcript collector"]}

    @add("static_no_cgroup2_mount_verification")
    def _() -> Mapping[str, Any]:
        text = (SOURCE_DIR / "supervisor.py").read_text(encoding="utf-8")
        assert "statfs" not in text and "CGROUP2_SUPER_MAGIC" not in text
        return {"conformance": False, "finding": "F-10", "missing": "native verification that the opened mount is actual cgroup2"}

    @add("static_no_worker_membership_readback_interface")
    def _() -> Mapping[str, Any]:
        protocol = supervisor_module.WorkerRuntime
        assert not hasattr(protocol, "read_membership")
        return {"conformance": False, "finding": "F-05", "missing": "post-drop worker and auxiliary cgroup membership readback"}

    @add("static_no_counter_delta_or_live_poll")
    def _() -> Mapping[str, Any]:
        source = (SOURCE_DIR / "supervisor.py").read_text(encoding="utf-8")
        run_source = ast.get_source_segment(source, next(node for node in ast.walk(ast.parse(source)) if isinstance(node, ast.FunctionDef) and node.name == "_verify_worker_terminal")) or ""
        assert "baseline" not in run_source and "oom_group_kill" in run_source
        return {"conformance": False, "finding": "F-05", "missing": "baseline-to-final counter increment check and bounded live counter polling"}

    @add("producer_nested_receipt_preserved_not_outer")
    def _() -> Mapping[str, Any]:
        receipt = json.loads((SOURCE_DIR / "check-receipt.json").read_text(encoding="utf-8"))
        custody = json.loads((REPO / "coordination/experiment-reserve/admission-20260907/group-oom-source-delivery-custody.json").read_text(encoding="utf-8"))
        assert receipt["suite"]["fixed_case_execution_count"] == 45
        assert receipt["suite"]["passed"] and receipt["command"]["exit_code"] == 0
        assert custody["known_nested_case_executions"] == 45 and custody["outer_exit"] is None
        return {"conformance": False, "finding": "F-11", "scope": "45 nested synthetic passes preserved; source review makes no inference about missing producer outer exit"}

    assert len(result) == 67, len(result)
    return result


class CaseTimeout(RuntimeError):
    pass


def _alarm(_signum: int, _frame: Any) -> None:
    raise CaseTimeout(f"case exceeded {PER_CASE_SECONDS}s")


def verify_bound_inputs() -> list[Mapping[str, Any]]:
    handoff = yaml.safe_load(HANDOFF.read_text(encoding="utf-8"))["handoff"]
    rows = []
    for binding in handoff["source_bindings"]:
        path = REPO / binding["path"]
        got = sha256(path)
        rows.append({"path": binding["path"], "expected_sha256": binding["sha256"], "actual_sha256": got, "matched": got == binding["sha256"]})
    assert len(rows) == 34 and all(row["matched"] for row in rows)
    return rows


def apply_limits() -> Mapping[str, Any]:
    applied: dict[str, Any] = {}
    current_as = resource.getrlimit(resource.RLIMIT_AS)
    applied["address_space_requested_soft_bytes"] = MEMORY_LIMIT_BYTES
    applied["address_space_prior"] = list(current_as)
    try:
        resource.setrlimit(resource.RLIMIT_AS, (MEMORY_LIMIT_BYTES, current_as[1]))
        applied["address_space_soft_enforced"] = True
        applied["address_space_actual"] = list(resource.getrlimit(resource.RLIMIT_AS))
    except (OSError, ValueError) as exc:
        applied["address_space_soft_enforced"] = False
        applied["address_space_setup_error"] = f"{type(exc).__name__}:{exc}"
        applied["address_space_actual"] = list(resource.getrlimit(resource.RLIMIT_AS))
    current_cpu = resource.getrlimit(resource.RLIMIT_CPU)
    cpu_hard = current_cpu[1]
    requested_soft = AGGREGATE_SECONDS if cpu_hard in (-1, resource.RLIM_INFINITY) else min(cpu_hard, AGGREGATE_SECONDS)
    applied["cpu_requested_soft_seconds"] = requested_soft
    applied["cpu_prior"] = list(current_cpu)
    try:
        resource.setrlimit(resource.RLIMIT_CPU, (requested_soft, cpu_hard))
        applied["cpu_soft_enforced"] = True
        applied["cpu_actual"] = list(resource.getrlimit(resource.RLIMIT_CPU))
    except (OSError, ValueError) as exc:
        applied["cpu_soft_enforced"] = False
        applied["cpu_setup_error"] = f"{type(exc).__name__}:{exc}"
        applied["cpu_actual"] = list(resource.getrlimit(resource.RLIMIT_CPU))
    applied["workers"] = MAXIMUM_WORKERS
    return applied


def run_suite() -> Mapping[str, Any]:
    limits = apply_limits()
    bindings = verify_bound_inputs()
    entries = cases()
    results: list[Mapping[str, Any]] = []
    started = time.monotonic()
    old_handler = signal.signal(signal.SIGALRM, _alarm)
    try:
        for case_id, action in entries:
            case_started = time.monotonic()
            signal.setitimer(signal.ITIMER_REAL, PER_CASE_SECONDS)
            try:
                detail = action() or {}
                results.append({"id": case_id, "passed": True, "wall_seconds": time.monotonic() - case_started, **detail})
            except BaseException as exc:
                results.append({"id": case_id, "passed": False, "wall_seconds": time.monotonic() - case_started, "error_type": type(exc).__name__, "error": str(exc)})
            finally:
                signal.setitimer(signal.ITIMER_REAL, 0)
    finally:
        signal.signal(signal.SIGALRM, old_handler)
    elapsed = time.monotonic() - started
    conformance_breaks = sorted({row.get("finding") for row in results if row.get("conformance") is False and row.get("finding")})
    return {
        "schema": "crypto.autoresearch.group_oom_independent_source_suite.v1",
        "task_id": TASK_ID,
        "source_task_id": SOURCE_TASK_ID,
        "source_only": True,
        "operational_containers_started": 0,
        "scientific_runs": 0,
        "live_cgroup_operations": 0,
        "real_forks": 0,
        "real_signals_sent": 0,
        "real_privilege_changes": 0,
        "real_pressure_allocations": 0,
        "input_binding_checks": bindings,
        "hard_limits": limits,
        "fixed_case_execution_count": len(results),
        "wall_seconds": elapsed,
        "results": results,
        "test_execution_passed": all(row["passed"] for row in results),
        "source_conformance_breaks_observed": conformance_breaks,
        "assigned_joint_verdict": "breaks",
    }


def rss_bytes(usage: resource.struct_rusage) -> tuple[int, str]:
    if sys.platform == "darwin":
        return int(usage.ru_maxrss), "ru_maxrss_bytes_on_darwin"
    return int(usage.ru_maxrss) * 1024, "ru_maxrss_kib_on_non_darwin_converted_to_bytes"


def run_final(receipt_path: Path) -> int:
    fixed_count = len(cases())
    assert fixed_count <= 128 and fixed_count <= MAXIMUM_CASES
    prior_failed_attempts: list[Mapping[str, Any]] = []
    if receipt_path.exists():
        prior = json.loads(receipt_path.read_text(encoding="utf-8"))
        prior_failed_attempts.append(prior)
    prior_executed_cases = sum(
        int((attempt.get("suite") or {}).get("fixed_case_execution_count") or 0)
        for attempt in prior_failed_attempts
    )
    prior_attempt_count = sum(
        1 + int((attempt.get("reservation") or {}).get("prior_failed_suite_attempts") or 0)
        for attempt in prior_failed_attempts
    )
    reservation = {
        "reserved_at_UTC": utc_now(),
        "maximum_total_fixed_case_executions": MAXIMUM_CASES,
        "prior_executed_case_count": prior_executed_cases,
        "prior_failed_suite_attempts": prior_attempt_count,
        "prior_failed_hard_limit_setup_attempts": prior_attempt_count,
        "complete_final_suite_reserved_before_execution": fixed_count,
        "complete_suite_maximum_cases": 128,
        "reruns": prior_attempt_count,
        "remaining_case_capacity": MAXIMUM_CASES - prior_executed_cases - fixed_count,
        "per_case_wall_limit_seconds": PER_CASE_SECONDS,
        "aggregate_wall_and_cpu_limit_seconds": AGGREGATE_SECONDS,
        "maximum_workers": MAXIMUM_WORKERS,
        "memory_limit_bytes": MEMORY_LIMIT_BYTES,
    }
    command = [sys.executable, "-B", str(Path(__file__).resolve()), "--suite-json"]
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    started_at = utc_now()
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    monotonic_started = time.monotonic()
    timed_out = False
    with tempfile.TemporaryDirectory(prefix="TASK-20260908-101548-") as td:
        stdout_path = Path(td) / "nested.stdout"
        stderr_path = Path(td) / "nested.stderr"
        with stdout_path.open("wb") as stdout_handle, stderr_path.open("wb") as stderr_handle:
            try:
                completed = subprocess.run(command, cwd=REPO, env=env, stdout=stdout_handle, stderr=stderr_handle, timeout=AGGREGATE_SECONDS, check=False)
                nested_exit_code: int | None = completed.returncode
            except subprocess.TimeoutExpired:
                timed_out = True
                nested_exit_code = None
        nested_stdout = stdout_path.read_text(encoding="utf-8", errors="replace")
        nested_stderr = stderr_path.read_text(encoding="utf-8", errors="replace")
    ended_at = utc_now()
    elapsed = time.monotonic() - monotonic_started
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    try:
        suite = json.loads(nested_stdout)
    except json.JSONDecodeError as exc:
        suite = {"test_execution_passed": False, "parse_error": str(exc)}
    peak_rss, peak_basis = rss_bytes(after)
    receipt = {
        "schema": "crypto.autoresearch.group_oom_independent_source_check_receipt.v1",
        "task_id": TASK_ID,
        "source_task_id": SOURCE_TASK_ID,
        "archived_by": ARCHIVE_TASK_ID,
        "source_only": True,
        "scope_exclusions": {
            "live_docker": True,
            "live_cgroup_or_sys": True,
            "privilege_change": True,
            "process_migration": True,
            "real_memory_pressure": True,
            "scientific_or_experiment_pipeline": True,
        },
        "revision_binding": {
            "authority_commit": AUTHORITY_COMMIT,
            "published_claim_commit": PUBLISHED_CLAIM_COMMIT,
            "source_snapshot": SOURCE_SNAPSHOT,
        },
        "inference": {
            "requested_policy": "review-adversarial",
            "resolved_model_id": "gpt-5.6-sol",
            "reasoning_effort": "xhigh",
            "fallback_allowed": False,
            "fallback_used": False,
            "degraded_allowed": False,
            "degraded_requirements": [],
            "independent_session": True,
            "serving_probe": "not_run_by_handoff",
        },
        "reservation": reservation,
        "nested_process_receipt": {
            "argv": command,
            "cwd": str(REPO),
            "environment": {"PYTHONDONTWRITEBYTECODE": "1"},
            "started_at_UTC": started_at,
            "ended_at_UTC": ended_at,
            "timeout_seconds": AGGREGATE_SECONDS,
            "timed_out": timed_out,
            "terminal_exit_code": nested_exit_code,
            "yielded_session_ids": [],
            "terminal_session_id": None,
            "stdout_redirected_before_invocation": True,
            "stderr_redirected_before_invocation": True,
            "stdout": nested_stdout,
            "stderr": nested_stderr,
        },
        "actual_metrics": {
            "wall_seconds": elapsed,
            "child_user_cpu_seconds": after.ru_utime - before.ru_utime,
            "child_system_cpu_seconds": after.ru_stime - before.ru_stime,
            "host_process_peak_rss_bytes": peak_rss,
            "host_process_peak_rss_basis": peak_basis,
        },
        "prior_failed_attempts": prior_failed_attempts,
        "outer_tool_response": None,
        "suite": suite,
        "limitations": [
            "The preserved producer artifact proves only a nested 45-case synthetic suite; its missing outer exit is not reconstructed.",
            "All independent cases are fixed source-level checks using injected objects, mocked syscalls/processes, or ordinary temporary files.",
            "No live cgroup2 mount, Docker create/inspect/start path, privilege transition, process migration, OOM, or outer-container terminal state was tested.",
            "A passing check harness means the independent assertions executed as designed; the assigned source-conformance joint breaks on the recorded counterexamples.",
        ],
    }
    with receipt_path.open("w", encoding="utf-8") as handle:
        json.dump(receipt, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")
    summary = {"receipt_path": str(receipt_path), "nested_terminal_exit_code": nested_exit_code, "suite_execution_passed": suite.get("test_execution_passed"), "fixed_case_execution_count": suite.get("fixed_case_execution_count"), "assigned_joint_verdict": suite.get("assigned_joint_verdict")}
    print(json.dumps(summary, sort_keys=True))
    return 0 if nested_exit_code == 0 and suite.get("test_execution_passed") is True else 2


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--suite-json", action="store_true")
    mode.add_argument("--run-final", action="store_true")
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    if args.suite_json:
        print(json.dumps(run_suite(), sort_keys=True, allow_nan=False))
        return 0
    if args.receipt is None:
        parser.error("--run-final requires --receipt")
    return run_final(args.receipt)


if __name__ == "__main__":
    raise SystemExit(main())
