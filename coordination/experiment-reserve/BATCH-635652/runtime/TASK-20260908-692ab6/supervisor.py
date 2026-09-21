"""Prospective, dependency-injected cgroup-v2 group-OOM supervisor.

Nothing in this module contacts Docker, opens ``/host-cgroup``, changes a
credential, forks a worker, or allocates pressure at import time.  Those effects
exist only behind injected transports and are deliberately not instantiated by
this source-only task.  The fixed mock suite drives the same ``run`` method that
a later, separately approved operational handoff would use.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import json
import os
from pathlib import PurePosixPath
import re
import stat
import time
from typing import Any, Callable, Iterable, Mapping, Protocol, Sequence

from container import (
    TASK_ID,
    ContainerBindingError,
    ContainerInspection,
    allowed_cgroup_relative_paths,
    require_exact_cgroup_relative_path,
    require_full_container_id,
    require_inspection_matches,
)


GIB = 1024 * 1024 * 1024
MIB = 1024 * 1024
NOBODY_ID = 65534
CASES = ("exact_profile", "group_zero_refused", "small_group_oom")
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
FULL_ID = re.compile(r"^[0-9a-f]{64}$")


class GuardError(RuntimeError):
    """A typed refusal or controlled infrastructure failure."""

    def __init__(self, code: str, detail: str = "") -> None:
        super().__init__(f"{code}{(': ' + detail) if detail else ''}")
        self.code = code
        self.detail = detail


class CgroupTransport(Protocol):
    """The only boundary allowed to access a prospective cgroup filesystem."""

    def open_verified_container_root(self, expected_container_id: str) -> Any: ...

    def relative_path(self, handle: Any) -> str: ...

    def read_text(self, directory: Any, filename: str) -> str: ...

    def write_text(self, directory: Any, filename: str, value: str) -> None: ...

    def create_child(self, parent: Any, name: str) -> Any: ...

    def list_children(self, directory: Any) -> Sequence[str]: ...

    def list_direct_members(self, directory: Any) -> Sequence[int]: ...

    def move_pid(self, directory: Any, pid: int) -> None: ...

    def child_is_populated(self, directory: Any) -> bool: ...

    def remove_empty_child(self, parent: Any, name: str) -> None: ...

    def close_in_child(self, directory: Any) -> None: ...


@dataclass(frozen=True)
class WorkerTerminal:
    """Terminal worker observation supplied by a process transport."""

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
    manual_kill: bool = False
    reason: str = ""


@dataclass(frozen=True)
class ChildHandle:
    """A task-owned, paused child; never a PID selected by discovery."""

    pid: int
    token: str


WorkerAction = Callable[["WorkerRuntime"], int]


class ProcessTransport(Protocol):
    """Injected process boundary.  Implementations may only operate owned children."""

    def supervisor_pid(self) -> int: ...

    def fork_paused(self, action: WorkerAction, inherited_writable_dirs: Sequence[Any]) -> ChildHandle: ...

    def release(self, child: ChildHandle) -> None: ...

    def wait_terminal(self, child: ChildHandle, timeout_seconds: float) -> WorkerTerminal: ...

    def kill_owned_child(self, child: ChildHandle) -> None: ...

    def supervisor_alive(self) -> bool: ...


class Clock(Protocol):
    def utc_now(self) -> str: ...

    def monotonic(self) -> float: ...


class SystemClock:
    """Side-effect-free until a caller asks it for a timestamp."""

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
    inspection: ContainerInspection
    requested_profile: GuardProfile
    worker_timeout_seconds: float = 45.0
    case_watchdog_seconds: float = 60.0

    @staticmethod
    def fixed(case_id: str, expected_container_id: str, inspection: ContainerInspection) -> "SupervisorRequest":
        profiles = {
            "exact_profile": GuardProfile(8 * GIB, 0, 1),
            "group_zero_refused": GuardProfile(8 * GIB, 0, 0),
            "small_group_oom": GuardProfile(64 * MIB, 0, 1),
        }
        if case_id not in profiles:
            raise GuardError("unknown_fixed_case", case_id)
        return SupervisorRequest(
            task_id=TASK_ID,
            case_id=case_id,
            expected_container_id=expected_container_id,
            inspection=inspection,
            requested_profile=profiles[case_id],
        )


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
    transcript: list[Mapping[str, Any]] = field(default_factory=list)
    profile_readback: Mapping[str, str] | None = None
    baseline_metrics: Mapping[str, str | None] | None = None
    terminal: Mapping[str, Any] | None = None
    final_metrics: Mapping[str, str | None] | None = None
    cleanup: list[Mapping[str, Any]] = field(default_factory=list)
    ended_at_UTC: str | None = None
    wall_seconds: float | None = None

    def as_dict(self) -> Mapping[str, Any]:
        return asdict(self)


def required_worker_profile(case_id: str) -> GuardProfile:
    """The true guard profile.  group_zero_refused must compare against one."""

    if case_id == "small_group_oom":
        return GuardProfile(64 * MIB, 0, 1)
    if case_id in {"exact_profile", "group_zero_refused"}:
        return GuardProfile(8 * GIB, 0, 1)
    raise GuardError("unknown_fixed_case", case_id)


def _parse_events(raw: str) -> Mapping[str, int]:
    values: dict[str, int] = {}
    for line in raw.splitlines():
        fields = line.split()
        if len(fields) != 2:
            raise GuardError("malformed_counter_file", raw)
        try:
            values[fields[0]] = int(fields[1])
        except ValueError as exc:
            raise GuardError("malformed_counter_file", raw) from exc
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
    """Return the fixed non-scientific case body for a future ProcessTransport.

    The real body is selected by a later operational handoff.  This action only
    verifies profile/readiness protocol and makes no reference to experimental
    arithmetic, keys, fixtures, or research runtimes.
    """

    def action(runtime: WorkerRuntime) -> int:
        runtime.bootstrap_after_migration()
        observed = runtime.read_profile()
        expected = expected_profile.as_files()
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


class WorkerRuntime(Protocol):
    """The child-side capability exposed to an injected process implementation."""

    def bootstrap_after_migration(self) -> None: ...

    def read_profile(self) -> Mapping[str, str]: ...

    def emit(self, event: Mapping[str, Any]) -> None: ...

    def run_fixed_small_group_oom(self) -> int: ...


class GroupOomSupervisor:
    """One container, one paused worker, exact profile-before-migration ordering."""

    def __init__(self, cgroups: CgroupTransport, processes: ProcessTransport, clock: Clock | None = None) -> None:
        self.cgroups = cgroups
        self.processes = processes
        self.clock = clock or SystemClock()

    def _event(self, outcome: SupervisorOutcome, step: str, **fields: Any) -> None:
        outcome.transcript.append({"sequence": len(outcome.transcript) + 1, "at_UTC": self.clock.utc_now(), "step": step, **fields})

    def _validate_request(self, request: SupervisorRequest) -> None:
        if request.task_id != TASK_ID:
            raise GuardError("wrong_task_id")
        if request.case_id not in CASES:
            raise GuardError("unknown_fixed_case", request.case_id)
        if request.worker_timeout_seconds <= 0 or request.worker_timeout_seconds > 45:
            raise GuardError("worker_watchdog_out_of_bounds")
        if request.case_watchdog_seconds <= 0 or request.case_watchdog_seconds > 60:
            raise GuardError("case_watchdog_out_of_bounds")
        try:
            require_full_container_id(request.expected_container_id)
            require_inspection_matches(request.inspection, request.expected_container_id, request.task_id)
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
            except GuardError as exc:
                if filename in {"memory.events", "memory.current", "cgroup.events"}:
                    raise
                metrics[filename] = None
        return metrics

    def _check_root_preconditions(self, root: Any, expected_id: str, supervisor_pid: int) -> None:
        try:
            actual_path = require_exact_cgroup_relative_path(expected_id, self.cgroups.relative_path(root))
        except ContainerBindingError as exc:
            raise GuardError("cgroup_path_refused", str(exc)) from exc
        if actual_path not in allowed_cgroup_relative_paths(expected_id):
            raise GuardError("cgroup_path_refused")
        if _must_read(self.cgroups, root, "cgroup.type") != "domain":
            raise GuardError("cgroup_not_domain")
        controllers = set(_must_read(self.cgroups, root, "cgroup.controllers").split())
        if "memory" not in controllers:
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
        actual = {filename: _must_read(self.cgroups, worker, filename) for filename in profile.as_files()}
        if actual != dict(profile.as_files()):
            raise GuardError("profile_readback_mismatch", json.dumps(actual, sort_keys=True))
        return actual

    def _verify_worker_terminal(
        self,
        request: SupervisorRequest,
        child: ChildHandle,
        worker: Any,
        terminal: WorkerTerminal,
        final_metrics: Mapping[str, str | None],
    ) -> tuple[str, str]:
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
            return ("complete", "profile_accepted")
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
            return ("complete", "typed_refusal")
        if request.case_id == "small_group_oom":
            if terminal.manual_kill:
                raise GuardError("manual_or_watchdog_kill_not_oom")
            if terminal.signal != "SIGKILL" or terminal.exit_code is not None:
                raise GuardError("small_oom_terminal_not_sigkill")
            if not any(event.get("event") == "before_allocation" for event in terminal.events):
                raise GuardError("small_oom_missing_before_allocation_marker")
            if not terminal.auxiliary_ready or terminal.auxiliary_children != 1:
                raise GuardError("small_oom_auxiliary_not_ready")
            counters_text = final_metrics.get("memory.events")
            if counters_text is None:
                raise GuardError("missing_oom_event_counters")
            counters = _parse_events(counters_text)
            if counters.get("oom_group_kill", 0) < 1 or counters.get("oom_kill", 0) < 2:
                raise GuardError("small_oom_counter_threshold_not_met")
            if self.cgroups.child_is_populated(worker):
                raise GuardError("worker_subtree_still_populated")
            if not self.processes.supervisor_alive():
                raise GuardError("supervisor_did_not_survive")
            return ("complete", "oom_observed")
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
    ) -> None:
        """Retain every cleanup action; never discover or sweep foreign processes."""

        def record(action: str, ok: bool, detail: str = "") -> None:
            outcome.cleanup.append({"at_UTC": self.clock.utc_now(), "action": action, "ok": ok, "detail": detail})

        if worker is not None:
            try:
                populated = self.cgroups.child_is_populated(worker)
                record("inspect_guard_worker_population", True, str(populated))
            except Exception as exc:  # partial custody survives even a broken cleanup transport
                populated = True
                record("inspect_guard_worker_population", False, f"{type(exc).__name__}:{exc}")
            if populated and child is not None:
                try:
                    self.processes.kill_owned_child(child)
                    record("kill_exact_owned_worker_on_cleanup", True, str(child.pid))
                except Exception as exc:
                    record("kill_exact_owned_worker_on_cleanup", False, f"{type(exc).__name__}:{exc}")
                try:
                    populated = self.cgroups.child_is_populated(worker)
                    record("reinspect_guard_worker_population", not populated, str(populated))
                except Exception as exc:
                    record("reinspect_guard_worker_population", False, f"{type(exc).__name__}:{exc}")
            if not populated and root is not None:
                try:
                    self.cgroups.remove_empty_child(root, "guard-worker")
                    record("remove_empty_guard_worker", True)
                    worker = None
                except Exception as exc:
                    record("remove_empty_guard_worker", False, f"{type(exc).__name__}:{exc}")
        if root is not None and supervisor is not None and supervisor_moved:
            try:
                self.cgroups.move_pid(root, self.processes.supervisor_pid())
                record("move_supervisor_back_to_verified_root", True)
                supervisor_moved = False
            except Exception as exc:
                record("move_supervisor_back_to_verified_root", False, f"{type(exc).__name__}:{exc}")
        if root is not None and memory_enabled:
            try:
                _must_write(self.cgroups, root, "cgroup.subtree_control", "-memory")
                record("disable_only_enabled_memory_delegation", True)
                memory_enabled = False
            except Exception as exc:
                record("disable_only_enabled_memory_delegation", False, f"{type(exc).__name__}:{exc}")
        if root is not None and supervisor is not None:
            try:
                if not self.cgroups.child_is_populated(supervisor):
                    self.cgroups.remove_empty_child(root, "guard-supervisor")
                    record("remove_empty_guard_supervisor", True)
                else:
                    record("remove_empty_guard_supervisor", False, "subgroup_populated")
            except Exception as exc:
                record("remove_empty_guard_supervisor", False, f"{type(exc).__name__}:{exc}")

    def run(self, request: SupervisorRequest) -> SupervisorOutcome:
        """Execute the frozen state machine through caller-provided transports.

        Every path produces an outcome and a partial transcript.  It does not
        promote any claim and makes no assumption that the planned writable bind
        or cgroup delegation is available in a future Docker VM.
        """

        began = self.clock.monotonic()
        outcome = SupervisorOutcome(
            task_id=request.task_id,
            case_id=request.case_id,
            expected_container_id=request.expected_container_id,
            started_at_UTC=self.clock.utc_now(),
        )
        root: Any | None = None
        supervisor: Any | None = None
        worker: Any | None = None
        child: ChildHandle | None = None
        memory_enabled = False
        supervisor_moved = False
        try:
            self._validate_request(request)
            self._event(outcome, "inspection_verified_before_cgroup_mutation", container_id=request.expected_container_id)
            root = self.cgroups.open_verified_container_root(request.expected_container_id)
            self._check_root_preconditions(root, request.expected_container_id, self.processes.supervisor_pid())
            self._event(outcome, "verified_exact_container_root", path=self.cgroups.relative_path(root))

            supervisor = self.cgroups.create_child(root, "guard-supervisor")
            self._event(outcome, "created_guard_supervisor")
            self.cgroups.move_pid(supervisor, self.processes.supervisor_pid())
            supervisor_moved = True
            self._event(outcome, "supervisor_moved_outside_worker", pid=self.processes.supervisor_pid())
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
                _worker_action(request.case_id, required_worker_profile(request.case_id)), (root, supervisor, worker)
            )
            self._event(outcome, "worker_forked_behind_barrier", pid=child.pid, token=child.token)
            self.cgroups.move_pid(worker, child.pid)
            if sorted(self.cgroups.list_direct_members(worker)) != [child.pid]:
                raise GuardError("worker_not_migrated_to_guard_worker")
            self._event(outcome, "worker_migrated_before_release", pid=child.pid)
            self.processes.release(child)
            self._event(outcome, "worker_released_after_profile_and_migration", pid=child.pid)

            terminal = self.processes.wait_terminal(child, request.worker_timeout_seconds)
            outcome.terminal = asdict(terminal)
            self._event(outcome, "worker_terminal_observed", terminal=dict(outcome.terminal))
            outcome.final_metrics = self._read_metrics(worker)
            self._event(outcome, "worker_counters_retained", metrics=dict(outcome.final_metrics))
            outcome.status, outcome.classification = self._verify_worker_terminal(
                request, child, worker, terminal, outcome.final_metrics
            )
        except GuardError as exc:
            outcome.status = "refused" if exc.code in {
                "container_binding_refused",
                "cgroup_path_refused",
                "memory_controller_unavailable",
                "subtree_control_not_initially_empty",
                "unexpected_container_root_members",
                "preexisting_guard_subgroup",
                "profile_readback_mismatch",
            } else "failed"
            outcome.failure_code = exc.code
            outcome.failure_detail = exc.detail
            self._event(outcome, "typed_failure", code=exc.code, detail=exc.detail)
        except Exception as exc:  # source code must not discard an unexpected transport fault
            outcome.status = "failed"
            outcome.failure_code = "unexpected_transport_error"
            outcome.failure_detail = f"{type(exc).__name__}:{exc}"
            self._event(outcome, "unexpected_failure", error=outcome.failure_detail)
        finally:
            self._cleanup(outcome, root, supervisor, worker, child, memory_enabled, supervisor_moved)
            outcome.ended_at_UTC = self.clock.utc_now()
            outcome.wall_seconds = self.clock.monotonic() - began
        return outcome


@dataclass
class DirectoryHandle:
    """Descriptor-backed directory state for the future live transport."""

    fd: int
    relative_path: str


class DescriptorCgroupTransport:
    """A future-live cgroup-v2 adapter using directory FDs and O_NOFOLLOW.

    It is intentionally not constructed in this task.  Every component is
    opened relative to the mounted cgroup root, checked as a real directory,
    and no arbitrary filename is accepted by ``read_text`` or ``write_text``.
    """

    def __init__(self, mount: str = "/host-cgroup") -> None:
        self.mount = mount

    def _open_relative_dir(self, relative_path: str) -> DirectoryHandle:
        if PurePosixPath(relative_path).is_absolute() or any(x in {"", ".", ".."} for x in relative_path.split("/")):
            raise GuardError("cgroup_path_traversal_or_root")
        flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
        fd = os.open(self.mount, flags)
        try:
            for component in relative_path.split("/"):
                next_fd = os.open(component, flags, dir_fd=fd)
                os.close(fd)
                fd = next_fd
                if not stat.S_ISDIR(os.fstat(fd).st_mode):
                    raise GuardError("cgroup_component_not_directory", component)
            return DirectoryHandle(fd=fd, relative_path=relative_path)
        except Exception:
            os.close(fd)
            raise

    def open_verified_container_root(self, expected_container_id: str) -> DirectoryHandle:
        cid = require_full_container_id(expected_container_id)
        last_error: Exception | None = None
        for candidate in allowed_cgroup_relative_paths(cid):
            try:
                handle = self._open_relative_dir(candidate)
                require_exact_cgroup_relative_path(cid, handle.relative_path)
                return handle
            except (FileNotFoundError, GuardError, ContainerBindingError) as exc:
                last_error = exc
        raise GuardError("exact_container_cgroup_not_found", str(last_error or "no candidates"))

    def relative_path(self, handle: DirectoryHandle) -> str:
        return handle.relative_path

    @staticmethod
    def _check_name(filename: str, allowed: frozenset[str]) -> None:
        if filename not in allowed or "/" in filename or filename in {".", ".."}:
            raise GuardError("unallowlisted_cgroup_filename", filename)

    def read_text(self, directory: DirectoryHandle, filename: str) -> str:
        self._check_name(filename, READ_FILES)
        fd = os.open(filename, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=directory.fd)
        try:
            chunks: list[bytes] = []
            while True:
                block = os.read(fd, 65536)
                if not block:
                    break
                chunks.append(block)
            return b"".join(chunks).decode("ascii")
        finally:
            os.close(fd)

    def write_text(self, directory: DirectoryHandle, filename: str, value: str) -> None:
        self._check_name(filename, WRITE_FILES)
        if not value or "\x00" in value:
            raise GuardError("invalid_cgroup_write_value", filename)
        fd = os.open(filename, os.O_WRONLY | os.O_NOFOLLOW, dir_fd=directory.fd)
        try:
            payload = (value + "\n").encode("ascii")
            if os.write(fd, payload) != len(payload):
                raise GuardError("partial_cgroup_write", filename)
        finally:
            os.close(fd)

    def create_child(self, parent: DirectoryHandle, name: str) -> DirectoryHandle:
        if name not in CHILD_NAMES:
            raise GuardError("unallowlisted_cgroup_child", name)
        os.mkdir(name, mode=0o755, dir_fd=parent.fd)
        return self._open_child(parent, name)

    def _open_child(self, parent: DirectoryHandle, name: str) -> DirectoryHandle:
        if name not in CHILD_NAMES:
            raise GuardError("unallowlisted_cgroup_child", name)
        fd = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent.fd)
        return DirectoryHandle(fd=fd, relative_path=f"{parent.relative_path}/{name}")

    def list_children(self, directory: DirectoryHandle) -> Sequence[str]:
        names = os.listdir(f"/proc/self/fd/{directory.fd}")
        children: list[str] = []
        for name in names:
            try:
                mode = os.stat(name, dir_fd=directory.fd, follow_symlinks=False).st_mode
            except OSError:
                continue
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
            if self.child_is_populated(child):
                raise GuardError("refuse_remove_populated_cgroup", name)
        finally:
            os.close(child.fd)
        os.rmdir(name, dir_fd=parent.fd)

    def close_in_child(self, directory: DirectoryHandle) -> None:
        os.close(directory.fd)

    def open_verified_worker_readonly(self, expected_container_id: str, worker_relative_path: str) -> DirectoryHandle:
        """Re-open only the worker directory after the child closed inherited FDs."""

        root = require_exact_cgroup_relative_path(expected_container_id, worker_relative_path.rsplit("/", 1)[0])
        expected = f"{root}/guard-worker"
        if worker_relative_path != expected:
            raise GuardError("worker_path_not_exact_verified_descendant")
        return self._open_relative_dir(worker_relative_path)


@dataclass
class _PosixChildState:
    release_write_fd: int
    report_read_fd: int
    pid: int
    released: bool = False


class PosixProcessTransport:
    """Future-live POSIX process boundary with a fork barrier and retained reports.

    Constructing the adapter does nothing.  A later operational handoff may pass
    it a factory that re-opens the already verified worker cgroup read-only and
    supplies the fixed, non-scientific worker body.  This class never chooses a
    PID by discovery and only signals handles it created.
    """

    def __init__(self, runtime_factory: Callable[[Callable[[Mapping[str, Any]], None], Sequence[DirectoryHandle]], WorkerRuntime]) -> None:
        self._runtime_factory = runtime_factory
        self._children: dict[str, _PosixChildState] = {}

    def supervisor_pid(self) -> int:
        return os.getpid()

    @staticmethod
    def _write_event(fd: int, event: Mapping[str, Any]) -> None:
        payload = (json.dumps(dict(event), sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
        os.write(fd, payload)

    def fork_paused(self, action: WorkerAction, inherited_writable_dirs: Sequence[Any]) -> ChildHandle:
        release_read, release_write = os.pipe()
        report_read, report_write = os.pipe()
        token = os.urandom(16).hex()
        pid = os.fork()
        if pid == 0:  # future worker path only; no source-task execution reaches it
            try:
                os.close(release_write)
                os.close(report_read)
                if os.read(release_read, 1) != b"R":
                    self._write_event(report_write, {"event": "barrier_failure"})
                    os._exit(71)
                runtime = self._runtime_factory(
                    lambda event: self._write_event(report_write, event),
                    tuple(inherited_writable_dirs),
                )
                exit_code = action(runtime)
                self._write_event(report_write, {"event": "worker_exit", "exit_code": exit_code})
                os._exit(exit_code)
            except BaseException as exc:
                try:
                    self._write_event(report_write, {"event": "worker_error", "type": type(exc).__name__, "message": str(exc)})
                finally:
                    os._exit(70)
        os.close(release_read)
        os.close(report_write)
        self._children[token] = _PosixChildState(release_write, report_read, pid)
        return ChildHandle(pid=pid, token=token)

    def release(self, child: ChildHandle) -> None:
        state = self._children.get(child.token)
        if state is None or state.pid != child.pid or state.released:
            raise GuardError("unknown_or_already_released_child")
        if os.write(state.release_write_fd, b"R") != 1:
            raise GuardError("worker_barrier_release_failed")
        os.close(state.release_write_fd)
        state.released = True

    @staticmethod
    def _decode_events(raw: bytes) -> tuple[Mapping[str, Any], ...]:
        events: list[Mapping[str, Any]] = []
        for line in raw.decode("utf-8", errors="replace").splitlines():
            try:
                value = json.loads(line)
            except json.JSONDecodeError:
                value = {"event": "malformed_worker_report", "line": line}
            if isinstance(value, Mapping):
                events.append(dict(value))
        return tuple(events)

    def wait_terminal(self, child: ChildHandle, timeout_seconds: float) -> WorkerTerminal:
        state = self._children.get(child.token)
        if state is None or state.pid != child.pid or not state.released:
            raise GuardError("unknown_or_unreleased_child")
        deadline = time.monotonic() + timeout_seconds
        status: int | None = None
        while time.monotonic() < deadline:
            waited, candidate = os.waitpid(child.pid, os.WNOHANG)
            if waited == child.pid:
                status = candidate
                break
            time.sleep(0.01)
        watchdog = status is None
        if watchdog:
            self.kill_owned_child(child)
            _, status = os.waitpid(child.pid, 0)
        chunks: list[bytes] = []
        while True:
            data = os.read(state.report_read_fd, 65536)
            if not data:
                break
            chunks.append(data)
        os.close(state.report_read_fd)
        self._children.pop(child.token, None)
        events = self._decode_events(b"".join(chunks))
        privilege = next((event for event in events if event.get("event") == "privilege_drop_verified"), {})
        exit_code = os.waitstatus_to_exitcode(status)
        signal = None if exit_code >= 0 else f"SIG{abs(exit_code)}"
        return WorkerTerminal(
            exit_code=None if exit_code < 0 else exit_code,
            signal=signal,
            watchdog=watchdog,
            events=events,
            effective_uid=privilege.get("uid"),
            effective_gid=privilege.get("gid"),
            capabilities_cleared=privilege.get("capabilities_cleared"),
            oom_score_adj=privilege.get("oom_score_adj"),
            auxiliary_ready=any(event.get("event") == "auxiliary_ready" for event in events),
            auxiliary_children=sum(1 for event in events if event.get("event") == "auxiliary_ready"),
            allocations_started=sum(1 for event in events if event.get("event") == "before_allocation"),
            manual_kill=watchdog,
            reason="watchdog" if watchdog else "terminal_wait_status",
        )

    def kill_owned_child(self, child: ChildHandle) -> None:
        state = self._children.get(child.token)
        if state is None or state.pid != child.pid:
            raise GuardError("refuse_kill_unowned_child")
        os.kill(child.pid, 9)

    def supervisor_alive(self) -> bool:
        return True


def fixed_small_group_oom_body(report: Callable[[Mapping[str, Any]], None]) -> int:
    """The future operational non-scientific 16MiB+128MiB case body.

    This function is never called by the source-task check.  In a live case the
    supervisor has already applied and read back the exact 64MiB/0/1 worker
    profile and migrated this worker.  The auxiliary inherits that same worker
    cgroup; no process is moved after pressure begins.
    """

    ready_read, ready_write = os.pipe()
    hold_read, hold_write = os.pipe()
    auxiliary_pid = os.fork()
    if auxiliary_pid == 0:
        os.close(ready_read)
        os.close(hold_write)
        try:
            allocation = bytearray(16 * MIB)
            for offset in range(0, len(allocation), 4096):
                allocation[offset] = 1
            oom_score_adj = Path("/proc/self/oom_score_adj").read_text(encoding="ascii").strip()
            os.write(ready_write, json.dumps({"pid": os.getpid(), "oom_score_adj": int(oom_score_adj)}).encode("ascii"))
            os.read(hold_read, 1)
            os._exit(0)
        except BaseException:
            os._exit(72)
    os.close(ready_write)
    os.close(hold_read)
    raw = os.read(ready_read, 4096)
    try:
        ready = json.loads(raw.decode("ascii"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise GuardError("auxiliary_readiness_missing") from exc
    if ready.get("oom_score_adj") == -1000:
        raise GuardError("auxiliary_protected_from_oom")
    report({"event": "auxiliary_ready", "pid": ready.get("pid"), "oom_score_adj": ready.get("oom_score_adj")})
    report({"event": "before_allocation", "requested_bytes": 128 * MIB})
    allocation = bytearray(128 * MIB)
    for offset in range(0, len(allocation), 4096):
        allocation[offset] = 1
    os.write(hold_write, b"X")
    os.waitpid(auxiliary_pid, 0)
    report({"event": "unexpected_allocation_survival", "bytes": len(allocation)})
    return 73


def make_posix_runtime_factory(
    cgroups: DescriptorCgroupTransport,
    expected_container_id: str,
    worker_relative_path: str,
) -> Callable[[Callable[[Mapping[str, Any]], None], Sequence[DirectoryHandle]], WorkerRuntime]:
    """Build the future child factory that reopens only its exact worker cgroup."""

    def factory(report: Callable[[Mapping[str, Any]], None], inherited: Sequence[DirectoryHandle]) -> WorkerRuntime:
        def read_profile() -> Mapping[str, str]:
            directory = cgroups.open_verified_worker_readonly(expected_container_id, worker_relative_path)
            try:
                return {name: _must_read(cgroups, directory, name) for name in ("memory.max", "memory.swap.max", "memory.oom.group")}
            finally:
                os.close(directory.fd)

        return PosixWorkerRuntime(
            read_profile=read_profile,
            inherited_writable_dirs=inherited,
            report=report,
            small_oom_body=lambda: fixed_small_group_oom_body(report),
        )

    return factory


class PosixWorkerRuntime:
    """Future child helper: close cgroup write FDs, then drop before case work."""

    def __init__(
        self,
        read_profile: Callable[[], Mapping[str, str]],
        inherited_writable_dirs: Sequence[DirectoryHandle],
        report: Callable[[Mapping[str, Any]], None],
        small_oom_body: Callable[[], int],
    ) -> None:
        self._read_profile = read_profile
        self._inherited = tuple(inherited_writable_dirs)
        self._report = report
        self._small_oom_body = small_oom_body

    def bootstrap_after_migration(self) -> None:
        for directory in self._inherited:
            os.close(directory.fd)
        os.setgroups([])
        os.setgid(NOBODY_ID)
        os.setuid(NOBODY_ID)
        status_text = Path("/proc/self/status").read_text(encoding="ascii")
        cap_eff = next((line.split()[1] for line in status_text.splitlines() if line.startswith("CapEff:")), None)
        oom_score_adj = Path("/proc/self/oom_score_adj").read_text(encoding="ascii").strip()
        self.emit(
            {
                "event": "privilege_drop_verified",
                "uid": os.geteuid(),
                "gid": os.getegid(),
                "capabilities_cleared": cap_eff == "0000000000000000",
                "oom_score_adj": int(oom_score_adj),
            }
        )
        if os.geteuid() != NOBODY_ID or os.getegid() != NOBODY_ID or cap_eff != "0000000000000000" or oom_score_adj == "-1000":
            raise GuardError("child_security_postcondition_failed")

    def read_profile(self) -> Mapping[str, str]:
        return dict(self._read_profile())

    def emit(self, event: Mapping[str, Any]) -> None:
        self._report(dict(event))

    def run_fixed_small_group_oom(self) -> int:
        return self._small_oom_body()
