#!/usr/bin/env python3
"""Fresh fixed S6 source-conformance checks for TASK-20260908-707dff.

The suite imports the archived S6 production helpers directly.  It reuses the
historical independent S5 fixture constructor only as a source-pinned governed
Git-history generator, replaces all production-module bindings with S6, and
owns every expectation below.  Producer regressions are parsed for custody but
are never executed or credited as independent evidence.

Only fixed static, arithmetic, synthetic-Git, streaming, custody, and temporary
artifact checks run.  No fixture search, collision census, scientific/null/
control/timing panel, prospective pipeline, launch admission, key, signature,
nonce, lock, run allocation, or RUN directory is invoked.
"""
from __future__ import annotations

import ast
import contextlib
import hashlib
import importlib.util
import io
import json
import os
import platform
import resource
import signal
import subprocess
import sys
import tempfile
import time
import types
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterator
from unittest.mock import patch

import yaml


TASK_ID = "TASK-20260908-707dff"
AUTHORITY_COMMIT = "466e65b77eb5506563989ef2b61c0b45a09f3386"
PUBLISHED_CLAIM_COMMIT = "42e39633d8c93f521db38822a0d9bcac214c1fb3"
SOURCE_SNAPSHOT = "c48a335b37aa7f5da9e71ae289d426806b8343d5"
SOURCE_TASK = "TASK-20260908-5c0cc3"
BASELINE_TASK = "TASK-20260908-e34baf"
ROOT = Path(__file__).resolve().parents[5]
HANDOFF = ROOT / f"ledger/handoffs/{TASK_ID}.yaml"
PLAN_REL = f"coordination/experiment-reserve/BATCH-1bb183/review-plan-{TASK_ID}.yaml"
CLAIM_REL = f"coordination/experiment-reserve/BATCH-1bb183/claims/{TASK_ID}.1.claim.json"
SNAPSHOT_REL = "coordination/experiment-reserve/BATCH-1bb183/archives/TASK-20260908-69f5db/snapshot.json"
IMPL = ROOT / f"experiments/EXP-ECDLP-651b94/implementation/{SOURCE_TASK}"
BASELINE = ROOT / f"experiments/EXP-ECDLP-651b94/implementation/{BASELINE_TASK}"
HISTORICAL_CHECK = ROOT / "coordination/experiment-reserve/BATCH-1bb183/reviews/TASK-20260908-1367aa/checks.py"
OUTER_REPO_UNINTENDED = Path("/Volumes/SSD990/crypto-autoresearcher") / IMPL.relative_to(ROOT)

sys.dont_write_bytecode = True


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git(repo: Path, *args: str, binary: bool = False) -> str | bytes:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return completed.stdout if binary else completed.stdout.decode().strip()


def git_blob(repo: Path, commit: str, relative: str) -> bytes:
    return git(repo, "show", f"{commit}:{relative}", binary=True)  # type: ignore[return-value]


def load_module(name: str, path: Path) -> types.ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


# The historical validator checker is a declared, hash-bound input.  Its
# governed Git fixture is retained, but all runtime lookups below are rebound
# to the S6 production modules before any case executes.
historical = load_module("_historical_validator_1367aa", HISTORICAL_CHECK)
streaming = load_module("streaming", IMPL / "streaming.py")
custody = load_module("custody", IMPL / "custody.py")
driver = load_module("driver", IMPL / "driver.py")
historical.ROOT = ROOT
historical.IMPL = IMPL
historical.driver = driver
historical.streaming = streaming
historical.custody = custody


