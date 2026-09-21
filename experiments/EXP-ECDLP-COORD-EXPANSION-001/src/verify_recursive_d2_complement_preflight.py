#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
PRODUCER_PATH = SCRIPT_PATH.with_name("recursive_d2_complement_preflight.py")
Point = tuple[int, int] | None


class Curve:
    def __init__(self, p: int, a: int) -> None:
        self.p, self.a = p, a % p

    def neg(self, value: Point) -> Point:
        return None if value is None else (value[0], (-value[1]) % self.p)

    def add(self, left: Point, right: Point, ops: dict[str, int]) -> Point:
        ops["point_add_calls"] += 1
        if left is None:
            return right
        if right is None:
            return left
        x1, y1 = left
        x2, y2 = right
        if x1 == x2 and (y1 + y2) % self.p == 0:
            return None
        if left == right:
            if y1 % self.p == 0:
                return None
            numerator, denominator = 3 * x1 * x1 + self.a, 2 * y1
        else:
            numerator, denominator = y2 - y1, x2 - x1
        slope = numerator * pow(denominator % self.p, -1, self.p) % self.p
        x3 = (slope * slope - x1 - x2) % self.p
        y3 = (slope * (x1 - x3) - y1) % self.p
        ops["field_inversions"] += 1
        ops["field_multiplications"] += 4
        return x3, y3

    def subtract(self, left: Point, right: Point, ops: dict[str, int]) -> Point:
        return self.add(left, self.neg(right), ops)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")).hexdigest()


def as_point(value: list[int] | None) -> Point:
    return None if value is None else (value[0], value[1])


def point_json(value: Point) -> list[int] | None:
    return None if value is None else [value[0], value[1]]


def point_key(value: Point) -> tuple[int, int, int]:
    return (1, 0, 0) if value is None else (0, value[0], value[1])


def state_level(curve: Curve, sources: list[Point], level: int, ops: dict[str, int]) -> dict[Point, list[tuple[int, ...]]]:
    states: dict[Point, list[tuple[int, ...]]] = {}
    for witness in itertools.combinations_with_replacement(range(len(sources)), level):
        total: Point = None
        for index in witness:
            total = curve.add(total, sources[index], ops)
        states.setdefault(total, []).append(witness)
    return states


def serialize_states(states: dict[Point, list[tuple[int, ...]]]) -> list[list[Any]]:
    return [[point_json(point), [list(witness) for witness in witnesses]] for point, witnesses in sorted(states.items(), key=lambda item: point_key(item[0]))]


def targets(curve: Curve, record: dict[str, Any], family: dict[str, Any]) -> dict[str, Point]:
    planted = as_point(family["relations"]["target_transcript"][0]["target"])
    held_out = as_point(family["held_out_descent"]["transcript"][0]["target"])
    generator = as_point(record["generator"])
    ops = {"point_add_calls": 0, "field_inversions": 0, "field_multiplications": 0}
    shifted = curve.add(planted, generator, ops)
    if shifted is None:
        raise AssertionError("shifted target became identity")
    return {"planted": planted, "held_out": held_out, "shifted_control": shifted}


def replay_witness(curve: Curve, sources: list[Point], witness: tuple[int, ...], expected: Point, ops: dict[str, int]) -> None:
    total: Point = None
    for index in witness:
        total = curve.add(total, sources[index], ops)
    if total != expected:
        raise AssertionError("witness mismatch")


def query_r3(curve: Curve, a_points: list[Point], r_points: list[Point], d3: dict[Point, list[tuple[int, ...]]], target: Point, ops: dict[str, int]) -> tuple[list[list[int]], dict[str, int]]:
    hits: set[tuple[int, ...]] = set(); lookups = 0; candidates = 0
    for a_point in a_points:
        after_a = curve.subtract(target, a_point, ops)
        for r_index, r_point in enumerate(r_points):
            complement = curve.subtract(after_a, r_point, ops)
            witnesses = d3.get(complement, [])
            lookups += 1; candidates += len(witnesses)
            for witness in witnesses:
                combined = tuple(sorted((r_index,) + witness))
                replay_witness(curve, r_points, combined, after_a, ops)
                hits.add(combined)
    return [list(hit) for hit in sorted(hits)], {"lookups": lookups, "candidate_witnesses": candidates}


def query_d2(curve: Curve, a_points: list[Point], r_points: list[Point], d2: dict[Point, list[tuple[int, ...]]], target: Point, ops: dict[str, int]) -> tuple[list[list[int]], dict[str, int]]:
    hits: set[tuple[int, ...]] = set(); lookups = 0; candidates = 0
    for a_point in a_points:
        after_a = curve.subtract(target, a_point, ops)
        for left_point, left_witnesses in d2.items():
            complement = curve.subtract(after_a, left_point, ops)
            right_witnesses = d2.get(complement, [])
            lookups += 1; candidates += len(left_witnesses) * len(right_witnesses)
            for left in left_witnesses:
                for right in right_witnesses:
                    combined = tuple(sorted(left + right))
                    replay_witness(curve, r_points, combined, after_a, ops)
                    hits.add(combined)
    return [list(hit) for hit in sorted(hits)], {"lookups": lookups, "candidate_witnesses": candidates}


