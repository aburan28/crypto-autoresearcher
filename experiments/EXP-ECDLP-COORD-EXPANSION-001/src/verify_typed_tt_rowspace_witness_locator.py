#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve()
PRODUCER_PATH = SCRIPT_PATH.with_name("typed_tt_rowspace_witness_locator.py")


def load_producer():
    spec = importlib.util.spec_from_file_location("typed_tt_rowspace_witness_verify", PRODUCER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load row-space locator producer")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    if len(sys.argv) != 5:
        raise SystemExit("usage: verifier per-target.json reuse.json input.json verification.json")
    per_target_path, reuse_path, input_path, output_path = map(Path, sys.argv[1:])
    per_target = json.loads(per_target_path.read_text(encoding="utf-8"))
    reuse = json.loads(reuse_path.read_text(encoding="utf-8"))
    producer = load_producer()
    families = per_target["config"]["families"]
    target_budget_factor = per_target["config"]["target_budget_factor"]
    rerun_per_target = producer.run(input_path, families, "per_target", target_budget_factor)
    rerun_reuse = producer.run(input_path, families, "reuse", target_budget_factor)
    per_summary = per_target.get("summary", {})
    reuse_summary = reuse.get("summary", {})
    per_rows = per_target.get("rows", [])
    reuse_rows = reuse.get("rows", [])
    reuse_not_worse = all(
        reuse_row["candidate_source_ops"]["unique_queries"] <= per_row["candidate_source_ops"]["unique_queries"]
        for per_row, reuse_row in zip(per_rows, reuse_rows)
    )
    reuse_strict = any(
        reuse_row["candidate_source_ops"]["unique_queries"] < per_row["candidate_source_ops"]["unique_queries"]
        for per_row, reuse_row in zip(per_rows, reuse_rows)
    )
    checks = {
        "per_target_protocol": per_target.get("protocol") == "EXP-ECDLP-COORD-EXPANSION-001-typed-tt-rowspace-witness-locator-v1",
        "reuse_protocol": reuse.get("protocol") == "EXP-ECDLP-COORD-EXPANSION-001-typed-tt-rowspace-witness-locator-v1",
        "producer_hash": per_target.get("source", {}).get("producer_sha256") == producer.sha256_file(PRODUCER_PATH),
        "adaptive_hash": per_target.get("source", {}).get("adaptive_sha256") == producer.sha256_file(producer.ADAPTIVE_SOURCE),
        "streaming_hash": per_target.get("source", {}).get("streaming_sha256") == producer.sha256_file(producer.STREAMING_SOURCE),
        "typed_five_hash": per_target.get("source", {}).get("typed_five_ec_sha256") == producer.sha256_file(producer.TYPED_FIVE_SOURCE),
        "input_hash": per_target.get("source", {}).get("input_sha256") == producer.sha256_file(input_path),
        "mode_binding": per_target.get("config", {}).get("mode") == "per_target" and reuse.get("config", {}).get("mode") == "reuse",
        "row_count": len(per_rows) == len(reuse_rows) == len(families) * 3,
        "per_target_rerun_digest": per_target.get("result_digest") == rerun_per_target.get("result_digest"),
        "reuse_rerun_digest": reuse.get("result_digest") == rerun_reuse.get("result_digest"),
        "per_target_witnesses": per_summary.get("all_candidate_witnesses_valid") is True and per_summary.get("all_per_target_exact") is True,
        "per_target_support": per_summary.get("all_supports_match") is True,
        "reuse_witnesses": reuse_summary.get("all_candidate_witnesses_valid") is True,
        "reuse_support": reuse_summary.get("all_supports_match") is True,
        "reuse_query_savings": reuse_not_worse and reuse_strict,
        "suffix_reconstruction_explicit": per_summary.get("mean_candidate_predicted_entries_fraction") == 1.0 and reuse_summary.get("mean_candidate_predicted_entries_fraction") == 1.0,
        "no_promotion": per_summary.get("breakthrough_claim") is False and per_summary.get("algorithm_promotion_gate") is False and reuse_summary.get("breakthrough_claim") is False and reuse_summary.get("algorithm_promotion_gate") is False,
    }
    checks["valid"] = all(checks.values())
    output_path.write_text(json.dumps({"protocol": "EXP-ECDLP-COORD-EXPANSION-001-typed-tt-rowspace-witness-locator-v1-verifier", "checks": checks, "valid": checks["valid"]}, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    return 0 if checks["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
