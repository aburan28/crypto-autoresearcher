#!/usr/bin/env python3
"""Null-only EXP-SMTH-PILOT-001 implementation and bounded pack sink.

This module deliberately has no curve, factor-base, S3, source, plant,
p-value, evidence, or research-state interface.  ``self-test`` uses only tiny
synthetic inputs.  ``run-null-pilot`` is the sole scientific entry point and
must not be invoked without a successor execution authorization.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import dataclasses
import gzip
import hashlib
import io
import json
import math
import os
from pathlib import Path
import resource
import shutil
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

assert RECORDS_PER_ARRAY == 130_816
assert TOTAL_RECORDS == 4_186_112
assert RECORDS_PER_SHARD * SHARD_COUNT == TOTAL_RECORDS


class IntegrityError(RuntimeError):
    """The deterministic construction or a certificate failed validation."""


class ResourceCapError(RuntimeError):
    """A frozen physical or computational ceiling was reached."""


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
    payload = canonical_json_bytes(value) + b"\n"
    if len(payload) > MAX_OTHER_FILE_BYTES:
        raise ResourceCapError(f"other artifact exceeds cap: {path}")
    partial = path.with_name(path.name + ".partial")
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
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
        raise RuntimeError("sympy is required") from exc
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
    """Yield (draw index, N, draw seed) in the frozen i<j order."""
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
            # The edge seed commits to the two independently seeded endpoints.
            edge_seed = hashlib.sha256(
                b"NULL-K512-ADD-EDGE|" + seeds[i][0] + seeds[i][1]
                + seeds[j][0] + seeds[j][1]
            ).digest()[:16]
            value = (
                ((a_values[i] + a_values[j]) % descriptor.p) * descriptor.p
                + ((b_values[i] + b_values[j]) % descriptor.p)
                + 1
            )
            yield draw, value, edge_seed
            draw += 1
    if draw != RECORDS_PER_ARRAY:
        raise IntegrityError("K512 edge count mismatch")


def verify_alleged_factors(N: int, factors: Sequence[Sequence[int]]) -> bool:
    try:
        from sympy import isprime
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("sympy is required") from exc
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
        raise RuntimeError("sympy is required") from exc
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
        self.raw.flush()


class CertificateShardWriter:
    def __init__(self, certificate_dir: Path):
        self.directory = certificate_dir
        self.directory.mkdir(parents=True, exist_ok=True)
        self.entries: list[dict] = []
        self.shard_index = -1
        self.record_count = 0
        self.total_records = 0
        self.logical_bytes = 0
        self._raw: BinaryIO | None = None
        self._capped: CappedRawWriter | None = None
        self._gzip: gzip.GzipFile | None = None
        self._partial: Path | None = None

    def _open(self) -> None:
        if self._gzip is not None:
            raise IntegrityError("multiple shard handles")
        self.shard_index += 1
        if self.shard_index >= SHARD_COUNT:
            raise IntegrityError("too many shards")
        final = self.directory / f"shard-{self.shard_index:03d}.jsonl.gz"
        partial = final.with_name(final.name + ".partial")
        partial.unlink(missing_ok=True)
        self._raw = partial.open("xb")
        self._capped = CappedRawWriter(self._raw, SHARD_CAP_BYTES)
        self._gzip = gzip.GzipFile(
            filename="", mode="wb", fileobj=self._capped, mtime=0
        )
        self._partial = partial
        self.record_count = 0
        self.logical_bytes = 0

    def write(self, record: dict) -> None:
        if self._gzip is None:
            self._open()
        if record["sequential_index"] != self.total_records:
            raise IntegrityError("non-sequential certificate record")
        payload = canonical_json_bytes(record) + b"\n"
        if len(payload) > RECORD_CAP_BYTES:
            raise IntegrityError("certificate logical record exceeds cap")
        try:
            assert self._gzip is not None
            self._gzip.write(payload)
        except BaseException:
            self.abort_current()
            raise
        self.record_count += 1
        self.total_records += 1
        self.logical_bytes += len(payload)
        if self.record_count == RECORDS_PER_SHARD:
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
            if self.record_count != RECORDS_PER_SHARD:
                raise IntegrityError("non-full certificate shard")
            compressed = partial.stat().st_size
            if compressed != capped.bytes_written or compressed > SHARD_CAP_BYTES:
                raise ResourceCapError("shard byte accounting mismatch")
            os.replace(partial, final)
            fsync_directory(self.directory)
            self.entries.append(
                {
                    "compressed_bytes": compressed,
                    "first_record_index": self.total_records - self.record_count,
                    "gzip_sha256": sha256_file(final),
                    "last_record_index": self.total_records - 1,
                    "logical_bytes": self.logical_bytes,
                    "record_count": self.record_count,
                    "repository_relative_path": str(final),
                    "shard_index": self.shard_index,
                }
            )
        except BaseException:
            partial.unlink(missing_ok=True)
            raise
        finally:
            self._gzip = None
            self._raw = None
            self._capped = None
            self._partial = None

    def abort_current(self) -> None:
        gzip_handle, raw, partial = self._gzip, self._raw, self._partial
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
        if partial is not None:
            partial.unlink(missing_ok=True)

    def finish(self) -> list[dict]:
        if self._gzip is not None:
            self.close_current()
        if self.total_records != TOTAL_RECORDS or len(self.entries) != SHARD_COUNT:
            raise IntegrityError("final shard or record count mismatch")
        if sum(entry["compressed_bytes"] for entry in self.entries) > MAX_SHARD_AGGREGATE_BYTES:
            raise ResourceCapError("aggregate shard cap exceeded")
        return self.entries


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


def _synthetic_producer(length: int, exit_status: int = 0) -> list[str]:
    code = (
        "import sys; n=int(sys.argv[1]); status=int(sys.argv[2]); "
        "sys.stdout.buffer.write(b'x'*n); sys.stdout.buffer.flush(); "
        "raise SystemExit(status)"
    )
    return [sys.executable, "-c", code, str(length), str(exit_status)]


def run_self_tests() -> dict:
    tests: list[dict] = []

    def check(name: str, function: Callable[[], None]) -> None:
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
            assert not verify_alleged_factors(12, [[2, 1], [6, 1]])
            oversized = dict(record)
            oversized["padding"] = "x" * 1025
            assert len(canonical_json_bytes(oversized)) > RECORD_CAP_BYTES

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

        check("bounded-pack-exact-cap", exact_cap)
        check("bounded-pack-cap-plus-one", cap_plus_one)
        check("bounded-pack-producer-failure", producer_failure)
        check("split-device-accounting", split_device)
        check("factor-certificate-controls", certificate_controls)
        check("deterministic-null-plumbing", deterministic_nulls)

    return {"scientific_runs": 0, "status": "pass", "tests": tests}


def _bounded_ordered_factorizations(
    indexed_values: Iterable[tuple[int, int]],
) -> Iterator[tuple[dict, int]]:
    with concurrent.futures.ProcessPoolExecutor(max_workers=WORKERS) as pool:
        pending: dict[int, concurrent.futures.Future] = {}
        source = iter(indexed_values)
        submit_index = 0
        yield_index = 0
        exhausted = False
        while pending or not exhausted:
            while not exhausted and len(pending) < QUEUE_RECORDS:
                try:
                    index, value = next(source)
                except StopIteration:
                    exhausted = True
                    break
                if index != submit_index:
                    raise IntegrityError("input index discontinuity")
                pending[index] = pool.submit(factor_certificate, index, value)
                submit_index += 1
            if yield_index in pending:
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


def run_null_pilot(output_root: Path) -> dict:
    """Run the one frozen null-only pilot. Caller must enforce authorization."""
    started_wall = time.monotonic()
    started_cpu = time.process_time()
    certificates = output_root / "results" / "certificates"
    writer = CertificateShardWriter(certificates)
    primality_checks = 0
    seed_seen: set[bytes] = set()
    seed_collisions = 0
    stream_roster = []
    array_results = []
    iid_references: dict[tuple[int, int], list[float]] = {}
    global_index = 0

    for descriptor in array_descriptors():
        stream_hash = hashlib.sha256()
        values: list[tuple[int, int]] = []
        for _, value, seed in iter_array_values(descriptor):
            stream_hash.update(seed)
            if seed in seed_seen:
                seed_collisions += 1
            seed_seen.add(seed)
            values.append((global_index + len(values), value))
        stream_roster.append({
            "bits": descriptor.bits,
            "fixture": descriptor.fixture,
            "null_type": descriptor.null_type,
            "replicate": descriptor.replicate,
            "draw_count": len(values),
            "ordered_seed_stream_sha256": stream_hash.hexdigest(),
        })
        lpfs = []
        for record, checks in _bounded_ordered_factorizations(values):
            writer.write(record)
            lpfs.append(record["LPF"])
            primality_checks += checks
            if primality_checks > MAX_PRIMALITY_CHECKS:
                raise ResourceCapError("global primality-check cap exceeded")
            if time.monotonic() - started_wall > MAX_WALL_SECONDS:
                raise ResourceCapError("wall-clock cap exceeded")
            if time.process_time() - started_cpu > MAX_CPU_SECONDS:
                raise ResourceCapError("CPU cap exceeded")
            rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            rss_bytes = rss if sys.platform == "darwin" else rss * 1024
            if rss_bytes > MAX_RSS_BYTES:
                raise ResourceCapError("RSS cap exceeded")
        key = (descriptor.bits, descriptor.fixture)
        z_values = [math.log(max(1, value)) / math.log(descriptor.X) for value in lpfs]
        if descriptor.null_type == "NULL-IID-EDGE" and descriptor.replicate == 0:
            iid_references[key] = z_values
        reference = iid_references.get(key)
        if reference is None:
            raise IntegrityError("first iid reference is unavailable")
        array_results.append({
            **dataclasses.asdict(descriptor),
            "X": descriptor.X,
            "statistics": _array_statistics(lpfs, descriptor.X, reference),
        })
        global_index += len(values)

    entries = writer.finish()
    if global_index != TOTAL_RECORDS or seed_collisions:
        raise IntegrityError("record count or seed collision failure")
    roster_without_hash = {
        "collision_count": seed_collisions,
        "domain": DOMAIN,
        "master_seed_recorded": MASTER_SEED,
        "seed_rule": "first_128_bits(SHA256(domain|object|bits|fixture|replicate|draw))",
        "streams": stream_roster,
    }
    roster = dict(roster_without_hash)
    roster["canonical_payload_sha256"] = hashlib.sha256(canonical_json_bytes(roster_without_hash)).hexdigest()
    manifest = {
        "aggregate_below_tracked_cap": sum(item["compressed_bytes"] for item in entries) <= MAX_SHARD_AGGREGATE_BYTES,
        "entries": entries,
        "every_object_below_github_limit": all(item["compressed_bytes"] <= SHARD_CAP_BYTES for item in entries),
        "exact_path_roster_sha256": hashlib.sha256(canonical_json_bytes([item["repository_relative_path"] for item in entries])).hexdigest(),
        "total_compressed_bytes": sum(item["compressed_bytes"] for item in entries),
        "total_logical_bytes": sum(item["logical_bytes"] for item in entries),
        "total_records": sum(item["record_count"] for item in entries),
    }
    atomic_json(output_root / "results" / "seed_roster.json", roster)
    atomic_json(certificates / "shard_manifest.json", manifest)
    result = {
        "array_results": array_results,
        "cpu_seconds": time.process_time() - started_cpu,
        "experiment_id": EXPERIMENT_ID,
        "factorization_calls": global_index,
        "primality_checks": primality_checks,
        "reconstructions": global_index,
        "scientific_scope": "null-only feasibility; nondecisional",
        "wall_seconds": time.monotonic() - started_wall,
    }
    atomic_json(output_root / "results" / "feasibility_report.json", result)
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("self-test", help="run bounded synthetic tests only")
    run = subparsers.add_parser("run-null-pilot", help="run the frozen null-only pilot")
    run.add_argument("--output-root", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    if arguments.command == "self-test":
        print(json.dumps(run_self_tests(), sort_keys=True, indent=2))
        return 0
    if arguments.command == "run-null-pilot":
        print(json.dumps(run_null_pilot(arguments.output_root), sort_keys=True, indent=2))
        return 0
    raise AssertionError("unreachable")


if __name__ == "__main__":
    raise SystemExit(main())
