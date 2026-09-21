#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import platform
import resource
import sys
import time
from collections import defaultdict
from dataclasses import asdict
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
ALIGNED_PATH = SCRIPT_PATH.with_name("typed_aligned_batch_mitm.py")


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load prerequisite: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ALIGNED = load_module("typed_two_dimensional_lattice_aligned", ALIGNED_PATH)
Point = ALIGNED.Point


def rss_bytes() -> int:
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(value if platform.system() == "Darwin" else value * 1024)


def point_from_json(value: list[int] | None) -> Point:
    return None if value is None else (value[0], value[1])


def negate(point: Point, p: int) -> Point:
    return None if point is None else (point[0], (-point[1]) % p)


def subtract(curve: Any, left: Point, right: Point, ops: Any) -> Point:
    return curve.add(left, negate(right, curve.p), ops)


def add_many(curve: Any, points: list[Point], ops: Any) -> Point:
    total: Point = None
    for point in points:
        total = curve.add(total, point, ops)
    return total


def lattice_coefficients(k: int, v: int, witness: tuple[int, int, int, int], r_size: int) -> list[int]:
    counts = [0] * r_size
    for index in witness:
        counts[index] += 1
    return [1, -k, -v, *counts[1:]]


def build_lattice_targets(curve: Any, q: int, generator: Point, q0_scalar: int, d_point: Point, e_point: Point, u_size: int, v_size: int) -> tuple[list[Point], dict[str, int]]:
    ops = ALIGNED.TYPED.Ops()
    q0 = curve.mul(q0_scalar, generator, ops)
    targets: list[Point] = []
    for v in range(v_size):
        row = curve.add(q0, curve.mul(v, e_point, ops), ops) if v else q0
        for u in range(u_size):
            targets.append(row if u == 0 else curve.add(targets[-1], d_point, ops))
    return targets, asdict(ops)


def build_lattice_keys(curve: Any, q: int, q0: Point, p0: Point, d_point: Point, e_point: Point, r_points: list[Point], a_size: int, u_size: int, v_size: int) -> dict[str, Any]:
    ops = ALIGNED.TYPED.Ops()
    keys: dict[Point, list[dict[str, int]]] = defaultdict(list)
    base = subtract(curve, q0, p0, ops)
    minimum_k = -(a_size - 1)
    records = 0
    for v in range(v_size):
        shifted = curve.add(base, curve.mul(v, e_point, ops), ops) if v else base
        shifted = curve.add(shifted, curve.mul(minimum_k % q, d_point, ops), ops)
        for k in range(minimum_k, u_size):
            if k != minimum_k:
                shifted = curve.add(shifted, d_point, ops)
            for r_index, r_point in enumerate(r_points):
                keys[subtract(curve, shifted, r_point, ops)].append({"k": k, "v": v, "r1": r_index})
                records += 1
    return {
        "keys_internal": keys,
        "summary": {
            "mode": "two_dimensional_lattice",
            "target_records": records,
            "unique_keys": len(keys),
            "key_collisions": records - len(keys),
            "theoretical_record_bound": (u_size + a_size - 1) * v_size * len(r_points),
            "ops": asdict(ops),
            "deep_bytes": ALIGNED.TYPED.COORDINATE.deep_size(keys),
        },
    }


