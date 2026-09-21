#!/usr/bin/env python3
"""Shared durable payload and operational-companion finalizer.

Production and fixed tests call :func:`finalize_run` directly.  There is no
test-only publication path.  The payload timing boundary closes after the
canonical payload rename and parent-directory fsync; the operational receipt
is then written in a separate stable namespace and explicitly excludes its own
write/fsync duration.
"""
from __future__ import annotations

import os
import shutil
import tempfile
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from streaming import (
    GuardedDigestWriter,
    hash_file,
    write_json_document,
)


class CustodyError(RuntimeError):
    """Durable payload or operational-companion custody failed."""


ArtifactProducer = Callable[[GuardedDigestWriter], None]


@dataclass
class FinalizationResult:
    payload_path: Path
    operational_receipt_path: Path
    payload_artifact_sha256: dict[str, str]
    timing_through_durable_payload: dict[str, Any]
    cleanup_errors: list[str] = field(default_factory=list)


def fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _typed_error_record(error: BaseException | None) -> dict[str, Any] | None:
    if error is None:
        return None
    return {
        "type": type(error).__name__,
        "message": str(error),
    }


def _attach_secondary(primary: BaseException, secondary: BaseException, phase: str) -> None:
    record = {"phase": phase, "type": type(secondary).__name__, "message": str(secondary)}
    failures = getattr(primary, "secondary_custody_failures", None)
    if failures is None:
        failures = []
        setattr(primary, "secondary_custody_failures", failures)
    failures.append(record)
    add_note = getattr(primary, "add_note", None)
    if callable(add_note):
        add_note(
            f"secondary custody failure at {phase}: {type(secondary).__name__}: {secondary}"
        )


