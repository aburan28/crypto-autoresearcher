"""Synthetic-fixture tests for harness/finite_yaml_locked_v1.py.

Authorized by DEC-20260908-195f0f (`coordination/pending-ideas/BATCH-855d5d/
integration/partial-disposition.json`). Every lock instance built in this
file is a disposable, clearly-labeled SYNTHETIC fixture: no test in this
file imports, invokes, or evaluates
`experiments/EXP-ECDLP-abf981/source/run_model_comparison.py` or
`experiments/EXP-ECDLP-2cb7f8/source/run.py`, and no test creates a
directory under either experiment's real `runs/`. `TASK_ID` below is a
syntactically valid but never-registered identifier used only to exercise
`launch_authority` matching logic; it names no real ledger or coordination
record.

Two properties of this specific execution environment are load-bearing for
how these tests are organized (both disclosed in
`harness/finite_yaml_locked_v1.py`'s own module docstring and in this task's
`implementation-report.json`, never hidden):

1. This sandbox runs the calling process as uid 0 (root).
   `src.crypto_autoresearcher.runner._locked_resource_policy` refuses root by
   design (root can bypass `RLIMIT_NPROC`), so `validate_lock` on an
   otherwise-fully-valid lock refuses at its LAST check, every time, in this
   environment. Tests that need to reach a SPECIFIC earlier refusal are
   ordered so that refusal fires before the root check is reached (see
   `harness/finite_yaml_locked_v1.py`'s own comment on why the resource
   check is last); `test_validate_lock_otherwise_valid_lock_refuses_on_root`
   demonstrates the terminal, otherwise-clean case explicitly.
2. Because `validate_lock` cannot return a `VerifiedLaunch` in this
   environment, `execute_locked` is exercised directly against a
   `VerifiedLaunch` assembled by REPLICATING validate_lock's own successful
   verification steps (hash-checking the same real repository files
   `validate_lock` would have hash-checked) -- the same "test seam for
   logic-level coverage only" pattern `harness/runner.py`'s
   `_verify_md5_collision_pair(cert, impls=...)` already uses in this
   repository. `execute_locked` itself never calls `_locked_resource_policy`,
   so this is a faithful exercise of its actual code, not a stub.
"""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from harness import finite_yaml_locked_v1 as fyl  # noqa: E402
from src.crypto_autoresearcher import runner as core_runner  # noqa: E402

WORKER = REPO_ROOT / "tests" / "fixtures" / "finite_yaml_locked_v1" / "worker.py"
ADAPTER_SOURCE = REPO_ROOT / "harness" / "finite_yaml_locked_v1.py"
# A stand-in "specification" for lock-shape testing only: an arbitrary,
# stable, already-tracked repository file. Deliberately NOT
# experiments/EXP-ECDLP-*/specification.yaml, so nothing in this file can be
# mistaken for exercising either real frozen experiment specification.
SYNTHETIC_SPEC_PATH = "schemas/finite-yaml-lock-v1.schema.json"

SCRATCH_ROOT = Path(
    "coordination/pending-ideas/BATCH-855d5d/integration/tasks/"
    "TASK-20260908-1a8f4c/scratch/synthetic-runs"
)

