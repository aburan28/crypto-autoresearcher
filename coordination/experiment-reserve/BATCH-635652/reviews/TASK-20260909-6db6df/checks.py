"""Independent fixed source controls for TASK-20260909-6db6df.

This checker never contacts Docker, reads or mutates a live cgroup, changes
credentials, performs a process migration, executes a pressure body, or runs a
scientific fixture.  Its only real child fixtures exercise the committed POSIX
pipe/barrier/drain/wait/reap transport under the current user.
"""
from __future__ import annotations

import argparse
import ast
from contextlib import ExitStack
from dataclasses import asdict
from datetime import datetime, timezone
import ctypes
import hashlib
from io import BytesIO
import json
import os
from pathlib import Path
import resource
import signal
import stat
import subprocess
import sys
import tarfile
import tempfile
import time
import traceback
from types import SimpleNamespace
from typing import Any, Callable, Mapping, Sequence
from unittest import mock

import yaml


TASK_ID = "TASK-20260909-6db6df"
PRODUCER_TASK_ID = "TASK-20260909-8cca96"
ARCHIVE_TASK_ID = "TASK-20260909-708ffe"
SOURCE_SNAPSHOT = "2b7ecb4ab3285174132eb37156676a6732952e95"
AUTHORITY_COMMIT = "9c5be915f59a844aa9fe2d490d9f1ce0f3eb2d1c"
CLAIM_COMMIT = "efe9afba4f3fbcd147dacda2680a007fa80cce7a"
HANDOFF_PATH = "ledger/handoffs/TASK-20260909-6db6df.yaml"
PLAN_PATH = "coordination/experiment-reserve/BATCH-635652/review-plan-TASK-20260909-6db6df.yaml"
CLAIM_PATH = "coordination/experiment-reserve/BATCH-635652/claims/TASK-20260909-6db6df.1.claim.json"
PRODUCER_BASE = "coordination/experiment-reserve/BATCH-635652/runtime/TASK-20260909-8cca96"
SNAPSHOT_PATH = "coordination/experiment-reserve/BATCH-635652/archives/TASK-20260909-a338d0/snapshot.json"
EXPECTED_REPO = "/Volumes/SSD990/crypto-autoresearcher/.worktrees/coordinator-reserve-admission-20260907"
PACKAGE_NAMES = (
    "supervisor.py",
    "container.py",
    "host.py",
    "tests.py",
    "protocol-binding.json",
    "implementation-report.yaml",
    "README.md",
)
PRODUCER_RECEIPT_NAME = "check-receipt.json"
MAX_SUITE_CASES = 128
MAX_TOTAL_CONTROLS = 384
FIXED_CONTROLS_PER_SUITE = 53
MAX_BENIGN_FIXTURE_STARTS = 32
MAX_FIXTURE_CONCURRENT = 2
MAX_FIXTURE_LIFETIME_SECONDS = 3.0
MAX_FIXTURE_PAYLOAD_BYTES = 1024 * 1024
PER_CASE_SECONDS = 10.0
AGGREGATE_SECONDS = 1800.0
MEMORY_LIMIT_BYTES = 2 * 1024 * 1024 * 1024
FAKE_ID = "a" * 64
OTHER_ID = "b" * 64
NONCE = "1" * 12


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical_sha(value: Any) -> str:
    return sha_bytes(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode())


def git_bytes(repo: Path, commit: str, path: str) -> bytes:
    return subprocess.check_output(
        ["git", "-C", str(repo), "show", f"{commit}:{path}"],
        stderr=subprocess.PIPE,
    )


def git_text(repo: Path, commit: str, path: str) -> str:
    return git_bytes(repo, commit, path).decode("utf-8", errors="strict")


def is_ancestor(repo: Path, older: str, newer: str) -> bool:
    return subprocess.run(
        ["git", "-C", str(repo), "merge-base", "--is-ancestor", older, newer],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    ).returncode == 0


def large_string_manifest(value: Any) -> list[Mapping[str, Any]]:
    rows: list[Mapping[str, Any]] = []

    def walk(current: Any, path: str) -> None:
        if isinstance(current, Mapping):
            for key, child in current.items():
                walk(child, f"{path}.{key}")
        elif isinstance(current, list):
            for index, child in enumerate(current):
                walk(child, f"{path}[{index}]")
        elif isinstance(current, str):
            raw = current.encode("utf-8")
            if len(raw) >= 1024:
                rows.append({"path": path, "bytes": len(raw), "sha256": sha_bytes(raw)})

    walk(value, "$")
    return rows


def resident_bytes(pid: int) -> tuple[int | None, str]:
    if sys.platform.startswith("linux"):
        try:
            for line in Path(f"/proc/{pid}/status").read_text(encoding="ascii").splitlines():
                if line.startswith("VmRSS:"):
                    return int(line.split()[1]) * 1024, "proc_status_vmrss"
        except (FileNotFoundError, ProcessLookupError):
            pass
        return None, "proc_status_post_exit_unavailable"
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
        try:
            info = ProcTaskInfo()
            libproc = ctypes.CDLL("/usr/lib/libproc.dylib")
            size = libproc.proc_pidinfo(pid, 4, 0, ctypes.byref(info), ctypes.sizeof(info))
            if size == ctypes.sizeof(info):
                return int(info.resident_size), "darwin_proc_pidinfo_resident_size"
        except OSError:
            pass
        return None, "darwin_proc_pidinfo_post_exit_unavailable"
    return None, "unsupported_platform"


class FixedClock:
    def __init__(self) -> None:
        self.value = 100.0

    def utc_now(self) -> str:
        self.value += 0.001
        return f"2026-09-09T00:00:{self.value % 60:09.6f}+00:00"

    def monotonic(self) -> float:
        self.value += 0.001
        return self.value


class InjectedCgroups:
    """Stateful cgroup-v2 model; it performs no live cgroup operation."""

    def __init__(self, supervisor_module: Any, faults: set[str] | None = None) -> None:
        self.s = supervisor_module
        self.faults = faults or set()
        self.root = f"docker/{FAKE_ID}"
        self.supervisor = f"{self.root}/guard-supervisor"
        self.worker = f"{self.root}/guard-worker"
        self.children: dict[str, list[str]] = {self.root: []}
        self.members: dict[str, list[int]] = {self.root: [4242]}
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
        self.trace: list[str] = []
        self.terminal_seen = False

    def open_verified_container_root(self, expected_container_id: str) -> str:
        return self.root

    def relative_path(self, handle: str) -> str:
        return handle

    def mount_facts(self, handle: str) -> Mapping[str, Any]:
        return {
            "system": "Linux", "filesystem_type": "cgroup2",
            "magic": self.s.CGROUP2_SUPER_MAGIC, "mount_point": "/host-cgroup",
            "read_write": True, "source": "cgroup2",
        }

    def read_text(self, directory: str, filename: str) -> str:
        self.trace.append(f"read:{directory}:{filename}")
        return _read_injected(self, directory, filename)

    def write_text(self, directory: str, filename: str, value: str) -> None:
        self.trace.append(f"write:{directory}:{filename}:{value}")
        if filename == "cgroup.subtree_control":
            if value == "+memory" and self.members[directory]:
                raise self.s.GuardError("synthetic_no_internal_processes")
            if value == "-memory" and "disable_failure" in self.faults:
                raise OSError("injected disable failure")
            if value == "-memory" and "disable_ignored" in self.faults:
                return
            self.files[directory][filename] = "memory\n" if value == "+memory" else ""
        else:
            self.files[directory][filename] = value + "\n"

    def create_child(self, parent: str, name: str) -> str:
        child = f"{parent}/{name}"
        self.children[parent].append(name)
        self.children[child] = []
        self.members[child] = []
        self.files[child] = {
            "cgroup.type": "domain\n", "cgroup.controllers": "memory\n",
            "cgroup.subtree_control": "", "cgroup.procs": "",
            "cgroup.events": "populated 0\n",
            "memory.events": "oom 5\noom_kill 7\noom_group_kill 3\n",
            "memory.current": "0\n", "memory.peak": "0\n", "cpu.stat": "usage_usec 0\n",
            "memory.max": "max\n", "memory.swap.max": "max\n", "memory.oom.group": "0\n",
        }
        self.trace.append(f"create:{name}")
        return child

    def list_children(self, directory: str) -> Sequence[str]:
        return tuple(self.children[directory])

    def list_direct_members(self, directory: str) -> Sequence[int]:
        if directory == self.supervisor:
            if "initial_supervisor_missing" in self.faults and not self.terminal_seen:
                return ()
            if "initial_supervisor_foreign" in self.faults and not self.terminal_seen:
                return (4242, 9999)
            if "final_supervisor_missing" in self.faults and self.terminal_seen:
                return ()
        return tuple(self.members[directory])

    def move_pid(self, directory: str, pid: int) -> None:
        self.trace.append(f"move:{pid}:{directory}")
        if "memory" in self.files[directory].get("cgroup.subtree_control", "").split():
            raise self.s.GuardError("synthetic_no_internal_processes")
        if directory == self.worker and "migration_failure" in self.faults:
            raise self.s.GuardError("injected_migration_failure")
        for row in self.members.values():
            while pid in row:
                row.remove(pid)
        self.members[directory].append(pid)
        self.files[directory]["cgroup.procs"] = "".join(f"{item}\n" for item in self.members[directory])
        self.files[directory]["cgroup.events"] = f"populated {int(bool(self.members[directory]))}\n"

    def child_is_populated(self, directory: str) -> bool:
        return bool(self.members[directory])

    def remove_empty_child(self, parent: str, name: str) -> None:
        if f"remove_{name}_failure" in self.faults:
            raise OSError("injected removal failure")
        child = f"{parent}/{name}"
        if self.members[child]:
            raise self.s.GuardError("refuse_remove_populated_cgroup")
        self.children[parent].remove(name)
        self.children.pop(child, None)
        self.members.pop(child, None)
        self.files.pop(child, None)
        self.trace.append(f"remove:{name}")

    def close_handle(self, directory: str) -> None:
        self.trace.append(f"close:{directory}")


