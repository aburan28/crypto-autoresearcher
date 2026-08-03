#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
import math
import platform
import resource
import sys
import time
from collections import Counter, defaultdict
from dataclasses import asdict
from pathlib import Path
from typing import Any


Point = tuple[int, int] | None
SCRIPT_PATH = Path(__file__).resolve()
TYPED_SOURCE = SCRIPT_PATH.with_name("typed_five_ec.py")


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load prerequisite: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


TYPED = load_module("typed_five_ec_aligned_batch", TYPED_SOURCE)


def canonical_digest(value: Any) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def rss_bytes() -> int:
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(value if platform.system() == "Darwin" else value * 1024)


def negate(point: Point, p: int) -> Point:
    return None if point is None else (point[0], (-point[1]) % p)


def subtract(curve: Any, left: Point, right: Point, ops: Any) -> Point:
    return curve.add(left, negate(right, curve.p), ops)


def point_from_json(value: list[int] | None) -> Point:
    return None if value is None else (value[0], value[1])


def point_json(point: Point) -> list[int] | None:
    return None if point is None else [point[0], point[1]]


def hash_scalar(label: str, q: int) -> int:
    return (
        int.from_bytes(hashlib.sha256(label.encode("ascii")).digest(), "big")
        % (q - 1)
        + 1
    )


def target_sizes(b_size: int, exponents: list[float]) -> list[dict[str, Any]]:
    records = []
    seen = set()
    for exponent in exponents:
        size = math.ceil(b_size**exponent)
        if size in seen:
            continue
        seen.add(size)
        records.append({"exponent": exponent, "size": size})
    return records