TASK_ID = "TASK-20260908-abcdef"  # syntactically valid, never a real record
OWNER = "executor-finite-yaml-lock-v1-tests"


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _base_document(run_dir_name: str, *, now: datetime | None = None) -> dict:
    now = now or datetime.now(timezone.utc)
    acquired = now - timedelta(minutes=5)
    expires = now + timedelta(hours=1)
    return {
        "finite_yaml_lock": {
            "format_version": 1,
            "experiment_id": "EXP-ECDLP-2cb7f8",
            "run_id": "RUN-ECDLP-3c6277",
            "specification": {
                "path": SYNTHETIC_SPEC_PATH,
                "sha256": _sha256_path(REPO_ROOT / SYNTHETIC_SPEC_PATH),
            },
            "metric_interpretation_ref": {
                "decision_id": "DEC-20260908-195f0f",
                "path": "coordination/pending-ideas/BATCH-855d5d/integration/partial-disposition.json",
                "sha256": _sha256_path(
                    REPO_ROOT
                    / "coordination/pending-ideas/BATCH-855d5d/integration/partial-disposition.json"
                ),
            },
            "run_directory": str(SCRATCH_ROOT / run_dir_name),
            "argv": [sys.executable, str(WORKER), "success"],
            "output_allowlist": [
                "command.txt",
                "environment.json",
                "stdout.log",
                "stderr.log",
                "raw-result.json",
                "manifest.yaml",
            ],
            "source_closure": [
                {"path": "harness/finite_yaml_locked_v1.py", "sha256": _sha256_path(ADAPTER_SOURCE)},
                {
                    "path": "tests/fixtures/finite_yaml_locked_v1/worker.py",
                    "sha256": _sha256_path(WORKER),
                },
            ],
            "executable": {
                "path": sys.executable,
                "sha256": _sha256_path(Path(sys.executable)),
                "version": sys.version,
            },
            "environment_allowlist": ["PATH"],
            "resource_policy": {
                "descendant_policy": "forbidden-via-rlimit-nproc-zero",
                "effective_uid": max(1, os.geteuid()),
                "memory_bytes": 256 * 1024 * 1024,
                "timeout_seconds": 5.0,
                "maximum_workers": 1,
            },
            "launch_authority_ref": {
                "task_id": TASK_ID,
                "owner": OWNER,
                "epoch": 1,
                "branch": "test-branch",
                "session": "test-session",
                "acquired_at": _iso(acquired),
                "expires_at": _iso(expires),
            },
            "native_launch_receipt": {
                "requested_policy": "executor-implementation",
                "resolved_model_id": None,
                "provider": None,
                "reasoning_effort": None,
                "session_id": "test-session",
                "model_verified": False,
                "adapter_probe_performed": False,
                "fallback_used": False,
                "degraded_allowed": False,
            },
            "scientific_execution_authorized": False,
            "created_at": _iso(now),
        }
    }


def _launch_authority(document: dict, *, now: datetime | None = None) -> dict:
    ref = document["finite_yaml_lock"]["launch_authority_ref"]
    return dict(ref)


def _write_lock(tmp_path: Path, document: dict, name: str = "lock.yaml") -> tuple[Path, str]:
    raw = yaml.safe_dump(document, sort_keys=False).encode("utf-8")
    path = tmp_path / name
    path.write_bytes(raw)
    return path, hashlib.sha256(raw).hexdigest()


def _run_id(document: dict) -> str:
    return document["finite_yaml_lock"]["run_id"]


# ---------------------------------------------------------------------------
# validate_lock: refusals that fire BEFORE the host-dependent resource check
# ---------------------------------------------------------------------------


def test_missing_lock_refuses(tmp_path):
    missing = tmp_path / "does-not-exist.yaml"
    with pytest.raises(fyl.FiniteYamlLockError, match="missing or not a plain file"):
        fyl.validate_lock(missing, "0" * 64, "RUN-ECDLP-3c6277", {})


def test_symlink_lock_refuses(tmp_path):
    doc = _base_document("symlink-case")
    real_path, digest = _write_lock(tmp_path, doc, name="real-lock.yaml")
    link_path = tmp_path / "lock.yaml"
    link_path.symlink_to(real_path)
    with pytest.raises(fyl.FiniteYamlLockError, match="must not be a symlink"):
        fyl.validate_lock(link_path, digest, _run_id(doc), _launch_authority(doc))


def test_wrong_published_expected_hash_refuses_no_self_attestation(tmp_path):
    doc = _base_document("wrong-hash-case")
    path, digest = _write_lock(tmp_path, doc)
    wrong = ("0" if digest[0] != "0" else "1") + digest[1:]
    with pytest.raises(fyl.FiniteYamlLockError, match="does not match the externally published"):
        fyl.validate_lock(path, wrong, _run_id(doc), _launch_authority(doc))


def test_malformed_expected_sha256_refuses(tmp_path):
    doc = _base_document("malformed-hash-case")
    path, _digest = _write_lock(tmp_path, doc)
    with pytest.raises(fyl.FiniteYamlLockError, match="externally published sha256 hex digest"):
        fyl.validate_lock(path, "not-a-hash", _run_id(doc), _launch_authority(doc))


def test_duplicate_yaml_keys_refuse(tmp_path):
    raw = (
        b"finite_yaml_lock:\n"
        b"  format_version: 1\n"
        b"  format_version: 1\n"
    )
    path = tmp_path / "lock.yaml"
    path.write_bytes(raw)
    digest = hashlib.sha256(raw).hexdigest()
    with pytest.raises(fyl.FiniteYamlLockError, match="duplicate mapping key"):
        fyl.validate_lock(path, digest, "RUN-ECDLP-3c6277", {})


