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
GENERATOR_PATH = SCRIPT_PATH.with_name("typed_aligned_batch_mitm.py")
TIMING_KEYS = {
    "peak_rss_bytes",
    "peak_rss_bytes_after_family",
    "total_wall_seconds",
}


def load_generator() -> Any:
    spec = importlib.util.spec_from_file_location(
        "typed_aligned_batch_mitm_for_verification",
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
    interior_signals = []
    one_instance = []
    semantics = True
    for row in result["rows"]:
        for cohort in row["cohorts"]:
            aligned = cohort["aligned"]
            random = cohort["random"]
            target_count = cohort["target_count"]
            semantics = semantics and all(
                cohort[mode]["scan"]["replay_mismatches"] == 0
                and cohort[mode]["scan"]["equation_mismatches"] == 0
                and cohort[mode]["scan"]["covered_targets"]
                <= target_count
                and cohort[mode]["scan"]["quotient_rank"]
                <= cohort[mode]["scan"]["quotient_width"]
                for mode in ("aligned", "random")
            )
            semantics = semantics and (
                aligned["keys"]["target_records"]
                == aligned["keys"]["theoretical_record_bound"]
                and random["keys"]["target_records"]
                == random["keys"]["theoretical_record_bound"]
            )
            exponent = cohort["target_exponent"]
            if 0.5 < exponent < 1.5:
                interior_signals.append(
                    aligned["keys"]["target_records"]
                    <= aligned["keys"]["theoretical_record_bound"]
                    and cohort["comparison"][
                        "aligned_over_random_target_records"
                    ]
                    <= 2 / min(row["a_size"], row["r_size"])
                    and aligned["scan"]["covered_target_fraction"]
                    >= 0.8
                    * random["scan"]["covered_target_fraction"]
                )
            one_instance.append(
                aligned["scan"]["full_quotient_rank"]
                and (
                    aligned["keys"]["ops"]["group_operations"]
                    + aligned["scan"]["query_ops"]["group_operations"]
                )
                < row["q"] ** 0.5
            )
    summary = result["summary"]
    return (
        summary["family_rows"] == len(result["rows"])
        and summary["cohorts"]
        == sum(len(row["cohorts"]) for row in result["rows"])
        and summary["many_target_structural_gate"]
        == (bool(interior_signals) and all(interior_signals))
        and summary["one_instance_relation_gate"]
        == (bool(one_instance) and all(one_instance))
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
            "typed-aligned-batch-mitm-v1"
        ),
        "generator_hash": raw["source"][
            "typed_aligned_batch_mitm_sha256"
        ]
        == generator.TYPED.sha256_file(GENERATOR_PATH),
        "typed_source_hash": raw["source"]["typed_five_ec_sha256"]
        == generator.TYPED.sha256_file(generator.TYPED_SOURCE),
        "input_hash": raw["source"]["input_result_sha256"]
        == generator.TYPED.sha256_file(input_path),
        "summary_consistent": summary_consistent(raw),
        "semantics_valid": bool(raw["summary"]["all_semantics_valid"]),
        "breakthrough_claim_false": raw["summary"]["breakthrough_claim"]
        is False,
    }
    rerun = generator.run(
        input_path,
        raw["config"]["families"],
        raw["config"]["target_exponents"],
    )
    raw_normalized = normalize(raw)
    rerun_normalized = normalize(rerun)
    checks["normalized_rerun_exact"] = (
        raw_normalized == rerun_normalized
    )
    return {
        "protocol": (
            "EXP-ECDLP-COORD-EXPANSION-001-"
            "typed-aligned-batch-mitm-v1-verifier"
        ),
        "raw_result_sha256": generator.TYPED.sha256_file(raw_path),
        "input_result_sha256": generator.TYPED.sha256_file(input_path),
        "generator_sha256": generator.TYPED.sha256_file(
            GENERATOR_PATH
        ),
        "verifier_sha256": generator.TYPED.sha256_file(SCRIPT_PATH),
        "raw_normalized_sha256": canonical_digest(raw_normalized),
        "rerun_normalized_sha256": canonical_digest(
            rerun_normalized
        ),
        "checks": checks,
        "family_rows_replayed": len(rerun["rows"]),
        "cohorts_replayed": sum(
            len(row["cohorts"]) for row in rerun["rows"]
        ),
        "valid": all(checks.values()),
        "boundary": (
            "Exact deterministic rerun and consistency verifier. It does "
            "not promote aligned target coverage into an ECDLP break."
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
