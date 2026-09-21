#!/usr/bin/env python3
"""Run the target-blind source compiler inside an audited staging root."""

from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from typing import Any, Mapping, Sequence


PROTOCOL = "EXP-ECDLP-TT-SOURCE-COMPILER-001"
RECEIPT_SCHEMA = "tt-source-staging-runtime-receipt-v1"
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
EXPECTED_STAGE_FILES = (
    "attest_tt_backend.py",
    "compile_tt_source_advice.py",
    "run_tt_source_partition.py",
    "source-execution-matrix-v2.json",
    "source-instance-manifest-v1.json",
    "tt_source_runtime.py",
)
FILESYSTEM_EVENT_NAMES = (
    "open",
    "stat",
    "lstat",
    "listdir",
    "scandir",
    "glob",
    "readlink",
    "chdir",
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


def sha256_file(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def stage_digest(rows: Sequence[Mapping[str, Any]]) -> str:
    digest = hashlib.sha256()
    for row in sorted(rows, key=lambda item: str(item["path"])):
        digest.update(str(row["path"]).encode("utf-8"))
        digest.update(b"\0")
        digest.update(bytes.fromhex(str(row["sha256"])))
    return digest.hexdigest()


def normalized_path(value: Any, cwd: str) -> str | None:
    if isinstance(value, int):
        return None
    try:
        raw = os.fsdecode(value)
    except (TypeError, ValueError):
        return None
    if not os.path.isabs(raw):
        raw = os.path.join(cwd, raw)
    return os.path.normpath(raw)


def path_within(path: str, root: str) -> bool:
    return path == root or path.startswith(root + os.sep)


class RuntimeAudit:
    def __init__(
        self,
        stage_root: str,
        *,
        expected_stage_files: Sequence[str] = EXPECTED_STAGE_FILES,
        cache_modules: Sequence[str] = (
            "attest_tt_backend",
            "compile_tt_source_advice",
            "tt_source_runtime",
        ),
        expected_environment_events: Sequence[Mapping[str, Any]] = (
            *EXPECTED_ENVIRONMENT_EVENTS,
        ),
    ) -> None:
        self.stage_root = stage_root
        self.cwd = stage_root
        self.expected_stage_files = tuple(expected_stage_files)
        self.expected_environment_events = tuple(expected_environment_events)
        self.stage_files = {
            os.path.join(stage_root, name) for name in self.expected_stage_files
        }
        cache_tag = sys.implementation.cache_tag
        self.cache_probe_paths = {
            os.path.join(stage_root, "__pycache__"),
            *(
                os.path.join(
                    stage_root,
                    "__pycache__",
                    f"{module}.{cache_tag}.pyc",
                )
                for module in cache_modules
            ),
        }
        self.runtime_roots = (os.path.normpath(sys.base_prefix),)
        self.runtime_files = (
            "/System/Library/CoreServices/SystemVersion.plist",
        )
        self.event_counts = {name: 0 for name in FILESYSTEM_EVENT_NAMES}
        self.event_counts.update(
            {
                "compile": 0,
                "ctypes_dlopen": 0,
                "exec": 0,
                "import": 0,
            }
        )
        self.read_paths: set[str] = set()
        self.directory_paths: set[str] = set()
        self.denied_events: list[dict[str, Any]] = []
        self.environment_events: list[dict[str, Any]] = []
        self.finalizing = False

    def allowed_path(self, path: str, *, directory: bool = False) -> bool:
        if path_within(path, self.stage_root):
            if directory:
                return path in {self.stage_root, os.path.join(self.stage_root, "__pycache__")}
            return path in self.stage_files or path in self.cache_probe_paths
        return path in self.runtime_files or any(
            path_within(path, root) for root in self.runtime_roots
        )

    def allowed_metadata_path(self, path: str) -> bool:
        if (
            path == self.stage_root
            or path in self.stage_files
            or path in self.cache_probe_paths
            or path in self.runtime_files
            or any(path_within(path, root) for root in self.runtime_roots)
        ):
            return True
        roots = (self.stage_root, *self.runtime_roots, *self.runtime_files)
        return path == os.sep or any(
            root.startswith(path + os.sep)
            for root in roots
        )

    def deny(self, event: str, detail: str) -> None:
        record = {"detail": detail, "event": event}
        self.denied_events.append(record)
        raise PermissionError(f"runtime audit denied {event}: {detail}")

    def check_path(self, event: str, value: Any, *, directory: bool = False) -> None:
        if self.finalizing:
            return
        path = normalized_path(value, self.cwd)
        if path is None:
            return
        metadata_probe = event in {"stat", "lstat", "readlink"}
        if metadata_probe:
            allowed = self.allowed_metadata_path(path)
        else:
            allowed = self.allowed_path(path, directory=directory)
        if not allowed:
            self.deny(event, path)
        self.event_counts[event] += 1
        if directory:
            self.directory_paths.add(path)
        else:
            self.read_paths.add(path)

    def audit_hook(self, event: str, args: tuple[Any, ...]) -> None:
        if self.finalizing:
            return
        if event == "open":
            path = args[0] if args else None
            mode = args[1] if len(args) > 1 else "r"
            flags = args[2] if len(args) > 2 else 0
            mode_text = mode if isinstance(mode, str) else ""
            write_mode = any(marker in mode_text for marker in ("w", "a", "x", "+"))
            if isinstance(flags, int):
                write_mask = (
                    os.O_WRONLY
                    | os.O_RDWR
                    | os.O_APPEND
                    | os.O_CREAT
                    | os.O_TRUNC
                )
                write_mode = write_mode or bool(flags & write_mask)
            if write_mode:
                self.deny("open", f"write mode for {path!r}")
            self.check_path("open", path)
            return
        if event == "os.listdir":
            self.check_path("listdir", args[0] if args else self.cwd, directory=True)
            return
        if event == "os.scandir":
            self.check_path("scandir", args[0] if args else self.cwd, directory=True)
            return
        if event == "os.chdir":
            self.check_path("chdir", args[0] if args else self.cwd, directory=True)
            return
        if event == "os.readlink":
            self.check_path("readlink", args[0] if args else None)
            return
        if event == "import":
            self.event_counts["import"] += 1
            return
        if event == "compile":
            self.event_counts["compile"] += 1
            return
        if event == "exec":
            self.event_counts["exec"] += 1
            return
        if event == "ctypes.dlopen":
            self.event_counts["ctypes_dlopen"] += 1
            return
        if event.startswith("subprocess.") or event in {
            "os.exec",
            "os.fork",
            "os.forkpty",
            "os.spawn",
            "os.system",
            "os.posix_spawn",
            "os.posix_spawnp",
            "pty.spawn",
        }:
            self.deny(event, "child processes are forbidden")
        if event.startswith("socket."):
            self.deny(event, "network access is forbidden")
        if event in {"os.putenv", "os.unsetenv"}:
            try:
                key = os.fsdecode(args[0])
                value = os.fsdecode(args[1]) if event == "os.putenv" else None
            except (IndexError, TypeError, ValueError):
                self.deny(event, "environment mutation arguments are invalid")
            observed = {"event": event, "key": key, "value": value}
            index = len(self.environment_events)
            if (
                index >= len(self.expected_environment_events)
                or observed != self.expected_environment_events[index]
            ):
                self.deny(event, f"unexpected environment mutation {observed!r}")
            self.environment_events.append(observed)
            return
        if event in {
            "os.chflags",
            "os.remove",
            "os.rename",
            "os.replace",
            "os.rmdir",
            "os.mkdir",
            "os.link",
            "os.symlink",
            "os.truncate",
            "os.chmod",
            "os.chown",
            "os.removexattr",
            "os.setxattr",
            "os.utime",
        }:
            self.deny(event, "filesystem mutation is forbidden")

    def receipt(
        self,
        *,
        static_audit_sha256: str,
        expected_stage_sha256: str,
        started_ns: int,
    ) -> dict[str, Any]:
        self.finalizing = True
        stage_rows = [
            {
                "bytes": os.path.getsize(os.path.join(self.stage_root, name)),
                "path": name,
                "sha256": sha256_file(os.path.join(self.stage_root, name)),
            }
            for name in self.expected_stage_files
        ]
        actual_stage_digest = stage_digest(stage_rows)
        read_rows: list[dict[str, Any]] = []
        for path in sorted(self.read_paths):
            try:
                if os.path.isfile(path):
                    read_rows.append(
                        {
                            "path": path,
                            "sha256": sha256_file(path),
                        }
                    )
            except OSError:
                continue
        return {
            "denied_event_count": len(self.denied_events),
            "denied_events": self.denied_events,
            "directory_paths": sorted(self.directory_paths),
            "environment": dict(sorted(os.environ.items())),
            "environment_events": self.environment_events,
            "event_counts": self.event_counts,
            "expected_stage_sha256": expected_stage_sha256,
            "filesystem_event_names": list(FILESYSTEM_EVENT_NAMES),
            "finished_ns": time.perf_counter_ns(),
            "read_file_count": len(read_rows),
            "read_files": read_rows,
            "runtime_files": list(self.runtime_files),
            "runtime_roots": list(self.runtime_roots),
            "schema": RECEIPT_SCHEMA,
            "stage_file_count": len(stage_rows),
            "stage_files": stage_rows,
            "stage_root": self.stage_root,
            "stage_root_basename": os.path.basename(self.stage_root),
            "stage_sha256": actual_stage_digest,
            "stage_started_ns": started_ns,
            "static_closure_audit_sha256": static_audit_sha256,
            "valid": (
                not self.denied_events
                and actual_stage_digest == expected_stage_sha256
                and dict(os.environ) == EXPECTED_ENVIRONMENT
                and tuple(self.environment_events) == self.expected_environment_events
            ),
        }


def parse_args(argv: Sequence[str]) -> dict[str, str]:
    values: dict[str, str] = {}
    index = 0
    while index < len(argv):
        flag = argv[index]
        if flag not in {
            "--execution-matrix",
            "--expected-stage-sha256",
            "--manifest",
            "--static-audit-sha256",
        }:
            raise ValueError(f"unexpected argument {flag!r}")
        if index + 1 >= len(argv):
            raise ValueError(f"missing value for {flag}")
        values[flag] = argv[index + 1]
        index += 2
    required = {
        "--execution-matrix",
        "--expected-stage-sha256",
        "--manifest",
        "--static-audit-sha256",
    }
    if set(values) != required:
        raise ValueError("staging runtime arguments are incomplete")
    for key in ("--expected-stage-sha256", "--static-audit-sha256"):
        if len(values[key]) != 64 or any(char not in "0123456789abcdef" for char in values[key]):
            raise ValueError(f"{key} is not a SHA-256 digest")
    return values


def install_path_wrappers(audit: RuntimeAudit) -> None:
    original_stat = os.stat
    original_lstat = os.lstat
    original_readlink = os.readlink

    def wrapped_stat(path: Any, *args: Any, **kwargs: Any) -> Any:
        audit.check_path("stat", path)
        return original_stat(path, *args, **kwargs)

    def wrapped_lstat(path: Any, *args: Any, **kwargs: Any) -> Any:
        audit.check_path("lstat", path)
        return original_lstat(path, *args, **kwargs)

    def wrapped_readlink(path: Any, *args: Any, **kwargs: Any) -> Any:
        audit.check_path("readlink", path)
        return original_readlink(path, *args, **kwargs)

    os.stat = wrapped_stat  # type: ignore[assignment]
    os.lstat = wrapped_lstat  # type: ignore[assignment]
    os.readlink = wrapped_readlink  # type: ignore[assignment]


def emit(value: Mapping[str, Any]) -> None:
    sys.stdout.buffer.write(canonical_bytes(value))
    sys.stdout.buffer.flush()


def main(argv: Sequence[str] | None = None) -> int:
    arguments = parse_args(list(sys.argv[1:] if argv is None else argv))
    stage_root = os.path.normpath(os.path.dirname(os.path.abspath(__file__)))
    if os.path.normpath(os.getcwd()) != stage_root:
        raise RuntimeError("source partition did not start in its staging root")
    observed_files = tuple(sorted(os.listdir(stage_root)))
    if observed_files != tuple(sorted(EXPECTED_STAGE_FILES)):
        raise RuntimeError("staging root file set differs from the frozen allowlist")

    os.environ.clear()
    os.environ.update(EXPECTED_ENVIRONMENT)
    if dict(os.environ) != EXPECTED_ENVIRONMENT:
        raise RuntimeError("source environment could not be reduced to the frozen allowlist")
    if stage_root not in sys.path:
        sys.path.insert(0, stage_root)

    audit = RuntimeAudit(stage_root)
    install_path_wrappers(audit)
    sys.addaudithook(audit.audit_hook)
    started_ns = time.perf_counter_ns()

    from compile_tt_source_advice import run_compiler
    from pathlib import Path

    raw = run_compiler(
        Path(arguments["--manifest"]),
        Path(arguments["--execution-matrix"]),
    )
    receipt = audit.receipt(
        static_audit_sha256=arguments["--static-audit-sha256"],
        expected_stage_sha256=arguments["--expected-stage-sha256"],
        started_ns=started_ns,
    )
    if not receipt["valid"]:
        raise RuntimeError(
            "staging runtime receipt is invalid: "
            + json.dumps(
                {
                    "denied_events": receipt["denied_events"],
                    "environment_matches": receipt["environment"]
                    == EXPECTED_ENVIRONMENT,
                    "stage_digest_matches": receipt["stage_sha256"]
                    == receipt["expected_stage_sha256"],
                },
                sort_keys=True,
                separators=(",", ":"),
            )
        )
    capability = raw["capability_audit"]
    capability.update(
        {
            "ast_call_graph_audit_passed": True,
            "environment_audit_passed": True,
            "filesystem_audit_passed": True,
            "isolated_staging_root": True,
            "repository_git_metadata_present": False,
            "runtime_receipt": receipt,
            "target_or_mutation_files_present": False,
        }
    )
    raw["provenance"]["runtime_receipt_sha256"] = hashlib.sha256(
        canonical_bytes(receipt)
    ).hexdigest()
    raw["summary"]["implementation_gate"] = "isolated_source_partition_preflight"
    emit(raw)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
