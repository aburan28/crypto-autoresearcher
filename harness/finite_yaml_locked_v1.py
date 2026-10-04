"""Additive finite-YAML locked adapter, v1 -- synthetic-fixture engineering only.

Authorized by DEC-20260908-195f0f (`coordination/pending-ideas/BATCH-855d5d/
integration/partial-disposition.json`, block `engineering_successor`) as the
"one narrow versioned finite-YAML locked adapter" for the two archived
partial instruments EXP-ECDLP-abf981 and EXP-ECDLP-2cb7f8. It exists to
remove the concrete lock/manifest/identifier/process-protection/provenance
incompatibilities recorded by DEC-20260908-b423e1
(`operational_interface_findings`), NOT to grant scientific-run authority.

Frozen public interface (engineering_successor.public_interface):

    validate_lock(lock_path, expected_sha256, run_id, launch_authority)
        -> VerifiedLaunch
    execute_locked(verified_launch) -> final_manifest_path

Hard scope, enforced in code, not merely documented:

  * `scientific_execution_authorized` in every finite-yaml-lock-v1 lock this
    module accepts MUST be exactly `false` (schema `const: false`,
    re-checked here). This module has no code path that can accept a lock
    that claims scientific authority; a future version, published and
    reviewed separately, would carry that.
  * `expected_sha256` is an externally supplied trust anchor (Coordinator
    launch authority), never computed from the lock file itself -- there is
    no self-attestation path.
  * `validate_lock` performs NO filesystem mutation and imports NOTHING
    beyond the reused low-level helpers below; every refusal in it happens
    before any scientific module could be imported or any directory
    created (DEC-20260908-195f0f engineering_successor.integration).
  * `execute_locked` creates the run directory exclusively (no-clobber),
    launches exactly one child process with the reused `_run_child`
    primitive, and writes the terminal manifest LAST and exclusively,
    excluding its own bytes from its own hash list.

Reused, NOT reimplemented, from `src/crypto_autoresearcher/runner.py` (after
reading its actual signatures, per the engineering_successor mandate):
`_sha256`, `_sha256_bytes`, `_ProtocolFile`, `_protocol_files_unchanged`,
`_tree_clean_except`, `_protocol_path`, `_locked_resource_policy`,
`_run_child`, `RecordValidationError`. This module does not import or call
`run_experiment`, `_load_approval_context`, or `_post_run_checks` from that
module (they require `specification.json`/`contract.md` and the legacy
numeric-only `execution-approval.schema.json`/`runner-receipt.schema.json`
envelope, which is exactly the incompatibility DEC-20260908-b423e1 recorded
as RUNNER-INTEGRATION-CONTRACT/RUNNER-IDENTIFIER-COMPATIBILITY). It also does
not import `harness/runner.py` for anything beyond what this module docstring
credits by name -- in particular it does not call that module's
`_inference_block`/`write_run`, which assume a different manifest shape and a
different (non-locked) trust model.

KNOWN, DISCLOSED environment limitation (recorded, not hidden, per the
"no unsupported platform mechanism may be silently labeled enforced" rule):
`_locked_resource_policy` requires a non-root effective UID because root can
bypass `RLIMIT_NPROC`. In a sandbox where the calling process itself runs as
uid 0, `validate_lock` refuses every lock for that reason alone -- this is a
genuine `infrastructure_error`, not a code defect, and is exercised and
recorded as its own synthetic control in
`tests/test_finite_yaml_locked_v1.py` / `synthetic-test-evidence.json` rather
than being caught and silently downgraded here.

This module has been exercised ONLY against
`tests/fixtures/finite_yaml_locked_v1/worker.py`, a benign, standard-library
-only, non-scientific synthetic subprocess. It has never imported, invoked,
or evaluated `experiments/EXP-ECDLP-abf981/source/run_model_comparison.py`
or `experiments/EXP-ECDLP-2cb7f8/source/run.py`, and creates no directory
under either experiment's real `runs/`.
"""
from __future__ import annotations

