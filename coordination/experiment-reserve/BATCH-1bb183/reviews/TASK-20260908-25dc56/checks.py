#!/usr/bin/env python3
"""Independent fixed source/admission/custody checks for TASK-20260908-25dc56.

The checks import trusted, hash-bound source and exercise only lower-level
static, arithmetic, mock, telemetry, temporary-file, and temporary-Git objects.
They never call fixture_scan, select_fixtures, future_cell,
run_future_pipeline, verify_launch_admission, driver.main, or any prospective
measurement entrypoint.  They allocate no real key, signature, lock, run id,
or production run directory and execute zero scientific cases.
"""
from __future__ import annotations

import ast
import copy
import hashlib
import importlib.util
import json
import os
import resource
import signal
import subprocess
import sys
import tempfile
import time
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterator
from unittest.mock import patch

import yaml


TASK_ID = "TASK-20260908-25dc56"
SOURCE_TASK_ID = "TASK-20260908-4cacf0"
AUTHORITY_COMMIT = "869b7962eba50355fdbf36d4356e104725e7b1f2"
CLAIM_COMMIT = "768584b935a929295e2f00649cb6c295c1dd97d0"
SOURCE_SNAPSHOT = "2c2b45a5772894c4bd0431cb2b5da45775382328"
ROOT = Path(__file__).resolve().parents[5]
HANDOFF_REL = f"ledger/handoffs/{TASK_ID}.yaml"
HANDOFF_PATH = ROOT / HANDOFF_REL
PLAN_REL = f"coordination/experiment-reserve/BATCH-1bb183/review-plan-{TASK_ID}.yaml"
PLAN_PATH = ROOT / PLAN_REL
DRIVER_REL = f"experiments/EXP-ECDLP-651b94/implementation/{SOURCE_TASK_ID}/driver.py"
DRIVER_PATH = ROOT / DRIVER_REL
EXECUTION_PLAN_REL = f"experiments/EXP-ECDLP-651b94/implementation/{SOURCE_TASK_ID}/execution-plan.json"
EXECUTION_PLAN_PATH = ROOT / EXECUTION_PLAN_REL
SNAPSHOT_RECEIPT_REL = "coordination/experiment-reserve/BATCH-1bb183/archives/TASK-20260908-5abf3c/snapshot.json"
CLAIM_REL = f"coordination/experiment-reserve/BATCH-1bb183/claims/{TASK_ID}.1.claim.json"
MEMORY_LIMIT_BYTES = 2 * 1024**3
CASE_TIMEOUT_SECONDS = 10
MAX_TOTAL_CASES = 640


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git(root: Path, *args: str, text: bool = True) -> str | bytes:
    result = subprocess.run(
        ["git", "-C", str(root), *args], check=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=text,
    )
    return result.stdout.strip() if text else result.stdout


def git_blob(root: Path, commit: str, path: str) -> bytes:
    return git(root, "show", f"{commit}:{path}", text=False)  # type: ignore[return-value]


def is_ancestor(root: Path, earlier: str, later: str) -> bool:
    return subprocess.run(
        ["git", "-C", str(root), "merge-base", "--is-ancestor", earlier, later],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    ).returncode == 0


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


driver = load_module("validator_25dc56_driver", DRIVER_PATH)
research_dispatch = load_module("validator_25dc56_dispatch", ROOT / "tools/research_dispatch.py")


def administrative_bindings() -> dict[str, Any]:
    handoff = yaml.safe_load(HANDOFF_PATH.read_text(encoding="utf-8"))["handoff"]
    bindings = handoff["source_bindings"]
    rows: list[dict[str, Any]] = []
    for row in bindings:
        path = row["path"]
        expected = row["sha256"]
        live = digest((ROOT / path).read_bytes())
        authority = digest(git_blob(ROOT, AUTHORITY_COMMIT, path))
        rows.append({
            "path": path,
            "expected_sha256": expected,
            "live_sha256": live,
            "authority_sha256": authority,
            "matched": expected == live == authority,
        })
    snapshot = json.loads(git_blob(ROOT, SOURCE_SNAPSHOT, SNAPSHOT_RECEIPT_REL))
    changed = set(filter(None, str(git(ROOT, "diff-tree", "--no-commit-id", "--name-only", "-r", SOURCE_SNAPSHOT)).splitlines()))
    expected_snapshot_paths = set(snapshot["source_path_sha256"]) | {SNAPSHOT_RECEIPT_REL}
    source_hashes_match = all(
        digest(git_blob(ROOT, SOURCE_SNAPSHOT, path)) == expected
        for path, expected in snapshot["source_path_sha256"].items()
    )
    claim = json.loads(git_blob(ROOT, CLAIM_COMMIT, CLAIM_REL))
    between = str(git(ROOT, "log", "--reverse", "--format=%H %P %s", "--ancestry-path", f"{AUTHORITY_COMMIT}..{CLAIM_COMMIT}")).splitlines()
    return {
        "declared_inputs": len(handoff["inputs"]),
        "declared_source_bindings": len(bindings),
        "inputs_equal_binding_paths_in_order": handoff["inputs"] == [row["path"] for row in bindings],
        "matching_live_and_authority_bindings": sum(row["matched"] for row in rows),
        "binding_mismatches": [row for row in rows if not row["matched"]],
        "handoff_authority_sha256": digest(git_blob(ROOT, AUTHORITY_COMMIT, HANDOFF_REL)),
        "live_handoff_sha256": digest(HANDOFF_PATH.read_bytes()),
        "review_plan_authority_sha256": digest(git_blob(ROOT, AUTHORITY_COMMIT, PLAN_REL)),
        "live_review_plan_sha256": digest(PLAN_PATH.read_bytes()),
        "source_snapshot": {
            "commit": SOURCE_SNAPSHOT,
            "parent": git(ROOT, "rev-parse", f"{SOURCE_SNAPSHOT}^"),
            "source_task_state": snapshot.get("source_task_state"),
            "failed_tasks_reclassified_completed": snapshot.get("failed_tasks_reclassified_completed"),
            "changed_paths_exact": changed == expected_snapshot_paths,
            "source_hashes_match": source_hashes_match,
            "changed_paths": sorted(changed),
        },
        "ancestry": {
            "source_snapshot_to_authority": is_ancestor(ROOT, SOURCE_SNAPSHOT, AUTHORITY_COMMIT),
            "authority_to_claim": is_ancestor(ROOT, AUTHORITY_COMMIT, CLAIM_COMMIT),
            "claim_to_head": is_ancestor(ROOT, CLAIM_COMMIT, str(git(ROOT, "rev-parse", "HEAD"))),
            "authority_to_claim_path": between,
            "direct_parent_equality_required": False,
        },
        "claim": {
            "commit": CLAIM_COMMIT,
            "task_id": claim.get("task_id"),
            "epoch": claim.get("epoch"),
            "owner": claim.get("owner"),
            "session": claim.get("session"),
            "write_scope": claim.get("write_scope"),
        },
        "all_bindings_matched": all(row["matched"] for row in rows),
    }


