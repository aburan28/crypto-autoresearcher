#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
GENERATOR_PATH = SCRIPT_PATH.with_name("elliptic_net_block_zero_v2.py")
BASE_VERIFIER_PATH = SCRIPT_PATH.with_name("verify_elliptic_net_block_zero.py")
TIMING_KEYS = {"peak_rss_bytes", "peak_rss_bytes_after_family", "total_wall_seconds"}


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load prerequisite: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


GENERATOR = load_module("elliptic_net_block_zero_v2_for_verification", GENERATOR_PATH)
BASE_VERIFIER = load_module(
    "elliptic_net_block_zero_v1_for_v2_verification", BASE_VERIFIER_PATH
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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


def check_result(raw: dict[str, Any], input_path: Path) -> dict[str, bool]:
    try:
        summary_consistent = BASE_VERIFIER.summary_consistent(raw)
        tree_accounting_consistent = BASE_VERIFIER.tree_accounting_consistent(raw)
    except (KeyError, TypeError, IndexError):
        summary_consistent = False
        tree_accounting_consistent = False
    checks = {
        "protocol": raw.get("protocol")
        == "EXP-ECDLP-COORD-EXPANSION-001-elliptic-net-block-zero-v2",
        "wrapper_hash": raw.get("source", {}).get("wrapper_sha256")
        == sha256_file(GENERATOR_PATH),
        "base_generator_hash": raw.get("source", {}).get("base_generator_sha256")
        == sha256_file(GENERATOR.BASE_SOURCE),
        "input_hash": raw.get("source", {}).get("input_result_sha256")
        == sha256_file(input_path),
        "normalization_mode": raw.get("config", {}).get("normalization")
        == "affine_output_locator_with_infinity_sentinel",
        "summary_consistent": summary_consistent,
        "tree_accounting_consistent": tree_accounting_consistent,
        "semantics_valid": bool(raw["summary"]["all_semantics_valid"]),
        "controls_valid": bool(raw["summary"]["all_controls_valid"]),
        "normalization_controls_valid": bool(
            raw["summary"]["normalization_controls_valid"]
        ),
        "normalization_records_valid": bool(raw["normalization_controls"]["all_pass"]),
        "promotion_false": raw["summary"]["algorithm_promotion_gate"] is False,
        "breakthrough_false": raw["summary"]["breakthrough_claim"] is False,
    }
    return checks


def mutation_rejections(raw: dict[str, Any], input_path: Path) -> dict[str, bool]:
    mutations: dict[str, dict[str, Any]] = {}
    changed = copy.deepcopy(raw)
    changed["protocol"] = "wrong"
    mutations["protocol"] = changed
    changed = copy.deepcopy(raw)
    changed["source"]["base_generator_sha256"] = "0" * 64
    mutations["base_generator_hash"] = changed
    changed = copy.deepcopy(raw)
    changed["config"]["normalization"] = "raw_projective_locator"
    mutations["normalization_mode"] = changed
    changed = copy.deepcopy(raw)
    changed["summary"]["normalization_controls_valid"] = False
    mutations["normalization_control_flag"] = changed
    changed = copy.deepcopy(raw)
    changed["summary"]["algorithm_promotion_gate"] = True
    mutations["promotion_gate"] = changed
    changed = copy.deepcopy(raw)
    changed["rows"][0]["semantics_valid"] = False
    mutations["semantic_row"] = changed
    return {
        name: not all(check_result(candidate, input_path).values())
        for name, candidate in mutations.items()
    }


def verify(raw_path: Path, input_override: Path | None = None) -> dict[str, Any]:
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    input_path = (
        input_override
        if input_override is not None
        else Path(raw["config"]["input_result"])
    )
    rerun = GENERATOR.run(
        input_path,
        raw["config"]["families"],
        raw["config"]["length_multiplier"],
    )
    checks = check_result(raw, input_path)
    checks["normalized_rerun_exact"] = normalize(raw) == normalize(rerun)
    checks["mutation_rejections"] = all(
        mutation_rejections(raw, input_path).values()
    )
    return {
        "protocol": (
            "EXP-ECDLP-COORD-EXPANSION-001-"
            "elliptic-net-block-zero-v2-verifier"
        ),
        "raw_result_sha256": sha256_file(raw_path),
        "input_result_sha256": sha256_file(input_path),
        "generator_sha256": sha256_file(GENERATOR_PATH),
        "verifier_sha256": sha256_file(SCRIPT_PATH),
        "raw_normalized_sha256": canonical_digest(normalize(raw)),
        "rerun_normalized_sha256": canonical_digest(normalize(rerun)),
        "checks": checks,
        "mutation_rejections_by_name": mutation_rejections(raw, input_path),
        "rows_replayed": len(rerun["rows"]),
        "verified_recurrence_signals": sum(
            row["recurrence_signal"] for row in rerun["rows"]
        ),
        "valid": all(checks.values()),
        "boundary": (
            "Independent normalized-locator replay and mutation audit. "
            "It does not turn a toy recurrence signature into an ECDLP result."
        ),
    }


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("raw_result", type=Path)
    parser.add_argument("--input", type=Path)
    args = parser.parse_args()
    receipt = verify(args.raw_result, args.input)
    print(json.dumps(receipt, sort_keys=True, separators=(",", ":")))
    return 0 if receipt["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
