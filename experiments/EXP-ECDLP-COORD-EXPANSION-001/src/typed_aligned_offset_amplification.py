#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import platform
import resource
import sys
import time
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


ALIGNED = load_module("typed_aligned_batch_mitm_offset", ALIGNED_PATH)
Point = ALIGNED.Point


def rss_bytes() -> int:
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(value if platform.system() == "Darwin" else value * 1024)


def point_from_json(value: list[int] | None) -> Point:
    return None if value is None else (value[0], value[1])


def target_schedule(
    curve: Any,
    q: int,
    generator: Point,
    d_point: Point,
    curve_id: str,
    family: str,
    target_count: int,
    offset: int,
) -> tuple[list[Point], int, dict[str, int]]:
    scalar = ALIGNED.hash_scalar(
        f"EXP-ECDLP-COORD-EXPANSION-001|OFFSET|{curve_id}|{family}|{offset}",
        q,
    )
    ops = ALIGNED.TYPED.Ops()
    q0 = curve.mul(scalar, generator, ops)
    targets = [q0]
    for _ in range(1, target_count):
        targets.append(curve.add(targets[-1], d_point, ops))
    return targets, scalar, asdict(ops)


def summarize_offset(
    keys: dict[str, Any], scan: dict[str, Any], target_ops: dict[str, int],
    offset: int, scalar: int,
) -> dict[str, Any]:
    return {
        "offset": offset,
        "q0_scalar_test_only": scalar,
        "target_build_ops": target_ops,
        "keys": keys["summary"],
        "scan": scan["summary"],
        "semantics_valid": (
            scan["summary"]["replay_mismatches"] == 0
            and scan["summary"]["equation_mismatches"] == 0
        ),
    }


def run_family(
    curve_record: dict[str, Any], family_record: dict[str, Any],
    exponents: list[float], offset_counts: list[int],
) -> dict[str, Any]:
    curve = ALIGNED.TYPED.Curve(
        curve_record["p"], curve_record["a"], curve_record["b"]
    )
    q = curve_record["q"]
    generator = point_from_json(curve_record["generator"])
    r_points = [point_from_json(value) for value in family_record["factor_base"]["points"]]
    progression = family_record["progression"]
    a_points = [point_from_json(value) for value in progression["points"]]
    p0 = point_from_json(progression["p0"])
    d_point = point_from_json(progression["d"])
    d2 = ALIGNED.build_d2(curve, r_points)
    cohorts: list[dict[str, Any]] = []
    for schedule in ALIGNED.target_sizes(len(r_points), exponents):
        target_count = schedule["size"]
        by_k: dict[int, dict[str, Any]] = {}
        for offset_count in offset_counts:
            offsets = []
            for offset in range(offset_count):
                targets, scalar, target_ops = target_schedule(
                    curve, q, generator, d_point, curve_record["id"],
                    family_record["family"], target_count, offset,
                )
                keys = ALIGNED.build_aligned_keys(
                    curve, q, targets[0], p0, d_point, r_points,
                    len(a_points), target_count,
                )
                scan = ALIGNED.scan_batch(
                    curve, q, d2, keys, "aligned", scalar, targets[0],
                    d_point, a_points, r_points, targets, target_count,
                )
                offsets.append(summarize_offset(keys, scan, target_ops, offset, scalar))

            total_targets = offset_count * target_count
            total_target_ops = sum(
                item["target_build_ops"]["group_operations"] for item in offsets
            )
            total_key_ops = sum(
                item["keys"]["ops"]["group_operations"] for item in offsets
            )
            total_scan_ops = sum(
                item["scan"]["query_ops"]["group_operations"] for item in offsets
            )
            covered = sum(item["scan"]["covered_targets"] for item in offsets)
            valid = all(item["semantics_valid"] for item in offsets)

            random_scalars = ALIGNED.random_target_scalars(
                f"OFFSET-CONTROL-{curve_record['id']}",
                family_record["family"], q, total_targets,
            )
            random_ops = ALIGNED.TYPED.Ops()
            random_targets = [curve.mul(scalar, generator, random_ops) for scalar in random_scalars]
            random_keys = ALIGNED.build_random_keys(
                curve, random_targets, random_scalars, a_points, r_points,
            )
            random_scan = ALIGNED.scan_batch(
                curve, q, d2, random_keys, "random", None, None, d_point,
                a_points, r_points, random_targets, total_targets,
            )
            random_covered = random_scan["summary"]["covered_targets"]
            aligned_core = total_target_ops + total_key_ops + total_scan_ops
            random_core = (
                random_ops.group_operations
                + random_keys["summary"]["ops"]["group_operations"]
                + random_scan["summary"]["query_ops"]["group_operations"]
            )
            by_k[str(offset_count)] = {
                "offset_count": offset_count,
                "offsets": offsets,
                "aggregate": {
                    "target_count": total_targets,
                    "covered_targets": covered,
                    "covered_fraction": covered / max(1, total_targets),
                    "total_core_online_group_operations": aligned_core,
                    "amortized_core_online_group_operations": aligned_core / max(1, total_targets),
                    "fixed_plus_core_group_operations": aligned_core + d2["summary"]["ops"]["group_operations"],
                    "amortized_fixed_plus_core_group_operations": (
                        aligned_core + d2["summary"]["ops"]["group_operations"]
                    ) / max(1, total_targets),
                    "total_target_records": sum(item["keys"]["target_records"] for item in offsets),
                    "peak_offset_deep_bytes": max(item["keys"]["deep_bytes"] for item in offsets),
                    "cumulative_offset_deep_bytes": sum(item["keys"]["deep_bytes"] for item in offsets),
                    "peak_retained_advice_deep_bytes": d2["summary"]["deep_bytes"] + max(item["keys"]["deep_bytes"] for item in offsets),
                    "per_offset_full_rank": sum(int(item["scan"]["full_quotient_rank"]) for item in offsets),
                    "semantics_valid": valid,
                },
                "random_control": {
                    "target_count": total_targets,
                    "covered_targets": random_covered,
                    "covered_fraction": random_covered / max(1, total_targets),
                    "core_online_group_operations": random_core,
                    "amortized_core_online_group_operations": random_core / max(1, total_targets),
                    "target_records": random_keys["summary"]["target_records"],
                    "deep_bytes": random_keys["summary"]["deep_bytes"],
                    "semantics_valid": (
                        random_scan["summary"]["replay_mismatches"] == 0
                        and random_scan["summary"]["equation_mismatches"] == 0
                    ),
                },
                "comparison": {
                    "aligned_over_random_coverage": (
                        covered / max(1, random_covered)
                    ),
                    "aligned_over_random_amortized_core": (
                        aligned_core / max(1, total_targets)
                    ) / max(random_core / max(1, total_targets), 1e-12),
                    "coverage_gate": (
                        covered / max(1, total_targets)
                        >= 0.8 * (random_covered / max(1, total_targets))
                    ),
                },
            }
        cohorts.append({
            "target_exponent": schedule["exponent"],
            "target_count": target_count,
            "offset_counts": by_k,
        })
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


