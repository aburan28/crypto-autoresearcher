#!/usr/bin/env python3
"""Run the frozen m=51 deep-volcano discovery scan.

Scientific execution is deliberately narrow: 256 fixed, indexed shards cover
exactly ``[0, 3_600_000_000)``; four scanner processes are pinned to CPUs
0--3; and exact classification is serialized in global-index order.  Every
rank is scanned and every sieve hit is classified even after the first 32
certified pairs with distinct parent and child Frobenius orbits are selected.
Duplicate or pilot-orbit recoveries never count.

Point-count, conductor, and isogeny certification belong to ``pipeline.py``.
This runner treats that program as an independently frozen subprocess with
the following interface::

    python3 pipeline.py classify --hits HITS.csv --out OUT --gp-bin GP

``OUT/records.jsonl`` must contain one globally ordered record for every sieve
hit, ``OUT/pairs.jsonl`` contains certified parent/child pairs, and
``OUT/selection.json`` contains the pipeline's local first-distinct selection.
All three are checked before their directory becomes immutable.

Completed build, shard, and classification directories are write-once and
sealed.  Failed attempts remain under ``attempts/`` and a later invocation can
resume without overwriting them.  A root ``MANIFEST.sha256`` is written only
for a terminal successful orchestration result (quota met, fixed range
exhausted, or mock complete).

``--mock`` exercises build, pinning, parallel chunk orchestration, resume, and
sealing with four tiny ``mock-scan`` shards.  Its deliberately incompatible
CSV schema and singular ``b=0`` fixtures are never sent to the scientific
pipeline and can never be accepted as scientific evidence.
"""

from __future__ import annotations

import argparse
import csv
import ctypes
import errno
import fcntl
import hashlib
import json
import math
import os
import platform
import re
import shlex
import shutil
import signal
import stat
import struct
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]

SCI_START = 0
SCI_END = 3_600_000_000
SCI_SHARDS = 256
SCI_SHARD_SIZE = 14_062_500
SCI_ROOT_SEED = 202_610_135_201
WORKERS = 4
CORES = (0, 1, 2, 3)
TARGET_PAIRS = 32
CLASSIFICATION_CERTIFICATE_BASE = "classification/payload"
SHARD_TIMEOUT_SECONDS = 1800
BUILD_TIMEOUT_SECONDS = 120
PIPELINE_TIMEOUT_SECONDS = 604_800
CONTROLS_TIMEOUT_SECONDS = 1800
PINNED_GP_IMAGE_ID = "sha256:7436527cbf48e6e00a4b574c31725a90d5802160fb817a8f6bd94128d95a3cd4"
PINNED_GP_BINARY_SHA256 = "35b1fc1911407f5e893f5ab6b683ac660d164d5d84223b1d38645ebc96d43379"
EXPECTED_SPEC_CANONICAL_SHA256 = "a3d08bf8e836fc474c2436548eb5b1430a5fe10f9d27eef8c82620c6907bbd43"
GP_CONTAINER_CPUSET = "0"
GP_CONTAINER_MEMORY = "12g"
GP_CONTAINER_NETWORK = "none"

MOCK_START = 0
MOCK_SHARDS = 4
MOCK_SHARD_SIZE = 8

FIELD_BITS = 51
FIELD_SIZE = 1 << FIELD_BITS
FIELD_MASK = FIELD_SIZE - 1
UINT64_MASK = (1 << 64) - 1
HASSE_RADIUS = math.isqrt(4 * FIELD_SIZE)
HASSE_MIN = FIELD_SIZE + 1 - HASSE_RADIUS
HASSE_MAX = FIELD_SIZE + 1 + HASSE_RADIUS
FIELD_ORBIT_SIZES = {1, 3, 17, 51}
AMBIENT_ORDER = 2_251_799_852_369_764
F_PI = 32_756_041
PILOT_BOTTOM_ORBIT_REP = 99_224_513_745_505
PILOT_PARENT_ORBIT_REP = 7_746_411_922_983
PILOT_BOTTOM_RAW_B = 675_235_026_289_400
EXPECTED_F271 = (
    623_162_416_261,
    25_640_824_825_979,
    30_885_819_784_827,
    57_318_330_399_736,
    67_694_307_705_004,
    72_881_269_935_803,
    115_635_957_935_040,
    116_461_223_646_592,
    116_511_665_573_478,
    121_360_481_466_206,
    130_246_110_195_364,
    147_686_731_444_433,
    213_718_369_432_541,
    237_711_860_122_495,
    360_860_333_097_189,
    370_376_419_722_289,
)
PRP_ZERO_PREIMAGE = 1_143_900_985_707_342
PRP_DERIVED_KEY_HEX = "c6ac26c5f692baa74a02c14f38de8e93bfe40c2d2ecbdcf7231ac6e79049d7b2"
FEISTEL_KEYS = (
    0x824FED8E0FDE5218,
    0x00B2A56B05421B2D,
    0xFD0F52502A0D3737,
    0x78CDB4C19DD24202,
    0x722CFEF7C6D0EA93,
    0xE007ABB4C970F252,
    0xA56276B6D4746BED,
    0x08E8F877EC4098BC,
    0x02EA18FD04E1DD08,
    0xEFB6477DE16EC1DA,
    0xAF1A485BBAF930E9,
    0xC80FF63F19D1D47C,
)

SEARCH_HEADER = ("global_index", "b", "x0", "x1", "x2")
MOCK_HEADER = ("record_kind", *SEARCH_HEADER)
RECORD_FIELDS = {
    "schema",
    *SEARCH_HEADER,
    "source_hit",
    "status",
    "admitted_failure",
    "control_mode",
    "certificate_path",
    "certificate_sha256",
    "certificate_bytes",
}
PAIR_FIELDS = (
    "schema",
    "global_index",
    "b",
    "a2",
    "ellcard",
    "bottom_orbit_rep",
    "bottom_orbit_size",
    "parent_b",
    "parent_a2",
    "parent_orbit_rep",
    "parent_orbit_size",
    "status",
    "source_hit",
    "certificate_path",
    "certificate_sha256",
)
PAIR_SCHEMA = "m51-deep-pair/v1"
SELECTION_SCHEMA = "m51-deep-selection/v1"
BENIGN_STATUSES = {
    "SIEVE_FALSE_POSITIVE_ORDER",
    "KNOWN_CRATER",
    "KNOWN_F271",
    "EXCLUDED_PILOT_ORBIT",
    "DIRECT_PARENT",
    "CERTIFIED_BOTTOM_PARENT",
}
FATAL_STATUSES = {
    "UNKNOWN_WITNESS_EXHAUSTED",
    "UNKNOWN_EMBEDDING_EXHAUSTED",
    "TARGET_RANK2_WITNESS_EXHAUSTED",
    "INVALID_CERTIFICATE",
    "ASCENT_FAILED",
    "WRONG_ORBIT_SIZE",
    "WRONG_PARENT_ORDER",
    "GP_ERROR",
}
POSITIVE_CONTROL_IDS = (
    "positive-f271-ascent",
    "positive-bottom-ascent",
    "positive-parent-rank2",
)
NEGATIVE_CONTROL_IDS = (
    "crater-exclusion",
    *(f"f271-exclusion-{number:02d}" for number in range(1, 17)),
    "pilot-source-exclusion",
)
CONTROL_IDS = (*NEGATIVE_CONTROL_IDS, *POSITIVE_CONTROL_IDS)
CONTROL_EXPECTED_STATUSES = {
    "crater-exclusion": "KNOWN_CRATER",
    **{
        f"f271-exclusion-{number:02d}": "KNOWN_F271"
        for number in range(1, 17)
    },
    "pilot-source-exclusion": "EXCLUDED_PILOT_ORBIT",
    "positive-f271-ascent": "POSITIVE_CONTROL_F271_TO_CRATER",
    "positive-bottom-ascent": "POSITIVE_CONTROL_BOTTOM_PARENT",
    "positive-parent-rank2": "DIRECT_PARENT",
}
CONTROL_MODES = {
    **{control_id: 0 for control_id in NEGATIVE_CONTROL_IDS},
    "positive-f271-ascent": 2,
    "positive-bottom-ascent": 1,
    "positive-parent-rank2": 0,
}
CENSUS_SOURCE_REVISION = "f0bdf9f739462766a9060532c59f9bfed69d00b1"
CENSUS_SOURCE_SHA256 = "a73ef01d0cb78be9f1c3df131c5598eae394541ce85a55fab5b33efaeca8d91b"
GP_STACK = "2G"
EMBED_SEED = 6_199_165_538_745_411_260
WITNESS_COUNT = 3
MAX_WITNESS_ATTEMPTS = 4096
MAX_CERT_DECIMAL_DIGITS = 4096
EXTENSION_MODULUS_DECIMAL_SHA256 = (
    "b0772b1c800814fefedd8eaf83e67c797649334ae701518e41f93a1200986d90"
)
EMBEDDING_X_DECIMAL_SHA256 = (
    "97b69f5f34d9aaaa8257a88fd5a9ca46c9a2618fc7b59145e81427175778573a"
)
GP_CHILD_ENV = {"LANG": "C", "LC_ALL": "C", "TZ": "UTC"}
RUNNER_CHILD_ENV = {
    "LANG": "C",
    "LC_ALL": "C",
    "PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
    "TZ": "UTC",
}
PYTHON_CHILD_FLAGS = ("-I", "-S", "-B")
PROCESS_RECEIPT_FIELDS = {
    "command",
    "cwd",
    "started_utc",
    "finished_utc",
    "elapsed_seconds",
    "exit_status",
    "timed_out",
    "cancelled",
    "environment",
}

CERTIFICATE_ALLOWED_FIELDS = {
    "admitted_failure", "class_discriminant", "class_discriminant_271_valuation",
    "class_trace", "codomain_minpoly_bits", "control_mode",
    "coprime_conductor_component_preserved", "coprime_conductor_preservation_check",
    "direct_parent_point_1_x_int", "direct_parent_point_1_xset",
    "direct_parent_point_1_xset_count",
    "direct_parent_point_2_absent_from_point_1_subgroup",
    "direct_parent_point_2_x_int", "dual_serialized", "edge_degree",
    "edge_direction", "edge_direction_derivation", "edge_separable",
    "embedded_b_int", "embedding_attempts", "embedding_modulus_check",
    "embedding_seed", "embedding_x_int", "expected_order",
    "extension_group_271_valuation", "extension_group_cofactor",
    "extension_modulus_bits", "extension_trace", "f271_census_complete_orbit_count",
    "f271_census_exclusion_role", "f271_census_sha256",
    "f271_census_source_revision", "f271_census_source_sha256", "f_pi",
    "f_pi_factor_primality", "f_pi_factorization", "field_degree",
    "field_modulus_bits", "global_index", "gp_log_sha256",
    "kernel_extension_coprime_to_271", "kernel_extension_degree",
    "kernel_field_degree", "kernel_frobenius_stable",
    "kernel_frobenius_x_multiplier_abs", "kernel_mul_271_zero", "kernel_prime",
    "kernel_sums_agree", "kernel_twist", "kernel_x_int",
    "map_evaluator_serialized", "maximal_order_class_number",
    "normalization_y_translation_int", "other_twist_271_valuation",
    "pilot_exclusion_scope", "pipeline_error", "raw_codomain_a1",
    "raw_codomain_a2", "raw_codomain_a3", "raw_codomain_a4_int",
    "raw_codomain_a6_int", "raw_codomain_delta_int", "raw_codomain_delta_nonzero",
    "raw_codomain_frobenius_fixed", "raw_target_b",
    "raw_target_to_rep_frobenius_power", "schema", "source_a2", "source_b",
    "source_conductor_derivation", "source_f_E", "source_orbit_rep",
    "source_orbit_size", "source_order", "source_to_orbit_rep_frobenius_power",
    "status", "target_a2", "target_b", "target_conductor_derivation", "target_f_E",
    "target_orbit_rep", "target_orbit_size", "target_order",
    "target_rank2_attempts_used", "target_rank2_infinity_skips",
    "target_rank2_other_twist_skips", "target_rank2_point_1_mul_271_zero",
    "target_rank2_point_1_x_int", "target_rank2_point_1_xset",
    "target_rank2_point_1_xset_count",
    "target_rank2_point_2_absent_from_point_1_subgroup",
    "target_rank2_point_2_mul_271_zero", "target_rank2_point_2_x_int",
    "target_witness_seed", "transfer_claim_permitted",
    "velu_half_kernel_sum_frobenius_fixed", "velu_half_kernel_sum_int",
    "witness_attempt_cap", "witness_attempts_used", "witness_count_found",
    "witness_count_required", "witness_infinity_skips", "witness_other_twist_skips",
    "witness_seed",
    *{
        f"witness_{number}_{suffix}"
        for number in range(1, WITNESS_COUNT + 1)
        for suffix in (
            "attempt", "raw_x_int", "order_2712_x_int", "order_271_x_int",
            "mul_271_nonzero", "mul_2712_zero",
        )
    },
}

CERTIFICATE_TERMINAL_FIELDS = {"admitted_failure", "status"}
CERTIFICATE_BASE_FIELDS = CERTIFICATE_TERMINAL_FIELDS | {
    "schema", "global_index", "source_b", "source_a2", "source_order",
    "expected_order", "source_orbit_rep", "source_orbit_size",
    "source_to_orbit_rep_frobenius_power", "field_degree", "field_modulus_bits",
    "class_trace", "class_discriminant", "f_pi", "f_pi_factorization",
    "f_pi_factor_primality", "class_discriminant_271_valuation",
    "kernel_extension_coprime_to_271", "maximal_order_class_number",
    "f271_census_sha256", "f271_census_source_revision",
    "f271_census_source_sha256", "f271_census_complete_orbit_count",
    "control_mode",
}
CERTIFICATE_DEEP_FIELDS = CERTIFICATE_BASE_FIELDS | {
    "kernel_prime", "kernel_field_degree", "kernel_extension_degree", "kernel_twist",
    "extension_trace", "extension_group_271_valuation", "other_twist_271_valuation",
    "extension_group_cofactor", "extension_modulus_bits", "embedding_seed",
    "embedding_attempts", "embedding_x_int", "embedding_modulus_check",
    "embedded_b_int", "witness_seed", "target_witness_seed",
    "witness_count_required", "witness_attempt_cap",
}
CERTIFICATE_WITNESS_SUMMARY_FIELDS = CERTIFICATE_DEEP_FIELDS | {
    "witness_attempts_used", "witness_count_found", "witness_other_twist_skips",
    "witness_infinity_skips",
}
CERTIFICATE_WITNESS_DETAIL_FIELDS = CERTIFICATE_WITNESS_SUMMARY_FIELDS | {
    f"witness_{number}_{suffix}"
    for number in range(1, WITNESS_COUNT + 1)
    for suffix in (
        "attempt", "raw_x_int", "order_2712_x_int", "order_271_x_int",
        "mul_271_nonzero", "mul_2712_zero",
    )
}
CERTIFICATE_DIRECT_PARENT_FIELDS = CERTIFICATE_WITNESS_SUMMARY_FIELDS | {
    "direct_parent_point_1_x_int", "direct_parent_point_2_x_int",
    "direct_parent_point_1_xset_count", "direct_parent_point_1_xset",
    "direct_parent_point_2_absent_from_point_1_subgroup", "source_f_E",
    "source_conductor_derivation",
}
CERTIFICATE_FULL_EDGE_FIELDS = CERTIFICATE_WITNESS_DETAIL_FIELDS | {
    "source_f_E", "source_conductor_derivation", "f271_census_exclusion_role",
    "kernel_x_int", "kernel_mul_271_zero", "kernel_frobenius_x_multiplier_abs",
    "kernel_frobenius_stable", "kernel_sums_agree", "velu_half_kernel_sum_int",
    "velu_half_kernel_sum_frobenius_fixed", "raw_codomain_a1",
    "raw_codomain_a2", "raw_codomain_a3", "raw_codomain_a4_int",
    "raw_codomain_a6_int", "normalization_y_translation_int",
    "raw_codomain_delta_int", "raw_codomain_delta_nonzero",
    "raw_codomain_frobenius_fixed", "raw_target_b", "codomain_minpoly_bits",
    "target_b", "target_a2", "target_order", "target_orbit_rep",
    "target_orbit_size", "raw_target_to_rep_frobenius_power", "target_f_E",
    "target_rank2_attempts_used", "target_rank2_other_twist_skips",
    "target_rank2_infinity_skips", "target_rank2_point_1_x_int",
    "target_rank2_point_2_x_int", "target_rank2_point_1_mul_271_zero",
    "target_rank2_point_2_mul_271_zero", "target_rank2_point_1_xset_count",
    "target_rank2_point_1_xset",
    "target_rank2_point_2_absent_from_point_1_subgroup",
    "target_conductor_derivation", "coprime_conductor_component_preserved",
    "coprime_conductor_preservation_check", "edge_degree", "edge_separable",
    "edge_direction", "edge_direction_derivation", "map_evaluator_serialized",
    "dual_serialized", "transfer_claim_permitted",
}
CERTIFICATE_GP_ERROR_FIELDS = CERTIFICATE_TERMINAL_FIELDS | {
    "schema", "global_index", "source_b", "source_a2", "expected_order",
    "field_degree", "f_pi", "class_discriminant_271_valuation",
    "kernel_extension_coprime_to_271", "maximal_order_class_number",
    "f271_census_sha256", "f271_census_source_revision",
    "f271_census_source_sha256", "f271_census_complete_orbit_count",
    "control_mode", "pipeline_error", "gp_log_sha256",
}
CERTIFICATE_SIGNED_INTEGER_FIELDS = {
    "class_trace", "class_discriminant", "extension_trace",
}
CERTIFICATE_TEXT_FIELDS = {
    "schema", "f_pi_factorization", "f271_census_sha256",
    "f271_census_source_revision", "f271_census_source_sha256",
    "direct_parent_point_1_xset", "target_rank2_point_1_xset",
    "source_conductor_derivation", "target_conductor_derivation",
    "f271_census_exclusion_role", "edge_direction",
    "edge_direction_derivation", "pilot_exclusion_scope", "pipeline_error",
    "gp_log_sha256", "status",
}

COMPILE_FLAGS = (
    "-std=gnu11",
    "-O3",
    "-Wall",
    "-Wextra",
    "-Wconversion",
    "-Wshadow",
    "-Werror",
    "-mpclmul",
    "-msse4.1",
    "-static",
)
REQUIRED_FROZEN = {
    "Dockerfile.gp",
    "PROTOCOL.md",
    "PROVENANCE.md",
    "classify_recover.gp",
    "floor271_orbits.csv",
    "params.h",
    "pipeline.py",
    "planning_stats.py",
    "run_scan.py",
    "search.c",
    "spec.json",
    "test_harness_contract.py",
    "test_sieve_reference.py",
    "upstream/lvl_check.gp",
    "upstream/vert_down.gp",
    "verify_prp.py",
}

_atomic_counter = 0
_atomic_lock = threading.Lock()
_subreaper_lock = threading.Lock()
_subreaper_enabled = False


class RunError(RuntimeError):
    """An integrity, execution, or frozen-contract failure."""


class AdmittedFailure(RunError):
    """A pipeline failure that invalidates rather than backfills the sample."""


def enable_child_subreaper() -> None:
    """Make orphaned grandchildren reapable by this runner (Linux prctl)."""
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


@dataclass(frozen=True)
class ScanLayout:
    start: int
    shards: int
    shard_size: int
    probe_root_seed: int
    mock: bool

    @property
    def end(self) -> int:
        return self.start + self.shards * self.shard_size

    def interval(self, shard_id: int) -> tuple[int, int]:
        if not 0 <= shard_id < self.shards:
            raise ValueError(f"invalid shard id {shard_id}")
        return self.start + shard_id * self.shard_size, self.shard_size


@dataclass(frozen=True)
class Pair:
    raw: dict[str, Any]
    global_index: int
    bottom_orbit_rep: int
    parent_orbit_rep: int


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def fsync_file(path: Path) -> None:
    with path.open("rb") as handle:
        os.fsync(handle.fileno())


def durable_mkdir(path: Path, *, parents: bool = False) -> None:
    if parents:
        missing: list[Path] = []
        cursor = path
        while not cursor.exists():
            missing.append(cursor)
            cursor = cursor.parent
        if not cursor.is_dir():
            raise RunError(f"directory ancestor is not a directory: {cursor}")
        for item in reversed(missing):
            item.mkdir()
            fsync_directory(item.parent)
    else:
        path.mkdir()
        fsync_directory(path.parent)


def _new_partial(path: Path) -> Path:
    global _atomic_counter
    with _atomic_lock:
        _atomic_counter += 1
        suffix = f".partial-{os.getpid()}-{threading.get_ident()}-{_atomic_counter}"
    return path.with_name(f".{path.name}{suffix}")


def rename_noreplace(source: Path, target: Path) -> None:
    libc = ctypes.CDLL(None, use_errno=True)
    try:
        renameat2 = libc.renameat2
    except AttributeError as exc:
        raise RunError("renameat2(RENAME_NOREPLACE) is required for publication") from exc
    renameat2.argtypes = (
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_uint,
    )
    renameat2.restype = ctypes.c_int
    if renameat2(-100, os.fsencode(source), -100, os.fsencode(target), 1) != 0:
        error_number = ctypes.get_errno()
        if error_number == errno.EEXIST:
            raise FileExistsError(
                error_number, "refusing to replace immutable path", str(target)
            )
        raise OSError(error_number, os.strerror(error_number), str(target))


