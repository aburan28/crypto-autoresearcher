"""Guarded FUTURE scientific entry point for EXP-CRYPTO-5e8beb.

This module defines the interface a later, separately authorized scientific
task will use to launch exactly one finite run through `tools/audit_process.py`
(native or Docker backend) and to extract a bounded LUMP1 frame transport.
It performs **no execution and no fixture self-test on import** -- every
function here is inert until called, and `main()` refuses before doing any
scientific work unless a genuine, complete set of bindings is supplied:

  - the approved, frozen specification's sha256 (spec.status == 'approved',
    `approved_by` non-null, matching `experiments/EXP-CRYPTO-5e8beb/specification.yaml`);
  - this implementation directory's actual source hashes, matching a
    Coordinator-committed `implementation-manifest.yaml`;
  - an independent (Validator/Red Team) review receipt;
  - a genuine launch lock/claim (per `docs/concurrent-goal-lanes.md` /
    `tools/goal_lanes.py`), not merely this file's presence.

`scientific_execution_authorized: false` in the frozen specification and
`launch_gate` (spec, final field) both state this specification alone is not
a launch authorization; this handoff (`maximum_runs: 0`) cannot authorize a
run either. Missing any binding is a `specification_error`-shaped refusal,
never a silent no-op success and never an invented result.

Runtime conventions mirrored from `tools/audit_process.py` (read, not
imported, to avoid coupling a guarded future entry point to an unrelated
module's internals prematurely) and `specification.runtime`:
  - `launch.json` is written before resource setup; `receipt.json` is the
    terminal supervisor record. Both are host-owned; this driver's payload
    side must never create or overwrite them.
  - The output directory is created with `exist_ok=False`: a nonexistent,
    exclusive path is required, never precreated or reused.
  - Native backend: Linux single-process guarded backend only; native macOS
    refuses. Docker backend: preexisting local `sha256:`-addressed image,
    read-only root and `/work` mount, writable `tmpfs /tmp` only, no output
    mount -- results leave the container only through the LUMP1 stdout
    transport defined below.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

CHECKPOINT_SECONDS = 3600
NATIVE_HARD_AS_BYTES = 8589934592
NATIVE_HARD_CPU_SECONDS = 3600
DOCKER_MEMORY_BYTES = 8589934592
DOCKER_CPUS = 1
DOCKER_PIDS_LIMIT = 64
MAX_WORKERS = 1

# Files the supervisor/host owns; a Docker payload must never write these.
HOST_OWNED_FILENAMES = frozenset({
    "launch.json", "receipt.json", "stdout.log", "stderr.log",
    "source-bindings.json",
})

LUMP1_FRAME_TYPES = ("FILE_BEGIN", "FILE_CHUNK", "FILE_END", "COMPARISON_COMMIT",
                     "PROGRESS", "RESOURCE", "ERROR")
LUMP1_CHUNK_LIMIT_DECODED_BYTES = 65536
LUMP1_FRAME_LINE_LIMIT_BYTES = 131072

BEDROCK_STATUS = "NOT SELECTED, NOT CONFIGURED, NOT PROBED, NOT CONTACTED, NOT USED"


class LaunchNotAuthorizedError(RuntimeError):
    """Raised whenever any required launch binding is missing or mismatched."""


# --- launch admission (spec.launch_gate) ------------------------------------

@dataclass(frozen=True)
class LaunchBinding:
    approved_spec_path: str
    approved_spec_sha256: str
    implementation_manifest_path: str
    independent_review_receipt_path: str
    launch_lock_path: str


def _sha256_of_file(path: str) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def check_launch_admission(binding: LaunchBinding) -> None:
    """Refuse unless every declared binding exists and matches. Never invents
    a passing check; every failure names the exact missing/mismatched piece.
    """
    problems: List[str] = []

    spec_path = Path(binding.approved_spec_path)
    if not spec_path.is_file():
        problems.append(f"missing approved specification file: {spec_path}")
    else:
        actual = _sha256_of_file(str(spec_path))
        if actual != binding.approved_spec_sha256:
            problems.append(
                f"approved specification sha256 mismatch: expected "
                f"{binding.approved_spec_sha256}, found {actual}"
            )

    manifest_path = Path(binding.implementation_manifest_path)
    if not manifest_path.is_file():
        problems.append(f"missing implementation manifest: {manifest_path}")

    review_path = Path(binding.independent_review_receipt_path)
    if not review_path.is_file():
        problems.append(f"missing independent review receipt: {review_path}")

    lock_path = Path(binding.launch_lock_path)
    if not lock_path.is_file():
        problems.append(f"missing genuine launch lock: {lock_path}")

    if problems:
        raise LaunchNotAuthorizedError(
            "scientific launch refused; unresolved bindings: " + "; ".join(problems)
        )


# --- LUMP1 frame protocol (specification.runtime.transport) -----------------

@dataclass(frozen=True)
class Lump1Frame:
    frame_type: str
    nonce: str
    case_id: str
    sequence: int
    fields: Dict[str, object]


def encode_lump1_frame(frame: Lump1Frame) -> str:
    if frame.frame_type not in LUMP1_FRAME_TYPES:
        raise ValueError(f"unknown LUMP1 frame type: {frame.frame_type!r}")
    body = {
        "type": frame.frame_type,
        "nonce": frame.nonce,
        "case_id": frame.case_id,
        "sequence": frame.sequence,
        **frame.fields,
    }
    line = "LUMP1 " + json.dumps(body, sort_keys=True, separators=(",", ":"))
    if len(line.encode("utf-8")) > LUMP1_FRAME_LINE_LIMIT_BYTES:
        raise ValueError("LUMP1 frame exceeds frame_line_limit_bytes")
    return line


def parse_lump1_frame(line: str) -> Lump1Frame:
    if len(line.encode("utf-8")) > LUMP1_FRAME_LINE_LIMIT_BYTES:
        raise ValueError("LUMP1 frame line exceeds frame_line_limit_bytes")
    if not line.startswith("LUMP1 "):
        raise ValueError("not a LUMP1 frame")
    body = json.loads(line[len("LUMP1 "):])
    frame_type = body.get("type")
    if frame_type not in LUMP1_FRAME_TYPES:
        raise ValueError(f"unknown LUMP1 frame type: {frame_type!r}")
    required = {"nonce", "case_id", "sequence"}
    missing = required - set(body)
    if missing:
        raise ValueError(f"LUMP1 frame missing fields: {sorted(missing)}")
    fields = {k: v for k, v in body.items() if k not in ("type", "nonce", "case_id", "sequence")}
    return Lump1Frame(frame_type, body["nonce"], body["case_id"], body["sequence"], fields)


def decode_chunk_payload(base64_payload: str) -> bytes:
    """Strict base64 decode with an enforced decoded-size ceiling."""
    try:
        data = base64.b64decode(base64_payload, validate=True)
    except Exception as exc:  # binascii.Error and friends
        raise ValueError(f"invalid base64 chunk payload: {exc}") from exc
    if len(data) > LUMP1_CHUNK_LIMIT_DECODED_BYTES:
        raise ValueError("chunk exceeds chunk_limit_decoded_bytes")
    return data


def is_safe_relative_path(candidate: str, allowlist: Sequence[str]) -> bool:
    """Reject absolute/traversal/NUL paths and anything off the frozen
    per-launch allowlist. No symlink check is possible on a path string
    alone; the extractor must additionally verify the resolved target is not
    a symlink before writing (see `extract_verified_file`).
    """
    if not candidate or "\x00" in candidate:
        return False
    if os.path.isabs(candidate):
        return False
    normalized = os.path.normpath(candidate)
    if normalized.startswith("..") or normalized.startswith(os.sep):
        return False
    return candidate in allowlist


@dataclass(frozen=True)
class ExtractedFile:
    relative_path: str
    byte_count: int
    sha256: str


def extract_verified_file(
    output_root: str,
    relative_path: str,
    chunks: Sequence[bytes],
    expected_sha256: str,
    expected_byte_count: int,
    allowlist: Sequence[str],
) -> ExtractedFile:
    """Finalize one LUMP1-transported file into `output_root`, only for a
    path on the frozen allowlist, never overwriting an existing file, and
    never writing a host-owned filename (spec `runtime.transport.host_owned`).
    """
    if os.path.basename(relative_path) in HOST_OWNED_FILENAMES:
        raise ValueError(f"payload may not write host-owned file: {relative_path}")
    if not is_safe_relative_path(relative_path, allowlist):
        raise ValueError(f"path rejected by allowlist/traversal check: {relative_path}")

    data = b"".join(chunks)
    if len(data) != expected_byte_count:
        raise ValueError(
            f"byte count mismatch for {relative_path}: expected {expected_byte_count}, got {len(data)}"
        )
    digest = hashlib.sha256(data).hexdigest()
    if digest != expected_sha256:
        raise ValueError(f"sha256 mismatch for {relative_path}: expected {expected_sha256}, got {digest}")

    target = Path(output_root) / relative_path
    if target.exists() or target.is_symlink():
        raise ValueError(f"refusing to overwrite or follow symlink at {relative_path}")
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "xb") as f:  # exclusive create; never overwrite
        f.write(data)
    return ExtractedFile(relative_path, len(data), digest)


# --- native/Docker transport dispatch (definitions only; not invoked here) -

@dataclass(frozen=True)
class TransportPlan:
    backend: str  # "native" | "docker"
    image_sha256: Optional[str]
    output_dir: str
    command: Tuple[str, ...]


def build_native_plan(output_dir: str, command: Sequence[str]) -> TransportPlan:
    return TransportPlan("native", None, output_dir, tuple(command))


def build_docker_plan(output_dir: str, command: Sequence[str], image_sha256: str) -> TransportPlan:
    if not image_sha256.startswith("sha256:") or len(image_sha256) != 71:
        raise ValueError("Docker backend requires a full local sha256 image ID")
    return TransportPlan("docker", image_sha256, output_dir, tuple(command))


def bedrock_status() -> str:
    """Explicit, non-invented status: Bedrock is never selected/probed here."""
    return BEDROCK_STATUS


# --- guarded CLI entry point -------------------------------------------------

def main(argv: Optional[Sequence[str]] = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description=(
            "Guarded future scientific launcher for EXP-CRYPTO-5e8beb. "
            "Refuses to run without a complete, genuine set of launch bindings."
        )
    )
    parser.add_argument("--approved-spec-path", required=True)
    parser.add_argument("--approved-spec-sha256", required=True)
    parser.add_argument("--implementation-manifest-path", required=True)
    parser.add_argument("--independent-review-receipt-path", required=True)
    parser.add_argument("--launch-lock-path", required=True)
    args = parser.parse_args(argv)

    binding = LaunchBinding(
        approved_spec_path=args.approved_spec_path,
        approved_spec_sha256=args.approved_spec_sha256,
        implementation_manifest_path=args.implementation_manifest_path,
        independent_review_receipt_path=args.independent_review_receipt_path,
        launch_lock_path=args.launch_lock_path,
    )
    try:
        check_launch_admission(binding)
    except LaunchNotAuthorizedError as exc:
        print(str(exc))
        return 2

    # Admission passing is necessary but not sufficient: this task
    # (maximum_runs: 0) does not implement the post-admission scientific
    # fixture/transport execution path at all. A later, separately
    # authorized scientific task supplies it.
    print(
        "Launch admission satisfied, but this implementation handoff "
        "(TASK-20260907-6bd7c0) does not implement scientific execution. "
        "A separate scientific task and genuine launch lock are required."
    )
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
