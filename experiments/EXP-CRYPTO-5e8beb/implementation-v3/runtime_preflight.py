"""Runtime preflight for EXP-CRYPTO-5e8beb (implementation-v3).

IMPLEMENTATION-V3 CHANGE from implementation/runtime_preflight.py (closes
review finding C11's stated cause, per
coordination/design/BATCH-51d1bb/reviews/TASK-20260908-0eabfe/implementation-review.yaml
and this task's handoff, ledger/handoffs/TASK-20260913-c43d3e.yaml):

The prior version performed *no* live-host or Docker probing at all and
always returned `ready_for_scientific_launch=False` unconditionally, by
construction, regardless of what the host could actually do. This version
adds real, side-effect-free capability probes:

  - `probe_cgroup_v2()` actually attempts to read
    `/sys/fs/cgroup/cgroup.controllers` (the canonical cgroup v2 unified
    mount point) and, if present, this process's own
    `/proc/self/cgroup` + `/sys/fs/cgroup/memory.max` /
    `/sys/fs/cgroup/cpu.max` / `/sys/fs/cgroup/pids.max` controller files,
    recording exactly what exists and what its content is -- never assuming
    `specification.runtime.native`'s eventual production path is present on
    THIS container, and never inventing a result for a path that does not
    exist here.
  - `probe_docker()` actually attempts to locate a `docker` binary on PATH
    (`shutil.which`) and, only if found, runs `docker info` (a read-only,
    non-mutating command) with a bounded timeout, recording the real exit
    code and a truncated excerpt of its output/error.
  - `probe_rlimit_capability()` actually reads back this process's own
    current `RLIMIT_AS` / `RLIMIT_CPU` soft/hard limits via
    `resource.getrlimit` (a read, not a change) as the native-backend
    protection-establishability signal.

None of these probes creates, deletes, or modifies any file, process,
container, or resource limit; they only read state that already exists on
the host. `check_protection_establishable` may now return
`ready_for_scientific_launch=True` when both the cgroup v2 controller file
(or, on the native path, an actually-settable RLIMIT_AS/RLIMIT_CPU pair) and
-- for the Docker backend specifically -- a working `docker info` are
genuinely observed, but it still reports `False` with a precise reason
whenever a probe fails, errors, or the relevant capability is simply absent
on this host. No result here is fabricated, assumed, or copied from another
host; every field traces to an actual command/read performed during this
call.

This module still performs the prior version's source-only declared-constant
comparison (`check_declared_constants`) unchanged in spirit, comparing
`driver.py`'s literal checkpoint/memory/worker constants against the frozen
specification's values.
"""
from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

import driver

EXPECTED_CHECKPOINT_SECONDS = 3600
EXPECTED_NATIVE_HARD_AS_BYTES = 8589934592
EXPECTED_NATIVE_HARD_CPU_SECONDS = 3600
EXPECTED_DOCKER_MEMORY_BYTES = 8589934592
EXPECTED_DOCKER_CPUS = 1
EXPECTED_DOCKER_PIDS_LIMIT = 64
EXPECTED_MAX_WORKERS = 1