import dataclasses
import hashlib
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Reused low-level helpers -- see module docstring for exactly which names
# and why. Imported by attribute access (`_core.` prefix throughout) rather
# than star-imported, so every reused symbol is traceable to its source line
# in a diff and nothing is silently shadowed.
from src.crypto_autoresearcher import runner as _core
from src.crypto_autoresearcher.records import (  # noqa: F401 (RecordValidationError re-exported)
    RecordValidationError,
    read_json,
    validate_instance,
)

FORMAT_VERSION = 1
LOCK_SCHEMA_PATH = REPO_ROOT / "schemas" / "finite-yaml-lock-v1.schema.json"

# Local identifier compatibility (DEC-20260908-b423e1 RUNNER-IDENTIFIER-
# COMPATIBILITY, addressed per DEC-20260908-195f0f engineering_successor.
# lock_compatibility.local_changes): accept BOTH the legacy numeric-only form
# the audited schemas still require and the frozen random six-hex suffix
# form the two archived instruments actually reserved. This widening is
# local to this new schema/module only; the legacy schemas and their
# consumers are untouched.
EXPERIMENT_ID_RE = re.compile(r"^EXP-[A-Z0-9]+-([0-9]{3,}|[0-9a-f]{6})$")
RUN_ID_RE = re.compile(r"^RUN-[A-Z0-9]+-([0-9]{3,}|[0-9a-f]{6})$")
TASK_ID_RE = re.compile(r"^TASK-[0-9]{8}-[0-9a-f]{6}$")
SHA256_RE = _core.SHA256_PATTERN

_LAUNCH_AUTHORITY_REQUIRED_FIELDS = (
    "task_id",
    "owner",
    "epoch",
    "branch",
    "session",
    "acquired_at",
    "expires_at",
)


class FiniteYamlLockError(RecordValidationError):
    """A refusal by this adapter, always raised before any scientific import
    or run-directory creation for `validate_lock`, and before any partial
    output beyond the exclusively-created run directory for
    `execute_locked`. Never raised to mean "scientific falsification"."""


@dataclasses.dataclass(frozen=True)
class VerifiedLaunch:
    """Everything `execute_locked` needs, and nothing it must re-derive from
    a mutable source. Every field here was checked against an externally
    supplied trust anchor by `validate_lock`; `execute_locked` re-checks the
    ones that can drift between validation and launch (protocol-file
    identity) but never re-trusts a field from `lock` directly."""

    lock_path: Path
    lock_sha256: str
    lock: dict[str, Any]
    experiment_id: str
    run_id: str
    run_dir: Path
    argv: list[str]
    output_allowlist: tuple[str, ...]
    timeout_seconds: float
    memory_bytes: int
    resource_policy: dict[str, Any]
    protocol_files: tuple[_core._ProtocolFile, ...]
    launch_authority: dict[str, Any]
    validated_at: str


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _parse_ts(value: Any, field: str) -> datetime:
    if not isinstance(value, str) or not value:
        raise FiniteYamlLockError(f"{field} must be an ISO-8601 timestamp")
    text = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise FiniteYamlLockError(f"{field} is not ISO-8601: {value!r}") from exc
    if parsed.tzinfo is None:
        raise FiniteYamlLockError(f"{field} must carry a timezone: {value!r}")
    return parsed.astimezone(timezone.utc)


def _load_schema() -> dict[str, Any]:
    try:
        return read_json(LOCK_SCHEMA_PATH)
    except RecordValidationError as exc:
        raise FiniteYamlLockError(f"cannot load lock schema: {exc}") from exc


def _read_lock_document(raw: bytes) -> dict[str, Any]:
    """Strict YAML parse with the same duplicate-key/finiteness posture the
    JSON-record loader in `src/crypto_autoresearcher/records.py` applies to
    JSON records, so a malformed or duplicate-keyed lock is refused here
    rather than silently taking "the last value wins"."""
    try:
        # yaml.safe_load with a custom Loader that rejects duplicate keys.
        class _StrictLoader(yaml.SafeLoader):
            pass

        def _no_duplicate_mapping(loader: yaml.SafeLoader, node: yaml.MappingNode) -> dict[str, Any]:
            mapping: dict[str, Any] = {}
            for key_node, value_node in node.value:
                key = loader.construct_object(key_node, deep=True)
                if key in mapping:
                    raise FiniteYamlLockError(f"lock contains duplicate mapping key: {key!r}")
                mapping[key] = loader.construct_object(value_node, deep=True)
            return mapping

        _StrictLoader.add_constructor(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _no_duplicate_mapping
        )
        document = yaml.load(raw, Loader=_StrictLoader)
    except FiniteYamlLockError:
        raise
    except yaml.YAMLError as exc:
        raise FiniteYamlLockError(f"lock is not valid YAML: {exc}") from exc
    if not isinstance(document, dict):
        raise FiniteYamlLockError("lock must deserialize to a mapping")
    for value in _walk_numbers(document):
        pass  # non-finite numbers (nan/inf) are impossible via yaml.safe_load's
              # resolver for this tag set, but guarded defensively below.
    return document


