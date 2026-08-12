#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
PRODUCER_PATH = SCRIPT_PATH.with_name("nonlinear_s4_quotient_preflight.py")
Point = tuple[int, int] | None


class Curve:
    def __init__(self, p: int, a: int) -> None:
        self.p, self.a = p, a % p

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


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")
    ).hexdigest()


def as_point(value: list[int] | None) -> Point:
    return None if value is None else (value[0], value[1])


def point_json(value: Point) -> list[int] | None:
    return None if value is None else [value[0], value[1]]


def point_key(value: Point) -> tuple[int, int, int]:
    return (1, 0, 0) if value is None else (0, value[0], value[1])


def exact_rank(flat: list[int], rows: int, width: int, p: int) -> int:
    pivots: dict[int, list[int]] = {}
    rank = 0
    for row_index in range(rows):
        row = [value % p for value in flat[row_index * width:(row_index + 1) * width]]
        while True:
            pivot = next((index for index, value in enumerate(row) if value), None)
            if pivot is None:
                break
            prior = pivots.get(pivot)
            if prior is None:
                inverse = pow(row[pivot], -1, p)
                row = [(value * inverse) % p for value in row]
                pivots[pivot] = row
                rank += 1
                break
            factor = row[pivot]
            row = [(value - factor * base) % p for value, base in zip(row, prior)]
    return rank


def state_level(curve: Curve, sources: list[Point], level: int, ops: dict[str, int]) -> dict[Point, tuple[int, ...]]:
    states: dict[Point, tuple[int, ...]] = {}
    for witness in itertools.combinations_with_replacement(range(len(sources)), level):
        total: Point = None
        for index in witness:
            total = curve.add(total, sources[index], ops)
        states.setdefault(total, witness)
    return states


def serialized_states(states: dict[Point, tuple[int, ...]]) -> list[list[Any]]:
    return [[point_json(point), list(witness)] for point, witness in sorted(states.items(), key=lambda item: point_key(item[0]))]


def feature_ranks(states: dict[Point, tuple[int, ...]], p: int, max_degree: int) -> list[dict[str, Any]]:
    points = sorted(states, key=point_key)
    result = []
    for degree in range(max_degree + 1):
        terms = [(i, total - i) for total in range(degree + 1) for i in range(total + 1)]
        width = len(terms) + 1
        flat = []
        for point in points:
            if point is None:
                flat.extend([0] * len(terms)); flat.append(1)
            else:
                x, y = point
                flat.extend(pow(x, i, p) * pow(y, j, p) % p for i, j in terms); flat.append(0)
        result.append({"degree": degree, "basis_terms": len(terms), "columns": width, "rank": exact_rank(flat, len(points), width, p) if points else 0, "support": len(points), "identity_present": None in states})
    return result


def family_state_record(record: dict[str, Any], family: dict[str, Any], max_degree: int) -> dict[str, Any]:
    curve = Curve(record["p"], record["a"])
    sources = [as_point(value) for value in family["factor_base"]["points"]]
    ops = {"point_add_calls": 0, "field_inversions": 0, "field_multiplications": 0}
    levels = {}
    for level in (2, 3):
        states = state_level(curve, sources, level, ops)
        serialized = serialized_states(states)
        levels[str(level)] = {"attempted_tuples": len(list(itertools.combinations_with_replacement(range(len(sources)), level))), "support_size": len(states), "identity_present": None in states, "state_digest": canonical_digest(serialized), "witness_digest": canonical_digest([entry[1] for entry in serialized]), "feature_ranks": feature_ranks(states, record["p"], max_degree)}
    return {"curve_id": record["id"], "family": family["family"], "p": record["p"], "q": record["q"], "source_size": len(sources), "levels": levels, "ops": ops}


def compare(candidate: dict[str, Any], control: dict[str, Any]) -> list[dict[str, Any]]:
    result = []
    for level in ("2", "3"):
        candidate_level, control_level = candidate["levels"][level], control["levels"][level]
        support_ratio = candidate_level["support_size"] / max(1, control_level["support_size"])
        for candidate_degree, control_degree in zip(candidate_level["feature_ranks"], control_level["feature_ranks"]):
            rank_ratio = candidate_degree["rank"] / max(1, control_degree["rank"])
            result.append({"level": int(level), "degree": candidate_degree["degree"], "candidate_rank": candidate_degree["rank"], "control_rank": control_degree["rank"], "rank_ratio": rank_ratio, "candidate_support": candidate_level["support_size"], "control_support": control_level["support_size"], "support_ratio": support_ratio, "signal": level == "3" and support_ratio >= 0.8 and rank_ratio <= 0.8})
    return result


