#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve()
PRODUCER_PATH = SCRIPT_PATH.with_name("typed_tt_fresh_witness_relation_audit.py")


def load_producer():
    spec = importlib.util.spec_from_file_location("typed_tt_fresh_witness_verify", PRODUCER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load fresh-witness producer")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    if len(sys.argv) != 5:
        raise SystemExit("usage: verifier full.json truncated.json input.json verification.json")
    full_path, truncated_path, input_path, output_path = map(Path, sys.argv[1:])
    full = json.loads(full_path.read_text(encoding="utf-8"))
    truncated = json.loads(truncated_path.read_text(encoding="utf-8"))
    producer = load_producer()
    families = full["config"]["families"]
    target_budget_factor = full["config"]["target_budget_factor"]
    rerun_full = producer.run(input_path, families, "full", target_budget_factor)
    rerun_truncated = producer.run(input_path, families, "truncated", target_budget_factor)
    full_summary = full.get("summary", {})
    truncated_summary = truncated.get("summary", {})
    full_rows = full.get("rows", [])
    truncated_rows = truncated.get("rows", [])
    checks = {
        "full_protocol": full.get("protocol") == "EXP-ECDLP-COORD-EXPANSION-001-typed-tt-fresh-witness-relation-audit-v1",
        "truncated_protocol": truncated.get("protocol") == "EXP-ECDLP-COORD-EXPANSION-001-typed-tt-fresh-witness-relation-audit-v1",
        "producer_hash": full.get("source", {}).get("producer_sha256") == producer.sha256_file(PRODUCER_PATH),
        "streaming_hash": full.get("source", {}).get("streaming_sha256") == producer.sha256_file(producer.STREAMING_SOURCE),
        "typed_five_hash": full.get("source", {}).get("typed_five_ec_sha256") == producer.sha256_file(producer.TYPED_FIVE_SOURCE),
        "input_hash": full.get("source", {}).get("input_sha256") == producer.sha256_file(input_path),
        "config_match": full.get("config", {}).get("mode") == "full" and truncated.get("config", {}).get("mode") == "truncated" and full.get("config", {}).get("families") == families and truncated.get("config", {}).get("families") == families,
        "row_count": len(full_rows) == len(truncated_rows) == len(families) * 3,
        "full_rerun_digest": full.get("result_digest") == rerun_full.get("result_digest"),
        "truncated_rerun_digest": truncated.get("result_digest") == rerun_truncated.get("result_digest"),
        "full_witnesses": full_summary.get("all_witnesses_valid") is True and full_summary.get("all_supports_match") is True,
        "full_tensor_control": full_summary.get("all_candidate_full_tensor_mode") is True and full_summary.get("mean_candidate_query_fraction_of_full_tensor") == 1.0,
        "full_no_rank_promotion": full_summary.get("breakthrough_claim") is False and full_summary.get("algorithm_promotion_gate") is False,
        "truncated_witnesses": truncated_summary.get("all_witnesses_valid") is True,
        "truncated_negative": truncated_summary.get("all_candidate_full_tensor_mode") is False and truncated_summary.get("all_supports_match") is False and truncated_summary.get("all_candidate_full_rank") is False,
        "truncated_no_promotion": truncated_summary.get("breakthrough_claim") is False and truncated_summary.get("algorithm_promotion_gate") is False,
    }
    checks["valid"] = all(checks.values())
    output_path.write_text(json.dumps({"protocol": "EXP-ECDLP-COORD-EXPANSION-001-typed-tt-fresh-witness-relation-audit-v1-verifier", "checks": checks, "valid": checks["valid"]}, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    return 0 if checks["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