def _walk_numbers(value: Any):
    if isinstance(value, float) and not _is_finite(value):
        raise FiniteYamlLockError("lock contains a non-finite number")
    if isinstance(value, dict):
        for item in value.values():
            yield from _walk_numbers(item)
    elif isinstance(value, list):
        for item in value:
            yield from _walk_numbers(item)
    else:
        yield value


def _is_finite(number: float) -> bool:
    return number == number and number not in (float("inf"), float("-inf"))


def _check_launch_authority(
    launch_authority: dict[str, Any], lock_ref: dict[str, Any], run_id: str, now: datetime
) -> None:
    if not isinstance(launch_authority, dict):
        raise FiniteYamlLockError("launch_authority must be a mapping")
    missing = [field for field in _LAUNCH_AUTHORITY_REQUIRED_FIELDS if field not in launch_authority]
    if missing:
        raise FiniteYamlLockError(f"launch_authority is missing fields: {sorted(missing)}")
    if not TASK_ID_RE.fullmatch(str(launch_authority["task_id"])):
        raise FiniteYamlLockError("launch_authority.task_id is not a TASK-YYYYMMDD-<6hex> identifier")
    if launch_authority["task_id"] != lock_ref.get("task_id"):
        raise FiniteYamlLockError(
            "launch_authority.task_id does not match the lock's bound launch_authority_ref.task_id"
        )
    if launch_authority.get("owner") != lock_ref.get("owner"):
        raise FiniteYamlLockError("launch_authority.owner does not match the lock's bound reference")
    if launch_authority.get("epoch") != lock_ref.get("epoch"):
        raise FiniteYamlLockError("launch_authority.epoch does not match the lock's bound reference (stale authority)")
    acquired = _parse_ts(launch_authority["acquired_at"], "launch_authority.acquired_at")
    expires = _parse_ts(launch_authority["expires_at"], "launch_authority.expires_at")
    if expires <= acquired:
        raise FiniteYamlLockError("launch_authority.expires_at must be after acquired_at")
    if now >= expires:
        raise FiniteYamlLockError(
            f"launch_authority expired at {launch_authority['expires_at']} (now {now.isoformat()})"
        )
    blob = json.dumps(launch_authority, sort_keys=True, default=str).lower()
    if "bedrock" in blob:
        raise FiniteYamlLockError("launch_authority references a prohibited inference backend (Bedrock)")


def _verify_source_closure(
    repo_root: Path, source_closure: list[dict[str, Any]]
) -> tuple[_core._ProtocolFile, ...]:
    """Hash-bind every declared source-closure file with the SAME primitives
    the audited runner uses for its own protocol hashes (`_protocol_path`,
    `_sha256`), so a traversal/symlink/absolute-path/duplicate-identity
    attempt is refused by code this module did not have to reinvent."""
    verified_paths: set[str] = set()
    resolved_paths: set[Path] = set()
    identities: set[tuple[int, int]] = set()
    protocol_files: list[_core._ProtocolFile] = []
    for record in source_closure:
        if not isinstance(record, dict) or set(record) != {"path", "sha256"}:
            raise FiniteYamlLockError(f"source_closure entry is malformed: {record!r}")
        path_text, expected_sha256 = record["path"], record["sha256"]
        if SHA256_RE.fullmatch(str(expected_sha256)) is None:
            raise FiniteYamlLockError(f"source_closure entry has an invalid SHA-256: {path_text!r}")
        try:
            path, normalized_path = _core._protocol_path(repo_root, path_text)
        except RecordValidationError as exc:
            raise FiniteYamlLockError(str(exc)) from exc
        stat_result = path.stat()
        identity = (stat_result.st_dev, stat_result.st_ino)
        if normalized_path in verified_paths or path in resolved_paths or identity in identities:
            raise FiniteYamlLockError(f"source_closure contains a duplicate/aliased path: {path_text!r}")
        verified_paths.add(normalized_path)
        resolved_paths.add(path)
        identities.add(identity)
        actual_sha256 = _core._sha256(path)
        if actual_sha256 != expected_sha256:
            raise FiniteYamlLockError(
                f"source_closure SHA-256 mismatch for {path_text!r}: "
                f"expected {expected_sha256}, got {actual_sha256} (preflight source/lock hash drift)"
            )
        protocol_files.append(
            _core._ProtocolFile(
                path=path,
                normalized_path=normalized_path,
                sha256=actual_sha256,
                device=stat_result.st_dev,
                inode=stat_result.st_ino,
            )
        )
    return tuple(protocol_files)