def self_files(cgroups: InjectedCgroups, directory: str, filename: str) -> str:
    try:
        return cgroups.files[directory][filename]
    except KeyError as exc:
        raise cgroups.s.GuardError("missing_cgroup_metric", filename) from exc


# Kept outside the class body to make a misspelled/implicit dictionary access
# impossible to hide in the injected model.
def _read_injected(cgroups: InjectedCgroups, directory: str, filename: str) -> str:
    return self_files(cgroups, directory, filename)


class InjectedProcesses:
    def __init__(self, supervisor_module: Any, cgroups: InjectedCgroups, case_id: str) -> None:
        self.s = supervisor_module
        self.cg = cgroups
        self.case_id = case_id
        self.child = supervisor_module.ChildHandle(4342, "independent-synthetic-worker")
        self.forked = False
        self.released = False
        self.finalized = False
        self.confirmed = False
        self.action: Any = None

    def supervisor_pid(self) -> int:
        return 4242

    def fork_paused(self, action: Any, inherited_writable_dirs: Sequence[Any]) -> Any:
        self.action = action
        self.forked = True
        self.cg.members[self.cg.supervisor].append(self.child.pid)
        return self.child

    def release(self, child: Any) -> None:
        self.released = True

    def confirm_membership(self, child: Any, auxiliary_pid: int) -> None:
        if auxiliary_pid != 4343:
            raise self.s.GuardError("wrong_auxiliary_identity")
        self.confirmed = True

    def wait_terminal(self, child: Any, timeout_seconds: float, event_observer: Any = None, poll_observer: Any = None) -> Any:
        privilege = {
            "event": "privilege_drop_verified", "uid": 65534, "gid": 65534,
            "capabilities_cleared": True, "oom_score_adj": 0,
        }
        if self.case_id == "small_group_oom":
            early = (
                privilege,
                {"event": "worker_membership_readback", "pid": child.pid, "direct_members": [child.pid]},
                {"event": "auxiliary_spawned", "pid": 4343},
                {"event": "auxiliary_ready", "pid": 4343, "oom_score_adj": 0},
            )
            self.cg.members[self.cg.worker] = [child.pid, 4343]
            if event_observer:
                event_observer(early)
            if not self.confirmed:
                raise self.s.GuardError("membership_not_confirmed")
            late = (
                {"event": "membership_acknowledged", "pid": 4343},
                {"event": "before_allocation", "requested_bytes": 128 * self.s.MIB},
            )
            if event_observer:
                event_observer(late)
            if poll_observer:
                poll_observer()
            events = early + late
            exit_code, signal_name = None, "SIGKILL"
            self.cg.files[self.cg.worker]["memory.events"] = "oom 7\noom_kill 9\noom_group_kill 4\n"
        else:
            events = (privilege, {"event": "profile_accepted"})
            exit_code, signal_name = 0, None
        self.cg.members[self.cg.worker] = []
        self.cg.files[self.cg.worker]["cgroup.procs"] = ""
        self.cg.files[self.cg.worker]["cgroup.events"] = "populated 0\n"
        self.cg.terminal_seen = True
        self.finalized = True
        return self.s.WorkerTerminal(
            exit_code=exit_code, signal=signal_name, watchdog=False, events=events,
            effective_uid=65534, effective_gid=65534, capabilities_cleared=True,
            oom_score_adj=0, auxiliary_ready=self.case_id == "small_group_oom",
            auxiliary_children=1 if self.case_id == "small_group_oom" else 0,
            allocations_started=1 if self.case_id == "small_group_oom" else 0,
            report_complete=True, owned_pid=child.pid, reaped=True,
            descriptors_closed=True,
        )

    def finalize_owned_child(self, child: Any, terminate: bool) -> Mapping[str, Any]:
        self.finalized = True
        for row in self.cg.members.values():
            while child.pid in row:
                row.remove(child.pid)
        return {"pid": child.pid, "reaped": True, "descriptors_closed": True, "report_complete": True}

    def custody_record(self, child: Any) -> Mapping[str, Any] | None:
        return None

    def active_owned_children(self) -> Sequence[int]:
        return () if self.finalized or not self.forked else (self.child.pid,)


def run_injected_supervisor(modules: Mapping[str, Any], case_id: str = "exact_profile", faults: set[str] | None = None) -> tuple[Any, Any, Any]:
    s = modules["supervisor"]
    cg = InjectedCgroups(s, faults)
    # Bind the deliberately factored dictionary reader without using a real fs.
    cg.read_text = lambda directory, filename: (
        cg.trace.append(f"read:{directory}:{filename}") or _read_injected(cg, directory, filename)
    )
    ps = InjectedProcesses(s, cg, case_id)
    outcome = s.GroupOomSupervisor(cg, ps, FixedClock()).run(s.SupervisorRequest.fixed(case_id, FAKE_ID))
    return outcome, cg, ps


def image_json(container_module: Any) -> str:
    return json.dumps([{
        "Id": container_module.PINNED_IMAGE_DIGEST,
        "RepoDigests": [f"python@{container_module.PINNED_IMAGE_DIGEST}"],
        "Os": "linux", "Architecture": "arm64",
    }])


def inspect_json(container_module: Any, *, cid: str = FAKE_ID, nonce: str | None = NONCE,
                 running: bool = False, exit_code: int = 0, oom: bool = False) -> str:
    labels = {"crypto.autoresearch.task": container_module.TASK_ID}
    if nonce is not None:
        labels["crypto.autoresearch.nonce"] = nonce
    return json.dumps([{
        "Id": cid,
        "Image": container_module.PINNED_IMAGE_DIGEST,
        "Config": {
            "Image": container_module.PINNED_IMAGE, "Labels": labels, "User": "0:0",
            "OpenStdin": True, "AttachStdin": True, "Tty": False,
            "Cmd": ["python3", "-B", "/opt/group-oom/container.py"],
        },
        "HostConfig": {
            "NetworkMode": "none", "ReadonlyRootfs": True, "CapDrop": ["ALL"],
            "CapAdd": ["SETUID", "SETGID"], "SecurityOpt": ["no-new-privileges:true"],
            "CgroupnsMode": "host", "PidMode": "private", "PidsLimit": 32,
            "NanoCpus": 1_000_000_000, "Memory": 8 * 1024**3,
            "MemorySwap": 8 * 1024**3, "Tmpfs": {"/tmp": "rw,size=16m"},
            "Privileged": False, "AutoRemove": False,
        },
        "Mounts": [{"Type": "bind", "Source": "/sys/fs/cgroup", "Destination": "/host-cgroup", "RW": True}],
        "State": {"Running": running, "ExitCode": exit_code, "OOMKilled": oom},
    }])


def command_result(host_module: Any, argv: Sequence[str], stdin: bytes | None,
                   stdout: str = "", stderr: str = "", exit_code: int = 0,
                   timed_out: bool = False) -> Any:
    return host_module.CommandResult(
        argv=tuple(argv), started_at_UTC="2026-09-09T00:00:00+00:00",
        ended_at_UTC="2026-09-09T00:00:00.001000+00:00", exit_code=exit_code,
        stdout=stdout, stderr=stderr, timed_out=timed_out, timeout_seconds=60.0,
        wall_seconds=0.001, stdin_bytes=len(stdin or b""),
        stdin_sha256=sha_bytes(stdin) if stdin is not None else None,
        process_pid=None, process_group_id=None, terminal_observed=True,
    )


