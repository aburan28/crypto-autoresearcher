#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
GENERATOR_PATH = SCRIPT_PATH.with_name(
    "four_sum_divisor_barrier.py"
)
TIMING_KEYS = {
    "peak_rss_bytes",
    "peak_rss_bytes_after_family",
    "total_wall_seconds",
}


def load_generator() -> Any:
    spec = importlib.util.spec_from_file_location(
        "four_sum_divisor_barrier_for_verification",
        GENERATOR_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load generator: {GENERATOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def canonical_digest(value: Any) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def normalize(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: normalize(item)
            for key, item in value.items()
            if key not in TIMING_KEYS
        }
    if isinstance(value, list):
        return [normalize(item) for item in value]
    return value


def summary_consistent(result: dict[str, Any]) -> bool:
    families = result["config"]["families"]
    control_family = result["config"]["positive_control"]
    rows = result["rows"]
    curve_ids = sorted({row["curve_id"] for row in rows})
    candidates = [row for row in rows if row["family"] in families]
    controls = [
        row for row in rows if row["family"] == control_family
    ]
    control_compression = all(
        control["reduced_divisor_degree"]
        < min(
            row["reduced_divisor_degree"]
            for row in candidates
            if row["curve_id"] == control["curve_id"]
        )
        for control in controls
    )
    promoted = [
        family
        for family in families
        if len(
            [
                row
                for row in candidates
                if row["family"] == family
                and row["explicit_barrier_signal"]
            ]
        )
        == len(curve_ids)
    ]
    rho_families = [
        family
        for family in families
        if len(
            [
                row
                for row in candidates
                if row["family"] == family
                and row["valid"]
                and row["d4_support_over_sqrt_q"] > 1
            ]
        )
        == len(curve_ids)
    ]
    summary = result["summary"]
    return (
        summary["family_rows"] == len(rows)
        and summary["candidate_rows"] == len(candidates)
        and summary["control_rows"] == len(controls)
        and summary["all_support_reconstructions_valid"]
        == all(row["valid"] for row in rows)
        and summary["positive_control_compressed"] == control_compression
        and summary["promoted_explicit_barrier_families"] == promoted
        and summary["explicit_divisor_barrier_gate"]
        == (len(promoted) == len(families) and control_compression)
        and summary["rho_payload_barrier_families"] == rho_families
        and summary["rho_payload_barrier_gate"]
        == (len(rho_families) == len(families) and control_compression)
    )


def accounting_consistent(result: dict[str, Any]) -> bool:
    for row in result["rows"]:
        b_size = row["r_size"]
        for arity in (2, 3, 4):
            level = row["levels"][str(arity)]
            if level["canonical_tuple_count"] != math_comb(
                b_size + arity - 1, arity
            ):
                return False
        if (
            row["d4_support_symmetric_difference"] != 0
            or row["reduced_divisor_degree"]
            != row["levels"]["4"]["unique_point_support"]
            or row["minimum_dense_pole_degree"]
            != row["reduced_divisor_degree"]
            or row["explicit_coordinate_algebra_dimension"]
            != row["reduced_divisor_degree"]
        ):
            return False
    return True


def math_comb(left: int, right: int) -> int:
    value = 1
    for index in range(1, right + 1):
        value = value * (left - right + index) // index
    return value


def verify(
    raw_path: Path, input_override: Path | None = None
) -> dict[str, Any]:
    generator = load_generator()
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    input_path = (
        input_override
        if input_override is not None
        else Path(raw["config"]["input_result"])
    )
    checks = {
        "protocol": raw.get("protocol")
        == (
            "EXP-ECDLP-COORD-EXPANSION-001-"
            "four-sum-divisor-barrier-v1"
        ),
        "generator_hash": raw["source"][
            "four_sum_divisor_barrier_sha256"
        ]
        == generator.sha256_file(GENERATOR_PATH),
        "typed_source_hash": raw["source"]["typed_five_ec_sha256"]
        == generator.sha256_file(generator.TYPED_SOURCE),
        "input_hash": raw["source"]["input_result_sha256"]
        == generator.sha256_file(input_path),
        "summary_consistent": summary_consistent(raw),
        "accounting_consistent": accounting_consistent(raw),
        "breakthrough_claim_false": raw["summary"]["breakthrough_claim"]
        is False,
    }
    rerun = generator.run(
        input_path,
        raw["config"]["families"],
        raw["config"]["positive_control"],
    )
    raw_normalized = normalize(raw)
    rerun_normalized = normalize(rerun)
    checks["normalized_rerun_exact"] = (
        raw_normalized == rerun_normalized
    )
    return {
        "protocol": (
            "EXP-ECDLP-COORD-EXPANSION-001-"
            "four-sum-divisor-barrier-v1-verifier"
        ),
        "raw_result_sha256": generator.sha256_file(raw_path),
        "input_result_sha256": generator.sha256_file(input_path),
        "generator_sha256": generator.sha256_file(GENERATOR_PATH),
        "verifier_sha256": generator.sha256_file(SCRIPT_PATH),
        "raw_normalized_sha256": canonical_digest(raw_normalized),
        "rerun_normalized_sha256": canonical_digest(
            rerun_normalized
        ),
        "checks": checks,
        "rows_replayed": len(rerun["rows"]),
        "valid": all(checks.values()),
        "boundary": (
            "Deterministic support and accounting replay. It certifies "
            "no succinct-circuit lower bound."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("raw_result", type=Path)
    parser.add_argument("--input", type=Path)
    args = parser.parse_args()
    receipt = verify(args.raw_result, args.input)
    print(
        json.dumps(
            receipt, sort_keys=True, separators=(",", ":")
        )
    )
    return 0 if receipt["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
