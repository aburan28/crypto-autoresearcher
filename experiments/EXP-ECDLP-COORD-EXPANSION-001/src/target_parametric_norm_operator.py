#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
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
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")).hexdigest()


def rss_bytes() -> int:
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(value if platform.system() == "Darwin" else value * 1024)


def point(value: list[int] | None) -> Point:
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
    result: dict[str, int] = {}
    for cut in range(1, len(dimensions)):
        rows = 1
        for size in dimensions[:cut]:
            rows *= size
        width = 1
        for size in dimensions[cut:]:
            width *= size
        result[str(cut)] = exact_rank(values, rows, width, p)
    return result


def target_choices(curve: AffineCurve, record: dict[str, Any], family: dict[str, Any]) -> dict[str, Point]:
    planted = point(family["relations"]["target_transcript"][0]["target"])
    held_out = point(family["held_out_descent"]["transcript"][0]["target"])
    generator = point(record["generator"])
    ops = {"point_add_calls": 0, "field_inversions": 0, "field_multiplications": 0}
    shifted = curve.add(planted, generator, ops)
    if shifted is None:
        raise AssertionError("shifted target became identity")
    return {"planted": planted, "held_out": held_out, "shifted_control": shifted}


def coefficients(target: Point, p: int, nu: int) -> list[int]:
    if target is None:
        return [1, 0, 0, 0, 1]
    tx, ty = target
    return [(tx * tx - nu * ty * ty) % p, (-2 * tx) % p, (2 * nu * ty) % p, 1, 1]


def feature_cell(record: dict[str, Any], family: dict[str, Any]) -> dict[str, Any]:
    p = record["p"]
    nu = nonsquare(p)
    curve = AffineCurve(p, record["a"], record["b"])
    a_points = [point(v) for v in family["progression"]["points"]]
    r_points = [point(v) for v in family["factor_base"]["points"]]
    dimensions = [len(a_points), len(r_points), len(r_points), len(r_points), len(r_points)]
    total = 1
    for size in dimensions:
        total *= size
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
                        for index, value in enumerate(values):
                            features[index].append(value)
    target_map = target_choices(curve, record, family)
    target_rows = []
    for label, target in target_map.items():
        coeff = coefficients(target, p, nu)
        h_values = [sum(c * v for c, v in zip(coeff, row)) % p for row in zip(*features)]
        if target is None:
            direct_values = [1] * len(outputs)
        else:
            tx, ty = target
            direct_values = [
                1 if output is None else ((output[0] - tx) ** 2 - nu * (output[1] - ty) ** 2) % p
                for output in outputs
            ]
        target_rows.append({
            "label": label,
            "target": point_json(target),
            "coefficients": coeff,
            "zero_count": sum(value == 0 for value in h_values),
            "h_digest": digest(h_values),
            "direct_h_digest": digest(direct_values),
            "reconstruction_exact": h_values == direct_values,
        })
    weights = [1, 2, 3]
    weighted_coeff = [sum(weights[i] * target_rows[i]["coefficients"][j] for i in range(3)) % p for j in range(5)]
    weighted_h = [sum(c * v for c, v in zip(weighted_coeff, row)) % p for row in zip(*features)]
    direct_weighted = [
        sum(weights[i] * (sum(c * v for c, v in zip(target_rows[i]["coefficients"], row)) % p) for i in range(3)) % p
        for row in zip(*features)
    ]
    return {
        "curve_id": record["id"],
        "family": family["family"],
        "p": p,
        "q": record["q"],
        "nu": nu,
        "dimensions": dimensions,
        "total_entries": total,
        "features": [
            {"name": name, "rank": rank_profile(values, dimensions, p), "digest": digest(values)}
            for name, values in zip(("one", "x", "y", "norm_source", "infinity_indicator"), features)
        ],
        "targets": target_rows,
        "target_coefficient_rank": exact_rank([v for row in [r["coefficients"] for r in target_rows] for v in row], 3, 5, p),
        "weighted_transpose": {
            "weights": weights,
            "weighted_coefficients": weighted_coeff,
            "weighted_digest": digest(weighted_h),
            "direct_weighted_digest": digest(direct_weighted),
            "exact": weighted_h == direct_weighted,
        },
        "ops": ops,
    }


def run(input_path: Path, families: list[str]) -> dict[str, Any]:
    started = time.perf_counter()
    source = json.loads(input_path.read_text(encoding="utf-8"))
    rows = []
    curve_ids = []
    for instance in source["instances"]:
        record = instance["curve"]
        curve_ids.append(record["id"])
        by_family = {item["family"]: item for item in instance["families"]}
        for family_name in families:
            rows.append(feature_cell(record, by_family[family_name]))
    return {
        "protocol": "EXP-ECDLP-COORD-EXPANSION-001-target-parametric-norm-operator-v1",
        "claim_status": ["HYPOTHESIS", "TOY-EVIDENCE", "MODEL-BOUND"],
        "source": {"producer_sha256": sha256_file(SCRIPT_PATH), "input_sha256": sha256_file(input_path)},
        "config": {
            "input_result": str(input_path.resolve()),
            "families": families,
            "target_batch": ["planted", "held_out", "shifted_control"],
            "features": ["one", "x", "y", "norm_source", "infinity_indicator"],
            "rank_field": "exact modular Gaussian elimination over F_p",
        },
        "rows": rows,
        "summary": {
            "curves": len(curve_ids),
            "curve_ids": curve_ids,
            "families": families,
            "cells": len(rows),
            "all_reconstructions_exact": all(
                target["reconstruction_exact"]
                for row in rows
                for target in row["targets"]
            ),
            "all_transpose_checks_exact": all(row["weighted_transpose"]["exact"] for row in rows),
            "algorithm_promotion_gate": False,
            "breakthrough_claim": False,
            "boundary": "Target-parametric linearization is an exact batch identity, not a zero finder or ECDLP algorithm.",
        },
        "accounting": {
            "point_add_calls": sum(row["ops"]["point_add_calls"] for row in rows),
            "field_inversions": sum(row["ops"]["field_inversions"] for row in rows),
            "field_multiplications": sum(row["ops"]["field_multiplications"] for row in rows),
            "tensor_entries": sum(row["total_entries"] for row in rows),
            "target_specializations": sum(len(row["targets"]) for row in rows),
        },
        "peak_rss_bytes": rss_bytes(),
        "total_wall_seconds": time.perf_counter() - started,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--families", nargs="+", required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.input, args.families), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
