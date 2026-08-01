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

    def neg(self, value: Point) -> Point:
        return None if value is None else (value[0], (-value[1]) % self.p)

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


def empty_ops() -> Ops:
    return {"point_add_calls": 0, "field_inversions": 0, "field_multiplications": 0}


def state_level(curve: AffineCurve, sources: list[Point], level: int, ops: Ops) -> dict[Point, list[tuple[int, ...]]]:
    states: dict[Point, list[tuple[int, ...]]] = {}
    for witness in itertools.combinations_with_replacement(range(len(sources)), level):
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
    generator = as_point(record["generator"])
    shifted = curve.add(planted, generator, empty_ops())
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
        raise AssertionError("pair-index witness mismatch")


def build_pair_records(curve: AffineCurve, d2: dict[Point, list[tuple[int, ...]]], ops: Ops) -> list[tuple[Point, tuple[int, ...]]]:
    points = sorted(d2, key=point_key)
    records: list[tuple[Point, tuple[int, ...]]] = []
    for left_index, left_point in enumerate(points):
        for right_point in points[left_index:]:
            pair_sum = curve.add(left_point, right_point, ops)
            for left_witness in d2[left_point]:
                for right_witness in d2[right_point]:
                    records.append((pair_sum, tuple(sorted(left_witness + right_witness))))
    return records


def build_indices(records: list[tuple[Point, tuple[int, ...]]], widths: list[int]) -> dict[str, Any]:
    exact: dict[str, list[list[int]]] = {}
    buckets: dict[str, dict[str, list[list[int]]]] = {}
    for point, witness in records:
        exact.setdefault(json.dumps(point_json(point), separators=(",", ":")), []).append(list(witness))
        for width in widths:
            modulus = 1 << width
            key = json.dumps(fingerprint(point, modulus), separators=(",", ":"))
            buckets.setdefault(str(width), {}).setdefault(key, []).append(list(witness))
    return {"exact": exact, "buckets": buckets}


def query_recursive(curve: AffineCurve, a_points: list[Point], r_points: list[Point], d2: dict[Point, list[tuple[int, ...]]], target: Point, ops: Ops) -> tuple[set[tuple[int, ...]], dict[str, int]]:
    hits: set[tuple[int, ...]] = set()
    lookups = 0
    candidates = 0
    rejected = 0
    for a_point in a_points:
        after_a = curve.subtract(target, a_point, ops)
        for left_point, left_witnesses in d2.items():
            complement = curve.subtract(after_a, left_point, ops)
            right_witnesses = d2.get(complement, [])
            lookups += 1
            candidates += len(left_witnesses) * len(right_witnesses)
            for left_witness in left_witnesses:
                for right_witness in right_witnesses:
                    witness = tuple(sorted(left_witness + right_witness))
                    replay_witness(curve, r_points, witness, after_a, ops)
                    hits.add(witness)
    return hits, {"lookups": lookups, "candidate_records": candidates}


def query_pair(curve: AffineCurve, a_points: list[Point], r_points: list[Point], index: dict[str, list[list[int]]], target: Point, ops: Ops, mode: str, modulus: int | None = None) -> tuple[set[tuple[int, ...]], dict[str, int]]:
    hits: set[tuple[int, ...]] = set()
    candidates = 0
    rejected = 0
    lookups = 0
    for a_point in a_points:
        complement = curve.subtract(target, a_point, ops)
        if mode == "exact":
            key = json.dumps(point_json(complement), separators=(",", ":"))
        else:
            assert modulus is not None
            key = json.dumps(fingerprint(complement, modulus), separators=(",", ":"))
        witnesses = index.get(key, [])
        lookups += 1
        candidates += len(witnesses)
        for raw_witness in witnesses:
            witness = tuple(raw_witness)
            if witness_sum(curve, r_points, witness, ops) == complement:
                hits.add(witness)
            else:
                rejected += 1
    return hits, {"lookups": lookups, "candidate_records": candidates, "rejected_candidates": rejected}