def arm(work: int = 10, successes: int = 2, failed: int = 0) -> dict[str, Any]:
    return {
        "transition_group_operations": work,
        "verification_group_operations": 0,
        "successes": successes,
        "failed_certificates": failed,
    }


def controls() -> dict[str, Any]:
    return {
        "cayley": {"passed": True},
        "relabel": True,
        "occupancy": True,
        "known_false": {
            "constant_o": {"nonzero_denominators": 0, "solves": 0},
            "mutated_candidate_fails_certificate": True,
        },
    }


def decision_panel(value: float = 0.30) -> list[dict[str, Any]]:
    return [
        {"curve_id": curve, "seed": seed, "u": u,
         "metric": {"available": True, "d": value}, "validity": {"valid": True}}
        for curve in ("c0", "c1", "c2", "c3")
        for seed in driver.HELDOUT_SEEDS for u in driver.US
    ]


def expect_raises(kind: type[BaseException], action: Callable[[], Any]) -> None:
    try:
        action()
    except kind:
        return
    raise AssertionError(f"expected {kind.__name__}")


def case_rng_exact() -> None:
    raw = b'["EXP-ECDLP-651b94","control",[17,1,2,19,0,0,0],7,0]'
    got = driver.stream_digest(purpose="control", params=(17, 1, 2, 19, 0, 0, 0), seed=7, counter=0)
    assert got == int.from_bytes(hashlib.sha256(raw).digest(), "big")


def case_rng_n1() -> None:
    assert driver.rejection_draw(purpose="query", params=(17, 1, 2, 19, 0, 0, 0), seed=7, counter=9, n=1) == (0, 10)


def case_rng_rejects_bad_inputs(value: tuple[str, tuple[int, ...], int, int, int]) -> None:
    purpose, params, seed, counter, n = value
    expect_raises(Exception, lambda: driver.rejection_draw(purpose=purpose, params=params, seed=seed, counter=counter, n=n))


def case_pooled_zero_arm_charged() -> None:
    work, successes, cost = driver.pooled_null_cost([arm(100, 0), arm(60, 10), arm(60, 10)])
    assert (work, successes, cost) == (220, 20, 11.0)


def case_zero_coordinate_unavailable() -> None:
    out = driver.cell_difference(arm(50, 0), [arm(60, 10)])
    assert out["available"] is False and out["d"] is None and out["unavailable_reason"] == "coordinate_zero_success"


def case_zero_pool_unavailable() -> None:
    out = driver.cell_difference(arm(50, 10), [arm(100, 0), arm(60, 0)])
    assert out["available"] is False and out["d"] is None and out["unavailable_reason"] == "pooled_null_zero_success"


def case_unequal_success_pool() -> None:
    rows = [arm(10, 10), arm(99, 1), arm(10, 10), arm(10, 10), arm(10, 10), arm(10, 10), arm(10, 10)]
    work, successes, cost = driver.pooled_null_cost(rows)
    assert (work, successes) == (159, 61) and abs(cost - 159 / 61) < 1e-15


def case_decision(branch: str, mutate: Callable[[list[dict[str, Any]]], None] | None = None, value: float = 0.3) -> None:
    rows = decision_panel(value)
    if mutate:
        mutate(rows)
    assert driver.global_decision(rows)["branch"] == branch


def validity_mutation(name: str) -> None:
    c = controls()
    coordinate = arm()
    nulls = [arm()]
    if name == "coordinate_certificate": coordinate["failed_certificates"] = 1
    elif name == "null_certificate": nulls[0]["failed_certificates"] = 1
    elif name == "cayley": c["cayley"]["passed"] = False
    elif name == "relabel": c["relabel"] = False
    elif name == "occupancy": c["occupancy"] = False
    elif name == "constant_o_denominator": c["known_false"]["constant_o"]["nonzero_denominators"] = 1
    elif name == "constant_o_solve": c["known_false"]["constant_o"]["solves"] = 1
    elif name == "mutated_candidate": c["known_false"]["mutated_candidate_fails_certificate"] = False
    else: raise ValueError(name)
    assert driver.reduce_validity(coordinate, nulls, c)["valid"] is False


def case_failed_certificate_stops() -> None:
    class MockCurve:
        def scalar(self, scalar: int, _point: Any) -> Any:
            return (scalar, scalar)
    certificates: list[dict[str, Any]] = []
    invalid: list[dict[str, Any]] = []
    def repeated(_curve: Any, state: Any, _g: Any, _q: Any, a: int, b: int, _r: int, _assignment: Any) -> tuple[Any, int, int, str]:
        return state, a, b + 1, "add"
    with patch.object(driver, "rho_step", side_effect=repeated), patch.object(driver, "binary_verifier", return_value=(None, 0, 1)):
        expect_raises(
            driver.MeasurementInvalidStop,
            lambda: driver.collision_census(MockCurve(), (1, 1), (2, 2), 3, None, lambda: None, certificates.append, None, invalid.append),
        )
    assert len(certificates) == len(invalid) == 1 and invalid[0]["certificate"] == certificates[0]


def rss_input(text: str, expected: int | None) -> None:
    result = type("Result", (), {"stdout": text})()
    with patch.object(driver.os, "getpgid", return_value=7), patch.object(driver.os, "getpid", return_value=9), patch.object(driver.subprocess, "run", return_value=result):
        if expected is None:
            expect_raises(driver.InfrastructureStop, driver.process_group_rss_bytes)
        else:
            assert driver.process_group_rss_bytes() == expected


def case_measured_diagnostic_boundaries() -> None:
    rows: list[dict[str, Any]] = []
    with patch.object(driver, "process_group_rss_bytes", side_effect=[101, 202]):
        value, row = driver.measured_diagnostic("fixed", lambda: 7, rows.append)
    assert value == 7 and rows == [row] and row["completed"] is True
    assert row["process_group_rss_start_bytes"] == 101 and row["process_group_rss_end_bytes"] == 202
    assert row["process_group_rss_boundary_sample_max_bytes"] == 202
    assert "process_group_rss_peak_bytes" not in row