def atomic_write_bytes(path: Path, payload: bytes) -> None:
    if path.exists() or path.is_symlink():
        raise FileExistsError(f"refusing to overwrite immutable file {path}")
    partial = _new_partial(path)
    with partial.open("xb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    try:
        # renameat2(RENAME_NOREPLACE) publishes one name atomically, without
        # the post-link duplicate-name crash window of link+unlink.
        rename_noreplace(partial, path)
    except BaseException:
        partial.unlink(missing_ok=True)
        raise
    fsync_directory(path.parent)


def atomic_write_text(path: Path, payload: str) -> None:
    atomic_write_bytes(path, payload.encode("utf-8"))


def atomic_write_json(path: Path, value: Any) -> None:
    atomic_write_text(path, json.dumps(value, indent=2, sort_keys=True) + "\n")


def atomic_replace_json(path: Path, value: Any) -> None:
    """Replace only a declared mutable state file, preserving crash atomicity."""
    partial = _new_partial(path)
    try:
        with partial.open("xb") as handle:
            handle.write((json.dumps(value, indent=2, sort_keys=True) + "\n").encode())
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(partial, path)
    except BaseException:
        partial.unlink(missing_ok=True)
        raise
    fsync_directory(path.parent)


def reject_duplicate_json_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def reject_json_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON constant {value!r}")


def finite_json_float(value: str) -> float:
    parsed = float(value)
    if not math.isfinite(parsed):
        raise ValueError(f"non-finite JSON float {value!r}")
    return parsed


def bounded_json_int(value: str) -> int:
    digits = value[1:] if value.startswith("-") else value
    if len(digits) > MAX_CERT_DECIMAL_DIGITS:
        raise ValueError("JSON integer exceeds the frozen decimal-length bound")
    return int(value)


def strict_json_loads(payload: str | bytes, context: str) -> Any:
    try:
        return json.loads(
            payload,
            object_pairs_hook=reject_duplicate_json_keys,
            parse_constant=reject_json_constant,
            parse_float=finite_json_float,
            parse_int=bounded_json_int,
        )
    except (json.JSONDecodeError, UnicodeError, ValueError) as exc:
        raise RunError(f"{context}: invalid strict JSON: {exc}") from exc


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = strict_json_loads(path.read_bytes(), str(path))
    except OSError as exc:
        raise RunError(f"cannot read JSON object {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise RunError(f"{path}: expected a JSON object")
    return value


def decimal_uint(value: Any, context: str, *, maximum: int | None = None) -> int:
    if isinstance(value, bool):
        raise RunError(f"{context}: boolean is not an unsigned integer")
    if isinstance(value, int):
        parsed = value
    elif isinstance(value, str) and value.isascii() and value.isdecimal():
        if len(value) > MAX_CERT_DECIMAL_DIGITS:
            raise RunError(f"{context}: decimal integer is too long")
        if value != "0" and value.startswith("0"):
            raise RunError(f"{context}: noncanonical decimal integer")
        try:
            parsed = int(value)
        except ValueError as exc:
            raise RunError(f"{context}: invalid bounded decimal integer") from exc
    else:
        raise RunError(f"{context}: expected an unsigned decimal integer")
    if parsed < 0 or (maximum is not None and parsed > maximum):
        raise RunError(f"{context}: integer outside permitted range")
    return parsed


def canonical_uint(value: Any, context: str, *, maximum: int | None = None) -> int:
    """Parse a generated JSON integer without accepting strings/bools/floats."""
    if type(value) is not int:
        raise RunError(f"{context}: expected a canonical JSON unsigned integer")
    if value < 0 or (maximum is not None and value > maximum):
        raise RunError(f"{context}: integer outside permitted range")
    return value


def exact_int_equal(value: Any, expected: int) -> bool:
    """Compare JSON integers without accepting bool or integral floats."""
    return type(value) is int and value == expected


def exact_optional_int_equal(value: Any, expected: int | None) -> bool:
    return value is None if expected is None else exact_int_equal(value, expected)


def exact_int_list(value: Any, expected: Iterable[int]) -> bool:
    expected_list = list(expected)
    return (
        isinstance(value, list)
        and len(value) == len(expected_list)
        and all(
            exact_int_equal(observed, wanted)
            for observed, wanted in zip(value, expected_list, strict=True)
        )
    )


def exact_json_equal(observed: Any, expected: Any) -> bool:
    """JSON equality that does not collapse bool/int/float numeric types."""
    if type(observed) is not type(expected):
        return False
    if isinstance(expected, dict):
        return set(observed) == set(expected) and all(
            exact_json_equal(observed[key], value) for key, value in expected.items()
        )
    if isinstance(expected, list):
        return len(observed) == len(expected) and all(
            exact_json_equal(left, right)
            for left, right in zip(observed, expected, strict=True)
        )
    return observed == expected


def validate_utc_timestamp(value: Any, context: str) -> datetime:
    if not isinstance(value, str) or re.fullmatch(
        r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}"
        r"(?:\.[0-9]{6})?\+00:00",
        value,
    ) is None:
        raise RunError(f"{context}: expected a canonical UTC RFC3339 timestamp")
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise RunError(f"{context}: invalid RFC3339 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise RunError(f"{context}: timestamp must have an explicit UTC offset")
    return parsed


def is_attempt_directory_name(value: str) -> bool:
    return re.fullmatch(r"attempt-[0-9]{6}", value) is not None


def safe_manifest_name(name: str) -> bool:
    pure = PurePosixPath(name)
    return (
        bool(name)
        and not pure.is_absolute()
        and "\\" not in name
        and all(piece not in ("", ".", "..") for piece in pure.parts)
        and str(pure) == name
    )


def read_hash_manifest(path: Path) -> tuple[dict[str, str], str]:
    try:
        content = path.read_text()
    except OSError as exc:
        raise RunError(f"cannot read hash manifest {path}: {exc}") from exc
    if not content or not content.endswith("\n"):
        raise RunError(f"{path}: manifest must be nonempty and newline terminated")
    entries: dict[str, str] = {}
    for line_number, line in enumerate(content.splitlines(), 1):
        pieces = line.split("  ", 1)
        if (
            len(pieces) != 2
            or len(pieces[0]) != 64
            or any(character not in "0123456789abcdef" for character in pieces[0])
            or not safe_manifest_name(pieces[1])
            or pieces[1] in entries
        ):
            raise RunError(f"{path}:{line_number}: malformed manifest entry")
        entries[pieces[1]] = pieces[0]
    if list(entries) != sorted(entries):
        raise RunError(f"{path}: entries are not sorted canonically")
    return entries, hashlib.sha256(content.encode()).hexdigest()


def verify_frozen_inputs() -> tuple[dict[str, str], str]:
    manifest = HERE / "FROZEN.sha256"
    if manifest.is_symlink() or not manifest.is_file():
        raise RunError("FROZEN.sha256 must be a regular non-symlink file")
    entries, manifest_hash = read_hash_manifest(manifest)
    if set(entries) != REQUIRED_FROZEN:
        raise RunError(
            "FROZEN.sha256 entries differ from the exact executable-input set; "
            f"missing={sorted(REQUIRED_FROZEN-set(entries))}, "
            f"extra={sorted(set(entries)-REQUIRED_FROZEN)}"
        )
    for name, expected in entries.items():
        source = HERE / name
        if not source.is_file() or source.is_symlink():
            raise RunError(f"frozen input is missing, non-regular, or a symlink: {source}")
        actual = sha256_file(source)
        if actual != expected:
            raise RunError(f"{source}: sha256={actual}, frozen={expected}")
    return entries, manifest_hash


def command_output(command: list[str], *, cwd: Path | None = None) -> str:
    process = subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
        env=RUNNER_CHILD_ENV,
    )
    if process.returncode != 0:
        raise RunError(
            f"command failed ({process.returncode}): {command!r}; "
            f"stderr={process.stderr[-1000:]!r}"
        )
    return process.stdout.strip()


def git_receipt() -> dict[str, Any]:
    commit = command_output(["git", "rev-parse", "HEAD"], cwd=REPO)
    status_text = command_output(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"], cwd=REPO
    )
    if status_text:
        raise RunError(
            "refusing execution from a dirty worktree; commit the complete frozen harness first"
        )
    return {
        "commit": commit,
        "status_porcelain": status_text,
        "worktree_clean": True,
    }


def validate_spec(spec: dict[str, Any]) -> dict[str, Any]:
    canonical_spec = json.dumps(
        spec, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
    ).encode()
    if hashlib.sha256(canonical_spec).hexdigest() != EXPECTED_SPEC_CANONICAL_SHA256:
        raise RunError("spec.json differs from the exact frozen semantic contract")
    expected_sections = {
        "schema",
        "status",
        "scope",
        "field_and_class",
        "scan",
        "sampling_prp",
        "population_model",
        "selection",
        "classifier",
        "controls",
        "output_contract",
        "runtime",
        "downstream_native_measurement",
    }
    if (
        set(spec) != expected_sections
        or spec.get("schema") != "m51-deep-scan-spec/v1"
        or spec.get("status") != "pre-outcome-freeze-ready"
        or spec.get("scope")
        != {
            "claim": (
                "endpoint-native discovery and certification only; downstream "
                "measurement is a non-frozen blueprint"
            ),
            "map_evaluator_required": False,
            "dual_required": False,
            "transfer_claim_permitted": False,
        }
    ):
        raise RunError("spec.json top-level schema or scope differs from the frozen study")
    scan = spec.get("scan")
    if not isinstance(scan, dict):
        raise RunError("spec.json: missing scan object")
    exact = {
        "start": SCI_START,
        "end": SCI_END,
        "shards": SCI_SHARDS,
        "shard_size": SCI_SHARD_SIZE,
        "probe_root_seed": SCI_ROOT_SEED,
        "workers": WORKERS,
        "cores": list(CORES),
        "target_pairs": TARGET_PAIRS,
        "pilot_bottom_orbit_rep": PILOT_BOTTOM_ORBIT_REP,
        "pilot_parent_orbit_rep": PILOT_PARENT_ORBIT_REP,
        "pilot_bottom_raw_b": PILOT_BOTTOM_RAW_B,
        "point_probes": 3,
        "timeout_seconds_per_shard": SHARD_TIMEOUT_SECONDS,
        "build_timeout_seconds": BUILD_TIMEOUT_SECONDS,
        "full_range_required": True,
        "early_stop_permitted": False,
    }
    for key, expected in exact.items():
        if scan.get(key) != expected:
            raise RunError(
                f"spec.json scan.{key}={scan.get(key)!r}; frozen runner expects {expected!r}"
            )
    sampling_prp = spec.get("sampling_prp")
    if (
        not isinstance(sampling_prp, dict)
        or sampling_prp.get("derived_key_hex") != PRP_DERIVED_KEY_HEX
        or not exact_int_equal(sampling_prp.get("zero_preimage"), PRP_ZERO_PREIMAGE)
        or sampling_prp.get("zero_preimage_outside_scan") is not True
    ):
        raise RunError("spec.json sampling_prp differs from the frozen PRP")
    population = spec.get("population_model")
    exact_population = {
        "eligible_models": 32_862_768,
        "expected_eligible_bottom_hits": 52.53840242858134,
        "exact_expected_distinct_eligible_parents": 51.96014232199414,
        "binomial_occupancy_approx_probability_at_least_32_distinct_parents": 0.998926642220153,
    }
    if not isinstance(population, dict) or any(
        population.get(key) != expected for key, expected in exact_population.items()
    ):
        raise RunError("spec.json population_model differs from frozen planning statistics")
    if spec.get("output_contract") != {
        "selection_path": "selection.json",
        "selection_schema": "m51-deep-global-selection/v1",
        "pair_schema": PAIR_SCHEMA,
        "certificate_base": CLASSIFICATION_CERTIFICATE_BASE,
        "terminal_seal": "MANIFEST.sha256",
    }:
        raise RunError("spec.json output_contract differs from the frozen handoff")
    if spec.get("controls") != {
        "required_count": len(CONTROL_IDS),
        "negative": "crater, all 16 f=271 representatives, and normal-mode pilot exclusion",
        "positive": [
            "f=271 floor to crater with order-271^2 witness",
            "pilot bottom to its frozen parent with order-271^2 witness",
            "pilot parent with independent rank-two 271-torsion",
        ],
        "must_pass_before_scan": True,
    }:
        raise RunError("spec.json controls differ from the frozen 21-control gate")
    runtime = spec.get("runtime")
    if not isinstance(runtime, dict):
        raise RunError("spec.json: missing runtime object")
    exact_runtime = {
        "source_image_content_id": PINNED_GP_IMAGE_ID,
        "gp_binary_sha256": PINNED_GP_BINARY_SHA256,
        "global_pipeline_timeout_seconds": PIPELINE_TIMEOUT_SECONDS,
        "controls_timeout_seconds": CONTROLS_TIMEOUT_SECONDS,
        "gp_stack": GP_STACK,
        "gp_fast_no_gprc": True,
        "gp_child_environment": GP_CHILD_ENV,
        "runner_child_environment": RUNNER_CHILD_ENV,
        "python_isolation_flags": list(PYTHON_CHILD_FLAGS),
        "linux_child_subreaper_required": True,
        "scanner_static_link_required": True,
        "container_scientific_route_enabled": False,
        "container_network": GP_CONTAINER_NETWORK,
        "container_memory": GP_CONTAINER_MEMORY,
        "container_cpuset": GP_CONTAINER_CPUSET,
    }
    for key, expected in exact_runtime.items():
        if runtime.get(key) != expected:
            raise RunError(
                f"spec.json runtime.{key}={runtime.get(key)!r}; expected {expected!r}"
            )
    if SCI_START + SCI_SHARDS * SCI_SHARD_SIZE != SCI_END:
        raise RunError("internal scientific scan partition mismatch")
    validate_bijection_range(SCI_ROOT_SEED, SCI_START, SCI_END - SCI_START)
    return scan


def copy_frozen_snapshot(
    destination: Path, frozen: tuple[dict[str, str], str]
) -> dict[str, Any]:
    entries, manifest_hash = frozen
    durable_mkdir(destination)
    receipt: dict[str, Any] = {}
    for name in [*entries, "FROZEN.sha256"]:
        source = HERE / name
        expected = entries.get(name, manifest_hash)
        target = destination / name
        durable_mkdir(target.parent, parents=True) if not target.parent.exists() else None
        partial = _new_partial(target)
        if sha256_file(source) != expected:
            raise RunError(f"frozen input changed before snapshot: {source}")
        with source.open("rb") as src, partial.open("xb") as dst:
            shutil.copyfileobj(src, dst)
            dst.flush()
            os.fsync(dst.fileno())
        if sha256_file(partial) != expected or sha256_file(source) != expected:
            raise RunError(f"snapshot hash mismatch for {source}")
        os.rename(partial, target)
        target.chmod(0o444)
        fsync_file(target)
        fsync_directory(target.parent)
        receipt[name] = {
            "source": str(source),
            "snapshot": str(target),
            "sha256": expected,
            "bytes": target.stat().st_size,
        }
    if verify_frozen_inputs() != frozen:
        raise RunError("frozen inputs changed during snapshot construction")
    return receipt


def verify_snapshot(out: Path, frozen: tuple[dict[str, str], str]) -> None:
    entries, manifest_hash = frozen
    expected_names = {*entries, "FROZEN.sha256"}
    inputs = out / "inputs"
    actual_names = {
        path.relative_to(inputs).as_posix()
        for path in inputs.rglob("*")
        if path.is_file() or path.is_symlink()
    }
    if actual_names != expected_names:
        raise RunError(
            "snapshot file set mismatch; "
            f"missing={sorted(expected_names-actual_names)}, "
            f"extra={sorted(actual_names-expected_names)}"
        )
    for name in sorted(expected_names):
        path = inputs / name
        if path.is_symlink() or not path.is_file():
            raise RunError(f"snapshot entry is not a regular file: {path}")
        if path.stat().st_mode & 0o222:
            raise RunError(f"snapshot entry is unexpectedly writable: {path}")
        expected = entries.get(name, manifest_hash)
        if sha256_file(path) != expected:
            raise RunError(f"snapshot hash mismatch: {path}")


def inspect_linked_objects(
    gp_bin: Path, ldd_bin: str
) -> tuple[str, str, dict[str, dict[str, Any]]]:
    ldd = subprocess.run(
        [ldd_bin, str(gp_bin)],
        capture_output=True,
        text=True,
        check=False,
        env=RUNNER_CHILD_ENV,
    )
    if ldd.returncode != 0 or ldd.stderr or "not found" in ldd.stdout:
        raise RunError(
            f"ldd failed or reported an unresolved object: "
            f"exit={ldd.returncode}, stderr={ldd.stderr[-1000:]!r}"
        )
    shared_objects: dict[str, dict[str, Any]] = {}
    for line_number, line in enumerate(ldd.stdout.splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("linux-vdso"):
            continue
        if "=>" in stripped:
            candidate = stripped.split("=>", 1)[1].strip().split(" ", 1)[0]
        else:
            candidate = stripped.split(" ", 1)[0]
        if not candidate.startswith("/"):
            raise RunError(f"unrecognized ldd line {line_number}: {line!r}")
        requested = Path(candidate)
        resolved = requested.resolve(strict=True)
        if not resolved.is_file():
            raise RunError(f"ldd target is not a regular file: {resolved}")
        shared_objects[str(requested)] = {
            "resolved_path": str(resolved),
            "sha256": sha256_file(resolved),
            "bytes": resolved.stat().st_size,
        }
    if not shared_objects:
        raise RunError("ldd returned no resolved shared objects for GP")
    return ldd.stdout, ldd.stderr, shared_objects


def resolve_gp_runtime(
    gp_bin_arg: Path | None, gp_image_arg: str | None, *, mock: bool
) -> dict[str, Any] | None:
    if mock:
        if gp_bin_arg is not None or gp_image_arg is not None:
            raise RunError("--mock cannot select a GP runtime")
        return None
    if gp_image_arg is not None:
        raise RunError(
            "--gp-image is disabled for admitted runs because killing the Docker CLI "
            "does not guarantee termination of the daemon-side container; use the "
            "exact frozen --gp-bin extraction"
        )
    if gp_bin_arg is None:
        raise RunError("scientific mode requires the exact frozen --gp-bin extraction")
    if gp_bin_arg.is_symlink():
        raise RunError("--gp-bin must not be a symlink")
    gp_bin = gp_bin_arg.resolve(strict=True)
    if not gp_bin.is_file() or gp_bin.is_symlink() or not os.access(gp_bin, os.X_OK):
        raise RunError(f"--gp-bin is not an executable regular file: {gp_bin}")
    binary_hash = sha256_file(gp_bin)
    if binary_hash != PINNED_GP_BINARY_SHA256:
        raise RunError(
            f"GP binary sha256={binary_hash}; frozen value={PINNED_GP_BINARY_SHA256}"
        )
    version = subprocess.run(
        [str(gp_bin), "--version"],
        capture_output=True,
        text=True,
        check=False,
        env=RUNNER_CHILD_ENV,
    )
    if version.returncode != 0:
        raise RunError(
            f"GP version probe failed ({version.returncode}): {version.stderr[-1000:]!r}"
        )
    ldd_bin = shutil.which("ldd", path=RUNNER_CHILD_ENV["PATH"])
    if ldd_bin is None:
        raise RunError("cannot record GP dependencies because ldd is unavailable")
    ldd_stdout, ldd_stderr, shared_objects = inspect_linked_objects(gp_bin, ldd_bin)
    return {
        "kind": "binary",
        "path": str(gp_bin),
        "sha256": binary_hash,
        "source_image_id": PINNED_GP_IMAGE_ID,
        "version_stdout": version.stdout,
        "version_stderr": version.stderr,
        "ldd_stdout": ldd_stdout,
        "ldd_stderr": ldd_stderr,
        "ldd_path": ldd_bin,
        "ldd_resolved_path": str(Path(ldd_bin).resolve(strict=True)),
        "ldd_sha256": sha256_file(Path(ldd_bin).resolve(strict=True)),
        "shared_objects": shared_objects,
    }


def host_receipt(gp_runtime: dict[str, Any] | None) -> dict[str, Any]:
    available = sorted(os.sched_getaffinity(0))
    if not set(CORES).issubset(available):
        raise RunError(f"required cores {list(CORES)} outside process affinity {available}")
    cpuinfo = Path("/proc/cpuinfo").read_text()
    model = None
    flags: set[str] = set()
    for line in cpuinfo.splitlines():
        if model is None and line.startswith("model name"):
            model = line.split(":", 1)[1].strip()
        if line.startswith("flags"):
            flags.update(line.split(":", 1)[1].split())
    required_flags = {"pclmulqdq", "sse4_1"}
    if not required_flags.issubset(flags):
        raise RunError(f"host lacks required CPU flags: {sorted(required_flags-flags)}")
    taskset = shutil.which("taskset", path=RUNNER_CHILD_ENV["PATH"])
    gcc = shutil.which("gcc", path=RUNNER_CHILD_ENV["PATH"])
    if taskset is None or gcc is None:
        raise RunError("required taskset or gcc executable is unavailable")
    taskset_resolved = Path(taskset).resolve(strict=True)
    gcc_resolved = Path(gcc).resolve(strict=True)
    return {
        "created_utc": utc_now(),
        "platform": platform.platform(),
        "uname": platform.uname()._asdict(),
        "python": sys.version,
        "python_executable": sys.executable,
        "python_sha256": sha256_file(Path(sys.executable).resolve()),
        "logical_cpus": os.cpu_count(),
        "process_affinity": available,
        "selected_cores": list(CORES),
        "cpu_model": model,
        "cpu_flags": sorted(flags),
        "required_cpu_flags": sorted(required_flags),
        "taskset": taskset,
        "taskset_resolved": str(taskset_resolved),
        "taskset_sha256": sha256_file(taskset_resolved),
        "gcc": gcc,
        "gcc_resolved": str(gcc_resolved),
        "gcc_sha256": sha256_file(gcc_resolved),
        "gcc_version": command_output([gcc, "--version"]).splitlines(),
        "gp": gp_runtime,
    }


def stable_host_identity(host: dict[str, Any]) -> dict[str, Any]:
    expected_fields = {
        "created_utc",
        "platform",
        "uname",
        "python",
        "python_executable",
        "python_sha256",
        "logical_cpus",
        "process_affinity",
        "selected_cores",
        "cpu_model",
        "cpu_flags",
        "required_cpu_flags",
        "taskset",
        "taskset_resolved",
        "taskset_sha256",
        "gcc",
        "gcc_resolved",
        "gcc_sha256",
        "gcc_version",
        "gp",
    }
    if set(host) != expected_fields:
        raise RunError("host receipt fields differ from the frozen schema")
    validate_utc_timestamp(host.get("created_utc"), "host receipt:created_utc")
    stable = {key: host[key] for key in expected_fields - {"created_utc", "gp"}}
    stable["gp"] = stable_gp_runtime_identity(host.get("gp"))
    return stable


def stable_gp_runtime_identity(
    gp_runtime: dict[str, Any] | None,
) -> dict[str, Any] | None:
    """Remove ASLR-bearing ldd text while retaining every resolved object hash."""
    if gp_runtime is None:
        return None
    expected_fields = {
        "kind", "path", "sha256", "source_image_id", "version_stdout",
        "version_stderr", "ldd_stdout", "ldd_stderr", "ldd_path",
        "ldd_resolved_path", "ldd_sha256", "shared_objects",
    }
    if set(gp_runtime) != expected_fields or gp_runtime.get("kind") != "binary":
        raise RunError("admitted runner permits only the extracted GP runtime")
    return {
        key: gp_runtime[key]
        for key in (
            "kind",
            "path",
            "sha256",
            "source_image_id",
            "version_stdout",
            "version_stderr",
            "ldd_path",
            "ldd_resolved_path",
            "ldd_sha256",
            "shared_objects",
        )
    }


def verify_gp_runtime_artifacts(gp_runtime: dict[str, Any]) -> None:
    if gp_runtime.get("kind") != "binary":
        raise RunError("admitted GP artifact check requires extracted binary")
    gp = Path(str(gp_runtime.get("path", "")))
    if (
        gp.is_symlink()
        or not gp.is_file()
        or sha256_file(gp) != gp_runtime.get("sha256")
        or gp_runtime.get("sha256") != PINNED_GP_BINARY_SHA256
    ):
        raise RunError("GP executable changed after runtime admission")
    ldd_path = str(gp_runtime.get("ldd_path", ""))
    ldd = Path(ldd_path)
    if (
        not ldd.is_file()
        or str(ldd.resolve(strict=True)) != gp_runtime.get("ldd_resolved_path")
        or sha256_file(ldd.resolve(strict=True)) != gp_runtime.get("ldd_sha256")
    ):
        raise RunError("ldd executable changed after runtime admission")
    version = subprocess.run(
        [str(gp), "--version"],
        capture_output=True,
        text=True,
        check=False,
        env=RUNNER_CHILD_ENV,
    )
    if (
        version.returncode != 0
        or version.stdout != gp_runtime.get("version_stdout")
        or version.stderr != gp_runtime.get("version_stderr")
    ):
        raise RunError("GP version probe changed after runtime admission")
    _, _, shared_objects = inspect_linked_objects(gp, ldd_path)
    if shared_objects != gp_runtime.get("shared_objects"):
        raise RunError("GP linked-object mapping or content changed after admission")


def run_process(
    command: list[str],
    *,
    cwd: Path | None = None,
    timeout: int,
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
        start_new_session=True,
        env=RUNNER_CHILD_ENV,
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

    def drain_after_group_cleanup() -> tuple[bytes, bytes]:
        """Drain only after the PGID is gone, with a final fixed time bound."""
        try:
            return process.communicate(timeout=2)
        except subprocess.TimeoutExpired as exc:
            # A descendant that escaped the session can otherwise hold an inherited
            # pipe forever.  It is outside the admitted child PGID; close our read
            # ends and make the attempt fail through the diagnostic stream.
            stdout = exc.output if isinstance(exc.output, bytes) else b""
            stderr = exc.stderr if isinstance(exc.stderr, bytes) else b""
            if process.stdout is not None:
                process.stdout.close()
            if process.stderr is not None:
                process.stderr.close()
            stderr += b"RUNNER: bounded pipe drain expired after process-group cleanup\n"
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
                # The direct child may have died while a GP/search descendant still
                # holds stdout/stderr.  Reap the whole PGID before draining pipes.
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
            stderr += b"RUNNER: residual process group terminated and reaped\n"
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
        "cwd": str(cwd) if cwd else None,
        "started_utc": started_utc,
        "finished_utc": utc_now(),
        "elapsed_seconds": time.monotonic() - started,
        "exit_status": process.returncode,
        "timed_out": timed_out,
        "cancelled": cancelled,
        "environment": RUNNER_CHILD_ENV,
        "stdout": stdout,
        "stderr": stderr,
    }


def tree_regular_files(root: Path, *, exclude_manifest: bool = True) -> list[Path]:
    if root.is_symlink() or not root.is_dir():
        raise RunError(f"sealed-tree root is not a regular directory: {root}")
    files: list[Path] = []
    for path in root.rglob("*"):
        if path.is_symlink():
            raise RunError(f"symlink forbidden in sealed tree: {path}")
        if path.is_dir():
            continue
        if not path.is_file() or not stat.S_ISREG(path.stat().st_mode):
            raise RunError(f"non-regular file forbidden in sealed tree: {path}")
        if exclude_manifest and path == root / "MANIFEST.sha256":
            continue
        files.append(path)
    return sorted(files, key=lambda path: path.relative_to(root).as_posix())


def tree_relative_directories(root: Path) -> list[str]:
    if root.is_symlink() or not root.is_dir():
        raise RunError(f"sealed-tree root is not a regular directory: {root}")
    directories: list[str] = []
    for path in root.rglob("*"):
        if path.is_symlink():
            raise RunError(f"symlink forbidden in sealed tree: {path}")
        if path.is_dir():
            directories.append(path.relative_to(root).as_posix())
    return sorted(directories)


def fsync_tree(root: Path) -> None:
    """Persist every regular file and directory before immutable promotion/seal."""
    files = tree_regular_files(root, exclude_manifest=False)
    for path in files:
        fsync_file(path)
    directories = [root, *(path for path in root.rglob("*") if path.is_dir())]
    for path in sorted(directories, key=lambda item: len(item.parts), reverse=True):
        if path.is_symlink():
            raise RunError(f"symlink forbidden while syncing sealed tree: {path}")
        fsync_directory(path)


def write_tree_manifest(root: Path) -> Path:
    manifest = root / "MANIFEST.sha256"
    if manifest.exists() or manifest.is_symlink():
        raise FileExistsError(f"refusing to overwrite seal {manifest}")
    directory_index = root / "DIRECTORIES.json"
    index_payload = (
        json.dumps(
            {
                "schema": "m51-sealed-directory-index/v1",
                "directories": tree_relative_directories(root),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    ).encode()
    owned_index: os.stat_result | None = None
    try:
        if directory_index.exists() or directory_index.is_symlink():
            if (
                directory_index.is_symlink()
                or not directory_index.is_file()
                or directory_index.read_bytes() != index_payload
            ):
                raise RunError(
                    "orphan directory index differs from the current terminal tree"
                )
        else:
            try:
                atomic_write_bytes(directory_index, index_payload)
                owned_index = directory_index.stat(follow_symlinks=False)
            except FileExistsError:
                # A cooperative racer should be excluded by the root lock.  If
                # one nevertheless won, reuse only an exact durable index.
                if (
                    directory_index.is_symlink()
                    or not directory_index.is_file()
                    or directory_index.read_bytes() != index_payload
                ):
                    raise RunError(
                        "concurrent directory index differs from terminal tree"
                    )
        fsync_tree(root)
        lines = [
            f"{sha256_file(path)}  {path.relative_to(root).as_posix()}"
            for path in tree_regular_files(root)
        ]
        atomic_write_text(manifest, "\n".join(lines) + ("\n" if lines else ""))
        return manifest
    except BaseException:
        if not manifest.exists() and owned_index is not None:
            try:
                current = directory_index.stat(follow_symlinks=False)
            except FileNotFoundError:
                current = None
            if (
                current is not None
                and stat.S_ISREG(current.st_mode)
                and current.st_dev == owned_index.st_dev
                and current.st_ino == owned_index.st_ino
            ):
                directory_index.unlink()
                fsync_directory(root)
        raise


def verify_tree_manifest(root: Path) -> dict[str, str]:
    entries, _ = read_hash_manifest(root / "MANIFEST.sha256")
    actual = {
        path.relative_to(root).as_posix()
        for path in tree_regular_files(root)
    }
    if actual != set(entries):
        raise RunError(
            f"sealed tree differs at {root}; missing={sorted(set(entries)-actual)}, "
            f"extra={sorted(actual-set(entries))}"
        )
    for name, expected in entries.items():
        if sha256_file(root / name) != expected:
            raise RunError(f"sealed file hash mismatch: {root/name}")
    directory_index = load_json(root / "DIRECTORIES.json")
    if directory_index != {
        "schema": "m51-sealed-directory-index/v1",
        "directories": tree_relative_directories(root),
    }:
        raise RunError(f"sealed directory set differs at {root}")
    return entries


def allocate_attempt(out: Path, kind: str, label: str) -> Path:
    parent = out / "attempts" / kind / label
    cursor = out
    for piece in ("attempts", kind, label):
        cursor = cursor / piece
        if cursor.exists() or cursor.is_symlink():
            if cursor.is_symlink() or not cursor.is_dir():
                raise RunError(f"attempt namespace component is not a real directory: {cursor}")
        else:
            durable_mkdir(cursor)
    if cursor != parent:
        raise RunError("internal attempt namespace construction mismatch")
    for number in range(1_000_000):
        candidate = parent / f"attempt-{number:06d}"
        try:
            durable_mkdir(candidate)
            return candidate
        except FileExistsError:
            continue
    raise RunError(f"attempt namespace exhausted under {parent}")


def promote_directory(
    source: Path, target: Path, *, require_manifest: bool = True
) -> None:
    if target.exists() or target.is_symlink():
        raise FileExistsError(f"refusing to replace immutable directory {target}")
    if require_manifest:
        verify_tree_manifest(source)
    elif any(
        (source / name).exists() or (source / name).is_symlink()
        for name in ("MANIFEST.sha256", "DIRECTORIES.json")
    ):
        raise RunError("unsealed initialization tree contains a terminal seal artifact")
    fsync_tree(source)
    rename_noreplace(source, target)
    fsync_directory(source.parent)
    fsync_directory(target.parent)


def write_process_logs(directory: Path, process: dict[str, Any]) -> None:
    atomic_write_bytes(directory / "stdout.log", process["stdout"])
    atomic_write_bytes(directory / "stderr.log", process["stderr"])


def receipt_process_fields(process: dict[str, Any]) -> dict[str, Any]:
    return {
        key: process[key]
        for key in (
            "command",
            "cwd",
            "started_utc",
            "finished_utc",
            "elapsed_seconds",
            "exit_status",
            "timed_out",
            "cancelled",
            "environment",
        )
    }


def validate_process_receipt(
    value: dict[str, Any],
    *,
    expected_command: list[str],
    expected_cwd: str | None,
    context: str,
) -> None:
    started = validate_utc_timestamp(value.get("started_utc"), f"{context}:started_utc")
    finished = validate_utc_timestamp(value.get("finished_utc"), f"{context}:finished_utc")
    if (
        value.get("command") != expected_command
        or value.get("cwd") != expected_cwd
        or not exact_int_equal(value.get("exit_status"), 0)
        or value.get("timed_out") is not False
        or value.get("cancelled") is not False
        or value.get("environment") != RUNNER_CHILD_ENV
        or not isinstance(value.get("elapsed_seconds"), (int, float))
        or isinstance(value.get("elapsed_seconds"), bool)
        or not math.isfinite(value.get("elapsed_seconds", float("nan")))
        or value.get("elapsed_seconds", -1) < 0
        or finished < started
    ):
        raise RunError(f"{context}: process receipt differs from the successful command")


def require_log(
    path: Path, expected_hash: Any, expected_bytes: bytes, context: str
) -> None:
    if (
        path.is_symlink()
        or not path.is_file()
        or path.read_bytes() != expected_bytes
        or expected_hash != sha256_file(path)
    ):
        raise RunError(f"{context}: sealed process log differs from its receipt")


def verify_static_elf(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    if len(data) < 64 or data[:4] != b"\x7fELF" or data[4] != 2 or data[5] != 1:
        raise RunError("scanner is not a 64-bit little-endian ELF executable")
    program_offset = struct.unpack_from("<Q", data, 32)[0]
    program_entry_size = struct.unpack_from("<H", data, 54)[0]
    program_count = struct.unpack_from("<H", data, 56)[0]
    if program_entry_size < 56 or program_count == 0:
        raise RunError("scanner ELF has malformed program headers")
    end = program_offset + program_entry_size * program_count
    if end > len(data):
        raise RunError("scanner ELF program headers extend past end of file")
    program_types = [
        struct.unpack_from("<I", data, program_offset + i * program_entry_size)[0]
        for i in range(program_count)
    ]
    if 2 in program_types or 3 in program_types:
        raise RunError("scanner ELF contains PT_DYNAMIC or PT_INTERP")
    return {
        "schema": "m51-static-elf/v1",
        "elf_class_bits": 64,
        "little_endian": True,
        "program_header_count": program_count,
        "pt_dynamic_present": False,
        "pt_interp_present": False,
    }


def validate_existing_build(
    out: Path, snapshots: Path, final: Path, receipt: dict[str, Any]
) -> Path:
    binary = final / "search"
    expected_top_fields = {
        "schema",
        "status",
        *PROCESS_RECEIPT_FIELDS,
        "logical_command",
        "source_sha256",
        "params_sha256",
        "compiler_version",
        "stdout_sha256",
        "stderr_sha256",
        "binary_sha256",
        "binary_bytes",
        "static_elf",
        "selftest",
        "reference_test",
        "prp_verification",
        "planning_stats",
        "contract_test",
    }
    if (
        set(receipt) != expected_top_fields
        or receipt.get("schema") != "m51-deep-build-receipt/v1"
        or receipt.get("status") != "complete"
        or receipt.get("logical_command")
        != ["gcc", *COMPILE_FLAGS, "-o", "search", "search.c"]
        or receipt.get("source_sha256") != sha256_file(snapshots / "search.c")
        or receipt.get("params_sha256") != sha256_file(snapshots / "params.h")
        or receipt.get("binary_sha256") != sha256_file(binary)
        or not exact_int_equal(receipt.get("binary_bytes"), binary.stat().st_size)
        or not exact_json_equal(receipt.get("static_elf"), verify_static_elf(binary))
    ):
        raise RunError("existing build receipt or binary metadata differs from contract")
    gcc = shutil.which("gcc", path=RUNNER_CHILD_ENV["PATH"])
    taskset = shutil.which("taskset", path=RUNNER_CHILD_ENV["PATH"])
    if gcc is None or taskset is None:
        raise RunError("build validation cannot resolve gcc or taskset")
    compile_command = receipt.get("command")
    if not isinstance(compile_command, list) or len(compile_command) < 3:
        raise RunError("existing build lacks an exact compiler command")
    recorded_binary = Path(str(compile_command[-2]))
    expected_attempt_parent = out / "attempts" / "build" / "search"
    if (
        compile_command != [gcc, *COMPILE_FLAGS, "-o", str(recorded_binary), "search.c"]
        or recorded_binary.name != "search"
        or recorded_binary.parent.parent != expected_attempt_parent
        or not is_attempt_directory_name(recorded_binary.parent.name)
        or receipt.get("compiler_version")
        != command_output([gcc, "--version"]).splitlines()
    ):
        raise RunError("existing build compiler provenance differs from contract")
    validate_process_receipt(
        receipt,
        expected_command=compile_command,
        expected_cwd=str(snapshots),
        context="build compiler",
    )
    require_log(final / "stdout.log", receipt.get("stdout_sha256"), b"", "build compiler")
    require_log(final / "stderr.log", receipt.get("stderr_sha256"), b"", "build compiler")

    common_test_fields = PROCESS_RECEIPT_FIELDS | {
        "stdout_sha256",
        "stderr_sha256",
        "requested_affinity",
    }
    tests: list[tuple[str, list[str], str, bytes, set[str]]] = [
        (
            "selftest",
            [taskset, "-c", "0", str(recorded_binary), "selftest"],
            "selftest",
            b"selftest ok\n",
            set(),
        ),
        (
            "reference_test",
            [
                taskset,
                "-c",
                "0",
                sys.executable,
                *PYTHON_CHILD_FLAGS,
                str(snapshots / "test_sieve_reference.py"),
                str(recorded_binary),
            ],
            "reference",
            b"reference vectors ok: 12 cases\n",
            {"source_sha256"},
        ),
        (
            "prp_verification",
            [
                taskset, "-c", "0", sys.executable, *PYTHON_CHILD_FLAGS,
                str(snapshots / "verify_prp.py"),
            ],
            "prp-verification",
            (final / "prp-verification.stdout.json").read_bytes(),
            {"source_sha256", "report_schema", "derived_key_hex"},
        ),
        (
            "planning_stats",
            [
                taskset, "-c", "0", sys.executable, *PYTHON_CHILD_FLAGS,
                str(snapshots / "planning_stats.py"),
            ],
            "planning-stats",
            (final / "planning-stats.stdout.json").read_bytes(),
            {
                "source_sha256",
                "schema",
                "eligible_models",
                "expected_eligible_hits",
                "exact_expected_distinct_parents",
                "binomial_occupancy_approx_probability_at_least_32",
                "quota_tail_is_exact_finite_population_probability",
                "model_condition",
            },
        ),
        (
            "contract_test",
            [
                taskset,
                "-c",
                "0",
                sys.executable,
                *PYTHON_CHILD_FLAGS,
                str(snapshots / "test_harness_contract.py"),
            ],
            "contract",
            b"harness contract ok\n",
            {"source_sha256"},
        ),
    ]
    source_for_test = {
        "reference_test": "test_sieve_reference.py",
        "prp_verification": "verify_prp.py",
        "planning_stats": "planning_stats.py",
        "contract_test": "test_harness_contract.py",
    }
    for name, command, log_stem, expected_stdout, extra_fields in tests:
        nested = receipt.get(name)
        if not isinstance(nested, dict) or set(nested) != common_test_fields | extra_fields:
            raise RunError(f"existing build {name} receipt fields differ from contract")
        validate_process_receipt(
            nested, expected_command=command, expected_cwd=None, context=f"build {name}"
        )
        if not exact_int_list(nested.get("requested_affinity"), [0]):
            raise RunError(f"existing build {name} affinity differs from contract")
        stdout_name = (
            f"{log_stem}.stdout.json"
            if name in {"prp_verification", "planning_stats"}
            else f"{log_stem}.stdout.log"
        )
        stderr_name = f"{log_stem}.stderr.log"
        require_log(
            final / stdout_name,
            nested.get("stdout_sha256"),
            expected_stdout,
            f"build {name}",
        )
        require_log(
            final / stderr_name,
            nested.get("stderr_sha256"),
            b"",
            f"build {name}",
        )
        source_name = source_for_test.get(name)
        if source_name is not None and nested.get("source_sha256") != sha256_file(
            snapshots / source_name
        ):
            raise RunError(f"existing build {name} source hash differs from snapshot")

    prp_report = strict_json_loads(
        (final / "prp-verification.stdout.json").read_bytes(),
        "sealed PRP verification",
    )
    if (
        not isinstance(prp_report, dict)
        or receipt["prp_verification"].get("report_schema")
        != "m51-deep-prp-verification/v1"
        or prp_report.get("schema") != "m51-deep-prp-verification/v1"
        or receipt["prp_verification"].get("derived_key_hex") != PRP_DERIVED_KEY_HEX
        or prp_report.get("derived_key_hex") != PRP_DERIVED_KEY_HEX
        or not exact_int_equal(prp_report.get("zero_preimage"), PRP_ZERO_PREIMAGE)
        or prp_report.get("scan_range_excludes_zero_preimage") is not True
    ):
        raise RunError("sealed PRP verification report differs from contract")
    planning_report = strict_json_loads(
        (final / "planning-stats.stdout.json").read_bytes(),
        "sealed planning statistics",
    )
    expected_planning = {
        "schema": "m51-deep-planning-stats/v1",
        "eligible_models": 32_862_768,
        "expected_eligible_hits": 52.53840242858134,
        "exact_expected_distinct_parents": 51.96014232199414,
        "binomial_occupancy_approx_probability_at_least_32": 0.998926642220153,
        "quota_tail_is_exact_finite_population_probability": False,
        "model_condition": "conditional on ideal-PRP exchangeability",
    }
    if not isinstance(planning_report, dict) or any(
        not exact_json_equal(planning_report.get(key), value)
        or not exact_json_equal(receipt["planning_stats"].get(key), value)
        for key, value in expected_planning.items()
    ):
        raise RunError("sealed planning-statistics report differs from contract")

    # Re-execute the two binary-dependent tests on the promoted scanner.  This
    # prevents a sealed unrelated ELF plus self-authored receipt from entering
    # a resumed scan.
    for command, expected_stdout, label in (
        ([taskset, "-c", "0", str(binary), "selftest"], b"selftest ok\n", "selftest"),
        (
            [
                taskset,
                "-c",
                "0",
                sys.executable,
                *PYTHON_CHILD_FLAGS,
                str(snapshots / "test_sieve_reference.py"),
                str(binary),
            ],
            b"reference vectors ok: 12 cases\n",
            "reference test",
        ),
    ):
        replay = run_process(command, timeout=BUILD_TIMEOUT_SECONDS)
        if (
            replay["timed_out"]
            or replay["cancelled"]
            or replay["exit_status"] != 0
            or replay["stdout"] != expected_stdout
            or replay["stderr"]
        ):
            raise RunError(f"promoted scanner failed replayed {label}")
    return binary


def build_search(out: Path, snapshots: Path) -> tuple[Path, dict[str, Any]]:
    final = out / "build"
    if final.exists():
        verify_tree_manifest(final)
        receipt = load_json(final / "receipt.json")
        binary = validate_existing_build(out, snapshots, final, receipt)
        return binary, receipt

    attempt = allocate_attempt(out, "build", "search")
    binary = attempt / "search"
    source = snapshots / "search.c"
    gcc = shutil.which("gcc", path=RUNNER_CHILD_ENV["PATH"])
    if gcc is None:
        raise RunError("fixed child PATH does not contain gcc")
    command = [gcc, *COMPILE_FLAGS, "-o", str(binary), source.name]
    process = run_process(command, cwd=source.parent, timeout=BUILD_TIMEOUT_SECONDS)
    write_process_logs(attempt, process)
    receipt = {
        "schema": "m51-deep-build-receipt/v1",
        "status": "failed",
        **receipt_process_fields(process),
        "logical_command": ["gcc", *COMPILE_FLAGS, "-o", "search", "search.c"],
        "source_sha256": sha256_file(source),
        "params_sha256": sha256_file(snapshots / "params.h"),
        "compiler_version": command_output([gcc, "--version"]).splitlines(),
        "stdout_sha256": sha256_file(attempt / "stdout.log"),
        "stderr_sha256": sha256_file(attempt / "stderr.log"),
    }
    if process["timed_out"] or process["cancelled"] or process["exit_status"] != 0:
        atomic_write_json(attempt / "receipt.json", receipt)
        write_tree_manifest(attempt)
        raise RunError(f"search build failed; immutable attempt retained at {attempt}")
    if process["stdout"] or process["stderr"]:
        atomic_write_json(attempt / "receipt.json", receipt)
        write_tree_manifest(attempt)
        raise RunError(f"warning-clean search build emitted output; attempt retained at {attempt}")
    if not binary.is_file() or binary.is_symlink():
        raise RunError("compiler reported success without a regular search binary")
    fsync_file(binary)
    static_elf = verify_static_elf(binary)

    selftest_command = [shutil.which("taskset", path=RUNNER_CHILD_ENV["PATH"]) or "taskset", "-c", "0", str(binary), "selftest"]
    selftest = run_process(selftest_command, timeout=BUILD_TIMEOUT_SECONDS)
    atomic_write_bytes(attempt / "selftest.stdout.log", selftest["stdout"])
    atomic_write_bytes(attempt / "selftest.stderr.log", selftest["stderr"])
    if (
        selftest["timed_out"]
        or selftest["cancelled"]
        or selftest["exit_status"] != 0
        or selftest["stdout"] != b"selftest ok\n"
        or selftest["stderr"]
    ):
        receipt["selftest"] = receipt_process_fields(selftest)
        atomic_write_json(attempt / "receipt.json", receipt)
        write_tree_manifest(attempt)
        raise RunError(f"search selftest failed; immutable attempt retained at {attempt}")

    reference_command = [
        shutil.which("taskset", path=RUNNER_CHILD_ENV["PATH"]) or "taskset",
        "-c",
        "0",
        sys.executable,
        *PYTHON_CHILD_FLAGS,
        str(snapshots / "test_sieve_reference.py"),
        str(binary),
    ]
    reference = run_process(reference_command, timeout=BUILD_TIMEOUT_SECONDS)
    atomic_write_bytes(attempt / "reference.stdout.log", reference["stdout"])
    atomic_write_bytes(attempt / "reference.stderr.log", reference["stderr"])
    if (
        reference["timed_out"]
        or reference["cancelled"]
        or reference["exit_status"] != 0
        or reference["stdout"] != b"reference vectors ok: 12 cases\n"
        or reference["stderr"]
    ):
        receipt["selftest"] = receipt_process_fields(selftest)
        receipt["reference_test"] = receipt_process_fields(reference)
        atomic_write_json(attempt / "receipt.json", receipt)
        write_tree_manifest(attempt)
        raise RunError(
            f"independent search reference test failed; immutable attempt retained at {attempt}"
        )

    prp_command = [
        shutil.which("taskset", path=RUNNER_CHILD_ENV["PATH"]) or "taskset",
        "-c",
        "0",
        sys.executable,
        *PYTHON_CHILD_FLAGS,
        str(snapshots / "verify_prp.py"),
    ]
    prp_check = run_process(prp_command, timeout=BUILD_TIMEOUT_SECONDS)
    atomic_write_bytes(attempt / "prp-verification.stdout.json", prp_check["stdout"])
    atomic_write_bytes(attempt / "prp-verification.stderr.log", prp_check["stderr"])
    prp_report: dict[str, Any] | None = None
    try:
        parsed_report = strict_json_loads(
            prp_check["stdout"], "verify_prp.py stdout"
        )
        if isinstance(parsed_report, dict):
            prp_report = parsed_report
    except RunError:
        pass
    if (
        prp_check["timed_out"]
        or prp_check["cancelled"]
        or prp_check["exit_status"] != 0
        or prp_check["stderr"]
        or prp_report is None
        or prp_report.get("schema") != "m51-deep-prp-verification/v1"
        or prp_report.get("derived_key_hex") != PRP_DERIVED_KEY_HEX
        or not exact_int_equal(prp_report.get("zero_preimage"), PRP_ZERO_PREIMAGE)
        or prp_report.get("scan_range_excludes_zero_preimage") is not True
    ):
        receipt["selftest"] = receipt_process_fields(selftest)
        receipt["reference_test"] = receipt_process_fields(reference)
        receipt["prp_verification"] = receipt_process_fields(prp_check)
        atomic_write_json(attempt / "receipt.json", receipt)
        write_tree_manifest(attempt)
        raise RunError(
            f"independent PRP verification failed; immutable attempt retained at {attempt}"
        )

    planning_command = [
        shutil.which("taskset", path=RUNNER_CHILD_ENV["PATH"]) or "taskset",
        "-c",
        "0",
        sys.executable,
        *PYTHON_CHILD_FLAGS,
        str(snapshots / "planning_stats.py"),
    ]
    planning = run_process(planning_command, timeout=BUILD_TIMEOUT_SECONDS)
    atomic_write_bytes(attempt / "planning-stats.stdout.json", planning["stdout"])
    atomic_write_bytes(attempt / "planning-stats.stderr.log", planning["stderr"])
    planning_report: dict[str, Any] | None = None
    try:
        parsed_planning = strict_json_loads(
            planning["stdout"], "planning_stats.py stdout"
        )
        if isinstance(parsed_planning, dict):
            planning_report = parsed_planning
    except RunError:
        pass
    expected_planning = {
        "schema": "m51-deep-planning-stats/v1",
        "eligible_models": 32_862_768,
        "expected_eligible_hits": 52.53840242858134,
        "exact_expected_distinct_parents": 51.96014232199414,
        "binomial_occupancy_approx_probability_at_least_32": 0.998926642220153,
        "quota_tail_is_exact_finite_population_probability": False,
        "model_condition": "conditional on ideal-PRP exchangeability",
    }
    if (
        planning["timed_out"]
        or planning["cancelled"]
        or planning["exit_status"] != 0
        or planning["stderr"]
        or planning_report is None
        or any(
            not exact_json_equal(planning_report.get(key), value)
            for key, value in expected_planning.items()
        )
    ):
        receipt["selftest"] = receipt_process_fields(selftest)
        receipt["reference_test"] = receipt_process_fields(reference)
        receipt["prp_verification"] = receipt_process_fields(prp_check)
        receipt["planning_stats"] = receipt_process_fields(planning)
        atomic_write_json(attempt / "receipt.json", receipt)
        write_tree_manifest(attempt)
        raise RunError(
            f"frozen planning-statistics preflight failed; immutable attempt retained at {attempt}"
        )

    contract_command = [
        shutil.which("taskset", path=RUNNER_CHILD_ENV["PATH"]) or "taskset",
        "-c",
        "0",
        sys.executable,
        *PYTHON_CHILD_FLAGS,
        str(snapshots / "test_harness_contract.py"),
    ]
    contract = run_process(contract_command, timeout=BUILD_TIMEOUT_SECONDS)
    atomic_write_bytes(attempt / "contract.stdout.log", contract["stdout"])
    atomic_write_bytes(attempt / "contract.stderr.log", contract["stderr"])
    if (
        contract["timed_out"]
        or contract["cancelled"]
        or contract["exit_status"] != 0
        or contract["stdout"] != b"harness contract ok\n"
        or contract["stderr"]
    ):
        receipt["selftest"] = receipt_process_fields(selftest)
        receipt["reference_test"] = receipt_process_fields(reference)
        receipt["prp_verification"] = receipt_process_fields(prp_check)
        receipt["planning_stats"] = receipt_process_fields(planning)
        receipt["contract_test"] = receipt_process_fields(contract)
        atomic_write_json(attempt / "receipt.json", receipt)
        write_tree_manifest(attempt)
        raise RunError(
            f"harness contract test failed; immutable attempt retained at {attempt}"
        )

    receipt.update(
        status="complete",
        binary_sha256=sha256_file(binary),
        binary_bytes=binary.stat().st_size,
        static_elf=static_elf,
        selftest={
            **receipt_process_fields(selftest),
            "stdout_sha256": sha256_file(attempt / "selftest.stdout.log"),
            "stderr_sha256": sha256_file(attempt / "selftest.stderr.log"),
            "requested_affinity": [0],
        },
        reference_test={
            **receipt_process_fields(reference),
            "source_sha256": sha256_file(snapshots / "test_sieve_reference.py"),
            "stdout_sha256": sha256_file(attempt / "reference.stdout.log"),
            "stderr_sha256": sha256_file(attempt / "reference.stderr.log"),
            "requested_affinity": [0],
        },
        prp_verification={
            **receipt_process_fields(prp_check),
            "source_sha256": sha256_file(snapshots / "verify_prp.py"),
            "stdout_sha256": sha256_file(attempt / "prp-verification.stdout.json"),
            "stderr_sha256": sha256_file(attempt / "prp-verification.stderr.log"),
            "requested_affinity": [0],
            "report_schema": prp_report["schema"],
            "derived_key_hex": prp_report["derived_key_hex"],
        },
        planning_stats={
            **receipt_process_fields(planning),
            "source_sha256": sha256_file(snapshots / "planning_stats.py"),
            "stdout_sha256": sha256_file(attempt / "planning-stats.stdout.json"),
            "stderr_sha256": sha256_file(attempt / "planning-stats.stderr.log"),
            "requested_affinity": [0],
            **expected_planning,
        },
        contract_test={
            **receipt_process_fields(contract),
            "source_sha256": sha256_file(snapshots / "test_harness_contract.py"),
            "stdout_sha256": sha256_file(attempt / "contract.stdout.log"),
            "stderr_sha256": sha256_file(attempt / "contract.stderr.log"),
            "requested_affinity": [0],
        },
    )
    atomic_write_json(attempt / "receipt.json", receipt)
    write_tree_manifest(attempt)
    promote_directory(attempt, final)
    return final / "search", receipt


def verify_built_scanner(out: Path, receipt: dict[str, Any]) -> Path:
    build = out / "build"
    verify_tree_manifest(build)
    binary = build / "search"
    if (
        binary.is_symlink()
        or not binary.is_file()
        or sha256_file(binary) != receipt.get("binary_sha256")
        or not exact_json_equal(verify_static_elf(binary), receipt.get("static_elf"))
    ):
        raise RunError("built scanner changed after its sealed build phase")
    return binary


def validate_bijection_range(seed: int, start: int, count: int) -> None:
    # The fixed root seed drives point-probe generation only.  The coefficient
    # permutation is seed independent, which makes the scanned b values unique.
    if not 0 <= seed <= UINT64_MASK:
        raise RunError("scan root seed is outside the uint64 domain")
    if not 0 <= start < FIELD_SIZE or count <= 0 or start + count > FIELD_SIZE:
        raise RunError("scan interval is outside the indexed 51-bit domain")
    if start <= PRP_ZERO_PREIMAGE < start + count:
        raise RunError("scan interval contains the unique singular b=0 preimage")


def permuted_b(seed: int, global_index: int) -> int:
    """Independent implementation of search.c's seed-independent 51-bit PRP."""
    if not 0 <= seed <= UINT64_MASK or not 0 <= global_index < FIELD_SIZE:
        raise RunError("coefficient permutation input is outside its frozen domain")

    def mix64(value: int) -> int:
        value &= UINT64_MASK
        value = ((value ^ (value >> 30)) * 0xBF58476D1CE4E5B9) & UINT64_MASK
        value = ((value ^ (value >> 27)) * 0x94D049BB133111EB) & UINT64_MASK
        return (value ^ (value >> 31)) & UINT64_MASK

    left = (global_index >> 25) & ((1 << 26) - 1)
    right = global_index & ((1 << 25) - 1)
    left_bits, right_bits = 26, 25
    for key in FEISTEL_KEYS:
        output = mix64(right ^ key ^ (right_bits << 56)) & ((1 << left_bits) - 1)
        left, right = right, left ^ output
        left_bits, right_bits = right_bits, left_bits
    return ((left & ((1 << 26) - 1)) << 25) | (right & ((1 << 25) - 1))


def derive_endpoint_seed(domain: bytes, hit: dict[str, int]) -> int:
    digest = hashlib.sha256()
    digest.update(domain)
    digest.update(bytes.fromhex(PRP_DERIVED_KEY_HEX))
    for field in SEARCH_HEADER:
        digest.update(hit[field].to_bytes(8, "big"))
    seed = int.from_bytes(digest.digest()[:8], "big") & ((1 << 63) - 1)
    return seed or 1


def control_endpoint_seed(label: str, *, target: bool) -> int:
    domain = (
        b"m51-deep-scan/v1/control-target/"
        if target
        else b"m51-deep-scan/v1/control-source/"
    )
    seed = int.from_bytes(
        hashlib.sha256(domain + label.encode("ascii")).digest()[:8], "big"
    ) & ((1 << 63) - 1)
    return seed or 1


def validate_hits(
    path: Path, layout: ScanLayout, shard_id: int
) -> list[dict[str, int]]:
    start, count = layout.interval(shard_id)
    expected_header = MOCK_HEADER if layout.mock else SEARCH_HEADER
    rows: list[dict[str, int]] = []
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != expected_header:
            raise RunError(f"{path}: output schema differs from {expected_header}")
        for line_number, row in enumerate(reader, 2):
            if None in row or any(value is None for value in row.values()):
                raise RunError(f"{path}:{line_number}: malformed CSV row")
            index = decimal_uint(row["global_index"], f"{path}:{line_number}:global_index")
            b = decimal_uint(row["b"], f"{path}:{line_number}:b", maximum=FIELD_MASK)
            coordinates = {
                field: decimal_uint(
                    row[field], f"{path}:{line_number}:{field}", maximum=FIELD_MASK
                )
                for field in ("x0", "x1", "x2")
            }
            if not start <= index < start + count:
                raise RunError(f"{path}:{line_number}: index outside shard interval")
            if rows and index <= rows[-1]["global_index"]:
                raise RunError(f"{path}:{line_number}: indices are not strictly increasing")
            if layout.mock:
                if row["record_kind"] != "MOCK_FIXTURE" or b != 0:
                    raise RunError(f"{path}:{line_number}: invalid mock-only fixture")
            else:
                expected_b = permuted_b(layout.probe_root_seed, index)
                if b == 0 or b != expected_b:
                    raise RunError(
                        f"{path}:{line_number}: coefficient differs from indexed bijection"
                    )
            rows.append(
                {
                    "global_index": index,
                    "b": b,
                    **coordinates,
                }
            )
    if layout.mock and [row["global_index"] for row in rows] != list(
        range(start, start + count)
    ):
        raise RunError(f"{path}: mock scan did not emit every fixture rank")
    return rows


def validate_shard_receipt(
    out: Path,
    final: Path,
    binary: Path,
    layout: ScanLayout,
    shard_id: int,
    receipt: dict[str, Any],
) -> list[dict[str, int]]:
    start, count = layout.interval(shard_id)
    core = CORES[shard_id % WORKERS]
    expected_fields = {
        "schema",
        "status",
        "shard_id",
        "start",
        "count",
        "end",
        "probe_root_seed",
        "core",
        "requested_affinity",
        "mock",
        "binary_sha256",
        "scientific_eligible",
        *PROCESS_RECEIPT_FIELDS,
        "stdout_sha256",
        "stderr_sha256",
        "hits_sha256",
        "hits_bytes",
        "hit_rows",
        "first_hit_index",
        "last_hit_index",
    }
    taskset = shutil.which("taskset", path=RUNNER_CHILD_ENV["PATH"])
    if taskset is None:
        raise RunError("shard validation cannot resolve taskset")
    command = receipt.get("command")
    if not isinstance(command, list) or len(command) != 9:
        raise RunError(f"existing shard command is malformed: {final}")
    recorded_hits = Path(str(command[-1]))
    expected_attempt_parent = out / "attempts" / "scan" / f"shard-{shard_id:03d}"
    mode = "mock-scan" if layout.mock else "scan"
    expected_command = [
        taskset,
        "-c",
        str(core),
        str(binary),
        mode,
        str(layout.probe_root_seed),
        str(start),
        str(count),
        str(recorded_hits),
    ]
    if (
        set(receipt) != expected_fields
        or receipt.get("schema") != "m51-deep-scan-shard-receipt/v1"
        or receipt.get("status") != "complete"
        or not exact_int_equal(receipt.get("shard_id"), shard_id)
        or not exact_int_equal(receipt.get("start"), start)
        or not exact_int_equal(receipt.get("count"), count)
        or not exact_int_equal(receipt.get("end"), start + count)
        or not exact_int_equal(receipt.get("probe_root_seed"), layout.probe_root_seed)
        or not exact_int_equal(receipt.get("core"), core)
        or not exact_int_list(receipt.get("requested_affinity"), [core])
        or receipt.get("mock") is not layout.mock
        or receipt.get("scientific_eligible") is not (not layout.mock)
        or receipt.get("binary_sha256") != sha256_file(binary)
        or command != expected_command
        or recorded_hits.name != "hits.csv"
        or recorded_hits.parent.parent != expected_attempt_parent
        or not is_attempt_directory_name(recorded_hits.parent.name)
    ):
        raise RunError(f"existing shard receipt differs from frozen range: {final}")
    validate_process_receipt(
        receipt, expected_command=expected_command, expected_cwd=None, context=str(final)
    )
    expected_stderr = (
        b"MOCK-SCAN ONLY: writing tagged singular fixtures, not scientific data\n"
        if layout.mock
        else b""
    )
    require_log(final / "stdout.log", receipt.get("stdout_sha256"), b"", str(final))
    require_log(
        final / "stderr.log", receipt.get("stderr_sha256"), expected_stderr, str(final)
    )
    hits = final / "hits.csv"
    hit_rows = validate_hits(hits, layout, shard_id)
    if (
        receipt.get("hits_sha256") != sha256_file(hits)
        or not exact_int_equal(receipt.get("hits_bytes"), hits.stat().st_size)
        or not exact_int_equal(receipt.get("hit_rows"), len(hit_rows))
        or (
            receipt.get("first_hit_index") is not None
            if not hit_rows
            else not exact_int_equal(
                receipt.get("first_hit_index"), hit_rows[0]["global_index"]
            )
        )
        or (
            receipt.get("last_hit_index") is not None
            if not hit_rows
            else not exact_int_equal(
                receipt.get("last_hit_index"), hit_rows[-1]["global_index"]
            )
        )
    ):
        raise RunError(f"existing shard hit metadata mismatch: {final}")
    return hit_rows


def scan_shard(
    out: Path,
    binary: Path,
    layout: ScanLayout,
    shard_id: int,
    stop: threading.Event,
) -> dict[str, Any]:
    label = f"shard-{shard_id:03d}"
    final = out / "chunks" / label
    start, count = layout.interval(shard_id)
    core = CORES[shard_id % WORKERS]
    if final.exists():
        verify_tree_manifest(final)
        receipt = load_json(final / "receipt.json")
        validate_shard_receipt(out, final, binary, layout, shard_id, receipt)
        return receipt

    attempt = allocate_attempt(out, "scan", label)
    hits = attempt / "hits.csv"
    mode = "mock-scan" if layout.mock else "scan"
    command = [
        shutil.which("taskset", path=RUNNER_CHILD_ENV["PATH"]) or "taskset",
        "-c",
        str(core),
        str(binary),
        mode,
        str(layout.probe_root_seed),
        str(start),
        str(count),
        str(hits),
    ]
    process = run_process(command, timeout=SHARD_TIMEOUT_SECONDS, cancel=stop)
    write_process_logs(attempt, process)
    receipt: dict[str, Any] = {
        "schema": "m51-deep-scan-shard-receipt/v1",
        "status": "failed",
        "shard_id": shard_id,
        "start": start,
        "count": count,
        "end": start + count,
        "probe_root_seed": layout.probe_root_seed,
        "core": core,
        "requested_affinity": [core],
        "mock": layout.mock,
        "binary_sha256": sha256_file(binary),
        "scientific_eligible": False,
        **receipt_process_fields(process),
        "stdout_sha256": sha256_file(attempt / "stdout.log"),
        "stderr_sha256": sha256_file(attempt / "stderr.log"),
    }
    try:
        if process["timed_out"] or process["cancelled"] or process["exit_status"] != 0:
            raise RunError(
                f"{label}: scanner exit={process['exit_status']} "
                f"timeout={process['timed_out']} cancelled={process['cancelled']}"
            )
        if process["stdout"]:
            raise RunError(f"{label}: scanner unexpectedly emitted stdout")
        if layout.mock:
            banner = b"MOCK-SCAN ONLY: writing tagged singular fixtures, not scientific data\n"
            if process["stderr"] != banner:
                raise RunError(f"{label}: mock scanner banner mismatch")
        elif process["stderr"]:
            raise RunError(f"{label}: scientific scanner unexpectedly emitted stderr")
        if not hits.is_file() or hits.is_symlink():
            raise RunError(f"{label}: scanner did not create a regular hits.csv")
        fsync_file(hits)
        hit_rows = validate_hits(hits, layout, shard_id)
        receipt.update(
            status="complete",
            hits_sha256=sha256_file(hits),
            hits_bytes=hits.stat().st_size,
            hit_rows=len(hit_rows),
            first_hit_index=hit_rows[0]["global_index"] if hit_rows else None,
            last_hit_index=hit_rows[-1]["global_index"] if hit_rows else None,
            scientific_eligible=not layout.mock,
        )
    except BaseException as exc:
        receipt["error"] = repr(exc)
        atomic_write_json(attempt / "receipt.json", receipt)
        write_tree_manifest(attempt)
        raise
    atomic_write_json(attempt / "receipt.json", receipt)
    write_tree_manifest(attempt)
    promote_directory(attempt, final)
    return receipt


def expected_global_hit_rows(out: Path, layout: ScanLayout) -> list[dict[str, int]]:
    if layout.mock:
        raise RunError("mock fixtures cannot form a scientific aggregate")
    rows: list[dict[str, int]] = []
    for shard_id in range(layout.shards):
        chunk = out / "chunks" / f"shard-{shard_id:03d}"
        if not chunk.is_dir():
            raise RunError(f"missing completed shard before aggregation: {chunk}")
        verify_tree_manifest(chunk)
        rows.extend(validate_hits(chunk / "hits.csv", layout, shard_id))
    indices = [row["global_index"] for row in rows]
    if any(right <= left for left, right in zip(indices, indices[1:])):
        raise RunError("concatenated shard hits are not globally strictly increasing")
    return rows


def validate_global_hits(
    path: Path, expected_rows: list[dict[str, int]]
) -> list[dict[str, int]]:
    actual: list[dict[str, int]] = []
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != SEARCH_HEADER:
            raise RunError(f"{path}: global hit schema mismatch")
        for line_number, row in enumerate(reader, 2):
            if None in row or any(value is None for value in row.values()):
                raise RunError(f"{path}:{line_number}: malformed global hit row")
            parsed = {
                field: decimal_uint(
                    row[field], f"{path}:{line_number}:{field}", maximum=FIELD_MASK
                )
                for field in SEARCH_HEADER
                if field != "global_index"
            }
            parsed["global_index"] = decimal_uint(
                row["global_index"], f"{path}:{line_number}:global_index"
            )
            actual.append(
                {
                    "global_index": parsed["global_index"],
                    "b": parsed["b"],
                    "x0": parsed["x0"],
                    "x1": parsed["x1"],
                    "x2": parsed["x2"],
                }
            )
    if actual != expected_rows:
        raise RunError("global hits.csv is not the exact ordered concatenation of shards")
    return actual


def validate_aggregate_receipt(
    out: Path,
    final: Path,
    layout: ScanLayout,
    rows: list[dict[str, int]],
    receipt: dict[str, Any],
) -> None:
    validate_utc_timestamp(receipt.get("created_utc"), "aggregate:created_utc")
    expected_chunk_hashes = {
        f"shard-{shard_id:03d}": sha256_file(
            out / "chunks" / f"shard-{shard_id:03d}" / "hits.csv"
        )
        for shard_id in range(layout.shards)
    }
    hits = final / "hits.csv"
    if (
        set(receipt)
        != {
            "schema",
            "status",
            "created_utc",
            "range",
            "shards",
            "rows",
            "first_hit_index",
            "last_hit_index",
            "hits_sha256",
            "hits_bytes",
            "chunk_hit_hashes",
        }
        or receipt.get("schema") != "m51-deep-global-hits-receipt/v1"
        or receipt.get("status") != "complete"
        or not exact_int_list(receipt.get("range"), [layout.start, layout.end])
        or not exact_int_equal(receipt.get("shards"), layout.shards)
        or not exact_int_equal(receipt.get("rows"), len(rows))
        or (
            receipt.get("first_hit_index") is not None
            if not rows
            else not exact_int_equal(
                receipt.get("first_hit_index"), rows[0]["global_index"]
            )
        )
        or (
            receipt.get("last_hit_index") is not None
            if not rows
            else not exact_int_equal(
                receipt.get("last_hit_index"), rows[-1]["global_index"]
            )
        )
        or receipt.get("hits_sha256") != sha256_file(hits)
        or not exact_int_equal(receipt.get("hits_bytes"), hits.stat().st_size)
        or receipt.get("chunk_hit_hashes") != expected_chunk_hashes
    ):
        raise RunError("global hit aggregate receipt differs from reconstruction")


def build_global_hits(
    out: Path, layout: ScanLayout
) -> tuple[Path, list[dict[str, int]], dict[str, Any]]:
    expected_rows = expected_global_hit_rows(out, layout)
    final = out / "aggregate"
    if final.exists():
        verify_tree_manifest(final)
        receipt = load_json(final / "receipt.json")
        rows = validate_global_hits(final / "hits.csv", expected_rows)
        validate_aggregate_receipt(out, final, layout, rows, receipt)
        return final / "hits.csv", rows, receipt

    attempt = allocate_attempt(out, "aggregate", "global-hits")
    hits = attempt / "hits.csv"
    with hits.open("x", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=SEARCH_HEADER, lineterminator="\n")
        writer.writeheader()
        writer.writerows(expected_rows)
        handle.flush()
        os.fsync(handle.fileno())
    rows = validate_global_hits(hits, expected_rows)
    chunk_hashes = {
        f"shard-{shard_id:03d}": sha256_file(
            out / "chunks" / f"shard-{shard_id:03d}" / "hits.csv"
        )
        for shard_id in range(layout.shards)
    }
    receipt = {
        "schema": "m51-deep-global-hits-receipt/v1",
        "status": "complete",
        "created_utc": utc_now(),
        "range": [layout.start, layout.end],
        "shards": layout.shards,
        "rows": len(rows),
        "first_hit_index": rows[0]["global_index"] if rows else None,
        "last_hit_index": rows[-1]["global_index"] if rows else None,
        "hits_sha256": sha256_file(hits),
        "hits_bytes": hits.stat().st_size,
        "chunk_hit_hashes": chunk_hashes,
    }
    validate_aggregate_receipt(out, attempt, layout, rows, receipt)
    atomic_write_json(attempt / "receipt.json", receipt)
    write_tree_manifest(attempt)
    promote_directory(attempt, final)
    return final / "hits.csv", rows, receipt


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    try:
        with path.open() as handle:
            for line_number, line in enumerate(handle, 1):
                if not line.endswith("\n"):
                    raise RunError(f"{path}:{line_number}: line is not newline terminated")
                try:
                    value = strict_json_loads(line, f"{path}:{line_number}")
                except RunError as exc:
                    raise RunError(f"{path}:{line_number}: invalid JSON") from exc
                if not isinstance(value, dict):
                    raise RunError(f"{path}:{line_number}: expected JSON object")
                records.append(value)
    except OSError as exc:
        raise RunError(f"cannot read {path}: {exc}") from exc
    return records


def parse_source_hit(value: Any, context: str) -> dict[str, int]:
    if not isinstance(value, dict) or set(value) != set(SEARCH_HEADER):
        raise RunError(
            f"{context}: source_hit must contain exactly global_index,b,x0,x1,x2"
        )
    return {
        field: canonical_uint(
            value[field],
            f"{context}:{field}",
            maximum=FIELD_MASK if field != "global_index" else None,
        )
        for field in SEARCH_HEADER
    }


def validate_certificate_reference(
    raw: dict[str, Any], payload: Path, context: str
) -> tuple[str, str]:
    relative = raw.get("certificate_path")
    expected_hash = raw.get("certificate_sha256")
    if (
        not isinstance(relative, str)
        or not safe_manifest_name(relative)
        or len(PurePosixPath(relative).parts) < 2
        or PurePosixPath(relative).parts[0] != "certificates"
    ):
        raise RunError(f"{context}: certificate_path is not under certificates/")
    if (
        not isinstance(expected_hash, str)
        or len(expected_hash) != 64
        or any(character not in "0123456789abcdef" for character in expected_hash)
    ):
        raise RunError(f"{context}: malformed certificate_sha256")
    certificate = payload / relative
    cursor = certificate
    while cursor != payload:
        if cursor.is_symlink():
            raise RunError(f"{context}: symlink forbidden in certificate path")
        cursor = cursor.parent
    if not certificate.is_file() or not stat.S_ISREG(certificate.stat().st_mode):
        raise RunError(f"{context}: certificate is missing or non-regular: {relative}")
    actual_hash = sha256_file(certificate)
    if actual_hash != expected_hash:
        raise RunError(
            f"{context}: certificate hash {actual_hash} differs from {expected_hash}"
        )
    return relative, expected_hash


def parse_endpoint_certificate(
    path: Path,
    source_hit: dict[str, int],
    status: str,
    admitted_failure: bool,
    control_mode: int,
    census_sha256: str,
    expected_source_seed: int,
    expected_target_seed: int,
    context: str,
) -> dict[str, str]:
    try:
        raw = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise RunError(f"{context}: cannot decode endpoint certificate") from exc
    if not raw or not raw.endswith("\n"):
        raise RunError(f"{context}: certificate is empty or not newline terminated")
    certificate: dict[str, str] = {}
    keys: list[str] = []
    for line_number, line in enumerate(raw.splitlines(), 1):
        if "=" not in line:
            raise RunError(f"{context}: certificate line {line_number} lacks '='")
        key, value = line.split("=", 1)
        if not key or key in certificate:
            raise RunError(f"{context}: empty or duplicate certificate key")
        certificate[key] = value
        keys.append(key)
    unknown_fields = set(certificate) - CERTIFICATE_ALLOWED_FIELDS
    if unknown_fields:
        raise RunError(
            f"{context}: certificate has unknown fields {sorted(unknown_fields)}"
        )
    if (
        keys[-1] != "status"
        or keys.count("status") != 1
        or keys.count("admitted_failure") != 1
    ):
        raise RunError(f"{context}: certificate lacks one terminal status")

    actual_fields = set(certificate)
    exact_field_options: tuple[set[str], ...]
    if status in {"SIEVE_FALSE_POSITIVE_ORDER", "KNOWN_CRATER", "KNOWN_F271"}:
        exact_field_options = (CERTIFICATE_BASE_FIELDS,)
    elif status == "DIRECT_PARENT":
        exact_field_options = (CERTIFICATE_DIRECT_PARENT_FIELDS,)
    elif status in {
        "CERTIFIED_BOTTOM_PARENT", "POSITIVE_CONTROL_F271_TO_CRATER"
    }:
        exact_field_options = (CERTIFICATE_FULL_EDGE_FIELDS,)
    elif status == "POSITIVE_CONTROL_BOTTOM_PARENT":
        exact_field_options = (CERTIFICATE_FULL_EDGE_FIELDS | {"pilot_exclusion_scope"},)
    elif status == "EXCLUDED_PILOT_ORBIT":
        scope = certificate.get("pilot_exclusion_scope")
        if scope == "source-orbit":
            exact_field_options = (CERTIFICATE_BASE_FIELDS | {"pilot_exclusion_scope"},)
        elif scope == "entire-parent-fiber":
            exact_field_options = (
                CERTIFICATE_FULL_EDGE_FIELDS | {"pilot_exclusion_scope"},
            )
        else:
            exact_field_options = ()
    elif status == "UNKNOWN_EMBEDDING_EXHAUSTED":
        exact_field_options = (CERTIFICATE_BASE_FIELDS | {"embedding_attempts"},)
    elif status == "UNKNOWN_WITNESS_EXHAUSTED":
        exact_field_options = (CERTIFICATE_WITNESS_SUMMARY_FIELDS,)
    elif status in {"TARGET_RANK2_WITNESS_EXHAUSTED", "ASCENT_FAILED"}:
        exact_field_options = (CERTIFICATE_WITNESS_DETAIL_FIELDS,)
    elif status == "INVALID_CERTIFICATE":
        exact_field_options = (
            CERTIFICATE_WITNESS_SUMMARY_FIELDS,
            CERTIFICATE_WITNESS_DETAIL_FIELDS,
            CERTIFICATE_FULL_EDGE_FIELDS,
        )
    elif status == "WRONG_ORBIT_SIZE":
        exact_field_options = (CERTIFICATE_BASE_FIELDS, CERTIFICATE_FULL_EDGE_FIELDS)
    elif status == "WRONG_PARENT_ORDER":
        exact_field_options = (
            CERTIFICATE_WITNESS_DETAIL_FIELDS,
            CERTIFICATE_FULL_EDGE_FIELDS,
        )
    elif status == "GP_ERROR":
        exact_field_options = (CERTIFICATE_GP_ERROR_FIELDS,)
    else:
        exact_field_options = ()
    if not any(actual_fields == option for option in exact_field_options):
        closest = min(
            exact_field_options,
            key=lambda option: len(actual_fields ^ option),
            default=set(),
        )
        raise RunError(
            f"{context}: certificate fields differ from status schema; "
            f"missing={sorted(closest-actual_fields)}, extra={sorted(actual_fields-closest)}"
        )
    expected_fixed = {
        "schema": "m51-deep-endpoint-certificate/v1",
        "global_index": str(source_hit["global_index"]),
        "source_b": str(source_hit["b"]),
        "source_a2": "0",
        "expected_order": str(AMBIENT_ORDER),
        "field_degree": str(FIELD_BITS),
        "f_pi": str(F_PI),
        "f271_census_sha256": census_sha256,
        "f271_census_source_revision": CENSUS_SOURCE_REVISION,
        "f271_census_source_sha256": CENSUS_SOURCE_SHA256,
        "f271_census_complete_orbit_count": "16",
        "control_mode": str(control_mode),
        "status": status,
        "admitted_failure": "1" if admitted_failure else "0",
    }
    if status != "GP_ERROR":
        expected_fixed.update(
            field_modulus_bits=str((1 << 51) + (1 << 6) + (1 << 3) + 2 + 1),
            class_trace=str((1 << 51) + 1 - AMBIENT_ORDER),
            class_discriminant=str(-7 * F_PI**2),
            f_pi_factorization="271*120871",
            f_pi_factor_primality="1",
        )
    for key, expected in expected_fixed.items():
        if certificate.get(key) != expected:
            raise RunError(
                f"{context}: certificate {key}={certificate.get(key)!r}, expected {expected!r}"
            )

    seed_fields = {
        "embedding_seed": EMBED_SEED,
        "witness_seed": expected_source_seed,
        "target_witness_seed": expected_target_seed,
        "witness_count_required": WITNESS_COUNT,
        "witness_attempt_cap": MAX_WITNESS_ATTEMPTS,
    }
    deep_seed_statuses = {
        "DIRECT_PARENT",
        "CERTIFIED_BOTTOM_PARENT",
        "POSITIVE_CONTROL_BOTTOM_PARENT",
        "POSITIVE_CONTROL_F271_TO_CRATER",
        "UNKNOWN_WITNESS_EXHAUSTED",
        "TARGET_RANK2_WITNESS_EXHAUSTED",
        "INVALID_CERTIFICATE",
        "ASCENT_FAILED",
        "WRONG_PARENT_ORDER",
    }
    require_seed_fields = status in deep_seed_statuses or (
        status == "EXCLUDED_PILOT_ORBIT"
        and certificate.get("pilot_exclusion_scope") == "entire-parent-fiber"
    )
    if require_seed_fields or set(seed_fields) & set(certificate):
        for key, expected in seed_fields.items():
            if certificate.get(key) != str(expected):
                raise RunError(
                    f"{context}: certificate {key} is not the deterministic frozen value"
                )

    def cert_uint(key: str) -> int:
        value = certificate.get(key)
        if (
            not isinstance(value, str)
            or not value.isascii()
            or not value.isdecimal()
            or len(value) > MAX_CERT_DECIMAL_DIGITS
            or (value != "0" and value.startswith("0"))
        ):
            raise RunError(f"{context}: certificate {key} is not canonical unsigned decimal")
        try:
            return int(value)
        except ValueError as exc:
            raise RunError(f"{context}: certificate {key} is not a bounded integer") from exc

    def cert_sint(key: str) -> int:
        value = certificate.get(key)
        if not isinstance(value, str):
            raise RunError(f"{context}: certificate {key} is not an integer")
        digits = value[1:] if value.startswith("-") else value
        if (
            not digits
            or not digits.isascii()
            or not digits.isdecimal()
            or len(digits) > MAX_CERT_DECIMAL_DIGITS
            or (digits != "0" and digits.startswith("0"))
            or value == "-0"
        ):
            raise RunError(f"{context}: certificate {key} is not a canonical integer")
        try:
            return int(value)
        except ValueError as exc:
            raise RunError(f"{context}: certificate {key} is not a bounded integer") from exc

    def cert_uint_vector(key: str, expected_length: int) -> list[int]:
        value = certificate.get(key)
        if not isinstance(value, str) or not value.startswith("[") or not value.endswith("]"):
            raise RunError(f"{context}: certificate {key} is not a GP integer vector")
        body = value[1:-1]
        pieces = [] if not body else body.split(", ")
        if len(pieces) != expected_length:
            raise RunError(
                f"{context}: certificate {key} has {len(pieces)} entries, "
                f"expected {expected_length}"
            )
        parsed: list[int] = []
        for number, piece in enumerate(pieces, 1):
            if (
                not piece.isascii()
                or not piece.isdecimal()
                or len(piece) > MAX_CERT_DECIMAL_DIGITS
                or (piece != "0" and piece.startswith("0"))
            ):
                raise RunError(f"{context}: certificate {key}[{number}] is noncanonical")
            try:
                parsed.append(int(piece))
            except ValueError as exc:
                raise RunError(
                    f"{context}: certificate {key}[{number}] is not bounded"
                ) from exc
        if len(set(parsed)) != len(parsed):
            raise RunError(f"{context}: certificate {key} contains duplicate x values")
        return parsed

    for key in actual_fields - CERTIFICATE_TEXT_FIELDS:
        if key in CERTIFICATE_SIGNED_INTEGER_FIELDS:
            cert_sint(key)
        else:
            cert_uint(key)
    if not 1 <= cert_uint("source_b") <= FIELD_MASK:
        raise RunError(f"{context}: source coefficient is outside nonzero GF(2^51)")

    for key, expected in {
        "class_discriminant_271_valuation": 2,
        "kernel_extension_coprime_to_271": 1,
        "maximal_order_class_number": 1,
    }.items():
        if cert_uint(key) != expected:
            raise RunError(f"{context}: certificate arithmetic lemma {key} failed")

    if status != "GP_ERROR":
        source_orbit_size = cert_uint("source_orbit_size")
        source_frobenius_power = cert_uint("source_to_orbit_rep_frobenius_power")
        if source_orbit_size == 0 or source_frobenius_power >= source_orbit_size:
            raise RunError(f"{context}: source orbit replay metadata is out of range")

    if "embedding_seed" in certificate:
        for key, expected in {
            "kernel_prime": 271,
            "kernel_field_degree": 51 * 45,
            "kernel_extension_degree": 45,
            "kernel_twist": 1,
            "extension_group_271_valuation": 2,
            "other_twist_271_valuation": 0,
            "embedding_modulus_check": 1,
        }.items():
            if cert_uint(key) != expected:
                raise RunError(f"{context}: extension replay field {key} failed")
        q = 1 << FIELD_BITS
        base_trace = q + 1 - AMBIENT_ORDER
        trace_previous, expected_extension_trace = 2, base_trace
        for _ in range(2, 45 + 1):
            trace_previous, expected_extension_trace = (
                expected_extension_trace,
                base_trace * expected_extension_trace - q * trace_previous,
            )
        extension_order = q**45 + 1 + expected_extension_trace
        expected_cofactor = extension_order // (271**2)
        if cert_sint("extension_trace") != expected_extension_trace:
            raise RunError(f"{context}: extension trace differs from recurrence")
        if cert_uint("extension_group_cofactor") != expected_cofactor:
            raise RunError(f"{context}: extension cofactor differs from trace/order")
        for key in ("extension_modulus_bits", "embedding_x_int", "embedded_b_int"):
            if cert_uint(key) <= 0:
                raise RunError(f"{context}: extension replay field {key} is not positive")
        if hashlib.sha256(certificate["extension_modulus_bits"].encode()).hexdigest() != EXTENSION_MODULUS_DECIMAL_SHA256:
            raise RunError(f"{context}: extension polynomial differs from the pinned GP field")
        if hashlib.sha256(certificate["embedding_x_int"].encode()).hexdigest() != EMBEDDING_X_DECIMAL_SHA256:
            raise RunError(f"{context}: base-field embedding differs from the pinned replay")
        embedding_attempts = cert_uint("embedding_attempts")
        if embedding_attempts != 1:
            raise RunError(f"{context}: embedding attempt count is out of range")
    elif "embedding_attempts" in certificate:
        embedding_attempts = cert_uint("embedding_attempts")
        if (
            not 1 <= embedding_attempts <= MAX_WITNESS_ATTEMPTS
            or (
                status == "UNKNOWN_EMBEDDING_EXHAUSTED"
                and embedding_attempts != MAX_WITNESS_ATTEMPTS
            )
        ):
            raise RunError(f"{context}: exhausted embedding attempt count is invalid")

    if "witness_attempts_used" in certificate:
        attempts_used = cert_uint("witness_attempts_used")
        count_found = cert_uint("witness_count_found")
        other_skips = cert_uint("witness_other_twist_skips")
        infinity_skips = cert_uint("witness_infinity_skips")
        if (
            attempts_used > MAX_WITNESS_ATTEMPTS
            or count_found > WITNESS_COUNT
            or other_skips + infinity_skips > attempts_used
        ):
            raise RunError(f"{context}: source witness counters are inconsistent")
        if CERTIFICATE_WITNESS_DETAIL_FIELDS <= actual_fields and count_found != WITNESS_COUNT:
            raise RunError(f"{context}: detailed source witness set is incomplete")

    if CERTIFICATE_WITNESS_DETAIL_FIELDS <= actual_fields:
        previous_attempt = 0
        for witness in range(1, WITNESS_COUNT + 1):
            attempt = cert_uint(f"witness_{witness}_attempt")
            if not previous_attempt < attempt <= MAX_WITNESS_ATTEMPTS:
                raise RunError(f"{context}: witness attempt indices are not increasing")
            previous_attempt = attempt
            for suffix in ("raw_x_int", "order_2712_x_int", "order_271_x_int"):
                cert_uint(f"witness_{witness}_{suffix}")
            if (
                cert_uint(f"witness_{witness}_mul_271_nonzero") != 1
                or cert_uint(f"witness_{witness}_mul_2712_zero") != 1
            ):
                raise RunError(
                    f"{context}: source torsion witness {witness} flags failed"
                )
        if cert_uint("witness_attempts_used") != previous_attempt:
            raise RunError(f"{context}: witness attempt total differs from witness 3")

    if status == "UNKNOWN_WITNESS_EXHAUSTED" and (
        cert_uint("witness_attempts_used") != MAX_WITNESS_ATTEMPTS
        or cert_uint("witness_count_found") >= WITNESS_COUNT
    ):
        raise RunError(f"{context}: exhausted source witness status is inconsistent")

    if actual_fields == CERTIFICATE_DIRECT_PARENT_FIELDS:
        if cert_uint("witness_count_found") != 0:
            raise RunError(f"{context}: direct-parent branch retained cyclic witnesses")
        direct_point_1 = cert_uint("direct_parent_point_1_x_int")
        direct_point_2 = cert_uint("direct_parent_point_2_x_int")
        direct_xset = cert_uint_vector("direct_parent_point_1_xset", 135)
        if direct_point_1 not in direct_xset or direct_point_2 in direct_xset:
            raise RunError(f"{context}: direct-parent independence certificate failed")
        if cert_uint("witness_attempts_used") < 1:
            raise RunError(f"{context}: direct-parent branch has no discovery attempt")
        if certificate.get("source_conductor_derivation") != (
            "two-independent-order271-x-points-full-rank"
        ):
            raise RunError(f"{context}: direct-parent conductor derivation changed")

    if CERTIFICATE_FULL_EDGE_FIELDS <= actual_fields:
        full_constants = {
            "source_order": AMBIENT_ORDER,
            "source_orbit_size": 17 if control_mode == 2 else 51,
            "source_f_E": 271 if control_mode == 2 else F_PI,
            "kernel_mul_271_zero": 1,
            "kernel_frobenius_stable": 1,
            "kernel_sums_agree": 1,
            "velu_half_kernel_sum_frobenius_fixed": 1,
            "raw_codomain_a1": 1,
            "raw_codomain_a2": 0,
            "raw_codomain_a3": 0,
            "raw_codomain_delta_nonzero": 1,
            "raw_codomain_frobenius_fixed": 1,
            "target_a2": 0,
            "target_f_E": 1 if control_mode == 2 else 120_871,
            "target_rank2_point_1_mul_271_zero": 1,
            "target_rank2_point_2_mul_271_zero": 1,
            "target_rank2_point_1_xset_count": 135,
            "target_rank2_point_2_absent_from_point_1_subgroup": 1,
            "coprime_conductor_component_preserved": 120_871,
            "coprime_conductor_preservation_check": 1,
            "edge_degree": 271,
            "edge_separable": 1,
            "map_evaluator_serialized": 0,
            "dual_serialized": 0,
            "transfer_claim_permitted": 0,
        }
        for key, expected in full_constants.items():
            if cert_uint(key) != expected:
                raise RunError(f"{context}: full-edge fixed field {key} changed")
        for key in (
            "kernel_x_int", "raw_codomain_a4_int", "raw_codomain_a6_int",
            "normalization_y_translation_int", "raw_codomain_delta_int",
            "velu_half_kernel_sum_int", "raw_target_b",
            "codomain_minpoly_bits", "target_b", "target_order", "target_orbit_rep",
            "target_rank2_point_1_x_int", "target_rank2_point_2_x_int",
        ):
            cert_uint(key)
        if (
            cert_uint("raw_target_b") == 0
            or cert_uint("codomain_minpoly_bits") == 0
            or cert_uint("target_b") == 0
        ):
            raise RunError(
                f"{context}: full-edge target/minimal-polynomial evidence is zero"
            )
        for key in ("raw_target_b", "target_b", "target_orbit_rep"):
            if not 1 <= cert_uint(key) <= FIELD_MASK:
                raise RunError(
                    f"{context}: full-edge {key} is outside nonzero GF(2^51)"
                )
        target_order = cert_uint("target_order")
        if not HASSE_MIN <= target_order <= HASSE_MAX:
            raise RunError(f"{context}: target order is outside exact Hasse interval")
        if target_order % 2:
            raise RunError(f"{context}: target order is odd despite rational 2-torsion")
        target_orbit_size = cert_uint("target_orbit_size")
        if target_orbit_size not in FIELD_ORBIT_SIZES:
            raise RunError(f"{context}: target orbit size is not a divisor of 51")
        validate_codomain_minpoly_bits(
            cert_uint("codomain_minpoly_bits"), target_orbit_size, context
        )
        if cert_uint("kernel_x_int") != cert_uint("witness_1_order_271_x_int"):
            raise RunError(f"{context}: serialized kernel differs from witness 1")
        if not 1 <= cert_uint("kernel_frobenius_x_multiplier_abs") <= 135:
            raise RunError(f"{context}: kernel Frobenius multiplier is out of range")
        velu_sum = cert_uint("velu_half_kernel_sum_int")
        if (
            cert_uint("raw_codomain_a4_int") != velu_sum
            or cert_uint("normalization_y_translation_int") != velu_sum
            or cert_uint("raw_codomain_delta_int") == 0
            or cert_uint("raw_codomain_a6_int")
            != (cert_uint("embedded_b_int") ^ velu_sum)
        ):
            raise RunError(f"{context}: full-edge quotient replay is inconsistent")
        if cert_uint("target_a2") != 0:
            raise RunError(f"{context}: normalized target model has nonzero a2")
        if cert_uint("target_orbit_rep") != cert_uint("target_b"):
            raise RunError(f"{context}: target representative differs from target_b")
        target_orbit_size = cert_uint("target_orbit_size")
        target_power = cert_uint("raw_target_to_rep_frobenius_power")
        if target_orbit_size == 0 or target_power >= target_orbit_size:
            raise RunError(f"{context}: target orbit replay metadata is out of range")
        target_attempts = cert_uint("target_rank2_attempts_used")
        target_other = cert_uint("target_rank2_other_twist_skips")
        target_infinity = cert_uint("target_rank2_infinity_skips")
        if (
            not 1 <= target_attempts <= MAX_WITNESS_ATTEMPTS
            or target_other + target_infinity > target_attempts
        ):
            raise RunError(f"{context}: target rank-two counters are inconsistent")
        target_xset = cert_uint_vector("target_rank2_point_1_xset", 135)
        if (
            cert_uint("target_rank2_point_1_x_int") not in target_xset
            or cert_uint("target_rank2_point_2_x_int") in target_xset
        ):
            raise RunError(f"{context}: target rank-two independence certificate failed")
        if cert_uint("coprime_conductor_component_preserved") != 120_871:
            raise RunError(f"{context}: coprime conductor component changed")
        expected_strings = {
            "edge_direction": "ascending",
            "edge_direction_derivation": (
                "depth-one-271-volcano-inert-prime-unique-order271-subgroup"
            ),
        }
        for key, expected in expected_strings.items():
            if certificate.get(key) != expected:
                raise RunError(f"{context}: certificate {key} differs from proof contract")
        if control_mode == 2:
            derivations = {
                "source_conductor_derivation": (
                    "control-order2712-witness-plus-frozen-source-binding"
                ),
                "f271_census_exclusion_role": "control-source-binding",
                "target_conductor_derivation": (
                    "complete-crater-binding-plus-independent-271-torsion"
                ),
            }
        else:
            derivations = {
                "source_conductor_derivation": (
                    "exact-order2712-source-plus-Fq-stable-271-kernel-plus-"
                    "certified-f120871-target"
                ),
                "f271_census_exclusion_role": "corroborating-not-load-bearing",
                "target_conductor_derivation": (
                    "crater-exclusion-plus-independent-271-torsion"
                ),
            }
        for key, expected in derivations.items():
            if certificate.get(key) != expected:
                raise RunError(f"{context}: certificate {key} differs from proof contract")

    if status == "WRONG_ORBIT_SIZE":
        if actual_fields == CERTIFICATE_BASE_FIELDS:
            expected_size = 17 if control_mode == 2 else 51
            if cert_uint("source_orbit_size") == expected_size:
                raise RunError(
                    f"{context}: WRONG_ORBIT_SIZE has the expected source size"
                )
        elif actual_fields == CERTIFICATE_FULL_EDGE_FIELDS:
            expected_size = 1 if control_mode == 2 else 51
            if cert_uint("target_orbit_size") == expected_size:
                raise RunError(
                    f"{context}: WRONG_ORBIT_SIZE has the expected target size"
                )
    if status == "WRONG_PARENT_ORDER" and actual_fields == CERTIFICATE_FULL_EDGE_FIELDS:
        if cert_uint("target_order") == AMBIENT_ORDER and cert_uint("target_a2") == 0:
            raise RunError(
                f"{context}: WRONG_PARENT_ORDER has the expected parent model/order"
            )
    if status == "INVALID_CERTIFICATE" and actual_fields == CERTIFICATE_FULL_EDGE_FIELDS:
        target_rep = cert_uint("target_orbit_rep")
        target_f = cert_uint("target_f_E")
        explains_invalid = (
            (control_mode == 2 and (target_rep != 1 or target_f != 1))
            or (control_mode == 1 and target_rep != PILOT_PARENT_ORBIT_REP)
        )
        if not explains_invalid:
            raise RunError(
                f"{context}: full INVALID_CERTIFICATE has no terminal contradiction"
            )

    if status != "GP_ERROR":
        source_order = cert_uint("source_order")
        source_rep = cert_uint("source_orbit_rep")
        source_orbit_size = cert_uint("source_orbit_size")
        if not HASSE_MIN <= source_order <= HASSE_MAX:
            raise RunError(f"{context}: source order is outside exact Hasse interval")
        if source_order % 2:
            raise RunError(f"{context}: source order is odd despite rational 2-torsion")
        if not 1 <= source_rep <= FIELD_MASK:
            raise RunError(f"{context}: source orbit representative is outside GF(2^51)")
        if source_orbit_size not in FIELD_ORBIT_SIZES:
            raise RunError(f"{context}: source orbit size is not a divisor of 51")
        if status == "SIEVE_FALSE_POSITIVE_ORDER":
            if source_order == AMBIENT_ORDER:
                raise RunError(f"{context}: in-class curve labeled a sieve false positive")
        elif source_order != AMBIENT_ORDER:
            raise RunError(f"{context}: non-class curve received an in-class status")

    def validate_deep_edge(
        source_f: int, source_orbit_size: int, target_f: int, target_orbit_size: int
    ) -> None:
        required = {
            "source_order": AMBIENT_ORDER,
            "source_orbit_size": source_orbit_size,
            "source_f_E": source_f,
            "witness_count_found": 3,
            "kernel_prime": 271,
            "kernel_extension_degree": 45,
            "extension_group_271_valuation": 2,
            "other_twist_271_valuation": 0,
            "kernel_mul_271_zero": 1,
            "kernel_frobenius_stable": 1,
            "kernel_sums_agree": 1,
            "velu_half_kernel_sum_frobenius_fixed": 1,
            "raw_codomain_a1": 1,
            "raw_codomain_a2": 0,
            "raw_codomain_a3": 0,
            "raw_codomain_delta_nonzero": 1,
            "raw_codomain_frobenius_fixed": 1,
            "target_order": AMBIENT_ORDER,
            "target_orbit_size": target_orbit_size,
            "target_f_E": target_f,
            "target_rank2_point_1_mul_271_zero": 1,
            "target_rank2_point_2_mul_271_zero": 1,
            "target_rank2_point_1_xset_count": 135,
            "target_rank2_point_2_absent_from_point_1_subgroup": 1,
            "coprime_conductor_preservation_check": 1,
            "edge_degree": 271,
            "edge_separable": 1,
            "map_evaluator_serialized": 0,
            "dual_serialized": 0,
            "transfer_claim_permitted": 0,
        }
        for key, expected in required.items():
            if cert_uint(key) != expected:
                raise RunError(f"{context}: positive endpoint certificate failed {key}")
        for witness in range(1, 4):
            if (
                cert_uint(f"witness_{witness}_mul_271_nonzero") != 1
                or cert_uint(f"witness_{witness}_mul_2712_zero") != 1
            ):
                raise RunError(f"{context}: source torsion witness {witness} failed")
        velu_sum = cert_uint("velu_half_kernel_sum_int")
        if (
            cert_uint("raw_codomain_a4_int") != velu_sum
            or cert_uint("normalization_y_translation_int") != velu_sum
            or cert_uint("raw_codomain_delta_int") == 0
        ):
            raise RunError(f"{context}: raw quotient/normalization certificate failed")
        if cert_uint("raw_codomain_a6_int") != (
            cert_uint("embedded_b_int") ^ velu_sum
        ):
            raise RunError(f"{context}: raw quotient a6 differs from B+v")
        frobenius_u = cert_uint("kernel_frobenius_x_multiplier_abs")
        if not 1 <= frobenius_u <= 135:
            raise RunError(f"{context}: kernel Frobenius multiplier is out of range")
        if cert_uint("target_orbit_rep") != cert_uint("target_b"):
            raise RunError(f"{context}: target is not its canonical orbit representative")

    if status in {"CERTIFIED_BOTTOM_PARENT", "POSITIVE_CONTROL_BOTTOM_PARENT"}:
        validate_deep_edge(F_PI, 51, 120_871, 51)
        if status == "CERTIFIED_BOTTOM_PARENT" and cert_uint("target_orbit_rep") == PILOT_PARENT_ORBIT_REP:
            raise RunError(f"{context}: pilot parent fiber was admitted")
        if status == "POSITIVE_CONTROL_BOTTOM_PARENT" and (
            cert_uint("source_orbit_rep") != PILOT_BOTTOM_ORBIT_REP
            or cert_uint("target_orbit_rep") != PILOT_PARENT_ORBIT_REP
            or certificate.get("pilot_exclusion_scope") != "entire-parent-fiber"
        ):
            raise RunError(f"{context}: pilot positive control endpoint binding failed")
    elif status == "POSITIVE_CONTROL_F271_TO_CRATER":
        validate_deep_edge(271, 17, 1, 1)
        if (
            cert_uint("source_orbit_rep") != EXPECTED_F271[0]
            or cert_uint("target_b") != 1
            or cert_uint("target_orbit_rep") != 1
        ):
            raise RunError(f"{context}: f271 positive control endpoint binding failed")
    elif status == "KNOWN_CRATER":
        if cert_uint("source_orbit_rep") != 1 or cert_uint("source_orbit_size") != 1:
            raise RunError(f"{context}: KNOWN_CRATER lacks exact crater binding")
    elif status == "KNOWN_F271":
        if cert_uint("source_orbit_rep") not in EXPECTED_F271 or cert_uint("source_orbit_size") != 17:
            raise RunError(f"{context}: KNOWN_F271 lacks frozen census binding")
    elif status == "EXCLUDED_PILOT_ORBIT":
        scope = certificate.get("pilot_exclusion_scope")
        if scope == "source-orbit":
            if (
                cert_uint("source_orbit_rep") != PILOT_BOTTOM_ORBIT_REP
                or cert_uint("source_orbit_size") != 51
            ):
                raise RunError(f"{context}: source pilot exclusion lacks exact orbit binding")
        elif scope == "entire-parent-fiber":
            validate_deep_edge(F_PI, 51, 120_871, 51)
            if cert_uint("target_orbit_rep") != PILOT_PARENT_ORBIT_REP:
                raise RunError(f"{context}: pilot-fiber exclusion lacks certified parent binding")
        else:
            raise RunError(f"{context}: pilot exclusion has unknown scope")
    elif status == "DIRECT_PARENT":
        required = {
            "source_order": AMBIENT_ORDER,
            "source_orbit_size": 51,
            "source_f_E": 120_871,
            "direct_parent_point_1_xset_count": 135,
            "direct_parent_point_2_absent_from_point_1_subgroup": 1,
        }
        for key, expected in required.items():
            if cert_uint(key) != expected:
                raise RunError(f"{context}: direct-parent certificate failed {key}")
    elif status == "GP_ERROR":
        pipeline_error = certificate.get("pipeline_error")
        if (
            not isinstance(pipeline_error, str)
            or not pipeline_error.startswith("certificate_rejected:")
            or certificate.get("gp_log_sha256")
            != hashlib.sha256(b"\0").hexdigest()
        ):
            raise RunError(f"{context}: admitted GP_ERROR lacks bound clean-batch cause")
    return certificate


def certificate_uint(certificate: dict[str, str], key: str, context: str) -> int:
    value = certificate.get(key)
    if (
        not isinstance(value, str)
        or not value.isascii()
        or not value.isdecimal()
        or len(value) > MAX_CERT_DECIMAL_DIGITS
    ):
        raise RunError(f"{context}: certificate {key} is not an unsigned decimal")
    if value != "0" and value.startswith("0"):
        raise RunError(f"{context}: certificate {key} is noncanonical")
    try:
        return int(value)
    except ValueError as exc:
        raise RunError(f"{context}: certificate {key} is not bounded") from exc


def validate_codomain_minpoly_bits(
    value: int, target_orbit_size: int, context: str
) -> None:
    if (
        value <= 0
        or value.bit_length() - 1 != target_orbit_size
        or value & 1 != 1
    ):
        raise RunError(
            f"{context}: codomain minimal polynomial is not the canonical "
            "monic degree/orbit encoding"
        )


def parse_pair(
    raw: dict[str, Any],
    context: str,
    *,
    payload: Path | None = None,
    expected_hit: dict[str, int] | None = None,
) -> Pair:
    if set(raw) != set(PAIR_FIELDS):
        raise RunError(
            f"{context}: pair fields differ from frozen schema; "
            f"missing={sorted(set(PAIR_FIELDS)-set(raw))}, "
            f"extra={sorted(set(raw)-set(PAIR_FIELDS))}"
        )
    if raw["schema"] != PAIR_SCHEMA or raw["status"] != "CERTIFIED_BOTTOM_PARENT":
        raise RunError(f"{context}: unexpected pair schema or status")
    values = {
        field: canonical_uint(raw[field], f"{context}:{field}")
        for field in (
            "global_index",
            "b",
            "a2",
            "ellcard",
            "bottom_orbit_rep",
            "bottom_orbit_size",
            "parent_b",
            "parent_a2",
            "parent_orbit_rep",
            "parent_orbit_size",
        )
    }
    if (
        values["a2"] != 0
        or values["parent_a2"] != 0
        or values["ellcard"] != AMBIENT_ORDER
        or values["bottom_orbit_size"] != 51
        or values["parent_orbit_size"] != 51
        or values["parent_b"] != values["parent_orbit_rep"]
        or not 0 < values["b"] <= FIELD_MASK
        or not 0 < values["parent_b"] <= FIELD_MASK
        or not 0 < values["bottom_orbit_rep"] <= FIELD_MASK
        or not 0 < values["parent_orbit_rep"] <= FIELD_MASK
    ):
        raise RunError(f"{context}: pair arithmetic metadata is invalid")
    source_hit = parse_source_hit(raw["source_hit"], f"{context}:source_hit")
    if expected_hit is not None:
        expected_source = {field: expected_hit[field] for field in SEARCH_HEADER}
        if source_hit != expected_source or values["b"] != expected_hit["b"]:
            raise RunError(f"{context}: pair is not bound to its originating hit")
    if payload is not None:
        validate_certificate_reference(raw, payload, context)
    else:
        certificate = raw["certificate_sha256"]
        if (
            not isinstance(certificate, str)
            or len(certificate) != 64
            or any(character not in "0123456789abcdef" for character in certificate)
            or not isinstance(raw["certificate_path"], str)
        ):
            raise RunError(f"{context}: malformed certificate reference")
    return Pair(
        raw=raw,
        global_index=values["global_index"],
        bottom_orbit_rep=values["bottom_orbit_rep"],
        parent_orbit_rep=values["parent_orbit_rep"],
    )


def eligible_pair(pair: Pair) -> bool:
    return (
        pair.bottom_orbit_rep != PILOT_BOTTOM_ORBIT_REP
        and pair.parent_orbit_rep != PILOT_PARENT_ORBIT_REP
        and canonical_uint(pair.raw["b"], "pair:b") != PILOT_BOTTOM_ORBIT_REP
        and canonical_uint(pair.raw["parent_b"], "pair:parent_b")
        != PILOT_PARENT_ORBIT_REP
    )


def validate_classification_payload(
    payload: Path,
    hit_rows: list[dict[str, int]],
    snapshots: Path,
    gp_runtime: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[Pair]]:
    validate_gp_runtime_payload(payload, gp_runtime, snapshots, "scientific classification")
    records = load_jsonl(payload / "records.jsonl")
    pairs_raw = load_jsonl(payload / "pairs.jsonl")
    selection = load_json(payload / "selection.json")
    record_indices: list[int] = []
    certified_indices: list[int] = []
    hit_by_index = {row["global_index"]: row for row in hit_rows}
    if len(hit_by_index) != len(hit_rows):
        raise RunError("hits.csv contains duplicate global indices")
    census_sha256 = sha256_file(snapshots / "floor271_orbits.csv")
    certificate_by_index: dict[int, dict[str, str]] = {}
    for number, record in enumerate(records, 1):
        context = f"{payload/'records.jsonl'}:{number}"
        if set(record) != RECORD_FIELDS:
            raise RunError(
                f"{context}: record fields differ from frozen schema; "
                f"missing={sorted(RECORD_FIELDS-set(record))}, "
                f"extra={sorted(set(record)-RECORD_FIELDS)}"
            )
        if record.get("schema") != "m51-deep-classification-record/v1":
            raise RunError(f"{context}: classification record schema mismatch")
        index = canonical_uint(record.get("global_index"), f"{context}:global_index")
        status_value = record.get("status")
        admitted = record.get("admitted_failure")
        if not isinstance(status_value, str) or status_value not in BENIGN_STATUSES | FATAL_STATUSES:
            raise RunError(f"{context}: unknown pipeline status {status_value!r}")
        if not isinstance(admitted, bool) or admitted != (status_value in FATAL_STATUSES):
            raise RunError(f"{context}: admitted_failure/status mismatch")
        expected_hit = hit_by_index.get(index)
        if expected_hit is None:
            raise RunError(f"{context}: record index is absent from hits.csv")
        source_hit = parse_source_hit(record.get("source_hit"), f"{context}:source_hit")
        expected_source = {field: expected_hit[field] for field in SEARCH_HEADER}
        top_level_hit = {
            field: canonical_uint(
                record.get(field),
                f"{context}:{field}",
                maximum=FIELD_MASK if field != "global_index" else None,
            )
            for field in SEARCH_HEADER
        }
        if source_hit != expected_source or top_level_hit != expected_source:
            raise RunError(f"{context}: record is not bound to its originating hit")
        if canonical_uint(record.get("control_mode"), f"{context}:control_mode") != 0:
            raise RunError(f"{context}: control mode is forbidden in scientific output")
        relative, _ = validate_certificate_reference(record, payload, context)
        certificate_bytes = canonical_uint(
            record.get("certificate_bytes"), f"{context}:certificate_bytes"
        )
        if certificate_bytes != (payload / relative).stat().st_size:
            raise RunError(f"{context}: certificate byte count mismatch")
        certificate_by_index[index] = parse_endpoint_certificate(
            payload / relative,
            expected_hit,
            status_value,
            admitted,
            0,
            census_sha256,
            derive_endpoint_seed(
                b"m51-deep-scan/v1/source-witness", expected_hit
            ),
            derive_endpoint_seed(b"m51-deep-scan/v1/target-rank2", expected_hit),
            context,
        )
        record_indices.append(index)
        if status_value == "CERTIFIED_BOTTOM_PARENT":
            certified_indices.append(index)
    if record_indices != [row["global_index"] for row in hit_rows]:
        raise RunError("pipeline records are not a one-for-one ordered image of hits.csv")

    pairs: list[Pair] = []
    record_by_index = {
        canonical_uint(record["global_index"], "record global_index"): record
        for record in records
    }
    for number, raw in enumerate(pairs_raw, 1):
        context = f"{payload/'pairs.jsonl'}:{number}"
        index = canonical_uint(
            raw.get("global_index"), f"{context}:global_index"
        )
        expected_hit = hit_by_index.get(index)
        if expected_hit is None:
            raise RunError("pipeline pair index is absent from hits.csv")
        pair = parse_pair(
            raw,
            context,
            payload=payload,
            expected_hit=expected_hit,
        )
        source_record = record_by_index[index]
        if (
            raw["source_hit"] != source_record["source_hit"]
            or raw["certificate_path"] != source_record["certificate_path"]
            or raw["certificate_sha256"] != source_record["certificate_sha256"]
        ):
            raise RunError("pipeline pair certificate/source differs from its decision record")
        certificate = certificate_by_index[index]
        expected_certificate_values = {
            "source_order": AMBIENT_ORDER,
            "source_orbit_rep": pair.bottom_orbit_rep,
            "source_orbit_size": canonical_uint(
                raw["bottom_orbit_size"], "pair bottom_orbit_size"
            ),
            "target_b": canonical_uint(raw["parent_b"], "pair parent_b"),
            "target_a2": canonical_uint(raw["parent_a2"], "pair parent_a2"),
            "target_order": AMBIENT_ORDER,
            "target_orbit_rep": pair.parent_orbit_rep,
            "target_orbit_size": canonical_uint(
                raw["parent_orbit_size"], "pair parent_orbit_size"
            ),
        }
        for key, expected in expected_certificate_values.items():
            if certificate_uint(certificate, key, context) != expected:
                raise RunError(
                    f"{context}: pair endpoint {key} differs from certificate"
                )
        if pairs and pair.global_index <= pairs[-1].global_index:
            raise RunError("pipeline pairs are not in strictly increasing global-index order")
        pairs.append(pair)
    if [pair.global_index for pair in pairs] != certified_indices:
        raise RunError("pipeline pairs do not correspond exactly to certified records")

    selection_fields = {
        "schema",
        "target_pairs",
        "selected_count",
        "selected",
        "valid",
        "cutoff_global_index",
        "blocking_failures",
        "provisional_selected",
        "rule",
    }
    if set(selection) != selection_fields or selection.get("schema") != SELECTION_SCHEMA:
        raise RunError("pipeline selection fields or schema differ from frozen contract")
    if not exact_int_equal(selection.get("target_pairs"), TARGET_PAIRS):
        raise RunError("pipeline selection target differs from the frozen quota")
    if selection.get("rule") != (
        "first eligible distinct parent orbit in global-index order; no outcome backfill"
    ):
        raise RunError("pipeline selection rule differs from the frozen rule")

    provisional: list[Pair] = []
    seen_bottom: set[int] = set()
    seen_parent: set[int] = set()
    for pair in pairs:
        if not eligible_pair(pair):
            continue
        if pair.bottom_orbit_rep in seen_bottom or pair.parent_orbit_rep in seen_parent:
            continue
        provisional.append(pair)
        seen_bottom.add(pair.bottom_orbit_rep)
        seen_parent.add(pair.parent_orbit_rep)
        if len(provisional) == TARGET_PAIRS:
            break
    cutoff = provisional[-1].global_index if len(provisional) == TARGET_PAIRS else None
    blocking = [
        record
        for record in records
        if record["admitted_failure"]
        and (
            cutoff is None
            or canonical_uint(record["global_index"], "blocking failure index") <= cutoff
        )
    ]
    valid = not blocking
    expected_selected = provisional if valid else []
    expected_rows = {
        "provisional_selected": [pair.raw for pair in provisional],
        "selected": [pair.raw for pair in expected_selected],
        "blocking_failures": blocking,
    }
    for field, expected in expected_rows.items():
        raw_rows = selection.get(field)
        if not isinstance(raw_rows, list) or not exact_json_equal(raw_rows, expected):
            raise RunError(f"pipeline selection {field} differs from reconstruction")
        if field != "blocking_failures":
            for number, raw in enumerate(raw_rows):
                context = f"{payload/'selection.json'}:{field}[{number}]"
                index = canonical_uint(raw.get("global_index"), f"{context}:global_index")
                expected_hit = hit_by_index.get(index)
                if expected_hit is None:
                    raise RunError(f"{context}: index is absent from hits.csv")
                parse_pair(raw, context, payload=payload, expected_hit=expected_hit)
    if (
        selection.get("valid") is not valid
        or not exact_int_equal(selection.get("selected_count"), len(expected_selected))
        or (
            selection.get("cutoff_global_index") is not None
            if cutoff is None
            else not exact_int_equal(selection.get("cutoff_global_index"), cutoff)
        )
    ):
        raise RunError("pipeline selection validity, count, or cutoff mismatch")
    validate_pipeline_payload_inventory(
        payload, records, snapshots, control_ids=None
    )
    return records, pairs


def pipeline_runtime_args(gp_runtime: dict[str, Any]) -> list[str]:
    if gp_runtime.get("kind") == "binary":
        return ["--gp-bin", str(gp_runtime["path"])]
    raise RunError("admitted runner permits only the exact extracted GP binary")


def validate_gp_runtime_payload(
    payload: Path,
    gp_runtime: dict[str, Any],
    snapshots: Path,
    context: str,
) -> dict[str, Any]:
    runtime = load_json(payload / "runtime.json")
    frozen_entries, _ = read_hash_manifest(snapshots / "FROZEN.sha256")
    try:
        frozen_classifier = frozen_entries["classify_recover.gp"]
        frozen_census = frozen_entries["floor271_orbits.csv"]
    except KeyError as exc:
        raise RunError(f"{context}: frozen manifest omits GP classifier input") from exc
    stdout_path = payload / "gp.stdout"
    stderr_path = payload / "gp.stderr"
    for stream in (stdout_path, stderr_path):
        if stream.is_symlink() or not stream.is_file():
            raise RunError(f"{context}: missing or non-regular GP stream {stream.name}")
    expected_runtime_fields = {
        "schema", "mode", "gp_binary", "gp_binary_sha256",
        "source_image_content_id", "environment", "command", "exit_status",
        "stdout_sha256", "stderr_sha256", "global_failure",
        "shared_extension_initialization", "gp_stack", "classifier_sha256",
        "census_sha256",
    }
    if (
        set(runtime) != expected_runtime_fields
        or runtime.get("schema") != "m51-deep-gp-runtime/v1"
        or runtime.get("global_failure") is not False
        or not exact_int_equal(runtime.get("exit_status"), 0)
        or runtime.get("shared_extension_initialization") is not True
        or runtime.get("gp_stack") != GP_STACK
        or stdout_path.stat().st_size != 0
        or stderr_path.stat().st_size != 0
        or runtime.get("stdout_sha256") != sha256_file(stdout_path)
        or runtime.get("stderr_sha256") != sha256_file(stderr_path)
        or runtime.get("classifier_sha256") != frozen_classifier
        or sha256_file(snapshots / "classify_recover.gp") != frozen_classifier
        or runtime.get("census_sha256") != frozen_census
        or sha256_file(snapshots / "floor271_orbits.csv") != frozen_census
    ):
        raise RunError(f"{context}: GP runtime reports failure or unknown frozen inputs")

    if gp_runtime.get("kind") == "binary":
        expected_gp = str(Path(gp_runtime["path"]).resolve())
        expected_command = [expected_gp, "-q", "-f", "-s", GP_STACK]
        if (
            runtime.get("mode") != "extracted-binary"
            or runtime.get("gp_binary") != expected_gp
            or runtime.get("gp_binary_sha256") != PINNED_GP_BINARY_SHA256
            or runtime.get("source_image_content_id") != PINNED_GP_IMAGE_ID
            or runtime.get("environment") != GP_CHILD_ENV
            or runtime.get("command") != expected_command
        ):
            raise RunError(f"{context}: unexpected extracted GP runtime")
    else:
        raise RunError(f"{context}: admitted runner requires extracted GP runtime")
    return runtime


def validate_pipeline_payload_inventory(
    payload: Path,
    records: list[dict[str, Any]],
    snapshots: Path,
    *,
    control_ids: tuple[str, ...] | None,
) -> None:
    """Bind every payload path plus the exact GP batch driver to admitted jobs."""
    expected_files = {
        "driver.gp",
        "gp.stdout",
        "gp.stderr",
        "runtime.json",
        "records.jsonl",
        *( ("controls.json",) if control_ids is not None else (
            "pairs.jsonl", "selection.json"
        ) ),
    }
    expected_directories = {"certificates", "partials"}
    actual_files: set[str] = set()
    actual_directories: set[str] = set()
    for child in payload.iterdir():
        if child.is_symlink():
            raise RunError(f"pipeline payload contains symlink {child.name}")
        if child.is_file():
            actual_files.add(child.name)
        elif child.is_dir():
            actual_directories.add(child.name)
        else:
            raise RunError(f"pipeline payload contains special entry {child.name}")
    if actual_files != expected_files or actual_directories != expected_directories:
        raise RunError(
            "pipeline payload top-level inventory differs from the frozen contract"
        )

    expected_certificates: set[str] = set()
    expected_partials: set[str] = set()
    driver_rows: list[list[int | str]] = []
    for number, record in enumerate(records):
        index = canonical_uint(record.get("global_index"), "payload record index")
        b = canonical_uint(record.get("b"), "payload record coefficient", maximum=FIELD_MASK)
        if control_ids is None:
            label = f"rank-{index:010d}"
            mode = 0
            source_seed = derive_endpoint_seed(
                b"m51-deep-scan/v1/source-witness", record
            )
            target_seed = derive_endpoint_seed(
                b"m51-deep-scan/v1/target-rank2", record
            )
        else:
            label = control_ids[number]
            mode = CONTROL_MODES[label]
            source_seed = control_endpoint_seed(label, target=False)
            target_seed = control_endpoint_seed(label, target=True)
        relative = f"certificates/{number:04d}-{label}.kv"
        if record.get("certificate_path") != relative:
            raise RunError("pipeline certificate name/order differs from admitted jobs")
        expected_certificates.add(Path(relative).name)
        if record.get("status") == "GP_ERROR":
            expected_partials.add(Path(relative).name)
        driver_rows.append(
            [index, b, source_seed, target_seed, mode, relative]
        )

    def exact_leaf_set(directory: Path, expected: set[str], context: str) -> None:
        actual: set[str] = set()
        for child in directory.iterdir():
            if child.is_symlink() or not child.is_file():
                raise RunError(f"{context} contains non-regular entry {child.name}")
            actual.add(child.name)
        if actual != expected:
            raise RunError(f"{context} file set differs from admitted jobs")

    exact_leaf_set(payload / "certificates", expected_certificates, "certificates")
    exact_leaf_set(payload / "partials", expected_partials, "partials")
    expected_driver = (
        f"EMBED_SEED={EMBED_SEED};\nWITNESS_COUNT={WITNESS_COUNT};\n"
        f"MAX_WITNESS_ATTEMPTS={MAX_WITNESS_ATTEMPTS};\n"
        f"BATCH_ROWS={json.dumps(driver_rows, separators=(',', ':'))};\n"
        f"read({json.dumps(str((snapshots / 'classify_recover.gp').resolve()))});\n"
    ).encode()
    if (payload / "driver.gp").read_bytes() != expected_driver:
        raise RunError("pipeline GP driver differs from reconstructed admitted jobs")


def validate_controls_payload(
    payload: Path, gp_runtime: dict[str, Any], snapshots: Path
) -> dict[str, Any]:
    summary = load_json(payload / "controls.json")
    records = load_jsonl(payload / "records.jsonl")
    runtime = validate_gp_runtime_payload(payload, gp_runtime, snapshots, "controls")
    controls = summary.get("controls")
    summary_fields = {
        "schema",
        "all_passed",
        "control_count",
        "expected",
        "observed",
        "controls",
        "positive_controls",
        "negative_controls",
        "runtime_sha256",
    }
    if (
        set(summary) != summary_fields
        or summary.get("schema") != "m51-deep-controls/v1"
        or summary.get("all_passed") is not True
        or not exact_int_equal(summary.get("control_count"), len(CONTROL_IDS))
        or not isinstance(controls, list)
        or len(controls) != len(CONTROL_IDS)
        or len(records) != len(CONTROL_IDS)
    ):
        raise RunError("control summary did not certify the exact 21-control design")
    if summary.get("positive_controls") != list(POSITIVE_CONTROL_IDS):
        raise RunError("positive control IDs or order differ from the frozen design")
    if summary.get("negative_controls") != list(NEGATIVE_CONTROL_IDS):
        raise RunError("negative control IDs or order differ from the frozen design")
    try:
        with (snapshots / "floor271_orbits.csv").open(newline="") as handle:
            census_reader = csv.DictReader(handle)
            if tuple(census_reader.fieldnames or ()) != (
                "orbit_id",
                "b",
                "a2",
                "orbit_size",
                "f_E",
            ):
                raise RunError("f=271 census header differs from frozen schema")
            census_rows = list(census_reader)
    except OSError as exc:
        raise RunError(f"cannot read frozen f=271 census: {exc}") from exc
    if len(census_rows) != 16:
        raise RunError("f=271 census does not contain exactly 16 orbit representatives")
    f271_reps = [
        decimal_uint(row["b"], f"f271 census row {number}:b", maximum=FIELD_MASK)
        for number, row in enumerate(census_rows, 1)
    ]
    expected_control_b = {
        "crater-exclusion": 1,
        **{
            f"f271-exclusion-{number:02d}": value
            for number, value in enumerate(f271_reps, 1)
        },
        "pilot-source-exclusion": PILOT_BOTTOM_RAW_B,
        "positive-f271-ascent": f271_reps[0],
        "positive-bottom-ascent": PILOT_BOTTOM_RAW_B,
        "positive-parent-rank2": PILOT_PARENT_ORBIT_REP,
    }
    observed_ids: list[str] = []
    for number, (control, record) in enumerate(zip(controls, records, strict=True)):
        context = f"{payload/'controls.json'}:controls[{number}]"
        if not isinstance(control, dict):
            raise RunError(f"{context}: expected object")
        control_id = control.get("id")
        observed_ids.append(control_id)
        expected_kind = "positive" if control_id in POSITIVE_CONTROL_IDS else "negative"
        expected_status = CONTROL_EXPECTED_STATUSES.get(control_id)
        if (
            control_id != CONTROL_IDS[number]
            or control.get("kind") != expected_kind
            or control.get("passed") is not True
            or control.get("expected") != expected_status
            or control.get("observed") != expected_status
        ):
            raise RunError(f"{context}: failed or changed frozen control")
        if set(control) != {
            "id",
            "kind",
            "expected",
            "observed",
            "passed",
            "certificate_path",
            "certificate_sha256",
        }:
            raise RunError(f"{context}: control row fields differ from frozen schema")
        if set(record) != RECORD_FIELDS:
            raise RunError(f"{context}: control record fields differ from frozen schema")
        record_mode = canonical_uint(record.get("control_mode"), f"{context}:control_mode")
        if (
            record.get("schema") != "m51-deep-classification-record/v1"
            or record.get("status") != control["observed"]
            or record.get("admitted_failure") is not False
            or record_mode != CONTROL_MODES[control_id]
            or record.get("certificate_path") != control.get("certificate_path")
            or record.get("certificate_sha256") != control.get("certificate_sha256")
        ):
            raise RunError(f"{context}: decision record differs from control summary")
        source_hit = parse_source_hit(record.get("source_hit"), f"{context}:source_hit")
        expected_source_hit = {
            "global_index": number,
            "b": expected_control_b[control_id],
            "x0": 0,
            "x1": 0,
            "x2": 0,
        }
        if source_hit != expected_source_hit:
            raise RunError(f"{context}: control source differs from frozen fixture")
        top_level_hit = {
            field: canonical_uint(
                record.get(field),
                f"{context}:{field}",
                maximum=FIELD_MASK if field != "global_index" else None,
            )
            for field in SEARCH_HEADER
        }
        if top_level_hit != source_hit:
            raise RunError(f"{context}: control source binding differs from record")
        relative, _ = validate_certificate_reference(record, payload, context)
        certificate_bytes = canonical_uint(
            record.get("certificate_bytes"), f"{context}:certificate_bytes"
        )
        if certificate_bytes != (payload / relative).stat().st_size:
            raise RunError(f"{context}: certificate byte count mismatch")
        certificate = parse_endpoint_certificate(
            payload / relative,
            source_hit,
            expected_status,
            False,
            CONTROL_MODES[control_id],
            sha256_file(snapshots / "floor271_orbits.csv"),
            control_endpoint_seed(control_id, target=False),
            control_endpoint_seed(control_id, target=True),
            context,
        )
        expected_certificate_ints = {
            "source_order": AMBIENT_ORDER,
            "source_orbit_rep": (
                1
                if control_id == "crater-exclusion"
                else expected_control_b[control_id]
                if control_id.startswith("f271-exclusion-")
                or control_id == "positive-f271-ascent"
                or control_id == "positive-parent-rank2"
                else PILOT_BOTTOM_ORBIT_REP
            ),
            "source_orbit_size": (
                1
                if control_id == "crater-exclusion"
                else 17
                if control_id.startswith("f271-exclusion-")
                or control_id == "positive-f271-ascent"
                else 51
            ),
        }
        if control_id == "positive-f271-ascent":
            expected_certificate_ints.update(
                target_b=1,
                target_order=AMBIENT_ORDER,
                target_orbit_rep=1,
                target_orbit_size=1,
            )
        elif control_id == "positive-bottom-ascent":
            expected_certificate_ints.update(
                target_b=PILOT_PARENT_ORBIT_REP,
                target_order=AMBIENT_ORDER,
                target_orbit_rep=PILOT_PARENT_ORBIT_REP,
                target_orbit_size=51,
            )
        for key, expected in expected_certificate_ints.items():
            if certificate_uint(certificate, key, context) != expected:
                raise RunError(f"{context}: control certificate {key} mismatch")
    if tuple(observed_ids) != CONTROL_IDS:
        raise RunError("control IDs are not the exact frozen ordered set")
    validate_pipeline_payload_inventory(
        payload, records, snapshots, control_ids=CONTROL_IDS
    )
    expected_map = {control["id"]: control["expected"] for control in controls}
    observed_map = {control["id"]: control["observed"] for control in controls}
    if summary.get("expected") != expected_map or summary.get("observed") != observed_map:
        raise RunError("control expected/observed maps differ from control rows")
    runtime_digest = hashlib.sha256(
        json.dumps(runtime, sort_keys=True).encode()
    ).hexdigest()
    if summary.get("runtime_sha256") != runtime_digest:
        raise RunError("controls runtime digest mismatch")
    return summary


def run_controls(
    out: Path,
    snapshots: Path,
    gp_runtime: dict[str, Any],
    stop: threading.Event,
) -> dict[str, Any]:
    final = out / "controls"
    stable_runtime = stable_gp_runtime_identity(gp_runtime)
    runtime_fingerprint = hashlib.sha256(
        (json.dumps(stable_runtime, sort_keys=True, separators=(",", ":")) + "\n").encode()
    ).hexdigest()
    if final.exists():
        verify_tree_manifest(final)
        receipt = load_json(final / "receipt.json")
        summary = validate_controls_payload(final / "payload", gp_runtime, snapshots)
        command = receipt.get("command")
        if not isinstance(command, list) or len(command) != 10:
            raise RunError("existing controls command is malformed")
        recorded_payload = Path(str(command[7]))
        expected_command = [
            sys.executable,
            *PYTHON_CHILD_FLAGS,
            str(snapshots / "pipeline.py"),
            "controls",
            "--out",
            str(recorded_payload),
            *pipeline_runtime_args(gp_runtime),
        ]
        try:
            recorded_runtime = stable_gp_runtime_identity(receipt.get("gp_runtime"))
        except (AttributeError, KeyError, TypeError, RunError) as exc:
            raise RunError("existing controls GP runtime is malformed") from exc
        if (
            set(receipt)
            != {
                "schema",
                "status",
                "pipeline_sha256",
                "gp_runtime",
                "gp_runtime_fingerprint",
                *PROCESS_RECEIPT_FIELDS,
                "stdout_sha256",
                "stderr_sha256",
                "control_count",
                "controls_sha256",
                "runtime_sha256",
            }
            or receipt.get("schema") != "m51-deep-controls-receipt/v1"
            or receipt.get("status") != "complete"
            or receipt.get("pipeline_sha256") != sha256_file(snapshots / "pipeline.py")
            or not exact_json_equal(recorded_runtime, stable_runtime)
            or receipt.get("gp_runtime_fingerprint") != runtime_fingerprint
            or not exact_int_equal(receipt.get("control_count"), len(CONTROL_IDS))
            or receipt.get("controls_sha256")
            != sha256_file(final / "payload" / "controls.json")
            or receipt.get("runtime_sha256")
            != sha256_file(final / "payload" / "runtime.json")
            or recorded_payload.name != "payload"
            or recorded_payload.parent.parent
            != out / "attempts" / "controls" / "frozen-controls"
            or not is_attempt_directory_name(recorded_payload.parent.name)
            or summary.get("all_passed") is not True
        ):
            raise RunError("existing controls receipt differs from frozen gate")
        validate_process_receipt(
            receipt,
            expected_command=expected_command,
            expected_cwd=None,
            context="controls pipeline",
        )
        require_log(
            final / "stdout.log", receipt.get("stdout_sha256"), b"", "controls pipeline"
        )
        require_log(
            final / "stderr.log", receipt.get("stderr_sha256"), b"", "controls pipeline"
        )
        return receipt

    attempt = allocate_attempt(out, "controls", "frozen-controls")
    payload = attempt / "payload"
    command = [
        sys.executable,
        *PYTHON_CHILD_FLAGS,
        str(snapshots / "pipeline.py"),
        "controls",
        "--out",
        str(payload),
        *pipeline_runtime_args(gp_runtime),
    ]
    process = run_process(
        command,
        timeout=CONTROLS_TIMEOUT_SECONDS,
        cancel=stop,
    )
    write_process_logs(attempt, process)
    receipt: dict[str, Any] = {
        "schema": "m51-deep-controls-receipt/v1",
        "status": "failed",
        "pipeline_sha256": sha256_file(snapshots / "pipeline.py"),
        "gp_runtime": gp_runtime,
        "gp_runtime_fingerprint": runtime_fingerprint,
        **receipt_process_fields(process),
        "stdout_sha256": sha256_file(attempt / "stdout.log"),
        "stderr_sha256": sha256_file(attempt / "stderr.log"),
    }
    try:
        if process["timed_out"] or process["cancelled"] or process["exit_status"] != 0:
            raise RunError(
                f"controls exit={process['exit_status']} timeout={process['timed_out']} "
                f"cancelled={process['cancelled']}"
            )
        if process["stdout"] or process["stderr"]:
            raise RunError("successful controls pipeline emitted stdout or stderr")
        if not payload.is_dir() or payload.is_symlink():
            raise RunError("controls did not create a regular payload directory")
        summary = validate_controls_payload(payload, gp_runtime, snapshots)
        receipt.update(
            status="complete",
            control_count=summary["control_count"],
            controls_sha256=sha256_file(payload / "controls.json"),
            runtime_sha256=sha256_file(payload / "runtime.json"),
        )
    except BaseException as exc:
        receipt["error"] = repr(exc)
        atomic_write_json(attempt / "receipt.json", receipt)
        write_tree_manifest(attempt)
        raise
    atomic_write_json(attempt / "receipt.json", receipt)
    write_tree_manifest(attempt)
    promote_directory(attempt, final)
    return receipt


def classify_global(
    out: Path,
    snapshots: Path,
    gp_runtime: dict[str, Any],
    hits: Path,
    hit_rows: list[dict[str, int]],
    stop: threading.Event,
) -> tuple[list[dict[str, Any]], list[Pair], dict[str, Any]]:
    final = out / "classification"
    stable_runtime = stable_gp_runtime_identity(gp_runtime)
    runtime_fingerprint = hashlib.sha256(
        (json.dumps(stable_runtime, sort_keys=True, separators=(",", ":")) + "\n").encode()
    ).hexdigest()
    if final.exists():
        verify_tree_manifest(final)
        receipt = load_json(final / "receipt.json")
        records, pairs = validate_classification_payload(
            final / "payload", hit_rows, snapshots, gp_runtime
        )
        command = receipt.get("command")
        if not isinstance(command, list) or len(command) != 12:
            raise RunError("existing classification command is malformed")
        recorded_payload = Path(str(command[9]))
        expected_command = [
            sys.executable,
            *PYTHON_CHILD_FLAGS,
            str(snapshots / "pipeline.py"),
            "classify",
            "--hits",
            str(hits),
            "--out",
            str(recorded_payload),
            *pipeline_runtime_args(gp_runtime),
        ]
        try:
            recorded_runtime = stable_gp_runtime_identity(receipt.get("gp_runtime"))
        except (AttributeError, KeyError, TypeError, RunError) as exc:
            raise RunError("existing classification GP runtime is malformed") from exc
        expected_payload_hashes = {
            name: sha256_file(final / "payload" / name)
            for name in ("records.jsonl", "pairs.jsonl", "selection.json")
        }
        if (
            set(receipt)
            != {
                "schema",
                "status",
                "hits",
                "hits_sha256",
                "hit_rows",
                "pipeline_sha256",
                "gp_runtime",
                "gp_runtime_fingerprint",
                *PROCESS_RECEIPT_FIELDS,
                "stdout_sha256",
                "stderr_sha256",
                "records",
                "certified_pairs",
                "payload_hashes",
            }
            or receipt.get("schema") != "m51-deep-global-classification-receipt/v1"
            or receipt.get("status") != "complete"
            or receipt.get("hits") != str(hits)
            or receipt.get("hits_sha256") != sha256_file(hits)
            or not exact_int_equal(receipt.get("hit_rows"), len(hit_rows))
            or receipt.get("pipeline_sha256") != sha256_file(snapshots / "pipeline.py")
            or not exact_json_equal(recorded_runtime, stable_runtime)
            or receipt.get("gp_runtime_fingerprint") != runtime_fingerprint
            or not exact_int_equal(receipt.get("records"), len(records))
            or not exact_int_equal(receipt.get("certified_pairs"), len(pairs))
            or receipt.get("payload_hashes") != expected_payload_hashes
            or recorded_payload.name != "payload"
            or recorded_payload.parent.parent
            != out / "attempts" / "classify" / "global"
            or not is_attempt_directory_name(recorded_payload.parent.name)
        ):
            raise RunError("existing classification receipt differs from reconstruction")
        validate_process_receipt(
            receipt,
            expected_command=expected_command,
            expected_cwd=None,
            context="classification pipeline",
        )
        require_log(
            final / "stdout.log",
            receipt.get("stdout_sha256"),
            b"",
            "classification pipeline",
        )
        require_log(
            final / "stderr.log",
            receipt.get("stderr_sha256"),
            b"",
            "classification pipeline",
        )
        return records, pairs, receipt

    attempt = allocate_attempt(out, "classify", "global")
    payload = attempt / "payload"
    command = [
        sys.executable,
        *PYTHON_CHILD_FLAGS,
        str(snapshots / "pipeline.py"),
        "classify",
        "--hits",
        str(hits),
        "--out",
        str(payload),
        *pipeline_runtime_args(gp_runtime),
    ]
    process = run_process(command, timeout=PIPELINE_TIMEOUT_SECONDS, cancel=stop)
    write_process_logs(attempt, process)
    receipt: dict[str, Any] = {
        "schema": "m51-deep-global-classification-receipt/v1",
        "status": "failed",
        "hits": str(hits),
        "hits_sha256": sha256_file(hits),
        "hit_rows": len(hit_rows),
        "pipeline_sha256": sha256_file(snapshots / "pipeline.py"),
        "gp_runtime": gp_runtime,
        "gp_runtime_fingerprint": runtime_fingerprint,
        **receipt_process_fields(process),
        "stdout_sha256": sha256_file(attempt / "stdout.log"),
        "stderr_sha256": sha256_file(attempt / "stderr.log"),
    }
    try:
        if process["timed_out"] or process["cancelled"] or process["exit_status"] != 0:
            raise RunError(
                f"global pipeline exit={process['exit_status']} "
                f"timeout={process['timed_out']} cancelled={process['cancelled']}"
            )
        if process["stdout"] or process["stderr"]:
            raise RunError("successful global pipeline emitted stdout or stderr")
        if not payload.is_dir() or payload.is_symlink():
            raise RunError("global pipeline did not create a regular output directory")
        records, pairs = validate_classification_payload(
            payload, hit_rows, snapshots, gp_runtime
        )
        receipt.update(
            status="complete",
            records=len(records),
            certified_pairs=len(pairs),
            payload_hashes={
                name: sha256_file(payload / name)
                for name in ("records.jsonl", "pairs.jsonl", "selection.json")
            },
        )
    except BaseException as exc:
        receipt["error"] = repr(exc)
        atomic_write_json(attempt / "receipt.json", receipt)
        write_tree_manifest(attempt)
        raise
    atomic_write_json(attempt / "receipt.json", receipt)
    write_tree_manifest(attempt)
    promote_directory(attempt, final)
    return records, pairs, receipt


def update_global_selection(
    selected: list[Pair],
    seen_bottom: set[int],
    seen_parent: set[int],
    records: list[dict[str, Any]],
    pairs: list[Pair],
) -> tuple[int | None, list[dict[str, Any]]]:
    pair_by_index = {pair.global_index: pair for pair in pairs}
    cutoff: int | None = selected[-1].global_index if len(selected) >= TARGET_PAIRS else None
    admitted_failures: list[dict[str, Any]] = []
    for record in records:
        index = canonical_uint(record["global_index"], "pipeline record global_index")
        if record["admitted_failure"]:
            admitted_failures.append(record)
            continue
        if cutoff is not None:
            continue
        pair = pair_by_index.get(index)
        if pair is None or not eligible_pair(pair):
            continue
        if pair.parent_orbit_rep in seen_parent or pair.bottom_orbit_rep in seen_bottom:
            continue
        selected.append(pair)
        seen_parent.add(pair.parent_orbit_rep)
        seen_bottom.add(pair.bottom_orbit_rep)
        if len(selected) == TARGET_PAIRS:
            cutoff = pair.global_index
    return cutoff, admitted_failures


def aggregate_selection_document(
    provisional_selected: list[Pair],
    classified_shards: int,
    scanned_shards: int,
    admitted_failures: list[dict[str, Any]],
) -> dict[str, Any]:
    cutoff = (
        provisional_selected[-1].global_index
        if len(provisional_selected) == TARGET_PAIRS
        else None
    )
    blocking_failures = [
        record
        for record in admitted_failures
        if cutoff is None
        or canonical_uint(record["global_index"], "admitted failure global_index") <= cutoff
    ]
    valid = not blocking_failures
    selected = provisional_selected if valid else []
    return {
        "schema": "m51-deep-global-selection/v1",
        "certificate_base": CLASSIFICATION_CERTIFICATE_BASE,
        "updated_utc": utc_now(),
        "target_pairs": TARGET_PAIRS,
        "selected_count": len(selected),
        "provisional_selected_count": len(provisional_selected),
        "cutoff_global_index": cutoff,
        "valid": valid,
        "classified_shards": classified_shards,
        "scanned_shards": scanned_shards,
        "pilot_exclusion": {
            "bottom_orbit_rep": PILOT_BOTTOM_ORBIT_REP,
            "parent_orbit_rep": PILOT_PARENT_ORBIT_REP,
        },
        "distinct_parent_orbits": len({pair.parent_orbit_rep for pair in selected}),
        "distinct_bottom_orbits": len({pair.bottom_orbit_rep for pair in selected}),
        "admitted_failures_seen": len(admitted_failures),
        "admitted_failures": admitted_failures,
        "blocking_failures": blocking_failures,
        "provisional_selected": [pair.raw for pair in provisional_selected],
        "selected": [pair.raw for pair in selected],
        "rule": (
            "first eligible distinct parent orbit in global-index order; "
            "no outcome backfill"
        ),
    }


def count_completed_shards(out: Path, layout: ScanLayout) -> int:
    return sum((out / "chunks" / f"shard-{i:03d}").is_dir() for i in range(layout.shards))


def validate_chunk_directory_set(out: Path, layout: ScanLayout) -> None:
    chunks = out / "chunks"
    expected = {f"shard-{shard_id:03d}" for shard_id in range(layout.shards)}
    actual: set[str] = set()
    for path in chunks.iterdir():
        if path.is_symlink() or not path.is_dir():
            raise RunError(f"unexpected non-directory entry under chunks/: {path}")
        actual.add(path.name)
    if actual != expected:
        raise RunError(
            "completed shard directory set mismatch; "
            f"missing={sorted(expected-actual)}, extra={sorted(actual-expected)}"
        )


def initialize_output(
    out: Path,
    mock: bool,
    gp_runtime: dict[str, Any] | None,
    frozen: tuple[dict[str, str], str],
    spec: dict[str, Any],
) -> None:
    if out.exists() or out.is_symlink():
        return
    init = out.with_name(f".{out.name}.initializing-{os.getpid()}")
    if init.exists() or init.is_symlink():
        raise RunError(f"refusing pre-existing initialization path {init}")
    durable_mkdir(init)
    try:
        for name in ("chunks", "attempts"):
            durable_mkdir(init / name)
        git_before = git_receipt()
        snapshots = copy_frozen_snapshot(init / "inputs", frozen)
        for name, receipt in snapshots.items():
            receipt["snapshot"] = str(out / "inputs" / name)
        git_after = git_receipt()
        if git_after != git_before:
            raise RunError("git revision or status changed during frozen snapshot")
        host = host_receipt(gp_runtime)
        host_payload = json.dumps(host, indent=2, sort_keys=True) + "\n"
        identity = {
            "schema": "m51-deep-scan-run/v1",
            "created_utc": utc_now(),
            "mode": "mock" if mock else "scientific",
            "scientific_eligible": not mock,
            "output": str(out),
            "git": git_after,
            "frozen_manifest_sha256": frozen[1],
            "spec_sha256": sha256_file(HERE / "spec.json"),
            "pipeline_sha256": sha256_file(HERE / "pipeline.py"),
            "search_source_sha256": sha256_file(HERE / "search.c"),
            "gp": stable_gp_runtime_identity(gp_runtime),
            "host_identity": stable_host_identity(host),
            "scan": spec["scan"],
            "mock_layout": {
                "start": MOCK_START,
                "shards": MOCK_SHARDS,
                "shard_size": MOCK_SHARD_SIZE,
            }
            if mock
            else None,
            "command": [sys.executable, *sys.argv],
            "snapshot_files": snapshots,
            "host_receipt_sha256": hashlib.sha256(host_payload.encode()).hexdigest(),
        }
        atomic_write_json(init / "run.json", identity)
        atomic_write_text(init / "host.json", host_payload)
        atomic_write_text(
            init / "run-command.txt",
            shlex.join([sys.executable, *sys.argv]) + "\n",
        )
        if mock:
            atomic_write_json(
                init / "MOCK-ONLY.json",
                {
                    "schema": "m51-deep-mock-warning/v1",
                    "scientific_eligible": False,
                    "warning": (
                        "mock-scan uses tagged singular fixtures and skips exact classification; "
                        "it is orchestration evidence only"
                    ),
                },
            )
        # The output root cannot carry MANIFEST.sha256 until it is terminal;
        # publishing that name here would make an initialized run look sealed.
        # All phase directories use the manifest-required default.
        promote_directory(init, out, require_manifest=False)
    except BaseException:
        # Preserve the initialization directory as evidence; never overwrite it.
        raise


def validate_resume_identity(
    out: Path,
    mock: bool,
    gp_runtime: dict[str, Any] | None,
    frozen: tuple[dict[str, str], str],
    spec: dict[str, Any],
) -> dict[str, Any]:
    if out.is_symlink() or not out.is_dir():
        raise RunError(f"output root is not a regular directory: {out}")
    identity = load_json(out / "run.json")
    expected_fields = {
        "schema",
        "created_utc",
        "mode",
        "scientific_eligible",
        "output",
        "git",
        "frozen_manifest_sha256",
        "spec_sha256",
        "pipeline_sha256",
        "search_source_sha256",
        "gp",
        "host_identity",
        "scan",
        "mock_layout",
        "command",
        "snapshot_files",
        "host_receipt_sha256",
    }
    if set(identity) != expected_fields:
        raise RunError("existing run.json fields differ from the frozen identity schema")
    if identity.get("schema") != "m51-deep-scan-run/v1":
        raise RunError("existing run.json schema differs from the frozen identity schema")
    validate_utc_timestamp(identity.get("created_utc"), "run.json:created_utc")
    if identity.get("mode") != ("mock" if mock else "scientific"):
        raise RunError("existing output mode differs from invocation")
    if identity.get("scientific_eligible") is not (not mock):
        raise RunError("existing output scientific eligibility differs from invocation")
    if identity.get("output") != str(out):
        raise RunError("existing output identity is bound to another path")
    if identity.get("frozen_manifest_sha256") != frozen[1]:
        raise RunError("existing output is bound to another FROZEN.sha256")
    entries, manifest_hash = frozen
    expected_snapshot_files = {}
    for name in [*entries, "FROZEN.sha256"]:
        snapshot = out / "inputs" / name
        expected_snapshot_files[name] = {
            "source": str(HERE / name),
            "snapshot": str(snapshot),
            "sha256": entries.get(name, manifest_hash),
            "bytes": snapshot.stat().st_size,
        }
    expected_static = {
        "spec_sha256": entries["spec.json"],
        "pipeline_sha256": entries["pipeline.py"],
        "search_source_sha256": entries["search.c"],
        "scan": spec["scan"],
        "mock_layout": {
            "start": MOCK_START,
            "shards": MOCK_SHARDS,
            "shard_size": MOCK_SHARD_SIZE,
        }
        if mock
        else None,
        "command": [sys.executable, *sys.argv],
        "snapshot_files": expected_snapshot_files,
    }
    for key, expected in expected_static.items():
        if not exact_json_equal(identity.get(key), expected):
            raise RunError(f"existing run.json {key} differs from the frozen identity")
    git = git_receipt()
    if not exact_json_equal(identity.get("git"), git):
        raise RunError("resume requires the original clean git snapshot")
    verify_snapshot(out, frozen)
    if not exact_json_equal(
        identity.get("gp"), stable_gp_runtime_identity(gp_runtime)
    ):
        raise RunError("resume GP runtime differs from the original run")
    host_path = out / "host.json"
    if (
        not host_path.is_file()
        or host_path.is_symlink()
        or sha256_file(host_path) != identity.get("host_receipt_sha256")
    ):
        raise RunError("host receipt differs from the run identity")
    recorded_host = load_json(host_path)
    if not exact_json_equal(
        identity.get("host_identity"), stable_host_identity(recorded_host)
    ):
        raise RunError("recorded host identity differs from run.json")
    current_host = host_receipt(gp_runtime)
    if not exact_json_equal(
        identity.get("host_identity"), stable_host_identity(current_host)
    ):
        raise RunError("current host/runtime differs from the admitted run host")
    command_path = out / "run-command.txt"
    if (
        not command_path.is_file()
        or command_path.is_symlink()
        or command_path.read_text() != shlex.join(identity["command"]) + "\n"
    ):
        raise RunError("run-command receipt differs from the run identity")
    mock_warning_path = out / "MOCK-ONLY.json"
    if mock:
        if not exact_json_equal(load_json(mock_warning_path), {
            "schema": "m51-deep-mock-warning/v1",
            "scientific_eligible": False,
            "warning": (
                "mock-scan uses tagged singular fixtures and skips exact classification; "
                "it is orchestration evidence only"
            ),
        }):
            raise RunError("mock-only warning differs from the frozen identity")
    elif mock_warning_path.exists() or mock_warning_path.is_symlink():
        raise RunError("scientific output contains a mock-only marker")
    return identity


def validate_terminal_session(
    out: Path, session: dict[str, Any], layout: ScanLayout, *, mock: bool
) -> None:
    def is_sha256(value: Any) -> bool:
        return (
            isinstance(value, str)
            and len(value) == 64
            and all(character in "0123456789abcdef" for character in value)
        )

    common_fields = {
        "schema",
        "status",
        "mode",
        "scientific_eligible",
        "started_utc",
        "resumed",
        "range",
        "shards_planned",
        "shard_size",
        "workers",
        "cores",
        "target_pairs",
        "phase",
        "binary_sha256",
        "shards_scanned",
        "shards_classified",
        "selected_pairs",
        "manifest",
        "finished_utc",
        "elapsed_seconds",
    }
    expected_fields = common_fields if mock else common_fields | {
        "controls_passed",
        "controls_sha256",
        "aggregate_hits_sha256",
        "sieve_hits",
        "classification_invocations",
        "provisional_selected_pairs",
        "cutoff_global_index",
        "admitted_failures_total",
        "admitted_failures_before_cutoff",
        "fixed_range_exhausted",
    }
    session_started = validate_utc_timestamp(
        session.get("started_utc"), "session:started_utc"
    )
    session_finished = validate_utc_timestamp(
        session.get("finished_utc"), "session:finished_utc"
    )
    if session_finished < session_started:
        raise RunError("session finished_utc precedes started_utc")
    if (
        set(session) != expected_fields
        or session.get("schema") != "m51-deep-scan-session/v1"
        or session.get("phase") != "complete"
        or session.get("mode") != ("mock" if mock else "scientific")
        or session.get("scientific_eligible") is not (not mock)
        or not exact_int_list(session.get("range"), [layout.start, layout.end])
        or not exact_int_equal(session.get("shards_planned"), layout.shards)
        or not exact_int_equal(session.get("shard_size"), layout.shard_size)
        or not exact_int_equal(session.get("workers"), WORKERS)
        or not exact_int_list(session.get("cores"), CORES)
        or session.get("manifest") != str(out / "MANIFEST.sha256")
        or not isinstance(session.get("resumed"), bool)
        or not isinstance(session.get("elapsed_seconds"), (int, float))
        or isinstance(session.get("elapsed_seconds"), bool)
        or not math.isfinite(session.get("elapsed_seconds", float("nan")))
        or session.get("elapsed_seconds", -1) < 0
        or not is_sha256(session.get("binary_sha256"))
    ):
        raise RunError("terminal session violates the frozen common invariants")
    if mock:
        if (
            session.get("status") != "mock_complete_not_scientific"
            or not exact_int_equal(session.get("target_pairs"), 0)
            or not exact_int_equal(session.get("shards_scanned"), layout.shards)
            or not exact_int_equal(session.get("shards_classified"), 0)
            or not exact_int_equal(session.get("selected_pairs"), 0)
        ):
            raise RunError("sealed mock session violates terminal invariants")
        validate_chunk_directory_set(out, layout)
        return

    allowed = {
        "quota_met_full_range_complete",
        "range_exhausted_quota_not_met",
        "invalid_admitted_failure_before_selection_cutoff",
    }
    status_value = session.get("status")
    selection = load_json(out / "selection.json")
    selection_fields = {
        "schema",
        "certificate_base",
        "updated_utc",
        "target_pairs",
        "selected_count",
        "provisional_selected_count",
        "cutoff_global_index",
        "valid",
        "classified_shards",
        "scanned_shards",
        "pilot_exclusion",
        "distinct_parent_orbits",
        "distinct_bottom_orbits",
        "admitted_failures_seen",
        "admitted_failures",
        "blocking_failures",
        "provisional_selected",
        "selected",
        "rule",
    }
    selected_count = selection.get("selected_count")
    provisional_count = selection.get("provisional_selected_count")
    admitted_failures_seen = selection.get("admitted_failures_seen")
    selection_cutoff = selection.get("cutoff_global_index")
    blocking_failures = selection.get("blocking_failures")
    if (
        not isinstance(selected_count, int)
        or isinstance(selected_count, bool)
        or not isinstance(provisional_count, int)
        or isinstance(provisional_count, bool)
        or not isinstance(admitted_failures_seen, int)
        or isinstance(admitted_failures_seen, bool)
        or not (
            selection_cutoff is None
            or (isinstance(selection_cutoff, int) and not isinstance(selection_cutoff, bool))
        )
        or not isinstance(blocking_failures, list)
    ):
        raise RunError("sealed scientific selection has invalid count fields")
    if (
        set(selection) != selection_fields
        or status_value not in allowed
        or session.get("controls_passed") is not True
        or not is_sha256(session.get("controls_sha256"))
        or not is_sha256(session.get("aggregate_hits_sha256"))
        or not isinstance(session.get("sieve_hits"), int)
        or isinstance(session.get("sieve_hits"), bool)
        or session.get("sieve_hits", -1) < 0
        or not exact_int_equal(session.get("target_pairs"), TARGET_PAIRS)
        or session.get("fixed_range_exhausted") is not True
        or not exact_int_equal(session.get("shards_scanned"), layout.shards)
        or not exact_int_equal(session.get("shards_classified"), layout.shards)
        or not exact_int_equal(session.get("classification_invocations"), 1)
        or selection.get("schema") != "m51-deep-global-selection/v1"
        or selection.get("certificate_base") != CLASSIFICATION_CERTIFICATE_BASE
        or not exact_int_equal(selection.get("target_pairs"), TARGET_PAIRS)
        or not exact_int_equal(selection.get("scanned_shards"), layout.shards)
        or not exact_int_equal(selection.get("classified_shards"), layout.shards)
        or not exact_int_equal(session.get("selected_pairs"), selected_count)
        or not exact_int_equal(
            session.get("provisional_selected_pairs"), provisional_count
        )
        or not exact_optional_int_equal(
            session.get("cutoff_global_index"), selection_cutoff
        )
        or not exact_int_equal(
            session.get("admitted_failures_total"), admitted_failures_seen
        )
        or not exact_int_equal(
            session.get("admitted_failures_before_cutoff"), len(blocking_failures)
        )
    ):
        raise RunError("sealed scientific session violates fixed-range invariants")
    terminal_exists = (out / "TERMINAL.json").is_file()
    if status_value == "invalid_admitted_failure_before_selection_cutoff":
        terminal = load_json(out / "TERMINAL.json")
        expected_terminal = {
            "schema": "m51-deep-terminal-failure/v1",
            "certificate_base": CLASSIFICATION_CERTIFICATE_BASE,
            "reason": "admitted_failure_before_selection_cutoff",
            "selection_cutoff_global_index": selection_cutoff,
            "records": blocking_failures,
            "backfill_permitted": False,
            "fixed_range_completed": True,
            "created_utc": terminal.get("created_utc"),
        }
        if set(terminal) != {
            "schema",
            "certificate_base",
            "reason",
            "selection_cutoff_global_index",
            "records",
            "backfill_permitted",
            "fixed_range_completed",
            "created_utc",
        } or not exact_json_equal(terminal, expected_terminal):
            raise RunError("sealed invalid session has malformed terminal evidence")
        validate_utc_timestamp(terminal.get("created_utc"), "terminal:created_utc")
        if (
            selection.get("valid") is not False
            or selected_count != 0
            or not blocking_failures
            or not terminal_exists
        ):
            raise RunError("sealed invalid session lacks its no-backfill failure evidence")
    elif (
        selection.get("valid") is not True
        or blocking_failures != []
        or terminal_exists
        or (
            status_value == "quota_met_full_range_complete"
            and selected_count != TARGET_PAIRS
        )
        or (
            status_value == "range_exhausted_quota_not_met"
            and not 0 <= selected_count < TARGET_PAIRS
        )
    ):
        raise RunError("sealed valid session conflicts with its selection evidence")
    validate_chunk_directory_set(out, layout)


def validate_root_selection(
    out: Path,
    layout: ScanLayout,
    records: list[dict[str, Any]],
    pairs: list[Pair],
) -> None:
    selected: list[Pair] = []
    cutoff, failures = update_global_selection(selected, set(), set(), records, pairs)
    expected = aggregate_selection_document(
        selected, layout.shards, layout.shards, failures
    )
    actual = load_json(out / "selection.json")
    validate_utc_timestamp(actual.get("updated_utc"), "root selection:updated_utc")
    expected["updated_utc"] = actual["updated_utc"]
    if not exact_json_equal(actual, expected):
        raise RunError("root selection differs from complete classification reconstruction")
    expected_cutoff = selected[-1].global_index if len(selected) == TARGET_PAIRS else None
    if cutoff != expected_cutoff:
        raise RunError("root selection cutoff differs from reconstruction")


def cleanup_stale_root_partials(out: Path) -> None:
    """Remove only crash leftovers for the two declared mutable root files."""
    patterns = (
        re.compile(r"^\.session\.json\.partial-[0-9]+-[0-9]+-[0-9]+$"),
        re.compile(r"^\.selection\.json\.partial-[0-9]+-[0-9]+-[0-9]+$"),
        re.compile(r"^\.TERMINAL\.json\.partial-[0-9]+-[0-9]+-[0-9]+$"),
        re.compile(r"^\.DIRECTORIES\.json\.partial-[0-9]+-[0-9]+-[0-9]+$"),
        re.compile(r"^\.MANIFEST\.sha256\.partial-[0-9]+-[0-9]+-[0-9]+$"),
    )
    removed = False
    for path in out.iterdir():
        if not any(pattern.fullmatch(path.name) for pattern in patterns):
            continue
        if path.is_symlink() or not path.is_file():
            raise RunError(f"stale root partial is not a regular file: {path}")
        path.unlink()
        removed = True
    if removed:
        fsync_directory(out)


def validate_root_top_level(out: Path, *, mock: bool, sealed: bool) -> None:
    expected = {
        "inputs", "chunks", "attempts", "build", "run.json", "host.json",
        "run-command.txt", "session.json",
    }
    if mock:
        expected.add("MOCK-ONLY.json")
    else:
        expected.update({"controls", "aggregate", "classification", "selection.json"})
        if (out / "TERMINAL.json").exists() or (out / "TERMINAL.json").is_symlink():
            expected.add("TERMINAL.json")
    if sealed:
        expected.update({"DIRECTORIES.json", "MANIFEST.sha256"})
    elif (out / "DIRECTORIES.json").exists() or (out / "DIRECTORIES.json").is_symlink():
        # An exact orphan index is recoverable after a crash between its
        # publication and MANIFEST publication.
        expected.add("DIRECTORIES.json")
    actual = {path.name for path in out.iterdir()}
    if actual != expected:
        raise RunError(
            "terminal root inventory differs from the frozen contract; "
            f"missing={sorted(expected-actual)}, extra={sorted(actual-expected)}"
        )
    directory_names = {"inputs", "chunks", "attempts", "build"}
    if not mock:
        directory_names.update({"controls", "aggregate", "classification"})
    for name in expected:
        path = out / name
        if path.is_symlink():
            raise RunError(f"terminal root entry is a symlink: {path}")
        if name in directory_names:
            if not path.is_dir():
                raise RunError(f"terminal root directory has wrong type: {path}")
        elif not path.is_file():
            raise RunError(f"terminal root file has wrong type: {path}")


def validate_complete_run(
    out: Path,
    snapshots: Path,
    gp_runtime: dict[str, Any] | None,
    layout: ScanLayout,
    session: dict[str, Any],
    frozen: tuple[dict[str, str], str],
) -> None:
    """Replay every cheap semantic gate before sealing and on sealed resume."""
    validate_root_top_level(
        out, mock=layout.mock, sealed=(out / "MANIFEST.sha256").exists()
    )
    required_directories = {"build", "chunks"}
    if not layout.mock:
        required_directories |= {"controls", "aggregate", "classification"}
    for name in required_directories:
        path = out / name
        if path.is_symlink() or not path.is_dir():
            raise RunError(f"complete run lacks immutable directory {name}")
    verify_snapshot(out, frozen)
    binary, build_receipt = build_search(out, snapshots)
    verify_built_scanner(out, build_receipt)
    if session.get("binary_sha256") != build_receipt.get("binary_sha256"):
        raise RunError("terminal session scanner hash differs from build receipt")
    validate_chunk_directory_set(out, layout)
    stop = threading.Event()
    for shard_id in range(layout.shards):
        scan_shard(out, binary, layout, shard_id, stop)
    if layout.mock:
        validate_terminal_session(out, session, layout, mock=True)
        return
    if gp_runtime is None:
        raise RunError("scientific terminal validation lacks its GP runtime")
    verify_gp_runtime_artifacts(gp_runtime)
    controls_receipt = run_controls(out, snapshots, gp_runtime, stop)
    global_hits, hit_rows, aggregate_receipt = build_global_hits(out, layout)
    records, pairs, classification_receipt = classify_global(
        out, snapshots, gp_runtime, global_hits, hit_rows, stop
    )
    if (
        session.get("controls_sha256") != controls_receipt.get("controls_sha256")
        or session.get("aggregate_hits_sha256")
        != aggregate_receipt.get("hits_sha256")
        or not exact_int_equal(
            session.get("sieve_hits"), aggregate_receipt.get("rows")
        )
        or not exact_int_equal(session.get("classification_invocations"), 1)
        or not exact_int_equal(classification_receipt.get("records"), len(records))
    ):
        raise RunError("terminal session hashes/counts differ from nested receipts")
    validate_root_selection(out, layout, records, pairs)
    verify_gp_runtime_artifacts(gp_runtime)
    verify_snapshot(out, frozen)
    validate_terminal_session(out, session, layout, mock=False)


def seal_final(out: Path) -> Path:
    if (out / "MANIFEST.sha256").exists():
        verify_tree_manifest(out)
        return out / "MANIFEST.sha256"
    manifest = write_tree_manifest(out)
    manifest_stat = manifest.stat(follow_symlinks=False)
    directory_index = out / "DIRECTORIES.json"
    directory_stat = directory_index.stat(follow_symlinks=False)
    try:
        verify_tree_manifest(out)
    except BaseException:
        # Recover only the seal inode this invocation just published.  The
        # run remains unsealed and retryable; never unlink an attacker swap.
        try:
            current = manifest.stat(follow_symlinks=False)
            if (
                stat.S_ISREG(current.st_mode)
                and current.st_dev == manifest_stat.st_dev
                and current.st_ino == manifest_stat.st_ino
            ):
                manifest.unlink()
                current_directory = directory_index.stat(follow_symlinks=False)
                if (
                    stat.S_ISREG(current_directory.st_mode)
                    and current_directory.st_dev == directory_stat.st_dev
                    and current_directory.st_ino == directory_stat.st_ino
                ):
                    directory_index.unlink()
                fsync_directory(out)
        except OSError:
            pass
        raise
    return manifest


def _run_unlocked(args: argparse.Namespace) -> dict[str, Any]:
    out = args.out.resolve(strict=False)
    repo = REPO.resolve()
    if out == repo or repo in out.parents:
        raise RunError("output root must be outside the git worktree")
    if out.parent.is_symlink() or not out.parent.is_dir():
        raise RunError(f"output parent must be an existing regular directory: {out.parent}")
    gp_runtime = resolve_gp_runtime(args.gp_bin, args.gp_image, mock=args.mock)

    frozen = verify_frozen_inputs()
    spec = load_json(HERE / "spec.json")
    validate_spec(spec)
    layout = (
        ScanLayout(MOCK_START, MOCK_SHARDS, MOCK_SHARD_SIZE, SCI_ROOT_SEED, True)
        if args.mock
        else ScanLayout(SCI_START, SCI_SHARDS, SCI_SHARD_SIZE, SCI_ROOT_SEED, False)
    )
    validate_bijection_range(
        layout.probe_root_seed, layout.start, layout.end - layout.start
    )
    initialize_output(out, args.mock, gp_runtime, frozen, spec)
    identity = validate_resume_identity(out, args.mock, gp_runtime, frozen, spec)
    if not (out / "MANIFEST.sha256").exists():
        cleanup_stale_root_partials(out)
    if gp_runtime is not None:
        verify_gp_runtime_artifacts(gp_runtime)

    if (out / "MANIFEST.sha256").exists():
        verify_tree_manifest(out)
        final_session = load_json(out / "session.json")
        validate_complete_run(
            out, out / "inputs", gp_runtime, layout, final_session, frozen
        )
        return final_session

    stop = threading.Event()
    previous_handlers: dict[int, Any] = {}

    def handle_signal(signum: int, _frame: Any) -> None:
        stop.set()

    for signum in (signal.SIGINT, signal.SIGTERM):
        previous_handlers[signum] = signal.getsignal(signum)
        signal.signal(signum, handle_signal)

    started = time.monotonic()
    session: dict[str, Any] = {
        "schema": "m51-deep-scan-session/v1",
        "status": "running",
        "mode": identity["mode"],
        "scientific_eligible": not args.mock,
        "started_utc": utc_now(),
        "resumed": any((out / "chunks").iterdir()),
        "range": [layout.start, layout.end],
        "shards_planned": layout.shards,
        "shard_size": layout.shard_size,
        "workers": WORKERS,
        "cores": list(CORES),
        "target_pairs": 0 if args.mock else TARGET_PAIRS,
        "phase": "build",
    }
    atomic_replace_json(out / "session.json", session)
    try:
        verify_snapshot(out, frozen)
        binary, build = build_search(out, out / "inputs")
        if verify_built_scanner(out, build) != binary:
            raise RunError("build returned a scanner outside its sealed directory")
        verify_snapshot(out, frozen)
        session.update(phase="scan", binary_sha256=build["binary_sha256"])
        atomic_replace_json(out / "session.json", session)

        if args.mock:
            verify_snapshot(out, frozen)
            verify_built_scanner(out, build)
            with ThreadPoolExecutor(max_workers=WORKERS) as executor:
                futures = {
                    executor.submit(scan_shard, out, binary, layout, shard_id, stop): shard_id
                    for shard_id in range(layout.shards)
                }
                errors: list[tuple[int, BaseException]] = []
                for future in as_completed(futures):
                    shard_id = futures[future]
                    try:
                        future.result()
                    except BaseException as exc:
                        stop.set()
                        errors.append((shard_id, exc))
                if errors:
                    errors.sort(key=lambda item: item[0])
                    raise errors[0][1]
            verify_built_scanner(out, build)
            verify_snapshot(out, frozen)
            session.update(
                status="mock_complete_not_scientific",
                phase="complete",
                scientific_eligible=False,
                shards_scanned=layout.shards,
                shards_classified=0,
                selected_pairs=0,
                manifest=str(out / "MANIFEST.sha256"),
                finished_utc=utc_now(),
                elapsed_seconds=time.monotonic() - started,
            )
            validate_chunk_directory_set(out, layout)
            atomic_replace_json(out / "session.json", session)
            verify_built_scanner(out, build)
            verify_snapshot(out, frozen)
            validate_complete_run(
                out, out / "inputs", gp_runtime, layout, session, frozen
            )
            seal_final(out)
            return session

        if gp_runtime is None:
            raise RunError("scientific run lost its extracted GP runtime binding")
        session.update(phase="controls")
        atomic_replace_json(out / "session.json", session)
        verify_snapshot(out, frozen)
        verify_gp_runtime_artifacts(gp_runtime)
        controls_receipt = run_controls(
            out, out / "inputs", gp_runtime, stop
        )
        verify_gp_runtime_artifacts(gp_runtime)
        verify_snapshot(out, frozen)
        session.update(
            phase="scan",
            controls_passed=True,
            controls_sha256=controls_receipt["controls_sha256"],
        )
        atomic_replace_json(out / "session.json", session)
        verify_snapshot(out, frozen)
        verify_built_scanner(out, build)
        next_shard = 0
        while (
            next_shard < layout.shards
            and (out / "chunks" / f"shard-{next_shard:03d}").is_dir()
        ):
            # Validate every completed prefix shard before accepting it for resume.
            scan_shard(out, binary, layout, next_shard, stop)
            next_shard += 1
        while next_shard < layout.shards:
            if stop.is_set():
                raise RunError("execution interrupted")
            wave_start = (next_shard // WORKERS) * WORKERS
            wave = list(range(wave_start, min(wave_start + WORKERS, layout.shards)))
            if wave:
                with ThreadPoolExecutor(max_workers=WORKERS) as executor:
                    futures = {
                        executor.submit(
                            scan_shard, out, binary, layout, shard_id, stop
                        ): shard_id
                        for shard_id in wave
                    }
                    errors: list[tuple[int, BaseException]] = []
                    for future in as_completed(futures):
                        shard_id = futures[future]
                        try:
                            future.result()
                        except BaseException as exc:
                            stop.set()
                            errors.append((shard_id, exc))
                    if errors:
                        errors.sort(key=lambda item: item[0])
                        raise errors[0][1]

            next_shard = wave[-1] + 1
            session.update(
                phase="scan",
                shards_scanned=count_completed_shards(out, layout),
                shards_classified=0,
                selected_pairs=0,
                current_shard=None,
            )
            atomic_replace_json(out / "session.json", session)

        scanned = count_completed_shards(out, layout)
        if scanned != layout.shards:
            raise RunError("runner stopped before complete fixed-range scan")
        validate_chunk_directory_set(out, layout)
        verify_built_scanner(out, build)
        verify_snapshot(out, frozen)

        session.update(phase="aggregate", shards_scanned=scanned)
        atomic_replace_json(out / "session.json", session)
        global_hits, hit_rows, aggregate_receipt = build_global_hits(out, layout)
        session.update(
            phase="classify",
            aggregate_hits_sha256=aggregate_receipt["hits_sha256"],
            sieve_hits=len(hit_rows),
        )
        atomic_replace_json(out / "session.json", session)
        verify_snapshot(out, frozen)
        verify_gp_runtime_artifacts(gp_runtime)
        records, pairs, _classification_receipt = classify_global(
            out, out / "inputs", gp_runtime, global_hits, hit_rows, stop
        )
        verify_gp_runtime_artifacts(gp_runtime)
        verify_snapshot(out, frozen)

        selected: list[Pair] = []
        seen_bottom: set[int] = set()
        seen_parent: set[int] = set()
        cutoff, admitted_failures = update_global_selection(
            selected, seen_bottom, seen_parent, records, pairs
        )
        selection_document = aggregate_selection_document(
            selected,
            layout.shards,
            scanned,
            admitted_failures,
        )
        atomic_replace_json(out / "selection.json", selection_document)
        expected_cutoff = (
            selected[-1].global_index if len(selected) == TARGET_PAIRS else None
        )
        if cutoff != expected_cutoff:
            raise RunError("internal selection cutoff mismatch")
        cutoff = selection_document["cutoff_global_index"]
        invalid_failures = selection_document["blocking_failures"]
        if invalid_failures:
            status_value = "invalid_admitted_failure_before_selection_cutoff"
            terminal_path = out / "TERMINAL.json"
            terminal_stable = {
                "schema": "m51-deep-terminal-failure/v1",
                "certificate_base": CLASSIFICATION_CERTIFICATE_BASE,
                "reason": "admitted_failure_before_selection_cutoff",
                "selection_cutoff_global_index": cutoff,
                "records": invalid_failures,
                "backfill_permitted": False,
                "fixed_range_completed": True,
            }
            if terminal_path.exists():
                existing_terminal = load_json(terminal_path)
                existing_stable = {
                    key: value
                    for key, value in existing_terminal.items()
                    if key != "created_utc"
                }
                if existing_stable != terminal_stable:
                    raise RunError("existing terminal failure record differs from reconstruction")
            else:
                atomic_write_json(
                    terminal_path,
                    {**terminal_stable, "created_utc": utc_now()},
                )
        elif len(selected) == TARGET_PAIRS:
            if (out / "TERMINAL.json").exists():
                raise RunError("unexpected terminal failure record for valid reconstruction")
            status_value = "quota_met_full_range_complete"
        else:
            if (out / "TERMINAL.json").exists():
                raise RunError("unexpected terminal failure record for valid reconstruction")
            status_value = "range_exhausted_quota_not_met"
        session.update(
            status=status_value,
            phase="complete",
            shards_scanned=scanned,
            shards_classified=layout.shards,
            classification_invocations=1,
            selected_pairs=selection_document["selected_count"],
            provisional_selected_pairs=selection_document["provisional_selected_count"],
            cutoff_global_index=cutoff,
            admitted_failures_total=len(admitted_failures),
            admitted_failures_before_cutoff=len(invalid_failures),
            fixed_range_exhausted=True,
            manifest=str(out / "MANIFEST.sha256"),
            finished_utc=utc_now(),
            elapsed_seconds=time.monotonic() - started,
        )
        session.pop("current_shard", None)
        atomic_replace_json(out / "session.json", session)
        verify_built_scanner(out, build)
        verify_snapshot(out, frozen)
        verify_gp_runtime_artifacts(gp_runtime)
        validate_complete_run(
            out, out / "inputs", gp_runtime, layout, session, frozen
        )
        seal_final(out)
        return session
    except BaseException as exc:
        # The root seal is the last mutable operation.  A later presentation
        # failure must never rewrite a session already covered by MANIFEST.
        if (out / "MANIFEST.sha256").exists():
            raise
        session.update(
            status="invalid" if isinstance(exc, AdmittedFailure) else "failed_resumable",
            phase=session.get("phase", "unknown"),
            error=repr(exc),
            failed_utc=utc_now(),
            elapsed_seconds=time.monotonic() - started,
            shards_scanned=count_completed_shards(out, layout),
        )
        try:
            atomic_replace_json(out / "session.json", session)
        except BaseException:
            pass
        raise
    finally:
        stop.set()
        for signum, handler in previous_handlers.items():
            signal.signal(signum, handler)


def run(args: argparse.Namespace) -> dict[str, Any]:
    """Serialize every mutation of one output root, including initialization."""
    if not (
        sys.flags.isolated
        and sys.flags.no_site
        and sys.flags.ignore_environment
        and sys.dont_write_bytecode
    ):
        raise RunError("invoke the admitted runner with python3 -I -S -B")
    enable_child_subreaper()
    out = args.out.resolve(strict=False)
    repo = REPO.resolve()
    if out == repo or repo in out.parents:
        raise RunError("output root must be outside the git worktree")
    if out.parent.is_symlink() or not out.parent.is_dir():
        raise RunError(f"output parent must be an existing regular directory: {out.parent}")
    lock_path = out.parent / f".{out.name}.run.lock"
    flags = os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(lock_path, flags, 0o600)
    except OSError as exc:
        raise RunError(f"cannot open output-root lock {lock_path}: {exc}") from exc
    try:
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RunError(f"another runner owns output root {out}") from exc
        return _run_unlocked(args)
    finally:
        try:
            fcntl.flock(descriptor, fcntl.LOCK_UN)
        finally:
            os.close(descriptor)


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run or resume the frozen m=51 deep-volcano discovery scan",
        allow_abbrev=False,
    )
    parser.add_argument("--out", type=Path, required=True, help="write-once run root outside git")
    parser.add_argument(
        "--gp-bin",
        type=Path,
        help="exact pinned PARI/GP extraction; required for scientific mode",
    )
    parser.add_argument(
        "--gp-image",
        help=(
            "rejected for admitted runs to prevent daemon-side container zombies; "
            f"the provenance image is {PINNED_GP_IMAGE_ID}"
        ),
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="run four tiny tagged mock-scan shards; never scientific evidence",
    )
    return parser.parse_args(argv)


def main() -> None:
    try:
        result = run(parse_args())
    except (RunError, OSError, ValueError) as exc:
        print(f"run_scan.py: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    try:
        print(json.dumps(result, indent=2, sort_keys=True))
    except BrokenPipeError as exc:
        raise SystemExit(1) from exc
    if str(result.get("status", "")).startswith("invalid_"):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