def run(result_path: Path, families: list[str], exponents: list[float], offset_counts: list[int]) -> dict[str, Any]:
    typed_result = json.loads(result_path.read_text(encoding="utf-8"))
    started = time.perf_counter()
    rows = []
    for instance in typed_result["instances"]:
        by_family = {row["family"]: row for row in instance["families"]}
        for family in families:
            rows.append(run_family(instance["curve"], by_family[family], exponents, offset_counts))
    cells = [
        cell
        for row in rows
        for cohort in row["cohorts"]
        for cell in cohort["offset_counts"].values()
    ]
    return {
        "protocol": "EXP-ECDLP-COORD-EXPANSION-001-typed-aligned-offset-amplification-v1",
        "claim_status": ["HYPOTHESIS", "OBSERVATION", "TOY-EVIDENCE", "MODEL-BOUND"],
        "source": {
            "typed_aligned_offset_amplification_sha256": ALIGNED.TYPED.sha256_file(SCRIPT_PATH),
            "typed_aligned_batch_mitm_sha256": ALIGNED.TYPED.sha256_file(ALIGNED_PATH),
            "input_result_sha256": ALIGNED.TYPED.sha256_file(result_path),
        },
        "config": {
            "input_result": str(result_path.resolve()),
            "families": families,
            "target_exponents": exponents,
            "offset_counts": offset_counts,
        },
        "rows": rows,
        "summary": {
            "family_rows": len(rows),
            "cohorts": sum(len(row["cohorts"]) for row in rows),
            "cells": len(cells),
            "all_semantics_valid": all(
                cell["aggregate"]["semantics_valid"]
                and cell["random_control"]["semantics_valid"]
                for cell in cells
            ),
            "coverage_signal_cells": sum(
                int(cell["comparison"]["coverage_gate"])
                for cell in cells
            ),
            "breakthrough_claim": False,
            "boundary": (
                "Common-offset coverage amplification for aligned many-target "
                "decomposition; independent offsets do not constitute a generic "
                "ECDLP relation collector."
            ),
        },
        "peak_rss_bytes": rss_bytes(),
        "total_wall_seconds": time.perf_counter() - started,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("result", type=Path)
    parser.add_argument("--families", nargs="+", required=True)
    parser.add_argument("--target-exponents", nargs="+", type=float, required=True)
    parser.add_argument("--offset-counts", nargs="+", type=int, required=True)
    args = parser.parse_args()
    if any(value <= 0 for value in args.offset_counts):
        raise SystemExit("offset counts must be positive")
    print(json.dumps(run(args.result, args.families, args.target_exponents, args.offset_counts), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
