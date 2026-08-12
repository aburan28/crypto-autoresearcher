#!/usr/bin/env python3
"""Pack and verify development-only TT supervision artifacts."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import resource
import shutil
import stat
import sys
import tempfile
import time
import zlib
from pathlib import Path
from typing import Any, Mapping, Sequence


PROTOCOL = "EXP-ECDLP-TT-SOURCE-COMPILER-001"
MANIFEST_SCHEMA = "tt-supervised-artifact-envelope-manifest-v1"
PARENT_RECEIPT_SCHEMA = "tt-source-parent-runtime-receipt-development-v1"
CHILD_SCHEMAS = {
    "producer": (
        "tt-source-compiler-raw-v1",
        "source_generator",
    ),
    "verifier": (
        "tt-source-strict-preflight-development-verification-v1",
        "source_verifier_strict_preflight_development",
    ),
}
ARTIFACT_NAMES = (
    "child-result.json.gz",
    "envelope-manifest.json",
    "parent-receipt.json",
)
APPLEDOUBLE_NAMES = tuple(f"._{name}" for name in ARTIFACT_NAMES)
AUTHORIZATION_FIELDS = (
    "artifact_freeze_authorized",
    "campaign_execution_authorized",
    "generic_runner_supervision_claim",
)
MAX_CHILD_BYTES = 256 * 1024 * 1024
MAX_COMPRESSED_BYTES = 256 * 1024 * 1024
MAX_RECEIPT_BYTES = 4 * 1024 * 1024
MAX_MANIFEST_BYTES = 1024 * 1024


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


def validate_digest(value: Any, label: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(character not in "0123456789abcdef" for character in value)
    ):
        raise ValueError(f"{label} is not a lowercase SHA-256 digest")
    return value


def _reject_constant(value: str) -> None:
    raise ValueError(f"JSON constant is forbidden: {value}")


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def strict_object(payload: bytes, label: str) -> dict[str, Any]:
    try:
        text = payload.decode("utf-8")
        value = json.loads(
            text,
            object_pairs_hook=_unique_object,
            parse_constant=_reject_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError(f"{label} is not strict UTF-8 JSON") from error
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    return value


def require_canonical(value: Mapping[str, Any], payload: bytes, label: str) -> None:
    encoder = json.JSONEncoder(
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )
    offset = 0
    for text in encoder.iterencode(value):
        chunk = text.encode("utf-8")
        if payload[offset : offset + len(chunk)] != chunk:
            raise ValueError(f"{label} is not canonical JSON")
        offset += len(chunk)
    if payload[offset:] != b"\n":
        raise ValueError(f"{label} does not have exactly one trailing newline")


def read_regular(path: Path, label: str, maximum_bytes: int) -> tuple[bytes, dict[str, int]]:
    nofollow = getattr(os, "O_NOFOLLOW", None)
    if nofollow is None:
        raise RuntimeError("supervised artifact verification requires O_NOFOLLOW")
    descriptor = os.open(path, os.O_RDONLY | os.O_CLOEXEC | int(nofollow))
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode) or before.st_size > maximum_bytes:
            raise ValueError(f"{label} is not a bounded regular file")
        chunks: list[bytes] = []
        remaining = before.st_size
        while remaining:
            chunk = os.read(descriptor, min(1024 * 1024, remaining))
            if not chunk:
                raise ValueError(f"{label} ended before its declared file size")
            chunks.append(chunk)
            remaining -= len(chunk)
        if os.read(descriptor, 1):
            raise ValueError(f"{label} grew while it was read")
        after = os.fstat(descriptor)
        if (
            before.st_dev != after.st_dev
            or before.st_ino != after.st_ino
            or before.st_size != after.st_size
        ):
            raise ValueError(f"{label} changed while it was read")
        return b"".join(chunks), {
            "device": before.st_dev,
            "inode": before.st_ino,
            "size": before.st_size,
        }
    finally:
        os.close(descriptor)


def inspect_regular(path: Path, label: str, maximum_bytes: int) -> dict[str, int]:
    nofollow = getattr(os, "O_NOFOLLOW", None)
    if nofollow is None:
        raise RuntimeError("supervised artifact verification requires O_NOFOLLOW")
    descriptor = os.open(path, os.O_RDONLY | os.O_CLOEXEC | int(nofollow))
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_size > maximum_bytes:
            raise ValueError(f"{label} is not a bounded regular file")
        return {
            "device": metadata.st_dev,
            "inode": metadata.st_ino,
            "size": metadata.st_size,
        }
    finally:
        os.close(descriptor)


def write_regular(path: Path, payload: bytes) -> dict[str, int]:
    descriptor = os.open(
        path,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC,
        0o600,
    )
    try:
        view = memoryview(payload)
        while view:
            written = os.write(descriptor, view)
            if written <= 0:
                raise OSError("artifact write made no progress")
            view = view[written:]
        os.fsync(descriptor)
        metadata = os.fstat(descriptor)
        return {
            "device": metadata.st_dev,
            "inode": metadata.st_ino,
            "size": metadata.st_size,
        }
    finally:
        os.close(descriptor)


def sync_directory(path: Path) -> None:
    nofollow = getattr(os, "O_NOFOLLOW", None)
    directory = getattr(os, "O_DIRECTORY", None)
    if nofollow is None or directory is None:
        raise RuntimeError("supervised artifact publication requires direct directory opens")
    descriptor = os.open(
        path,
        os.O_RDONLY | os.O_CLOEXEC | int(nofollow) | int(directory),
    )
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISDIR(metadata.st_mode):
            raise ValueError("supervised artifact publication root changed type")
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def finalize_private_publication_directory(root: Path) -> dict[str, int]:
    """Remove only exFAT AppleDouble metadata from a fresh private directory."""
    expected = set(ARTIFACT_NAMES)
    sidecars = set(APPLEDOUBLE_NAMES)
    observed = {path.name for path in root.iterdir()}
    if not expected.issubset(observed) or observed - expected - sidecars:
        raise RuntimeError("private supervised artifact staging set changed")
    metadata = {name: os.lstat(root / name) for name in observed}
    root_metadata = os.lstat(root)
    peak_logical_bytes = root_metadata.st_size + sum(
        item.st_size for item in metadata.values()
    )
    peak_allocated_bytes = root_metadata.st_blocks * 512 + sum(
        item.st_blocks * 512 for item in metadata.values()
    )
    sidecar_logical_bytes = 0
    sidecar_allocated_bytes = 0
    for name in sorted(observed & sidecars):
        path = root / name
        item = metadata[name]
        if not stat.S_ISREG(item.st_mode) or item.st_nlink != 1:
            raise RuntimeError("private AppleDouble staging path changed type")
        sidecar_logical_bytes += item.st_size
        sidecar_allocated_bytes += item.st_blocks * 512
        os.unlink(path)
    if {path.name for path in root.iterdir()} != expected:
        raise RuntimeError("private supervised artifact staging cleanup was incomplete")
    sync_directory(root)
    return {
        "appledouble_removed_allocated_bytes": sidecar_allocated_bytes,
        "appledouble_removed_count": len(observed & sidecars),
        "appledouble_removed_logical_bytes": sidecar_logical_bytes,
        "temporary_peak_observed_allocated_bytes": peak_allocated_bytes,
        "temporary_peak_observed_logical_bytes": peak_logical_bytes,
    }


def deterministic_gzip(payload: bytes) -> bytes:
    return gzip.compress(payload, compresslevel=9, mtime=0)


def bounded_gzip_decompress(payload: bytes, maximum_bytes: int) -> bytes:
    decoder = zlib.decompressobj(wbits=31)
    result = decoder.decompress(payload, maximum_bytes + 1)
    if len(result) > maximum_bytes or decoder.unconsumed_tail:
        raise ValueError("gzip child result exceeds its uncompressed byte gate")
    result += decoder.flush(maximum_bytes + 1 - len(result))
    if len(result) > maximum_bytes:
        raise ValueError("gzip child result exceeds its uncompressed byte gate")
    if not decoder.eof:
        raise ValueError("gzip child result is truncated")
    if decoder.unused_data:
        raise ValueError("gzip child result has a trailing member or trailing bytes")
    return result


def reject_authorization_claims(value: Mapping[str, Any], label: str) -> None:
    pending: list[Any] = [value]
    while pending:
        current = pending.pop()
        if isinstance(current, dict):
            for key, nested in current.items():
                if key in AUTHORIZATION_FIELDS and nested is not False:
                    raise ValueError(
                        f"{label} asserts forbidden authority through {key}"
                    )
                if isinstance(nested, (dict, list)):
                    pending.append(nested)
        elif isinstance(current, list):
            pending.extend(
                nested for nested in current if isinstance(nested, (dict, list))
            )


def validate_child(
    child: Mapping[str, Any],
    child_bytes: bytes,
    role: str,
) -> None:
    if role not in CHILD_SCHEMAS:
        raise ValueError(f"unsupported supervised artifact role: {role!r}")
    expected_schema, expected_partition = CHILD_SCHEMAS[role]
    if (
        child.get("schema") != expected_schema
        or child.get("partition") != expected_partition
        or child.get("protocol") != PROTOCOL
        or child.get("valid") is not True
    ):
        raise ValueError("supervised child result boundary changed")
    reject_authorization_claims(child, "supervised child result")
    if role == "producer":
        claim = child.get("claim_boundary")
        expected_claim = {
            "breakthrough_claim": False,
            "ecdlp_improvement_claim": False,
            "index_calculus_claim": False,
            "locator_claim": False,
            "target_specialization_claim": False,
            "toy_restricted_model_bound": True,
        }
        if claim != expected_claim:
            raise ValueError("supervised producer claim boundary changed")
    elif child.get("artifact_freeze_authorized") is not False:
        raise ValueError("supervised verifier unexpectedly authorizes artifact freeze")
    require_canonical(child, child_bytes, "supervised child result")


def validate_parent_receipt(
    receipt: Mapping[str, Any],
    receipt_bytes: bytes,
    child_bytes: bytes,
    role: str,
) -> str:
    if (
        receipt.get("schema") != PARENT_RECEIPT_SCHEMA
        or receipt.get("protocol") != PROTOCOL
        or receipt.get("role") != role
        or receipt.get("valid") is not True
        or receipt.get("artifact_freeze_authorized") is not False
    ):
        raise ValueError("source parent supervision receipt boundary changed")
    reject_authorization_claims(receipt, "source parent supervision receipt")
    require_canonical(receipt, receipt_bytes, "source parent supervision receipt")
    child_digest = sha256_bytes(child_bytes)
    output = receipt.get("output")
    child = receipt.get("child")
    stage = receipt.get("stage")
    if (
        not isinstance(output, dict)
        or output.get("bytes") != len(child_bytes)
        or output.get("sha256") != child_digest
        or not isinstance(child, dict)
        or child.get("stdout_bytes") != len(child_bytes)
        or child.get("stdout_sha256") != child_digest
        or child.get("returncode") != 0
        or child.get("timed_out") is not False
        or not isinstance(stage, dict)
    ):
        raise ValueError("parent receipt does not bind the exact child result")
    return validate_digest(
        stage.get("static_audit_sha256"),
        "parent receipt static audit SHA-256",
    )


def manifest_record(
    *,
    child: Mapping[str, Any],
    child_bytes: bytes,
    compressed: bytes,
    receipt: Mapping[str, Any],
    receipt_bytes: bytes,
    role: str,
    static_audit_sha256: str,
) -> dict[str, Any]:
    return {
        "artifact_freeze_authorized": False,
        "boundary": (
            "Development-only deterministic package of one supervised child result "
            "and parent receipt. It is not an execution approval or frozen artifact."
        ),
        "child_result": {
            "compressed_bytes": len(compressed),
            "compressed_sha256": sha256_bytes(compressed),
            "path": "child-result.json.gz",
            "schema": child["schema"],
            "uncompressed_bytes": len(child_bytes),
            "uncompressed_sha256": sha256_bytes(child_bytes),
        },
        "compression": {
            "format": "gzip-rfc1952",
            "level": 9,
            "mtime": 0,
            "single_member": True,
        },
        "parent_receipt": {
            "bytes": len(receipt_bytes),
            "path": "parent-receipt.json",
            "schema": receipt["schema"],
            "sha256": sha256_bytes(receipt_bytes),
        },
        "protocol": PROTOCOL,
        "role": role,
        "schema": MANIFEST_SCHEMA,
        "static_closure_audit_sha256": static_audit_sha256,
        "trust_model": {
            "campaign_execution_authorized": False,
            "generic_runner_supervision_claim": False,
            "host": "trusted-local-host-without-concurrent-mutation",
            "malicious_host_excluded": True,
            "parent": "reviewed-trusted-source-staging-parent",
        },
        "valid": True,
    }


def validate_artifact_file_set(root: Path) -> dict[str, dict[str, int]]:
    if not root.is_dir() or root.is_symlink():
        raise ValueError("supervised artifact root is not a direct directory")
    observed = tuple(sorted(path.name for path in root.iterdir()))
    if observed != ARTIFACT_NAMES:
        raise ValueError("supervised artifact file set changed")
    identities: dict[str, dict[str, int]] = {}
    maximum = {
        "child-result.json.gz": MAX_COMPRESSED_BYTES,
        "envelope-manifest.json": MAX_MANIFEST_BYTES,
        "parent-receipt.json": MAX_RECEIPT_BYTES,
    }
    for name in ARTIFACT_NAMES:
        identities[name] = inspect_regular(root / name, name, maximum[name])
    inode_keys = {
        (identity["device"], identity["inode"])
        for identity in identities.values()
    }
    if len(inode_keys) != len(ARTIFACT_NAMES):
        raise ValueError("supervised artifact files alias one inode")
    return identities


def verify_artifact(root: Path) -> tuple[dict[str, Any], bytes]:
    validate_artifact_file_set(root)
    manifest_bytes, _ = read_regular(
        root / "envelope-manifest.json",
        "envelope manifest",
        MAX_MANIFEST_BYTES,
    )
    receipt_bytes, _ = read_regular(
        root / "parent-receipt.json",
        "parent receipt",
        MAX_RECEIPT_BYTES,
    )
    compressed, _ = read_regular(
        root / "child-result.json.gz",
        "compressed child result",
        MAX_COMPRESSED_BYTES,
    )
    manifest = strict_object(manifest_bytes, "envelope manifest")
    receipt = strict_object(receipt_bytes, "parent receipt")
    require_canonical(manifest, manifest_bytes, "envelope manifest")
    child_bytes = bounded_gzip_decompress(compressed, MAX_CHILD_BYTES)
    if compressed != deterministic_gzip(child_bytes):
        raise ValueError("child result is not the deterministic canonical gzip stream")
    child = strict_object(child_bytes, "supervised child result")
    role = manifest.get("role")
    if not isinstance(role, str):
        raise ValueError("envelope manifest role is missing")
    validate_child(child, child_bytes, role)
    static_audit_sha256 = validate_parent_receipt(
        receipt,
        receipt_bytes,
        child_bytes,
        role,
    )
    expected = manifest_record(
        child=child,
        child_bytes=child_bytes,
        compressed=compressed,
        receipt=receipt,
        receipt_bytes=receipt_bytes,
        role=role,
        static_audit_sha256=static_audit_sha256,
    )
    if manifest != expected:
        raise ValueError("envelope manifest does not match the packaged authorities")
    return manifest, child_bytes


def max_rss_bytes() -> int:
    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value if sys.platform == "darwin" else value * 1024


def pack_artifact(
    child_path: Path,
    receipt_path: Path,
    output_dir: Path,
) -> dict[str, Any]:
    started_wall = time.perf_counter_ns()
    started_cpu = time.process_time_ns()
    child_bytes, _ = read_regular(child_path, "supervised child result", MAX_CHILD_BYTES)
    receipt_bytes, _ = read_regular(
        receipt_path,
        "source parent supervision receipt",
        MAX_RECEIPT_BYTES,
    )
    child = strict_object(child_bytes, "supervised child result")
    receipt = strict_object(receipt_bytes, "source parent supervision receipt")
    role = receipt.get("role")
    if not isinstance(role, str):
        raise ValueError("source parent receipt role is missing")
    validate_child(child, child_bytes, role)
    static_audit_sha256 = validate_parent_receipt(
        receipt,
        receipt_bytes,
        child_bytes,
        role,
    )
    compressed = deterministic_gzip(child_bytes)
    manifest = manifest_record(
        child=child,
        child_bytes=child_bytes,
        compressed=compressed,
        receipt=receipt,
        receipt_bytes=receipt_bytes,
        role=role,
        static_audit_sha256=static_audit_sha256,
    )
    manifest_bytes = canonical_bytes(manifest)

    destination = output_dir.parent.resolve(strict=True) / output_dir.name
    if destination.exists() or destination.is_symlink():
        raise ValueError("supervised artifact destination already exists")
    temporary = Path(
        tempfile.mkdtemp(
            prefix=f".{destination.name}.",
            dir=destination.parent,
        )
    )
    published = False
    try:
        identities = {
            "child-result.json.gz": write_regular(
                temporary / "child-result.json.gz", compressed
            ),
            "envelope-manifest.json": write_regular(
                temporary / "envelope-manifest.json", manifest_bytes
            ),
            "parent-receipt.json": write_regular(
                temporary / "parent-receipt.json", receipt_bytes
            ),
        }
        if len(
            {
                (identity["device"], identity["inode"])
                for identity in identities.values()
            }
        ) != len(ARTIFACT_NAMES):
            raise RuntimeError("new supervised artifact files alias one inode")
        publication = finalize_private_publication_directory(temporary)
        os.replace(temporary, destination)
        published = True
        sync_directory(destination.parent)
        verified_manifest, verified_child = verify_artifact(destination)
        if verified_manifest != manifest or verified_child != child_bytes:
            raise RuntimeError("published supervised artifact failed exact verification")
    except Exception as error:
        if published:
            try:
                if destination.is_symlink() or not destination.is_dir():
                    raise RuntimeError("published artifact changed type before cleanup")
                shutil.rmtree(destination)
                sync_directory(destination.parent)
            except Exception as cleanup_error:
                raise RuntimeError(
                    "published supervised artifact failed and cleanup was incomplete"
                ) from cleanup_error
        raise
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)
    wall_ns = time.perf_counter_ns() - started_wall
    cpu_ns = time.process_time_ns() - started_cpu
    written_bytes = len(compressed) + len(receipt_bytes) + len(manifest_bytes)
    return {
        "artifact_freeze_authorized": False,
        "artifact_root": str(destination),
        "child_result_sha256": sha256_bytes(child_bytes),
        "compressed_bytes": len(compressed),
        "compression_ratio": len(compressed) / len(child_bytes),
        "cpu_ns": cpu_ns,
        "input_bytes": len(child_bytes) + len(receipt_bytes),
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "peak_rss_bytes": max_rss_bytes(),
        "publication": {
            **publication,
            "atomic_directory_rename_count": 1,
            "caught_failure_cleanup": "remove-private-or-published-temporary-directory",
            "directory_fsync_count": 2,
            "file_fsync_count": len(ARTIFACT_NAMES),
            "power_loss_crash_residue_measured": False,
            "temporary_path_present_after_success": temporary.exists(),
        },
        "read_bytes": len(child_bytes) + len(receipt_bytes) + written_bytes,
        "role": role,
        "schema": "tt-supervised-artifact-pack-development-report-v1",
        "valid": True,
        "wall_clock_ns": wall_ns,
        "written_bytes": written_bytes,
    }


def atomic_extract(path: Path, payload: bytes) -> None:
    destination = path.parent.resolve(strict=True) / path.name
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
    finally:
        if temporary.exists():
            temporary.unlink()


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    subparsers = parser.add_subparsers(dest="command", required=True)
    pack = subparsers.add_parser("pack")
    pack.add_argument("--child-result", required=True, type=Path)
    pack.add_argument("--parent-receipt", required=True, type=Path)
    pack.add_argument("--output-dir", required=True, type=Path)
    verify = subparsers.add_parser("verify")
    verify.add_argument("--artifact-dir", required=True, type=Path)
    verify.add_argument("--extract-child", type=Path)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    try:
        args = parse_args(argv)
        if args.command == "pack":
            report = pack_artifact(
                args.child_result,
                args.parent_receipt,
                args.output_dir,
            )
        else:
            started_wall = time.perf_counter_ns()
            started_cpu = time.process_time_ns()
            manifest, child_bytes = verify_artifact(args.artifact_dir)
            if args.extract_child is not None:
                args.extract_child.parent.mkdir(parents=True, exist_ok=True)
                atomic_extract(args.extract_child, child_bytes)
            report = {
                "artifact_freeze_authorized": False,
                "artifact_root": str(args.artifact_dir.absolute()),
                "child_result_bytes": len(child_bytes),
                "child_result_sha256": manifest["child_result"][
                    "uncompressed_sha256"
                ],
                "compressed_bytes": manifest["child_result"]["compressed_bytes"],
                "compression_ratio": (
                    manifest["child_result"]["compressed_bytes"] / len(child_bytes)
                ),
                "cpu_ns": time.process_time_ns() - started_cpu,
                "peak_rss_bytes": max_rss_bytes(),
                "read_bytes": (
                    manifest["child_result"]["compressed_bytes"]
                    + manifest["parent_receipt"]["bytes"]
                    + len(canonical_bytes(manifest))
                ),
                "role": manifest["role"],
                "schema": "tt-supervised-artifact-verify-development-report-v1",
                "valid": True,
                "wall_clock_ns": time.perf_counter_ns() - started_wall,
                "written_bytes": len(child_bytes) if args.extract_child is not None else 0,
            }
    except Exception as error:
        report = {
            "artifact_freeze_authorized": False,
            "error": {"message": str(error), "type": type(error).__name__},
            "schema": "tt-supervised-artifact-operation-failure-v1",
            "valid": False,
        }
        sys.stdout.buffer.write(canonical_bytes(report))
        return 1
    sys.stdout.buffer.write(canonical_bytes(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