def query_d4(curve: Curve, a_points: list[Point], d4: dict[Point, list[tuple[int, ...]]], target: Point, r_points: list[Point], ops: dict[str, int]) -> tuple[list[list[int]], dict[str, int]]:
    hits: set[tuple[int, ...]] = set(); candidates = 0
    for a_point in a_points:
        complement = curve.subtract(target, a_point, ops)
        witnesses = d4.get(complement, [])
        candidates += len(witnesses)
        for witness in witnesses:
            replay_witness(curve, r_points, witness, complement, ops)
            hits.add(tuple(witness))
    return [list(hit) for hit in sorted(hits)], {"lookups": len(a_points), "candidate_witnesses": candidates}


def advice(states: dict[Point, list[tuple[int, ...]]], level: int) -> dict[str, int]:
    records = sum(len(value) for value in states.values())
    return {"state_count": len(states), "witness_records": records, "key_field_elements": 2 * len(states), "witness_index_words": level * records, "logical_advice_words": 2 * len(states) + level * records}


def row(record: dict[str, Any], family: dict[str, Any]) -> dict[str, Any]:
    curve = Curve(record["p"], record["a"])
    a_points = [as_point(value) for value in family["progression"]["points"]]
    r_points = [as_point(value) for value in family["factor_base"]["points"]]
    states, build_ops = {}, {}
    for level in (2, 3, 4):
        ops = {"point_add_calls": 0, "field_inversions": 0, "field_multiplications": 0}
        states[level] = state_level(curve, r_points, level, ops); build_ops[str(level)] = ops
    adv = {f"d{level}": advice(states[level], level) for level in (2, 3, 4)}
    target_rows = []
    for label, target in targets(curve, record, family).items():
        d2_ops = {"point_add_calls": 0, "field_inversions": 0, "field_multiplications": 0}
        r3_ops = {"point_add_calls": 0, "field_inversions": 0, "field_multiplications": 0}
        d4_ops = {"point_add_calls": 0, "field_inversions": 0, "field_multiplications": 0}
        d2_hits, d2_metrics = query_d2(curve, a_points, r_points, states[2], target, d2_ops)
        r3_hits, r3_metrics = query_r3(curve, a_points, r_points, states[3], target, r3_ops)
        d4_hits, d4_metrics = query_d4(curve, a_points, states[4], target, r_points, d4_ops)
        routes = {"d2_plus_d2": {"hits": d2_hits, "metrics": d2_metrics, "ops": d2_ops, "advice": adv["d2"]}, "r_plus_d3": {"hits": r3_hits, "metrics": r3_metrics, "ops": r3_ops, "advice": adv["d3"]}, "materialized_d4": {"hits": d4_hits, "metrics": d4_metrics, "ops": d4_ops, "advice": adv["d4"]}}
        for route in routes.values():
            online = sum(route["ops"].values()); words = route["advice"]["logical_advice_words"]
            route["frontier"] = {"online_work": online, "advice_words": words, "S_T2_over_q": words * online * online / record["q"], "success": bool(route["hits"])}
        target_rows.append({"label": label, "target": point_json(target), "routes": routes, "d2_equals_d4": d2_hits == d4_hits, "r3_equals_d4": r3_hits == d4_hits})
    return {"curve_id": record["id"], "family": family["family"], "p": record["p"], "q": record["q"], "a_size": len(a_points), "r_size": len(r_points), "supports": {f"d{level}": len(states[level]) for level in (2, 3, 4)}, "state_digests": {f"d{level}": digest(serialize_states(states[level])) for level in (2, 3, 4)}, "advice": adv, "build_ops": build_ops, "targets": target_rows}


