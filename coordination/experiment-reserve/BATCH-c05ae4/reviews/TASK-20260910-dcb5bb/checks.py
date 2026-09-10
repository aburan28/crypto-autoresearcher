"""Independent artificial controls for TASK-20260910-dcb5bb.

This checker consumes only copied, hash-bound repository inputs and synthetic
cost/context/timing records.  It does not execute producer controllers,
scientific code, fixtures, network operations, or private material.
"""
from __future__ import annotations

import argparse
import base64
import copy
import hashlib
import json
import os
import signal
import sys
import time
import traceback
from fractions import Fraction
from itertools import product
from pathlib import Path
from typing import Any, Callable

import yaml


TASK_ID = "TASK-20260910-dcb5bb"
BLIND_NOTE_SHA256 = "e21ed35244a3dcc138697f216832a18b94f62b0d73d0b48f7a1429ccd5731d9c"
SOURCE_SNAPSHOT = "3e2a3488d0ee268aa3f907f9e5afe2e802016ba3"
AUTHORITY_HEAD = "70f12d8af47bd77c526c7b95cd86ccb9f7ea6bfa"
MAX_CASE_SECONDS = 60


class CheckFailure(AssertionError):
    pass


def require(condition: bool, detail: str) -> None:
    if condition is not True:
        raise CheckFailure(detail)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_case(case: dict[str, Any]) -> bytes:
    return json.dumps(case, sort_keys=True, ensure_ascii=True, allow_nan=False,
                      separators=(",", ":")).encode("utf-8")


def expect_cost_error(call: Callable[[], Any], code: str | None = None) -> str:
    try:
        call()
    except CostError as error:
        if code is not None and error.code != code:
            raise CheckFailure(f"expected CostError {code}, got {error.code}") from error
        return error.code
    raise CheckFailure("known-invalid artificial input was accepted")


def context_data() -> dict[str, Any]:
    return {
        "record_type": "cm_cost_context",
        "candidate_origins": {"I0": 10, "I1": 20, "I2": 30},
        "candidate_trace": [
            {"interval": interval, "event_ordinal": origin + offset, "outcome": "accepted"}
            for interval, origin in (("I0", 10), ("I1", 20), ("I2", 30))
            for offset in range(2)
        ],
        "class_memberships": {
            fixture: {"C0": ["K0", "K1"], "C1": ["K2", "K3"]}
            for fixture in FIXTURES
        },
        "frozen_winners": [
            {"interval": interval, "coordinate": coordinate, "arm": 2}
            for interval in INTERVALS for coordinate in COORDINATES
        ],
    }


def raw_record(*, ordinal: int, component: str = "scalar_multiplication",
               scope: str = "block_repetition", phase: str = "evaluation",
               plane: str = "main", arm: int = 2, status: str = "complete",
               cpu: int | None = 17, wall: int | None = 19,
               rss: int | None = 31) -> dict[str, Any]:
    reason = None if status in ("complete", "below_resolution") else "capture_failed"
    row: dict[str, Any] = {
        "record_type": "raw_cost",
        "raw_cost_row_id": f"independent-row-{ordinal}",
        "physical_event_id": f"independent-event-{ordinal}",
        "event_ordinal": ordinal,
        "component": component,
        "phase": phase,
        "status": status,
        "CPU_nanoseconds": cpu,
        "CPU_unavailable_reason": None if cpu is not None else "capture_failed",
        "wall_nanoseconds": wall,
        "wall_unavailable_reason": None if wall is not None else "capture_failed",
        "process_group_peak_RSS_bytes": rss,
        "RSS_unavailable_reason": None if rss is not None else "capture_failed",
        "operation_counts": None,
        "operation_counts_unavailable_reason": "uninstrumented_backend",
        "capture_interval": {
            "stream_id": "independent-stream",
            "process_group_id": 7001 if reason is None else None,
            "cpu_started_ns": ordinal * 1000 if reason is None else None,
            "cpu_finished_ns": ordinal * 1000 + (cpu or 0) if reason is None else None,
            "wall_started_ns": ordinal * 1000 if reason is None else None,
            "wall_finished_ns": ordinal * 1000 + (wall or 0) if reason is None else None,
            "reason": reason,
        },
        "charge_kind": "exclusive_leaf",
        "source_leaf_ids": [],
        "scope": scope,
    }
    if scope in ("interval", "selection_stratum"):
        row["interval"] = "I0"
    if scope not in ("global", "interval", "selection_stratum", "scaffolding"):
        row["fixture"] = "I0F0"
    if scope == "kernel":
        row["kernel"] = "K0"
    if scope == "class":
        row["class"] = "C0"
    if scope in ("endpoint_coordinate", "arm_workload", "timing_block", "block_repetition"):
        row.update(endpoint="K0", coordinate=1)
    if scope == "selection_stratum":
        row["coordinate"] = 1
    if scope in ("arm_workload", "timing_block", "block_repetition"):
        row.update(plane=plane, arm=arm,
                   seed=606101 if plane == "selection" else 606103,
                   q=256 if plane == "selection" else 4096)
    if scope in ("timing_block", "block_repetition"):
        row["block"] = 0
    if scope == "block_repetition":
        row["repetition"] = 1
    if scope == "scaffolding":
        row.update(scaffold_kind=component, owner={"scope": "global"})
    return row


