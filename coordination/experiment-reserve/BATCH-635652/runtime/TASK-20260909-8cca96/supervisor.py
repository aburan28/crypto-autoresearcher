"""Confined cgroup-v2 group-OOM supervisor with complete child custody.

Importing and constructing these classes performs no external action.  Native
filesystem, cgroup, credential, process, and pressure effects occur only after
the container entry point is invoked by a separately approved live handoff.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import ctypes
import errno
import json
import os
from pathlib import Path, PurePosixPath
import platform
import re
import select
import signal
import stat
import sys
import time
from typing import Any, Callable, Mapping, Protocol, Sequence

from container import (
    CASES,
    TASK_ID,
    ContainerBindingError,
    allowed_cgroup_relative_paths,
    require_exact_cgroup_relative_path,
    require_full_container_id,
)


GIB = 1024 * 1024 * 1024
MIB = 1024 * 1024
NOBODY_ID = 65534
CGROUP2_SUPER_MAGIC = 0x63677270
MAX_EVENT_BYTES = 1024 * 1024
MAX_EVENT_LINE_BYTES = 256 * 1024
POLL_INTERVAL_SECONDS = 0.05
READ_FILES = frozenset(
    {
        "cgroup.controllers",
        "cgroup.events",
        "cgroup.procs",
        "cgroup.subtree_control",
        "cgroup.type",
        "cpu.stat",
        "memory.current",
        "memory.events",
        "memory.max",
        "memory.oom.group",
        "memory.peak",
        "memory.swap.max",
    }
)
WRITE_FILES = frozenset(
    {"cgroup.procs", "cgroup.subtree_control", "memory.max", "memory.oom.group", "memory.swap.max"}
)
CHILD_NAMES = frozenset({"guard-supervisor", "guard-worker"})


class GuardError(RuntimeError):
    """Typed refusal or controlled infrastructure/custody failure."""

    def __init__(self, code: str, detail: str = "") -> None:
        super().__init__(f"{code}{(': ' + detail) if detail else ''}")
        self.code = code
        self.detail = detail


@dataclass(frozen=True)
class MountFacts:
    system: str
    filesystem_type: str
    magic: int
    mount_point: str
    read_write: bool
    source: str


@dataclass
class DirectoryHandle:
    fd: int
    relative_path: str
    device: int
    inode: int
    mount_facts: MountFacts
    closed: bool = False


class CgroupTransport(Protocol):
    def open_verified_container_root(self, expected_container_id: str) -> Any: ...
    def relative_path(self, handle: Any) -> str: ...
    def mount_facts(self, handle: Any) -> Mapping[str, Any]: ...
    def read_text(self, directory: Any, filename: str) -> str: ...
    def write_text(self, directory: Any, filename: str, value: str) -> None: ...
    def create_child(self, parent: Any, name: str) -> Any: ...
    def list_children(self, directory: Any) -> Sequence[str]: ...
    def list_direct_members(self, directory: Any) -> Sequence[int]: ...
    def move_pid(self, directory: Any, pid: int) -> None: ...
    def child_is_populated(self, directory: Any) -> bool: ...
    def remove_empty_child(self, parent: Any, name: str) -> None: ...
    def close_handle(self, directory: Any) -> None: ...


@dataclass(frozen=True)
class ChildHandle:
    pid: int
    token: str


@dataclass(frozen=True)
class WorkerTerminal:
    exit_code: int | None
    signal: str | None
    watchdog: bool
    events: tuple[Mapping[str, Any], ...]
    effective_uid: int | None
    effective_gid: int | None
    capabilities_cleared: bool | None
    oom_score_adj: int | None
    auxiliary_ready: bool
    auxiliary_children: int
    allocations_started: int
    report_complete: bool
    owned_pid: int
    reaped: bool
    descriptors_closed: bool
    parent_terminated: bool = False
    manual_kill: bool = False
    reason: str = ""


class WorkerRuntime(Protocol):
    def bootstrap_after_migration(self) -> None: ...
    def read_profile(self) -> Mapping[str, str]: ...
    def read_membership(self) -> Sequence[int]: ...
    def emit(self, event: Mapping[str, Any]) -> None: ...
    def await_membership_verification(self, auxiliary_pid: int) -> None: ...
    def run_fixed_small_group_oom(self) -> int: ...


WorkerAction = Callable[[WorkerRuntime], int]
EventObserver = Callable[[tuple[Mapping[str, Any], ...]], None]
PollObserver = Callable[[], None]


class ProcessTransport(Protocol):
    def supervisor_pid(self) -> int: ...
    def fork_paused(self, action: WorkerAction, inherited_writable_dirs: Sequence[Any]) -> ChildHandle: ...
    def release(self, child: ChildHandle) -> None: ...
    def confirm_membership(self, child: ChildHandle, auxiliary_pid: int) -> None: ...
    def wait_terminal(
        self,
        child: ChildHandle,
        timeout_seconds: float,
        event_observer: EventObserver | None = None,
        poll_observer: PollObserver | None = None,
    ) -> WorkerTerminal: ...
    def finalize_owned_child(self, child: ChildHandle, terminate: bool) -> Mapping[str, Any]: ...
    def custody_record(self, child: ChildHandle) -> Mapping[str, Any] | None: ...
    def active_owned_children(self) -> Sequence[int]: ...


class Clock(Protocol):
    def utc_now(self) -> str: ...
    def monotonic(self) -> float: ...


class SystemClock:
    def utc_now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def monotonic(self) -> float:
        return time.monotonic()


@dataclass(frozen=True)
class GuardProfile:
    memory_max: int
    memory_swap_max: int
    oom_group: int

    def as_files(self) -> Mapping[str, str]:
        return {
            "memory.max": str(self.memory_max),
            "memory.swap.max": str(self.memory_swap_max),
            "memory.oom.group": str(self.oom_group),
        }


@dataclass(frozen=True)
class SupervisorRequest:
    task_id: str
    case_id: str
    expected_container_id: str
    requested_profile: GuardProfile
    worker_timeout_seconds: float = 45.0
    case_watchdog_seconds: float = 60.0

    @staticmethod
    def fixed(case_id: str, expected_container_id: str) -> "SupervisorRequest":
        profiles = {
            "exact_profile": GuardProfile(8 * GIB, 0, 1),
            "group_zero_refused": GuardProfile(8 * GIB, 0, 0),
            "small_group_oom": GuardProfile(64 * MIB, 0, 1),
        }
        if case_id not in profiles:
            raise GuardError("unknown_fixed_case", case_id)
        return SupervisorRequest(TASK_ID, case_id, expected_container_id, profiles[case_id])


@dataclass
class SupervisorOutcome:
    task_id: str
    case_id: str
    expected_container_id: str
    started_at_UTC: str
    status: str = "running"
    classification: str | None = None
    failure_code: str | None = None
    failure_detail: str | None = None
    failures: list[Mapping[str, Any]] = field(default_factory=list)
    transcript: list[Mapping[str, Any]] = field(default_factory=list)
    mount_verification: Mapping[str, Any] | None = None
    profile_readback: Mapping[str, str] | None = None
    baseline_metrics: Mapping[str, str | None] | None = None
    counter_polls: list[Mapping[str, Any]] = field(default_factory=list)
    terminal: Mapping[str, Any] | None = None
    final_metrics: Mapping[str, str | None] | None = None
    counter_deltas: Mapping[str, int] | None = None
    inner_supervisor_evidence: Mapping[str, Any] | None = None
    cleanup: list[Mapping[str, Any]] = field(default_factory=list)
    cleanup_complete: bool = False
    ended_at_UTC: str | None = None
    wall_seconds: float | None = None

    def as_dict(self) -> Mapping[str, Any]:
        return asdict(self)


def required_worker_profile(case_id: str) -> GuardProfile:
    if case_id == "small_group_oom":
        return GuardProfile(64 * MIB, 0, 1)
    if case_id in {"exact_profile", "group_zero_refused"}:
        return GuardProfile(8 * GIB, 0, 1)
    raise GuardError("unknown_fixed_case", case_id)


def _parse_events(raw: str) -> Mapping[str, int]:
    values: dict[str, int] = {}
    for line in raw.splitlines():
        fields = line.split()
        if len(fields) != 2 or fields[0] in values:
            raise GuardError("malformed_counter_file", raw)
        try:
            value = int(fields[1])
        except ValueError as exc:
            raise GuardError("malformed_counter_file", raw) from exc
        if value < 0:
            raise GuardError("negative_counter_value", fields[0])
        values[fields[0]] = value
    return values


def _must_read(backend: CgroupTransport, directory: Any, filename: str) -> str:
    if filename not in READ_FILES:
        raise GuardError("unallowlisted_cgroup_read", filename)
    value = backend.read_text(directory, filename)
    if value is None:
        raise GuardError("missing_cgroup_metric", filename)
    return str(value).strip()


def _must_write(backend: CgroupTransport, directory: Any, filename: str, value: str) -> None:
    if filename not in WRITE_FILES:
        raise GuardError("unallowlisted_cgroup_write", filename)
    backend.write_text(directory, filename, value)


def _worker_action(case_id: str, expected_profile: GuardProfile) -> WorkerAction:
    def action(runtime: WorkerRuntime) -> int:
        runtime.bootstrap_after_migration()
        observed = dict(runtime.read_profile())
        members = sorted(int(pid) for pid in runtime.read_membership())
        own_pid = os.getpid()
        runtime.emit({"event": "worker_membership_readback", "pid": own_pid, "direct_members": members})
        if members != [own_pid]:
            raise GuardError("worker_membership_readback_mismatch", json.dumps(members))
        expected = dict(expected_profile.as_files())
        if observed != expected:
            runtime.emit(
                {
                    "event": "typed_configuration_refusal",
                    "reason": "memory_guard_unavailable",
                    "observed_profile": observed,
                    "required_profile": expected,
                }
            )
            return 42
        if case_id == "exact_profile":
            runtime.emit({"event": "profile_accepted", "profile": observed})
            return 0
        if case_id == "small_group_oom":
            return runtime.run_fixed_small_group_oom()
        raise GuardError("unknown_fixed_case", case_id)

    return action


class GroupOomSupervisor:
    """Frozen profile-before-fork state machine plus failure-closed cleanup."""

    def __init__(self, cgroups: CgroupTransport, processes: ProcessTransport, clock: Clock | None = None) -> None:
        self.cgroups = cgroups
        self.processes = processes
        self.clock = clock or SystemClock()

    def _event(self, outcome: SupervisorOutcome, step: str, **fields: Any) -> None:
        outcome.transcript.append(
            {"sequence": len(outcome.transcript) + 1, "at_UTC": self.clock.utc_now(), "step": step, **fields}
        )

    def _failure(self, outcome: SupervisorOutcome, phase: str, code: str, detail: str = "") -> None:
        row = {"at_UTC": self.clock.utc_now(), "phase": phase, "code": code, "detail": detail}
        outcome.failures.append(row)
        if outcome.failure_code is None:
            outcome.failure_code = code
            outcome.failure_detail = detail

    def _validate_request(self, request: SupervisorRequest) -> None:
        if request.task_id != TASK_ID:
            raise GuardError("wrong_task_id")
        if request.case_id not in CASES:
            raise GuardError("unknown_fixed_case", request.case_id)
        if not (0 < request.worker_timeout_seconds <= 45):
            raise GuardError("worker_watchdog_out_of_bounds")
        if not (0 < request.case_watchdog_seconds <= 60):
            raise GuardError("case_watchdog_out_of_bounds")
        try:
            require_full_container_id(request.expected_container_id)
        except ContainerBindingError as exc:
            raise GuardError("container_binding_refused", str(exc)) from exc
        canonical = required_worker_profile(request.case_id)
        if request.case_id == "group_zero_refused":
            if request.requested_profile != GuardProfile(8 * GIB, 0, 0):
                raise GuardError("group_zero_control_parameters_changed")
        elif request.requested_profile != canonical:
            raise GuardError("fixed_profile_parameters_changed")

    def _read_metrics(self, directory: Any) -> Mapping[str, str | None]:
        metrics: dict[str, str | None] = {}
        for filename in ("memory.events", "memory.current", "memory.peak", "cpu.stat", "cgroup.events"):
            try:
                metrics[filename] = _must_read(self.cgroups, directory, filename)
            except GuardError:
                if filename in {"memory.events", "memory.current", "cgroup.events"}:
                    raise
                metrics[filename] = None
        return metrics

    def _check_root_preconditions(self, root: Any, expected_id: str, supervisor_pid: int) -> None:
        try:
            actual = require_exact_cgroup_relative_path(expected_id, self.cgroups.relative_path(root))
        except ContainerBindingError as exc:
            raise GuardError("cgroup_path_refused", str(exc)) from exc
        if actual not in allowed_cgroup_relative_paths(expected_id):
            raise GuardError("cgroup_path_refused")
        facts = self.cgroups.mount_facts(root)
        if facts.get("system") != "Linux" or facts.get("filesystem_type") != "cgroup2":
            raise GuardError("cgroup2_mount_not_verified")
        if facts.get("read_write") is not True:
            raise GuardError("cgroup_delegation_mount_readonly")
        if _must_read(self.cgroups, root, "cgroup.type") != "domain":
            raise GuardError("cgroup_not_domain")
        if "memory" not in set(_must_read(self.cgroups, root, "cgroup.controllers").split()):
            raise GuardError("memory_controller_unavailable")
        if _must_read(self.cgroups, root, "cgroup.subtree_control") != "":
            raise GuardError("subtree_control_not_initially_empty")
        if sorted(self.cgroups.list_direct_members(root)) != [supervisor_pid]:
            raise GuardError("unexpected_container_root_members")
        if self.cgroups.list_children(root):
            raise GuardError("preexisting_guard_subgroup")

    def _write_and_read_profile(self, worker: Any, profile: GuardProfile) -> Mapping[str, str]:
        for filename, value in profile.as_files().items():
            _must_write(self.cgroups, worker, filename, value)
        actual = {name: _must_read(self.cgroups, worker, name) for name in profile.as_files()}
        if actual != dict(profile.as_files()):
            raise GuardError("profile_readback_mismatch", json.dumps(actual, sort_keys=True))
        return actual

    @staticmethod
    def _counter_delta(
        baseline_metrics: Mapping[str, str | None], final_metrics: Mapping[str, str | None]
    ) -> Mapping[str, int]:
        baseline_raw = baseline_metrics.get("memory.events")
        final_raw = final_metrics.get("memory.events")
        if baseline_raw is None or final_raw is None:
            raise GuardError("missing_oom_event_counters")
        baseline = _parse_events(baseline_raw)
        final = _parse_events(final_raw)
        required = ("oom_group_kill", "oom_kill")
        missing = [name for name in required if name not in baseline or name not in final]
        if missing:
            raise GuardError("missing_required_oom_counter", ",".join(missing))
        deltas = {name: final[name] - baseline[name] for name in required}
        if any(value < 0 for value in deltas.values()):
            raise GuardError("oom_counter_decreased", json.dumps(deltas, sort_keys=True))
        return deltas

    def _verify_worker_terminal(
        self,
        request: SupervisorRequest,
        worker: Any,
        terminal: WorkerTerminal,
        baseline_metrics: Mapping[str, str | None],
        final_metrics: Mapping[str, str | None],
        membership_verified: bool,
    ) -> tuple[str, str, Mapping[str, int] | None]:
        if not terminal.report_complete or not terminal.reaped or not terminal.descriptors_closed:
            raise GuardError("worker_terminal_custody_incomplete")
        if terminal.watchdog:
            raise GuardError("worker_watchdog", terminal.reason)
        if terminal.effective_uid != NOBODY_ID or terminal.effective_gid != NOBODY_ID:
            raise GuardError("worker_privilege_drop_failed")
        if terminal.capabilities_cleared is not True:
            raise GuardError("worker_capability_drop_failed")
        if terminal.oom_score_adj == -1000:
            raise GuardError("worker_protected_from_oom")
        if request.case_id == "exact_profile":
            if terminal.exit_code != 0 or terminal.signal is not None:
                raise GuardError("exact_profile_terminal_mismatch")
            if not any(event.get("event") == "profile_accepted" for event in terminal.events):
                raise GuardError("exact_profile_missing_worker_readback")
            return ("inner_complete", "profile_accepted", None)
        if request.case_id == "group_zero_refused":
            typed = any(
                event.get("event") == "typed_configuration_refusal"
                and event.get("reason") == "memory_guard_unavailable"
                for event in terminal.events
            )
            if terminal.exit_code != 42 or terminal.signal is not None or not typed:
                raise GuardError("group_zero_not_typed_refusal")
            if terminal.allocations_started != 0 or terminal.auxiliary_children != 0:
                raise GuardError("group_zero_started_stress")
            return ("inner_complete", "typed_refusal", None)
        if request.case_id == "small_group_oom":
            if terminal.manual_kill or terminal.parent_terminated:
                raise GuardError("manual_or_watchdog_kill_not_oom")
            if terminal.signal != "SIGKILL" or terminal.exit_code is not None:
                raise GuardError("small_oom_terminal_not_sigkill")
            events = [str(event.get("event")) for event in terminal.events]
            for required in ("auxiliary_spawned", "auxiliary_ready", "membership_acknowledged", "before_allocation"):
                if required not in events:
                    raise GuardError("small_oom_missing_required_marker", required)
            if not (
                events.index("auxiliary_spawned")
                < events.index("auxiliary_ready")
                < events.index("membership_acknowledged")
                < events.index("before_allocation")
            ):
                raise GuardError("small_oom_marker_order_invalid")
            if not membership_verified or not terminal.auxiliary_ready or terminal.auxiliary_children != 1:
                raise GuardError("small_oom_auxiliary_membership_not_verified")
            deltas = self._counter_delta(baseline_metrics, final_metrics)
            if deltas["oom_group_kill"] < 1 or deltas["oom_kill"] < 2:
                raise GuardError("small_oom_counter_increment_not_met", json.dumps(deltas, sort_keys=True))
            if self.cgroups.child_is_populated(worker) or self.cgroups.list_direct_members(worker):
                raise GuardError("worker_subtree_still_populated")
            return ("inner_complete", "oom_observed_inner_pending_outer", deltas)
        raise GuardError("unknown_fixed_case", request.case_id)

    def _cleanup(
        self,
        outcome: SupervisorOutcome,
        root: Any | None,
        supervisor: Any | None,
        worker: Any | None,
        child: ChildHandle | None,
        memory_enabled: bool,
        supervisor_moved: bool,
    ) -> bool:
        complete = True

        def record(action: str, ok: bool, detail: Any = "") -> None:
            nonlocal complete
            complete = complete and ok
            outcome.cleanup.append(
                {"at_UTC": self.clock.utc_now(), "action": action, "ok": ok, "detail": detail}
            )

        if child is not None:
            try:
                custody = self.processes.finalize_owned_child(child, terminate=True)
                ok = bool(custody.get("reaped") and custody.get("descriptors_closed"))
                record("finalize_exact_owned_worker", ok, custody)
            except Exception as exc:
                record("finalize_exact_owned_worker", False, f"{type(exc).__name__}:{exc}")
        try:
            active = list(self.processes.active_owned_children())
            record("verify_no_active_owned_worker", not active, active)
        except Exception as exc:
            record("verify_no_active_owned_worker", False, f"{type(exc).__name__}:{exc}")

        if worker is not None:
            try:
                populated = self.cgroups.child_is_populated(worker)
                members = list(self.cgroups.list_direct_members(worker))
                record("inspect_guard_worker_population", not populated and not members, {"populated": populated, "members": members})
            except Exception as exc:
                populated, members = True, ["unknown"]
                record("inspect_guard_worker_population", False, f"{type(exc).__name__}:{exc}")
            if not populated and not members and root is not None:
                try:
                    self.cgroups.remove_empty_child(root, "guard-worker")
                    record("remove_empty_guard_worker", True)
                except Exception as exc:
                    record("remove_empty_guard_worker", False, f"{type(exc).__name__}:{exc}")
        delegation_disabled = not memory_enabled
        if root is not None and memory_enabled:
            try:
                _must_write(self.cgroups, root, "cgroup.subtree_control", "-memory")
                if "memory" in _must_read(self.cgroups, root, "cgroup.subtree_control").split():
                    raise GuardError("memory_delegation_not_disabled")
                delegation_disabled = True
                record("disable_only_enabled_memory_delegation", True)
            except Exception as exc:
                record("disable_only_enabled_memory_delegation", False, f"{type(exc).__name__}:{exc}")
        if root is not None and supervisor is not None and supervisor_moved:
            if not delegation_disabled:
                record("move_supervisor_back_to_verified_root", False, "memory_delegation_not_disabled")
            else:
                try:
                    pid = self.processes.supervisor_pid()
                    self.cgroups.move_pid(root, pid)
                    if sorted(self.cgroups.list_direct_members(root)) != [pid]:
                        raise GuardError("supervisor_return_membership_mismatch")
                    record("move_supervisor_back_to_verified_root", True)
                    supervisor_moved = False
                except Exception as exc:
                    record("move_supervisor_back_to_verified_root", False, f"{type(exc).__name__}:{exc}")
        if root is not None and supervisor is not None:
            try:
                populated = self.cgroups.child_is_populated(supervisor)
                members = list(self.cgroups.list_direct_members(supervisor))
                if populated or members:
                    raise GuardError("supervisor_subgroup_still_populated", json.dumps(members))
                self.cgroups.remove_empty_child(root, "guard-supervisor")
                record("remove_empty_guard_supervisor", True)
            except Exception as exc:
                record("remove_empty_guard_supervisor", False, f"{type(exc).__name__}:{exc}")
        for label, handle in (("worker", worker), ("supervisor", supervisor), ("root", root)):
            if handle is None:
                continue
            try:
                self.cgroups.close_handle(handle)
                record(f"close_{label}_descriptor", True)
            except Exception as exc:
                record(f"close_{label}_descriptor", False, f"{type(exc).__name__}:{exc}")
        return complete

    def run(self, request: SupervisorRequest) -> SupervisorOutcome:
        began = self.clock.monotonic()
        outcome = SupervisorOutcome(request.task_id, request.case_id, request.expected_container_id, self.clock.utc_now())
        root = supervisor = worker = None
        child: ChildHandle | None = None
        memory_enabled = supervisor_moved = membership_verified = False
        latest_events: list[Mapping[str, Any]] = []
        acknowledged_aux: int | None = None
        try:
            self._validate_request(request)
            root = self.cgroups.open_verified_container_root(request.expected_container_id)
            outcome.mount_verification = dict(self.cgroups.mount_facts(root))
            self._check_root_preconditions(root, request.expected_container_id, self.processes.supervisor_pid())
            self._event(outcome, "verified_linux_cgroup2_exact_container_root", path=self.cgroups.relative_path(root), facts=outcome.mount_verification)

            supervisor = self.cgroups.create_child(root, "guard-supervisor")
            self._event(outcome, "created_guard_supervisor")
            self.cgroups.move_pid(supervisor, self.processes.supervisor_pid())
            supervisor_moved = True
            supervisor_members = sorted(self.cgroups.list_direct_members(supervisor))
            if supervisor_members != [self.processes.supervisor_pid()]:
                raise GuardError("supervisor_subgroup_membership_mismatch")
            self._event(outcome, "supervisor_moved_outside_worker", pid=self.processes.supervisor_pid(), members=supervisor_members)
            if self.cgroups.list_direct_members(root):
                raise GuardError("container_root_not_empty_after_supervisor_move")
            _must_write(self.cgroups, root, "cgroup.subtree_control", "+memory")
            memory_enabled = True
            self._event(outcome, "memory_delegation_enabled_after_root_empty")

            worker = self.cgroups.create_child(root, "guard-worker")
            self._event(outcome, "created_guard_worker")
            outcome.profile_readback = self._write_and_read_profile(worker, request.requested_profile)
            self._event(outcome, "worker_profile_written_and_read_before_fork", profile=dict(outcome.profile_readback))
            outcome.baseline_metrics = self._read_metrics(worker)
            self._event(outcome, "baseline_metrics_retained", metrics=dict(outcome.baseline_metrics))

            child = self.processes.fork_paused(
                _worker_action(request.case_id, required_worker_profile(request.case_id)),
                (root, supervisor, worker),
            )
            self._event(outcome, "worker_forked_behind_barrier", pid=child.pid, token=child.token)
            self.cgroups.move_pid(worker, child.pid)
            if sorted(self.cgroups.list_direct_members(worker)) != [child.pid]:
                raise GuardError("worker_not_migrated_to_guard_worker")
            self._event(outcome, "worker_migrated_before_release", pid=child.pid)
            self.processes.release(child)
            self._event(outcome, "worker_released_after_profile_and_migration", pid=child.pid)

            def observe_events(events: tuple[Mapping[str, Any], ...]) -> None:
                nonlocal membership_verified, acknowledged_aux
                latest_events.extend(events)
                for event in events:
                    if event.get("event") != "auxiliary_ready":
                        continue
                    auxiliary_pid = event.get("pid")
                    spawned = [row.get("pid") for row in latest_events if row.get("event") == "auxiliary_spawned"]
                    if not isinstance(auxiliary_pid, int) or spawned != [auxiliary_pid]:
                        raise GuardError("auxiliary_identity_mismatch")
                    members = sorted(self.cgroups.list_direct_members(worker))
                    if members != sorted([child.pid, auxiliary_pid]):
                        raise GuardError("worker_auxiliary_membership_mismatch", json.dumps(members))
                    self.processes.confirm_membership(child, auxiliary_pid)
                    acknowledged_aux = auxiliary_pid
                    membership_verified = True
                    self._event(outcome, "both_worker_members_verified_before_pressure", members=members)

            def poll_counters() -> None:
                if request.case_id != "small_group_oom":
                    return
                raw = _must_read(self.cgroups, worker, "memory.events")
                parsed = dict(_parse_events(raw))
                outcome.counter_polls.append(
                    {"sequence": len(outcome.counter_polls) + 1, "at_UTC": self.clock.utc_now(), "counters": parsed}
                )
                if len(outcome.counter_polls) > 1024:
                    raise GuardError("counter_poll_bound_exceeded")

            terminal = self.processes.wait_terminal(child, request.worker_timeout_seconds, observe_events, poll_counters)
            outcome.terminal = asdict(terminal)
            self._event(outcome, "worker_terminal_observed", terminal=dict(outcome.terminal))
            outcome.final_metrics = self._read_metrics(worker)
            self._event(outcome, "worker_counters_retained", metrics=dict(outcome.final_metrics))
            supervisor_members = sorted(self.cgroups.list_direct_members(supervisor))
            root_members = sorted(self.cgroups.list_direct_members(root))
            if supervisor_members != [self.processes.supervisor_pid()] or root_members:
                raise GuardError("final_supervisor_membership_mismatch")
            outcome.inner_supervisor_evidence = {
                "supervisor_subgroup_members": supervisor_members,
                "container_root_members": root_members,
                "supervisor_membership_verified": True,
                "observed_after_worker_terminal": True,
                "supervisor_pid": self.processes.supervisor_pid(),
                "worker_pid": child.pid,
                "worker_reaped": terminal.reaped,
                "membership_acknowledged_auxiliary_pid": acknowledged_aux,
                "at_UTC": self.clock.utc_now(),
            }
            self._event(outcome, "inner_supervisor_observed_after_worker_terminal", evidence=outcome.inner_supervisor_evidence)
            outcome.status, outcome.classification, outcome.counter_deltas = self._verify_worker_terminal(
                request,
                worker,
                terminal,
                outcome.baseline_metrics,
                outcome.final_metrics,
                membership_verified,
            )
        except GuardError as exc:
            outcome.status = "refused" if exc.code in {
                "container_binding_refused",
                "cgroup_path_refused",
                "cgroup2_mount_not_verified",
                "cgroup_delegation_mount_readonly",
                "memory_controller_unavailable",
                "subtree_control_not_initially_empty",
                "unexpected_container_root_members",
                "preexisting_guard_subgroup",
                "profile_readback_mismatch",
            } else "failed"
            self._failure(outcome, "primary", exc.code, exc.detail)
            self._event(outcome, "typed_failure", code=exc.code, detail=exc.detail)
        except Exception as exc:
            outcome.status = "failed"
            detail = f"{type(exc).__name__}:{exc}"
            self._failure(outcome, "primary", "unexpected_transport_error", detail)
            self._event(outcome, "unexpected_failure", error=detail)
        finally:
            outcome.cleanup_complete = self._cleanup(
                outcome, root, supervisor, worker, child, memory_enabled, supervisor_moved
            )
            if outcome.failure_code in {
                "cgroup_child_create_rollback_failed",
                "owned_child_signal_permission_denied",
                "auxiliary_cleanup_incomplete",
            }:
                outcome.cleanup_complete = False
            if not outcome.cleanup_complete:
                self._failure(outcome, "cleanup", "incomplete_required_cleanup", "one or more cleanup/custody actions failed")
                outcome.status = "failed_custody"
            outcome.ended_at_UTC = self.clock.utc_now()
            outcome.wall_seconds = self.clock.monotonic() - began
        return outcome


class _StatFs(ctypes.Structure):
    _fields_ = [
        ("f_type", ctypes.c_long),
        ("f_bsize", ctypes.c_long),
        ("f_blocks", ctypes.c_ulong),
        ("f_bfree", ctypes.c_ulong),
        ("f_bavail", ctypes.c_ulong),
        ("f_files", ctypes.c_ulong),
        ("f_ffree", ctypes.c_ulong),
        ("f_fsid", ctypes.c_int * 2),
        ("f_namelen", ctypes.c_long),
        ("f_frsize", ctypes.c_long),
        ("f_flags", ctypes.c_long),
        ("f_spare", ctypes.c_long * 4),
    ]


def _unescape_mountinfo(value: str) -> str:
    return re.sub(r"\\([0-7]{3})", lambda match: chr(int(match.group(1), 8)), value)


class NativeMountVerifier:
    """Linux fstatfs plus exact mountinfo verification, invoked only on open."""

    def verify(self, fd: int, mount: str) -> MountFacts:
        system = platform.system()
        if system != "Linux":
            raise GuardError("native_linux_required", system)
        libc = ctypes.CDLL(None, use_errno=True)
        facts = _StatFs()
        if libc.fstatfs(fd, ctypes.byref(facts)) != 0:
            number = ctypes.get_errno()
            raise GuardError("fstatfs_failed", os.strerror(number))
        if int(facts.f_type) != CGROUP2_SUPER_MAGIC:
            raise GuardError("mount_not_cgroup2", hex(int(facts.f_type)))
        exact = os.path.abspath(mount)
        matches: list[tuple[str, str, bool]] = []
        for line in Path("/proc/self/mountinfo").read_text(encoding="utf-8").splitlines():
            left, separator, right = line.partition(" - ")
            if not separator:
                continue
            fields = left.split()
            post = right.split()
            if len(fields) < 6 or len(post) < 2:
                continue
            mount_point = _unescape_mountinfo(fields[4])
            if mount_point == exact:
                matches.append((post[0], post[1], "rw" in fields[5].split(",")))
        if len(matches) != 1:
            raise GuardError("cgroup_mountinfo_missing_or_ambiguous", str(len(matches)))
        fs_type, source, read_write = matches[0]
        if fs_type != "cgroup2":
            raise GuardError("mountinfo_not_cgroup2", fs_type)
        if not read_write:
            raise GuardError("cgroup_delegation_mount_readonly")
        return MountFacts(system, fs_type, int(facts.f_type), exact, read_write, source)


class NativeMembershipReader:
    def own_relative_path(self, expected_container_id: str) -> str:
        raw = Path("/proc/self/cgroup").read_text(encoding="ascii")
        rows = [line for line in raw.splitlines() if line]
        if len(rows) != 1 or not rows[0].startswith("0::/"):
            raise GuardError("unified_cgroup_membership_missing_or_ambiguous")
        relative = rows[0][4:]
        try:
            return require_exact_cgroup_relative_path(expected_container_id, relative)
        except ContainerBindingError as exc:
            raise GuardError("own_cgroup_membership_not_exact_container", str(exc)) from exc


class DescriptorCgroupTransport:
    """Descriptor/no-follow adapter confined to the exact own cgroup2 subtree."""

    def __init__(
        self,
        mount: str = "/host-cgroup",
        mount_verifier: Any | None = None,
        membership_reader: Any | None = None,
    ) -> None:
        self.mount = mount
        self._mount_verifier = mount_verifier or NativeMountVerifier()
        self._membership_reader = membership_reader or NativeMembershipReader()

    @staticmethod
    def _validate_relative(relative_path: str) -> None:
        if PurePosixPath(relative_path).is_absolute() or any(
            part in {"", ".", ".."} for part in relative_path.split("/")
        ):
            raise GuardError("cgroup_path_traversal_or_root")

    def _open_relative_dir(self, relative_path: str) -> DirectoryHandle:
        self._validate_relative(relative_path)
        flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
        mount_fd = os.open(self.mount, flags)
        facts: MountFacts | None = None
        fd = mount_fd
        try:
            facts = self._mount_verifier.verify(mount_fd, self.mount)
            for component in relative_path.split("/"):
                expected = os.stat(component, dir_fd=fd, follow_symlinks=False)
                next_fd = os.open(component, flags, dir_fd=fd)
                if fd != mount_fd:
                    os.close(fd)
                fd = next_fd
                observed = os.fstat(fd)
                if not stat.S_ISDIR(observed.st_mode):
                    raise GuardError("cgroup_component_not_directory", component)
                if (observed.st_dev, observed.st_ino) != (expected.st_dev, expected.st_ino):
                    raise GuardError("cgroup_descriptor_identity_changed", component)
            if fd != mount_fd:
                os.close(mount_fd)
            observed = os.fstat(fd)
            return DirectoryHandle(fd, relative_path, observed.st_dev, observed.st_ino, facts)
        except Exception:
            for candidate in {fd, mount_fd}:
                try:
                    os.close(candidate)
                except OSError:
                    pass
            raise

    def open_verified_container_root(self, expected_container_id: str) -> DirectoryHandle:
        cid = require_full_container_id(expected_container_id)
        actual = self._membership_reader.own_relative_path(cid)
        handle = self._open_relative_dir(actual)
        require_exact_cgroup_relative_path(cid, handle.relative_path)
        return handle

    def relative_path(self, handle: DirectoryHandle) -> str:
        return handle.relative_path

    def mount_facts(self, handle: DirectoryHandle) -> Mapping[str, Any]:
        return asdict(handle.mount_facts)

    @staticmethod
    def _check_name(filename: str, allowed: frozenset[str]) -> None:
        if filename not in allowed or "/" in filename or filename in {".", ".."}:
            raise GuardError("unallowlisted_cgroup_filename", filename)

    @staticmethod
    def _write_all(fd: int, payload: bytes, code: str) -> None:
        offset = 0
        while offset < len(payload):
            try:
                written = os.write(fd, payload[offset:])
            except InterruptedError:
                continue
            if written <= 0:
                raise GuardError(code)
            offset += written

    def read_text(self, directory: DirectoryHandle, filename: str) -> str:
        self._check_name(filename, READ_FILES)
        fd = os.open(filename, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=directory.fd)
        try:
            chunks: list[bytes] = []
            total = 0
            while True:
                try:
                    block = os.read(fd, 65536)
                except InterruptedError:
                    continue
                if not block:
                    break
                total += len(block)
                if total > MAX_EVENT_BYTES:
                    raise GuardError("cgroup_read_too_large", filename)
                chunks.append(block)
            return b"".join(chunks).decode("ascii", errors="strict")
        finally:
            os.close(fd)

    def write_text(self, directory: DirectoryHandle, filename: str, value: str) -> None:
        self._check_name(filename, WRITE_FILES)
        if not value or "\x00" in value or "\n" in value:
            raise GuardError("invalid_cgroup_write_value", filename)
        fd = os.open(filename, os.O_WRONLY | os.O_NOFOLLOW, dir_fd=directory.fd)
        try:
            self._write_all(fd, (value + "\n").encode("ascii"), "partial_cgroup_write")
        finally:
            os.close(fd)

    def create_child(self, parent: DirectoryHandle, name: str) -> DirectoryHandle:
        if name not in CHILD_NAMES:
            raise GuardError("unallowlisted_cgroup_child", name)
        os.mkdir(name, mode=0o755, dir_fd=parent.fd)
        try:
            return self._open_child(parent, name)
        except Exception as primary:
            try:
                os.rmdir(name, dir_fd=parent.fd)
            except Exception as cleanup:
                raise GuardError(
                    "cgroup_child_create_rollback_failed",
                    f"primary={type(primary).__name__}:{primary};cleanup={type(cleanup).__name__}:{cleanup}",
                ) from primary
            raise

    def _open_child(self, parent: DirectoryHandle, name: str) -> DirectoryHandle:
        if name not in CHILD_NAMES:
            raise GuardError("unallowlisted_cgroup_child", name)
        fd = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent.fd)
        observed = os.fstat(fd)
        return DirectoryHandle(
            fd,
            f"{parent.relative_path}/{name}",
            observed.st_dev,
            observed.st_ino,
            parent.mount_facts,
        )

    def list_children(self, directory: DirectoryHandle) -> Sequence[str]:
        children: list[str] = []
        for name in os.listdir(directory.fd):
            try:
                mode = os.stat(name, dir_fd=directory.fd, follow_symlinks=False).st_mode
            except OSError as exc:
                raise GuardError("cgroup_child_stat_failed", f"{name}: {type(exc).__name__}: {exc}") from exc
            if stat.S_ISDIR(mode):
                children.append(name)
        return sorted(children)

    def list_direct_members(self, directory: DirectoryHandle) -> Sequence[int]:
        raw = self.read_text(directory, "cgroup.procs")
        if not raw.strip():
            return []
        try:
            return sorted({int(value) for value in raw.split()})
        except ValueError as exc:
            raise GuardError("malformed_cgroup_procs", raw) from exc

    def move_pid(self, directory: DirectoryHandle, pid: int) -> None:
        if not isinstance(pid, int) or pid <= 0:
            raise GuardError("invalid_owned_pid")
        self.write_text(directory, "cgroup.procs", str(pid))

    def child_is_populated(self, directory: DirectoryHandle) -> bool:
        events = _parse_events(self.read_text(directory, "cgroup.events"))
        if "populated" not in events:
            raise GuardError("missing_cgroup_populated_counter")
        return events["populated"] != 0

    def remove_empty_child(self, parent: DirectoryHandle, name: str) -> None:
        if name not in CHILD_NAMES:
            raise GuardError("unallowlisted_cgroup_child", name)
        child = self._open_child(parent, name)
        try:
            if self.child_is_populated(child) or self.list_direct_members(child):
                raise GuardError("refuse_remove_populated_cgroup", name)
        finally:
            self.close_handle(child)
        os.rmdir(name, dir_fd=parent.fd)

    def close_handle(self, directory: DirectoryHandle) -> None:
        if directory.closed:
            return
        os.close(directory.fd)
        directory.closed = True

    def open_verified_worker_readonly(self, expected_container_id: str, worker_path: str) -> DirectoryHandle:
        root = worker_path.rsplit("/", 1)[0] if "/" in worker_path else ""
        require_exact_cgroup_relative_path(expected_container_id, root)
        if worker_path != f"{root}/guard-worker":
            raise GuardError("worker_path_not_exact_verified_descendant")
        return self._open_relative_dir(worker_path)


@dataclass
class _PosixChildState:
    control_write_fd: int
    report_read_fd: int
    pid: int
    released: bool = False
    membership_confirmed: bool = False
    buffer: bytearray = field(default_factory=bytearray)
    events: list[Mapping[str, Any]] = field(default_factory=list)
    report_eof: bool = False
    wait_status: int | None = None
    reaped: bool = False
    parent_terminated: bool = False
    descriptors_closed: bool = False
    read_error: str | None = None


RuntimeFactory = Callable[
    [Callable[[Mapping[str, Any]], None], Sequence[DirectoryHandle], Callable[[int], None], Callable[[], None]],
    WorkerRuntime,
]


class PosixProcessTransport:
    """Owned POSIX child transport with nonblocking report draining and reaping."""

    def __init__(self, runtime_factory: RuntimeFactory) -> None:
        self._runtime_factory = runtime_factory
        self._children: dict[str, _PosixChildState] = {}
        self._custody: dict[str, Mapping[str, Any]] = {}

    def supervisor_pid(self) -> int:
        return os.getpid()

    @staticmethod
    def _close_quiet(fd: int | None) -> None:
        if fd is None or fd < 0:
            return
        while True:
            try:
                os.close(fd)
                return
            except InterruptedError:
                continue
            except OSError:
                return

    @staticmethod
    def _write_all(fd: int, payload: bytes, code: str) -> None:
        offset = 0
        while offset < len(payload):
            try:
                written = os.write(fd, payload[offset:])
            except InterruptedError:
                continue
            if written <= 0:
                raise GuardError(code)
            offset += written

    @classmethod
    def _write_event(cls, fd: int, event: Mapping[str, Any]) -> None:
        payload = (json.dumps(dict(event), sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
        if len(payload) > MAX_EVENT_LINE_BYTES:
            raise GuardError("worker_event_too_large")
        cls._write_all(fd, payload, "worker_event_sink_incomplete")

    @staticmethod
    def _read_exact(fd: int, expected: bytes) -> None:
        received = bytearray()
        while len(received) < len(expected):
            try:
                block = os.read(fd, len(expected) - len(received))
            except InterruptedError:
                continue
            if not block:
                break
            received.extend(block)
        if bytes(received) != expected:
            raise GuardError("worker_control_barrier_failed")

    def fork_paused(self, action: WorkerAction, inherited_writable_dirs: Sequence[Any]) -> ChildHandle:
        opened: list[int] = []
        try:
            control_read, control_write = os.pipe()
            opened.extend((control_read, control_write))
            report_read, report_write = os.pipe()
            opened.extend((report_read, report_write))
            token = os.urandom(16).hex()
            pid = os.fork()
        except BaseException:
            for fd in opened:
                self._close_quiet(fd)
            raise
        if pid == 0:
            self._close_quiet(control_write)
            self._close_quiet(report_read)
            try:
                self._read_exact(control_read, b"R")

                def await_membership(auxiliary_pid: int) -> None:
                    self._write_event(report_write, {"event": "membership_waiting", "pid": auxiliary_pid})
                    self._read_exact(control_read, b"M")
                    self._write_event(report_write, {"event": "membership_acknowledged", "pid": auxiliary_pid})

                def close_in_auxiliary() -> None:
                    self._close_quiet(control_read)
                    self._close_quiet(report_write)

                runtime = self._runtime_factory(
                    lambda event: self._write_event(report_write, event),
                    tuple(inherited_writable_dirs),
                    await_membership,
                    close_in_auxiliary,
                )
                code = int(action(runtime))
                self._write_event(report_write, {"event": "worker_exit", "exit_code": code})
                os._exit(code)
            except BaseException as exc:
                try:
                    self._write_event(
                        report_write,
                        {"event": "worker_error", "type": type(exc).__name__, "message": str(exc)},
                    )
                except BaseException:
                    pass
                os._exit(70)
            finally:
                self._close_quiet(control_read)
                self._close_quiet(report_write)
        self._close_quiet(control_read)
        self._close_quiet(report_write)
        try:
            os.set_blocking(report_read, False)
        except Exception:
            try:
                os.kill(pid, signal.SIGKILL)
                while True:
                    try:
                        os.waitpid(pid, 0)
                        break
                    except InterruptedError:
                        continue
            finally:
                self._close_quiet(control_write)
                self._close_quiet(report_read)
            raise
        self._children[token] = _PosixChildState(control_write, report_read, pid)
        return ChildHandle(pid, token)

    def _state(self, child: ChildHandle) -> _PosixChildState:
        state = self._children.get(child.token)
        if state is None or state.pid != child.pid:
            raise GuardError("refuse_unowned_child")
        return state

    def release(self, child: ChildHandle) -> None:
        state = self._state(child)
        if state.released:
            raise GuardError("unknown_or_already_released_child")
        try:
            self._write_all(state.control_write_fd, b"R", "worker_barrier_release_failed")
            state.released = True
        except Exception:
            self.finalize_owned_child(child, terminate=True)
            raise

    def confirm_membership(self, child: ChildHandle, auxiliary_pid: int) -> None:
        state = self._state(child)
        if not state.released or state.membership_confirmed or auxiliary_pid <= 0:
            raise GuardError("invalid_membership_confirmation")
        self._write_all(state.control_write_fd, b"M", "membership_confirmation_sink_failed")
        state.membership_confirmed = True

    @staticmethod
    def _decode_line(line: bytes) -> Mapping[str, Any]:
        if not line or len(line) > MAX_EVENT_LINE_BYTES:
            raise GuardError("malformed_worker_report_line")
        try:
            value = json.loads(line.decode("utf-8", errors="strict"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise GuardError("malformed_worker_report_line") from exc
        if not isinstance(value, Mapping) or not isinstance(value.get("event"), str):
            raise GuardError("malformed_worker_report_event")
        return dict(value)

    def _drain(self, state: _PosixChildState) -> tuple[Mapping[str, Any], ...]:
        new_events: list[Mapping[str, Any]] = []
        while not state.report_eof:
            try:
                block = os.read(state.report_read_fd, 65536)
            except BlockingIOError:
                break
            except InterruptedError:
                continue
            except OSError as exc:
                state.read_error = f"{type(exc).__name__}:{exc}"
                raise GuardError("worker_report_read_failed", state.read_error) from exc
            if not block:
                state.report_eof = True
                break
            state.buffer.extend(block)
            if len(state.buffer) > MAX_EVENT_BYTES:
                raise GuardError("worker_report_too_large")
            while b"\n" in state.buffer:
                line, _, remainder = state.buffer.partition(b"\n")
                state.buffer = bytearray(remainder)
                event = self._decode_line(line)
                state.events.append(event)
                new_events.append(event)
        return tuple(new_events)

    @staticmethod
    def _wait_nohang(pid: int) -> tuple[int, int]:
        while True:
            try:
                return os.waitpid(pid, os.WNOHANG)
            except InterruptedError:
                continue

    @staticmethod
    def _wait_blocking(pid: int) -> int:
        while True:
            try:
                waited, status = os.waitpid(pid, 0)
                if waited == pid:
                    return status
            except InterruptedError:
                continue

    @staticmethod
    def _signal_name(exit_code: int) -> str:
        try:
            return signal.Signals(abs(exit_code)).name
        except ValueError as exc:
            raise GuardError("unknown_terminal_signal", str(exit_code)) from exc

    def _close_state_descriptors(self, state: _PosixChildState) -> None:
        self._close_quiet(state.control_write_fd)
        self._close_quiet(state.report_read_fd)
        state.control_write_fd = -1
        state.report_read_fd = -1
        state.descriptors_closed = True

    def _custody_from_state(self, token: str, state: _PosixChildState) -> Mapping[str, Any]:
        exit_code: int | None = None
        signal_name: str | None = None
        if state.wait_status is not None:
            converted = os.waitstatus_to_exitcode(state.wait_status)
            if converted < 0:
                signal_name = self._signal_name(converted)
            else:
                exit_code = converted
        auxiliary_spawned = [event.get("pid") for event in state.events if event.get("event") == "auxiliary_spawned"]
        auxiliary_terminal = [event.get("pid") for event in state.events if event.get("event") == "auxiliary_terminal"]
        return {
            "token": token,
            "pid": state.pid,
            "exit_code": exit_code,
            "signal": signal_name,
            "wait_status": state.wait_status,
            "reaped": state.reaped,
            "parent_terminated": state.parent_terminated,
            "report_eof": state.report_eof,
            "report_complete": state.report_eof and not state.buffer and state.read_error is None,
            "report_bytes_buffered": sum(
                len((json.dumps(dict(event), sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8"))
                for event in state.events
            ),
            "event_count": len(state.events),
            "descriptors_closed": state.descriptors_closed,
            "membership_confirmed": state.membership_confirmed,
            "auxiliary_spawned_pids": auxiliary_spawned,
            "auxiliary_terminal_pids": auxiliary_terminal,
            "read_error": state.read_error,
        }

    def _finish_state(self, child: ChildHandle, state: _PosixChildState) -> Mapping[str, Any]:
        primary: GuardError | None = None
        drain_deadline = time.monotonic() + 1.0
        try:
            while not state.report_eof:
                try:
                    self._drain(state)
                except GuardError as exc:
                    primary = primary or exc
                    break
                if not state.report_eof:
                    if time.monotonic() >= drain_deadline:
                        primary = primary or GuardError("worker_report_eof_timeout")
                        break
                    select.select([state.report_read_fd], [], [], 0.05)
            if state.buffer:
                primary = primary or GuardError("truncated_worker_report")
        finally:
            self._close_state_descriptors(state)
            custody = self._custody_from_state(child.token, state)
            self._custody[child.token] = custody
            self._children.pop(child.token, None)
        if primary is not None:
            raise primary
        return custody

    def wait_terminal(
        self,
        child: ChildHandle,
        timeout_seconds: float,
        event_observer: EventObserver | None = None,
        poll_observer: PollObserver | None = None,
    ) -> WorkerTerminal:
        state = self._state(child)
        if not state.released:
            raise GuardError("unknown_or_unreleased_child")
        deadline = time.monotonic() + timeout_seconds
        next_poll = time.monotonic()
        watchdog = False
        primary: GuardError | None = None
        secondary: list[str] = []
        while state.wait_status is None:
            try:
                events = self._drain(state)
                if events and event_observer is not None:
                    event_observer(events)
                now = time.monotonic()
                if poll_observer is not None and now >= next_poll:
                    poll_observer()
                    next_poll = now + POLL_INTERVAL_SECONDS
            except GuardError as exc:
                primary = exc
                break
            waited, status = self._wait_nohang(child.pid)
            if waited == child.pid:
                state.wait_status = status
                state.reaped = True
                break
            if time.monotonic() >= deadline:
                watchdog = True
                primary = GuardError("worker_watchdog")
                break
            select.select([state.report_read_fd], [], [], min(POLL_INTERVAL_SECONDS, max(0.0, deadline - time.monotonic())))
        if state.wait_status is None:
            # Closing the control writer lets a child blocked on membership
            # acknowledgement unwind and clean its same-UID auxiliary first.
            self._close_quiet(state.control_write_fd)
            state.control_write_fd = -1
            grace_deadline = time.monotonic() + 0.5
            while state.wait_status is None and time.monotonic() < grace_deadline:
                try:
                    events = self._drain(state)
                    if events and event_observer is not None:
                        event_observer(events)
                except GuardError as exc:
                    secondary.append(f"grace_report={exc.code}:{exc.detail}")
                    break
                waited, status = self._wait_nohang(child.pid)
                if waited == child.pid:
                    state.wait_status, state.reaped = status, True
                    break
                select.select([state.report_read_fd], [], [], 0.05)
        if state.wait_status is None:
            signal_permitted = True
            try:
                os.kill(child.pid, signal.SIGKILL)
                state.parent_terminated = True
            except ProcessLookupError:
                pass
            except PermissionError as exc:
                signal_permitted = False
                secondary.append(f"owned_child_signal_permission_denied:{exc}")
            if signal_permitted:
                try:
                    state.wait_status = self._wait_blocking(child.pid)
                    state.reaped = True
                except ChildProcessError as exc:
                    secondary.append(f"owned_child_reap_failed:{exc}")
            else:
                self._close_state_descriptors(state)
                custody = self._custody_from_state(child.token, state)
                self._custody[child.token] = custody
                detail = ";".join(
                    [primary.detail if primary and primary.detail else "", *secondary]
                ).strip(";")
                raise GuardError(primary.code if primary else "owned_child_signal_permission_denied", detail)
        try:
            custody = self._finish_state(child, state)
        except GuardError as exc:
            if primary is None:
                primary = exc
            else:
                secondary.append(f"terminal_custody={exc.code}:{exc.detail}")
            custody = self._custody.get(child.token, {})
        if primary is not None and secondary:
            primary = GuardError(primary.code, ";".join([primary.detail, *secondary]).strip(";"))
        if primary is not None and not watchdog:
            raise primary
        events = tuple(state.events)
        privilege = next((event for event in events if event.get("event") == "privilege_drop_verified"), {})
        exit_code = custody.get("exit_code")
        signal_name = custody.get("signal")
        terminal = WorkerTerminal(
            exit_code=exit_code if isinstance(exit_code, int) else None,
            signal=signal_name if isinstance(signal_name, str) else None,
            watchdog=watchdog,
            events=events,
            effective_uid=privilege.get("uid"),
            effective_gid=privilege.get("gid"),
            capabilities_cleared=privilege.get("capabilities_cleared"),
            oom_score_adj=privilege.get("oom_score_adj"),
            auxiliary_ready=any(event.get("event") == "auxiliary_ready" for event in events),
            auxiliary_children=sum(1 for event in events if event.get("event") == "auxiliary_spawned"),
            allocations_started=sum(1 for event in events if event.get("event") == "before_allocation"),
            report_complete=bool(custody.get("report_complete")),
            owned_pid=child.pid,
            reaped=bool(custody.get("reaped")),
            descriptors_closed=bool(custody.get("descriptors_closed")),
            parent_terminated=bool(custody.get("parent_terminated")),
            manual_kill=bool(custody.get("parent_terminated")),
            reason="watchdog" if watchdog else "terminal_wait_status",
        )
        return terminal

    def finalize_owned_child(self, child: ChildHandle, terminate: bool) -> Mapping[str, Any]:
        retained = self._custody.get(child.token)
        if retained is not None and child.token not in self._children:
            return retained
        state = self._state(child)
        if state.wait_status is None:
            waited, status = self._wait_nohang(child.pid)
            if waited == child.pid:
                state.wait_status, state.reaped = status, True
            elif terminate:
                try:
                    os.kill(child.pid, signal.SIGKILL)
                    state.parent_terminated = True
                except ProcessLookupError:
                    pass
                except PermissionError as exc:
                    raise GuardError("owned_child_signal_permission_denied", str(exc)) from exc
                state.wait_status = self._wait_blocking(child.pid)
                state.reaped = True
            else:
                raise GuardError("owned_child_still_running")
        return self._finish_state(child, state)

    def custody_record(self, child: ChildHandle) -> Mapping[str, Any] | None:
        return self._custody.get(child.token)

    def active_owned_children(self) -> Sequence[int]:
        return tuple(state.pid for state in self._children.values())


def _write_all_fd(fd: int, payload: bytes, code: str) -> None:
    PosixProcessTransport._write_all(fd, payload, code)


def _waitpid_exact(pid: int) -> int:
    return PosixProcessTransport._wait_blocking(pid)


def fixed_small_group_oom_body(
    report: Callable[[Mapping[str, Any]], None],
    await_membership: Callable[[int], None],
    close_in_auxiliary: Callable[[], None],
) -> int:
    """Frozen future 16 MiB auxiliary plus 128 MiB direct-worker control."""

    descriptors: list[int] = []
    auxiliary_pid: int | None = None
    auxiliary_reaped = False
    try:
        ready_read, ready_write = os.pipe()
        descriptors.extend((ready_read, ready_write))
        hold_read, hold_write = os.pipe()
        descriptors.extend((hold_read, hold_write))
        auxiliary_pid = os.fork()
    except BaseException:
        for fd in descriptors:
            PosixProcessTransport._close_quiet(fd)
        raise
    if auxiliary_pid == 0:
        PosixProcessTransport._close_quiet(ready_read)
        PosixProcessTransport._close_quiet(hold_write)
        close_in_auxiliary()
        try:
            allocation = bytearray(16 * MIB)
            for offset in range(0, len(allocation), 4096):
                allocation[offset] = 1
            oom_score_adj = int(Path("/proc/self/oom_score_adj").read_text(encoding="ascii").strip())
            payload = json.dumps(
                {"pid": os.getpid(), "oom_score_adj": oom_score_adj}, sort_keys=True, separators=(",", ":")
            ).encode("ascii") + b"\n"
            _write_all_fd(ready_write, payload, "auxiliary_readiness_sink_failed")
            PosixProcessTransport._close_quiet(ready_write)
            ready_write = -1
            while True:
                try:
                    os.read(hold_read, 1)
                    break
                except InterruptedError:
                    continue
            os._exit(0)
        except BaseException:
            os._exit(72)
        finally:
            PosixProcessTransport._close_quiet(ready_write)
            PosixProcessTransport._close_quiet(hold_read)
    PosixProcessTransport._close_quiet(ready_write)
    PosixProcessTransport._close_quiet(hold_read)
    ready_write = hold_read = -1
    report({"event": "auxiliary_spawned", "pid": auxiliary_pid})
    try:
        deadline = time.monotonic() + 5.0
        raw = bytearray()
        while b"\n" not in raw and time.monotonic() < deadline:
            readable, _, _ = select.select([ready_read], [], [], min(0.05, max(0.0, deadline - time.monotonic())))
            if not readable:
                continue
            try:
                block = os.read(ready_read, 4096)
            except InterruptedError:
                continue
            if not block:
                break
            raw.extend(block)
            if len(raw) > 4096:
                raise GuardError("auxiliary_readiness_too_large")
        if not raw.endswith(b"\n") or raw.count(b"\n") != 1:
            raise GuardError("auxiliary_readiness_missing_or_truncated")
        try:
            ready = json.loads(raw.decode("ascii", errors="strict"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise GuardError("auxiliary_readiness_malformed") from exc
        if not isinstance(ready, Mapping) or ready.get("pid") != auxiliary_pid:
            raise GuardError("auxiliary_identity_mismatch")
        if ready.get("oom_score_adj") == -1000:
            raise GuardError("auxiliary_protected_from_oom")
        report({"event": "auxiliary_ready", "pid": auxiliary_pid, "oom_score_adj": ready.get("oom_score_adj")})
        await_membership(auxiliary_pid)
        report({"event": "before_allocation", "requested_bytes": 128 * MIB})
        allocation = bytearray(128 * MIB)
        for offset in range(0, len(allocation), 4096):
            allocation[offset] = 1
        _write_all_fd(hold_write, b"X", "auxiliary_release_sink_failed")
        status = _waitpid_exact(auxiliary_pid)
        auxiliary_reaped = True
        report(
            {
                "event": "auxiliary_terminal",
                "pid": auxiliary_pid,
                "wait_status": status,
                "exit_code": os.waitstatus_to_exitcode(status),
            }
        )
        report({"event": "unexpected_allocation_survival", "bytes": len(allocation)})
        return 73
    finally:
        active_error = sys.exception()
        PosixProcessTransport._close_quiet(ready_read)
        PosixProcessTransport._close_quiet(hold_write)
        if auxiliary_pid is not None and not auxiliary_reaped:
            cleanup_error: str | None = None
            try:
                os.kill(auxiliary_pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            except PermissionError as exc:
                cleanup_error = f"PermissionError:{exc}"
            try:
                status = _waitpid_exact(auxiliary_pid)
                auxiliary_reaped = True
                report(
                    {
                        "event": "auxiliary_terminal",
                        "pid": auxiliary_pid,
                        "wait_status": status,
                        "exit_code": os.waitstatus_to_exitcode(status),
                        "cleanup": True,
                    }
                )
            except (ChildProcessError, PermissionError) as exc:
                cleanup_error = cleanup_error or f"{type(exc).__name__}:{exc}"
            if cleanup_error is not None or not auxiliary_reaped:
                primary = (
                    f"{type(active_error).__name__}:{active_error}"
                    if active_error is not None
                    else "none"
                )
                raise GuardError(
                    "auxiliary_cleanup_incomplete",
                    f"primary={primary};cleanup={cleanup_error or 'not_reaped'}",
                )


def make_posix_runtime_factory(cgroups: DescriptorCgroupTransport, expected_container_id: str) -> RuntimeFactory:
    def factory(
        report: Callable[[Mapping[str, Any]], None],
        inherited: Sequence[DirectoryHandle],
        await_membership: Callable[[int], None],
        close_in_auxiliary: Callable[[], None],
    ) -> WorkerRuntime:
        if not inherited:
            raise GuardError("missing_inherited_worker_handle")
        worker_path = inherited[-1].relative_path

        def with_worker(reader: Callable[[DirectoryHandle], Any]) -> Any:
            directory = cgroups.open_verified_worker_readonly(expected_container_id, worker_path)
            try:
                return reader(directory)
            finally:
                cgroups.close_handle(directory)

        return PosixWorkerRuntime(
            read_profile=lambda: with_worker(
                lambda directory: {
                    name: _must_read(cgroups, directory, name)
                    for name in ("memory.max", "memory.swap.max", "memory.oom.group")
                }
            ),
            read_membership=lambda: with_worker(lambda directory: cgroups.list_direct_members(directory)),
            inherited_writable_dirs=inherited,
            report=report,
            await_membership=await_membership,
            close_in_auxiliary=close_in_auxiliary,
        )

    return factory


class PosixWorkerRuntime:
    def __init__(
        self,
        read_profile: Callable[[], Mapping[str, str]],
        read_membership: Callable[[], Sequence[int]],
        inherited_writable_dirs: Sequence[DirectoryHandle],
        report: Callable[[Mapping[str, Any]], None],
        await_membership: Callable[[int], None],
        close_in_auxiliary: Callable[[], None],
    ) -> None:
        self._read_profile = read_profile
        self._read_membership = read_membership
        self._inherited = tuple(inherited_writable_dirs)
        self._report = report
        self._await_membership = await_membership
        self._close_in_auxiliary = close_in_auxiliary

    def bootstrap_after_migration(self) -> None:
        for directory in self._inherited:
            while True:
                try:
                    os.close(directory.fd)
                    break
                except InterruptedError:
                    continue
        os.setgroups([])
        os.setgid(NOBODY_ID)
        os.setuid(NOBODY_ID)
        status_text = Path("/proc/self/status").read_text(encoding="ascii")
        cap_eff = next((line.split()[1] for line in status_text.splitlines() if line.startswith("CapEff:")), None)
        oom_score_adj = Path("/proc/self/oom_score_adj").read_text(encoding="ascii").strip()
        evidence = {
            "event": "privilege_drop_verified",
            "uid": os.geteuid(),
            "gid": os.getegid(),
            "capabilities_cleared": cap_eff == "0000000000000000",
            "oom_score_adj": int(oom_score_adj),
        }
        self.emit(evidence)
        if (
            evidence["uid"] != NOBODY_ID
            or evidence["gid"] != NOBODY_ID
            or evidence["capabilities_cleared"] is not True
            or evidence["oom_score_adj"] == -1000
        ):
            raise GuardError("child_security_postcondition_failed")

    def read_profile(self) -> Mapping[str, str]:
        return dict(self._read_profile())

    def read_membership(self) -> Sequence[int]:
        return tuple(self._read_membership())

    def emit(self, event: Mapping[str, Any]) -> None:
        self._report(dict(event))

    def await_membership_verification(self, auxiliary_pid: int) -> None:
        self._await_membership(auxiliary_pid)

    def run_fixed_small_group_oom(self) -> int:
        return fixed_small_group_oom_body(
            self._report,
            self._await_membership,
            self._close_in_auxiliary,
        )