def test_nonfinite_number_refuses(tmp_path):
    doc = _base_document("nonfinite-case")
    doc["finite_yaml_lock"]["resource_policy"]["timeout_seconds"] = float("nan")
    raw = yaml.safe_dump(doc, sort_keys=False).encode("utf-8")
    assert ".nan" in raw.decode("utf-8")
    path = tmp_path / "lock.yaml"
    path.write_bytes(raw)
    digest = hashlib.sha256(raw).hexdigest()
    with pytest.raises(fyl.FiniteYamlLockError, match="non-finite number"):
        fyl.validate_lock(path, digest, _run_id(doc), _launch_authority(doc))


def test_schema_violation_missing_field_refuses(tmp_path):
    doc = _base_document("missing-field-case")
    del doc["finite_yaml_lock"]["executable"]
    path, digest = _write_lock(tmp_path, doc)
    with pytest.raises(fyl.FiniteYamlLockError, match="does not satisfy finite-yaml-lock-v1 schema"):
        fyl.validate_lock(path, digest, _run_id(doc), _launch_authority(doc))


def test_schema_rejects_unknown_key(tmp_path):
    doc = _base_document("unknown-key-case")
    doc["finite_yaml_lock"]["unexpected_field"] = "nope"
    path, digest = _write_lock(tmp_path, doc)
    with pytest.raises(fyl.FiniteYamlLockError, match="does not satisfy finite-yaml-lock-v1 schema"):
        fyl.validate_lock(path, digest, _run_id(doc), _launch_authority(doc))


def test_wrong_format_version_refuses(tmp_path):
    doc = _base_document("format-version-case")
    doc["finite_yaml_lock"]["format_version"] = 2
    path, digest = _write_lock(tmp_path, doc)
    with pytest.raises(fyl.FiniteYamlLockError, match="does not satisfy finite-yaml-lock-v1 schema"):
        fyl.validate_lock(path, digest, _run_id(doc), _launch_authority(doc))


def test_scientific_execution_authorized_true_refuses(tmp_path):
    doc = _base_document("sci-auth-case")
    doc["finite_yaml_lock"]["scientific_execution_authorized"] = True
    path, digest = _write_lock(tmp_path, doc)
    with pytest.raises(fyl.FiniteYamlLockError, match="does not satisfy finite-yaml-lock-v1 schema"):
        fyl.validate_lock(path, digest, _run_id(doc), _launch_authority(doc))


def test_run_id_mismatch_refuses_wrong_cell(tmp_path):
    doc = _base_document("run-id-mismatch-case")
    path, digest = _write_lock(tmp_path, doc)
    with pytest.raises(fyl.FiniteYamlLockError, match="does not match the lock"):
        fyl.validate_lock(path, digest, "RUN-ECDLP-413b2a", _launch_authority(doc))


def test_unrecognized_run_id_form_refuses(tmp_path):
    doc = _base_document("bad-run-id-form-case")
    path, digest = _write_lock(tmp_path, doc)
    with pytest.raises(fyl.FiniteYamlLockError, match="not a recognized identifier form"):
        fyl.validate_lock(path, digest, "RUN-ECDLP-not-an-id!", _launch_authority(doc))


def test_launch_authority_missing_fields_refuses(tmp_path):
    doc = _base_document("missing-authority-case")
    path, digest = _write_lock(tmp_path, doc)
    authority = _launch_authority(doc)
    del authority["epoch"]
    with pytest.raises(fyl.FiniteYamlLockError, match="missing fields"):
        fyl.validate_lock(path, digest, _run_id(doc), authority)


def test_launch_authority_unauthorized_task_refuses(tmp_path):
    doc = _base_document("unauthorized-task-case")
    path, digest = _write_lock(tmp_path, doc)
    authority = _launch_authority(doc)
    authority["task_id"] = "TASK-20260908-111111"
    with pytest.raises(fyl.FiniteYamlLockError, match="does not match the lock's bound launch_authority_ref"):
        fyl.validate_lock(path, digest, _run_id(doc), authority)


def test_launch_authority_stale_epoch_refuses(tmp_path):
    doc = _base_document("stale-epoch-case")
    path, digest = _write_lock(tmp_path, doc)
    authority = _launch_authority(doc)
    authority["epoch"] = 2
    with pytest.raises(fyl.FiniteYamlLockError, match="stale authority"):
        fyl.validate_lock(path, digest, _run_id(doc), authority)


def test_launch_authority_expired_refuses(tmp_path):
    now = datetime.now(timezone.utc)
    doc = _base_document("expired-case", now=now - timedelta(hours=2))
    path, digest = _write_lock(tmp_path, doc)
    with pytest.raises(fyl.FiniteYamlLockError, match="expired"):
        fyl.validate_lock(path, digest, _run_id(doc), _launch_authority(doc), now=now)