def build_d2(curve: Any, r_points: list[Point]) -> dict[str, Any]:
    ops = TYPED.Ops()
    witnesses: dict[Point, list[tuple[int, int]]] = defaultdict(list)
    attempts = 0
    for left in range(len(r_points)):
        for right in range(left, len(r_points)):
            attempts += 1
            point = curve.add(r_points[left], r_points[right], ops)
            witnesses[point].append((left, right))
    serializable = [
        {
            "point": point_json(point),
            "witnesses": [list(pair) for pair in pairs],
        }
        for point, pairs in sorted(
            witnesses.items(),
            key=lambda item: (
                item[0] is None,
                item[0] if item[0] is not None else (0, 0),
            ),
        )
    ]
    return {
        "points_internal": list(witnesses),
        "witnesses_internal": witnesses,
        "summary": {
            "attempted_transitions": attempts,
            "unique_points": len(witnesses),
            "witness_records": sum(map(len, witnesses.values())),
            "ops": asdict(ops),
            "deep_bytes": TYPED.COORDINATE.deep_size(witnesses),
            "serialized_bytes": len(
                json.dumps(
                    serializable,
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode("ascii")
            ),
            "digest": canonical_digest(serializable),
        },
    }


def quotient_coefficients(
    d_coefficient: int,
    r_witness: tuple[int, int, int, int],
    r_size: int,
) -> list[int]:
    counts = Counter(r_witness)
    if sum(counts.values()) != 4:
        raise AssertionError("relation must contain four R terms")
    return [1, d_coefficient] + [
        counts[index] for index in range(1, r_size)
    ]


def random_target_scalars(
    curve_id: str, family: str, q: int, count: int
) -> list[int]:
    scalars = []
    used = set()
    draw = 0
    while len(scalars) < count:
        scalar = hash_scalar(
            (
                "EXP-ECDLP-COORD-EXPANSION-001|"
                f"ALIGNED-BATCH|{curve_id}|{family}|RANDOM|{draw}"
            ),
            q,
        )
        draw += 1
        if scalar in used:
            continue
        used.add(scalar)
        scalars.append(scalar)
    return scalars


def build_aligned_keys(
    curve: Any,
    q: int,
    q0: Point,
    p0: Point,
    d_point: Point,
    r_points: list[Point],
    a_size: int,
    target_count: int,
) -> dict[str, Any]:
    ops = TYPED.Ops()
    keys: dict[Point, list[dict[str, int]]] = defaultdict(list)
    base = subtract(curve, q0, p0, ops)
    minimum_k = -(a_size - 1)
    maximum_k = target_count - 1
    shifted = curve.add(
        base, curve.mul(minimum_k % q, d_point, ops), ops
    )
    records = 0
    for k in range(minimum_k, maximum_k + 1):
        if k != minimum_k:
            shifted = curve.add(shifted, d_point, ops)
        for r_index, r_point in enumerate(r_points):
            key = subtract(curve, shifted, r_point, ops)
            keys[key].append({"k": k, "r1": r_index})
            records += 1
    return {
        "keys_internal": keys,
        "summary": {
            "mode": "aligned",
            "target_records": records,
            "unique_keys": len(keys),
            "key_collisions": records - len(keys),
            "theoretical_record_bound": (
                target_count + a_size - 1
            )
            * len(r_points),
            "ops": asdict(ops),
            "deep_bytes": TYPED.COORDINATE.deep_size(keys),
        },
    }


def build_random_keys(
    curve: Any,
    target_points: list[Point],
    target_scalars: list[int],
    a_points: list[Point],
    r_points: list[Point],
) -> dict[str, Any]:
    ops = TYPED.Ops()
    keys: dict[Point, list[dict[str, int]]] = defaultdict(list)
    records = 0
    for target_index, (target, scalar) in enumerate(
        zip(target_points, target_scalars)
    ):
        for a_index, a_point in enumerate(a_points):
            complement = subtract(curve, target, a_point, ops)
            for r_index, r_point in enumerate(r_points):
                key = subtract(curve, complement, r_point, ops)
                keys[key].append(
                    {
                        "target": target_index,
                        "a": a_index,
                        "r1": r_index,
                        "rhs": scalar,
                    }
                )
                records += 1
    return {
        "keys_internal": keys,
        "summary": {
            "mode": "random",
            "target_records": records,
            "unique_keys": len(keys),
            "key_collisions": records - len(keys),
            "theoretical_record_bound": (
                len(target_points) * len(a_points) * len(r_points)
            ),
            "ops": asdict(ops),
            "deep_bytes": TYPED.COORDINATE.deep_size(keys),
        },
    }


def add_many(curve: Any, points: list[Point], ops: Any) -> Point:
    total: Point = None
    for point in points:
        total = curve.add(total, point, ops)
    return total


def scan_batch(
    curve: Any,
    q: int,
    d2: dict[str, Any],
    keys: dict[str, Any],
    mode: str,
    q0_scalar: int | None,
    q0_point: Point | None,
    d_point: Point,
    a_points: list[Point],
    r_points: list[Point],
    target_points: list[Point],
    target_count: int,
) -> dict[str, Any]:
    query_ops = TYPED.Ops()
    replay_ops = TYPED.Ops()
    basis = TYPED.IncrementalBasis(len(r_points) + 1, q)
    equations: dict[
        tuple[tuple[int, ...], int], dict[str, Any]
    ] = {}
    replayed = set()
    covered = set()
    attempts = 0
    lookups = 0
    hit_key_records = 0
    witness_replays = 0
    replay_mismatches = 0
    equation_mismatches = 0
    for d2_point in d2["points_internal"]:
        for r4, r4_point in enumerate(r_points):
            attempts += 1
            d3_point = curve.add(d2_point, r4_point, query_ops)
            lookups += 1
            records = keys["keys_internal"].get(d3_point, ())
            if not records:
                continue
            for pair in d2["witnesses_internal"][d2_point]:
                for record in records:
                    hit_key_records += 1
                    r_witness = (
                        record["r1"],
                        pair[0],
                        pair[1],
                        r4,
                    )
                    if mode == "aligned":
                        k = record["k"]
                        first_t = max(0, k)
                        last_t = min(target_count - 1, k + len(a_points) - 1)
                        if first_t > last_t:
                            raise AssertionError("aligned key has no target")
                        valid_targets = range(first_t, last_t + 1)
                        valid_targets = list(valid_targets)
                        covered.update(valid_targets)
                        target_index = first_t
                        a_index = target_index - k
                        coefficients = quotient_coefficients(
                            -k, r_witness, len(r_points)
                        )
                        if q0_scalar is None or q0_point is None:
                            raise AssertionError("aligned target missing Q0")
                        rhs = q0_scalar
                    else:
                        target_index = record["target"]
                        a_index = record["a"]
                        covered.add(target_index)
                        coefficients = quotient_coefficients(
                            a_index, r_witness, len(r_points)
                        )
                        rhs = record["rhs"]
                        valid_targets = [target_index]
                    for replay_target in valid_targets:
                        replay_a = (
                            replay_target - record["k"]
                            if mode == "aligned"
                            else record["a"]
                        )
                        replay_key = (
                            replay_target,
                            replay_a,
                            r_witness,
                        )
                        if replay_key in replayed:
                            continue
                        replayed.add(replay_key)
                        witness_replays += 1
                        replay = add_many(
                            curve,
                            [
                                a_points[replay_a],
                                *(
                                    r_points[index]
                                    for index in r_witness
                                ),
                            ],
                            replay_ops,
                        )
                        expected_target = target_points[replay_target]
                        replay_mismatches += int(
                            replay != expected_target
                        )
                    equation_key = (tuple(coefficients), rhs)
                    equations.setdefault(
                        equation_key,
                        {
                            "coefficients": coefficients,
                            "rhs": rhs,
                            "target_index": target_index,
                            "a_index": a_index,
                            "r_witness": list(r_witness),
                        },
                    )
    independent_equations = []
    for equation in equations.values():
        if basis.insert(
            equation["coefficients"], equation["rhs"]
        ):
            independent_equations.append(equation)
    if replay_mismatches or equation_mismatches:
        raise AssertionError("batch witness or equation mismatch")
    return {
        "summary": {
            "d3_attempted_transitions": attempts,
            "lookups": lookups,
            "hit_key_records": hit_key_records,
            "witness_replays": witness_replays,
            "covered_targets": len(covered),
            "covered_target_fraction": len(covered)
            / max(1, target_count),
            "distinct_equations": len(equations),
            "independent_equations": len(independent_equations),
            "quotient_rank": basis.rank,
            "quotient_width": len(r_points) + 1,
            "full_quotient_rank": basis.rank == len(r_points) + 1,
            "replay_mismatches": replay_mismatches,
            "equation_mismatches": equation_mismatches,
            "query_ops": asdict(query_ops),
            "replay_ops": asdict(replay_ops),
            "linear_ops": asdict(basis.ops),
            "equation_digest": canonical_digest(
                sorted(
                    (
                        list(key[0]),
                        key[1],
                    )
                    for key in equations
                )
            ),
        },
        "independent_equations": independent_equations,
    }


def run_family(
    curve_record: dict[str, Any],
    family_record: dict[str, Any],
    exponents: list[float],
) -> dict[str, Any]:
    curve = TYPED.Curve(
        curve_record["p"], curve_record["a"], curve_record["b"]
    )
    q = curve_record["q"]
    generator = point_from_json(curve_record["generator"])
    r_points = [
        point_from_json(value)
        for value in family_record["factor_base"]["points"]
    ]
    progression = family_record["progression"]
    a_points = [point_from_json(value) for value in progression["points"]]
    p0 = point_from_json(progression["p0"])
    d_point = point_from_json(progression["d"])
    d2 = build_d2(curve, r_points)
    cohorts = []
    for schedule in target_sizes(len(r_points), exponents):
        target_count = schedule["size"]
        q0_scalar = hash_scalar(
            (
                "EXP-ECDLP-COORD-EXPANSION-001|ALIGNED-BATCH|"
                f"{curve_record['id']}|{family_record['family']}|Q0"
            ),
            q,
        )
        aligned_target_ops = TYPED.Ops()
        q0_point = curve.mul(
            q0_scalar, generator, aligned_target_ops
        )
        aligned_targets = [q0_point]
        for _ in range(1, target_count):
            aligned_targets.append(
                curve.add(
                    aligned_targets[-1],
                    d_point,
                    aligned_target_ops,
                )
            )
        aligned_keys = build_aligned_keys(
            curve,
            q,
            q0_point,
            p0,
            d_point,
            r_points,
            len(a_points),
            target_count,
        )
        aligned = scan_batch(
            curve,
            q,
            d2,
            aligned_keys,
            "aligned",
            q0_scalar,
            q0_point,
            d_point,
            a_points,
            r_points,
            aligned_targets,
            target_count,
        )
        random_scalars = random_target_scalars(
            curve_record["id"],
            family_record["family"],
            q,
            target_count,
        )
        random_target_ops = TYPED.Ops()
        random_targets = [
            curve.mul(scalar, generator, random_target_ops)
            for scalar in random_scalars
        ]
        random_keys = build_random_keys(
            curve,
            random_targets,
            random_scalars,
            a_points,
            r_points,
        )
        random_result = scan_batch(
            curve,
            q,
            d2,
            random_keys,
            "random",
            None,
            None,
            d_point,
            a_points,
            r_points,
            random_targets,
            target_count,
        )
        mode_costs = {}
        for mode, target_build, key_record, scan_record in (
            (
                "aligned",
                aligned_target_ops,
                aligned_keys["summary"],
                aligned["summary"],
            ),
            (
                "random",
                random_target_ops,
                random_keys["summary"],
                random_result["summary"],
            ),
        ):
            core_online = (
                target_build.group_operations
                + key_record["ops"]["group_operations"]
                + scan_record["query_ops"]["group_operations"]
            )
            with_fixed = (
                core_online
                + d2["summary"]["ops"]["group_operations"]
            )
            covered = scan_record["covered_targets"]
            mode_costs[mode] = {
                "core_online_group_operations": core_online,
                "one_batch_plus_fixed_group_operations": with_fixed,
                "audit_replay_group_operations": scan_record[
                    "replay_ops"
                ]["group_operations"],
                "core_online_group_operations_per_covered_target": (
                    core_online / max(1, covered)
                ),
                "one_batch_plus_fixed_group_operations_per_covered_target": (
                    with_fixed / max(1, covered)
                ),
                "fixed_plus_key_deep_bytes": (
                    d2["summary"]["deep_bytes"]
                    + key_record["deep_bytes"]
                ),
                "fixed_plus_target_records": (
                    d2["summary"]["witness_records"]
                    + key_record["target_records"]
                ),
            }
        cohorts.append(
            {
                "target_exponent": schedule["exponent"],
                "target_count": target_count,
                "target_build_ops": {
                    "aligned": asdict(aligned_target_ops),
                    "random": asdict(random_target_ops),
                },
                "aligned": {
                    "keys": aligned_keys["summary"],
                    "scan": aligned["summary"],
                },
                "random": {
                    "keys": random_keys["summary"],
                    "scan": random_result["summary"],
                },
                "comparison": {
                    "aligned_over_random_target_records": (
                        aligned_keys["summary"]["target_records"]
                        / random_keys["summary"]["target_records"]
                    ),
                    "aligned_over_random_deep_bytes": (
                        aligned_keys["summary"]["deep_bytes"]
                        / random_keys["summary"]["deep_bytes"]
                    ),
                    "aligned_over_random_coverage": (
                        aligned["summary"]["covered_target_fraction"]
                        / max(
                            random_result["summary"][
                                "covered_target_fraction"
                            ],
                            1 / target_count,
                        )
                    ),
                    "aligned_rank_per_distinct_equation": (
                        aligned["summary"]["quotient_rank"]
                        / max(
                            1,
                            aligned["summary"]["distinct_equations"],
                        )
                    ),
                },
                "costs": mode_costs,
            }
        )
    return {
        "curve_id": curve_record["id"],
        "q": q,
        "family": family_record["family"],
        "a_size": len(a_points),
        "r_size": len(r_points),
        "d2": d2["summary"],
        "cohorts": cohorts,
        "peak_rss_bytes_after_family": rss_bytes(),
    }


def run(
    result_path: Path,
    families: list[str],
    exponents: list[float],
) -> dict[str, Any]:
    typed_result = json.loads(result_path.read_text(encoding="utf-8"))
    started = time.perf_counter()
    rows = []
    for instance in typed_result["instances"]:
        by_family = {
            row["family"]: row for row in instance["families"]
        }
        for family in families:
            rows.append(
                run_family(
                    instance["curve"], by_family[family], exponents
                )
            )
    interior_signals = []
    one_instance_passes = []
    for row in rows:
        for cohort in row["cohorts"]:
            exponent = cohort["target_exponent"]
            if 0.5 < exponent < 1.5:
                interior_signals.append(
                    cohort["aligned"]["keys"]["target_records"]
                    <= cohort["aligned"]["keys"][
                        "theoretical_record_bound"
                    ]
                    and cohort["comparison"][
                        "aligned_over_random_target_records"
                    ]
                    <= 2 / min(row["a_size"], row["r_size"])
                    and cohort["aligned"]["scan"][
                        "covered_target_fraction"
                    ]
                    >= 0.8
                    * cohort["random"]["scan"][
                        "covered_target_fraction"
                    ]
                )
            one_instance_passes.append(
                cohort["aligned"]["scan"]["full_quotient_rank"]
                and (
                    cohort["aligned"]["keys"]["ops"][
                        "group_operations"
                    ]
                    + cohort["aligned"]["scan"]["query_ops"][
                        "group_operations"
                    ]
                )
                < math.sqrt(row["q"])
            )
    return {
        "protocol": (
            "EXP-ECDLP-COORD-EXPANSION-001-"
            "typed-aligned-batch-mitm-v1"
        ),
        "claim_status": [
            "HYPOTHESIS",
            "TOY-EVIDENCE",
            "MODEL-BOUND",
            "NOVELTY-UNVERIFIED",
        ],
        "source": {
            "typed_aligned_batch_mitm_sha256": TYPED.sha256_file(
                SCRIPT_PATH
            ),
            "typed_five_ec_sha256": TYPED.sha256_file(TYPED_SOURCE),
            "input_result_sha256": TYPED.sha256_file(result_path),
        },
        "config": {
            "input_result": str(result_path.resolve()),
            "families": families,
            "target_exponents": exponents,
        },
        "rows": rows,
        "summary": {
            "family_rows": len(rows),
            "cohorts": sum(len(row["cohorts"]) for row in rows),
            "many_target_structural_gate": bool(interior_signals)
            and all(interior_signals),
            "one_instance_relation_gate": bool(one_instance_passes)
            and all(one_instance_passes),
            "all_semantics_valid": all(
                cohort[mode]["scan"]["replay_mismatches"] == 0
                and cohort[mode]["scan"]["equation_mismatches"] == 0
                for row in rows
                for cohort in row["cohorts"]
                for mode in ("aligned", "random")
            ),
            "breakthrough_claim": False,
            "boundary": (
                "Aligned many-target decomposition diagnostic. It is not "
                "a one-target ECDLP exponent claim."
            ),
        },
        "peak_rss_bytes": rss_bytes(),
        "total_wall_seconds": time.perf_counter() - started,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("result", type=Path)
    parser.add_argument("--families", nargs="+", required=True)
    parser.add_argument(
        "--target-exponents", nargs="+", type=float, required=True
    )
    args = parser.parse_args()
    print(
        json.dumps(
            run(
                args.result,
                args.families,
                args.target_exponents,
            ),
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
