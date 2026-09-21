#!/usr/bin/env python3
"""Static capability audit for the TT source producer and source verifier.

This is a harness-side tool.  It parses source without importing or executing
the audited modules and writes one canonical JSON document to stdout.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Iterator, Mapping, Sequence


SCHEMA = "exp-ecdlp-tt-source-compiler-capability-audit-v1"
AUDITOR_VERSION = 1
SCRIPT_PATH = Path(__file__).resolve()
SOURCE_DIR = SCRIPT_PATH.parent
EXPERIMENT_DIR = SOURCE_DIR.parent

ROLE_PRODUCER = "producer"
ROLE_VERIFIER = "verifier"
ROLES = (ROLE_PRODUCER, ROLE_VERIFIER)
EXPECTED_HARNESS_FILES = (
    "audit_tt_source_closure.py",
    "run_tt_source_partition.py",
    "run_tt_source_verifier_partition.py",
    "stage_tt_source_partition.py",
    "stage_tt_target_partition.py",
)

CANONICAL_IR_KINDS = (
    "input_coordinate",
    "scale",
    "direct_sum",
    "stage_a_contract",
    "stage_b_contract",
    "rank_factor",
    "absorb_left",
    "absorb_right",
    "emit",
    "free",
)

DYNAMIC_MODULE_ROOTS = {
    "code",
    "codeop",
    "dill",
    "importlib",
    "marshal",
    "pickle",
    "pkgutil",
    "runpy",
}
PROCESS_MODULE_ROOTS = {
    "asyncio.subprocess",
    "multiprocessing",
    "os",  # Individual safe os APIs are handled at call sites.
    "pty",
    "subprocess",
}
NETWORK_MODULE_ROOTS = {
    "ftplib",
    "http",
    "requests",
    "socket",
    "ssl",
    "telnetlib",
    "urllib",
    "webbrowser",
    "xmlrpc",
}
ESCAPE_MODULE_ROOTS = {"array", "cffi", "ctypes", "mmap"}
FILESYSTEM_OR_OUTPUT_MODULE_ROOTS = {"logging", "shutil", "tempfile", "warnings"}

DYNAMIC_CALL_NAMES = {
    "__import__",
    "compile",
    "delattr",
    "eval",
    "exec",
    "getattr",
    "globals",
    "locals",
    "setattr",
    "vars",
}
PROCESS_CALL_NAMES = {
    "execv",
    "execve",
    "fork",
    "forkpty",
    "popen",
    "posix_spawn",
    "posix_spawnp",
    "spawnl",
    "spawnle",
    "spawnlp",
    "spawnlpe",
    "spawnv",
    "spawnve",
    "spawnvp",
    "spawnvpe",
    "startfile",
    "system",
}
NETWORK_CALL_NAMES = {
    "connect",
    "connect_ex",
    "create_connection",
    "getaddrinfo",
    "listen",
    "request",
    "send",
    "sendall",
    "socket",
    "urlopen",
}
WRITE_METHOD_NAMES = {
    "mkdir",
    "makedirs",
    "remove",
    "rename",
    "replace",
    "rmdir",
    "symlink",
    "touch",
    "truncate",
    "unlink",
    "write",
    "write_bytes",
    "write_text",
    "writelines",
}
DIRECTORY_ENUMERATION_NAMES = {"fwalk", "glob", "iglob", "iterdir", "listdir", "rglob", "scandir", "walk"}

SAFE_BUILTIN_CALLS = {
    "abs",
    "all",
    "any",
    "ascii",
    "bin",
    "bool",
    "bytearray",
    "bytes",
    "callable",
    "classmethod",
    "chr",
    "dict",
    "divmod",
    "enumerate",
    "filter",
    "format",
    "frozenset",
    "hash",
    "hex",
    "id",
    "int",
    "isinstance",
    "issubclass",
    "iter",
    "len",
    "list",
    "map",
    "max",
    "memoryview",
    "min",
    "next",
    "oct",
    "ord",
    "pow",
    "print",
    "property",
    "range",
    "repr",
    "reversed",
    "round",
    "set",
    "slice",
    "sorted",
    "str",
    "staticmethod",
    "sum",
    "super",
    "tuple",
    "type",
    "zip",
}
FORBIDDEN_NUMERIC_BUILTINS = {"complex", "float"}

SAFE_UNKNOWN_METHODS = {
    "__init__",
    "add",
    "add_argument",
    "append",
    "bit_length",
    "clear",
    "copy",
    "count",
    "decode",
    "digest",
    "discard",
    "encode",
    "endswith",
    "extend",
    "fromhex",
    "get",
    "group",
    "hexdigest",
    "index",
    "insert",
    "items",
    "is_file",
    "join",
    "keys",
    "lower",
    "lstrip",
    "open",
    "parse_args",
    "read",
    "read_bytes",
    "read_text",
    "resolve",
    "pop",
    "remove",
    "replace",
    "reverse",
    "rsplit",
    "rstrip",
    "setdefault",
    "sort",
    "split",
    "startswith",
    "stat",
    "strip",
    "to_bytes",
    "union",
    "update",
    "upper",
    "values",
}

NUMPY_ALLOWED_FUNCTIONS = {
    "copy",
    "empty",
    "flatnonzero",
    "matmul",
    "multiply",
    "remainder",
    "subtract",
    "zeros",
}
NUMPY_ALLOWED_METHODS = {"copy", "reshape"}
NUMPY_FORBIDDEN_FUNCTIONS = {
    "arange",
    "array",
    "buffer",
    "asarray",
    "broadcast_arrays",
    "broadcast_to",
    "concatenate",
    "einsum",
    "fromfunction",
    "full",
    "indices",
    "kron",
    "meshgrid",
    "ndarray",
    "ndindex",
    "ones",
    "stack",
    "tensordot",
    "tile",
}
NUMPY_FORBIDDEN_METHODS = {
    "astype",
    "choose",
    "compress",
    "cumprod",
    "cumsum",
    "diagonal",
    "dot",
    "flatten",
    "item",
    "nonzero",
    "prod",
    "ravel",
    "repeat",
    "resize",
    "sum",
    "take",
    "tobytes",
    "tolist",
    "trace",
    "transpose",
}
NUMPY_ALLOCATION_FUNCTIONS = {
    "array",
    "asarray",
    "empty",
    "fromfunction",
    "full",
    "indices",
    "meshgrid",
    "ndarray",
    "ones",
    "zeros",
}
NUMPY_ARITHMETIC_FUNCTIONS = {"matmul", "multiply", "remainder", "subtract"}
ALLOWED_INT64_DTYPE_STRINGS = {"<i8", "=i8", "i8", "int64"}
FLOAT_DTYPE_FRAGMENT = re.compile(r"(?:float|double|complex|f[248]|c(?:8|16)|object)", re.I)

B_NAMES = {
    "b",
    "base",
    "base_size",
    "factor_base_size",
    "mode_size",
    "physical_dimension",
    "physical_size",
}
FIELD_MODULUS_NAMES = {"field_modulus", "modulus", "p", "prime"}
ARRAY_NAME_FRAGMENTS = (
    "array",
    "core",
    "factor",
    "matrix",
    "prefix",
    "residue",
    "table",
    "tensor",
    "transfer",
    "tt",
)
MODE_NAME_RE = re.compile(r"^(?:physical_)?mode(?:_index)?$|^axis$|^p[1-5]$", re.I)
SLICE_NAME_RE = re.compile(r"^(?:physical_)?slice(?:_index)?$", re.I)

PRODUCER_FORBIDDEN_LOCAL_FRAGMENTS = (
    "audit",
    "mutation",
    "specialize",
    "target",
    "verifier",
    "verify",
)
VERIFIER_FORBIDDEN_LOCAL_FRAGMENTS = (
    "compile_tt_source",
    "compiler",
    "producer",
    "source_runtime",
    "tt_source_runtime",
)

PRODUCER_ALLOWED_DATA = {
    "source-execution-matrix-v2.json",
    "source-instance-manifest-v1.json",
}
VERIFIER_ALLOWED_DATA = PRODUCER_ALLOWED_DATA | {"source-generator-raw-result.json"}
PRODUCER_ALLOWED_PATH_OPTIONS = {
    "--execution-matrix",
    "--manifest",
    "--source-execution-matrix",
    "--source-manifest",
}
VERIFIER_ALLOWED_PATH_OPTIONS = PRODUCER_ALLOWED_PATH_OPTIONS | {"--raw-result"}
FORBIDDEN_ARTIFACT_FRAGMENTS = (
    "execution-matrix-v4",
    "exp-ecdlp-tt-norm-rank-001",
    "frozen-source-advice",
    "frozen-source-control-certificates",
    "mutation-manifest",
    "prior run",
    "target-instance-manifest",
)


class AuditConfigurationError(RuntimeError):
    """Raised when the harness asks for an ill-defined audit."""


@dataclass(frozen=True, order=True)
class Violation:
    role: str
    path: str
    line: int
    column: int
    reason_code: str
    symbol: str
    detail: str

    def as_json(self) -> dict[str, Any]:
        return {
            "column": self.column,
            "detail": self.detail,
            "line": self.line,
            "path": self.path,
            "reason_code": self.reason_code,
            "role": self.role,
            "symbol": self.symbol,
        }


@dataclass(frozen=True)
class Binding:
    kind: str
    target: str


@dataclass
class ModuleInfo:
    path: Path
    relative_path: str
    module_name: str
    source: str
    digest: str
    tree: ast.Module | None
    parse_error: str | None = None
    imports: dict[str, Binding] = field(default_factory=dict)
    definitions: dict[str, str] = field(default_factory=dict)
    class_methods: dict[str, set[str]] = field(default_factory=dict)


@dataclass(frozen=True)
class Policy:
    protocol_version: int
    allowed_ir_kinds: tuple[str, ...]
    allowed_numpy_functions: tuple[str, ...]
    forbidden_numpy_functions: tuple[str, ...]
    forbidden_import_roots: tuple[str, ...]
    environment_allowlist: tuple[str, ...]
    maximum_ndarray_dimensions: int
    source_b_values: tuple[int, ...]
    policy_file_hashes: tuple[tuple[str, str], ...]
    sensitive_strings: frozenset[str]
    sensitive_sequences: frozenset[str]
    mutation_count: int

    def public_json(self) -> dict[str, Any]:
        return {
            "allowed_ir_kinds": list(self.allowed_ir_kinds),
            "allowed_numpy_functions": list(self.allowed_numpy_functions),
            "environment_allowlist": list(self.environment_allowlist),
            "forbidden_import_roots": list(self.forbidden_import_roots),
            "forbidden_numpy_functions": list(self.forbidden_numpy_functions),
            "maximum_ndarray_dimensions": self.maximum_ndarray_dimensions,
            "mutation_count": self.mutation_count,
            "policy_file_hashes": [
                {"path": path, "sha256": digest}
                for path, digest in self.policy_file_hashes
            ],
            "protocol_version": self.protocol_version,
            "sensitive_sequence_count": len(self.sensitive_sequences),
            "sensitive_string_count": len(self.sensitive_strings),
            "source_b_values": list(self.source_b_values),
        }


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def closure_digest(rows: Sequence[Mapping[str, Any]]) -> str:
    digest = hashlib.sha256()
    for row in sorted(rows, key=lambda item: str(item["path"])):
        digest.update(str(row["path"]).encode("utf-8"))
        digest.update(b"\0")
        digest.update(bytes.fromhex(str(row["sha256"])))
    return digest.hexdigest()


def read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise AuditConfigurationError(f"cannot read {label}: {exc.__class__.__name__}") from exc
    if not isinstance(value, dict):
        raise AuditConfigurationError(f"{label} must contain a JSON object")
    return value


def path_label(path: Path, base: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(base.resolve()).as_posix()
    except ValueError:
        return resolved.name


def walk_json_values(value: Any) -> Iterator[Any]:
    if isinstance(value, Mapping):
        for child in value.values():
            yield from walk_json_values(child)
    elif isinstance(value, list):
        yield value
        for child in value:
            yield from walk_json_values(child)
    else:
        yield value


def walk_json_keys(value: Any) -> Iterator[str]:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if isinstance(key, str):
                yield key
            yield from walk_json_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_json_keys(child)


def scalar_strings(value: Any) -> set[str]:
    return {item for item in walk_json_values(value) if isinstance(item, str)}


def integer_sequences(value: Any) -> set[str]:
    result: set[str] = set()
    for item in walk_json_values(value):
        if (
            isinstance(item, list)
            and len(item) >= 2
            and all(isinstance(element, int) and not isinstance(element, bool) for element in item)
        ):
            result.add(canonical_json_bytes(item).decode("ascii"))
    return result


def target_specific_strings(target_document: Mapping[str, Any], full_matrix: Mapping[str, Any]) -> set[str]:
    result: set[str] = set()
    target = target_document.get("target_manifest")
    if isinstance(target, Mapping):
        identifier = target.get("id")
        if isinstance(identifier, str):
            result.add(identifier)
        instances = target.get("instances")
        if isinstance(instances, list):
            for instance in instances:
                if not isinstance(instance, Mapping):
                    continue
                targets = instance.get("targets")
                if not isinstance(targets, Mapping):
                    continue
                for label, record in targets.items():
                    if isinstance(label, str):
                        result.add(label)
                    if isinstance(record, Mapping) and isinstance(record.get("target_id"), str):
                        result.add(record["target_id"])
        schedule = target.get("schedule")
        if isinstance(schedule, list):
            result.update(item for item in schedule if isinstance(item, str))
    matrix_schedule = full_matrix.get("target_schedule")
    if isinstance(matrix_schedule, list):
        for item in walk_json_values(matrix_schedule):
            if isinstance(item, str):
                result.add(item)
    return {item for item in result if len(item) >= 3}


def load_policy(
    contract_path: Path,
    source_matrix_path: Path,
    full_matrix_path: Path,
    mutation_manifest_path: Path,
    source_manifest_path: Path,
    target_manifest_path: Path,
) -> Policy:
    all_paths = (
        contract_path,
        source_matrix_path,
        full_matrix_path,
        mutation_manifest_path,
        source_manifest_path,
        target_manifest_path,
    )
    for path in all_paths:
        if not path.is_file():
            raise AuditConfigurationError(f"required policy file is missing: {path.name}")

    contract_text = contract_path.read_text(encoding="utf-8")
    for heading in ("## C3:", "## C4:", "## C5:"):
        if heading not in contract_text:
            raise AuditConfigurationError(f"contract is missing {heading[:-1]}")

    source_doc = read_json(source_matrix_path, "source execution matrix")
    full_doc = read_json(full_matrix_path, "full execution matrix")
    mutation_doc = read_json(mutation_manifest_path, "mutation manifest")
    source_manifest = read_json(source_manifest_path, "source manifest")
    target_manifest = read_json(target_manifest_path, "target manifest")

    source = source_doc.get("source_execution_matrix")
    full = full_doc.get("execution_matrix")
    mutation = mutation_doc.get("mutation_manifest")
    if not isinstance(source, dict) or not isinstance(full, dict) or not isinstance(mutation, dict):
        raise AuditConfigurationError("policy documents use an unexpected top-level schema")

    versions = {source.get("protocol_version"), full.get("protocol_version"), mutation.get("protocol_version")}
    if versions != {5}:
        raise AuditConfigurationError("policy protocol versions do not all equal 5")

    source_ir = source.get("accepted_operation_ir", {}).get("node_kinds")
    full_ir = full.get("accepted_operation_ir", {}).get("node_kinds")
    if source_ir != full_ir or tuple(source_ir or ()) != CANONICAL_IR_KINDS:
        raise AuditConfigurationError("closed IR differs from the reviewed ten-node IR")

    source_backend = source.get("backend_gate")
    full_backend = full.get("backend_gate")
    if not isinstance(source_backend, dict) or not isinstance(full_backend, dict):
        raise AuditConfigurationError("backend gate is missing")
    allowed_kernels = tuple(sorted(source_backend.get("allowed_dense_kernels", ())))
    full_allowed = tuple(sorted(full_backend.get("allowed_dense_kernels", ())))
    if allowed_kernels != full_allowed:
        raise AuditConfigurationError("source and full NumPy allowlists differ")
    normalized_allowed = tuple(sorted("reshape" if item == "reshape_C" else item for item in allowed_kernels))
    if set(normalized_allowed) != NUMPY_ALLOWED_FUNCTIONS | {"reshape"}:
        raise AuditConfigurationError("NumPy allowlist differs from the reviewed backend")

    forbidden_kernels = tuple(sorted(source_backend.get("forbidden_dense_kernels", ())))
    source_boundary = source.get("source_capability_boundary")
    full_boundaries = full.get("capability_boundaries")
    if not isinstance(source_boundary, dict) or not isinstance(full_boundaries, dict):
        raise AuditConfigurationError("capability boundary is missing")
    local_boundary = full_boundaries.get("local_source_closure")
    if not isinstance(local_boundary, dict):
        raise AuditConfigurationError("local source closure boundary is missing")

    source_forbidden_imports = set(source_boundary.get("forbidden_imports", ()))
    full_forbidden_imports = set(local_boundary.get("forbidden_imports", ()))
    if source_forbidden_imports != full_forbidden_imports:
        raise AuditConfigurationError("source and full forbidden-import sets differ")

    environment_allowlist = tuple(sorted(source_boundary.get("environment_read_allowlist", ())))
    maximum_dimensions = source_boundary.get("maximum_ndarray_dimensions")
    if not isinstance(maximum_dimensions, int) or maximum_dimensions != 3:
        raise AuditConfigurationError("maximum ndarray dimension is not the reviewed value 3")

    source_cells = source.get("source_cells")
    if not isinstance(source_cells, list):
        raise AuditConfigurationError("source cells are missing")
    b_values = sorted(
        {
            cell.get("B")
            for cell in source_cells
            if isinstance(cell, dict) and isinstance(cell.get("B"), int)
        }
    )
    if not b_values:
        raise AuditConfigurationError("source B values are missing")

    source_binding = source.get("bindings", {})
    full_binding = full.get("bindings", {})
    expected_bindings = (
        (source_manifest_path, source_binding.get("source_manifest_sha256")),
        (source_manifest_path, full_binding.get("source_manifest_sha256")),
        (source_matrix_path, full_binding.get("source_execution_matrix_sha256")),
        (target_manifest_path, full_binding.get("target_manifest_sha256")),
        (mutation_manifest_path, full_binding.get("mutation_manifest_sha256")),
    )
    for path, expected in expected_bindings:
        if not isinstance(expected, str) or sha256_file(path) != expected:
            raise AuditConfigurationError(f"policy binding mismatch for {path.name}")

    mutations = mutation.get("mutations")
    if not isinstance(mutations, list) or len(mutations) != 29:
        raise AuditConfigurationError("mutation manifest does not contain 29 frozen mutations")

    source_strings = scalar_strings(source_manifest) | scalar_strings(source_doc)
    sensitive_strings = target_specific_strings(target_manifest, full) - source_strings
    target_digest = full_binding.get("target_manifest_sha256")
    if isinstance(target_digest, str):
        sensitive_strings.add(target_digest)
    sensitive_strings.add(sha256_file(full_matrix_path))
    sensitive_strings.add(sha256_file(mutation_manifest_path))
    for item in mutations:
        if isinstance(item, dict) and isinstance(item.get("id"), str):
            sensitive_strings.add(item["id"])

    source_sequences = integer_sequences(source_manifest) | integer_sequences(source_doc)
    sensitive_sequences = integer_sequences(target_manifest) - source_sequences

    policy_hashes = tuple(
        sorted(
            (path_label(path, EXPERIMENT_DIR), sha256_file(path))
            for path in all_paths
        )
    )
    forbidden_roots = tuple(
        sorted(
            source_forbidden_imports
            | DYNAMIC_MODULE_ROOTS
            | NETWORK_MODULE_ROOTS
            | ESCAPE_MODULE_ROOTS
            | FILESYSTEM_OR_OUTPUT_MODULE_ROOTS
        )
    )
    return Policy(
        protocol_version=5,
        allowed_ir_kinds=tuple(source_ir),
        allowed_numpy_functions=tuple(sorted(set(normalized_allowed) - {"reshape"})),
        forbidden_numpy_functions=tuple(sorted(set(forbidden_kernels) | NUMPY_FORBIDDEN_FUNCTIONS)),
        forbidden_import_roots=forbidden_roots,
        environment_allowlist=environment_allowlist,
        maximum_ndarray_dimensions=maximum_dimensions,
        source_b_values=tuple(b_values),
        policy_file_hashes=policy_hashes,
        sensitive_strings=frozenset(sensitive_strings),
        sensitive_sequences=frozenset(sensitive_sequences),
        mutation_count=len(mutations),
    )


def module_name_for(path: Path, source_root: Path) -> str:
    relative = path.resolve().relative_to(source_root.resolve())
    parts = list(relative.with_suffix("").parts)
    if parts and parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def build_module_index(source_root: Path) -> tuple[dict[str, Path], dict[Path, str]]:
    by_name: dict[str, Path] = {}
    by_path: dict[Path, str] = {}
    for path in sorted(source_root.rglob("*.py")):
        if path.name.startswith("._") or "__pycache__" in path.parts:
            continue
        if path.is_symlink():
            raise AuditConfigurationError(f"local source symlink is forbidden: {path.name}")
        resolved = path.resolve()
        try:
            resolved.relative_to(source_root.resolve())
        except ValueError as exc:
            raise AuditConfigurationError(f"local source path escapes the root: {path.name}") from exc
        name = module_name_for(resolved, source_root)
        if name in by_name and by_name[name] != resolved:
            raise AuditConfigurationError(f"duplicate local module name: {name or '<root>'}")
        by_name[name] = resolved
        by_path[resolved] = name
    return by_name, by_path


def parse_module(path: Path, source_root: Path, module_name: str) -> ModuleInfo:
    try:
        data = path.read_bytes()
        source = data.decode("utf-8")
    except (OSError, UnicodeError) as exc:
        return ModuleInfo(
            path=path,
            relative_path=path_label(path, source_root),
            module_name=module_name,
            source="",
            digest="",
            tree=None,
            parse_error=exc.__class__.__name__,
        )
    try:
        tree = ast.parse(source, filename=path.as_posix(), type_comments=True)
        error = None
    except SyntaxError as exc:
        tree = None
        error = f"{exc.msg} at {exc.lineno or 0}:{exc.offset or 0}"
    info = ModuleInfo(
        path=path,
        relative_path=path_label(path, source_root),
        module_name=module_name,
        source=source,
        digest=sha256_bytes(data),
        tree=tree,
        parse_error=error,
    )
    if tree is not None:
        collect_module_symbols(info)
    return info


def collect_module_symbols(info: ModuleInfo) -> None:
    assert info.tree is not None
    for node in info.tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            info.definitions[node.name] = f"{info.module_name}.{node.name}".lstrip(".")
        elif isinstance(node, ast.ClassDef):
            qualname = f"{info.module_name}.{node.name}".lstrip(".")
            info.definitions[node.name] = qualname
            info.class_methods[node.name] = {
                child.name
                for child in node.body
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
            }


def resolve_relative_module(current: str, is_package: bool, level: int, module: str | None) -> str | None:
    package_parts = current.split(".") if is_package else current.split(".")[:-1]
    if level <= 0:
        return module or ""
    ascents = level - 1
    if ascents > len(package_parts):
        return None
    prefix = package_parts[: len(package_parts) - ascents]
    if module:
        prefix.extend(module.split("."))
    return ".".join(part for part in prefix if part)


def module_root(name: str) -> str:
    return name.split(".", 1)[0]


def matches_module_set(name: str, candidates: Iterable[str]) -> bool:
    return any(name == candidate or name.startswith(candidate + ".") for candidate in candidates)


def imported_modules(info: ModuleInfo) -> list[tuple[ast.AST, str, str, str | None]]:
    """Return (node, bound name, module, imported symbol) rows."""
    rows: list[tuple[ast.AST, str, str, str | None]] = []
    if info.tree is None:
        return rows
    is_package = info.path.name == "__init__.py"
    for node in ast.walk(info.tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                bound = alias.asname or alias.name.split(".", 1)[0]
                rows.append((node, bound, alias.name, None))
        elif isinstance(node, ast.ImportFrom):
            base = resolve_relative_module(
                info.module_name,
                is_package,
                node.level,
                node.module,
            )
            if base is None:
                rows.append((node, "*", "<outside-root>", None))
                continue
            for alias in node.names:
                bound = alias.asname or alias.name
                rows.append((node, bound, base, alias.name))
    return rows


def bind_imports(
    info: ModuleInfo,
    module_index: Mapping[str, Path],
) -> tuple[set[str], list[Violation]]:
    dependencies: set[str] = set()
    violations: list[Violation] = []
    for node, bound, base, symbol in imported_modules(info):
        if base == "<outside-root>":
            violations.append(
                Violation(
                    role="",
                    path=info.relative_path,
                    line=getattr(node, "lineno", 0),
                    column=getattr(node, "col_offset", 0),
                    reason_code="IMPORT_OUTSIDE_SOURCE_ROOT",
                    symbol=bound,
                    detail="relative import escapes the declared local source root",
                )
            )
            continue
        if symbol is None:
            if base in module_index:
                info.imports[bound] = Binding("local_module", base)
                dependencies.add(base)
            else:
                info.imports[bound] = Binding("external_module", base)
            continue

        candidate_module = f"{base}.{symbol}" if base else symbol
        if candidate_module in module_index:
            info.imports[bound] = Binding("local_module", candidate_module)
            dependencies.add(candidate_module)
        elif base in module_index:
            info.imports[bound] = Binding("local_symbol", f"{base}.{symbol}".lstrip("."))
            dependencies.add(base)
        else:
            info.imports[bound] = Binding("external_symbol", f"{base}.{symbol}".lstrip("."))
    return dependencies, violations


@dataclass
class Closure:
    role: str
    entry: Path
    source_root: Path
    modules: dict[str, ModuleInfo]
    import_violations: list[Violation]

    @property
    def paths(self) -> set[Path]:
        return {module.path for module in self.modules.values()}


def build_closure(role: str, entry: Path, source_root: Path) -> Closure:
    source_root = source_root.resolve()
    entry = entry.resolve()
    try:
        entry.relative_to(source_root)
    except ValueError as exc:
        raise AuditConfigurationError(f"{role} entry is outside the source root") from exc
    if not entry.is_file() or entry.suffix != ".py":
        raise AuditConfigurationError(f"{role} entry is not a Python file")

    module_index, by_path = build_module_index(source_root)
    if entry not in by_path:
        raise AuditConfigurationError(f"{role} entry is absent from the module index")

    pending = [by_path[entry]]
    modules: dict[str, ModuleInfo] = {}
    violations: list[Violation] = []
    while pending:
        name = pending.pop(0)
        if name in modules:
            continue
        path = module_index[name]
        info = parse_module(path, source_root, name)
        modules[name] = info
        if info.tree is None:
            violations.append(
                Violation(
                    role=role,
                    path=info.relative_path,
                    line=0,
                    column=0,
                    reason_code="AST_PARSE_ERROR",
                    symbol=name,
                    detail=info.parse_error or "source could not be parsed",
                )
            )
            continue
        dependencies, import_errors = bind_imports(info, module_index)
        violations.extend(
            Violation(
                role=role,
                path=item.path,
                line=item.line,
                column=item.column,
                reason_code=item.reason_code,
                symbol=item.symbol,
                detail=item.detail,
            )
            for item in import_errors
        )
        pending.extend(sorted(dependencies - modules.keys()))
    return Closure(role, entry, source_root, modules, violations)


def flatten_attribute(node: ast.AST) -> tuple[str | None, list[str]]:
    parts: list[str] = []
    current = node
    while isinstance(current, ast.Attribute):
        parts.append(current.attr)
        current = current.value
    if isinstance(current, ast.Name):
        return current.id, list(reversed(parts))
    return None, list(reversed(parts))


def literal_string(node: ast.AST | None) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        values: list[str] = []
        for child in node.values:
            if not isinstance(child, ast.Constant) or not isinstance(child.value, str):
                return None
            values.append(child.value)
        return "".join(values)
    return None


def literal_int(node: ast.AST | None) -> int | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, int) and not isinstance(node.value, bool):
        return node.value
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
        value = literal_int(node.operand)
        if value is not None:
            return -value if isinstance(node.op, ast.USub) else value
    return None


def literal_sequence(node: ast.AST) -> str | None:
    if not isinstance(node, (ast.List, ast.Tuple)):
        return None
    values: list[int] = []
    for child in node.elts:
        value = literal_int(child)
        if value is None:
            return None
        values.append(value)
    if len(values) < 2:
        return None
    return canonical_json_bytes(values).decode("ascii")


def normalized_name(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def is_b_name(name: str) -> bool:
    return normalized_name(name) in B_NAMES


def is_field_modulus_name(name: str) -> bool:
    return normalized_name(name) in FIELD_MODULUS_NAMES


def expression_names(node: ast.AST) -> set[str]:
    return {
        child.id
        for child in ast.walk(node)
        if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Load)
    }


def has_arrayish_name(node: ast.AST) -> bool:
    for name in expression_names(node):
        lowered = normalized_name(name)
        if any(fragment in lowered for fragment in ARRAY_NAME_FRAGMENTS):
            return True
    return False


def constant_int_expression(
    node: ast.AST,
    assignments: Mapping[str, ast.AST],
    seen: frozenset[str] = frozenset(),
) -> int | None:
    direct = literal_int(node)
    if direct is not None:
        return direct
    if isinstance(node, ast.Name) and node.id in assignments and node.id not in seen:
        return constant_int_expression(assignments[node.id], assignments, seen | {node.id})
    if isinstance(node, ast.BinOp):
        left = constant_int_expression(node.left, assignments, seen)
        right = constant_int_expression(node.right, assignments, seen)
        if left is None or right is None:
            return None
        try:
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            if isinstance(node.op, ast.FloorDiv) and right != 0:
                return left // right
            if isinstance(node.op, ast.Mod) and right != 0:
                return left % right
            if isinstance(node.op, ast.Pow) and 0 <= right <= 16:
                return left**right
        except (ArithmeticError, OverflowError):
            return None
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "pow":
        if len(node.args) == 2:
            left = constant_int_expression(node.args[0], assignments, seen)
            right = constant_int_expression(node.args[1], assignments, seen)
            if left is not None and right is not None and 0 <= right <= 16:
                return left**right
    return None


def b_degree(
    node: ast.AST,
    assignments: Mapping[str, ast.AST],
    seen: frozenset[str] = frozenset(),
) -> int | None:
    if isinstance(node, ast.Name):
        if is_b_name(node.id):
            return 1
        if node.id in assignments and node.id not in seen:
            return b_degree(assignments[node.id], assignments, seen | {node.id})
        return None
    if literal_int(node) is not None:
        return 0
    if isinstance(node, ast.BinOp):
        left = b_degree(node.left, assignments, seen)
        right = b_degree(node.right, assignments, seen)
        if isinstance(node.op, ast.Mult) and left is not None and right is not None:
            return left + right
        if isinstance(node.op, ast.Pow):
            exponent = constant_int_expression(node.right, assignments, seen)
            if left is not None and exponent is not None and exponent >= 0:
                return left * exponent
        return None
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "pow":
        if len(node.args) == 2:
            base = b_degree(node.args[0], assignments, seen)
            exponent = constant_int_expression(node.args[1], assignments, seen)
            if base is not None and exponent is not None and exponent >= 0:
                return base * exponent
    if isinstance(node, ast.Call):
        root, attrs = flatten_attribute(node.func)
        call_name = attrs[-1] if attrs else root
        if call_name == "prod" and node.args:
            values = node.args[0]
            if isinstance(values, (ast.List, ast.Tuple)):
                degrees = [b_degree(item, assignments, seen) for item in values.elts]
                if degrees and all(item is not None for item in degrees):
                    return sum(item for item in degrees if item is not None)
            if isinstance(values, ast.BinOp) and isinstance(values.op, ast.Mult):
                sequence: ast.List | ast.Tuple | None = None
                count_node: ast.AST | None = None
                if isinstance(values.left, (ast.List, ast.Tuple)):
                    sequence, count_node = values.left, values.right
                elif isinstance(values.right, (ast.List, ast.Tuple)):
                    sequence, count_node = values.right, values.left
                if sequence is not None and count_node is not None:
                    count = constant_int_expression(count_node, assignments, seen)
                    degrees = [b_degree(item, assignments, seen) for item in sequence.elts]
                    if count is not None and degrees and all(item is not None for item in degrees):
                        return count * sum(item for item in degrees if item is not None)
    return None


def shape_dimensions(node: ast.AST, assignments: Mapping[str, ast.AST]) -> int | None:
    if isinstance(node, (ast.Tuple, ast.List)):
        return len(node.elts)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mult):
        if isinstance(node.left, (ast.Tuple, ast.List)):
            count = constant_int_expression(node.right, assignments)
            if count is not None:
                return len(node.left.elts) * count
        if isinstance(node.right, (ast.Tuple, ast.List)):
            count = constant_int_expression(node.left, assignments)
            if count is not None:
                return len(node.right.elts) * count
    if isinstance(node, ast.Name) and node.id in assignments:
        return shape_dimensions(assignments[node.id], assignments)
    return None


def function_ir_kinds(node: ast.FunctionDef | ast.AsyncFunctionDef, allowed: set[str]) -> set[str]:
    result: set[str] = set()
    name = normalized_name(node.name)
    for kind in allowed:
        if re.search(rf"(?:^|_){re.escape(kind)}(?:_|$)", name):
            result.add(kind)

    docstring = ast.get_docstring(node, clean=False) or ""
    for match in re.finditer(r"TT_IR(?:_NODE)?\s*:\s*([a-z0-9_, ]+)", docstring, re.I):
        for item in match.group(1).split(","):
            candidate = normalized_name(item)
            if candidate:
                result.add(candidate)

    for decorator in node.decorator_list:
        if not isinstance(decorator, ast.Call):
            continue
        root, attrs = flatten_attribute(decorator.func)
        decorator_name = ".".join(([root] if root else []) + attrs).lower()
        if decorator_name.endswith(("ir_node", "ir_primitive", "tt_ir_primitive")):
            if decorator.args:
                marker = literal_string(decorator.args[0])
                if marker:
                    result.add(normalized_name(marker))
    for child in ast.walk(node):
        if not isinstance(child, ast.Call) or not child.args:
            continue
        root, attrs = flatten_attribute(child.func)
        if attrs and attrs[-1] in {"_begin_event", "begin_event", "begin_ir_event"}:
            marker = literal_string(child.args[0])
            if marker:
                result.add(normalized_name(marker))
    return result


def function_is_traced_ir_support(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    parameters = {argument.arg for argument in list(node.args.posonlyargs) + list(node.args.args) + list(node.args.kwonlyargs)}
    if "event" not in parameters:
        return False
    charged = False
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            _, attrs = flatten_attribute(child.func)
            if attrs and attrs[-1] in {"_charge_operations", "_charge_traffic", "_finish_event"}:
                if child.args and isinstance(child.args[0], ast.Name) and child.args[0].id == "event":
                    charged = True
    return charged


def expression_has_array_data(node: ast.AST) -> bool:
    for child in ast.walk(node):
        if isinstance(child, ast.Attribute) and child.attr in {"data", "values"}:
            root, _ = flatten_attribute(child)
            if root is not None and any(fragment in normalized_name(root) for fragment in ARRAY_NAME_FRAGMENTS):
                return True
        if isinstance(child, ast.Subscript) and has_arrayish_name(child.value):
            return True
    return False


@dataclass
class FunctionFrame:
    qualname: str
    node: ast.FunctionDef | ast.AsyncFunctionDef
    class_name: str | None
    ir_kinds: set[str]
    assignments: dict[str, ast.AST] = field(default_factory=dict)
    parameters: set[str] = field(default_factory=set)
    traced_ir_support: bool = False
    loop_physical_stack: list[bool] = field(default_factory=list)
    loop_repeat_stack: list[int | None] = field(default_factory=list)
    radix_decode_count: int = 0


class StaticScanner(ast.NodeVisitor):
    def __init__(self, closure: Closure, policy: Policy) -> None:
        self.closure = closure
        self.role = closure.role
        self.policy = policy
        self.allowed_ir = set(policy.allowed_ir_kinds)
        self.module: ModuleInfo | None = None
        self.class_stack: list[str] = []
        self.function_stack: list[FunctionFrame] = []
        self.module_assignments: dict[str, ast.AST] = {}
        self.violations: list[Violation] = list(closure.import_violations)
        self.local_imports: set[tuple[str, str, str]] = set()
        self.external_imports: set[tuple[str, str, str]] = set()
        self.call_edges: set[tuple[str, str, str, int]] = set()
        self.overapprox_call_edges: set[tuple[str, str, str, int]] = set()
        self.ir_primitives: set[tuple[str, str, tuple[str, ...]]] = set()
        self.features: set[tuple[str, str, int, str]] = set()
        self._reported: set[tuple[str, str, int, int, str, str]] = set()
        self.traced_support_definitions = self._collect_traced_support_definitions()

    def _collect_traced_support_definitions(self) -> dict[str, ast.FunctionDef | ast.AsyncFunctionDef]:
        result: dict[str, ast.FunctionDef | ast.AsyncFunctionDef] = {}
        for module in self.closure.modules.values():
            if module.tree is None:
                continue
            for statement in module.tree.body:
                if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if function_is_traced_ir_support(statement):
                        result[f"{module.module_name}.{statement.name}".lstrip(".")] = statement
                elif isinstance(statement, ast.ClassDef):
                    for child in statement.body:
                        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and function_is_traced_ir_support(child):
                            result[f"{module.module_name}.{statement.name}.{child.name}".lstrip(".")] = child
        return result

    @property
    def frame(self) -> FunctionFrame | None:
        return self.function_stack[-1] if self.function_stack else None

    @property
    def assignments(self) -> Mapping[str, ast.AST]:
        return self.frame.assignments if self.frame is not None else self.module_assignments

    @property
    def caller(self) -> str:
        assert self.module is not None
        if self.frame is not None:
            return self.frame.qualname
        return f"{self.module.module_name or '<root>'}::<module>"

    def add_violation(
        self,
        node: ast.AST,
        reason_code: str,
        symbol: str,
        detail: str,
    ) -> None:
        assert self.module is not None
        key = (
            reason_code,
            self.module.relative_path,
            getattr(node, "lineno", 0),
            getattr(node, "col_offset", 0),
            symbol,
            detail,
        )
        if key in self._reported:
            return
        self._reported.add(key)
        self.violations.append(
            Violation(
                role=self.role,
                path=self.module.relative_path,
                line=getattr(node, "lineno", 0),
                column=getattr(node, "col_offset", 0),
                reason_code=reason_code,
                symbol=symbol,
                detail=detail,
            )
        )

    def add_feature(self, node: ast.AST, code: str, detail: str) -> None:
        assert self.module is not None
        self.features.add((self.module.relative_path, code, getattr(node, "lineno", 0), detail))

    def scan(self) -> None:
        for name in sorted(self.closure.modules):
            module = self.closure.modules[name]
            if module.tree is None:
                continue
            self.module = module
            self.module_assignments = {}
            self._audit_raw_source(module)
            self._audit_imports(module)
            self.visit(module.tree)
        if self.role == ROLE_PRODUCER:
            self._audit_producer_call_cycles()
        self.module = None

    def _audit_raw_source(self, module: ModuleInfo) -> None:
        lowered = module.source.lower()
        for fragment in FORBIDDEN_ARTIFACT_FRAGMENTS:
            if fragment not in lowered:
                continue
            verifier_outputs = (
                "frozen-source-advice",
                "frozen-source-control-certificates",
                "source-advice-receipt",
            )
            if self.role == ROLE_VERIFIER and any(item in lowered for item in verifier_outputs) and fragment in verifier_outputs:
                continue
            index = lowered.index(fragment)
            line = module.source.count("\n", 0, index) + 1
            column = index - module.source.rfind("\n", 0, index) - 1
            marker = ast.Constant(value=fragment)
            marker.lineno = line
            marker.col_offset = column
            self.add_violation(
                marker,
                "PHASE_FORBIDDEN_ARTIFACT_SOURCE_TEXT",
                "source-text",
                f"raw source names a withheld or prior artifact (marker_sha256={sha256_bytes(fragment.encode('utf-8'))})",
            )
        for sensitive in sorted(self.policy.sensitive_strings):
            if sensitive not in module.source:
                continue
            index = module.source.index(sensitive)
            line = module.source.count("\n", 0, index) + 1
            column = index - module.source.rfind("\n", 0, index) - 1
            marker = ast.Constant(value=sensitive)
            marker.lineno = line
            marker.col_offset = column
            self.add_violation(
                marker,
                "PHASE_WITHHELD_LITERAL_SOURCE_TEXT",
                "source-text",
                f"raw source contains a withheld target, mutation, or harness digest (literal_sha256={sha256_bytes(sensitive.encode('utf-8'))})",
            )

    def _audit_producer_call_cycles(self) -> None:
        adjacency: dict[str, set[str]] = {}
        edge_location: dict[tuple[str, str], tuple[str, int]] = {}
        local_symbols = {
            value
            for module in self.closure.modules.values()
            for value in module.definitions.values()
        }
        local_prefixes = tuple(sorted(local_symbols))
        for caller, callee, path, line in self.call_edges:
            if (caller, callee, path, line) in self.overapprox_call_edges:
                continue
            if not any(callee == symbol or callee.startswith(symbol + ".") for symbol in local_prefixes):
                continue
            adjacency.setdefault(caller, set()).add(callee)
            edge_location[(caller, callee)] = (path, line)

        visiting: set[str] = set()
        visited: set[str] = set()
        reported: set[tuple[str, ...]] = set()

        def visit(symbol: str, stack: list[str]) -> None:
            if symbol in visiting:
                start = stack.index(symbol) if symbol in stack else 0
                cycle = tuple(stack[start:] + [symbol])
                normalized = tuple(sorted(set(cycle)))
                if normalized not in reported:
                    reported.add(normalized)
                    previous = stack[-1] if stack else symbol
                    path, line = edge_location.get((previous, symbol), (self.closure.entry.name, 0))
                    self.violations.append(
                        Violation(
                            role=self.role,
                            path=path,
                            line=line,
                            column=0,
                            reason_code="CAP_PRODUCER_RECURSION",
                            symbol=" -> ".join(cycle),
                            detail="recursive producer call cycles can implement unbounded generic tuple traversal outside the literal TT schedule",
                        )
                    )
                return
            if symbol in visited:
                return
            visiting.add(symbol)
            stack.append(symbol)
            for target in sorted(adjacency.get(symbol, ())):
                visit(target, stack)
            stack.pop()
            visiting.remove(symbol)
            visited.add(symbol)

        for symbol in sorted(adjacency):
            visit(symbol, [])

    def _audit_imports(self, module: ModuleInfo) -> None:
        assert module.tree is not None
        for node, bound, base, symbol in imported_modules(module):
            imported = f"{base}.{symbol}" if symbol and base else (symbol or base)
            if symbol == "*":
                self.add_violation(
                    node,
                    "IMPORT_WILDCARD",
                    imported,
                    "wildcard imports make the local call closure unprovable",
                )
            binding = module.imports.get(bound)
            if binding is not None and binding.kind.startswith("local"):
                self.local_imports.add((module.relative_path, bound, binding.target))
                self._audit_local_role_import(node, binding.target)
                continue

            self.external_imports.add((module.relative_path, bound, imported))
            root = module_root(base)
            if self._authorized_attestation_import(base):
                self.add_feature(node, "AUTHORIZED_BACKEND_ATTESTATION_IMPORT", imported)
            elif matches_module_set(base, self.policy.forbidden_import_roots):
                code = "CAP_FORBIDDEN_IMPORT"
                if matches_module_set(base, DYNAMIC_MODULE_ROOTS):
                    code = "CAP_DYNAMIC_IMPORT"
                elif matches_module_set(base, NETWORK_MODULE_ROOTS):
                    code = "CAP_NETWORK_IMPORT"
                elif matches_module_set(base, ESCAPE_MODULE_ROOTS):
                    code = "CAP_BACKEND_ESCAPE_IMPORT"
                elif matches_module_set(base, FILESYSTEM_OR_OUTPUT_MODULE_ROOTS):
                    code = "CAP_FILESYSTEM_CAPABILITY_IMPORT"
                self.add_violation(node, code, imported, "module is outside the reviewed source capability closure")
            elif root in {"multiprocessing", "pty"}:
                self.add_violation(node, "CAP_CHILD_PROCESS_IMPORT", imported, "child-process module is forbidden")
            elif root == "numpy" and self.role == ROLE_VERIFIER:
                self.add_violation(
                    node,
                    "NUMPY_VERIFIER_IMPORT",
                    imported,
                    "the independent verifier backend is Python arbitrary-precision integer code",
                )
            elif root != "numpy" and root not in sys.stdlib_module_names and root != "__future__":
                self.add_violation(
                    node,
                    "IMPORT_UNBOUND_EXTERNAL",
                    imported,
                    "third-party dependency is outside the pinned Python/NumPy closure",
                )

    def _in_attestation_module(self) -> bool:
        return self.module is not None and self.module.path.name == "attest_tt_backend.py"

    def _authorized_attestation_import(self, name: str) -> bool:
        return self.role == ROLE_PRODUCER and self._in_attestation_module() and name in {
            "ctypes",
            "importlib.metadata",
        }

    def _in_attestation_function(self, *names: str) -> bool:
        return (
            self.role == ROLE_PRODUCER
            and self._in_attestation_module()
            and self.frame is not None
            and self.frame.node.name in set(names)
        )

    def _audit_local_role_import(self, node: ast.AST, target: str) -> None:
        lowered = normalized_name(target)
        fragments = (
            PRODUCER_FORBIDDEN_LOCAL_FRAGMENTS
            if self.role == ROLE_PRODUCER
            else VERIFIER_FORBIDDEN_LOCAL_FRAGMENTS
        )
        if any(fragment in lowered for fragment in fragments):
            self.add_violation(
                node,
                "ROLE_FORBIDDEN_LOCAL_IMPORT",
                target,
                f"{self.role} closure imports a module reserved for the other phase or the harness",
            )

    def visit_ClassDef(self, node: ast.ClassDef) -> Any:
        self.class_stack.append(node.name)
        for decorator in node.decorator_list:
            self._audit_bare_decorator(decorator)
            self.visit(decorator)
        for base in node.bases:
            self.visit(base)
        for keyword in node.keywords:
            self.visit(keyword.value)
        for statement in node.body:
            self.visit(statement)
        self.class_stack.pop()
        return None

    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        return self._visit_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> Any:
        self.add_violation(
            node,
            "CAP_ASYNC_CODE",
            node.name,
            "async execution is outside the deterministic single-process source closure",
        )
        return self._visit_function(node)

    def _visit_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        assert self.module is not None
        if self.function_stack:
            self.add_violation(
                node,
                "CAP_NESTED_CODE",
                node.name,
                "nested function definitions obscure the static local call closure",
            )
        kinds = function_ir_kinds(node, self.allowed_ir)
        unknown = kinds - self.allowed_ir
        for kind in sorted(unknown):
            self.add_violation(node, "IR_UNKNOWN_NODE_KIND", kind, "IR marker is not in the closed ten-node vocabulary")
        parameters = {
            argument.arg
            for argument in (
                list(node.args.posonlyargs)
                + list(node.args.args)
                + list(node.args.kwonlyargs)
            )
        }
        if node.args.vararg is not None:
            parameters.add(node.args.vararg.arg)
        if node.args.kwarg is not None:
            parameters.add(node.args.kwarg.arg)
        qualname_parts = [self.module.module_name] if self.module.module_name else []
        qualname_parts.extend(self.class_stack)
        qualname_parts.append(node.name)
        frame = FunctionFrame(
            qualname=".".join(qualname_parts),
            node=node,
            class_name=self.class_stack[-1] if self.class_stack else None,
            ir_kinds=kinds,
            parameters=parameters,
            traced_ir_support=function_is_traced_ir_support(node),
        )
        if kinds:
            self.ir_primitives.add((self.module.relative_path, frame.qualname, tuple(sorted(kinds))))
            mode_parameters = [name for name in parameters if MODE_NAME_RE.fullmatch(name)]
            slice_parameters = [name for name in parameters if SLICE_NAME_RE.fullmatch(name)]
            plural_parameters = [name for name in parameters if normalized_name(name) in {"modes", "slices"}]
            if len(mode_parameters) > 1 or len(slice_parameters) > 1 or plural_parameters:
                self.add_violation(
                    node,
                    "IR_MULTI_PHYSICAL_ARGUMENT",
                    frame.qualname,
                    "an IR primitive may receive at most one physical mode and one physical slice",
                )

        for decorator in node.decorator_list:
            self._audit_bare_decorator(decorator)
            self.visit(decorator)
        for default in list(node.args.defaults) + [item for item in node.args.kw_defaults if item]:
            self.visit(default)
        self.function_stack.append(frame)
        for statement in node.body:
            self.visit(statement)
        if frame.radix_decode_count >= 5:
            if self.role == ROLE_PRODUCER:
                self.add_violation(
                    node,
                    "ENUM_RADIX_DECODE_5",
                    frame.qualname,
                    "five or more base-B radix steps occur in one producer function",
                )
            else:
                self.add_feature(node, "VERIFIER_RADIX_ENUMERATION", "explicit verifier radix traversal observed")
        self.function_stack.pop()

    def _audit_bare_decorator(self, node: ast.AST) -> None:
        if isinstance(node, ast.Call):
            return
        resolved = self.resolve_callable(node)
        display = self._call_display(node)
        if resolved is None:
            self.add_violation(node, "CAP_UNBOUND_HELPER", display, "decorator cannot be bound inside the static source closure")
            return
        kind, target = resolved
        if kind == "local":
            assert self.module is not None
            self.call_edges.add((self.caller, target, self.module.relative_path, getattr(node, "lineno", 0)))

    def visit_Lambda(self, node: ast.Lambda) -> Any:
        self.add_feature(node, "STATIC_LAMBDA_AUDITED", "lambda body is included in the AST closure")
        self.generic_visit(node)
        return None

    def visit_Assign(self, node: ast.Assign) -> Any:
        self.visit(node.value)
        for target in node.targets:
            self.visit(target)
            if self.role == ROLE_PRODUCER and self._target_is_array_storage(target):
                self._require_ir_owner(
                    node,
                    "IR_ARRAY_WRITE_OUTSIDE_CLOSED_IR",
                    self._call_display(target),
                    allow_multiple=True,
                )
            if isinstance(target, ast.Name):
                self._audit_callable_alias(node, target.id, node.value)
                if not isinstance(node.value, (ast.Lambda, ast.Yield, ast.YieldFrom)):
                    if self.frame is not None:
                        self.frame.assignments[target.id] = node.value
                    else:
                        self.module_assignments[target.id] = node.value
        return None

    def visit_AnnAssign(self, node: ast.AnnAssign) -> Any:
        self.visit(node.annotation)
        if node.value is not None:
            self.visit(node.value)
        self.visit(node.target)
        if self.role == ROLE_PRODUCER and self._target_is_array_storage(node.target):
            self._require_ir_owner(
                node,
                "IR_ARRAY_WRITE_OUTSIDE_CLOSED_IR",
                self._call_display(node.target),
                allow_multiple=True,
            )
        if isinstance(node.target, ast.Name) and node.value is not None:
            self._audit_callable_alias(node, node.target.id, node.value)
            if self.frame is not None:
                self.frame.assignments[node.target.id] = node.value
            else:
                self.module_assignments[node.target.id] = node.value
        return None

    def _target_is_array_storage(self, target: ast.AST) -> bool:
        if isinstance(target, ast.Attribute):
            return target.attr == "data" and has_arrayish_name(target.value)
        if not isinstance(target, ast.Subscript):
            return False
        base = target.value
        if isinstance(base, ast.Attribute) and base.attr == "data":
            return True
        if isinstance(base, ast.Name):
            assigned = self.assignments.get(base.id)
            if assigned is not None and self._is_builtin_container_expression(assigned):
                return False
            if any(fragment in normalized_name(base.id) for fragment in ARRAY_NAME_FRAGMENTS):
                return True
            return assigned is not None and expression_has_array_data(assigned)
        return expression_has_array_data(base)

    def _is_builtin_container_expression(self, node: ast.AST) -> bool:
        if isinstance(node, (ast.Dict, ast.DictComp, ast.List, ast.ListComp, ast.Set, ast.SetComp, ast.Tuple)):
            return True
        if isinstance(node, ast.Call):
            resolved = self.resolve_callable(node.func)
            return resolved is not None and resolved[0] == "builtin" and resolved[1] in {
                "dict",
                "frozenset",
                "list",
                "set",
                "tuple",
            }
        return False

    def _audit_callable_alias(self, node: ast.AST, target: str, value: ast.AST) -> None:
        if not isinstance(value, (ast.Name, ast.Attribute)):
            return
        resolved = self.resolve_callable(value)
        if resolved is not None and resolved[0] in {"local", "external"}:
            self.add_violation(
                node,
                "CAP_CALLABLE_ALIAS",
                target,
                "callable rebinding obscures the reviewed import and call graph",
            )

    def resolve_callable(self, node: ast.AST) -> tuple[str, str] | None:
        assert self.module is not None
        if isinstance(node, ast.Name):
            if node.id in self.module.definitions:
                return "local", self.module.definitions[node.id]
            binding = self.module.imports.get(node.id)
            if binding is not None:
                kind = "local" if binding.kind.startswith("local") else "external"
                return kind, binding.target
            if node.id in SAFE_BUILTIN_CALLS or node.id in DYNAMIC_CALL_NAMES or node.id in FORBIDDEN_NUMERIC_BUILTINS or node.id == "open":
                return "builtin", node.id
            if node.id in {"Exception", "RuntimeError", "ValueError", "AssertionError", "TypeError", "KeyError", "IndexError", "OSError", "SystemExit"}:
                return "builtin", node.id
            return None
        if isinstance(node, ast.Attribute):
            root, attrs = flatten_attribute(node)
            if root is not None:
                binding = self.module.imports.get(root)
                if binding is not None:
                    target = ".".join((binding.target, *attrs))
                    kind = "local" if binding.kind.startswith("local") else "external"
                    return kind, target
                if root == "self" and self.frame is not None and self.frame.class_name:
                    methods = self.module.class_methods.get(self.frame.class_name, set())
                    if attrs and attrs[-1] in methods:
                        prefix = f"{self.module.module_name}.{self.frame.class_name}".lstrip(".")
                        return "local", f"{prefix}.{attrs[-1]}"
            if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name) and node.value.func.id == "super":
                return "method", attrs[-1] if attrs else node.attr
            if attrs:
                candidates = self._local_method_candidates(attrs[-1])
                if candidates:
                    return "local_method_set", "|".join(candidates)
            if attrs and attrs[-1] in SAFE_UNKNOWN_METHODS | NUMPY_ALLOWED_METHODS | NUMPY_FORBIDDEN_METHODS | WRITE_METHOD_NAMES:
                return "method", attrs[-1]
            return None
        return None

    def _local_method_candidates(self, method: str) -> list[str]:
        candidates: list[str] = []
        for module in self.closure.modules.values():
            for class_name, methods in module.class_methods.items():
                if method in methods:
                    prefix = f"{module.module_name}.{class_name}".lstrip(".")
                    candidates.append(f"{prefix}.{method}")
        return sorted(candidates)

    def visit_Call(self, node: ast.Call) -> Any:
        resolved = self.resolve_callable(node.func)
        display = self._call_display(node.func)
        self._audit_capability_name(node, display)
        self._audit_cli_path_option(node, display)
        self._audit_syntactic_array_method(node)
        if resolved is None:
            if self._authorized_attestation_unbound_call(display):
                self.add_feature(node, "AUTHORIZED_BACKEND_ATTESTATION_CALL", display)
            else:
                self.add_violation(
                    node,
                    "CAP_UNBOUND_HELPER",
                    display,
                    "call target cannot be bound to a local definition, reviewed external import, builtin, or safe value method",
                )
        else:
            kind, target = resolved
            if kind == "local":
                self._audit_local_call(node, target)
            elif kind == "local_method_set":
                for candidate in target.split("|"):
                    self._audit_local_call(node, candidate, overapprox=True)
            elif kind == "external":
                self._audit_external_call(node, target)
            elif kind == "builtin":
                self._audit_builtin_call(node, target)
            elif kind == "method":
                self._audit_method_call(node, target)

        self._audit_product_call(node, resolved, display)
        self._audit_b5_call(node, resolved, display)
        self._audit_radix_call(node, resolved, display)
        for keyword in node.keywords:
            self._audit_dtype_keyword(node, keyword)
        self.generic_visit(node)
        return None

    def _audit_cli_path_option(self, node: ast.Call, display: str) -> None:
        if display.rsplit(".", 1)[-1] != "add_argument" or not node.args:
            return
        options = [literal_string(argument) for argument in node.args]
        option_names = {item for item in options if item and item.startswith("--")}
        if not option_names:
            return
        type_keyword = next((keyword.value for keyword in node.keywords if keyword.arg == "type"), None)
        path_typed = False
        if type_keyword is not None:
            resolved = self.resolve_callable(type_keyword)
            path_typed = resolved is not None and resolved[1].endswith("pathlib.Path")
        pathish_name = any(
            any(fragment in option for fragment in ("artifact", "file", "manifest", "matrix", "output", "path", "result"))
            for option in option_names
        )
        if not path_typed and not pathish_name:
            return
        allowed = PRODUCER_ALLOWED_PATH_OPTIONS if self.role == ROLE_PRODUCER else VERIFIER_ALLOWED_PATH_OPTIONS
        forbidden = sorted(option_names - allowed)
        if forbidden:
            self.add_violation(
                node,
                "CAP_CLI_DATA_INPUT_OUTSIDE_ALLOWLIST",
                ",".join(forbidden),
                "path-valued CLI option is outside the role's frozen data-read allowlist",
            )

    def _audit_syntactic_array_method(self, node: ast.Call) -> None:
        if self.role != ROLE_PRODUCER or not isinstance(node.func, ast.Attribute):
            return
        method = node.func.attr
        receiver = node.func.value
        array_receiver = expression_has_array_data(receiver) or has_arrayish_name(receiver)
        if method == "reshape" and array_receiver:
            self._audit_reshape_call(node)
        elif method in NUMPY_FORBIDDEN_METHODS and array_receiver:
            self.add_violation(node, "NUMPY_FORBIDDEN_API", method, "array method is outside the reviewed dense-kernel allowlist")

    def _audit_capability_name(self, node: ast.Call, display: str) -> None:
        lowered = display.lower()
        last = lowered.rsplit(".", 1)[-1]
        if last in NETWORK_CALL_NAMES:
            self.add_violation(node, "CAP_NETWORK", display, "network-capability method is forbidden even when receiver type is unresolved")
        if last in PROCESS_CALL_NAMES and ("." not in lowered or lowered.startswith(("os.", "subprocess.", "multiprocessing.", "pty."))):
            self.add_violation(node, "CAP_CHILD_PROCESS", display, "child-process capability is forbidden")

    def _call_display(self, node: ast.AST) -> str:
        if isinstance(node, ast.Name):
            return node.id
        root, attrs = flatten_attribute(node)
        if root is not None:
            return ".".join((root, *attrs))
        return node.__class__.__name__

    def _audit_local_call(self, node: ast.Call, target: str, *, overapprox: bool = False) -> None:
        assert self.module is not None
        target_module = target.rsplit(".", 1)[0] if "." in target else ""
        target_symbol = target.rsplit(".", 1)[-1]
        info = self.closure.modules.get(target_module)
        locally_bound = False
        if info is not None:
            locally_bound = target_symbol in info.definitions
        if not locally_bound:
            for module in self.closure.modules.values():
                if target in module.definitions.values():
                    locally_bound = True
                    break
                if any(target.startswith(value + ".") for value in module.definitions.values()):
                    locally_bound = True
                    break
        if not locally_bound:
            self.add_violation(
                node,
                "CAP_UNBOUND_LOCAL_HELPER",
                target,
                "local imported call target has no statically bound definition in the hashed closure",
            )
        if not overapprox and target in self.traced_support_definitions:
            event_values = list(node.args) + [
                keyword.value for keyword in node.keywords if keyword.arg == "event"
            ]
            if not any(self._is_bound_ir_event(value) for value in event_values):
                self.add_violation(
                    node,
                    "IR_UNBOUND_SUPPORT_EVENT",
                    target,
                    "traced NumPy support helper is called without an event derived from a closed-IR begin event",
                )
        edge = (self.caller, target, self.module.relative_path, node.lineno)
        self.call_edges.add(edge)
        if overapprox:
            self.overapprox_call_edges.add(edge)

    def _is_bound_ir_event(self, node: ast.AST) -> bool:
        if isinstance(node, ast.Name):
            if self.frame is not None and node.id == "event" and (
                self.frame.traced_ir_support or bool(self.frame.ir_kinds)
            ):
                return True
            assigned = self.assignments.get(node.id)
            if assigned is not None:
                return self._is_bound_ir_event(assigned)
            return False
        if not isinstance(node, ast.Call) or not node.args:
            return False
        _, attrs = flatten_attribute(node.func)
        if not attrs or attrs[-1] not in {"_begin_event", "begin_event", "begin_ir_event"}:
            return False
        marker = literal_string(node.args[0])
        return marker is not None and normalized_name(marker) in self.allowed_ir

    def _audit_external_call(self, node: ast.Call, target: str) -> None:
        lowered = target.lower()
        last = lowered.rsplit(".", 1)[-1]
        root = module_root(lowered)
        if matches_module_set(lowered, DYNAMIC_MODULE_ROOTS) or last in DYNAMIC_CALL_NAMES:
            if self._authorized_attestation_dynamic_call(node, target):
                self.add_feature(node, "AUTHORIZED_BACKEND_ATTESTATION_INTROSPECTION", target)
            else:
                self.add_violation(node, "CAP_DYNAMIC_CODE", target, "dynamic import, code, or attribute dispatch is forbidden")
        os_process_call = root == "os" and last in PROCESS_CALL_NAMES
        if os_process_call or root in {"multiprocessing", "pty", "subprocess"}:
            self.add_violation(node, "CAP_CHILD_PROCESS", target, "child-process execution is forbidden")
        if last in NETWORK_CALL_NAMES or matches_module_set(lowered, NETWORK_MODULE_ROOTS):
            self.add_violation(node, "CAP_NETWORK", target, "network access is forbidden")
        if root == "numpy":
            self._audit_numpy_call(node, target)
        if root == "ctypes" and target != "ctypes.CDLL":
            self.add_violation(node, "CAP_BACKEND_ESCAPE", target, "ctypes calls are forbidden outside the exact dyld image-registry entry point")
        if target == "ctypes.CDLL" or lowered.endswith(".cdll"):
            if self._authorized_dyld_call(node):
                self.add_feature(node, "AUTHORIZED_DYLD_IMAGE_REGISTRY", target)
            else:
                self.add_violation(node, "CAP_BACKEND_ESCAPE", target, "native-library loading is forbidden outside backend attestation")
        if "importlib.metadata" in lowered and lowered.endswith(".distribution"):
            allowed = (
                self._in_attestation_function("numpy_distribution_closure")
                and len(node.args) == 1
                and literal_string(node.args[0]) == "numpy"
            )
            if not allowed:
                self.add_violation(node, "CAP_DYNAMIC_IMPORT", target, "distribution lookup is authorized only for the pinned NumPy closure")
        if last in WRITE_METHOD_NAMES and not self._is_stdout_method(node):
            self.add_violation(node, "CAP_FILESYSTEM_WRITE", target, "audited source processes emit JSON only to stdout")
        if last in DIRECTORY_ENUMERATION_NAMES:
            self.add_violation(node, "CAP_DIRECTORY_ENUMERATION", target, "source code may not enumerate directories")
        if lowered in {"json.dump", "json.dump_json"}:
            if len(node.args) < 2 or not self._is_stdout_expression(node.args[1]):
                self.add_violation(node, "CAP_FILESYSTEM_WRITE", target, "json.dump is allowed only with sys.stdout")
        self._audit_environment_call(node, target)
        self._audit_file_call(node, target)

    def _authorized_attestation_dynamic_call(self, node: ast.Call, target: str) -> bool:
        if (
            target == "getattr"
            and self._in_attestation_function("loaded_numpy_extensions")
            and len(node.args) >= 2
            and literal_string(node.args[1]) == "__file__"
        ):
            return True
        lowered = target.lower()
        return (
            "importlib.metadata" in lowered
            and lowered.endswith(".distribution")
            and self._in_attestation_function("numpy_distribution_closure")
            and len(node.args) == 1
            and literal_string(node.args[0]) == "numpy"
        )

    def _authorized_attestation_unbound_call(self, display: str) -> bool:
        if self._in_attestation_function("numpy_distribution_closure") and display == "distribution.locate_file":
            return True
        if self._in_attestation_function("loaded_dyld_images") and display in {
            "process._dyld_get_image_name",
            "process._dyld_image_count",
        }:
            return True
        return False

    def _authorized_dyld_call(self, node: ast.Call) -> bool:
        return (
            self._in_attestation_function("loaded_dyld_images")
            and len(node.args) == 1
            and isinstance(node.args[0], ast.Constant)
            and node.args[0].value is None
        )

    def _audit_builtin_call(self, node: ast.Call, target: str) -> None:
        if target in DYNAMIC_CALL_NAMES:
            if self._authorized_attestation_dynamic_call(node, target):
                self.add_feature(node, "AUTHORIZED_BACKEND_ATTESTATION_INTROSPECTION", target)
            else:
                self.add_violation(node, "CAP_DYNAMIC_CODE", target, "dynamic code and dynamic attribute dispatch are forbidden")
        elif target in FORBIDDEN_NUMERIC_BUILTINS:
            self.add_violation(node, "NUMERIC_FLOAT_OR_COMPLEX", target, "floating-point and complex conversion are forbidden")
        elif target == "open":
            self._audit_open_call(node, target, path_node=node.args[0] if node.args else None)
        elif target == "print":
            self.add_violation(node, "CAP_NONCANONICAL_OUTPUT", target, "print is forbidden; emit exactly one canonical JSON object through the reviewed stdout path")

    def _audit_method_call(self, node: ast.Call, method: str) -> None:
        lowered = method.lower()
        if lowered in WRITE_METHOD_NAMES:
            if not self._is_stdout_method(node):
                self.add_violation(node, "CAP_FILESYSTEM_WRITE", method, "audited source processes emit JSON only to stdout")
        if lowered in DIRECTORY_ENUMERATION_NAMES:
            self.add_violation(node, "CAP_DIRECTORY_ENUMERATION", method, "source code may not enumerate directories")
        if lowered == "open":
            receiver = node.func.value if isinstance(node.func, ast.Attribute) else None
            self._audit_open_call(node, method, path_node=receiver, method_call=True)
        elif lowered in {"read_bytes", "read_text", "stat", "is_file"}:
            receiver = node.func.value if isinstance(node.func, ast.Attribute) else None
            self._audit_path_read(node, method, receiver)
        if self.role == ROLE_PRODUCER and lowered in NUMPY_FORBIDDEN_METHODS:
            self.add_violation(node, "NUMPY_FORBIDDEN_API", method, "ndarray method is outside the reviewed dense-kernel allowlist")
        if lowered == "reshape":
            self._audit_reshape_call(node)

    def _is_stdout_expression(self, node: ast.AST) -> bool:
        root, attrs = flatten_attribute(node)
        return root == "sys" and attrs in (["stdout"], ["stdout", "buffer"])

    def _is_stdout_method(self, node: ast.Call) -> bool:
        if not isinstance(node.func, ast.Attribute):
            return False
        root, attrs = flatten_attribute(node.func.value)
        return root == "sys" and attrs[:1] == ["stdout"]

    def _audit_open_call(
        self,
        node: ast.Call,
        symbol: str,
        path_node: ast.AST | None,
        method_call: bool = False,
    ) -> None:
        mode_node: ast.AST | None = None
        if method_call:
            if node.args:
                mode_node = node.args[0]
        elif len(node.args) >= 2:
            mode_node = node.args[1]
        for keyword in node.keywords:
            if keyword.arg == "mode":
                mode_node = keyword.value
        mode = literal_string(mode_node) if mode_node is not None else "r"
        if mode is None:
            self.add_violation(node, "CAP_DYNAMIC_FILE_MODE", symbol, "file mode must be a static read-only literal")
        elif any(character in mode for character in "wax+"):
            self.add_violation(node, "CAP_FILESYSTEM_WRITE", symbol, "file writes are forbidden by the stdout-only boundary")
        self._audit_path_read(node, symbol, path_node)

    def _audit_path_read(self, node: ast.AST, symbol: str, path_node: ast.AST | None) -> None:
        if self._authorized_attestation_file_read(symbol):
            self.add_feature(node, "AUTHORIZED_BACKEND_ATTESTATION_READ", symbol)
            return
        path = self._extract_path_literal(path_node)
        if path is None:
            self.add_feature(node, "RUNTIME_PATH_GATE_REQUIRED", f"{symbol} uses a nonliteral path")
            return
        basename = Path(path).name
        allowed = PRODUCER_ALLOWED_DATA if self.role == ROLE_PRODUCER else VERIFIER_ALLOWED_DATA
        if basename not in allowed:
            digest = sha256_bytes(path.encode("utf-8"))
            self.add_violation(
                node,
                "CAP_DATA_READ_OUTSIDE_ALLOWLIST",
                symbol,
                f"literal input path is outside the role allowlist (literal_sha256={digest})",
            )

    def _authorized_attestation_file_read(self, symbol: str) -> bool:
        if not self._in_attestation_module():
            return False
        return self.frame is not None and self.frame.node.name in {
            "build_attestation",
            "load_source_matrix",
            "loaded_numpy_extensions",
            "numpy_distribution_closure",
            "sha256_file",
        }

    def _extract_path_literal(self, node: ast.AST | None) -> str | None:
        if node is None:
            return None
        direct = literal_string(node)
        if direct is not None:
            return direct
        if isinstance(node, ast.Call):
            resolved = self.resolve_callable(node.func)
            if resolved and resolved[1].endswith("Path") and node.args:
                return literal_string(node.args[0])
        if isinstance(node, ast.Name) and node.id in self.assignments:
            return self._extract_path_literal(self.assignments[node.id])
        return None

    def _audit_environment_call(self, node: ast.Call, target: str) -> None:
        lowered = target.lower()
        if lowered not in {"os.getenv", "os.environ.get"}:
            return
        key = literal_string(node.args[0]) if node.args else None
        if key is None:
            if self._authorized_attestation_environment_read():
                self.add_feature(node, "AUTHORIZED_BACKEND_ATTESTATION_ENVIRONMENT", "six-key attestation allowlist")
            else:
                self.add_violation(node, "CAP_DYNAMIC_ENVIRONMENT_READ", target, "environment key must be a frozen literal")
        elif key not in self.policy.environment_allowlist:
            self.add_violation(node, "CAP_ENVIRONMENT_READ", target, "environment key is outside the six-key allowlist")

    def _authorized_attestation_environment_read(self) -> bool:
        if not self._in_attestation_function("build_attestation") or self.module is None:
            return False
        expected = tuple(self.policy.environment_allowlist)
        for statement in self.module.tree.body if self.module.tree is not None else ():
            if isinstance(statement, ast.Assign) and any(
                isinstance(target, ast.Name) and target.id == "THREAD_ENVIRONMENT"
                for target in statement.targets
            ):
                if isinstance(statement.value, (ast.Tuple, ast.List)):
                    observed = tuple(literal_string(item) for item in statement.value.elts)
                    return tuple(sorted(item for item in observed if item is not None)) == expected
        return False

    def _audit_file_call(self, node: ast.Call, target: str) -> None:
        lowered = target.lower()
        if lowered in {"pathlib.path.read_bytes", "pathlib.path.read_text", "pathlib.path.stat"}:
            path_node = node.func.value if isinstance(node.func, ast.Attribute) else None
            self._audit_path_read(node, target, path_node)

    def _audit_numpy_call(self, node: ast.Call, target: str) -> None:
        if self.role == ROLE_VERIFIER:
            self.add_violation(node, "NUMPY_VERIFIER_USE", target, "independent verifier may not use the producer NumPy backend")
            return
        lowered = target.lower()
        if ".linalg" in lowered:
            self.add_violation(node, "NUMPY_FORBIDDEN_API", target, "np.linalg is prohibited")
        name = lowered.rsplit(".", 1)[-1]
        if name == "dtype":
            if len(node.args) != 1 or not self._is_int64_dtype_expression(node.args[0]):
                self.add_violation(node, "NUMPY_FORBIDDEN_DTYPE", target, "np.dtype is authorized only for signed int64 metadata checks")
            return
        allowed = set(self.policy.allowed_numpy_functions) | {"reshape"}
        if name not in allowed:
            self.add_violation(node, "NUMPY_FORBIDDEN_API", target, "NumPy call is outside the reviewed dense-kernel allowlist")
        if name in NUMPY_ALLOCATION_FUNCTIONS or name == "reshape":
            self._audit_numpy_shape(node, name, function_style=True)
            if name == "reshape":
                self.add_feature(node, "RESHAPE_REQUIRES_RUNTIME_VIEW_PROOF", "static audit accepts reshape_C; allocation identity must be reconciled at runtime")
            else:
                self._require_ir_owner(node, "IR_ALLOCATION_OUTSIDE_CLOSED_IR", target)
        if name in NUMPY_ARITHMETIC_FUNCTIONS:
            self._require_ir_owner(node, "IR_ARITHMETIC_OUTSIDE_CLOSED_IR", target)
        if name in {"empty", "zeros"}:
            dtype_keyword = next((item for item in node.keywords if item.arg == "dtype"), None)
            if dtype_keyword is None:
                self.add_violation(node, "NUMPY_DTYPE_UNPROVEN", target, "allocation must state dtype=np.int64 explicitly")
        self._audit_c_order(node, name)

    def _audit_reshape_call(self, node: ast.Call) -> None:
        if self.role == ROLE_PRODUCER:
            self._audit_numpy_shape(node, "reshape", function_style=False)
            self.add_feature(node, "RESHAPE_REQUIRES_RUNTIME_VIEW_PROOF", "static audit accepts reshape_C; allocation identity must be reconciled at runtime")
            self._audit_c_order(node, "reshape")

    def _audit_numpy_shape(self, node: ast.Call, name: str, function_style: bool) -> None:
        shape_node: ast.AST | None = None
        explicit_dimensions: int | None = None
        if name == "reshape":
            if function_style:
                shape_args = node.args[1:]
            else:
                shape_args = node.args
            if len(shape_args) == 1:
                shape_node = shape_args[0]
            elif len(shape_args) > 1:
                explicit_dimensions = len(shape_args)
        elif node.args:
            shape_node = node.args[0]
        dimensions = explicit_dimensions
        if dimensions is None and shape_node is not None:
            dimensions = shape_dimensions(shape_node, self.assignments)
        if dimensions is None and shape_node is not None and self._shape_is_guarded(shape_node):
            self.add_feature(node, "STATIC_ARRAY_DIMENSION_GUARD", "shape length is refused above the reviewed maximum before allocation")
        elif dimensions is None:
            self.add_violation(
                node,
                "ARRAY_DIMENSION_UNPROVEN",
                name,
                "static audit cannot prove that the array has at most three dimensions",
            )
        elif dimensions > self.policy.maximum_ndarray_dimensions:
            code = "ARRAY_FIVE_DIMENSIONAL" if dimensions >= 5 else "ARRAY_DIMENSION_LIMIT"
            self.add_violation(
                node,
                code,
                name,
                f"array has {dimensions} dimensions; reviewed maximum is {self.policy.maximum_ndarray_dimensions}",
            )

    def _shape_is_guarded(self, shape_node: ast.AST) -> bool:
        if self.frame is None or not isinstance(shape_node, ast.Name):
            return False
        shape_name = shape_node.id
        for statement in ast.walk(self.frame.node):
            if not isinstance(statement, ast.If) or not isinstance(statement.test, ast.Compare):
                continue
            child = statement.test
            if len(child.ops) != 1 or len(child.comparators) != 1:
                continue
            if not isinstance(child.left, ast.Call) or not isinstance(child.left.func, ast.Name) or child.left.func.id != "len":
                continue
            if len(child.left.args) != 1 or not isinstance(child.left.args[0], ast.Name) or child.left.args[0].id != shape_name:
                continue
            boundary = literal_int(child.comparators[0])
            threshold_matches = (
                isinstance(child.ops[0], ast.Gt) and boundary == self.policy.maximum_ndarray_dimensions
            ) or (
                isinstance(child.ops[0], ast.GtE) and boundary == self.policy.maximum_ndarray_dimensions + 1
            )
            if not threshold_matches:
                continue
            refuses = any(
                isinstance(body_node, ast.Raise)
                or (
                    isinstance(body_node, ast.Call)
                    and self._call_display(body_node.func).rsplit(".", 1)[-1] in {"_refuse", "reject"}
                )
                for body_statement in statement.body
                for body_node in ast.walk(body_statement)
            )
            if refuses:
                return True
        return False

    def _is_int64_dtype_expression(self, node: ast.AST) -> bool:
        text = literal_string(node)
        if text is not None:
            return text.lower() in ALLOWED_INT64_DTYPE_STRINGS
        if isinstance(node, (ast.Name, ast.Attribute)):
            resolved = self.resolve_callable(node)
            return resolved is not None and resolved[1].lower() == "numpy.int64"
        return False

    def _audit_dtype_keyword(self, call: ast.Call, keyword: ast.keyword) -> None:
        if keyword.arg != "dtype":
            return
        valid = False
        text = literal_string(keyword.value)
        if text is not None:
            valid = text.lower() in ALLOWED_INT64_DTYPE_STRINGS
        elif isinstance(keyword.value, (ast.Name, ast.Attribute)):
            resolved = self.resolve_callable(keyword.value)
            valid = resolved is not None and resolved[1].lower() == "numpy.int64"
        if not valid:
            self.add_violation(call, "NUMPY_FORBIDDEN_DTYPE", "dtype", "only signed NumPy int64 is allowed")

    def _audit_c_order(self, node: ast.Call, symbol: str) -> None:
        for keyword in node.keywords:
            if keyword.arg == "order" and literal_string(keyword.value) != "C":
                self.add_violation(node, "NUMPY_NON_C_ORDER", symbol, "dense arrays and reshapes must use C order")

    def _require_ir_owner(
        self,
        node: ast.AST,
        reason_code: str,
        symbol: str,
        *,
        allow_multiple: bool = False,
    ) -> None:
        if self.role != ROLE_PRODUCER:
            return
        kinds = self.frame.ir_kinds if self.frame is not None else set()
        if len(kinds) == 1 and kinds <= self.allowed_ir:
            return
        if allow_multiple and kinds and kinds <= self.allowed_ir:
            if len(kinds) > 1:
                self.add_feature(node, "MULTI_IR_INTERPRETER_WRITE", self.frame.qualname if self.frame else symbol)
            return
        if self.frame is not None and self.frame.traced_ir_support:
            self.add_feature(node, "TRACED_IR_SUPPORT_HELPER", self.frame.qualname)
            return
        if len(kinds) > 1:
            detail = "allocation or arithmetic path has multiple static IR owners"
        else:
            detail = "allocation or arithmetic path has no explicit closed-IR owner; use an IR-named function, TT_IR docstring marker, or audited IR decorator"
        self.add_violation(node, reason_code, symbol, detail)

    def _audit_product_call(
        self,
        node: ast.Call,
        resolved: tuple[str, str] | None,
        display: str,
    ) -> None:
        target = resolved[1] if resolved is not None else display
        if target.rsplit(".", 1)[-1] != "product":
            return
        repeat = next((literal_int(keyword.value) for keyword in node.keywords if keyword.arg == "repeat"), None)
        if repeat == 5:
            if self.role == ROLE_PRODUCER:
                self.add_violation(node, "ENUM_PRODUCT_REPEAT_5", target, "five-source Cartesian product is forbidden in the producer")
            else:
                self.add_violation(node, "ENUM_GENERIC_TUPLE_ITERATOR", target, "verifier enumeration must use a dedicated explicit traversal, not a generic product helper")

    def _audit_b5_call(
        self,
        node: ast.Call,
        resolved: tuple[str, str] | None,
        display: str,
    ) -> None:
        target = resolved[1] if resolved is not None else display
        if target.rsplit(".", 1)[-1] != "range" or not node.args:
            return
        stop = node.args[-1]
        degree = b_degree(stop, self.assignments)
        constant = constant_int_expression(stop, self.assignments)
        literal_b5 = constant in {value**5 for value in self.policy.source_b_values}
        if degree == 5 or literal_b5:
            if self.role == ROLE_PRODUCER:
                code = "ENUM_B5_TRAVERSAL" if degree == 5 else "ENUM_CONSTANT_FOLDED_B5"
                self.add_violation(node, code, target, "producer may not traverse a flattened B^5 physical table")
            else:
                self.add_feature(node, "VERIFIER_B5_ENUMERATION", "independent verifier enumeration observed")

    def _audit_radix_call(
        self,
        node: ast.Call,
        resolved: tuple[str, str] | None,
        display: str,
    ) -> None:
        target = resolved[1] if resolved is not None else display
        if target.rsplit(".", 1)[-1] != "divmod" or len(node.args) < 2:
            return
        if b_degree(node.args[1], self.assignments) != 1 or self.frame is None:
            return
        multiplier = max((value for value in self.frame.loop_repeat_stack if value is not None), default=1)
        self.frame.radix_decode_count += multiplier

    def visit_For(self, node: ast.For) -> Any:
        return self._visit_loop(node)

    def visit_AsyncFor(self, node: ast.AsyncFor) -> Any:
        self.add_violation(node, "CAP_ASYNC_CODE", "async for", "async execution is outside the deterministic source closure")
        return self._visit_loop(node)

    def _visit_loop(self, node: ast.For | ast.AsyncFor) -> None:
        if self._is_environment_object(node.iter):
            self.add_violation(node, "CAP_ENVIRONMENT_ENUMERATION", "os.environ", "environment enumeration is forbidden")
        physical = self._is_physical_loop(node)
        if self.frame is not None:
            self.frame.loop_physical_stack.append(physical)
            self.frame.loop_repeat_stack.append(self._static_loop_count(node.iter))
            depth = sum(self.frame.loop_physical_stack)
            if depth >= 5:
                if self.role == ROLE_PRODUCER:
                    self.add_violation(node, "ENUM_FIVE_NESTED_LOOPS", "for", "five nested physical-mode loops are forbidden in the producer")
                else:
                    self.add_feature(node, "VERIFIER_EXPLICIT_FIVE_LOOP_ENUMERATION", "independent explicit traversal observed")
        self.visit(node.target)
        self.visit(node.iter)
        for statement in node.body:
            self.visit(statement)
        for statement in node.orelse:
            self.visit(statement)
        if self.frame is not None:
            self.frame.loop_physical_stack.pop()
            self.frame.loop_repeat_stack.pop()

    def _static_loop_count(self, iterator: ast.AST) -> int | None:
        if not isinstance(iterator, ast.Call):
            return None
        resolved = self.resolve_callable(iterator.func)
        if not resolved or resolved[1].rsplit(".", 1)[-1] != "range" or not iterator.args:
            return None
        if len(iterator.args) == 1:
            return constant_int_expression(iterator.args[0], self.assignments)
        if len(iterator.args) >= 2:
            start = constant_int_expression(iterator.args[0], self.assignments)
            stop = constant_int_expression(iterator.args[1], self.assignments)
            step = constant_int_expression(iterator.args[2], self.assignments) if len(iterator.args) >= 3 else 1
            if start is not None and stop is not None and step not in {None, 0}:
                return len(range(start, stop, step))
        return None

    def _is_physical_loop(self, node: ast.For | ast.AsyncFor) -> bool:
        target_names = {
            child.id
            for child in ast.walk(node.target)
            if isinstance(child, ast.Name)
        }
        if any(MODE_NAME_RE.fullmatch(name) or re.fullmatch(r"[ijklm]|i[1-5]", name, re.I) for name in target_names):
            return True
        if isinstance(node.iter, ast.Call) and node.iter.args:
            resolved = self.resolve_callable(node.iter.func)
            if resolved and resolved[1].rsplit(".", 1)[-1] == "range":
                return b_degree(node.iter.args[-1], self.assignments) == 1
        return False

    def visit_ListComp(self, node: ast.ListComp) -> Any:
        self._audit_comprehension(node, node.generators)
        self.generic_visit(node)
        return None

    def visit_SetComp(self, node: ast.SetComp) -> Any:
        self._audit_comprehension(node, node.generators)
        self.generic_visit(node)
        return None

    def visit_DictComp(self, node: ast.DictComp) -> Any:
        self._audit_comprehension(node, node.generators)
        self.generic_visit(node)
        return None

    def visit_GeneratorExp(self, node: ast.GeneratorExp) -> Any:
        self._audit_comprehension(node, node.generators)
        self.generic_visit(node)
        return None

    def _audit_comprehension(self, node: ast.AST, generators: Sequence[ast.comprehension]) -> None:
        if any(self._is_environment_object(generator.iter) for generator in generators):
            self.add_violation(node, "CAP_ENVIRONMENT_ENUMERATION", "os.environ", "environment enumeration is forbidden")
        if len(generators) >= 5:
            if self.role == ROLE_PRODUCER:
                self.add_violation(node, "ENUM_FIVE_NESTED_LOOPS", "comprehension", "five-generator physical comprehension is forbidden")
            else:
                self.add_feature(node, "VERIFIER_EXPLICIT_FIVE_LOOP_ENUMERATION", "independent comprehension traversal observed")

    def _is_environment_object(self, node: ast.AST) -> bool:
        root, attrs = flatten_attribute(node)
        return root == "os" and attrs == ["environ"]

    def visit_BinOp(self, node: ast.BinOp) -> Any:
        degree = b_degree(node, self.assignments)
        if degree == 5 and self.role == ROLE_PRODUCER:
            self.add_violation(node, "ENUM_B5_EXPRESSION", "B^5", "producer contains a symbolic B^5 expression or constant-folded equivalent")
        if isinstance(node.op, (ast.Mod, ast.FloorDiv)) and b_degree(node.right, self.assignments) == 1:
            if self.frame is not None:
                multiplier = max((value for value in self.frame.loop_repeat_stack if value is not None), default=1)
                self.frame.radix_decode_count += multiplier
        if isinstance(node.op, ast.Mult):
            sequence_side: ast.AST | None = None
            count_side: ast.AST | None = None
            if isinstance(node.left, (ast.List, ast.Tuple)):
                sequence_side, count_side = node.left, node.right
            elif isinstance(node.right, (ast.List, ast.Tuple)):
                sequence_side, count_side = node.right, node.left
            if sequence_side is not None and count_side is not None:
                count = constant_int_expression(count_side, self.assignments)
                degree_count = b_degree(count_side, self.assignments)
                if self.role == ROLE_PRODUCER and (
                    degree_count == 5
                    or count in {value**5 for value in self.policy.source_b_values}
                    or (count is not None and count > 1_000_000)
                ):
                    self.add_violation(node, "IR_UNTRACED_DENSE_ALLOCATION", "sequence-repeat", "producer constructs a dense Python sequence outside audited NumPy allocation events")
        if self.role == ROLE_PRODUCER and self._is_array_arithmetic(node):
            self._require_ir_owner(node, "IR_ARITHMETIC_OUTSIDE_CLOSED_IR", node.op.__class__.__name__)
        self.generic_visit(node)
        return None

    def _is_array_arithmetic(self, node: ast.BinOp) -> bool:
        if isinstance(node.op, ast.MatMult):
            return True
        return expression_has_array_data(node)

    def visit_AugAssign(self, node: ast.AugAssign) -> Any:
        if self.role == ROLE_PRODUCER and (expression_has_array_data(node) or isinstance(node.op, ast.MatMult)):
            self._require_ir_owner(node, "IR_ARITHMETIC_OUTSIDE_CLOSED_IR", node.op.__class__.__name__)
        self.generic_visit(node)
        return None

    def visit_Subscript(self, node: ast.Subscript) -> Any:
        if self.role == ROLE_PRODUCER and isinstance(node.slice, ast.Tuple) and len(node.slice.elts) >= 5:
            self.add_violation(node, "ENUM_GENERIC_FIVE_INDEX", "subscript", "generic five-index physical access is forbidden in the producer")
        if (
            isinstance(node.slice, ast.Tuple)
            and len(node.slice.elts) > self.policy.maximum_ndarray_dimensions
            and has_arrayish_name(node.value)
        ):
            code = "ARRAY_FIVE_DIMENSIONAL" if len(node.slice.elts) >= 5 else "ARRAY_DIMENSION_LIMIT"
            self.add_violation(node, code, "subscript", "subscript exceeds the reviewed three-dimensional array boundary")
        root, attrs = flatten_attribute(node.value)
        if root == "os" and attrs == ["environ"]:
            key = literal_string(node.slice)
            if key is None or key not in self.policy.environment_allowlist:
                self.add_violation(node, "CAP_ENVIRONMENT_READ", "os.environ", "environment subscript is outside the six-key literal allowlist")
        self.generic_visit(node)
        return None

    def visit_Tuple(self, node: ast.Tuple) -> Any:
        self._audit_five_index_value(node)
        self._audit_sensitive_sequence(node)
        self.generic_visit(node)
        return None

    def visit_List(self, node: ast.List) -> Any:
        self._audit_five_index_value(node)
        self._audit_sensitive_sequence(node)
        self.generic_visit(node)
        return None

    def _audit_five_index_value(self, node: ast.List | ast.Tuple) -> None:
        if self.role != ROLE_PRODUCER or len(node.elts) != 5:
            return
        names = [child.id for child in node.elts if isinstance(child, ast.Name)]
        if len(names) == 5 and all(re.fullmatch(r"[ijklm]|i[1-5]|p[1-5]", name, re.I) for name in names):
            self.add_violation(node, "ENUM_GENERIC_FIVE_INDEX", "five-index tuple", "producer constructs a generic five-mode index")

    def _audit_sensitive_sequence(self, node: ast.List | ast.Tuple) -> None:
        sequence = literal_sequence(node)
        if sequence is not None and sequence in self.policy.sensitive_sequences:
            self.add_violation(
                node,
                "PHASE_WITHHELD_TARGET_LITERAL",
                "integer-sequence",
                f"source closure contains a withheld target sequence (literal_sha256={sha256_bytes(sequence.encode('ascii'))})",
            )

    def visit_Constant(self, node: ast.Constant) -> Any:
        if isinstance(node.value, (float, complex)):
            self.add_violation(node, "NUMERIC_FLOAT_OR_COMPLEX", type(node.value).__name__, "floating-point and complex literals are forbidden")
        if not isinstance(node.value, str):
            return None
        lowered = node.value.lower()
        for fragment in FORBIDDEN_ARTIFACT_FRAGMENTS:
            if fragment in lowered:
                verifier_outputs = (
                    "frozen-source-advice",
                    "frozen-source-control-certificates",
                    "source-advice-receipt",
                )
                allowed = self.role == ROLE_VERIFIER and (
                    Path(node.value).name == "source-generator-raw-result.json"
                    or any(item in lowered for item in verifier_outputs)
                )
                if not allowed:
                    self.add_violation(
                        node,
                        "PHASE_FORBIDDEN_ARTIFACT_LITERAL",
                        "string-literal",
                        f"literal names a withheld or prior artifact (literal_sha256={sha256_bytes(node.value.encode('utf-8'))})",
                    )
                break
        if node.value in self.policy.sensitive_strings:
            self.add_violation(
                node,
                "PHASE_WITHHELD_TARGET_LITERAL",
                "string-literal",
                f"source closure contains a withheld target or mutation literal (literal_sha256={sha256_bytes(node.value.encode('utf-8'))})",
            )
        if FLOAT_DTYPE_FRAGMENT.fullmatch(node.value.strip()) and node.value.lower() not in ALLOWED_INT64_DTYPE_STRINGS:
            self.add_violation(node, "NUMPY_FORBIDDEN_DTYPE", "dtype-literal", "floating, complex, or object dtype literal is forbidden")
        return None

    def visit_Attribute(self, node: ast.Attribute) -> Any:
        resolved = self.resolve_callable(node)
        if resolved and resolved[0] == "external":
            lowered = resolved[1].lower()
            if lowered == "sys.path" or lowered.startswith("sys.path."):
                self.add_violation(node, "CAP_IMPORT_PATH_ACCESS", resolved[1], "sys.path access can escape the hashed local import closure")
            if lowered == "sys.modules" or lowered.startswith("sys.modules."):
                if self._in_attestation_function("loaded_numpy_extensions"):
                    self.add_feature(node, "AUTHORIZED_BACKEND_MODULE_REGISTRY", resolved[1])
                else:
                    self.add_violation(node, "CAP_DYNAMIC_IMPORT", resolved[1], "module-registry access is forbidden outside backend attestation")
            if lowered.startswith("ctypes.") and lowered.rsplit(".", 1)[-1] not in {"cdll", "c_uint32", "c_char_p"}:
                self.add_violation(node, "CAP_BACKEND_ESCAPE", resolved[1], "ctypes attribute is outside the exact dyld attestation allowlist")
        if resolved and resolved[0] == "external" and resolved[1].lower().startswith("numpy."):
            lowered = resolved[1].lower()
            if ".linalg" in lowered:
                self.add_violation(node, "NUMPY_FORBIDDEN_API", resolved[1], "np.linalg is prohibited")
            last = lowered.rsplit(".", 1)[-1]
            if FLOAT_DTYPE_FRAGMENT.fullmatch(last) and last != "int64":
                self.add_violation(node, "NUMPY_FORBIDDEN_DTYPE", resolved[1], "only signed NumPy int64 is allowed")
        self.generic_visit(node)
        return None


def role_report(scanner: StaticScanner) -> dict[str, Any]:
    closure = scanner.closure
    files = [
        {
            "bytes": len(module.source.encode("utf-8")),
            "module": module.module_name,
            "path": module.relative_path,
            "sha256": module.digest,
        }
        for module in sorted(closure.modules.values(), key=lambda item: item.relative_path)
    ]
    violations = sorted(set(scanner.violations))
    return {
        "call_edges": [
            {"callee": callee, "caller": caller, "line": line, "path": path}
            for caller, callee, path, line in sorted(scanner.call_edges)
        ],
        "closure_files": files,
        "entry": path_label(closure.entry, closure.source_root),
        "external_imports": [
            {"bound_as": bound, "imported": imported, "path": path}
            for path, bound, imported in sorted(scanner.external_imports)
        ],
        "features": [
            {"detail": detail, "feature_code": code, "line": line, "path": path}
            for path, code, line, detail in sorted(scanner.features)
        ],
        "ir_primitives": [
            {"ir_kinds": list(kinds), "path": path, "symbol": symbol}
            for path, symbol, kinds in sorted(scanner.ir_primitives)
        ],
        "local_imports": [
            {"bound_as": bound, "path": path, "target": target}
            for path, bound, target in sorted(scanner.local_imports)
        ],
        "role": closure.role,
        "valid": not violations,
        "violations": [item.as_json() for item in violations],
    }


def source_is_inert_package_init(module: ModuleInfo) -> bool:
    if module.path.name != "__init__.py" or module.tree is None:
        return False
    body = list(module.tree.body)
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
        body.pop(0)
    return not body


def cross_role_violations(
    producer: Closure | None,
    verifier: Closure | None,
) -> tuple[list[Violation], dict[str, Any]]:
    if producer is None or verifier is None:
        return [], {
            "performed": False,
            "reason": "both --producer-entry and --verifier-entry are required for closure-disjointness proof",
            "shared_files": [],
        }
    producer_by_path = {module.path: module for module in producer.modules.values()}
    verifier_by_path = {module.path: module for module in verifier.modules.values()}
    shared = sorted(producer.paths & verifier.paths)
    actionable = [
        path
        for path in shared
        if not (
            source_is_inert_package_init(producer_by_path[path])
            and source_is_inert_package_init(verifier_by_path[path])
        )
    ]
    violations = [
        Violation(
            role="cross-role",
            path=path_label(path, producer.source_root),
            line=0,
            column=0,
            reason_code="ROLE_SHARED_IMPLEMENTATION_CLOSURE",
            symbol=path.name,
            detail="producer and independent verifier share a non-inert local module",
        )
        for path in actionable
    ]
    return violations, {
        "performed": True,
        "shared_files": [path_label(path, producer.source_root) for path in shared],
        "shared_inert_package_initializers": [
            path_label(path, producer.source_root) for path in shared if path not in actionable
        ],
        "valid": not actionable,
    }


def build_audit_report(
    policy: Policy,
    source_root: Path,
    entries: Mapping[str, Path],
) -> tuple[dict[str, Any], int]:
    closures: dict[str, Closure] = {}
    scanners: dict[str, StaticScanner] = {}
    for role in ROLES:
        entry = entries.get(role)
        if entry is None:
            continue
        closure = build_closure(role, entry, source_root)
        scanner = StaticScanner(closure, policy)
        scanner.scan()
        closures[role] = closure
        scanners[role] = scanner

    cross_violations, cross_report = cross_role_violations(
        closures.get(ROLE_PRODUCER),
        closures.get(ROLE_VERIFIER),
    )
    violations = sorted(
        set(
            item
            for scanner in scanners.values()
            for item in scanner.violations
        )
        | set(cross_violations)
    )
    valid = bool(scanners) and not violations
    harness_rows = [
        {
            "bytes": (source_root / name).stat().st_size,
            "path": name,
            "sha256": sha256_file(source_root / name),
        }
        for name in EXPECTED_HARNESS_FILES
    ]
    report: dict[str, Any] = {
        "auditor": {
            "path": SCRIPT_PATH.name,
            "sha256": sha256_file(SCRIPT_PATH),
            "version": AUDITOR_VERSION,
        },
        "boundary": {
            "execution": "harness-side static analysis only",
            "report_visibility": "contains withheld policy hashes; never stage this report into a source producer or source verifier root",
            "source_execution": False,
        },
        "cross_role": cross_report,
        "harness": {
            "closure_sha256": closure_digest(harness_rows),
            "files": harness_rows,
        },
        "limitations": [
            "Static audit does not replace isolated-staging runtime filesystem, allocation, environment, or IR-event interception.",
            "External standard-library and NumPy files are classified here; their complete file and loader identities belong to attest_tt_backend.py and the pre-run receipt.",
            "IR ownership is accepted only through a canonical IR token in the function name, a TT_IR docstring marker, or an audited IR decorator; runtime trace reconciliation remains mandatory.",
            "Target-literal checks cover direct target-only strings, committed digests, and exact integer sequences; encoded, computed, or side-channel target inference requires the runtime phase firewall and digest-invariance control.",
            "Unknown NumPy allocation dimensionality is rejected rather than inferred from execution.",
        ],
        "policy": policy.public_json(),
        "roles": {role: role_report(scanners[role]) for role in sorted(scanners)},
        "schema": SCHEMA,
        "valid": valid,
        "violations": [item.as_json() for item in violations],
    }
    report["payload_sha256"] = sha256_bytes(canonical_json_bytes(report))
    return report, 0 if valid else 1


def schema_document() -> dict[str, Any]:
    value: dict[str, Any] = {
        "canonical_encoding": "UTF-8 sorted-key compact JSON with one trailing newline",
        "cli": {
            "default_source_root": "directory containing audit_tt_source_closure.py",
            "required": ["at least one role entry, unless a default-named role entry exists"],
            "role_entries": ["--producer-entry", "--verifier-entry"],
            "recommended": "pass both role entries so closure disjointness is checked",
        },
        "exit_codes": {"0": "valid", "1": "policy violation", "2": "configuration or CLI error"},
        "ir_marker_forms": [
            "canonical IR token in function name",
            "function docstring line TT_IR: <node_kind>",
            "@ir_node(<node_kind>), @ir_primitive(<node_kind>), or @tt_ir_primitive(<node_kind>)",
        ],
        "reason_code_families": {
            "ARRAY_": "array dimension proof",
            "CAP_": "capability, import, call, filesystem, environment, process, or network boundary",
            "ENUM_": "producer physical-tuple enumeration boundary",
            "IMPORT_": "local/import closure binding",
            "IR_": "closed operation-IR ownership",
            "NUMPY_": "pinned dense-backend API and dtype policy",
            "PHASE_": "target/mutation/prior-artifact phase firewall",
            "ROLE_": "producer/verifier independence",
        },
        "report_required_keys": [
            "auditor",
            "boundary",
            "cross_role",
            "harness",
            "limitations",
            "payload_sha256",
            "policy",
            "roles",
            "schema",
            "valid",
            "violations",
        ],
        "schema": SCHEMA,
    }
    value["payload_sha256"] = sha256_bytes(canonical_json_bytes(value))
    return value


def resolve_entry(value: Path | None, source_root: Path, default_name: str) -> Path | None:
    if value is None:
        candidate = source_root / default_name
        return candidate if candidate.is_file() else None
    if value.is_absolute():
        return value
    cwd_candidate = (Path.cwd() / value).resolve()
    if cwd_candidate.is_file():
        return cwd_candidate
    return (source_root / value).resolve()


def emit_json(value: Any) -> None:
    sys.stdout.buffer.write(canonical_json_bytes(value) + b"\n")
    sys.stdout.buffer.flush()


def configuration_error_report(message: str) -> dict[str, Any]:
    report: dict[str, Any] = {
        "auditor": {"path": SCRIPT_PATH.name, "sha256": sha256_file(SCRIPT_PATH), "version": AUDITOR_VERSION},
        "boundary": {
            "execution": "harness-side static analysis only",
            "report_visibility": "never stage into a source process",
            "source_execution": False,
        },
        "error": {"reason_code": "AUDIT_CONFIGURATION_ERROR", "message": message},
        "schema": SCHEMA,
        "valid": False,
    }
    report["payload_sha256"] = sha256_bytes(canonical_json_bytes(report))
    return report


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog=(
            "Pass producer and verifier together for the independence proof. "
            "Explicit producer NumPy kernels need one closed-IR owner; use an IR token "
            "in the function name, a TT_IR docstring marker, or an audited IR decorator."
        ),
    )
    parser.add_argument("--source-root", type=Path, default=SOURCE_DIR, help="root used to resolve and contain local Python imports")
    parser.add_argument("--producer-entry", type=Path, help="source-producer Python entry point")
    parser.add_argument("--verifier-entry", type=Path, help="independent source-verifier Python entry point")
    parser.add_argument("--contract", type=Path, default=EXPERIMENT_DIR / "contract-v5.md")
    parser.add_argument(
        "--source-execution-matrix",
        type=Path,
        default=EXPERIMENT_DIR / "source-execution-matrix-v2.json",
    )
    parser.add_argument(
        "--full-execution-matrix",
        type=Path,
        default=EXPERIMENT_DIR / "execution-matrix-v4.json",
    )
    parser.add_argument(
        "--mutation-manifest",
        type=Path,
        default=EXPERIMENT_DIR / "mutation-manifest-v4.json",
    )
    parser.add_argument(
        "--source-manifest",
        type=Path,
        default=EXPERIMENT_DIR / "source-instance-manifest-v1.json",
    )
    parser.add_argument(
        "--target-manifest",
        type=Path,
        default=EXPERIMENT_DIR / "target-instance-manifest-v1.json",
    )
    parser.add_argument("--describe-schema", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args(argv)


def write_fixture(root: Path, name: str, source: str) -> Path:
    path = root / name
    path.write_text(source.strip() + "\n", encoding="utf-8")
    return path


def self_test(policy: Policy) -> tuple[dict[str, Any], int]:
    checks: list[dict[str, Any]] = []

    def record(name: str, passed: bool, observed: Iterable[str], expected: Iterable[str]) -> None:
        checks.append(
            {
                "expected_reason_codes": sorted(expected),
                "name": name,
                "observed_reason_codes": sorted(observed),
                "passed": passed,
            }
        )

    with tempfile.TemporaryDirectory(prefix="tt-source-audit-") as temporary:
        root = Path(temporary)
        safe_producer = write_fixture(
            root,
            "safe_producer.py",
            """