def test_launch_authority_bedrock_refuses(tmp_path):
    doc = _base_document("bedrock-case")
    path, digest = _write_lock(tmp_path, doc)
    authority = _launch_authority(doc)
    authority["session"] = "session-via-amazon-bedrock"
    with pytest.raises(fyl.FiniteYamlLockError, match="Bedrock"):
        fyl.validate_lock(path, digest, _run_id(doc), authority)


def test_maximum_workers_not_one_refuses(tmp_path):
    doc = _base_document("workers-case")
    doc["finite_yaml_lock"]["resource_policy"]["maximum_workers"] = 1
    # Schema pins maximum_workers to const 1, so exercise the adapter's own
    # redundant defense-in-depth check by tampering with the schema's own
    # const in a scoped copy is not possible without editing the shared
    # schema file; instead confirm the schema itself refuses any other value.
    doc["finite_yaml_lock"]["resource_policy"]["maximum_workers"] = 2
    path, digest = _write_lock(tmp_path, doc)
    with pytest.raises(fyl.FiniteYamlLockError, match="does not satisfy finite-yaml-lock-v1 schema"):
        fyl.validate_lock(path, digest, _run_id(doc), _launch_authority(doc))


def test_run_directory_escape_refuses(tmp_path):
    doc = _base_document("escape-case")
    doc["finite_yaml_lock"]["run_directory"] = "../outside-the-repository"
    path, digest = _write_lock(tmp_path, doc)
    with pytest.raises(fyl.FiniteYamlLockError, match="escapes the repository"):
        fyl.validate_lock(path, digest, _run_id(doc), _launch_authority(doc))


def test_run_directory_already_exists_refuses_no_clobber(tmp_path):
    doc = _base_document("noclobber-case")
    # "schemas" always exists in this repository and is never mutated here;
    # used purely as an existing-directory fixture for the no-clobber check.
    doc["finite_yaml_lock"]["run_directory"] = "schemas"
    path, digest = _write_lock(tmp_path, doc)
    with pytest.raises(fyl.FiniteYamlLockError, match="run records are immutable"):
        fyl.validate_lock(path, digest, _run_id(doc), _launch_authority(doc))


def test_specification_hash_drift_refuses(tmp_path):
    doc = _base_document("spec-drift-case")
    doc["finite_yaml_lock"]["specification"]["sha256"] = "0" * 64
    path, digest = _write_lock(tmp_path, doc)
    with pytest.raises(fyl.FiniteYamlLockError, match="specification hash does not match"):
        fyl.validate_lock(path, digest, _run_id(doc), _launch_authority(doc))


def test_source_closure_missing_file_refuses(tmp_path):
    doc = _base_document("missing-source-case")
    doc["finite_yaml_lock"]["source_closure"].append(
        {"path": "harness/does-not-exist-anywhere.py", "sha256": "0" * 64}
    )
    path, digest = _write_lock(tmp_path, doc)
    with pytest.raises(fyl.FiniteYamlLockError):
        fyl.validate_lock(path, digest, _run_id(doc), _launch_authority(doc))


def test_source_closure_traversal_refuses(tmp_path):
    doc = _base_document("traversal-case")
    doc["finite_yaml_lock"]["source_closure"].append(
        {"path": "../etc/passwd", "sha256": "0" * 64}
    )
    path, digest = _write_lock(tmp_path, doc)
    with pytest.raises(fyl.FiniteYamlLockError):
        fyl.validate_lock(path, digest, _run_id(doc), _launch_authority(doc))


def test_source_closure_duplicate_path_refuses(tmp_path):
    doc = _base_document("dup-source-case")
    doc["finite_yaml_lock"]["source_closure"].append(
        dict(doc["finite_yaml_lock"]["source_closure"][0])
    )
    path, digest = _write_lock(tmp_path, doc)
    with pytest.raises(fyl.FiniteYamlLockError, match="duplicate/aliased path"):
        fyl.validate_lock(path, digest, _run_id(doc), _launch_authority(doc))


def test_source_closure_hash_drift_refuses(tmp_path):
    doc = _base_document("source-drift-case")
    doc["finite_yaml_lock"]["source_closure"][0]["sha256"] = "0" * 64
    path, digest = _write_lock(tmp_path, doc)
    with pytest.raises(fyl.FiniteYamlLockError, match="hash drift"):
        fyl.validate_lock(path, digest, _run_id(doc), _launch_authority(doc))


