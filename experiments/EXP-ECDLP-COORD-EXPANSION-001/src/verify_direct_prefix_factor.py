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
GENERATOR_PATH = SCRIPT_PATH.with_name("direct_prefix_factor.py")
TIMING_KEYS = {
    "peak_rss_bytes",
    "peak_rss_bytes_after_family",
    "total_wall_seconds",
}


def load_generator() -> Any:
    spec = importlib.util.spec_from_file_location(
        "direct_prefix_factor_for_verification", GENERATOR_PATH
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
    controls = result["controls"]
    controls_valid = (
        controls["cubic_reduces_to_zero"]
        and controls["symbolic_rcb_matches_numeric"]
        and controls["symbolic_rcb_degrees"] == [2, 2, 2]
    )
    factors_valid = all(
        row["valid"]
        and [cut["basis_dimension"] for cut in row["cuts"]] == [48, 24]
        and all(
            target["factor_mismatches"] == 0
            and target["component_mismatches"] == 0
            and target["zero_set_mismatches"] == 0
            and target["factor_digest"] == target["exact_digest"]
            for cut in row["cuts"]
            for target in cut["targets"].values()
        )
        for row in result["rows"]
    )
    summary = result["summary"]
    return (
        summary["family_rows"] == len(result["rows"])
        and summary["all_controls_valid"] == controls_valid
        and summary["all_factorizations_valid"] == factors_valid
        and summary["direct_factor_gate"] == factors_valid
        and summary["zero_index_constructed"] is False
        and summary["algorithm_promotion_gate"] is False
    )


def accounting_consistent(result: dict[str, Any]) -> bool:
    for row in result["rows"]:
        for cut in row["cuts"]:
            expected_suffix = row["r_size"] ** (5 - cut["cut"])
            if (
                cut["suffix_count"] != expected_suffix
                or cut["basis_dimension"] != 3 * cut["degree"]
                or cut["target_independent_advice_field_elements"]
                != 4 * expected_suffix * cut["basis_dimension"]
            ):
                return False
            for target in cut["targets"].values():
                if (
                    target["target_dependent_advice_field_elements"]
                    != expected_suffix * cut["basis_dimension"]
                    or target["target_specialization_multiplications"]
                    != 4 * expected_suffix * cut["basis_dimension"]
                    or target["pair_verifications"]
                    != cut["prefix_count"] * cut["suffix_count"]
                ):
                    return False
    return True


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
        == "EXP-ECDLP-COORD-EXPANSION-001-direct-prefix-factor-v1",
        "generator_hash": raw["source"]["direct_prefix_factor_sha256"]
        == generator.sha256_file(GENERATOR_PATH),
        "norm_source_hash": raw["source"][
            "typed_s4_norm_rank_sha256"
        ]
        == generator.sha256_file(generator.NORM_SOURCE),
        "typed_source_hash": raw["source"]["typed_five_ec_sha256"]
        == generator.sha256_file(generator.NORM.TYPED_EC_SOURCE),
        "tt_source_hash": raw["source"]["tt_norm_rank_sha256"]
        == generator.sha256_file(generator.NORM.TT_SOURCE),
        "input_hash": raw["source"]["input_result_sha256"]
        == generator.sha256_file(input_path),
        "summary_consistent": summary_consistent(raw),
        "accounting_consistent": accounting_consistent(raw),
        "breakthrough_claim_false": raw["summary"]["breakthrough_claim"]
        is False,
    }
    rerun = generator.run(input_path, raw["config"]["families"])
    raw_normalized = normalize(raw)
    rerun_normalized = normalize(rerun)
    checks["normalized_rerun_exact"] = (
        raw_normalized == rerun_normalized
    )
    return {
        "protocol": (
            "EXP-ECDLP-COORD-EXPANSION-001-"
            "direct-prefix-factor-v1-verifier"
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
            "Exact deterministic factor and accounting replay. It does "
            "not provide a zero-reporting algorithm."
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
