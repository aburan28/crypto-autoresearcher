#!/usr/bin/env python3
"""Stage the source-only closure and replace this process with pinned Python."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence


EXPECTED_ENVIRONMENT = {
    "MKL_NUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "PYTHONHASHSEED": "0",
    "VECLIB_MAXIMUM_THREADS": "1",
}
SOURCE_FILES = (
    "attest_tt_backend.py",
    "compile_tt_source_advice.py",
    "run_tt_source_partition.py",
    "tt_source_runtime.py",
)
DATA_FILES = (
    "source-execution-matrix-v2.json",
    "source-instance-manifest-v1.json",
)
PRODUCER_CLOSURE_FILES = (
    "attest_tt_backend.py",
    "compile_tt_source_advice.py",
    "tt_source_runtime.py",
)
VERIFIER_CLOSURE_FILES = ("verify_tt_source_advice.py",)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def stage_digest(rows: Sequence[Mapping[str, Any]]) -> str:
    digest = hashlib.sha256()
    for row in sorted(rows, key=lambda item: str(item["path"])):
        digest.update(str(row["path"]).encode("utf-8"))
        digest.update(b"\0")
        digest.update(bytes.fromhex(str(row["sha256"])))
    return digest.hexdigest()


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def validate_closure_rows(
    rows_value: Any,
    *,
    expected_names: Sequence[str],
    source_dir: Path,
    role: str,
) -> None:
    if not isinstance(rows_value, list):
        raise ValueError(f"static {role} closure is not an array")
    rows: dict[str, Mapping[str, Any]] = {}
    for row in rows_value:
        if not isinstance(row, dict):
            raise ValueError(f"static {role} closure row is not an object")
        path = row.get("path")
        if not isinstance(path, str) or path in rows:
            raise ValueError(f"static {role} closure path is invalid")
        rows[path] = row
    if set(rows) != set(expected_names):
        raise ValueError(f"static {role} closure file set changed")
    for name in expected_names:
        path = source_dir / name
        row = rows[name]
        if row.get("sha256") != sha256_file(path):
            raise ValueError(f"static {role} closure digest changed for {name}")
        if row.get("bytes") != path.stat().st_size:
            raise ValueError(f"static {role} closure size changed for {name}")


def validate_static_closure_audit(
    audit: Any,
    audit_bytes: bytes,
    source_dir: Path,
) -> None:
    if not isinstance(audit, dict) or audit.get("valid") is not True:
        raise ValueError("static closure audit is absent or invalid")
    if audit_bytes != canonical_bytes(audit):
        raise ValueError("static closure audit is not canonical JSON")
    if audit.get("schema") != "exp-ecdlp-tt-source-compiler-capability-audit-v1":
        raise ValueError("static closure audit schema changed")
    payload_sha256 = audit.get("payload_sha256")
    payload = dict(audit)
    payload.pop("payload_sha256", None)
    expected_payload_sha256 = hashlib.sha256(canonical_bytes(payload)[:-1]).hexdigest()
    if payload_sha256 != expected_payload_sha256:
        raise ValueError("static closure audit payload digest changed")
    cross_role = audit.get("cross_role")
    if not isinstance(cross_role, dict) or cross_role.get("valid") is not True:
        raise ValueError("producer/verifier closure disjointness did not pass")
    if cross_role.get("shared_files") != []:
        raise ValueError("producer/verifier closure unexpectedly shares files")

    auditor = audit.get("auditor")
    if not isinstance(auditor, dict):
        raise ValueError("static closure auditor identity is missing")
    if auditor.get("path") != "audit_tt_source_closure.py" or auditor.get("version") != 1:
        raise ValueError("static closure auditor identity changed")
    if auditor.get("sha256") != sha256_file(source_dir / "audit_tt_source_closure.py"):
        raise ValueError("static closure auditor digest changed")

    roles = audit.get("roles")
    if not isinstance(roles, dict):
        raise ValueError("static closure role records are missing")
    expected_roles = (
        ("producer", "compile_tt_source_advice.py", PRODUCER_CLOSURE_FILES),
        ("verifier", "verify_tt_source_advice.py", VERIFIER_CLOSURE_FILES),
    )
    for role_name, entry, expected_names in expected_roles:
        role = roles.get(role_name)
        if not isinstance(role, dict) or role.get("valid") is not True:
            raise ValueError(f"static {role_name} closure did not pass")
        if role.get("entry") != entry or role.get("violations") != []:
            raise ValueError(f"static {role_name} closure identity changed")
        validate_closure_rows(
            role.get("closure_files"),
            expected_names=expected_names,
            source_dir=source_dir,
            role=role_name,
        )


def remove_appledouble_files(stage_root: Path) -> None:
    for path in stage_root.iterdir():
        if path.name.startswith("._"):
            path.unlink()


def validate_staged_file_set(stage_root: Path) -> tuple[str, ...]:
    observed_names = tuple(sorted(path.name for path in stage_root.iterdir()))
    expected_names = tuple(sorted((*SOURCE_FILES, *DATA_FILES)))
    if observed_names != expected_names:
        raise RuntimeError("staged file set differs from source-only allowlist")
    return expected_names


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--experiment-dir", required=True, type=Path)
    parser.add_argument("--closure-audit", required=True, type=Path)
    parser.add_argument("--staging-parent", required=True, type=Path)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    experiment_dir = args.experiment_dir.resolve()
    source_dir = experiment_dir / "src"
    if args.closure_audit.name != "source-static-closure-audit.json":
        raise ValueError("static closure audit basename is not frozen")
    audit_bytes = args.closure_audit.read_bytes()
    audit = json.loads(audit_bytes)
    validate_static_closure_audit(audit, audit_bytes, source_dir)
    static_audit_sha256 = hashlib.sha256(audit_bytes).hexdigest()

    matrix_path = experiment_dir / "source-execution-matrix-v2.json"
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))[
        "source_execution_matrix"
    ]
    python_path = Path(matrix["backend_gate"]["python_executable"])
    if sha256_file(python_path) != matrix["backend_gate"]["python_executable_sha256"]:
        raise ValueError("pinned Python executable digest changed")

    args.staging_parent.mkdir(parents=True, exist_ok=True)
    stage_root = Path(
        tempfile.mkdtemp(
            prefix="tt-source-partition-",
            dir=args.staging_parent.resolve(),
        )
    )
    for name in SOURCE_FILES:
        shutil.copyfile(source_dir / name, stage_root / name)
    for name in DATA_FILES:
        shutil.copyfile(experiment_dir / name, stage_root / name)
    remove_appledouble_files(stage_root)
    expected_names = validate_staged_file_set(stage_root)
    stage_rows = [
        {
            "path": name,
            "sha256": sha256_file(stage_root / name),
        }
        for name in expected_names
    ]
    expected_stage_sha256 = stage_digest(stage_rows)

    bootstrap = stage_root / "run_tt_source_partition.py"
    manifest = stage_root / "source-instance-manifest-v1.json"
    execution_matrix = stage_root / "source-execution-matrix-v2.json"
    command = [
        str(python_path),
        "-I",
        "-B",
        str(bootstrap),
        "--manifest",
        str(manifest),
        "--execution-matrix",
        str(execution_matrix),
        "--expected-stage-sha256",
        expected_stage_sha256,
        "--static-audit-sha256",
        static_audit_sha256,
    ]
    os.chdir(stage_root)
    os.execve(str(python_path), command, EXPECTED_ENVIRONMENT)
    raise AssertionError("os.execve returned unexpectedly")


if __name__ == "__main__":
    raise SystemExit(main())