def full_input_audit() -> dict[str, Any]:
    handoff_bytes = HANDOFF.read_bytes()
    handoff = yaml.safe_load(handoff_bytes)["handoff"]
    inputs = handoff["inputs"]
    bindings = handoff["source_bindings"]
    if len(inputs) != 115 or len(bindings) != 115:
        raise AssertionError("expected exactly 115 declared inputs and bindings")
    if inputs != [row["path"] for row in bindings] or len(set(inputs)) != len(inputs):
        raise AssertionError("input/source-binding inventory is not exact, ordered, and unique")

    parsed = {"python": 0, "json": 0, "yaml": 0, "text": 0}
    reads: dict[str, str] = {}
    bytes_read = 0
    source_matches = 0
    source_missing: list[str] = []
    governing_commits: dict[str, str] = {}
    for row in bindings:
        relative = row["path"]
        expected = row["sha256"]
        live = (ROOT / relative).read_bytes()
        bytes_read += len(live)
        observed = digest(live)
        if observed != expected:
            raise AssertionError(f"live binding mismatch: {relative}")
        if digest(git_blob(ROOT, AUTHORITY_COMMIT, relative)) != expected:
            raise AssertionError(f"authority binding mismatch: {relative}")
        if digest(git_blob(ROOT, PUBLISHED_CLAIM_COMMIT, relative)) != expected:
            raise AssertionError(f"claim binding mismatch: {relative}")
        governing = AUTHORITY_COMMIT if relative == PLAN_REL else SOURCE_SNAPSHOT
        governing_commits[relative] = governing
        try:
            source_data = git_blob(ROOT, SOURCE_SNAPSHOT, relative)
        except subprocess.CalledProcessError:
            source_missing.append(relative)
        else:
            source_matches += 1
            if relative == PLAN_REL or digest(source_data) != expected:
                raise AssertionError(f"source snapshot origin mismatch: {relative}")
        if digest(git_blob(ROOT, governing, relative)) != expected:
            raise AssertionError(f"governing-commit binding mismatch: {relative}")

        suffix = Path(relative).suffix
        if suffix == ".py":
            ast.parse(live, filename=relative)
            parsed["python"] += 1
        elif suffix == ".json":
            json.loads(live)
            parsed["json"] += 1
        elif suffix in {".yaml", ".yml"}:
            yaml.safe_load(live)
            parsed["yaml"] += 1
        else:
            live.decode("utf-8")
            parsed["text"] += 1
        reads[relative] = observed

    if source_matches != 114 or source_missing != [PLAN_REL]:
        raise AssertionError(f"unexpected source/plan split: {source_matches}, {source_missing}")
    if git(ROOT, "merge-base", "--is-ancestor", SOURCE_SNAPSHOT, AUTHORITY_COMMIT) != "":
        raise AssertionError("source does not precede authority")
    if git(ROOT, "merge-base", "--is-ancestor", AUTHORITY_COMMIT, PUBLISHED_CLAIM_COMMIT) != "":
        raise AssertionError("authority does not precede published claim")
    plan_origins = str(git(
        ROOT, "log", "--format=%H", "--diff-filter=A", AUTHORITY_COMMIT, "--", PLAN_REL
    )).splitlines()
    if plan_origins != [AUTHORITY_COMMIT]:
        raise AssertionError(f"review plan first-add origin differs: {plan_origins}")
    if git(ROOT, "rev-parse", f"{PUBLISHED_CLAIM_COMMIT}^") != AUTHORITY_COMMIT:
        raise AssertionError("published claim is not the authority child")
    claim_changed = str(git(
        ROOT, "diff-tree", "--no-commit-id", "--name-only", "-r", PUBLISHED_CLAIM_COMMIT
    )).splitlines()
    if claim_changed != [CLAIM_REL]:
        raise AssertionError(f"published claim changed unexpected paths: {claim_changed}")

    snapshot = json.loads(git_blob(ROOT, SOURCE_SNAPSHOT, SNAPSHOT_REL))
    changed = set(filter(None, str(git(
        ROOT, "diff-tree", "--no-commit-id", "--name-only", "-r", SOURCE_SNAPSHOT
    )).splitlines()))
    expected_changed = set(snapshot["source_path_sha256"]) | {SNAPSHOT_REL}
    if changed != expected_changed or len(snapshot["source_path_sha256"]) != 8:
        raise AssertionError("S6 snapshot changed-path inventory is not exact")
    for relative, expected in snapshot["source_path_sha256"].items():
        if digest(git_blob(ROOT, SOURCE_SNAPSHOT, relative)) != expected:
            raise AssertionError(f"S6 snapshot receipt hash mismatch: {relative}")

    report = yaml.safe_load((IMPL / "implementation-report.yaml").read_bytes())["execution_report"]
    plan = json.loads((IMPL / "execution-plan.json").read_bytes())
    producer_receipt = json.loads((IMPL / "regression-receipt.json").read_bytes())
    attempts = producer_receipt.get("attempts", [])
    producer_rows = sum(
        len(row.get("stdout_parsed_complete_json", {}).get("results", []))
        for row in attempts
    )
    if report["implementation_commit"] is not None or plan["implementation_commit"] is not None:
        raise AssertionError("pre-snapshot metadata invented an implementation commit")
    if report["checkout_base"] == SOURCE_SNAPSHOT or plan["checkout_base"] == SOURCE_SNAPSHOT:
        raise AssertionError("checkout base was substituted for the implementation snapshot")
    if report["protocol_deviations"][0]["kind"] != "operational_path_resolution":
        raise AssertionError("wrong-checkout copy/removal disclosure is absent")
    if OUTER_REPO_UNINTENDED.exists():
        raise AssertionError(f"disclosed unintended checkout path is present: {OUTER_REPO_UNINTENDED}")

    return {
        "handoff_sha256": digest(handoff_bytes),
        "declared_input_count": len(inputs),
        "declared_input_bytes_read": bytes_read,
        "live_binding_matches": len(inputs),
        "authority_binding_matches": len(inputs),
        "published_claim_binding_matches": len(inputs),
        "source_snapshot_binding_matches": source_matches,
        "source_snapshot_missing_paths": source_missing,
        "governing_commit_counts": {
            SOURCE_SNAPSHOT: sum(value == SOURCE_SNAPSHOT for value in governing_commits.values()),
            AUTHORITY_COMMIT: sum(value == AUTHORITY_COMMIT for value in governing_commits.values()),
        },
        "plan_first_add_commit": plan_origins[0],
        "parsed_input_types": parsed,
        "source_reads": reads,
        "snapshot_changed_paths": sorted(changed),
        "snapshot_source_artifact_count": len(snapshot["source_path_sha256"]),
        "producer_receipt_attempt_count": len(attempts),
        "producer_receipt_case_rows": producer_rows,
        "producer_receipt_used_as_independent_evidence": False,
        "producer_disclosed_wrong_checkout_copy_removal": True,
        "unintended_checkout_path_currently_absent": True,
    }


