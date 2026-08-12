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
GENERATOR_PATH = SCRIPT_PATH.with_name("elliptic_net_block_zero.py")
TIMING_KEYS = {
    "peak_rss_bytes",
    "peak_rss_bytes_after_family",
    "total_wall_seconds",
}


def load_generator() -> Any:
    spec = importlib.util.spec_from_file_location(
        "elliptic_net_block_zero_for_verification",
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
    rows = result["rows"]
    curve_ids = sorted({row["curve_id"] for row in rows})
    families = result["config"]["families"]
    promoted = [
        family
        for family in families
        if len(
            [
                row
                for row in rows
                if row["family"] == family and row["recurrence_signal"]
            ]
        )
        == len(curve_ids)
    ]
    controls_valid = all(
        record["planted_linear"]["recovered_order"]
        <= record["planted_linear"]["planted_order"]
        and record["planted_linear"]["recovered_violations"] == 0
        and record["planted_linear"]["planted_violations"] == 0
        and record["planted_linear"]["train_test"]["held_out_exact"]
        and record["elliptic_divisibility"]["ward_violations"] == 0
        and record["elliptic_divisibility"]["somos4"]["exact"]
        and not record["deterministic_random"]["somos4"]["exact"]
        for record in result["controls"].values()
    )
    semantics_valid = all(
        row["semantics_valid"] and row["planted_descent_replay"]
        for row in rows
    )
    summary = result["summary"]
    return (
        summary["family_rows"] == len(rows)
        and summary["curve_count"] == len(curve_ids)
        and summary["promoted_families"] == promoted
        and summary["recurrence_signal_gate"]
        == (len(promoted) >= 3)
        and summary["constructible_implicit_state"] is False
        and summary["algorithm_promotion_gate"] is False
        and summary["all_controls_valid"] == controls_valid
        and summary["all_semantics_valid"] == semantics_valid
    )


def tree_accounting_consistent(result: dict[str, Any]) -> bool:
    for row in result["rows"]:
        length = row["sequence_length"]
        leaves = row["canonical_tuple_count"]
        for variant in row["variants"].values():
            source = variant["source"]
            if (
                source["a_count"] != length
                or source["canonical_tuple_count"] != leaves
                or source["locator_evaluations"] != 2 * length * leaves
                or source["rcb_calls"] != 4 * length * leaves
            ):
                return False
            for tree in variant["trees"].values():
                expected_elements = sum(
                    level["node_count"] * length
                    for level in tree["levels"]
                )
                if (
                    tree["leaf_count"] != leaves
                    or tree["materialized_field_elements"]
                    != expected_elements
                    or tree["root"]["full_recurrence_violations"] != 0
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
        == (
            "EXP-ECDLP-COORD-EXPANSION-001-"
            "elliptic-net-block-zero-v1"
        ),
        "generator_hash": raw["source"][
            "elliptic_net_block_zero_sha256"
        ]
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
        "tree_accounting_consistent": tree_accounting_consistent(raw),
        "semantics_valid": bool(raw["summary"]["all_semantics_valid"]),
        "controls_valid": bool(raw["summary"]["all_controls_valid"]),
        "breakthrough_claim_false": raw["summary"]["breakthrough_claim"]
        is False,
    }
    rerun = generator.run(
        input_path,
        raw["config"]["families"],
        raw["config"]["length_multiplier"],
    )
    raw_normalized = normalize(raw)
    rerun_normalized = normalize(rerun)
    checks["normalized_rerun_exact"] = (
        raw_normalized == rerun_normalized
    )
    return {
        "protocol": (
            "EXP-ECDLP-COORD-EXPANSION-001-"
            "elliptic-net-block-zero-v1-verifier"
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
            "Exact deterministic rerun and accounting verifier. It does "
            "not turn a toy recurrence signature into an ECDLP result."
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