def timing_row(key: tuple[Any, ...], *, resource: bool | None = True) -> dict[str, Any]:
    plane, fixture, endpoint, coordinate, seed, q, arm, block = key
    return {
        "record_type": "cm_timing_block", "plane": plane, "fixture": fixture,
        "endpoint": endpoint, "coordinate": coordinate, "seed": seed, "q": q,
        "arm": arm, "block": block, "status": "complete", "repetitions": 1,
        "cumulative_group_CPU_nanoseconds": [100_000_000],
        "replay_verified": True, "resource_accounted": resource,
    }


def case_bound_inputs(env: dict[str, Any]) -> dict[str, Any]:
    handoff = yaml.safe_load((env["control"] / "handoff.yaml").read_bytes())["handoff"]
    bindings = handoff["source_bindings"]
    require(len(bindings) == 51, "handoff must bind exactly 51 declared inputs")
    require(len({item["path"] for item in bindings}) == 51, "bound paths must be unique")
    require(handoff["inputs"] == [item["path"] for item in bindings],
            "input order and source-binding order differ")
    mismatches = []
    total_bytes = 0
    for item in bindings:
        data = (env["repo_inputs"] / item["path"]).read_bytes()
        total_bytes += len(data)
        if sha(data) != item["sha256"]:
            mismatches.append(item["path"])
    require(not mismatches, "bound input hash mismatch: " + ",".join(mismatches))
    plan = yaml.safe_load((env["repo_inputs"] / handoff["review_plan_path"]).read_bytes())["review_plan"]
    require(plan == handoff["review_plan"], "separate review plan differs from handoff copy")
    require(plan["source_snapshot"] == SOURCE_SNAPSHOT, "source snapshot mismatch")
    return {"bindings_checked": 51, "bytes_hashed": total_bytes,
            "source_snapshot": SOURCE_SNAPSHOT, "authority_head": AUTHORITY_HEAD}


def case_snapshot_bindings(env: dict[str, Any]) -> dict[str, Any]:
    rel = Path("experiments/EXP-ECDLP-1b1b99/implementation/TASK-20260910-2631a0")
    snap = json.loads((env["repo_inputs"] / "coordination/experiment-reserve/BATCH-c05ae4/archives/TASK-20260910-5cd8a5/snapshot.json").read_bytes())
    require(snap["source_task_ids"] == ["TASK-20260910-2631a0"], "snapshot source task")
    require(snap["scientific_executions"] == 0, "snapshot claims scientific work")
    expected = snap["source_path_sha256"]
    require(len(expected) == 9, "snapshot must bind nine producer artifacts")
    for path, digest in expected.items():
        require(sha((env["repo_inputs"] / path).read_bytes()) == digest,
                "snapshot source hash mismatch: " + path)
    for name in ("costs.py", "allocations.py", "reducers.py"):
        require((env["source"] / name).read_bytes() == (env["repo_inputs"] / rel / name).read_bytes(),
                "executed review source copy mismatch: " + name)
    return {"snapshot_paths_checked": 9, "snapshot_declares_commit_inside_itself": False,
            "snapshot_binding_note": snap["binding_note"]}


def _decode_blob(blob: dict[str, Any], label: str) -> bytes:
    require(set(blob) == {"bytes", "content_b64", "sha256"}, "blob fields: " + label)
    data = base64.b64decode(blob["content_b64"], validate=True)
    require(len(data) == blob["bytes"], "blob length: " + label)
    require(sha(data) == blob["sha256"], "blob digest: " + label)
    return data


def _json_lines(data: bytes, label: str) -> list[dict[str, Any]]:
    rows = []
    for number, line in enumerate(data.splitlines(), 1):
        try:
            row = json.loads(line)
        except Exception as error:
            raise CheckFailure(f"invalid JSONL {label}:{number}") from error
        require(type(row) is dict, f"non-object JSONL {label}:{number}")
        rows.append(row)
    return rows


