#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve()
PRODUCER_PATH = SCRIPT_PATH.with_name("typed_tt_circuit_native_accounting_preflight.py")


def load_producer():
    spec = importlib.util.spec_from_file_location("typed_tt_circuit_native_verify", PRODUCER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load circuit-native producer")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    if len(sys.argv) != 5:
        raise SystemExit("usage: verifier raw-result.json input.json baseline.json verification.json")
    raw_path, input_path, baseline_path, output_path = map(Path, sys.argv[1:])
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    producer = load_producer()
    rerun = producer.run(input_path, baseline_path, raw["config"]["families"], raw["config"]["prefix_order"])
    summary = raw.get("summary", {})
    checks = {
        "protocol": raw.get("protocol") == "EXP-ECDLP-COORD-EXPANSION-001-typed-tt-circuit-native-accounting-preflight-v1",
        "input_hash": raw.get("source", {}).get("input_sha256") == producer.sha256_file(input_path),
        "baseline_hash": raw.get("source", {}).get("adaptive_baseline_sha256") == producer.sha256_file(baseline_path),
        "typed_five_hash": raw.get("source", {}).get("typed_five_ec_sha256") == producer.sha256_file(producer.TYPED_FIVE.SCRIPT_PATH),
        "rows": len(raw.get("rows", [])) == len(rerun.get("rows", [])) == 12,
        "result_digest": raw.get("result_digest") == rerun.get("result_digest"),
        "prefix_order": raw.get("config", {}).get("prefix_order") in {"diagonal", "lexicographic", "reverse_lexicographic"},
        "expected_exactness_recorded": raw.get("config", {}).get("expected_exact") == (raw.get("summary", {}).get("all_exact_validation") is True),
        "exactness_reproduced": raw.get("summary", {}).get("all_exact_validation") == rerun.get("summary", {}).get("all_exact_validation"),
        "adaptive": summary.get("all_adaptive") is True,
        "exact_validation": (summary.get("all_exact_validation") is True) == (raw.get("config", {}).get("expected_exact") is True),
        "advice_target_independent": summary.get("all_fixed_curve_advice_target_independent") is True,
        "counter_paths": summary.get("all_counter_paths_present") is True,
        "direct_reference_exact": summary.get("all_direct_reference_exact") is True,
        "relation_bindings": summary.get("all_relation_bindings") is True,
        "supported_descent_exact": (summary.get("all_supported_descent_exact") is True) == (raw.get("config", {}).get("expected_exact") is True),
        "sealed_baseline_matches": (summary.get("all_sealed_baseline_matches") is True) == (raw.get("config", {}).get("expected_exact") is True),
        "charged_win": summary.get("rows_with_charged_point_add_win", 0) > 0,
        "rho_references": all(row.get("rho_reference", {}).get("status") == "PASS" for row in raw.get("rows", [])),
        "breakthrough_false": summary.get("breakthrough_claim") is False,
        "promotion_false": summary.get("algorithm_promotion_gate") is False,
    }
    checks["valid"] = all(checks.values())
    output_path.write_text(json.dumps({"protocol": "EXP-ECDLP-COORD-EXPANSION-001-typed-tt-circuit-native-accounting-preflight-v1-verifier", "checks": checks, "valid": checks["valid"]}, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    return 0 if checks["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