def normalized_module(path: Path, *, omitted: set[str], assignments: set[str]) -> str:
    tree = ast.parse(path.read_bytes(), filename=str(path))
    body: list[ast.stmt] = []
    for node in tree.body:
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            continue
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.name in omitted:
            continue
        if isinstance(node, ast.Assign):
            names = {target.id for target in node.targets if isinstance(target, ast.Name)}
            if names & assignments:
                continue
        body.append(node)
    tree.body = body
    return ast.dump(tree, include_attributes=False)


def case_scientific_driver_preserved() -> None:
    omitted = {"verify_review_admission", "protocol_coverage"}
    assignments = {"TASK_ID", "CORRECTION_DECISION_ID"}
    assert normalized_module(BASELINE / "driver.py", omitted=omitted, assignments=assignments) == normalized_module(
        IMPL / "driver.py", omitted=omitted, assignments=assignments
    )


def case_streaming_only_iter_jsonl_changed() -> None:
    assert normalized_module(BASELINE / "streaming.py", omitted={"iter_jsonl"}, assignments=set()) == normalized_module(
        IMPL / "streaming.py", omitted={"iter_jsonl"}, assignments=set()
    )


def case_custody_byte_identical_to_s5() -> None:
    assert (BASELINE / "custody.py").read_bytes() == (IMPL / "custody.py").read_bytes()


def case_protocol_coverage_retains_every_prior_key() -> None:
    current = driver.protocol_coverage()
    assert current["S6-01_exact_review_plan_origin"] == "verify_review_admission/governing_commit"
    assert current["S6-02_jsonl_record_bound"] == "streaming.iter_jsonl"
    assert set(current) == set(load_module("_baseline_driver_for_coverage", BASELINE / "driver.py").protocol_coverage()) | {
        "S6-01_exact_review_plan_origin", "S6-02_jsonl_record_bound"
    }


def history_accepts(**kwargs: Any) -> None:
    historical.expect_accept(include_plan_input=True, **kwargs)


def history_rejects(**kwargs: Any) -> None:
    historical.expect_reject(**kwargs)


def case_inline_plan_with_declared_input() -> None:
    history_accepts(nested_plan="inline")


def case_path_plan_with_declared_input() -> None:
    history_accepts(nested_plan="path")


def case_omitted_plan_input_rejected() -> None:
    history_rejects(include_plan_input=False)


def run_history_with_admission_mutation(mutate: Callable[[dict[str, Any], Any], None]) -> None:
    history = historical.build_history(include_plan_input=True)
    try:
        mutate(history.admission, history)
        with historical.patched_root(history):
            try:
                driver.verify_review_admission(history.admission, history.source, history.executing)
            except driver.LaunchRefused:
                return
        raise AssertionError("known-invalid review-plan authority was accepted")
    finally:
        history.close()


