#!/usr/bin/env python3
"""Stage and externally supervise one development target partition."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import resource
import shutil
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


def sandbox_profile(stage_root: Path, python_root: Path) -> str:
    if not stage_root.is_absolute() or not python_root.is_absolute():
        raise ValueError("target sandbox paths must be absolute")
    return "\n".join(
        (
            "(version 1)",
            "(allow default)",
            "(deny network*)",
            "(deny process-fork)",
            "(deny file-write*)",
        )
    )


def validate_child_runtime_receipt(
    receipt: Mapping[str, Any],
    *,
    role: str,
    stage_rows: Sequence[Mapping[str, Any]],
    stage_sha256: str,
    static_audit_sha256: str,
    python_root: Path,
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
    checks = backend.get("checks") if isinstance(backend, dict) else None
    if (
        not isinstance(backend, dict)
        or backend.get("valid") is not True
        or not isinstance(checks, list)
        or any(
            not isinstance(check, dict)
            or check.get("match") is not True
            or check.get("expected") != check.get("observed")
            for check in checks
        )
    ):
        raise ValueError("target child backend attestation changed")
    expected_check_fields = {
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
    }
    if {check.get("field") for check in checks} != expected_check_fields:
        raise ValueError("target child backend check set changed")
    read_rows = receipt.get("read_files")
    if not isinstance(read_rows, list) or receipt.get("read_file_count") != len(read_rows):
        raise ValueError("target child read-file receipt is malformed")
    allowed_roots = (
        stage_root.resolve(),
        python_root.resolve(),
        Path("/System/Library"),
        Path("/usr/bin"),
        Path("/usr/lib"),
        Path("/private/var/db/timezone"),
        Path("/dev/null"),
    )
    observed_paths: set[str] = set()
    for row in read_rows:
        if not isinstance(row, dict) or not isinstance(row.get("path"), str):
            raise ValueError("target child read-file row is malformed")
        path = Path(row["path"]).resolve()
        path_text = str(path)
        if path_text in observed_paths:
            raise ValueError("target child read-file receipt contains duplicates")
        observed_paths.add(path_text)
        if not any(path == root or root in path.parents for root in allowed_roots):
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


def copy_checked(source: Path, destination: Path, maximum_bytes: int) -> None:
    expected_size = source.stat().st_size
    if expected_size > maximum_bytes:
        raise ValueError(f"staged input {source.name} exceeds {maximum_bytes} bytes")
    shutil.copyfile(source, destination)
    if destination.stat().st_size != expected_size or sha256_file(destination) != sha256_file(source):
        raise ValueError(f"staged input {source.name} changed during copy")


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
    matrix_path = experiment_dir / "execution-matrix-v4.json"
    matrix_record, _ = read_object(
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

    args.staging_parent.mkdir(parents=True, exist_ok=True)
    stage_root = Path(
        tempfile.mkdtemp(
            prefix=f"tt-target-{role}-",
            dir=args.staging_parent.resolve(),
        )
    )
    for name in (*ROLE_SOURCE_FILES[role], "attest_tt_backend.py", "run_tt_target_partition.py"):
        copy_checked(source_dir / name, stage_root / name, MAX_INPUT_BYTES)
    copy_checked(matrix_path, stage_root / "execution-matrix-v4.json", MAX_INPUT_BYTES)
    copy_checked(
        experiment_dir / "target-instance-manifest-v1.json",
        stage_root / "target-instance-manifest-v1.json",
        MAX_INPUT_BYTES,
    )
    copy_checked(
        args.candidate_source_bundle.resolve(),
        stage_root / "candidate-source-bundle.json",
        MAX_INPUT_BYTES,
    )
    if role == "verifier":
        copy_checked(
            args.raw_result.resolve(),
            stage_root / "target-raw-result.json",
            MAX_RAW_BYTES,
        )
    remove_appledouble_files(stage_root)
    stage_rows = collect_stage_rows(stage_root, role)
    expected_stage_sha256 = stage_digest(stage_rows)
    static_audit_sha256 = sha256_bytes(audit_bytes)
    profile = sandbox_profile(stage_root, python_path.parent.parent)
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
    if before_usage.ru_utime != 0 or before_usage.ru_stime != 0 or before_usage.ru_maxrss != 0:
        raise RuntimeError("target staging parent had prior child resource usage")
    child_usage = rusage_record(after_usage)
    post_stage_rows = collect_stage_rows(stage_root, role)
    if post_stage_rows != stage_rows or stage_digest(post_stage_rows) != expected_stage_sha256:
        raise RuntimeError("target stage changed while the child was running")
    runtime_receipt, auxiliary_stderr = parse_child_receipt(stderr)
    result = json.loads(stdout)
    if not isinstance(result, dict) or stdout != canonical_bytes(result):
        raise ValueError("target child stdout is not one canonical JSON object")
    validate_child_runtime_receipt(
        runtime_receipt,
        role=role,
        stage_rows=stage_rows,
        stage_sha256=expected_stage_sha256,
        static_audit_sha256=static_audit_sha256,
        python_root=python_path.parent.parent,
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
            "rusage, streams, and pre/post stage hashes are parent-observed. File-read "
            "enumeration remains child-audited. No artifact is frozen and no campaign "
            "or cryptanalytic claim is authorized."
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
            "file_reads": "child_audited_not_os_enforced",
            "file_writes": "denied",
            "network": "denied",
            "process_fork": "denied",
        },
        "stage": {
            "files": stage_rows,
            "post_run_files": post_stage_rows,
            "root": str(stage_root),
            "sandbox_profile_sha256": profile_sha256,
            "sha256": expected_stage_sha256,
            "static_audit_sha256": static_audit_sha256,
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
