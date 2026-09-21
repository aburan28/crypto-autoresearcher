#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
PRODUCER_PATH = SCRIPT_PATH.with_name("negation_quotient_fixed_preprocessing.py")
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


def point_sort_key(value: Point) -> tuple[int, int, int]:
    return (1, 0, 0) if value is None else (0, value[0], value[1])


def sign_bit(y: int, p: int) -> int:
    return int(y > p - y)


def state_level(curve: Curve, sources: list[Point], level: int, ops: dict[str, int]) -> dict[Point, list[tuple[int, ...]]]:
    states: dict[Point, list[tuple[int, ...]]] = {}
    for witness in itertools.combinations_with_replacement(range(len(sources)), level):
        total: Point = None
        for index in witness:
            total = curve.add(total, sources[index], ops)
        states.setdefault(total, []).append(witness)
    return states


def serialize_states(states: dict[Point, list[tuple[int, ...]]]) -> list[list[Any]]:
    return [[point_json(point), [list(witness) for witness in witnesses]] for point, witnesses in sorted(states.items(), key=lambda item: point_sort_key(item[0]))]


def build_x_index(states: dict[Point, list[tuple[int, ...]]]) -> dict[str, Any]:
    buckets: dict[str, dict[str, list[tuple[int, ...]]]] = {}
    infinity: list[tuple[int, ...]] = []
    for point, witnesses in states.items():
        if point is None:
            infinity.extend(witnesses)
        else:
            x, y = point
            buckets.setdefault(str(x), {}).setdefault(str(sign_bit(y, 0) if False else 0), [])
            # The sign is filled by the caller because this verifier binds p explicitly.
            buckets[str(x)].setdefault("__raw__", []).extend(witnesses)
    return {"buckets": buckets, "infinity": infinity}


def build_x_index_p(states: dict[Point, list[tuple[int, ...]]], p: int) -> dict[str, Any]:
    buckets: dict[str, dict[str, list[tuple[int, ...]]]] = {}
    infinity: list[tuple[int, ...]] = []
    for point, witnesses in states.items():
        if point is None:
            infinity.extend(witnesses)
        else:
            x, y = point
            buckets.setdefault(str(x), {}).setdefault(str(sign_bit(y, p)), []).extend(witnesses)
    return {"buckets": buckets, "infinity": infinity}


def targets(curve: Curve, record: dict[str, Any], family: dict[str, Any]) -> dict[str, Point]:
    planted = as_point(family["relations"]["target_transcript"][0]["target"])
    held_out = as_point(family["held_out_descent"]["transcript"][0]["target"])
    generator = as_point(record["generator"])
    ops = {"point_add_calls": 0, "field_inversions": 0, "field_multiplications": 0}
    shifted = curve.add(planted, generator, ops)
    if shifted is None:
        raise AssertionError("shifted target became identity")
    return {"planted": planted, "held_out": held_out, "shifted_control": shifted}


def lookup_full(index: dict[Point, list[tuple[int, ...]]], point: Point) -> list[tuple[int, ...]]:
    return index.get(point, [])


def lookup_x(index: dict[str, Any], point: Point, p: int) -> list[tuple[int, ...]]:
    if point is None:
        return index["infinity"]
    x, y = point
    return index["buckets"].get(str(x), {}).get(str(sign_bit(y, p)), [])


def canonical_hits(curve: Curve, a_points: list[Point], r_points: list[Point], d3: dict[Point, list[tuple[int, ...]]], target: Point, ops: dict[str, int], kind: str, x_index: dict[str, Any] | None, p: int) -> tuple[list[list[int]], dict[str, int]]:
    hits: set[tuple[int, ...]] = set()
    lookup_count = 0
    candidate_witnesses = 0
    for a_index, a_point in enumerate(a_points):
        after_a = curve.subtract(target, a_point, ops)
        for r_index, r_point in enumerate(r_points):
            complement = curve.subtract(after_a, r_point, ops)
            witnesses = lookup_full(d3, complement) if kind == "point" else lookup_x(x_index or {}, complement, p)
            lookup_count += 1
            candidate_witnesses += len(witnesses)
            for witness in witnesses:
                combined = tuple(sorted((r_index,) + witness))
                total: Point = None
                for index in combined:
                    total = curve.add(total, r_points[index], ops)
                expected = after_a
                if total != expected:
                    raise AssertionError("witness replay mismatch")
                hits.add(combined)
    return [list(hit) for hit in sorted(hits)], {"lookups": lookup_count, "candidate_witnesses": candidate_witnesses}