def test_executable_hash_mismatch_refuses(tmp_path):
    doc = _base_document("executable-drift-case")
    doc["finite_yaml_lock"]["executable"]["sha256"] = "0" * 64
    path, digest = _write_lock(tmp_path, doc)
    with pytest.raises(fyl.FiniteYamlLockError, match="executable hash does not match"):
        fyl.validate_lock(path, digest, _run_id(doc), _launch_authority(doc))


def test_argv_empty_refuses(tmp_path):
    doc = _base_document("empty-argv-case")
    doc["finite_yaml_lock"]["argv"] = []
    path, digest = _write_lock(tmp_path, doc)
    with pytest.raises(fyl.FiniteYamlLockError, match="does not satisfy finite-yaml-lock-v1 schema"):
        fyl.validate_lock(path, digest, _run_id(doc), _launch_authority(doc))


# ---------------------------------------------------------------------------
# validate_lock: the terminal, host-dependent resource-policy check
# ---------------------------------------------------------------------------


def test_validate_lock_observes_host_resource_policy(tmp_path):
    """An otherwise valid lock is refused only on a root-hosted runner.

    The resource-policy gate is intentionally host-dependent: root can bypass
    the process-count limit, whereas an unprivileged CI worker can enforce it.
    Exercise the real validation path in either environment instead of making
    the suite depend on the developer sandbox's effective UID.
    """
    doc = _base_document("terminal-valid-case")
    path, digest = _write_lock(tmp_path, doc)
    if os.geteuid() == 0:
        with pytest.raises(fyl.FiniteYamlLockError, match="resource-policy preflight refused by this host"):
            fyl.validate_lock(path, digest, _run_id(doc), _launch_authority(doc))
    else:
        verified = fyl.validate_lock(path, digest, _run_id(doc), _launch_authority(doc))
        assert verified.run_id == _run_id(doc)


# ---------------------------------------------------------------------------
# The reused _run_child primitive: actual benign synthetic child success,
# failure, crash, and bounded timeout (uid-independent -- see file docstring
# point 2 for why this is tested directly rather than only through
# execute_locked in this sandbox).
# ---------------------------------------------------------------------------


def _run_worker(tmp_path, mode, *, timeout=5.0, memory_bytes=256 * 1024 * 1024, cpu_seconds=5.0):
    stdout_path = tmp_path / "stdout.log"
    stderr_path = tmp_path / "stderr.log"
    return core_runner._run_child(
        command=[sys.executable, str(WORKER), mode],
        cwd=tmp_path,
        timeout_seconds=timeout,
        memory_bytes=memory_bytes,
        cpu_seconds=cpu_seconds,
        stdout_path=stdout_path,
        stderr_path=stderr_path,
        descendant_slots=0,
    )


def test_run_child_benign_success(tmp_path):
    child = _run_worker(tmp_path, "success")
    assert child.return_code == 0
    assert child.infrastructure_error is None
    assert not child.timed_out
    payload = json.loads(child.stdout)
    assert payload == {
        "status": "ok",
        "synthetic": True,
        "kind": "benign_fixture",
        "scientific_content": False,
        "note": "no curve, divisor, section, or scientific enumeration occurred",
    }
    status, valid, reason = fyl._classify(child, 256 * 1024 * 1024)
    assert (status, valid, reason) == ("completed_valid", True, None)


def test_run_child_deliberate_failure(tmp_path):
    child = _run_worker(tmp_path, "failure")
    assert child.return_code == 2
    status, valid, reason = fyl._classify(child, 256 * 1024 * 1024)
    assert status == "failed_implementation"
    assert valid is False
    assert "return code 2" in reason
    assert "synthetic deliberate failure" in child.stderr


def test_run_child_deliberate_crash(tmp_path):
    child = _run_worker(tmp_path, "crash")
    assert child.return_code not in (0, None)
    assert "RuntimeError" in child.stderr
    status, valid, _reason = fyl._classify(child, 256 * 1024 * 1024)
    assert status == "failed_implementation"
    assert valid is False


def test_run_child_bounded_timeout_kills_process_group(tmp_path):
    child = _run_worker(tmp_path, "timeout", timeout=1.0, cpu_seconds=60.0)
    assert child.timed_out is True
    assert child.group_quiescent is True
    status, valid, reason = fyl._classify(child, 256 * 1024 * 1024)
    assert status == "resource_exhaustion"
    assert valid is False
    assert "timeout" in reason