def scan_lattice(curve: Any, q: int, d2: dict[str, Any], keys: dict[str, Any], q0_scalar: int, d_point: Point, a_points: list[Point], r_points: list[Point], targets: list[Point], u_size: int, v_size: int) -> dict[str, Any]:
    query_ops = ALIGNED.TYPED.Ops()
    replay_ops = ALIGNED.TYPED.Ops()
    basis = ALIGNED.TYPED.IncrementalBasis(len(r_points) + 2, q)
    equations: dict[tuple[tuple[int, ...], int], dict[str, Any]] = {}
    covered: set[int] = set()
    replayed: set[tuple[int, tuple[int, int, int, int]]] = set()
    attempts = 0
    hit_records = 0
    witness_replays = 0
    replay_mismatches = 0
    for d2_point in d2["points_internal"]:
        for r4, r4_point in enumerate(r_points):
            attempts += 1
            d3_point = curve.add(d2_point, r4_point, query_ops)
            for pair in d2["witnesses_internal"][d2_point]:
                for record in keys["keys_internal"].get(d3_point, ()):
                    hit_records += 1
                    witness = (record["r1"], pair[0], pair[1], r4)
                    k, v = record["k"], record["v"]
                    first_u, last_u = max(0, k), min(u_size - 1, k + len(a_points) - 1)
                    coefficients = lattice_coefficients(k, v, witness, len(r_points))
                    equation_key = (tuple(coefficients), q0_scalar)
                    equations.setdefault(equation_key, {"coefficients": coefficients, "rhs": q0_scalar, "u": first_u, "v": v, "witness": list(witness)})
                    for u in range(first_u, last_u + 1):
                        target_index = v * u_size + u
                        covered.add(target_index)
                        replay_key = (target_index, witness)
                        if replay_key in replayed:
                            continue
                        replayed.add(replay_key)
                        witness_replays += 1
                        replay = add_many(curve, [a_points[u - k], *(r_points[index] for index in witness)], replay_ops)
                        replay_mismatches += int(replay != targets[target_index])
    independent = []
    for equation in equations.values():
        if basis.insert(equation["coefficients"], equation["rhs"]):
            independent.append(equation)
    if replay_mismatches:
        raise AssertionError("lattice witness replay mismatch")
    return {
        "summary": {
            "d3_attempted_transitions": attempts,
            "lookups": attempts,
            "hit_key_records": hit_records,
            "witness_replays": witness_replays,
            "covered_targets": len(covered),
            "covered_target_fraction": len(covered) / max(1, u_size * v_size),
            "distinct_equations": len(equations),
            "independent_equations": len(independent),
            "quotient_rank": basis.rank,
            "quotient_width": len(r_points) + 2,
            "full_quotient_rank": basis.rank == len(r_points) + 2,
            "replay_mismatches": replay_mismatches,
            "equation_mismatches": 0,
            "query_ops": asdict(query_ops),
            "replay_ops": asdict(replay_ops),
            "linear_ops": asdict(basis.ops),
        },
        "independent_equations": independent,
    }


def run_family(curve_record: dict[str, Any], family_record: dict[str, Any], u_exponents: list[float], v_sizes: list[int]) -> dict[str, Any]:
    curve = ALIGNED.TYPED.Curve(curve_record["p"], curve_record["a"], curve_record["b"])
    q = curve_record["q"]
    generator = point_from_json(curve_record["generator"])
    r_points = [point_from_json(value) for value in family_record["factor_base"]["points"]]
    progression = family_record["progression"]
    a_points = [point_from_json(value) for value in progression["points"]]
    p0, d_point = point_from_json(progression["p0"]), point_from_json(progression["d"])
    d2 = ALIGNED.build_d2(curve, r_points)
    cohorts = []
    for schedule in ALIGNED.target_sizes(len(r_points), u_exponents):
        u_size = schedule["size"]
        cells = {}
        for v_size in v_sizes:
            q0_scalar = ALIGNED.hash_scalar(f"EXP-ECDLP-COORD-EXPANSION-001|LATTICE|{curve_record['id']}|{family_record['family']}|Q0|{u_size}|{v_size}", q)
            e_scalar = ALIGNED.hash_scalar(f"EXP-ECDLP-COORD-EXPANSION-001|LATTICE|{curve_record['id']}|{family_record['family']}|E|{u_size}|{v_size}", q)
            e_point_ops = ALIGNED.TYPED.Ops()
            e_point = curve.mul(e_scalar, generator, e_point_ops)
            targets, target_ops = build_lattice_targets(curve, q, generator, q0_scalar, d_point, e_point, u_size, v_size)
            keys = build_lattice_keys(curve, q, targets[0], p0, d_point, e_point, r_points, len(a_points), u_size, v_size)
            lattice = scan_lattice(curve, q, d2, keys, q0_scalar, d_point, a_points, r_points, targets, u_size, v_size)
            total_targets = u_size * v_size
            random_scalars = ALIGNED.random_target_scalars(f"LATTICE-CONTROL-{curve_record['id']}", family_record["family"], q, total_targets)
            random_ops = ALIGNED.TYPED.Ops()
            random_targets = [curve.mul(scalar, generator, random_ops) for scalar in random_scalars]
            random_keys = ALIGNED.build_random_keys(curve, random_targets, random_scalars, a_points, r_points)
            random_scan = ALIGNED.scan_batch(curve, q, d2, random_keys, "random", None, None, d_point, a_points, r_points, random_targets, total_targets)
            online = target_ops["group_operations"] + keys["summary"]["ops"]["group_operations"] + lattice["summary"]["query_ops"]["group_operations"]
            cells[str(v_size)] = {
                "u_size": u_size,
                "v_size": v_size,
                "q0_scalar_test_only": q0_scalar,
                "e_scalar_test_only": e_scalar,
                "target_build_ops": target_ops,
                "keys": keys["summary"],
                "scan": lattice["summary"],
                "aggregate": {
                    "target_count": total_targets,
                    "core_online_group_operations": online,
                    "fixed_plus_core_group_operations": online + d2["summary"]["ops"]["group_operations"],
                    "amortized_fixed_plus_core_group_operations": (online + d2["summary"]["ops"]["group_operations"]) / max(1, total_targets),
                    "peak_retained_advice_deep_bytes": d2["summary"]["deep_bytes"] + keys["summary"]["deep_bytes"],
                    "semantics_valid": lattice["summary"]["replay_mismatches"] == 0,
                },
                "random_control": {
                    "covered_targets": random_scan["summary"]["covered_targets"],
                    "covered_fraction": random_scan["summary"]["covered_target_fraction"],
                    "core_online_group_operations": random_ops.group_operations + random_keys["summary"]["ops"]["group_operations"] + random_scan["summary"]["query_ops"]["group_operations"],
                    "target_records": random_keys["summary"]["target_records"],
                    "deep_bytes": random_keys["summary"]["deep_bytes"],
                    "semantics_valid": random_scan["summary"]["replay_mismatches"] == 0,
                },
                "comparison": {
                    "aligned_over_random_coverage": lattice["summary"]["covered_target_fraction"] / max(random_scan["summary"]["covered_target_fraction"], 1 / max(1, total_targets)),
                    "record_reduction_vs_random": keys["summary"]["target_records"] / max(1, random_keys["summary"]["target_records"]),
                },
            }
        cohorts.append({"u_exponent": schedule["exponent"], "u_size": u_size, "v_sizes": cells})
    return {"curve_id": curve_record["id"], "q": q, "family": family_record["family"], "a_size": len(a_points), "r_size": len(r_points), "d2": d2["summary"], "cohorts": cohorts, "peak_rss_bytes_after_family": rss_bytes()}


