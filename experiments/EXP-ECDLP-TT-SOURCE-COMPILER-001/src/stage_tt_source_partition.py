#!/usr/bin/env python3
"""Stage and externally supervise the development source partition."""

from __future__ import annotations

import argparse
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

import audit_tt_source_closure as source_auditor
import stage_tt_target_partition as supervisor


PROTOCOL = "EXP-ECDLP-TT-SOURCE-COMPILER-001"
EXPECTED_ENVIRONMENT = supervisor.EXPECTED_ENVIRONMENT
EXPECTED_ENVIRONMENT_EVENTS = supervisor.EXPECTED_ENVIRONMENT_EVENTS
SOURCE_FILES = (
    "attest_tt_backend.py",
    "compile_tt_source_advice.py",
    "run_tt_source_partition.py",
    "tt_source_runtime.py",
)
VERIFIER_SOURCE_FILES = (
    "run_tt_source_partition.py",
    "run_tt_source_verifier_partition.py",
    "verify_tt_source_advice.py",
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
EXPECTED_HARNESS_FILES = (
    "audit_tt_source_closure.py",
    "run_tt_source_partition.py",
    "run_tt_source_verifier_partition.py",
    "stage_tt_source_partition.py",
    "stage_tt_target_partition.py",
)
POLICY_FILE_NAMES = (
    "contract-v5.md",
    "source-execution-matrix-v2.json",
    "execution-matrix-v4.json",
    "mutation-manifest-v4.json",
    "source-instance-manifest-v1.json",
    "target-instance-manifest-v1.json",
)
ROLE_SOURCE_FILES = {
    "producer": SOURCE_FILES,
    "verifier": VERIFIER_SOURCE_FILES,
}
ROLE_EXTRA_FILES = {
    "producer": (),
    "verifier": ("source-generator-raw-result.json",),
}
MAX_INPUT_BYTES = 16 * 1024 * 1024
MAX_RAW_BYTES = 256 * 1024 * 1024
MAX_VERIFIER_STDERR_BYTES = 4 * 1024 * 1024
SOURCE_VERIFIER_RECEIPT_PREFIX = b"TT_SOURCE_VERIFIER_RUNTIME_RECEIPT\t"
SOURCE_BACKEND_CHECK_FIELDS = (
    "array_order_contract",
    "dtype_contract",
    "machine",
    "numpy_distribution_file_count",
    "numpy_installed_closure_sha256",
    "numpy_multiarray_umath_sha256",
    "numpy_version",
    "os_loader_dependencies_loaded",
    "platform",
    "python_executable",
    "python_executable_sha256",
    "python_hash_seed_deterministic",
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
    return supervisor.sha256_file(path)


def stage_digest(rows: Sequence[Mapping[str, Any]]) -> str:
    return supervisor.stage_digest(rows)


def retain_policy_payloads(experiment_dir: Path) -> dict[str, bytes]:
    return {
        name: supervisor.read_stable_bytes(
            experiment_dir / name,
            f"source static-audit policy input {name}",
            MAX_INPUT_BYTES,
        )
        for name in POLICY_FILE_NAMES
    }


def regenerate_static_closure_audit(
    experiment_dir: Path,
    source_dir: Path,
) -> dict[str, Any]:
    policy = source_auditor.load_policy(
        experiment_dir / "contract-v5.md",
        experiment_dir / "source-execution-matrix-v2.json",
        experiment_dir / "execution-matrix-v4.json",
        experiment_dir / "mutation-manifest-v4.json",
        experiment_dir / "source-instance-manifest-v1.json",
        experiment_dir / "target-instance-manifest-v1.json",
    )
    report, status = source_auditor.build_audit_report(
        policy,
        source_dir,
        {
            source_auditor.ROLE_PRODUCER: source_dir
            / "compile_tt_source_advice.py",
            source_auditor.ROLE_VERIFIER: source_dir
            / "verify_tt_source_advice.py",
        },
    )
    if status != 0 or report.get("valid") is not True:
        raise ValueError("fresh parent static source audit did not pass")
    return report


def expected_policy_hash_rows(
    policy_payloads: Mapping[str, bytes],
) -> list[dict[str, str]]:
    if set(policy_payloads) != set(POLICY_FILE_NAMES):
        raise ValueError("retained static-audit policy input set changed")
    return [
        {"path": name, "sha256": sha256_bytes(policy_payloads[name])}
        for name in sorted(POLICY_FILE_NAMES)
    ]


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
    experiment_dir: Path,
    policy_payloads: Mapping[str, bytes],
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
    expected_payload_sha256 = sha256_bytes(canonical_bytes(payload)[:-1])
    if payload_sha256 != expected_payload_sha256:
        raise ValueError("static closure audit payload digest changed")
    policy = audit.get("policy")
    if (
        not isinstance(policy, dict)
        or policy.get("policy_file_hashes")
        != expected_policy_hash_rows(policy_payloads)
    ):
        raise ValueError("static closure audit policy hashes changed")
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

    harness = audit.get("harness")
    if not isinstance(harness, dict) or not isinstance(harness.get("files"), list):
        raise ValueError("static source harness closure is missing")
    harness_rows = {
        row.get("path"): row
        for row in harness["files"]
        if isinstance(row, dict) and isinstance(row.get("path"), str)
    }
    if set(harness_rows) != set(EXPECTED_HARNESS_FILES):
        raise ValueError("static source harness file set changed")
    for name in EXPECTED_HARNESS_FILES:
        path = source_dir / name
        row = harness_rows[name]
        if (
            row.get("bytes") != path.stat().st_size
            or row.get("sha256") != sha256_file(path)
        ):
            raise ValueError(f"static source harness changed for {name}")
    if harness.get("closure_sha256") != stage_digest(list(harness_rows.values())):
        raise ValueError("static source harness closure digest changed")
    fresh_audit = regenerate_static_closure_audit(experiment_dir, source_dir)
    if audit != fresh_audit:
        raise ValueError("static closure audit differs from fresh parent replay")
    if retain_policy_payloads(experiment_dir) != dict(policy_payloads):
        raise ValueError("static closure audit policy inputs changed during replay")


def remove_appledouble_files(stage_root: Path) -> None:
    for path in stage_root.iterdir():
        if path.name.startswith("._"):
            path.unlink()


def expected_stage_names(role: str = "producer") -> tuple[str, ...]:
    return tuple(
        sorted((*ROLE_SOURCE_FILES[role], *DATA_FILES, *ROLE_EXTRA_FILES[role]))
    )


def collect_stage_rows(
    stage_root: Path,
    role: str = "producer",
) -> list[dict[str, Any]]:
    observed_names = tuple(sorted(path.name for path in stage_root.iterdir()))
    if observed_names != expected_stage_names(role):
        raise RuntimeError("source staged file set differs from its allowlist")
    return [
        {
            "bytes": (stage_root / name).stat().st_size,
            "path": name,
            "sha256": sha256_file(stage_root / name),
        }
        for name in observed_names
    ]


def validate_staged_file_set(
    stage_root: Path,
    role: str = "producer",
) -> tuple[str, ...]:
    collect_stage_rows(stage_root, role)
    return expected_stage_names(role)


def collect_stage_identity_rows(
    stage_root: Path,
    role: str = "producer",
) -> list[dict[str, Any]]:
    resolved_root = stage_root.resolve()
    observed_names = tuple(sorted(path.name for path in resolved_root.iterdir()))
    if observed_names != expected_stage_names(role):
        raise RuntimeError("source staged identity set differs from its allowlist")
    paths = [(".", resolved_root), *[(name, resolved_root / name) for name in observed_names]]
    rows: list[dict[str, Any]] = []
    for name, path in paths:
        metadata = path.stat(follow_symlinks=False)
        expected_kind = (
            stat.S_ISDIR(metadata.st_mode)
            if name == "."
            else stat.S_ISREG(metadata.st_mode)
        )
        if not expected_kind:
            raise ValueError(f"source staged path has the wrong vnode type: {name}")
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
    """Hold source-stage vnodes open and retain namespace/content events."""

    def __init__(self, stage_root: Path, role: str = "producer") -> None:
        if sys.platform != "darwin" or not hasattr(select, "kqueue"):
            raise RuntimeError("source stage mutation monitoring requires macOS kqueue")
        self.stage_root = stage_root.resolve()
        self.role = role
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
                raise RuntimeError("source staged file set changed before monitoring")
            for name in observed_names:
                self._register(
                    self.stage_root / name,
                    name,
                    expect_directory=False,
                )
            self.validate_bindings(
                collect_stage_identity_rows(self.stage_root, role)
            )
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
            raise RuntimeError(f"source stage vnode binding changed during setup: {name}")
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
            raise RuntimeError("source stage path identities differ from watched vnodes")

    def poll(self) -> list[dict[str, Any]]:
        if self._closed:
            raise RuntimeError("source stage mutation monitor is closed")
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
        raise RuntimeError("source stage mutated while the child was running")


def approved_source_payloads(
    audit: Mapping[str, Any],
    source_dir: Path,
    role: str = "producer",
) -> dict[str, bytes]:
    role_record = audit["roles"][role]
    role_digests = {
        row["path"]: row["sha256"] for row in role_record["closure_files"]
    }
    harness_digests = {
        row["path"]: row["sha256"] for row in audit["harness"]["files"]
    }
    expected_digests = (
        {
            **{name: role_digests[name] for name in PRODUCER_CLOSURE_FILES},
            "run_tt_source_partition.py": harness_digests[
                "run_tt_source_partition.py"
            ],
        }
        if role == "producer"
        else {
            "run_tt_source_partition.py": harness_digests[
                "run_tt_source_partition.py"
            ],
            "run_tt_source_verifier_partition.py": harness_digests[
                "run_tt_source_verifier_partition.py"
            ],
            "verify_tt_source_advice.py": role_digests[
                "verify_tt_source_advice.py"
            ],
        }
    )
    payloads: dict[str, bytes] = {}
    for name, expected_digest in expected_digests.items():
        payload = supervisor.read_stable_bytes(
            source_dir / name,
            f"approved source file {name}",
            MAX_INPUT_BYTES,
        )
        if sha256_bytes(payload) != expected_digest:
            raise ValueError(f"approved source file changed before staging: {name}")
        payloads[name] = payload
    return payloads


def validate_approved_stage_manifest(
    approved_rows: Sequence[Mapping[str, Any]],
    observed_rows: Sequence[Mapping[str, Any]],
) -> None:
    supervisor.validate_approved_stage_manifest(approved_rows, observed_rows)


def source_backend_expectations(backend_gate: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "array_order_contract": backend_gate["array_order"],
        "dtype_contract": backend_gate["dtype"],
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
        "python_hash_seed_deterministic": True,
        "python_version": backend_gate["python_version"],
        "thread_count": backend_gate["thread_count"],
    }


def validate_source_backend_attestation(
    record: Any,
    *,
    backend_gate: Mapping[str, Any],
    matrix_sha256: str,
    runtime_boundary: Mapping[str, Any],
) -> None:
    if (
        not isinstance(record, dict)
        or record.get("protocol")
        != "EXP-ECDLP-TT-SOURCE-COMPILER-001-BACKEND-ATTESTATION-V1"
        or record.get("valid") is not True
        or set(record)
        != {
            "boundary",
            "checks",
            "observed",
            "protocol",
            "source_execution_matrix",
            "valid",
        }
    ):
        raise ValueError("source child backend attestation changed")
    matrix = record.get("source_execution_matrix")
    if matrix != {
        "path": "source-execution-matrix-v2.json",
        "sha256": matrix_sha256,
    }:
        raise ValueError("source child backend matrix binding changed")
    checks = record.get("checks")
    expected_values = source_backend_expectations(backend_gate)
    if not isinstance(checks, list) or len(checks) != len(SOURCE_BACKEND_CHECK_FIELDS):
        raise ValueError("source child backend check set changed")
    by_field: dict[str, Mapping[str, Any]] = {}
    for check in checks:
        if (
            not isinstance(check, dict)
            or set(check) != {"expected", "field", "match", "observed"}
            or not isinstance(check.get("field"), str)
            or check["field"] in by_field
        ):
            raise ValueError("source child backend check schema changed")
        by_field[check["field"]] = check
    if set(by_field) != set(SOURCE_BACKEND_CHECK_FIELDS):
        raise ValueError("source child backend check fields changed")
    for field in SOURCE_BACKEND_CHECK_FIELDS:
        expected = expected_values[field]
        check = by_field[field]
        if (
            check.get("match") is not True
            or type(check.get("expected")) is not type(expected)
            or type(check.get("observed")) is not type(expected)
            or check.get("expected") != expected
            or check.get("observed") != expected
        ):
            raise ValueError(f"source child backend value changed for {field}")

    observed = record.get("observed")
    if not isinstance(observed, dict):
        raise ValueError("source child backend observations are missing")
    members = observed.get("numpy_distribution_members")
    expected_distribution = runtime_boundary.get("numpy_distribution")
    if not isinstance(members, list) or not isinstance(expected_distribution, dict):
        raise ValueError("source child NumPy distribution observation changed")
    member_digest = hashlib.sha256()
    seen: set[str] = set()
    previous = ""
    for row in members:
        if (
            not isinstance(row, dict)
            or set(row) != {"bytes", "path", "sha256"}
            or not isinstance(row.get("path"), str)
            or not isinstance(row.get("bytes"), int)
            or row["bytes"] < 0
            or not isinstance(row.get("sha256"), str)
            or len(row["sha256"]) != 64
            or any(char not in "0123456789abcdef" for char in row["sha256"])
            or row["path"] in seen
            or row["path"] < previous
        ):
            raise ValueError("source child NumPy distribution row changed")
        seen.add(row["path"])
        previous = row["path"]
        member_digest.update(row["path"].encode("utf-8"))
        member_digest.update(b"\0")
        member_digest.update(bytes.fromhex(row["sha256"]))
    if (
        len(members) != expected_distribution.get("file_count")
        or member_digest.hexdigest() != expected_distribution.get("sha256")
        or observed.get("numpy_installed_closure_sha256")
        != expected_distribution.get("sha256")
    ):
        raise ValueError("source child NumPy distribution closure changed")
    multiarray = observed.get("numpy_multiarray_umath")
    if (
        not isinstance(multiarray, dict)
        or set(multiarray) != {"path", "sha256"}
        or multiarray.get("sha256") != backend_gate["numpy_multiarray_umath_sha256"]
    ):
        raise ValueError("source child NumPy multiarray identity changed")
    loaded_extensions = observed.get("loaded_numpy_extensions")
    if not isinstance(loaded_extensions, list) or [
        row.get("sha256")
        for row in loaded_extensions
        if isinstance(row, dict) and "_multiarray_umath" in str(row.get("path"))
    ] != [backend_gate["numpy_multiarray_umath_sha256"]]:
        raise ValueError("source child loaded extension identity changed")
    expected_loaders = backend_gate["os_loader_dependencies"]
    loaded_images = observed.get("loaded_os_images")
    if (
        observed.get("expected_os_loader_dependencies") != expected_loaders
        or not isinstance(loaded_images, list)
        or any(loader not in loaded_images for loader in expected_loaders)
    ):
        raise ValueError("source child loader observation changed")
    if observed.get("thread_environment") != EXPECTED_ENVIRONMENT:
        raise ValueError("source child backend environment changed")


def validate_producer_child_result(
    result: Mapping[str, Any],
    *,
    backend_gate: Mapping[str, Any],
    matrix_sha256: str,
    runtime_boundary: Mapping[str, Any],
    stage_rows: Sequence[Mapping[str, Any]],
    stage_sha256: str,
    static_audit_sha256: str,
    stage_root: Path,
) -> None:
    claims = result.get("claim_boundary")
    capability = result.get("capability_audit")
    provenance = result.get("provenance")
    summary = result.get("summary")
    if (
        result.get("schema") != "tt-source-compiler-raw-v1"
        or result.get("protocol") != PROTOCOL
        or result.get("partition") != "source_generator"
        or result.get("valid") is not True
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
        or not isinstance(capability, dict)
        or not isinstance(provenance, dict)
        or not isinstance(summary, dict)
        or summary.get("source_cells") != 7
        or summary.get("source_tensor_records") != 63
        or summary.get("implementation_gate") != "isolated_source_partition_preflight"
    ):
        raise ValueError("source child result boundary changed")
    for key in (
        "ast_call_graph_audit_passed",
        "environment_audit_passed",
        "filesystem_audit_passed",
        "isolated_staging_root",
    ):
        if capability.get(key) is not True:
            raise ValueError(f"source child capability did not pass: {key}")
    if (
        capability.get("repository_git_metadata_present") is not False
        or capability.get("target_or_mutation_files_present") is not False
    ):
        raise ValueError("source child phase boundary changed")

    receipt = capability.get("runtime_receipt")
    if not isinstance(receipt, dict):
        raise ValueError("source child runtime receipt is missing")
    if (
        receipt.get("schema") != "tt-source-staging-runtime-receipt-v1"
        or receipt.get("valid") is not True
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
        raise ValueError("source child runtime receipt boundary changed")
    if provenance.get("runtime_receipt_sha256") != sha256_bytes(canonical_bytes(receipt)):
        raise ValueError("source child runtime receipt digest changed")

    validate_source_backend_attestation(
        result.get("backend_attestation"),
        backend_gate=backend_gate,
        matrix_sha256=matrix_sha256,
        runtime_boundary=runtime_boundary,
    )
    read_rows = receipt.get("read_files")
    if not isinstance(read_rows, list) or receipt.get("read_file_count") != len(read_rows):
        raise ValueError("source child read-file receipt is malformed")
    read_filters = runtime_boundary.get("read_filters")
    if not isinstance(read_filters, list) or any(
        not isinstance(item, dict) for item in read_filters
    ):
        raise ValueError("source parent runtime read filters are malformed")
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
            raise ValueError("source child read-file row is malformed")
        path = Path(row["path"]).resolve()
        path_text = str(path)
        if path_text in observed_paths:
            raise ValueError("source child read-file receipt contains duplicates")
        observed_paths.add(path_text)
        if not any(
            supervisor.runtime_filter_allows(path, item) for item in effective_filters
        ):
            raise ValueError(f"source child read escaped allowed roots: {path}")
        if not path.is_file() or row.get("sha256") != sha256_file(path):
            raise ValueError(f"source child read-file digest changed: {path}")


def parse_source_verifier_receipt(stderr: bytes) -> tuple[dict[str, Any], bytes]:
    if len(stderr) > MAX_VERIFIER_STDERR_BYTES:
        raise ValueError("source verifier runtime receipt exceeds its byte gate")
    if not stderr.startswith(SOURCE_VERIFIER_RECEIPT_PREFIX):
        raise ValueError("source verifier did not emit a runtime receipt")
    receipt_payload = stderr[len(SOURCE_VERIFIER_RECEIPT_PREFIX) :]
    receipt = json.loads(receipt_payload)
    if not isinstance(receipt, dict) or receipt_payload != canonical_bytes(receipt):
        raise ValueError("source verifier runtime receipt framing is not exact canonical JSON")
    return receipt, b""


def validate_verifier_child_result(
    result: Mapping[str, Any],
    receipt: Mapping[str, Any],
    *,
    raw_result_sha256: str,
    runtime_boundary: Mapping[str, Any],
    stage_rows: Sequence[Mapping[str, Any]],
    stage_sha256: str,
    static_audit_sha256: str,
    stage_root: Path,
    stdout: bytes,
) -> None:
    if (
        result.get("schema")
        != "tt-source-strict-preflight-development-verification-v1"
        or result.get("protocol") != PROTOCOL
        or result.get("partition")
        != "source_verifier_strict_preflight_development"
        or result.get("valid") is not True
        or result.get("artifact_freeze_authorized") is not False
        or result.get("raw_result_sha256") != raw_result_sha256
        or not isinstance(result.get("audits"), dict)
        or not isinstance(result.get("candidate_artifact_digests"), dict)
        or not isinstance(result.get("verifier_accounting"), dict)
    ):
        raise ValueError("source verifier child result boundary changed")
    if (
        receipt.get("schema") != "tt-source-staging-runtime-receipt-v1"
        or receipt.get("role") != "verifier"
        or receipt.get("valid") is not True
        or receipt.get("result_sha256") != sha256_bytes(stdout)
        or receipt.get("expected_stage_sha256") != stage_sha256
        or receipt.get("stage_sha256") != stage_sha256
        or receipt.get("static_closure_audit_sha256") != static_audit_sha256
        or receipt.get("denied_event_count") != 0
        or receipt.get("denied_events") != []
        or receipt.get("environment") != EXPECTED_ENVIRONMENT
        or receipt.get("environment_events") != []
        or receipt.get("stage_files") != list(stage_rows)
        or receipt.get("stage_file_count") != len(stage_rows)
        or receipt.get("stage_root") != str(stage_root.resolve())
    ):
        raise ValueError("source verifier child runtime receipt boundary changed")
    read_rows = receipt.get("read_files")
    if not isinstance(read_rows, list) or receipt.get("read_file_count") != len(read_rows):
        raise ValueError("source verifier read-file receipt is malformed")
    read_filters = runtime_boundary.get("read_filters")
    if not isinstance(read_filters, list) or any(
        not isinstance(item, dict) for item in read_filters
    ):
        raise ValueError("source verifier runtime read filters are malformed")
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
            raise ValueError("source verifier read-file row is malformed")
        path = Path(row["path"]).resolve()
        path_text = str(path)
        if path_text in observed_paths:
            raise ValueError("source verifier read-file receipt contains duplicates")
        observed_paths.add(path_text)
        if not any(
            supervisor.runtime_filter_allows(path, item) for item in effective_filters
        ):
            raise ValueError(f"source verifier read escaped allowed roots: {path}")
        if not path.is_file() or row.get("sha256") != sha256_file(path):
            raise ValueError(f"source verifier read-file digest changed: {path}")


def publication_path(path: Path) -> Path:
    if not path.name or path.name in {".", ".."}:
        raise ValueError("source publication path has no regular-file basename")
    return path.parent.resolve(strict=True) / path.name


def read_published_payload(path: Path, expected: bytes) -> dict[str, int]:
    nofollow = getattr(os, "O_NOFOLLOW", None)
    if nofollow is None:
        raise RuntimeError("source publication requires O_NOFOLLOW")
    descriptor = os.open(path, os.O_RDONLY | os.O_CLOEXEC | int(nofollow))
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_size != len(expected):
            raise RuntimeError("source publication is not the expected regular file")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        if b"".join(chunks) != expected:
            raise RuntimeError("source publication bytes changed after atomic replace")
        return {
            "device": metadata.st_dev,
            "inode": metadata.st_ino,
            "size": metadata.st_size,
        }
    finally:
        os.close(descriptor)


def atomic_publish_payload(path: Path, payload: bytes) -> dict[str, int]:
    destination = publication_path(path)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.",
        dir=destination.parent,
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb", closefd=True) as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, destination)
        return read_published_payload(destination, payload)
    finally:
        if temporary.exists():
            temporary.unlink()


def publish_output_and_receipt(
    output_path: Path,
    output_payload: bytes,
    receipt_path: Path,
    receipt: dict[str, Any],
) -> tuple[Path, Path]:
    output = publication_path(output_path)
    receipt_output = publication_path(receipt_path)
    if output == receipt_output:
        raise ValueError("source output and receipt paths must be distinct")

    output_identity = atomic_publish_payload(output, output_payload)
    receipt["publication"] = {
        "output_identity": output_identity,
        "policy": (
            "output_then_receipt_individual_atomic_replace; "
            "nofollow_regular_file_reopen; final_inode_distinctness"
        ),
    }
    receipt_payload = canonical_bytes(receipt)
    receipt_identity = atomic_publish_payload(receipt_output, receipt_payload)
    final_output_identity = read_published_payload(output, output_payload)
    final_receipt_identity = read_published_payload(receipt_output, receipt_payload)
    if output_identity != final_output_identity or receipt_identity != final_receipt_identity:
        raise RuntimeError("source publication identity changed during final verification")
    if (
        final_output_identity["device"],
        final_output_identity["inode"],
    ) == (
        final_receipt_identity["device"],
        final_receipt_identity["inode"],
    ):
        raise RuntimeError("source output and receipt alias one inode")
    return output, receipt_output


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument(
        "--role",
        choices=tuple(ROLE_SOURCE_FILES),
        default="producer",
    )
    parser.add_argument("--experiment-dir", required=True, type=Path)
    parser.add_argument("--closure-audit", required=True, type=Path)
    parser.add_argument("--staging-parent", required=True, type=Path)
    parser.add_argument("--raw-result", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--receipt-output", required=True, type=Path)
    return parser.parse_args(argv)


def run(args: argparse.Namespace) -> dict[str, Any]:
    role = args.role
    if (role == "verifier") != (args.raw_result is not None):
        raise ValueError("--raw-result is required only for the verifier role")
    experiment_dir = args.experiment_dir.resolve()
    source_dir = experiment_dir / "src"
    if args.closure_audit.name != "source-static-closure-audit.json":
        raise ValueError("static closure audit basename is not frozen")
    audit_bytes = supervisor.read_stable_bytes(
        args.closure_audit.resolve(),
        "source static closure audit",
        MAX_INPUT_BYTES,
    )
    audit = json.loads(audit_bytes)
    if not isinstance(audit, dict) or audit_bytes != canonical_bytes(audit):
        raise ValueError("source static closure audit is not canonical JSON")
    policy_payloads = retain_policy_payloads(experiment_dir)
    validate_static_closure_audit(
        audit,
        audit_bytes,
        source_dir,
        experiment_dir,
        policy_payloads,
    )
    role_payloads = approved_source_payloads(audit, source_dir, role)
    static_audit_sha256 = sha256_bytes(audit_bytes)

    matrix_bytes = policy_payloads["source-execution-matrix-v2.json"]
    matrix_record = json.loads(matrix_bytes)
    if not isinstance(matrix_record, dict):
        raise ValueError("source execution matrix must be a JSON object")
    matrix = matrix_record.get("source_execution_matrix")
    if not isinstance(matrix, dict):
        raise ValueError("source execution matrix wrapper is malformed")
    backend = matrix.get("backend_gate")
    gates = matrix.get("resource_gates")
    if not isinstance(backend, dict) or not isinstance(gates, dict):
        raise ValueError("source execution matrix backend or resource gates are missing")
    python_path = Path(str(backend.get("python_executable")))
    if sha256_file(python_path) != backend.get("python_executable_sha256"):
        raise ValueError("pinned Python executable digest changed")
    runtime_backend = dict(backend)
    runtime_backend["python_version"] = str(backend["python_version"]).split()[0]
    runtime_boundary = supervisor.build_runtime_boundary(python_path, runtime_backend)
    manifest_payload = policy_payloads["source-instance-manifest-v1.json"]
    raw_result_payload = (
        supervisor.read_stable_bytes(
            args.raw_result.resolve(),
            "source producer raw result",
            MAX_RAW_BYTES,
        )
        if role == "verifier"
        else None
    )

    args.staging_parent.mkdir(parents=True, exist_ok=True)
    stage_root = Path(
        tempfile.mkdtemp(
            prefix=(
                "tt-source-partition-"
                if role == "producer"
                else "tt-source-verifier-"
            ),
            dir=args.staging_parent.resolve(),
        )
    )
    approved_stage_rows: list[dict[str, Any]] = []
    for name, payload in sorted(role_payloads.items()):
        approved_stage_rows.append(
            supervisor.stage_retained_payload(
                stage_root / name,
                payload,
                MAX_INPUT_BYTES,
            )
        )
    approved_stage_rows.append(
        supervisor.stage_retained_payload(
            stage_root / "source-execution-matrix-v2.json",
            matrix_bytes,
            MAX_INPUT_BYTES,
        )
    )
    approved_stage_rows.append(
        supervisor.stage_retained_payload(
            stage_root / "source-instance-manifest-v1.json",
            manifest_payload,
            MAX_INPUT_BYTES,
        )
    )
    if role == "verifier":
        if raw_result_payload is None:
            raise RuntimeError("source verifier raw result was not retained")
        approved_stage_rows.append(
            supervisor.stage_retained_payload(
                stage_root / "source-generator-raw-result.json",
                raw_result_payload,
                MAX_RAW_BYTES,
            )
        )
    remove_appledouble_files(stage_root)
    stage_rows = collect_stage_rows(stage_root, role)
    validate_approved_stage_manifest(approved_stage_rows, stage_rows)
    stage_identity_rows = collect_stage_identity_rows(stage_root, role)
    expected_stage_sha256 = stage_digest(stage_rows)
    profile = supervisor.sandbox_profile(stage_root, stage_rows, runtime_boundary)
    profile_sha256 = sha256_bytes(profile.encode("utf-8"))

    command_prefix = [
        "/usr/bin/sandbox-exec",
        "-p",
        profile,
        str(python_path),
        "-I",
        "-B",
    ]
    command = command_prefix + (
        [
            str(stage_root / "run_tt_source_partition.py"),
            "--manifest",
            str(stage_root / "source-instance-manifest-v1.json"),
            "--execution-matrix",
            str(stage_root / "source-execution-matrix-v2.json"),
            "--expected-stage-sha256",
            expected_stage_sha256,
            "--static-audit-sha256",
            static_audit_sha256,
        ]
        if role == "producer"
        else [
            str(stage_root / "run_tt_source_verifier_partition.py"),
            "--manifest",
            str(stage_root / "source-instance-manifest-v1.json"),
            "--execution-matrix",
            str(stage_root / "source-execution-matrix-v2.json"),
            "--raw-result",
            str(stage_root / "source-generator-raw-result.json"),
            "--expected-static-closure-audit-sha256",
            static_audit_sha256,
            "--strict-preflight-development",
            "--expected-stage-sha256",
            expected_stage_sha256,
            "--static-audit-sha256",
            static_audit_sha256,
        ]
    )
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
            raise RuntimeError("source stage changed before supervised execution")
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
                timeout=int(gates["wall_clock_seconds"])
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
            raise RuntimeError("source staging parent had prior child resource usage")
        child_usage = supervisor.rusage_record(after_usage)
        post_stage_rows = collect_stage_rows(stage_root, role)
        post_stage_identity_rows = collect_stage_identity_rows(stage_root, role)
        monitor.validate_bindings(post_stage_identity_rows)
        if (
            post_stage_rows != stage_rows
            or post_stage_identity_rows != stage_identity_rows
            or stage_digest(post_stage_rows) != expected_stage_sha256
        ):
            raise RuntimeError("source stage changed while the child was running")
        post_runtime_boundary = supervisor.build_runtime_boundary(
            python_path,
            runtime_backend,
        )
        if post_runtime_boundary != runtime_boundary:
            raise RuntimeError("source parent-pinned runtime changed during the child run")
        stage_mutation_events = monitor.poll()
    finally:
        monitor.close()
    reject_stage_mutations(stage_mutation_events)

    child_runtime_receipt: dict[str, Any] | None = None
    auxiliary_stderr = stderr
    if role == "verifier":
        child_runtime_receipt, auxiliary_stderr = parse_source_verifier_receipt(
            stderr
        )
    if process.returncode != 0 or timed_out or auxiliary_stderr:
        raise RuntimeError("source staged child or diagnostic stream is invalid")
    if len(stdout) > int(gates["raw_result_bytes"]):
        raise ValueError("source staged child output exceeds raw-result gate")
    if wall_clock_ns > int(gates["wall_clock_seconds"]) * 1_000_000_000:
        raise ValueError("source staged child exceeds wall-clock gate")
    if child_usage["maximum_rss_bytes"] > int(gates["peak_rss_bytes"]):
        raise ValueError("source staged child exceeds RSS gate")
    result = json.loads(stdout)
    if not isinstance(result, dict) or stdout != canonical_bytes(result):
        raise ValueError("source child stdout is not one canonical JSON object")
    if role == "producer":
        validate_producer_child_result(
            result,
            backend_gate=backend,
            matrix_sha256=sha256_bytes(matrix_bytes),
            runtime_boundary=runtime_boundary,
            stage_rows=stage_rows,
            stage_sha256=expected_stage_sha256,
            static_audit_sha256=static_audit_sha256,
            stage_root=stage_root,
        )
    else:
        if child_runtime_receipt is None or raw_result_payload is None:
            raise RuntimeError("source verifier supervision record is incomplete")
        validate_verifier_child_result(
            result,
            child_runtime_receipt,
            raw_result_sha256=sha256_bytes(raw_result_payload),
            runtime_boundary=runtime_boundary,
            stage_rows=stage_rows,
            stage_sha256=expected_stage_sha256,
            static_audit_sha256=static_audit_sha256,
            stage_root=stage_root,
            stdout=stdout,
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.receipt_output.parent.mkdir(parents=True, exist_ok=True)
    output_path = publication_path(args.output)
    receipt_path = publication_path(args.receipt_output)
    if output_path == receipt_path:
        raise ValueError("source output and receipt paths must be distinct")
    receipt = {
        "artifact_freeze_authorized": False,
        "boundary": (
            f"Development-only supervised source {role} partition receipt. Direct child time, "
            "rusage, streams, pre/post stage hashes, stage vnode events, and pre/post "
            "runtime snapshots are parent-observed. File-data reads are OS-limited to "
            "literal staged paths and parent-snapshotted runtime roots; child read "
            "enumeration is diagnostic only. Concurrent runtime namespace mutation "
            "and OS shared-cache identity remain outside this model. No source advice "
            "is frozen and no campaign or cryptanalytic claim is authorized."
        ),
        "child": {
            "command": command,
            "runtime_receipt": child_runtime_receipt,
            "returncode": process.returncode,
            "rusage": child_usage,
            "stderr_bytes": len(stderr),
            "stdout_bytes": len(stdout),
            "stdout_sha256": sha256_bytes(stdout),
            "timed_out": timed_out,
            "wall_clock_ns": wall_clock_ns,
        },
        "output": {
            "bytes": len(stdout),
            "path": str(output_path),
            "sha256": sha256_bytes(stdout),
        },
        "protocol": PROTOCOL,
        "role": role,
        "schema": "tt-source-parent-runtime-receipt-development-v1",
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
            "static_harness_closure_sha256": audit["harness"]["closure_sha256"],
        },
        "runtime_boundary": {
            "closure_sha256": runtime_boundary["closure_sha256"],
            "post_run_closure_sha256": post_runtime_boundary["closure_sha256"],
            "record": runtime_boundary,
        },
        "valid": True,
    }
    published_output, published_receipt = publish_output_and_receipt(
        output_path,
        stdout,
        receipt_path,
        receipt,
    )
    if published_output != output_path or published_receipt != receipt_path:
        raise RuntimeError("source publication paths changed during atomic output")
    return receipt


def main(argv: Sequence[str] | None = None) -> int:
    try:
        args = parse_args(argv)
        receipt = run(args)
    except Exception as error:
        failure = {
            "artifact_freeze_authorized": False,
            "error": {"message": str(error), "type": type(error).__name__},
            "schema": "tt-source-parent-runtime-receipt-development-failure-v1",
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
                "schema": "tt-source-parent-runtime-summary-development-v1",
                "stage_sha256": receipt["stage"]["sha256"],
                "valid": True,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
