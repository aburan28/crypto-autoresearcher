#!/usr/bin/env python3
"""Audit x-only compressed-join signals against sign-matched random fibers."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import statistics
import sys
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
GENERATOR_PATH = SCRIPT_PATH.with_name("compressed_join.py")
X_ONLY_ROUTERS = ["x_mod", "x_interval", "legendre_vector"]


def load_generator() -> Any:
    spec = importlib.util.spec_from_file_location(
        "compressed_join_fiber_audit_generator", GENERATOR_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load generator: {GENERATOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


GENERATOR = load_generator()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def strict_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def reject_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON value: {value}")


def load_json(path: Path) -> dict[str, Any]:
    result = json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=strict_pairs,
        parse_constant=reject_constant,
    )
    if type(result) is not dict:
        raise ValueError("input result must be a JSON object")
    return result


def random_fiber_bucket(
    name: str,
    point: tuple[int, int] | None,
    bucket_count: int,
    curve: Any,
    q: int,
    seed: int,
    scalar_index: dict[tuple[int, int] | None, int] | None = None,
) -> int:
    """Hash the public x-fiber, intentionally identifying P and -P."""
    if name != GENERATOR.NEGATIVE_CONTROL:
        return ORIGINAL_BUCKET(
            name, point, bucket_count, curve, q, seed, scalar_index
        )
    width = max(1, math.ceil(curve.p.bit_length() / 8))
    encoded = b"identity" if point is None else b"x" + point[0].to_bytes(width, "big")
    digest = hashlib.sha256(
        seed.to_bytes(16, "big", signed=False)
        + bucket_count.to_bytes(8, "big")
        + encoded
    ).digest()
    return int.from_bytes(digest[:8], "big") % bucket_count


ORIGINAL_BUCKET = GENERATOR.router_bucket


def metric_record(advice: Any, samples: dict[str, Any]) -> dict[str, float | int]:
    return {
        "payload_bits": advice.record["payload_bit_lower_estimate"],
        "route_triples": advice.record["distinct_route_triples"],
        "occupied_buckets": advice.record["occupied_d2_buckets"],
        "supported_d4_point_reads": samples["supported_d4"]["average_point_reads"],
        "supported_d5_point_reads": samples["supported_d5"]["average_point_reads"],
        "supported_d4_group_operations": samples["supported_d4"][
            "average_group_operations"
        ],
        "supported_d5_group_operations": samples["supported_d5"][
            "average_group_operations"
        ],
    }


def distribution(values: list[float | int]) -> dict[str, float]:
    return {
        "minimum": float(min(values)),
        "median": float(statistics.median(values)),
        "maximum": float(max(values)),
    }


def run_audit(
    document: dict[str, Any],
    input_path: Path,
    bucket_counts: list[int],
    null_seeds: list[int],
) -> dict[str, Any]:
    if document.get("protocol") != GENERATOR.PROTOCOL:
        raise ValueError("input protocol mismatch")
    if not document.get("development_only"):
        raise ValueError("fiber-null audit is scoped to a development artifact")
    if not null_seeds or len(null_seeds) != len(set(null_seeds)):
        raise ValueError("null seeds must be nonempty and distinct")
    if any(not GENERATOR.is_power_of_two(value) for value in bucket_counts):
        raise ValueError("bucket counts must be powers of two")

    GENERATOR.compile_router.__globals__["router_bucket"] = random_fiber_bucket
    GENERATOR.query_d4.__globals__["router_bucket"] = random_fiber_bucket
    rows = []
    try:
        for instance in document["instances"]:
            curve_record = instance["curve"]
            curve = GENERATOR.Curve(
                curve_record["p"], curve_record["a"], curve_record["b"]
            )
            q = curve_record["q"]
            generator = GENERATOR.BASE.point_from_json(curve_record["generator"])
            for family in instance["families"]:
                factor_points = [
                    GENERATOR.BASE.point_from_json(point)
                    for point in family["factor_base"]["points"]
                ]
                d2 = GENERATOR.build_d2(curve, factor_points)
                d4 = GENERATOR.build_d4(curve, d2)
                d5_support, _ = GENERATOR.build_d5_support(
                    curve, factor_points, d4
                )
                for bucket_count in bucket_counts:
                    controls = []
                    for null_seed in null_seeds:
                        router_seed = (
                            null_seed
                            ^ instance["seed"]
                            ^ bucket_count * 0xA4093822
                        ) & ((1 << 128) - 1)
                        advice = GENERATOR.compile_router(
                            curve,
                            q,
                            factor_points,
                            d2,
                            d4,
                            GENERATOR.NEGATIVE_CONTROL,
                            bucket_count,
                            router_seed,
                            None,
                        )
                        samples = GENERATOR.run_query_samples(
                            curve,
                            q,
                            generator,
                            factor_points,
                            d2,
                            d4,
                            d5_support,
                            advice,
                            router_seed,
                            instance["target_seed"],
                            None,
                            document["configuration"]["query_samples"],
                        )
                        controls.append(
                            {
                                "null_seed": null_seed,
                                **metric_record(advice, samples),
                            }
                        )
                    distributions = {
                        metric: distribution([record[metric] for record in controls])
                        for metric in (
                            "payload_bits",
                            "route_triples",
                            "occupied_buckets",
                            "supported_d4_point_reads",
                            "supported_d5_point_reads",
                            "supported_d4_group_operations",
                            "supported_d5_group_operations",
                        )
                    }
                    for router_name in X_ONLY_ROUTERS:
                        candidate = next(
                            row
                            for row in family["rows"]
                            if row["router"] == router_name
                            and row["bucket_count"] == bucket_count
                        )
                        candidate_metrics = {
                            "payload_bits": candidate["advice"][
                                "payload_bit_lower_estimate"
                            ],
                            "route_triples": candidate["advice"][
                                "distinct_route_triples"
                            ],
                            "occupied_buckets": candidate["advice"][
                                "occupied_d2_buckets"
                            ],
                            "supported_d4_point_reads": candidate[
                                "query_samples"
                            ]["supported_d4"]["average_point_reads"],
                            "supported_d5_point_reads": candidate[
                                "query_samples"
                            ]["supported_d5"]["average_point_reads"],
                            "supported_d4_group_operations": candidate[
                                "query_samples"
                            ]["supported_d4"]["average_group_operations"],
                            "supported_d5_group_operations": candidate[
                                "query_samples"
                            ]["supported_d5"]["average_group_operations"],
                        }
                        ratios = {
                            metric: candidate_metrics[metric]
                            / distributions[metric]["median"]
                            for metric in candidate_metrics
                        }
                        joint_pass = (
                            ratios["payload_bits"] <= 0.8
                            and ratios["supported_d4_point_reads"] <= 0.8
                            and ratios["supported_d5_point_reads"] <= 0.8
                        )
                        rows.append(
                            {
                                "bits": curve_record["bits"],
                                "curve_id": curve_record["id"],
                                "family": family["family"],
                                "router": router_name,
                                "bucket_count": bucket_count,
                                "candidate": candidate_metrics,
                                "fiber_null_distributions": distributions,
                                "ratios_to_fiber_null_median": ratios,
                                "joint_20_percent_gate": joint_pass,
                            }
                        )
    finally:
        GENERATOR.compile_router.__globals__["router_bucket"] = ORIGINAL_BUCKET
        GENERATOR.query_d4.__globals__["router_bucket"] = ORIGINAL_BUCKET

    summary = {}
    for router_name in X_ONLY_ROUTERS:
        selected = [row for row in rows if row["router"] == router_name]
        summary[router_name] = {
            "rows": len(selected),
            "joint_20_percent_gate_count": sum(
                int(row["joint_20_percent_gate"]) for row in selected
            ),
            "payload_ratio_range": [
                min(
                    row["ratios_to_fiber_null_median"]["payload_bits"]
                    for row in selected
                ),
                max(
                    row["ratios_to_fiber_null_median"]["payload_bits"]
                    for row in selected
                ),
            ],
            "d4_read_ratio_range": [
                min(
                    row["ratios_to_fiber_null_median"][
                        "supported_d4_point_reads"
                    ]
                    for row in selected
                ),
                max(
                    row["ratios_to_fiber_null_median"][
                        "supported_d4_point_reads"
                    ]
                    for row in selected
                ),
            ],
            "d5_read_ratio_range": [
                min(
                    row["ratios_to_fiber_null_median"][
                        "supported_d5_point_reads"
                    ]
                    for row in selected
                ),
                max(
                    row["ratios_to_fiber_null_median"][
                        "supported_d5_point_reads"
                    ]
                    for row in selected
                ),
            ],
        }
    return {
        "protocol": "AUDIT-ECDLP-COMPRESSED-JOIN-FIBER-NULL-001",
        "status": ["OBSERVATION", "REVISE", "TOY-EVIDENCE"],
        "development_only": True,
        "input_file_sha256": sha256_file(input_path),
        "source_hashes": {
            "fiber_null_audit_sha256": sha256_file(SCRIPT_PATH),
            "compressed_join_sha256": sha256_file(GENERATOR_PATH),
        },
        "configuration": {
            "bucket_counts": bucket_counts,
            "null_seeds": null_seeds,
            "query_samples": document["configuration"]["query_samples"],
            "routers": X_ONLY_ROUTERS,
            "null": (
                "SHA-256 of the public x-fiber; P and -P receive the same label"
            ),
        },
        "rows": rows,
        "summary": summary,
        "routing_rows": [
            {
                "curve_id": row["curve_id"],
                "family": row["family"],
                "router": row["router"],
                "bucket_count": row["bucket_count"],
            }
            for row in rows
            if row["joint_20_percent_gate"]
        ],
        "interpretation": (
            "A full-point random label is not a symmetry-matched null for an x-only "
            "router. No routing row means the v1 coordinate signal does not survive "
            "this repair; it does not rule out source-tagged or batch compilers."
        ),
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--bucket-counts", type=int, nargs="+", default=[16, 32])
    parser.add_argument(
        "--null-seeds",
        type=int,
        nargs="+",
        default=[901, 907, 911, 919, 929, 937, 941, 947],
    )
    parser.add_argument("--output", type=Path)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    document = load_json(args.input)
    result = run_audit(
        document,
        args.input,
        args.bucket_counts,
        args.null_seeds,
    )
    encoded = json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n"
    if args.output is None:
        sys.stdout.write(encoded)
    else:
        args.output.write_text(encoded, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
