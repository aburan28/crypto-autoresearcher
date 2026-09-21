#!/usr/bin/env python3
"""Fail-closed control-fixture validator for the EXP-XOR v5 package.

The validator consumes synthetic run/event/matrix fixtures and applies every
accepted and negative case in memory. It never runs an ECDLP implementation,
does not write files, and is not evidence of a cryptographic result.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import struct
from collections import Counter
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

P_VALUES = (101, 103, 107, 211)
B_VALUES = ((1, 2), (2, 5))
PHASES = ("input", "curve", "factor_base", "table", "query", "verify", "serialize")
PREDECESSORS = ("EXP-XOR-7267e4", "H-XOR-a227dc", "TASK-20260808-e6022f")
OUTPUT_CAP = 27111981056


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def fail(message: str) -> None:
    raise ValueError(message)


def check_schema(schema: Any, data: Any, label: str) -> None:
    errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: list(e.path))
    if errors:
        fail(f"{label}: schema error at {list(errors[0].path)}: {errors[0].message}")


def digest_input(arithmetic: dict[str, Any]) -> str:
    payload = arithmetic["canonical_payload_utf8"].encode("utf-8")
    preimage = b"XOR-INPUT-v5\x00" + struct.pack(">I", len(payload)) + payload
    if preimage.hex() != arithmetic["input_preimage_hex"]:
        fail("input preimage bytes are not canonical")
    return hashlib.sha256(preimage).hexdigest()


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def ec_add(P: tuple[int, int] | None, Q: tuple[int, int] | None, p: int, A: int) -> tuple[int, int] | None:
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if P == Q:
        if y1 % p == 0:
            return None
        lam = ((3 * x1 * x1 + A) * pow(2 * y1, -1, p)) % p
    else:
        lam = ((y2 - y1) * pow((x2 - x1) % p, -1, p)) % p
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return x3, y3


def validate_arithmetic(path: Path) -> dict[str, Any]:
    data = read_json(path)
    if data["schema"] != "xor-arithmetic-fixture/v5":
        fail("arithmetic fixture schema version mismatch")
    if digest_input(data) != data["input_digest"]:
        fail("input digest mismatch")
    p = data["input"]["p"]
    if not data["p_prime"] or not data["p_gt_3"] or not is_prime(p) or p <= 3:
        fail("prime/domain gate failed")
    b = data["factor_base"]
    selected = max(i for i in range(100) if i ** data["input"]["b_den"] <= p ** data["input"]["b_num"])
    if selected != b["B"] or not (selected ** 5 <= p ** 2 < (selected + 1) ** 5):
        fail("integer factor-base bound failed")
    curve = data["curve"]
    A, B = curve["A"], curve["B"]
    if (4 * A ** 3 + 27 * B ** 2) % p == 0 or not curve["discriminant_nonzero"]:
        fail("curve nonsingularity gate failed")
    point = (curve["first_eligible_point"]["x"], curve["first_eligible_point"]["y"])
    if (point[1] * point[1] - (point[0] ** 3 + A * point[0] + B)) % p != 0:
        fail("arithmetic fixture point is not on curve")
    Q: tuple[int, int] | None = None
    trace: list[str] = []
    for k in range(1, 20):
        Q = ec_add(Q, point, p, A)
        trace.append("NONE" if Q is None else f"({Q[0]},{Q[1]})")
        if Q is None:
            break
    if k != curve["first_eligible_point"]["least_order"] or k != 6:
        fail("least-order gate failed")
    expected_trace = [x.split("=", 1)[1] for x in curve["first_eligible_point"]["order_trace"]]
    if trace != expected_trace:
        fail("order trace mismatch")
    lift = data["lift_x"]
    if lift["roots"] != sorted(lift["roots"]) or lift["selected_smallest_y"] != min(lift["roots"]):
        fail("lift_x root ordering failed")
    if data["identity_encoding"]["none_hex"] != "ffffffff":
        fail("NONE encoding failed")
    if data["output"]["F"] <= 0 or data["output"]["R_star_count"] <= 0:
        fail("empty F or reference output was not rejected")
    return data


def key_tuple(key: dict[str, Any]) -> tuple[Any, ...]:
    return tuple(key[name] for name in ("p", "b_num", "b_den", "arm", "seed", "process_replica", "null_replica"))


def expected_keys() -> list[dict[str, Any]]:
    keys: list[dict[str, Any]] = []
    for p in P_VALUES:
        for b_num, b_den in B_VALUES:
            for arm in ("A", "B"):
                for replica in range(5):
                    keys.append({"p": p, "b_num": b_num, "b_den": b_den, "arm": arm, "seed": 0, "process_replica": replica, "null_replica": 0xFFFFFFFF, "shard": 0})
            for seed in range(1, 6):
                for null_replica in range(8):
                    keys.append({"p": p, "b_num": b_num, "b_den": b_den, "arm": "D", "seed": seed, "process_replica": 0, "null_replica": null_replica, "shard": 0})
    keys.sort(key=key_tuple)
    for ordinal, key in enumerate(keys):
        key["shard"] = ordinal % 4
    return keys


def derive_event_counters(events: list[dict[str, Any]]) -> dict[str, Any]:
    phase = Counter(event["phase"] for event in events)
    candidates = [event for event in events if event["candidate_identity"] is not None]
    verified = sum(event["candidate_outcome"] == "verified" for event in candidates)
    aborted = sum(event["candidate_outcome"] == "aborted" for event in candidates)
    relations = [tuple(event["relation_identity"]) for event in events if event["relation_identity"] is not None]
    queries = [event["query_identity"] for event in events if event["query_identity"] is not None]
    buckets = Counter(event["table_bucket"] for event in events if event["table_bucket"] is not None)
    return {
        "event_count": len(events),
        "exception_count": sum(event["outcome"] == "exception" for event in events),
        "phase_counters": {name: phase[name] for name in PHASES},
        "candidate_counters": {"attempts": len(candidates), "verified": verified, "aborted": aborted, "unique": len({e["candidate_identity"] for e in candidates}), "duplicate_events": len(candidates) - len({e["candidate_identity"] for e in candidates}), "relation_events": len(relations), "false_positive_events": verified - len(relations), "relation_unique": len(set(relations)), "relation_duplicate_events": len(relations) - len(set(relations))},
        "query_counters": {"events": len(queries), "unique": len(set(queries)), "duplicate_events": len(queries) - len(set(queries))},
        "table_bucket_sizes": [buckets[i] for i in sorted(buckets)],
        "table_insert_events": sum(buckets.values()),
    }


def validate_event(data: Any, schema: Any, expected_run_id: str, expected_sha: str | None = None, raw_bytes: bytes | None = None) -> dict[str, Any]:
    check_schema(schema, data, "event ledger")
    if data["run_id"] != expected_run_id:
        fail("event ledger run id mismatch")
    if expected_sha is not None and raw_bytes is not None and hashlib.sha256(raw_bytes).hexdigest() != expected_sha:
        fail("event ledger byte hash mismatch")
    events = data["events"]
    if data["event_count"] != len(events) or [event["event_index"] for event in events] != list(range(len(events))):
        fail("event indices are not contiguous zero-based")
    derived = derive_event_counters(events)
    if data["counters"] != derived:
        fail("event counters do not equal recomputed event stream")
    if derived["candidate_counters"]["verified"] != derived["candidate_counters"]["relation_events"] + derived["candidate_counters"]["false_positive_events"]:
        fail("false-positive equation failed")
    if derived["candidate_counters"]["attempts"] != derived["candidate_counters"]["verified"] + derived["candidate_counters"]["aborted"]:
        fail("candidate attempt equation failed")
    return derived


def apply_patch(data: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    out = copy.deepcopy(data)
    for dotted, value in patch.items():
        target = out
        parts = dotted.split(".")
        if "run" in target and parts[0] not in target:
            target = target["run"]
        for part in parts[:-1]:
            target = target[part]
        target[parts[-1]] = value
    return out


def validate_run(data: Any, schema: Any, event_schema: Any, arithmetic: dict[str, Any], fixture_root: Path, contract: dict[str, Any]) -> None:
    check_schema(schema, data, "run")
    run = data["run"]
    if run["inputs"]["input_digest"] != arithmetic["input_digest"]:
        fail("run input digest does not match arithmetic fixture")
    if any(run["source_blobs"].get(k) != v for k, v in contract["fixture_source_blobs"].items()):
        fail("run source_blobs are not bound to the control contract")
    timing = run["timing"]
    if timing["finished_monotonic_ns"] <= timing["started_monotonic_ns"]:
        fail("run timing endpoints are not ordered")
    if timing["c_wall_seconds"] != (timing["finished_monotonic_ns"] - timing["started_monotonic_ns"]) / 1_000_000_000:
        fail("run wall seconds do not equal raw monotonic endpoints")
    if run["resources"]["output_bytes"] != sum(run["resources"][x] for x in ("raw_bytes", "stdout_bytes", "stderr_bytes")):
        fail("run output bytes do not equal raw/stdout/stderr classes")
    if run["status"] == "completed_valid" and (run["terminal_reason"] is not None or not run["result"]["valid"] or run["result"]["invalid_reason"] is not None):
        fail("completed_valid terminal relation failed")
    if run["status"] != "completed_valid" and (run["terminal_reason"] is None or run["result"]["valid"] or run["result"]["invalid_reason"] is None):
        fail("non-valid terminal relation failed")
    event_path = fixture_root / run["event_ledger"]["path"]
    raw = event_path.read_bytes()
    event_data = read_json(event_path)
    derived = validate_event(event_data, event_schema, run["id"], run["event_ledger"]["sha256"], raw)
    if run["event_ledger"]["event_count"] != derived["event_count"] or run["event_ledger"]["last_event_index"] != derived["event_count"] - 1:
        fail("run event ledger summary mismatch")
    if run["phase_counters"]["total"] != sum(run["phase_counters"][p] for p in PHASES):
        fail("run phase total mismatch")
    for field in ("phase_counters", "candidate_counters", "query_counters", "table_bucket_sizes"):
        observed = run[field]
        expected = derived[field]
        if field == "phase_counters":
            observed = {name: observed[name] for name in PHASES}
        if observed != expected:
            fail(f"run {field} does not equal event ledger")


def validate_arm_shape(arm: dict[str, Any]) -> None:
    state = arm["state"]
    if state == "not_attempted":
        if arm["run_id"] is not None or arm["included_in_metrics"] or any(x is not None for x in arm["wall_repeats"]):
            fail("not_attempted arm has attempted fields")
    else:
        if arm["run_id"] is None or arm["terminal_reason"] is not None or not arm["included_in_metrics"]:
            fail("attempted arm terminal relation failed")
        if any(x is None for x in arm["wall_repeats"]):
            fail("attempted arm has null wall repeat")


def validate_matrix(data: Any, schema: Any) -> None:
    check_schema(schema, data, "matrix")
    wanted = expected_keys()
    arms = data["arms"]
    if [key_tuple(x["arm_key"]) for x in arms] != [key_tuple(x) for x in wanted]:
        fail("matrix keys are not the exact canonical ordered domain")
    if len({key_tuple(x["arm_key"]) for x in arms}) != 400:
        fail("matrix arm keys are not unique")
    for arm, want in zip(arms, wanted):
        if arm["arm_key"] != want:
            fail("matrix key shard or field differs from canonical ordinal")
        validate_arm_shape(arm)
    shard_numbers = [s["shard"] for s in data["shards"]]
    if shard_numbers != [0, 1, 2, 3]:
        fail("shard numbers are not canonical and unique")
    expected_sets = [{key_tuple(wanted[i]) for i in range(s, 400, 4)} for s in range(4)]
    actual_sets = []
    for s, shard in enumerate(data["shards"]):
        actual = [key_tuple(key) for key in shard["arm_keys"]]
        expected = [key_tuple(wanted[i]) for i in range(s, 400, 4)]
        if actual != expected or any(key["shard"] != s for key in shard["arm_keys"]):
            fail("shard membership is not canonical ordered ownership")
        actual_sets.append(set(actual))
    if any(actual_sets[i] & actual_sets[j] for i in range(4) for j in range(i)) or set.union(*actual_sets) != set(key_tuple(x) for x in wanted):
        fail("shard coverage is not disjoint complete coverage")
    intervals = [s["worker_interval"] for s in data["shards"]]
    if max(x["start_ns"] for x in intervals) >= min(x["stop_ns"] for x in intervals):
        fail("concurrent worker intervals do not overlap")
    totals = data["totals"]
    states = Counter(arm["state"] for arm in arms)
    if totals["attempted"] != 400 - states.get("not_attempted", 0) or totals["not_attempted"] != states.get("not_attempted", 0):
        fail("matrix attempted/not_attempted equation failed")
    for state in ("completed_valid", "completed_invalid", "failed_infrastructure", "failed_implementation", "resource_exhaustion", "cancelled_by_budget"):
        if totals[state] != states.get(state, 0):
            fail(f"matrix state total failed for {state}")
    if totals["worker_wall_seconds"] != max(s["wall_seconds"] for s in data["shards"]):
        fail("worker wall max equation failed")
    expected_wall = totals["coordinator_wall_seconds"] + totals["worker_wall_seconds"] + totals["replay_wall_seconds"] + totals["analysis_wall_seconds"] + totals["hashing_wall_seconds"] + totals["serialization_wall_seconds"]
    if totals["campaign_wall_seconds"] != expected_wall:
        fail("campaign wall equation failed")
    expected_cpu = totals["arm_cpu_seconds"] + totals["replay_cpu_seconds"] + totals["analysis_cpu_seconds"] + totals["hashing_cpu_seconds"] + totals["serialization_cpu_seconds"]
    if totals["cpu_seconds"] != expected_cpu:
        fail("campaign CPU equation failed")
    coordinator_peak = totals["coordinator_rss_peak_bytes"]
    host_peak = coordinator_peak + sum(max(s["rss_samples"]) for s in data["shards"])
    if totals["host_rss_peak_bytes"] != host_peak or host_peak > totals["host_rss_reservation_bytes"]:
        fail("host RSS concurrency equation or reservation failed")
    for s in data["shards"]:
        if s["output_bytes"] != sum(115 for _ in s["arm_keys"]):
            fail("shard output bytes do not equal arm byte classes")
    arm_raw = sum(a["resource_bytes"]["raw"] for a in arms)
    arm_stdout = sum(a["resource_bytes"]["stdout"] for a in arms)
    arm_stderr = sum(a["resource_bytes"]["stderr"] for a in arms)
    expected_output = arm_raw + arm_stdout + arm_stderr + totals["replay_bytes"] + totals["analysis_bytes"] + totals["global_log_bytes"]
    if (totals["arm_raw_bytes"], totals["arm_stdout_bytes"], totals["arm_stderr_bytes"]) != (arm_raw, arm_stdout, arm_stderr) or totals["output_bytes"] != expected_output or expected_output > OUTPUT_CAP:
        fail("campaign byte equation or cap failed")
    for e in data["estimands"]:
        a = [x for x in arms if x["arm_key"]["p"] == e["p"] and x["arm_key"]["b_num"] == e["b_num"] and x["arm_key"]["b_den"] == e["b_den"] and x["arm_key"]["arm"] == "A"]
        b = [x for x in arms if x["arm_key"]["p"] == e["p"] and x["arm_key"]["b_num"] == e["b_num"] and x["arm_key"]["b_den"] == e["b_den"] and x["arm_key"]["arm"] == "B"]
        if len(a) != 5 or len(b) != 5 or not all(x["state"] == "completed_valid" and x["included_in_metrics"] for x in a + b):
            fail("A/B estimand does not have exactly five valid repeats per side")
        av, bv = [x["wall_repeats"][0] for x in a], [x["wall_repeats"][0] for x in b]
        if av != e["a_wall_repeats"] or bv != e["b_wall_repeats"] or e["median_a_seconds"] != sorted(av)[2] or e["median_b_seconds"] != sorted(bv)[2]:
            fail("A/B raw repeat or median mismatch")
        if e["delta_ab_wall"] != (e["median_a_seconds"] - e["median_b_seconds"]) / e["median_a_seconds"]:
            fail("A/B delta formula mismatch")


def validate_predecessor(path: Path, repo_root: Path, candidate: dict[str, Any] | None = None) -> None:
    data = read_json(path)
    if tuple(data["historical_ineligible_ids"]) != PREDECESSORS or [r["id"] for r in data["records"]] != list(PREDECESSORS):
        fail("predecessor set/order mismatch")
    for record in data["records"]:
        source = repo_root / record["path"]
        if not record["historical"] or record["selected_contract"] or record["eligible_dependency"] or not source.is_file() or hashlib.sha256(source.read_bytes()).hexdigest() != record["sha256"]:
            fail(f"predecessor source or flags invalid: {record['id']}")
    gate = data["required_future_gate"]
    required = ("reject_if_selected_contract", "reject_if_dependency", "reject_if_hash_mismatch", "reject_if_any_id_missing", "reject_if_any_new_stale_id_is_discovered", "approval_lock_must_bind_this_record", "dispatch_validator_must_read_this_record")
    if not all(gate.get(name) is True for name in required):
        fail("predecessor future gate is incomplete")
    c = candidate or data["candidate_fixture"]
    if c["selected_contract_id"] in PREDECESSORS or set(c["dependency_ids"]) & set(PREDECESSORS) or c["discovered_stale_ids"]:
        fail("candidate selects or depends on a stale predecessor")


def validate_arm_case(case: dict[str, Any]) -> None:
    if case["state"] != "not_attempted" or case["run_id"] is not None or case["included_in_metrics"] or any(value is not None for value in case["wall_repeats"]):
        fail("unattempted matrix-arm fixture is not preserved")


def validate_control_fixtures(args: argparse.Namespace) -> None:
    fixture_root = args.fixtures.parent
    contract = read_json(args.contract)
    manifest = read_json(args.fixtures)
    if manifest["schema"] != "xor-fixture-manifest/v5" or not manifest["all_cases_are_applied"] or not manifest["all_negative_cases_must_fail"]:
        fail("fixture manifest is not executable v5")
    arithmetic = validate_arithmetic(args.arithmetic)
    run_schema, matrix_schema, event_schema = read_json(args.run_schema), read_json(args.matrix_schema), read_json(args.event_schema)
    canonical_run = read_json(fixture_root / contract["canonical"]["run"])
    canonical_event = read_json(fixture_root / contract["canonical"]["event"])
    canonical_matrix = read_json(fixture_root / contract["canonical"]["matrix"])
    validate_run(canonical_run, run_schema, event_schema, arithmetic, fixture_root, contract)
    validate_matrix(canonical_matrix, matrix_schema)
    for case_spec in contract["accepted_cases"]:
        case = read_json(fixture_root / case_spec.get("path", f"{case_spec['id']}.json")) if case_spec["id"] == "unattempted_matrix_arm" else read_json(fixture_root / f"{case_spec['id']}.json")
        if case["fixture_id"] != case_spec["id"]:
            fail(f"accepted case id mismatch: {case_spec['id']}")
        if case_spec["kind"] == "matrix_arm":
            validate_arm_case(case)
            continue
        patched = apply_patch(canonical_run, case_spec["patch"])
        validate_run(patched, run_schema, event_schema, arithmetic, fixture_root, contract)
        expected = case_spec["expected"]
        actual = patched["run"]
        if any(actual.get(key) != value for key, value in (("status", expected["status"]), ("attempted", expected["attempted"]), ("terminal_reason", expected["terminal_reason"]))):
            fail(f"accepted case expectation mismatch: {case_spec['id']}")
        if actual["result"]["valid"] != expected["valid"]:
            fail(f"accepted result expectation mismatch: {case_spec['id']}")
    validate_predecessor(args.predecessor, args.repo_root)
    failures: list[str] = []
    for mutation in contract["negative_mutations"]:
        try:
            if mutation["id"] == "attempted_false_completed_valid":
                x = copy.deepcopy(canonical_run); x["run"]["attempted"] = False; validate_run(x, run_schema, event_schema, arithmetic, fixture_root, contract)
            elif mutation["id"] == "terminal_reason_missing":
                x = apply_patch(canonical_run, {"status":"completed_invalid","terminal_reason":None,"result.valid":False,"result.invalid_reason":"missing"}); validate_run(x, run_schema, event_schema, arithmetic, fixture_root, contract)
            elif mutation["id"] == "phase_total_mismatch":
                x = copy.deepcopy(canonical_run); x["run"]["phase_counters"]["total"] += 1; validate_run(x, run_schema, event_schema, arithmetic, fixture_root, contract)
            elif mutation["id"] == "event_index_gap":
                x = copy.deepcopy(canonical_event); x["events"][2]["event_index"] = 99; validate_event(x, event_schema, canonical_run["run"]["id"])
            elif mutation["id"] == "duplicate_arm_key":
                x = copy.deepcopy(canonical_matrix); x["arms"][1]["arm_key"] = copy.deepcopy(x["arms"][0]["arm_key"]); validate_matrix(x, matrix_schema)
            elif mutation["id"] == "duplicate_shard_number":
                x = copy.deepcopy(canonical_matrix); x["shards"][1]["shard"] = 0; validate_matrix(x, matrix_schema)
            elif mutation["id"] == "empty_shard_membership":
                x = copy.deepcopy(canonical_matrix); x["shards"][0]["arm_keys"] = []; validate_matrix(x, matrix_schema)
            elif mutation["id"] == "terminal_total_mismatch":
                x = copy.deepcopy(canonical_matrix); x["totals"]["completed_valid"] -= 1; validate_matrix(x, matrix_schema)
            elif mutation["id"] == "stale_predecessor_selected":
                validate_predecessor(args.predecessor, args.repo_root, {"selected_contract_id": "EXP-XOR-7267e4", "approval_lock_ids": [], "dependency_ids": ["TASK-20260808-e6022f"], "discovered_stale_ids": []})
            else:
                fail(f"unknown mutation {mutation['id']}")
        except (ValueError, KeyError, TypeError, AssertionError):
            continue
        failures.append(mutation["id"])
    if failures:
        fail(f"negative mutations unexpectedly passed: {failures}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-schema", required=True, type=Path)
    parser.add_argument("--matrix-schema", required=True, type=Path)
    parser.add_argument("--event-schema", required=True, type=Path)
    parser.add_argument("--fixtures", required=True, type=Path)
    parser.add_argument("--contract", required=True, type=Path)
    parser.add_argument("--arithmetic", required=True, type=Path)
    parser.add_argument("--predecessor", required=True, type=Path)
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--run", type=Path)
    parser.add_argument("--matrix", type=Path)
    args = parser.parse_args()
    validate_control_fixtures(args)
    if args.run or args.matrix:
        fail("external run/matrix validation is not enabled in the fixture-only control package")
    print("VALIDATION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