def case_producer_custody(env: dict[str, Any]) -> dict[str, Any]:
    receipt_path = env["repo_inputs"] / "experiments/EXP-ECDLP-1b1b99/implementation/TASK-20260910-2631a0/check-receipt.json"
    receipt = json.loads(receipt_path.read_bytes())
    require(receipt["record_type"] == "cm_cost_component_all_attempt_receipt", "receipt type")
    require(receipt["counts"] == {"started": 785, "completed": 785, "passed": 777, "failed": 8}, "all-attempt counts")
    require(receipt["final_complete_suite"] == {"started": 397, "completed": 397, "passed": 397, "failed": 0}, "final-suite counts")
    require(receipt["scientific_runs"] == 0 and receipt["scientific_admission"] is False, "receipt boundary")
    _decode_blob(receipt["assembler"], "assembler")
    attempts = receipt["attempts"]
    require(len(attempts) == 2, "two producer attempts required")
    expected_counts = ((388, 380, 8, 1), (397, 397, 0, 0))
    decoded_sources: list[dict[str, bytes]] = []
    aggregate = {"started": 0, "completed": 0, "passed": 0, "failed": 0}
    failure_types: list[str] = []
    failure_ids: list[str] = []
    for attempt_index, (attempt, expected) in enumerate(zip(attempts, expected_counts), 1):
        evidence = attempt["embedded_evidence"]
        required = {"case-journal.jsonl", "checker-pid.json", "checker.stderr", "checker.stdout",
                    "coverage.json", "handoff.yaml", "launch-plan.json", "monitor-readiness.json",
                    "samples.jsonl", "source/allocations.py", "source/costs.py", "source/coverage.json",
                    "source/integration-contract.json", "source/reducers.py", "source/tests.py",
                    "supervisor-terminal.json", "supervisor.py"}
        require(required <= set(evidence), f"attempt {attempt_index} missing retained streams")
        decoded = {name: _decode_blob(blob, f"attempt{attempt_index}/{name}") for name, blob in evidence.items()}
        for name in evidence:
            if name.startswith("outer-tool-"):
                json.loads(decoded[name])
        require(any(name.startswith("outer-tool-") for name in evidence), "outer tool calls missing")
        registry = json.loads(decoded["coverage.json"])
        cases = registry["cases"]
        journal = _json_lines(decoded["case-journal.jsonl"], f"attempt{attempt_index}/journal")
        starts = [row for row in journal if row.get("event") == "case_start"]
        results = [row for row in journal if row.get("event") == "case_result"]
        terminals = [row for row in journal if row.get("event") == "suite_terminal"]
        ids = [case["id"] for case in cases]
        require([row["id"] for row in starts] == ids == [row["id"] for row in results],
                f"attempt {attempt_index} journal/registry order")
        require(len(terminals) == 1, f"attempt {attempt_index} suite terminal")
        for start, case in zip(starts, cases):
            require(start["case_definition_sha256"] == sha(canonical_case(case)),
                    "case definition digest mismatch: " + start["id"])
        started, passed, failed, returncode = expected
        require((len(starts), len(results), sum(row["outcome"] == "pass" for row in results),
                 sum(row["outcome"] == "fail" for row in results)) == (started, started, passed, failed),
                f"attempt {attempt_index} journal counts")
        require(attempt["counts"] == {"started": started, "completed": started, "passed": passed, "failed": failed},
                f"attempt {attempt_index} receipt counts")
        pid = attempt["terminal"]["terminal"]["pid"]
        require(all(row["pid"] == pid for row in starts + results), f"attempt {attempt_index} PID binding")
        require(all(type(row["wall_ns"]) is int and row["wall_ns"] >= 0 and
                    type(row["process_cpu_ns"]) is int and row["process_cpu_ns"] >= 0 for row in results),
                f"attempt {attempt_index} per-case resource observations")
        terminal = attempt["terminal"]
        require(terminal["primary_failure"] is None and terminal["cleanup_errors"] == [], "supervisor failures")
        require(terminal["terminal"]["reaped"] is True and terminal["terminal"]["returncode"] == returncode,
                f"attempt {attempt_index} reaping/returncode")
        require(terminal["hard_memory_limit"] is False and terminal["peak_sampled_checker_RSS_bytes"] < 2*1024**3,
                f"attempt {attempt_index} sampled RSS boundary")
        require(terminal["terminal"]["user_cpu_seconds"] >= 0 and terminal["terminal"]["system_cpu_seconds"] >= 0 and terminal["observed_wall_seconds"] >= 0,
                f"attempt {attempt_index} CPU/wall custody")
        samples = _json_lines(decoded["samples.jsonl"], f"attempt{attempt_index}/samples")
        readiness = json.loads(decoded["monitor-readiness.json"])
        # Read the periodic and monitor-readiness streams independently.  The
        # terminal-minus-stream count is retained as an observation rather
        # than being explained or filled in by inference.
        require(len(samples) > 0, "RSS sample stream is empty")
        rss_count_delta = terminal["RSS_samples"] - len(samples)
        rss_values = []
        missing_periodic_rss = 0
        for sample in samples:
            values = [value for key, value in sample.items()
                      if type(value) is int and "rss" in key.lower() and "limit" not in key.lower()]
            if values:
                rss_values.append(max(values))
            else:
                missing_periodic_rss += 1
        def retained_rss(value: Any) -> list[int]:
            if type(value) is dict:
                here = [item for key, item in value.items()
                        if type(item) is int and "rss" in key.lower() and "limit" not in key.lower()]
                return here + [item for child in value.values() for item in retained_rss(child)]
            if type(value) is list:
                return [item for child in value for item in retained_rss(child)]
            return []
        readiness_rss = retained_rss(readiness)
        rss_values.extend(readiness_rss)
        peak_recomputed = bool(rss_values)
        if peak_recomputed:
            require(max(rss_values) == terminal["peak_sampled_checker_RSS_bytes"], "sampled RSS maximum")
        for row in results:
            if row["outcome"] == "fail":
                failure_types.append(row["error"]["type"])
                failure_ids.append(row["id"])
        attempt["independent_RSS_count_audit"] = {
            "terminal_count": terminal["RSS_samples"],
            "periodic_stream_rows": len(samples),
            "terminal_minus_periodic_rows": rss_count_delta,
            "periodic_rows_without_RSS_value": missing_periodic_rss,
            "readiness_RSS_values": readiness_rss,
            "peak_recomputed_from_exposed_integer_RSS_fields": peak_recomputed,
        }
        decoded_sources.append({name.removeprefix("source/"): data for name, data in decoded.items() if name.startswith("source/")})
        for key in aggregate:
            aggregate[key] += attempt["counts"][key]
    require(aggregate == receipt["counts"], "attempt totals do not reconcile")
    require(failure_types.count("TimeoutError") == 7 and len(failure_types) == 8,
            "attempt1 must retain seven watchdog failures and one distinct test failure")
    require(sum("connected" in item for item in failure_ids) == 7, "seven connected watchdog cases not retained")
    require(any("joint" in item for item in failure_ids), "incorrect instability construction failure missing")
    for name in ("allocations.py", "reducers.py", "integration-contract.json"):
        require(decoded_sources[0][name] == decoded_sources[1][name], "unexpected correction boundary: " + name)
    for name in ("costs.py", "tests.py", "coverage.json"):
        require(decoded_sources[0][name] != decoded_sources[1][name], "expected corrected source unchanged: " + name)
    final_root = env["repo_inputs"] / "experiments/EXP-ECDLP-1b1b99/implementation/TASK-20260910-2631a0"
    for name in ("costs.py", "allocations.py", "reducers.py", "tests.py", "coverage.json", "integration-contract.json"):
        require(decoded_sources[1][name] == (final_root / name).read_bytes(), "final source differs from attempt2: " + name)
    require(receipt["post_test_edits"] == {"algorithm_sources_changed": False, "metadata_only": ["README.md"],
            "new_delivery_records": ["implementation-report.yaml", "check-receipt.json"]}, "post-test edit boundary")
    for name, item in receipt["final_nonreceipt_artifacts"].items():
        data = (final_root / name).read_bytes()
        require(len(data) == item["bytes"] and sha(data) == item["sha256"], "final artifact binding: " + name)
    return {"producer_cases_checked": 785, "attempts_checked": 2,
            "attempt1_failure_types": failure_types,
            "source_versions_checked": 2,
            "RSS_count_audits": [a["independent_RSS_count_audit"] for a in attempts],
            "peak_sampled_RSS_bytes": max(a["terminal"]["peak_sampled_checker_RSS_bytes"] for a in attempts)}


