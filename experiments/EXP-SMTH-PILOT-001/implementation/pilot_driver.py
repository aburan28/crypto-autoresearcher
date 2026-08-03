#!/usr/bin/env python3
"""Null-only EXP-SMTH-PILOT-001 implementation and bounded pack sink.

This module deliberately has no curve, factor-base, S3, source, plant,
p-value, evidence, or research-state interface.  ``self-test`` uses only tiny
synthetic inputs.  ``run-null-pilot`` is the sole scientific entry point and
must not be invoked without a successor execution authorization.
"""

from __future__ import annotations

import argparse
import builtins
import concurrent.futures
from concurrent.futures.process import BrokenProcessPool
import contextlib
import dataclasses
from datetime import datetime, timezone
import fcntl
import gzip
import hashlib
import io
import json
import math
import os
from pathlib import Path
import resource
import socket
import subprocess
import sys
import tempfile
import time
from typing import BinaryIO, Callable, Iterable, Iterator, Sequence


EXPERIMENT_ID = "EXP-SMTH-PILOT-001"
RUN_ID = "RUN-SMTH-PILOT-001"
DOMAIN = "EXP-SMTH-PILOT-001/v1"
MASTER_SEED = 25051
BITS = (16, 20)
FIXTURES_PER_BIT = 2
NULL_TYPES = ("NULL-IID-EDGE", "NULL-K512-ADD")
REPLICATES = 4
VERTICES = 512
RECORDS_PER_ARRAY = VERTICES * (VERTICES - 1) // 2
ARRAY_COUNT = len(BITS) * FIXTURES_PER_BIT * len(NULL_TYPES) * REPLICATES
TOTAL_RECORDS = ARRAY_COUNT * RECORDS_PER_ARRAY
RECORDS_PER_SHARD = 32704
SHARD_COUNT = 128
SHARD_CAP_BYTES = 8_388_608
RECORD_CAP_BYTES = 1024
QUEUE_RECORDS = 4096
WORKERS = 4
MAX_PRIMALITY_CHECKS_PER_INTEGER = 12
MAX_PRIMALITY_CHECKS = 50_233_344
MAX_WALL_SECONDS = 7200
MAX_CPU_SECONDS = 28800
MAX_RSS_BYTES = 4_294_967_296
MAX_RUN_DISK_BYTES = 1_610_612_736
MAX_SHARD_AGGREGATE_BYTES = 1_073_741_824
MAX_OTHER_AGGREGATE_BYTES = 134_217_728
MAX_OTHER_FILE_BYTES = 33_554_432
MAX_TRACKED_BYTES = 1_207_959_552
BASELINE_PACK_CAP_BYTES = 150_000_000
FINAL_PACK_CAP_BYTES = 1_500_000_000
WORKTREE_RESERVATION_BYTES = 1_610_612_736
COMMON_DIR_RESERVATION_BYTES = 5_297_483_648
SAME_DEVICE_RESERVATION_BYTES = 6_908_096_384
FULL_V2_FACTORING_SUBTOTAL = 79_536_128
EXP_REL = Path("experiments/EXP-SMTH-PILOT-001")
REPO_ROOT = Path(__file__).resolve().parents[3]
RUN_REL = EXP_REL / "runs" / RUN_ID
RESULT_REL = EXP_REL / "results"
CERT_REL = RESULT_REL / "certificates"
RUN_FIXED_RELATIVE_PATHS = (
    RUN_REL / "manifest.yaml",
    RUN_REL / "command.txt",
    RUN_REL / "environment.json",
    RUN_REL / "stdout.log",
    RUN_REL / "stderr.log",
    RUN_REL / "raw-result.json",
    RESULT_REL / "feasibility_report.json",
    RESULT_REL / "seed_roster.json",
    CERT_REL / "shard_manifest.json",
)
SHARD_RELATIVE_PATHS = tuple(
    CERT_REL / f"shard-{index:03d}.jsonl.gz" for index in range(SHARD_COUNT)
)
RUN_EVIDENCE_ROSTER = RUN_FIXED_RELATIVE_PATHS + SHARD_RELATIVE_PATHS
SEED_COUNT = 2_109_444

assert RECORDS_PER_ARRAY == 130_816
assert TOTAL_RECORDS == 4_186_112
assert RECORDS_PER_SHARD * SHARD_COUNT == TOTAL_RECORDS
assert len(RUN_EVIDENCE_ROSTER) == len(set(RUN_EVIDENCE_ROSTER)) == 137


class IntegrityError(RuntimeError):
    """The deterministic construction or a certificate failed validation."""


class ResourceCapError(RuntimeError):
    """A frozen physical or computational ceiling was reached."""


class NetworkBlockedError(RuntimeError):
    """An attempted network-capable socket violates the frozen run guard."""


class DependencyInfrastructureError(RuntimeError):
    """A required runtime dependency is unavailable."""


def classify_failure(error: BaseException) -> tuple[str, str]:
    """Return (manifest status, failure class) without conflating integrity."""
    if isinstance(error, IntegrityError):
        return "invalid_integrity", "invalid_integrity"
    if isinstance(error, ResourceCapError):
        return "failed_infrastructure_or_budget", "resource_exhaustion"
    if isinstance(
        error,
        (
            BrokenProcessPool,
            DependencyInfrastructureError,
            ImportError,
            ModuleNotFoundError,
            OSError,
            subprocess.SubprocessError,
            KeyboardInterrupt,
        ),
    ):
        return "failed_infrastructure_or_budget", "infrastructure_error"
    return "failed_implementation", "implementation_error"


def cumulative_resources(
    prior_cpu: float,
    prior_wall: float,
    prior_peak_rss: int,
    attempt_sample: dict,
    attempt_wall: float,
) -> dict:
    return {
        "cpu_seconds": prior_cpu + attempt_sample["cpu_seconds"],
        "peak_rss_bytes": max(prior_peak_rss, attempt_sample["peak_rss_bytes"]),
        "wall_seconds": prior_wall + attempt_wall,
    }


def append_ordered_event(
    history: list[dict], event_type: str, **fields: object
) -> dict:
    event = {
        "event_type": event_type,
        "sequence": len(history),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        **fields,
    }
    history.append(event)
    return event


def repository_path(relative: Path) -> Path:
    if relative.is_absolute() or relative not in RUN_EVIDENCE_ROSTER:
        raise IntegrityError(f"path is outside exact run roster: {relative}")
    resolved = (REPO_ROOT / relative).resolve()
    if not resolved.is_relative_to(REPO_ROOT.resolve()):
        raise IntegrityError("repository path escaped checkout")
    return resolved


def validate_repository_binding() -> None:
    expected = (REPO_ROOT / EXP_REL / "implementation" / "pilot_driver.py").resolve()
    if Path(__file__).resolve() != expected:
        raise IntegrityError("driver is not at its frozen repository path")
    if len(RUN_EVIDENCE_ROSTER) != 137:
        raise IntegrityError("run-evidence roster count mismatch")
    for relative in RUN_EVIDENCE_ROSTER:
        repository_path(relative)


def resolved_descriptor_path(descriptor: int) -> Path:
    """Return the kernel-reported path for one regular-file descriptor."""
    try:
        if sys.platform == "darwin":
            if not hasattr(fcntl, "F_GETPATH"):
                raise IntegrityError("fcntl.F_GETPATH is unavailable on macOS")
            raw = fcntl.fcntl(descriptor, fcntl.F_GETPATH, b"\0" * 1024)
            path_bytes = raw.split(b"\0", 1)[0]
            if not path_bytes:
                raise IntegrityError(f"descriptor {descriptor} has no resolved path")
            return Path(os.fsdecode(path_bytes)).resolve(strict=True)
        if sys.platform.startswith("linux"):
            return Path(f"/proc/self/fd/{descriptor}").resolve(strict=True)
    except OSError as exc:
        raise IntegrityError(
            f"cannot resolve file descriptor {descriptor} to an exact path"
        ) from exc
    raise IntegrityError(
        f"exact descriptor-path validation is unsupported on {sys.platform}"
    )


def validate_descriptor_paths(bindings: Sequence[tuple[int, Path]]) -> None:
    for descriptor, target in bindings:
        try:
            expected = target.resolve(strict=True)
        except OSError as exc:
            raise IntegrityError(f"cannot resolve expected log path: {target}") from exc
        actual = resolved_descriptor_path(descriptor)
        if actual != expected:
            raise IntegrityError(
                f"file descriptor {descriptor} resolves to {actual}, not {expected}"
            )


def validate_log_redirections() -> None:
    validate_descriptor_paths(
        (
            (1, REPO_ROOT / RUN_REL / "stdout.log"),
            (2, REPO_ROOT / RUN_REL / "stderr.log"),
        )
    )
    OUTPUT_HANDLES.current = 2
    OUTPUT_HANDLES.observed_maximum = max(OUTPUT_HANDLES.observed_maximum, 2)


class OutputHandleBudget:
    def __init__(self, maximum: int = 8):
        self.maximum = maximum
        self.current = 0
        self.observed_maximum = 0

    @contextlib.contextmanager
    def opened(self) -> Iterator[None]:
        self.current += 1
        self.observed_maximum = max(self.observed_maximum, self.current)
        if self.current > self.maximum:
            self.current -= 1
            raise ResourceCapError("process-output handle cap exceeded")
        try:
            yield
        finally:
            self.current -= 1


OUTPUT_HANDLES = OutputHandleBudget()


def _install_no_network_guard() -> tuple[object, object]:
    original_socket = socket.socket
    original_create_connection = socket.create_connection

    class GuardedSocket(original_socket):  # type: ignore[misc, valid-type]
        def __init__(self, family=socket.AF_INET, *args, **kwargs):
            if family in (socket.AF_INET, socket.AF_INET6):
                raise NetworkBlockedError("network socket creation blocked")
            super().__init__(family, *args, **kwargs)

    def blocked_create_connection(*_args, **_kwargs):
        raise NetworkBlockedError("network connection blocked")

    socket.socket = GuardedSocket
    socket.create_connection = blocked_create_connection
    return original_socket, original_create_connection


@contextlib.contextmanager
def no_network_guard() -> Iterator[None]:
    originals = _install_no_network_guard()
    try:
        yield
    finally:
        socket.socket = originals[0]  # type: ignore[assignment]
        socket.create_connection = originals[1]  # type: ignore[assignment]


def _worker_no_network_guard() -> None:
    _install_no_network_guard()


def _parse_ps_cpu(value: str) -> float:
    day_split = value.split("-")
    days = int(day_split[0]) if len(day_split) == 2 else 0
    clock = day_split[-1].split(":")
    if len(clock) == 3:
        hours, minutes, seconds = clock
    else:
        hours, minutes, seconds = "0", clock[0], clock[1]
    return days * 86400 + int(hours) * 3600 + int(minutes) * 60 + float(seconds)


