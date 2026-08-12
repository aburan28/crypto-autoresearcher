#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
from collections import Counter
from pathlib import Path
from typing import Any


Point = tuple[int, int] | None
SCRIPT_PATH = Path(__file__).resolve()
EXPERIMENT_SOURCE = SCRIPT_PATH.with_name("coordinate_expansion.py")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_hash(value: Any) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def is_prime(value: int) -> bool:
    if value < 2:
        return False
    for prime in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if value % prime == 0:
            return value == prime
    d = value - 1
    s = 0
    while d % 2 == 0:
        s += 1
        d //= 2
    for base in (2, 325, 9375, 28178, 450775, 9780504, 1795265022):
        if base % value == 0:
            continue
        x = pow(base, d, value)
        if x in (1, value - 1):
            continue
        for _ in range(s - 1):
            x = x * x % value
            if x == value - 1:
                break
        else:
            return False
    return True


class Curve:
    def __init__(self, p: int, a: int, b: int) -> None:
        self.p = p
        self.a = a % p
        self.b = b % p

    def neg(self, point: Point) -> Point:
        return None if point is None else (point[0], (-point[1]) % self.p)

    def on_curve(self, point: Point) -> bool:
        if point is None:
            return True
        x, y = point
        return (
            y * y - (x * x * x + self.a * x + self.b)
        ) % self.p == 0

    def add(self, left: Point, right: Point) -> Point:
        if left is None:
            return right
        if right is None:
            return left
        x1, y1 = left
        x2, y2 = right
        if x1 == x2 and (y1 + y2) % self.p == 0:
            return None
        if left == right:
            slope = (
                (3 * x1 * x1 + self.a)
                * pow(2 * y1, -1, self.p)
                % self.p
            )
        else:
            slope = (
                (y2 - y1)
                * pow((x2 - x1) % self.p, -1, self.p)
                % self.p
            )
        x3 = (slope * slope - x1 - x2) % self.p
        return x3, (slope * (x1 - x3) - y1) % self.p

    def mul(self, scalar: int, point: Point) -> Point:
        result = None
        addend = point
        while scalar:
            if scalar & 1:
                result = self.add(result, addend)
            scalar >>= 1
            if scalar:
                addend = self.add(addend, addend)
        return result


def curve_order(curve: Curve) -> int:
    total = 1
    exponent = (curve.p - 1) // 2
    for x in range(curve.p):
        rhs = (x * x * x + curve.a * x + curve.b) % curve.p
        if rhs == 0:
            total += 1
        elif pow(rhs, exponent, curve.p) == 1:
            total += 2
    return total


def as_point(value: list[int] | None) -> Point:
    return None if value is None else (value[0], value[1])


def close(left: float, right: float) -> bool:
    return math.isclose(left, right, rel_tol=1e-12, abs_tol=1e-12)


def support_chain(scalars: list[int], q: int) -> list[set[int]]:
    levels = [{0}]
    for _ in range(5):
        levels.append(
            {
                (partial + scalar) % q
                for partial in levels[-1]
                for scalar in scalars
            }
        )
    return levels


def split_statistics(
    d2: set[int], d3: set[int], d5: set[int], q: int
) -> dict[str, float | int]:
    hits = Counter((left + right) % q for left in d2 for right in d3)
    if set(hits) != d5:
        raise AssertionError("independent D2+D3 support mismatch")

    def t_perm(scan_size: int) -> float:
        return statistics.fmean(
            (scan_size + 1) / (hits[target] + 1)
            if target in hits
            else float(scan_size)
            for target in range(1, q)
        )

    t2 = t_perm(len(d2))
    t3 = t_perm(len(d3))
    support_mass = len(d2) + len(d3)
    return {
        "split_redundancy": len(d2) * len(d3) / len(d5),
        "split_hit_mean_on_support": statistics.fmean(hits.values()),
        "split_hit_maximum": max(hits.values()),
        "t_perm_store_d3_scan_d2": t2,
        "t_perm_store_d2_scan_d3": t3,
        "phi_store_d3_scan_d2": support_mass * t2**2 / len(d5),
        "phi_store_d2_scan_d3": support_mass * t3**2 / len(d5),
    }