def case_wrong_plan_commit_rejected() -> None:
    def mutate(admission: dict[str, Any], history: Any) -> None:
        admission["review_plan_commit"] = str(git(history.root, "rev-parse", f"{history.claim}^"))
    run_history_with_admission_mutation(mutate)


def case_backdated_plan_commit_rejected() -> None:
    run_history_with_admission_mutation(lambda admission, history: admission.__setitem__("review_plan_commit", history.source))


def case_wrong_plan_hash_rejected() -> None:
    run_history_with_admission_mutation(lambda admission, _history: admission.__setitem__("review_plan_sha256", "0" * 64))


def case_exact_governing_commit_trace() -> None:
    history = historical.build_history(include_plan_input=True)
    calls: list[tuple[str, str]] = []
    original = driver.git_blob_hash

    def traced(commit: str, relative: str) -> str:
        calls.append((commit, relative))
        return original(commit, relative)

    try:
        with historical.patched_root(history), patch.object(driver, "git_blob_hash", side_effect=traced):
            driver.verify_review_admission(history.admission, history.source, history.executing)
        plan_rel = history.admission["review_plan_path"]
        assert (history.plan, plan_rel) in calls
        assert (history.source, plan_rel) not in calls
        source_paths = {
            row["path"] for row in yaml.safe_load(git_blob(
                history.root, history.authority, history.admission["external_queue_path"]
            ))["tasks"][0]["handoff"]["source_bindings"] if row["path"] != plan_rel
        }
        assert all((history.source, relative) in calls for relative in source_paths)
        assert all(commit != history.plan for commit, relative in calls if relative in source_paths)
    finally:
        history.close()


def case_plan_binding_digest_rejected() -> None:
    history = historical.build_history(include_plan_input=True)
    original = driver.git_blob_bytes
    final_queue = history.admission["external_queue_path"]

    def changed_queue(commit: str, relative: str) -> bytes:
        data = original(commit, relative)
        if relative != final_queue or commit not in {history.authority, history.claim}:
            return data
        document = json.loads(data)
        review = next(row for row in document["tasks"] if row["id"] == history.admission["review_task_id"])
        for binding in review["handoff"]["source_bindings"]:
            if binding["path"] == history.admission["review_plan_path"]:
                binding["sha256"] = "f" * 64
        return (json.dumps(document, sort_keys=True) + "\n").encode()

    try:
        with historical.patched_root(history):
            final_bytes = changed_queue(history.authority, final_queue)
        history.admission["external_queue_sha256"] = digest(final_bytes)
        with historical.patched_root(history), patch.object(driver, "git_blob_bytes", side_effect=changed_queue):
            try:
                driver.verify_review_admission(history.admission, history.source, history.executing)
            except driver.LaunchRefused:
                return
        raise AssertionError("wrong plan binding digest was accepted")
    finally:
        history.close()


def case_plan_source_read_digest_rejected() -> None:
    history = historical.build_history(include_plan_input=True)
    original_bytes = driver.git_blob_bytes
    original_hash = driver.git_blob_hash
    report_path = history.admission["review_report_path"]
    altered: bytes | None = None

    def bytes_override(commit: str, relative: str) -> bytes:
        nonlocal altered
        data = original_bytes(commit, relative)
        if commit == history.archive and relative == report_path:
            document = yaml.safe_load(data)
            document["validation_report"]["review_attestation"]["source_reads"][history.admission["review_plan_path"]] = "0" * 64
            altered = yaml.safe_dump(document, sort_keys=False).encode()
            return altered
        return data

    def hash_override(commit: str, relative: str) -> str:
        if commit == history.archive and relative == report_path:
            return history.admission["review_report_sha256"]
        return original_hash(commit, relative)

    try:
        with historical.patched_root(history), patch.object(driver, "git_blob_bytes", side_effect=bytes_override), patch.object(
            driver, "git_blob_hash", side_effect=hash_override
        ):
            try:
                driver.verify_review_admission(history.admission, history.source, history.executing)
            except driver.LaunchRefused:
                assert altered is not None
                return
        raise AssertionError("wrong attested plan source-read digest was accepted")
    finally:
        history.close()


