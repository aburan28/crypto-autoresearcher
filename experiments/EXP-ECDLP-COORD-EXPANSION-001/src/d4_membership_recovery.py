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


def states(curve: AffineCurve, sources: list[Point], degree: int, ops: Ops) -> dict[Point, list[tuple[int, ...]]]:
    output: dict[Point, list[tuple[int, ...]]] = {}
    for witness in itertools.combinations_with_replacement(range(len(sources)), degree):
        total: Point = None
        for index in witness:
            total = curve.add(total, sources[index], ops)
        output.setdefault(total, []).append(witness)
    return output


def serialize_states(states_map: dict[Point, list[tuple[int, ...]]]) -> list[list[Any]]:
    return [[point_json(point), [list(item) for item in witnesses]] for point, witnesses in sorted(states_map.items(), key=lambda item: point_key(item[0]))]


def target_choices(curve: AffineCurve, record: dict[str, Any], family: dict[str, Any]) -> dict[str, Point]:
    planted = as_point(family["relations"]["target_transcript"][0]["target"]); held_out = as_point(family["held_out_descent"]["transcript"][0]["target"]); shifted = curve.add(planted, as_point(record["generator"]), empty_ops())
    if shifted is None:
        raise AssertionError("shifted target became identity")
    return {"planted": planted, "held_out": held_out, "shifted_control": shifted}


def replay_witness(curve: AffineCurve, sources: list[Point], witness: tuple[int, ...], expected: Point, ops: Ops) -> None:
    total: Point = None
    for index in witness:
        total = curve.add(total, sources[index], ops)
    if total != expected:
        raise AssertionError("recovery witness mismatch")


def advice_d2(d2: dict[Point, list[tuple[int, ...]]]) -> dict[str, int]:
    records = sum(len(value) for value in d2.values())
    return {"state_count": len(d2), "witness_records": records, "key_field_elements": 2 * len(d2), "witness_index_words": 2 * records, "logical_advice_words": 2 * len(d2) + 2 * records}


def query_recursive(curve: AffineCurve, a_points: list[Point], sources: list[Point], d2: dict[Point, list[tuple[int, ...]]], target: Point, ops: Ops) -> tuple[set[tuple[int, ...]], dict[str, int]]:
    hits: set[tuple[int, ...]] = set(); pair_lookups = 0; products = 0
    for a_point in a_points:
        after_a = curve.subtract(target, a_point, ops)
        for left_point, left_witnesses in d2.items():
            right_point = curve.subtract(after_a, left_point, ops); right_witnesses = d2.get(right_point, [])
            pair_lookups += 1; products += len(left_witnesses) * len(right_witnesses)
            for left_witness in left_witnesses:
                for right_witness in right_witnesses:
                    witness = tuple(sorted(left_witness + right_witness)); replay_witness(curve, sources, witness, after_a, ops); hits.add(witness)
    return hits, {"membership_lookups": 0, "support_hits": 0, "recovery_pair_lookups": pair_lookups, "candidate_witness_products": products, "rejected_witnesses": 0}


def query_materialized(curve: AffineCurve, a_points: list[Point], sources: list[Point], d4: dict[Point, list[tuple[int, ...]]], target: Point, ops: Ops) -> tuple[set[tuple[int, ...]], dict[str, int]]:
    hits: set[tuple[int, ...]] = set(); products = 0; support_hits = 0
    for a_point in a_points:
        complement = curve.subtract(target, a_point, ops); witnesses = d4.get(complement, []); products += len(witnesses); support_hits += int(bool(witnesses))
        for witness in witnesses:
            replay_witness(curve, sources, witness, complement, ops); hits.add(tuple(witness))
    return hits, {"membership_lookups": len(a_points), "support_hits": support_hits, "recovery_pair_lookups": 0, "candidate_witness_products": products, "rejected_witnesses": 0}


def recover_one_complement(curve: AffineCurve, sources: list[Point], d2: dict[Point, list[tuple[int, ...]]], complement: Point, ops: Ops) -> tuple[set[tuple[int, ...]], int, int]:
    hits: set[tuple[int, ...]] = set(); pair_lookups = 0; products = 0
    for left_point, left_witnesses in d2.items():
        right_point = curve.subtract(complement, left_point, ops); right_witnesses = d2.get(right_point, [])
        pair_lookups += 1; products += len(left_witnesses) * len(right_witnesses)
        for left_witness in left_witnesses:
            for right_witness in right_witnesses:
                witness = tuple(sorted(left_witness + right_witness)); replay_witness(curve, sources, witness, complement, ops); hits.add(witness)
    return hits, pair_lookups, products


def query_membership_recovery(curve: AffineCurve, a_points: list[Point], sources: list[Point], d2: dict[Point, list[tuple[int, ...]]], d4_support: set[Point], target: Point, ops: Ops) -> tuple[set[tuple[int, ...]], dict[str, int]]:
    hits: set[tuple[int, ...]] = set(); support_hits = 0; pair_lookups = 0; products = 0
    for a_point in a_points:
        complement = curve.subtract(target, a_point, ops)
        if complement not in d4_support:
            continue
        support_hits += 1
        recovered, lookups, candidate_products = recover_one_complement(curve, sources, d2, complement, ops)
        hits.update(recovered); pair_lookups += lookups; products += candidate_products
    return hits, {"membership_lookups": len(a_points), "support_hits": support_hits, "recovery_pair_lookups": pair_lookups, "candidate_witness_products": products, "rejected_witnesses": 0}