def verify_record(
    record: dict[str, Any],
    curve: Curve,
    q: int,
    point_to_scalar: dict[Point, int],
    target_points: list[Point],
) -> None:
    factor_base = record["factor_base"]
    digest = canonical_hash(factor_base)
    assert digest == record["factor_base_digest_before_audit"]
    assert digest == record["factor_base_digest_after_audit"]
    points = [as_point(value) for value in factor_base["points"]]
    assert len(points) == factor_base["size"] == len(set(points))
    assert all(curve.on_curve(point) and point is not None for point in points)
    if record["symmetry_mode"] == "sign_complete":
        assert len(points) % 2 == 0
        assert all(
            points[index + 1] == curve.neg(points[index])
            for index in range(0, len(points), 2)
        )
    scalars = [point_to_scalar[point] for point in points]
    assert scalars == record["factor_base_scalars_diagnostic"]
    levels = support_chain(scalars, q)
    profiles = record["audit"]["profiles"]
    assert len(profiles) == 5
    for depth, profile in enumerate(profiles, 1):
        assert profile["support_size"] == len(levels[depth])
        assert (
            record["audit"]["audit_point_build_profiles"][depth - 1][
                "support_size"
            ]
            == len(levels[depth])
        )
    d1, d2, d3, d5 = (
        levels[1],
        levels[2],
        levels[3],
        levels[5],
    )
    d5_new = d5 - d1 - d3
    assert record["compiler"]["d2_entries"] == len(d2)
    assert record["compiler"]["d3_entries"] == len(d3)
    assert record["audit"]["d5_nonidentity_size"] == len(d5 - {0})
    assert record["audit"]["d5_new_size"] == len(d5_new)
    assert close(
        record["audit"]["epsilon_nonidentity"],
        len(d5 - {0}) / (q - 1),
    )
    split = split_statistics(d2, d3, d5, q)
    for key, expected in split.items():
        actual = record["audit"][key]
        assert actual == expected if isinstance(expected, int) else close(
            actual, expected
        )
    assert (
        record["query"]["api_boundary"]
        == "TARGET_POINTS_AND_POINT_ADVICE_ONLY"
    )
    sampled_successes = sum(
        point_to_scalar[target] in d5 for target in target_points
    )
    for order in record["query"]["scan_orders"].values():
        assert order["target_count"] == len(target_points)
        assert order["successful_targets"] == sampled_successes
        assert 1 <= order["probes_per_target_mean"] <= len(d2)
    witness = record["query"]["first_witness"]
    if witness is not None:
        recovered = None
        for index in witness["factor_base_indices"]:
            recovered = curve.add(recovered, points[index])
        assert recovered == target_points[witness["target_index"]]


METRICS = {
    "d2": lambda record: record["compiler"]["d2_entries"],
    "d3": lambda record: record["compiler"]["d3_entries"],
    "d5_nonidentity": lambda record: record["audit"][
        "d5_nonidentity_size"
    ],
    "d5_new": lambda record: record["audit"]["d5_new_size"],
    "t_perm": lambda record: record["audit"][
        "t_perm_store_d3_scan_d2"
    ],
    "phi": lambda record: record["audit"]["phi_store_d3_scan_d2"],
    "persistent_bytes": lambda record: record["compiler"][
        "persistent_json_bytes"
    ],
}