def case_measured_diagnostic_interruption() -> None:
    rows: list[dict[str, Any]] = []
    with patch.object(driver, "process_group_rss_bytes", side_effect=[202, 101]):
        expect_raises(driver.ResourceStop, lambda: driver.measured_diagnostic("fixed", lambda: (_ for _ in ()).throw(driver.ResourceStop("fixed")), rows.append))
    assert len(rows) == 1 and rows[0]["completed"] is False and "ResourceStop" in rows[0]["error"]


def case_write_chunks_bounded() -> None:
    sizes: list[int] = []
    class Sink:
        def write(self, value: bytes) -> None:
            sizes.append(len(value))
    driver.write_chunked(Sink(), b"x" * (2 * driver.MAX_SERIALIZATION_CHUNK_BYTES + 17))
    assert sizes == [driver.MAX_SERIALIZATION_CHUNK_BYTES, driver.MAX_SERIALIZATION_CHUNK_BYTES, 17]


def case_json_guard_interrupts() -> None:
    calls = 0
    def stop() -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise driver.CancellationStop("fixed")
    expect_raises(driver.CancellationStop, lambda: driver.json_bytes_chunked({"rows": list(range(100))}, check=stop))
    assert calls == 2


def case_json_has_no_whole_artifact_buffer() -> None:
    tree = ast.parse(Path(DRIVER_PATH).read_text(encoding="utf-8"))
    fn = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "json_bytes_chunked")
    has_bytearray = any(isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "bytearray" for node in ast.walk(fn))
    returns_bytes = any(isinstance(node, ast.Return) and isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name) and node.value.func.id == "bytes" for node in ast.walk(fn))
    assert not (has_bytearray and returns_bytes), "JSON fragments are accumulated into one bytearray and copied to one bytes object"


def case_yaml_is_streamed_before_materialization() -> None:
    calls = 0
    def check() -> None:
        nonlocal calls
        calls += 1
    with patch.object(driver.yaml, "safe_dump", side_effect=RuntimeError("monolithic serializer entered")):
        try:
            driver.yaml_bytes_chunked({"rows": list(range(1000))}, check=check)
        except RuntimeError:
            pass
    assert calls > 0, "yaml.safe_dump materializes the complete text before the first guarded chunk"


def case_artifact_builder_avoids_whole_payloads() -> None:
    source = ast.parse(Path(DRIVER_PATH).read_text(encoding="utf-8"))
    fn = next(node for node in source.body if isinstance(node, ast.FunctionDef) and node.name == "artifact_bytes")
    assigned_names: set[str] = set()
    for node in ast.walk(fn):
        if isinstance(node, ast.Assign):
            assigned_names.update(target.id for target in node.targets if isinstance(target, ast.Name))
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            assigned_names.add(node.target.id)
    forbidden = {"cost_rows", "raw_lines", "manifest_bytes", "fixtures_bytes", "controls_bytes", "certificates_bytes", "raw_result"}
    assert not forbidden.issubset(assigned_names), "artifact_bytes constructs multiple complete all-history payloads in memory"


def case_occupancy_stops_before_null_census() -> None:
    tree = ast.parse(Path(DRIVER_PATH).read_text(encoding="utf-8"))
    fn = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "future_cell")
    for node in ast.walk(fn):
        if isinstance(node, ast.For) and any(isinstance(call, ast.Call) and getattr(call.func, "id", None) == "occupancy_assignment" for call in ast.walk(node)):
            if any(isinstance(call, ast.Call) and getattr(call.func, "id", None) == "collision_census_with_custody" for call in ast.walk(node)):
                raise AssertionError("each null collision census runs before all seven assignments are occupancy-checked")


def case_relabel_stops_before_later_controls() -> None:
    source = ast.get_source_segment(DRIVER_PATH.read_text(encoding="utf-8"), next(node for node in ast.parse(DRIVER_PATH.read_text(encoding="utf-8")).body if isinstance(node, ast.FunctionDef) and node.name == "future_cell")) or ""
    relabel = source.index("relabel, relabel_cost")
    constant = source.index("constant_o, constant_o_cost")
    assert "MeasurementInvalidStop" in source[relabel:constant]


def case_progress_caps() -> None:
    with tempfile.TemporaryDirectory(prefix="validator-25dc56-progress-") as temporary:
        sink = driver.ProgressSink(Path(temporary))
        expect_raises(driver.ResourceStop, lambda: sink.record_progress({"event": "x", "payload": "y" * 2000}))
        assert not (Path(temporary) / "progress-events.jsonl").exists()
        sink.progress_bytes = driver.MAX_PROGRESS_LOG_BYTES - 5
        expect_raises(driver.ResourceStop, lambda: sink.record_progress({"event": "small"}))


def case_progress_append_and_latest() -> None:
    with tempfile.TemporaryDirectory(prefix="validator-25dc56-progress-") as temporary:
        sink = driver.ProgressSink(Path(temporary))
        sink.record_progress({"event": "one", "phase": "a", "index": 1})
        sink.record_progress({"event": "two", "phase": "b", "index": 2})
        events = (Path(temporary) / "progress-events.jsonl").read_text().splitlines()
        latest = json.loads((Path(temporary) / "progress-latest.json").read_text())
        assert len(events) == 2 and latest["event"] == "two"
        assert sink.progress_event_count == 2 and sink.progress_bytes == sum(len(line.encode()) + 1 for line in events)


def case_guard_persists_before_poll() -> None:
    order: list[str] = []
    class Probe:
        def should_probe(self) -> bool:
            order.append("eligibility")
            return True
        def check(self) -> None:
            order.append("poll")
    probe = Probe()
    driver.guarded_checkpoint(probe.check, 0, "fixed", lambda _row: order.append("persist"))
    assert order == ["eligibility", "persist", "poll"]


def case_guard_signal_every_opportunity() -> None:
    with tempfile.TemporaryDirectory(prefix="validator-25dc56-guard-") as temporary:
        guard = driver.Guard(driver.ProgressSink(Path(temporary)), cancelled=True)
        expect_raises(driver.CancellationStop, guard.should_probe)
        assert guard.guard_requests == 1