def run_row(record: dict[str, Any], family: dict[str, Any]) -> dict[str, Any]:
    curve = AffineCurve(record["p"], record["a"], record["b"]); a_points = [as_point(value) for value in family["progression"]["points"]]; sources = [as_point(value) for value in family["factor_base"]["points"]]
    d2_ops = empty_ops(); d4_ops = empty_ops(); d2 = states(curve, sources, 2, d2_ops); d4 = states(curve, sources, 4, d4_ops); d2_adv = advice_d2(d2); d4_records = sum(len(value) for value in d4.values()); membership_adv = {"d2_base": d2_adv, "support_state_count": len(d4), "support_key_field_elements": 2 * len(d4), "logical_advice_words": d2_adv["logical_advice_words"] + 2 * len(d4)}; support = set(d4)
    target_rows = []
    for label, target in target_choices(curve, record, family).items():
        routes: dict[str, Any] = {}; ops = empty_ops(); hits, metrics = query_recursive(curve, a_points, sources, d2, target, ops); routes["recursive_d2"] = {"hits": sorted([list(item) for item in hits]), "metrics": metrics, "ops": ops, "advice": d2_adv}
        ops = empty_ops(); hits, metrics = query_materialized(curve, a_points, sources, d4, target, ops); routes["materialized_d4"] = {"hits": sorted([list(item) for item in hits]), "metrics": metrics, "ops": ops, "advice": {"state_count": len(d4), "witness_records": d4_records, "key_field_elements": 2 * len(d4), "witness_index_words": 4 * d4_records, "logical_advice_words": 2 * len(d4) + 4 * d4_records}}
        ops = empty_ops(); hits, metrics = query_membership_recovery(curve, a_points, sources, d2, support, target, ops); routes["membership_recovery"] = {"hits": sorted([list(item) for item in hits]), "metrics": metrics, "ops": ops, "advice": membership_adv}
        for route in routes.values():
            online = sum(route["ops"].values()); words = route["advice"]["logical_advice_words"]; route["frontier"] = {"online_work": online, "advice_words": words, "S_T2_over_q": words * online * online / record["q"], "success": bool(route["hits"])}
        baseline = routes["recursive_d2"]["hits"]; target_rows.append({"label": label, "target": point_json(target), "routes": routes, "all_routes_equal": all(route["hits"] == baseline for route in routes.values())})
    return {"curve_id": record["id"], "family": family["family"], "p": record["p"], "q": record["q"], "a_size": len(a_points), "r_size": len(sources), "supports": {"d2": len(d2), "d4": len(d4)}, "state_digests": {"d2": digest(serialize_states(d2)), "d4": digest(serialize_states(d4))}, "advice": {"d2": d2_adv, "d4": {"state_count": len(d4), "witness_records": d4_records, "logical_advice_words": 2 * len(d4) + 4 * d4_records}, "membership_recovery": membership_adv}, "build_ops": {"d2": d2_ops, "d4": d4_ops}, "targets": target_rows}


def replay(input_path: Path, families: list[str]) -> dict[str, Any]:
    source = json.loads(input_path.read_text(encoding="utf-8")); rows = []
    for instance in source["instances"]:
        by_family = {item["family"]: item for item in instance["families"]}
        for family_name in families:
            rows.append(run_row(instance["curve"], by_family[family_name]))
    return {"protocol": "EXP-ECDLP-COORD-EXPANSION-001-d4-membership-recovery-v1", "claim_status": ["HYPOTHESIS", "TOY-EVIDENCE", "MODEL-BOUND"], "source": {"producer_sha256": sha256_file(SCRIPT_PATH), "input_sha256": sha256_file(input_path)}, "config": {"input_result": str(input_path.resolve()), "families": families, "targets": ["planted", "held_out", "shifted_control"], "routes": ["recursive_d2", "materialized_d4", "membership_recovery"], "witness_policy": "D2 witness advice retained; D4 membership support only; exact recursive recovery on support hits", "frontier": "logical advice words and charged affine group/field operation proxy; S*T^2/q diagnostic only"}, "rows": rows, "summary": {"cells": len(rows), "targets": sum(len(row["targets"]) for row in rows), "all_routes_exact": all(target["all_routes_equal"] for row in rows for target in row["targets"]), "algorithm_promotion_gate": False, "breakthrough_claim": False, "boundary": "Exact D4 support membership with deferred D2 recovery; no generic ECDLP claim."}, "accounting": {"d2_build_adds": sum(row["build_ops"]["d2"]["point_add_calls"] for row in rows), "d4_build_adds": sum(row["build_ops"]["d4"]["point_add_calls"] for row in rows), "target_queries": sum(len(row["targets"]) for row in rows)}}


def run(input_path: Path, families: list[str]) -> dict[str, Any]:
    started = time.perf_counter(); result = replay(input_path, families); result["peak_rss_bytes"] = rss_bytes(); result["total_wall_seconds"] = time.perf_counter() - started; return result


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("input", type=Path); parser.add_argument("--families", nargs="+", required=True); args = parser.parse_args(); print(json.dumps(run(args.input, args.families), sort_keys=True, separators=(",", ":"))); return 0


if __name__ == "__main__":
    raise SystemExit(main())