def test_run_child_partial_artifacts_preserved_on_failure(tmp_path):
    """stdout/stderr logs exist and are non-clobbered even for a failing
    child -- 'preserve partial output on any failure' (DEC-20260908-195f0f
    engineering_successor.integration)."""
    stdout_path = tmp_path / "stdout.log"
    stderr_path = tmp_path / "stderr.log"
    core_runner._run_child(
        command=[sys.executable, str(WORKER), "failure"],
        cwd=tmp_path,
        timeout_seconds=5.0,
        memory_bytes=256 * 1024 * 1024,
        cpu_seconds=5.0,
        stdout_path=stdout_path,
        stderr_path=stderr_path,
        descendant_slots=0,
    )
    assert stdout_path.is_file()
    assert stderr_path.is_file()
    assert "synthetic deliberate failure" in stderr_path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# execute_locked, exercised directly against a manually assembled
# VerifiedLaunch (see file docstring point 2 for why).
# ---------------------------------------------------------------------------


def _verified_launch_for(run_dir_name: str, mode: str, *, timeout=5.0) -> "fyl.VerifiedLaunch":
    # Each call to execute_locked() actually creates run_dir on disk and
    # run directories are immutable/no-clobber by design (see
    # test_execute_locked_no_clobber_on_replay), so every OTHER test that
    # calls execute_locked needs a run_dir that has never existed before --
    # including across repeated `pytest` invocations in this same
    # worktree, since retained synthetic evidence is intentionally not
    # cleaned up between runs (see _cleanup_scratch_run_dirs above). A
    # per-process-per-call unique suffix keeps every such test independently
    # repeatable without deleting any prior run's retained evidence.
    unique_name = f"{run_dir_name}-{os.getpid()}-{time.monotonic_ns()}"
    doc = _base_document(unique_name)
    body = doc["finite_yaml_lock"]
    body["argv"] = [sys.executable, str(WORKER), mode]
    body["resource_policy"]["timeout_seconds"] = timeout
    protocol_files = fyl._verify_source_closure(REPO_ROOT, body["source_closure"])
    run_dir = (REPO_ROOT / body["run_directory"]).resolve()
    return fyl.VerifiedLaunch(
        lock_path=Path("synthetic-in-memory-lock.yaml"),
        lock_sha256=hashlib.sha256(yaml.safe_dump(doc).encode()).hexdigest(),
        lock=doc,
        experiment_id=body["experiment_id"],
        run_id=body["run_id"],
        run_dir=run_dir,
        argv=body["argv"],
        output_allowlist=tuple(body["output_allowlist"]),
        timeout_seconds=float(body["resource_policy"]["timeout_seconds"]),
        memory_bytes=int(body["resource_policy"]["memory_bytes"]),
        resource_policy=dict(body["resource_policy"]),
        protocol_files=protocol_files,
        launch_authority=_launch_authority(doc),
        validated_at=fyl._utc_now_iso(),
    )


@pytest.fixture(autouse=True)
def _cleanup_scratch_run_dirs():
    created_before = set()
    root = REPO_ROOT / SCRATCH_ROOT
    if root.is_dir():
        created_before = {p.name for p in root.iterdir()}
    yield
    # Intentionally NOT deleted: this task's completion gate requires every
    # synthetic run's artifacts to be retained and cross-referenced from
    # synthetic-test-evidence.json before "ordinary scratch cleanup" (which
    # the Coordinator/QA task performs later, not this fixture).


def test_execute_locked_success_end_to_end(tmp_path, monkeypatch):
    # Other retained research artifacts may legitimately exist in the shared
    # repository while this synthetic run is tested. The postflight-drift
    # branch has its own deterministic test below; isolate the benign child
    # success contract here from unrelated worktree state.
    monkeypatch.setattr(fyl._core, "_tree_clean_except", lambda _root, _run_dir: True)
    verified = _verified_launch_for("execute-success-case", "success")
    manifest_path = fyl.execute_locked(verified)
    manifest = yaml.safe_load(Path(manifest_path).read_text(encoding="utf-8"))
    run = manifest["finite_yaml_locked_run"]
    assert run["scientific_content"] is False
    assert run["post_run_checks"]["process_group_quiescent"] is True
    assert run["post_run_checks"]["source_closure_unchanged"] is True
    # This focused success test supplies a clean postflight seam; the distinct
    # mutation test below proves the actual fail-closed drift transition.
    assert run["post_run_checks"]["tree_unchanged_except_run_dir"] is True
    assert run["status"] == "completed_valid"
    assert run["valid"] is True
    assert run["invalid_reason"] is None
    run_dir = Path(verified.run_dir)
    for name in ("command.txt", "environment.json", "stdout.log", "stderr.log", "raw-result.json", "manifest.yaml"):
        assert (run_dir / name).is_file(), name
    raw_result = json.loads((run_dir / "raw-result.json").read_text(encoding="utf-8"))
    assert raw_result["scientific_content"] is False
    assert raw_result["child"]["return_code"] == 0


