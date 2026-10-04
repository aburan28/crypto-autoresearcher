#!/usr/bin/env python3
"""Bounded synthetic/static admission checks for TASK-20260907-774962.

This script performs no frozen fixture selection, collision census, control
matrix, candidate search, or scientific observation.  It executes exactly 17
small static or synthetic/mock cases, serially, with a ten-second alarm per
case.  Results are printed as JSON for transcription into check-receipt.json.
"""
from __future__ import annotations

import base64
import contextlib
import hashlib
import importlib.util
import inspect
import json
import math
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Callable, Iterator

import yaml


HERE = Path(__file__).resolve()
REPO = next(parent for parent in HERE.parents if (parent / "AGENTS.md").is_file())
IMPLEMENTATION = REPO / "experiments/EXP-ECDLP-651b94/implementation/TASK-20260906-9393c3"
DRIVER_PATH = IMPLEMENTATION / "driver.py"
PLAN_PATH = IMPLEMENTATION / "execution-plan.json"
SPEC_PATH = REPO / "experiments/EXP-ECDLP-651b94/specification.yaml"
REVIEW_PLAN_PATH = REPO / "coordination/experiment-reserve/BATCH-1bb183/spectral-review-plan.yaml"
SNAPSHOT_COMMIT = "da2753868e183e40512410baa0e7e79c6595da54"
REVIEW_PLAN_COMMIT = "915f5b19b81cc792e3ac9e34b2a5f656c4fff678"
EXPECTED_SHA256 = {
    "experiments/EXP-ECDLP-651b94/specification.yaml": "97b44f40c8f9d52a587cf4fd9788dd391e42ce5c6dab8ec212a8af34cdfa4eee",
    "experiments/EXP-ECDLP-651b94/implementation/TASK-20260906-9393c3/driver.py": "3f8a862c0bec7d5ddab3b6de9b104e0a61a6f0530dc7dfdae912d652985d4b75",
    "experiments/EXP-ECDLP-651b94/implementation/TASK-20260906-9393c3/tests.py": "3ddc5d83deefc485f04ccd64f3da4a276107649c105f67d0bf74ce5470dc7a57",
    "experiments/EXP-ECDLP-651b94/implementation/TASK-20260906-9393c3/README.md": "a7e3ff4eb1eabf1433db9f7d6cc22921df51969b3c58b496e5177f9af5948b2a",
    "experiments/EXP-ECDLP-651b94/implementation/TASK-20260906-9393c3/implementation-report.yaml": "ba4f7849c96a06633d2397f882ae56167f76c48bb1816787fae83376a9ccf723",
    "experiments/EXP-ECDLP-651b94/implementation/TASK-20260906-9393c3/execution-plan.json": "b4811749f0d2a07d267bf4552bd8fcada5b41d4478e13245e8c43b18c3f6a58a",
}