import numpy as np

def stage_a_contract():
    return np.empty((1, 2, 3), dtype=np.int64, order="C")

def main():
    return stage_a_contract()
""",
        )
        safe_verifier = write_fixture(
            root,
            "safe_verifier.py",
            """
def enumerate_values(B):
    total = 0
    for i in range(B):
        for j in range(B):
            for k in range(B):
                for l in range(B):
                    for m in range(B):
                        total += i + j + k + l + m
    return total
""",
        )
        safe_report, _ = build_audit_report(
            policy,
            root,
            {ROLE_PRODUCER: safe_producer, ROLE_VERIFIER: safe_verifier},
        )
        safe_codes = {item["reason_code"] for item in safe_report["violations"]}
        record("role_split_allows_explicit_verifier_enumeration", not safe_codes, safe_codes, ())

        b5 = write_fixture(
            root,
            "bad_b5.py",
            """
def main(B):
    for flat in range(B * B * B * B * B):
        pass
""",
        )
        report, _ = build_audit_report(policy, root, {ROLE_PRODUCER: b5})
        codes = {item["reason_code"] for item in report["violations"]}
        expected = {"ENUM_B5_EXPRESSION", "ENUM_B5_TRAVERSAL"}
        record("producer_b5", expected <= codes, codes, expected)

        folded_b5 = write_fixture(root, "bad_folded_b5.py", "def main():\n    return list(range(3125))")
        report, _ = build_audit_report(policy, root, {ROLE_PRODUCER: folded_b5})
        codes = {item["reason_code"] for item in report["violations"]}
        expected = {"ENUM_CONSTANT_FOLDED_B5"}
        record("constant_folded_b5", expected <= codes, codes, expected)

        product_folded = write_fixture(
            root,
            "bad_math_product.py",
            "import math\n\ndef main(B):\n    return range(math.prod([B] * 5))",
        )
        report, _ = build_audit_report(policy, root, {ROLE_PRODUCER: product_folded})
        codes = {item["reason_code"] for item in report["violations"]}
        expected = {"ENUM_B5_TRAVERSAL"}
        record("math_product_b5", expected <= codes, codes, expected)

        product5 = write_fixture(
            root,
            "bad_product5.py",
            "from itertools import product\n\ndef main(B):\n    return product(range(B), repeat=5)",
        )
        report, _ = build_audit_report(policy, root, {ROLE_PRODUCER: product5})
        codes = {item["reason_code"] for item in report["violations"]}
        expected = {"CAP_FORBIDDEN_IMPORT", "ENUM_PRODUCT_REPEAT_5"}
        record("generic_product5", expected <= codes, codes, expected)

        radix5 = write_fixture(
            root,
            "bad_radix5.py",
            """
