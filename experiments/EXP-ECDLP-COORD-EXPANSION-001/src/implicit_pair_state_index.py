#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import platform
import resource
import time
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
Point = tuple[int, int] | None
Ops = dict[str, int]


class AffineCurve:
    def __init__(self, p: int, a: int, b: int) -> None:
        self.p, self.a, self.b = p, a % p, b % p

    def neg(self, point: Point) -> Point:
        return None if point is None else (point[0], (-point[1]) % self.p)

    def add(self, left: Point, right: Point, ops: Ops) -> Point:
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

    def subtract(self, left: Point, right: Point, ops: Ops) -> Point:
        return self.add(left, self.neg(right), ops)


def empty_ops() -> Ops:
    return {"point_add_calls": 0, "field_inversions": 0, "field_multiplications": 0}


def sha256_file(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")).hexdigest()


def rss_bytes() -> int:
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(value if platform.system() == "Darwin" else value * 1024)


def as_point(value: list[int] | None) -> Point:
    return None if value is None else (value[0], value[1])


def point_json(value: Point) -> list[int] | None:
    return None if value is None else [value[0], value[1]]


def point_key(value: Point) -> tuple[int, int, int]:
    return (1, 0, 0) if value is None else (0, value[0], value[1])


def state_level(curve: AffineCurve, sources: list[Point], degree: int, ops: Ops) -> dict[Point, list[tuple[int, ...]]]:
    states: dict[Point, list[tuple[int, ...]]] = {}
    for witness in itertools.combinations_with_replacement(range(len(sources)), degree):
        total: Point = None
        for index in witness:
            total = curve.add(total, sources[index], ops)
        states.setdefault(total, []).append(witness)
    return states


def serialize_states(states: dict[Point, list[tuple[int, ...]]]) -> list[list[Any]]:
    return [[point_json(point), [list(item) for item in witnesses]] for point, witnesses in sorted(states.items(), key=lambda item: point_key(item[0]))]


def target_choices(curve: AffineCurve, record: dict[str, Any], family: dict[str, Any]) -> dict[str, Point]:
    planted = as_point(family["relations"]["target_transcript"][0]["target"])
    held_out = as_point(family["held_out_descent"]["transcript"][0]["target"])
    shifted = curve.add(planted, as_point(record["generator"]), empty_ops())
    if shifted is None:
        raise AssertionError("shifted target became identity")
    return {"planted": planted, "held_out": held_out, "shifted_control": shifted}


def fingerprint(point: Point, modulus: int) -> tuple[int, int, int]:
    if point is None:
        return (1, 0, 0)
    return (0, point[0] % modulus, point[1] % modulus)


def witness_sum(curve: AffineCurve, sources: list[Point], witness: tuple[int, ...], ops: Ops) -> Point:
    total: Point = None
    for index in witness:
        total = curve.add(total, sources[index], ops)
    return total


def replay_witness(curve: AffineCurve, sources: list[Point], witness: tuple[int, ...], expected: Point, ops: Ops) -> None:
    if witness_sum(curve, sources, witness, ops) != expected:
        raise AssertionError("deferred witness mismatch")


def build_pair_states(curve: AffineCurve, d2: dict[Point, list[tuple[int, ...]]], ops: Ops) -> tuple[list[Point], list[tuple[Point, int, int]]]:
    points = sorted(d2, key=point_key)
    records: list[tuple[Point, int, int]] = []
    for left_id, left in enumerate(points):
        for right_id in range(left_id, len(points)):
            total = curve.add(left, points[right_id], ops)
            records.append((total, left_id, right_id))
    return points, records


def build_indexes(records: list[tuple[Point, int, int]], widths: list[int]) -> dict[str, Any]:
    exact: dict[str, list[list[int]]] = {}
    buckets: dict[str, dict[str, list[list[int]]]] = {str(width): {} for width in widths}
    for point, left_id, right_id in records:
        exact.setdefault(json.dumps(point_json(point), separators=(",", ":")), []).append([left_id, right_id])
        for width in widths:
            key = json.dumps(fingerprint(point, 1 << width), separators=(",", ":"))
            buckets[str(width)].setdefault(key, []).append([left_id, right_id])
    return {"exact": exact, "buckets": buckets}


def query_recursive(curve: AffineCurve, a_points: list[Point], sources: list[Point], d2: dict[Point, list[tuple[int, ...]]], target: Point, ops: Ops) -> tuple[set[tuple[int, ...]], dict[str, int]]:
    hits: set[tuple[int, ...]] = set(); lookups = 0; candidates = 0
    for a_point in a_points:
        after_a = curve.subtract(target, a_point, ops)
        for left_point, left_witnesses in d2.items():
            complement = curve.subtract(after_a, left_point, ops)
            right_witnesses = d2.get(complement, [])
            lookups += 1; candidates += len(left_witnesses) * len(right_witnesses)
            for left_witness in left_witnesses:
                for right_witness in right_witnesses:
                    witness = tuple(sorted(left_witness + right_witness))
                    replay_witness(curve, sources, witness, after_a, ops)
                    hits.add(witness)
    return hits, {"lookups": lookups, "candidate_pair_records": lookups, "candidate_witness_products": candidates, "state_sum_rejects": 0, "rejected_witnesses": 0}


def query_materialized_d4(curve: AffineCurve, a_points: list[Point], sources: list[Point], d4: dict[Point, list[tuple[int, ...]]], target: Point, ops: Ops) -> tuple[set[tuple[int, ...]], dict[str, int]]:
    hits: set[tuple[int, ...]] = set(); candidates = 0
    for a_point in a_points:
        complement = curve.subtract(target, a_point, ops)
        witnesses = d4.get(complement, [])
        candidates += len(witnesses)
        for witness in witnesses:
            replay_witness(curve, sources, witness, complement, ops)
            hits.add(tuple(witness))
    return hits, {"lookups": len(a_points), "candidate_pair_records": len(a_points), "candidate_witness_products": candidates, "state_sum_rejects": 0, "rejected_witnesses": 0}


def query_index(curve: AffineCurve, a_points: list[Point], sources: list[Point], d2_points: list[Point], d2: dict[Point, list[tuple[int, ...]]], table: dict[str, list[list[int]]], target: Point, ops: Ops, width: int | None = None) -> tuple[set[tuple[int, ...]], dict[str, int]]:
    hits: set[tuple[int, ...]] = set(); pair_candidates = 0; witness_products = 0; state_rejects = 0; rejected_witnesses = 0
    for a_point in a_points:
        complement = curve.subtract(target, a_point, ops)
        key_value = point_json(complement) if width is None else fingerprint(complement, 1 << width)
        key = json.dumps(key_value, separators=(",", ":"))
        candidates = table.get(key, [])
        pair_candidates += len(candidates)
        for left_id, right_id in candidates:
            left_point, right_point = d2_points[left_id], d2_points[right_id]
            if width is not None and curve.add(left_point, right_point, ops) != complement:
                state_rejects += 1
                continue
            left_witnesses = d2[left_point]; right_witnesses = d2[right_point]
            witness_products += len(left_witnesses) * len(right_witnesses)
            for left_witness in left_witnesses:
                for right_witness in right_witnesses:
                    witness = tuple(sorted(left_witness + right_witness))
                    if witness_sum(curve, sources, witness, ops) == complement:
                        hits.add(witness)
                    else:
                        rejected_witnesses += 1
    return hits, {"lookups": len(a_points), "candidate_pair_records": pair_candidates, "candidate_witness_products": witness_products, "state_sum_rejects": state_rejects, "rejected_witnesses": rejected_witnesses}


def d2_advice(d2: dict[Point, list[tuple[int, ...]]]) -> dict[str, int]:
    records = sum(len(value) for value in d2.values())
    return {"state_count": len(d2), "witness_records": records, "key_field_elements": 2 * len(d2), "witness_index_words": 2 * records, "logical_advice_words": 2 * len(d2) + 2 * records}


def state_pair_advice(d2: dict[Point, list[tuple[int, ...]]], records: list[tuple[Point, int, int]], indexes: dict[str, Any], widths: list[int]) -> dict[str, Any]:
    base = d2_advice(d2)
    result: dict[str, Any] = {"pair_records": len(records), "pair_state_id_words": 2 * len(records), "d2_base": base, "exact": {}, "fingerprints": {}}
    result["exact"] = {"bucket_count": len(indexes["exact"]), "key_field_elements": 2 * len(indexes["exact"]), "logical_advice_words": base["logical_advice_words"] + 2 * len(indexes["exact"]) + 2 * len(records)}
    for width in widths:
        table = indexes["buckets"][str(width)]
        result["fingerprints"][str(width)] = {"bucket_count": len(table), "key_field_elements": len(table), "logical_advice_words": base["logical_advice_words"] + len(table) + 2 * len(records)}
    return result


def run_row(record: dict[str, Any], family: dict[str, Any], widths: list[int]) -> dict[str, Any]:
    curve = AffineCurve(record["p"], record["a"], record["b"])
    a_points = [as_point(value) for value in family["progression"]["points"]]
    sources = [as_point(value) for value in family["factor_base"]["points"]]
    d2_ops = empty_ops(); d4_ops = empty_ops(); pair_ops = empty_ops()
    d2 = state_level(curve, sources, 2, d2_ops); d4 = state_level(curve, sources, 4, d4_ops)
    d2_points, records = build_pair_states(curve, d2, pair_ops)
    indexes = build_indexes(records, widths)
    advice = state_pair_advice(d2, records, indexes, widths)
    target_rows = []
    for label, target in target_choices(curve, record, family).items():
        routes: dict[str, Any] = {}
        ops = empty_ops(); hits, metrics = query_recursive(curve, a_points, sources, d2, target, ops)
        routes["recursive_d2"] = {"hits": sorted([list(item) for item in hits]), "metrics": metrics, "ops": ops, "advice": d2_advice(d2)}
        ops = empty_ops(); hits, metrics = query_materialized_d4(curve, a_points, sources, d4, target, ops)
        routes["materialized_d4"] = {"hits": sorted([list(item) for item in hits]), "metrics": metrics, "ops": ops, "advice": {"state_count": len(d4), "witness_records": sum(len(value) for value in d4.values()), "key_field_elements": 2 * len(d4), "witness_index_words": 4 * sum(len(value) for value in d4.values()), "logical_advice_words": 2 * len(d4) + 4 * sum(len(value) for value in d4.values())}}
        ops = empty_ops(); hits, metrics = query_index(curve, a_points, sources, d2_points, d2, indexes["exact"], target, ops)
        routes["exact_state_pair"] = {"hits": sorted([list(item) for item in hits]), "metrics": metrics, "ops": ops, "advice": advice["exact"]}
        for width in widths:
            ops = empty_ops(); hits, metrics = query_index(curve, a_points, sources, d2_points, d2, indexes["buckets"][str(width)], target, ops, width)
            routes[f"fingerprint_w{width}"] = {"hits": sorted([list(item) for item in hits]), "metrics": metrics, "ops": ops, "advice": advice["fingerprints"][str(width)]}
        for route in routes.values():
            online = sum(route["ops"].values()); words = route["advice"]["logical_advice_words"]
            route["frontier"] = {"online_work": online, "advice_words": words, "S_T2_over_q": words * online * online / record["q"], "success": bool(route["hits"])}
        baseline = routes["recursive_d2"]["hits"]
        target_rows.append({"label": label, "target": point_json(target), "routes": routes, "all_routes_equal": all(route["hits"] == baseline for route in routes.values())})
    return {"curve_id": record["id"], "family": family["family"], "p": record["p"], "q": record["q"], "a_size": len(a_points), "r_size": len(sources), "supports": {"d2": len(d2), "d4": len(d4)}, "state_digests": {"d2": digest(serialize_states(d2)), "d4": digest(serialize_states(d4))}, "pair_index": {"record_digest": digest([[point_json(point), left_id, right_id] for point, left_id, right_id in records]), "record_count": len(records), "advice": advice}, "build_ops": {"d2": d2_ops, "d4": d4_ops, "pair": pair_ops}, "targets": target_rows}


def serialize_input(input_path: Path, families: list[str], widths: list[int]) -> dict[str, Any]:
    source = json.loads(input_path.read_text(encoding="utf-8")); rows = []
    for instance in source["instances"]:
        by_family = {item["family"]: item for item in instance["families"]}
        for family_name in families:
            rows.append(run_row(instance["curve"], by_family[family_name], widths))
    routes = ["recursive_d2", "materialized_d4", "exact_state_pair"] + [f"fingerprint_w{width}" for width in widths]
    return {"protocol": "EXP-ECDLP-COORD-EXPANSION-001-implicit-pair-state-index-v1", "claim_status": ["HYPOTHESIS", "TOY-EVIDENCE", "MODEL-BOUND"], "source": {"producer_sha256": sha256_file(SCRIPT_PATH), "input_sha256": sha256_file(input_path)}, "config": {"input_result": str(input_path.resolve()), "families": families, "targets": ["planted", "held_out", "shifted_control"], "routes": routes, "widths": widths, "fingerprint": "identity-or-(x mod 2^w,y mod 2^w)", "witness_policy": "all nondecreasing D2 witness lists, deferred state-ID pair lift, canonicalized four-source tuples", "frontier": "logical advice words and charged affine group/field operation proxy; S*T^2/q diagnostic only"}, "rows": rows, "summary": {"cells": len(rows), "targets": sum(len(row["targets"]) for row in rows), "all_routes_exact": all(target["all_routes_equal"] for row in rows for target in row["targets"]), "algorithm_promotion_gate": False, "breakthrough_claim": False, "boundary": "Exact implicit witness-lift pair-state preflight; no generic ECDLP claim."}, "accounting": {"d2_build_adds": sum(row["build_ops"]["d2"]["point_add_calls"] for row in rows), "d4_build_adds": sum(row["build_ops"]["d4"]["point_add_calls"] for row in rows), "pair_build_adds": sum(row["build_ops"]["pair"]["point_add_calls"] for row in rows), "target_queries": sum(len(row["targets"]) for row in rows)}}


def run(input_path: Path, families: list[str], widths: list[int]) -> dict[str, Any]:
    started = time.perf_counter(); result = serialize_input(input_path, families, widths); result["peak_rss_bytes"] = rss_bytes(); result["total_wall_seconds"] = time.perf_counter() - started; return result


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("input", type=Path); parser.add_argument("--families", nargs="+", required=True); parser.add_argument("--widths", nargs="+", type=int, default=[1, 2, 4, 8]); args = parser.parse_args()
    if any(width <= 0 or width > 12 for width in args.widths) or len(set(args.widths)) != len(args.widths):
        raise SystemExit("widths must be distinct integers in [1,12]")
    print(json.dumps(run(args.input, args.families, args.widths), sort_keys=True, separators=(",", ":"))); return 0


if __name__ == "__main__":
    raise SystemExit(main())