def _selection_estimates(case: str) -> dict[tuple[str, str, int, int], BlockEstimate]:
    values = {2: Fraction(30), 3: Fraction(60), 4: Fraction(80),
              5: Fraction(100), 6: Fraction(120), 7: Fraction(105)}
    if case == "B":
        values[7] = Fraction(3)
    return {(fixture, endpoint, coordinate, arm): BlockEstimate(34, (values[arm],)*7, None)
            for fixture, endpoint, coordinate, arm in product(FIXTURES, ENDPOINTS, COORDINATES, range(2, 8))}


def case_blind_arithmetic_a(env: dict[str, Any]) -> dict[str, Any]:
    rows = select_candidates(_selection_estimates("A"))
    require(all(row["winner"] == 2 for row in rows), "case A winner")
    scores = [item["score"]["value"] for item in rows[0]["scores"]]
    require(scores == [{"numerator": value, "denominator": 1} for value in (64, 94, 114, 134, 154, 139)], "case A scores")
    scalar = [BlockEstimate(3669 + 34, (Fraction(30),)*7, None)] * 2
    transport = [BlockEstimate(34, (Fraction(25),)*7, None)] * 2
    ratio = ratio_of_totals(scalar, transport)
    require(ratio == {"kind": "value", "value": {"numerator": 3733, "denominator": 59}}, "case A ratio")
    require(all(ratio_of_totals(scalar, transport, b) == ratio for b in BLOCKS), "case A joint omissions")
    return {"winner": 2, "actual_selection_spend_ns": 3669, "ratio": "3733/59"}


def case_blind_arithmetic_b(env: dict[str, Any]) -> dict[str, Any]:
    rows = select_candidates(_selection_estimates("B"))
    require(all(row["winner"] == 7 for row in rows), "case B winner")
    scores = [item["score"]["value"] for item in rows[0]["scores"]]
    require(scores == [{"numerator": value, "denominator": 1} for value in (64, 94, 114, 134, 154, 37)], "case B scores")
    scalar = [BlockEstimate(2976 + 34, (Fraction(105),)*7, None)] * 2
    transport = [BlockEstimate(34, (Fraction(25),)*7, None)] * 2
    ratio = ratio_of_totals(scalar, transport)
    require(ratio == {"kind": "value", "value": {"numerator": 3115, "denominator": 59}}, "case B ratio")
    require(all(ratio_of_totals(scalar, transport, b) == ratio for b in BLOCKS), "case B joint omissions")
    return {"winner": 7, "actual_selection_spend_ns": 2976, "ratio": "3115/59"}


