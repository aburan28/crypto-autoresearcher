"""Fixed ordinary-filesystem/mock checks for TASK-20260908-692ab6.

The suite never creates a container, contacts a Docker API, opens a cgroup,
changes credentials, or creates pressure.  It imports the production state
machine and supplies synthetic cgroup/process observations.  ``--run-final``
spawns one ordinary Python child to capture complete stdout/stderr and writes
the seventh task artifact, ``check-receipt.json``.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import json
from pathlib import Path
import resource
import subprocess
import sys
import time
from typing import Any, Mapping, Sequence

from container import ContainerInspection, PlannedMount, TASK_ID, planned_container
from supervisor import (
    ChildHandle,
    CgroupTransport,
    GIB,
    MIB,
    GroupOomSupervisor,
    GuardError,
    GuardProfile,
    ProcessTransport,
    SupervisorRequest,
    WorkerAction,
    WorkerRuntime,
    WorkerTerminal,
)


HERE = Path(__file__).resolve().parent
RECEIPT = HERE / "check-receipt.json"
FINAL_SUITE_CASES = 45
MAX_FIXED_CASES = 320
FAKE_ID = "a" * 64


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def inspection(container_id: str = FAKE_ID) -> ContainerInspection:
    plan = planned_container()
    return ContainerInspection(
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


class SyntheticCgroups(CgroupTransport):
    """A fixed cgroup-v2 model; it is ordinary in-memory data, never /sys."""

    def __init__(self, faults: set[str]) -> None:
        self.faults = faults
        self.root = f"docker/{FAKE_ID}"
        self.files: dict[str, dict[str, str]] = {
            self.root: {
                "cgroup.type": "domain",
                "cgroup.controllers": "cpu memory pids",
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
        self.after_terminal = False
        self.worker_path: str | None = None
        self.writes: list[tuple[str, str, str]] = []
        if "bad_path_traversal" in faults:
            self.root = f"docker/{FAKE_ID}/../other"
        elif "bad_path_root" in faults:
            self.root = ""
        elif "bad_path_parent" in faults:
            self.root = "docker"
        if "unexpected_root_members" in faults:
            self.members[f"docker/{FAKE_ID}"] = [4242, 8888]
        if "preexisting_guard" in faults:
            self.children[f"docker/{FAKE_ID}"].append("guard-worker")
        if "preexisting_generic" in faults:
            self.children[f"docker/{FAKE_ID}"].append("foreign-child")
        if "missing_controller" in faults:
            self.files[f"docker/{FAKE_ID}"]["cgroup.controllers"] = "cpu pids\n"
        if "nonempty_subtree_control" in faults:
            self.files[f"docker/{FAKE_ID}"]["cgroup.subtree_control"] = "memory\n"
        if "not_domain" in faults:
            self.files[f"docker/{FAKE_ID}"]["cgroup.type"] = "threaded\n"

    def open_verified_container_root(self, expected_container_id: str) -> str:
        if "missing_root" in self.faults:
            raise GuardError("exact_container_cgroup_not_found")
        if "symlink" in self.faults:
            raise GuardError("symlink_component_refused")
        if expected_container_id != FAKE_ID:
            raise GuardError("exact_container_cgroup_not_found")
        return self.root

    def relative_path(self, handle: str) -> str:
        return handle

    def read_text(self, directory: str, filename: str) -> str:
        if "missing_events" in self.faults and self.after_terminal and filename == "memory.events":
            raise GuardError("missing_cgroup_metric", filename)
        if directory not in self.files or filename not in self.files[directory]:
            raise GuardError("missing_cgroup_metric", filename)
        value = self.files[directory][filename]
        if "profile_readback_mismatch" in self.faults and directory == self.worker_path and filename == "memory.oom.group":
            return "0\n" if value.strip() == "1" else "1\n"
        return value

    def write_text(self, directory: str, filename: str, value: str) -> None:
        if "write_error" in self.faults and filename == "memory.max":
            raise OSError("synthetic readonly/delegation failure")
        if "partial_write" in self.faults and filename == "memory.swap.max":
            raise GuardError("partial_cgroup_write", filename)
        self.writes.append((directory, filename, value))
        self.files[directory][filename] = value + "\n"

    def create_child(self, parent: str, name: str) -> str:
        if name in self.children[parent]:
            raise GuardError("cgroup_child_already_exists", name)
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
            "memory.events": "oom 0\noom_kill 0\noom_group_kill 0\n",
            "memory.current": "0\n",
            "memory.peak": "0\n",
            "cpu.stat": "usage_usec 0\n",
            "memory.max": "max\n",
            "memory.swap.max": "max\n",
            "memory.oom.group": "0\n",
        }
        if name == "guard-worker":
            self.worker_path = child
        return child

    def list_children(self, directory: str) -> Sequence[str]:
        return list(self.children[directory])

    def list_direct_members(self, directory: str) -> Sequence[int]:
        if "child_not_migrated" in self.faults and directory == self.worker_path:
            return []
        return list(self.members[directory])

    def move_pid(self, directory: str, pid: int) -> None:
        if directory == f"docker/{FAKE_ID}/guard-supervisor":
            self.members[f"docker/{FAKE_ID}"] = []
        if directory == self.worker_path and "migration_transport_error" in self.faults:
            raise GuardError("worker_migration_transport_error")
        for members in self.members.values():
            if pid in members:
                members.remove(pid)
        self.members[directory] = [pid]
        self.files[directory]["cgroup.procs"] = f"{pid}\n"
        self.files[directory]["cgroup.events"] = "populated 1\n"

    def child_is_populated(self, directory: str) -> bool:
        if "worker_still_populated" in self.faults and directory == self.worker_path:
            return True
        return bool(self.members[directory])

    def remove_empty_child(self, parent: str, name: str) -> None:
        if "worker_cleanup_failure" in self.faults and name == "guard-worker":
            raise OSError("synthetic worker cleanup failure")
        if "supervisor_cleanup_failure" in self.faults and name == "guard-supervisor":
            raise OSError("synthetic supervisor cleanup failure")
        child = f"{parent}/{name}"
        if self.child_is_populated(child):
            raise GuardError("refuse_remove_populated_cgroup")
        self.children[parent].remove(name)
        self.children.pop(child, None)
        self.members.pop(child, None)
        self.files.pop(child, None)

    def close_in_child(self, directory: str) -> None:
        return None

    def make_terminal_state(self, case_id: str) -> None:
        self.after_terminal = True
        if self.worker_path is None:
            return
        self.members[self.worker_path] = []
        self.files[self.worker_path]["cgroup.procs"] = ""
        self.files[self.worker_path]["cgroup.events"] = "populated 0\n"
        if case_id == "small_group_oom":
            counts = "oom 1\noom_kill 2\noom_group_kill 1\n"
            if "low_oom_counters" in self.faults:
                counts = "oom 1\noom_kill 1\noom_group_kill 0\n"
            self.files[self.worker_path]["memory.events"] = counts


class SyntheticRuntime(WorkerRuntime):
    def __init__(self, cgroups: SyntheticCgroups, case_id: str, faults: set[str]) -> None:
        self.cgroups = cgroups
        self.case_id = case_id
        self.faults = faults
        self.events: list[Mapping[str, Any]] = []

    def bootstrap_after_migration(self) -> None:
        if "bootstrap_failure" in self.faults:
            raise GuardError("synthetic_drop_failure")
        self.emit(
            {
                "event": "privilege_drop_verified",
                "uid": 0 if "uid_failure" in self.faults else 65534,
                "gid": 0 if "gid_failure" in self.faults else 65534,
                "capabilities_cleared": "capability_failure" not in self.faults,
                "oom_score_adj": -1000 if "protected_oom" in self.faults else 0,
            }
        )

    def read_profile(self) -> Mapping[str, str]:
        assert self.cgroups.worker_path is not None
        return {
            name: self.cgroups.read_text(self.cgroups.worker_path, name).strip()
            for name in ("memory.max", "memory.swap.max", "memory.oom.group")
        }

    def emit(self, event: Mapping[str, Any]) -> None:
        self.events.append(dict(event))

    def run_fixed_small_group_oom(self) -> int:
        if "missing_aux_ready" not in self.faults:
            self.emit({"event": "auxiliary_ready", "pid": 4343, "oom_score_adj": 0})
        if "missing_before_marker" not in self.faults:
            self.emit({"event": "before_allocation", "requested_bytes": 128 * MIB})
        return 137


class SyntheticProcesses(ProcessTransport):
    def __init__(self, cgroups: SyntheticCgroups, case_id: str, faults: set[str]) -> None:
        self.cgroups = cgroups
        self.case_id = case_id
        self.faults = faults
        self.action: WorkerAction | None = None
        self.runtime = SyntheticRuntime(cgroups, case_id, faults)
        self.released = False
        self.killed = False

    def supervisor_pid(self) -> int:
        return 4242

    def fork_paused(self, action: WorkerAction, inherited_writable_dirs: Sequence[Any]) -> ChildHandle:
        self.action = action
        return ChildHandle(pid=4342, token="synthetic-owned-worker")

    def release(self, child: ChildHandle) -> None:
        if child.token != "synthetic-owned-worker":
            raise GuardError("unknown_or_already_released_child")
        self.released = True
        assert self.action is not None
        try:
            self.action(self.runtime)
        except GuardError as exc:
            self.runtime.emit({"event": "worker_error", "code": exc.code})

    def wait_terminal(self, child: ChildHandle, timeout_seconds: float) -> WorkerTerminal:
        if not self.released:
            raise GuardError("unknown_or_unreleased_child")
        self.cgroups.make_terminal_state(self.case_id)
        events = list(self.runtime.events)
        if "missing_profile_accepted" in self.faults:
            events = [event for event in events if event.get("event") != "profile_accepted"]
        if "missing_typed_refusal" in self.faults:
            events = [event for event in events if event.get("event") != "typed_configuration_refusal"]
        privilege = next((event for event in events if event.get("event") == "privilege_drop_verified"), {})
        exit_code: int | None = 0 if self.case_id == "exact_profile" else 42 if self.case_id == "group_zero_refused" else None
        signal: str | None = None if self.case_id != "small_group_oom" else "SIGKILL"
        if "bad_exact_terminal" in self.faults:
            exit_code = 7
        if "bad_group_zero_terminal" in self.faults:
            exit_code = 0
        if "non_sigkill" in self.faults:
            signal = "SIGTERM"
        return WorkerTerminal(
            exit_code=exit_code,
            signal=signal,
            watchdog="watchdog" in self.faults,
            events=tuple(events),
            effective_uid=privilege.get("uid"),
            effective_gid=privilege.get("gid"),
            capabilities_cleared=privilege.get("capabilities_cleared"),
            oom_score_adj=privilege.get("oom_score_adj"),
            auxiliary_ready=any(event.get("event") == "auxiliary_ready" for event in events),
            auxiliary_children=sum(1 for event in events if event.get("event") == "auxiliary_ready"),
            allocations_started=(1 if "group_zero_allocates" in self.faults and self.case_id == "group_zero_refused" else sum(1 for event in events if event.get("event") == "before_allocation")),
            manual_kill="manual_kill" in self.faults,
            reason="synthetic terminal",
        )

    def kill_owned_child(self, child: ChildHandle) -> None:
        if child.token != "synthetic-owned-worker":
            raise GuardError("refuse_kill_unowned_child")
        self.killed = True
        if self.cgroups.worker_path is not None:
            self.cgroups.members[self.cgroups.worker_path] = []

    def supervisor_alive(self) -> bool:
        return "supervisor_dead" not in self.faults


def run_case(name: str, case_id: str, faults: set[str], expected_code: str | None, expect_success: bool = False) -> Mapping[str, Any]:
    cgroups = SyntheticCgroups(faults)
    processes = SyntheticProcesses(cgroups, case_id, faults)
    request = SupervisorRequest.fixed(case_id, FAKE_ID, inspection())
    if "short_id" in faults:
        request = SupervisorRequest.fixed(case_id, "a" * 63, inspection())
    if "upper_id" in faults:
        request = SupervisorRequest.fixed(case_id, "A" * 64, inspection("A" * 64))
    if "inspection_mismatch" in faults:
        request = SupervisorRequest.fixed(case_id, FAKE_ID, inspection("b" * 64))
    if "wrong_task" in faults:
        request = SupervisorRequest(
            task_id="TASK-00000000-deadbe",
            case_id=case_id,
            expected_container_id=FAKE_ID,
            inspection=inspection(),
            requested_profile=request.requested_profile,
        )
    if "profile_parameter_changed" in faults:
        request = SupervisorRequest(
            task_id=TASK_ID,
            case_id=case_id,
            expected_container_id=FAKE_ID,
            inspection=inspection(),
            requested_profile=GuardProfile(123, 0, 1),
        )
    outcome = GroupOomSupervisor(cgroups, processes).run(request)
    passed = bool(outcome.transcript) and (outcome.failure_code == expected_code if expected_code else outcome.status == "complete")
    if expect_success:
        passed = passed and outcome.classification in {"profile_accepted", "typed_refusal", "oom_observed"}
    cleanup_failure_retained = any(action["ok"] is False for action in outcome.cleanup)
    if "worker_cleanup_failure" in faults or "supervisor_cleanup_failure" in faults:
        passed = passed and cleanup_failure_retained
    return {
        "id": name,
        "passed": passed,
        "expected_failure_code": expected_code,
        "actual_status": outcome.status,
        "actual_classification": outcome.classification,
        "actual_failure_code": outcome.failure_code,
        "transcript_persisted": bool(outcome.transcript),
        "cleanup_failure_retained": cleanup_failure_retained,
        "cleanup_actions": len(outcome.cleanup),
        "ordering": [event["step"] for event in outcome.transcript],
    }


def full_suite() -> Mapping[str, Any]:
    vectors: list[tuple[str, str, set[str], str | None, bool]] = [
        ("exact_profile_pass", "exact_profile", set(), None, True),
        ("group_zero_typed_refusal_pass", "group_zero_refused", set(), None, True),
        ("small_group_oom_pass", "small_group_oom", set(), None, True),
        ("wrong_short_id", "exact_profile", {"short_id"}, "container_binding_refused", False),
        ("wrong_upper_id", "exact_profile", {"upper_id"}, "container_binding_refused", False),
        ("inspection_id_mismatch", "exact_profile", {"inspection_mismatch"}, "container_binding_refused", False),
        ("traversal_path", "exact_profile", {"bad_path_traversal"}, "cgroup_path_refused", False),
        ("root_path", "exact_profile", {"bad_path_root"}, "cgroup_path_refused", False),
        ("parent_path", "exact_profile", {"bad_path_parent"}, "cgroup_path_refused", False),
        ("symlink_component", "exact_profile", {"symlink"}, "symlink_component_refused", False),
        ("missing_exact_root", "exact_profile", {"missing_root"}, "exact_container_cgroup_not_found", False),
        ("unexpected_root_members", "exact_profile", {"unexpected_root_members"}, "unexpected_container_root_members", False),
        ("preexisting_guard_directory", "exact_profile", {"preexisting_guard"}, "preexisting_guard_subgroup", False),
        ("preexisting_generic_directory", "exact_profile", {"preexisting_generic"}, "preexisting_guard_subgroup", False),
        ("memory_controller_missing", "exact_profile", {"missing_controller"}, "memory_controller_unavailable", False),
        ("subtree_control_not_empty", "exact_profile", {"nonempty_subtree_control"}, "subtree_control_not_initially_empty", False),
        ("non_domain_root", "exact_profile", {"not_domain"}, "cgroup_not_domain", False),
        ("delegation_write_error", "exact_profile", {"write_error"}, "unexpected_transport_error", False),
        ("partial_profile_write", "exact_profile", {"partial_write"}, "partial_cgroup_write", False),
        ("profile_readback_mismatch", "exact_profile", {"profile_readback_mismatch"}, "profile_readback_mismatch", False),
        ("worker_migration_transport_failure", "exact_profile", {"migration_transport_error"}, "worker_migration_transport_error", False),
        ("worker_not_migrated", "exact_profile", {"child_not_migrated"}, "worker_not_migrated_to_guard_worker", False),
        ("dropped_uid_failure", "exact_profile", {"uid_failure"}, "worker_privilege_drop_failed", False),
        ("dropped_gid_failure", "exact_profile", {"gid_failure"}, "worker_privilege_drop_failed", False),
        ("capability_failure", "exact_profile", {"capability_failure"}, "worker_capability_drop_failed", False),
        ("protected_oom_score", "exact_profile", {"protected_oom"}, "worker_protected_from_oom", False),
        ("exact_missing_profile_readback", "exact_profile", {"missing_profile_accepted"}, "exact_profile_missing_worker_readback", False),
        ("exact_bad_terminal", "exact_profile", {"bad_exact_terminal"}, "exact_profile_terminal_mismatch", False),
        ("group_zero_missing_typed_event", "group_zero_refused", {"missing_typed_refusal"}, "group_zero_not_typed_refusal", False),
        ("group_zero_bad_terminal", "group_zero_refused", {"bad_group_zero_terminal"}, "group_zero_not_typed_refusal", False),
        ("group_zero_stress_guard", "group_zero_refused", {"group_zero_allocates"}, "group_zero_started_stress", False),
        ("small_auxiliary_readiness", "small_group_oom", {"missing_aux_ready"}, "small_oom_auxiliary_not_ready", False),
        ("small_before_marker", "small_group_oom", {"missing_before_marker"}, "small_oom_missing_before_allocation_marker", False),
        ("small_non_sigkill", "small_group_oom", {"non_sigkill"}, "small_oom_terminal_not_sigkill", False),
        ("small_manual_kill", "small_group_oom", {"manual_kill"}, "manual_or_watchdog_kill_not_oom", False),
        ("small_missing_counters", "small_group_oom", {"missing_events"}, "missing_cgroup_metric", False),
        ("small_counter_threshold", "small_group_oom", {"low_oom_counters"}, "small_oom_counter_threshold_not_met", False),
        ("small_subtree_populated", "small_group_oom", {"worker_still_populated"}, "worker_subtree_still_populated", False),
        ("small_supervisor_survival", "small_group_oom", {"supervisor_dead"}, "supervisor_did_not_survive", False),
        ("worker_watchdog", "small_group_oom", {"watchdog"}, "worker_watchdog", False),
        ("partial_worker_cleanup", "exact_profile", {"worker_cleanup_failure"}, None, True),
        ("partial_supervisor_cleanup", "exact_profile", {"supervisor_cleanup_failure"}, None, True),
        ("worker_bootstrap_failure", "exact_profile", {"bootstrap_failure"}, "worker_privilege_drop_failed", False),
        ("wrong_task_id", "exact_profile", {"wrong_task"}, "wrong_task_id", False),
        ("fixed_parameter_change", "exact_profile", {"profile_parameter_changed"}, "fixed_profile_parameters_changed", False),
    ]
    assert len(vectors) == FINAL_SUITE_CASES
    results = [run_case(*vector) for vector in vectors]
    exact = next(result for result in results if result["id"] == "exact_profile_pass")
    required_order = [
        "worker_profile_written_and_read_before_fork",
        "worker_forked_behind_barrier",
        "worker_migrated_before_release",
        "worker_released_after_profile_and_migration",
    ]
    ordering_guard = all(exact["ordering"].index(step) == exact["ordering"].index(step) for step in required_order) and [
        exact["ordering"].index(step) for step in required_order
    ] == sorted(exact["ordering"].index(step) for step in required_order)
    for result in results:
        result["passed"] = bool(result["passed"] and result["transcript_persisted"])
    return {
        "schema": "crypto.autoresearch.group_oom_supervisor_fixed_mock_suite.v1",
        "task_id": TASK_ID,
        "source_only": True,
        "fixed_case_execution_count": len(results),
        "ordering_guard": ordering_guard,
        "results": results,
        "passed": all(result["passed"] for result in results) and ordering_guard,
    }


def run_final_suite(receipt_path: Path) -> int:
    started_at = utc_now()
    monotonic_started = time.monotonic()
    child_before = resource.getrusage(resource.RUSAGE_CHILDREN)
    command = [sys.executable, "-B", str(HERE / "tests.py"), "--suite-json"]
    completed = subprocess.run(command, cwd=str(HERE), capture_output=True, text=True, check=False)
    child_after = resource.getrusage(resource.RUSAGE_CHILDREN)
    ended_at = utc_now()
    try:
        suite = json.loads(completed.stdout)
    except json.JSONDecodeError:
        suite = {"passed": False, "parse_error": True}
    receipt = {
        "schema": "crypto.autoresearch.group_oom_supervisor_source_check_receipt.v1",
        "task_id": TASK_ID,
        "source_only": True,
        "scientific_runs": 0,
        "operational_containers_started": 0,
        "reservation": {
            "maximum_fixed_static_or_mock_case_executions": MAX_FIXED_CASES,
            "prior_executed_case_count": 0,
            "complete_final_suite_reserved_before_execution": FINAL_SUITE_CASES,
            "executed_final_suite_case_count": suite.get("fixed_case_execution_count"),
            "remaining_correction_capacity": MAX_FIXED_CASES - FINAL_SUITE_CASES,
            "reruns": 0,
        },
        "command": {
            "argv": command,
            "started_at_UTC": started_at,
            "ended_at_UTC": ended_at,
            "session_id": None,
            "yielded_session_ids": [],
            "terminal_polled": True,
            "exit_code": completed.returncode,
            "stdout_redirected_to_retained_receipt": completed.stdout,
            "stderr_redirected_to_retained_receipt": completed.stderr,
        },
        "actual_metrics": {
            "wall_seconds": time.monotonic() - monotonic_started,
            "child_user_cpu_seconds": child_after.ru_utime - child_before.ru_utime,
            "child_system_cpu_seconds": child_after.ru_stime - child_before.ru_stime,
            "host_process_peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * (1 if sys.platform == "darwin" else 1024),
            "host_process_peak_rss_basis": "ru_maxrss bytes on darwin; kibibytes converted to bytes elsewhere",
        },
        "suite": suite,
        "limitations": [
            "All observations are fixed synthetic filesystem/process/container data; no live Docker, cgroup, privilege, migration, or pressure action occurred.",
            "The planned writable /host-cgroup bind and cgroup controller delegation are represented as prospective checks only; their local availability remains untested.",
            "A passing mock suite is source conformance evidence only. It is not a live operational control pass, OOM observation, scientific run, or research claim.",
        ],
    }
    with receipt_path.open("x", encoding="utf-8") as handle:
        json.dump(receipt, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(json.dumps({"receipt": str(receipt_path), "passed": bool(suite.get("passed"))}, sort_keys=True))
    return 0 if completed.returncode == 0 and suite.get("passed") else 2


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite-json", action="store_true")
    parser.add_argument("--run-final", action="store_true")
    parser.add_argument("--receipt", type=Path, default=RECEIPT)
    args = parser.parse_args()
    if args.suite_json == args.run_final:
        parser.error("choose exactly one of --suite-json or --run-final")
    if args.suite_json:
        suite = full_suite()
        print(json.dumps(suite, sort_keys=True))
        return 0 if suite["passed"] else 2
    return run_final_suite(args.receipt)


if __name__ == "__main__":
    raise SystemExit(main())
