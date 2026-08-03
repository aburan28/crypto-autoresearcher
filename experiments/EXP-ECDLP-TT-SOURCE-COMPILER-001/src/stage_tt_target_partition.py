#!/usr/bin/env python3
"""Stage and externally supervise one development target partition."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import resource
import select
import stat
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Mapping, Sequence


PROTOCOL = "EXP-ECDLP-TT-SOURCE-COMPILER-001"
RECEIPT_PREFIX = b"TT_TARGET_RUNTIME_RECEIPT\t"
EXPECTED_ENVIRONMENT = {
    "MKL_NUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "PYTHONHASHSEED": "0",
    "VECLIB_MAXIMUM_THREADS": "1",
}
EXPECTED_ENVIRONMENT_EVENTS = (
    {"event": "os.putenv", "key": "OPENBLAS_MAIN_FREE", "value": "1"},
    {"event": "os.putenv", "key": "GOTOBLAS_MAIN_FREE", "value": "1"},
    {"event": "os.unsetenv", "key": "OPENBLAS_MAIN_FREE", "value": None},
    {"event": "os.unsetenv", "key": "GOTOBLAS_MAIN_FREE", "value": None},
)
EXPECTED_HARNESS_FILES = (
    "attest_tt_backend.py",
    "audit_tt_target_closure.py",
    "run_tt_target_partition.py",
    "stage_tt_target_partition.py",
)
COMMON_STAGE_FILES = (
    "attest_tt_backend.py",
    "candidate-source-bundle.json",
    "execution-matrix-v4.json",
    "run_tt_target_partition.py",
    "target-instance-manifest-v1.json",
)
ROLE_SOURCE_FILES = {
    "producer": (
        "compile_tt_target_advice.py",
        "tt_target_coefficients.py",
        "tt_target_runtime.py",
    ),
    "verifier": ("verify_tt_target_advice.py",),
}
ROLE_EXTRA_FILES = {
    "producer": (),
    "verifier": ("target-raw-result.json",),
}
MAX_INPUT_BYTES = 16 * 1024 * 1024
MAX_RAW_BYTES = 256 * 1024 * 1024
SYSTEM_VERSION_PATH = Path("/System/Library/CoreServices/SystemVersion.plist")
DEV_NULL_PATH = Path("/dev/null")
BACKEND_CHECK_FIELDS = (
    "machine",
    "numpy_distribution_file_count",
    "numpy_installed_closure_sha256",
    "numpy_multiarray_umath_sha256",
    "numpy_version",
    "os_loader_dependencies_loaded",
    "platform",
    "python_executable",
    "python_executable_sha256",
    "python_version",
    "thread_count",
)


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


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def read_canonical_object(path: Path, label: str, maximum_bytes: int) -> tuple[dict[str, Any], bytes]:
    expected_size = path.stat().st_size
    if expected_size > maximum_bytes:
        raise ValueError(f"{label} exceeds {maximum_bytes} bytes")
    payload = path.read_bytes()
    if len(payload) != expected_size:
        raise ValueError(f"{label} changed while it was read")
    value = json.loads(payload)
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    if payload != canonical_bytes(value):
        raise ValueError(f"{label} is not canonical JSON")
    return value, payload


def read_object(path: Path, label: str, maximum_bytes: int) -> tuple[dict[str, Any], bytes]:
    expected_size = path.stat().st_size
    if expected_size > maximum_bytes:
        raise ValueError(f"{label} exceeds {maximum_bytes} bytes")
    payload = path.read_bytes()
    if len(payload) != expected_size:
        raise ValueError(f"{label} changed while it was read")
    value = json.loads(payload)
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    return value, payload


def stage_digest(rows: Sequence[Mapping[str, Any]]) -> str:
    digest = hashlib.sha256()
    for row in sorted(rows, key=lambda item: str(item["path"])):
        digest.update(str(row["path"]).encode("utf-8"))
        digest.update(b"\0")
        digest.update(bytes.fromhex(str(row["sha256"])))
    return digest.hexdigest()


def path_within(path: Path, root: Path) -> bool:
    return path == root or root in path.parents


def exact_node_row(path: Path) -> dict[str, Any]:
    absolute = path.absolute()
    metadata = absolute.lstat()
    row: dict[str, Any] = {
        "mode": stat.S_IMODE(metadata.st_mode),
        "path": str(absolute),
    }
    if stat.S_ISREG(metadata.st_mode):
        row.update(
            {
                "bytes": metadata.st_size,
                "kind": "file",
                "sha256": sha256_file(absolute),
            }
        )
        return row
    if stat.S_ISLNK(metadata.st_mode):
        resolved = absolute.resolve(strict=True)
        if not resolved.is_file():
            raise ValueError(f"runtime symlink target is not a file: {absolute}")
        row.update(
            {
                "kind": "symlink",
                "resolved_bytes": resolved.stat().st_size,
                "resolved_path": str(resolved),
                "resolved_sha256": sha256_file(resolved),
                "target": os.readlink(absolute),
            }
        )
        return row
    if stat.S_ISCHR(metadata.st_mode):
        row.update({"device": metadata.st_rdev, "kind": "character_device"})
        return row
    raise ValueError(f"unsupported runtime allowlist node: {absolute}")


def directory_snapshot(path: Path) -> dict[str, Any]:
    absolute = path.resolve(strict=True)
    if not absolute.is_dir():
        raise ValueError(f"runtime directory is missing: {absolute}")
    names = sorted(os.listdir(absolute))
    return {
        "entry_count": len(names),
        "entries_sha256": sha256_bytes(canonical_bytes(names)),
        "path": str(absolute),
    }


def runtime_tree_closure(
    root: Path,
    *,
    excluded_roots: Sequence[Path] = (),
) -> tuple[dict[str, Any], tuple[Path, ...]]:
    resolved_root = root.resolve(strict=True)
    if not resolved_root.is_dir():
        raise ValueError(f"runtime tree root is not a directory: {resolved_root}")
    exclusions = tuple(path.resolve(strict=True) for path in excluded_roots)
    if any(not path_within(path, resolved_root) for path in exclusions):
        raise ValueError("runtime tree exclusion escapes its root")
    rows: list[dict[str, Any]] = []
    escaped_file_targets: set[Path] = set()
    total_bytes = 0
    counts = {"directories": 0, "files": 0, "symlinks": 0}

    def walk(directory: Path) -> None:
        nonlocal total_bytes
        with os.scandir(directory) as entries:
            ordered = sorted(entries, key=lambda item: item.name)
        for entry in ordered:
            path = Path(entry.path)
            if path in exclusions:
                continue
            relative = path.relative_to(resolved_root).as_posix()
            metadata = entry.stat(follow_symlinks=False)
            if entry.is_symlink():
                resolved = path.resolve(strict=True)
                row: dict[str, Any] = {
                    "kind": "symlink",
                    "path": relative,
                    "resolved_path": str(resolved),
                    "target": os.readlink(path),
                }
                if resolved.is_file():
                    row["resolved_bytes"] = resolved.stat().st_size
                    row["resolved_sha256"] = sha256_file(resolved)
                    if not path_within(resolved, resolved_root):
                        escaped_file_targets.add(resolved)
                elif resolved.is_dir():
                    if not path_within(resolved, resolved_root):
                        raise ValueError(
                            f"runtime tree has an escaping directory symlink: {path}"
                        )
                else:
                    raise ValueError(f"runtime tree symlink target is unsupported: {path}")
                counts["symlinks"] += 1
                rows.append(row)
                continue
            if entry.is_dir(follow_symlinks=False):
                counts["directories"] += 1
                rows.append({"kind": "directory", "path": relative})
                walk(path)
                continue
            if entry.is_file(follow_symlinks=False):
                digest = sha256_file(path)
                total_bytes += metadata.st_size
                counts["files"] += 1
                rows.append(
                    {
                        "bytes": metadata.st_size,
                        "kind": "file",
                        "path": relative,
                        "sha256": digest,
                    }
                )
                continue
            raise ValueError(f"runtime tree contains an unsupported node: {path}")

    walk(resolved_root)
    summary = {
        "bytes": total_bytes,
        "directory_count": counts["directories"],
        "excluded_roots": [str(path) for path in exclusions],
        "file_count": counts["files"],
        "root": str(resolved_root),
        "sha256": sha256_bytes(canonical_bytes(rows)),
        "symlink_count": counts["symlinks"],
    }
    return summary, tuple(sorted(escaped_file_targets, key=str))


def numpy_distribution_closure(
    site_packages: Path,
    dist_info: Path,
) -> tuple[dict[str, Any], tuple[Path, ...]]:
    record_path = dist_info / "RECORD"
    members: list[tuple[str, Path]] = []
    seen: set[str] = set()
    with record_path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.reader(handle):
            if not row or not row[0]:
                continue
            relative = row[0]
            if relative in seen or Path(relative).is_absolute():
                raise ValueError("NumPy RECORD paths are duplicated or absolute")
            seen.add(relative)
            absolute = (site_packages / relative).resolve(strict=True)
            if absolute.is_file():
                members.append((relative, absolute))
    digest = hashlib.sha256()
    total_bytes = 0
    absolute_paths: list[Path] = []
    for relative, absolute in sorted(members, key=lambda item: item[0]):
        member_digest = sha256_file(absolute)
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(bytes.fromhex(member_digest))
        total_bytes += absolute.stat().st_size
        absolute_paths.append(absolute)
    return (
        {
            "bytes": total_bytes,
            "file_count": len(members),
            "record_path": str(record_path.resolve()),
            "sha256": digest.hexdigest(),
        },
        tuple(absolute_paths),
    )


def backend_check_expectations(backend_gate: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "machine": backend_gate["machine"],
        "numpy_distribution_file_count": backend_gate[
            "numpy_distribution_file_count"
        ],
        "numpy_installed_closure_sha256": backend_gate[
            "numpy_installed_closure_sha256"
        ],
        "numpy_multiarray_umath_sha256": backend_gate[
            "numpy_multiarray_umath_sha256"
        ],
        "numpy_version": backend_gate["numpy_version"],
        "os_loader_dependencies_loaded": True,
        "platform": backend_gate["platform"],
        "python_executable": backend_gate["python_executable"],
        "python_executable_sha256": backend_gate["python_executable_sha256"],
        "python_version": backend_gate["python_version"],
        "thread_count": backend_gate["thread_count"],
    }


def build_runtime_boundary(
    python_path: Path,
    backend_gate: Mapping[str, Any],
) -> dict[str, Any]:
    if not python_path.is_absolute():
        raise ValueError("pinned Python executable path must be absolute")
    python_root = python_path.parent.parent.resolve(strict=True)
    version_parts = str(backend_gate["python_version"]).split(".")
    if len(version_parts) < 2 or not all(part.isdigit() for part in version_parts):
        raise ValueError("pinned Python version is malformed")
    stdlib = python_root / "lib" / f"python{version_parts[0]}.{version_parts[1]}"
    site_packages = stdlib / "site-packages"
    numpy_package = site_packages / "numpy"
    dist_candidates = sorted(site_packages.glob("numpy-*.dist-info"), key=str)
    if len(dist_candidates) != 1:
        raise ValueError("the pinned runtime must have one NumPy dist-info directory")
    dist_info = dist_candidates[0]
    expected_dist_name = f"numpy-{backend_gate['numpy_version']}.dist-info"
    if dist_info.name != expected_dist_name:
        raise ValueError("the NumPy dist-info version differs from the backend gate")

    tree_specs = ((stdlib, (site_packages,)), (numpy_package, ()), (dist_info, ()))
    optional_numpy_libs = site_packages / "numpy.libs"
    if optional_numpy_libs.exists():
        tree_specs += ((optional_numpy_libs, ()),)
    tree_summaries: list[dict[str, Any]] = []
    escaped_targets: set[Path] = set()
    for root, exclusions in tree_specs:
        summary, escaped = runtime_tree_closure(root, excluded_roots=exclusions)
        tree_summaries.append(summary)
        escaped_targets.update(escaped)

    distribution, distribution_paths = numpy_distribution_closure(
        site_packages, dist_info
    )
    if (
        distribution["file_count"]
        != backend_gate["numpy_distribution_file_count"]
        or distribution["sha256"]
        != backend_gate["numpy_installed_closure_sha256"]
    ):
        raise ValueError("parent-derived NumPy distribution closure changed")

    numpy_roots = tuple(root.resolve() for root, _ in tree_specs[1:])
    external_distribution_files = {
        path
        for path in distribution_paths
        if not any(path_within(path, root) for root in numpy_roots)
    }
    exact_paths = {
        python_path.absolute(),
        python_path.resolve(strict=True),
        (python_root / "Python").resolve(strict=True),
        SYSTEM_VERSION_PATH.resolve(strict=True),
        DEV_NULL_PATH,
        *external_distribution_files,
        *escaped_targets,
    }
    exact_nodes = [exact_node_row(path) for path in sorted(exact_paths, key=str)]

    read_filters: list[dict[str, Any]] = [
        {"kind": "literal", "path": "/"},
        {
            "excluded_path": str(site_packages.resolve()),
            "kind": "subpath_excluding",
            "path": str(stdlib.resolve()),
        },
        {"kind": "literal", "path": str(site_packages.resolve())},
    ]
    read_filters.extend(
        {"kind": "subpath", "path": str(root)} for root in numpy_roots
    )
    read_filters.extend(
        {"kind": "literal", "path": str(path)}
        for path in sorted(exact_paths, key=str)
    )
    unique_filters = {
        canonical_bytes(item): item for item in read_filters
    }
    ordered_filters = [unique_filters[key] for key in sorted(unique_filters)]

    boundary: dict[str, Any] = {
        "directory_data": [
            directory_snapshot(Path("/")),
            directory_snapshot(site_packages),
        ],
        "exact_nodes": exact_nodes,
        "numpy_distribution": distribution,
        "python_root": str(python_root),
        "read_filters": ordered_filters,
        "schema": "tt-target-parent-runtime-boundary-development-v1",
        "trees": tree_summaries,
    }
    boundary["closure_sha256"] = sha256_bytes(canonical_bytes(boundary))
    return boundary


def runtime_filter_allows(path: Path, read_filter: Mapping[str, Any]) -> bool:
    candidate = path.absolute()
    try:
        resolved = candidate.resolve(strict=True)
    except OSError:
        resolved = candidate
    root = Path(str(read_filter.get("path"))).absolute()
    kind = read_filter.get("kind")
    if kind == "literal":
        return candidate == root or resolved == root
    if kind == "subpath":
        return path_within(candidate, root) or path_within(resolved, root)
    if kind == "subpath_excluding":
        excluded = Path(str(read_filter.get("excluded_path"))).absolute()
        return (
            (path_within(candidate, root) and not path_within(candidate, excluded))
            or (path_within(resolved, root) and not path_within(resolved, excluded))
        )
    raise ValueError("runtime read filter kind is invalid")


def expected_stage_names(role: str) -> tuple[str, ...]:
    return tuple(
        sorted((*COMMON_STAGE_FILES, *ROLE_SOURCE_FILES[role], *ROLE_EXTRA_FILES[role]))
    )


def collect_stage_rows(stage_root: Path, role: str) -> list[dict[str, Any]]:
    observed_names = tuple(sorted(path.name for path in stage_root.iterdir()))
    if observed_names != expected_stage_names(role):
        raise ValueError("target staged file set differs from its role allowlist")
    return [
        {
            "bytes": (stage_root / name).stat().st_size,
            "path": name,
            "sha256": sha256_file(stage_root / name),
        }
        for name in observed_names
    ]


def collect_stage_identity_rows(stage_root: Path, role: str) -> list[dict[str, Any]]:
    resolved_root = stage_root.resolve()
    observed_names = tuple(sorted(path.name for path in resolved_root.iterdir()))
    if observed_names != expected_stage_names(role):
        raise ValueError("target staged identity set differs from its role allowlist")
    paths = [(".", resolved_root), *[(name, resolved_root / name) for name in observed_names]]
    rows: list[dict[str, Any]] = []
    for name, path in paths:
        metadata = path.stat(follow_symlinks=False)
        expected_kind = stat.S_ISDIR(metadata.st_mode) if name == "." else stat.S_ISREG(
            metadata.st_mode
        )
        if not expected_kind:
            raise ValueError(f"target staged path has the wrong vnode type: {name}")
        rows.append(
            {
                "device": metadata.st_dev,
                "inode": metadata.st_ino,
                "path": name,
                "size": metadata.st_size,
            }
        )
    return rows


class StageMutationMonitor:
    """Hold stage vnodes open and retain any namespace/content mutation event."""

    def __init__(self, stage_root: Path, role: str) -> None:
        if sys.platform != "darwin" or not hasattr(select, "kqueue"):
            raise RuntimeError("target stage mutation monitoring requires macOS kqueue")
        self.stage_root = stage_root.resolve()
        self._queue = select.kqueue()
        self._fds: dict[int, str] = {}
        self._identities: dict[str, dict[str, Any]] = {}
        self._closed = False
        note_names = (
            "KQ_NOTE_ATTRIB",
            "KQ_NOTE_DELETE",
            "KQ_NOTE_EXTEND",
            "KQ_NOTE_LINK",
            "KQ_NOTE_RENAME",
            "KQ_NOTE_REVOKE",
            "KQ_NOTE_WRITE",
        )
        self._note_flags = {
            name: int(getattr(select, name)) for name in note_names
        }
        try:
            self._register(self.stage_root, ".", expect_directory=True)
            observed_names = tuple(
                sorted(path.name for path in self.stage_root.iterdir())
            )
            if observed_names != expected_stage_names(role):
                raise ValueError("target staged file set changed before monitoring")
            for name in observed_names:
                self._register(
                    self.stage_root / name,
                    name,
                    expect_directory=False,
                )
            self.validate_bindings(collect_stage_identity_rows(self.stage_root, role))
            reject_stage_mutations(self.poll())
        except Exception:
            self.close()
            raise

    def _register(self, path: Path, name: str, *, expect_directory: bool) -> None:
        open_flags = int(getattr(os, "O_EVTONLY")) | int(os.O_CLOEXEC)
        descriptor = os.open(path, open_flags)
        self._fds[descriptor] = str(path)
        event = select.kevent(
            descriptor,
            filter=select.KQ_FILTER_VNODE,
            flags=select.KQ_EV_ADD | select.KQ_EV_CLEAR,
            fflags=sum(self._note_flags.values()),
        )
        self._queue.control([event], 0, 0)
        descriptor_metadata = os.fstat(descriptor)
        path_metadata = path.stat(follow_symlinks=False)
        type_matches = (
            stat.S_ISDIR(descriptor_metadata.st_mode)
            and stat.S_ISDIR(path_metadata.st_mode)
            if expect_directory
            else stat.S_ISREG(descriptor_metadata.st_mode)
            and stat.S_ISREG(path_metadata.st_mode)
        )
        if (
            not type_matches
            or descriptor_metadata.st_dev != path_metadata.st_dev
            or descriptor_metadata.st_ino != path_metadata.st_ino
        ):
            raise RuntimeError(f"target stage vnode binding changed during setup: {name}")
        self._identities[name] = {
            "device": descriptor_metadata.st_dev,
            "inode": descriptor_metadata.st_ino,
            "path": name,
            "size": descriptor_metadata.st_size,
        }

    @property
    def identity_rows(self) -> list[dict[str, Any]]:
        return [self._identities[name] for name in sorted(self._identities)]

    def validate_bindings(self, rows: Sequence[Mapping[str, Any]]) -> None:
        if list(rows) != self.identity_rows:
            raise RuntimeError("target stage path identities differ from watched vnodes")

    def poll(self) -> list[dict[str, Any]]:
        if self._closed:
            raise RuntimeError("target stage mutation monitor is closed")
        records: list[dict[str, Any]] = []
        while True:
            events = self._queue.control(None, max(1, len(self._fds) * 2), 0)
            if not events:
                break
            for event in events:
                flags = [
                    name
                    for name, value in self._note_flags.items()
                    if event.fflags & value
                ]
                records.append(
                    {
                        "event_flags": sorted(flags),
                        "filter": int(event.filter),
                        "flags": int(event.flags),
                        "path": self._fds.get(int(event.ident), "unknown"),
                    }
                )
        return records

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        try:
            self._queue.close()
        finally:
            for descriptor in self._fds:
                try:
                    os.close(descriptor)
                except OSError:
                    pass
            self._fds.clear()

    def __enter__(self) -> StageMutationMonitor:
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()


def reject_stage_mutations(events: Sequence[Mapping[str, Any]]) -> None:
    if events:
        raise RuntimeError("target stage mutated while the child was running")


def validate_static_audit(
    audit: Mapping[str, Any],
    audit_bytes: bytes,
    *,
    role: str,
    source_dir: Path,
) -> None:
    if audit_bytes != canonical_bytes(audit):
        raise ValueError("target static closure audit is not canonical JSON")
    if (
        audit.get("schema")
        != "exp-ecdlp-tt-target-capability-audit-development-v1"
        or audit.get("valid") is not True
        or audit.get("violations") != []
        or audit.get("artifact_freeze_authorized") is not False
    ):
        raise ValueError("target static closure audit boundary is invalid")
    role_record = audit.get(role)
    if not isinstance(role_record, dict):
        raise ValueError(f"target static {role} closure is missing")
    expected = tuple(sorted(ROLE_SOURCE_FILES[role]))
    observed = role_record.get("files")
    reports = role_record.get("reports")
    if observed != list(expected) or not isinstance(reports, list):
        raise ValueError(f"target static {role} closure file set changed")
    by_name = {
        report.get("file"): report
        for report in reports
        if isinstance(report, dict) and isinstance(report.get("file"), str)
    }
    if set(by_name) != set(expected):
        raise ValueError(f"target static {role} closure reports changed")
    for name in expected:
        report = by_name[name]
        if (
            report.get("valid") is not True
            or report.get("violations") != []
            or report.get("sha256") != sha256_file(source_dir / name)
        ):
            raise ValueError(f"target static {role} closure changed for {name}")
    harness = audit.get("harness")
    if not isinstance(harness, dict) or not isinstance(harness.get("files"), list):
        raise ValueError("target static harness closure is missing")
    harness_rows = {
        row.get("path"): row
        for row in harness["files"]
        if isinstance(row, dict) and isinstance(row.get("path"), str)
    }
    if set(harness_rows) != set(EXPECTED_HARNESS_FILES):
        raise ValueError("target static harness file set changed")
    for name in EXPECTED_HARNESS_FILES:
        path = source_dir / name
        row = harness_rows[name]
        if (
            row.get("bytes") != path.stat().st_size
            or row.get("sha256") != sha256_file(path)
        ):
            raise ValueError(f"target static harness changed for {name}")
    if harness.get("closure_sha256") != stage_digest(list(harness_rows.values())):
        raise ValueError("target static harness closure digest changed")


def normalized_rss_bytes(raw_rss: int) -> int:
    return raw_rss if sys.platform == "darwin" else raw_rss * 1024


def rusage_record(usage: resource.struct_rusage) -> dict[str, Any]:
    raw_rss = int(usage.ru_maxrss)
    return {
        "involuntary_context_switches": int(usage.ru_nivcsw),
        "major_page_faults": int(usage.ru_majflt),
        "maximum_rss_bytes": normalized_rss_bytes(raw_rss),
        "minor_page_faults": int(usage.ru_minflt),
        "raw_ru_maxrss": raw_rss,
        "system_cpu_ns": int(usage.ru_stime * 1_000_000_000),
        "user_cpu_ns": int(usage.ru_utime * 1_000_000_000),
        "voluntary_context_switches": int(usage.ru_nvcsw),
    }


def parse_child_receipt(stderr: bytes) -> tuple[dict[str, Any], bytes]:
    receipt_payload: bytes | None = None
    auxiliary: list[bytes] = []
    for line in stderr.splitlines(keepends=True):
        if line.startswith(RECEIPT_PREFIX):
            if receipt_payload is not None:
                raise ValueError("target child emitted more than one runtime receipt")
            receipt_payload = line[len(RECEIPT_PREFIX) :]
        elif line.strip():
            auxiliary.append(line)
    if receipt_payload is None:
        raise ValueError("target child did not emit a runtime receipt")
    if not receipt_payload.endswith(b"\n"):
        receipt_payload += b"\n"
    receipt = json.loads(receipt_payload)
    if not isinstance(receipt, dict) or receipt_payload != canonical_bytes(receipt):
        raise ValueError("target child runtime receipt is not canonical JSON")
    return receipt, b"".join(auxiliary)


def sandbox_filter_expression(read_filter: Mapping[str, Any]) -> str:
    kind = read_filter.get("kind")
    path = read_filter.get("path")
    if not isinstance(path, str) or not Path(path).is_absolute():
        raise ValueError("target sandbox read filter path must be absolute")
    quoted_path = json.dumps(path)
    if kind == "literal":
        return f"(literal {quoted_path})"
    if kind == "subpath":
        return f"(subpath {quoted_path})"
    excluded = read_filter.get("excluded_path")
    if (
        kind == "subpath_excluding"
        and isinstance(excluded, str)
        and Path(excluded).is_absolute()
    ):
        return (
            "(require-all "
            f"(subpath {quoted_path}) "
            f"(require-not (subpath {json.dumps(excluded)})))"
        )
    raise ValueError("target sandbox read filter is malformed")


def sandbox_profile(
    stage_root: Path,
    stage_rows: Sequence[Mapping[str, Any]],
    runtime_boundary: Mapping[str, Any],
) -> str:
    if not stage_root.is_absolute():
        raise ValueError("target sandbox stage path must be absolute")
    resolved_stage = stage_root.resolve()
    parts = resolved_stage.parts
    if len(parts) < 3 or parts[1] != "Volumes":
        raise ValueError("target stage must be on a mounted external volume")
    unsigned_boundary = dict(runtime_boundary)
    boundary_digest = unsigned_boundary.pop("closure_sha256", None)
    if (
        runtime_boundary.get("schema")
        != "tt-target-parent-runtime-boundary-development-v1"
        or boundary_digest != sha256_bytes(canonical_bytes(unsigned_boundary))
        or not isinstance(runtime_boundary.get("read_filters"), list)
    ):
        raise ValueError("target parent runtime boundary is invalid")
    stage_names = [row.get("path") for row in stage_rows]
    if any(
        not isinstance(name, str)
        or Path(name).name != name
        or name.startswith("._")
        for name in stage_names
    ) or len(set(stage_names)) != len(stage_names):
        raise ValueError("target stage rows are malformed")
    filters = [
        sandbox_filter_expression({"kind": "literal", "path": str(resolved_stage)}),
        *(
            sandbox_filter_expression(
                {"kind": "literal", "path": str(resolved_stage / str(name))}
            )
            for name in sorted(stage_names)
        ),
    ]
    filters.extend(
        sandbox_filter_expression(item)
        for item in runtime_boundary["read_filters"]
        if isinstance(item, dict)
    )
    if len(filters) != len(runtime_boundary["read_filters"]) + len(stage_rows) + 1:
        raise ValueError("target runtime read filters are malformed")
    allowed_reads = " ".join(filters)
    return "\n".join(
        (
            "(version 1)",
            "(allow default)",
            "(deny network*)",
            "(deny process-fork)",
            "(deny file-write*)",
            "(deny file-read-data "
            f"(require-not (require-any {allowed_reads})))",
        )
    )


def validate_child_backend_attestation(
    backend: Any,
    expected_values: Mapping[str, Any],
) -> None:
    checks = backend.get("checks") if isinstance(backend, dict) else None
    if (
        not isinstance(backend, dict)
        or backend.get("valid") is not True
        or not isinstance(checks, list)
        or len(checks) != len(BACKEND_CHECK_FIELDS)
    ):
        raise ValueError("target child backend attestation changed")
    by_field: dict[str, Mapping[str, Any]] = {}
    for check in checks:
        if (
            not isinstance(check, dict)
            or set(check) != {"expected", "field", "match", "observed"}
            or not isinstance(check.get("field"), str)
            or check["field"] in by_field
        ):
            raise ValueError("target child backend check schema changed")
        by_field[check["field"]] = check
    if set(by_field) != set(BACKEND_CHECK_FIELDS) or set(expected_values) != set(
        BACKEND_CHECK_FIELDS
    ):
        raise ValueError("target child backend check set changed")
    for field in BACKEND_CHECK_FIELDS:
        expected = expected_values[field]
        check = by_field[field]
        if (
            check.get("match") is not True
            or type(check.get("expected")) is not type(expected)
            or type(check.get("observed")) is not type(expected)
            or check.get("expected") != expected
            or check.get("observed") != expected
        ):
            raise ValueError(f"target child backend value changed for {field}")


def validate_child_runtime_receipt(
    receipt: Mapping[str, Any],
    *,
    backend_expectations: Mapping[str, Any],
    role: str,
    runtime_boundary: Mapping[str, Any],
    stage_rows: Sequence[Mapping[str, Any]],
    stage_sha256: str,
    static_audit_sha256: str,
    stage_root: Path,
) -> None:
    if (
        receipt.get("schema")
        != "tt-target-child-runtime-receipt-development-v1"
        or receipt.get("valid") is not True
        or receipt.get("role") != role
        or receipt.get("expected_stage_sha256") != stage_sha256
        or receipt.get("stage_sha256") != stage_sha256
        or receipt.get("static_closure_audit_sha256") != static_audit_sha256
        or receipt.get("denied_event_count") != 0
        or receipt.get("denied_events") != []
        or receipt.get("environment") != EXPECTED_ENVIRONMENT
        or receipt.get("environment_events") != list(EXPECTED_ENVIRONMENT_EVENTS)
        or receipt.get("stage_files") != list(stage_rows)
        or receipt.get("stage_file_count") != len(stage_rows)
        or receipt.get("stage_root") != str(stage_root.resolve())
    ):
        raise ValueError("target child runtime receipt boundary changed")
    backend = receipt.get("backend_attestation")
    validate_child_backend_attestation(backend, backend_expectations)
    read_rows = receipt.get("read_files")
    if not isinstance(read_rows, list) or receipt.get("read_file_count") != len(read_rows):
        raise ValueError("target child read-file receipt is malformed")
    read_filters = runtime_boundary.get("read_filters")
    if not isinstance(read_filters, list) or any(
        not isinstance(item, dict) for item in read_filters
    ):
        raise ValueError("target parent runtime read filters are malformed")
    effective_filters = [
        {"kind": "literal", "path": str(stage_root.resolve())},
        *(
            {
                "kind": "literal",
                "path": str(stage_root.resolve() / str(row["path"])),
            }
            for row in stage_rows
        ),
        *read_filters,
    ]
    observed_paths: set[str] = set()
    for row in read_rows:
        if not isinstance(row, dict) or not isinstance(row.get("path"), str):
            raise ValueError("target child read-file row is malformed")
        path = Path(row["path"]).resolve()
        path_text = str(path)
        if path_text in observed_paths:
            raise ValueError("target child read-file receipt contains duplicates")
        observed_paths.add(path_text)
        if not any(runtime_filter_allows(path, item) for item in effective_filters):
            raise ValueError(f"target child read escaped allowed roots: {path}")
        if not path.is_file() or row.get("sha256") != sha256_file(path):
            raise ValueError(f"target child read-file digest changed: {path}")


def validate_child_result(
    result: Mapping[str, Any],
    *,
    role: str,
    stdout: bytes,
    raw_result_sha256: str | None,
) -> None:
    expected = {
        "producer": (
            "tt-target-compiler-development-raw-v1",
            "target_generator_development",
        ),
        "verifier": (
            "tt-target-verifier-development-v1",
            "target_verifier_development",
        ),
    }[role]
    claims = result.get("claim_boundary")
    if (
        result.get("schema") != expected[0]
        or result.get("partition") != expected[1]
        or result.get("protocol") != PROTOCOL
        or result.get("valid") is not True
        or result.get("artifact_freeze_authorized") is not False
        or not isinstance(claims, dict)
        or claims.get("toy_restricted_model_bound") is not True
        or any(
            claims.get(key) is not False
            for key in (
                "breakthrough_claim",
                "ecdlp_improvement_claim",
                "index_calculus_claim",
                "locator_claim",
                "target_specialization_claim",
            )
        )
    ):
        raise ValueError("target child result boundary changed")
    if role == "producer":
        summary = result.get("summary")
        if (
            not isinstance(summary, dict)
            or summary.get("target_tensor_records") != 25
            or summary.get("serialized_bytes") != len(stdout)
            or not isinstance(result.get("runtime"), dict)
        ):
            raise ValueError("target producer result summary changed")
    else:
        inputs = result.get("inputs")
        if (
            not isinstance(inputs, dict)
            or inputs.get("target_raw_result_sha256") != raw_result_sha256
            or not isinstance(result.get("audits"), dict)
            or not isinstance(result.get("verifier_accounting"), dict)
        ):
            raise ValueError("target verifier result bindings changed")


def read_stable_bytes(path: Path, label: str, maximum_bytes: int) -> bytes:
    before = path.stat(follow_symlinks=False)
    if not stat.S_ISREG(before.st_mode) or before.st_size > maximum_bytes:
        raise ValueError(f"{label} is not a bounded regular file")
    payload = path.read_bytes()
    after = path.stat(follow_symlinks=False)
    if (
        before.st_dev != after.st_dev
        or before.st_ino != after.st_ino
        or before.st_size != after.st_size
        or len(payload) != before.st_size
    ):
        raise ValueError(f"{label} changed while retained by the parent")
    return payload


def approved_role_payloads(
    audit: Mapping[str, Any],
    *,
    role: str,
    source_dir: Path,
) -> dict[str, bytes]:
    role_record = audit[role]
    reports = {
        row["file"]: row["sha256"] for row in role_record["reports"]
    }
    harness = {
        row["path"]: row["sha256"] for row in audit["harness"]["files"]
    }
    expected_digests = {
        **{name: reports[name] for name in ROLE_SOURCE_FILES[role]},
        **{
            name: harness[name]
            for name in ("attest_tt_backend.py", "run_tt_target_partition.py")
        },
    }
    payloads: dict[str, bytes] = {}
    for name, expected_digest in expected_digests.items():
        payload = read_stable_bytes(
            source_dir / name,
            f"approved target source {name}",
            MAX_INPUT_BYTES,
        )
        if sha256_bytes(payload) != expected_digest:
            raise ValueError(f"approved target source changed before staging: {name}")
        payloads[name] = payload
    return payloads


def stage_retained_payload(
    destination: Path,
    payload: bytes,
    maximum_bytes: int,
) -> dict[str, Any]:
    if len(payload) > maximum_bytes:
        raise ValueError(f"staged input {destination.name} exceeds {maximum_bytes} bytes")
    destination.write_bytes(payload)
    if destination.read_bytes() != payload:
        raise ValueError(f"staged input {destination.name} changed while written")
    return {
        "bytes": len(payload),
        "path": destination.name,
        "sha256": sha256_bytes(payload),
    }


def validate_approved_stage_manifest(
    approved_rows: Sequence[Mapping[str, Any]],
    observed_rows: Sequence[Mapping[str, Any]],
) -> None:
    approved = sorted(approved_rows, key=lambda row: str(row["path"]))
    observed = sorted(observed_rows, key=lambda row: str(row["path"]))
    if approved != observed:
        raise RuntimeError("target stage differs from parent-retained approved bytes")


def remove_appledouble_files(stage_root: Path) -> None:
    for path in stage_root.iterdir():
        if path.name.startswith("._"):
            path.unlink()


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--role", choices=tuple(ROLE_SOURCE_FILES), required=True)
    parser.add_argument("--experiment-dir", type=Path, required=True)
    parser.add_argument("--candidate-source-bundle", type=Path, required=True)
    parser.add_argument("--closure-audit", type=Path, required=True)
    parser.add_argument("--staging-parent", type=Path, required=True)
    parser.add_argument("--raw-result", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--receipt-output", type=Path, required=True)
    return parser.parse_args(argv)


def run(args: argparse.Namespace) -> dict[str, Any]:
    role = args.role
    if (role == "verifier") != (args.raw_result is not None):
        raise ValueError("--raw-result is required only for the verifier role")
    experiment_dir = args.experiment_dir.resolve()
    source_dir = experiment_dir / "src"
    audit, audit_bytes = read_canonical_object(
        args.closure_audit.resolve(), "target static closure audit", MAX_INPUT_BYTES
    )
    validate_static_audit(
        audit, audit_bytes, role=role, source_dir=source_dir
    )
    role_payloads = approved_role_payloads(
        audit,
        role=role,
        source_dir=source_dir,
    )
    matrix_path = experiment_dir / "execution-matrix-v4.json"
    matrix_record, matrix_bytes = read_object(
        matrix_path, "execution matrix", MAX_INPUT_BYTES
    )
    matrix = matrix_record.get("execution_matrix")
    if not isinstance(matrix, dict):
        raise ValueError("execution matrix wrapper is malformed")
    backend = matrix.get("backend_gate")
    gates = matrix.get("resource_gates")
    if not isinstance(backend, dict) or not isinstance(gates, dict):
        raise ValueError("execution matrix backend or resource gates are missing")
    python_path = Path(str(backend.get("python_executable")))
    if sha256_file(python_path) != backend.get("python_executable_sha256"):
        raise ValueError("pinned Python executable digest changed")
    backend_expectations = backend_check_expectations(backend)
    runtime_boundary = build_runtime_boundary(python_path, backend)
    target_manifest_payload = read_stable_bytes(
        experiment_dir / "target-instance-manifest-v1.json",
        "target instance manifest",
        MAX_INPUT_BYTES,
    )
    candidate_bundle_payload = read_stable_bytes(
        args.candidate_source_bundle.resolve(),
        "candidate source bundle",
        MAX_INPUT_BYTES,
    )
    raw_result_payload = (
        read_stable_bytes(
            args.raw_result.resolve(),
            "target raw result",
            MAX_RAW_BYTES,
        )
        if role == "verifier"
        else None
    )

    args.staging_parent.mkdir(parents=True, exist_ok=True)
    stage_root = Path(
        tempfile.mkdtemp(
            prefix=f"tt-target-{role}-",
            dir=args.staging_parent.resolve(),
        )
    )
    approved_stage_rows: list[dict[str, Any]] = []
    for name, payload in sorted(role_payloads.items()):
        approved_stage_rows.append(
            stage_retained_payload(stage_root / name, payload, MAX_INPUT_BYTES)
        )
    approved_stage_rows.append(
        stage_retained_payload(
            stage_root / "execution-matrix-v4.json",
            matrix_bytes,
            MAX_INPUT_BYTES,
        )
    )
    approved_stage_rows.append(
        stage_retained_payload(
            stage_root / "target-instance-manifest-v1.json",
            target_manifest_payload,
            MAX_INPUT_BYTES,
        )
    )
    approved_stage_rows.append(
        stage_retained_payload(
            stage_root / "candidate-source-bundle.json",
            candidate_bundle_payload,
            MAX_INPUT_BYTES,
        )
    )
    if role == "verifier":
        if raw_result_payload is None:
            raise RuntimeError("target verifier raw result was not retained")
        approved_stage_rows.append(
            stage_retained_payload(
                stage_root / "target-raw-result.json",
                raw_result_payload,
                MAX_RAW_BYTES,
            )
        )
    remove_appledouble_files(stage_root)
    stage_rows = collect_stage_rows(stage_root, role)
    validate_approved_stage_manifest(approved_stage_rows, stage_rows)
    stage_identity_rows = collect_stage_identity_rows(stage_root, role)
    expected_stage_sha256 = stage_digest(stage_rows)
    static_audit_sha256 = sha256_bytes(audit_bytes)
    profile = sandbox_profile(stage_root, stage_rows, runtime_boundary)
    profile_sha256 = sha256_bytes(profile.encode("utf-8"))

    command = [
        "/usr/bin/sandbox-exec",
        "-p",
        profile,
        str(python_path),
        "-I",
        "-B",
        str(stage_root / "run_tt_target_partition.py"),
        "--role",
        role,
        "--expected-stage-sha256",
        expected_stage_sha256,
        "--static-audit-sha256",
        static_audit_sha256,
    ]
    monitor = StageMutationMonitor(stage_root, role)
    try:
        monitored_stage_rows = collect_stage_rows(stage_root, role)
        monitored_stage_identity_rows = collect_stage_identity_rows(stage_root, role)
        monitor.validate_bindings(monitored_stage_identity_rows)
        setup_mutation_events = monitor.poll()
        if (
            monitored_stage_rows != stage_rows
            or monitored_stage_identity_rows != stage_identity_rows
        ):
            raise RuntimeError("target stage changed before supervised execution")
        reject_stage_mutations(setup_mutation_events)
        before_usage = resource.getrusage(resource.RUSAGE_CHILDREN)
        wall_start = time.perf_counter_ns()
        process = subprocess.Popen(
            command,
            cwd=stage_root,
            env=EXPECTED_ENVIRONMENT,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        timed_out = False
        try:
            stdout, stderr = process.communicate(
                timeout=int(gates["wall_clock_seconds_per_partition"])
            )
        except subprocess.TimeoutExpired:
            timed_out = True
            process.kill()
            stdout, stderr = process.communicate()
        wall_clock_ns = time.perf_counter_ns() - wall_start
        after_usage = resource.getrusage(resource.RUSAGE_CHILDREN)
        if (
            before_usage.ru_utime != 0
            or before_usage.ru_stime != 0
            or before_usage.ru_maxrss != 0
        ):
            raise RuntimeError("target staging parent had prior child resource usage")
        child_usage = rusage_record(after_usage)
        post_stage_rows = collect_stage_rows(stage_root, role)
        post_stage_identity_rows = collect_stage_identity_rows(stage_root, role)
        monitor.validate_bindings(post_stage_identity_rows)
        if (
            post_stage_rows != stage_rows
            or post_stage_identity_rows != stage_identity_rows
            or stage_digest(post_stage_rows) != expected_stage_sha256
        ):
            raise RuntimeError("target stage changed while the child was running")
        post_runtime_boundary = build_runtime_boundary(python_path, backend)
        if post_runtime_boundary != runtime_boundary:
            raise RuntimeError("target parent-pinned runtime changed during the child run")
        stage_mutation_events = monitor.poll()
    finally:
        monitor.close()
    reject_stage_mutations(stage_mutation_events)
    runtime_receipt, auxiliary_stderr = parse_child_receipt(stderr)
    result = json.loads(stdout)
    if not isinstance(result, dict) or stdout != canonical_bytes(result):
        raise ValueError("target child stdout is not one canonical JSON object")
    validate_child_runtime_receipt(
        runtime_receipt,
        backend_expectations=backend_expectations,
        role=role,
        runtime_boundary=runtime_boundary,
        stage_rows=stage_rows,
        stage_sha256=expected_stage_sha256,
        static_audit_sha256=static_audit_sha256,
        stage_root=stage_root,
    )
    raw_result_sha256 = (
        sha256_file(stage_root / "target-raw-result.json")
        if role == "verifier"
        else None
    )
    validate_child_result(
        result,
        role=role,
        stdout=stdout,
        raw_result_sha256=raw_result_sha256,
    )
    if (
        process.returncode != 0
        or timed_out
        or auxiliary_stderr
    ):
        raise RuntimeError("target staged child or runtime receipt is invalid")
    if len(stdout) > int(gates["raw_result_bytes_per_partition"]):
        raise ValueError("target staged child output exceeds raw-result gate")
    if wall_clock_ns > int(gates["wall_clock_seconds_per_partition"]) * 1_000_000_000:
        raise ValueError("target staged child exceeds wall-clock gate")
    total_cpu_ns = child_usage["user_cpu_ns"] + child_usage["system_cpu_ns"]
    cpu_cap_ns = int(gates["total_cpu_hours"]) * 3600 * 1_000_000_000
    if total_cpu_ns > cpu_cap_ns:
        raise ValueError("target staged child exceeds aggregate CPU gate")
    if child_usage["maximum_rss_bytes"] > int(gates["peak_rss_bytes"]):
        raise ValueError("target staged child exceeds RSS gate")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.receipt_output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(stdout)
    receipt = {
        "artifact_freeze_authorized": False,
        "boundary": (
            "Development-only supervised target partition receipt. Direct child time, "
            "rusage, streams, pre/post stage hashes, stage vnode events, and pre/post "
            "runtime snapshots are parent-observed. File-data reads are OS-limited to "
            "literal staged paths and parent-snapshotted runtime roots; child read "
            "enumeration is diagnostic only. Concurrent runtime namespace mutation "
            "and OS shared-cache identity remain outside this model. No artifact is "
            "frozen and no campaign or cryptanalytic claim is authorized."
        ),
        "child": {
            "auxiliary_stderr_bytes": len(auxiliary_stderr),
            "command": command,
            "returncode": process.returncode,
            "rusage": child_usage,
            "runtime_receipt": runtime_receipt,
            "stderr_bytes": len(stderr),
            "stdout_bytes": len(stdout),
            "stdout_sha256": sha256_bytes(stdout),
            "timed_out": timed_out,
            "wall_clock_ns": wall_clock_ns,
        },
        "output": {
            "bytes": len(stdout),
            "path": str(args.output.resolve()),
            "sha256": sha256_bytes(stdout),
        },
        "protocol": PROTOCOL,
        "role": role,
        "schema": "tt-target-parent-runtime-receipt-development-v1",
        "os_sandbox": {
            "file_reads": (
                "default_deny_file_data; literal_stage_paths; "
                "pre_post_parent_snapshotted_runtime_roots; "
                "runtime_toctou_and_shared_cache_identity_model_limited"
            ),
            "file_writes": "denied",
            "network": "denied",
            "process_fork": "denied",
        },
        "stage": {
            "approved_files": sorted(
                approved_stage_rows,
                key=lambda row: str(row["path"]),
            ),
            "files": stage_rows,
            "identity_rows": stage_identity_rows,
            "monitored_files": monitored_stage_rows,
            "monitored_identity_rows": monitored_stage_identity_rows,
            "mutation_events": stage_mutation_events,
            "mutation_monitor": "macos_kqueue_vnode",
            "post_run_files": post_stage_rows,
            "post_run_identity_rows": post_stage_identity_rows,
            "root": str(stage_root),
            "sandbox_profile_sha256": profile_sha256,
            "setup_mutation_events": setup_mutation_events,
            "sha256": expected_stage_sha256,
            "static_audit_sha256": static_audit_sha256,
        },
        "runtime_boundary": {
            "closure_sha256": runtime_boundary["closure_sha256"],
            "post_run_closure_sha256": post_runtime_boundary["closure_sha256"],
            "record": runtime_boundary,
        },
        "valid": True,
    }
    receipt_payload = canonical_bytes(receipt)
    args.receipt_output.write_bytes(receipt_payload)
    return receipt


def main(argv: Sequence[str] | None = None) -> int:
    try:
        args = parse_args(argv)
        receipt = run(args)
    except Exception as error:
        failure = {
            "artifact_freeze_authorized": False,
            "error": {"message": str(error), "type": type(error).__name__},
            "schema": "tt-target-parent-runtime-receipt-development-failure-v1",
            "valid": False,
        }
        sys.stdout.buffer.write(canonical_bytes(failure))
        return 1
    sys.stdout.buffer.write(
        canonical_bytes(
            {
                "output": receipt["output"],
                "receipt_output": str(args.receipt_output.resolve()),
                "role": receipt["role"],
                "schema": "tt-target-parent-runtime-summary-development-v1",
                "stage_sha256": receipt["stage"]["sha256"],
                "valid": True,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
