"""Consolidated guarded driver for EXP-CRYPTO-5e8beb (implementation-v3).

This module supersedes, for a single self-contained directory, both
`implementation/driver.py` (LUMP1 transport, transport-plan builders,
existence-only admission gate) and `implementation-v2/driver.py` (an
always-refusing placeholder). It closes two independently-confirmed review
gaps from
`coordination/design/BATCH-51d1bb/reviews/TASK-20260908-0eabfe/implementation-review.yaml`:

  - C10: `check_launch_admission` now performs genuine CONTENT verification
    of all four required bindings (approved spec YAML, implementation
    manifest hashes, independent review receipt, launch lock claim) instead
    of existence-only / caller-suppliable-hash checks. See the four
    `_check_*` helpers below.
  - C8: `panel_scoring.py` (copied in unchanged from `implementation-v2/`,
    independently re-verified by this task -- see
    `implementation-report.yaml`'s `panel_scoring_reverification` block and
    this task's own synthetic re-derivation script) is wired to this
    driver's `assemble_panel_metadata` so a genuinely admitted launch could
    produce a real positive/negative panel-advantage decision.

This task (`TASK-20260913-c43d3e`, handoff `ledger/handoffs/TASK-20260913-c43d3e.yaml`)
still does NOT authorize any scientific run:
`scientific_execution_authorized: false` in the frozen specification and
this handoff's `maximum_runs: 0` both bind. `run_scientific_pipeline` below
is real, callable, end-to-end code (fixture generation through
certificate/panel-score output) -- implementing the launch_gate's
post-admission execution path is exactly what this task's completion_gate
requires -- but it is NEVER invoked by this module against the specification's
actual frozen panel (N in {11,15,17}, seeds 0..31, kernels R1-R4/P/U) during
this task. It is smoke-tested only against an explicitly-labeled non-frozen
toy panel (N in {3,4}), per this task's constraints. No launch lock exists
for this task, so `main()` is never invoked here with a bundle that would
pass admission.

Runtime conventions mirrored from `tools/audit_process.py` (read, not
imported) and `specification.runtime`, unchanged from `implementation/driver.py`:
  - `launch.json` is written before resource setup; `receipt.json` is the
    terminal supervisor record. Both are host-owned; this driver's payload
    side must never create or overwrite them.
  - The output directory is created with `exist_ok=False` by the supervisor;
    this driver never precreates or reuses it when running under the real
    supervisor flow (see `run_scientific_pipeline`'s `create_output_dir`).
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
from dataclasses import dataclass
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import yaml

import fixtures
import kernels
import transcripts
import reference
import certificates
import panel_scoring

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

CLAIM_SCHEMA = "crypto.autoresearch.task_claim.v1"  # tools/goal_lanes.py CLAIM_SCHEMA


class LaunchNotAuthorizedError(RuntimeError):
    """Raised whenever any required launch binding is missing, unparseable,
    or fails a content check. Fail-closed: every problem is named."""


# --- launch admission (spec.launch_gate) ------------------------------------
# IMPLEMENTATION-V3: real content verification for all four bindings (C10).

@dataclass(frozen=True)
class LaunchBinding:
    approved_spec_path: str
    implementation_dir: str
    implementation_manifest_path: str
    independent_review_receipt_path: str
    launch_lock_path: str
    expected_spec_experiment_id: str = "EXP-CRYPTO-5e8beb"
    expected_reviewed_commit: Optional[str] = None
    expected_reviewed_path_fragment: Optional[str] = None
    expected_task_id: Optional[str] = None
    expected_write_scope_prefix: str = "experiments/EXP-CRYPTO-5e8beb/"


def _sha256_of_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _check_approved_spec(binding: LaunchBinding) -> List[str]:
    """(a) Parse the approved spec's own YAML content and require
    status=='approved' and approved_by non-null -- not a caller-supplied
    hash comparison alone."""
    path = Path(binding.approved_spec_path)
    if not path.is_file():
        return [f"missing approved specification file: {path}"]
    try:
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return [f"approved specification failed to parse as YAML: {exc}"]
    experiment = doc.get("experiment") if isinstance(doc, dict) else None
    if not isinstance(experiment, dict):
        return ["approved specification has no top-level 'experiment' mapping"]
    problems: List[str] = []
    if experiment.get("status") != "approved":
        problems.append(f"specification status is {experiment.get('status')!r}, not 'approved'")
    if not experiment.get("approved_by"):
        problems.append("specification approved_by is null or empty")
    if binding.expected_spec_experiment_id and experiment.get("id") != binding.expected_spec_experiment_id:
        problems.append(
            f"specification id {experiment.get('id')!r} does not match expected "
            f"{binding.expected_spec_experiment_id!r}"
        )
    if not experiment.get("frozen"):
        problems.append("specification frozen field is not true")
    return problems


def _check_implementation_manifest(binding: LaunchBinding) -> List[str]:
    """(b) Read implementation-manifest.yaml's implementation_files_sha256
    entries and compare each against the actual current bytes of the
    corresponding file in implementation_dir -- not merely file existence."""
    manifest_path = Path(binding.implementation_manifest_path)
    if not manifest_path.is_file():
        return [f"missing implementation manifest: {manifest_path}"]
    try:
        doc = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return [f"implementation manifest failed to parse as YAML: {exc}"]
    manifest = doc.get("implementation_manifest") if isinstance(doc, dict) else None
    if not isinstance(manifest, dict):
        return ["implementation manifest has no top-level 'implementation_manifest' mapping"]
    hashes = manifest.get("implementation_files_sha256")
    if not isinstance(hashes, dict) or not hashes:
        return ["implementation manifest has no non-empty implementation_files_sha256 mapping"]
    impl_dir = Path(binding.implementation_dir)
    problems: List[str] = []
    for filename, expected_hash in hashes.items():
        if not isinstance(filename, str) or not isinstance(expected_hash, str):
            problems.append(f"manifest entry {filename!r}: non-string filename/hash")
            continue
        file_path = impl_dir / filename
        if not file_path.is_file():
            problems.append(f"manifest lists {filename!r} but it is missing at {file_path}")
            continue
        actual = _sha256_of_file(file_path)
        if actual != expected_hash:
            problems.append(
                f"sha256 mismatch for {filename}: manifest says {expected_hash}, actual on disk is {actual}"
            )
    return problems


def _extract_review_verdict_commit_haystack(doc: dict) -> Tuple[Optional[str], Optional[str], str]:
    """Best-effort extraction across the two review-receipt shapes actually
    used in this repository: the `validation_report` schema in
    `agents/validator.md` (`verdict: passed|failed|incomplete|invalid`) and
    the `implementation_review` shape used for static implementation reviews
    (`verdict: PASSED|REVISE|FAILED`, plus `review_attestation.verdict` and
    `snapshot_verification.commit_reviewed`). Returns (verdict, commit,
    full-document-json-haystack) for the caller to check.
    """
    verdict = None
    commit = None
    for top_key in ("validation_report", "implementation_review"):
        block = doc.get(top_key)
        if isinstance(block, dict):
            if verdict is None and "verdict" in block:
                verdict = block["verdict"]
            snap = block.get("snapshot_verification")
            if isinstance(snap, dict) and commit is None:
                commit = snap.get("commit_reviewed")
            attestation = block.get("review_attestation")
            if isinstance(attestation, dict) and verdict is None:
                verdict = attestation.get("verdict")
    if verdict is None and "verdict" in doc:
        verdict = doc["verdict"]
    haystack = json.dumps(doc, sort_keys=True, default=str)
    return verdict, commit, haystack


def _check_independent_review_receipt(binding: LaunchBinding) -> List[str]:
    """(c) Parse the receipt as YAML, require a passed-equivalent verdict
    bound to the exact reviewed commit/path -- not merely file existence."""
    path = Path(binding.independent_review_receipt_path)
    if not path.is_file():
        return [f"missing independent review receipt: {path}"]
    try:
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return [f"independent review receipt failed to parse as YAML: {exc}"]
    if not isinstance(doc, dict):
        return ["independent review receipt did not parse to a mapping"]
    verdict, commit, haystack = _extract_review_verdict_commit_haystack(doc)
    problems: List[str] = []
    if verdict is None:
        problems.append("independent review receipt has no recognizable verdict field")
    elif str(verdict).strip().lower() != "passed":
        problems.append(f"independent review receipt verdict is {verdict!r}, not a passed-equivalent")
    if binding.expected_reviewed_commit is not None:
        if commit != binding.expected_reviewed_commit:
            problems.append(
                f"independent review receipt's reviewed commit {commit!r} does not match "
                f"expected {binding.expected_reviewed_commit!r}"
            )
    if binding.expected_reviewed_path_fragment is not None:
        if binding.expected_reviewed_path_fragment not in haystack:
            problems.append(
                f"independent review receipt does not reference expected reviewed path "
                f"fragment {binding.expected_reviewed_path_fragment!r}"
            )
    return problems


def _parse_claim_timestamp(value: Any) -> datetime:
    if not isinstance(value, str) or not value:
        raise ValueError("timestamp must be a non-empty string")
    text = value[:-1] + "+00:00" if value.endswith("Z") else value
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        raise ValueError("timestamp must carry a timezone")
    return parsed.astimezone(timezone.utc)


def _check_launch_lock(binding: LaunchBinding) -> List[str]:
    """(d) Read the launch lock via tools/goal_lanes.py's actual claim-file
    schema (crypto.autoresearch.task_claim.v1): a live, unexpired claim
    naming this task's own write scope, with no sibling release file for the
    same (task_id, epoch) -- not merely Path.is_file(). Reimplemented here
    (rather than importing tools/goal_lanes.py) so implementation-v3 stays a
    self-contained directory, but the field semantics (schema string, epoch
    fencing, expires_at, write_scope, sibling release ends a claim) are
    reproduced exactly from that module.
    """
    path = Path(binding.launch_lock_path)
    if not path.is_file():
        return [f"missing genuine launch lock: {path}"]
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"launch lock failed to parse as JSON: {exc}"]
    if not isinstance(doc, dict):
        return ["launch lock did not parse to a JSON object"]
    problems: List[str] = []
    if doc.get("schema") != CLAIM_SCHEMA:
        problems.append(f"launch lock schema is {doc.get('schema')!r}, expected {CLAIM_SCHEMA!r}")
    if binding.expected_task_id is not None and doc.get("task_id") != binding.expected_task_id:
        problems.append(
            f"launch lock task_id {doc.get('task_id')!r} does not match expected "
            f"{binding.expected_task_id!r}"
        )
    owner = doc.get("owner")
    if not isinstance(owner, str) or not owner:
        problems.append("launch lock has no valid non-empty 'owner'")
    expires_at = doc.get("expires_at")
    expiry: Optional[datetime] = None
    try:
        expiry = _parse_claim_timestamp(expires_at)
    except (ValueError, TypeError) as exc:
        problems.append(f"launch lock expires_at is unparseable ({expires_at!r}): {exc}")
    if expiry is not None and datetime.now(timezone.utc) >= expiry:
        problems.append(f"launch lock is expired (expires_at={expires_at})")
    write_scope = doc.get("write_scope")
    if not isinstance(write_scope, list) or not any(
        isinstance(entry, str) and entry.startswith(binding.expected_write_scope_prefix)
        for entry in write_scope
    ):
        problems.append(
            f"launch lock write_scope {write_scope!r} does not name a path starting with "
            f"{binding.expected_write_scope_prefix!r}"
        )
    epoch = doc.get("epoch")
    task_id = doc.get("task_id")
    if isinstance(epoch, int) and isinstance(task_id, str):
        release_path = path.parent / f"{task_id}.{epoch}.release.json"
        if release_path.is_file():
            problems.append(
                f"launch lock has a sibling release file ({release_path.name}); "
                "the claim it names is no longer live"
            )
    else:
        problems.append("launch lock has no integer 'epoch' and string 'task_id'; cannot check for a release")
    return problems


def check_launch_admission(binding: LaunchBinding) -> None:
    """Refuse unless every declared binding exists AND its content genuinely
    verifies. Never invents a passing check; every failure names the exact
    missing/mismatched/unparseable piece. Fail-closed: any exception raised
    by a sub-check is caught by that sub-check itself and turned into a
    named problem, never allowed to silently pass admission.
    """
    problems: List[str] = []
    problems += _check_approved_spec(binding)
    problems += _check_implementation_manifest(binding)
    problems += _check_independent_review_receipt(binding)
    problems += _check_launch_lock(binding)

    if problems:
        raise LaunchNotAuthorizedError(
            "scientific launch refused; unresolved bindings: " + "; ".join(problems)
        )


# --- LUMP1 frame protocol (specification.runtime.transport) -----------------
# Unchanged from implementation/driver.py.

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
    import os
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
    import os
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


# --- C8: panel-advantage scoring wiring --------------------------------------
# panel_scoring.py is copied in unchanged from implementation-v2/ (see
# implementation-manifest.yaml for its sha256, matching the copied file's
# on-disk hash). This section assembles the metadata dict
# panel_scoring.score_panel_advantage expects out of real
# kernels.KernelCertificate objects, so a genuinely admitted future launch
# can actually decide conjecture_positive/conjecture_negative -- not just
# compute raw per-partition certificates with no scoring step (C8's gap).

def assemble_panel_metadata(
    certs_by_key: Dict[Tuple[int, int, str, Optional[int]], Dict[str, kernels.KernelCertificate]],
    controls: Dict[str, bool],
    validity: bool,
) -> dict:
    """Build the exact input shape panel_scoring.score_panel_advantage
    expects (specification.panel_advantage) from a mapping
    `(N, q, kind, seed) -> {kernel_name: KernelCertificate}`, where kind is
    "coordinate" (seed=None) or "matched" (seed=0..31).

    Raises KeyError with a clear message if a required (N, q, kind[, seed],
    kernel) combination is absent from `certs_by_key` -- this function never
    silently substitutes a zero or a fabricated value for missing data.
    """
    rows = []
    for n, q, kernel_name in panel_scoring.PANEL_IDS:
        coord_key = (n, q, "coordinate", None)
        if coord_key not in certs_by_key or kernel_name not in certs_by_key[coord_key]:
            raise KeyError(f"missing coordinate certificate for N={n} q={q} kernel={kernel_name}")
        coordinate_delta = certs_by_key[coord_key][kernel_name].delta
        nulls = []
        for seed in panel_scoring.SEEDS:
            matched_key = (n, q, "matched", seed)
            if matched_key not in certs_by_key or kernel_name not in certs_by_key[matched_key]:
                raise KeyError(f"missing matched certificate for N={n} q={q} kernel={kernel_name} seed={seed}")
            nulls.append({
                "seed": seed,
                "delta": panel_scoring.rational(certs_by_key[matched_key][kernel_name].delta),
            })
        rows.append({
            "N": n, "q": q, "kernel": kernel_name,
            "coordinate_delta": panel_scoring.rational(coordinate_delta),
            "nulls": nulls,
        })
    return {"panels": rows, "validity": validity, "controls": dict(controls)}


# --- C10 completion: the actual end-to-end scientific execution path -------
# Real, callable code (fixture generation through certificate/panel-score
# output), per specification.artifacts' file/directory layout. NEVER invoked
# by this task against the real frozen panel (see module docstring). Smoke
# tested only against an explicitly-labeled non-frozen toy panel.

def _write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "x", encoding="utf-8") as fh:
        json.dump(obj, fh, sort_keys=True, indent=2)
        fh.write("\n")


def _serialize_law(law: dict) -> dict:
    return {
        "labels": list(law["labels"]),
        "nu": {str(l): panel_scoring.rational(p) for l, p in law["nu"].items()},
        "mu": {str(l): {str(d): panel_scoring.rational(p) for d, p in row.items()}
               for l, row in law["mu"].items()},
    }


def _serialize_K(K: dict) -> dict:
    return {
        str(x): {str(l): {str(b): panel_scoring.rational(p) for b, p in row.items()}
                 for l, row in labels.items()}
        for x, labels in K.items()
    }


def write_partition_artifacts(run_dir: Path, record: "fixtures.PartitionRecord") -> None:
    base = run_dir / certificates.expected_partition_dir(record.spec.index)
    _write_json(base / "feature.json", {"feature": list(record.feature)})
    fibers = kernels.fibers_of(record.feature, record.spec.N)
    _write_json(base / "fibers.json", {str(k): v for k, v in fibers.items()})
    generation = None
    if record.generation is not None:
        generation = {
            "total_digests": record.generation.total_digests,
            "rejected_digests": record.generation.rejected_digests,
        }
    _write_json(base / "generation.json", generation)
    _write_json(base / "description.json", fixtures.canonical_descriptor(record))


def write_kernel_artifacts(
    run_dir: Path, index: int, kernel_name: str, law: dict,
    K: dict, cert: "kernels.KernelCertificate", checker_report: dict,
) -> None:
    base = run_dir / certificates.expected_kernel_dir(index, kernel_name)
    _write_json(base / "law.json", _serialize_law(law))
    _write_json(base / "K.json", _serialize_K(K))
    pair_tv_path = base / "pair-TV.jsonl"
    pair_tv_path.parent.mkdir(parents=True, exist_ok=True)
    with open(pair_tv_path, "x", encoding="utf-8") as fh:
        for pc in cert.pair_certs:
            row = {
                "x": pc.x, "xp": pc.xp,
                "per_label_tv": {str(l): panel_scoring.rational(v) for l, v in pc.per_label_tv.items()},
                "joint_tv": panel_scoring.rational(pc.joint_tv),
            }
            fh.write(json.dumps(row, sort_keys=True) + "\n")
    _write_json(base / "maxima.json", {
        "delta_l": {str(l): panel_scoring.rational(v) for l, v in cert.delta_l.items()},
        "delta_l_witness": {str(l): list(w) if w else None for l, w in cert.delta_l_witness.items()},
        "delta": panel_scoring.rational(cert.delta),
        "delta_witness": list(cert.delta_witness) if cert.delta_witness else None,
        "per_operation_max": panel_scoring.rational(cert.per_operation_max),
        "per_operation_max_label": cert.per_operation_max_label,
    })
    _write_json(base / "checker-report.json", checker_report)


def write_transcript_artifacts(
    run_dir: Path, index: int, kernel_name: str, x: int, t: int,
    real_dist: dict, sim_dist: dict, ref_dist: dict, tv_certificate: dict, status: dict,
) -> None:
    base = run_dir / certificates.expected_transcript_dir(index, kernel_name, x, t)
    _write_json(base / "real-joint.json", certificates.serialize_distribution(real_dist))
    _write_json(base / "simulator-joint.json", certificates.serialize_distribution(sim_dist))
    _write_json(base / "reference-joint.json", certificates.serialize_distribution(ref_dist))
    _write_json(base / "TV-certificate.json", tv_certificate)
    _write_json(base / "status.json", status)


def certify_partition_kernel(
    N: int, feature: Sequence[int], kernel_name: str,
) -> Tuple[dict, dict, "kernels.KernelCertificate", dict]:
    """Producer kernel certification plus an independent reference
    cross-check (spec `computation.independent_checker`,
    `controls.independent_exact_tables`)."""
    law = kernels.reduced_law(kernel_name, N)
    K = kernels.build_K(law, N, feature)
    cert = kernels.certify_kernel(kernel_name, N, feature)
    ref_scores = reference.reference_kernel_scores(kernel_name, N, feature)
    agree = (
        reference.agrees_exactly(cert.delta, ref_scores["delta"])
        and reference.agrees_exactly(cert.per_operation_max, ref_scores["per_operation_max"])
        and all(
            reference.agrees_exactly(cert.delta_l.get(l), ref_scores["delta_l"].get(l))
            for l in set(cert.delta_l) | set(ref_scores["delta_l"])
        )
    )
    checker_report = {
        "producer_reference_agreement": agree,
        "producer_delta": panel_scoring.rational(cert.delta),
        "reference_delta": panel_scoring.rational(ref_scores["delta"]),
    }
    return law, K, cert, checker_report


def certify_transcript(
    law: dict, N: int, feature: Sequence[int], kernel_name: str, x0: int, horizon: int,
) -> Tuple[dict, dict, dict, dict, dict]:
    """Producer real/simulator DP plus independent reference latent-path
    enumeration cross-check, plus the frozen coupling-bound arithmetic."""
    real_joint, real_marginal = transcripts.real_transcript_distribution(law, N, feature, x0, horizon)
    sim_joint, sim_marginal = transcripts.simulator_transcript_distribution(law, N, feature, x0, horizon)
    ref_dist = reference.reference_real_transcript_distribution(kernel_name, N, feature, x0, horizon)
    ref_sim = reference.reference_simulator_transcript_distribution(kernel_name, N, feature, x0, horizon)
    full_tv = kernels.total_variation(real_marginal, sim_marginal)
    ref_full_tv = reference.reference_full_transcript_tv(kernel_name, N, feature, x0, horizon)
    delta = kernels.certify_kernel(kernel_name, N, feature).delta
    bound = transcripts.coupling_bound(horizon, delta)
    vacuous = transcripts.is_vacuous(bound)
    agree = (
        reference.agrees_exactly(real_marginal, ref_dist)
        and reference.agrees_exactly(sim_marginal, ref_sim)
        and reference.agrees_exactly(full_tv, ref_full_tv)
    )
    bound_violated = full_tv > bound
    tv_certificate = {
        "full_joint_transcript_tv": panel_scoring.rational(full_tv),
        "bound": panel_scoring.rational(bound),
        "vacuous": vacuous,
        "bound_violated": bound_violated,
        "producer_reference_agreement": agree,
    }
    status = {
        "status": (
            certificates.CertificateStatus.VACUOUS_BOUND.value if vacuous
            else certificates.CertificateStatus.OK.value
        ),
        "agrees_with_reference": agree,
    }
    return real_marginal, sim_marginal, ref_dist, tv_certificate, status


def run_scientific_pipeline(
    output_dir: str,
    partition_specs: Sequence["fixtures.PartitionSpec"],
    horizons: Sequence[int] = (0, 1, 2, 3),
    kernel_names: Sequence[str] = fixtures.KERNEL_ORDER,
    write_files: bool = True,
    create_output_dir: bool = True,
) -> dict:
    """Full fixture-to-certificate pipeline: for each declared partition spec,
    build the partition, certify every declared kernel (with an independent
    reference cross-check), and propagate real/simulator transcripts for
    every initial state and horizon (also cross-checked against reference.py).

    This is the callable code implementing specification.computation and
    specification.artifacts' file layout end to end. It is intentionally
    generic over `partition_specs`: this task supplies only a small,
    explicitly non-frozen toy panel for a structural smoke test (see
    implementation-report.yaml); a real launch would supply
    `fixtures.iter_partition_specs()` (all 272 fixed partitions) instead --
    this task never does that.
    """
    run_dir = Path(output_dir)
    if create_output_dir:
        run_dir.mkdir(parents=True, exist_ok=False)
    elif not run_dir.is_dir():
        raise FileNotFoundError(
            f"{run_dir} does not exist; the supervisor must create the exclusive output "
            "directory before this pipeline writes into it"
        )

    certs_by_key: Dict[Tuple[int, int, str, Optional[int]], Dict[str, kernels.KernelCertificate]] = {}
    total_transcript_checks = 0
    total_kernel_cells = 0
    all_agree = True

    for spec in partition_specs:
        record = fixtures.build_partition(spec)
        if write_files:
            write_partition_artifacts(run_dir, record)
        key = (spec.N, spec.q, spec.kind, spec.seed)
        certs_by_key.setdefault(key, {})
        for kernel_name in kernel_names:
            law, K, cert, checker_report = certify_partition_kernel(spec.N, record.feature, kernel_name)
            certs_by_key[key][kernel_name] = cert
            total_kernel_cells += 1
            all_agree = all_agree and checker_report["producer_reference_agreement"]
            if write_files:
                write_kernel_artifacts(run_dir, spec.index, kernel_name, law, K, cert, checker_report)
            for x0 in range(spec.N):
                for t in horizons:
                    real_m, sim_m, ref_d, tv_cert, status = certify_transcript(
                        law, spec.N, record.feature, kernel_name, x0, t
                    )
                    total_transcript_checks += 1
                    all_agree = all_agree and tv_cert["producer_reference_agreement"]
                    if write_files:
                        write_transcript_artifacts(
                            run_dir, spec.index, kernel_name, x0, t, real_m, sim_m, ref_d, tv_cert, status
                        )

    summary = {
        "partitions_processed": len(list(partition_specs)),
        "kernel_cells_processed": total_kernel_cells,
        "transcript_checks_processed": total_transcript_checks,
        "producer_reference_agreement": all_agree,
        "certs_by_key": certs_by_key,
        "output_dir": str(run_dir),
    }
    return summary


def run_assumption_trap(output_dir: Optional[str] = None, write_files: bool = True) -> dict:
    """Certify all 11 assumption-trap starts (producer + independent
    reference), classified `bound_inapplicable`, never a counterexample."""
    all_agree = True
    certs = transcripts.certify_all_trap_starts()
    for x0, cert in certs.items():
        ref_cert = reference.reference_trap_certificate(x0)
        agree = (
            reference.agrees_exactly(cert.full_transcript_tv, ref_cert["full_transcript_tv"])
            and reference.agrees_exactly(cert.final_marginal_tv, ref_cert["final_marginal_tv"])
            and cert.classification == ref_cert["classification"] == "bound_inapplicable"
        )
        all_agree = all_agree and agree
        if write_files and output_dir is not None:
            base = Path(output_dir) / certificates.expected_trap_dir(x0)
            _write_json(base / "real-joint.json", certificates.serialize_distribution(cert.real))
            _write_json(base / "simulator-joint.json", certificates.serialize_distribution(cert.comparison))
            _write_json(base / "reference-joint.json", certificates.serialize_distribution(ref_cert["real"]))
            _write_json(base / "TV-certificate.json", {
                "full_transcript_tv": panel_scoring.rational(cert.full_transcript_tv),
                "final_marginal_tv": panel_scoring.rational(cert.final_marginal_tv),
            })
            _write_json(base / "assumption-status.json", {
                "classification": cert.classification, "agrees_with_reference": agree,
            })
    return {"trap_starts_processed": len(certs), "producer_reference_agreement": all_agree}


# --- guarded CLI entry point -------------------------------------------------

def main(argv: Optional[Sequence[str]] = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description=(
            "Guarded scientific launcher for EXP-CRYPTO-5e8beb (implementation-v3). "
            "Refuses to run without a complete, content-verified set of launch bindings."
        )
    )
    parser.add_argument("--approved-spec-path", required=True)
    parser.add_argument("--implementation-dir", required=True)
    parser.add_argument("--implementation-manifest-path", required=True)
    parser.add_argument("--independent-review-receipt-path", required=True)
    parser.add_argument("--launch-lock-path", required=True)
    parser.add_argument("--expected-reviewed-commit")
    parser.add_argument("--expected-reviewed-path-fragment")
    parser.add_argument("--expected-task-id")
    parser.add_argument("--output-dir")
    args = parser.parse_args(argv)

    binding = LaunchBinding(
        approved_spec_path=args.approved_spec_path,
        implementation_dir=args.implementation_dir,
        implementation_manifest_path=args.implementation_manifest_path,
        independent_review_receipt_path=args.independent_review_receipt_path,
        launch_lock_path=args.launch_lock_path,
        expected_reviewed_commit=args.expected_reviewed_commit,
        expected_reviewed_path_fragment=args.expected_reviewed_path_fragment,
        expected_task_id=args.expected_task_id,
    )
    try:
        check_launch_admission(binding)
    except LaunchNotAuthorizedError as exc:
        print(str(exc))
        return 2

    # Admission passing is necessary but not sufficient for a real launch:
    # this task (maximum_runs: 0) never supplies a genuine launch lock to
    # this CLI itself, so this branch is reachable only by a later,
    # separately authorized scientific task. When reached, it would run the
    # REAL frozen panel (fixtures.iter_partition_specs()), never a toy one.
    if args.output_dir is None:
        print("Launch admission satisfied, but no --output-dir was supplied; nothing to do.")
        return 3
    # Wired end-to-end path: a genuinely admitted launch runs the REAL frozen
    # 272-partition panel (never a toy substitute) through the same pipeline
    # this task's own toy smoke test exercises below. TASK-20260913-c43d3e
    # never reaches this line: no launch lock exists for this task, and this
    # module is never invoked with a bundle that satisfies check_launch_admission.
    summary = run_scientific_pipeline(
        args.output_dir,
        list(fixtures.iter_partition_specs()),
        horizons=(0, 1, 2, 3),
        kernel_names=fixtures.KERNEL_ORDER,
        write_files=True,
        create_output_dir=False,
    )
    run_assumption_trap(args.output_dir, write_files=True)
    print(json.dumps({
        "partitions_processed": summary["partitions_processed"],
        "kernel_cells_processed": summary["kernel_cells_processed"],
        "transcript_checks_processed": summary["transcript_checks_processed"],
        "producer_reference_agreement": summary["producer_reference_agreement"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