@dataclasses.dataclass
class ProcessTreeMonitor:
    started_wall: float = dataclasses.field(default_factory=time.monotonic)
    peak_rss_bytes: int = 0
    maximum_cpu_seconds: float = MAX_CPU_SECONDS
    maximum_rss_bytes: int = MAX_RSS_BYTES

    def __post_init__(self) -> None:
        usage = resource.getrusage(resource.RUSAGE_CHILDREN)
        self._baseline_children_cpu = usage.ru_utime + usage.ru_stime
        self._baseline_parent_cpu = time.process_time()
        self._worker_cpu_seconds = 0.0
        self._worker_peak_rss: dict[int, int] = {}

    def observe_worker_record(
        self, worker_pid: int, worker_cpu_seconds: float, worker_peak_rss_bytes: int
    ) -> dict:
        self._worker_cpu_seconds += worker_cpu_seconds
        self._worker_peak_rss[worker_pid] = max(
            self._worker_peak_rss.get(worker_pid, 0), worker_peak_rss_bytes
        )
        parent_usage = resource.getrusage(resource.RUSAGE_SELF)
        parent_peak = parent_usage.ru_maxrss
        if sys.platform != "darwin":
            parent_peak *= 1024
        cpu_seconds = (
            time.process_time() - self._baseline_parent_cpu + self._worker_cpu_seconds
        )
        conservative_rss = parent_peak + sum(self._worker_peak_rss.values())
        self.peak_rss_bytes = max(self.peak_rss_bytes, conservative_rss)
        if cpu_seconds > self.maximum_cpu_seconds:
            raise ResourceCapError("process-tree CPU cap exceeded")
        if self.peak_rss_bytes > self.maximum_rss_bytes:
            raise ResourceCapError("process-tree RSS cap exceeded")
        return {
            "cpu_seconds": cpu_seconds,
            "peak_rss_bytes": self.peak_rss_bytes,
        }

    def sample(self, *, enforce: bool = True) -> dict:
        with OUTPUT_HANDLES.opened():
            result = subprocess.run(
                ["ps", "-axo", "pid=,ppid=,rss=,time="],
                check=True,
                capture_output=True,
                text=True,
            )
        rows: dict[int, tuple[int, int, float]] = {}
        for line in result.stdout.splitlines():
            fields = line.split()
            if len(fields) != 4:
                continue
            pid, ppid, rss_kib = map(int, fields[:3])
            rows[pid] = (ppid, rss_kib * 1024, _parse_ps_cpu(fields[3]))
        selected = {os.getpid()}
        changed = True
        while changed:
            changed = False
            for pid, (ppid, _, _) in rows.items():
                if ppid in selected and pid not in selected:
                    selected.add(pid)
                    changed = True
        active_cpu = sum(rows[pid][2] for pid in selected if pid in rows)
        active_rss = sum(rows[pid][1] for pid in selected if pid in rows)
        child_usage = resource.getrusage(resource.RUSAGE_CHILDREN)
        waited_cpu = max(
            0.0,
            child_usage.ru_utime
            + child_usage.ru_stime
            - self._baseline_children_cpu,
        )
        observed_cpu = (
            time.process_time() - self._baseline_parent_cpu + self._worker_cpu_seconds
        )
        cpu_seconds = max(active_cpu + waited_cpu, observed_cpu)
        self.peak_rss_bytes = max(self.peak_rss_bytes, active_rss)
        if enforce:
            if cpu_seconds > self.maximum_cpu_seconds:
                raise ResourceCapError("process-tree CPU cap exceeded")
            if self.peak_rss_bytes > self.maximum_rss_bytes:
                raise ResourceCapError("process-tree RSS cap exceeded")
        return {
            "cpu_seconds": cpu_seconds,
            "current_rss_bytes": active_rss,
            "peak_rss_bytes": self.peak_rss_bytes,
            "process_count": len(selected),
            "wall_seconds": time.monotonic() - self.started_wall,
        }

    def accounting_without_subprocess(self) -> dict:
        parent_usage = resource.getrusage(resource.RUSAGE_SELF)
        parent_peak = parent_usage.ru_maxrss
        if sys.platform != "darwin":
            parent_peak *= 1024
        return {
            "cpu_seconds": time.process_time() - self._baseline_parent_cpu + self._worker_cpu_seconds,
            "peak_rss_bytes": max(
                self.peak_rss_bytes,
                parent_peak + sum(self._worker_peak_rss.values()),
            ),
        }


def _allocated_bytes(path: Path) -> int:
    stat = path.stat()
    return getattr(stat, "st_blocks", 0) * 512 or stat.st_size


def measure_run_storage() -> dict:
    shard_paths = set(SHARD_RELATIVE_PATHS)
    shard_bytes = other_bytes = physical_bytes = 0
    oversized_other = []
    for relative in RUN_EVIDENCE_ROSTER:
        path = REPO_ROOT / relative
        if path.exists() and path.is_file():
            size = path.stat().st_size
            physical_bytes += _allocated_bytes(path)
            if relative in shard_paths:
                shard_bytes += size
            else:
                other_bytes += size
                if size > MAX_OTHER_FILE_BYTES:
                    oversized_other.append(str(relative))
    for directory in (REPO_ROOT / RUN_REL, REPO_ROOT / CERT_REL):
        if directory.exists():
            for partial in directory.rglob("*.partial"):
                physical_bytes += _allocated_bytes(partial)
    tracked_bytes = shard_bytes + other_bytes
    return {
        "other_tracked_bytes": other_bytes,
        "physical_run_bytes": physical_bytes,
        "shard_tracked_bytes": shard_bytes,
        "tracked_bytes": tracked_bytes,
        "oversized_other_paths": oversized_other,
    }


def enforce_storage_caps(measurement: dict) -> None:
    if measurement["physical_run_bytes"] > MAX_RUN_DISK_BYTES:
        raise ResourceCapError("run-phase disk cap exceeded")
    if measurement["shard_tracked_bytes"] > MAX_SHARD_AGGREGATE_BYTES:
        raise ResourceCapError("aggregate shard cap exceeded")
    if measurement["other_tracked_bytes"] > MAX_OTHER_AGGREGATE_BYTES:
        raise ResourceCapError("aggregate other-artifact cap exceeded")
    if measurement["tracked_bytes"] > MAX_TRACKED_BYTES:
        raise ResourceCapError("aggregate tracked-byte cap exceeded")
    if measurement.get("oversized_other_paths"):
        raise ResourceCapError("individual other-artifact cap exceeded")


def finalize_stable_storage_receipt(
    result: dict,
    manifest: dict,
    result_paths: Sequence[Path],
    manifest_path: Path,
    measure: Callable[[], dict],
    enforce: Callable[[dict], None],
    *,
    maximum_iterations: int = 16,
) -> dict:
    """Converge self-accounting terminal JSON files without a later write."""
    candidate = measure()
    for iteration in range(maximum_iterations):
        result["terminal_storage_receipt"] = candidate
        if "disk_bytes_by_phase_and_total" in result:
            result["disk_bytes_by_phase_and_total"]["run_phase_final"] = candidate
            result["disk_bytes_by_phase_and_total"]["total_physical_bytes"] = candidate[
                "physical_run_bytes"
            ]
        if "projected_v2_full_contract" in result:
            result["projected_v2_full_contract"]["modeled_disk_bytes"] = (
                candidate["tracked_bytes"]
                * result["projected_v2_full_contract"]["factorization_count"]
                / TOTAL_RECORDS
            )
        for path in result_paths:
            atomic_json(path, result)
        manifest["final_storage"] = candidate
        manifest["storage_receipt_iteration"] = iteration
        manifest["result_sha256"] = hashlib.sha256(
            canonical_json_bytes(result)
        ).hexdigest()
        atomic_json(manifest_path, manifest)
        observed = measure()
        enforce(observed)
        if observed == candidate:
            # No write follows this equality check. The bytes just measured are
            # the terminal bytes whose receipt is embedded in all three files.
            return observed
        candidate = observed
    raise ResourceCapError("terminal storage receipt did not converge")