class InjectedDocker:
    def __init__(self, modules: Mapping[str, Any], case_id: str = "exact_profile", fault: str | None = None) -> None:
        self.c = modules["container"]
        self.h = modules["host"]
        self.case_id = case_id
        self.fault = fault
        self.calls: list[tuple[tuple[str, ...], bytes | None]] = []
        self.inspect_count = 0
        self.emitted = ""

    def _wire(self) -> Mapping[str, Any]:
        if self.fault == "startup_failure":
            return self.c.source_startup_failure(ValueError("independent startup failure"))
        identity = self.c.StartupIdentity(self.c.TASK_ID, FAKE_ID, self.case_id)
        outcome = self.modules_outcome(identity)
        wire = self.c.source_result(identity, outcome)
        if self.fault == "wrong_schema":
            wire["schema"] = "crypto.autoresearch.fabricated.v1"
        elif self.fault == "missing_identity":
            wire.pop("startup_identity")
        elif self.fault == "wrong_identity":
            wire["startup_identity"] = {**wire["startup_identity"], "expected_container_id": OTHER_ID}
        elif self.fault == "missing_outcome":
            wire.pop("outcome")
        elif self.fault == "false_cleanup":
            wire["outcome"]["cleanup_complete"] = 1
        elif self.fault == "wrong_status":
            wire["outcome"]["status"] = "failed"
        elif self.fault == "wrong_classification":
            wire["outcome"]["classification"] = "wrong"
        return wire

    def modules_outcome(self, identity: Any) -> Mapping[str, Any]:
        classification = {
            "exact_profile": "profile_accepted",
            "group_zero_refused": "typed_refusal",
            "small_group_oom": "oom_observed_inner_pending_outer",
        }[self.case_id]
        return {
            "task_id": identity.task_id, "case_id": identity.case_id,
            "expected_container_id": identity.expected_container_id,
            "status": "inner_complete", "classification": classification,
            "cleanup_complete": True, "failures": [], "transcript": [],
        }

    def run(self, argv: Sequence[str], stdin: bytes | None, timeout_seconds: float) -> Any:
        argv = tuple(argv)
        self.calls.append((argv, stdin))
        action = argv[3]
        if action == "image":
            return command_result(self.h, argv, stdin, image_json(self.c))
        if action == "create":
            return command_result(self.h, argv, stdin, FAKE_ID + "\n")
        if action == "inspect":
            self.inspect_count += 1
            if self.inspect_count == 1:
                cid = OTHER_ID if self.fault == "wrong_container_id" else FAKE_ID
                nonce = None if self.fault == "missing_nonce" else ("2" * 12 if self.fault == "wrong_nonce" else NONCE)
                return command_result(self.h, argv, stdin, inspect_json(self.c, cid=cid, nonce=nonce))
            return command_result(self.h, argv, stdin, inspect_json(self.c))
        if action == "cp":
            if stdin is None:
                raise AssertionError("archive stdin absent")
            with tarfile.open(fileobj=BytesIO(stdin), mode="r:") as archive:
                if sorted(archive.getnames()) != ["group-oom/container.py", "group-oom/supervisor.py"]:
                    raise AssertionError("unexpected helper archive")
            return command_result(self.h, argv, stdin)
        if action == "start":
            wire = self._wire()
            self.emitted = json.dumps(wire, sort_keys=True, separators=(",", ":")) + "\n"
            code = 2 if self.fault == "startup_failure" else 0
            return command_result(self.h, argv, stdin, self.emitted, exit_code=code)
        if action == "logs":
            return command_result(self.h, argv, stdin, self.emitted)
        if action in {"kill", "rm"}:
            return command_result(self.h, argv, stdin, FAKE_ID + "\n")
        raise AssertionError(argv)


class FixtureRuntime:
    def __init__(self, report: Any, await_membership: Any) -> None:
        self.report = report
        self.await_membership_callback = await_membership

    def emit(self, event: Mapping[str, Any]) -> None:
        self.report(dict(event))

    def await_membership_verification(self, pid: int) -> None:
        self.await_membership_callback(pid)


def fixture_factory(report: Any, inherited: Any, await_membership: Any, close_in_auxiliary: Any) -> Any:
    return FixtureRuntime(report, await_membership)


def terminal_summary(terminal: Any) -> Mapping[str, Any]:
    if isinstance(terminal, Mapping):
        return dict(terminal)
    events = []
    for event in terminal.events:
        row = {key: value for key, value in event.items() if key != "payload"}
        if "payload" in event:
            raw = str(event["payload"]).encode()
            row["payload_bytes"] = len(raw)
            row["payload_sha256"] = sha_bytes(raw)
        events.append(row)
    return {
        "owned_pid": terminal.owned_pid, "exit_code": terminal.exit_code,
        "signal": terminal.signal, "watchdog": terminal.watchdog,
        "reaped": terminal.reaped, "descriptors_closed": terminal.descriptors_closed,
        "report_complete": terminal.report_complete,
        "parent_terminated": terminal.parent_terminated, "events": events,
    }


def load_modules(source_dir: Path) -> Mapping[str, Any]:
    sys.path.insert(0, str(source_dir))
    for name in ("container", "supervisor", "host"):
        sys.modules.pop(name, None)
    import container
    import supervisor
    import host
    return {"container": container, "supervisor": supervisor, "host": host}


Case = tuple[str, Callable[[], Mapping[str, Any] | None]]