def query_materialized_d4(curve: AffineCurve, a_points: list[Point], r_points: list[Point], d4: dict[Point, list[tuple[int, ...]]], target: Point, ops: Ops) -> tuple[set[tuple[int, ...]], dict[str, int]]:
    hits: set[tuple[int, ...]] = set()
    candidates = 0
    for a_point in a_points:
        complement = curve.subtract(target, a_point, ops)
        witnesses = d4.get(complement, [])
        candidates += len(witnesses)
        for witness in witnesses:
            replay_witness(curve, r_points, witness, complement, ops)
            hits.add(tuple(witness))
    return hits, {"lookups": len(a_points), "candidate_records": candidates, "rejected_candidates": 0}


def advice(states: dict[Point, list[tuple[int, ...]]], level: int) -> dict[str, int]:
    records = sum(len(value) for value in states.values())
    return {"state_count": len(states), "witness_records": records, "key_field_elements": 2 * len(states), "witness_index_words": level * records, "logical_advice_words": 2 * len(states) + level * records}


def pair_advice(records: list[tuple[Point, tuple[int, ...]]], index: dict[str, Any], widths: list[int]) -> dict[str, Any]:
    result: dict[str, Any] = {"pair_records": len(records), "witness_index_words": 4 * len(records), "exact": {"bucket_count": len(index["exact"]), "key_field_elements": 2 * len(index["exact"])}, "fingerprints": {}}
    for width in widths:
        buckets = index["buckets"][str(width)]
        result["fingerprints"][str(width)] = {"bucket_count": len(buckets), "key_field_elements": len(buckets), "logical_advice_words": len(buckets) + 4 * len(records)}
    result["exact"]["logical_advice_words"] = result["exact"]["key_field_elements"] + 4 * len(records)
    return result


def run_row(record: dict[str, Any], family: dict[str, Any], widths: list[int]) -> dict[str, Any]:
    curve = AffineCurve(record["p"], record["a"], record["b"])
    a_points = [as_point(value) for value in family["progression"]["points"]]
    r_points = [as_point(value) for value in family["factor_base"]["points"]]
    d2_ops = empty_ops(); d4_ops = empty_ops(); pair_ops = empty_ops()
    d2 = state_level(curve, r_points, 2, d2_ops)
    d4 = state_level(curve, r_points, 4, d4_ops)
    records = build_pair_records(curve, d2, pair_ops)
    indices = build_indices(records, widths)
    pair_cost = pair_advice(records, indices, widths)
    target_rows = []
    for label, target in target_choices(curve, record, family).items():
        rec_ops = empty_ops(); d4_query_ops = empty_ops(); exact_ops = empty_ops()
        bucket_ops = {str(width): empty_ops() for width in widths}
        recursive_hits, recursive_metrics = query_recursive(curve, a_points, r_points, d2, target, rec_ops)
        exact_hits, exact_metrics = query_pair(curve, a_points, r_points, indices["exact"], target, exact_ops, "exact")
        routes: dict[str, Any] = {
            "recursive_d2": {"hits": sorted([list(item) for item in recursive_hits]), "metrics": recursive_metrics, "ops": rec_ops, "advice": advice(d2, 2)},
            "materialized_d4": {},
            "exact_pair_index": {"hits": sorted([list(item) for item in exact_hits]), "metrics": exact_metrics, "ops": exact_ops, "advice": pair_cost["exact"]},
        }
        d4_hits, d4_metrics = query_materialized_d4(curve, a_points, r_points, d4, target, d4_query_ops)
        routes["materialized_d4"] = {"hits": sorted([list(item) for item in d4_hits]), "metrics": d4_metrics, "ops": d4_query_ops, "advice": advice(d4, 4)}
        for width in widths:
            hits, metrics = query_pair(curve, a_points, r_points, indices["buckets"][str(width)], target, bucket_ops[str(width)], "fingerprint", 1 << width)
            routes[f"fingerprint_w{width}"] = {"hits": sorted([list(item) for item in hits]), "metrics": metrics, "ops": bucket_ops[str(width)], "advice": pair_cost["fingerprints"][str(width)]}
        for route in routes.values():
            online = sum(route["ops"].values())
            words = route["advice"]["logical_advice_words"]
            route["frontier"] = {"online_work": online, "advice_words": words, "S_T2_over_q": words * online * online / record["q"], "success": bool(route["hits"])}
        target_rows.append({"label": label, "target": point_json(target), "routes": routes, "all_routes_equal": all(route["hits"] == routes["recursive_d2"]["hits"] for route in routes.values())})
    return {
        "curve_id": record["id"], "family": family["family"], "p": record["p"], "q": record["q"], "a_size": len(a_points), "r_size": len(r_points),
        "supports": {"d2": len(d2), "d4": len(d4)}, "state_digests": {"d2": digest(serialize_states(d2)), "d4": digest(serialize_states(d4))},
        "pair_index": {"record_digest": digest([[point_json(point), list(witness)] for point, witness in records]), "record_count": len(records), "advice": pair_cost},
        "build_ops": {"d2": d2_ops, "d4": d4_ops, "pair": pair_ops}, "targets": target_rows,
    }