def json_record(size: int) -> bytes:
    if size < 2:
        raise ValueError(size)
    return b'"' + b"x" * (size - 2) + b'"'


def read_jsonl(payload: bytes, limit: int) -> list[Any]:
    with tempfile.TemporaryDirectory(prefix="validator-707dff-jsonl-") as temporary:
        path = Path(temporary) / "rows.jsonl"
        path.write_bytes(payload)
        return list(streaming.iter_jsonl(path, maximum_record_bytes=limit))


def rejects_before_oversize_parse(payload: bytes, limit: int, expected_valid_parses: int = 0) -> None:
    with tempfile.TemporaryDirectory(prefix="validator-707dff-jsonl-reject-") as temporary:
        path = Path(temporary) / "rows.jsonl"
        path.write_bytes(payload)
        real_loads = json.loads
        calls: list[int] = []

        def controlled(raw: bytes) -> Any:
            calls.append(len(raw))
            if len(calls) > expected_valid_parses:
                raise AssertionError("oversized JSONL record reached json.loads")
            return real_loads(raw)

        with patch.object(streaming.json, "loads", side_effect=controlled):
            try:
                list(streaming.iter_jsonl(path, maximum_record_bytes=limit))
            except streaming.StreamingEncodingError:
                assert len(calls) == expected_valid_parses
                return
        raise AssertionError("oversized JSONL record was accepted")


def case_jsonl_multiple_blank_lines_ordered() -> None:
    assert read_jsonl(b'{"i":1}\n\n{"i":2}\n{"i":3}', 16) == [{"i": 1}, {"i": 2}, {"i": 3}]


def case_jsonl_exact_bound_newline() -> None:
    assert read_jsonl(json_record(1024) + b"\n", 1024) == ["x" * 1022]


def case_jsonl_exact_bound_eof() -> None:
    assert read_jsonl(json_record(1024), 1024) == ["x" * 1022]


def case_jsonl_over_bound_newline_first_chunk() -> None:
    rejects_before_oversize_parse(json_record(1025) + b"\n", 1024)


def case_jsonl_over_bound_newline_cross_chunk() -> None:
    rejects_before_oversize_parse(json_record(streaming.MAX_CHUNK_BYTES + 1) + b"\n", streaming.MAX_CHUNK_BYTES)


def case_jsonl_over_bound_eof() -> None:
    rejects_before_oversize_parse(json_record(1025), 1024)


def case_jsonl_valid_prefix_then_oversize_newline() -> None:
    rejects_before_oversize_parse(b'{"v":1}\n' + json_record(1025) + b"\n", 1024, 1)


def case_jsonl_valid_prefix_then_oversize_eof() -> None:
    rejects_before_oversize_parse(b'{"v":1}\n' + json_record(1025), 1024, 1)


def case_jsonl_chunk_reads_bounded() -> None:
    class Handle:
        def __init__(self, payload: bytes) -> None:
            self.payload = io.BytesIO(payload)
            self.requests: list[int] = []
        def __enter__(self) -> "Handle": return self
        def __exit__(self, *_args: Any) -> None: return None
        def read(self, size: int) -> bytes:
            self.requests.append(size)
            return self.payload.read(size)

    class Source:
        def __init__(self, payload: bytes) -> None:
            self.handle = Handle(payload)
        def exists(self) -> bool: return True
        def open(self, mode: str) -> Handle:
            assert mode == "rb"
            return self.handle

    source = Source(b'{"a":1}\n{"b":2}\n')
    assert list(streaming.iter_jsonl(source, maximum_record_bytes=16)) == [{"a": 1}, {"b": 2}]
    assert source.handle.requests and set(source.handle.requests) == {streaming.MAX_CHUNK_BYTES}


