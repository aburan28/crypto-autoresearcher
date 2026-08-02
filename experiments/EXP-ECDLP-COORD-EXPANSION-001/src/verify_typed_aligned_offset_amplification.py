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
GENERATOR_PATH = SCRIPT_PATH.with_name("typed_aligned_offset_amplification.py")
TIMING_KEYS = {"peak_rss_bytes", "peak_rss_bytes_after_family", "total_wall_seconds"}


def load_generator() -> Any:
    spec = importlib.util.spec_from_file_location("offset_amplification_for_verification", GENERATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load generator: {GENERATOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def digest(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def normalize(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: normalize(item) for key, item in value.items() if key not in TIMING_KEYS}
    if isinstance(value, list):
        return [normalize(item) for item in value]
    return value


def consistency(raw: dict[str, Any]) -> bool:
    for row in raw["rows"]:
        for cohort in row["cohorts"]:
            for cell in cohort["offset_counts"].values():
                aggregate = cell["aggregate"]
                random = cell["random_control"]
                if not aggregate["semantics_valid"] or not random["semantics_valid"]:
                    return False
                if aggregate["target_count"] != sum(
                    item["scan"]["covered_targets"] * 0 + cohort["target_count"]
                    for item in cell["offsets"]
                ):
                    return False
                if aggregate["covered_targets"] > aggregate["target_count"]:
                    return False
                if random["covered_targets"] > random["target_count"]:
                    return False
                if cell["comparison"]["coverage_gate"] != (
                    aggregate["covered_fraction"] >= 0.8 * random["covered_fraction"]
                ):
                    return False
    return True


def verify(raw_path: Path, input_override: Path | None = None) -> dict[str, Any]:
    generator = load_generator()
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    input_path = input_override if input_override is not None else Path(raw["config"]["input_result"])
    checks = {
        "protocol": raw.get("protocol") == "EXP-ECDLP-COORD-EXPANSION-001-typed-aligned-offset-amplification-v1",
        "generator_hash": raw["source"]["typed_aligned_offset_amplification_sha256"] == generator.ALIGNED.TYPED.sha256_file(GENERATOR_PATH),
        "aligned_source_hash": raw["source"]["typed_aligned_batch_mitm_sha256"] == generator.ALIGNED.TYPED.sha256_file(generator.ALIGNED_PATH),
        "input_hash": raw["source"]["input_result_sha256"] == generator.ALIGNED.TYPED.sha256_file(input_path),
        "config": raw["config"]["offset_counts"] == sorted(set(raw["config"]["offset_counts"])) and all(value > 0 for value in raw["config"]["offset_counts"]),
        "consistency": consistency(raw),
        "breakthrough_claim_false": raw["summary"]["breakthrough_claim"] is False,
    }
    rerun = generator.run(input_path, raw["config"]["families"], raw["config"]["target_exponents"], raw["config"]["offset_counts"])
    normalized = normalize(raw)
    rerun_normalized = normalize(rerun)
    checks["normalized_rerun_exact"] = normalized == rerun_normalized
    return {
        "protocol": "EXP-ECDLP-COORD-EXPANSION-001-typed-aligned-offset-amplification-verifier",
        "raw_result_sha256": generator.ALIGNED.TYPED.sha256_file(raw_path),
        "input_result_sha256": generator.ALIGNED.TYPED.sha256_file(input_path),
        "generator_sha256": generator.ALIGNED.TYPED.sha256_file(GENERATOR_PATH),
        "verifier_sha256": generator.ALIGNED.TYPED.sha256_file(SCRIPT_PATH),
        "raw_normalized_sha256": digest(normalized),
        "rerun_normalized_sha256": digest(rerun_normalized),
        "checks": checks,
        "family_rows_replayed": len(rerun.get("rows", [])),
        "cells_replayed": sum(len(cohort["offset_counts"]) for row in rerun.get("rows", []) for cohort in row.get("cohorts", [])),
        "valid": all(checks.values()),
        "boundary": "Independent deterministic replay and cost/coverage consistency; no generic ECDLP claim.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("raw_result", type=Path)
    parser.add_argument("--input", type=Path)
    args = parser.parse_args()
    receipt = verify(args.raw_result, args.input)
    print(json.dumps(receipt, sort_keys=True, separators=(",", ":")))
    return 0 if receipt["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