def build_cases(repo: Path, source_dir: Path, reservation: Mapping[str, Any], modules: Mapping[str, Any]) -> list[Case]:
    c, s, h = modules["container"], modules["supervisor"], modules["host"]
    producer_receipt = json.loads((source_dir / PRODUCER_RECEIPT_NAME).read_text(encoding="utf-8"))
    protocol = json.loads((source_dir / "protocol-binding.json").read_text(encoding="utf-8"))
    implementation = yaml.safe_load((source_dir / "implementation-report.yaml").read_text(encoding="utf-8"))
    cases: list[Case] = []

    def add(name: str) -> Callable[[Callable[[], Mapping[str, Any] | None]], Callable[[], Mapping[str, Any] | None]]:
        def decorate(function: Callable[[], Mapping[str, Any] | None]) -> Callable[[], Mapping[str, Any] | None]:
            cases.append((name, function))
            return function
        return decorate

    @add("binding_all_69_exact_and_origin_partition")
    def _() -> Mapping[str, Any]:
        rows = reservation["source_binding_checks"]
        assert len(rows) == 69 and sum(row["commit"] == SOURCE_SNAPSHOT for row in rows) == 68
        assert sum(row["commit"] == AUTHORITY_COMMIT for row in rows) == 1
        assert all(row["matched"] and row["same_at_authority"] for row in rows)
        return {"binding_count": len(rows), "source_snapshot_count": 68, "authority_count": 1}

    @add("binding_commit_chain_and_claim_scope")
    def _() -> Mapping[str, Any]:
        claim = reservation["claim"]
        assert is_ancestor(repo, SOURCE_SNAPSHOT, AUTHORITY_COMMIT)
        assert is_ancestor(repo, AUTHORITY_COMMIT, CLAIM_COMMIT)
        assert claim["worktree"] == EXPECTED_REPO and claim["task_id"] == TASK_ID
        assert claim["write_scope"] == reservation["write_scope"]
        return {"source_snapshot": SOURCE_SNAPSHOT, "authority": AUTHORITY_COMMIT, "claim": CLAIM_COMMIT}

    @add("binding_review_plan_matches_handoff_exactly")
    def _() -> None:
        assert reservation["review_plan"] == reservation["handoff_review_plan"]
        assert reservation["review_plan"]["source_snapshot"] == SOURCE_SNAPSHOT
        assert reservation["review_plan"]["joints"][0]["assigned_to"] == TASK_ID

    @add("binding_snapshot_archive_exact")
    def _() -> None:
        snapshot = json.loads(git_text(repo, SOURCE_SNAPSHOT, SNAPSHOT_PATH))
        assert snapshot["task_id"] == "TASK-20260909-a338d0"
        assert snapshot["source_task_ids"] == [PRODUCER_TASK_ID]
        for path, expected in snapshot["source_path_sha256"].items():
            assert sha_bytes(git_bytes(repo, SOURCE_SNAPSHOT, path)) == expected

    @add("producer_two_attempt_custody_recomputed")
    def _() -> Mapping[str, Any]:
        attempts = producer_receipt["attempts"]
        assert len(attempts) == 2
        counts = []
        pids: list[int] = []
        for attempt in attempts:
            suite = attempt["suite"]
            parsed = json.loads(attempt["stdout"])
            assert parsed == suite and attempt["suite_parse_error"] is None
            assert attempt["worker_exit_code"] == (0 if suite["passed"] else 2)
            assert all(row["matched"] for row in suite["input_binding_checks"])
            benign = suite["benign_process_accounting"]
            assert benign["actual_starts"] == 5
            assert len(benign["created_pids"]) == len(benign["terminal_statuses"]) == 5
            assert all(row["reaped"] and row["descriptors_closed"] for row in benign["terminal_statuses"])
            pids.extend(benign["created_pids"])
            counts.append((suite["fixed_case_execution_count"], suite["passed_case_count"]))
        assert counts == [(99, 98), (99, 99)] and len(set(pids)) == 10
        assert producer_receipt["accounting"]["actual_created_pids"] == pids
        return {"attempt_counts": counts, "actual_created_pids": pids}

    @add("producer_all_embedded_large_bytes_hashed")
    def _() -> Mapping[str, Any]:
        manifest = large_string_manifest(producer_receipt)
        assert len(manifest) == 20
        payloads = [row for row in manifest if row["bytes"] == 131072]
        assert len(payloads) == 4 and len({row["sha256"] for row in payloads}) == 1
        assert sha_bytes(json.dumps(producer_receipt, sort_keys=True, separators=(",", ":")).encode())
        return {"large_string_count": len(manifest), "large_strings": manifest}

    @add("producer_attempt_source_and_controller_copies_exact")
    def _() -> Mapping[str, Any]:
        attempts = producer_receipt["attempts"]
        for attempt in attempts:
            assert sha_bytes(attempt["controller_source"].encode()) == attempt["reservation"]["controller_sha256"]
            tree = ast.parse(attempt["controller_source"])
            assert not any(
                isinstance(node, ast.Attribute) and node.attr == "RLIMIT_AS"
                for node in ast.walk(tree)
            )
            for name, text in attempt["source_versions"].items():
                assert sha_bytes(text.encode()) == attempt["reservation"]["source_sha256"][name]
        for name in ("supervisor.py", "container.py", "host.py"):
            assert attempts[0]["source_versions"][name] == attempts[1]["source_versions"][name]
            assert attempts[1]["source_versions"][name].encode() == (source_dir / name).read_bytes()
        assert attempts[0]["source_versions"]["tests.py"] != attempts[1]["source_versions"]["tests.py"]
        assert producer_receipt["failed_attempt_diagnosis"]["case"] == "nf04_supervisor_final_missing"
        return {
            "controller_sha256": [sha_bytes(row["controller_source"].encode()) for row in attempts],
            "production_source_unchanged": True,
        }

    @add("producer_raw_rss_basis_and_accounting_recomputed")
    def _() -> Mapping[str, Any]:
        peaks = []
        for attempt in producer_receipt["attempts"]:
            samples = attempt["rss_samples"]
            assert samples and all(row["pid"] == attempt["worker_pid"] for row in samples)
            assert len({row["basis"] for row in samples}) == 1
            peak = max(row["rss_bytes"] for row in samples)
            assert peak == attempt["peak_observed_worker_rss_bytes"]
            assert attempt["hard_memory_guard_claim"] is False
            peaks.append(peak)
        assert max(peaks) == producer_receipt["accounting"]["maximum_sampled_worker_rss_bytes"]
        return {"sample_counts": [len(row["rss_samples"]) for row in producer_receipt["attempts"]], "peaks": peaks}

    @add("producer_metadata_and_current_hash_graph")
    def _() -> None:
        report = implementation["execution_report"]
        assert report["source_only"] is True and report["scientific_runs"] == 0
        assert report["measurement_admitted"] is False and report["source_acceptance"] is False
        assert report["accounting"]["registered_case_executions"] == 198
        assert report["accounting"]["benign_process_starts"] == 10
        for path, expected in producer_receipt["final_source_sha256"].items():
            assert sha_bytes(git_bytes(repo, SOURCE_SNAPSHOT, path)) == expected
        assert protocol["task_id"] == PRODUCER_TASK_ID and len(protocol["registered_unit_cases"]) == 99

    def run_host(case_id: str = "exact_profile", fault: str | None = None) -> tuple[Any, InjectedDocker]:
        transport = InjectedDocker(modules, case_id, fault)
        hashes = {name: sha_bytes((source_dir / name).read_bytes()) for name in h.HELPERS}
        outcome = h.DockerHostAdapter(transport, source_dir, hashes, lambda: NONCE).run_case(case_id)
        return outcome, transport

    @add("nf01_actual_serializer_to_actual_host_all_clean_cases")
    def _() -> Mapping[str, Any]:
        rows = []
        for case_id in c.CASES:
            outcome, transport = run_host(case_id)
            assert outcome.status == "complete" and outcome.exact_container_removed
            assert outcome.inner_report["schema"] == c.RESULT_SCHEMA
            rows.append({"case_id": case_id, "classification": outcome.classification, "commands": len(outcome.commands)})
        return {"cases": rows}

    for fault, expected in (
        ("startup_failure", "inner_startup_failure"),
        ("wrong_schema", "inner_report_schema_mismatch"),
        ("missing_identity", "inner_report_startup_identity_mismatch"),
        ("wrong_identity", "inner_report_startup_identity_mismatch"),
        ("missing_outcome", "inner_cleanup_or_report_incomplete"),
        ("false_cleanup", "inner_cleanup_or_report_incomplete"),
        ("wrong_status", "inner_cleanup_or_report_incomplete"),
        ("wrong_classification", "inner_classification_mismatch"),
    ):
        @add(f"nf01_{fault}_fails_closed")
        def _(fault=fault, expected=expected) -> None:
            outcome, _transport = run_host("exact_profile", fault)
            assert outcome.status == "failed" and outcome.exact_container_removed
            assert outcome.primary_failure["code"] == expected

    @add("nf02_disable_precedes_supervisor_return")
    def _() -> Mapping[str, Any]:
        outcome, cg, _ps = run_injected_supervisor(modules)
        disable = cg.trace.index(f"write:{cg.root}:cgroup.subtree_control:-memory")
        back = cg.trace.index(f"move:4242:{cg.root}")
        assert outcome.status == "inner_complete" and outcome.cleanup_complete and disable < back
        return {"disable_index": disable, "supervisor_return_index": back}

    for fault in ("disable_failure", "disable_ignored"):
        @add(f"nf02_{fault}_prevents_clean_return")
        def _(fault=fault) -> None:
            outcome, cg, _ps = run_injected_supervisor(modules, faults={fault})
            assert outcome.status == "failed_custody" and not outcome.cleanup_complete
            assert f"move:4242:{cg.root}" not in cg.trace

    @add("nf03_nonce_verified_before_copy_and_start")
    def _() -> Mapping[str, Any]:
        outcome, transport = run_host()
        actions = [argv[3] for argv, _stdin in transport.calls]
        assert outcome.status == "complete"
        assert actions.index("inspect") < actions.index("cp") < actions.index("start")
        return {"actions": actions}

    for fault in ("missing_nonce", "wrong_nonce", "wrong_container_id"):
        @add(f"nf03_{fault}_refuses_all_identity_dependent_mutation")
        def _(fault=fault) -> None:
            outcome, transport = run_host("exact_profile", fault)
            actions = [argv[3] for argv, _stdin in transport.calls]
            assert outcome.status == "failed" and not outcome.exact_container_removed
            assert not any(action in {"cp", "start", "kill", "rm"} for action in actions)
            assert outcome.cleanup == [{
                "action": "refuse_mutation_of_unverified_container_identity",
                "container_id": FAKE_ID,
                "verified_owned_identity": False,
            }]

    for fault in ("initial_supervisor_missing", "initial_supervisor_foreign", "final_supervisor_missing"):
        @add(f"nf04_{fault}_fails_closed")
        def _(fault=fault) -> None:
            outcome, cg, ps = run_injected_supervisor(modules, faults={fault})
            assert outcome.status != "inner_complete"
            if fault.startswith("initial"):
                assert not ps.forked and f"write:{cg.root}:cgroup.subtree_control:+memory" not in cg.trace
            else:
                assert outcome.failure_code == "final_supervisor_membership_mismatch"

    for error_type in (PermissionError, FileNotFoundError, OSError):
        @add(f"nf05_{error_type.__name__}_enumeration_fails_closed")
        def _(error_type=error_type) -> None:
            transport = object.__new__(s.DescriptorCgroupTransport)
            with mock.patch.object(s.os, "listdir", return_value=["foreign"]), mock.patch.object(
                s.os, "stat", side_effect=error_type("independent enumeration failure")
            ):
                try:
                    transport.list_children(SimpleNamespace(fd=42))
                except s.GuardError as exc:
                    assert exc.code == "cgroup_child_stat_failed" and "foreign" in exc.detail
                else:
                    raise AssertionError("uninspectable child was treated as absent")

    @add("prior_f01_path_import_and_native_references_resolve")
    def _() -> None:
        tree = ast.parse((source_dir / "supervisor.py").read_text(encoding="utf-8"))
        names = {alias.name for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module == "pathlib" for alias in node.names}
        assert {"Path", "PurePosixPath"} <= names

    @add("prior_f02_sigkill_is_canonical")
    def _() -> None:
        assert s.PosixProcessTransport._signal_name(-signal.SIGKILL) == "SIGKILL"

    @add("prior_f03_migration_failure_finalizes_owned_worker")
    def _() -> None:
        outcome, _cg, ps = run_injected_supervisor(modules, faults={"migration_failure"})
        assert outcome.failure_code == "injected_migration_failure" and ps.finalized
        assert not ps.active_owned_children()

    @add("prior_f03_malformed_auxiliary_ready_has_exact_cleanup")
    def _() -> None:
        reports: list[Mapping[str, Any]] = []
        with ExitStack() as stack:
            stack.enter_context(mock.patch.object(s.os, "pipe", side_effect=[(10, 11), (12, 13)]))
            stack.enter_context(mock.patch.object(s.os, "fork", return_value=9002))
            stack.enter_context(mock.patch.object(s.PosixProcessTransport, "_close_quiet"))
            stack.enter_context(mock.patch.object(s.select, "select", return_value=([10], [], [])))
            stack.enter_context(mock.patch.object(s.os, "read", side_effect=[b"{", b""]))
            killed = stack.enter_context(mock.patch.object(s.os, "kill"))
            waited = stack.enter_context(mock.patch.object(s, "_waitpid_exact", return_value=signal.SIGKILL))
            try:
                s.fixed_small_group_oom_body(reports.append, lambda _pid: None, lambda: None)
            except s.GuardError as exc:
                assert exc.code == "auxiliary_readiness_missing_or_truncated"
            else:
                raise AssertionError("malformed readiness accepted")
        killed.assert_called_once_with(9002, signal.SIGKILL)
        waited.assert_called_once_with(9002)

    @add("prior_f04_cleanup_failure_downgrades_result")
    def _() -> None:
        outcome, _cg, _ps = run_injected_supervisor(modules, faults={"remove_guard-worker_failure"})
        assert outcome.status == "failed_custody" and not outcome.cleanup_complete
        assert outcome.classification == "profile_accepted"

    @add("prior_f05_membership_poll_and_counter_delta")
    def _() -> Mapping[str, Any]:
        outcome, _cg, _ps = run_injected_supervisor(modules, "small_group_oom")
        assert outcome.status == "inner_complete"
        assert outcome.counter_deltas == {"oom_group_kill": 1, "oom_kill": 2}
        assert outcome.counter_polls
        return {"counter_deltas": outcome.counter_deltas, "polls": len(outcome.counter_polls)}

    @add("prior_f06_partial_child_create_rolls_back_or_types_failure")
    def _() -> None:
        transport = object.__new__(s.DescriptorCgroupTransport)
        transport.mount = "/unused"
        parent = SimpleNamespace(fd=42)
        with ExitStack() as stack:
            stack.enter_context(mock.patch.object(s.os, "mkdir"))
            stack.enter_context(mock.patch.object(transport, "_open_child", side_effect=OSError("open")))
            removed = stack.enter_context(mock.patch.object(s.os, "rmdir"))
            try:
                transport.create_child(parent, "guard-worker")
            except OSError:
                pass
            else:
                raise AssertionError("open failure accepted")
        removed.assert_called_once_with("guard-worker", dir_fd=42)

    @add("prior_f07_fork_failure_closes_four_pipe_descriptors")
    def _() -> None:
        transport = s.PosixProcessTransport(fixture_factory)
        with ExitStack() as stack:
            stack.enter_context(mock.patch.object(s.os, "pipe", side_effect=[(10, 11), (12, 13)]))
            stack.enter_context(mock.patch.object(s.os, "fork", side_effect=OSError("fork")))
            closed = stack.enter_context(mock.patch.object(s.PosixProcessTransport, "_close_quiet"))
            try:
                transport.fork_paused(lambda _runtime: 0, ())
            except OSError:
                pass
            else:
                raise AssertionError("fork failure accepted")
        assert {row.args[0] for row in closed.call_args_list} == {10, 11, 12, 13}

    @add("prior_f08_partial_and_interrupted_event_writes_complete")
    def _() -> None:
        read_fd, write_fd = os.pipe()
        original = os.write
        calls = 0
        def interrupted_partial(fd: int, payload: bytes) -> int:
            nonlocal calls
            calls += 1
            if calls == 1:
                raise InterruptedError()
            return original(fd, payload[:2] if calls == 2 else payload)
        try:
            with mock.patch.object(s.os, "write", side_effect=interrupted_partial):
                s.PosixProcessTransport._write_event(write_fd, {"event": "independent", "value": 1})
            os.close(write_fd)
            write_fd = -1
            assert json.loads(os.read(read_fd, 4096)) == {"event": "independent", "value": 1}
        finally:
            if write_fd >= 0:
                os.close(write_fd)
            os.close(read_fd)

    @add("prior_f09_outer_terminal_is_host_observation")
    def _() -> None:
        text = (source_dir / "supervisor.py").read_text(encoding="utf-8")
        host_text = (source_dir / "host.py").read_text(encoding="utf-8")
        assert "supervisor_alive" not in text
        assert "OOMKilled" in host_text and "terminal_container_inspections" in host_text

    @add("prior_f10_native_host_and_mount_verifier_implemented")
    def _() -> None:
        assert hasattr(h, "DockerHostAdapter") and hasattr(h, "SubprocessTransport")
        assert hasattr(s, "NativeMountVerifier") and hasattr(s, "NativeMembershipReader")
        text = (source_dir / "supervisor.py").read_text(encoding="utf-8")
        assert "fstatfs" in text and "CGROUP2_SUPER_MAGIC" in text and "O_NOFOLLOW" in text

    @add("prior_f11_historical_custody_gap_not_reconstructed")
    def _() -> None:
        gap_path = "coordination/experiment-reserve/admission-20260907/group-oom-native-prior-custody-gap.json"
        gap = json.loads(git_text(repo, SOURCE_SNAPSHOT, gap_path))
        assert gap["prior_cases_summary_only"] == 251 and gap["prior_benign_children_summary_only"] == 15
        assert producer_receipt["limitations"][3].startswith("Prior251cases and15starts remain summary-only")

    @add("break_current_container_name_uses_current_task_identity")
    def _() -> None:
        outcome, _transport = run_host()
        expected_prefix = "task-20260909-8cca96-exact-profile-"
        assert outcome.container_name.startswith(expected_prefix), (
            f"current source emitted stale container name {outcome.container_name!r}; expected prefix {expected_prefix!r}"
        )

    @add("break_owned_cgroup_removal_revalidates_created_handle_identity")
    def _() -> None:
        transport = object.__new__(s.DescriptorCgroupTransport)
        parent = SimpleNamespace(fd=42)
        created = s.DirectoryHandle(100, f"docker/{FAKE_ID}/guard-worker", 7, 11, SimpleNamespace())
        replacement = s.DirectoryHandle(101, f"docker/{FAKE_ID}/guard-worker", 7, 12, SimpleNamespace())
        with ExitStack() as stack:
            stack.enter_context(mock.patch.object(transport, "_open_child", return_value=replacement))
            stack.enter_context(mock.patch.object(transport, "child_is_populated", return_value=False))
            stack.enter_context(mock.patch.object(transport, "list_direct_members", return_value=[]))
            stack.enter_context(mock.patch.object(transport, "close_handle"))
            removed = stack.enter_context(mock.patch.object(s.os, "rmdir"))
            try:
                # The production API receives only the name, so it cannot compare
                # replacement inode 12 with the created owned handle inode 11.
                transport.remove_empty_child(parent, "guard-worker")
            except s.GuardError:
                return
        assert not removed.called, (
            f"replacement cgroup inode {(replacement.device, replacement.inode)} was removed without matching "
            f"created owned inode {(created.device, created.inode)}"
        )

    @add("break_host_launch_exception_retains_attempted_command_custody")
    def _() -> None:
        class RaisingTransport:
            def run(self, argv: Sequence[str], stdin: bytes | None, timeout_seconds: float) -> Any:
                raise OSError("independent launch failure")
        hashes = {name: sha_bytes((source_dir / name).read_bytes()) for name in h.HELPERS}
        outcome = h.DockerHostAdapter(RaisingTransport(), source_dir, hashes, lambda: NONCE).run_case("exact_profile")
        assert outcome.status == "failed" and outcome.primary_failure["code"] == "unexpected_host_error"
        assert outcome.commands, "transport launch exception erased argv/stdin/timing custody before _run appended a row"

    @add("break_release_preserves_primary_when_finalize_also_fails")
    def _() -> None:
        transport = s.PosixProcessTransport(fixture_factory)
        read_fd, write_fd = os.pipe()
        report_read, report_write = os.pipe()
        child = s.ChildHandle(999999, "synthetic-release-primary")
        state = s._PosixChildState(write_fd, report_read, child.pid)
        transport._children[child.token] = state
        os.close(write_fd)
        state.control_write_fd = write_fd
        try:
            with mock.patch.object(transport, "finalize_owned_child", side_effect=s.GuardError("secondary_cleanup_failure")):
                try:
                    transport.release(child)
                except BaseException as exc:
                    assert isinstance(exc, OSError) and "Bad file descriptor" in str(exc), (
                        f"primary release sink error was replaced by {type(exc).__name__}:{exc}"
                    )
                else:
                    raise AssertionError("release unexpectedly succeeded")
        finally:
            for fd in (read_fd, report_read, report_write):
                try:
                    os.close(fd)
                except OSError:
                    pass
            transport._children.pop(child.token, None)

    @add("limitation_memory_enable_has_no_explicit_readback")
    def _() -> Mapping[str, Any]:
        tree = ast.parse((source_dir / "supervisor.py").read_text(encoding="utf-8"))
        run = next(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == "run")
        text = ast.get_source_segment((source_dir / "supervisor.py").read_text(encoding="utf-8"), run) or ""
        enabled_line = '_must_write(self.cgroups, root, "cgroup.subtree_control", "+memory")'
        assert enabled_line in text
        return {"explicit_enable_readback_present": 'cgroup.subtree_control").split()' in text[text.index(enabled_line):text.index(enabled_line)+300]}

    @add("real_posix_large_event_drain_and_reap")
    def _() -> Mapping[str, Any]:
        transport = s.PosixProcessTransport(fixture_factory)
        payload = "x" * 131072
        child = transport.fork_paused(lambda runtime: (runtime.emit({"event": "fixture", "payload": payload}) or 0), ())
        transport.release(child)
        terminal = transport.wait_terminal(child, 2.0)
        assert terminal.exit_code == 0 and terminal.reaped and terminal.descriptors_closed and terminal.report_complete
        return {"process_starts": 1, "created_pids": [child.pid], "synthetic_marker_pids": [],
                "payload_bytes": len(payload), "terminal_statuses": [terminal_summary(terminal)], "max_concurrent": 1}

    @add("real_posix_membership_barrier")
    def _() -> Mapping[str, Any]:
        transport = s.PosixProcessTransport(fixture_factory)
        marker = os.getpid() + 100000
        def action(runtime: Any) -> int:
            runtime.emit({"event": "auxiliary_ready", "pid": marker})
            runtime.await_membership_verification(marker)
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
        return {"process_starts": 1, "created_pids": [child.pid], "synthetic_marker_pids": [marker],
                "payload_bytes": 0, "terminal_statuses": [terminal_summary(terminal)], "max_concurrent": 1}

    @add("real_posix_watchdog_signal_reap")
    def _() -> Mapping[str, Any]:
        transport = s.PosixProcessTransport(fixture_factory)
        # Exceed wait_terminal's 0.5 second grace window while remaining well
        # inside the handoff's three-second fixture-lifetime bound.
        child = transport.fork_paused(lambda _runtime: (time.sleep(1.0) or 0), ())
        transport.release(child)
        terminal = transport.wait_terminal(child, 0.05)
        assert terminal.watchdog and terminal.signal == "SIGKILL" and terminal.reaped and terminal.descriptors_closed
        return {"process_starts": 1, "created_pids": [child.pid], "synthetic_marker_pids": [],
                "payload_bytes": 0, "terminal_statuses": [terminal_summary(terminal)], "max_concurrent": 1}

    @add("real_posix_report_read_failure_reaps_and_closes")
    def _() -> Mapping[str, Any]:
        transport = s.PosixProcessTransport(fixture_factory)
        child = transport.fork_paused(lambda _runtime: (time.sleep(0.2) or 0), ())
        transport.release(child)
        os.close(transport._children[child.token].report_read_fd)
        try:
            transport.wait_terminal(child, 1.0)
        except s.GuardError as exc:
            assert exc.code == "worker_report_read_failed"
        else:
            raise AssertionError("report read failure accepted")
        custody = transport.custody_record(child)
        assert custody and custody["reaped"] and custody["descriptors_closed"] and not transport.active_owned_children()
        return {"process_starts": 1, "created_pids": [child.pid], "synthetic_marker_pids": [],
                "payload_bytes": 0, "terminal_statuses": [terminal_summary(custody)], "max_concurrent": 1}

    @add("real_posix_release_failure_reaps_and_closes")
    def _() -> Mapping[str, Any]:
        transport = s.PosixProcessTransport(fixture_factory)
        child = transport.fork_paused(lambda _runtime: 0, ())
        os.close(transport._children[child.token].control_write_fd)
        try:
            transport.release(child)
        except OSError:
            pass
        else:
            raise AssertionError("release failure accepted")
        custody = transport.custody_record(child)
        assert custody and custody["reaped"] and custody["descriptors_closed"] and not transport.active_owned_children()
        return {"process_starts": 1, "created_pids": [child.pid], "synthetic_marker_pids": [],
                "payload_bytes": 0, "terminal_statuses": [terminal_summary(custody)], "max_concurrent": 1}

    return cases


