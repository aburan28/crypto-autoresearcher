#!/usr/bin/env python3
"""Static development audit for disjoint target producer/verifier closures."""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence


SCHEMA = "exp-ecdlp-tt-target-capability-audit-development-v1"
EXPECTED_PRODUCER_FILES = (
    "compile_tt_target_advice.py",
    "tt_target_coefficients.py",
    "tt_target_runtime.py",
)
EXPECTED_VERIFIER_FILES = ("verify_tt_target_advice.py",)
EXPECTED_HARNESS_FILES = (
    "attest_tt_backend.py",
    "audit_tt_target_closure.py",
    "run_tt_target_partition.py",
    "stage_tt_target_partition.py",
)
FORBIDDEN_IMPORT_ROOTS = {
    "_thread",
    "ctypes",
    "itertools",
    "mmap",
    "multiprocessing",
    "requests",
    "socket",
    "subprocess",
    "threading",
    "urllib",
}
FORBIDDEN_CALLS = {
    "__import__",
    "compile",
    "connect",
    "eval",
    "exec",
    "execl",
    "execle",
    "execlp",
    "execlpe",
    "execv",
    "execve",
    "execvp",
    "execvpe",
    "fork",
    "popen",
    "posix_spawn",
    "request",
    "socket",
    "system",
    "urlopen",
}
FORBIDDEN_TUPLE_BUILDERS = {
    "meshgrid",
    "ndindex",
    "product",
}


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def closure_digest(root: Path, paths: Sequence[Path]) -> str:
    digest = hashlib.sha256()
    for path in sorted(paths, key=lambda item: item.relative_to(root).as_posix()):
        relative = path.relative_to(root).as_posix().encode("utf-8")
        digest.update(relative)
        digest.update(b"\0")
        digest.update(bytes.fromhex(file_digest(path)))
    return digest.hexdigest()


def call_name(node: ast.Call) -> str | None:
    function = node.func
    if isinstance(function, ast.Name):
        return function.id
    if isinstance(function, ast.Attribute):
        return function.attr
    return None


def import_roots(tree: ast.AST) -> set[str]:
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".", 1)[0])
    return roots


def local_dependencies(root: Path, tree: ast.AST) -> set[Path]:
    result: set[Path] = set()
    for module in import_roots(tree):
        candidate = root / f"{module}.py"
        if candidate.is_file():
            result.add(candidate.resolve())
    return result


def transitive_closure(root: Path, entry: Path) -> tuple[Path, ...]:
    root = root.resolve()
    pending = [entry.resolve()]
    observed: set[Path] = set()
    while pending:
        path = pending.pop()
        if path in observed:
            continue
        if path.parent != root or not path.is_file():
            raise ValueError(f"local closure path escapes source root: {path}")
        observed.add(path)
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        pending.extend(local_dependencies(root, tree) - observed)
    return tuple(sorted(observed))


class LoopDepthVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.depth = 0
        self.maximum = 0

    def visit_For(self, node: ast.For) -> None:  # noqa: N802
        self.depth += 1
        self.maximum = max(self.maximum, self.depth)
        self.generic_visit(node)
        self.depth -= 1

    def visit_AsyncFor(self, node: ast.AsyncFor) -> None:  # noqa: N802
        self.visit_For(node)  # type: ignore[arg-type]