def _write_small_json_durable(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        writer = GuardedDigestWriter(handle, purpose="operational_companion_write")
        write_json_document(writer, value)
        handle.flush()
        os.fsync(handle.fileno())
    fsync_directory(path.parent)


def _quarantine(
    runs: Path,
    candidate: Path,
    *,
    run_id: str,
    phase: str,
    error: BaseException,
) -> Path | None:
    if not candidate.exists():
        return None
    incomplete = runs / "incomplete"
    incomplete.mkdir(parents=True, exist_ok=True)
    retained = incomplete / f"{run_id}-{uuid.uuid4().hex[:12]}"
    marker = candidate / "publication-failure.json"
    try:
        _write_small_json_durable(
            marker,
            {
                "classification": "infrastructure_error",
                "run_id": run_id,
                "phase": phase,
                "error": _typed_error_record(error),
                "publication_state": "incomplete_quarantine_pending",
            },
        )
    except Exception:
        # The move is still attempted; callers retain both failures.
        pass
    os.rename(candidate, retained)
    fsync_directory(incomplete)
    fsync_directory(runs)
    return retained


def _write_payload(
    *,
    staging: Path,
    artifact_order: Sequence[str],
    producers: Mapping[str, ArtifactProducer],
    integrity_name: str,
    check: Callable[[], None] | None,
    on_progress: Callable[[dict[str, Any]], None] | None,
    phase_hook: Callable[[str, str | None], None] | None,
) -> dict[str, str]:
    expected_producers = set(artifact_order) - {integrity_name}
    if set(producers) != expected_producers:
        missing = sorted(expected_producers - set(producers))
        extra = sorted(set(producers) - expected_producers)
        raise CustodyError(f"artifact producer inventory mismatch; missing={missing}; extra={extra}")
    hashes: dict[str, str] = {}
    for name in artifact_order:
        if name == integrity_name:
            continue
        if phase_hook is not None:
            phase_hook("before_artifact", name)
        target = staging / name
        with target.open("xb") as handle:
            writer = GuardedDigestWriter(
                handle,
                check=check,
                on_progress=on_progress,
                purpose=f"artifact:{name}",
            )
            producers[name](writer)
            handle.flush()
            os.fsync(handle.fileno())
            hashes[name] = writer.hexdigest()
        if phase_hook is not None:
            phase_hook("after_artifact", name)
    integrity_path = staging / integrity_name
    with integrity_path.open("xb") as handle:
        writer = GuardedDigestWriter(
            handle,
            check=check,
            on_progress=on_progress,
            purpose=f"artifact:{integrity_name}",
        )
        write_json_document(writer, {"artifact_sha256": hashes})
        handle.flush()
        os.fsync(handle.fileno())
    expected = set(artifact_order)
    actual = {path.name for path in staging.iterdir() if path.is_file()}
    if actual != expected:
        raise CustodyError(f"staged artifact set differs; expected={sorted(expected)} actual={sorted(actual)}")
    for name, digest in hashes.items():
        if hash_file(staging / name, check=check) != digest:
            raise CustodyError(f"staged artifact hash mismatch: {name}")
    return hashes


def _write_operational_companion(
    *,
    custody_root: Path,
    run_id: str,
    receipt: dict[str, Any],
    phase_hook: Callable[[str, str | None], None] | None,
) -> Path:
    custody_root.mkdir(parents=True, exist_ok=True)
    final = custody_root / run_id
    if final.exists():
        raise CustodyError("operational companion already exists for allocated run id")
    staging = Path(tempfile.mkdtemp(prefix=f".{run_id}.staging-", dir=custody_root))
    try:
        target = staging / "operational-completion.json"
        if phase_hook is not None:
            phase_hook("before_companion_write", None)
        _write_small_json_durable(target, receipt)
        if phase_hook is not None:
            phase_hook("after_companion_write", None)
        fsync_directory(staging)
        os.rename(staging, final)
        if phase_hook is not None:
            phase_hook("after_companion_rename", None)
        fsync_directory(custody_root)
        return final / "operational-completion.json"
    except Exception:
        # Never delete the only failed companion staging evidence.
        raise


def finalize_run(
    *,
    run_root: Path,
    run_id: str,
    artifact_order: Sequence[str],
    producers: Mapping[str, ArtifactProducer],
    integrity_name: str,
    meter: Any,
    guard_telemetry: Callable[[], dict[str, Any]],
    primary_stop: BaseException | None = None,
    check: Callable[[], None] | None = None,
    on_progress: Callable[[dict[str, Any]], None] | None = None,
    cleanup_paths: Sequence[Path] = (),
    phase_hook: Callable[[str, str | None], None] | None = None,
) -> FinalizationResult:
    """Publish one payload and its stable operational companion.

    ``primary_stop`` records a scientific or operational stop already caught by
    the runner.  If later custody fails, the exact object is re-raised with the
    secondary custody error attached, preserving its original type.
    """
    runs = run_root / "runs"
    custody_root = run_root / "runtime-custody"
    runs.mkdir(parents=True, exist_ok=True)
    final = runs / run_id
    if final.exists():
        raise CustodyError("allocated run id already has a final payload directory")
    staging = Path(tempfile.mkdtemp(prefix=f".{run_id}.staging-", dir=runs))
    payload_hashes: dict[str, str] | None = None
    payload_published = False
    phase = "serialization"
    try:
        payload_hashes = _write_payload(
            staging=staging,
            artifact_order=artifact_order,
            producers=producers,
            integrity_name=integrity_name,
            check=check,
            on_progress=on_progress,
            phase_hook=phase_hook,
        )
        phase = "payload_pre_rename_durability"
        fsync_directory(staging)
        fsync_directory(runs)
        if phase_hook is not None:
            phase_hook("before_payload_rename", None)
        phase = "payload_rename"
        os.rename(staging, final)
        payload_published = True
        if phase_hook is not None:
            phase_hook("after_payload_rename", None)
        phase = "payload_parent_durability"
        fsync_directory(runs)
        meter.finish()
        payload_timing = meter.snapshot(finish=False)
    except BaseException as error:
        candidate = final if payload_published else staging
        try:
            _quarantine(runs, candidate, run_id=run_id, phase=phase, error=error)
        except BaseException as secondary:
            _attach_secondary(error, secondary, f"{phase}:quarantine")
        if primary_stop is not None:
            _attach_secondary(primary_stop, error, phase)
            raise primary_stop
        raise

    receipt = {
        "schema": "crypto.autoresearch.operational_completion_receipt.v2",
        "run_id": run_id,
        "state": "durable_payload_published",
        "payload_path": f"runs/{run_id}",
        "payload_artifact_sha256": payload_hashes,
        "timing_through_durable_payload": payload_timing,
        "primary_stop": _typed_error_record(primary_stop),
        "guard_telemetry": guard_telemetry(),
        "terminal_receipt_scope": (
            "The measured boundary ends after durable payload publication. "
            "This separately written receipt excludes its own write, rename, and fsync duration "
            "and contains no self-hash."
        ),
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    phase = "operational_companion"
    try:
        receipt_path = _write_operational_companion(
            custody_root=custody_root,
            run_id=run_id,
            receipt=receipt,
            phase_hook=phase_hook,
        )
    except BaseException as error:
        try:
            _quarantine(runs, final, run_id=run_id, phase=phase, error=error)
        except BaseException as secondary:
            _attach_secondary(error, secondary, f"{phase}:payload_quarantine")
        if primary_stop is not None:
            _attach_secondary(primary_stop, error, phase)
            raise primary_stop
        raise CustodyError(
            f"operational companion failed after payload publication: {type(error).__name__}: {error}"
        ) from error

    cleanup_errors: list[str] = []
    for path in cleanup_paths:
        try:
            if path.exists():
                shutil.rmtree(path)
        except BaseException as error:
            # Both required durable records already exist.  Retain the progress
            # tree and report the cleanup problem without rewriting the stable
            # receipt or destroying either custody namespace.
            cleanup_errors.append(f"{path}: {type(error).__name__}: {error}")
    return FinalizationResult(
        payload_path=final,
        operational_receipt_path=receipt_path,
        payload_artifact_sha256=payload_hashes,
        timing_through_durable_payload=payload_timing,
        cleanup_errors=cleanup_errors,
    )
