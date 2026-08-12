#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import platform
import resource
import time
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
Point = tuple[int, int] | None


class AffineCurve:
    def __init__(self, p: int, a: int, b: int) -> None:
        self.p, self.a, self.b = p, a % p, b % p

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
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")).hexdigest()


def rss_bytes() -> int:
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(value if platform.system() == "Darwin" else value * 1024)


def as_point(value: list[int] | None) -> Point:
    return None if value is None else (value[0], value[1])


def point_json(value: Point) -> list[int] | None:
    return None if value is None else [value[0], value[1]]


def point_sort_key(value: Point) -> tuple[int, int, int]:
    return (1, 0, 0) if value is None else (0, value[0], value[1])


def sign_bit(y: int, p: int) -> int:
    return int(y > p - y)


def state_level(curve: AffineCurve, sources: list[Point], level: int, ops: dict[str, int]) -> dict[Point, list[tuple[int, ...]]]:
    states: dict[Point, list[tuple[int, ...]]] = {}
    for witness in itertools.combinations_with_replacement(range(len(sources)), level):
        total: Point = None
        for index in witness:
            total = curve.add(total, sources[index], ops)
        states.setdefault(total, []).append(witness)
    return states


def serialize_states(states: dict[Point, list[tuple[int, ...]]]) -> list[list[Any]]:
    return [[point_json(point), [list(witness) for witness in witnesses]] for point, witnesses in sorted(states.items(), key=lambda item: point_sort_key(item[0]))]


def build_x_index(states: dict[Point, list[tuple[int, ...]]], p: int) -> dict[str, Any]:
    buckets: dict[str, dict[str, list[tuple[int, ...]]]] = {}
    infinity: list[tuple[int, ...]] = []
    for point, witnesses in states.items():
        if point is None:
            infinity.extend(witnesses)
            continue
        x, y = point
        buckets.setdefault(str(x), {}).setdefault(str(sign_bit(y, p)), []).extend(witnesses)
    return {"buckets": buckets, "infinity": infinity}


def target_choices(curve: AffineCurve, record: dict[str, Any], family: dict[str, Any]) -> dict[str, Point]:
    planted = as_point(family["relations"]["target_transcript"][0]["target"])
    held_out = as_point(family["held_out_descent"]["transcript"][0]["target"])
    generator = as_point(record["generator"])
    ops = {"point_add_calls": 0, "field_inversions": 0, "field_multiplications": 0}
    shifted = curve.add(planted, generator, ops)
    if shifted is None:
        raise AssertionError("shifted target became identity")
    return {"planted": planted, "held_out": held_out, "shifted_control": shifted}


def lookup_witnesses_full(index: dict[Point, list[tuple[int, ...]]], point: Point) -> list[tuple[int, ...]]:
    return index.get(point, [])


def lookup_witnesses_x(index: dict[str, Any], point: Point, p: int) -> list[tuple[int, ...]]:
    if point is None:
        return index["infinity"]
    x, y = point
    return index["buckets"].get(str(x), {}).get(str(sign_bit(y, p)), [])


def canonical_hits(curve: AffineCurve, a_points: list[Point], r_points: list[Point], d3: dict[Point, list[tuple[int, ...]]], target: Point, ops: dict[str, int], lookup_kind: str, x_index: dict[str, Any] | None, p: int) -> tuple[list[list[int]], dict[str, int]]:
    hits: set[tuple[int, ...]] = set()
    lookup_count = 0
    candidate_witnesses = 0
    for a_index, a_point in enumerate(a_points):
        after_a = curve.subtract(target, a_point, ops)
        for r_index, r_point in enumerate(r_points):
            complement = curve.subtract(after_a, r_point, ops)
            if lookup_kind == "point":
                witnesses = lookup_witnesses_full(d3, complement)
            else:
                assert x_index is not None
                witnesses = lookup_witnesses_x(x_index, complement, p)
            lookup_count += 1
            candidate_witnesses += len(witnesses)
            for witness in witnesses:
                combined = tuple(sorted((r_index,) + witness))
                total: Point = None
                for index in combined:
                    total = curve.add(total, r_points[index], ops)
                if total != after_a:
                    raise AssertionError("D3 witness replay mismatch")
                hits.add(combined)
    return [list(hit) for hit in sorted(hits)], {"lookups": lookup_count, "candidate_witnesses": candidate_witnesses}


def query_d4(curve: AffineCurve, a_points: list[Point], d4: dict[Point, list[tuple[int, ...]]], target: Point, r_points: list[Point], ops: dict[str, int]) -> tuple[list[list[int]], dict[str, int]]:
    hits: set[tuple[int, ...]] = set()
    for a_index, a_point in enumerate(a_points):
        complement = curve.subtract(target, a_point, ops)
        for witness in d4.get(complement, []):
            hits.add(tuple(sorted(witness)))
    return [list(hit) for hit in sorted(hits)], {"lookups": len(a_points), "candidate_witnesses": sum(len(d4.get(curve.subtract(target, a, {"point_add_calls": 0, "field_inversions": 0, "field_multiplications": 0}), [])) for a in a_points)}


def logical_advice(states: dict[Point, list[tuple[int, ...]]], level: int, x_index: dict[str, Any] | None = None) -> dict[str, int]:
    witness_records = sum(len(value) for value in states.values())
    if x_index is None:
        key_fields = 2 * len(states)
        sign_bits = 0
    else:
        key_fields = len(x_index["buckets"])
        sign_bits = sum(len(signs) for signs in x_index["buckets"].values()) + int(bool(x_index["infinity"]))
    return {"state_count": len(states), "witness_records": witness_records, "key_field_elements": key_fields, "sign_bits": sign_bits, "witness_index_words": level * witness_records, "logical_advice_words": key_fields + sign_bits + level * witness_records}


