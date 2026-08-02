#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
PRODUCER_PATH = SCRIPT_PATH.with_name("d4_membership_batch.py")
BASE_PATH = SCRIPT_PATH.with_name("d4_membership_recovery.py")


def sha256_file(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")).hexdigest()


def normalize(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: normalize(item) for key, item in value.items() if key not in {"peak_rss_bytes", "total_wall_seconds"}}
    if isinstance(value, list):
        return [normalize(item) for item in value]
    return value


def advice_name(route_name: str) -> str:
    return "d2" if route_name == "recursive_d2" else "d4" if route_name == "materialized_d4" else "membership_recovery"


def recompute_batch(batch: dict[str, Any], q: int, advice: dict[str, Any]) -> dict[str, Any]:
    expected: dict[str, Any] = {"target_digest": digest([row["target"] for row in batch["targets"]]), "all_routes_equal": True, "aggregates": {}}
    batch_size = batch["batch_size"]
    for row in batch["targets"]:
        expected["all_routes_equal"] = expected["all_routes_equal"] and row["all_routes_equal"]
    for route_name in ("recursive_d2", "materialized_d4", "membership_recovery"):
        values = [row["routes"][route_name] for row in batch["targets"]]
        successful = sum(int(item["frontier"]["success"]) for item in values)
        total_work = sum(item["frontier"]["online_work"] for item in values)
        epsilon = successful / batch_size
        words = advice[advice_name(route_name)]["logical_advice_words"]
        expected["aggregates"][route_name] = {"advice_words": words, "successful_targets": successful, "epsilon": epsilon, "total_online_work": total_work, "amortized_online_work": total_work / batch_size, "S_T2_over_epsilon_q": None if epsilon == 0 else words * (total_work / batch_size) ** 2 / (epsilon * q)}
    return expected


def check(raw: dict[str, Any], input_path: Path, predecessor_path: Path) -> dict[str, bool]:
    checks = {"protocol": False, "producer_hash": False, "base_hash": False, "predecessor_receipt": False, "input_hash": False, "config": False, "batch_aggregation": False, "exact_flags": False, "promotion_false": False, "breakthrough_false": False, "boundary": False}
    try:
        predecessor = json.loads(predecessor_path.read_text(encoding="utf-8"))
        expected_routes = ["recursive_d2", "materialized_d4", "membership_recovery"]
        config = raw["config"]
        aggregation_ok = True; flags_ok = True
        for row in raw["rows"]:
            for batch in row["batches"]:
                expected = recompute_batch(batch, row["q"], row["advice"])
                aggregation_ok = aggregation_ok and batch["target_digest"] == expected["target_digest"] and batch["aggregates"] == expected["aggregates"]
                flags_ok = flags_ok and batch["all_routes_equal"] is expected["all_routes_equal"]
        checks.update({"protocol": raw["protocol"] == "EXP-ECDLP-COORD-EXPANSION-001-d4-membership-batch-v1", "producer_hash": raw["source"]["producer_sha256"] == sha256_file(PRODUCER_PATH), "base_hash": raw["source"]["base_route_sha256"] == sha256_file(BASE_PATH), "predecessor_receipt": raw["source"]["predecessor_verification_sha256"] == sha256_file(predecessor_path) and predecessor.get("valid") is True and predecessor.get("checks", {}).get("normalized_replay_exact") is True, "input_hash": raw["source"]["input_sha256"] == sha256_file(input_path), "config": config["routes"] == expected_routes and config["batch_sizes"] == sorted(set(config["batch_sizes"])) and all(size > 0 for size in config["batch_sizes"]) and config["schedules"] == ["supported_batch", "translated_control"], "batch_aggregation": aggregation_ok, "exact_flags": flags_ok and raw["summary"]["all_batches_exact"] is True, "promotion_false": raw["summary"]["algorithm_promotion_gate"] is False, "breakthrough_false": raw["summary"]["breakthrough_claim"] is False, "boundary": "no generic ECDLP claim" in raw["summary"]["boundary"]})
    except (KeyError, TypeError, IndexError, json.JSONDecodeError):
        pass
    return checks


def mutation_rejections(raw: dict[str, Any], input_path: Path, predecessor_path: Path, expected_checks: dict[str, bool]) -> dict[str, bool]:
    mutations = {}
    changed = copy.deepcopy(raw); changed["protocol"] = "wrong"; mutations["protocol"] = changed
    changed = copy.deepcopy(raw); changed["source"]["base_route_sha256"] = "0" * 64; mutations["base_hash"] = changed
    changed = copy.deepcopy(raw); changed["rows"][0]["batches"][0]["aggregates"]["membership_recovery"]["total_online_work"] += 1; mutations["aggregate"] = changed
    changed = copy.deepcopy(raw); changed["rows"][0]["batches"][0]["target_digest"] = "0" * 64; mutations["target_digest"] = changed
    changed = copy.deepcopy(raw); changed["summary"]["breakthrough_claim"] = True; mutations["boundary_gate"] = changed
    return {name: not all(check(candidate, input_path, predecessor_path).values()) for name, candidate in mutations.items()}


def verify(raw_path: Path, input_override: Path | None = None) -> dict[str, Any]:
    raw = json.loads(raw_path.read_text(encoding="utf-8")); input_path = input_override if input_override is not None else Path(raw["config"]["input_result"]); predecessor_path = raw_path.parent.parent / ".." / "D4-MEMBERSHIP-RECOVERY-V1" / "RUN-001" / "verification.json"
    predecessor_path = predecessor_path.resolve(); checks = check(raw, input_path, predecessor_path); mutations = mutation_rejections(raw, input_path, predecessor_path, checks); checks["mutation_rejections"] = all(mutations.values())
    return {"protocol": "EXP-ECDLP-COORD-EXPANSION-001-d4-membership-batch-verifier", "raw_result_sha256": sha256_file(raw_path), "input_result_sha256": sha256_file(input_path), "predecessor_verification_sha256": sha256_file(predecessor_path), "producer_sha256": sha256_file(PRODUCER_PATH), "verifier_sha256": sha256_file(SCRIPT_PATH), "raw_normalized_sha256": digest(normalize(raw)), "checks": checks, "mutation_rejections_by_name": mutations, "rows_replayed": len(raw.get("rows", [])), "batches_replayed": sum(len(row.get("batches", [])) for row in raw.get("rows", [])), "valid": all(checks.values()), "boundary": "Independent batch aggregation replay; predecessor route is independently receipt-linked; no generic ECDLP claim."}


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("raw_result", type=Path); parser.add_argument("--input", type=Path); args = parser.parse_args(); receipt = verify(args.raw_result, args.input); print(json.dumps(receipt, sort_keys=True, separators=(",", ":"))); return 0 if receipt["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