def main(flat, B):
    d0 = flat % B
    flat = flat // B
    d1 = flat % B
    flat = flat // B
    d2 = flat % B
    flat = flat // B
    return d0, d1, d2, flat % B, flat // B
""",
        )
        report, _ = build_audit_report(policy, root, {ROLE_PRODUCER: radix5})
        codes = {item["reason_code"] for item in report["violations"]}
        expected = {"ENUM_RADIX_DECODE_5"}
        record("radix_decode5", expected <= codes, codes, expected)

        report, _ = build_audit_report(policy, root, {ROLE_PRODUCER: safe_verifier})
        codes = {item["reason_code"] for item in report["violations"]}
        expected = {"ENUM_FIVE_NESTED_LOOPS"}
        record("producer_five_nested_loops", expected <= codes, codes, expected)

        bad_numpy = write_fixture(
            root,
            "bad_numpy.py",
            """
import numpy as np

def helper():
    return np.zeros((2, 2, 2, 2, 2), dtype=np.float64)
""",
        )
        report, _ = build_audit_report(policy, root, {ROLE_PRODUCER: bad_numpy})
        codes = {item["reason_code"] for item in report["violations"]}
        expected = {"ARRAY_FIVE_DIMENSIONAL", "IR_ALLOCATION_OUTSIDE_CLOSED_IR", "NUMPY_FORBIDDEN_DTYPE"}
        record("five_dimensional_float_allocation", expected <= codes, codes, expected)

        forbidden_numpy = write_fixture(
            root,
            "bad_einsum.py",
            "import numpy as np\n\ndef helper(left, right):\n    return np.einsum('ij,jk->ik', left, right)",
        )
        report, _ = build_audit_report(policy, root, {ROLE_PRODUCER: forbidden_numpy})
        codes = {item["reason_code"] for item in report["violations"]}
        expected = {"NUMPY_FORBIDDEN_API"}
        record("forbidden_numpy_api", expected <= codes, codes, expected)

        array_write = write_fixture(root, "bad_array_write.py", "def helper(matrix):\n    matrix[0, 0] = 1")
        report, _ = build_audit_report(policy, root, {ROLE_PRODUCER: array_write})
        codes = {item["reason_code"] for item in report["violations"]}
        expected = {"IR_ARRAY_WRITE_OUTSIDE_CLOSED_IR"}
        record("untraced_array_write", expected <= codes, codes, expected)

        dense_python = write_fixture(root, "bad_dense_python.py", "def main():\n    return [0] * 3125")
        report, _ = build_audit_report(policy, root, {ROLE_PRODUCER: dense_python})
        codes = {item["reason_code"] for item in report["violations"]}
        expected = {"IR_UNTRACED_DENSE_ALLOCATION"}
        record("dense_python_table", expected <= codes, codes, expected)

        target_read = write_fixture(
            root,
            "bad_target_read.py",
            'def main():\n    with open("target-instance-manifest-v1.json", "r") as handle:\n        return handle.read()',
        )
        report, _ = build_audit_report(policy, root, {ROLE_PRODUCER: target_read})
        codes = {item["reason_code"] for item in report["violations"]}
        expected = {"CAP_DATA_READ_OUTSIDE_ALLOWLIST", "PHASE_FORBIDDEN_ARTIFACT_LITERAL"}
        record("target_artifact_read", expected <= codes, codes, expected)

        path_option = write_fixture(
            root,
            "bad_path_option.py",
            """
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--control-manifest", type=Path)
    return parser.parse_args()
