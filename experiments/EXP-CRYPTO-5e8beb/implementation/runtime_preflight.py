"""Source-only runtime preflight for EXP-CRYPTO-5e8beb.

Per the frozen specification's `runtime.admission` field: "Preflight source
only during implementation; actual backend/guard/failure-capture/transport
checks and genuine launch bindings precede scientific fixture work." This
module therefore performs **no actual resource, backend or environment
probing** -- it does not call `platform.system()`, `resource.getrlimit()`,
`shutil.disk_usage()`, the Docker CLI, or anything else that inspects the
live host. It only checks that the *declared source constants* in
`driver.py` (and, transitively, this module) agree with the frozen
specification's checkpoint/memory/worker values, and it reports explicitly
that real backend/resource verification has not happened here.

Fail-closed discipline: every function below defaults to reporting
`ready_for_scientific_launch = False`. There is no code path in this module
that can report readiness for an actual run; that determination belongs to a
later, separately authorized preflight step that does perform real probing
and is exercised outside this implementation task (`maximum_runs: 0`).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

import driver

EXPECTED_CHECKPOINT_SECONDS = 3600
EXPECTED_NATIVE_HARD_AS_BYTES = 8589934592
EXPECTED_NATIVE_HARD_CPU_SECONDS = 3600
EXPECTED_DOCKER_MEMORY_BYTES = 8589934592
EXPECTED_DOCKER_CPUS = 1
EXPECTED_DOCKER_PIDS_LIMIT = 64
EXPECTED_MAX_WORKERS = 1


@dataclass(frozen=True)
class PreflightReport:
    constants_consistent: bool
    problems: List[str]
    ready_for_scientific_launch: bool
    reason: str

    def to_json(self) -> dict:
        return {
            "constants_consistent": self.constants_consistent,
            "problems": list(self.problems),
            "ready_for_scientific_launch": self.ready_for_scientific_launch,
            "reason": self.reason,
        }


def check_declared_constants() -> PreflightReport:
    """Compare `driver.py`'s declared checkpoint/memory/worker constants
    against the frozen specification's values (`runtime.checkpoint_seconds`,
    `runtime.native.hard_AS_bytes`, `runtime.native.hard_CPU_limit_seconds`,
    `runtime.docker.memory_bytes`, `runtime.docker.cpus`,
    `runtime.docker.pids_limit`, `budget.maximum_workers`). This is a static
    source comparison, not a measurement of the live machine.
    """
    problems: List[str] = []

    checks = (
        ("driver.CHECKPOINT_SECONDS", driver.CHECKPOINT_SECONDS, EXPECTED_CHECKPOINT_SECONDS),
        ("driver.NATIVE_HARD_AS_BYTES", driver.NATIVE_HARD_AS_BYTES, EXPECTED_NATIVE_HARD_AS_BYTES),
        ("driver.NATIVE_HARD_CPU_SECONDS", driver.NATIVE_HARD_CPU_SECONDS, EXPECTED_NATIVE_HARD_CPU_SECONDS),
        ("driver.DOCKER_MEMORY_BYTES", driver.DOCKER_MEMORY_BYTES, EXPECTED_DOCKER_MEMORY_BYTES),
        ("driver.DOCKER_CPUS", driver.DOCKER_CPUS, EXPECTED_DOCKER_CPUS),
        ("driver.DOCKER_PIDS_LIMIT", driver.DOCKER_PIDS_LIMIT, EXPECTED_DOCKER_PIDS_LIMIT),
        ("driver.MAX_WORKERS", driver.MAX_WORKERS, EXPECTED_MAX_WORKERS),
    )
    for name, actual, expected in checks:
        if actual != expected:
            problems.append(f"{name} = {actual!r} does not match frozen spec value {expected!r}")

    return PreflightReport(
        constants_consistent=not problems,
        problems=problems,
        ready_for_scientific_launch=False,
        reason=(
            "Source-only check: declared checkpoint/memory/worker constants "
            "were compared against the frozen specification, but no actual "
            "backend, resource limit, failure-capture or transport probing "
            "was performed. A genuine preflight against the live host/Docker "
            "backend is required before any scientific launch and is out of "
            "this implementation task's scope (maximum_runs: 0)."
        ),
    )


def check_protection_establishable() -> PreflightReport:
    """Fail closed on the question 'can a hard protection mechanism later be
    established here?' -- this module cannot answer that without probing the
    live host, which it is not authorized to do. It always reports not-ready,
    with the precise reason, rather than assuming success.
    """
    return PreflightReport(
        constants_consistent=True,
        problems=[],
        ready_for_scientific_launch=False,
        reason=(
            "Whether a hard RLIMIT_AS/RLIMIT_CPU boundary (native, Linux) or "
            "a verified cgroup memory/CPU/pids boundary (Docker, sha256-pinned "
            "image) can actually be established on the executing host is "
            "unknown until a real preflight runs `tools/audit_process.py` or "
            "equivalent and reads back the limits. This module intentionally "
            "performs no such probe and reports not-ready rather than "
            "silently assuming the protection will succeed."
        ),
    )


def full_preflight_report() -> dict:
    """Aggregate report for implementation-report.yaml / README.md cross-check."""
    constants = check_declared_constants()
    protection = check_protection_establishable()
    return {
        "declared_constants": constants.to_json(),
        "protection_establishable": protection.to_json(),
        "ready_for_scientific_launch": False,
        "note": (
            "Both sub-checks are source-only. Neither result may be read as "
            "evidence that a scientific run would succeed on any particular "
            "host or backend."
        ),
    }
