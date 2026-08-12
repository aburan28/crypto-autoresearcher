#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve()
PRODUCER_PATH = SCRIPT_PATH.with_name("typed_tt_relation_descent_binding_preflight.py")


def load_producer():
    spec = importlib.util.spec_from_file_location("typed_tt_relation_descent_binding_verify", PRODUCER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load binding producer")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    if len(sys.argv) != 5:
        raise SystemExit("usage: verifier raw-result.json input.json adaptive-result.json verification.json")
    raw_path, input_path, adaptive_path, output_path = map(Path, sys.argv[1:])
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    producer = load_producer()
    rerun = producer.run(input_path, adaptive_path, raw["config"]["families"])
    summary = raw.get("summary", {})
    rerun_summary = rerun.get("summary", {})
    checks = {
        "protocol": raw.get("protocol") == "EXP-ECDLP-COORD-EXPANSION-001-typed-tt-relation-descent-binding-preflight-v1",
        "input_hash": raw.get("source", {}).get("input_sha256") == producer.sha256_file(input_path),
        "adaptive_hash": raw.get("source", {}).get("adaptive_result_sha256") == producer.sha256_file(adaptive_path),
        "rows": len(raw.get("rows", [])) == len(rerun.get("rows", [])) == 12,
        "result_digest": raw.get("result_digest") == rerun.get("result_digest"),
        "relation_target_bindings": summary.get("all_relation_target_bindings") is True and summary.get("all_relation_target_bindings") == rerun_summary.get("all_relation_target_bindings"),
        "held_out_target_bindings": summary.get("all_held_out_target_bindings") is True and summary.get("all_held_out_target_bindings") == rerun_summary.get("all_held_out_target_bindings"),
        "relation_witnesses": summary.get("all_relation_witnesses_present") is True and summary.get("all_relation_witnesses_present") == rerun_summary.get("all_relation_witnesses_present"),
        "relation_exact": summary.get("all_relation_targets_exact") is True and summary.get("all_relation_targets_exact") == rerun_summary.get("all_relation_targets_exact"),
        "descent_exact": summary.get("all_supported_descent_targets_exact") is True and summary.get("all_supported_descent_targets_exact") == rerun_summary.get("all_supported_descent_targets_exact"),
        "descent_replayed": summary.get("all_supported_descent_targets_replayed") is True and summary.get("all_supported_descent_targets_replayed") == rerun_summary.get("all_supported_descent_targets_replayed"),
        "breakthrough_false": summary.get("breakthrough_claim") is False,
        "promotion_false": summary.get("algorithm_promotion_gate") is False,
    }
    checks["valid"] = all(checks.values())
    output_path.write_text(json.dumps({"protocol": "EXP-ECDLP-COORD-EXPANSION-001-typed-tt-relation-descent-binding-preflight-v1-verifier", "checks": checks, "valid": checks["valid"]}, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    return 0 if checks["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