def case_progress_upper_bounds() -> None:
    cells = 4 * (len(driver.EXPLORATORY_SEEDS) + len(driver.HELDOUT_SEEDS)) * len(driver.US)
    max_r = 509
    certificate_events = cells * 8 * max_r
    transition_steps = cells * 8 * max_r * (max_r + 1)
    safe_events = driver.MAX_PROGRESS_LOG_BYTES // driver.MAX_PROGRESS_EVENT_BYTES
    assert cells == 192 and certificate_events == 781824 and transition_steps == 398730240
    assert safe_events == 262144 and certificate_events > safe_events


def case_operational_receipt_survives_success() -> None:
    source = Path(DRIVER_PATH).read_text(encoding="utf-8")
    fn = ast.get_source_segment(source, next(node for node in ast.parse(source).body if isinstance(node, ast.FunctionDef) and node.name == "run_future_pipeline")) or ""
    receipt = fn.index("retain_operational_completion(")
    cleanup = fn.index("shutil.rmtree(progress_dir)")
    assert cleanup < receipt, "success writes the required receipt in progress_dir and then deletes that entire tree"


def case_operational_receipt_is_durable_artifact() -> None:
    plan = json.loads(EXECUTION_PLAN_PATH.read_text(encoding="utf-8"))
    required = plan["future_operational_custody"]["required_post_boundary_receipt"]
    assert required == "progress/operational-completion.json"
    assert "operational-completion.json" in driver.EXPERIMENT_ARTIFACTS, "required completion receipt is outside the published artifact set"


def case_terminal_receipt_failure_preserves_original_stop() -> None:
    source = Path(DRIVER_PATH).read_text(encoding="utf-8")
    fn = ast.get_source_segment(source, next(node for node in ast.parse(source).body if isinstance(node, ast.FunctionDef) and node.name == "run_future_pipeline")) or ""
    typed = fn.index("except (CancellationStop, ResourceStop, InfrastructureStop) as exc:")
    generic = fn.index("except Exception as exc:", typed)
    block = fn[typed:generic]
    assert "try:" in block, "terminal receipt I/O can replace the original typed cancellation/resource/infrastructure stop"


def case_meter_finishes_after_publish() -> None:
    source = Path(DRIVER_PATH).read_text(encoding="utf-8")
    fn = ast.get_source_segment(source, next(node for node in ast.parse(source).body if isinstance(node, ast.FunctionDef) and node.name == "run_future_pipeline")) or ""
    assert fn.index("hashes = atomic_publish") < fn.index("meter.finish()")


def case_low_level_operational_receipt_shape() -> None:
    with tempfile.TemporaryDirectory(prefix="validator-25dc56-receipt-") as temporary:
        root = Path(temporary)
        sink = driver.ProgressSink(root)
        guard = driver.Guard(sink)
        meter = driver.ResourceMeter()
        target = driver.retain_operational_completion(root, meter=meter, guard=guard, state="fixed", payload_hashes={"x": "a" * 64}, error=None)
        record = json.loads(target.read_text())
        assert record["state"] == "fixed" and "timing_through_durable_payload" in record
        assert "self" in record["terminal_receipt_scope"]


def case_missing_payload_never_publishes_final() -> None:
    payload = {name: f"fixed:{name}\n".encode() for name in driver.EXPERIMENT_ARTIFACTS[:-1] if name != "raw-result.json"}
    with tempfile.TemporaryDirectory(prefix="validator-25dc56-publish-") as temporary:
        root = Path(temporary)
        expect_raises(ValueError, lambda: driver.atomic_publish(root, "unit-fixed", payload))
        assert not (root / "runs" / "unit-fixed").exists()


def case_atomic_stop_type(kind: type[BaseException]) -> None:
    payload = {name: f"fixed:{name}\n".encode() for name in driver.EXPERIMENT_ARTIFACTS[:-1]}
    with tempfile.TemporaryDirectory(prefix="validator-25dc56-publish-") as temporary:
        root = Path(temporary)
        expect_raises(kind, lambda: driver.atomic_publish(root, "unit-fixed", payload, check=lambda: (_ for _ in ()).throw(kind("fixed"))))


def case_quarantine_parent_fsync_truthful() -> None:
    with tempfile.TemporaryDirectory(prefix="validator-25dc56-quarantine-") as temporary:
        runs = Path(temporary) / "runs"; final = runs / "unit-fixed"; final.mkdir(parents=True)
        def fsync(path: Path) -> None:
            if path == runs: raise OSError("fixed parent fsync")
        with patch.object(driver, "fsync_directory", side_effect=fsync):
            result = driver.retain_publication_failure(runs=runs, run_id="unit-fixed", staging=runs/"staging", final=final, error=OSError("fixed"), phase="post_rename_durability")
        assert result["state"] == "quarantine_parent_fsync_failed" and result["quarantine_complete"] is False


def case_quarantine_receipt_failure_not_annotated() -> None:
    with tempfile.TemporaryDirectory(prefix="validator-25dc56-quarantine-") as temporary:
        runs = Path(temporary) / "runs"; final = runs / "unit-fixed"; final.mkdir(parents=True)
        with patch.object(Path, "write_bytes", side_effect=OSError("fixed receipt failure")):
            result = driver.retain_publication_failure(runs=runs, run_id="unit-fixed", staging=runs/"staging", final=final, error=OSError("fixed"), phase="post_rename_durability")
        assert result["receipt_written"] is False and result["state"] != "annotated_final"


def case_handlers_cover_assembly_and_publication() -> None:
    source = Path(DRIVER_PATH).read_text(encoding="utf-8")
    fn = ast.get_source_segment(source, next(node for node in ast.parse(source).body if isinstance(node, ast.FunctionDef) and node.name == "run_future_pipeline")) or ""
    assert fn.index("payload = artifact_bytes") < fn.index("signal.signal(signum, handler)")
    assert fn.index("hashes = atomic_publish") < fn.index("signal.signal(signum, handler)")


def case_invalid_cell_stops_before_next_cell() -> None:
    source = Path(DRIVER_PATH).read_text(encoding="utf-8")
    fn = ast.get_source_segment(source, next(node for node in ast.parse(source).body if isinstance(node, ast.FunctionDef) and node.name == "run_future_pipeline")) or ""
    recorded = fn.index("sink.record_cell(cell)")
    stopped = fn.index("raise MeasurementInvalidStop", recorded)
    assert recorded < stopped and "if not cell[\"validity\"][\"valid\"]" in fn[recorded:stopped]