def replay(input_path: Path, families: list[str], widths: list[int]) -> dict[str, Any]:
    source = json.loads(input_path.read_text(encoding="utf-8"))
    rows = []
    for instance in source["instances"]:
        by_family = {item["family"]: item for item in instance["families"]}
        for family_name in families:
            rows.append(run_row(instance["curve"], by_family[family_name], widths))
    routes = ["recursive_d2", "materialized_d4", "exact_pair_index"] + [f"fingerprint_w{width}" for width in widths]
    return {
        "protocol": "EXP-ECDLP-COORD-EXPANSION-001-target-conditioned-pair-index-v1",
        "claim_status": ["HYPOTHESIS", "TOY-EVIDENCE", "MODEL-BOUND"],
        "source": {"producer_sha256": sha256_file(SCRIPT_PATH), "input_sha256": sha256_file(input_path)},
        "config": {"input_result": str(input_path.resolve()), "families": families, "targets": ["planted", "held_out", "shifted_control"], "routes": routes, "widths": widths, "fingerprint": "identity-or-(x mod 2^w,y mod 2^w)", "witness_policy": "all nondecreasing D2 witness products, canonicalized four-source tuples", "frontier": "logical advice words and charged affine group/field operation proxy; S*T^2/q diagnostic only"},
        "rows": rows,
        "summary": {"cells": len(rows), "targets": sum(len(row["targets"]) for row in rows), "all_routes_exact": all(target["all_routes_equal"] for row in rows for target in row["targets"]), "algorithm_promotion_gate": False, "breakthrough_claim": False, "boundary": "Exact target-conditioned coordinate pair-index preflight; no generic ECDLP claim."},
        "accounting": {"d2_build_adds": sum(row["build_ops"]["d2"]["point_add_calls"] for row in rows), "d4_build_adds": sum(row["build_ops"]["d4"]["point_add_calls"] for row in rows), "pair_build_adds": sum(row["build_ops"]["pair"]["point_add_calls"] for row in rows), "target_queries": sum(len(row["targets"]) for row in rows)},
    }


def run(input_path: Path, families: list[str], widths: list[int]) -> dict[str, Any]:
    started = time.perf_counter()
    result = replay(input_path, families, widths)
    result["peak_rss_bytes"] = rss_bytes()
    result["total_wall_seconds"] = time.perf_counter() - started
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--families", nargs="+", required=True)
    parser.add_argument("--widths", nargs="+", type=int, default=[1, 2, 4, 8])
    args = parser.parse_args()
    if any(width <= 0 or width > 12 for width in args.widths) or len(set(args.widths)) != len(args.widths):
        raise SystemExit("widths must be distinct integers in [1,12]")
    print(json.dumps(run(args.input, args.families, args.widths), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