def test_execute_locked_postflight_drift_refuses(tmp_path, monkeypatch):
    """A postflight worktree mutation invalidates an otherwise benign run."""
    monkeypatch.setattr(fyl._core, "_tree_clean_except", lambda _root, _run_dir: False)
    verified = _verified_launch_for("execute-postflight-drift-case", "success")
    manifest_path = fyl.execute_locked(verified)
    manifest = yaml.safe_load(Path(manifest_path).read_text(encoding="utf-8"))
    run = manifest["finite_yaml_locked_run"]
    assert run["post_run_checks"]["tree_unchanged_except_run_dir"] is False
    assert run["status"] == "failed_infrastructure"
    assert run["valid"] is False
    assert "postflight drift" in run["invalid_reason"]


def test_execute_locked_deliberate_failure_end_to_end(tmp_path):
    verified = _verified_launch_for("execute-failure-case", "failure")
    manifest_path = fyl.execute_locked(verified)
    manifest = yaml.safe_load(Path(manifest_path).read_text(encoding="utf-8"))
    run = manifest["finite_yaml_locked_run"]
    # Both the child's own nonzero exit AND the (expected, disclosed)
    # worktree drift point the same direction here; either alone would
    # already forbid completed_valid.
    assert run["status"] in ("failed_implementation", "failed_infrastructure")
    assert run["valid"] is False
    stderr_text = (Path(verified.run_dir) / "stderr.log").read_text(encoding="utf-8")
    assert "synthetic deliberate failure" in stderr_text


def test_execute_locked_no_clobber_on_replay(tmp_path):
    verified = _verified_launch_for("execute-noclobber-case", "success")
    fyl.execute_locked(verified)
    with pytest.raises(FileExistsError):
        fyl.execute_locked(verified)


def test_execute_locked_bounded_timeout_end_to_end(tmp_path):
    verified = _verified_launch_for("execute-timeout-case", "timeout", timeout=1.0)
    manifest_path = fyl.execute_locked(verified)
    manifest = yaml.safe_load(Path(manifest_path).read_text(encoding="utf-8"))
    run = manifest["finite_yaml_locked_run"]
    # As with the deliberate-failure case above: the child's own timeout AND
    # the disclosed worktree drift both forbid completed_valid here; either
    # alone would already do so, so the manifest status may read as either
    # depending on which the code checks. raw-result.json is the source of
    # truth for what actually happened to the child itself.
    assert run["status"] in ("resource_exhaustion", "failed_infrastructure")
    assert run["valid"] is False
    assert run["post_run_checks"]["process_group_quiescent"] is True
    raw_result = json.loads((Path(verified.run_dir) / "raw-result.json").read_text(encoding="utf-8"))
    assert raw_result["child"]["timed_out"] is True


# ---------------------------------------------------------------------------
# Twelve-case recovery inventory (EXP-ECDLP-2cb7f8/source-v2/locked_entry.py)
# -- static metadata only, no scientific field or section evaluated.
# ---------------------------------------------------------------------------