def minimal_handoff(task_id: str, inputs: list[str], bindings: list[dict[str, str]], outputs: list[str], archive_id: str, plan: dict[str, Any] | None) -> dict[str, Any]:
    value: dict[str, Any] = {
        "id": task_id, "from": "coordinator", "to": "validator",
        "objective": "fixed governed source review", "uncertainty_reduced": "fixed admission",
        "inputs": inputs, "source_bindings": bindings,
        "constraints": ["fixed lower-level synthetic only"],
        "deliverables": outputs, "write_scope": outputs, "artifact_paths": outputs,
        "archived_by": archive_id, "completion_gate": ["three exact fixed outputs"],
        "budget": {"wall_clock_seconds": None, "memory_gb": 2, "maximum_runs": 0},
        "inference": {"policy": "review-adversarial", "reasoning_effort": "xhigh", "fallback_allowed": False, "degraded_allowed": False, "independent_session_required": True},
    }
    if plan is not None:
        value["review_plan"] = plan["review_plan"]
        value["review_plan_path"] = "coordination/review-plan.yaml"
    return value


@dataclass
class History:
    holder: tempfile.TemporaryDirectory[str]
    root: Path
    admission: dict[str, Any]
    reviewed: str
    executing: str
    queued_queue: dict[str, Any]
    final_queue: dict[str, Any]

    def close(self) -> None:
        self.holder.cleanup()