def _case_alarm(_signum: int, _frame: Any) -> None:
    raise TimeoutError(f"case exceeded {PER_CASE_SECONDS} seconds")


def run_suite(repo: Path, source_dir: Path, reservation_path: Path) -> Mapping[str, Any]:
    started = time.monotonic()
    reservation = json.loads(reservation_path.read_text(encoding="utf-8"))
    modules = load_modules(source_dir)
    definitions = build_cases(repo, source_dir, reservation, modules)
    if len(definitions) != FIXED_CONTROLS_PER_SUITE or len(definitions) != reservation["registered_controls_reserved"]:
        raise RuntimeError("fixed-control registration changed after reservation")
    if len(definitions) > MAX_SUITE_CASES:
        raise RuntimeError("suite exceeds 128 fixed controls")
    results: list[Mapping[str, Any]] = []
    signal.signal(signal.SIGALRM, _case_alarm)
    for case_id, function in definitions:
        began = time.monotonic()
        signal.setitimer(signal.ITIMER_REAL, PER_CASE_SECONDS)
        try:
            detail = function() or {}
            results.append({"id": case_id, "passed": True, "wall_seconds": time.monotonic() - began, **detail})
        except BaseException as exc:
            results.append({
                "id": case_id, "passed": False, "wall_seconds": time.monotonic() - began,
                "error_type": type(exc).__name__, "error": str(exc),
                "traceback": traceback.format_exc(),
            })
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
        if time.monotonic() - started > AGGREGATE_SECONDS:
            raise RuntimeError("aggregate executed-check bound exceeded")
    fixture_rows = [row for row in results if row.get("process_starts")]
    starts = sum(int(row.get("process_starts", 0)) for row in fixture_rows)
    pids = [pid for row in fixture_rows for pid in row.get("created_pids", [])]
    markers = [pid for row in fixture_rows for pid in row.get("synthetic_marker_pids", [])]
    terminals = [item for row in fixture_rows for item in row.get("terminal_statuses", [])]
    maximum_case_wall = max((float(row["wall_seconds"]) for row in results), default=0.0)
    maximum_fixture_wall = max((float(row["wall_seconds"]) for row in fixture_rows), default=0.0)
    max_payload = max((int(row.get("payload_bytes", 0)) for row in fixture_rows), default=0)
    max_concurrent = max((int(row.get("max_concurrent", 0)) for row in fixture_rows), default=0)
    custody_ok = (
        len(pids) == len(terminals) == starts
        and all(row.get("reaped") and row.get("descriptors_closed") for row in terminals)
    )
    return {
        "schema": "crypto.autoresearch.native_integration_independent_source_suite.v1",
        "task_id": TASK_ID,
        "producer_task_id": PRODUCER_TASK_ID,
        "source_only": True,
        "scientific_runs": 0,
        "live_docker_calls": 0,
        "live_cgroup_or_mount_accesses": 0,
        "privilege_changes": 0,
        "process_migrations": 0,
        "memory_pressure_actions": 0,
        "fixed_control_count": len(results),
        "passed_control_count": sum(bool(row["passed"]) for row in results),
        "failed_control_count": sum(not bool(row["passed"]) for row in results),
        "results": results,
        "benign_process_accounting": {
            "maximum_starts": MAX_BENIGN_FIXTURE_STARTS,
            "actual_starts": starts,
            "maximum_concurrent": MAX_FIXTURE_CONCURRENT,
            "actual_maximum_concurrent": max_concurrent,
            "maximum_child_lifetime_seconds": MAX_FIXTURE_LIFETIME_SECONDS,
            "observed_maximum_fixture_case_wall_seconds": maximum_fixture_wall,
            "lifetime_basis": "fixture case wall from before fork through terminal custody; conservative rather than exact child lifetime",
            "maximum_deliberate_payload_bytes": MAX_FIXTURE_PAYLOAD_BYTES,
            "actual_maximum_deliberate_payload_bytes": max_payload,
            "created_pids": pids,
            "synthetic_marker_pids": markers,
            "terminal_statuses": terminals,
            "all_reaped_and_descriptors_closed": custody_ok,
        },
        "maximum_case_wall_seconds": maximum_case_wall,
        "wall_seconds": time.monotonic() - started,
        "passed": all(row["passed"] for row in results) and custody_ok,
    }