def audit_file(path: Path, role: str) -> dict[str, Any]:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    roots = import_roots(tree)
    violations: list[dict[str, Any]] = []
    for root in sorted(roots & FORBIDDEN_IMPORT_ROOTS):
        violations.append({"kind": "forbidden_import", "name": root})
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = call_name(node)
        if name in FORBIDDEN_CALLS:
            violations.append(
                {"kind": "forbidden_call", "line": node.lineno, "name": name}
            )
        if name in FORBIDDEN_TUPLE_BUILDERS:
            violations.append(
                {"kind": "forbidden_tuple_builder", "line": node.lineno, "name": name}
            )
        if name in {"write", "write_bytes", "write_text", "writelines"}:
            expression = ast.unparse(node.func)
            if not expression.startswith("sys.stdout"):
                violations.append(
                    {
                        "kind": "non_stdout_write",
                        "line": node.lineno,
                        "name": expression,
                    }
                )
    loop_visitor = LoopDepthVisitor()
    loop_visitor.visit(tree)
    if role == "producer" and loop_visitor.maximum >= 5:
        violations.append(
            {"kind": "five_nested_loops", "maximum_loop_depth": loop_visitor.maximum}
        )
    return {
        "file": path.name,
        "forbidden_imports": sorted(roots & FORBIDDEN_IMPORT_ROOTS),
        "maximum_loop_depth": loop_visitor.maximum,
        "sha256": file_digest(path),
        "valid": not violations,
        "violations": violations,
    }


def audit_closures(
    source_root: Path,
    producer_entry: Path,
    verifier_entry: Path,
) -> dict[str, Any]:
    source_root = source_root.resolve()
    producer = transitive_closure(source_root, producer_entry)
    verifier = transitive_closure(source_root, verifier_entry)
    producer_names = tuple(path.name for path in producer)
    verifier_names = tuple(path.name for path in verifier)
    role_reports = {
        "producer": [audit_file(path, "producer") for path in producer],
        "verifier": [audit_file(path, "verifier") for path in verifier],
    }
    violations: list[dict[str, Any]] = []
    if producer_names != tuple(sorted(EXPECTED_PRODUCER_FILES)):
        violations.append(
            {
                "kind": "producer_closure_changed",
                "expected": sorted(EXPECTED_PRODUCER_FILES),
                "observed": list(producer_names),
            }
        )
    if verifier_names != EXPECTED_VERIFIER_FILES:
        violations.append(
            {
                "kind": "verifier_closure_changed",
                "expected": list(EXPECTED_VERIFIER_FILES),
                "observed": list(verifier_names),
            }
        )
    overlap = sorted(set(producer_names) & set(verifier_names))
    if overlap:
        violations.append({"kind": "producer_verifier_overlap", "files": overlap})
    for role, reports in role_reports.items():
        for report in reports:
            for violation in report["violations"]:
                violations.append(
                    {"file": report["file"], "role": role, **violation}
                )
    harness_paths = tuple((source_root / name).resolve() for name in EXPECTED_HARNESS_FILES)
    for path in harness_paths:
        if path.parent != source_root or not path.is_file():
            violations.append({"kind": "harness_file_missing", "file": path.name})
    harness_rows = [
        {
            "bytes": path.stat().st_size,
            "path": path.name,
            "sha256": file_digest(path),
        }
        for path in harness_paths
        if path.is_file()
    ]
    return {
        "artifact_freeze_authorized": False,
        "boundary": (
            "Development static closure audit only. Runtime isolation, package/loader "
            "attestation, and execution authorization remain separate gates."
        ),
        "producer": {
            "closure_sha256": closure_digest(source_root, producer),
            "entry": producer_entry.name,
            "files": list(producer_names),
            "reports": role_reports["producer"],
        },
        "harness": {
            "closure_sha256": closure_digest(source_root, harness_paths),
            "files": harness_rows,
        },
        "schema": SCHEMA,
        "valid": not violations,
        "verifier": {
            "closure_sha256": closure_digest(source_root, verifier),
            "entry": verifier_entry.name,
            "files": list(verifier_names),
            "reports": role_reports["verifier"],
        },
        "violations": violations,
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--producer-entry", type=Path, required=True)
    parser.add_argument("--verifier-entry", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    try:
        args = parse_args(argv)
        result = audit_closures(
            args.source_root, args.producer_entry, args.verifier_entry
        )
    except Exception as error:
        result = {
            "artifact_freeze_authorized": False,
            "error": {"message": str(error), "type": type(error).__name__},
            "schema": "exp-ecdlp-tt-target-capability-audit-development-failure-v1",
            "valid": False,
        }
    sys.stdout.buffer.write(canonical_json_bytes(result) + b"\n")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