def case_strict_carriers(env: dict[str, Any]) -> dict[str, Any]:
    require(strict_json_loads(b'{"x":1}') == {"x": 1}, "strict integer JSON")
    codes = [
        expect_cost_error(lambda: strict_json_loads(b'{"x":1,"x":2}'), "duplicate_json_key"),
        expect_cost_error(lambda: strict_json_loads(b'{"x":{"y":1,"y":2}}'), "duplicate_json_key"),
        expect_cost_error(lambda: strict_json_loads(b'{"x":1.0}'), "forbidden_float"),
        expect_cost_error(lambda: decode_fraction({"numerator": True, "denominator": 1}), "fraction_numerator"),
        expect_cost_error(lambda: decode_fraction({"numerator": 2, "denominator": 2}), "fraction_not_canonical"),
    ]
    complete_missing_rss = raw_record(ordinal=901, rss=None)
    codes.append(expect_cost_error(lambda: validate_raw_semantics(env["contract"], complete_missing_rss),
                                   "cost_record_schema_error"))
    wrong_arm = raw_record(ordinal=902, component="every_per_point_table", arm=2)
    codes.append(expect_cost_error(lambda: validate_raw_semantics(env["contract"], wrong_arm),
                                   "cost_record_schema_error"))
    return {"typed_refusals": codes}


def case_context_identity(env: dict[str, Any]) -> dict[str, Any]:
    context = AllocationContext(context_data())
    require(context.candidate_fixture("I1", 20) == "I1F0", "global origin retained")
    require(context.candidate_fixture("I2", 31) == "I2F1", "global ordinal is not local index")
    data = context_data()
    data["candidate_trace"][2]["event_ordinal"] = 0
    expect_cost_error(lambda: AllocationContext(data), "candidate_prefix_missing_or_duplicate")
    data = context_data()
    data["class_memberships"]["I0F0"]["C0"] = ["K0", "endpoint-one"]
    expect_cost_error(lambda: AllocationContext(data), "class_requires_two_endpoint_labels")
    return {"global_origins": [10, 20, 30], "classes_partitioned": True}


def case_integer_allocations(env: dict[str, Any]) -> dict[str, Any]:
    context = AllocationContext(context_data())
    row = raw_record(ordinal=1, component="global_public_source_initialization", scope="global", phase="setup",
                     cpu=10**80 + 73, wall=10**80 + 145)
    groups, issues = expected_groups(env["contract"], row, context)
    require(not issues and len(groups) == 16 and all(len(group.targets) == 72 for group in groups), "global shared alternative groups")
    edges = list(edges_from_groups(row, (groups[0],)))
    require(len(edges) == 72, "global target count")
    require(sum(Fraction(e["weight"]["numerator"], e["weight"]["denominator"]) for e in edges) == 1, "weights sum one")
    require(sum(e["allocated_CPU_nanoseconds"] for e in edges) == row["CPU_nanoseconds"], "CPU integer reconciliation")
    base, remainder = divmod(row["CPU_nanoseconds"], 72)
    require([e["allocated_CPU_nanoseconds"] for e in edges] == [base + int(i < remainder) for i in range(72)], "canonical remainder order")
    lib = raw_record(ordinal=2, component="global_library_initialization", scope="global", phase="setup", cpu=73, wall=145)
    lib_groups, issues = expected_groups(env["contract"], lib, context)
    require(not issues and len(lib_groups) == 9 and lib_groups[-1].scenario == {"kind": "selection_score", "candidate_arm": 7}, "candidate7 global initialization group")
    overhead = raw_record(ordinal=3, component="baseline_selection_stratum_overhead", scope="selection_stratum", phase="selection", cpu=9, wall=17)
    overhead_groups, issues = expected_groups(env["contract"], overhead, context)
    require(not issues and len(overhead_groups) == 8 and all(len(group.targets) == 8 for group in overhead_groups), "selection stratum 1/8 groups")
    return {"global_targets": 72, "global_groups": 16, "library_groups": 9,
            "selection_stratum_targets": 8, "arbitrary_integer_bits": row["CPU_nanoseconds"].bit_length()}


def case_capture_identity(env: dict[str, Any]) -> dict[str, Any]:
    scratch = env["case_scratch"] / "capture"
    scratch.mkdir()
    with CostLedger(env["contract"], scratch) as ledger:
        first = raw_record(ordinal=1)
        first["capture_interval"].update(cpu_started_ns=0, cpu_finished_ns=10, wall_started_ns=0, wall_finished_ns=10)
        first.update(CPU_nanoseconds=10, wall_nanoseconds=10)
        second = raw_record(ordinal=2)
        second["capture_interval"].update(cpu_started_ns=10, cpu_finished_ns=20, wall_started_ns=10, wall_finished_ns=20)
        second.update(CPU_nanoseconds=10, wall_nanoseconds=10)
        ledger.add(first); ledger.add(second); ledger.finalize()
        require(actual_campaign_accounting(ledger)["CPU_nanoseconds"] == 20, "adjacent spans")
    overlap_scratch = env["case_scratch"] / "overlap"
    overlap_scratch.mkdir()
    with CostLedger(env["contract"], overlap_scratch) as ledger:
        first = raw_record(ordinal=1)
        first["capture_interval"].update(cpu_started_ns=0, cpu_finished_ns=10, wall_started_ns=0, wall_finished_ns=10)
        first.update(CPU_nanoseconds=10, wall_nanoseconds=10)
        second = raw_record(ordinal=2)
        second["capture_interval"].update(cpu_started_ns=9, cpu_finished_ns=12, wall_started_ns=9, wall_finished_ns=12)
        second.update(CPU_nanoseconds=3, wall_nanoseconds=3)
        ledger.add(first)
        expect_cost_error(lambda: ledger.add(second), "overlapping_exclusive_capture")
    return {"adjacent_accepted": True, "overlap_refused": True}