def representative_cell() -> dict[str, Any]:
    arm = {
        "arm": 1, "starts": 2, "successes": 1,
        "transition_group_operations": 3, "verification_group_operations": 2,
        "group_additions": 3, "group_doublings": 0, "charged_cost": 5,
        "failed_certificates": 0, "diagnostic_costs": {}, "diagnostic_meter": {},
        "secondary": {}, "rng_counter_end": 1, "bucket_counts": [1, 1, 1],
    }
    coordinate = {**arm, "arm": "coordinate"}
    controls = {
        "cayley": {"passed": True}, "relabel": True, "occupancy": True,
        "known_false": {"constant_o": {"nonzero_denominators": 0, "solves": 0},
                        "mutated_candidate_fails_certificate": True},
    }
    return {
        "curve_id": "fixed", "seed": 606308, "u": 1, "stream": "heldout",
        "metric": {"available": True, "unavailable_reason": None, "d": 0.25,
                   "coordinate_work": 5, "coordinate_successes": 1, "coordinate_cost": 5.0,
                   "pooled_null_work": 5, "pooled_null_successes": 1,
                   "pooled_null_cost": 5.0, "zero_yield_null_arms": []},
        "coordinate": coordinate, "nulls": [arm], "controls": controls,
        "validity": {"valid": True, "certificate_failures": 0, "failed_controls": [],
                     "control_results": {"cayley_exact": True}},
        "subgroup_enumeration": {"classification": "verified", "points": 3},
        "diagnostic_costs": {"subgroup_enumeration": {"completed": True}},
    }


def case_complete_artifact_producers_and_types() -> None:
    with tempfile.TemporaryDirectory(prefix="validator-707dff-artifacts-") as temporary:
        root = Path(temporary)
        progress = root / "progress"
        progress.mkdir()
        sink = driver.ProgressSink(progress)
        sink.record_fixture({"curve_id": "fixed", "p": 11, "G": [1, 2]})
        sink.record_rejection({"curve_id": "rejected", "reason": "fixed"})
        sink.record_partial({"kind": "fixed", "certificate": {"classification": "partial"}})
        sink.record_scientific_certificate({"kind": "fixed", "certificate": {"classification": "verified"}})
        sink.record_diagnostic({"diagnostic": "fixed", "completed": False, "error": "fixed interruption"})
        sink.record_cell(representative_cell())
        meter = historical.Meter()
        provenance = {"commit": SOURCE_SNAPSHOT, "dirty": False, "command": "fixed lower-level serialization"}
        with patch.object(driver, "process_group_rss_bytes", return_value=123456):
            producers = driver.artifact_producers(
                lock={"run_id": "fixed-synthetic"}, provenance=provenance, meter=meter,
                sink=sink, status="completed_invalid", error="fixed only",
                decision={"branch": "inconclusive"},
            )
        result = custody.finalize_run(
            run_root=root, run_id="fixed-synthetic", artifact_order=driver.EXPERIMENT_ARTIFACTS,
            producers=producers, integrity_name="package-sha256.json", meter=meter,
            guard_telemetry=lambda: {"fixed": True}, cleanup_paths=(),
        )
        payload = result.payload_path
        assert {path.name for path in payload.iterdir()} == set(driver.EXPERIMENT_ARTIFACTS)
        manifest = json.loads((payload / "manifest.yaml").read_bytes())
        assert type(manifest["run"]["inputs"]["parameters"]["frozen_heldout_seeds"][0]) is int
        assert type(manifest["run"]["result"]["valid"]) is bool
        assert manifest["run"]["resources"]["rss_boundary_sample_bytes"] == 123456
        assert json.loads((payload / "controls.json").read_bytes())[0]["controls"]["occupancy"] is True
        certificates = json.loads((payload / "certificates.json").read_bytes())
        assert len(certificates["partial_certificates"]) == 1 and len(certificates["scientific_records"]) == 1
        assert json.loads((payload / "raw.jsonl").read_bytes())["seed"] == 606308
        assert (payload / "costs.csv").read_text().splitlines()[0].startswith("curve_id,seed,u,stream")


def case_maximum_certificate_count_streams_lazily() -> None:
    count = 781_824

    class NullHandle:
        def __init__(self) -> None: self.fragments = 0
        def write(self, fragment: bytes) -> int:
            self.fragments += 1
            return len(fragment)

    generated = 0
    def records() -> Iterator[None]:
        nonlocal generated
        for _ in range(count):
            generated += 1
            yield None

    handle = NullHandle()
    writer = streaming.GuardedDigestWriter(handle)
    streaming.stream_json_array(writer, records())
    assert generated == count and handle.fragments == 2 * count + 1


def case_guard_cadence_and_memory_stop() -> None:
    with tempfile.TemporaryDirectory(prefix="validator-707dff-guard-") as temporary:
        sink = driver.ProgressSink(Path(temporary))
        guard = driver.Guard(sink, limit_bytes=100)
        with patch.object(driver, "process_group_rss_bytes", side_effect=[90, 101]), patch.object(
            driver.time, "monotonic", side_effect=[1.0, 1.0, 1.1, 1.3, 1.3]
        ):
            guard.check()
            guard.check()
            try:
                guard.check()
            except driver.ResourceStop:
                pass
            else:
                raise AssertionError("over-limit fixed RSS sample was accepted")
        assert guard.actual_polls == 2 and guard.sampled_process_group_max_bytes == 101