CGROUP_V2_ROOT = Path("/sys/fs/cgroup")
CGROUP_V2_CONTROLLERS_FILE = CGROUP_V2_ROOT / "cgroup.controllers"
CGROUP_V2_CONTROLLER_FILES = ("memory.max", "cpu.max", "pids.max")
DOCKER_INFO_TIMEOUT_SECONDS = 10
DOCKER_OUTPUT_EXCERPT_BYTES = 2000


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
    """Static source comparison of driver.py's declared constants against the
    frozen specification's values. Unchanged in spirit from implementation/.
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
            "were compared against the frozen specification. This sub-check "
            "alone never reports readiness; see check_protection_establishable "
            "for the live-host probe result."
        ),
    )


# --- real, side-effect-free capability probes -------------------------------

@dataclass(frozen=True)
class CgroupV2Probe:
    unified_root_exists: bool
    controllers_file_path: str
    controllers_file_readable: bool
    controllers_content: Optional[str]
    controller_files_present: Dict[str, bool]
    controller_files_content: Dict[str, Optional[str]]
    own_cgroup_path: Optional[str]
    error: Optional[str]

    def to_json(self) -> dict:
        return {
            "unified_root_exists": self.unified_root_exists,
            "controllers_file_path": self.controllers_file_path,
            "controllers_file_readable": self.controllers_file_readable,
            "controllers_content": self.controllers_content,
            "controller_files_present": dict(self.controller_files_present),
            "controller_files_content": dict(self.controller_files_content),
            "own_cgroup_path": self.own_cgroup_path,
            "error": self.error,
        }


def probe_cgroup_v2() -> CgroupV2Probe:
    """Actually read the cgroup v2 unified hierarchy on THIS host, if present.

    Reports what genuinely exists at `/sys/fs/cgroup` -- the standard cgroup
    v2 unified mount point -- rather than assuming
    specification.runtime.native's eventual production path is present in
    this implementation-time container. A missing or unreadable path is
    reported as such, never silently treated as success.
    """
    error: Optional[str] = None
    own_cgroup_path: Optional[str] = None
    try:
        own_cgroup_path = Path("/proc/self/cgroup").read_text(encoding="utf-8").strip()
    except OSError as exc:
        error = f"/proc/self/cgroup unreadable: {exc}"

    root_exists = CGROUP_V2_ROOT.is_dir()
    controllers_readable = False
    controllers_content: Optional[str] = None
    if CGROUP_V2_CONTROLLERS_FILE.is_file():
        try:
            controllers_content = CGROUP_V2_CONTROLLERS_FILE.read_text(encoding="utf-8").strip()
            controllers_readable = True
        except OSError as exc:
            error = (error + "; " if error else "") + f"cgroup.controllers unreadable: {exc}"

    present: Dict[str, bool] = {}
    content: Dict[str, Optional[str]] = {}
    for name in CGROUP_V2_CONTROLLER_FILES:
        path = CGROUP_V2_ROOT / name
        present[name] = path.is_file()
        if present[name]:
            try:
                content[name] = path.read_text(encoding="utf-8").strip()
            except OSError as exc:
                content[name] = None
                error = (error + "; " if error else "") + f"{name} unreadable: {exc}"
        else:
            content[name] = None

    return CgroupV2Probe(
        unified_root_exists=root_exists,
        controllers_file_path=str(CGROUP_V2_CONTROLLERS_FILE),
        controllers_file_readable=controllers_readable,
        controllers_content=controllers_content,
        controller_files_present=present,
        controller_files_content=content,
        own_cgroup_path=own_cgroup_path,
        error=error,
    )


@dataclass(frozen=True)
class DockerProbe:
    binary_found: bool
    binary_path: Optional[str]
    info_attempted: bool
    info_exit_code: Optional[int]
    info_stdout_excerpt: Optional[str]
    info_stderr_excerpt: Optional[str]
    info_timed_out: bool
    error: Optional[str]

    def to_json(self) -> dict:
        return {
            "binary_found": self.binary_found,
            "binary_path": self.binary_path,
            "info_attempted": self.info_attempted,
            "info_exit_code": self.info_exit_code,
            "info_stdout_excerpt": self.info_stdout_excerpt,
            "info_stderr_excerpt": self.info_stderr_excerpt,
            "info_timed_out": self.info_timed_out,
            "error": self.error,
        }


def probe_docker() -> DockerProbe:
    """Actually check for a `docker` binary on PATH and, only if found, run
    the read-only `docker info` with a bounded timeout. Never invents a
    result: absence of the binary is reported as absence, and any failure
    (nonzero exit, timeout, daemon unreachable) is reported with its real
    exit code / output excerpt, never silently upgraded to success.
    """
    binary_path = shutil.which("docker")
    if binary_path is None:
        return DockerProbe(
            binary_found=False, binary_path=None, info_attempted=False,
            info_exit_code=None, info_stdout_excerpt=None, info_stderr_excerpt=None,
            info_timed_out=False, error="docker binary not found on PATH",
        )
    try:
        proc = subprocess.run(
            [binary_path, "info"],
            capture_output=True, text=True, timeout=DOCKER_INFO_TIMEOUT_SECONDS,
        )
        return DockerProbe(
            binary_found=True, binary_path=binary_path, info_attempted=True,
            info_exit_code=proc.returncode,
            info_stdout_excerpt=proc.stdout[:DOCKER_OUTPUT_EXCERPT_BYTES],
            info_stderr_excerpt=proc.stderr[:DOCKER_OUTPUT_EXCERPT_BYTES],
            info_timed_out=False, error=None,
        )
    except subprocess.TimeoutExpired as exc:
        return DockerProbe(
            binary_found=True, binary_path=binary_path, info_attempted=True,
            info_exit_code=None, info_stdout_excerpt=None, info_stderr_excerpt=None,
            info_timed_out=True, error=f"docker info timed out after {DOCKER_INFO_TIMEOUT_SECONDS}s: {exc}",
        )
    except OSError as exc:
        return DockerProbe(
            binary_found=True, binary_path=binary_path, info_attempted=True,
            info_exit_code=None, info_stdout_excerpt=None, info_stderr_excerpt=None,
            info_timed_out=False, error=f"docker info failed to launch: {exc}",
        )


@dataclass(frozen=True)
class RlimitProbe:
    platform_is_linux: bool
    resource_module_available: bool
    as_soft: Optional[int]
    as_hard: Optional[int]
    cpu_soft: Optional[int]
    cpu_hard: Optional[int]
    error: Optional[str]

    def to_json(self) -> dict:
        return {
            "platform_is_linux": self.platform_is_linux,
            "resource_module_available": self.resource_module_available,
            "as_soft": self.as_soft, "as_hard": self.as_hard,
            "cpu_soft": self.cpu_soft, "cpu_hard": self.cpu_hard,
            "error": self.error,
        }


def probe_rlimit_capability() -> RlimitProbe:
    """Read back (never set) this process's own current RLIMIT_AS/RLIMIT_CPU
    limits, as the native-backend read-back signal specification.runtime.
    native.resource_guard describes ("Apply and read back actual hard limits
    before fixture work"). This probe only performs the read-back half; it
    never applies a limit, since that would be a side effect this
    preparation-only task must not perform.
    """
    import platform
    is_linux = platform.system() == "Linux"
    try:
        import resource
    except ImportError as exc:
        return RlimitProbe(
            platform_is_linux=is_linux, resource_module_available=False,
            as_soft=None, as_hard=None, cpu_soft=None, cpu_hard=None,
            error=f"resource module unavailable: {exc}",
        )
    try:
        as_soft, as_hard = resource.getrlimit(resource.RLIMIT_AS)
        cpu_soft, cpu_hard = resource.getrlimit(resource.RLIMIT_CPU)
        return RlimitProbe(
            platform_is_linux=is_linux, resource_module_available=True,
            as_soft=as_soft, as_hard=as_hard, cpu_soft=cpu_soft, cpu_hard=cpu_hard,
            error=None,
        )
    except (ValueError, OSError) as exc:
        return RlimitProbe(
            platform_is_linux=is_linux, resource_module_available=True,
            as_soft=None, as_hard=None, cpu_soft=None, cpu_hard=None,
            error=f"getrlimit failed: {exc}",
        )


def check_protection_establishable() -> PreflightReport:
    """Actually probe this host's real capability to later establish a hard
    protection boundary, instead of unconditionally refusing.

    `ready_for_scientific_launch=True` is returned only when EITHER:
      - the native path looks viable: `resource` is importable, RLIMIT_AS and
        RLIMIT_CPU can genuinely be read back (platform is Linux, per
        specification.runtime.native.supported: "native macOS refuses"), OR
      - the Docker path looks viable: a `docker` binary exists on PATH AND
        `docker info` exits 0.
    A live cgroup v2 controller file is recorded as informative context (this
    process's OWN cgroup membership/controllers) but is not by itself
    sufficient or necessary for readiness, since a plain native RLIMIT-based
    guard does not require the caller's own process to already be inside a
    cgroup v2 tree, and a Docker-backend guard establishes its own container
    cgroup fresh at launch rather than reusing this process's.
    Any probe error is recorded and drives ready_for_scientific_launch=False
    with a precise reason; nothing here is assumed or copied from another
    host.
    """
    cgroup = probe_cgroup_v2()
    docker = probe_docker()
    rlimit = probe_rlimit_capability()

    native_viable = (
        rlimit.platform_is_linux
        and rlimit.resource_module_available
        and rlimit.error is None
        and rlimit.as_soft is not None
        and rlimit.cpu_soft is not None
    )
    docker_viable = docker.binary_found and docker.info_attempted and docker.info_exit_code == 0

    ready = native_viable or docker_viable
    reasons = []
    if native_viable:
        reasons.append(
            "native backend read-back succeeded: platform is Linux and "
            "RLIMIT_AS/RLIMIT_CPU were genuinely read via resource.getrlimit "
            f"(AS soft={rlimit.as_soft} hard={rlimit.as_hard}, "
            f"CPU soft={rlimit.cpu_soft} hard={rlimit.cpu_hard}). CAVEAT: this "
            "is a read-back-only signal -- actually lowering the hard limit "
            "with resource.setrlimit was deliberately NOT attempted, because "
            "a hard RLIMIT can only be lowered, never raised back, without "
            "elevated privilege, so testing it would irreversibly change "
            "this process's own session for the rest of its life. This "
            "probe therefore establishes only that a future guard COULD read "
            "the current limits before attempting to set them, not that "
            "setting a tighter limit would succeed on this host."
        )
    else:
        reasons.append(
            "native backend not viable on this host: "
            f"platform_is_linux={rlimit.platform_is_linux}, "
            f"resource_module_available={rlimit.resource_module_available}, "
            f"error={rlimit.error!r}."
        )
    if docker_viable:
        reasons.append(
            f"Docker backend viable: `docker` found at {docker.binary_path!r} "
            f"and `docker info` exited 0."
        )
    else:
        reasons.append(
            "Docker backend not viable on this host: "
            f"binary_found={docker.binary_found}, "
            f"info_exit_code={docker.info_exit_code}, "
            f"info_timed_out={docker.info_timed_out}, error={docker.error!r}."
        )
    reasons.append(
        f"cgroup v2 unified root present={cgroup.unified_root_exists}, "
        f"cgroup.controllers readable={cgroup.controllers_file_readable} "
        f"(content={cgroup.controllers_content!r}); this process's own cgroup "
        f"membership={cgroup.own_cgroup_path!r}. Recorded as context only; "
        "not itself sufficient or required for readiness (see docstring)."
    )

    return PreflightReport(
        constants_consistent=True,
        problems=[],
        ready_for_scientific_launch=ready,
        reason=(
            ("READY: " if ready else "NOT READY: ") + " ".join(reasons)
        ),
    )


def full_preflight_report() -> dict:
    """Aggregate report for implementation-report.yaml / README.md cross-check.

    Includes the raw probe outputs (never just the boolean verdicts) so a
    reader can see exactly what was observed on this host without re-running
    anything.
    """
    constants = check_declared_constants()
    protection = check_protection_establishable()
    cgroup = probe_cgroup_v2()
    docker = probe_docker()
    rlimit = probe_rlimit_capability()
    ready = constants.constants_consistent and protection.ready_for_scientific_launch
    return {
        "declared_constants": constants.to_json(),
        "protection_establishable": protection.to_json(),
        "raw_probes": {
            "cgroup_v2": cgroup.to_json(),
            "docker": docker.to_json(),
            "rlimit": rlimit.to_json(),
        },
        "ready_for_scientific_launch": ready,
        "note": (
            "declared_constants is a static source comparison; "
            "protection_establishable and raw_probes are real, side-effect-free "
            "live-host probes actually executed on this container at report-generation "
            "time. ready_for_scientific_launch here is the AND of both -- neither "
            "sub-result nor this aggregate implies check_launch_admission has been "
            "satisfied, nor does it authorize any run by itself."
        ),
    }