def case_rollup_completeness_break(env: dict[str, Any]) -> dict[str, Any]:
    scratch = env["case_scratch"] / "rollup"
    scratch.mkdir()
    leaf = raw_record(ordinal=1, component="level_source_certificate", scope="fixture", phase="setup")
    rollup = raw_record(ordinal=2, component="level_and_multiplicity_certificate", scope="fixture", phase="setup")
    rollup.update(charge_kind="derived_rollup", source_leaf_ids=[leaf["raw_cost_row_id"]],
                  CPU_nanoseconds=None, CPU_unavailable_reason="derived_rollup",
                  wall_nanoseconds=None, wall_unavailable_reason="derived_rollup")
    with CostLedger(env["contract"], scratch) as ledger:
        ledger.add(leaf); ledger.add(rollup)
        result = ledger.finalize()
    require(result["ledger_identity_and_capture_consistent"] is True,
            "implementation behavior changed; re-evaluate this counterexample")
    return {"breaking_observation": "single-leaf level_and_multiplicity rollup accepted",
            "missing_required_leaf_kinds": ["class_multiplicity_certificate", "within_pair_isomorphism"]}


def case_resource_prerequisite_break(env: dict[str, Any]) -> dict[str, Any]:
    rows = []
    corrupted_key = None
    for key in expected_timing_keys():
        resource = True
        if corrupted_key is None and key[0] == "top_control":
            resource = False
            corrupted_key = key
        rows.append(timing_row(key, resource=resource))
    index = TimingIndex(rows)
    facts = index.cost_related_hard_facts()
    require(all(facts.values()), "counterexample requires the derived timing hard facts to remain all true")
    unresolved = list(index.iter_unresolved())
    require(len(unresolved) == 1 and unresolved[0]["reason"] == "invalid_input", "false resource observation must remain visible")
    names = env["contract"].contract["runner"]["hard_validity_reducer"]["completed_valid_if_and_only_if"]
    supplied = supplied_hard_prerequisites(env["contract"], {name: True for name in names})
    require(supplied["supplied_conjunction"] is True, "supplied true conjunction")
    return {"breaking_observation": "all exposed timing hard facts true while one retained resource_accounted flag is false",
            "contradictory_key": list(corrupted_key), "unresolved_timing_rows": 1,
            "supplied_resource_and_custody_receipts_valid": True}


def case_partial_actual_only_break(env: dict[str, Any]) -> dict[str, Any]:
    scratch = env["case_scratch"] / "partial"
    scratch.mkdir()
    row = raw_record(ordinal=1, component="reporting_and_artifact_publication", scope="scaffolding",
                     phase="publication", status="partial", cpu=None, wall=None, rss=None)
    context = AllocationContext(context_data())
    with CostLedger(env["contract"], scratch) as ledger:
        ledger.add(row); ledger.finalize()
        inventory = [{"raw_cost_row_id": row["raw_cost_row_id"],
                      "canonical_record_sha256": sha(canonical_json(row))}]
        ledger.compare_capture_inventory(inventory)
        edges = list(iter_expected_edges(ledger, context))
        require(len(edges) == 1 and edges[0]["strategy_view"] == "actual_only_scaffolding", "partial actual-only edge")
        result = reduce_cost_component(ledger, context, TimingIndex([]), edges)
    require(result["state"] == "cost_projection_computed", "partial actual-only row should expose the implementation gap")
    require(result["actual_accounting"]["partial_or_failed_row_count"] == 1 and result["actual_accounting"]["CPU_nanoseconds"] is None,
            "partial physical observation retained")
    return {"breaking_observation": "cost_projection_computed despite retained partial resource-unaccounted actual-only leaf",
            "cost_projection_cells_resolved": 0}