def verify_statistics(records: list[dict[str, Any]]) -> None:
    for symmetry in ("sign_canonical", "sign_complete"):
        group = [
            record
            for record in records
            if record["symmetry_mode"] == symmetry
        ]
        null_groups = {
            family: [
                record for record in group if record["family"] == family
            ]
            for family in ("random_x", "source_prf_x", "random")
        }
        assert all(len(nulls) == 31 for nulls in null_groups.values())
        medians = {
            family: {
                name: statistics.median(getter(record) for record in nulls)
                for name, getter in METRICS.items()
            }
            for family, nulls in null_groups.items()
        }
        coordinate_nulls = null_groups["random_x"] + null_groups[
            "source_prf_x"
        ]
        for record in group:
            assert record["null_medians"] == medians
            for family in medians:
                for name, getter in METRICS.items():
                    expected = getter(record) / max(
                        medians[family][name], 1e-300
                    )
                    assert close(
                        record["ratios_to_null_medians"][family][name],
                        expected,
                    )
            dominated = sum(
                null["audit"]["d5_nonidentity_size"]
                >= record["audit"]["d5_nonidentity_size"]
                and null["audit"]["d5_new_size"]
                >= record["audit"]["d5_new_size"]
                and null["compiler"]["d2_entries"]
                <= record["compiler"]["d2_entries"]
                and null["compiler"]["d3_entries"]
                <= record["compiler"]["d3_entries"]
                and null["audit"]["phi_store_d3_scan_d2"]
                <= record["audit"]["phi_store_d3_scan_d2"]
                for null in coordinate_nulls
            )
            p_value = (1 + dominated) / (1 + len(coordinate_nulls))
            assert close(record["empirical_joint_dominance_p"], p_value)
            scan_means = [
                value["probes_per_target_mean"]
                for value in record["query"]["scan_orders"].values()
            ]
            spread = max(scan_means) / min(scan_means)
            assert close(record["scan_order_mean_spread_ratio"], spread)
            ratios = [
                record["ratios_to_null_medians"][family]
                for family in ("random_x", "source_prf_x")
            ]
            gate = (
                record["family"]
                in ("x_interval", "square_map", "rational_union")
                and all(
                    ratio["d5_nonidentity"] >= 0.9
                    and ratio["d5_new"] >= 0.9
                    and ratio["d2"] <= 0.8
                    and ratio["d3"] <= 0.8
                    for ratio in ratios
                )
                and p_value <= 0.05
                and spread <= 1.05
                and record["query"]["first_witness"] is not None
            )
            assert record["stage_a_joint_gate"] == gate


def verify_result(
    raw_path: Path, manifest_path: Path
) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text())
    assert sha256_file(raw_path) == manifest["raw_result_sha256"]
    assert sha256_file(EXPERIMENT_SOURCE) == manifest["source_sha256"]
    result = json.loads(raw_path.read_text())
    assert result["valid"] is True
    assert result["interpretation_eligible"] is True
    assert result["source"]["coordinate_expansion_sha256"] == manifest[
        "source_sha256"
    ]
    assert result["config"]["null_draws"] == 31
    assert result["config"]["bit_sizes"] == [10, 12, 14]
    assert result["config"]["seeds"] == [271828]
    assert len(result["instances"]) == 3
    total_records = 0
    candidate_passes = 0
    for instance in result["instances"]:
        record = instance["curve"]
        curve = Curve(record["p"], record["a"], record["b"])
        q = record["q"]
        generator = as_point(record["generator"])
        assert is_prime(curve.p) and is_prime(q)
        assert curve_order(curve) == q == record["order"]
        assert record["cofactor"] == 1
        assert record["trace"] == curve.p + 1 - q
        assert record["trace"] not in (0, 1)
        assert curve.on_curve(generator)
        assert curve.mul(q, generator) is None
        target_points = [
            as_point(value) for value in instance["target_points"]
        ]
        assert target_points == [
            curve.mul(scalar, generator)
            for scalar in instance["target_scalars"]
        ]
        point_to_scalar = {}
        point = None
        for scalar in range(q):
            assert point not in point_to_scalar
            point_to_scalar[point] = scalar
            point = curve.add(point, generator)
        assert point is None and len(point_to_scalar) == q
        records = instance["configurations"]
        assert len(records) == 194
        for configuration in records:
            verify_record(
                configuration,
                curve,
                q,
                point_to_scalar,
                target_points,
            )
        verify_statistics(records)
        digests = [
            configuration["factor_base_digest_before_audit"]
            for configuration in records
        ]
        assert canonical_hash(digests) == instance[
            "factor_base_digest_set_before_audit"
        ]
        assert instance["factor_base_digest_set_before_audit"] == instance[
            "factor_base_digest_set_after_audit"
        ]
        total_records += len(records)
        candidate_passes += sum(
            configuration["stage_a_joint_gate"]
            for configuration in records
        )
    assert total_records == manifest["configurations"] == 582
    assert candidate_passes == 0
    assert result["summary"]["promoted_candidate_cells"] == []
    assert result["summary"]["breakthrough_claim"] is False
    assert result["summary"]["result_classification"] == manifest[
        "result_classification"
    ]
    return {
        "valid": True,
        "raw_result_sha256": manifest["raw_result_sha256"],
        "source_sha256": manifest["source_sha256"],
        "instances_verified": len(result["instances"]),
        "configurations_verified": total_records,
        "candidate_stage_a_passes": candidate_passes,
        "breakthrough_claim": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("raw_result", type=Path)
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    print(
        json.dumps(
            verify_result(args.raw_result, args.manifest),
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
