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
GENERATOR_PATH = SCRIPT_PATH.with_name("typed_s4_factor_geometry.py")
TIMING_KEYS = {
    "peak_rss_bytes",
    "peak_rss_bytes_after_cell",
    "total_wall_seconds",
    "wall_seconds",
}


def load_generator() -> Any:
    spec = importlib.util.spec_from_file_location(
        "typed_s4_factor_geometry_for_verification",
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
    comparisons = result["comparisons"]
    families = result["config"]["families"]
    curve_ids = {
        comparison["curve_id"] for comparison in comparisons
    }
    promoted = []
    for family in families:
        rows = [
            comparison
            for comparison in comparisons
            if comparison["family"] == family
        ]
        if (
            len(rows) == len(curve_ids)
            and all(row["all_cuts_collapse"] for row in rows)
        ):
            promoted.append(family)
    summary = result["summary"]
    semantics = all(
        cell["source"]["invalid_projective_count"] == 0
        and cell["source"]["affine_replay_mismatches"] == 0
        and cell["locator"]["zero_set_mismatches"] == 0
        and cell["locator"]["witness_count"] >= 1
        and all(
            factor["reconstruction_mismatches"] == 0
            and factor["zero_set_mismatches"] == 0
            and factor["dense_control"]["all_rank_matched"]
            and factor["dense_control"]["all_geometry_generic"]
            for factor in cell["factors"]
        )
        for cell in result["cells"]
    )
    return (
        summary["cells"] == len(result["cells"])
        and summary["matched_comparisons"] == len(comparisons)
        and summary["promoted_families"] == promoted
        and summary["positive_gate"] == (len(promoted) >= 3)
        and summary["all_semantics_valid"] == semantics
    )


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
            "typed-s4-factor-geometry-v1"
        ),
        "generator_hash": raw["source"][
            "typed_s4_factor_geometry_sha256"
        ]
        == generator.NORM.sha256_file(GENERATOR_PATH),
        "norm_source_hash": raw["source"]["typed_s4_norm_rank_sha256"]
        == generator.NORM.sha256_file(generator.NORM_SOURCE),
        "input_hash": raw["source"]["input_result_sha256"]
        == generator.NORM.sha256_file(input_path),
        "summary_consistent": summary_consistent(raw),
        "semantics_valid": bool(raw["summary"]["all_semantics_valid"]),
        "breakthrough_claim_false": raw["summary"]["breakthrough_claim"]
        is False,
    }
    rerun = generator.run(
        input_path,
        raw["config"]["families"],
        raw["config"]["a_variants"],
        raw["config"]["cuts"],
        raw["config"]["dense_controls"],
    )
    raw_normalized = normalize(raw)
    rerun_normalized = normalize(rerun)
    checks["normalized_rerun_exact"] = (
        raw_normalized == rerun_normalized
    )
    return {
        "protocol": (
            "EXP-ECDLP-COORD-EXPANSION-001-"
            "typed-s4-factor-geometry-v1-verifier"
        ),
        "raw_result_sha256": generator.NORM.sha256_file(raw_path),
        "input_result_sha256": generator.NORM.sha256_file(input_path),
        "generator_sha256": generator.NORM.sha256_file(
            GENERATOR_PATH
        ),
        "verifier_sha256": generator.NORM.sha256_file(SCRIPT_PATH),
        "raw_normalized_sha256": canonical_digest(raw_normalized),
        "rerun_normalized_sha256": canonical_digest(
            rerun_normalized
        ),
        "checks": checks,
        "cells_replayed": len(rerun["cells"]),
        "comparisons_replayed": len(rerun["comparisons"]),
        "valid": all(checks.values()),
        "boundary": (
            "Exact deterministic rerun and consistency verifier. It does "
            "not turn enumerated factor geometry into an indexed join."
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