def query_d4(curve: Curve, a_points: list[Point], d4: dict[Point, list[tuple[int, ...]]], target: Point) -> tuple[list[list[int]], dict[str, int], dict[str, int]]:
    hits: set[tuple[int, ...]] = set()
    candidate_witnesses = 0
    ops = {"point_add_calls": 0, "field_inversions": 0, "field_multiplications": 0}
    for a_point in a_points:
        complement = curve.subtract(target, a_point, ops)
        witnesses = d4.get(complement, [])
        candidate_witnesses += len(witnesses)
        hits.update(tuple(sorted(witness)) for witness in witnesses)
    return [list(hit) for hit in sorted(hits)], {"lookups": len(a_points), "candidate_witnesses": candidate_witnesses}, ops


def logical_advice(states: dict[Point, list[tuple[int, ...]]], level: int, x_index: dict[str, Any] | None = None) -> dict[str, int]:
    witness_records = sum(len(value) for value in states.values())
    if x_index is None:
        key_fields, sign_bits_count = 2 * len(states), 0
    else:
        key_fields = len(x_index["buckets"])
        sign_bits_count = sum(len(signs) for signs in x_index["buckets"].values()) + int(bool(x_index["infinity"]))
    return {"state_count": len(states), "witness_records": witness_records, "key_field_elements": key_fields, "sign_bits": sign_bits_count, "witness_index_words": level * witness_records, "logical_advice_words": key_fields + sign_bits_count + level * witness_records}


def row(record: dict[str, Any], family: dict[str, Any]) -> dict[str, Any]:
    p = record["p"]
    curve = Curve(p, record["a"])
    a_points = [as_point(value) for value in family["progression"]["points"]]
    r_points = [as_point(value) for value in family["factor_base"]["points"]]
    d3_ops = {"point_add_calls": 0, "field_inversions": 0, "field_multiplications": 0}
    d4_ops = {"point_add_calls": 0, "field_inversions": 0, "field_multiplications": 0}
    d3 = state_level(curve, r_points, 3, d3_ops)
    d4 = state_level(curve, r_points, 4, d4_ops)
    x_index = build_x_index_p(d3, p)
    advice = {"d3_point": logical_advice(d3, 3), "d3_x_quotient": logical_advice(d3, 3, x_index), "d4_point": logical_advice(d4, 4)}
    target_rows = []
    for label, target in targets(curve, record, family).items():
        point_ops = {"point_add_calls": 0, "field_inversions": 0, "field_multiplications": 0}
        x_ops = {"point_add_calls": 0, "field_inversions": 0, "field_multiplications": 0}
        full_hits, full_metrics = canonical_hits(curve, a_points, r_points, d3, target, point_ops, "point", None, p)
        x_hits, x_metrics = canonical_hits(curve, a_points, r_points, d3, target, x_ops, "x", x_index, p)
        d4_hits, d4_metrics, d4_query_ops = query_d4(curve, a_points, d4, target)
        target_row = {"label": label, "target": point_json(target), "full_point": {"hits": full_hits, "metrics": full_metrics, "ops": point_ops}, "x_quotient": {"hits": x_hits, "metrics": x_metrics, "ops": x_ops}, "materialized_d4": {"hits": d4_hits, "metrics": d4_metrics, "ops": d4_query_ops}, "full_equals_x": full_hits == x_hits, "full_equals_d4": full_hits == d4_hits}
        target_row["frontier"] = {}
        for name, advice_name in (("full_point", "d3_point"), ("x_quotient", "d3_x_quotient"), ("materialized_d4", "d4_point")):
            ops = target_row[name]["ops"]
            online = ops["point_add_calls"] + ops["field_inversions"] + ops["field_multiplications"]
            words = advice[advice_name]["logical_advice_words"]
            target_row["frontier"][name] = {"online_work": online, "advice_words": words, "S_T2_over_q": words * online * online / record["q"], "success": bool(target_row[name]["hits"])}
        target_rows.append(target_row)
    return {"curve_id": record["id"], "family": family["family"], "p": p, "q": record["q"], "a_size": len(a_points), "r_size": len(r_points), "d3_support": len(d3), "d4_support": len(d4), "d3_state_digest": digest(serialize_states(d3)), "d4_state_digest": digest(serialize_states(d4)), "advice": advice, "build_ops": {"d3": d3_ops, "d4": d4_ops}, "targets": target_rows}