def prepare_reservation(
    repo: Path,
    attempt_dir: Path,
    checker_path: Path,
    attempt_number: int,
    prior_controls: int,
    prior_starts: int,
    final_suite: bool,
) -> Mapping[str, Any]:
    if str(repo.resolve()) != EXPECTED_REPO:
        raise RuntimeError(f"explicit --repo mismatch: {repo}")
    handoff = yaml.safe_load(git_text(repo, AUTHORITY_COMMIT, HANDOFF_PATH))["handoff"]
    review_plan = yaml.safe_load(git_text(repo, AUTHORITY_COMMIT, PLAN_PATH))["review_plan"]
    claim = json.loads(git_text(repo, CLAIM_COMMIT, CLAIM_PATH))
    binding_rows = []
    for binding in handoff["source_bindings"]:
        path = binding["path"]
        commit = AUTHORITY_COMMIT if path == PLAN_PATH else SOURCE_SNAPSHOT
        raw = git_bytes(repo, commit, path)
        actual = sha_bytes(raw)
        authority_actual = sha_bytes(git_bytes(repo, AUTHORITY_COMMIT, path))
        binding_rows.append({
            "path": path, "commit": commit, "expected": binding["sha256"],
            "actual": actual, "matched": actual == binding["sha256"],
            "same_at_authority": authority_actual == actual,
        })
    try:
        git_bytes(repo, SOURCE_SNAPSHOT, PLAN_PATH)
        plan_absent = False
    except subprocess.CalledProcessError:
        plan_absent = True
    expected_scope = [
        f"coordination/experiment-reserve/BATCH-635652/reviews/{TASK_ID}/review.yaml",
        f"coordination/experiment-reserve/BATCH-635652/reviews/{TASK_ID}/checks.py",
        f"coordination/experiment-reserve/BATCH-635652/reviews/{TASK_ID}/check-receipt.json",
    ]
    final_control_reserve = 0 if final_suite else FIXED_CONTROLS_PER_SUITE
    final_start_reserve = 0 if final_suite else 5
    if prior_controls + FIXED_CONTROLS_PER_SUITE + final_control_reserve > MAX_TOTAL_CONTROLS:
        raise RuntimeError("fixed-control budget would consume the reserved final suite")
    if prior_starts + 5 + final_start_reserve > MAX_BENIGN_FIXTURE_STARTS:
        raise RuntimeError("benign-start budget would consume the reserved final suite")
    return {
        "schema": "crypto.autoresearch.native_integration_independent_reservation.v1",
        "task_id": TASK_ID,
        "reserved_at_UTC": utc_now(),
        "repo": str(repo.resolve()),
        "source_snapshot": SOURCE_SNAPSHOT,
        "authority_commit": AUTHORITY_COMMIT,
        "claim_commit": CLAIM_COMMIT,
        "checker_path": str(checker_path),
        "checker_bytes": len(checker_path.read_bytes()),
        "checker_sha256": sha_bytes(checker_path.read_bytes()),
        "attempt_dir": str(attempt_dir),
        "attempt_number": attempt_number,
        "final_suite": final_suite,
        "registered_controls_reserved": FIXED_CONTROLS_PER_SUITE,
        "benign_fixture_starts_reserved": 5,
        "prior_executed_controls": prior_controls,
        "prior_benign_fixture_starts": prior_starts,
        "final_control_reserve_after_this_attempt": final_control_reserve,
        "final_start_reserve_after_this_attempt": final_start_reserve,
        "attempt_receipt_path": str(attempt_dir / "attempt.json"),
        "terminal_command_result_path": str(attempt_dir / "command-result.json"),
        "stdout_path": str(attempt_dir / "stdout"),
        "stderr_path": str(attempt_dir / "stderr"),
        "source_dir": str(attempt_dir / "source"),
        "source_binding_checks": binding_rows,
        "plan_absent_at_source_snapshot": plan_absent,
        "review_plan": review_plan,
        "handoff_review_plan": handoff["review_plan"],
        "claim": claim,
        "write_scope": expected_scope,
        "limits": {
            "maximum_total_controls": MAX_TOTAL_CONTROLS,
            "maximum_suite_controls": MAX_SUITE_CASES,
            "maximum_benign_fixture_starts": MAX_BENIGN_FIXTURE_STARTS,
            "maximum_fixture_concurrent": MAX_FIXTURE_CONCURRENT,
            "maximum_fixture_lifetime_seconds": MAX_FIXTURE_LIFETIME_SECONDS,
            "maximum_fixture_payload_bytes": MAX_FIXTURE_PAYLOAD_BYTES,
            "per_case_seconds": PER_CASE_SECONDS,
            "aggregate_seconds": AGGREGATE_SECONDS,
            "memory_bytes": MEMORY_LIMIT_BYTES,
            "rlimit_as_attempted": False,
        },
    }


