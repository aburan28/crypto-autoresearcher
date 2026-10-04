#!/usr/bin/env python3
"""Cold single-target process runner for RUN-KIC-e3dbed.

``prepare`` creates custody without launching a solver. ``validate-preserved-
conformance`` parses attempt 2 without launching a solver. ``scientific`` runs
the frozen schedule only after a committed Coordinator admission binds this
exact code, the common ARM fairness amendment, attempt 3, sources, and binaries.
The protocol word ``binary`` is a placeholder, never an argv token.
"""

from __future__ import annotations

import argparse
import ctypes
import datetime as dt
import gzip
import hashlib
import io
import json
import os
import platform
import shutil
import signal
import statistics
import subprocess
import sys
import tarfile
import time
import tomllib
from pathlib import Path
from typing import Any, Iterable

RUN_ROOT = Path(__file__).resolve().parent
PACKAGE_ROOT = RUN_ROOT.parents[1]
REPO_ROOT = PACKAGE_ROOT.parents[1]
PROTOCOL_PATH = PACKAGE_ROOT / "protocol.json"
BASELINE_SOURCE = PACKAGE_ROOT / "source_arm"
CANDIDATE_SOURCE = PACKAGE_ROOT / "source_arm_allocation"
BASELINE_BUILD = PACKAGE_ROOT / "arm_build" / "target" / "release" / "examples"
CANDIDATE_BUILD = RUN_ROOT / "arm_candidate_target" / "release" / "examples"
BASELINE_DIRECT = BASELINE_BUILD / "koblitz_rank_fixture"
BASELINE_RHO = BASELINE_BUILD / "koblitz_rho_fixture"
CANDIDATE_DIRECT = CANDIDATE_BUILD / "koblitz_rank_fixture"
ANALYZER_PATH = RUN_ROOT / "analyze.py"
CASE_MANIFEST_PATH = RUN_ROOT / "case_manifest.json"
PREFLIGHT_PATH = RUN_ROOT / "runner_preflight.json"
PROCESSES_PATH = RUN_ROOT / "processes.jsonl"
RAW_ROOT = RUN_ROOT / "raw_processes"
CALIBRATION_SELECTION_PATH = RUN_ROOT / "calibration_selection.json"
RAW_TAR_PATH = RUN_ROOT / "raw_processes.tar.gz"
RAW_MANIFEST_PATH = RUN_ROOT / "raw_processes_manifest.json"
ENVIRONMENT_PATH = RUN_ROOT / "environment.json"
EXECUTION_RECEIPT_PATH = RUN_ROOT / "execution_receipt.json"
ARTIFACT_MANIFEST_PATH = RUN_ROOT / "artifact_manifest.json"
ADMISSION_PATH = PACKAGE_ROOT / "measurement_admission.json"
SOURCE_CLOSURE_PATH = RUN_ROOT / "source_closure.json"
BUILD_TOOLCHAIN_PATH = RUN_ROOT / "build_toolchain.json"
CANDIDATE_PATCH_PATH = RUN_ROOT / "candidate.patch"
CANDIDATE_TAR_PATH = RUN_ROOT / "candidate_source.tar.gz"
CUSTODY_ROOT = RUN_ROOT / "custody"
BINARIES_TAR_PATH = CUSTODY_ROOT / "binaries.tar.gz"
DEPENDENCIES_TAR_PATH = CUSTODY_ROOT / "dependencies.tar.gz"
CUSTODY_LOCK_PATH = CUSTODY_ROOT / "Cargo.lock"
PRESERVED_ATTEMPT2 = RUN_ROOT / "conformance" / "attempt2"
PRESERVED_VALIDATION_PATH = PRESERVED_ATTEMPT2 / "validation_attempt3_static.json"
ATTEMPT3_ROOT = RUN_ROOT / "conformance" / "attempt3"
ATTEMPT3_FINAL_VALIDATION_PATH = ATTEMPT3_ROOT / "final_parser_validation.json"

PROTOCOL_SHA256 = "27f2de2414d5b5e3882bfee54ae122f62c4b84b36bdc031cbf67d7ffa892c708"
EXPERIMENT_ID = "RUN-KIC-e3dbed"
TASK_ID = "TASK-20260921-362caa"
N = 53
SUBGROUP_ORDER = 21044858204113
WATCHDOG_SECONDS = 240.0
MEMORY_LIMIT_BYTES = 8 * 1024**3
DIRECT_ENV = {
    "KIC_INCREMENTAL_RANK_CROSSCHECK": "0", "KIC_RANK_SURPLUS": "0",
    "KIC_RANK_AWARE_PAIR_SCAN": "1", "KIC_PARALLEL_SUPPORT_EXPANSION": "0",
    "KIC_PIPELINED_SUPPORT_EXPANSION": "0", "RAYON_NUM_THREADS": "1",
}
RHO_ENV = {"RAYON_NUM_THREADS": "1"}
CALIBRATION_CONFIGS = (
    ("baseline_unmodified_eta_1_128", "baseline", 128),
    ("allocation_only_eta_1_128", "candidate", 128),
    ("allocation_only_eta_1_256", "candidate", 256),
    ("allocation_only_eta_1_512", "candidate", 512),
)
CALIBRATION_SCALARS = (
    2039485612345, 18972654321098, 14723890561234, 9182736450192,
    20018473650981, 6432198765012, 17364509281764, 11230984567123,
    19874561230987, 7812345098765, 15678902345678, 20987654321012,
)
HELDOUT_SCALARS = (
    16420987543210, 5098712345678, 19123456789012, 8675309123456,
    14285714285714, 20765432109876, 10987654321098, 17530986420135,
    7319450867123, 19682013457901, 12468097531246, 2135790246813,
    18123450987654, 9988776655443, 15432098765432, 6789012345678,
    20246801357924, 13579246801357, 18765432098765, 8246801357924,
    16975308642197, 4567890123456, 20567890123456, 11864209753186,
)
EXPECTED_K = {128: 94, 256: 75, 512: 60}


class ValidationError(RuntimeError):
    def __init__(self, message: str, *, unexpected: bool = False) -> None:
        super().__init__(message)
        self.unexpected = unexpected


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def digest_value(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, sort_keys=True, indent=2)
        stream.write("\n")
        stream.flush(); os.fsync(stream.fileno())
    os.replace(temporary, path)