def case_timing_boundary_is_stable_before_companion() -> None:
    meter = historical.Meter()
    with tempfile.TemporaryDirectory(prefix="validator-707dff-timing-") as temporary:
        result = custody.finalize_run(
            run_root=Path(temporary), run_id="fixed-synthetic",
            artifact_order=("payload.json", "integrity.json"),
            producers=historical.minimal_producers(False), integrity_name="integrity.json",
            meter=meter, guard_telemetry=lambda: {"fixed": True},
        )
        payload_timing = result.timing_through_durable_payload
        companion = json.loads(result.operational_receipt_path.read_bytes())
        assert payload_timing == companion["timing_through_durable_payload"]
        scope = companion["terminal_receipt_scope"]
        assert "excludes its own write" in scope and "fsync duration" in scope and "no self-hash" in scope


@dataclass(frozen=True)
class Case:
    name: str
    action: Callable[[], None]


_REMOVED_HISTORICAL_EXPECTATIONS = {
    "reduced_input_lifecycle_reachable",
    "inline_only_plan_reachable",
    "path_only_plan_reachable",
}

CASES = [
    *[Case(item.name, item.action) for item in historical.CASES if item.name not in _REMOVED_HISTORICAL_EXPECTATIONS],
    Case("scientific_driver_ast_preserved_from_s5", case_scientific_driver_preserved),
    Case("streaming_only_iter_jsonl_changed_from_s5", case_streaming_only_iter_jsonl_changed),
    Case("custody_byte_identical_to_s5", case_custody_byte_identical_to_s5),
    Case("protocol_coverage_retains_prior_keys", case_protocol_coverage_retains_every_prior_key),
    Case("inline_plan_with_declared_input_reachable", case_inline_plan_with_declared_input),
    Case("path_plan_with_declared_input_reachable", case_path_plan_with_declared_input),
    Case("omitted_plan_input_rejected", case_omitted_plan_input_rejected),
    Case("wrong_plan_commit_rejected", case_wrong_plan_commit_rejected),
    Case("backdated_plan_commit_rejected", case_backdated_plan_commit_rejected),
    Case("wrong_plan_hash_rejected", case_wrong_plan_hash_rejected),
    Case("exact_governing_commit_trace", case_exact_governing_commit_trace),
    Case("wrong_plan_binding_digest_rejected", case_plan_binding_digest_rejected),
    Case("wrong_plan_source_read_digest_rejected", case_plan_source_read_digest_rejected),
    Case("jsonl_multiple_records_blank_lines_ordered", case_jsonl_multiple_blank_lines_ordered),
    Case("jsonl_exact_bound_newline_valid", case_jsonl_exact_bound_newline),
    Case("jsonl_exact_bound_eof_valid", case_jsonl_exact_bound_eof),
    Case("jsonl_one_over_newline_first_chunk_rejected", case_jsonl_over_bound_newline_first_chunk),
    Case("jsonl_one_over_newline_cross_chunk_rejected", case_jsonl_over_bound_newline_cross_chunk),
    Case("jsonl_one_over_eof_rejected", case_jsonl_over_bound_eof),
    Case("jsonl_valid_prefix_later_newline_oversize_rejected", case_jsonl_valid_prefix_then_oversize_newline),
    Case("jsonl_valid_prefix_later_eof_oversize_rejected", case_jsonl_valid_prefix_then_oversize_eof),
    Case("jsonl_read_chunks_bounded", case_jsonl_chunk_reads_bounded),
    Case("complete_artifact_producers_and_types", case_complete_artifact_producers_and_types),
    Case("maximum_certificate_count_streams_lazily", case_maximum_certificate_count_streams_lazily),
    Case("guard_cadence_and_memory_stop", case_guard_cadence_and_memory_stop),
    Case("timing_boundary_stable_before_companion", case_timing_boundary_is_stable_before_companion),
]


FORBIDDEN = (
    "fixture_scan", "select_fixtures", "collision_census", "collision_census_with_custody",
    "constant_o_census", "cayley_control", "future_cell", "run_future_pipeline",
    "verify_launch_admission", "verify_signature", "verify_run_allocation",
)


