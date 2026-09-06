#!/usr/bin/env python3
"""Read-only control-plane validator for the EXP-XOR v4 freeze package.

This validator validates schemas, fixture records, exact matrix bookkeeping,
event/counter equations, and predecessor exclusion. It never runs an ECDLP
arm and never writes a file.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from collections import Counter
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

P_VALUES = (101, 103, 107, 211)
B_VALUES = ((2, 5), (1, 2))
PREDECESSORS = ("EXP-XOR-7267e4", "H-XOR-a227dc", "TASK-20260808-e6022f")
PHASES = ("input", "curve", "factor_base", "table", "query", "verify", "serialize")
OUTPUT_CAP = 27111981056


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def fail(message: str) -> None:
    raise ValueError(message)


def check_schema(schema: Any, data: Any, label: str) -> None:
    errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: list(e.path))
    if errors:
        fail(f"{label}: schema error at {list(errors[0].path)}: {errors[0].message}")


def typed_field(tag: int, value: bytes) -> bytes:
    return bytes([tag]) + struct.pack(">I", len(value)) + value


def seed_bytes(fixture: dict[str, Any]) -> bytes:
    fields = [
        (1, struct.pack(">Q", fixture["campaign_seed"])),
        (2, struct.pack(">I", fixture["p"])),
        (3, struct.pack(">I", fixture["b_num"])),
        (4, struct.pack(">I", fixture["b_den"])),
        (5, fixture["arm"].encode("ascii")),
        (6, struct.pack(">I", fixture["process_replica"])),
        (7, struct.pack(">I", fixture["null_replica"])),
        (8, fixture["query_schedule_id"].encode("ascii")),
    ]
    return b"".join(typed_field(tag, value) for tag, value in fields)


def validate_prng_fixture(contract: dict[str, Any]) -> None:
    fixture = contract["canonical_prng"]["fixture"]
    raw = seed_bytes(fixture)
    if raw.hex() != fixture["seed_hex"]:
        fail("PRNG fixture seed bytes mismatch")
    if hashlib.sha256(raw).hexdigest() != fixture["seed_sha256"]:
        fail("PRNG fixture seed digest mismatch")
    threshold = (256 // fixture["p"]) * fixture["p"]
    if threshold != fixture["threshold_L"]:
        fail("PRNG fixture rejection threshold mismatch")
    expected = fixture["first_consumed_words"]
    for item in expected:
        counter = item["counter"]
        digest = hashlib.sha256(
            b"XOR-PRNG-v1" + struct.pack(">I", len(raw)) + raw + struct.pack(">Q", counter)
        ).digest()
        word = int.from_bytes(digest[:8], "big")
        byte = word & 0xFF
        accepted = byte < threshold
        query_x = byte % fixture["p"] if accepted else None
        if item["word_hex"] != f"{word:016x}" or item["byte"] != f"{byte:02x}":
            fail(f"PRNG fixture word mismatch at counter {counter}")
        if item["accepted"] != accepted or item["query_x"] != query_x:
            fail(f"PRNG fixture acceptance mismatch at counter {counter}")
    if [x["query_index"] for x in expected if x["accepted"]] != [0, 1]:
        fail("PRNG fixture query indices are not zero-based")


def key_tuple(key: dict[str, Any]) -> tuple[Any, ...]:
    return tuple(key[name] for name in ("p", "b_num", "b_den", "arm", "seed", "process_replica", "null_replica"))


def expected_keys() -> list[dict[str, Any]]:
    keys: list[dict[str, Any]] = []
    for p in P_VALUES:
        for b_num, b_den in B_VALUES:
            for arm in ("A", "B"):
                for process_replica in range(5):
                    keys.append({"p": p, "b_num": b_num, "b_den": b_den, "arm": arm, "seed": 0, "process_replica": process_replica, "null_replica": 0xFFFFFFFF, "shard": 0})
            for seed in range(1, 6):
                for null_replica in range(8):
                    keys.append({"p": p, "b_num": b_num, "b_den": b_den, "arm": "D", "seed": seed, "process_replica": 0, "null_replica": null_replica, "shard": 0})
    keys.sort(key=key_tuple)
    for ordinal, key in enumerate(keys):
        key["shard"] = ordinal % 4
    return keys


def validate_run(data: Any, schema: Any) -> None:
    check_schema(schema, data, "run")
    run = data["run"]
    if run["phase_counters"]["total"] != sum(run["phase_counters"][phase] for phase in PHASES):
        fail("run phase total does not equal the seven-phase sum")
    ledger = run["event_ledger"]
    if ledger["event_count"] != run["phase_counters"]["total"]:
        fail("event count does not equal C_add total")
    if ledger["last_event_index"] != ledger["event_count"] - 1:
        fail("event ledger last index is not event_count-1")
    c = run["candidate_counters"]
    if c["attempts"] != c["verified"] + c["aborted"]:
        fail("candidate attempt conservation failed")
    if c["verified"] != c["relation_events"] + c["false_positive_events"]:
        fail("candidate verification conservation failed")
    if c["relation_events"] != c["relation_unique"] + c["relation_duplicate_events"]:
        fail("relation conservation failed")
    if c["attempts"] != c["unique"] + c["duplicate_events"]:
        fail("candidate identity conservation failed")
    q = run["query_counters"]
    if q["events"] != q["unique"] + q["duplicate_events"]:
        fail("query conservation failed")


def validate_matrix(data: Any, schema: Any) -> None:
    check_schema(schema, data, "matrix")
    expected = expected_keys()
    arms = data["arms"]
    actual = [key_tuple(item["arm_key"]) for item in arms]
    wanted = [key_tuple(item) for item in expected]
    if actual != wanted:
        fail("matrix arm keys are not the exact sorted 400-key domain")
    for item, wanted_key in zip(arms, expected):
        if item["arm_key"]["shard"] != wanted_key["shard"]:
            fail("matrix arm has incorrect canonical shard")
    shard_sets = []
    for shard in data["shards"]:
        if len(shard["arm_keys"]) != 100:
            fail("each shard must contain exactly 100 keys")
        shard_sets.append({key_tuple(key) for key in shard["arm_keys"]})
    if {s["shard"] for s in data["shards"]} != {0, 1, 2, 3}:
        fail("shard numbers are not exactly 0,1,2,3")
    if set.union(*shard_sets) != set(wanted) or sum(map(len, shard_sets)) != 400:
        fail("shard ownership is not disjoint complete coverage")
    if any(shard_sets[i] & shard_sets[j] for i in range(4) for j in range(i)):
        fail("shard ownership overlaps")
    states = Counter(item["state"] for item in arms)
    totals = data["totals"]
    attempted = 400 - states.get("not_attempted", 0)
    if totals["attempted"] != attempted or totals["not_attempted"] != states.get("not_attempted", 0):
        fail("attempted/not_attempted totals disagree with arm states")
    for state in ("completed_valid", "completed_invalid", "failed_infrastructure", "failed_implementation", "resource_exhaustion", "cancelled_by_budget"):
        if totals[state] != states.get(state, 0):
            fail(f"matrix terminal total disagrees for {state}")
    worker_wall = max(shard["wall_seconds"] for shard in data["shards"])
    if totals["worker_wall_seconds"] != worker_wall:
        fail("worker_wall is not max shard wall")
    expected_wall = totals["coordinator_wall_seconds"] + worker_wall + totals["replay_wall_seconds"] + totals["analysis_wall_seconds"] + totals["hashing_wall_seconds"] + totals["serialization_wall_seconds"]
    if totals["campaign_wall_seconds"] != expected_wall:
        fail("campaign wall equation failed")
    expected_cpu = totals["arm_cpu_seconds"] + totals["replay_cpu_seconds"] + totals["analysis_cpu_seconds"] + totals["hashing_cpu_seconds"] + totals["serialization_cpu_seconds"]
    if totals["cpu_seconds"] != expected_cpu:
        fail("campaign CPU equation failed")
    expected_bytes = sum(item["resource_bytes"][name] for item in arms for name in ("raw", "stdout", "stderr")) + totals["replay_bytes"] + totals["analysis_bytes"] + totals["global_log_bytes"]
    if totals["output_bytes"] != expected_bytes or totals["output_bytes"] > OUTPUT_CAP:
        fail("campaign output-byte equation or cap failed")


def validate_predecessor(path: Path, repo_root: Path) -> None:
    data = read_json(path)
    if tuple(data["historical_ineligible_ids"]) != PREDECESSORS:
        fail("predecessor exclusion set is not exact")
    if [record["id"] for record in data["records"]] != list(PREDECESSORS):
        fail("predecessor records are not in exact order")
    for record in data["records"]:
        if not record["historical"] or record["selected_contract"] or record["eligible_dependency"]:
            fail(f"predecessor admission flags are unsafe for {record['id']}")
        source = repo_root / record["path"]
        if not source.is_file():
            fail(f"predecessor source is missing: {record['path']}")
        if hashlib.sha256(source.read_bytes()).hexdigest() != record["sha256"]:
            fail(f"predecessor source hash mismatch: {record['id']}")
    gate = data["required_future_gate"]
    if not all(gate[name] for name in ("reject_if_selected_contract", "reject_if_dependency", "reject_if_hash_mismatch", "reject_if_any_id_missing", "approval_lock_must_bind_this_record", "dispatch_validator_must_read_this_record")):
        fail("predecessor future gate is incomplete")


def validate_fixtures(manifest_path: Path, contract: dict[str, Any]) -> None:
    manifest = read_json(manifest_path)
    if manifest["schema"] != "xor-fixture-manifest/v4" or len(manifest["fixtures"]) != 6:
        fail("fixture manifest is incomplete")
    for fixture in manifest["fixtures"]:
        data = read_json(manifest_path.parent / fixture["path"])
        if data["fixture_id"] != fixture["id"]:
            fail(f"fixture id mismatch for {fixture['id']}")
        for field, expected in fixture["expected"].items():
            actual = data.get(field)
            if actual is None and field == "valid":
                actual = data.get("expected", {}).get("result_valid")
            if actual is None:
                actual = data.get("expected", {}).get(field)
            if actual != expected:
                fail(f"fixture expectation mismatch for {fixture['id']}:{field}")
    if set(manifest["negative_mutations"]) != set(item["id"] for item in contract["rejected_fixtures"]):
        fail("negative fixture mutation set mismatch")
    validate_prng_fixture(contract)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-schema", required=True, type=Path)
    parser.add_argument("--matrix-schema", required=True, type=Path)
    parser.add_argument("--event-schema", required=True, type=Path)
    parser.add_argument("--fixtures", required=True, type=Path)
    parser.add_argument("--contract", type=Path)
    parser.add_argument("--predecessor", type=Path)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--run", type=Path)
    parser.add_argument("--matrix", type=Path)
    args = parser.parse_args()
    contract_path = args.contract or args.fixtures.parent.parent / "validation_contract_xor_v4.json"
    contract = read_json(contract_path)
    validate_fixtures(args.fixtures, contract)
    if args.predecessor:
        validate_predecessor(args.predecessor, args.repo_root)
    if args.run:
        validate_run(read_json(args.run), read_json(args.run_schema))
    if args.matrix:
        validate_matrix(read_json(args.matrix), read_json(args.matrix_schema))
    print("VALIDATION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
