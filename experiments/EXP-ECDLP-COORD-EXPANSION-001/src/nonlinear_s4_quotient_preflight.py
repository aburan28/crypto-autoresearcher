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


def canonical_digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")
    ).hexdigest()


def rss_bytes() -> int:
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(value if platform.system() == "Darwin" else value * 1024)


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


def state_level(
    curve: AffineCurve,
    sources: list[Point],
    level: int,
    ops: dict[str, int],
) -> dict[Point, tuple[int, ...]]:
    states: dict[Point, tuple[int, ...]] = {}
    for witness in itertools.combinations_with_replacement(range(len(sources)), level):
        total: Point = None
        for index in witness:
            total = curve.add(total, sources[index], ops)
        states.setdefault(total, witness)
    return states


def serialized_states(states: dict[Point, tuple[int, ...]]) -> list[list[Any]]:
    return [
        [point_json(point), list(witness)]
        for point, witness in sorted(states.items(), key=lambda item: point_key(item[0]))
    ]


def feature_rank_curve(states: dict[Point, tuple[int, ...]], p: int, max_degree: int) -> list[dict[str, Any]]:
    points = sorted(states, key=point_key)
    result = []
    for degree in range(max_degree + 1):
        terms = [(i, total - i) for total in range(degree + 1) for i in range(total + 1)]
        rows: list[int] = []
        for value in points:
            if value is None:
                rows.extend([0] * len(terms))
                rows.append(1)
                continue
            x, y = value
            rows.extend(pow(x, i, p) * pow(y, j, p) % p for i, j in terms)
            rows.append(0)
        width = len(terms) + 1
        result.append({
            "degree": degree,
            "basis_terms": len(terms),
            "columns": width,
            "rank": exact_rank(rows, len(points), width, p) if points else 0,
            "support": len(points),
            "identity_present": None in states,
        })
    return result


def family_state_record(
    record: dict[str, Any], family: dict[str, Any], max_degree: int
) -> dict[str, Any]:
    curve = AffineCurve(record["p"], record["a"], record["b"])
    sources = [as_point(value) for value in family["factor_base"]["points"]]
    ops = {"point_add_calls": 0, "field_inversions": 0, "field_multiplications": 0}
    levels = {}
    for level in (2, 3):
        states = state_level(curve, sources, level, ops)
        serialized = serialized_states(states)
        levels[str(level)] = {
            "attempted_tuples": len(list(itertools.combinations_with_replacement(range(len(sources)), level))),
            "support_size": len(states),
            "identity_present": None in states,
            "state_digest": canonical_digest(serialized),
            "witness_digest": canonical_digest([entry[1] for entry in serialized]),
            "feature_ranks": feature_rank_curve(states, record["p"], max_degree),
        }
    return {
        "curve_id": record["id"],
        "family": family["family"],
        "p": record["p"],
        "q": record["q"],
        "source_size": len(sources),
        "levels": levels,
        "ops": ops,
    }


def compare(candidate: dict[str, Any], control: dict[str, Any]) -> list[dict[str, Any]]:
    comparisons = []
    for level in ("2", "3"):
        candidate_level = candidate["levels"][level]
        control_level = control["levels"][level]
        support_ratio = candidate_level["support_size"] / max(1, control_level["support_size"])
        for candidate_degree, control_degree in zip(
            candidate_level["feature_ranks"], control_level["feature_ranks"]
        ):
            rank_ratio = candidate_degree["rank"] / max(1, control_degree["rank"])
            comparisons.append({
                "level": int(level),
                "degree": candidate_degree["degree"],
                "candidate_rank": candidate_degree["rank"],
                "control_rank": control_degree["rank"],
                "rank_ratio": rank_ratio,
                "candidate_support": candidate_level["support_size"],
                "control_support": control_level["support_size"],
                "support_ratio": support_ratio,
                "signal": level == "3" and support_ratio >= 0.8 and rank_ratio <= 0.8,
            })
    return comparisons


def run(input_path: Path, families: list[str], max_degree: int) -> dict[str, Any]:
    started = time.perf_counter()
    source = json.loads(input_path.read_text(encoding="utf-8"))
    rows = []
    comparisons = []
    curve_ids = []
    for instance in source["instances"]:
        record = instance["curve"]
        curve_ids.append(record["id"])
        by_family = {item["family"]: item for item in instance["families"]}
        control = family_state_record(record, by_family["random_x"], max_degree)
        for family_name in families:
            candidate = family_state_record(record, by_family[family_name], max_degree)
            rows.append(candidate)
            comparisons.extend(compare(candidate, control))
    return {
        "protocol": "EXP-ECDLP-COORD-EXPANSION-001-nonlinear-s4-quotient-preflight-v1",
        "claim_status": ["HYPOTHESIS", "TOY-EVIDENCE", "MODEL-BOUND"],
        "source": {"producer_sha256": sha256_file(SCRIPT_PATH), "input_sha256": sha256_file(input_path)},
        "config": {
            "input_result": str(input_path.resolve()),
            "families": families,
            "control_family": "random_x",
            "levels": [2, 3],
            "max_degree": max_degree,
            "feature_space": "affine monomials x^i y^j with i+j<=degree plus an infinity indicator",
            "witness_policy": "lexicographically first nondecreasing source tuple per exact point state",
        },
        "rows": rows,
        "comparisons": comparisons,
        "summary": {
            "curves": len(curve_ids),
            "curve_ids": curve_ids,
            "families": families,
            "cells": len(rows),
            "comparison_rows": len(comparisons),
            "quotient_signal_rows": sum(item["signal"] for item in comparisons),
            "algorithm_promotion_gate": False,
            "breakthrough_claim": False,
            "boundary": "Nonlinear feature-rank preflight with exact source witnesses; no compact S4 selector or ECDLP claim.",
        },
        "accounting": {
            "point_add_calls": sum(row["ops"]["point_add_calls"] for row in rows),
            "field_inversions": sum(row["ops"]["field_inversions"] for row in rows),
            "field_multiplications": sum(row["ops"]["field_multiplications"] for row in rows),
            "state_levels": sum(len(row["levels"]) for row in rows),
        },
        "peak_rss_bytes": rss_bytes(),
        "total_wall_seconds": time.perf_counter() - started,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--families", nargs="+", required=True)
    parser.add_argument("--max-degree", type=int, default=8)
    args = parser.parse_args()
    print(json.dumps(run(args.input, args.families, args.max_degree), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