def run_row(record: dict[str, Any], family: dict[str, Any]) -> dict[str, Any]:
    p = record["p"]
    curve = AffineCurve(p, record["a"], record["b"])
    a_points = [as_point(value) for value in family["progression"]["points"]]
    r_points = [as_point(value) for value in family["factor_base"]["points"]]
    build_ops_d3 = {"point_add_calls": 0, "field_inversions": 0, "field_multiplications": 0}
    build_ops_d4 = {"point_add_calls": 0, "field_inversions": 0, "field_multiplications": 0}
    d3 = state_level(curve, r_points, 3, build_ops_d3)
    d4 = state_level(curve, r_points, 4, build_ops_d4)
    x_index = build_x_index(d3, p)
    targets = target_choices(curve, record, family)
    query_rows = []
    for label, target in targets.items():
        point_ops = {"point_add_calls": 0, "field_inversions": 0, "field_multiplications": 0}
        x_ops = {"point_add_calls": 0, "field_inversions": 0, "field_multiplications": 0}
        d4_ops = {"point_add_calls": 0, "field_inversions": 0, "field_multiplications": 0}
        full_hits, full_metrics = canonical_hits(curve, a_points, r_points, d3, target, point_ops, "point", None, p)
        x_hits, x_metrics = canonical_hits(curve, a_points, r_points, d3, target, x_ops, "x", x_index, p)
        d4_hits, d4_metrics = query_d4(curve, a_points, d4, target, r_points, d4_ops)
        query_rows.append({"label": label, "target": point_json(target), "full_point": {"hits": full_hits, "metrics": full_metrics, "ops": point_ops}, "x_quotient": {"hits": x_hits, "metrics": x_metrics, "ops": x_ops}, "materialized_d4": {"hits": d4_hits, "metrics": d4_metrics, "ops": d4_ops}, "full_equals_x": full_hits == x_hits, "full_equals_d4": full_hits == d4_hits})
    advice = {"d3_point": logical_advice(d3, 3), "d3_x_quotient": logical_advice(d3, 3, x_index), "d4_point": logical_advice(d4, 4)}
    for query in query_rows:
        query["frontier"] = {}
        for name in ("full_point", "x_quotient", "materialized_d4"):
            ops = query[name]["ops"]
            online = ops["point_add_calls"] + ops["field_inversions"] + ops["field_multiplications"]
            advice_words = advice["d3_point" if name == "full_point" else "d3_x_quotient" if name == "x_quotient" else "d4_point"]["logical_advice_words"]
            query["frontier"][name] = {"online_work": online, "advice_words": advice_words, "S_T2_over_q": advice_words * online * online / record["q"], "success": bool(query[name]["hits"])}
    return {"curve_id": record["id"], "family": family["family"], "p": p, "q": record["q"], "a_size": len(a_points), "r_size": len(r_points), "d3_support": len(d3), "d4_support": len(d4), "d3_state_digest": canonical_digest(serialize_states(d3)), "d4_state_digest": canonical_digest(serialize_states(d4)), "advice": advice, "build_ops": {"d3": build_ops_d3, "d4": build_ops_d4}, "targets": query_rows}


def run(input_path: Path, families: list[str]) -> dict[str, Any]:
    started = time.perf_counter()
    source = json.loads(input_path.read_text(encoding="utf-8"))
    rows = []
    for instance in source["instances"]:
        record = instance["curve"]
        by_family = {item["family"]: item for item in instance["families"]}
        for family_name in families:
            rows.append(run_row(record, by_family[family_name]))
    return {"protocol": "EXP-ECDLP-COORD-EXPANSION-001-negation-quotient-fixed-preprocessing-v1", "claim_status": ["HYPOTHESIS", "TOY-EVIDENCE", "MODEL-BOUND"], "source": {"producer_sha256": sha256_file(SCRIPT_PATH), "input_sha256": sha256_file(input_path)}, "config": {"input_result": str(input_path.resolve()), "families": families, "target_batch": ["planted", "held_out", "shifted_control"], "candidate": "x-coordinate plus elliptic-negation sign mask over exact D3 states", "baselines": ["full point-keyed D3", "materialized point-keyed D4"], "frontier": "logical advice words and online group/field operation proxy; S*T^2/q is diagnostic only"}, "rows": rows, "summary": {"cells": len(rows), "targets": sum(len(row["targets"]) for row in rows), "all_quotient_checks_exact": all(query["full_equals_x"] for row in rows for query in row["targets"]), "all_d4_checks_exact": all(query["full_equals_d4"] for row in rows for query in row["targets"]), "algorithm_promotion_gate": False, "breakthrough_claim": False, "boundary": "Fixed-curve negation quotient and preprocessing tradeoff only; no generic ECDLP claim."}, "accounting": {"d3_build_point_adds": sum(row["build_ops"]["d3"]["point_add_calls"] for row in rows), "d4_build_point_adds": sum(row["build_ops"]["d4"]["point_add_calls"] for row in rows), "query_targets": sum(len(row["targets"]) for row in rows)}, "peak_rss_bytes": rss_bytes(), "total_wall_seconds": time.perf_counter() - started}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--families", nargs="+", required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.input, args.families), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
