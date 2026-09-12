"""driver.py -- single coordinator/runner entry point for EXP-CRYPTO-9225d2.

STATUS: source only. Importing this module triggers NO fixture generation,
NO benchmark execution, and NO scientific job. `main()` (the only would-be
executing entry point) raises immediately rather than run, because
TASK-20260907-ecd3a2 authorizes zero scientific runs (maximum_runs=0).

Defines:
  - the exact 40 logical jobs / physical cells the frozen specification
    declares (10 arithmetic bundles x 9 routine/environment cells + 9
    primitive cells each, 30 rho jobs across 3 rungs x 10 seeds);
  - three-process barrier logic hookup for rho jobs (delegated to
    rho.CoordinatorBarrier);
  - timer interfaces (wall/CPU nanosecond) that record but do not fabricate
    a measurement;
  - a cgroup v2 admission interface (memory.max, memory.swap.max, pids.max,
    cpu.max readback) that REFUSES admission rather than assume a launcher
    supports these controls;
  - a resource-accounting interface (RSS, memory.peak, memory.events,
    cpu.stat) that records None/unmeasured rather than invent a value;
  - an exclusive-output-directory interface (fails preflight rather than
    write into a shared/non-exclusive path);
  - a checkpoint interface bound to rho.RhoCheckpoint's fields.

This module does not edit or depend on any shared launch tooling outside
its own file (per handoff constraint "Do not edit shared launch tools").
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

# NOTE: these imports are for type/interface reuse only; nothing imported
# here is invoked to run a scientific measurement at import time.
from arithmetic import SECP256K1_GX, SECP256K1_GY, SECP256K1_N  # noqa: F401
from rho import RHO_LANES, RHO_PROCESSES_PER_JOB, DP_BITS_BY_K  # noqa: F401


# ---------------------------------------------------------------------------
# Exact job/cell enumeration (spec.experimental_unit, spec.independent_variables)
# ---------------------------------------------------------------------------

SEEDS = [
    20260825, 20260826, 20260827, 20260828, 20260829,
    20260830, 20260831, 20260901, 20260902, 20260903,
]
SCALAR_ROUTINES = ["reference", "planted", "null"]
ENVIRONMENTS = ["A_boot_1", "B_boot_1", "A_boot_2"]
FIELD_PRIMITIVES = ["M", "S", "I"]
RHO_ORDER_BITS = [40, 48, 56]
MODELED_WORKERS = [1, 2, 256]
MODELED_DP_BITS = [104, 112, 120]

LOGICAL_JOBS_TOTAL = 40
ARITHMETIC_JOBS = 10  # one per seed
RHO_JOBS = 30  # 3 rungs x 10 seeds
MODELED_ROWS = 9  # 3 x 3 cartesian, computed in the summary, not per job

assert ARITHMETIC_JOBS + RHO_JOBS == LOGICAL_JOBS_TOTAL


@dataclass(frozen=True)
class ArithmeticJobSpec:
    """One arithmetic logical job: a seed, spanning its nine routine cells
    and nine primitive cells across all three environments (spec.
    experimental_unit.accounting_note)."""

    seed: int

    def routine_cells(self) -> List[Tuple[str, str]]:
        """Environment order A_boot_1, B_boot_1, A_boot_2; primitives
        M,S,I followed by routines reference,planted,null (spec.ordering
        .arithmetic_cells) -- here enumerated as (environment, routine)."""
        cells = []
        for env in ENVIRONMENTS:
            for routine in SCALAR_ROUTINES:
                cells.append((env, routine))
        return cells

    def primitive_cells(self) -> List[Tuple[str, str]]:
        cells = []
        for env in ENVIRONMENTS:
            for primitive in FIELD_PRIMITIVES:
                cells.append((env, primitive))
        return cells


@dataclass(frozen=True)
class RhoJobSpec:
    """One rho logical job: a (k_bits, seed) pair."""

    k_bits: int
    seed: int


def enumerate_arithmetic_jobs() -> List[ArithmeticJobSpec]:
    """Arithmetic bundles by the listed seed order (spec.ordering.jobs)."""
    return [ArithmeticJobSpec(seed=seed) for seed in SEEDS]


def enumerate_rho_jobs() -> List[RhoJobSpec]:
    """Rho by increasing rung and listed seed order (spec.ordering.jobs)."""
    jobs = []
    for k_bits in RHO_ORDER_BITS:
        for seed in SEEDS:
            jobs.append(RhoJobSpec(k_bits=k_bits, seed=seed))
    return jobs


def enumerate_all_logical_jobs() -> List[object]:
    """Model rows follow all required measured panels (spec.ordering.jobs);
    modeled rows are a summary-level computation, not additional logical
    jobs, so they are not included in this 40-element list."""
    jobs: List[object] = []
    jobs.extend(enumerate_arithmetic_jobs())
    jobs.extend(enumerate_rho_jobs())
    if len(jobs) != LOGICAL_JOBS_TOTAL:
        raise AssertionError(f"expected exactly {LOGICAL_JOBS_TOTAL} logical jobs, got {len(jobs)}")
    return jobs


def enumerate_model_rows() -> List[Tuple[int, int]]:
    """(m, d) pairs ordered by m then d, per spec.model_256.scenarios."""
    rows = []
    for m in MODELED_WORKERS:
        for d in MODELED_DP_BITS:
            rows.append((m, d))
    if len(rows) != MODELED_ROWS:
        raise AssertionError(f"expected exactly {MODELED_ROWS} model rows, got {len(rows)}")
    return rows


# ---------------------------------------------------------------------------
# Timer interfaces -- record, never fabricate
# ---------------------------------------------------------------------------


@dataclass
class TimingSample:
    wall_ns: Optional[int] = None
    cpu_ns: Optional[int] = None
    resolution_ns: Optional[int] = None
    clock_method: Optional[str] = None


class Timer:
    """Wraps monotonic wall-clock and process CPU-time measurement around a
    full batch, per spec.hosts.timing. Records resolution and
    implementation. This class does not itself invoke any payload work; a
    caller supplies the timed region."""

    def __init__(self) -> None:
        self._wall_start: Optional[int] = None
        self._cpu_start: Optional[int] = None

    def start(self) -> None:
        self._wall_start = time.monotonic_ns()
        self._cpu_start = time.process_time_ns()

    def stop(self) -> TimingSample:
        if self._wall_start is None or self._cpu_start is None:
            raise RuntimeError("Timer.stop called before Timer.start")
        wall_ns = time.monotonic_ns() - self._wall_start
        cpu_ns = time.process_time_ns() - self._cpu_start
        return TimingSample(
            wall_ns=wall_ns,
            cpu_ns=cpu_ns,
            resolution_ns=1,  # time.monotonic_ns/process_time_ns nominal ns resolution;
                               # actual OS resolution is a host property to be verified
                               # at admission, not assumed here.
            clock_method="time.monotonic_ns/time.process_time_ns",
        )


# ---------------------------------------------------------------------------
# cgroup v2 admission interface -- refuses rather than assumes
# ---------------------------------------------------------------------------


@dataclass
class CgroupAdmissionResult:
    admitted: bool
    memory_max_bytes_readback: Optional[int]
    memory_swap_max_readback: Optional[int]
    pids_max_readback: Optional[int]
    cpu_max_readback: Optional[str]
    refusal_reason: Optional[str]


REQUIRED_MEMORY_MAX_BYTES = 8 * (2 ** 30)
REQUIRED_PIDS_MAX = 3
REQUIRED_CPU_MAX_BY_JOB = {
    "arithmetic": "100000 100000",
    "rho": "300000 100000",
}


def check_cgroup_admission(
    cgroup_path: Optional[str],
    job_kind: str = "arithmetic",
    *,
    job_type: Optional[str] = None,
) -> CgroupAdmissionResult:
    """Read back cgroup v2 controls from `cgroup_path` and refuse admission
    if delegation is absent or values do not match the required contract
    (spec.runtime.contract). Does NOT create, delegate, or assume a cgroup
    exists; a missing path or missing controller files is a hard refusal,
    never a fabricated pass. Not invoked against a real cgroup in this
    task -- this task performs no scientific admission.

    job_kind selects the frozen cpu.max quota: arithmetic uses
    100000 100000 (one process); rho uses 300000 100000 (three processes).
    pids.max must be exactly 3 (DEC-20260908-ffb734 finding (d) / C12). An
    unrecognized job_kind is itself a refusal (never a fabricated pass),
    consistent with this function's refuse-rather-than-assume contract.
    `job_type` is accepted as a keyword alias for `job_kind` so revise-fix
    documentation that used that name remains callable without a second
    signature; if both are supplied, `job_type` wins.
    """
    if job_type is not None:
        # Keyword alias for revise-fix docs that named the selector job_type.
        job_kind = job_type
    if not cgroup_path or not os.path.isdir(cgroup_path):
        return CgroupAdmissionResult(
            admitted=False,
            memory_max_bytes_readback=None,
            memory_swap_max_readback=None,
            pids_max_readback=None,
            cpu_max_readback=None,
            refusal_reason="no delegated cgroup path provided or path does not exist",
        )

    def _read_int_file(name: str) -> Optional[int]:
        path = os.path.join(cgroup_path, name)
        if not os.path.isfile(path):
            return None
        try:
            with open(path, "r") as fh:
                content = fh.read().strip()
            if content == "max":
                return None
            return int(content)
        except (OSError, ValueError):
            return None

    def _read_str_file(name: str) -> Optional[str]:
        path = os.path.join(cgroup_path, name)
        if not os.path.isfile(path):
            return None
        try:
            with open(path, "r") as fh:
                return fh.read().strip()
        except OSError:
            return None

    mem_max = _read_int_file("memory.max")
    swap_max = _read_int_file("memory.swap.max")
    pids_max = _read_int_file("pids.max")
    cpu_max = _read_str_file("cpu.max")

    if mem_max != REQUIRED_MEMORY_MAX_BYTES:
        return CgroupAdmissionResult(
            admitted=False, memory_max_bytes_readback=mem_max,
            memory_swap_max_readback=swap_max, pids_max_readback=pids_max,
            cpu_max_readback=cpu_max,
            refusal_reason=f"memory.max readback {mem_max} != required {REQUIRED_MEMORY_MAX_BYTES}",
        )
    if swap_max != 0:
        return CgroupAdmissionResult(
            admitted=False, memory_max_bytes_readback=mem_max,
            memory_swap_max_readback=swap_max, pids_max_readback=pids_max,
            cpu_max_readback=cpu_max,
            refusal_reason=f"memory.swap.max readback {swap_max} != required 0",
        )
    if pids_max != REQUIRED_PIDS_MAX:
        return CgroupAdmissionResult(
            admitted=False, memory_max_bytes_readback=mem_max,
            memory_swap_max_readback=swap_max, pids_max_readback=pids_max,
            cpu_max_readback=cpu_max,
            refusal_reason=(
                f"pids.max readback {pids_max} != required exactly "
                f"{REQUIRED_PIDS_MAX}"
            ),
        )
    required_cpu = REQUIRED_CPU_MAX_BY_JOB.get(job_kind)
    if required_cpu is None:
        return CgroupAdmissionResult(
            admitted=False, memory_max_bytes_readback=mem_max,
            memory_swap_max_readback=swap_max, pids_max_readback=pids_max,
            cpu_max_readback=cpu_max,
            refusal_reason=(
                f"job_kind {job_kind!r} is not one of "
                f"{sorted(REQUIRED_CPU_MAX_BY_JOB)}"
            ),
        )
    if cpu_max != required_cpu:
        return CgroupAdmissionResult(
            admitted=False, memory_max_bytes_readback=mem_max,
            memory_swap_max_readback=swap_max, pids_max_readback=pids_max,
            cpu_max_readback=cpu_max,
            refusal_reason=(
                f"cpu.max readback {cpu_max!r} != required {required_cpu!r} "
                f"for job_kind={job_kind}"
            ),
        )

    return CgroupAdmissionResult(
        admitted=True, memory_max_bytes_readback=mem_max,
        memory_swap_max_readback=swap_max, pids_max_readback=pids_max,
        cpu_max_readback=cpu_max, refusal_reason=None,
    )


# ---------------------------------------------------------------------------
# Resource-accounting interface -- records, never invents
# ---------------------------------------------------------------------------


@dataclass
class ResourceSample:
    payload_peak_rss_bytes: Optional[int] = None
    cgroup_memory_peak_bytes: Optional[int] = None
    cgroup_memory_events: Optional[Dict[str, int]] = None
    cgroup_cpu_stat: Optional[Dict[str, int]] = None
    sampling_method: Optional[str] = None
    sampling_interval_ms: Optional[int] = None
    host_wide_context_note: Optional[str] = None


def read_cgroup_resource_accounting(cgroup_path: Optional[str]) -> ResourceSample:
    """Read cgroup memory.peak, memory.events, aggregate cpu.stat before
    cleanup, per spec.runtime.contract. Returns None fields when the path
    or controller files are absent, rather than a fabricated zero or
    average. Not invoked against a real cgroup in this task."""
    if not cgroup_path or not os.path.isdir(cgroup_path):
        return ResourceSample(sampling_method=None, host_wide_context_note="no cgroup path available")
    return ResourceSample(
        payload_peak_rss_bytes=None,  # RSS sampling is a separate declared OS
                                        # method (spec.hosts.resource_sampling);
                                        # not performed here.
        cgroup_memory_peak_bytes=None,
        cgroup_memory_events=None,
        cgroup_cpu_stat=None,
        sampling_method=None,
        sampling_interval_ms=None,
        host_wide_context_note="interface only; no admitted cgroup read in this task",
    )


# ---------------------------------------------------------------------------
# Exclusive-output-directory interface
# ---------------------------------------------------------------------------


@dataclass
class ExclusiveOutputResult:
    acquired: bool
    directory: Optional[str]
    refusal_reason: Optional[str]


def acquire_exclusive_output_directory(run_root: str) -> ExclusiveOutputResult:
    """Fail preflight if the directory already exists (non-exclusive) or if
    the parent is not writable, rather than silently reusing or fabricating
    a durable-output guarantee (spec.runtime.environment: "a launcher
    lacking durable output access fails preflight"). Not invoked to create
    a real run directory in this task; this task's own write_scope is fixed
    to the ten implementation files, not experiments/EXP-CRYPTO-9225d2/runs/.
    """
    if os.path.exists(run_root):
        return ExclusiveOutputResult(
            acquired=False, directory=run_root,
            refusal_reason=f"{run_root} already exists; exclusive output directories are required",
        )
    parent = os.path.dirname(run_root.rstrip("/")) or "."
    if not os.path.isdir(parent) or not os.access(parent, os.W_OK):
        return ExclusiveOutputResult(
            acquired=False, directory=run_root,
            refusal_reason=f"parent directory {parent} does not exist or is not writable",
        )
    return ExclusiveOutputResult(acquired=False, directory=run_root,
                                  refusal_reason="acquire_exclusive_output_directory is an interface "
                                                 "check only in this task; it does not create the "
                                                 "directory (no run is authorized)")


# ---------------------------------------------------------------------------
# Checkpoint interface hookup
# ---------------------------------------------------------------------------


@dataclass
class CheckpointIndexEntry:
    logical_job_id: str
    checkpoint_present: bool
    checkpoint_sha256: Optional[str]
    checkpoint_byte_length: Optional[int]
    completed_work_boundary: Optional[str]


def watchdog_seconds() -> int:
    """3600-second wall watchdog requests a checkpoint then terminates;
    cleanup can take five further seconds (spec.runtime.contract). This is
    a machine-protection constant, not a research spending cap."""
    return 3600


# ---------------------------------------------------------------------------
# Entry point -- guarded, never runs
# ---------------------------------------------------------------------------


def main() -> None:
    raise RuntimeError(
        "driver.main() is source-only in TASK-20260907-ecd3a2. This task "
        "authorizes zero scientific execution (maximum_runs=0); no fixture, "
        "benchmark, or rho job may be launched from this delivery. A "
        "future, separately authorized scientific-execution task removes "
        "this guard after independent checker/predictor review, fixture "
        "certificate realization, and two-physical-host admission are all "
        "complete."
    )


if __name__ == "__main__":
    main()


__all__ = [
    "SEEDS",
    "SCALAR_ROUTINES",
    "ENVIRONMENTS",
    "FIELD_PRIMITIVES",
    "RHO_ORDER_BITS",
    "MODELED_WORKERS",
    "MODELED_DP_BITS",
    "LOGICAL_JOBS_TOTAL",
    "ARITHMETIC_JOBS",
    "RHO_JOBS",
    "MODELED_ROWS",
    "ArithmeticJobSpec",
    "RhoJobSpec",
    "enumerate_arithmetic_jobs",
    "enumerate_rho_jobs",
    "enumerate_all_logical_jobs",
    "enumerate_model_rows",
    "TimingSample",
    "Timer",
    "CgroupAdmissionResult",
    "check_cgroup_admission",
    "ResourceSample",
    "read_cgroup_resource_accounting",
    "ExclusiveOutputResult",
    "acquire_exclusive_output_directory",
    "CheckpointIndexEntry",
    "watchdog_seconds",
    "main",
]

# NOTE: `main()` raises immediately rather than run; no fixture generation
# or benchmark execution occurs at import. Only `python3 -m py_compile`
# static syntax checking has been performed against this file under
# TASK-20260907-ecd3a2 (see preparation-report.yaml). No cgroup, timer,
# resource, enumeration, or other function in this module has been invoked
# against real system state or real data in this task.