def _load_locked_entry_2cb7f8():
    path = REPO_ROOT / "experiments" / "EXP-ECDLP-2cb7f8" / "source-v2" / "locked_entry.py"
    spec = importlib.util.spec_from_file_location("exp_ecdlp_2cb7f8_locked_entry", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


LOCKED_ENTRY_2CB7F8 = _load_locked_entry_2cb7f8()


def test_recovery_case_inventory_accepts_the_frozen_twelve():
    LOCKED_ENTRY_2CB7F8.validate_recovery_case_inventory(list(LOCKED_ENTRY_2CB7F8.RECOVERY_CASE_IDS))


def test_recovery_case_inventory_rejects_reorder():
    mutated = list(LOCKED_ENTRY_2CB7F8.RECOVERY_CASE_IDS)
    mutated[0], mutated[1] = mutated[1], mutated[0]
    with pytest.raises(LOCKED_ENTRY_2CB7F8.RecoveryInventoryError, match="reordered_only=True"):
        LOCKED_ENTRY_2CB7F8.validate_recovery_case_inventory(mutated)


def test_recovery_case_inventory_rejects_deleted_case():
    mutated = list(LOCKED_ENTRY_2CB7F8.RECOVERY_CASE_IDS)[:-1]
    with pytest.raises(LOCKED_ENTRY_2CB7F8.RecoveryInventoryError, match="missing="):
        LOCKED_ENTRY_2CB7F8.validate_recovery_case_inventory(mutated)


def test_recovery_case_inventory_rejects_duplicate_id():
    mutated = list(LOCKED_ENTRY_2CB7F8.RECOVERY_CASE_IDS) + [LOCKED_ENTRY_2CB7F8.RECOVERY_CASE_IDS[0]]
    with pytest.raises(LOCKED_ENTRY_2CB7F8.RecoveryInventoryError, match="duplicate IDs"):
        LOCKED_ENTRY_2CB7F8.validate_recovery_case_inventory(mutated)


def test_recovery_case_arms_reject_one_case_difference():
    arm_b = list(LOCKED_ENTRY_2CB7F8.RECOVERY_CASE_IDS)
    arm_i = list(LOCKED_ENTRY_2CB7F8.RECOVERY_CASE_IDS)
    arm_i[-1] = "O_present"  # collapses O_absent into a duplicate of O_present
    with pytest.raises(LOCKED_ENTRY_2CB7F8.RecoveryInventoryError):
        LOCKED_ENTRY_2CB7F8.validate_recovery_case_arms(arm_b, arm_i)


def test_recovery_case_arms_accept_identical_inventories():
    arm_b = list(LOCKED_ENTRY_2CB7F8.RECOVERY_CASE_IDS)
    arm_i = list(LOCKED_ENTRY_2CB7F8.RECOVERY_CASE_IDS)
    LOCKED_ENTRY_2CB7F8.validate_recovery_case_arms(arm_b, arm_i)


# ---------------------------------------------------------------------------
# Non-invocation: this test file, the adapter, and both wrappers never
# import or evaluate either archived experiment kernel.
# ---------------------------------------------------------------------------


def test_this_suite_never_imported_either_experiment_kernel():
    forbidden_module_name_fragments = ("run_model_comparison", "group_oracle", "incidence", "presentation_inventory")
    for name, module in list(sys.modules.items()):
        source_file = getattr(module, "__file__", None) or ""
        if "experiments/EXP-ECDLP-abf981/source/" in source_file or "experiments/EXP-ECDLP-2cb7f8/source/" in source_file:
            pytest.fail(f"forbidden kernel import detected: {name} ({source_file})")
        for fragment in forbidden_module_name_fragments:
            assert fragment != name, f"forbidden kernel module name imported: {name}"


def test_adapter_module_source_has_no_static_kernel_import():
    text = ADAPTER_SOURCE.read_text(encoding="utf-8")
    for forbidden in ("import run_model_comparison", "import run\n", "from experiments"):
        assert forbidden not in text


# ---------------------------------------------------------------------------
# Original CLI refusals remain intact (no bypass, no removal).
# ---------------------------------------------------------------------------


def test_abf981_cli_still_refuses_scientific_invocation(tmp_path):
    import subprocess

    kernel = REPO_ROOT / "experiments/EXP-ECDLP-abf981/source/run_model_comparison.py"
    # The frozen exact reservation for cell p11 (specification.yaml
    # run_bindings); main() requires an exact match before it will even
    # reach its own refusal message. This path is never created: main()
    # refuses (and this test asserts that) before any directory would be
    # made.
    frozen_run_dir_relative = "experiments/EXP-ECDLP-abf981/runs/RUN-ECDLP-56d8aa"
    frozen_run_dir = REPO_ROOT / frozen_run_dir_relative
    assert not frozen_run_dir.exists(), "precondition: the real reserved run directory must not already exist"
    completed = subprocess.run(
        [
            sys.executable,
            str(kernel),
            "--spec",
            "experiments/EXP-ECDLP-abf981/specification.yaml",
            "--cell",
            "p11",
            "--run-dir",
            frozen_run_dir_relative,
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert completed.returncode == 2
    assert "locked_runner_integration_unresolved" in completed.stderr
    assert not frozen_run_dir.exists(), "the archived CLI must not have created the reserved run directory"


def test_2cb7f8_cli_still_refuses_every_invocation(tmp_path):
    import subprocess

    kernel = REPO_ROOT / "experiments/EXP-ECDLP-2cb7f8/source/run.py"
    completed = subprocess.run(
        [
            sys.executable,
            str(kernel),
            "--config-json",
            json.dumps(
                {
                    "experiment_id": "EXP-ECDLP-2cb7f8",
                    "version": 1,
                    "case_id": "E5",
                    "p": 5,
                    "curve_constant": 1,
                    "run_id": "RUN-ECDLP-3c6277",
                }
            ),
            "--locked-plan",
            "unused.json",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert completed.returncode == 2
    assert "UNRESOLVED_CANONICAL_RUNNER_INTERFACE" in completed.stderr