def case_panel_and_loo(env: dict[str, Any]) -> dict[str, Any]:
    context = AllocationContext(context_data())
    estimates = {(view, f, e, u, seed, q): BlockEstimate(0, (Fraction(value),)*7, None)
                 for view, value in (("scalar", 12), ("transport", 10))
                 for f, e, u, seed, q in product(FIXTURES, ENDPOINTS, COORDINATES, SEEDS, QS)}
    outputs = panel_cost_outputs(context, estimates)
    require((len(outputs["R_cells"]), len(outputs["R_global"]), len(outputs["q_star"])) == (288, 8, 36), "288/8/36 output identity")
    require(statistical_branch(outputs["R_cells"], True) == "finite_panel_signal_only", "exact 6/5 threshold")
    governing = [row for row in outputs["R_cells"] if row["seed"] == 606103 and row["q"] == 4096]
    require(len(governing) == 36 and all([item["omitted_block"] for item in row["leave_one_out"]] == list(BLOCKS) for row in governing), "36 labelled LOO cells")
    changed = copy.deepcopy(outputs)
    changed["R_cells"][0] = copy.deepcopy(changed["R_cells"][1])
    expect_cost_error(lambda: compare_cost_projection(outputs, changed), "duplicate_cell")
    invalid = BlockEstimate(0, (Fraction(1),)*6 + (None,), None)
    expect_cost_error(lambda: invalid.total(6), "invalid_original_normalized_block")
    ratio_of_sums = copy.deepcopy(estimates)
    for key in ratio_of_sums:
        view, _fixture, endpoint, _coordinate, _seed, _q = key
        if endpoint in ("K0", "K1"):
            value = 100 if (view == "scalar") == (endpoint == "K0") else 1
            ratio_of_sums[key] = BlockEstimate(0, (Fraction(value),)*7, None)
    aggregated = panel_cost_outputs(context, ratio_of_sums)
    require(all(row["ratio"] == {"kind": "value", "value": {"numerator": 1, "denominator": 1}}
                for row in aggregated["R_cells"] if row["class"] == "C0"),
            "class aggregation must be ratio of endpoint sums")
    label_sensitive = copy.deepcopy(estimates)
    for key in label_sensitive:
        if key[0] == "scalar":
            label_sensitive[key] = BlockEstimate(0, tuple(Fraction(value) for value in (10, 11, 12, 13, 14, 15, 16)), None)
        else:
            label_sensitive[key] = BlockEstimate(0, (Fraction(10),)*7, None)
    expected_labelled = panel_cost_outputs(context, label_sensitive)
    relabelled = copy.deepcopy(expected_labelled)
    row = next(item for item in relabelled["R_cells"] if item["seed"] == 606103 and item["q"] == 4096)
    row["leave_one_out"][0]["omitted_block"], row["leave_one_out"][6]["omitted_block"] = 6, 0
    expect_cost_error(lambda: compare_cost_projection(expected_labelled, relabelled),
                      "cell_projection_disagrees_with_retained_costs")
    estimates[("scalar", "I0F0", "K0", 1, 606103, 4096)] = BlockEstimate(0, (Fraction(1),)*7, None)
    mixed = panel_cost_outputs(context, estimates)
    require(statistical_branch(mixed["R_cells"], True) == "inconclusive", "global summary cannot override one failing cell")
    return {"cells": 288, "globals": 8, "q_stars": 36, "labelled_omissions": 252}


def case_hard_conjunction(env: dict[str, Any]) -> dict[str, Any]:
    names = env["contract"].contract["runner"]["hard_validity_reducer"]["completed_valid_if_and_only_if"]
    all_true = {name: True for name in names}
    require(supplied_hard_prerequisites(env["contract"], all_true)["supplied_conjunction"] is True, "all hard prerequisites")
    missing = dict(all_true); missing.pop(names[0])
    require(supplied_hard_prerequisites(env["contract"], missing)["supplied_conjunction"] is False, "missing prerequisite")
    false = dict(all_true); false[names[-1]] = False
    require(supplied_hard_prerequisites(env["contract"], false)["supplied_conjunction"] is False, "false prerequisite")
    null = dict(all_true); null[names[-1]] = None
    require(supplied_hard_prerequisites(env["contract"], null)["supplied_conjunction"] is False, "unknown prerequisite")
    return {"hard_prerequisite_count": len(names), "missing_false_null_refused": True}


CASES: tuple[dict[str, Any], ...] = (
    {"id": "bindings.all51", "function": case_bound_inputs,
     "predicate": "all 51 handoff-bound inputs exist and hash exactly"},
    {"id": "snapshot.nine_artifacts", "function": case_snapshot_bindings,
     "predicate": "snapshot binds all nine final producer artifacts"},
    {"id": "custody.producer_all_attempts", "function": case_producer_custody,
     "predicate": "785 case starts/results, both source versions and supervisor custody reconcile"},
    {"id": "blind.case_A", "function": case_blind_arithmetic_a,
     "predicate": "case A scores, winner, actual spend, cold totals and ratio equal blind derivation"},
    {"id": "blind.case_B", "function": case_blind_arithmetic_b,
     "predicate": "case B normalizes before selection but charges physical selection spend"},
    {"id": "carrier.strict_json_fraction", "function": case_strict_carriers,
     "predicate": "duplicate keys, float tokens, bool integers and unreduced fractions are refused"},
    {"id": "context.origins_classes", "function": case_context_identity,
     "predicate": "origins are explicit global ordinals and class aliases are refused"},
    {"id": "allocation.integer_remainders", "function": case_integer_allocations,
     "predicate": "72 and 8 target groups preserve exact arbitrary integer costs in canonical order"},
    {"id": "ledger.capture_identity", "function": case_capture_identity,
     "predicate": "adjacent intervals are accepted and overlapping physical intervals refused"},
    {"id": "break.rollup_completeness", "function": case_rollup_completeness_break,
     "predicate": "known-incomplete level/multiplicity rollup is currently accepted"},
    {"id": "break.resource_prerequisite", "function": case_resource_prerequisite_break,
     "predicate": "a supplied true custody prerequisite does not override a retained false resource fact"},
    {"id": "break.partial_actual_only", "function": case_partial_actual_only_break,
     "predicate": "partial unaccounted actual-only work must prevent a completed cost projection"},
    {"id": "reduction.panel_loo", "function": case_panel_and_loo,
     "predicate": "all 288/8/36 identities, labels, joint omission and per-cell gate hold"},
    {"id": "hard.conjunction", "function": case_hard_conjunction,
     "predicate": "missing, false and unknown hard prerequisites cannot count true"},
)


