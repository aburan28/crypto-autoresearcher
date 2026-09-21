#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
PRODUCER_PATH = SCRIPT_PATH.with_name("tt_zero_locator_rank_census.py")

Point = tuple[int, int] | None


class AffineCurve:
    def __init__(self, p: int, a: int, b: int) -> None:
        self.p = p
        self.a = a % p
        self.b = b % p

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
            numerator = (3 * x1 * x1 + self.a) % self.p
            denominator = (2 * y1) % self.p
        else:
            numerator = (y2 - y1) % self.p
            denominator = (x2 - x1) % self.p
        slope = numerator * pow(denominator, -1, self.p) % self.p
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


def canonical_digest(value: Any) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def point(value: list[int] | None) -> Point:
    return None if value is None else (value[0], value[1])


def point_json(value: Point) -> list[int] | None:
    return None if value is None else [value[0], value[1]]


def nonsquare(p: int) -> int:
    for value in range(2, p):
        if pow(value, (p - 1) // 2, p) == p - 1:
            return value
    raise ValueError("no nonsquare")


def exact_rank(rows: list[int], row_count: int, width: int, p: int) -> int:
    pivots: dict[int, list[int]] = {}
    rank = 0
    for row_index in range(row_count):
        row = [value % p for value in rows[row_index * width:(row_index + 1) * width]]
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
            row = [
                (value - factor * base) % p
                for value, base in zip(row, prior)
            ]
    return rank


def rank_profile(values: list[int], dimensions: list[int], p: int) -> dict[str, int]:
    profile: dict[str, int] = {}
    for cut in range(1, len(dimensions)):
        row_count = 1
        for size in dimensions[:cut]:
            row_count *= size
        width = 1
        for size in dimensions[cut:]:
            width *= size
        profile[str(cut)] = exact_rank(values, row_count, width, p)
    return profile


def support_matched_random(length: int, support: int, label: str) -> list[int]:
    keyed = [
        (hashlib.sha256(f"{label}|{index}".encode("ascii")).digest(), index)
        for index in range(length)
    ]
    selected = {index for _, index in sorted(keyed)[:support]}
    return [int(index in selected) for index in range(length)]


def target_choices(
    curve: AffineCurve, curve_record: dict[str, Any], family: dict[str, Any]
) -> dict[str, Point]:
    planted = point(family["relations"]["target_transcript"][0]["target"])
    held_out = point(family["held_out_descent"]["transcript"][0]["target"])
    generator = point(curve_record["generator"])
    ops = {"point_add_calls": 0, "field_inversions": 0, "field_multiplications": 0}
    shifted = curve.add(planted, generator, ops)
    if shifted is None:
        raise AssertionError("shifted control target became identity")
    return {"planted": planted, "held_out": held_out, "shifted_control": shifted}


def census_cell(
    curve_record: dict[str, Any], family: dict[str, Any], label: str, target: Point
) -> dict[str, Any]:
    p = curve_record["p"]
    curve = AffineCurve(p, curve_record["a"], curve_record["b"])
    a_points = [point(value) for value in family["progression"]["points"]]
    r_points = [point(value) for value in family["factor_base"]["points"]]
    dimensions = [len(a_points), len(r_points), len(r_points), len(r_points), len(r_points)]
    total = 1
    for size in dimensions:
        total *= size
    nu = nonsquare(p)
    ops = {"point_add_calls": 0, "field_inversions": 0, "field_multiplications": 0}
    h_values: list[int] = []
    tx, ty = target if target is not None else (None, None)
    if tx is None or ty is None:
        raise AssertionError("finite target required")
    for a_point in a_points:
        for r0 in r_points:
            for r1 in r_points:
                for r2 in r_points:
                    for r3 in r_points:
                        output: Point = None
                        for source in (a_point, r0, r1, r2, r3):
                            output = curve.add(output, source, ops)
                        if output is None:
                            h_values.append(1)
                            continue
                        x, y = output
                        dx = (x - tx) % p
                        dy = (y - ty) % p
                        h_values.append((dx * dx - nu * dy * dy) % p)
    stages = {"h": h_values}
    stages["h2"] = [value * value % p for value in h_values]
    stages["h4"] = [value * value % p for value in stages["h2"]]
    stages["h8"] = [value * value % p for value in stages["h4"]]
    stages["indicator"] = [int(value == 0) for value in h_values]
    stage_rows: dict[str, Any] = {}
    for name, values in stages.items():
        stage_rows[name] = {
            "ranks": rank_profile(values, dimensions, p),
            "support": sum(value != 0 for value in values),
            "zero_count": sum(value == 0 for value in values),
            "digest": canonical_digest(values),
        }
    support = stage_rows["indicator"]["zero_count"]
    random_indicator = support_matched_random(
        total, support, f"{curve_record['id']}|{family['family']}|{label}"
    )
    return {
        "curve_id": curve_record["id"],
        "family": family["family"],
        "target_label": label,
        "target": point_json(target),
        "p": p,
        "q": curve_record["q"],
        "dimensions": dimensions,
        "nu": nu,
        "total_entries": total,
        "stages": stage_rows,
        "matched_random_indicator": {
            "ranks": rank_profile(random_indicator, dimensions, p),
            "support": support,
            "digest": canonical_digest(random_indicator),
        },
        "ops": ops,
    }


def replay(input_path: Path, families: list[str]) -> dict[str, Any]:
    source = json.loads(input_path.read_text(encoding="utf-8"))
    rows = []
    curve_ids = []
    for instance in source["instances"]:
        curve_record = instance["curve"]
        curve_ids.append(curve_record["id"])
        curve = AffineCurve(curve_record["p"], curve_record["a"], curve_record["b"])
        by_family = {record["family"]: record for record in instance["families"]}
        for family_name in families:
            family = by_family[family_name]
            for label, target in target_choices(curve, curve_record, family).items():
                rows.append(census_cell(curve_record, family, label, target))
    p = source["instances"][0]["curve"]["p"]
    control_dimensions = [2, 3, 3, 2, 2]
    control_total = 2 * 3 * 3 * 2 * 2
    rank_one = [1] * control_total
    rank_two = [((index // 2) + (index // 4)) % p for index in range(control_total)]
    return {
        "protocol": "EXP-ECDLP-COORD-EXPANSION-001-tt-zero-locator-rank-census-v1",
        "claim_status": ["HYPOTHESIS", "TOY-EVIDENCE", "MODEL-BOUND"],
        "source": {
            "producer_sha256": sha256_file(PRODUCER_PATH),
            "input_sha256": sha256_file(input_path),
        },
        "config": {
            "input_result": str(input_path.resolve()),
            "families": families,
            "targets": ["planted", "held_out", "shifted_control"],
            "stages": ["h", "h2", "h4", "h8", "indicator"],
            "rank_field": "exact modular Gaussian elimination over F_p",
        },
        "controls": {
            "rank_one": {"ranks": rank_profile(rank_one, control_dimensions, p)},
            "rank_two_candidate": {
                "ranks": rank_profile(rank_two, control_dimensions, p)
            },
            "pass": rank_profile(rank_one, control_dimensions, p)["2"] == 1
            and rank_profile(rank_one, control_dimensions, p)["3"] == 1,
        },
        "rows": rows,
        "summary": {
            "curves": len(curve_ids),
            "curve_ids": curve_ids,
            "families": families,
            "cells": len(rows),
            "central_rank_signal_rows": sum(
                row["stages"]["h8"]["ranks"]["2"]
                < min(row["dimensions"][0] * row["dimensions"][1], row["dimensions"][2] * row["dimensions"][3] * row["dimensions"][4])
                for row in rows
            ),
            "algorithm_promotion_gate": False,
            "breakthrough_claim": False,
            "boundary": (
                "Exact finite-field TT rank census. Low final indicator rank "
                "is sparse support evidence, not a compact locator or ECDLP route."
            ),
        },
        "accounting": {
            "point_add_calls": sum(row["ops"]["point_add_calls"] for row in rows),
            "field_inversions": sum(row["ops"]["field_inversions"] for row in rows),
            "field_multiplications": sum(row["ops"]["field_multiplications"] for row in rows),
            "tensor_entries": sum(row["total_entries"] for row in rows),
        },
    }


def normalize(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: normalize(item)
            for key, item in value.items()
            if key not in {"peak_rss_bytes", "total_wall_seconds"}
        }
    if isinstance(value, list):
        return [normalize(item) for item in value]
    return value


def check_result(raw: dict[str, Any], input_path: Path) -> dict[str, bool]:
    rows = raw.get("rows", [])
    try:
        shape_valid = all(
            len(row["dimensions"]) == 5
            and row["total_entries"] == __import__("functools").reduce(
                lambda left, right: left * right, row["dimensions"], 1
            )
            for row in rows
        )
        controls_valid = (
            raw["controls"]["pass"] is True
            and all(value == 1 for value in raw["controls"]["rank_one"]["ranks"].values())
        )
        summary_valid = (
            raw["summary"]["algorithm_promotion_gate"] is False
            and raw["summary"]["breakthrough_claim"] is False
            and raw["summary"]["cells"] == len(rows)
        )
    except (KeyError, TypeError, ValueError):
        shape_valid = controls_valid = summary_valid = False
    return {
        "protocol": raw.get("protocol")
        == "EXP-ECDLP-COORD-EXPANSION-001-tt-zero-locator-rank-census-v1",
        "producer_hash": raw.get("source", {}).get("producer_sha256")
        == sha256_file(PRODUCER_PATH),
        "input_hash": raw.get("source", {}).get("input_sha256")
        == sha256_file(input_path),
        "rank_field": raw.get("config", {}).get("rank_field")
        == "exact modular Gaussian elimination over F_p",
        "shape_valid": shape_valid,
        "controls_valid": controls_valid,
        "summary_valid": summary_valid,
        "boundary_present": "not a compact locator" in raw.get("summary", {}).get("boundary", ""),
    }


def mutation_rejections(
    raw: dict[str, Any], input_path: Path, expected: dict[str, Any]
) -> dict[str, bool]:
    mutations: dict[str, dict[str, Any]] = {}
    changed = copy.deepcopy(raw)
    changed["protocol"] = "wrong"
    mutations["protocol"] = changed
    changed = copy.deepcopy(raw)
    changed["source"]["producer_sha256"] = "0" * 64
    mutations["producer_hash"] = changed
    changed = copy.deepcopy(raw)
    changed["rows"][0]["stages"]["h"]["ranks"]["2"] += 1
    mutations["rank_cell"] = changed
    changed = copy.deepcopy(raw)
    changed["summary"]["breakthrough_claim"] = True
    mutations["boundary_gate"] = changed
    changed = copy.deepcopy(raw)
    changed["controls"]["pass"] = False
    mutations["control_flag"] = changed
    return {
        name: not (
            all(check_result(candidate, input_path).values())
            and normalize(candidate) == normalize(expected)
        )
        for name, candidate in mutations.items()
    }


def verify(raw_path: Path, input_override: Path | None = None) -> dict[str, Any]:
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    input_path = input_override if input_override is not None else Path(raw["config"]["input_result"])
    rerun = replay(input_path, raw["config"]["families"])
    checks = check_result(raw, input_path)
    checks["normalized_replay_exact"] = normalize(raw) == normalize(rerun)
    mutation_results = mutation_rejections(raw, input_path, rerun)
    checks["mutation_rejections"] = all(mutation_results.values())
    return {
        "protocol": "EXP-ECDLP-COORD-EXPANSION-001-tt-zero-locator-rank-census-verifier",
        "raw_result_sha256": sha256_file(raw_path),
        "input_result_sha256": sha256_file(input_path),
        "producer_sha256": sha256_file(PRODUCER_PATH),
        "verifier_sha256": sha256_file(SCRIPT_PATH),
        "raw_normalized_sha256": canonical_digest(normalize(raw)),
        "replay_normalized_sha256": canonical_digest(normalize(rerun)),
        "checks": checks,
        "mutation_rejections_by_name": mutation_results,
        "rows_replayed": len(rerun["rows"]),
        "valid": all(checks.values()),
        "boundary": "Independent finite-field rank replay; no solver or ECDLP claim.",
    }


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
