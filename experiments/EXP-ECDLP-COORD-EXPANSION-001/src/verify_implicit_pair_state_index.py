#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
PRODUCER_PATH = SCRIPT_PATH.with_name("implicit_pair_state_index.py")
Point = tuple[int, int] | None


class Curve:
    def __init__(self, p: int, a: int, b: int) -> None:
        self.p, self.a, self.b = p, a % p, b % p

    def neg(self, point: Point) -> Point:
        return None if point is None else (point[0], (-point[1]) % self.p)

    def add(self, left: Point, right: Point, ops: dict[str, int]) -> Point:
        ops["point_add_calls"] += 1
        if left is None:
            return right
        if right is None:
            return left
        x1, y1 = left; x2, y2 = right
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
        ops["field_inversions"] += 1; ops["field_multiplications"] += 4
        return x3, y3

    def subtract(self, left: Point, right: Point, ops: dict[str, int]) -> Point:
        return self.add(left, self.neg(right), ops)


def empty_ops() -> dict[str, int]:
    return {"point_add_calls": 0, "field_inversions": 0, "field_multiplications": 0}


def sha256_file(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")).hexdigest()


def as_point(value: list[int] | None) -> Point:
    return None if value is None else (value[0], value[1])


def point_json(value: Point) -> list[int] | None:
    return None if value is None else [value[0], value[1]]


def point_key(value: Point) -> tuple[int, int, int]:
    return (1, 0, 0) if value is None else (0, value[0], value[1])


def generate_states(curve: Curve, sources: list[Point], degree: int, ops: dict[str, int]) -> dict[Point, list[tuple[int, ...]]]:
    output: dict[Point, list[tuple[int, ...]]] = {}
    for witness in itertools.combinations_with_replacement(range(len(sources)), degree):
        total: Point = None
        for index in witness:
            total = curve.add(total, sources[index], ops)
        output.setdefault(total, []).append(witness)
    return output


def serialize_states(states: dict[Point, list[tuple[int, ...]]]) -> list[list[Any]]:
    return [[point_json(point), [list(item) for item in witnesses]] for point, witnesses in sorted(states.items(), key=lambda item: point_key(item[0]))]


def fingerprint(point: Point, modulus: int) -> tuple[int, int, int]:
    return (1, 0, 0) if point is None else (0, point[0] % modulus, point[1] % modulus)


def targets(curve: Curve, record: dict[str, Any], family: dict[str, Any]) -> dict[str, Point]:
    planted = as_point(family["relations"]["target_transcript"][0]["target"])
    held_out = as_point(family["held_out_descent"]["transcript"][0]["target"])
    shifted = curve.add(planted, as_point(record["generator"]), empty_ops())
    if shifted is None:
        raise AssertionError("invalid shifted target")
    return {"planted": planted, "held_out": held_out, "shifted_control": shifted}


def witness_sum(curve: Curve, sources: list[Point], witness: tuple[int, ...], ops: dict[str, int]) -> Point:
    total: Point = None
    for index in witness:
        total = curve.add(total, sources[index], ops)
    return total


def replay(curve: Curve, sources: list[Point], witness: tuple[int, ...], expected: Point, ops: dict[str, int]) -> None:
    if witness_sum(curve, sources, witness, ops) != expected:
        raise AssertionError("verifier witness mismatch")


def pair_states(curve: Curve, d2: dict[Point, list[tuple[int, ...]]], ops: dict[str, int]) -> tuple[list[Point], list[tuple[Point, int, int]]]:
    points = sorted(d2, key=point_key); records = []
    for left_id, left in enumerate(points):
        for right_id in range(left_id, len(points)):
            records.append((curve.add(left, points[right_id], ops), left_id, right_id))
    return points, records


def make_indexes(records: list[tuple[Point, int, int]], widths: list[int]) -> tuple[dict[str, list[list[int]]], dict[str, dict[str, list[list[int]]]]]:
    exact: dict[str, list[list[int]]] = {}; buckets = {str(width): {} for width in widths}
    for point, left_id, right_id in records:
        exact.setdefault(json.dumps(point_json(point), separators=(",", ":")), []).append([left_id, right_id])
        for width in widths:
            key = json.dumps(fingerprint(point, 1 << width), separators=(",", ":"))
            buckets[str(width)].setdefault(key, []).append([left_id, right_id])
    return exact, buckets


def recursive_query(curve: Curve, a_points: list[Point], sources: list[Point], d2: dict[Point, list[tuple[int, ...]]], target: Point, ops: dict[str, int]) -> tuple[set[tuple[int, ...]], dict[str, int]]:
    hits: set[tuple[int, ...]] = set(); candidates = 0; lookups = 0
    for a_point in a_points:
        after_a = curve.subtract(target, a_point, ops)
        for left_point, left_witnesses in d2.items():
            complement = curve.subtract(after_a, left_point, ops); right_witnesses = d2.get(complement, [])
            lookups += 1; candidates += len(left_witnesses) * len(right_witnesses)
            for left_witness in left_witnesses:
                for right_witness in right_witnesses:
                    witness = tuple(sorted(left_witness + right_witness)); replay(curve, sources, witness, after_a, ops); hits.add(witness)
    return hits, {"lookups": lookups, "candidate_pair_records": lookups, "candidate_witness_products": candidates, "state_sum_rejects": 0, "rejected_witnesses": 0}


def d4_query(curve: Curve, a_points: list[Point], sources: list[Point], d4: dict[Point, list[tuple[int, ...]]], target: Point, ops: dict[str, int]) -> tuple[set[tuple[int, ...]], dict[str, int]]:
    hits: set[tuple[int, ...]] = set(); candidates = 0
    for a_point in a_points:
        complement = curve.subtract(target, a_point, ops); witnesses = d4.get(complement, []); candidates += len(witnesses)
        for witness in witnesses:
            replay(curve, sources, witness, complement, ops); hits.add(tuple(witness))
    return hits, {"lookups": len(a_points), "candidate_pair_records": len(a_points), "candidate_witness_products": candidates, "state_sum_rejects": 0, "rejected_witnesses": 0}


def index_query(curve: Curve, a_points: list[Point], sources: list[Point], points: list[Point], d2: dict[Point, list[tuple[int, ...]]], table: dict[str, list[list[int]]], target: Point, ops: dict[str, int], width: int | None = None) -> tuple[set[tuple[int, ...]], dict[str, int]]:
    hits: set[tuple[int, ...]] = set(); pair_count = 0; witness_count = 0; state_rejects = 0; witness_rejects = 0
    for a_point in a_points:
        complement = curve.subtract(target, a_point, ops)
        value = point_json(complement) if width is None else fingerprint(complement, 1 << width)
        candidates = table.get(json.dumps(value, separators=(",", ":")), []); pair_count += len(candidates)
        for left_id, right_id in candidates:
            if width is not None and curve.add(points[left_id], points[right_id], ops) != complement:
                state_rejects += 1; continue
            left_witnesses = d2[points[left_id]]; right_witnesses = d2[points[right_id]]; witness_count += len(left_witnesses) * len(right_witnesses)
            for left_witness in left_witnesses:
                for right_witness in right_witnesses:
                    witness = tuple(sorted(left_witness + right_witness))
                    if witness_sum(curve, sources, witness, ops) == complement:
                        hits.add(witness)
                    else:
                        witness_rejects += 1
    return hits, {"lookups": len(a_points), "candidate_pair_records": pair_count, "candidate_witness_products": witness_count, "state_sum_rejects": state_rejects, "rejected_witnesses": witness_rejects}


def d2_advice(d2: dict[Point, list[tuple[int, ...]]]) -> dict[str, int]:
    records = sum(len(value) for value in d2.values())
    return {"state_count": len(d2), "witness_records": records, "key_field_elements": 2 * len(d2), "witness_index_words": 2 * records, "logical_advice_words": 2 * len(d2) + 2 * records}


def row(record: dict[str, Any], family: dict[str, Any], widths: list[int]) -> dict[str, Any]:
    curve = Curve(record["p"], record["a"], record["b"]); a_points = [as_point(value) for value in family["progression"]["points"]]; sources = [as_point(value) for value in family["factor_base"]["points"]]
    d2_ops = empty_ops(); d4_ops = empty_ops(); pair_ops = empty_ops(); d2 = generate_states(curve, sources, 2, d2_ops); d4 = generate_states(curve, sources, 4, d4_ops); points, records = pair_states(curve, d2, pair_ops); exact, buckets = make_indexes(records, widths)
    base = d2_advice(d2); record_advice = {"pair_records": len(records), "pair_state_id_words": 2 * len(records), "d2_base": base, "exact": {"bucket_count": len(exact), "key_field_elements": 2 * len(exact), "logical_advice_words": base["logical_advice_words"] + 2 * len(exact) + 2 * len(records)}, "fingerprints": {}}
    for width in widths:
        table = buckets[str(width)]; record_advice["fingerprints"][str(width)] = {"bucket_count": len(table), "key_field_elements": len(table), "logical_advice_words": base["logical_advice_words"] + len(table) + 2 * len(records)}
    target_rows = []
    for label, target in targets(curve, record, family).items():
        routes: dict[str, Any] = {}; ops = empty_ops(); hits, metrics = recursive_query(curve, a_points, sources, d2, target, ops); routes["recursive_d2"] = {"hits": sorted([list(item) for item in hits]), "metrics": metrics, "ops": ops, "advice": base}
        ops = empty_ops(); hits, metrics = d4_query(curve, a_points, sources, d4, target, ops); d4_records = sum(len(value) for value in d4.values()); routes["materialized_d4"] = {"hits": sorted([list(item) for item in hits]), "metrics": metrics, "ops": ops, "advice": {"state_count": len(d4), "witness_records": d4_records, "key_field_elements": 2 * len(d4), "witness_index_words": 4 * d4_records, "logical_advice_words": 2 * len(d4) + 4 * d4_records}}
        ops = empty_ops(); hits, metrics = index_query(curve, a_points, sources, points, d2, exact, target, ops); routes["exact_state_pair"] = {"hits": sorted([list(item) for item in hits]), "metrics": metrics, "ops": ops, "advice": record_advice["exact"]}
        for width in widths:
            ops = empty_ops(); hits, metrics = index_query(curve, a_points, sources, points, d2, buckets[str(width)], target, ops, width); routes[f"fingerprint_w{width}"] = {"hits": sorted([list(item) for item in hits]), "metrics": metrics, "ops": ops, "advice": record_advice["fingerprints"][str(width)]}
        for route in routes.values():
            online = sum(route["ops"].values()); words = route["advice"]["logical_advice_words"]; route["frontier"] = {"online_work": online, "advice_words": words, "S_T2_over_q": words * online * online / record["q"], "success": bool(route["hits"])}
        baseline = routes["recursive_d2"]["hits"]; target_rows.append({"label": label, "target": point_json(target), "routes": routes, "all_routes_equal": all(route["hits"] == baseline for route in routes.values())})
    return {"curve_id": record["id"], "family": family["family"], "p": record["p"], "q": record["q"], "a_size": len(a_points), "r_size": len(sources), "supports": {"d2": len(d2), "d4": len(d4)}, "state_digests": {"d2": digest(serialize_states(d2)), "d4": digest(serialize_states(d4))}, "pair_index": {"record_digest": digest([[point_json(point), left_id, right_id] for point, left_id, right_id in records]), "record_count": len(records), "advice": record_advice}, "build_ops": {"d2": d2_ops, "d4": d4_ops, "pair": pair_ops}, "targets": target_rows}


def replay_result(input_path: Path, families: list[str], widths: list[int]) -> dict[str, Any]:
    source = json.loads(input_path.read_text(encoding="utf-8")); rows = []
    for instance in source["instances"]:
        by_family = {item["family"]: item for item in instance["families"]}
        for family_name in families:
            rows.append(row(instance["curve"], by_family[family_name], widths))
    routes = ["recursive_d2", "materialized_d4", "exact_state_pair"] + [f"fingerprint_w{width}" for width in widths]
    return {"protocol": "EXP-ECDLP-COORD-EXPANSION-001-implicit-pair-state-index-v1", "claim_status": ["HYPOTHESIS", "TOY-EVIDENCE", "MODEL-BOUND"], "source": {"producer_sha256": sha256_file(PRODUCER_PATH), "input_sha256": sha256_file(input_path)}, "config": {"input_result": str(input_path.resolve()), "families": families, "targets": ["planted", "held_out", "shifted_control"], "routes": routes, "widths": widths, "fingerprint": "identity-or-(x mod 2^w,y mod 2^w)", "witness_policy": "all nondecreasing D2 witness lists, deferred state-ID pair lift, canonicalized four-source tuples", "frontier": "logical advice words and charged affine group/field operation proxy; S*T^2/q diagnostic only"}, "rows": rows, "summary": {"cells": len(rows), "targets": sum(len(row["targets"]) for row in rows), "all_routes_exact": all(target["all_routes_equal"] for row in rows for target in row["targets"]), "algorithm_promotion_gate": False, "breakthrough_claim": False, "boundary": "Exact implicit witness-lift pair-state preflight; no generic ECDLP claim."}, "accounting": {"d2_build_adds": sum(row["build_ops"]["d2"]["point_add_calls"] for row in rows), "d4_build_adds": sum(row["build_ops"]["d4"]["point_add_calls"] for row in rows), "pair_build_adds": sum(row["build_ops"]["pair"]["point_add_calls"] for row in rows), "target_queries": sum(len(row["targets"]) for row in rows)}}


def normalize(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: normalize(item) for key, item in value.items() if key not in {"peak_rss_bytes", "total_wall_seconds"}}
    if isinstance(value, list):
        return [normalize(item) for item in value]
    return value


def check(raw: dict[str, Any], input_path: Path) -> dict[str, bool]:
    checks = {"protocol": False, "producer_hash": False, "input_hash": False, "widths": False, "routes": False, "exact_summary": False, "promotion_false": False, "breakthrough_false": False, "boundary": False}
    try:
        expected = ["recursive_d2", "materialized_d4", "exact_state_pair"] + [f"fingerprint_w{width}" for width in raw["config"]["widths"]]
        checks.update({"protocol": raw["protocol"] == "EXP-ECDLP-COORD-EXPANSION-001-implicit-pair-state-index-v1", "producer_hash": raw["source"]["producer_sha256"] == sha256_file(PRODUCER_PATH), "input_hash": raw["source"]["input_sha256"] == sha256_file(input_path), "widths": raw["config"]["widths"] == sorted(set(raw["config"]["widths"])) and all(0 < width <= 12 for width in raw["config"]["widths"]), "routes": raw["config"]["routes"] == expected, "exact_summary": raw["summary"]["all_routes_exact"] is True, "promotion_false": raw["summary"]["algorithm_promotion_gate"] is False, "breakthrough_false": raw["summary"]["breakthrough_claim"] is False, "boundary": "no generic ECDLP claim" in raw["summary"]["boundary"]})
    except (KeyError, TypeError, IndexError):
        pass
    return checks


def mutation_rejections(raw: dict[str, Any], input_path: Path, expected: dict[str, Any]) -> dict[str, bool]:
    mutations = {}
    changed = copy.deepcopy(raw); changed["protocol"] = "wrong"; mutations["protocol"] = changed
    changed = copy.deepcopy(raw); changed["source"]["producer_sha256"] = "0" * 64; mutations["producer_hash"] = changed
    changed = copy.deepcopy(raw); changed["config"]["widths"][0] += 1; mutations["widths"] = changed
    changed = copy.deepcopy(raw); changed["rows"][0]["targets"][0]["routes"]["exact_state_pair"]["metrics"]["candidate_witness_products"] += 1; mutations["metric"] = changed
    changed = copy.deepcopy(raw); changed["summary"]["breakthrough_claim"] = True; mutations["boundary_gate"] = changed
    return {name: not (all(check(candidate, input_path).values()) and normalize(candidate) == normalize(expected)) for name, candidate in mutations.items()}


def verify(raw_path: Path, input_override: Path | None = None) -> dict[str, Any]:
    raw = json.loads(raw_path.read_text(encoding="utf-8")); input_path = input_override if input_override is not None else Path(raw["config"]["input_result"]); expected = replay_result(input_path, raw["config"]["families"], raw["config"]["widths"]); checks = check(raw, input_path); checks["normalized_replay_exact"] = normalize(raw) == normalize(expected); mutations = mutation_rejections(raw, input_path, expected); checks["mutation_rejections"] = all(mutations.values())
    return {"protocol": "EXP-ECDLP-COORD-EXPANSION-001-implicit-pair-state-index-verifier", "raw_result_sha256": sha256_file(raw_path), "input_result_sha256": sha256_file(input_path), "producer_sha256": sha256_file(PRODUCER_PATH), "verifier_sha256": sha256_file(SCRIPT_PATH), "raw_normalized_sha256": digest(normalize(raw)), "replay_normalized_sha256": digest(normalize(expected)), "checks": checks, "mutation_rejections_by_name": mutations, "rows_replayed": len(expected["rows"]), "valid": all(checks.values()), "boundary": "Independent deferred witness-lift replay; no generic ECDLP claim."}


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("raw_result", type=Path); parser.add_argument("--input", type=Path); args = parser.parse_args(); receipt = verify(args.raw_result, args.input); print(json.dumps(receipt, sort_keys=True, separators=(",", ":"))); return 0 if receipt["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
