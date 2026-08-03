#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
PRODUCER_PATH = SCRIPT_PATH.with_name("target_parametric_norm_operator.py")
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
        result = ((slope * slope - x1 - x2) % self.p, (slope * (x1 - (slope * slope - x1 - x2)) - y1) % self.p)
        ops["field_inversions"] += 1
        ops["field_multiplications"] += 4
        return result


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")).hexdigest()


def as_point(value: list[int] | None) -> Point:
    return None if value is None else (value[0], value[1])


def point_json(value: Point) -> list[int] | None:
    return None if value is None else [value[0], value[1]]


def nonsquare(p: int) -> int:
    for value in range(2, p):
        if pow(value, (p - 1) // 2, p) == p - 1:
            return value
    raise ValueError("no nonsquare")


def exact_rank(flat: list[int], rows: int, width: int, p: int) -> int:
    pivots: dict[int, list[int]] = {}
    rank = 0
    for row_index in range(rows):
        row = [v % p for v in flat[row_index * width:(row_index + 1) * width]]
        while True:
            pivot = next((i for i, value in enumerate(row) if value), None)
            if pivot is None:
                break
            prior = pivots.get(pivot)
            if prior is None:
                inv = pow(row[pivot], -1, p)
                row = [(value * inv) % p for value in row]
                pivots[pivot] = row
                rank += 1
                break
            factor = row[pivot]
            row = [(value - factor * base) % p for value, base in zip(row, prior)]
    return rank


def rank_profile(values: list[int], dimensions: list[int], p: int) -> dict[str, int]:
    profile = {}
    for cut in range(1, len(dimensions)):
        rows = 1
        for size in dimensions[:cut]:
            rows *= size
        width = 1
        for size in dimensions[cut:]:
            width *= size
        profile[str(cut)] = exact_rank(values, rows, width, p)
    return profile


def targets(curve: Curve, record: dict[str, Any], family: dict[str, Any]) -> dict[str, Point]:
    planted = as_point(family["relations"]["target_transcript"][0]["target"])
    held_out = as_point(family["held_out_descent"]["transcript"][0]["target"])
    generator = as_point(record["generator"])
    ops = {"point_add_calls": 0, "field_inversions": 0, "field_multiplications": 0}
    shifted = curve.add(planted, generator, ops)
    if shifted is None:
        raise AssertionError("shifted target became identity")
    return {"planted": planted, "held_out": held_out, "shifted_control": shifted}


def coeff(target: Point, p: int, nu: int) -> list[int]:
    if target is None:
        return [1, 0, 0, 0, 1]
    tx, ty = target
    return [(tx * tx - nu * ty * ty) % p, (-2 * tx) % p, (2 * nu * ty) % p, 1, 1]


def cell(record: dict[str, Any], family: dict[str, Any]) -> dict[str, Any]:
    p, nu = record["p"], nonsquare(record["p"])
    curve = Curve(p, record["a"])
    a_points = [as_point(v) for v in family["progression"]["points"]]
    r_points = [as_point(v) for v in family["factor_base"]["points"]]
    dimensions = [len(a_points), len(r_points), len(r_points), len(r_points), len(r_points)]
    features = [[] for _ in range(5)]
    outputs: list[Point] = []
    ops = {"point_add_calls": 0, "field_inversions": 0, "field_multiplications": 0}
    for a_point in a_points:
        for r0 in r_points:
            for r1 in r_points:
                for r2 in r_points:
                    for r3 in r_points:
                        output: Point = None
                        for source in (a_point, r0, r1, r2, r3):
                            output = curve.add(output, source, ops)
                        if output is None:
                            values = [0, 0, 0, 0, 1]
                        else:
                            x, y = output
                            values = [1, x % p, y % p, (x * x - nu * y * y) % p, 0]
                        outputs.append(output)
                        for i, value in enumerate(values):
                            features[i].append(value)
    target_rows = []
    target_map = targets(curve, record, family)
    for label, target in target_map.items():
        coefficients = coeff(target, p, nu)
        values = [sum(c * v for c, v in zip(coefficients, row)) % p for row in zip(*features)]
        if target is None:
            direct_values = [1] * len(outputs)
        else:
            tx, ty = target
            direct_values = [1 if output is None else ((output[0] - tx) ** 2 - nu * (output[1] - ty) ** 2) % p for output in outputs]
        target_rows.append({"label": label, "target": point_json(target), "coefficients": coefficients, "zero_count": sum(v == 0 for v in values), "h_digest": digest(values), "direct_h_digest": digest(direct_values), "reconstruction_exact": values == direct_values})
    weights = [1, 2, 3]
    weighted_coeff = [sum(weights[i] * target_rows[i]["coefficients"][j] for i in range(3)) % p for j in range(5)]
    weighted = [sum(c * v for c, v in zip(weighted_coeff, row)) % p for row in zip(*features)]
    direct = [sum(weights[i] * (sum(c * v for c, v in zip(target_rows[i]["coefficients"], row)) % p) for i in range(3)) % p for row in zip(*features)]
    return {
        "curve_id": record["id"], "family": family["family"], "p": p, "q": record["q"], "nu": nu,
        "dimensions": dimensions, "total_entries": len(features[0]),
        "features": [{"name": name, "rank": rank_profile(values, dimensions, p), "digest": digest(values)} for name, values in zip(("one", "x", "y", "norm_source", "infinity_indicator"), features)],
        "targets": target_rows,
        "target_coefficient_rank": exact_rank([v for row in [r["coefficients"] for r in target_rows] for v in row], 3, 5, p),
        "weighted_transpose": {"weights": weights, "weighted_coefficients": weighted_coeff, "weighted_digest": digest(weighted), "direct_weighted_digest": digest(direct), "exact": weighted == direct},
        "ops": ops,
    }


def replay(input_path: Path, families: list[str]) -> dict[str, Any]:
    source = json.loads(input_path.read_text(encoding="utf-8"))
    rows, curve_ids = [], []
    for instance in source["instances"]:
        record = instance["curve"]
        curve_ids.append(record["id"])
        by_family = {item["family"]: item for item in instance["families"]}
        for family_name in families:
            rows.append(cell(record, by_family[family_name]))
    return {
        "protocol": "EXP-ECDLP-COORD-EXPANSION-001-target-parametric-norm-operator-v1",
        "claim_status": ["HYPOTHESIS", "TOY-EVIDENCE", "MODEL-BOUND"],
        "source": {"producer_sha256": sha256_file(PRODUCER_PATH), "input_sha256": sha256_file(input_path)},
        "config": {"input_result": str(input_path.resolve()), "families": families, "target_batch": ["planted", "held_out", "shifted_control"], "features": ["one", "x", "y", "norm_source", "infinity_indicator"], "rank_field": "exact modular Gaussian elimination over F_p"},
        "rows": rows,
        "summary": {"curves": len(curve_ids), "curve_ids": curve_ids, "families": families, "cells": len(rows), "all_reconstructions_exact": all(target["reconstruction_exact"] for row in rows for target in row["targets"]), "all_transpose_checks_exact": all(row["weighted_transpose"]["exact"] for row in rows), "algorithm_promotion_gate": False, "breakthrough_claim": False, "boundary": "Target-parametric linearization is an exact batch identity, not a zero finder or ECDLP algorithm."},
        "accounting": {"point_add_calls": sum(row["ops"]["point_add_calls"] for row in rows), "field_inversions": sum(row["ops"]["field_inversions"] for row in rows), "field_multiplications": sum(row["ops"]["field_multiplications"] for row in rows), "tensor_entries": sum(row["total_entries"] for row in rows), "target_specializations": sum(len(row["targets"]) for row in rows)},
    }


def normalize(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: normalize(item) for key, item in value.items() if key not in {"peak_rss_bytes", "total_wall_seconds"}}
    if isinstance(value, list):
        return [normalize(item) for item in value]
    return value


def check(raw: dict[str, Any], input_path: Path) -> dict[str, bool]:
    checks = {
        "protocol": False,
        "producer_hash": False,
        "input_hash": False,
        "rank_field": False,
        "transpose_flag": False,
        "reconstruction_flag": False,
        "promotion_false": False,
        "breakthrough_false": False,
        "boundary": False,
        "all_rows_exact": False,
    }
    try:
        checks.update({
            "protocol": raw["protocol"] == "EXP-ECDLP-COORD-EXPANSION-001-target-parametric-norm-operator-v1",
            "producer_hash": raw["source"]["producer_sha256"] == sha256_file(PRODUCER_PATH),
            "input_hash": raw["source"]["input_sha256"] == sha256_file(input_path),
            "rank_field": raw["config"]["rank_field"] == "exact modular Gaussian elimination over F_p",
            "transpose_flag": raw["summary"]["all_transpose_checks_exact"] is True,
            "reconstruction_flag": raw["summary"]["all_reconstructions_exact"] is True,
            "promotion_false": raw["summary"]["algorithm_promotion_gate"] is False,
            "breakthrough_false": raw["summary"]["breakthrough_claim"] is False,
            "boundary": "not a zero finder" in raw["summary"]["boundary"],
            "all_rows_exact": all(row["weighted_transpose"]["exact"] for row in raw["rows"]),
            "all_reconstruction_rows_exact": all(
                target["reconstruction_exact"]
                for row in raw["rows"]
                for target in row["targets"]
            ),
        })
        return checks
    except (KeyError, TypeError, IndexError):
        return checks


def mutation_rejections(raw: dict[str, Any], input_path: Path, expected: dict[str, Any]) -> dict[str, bool]:
    mutations = {}
    changed = copy.deepcopy(raw); changed["protocol"] = "wrong"; mutations["protocol"] = changed
    changed = copy.deepcopy(raw); changed["source"]["producer_sha256"] = "0" * 64; mutations["producer_hash"] = changed
    changed = copy.deepcopy(raw); changed["rows"][0]["weighted_transpose"]["exact"] = False; mutations["transpose_row"] = changed
    changed = copy.deepcopy(raw); changed["summary"]["breakthrough_claim"] = True; mutations["boundary_gate"] = changed
    changed = copy.deepcopy(raw); changed["rows"][0]["features"][0]["rank"]["2"] += 1; mutations["rank_row"] = changed
    return {name: not (all(check(candidate, input_path).values()) and normalize(candidate) == normalize(expected)) for name, candidate in mutations.items()}


def verify(raw_path: Path, input_override: Path | None = None) -> dict[str, Any]:
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    input_path = input_override if input_override is not None else Path(raw["config"]["input_result"])
    expected = replay(input_path, raw["config"]["families"])
    checks = check(raw, input_path)
    checks["normalized_replay_exact"] = normalize(raw) == normalize(expected)
    mutations = mutation_rejections(raw, input_path, expected)
    checks["mutation_rejections"] = all(mutations.values())
    return {"protocol": "EXP-ECDLP-COORD-EXPANSION-001-target-parametric-norm-operator-verifier", "raw_result_sha256": sha256_file(raw_path), "input_result_sha256": sha256_file(input_path), "producer_sha256": sha256_file(PRODUCER_PATH), "verifier_sha256": sha256_file(SCRIPT_PATH), "raw_normalized_sha256": digest(normalize(raw)), "replay_normalized_sha256": digest(normalize(expected)), "checks": checks, "mutation_rejections_by_name": mutations, "rows_replayed": len(expected["rows"]), "valid": all(checks.values()), "boundary": "Independent batch-linearization replay; no solver, index, or ECDLP claim."}


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