def run_controller(
    repo: Path,
    attempt_dir: Path,
    attempt_number: int,
    prior_controls: int,
    prior_starts: int,
    final_suite: bool,
) -> int:
    checker = Path(__file__).resolve()
    attempt_dir = attempt_dir.resolve()
    if not attempt_dir.is_dir():
        raise RuntimeError("attempt directory must be pre-reserved")
    if checker.parent != attempt_dir:
        raise RuntimeError("controller must run from the pre-reserved exact checker copy")
    source_dir = attempt_dir / "source"
    source_dir.mkdir(mode=0o700)
    reservation = prepare_reservation(
        repo, attempt_dir, checker, attempt_number, prior_controls, prior_starts, final_suite
    )
    reservation_path = attempt_dir / "reservation.json"
    with reservation_path.open("x", encoding="utf-8") as stream:
        json.dump(reservation, stream, indent=2, sort_keys=True)
        stream.write("\n")
    source_versions: dict[str, str] = {}
    source_sha256: dict[str, str] = {}
    for name in (*PACKAGE_NAMES, PRODUCER_RECEIPT_NAME):
        raw = git_bytes(repo, SOURCE_SNAPSHOT, f"{PRODUCER_BASE}/{name}")
        (source_dir / name).write_bytes(raw)
        source_sha256[name] = sha_bytes(raw)
        if name != PRODUCER_RECEIPT_NAME:
            source_versions[name] = raw.decode("utf-8", errors="strict")
    producer_record = json.loads((source_dir / PRODUCER_RECEIPT_NAME).read_text(encoding="utf-8"))
    large_source_records = {
        PRODUCER_RECEIPT_NAME: {
            "bytes": (source_dir / PRODUCER_RECEIPT_NAME).stat().st_size,
            "sha256": source_sha256[PRODUCER_RECEIPT_NAME],
            "large_strings": large_string_manifest(producer_record),
        }
    }
    argv = (
        sys.executable, "-B", str(checker), "--suite-json",
        "--repo", str(repo.resolve()), "--source-dir", str(source_dir),
        "--reservation", str(reservation_path),
    )
    stdout_path = attempt_dir / "stdout"
    stderr_path = attempt_dir / "stderr"
    stdout_path.touch(exist_ok=False)
    stderr_path.touch(exist_ok=False)
    attempt_path = attempt_dir / "attempt.json"
    command_result_path = attempt_dir / "command-result.json"
    started_at = utc_now()
    began = time.monotonic()
    usage_before = resource.getrusage(resource.RUSAGE_CHILDREN)
    base_attempt: dict[str, Any] = {
        "schema": "crypto.autoresearch.native_integration_independent_attempt.v1",
        "task_id": TASK_ID,
        "reservation": reservation,
        "argv": list(argv),
        "started_at_UTC": started_at,
        "checker_source": checker.read_text(encoding="utf-8"),
        "source_versions": source_versions,
        "source_sha256": source_sha256,
        "large_source_records": large_source_records,
        "rlimit_as_attempted": False,
        "scientific_runs": 0,
        "live_docker_calls": 0,
        "live_cgroup_or_mount_accesses": 0,
        "privilege_changes": 0,
        "process_migrations": 0,
        "memory_pressure_actions": 0,
    }
    try:
        stdout_stream = stdout_path.open("wb")
        stderr_stream = stderr_path.open("wb")
        process = subprocess.Popen(
            argv, cwd=str(repo.resolve()), stdin=subprocess.DEVNULL,
            stdout=stdout_stream, stderr=stderr_stream, start_new_session=True,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
    except BaseException as exc:
        base_attempt.update({
            "ended_at_UTC": utc_now(), "wall_seconds": time.monotonic() - began,
            "launch_exception": {"type": type(exc).__name__, "message": str(exc), "traceback": traceback.format_exc()},
            "terminal_observed": False, "worker_pid": None, "worker_process_group": None,
            "worker_exit_code": None, "stdout": stdout_path.read_text(errors="replace"),
            "stderr": stderr_path.read_text(errors="replace"), "rss_samples": [],
            "post_exit_rss": {"resident_bytes": None, "basis": "launch_failed"},
            "suite": None, "suite_parse_error": "launch_failed",
        })
        with command_result_path.open("x", encoding="utf-8") as stream:
            json.dump(base_attempt, stream, indent=2, sort_keys=True)
            stream.write("\n")
        with attempt_path.open("x", encoding="utf-8") as stream:
            json.dump(base_attempt, stream, indent=2, sort_keys=True)
            stream.write("\n")
        raise
    finally:
        if "stdout_stream" in locals():
            stdout_stream.close()
        if "stderr_stream" in locals():
            stderr_stream.close()
    samples: list[Mapping[str, Any]] = []
    watchdog: Mapping[str, Any] | None = None
    while process.poll() is None:
        value, basis = resident_bytes(process.pid)
        samples.append({"at_UTC": utc_now(), "pid": process.pid, "rss_bytes": value, "basis": basis})
        if value is not None and value > MEMORY_LIMIT_BYTES:
            os.killpg(process.pid, signal.SIGKILL)
            watchdog = {"reason": "resident_memory_threshold", "observed": value, "limit": MEMORY_LIMIT_BYTES}
            break
        if time.monotonic() - began > AGGREGATE_SECONDS:
            os.killpg(process.pid, signal.SIGKILL)
            watchdog = {"reason": "aggregate_wall_watchdog", "limit_seconds": AGGREGATE_SECONDS}
            break
        time.sleep(0.01)
    exit_code = process.wait()
    usage_after = resource.getrusage(resource.RUSAGE_CHILDREN)
    post_rss, post_basis = resident_bytes(process.pid)
    raw_stdout = stdout_path.read_text(encoding="utf-8", errors="replace")
    raw_stderr = stderr_path.read_text(encoding="utf-8", errors="replace")
    # Persist the terminal command result before attempting to parse stdout.
    base_attempt.update({
        "ended_at_UTC": utc_now(), "wall_seconds": time.monotonic() - began,
        "launch_exception": None, "terminal_observed": True,
        "worker_pid": process.pid, "worker_process_group": process.pid,
        "worker_exit_code": exit_code, "watchdog_stop": watchdog,
        "stdout": raw_stdout, "stderr": raw_stderr, "rss_samples": samples,
        "peak_observed_worker_rss_bytes": max((row["rss_bytes"] or 0 for row in samples), default=0),
        "peak_observed_worker_rss_basis": sorted({row["basis"] for row in samples}),
        "post_exit_rss": {"resident_bytes": post_rss, "basis": post_basis},
        "hard_kernel_memory_claim": False,
        "children_user_cpu_seconds": usage_after.ru_utime - usage_before.ru_utime,
        "children_system_cpu_seconds": usage_after.ru_stime - usage_before.ru_stime,
        "children_peak_rss_raw": usage_after.ru_maxrss,
        "suite": None, "suite_parse_error": "not_yet_parsed",
    })
    with command_result_path.open("x", encoding="utf-8") as stream:
        json.dump(base_attempt, stream, indent=2, sort_keys=True)
        stream.write("\n")
    try:
        suite = json.loads(raw_stdout)
        parse_error = None
    except BaseException as exc:
        suite = None
        parse_error = f"{type(exc).__name__}:{exc}"
    base_attempt["suite"] = suite
    base_attempt["suite_parse_error"] = parse_error
    # The terminal command record above is immutable and predates parsing.
    # The complete attempt receipt is now created once at its separate path.
    with attempt_path.open("x", encoding="utf-8") as stream:
        json.dump(base_attempt, stream, indent=2, sort_keys=True)
        stream.write("\n")
    summary = {
        "attempt_dir": str(attempt_dir), "worker_pid": process.pid,
        "worker_exit_code": exit_code, "suite_parse_error": parse_error,
        "fixed_controls": suite.get("fixed_control_count") if isinstance(suite, Mapping) else None,
        "passed_controls": suite.get("passed_control_count") if isinstance(suite, Mapping) else None,
        "fixture_starts": (suite.get("benign_process_accounting") or {}).get("actual_starts") if isinstance(suite, Mapping) else None,
        "rss_samples": len(samples), "peak_rss_bytes": base_attempt["peak_observed_worker_rss_bytes"],
        "suite_passed": suite.get("passed") if isinstance(suite, Mapping) else False,
    }
    print(json.dumps(summary, sort_keys=True))
    return 0 if exit_code == 0 and isinstance(suite, Mapping) and suite.get("passed") else 2


def assemble_receipt(output: Path, attempts: Sequence[Path], outer_responses: Sequence[str]) -> None:
    if output.exists():
        raise RuntimeError("canonical receipt already exists")
    if len(attempts) != len(outer_responses) or not attempts:
        raise RuntimeError("each terminated attempt requires one exact outer response")
    rows = []
    for path, outer_raw in zip(attempts, outer_responses, strict=True):
        attempt = json.loads(path.read_text(encoding="utf-8"))
        outer = json.loads(outer_raw)
        attempt["outer_tool_response"] = outer
        rows.append(attempt)
    total_controls = sum(int(row["suite"]["fixed_control_count"]) for row in rows if isinstance(row.get("suite"), Mapping))
    reported_starts = sum(int(row["suite"]["benign_process_accounting"]["actual_starts"]) for row in rows if isinstance(row.get("suite"), Mapping))
    unretained_fixture_starts = []
    for attempt_index, row in enumerate(rows, start=1):
        if not isinstance(row.get("suite"), Mapping):
            continue
        for result in row["suite"]["results"]:
            if (
                result["id"] == "real_posix_watchdog_signal_reap"
                and not result["passed"]
                and "assert terminal.watchdog" in result.get("traceback", "")
            ):
                unretained_fixture_starts.append({
                    "attempt": attempt_index,
                    "case_id": result["id"],
                    "basis": "traceback reaches the post-wait terminal assertion after fork_paused returned",
                    "created_pid": None,
                    "terminal_status": None,
                    "custody": "incomplete; never reconstructed",
                })
    source_derived_total_starts = reported_starts + len(unretained_fixture_starts)
    created_pids = [
        pid for row in rows if isinstance(row.get("suite"), Mapping)
        for pid in row["suite"]["benign_process_accounting"]["created_pids"]
    ]
    checker_hashes = sorted({sha_bytes(row["checker_source"].encode()) for row in rows})
    receipt = {
        "schema": "crypto.autoresearch.native_integration_independent_custody.v1",
        "task_id": TASK_ID,
        "producer_task_id": PRODUCER_TASK_ID,
        "source_snapshot": SOURCE_SNAPSHOT,
        "authority_commit": AUTHORITY_COMMIT,
        "published_claim_commit": CLAIM_COMMIT,
        "archived_by": ARCHIVE_TASK_ID,
        "created_at_UTC": utc_now(),
        "canonical_receipt_created_after_all_attempts": True,
        "no_further_invocation_planned": True,
        "attempts": rows,
        "accounting": {
            "suite_invocations": len(rows),
            "fixed_controls": total_controls,
            "maximum_fixed_controls": MAX_TOTAL_CONTROLS,
            "remaining_fixed_controls": MAX_TOTAL_CONTROLS - total_controls,
            "reported_benign_fixture_starts": reported_starts,
            "known_unretained_fixture_starts": unretained_fixture_starts,
            "source_derived_total_benign_fixture_starts": source_derived_total_starts,
            "maximum_benign_fixture_starts": MAX_BENIGN_FIXTURE_STARTS,
            "remaining_benign_fixture_starts": MAX_BENIGN_FIXTURE_STARTS - source_derived_total_starts,
            "actual_created_fixture_pids": created_pids,
            "checker_process_pids": [row.get("worker_pid") for row in rows],
            "checker_sha256": checker_hashes,
            "maximum_sampled_checker_rss_bytes": max((row.get("peak_observed_worker_rss_bytes") or 0 for row in rows), default=0),
            "raw_rss_basis": "parent samples exact owned checker PID; descendants are not aggregated; post-exit unavailability is retained",
            "rlimit_as_attempted": False,
        },
        "observations": {
            "all_source_bindings_matched": all(
                item["matched"] and item["same_at_authority"]
                for item in rows[0]["reservation"]["source_binding_checks"]
            ),
            "binding_count": len(rows[0]["reservation"]["source_binding_checks"]),
            "source_snapshot_binding_count": sum(
                item["commit"] == SOURCE_SNAPSHOT for item in rows[0]["reservation"]["source_binding_checks"]
            ),
            "authority_binding_count": sum(
                item["commit"] == AUTHORITY_COMMIT for item in rows[0]["reservation"]["source_binding_checks"]
            ),
            "failed_controls_by_attempt": [
                [{"id": result["id"], "error_type": result.get("error_type"), "error": result.get("error")}
                 for result in row["suite"]["results"] if not result["passed"]]
                for row in rows
            ],
            "scientific_runs": 0,
            "live_docker_calls": 0,
            "live_cgroup_or_mount_accesses": 0,
            "privilege_changes": 0,
            "process_migrations": 0,
            "memory_pressure_actions": 0,
        },
        "limitations": [
            "Source and fixed injected controls only; no Docker,cgroup,mount,privilege,migration,pressure or scientific execution.",
            "Parent RSS samples cover each exact owned checker PID only; raw samples and post-exit unavailability are retained. No RLIMIT_AS or hard-kernel-memory claim.",
            "Synthetic auxiliary marker PIDs are recorded separately from actual forked fixture PIDs.",
            "The producer's prior251cases and15starts remain summary-only and are not reconstructed or retrovalidated.",
            "A source failure does not establish live-platform behavior; operational admission remains a separate Coordinator decision and review chain.",
        ],
        "receipt_self_hash": None,
    }
    with output.open("x", encoding="utf-8") as stream:
        json.dump(receipt, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--suite-json", action="store_true")
    mode.add_argument("--controller", action="store_true")
    mode.add_argument("--assemble-receipt", action="store_true")
    parser.add_argument("--repo", type=Path)
    parser.add_argument("--source-dir", type=Path)
    parser.add_argument("--reservation", type=Path)
    parser.add_argument("--attempt-dir", type=Path)
    parser.add_argument("--attempt-number", type=int)
    parser.add_argument("--prior-controls", type=int, default=0)
    parser.add_argument("--prior-starts", type=int, default=0)
    parser.add_argument("--final-suite", action="store_true")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--attempt", action="append", type=Path, default=[])
    parser.add_argument("--outer-response", action="append", default=[])
    args = parser.parse_args()
    if args.suite_json:
        if not args.repo or not args.source_dir or not args.reservation:
            parser.error("suite mode requires --repo, --source-dir and --reservation")
        suite = run_suite(args.repo.resolve(), args.source_dir.resolve(), args.reservation.resolve())
        print(json.dumps(suite, sort_keys=True, separators=(",", ":"), allow_nan=False))
        return 0 if suite["passed"] else 2
    if args.controller:
        if not args.repo or not args.attempt_dir or args.attempt_number is None:
            parser.error("controller mode requires --repo, --attempt-dir and --attempt-number")
        return run_controller(
            args.repo.resolve(), args.attempt_dir, args.attempt_number,
            args.prior_controls, args.prior_starts, args.final_suite,
        )
    if not args.output:
        parser.error("assembly mode requires --output")
    assemble_receipt(args.output.resolve(), args.attempt, args.outer_response)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