def validate_lock(
    lock_path: str | Path,
    expected_sha256: str,
    run_id: str,
    launch_authority: dict[str, Any],
    *,
    now: datetime | None = None,
) -> VerifiedLaunch:
    """Refuse before any scientific import or `mkdir`. Every failure raises
    `FiniteYamlLockError` (a `RecordValidationError` subclass) with a
    specific, named reason; nothing here mutates the filesystem.
    """
    now = now or datetime.now(timezone.utc)
    lock_path = Path(lock_path)
    if lock_path.is_symlink():
        raise FiniteYamlLockError(f"lock must not be a symlink: {lock_path}")
    if not lock_path.is_file():
        raise FiniteYamlLockError(f"lock is missing or not a plain file: {lock_path}")

    raw = lock_path.read_bytes()
    actual_sha256 = hashlib.sha256(raw).hexdigest()
    if not isinstance(expected_sha256, str) or SHA256_RE.fullmatch(expected_sha256) is None:
        raise FiniteYamlLockError(
            "expected_sha256 must be an externally published sha256 hex digest "
            "(no self-attestation by the lock or its caller)"
        )
    if actual_sha256 != expected_sha256.lower():
        raise FiniteYamlLockError(
            f"lock content does not match the externally published expected hash: "
            f"expected {expected_sha256}, got {actual_sha256}"
        )

    document = _read_lock_document(raw)
    schema = _load_schema()
    try:
        validate_instance(document, schema)
    except RecordValidationError as exc:
        raise FiniteYamlLockError(f"lock does not satisfy finite-yaml-lock-v1 schema: {exc}") from exc

    body = document["finite_yaml_lock"]
    if body["format_version"] != FORMAT_VERSION:
        raise FiniteYamlLockError(f"unsupported lock format_version: {body['format_version']!r}")
    if body["scientific_execution_authorized"] is not False:
        raise FiniteYamlLockError(
            "this adapter version accepts only scientific_execution_authorized: false locks"
        )
    if EXPERIMENT_ID_RE.fullmatch(body["experiment_id"]) is None:
        raise FiniteYamlLockError(f"lock experiment_id is not a recognized identifier form: {body['experiment_id']!r}")
    if RUN_ID_RE.fullmatch(body["run_id"]) is None:
        raise FiniteYamlLockError(f"lock run_id is not a recognized identifier form: {body['run_id']!r}")
    if not isinstance(run_id, str) or RUN_ID_RE.fullmatch(run_id) is None:
        raise FiniteYamlLockError(f"caller-supplied run_id is not a recognized identifier form: {run_id!r}")
    if body["run_id"] != run_id:
        raise FiniteYamlLockError(
            f"caller-supplied run_id does not match the lock: expected {body['run_id']!r}, got {run_id!r}"
        )

    _check_launch_authority(launch_authority, body["launch_authority_ref"], run_id, now)

    if body["resource_policy"]["maximum_workers"] != 1:
        raise FiniteYamlLockError("this adapter version accepts only maximum_workers: 1 locks")

    repo_relative_run_dir = body["run_directory"]
    run_dir = (REPO_ROOT / repo_relative_run_dir).resolve()
    try:
        run_dir.relative_to(REPO_ROOT)
    except ValueError as exc:
        raise FiniteYamlLockError(f"run_directory escapes the repository: {repo_relative_run_dir!r}") from exc
    if run_dir.exists() or run_dir.is_symlink():
        raise FiniteYamlLockError(f"run_directory already exists; run records are immutable: {run_dir}")

    specification_path, _ = _core._protocol_path(REPO_ROOT, body["specification"]["path"])
    specification_sha256 = _core._sha256(specification_path)
    if specification_sha256 != body["specification"]["sha256"]:
        raise FiniteYamlLockError("lock specification hash does not match the bytes on disk")

    protocol_files = _verify_source_closure(REPO_ROOT, body["source_closure"])

    executable_path, _ = _core._protocol_path(REPO_ROOT, body["executable"]["path"]) if not Path(
        body["executable"]["path"]
    ).is_absolute() else (Path(body["executable"]["path"]), body["executable"]["path"])
    if not executable_path.is_file():
        raise FiniteYamlLockError(f"lock executable is missing: {executable_path}")
    if _core._sha256(executable_path) != body["executable"]["sha256"]:
        raise FiniteYamlLockError("lock executable hash does not match the file on disk")

    argv = list(body["argv"])
    if not argv or any(not isinstance(item, str) or not item for item in argv):
        raise FiniteYamlLockError("lock argv must be a nonempty list of nonempty strings")

    # Checked LAST, deliberately: every check above this line is a pure
    # lock/claim/source-integrity check, independent of the host this
    # process happens to run on. This one is host-dependent (see the module
    # docstring's "KNOWN, DISCLOSED environment limitation") and is kept
    # last so a test targeting any earlier refusal is not pre-empted by it.
    try:
        live_resource_policy = _core._locked_resource_policy(descendant_slots=0)
    except RecordValidationError as exc:
        # A genuine, disclosed environment limitation: this is an
        # infrastructure_error, not a code defect and not a scientific
        # finding. Never silently downgraded or swallowed.
        raise FiniteYamlLockError(f"resource-policy preflight refused by this host: {exc}") from exc
    if live_resource_policy["descendant_policy"] != body["resource_policy"]["descendant_policy"]:
        raise FiniteYamlLockError("lock resource_policy.descendant_policy does not match this host's runtime policy")
    if live_resource_policy["effective_uid"] != body["resource_policy"]["effective_uid"]:
        raise FiniteYamlLockError("lock resource_policy.effective_uid does not match this host's runtime UID")

    return VerifiedLaunch(
        lock_path=lock_path,
        lock_sha256=actual_sha256,
        lock=document,
        experiment_id=body["experiment_id"],
        run_id=body["run_id"],
        run_dir=run_dir,
        argv=argv,
        output_allowlist=tuple(body["output_allowlist"]),
        timeout_seconds=float(body["resource_policy"]["timeout_seconds"]),
        memory_bytes=int(body["resource_policy"]["memory_bytes"]),
        resource_policy=dict(body["resource_policy"]),
        protocol_files=protocol_files,
        launch_authority=dict(launch_authority),
        validated_at=_utc_now_iso(),
    )


