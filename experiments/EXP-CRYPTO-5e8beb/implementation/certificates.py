"""Canonical serialization, witnesses, hashing and the expected artifact
index for EXP-CRYPTO-5e8beb.

This module defines pure, deterministic serialization helpers shared by the
future driver (never by `reference.py`, which stays fully independent). It
performs no filesystem I/O and no scientific computation; it only describes
*shapes*: how a Fraction becomes JSON, how a distribution/pair/witness is
canonicalized and hashed, and what the full expected path/count index for one
completed run looks like, matching `specification.artifacts` and
`specification.fixed_counts` exactly.

Nothing here is invoked at import time or by this task.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum
from fractions import Fraction
from typing import Any, Dict, List, Optional, Sequence, Tuple

import fixtures


# --- canonical fraction / table serialization -------------------------------

def serialize_fraction(value: Fraction) -> Dict[str, int]:
    """Canonical integer numerator / positive-denominator serialization."""
    if not isinstance(value, Fraction):
        value = Fraction(value)
    if value.denominator <= 0:
        raise ValueError("Fraction denominator must already be positive")
    return {"numerator": value.numerator, "denominator": value.denominator}


def deserialize_fraction(obj: Dict[str, int]) -> Fraction:
    num, den = obj["numerator"], obj["denominator"]
    if den <= 0:
        raise ValueError("invalid_denominator: denominator must be positive")
    return Fraction(num, den)


def serialize_distribution(dist: Dict[Any, Fraction]) -> List[Dict[str, Any]]:
    """A canonical list of {key, mass} rows, keys rendered as strings so JSON
    key types never lose transcript-tuple structure; ordered by the string
    form of the key for a stable byte-for-byte hash.
    """
    rows = [{"key": repr(k), "mass": serialize_fraction(v)} for k, v in dist.items()]
    rows.sort(key=lambda r: r["key"])
    return rows


def canonical_json_bytes(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def hash_object(obj: Any) -> str:
    return sha256_hex(canonical_json_bytes(obj))


# --- witnesses ----------------------------------------------------------------

@dataclass(frozen=True)
class PairWitness:
    """Serializable form of a maximizer witness pair, or an explicit null."""
    x: Optional[int]
    xp: Optional[int]

    @staticmethod
    def from_optional_pair(pair: Optional[Tuple[int, int]]) -> "PairWitness":
        if pair is None:
            return PairWitness(None, None)
        return PairWitness(pair[0], pair[1])

    def to_json(self) -> Dict[str, Optional[int]]:
        return {"x": self.x, "xp": self.xp}


# --- status / validity taxonomy ---------------------------------------------

class CertificateStatus(str, Enum):
    OK = "ok"
    BOUND_INAPPLICABLE = "bound_inapplicable"   # assumption-trap classification
    VACUOUS_BOUND = "vacuous_bound"             # bound == 1, never quantitative evidence
    INVALID_MEASUREMENT = "invalid_measurement"
    INCOMPLETE = "incomplete"


@dataclass(frozen=True)
class CertificateResult:
    status: CertificateStatus
    reason: Optional[str] = None
    payload: Optional[dict] = None

    def to_json(self) -> dict:
        return {
            "status": self.status.value,
            "reason": self.reason,
            "payload": self.payload,
        }


def incomplete_result(reason: str) -> CertificateResult:
    return CertificateResult(CertificateStatus.INCOMPLETE, reason=reason)


def invalid_result(reason: str) -> CertificateResult:
    return CertificateResult(CertificateStatus.INVALID_MEASUREMENT, reason=reason)


def bound_inapplicable_result(payload: dict) -> CertificateResult:
    return CertificateResult(CertificateStatus.BOUND_INAPPLICABLE, payload=payload)


def ok_result(payload: dict, vacuous: bool = False) -> CertificateResult:
    if vacuous:
        return CertificateResult(CertificateStatus.VACUOUS_BOUND, payload=payload)
    return CertificateResult(CertificateStatus.OK, payload=payload)


# --- expected artifact path/count index -------------------------------------
# Mirrors specification.artifacts and specification.fixed_counts exactly.
# Building this index performs no I/O; it only enumerates the paths a
# completed run is expected to contain, for later completeness checking.

ROOT_FILENAMES = (
    "launch.json", "receipt.json", "manifest.yaml", "command.txt",
    "environment.json", "stdout.log", "stderr.log", "raw-result.json",
    "source-bindings.json", "launch-binding.json", "fixture-index.json",
    "score-table.json", "control-summary.json", "counters.json",
    "resources.json", "incomplete-receipts.jsonl", "execution-report.yaml",
    "artifact-sha256.json",
)
PARTITION_FILENAMES = ("feature.json", "fibers.json", "generation.json", "description.json")
KERNEL_FILENAMES = ("law.json", "K.json", "pair-TV.jsonl", "maxima.json", "checker-report.json")
TRANSCRIPT_FILENAMES = (
    "real-joint.json", "simulator-joint.json", "reference-joint.json",
    "TV-certificate.json", "status.json",
)
TRAP_FILENAMES = (
    "law.json", "real-joint.json", "simulator-joint.json",
    "reference-joint.json", "TV-certificate.json", "assumption-status.json",
)
HORIZONS = (0, 1, 2, 3)


def expected_partition_dir(index: int) -> str:
    return f"partitions/{index:03d}"


def expected_kernel_dir(index: int, kernel_name: str) -> str:
    return f"{expected_partition_dir(index)}/kernels/{kernel_name}"


def expected_transcript_dir(index: int, kernel_name: str, x: int, t: int) -> str:
    return f"{expected_kernel_dir(index, kernel_name)}/starts/x-{x}/t-{t}"


def expected_trap_dir(x: int) -> str:
    return f"assumption-trap/x-{x}"


def expected_partition_paths() -> List[str]:
    paths = []
    for spec in fixtures.iter_partition_specs():
        base = expected_partition_dir(spec.index)
        for name in PARTITION_FILENAMES:
            paths.append(f"{base}/{name}")
    return paths


def expected_kernel_paths() -> List[str]:
    paths = []
    for spec in fixtures.iter_partition_specs():
        for kernel_name in fixtures.KERNEL_ORDER:
            base = expected_kernel_dir(spec.index, kernel_name)
            for name in KERNEL_FILENAMES:
                paths.append(f"{base}/{name}")
    return paths


def expected_transcript_paths() -> List[str]:
    paths = []
    for spec in fixtures.iter_partition_specs():
        for kernel_name in fixtures.KERNEL_ORDER:
            for x in range(spec.N):
                for t in HORIZONS:
                    base = expected_transcript_dir(spec.index, kernel_name, x, t)
                    for name in TRANSCRIPT_FILENAMES:
                        paths.append(f"{base}/{name}")
    return paths


def expected_trap_paths() -> List[str]:
    paths = []
    for x in range(11):  # spec.assumption_trap.N == 11, every visible state
        base = expected_trap_dir(x)
        for name in TRAP_FILENAMES:
            paths.append(f"{base}/{name}")
    return paths


def expected_artifact_index() -> Dict[str, List[str]]:
    """Full expected artifact path index for one completed run directory
    (relative to `experiments/EXP-CRYPTO-5e8beb/runs/<RUN_ID>/`).
    """
    return {
        "root_filenames": list(ROOT_FILENAMES),
        "partition_paths": expected_partition_paths(),
        "kernel_paths": expected_kernel_paths(),
        "transcript_paths": expected_transcript_paths(),
        "trap_paths": expected_trap_paths(),
    }


def expected_counts() -> Dict[str, int]:
    """Fixed counts recomputed from the path index, to be cross-checked
    against `specification.fixed_counts` (never invented, never adjusted).
    """
    index = expected_artifact_index()
    n_partitions = fixtures.spec_count()
    n_kernel_cells = n_partitions * len(fixtures.KERNEL_ORDER)
    n_initial_state_kernel_combinations = sum(
        spec.N for spec in fixtures.iter_partition_specs()
    ) * len(fixtures.KERNEL_ORDER)
    n_main_transcript_checks = n_initial_state_kernel_combinations * len(HORIZONS)
    return {
        "main_partitions": n_partitions,
        "main_partition_kernel_cells": n_kernel_cells,
        "initial_state_kernel_combinations": n_initial_state_kernel_combinations,
        "main_full_transcript_checks": n_main_transcript_checks,
        "trap_full_transcript_checks": 11,
        "total_full_transcript_checks": n_main_transcript_checks + 11,
    }
