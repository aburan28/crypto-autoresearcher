#!/usr/bin/env python3
"""Fail-closed verification for RECON-20260802-001 history artifacts."""
from __future__ import annotations

import argparse
import hashlib
import json
import stat
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.author_reconciliation_history import (
    AUTHORITY_CODE,
    CONTRACT_PATH,
    CONTRACT_SHA256,
    SNAPSHOT_COMMIT,
    Compilation,
    HistoryCompilerError,
    build_compilation,
    pretty_json,
)


TASK_ROOT = ROOT / "coordination/reconciliation/RECON-20260802-001/tasks/TASK-20260803-003"
DEFAULT_SOURCE_TABLE = TASK_ROOT / "source_occurrence_table.json"
DEFAULT_REFERENCE_TABLE = TASK_ROOT / "reference_occurrence_table.json"
IMPLEMENTATION_PATHS = {
    "compiler_sha256": "tools/author_reconciliation_history.py",
    "checker_sha256": "tools/check_reconciliation_generated_artifacts.py",
    "dispatcher_sha256": "tools/research_dispatch.py",
}


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _regular_file_bytes(path: Path, code: str) -> bytes:
    try:
        mode = path.lstat().st_mode
    except OSError as error:
        raise HistoryCompilerError(code, f"{path}: {error}") from error
    if path.is_symlink() or not stat.S_ISREG(mode):
        raise HistoryCompilerError(code, f"{path} is not a regular non-symlink file")
    return path.read_bytes()


def validate_candidate(compilation: Compilation, candidate_root: Path) -> dict[str, int]:
    """Verify a materialized candidate without mutating it."""

    root = candidate_root.resolve()
    copies = absences = outputs = 0
    for row in compilation.preservation_mappings:
        target = root.joinpath(*Path(row["target_path"]).parts)
        try:
            target.resolve(strict=False).relative_to(root)
        except ValueError as error:
            raise HistoryCompilerError("CANDIDATE_PATH_ESCAPE", row["target_path"]) from error
        if row["disposition"] == "absence_attestation":
            if target.exists() or target.is_symlink():
                raise HistoryCompilerError("ABSENCE_MATERIALIZED", row["target_path"])
            absences += 1
            continue
        content = _regular_file_bytes(target, "PRESERVATION_TARGET_INVALID")
        if _sha256(content) != row["source_sha256"]:
            raise HistoryCompilerError("PRESERVATION_TARGET_HASH_MISMATCH", row["target_path"])
        copies += 1
    for relative, expected in compilation.generated_outputs.items():
        target = root.joinpath(*Path(relative).parts)
        content = _regular_file_bytes(target, "GENERATED_OUTPUT_INVALID")
        if content != expected:
            raise HistoryCompilerError("GENERATED_OUTPUT_MISMATCH", relative)
        outputs += 1
    return {"blob_copies": copies, "absence_attestations": absences, "history_outputs": outputs}


def _verify_table(path: Path, expected: bytes, code: str) -> str:
    observed = _regular_file_bytes(path, code)
    if observed != expected:
        raise HistoryCompilerError(code, f"byte mismatch: {path}")
    return _sha256(observed)


def check(
    repo_root: Path = ROOT,
    source_table: Path = DEFAULT_SOURCE_TABLE,
    reference_table: Path = DEFAULT_REFERENCE_TABLE,
    candidate_root: Path | None = None,
) -> dict[str, Any]:
    findings: list[dict[str, str]] = []
    compilation: Compilation | None = None
    candidate_counts: dict[str, int] | None = None
    source_sha = reference_sha = None
    try:
        compilation = build_compilation(repo_root)
        source_sha = _verify_table(
            source_table,
            pretty_json(compilation.source_occurrences),
            "SOURCE_TABLE_BINDING_MISMATCH",
        )
        reference_sha = _verify_table(
            reference_table,
            pretty_json(compilation.reference_occurrences),
            "REFERENCE_TABLE_BINDING_MISMATCH",
        )
        if candidate_root is not None:
            candidate_counts = validate_candidate(compilation, candidate_root)
    except (OSError, HistoryCompilerError) as error:
        code = error.code if isinstance(error, HistoryCompilerError) else "INPUT_INVALID"
        findings.append({"code": code, "detail": str(error)})

    summary = compilation.summary() if compilation is not None else {}
    source_summary = (
        compilation.source_occurrences.get("summary", {})
        if compilation is not None
        else {}
    )
    reference_summary = (
        compilation.reference_occurrences.get("summary", {})
        if compilation is not None
        else {}
    )
    implementation_bindings: dict[str, str | None] = {}
    for key, relative in IMPLEMENTATION_PATHS.items():
        try:
            implementation_bindings[key] = _sha256(
                _regular_file_bytes(repo_root / relative, "IMPLEMENTATION_BINDING_INVALID")
            )
        except (OSError, HistoryCompilerError) as error:
            code = error.code if isinstance(error, HistoryCompilerError) else "INPUT_INVALID"
            findings.append({"code": code, "detail": str(error)})
            implementation_bindings[key] = None
    return {
        "schema": "crypto.autoresearch.reconciliation_history_static_check.v1",
        "reconciliation_id": "RECON-20260802-001",
        "task_id": "TASK-20260803-003",
        "pass": not findings,
        "authority": AUTHORITY_CODE,
        "input_bindings": {
            "contract_snapshot_commit": SNAPSHOT_COMMIT,
            "contract_path": CONTRACT_PATH,
            "contract_sha256": CONTRACT_SHA256,
            "source_table_sha256": source_sha,
            "reference_table_sha256": reference_sha,
        },
        "implementation_bindings": implementation_bindings,
        "counts": {
            "source_occurrences": summary.get("source_occurrence_rows"),
            "original_ids": source_summary.get("original_id_count"),
            "identity_id_counts": source_summary.get("identity_id_counts"),
            "source_state_counts": source_summary.get("state_counts"),
            "archive_entries": source_summary.get("archive_entry_count"),
            "archive_hash_bound": source_summary.get("archive_hash_bound_count"),
            "archive_unbound": source_summary.get("archive_unbound_count"),
            "archive_source_history_unreachable": source_summary.get(
                "archive_source_history_unreachable_count"
            ),
            "reference_occurrences": summary.get("reference_occurrence_rows"),
            "reference_queue_occurrences": reference_summary.get("queue_row_count"),
            "preservation_mappings": summary.get("preservation_mapping_rows"),
            "preservation_blob_copies": summary.get("preservation_blob_copies"),
            "preservation_absence_attestations": summary.get(
                "preservation_absence_attestations"
            ),
            "generated_history_outputs": summary.get("generated_history_outputs"),
        },
        "candidate_counts": candidate_counts,
        "findings": findings,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--source-table", type=Path, default=DEFAULT_SOURCE_TABLE)
    parser.add_argument("--reference-table", type=Path, default=DEFAULT_REFERENCE_TABLE)
    parser.add_argument("--candidate-root", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args(argv)
    report = check(
        args.repo_root,
        args.source_table,
        args.reference_table,
        args.candidate_root,
    )
    encoded = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(encoded, encoding="utf-8")
    else:
        sys.stdout.write(encoded)
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
