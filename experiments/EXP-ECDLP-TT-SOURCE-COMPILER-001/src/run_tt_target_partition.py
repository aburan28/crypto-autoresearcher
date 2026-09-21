#!/usr/bin/env python3
"""Run one target role in an OS write-blocked, hash-audited development stage."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import sys
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
COMMON_STAGE_FILES = (
    "attest_tt_backend.py",
    "candidate-source-bundle.json",
    "execution-matrix-v4.json",
    "run_tt_target_partition.py",
    "target-instance-manifest-v1.json",
)
ROLE_FILES = {
    "producer": (
        "compile_tt_target_advice.py",
        "tt_target_coefficients.py",
        "tt_target_runtime.py",
    ),
    "verifier": ("target-raw-result.json", "verify_tt_target_advice.py"),
}
FILESYSTEM_EVENT_NAMES = (
    "open",
    "stat",
    "lstat",
    "listdir",
    "scandir",
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


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
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
    def __init__(self, stage_root: str, role: str) -> None:
        self.stage_root = stage_root
        self.role = role
        self.cwd = stage_root
        expected_names = tuple(sorted((*COMMON_STAGE_FILES, *ROLE_FILES[role])))
        self.expected_names = expected_names
        self.stage_files = {
            os.path.join(stage_root, name) for name in expected_names
        }
        cache_tag = sys.implementation.cache_tag
        modules = tuple(
            name[:-3]
            for name in expected_names
            if name.endswith(".py")
        )
        self.cache_probe_paths = {
            os.path.join(stage_root, "__pycache__"),
            *(
                os.path.join(
                    stage_root,
                    "__pycache__",
                    f"{module}.{cache_tag}.pyc",
                )
                for module in modules
            ),
        }
        self.runtime_roots = (os.path.normpath(sys.base_prefix),)
        self.runtime_files = (
            "/System/Library/CoreServices/SystemVersion.plist",
        )
        self.event_counts = {name: 0 for name in FILESYSTEM_EVENT_NAMES}
        self.event_counts.update(
            {"compile": 0, "ctypes_dlopen": 0, "exec": 0, "import": 0}
        )
        self.read_paths: set[str] = set()
        self.directory_paths: set[str] = set()
        self.denied_events: list[dict[str, Any]] = []
        self.environment_events: list[dict[str, Any]] = []
        self.finalizing = False

    def allowed_path(self, path: str, *, directory: bool = False) -> bool:
        if path_within(path, self.stage_root):
            if directory:
                return path in {
                    self.stage_root,
                    os.path.join(self.stage_root, "__pycache__"),
                }
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
            root.startswith(path + os.sep) for root in roots
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
        if event in {"stat", "lstat", "readlink"}:
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
                index >= len(EXPECTED_ENVIRONMENT_EVENTS)
                or observed != EXPECTED_ENVIRONMENT_EVENTS[index]
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
        backend_attestation: Mapping[str, Any],
        expected_stage_sha256: str,
        static_audit_sha256: str,
        started_ns: int,
    ) -> dict[str, Any]:
        self.finalizing = True
        stage_rows = [
            {
                "bytes": os.path.getsize(os.path.join(self.stage_root, name)),
                "path": name,
                "sha256": sha256_file(os.path.join(self.stage_root, name)),
            }
            for name in self.expected_names
        ]
        actual_stage_sha256 = stage_digest(stage_rows)
        read_rows: list[dict[str, Any]] = []
        for path in sorted(self.read_paths):
            try:
                if os.path.isfile(path):
                    read_rows.append({"path": path, "sha256": sha256_file(path)})
            except OSError:
                continue
        return {
            "backend_attestation": backend_attestation,
            "denied_event_count": len(self.denied_events),
            "denied_events": self.denied_events,
            "directory_paths": sorted(self.directory_paths),
            "environment": dict(sorted(os.environ.items())),
            "environment_events": self.environment_events,
            "event_counts": self.event_counts,
            "expected_stage_sha256": expected_stage_sha256,
            "finished_ns": time.perf_counter_ns(),
            "read_file_count": len(read_rows),
            "read_files": read_rows,
            "role": self.role,
            "runtime_files": list(self.runtime_files),
            "runtime_roots": list(self.runtime_roots),
            "schema": "tt-target-child-runtime-receipt-development-v1",
            "stage_file_count": len(stage_rows),
            "stage_files": stage_rows,
            "stage_root": self.stage_root,
            "stage_sha256": actual_stage_sha256,
            "stage_started_ns": started_ns,
            "static_closure_audit_sha256": static_audit_sha256,
            "valid": (
                not self.denied_events
                and actual_stage_sha256 == expected_stage_sha256
                and dict(os.environ) == EXPECTED_ENVIRONMENT
                and tuple(self.environment_events) == EXPECTED_ENVIRONMENT_EVENTS
                and backend_attestation.get("valid") is True
            ),
        }


def parse_args(argv: Sequence[str]) -> dict[str, str]:
    values: dict[str, str] = {}
    index = 0
    allowed = {
        "--expected-stage-sha256",
        "--role",
        "--static-audit-sha256",
    }
    while index < len(argv):
        flag = argv[index]
        if flag not in allowed or index + 1 >= len(argv):
            raise ValueError(f"unexpected or incomplete target runtime argument {flag!r}")
        values[flag] = argv[index + 1]
        index += 2
    if set(values) != allowed or values["--role"] not in ROLE_FILES:
        raise ValueError("target runtime arguments are incomplete")
    for key in ("--expected-stage-sha256", "--static-audit-sha256"):
        value = values[key]
        if len(value) != 64 or any(char not in "0123456789abcdef" for char in value):
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


def build_backend_attestation(matrix_path: Path) -> dict[str, Any]:
    import attest_tt_backend as backend

    matrix_record = json.loads(matrix_path.read_bytes())
    matrix = matrix_record.get("execution_matrix")
    if not isinstance(matrix, dict) or not isinstance(matrix.get("backend_gate"), dict):
        raise ValueError("target execution matrix backend gate is malformed")
    expected = matrix["backend_gate"]
    executable = Path(sys.executable)
    members, closure_digest = backend.numpy_distribution_closure()
    multiarray_path = Path(backend._multiarray_umath.__file__).resolve()
    dyld_images = backend.loaded_dyld_images()
    expected_loaders = expected["os_loader_dependencies"]
    thread_environment = {
        name: os.environ.get(name) for name in backend.THREAD_ENVIRONMENT
    }
    observed_thread_count = all(
        thread_environment[name] == "1"
        for name in backend.THREAD_ENVIRONMENT[1:]
    )
    checks = [
        backend.compare(expected["python_executable"], str(executable), "python_executable"),
        backend.compare(
            expected["python_executable_sha256"],
            backend.sha256_file(executable),
            "python_executable_sha256",
        ),
        backend.compare(expected["python_version"], platform.python_version(), "python_version"),
        backend.compare(expected["platform"], backend.normalized_platform(), "platform"),
        backend.compare(expected["machine"], platform.machine(), "machine"),
        backend.compare(expected["numpy_version"], backend.np.__version__, "numpy_version"),
        backend.compare(
            expected["numpy_distribution_file_count"],
            len(members),
            "numpy_distribution_file_count",
        ),
        backend.compare(
            expected["numpy_installed_closure_sha256"],
            closure_digest,
            "numpy_installed_closure_sha256",
        ),
        backend.compare(
            expected["numpy_multiarray_umath_sha256"],
            backend.sha256_file(multiarray_path),
            "numpy_multiarray_umath_sha256",
        ),
        backend.compare(
            True,
            all(path in dyld_images for path in expected_loaders),
            "os_loader_dependencies_loaded",
        ),
        backend.compare(
            expected["thread_count"],
            1 if observed_thread_count else None,
            "thread_count",
        ),
    ]
    return {
        "checks": checks,
        "loaded_numpy_extensions": backend.loaded_numpy_extensions(),
        "numpy_distribution_file_count": len(members),
        "numpy_installed_closure_sha256": closure_digest,
        "numpy_multiarray_umath": {
            "path": str(multiarray_path),
            "sha256": backend.sha256_file(multiarray_path),
        },
        "os_loader_images": dyld_images,
        "protocol": f"{PROTOCOL}-TARGET-BACKEND-ATTESTATION-DEVELOPMENT-V1",
        "thread_environment": thread_environment,
        "valid": all(check["match"] for check in checks),
    }


def run_role(role: str, stage_root: Path) -> dict[str, Any]:
    if role == "producer":
        import argparse
        import compile_tt_target_advice as producer

        return producer.compile_development(
            argparse.Namespace(
                candidate_source_bundle=stage_root / "candidate-source-bundle.json",
                execution_matrix=stage_root / "execution-matrix-v4.json",
                target_manifest=stage_root / "target-instance-manifest-v1.json",
            )
        )
    import argparse
    import verify_tt_target_advice as verifier

    return verifier.verify(
        argparse.Namespace(
            candidate_source_bundle=stage_root / "candidate-source-bundle.json",
            execution_matrix=stage_root / "execution-matrix-v4.json",
            raw_result=stage_root / "target-raw-result.json",
            target_manifest=stage_root / "target-instance-manifest-v1.json",
        )
    )


def main(argv: Sequence[str] | None = None) -> int:
    arguments = parse_args(list(sys.argv[1:] if argv is None else argv))
    role = arguments["--role"]
    stage_root = Path(__file__).resolve().parent
    if Path.cwd().resolve() != stage_root:
        raise RuntimeError("target partition did not start in its staging root")
    expected_names = tuple(sorted((*COMMON_STAGE_FILES, *ROLE_FILES[role])))
    if tuple(sorted(path.name for path in stage_root.iterdir())) != expected_names:
        raise RuntimeError("target staging root file set differs from its role allowlist")

    os.environ.clear()
    os.environ.update(EXPECTED_ENVIRONMENT)
    if dict(os.environ) != EXPECTED_ENVIRONMENT:
        raise RuntimeError("target environment could not be reduced to its allowlist")
    if str(stage_root) not in sys.path:
        sys.path.insert(0, str(stage_root))

    audit = RuntimeAudit(str(stage_root), role)
    install_path_wrappers(audit)
    sys.addaudithook(audit.audit_hook)
    started_ns = time.perf_counter_ns()
    backend_attestation = build_backend_attestation(
        stage_root / "execution-matrix-v4.json"
    )
    if backend_attestation.get("valid") is not True:
        raise RuntimeError("target backend attestation failed")
    backend_dlopen_events = audit.event_counts["ctypes_dlopen"]
    result = run_role(role, stage_root)
    if audit.event_counts["ctypes_dlopen"] != backend_dlopen_events:
        raise RuntimeError("target role loaded a dynamic library after backend attestation")
    receipt = audit.receipt(
        backend_attestation=backend_attestation,
        expected_stage_sha256=arguments["--expected-stage-sha256"],
        static_audit_sha256=arguments["--static-audit-sha256"],
        started_ns=started_ns,
    )
    if not receipt["valid"]:
        raise RuntimeError("target child runtime receipt is invalid")
    result_payload = canonical_bytes(result)
    if role == "producer" and len(result_payload) != result["summary"]["serialized_bytes"]:
        raise RuntimeError("staged target producer serialized-byte count changed")
    sys.stderr.buffer.write(RECEIPT_PREFIX + canonical_bytes(receipt))
    sys.stderr.buffer.flush()
    sys.stdout.buffer.write(result_payload)
    sys.stdout.buffer.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