""",
        )
        report, _ = build_audit_report(policy, root, {ROLE_VERIFIER: path_option})
        codes = {item["reason_code"] for item in report["violations"]}
        expected = {"CAP_CLI_DATA_INPUT_OUTSIDE_ALLOWLIST"}
        record("path_cli_allowlist", expected <= codes, codes, expected)

        child_process = write_fixture(
            root,
            "bad_subprocess.py",
            'import subprocess\n\ndef main():\n    return subprocess.run(["true"])',
        )
        report, _ = build_audit_report(policy, root, {ROLE_PRODUCER: child_process})
        codes = {item["reason_code"] for item in report["violations"]}
        expected = {"CAP_FORBIDDEN_IMPORT", "CAP_CHILD_PROCESS"}
        record("child_process", expected <= codes, codes, expected)

        dynamic = write_fixture(root, "bad_dynamic.py", "def main(text):\n    return eval(text)")
        report, _ = build_audit_report(policy, root, {ROLE_PRODUCER: dynamic})
        codes = {item["reason_code"] for item in report["violations"]}
        expected = {"CAP_DYNAMIC_CODE"}
        record("dynamic_code", expected <= codes, codes, expected)

        unbound = write_fixture(root, "bad_unbound.py", "def main():\n    return hidden_helper()")
        report, _ = build_audit_report(policy, root, {ROLE_PRODUCER: unbound})
        codes = {item["reason_code"] for item in report["violations"]}
        expected = {"CAP_UNBOUND_HELPER"}
        record("unbound_helper", expected <= codes, codes, expected)

        recursive = write_fixture(root, "bad_recursive.py", "def main():\n    return main()")
        report, _ = build_audit_report(policy, root, {ROLE_PRODUCER: recursive})
        codes = {item["reason_code"] for item in report["violations"]}
        expected = {"CAP_PRODUCER_RECURSION"}
        record("producer_recursion", expected <= codes, codes, expected)

        producer_module = write_fixture(root, "producer_runtime.py", "def stage_a_contract():\n    return 1")
        verifier_import = write_fixture(
            root,
            "verifier_import.py",
            "from producer_runtime import stage_a_contract\n\ndef main():\n    return stage_a_contract()",
        )
        report, _ = build_audit_report(
            policy,
            root,
            {ROLE_PRODUCER: producer_module, ROLE_VERIFIER: verifier_import},
        )
        codes = {item["reason_code"] for item in report["violations"]}
        expected = {"ROLE_FORBIDDEN_LOCAL_IMPORT", "ROLE_SHARED_IMPLEMENTATION_CLOSURE"}
        record("verifier_producer_alias", expected <= codes, codes, expected)

        attestation_path = SOURCE_DIR / "attest_tt_backend.py"
        if attestation_path.is_file():
            report, _ = build_audit_report(policy, SOURCE_DIR, {ROLE_PRODUCER: attestation_path})
            codes = {item["reason_code"] for item in report["violations"]}
            record("scoped_backend_attestation", not codes, codes, ())

    valid = all(item["passed"] for item in checks)
    report: dict[str, Any] = {
        "checks": checks,
        "schema": f"{SCHEMA}-self-test-v1",
        "valid": valid,
    }
    report["payload_sha256"] = sha256_bytes(canonical_json_bytes(report))
    return report, 0 if valid else 1


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if args.describe_schema:
        emit_json(schema_document())
        return 0
    try:
        policy = load_policy(
            args.contract.resolve(),
            args.source_execution_matrix.resolve(),
            args.full_execution_matrix.resolve(),
            args.mutation_manifest.resolve(),
            args.source_manifest.resolve(),
            args.target_manifest.resolve(),
        )
        if args.self_test:
            report, status = self_test(policy)
            emit_json(report)
            return status

        source_root = args.source_root.resolve()
        if not source_root.is_dir():
            raise AuditConfigurationError("source root is not a directory")
        if args.producer_entry is None and args.verifier_entry is None:
            producer = resolve_entry(None, source_root, "compile_tt_source_advice.py")
            verifier = resolve_entry(None, source_root, "verify_tt_source_advice.py")
        else:
            producer = resolve_entry(args.producer_entry, source_root, "compile_tt_source_advice.py") if args.producer_entry is not None else None
            verifier = resolve_entry(args.verifier_entry, source_root, "verify_tt_source_advice.py") if args.verifier_entry is not None else None
        entries = {
            role: entry
            for role, entry in ((ROLE_PRODUCER, producer), (ROLE_VERIFIER, verifier))
            if entry is not None
        }
        if not entries:
            raise AuditConfigurationError("no auditable producer or verifier entry was supplied or found")
        report, status = build_audit_report(policy, source_root, entries)
    except AuditConfigurationError as exc:
        emit_json(configuration_error_report(str(exc)))
        return 2
    emit_json(report)
    return status


if __name__ == "__main__":
    raise SystemExit(main())
