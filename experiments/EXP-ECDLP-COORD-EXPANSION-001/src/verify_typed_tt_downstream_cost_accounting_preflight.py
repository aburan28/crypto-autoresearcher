#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve()
PRODUCER_PATH = SCRIPT_PATH.with_name("typed_tt_downstream_cost_accounting_preflight.py")


def load_producer():
    spec = importlib.util.spec_from_file_location("typed_tt_downstream_cost_verify", PRODUCER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load downstream-cost producer")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    if len(sys.argv) != 7:
        raise SystemExit("usage: verifier raw-result.json input.json materialized.json batch.json negative-batch.json verification.json")
    raw_path, input_path, materialized_path, batch_path, negative_batch_path, output_path = map(Path, sys.argv[1:])
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    producer = load_producer()
    rerun = producer.run(input_path, materialized_path, batch_path, negative_batch_path, raw["config"]["families"])
    summary = raw.get("summary", {})
    checks = {
        "protocol": raw.get("protocol") == "EXP-ECDLP-COORD-EXPANSION-001-typed-tt-downstream-cost-accounting-preflight-v1",
        "producer_hash": raw.get("source", {}).get("producer_sha256") == producer.sha256_file(PRODUCER_PATH),
        "typed_five_hash": raw.get("source", {}).get("typed_five_ec_sha256") == producer.sha256_file(producer.TYPED_FIVE_SOURCE),
        "input_hash": raw.get("source", {}).get("input_sha256") == producer.sha256_file(input_path),
        "materialized_hash": raw.get("source", {}).get("materialized_sha256") == producer.sha256_file(materialized_path),
        "batch_hash": raw.get("source", {}).get("batch_sha256") == producer.sha256_file(batch_path),
        "negative_batch_hash": raw.get("source", {}).get("negative_batch_sha256") == producer.sha256_file(negative_batch_path),
        "rows": len(raw.get("rows", [])) == len(rerun.get("rows", [])) == 12,
        "result_digest": raw.get("result_digest") == rerun.get("result_digest"),
        "independent_public_support": summary.get("all_public_construction_matches") is True and summary.get("all_compiler_matches") is True,
        "independent_relation": summary.get("all_relation_transcripts_match") is True and summary.get("all_relation_equations_match") is True and summary.get("all_relation_solutions_match") is True and summary.get("all_relation_ranks_match") is True,
        "independent_descent": summary.get("all_descent_transcripts_match") is True and summary.get("all_descents_verified") is True,
        "candidate_binding": summary.get("all_candidate_full_exact") is True and summary.get("all_candidate_direct_reference_exact") is True,
        "negative_binding": summary.get("all_negative_direct_arithmetic_exact") is True and summary.get("all_negative_exactness_failures") is True,
        "mixed_comparison_disabled": raw.get("config", {}).get("mixed_cost_comparison") is False,
        "breakthrough_false": summary.get("breakthrough_claim") is False,
        "promotion_false": summary.get("algorithm_promotion_gate") is False,
    }
    checks["valid"] = all(checks.values())
    output_path.write_text(json.dumps({"protocol": "EXP-ECDLP-COORD-EXPANSION-001-typed-tt-downstream-cost-accounting-preflight-v1-verifier", "checks": checks, "valid": checks["valid"]}, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    return 0 if checks["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