def canonical_json_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def sha256_file(path: Path, chunk_bytes: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(chunk_bytes)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def atomic_json(path: Path, value: object) -> None:
    atomic_bytes(path, canonical_json_bytes(value) + b"\n")


def atomic_bytes(path: Path, payload: bytes) -> None:
    if len(payload) > MAX_OTHER_FILE_BYTES:
        raise ResourceCapError(f"other artifact exceeds cap: {path}")
    partial = path.with_name(path.name + ".partial")
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with OUTPUT_HANDLES.opened():
            with partial.open("xb") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
        os.replace(partial, path)
        fsync_directory(path.parent)
    except BaseException:
        partial.unlink(missing_ok=True)
        raise


def derived_seed(
    object_name: str, bits: int, fixture: int, replicate: int, draw: int
) -> bytes:
    # The frozen seed rule names exactly these six pipe-separated fields.
    material = (
        f"{DOMAIN}|{object_name}|{bits}|{fixture}|{replicate}|{draw}"
    ).encode("utf-8")
    return hashlib.sha256(material).digest()[:16]


@dataclasses.dataclass(frozen=True, order=True)
class SeedStreamDescriptor:
    object_name: str
    bits: int
    fixture: int
    replicate: int
    first_draw: int
    last_draw: int

    @property
    def seed_count(self) -> int:
        return self.last_draw - self.first_draw + 1


def seed_stream_descriptors() -> list[SeedStreamDescriptor]:
    descriptors = []
    for bits in BITS:
        for fixture in range(FIXTURES_PER_BIT):
            for replicate in range(REPLICATES):
                descriptors.append(
                    SeedStreamDescriptor(
                        "NULL-IID-EDGE", bits, fixture, replicate, 0, 130815
                    )
                )
                descriptors.append(
                    SeedStreamDescriptor(
                        "NULL-K512-ADD-A", bits, fixture, replicate, 0, 511
                    )
                )
                descriptors.append(
                    SeedStreamDescriptor(
                        "NULL-K512-ADD-B", bits, fixture, replicate, 0, 511
                    )
                )
    for bits in BITS:
        for fixture in range(FIXTURES_PER_BIT):
            descriptors.append(
                SeedStreamDescriptor("prime", bits, fixture, 0, 0, 0)
            )
    descriptors.sort()
    if len(descriptors) != 52 or sum(item.seed_count for item in descriptors) != SEED_COUNT:
        raise IntegrityError("compact seed descriptor arithmetic mismatch")
    return descriptors


def build_seed_roster() -> dict:
    exact_membership: set[bytes] = set()
    all_digest = hashlib.sha256()
    entries = []
    collision_count = 0
    inserted_count = 0
    for descriptor in seed_stream_descriptors():
        stream_digest = hashlib.sha256()
        for draw in range(descriptor.first_draw, descriptor.last_draw + 1):
            seed = derived_seed(
                descriptor.object_name,
                descriptor.bits,
                descriptor.fixture,
                descriptor.replicate,
                draw,
            )
            inserted_count += 1
            if seed in exact_membership:
                collision_count += 1
            exact_membership.add(seed)
            stream_digest.update(seed)
            all_digest.update(seed)
        entries.append(
            {
                "bits": descriptor.bits,
                "first_draw": descriptor.first_draw,
                "fixture": descriptor.fixture,
                "last_draw": descriptor.last_draw,
                "object_name": descriptor.object_name,
                "ordered_concatenated_seed_bytes_sha256": stream_digest.hexdigest(),
                "replicate": descriptor.replicate,
                "seed_count": descriptor.seed_count,
            }
        )
    if inserted_count != SEED_COUNT or len(exact_membership) != SEED_COUNT or collision_count:
        raise IntegrityError("exact seed collision membership failed")
    payload = {
        "collision_count": collision_count,
        "derivation": {
            "domain": DOMAIN,
            "integer_encoding": "base-10 ASCII without sign, padding or whitespace",
            "seed_bytes": "first 16 bytes of SHA-256 over the exact UTF-8 domain string",
            "separator_hex": "7c",
            "tuple_fields_in_order": [
                "domain", "object_name", "bits", "fixture", "replicate", "draw"
            ],
        },
        "distinct_count": len(exact_membership),
        "inserted_count": inserted_count,
        "ordered_all_seed_bytes_sha256": all_digest.hexdigest(),
        "schema": "compact_mechanically_expandable_v1",
        "stream_entries": entries,
    }
    roster = dict(payload)
    roster["canonical_payload_sha256"] = hashlib.sha256(
        canonical_json_bytes(payload)
    ).hexdigest()
    if len(canonical_json_bytes(roster)) + 1 > MAX_OTHER_FILE_BYTES:
        raise ResourceCapError("compact seed roster exceeds frozen cap")
    return roster


def verify_seed_roster(roster: dict) -> bool:
    if roster.get("canonical_payload_sha256") is None:
        return False
    payload = dict(roster)
    claimed = payload.pop("canonical_payload_sha256")
    if hashlib.sha256(canonical_json_bytes(payload)).hexdigest() != claimed:
        return False
    rebuilt = build_seed_roster()
    return rebuilt == roster


def deterministic_bytes(seed: bytes) -> Iterator[bytes]:
    counter = 0
    while True:
        yield hashlib.sha256(seed + counter.to_bytes(8, "big")).digest()
        counter += 1


def unbiased_integer(seed: bytes, upper_inclusive: int) -> int:
    if upper_inclusive < 1:
        raise ValueError("upper_inclusive must be positive")
    width = upper_inclusive.bit_length()
    byte_count = (width + 7) // 8
    excess = byte_count * 8 - width
    for block in deterministic_bytes(seed):
        candidate = int.from_bytes(block[:byte_count], "big")
        if excess:
            candidate >>= excess
        if candidate < upper_inclusive:
            return candidate + 1
    raise AssertionError("unreachable")


def unbiased_residue(seed: bytes, modulus: int) -> int:
    return unbiased_integer(seed, modulus) - 1


def deterministic_prime(bits: int, fixture: int) -> int:
    try:
        from sympy import isprime
    except ImportError as exc:  # pragma: no cover - environment failure path
        raise DependencyInfrastructureError("sympy is required") from exc
    seed = int.from_bytes(derived_seed("prime", bits, fixture, 0, 0), "big")
    candidate = (1 << (bits - 1)) + seed % (1 << (bits - 2))
    if candidate % 2 == 0:
        candidate += 1
    while candidate < (1 << bits):
        if isprime(candidate):
            return candidate
        candidate += 2
    raise IntegrityError(f"prime search escaped {bits}-bit range")


@dataclasses.dataclass(frozen=True)
class ArrayDescriptor:
    bits: int
    fixture: int
    null_type: str
    replicate: int
    p: int

    @property
    def X(self) -> int:
        return self.p * self.p


def array_descriptors() -> list[ArrayDescriptor]:
    descriptors: list[ArrayDescriptor] = []
    for bits in BITS:
        for fixture in range(FIXTURES_PER_BIT):
            p = deterministic_prime(bits, fixture)
            for null_type in NULL_TYPES:
                for replicate in range(REPLICATES):
                    descriptors.append(
                        ArrayDescriptor(bits, fixture, null_type, replicate, p)
                    )
    if len(descriptors) != ARRAY_COUNT:
        raise IntegrityError("array count mismatch")
    return descriptors


def iter_array_values(
    descriptor: ArrayDescriptor,
) -> Iterator[tuple[int, int, bytes]]:
    """Yield (draw index, N, seed-or-edge-commitment) in frozen order."""
    if descriptor.null_type == "NULL-IID-EDGE":
        for draw in range(RECORDS_PER_ARRAY):
            seed = derived_seed(
                descriptor.null_type,
                descriptor.bits,
                descriptor.fixture,
                descriptor.replicate,
                draw,
            )
            yield draw, unbiased_integer(seed, descriptor.X), seed
        return
    if descriptor.null_type != "NULL-K512-ADD":
        raise IntegrityError("unknown null type")
    a_values = []
    b_values = []
    seeds = []
    for vertex in range(VERTICES):
        a_seed = derived_seed(
            "NULL-K512-ADD-A",
            descriptor.bits,
            descriptor.fixture,
            descriptor.replicate,
            vertex,
        )
        b_seed = derived_seed(
            "NULL-K512-ADD-B",
            descriptor.bits,
            descriptor.fixture,
            descriptor.replicate,
            vertex,
        )
        a_values.append(unbiased_residue(a_seed, descriptor.p))
        b_values.append(unbiased_residue(b_seed, descriptor.p))
        seeds.append((a_seed, b_seed))
    draw = 0
    for i in range(VERTICES):
        for j in range(i + 1, VERTICES):
            # This is an edge commitment, never a tuple-derived seed and never
            # part of exact collision membership under AMEND-008/009.
            edge_commitment = hashlib.sha256(
                b"NULL-K512-ADD-EDGE|" + seeds[i][0] + seeds[i][1]
                + seeds[j][0] + seeds[j][1]
            ).digest()[:16]
            value = (
                ((a_values[i] + a_values[j]) % descriptor.p) * descriptor.p
                + ((b_values[i] + b_values[j]) % descriptor.p)
                + 1
            )
            yield draw, value, edge_commitment
            draw += 1
    if draw != RECORDS_PER_ARRAY:
        raise IntegrityError("K512 edge count mismatch")


def verify_alleged_factors(N: int, factors: Sequence[Sequence[int]]) -> bool:
    try:
        from sympy import isprime
    except ImportError as exc:  # pragma: no cover
        raise DependencyInfrastructureError("sympy is required") from exc
    if N < 1 or len(factors) > MAX_PRIMALITY_CHECKS_PER_INTEGER:
        return False
    reconstruction = 1
    previous = 1
    for item in factors:
        if len(item) != 2:
            return False
        prime, exponent = int(item[0]), int(item[1])
        if prime <= previous or exponent < 1 or not isprime(prime):
            return False
        reconstruction *= prime**exponent
        previous = prime
    return reconstruction == N


def factor_certificate(sequential_index: int, N: int) -> tuple[dict, int]:
    try:
        from sympy import factorint, isprime
    except ImportError as exc:  # pragma: no cover
        raise DependencyInfrastructureError("sympy is required") from exc
    if N < 1:
        raise IntegrityError("N outside [1,X]")
    raw = factorint(N)
    factors = sorted((int(prime), int(exponent)) for prime, exponent in raw.items())
    if len(factors) > MAX_PRIMALITY_CHECKS_PER_INTEGER:
        raise ResourceCapError("per-integer primality ceiling exceeded")
    primality_checks = 0
    reconstruction = 1
    for prime, exponent in factors:
        primality_checks += 1
        if not isprime(prime):
            raise IntegrityError("factorint returned a composite factor")
        reconstruction *= prime**exponent
    if reconstruction != N:
        raise IntegrityError("factor reconstruction mismatch")
    record = {
        "LPF": max((prime for prime, _ in factors), default=1),
        "N": N,
        "reconstruction_ok": True,
        "sequential_index": sequential_index,
        "sorted_factors": [[prime, exponent] for prime, exponent in factors],
    }
    if len(canonical_json_bytes(record)) + 1 > RECORD_CAP_BYTES:
        raise IntegrityError("certificate logical record exceeds 1024 bytes")
    return record, primality_checks


def measured_factor_certificate(
    sequential_index: int, N: int
) -> tuple[dict, int, int, float, int]:
    started_cpu = time.process_time()
    record, checks = factor_certificate(sequential_index, N)
    usage = resource.getrusage(resource.RUSAGE_SELF)
    rss_bytes = usage.ru_maxrss if sys.platform == "darwin" else usage.ru_maxrss * 1024
    return record, checks, os.getpid(), time.process_time() - started_cpu, rss_bytes


def _synthetic_crash_worker() -> None:
    os._exit(17)


class CappedRawWriter(io.RawIOBase):
    """Raw writer that never writes a byte beyond its immutable cap."""

    def __init__(self, raw: BinaryIO, cap_bytes: int):
        self.raw = raw
        self.cap_bytes = cap_bytes
        self.bytes_written = 0

    def writable(self) -> bool:
        return True

    def write(self, data: bytes | bytearray) -> int:
        view = memoryview(data)
        remaining = self.cap_bytes - self.bytes_written
        accepted = min(len(view), max(0, remaining))
        if accepted:
            written = self.raw.write(view[:accepted])
            if written != accepted:
                raise OSError("short write")
            self.bytes_written += written
        if accepted != len(view):
            raise ResourceCapError("compressed shard cap exceeded")
        return accepted

    def flush(self) -> None:
        if not self.raw.closed:
            self.raw.flush()


class CertificateShardWriter:
    def __init__(
        self,
        certificate_dir: Path,
        *,
        checkpoint_callback: Callable[[list[dict], int], None] | None = None,
        records_per_shard: int = RECORDS_PER_SHARD,
        shard_count: int = SHARD_COUNT,
        total_records_expected: int = TOTAL_RECORDS,
        enforce_repository_paths: bool = False,
    ):
        self.directory = certificate_dir
        self.directory.mkdir(parents=True, exist_ok=True)
        if enforce_repository_paths and certificate_dir.resolve() != (REPO_ROOT / CERT_REL).resolve():
            raise IntegrityError("certificate directory is not frozen repository path")
        self.checkpoint_callback = checkpoint_callback
        self.records_per_shard = records_per_shard
        self.shard_count_expected = shard_count
        self.total_records_expected = total_records_expected
        self.enforce_repository_paths = enforce_repository_paths
        self.entries: list[dict] = []
        self.shard_index = -1
        self.record_count = 0
        self.total_records = 0
        self.logical_bytes = 0
        self._raw: BinaryIO | None = None
        self._capped: CappedRawWriter | None = None
        self._gzip: gzip.GzipFile | None = None
        self._partial: Path | None = None
        self._output_context = None

    def restore_verified(self, entries: Sequence[dict]) -> None:
        if self.entries or self._gzip is not None:
            raise IntegrityError("writer restore requires fresh state")
        expected_first = 0
        for expected_index, entry in enumerate(entries):
            if entry["shard_index"] != expected_index:
                raise IntegrityError("checkpoint shard index discontinuity")
            if entry["first_record_index"] != expected_first:
                raise IntegrityError("checkpoint record index discontinuity")
            if entry["record_count"] != self.records_per_shard:
                raise IntegrityError("checkpoint shard count mismatch")
            relative = Path(entry["repository_relative_path"])
            if self.enforce_repository_paths and relative != SHARD_RELATIVE_PATHS[expected_index]:
                raise IntegrityError("checkpoint path mismatch")
            path = REPO_ROOT / relative if self.enforce_repository_paths else self.directory / relative.name
            if not path.is_file() or path.stat().st_size != entry["compressed_bytes"]:
                raise IntegrityError("checkpoint shard missing or size mismatch")
            if sha256_file(path) != entry["gzip_sha256"]:
                raise IntegrityError("checkpoint shard hash mismatch")
            if not verify_shard_boundaries(path, entry):
                raise IntegrityError("checkpoint shard boundary reconstruction failed")
            self.entries.append(dict(entry))
            expected_first += entry["record_count"]
        self.shard_index = len(self.entries) - 1
        self.total_records = expected_first

    def reconcile_to_verified(self) -> None:
        verified = len(self.entries)
        for partial in self.directory.glob("shard-*.jsonl.gz.partial"):
            partial.unlink(missing_ok=True)
        for final in self.directory.glob("shard-*.jsonl.gz"):
            try:
                index = int(final.name[6:9])
            except ValueError as exc:
                raise IntegrityError("unexpected shard filename") from exc
            if index >= verified:
                final.unlink()
        self.total_records = sum(entry["record_count"] for entry in self.entries)
        self.shard_index = len(self.entries) - 1

    def _open(self) -> None:
        if self._gzip is not None:
            raise IntegrityError("multiple shard handles")
        self.shard_index += 1
        if self.shard_index >= self.shard_count_expected:
            raise IntegrityError("too many shards")
        final = self.directory / f"shard-{self.shard_index:03d}.jsonl.gz"
        partial = final.with_name(final.name + ".partial")
        partial.unlink(missing_ok=True)
        self._output_context = OUTPUT_HANDLES.opened()
        self._output_context.__enter__()
        self._raw = partial.open("xb")
        self._capped = CappedRawWriter(self._raw, SHARD_CAP_BYTES)
        self._gzip = gzip.GzipFile(
            filename="", mode="wb", fileobj=self._capped, mtime=0
        )
        self._partial = partial
        self.record_count = 0
        self.logical_bytes = 0

    def write(self, record: dict) -> None:
        if record["sequential_index"] != self.total_records:
            raise IntegrityError("non-sequential certificate record")
        payload = canonical_json_bytes(record) + b"\n"
        if len(payload) > RECORD_CAP_BYTES:
            raise IntegrityError("certificate logical record exceeds cap")
        if self._gzip is None:
            self._open()
        try:
            assert self._gzip is not None
            self._gzip.write(payload)
        except BaseException:
            self.abort_current()
            raise
        self.record_count += 1
        self.total_records += 1
        self.logical_bytes += len(payload)
        if self.record_count == self.records_per_shard:
            self.close_current()

    def close_current(self) -> None:
        if self._gzip is None:
            return
        partial = self._partial
        raw = self._raw
        capped = self._capped
        assert partial is not None and raw is not None and capped is not None
        final = partial.with_name(partial.name.removesuffix(".partial"))
        try:
            self._gzip.close()
            raw.flush()
            os.fsync(raw.fileno())
            raw.close()
            if self.record_count != self.records_per_shard:
                raise IntegrityError("non-full certificate shard")
            compressed = partial.stat().st_size
            if compressed != capped.bytes_written or compressed > SHARD_CAP_BYTES:
                raise ResourceCapError("shard byte accounting mismatch")
            os.replace(partial, final)
            fsync_directory(self.directory)
            relative_path = (
                str(final.relative_to(REPO_ROOT))
                if self.enforce_repository_paths
                else final.name
            )
            entry = {
                    "compressed_bytes": compressed,
                    "first_record_index": self.total_records - self.record_count,
                    "gzip_sha256": sha256_file(final),
                    "last_record_index": self.total_records - 1,
                    "logical_bytes": self.logical_bytes,
                    "record_count": self.record_count,
                    "repository_relative_path": relative_path,
                    "shard_index": self.shard_index,
                }
            if not verify_shard_boundaries(final, entry):
                final.unlink(missing_ok=True)
                raise IntegrityError("independent shard-boundary reconstruction failed")
            self.entries.append(entry)
            if self.checkpoint_callback is not None:
                try:
                    self.checkpoint_callback(list(self.entries), self.total_records)
                except BaseException:
                    self.entries.pop()
                    final.unlink(missing_ok=True)
                    fsync_directory(self.directory)
                    raise
        except BaseException:
            if not raw.closed:
                raw.close()
            partial.unlink(missing_ok=True)
            raise
        finally:
            self._gzip = None
            self._raw = None
            self._capped = None
            self._partial = None
            if self._output_context is not None:
                self._output_context.__exit__(None, None, None)
                self._output_context = None

    def abort_current(self) -> None:
        gzip_handle, raw, partial = self._gzip, self._raw, self._partial
        capped = self._capped
        self._gzip = None
        self._raw = None
        self._capped = None
        self._partial = None
        if gzip_handle is not None:
            try:
                gzip_handle.close()
            except BaseException:
                pass
        if raw is not None and not raw.closed:
            raw.close()
        if capped is not None and not capped.closed:
            capped.close()
        if partial is not None:
            partial.unlink(missing_ok=True)
        if self._output_context is not None:
            self._output_context.__exit__(None, None, None)
            self._output_context = None

    def finish(self) -> list[dict]:
        if self._gzip is not None:
            self.close_current()
        if (
            self.total_records != self.total_records_expected
            or len(self.entries) != self.shard_count_expected
        ):
            raise IntegrityError("final shard or record count mismatch")
        if sum(entry["compressed_bytes"] for entry in self.entries) > MAX_SHARD_AGGREGATE_BYTES:
            raise ResourceCapError("aggregate shard cap exceeded")
        return self.entries


def verify_shard_entry(path: Path, entry: dict) -> bool:
    return (
        path.is_file()
        and path.stat().st_size == entry["compressed_bytes"]
        and sha256_file(path) == entry["gzip_sha256"]
    )


def verify_shard_boundaries(path: Path, entry: dict) -> bool:
    first = last = None
    count = 0
    with gzip.open(path, "rb") as handle:
        for line in handle:
            record = json.loads(line)
            if first is None:
                first = record
            last = record
            count += 1
    if first is None or last is None or count != entry["record_count"]:
        return False
    for record, expected_index in (
        (first, entry["first_record_index"]),
        (last, entry["last_record_index"]),
    ):
        if record["sequential_index"] != expected_index:
            return False
        if not verify_alleged_factors(record["N"], record["sorted_factors"]):
            return False
        if record["LPF"] != max(
            (pair[0] for pair in record["sorted_factors"]), default=1
        ):
            return False
    return True


@dataclasses.dataclass(frozen=True)
class PackSinkResult:
    status: str
    bytes_written: int
    sha256: str | None
    producer_exit_status: int
    final_path: str
    partial_present: bool
    command: tuple[str, ...]
    revisions_utf8: str
    git_version: str | None


def bounded_pack_sink(
    producer_argv: Sequence[str],
    revisions: bytes,
    final_path: Path,
    cap_bytes: int,
    *,
    environment: dict[str, str] | None = None,
    chunk_bytes: int = 1024 * 1024,
) -> PackSinkResult:
    """Stream producer stdout into a file without ever exceeding cap_bytes."""
    if cap_bytes < 0 or chunk_bytes < 1:
        raise ValueError("invalid sink bounds")
    final_path.parent.mkdir(parents=True, exist_ok=True)
    partial = final_path.with_name(final_path.name + ".partial")
    if final_path.exists() or partial.exists():
        raise FileExistsError("pack destination already exists")
    stderr_file = tempfile.TemporaryFile()
    command = tuple(str(item) for item in producer_argv)
    git_version = None
    if command and Path(command[0]).name == "git":
        version = subprocess.run(
            [command[0], "--version"], check=True, capture_output=True, text=True
        )
        git_version = version.stdout.strip()
    try:
        revisions_utf8 = revisions.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("pack revisions must be UTF-8") from exc
    process = subprocess.Popen(
        list(command),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=stderr_file,
        env=environment,
    )
    assert process.stdin is not None and process.stdout is not None
    digest = hashlib.sha256()
    bytes_written = 0
    overflow = False
    try:
        try:
            process.stdin.write(revisions)
            process.stdin.close()
        except BrokenPipeError:
            process.stdin.close()
        with partial.open("xb") as sink:
            while True:
                chunk = process.stdout.read(chunk_bytes)
                if not chunk:
                    break
                remaining = cap_bytes - bytes_written
                accepted = min(len(chunk), max(0, remaining))
                if accepted:
                    sink.write(chunk[:accepted])
                    digest.update(chunk[:accepted])
                    bytes_written += accepted
                if accepted != len(chunk):
                    overflow = True
                    process.stdout.close()
                    break
            exit_status = process.wait()
            if overflow or exit_status != 0:
                raise ResourceCapError("pack overflow") if overflow else subprocess.CalledProcessError(exit_status, producer_argv)
            sink.flush()
            os.fsync(sink.fileno())
        os.replace(partial, final_path)
        fsync_directory(final_path.parent)
        return PackSinkResult(
            "success", bytes_written, digest.hexdigest(), exit_status,
            str(final_path), False, command, revisions_utf8, git_version
        )
    except BaseException:
        if process.poll() is None:
            process.stdout.close()
            process.wait()
        exit_status = process.returncode
        partial.unlink(missing_ok=True)
        return PackSinkResult(
            "overflow" if overflow else "producer_failure",
            bytes_written,
            None,
            int(exit_status if exit_status is not None else -1),
            str(final_path),
            partial.exists(),
            command,
            revisions_utf8,
            git_version,
        )
    finally:
        stderr_file.close()


@dataclasses.dataclass(frozen=True)
class DeviceGate:
    layout: str
    passed: bool
    required_worktree_bytes: int
    required_common_bytes: int


def evaluate_device_gate(
    worktree_device: int,
    common_device: int,
    worktree_free_bytes: int,
    common_free_bytes: int,
) -> DeviceGate:
    if worktree_device == common_device:
        return DeviceGate(
            "same-device",
            worktree_free_bytes >= SAME_DEVICE_RESERVATION_BYTES,
            SAME_DEVICE_RESERVATION_BYTES,
            SAME_DEVICE_RESERVATION_BYTES,
        )
    return DeviceGate(
        "split-device",
        worktree_free_bytes >= WORKTREE_RESERVATION_BYTES
        and common_free_bytes >= COMMON_DIR_RESERVATION_BYTES,
        WORKTREE_RESERVATION_BYTES,
        COMMON_DIR_RESERVATION_BYTES,
    )


def _filesystem_identity(path: Path) -> dict:
    with OUTPUT_HANDLES.opened():
        result = subprocess.run(
            ["df", "-P", str(path)], check=True, capture_output=True, text=True
        )
    fields = result.stdout.splitlines()[-1].split()
    statvfs = os.statvfs(path)
    return {
        "device_id": path.stat().st_dev,
        "free_bytes": statvfs.f_bavail * statvfs.f_frsize,
        "mount_point": fields[-1],
        "mount_source": fields[0],
        "path": str(path),
    }


def measure_device_layout(*, enforce_gate: bool = True) -> dict:
    with OUTPUT_HANDLES.opened():
        common_text = subprocess.run(
            ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
            cwd=REPO_ROOT, check=True, capture_output=True, text=True
        ).stdout.strip()
    worktree = _filesystem_identity(REPO_ROOT)
    common = _filesystem_identity(Path(common_text))
    gate = evaluate_device_gate(
        worktree["device_id"], common["device_id"],
        worktree["free_bytes"], common["free_bytes"]
    )
    measurement = {
        "common_directory": common,
        "gate": dataclasses.asdict(gate),
        "worktree": worktree,
    }
    if enforce_gate and not gate.passed:
        raise ResourceCapError("per-device free-space gate failed")
    return measurement


def _synthetic_producer(length: int, exit_status: int = 0) -> list[str]:
    code = (
        "import sys; n=int(sys.argv[1]); status=int(sys.argv[2]); "
        "sys.stdout.buffer.write(b'x'*n); sys.stdout.buffer.flush(); "
        "raise SystemExit(status)"
    )
    return [sys.executable, "-c", code, str(length), str(exit_status)]


def run_self_tests(only: set[str] | None = None) -> dict:
    tests: list[dict] = []

    def check(name: str, function: Callable[[], None]) -> None:
        if only and name not in only:
            return
        started = time.monotonic()
        function()
        tests.append({"name": name, "status": "pass", "seconds": time.monotonic() - started})

    with tempfile.TemporaryDirectory(prefix="smth-pilot-tests-") as temporary:
        root = Path(temporary)

        def exact_cap() -> None:
            result = bounded_pack_sink(_synthetic_producer(4096), b"", root / "exact.pack", 4096, chunk_bytes=257)
            assert result.status == "success" and result.bytes_written == 4096
            assert (root / "exact.pack").stat().st_size == 4096

        def cap_plus_one() -> None:
            result = bounded_pack_sink(_synthetic_producer(4097), b"", root / "overflow.pack", 4096, chunk_bytes=257)
            assert result.status == "overflow" and result.bytes_written == 4096
            assert not (root / "overflow.pack").exists()
            assert not (root / "overflow.pack.partial").exists()

        def producer_failure() -> None:
            result = bounded_pack_sink(_synthetic_producer(64, 7), b"", root / "failure.pack", 4096)
            assert result.status == "producer_failure" and result.producer_exit_status == 7
            assert not (root / "failure.pack").exists()
            assert not (root / "failure.pack.partial").exists()

        def split_device() -> None:
            passed = evaluate_device_gate(1, 2, WORKTREE_RESERVATION_BYTES, COMMON_DIR_RESERVATION_BYTES)
            failed_worktree = evaluate_device_gate(1, 2, WORKTREE_RESERVATION_BYTES - 1, COMMON_DIR_RESERVATION_BYTES)
            failed_common = evaluate_device_gate(1, 2, WORKTREE_RESERVATION_BYTES, COMMON_DIR_RESERVATION_BYTES - 1)
            same = evaluate_device_gate(3, 3, SAME_DEVICE_RESERVATION_BYTES, SAME_DEVICE_RESERVATION_BYTES)
            assert passed.passed and not failed_worktree.passed and not failed_common.passed
            assert same.passed and same.layout == "same-device"

        def certificate_controls() -> None:
            record, checks = factor_certificate(0, 360)
            assert checks == 3 and record["LPF"] == 5
            assert verify_alleged_factors(360, record["sorted_factors"])
            twelve_with_composite = [
                [2, 1], [3, 1], [5, 1], [7, 1], [11, 1], [13, 1],
                [17, 1], [19, 1], [23, 1], [29, 1], [31, 1], [35, 1],
            ]
            assert not verify_alleged_factors(math.prod(item[0] for item in twelve_with_composite), twelve_with_composite)
            oversized = dict(record)
            oversized["padding"] = ""
            padding_bytes = 1025 - (len(canonical_json_bytes(oversized)) + 1)
            assert padding_bytes > 0
            oversized["padding"] = "x" * padding_bytes
            assert len(canonical_json_bytes(oversized)) + 1 == 1025
            writer = CertificateShardWriter(
                root / "oversize", records_per_shard=1, shard_count=1,
                total_records_expected=1
            )
            try:
                writer.write(oversized)
            except IntegrityError:
                pass
            else:
                raise AssertionError("writer accepted 1025-byte record")
            assert not list((root / "oversize").glob("*.partial"))

        def deterministic_nulls() -> None:
            p = deterministic_prime(16, 0)
            iid = ArrayDescriptor(16, 0, "NULL-IID-EDGE", 0, p)
            add = ArrayDescriptor(16, 0, "NULL-K512-ADD", 0, p)
            iid_values = [next(iter_array_values(iid)) for _ in range(2)]
            assert iid_values[0] == iid_values[1]
            add_iter = iter_array_values(add)
            first = next(add_iter)
            assert 1 <= first[1] <= add.X
            assert len({derived_seed("probe", 16, 0, 0, i) for i in range(64)}) == 64

        def exact_path_roster() -> None:
            assert len(RUN_EVIDENCE_ROSTER) == len(set(RUN_EVIDENCE_ROSTER)) == 137
            assert SHARD_RELATIVE_PATHS[0] == CERT_REL / "shard-000.jsonl.gz"
            assert SHARD_RELATIVE_PATHS[-1] == CERT_REL / "shard-127.jsonl.gz"
            try:
                repository_path(Path("outside.json"))
            except IntegrityError:
                pass
            else:
                raise AssertionError("arbitrary output path accepted")

        def resource_controls() -> None:
            enforce_storage_caps({
                "physical_run_bytes": MAX_RUN_DISK_BYTES,
                "shard_tracked_bytes": MAX_SHARD_AGGREGATE_BYTES,
                "other_tracked_bytes": MAX_OTHER_AGGREGATE_BYTES,
                "tracked_bytes": MAX_TRACKED_BYTES,
            })
            over = {
                "physical_run_bytes": MAX_RUN_DISK_BYTES + 1,
                "shard_tracked_bytes": 0,
                "other_tracked_bytes": 0,
                "tracked_bytes": 0,
            }
            try:
                enforce_storage_caps(over)
            except ResourceCapError:
                pass
            else:
                raise AssertionError("disk cap plus one accepted")
            budget = OutputHandleBudget(maximum=1)
            try:
                with budget.opened():
                    with budget.opened():
                        pass
            except ResourceCapError:
                pass
            else:
                raise AssertionError("output handle cap plus one accepted")
            with no_network_guard():
                try:
                    socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                except NetworkBlockedError:
                    pass
                else:
                    raise AssertionError("network guard accepted AF_INET")
            monitor = ProcessTreeMonitor(maximum_cpu_seconds=MAX_CPU_SECONDS, maximum_rss_bytes=MAX_RSS_BYTES)
            sample = monitor.sample()
            assert sample["process_count"] >= 1 and sample["peak_rss_bytes"] > 0
            try:
                ProcessTreeMonitor(maximum_rss_bytes=0).sample()
            except ResourceCapError:
                pass
            else:
                raise AssertionError("process-tree RSS cap plus one accepted")

        def checkpoint_resume_and_cleanup() -> None:
            checkpoint = root / "checkpoint.json"
            events = []

            def save(entries: list[dict], next_index: int) -> None:
                payload = {"completed_shards": entries, "next_deterministic_index": next_index}
                atomic_json(checkpoint, payload)
                events.append(next_index)

            directory = root / "resume-certificates"
            first = CertificateShardWriter(
                directory, checkpoint_callback=save, records_per_shard=2,
                shard_count=2, total_records_expected=4
            )
            for index in range(2):
                first.write({"LPF": 2, "N": 2, "reconstruction_ok": True, "sequential_index": index, "sorted_factors": [[2, 1]]})
            saved = json.loads(checkpoint.read_text())
            resumed = CertificateShardWriter(
                directory, checkpoint_callback=save, records_per_shard=2,
                shard_count=2, total_records_expected=4
            )
            resumed.restore_verified(saved["completed_shards"])
            resumed.write({"LPF": 3, "N": 3, "reconstruction_ok": True, "sequential_index": 2, "sorted_factors": [[3, 1]]})
            resumed.abort_current()
            resumed.reconcile_to_verified()
            assert not list(directory.glob("*.partial"))
            assert (directory / "shard-000.jsonl.gz").exists()
            assert not (directory / "shard-001.jsonl.gz").exists()
            resumed.write({"LPF": 3, "N": 3, "reconstruction_ok": True, "sequential_index": 2, "sorted_factors": [[3, 1]]})
            resumed.write({"LPF": 5, "N": 5, "reconstruction_ok": True, "sequential_index": 3, "sorted_factors": [[5, 1]]})
            assert len(resumed.finish()) == 2 and events == [2, 4]

        def shard_mutation_and_hash_controls() -> None:
            directory = root / "mutation-shard"
            writer = CertificateShardWriter(
                directory, records_per_shard=1, shard_count=1,
                total_records_expected=1
            )
            writer.write({"LPF": 2, "N": 2, "reconstruction_ok": True, "sequential_index": 0, "sorted_factors": [[2, 1]]})
            entry = writer.finish()[0]
            path = directory / "shard-000.jsonl.gz"
            assert verify_shard_entry(path, entry)
            changed = bytearray(path.read_bytes())
            changed[len(changed) // 2] ^= 1
            path.write_bytes(changed)
            assert not verify_shard_entry(path, entry)
            sample = {"schema": "test", "stream_entries": [], "inserted_count": 0}
            wrapped = dict(sample)
            wrapped["canonical_payload_sha256"] = hashlib.sha256(canonical_json_bytes(sample)).hexdigest()
            claimed = wrapped.pop("canonical_payload_sha256")
            assert hashlib.sha256(canonical_json_bytes(wrapped)).hexdigest() == claimed

        def compact_seed_contract() -> None:
            roster = build_seed_roster()
            assert len(roster["stream_entries"]) == 52
            assert roster["inserted_count"] == roster["distinct_count"] == SEED_COUNT
            assert roster["collision_count"] == 0
            assert roster["ordered_all_seed_bytes_sha256"] == "c3991b86bedce849dd8b13dee1550ae79405526d9b1467ff4ac30436bdc37fc6"
            assert verify_seed_roster(roster)

        def integrity_and_resource_failure_cleanup() -> None:
            directory = root / "worker-failure"
            writer = CertificateShardWriter(
                directory, records_per_shard=2, shard_count=1,
                total_records_expected=2
            )
            try:
                for record, _checks, _pid, _cpu, _rss in _bounded_ordered_factorizations([(0, 2), (1, 0)]):
                    writer.write(record)
            except IntegrityError:
                writer.abort_current()
                writer.reconcile_to_verified()
            else:
                raise AssertionError("synthetic worker failure was accepted")
            assert not list(directory.glob("*.partial"))
            assert not list(directory.glob("shard-*.jsonl.gz"))
            assert classify_failure(IntegrityError("synthetic")) == (
                "invalid_integrity", "invalid_integrity"
            )
            writer = CertificateShardWriter(
                directory, records_per_shard=2, shard_count=1,
                total_records_expected=2
            )
            try:
                writer.write({"LPF": 2, "N": 2, "reconstruction_ok": True, "sequential_index": 0, "sorted_factors": [[2, 1]]})
                raise ResourceCapError("synthetic cap stop")
            except ResourceCapError:
                writer.abort_current()
                writer.reconcile_to_verified()
            assert not list(directory.glob("*.partial"))
            assert classify_failure(ResourceCapError("synthetic")) == (
                "failed_infrastructure_or_budget", "resource_exhaustion"
            )

        def cumulative_stop_resume_events() -> None:
            history: list[dict] = []
            append_ordered_event(
                history, "checkpoint", cpu_seconds=2.0,
                next_deterministic_index=2, outcome="running_checkpoint",
                peak_rss_bytes=100, wall_seconds=3.0
            )
            stopped = cumulative_resources(
                2.0, 3.0, 100,
                {"cpu_seconds": 0.75, "peak_rss_bytes": 120}, 1.25
            )
            append_ordered_event(
                history, "stop", **stopped,
                next_deterministic_index=2,
                outcome="failed_infrastructure_or_budget"
            )
            receipt = root / "event-checkpoint.json"
            atomic_json(receipt, {"event_history": history, **stopped})
            loaded = json.loads(receipt.read_text())
            append_ordered_event(
                loaded["event_history"], "resume",
                cpu_seconds=loaded["cpu_seconds"],
                next_deterministic_index=2, outcome="resume_started",
                peak_rss_bytes=loaded["peak_rss_bytes"],
                wall_seconds=loaded["wall_seconds"]
            )
            completed = cumulative_resources(
                loaded["cpu_seconds"], loaded["wall_seconds"],
                loaded["peak_rss_bytes"],
                {"cpu_seconds": 0.5, "peak_rss_bytes": 110}, 0.5
            )
            append_ordered_event(
                loaded["event_history"], "checkpoint", **completed,
                next_deterministic_index=4, outcome="running_checkpoint"
            )
            assert completed == {
                "cpu_seconds": 3.25,
                "peak_rss_bytes": 120,
                "wall_seconds": 4.75,
            }
            assert [item["event_type"] for item in loaded["event_history"]] == [
                "checkpoint", "stop", "resume", "checkpoint"
            ]
            assert [item["sequence"] for item in loaded["event_history"]] == list(range(4))

        def broken_worker_pool_infrastructure() -> None:
            directory = root / "broken-pool"
            checkpoints = []
            writer = CertificateShardWriter(
                directory,
                checkpoint_callback=lambda entries, index: checkpoints.append((entries, index)),
                records_per_shard=1, shard_count=2,
                total_records_expected=2
            )
            writer.write({"LPF": 2, "N": 2, "reconstruction_ok": True, "sequential_index": 0, "sorted_factors": [[2, 1]]})
            try:
                with concurrent.futures.ProcessPoolExecutor(max_workers=1) as pool:
                    pool.submit(_synthetic_crash_worker).result()
            except BrokenProcessPool as error:
                status, failure_class = classify_failure(error)
                writer.abort_current()
                writer.reconcile_to_verified()
            else:
                raise AssertionError("real worker exit did not break process pool")
            assert status == "failed_infrastructure_or_budget"
            assert failure_class == "infrastructure_error"
            assert checkpoints[0][1] == 1
            assert (directory / "shard-000.jsonl.gz").is_file()
            assert not list(directory.glob("*.partial"))
            assert classify_failure(ModuleNotFoundError("synthetic dependency"))[1] == "infrastructure_error"

        def dependency_wrapper_and_terminal_storage() -> None:
            original_import = builtins.__import__

            def missing_sympy(name, *args, **kwargs):
                if name == "sympy" or name.startswith("sympy."):
                    raise ModuleNotFoundError("synthetic missing sympy")
                return original_import(name, *args, **kwargs)

            builtins.__import__ = missing_sympy
            try:
                try:
                    factor_certificate(0, 2)
                except DependencyInfrastructureError as error:
                    status, failure_class = classify_failure(error)
                else:
                    raise AssertionError("real factor wrapper hid missing SymPy")
            finally:
                builtins.__import__ = original_import
            assert status == "failed_infrastructure_or_budget"
            assert failure_class == "infrastructure_error"

            terminal_root = root / "terminal-storage"
            terminal_root.mkdir()
            stdout_path = terminal_root / "stdout.log"
            raw_path = terminal_root / "raw-result.json"
            report_path = terminal_root / "feasibility_report.json"
            manifest_path = terminal_root / "manifest.yaml"
            stdout_path.write_bytes(
                b'{"terminal_record":"see manifest"}\n'
            )
            paths = (stdout_path, raw_path, report_path, manifest_path)

            def measure_terminal() -> dict:
                logical = sum(path.stat().st_size for path in paths if path.exists())
                physical = sum(_allocated_bytes(path) for path in paths if path.exists())
                return {
                    "other_tracked_bytes": logical,
                    "oversized_other_paths": [],
                    "physical_run_bytes": physical,
                    "shard_tracked_bytes": 0,
                    "tracked_bytes": logical,
                }

            def enforce_terminal(value: dict) -> None:
                assert value["tracked_bytes"] < 1_000_000
                assert value["physical_run_bytes"] < 1_000_000

            synthetic_result = {
                "disk_bytes_by_phase_and_total": {},
                "factorization_calls": 0,
            }
            synthetic_manifest = {"status": "completed_feasibility_only"}
            receipt = finalize_stable_storage_receipt(
                synthetic_result,
                synthetic_manifest,
                (raw_path, report_path),
                manifest_path,
                measure_terminal,
                enforce_terminal,
            )
            assert receipt == measure_terminal()
            assert json.loads(raw_path.read_text())["terminal_storage_receipt"] == receipt
            assert json.loads(report_path.read_text())["terminal_storage_receipt"] == receipt
            assert json.loads(manifest_path.read_text())["final_storage"] == receipt

        def real_subprocess_descriptor_redirection() -> None:
            descriptor_root = root / "descriptor-redirection"
            descriptor_root.mkdir()
            stdout_path = descriptor_root / "stdout.log"
            stderr_path = descriptor_root / "stderr.log"
            wrong_path = descriptor_root / "wrong.log"
            receipt_path = descriptor_root / "receipt.json"
            wrong_path.write_bytes(b"")
            child_code = r'''
import importlib.util
import json
import os
from pathlib import Path
import sys

module_path, stdout_text, stderr_text, wrong_text, receipt_text = sys.argv[1:]
spec = importlib.util.spec_from_file_location("smth_descriptor_child", module_path)
if spec is None or spec.loader is None:
    raise RuntimeError("cannot load pilot driver")
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
stdout_path = Path(stdout_text)
stderr_path = Path(stderr_text)
wrong_path = Path(wrong_text)
old_samefile_matches = os.path.samefile("/dev/fd/1", stdout_path)
if sys.platform == "darwin" and old_samefile_matches:
    raise AssertionError("old /dev/fd samefile failure was not reproduced")
module.validate_descriptor_paths(((1, stdout_path), (2, stderr_path)))
try:
    module.validate_descriptor_paths(((1, wrong_path),))
except module.IntegrityError:
    mismatch_rejected = True
else:
    mismatch_rejected = False
if not mismatch_rejected:
    raise AssertionError("exact-path guard accepted a wrong target")
Path(receipt_text).write_text(json.dumps({
    "mismatch_rejected": mismatch_rejected,
    "new_guard_passed": True,
    "old_samefile_matches": old_samefile_matches,
    "platform": sys.platform,
}) + "\n")
'''
            with stdout_path.open("wb") as stdout_handle, stderr_path.open("wb") as stderr_handle:
                completed = subprocess.run(
                    [
                        sys.executable,
                        "-c",
                        child_code,
                        str(Path(__file__).resolve()),
                        str(stdout_path.resolve()),
                        str(stderr_path.resolve()),
                        str(wrong_path.resolve()),
                        str(receipt_path.resolve()),
                    ],
                    env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                    stdout=stdout_handle,
                    stderr=stderr_handle,
                    check=False,
                )
            if completed.returncode != 0:
                raise AssertionError(
                    "real descriptor-redirection child failed: "
                    + stderr_path.read_text(errors="replace")
                )
            receipt = json.loads(receipt_path.read_text())
            assert receipt["new_guard_passed"] is True
            assert receipt["mismatch_rejected"] is True
            if sys.platform == "darwin":
                assert receipt["old_samefile_matches"] is False

        check("bounded-pack-exact-cap", exact_cap)
        check("bounded-pack-cap-plus-one", cap_plus_one)
        check("bounded-pack-producer-failure", producer_failure)
        check("split-device-accounting", split_device)
        check("factor-certificate-controls", certificate_controls)
        check("deterministic-null-plumbing", deterministic_nulls)
        check("exact-137-path-roster", exact_path_roster)
        check("process-tree-disk-handle-network-controls", resource_controls)
        check("checkpoint-resume-interruption-cleanup", checkpoint_resume_and_cleanup)
        check("one-byte-mutation-and-independent-hashes", shard_mutation_and_hash_controls)
        check("compact-52-stream-2109444-seed-contract", compact_seed_contract)
        check("integrity-and-resource-failure-cleanup", integrity_and_resource_failure_cleanup)
        check("cumulative-stop-resume-event-charging", cumulative_stop_resume_events)
        check("broken-worker-pool-infrastructure", broken_worker_pool_infrastructure)
        check("dependency-wrapper-and-terminal-storage", dependency_wrapper_and_terminal_storage)
        check("real-subprocess-descriptor-redirection", real_subprocess_descriptor_redirection)

    return {"scientific_runs": 0, "status": "pass", "tests": tests}


def _bounded_ordered_factorizations(
    indexed_values: Iterable[tuple[int, int]],
) -> Iterator[tuple[dict, int, int, float, int]]:
    with concurrent.futures.ProcessPoolExecutor(
        max_workers=WORKERS, initializer=_worker_no_network_guard
    ) as pool:
        pending: dict[int, concurrent.futures.Future] = {}
        source = iter(indexed_values)
        submit_index: int | None = None
        yield_index: int | None = None
        exhausted = False
        while pending or not exhausted:
            while not exhausted and len(pending) < QUEUE_RECORDS:
                try:
                    index, value = next(source)
                except StopIteration:
                    exhausted = True
                    break
                if submit_index is None:
                    submit_index = yield_index = index
                if index != submit_index:
                    raise IntegrityError("input index discontinuity")
                pending[index] = pool.submit(measured_factor_certificate, index, value)
                submit_index += 1
            if yield_index is not None and yield_index in pending:
                yield pending.pop(yield_index).result()
                yield_index += 1


def _ks_two_sided(left: Sequence[float], right: Sequence[float]) -> float:
    a, b = sorted(left), sorted(right)
    i = j = 0
    maximum = 0.0
    while i < len(a) or j < len(b):
        if j == len(b) or (i < len(a) and a[i] <= b[j]):
            value = a[i]
        else:
            value = b[j]
        while i < len(a) and a[i] <= value:
            i += 1
        while j < len(b) and b[j] <= value:
            j += 1
        maximum = max(maximum, abs(i / len(a) - j / len(b)))
    return maximum


def _array_statistics(lpfs: Sequence[int], X: int, reference: Sequence[float]) -> dict:
    z_values = [math.log(max(1, value)) / math.log(X) for value in lpfs]
    top = sorted(z_values, reverse=True)
    return {
        "ks_two_sided_against_first_iid": _ks_two_sided(z_values, reference),
        "smooth_rates": {str(u): sum(value**u <= X for value in lpfs) / len(lpfs) for u in (2, 3, 4, 5)},
        "top_z_means": {str(k): sum(top[:k]) / k for k in (1, 8, 64, 512)},
    }


def _load_lpfs(first_index: int, last_index_exclusive: int) -> list[int]:
    values = []
    if first_index >= last_index_exclusive:
        return values
    first_shard = first_index // RECORDS_PER_SHARD
    last_shard = (last_index_exclusive - 1) // RECORDS_PER_SHARD
    for shard_index in range(first_shard, last_shard + 1):
        path = REPO_ROOT / SHARD_RELATIVE_PATHS[shard_index]
        with gzip.open(path, "rb") as handle:
            for line in handle:
                record = json.loads(line)
                index = record["sequential_index"]
                if first_index <= index < last_index_exclusive:
                    if not verify_alleged_factors(record["N"], record["sorted_factors"]):
                        raise IntegrityError("resume certificate reconstruction failed")
                    values.append(record["LPF"])
    if len(values) != last_index_exclusive - first_index:
        raise IntegrityError("resume LPF reconstruction count mismatch")
    return values


def _write_provenance_files(resume: bool, device_layout: dict) -> dict:
    import platform
    import sympy

    git_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, check=True,
        capture_output=True, text=True
    ).stdout.strip()
    status_lines = subprocess.run(
        ["git", "status", "--porcelain"], cwd=REPO_ROOT, check=True,
        capture_output=True, text=True
    ).stdout.splitlines()
    roster_strings = {str(path) for path in RUN_EVIDENCE_ROSTER}
    dirty_outside_run_roster = []
    for line in status_lines:
        named = line[3:].split(" -> ")[-1]
        if named not in roster_strings:
            dirty_outside_run_roster.append(line)
    environment = {
        "git_commit": git_sha,
        "git_dirty_outside_exact_run_roster": bool(dirty_outside_run_roster),
        "git_status_outside_exact_run_roster": dirty_outside_run_roster,
        "master_seed_provenance": MASTER_SEED,
        "pre_run_device_layout": device_layout,
        "platform": platform.platform(),
        "python": sys.version,
        "sympy_version": sympy.__version__,
    }
    atomic_bytes(
        repository_path(RUN_REL / "command.txt"),
        (f"python3 {EXP_REL}/implementation/pilot_driver.py run-null-pilot"
         + (" --resume" if resume else "") + "\n").encode(),
    )
    atomic_json(repository_path(RUN_REL / "environment.json"), environment)
    return environment


def run_null_pilot(*, resume: bool = False) -> dict:
    """Run the one frozen null-only pilot at its exact repository paths."""
    validate_repository_binding()
    manifest_path = repository_path(RUN_REL / "manifest.yaml")
    certificate_dir = (REPO_ROOT / CERT_REL).resolve()
    event_history: list[dict] = []
    array_results: list[dict] = []
    cell_resources: dict[str, dict] = {}
    prior_wall = prior_cpu = 0.0
    prior_peak_rss = 0
    primality_checks = 0
    resume_count = 0
    saved_entries: list[dict] = []

    if resume:
        if not manifest_path.is_file():
            raise IntegrityError("resume requested without checkpoint")
        checkpoint = json.loads(manifest_path.read_text())
        if checkpoint.get("status") not in (
            "running_checkpoint", "failed_infrastructure_or_budget"
        ):
            raise IntegrityError("checkpoint status is not resumable")
        if checkpoint.get("resume_count") != 0:
            raise IntegrityError("exactly one resume already consumed")
        saved_entries = checkpoint["completed_shards"]
        primality_checks = checkpoint["primality_checks"]
        prior_wall = checkpoint["wall_seconds"]
        prior_cpu = checkpoint["cpu_seconds"]
        prior_peak_rss = checkpoint["peak_rss_bytes"]
        event_history = checkpoint.get(
            "event_history", checkpoint.get("checkpoint_events", [])
        )
        array_results = checkpoint.get("array_results", [])
        cell_resources = checkpoint.get("cell_resources", {})
        resume_count = 1
    else:
        forbidden_existing = [
            relative for relative in RUN_EVIDENCE_ROSTER
            if (REPO_ROOT / relative).exists()
            and relative not in (RUN_REL / "stdout.log", RUN_REL / "stderr.log")
        ]
        if forbidden_existing:
            raise IntegrityError("fresh run would overwrite frozen evidence paths")
        for log_relative in (RUN_REL / "stdout.log", RUN_REL / "stderr.log"):
            log_path = REPO_ROOT / log_relative
            if not log_path.is_file():
                raise IntegrityError(
                    f"runner must redirect exact log path before execution: {log_relative}"
                )

    validate_log_redirections()
    device_layout = measure_device_layout()
    environment: dict = {}
    monitor = ProcessTreeMonitor(
        maximum_cpu_seconds=max(0.0, MAX_CPU_SECONDS - prior_cpu),
        maximum_rss_bytes=MAX_RSS_BYTES,
    )
    started = time.monotonic()
    active_cell_key: str | None = None
    last_cell_wall = time.monotonic()
    last_cell_cpu = 0.0
    writer: CertificateShardWriter | None = None

    if resume:
        append_ordered_event(
            event_history,
            "resume",
            cpu_seconds=prior_cpu,
            next_deterministic_index=len(saved_entries) * RECORDS_PER_SHARD,
            outcome="resume_started",
            peak_rss_bytes=prior_peak_rss,
            resume_count=resume_count,
            wall_seconds=prior_wall,
        )
        checkpoint["event_history"] = event_history
        checkpoint["resume_count"] = resume_count
        checkpoint["status"] = "running_checkpoint"
        atomic_json(manifest_path, checkpoint)

    def checkpoint_callback(entries: list[dict], next_index: int) -> None:
        nonlocal last_cell_wall, last_cell_cpu
        resource_sample = monitor.sample()
        cumulative_cpu = prior_cpu + resource_sample["cpu_seconds"]
        cumulative_wall = prior_wall + time.monotonic() - started
        if cumulative_wall > MAX_WALL_SECONDS:
            raise ResourceCapError("wall-clock cap exceeded")
        if active_cell_key is not None:
            cell = cell_resources.setdefault(active_cell_key, {
                "cpu_seconds": 0.0, "factorizations": 0,
                "logical_certificate_bytes": 0, "compressed_certificate_bytes": 0,
                "wall_seconds": 0.0,
            })
            cell["wall_seconds"] += time.monotonic() - last_cell_wall
            cell["cpu_seconds"] += max(0.0, resource_sample["cpu_seconds"] - last_cell_cpu)
            cell["factorizations"] = next_index - sum(
                value["factorizations"] for key, value in cell_resources.items()
                if key != active_cell_key
            )
            cell["compressed_certificate_bytes"] = sum(
                entry["compressed_bytes"] for entry in entries
                if _cell_key_for_shard(entry["shard_index"]) == active_cell_key
            )
            cell["logical_certificate_bytes"] = sum(
                entry["logical_bytes"] for entry in entries
                if _cell_key_for_shard(entry["shard_index"]) == active_cell_key
            )
            last_cell_wall = time.monotonic()
            last_cell_cpu = resource_sample["cpu_seconds"]
        storage = measure_run_storage()
        enforce_storage_caps(storage)
        event = append_ordered_event(
            event_history,
            "checkpoint",
            completed_shard_count=len(entries),
            cpu_seconds=cumulative_cpu,
            disk_bytes=storage,
            next_deterministic_index=next_index,
            no_network_guard_enforced=True,
            observed_maximum_process_output_handles=OUTPUT_HANDLES.observed_maximum,
            outcome="running_checkpoint",
            peak_rss_bytes=max(prior_peak_rss, resource_sample["peak_rss_bytes"]),
            resume_count=resume_count,
            wall_seconds=cumulative_wall,
            device_layout=measure_device_layout(enforce_gate=False),
        )
        atomic_json(manifest_path, {
            "array_results": array_results,
            "cell_resources": cell_resources,
            "checkpoint_events": [
                item for item in event_history if item["event_type"] == "checkpoint"
            ],
            "completed_shards": entries,
            "cpu_seconds": cumulative_cpu,
            "experiment_id": EXPERIMENT_ID,
            "event_history": event_history,
            "next_deterministic_index": next_index,
            "peak_rss_bytes": event["peak_rss_bytes"],
            "primality_checks": primality_checks,
            "resume_count": resume_count,
            "run_id": RUN_ID,
            "status": "running_checkpoint",
            "wall_seconds": cumulative_wall,
        })

    try:
        with no_network_guard():
            if (
                prior_cpu >= MAX_CPU_SECONDS
                or prior_wall >= MAX_WALL_SECONDS
                or prior_peak_rss > MAX_RSS_BYTES
            ):
                raise ResourceCapError("cumulative resume budget already exhausted")
            environment = _write_provenance_files(resume, device_layout)
            seed_roster = build_seed_roster()
            atomic_json(repository_path(RESULT_REL / "seed_roster.json"), seed_roster)
            writer = CertificateShardWriter(
                certificate_dir,
                checkpoint_callback=checkpoint_callback,
                enforce_repository_paths=True,
            )
            if saved_entries:
                writer.restore_verified(saved_entries)
                writer.reconcile_to_verified()
            resume_index = writer.total_records
            global_index = 0
            iid_references: dict[tuple[int, int], list[float]] = {}

            for descriptor in array_descriptors():
                active_cell_key = f"{descriptor.bits}:{descriptor.null_type}"
                last_cell_wall = time.monotonic()
                last_cell_cpu = monitor.sample()["cpu_seconds"]
                array_start = global_index
                array_end = array_start + RECORDS_PER_ARRAY
                completed_end = min(max(resume_index, array_start), array_end)
                lpfs = _load_lpfs(array_start, completed_end)
                indexed_values = []
                for draw, value, _commitment in iter_array_values(descriptor):
                    index = array_start + draw
                    if index >= resume_index:
                        indexed_values.append((index, value))
                for record, checks, worker_pid, worker_cpu, worker_rss in _bounded_ordered_factorizations(indexed_values):
                    record_sample = monitor.observe_worker_record(
                        worker_pid, worker_cpu, worker_rss
                    )
                    record_resources = cumulative_resources(
                        prior_cpu,
                        prior_wall,
                        prior_peak_rss,
                        record_sample,
                        time.monotonic() - started,
                    )
                    if record_resources["wall_seconds"] > MAX_WALL_SECONDS:
                        raise ResourceCapError("wall-clock cap exceeded")
                    primality_checks += checks
                    if primality_checks > MAX_PRIMALITY_CHECKS:
                        raise ResourceCapError("global primality-check cap exceeded")
                    writer.write(record)
                    lpfs.append(record["LPF"])
                if len(lpfs) != RECORDS_PER_ARRAY:
                    raise IntegrityError("array reconstruction count mismatch")
                key = (descriptor.bits, descriptor.fixture)
                z_values = [
                    math.log(max(1, value)) / math.log(descriptor.X) for value in lpfs
                ]
                if descriptor.null_type == "NULL-IID-EDGE" and descriptor.replicate == 0:
                    iid_references[key] = z_values
                reference = iid_references.get(key)
                if reference is None:
                    raise IntegrityError("first iid reference unavailable")
                result = {
                    **dataclasses.asdict(descriptor),
                    "X": descriptor.X,
                    "statistics": _array_statistics(lpfs, descriptor.X, reference),
                }
                if len(array_results) <= global_index // RECORDS_PER_ARRAY:
                    array_results.append(result)
                global_index = array_end

            entries = writer.finish()
            active_cell_key = None
            if global_index != TOTAL_RECORDS or primality_checks > MAX_PRIMALITY_CHECKS:
                raise IntegrityError("final count mismatch")
            resource_sample = monitor.sample()
            storage = measure_run_storage()
            enforce_storage_caps(storage)
            manifest = {
                "aggregate_below_tracked_cap": sum(item["compressed_bytes"] for item in entries) <= MAX_SHARD_AGGREGATE_BYTES,
                "entries": entries,
                "every_object_below_github_limit": all(item["compressed_bytes"] <= SHARD_CAP_BYTES for item in entries),
                "exact_path_roster_sha256": hashlib.sha256(canonical_json_bytes([str(path) for path in SHARD_RELATIVE_PATHS])).hexdigest(),
                "total_compressed_bytes": sum(item["compressed_bytes"] for item in entries),
                "total_logical_bytes": sum(item["logical_bytes"] for item in entries),
                "total_records": sum(item["record_count"] for item in entries),
            }
            atomic_json(repository_path(CERT_REL / "shard_manifest.json"), manifest)
            total_wall = prior_wall + time.monotonic() - started
            total_cpu = prior_cpu + resource_sample["cpu_seconds"]
            append_ordered_event(
                event_history,
                "complete",
                cpu_seconds=total_cpu,
                next_deterministic_index=TOTAL_RECORDS,
                outcome="completed_feasibility_only",
                peak_rss_bytes=max(
                    prior_peak_rss, resource_sample["peak_rss_bytes"]
                ),
                resume_count=resume_count,
                wall_seconds=total_wall,
            )
            rates = {}
            bytes_per_certificate = {}
            for key, cell in sorted(cell_resources.items()):
                rates[key] = {
                    "per_cpu_second": cell["factorizations"] / cell["cpu_seconds"] if cell["cpu_seconds"] else None,
                    "per_wall_second": cell["factorizations"] / cell["wall_seconds"] if cell["wall_seconds"] else None,
                }
                bytes_per_certificate[key] = {
                    "compressed": cell["compressed_certificate_bytes"] / cell["factorizations"] if cell["factorizations"] else None,
                    "logical": cell["logical_certificate_bytes"] / cell["factorizations"] if cell["factorizations"] else None,
                }
            multiplier = FULL_V2_FACTORING_SUBTOTAL / TOTAL_RECORDS
            result = {
                "array_results": array_results,
                "certificate_bytes_per_factorization_by_bits_and_null_type": bytes_per_certificate,
                "checkpoint_events": [
                    item for item in event_history
                    if item["event_type"] == "checkpoint"
                ],
                "cpu_seconds": total_cpu,
                "dependency_provenance": environment,
                "disk_bytes_by_phase_and_total": {"run_phase_final": storage, "total_physical_bytes": storage["physical_run_bytes"]},
                "experiment_id": EXPERIMENT_ID,
                "event_history": event_history,
                "factorization_calls": global_index,
                "factorizations_per_second_by_bits_and_null_type": rates,
                "peak_rss_bytes": max(prior_peak_rss, resource_sample["peak_rss_bytes"]),
                "primality_checks": primality_checks,
                "projected_v2_full_contract": {
                    "factorization_count": FULL_V2_FACTORING_SUBTOTAL,
                    "modeled_cpu_seconds": total_cpu * multiplier,
                    "modeled_disk_bytes": storage["tracked_bytes"] * multiplier,
                    "modeled_wall_seconds": total_wall * multiplier,
                    "optimistic_linearity_caveat": "Linear scaling from this null-only pilot; excludes rejection draws, retries, orchestration and non-factorization full-contract costs.",
                },
                "reconstructions": global_index,
                "resume_count": resume_count,
                "no_network_guard_enforced": True,
                "observed_maximum_process_output_handles": OUTPUT_HANDLES.observed_maximum,
                "scientific_scope": "null-only feasibility; nondecisional",
                "resume_events": [
                    item for item in event_history if item["event_type"] == "resume"
                ],
                "stops": [
                    item for item in event_history if item["event_type"] == "stop"
                ],
                "sympy_version": environment["sympy_version"],
                "wall_seconds": total_wall,
            }
            final_manifest = json.loads(manifest_path.read_text())
            final_manifest.update({
                "event_history": event_history,
                "status": "completed_feasibility_only",
            })
            result_paths = (
                repository_path(RUN_REL / "raw-result.json"),
                repository_path(RESULT_REL / "feasibility_report.json"),
            )
            preterminal_missing = [
                str(relative) for relative in RUN_EVIDENCE_ROSTER
                if not (REPO_ROOT / relative).is_file()
                and relative not in (
                    RUN_REL / "raw-result.json",
                    RESULT_REL / "feasibility_report.json",
                )
            ]
            if preterminal_missing:
                raise IntegrityError(
                    f"required preterminal paths missing: {preterminal_missing}"
                )
            terminal_message = canonical_json_bytes({
                "experiment_id": EXPERIMENT_ID,
                "run_id": RUN_ID,
                "terminal_record": "see manifest",
            }) + b"\n"
            sys.stdout.buffer.write(terminal_message)
            sys.stdout.buffer.flush()
            os.fsync(sys.stdout.fileno())
            finalize_stable_storage_receipt(
                result,
                final_manifest,
                result_paths,
                manifest_path,
                measure_run_storage,
                enforce_storage_caps,
            )
            missing = [
                str(relative) for relative in RUN_EVIDENCE_ROSTER
                if not (REPO_ROOT / relative).is_file()
            ]
            if missing:
                raise IntegrityError(f"terminal evidence paths missing: {missing}")
            return result
    except BaseException as exc:
        if writer is not None:
            writer.abort_current()
            writer.reconcile_to_verified()
        failure = {}
        if manifest_path.exists():
            try:
                failure = json.loads(manifest_path.read_text())
            except (json.JSONDecodeError, OSError):
                failure = {}
        status, failure_class = classify_failure(exc)
        try:
            failed_sample = monitor.sample(enforce=False)
        except BaseException:
            failed_sample = monitor.accounting_without_subprocess()
        charged = cumulative_resources(
            prior_cpu,
            prior_wall,
            prior_peak_rss,
            failed_sample,
            time.monotonic() - started,
        )
        next_index = len(writer.entries if writer else saved_entries) * RECORDS_PER_SHARD
        append_ordered_event(
            event_history,
            "stop",
            cpu_seconds=charged["cpu_seconds"],
            error_class=type(exc).__name__,
            failure_class=failure_class,
            next_deterministic_index=next_index,
            outcome=status,
            peak_rss_bytes=charged["peak_rss_bytes"],
            resume_count=resume_count,
            wall_seconds=charged["wall_seconds"],
        )
        failure.update({
            "completed_shards": list(writer.entries) if writer else saved_entries,
            "cpu_seconds": charged["cpu_seconds"],
            "error_class": type(exc).__name__,
            "error_message": str(exc),
            "event_history": event_history,
            "experiment_id": EXPERIMENT_ID,
            "failure_class": failure_class,
            "next_deterministic_index": next_index,
            "peak_rss_bytes": charged["peak_rss_bytes"],
            "primality_checks": primality_checks,
            "resume_count": resume_count,
            "status": status,
            "stop_events": [
                item for item in event_history if item["event_type"] == "stop"
            ],
            "wall_seconds": charged["wall_seconds"],
        })
        atomic_json(manifest_path, failure)
        raise


def _cell_key_for_shard(shard_index: int) -> str:
    descriptor = array_descriptors()[shard_index // 4]
    return f"{descriptor.bits}:{descriptor.null_type}"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    test = subparsers.add_parser("self-test", help="run bounded synthetic tests only")
    test.add_argument("--only", action="append", default=[], help="run one named synthetic test")
    run = subparsers.add_parser("run-null-pilot", help="run the frozen null-only pilot")
    run.add_argument("--resume", action="store_true", help="consume the single deterministic resume")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    if arguments.command == "self-test":
        print(json.dumps(run_self_tests(set(arguments.only) or None), sort_keys=True, indent=2))
        return 0
    if arguments.command == "run-null-pilot":
        run_null_pilot(resume=arguments.resume)
        return 0
    raise AssertionError("unreachable")


if __name__ == "__main__":
    raise SystemExit(main())