def replay(input_path: Path, families: list[str]) -> dict[str, Any]:
    source = json.loads(input_path.read_text(encoding="utf-8")); rows = []
    for instance in source["instances"]:
        record = instance["curve"]; by_family = {item["family"]: item for item in instance["families"]}
        for family_name in families:
            rows.append(row(record, by_family[family_name]))
    return {"protocol": "EXP-ECDLP-COORD-EXPANSION-001-recursive-d2-complement-preflight-v1", "claim_status": ["HYPOTHESIS", "TOY-EVIDENCE", "MODEL-BOUND"], "source": {"producer_sha256": sha256_file(PRODUCER_PATH), "input_sha256": sha256_file(input_path)}, "config": {"input_result": str(input_path.resolve()), "families": families, "targets": ["planted", "held_out", "shifted_control"], "routes": ["D2+D2", "R+D3", "materialized-D4"], "witness_policy": "all nondecreasing source tuples per state; canonicalized four-source witnesses", "frontier": "logical advice words and charged group/field operation proxy; S*T^2/q diagnostic only"}, "rows": rows, "summary": {"cells": len(rows), "targets": sum(len(row["targets"]) for row in rows), "all_d2_d4_exact": all(target["d2_equals_d4"] for row in rows for target in row["targets"]), "all_r3_d4_exact": all(target["r3_equals_d4"] for row in rows for target in row["targets"]), "algorithm_promotion_gate": False, "breakthrough_claim": False, "boundary": "Exact recursive complement preflight; no generic ECDLP claim."}, "accounting": {"d2_build_adds": sum(row["build_ops"]["2"]["point_add_calls"] for row in rows), "d3_build_adds": sum(row["build_ops"]["3"]["point_add_calls"] for row in rows), "d4_build_adds": sum(row["build_ops"]["4"]["point_add_calls"] for row in rows), "target_queries": sum(len(row["targets"]) for row in rows)}}


def normalize(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: normalize(item) for key, item in value.items() if key not in {"peak_rss_bytes", "total_wall_seconds"}}
    if isinstance(value, list):
        return [normalize(item) for item in value]
    return value


def check(raw: dict[str, Any], input_path: Path) -> dict[str, bool]:
    checks = {"protocol": False, "producer_hash": False, "input_hash": False, "routes": False, "promotion_false": False, "breakthrough_false": False, "boundary": False}
    try:
        checks.update({"protocol": raw["protocol"] == "EXP-ECDLP-COORD-EXPANSION-001-recursive-d2-complement-preflight-v1", "producer_hash": raw["source"]["producer_sha256"] == sha256_file(PRODUCER_PATH), "input_hash": raw["source"]["input_sha256"] == sha256_file(input_path), "routes": raw["config"]["routes"] == ["D2+D2", "R+D3", "materialized-D4"], "promotion_false": raw["summary"]["algorithm_promotion_gate"] is False, "breakthrough_false": raw["summary"]["breakthrough_claim"] is False, "boundary": "no generic ECDLP claim" in raw["summary"]["boundary"]})
    except (KeyError, TypeError, IndexError):
        pass
    return checks


def mutation_rejections(raw: dict[str, Any], input_path: Path, expected: dict[str, Any]) -> dict[str, bool]:
    mutations = {}
    changed = copy.deepcopy(raw); changed["protocol"] = "wrong"; mutations["protocol"] = changed
    changed = copy.deepcopy(raw); changed["source"]["producer_sha256"] = "0" * 64; mutations["producer_hash"] = changed
    changed = copy.deepcopy(raw); changed["rows"][0]["targets"][0]["d2_equals_d4"] = False; mutations["d2_flag"] = changed
    changed = copy.deepcopy(raw); changed["rows"][0]["targets"][0]["routes"]["d2_plus_d2"]["frontier"]["online_work"] += 1; mutations["cost_row"] = changed
    changed = copy.deepcopy(raw); changed["summary"]["breakthrough_claim"] = True; mutations["boundary_gate"] = changed
    return {name: not (all(check(candidate, input_path).values()) and normalize(candidate) == normalize(expected)) for name, candidate in mutations.items()}


def verify(raw_path: Path, input_override: Path | None = None) -> dict[str, Any]:
    raw = json.loads(raw_path.read_text(encoding="utf-8")); input_path = input_override if input_override is not None else Path(raw["config"]["input_result"])
    expected = replay(input_path, raw["config"]["families"]); checks = check(raw, input_path)
    checks["normalized_replay_exact"] = normalize(raw) == normalize(expected)
    mutations = mutation_rejections(raw, input_path, expected); checks["mutation_rejections"] = all(mutations.values())
    return {"protocol": "EXP-ECDLP-COORD-EXPANSION-001-recursive-d2-complement-preflight-verifier", "raw_result_sha256": sha256_file(raw_path), "input_result_sha256": sha256_file(input_path), "producer_sha256": sha256_file(PRODUCER_PATH), "verifier_sha256": sha256_file(SCRIPT_PATH), "raw_normalized_sha256": digest(normalize(raw)), "replay_normalized_sha256": digest(normalize(expected)), "checks": checks, "mutation_rejections_by_name": mutations, "rows_replayed": len(expected["rows"]), "valid": all(checks.values()), "boundary": "Independent recursive complement replay; no generic ECDLP claim."}


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(); parser.add_argument("raw_result", type=Path); parser.add_argument("--input", type=Path)
    args = parser.parse_args(); receipt = verify(args.raw_result, args.input)
    print(json.dumps(receipt, sort_keys=True, separators=(",", ":")))
    return 0 if receipt["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