class CaseTimeout(RuntimeError):
    pass


def timeout_handler(_signum: int, _frame: Any) -> None:
    raise CaseTimeout("fixed case exceeded 10 seconds")


@contextlib.contextmanager
def forbidden_call_guards() -> Iterator[None]:
    def refused(*_args: Any, **_kwargs: Any) -> Any:
        raise AssertionError("forbidden scientific/launch helper was invoked")
    with contextlib.ExitStack() as stack:
        for name in FORBIDDEN:
            stack.enter_context(patch.object(driver, name, side_effect=refused))
        yield


def main() -> int:
    if not (1 <= len(CASES) <= 128):
        raise RuntimeError(f"complete suite has {len(CASES)} cases; required range is 1..128")
    administrative = full_input_audit()
    signal.signal(signal.SIGALRM, timeout_handler)
    started_at = datetime.now(timezone.utc)
    started_wall = time.monotonic()
    started_cpu = time.process_time()
    rss_unit = 1 if platform.system() == "Darwin" else 1024
    rss_start = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * rss_unit
    results: list[dict[str, Any]] = []
    with forbidden_call_guards():
        for case in CASES:
            case_wall = time.monotonic()
            case_cpu = time.process_time()
            signal.alarm(10)
            try:
                case.action()
            except Exception as exc:
                outcome = "FAIL"
                detail = f"{type(exc).__name__}: {exc}"
            else:
                outcome = "PASS"
                detail = "fixed source obligation held"
            finally:
                signal.alarm(0)
            results.append({
                "name": case.name,
                "outcome": outcome,
                "detail": detail,
                "wall_seconds": round(time.monotonic() - case_wall, 6),
                "cpu_seconds": round(time.process_time() - case_cpu, 6),
            })
    ended_at = datetime.now(timezone.utc)
    failed = [row for row in results if row["outcome"] == "FAIL"]
    output = {
        "schema": "crypto.autoresearch.independent_s6_source_checks.v1",
        "task_id": TASK_ID,
        "authority_commit": AUTHORITY_COMMIT,
        "published_claim_commit": PUBLISHED_CLAIM_COMMIT,
        "source_snapshot_commit": SOURCE_SNAPSHOT,
        "source_task_id": SOURCE_TASK,
        "scope": "one complete S6 source/admission/streaming/custody joint; fixed lower-level checks only",
        "administrative_checks": administrative,
        "limits": {
            "maximum_total_case_executions_including_failures_parameters_and_reruns": 640,
            "complete_suite_cases": len(CASES),
            "reserved_corrected_complete_final_suite_cases": len(CASES),
            "maximum_cases_per_complete_suite": 128,
            "maximum_seconds_per_case": 10,
            "maximum_aggregate_executed_check_wall_cpu_seconds": 1800,
            "memory_limit_bytes": 2 * 1024**3,
            "maximum_workers": 1,
            "maximum_scientific_runs": 0,
        },
        "actual": {
            "suite_invocations_this_process": 1,
            "case_executions_including_failures_parameters_and_reruns": len(results),
            "passed": len(results) - len(failed),
            "failed": len(failed),
            "errors": 0,
            "timeouts": sum("CaseTimeout" in row["detail"] for row in results),
            "absolute_utc_start": started_at.isoformat(),
            "absolute_utc_end": ended_at.isoformat(),
            "script_wall_seconds": round(time.monotonic() - started_wall, 6),
            "script_cpu_seconds": round(time.process_time() - started_cpu, 6),
            "maximum_case_wall_seconds": max(row["wall_seconds"] for row in results),
            "maximum_case_cpu_seconds": max(row["cpu_seconds"] for row in results),
            "ru_maxrss_start_bytes": rss_start,
            "ru_maxrss_end_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * rss_unit,
            "ru_maxrss_scope": "process lifetime high-water at suite boundaries",
            "maximum_workers": 1,
        },
        "forbidden_work_executed": {
            "fixture_or_candidate_search": 0,
            "scientific_collision_census": 0,
            "scientific_null_control_or_timing_panel": 0,
            "sage_or_pari": 0,
            "verify_launch_admission": 0,
            "future_run_or_prospective_pipeline": 0,
            "real_key_signature_nonce_or_lock": 0,
            "real_run_allocation_or_RUN_directory": 0,
        },
        "results": results,
    }
    print(json.dumps(output, sort_keys=True))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
