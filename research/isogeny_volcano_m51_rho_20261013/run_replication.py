#!/usr/bin/env python3
"""Execute and normalize the frozen m=51 volcano-level rho design.

This runner is deliberately fail-closed and has no resume mode.  A launch
must use a new or empty output directory.  Core outputs are first written to
``*.partial`` files, validated against the independently reimplemented target
and walk-stream derivations, and only then renamed into the immutable raw
tree.  The final ``records.csv`` and ``certificates.json`` are the inputs
consumed by ``analyze.py``.

The ``--selftest-only`` path builds the frozen source and emits all required
startup certificates, but does not execute any rho solve.  It is intended for
pre-launch harness validation and is not a scientific run.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import platform
import random
import signal
import shlex
import shutil
import subprocess
import sys
import threading
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
UINT64_MASK = (1 << 64) - 1

ARM_IDS = (
    "crater-neg",
    "crater-tau51",
    "crater-tau17",
    "floor-neg",
    "floor-tau17",
)
ARM_MODE = {
    "crater-neg": 0,
    "crater-tau51": 1,
    "crater-tau17": 2,
    "floor-neg": 0,
    "floor-tau17": 2,
}
RAW_HEADER = (
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
NORMALIZED_HEADER = (
    "block_id",
    "replicate",
    "arm",
    "curve_id",
    "orbit_id",
    "b",
    "a2",
    "mode",
    "setup_seed",
    "target_seed",
    "walk_seed",
    "run",
    "target_index",
    "k",
    "walk_stream_seed",
    *RAW_HEADER[4:],
)
COMPILE_FLAGS = (
    "-std=gnu11",
    "-O2",
    "-Wall",
    "-Wextra",
    "-Wconversion",
    "-Wshadow",
    "-mpclmul",
    "-msse4.1",
)
SELFTEST_TIMEOUT_SECONDS = 300
BUILD_TIMEOUT_SECONDS = 120
EXPECTED_SETUP_ADDS = 128
EXPECTED_SETUP_DOUBLES = 34
FROZEN_FILES = (
    "PROTOCOL.md",
    "TRACE_ZERO_LANE.md",
    "spec.json",
    "sample.csv",
    "rho.c",
    "params.h",
    "run_replication.py",
    "analyze.py",
    "plot.py",
)


@dataclass(frozen=True)
class Sample:
    curve_id: str
    level: str
    orbit_id: int | None
    b: int
    a2: int
    orbit_size: int
    f_E: int
    source_status: str


@dataclass(frozen=True)
class Job:
    replicate: str
    arm: str
    curve_id: str
    orbit_id: int | None
    b: int
    a2: int
    mode: int
    target_start: int
    targets: int
    setup_seed: int
    target_seed: int
    walk_seed: int

    @property
    def filename(self) -> str:
        label = "primary" if self.replicate == "primary" else "aa-b"
        return f"{label}_b{self.target_start:04d}_{self.arm}.csv"

    @property
    def key(self) -> tuple[str, int, str]:
        return self.replicate, self.target_start, self.arm


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def durable_replace(source: Path, target: Path) -> None:
    os.replace(source, target)
    fsync_directory(target.parent)


def durable_mkdir(path: Path, *, parents: bool = False) -> None:
    path.mkdir(parents=parents)
    fsync_directory(path.parent)


def fsync_file(path: Path) -> None:
    with path.open("rb") as handle:
        os.fsync(handle.fileno())


def append_text_durable(path: Path, value: str) -> None:
    created = not path.exists()
    with path.open("a") as handle:
        handle.write(value)
        handle.flush()
        os.fsync(handle.fileno())
    if created:
        fsync_directory(path.parent)


def append_jsonl_durable(path: Path, value: Any) -> None:
    append_text_durable(path, json.dumps(value, sort_keys=True) + "\n")


def atomic_write_text(path: Path, value: str) -> None:
    """Write a small provenance artifact without exposing a final partial."""
    if path.exists():
        raise FileExistsError(f"refusing to overwrite {path}")
    partial = path.with_name(path.name + ".partial")
    if partial.exists():
        raise FileExistsError(f"refusing pre-existing partial {partial}")
    with partial.open("x") as handle:
        handle.write(value)
        handle.flush()
        os.fsync(handle.fileno())
    durable_replace(partial, path)


def replace_json(path: Path, value: Any) -> None:
    """Atomically create or replace mutable session state."""
    partial = path.with_name(path.name + ".partial")
    if partial.exists():
        raise FileExistsError(f"refusing pre-existing partial {partial}")
    with partial.open("x") as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    durable_replace(partial, path)


def command_output(argv: list[str], *, cwd: Path | None = None) -> str:
    process = subprocess.run(argv, cwd=cwd, check=True, text=True, capture_output=True)
    if process.stderr:
        raise RuntimeError(f"unexpected stderr from {argv!r}: {process.stderr[-1000:]}")
    return process.stdout.strip()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return value


def parse_uint64_decimal(value: Any, context: str) -> int:
    if not isinstance(value, str) or not value or not value.isascii() or not value.isdecimal():
        raise ValueError(f"{context}: expected an unsigned decimal integer")
    parsed = int(value, 10)
    if parsed > UINT64_MASK:
        raise ValueError(f"{context}: integer exceeds uint64")
    return parsed


def read_samples(path: Path) -> tuple[dict[str, Sample], list[str]]:
    expected_header = (
        "curve_id",
        "level",
        "orbit_id",
        "b",
        "a2",
        "orbit_size",
        "f_E",
        "source_status",
    )
    samples: dict[str, Sample] = {}
    floor_ids: list[str] = []
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != expected_header:
            raise ValueError(f"{path}: sample schema differs from the frozen schema")
        for line_number, raw in enumerate(reader, 2):
            if None in raw:
                raise ValueError(f"{path}:{line_number}: trailing sample fields")
            try:
                orbit_id = int(raw["orbit_id"]) if raw["orbit_id"] else None
                sample = Sample(
                    curve_id=raw["curve_id"],
                    level=raw["level"],
                    orbit_id=orbit_id,
                    b=int(raw["b"]),
                    a2=int(raw["a2"]),
                    orbit_size=int(raw["orbit_size"]),
                    f_E=int(raw["f_E"]),
                    source_status=raw["source_status"],
                )
            except (KeyError, ValueError) as exc:
                raise ValueError(f"{path}:{line_number}: malformed sample row") from exc
            for field, value in (
                ("orbit_id", sample.orbit_id),
                ("b", sample.b),
                ("a2", sample.a2),
                ("orbit_size", sample.orbit_size),
                ("f_E", sample.f_E),
            ):
                if value is not None and not 0 <= value <= UINT64_MASK:
                    raise ValueError(f"{path}:{line_number}: {field} is outside uint64")
            if sample.curve_id in samples:
                raise ValueError(f"{path}: duplicate curve_id {sample.curve_id}")
            samples[sample.curve_id] = sample
            if sample.level == "floor-271":
                floor_ids.append(sample.curve_id)

    expected_ids = {"m51-crater", *(f"m51-floor-o{i:02d}" for i in range(1, 17))}
    if set(samples) != expected_ids:
        raise ValueError("sample.csv does not contain the exact frozen 17 curve IDs")
    crater = samples["m51-crater"]
    if (
        crater.level != "crater"
        or crater.orbit_id is not None
        or crater.b != 1
        or crater.a2 != 0
        or crater.orbit_size != 1
        or crater.f_E != 1
        or crater.source_status != "koblitz_crater"
    ):
        raise ValueError("sample.csv crater metadata differs from the frozen crater")
    floor_ids.sort(key=lambda curve_id: samples[curve_id].orbit_id or 0)
    expected_representatives = (
        623162416261,
        25640824825979,
        30885819784827,
        57318330399736,
        67694307705004,
        72881269935803,
        115635957935040,
        116461223646592,
        116511665573478,
        121360481466206,
        130246110195364,
        147686731444433,
        213718369432541,
        237711860122495,
        360860333097189,
        370376419722289,
    )
    for orbit_id, (curve_id, representative) in enumerate(
        zip(floor_ids, expected_representatives), 1
    ):
        sample = samples[curve_id]
        if (
            sample.level != "floor-271"
            or sample.orbit_id != orbit_id
            or sample.b != representative
            or sample.a2 != 0
            or sample.orbit_size != 17
            or sample.f_E != 271
            or sample.source_status != "cm_floor_set_kernel_check_40of40_14of16_orbits"
        ):
            raise ValueError(f"sample.csv frozen floor metadata mismatch for orbit {orbit_id}")
    return samples, floor_ids


def validate_spec(spec: dict[str, Any]) -> None:
    if spec.get("schema") != "m51-volcano-rho-study/v1":
        raise ValueError("unexpected spec schema")
    design = spec.get("design", {})
    exact_design = {
        "primary_target_blocks": 4096,
        "floor_orbits": 16,
        "blocks_per_floor_orbit": 256,
        "blocks_per_job": 64,
        "primary_records": 20480,
        "inferential_target_blocks": 3072,
        "inferential_blocks_per_floor_orbit": 192,
        "inferential_subset": "within_orbit_offset in [64,255]",
        "inferential_records": 15360,
        "aa_blocks_per_orbit": 64,
        "aa_target_blocks": 1024,
        "aa_subset": "within_orbit_offset in [0,63]",
        "aa_holdout_for_inference": True,
        "aa_extra_records": 5120,
        "total_records": 25600,
        "max_workers": 4,
        "timeout_seconds_per_job": 1800,
        "replacement_of_failed_records": False,
    }
    for field, expected in exact_design.items():
        if design.get(field) != expected:
            raise ValueError(f"spec design {field}={design.get(field)!r}, expected {expected!r}")
    expected_seeds = {
        "target_root": 202610135101,
        "setup_root": 202610135102,
        "walk_primary_root": 202610135103,
        "walk_aa_root": 202610135104,
        "schedule_root": 202610135105,
        "bootstrap_root": 202610135106,
    }
    if spec.get("seeds") != expected_seeds:
        raise ValueError("spec seed namespaces differ from the frozen design")
    expected_compile = " ".join(["gcc", *COMPILE_FLAGS, "-o", "rho", "rho.c"])
    execution_requirements = spec.get("execution_requirements", {})
    if execution_requirements.get("compile") != expected_compile:
        raise ValueError("spec compile command differs from the implemented frozen build")
    exact_execution_gates = {
        "build_timeout_seconds": BUILD_TIMEOUT_SECONDS,
        "receipt_elapsed_tolerance_seconds": 2.0,
        "frozen_manifest": "FROZEN.sha256",
        "atomic_partial_completion_required": True,
        "unsafe_resume_permitted": False,
        "stop_all_workers_on_failure_or_interrupt": True,
    }
    for field, expected in exact_execution_gates.items():
        if execution_requirements.get(field) != expected:
            raise ValueError(f"spec execution requirement {field} differs from the runner")
    expected_distribution_metrics = [
        "walk_ops",
        "walk_adds",
        "walk_doubles",
        "setup_ops",
        "setup_adds",
        "setup_doubles",
        "ops",
        "adds",
        "doubles",
        "canon_calls",
        "canon_x_squares",
        "canon_y_squares",
        "canon_sign_tests",
        "canon_negations",
        "walks",
        "cycles",
        "abandoned",
        "useless",
        "sec",
    ]
    if spec.get("accounting", {}).get("distribution_summary_metrics") != expected_distribution_metrics:
        raise ValueError("spec distribution summary metrics differ from the frozen analyzer contract")
    family = spec.get("curve_family", {})
    exact_family = {
        "field_degree": 51,
        "field_reduction_mask_hex": "0x4b",
        "a2": 0,
        "ambient_order": 2251799852369764,
        "subgroup_order": 17192986687,
        "cofactor": 130972,
        "D_K": -7,
        "f_pi": 32756041,
    }
    for field, expected in exact_family.items():
        if family.get(field) != expected:
            raise ValueError(f"spec curve_family {field} differs from the frozen value")
    arm_documents = spec.get("arms")
    if not isinstance(arm_documents, list):
        raise ValueError("spec arms must be a list")
    if [(arm.get("id"), arm.get("mode")) for arm in arm_documents] != [
        (arm, ARM_MODE[arm]) for arm in ARM_IDS
    ]:
        raise ValueError("spec arm order or core modes differ from the frozen runner")
    normalized = spec.get("normalized_record_schema")
    if not isinstance(normalized, list) or len(normalized) != len(set(normalized)):
        raise ValueError("spec normalized_record_schema is missing or has duplicates")
    if tuple(normalized) != NORMALIZED_HEADER:
        raise ValueError("spec normalized_record_schema differs from runner output fields/order")
    certificate_schema = spec.get("normalized_certificate_schema", {})
    if (
        certificate_schema.get("file") != "certificates.json"
        or certificate_schema.get("schema") != "m51-rho-certificates/v1"
        or certificate_schema.get("top_level_fields")
        != [
            "schema",
            "created_utc",
            "rho_source_sha256",
            "params_source_sha256",
            "binary_sha256",
            "entries",
        ]
        or certificate_schema.get("fields")
        != [
            "curve_id",
            "selftest_ok",
            "b",
            "a2",
            "mode",
            "action_step",
            "action_order",
            "setup_seed",
            "pgen_x",
            "pgen_y",
            "setup_fingerprint",
        ]
    ):
        raise ValueError("spec certificate schema differs from runner output")
    manifest_schema = spec.get("normalized_run_manifest_schema", {})
    if (
        manifest_schema.get("file") != "run_manifest.json"
        or manifest_schema.get("schema") != "m51-rho-run-manifest/v1"
        or manifest_schema.get("top_level_fields")
        != [
            "schema",
            "study_id",
            "status",
            "created_utc",
            "inputs",
            "build",
            "parameters",
            "execution",
        ]
        or manifest_schema.get("required_sections")
        != ["inputs", "build", "parameters", "execution"]
        or manifest_schema.get("inputs_fields")
        != [
            "rho_source_sha256",
            "params_source_sha256",
            "runner_source_sha256",
            "analyzer_source_sha256",
            "plot_source_sha256",
            "protocol_sha256",
            "trace_zero_lane_sha256",
            "frozen_manifest_sha256",
            "spec_sha256",
            "sample_sha256",
            "records_sha256",
            "certificates_sha256",
        ]
        or manifest_schema.get("build_fields")
        != [
            "command",
            "actual_command",
            "binary_sha256",
            "compiler_version",
            "cpu_features",
            "git_commit",
            "git_dirty",
            "host",
            "cpu_affinity",
        ]
        or manifest_schema.get("parameter_fields")
        != [
            "field_degree",
            "field_reduction_mask",
            "field_polynomial",
            "subgroup_order",
            "cofactor",
            "ambient_order",
            "a2",
        ]
        or manifest_schema.get("execution_fields")
        != [
            "records",
            "primary_blocks",
            "aa_blocks",
            "jobs_planned",
            "jobs_completed",
            "blocks_per_job",
            "max_workers",
            "workers_used",
            "cores",
            "timeout_seconds_per_job",
            "schedule_root",
            "replacement_records",
            "failed_jobs",
            "timed_out_jobs",
            "missing_jobs",
            "extra_jobs",
            "job_order",
            "job_receipts_sha256",
            "plan_sha256",
        ]
    ):
        raise ValueError("spec run-manifest schema differs from runner output")


def read_frozen_manifest(base: Path = HERE) -> tuple[dict[str, str], str]:
    path = base / "FROZEN.sha256"
    try:
        content = path.read_text()
    except OSError as exc:
        raise ValueError(f"missing frozen-input manifest {path}") from exc
    if not content or not content.endswith("\n"):
        raise ValueError(f"{path}: frozen-input manifest must be nonempty and newline-terminated")
    entries: dict[str, str] = {}
    for line_number, line in enumerate(content.splitlines(), 1):
        pieces = line.split("  ", 1)
        if (
            len(pieces) != 2
            or len(pieces[0]) != 64
            or any(character not in "0123456789abcdef" for character in pieces[0])
            or Path(pieces[1]).name != pieces[1]
            or pieces[1] in entries
        ):
            raise ValueError(f"{path}:{line_number}: malformed frozen-input entry")
        entries[pieces[1]] = pieces[0]
    if set(entries) != set(FROZEN_FILES):
        raise ValueError(
            f"{path}: frozen file set mismatch; missing={sorted(set(FROZEN_FILES)-set(entries))}, "
            f"extra={sorted(set(entries)-set(FROZEN_FILES))}"
        )
    if list(entries) != sorted(FROZEN_FILES):
        raise ValueError(f"{path}: frozen-input entries are not in canonical sorted order")
    return entries, hashlib.sha256(content.encode()).hexdigest()


def verify_frozen_inputs(spec: dict[str, Any]) -> tuple[dict[str, str], str]:
    entries, manifest_sha256 = read_frozen_manifest()
    for name, expected in entries.items():
        path = HERE / name
        actual = sha256_file(path)
        if actual != expected:
            raise ValueError(f"{path}: sha256={actual}, frozen={expected}")
    provenance = spec["provenance"]
    for field, name in (
        ("rho_source_sha256", "rho.c"),
        ("params_source_sha256", "params.h"),
    ):
        if provenance[field] != entries[name]:
            raise ValueError(f"spec provenance {field} differs from FROZEN.sha256")
    return entries, manifest_sha256


def snapshot_inputs(
    out: Path,
    frozen: tuple[dict[str, str], str] | None = None,
) -> dict[str, Any]:
    entries, frozen_manifest_sha256 = frozen or read_frozen_manifest()
    inputs = out / "inputs"
    durable_mkdir(inputs)
    receipts: dict[str, Any] = {}
    for name in (*FROZEN_FILES, "FROZEN.sha256"):
        source = HERE / name
        target = inputs / name
        partial = target.with_name(target.name + ".partial")
        expected = entries.get(name, frozen_manifest_sha256)
        if sha256_file(source) != expected:
            raise RuntimeError(f"input changed before snapshot copy: {source}")
        with source.open("rb") as src, partial.open("xb") as dst:
            shutil.copyfileobj(src, dst)
            dst.flush()
            os.fsync(dst.fileno())
        if sha256_file(partial) != expected or sha256_file(source) != expected:
            raise RuntimeError(f"input snapshot hash mismatch for {source}")
        durable_replace(partial, target)
        receipts[name] = {
            "source_path": str(source),
            "snapshot_path": str(target),
            "sha256": sha256_file(target),
            "bytes": target.stat().st_size,
        }
    if read_frozen_manifest() != (entries, frozen_manifest_sha256):
        raise RuntimeError("frozen inputs changed during snapshot construction")
    return receipts


def mix64(value: int) -> int:
    value &= UINT64_MASK
    value = ((value ^ (value >> 30)) * 0xBF58476D1CE4E5B9) & UINT64_MASK
    value = ((value ^ (value >> 27)) * 0x94D049BB133111EB) & UINT64_MASK
    return (value ^ (value >> 31)) & UINT64_MASK


def indexed_word(seed: int, index: int, domain: int, attempt: int) -> int:
    return mix64(
        seed
        ^ domain
        ^ mix64((index + 0x9E3779B97F4A7C15) & UINT64_MASK)
        ^ mix64((attempt + 0xD1B54A32D192ED03) & UINT64_MASK)
    )


def indexed_bounded(seed: int, index: int, domain: int, bound: int) -> int:
    if not 0 < bound <= 1 << 64:
        raise ValueError("invalid indexed RNG bound")
    threshold = ((-bound) & UINT64_MASK) % bound
    attempt = 0
    while True:
        value = indexed_word(seed, index, domain, attempt)
        if value >= threshold:
            return value % bound
        attempt += 1
        if attempt > UINT64_MASK:
            raise RuntimeError("indexed RNG rejection loop exhausted")


def expected_scalar(seed: int, index: int, subgroup_order: int) -> int:
    return 1 + indexed_bounded(seed, index, 0x5441524745544B31, subgroup_order - 1)


def expected_walk_stream(seed: int, index: int) -> int:
    return indexed_word(seed, index, 0x57414C4B53545231, 0)


def make_jobs(spec: dict[str, Any], samples: dict[str, Sample]) -> list[Job]:
    design = spec["design"]
    seeds = spec["seeds"]
    size = int(design["blocks_per_job"])
    jobs: list[Job] = []
    for target_start in range(0, int(design["primary_target_blocks"]), size):
        orbit_id = 1 + target_start // int(design["blocks_per_floor_orbit"])
        for arm in ARM_IDS:
            curve_id = "m51-crater" if arm.startswith("crater-") else f"m51-floor-o{orbit_id:02d}"
            sample = samples[curve_id]
            jobs.append(
                Job(
                    replicate="primary",
                    arm=arm,
                    curve_id=curve_id,
                    orbit_id=sample.orbit_id,
                    b=sample.b,
                    a2=sample.a2,
                    mode=ARM_MODE[arm],
                    target_start=target_start,
                    targets=size,
                    setup_seed=int(seeds["setup_root"]),
                    target_seed=int(seeds["target_root"]),
                    walk_seed=int(seeds["walk_primary_root"]),
                )
            )
    for orbit_id in range(1, int(design["floor_orbits"]) + 1):
        target_start = (orbit_id - 1) * int(design["blocks_per_floor_orbit"])
        for arm in ARM_IDS:
            curve_id = "m51-crater" if arm.startswith("crater-") else f"m51-floor-o{orbit_id:02d}"
            sample = samples[curve_id]
            jobs.append(
                Job(
                    replicate="aa-b",
                    arm=arm,
                    curve_id=curve_id,
                    orbit_id=sample.orbit_id,
                    b=sample.b,
                    a2=sample.a2,
                    mode=ARM_MODE[arm],
                    target_start=target_start,
                    targets=size,
                    setup_seed=int(seeds["setup_root"]),
                    target_seed=int(seeds["target_root"]),
                    walk_seed=int(seeds["walk_aa_root"]),
                )
            )

    expected_jobs = (int(design["primary_records"]) + int(design["aa_extra_records"])) // size
    if len(jobs) != expected_jobs or sum(job.targets for job in jobs) != int(design["total_records"]):
        raise ValueError("internal job/solve total differs from frozen design")
    if len({job.key for job in jobs}) != len(jobs) or len({job.filename for job in jobs}) != len(jobs):
        raise ValueError("internal duplicate job key or filename")
    primary_starts = range(0, int(design["primary_target_blocks"]), size)
    for target_start in primary_starts:
        block_jobs = [job for job in jobs if job.replicate == "primary" and job.target_start == target_start]
        if [job.arm for job in block_jobs] != list(ARM_IDS):
            raise ValueError(f"primary five-arm block is incomplete at {target_start}")
        if len({(job.setup_seed, job.target_seed, job.walk_seed) for job in block_jobs}) != 1:
            raise ValueError(f"primary five-arm seed pairing failed at {target_start}")
    return jobs


def selftest_pairs(samples: dict[str, Sample], floor_ids: list[str]) -> list[tuple[str, int]]:
    return [
        ("m51-crater", 0),
        ("m51-crater", 1),
        ("m51-crater", 2),
        *((curve_id, mode) for curve_id in floor_ids for mode in (0, 2)),
    ]


def host_receipt(cores: list[int]) -> dict[str, Any]:
    cpuinfo = Path("/proc/cpuinfo").read_text()
    model = None
    flags: set[str] = set()
    for line in cpuinfo.splitlines():
        if model is None and line.startswith("model name"):
            model = line.split(":", 1)[1].strip()
        if line.startswith("flags"):
            flags.update(line.split(":", 1)[1].split())
    required = {"pclmulqdq", "sse4_1"}
    if not required.issubset(flags):
        raise RuntimeError(f"host lacks required CPU flags: {sorted(required - flags)}")
    return {
        "created_utc": utc_now(),
        "platform": platform.platform(),
        "uname": platform.uname()._asdict(),
        "python": sys.version,
        "python_executable": sys.executable,
        "logical_cpus": os.cpu_count(),
        "process_affinity": sorted(os.sched_getaffinity(0)),
        "selected_cores": cores,
        "cpu_model": model,
        "cpu_flags": sorted(flags),
        "required_cpu_flags": sorted(required),
        "taskset": shutil.which("taskset"),
        "gcc": shutil.which("gcc"),
    }


def git_receipt() -> dict[str, Any]:
    commit = command_output(["git", "rev-parse", "HEAD"], cwd=REPO)
    status = command_output(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"], cwd=REPO
    )
    if status:
        raise RuntimeError(
            "refusing scientific execution from a dirty worktree; commit the frozen harness first"
        )
    return {"commit": commit, "status_porcelain": status, "worktree_clean": True}


def run_process(
    command: list[str],
    *,
    cwd: Path | None = None,
    timeout: int | None = None,
    cancel: threading.Event | None = None,
) -> dict[str, Any]:
    started_utc = utc_now()
    start = time.monotonic()
    process = subprocess.Popen(
        command,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
    )
    deadline = start + timeout if timeout is not None else None
    timed_out = False
    cancelled = False

    def terminate() -> None:
        if process.poll() is not None:
            return
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            return
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait()

    try:
        while True:
            if process.poll() is not None:
                stdout, stderr = process.communicate()
                break
            if cancel is not None and cancel.is_set():
                cancelled = True
                terminate()
                stdout, stderr = process.communicate()
                break
            if deadline is not None and time.monotonic() >= deadline:
                timed_out = True
                terminate()
                stdout, stderr = process.communicate()
                break
            wait = 0.1
            if deadline is not None:
                wait = max(0.001, min(wait, deadline - time.monotonic()))
            try:
                stdout, stderr = process.communicate(timeout=wait)
                break
            except subprocess.TimeoutExpired:
                continue
    except BaseException:
        terminate()
        process.communicate()
        raise
    return {
        "command": command,
        "cwd": str(cwd) if cwd else None,
        "started_utc": started_utc,
        "finished_utc": utc_now(),
        "elapsed_sec": time.monotonic() - start,
        "exit_status": process.returncode,
        "timed_out": timed_out,
        "cancelled": cancelled,
        "stdout": stdout,
        "stderr": stderr,
    }


def build_binary(out: Path, snapshots: dict[str, Any]) -> tuple[Path, dict[str, Any]]:
    build_dir = out / "build"
    durable_mkdir(build_dir)
    binary = build_dir / "rho"
    partial = binary.with_name(binary.name + ".partial")
    source = Path(snapshots["rho.c"]["snapshot_path"])
    command = ["gcc", *COMPILE_FLAGS, "-o", str(partial), source.name]
    receipt = run_process(command, cwd=source.parent, timeout=BUILD_TIMEOUT_SECONDS)
    atomic_write_text(build_dir / "gcc.stdout.log", str(receipt["stdout"]))
    atomic_write_text(build_dir / "gcc.stderr.log", str(receipt["stderr"]))
    if receipt["timed_out"] or receipt["cancelled"] or receipt["exit_status"] != 0:
        replace_json(build_dir / "build-receipt.json", receipt)
        raise RuntimeError(f"gcc failed with exit status {receipt['exit_status']}")
    if receipt["stderr"]:
        replace_json(build_dir / "build-receipt.json", receipt)
        raise RuntimeError("warning-clean frozen build emitted stderr")
    if not partial.is_file():
        raise RuntimeError("gcc reported success without creating the binary")
    fsync_file(partial)
    durable_replace(partial, binary)
    receipt.update(
        {
            "logical_frozen_command": ["gcc", *COMPILE_FLAGS, "-o", "rho", "rho.c"],
            "compiler_version": command_output(["gcc", "--version"]).splitlines(),
            "source_sha256": sha256_file(source),
            "params_sha256": sha256_file(source.parent / "params.h"),
            "binary": str(binary),
            "binary_sha256": sha256_file(binary),
        }
    )
    expected_receipt_fields = {
        "command",
        "cwd",
        "started_utc",
        "finished_utc",
        "elapsed_sec",
        "exit_status",
        "timed_out",
        "cancelled",
        "stdout",
        "stderr",
        "logical_frozen_command",
        "compiler_version",
        "source_sha256",
        "params_sha256",
        "binary",
        "binary_sha256",
    }
    if set(receipt) != expected_receipt_fields:
        raise RuntimeError("successful build receipt schema drifted")
    replace_json(build_dir / "build-receipt.json", receipt)
    return binary, receipt


def parse_selftest_line(line: str, curve_id: str) -> dict[str, Any]:
    tokens = line.strip().split()
    values: dict[str, str] = {}
    for token in tokens:
        if token.count("=") != 1:
            raise ValueError(f"malformed selftest token {token!r}")
        key, value = token.split("=", 1)
        if key in values:
            raise ValueError(f"duplicate selftest field {key}")
        values[key] = value
    expected = {
        "selftest_ok",
        "b",
        "a2",
        "mode",
        "action_step",
        "action_order",
        "setup_seed",
        "pgen_x",
        "pgen_y",
        "setup_fingerprint",
    }
    if set(values) != expected:
        raise ValueError(
            f"selftest fields differ; missing={sorted(expected - set(values))}, "
            f"extra={sorted(set(values) - expected)}"
        )
    entry: dict[str, Any] = {"curve_id": curve_id}
    for field in expected - {"setup_fingerprint"}:
        entry[field] = parse_uint64_decimal(values[field], f"selftest {field}")
    fingerprint = values["setup_fingerprint"]
    if len(fingerprint) != 16 or any(ch not in "0123456789abcdef" for ch in fingerprint):
        raise ValueError("selftest fingerprint is not 16 lowercase hexadecimal digits")
    entry["setup_fingerprint"] = fingerprint
    return entry


def run_selftests(
    out: Path,
    binary: Path,
    samples: dict[str, Sample],
    floor_ids: list[str],
    setup_seed: int,
    core: int,
) -> tuple[Path, dict[str, Any]]:
    receipts_path = out / "selftests.jsonl"
    entries: list[dict[str, Any]] = []
    expected_action = {0: (0, 1), 1: (1, 51), 2: (17, 3)}
    for curve_id, mode in selftest_pairs(samples, floor_ids):
        sample = samples[curve_id]
        command = [
            "taskset",
            "-c",
            str(core),
            str(binary),
            "selftest",
            str(sample.b),
            str(sample.a2),
            str(mode),
            str(setup_seed),
        ]
        receipt = run_process(command, timeout=SELFTEST_TIMEOUT_SECONDS)
        receipt.update({"curve_id": curve_id, "mode": mode, "core": core})
        try:
            if (
                receipt["timed_out"]
                or receipt["cancelled"]
                or receipt["exit_status"] != 0
                or receipt["stderr"]
            ):
                raise RuntimeError(f"selftest process failed for {curve_id}, mode {mode}")
            lines = str(receipt["stdout"]).splitlines()
            if len(lines) != 1:
                raise ValueError(
                    f"selftest emitted {len(lines)} lines for {curve_id}, mode {mode}"
                )
            entry = parse_selftest_line(lines[0], curve_id)
            step, order = expected_action[mode]
            exact = {
                "selftest_ok": 1,
                "b": sample.b,
                "a2": sample.a2,
                "mode": mode,
                "action_step": step,
                "action_order": order,
                "setup_seed": setup_seed,
            }
            if any(entry[field] != expected for field, expected in exact.items()):
                raise ValueError(f"selftest certificate mismatch for {curve_id}, mode {mode}")
            if not (0 < entry["pgen_x"] < (1 << 51)) or not (
                0 <= entry["pgen_y"] < (1 << 51)
            ):
                raise ValueError(f"selftest subgroup basis encoding is out of range for {curve_id}")
        except BaseException as exc:
            receipt["status"] = "failed"
            receipt["validation_error"] = repr(exc)
            append_jsonl_durable(receipts_path, receipt)
            raise
        receipt["status"] = "completed"
        receipt["certificate"] = entry
        expected_receipt_fields = {
            "command",
            "cwd",
            "started_utc",
            "finished_utc",
            "elapsed_sec",
            "exit_status",
            "timed_out",
            "cancelled",
            "stdout",
            "stderr",
            "curve_id",
            "mode",
            "core",
            "status",
            "certificate",
        }
        if set(receipt) != expected_receipt_fields or receipt["cwd"] is not None:
            raise RuntimeError("successful selftest receipt schema or cwd drifted")
        append_jsonl_durable(receipts_path, receipt)
        entries.append(entry)

    by_curve: dict[str, set[tuple[int, int, str]]] = {}
    for entry in entries:
        state = (entry["pgen_x"], entry["pgen_y"], entry["setup_fingerprint"])
        by_curve.setdefault(entry["curve_id"], set()).add(state)
    unequal = sorted(curve_id for curve_id, states in by_curve.items() if len(states) != 1)
    if unequal:
        raise ValueError(f"mode-dependent setup state for curves {unequal}")
    if len(entries) != 35:
        raise ValueError(f"selftest certificate count {len(entries)}, expected 35")

    document = {
        "schema": "m51-rho-certificates/v1",
        "created_utc": utc_now(),
        "rho_source_sha256": sha256_file(out / "inputs" / "rho.c"),
        "params_source_sha256": sha256_file(out / "inputs" / "params.h"),
        "binary_sha256": sha256_file(binary),
        "entries": entries,
    }
    certificate_path = out / "certificates.json"
    atomic_write_text(certificate_path, json.dumps(document, indent=2, sort_keys=True) + "\n")
    return certificate_path, {
        "entries": len(entries),
        "receipts_sha256": sha256_file(receipts_path),
        "certificates_sha256": sha256_file(certificate_path),
    }


def validate_raw_csv(
    path: Path,
    job: Job,
    *,
    subgroup_order: int,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != RAW_HEADER:
            raise ValueError(f"{path}: raw CSV header differs from the frozen core schema")
        for line_number, raw in enumerate(reader, 2):
            if None in raw:
                raise ValueError(f"{path}:{line_number}: trailing core fields")
            try:
                row: dict[str, Any] = {
                    field: parse_uint64_decimal(raw[field], f"{path}:{line_number}:{field}")
                    for field in RAW_INTEGER_FIELDS
                }
                row["sec"] = float(raw["sec"])
            except (KeyError, TypeError, ValueError) as exc:
                raise ValueError(f"{path}:{line_number}: nonnumeric or missing core field") from exc
            rows.append(row)
    if len(rows) != job.targets:
        raise ValueError(f"{path}: found {len(rows)} rows, expected exactly {job.targets}")

    for offset, row in enumerate(rows):
        target_index = job.target_start + offset
        if row["run"] != offset or row["target_index"] != target_index:
            raise ValueError(f"{path}: run/target index mismatch at row {offset}")
        scalar = expected_scalar(job.target_seed, target_index, subgroup_order)
        stream = expected_walk_stream(job.walk_seed, target_index)
        if row["target_scalar"] != scalar:
            raise ValueError(f"{path}: substituted or misderived target scalar at {target_index}")
        if row["walk_stream_seed"] != stream:
            raise ValueError(f"{path}: incorrect walk stream at {target_index}")
        if row["ok"] != 1:
            raise ValueError(f"{path}: planted-key verification failed at {target_index}")
        if any(not 0 <= row[field] <= UINT64_MASK for field in RAW_INTEGER_FIELDS):
            raise ValueError(f"{path}: integer field outside uint64 at {target_index}")
        if not math.isfinite(row["sec"]) or row["sec"] <= 0:
            raise ValueError(f"{path}: invalid measured seconds at {target_index}")
        identities = (
            (row["setup_ops"], row["setup_adds"] + row["setup_doubles"], "setup ops"),
            (row["walk_ops"], row["walk_adds"] + row["walk_doubles"], "walk ops"),
            (row["ops"], row["adds"] + row["doubles"], "total ops"),
            (row["ops"], row["setup_ops"] + row["walk_ops"], "setup/walk ops"),
            (row["adds"], row["setup_adds"] + row["walk_adds"], "add split"),
            (row["doubles"], row["setup_doubles"] + row["walk_doubles"], "double split"),
        )
        for actual, expected, label in identities:
            if actual != expected:
                raise ValueError(f"{path}: {label} identity failed at {target_index}")
        if row["setup_adds"] != EXPECTED_SETUP_ADDS or row["setup_doubles"] != EXPECTED_SETUP_DOUBLES:
            raise ValueError(f"{path}: frozen target-setup count failed at {target_index}")
        if row["walk_ops"] <= 0 or row["walks"] <= 0:
            raise ValueError(f"{path}: empty collision walk at {target_index}")
        if row["abandoned"] > row["walks"] or row["useless"] > row["walks"]:
            raise ValueError(f"{path}: walk diagnostic count exceeds starts at {target_index}")
        if row["canon_sign_tests"] != row["canon_calls"]:
            raise ValueError(f"{path}: canonicalizer call/sign count failed at {target_index}")
        if row["canon_negations"] > row["canon_sign_tests"]:
            raise ValueError(f"{path}: canonicalizer counter order failed at {target_index}")
        if job.mode == 0:
            if row["canon_x_squares"] != 0 or row["canon_y_squares"] != 0:
                raise ValueError(f"{path}: mode-0 action squares are nonzero at {target_index}")
        elif job.mode == 1:
            if (
                row["canon_x_squares"] != 50 * row["canon_calls"]
                or row["canon_y_squares"] > 50 * row["canon_calls"]
            ):
                raise ValueError(f"{path}: mode-1 action primitive multiple failed at {target_index}")
        elif job.mode == 2:
            if (
                row["canon_x_squares"] != 34 * row["canon_calls"]
                or row["canon_y_squares"] % 17
                or row["canon_y_squares"] > 34 * row["canon_calls"]
            ):
                raise ValueError(f"{path}: mode-2 action primitive multiple failed at {target_index}")
        else:
            raise ValueError(f"{path}: unsupported mode {job.mode}")
    return rows


def normalized_rows(job: Job, raw_rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for row in raw_rows:
        normalized = {
            "block_id": row["target_index"],
            "replicate": job.replicate,
            "arm": job.arm,
            "curve_id": job.curve_id,
            "orbit_id": job.orbit_id,
            "b": job.b,
            "a2": job.a2,
            "mode": job.mode,
            "setup_seed": job.setup_seed,
            "target_seed": job.target_seed,
            "walk_seed": job.walk_seed,
            "run": row["run"],
            "target_index": row["target_index"],
            "k": row["target_scalar"],
            "walk_stream_seed": row["walk_stream_seed"],
        }
        normalized.update({field: row[field] for field in RAW_HEADER[4:]})
        output.append(normalized)
    return output


def run_jobs(
    out: Path,
    binary: Path,
    jobs: list[Job],
    scheduled: list[Job],
    cores: list[int],
    timeout_seconds: int,
    subgroup_order: int,
) -> dict[str, Any]:
    raw_dir = out / "raw"
    durable_mkdir(raw_dir)
    receipts_path = out / "jobs.jsonl"
    receipt_lock = threading.Lock()
    progress_lock = threading.Lock()
    error_lock = threading.Lock()
    stop = threading.Event()
    errors: list[BaseException] = []
    completed = 0
    launch_start = time.monotonic()
    assigned_core = {job.key: cores[index % len(cores)] for index, job in enumerate(scheduled)}
    buckets: list[list[Job]] = [[] for _ in cores]
    for index, job in enumerate(scheduled):
        buckets[index % len(cores)].append(job)

    def append_receipt(receipt: dict[str, Any]) -> None:
        with receipt_lock:
            append_jsonl_durable(receipts_path, receipt)

    def execute(core: int, job: Job) -> dict[str, Any]:
        final = raw_dir / job.filename
        partial = final.with_name(final.name + ".partial")
        if final.exists() or partial.exists():
            raise FileExistsError(f"refusing pre-existing job output for {job.key}")
        command = [
            "taskset",
            "-c",
            str(core),
            str(binary),
            "run",
            str(job.b),
            str(job.a2),
            str(job.mode),
            str(job.targets),
            str(job.setup_seed),
            str(job.target_seed),
            str(job.walk_seed),
            str(job.target_start),
            str(partial),
        ]
        receipt = run_process(command, timeout=timeout_seconds, cancel=stop)
        receipt.update(
            {
                "job": asdict(job) | {"filename": job.filename},
                "core": core,
                "status": "failed",
                "output_partial": str(partial),
                "output_final": str(final),
            }
        )
        if receipt["timed_out"]:
            raise JobFailure(f"job timed out: {job.key}", receipt)
        if receipt["cancelled"]:
            raise JobFailure(f"job cancelled after peer failure or interrupt: {job.key}", receipt)
        if receipt["exit_status"] != 0:
            raise JobFailure(f"job exited {receipt['exit_status']}: {job.key}", receipt)
        if receipt["stdout"] or receipt["stderr"]:
            raise JobFailure(f"job emitted unexpected stdout/stderr: {job.key}", receipt)
        if not partial.is_file():
            raise JobFailure(f"job produced no raw output: {job.key}", receipt)
        fsync_file(partial)
        try:
            validated = validate_raw_csv(partial, job, subgroup_order=subgroup_order)
        except BaseException as exc:
            receipt["validation_error"] = repr(exc)
            raise JobFailure(f"job validation failed: {job.key}", receipt) from exc
        durable_replace(partial, final)
        receipt.update(
            {
                "status": "completed",
                "validation": {
                    "rows": len(validated),
                    "verified": sum(row["ok"] for row in validated),
                    "target_start": validated[0]["target_index"],
                    "target_stop_exclusive": validated[-1]["target_index"] + 1,
                },
                "sha256": sha256_file(final),
            }
        )
        expected_receipt_fields = {
            "command",
            "cwd",
            "started_utc",
            "finished_utc",
            "elapsed_sec",
            "exit_status",
            "timed_out",
            "cancelled",
            "stdout",
            "stderr",
            "job",
            "core",
            "status",
            "output_partial",
            "output_final",
            "validation",
            "sha256",
        }
        if set(receipt) != expected_receipt_fields or receipt["cwd"] is not None:
            raise JobFailure(f"successful job receipt schema or cwd drifted: {job.key}", receipt)
        return receipt

    def worker(core: int, bucket: list[Job]) -> None:
        nonlocal completed
        for job in bucket:
            if stop.is_set():
                return
            try:
                receipt = execute(core, job)
                append_receipt(receipt)
            except JobFailure as exc:
                with error_lock:
                    errors.append(exc)
                stop.set()
                try:
                    append_receipt(exc.receipt)
                except BaseException as receipt_exc:
                    with error_lock:
                        errors.append(receipt_exc)
                return
            except BaseException as exc:
                with error_lock:
                    errors.append(exc)
                stop.set()
                try:
                    append_receipt(
                        {
                            "job": asdict(job) | {"filename": job.filename},
                            "core": core,
                            "status": "failed",
                            "error": repr(exc),
                            "finished_utc": utc_now(),
                        }
                    )
                except BaseException as receipt_exc:
                    with error_lock:
                        errors.append(receipt_exc)
                return
            try:
                with progress_lock:
                    completed += 1
                    if completed % 10 == 0 or completed == len(scheduled):
                        message = (
                            f"{utc_now()} {completed}/{len(scheduled)} jobs; "
                            f"elapsed={time.monotonic() - launch_start:.1f}s"
                        )
                        print(message, flush=True)
                        append_text_durable(out / "run.stdout.log", message + "\n")
            except BaseException as exc:
                with error_lock:
                    errors.append(exc)
                stop.set()
                return

    threads: list[threading.Thread] = []
    try:
        for core, bucket in zip(cores, buckets):
            if stop.is_set():
                break
            thread = threading.Thread(target=worker, args=(core, bucket), name=f"core-{core}")
            threads.append(thread)
            thread.start()
        for thread in threads:
            if thread.ident is not None:
                thread.join()
    except BaseException:
        stop.set()
        for thread in threads:
            if thread.ident is not None:
                thread.join()
        raise
    if errors:
        raise errors[0]
    if completed != len(scheduled):
        raise RuntimeError(f"only {completed}/{len(scheduled)} jobs completed")

    expected_files = {job.filename for job in jobs}
    actual_files = {path.name for path in raw_dir.iterdir() if path.is_file()}
    if actual_files != expected_files:
        raise RuntimeError(
            f"raw tree mismatch; missing={sorted(expected_files - actual_files)[:8]}, "
            f"extra={sorted(actual_files - expected_files)[:8]}"
        )
    if set(assigned_core) != {job.key for job in jobs}:
        raise RuntimeError("internal core-assignment key mismatch")
    try:
        receipts = [
            json.loads(line)
            for line in receipts_path.read_text().splitlines()
            if line.strip()
        ]
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("job receipt stream is missing or malformed") from exc
    if len(receipts) != len(jobs):
        raise ValueError(f"found {len(receipts)} job receipts, expected {len(jobs)}")
    expected_by_key = {job.key: job for job in jobs}
    seen: set[tuple[str, int, str]] = set()
    for receipt in receipts:
        job_document = receipt.get("job")
        if not isinstance(job_document, dict):
            raise ValueError("job receipt lacks a job object")
        key = (
            str(job_document.get("replicate")),
            int(job_document.get("target_start", -1)),
            str(job_document.get("arm")),
        )
        if key in seen or key not in expected_by_key:
            raise ValueError(f"duplicate or unexpected job receipt {key}")
        seen.add(key)
        job = expected_by_key[key]
        expected_job_document = asdict(job) | {"filename": job.filename}
        if job_document != expected_job_document:
            raise ValueError(f"job receipt metadata differs from the plan for {key}")
        expected_receipt_fields = {
            "command",
            "cwd",
            "started_utc",
            "finished_utc",
            "elapsed_sec",
            "exit_status",
            "timed_out",
            "cancelled",
            "stdout",
            "stderr",
            "job",
            "core",
            "status",
            "output_partial",
            "output_final",
            "validation",
            "sha256",
        }
        if set(receipt) != expected_receipt_fields or receipt["cwd"] is not None:
            raise ValueError(f"successful job receipt schema or cwd drifted for {key}")
        final = raw_dir / job.filename
        partial = final.with_name(final.name + ".partial")
        expected_command = [
            "taskset",
            "-c",
            str(assigned_core[key]),
            str(binary),
            "run",
            str(job.b),
            str(job.a2),
            str(job.mode),
            str(job.targets),
            str(job.setup_seed),
            str(job.target_seed),
            str(job.walk_seed),
            str(job.target_start),
            str(partial),
        ]
        if (
            receipt.get("status") != "completed"
            or receipt.get("core") != assigned_core[key]
            or receipt.get("command") != expected_command
            or receipt.get("exit_status") != 0
            or receipt.get("timed_out") is not False
            or receipt.get("cancelled") is not False
            or receipt.get("stdout") != ""
            or receipt.get("stderr") != ""
            or receipt.get("output_partial") != str(partial)
            or receipt.get("output_final") != str(final)
        ):
            raise ValueError(f"job process receipt failed closed validation for {key}")
        exact_validation = {
            "rows": job.targets,
            "verified": job.targets,
            "target_start": job.target_start,
            "target_stop_exclusive": job.target_start + job.targets,
        }
        if receipt.get("validation") != exact_validation:
            raise ValueError(f"job validation receipt mismatch for {key}")
        if not receipt.get("started_utc") or not receipt.get("finished_utc"):
            raise ValueError(f"job timestamp receipt missing for {key}")
        if receipt.get("sha256") != sha256_file(final):
            raise ValueError(f"job raw hash receipt mismatch for {key}")
    if seen != set(expected_by_key):
        raise ValueError("job receipt set is incomplete")
    return {
        "jobs": completed,
        "records": sum(job.targets for job in jobs),
        "receipts_sha256": sha256_file(receipts_path),
        "elapsed_sec": time.monotonic() - launch_start,
    }


class JobFailure(RuntimeError):
    def __init__(self, message: str, receipt: dict[str, Any]):
        super().__init__(message)
        receipt["error"] = message
        self.receipt = receipt


def write_records(
    out: Path,
    jobs: list[Job],
    spec: dict[str, Any],
) -> tuple[Path, dict[str, Any]]:
    raw_dir = out / "raw"
    record_path = out / "records.csv"
    partial = record_path.with_name(record_path.name + ".partial")
    if record_path.exists() or partial.exists():
        raise FileExistsError("refusing pre-existing normalized records output")
    fieldnames = list(spec["normalized_record_schema"])
    subgroup_order = int(spec["curve_family"]["subgroup_order"])
    ordered = sorted(
        jobs,
        key=lambda job: (
            0 if job.replicate == "primary" else 1,
            job.target_start,
            ARM_IDS.index(job.arm),
        ),
    )
    count = 0
    key_set: set[tuple[str, int, str]] = set()
    pairing: dict[tuple[str, int], list[dict[str, Any]]] = {}
    with partial.open("x", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="raise")
        writer.writeheader()
        for job in ordered:
            raw_rows = validate_raw_csv(raw_dir / job.filename, job, subgroup_order=subgroup_order)
            for row in normalized_rows(job, raw_rows):
                key = (row["replicate"], row["block_id"], row["arm"])
                if key in key_set:
                    raise ValueError(f"duplicate normalized record {key}")
                key_set.add(key)
                pairing.setdefault((row["replicate"], row["block_id"]), []).append(row)
                writer.writerow(row)
                count += 1
        handle.flush()
        os.fsync(handle.fileno())
    if count != int(spec["design"]["total_records"]):
        raise ValueError(f"normalized record count {count}, expected {spec['design']['total_records']}")

    for block_id in range(int(spec["design"]["primary_target_blocks"])):
        rows = pairing.get(("primary", block_id), [])
        if {row["arm"] for row in rows} != set(ARM_IDS) or len(rows) != len(ARM_IDS):
            raise ValueError(f"normalized primary arm set failed at block {block_id}")
        expected_k = expected_scalar(
            int(spec["seeds"]["target_root"]), block_id, subgroup_order
        )
        expected_stream = expected_walk_stream(
            int(spec["seeds"]["walk_primary_root"]), block_id
        )
        if {row["k"] for row in rows} != {expected_k}:
            raise ValueError(f"normalized target pairing failed at block {block_id}")
        if {row["walk_stream_seed"] for row in rows} != {expected_stream}:
            raise ValueError(f"normalized walk pairing failed at block {block_id}")
        within = block_id % int(spec["design"]["blocks_per_floor_orbit"])
        aa_rows = pairing.get(("aa-b", block_id), [])
        if within < int(spec["design"]["aa_blocks_per_orbit"]):
            if {row["arm"] for row in aa_rows} != set(ARM_IDS) or len(aa_rows) != len(ARM_IDS):
                raise ValueError(f"normalized A/A arm set failed at block {block_id}")
            aa_stream = expected_walk_stream(int(spec["seeds"]["walk_aa_root"]), block_id)
            if {row["k"] for row in aa_rows} != {expected_k}:
                raise ValueError(f"normalized A/A scalar pairing failed at block {block_id}")
            if {row["walk_stream_seed"] for row in aa_rows} != {aa_stream}:
                raise ValueError(f"normalized A/A walk stream failed at block {block_id}")
            if aa_stream == expected_stream:
                raise ValueError(f"A/A stream collision at block {block_id}")
        elif aa_rows:
            raise ValueError(f"unexpected A/A records at block {block_id}")

    durable_replace(partial, record_path)
    return record_path, {
        "rows": count,
        "unique_keys": len(key_set),
        "sha256": sha256_file(record_path),
    }


def append_manifest(out: Path, paths: Iterable[Path]) -> Path:
    manifest = out / "MANIFEST.sha256"
    lines = []
    for path in sorted(paths, key=lambda item: str(item.relative_to(out))):
        lines.append(f"{sha256_file(path)}  {path.relative_to(out)}")
    atomic_write_text(manifest, "\n".join(lines) + "\n")
    return manifest


def write_run_manifest(
    out: Path,
    *,
    spec: dict[str, Any],
    build: dict[str, Any],
    provenance: dict[str, Any],
    records: Path,
    certificates: Path,
    run_receipt: dict[str, Any],
    workers_used: int,
    cores: list[int],
) -> Path:
    """Create the analyzer-bound complete-run manifest after normalization."""
    compiler_lines = build.get("compiler_version")
    if not isinstance(compiler_lines, list) or not compiler_lines:
        raise ValueError("build receipt lacks the compiler-version lines")
    host = provenance["host"]
    manifest = {
        "schema": "m51-rho-run-manifest/v1",
        "study_id": spec["study_id"],
        "status": "complete",
        "created_utc": utc_now(),
        "inputs": {
            "rho_source_sha256": sha256_file(out / "inputs" / "rho.c"),
            "params_source_sha256": sha256_file(out / "inputs" / "params.h"),
            "runner_source_sha256": sha256_file(out / "inputs" / "run_replication.py"),
            "analyzer_source_sha256": sha256_file(out / "inputs" / "analyze.py"),
            "plot_source_sha256": sha256_file(out / "inputs" / "plot.py"),
            "protocol_sha256": sha256_file(out / "inputs" / "PROTOCOL.md"),
            "trace_zero_lane_sha256": sha256_file(
                out / "inputs" / "TRACE_ZERO_LANE.md"
            ),
            "frozen_manifest_sha256": sha256_file(out / "inputs" / "FROZEN.sha256"),
            "spec_sha256": sha256_file(out / "inputs" / "spec.json"),
            "sample_sha256": sha256_file(out / "inputs" / "sample.csv"),
            "records_sha256": sha256_file(records),
            "certificates_sha256": sha256_file(certificates),
        },
        "build": {
            "command": spec["execution_requirements"]["compile"],
            "actual_command": build["command"],
            "compiler_version": "\n".join(str(line) for line in compiler_lines),
            "binary_sha256": build["binary_sha256"],
            "cpu_features": host["cpu_flags"],
            "git_commit": provenance["git"]["commit"],
            "git_dirty": not provenance["git"]["worktree_clean"],
            "host": host["platform"],
            "cpu_affinity": cores,
        },
        "parameters": {
            "field_polynomial": "z^51 + z^6 + z^3 + z + 1",
            "field_degree": 51,
            "field_reduction_mask": 75,
            "subgroup_order": spec["curve_family"]["subgroup_order"],
            "cofactor": spec["curve_family"]["cofactor"],
            "ambient_order": spec["curve_family"]["ambient_order"],
            "a2": 0,
        },
        "execution": {
            "records": spec["design"]["total_records"],
            "primary_blocks": spec["design"]["primary_target_blocks"],
            "aa_blocks": spec["design"]["aa_target_blocks"],
            "jobs_planned": 400,
            "jobs_completed": run_receipt["jobs"],
            "blocks_per_job": spec["design"]["blocks_per_job"],
            "max_workers": spec["design"]["max_workers"],
            "workers_used": workers_used,
            "cores": cores,
            "timeout_seconds_per_job": spec["design"]["timeout_seconds_per_job"],
            "schedule_root": spec["seeds"]["schedule_root"],
            "job_order": "seeded_shuffle",
            "replacement_records": 0,
            "failed_jobs": [],
            "timed_out_jobs": [],
            "missing_jobs": [],
            "extra_jobs": [],
            "job_receipts_sha256": run_receipt["receipts_sha256"],
            "plan_sha256": sha256_file(out / "plan.json"),
        },
    }
    path = out / "run_manifest.json"
    atomic_write_text(path, json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return path


def parse_cores(value: str | None, workers: int) -> list[int]:
    available = sorted(os.sched_getaffinity(0))
    if value is not None:
        try:
            cores = [int(item) for item in value.split(",")]
        except ValueError as exc:
            raise ValueError("--cores must be a comma-separated integer list") from exc
    else:
        cores = available[:workers]
    if workers < 1 or workers > 4:
        raise ValueError("--workers must be between 1 and the frozen maximum 4")
    if len(cores) != workers or len(set(cores)) != workers:
        raise ValueError("--workers must equal the number of distinct pinned cores")
    if not set(cores).issubset(available):
        raise ValueError(f"requested cores {cores} outside process affinity {available}")
    return cores


def reject_duplicate_cli_options(argv: list[str]) -> None:
    canonical = ("--out", "--workers", "--cores", "--selftest-only")
    seen: set[str] = set()
    for item in argv:
        matched = next(
            (option for option in canonical if item == option or item.startswith(option + "=")),
            None,
        )
        if matched is None:
            continue
        if matched in seen:
            raise ValueError(f"command line repeats {matched}; options must be unique")
        seen.add(matched)


def main() -> None:
    reject_duplicate_cli_options(sys.argv[1:])
    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument(
        "--cores",
        help="comma-separated pinned cores; default is the first --workers cores in affinity",
    )
    parser.add_argument(
        "--selftest-only",
        action="store_true",
        help="build and certify all curve/mode pairs without launching any rho jobs",
    )
    args = parser.parse_args()
    cores = parse_cores(args.cores, args.workers)
    out = args.out.resolve()
    if out == REPO or REPO in out.parents:
        raise ValueError("run output must be outside the repository worktree")
    if out.exists() and any(out.iterdir()):
        raise FileExistsError(f"{out} is nonempty; no resume or overwrite is permitted")
    if not out.exists():
        durable_mkdir(out, parents=True)

    session: dict[str, Any] = {
        "schema": "m51-volcano-rho-session/v1",
        "started_utc": utc_now(),
        "status": "initializing",
        "selftest_only": args.selftest_only,
        "workers": args.workers,
        "cores": cores,
        "phase": "preflight",
    }
    replace_json(out / "session.json", session)
    try:
        spec = load_json(HERE / "spec.json")
        validate_spec(spec)
        frozen = verify_frozen_inputs(spec)
        host = host_receipt(cores)
        git_before = git_receipt()
        snapshots = snapshot_inputs(out, frozen)
        git_after = git_receipt()
        if git_after != git_before:
            raise RuntimeError("git revision or worktree state changed during frozen-input snapshot")
        spec = load_json(Path(snapshots["spec.json"]["snapshot_path"]))
        validate_spec(spec)
        samples, floor_ids = read_samples(Path(snapshots["sample.csv"]["snapshot_path"]))
        provenance = {
            "schema": "m51-volcano-rho-provenance/v1",
            "created_utc": utc_now(),
            "git": git_after,
            "git_before_snapshot": git_before,
            "git_after_snapshot": git_after,
            "host": host,
            "inputs": snapshots,
            "frozen_manifest_sha256": frozen[1],
            "invocation": [sys.executable, *sys.argv],
            "invocation_shell": shlex.join([sys.executable, *sys.argv]),
            "cwd": str(Path.cwd()),
        }
        atomic_write_text(out / "provenance.json", json.dumps(provenance, indent=2, sort_keys=True) + "\n")
        atomic_write_text(out / "run-command.txt", provenance["invocation_shell"] + "\n")

        session.update(status="running", phase="build")
        replace_json(out / "session.json", session)
        binary, build = build_binary(out, snapshots)
        session.update(phase="selftests", binary_sha256=build["binary_sha256"])
        replace_json(out / "session.json", session)
        certificates, certificate_receipt = run_selftests(
            out,
            binary,
            samples,
            floor_ids,
            int(spec["seeds"]["setup_root"]),
            cores[0],
        )
        if args.selftest_only:
            session.update(
                status="selftests_complete_no_benchmark",
                phase="complete",
                finished_utc=utc_now(),
                certificates=certificate_receipt,
                records=None,
                jobs_completed=0,
                scientific_run=False,
            )
            replace_json(out / "session.json", session)
            append_manifest(
                out,
                [
                    path
                    for path in out.rglob("*")
                    if path.is_file() and path.name != "MANIFEST.sha256"
                ],
            )
            print(json.dumps(session, indent=2, sort_keys=True))
            return

        jobs = make_jobs(spec, samples)
        scheduled = list(jobs)
        random.Random(int(spec["seeds"]["schedule_root"])).shuffle(scheduled)
        plan_jobs = []
        for schedule_index, job in enumerate(scheduled):
            plan_jobs.append(
                asdict(job)
                | {
                    "filename": job.filename,
                    "schedule_index": schedule_index,
                    "assigned_core": cores[schedule_index % len(cores)],
                }
            )
        plan = {
            "schema": "m51-volcano-rho-plan/v1",
            "created_utc": utc_now(),
            "schedule_algorithm": "python-random-v3-seeded-shuffle",
            "schedule_root": spec["seeds"]["schedule_root"],
            "workers": args.workers,
            "cores": cores,
            "blocks_per_job": spec["design"]["blocks_per_job"],
            "jobs": plan_jobs,
            "expected_jobs": len(jobs),
            "expected_records": sum(job.targets for job in jobs),
        }
        atomic_write_text(out / "plan.json", json.dumps(plan, indent=2, sort_keys=True) + "\n")
        session.update(
            phase="jobs",
            expected_jobs=len(jobs),
            expected_records=sum(job.targets for job in jobs),
            plan_sha256=sha256_file(out / "plan.json"),
        )
        replace_json(out / "session.json", session)
        run_receipt = run_jobs(
            out,
            binary,
            jobs,
            scheduled,
            cores,
            int(spec["design"]["timeout_seconds_per_job"]),
            int(spec["curve_family"]["subgroup_order"]),
        )
        session.update(phase="normalization", jobs_completed=run_receipt["jobs"])
        replace_json(out / "session.json", session)
        records, record_receipt = write_records(out, jobs, spec)
        if not certificates.is_file() or not records.is_file():
            raise RuntimeError("normalized analyzer inputs are missing")
        run_manifest = write_run_manifest(
            out,
            spec=spec,
            build=build,
            provenance=provenance,
            records=records,
            certificates=certificates,
            run_receipt=run_receipt,
            workers_used=args.workers,
            cores=cores,
        )
        session.update(
            status="complete",
            phase="complete",
            finished_utc=utc_now(),
            scientific_run=True,
            certificates=certificate_receipt,
            job_run=run_receipt,
            records=record_receipt,
            run_manifest={
                "path": str(run_manifest),
                "sha256": sha256_file(run_manifest),
            },
        )
        replace_json(out / "session.json", session)
        manifest = append_manifest(
            out,
            [
                path
                for path in out.rglob("*")
                if path.is_file() and path.name != "MANIFEST.sha256"
            ],
        )
        print(
            json.dumps(
                {
                    "session": session,
                    "records": str(records),
                    "certificates": str(certificates),
                    "run_manifest": str(run_manifest),
                    "manifest": str(manifest),
                },
                indent=2,
                sort_keys=True,
            )
        )
    except BaseException as exc:
        session.update(
            status="failed",
            phase=session.get("phase", "unknown"),
            finished_utc=utc_now(),
            error=repr(exc),
        )
        try:
            replace_json(out / "session.json", session)
        except BaseException:
            pass
        raise


if __name__ == "__main__":
    main()