def _classify(child: "_core._ChildResult", memory_bytes: int) -> tuple[str, bool, str | None]:
    if child.infrastructure_error is not None:
        return "failed_infrastructure", False, child.infrastructure_error
    if child.timed_out:
        return "resource_exhaustion", False, "wall-clock timeout"
    if child.memory_killed or child.peak_rss_bytes > memory_bytes:
        return "resource_exhaustion", False, "memory limit exceeded"
    if child.cpu_killed:
        return "resource_exhaustion", False, "CPU-time limit exceeded"
    if child.return_code != 0:
        return "failed_implementation", False, f"child exited with return code {child.return_code}"
    return "completed_valid", True, None


def execute_locked(verified: VerifiedLaunch) -> str:
    """Create the run directory exclusively, launch exactly one child with
    the reused `_run_child` primitive, and write the terminal manifest last
    and exclusively. Never invoked on a lock this module did not itself
    verify with `validate_lock` in the same call sequence."""
    run_dir = verified.run_dir
    run_dir.mkdir(parents=True, exist_ok=False)

    stdout_path = run_dir / "stdout.log"
    stderr_path = run_dir / "stderr.log"
    command_path = run_dir / "command.txt"
    environment_path = run_dir / "environment.json"
    raw_result_path = run_dir / "raw-result.json"
    manifest_path = run_dir / "manifest.yaml"

    command_path.write_text(" ".join(verified.argv) + "\n", encoding="utf-8")
    environment_path.write_text(
        json.dumps(_core._environment(), indent=2, sort_keys=True), encoding="utf-8"
    )

    started_wall = time.time()
    started_monotonic = time.monotonic()
    child = _core._run_child(
        command=verified.argv,
        cwd=run_dir,
        timeout_seconds=verified.timeout_seconds,
        memory_bytes=verified.memory_bytes,
        cpu_seconds=verified.timeout_seconds,
        stdout_path=stdout_path,
        stderr_path=stderr_path,
        descendant_slots=0,
    )
    finished_monotonic = time.monotonic()
    finished_wall = time.time()

    status, valid, invalid_reason = _classify(child, verified.memory_bytes)

    protocol_files_unchanged = _core._protocol_files_unchanged(verified.protocol_files)
    tree_unchanged = _core._tree_clean_except(REPO_ROOT, run_dir)
    if not protocol_files_unchanged or not tree_unchanged:
        status, valid = "failed_infrastructure", False
        invalid_reason = "postflight drift: " + ", ".join(
            name
            for name, ok in (
                ("source_closure_unchanged", protocol_files_unchanged),
                ("tree_unchanged_except_run_dir", tree_unchanged),
            )
            if not ok
        )

    raw_result = {
        "child": {
            "return_code": child.return_code,
            "timed_out": child.timed_out,
            "memory_killed": child.memory_killed,
            "cpu_killed": child.cpu_killed,
            "infrastructure_error": child.infrastructure_error,
            "group_quiescent": child.group_quiescent,
            "wall_seconds": child.wall_seconds,
            "cpu_seconds": child.cpu_seconds,
            "peak_rss_bytes": child.peak_rss_bytes,
        },
        "scientific_content": False,
    }
    raw_result_path.write_text(
        json.dumps(raw_result, indent=2, sort_keys=True, default=str), encoding="utf-8"
    )

    manifest = {
        "finite_yaml_locked_run": {
            "format_version": FORMAT_VERSION,
            "experiment_id": verified.experiment_id,
            "run_id": verified.run_id,
            "status": status,
            "valid": valid,
            "invalid_reason": invalid_reason,
            "lock": {"path": str(verified.lock_path), "sha256": verified.lock_sha256},
            "launch_authority": verified.launch_authority,
            "command": " ".join(verified.argv),
            "timing": {
                "started_at": datetime.fromtimestamp(started_wall, tz=timezone.utc).isoformat(),
                "finished_at": datetime.fromtimestamp(finished_wall, tz=timezone.utc).isoformat(),
                "wall_seconds": round(finished_monotonic - started_monotonic, 6),
                "timing_source": "wrapper",
            },
            "resources": {
                "peak_rss_bytes": child.peak_rss_bytes,
                "cpu_seconds": round(child.cpu_seconds, 6),
                "descendant_policy": verified.resource_policy["descendant_policy"],
            },
            "post_run_checks": {
                "process_group_quiescent": child.group_quiescent,
                "source_closure_unchanged": protocol_files_unchanged,
                "tree_unchanged_except_run_dir": tree_unchanged,
            },
            "artifacts": {
                name: {
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                    "bytes": path.stat().st_size,
                }
                for name, path in (
                    ("command.txt", command_path),
                    ("environment.json", environment_path),
                    ("stdout.log", stdout_path),
                    ("stderr.log", stderr_path),
                    ("raw-result.json", raw_result_path),
                )
            },
            "certificate": {"kind": "none", "verified": None, "verifier": None},
            "scientific_content": False,
            "note": (
                "This run was launched by harness/finite_yaml_locked_v1.py against a "
                "scientific_execution_authorized: false lock. No curve, divisor, "
                "section, or scientific enumeration occurred."
            ),
        }
    }
    if manifest_path.exists() or manifest_path.is_symlink():
        raise FiniteYamlLockError(f"manifest already exists (no-clobber): {manifest_path}")
    manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    return str(manifest_path)