def run(attempt: Path) -> int:
    global CostError, CostContract, CostLedger, canonical_json, strict_json_loads
    global validate_raw_semantics, actual_campaign_accounting, AllocationContext, FIXTURES, INTERVALS, ENDPOINTS
    global COORDINATES, SEEDS, QS, EdgeGroup, expected_groups, edges_from_groups
    global iter_expected_edges, TimingIndex, expected_timing_keys, BlockEstimate, BLOCKS
    global select_candidates, ratio_of_totals, decode_fraction, panel_cost_outputs
    global statistical_branch, compare_cost_projection, supplied_hard_prerequisites
    global reduce_cost_component

    attempt = attempt.resolve(strict=True)
    source = attempt / "source"
    sys.path.insert(0, str(source))
    from costs import (CostError, CostContract, CostLedger, canonical_json,
                       strict_json_loads, validate_raw_semantics,
                       actual_campaign_accounting)
    from allocations import (AllocationContext, FIXTURES, INTERVALS, ENDPOINTS,
                             COORDINATES, SEEDS, QS, EdgeGroup, expected_groups,
                             edges_from_groups, iter_expected_edges)
    from reducers import (TimingIndex, expected_timing_keys, BlockEstimate, BLOCKS,
                         select_candidates, ratio_of_totals, decode_fraction,
                         panel_cost_outputs, statistical_branch,
                         compare_cost_projection, supplied_hard_prerequisites,
                         reduce_cost_component)

    env = {
        "attempt": attempt,
        "source": source,
        "control": attempt / "control",
        "repo_inputs": attempt / "inputs" / "repo",
        "case_scratch": attempt / "case-scratch",
    }
    env["case_scratch"].mkdir(exist_ok=False)
    contract_path = env["repo_inputs"] / "coordination/experiment-reserve/BATCH-45b4d5/corrections/TASK-20260908-d18d13/EXP-ECDLP-1b1b99.yaml"
    schema_path = env["repo_inputs"] / "coordination/experiment-reserve/BATCH-45b4d5/corrections/TASK-20260908-d18d13/schema.json"
    env["contract"] = CostContract(contract_path.read_bytes(), schema_path.read_bytes())

    journal_path = attempt / "case-journal.jsonl"
    failures = 0
    previous = signal.getsignal(signal.SIGALRM)

    def timeout(_signum: int, _frame: Any) -> None:
        raise TimeoutError("independent fixed case exceeded 60-second watchdog")

    signal.signal(signal.SIGALRM, timeout)
    try:
        with journal_path.open("x", encoding="utf-8") as journal:
            def persist(row: dict[str, Any]) -> None:
                text = json.dumps(row, sort_keys=True, ensure_ascii=True, allow_nan=False)
                journal.write(text + "\n"); journal.flush(); os.fsync(journal.fileno())
                print(text, flush=True)

            for case in CASES:
                started_wall = time.monotonic_ns()
                started_cpu = time.process_time_ns()
                definition = {"id": case["id"], "predicate": case["predicate"]}
                persist({"event": "case_start", "id": case["id"], "pid": os.getpid(),
                         "case_definition_sha256": sha(canonical_case(definition)),
                         "monotonic_ns": started_wall, "process_cpu_ns": started_cpu})
                signal.setitimer(signal.ITIMER_REAL, MAX_CASE_SECONDS)
                error = None
                observation = None
                try:
                    observation = case["function"](env)
                except Exception as caught:
                    failures += 1
                    error = {"type": type(caught).__name__, "detail": str(caught),
                             "traceback": traceback.format_exc()}
                finally:
                    signal.setitimer(signal.ITIMER_REAL, 0)
                persist({"event": "case_result", "id": case["id"], "pid": os.getpid(),
                         "outcome": "pass" if error is None else "fail", "error": error,
                         "observation": observation,
                         "wall_ns": time.monotonic_ns() - started_wall,
                         "process_cpu_ns": time.process_time_ns() - started_cpu})
            persist({"event": "suite_terminal", "pid": os.getpid(),
                     "controls_started": len(CASES), "controls_completed": len(CASES),
                     "passed": len(CASES) - failures, "failed": failures,
                     "scientific_runs": 0, "fixture_children": 0})
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)
    return 1 if failures else 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempt", required=True)
    args = parser.parse_args()
    raise SystemExit(run(Path(args.attempt)))
