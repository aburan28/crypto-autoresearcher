#!/usr/bin/env python3
"""Execute the materialized-D4 baseline on compressed-join target schedules."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import statistics
import sys
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
GENERATOR_PATH = SCRIPT_PATH.with_name("compressed_join.py")


def load_generator() -> Any:
    spec = importlib.util.spec_from_file_location(
        "compressed_join_materialized_audit_generator", GENERATOR_PATH
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


def run_audit(document: dict[str, Any], input_path: Path) -> dict[str, Any]:
    if document.get("protocol") != GENERATOR.PROTOCOL:
        raise ValueError("input protocol mismatch")
    baseline_rows = []
    comparison_rows = []
    for instance in document["instances"]:
        curve_record = instance["curve"]
        curve = GENERATOR.Curve(
            curve_record["p"], curve_record["a"], curve_record["b"]
        )
        for family in instance["families"]:
            factor_points = [
                GENERATOR.BASE.point_from_json(point)
                for point in family["factor_base"]["points"]
            ]
            compiled = GENERATOR.BASE.compile_four_sum_advice(
                curve, factor_points, 1
            )
            targets = [
                GENERATOR.BASE.point_from_json(record["target"])
                for record in family["rows"][0]["query_samples"]["supported_d5"][
                    "records"
                ]
            ]
            query_records = []
            verification_ops = GENERATOR.Ops()
            for target in targets:
                result = GENERATOR.BASE.query_target(
                    curve,
                    target,
                    factor_points,
                    compiled.mapping,
                    1,
                )
                if not result["relations"]:
                    raise AssertionError("materialized baseline missed a supported D5 target")
                witness = result["relations"][0]
                if not GENERATOR.BASE.verify_witness(
                    curve,
                    factor_points,
                    witness,
                    target,
                    verification_ops,
                ):
                    raise AssertionError("materialized baseline returned an invalid witness")
                query_records.append(
                    {
                        "target": GENERATOR.BASE.point_json(target),
                        "witness": list(witness),
                        "group_operations": result["ops"].group_operations,
                        "probes": result["probes"],
                        "witness_reads": result["witness_reads"],
                    }
                )
            average_ops = statistics.fmean(
                record["group_operations"] for record in query_records
            )
            baseline = {
                "bits": curve_record["bits"],
                "curve_id": curve_record["id"],
                "family": family["family"],
                "sample_count": len(query_records),
                "advice_bits": compiled.record["payload_bit_lower_estimate"],
                "average_group_operations": average_ops,
                "maximum_group_operations": max(
                    record["group_operations"] for record in query_records
                ),
                "average_probes": statistics.fmean(
                    record["probes"] for record in query_records
                ),
                "verification_audit_ops": vars(verification_ops),
                "records": query_records,
            }
            baseline_rows.append(baseline)
            for candidate in family["rows"]:
                if candidate["router"] not in GENERATOR.CANDIDATE_ROUTERS:
                    continue
                comparison_rows.append(
                    {
                        "bits": curve_record["bits"],
                        "curve_id": curve_record["id"],
                        "family": family["family"],
                        "router": candidate["router"],
                        "bucket_count": candidate["bucket_count"],
                        "advice_ratio_to_materialized": (
                            candidate["advice"]["payload_bit_lower_estimate"]
                            / baseline["advice_bits"]
                        ),
                        "supported_d5_group_operation_ratio_to_materialized": (
                            candidate["query_samples"]["supported_d5"][
                                "average_group_operations"
                            ]
                            / average_ops
                        ),
                        "dominates_both": (
                            candidate["advice"]["payload_bit_lower_estimate"]
                            < baseline["advice_bits"]
                            and candidate["query_samples"]["supported_d5"][
                                "average_group_operations"
                            ]
                            < average_ops
                        ),
                    }
                )

    summary = {}
    for router in GENERATOR.CANDIDATE_ROUTERS:
        selected = [row for row in comparison_rows if row["router"] == router]
        if not selected:
            continue
        summary[router] = {
            "rows": len(selected),
            "dominates_both_count": sum(int(row["dominates_both"]) for row in selected),
            "advice_ratio_range": [
                min(row["advice_ratio_to_materialized"] for row in selected),
                max(row["advice_ratio_to_materialized"] for row in selected),
            ],
            "online_ratio_range": [
                min(
                    row["supported_d5_group_operation_ratio_to_materialized"]
                    for row in selected
                ),
                max(
                    row["supported_d5_group_operation_ratio_to_materialized"]
                    for row in selected
                ),
            ],
        }
    return {
        "protocol": "AUDIT-ECDLP-COMPRESSED-JOIN-MATERIALIZED-001",
        "status": ["NEGATIVE RESULT", "TOY-EVIDENCE"],
        "development_only": True,
        "input_file_sha256": sha256_file(input_path),
        "source_hashes": {
            "materialized_audit_sha256": sha256_file(SCRIPT_PATH),
            "compressed_join_sha256": sha256_file(GENERATOR_PATH),
        },
        "baseline_rows": baseline_rows,
        "comparison_rows": comparison_rows,
        "summary": summary,
        "interpretation": (
            "The router exposes a space/query tradeoff, but no tested row uses both "
            "less advice and fewer supported-target group operations than the exact "
            "materialized D4 dictionary."
        ),
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    result = run_audit(load_json(args.input), args.input)
    encoded = json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n"
    if args.output is None:
        sys.stdout.write(encoded)
    else:
        args.output.write_text(encoded, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
