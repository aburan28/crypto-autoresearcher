#!/usr/bin/env python3
"""Fail-closed launcher for the frozen four-level m=51 native-rho study.

Scientific mode requires the eventual endpoint binding and FROZEN.sha256.
The pre-discovery ``--mock`` and ``--selftest-only`` modes are explicitly
non-scientific and never execute rho on a deep endpoint.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import ctypes
import hashlib
import json
import math
import os
import platform
import random
import shlex
import shutil
import signal
import stat
import struct
import subprocess
import sys
import threading
import time
import types
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]


def _load_local_source(name: str, path: Path) -> tuple[Any, str]:
    """Compile named local source bytes directly, bypassing every pyc cache."""
    if path.is_symlink() or not path.is_file():
        raise RuntimeError(f"local module is not a regular file: {path}")
    source = path.read_bytes()
    digest = hashlib.sha256(source).hexdigest()
    module = types.ModuleType(name)
    module.__file__ = str(path)
    module.__package__ = ""
    previous = sys.modules.get(name)
    sys.modules[name] = module
    try:
        exec(compile(source, str(path), "exec"), module.__dict__)
    except BaseException:
        if previous is None:
            sys.modules.pop(name, None)
        else:
            sys.modules[name] = previous
        raise
    if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        raise RuntimeError(f"local module changed while loading: {path}")
    return module, digest


_design_module, LOADED_DESIGN_SHA256 = _load_local_source(
    "m51_runner_design", HERE / "design.py"
)
analysis_module: Any | None = None
LOADED_ANALYZE_SHA256: str | None = None

ARMS = _design_module.ARMS
CORE_PLAN_HEADER = _design_module.CORE_PLAN_HEADER
FIELD_MASK = _design_module.FIELD_MASK
INFERENCE_BLOCKS = _design_module.INFERENCE_BLOCKS
PAIR_COUNT = _design_module.PAIR_COUNT
PLAN_HEADER = _design_module.PLAN_HEADER
RNG_TEST_VECTORS = _design_module.RNG_TEST_VECTORS
SUBGROUP_ORDER = _design_module.SUBGROUP_ORDER
EndpointPair = _design_module.EndpointPair
build_plan = _design_module.build_plan
build_setup_robustness_plan = _design_module.build_setup_robustness_plan
conjugate = _design_module.conjugate
expected_scalar = _design_module.expected_scalar
expected_walk_stream = _design_module.expected_walk_stream
generate_schedule = _design_module.generate_schedule
load_json = _design_module.load_json
load_selection = _design_module.load_selection
orbit = _design_module.orbit
permuted = _design_module.permuted
read_f271_orbits = _design_module.read_f271_orbits
read_schedule = _design_module.read_schedule
sha256_file = _design_module.sha256_file
valid_sha256 = _design_module.valid_sha256

UINT64_MAX = (1 << 64) - 1
COMPILE_FLAGS = (
    "-std=gnu11",
    "-O2",
    "-Wall",
    "-Wextra",
    "-Wconversion",
    "-Wshadow",
    "-Werror",
    "-mpclmul",
    "-msse4.1",
    "-static",
)
CHILD_ENV = {
    "LANG": "C",
    "LC_ALL": "C",
    "PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
    "TZ": "UTC",
}
ANALYSIS_ENV = {
    **CHILD_ENV,
    "MKL_NUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
}
FROZEN_FILES = (
    "PROTOCOL.md",
    "README.md",
    "TRANSFER_BOUNDARY.md",
    "analyze.py",
    "batch_driver.c",
    "bind_selection.py",
    "build_schedule.py",
    "deep_selection.json",
    "design.py",
    "floor271_orbits.csv",
    "params.h",
    "rho.c",
    "run_benchmark.py",
    "schedule.csv",
    "spec.json",
    "synthetic_test.py",
)
RAW_HEADER = (
    "unit_id",
    "record_id",
    "run",
    "target_index",
    "target_scalar",
    "walk_stream_seed",
    "ops",
    "adds",
    "doubles",
    "setup_ops",
    "setup_adds",
    "setup_doubles",
    "walk_ops",
    "walk_adds",
    "walk_doubles",
    "canon_calls",
    "canon_x_squares",
    "canon_y_squares",
    "canon_sign_tests",
    "canon_negations",
    "walks",
    "cycles",
    "abandoned",
    "useless",
    "ok",
    "sec",
)
RAW_INTEGER_FIELDS = RAW_HEADER[:-1]
SETUP_HEADER = (
    "unit_id",
    "b",
    "a2",
    "mode",
    "setup_seed",
    "pgen_x",
    "pgen_y",
    "setup_fingerprint",
    "setup_sec",
)
NORMALIZED_HEADER = (
    *PLAN_HEADER,
    "worker",
    "unit_id",
    *(field for field in RAW_HEADER[2:] if field != "target_index"),
)


class RunError(RuntimeError):
    pass


def prepare_scientific_python_runtime() -> Any:
    """Fail before output unless Python is isolated, then import NumPy sanely."""
    global analysis_module, LOADED_ANALYZE_SHA256
    if sys.flags.isolated != 1 or sys.flags.dont_write_bytecode != 1:
        raise RunError("scientific mode requires Python -I -B")
    if "-I" not in sys.orig_argv or "-B" not in sys.orig_argv:
        raise RunError("scientific mode requires explicit separate -I and -B flags")
    if dict(os.environ) != ANALYSIS_ENV:
        raise RunError(
            "scientific mode requires the exact sanitized analysis environment"
        )
    # NumPy is first imported by analyze.py below, after the numerical backend
    # thread/environment contract has become exact for this process.
    os.environ.clear()
    os.environ.update(ANALYSIS_ENV)
    if analysis_module is None:
        analysis_module, LOADED_ANALYZE_SHA256 = _load_local_source(
            "m51_runner_analyze", HERE / "analyze.py"
        )
    return analysis_module


def analysis_runtime_receipt() -> dict[str, Any]:
    if analysis_module is None or LOADED_ANALYZE_SHA256 is None:
        raise RunError("analysis runtime was not initialized")
    np = analysis_module.np
    numpy_init = Path(np.__file__).resolve(strict=True)
    numpy_core = Path(np._core._multiarray_umath.__file__).resolve(strict=True)
    mapped: dict[str, str] = {}
    for line in Path("/proc/self/maps").read_text().splitlines():
        fields = line.split()
        if len(fields) < 6 or not fields[-1].startswith("/"):
            continue
        raw_path = fields[-1]
        lowered = raw_path.lower()
        if not any(token in lowered for token in ("numpy", "openblas", "lapack", "libblas", "libgomp")):
            continue
        path = Path(raw_path)
        if path.is_file() and not path.is_symlink():
            resolved = path.resolve(strict=True)
            mapped[str(resolved)] = sha256_file(resolved)
    config = getattr(np.__config__, "CONFIG", None)
    try:
        config_json = json.loads(json.dumps(config, sort_keys=True, default=str))
    except (TypeError, ValueError) as exc:
        raise RunError("NumPy build configuration is not serializable") from exc
    return {
        "schema": "m51-deep-rho-analysis-runtime/v1",
        "command": list(getattr(sys, "orig_argv", sys.argv)),
        "argv": list(sys.argv),
        "environment": dict(ANALYSIS_ENV),
        "python": {
            "version": sys.version,
            "executable": str(Path(sys.executable).resolve(strict=True)),
            "executable_sha256": sha256_file(Path(sys.executable).resolve(strict=True)),
            "flags": {
                "isolated": sys.flags.isolated,
                "dont_write_bytecode": sys.flags.dont_write_bytecode,
                "ignore_environment": sys.flags.ignore_environment,
                "no_user_site": sys.flags.no_user_site,
            },
        },
        "numpy": {
            "version": np.__version__,
            "package_init": str(numpy_init),
            "package_init_sha256": sha256_file(numpy_init),
            "core_extension": str(numpy_core),
            "core_extension_sha256": sha256_file(numpy_core),
            "build_config": config_json,
            "mapped_numerical_objects": [
                {"path": path, "sha256": digest}
                for path, digest in sorted(mapped.items())
            ],
        },
        "local_source": {
            "design_sha256": LOADED_DESIGN_SHA256,
            "analyze_sha256": LOADED_ANALYZE_SHA256,
        },
    }


_subreaper_lock = threading.Lock()
_subreaper_enabled = False


@dataclass
class Unit:
    key: tuple[str, int, int, int, int]
    chunk: int
    records: list[dict[str, Any]]


@dataclass
class WorkerPlan:
    worker: int
    core: int
    units: list[Unit]
    records: list[dict[str, Any]]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def durable_mkdir(path: Path, *, parents: bool = False) -> None:
    path.mkdir(parents=parents)
    fsync_directory(path.parent)


def atomic_write_text(path: Path, value: str) -> None:
    if path.exists() or path.is_symlink():
        raise FileExistsError(f"refusing to overwrite {path}")
    partial = path.with_name(path.name + ".partial")
    if partial.exists() or partial.is_symlink():
        raise FileExistsError(f"refusing pre-existing partial {partial}")
    with partial.open("x") as handle:
        handle.write(value)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(partial, path)
    fsync_directory(path.parent)


def atomic_write_json(path: Path, value: Any) -> None:
    atomic_write_text(path, json.dumps(value, indent=2, sort_keys=True) + "\n")


def replace_json(path: Path, value: Any) -> None:
    partial = path.with_name(path.name + ".partial")
    if partial.exists() or partial.is_symlink():
        raise FileExistsError(f"refusing pre-existing partial {partial}")
    with partial.open("x") as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(partial, path)
    fsync_directory(path.parent)


def valid_manifest_name(value: str) -> bool:
    path = PurePosixPath(value)
    return (
        value == path.as_posix()
        and not path.is_absolute()
        and len(path.parts) == 1
        and path.parts[0] not in ("", ".", "..")
    )


def verify_frozen_inputs() -> tuple[dict[str, str], str]:
    path = HERE / "FROZEN.sha256"
    if path.is_symlink() or not path.is_file():
        raise RunError("scientific mode requires a regular FROZEN.sha256")
    content = path.read_text()
    if not content or not content.endswith("\n"):
        raise RunError("FROZEN.sha256 must be nonempty and newline terminated")
    entries: dict[str, str] = {}
    for number, line in enumerate(content.splitlines(), 1):
        pieces = line.split("  ", 1)
        if (
            len(pieces) != 2
            or not valid_sha256(pieces[0])
            or not valid_manifest_name(pieces[1])
            or pieces[1] in entries
        ):
            raise RunError(f"FROZEN.sha256:{number}: malformed entry")
        entries[pieces[1]] = pieces[0]
    if tuple(entries) != tuple(sorted(FROZEN_FILES)) or set(entries) != set(FROZEN_FILES):
        raise RunError("FROZEN.sha256 file set/order differs from the scientific contract")
    for name, expected in entries.items():
        target = HERE / name
        if target.is_symlink() or not target.is_file() or sha256_file(target) != expected:
            raise RunError(f"frozen input differs: {name}")
    return entries, hashlib.sha256(content.encode()).hexdigest()


def enable_child_subreaper() -> None:
    """Make orphaned descendants reapable by this Linux runner."""
    global _subreaper_enabled
    with _subreaper_lock:
        if _subreaper_enabled:
            return
        libc = ctypes.CDLL(None, use_errno=True)
        try:
            prctl = libc.prctl
        except AttributeError as exc:
            raise RunError("prctl(PR_SET_CHILD_SUBREAPER) is required") from exc
        prctl.argtypes = (
            ctypes.c_int,
            ctypes.c_ulong,
            ctypes.c_ulong,
            ctypes.c_ulong,
            ctypes.c_ulong,
        )
        prctl.restype = ctypes.c_int
        if prctl(36, 1, 0, 0, 0) != 0:  # PR_SET_CHILD_SUBREAPER
            error_number = ctypes.get_errno()
            raise OSError(error_number, os.strerror(error_number))
        _subreaper_enabled = True


def command_output(
    argv: list[str], *, cwd: Path | None = None, timeout: float = 30.0
) -> str:
    """Run even short provenance commands under the bounded group lifecycle."""
    receipt = run_subprocess(argv, cwd=cwd or HERE, timeout=timeout)
    if (
        receipt["exit_status"] != 0
        or receipt["timed_out"]
        or receipt["cancelled"]
        or receipt["residual_group_cleaned"]
        or receipt["stderr"]
    ):
        raise RunError(
            f"command failed {argv!r}: rc={receipt['exit_status']}, "
            f"stderr={receipt['stderr'][-1000:]!r}"
        )
    return str(receipt["stdout"]).strip()


def git_receipt(*, require_clean: bool) -> dict[str, Any]:
    root = Path(command_output(["git", "rev-parse", "--show-toplevel"], cwd=HERE)).resolve()
    if root != REPO.resolve():
        raise RunError("study directory resolves to an unexpected Git worktree")
    status = command_output(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"], cwd=REPO
    )
    if require_clean and status:
        raise RunError("scientific launch requires a clean committed worktree")
    return {
        "root": str(root),
        "commit": command_output(["git", "rev-parse", "HEAD"], cwd=REPO),
        "branch": command_output(["git", "branch", "--show-current"], cwd=REPO),
        "status_porcelain": status,
        "clean": not bool(status),
    }


def host_receipt(
    cores: list[int], *, analysis_runtime: dict[str, Any] | None = None
) -> dict[str, Any]:
    available = sorted(os.sched_getaffinity(0))
    if not set(cores).issubset(available):
        raise RunError(f"required cores {cores} outside affinity {available}")
    flags: set[str] = set()
    model = None
    for line in Path("/proc/cpuinfo").read_text().splitlines():
        if model is None and line.startswith("model name"):
            model = line.split(":", 1)[1].strip()
        if line.startswith("flags"):
            flags.update(line.split(":", 1)[1].split())
    missing = {"pclmulqdq", "sse4_1"} - flags
    if missing:
        raise RunError(f"host lacks required CPU features: {sorted(missing)}")
    gcc = shutil.which("gcc", path=CHILD_ENV["PATH"])
    taskset = shutil.which("taskset", path=CHILD_ENV["PATH"])
    if gcc is None or taskset is None:
        raise RunError("gcc and taskset are required")
    return {
        "created_utc": utc_now(),
        "platform": platform.platform(),
        "uname": platform.uname()._asdict(),
        "python": sys.version,
        "python_executable": sys.executable,
        "python_sha256": sha256_file(Path(sys.executable).resolve()),
        "python_flags": {
            "isolated": sys.flags.isolated,
            "dont_write_bytecode": sys.flags.dont_write_bytecode,
            "ignore_environment": sys.flags.ignore_environment,
            "no_user_site": sys.flags.no_user_site,
        },
        "analysis_runtime": analysis_runtime,
        "process_affinity": available,
        "selected_cores": cores,
        "cpu_model": model,
        "cpu_flags": sorted(flags),
        "gcc": gcc,
        "gcc_sha256": sha256_file(Path(gcc).resolve()),
        "gcc_version": command_output([gcc, "--version"]).splitlines()[0],
        "taskset": taskset,
        "taskset_sha256": sha256_file(Path(taskset).resolve()),
    }


def validate_spec(spec: dict[str, Any]) -> None:
    if spec.get("schema") != "m51-deep-rho-study/v1":
        raise RunError("spec schema differs")
    design = spec.get("design")
    if not isinstance(design, dict) or any(
        design.get(key) != value
        for key, value in {
            "pair_strata": 32,
            "inference_blocks": 3072,
            "inference_solves": 12288,
            "aa_blocks": 1024,
            "aa_solves": 8192,
            "total_solves": 20480,
            "expected_distinct_native_models": 3537,
            "expected_execution_units": 3556,
        }.items()
    ):
        raise RunError("spec design constants differ")
    seeds = spec.get("seeds")
    expected_seeds = {
        "setup_root": 202610136102,
        "target_root": 202610136101,
        "walk_inference_root": 202610136103,
        "walk_aa_a_root": 202610136104,
        "walk_aa_b_root": 202610136105,
        "schedule_root": 202610136106,
        "multiplier_root": 202610136107,
        "synthetic_test_root": 202610136108,
    }
    if seeds != expected_seeds:
        raise RunError("spec seed namespaces differ")
    family = spec.get("contrast_family")
    if (
        not isinstance(family, dict)
        or family.get("family_confidence") != 0.95
        or family.get("resamples") != 100000
        or family.get("multiplier_domain") != 0x4D41494E
        or family.get("pairwise_equivalence_boundary_inclusive") is not True
        or len(family.get("pairwise", [])) != 6
        or len(family.get("factorial", [])) != 3
    ):
        raise RunError("spec nine-contrast inference family differs")
    aa_gate = spec.get("aa_gate")
    if (
        not isinstance(aa_gate, dict)
        or aa_gate.get("family_confidence") != 0.99
        or aa_gate.get("resamples") != 100000
        or aa_gate.get("multiplier_domain") != 0x41414741
        or aa_gate.get("margin_bits") != 0.15
        or aa_gate.get("margin_boundary_inclusive") is not True
    ):
        raise RunError("spec A/A gate differs")
    execution = spec.get("execution")
    if (
        not isinstance(execution, dict)
        or execution.get("child_environment") != CHILD_ENV
        or execution.get("analysis_environment") != ANALYSIS_ENV
        or execution.get("scientific_python_flags") != ["-I", "-B"]
        or execution.get("static_elf_without_pt_interp_or_pt_dynamic_required") is not True
        or execution.get("linux_child_subreaper_and_process_group_cleanup_required") is not True
        or "-static" not in str(execution.get("compile", "")).split()
    ):
        raise RunError("spec execution-integrity contract differs")
    robustness = spec.get("setup_robustness")
    if (
        not isinstance(robustness, dict)
        or robustness.get("inferential_fresh_setup_roots") != 16
        or robustness.get("descriptive_original_root_bridges") != 1
        or robustness.get("total_setup_roots") != 17
        or robustness.get("blocks_per_setup_root") != 32
        or robustness.get("arms_per_block") != 4
        or robustness.get("conditional_solves") != 2176
        or robustness.get("family_confidence") != 0.95
        or robustness.get("trigger_abs_bits") != 0.5
        or robustness.get("sign_vectors") != 65536
        or robustness.get("sign_vectors_sha256")
        != "9b8f77ce3b82c7aec98a8de4808e3518d8fa8d7833735bd2373edad34582e9f1"
        or robustness.get("critical_rank_1_based") != 62260
        or robustness.get("panel_seed") != 202610136109
        or robustness.get("target_seed") != 202610136110
        or robustness.get("walk_seed") != 202610136111
        or robustness.get("setup_seed_derivation_root") != 202610136112
        or not isinstance(robustness.get("setup_seeds"), list)
        or len(set(robustness.get("setup_seeds", []))) != 16
        or robustness.get("original_setup_seed") != expected_seeds["setup_root"]
        or not isinstance(robustness.get("disjoint_from_primary_seeds"), list)
        or set(robustness.get("disjoint_from_primary_seeds", []))
        != set(expected_seeds.values())
        or robustness.get("distinct_models_by_arm")
        != {"C": 1, "A": 32, "P": 32, "B": 32}
        or robustness.get("distinct_models_total") != 97
        or robustness.get("execution_units_if_triggered") != 1649
        or robustness.get("post_seal_recovery")
        != "if an asynchronous exception lands after an atomic primary or conditional phase seal, classify or recover that phase only after independently verifying every on-disk MANIFEST entry and bound phase artifact; a missing, malformed, or mismatched seal is never recovered"
        or robustness.get("persistence_rule")
        != {
            "scope": "each primary triggering contrast",
            "directional": "fresh-root simultaneous CI strictly excludes zero in the primary direction",
            "practical": "fresh-root simultaneous CI lies wholly at or beyond +0.5 bit for a positive primary direction or -0.5 bit for a negative primary direction",
            "practical_threshold_abs_bits": 0.5,
            "practical_boundary_inclusive": True,
            "global_categories": ["complete", "partial", "none"],
            "same-sign_point_alone_is_persistence": False,
        }
    ):
        raise RunError("spec setup-robustness contract differs")
    inputs = spec.get("inputs")
    for name, expected in {
        "f271_census_sha256": "bb4b64d5e8d53b323cd7493af435c738198b90b0ba8696316bb36e8709150fbe",
        "rho_core_sha256": "f86cf62f8c0bf6ea9bb35e5358e0aec99f995db5779b0cf179d1b896d7cb9327",
        "params_sha256": "cb3790db6122996da89b260a6bd57301b02f5f96760fe80caacb795b3bef18b2",
        "schedule_sha256": "9ee1fbc0371f501a91c6af6d337d10ffed4b0be0b0b35c3609049a343bf4cc7a",
    }.items():
        if not isinstance(inputs, dict) or inputs.get(name) != expected:
            raise RunError(f"spec input binding differs: {name}")


def copy_snapshot(out: Path, frozen: tuple[dict[str, str], str]) -> Path:
    inputs = out / "inputs"
    durable_mkdir(inputs)
    entries, _ = frozen
    for name, expected in entries.items():
        source = HERE / name
        target = inputs / name
        partial = target.with_name(target.name + ".partial")
        with source.open("rb") as src, partial.open("xb") as dst:
            shutil.copyfileobj(src, dst)
            dst.flush()
            os.fsync(dst.fileno())
        if sha256_file(partial) != expected:
            raise RunError(f"snapshot copy hash differs: {name}")
        os.replace(partial, target)
        fsync_directory(inputs)
    atomic_write_text(inputs / "FROZEN.sha256", (HERE / "FROZEN.sha256").read_text())
    return inputs


def run_subprocess(
    command: list[str],
    *,
    cwd: Path,
    timeout: float,
    cancel: threading.Event | None = None,
) -> dict[str, Any]:
    enable_child_subreaper()
    started_utc = utc_now()
    started = time.monotonic()
    process = subprocess.Popen(
        command,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=True,
        env=CHILD_ENV,
    )
    deadline = started + timeout
    timed_out = False
    cancelled = False

    def signal_group(signum: int) -> bool:
        try:
            os.killpg(process.pid, signum)
        except ProcessLookupError:
            return False
        return True

    def terminate() -> None:
        signal_group(signal.SIGTERM)
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            signal_group(signal.SIGKILL)
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired as exc:
                raise RunError(
                    f"process-group leader {process.pid} survived SIGKILL"
                ) from exc

    def reap_group_children() -> None:
        while True:
            try:
                child, _ = os.waitpid(-process.pid, os.WNOHANG)
            except ChildProcessError:
                return
            if child == 0:
                return

    def group_exists() -> bool:
        try:
            os.killpg(process.pid, 0)
        except ProcessLookupError:
            return False
        except PermissionError:
            return True
        return True

    def cleanup_residual_group() -> bool:
        residual = group_exists()
        if not residual:
            reap_group_children()
            return False
        signal_group(signal.SIGTERM)
        grace_deadline = time.monotonic() + 2
        while time.monotonic() < grace_deadline:
            reap_group_children()
            if not group_exists():
                return True
            time.sleep(0.01)
        signal_group(signal.SIGKILL)
        kill_deadline = time.monotonic() + 2
        while time.monotonic() < kill_deadline:
            reap_group_children()
            if not group_exists():
                return True
            time.sleep(0.01)
        reap_group_children()
        if group_exists():
            raise RunError(f"process group {process.pid} survived SIGKILL/reap")
        return True

    def drain_after_group_cleanup() -> tuple[str, str]:
        """Drain pipes only after the process group is gone, with a hard bound."""
        try:
            return process.communicate(timeout=2)
        except subprocess.TimeoutExpired as exc:
            stdout = exc.output if isinstance(exc.output, str) else ""
            stderr = exc.stderr if isinstance(exc.stderr, str) else ""
            if process.stdout is not None:
                process.stdout.close()
            if process.stderr is not None:
                process.stderr.close()
            stderr += "RUNNER: bounded pipe drain expired after process-group cleanup\n"
            return stdout, stderr

    residual_cleaned = False
    try:
        while True:
            if cancel is not None and cancel.is_set():
                cancelled = True
                terminate()
                residual_cleaned = cleanup_residual_group()
                stdout, stderr = drain_after_group_cleanup()
                break
            if time.monotonic() >= deadline:
                timed_out = True
                terminate()
                residual_cleaned = cleanup_residual_group()
                stdout, stderr = drain_after_group_cleanup()
                break
            if process.poll() is not None:
                residual_cleaned = cleanup_residual_group()
                stdout, stderr = drain_after_group_cleanup()
                break
            try:
                stdout, stderr = process.communicate(
                    timeout=max(0.001, min(0.1, deadline - time.monotonic()))
                )
                break
            except subprocess.TimeoutExpired:
                continue
        residual_cleaned = cleanup_residual_group() or residual_cleaned
        if residual_cleaned:
            stderr += "RUNNER: residual process group terminated and reaped\n"
    except BaseException:
        try:
            terminate()
        finally:
            try:
                cleanup_residual_group()
            finally:
                drain_after_group_cleanup()
        raise
    return {
        "command": command,
        "cwd": str(cwd),
        "started_utc": started_utc,
        "finished_utc": utc_now(),
        "elapsed_seconds": time.monotonic() - started,
        "exit_status": process.returncode,
        "timed_out": timed_out,
        "cancelled": cancelled,
        "residual_group_cleaned": residual_cleaned,
        "environment": CHILD_ENV,
        "stdout": stdout,
        "stderr": stderr,
    }


def verify_static_elf(path: Path) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise RunError(f"compiled binary is not a regular file: {path}")
    data = path.read_bytes()
    if len(data) < 64 or data[:4] != b"\x7fELF" or data[4] != 2 or data[5] != 1:
        raise RunError("compiled binary is not a 64-bit little-endian ELF executable")
    program_offset = struct.unpack_from("<Q", data, 32)[0]
    program_entry_size = struct.unpack_from("<H", data, 54)[0]
    program_count = struct.unpack_from("<H", data, 56)[0]
    if program_entry_size < 56 or program_count == 0:
        raise RunError("compiled ELF has malformed program headers")
    if program_offset + program_entry_size * program_count > len(data):
        raise RunError("compiled ELF program headers extend past end of file")
    program_types = [
        struct.unpack_from("<I", data, program_offset + index * program_entry_size)[0]
        for index in range(program_count)
    ]
    if 2 in program_types or 3 in program_types:  # PT_DYNAMIC, PT_INTERP
        raise RunError("compiled ELF contains PT_DYNAMIC or PT_INTERP")
    return {
        "schema": "m51-deep-rho-static-elf/v1",
        "elf_class_bits": 64,
        "little_endian": True,
        "program_header_count": program_count,
        "pt_dynamic_present": False,
        "pt_interp_present": False,
    }


def build_binaries(inputs: Path, out: Path, host: dict[str, Any]) -> dict[str, Any]:
    build = out / "build"
    durable_mkdir(build)
    batch_partial = build / "rho-batch.partial"
    legacy_partial = build / "rho-selftest.partial"
    batch_command = [host["gcc"], *COMPILE_FLAGS, "-o", str(batch_partial), "batch_driver.c"]
    legacy_command = [host["gcc"], *COMPILE_FLAGS, "-o", str(legacy_partial), "rho.c"]
    receipts = []
    for label, command, partial, final in (
        ("batch", batch_command, batch_partial, build / "rho-batch"),
        ("selftest", legacy_command, legacy_partial, build / "rho-selftest"),
    ):
        receipt = run_subprocess(command, cwd=inputs, timeout=120)
        stdout = receipt.pop("stdout")
        stderr = receipt.pop("stderr")
        atomic_write_text(build / f"{label}.stdout", stdout)
        atomic_write_text(build / f"{label}.stderr", stderr)
        receipt.update(
            {
                "stdout_sha256": sha256_file(build / f"{label}.stdout"),
                "stderr_sha256": sha256_file(build / f"{label}.stderr"),
            }
        )
        if receipt["exit_status"] != 0 or receipt["timed_out"] or stderr:
            atomic_write_json(build / f"{label}.receipt.json", receipt)
            raise RunError(f"build failed: {receipt}")
        if not partial.is_file():
            raise RunError("compiler did not create expected binary")
        receipt["static_elf"] = verify_static_elf(partial)
        with partial.open("rb") as handle:
            os.fsync(handle.fileno())
        os.replace(partial, final)
        fsync_directory(build)
        atomic_write_json(build / f"{label}.receipt.json", receipt)
        receipts.append(receipt)
    summary = {
        "schema": "m51-deep-rho-build/v1",
        "compile_flags": list(COMPILE_FLAGS),
        "receipts": receipts,
        "batch_binary_sha256": sha256_file(build / "rho-batch"),
        "selftest_binary_sha256": sha256_file(build / "rho-selftest"),
        "rho_source_sha256": sha256_file(inputs / "rho.c"),
        "batch_driver_sha256": sha256_file(inputs / "batch_driver.c"),
        "params_sha256": sha256_file(inputs / "params.h"),
    }
    atomic_write_json(build / "build-receipt.json", summary)
    return summary


def run_startup_selftests(
    binary: Path,
    f271: dict[int, int],
    setup_seed: int,
    out: Path,
) -> dict[str, Any]:
    directory = out / "selftests"
    durable_mkdir(directory)
    cases = [("C", 1), *((f"A-o{orbit_id:02d}", b) for orbit_id, b in sorted(f271.items()))]
    certificates: list[dict[str, Any]] = []
    for label, b in cases:
        command = [str(binary), "selftest", str(b), "0", "0", str(setup_seed)]
        receipt = run_subprocess(command, cwd=binary.parent, timeout=300)
        atomic_write_text(directory / f"{label}.stdout", receipt["stdout"])
        atomic_write_text(directory / f"{label}.stderr", receipt["stderr"])
        stable_receipt = {key: value for key, value in receipt.items() if key not in ("stdout", "stderr")}
        stable_receipt["stdout_sha256"] = sha256_file(directory / f"{label}.stdout")
        stable_receipt["stderr_sha256"] = sha256_file(directory / f"{label}.stderr")
        atomic_write_json(directory / f"{label}.receipt.json", stable_receipt)
        if receipt["exit_status"] != 0 or receipt["timed_out"] or receipt["stderr"]:
            raise RunError(f"startup selftest failed for {label}")
        line = receipt["stdout"].strip()
        fields: dict[str, str] = {}
        for token in line.split():
            if "=" not in token:
                raise RunError(f"malformed selftest output for {label}")
            key, value = token.split("=", 1)
            if key in fields:
                raise RunError(f"duplicate selftest field for {label}: {key}")
            fields[key] = value
        expected = {
            "selftest_ok": "1",
            "b": str(b),
            "a2": "0",
            "mode": "0",
            "action_step": "0",
            "action_order": "1",
            "setup_seed": str(setup_seed),
        }
        if any(fields.get(key) != value for key, value in expected.items()):
            raise RunError(f"selftest certificate differs for {label}")
        if set(fields) != {*expected, "pgen_x", "pgen_y", "setup_fingerprint"}:
            raise RunError(f"selftest fields differ for {label}")
        certificates.append({"label": label, **fields})
    summary = {
        "schema": "m51-deep-rho-startup-selftests/v1",
        "count": len(certificates),
        "certificates": certificates,
    }
    atomic_write_json(out / "selftests.json", summary)
    return summary


def run_rng_vector_crosscheck(binary: Path, out: Path) -> dict[str, Any]:
    """Cross-check frozen Python oracle literals against the compiled C core."""
    directory = out / "rng-vectors"
    durable_mkdir(directory)
    certificates: list[dict[str, Any]] = []
    for index, vector in enumerate(RNG_TEST_VECTORS):
        target_seed, walk_seed, target_index, scalar, stream = vector
        if expected_scalar(target_seed, target_index) != scalar:
            raise RunError(f"Python scalar oracle differs from fixed vector {index}")
        if expected_walk_stream(walk_seed, target_index) != stream:
            raise RunError(f"Python walk-stream oracle differs from fixed vector {index}")
        command = [
            str(binary),
            "rng-vector",
            str(target_seed),
            str(walk_seed),
            str(target_index),
        ]
        receipt = run_subprocess(command, cwd=binary.parent, timeout=30)
        stdout_path = directory / f"vector-{index:02d}.stdout"
        stderr_path = directory / f"vector-{index:02d}.stderr"
        atomic_write_text(stdout_path, receipt.pop("stdout"))
        atomic_write_text(stderr_path, receipt.pop("stderr"))
        receipt.update(
            {
                "stdout_sha256": sha256_file(stdout_path),
                "stderr_sha256": sha256_file(stderr_path),
            }
        )
        atomic_write_json(directory / f"vector-{index:02d}.receipt.json", receipt)
        expected_line = (
            f"target_seed={target_seed} walk_seed={walk_seed} "
            f"target_index={target_index} target_scalar={scalar} "
            f"walk_stream_seed={stream}\n"
        )
        if (
            receipt["exit_status"] != 0
            or receipt["timed_out"]
            or receipt["cancelled"]
            or receipt["residual_group_cleaned"]
            or stdout_path.read_text() != expected_line
            or stderr_path.stat().st_size != 0
        ):
            raise RunError(f"compiled C RNG vector differs at index {index}")
        certificates.append(
            {
                "index": index,
                "target_seed": target_seed,
                "walk_seed": walk_seed,
                "target_index": target_index,
                "target_scalar": scalar,
                "walk_stream_seed": stream,
                "stdout_sha256": sha256_file(stdout_path),
                "receipt_sha256": sha256_file(directory / f"vector-{index:02d}.receipt.json"),
            }
        )
    summary = {
        "schema": "m51-deep-rho-rng-crosscheck/v1",
        "count": len(certificates),
        "binary_sha256": sha256_file(binary),
        "vectors": certificates,
    }
    atomic_write_json(out / "rng_vectors.json", summary)
    return summary


def make_units(
    records: list[dict[str, Any]],
    seed: int,
    workers: int,
    cores: list[int],
    *,
    expected_models: int = 3537,
    expected_units: int = 3556,
    expected_records: int = 20480,
) -> list[WorkerPlan]:
    grouped: dict[tuple[str, int, int, int, int], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        key = (
            str(record["curve_id"]),
            int(record["b"]),
            int(record["a2"]),
            int(record["mode"]),
            int(record["setup_seed"]),
        )
        grouped[key].append(record)
    if len({str(record["curve_id"]) for record in records}) != expected_models:
        raise RunError(
            f"record plan exercises an unexpected number of distinct models; expected {expected_models}"
        )
    units: list[Unit] = []
    for key, values in sorted(grouped.items()):
        values.sort(key=lambda row: row["record_id"])
        for chunk, offset in enumerate(range(0, len(values), 256)):
            units.append(Unit(key=key, chunk=chunk, records=values[offset : offset + 256]))
    if len(units) != expected_units:
        raise RunError(f"record plan has {len(units)} execution units, expected {expected_units}")
    units.sort(
        key=lambda unit: (
            hashlib.sha256(
                f"{seed}|execution-unit|{unit.key}|{unit.chunk}".encode("ascii")
            ).digest(),
            unit.key,
            unit.chunk,
        )
    )
    allocations: list[list[Unit]] = [[] for _ in range(workers)]
    loads = [0] * workers
    for unit in units:
        worker = min(range(workers), key=lambda index: (loads[index], index))
        allocations[worker].append(unit)
        loads[worker] += len(unit.records)
    plans = [
        WorkerPlan(
            worker=index,
            core=cores[index],
            units=allocations[index],
            records=[record for unit in allocations[index] for record in unit.records],
        )
        for index in range(workers)
    ]
    if sorted(loads)[-1] - sorted(loads)[0] > 256 or sum(loads) != expected_records:
        raise RunError(f"worker load balance differs: {loads}")
    return plans


def canonical_plan_sha256(records: list[dict[str, Any]]) -> str:
    encoded = json.dumps(
        records, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def validate_robustness_setup_certificates(
    planned: list[dict[str, Any]],
    setups: list[dict[str, Any]],
    setup_seeds: list[int],
) -> dict[str, Any]:
    """Require one independently generated certificate per model and root."""
    if len(setup_seeds) != 17 or len(set(setup_seeds)) != 17:
        raise RunError("setup-robustness requires 17 distinct setup roots")
    expected_models: dict[str, tuple[int, int, int]] = {}
    for row in planned:
        identity = (int(row["b"]), int(row["a2"]), int(row["mode"]))
        prior = expected_models.setdefault(str(row["curve_id"]), identity)
        if prior != identity:
            raise RunError("setup-robustness curve identity changes across roots")
    if len(expected_models) != 97:
        raise RunError("setup-robustness panel does not contain 97 native models")
    by_curve: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in setups:
        by_curve[str(row["curve_id"])].append(row)
    if set(by_curve) != set(expected_models):
        raise RunError("setup-robustness setup/model coverage differs")
    expected_seed_set = set(setup_seeds)
    for curve_id, rows in by_curve.items():
        if len(rows) != 17 or {int(row["setup_seed"]) for row in rows} != expected_seed_set:
            raise RunError(f"setup-robustness {curve_id} lacks one setup per root")
        b, a2, mode = expected_models[curve_id]
        if any(
            (int(row["b"]), int(row["a2"]), int(row["mode"])) != (b, a2, mode)
            for row in rows
        ):
            raise RunError(f"setup-robustness {curve_id} setup identity differs")
        identities = {
            (int(row["pgen_x"]), int(row["pgen_y"]), str(row["setup_fingerprint"]))
            for row in rows
        }
        if len(identities) != 17:
            raise RunError(
                f"setup-robustness {curve_id} does not have 17 distinct setup certificates"
            )
    return {
        "distinct_models": len(by_curve),
        "certificates_per_model": 17,
        "distinct_certificate_identities_per_model": 17,
        "setup_seeds": setup_seeds,
    }


def write_csv_exclusive(path: Path, fieldnames: Iterable[str], rows: Iterable[dict[str, Any]]) -> None:
    if path.exists() or path.is_symlink():
        raise FileExistsError(f"refusing to overwrite {path}")
    partial = path.with_name(path.name + ".partial")
    with partial.open("x", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=tuple(fieldnames), lineterminator="\n", extrasaction="raise")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(partial, path)
    fsync_directory(path.parent)


def materialize_plan(
    records: list[dict[str, Any]],
    worker_plans: list[WorkerPlan],
    out: Path,
) -> dict[str, Any]:
    plan_dir = out / "plans"
    durable_mkdir(plan_dir)
    write_csv_exclusive(out / "record_plan.csv", PLAN_HEADER, records)
    workers = []
    for plan in worker_plans:
        core_rows: list[dict[str, Any]] = []
        for local_unit, unit in enumerate(plan.units):
            for record in unit.records:
                core_rows.append(
                    {
                        "unit_id": local_unit,
                        "record_id": record["record_id"],
                        "b": record["b"],
                        "a2": record["a2"],
                        "mode": record["mode"],
                        "setup_seed": record["setup_seed"],
                        "target_seed": record["target_seed"],
                        "walk_seed": record["walk_seed"],
                        "target_index": record["target_index"],
                    }
                )
        path = plan_dir / f"worker-{plan.worker}.csv"
        write_csv_exclusive(path, CORE_PLAN_HEADER, core_rows)
        workers.append(
            {
                "worker": plan.worker,
                "core": plan.core,
                "records": len(core_rows),
                "units": len(plan.units),
                "plan": path.relative_to(out).as_posix(),
                "plan_sha256": sha256_file(path),
            }
        )
    summary = {
        "schema": "m51-deep-rho-plan/v1",
        "records": len(records),
        "record_plan_sha256": sha256_file(out / "record_plan.csv"),
        "distinct_models": len({record["curve_id"] for record in records}),
        "execution_units": sum(len(plan.units) for plan in worker_plans),
        "workers": workers,
    }
    atomic_write_json(out / "plan.json", summary)
    return summary


def worker_command(
    plan: WorkerPlan,
    out: Path,
    binary: Path,
    taskset: str,
    timeout: float,
    cancel: threading.Event,
) -> dict[str, Any]:
    raw_dir = out / "raw"
    plan_path = out / "plans" / f"worker-{plan.worker}.csv"
    result_partial = raw_dir / f"worker-{plan.worker}.results.csv.partial"
    setup_partial = raw_dir / f"worker-{plan.worker}.setups.csv.partial"
    command = [
        taskset,
        "-c",
        str(plan.core),
        str(binary),
        "run-plan",
        str(plan_path),
        str(result_partial),
        str(setup_partial),
    ]
    receipt = run_subprocess(command, cwd=out, timeout=timeout, cancel=cancel)
    stdout_path = raw_dir / f"worker-{plan.worker}.stdout"
    stderr_path = raw_dir / f"worker-{plan.worker}.stderr"
    atomic_write_text(stdout_path, receipt.pop("stdout"))
    atomic_write_text(stderr_path, receipt.pop("stderr"))
    receipt.update(
        {
            "schema": "m51-deep-rho-worker-receipt/v1",
            "worker": plan.worker,
            "core": plan.core,
            "plan_sha256": sha256_file(plan_path),
            "binary_sha256": sha256_file(binary),
            "stdout_sha256": sha256_file(stdout_path),
            "stderr_sha256": sha256_file(stderr_path),
            "expected_records": len(plan.records),
            "expected_units": len(plan.units),
        }
    )
    success = (
        receipt["exit_status"] == 0
        and not receipt["timed_out"]
        and not receipt["cancelled"]
        and not receipt["residual_group_cleaned"]
        and receipt["environment"] == CHILD_ENV
        and (raw_dir / f"worker-{plan.worker}.stderr").stat().st_size == 0
        and result_partial.is_file()
        and setup_partial.is_file()
    )
    receipt["success"] = success
    atomic_write_json(raw_dir / f"worker-{plan.worker}.receipt.json", receipt)
    if success:
        for partial, final in (
            (result_partial, raw_dir / f"worker-{plan.worker}.results.csv"),
            (setup_partial, raw_dir / f"worker-{plan.worker}.setups.csv"),
        ):
            with partial.open("rb") as handle:
                os.fsync(handle.fileno())
            os.replace(partial, final)
            fsync_directory(raw_dir)
    else:
        cancel.set()
    return receipt


def parse_decimal(value: Any, context: str) -> int:
    if not isinstance(value, str) or not value or not value.isascii() or not value.isdecimal():
        raise RunError(f"{context}: expected unsigned decimal")
    parsed = int(value)
    if parsed > UINT64_MAX:
        raise RunError(f"{context}: exceeds uint64")
    return parsed


def validate_raw_worker(plan: WorkerPlan, out: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    raw_dir = out / "raw"
    path = raw_dir / f"worker-{plan.worker}.results.csv"
    expected_records = plan.records
    rows: list[dict[str, Any]] = []
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != RAW_HEADER:
            raise RunError(f"{path}: raw header differs")
        for line_number, raw in enumerate(reader, 2):
            if None in raw or set(raw) != set(RAW_HEADER):
                raise RunError(f"{path}:{line_number}: malformed row")
            parsed = {
                field: parse_decimal(raw[field], f"{path}:{line_number}:{field}")
                for field in RAW_INTEGER_FIELDS
                if field != "record_id"
            }
            parsed["record_id"] = raw["record_id"]
            try:
                parsed["sec"] = float(raw["sec"])
            except ValueError as exc:
                raise RunError(f"{path}:{line_number}: invalid seconds") from exc
            rows.append(parsed)
    if len(rows) != len(expected_records):
        raise RunError(f"{path}: found {len(rows)} rows, expected {len(expected_records)}")

    unit_for_record: dict[str, int] = {}
    unit_key: dict[int, Unit] = {}
    for local_unit, unit in enumerate(plan.units):
        unit_key[local_unit] = unit
        for record in unit.records:
            unit_for_record[record["record_id"]] = local_unit
    normalized: list[dict[str, Any]] = []
    for index, (row, expected) in enumerate(zip(rows, expected_records, strict=True)):
        if row["record_id"] != expected["record_id"] or row["run"] != index:
            raise RunError(f"{path}: output order/key differs at row {index}")
        expected_unit = unit_for_record[expected["record_id"]]
        if row["unit_id"] != expected_unit or row["target_index"] != expected["target_index"]:
            raise RunError(f"{path}: unit/target binding differs for {row['record_id']}")
        scalar = expected_scalar(expected["target_seed"], expected["target_index"])
        stream = expected_walk_stream(expected["walk_seed"], expected["target_index"])
        if row["target_scalar"] != scalar or row["walk_stream_seed"] != stream:
            raise RunError(f"{path}: scalar/walk stream differs for {row['record_id']}")
        identities = (
            (row["setup_ops"], row["setup_adds"] + row["setup_doubles"]),
            (row["walk_ops"], row["walk_adds"] + row["walk_doubles"]),
            (row["ops"], row["adds"] + row["doubles"]),
            (row["ops"], row["setup_ops"] + row["walk_ops"]),
            (row["adds"], row["setup_adds"] + row["walk_adds"]),
            (row["doubles"], row["setup_doubles"] + row["walk_doubles"]),
        )
        if any(actual != wanted for actual, wanted in identities):
            raise RunError(f"{path}: operation identity differs for {row['record_id']}")
        if row["setup_adds"] != 128 or row["setup_doubles"] != 34:
            raise RunError(f"{path}: target setup count differs for {row['record_id']}")
        if (
            row["ok"] != 1
            or row["walk_ops"] <= 0
            or row["walks"] <= 0
            or row["abandoned"] > row["walks"]
            or row["useless"] > row["walks"]
            or row["canon_sign_tests"] != row["canon_calls"]
            or row["canon_negations"] > row["canon_sign_tests"]
            or row["canon_x_squares"] != 0
            or row["canon_y_squares"] != 0
            or not math.isfinite(row["sec"])
            or row["sec"] <= 0
        ):
            raise RunError(f"{path}: correctness/counter gate differs for {row['record_id']}")
        normalized.append(
            {
                **expected,
                "worker": plan.worker,
                "unit_id": expected_unit,
                **{key: value for key, value in row.items() if key not in ("record_id", "unit_id")},
            }
        )

    setup_path = raw_dir / f"worker-{plan.worker}.setups.csv"
    setups: list[dict[str, Any]] = []
    with setup_path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != SETUP_HEADER:
            raise RunError(f"{setup_path}: setup header differs")
        for line_number, raw in enumerate(reader, 2):
            if None in raw or set(raw) != set(SETUP_HEADER):
                raise RunError(f"{setup_path}:{line_number}: malformed setup row")
            row = {
                key: parse_decimal(raw[key], f"{setup_path}:{line_number}:{key}")
                for key in SETUP_HEADER
                if key not in ("setup_fingerprint", "setup_sec")
            }
            fingerprint = raw["setup_fingerprint"]
            if len(fingerprint) != 16 or any(c not in "0123456789abcdef" for c in fingerprint):
                raise RunError(f"{setup_path}:{line_number}: malformed setup fingerprint")
            try:
                setup_sec = float(raw["setup_sec"])
            except ValueError as exc:
                raise RunError(f"{setup_path}:{line_number}: malformed setup seconds") from exc
            row.update({"setup_fingerprint": fingerprint, "setup_sec": setup_sec})
            setups.append(row)
    if len(setups) != len(plan.units):
        raise RunError(f"{setup_path}: found {len(setups)} setup rows, expected {len(plan.units)}")
    for local_unit, (row, unit) in enumerate(zip(setups, plan.units, strict=True)):
        _, b, a2, mode, setup_seed = unit.key
        if (
            row["unit_id"] != local_unit
            or row["b"] != b
            or row["a2"] != a2
            or row["mode"] != mode
            or row["setup_seed"] != setup_seed
            or row["pgen_x"] > FIELD_MASK
            or row["pgen_y"] > FIELD_MASK
            or (row["pgen_x"] == 0 and row["pgen_y"] == 0)
            or not math.isfinite(row["setup_sec"])
            or row["setup_sec"] <= 0
        ):
            raise RunError(f"{setup_path}: native setup certificate differs at unit {local_unit}")
        row["worker"] = plan.worker
        row["curve_id"] = unit.key[0]
    return normalized, setups


def run_setup_robustness_phase(
    *,
    root: Path,
    binary: Path,
    host: dict[str, Any],
    spec: dict[str, Any],
    pairs: list[EndpointPair],
    f271: dict[int, int],
    trigger: dict[str, Any],
    trigger_decision_sha256: str,
    primary_records_sha256: str,
    preflight_plan_sha256: str,
) -> dict[str, Any]:
    phase = root / "setup_robustness"
    durable_mkdir(phase)
    config = spec["setup_robustness"]
    records = build_setup_robustness_plan(pairs, f271, config)
    if canonical_plan_sha256(records) != preflight_plan_sha256:
        raise RunError("setup-robustness plan differs from the pre-primary preflight")
    worker_plans = make_units(
        records,
        int(config["panel_seed"]),
        4,
        list(spec["execution"]["cores"]),
        expected_models=97,
        expected_units=1649,
        expected_records=2176,
    )
    plan_summary = materialize_plan(records, worker_plans, phase)
    raw_dir = phase / "raw"
    durable_mkdir(raw_dir)
    cancel = threading.Event()
    receipts: list[dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(
                worker_command,
                plan,
                phase,
                binary,
                host["taskset"],
                float(spec["execution"]["worker_timeout_seconds"]),
                cancel,
            )
            for plan in worker_plans
        ]
        try:
            for future in concurrent.futures.as_completed(futures):
                receipt = future.result()
                receipts.append(receipt)
                if not receipt["success"]:
                    cancel.set()
        except BaseException:
            cancel.set()
            raise
    if len(receipts) != 4 or any(not receipt["success"] for receipt in receipts):
        raise RunError("one or more setup-robustness workers failed")

    normalized: list[dict[str, Any]] = []
    setups: list[dict[str, Any]] = []
    for worker in worker_plans:
        worker_rows, worker_setups = validate_raw_worker(worker, phase)
        normalized.extend(worker_rows)
        setups.extend(worker_setups)
    normalized.sort(key=lambda row: row["record_id"])
    if len(normalized) != 2176 or len({row["record_id"] for row in normalized}) != 2176:
        raise RunError("setup-robustness normalized record count/key mismatch")
    if len(setups) != 1649:
        raise RunError("setup-robustness native setup invocation count differs")
    all_setup_seeds = [*config["setup_seeds"], config["original_setup_seed"]]
    setup_certificate_audit = validate_robustness_setup_certificates(
        records, setups, all_setup_seeds
    )
    write_csv_exclusive(phase / "records.csv", NORMALIZED_HEADER, normalized)
    setup_fields = ("worker", "curve_id", *SETUP_HEADER)
    write_csv_exclusive(
        phase / "native_setups.csv",
        setup_fields,
        sorted(setups, key=lambda row: (row["worker"], row["unit_id"])),
    )
    if analysis_module is None:
        raise RunError("analysis runtime was not initialized")
    analysis = analysis_module.analyze_setup_robustness(config, normalized, trigger)
    atomic_write_json(phase / "analysis.json", analysis)
    manifest = {
        "schema": "m51-deep-rho-setup-robustness-run/v1",
        "scientific": True,
        "trigger_decision_sha256": trigger_decision_sha256,
        "primary_records_sha256": primary_records_sha256,
        "preflight_plan_sha256": preflight_plan_sha256,
        "records": 2176,
        "fresh_inferential_setup_root_clusters": 16,
        "descriptive_original_root_bridges": 1,
        "total_setup_roots": 17,
        "blocks_per_setup_root": 32,
        "distinct_models": 97,
        "execution_units": 1649,
        "execution_status": "complete",
        "analysis_status": analysis["status"],
        "setup_certificate_audit": setup_certificate_audit,
        "record_plan_sha256": plan_summary["record_plan_sha256"],
        "records_sha256": sha256_file(phase / "records.csv"),
        "native_setups_sha256": sha256_file(phase / "native_setups.csv"),
        "analysis_sha256": sha256_file(phase / "analysis.json"),
        "binary_sha256": sha256_file(binary),
        "worker_receipts": sorted(
            (
                {
                    "worker": receipt["worker"],
                    "sha256": sha256_file(
                        raw_dir / f"worker-{receipt['worker']}.receipt.json"
                    ),
                }
                for receipt in receipts
            ),
            key=lambda row: row["worker"],
        ),
        "finished_utc": utc_now(),
    }
    atomic_write_json(phase / "run_manifest.json", manifest)
    seal_tree(phase)
    return recover_sealed_setup_robustness_summary(
        phase=phase,
        binary=binary,
        trigger_decision_sha256=trigger_decision_sha256,
        primary_records_sha256=primary_records_sha256,
        preflight_plan_sha256=preflight_plan_sha256,
    )


def tree_files(root: Path) -> list[Path]:
    result = []
    for path in root.rglob("*"):
        if path.is_symlink():
            raise RunError(f"symlink forbidden in output tree: {path}")
        if path.is_dir():
            continue
        if not path.is_file() or not stat.S_ISREG(path.stat().st_mode):
            raise RunError(f"non-regular output path: {path}")
        if path != root / "MANIFEST.sha256":
            result.append(path)
    return sorted(result, key=lambda path: path.relative_to(root).as_posix())


def seal_tree(root: Path) -> Path:
    lines = [f"{sha256_file(path)}  {path.relative_to(root).as_posix()}" for path in tree_files(root)]
    atomic_write_text(root / "MANIFEST.sha256", "\n".join(lines) + "\n")
    return root / "MANIFEST.sha256"


def verify_sealed_tree(root: Path) -> tuple[dict[str, str], str]:
    """Verify a tree seal without trusting any pre-seal in-memory state."""
    manifest_path = root / "MANIFEST.sha256"
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise RunError(f"missing regular tree manifest: {manifest_path}")
    content = manifest_path.read_text()
    if not content or not content.endswith("\n"):
        raise RunError(f"empty or unterminated tree manifest: {manifest_path}")
    entries: dict[str, str] = {}
    for line_number, line in enumerate(content.splitlines(), 1):
        pieces = line.split("  ", 1)
        relative = PurePosixPath(pieces[1]) if len(pieces) == 2 else None
        if (
            len(pieces) != 2
            or not valid_sha256(pieces[0])
            or relative is None
            or pieces[1] != relative.as_posix()
            or relative.is_absolute()
            or not relative.parts
            or any(part in ("", ".", "..") for part in relative.parts)
            or pieces[1] in entries
            or pieces[1] == "MANIFEST.sha256"
        ):
            raise RunError(
                f"malformed tree manifest entry: {manifest_path}:{line_number}"
            )
        entries[pieces[1]] = pieces[0]
    actual = {
        path.relative_to(root).as_posix()
        for path in tree_files(root)
    }
    if actual != set(entries):
        raise RunError("sealed tree file set differs from its manifest")
    for name, expected in entries.items():
        if sha256_file(root / name) != expected:
            raise RunError(f"sealed tree hash differs: {name}")
    return entries, hashlib.sha256(content.encode()).hexdigest()


def recover_sealed_setup_robustness_summary(
    *,
    phase: Path,
    binary: Path,
    trigger_decision_sha256: str,
    primary_records_sha256: str,
    preflight_plan_sha256: str,
) -> dict[str, Any]:
    """Reconstruct a completed conditional phase after a post-seal interrupt."""
    _entries, phase_manifest_sha256 = verify_sealed_tree(phase)
    manifest = load_json(phase / "run_manifest.json")
    analysis = load_json(phase / "analysis.json")
    analysis_status = analysis.get("status")
    if (
        manifest.get("schema") != "m51-deep-rho-setup-robustness-run/v1"
        or manifest.get("scientific") is not True
        or manifest.get("trigger_decision_sha256") != trigger_decision_sha256
        or manifest.get("primary_records_sha256") != primary_records_sha256
        or manifest.get("preflight_plan_sha256") != preflight_plan_sha256
        or manifest.get("records") != 2176
        or manifest.get("fresh_inferential_setup_root_clusters") != 16
        or manifest.get("descriptive_original_root_bridges") != 1
        or manifest.get("total_setup_roots") != 17
        or manifest.get("blocks_per_setup_root") != 32
        or manifest.get("distinct_models") != 97
        or manifest.get("execution_units") != 1649
        or manifest.get("execution_status") != "complete"
        or analysis.get("schema")
        != "m51-deep-rho-setup-robustness-analysis/v1"
        or analysis_status not in ("complete", "non_estimable")
        or manifest.get("analysis_status") != analysis_status
        or manifest.get("record_plan_sha256")
        != sha256_file(phase / "record_plan.csv")
        or manifest.get("records_sha256") != sha256_file(phase / "records.csv")
        or manifest.get("native_setups_sha256")
        != sha256_file(phase / "native_setups.csv")
        or manifest.get("analysis_sha256") != sha256_file(phase / "analysis.json")
        or manifest.get("binary_sha256") != sha256_file(binary)
    ):
        raise RunError("sealed setup-robustness phase cannot be recovered")
    return {
        "triggered": True,
        "status": analysis_status,
        "execution_status": "complete",
        "records": 2176,
        "analysis_status": analysis_status,
        "phase_manifest_sha256": phase_manifest_sha256,
        "run_manifest_sha256": sha256_file(phase / "run_manifest.json"),
        "analysis_sha256": sha256_file(phase / "analysis.json"),
    }


def fixture_pairs() -> list[EndpointPair]:
    # Algebraically unclassified fixtures for mock plan-shape testing only.
    representatives: list[int] = []
    seen: set[int] = set()
    candidate = 2
    while len(representatives) < 64:
        values = orbit(candidate)
        representative = min(values)
        if len(values) == 51 and representative not in seen:
            representatives.append(representative)
            seen.add(representative)
        candidate += 1
    return [
        EndpointPair(
            pair_id=index,
            global_index=index,
            parent_b=representatives[2 * index],
            parent_orbit_rep=representatives[2 * index],
            bottom_b=conjugate(
                representatives[2 * index + 1], 1 + index % 50
            ),
            bottom_orbit_rep=representatives[2 * index + 1],
            certificate_sha256="0" * 64,
        )
        for index in range(32)
    ]


def initialize_out(out: Path) -> None:
    if out.exists():
        if out.is_symlink() or not out.is_dir() or any(out.iterdir()):
            raise RunError("output must be absent or an empty regular directory")
    else:
        if not out.parent.is_dir() or out.parent.is_symlink():
            raise RunError("output parent must be an existing regular directory")
        durable_mkdir(out)


def run_mock(args: argparse.Namespace) -> dict[str, Any]:
    out = args.out.resolve(strict=False)
    initialize_out(out)
    spec = load_json(HERE / "spec.json")
    validate_spec(spec)
    schedule = read_schedule(HERE / "schedule.csv")
    if schedule != generate_schedule(spec["seeds"]["schedule_root"]):
        raise RunError("materialized schedule differs from regeneration")
    f271 = read_f271_orbits(HERE / "floor271_orbits.csv")
    records = build_plan(schedule, fixture_pairs(), f271, spec["seeds"])
    workers = make_units(records, spec["seeds"]["schedule_root"], 4, [0, 1, 2, 3])
    summary = {
        "schema": "m51-deep-rho-mock/v1",
        "scientific": False,
        "deep_endpoints_classified": False,
        "rho_executed": False,
        "records_planned": len(records),
        "blocks": len(schedule),
        "distinct_fixture_models": len({record["curve_id"] for record in records}),
        "execution_units": sum(len(worker.units) for worker in workers),
        "worker_loads": [len(worker.records) for worker in workers],
        "git": git_receipt(require_clean=False),
        "created_utc": utc_now(),
    }
    atomic_write_json(out / "MOCK.json", summary)
    seal_tree(out)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return summary


def run_selftest_only(args: argparse.Namespace) -> dict[str, Any]:
    out = args.out.resolve(strict=False)
    initialize_out(out)
    spec = load_json(HERE / "spec.json")
    validate_spec(spec)
    host = host_receipt([0, 1, 2, 3])
    build = build_binaries(HERE, out, host)
    rng_vectors = run_rng_vector_crosscheck(out / "build/rho-batch", out)
    f271 = read_f271_orbits(HERE / "floor271_orbits.csv")
    selftests = run_startup_selftests(
        out / "build/rho-selftest", f271, spec["seeds"]["setup_root"], out
    )
    summary = {
        "schema": "m51-deep-rho-selftest-session/v1",
        "scientific": False,
        "deep_endpoint_rho_executed": False,
        "status": "selftest_complete",
        "build": build,
        "selftests": selftests["count"],
        "rng_vectors": rng_vectors["count"],
        "host": host,
        "git": git_receipt(require_clean=False),
        "finished_utc": utc_now(),
    }
    atomic_write_json(out / "session.json", summary)
    seal_tree(out)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return summary


def run_scientific(args: argparse.Namespace) -> dict[str, Any]:
    analysis = prepare_scientific_python_runtime()
    started = time.monotonic()
    started_utc = utc_now()
    out = args.out.resolve(strict=False)
    if out == REPO.resolve() or REPO.resolve() in out.parents:
        raise RunError("scientific output must be outside the Git worktree")
    frozen = verify_frozen_inputs()
    if (
        LOADED_DESIGN_SHA256 != frozen[0]["design.py"]
        or LOADED_ANALYZE_SHA256 != frozen[0]["analyze.py"]
    ):
        raise RunError("loaded local scientific source differs from FROZEN.sha256")
    git_before = git_receipt(require_clean=True)
    spec = load_json(HERE / "spec.json")
    validate_spec(spec)
    if spec.get("status") not in ("frozen-design-unlaunched", "frozen-design"):
        raise RunError("spec status was not changed to frozen before launch")
    schedule = read_schedule(HERE / "schedule.csv")
    if schedule != generate_schedule(spec["seeds"]["schedule_root"]):
        raise RunError("materialized schedule differs from exact regeneration")
    _selection_document, pairs = load_selection(HERE / "deep_selection.json")
    f271 = read_f271_orbits(HERE / "floor271_orbits.csv")
    records = build_plan(schedule, pairs, f271, spec["seeds"])
    robustness_plan = build_setup_robustness_plan(
        pairs, f271, spec["setup_robustness"]
    )
    robustness_plan_sha256 = canonical_plan_sha256(robustness_plan)
    cores = list(spec["execution"]["cores"])
    # This constructs and validates all 1,649 planned setup units before a
    # primary worker can start, including the false-trigger path.
    robustness_units = make_units(
        robustness_plan,
        int(spec["setup_robustness"]["panel_seed"]),
        4,
        cores,
        expected_models=97,
        expected_units=1649,
        expected_records=2176,
    )
    if sum(len(plan.units) for plan in robustness_units) != 1649:
        raise RunError("setup-robustness preflight unit count differs")
    runtime_receipt = analysis_runtime_receipt()
    host = host_receipt(cores, analysis_runtime=runtime_receipt)

    initialize_out(out)
    session: dict[str, Any] = {
        "schema": "m51-deep-rho-session/v1",
        "scientific": True,
        "status": "starting",
        "started_utc": started_utc,
    }
    atomic_write_json(out / "session.json", session)
    completed_session: dict[str, Any] | None = None
    robustness_failure: BaseException | None = None
    primary_tree_manifest: Path | None = None
    try:
        inputs = copy_snapshot(out, frozen)
        git_after = git_receipt(require_clean=True)
        if git_before != git_after:
            raise RunError("Git snapshot changed while copying frozen inputs")
        analysis.bind_design(inputs / "design.py", frozen[0]["design.py"])
        atomic_write_json(
            out / "provenance.json",
            {
                "git": git_before,
                "host": host,
                "frozen_manifest_sha256": frozen[1],
            },
        )
        preflight = {
            "schema": "m51-deep-rho-setup-robustness-preflight/v1",
            "validated_before_primary_execution": True,
            "canonical_plan_sha256": robustness_plan_sha256,
            "records": 2176,
            "panel_slots_per_arm": 32,
            "distinct_models": 97,
            "execution_units": 1649,
            "fresh_inferential_setup_roots": 16,
            "descriptive_original_root_bridges": 1,
            "total_setup_roots": 17,
        }
        atomic_write_json(out / "setup_robustness_preflight.json", preflight)
        build = build_binaries(inputs, out, host)
        rng_vectors = run_rng_vector_crosscheck(out / "build/rho-batch", out)
        selftests = run_startup_selftests(
            out / "build/rho-selftest", f271, spec["seeds"]["setup_root"], out
        )
        primary = out / "primary"
        durable_mkdir(primary)
        worker_plans = make_units(records, spec["seeds"]["schedule_root"], 4, cores)
        plan_summary = materialize_plan(records, worker_plans, primary)
        raw_dir = primary / "raw"
        durable_mkdir(raw_dir)
        cancel = threading.Event()
        receipts: list[dict[str, Any]] = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [
                executor.submit(
                    worker_command,
                    plan,
                    primary,
                    out / "build/rho-batch",
                    host["taskset"],
                    float(spec["execution"]["worker_timeout_seconds"]),
                    cancel,
                )
                for plan in worker_plans
            ]
            try:
                for future in concurrent.futures.as_completed(futures):
                    receipt = future.result()
                    receipts.append(receipt)
                    if not receipt["success"]:
                        cancel.set()
            except BaseException:
                cancel.set()
                raise
        if len(receipts) != 4 or any(not receipt["success"] for receipt in receipts):
            raise RunError("one or more benchmark workers failed; partial artifacts retained")

        normalized: list[dict[str, Any]] = []
        setups: list[dict[str, Any]] = []
        for worker in worker_plans:
            worker_rows, worker_setups = validate_raw_worker(worker, primary)
            normalized.extend(worker_rows)
            setups.extend(worker_setups)
        normalized.sort(key=lambda row: row["record_id"])
        if len(normalized) != 20480 or len({row["record_id"] for row in normalized}) != 20480:
            raise RunError("normalized record count/key mismatch")
        write_csv_exclusive(primary / "records.csv", NORMALIZED_HEADER, normalized)
        setup_fields = ("worker", "curve_id", *SETUP_HEADER)
        write_csv_exclusive(
            primary / "native_setups.csv",
            setup_fields,
            sorted(setups, key=lambda row: (row["worker"], row["unit_id"])),
        )
        if len(setups) != 3556:
            raise RunError("native setup invocation count differs")
        aa = [row for row in normalized if row["subset"] == "aa"]
        inference = [row for row in normalized if row["subset"] == "inference"]
        if len(inference) != 12288 or len(aa) != 8192:
            raise RunError("normalized subset counts differ")

        primary_trigger_analysis = analysis.analyze_records(spec, normalized)
        atomic_write_json(
            primary / "analysis.json", primary_trigger_analysis
        )
        primary_manifest = {
            "schema": "m51-deep-rho-primary-run/v1",
            "scientific": True,
            "started_utc": started_utc,
            "finished_utc": utc_now(),
            "frozen_manifest_sha256": frozen[1],
            "selection_binding_sha256": sha256_file(inputs / "deep_selection.json"),
            "schedule_sha256": sha256_file(inputs / "schedule.csv"),
            "rho_source_sha256": sha256_file(inputs / "rho.c"),
            "batch_driver_sha256": sha256_file(inputs / "batch_driver.c"),
            "binary_sha256": build["batch_binary_sha256"],
            "record_plan_sha256": plan_summary["record_plan_sha256"],
            "records_sha256": sha256_file(primary / "records.csv"),
            "native_setups_sha256": sha256_file(primary / "native_setups.csv"),
            "analysis_sha256": sha256_file(primary / "analysis.json"),
            "records": 20480,
            "inference_records": 12288,
            "aa_records": 8192,
            "execution_units": 3556,
            "distinct_models": 3537,
            "worker_receipts": sorted(
                (
                    {
                        "worker": receipt["worker"],
                        "sha256": sha256_file(
                            raw_dir / f"worker-{receipt['worker']}.receipt.json"
                        ),
                    }
                    for receipt in receipts
                ),
                key=lambda row: row["worker"],
            ),
        }
        atomic_write_json(primary / "run_manifest.json", primary_manifest)
        # Bind the expected path before sealing so an asynchronous exception
        # after the atomic MANIFEST write cannot erase knowledge of the
        # independently completed primary phase.  The exception path still
        # verifies the on-disk tree before classifying it as complete.
        primary_tree_manifest = primary / "MANIFEST.sha256"
        seal_tree(primary)
        verify_sealed_tree(primary)

        sealed_primary_analysis = load_json(primary / "analysis.json")
        if sealed_primary_analysis != primary_trigger_analysis:
            raise RunError("sealed primary analysis bytes differ from in-memory analysis")
        trigger = analysis.setup_robustness_trigger(
            sealed_primary_analysis, spec["setup_robustness"]
        )
        trigger_decision = {
            "schema": "m51-deep-rho-setup-robustness-decision/v1",
            "created_utc": utc_now(),
            "primary_tree_manifest_sha256": sha256_file(primary_tree_manifest),
            "primary_run_manifest_sha256": sha256_file(primary / "run_manifest.json"),
            "primary_records_sha256": sha256_file(primary / "records.csv"),
            "primary_analysis_sha256": sha256_file(primary / "analysis.json"),
            "preflight_plan_sha256": robustness_plan_sha256,
            "frozen_manifest_sha256": frozen[1],
            **trigger,
        }
        atomic_write_json(out / "setup_robustness_decision.json", trigger_decision)
        trigger_decision_sha256 = sha256_file(
            out / "setup_robustness_decision.json"
        )
        if trigger["triggered"]:
            session.update(phase="setup_robustness")
            replace_json(out / "session.json", session)
            try:
                robustness_summary = run_setup_robustness_phase(
                    root=out,
                    binary=out / "build/rho-batch",
                    host=host,
                    spec=spec,
                    pairs=pairs,
                    f271=f271,
                    trigger=trigger,
                    trigger_decision_sha256=trigger_decision_sha256,
                    primary_records_sha256=sha256_file(primary / "records.csv"),
                    preflight_plan_sha256=robustness_plan_sha256,
                )
            except BaseException as exc:
                try:
                    robustness_summary = recover_sealed_setup_robustness_summary(
                        phase=out / "setup_robustness",
                        binary=out / "build/rho-batch",
                        trigger_decision_sha256=trigger_decision_sha256,
                        primary_records_sha256=sha256_file(primary / "records.csv"),
                        preflight_plan_sha256=robustness_plan_sha256,
                    )
                except BaseException:
                    robustness_failure = exc
                    robustness_summary = {
                        "triggered": True,
                        "status": "failed",
                        "execution_status": "failed",
                        "analysis_status": "not_available",
                        "records": 0,
                        "error": repr(exc),
                        "partial_artifacts_retained": (
                            out / "setup_robustness"
                        ).exists(),
                    }
                else:
                    robustness_summary["post_seal_recovery"] = {
                        "verified_on_disk": True,
                        "interrupted_exception": repr(exc),
                    }
        else:
            robustness_summary = {
                "triggered": False,
                "status": "not_triggered",
                "execution_status": "not_run",
                "analysis_status": "not_run",
                "records": 0,
                "qualifying_contrasts": trigger["qualifying_contrasts"],
            }

        run_manifest = {
            "schema": "m51-deep-rho-run-manifest/v1",
            "study_id": spec["study_id"],
            "scientific": True,
            "started_utc": started_utc,
            "finished_utc": utc_now(),
            "frozen_manifest_sha256": frozen[1],
            "selection_binding_sha256": sha256_file(inputs / "deep_selection.json"),
            "schedule_sha256": sha256_file(inputs / "schedule.csv"),
            "rho_source_sha256": sha256_file(inputs / "rho.c"),
            "batch_driver_sha256": sha256_file(inputs / "batch_driver.c"),
            "binary_sha256": build["batch_binary_sha256"],
            "primary": {
                "tree_manifest_sha256": sha256_file(primary_tree_manifest),
                "run_manifest_sha256": sha256_file(primary / "run_manifest.json"),
                "records_sha256": sha256_file(primary / "records.csv"),
                "analysis_sha256": sha256_file(primary / "analysis.json"),
                "records": 20480,
                "execution_units": 3556,
                "distinct_models": 3537,
            },
            "selftests": selftests["count"],
            "rng_vectors": rng_vectors["count"],
            "setup_robustness_preflight_sha256": sha256_file(
                out / "setup_robustness_preflight.json"
            ),
            "setup_robustness_decision_sha256": trigger_decision_sha256,
            "setup_robustness": robustness_summary,
            "total_records": 20480 + int(robustness_summary["records"]),
            "accounting": spec["accounting"],
            "claim_boundary": spec["claim_boundary"],
        }
        atomic_write_json(out / "run_manifest.json", run_manifest)
        terminal_status = (
            "primary_complete_robustness_failed"
            if robustness_failure is not None
            else "primary_complete_robustness_non_estimable"
            if robustness_summary["analysis_status"] == "non_estimable"
            else "complete"
        )
        terminal_phase = (
            "setup_robustness_failed"
            if robustness_failure is not None
            else "setup_robustness_non_estimable"
            if robustness_summary["analysis_status"] == "non_estimable"
            else "complete"
        )
        session.update(
            status=terminal_status,
            phase=terminal_phase,
            finished_utc=utc_now(),
            elapsed_seconds=time.monotonic() - started,
            records=20480,
            total_records=20480 + int(robustness_summary["records"]),
            setup_robustness_triggered=bool(robustness_summary["triggered"]),
            execution_units=(
                5205
                if robustness_summary["execution_status"] == "complete"
                else 3556
            ),
            manifest="MANIFEST.sha256",
            run_manifest_sha256=sha256_file(out / "run_manifest.json"),
        )
        replace_json(out / "session.json", session)
        seal_tree(out)
        completed_session = dict(session)
    except BaseException as exc:
        if (out / "MANIFEST.sha256").exists():
            raise RunError("refusing to mutate a terminally sealed run") from exc
        primary_sealed = False
        primary_candidate = out / "primary"
        if (primary_candidate / "MANIFEST.sha256").is_file():
            try:
                verify_sealed_tree(primary_candidate)
            except BaseException:
                primary_sealed = False
            else:
                primary_tree_manifest = primary_candidate / "MANIFEST.sha256"
                primary_sealed = True
        session.update(
            status=(
                "primary_complete_postprimary_failed"
                if primary_sealed
                else "invalid"
            ),
            phase=session.get("phase", "unknown"),
            failed_utc=utc_now(),
            elapsed_seconds=time.monotonic() - started,
            error=repr(exc),
        )
        try:
            replace_json(out / "session.json", session)
        except BaseException:
            pass
        raise
    if completed_session is None:
        raise RunError("scientific run ended without a completed session")
    print(json.dumps(completed_session, indent=2, sort_keys=True))
    if robustness_failure is not None:
        raise RunError(
            "primary phase is sealed, but the mandatory setup-robustness lane failed"
        ) from robustness_failure
    return completed_session


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--mock", action="store_true")
    modes.add_argument("--selftest-only", action="store_true")
    args = parser.parse_args()
    if args.mock:
        run_mock(args)
    elif args.selftest_only:
        run_selftest_only(args)
    else:
        run_scientific(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