def write_once_json(path: Path, value: Any) -> None:
    encoded = json.dumps(value, sort_keys=True, indent=2) + "\n"
    if path.exists():
        if path.read_text(encoding="utf-8") != encoded:
            raise RuntimeError(f"immutable artifact already exists with different bytes: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(encoded); stream.flush(); os.fsync(stream.fileno())


def append_jsonl(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n")
        stream.flush(); os.fsync(stream.fileno())


def require(condition: bool, message: str, *, unexpected: bool = False) -> None:
    if not condition:
        raise ValidationError(message, unexpected=unexpected)


def field(record: dict[str, Any], name: str, *, nullable: bool = False) -> Any:
    require(name in record, f"missing required field {name!r}")
    value = record[name]
    if not nullable:
        require(value is not None, f"required field {name!r} is null")
    return value


def derive_seed(label: str) -> int:
    return int.from_bytes(hashlib.sha256(label.encode()).digest()[:8], "little")


def compute_k(n: int, denominator: int, order: int) -> int:
    k = 1
    while ((2 * n * k) ** 3) * denominator < order * 6:
        k += 1
    return k


def load_protocol() -> dict[str, Any]:
    require(PROTOCOL_PATH.is_file(), "protocol.json is absent")
    require(sha256_file(PROTOCOL_PATH) == PROTOCOL_SHA256, "protocol hash changed")
    protocol = json.loads(PROTOCOL_PATH.read_text())
    require(protocol.get("experiment_id") == EXPERIMENT_ID, "experiment id mismatch")
    return protocol


def parse_json_lines(data: bytes) -> list[dict[str, Any]]:
    records = []
    for line_number, line in enumerate(data.decode("utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValidationError(f"stdout line {line_number} is not JSON: {exc}") from exc
        require(isinstance(value, dict), f"stdout line {line_number} is not a JSON object")
        records.append(value)
    require(bool(records), "stdout contains no JSON records")
    return records


def exact_one(records: list[dict[str, Any]], kind: str) -> dict[str, Any]:
    matches = [record for record in records if record.get("kind") == kind]
    require(len(matches) == 1, f"expected exactly one {kind}, found {len(matches)}")
    return matches[0]


def parse_direct_output(data: bytes, *, expected_scalar: int, expected_n: int, expected_k: int,
                        expected_arithmetic_backend: str | None = None) -> dict[str, Any]:
    records = parse_json_lines(data)
    allowed = {"point_defined_factor_base", "relation_rank_receipt", "relation_rank_summary"}
    for record in records:
        require(record.get("kind") in allowed, f"unexpected direct record kind {record.get('kind')!r}")
    base = exact_one(records, "point_defined_factor_base")
    summary = exact_one(records, "relation_rank_summary")
    relations = [r for r in records if r.get("kind") == "relation_rank_receipt"]
    relations.sort(key=lambda r: field(r, "accepted_relation"))
    base_hash = field(base, "base_hash")
    require(isinstance(base_hash, str) and len(base_hash) == 64, "invalid base_hash")
    require(field(base, "n") == expected_n, "base n mismatch")
    require(field(base, "orbit_columns") == expected_k, "factor-base K mismatch")
    require(field(base, "subgroup_membership_verified") is True, "base subgroup check failed")
    require(field(base, "selection_uses_scalar_labels") is False, "base used scalar labels")
    require(field(base, "parallel_support_expansion") is False, "parallel support enabled")
    require(field(base, "pipelined_support_expansion") is False, "pipelined support enabled")
    require(field(base, "parallel_support_expansion_threads") == 0, "support threads not zero")
    require(field(summary, "n") == expected_n and field(summary, "base_hash") == base_hash, "summary/base mismatch")
    require(field(summary, "status") == "FULL_RANK", "direct status is not FULL_RANK")
    require(field(summary, "fixture_scalar_source") == "explicit_public_validation_scalar", "non-explicit target")
    require(field(summary, "target_kind") == "known_scalar_multiple", "unexpected target kind")
    require(field(summary, "target_scalar_constructed") is True, "target not scalar constructed")
    require(field(summary, "published_fixture_scalar") == expected_scalar, "published scalar mismatch", unexpected=True)
    require(field(summary, "recovered_fixture_scalar") == expected_scalar, "recovered scalar mismatch", unexpected=True)
    require(field(summary, "linear_solution_verified") is True, "linear verification failed", unexpected=True)
    require(field(summary, "all_relations_group_verified") is True, "group verification failed", unexpected=True)
    require(field(summary, "query_parallel_threads") == 1, "query threads not one")
    require(field(summary, "query_mode") == "pair_pair_parallel_4096", "query mode mismatch")
    published_q = field(summary, "published_q")
    require(isinstance(published_q, list) and len(published_q) == 2, "published_q malformed")
    admitted = field(summary, "admitted_relations")
    require(isinstance(admitted, int) and admitted > 0 and len(relations) == admitted, "relation count mismatch")
    require(field(summary, "reference_relations_validated") == admitted, "not all relations validated")
    require([field(r, "accepted_relation") for r in relations] == list(range(1, admitted + 1)), "relation sequence incomplete")
    relation_hashes, sparse_rows, rank_progression = [], [], []
    for relation in relations:
        require(field(relation, "n") == expected_n and field(relation, "base_hash") == base_hash, "relation/base mismatch")
        require(field(relation, "published_fixture_scalar") == expected_scalar, "relation scalar mismatch", unexpected=True)
        require(field(relation, "target_kind") == "known_scalar_multiple", "relation target mismatch")
        require(field(relation, "target_scalar_constructed") is True, "relation target not constructed")
        require(field(relation, "fixture_scalar_used_by_collector") is False, "collector used scalar")
        require(field(relation, "verified_group_identity") is True, "relation group identity failed", unexpected=True)
        relation_hash = field(relation, "relation_hash")
        sparse_row = field(relation, "sparse_row")
        require(isinstance(relation_hash, str) and len(relation_hash) == 64, "invalid relation hash")
        require(isinstance(sparse_row, list) and bool(sparse_row), "invalid sparse row")
        relation_hashes.append(relation_hash); sparse_rows.append(sparse_row)
        rank_progression.append({k: field(relation, k) for k in ("accepted_relation", "rank_before", "rank_after", "rank_incremented")})
    summary_hashes = field(summary, "relation_hashes", nullable=True)
    if summary_hashes is not None:
        require(summary_hashes == relation_hashes, "summary relation hashes differ")
    terminal_rank, columns = field(summary, "terminal_rank"), field(summary, "matrix_columns")
    require(terminal_rank == columns, "terminal rank not full")
    require(columns == expected_k + 1, "matrix column count is not K+1")
    require(field(summary, "surplus_relations") == 0, "surplus relation count is not zero")
    rank_fields = {
        "matrix_columns": columns, "terminal_rank": terminal_rank,
        "full_rank_at_relation": field(summary, "full_rank_at_relation"),
        "admitted_relations": admitted, "surplus_relations": field(summary, "surplus_relations"),
        "rank_progression": rank_progression,
    }
    field_mul_backend = field(summary, "field_mul_backend")
    field_square_backend = field(summary, "field_square_backend")
    if expected_arithmetic_backend is not None:
        require(field_mul_backend == expected_arithmetic_backend, "direct multiplication backend mismatch")
        require(field_square_backend == expected_arithmetic_backend, "direct squaring backend mismatch")
    semantic = {
        "n": expected_n, "status": "FULL_RANK", "factor_base_k": expected_k, "base_hash": base_hash,
        "factor_base_points": field(base, "factor_base_points"), "relation_hashes": relation_hashes,
        "sparse_rows": sparse_rows, "rank_fields": rank_fields,
        "published_fixture_scalar": expected_scalar, "recovered_fixture_scalar": expected_scalar,
        "published_q": published_q, "linear_solution_verified": True,
        "all_relations_group_verified": True, "query_parallel_threads": 1,
        "parallel_support_expansion_threads": 0,
        "field_mul_backend": field_mul_backend,
        "field_square_backend": field_square_backend,
    }
    return {
        **semantic, "accepted_relation_digest": digest_value(relation_hashes),
        "sparse_rows_digest": digest_value(sparse_rows), "result_digest": digest_value(semantic),
        "relation_hashes_derived_from_receipt_rows": summary_hashes is None, "record_count": len(records),
    }


def parse_rho_output(data: bytes, *, expected_scalar: int, expected_n: int,
                     expected_arithmetic_backend: str | None = None) -> dict[str, Any]:
    records = parse_json_lines(data)
    require(len(records) == 1, f"expected one rho record, found {len(records)}")
    receipt = records[0]
    require(receipt.get("kind") == "rho_public_fixture", "rho kind mismatch")
    require(field(receipt, "n") == expected_n, "rho n mismatch")
    require(field(receipt, "fixture_scalar_source") == "explicit_public_validation_scalar", "rho target not explicit")
    require(field(receipt, "target_kind") == "known_scalar_multiple", "rho target kind mismatch")
    require(field(receipt, "target_scalar_constructed") is True, "rho target not constructed")
    require(field(receipt, "published_fixture_scalar") == expected_scalar, "rho published scalar mismatch", unexpected=True)
    require(field(receipt, "recovered_fixture_scalar") == expected_scalar, "rho recovered scalar mismatch", unexpected=True)
    require(field(receipt, "verified") is True, "rho verification failed", unexpected=True)
    require(field(receipt, "reference_group_validation") is True, "rho group validation failed", unexpected=True)
    published_q = field(receipt, "published_q")
    require(isinstance(published_q, list) and len(published_q) == 2, "rho published_q malformed")
    multiplication_backend = receipt.get("field_multiplication_backend")
    squaring_backend = receipt.get("field_squaring_backend")
    if expected_arithmetic_backend is not None:
        field(receipt, "field_multiplication_backend")
        field(receipt, "field_squaring_backend")
        require(multiplication_backend == expected_arithmetic_backend, "rho multiplication backend mismatch")
        require(squaring_backend == expected_arithmetic_backend, "rho squaring backend mismatch")
    semantic = {
        "n": expected_n, "published_fixture_scalar": expected_scalar,
        "recovered_fixture_scalar": expected_scalar, "published_q": published_q,
        "verified": True, "reference_group_validation": True,
        "quotient_mode": field(receipt, "quotient_mode"),
        "arithmetic_backend": field(receipt, "arithmetic_backend"),
        "field_multiplication_backend": multiplication_backend,
        "field_squaring_backend": squaring_backend,
    }
    return {**semantic, "result_digest": digest_value(semantic), "record_count": 1}


def direct_equivalence(left: dict[str, Any], right: dict[str, Any]) -> dict[str, list[Any]]:
    keys = (
        "factor_base_k", "base_hash", "factor_base_points", "relation_hashes", "sparse_rows",
        "rank_fields", "published_fixture_scalar", "recovered_fixture_scalar", "published_q",
        "linear_solution_verified", "all_relations_group_verified", "accepted_relation_digest",
        "sparse_rows_digest", "result_digest", "field_mul_backend", "field_square_backend",
    )
    return {key: [left.get(key), right.get(key)] for key in keys if left.get(key) != right.get(key)}


def make_case_manifest() -> dict[str, Any]:
    protocol = load_protocol(); calibration, heldout = [], []; ordinal = 0
    for scalar_index, scalar in enumerate(CALIBRATION_SCALARS, 1):
        label, numeric_seed = f"CSIC53-CAL-v1-s{scalar_index}", derive_seed(f"CSIC53-CAL-v1-s{scalar_index}")
        for configuration, source, denominator in CALIBRATION_CONFIGS:
            ordinal += 1
            calibration.append({
                "ordinal": ordinal, "phase": "calibration", "id": f"cal-s{scalar_index:02d}-{configuration}",
                "scalar_index": scalar_index, "scalar": scalar, "solver": "direct",
                "configuration": configuration, "source": source, "eta_denominator": denominator,
                "factor_base_k": compute_k(N, denominator, SUBGROUP_ORDER), "seed_label": label, "seed": numeric_seed,
            })
    for scalar_index, scalar in enumerate(HELDOUT_SCALARS, 1):
        order = ("direct", "rho") if scalar_index % 2 else ("rho", "direct")
        for solver in order:
            ordinal += 1; label = f"CSIC53-HO-v1-{solver}-s{scalar_index}"
            heldout.append({
                "ordinal": ordinal, "phase": "heldout", "id": f"ho-s{scalar_index:02d}-{solver}",
                "scalar_index": scalar_index, "scalar": scalar, "solver": solver,
                "source": "candidate" if solver == "direct" else "baseline",
                "eta_denominator_source": "calibration_selection.json" if solver == "direct" else None,
                "seed_label": label, "seed": derive_seed(label),
            })
    require(len(calibration) == 48 and len(heldout) == 48 and ordinal == 96, "case count error")
    require(len(set(CALIBRATION_SCALARS + HELDOUT_SCALARS)) == 36, "scalars not disjoint")
    require({d: compute_k(N, d, SUBGROUP_ORDER) for d in EXPECTED_K} == EXPECTED_K, "K changed")
    return {
        "schema": "crypto.autoresearch.cold_single_ic_case_manifest.v1", "experiment_id": EXPERIMENT_ID,
        "task_id": TASK_ID, "protocol_sha256": PROTOCOL_SHA256,
        "seed_derivation": "first eight SHA-256 bytes interpreted little-endian",
        "execution_order": "case-major calibration then alternating held-out pairs",
        "calibration": calibration, "heldout": heldout,
        "counts": {"calibration": 48, "heldout": 48, "scientific": 96},
        "protocol_case_digest": digest_value(protocol["frozen_cases"]),
    }


def normalized_tar(paths: Iterable[tuple[Path, str]], destination: Path, extra: dict[str, bytes] | None = None) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True); temporary = destination.with_name(destination.name + ".tmp")
    with temporary.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode="w", format=tarfile.PAX_FORMAT) as archive:
                for path, arcname in sorted(paths, key=lambda item: item[1]):
                    info = archive.gettarinfo(str(path), arcname=arcname)
                    info.uid = info.gid = 0; info.uname = info.gname = ""; info.mtime = 0
                    with path.open("rb") as source:
                        archive.addfile(info, source)
                for name, data in sorted((extra or {}).items()):
                    info = tarfile.TarInfo(name); info.size = len(data); info.mode = 0o644
                    info.uid = info.gid = 0; info.uname = info.gname = ""; info.mtime = 0
                    archive.addfile(info, io.BytesIO(data))
        raw.flush(); os.fsync(raw.fileno())
    os.replace(temporary, destination)


def source_files(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*") if p.is_file() and "target" not in p.relative_to(root).parts and ".git" not in p.relative_to(root).parts)


def tree_manifest(root: Path) -> list[dict[str, Any]]:
    return [{"path": p.relative_to(root).as_posix(), "bytes": p.stat().st_size, "sha256": sha256_file(p)} for p in source_files(root)]


def candidate_patch() -> bytes:
    result = subprocess.run([
        "git", "diff", "--no-index", "--", str(BASELINE_SOURCE / "examples/koblitz_rank_fixture.rs"),
        str(CANDIDATE_SOURCE / "examples/koblitz_rank_fixture.rs")
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    require(result.returncode in (0, 1), f"candidate diff failed: {result.stderr.decode(errors='replace')}")
    return result.stdout.replace(str(BASELINE_SOURCE).encode(), b"a").replace(str(CANDIDATE_SOURCE).encode(), b"b")


def dependency_crates(lock_path: Path) -> tuple[list[tuple[Path, str]], list[dict[str, Any]]]:
    lock = tomllib.loads(lock_path.read_text()); cache_roots = sorted((Path.home() / ".cargo/registry/cache").glob("*"))
    archives, manifest = [], []
    for package in lock["package"]:
        if not str(package.get("source", "")).startswith("registry+"):
            continue
        filename = f"{package['name']}-{package['version']}.crate"
        matches = [root / filename for root in cache_roots if (root / filename).is_file()]
        require(len(matches) == 1, f"offline crate missing or ambiguous: {filename}")
        path = matches[0]; actual = sha256_file(path)
        require(package.get("checksum") == actual, f"crate checksum mismatch: {filename}")
        archives.append((path, f"crates/{filename}"))
        manifest.append({"name": package["name"], "version": package["version"], "sha256": actual, "bytes": path.stat().st_size, "archive": f"crates/{filename}"})
    return archives, manifest


def prepare() -> None:
    load_protocol()
    required = [BASELINE_SOURCE, CANDIDATE_SOURCE, BASELINE_DIRECT, BASELINE_RHO, CANDIDATE_DIRECT, ANALYZER_PATH,
                PACKAGE_ROOT / "source_snapshot.tar.gz", PACKAGE_ROOT / "source_origin.json", BASELINE_SOURCE / "Cargo.lock", CANDIDATE_SOURCE / "Cargo.lock"]
    for path in required:
        require(path.exists(), f"preparation input absent: {path}")
    require(sha256_file(PACKAGE_ROOT / "source_snapshot.tar.gz") == "2977cb02422409112a3454e5dac989515500f1e83d489df46cd324cd6fa4cf70", "archive hash mismatch")
    require(sha256_file(PACKAGE_ROOT / "source_origin.json") == "6884fe750094762b4389d53c4f4b64d537801d9be9d8cb4ac8d88e28a87e0632", "origin hash mismatch")
    require(sha256_file(PACKAGE_ROOT / "source_arm_snapshot.tar.gz") == "c8269bbdcb505b5f5e8f337a2acaad76424ec93a41ca3f076c36b0b6c6304c5b", "ARM source archive hash mismatch")
    require(sha256_file(PACKAGE_ROOT / "source_arm_origin.json") == "02f9ed2f247d05a03b2157e4677591f803b1b33454fcea4bff4c0d66e6507ff2", "ARM source origin hash mismatch")
    require(sha256_file(BASELINE_SOURCE / "Cargo.lock") == sha256_file(CANDIDATE_SOURCE / "Cargo.lock"), "candidate lock mismatch")
    baseline_tree, candidate_tree = tree_manifest(BASELINE_SOURCE), tree_manifest(CANDIDATE_SOURCE)
    left, right = {r["path"]: r for r in baseline_tree}, {r["path"]: r for r in candidate_tree}
    changed = sorted(p for p in set(left) | set(right) if left.get(p) != right.get(p))
    require(changed == ["examples/koblitz_rank_fixture.rs"], f"candidate changed files invalid: {changed}")
    patch = candidate_patch()
    require(b"HashMap::with_capacity(0)" in patch and b"PairMode::Full" in patch, "candidate patch wrong")
    CANDIDATE_PATCH_PATH.write_bytes(patch)
    normalized_tar([(p, f"source_arm_allocation/{p.relative_to(CANDIDATE_SOURCE).as_posix()}") for p in source_files(CANDIDATE_SOURCE)], CANDIDATE_TAR_PATH)
    CUSTODY_ROOT.mkdir(parents=True, exist_ok=True); shutil.copyfile(BASELINE_SOURCE / "Cargo.lock", CUSTODY_LOCK_PATH)
    normalized_tar([(BASELINE_DIRECT, "binaries/baseline/koblitz_rank_fixture"), (BASELINE_RHO, "binaries/baseline/koblitz_rho_fixture"), (CANDIDATE_DIRECT, "binaries/candidate/koblitz_rank_fixture")], BINARIES_TAR_PATH)
    crates, crate_manifest = dependency_crates(BASELINE_SOURCE / "Cargo.lock")
    normalized_tar(crates, DEPENDENCIES_TAR_PATH, {"dependency_manifest.json": json.dumps(crate_manifest, sort_keys=True, indent=2).encode() + b"\n"})
    atomic_json(CASE_MANIFEST_PATH, make_case_manifest())
    attempt3_valid = False
    if (ATTEMPT3_ROOT / "summary.json").is_file():
        attempt3_valid = json.loads((ATTEMPT3_ROOT / "summary.json").read_text()).get("valid") is True
    source_closure = {
        "schema": "crypto.autoresearch.cold_single_ic_source_closure.v2", "experiment_id": EXPERIMENT_ID,
        "created_at": utc_now(), "protocol_sha256": PROTOCOL_SHA256,
        "fairness_status": "common_arm_arithmetic_applied_equally; attempt3 valid; pending committed measurement admission" if attempt3_valid else "common_arm_arithmetic_applied_equally; pending committed admission and attempt3",
        "science_admissible": False,
        "common_arm_port": {"patch": "research/cold_single_ic_20260921/common_arm_port.patch", "origin": "research/cold_single_ic_20260921/source_arm_origin.json"},
        "baseline_archive": {"sha256": sha256_file(PACKAGE_ROOT / "source_snapshot.tar.gz")},
        "origin_record": {"sha256": sha256_file(PACKAGE_ROOT / "source_origin.json")},
        "arm_source_archive": {"sha256": sha256_file(PACKAGE_ROOT / "source_arm_snapshot.tar.gz")},
        "arm_source_origin": {"sha256": sha256_file(PACKAGE_ROOT / "source_arm_origin.json")},
        "common_arm_port_patch_sha256": sha256_file(PACKAGE_ROOT / "common_arm_port.patch"),
        "baseline_source": {"files": len(baseline_tree), "bytes": sum(r["bytes"] for r in baseline_tree), "tree_digest": digest_value(baseline_tree)},
        "candidate_source": {"files": len(candidate_tree), "bytes": sum(r["bytes"] for r in candidate_tree), "tree_digest": digest_value(candidate_tree)},
        "candidate_changed_paths": changed, "candidate_patch_sha256": sha256_file(CANDIDATE_PATCH_PATH),
        "candidate_source_tar_sha256": sha256_file(CANDIDATE_TAR_PATH), "cargo_lock_sha256": sha256_file(CUSTODY_LOCK_PATH),
        "dependency_count": len(crate_manifest), "dependencies_tar_sha256": sha256_file(DEPENDENCIES_TAR_PATH),
        "binary_sha256": {"baseline_direct": sha256_file(BASELINE_DIRECT), "baseline_rho": sha256_file(BASELINE_RHO), "candidate_direct": sha256_file(CANDIDATE_DIRECT)},
        "binaries_tar_sha256": sha256_file(BINARIES_TAR_PATH),
        "source_sha256": {
            "baseline_direct": sha256_file(BASELINE_SOURCE / "examples/koblitz_rank_fixture.rs"),
            "baseline_rho": sha256_file(BASELINE_SOURCE / "examples/koblitz_rho_fixture.rs"),
            "candidate_direct": sha256_file(CANDIDATE_SOURCE / "examples/koblitz_rank_fixture.rs"),
        },
        "candidate_build": {
            "build_argv": ["cargo", "build", "--offline", "--locked", "--release", "--jobs", "2", "--example", "koblitz_rank_fixture", "--example", "koblitz_rho_fixture"],
            "test_argv": ["cargo", "test", "--offline", "--locked", "--release", "--jobs", "2", "--example", "koblitz_rank_fixture", "--example", "koblitz_rho_fixture"],
            "build_exit_code": 0, "test_exit_code": 0,
            "rank_tests_passed": 10, "rho_tests_passed": 3, "failed": 0,
            "target_directory": str(CANDIDATE_BUILD.parents[1]),
        },
    }
    atomic_json(SOURCE_CLOSURE_PATH, source_closure)
    command_receipts = {}
    for name, command in {"rustc": ["rustc", "--version", "--verbose"], "cargo": ["cargo", "--version", "--verbose"], "uname": ["uname", "-a"], "sw_vers": ["sw_vers"]}.items():
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, text=True)
        command_receipts[name] = {"argv": command, "exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr}
    atomic_json(BUILD_TOOLCHAIN_PATH, {
        "schema": "crypto.autoresearch.build_toolchain.v2", "created_at": utc_now(),
        "host": {"platform": platform.platform(), "machine": platform.machine(), "python": sys.version},
        "commands": command_receipts, "arm_build_receipt_sha256": sha256_file(PACKAGE_ROOT / "arm_build" / "receipt.json"),
        "arm_verification_sha256": sha256_file(PACKAGE_ROOT / "arm_build" / "verification.json"),
        "candidate_build": source_closure["candidate_build"],
        "scope": "toolchain and build custody; no scientific process",
    })
    atomic_json(PREFLIGHT_PATH, {
        "schema": "crypto.autoresearch.cold_single_ic_runner_preflight.v2", "created_at": utc_now(),
        "experiment_id": EXPERIMENT_ID, "protocol_sha256": PROTOCOL_SHA256,
        "runner_sha256": sha256_file(Path(__file__).resolve()), "analyze_sha256": sha256_file(ANALYZER_PATH),
        "case_manifest_sha256": sha256_file(CASE_MANIFEST_PATH), "source_closure_sha256": sha256_file(SOURCE_CLOSURE_PATH),
        "candidate_patch_sha256": sha256_file(CANDIDATE_PATCH_PATH), "candidate_source_tar_sha256": sha256_file(CANDIDATE_TAR_PATH),
        "build_toolchain_sha256": sha256_file(BUILD_TOOLCHAIN_PATH),
        "custody": {"binaries_tar_sha256": sha256_file(BINARIES_TAR_PATH), "cargo_lock_sha256": sha256_file(CUSTODY_LOCK_PATH), "dependencies_tar_sha256": sha256_file(DEPENDENCIES_TAR_PATH)},
        "binary_sha256": source_closure["binary_sha256"], "source_sha256": source_closure["source_sha256"],
        "admission_state": "REFUSED_PENDING_COMMITTED_ATTEMPT3_AND_MEASUREMENT_ADMISSION",
        "model_resolution": {"requested_policy": "executor-implementation", "resolved_model_id": "gpt-5.6-sol", "reasoning_effort": "high", "model_verified": False, "note": "static adapter resolution only; not a serving-model probe"},
    })


def validate_preserved_conformance() -> None:
    paths = {"baseline_ic": PRESERVED_ATTEMPT2 / "baseline_ic.stdout", "allocation_ic": PRESERVED_ATTEMPT2 / "allocation_ic.stdout", "rho": PRESERVED_ATTEMPT2 / "rho.stdout"}
    for path in paths.values(): require(path.is_file(), f"preserved output absent: {path}")
    parsed = {
        "baseline_ic": parse_direct_output(paths["baseline_ic"].read_bytes(), expected_scalar=17, expected_n=13, expected_k=1),
        "allocation_ic": parse_direct_output(paths["allocation_ic"].read_bytes(), expected_scalar=17, expected_n=13, expected_k=1),
        "rho": parse_rho_output(paths["rho"].read_bytes(), expected_scalar=17, expected_n=13),
    }
    mismatches = direct_equivalence(parsed["baseline_ic"], parsed["allocation_ic"])
    require(not mismatches, f"preserved direct mismatch: {json.dumps(mismatches, sort_keys=True)}")
    require(parsed["baseline_ic"]["published_q"] == parsed["rho"]["published_q"], "direct/rho points differ")
    write_once_json(PRESERVED_VALIDATION_PATH, {
        "schema": "crypto.autoresearch.preserved_conformance_validation.v1", "created_at": utc_now(),
        "method": "static parse of preserved attempt-2 stdout; no process launched",
        "source_stdout_sha256": {name: sha256_file(path) for name, path in paths.items()},
        "expected": {"n": 13, "a": 0, "eta": "1/2", "numeric_seed": 13001, "explicit_public_scalar": 17},
        "valid": True, "direct_equivalence_mismatches": {}, "parsed": parsed,
        "prior_checker_records_preserved": ["baseline_ic.json", "allocation_ic.json"], "rho_prior_exit_receipt_absent": True,
        "science_effect": "none; attempt 3 and all scientific processes remain refused",
    })


def conformance_attempt3() -> None:
    """Run the three Coordinator-admitted untimed controls exactly once."""
    require(not ATTEMPT3_ROOT.exists(), f"immutable attempt-3 root already exists: {ATTEMPT3_ROOT}")
    admission = PACKAGE_ROOT / "conformance_attempt3_admission.json"
    amendment = PACKAGE_ROOT / "hardware_fairness_amendment.json"
    verification = PACKAGE_ROOT / "arm_build" / "verification.json"
    path_resolution = PACKAGE_ROOT / "conformance_path_resolution.json"
    for path in (admission, amendment, verification, path_resolution):
        require(path.is_file() and git_blob_matches_head(path), f"attempt-3 prerequisite is not committed: {path}")
    admission_record = json.loads(admission.read_text())
    amendment_record = json.loads(amendment.read_text())
    verification_record = json.loads(verification.read_text())
    resolution_record = json.loads(path_resolution.read_text())
    require(admission_record.get("status") == "approved_prospective", "attempt-3 admission is not approved")
    require(amendment_record.get("status") == "approved_prospective", "hardware amendment is not approved")
    require(verification_record.get("status") == "passed", "common ARM verification did not pass")
    require(resolution_record.get("canonical_directory") == "research/cold_single_ic_20260921/artifacts/RUN-KIC-e3dbed/conformance/attempt3", "attempt-3 path resolution mismatch")
    require(sha256_file(BASELINE_DIRECT) == verification_record["binaries"]["koblitz_rank_fixture"]["sha256"], "baseline direct binary differs from ARM verification")
    require(sha256_file(BASELINE_RHO) == verification_record["binaries"]["koblitz_rho_fixture"]["sha256"], "rho binary differs from ARM verification")
    require(CANDIDATE_DIRECT.is_file(), "candidate direct binary absent")
    ATTEMPT3_ROOT.mkdir(parents=True)
    cases = (
        ("baseline_ic", BASELINE_DIRECT, ["13", "0", "1", "2", "13001", "signed_expanded", "independent", "pair_pair_parallel_4096", "1", "17"], True),
        ("allocation_ic", CANDIDATE_DIRECT, ["13", "0", "1", "2", "13001", "signed_expanded", "independent", "pair_pair_parallel_4096", "1", "17"], True),
        ("rho", BASELINE_RHO, ["13", "0", "signed_frobenius", "1", "packed", "13001", "17"], False),
    )
    receipts = {}
    for case_id, binary, argv, direct in cases:
        case_root = ATTEMPT3_ROOT / case_id
        case_root.mkdir()
        cwd = case_root / "cwd"; cwd.mkdir()
        stdout_path = case_root / "stdout.jsonl"; stderr_path = case_root / "stderr.txt"
        environment = clean_environment(cwd, direct)
        with stdout_path.open("xb") as stdout, stderr_path.open("xb") as stderr:
            try:
                process = subprocess.Popen([str(binary), *argv], cwd=cwd, env=environment, stdin=subprocess.DEVNULL,
                                           stdout=stdout, stderr=stderr, start_new_session=True, close_fds=True)
                _, status, _usage = os.wait4(process.pid, 0)
                process.returncode = os.waitstatus_to_exitcode(status)
                popen_error = None
            except Exception as exc:
                status = None
                popen_error = f"{type(exc).__name__}: {exc}"
            stdout.flush(); stderr.flush(); os.fsync(stdout.fileno()); os.fsync(stderr.fileno())
        exit_code = os.waitstatus_to_exitcode(status) if status is not None else None
        parsed = None; validation_error = popen_error
        if popen_error is None and exit_code == 0:
            try:
                parsed = (
                    parse_direct_output(stdout_path.read_bytes(), expected_scalar=17, expected_n=13, expected_k=1,
                                        expected_arithmetic_backend="aarch64_pmull")
                    if direct else
                    parse_rho_output(stdout_path.read_bytes(), expected_scalar=17, expected_n=13,
                                     expected_arithmetic_backend="aarch64_pmull")
                )
            except Exception as exc:
                validation_error = f"{type(exc).__name__}: {exc}"
        elif popen_error is None:
            validation_error = f"child exited {exit_code}"
        valid = exit_code == 0 and parsed is not None
        receipt = {
            "schema": "crypto.autoresearch.cold_single_ic_conformance_receipt.v1",
            "case_id": case_id, "phase": "untimed_conformance_attempt3",
            "argv": [str(binary), *argv], "binary_sha256": sha256_file(binary),
            "cwd": str(cwd), "environment": environment, "exit_code": exit_code,
            "stdout_sha256": sha256_file(stdout_path), "stderr_sha256": sha256_file(stderr_path),
            "parsed_receipt": parsed, "valid": valid, "validation_error": validation_error,
            "timing_cpu_rss_not_retained": True,
        }
        write_once_json(case_root / "receipt.json", receipt)
        receipts[case_id] = receipt
        require(valid, f"attempt-3 {case_id} failed: {validation_error}")
    mismatches = direct_equivalence(receipts["baseline_ic"]["parsed_receipt"], receipts["allocation_ic"]["parsed_receipt"])
    require(not mismatches, f"attempt-3 direct equivalence mismatch: {json.dumps(mismatches, sort_keys=True)}")
    require(receipts["baseline_ic"]["parsed_receipt"]["published_q"] == receipts["rho"]["parsed_receipt"]["published_q"], "attempt-3 direct/rho point mismatch")
    write_once_json(ATTEMPT3_ROOT / "summary.json", {
        "schema": "crypto.autoresearch.cold_single_ic_conformance_summary.v1",
        "experiment_id": EXPERIMENT_ID, "attempt": 3, "valid": True,
        "children": 3, "logical_cases": 3, "serial": True,
        "timing_cpu_rss_not_retained": True, "direct_equivalence_mismatches": {},
        "backend": "aarch64_pmull", "receipts": {name: f"{name}/receipt.json" for name in receipts},
        "hardware_fairness_amendment_sha256": sha256_file(amendment),
        "conformance_admission_sha256": sha256_file(admission),
        "arm_verification_sha256": sha256_file(verification),
        "path_resolution_sha256": sha256_file(path_resolution),
        "scientific_children_executed": 0,
    })


def validate_attempt3_final_parser() -> None:
    """Additively bind the final parser to immutable attempt-3 stdout bytes."""
    summary = ATTEMPT3_ROOT / "summary.json"
    require(summary.is_file() and json.loads(summary.read_text()).get("valid") is True, "valid attempt-3 summary absent")
    paths = {
        "baseline_ic": ATTEMPT3_ROOT / "baseline_ic" / "stdout.jsonl",
        "allocation_ic": ATTEMPT3_ROOT / "allocation_ic" / "stdout.jsonl",
        "rho": ATTEMPT3_ROOT / "rho" / "stdout.jsonl",
    }
    parsed = {
        "baseline_ic": parse_direct_output(paths["baseline_ic"].read_bytes(), expected_scalar=17, expected_n=13,
                                           expected_k=1, expected_arithmetic_backend="aarch64_pmull"),
        "allocation_ic": parse_direct_output(paths["allocation_ic"].read_bytes(), expected_scalar=17, expected_n=13,
                                             expected_k=1, expected_arithmetic_backend="aarch64_pmull"),
        "rho": parse_rho_output(paths["rho"].read_bytes(), expected_scalar=17, expected_n=13,
                                expected_arithmetic_backend="aarch64_pmull"),
    }
    mismatches = direct_equivalence(parsed["baseline_ic"], parsed["allocation_ic"])
    require(not mismatches, f"final parser direct mismatch: {json.dumps(mismatches, sort_keys=True)}")
    require(parsed["baseline_ic"]["published_q"] == parsed["rho"]["published_q"], "final parser direct/rho point mismatch")
    write_once_json(ATTEMPT3_FINAL_VALIDATION_PATH, {
        "schema": "crypto.autoresearch.cold_single_ic_final_parser_validation.v1",
        "method": "static reparse of immutable attempt-3 stdout; no process launched",
        "runner_sha256": sha256_file(Path(__file__).resolve()),
        "stdout_sha256": {name: sha256_file(path) for name, path in paths.items()},
        "valid": True, "direct_equivalence_mismatches": {}, "parsed": parsed,
        "science_effect": "none; all 96 scientific children remain held pending committed measurement admission",
    })


class DarwinMemorySampler:
    class RusageInfoV2(ctypes.Structure):
        _fields_ = [("ri_uuid", ctypes.c_ubyte * 16)] + [(name, ctypes.c_uint64) for name in (
            "ri_user_time", "ri_system_time", "ri_pkg_idle_wkups", "ri_interrupt_wkups", "ri_pageins",
            "ri_wired_size", "ri_resident_size", "ri_phys_footprint", "ri_proc_start_abstime",
            "ri_proc_exit_abstime", "ri_child_user_time", "ri_child_system_time", "ri_child_pkg_idle_wkups",
            "ri_child_interrupt_wkups", "ri_child_pageins", "ri_child_elapsed_abstime",
            "ri_diskio_bytesread", "ri_diskio_byteswritten")]

    def __init__(self) -> None:
        self.method, self.detail, self.function = "unavailable", None, None
        if platform.system() != "Darwin":
            self.detail = "Darwin-only proc_pid_rusage sampler"; return
        try:
            function = ctypes.CDLL("/usr/lib/libproc.dylib", use_errno=True).proc_pid_rusage
            function.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_void_p]; function.restype = ctypes.c_int
            self.function = function; self.method = "proc_pid_rusage.RUSAGE_INFO_V2.ri_phys_footprint_sampled"
        except Exception as exc:
            self.detail = repr(exc)

    def sample(self, pid: int) -> int | None:
        if self.function is None: return None
        info = self.RusageInfoV2()
        if self.function(pid, 2, ctypes.byref(info)) != 0:
            self.detail = f"proc_pid_rusage errno={ctypes.get_errno()}"; return None
        return int(info.ri_phys_footprint)


def clean_environment(work: Path, direct: bool) -> dict[str, str]:
    temporary, home = work / "tmp", work / "home"; temporary.mkdir(); home.mkdir()
    environment = {"PATH": os.defpath, "HOME": str(home), "TMPDIR": str(temporary), "LANG": "C", "LC_ALL": "C"}
    environment.update(DIRECT_ENV if direct else RHO_ENV); return environment


def case_command(case: dict[str, Any], selected_denominator: int | None = None) -> tuple[Path, list[str], bool, int | None]:
    scalar, seed = case["scalar"], case["seed"]
    if case["solver"] == "direct":
        denominator = case.get("eta_denominator", selected_denominator); require(denominator in EXPECTED_K, "direct denominator absent")
        binary = BASELINE_DIRECT if case["source"] == "baseline" else CANDIDATE_DIRECT
        return binary, [str(N), "0", "1", str(denominator), str(seed), "signed_expanded", "independent", "pair_pair_parallel_4096", "1", str(scalar)], True, denominator
    require(case["solver"] == "rho", f"unknown solver {case['solver']!r}")
    return BASELINE_RHO, [str(N), "0", "signed_frobenius", "1", "packed", str(seed), str(scalar)], False, None


def kill_process_group(process: subprocess.Popen[Any]) -> None:
    try: os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError: pass


def run_scientific_child(case: dict[str, Any], selected_denominator: int | None) -> dict[str, Any]:
    process_dir = RAW_ROOT / f"{case['ordinal']:03d}_{case['id']}"; require(not process_dir.exists(), f"cwd exists: {process_dir}")
    process_dir.mkdir(parents=True); work = process_dir / "cwd"; work.mkdir()
    stdout_path, stderr_path = process_dir / "stdout.jsonl", process_dir / "stderr.txt"
    binary, argv, direct, denominator = case_command(case, selected_denominator); require(binary.is_file(), f"binary absent: {binary}")
    environment = clean_environment(work, direct); sampler = DarwinMemorySampler()
    started_at, start_ns = utc_now(), time.monotonic_ns(); status = usage = reaped_ns = None
    timeout_reached = memory_cap_reached = False; sampled_peak = None; sample_count = 0
    popen_error = None; last_memory_sample_ns = 0
    with stdout_path.open("xb") as stdout, stderr_path.open("xb") as stderr:
        try:
            process = subprocess.Popen([str(binary), *argv], cwd=work, env=environment, stdin=subprocess.DEVNULL,
                                       stdout=stdout, stderr=stderr, start_new_session=True, close_fds=True)
        except Exception as exc:
            popen_error = f"{type(exc).__name__}: {exc}"
        if popen_error is None:
            while True:
                waited_pid, waited_status, waited_usage = os.wait4(process.pid, os.WNOHANG)
                if waited_pid == process.pid:
                    status, usage, reaped_ns = waited_status, waited_usage, time.monotonic_ns()
                    break
                now_ns = time.monotonic_ns()
                if now_ns - last_memory_sample_ns >= 50_000_000:
                    current = sampler.sample(process.pid); last_memory_sample_ns = now_ns
                    if current is not None:
                        sample_count += 1; sampled_peak = current if sampled_peak is None else max(sampled_peak, current)
                        if current >= MEMORY_LIMIT_BYTES: memory_cap_reached = True; kill_process_group(process)
                if (now_ns - start_ns) / 1e9 >= WATCHDOG_SECONDS: timeout_reached = True; kill_process_group(process)
                if timeout_reached or memory_cap_reached:
                    _, status, usage = os.wait4(process.pid, 0); reaped_ns = time.monotonic_ns(); break
                time.sleep(0.001)
            process.returncode = os.waitstatus_to_exitcode(status)
        else:
            reaped_ns = time.monotonic_ns()
        stdout.flush(); stderr.flush(); os.fsync(stdout.fileno()); os.fsync(stderr.fileno())
    durable_ns, ended_at = time.monotonic_ns(), utc_now()
    unexpected_files = sorted(p.relative_to(work).as_posix() for p in work.rglob("*") if p.is_file() and not p.relative_to(work).as_posix().startswith(("home/", "tmp/")))
    exit_code = os.waitstatus_to_exitcode(status) if status is not None else None
    parsed = None; validation_error = popen_error; unexpected = bool(unexpected_files)
    terminal_state = "completed_valid"
    if popen_error is not None: terminal_state = "failed_infrastructure"
    elif timeout_reached or memory_cap_reached: terminal_state = "resource_exhaustion"
    elif exit_code != 0: terminal_state = "failed_implementation"
    else:
        try:
            parsed = parse_direct_output(stdout_path.read_bytes(), expected_scalar=case["scalar"], expected_n=N,
                                         expected_k=EXPECTED_K[denominator], expected_arithmetic_backend="aarch64_pmull") if direct else parse_rho_output(
                                             stdout_path.read_bytes(), expected_scalar=case["scalar"], expected_n=N,
                                             expected_arithmetic_backend="aarch64_pmull")
        except ValidationError as exc:
            validation_error, unexpected, terminal_state = str(exc), unexpected or exc.unexpected, "completed_invalid"
        except Exception as exc:
            validation_error, terminal_state = f"parser {type(exc).__name__}: {exc}", "failed_implementation"
    if unexpected_files: validation_error, terminal_state = f"unexpected cwd state: {unexpected_files}", "completed_invalid"
    return {
        "schema": "crypto.autoresearch.cold_single_ic_process_receipt.v1", "experiment_id": EXPERIMENT_ID, "task_id": TASK_ID,
        "ordinal": case["ordinal"], "case_id": case["id"], "phase": case["phase"], "scalar_index": case["scalar_index"],
        "scalar": case["scalar"], "solver": case["solver"], "configuration": case.get("configuration"), "source": case["source"],
        "eta_denominator": denominator, "factor_base_k": EXPECTED_K.get(denominator), "seed_label": case["seed_label"], "seed": case["seed"],
        "argv": [str(binary), *argv], "binary_sha256": sha256_file(binary), "cwd": str(work), "environment": environment,
        "started_at": started_at, "ended_at": ended_at,
        "wall_monotonic_ns": reaped_ns - start_ns, "wall_seconds": (reaped_ns - start_ns) / 1e9,
        "parent_output_durability_seconds": (durable_ns - reaped_ns) / 1e9,
        "reap_poll_interval_seconds": 0.001, "memory_sample_interval_seconds": 0.05,
        "observed_reap_envelope_seconds": 0.001,
        "user_cpu_seconds": usage.ru_utime if usage is not None else None,
        "system_cpu_seconds": usage.ru_stime if usage is not None else None,
        "wait4_ru_maxrss": usage.ru_maxrss if usage is not None else None,
        "wait4_ru_maxrss_unit": "bytes" if platform.system() == "Darwin" else "platform-dependent",
        "resource_collection": "os.wait4 per PID; Popen.poll unused",
        "memory_sampling": {"method": sampler.method, "detail": sampler.detail, "sample_count": sample_count, "sampled_peak_bytes": sampled_peak,
                            "limit_bytes": MEMORY_LIMIT_BYTES, "cooperative_cap_enforced": sample_count > 0, "cap_reached": memory_cap_reached},
        "watchdog_seconds": WATCHDOG_SECONDS, "watchdog_reached": timeout_reached, "exit_code": exit_code,
        "terminal_state": terminal_state, "valid": terminal_state == "completed_valid", "validation_error": validation_error,
        "unexpected_stop_condition": unexpected, "retained_state_detected": bool(unexpected_files),
        "stdout_path": stdout_path.relative_to(RUN_ROOT).as_posix(), "stdout_sha256": sha256_file(stdout_path),
        "stderr_path": stderr_path.relative_to(RUN_ROOT).as_posix(), "stderr_sha256": sha256_file(stderr_path), "parsed_receipt": parsed,
    }


def git_blob_matches_head(path: Path) -> bool:
    relative = path.relative_to(REPO_ROOT).as_posix()
    result = subprocess.run(["git", "show", f"HEAD:{relative}"], cwd=REPO_ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    return result.returncode == 0 and result.stdout == path.read_bytes()


def verify_measurement_admission() -> dict[str, Any]:
    require(ADMISSION_PATH.is_file() and git_blob_matches_head(ADMISSION_PATH), "REFUSED: committed admission absent")
    admission = json.loads(ADMISSION_PATH.read_text())
    required = {"schema": "crypto.autoresearch.measurement_admission.v2", "status": "admitted", "approved_by_role": "coordinator",
                "experiment_id": EXPERIMENT_ID, "task_id": TASK_ID, "protocol_sha256": PROTOCOL_SHA256,
                "runner_sha256": sha256_file(Path(__file__).resolve()), "analyze_sha256": sha256_file(ANALYZER_PATH),
                "case_manifest_sha256": sha256_file(CASE_MANIFEST_PATH), "runner_preflight_sha256": sha256_file(PREFLIGHT_PATH)}
    for key, expected in required.items(): require(admission.get(key) == expected, f"REFUSED: admission {key} mismatch")
    binaries = {"baseline_direct": sha256_file(BASELINE_DIRECT), "baseline_rho": sha256_file(BASELINE_RHO), "candidate_direct": sha256_file(CANDIDATE_DIRECT)}
    sources = {"baseline_direct": sha256_file(BASELINE_SOURCE / "examples/koblitz_rank_fixture.rs"), "baseline_rho": sha256_file(BASELINE_SOURCE / "examples/koblitz_rho_fixture.rs"), "candidate_direct": sha256_file(CANDIDATE_SOURCE / "examples/koblitz_rank_fixture.rs")}
    require(admission.get("binary_sha256") == binaries and admission.get("source_sha256") == sources, "REFUSED: source/binary hashes mismatch")
    fairness = admission.get("equal_arm_arithmetic_fairness_amendment"); require(isinstance(fairness, dict), "REFUSED: fairness amendment absent")
    amendment_path = REPO_ROOT / str(fairness.get("path", ""))
    require(amendment_path.is_file() and git_blob_matches_head(amendment_path) and fairness.get("sha256") == sha256_file(amendment_path), "REFUSED: fairness amendment not committed/bound")
    require(fairness.get("applied_equally_to") == ["baseline_direct", "candidate_direct", "baseline_rho"], "REFUSED: fairness not equal")
    attempt = admission.get("attempt3_conformance", {}); attempt_path = REPO_ROOT / str(attempt.get("path", ""))
    require(attempt.get("valid") is True and attempt_path.is_file() and git_blob_matches_head(attempt_path) and attempt.get("sha256") == sha256_file(attempt_path), "REFUSED: committed attempt3 absent")
    return admission


def load_processes() -> list[dict[str, Any]]:
    if not PROCESSES_PATH.exists(): return []
    return [json.loads(line) for line in PROCESSES_PATH.read_text().splitlines() if line]


def select_calibration(rows: list[dict[str, Any]]) -> dict[str, Any]:
    require(len(rows) == 48 and all(r["phase"] == "calibration" for r in rows), "selection needs 48 calibration rows")
    equivalence = []
    for index in range(1, 13):
        baseline = next(r for r in rows if r["scalar_index"] == index and r["configuration"] == "baseline_unmodified_eta_1_128")
        candidate = next(r for r in rows if r["scalar_index"] == index and r["configuration"] == "allocation_only_eta_1_128")
        require(baseline["valid"] and candidate["valid"], f"invalid equivalence control {index}")
        mismatches = direct_equivalence(baseline["parsed_receipt"], candidate["parsed_receipt"]); equivalence.append({"scalar_index": index, "mismatches": mismatches})
        require(not mismatches, f"equivalence mismatch {index}: {json.dumps(mismatches, sort_keys=True)}", unexpected=True)
    medians = {}
    for configuration, _, _ in CALIBRATION_CONFIGS[1:]:
        selected = [r for r in rows if r["configuration"] == configuration]
        require(len(selected) == 12 and all(r["valid"] for r in selected), f"{configuration} lacks 12 valid rows")
        medians[configuration] = statistics.median(r["wall_seconds"] for r in selected)
    order = {name: i for i, (name, _, _) in enumerate(CALIBRATION_CONFIGS[1:])}
    winner = min(medians, key=lambda name: (medians[name], order[name])); denominator = next(d for name, _, d in CALIBRATION_CONFIGS if name == winner)
    return {"schema": "crypto.autoresearch.cold_single_ic_calibration_selection.v1", "created_at": utc_now(), "experiment_id": EXPERIMENT_ID,
            "input_processes_prefix_digest": digest_value(rows), "equivalence_gate": {"passed": True, "pairs": equivalence},
            "candidate_median_wall_seconds": medians, "selection_rule": "smallest median; exact ties choose listed smaller denominator",
            "winner_configuration": winner, "winner_eta_denominator": denominator, "winner_factor_base_k": EXPECTED_K[denominator], "calibration_is_not_performance_claim": True}


def scientific() -> None:
    load_protocol(); verify_measurement_admission(); manifest = json.loads(CASE_MANIFEST_PATH.read_text())
    cases = manifest["calibration"] + manifest["heldout"]; require(len(cases) == 96, "manifest count not 96")
    existing = load_processes(); require(len(existing) <= 96, "receipt count exceeds cap")
    for index, row in enumerate(existing):
        require((row.get("ordinal"), row.get("case_id")) == (cases[index]["ordinal"], cases[index]["id"]), "receipts not exact prefix")
        require(row.get("unexpected_stop_condition") is not True, f"REFUSED: prior unexpected stop condition at {row.get('case_id')}")
    selected_denominator = None
    if len(existing) >= 48:
        if not CALIBRATION_SELECTION_PATH.exists(): write_once_json(CALIBRATION_SELECTION_PATH, select_calibration(existing[:48]))
        selected_denominator = json.loads(CALIBRATION_SELECTION_PATH.read_text())["winner_eta_denominator"]
    for case in cases[len(existing):]:
        if case["phase"] == "heldout" and selected_denominator is None:
            selection = select_calibration(load_processes()[:48]); write_once_json(CALIBRATION_SELECTION_PATH, selection); selected_denominator = selection["winner_eta_denominator"]
        receipt = run_scientific_child(case, selected_denominator); append_jsonl(PROCESSES_PATH, receipt)
        if receipt["unexpected_stop_condition"]: raise RuntimeError(f"unexpected observation at {case['id']}: {receipt['validation_error']}")
        if case["phase"] == "calibration" and case["ordinal"] == 48:
            selection = select_calibration(load_processes()); write_once_json(CALIBRATION_SELECTION_PATH, selection); selected_denominator = selection["winner_eta_denominator"]
    require(len(load_processes()) == 96, "schedule did not reach 96 terminal rows")
    analysis = subprocess.run([sys.executable, str(ANALYZER_PATH)], cwd=RUN_ROOT, check=False)
    require(analysis.returncode == 0, f"analysis program exited {analysis.returncode}")
    finalize()


def finalize() -> None:
    rows = load_processes()
    require(len(rows) == 96, "finalization requires 96 process receipts")
    for required in (RUN_ROOT / "analysis.json", RUN_ROOT / "analysis.md", CALIBRATION_SELECTION_PATH):
        require(required.is_file(), f"finalization input absent: {required}")
    raw_files = sorted(path for path in RAW_ROOT.rglob("*") if path.is_file())
    require(bool(raw_files), "raw process directory is empty")
    raw_manifest = {
        "schema": "crypto.autoresearch.raw_processes_manifest.v1",
        "experiment_id": EXPERIMENT_ID,
        "files": [{"path": path.relative_to(RUN_ROOT).as_posix(), "bytes": path.stat().st_size, "sha256": sha256_file(path)} for path in raw_files],
    }
    raw_manifest["tree_digest"] = digest_value(raw_manifest["files"])
    atomic_json(RAW_MANIFEST_PATH, raw_manifest)
    normalized_tar([(path, path.relative_to(RUN_ROOT).as_posix()) for path in raw_files], RAW_TAR_PATH)
    git_head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, stdout=subprocess.PIPE, text=True, check=True).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain", "--", str(PACKAGE_ROOT.relative_to(REPO_ROOT))], cwd=REPO_ROOT, stdout=subprocess.PIPE, text=True, check=True).stdout.splitlines()
    atomic_json(ENVIRONMENT_PATH, {
        "schema": "crypto.autoresearch.cold_single_ic_environment.v1",
        "experiment_id": EXPERIMENT_ID,
        "git_head": git_head,
        "scoped_dirty_paths": dirty,
        "platform": platform.platform(), "machine": platform.machine(), "python": sys.version,
        "direct_child_environment": {"PATH": os.defpath, "HOME": "<fresh-case-cwd>/home", "TMPDIR": "<fresh-case-cwd>/tmp", "LANG": "C", "LC_ALL": "C", **DIRECT_ENV},
        "rho_child_environment": {"PATH": os.defpath, "HOME": "<fresh-case-cwd>/home", "TMPDIR": "<fresh-case-cwd>/tmp", "LANG": "C", "LC_ALL": "C", **RHO_ENV},
        "environment_capture": "explicit whitelist template only; parent os.environ was not dumped",
    })
    terminal_counts: dict[str, int] = {}
    for row in rows:
        terminal_counts[row["terminal_state"]] = terminal_counts.get(row["terminal_state"], 0) + 1
    anomalies = [
        {"case_id": row["case_id"], "terminal_state": row["terminal_state"], "validation_error": row.get("validation_error")}
        for row in rows if not row["valid"] or row.get("unexpected_stop_condition")
    ]
    atomic_json(EXECUTION_RECEIPT_PATH, {
        "execution_report": {
            "experiment_id": EXPERIMENT_ID,
            "task_id": TASK_ID,
            "implementation_commit": git_head,
            "protocol_sha256": PROTOCOL_SHA256,
            "protocol_deviations": [],
            "runs": {"terminal_counts": terminal_counts, "completed": [row["case_id"] for row in rows if row["valid"]],
                     "invalid": [row["case_id"] for row in rows if row["terminal_state"] == "completed_invalid"],
                     "failed": [row["case_id"] for row in rows if row["terminal_state"].startswith("failed_") or row["terminal_state"] == "resource_exhaustion"]},
            "observations": [{"analysis": "analysis.json", "frozen_prediction_reference": "protocol.json#measurement_and_analysis"}],
            "anomalies": anomalies,
            "artifact_paths": ["processes.jsonl", "raw_processes.tar.gz", "raw_processes_manifest.json", "analysis.json", "analysis.md"],
            "executor_assessment": {"protocol_complete": len(rows) == 96, "data_quality": "good" if not anomalies else "limited", "requires_rerun": False},
            "claim_boundary": "executor observations only; no scientific interpretation or status transition",
        }
    })
    declared = [
        "runner.py", "analyze.py", "source_closure.json", "candidate.patch", "candidate_source.tar.gz",
        "build_toolchain.json", "runner_preflight.json", "case_manifest.json", "processes.jsonl",
        "raw_processes.tar.gz", "calibration_selection.json", "analysis.json", "analysis.md",
        "environment.json", "execution_receipt.json", "custody/binaries.tar.gz", "custody/Cargo.lock",
        "custody/dependencies.tar.gz", "raw_processes_manifest.json",
        "preserved_implementation_attempt1/runner.py", "preserved_implementation_attempt1/analyze.py",
        "preserved_implementation_attempt1/preservation.json",
    ]
    missing = [name for name in declared if not (RUN_ROOT / name).is_file()]
    require(not missing, f"declared artifacts absent: {missing}")
    atomic_json(ARTIFACT_MANIFEST_PATH, {
        "schema": "crypto.autoresearch.artifact_manifest.v1", "experiment_id": EXPERIMENT_ID,
        "self_hash_omitted": True,
        "artifacts": [{"path": name, "bytes": (RUN_ROOT / name).stat().st_size, "sha256": sha256_file(RUN_ROOT / name)} for name in declared],
    })


def self_test() -> None:
    require({d: compute_k(N, d, SUBGROUP_ORDER) for d in EXPECTED_K} == EXPECTED_K, "K failed")
    baseline = parse_direct_output((PRESERVED_ATTEMPT2 / "baseline_ic.stdout").read_bytes(), expected_scalar=17, expected_n=13, expected_k=1)
    candidate = parse_direct_output((PRESERVED_ATTEMPT2 / "allocation_ic.stdout").read_bytes(), expected_scalar=17, expected_n=13, expected_k=1)
    # Old rho lacks new ARM backend tags; validate its pre-amendment schema explicitly.
    old = json.loads((PRESERVED_ATTEMPT2 / "rho.stdout").read_text())
    old.setdefault("field_multiplication_backend", None); old.setdefault("field_squaring_backend", None)
    rho = parse_rho_output((json.dumps(old) + "\n").encode(), expected_scalar=17, expected_n=13)
    require(not direct_equivalence(baseline, candidate), "direct equivalence failed")
    require(baseline["published_q"] == rho["published_q"], "point mismatch")
    manifest = make_case_manifest()
    require([r["configuration"] for r in manifest["calibration"][:4]] == [r[0] for r in CALIBRATION_CONFIGS], "not case-major")
    require([r["solver"] for r in manifest["heldout"][:4]] == ["direct", "rho", "rho", "direct"], "alternation failed")
    print(json.dumps({"self_test": "PASS", "tests": 7}, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--phase", required=True, choices=("prepare", "validate-preserved-conformance", "conformance-attempt3", "validate-attempt3-final", "scientific", "finalize", "self-test")); args = parser.parse_args()
    {"prepare": prepare, "validate-preserved-conformance": validate_preserved_conformance,
     "conformance-attempt3": conformance_attempt3, "scientific": scientific,
     "validate-attempt3-final": validate_attempt3_final_parser,
     "finalize": finalize, "self-test": self_test}[args.phase]()


if __name__ == "__main__": main()