def replay(input_path: Path, families: list[str], max_degree: int) -> dict[str, Any]:
    source = json.loads(input_path.read_text(encoding="utf-8"))
    rows, comparisons, curve_ids = [], [], []
    for instance in source["instances"]:
        record = instance["curve"]
        curve_ids.append(record["id"])
        by_family = {item["family"]: item for item in instance["families"]}
        control = family_state_record(record, by_family["random_x"], max_degree)
        for family_name in families:
            candidate = family_state_record(record, by_family[family_name], max_degree)
            rows.append(candidate); comparisons.extend(compare(candidate, control))
    return {"protocol": "EXP-ECDLP-COORD-EXPANSION-001-nonlinear-s4-quotient-preflight-v1", "claim_status": ["HYPOTHESIS", "TOY-EVIDENCE", "MODEL-BOUND"], "source": {"producer_sha256": sha256_file(PRODUCER_PATH), "input_sha256": sha256_file(input_path)}, "config": {"input_result": str(input_path.resolve()), "families": families, "control_family": "random_x", "levels": [2, 3], "max_degree": max_degree, "feature_space": "affine monomials x^i y^j with i+j<=degree plus an infinity indicator", "witness_policy": "lexicographically first nondecreasing source tuple per exact point state"}, "rows": rows, "comparisons": comparisons, "summary": {"curves": len(curve_ids), "curve_ids": curve_ids, "families": families, "cells": len(rows), "comparison_rows": len(comparisons), "quotient_signal_rows": sum(item["signal"] for item in comparisons), "algorithm_promotion_gate": False, "breakthrough_claim": False, "boundary": "Nonlinear feature-rank preflight with exact source witnesses; no compact S4 selector or ECDLP claim."}, "accounting": {"point_add_calls": sum(row["ops"]["point_add_calls"] for row in rows), "field_inversions": sum(row["ops"]["field_inversions"] for row in rows), "field_multiplications": sum(row["ops"]["field_multiplications"] for row in rows), "state_levels": sum(len(row["levels"]) for row in rows)}}


def normalize(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: normalize(item) for key, item in value.items() if key not in {"peak_rss_bytes", "total_wall_seconds"}}
    if isinstance(value, list):
        return [normalize(item) for item in value]
    return value


def check(raw: dict[str, Any], input_path: Path) -> dict[str, bool]:
    checks = {"protocol": False, "producer_hash": False, "input_hash": False, "feature_space": False, "promotion_false": False, "breakthrough_false": False, "boundary": False}
    try:
        checks.update({"protocol": raw["protocol"] == "EXP-ECDLP-COORD-EXPANSION-001-nonlinear-s4-quotient-preflight-v1", "producer_hash": raw["source"]["producer_sha256"] == sha256_file(PRODUCER_PATH), "input_hash": raw["source"]["input_sha256"] == sha256_file(input_path), "feature_space": "infinity indicator" in raw["config"]["feature_space"], "promotion_false": raw["summary"]["algorithm_promotion_gate"] is False, "breakthrough_false": raw["summary"]["breakthrough_claim"] is False, "boundary": "no compact S4 selector" in raw["summary"]["boundary"]})
    except (KeyError, TypeError, IndexError):
        pass
    return checks


def mutation_rejections(raw: dict[str, Any], input_path: Path, expected: dict[str, Any]) -> dict[str, bool]:
    mutations = {}
    changed = copy.deepcopy(raw); changed["protocol"] = "wrong"; mutations["protocol"] = changed
    changed = copy.deepcopy(raw); changed["source"]["producer_sha256"] = "0" * 64; mutations["producer_hash"] = changed
    changed = copy.deepcopy(raw); changed["rows"][0]["levels"]["3"]["support_size"] += 1; mutations["support_size"] = changed
    changed = copy.deepcopy(raw); changed["comparisons"][0]["signal"] = True; mutations["comparison_signal"] = changed
    changed = copy.deepcopy(raw); changed["summary"]["breakthrough_claim"] = True; mutations["boundary_gate"] = changed
    return {name: not (all(check(candidate, input_path).values()) and normalize(candidate) == normalize(expected)) for name, candidate in mutations.items()}


def verify(raw_path: Path, input_override: Path | None = None) -> dict[str, Any]:
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    input_path = input_override if input_override is not None else Path(raw["config"]["input_result"])
    expected = replay(input_path, raw["config"]["families"], raw["config"]["max_degree"])
    checks = check(raw, input_path)
    checks["normalized_replay_exact"] = normalize(raw) == normalize(expected)
    mutations = mutation_rejections(raw, input_path, expected)
    checks["mutation_rejections"] = all(mutations.values())
    return {"protocol": "EXP-ECDLP-COORD-EXPANSION-001-nonlinear-s4-quotient-preflight-verifier", "raw_result_sha256": sha256_file(raw_path), "input_result_sha256": sha256_file(input_path), "producer_sha256": sha256_file(PRODUCER_PATH), "verifier_sha256": sha256_file(SCRIPT_PATH), "raw_normalized_sha256": canonical_digest(normalize(raw)), "replay_normalized_sha256": canonical_digest(normalize(expected)), "checks": checks, "mutation_rejections_by_name": mutations, "rows_replayed": len(expected["rows"]), "comparisons_replayed": len(expected["comparisons"]), "valid": all(checks.values()), "boundary": "Independent nonlinear-state replay; no compact selector or ECDLP claim."}


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