def run(result_path: Path, families: list[str], u_exponents: list[float], v_sizes: list[int]) -> dict[str, Any]:
    typed_result = json.loads(result_path.read_text(encoding="utf-8"))
    started = time.perf_counter()
    rows = []
    for instance in typed_result["instances"]:
        by_family = {row["family"]: row for row in instance["families"]}
        for family in families:
            rows.append(run_family(instance["curve"], by_family[family], u_exponents, v_sizes))
    cells = [cell for row in rows for cohort in row["cohorts"] for cell in cohort["v_sizes"].values()]
    return {
        "protocol": "EXP-ECDLP-COORD-EXPANSION-001-typed-two-dimensional-lattice-v1",
        "claim_status": ["HYPOTHESIS", "OBSERVATION", "TOY-EVIDENCE", "MODEL-BOUND"],
        "source": {"typed_two_dimensional_lattice_sha256": ALIGNED.TYPED.sha256_file(SCRIPT_PATH), "typed_aligned_batch_mitm_sha256": ALIGNED.TYPED.sha256_file(ALIGNED_PATH), "input_result_sha256": ALIGNED.TYPED.sha256_file(result_path)},
        "config": {"input_result": str(result_path.resolve()), "families": families, "u_exponents": u_exponents, "v_sizes": v_sizes},
        "rows": rows,
        "summary": {"family_rows": len(rows), "cohorts": sum(len(row["cohorts"]) for row in rows), "cells": len(cells), "all_semantics_valid": all(cell["aggregate"]["semantics_valid"] and cell["random_control"]["semantics_valid"] for cell in cells), "full_rank_cells": sum(int(cell["scan"]["full_quotient_rank"]) for cell in cells), "breakthrough_claim": False, "boundary": "Two-dimensional aligned target-lattice diagnostic; no generic ECDLP claim."},
        "peak_rss_bytes": rss_bytes(),
        "total_wall_seconds": time.perf_counter() - started,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("result", type=Path)
    parser.add_argument("--families", nargs="+", required=True)
    parser.add_argument("--u-exponents", nargs="+", type=float, required=True)
    parser.add_argument("--v-sizes", nargs="+", type=int, required=True)
    args = parser.parse_args()
    if any(value <= 0 for value in args.v_sizes) or sorted(set(args.v_sizes)) != args.v_sizes:
        raise SystemExit("v sizes must be positive and sorted")
    print(json.dumps(run(args.result, args.families, args.u_exponents, args.v_sizes), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