def commit_paths(root: Path, message: str, paths: list[str], allow_empty: bool = False) -> str:
    if paths:
        subprocess.run(["git", "-C", str(root), "add", "--", *paths], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    args = ["git", "-C", str(root), "commit", "-q", "-m", message]
    if allow_empty:
        args.insert(-2, "--allow-empty")
    subprocess.run(args, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return str(git(root, "rev-parse", "HEAD"))


def write_file(root: Path, relative: str, data: bytes) -> None:
    target = root / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)


def build_history(*, mutation: str | None = None) -> History:
    holder = tempfile.TemporaryDirectory(prefix="validator-25dc56-history-")
    root = Path(holder.name).resolve()
    subprocess.run(["git", "-C", str(root), "init", "-q", "-b", "main"], check=True)
    subprocess.run(["git", "-C", str(root), "config", "user.name", "Fresh Validator Fixture"], check=True)
    subprocess.run(["git", "-C", str(root), "config", "user.email", "validator@example.test"], check=True)
    review_id = "TASK-20260908-abc123"
    archive_id = "TASK-20260908-def456"
    outputs = [f"coordination/reviews/{review_id}/review.yaml", f"coordination/reviews/{review_id}/checks.py", f"coordination/reviews/{review_id}/check-receipt.json"]
    receipt_rel = f"coordination/archives/{archive_id}/snapshot.json"
    queue_rel = "coordination/dispatch_queue.json"
    plan_rel = "coordination/review-plan.yaml"
    claim_rel = f"coordination/claims/{review_id}.1.claim.json"
    release_rel = f"coordination/claims/{review_id}.1.release.json"
    source_payloads = {
        DRIVER_REL: b"fixed reviewed driver\n",
        EXECUTION_PLAN_REL: b"{}\n",
        "experiments/EXP-ECDLP-651b94/specification.yaml": b"fixed specification\n",
        "experiments/EXP-ECDLP-651b94/amendments/DEC-20260907-38017a.yaml": b"fixed amendment\n",
        driver.DISPATCH_VALIDATOR_RELATIVE_PATH: (ROOT / driver.DISPATCH_VALIDATOR_RELATIVE_PATH).read_bytes(),
        driver.GOAL_LANES_RELATIVE_PATH: (ROOT / driver.GOAL_LANES_RELATIVE_PATH).read_bytes(),
    }
    for path, data in source_payloads.items(): write_file(root, path, data)
    reviewed = commit_paths(root, "reviewed source", list(source_payloads))
    inputs = list(source_payloads)
    bindings = [{"path": path, "sha256": digest(data)} for path, data in source_payloads.items()]
    if mutation == "binding_digest_mismatch": bindings[0]["sha256"] = "f" * 64
    joint = "Corrected executable spectral protocol and admission/custody conformance"
    plan: dict[str, Any] = {"review_plan": {
        "claim_under_review": "fixed source admission", "coordinator_prior": "fixed prior",
        "recorded_before_reviewers": True, "source_snapshot": reviewed,
        "joints": [{"joint": joint, "assigned_to": review_id, "attack_plan": "fixed attack", "breaking_artifact": "fixed artifact"}],
        "blindness": {"mutual": False, "lifted_for": [review_id], "rationale": "fixed hardening"},
        "proves_too_much": {"objects": ["fixed false object"], "failure_signature": "must reject", "assigned_to": review_id},
        "blind_rederivation": {"required": False, "quantity": "fixed", "parameters": "fixed", "blind_from": [], "assigned_to": review_id},
        "procedure_deviations": [],
    }}
    if mutation == "incomplete_plan_sections":
        plan["review_plan"]["blindness"] = {}
        plan["review_plan"]["proves_too_much"] = {}
    handoff = minimal_handoff(review_id, inputs, bindings, outputs, archive_id, None if mutation == "missing_nested_review_plan" else plan)
    archive_handoff = {
        "objective": "fixed archive", "uncertainty_reduced": "fixed custody", "inputs": outputs,
        "constraints": ["fixed"], "deliverables": [receipt_rel], "completion_gate": ["exact archive"],
        "budget": {"wall_clock_seconds": None, "memory_gb": None, "maximum_runs": 0},
        "inference": {"policy": "coordinator-orchestration-code", "reasoning_effort": "high"},
    }
    review_task = {"id": review_id, "title": "fixed review", "role": "validator", "state": "queued", "priority": 90, "review_required": False, "depends_on": [], "read_scope": inputs, "write_scope": outputs, "artifact_paths": outputs, "handoff": handoff}
    archive_task = {"id": archive_id, "title": "fixed archive", "role": "coordinator", "state": "queued", "priority": 89, "review_required": False, "depends_on": [review_id], "read_scope": outputs, "write_scope": [receipt_rel], "artifact_paths": [receipt_rel], "handoff": archive_handoff, "archive": {"kind": "snapshot", "source_task_ids": [review_id], "commit_sha": None, "parent_sha": None, "path_sha256": {}, "record_ids": [archive_id, review_id]}}
    queued = {"schema": "crypto.autoresearch.dispatch_queue.v1", "objective": "fixed governed lifecycle", "max_concurrent": 1, "tasks": [review_task, archive_task]}
    write_file(root, plan_rel, yaml.safe_dump(plan, sort_keys=False).encode())
    write_file(root, queue_rel, (json.dumps(queued, sort_keys=True) + "\n").encode())
    plan_commit = commit_paths(root, "precommit plan and queue", [plan_rel, queue_rel])
    # Intentional unrelated authority between the plan and claim.  Ancestry,
    # rather than direct-parent equality, is the correct lifecycle relation.
    write_file(root, "coordination/unrelated-runtime-authority.txt", b"fixed unrelated authority\n")
    commit_paths(root, "unrelated runtime authority", ["coordination/unrelated-runtime-authority.txt"])
    claim = {"schema": "crypto.autoresearch.task_claim.v1", "task_id": review_id, "epoch": 1, "owner": "fixed-owner", "session": "fixed-session", "branch": "main", "worktree": str(root), "acquired_at": "2026-09-09T00:00:00Z", "expires_at": "2026-09-09T01:00:00Z", "write_scope": outputs, "supersedes": None, "forced": False}
    write_file(root, claim_rel, (json.dumps(claim, sort_keys=True) + "\n").encode())
    claim_commit = commit_paths(root, "claim review", [claim_rel])
    source_reads = {path: digest(data) for path, data in source_payloads.items()}
    report = {"validation_report": {
        "id": review_id, "task_id": review_id, "role": "validator", "source_snapshot_commit": reviewed,
        "review_plan_path": plan_rel, "review_plan_commit": plan_commit,
        "claim_commit": claim_commit, "claim_owner": "fixed-owner", "claim_session": "fixed-session", "claim_epoch": 1,
        "artifact_paths": outputs, "owned_joint_verdict": "PASS", "verdict": "passed",
        "inference": {"requested_policy": "review-adversarial", "resolved_model_id": "fixed-independent-model", "reasoning_effort": "xhigh", "independent_session": True, "fallback_used": False, "degraded_used": False, "bedrock_used": False, "provenance": "fixed native fixture"},
        "review_attestation": {"task_id": review_id, "joints_owned": [joint], "complete_source_read": True, "review_plan_path": plan_rel, "source_reads": source_reads, "sources_read": list(source_reads), "read_sibling_reports": False, "blind_from_respected": None, "verdict": "holds"},
    }}
    if mutation == "contradictory_attestation": report["validation_report"]["review_attestation"]["verdict"] = "breaks"
    payloads = {outputs[0]: yaml.safe_dump(report, sort_keys=False).encode(), outputs[1]: b"# fixed checker\n", outputs[2]: b'{"fixed":true}\n'}
    output_hashes = {path: digest(data) for path, data in payloads.items()}
    release_hashes = dict(output_hashes)
    if mutation == "release_hashes_empty": release_hashes = {}
    elif mutation == "release_hashes_wrong": release_hashes = {path: "f" * 64 for path in outputs}
    elif mutation == "release_hashes_partial": release_hashes = {outputs[0]: output_hashes[outputs[0]]}
    release = {"schema": "crypto.autoresearch.task_release.v1", "task_id": review_id, "epoch": 1, "owner": "fixed-owner", "outcome": "completed", "released_at": "2026-09-09T00:10:00Z", "was_expired": False, "note": "fixed", "artifact_sha256": release_hashes}
    write_file(root, release_rel, (json.dumps(release, sort_keys=True) + "\n").encode())
    release_commit = commit_paths(root, "release review", [release_rel])
    for path, data in payloads.items(): write_file(root, path, data)
    receipt = {"schema": "crypto.autoresearch.review_snapshot.v1", "task_id": archive_id, "source_task_ids": [review_id], "parent_sha": release_commit, "source_path_sha256": output_hashes}
    write_file(root, receipt_rel, (json.dumps(receipt, sort_keys=True) + "\n").encode())
    archive_commit = commit_paths(root, "archive review", list(payloads) + [receipt_rel])
    archive_hashes = {**output_hashes, receipt_rel: digest((root / receipt_rel).read_bytes())}
    final = copy.deepcopy(queued)
    final_review, final_archive = final["tasks"]
    final_review["state"] = "completed"
    if mutation == "changed_completed_dependencies": final_review["depends_on"] = ["TASK-UNKNOWN-dead00"]
    final_archive["state"] = "completed"
    final_archive["archive"].update({"commit_sha": archive_commit, "parent_sha": release_commit, "path_sha256": archive_hashes})
    if mutation == "extra_invalid_queue_task": final["tasks"].append({"id": "TASK-BAD-abcdef", "role": "not-a-role"})
    write_file(root, queue_rel, (json.dumps(final, sort_keys=True) + "\n").encode())
    external = commit_paths(root, "external authority", [queue_rel])
    executing = commit_paths(root, "executing descendant", [], allow_empty=True)
    admission = {
        "external_authority_commit": external, "external_queue_path": queue_rel, "external_queue_sha256": digest((root / queue_rel).read_bytes()),
        "archive_task_id": archive_id, "archive_commit": archive_commit, "snapshot_receipt_path": receipt_rel, "snapshot_receipt_sha256": archive_hashes[receipt_rel],
        "review_task_id": review_id, "review_report_path": outputs[0], "review_report_sha256": output_hashes[outputs[0]],
        "review_plan_path": plan_rel, "review_plan_commit": plan_commit, "review_plan_sha256": digest(git_blob(root, plan_commit, plan_rel)),
        "reviewed_source_snapshot": reviewed, "required_verdict": "PASS",
        "review_claim_path": claim_rel, "review_claim_sha256": digest(git_blob(root, claim_commit, claim_rel)), "review_claim_commit": claim_commit,
        "review_release_path": release_rel, "review_release_sha256": digest(git_blob(root, release_commit, release_rel)), "review_release_commit": release_commit,
    }
    return History(holder, root, admission, reviewed, executing, queued, final)


@contextmanager
def patched_history(history: History) -> Iterator[None]:
    with patch.object(driver, "ROOT", history.root):
        yield


class TempRepositoryVerifier:
    def __init__(self, root: Path): self.root = root
    def verify_archive(self, task: dict[str, Any], expected_paths: list[str]) -> None:
        archive = task["archive"]
        commit = archive["commit_sha"]
        changed = set(filter(None, str(git(self.root, "diff-tree", "--no-commit-id", "--name-only", "-r", commit)).splitlines()))
        assert changed == set(expected_paths) == set(archive["path_sha256"])
        assert str(git(self.root, "rev-parse", f"{commit}^")) == archive["parent_sha"]
        for path, expected in archive["path_sha256"].items(): assert digest(git_blob(self.root, commit, path)) == expected


def admission_result(mutation: str | None = None) -> tuple[bool, dict[str, Any]]:
    history = build_history(mutation=mutation)
    details: dict[str, Any] = {}
    try:
        if mutation is None:
            research_dispatch.validate_queue(copy.deepcopy(history.queued_queue))
            research_dispatch.validate_queue(copy.deepcopy(history.final_queue), repository_verifier=TempRepositoryVerifier(history.root))
            details["canonical_queued_and_completed_validation"] = "PASS"
        with patched_history(history):
            driver.verify_review_admission(history.admission, history.reviewed, history.executing)
        return True, details
    except driver.LaunchRefused as exc:
        details["launch_refused"] = str(exc)
        return False, details
    finally:
        history.close()


def case_governed_lifecycle_reachable() -> None:
    accepted, details = admission_result()
    assert accepted and details.get("canonical_queued_and_completed_validation") == "PASS"


def malformed_admission_must_refuse(mutation: str) -> None:
    accepted, _details = admission_result(mutation)
    assert not accepted, f"malformed lifecycle admitted: {mutation}"


@dataclass(frozen=True)
class Case:
    name: str
    action: Callable[[], None]


def drop_last(rows: list[dict[str, Any]]) -> None: rows.pop()
def invalidate_first(rows: list[dict[str, Any]]) -> None: rows[0]["validity"]["valid"] = False
def unavailable_first(rows: list[dict[str, Any]]) -> None: rows[0]["metric"] = {"available": False, "d": None}
def below_u(rows: list[dict[str, Any]]) -> None:
    for row in rows:
        if row["u"] == 3: row["metric"]["d"] = 0.1
def nonpositive_curve(rows: list[dict[str, Any]]) -> None:
    for row in rows:
        if row["u"] == 1 and row["curve_id"] == "c0": row["metric"]["d"] = 0.0
def mixed(rows: list[dict[str, Any]]) -> None:
    rows[0]["metric"]["d"] = 0.1
    rows[1]["metric"]["d"] = -0.1


CASES: list[Case] = [
    Case("rng_exact_serialization", case_rng_exact),
    Case("rng_n_one_consumes_one_digest", case_rng_n1),
    *[Case(f"rng_rejects_{index}", lambda value=value: case_rng_rejects_bad_inputs(value)) for index, value in enumerate([
        ("bad", (17,1,2,19,0,0,0), 1, 0, 3),
        ("query", (17,1,2), 1, 0, 3),
        ("query", (17,1,2,19,0,0,0), -1, 0, 3),
        ("query", (17,1,2,19,0,0,0), 1, -1, 3),
        ("query", (17,1,2,19,0,0,0), 1, 0, 0),
    ], 1)],
    Case("pooled_zero_arm_work_retained", case_pooled_zero_arm_charged),
    Case("zero_coordinate_success_unavailable", case_zero_coordinate_unavailable),
    Case("zero_pooled_null_success_unavailable", case_zero_pool_unavailable),
    Case("unequal_successes_use_direct_pool", case_unequal_success_pool),
    Case("complete_positive_panel", lambda: case_decision("positive")),
    Case("complete_negative_panel", lambda: case_decision("negative", value=0.0)),
    Case("mixed_panel_inconclusive", lambda: case_decision("inconclusive", mixed, value=0.0)),
    Case("missing_panel_inconclusive", lambda: case_decision("inconclusive", drop_last)),
    Case("invalid_panel_inconclusive", lambda: case_decision("inconclusive", invalidate_first)),
    Case("unavailable_panel_inconclusive", lambda: case_decision("inconclusive", unavailable_first)),
    Case("one_coordinate_below_threshold", lambda: case_decision("inconclusive", below_u)),
    Case("one_curve_nonpositive", lambda: case_decision("inconclusive", nonpositive_curve)),
    *[Case(f"validity_rejects_{name}", lambda name=name: validity_mutation(name)) for name in (
        "coordinate_certificate", "null_certificate", "cayley", "relabel", "occupancy",
        "constant_o_denominator", "constant_o_solve", "mutated_candidate",
    )],
    Case("failed_scalar_certificate_retained_and_stops", case_failed_certificate_stops),
    Case("rss_empty_refused", lambda: rss_input("", None)),
    Case("rss_malformed_refused", lambda: rss_input("9 7\n", None)),
    Case("rss_nonnumeric_refused", lambda: rss_input("9 7 x\n", None)),
    Case("rss_missing_current_refused", lambda: rss_input("10 7 8\n", None)),
    Case("rss_wrong_group_refused", lambda: rss_input("9 8 8\n10 7 8\n", None)),
    Case("rss_matching_group_summed", lambda: rss_input("9 7 12\n10 7 8\n", 20 * 1024)),
    Case("diagnostic_boundary_rss_truthful", case_measured_diagnostic_boundaries),
    Case("interrupted_diagnostic_retained_once", case_measured_diagnostic_interruption),
    Case("write_chunks_at_most_64k", case_write_chunks_bounded),
    Case("json_guard_can_interrupt", case_json_guard_interrupts),
    Case("json_no_whole_artifact_buffer", case_json_has_no_whole_artifact_buffer),
    Case("yaml_guard_precedes_materialization", case_yaml_is_streamed_before_materialization),
    Case("artifact_builder_avoids_whole_payloads", case_artifact_builder_avoids_whole_payloads),
    Case("occupancy_stops_before_null_census", case_occupancy_stops_before_null_census),
    Case("relabel_stops_before_later_controls", case_relabel_stops_before_later_controls),
    Case("progress_event_and_log_caps_fail_closed", case_progress_caps),
    Case("progress_append_log_and_compact_latest", case_progress_append_and_latest),
    Case("guard_persists_coordinates_before_poll", case_guard_persists_before_poll),
    Case("guard_checks_signal_at_opportunity", case_guard_signal_every_opportunity),
    Case("full_panel_progress_and_work_bounds", case_progress_upper_bounds),
    Case("operational_receipt_survives_success", case_operational_receipt_survives_success),
    Case("operational_receipt_is_published_artifact", case_operational_receipt_is_durable_artifact),
    Case("terminal_receipt_failure_preserves_typed_stop", case_terminal_receipt_failure_preserves_original_stop),
    Case("timing_finishes_after_payload_publication", case_meter_finishes_after_publish),
    Case("low_level_operational_receipt_shape", case_low_level_operational_receipt_shape),
    Case("missing_payload_never_publishes_final", case_missing_payload_never_publishes_final),
    Case("atomic_publication_preserves_cancellation", lambda: case_atomic_stop_type(driver.CancellationStop)),
    Case("atomic_publication_preserves_resource_stop", lambda: case_atomic_stop_type(driver.ResourceStop)),
    Case("quarantine_parent_fsync_is_non_durable", case_quarantine_parent_fsync_truthful),
    Case("failed_quarantine_receipt_not_annotated", case_quarantine_receipt_failure_not_annotated),
    Case("signal_handlers_cover_assembly_publication", case_handlers_cover_assembly_and_publication),
    Case("invalid_cell_retained_then_stops", case_invalid_cell_stops_before_next_cell),
    Case("governed_queued_release_archive_reachable", case_governed_lifecycle_reachable),
    Case("empty_release_hashes_refused", lambda: malformed_admission_must_refuse("release_hashes_empty")),
    Case("wrong_release_hashes_refused", lambda: malformed_admission_must_refuse("release_hashes_wrong")),
    Case("partial_release_hashes_refused", lambda: malformed_admission_must_refuse("release_hashes_partial")),
    Case("contradictory_attestation_refused", lambda: malformed_admission_must_refuse("contradictory_attestation")),
    Case("wrong_handoff_binding_digest_refused", lambda: malformed_admission_must_refuse("binding_digest_mismatch")),
    Case("missing_nested_review_plan_refused", lambda: malformed_admission_must_refuse("missing_nested_review_plan")),
    Case("incomplete_plan_sections_refused", lambda: malformed_admission_must_refuse("incomplete_plan_sections")),
    Case("changed_completed_dependencies_refused", lambda: malformed_admission_must_refuse("changed_completed_dependencies")),
    Case("extra_invalid_queue_task_refused", lambda: malformed_admission_must_refuse("extra_invalid_queue_task")),
]


class CaseTimeout(RuntimeError): pass
def timeout_handler(_signum: int, _frame: Any) -> None: raise CaseTimeout("fixed case exceeded 10 seconds")


def ru_maxrss_bytes() -> int:
    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    # Darwin reports bytes; Linux reports KiB.  Preserve the platform scope.
    return value if sys.platform == "darwin" else value * 1024


def main() -> int:
    if len(CASES) > MAX_TOTAL_CASES: raise RuntimeError("case inventory exceeds 640")
    signal.signal(signal.SIGALRM, timeout_handler)
    admin = administrative_bindings()
    if not admin["all_bindings_matched"]: raise RuntimeError("source binding mismatch before fixed cases")
    start_wall = time.monotonic()
    start_cpu = time.process_time()
    start_rss = ru_maxrss_bytes()
    results: list[dict[str, Any]] = []
    for case in CASES:
        wall = time.monotonic(); cpu = time.process_time(); rss = ru_maxrss_bytes()
        signal.alarm(CASE_TIMEOUT_SECONDS)
        outcome = "PASS"; detail = "fixed obligation held"
        try:
            case.action()
        except AssertionError as exc:
            outcome, detail = "FAIL", f"AssertionError: {exc}"
        except Exception as exc:
            outcome, detail = "ERROR", f"{type(exc).__name__}: {exc}"
        finally:
            signal.alarm(0)
        results.append({
            "name": case.name, "outcome": outcome, "detail": detail,
            "wall_seconds": round(time.monotonic() - wall, 6),
            "cpu_seconds": round(time.process_time() - cpu, 6),
            "ru_maxrss_scope": "process_lifetime_high_water_at_case_boundaries",
            "ru_maxrss_start_bytes": rss, "ru_maxrss_end_bytes": ru_maxrss_bytes(),
        })
    failed = [row for row in results if row["outcome"] == "FAIL"]
    errors = [row for row in results if row["outcome"] == "ERROR"]
    record = {
        "schema": "crypto.autoresearch.independent_source_admission_checks.v2",
        "task_id": TASK_ID, "source_task_id": SOURCE_TASK_ID,
        "source_snapshot_commit": SOURCE_SNAPSHOT, "review_authority_commit": AUTHORITY_COMMIT,
        "published_claim_commit": CLAIM_COMMIT,
        "scope": "one source/admission/custody joint; fixed static/arithmetic/synthetic/mock/temporary-Git cases only",
        "pre_reservation": {"suite_invocations_reserved": 1, "complete_suite_cases_reserved": len(CASES), "prior_case_executions": 0, "remaining_after_reservation": MAX_TOTAL_CASES - len(CASES)},
        "limits": {"maximum_total_case_executions_including_failures_and_reruns": MAX_TOTAL_CASES, "maximum_seconds_per_case": CASE_TIMEOUT_SECONDS, "maximum_aggregate_wall_cpu_seconds": 1800, "maximum_workers": 1, "memory_limit_bytes": MEMORY_LIMIT_BYTES, "scientific_runs": 0},
        "administrative_checks": admin,
        "actual": {
            "suite_invocations": 1, "case_executions_including_failures_and_reruns": len(results),
            "passed": len(results) - len(failed) - len(errors), "failed": len(failed), "errors": len(errors),
            "timeouts": sum("CaseTimeout" in row["detail"] for row in results),
            "internal_wall_seconds": round(time.monotonic() - start_wall, 6),
            "internal_cpu_seconds": round(time.process_time() - start_cpu, 6),
            "maximum_case_wall_seconds": max((row["wall_seconds"] for row in results), default=0),
            "maximum_case_cpu_seconds": max((row["cpu_seconds"] for row in results), default=0),
            "ru_maxrss_scope": "process_lifetime_high_water_at_suite_boundaries",
            "ru_maxrss_start_bytes": start_rss, "ru_maxrss_end_bytes": ru_maxrss_bytes(),
            "maximum_workers": 1,
        },
        "forbidden_work_executed": {"scientific_fixture_or_candidate_search": 0, "scientific_collision_census": 0, "scientific_null_control_or_timing_panel": 0, "sage_or_pari": 0, "prospective_pipeline_or_entrypoint": 0, "real_key_signature_nonce_lock": 0, "real_run_allocation_or_production_RUN_directory": 0},
        "full_panel_static_bounds": {"cells": 192, "max_subgroup_order": 509, "certificate_completion_events_upper_bound": 781824, "transition_steps_upper_bound": 398730240, "safe_progress_event_cap": 262144, "interpretation": "The cap is a safe operational stop, not a full-panel completion claim; no scientific work was executed."},
        "results": results,
    }
    print(json.dumps(record, sort_keys=True))
    return 2 if errors else 1 if failed else 0


if __name__ == "__main__": raise SystemExit(main())