spec = importlib.util.spec_from_file_location("spectral_driver_under_review", DRIVER_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError("cannot import bound driver")
driver = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = driver
spec.loader.exec_module(driver)


@contextlib.contextmanager
def patched(obj: Any, name: str, value: Any) -> Iterator[None]:
    previous = getattr(obj, name)
    setattr(obj, name, value)
    try:
        yield
    finally:
        setattr(obj, name, previous)


def git_blob(commit: str, relative: str) -> bytes:
    return subprocess.run(
        ["git", "show", f"{commit}:{relative}"],
        cwd=REPO,
        capture_output=True,
        check=True,
    ).stdout


def check_source_and_snapshot_bindings() -> str:
    for relative, expected in EXPECTED_SHA256.items():
        live = hashlib.sha256((REPO / relative).read_bytes()).hexdigest()
        snap = hashlib.sha256(git_blob(SNAPSHOT_COMMIT, relative)).hexdigest()
        assert live == expected, f"live hash mismatch for {relative}: {live}"
        assert snap == expected, f"snapshot hash mismatch for {relative}: {snap}"
    plan_live = hashlib.sha256(REVIEW_PLAN_PATH.read_bytes()).hexdigest()
    plan_snap = hashlib.sha256(
        git_blob(REVIEW_PLAN_COMMIT, str(REVIEW_PLAN_PATH.relative_to(REPO)))
    ).hexdigest()
    assert plan_live == plan_snap == "73c81dc8ceae831bcb4a5c64d7eb30757c0f0a731ce54a82dd6a20258b9c6501"
    return "six producer bindings and the prereview-plan binding match live and committed bytes"


def check_rng_canonicalization_and_counter() -> str:
    params = (17, 1, 2, 19, 0, 3, 7)
    payload = json.dumps(
        [driver.EXPERIMENT_ID, "shuffle", list(params), 606308, 0],
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    expected = int.from_bytes(hashlib.sha256(payload).digest(), "big")
    actual = driver.stream_digest(purpose="shuffle", params=params, seed=606308, counter=0)
    draw, counter = driver.rejection_draw(
        purpose="target", params=(17, 1, 2, 19, 0, 0, 0), seed=606308, counter=0, n=1
    )
    assert actual == expected
    assert (draw, counter) == (0, 1), (draw, counter)
    return "canonical SHA-256 bytes agree independently; n=1 consumes exactly one digest"


def check_coordinate_and_rho_arithmetic() -> str:
    curve = driver.Curve(17, 2, 2)
    point = (5, 1)
    twice = curve.add(point, point)
    u = 3
    transported_curve = driver.coordinate_curve(curve, u)
    transported_point = driver.coordinate_transport(curve, point, u)
    transported_twice = driver.coordinate_transport(curve, twice, u)
    assert transported_curve.on_curve(transported_point)
    assert transported_curve.add(transported_point, transported_point) == transported_twice
    assignment = {transported_point: 2}
    _, next_a, next_b, op = driver.rho_step(
        transported_curve, transported_point, transported_point, transported_twice,
        4, 6, 19, assignment,
    )
    assert (next_a, next_b, op) == (8, 12, "double")
    return "synthetic isomorphism commutes with doubling and the selected rho label doubles both coefficients"


class CyclicMock:
    def __init__(self, order: int):
        self.order = order

    def add(self, left: Any, right: Any) -> int:
        a = 0 if left is None else int(left)
        b = 0 if right is None else int(right)
        return (a + b) % self.order

    def scalar(self, scalar: int, point: Any) -> int:
        p = 0 if point is None else int(point)
        return (scalar * p) % self.order


def check_synthetic_collision_census() -> str:
    r = 5
    curve = CyclicMock(r)
    assignment = {0: 0, 1: 1, 2: 2, 3: 0, 4: 1}
    result = driver.collision_census(curve, 1, 2, r, assignment)
    assert result["starts"] == r
    assert len(result["certificates"]) == r
    assert all(cert["repeat_step"] <= r + 1 for cert in result["certificates"])
    successful = [cert for cert in result["certificates"] if cert["verified"]]
    assert successful, "synthetic table unexpectedly has no verifiable collision"
    assert all(cert["candidate"] == 2 for cert in successful)
    zero = [{"transition_group_operations": 7, "verification_group_operations": 3, "successes": 0}]
    assert math.isinf(driver.pooled_null_cost(zero))
    return f"five synthetic starts terminate; {len(successful)} recovered labels equal Q=2; zero-success cost is infinite"


def check_occupancy_and_relabel_instrument() -> str:
    points = [0, 1, 2, 3]
    values = [0, 0, 1, 2]
    assignment, counter = driver.occupancy_assignment(
        points, values, params=(17, 1, 2, 5, 0, 1, 1), seed=606308
    )
    assert sorted(assignment.values()) == sorted(values)
    assert counter == 3
    transition = {
        0: (1, 1, 0, "add"),
        1: (2, 0, 1, "add"),
        2: (3, 0, 0, "double"),
        3: (0, 1, 0, "add"),
    }
    bijection = {0: 2, 1: 0, 2: 3, 3: 1}
    assert driver.relabel_control(transition, points, bijection, 5) is True
    return "synthetic shuffle preserves the bucket multiset and the conjugated finite transition table preserves outcomes"


def check_singular_fixture_is_discarded() -> str:
    try:
        driver.Curve(7, 1, 2)
    except ValueError:
        singular_rejected = True
    else:
        singular_rejected = False
    source = inspect.getsource(driver.fixture_candidates)
    catches_singular = "except ValueError" in source or "try:" in source
    assert singular_rejected
    assert catches_singular, (
        "Curve(7,1,2) is singular, but fixture_candidates constructs Curve before any "
        "discard/catch; a singular B aborts enumeration instead of being discarded"
    )
    return "singular candidates are explicitly discarded"


def check_constant_map_control_is_executed() -> str:
    source = inspect.getsource(driver.known_false_control)
    executes_reset_transition = "rho_step" in source or "collision_census" in source
    reports_outcomes = "successes" in source or "collisions" in source
    assert executes_reset_transition and reports_outcomes, (
        "known_false_control initializes delta_b_zero=True and compares zero labels, "
        "without executing a reset transition or recording collision/solve outcomes"
    )
    return "constant-O reset map was executed and its collision/solve outcomes were checked"


def make_signed_lock(directory: Path) -> tuple[Path, str, dict[str, Any]]:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

    receipt = directory / "synthetic-review-receipt.yaml"
    receipt.write_text("synthetic: true\n", encoding="utf-8")
    private = Ed25519PrivateKey.generate()
    public_raw = private.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    public_b64 = base64.b64encode(public_raw).decode("ascii")
    lock: dict[str, Any] = {
        "kind": "genuine_runtime_code_execution_lock",
        "approved": True,
        "experiment_id": driver.EXPERIMENT_ID,
        "approval_decision_id": driver.APPROVAL_ID,
        "spec_sha256": hashlib.sha256(SPEC_PATH.read_bytes()).hexdigest(),
        "driver_sha256": hashlib.sha256(DRIVER_PATH.read_bytes()).hexdigest(),
        "execution_plan_sha256": hashlib.sha256(PLAN_PATH.read_bytes()).hexdigest(),
        "runtime": driver.actual_runtime_binding(),
        "resource_limits": {
            "wall_clock_seconds": 5400,
            "total_cpu_hours": 1.5,
            "maximum_memory_gb": 8,
            "maximum_runs": 1,
            "maximum_workers": 1,
        },
        "signature": "",
        "runtime_verified": True,
        "code_verified": True,
        "implementation_review_receipt": {
            "path": str(receipt),
            "sha256": hashlib.sha256(receipt.read_bytes()).hexdigest(),
        },
        "run_id": "RUN-SYNTHETIC-LOCK",
        "public_key_b64": public_b64,
    }
    lock["signature"] = base64.b64encode(private.sign(driver.lock_payload(lock))).decode("ascii")
    path = directory / "lock.json"
    path.write_text(json.dumps(lock), encoding="utf-8")
    return path, public_b64, lock


def check_valid_ephemeral_lock() -> str:
    with tempfile.TemporaryDirectory(prefix="spectral-lock-valid-") as tmp:
        path, public_b64, _ = make_signed_lock(Path(tmp))
        verified = driver.verify_launch_lock(
            path, trusted_public_key_b64=public_b64, execution_plan=PLAN_PATH
        )
        assert verified["run_id"] == "RUN-SYNTHETIC-LOCK"
    return "ephemeral correctly signed lock binds the exact spec, driver, plan, runtime, limits, receipt and run id"


def check_forged_signature_rejected() -> str:
    with tempfile.TemporaryDirectory(prefix="spectral-lock-forged-") as tmp:
        path, public_b64, lock = make_signed_lock(Path(tmp))
        lock["signature"] = base64.b64encode(bytes(64)).decode("ascii")
        path.write_text(json.dumps(lock), encoding="utf-8")
        try:
            driver.verify_launch_lock(path, trusted_public_key_b64=public_b64, execution_plan=PLAN_PATH)
        except driver.LaunchRefused as exc:
            assert "signature verification failed" in str(exc)
        else:
            raise AssertionError("forged detached signature was accepted")
    return "forged Ed25519 signature is rejected"


def check_stale_driver_binding_rejected() -> str:
    with tempfile.TemporaryDirectory(prefix="spectral-lock-stale-") as tmp:
        path, public_b64, lock = make_signed_lock(Path(tmp))
        lock["driver_sha256"] = "0" * 64
        path.write_text(json.dumps(lock), encoding="utf-8")
        try:
            driver.verify_launch_lock(path, trusted_public_key_b64=public_b64, execution_plan=PLAN_PATH)
        except driver.LaunchRefused as exc:
            assert "actual driver and execution plan" in str(exc)
        else:
            raise AssertionError("stale driver binding was accepted")
    return "stale driver hash is rejected before launch"


def check_runtime_mismatch_rejected() -> str:
    with tempfile.TemporaryDirectory(prefix="spectral-lock-runtime-") as tmp:
        path, public_b64, lock = make_signed_lock(Path(tmp))
        lock["runtime"] = {**lock["runtime"], "python": "0.0-synthetic-mismatch"}
        path.write_text(json.dumps(lock), encoding="utf-8")
        try:
            driver.verify_launch_lock(path, trusted_public_key_b64=public_b64, execution_plan=PLAN_PATH)
        except driver.LaunchRefused as exc:
            assert "runtime does not match" in str(exc)
        else:
            raise AssertionError("runtime mismatch was accepted")
    return "exact runtime mismatch is rejected"


def check_manifest_minimum_schema() -> str:
    manifest = yaml.safe_load(
        driver._manifest(
            {"run_id": "RUN-SYNTHETIC-MANIFEST"},
            "2026-09-07T00:00:00+00:00",
            "completed_valid",
            error=None,
            fixtures=[],
            panel=[],
            elapsed=1.0,
        )
    )["run"]
    missing = []
    code = manifest.get("code") or {}
    resources = manifest.get("resources") or {}
    result = manifest.get("result") or {}
    if not code.get("commit"):
        missing.append("run.code.commit")
    if not code.get("command"):
        missing.append("run.code.command")
    if resources.get("cpu_seconds") is None:
        missing.append("run.resources.cpu_seconds")
    if not isinstance(result.get("certificate"), dict):
        missing.append("run.result.certificate")
    if not isinstance(manifest.get("artifacts"), dict):
        missing.append("run.artifacts")
    assert not missing, "minimum manifest omissions: " + ", ".join(missing)
    return "manifest satisfies the repository minimum execution-provenance and result schema"


def minimal_cell(*, known_false_passes: bool = True) -> dict[str, Any]:
    return {
        "curve_id": "synthetic-curve",
        "seed": 606308,
        "u": 1,
        "d": 0.0,
        "controls": {
            "known_false": {
                "constant_map_delta_b_zero": known_false_passes,
                "mutated_candidate_fails_certificate": known_false_passes,
            }
        },
    }


def check_cancellation_preserves_partial_and_classifies() -> str:
    captured: dict[str, bytes] = {}
    partial_row = minimal_cell()

    def fail_after_one(_fixtures: Any, _checkpoint: Any) -> list[dict[str, Any]]:
        produced = [partial_row]
        exc = driver.LaunchRefused("cancelled")
        exc.partial_panel = produced
        raise exc

    def persist(**kwargs: Any) -> dict[str, str]:
        captured.update(kwargs["artifacts"])
        return {name: hashlib.sha256(payload).hexdigest() for name, payload in captured.items()}

    with tempfile.TemporaryDirectory(prefix="spectral-cancel-") as tmp, \
         patched(driver, "verify_launch_lock", lambda *args, **kwargs: {"run_id": "RUN-SYNTHETIC-CANCEL"}), \
         patched(driver, "select_fixtures", lambda checkpoint: {9: [{}, {}], 11: [{}, {}]}), \
         patched(driver, "future_panel", fail_after_one), \
         patched(driver, "persist_verified_artifacts", persist), \
         patched(driver, "_peak_rss_bytes", lambda: 1):
        try:
            driver.run_admitted_pipeline(
                lock_path=Path(tmp) / "unused-lock",
                trusted_public_key_b64="synthetic",
                execution_plan=PLAN_PATH,
                experiment_root=Path(tmp),
            )
        except driver.LaunchRefused:
            pass
        else:
            raise AssertionError("synthetic cancellation did not stop")
    manifest_status = yaml.safe_load(captured["manifest.yaml"])["run"]["status"]
    raw = captured["raw.jsonl"]
    assert manifest_status != "completed_invalid" and b"synthetic-curve" in raw, (
        f"cancellation recorded status={manifest_status!r}, raw_rows="
        f"{sum(bool(line) for line in raw.splitlines())}; the completed row was lost"
    )
    return "cancellation has a non-invalid terminal class and retains already-completed rows"


def check_wall_deadline_is_enforced() -> str:
    captured: dict[str, bytes] = {}
    times = iter((0.0, 5401.0))

    def persist(**kwargs: Any) -> dict[str, str]:
        captured.update(kwargs["artifacts"])
        return {}

    with tempfile.TemporaryDirectory(prefix="spectral-wall-") as tmp, \
         patched(driver, "verify_launch_lock", lambda *args, **kwargs: {"run_id": "RUN-SYNTHETIC-WALL"}), \
         patched(driver, "select_fixtures", lambda checkpoint: {9: [{}, {}], 11: [{}, {}]}), \
         patched(driver, "future_panel", lambda fixtures, checkpoint: [minimal_cell()]), \
         patched(driver, "all_u_decisions", lambda panel: {1: "inconclusive", 2: "inconclusive", 3: "inconclusive"}), \
         patched(driver, "persist_verified_artifacts", persist), \
         patched(driver, "_peak_rss_bytes", lambda: 1), \
         patched(driver.time, "monotonic", lambda: next(times)):
        driver.run_admitted_pipeline(
            lock_path=Path(tmp) / "unused-lock",
            trusted_public_key_b64="synthetic",
            execution_plan=PLAN_PATH,
            experiment_root=Path(tmp),
        )
    status = yaml.safe_load(captured["manifest.yaml"])["run"]["status"]
    assert status != "completed_valid", (
        f"elapsed wall time exceeded 5400 seconds but status={status!r}; no wall deadline is checked"
    )
    return "wall-clock overrun is stopped and classified before a valid package is emitted"


def check_initial_rss_failure_gets_terminal_package() -> str:
    persisted: list[dict[str, bytes]] = []

    def persist(**kwargs: Any) -> dict[str, str]:
        persisted.append(kwargs["artifacts"])
        return {}

    with tempfile.TemporaryDirectory(prefix="spectral-rss-") as tmp, \
         patched(driver, "verify_launch_lock", lambda *args, **kwargs: {"run_id": "RUN-SYNTHETIC-RSS"}), \
         patched(driver, "persist_verified_artifacts", persist), \
         patched(driver, "_peak_rss_bytes", lambda: 8 * 1024**3 + 1):
        try:
            driver.run_admitted_pipeline(
                lock_path=Path(tmp) / "unused-lock",
                trusted_public_key_b64="synthetic",
                execution_plan=PLAN_PATH,
                experiment_root=Path(tmp),
            )
        except driver.LaunchRefused as exc:
            assert "RSS exceeded" in str(exc)
        else:
            raise AssertionError("synthetic RSS overrun did not stop")
    assert persisted, "initial RSS checkpoint is outside the preservation try-block; no terminal package was written"
    return "an RSS refusal at the initial checkpoint still emits a terminal canonical package"


def check_failed_control_blocks_valid_package() -> str:
    captured: dict[str, bytes] = {}

    def persist(**kwargs: Any) -> dict[str, str]:
        captured.update(kwargs["artifacts"])
        return {}

    with tempfile.TemporaryDirectory(prefix="spectral-control-") as tmp, \
         patched(driver, "verify_launch_lock", lambda *args, **kwargs: {"run_id": "RUN-SYNTHETIC-CONTROL"}), \
         patched(driver, "select_fixtures", lambda checkpoint: {9: [{}, {}], 11: [{}, {}]}), \
         patched(driver, "future_panel", lambda fixtures, checkpoint: [minimal_cell(known_false_passes=False)]), \
         patched(driver, "all_u_decisions", lambda panel: {1: "inconclusive", 2: "inconclusive", 3: "inconclusive"}), \
         patched(driver, "persist_verified_artifacts", persist), \
         patched(driver, "_peak_rss_bytes", lambda: 1):
        driver.run_admitted_pipeline(
            lock_path=Path(tmp) / "unused-lock",
            trusted_public_key_b64="synthetic",
            execution_plan=PLAN_PATH,
            experiment_root=Path(tmp),
        )
    status = yaml.safe_load(captured["manifest.yaml"])["run"]["status"]
    assert status != "completed_valid", (
        "a panel carrying false known-false control booleans was emitted as completed_valid"
    )
    return "false named-control booleans invalidate the package"


def check_artifact_write_is_atomic() -> str:
    artifacts = {name: f"synthetic:{name}\n".encode() for name in driver.RUN_ARTIFACT_NAMES}
    original_write = Path.write_bytes

    def fail_mid_write(path: Path, payload: bytes) -> int:
        if path.name == "raw.jsonl":
            raise OSError("synthetic mid-package write failure")
        return original_write(path, payload)

    with tempfile.TemporaryDirectory(prefix="spectral-atomic-") as tmp, \
         patched(driver, "verify_launch_lock", lambda *args, **kwargs: {"run_id": "RUN-SYNTHETIC-ATOMIC"}), \
         patched(Path, "write_bytes", fail_mid_write):
        root = Path(tmp)
        try:
            driver.persist_verified_artifacts(
                lock_path=root / "unused-lock",
                trusted_public_key_b64="synthetic",
                execution_plan=PLAN_PATH,
                experiment_root=root,
                artifacts=artifacts,
            )
        except OSError as exc:
            assert "synthetic mid-package" in str(exc)
        else:
            raise AssertionError("synthetic write fault did not fire")
        final_dir = root / "runs/RUN-SYNTHETIC-ATOMIC"
        residue = sorted(path.name for path in final_dir.iterdir()) if final_dir.exists() else []
        assert not final_dir.exists(), (
            f"non-atomic write left final run directory with {residue}; immutable retry is then refused"
        )
    return "a mid-package write cannot expose a partial final run directory"


CASES: list[tuple[str, Callable[[], str]]] = [
    ("source_and_snapshot_bindings", check_source_and_snapshot_bindings),
    ("rng_canonicalization_and_counter", check_rng_canonicalization_and_counter),
    ("coordinate_and_rho_arithmetic", check_coordinate_and_rho_arithmetic),
    ("synthetic_collision_census", check_synthetic_collision_census),
    ("occupancy_and_relabel_instrument", check_occupancy_and_relabel_instrument),
    ("singular_fixture_discard", check_singular_fixture_is_discarded),
    ("constant_map_control_execution", check_constant_map_control_is_executed),
    ("valid_ephemeral_lock", check_valid_ephemeral_lock),
    ("forged_signature_rejection", check_forged_signature_rejected),
    ("stale_driver_binding_rejection", check_stale_driver_binding_rejected),
    ("runtime_mismatch_rejection", check_runtime_mismatch_rejected),
    ("minimum_manifest_schema", check_manifest_minimum_schema),
    ("cancellation_partial_retention", check_cancellation_preserves_partial_and_classifies),
    ("wall_deadline_enforcement", check_wall_deadline_is_enforced),
    ("initial_rss_terminal_package", check_initial_rss_failure_gets_terminal_package),
    ("failed_control_blocks_valid_package", check_failed_control_blocks_valid_package),
    ("atomic_artifact_custody", check_artifact_write_is_atomic),
]


class CaseTimeout(RuntimeError):
    pass


def alarm_handler(_signum: int, _frame: Any) -> None:
    raise CaseTimeout("case exceeded 10 seconds")


def main() -> int:
    signal.signal(signal.SIGALRM, alarm_handler)
    started = time.monotonic()
    results = []
    for name, function in CASES:
        case_started = time.monotonic()
        signal.setitimer(signal.ITIMER_REAL, 10.0)
        try:
            detail = function()
        except AssertionError as exc:
            status = "FAIL"
            detail = str(exc)
        except Exception as exc:  # every unexpected check failure remains visible
            status = "ERROR"
            detail = f"{type(exc).__name__}: {exc}"
        else:
            status = "PASS"
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0.0)
        results.append({
            "name": name,
            "status": status,
            "detail": detail,
            "wall_seconds": round(time.monotonic() - case_started, 6),
        })
    total = time.monotonic() - started
    document = {
        "task_id": "TASK-20260907-774962",
        "scope": "static and synthetic/mock implementation admission only",
        "case_executions": len(results),
        "scientific_runs": 0,
        "maximum_seconds_per_case": 10,
        "aggregate_wall_seconds": round(total, 6),
        "results": results,
        "summary": {
            "passed": sum(item["status"] == "PASS" for item in results),
            "failed": sum(item["status"] == "FAIL" for item in results),
            "errors": sum(item["status"] == "ERROR" for item in results),
            "verdict": "PASS" if all(item["status"] == "PASS" for item in results) else "NEEDS_CORRECTION",
        },
    }
    print(json.dumps(document, indent=2, sort_keys=False))
    return 0 if document["summary"]["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