def replay(input_path: Path, families: list[str]) -> dict[str, Any]:
    source = json.loads(input_path.read_text(encoding="utf-8"))
    rows = []
    for instance in source["instances"]:
        record = instance["curve"]
        by_family = {item["family"]: item for item in instance["families"]}
        for family_name in families:
            rows.append(row(record, by_family[family_name]))
    return {"protocol": "EXP-ECDLP-COORD-EXPANSION-001-negation-quotient-fixed-preprocessing-v1", "claim_status": ["HYPOTHESIS", "TOY-EVIDENCE", "MODEL-BOUND"], "source": {"producer_sha256": sha256_file(PRODUCER_PATH), "input_sha256": sha256_file(input_path)}, "config": {"input_result": str(input_path.resolve()), "families": families, "target_batch": ["planted", "held_out", "shifted_control"], "candidate": "x-coordinate plus elliptic-negation sign mask over exact D3 states", "baselines": ["full point-keyed D3", "materialized point-keyed D4"], "frontier": "logical advice words and online group/field operation proxy; S*T^2/q is diagnostic only"}, "rows": rows, "summary": {"cells": len(rows), "targets": sum(len(row["targets"]) for row in rows), "all_quotient_checks_exact": all(query["full_equals_x"] for row in rows for query in row["targets"]), "all_d4_checks_exact": all(query["full_equals_d4"] for row in rows for query in row["targets"]), "algorithm_promotion_gate": False, "breakthrough_claim": False, "boundary": "Fixed-curve negation quotient and preprocessing tradeoff only; no generic ECDLP claim."}, "accounting": {"d3_build_point_adds": sum(row["build_ops"]["d3"]["point_add_calls"] for row in rows), "d4_build_point_adds": sum(row["build_ops"]["d4"]["point_add_calls"] for row in rows), "query_targets": sum(len(row["targets"]) for row in rows)}}


def normalize(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: normalize(item) for key, item in value.items() if key not in {"peak_rss_bytes", "total_wall_seconds"}}
    if isinstance(value, list):
        return [normalize(item) for item in value]
    return value


def check(raw: dict[str, Any], input_path: Path) -> dict[str, bool]:
    checks = {"protocol": False, "producer_hash": False, "input_hash": False, "candidate": False, "promotion_false": False, "breakthrough_false": False, "boundary": False}
    try:
        checks.update({"protocol": raw["protocol"] == "EXP-ECDLP-COORD-EXPANSION-001-negation-quotient-fixed-preprocessing-v1", "producer_hash": raw["source"]["producer_sha256"] == sha256_file(PRODUCER_PATH), "input_hash": raw["source"]["input_sha256"] == sha256_file(input_path), "candidate": "sign mask" in raw["config"]["candidate"], "promotion_false": raw["summary"]["algorithm_promotion_gate"] is False, "breakthrough_false": raw["summary"]["breakthrough_claim"] is False, "boundary": "no generic ECDLP claim" in raw["summary"]["boundary"]})
    except (KeyError, TypeError, IndexError):
        pass
    return checks


def mutation_rejections(raw: dict[str, Any], input_path: Path, expected: dict[str, Any]) -> dict[str, bool]:
    mutations = {}
    changed = copy.deepcopy(raw); changed["protocol"] = "wrong"; mutations["protocol"] = changed
    changed = copy.deepcopy(raw); changed["source"]["producer_sha256"] = "0" * 64; mutations["producer_hash"] = changed
    changed = copy.deepcopy(raw); changed["rows"][0]["targets"][0]["full_equals_x"] = False; mutations["quotient_flag"] = changed
    changed = copy.deepcopy(raw); changed["rows"][0]["advice"]["d3_x_quotient"]["logical_advice_words"] += 1; mutations["advice_words"] = changed
    changed = copy.deepcopy(raw); changed["summary"]["breakthrough_claim"] = True; mutations["boundary_gate"] = changed
    return {name: not (all(check(candidate, input_path).values()) and normalize(candidate) == normalize(expected)) for name, candidate in mutations.items()}


def verify(raw_path: Path, input_override: Path | None = None) -> dict[str, Any]:
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    input_path = input_override if input_override is not None else Path(raw["config"]["input_result"])
    expected = replay(input_path, raw["config"]["families"])
    checks = check(raw, input_path)
    checks["normalized_replay_exact"] = normalize(raw) == normalize(expected)
    mutations = mutation_rejections(raw, input_path, expected)
    checks["mutation_rejections"] = all(mutations.values())
    return {"protocol": "EXP-ECDLP-COORD-EXPANSION-001-negation-quotient-fixed-preprocessing-verifier", "raw_result_sha256": sha256_file(raw_path), "input_result_sha256": sha256_file(input_path), "producer_sha256": sha256_file(PRODUCER_PATH), "verifier_sha256": sha256_file(SCRIPT_PATH), "raw_normalized_sha256": digest(normalize(raw)), "replay_normalized_sha256": digest(normalize(expected)), "checks": checks, "mutation_rejections_by_name": mutations, "rows_replayed": len(expected["rows"]), "valid": all(checks.values()), "boundary": "Independent fixed-curve quotient replay; no generic ECDLP claim."}


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("raw_result", type=Path)
    parser.add_argument("--input", type=Path)
    args = parser.parse_args()
    receipt = verify(args.raw_result, args.input)
    print(json.dumps(receipt, sort_keys=True, separators=(",", ":")))
    return 0 if receipt["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
