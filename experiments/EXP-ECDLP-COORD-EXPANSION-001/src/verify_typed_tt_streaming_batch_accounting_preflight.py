#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve()
PRODUCER_PATH = SCRIPT_PATH.with_name("typed_tt_streaming_batch_accounting_preflight.py")


def load_producer():
    spec = importlib.util.spec_from_file_location("typed_tt_streaming_batch_verify", PRODUCER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load streaming-batch producer")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    if len(sys.argv) != 5:
        raise SystemExit("usage: verifier raw-result.json input.json materialized.json verification.json")
    raw_path, input_path, materialized_path, output_path = map(Path, sys.argv[1:])
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    producer = load_producer()
    rerun = producer.run(input_path, materialized_path, raw["config"]["families"], raw["config"]["prefix_order"])
    summary = raw.get("summary", {})
    expected_exact = raw.get("config", {}).get("expected_exact") is True
    expected_labels = ["balanced_1", "balanced_2", "balanced_4", "balanced_8", "full"]
    checks = {
        "protocol": raw.get("protocol") == "EXP-ECDLP-COORD-EXPANSION-001-typed-tt-streaming-batch-accounting-preflight-v1",
        "producer_hash": raw.get("source", {}).get("producer_sha256") == producer.sha256_file(PRODUCER_PATH),
        "streaming_hash": raw.get("source", {}).get("streaming_sha256") == producer.sha256_file(producer.STREAMING_SOURCE),
        "input_hash": raw.get("source", {}).get("input_sha256") == producer.sha256_file(input_path),
        "materialized_hash": raw.get("source", {}).get("materialized_sha256") == producer.sha256_file(materialized_path),
        "typed_five_hash": raw.get("source", {}).get("typed_five_ec_sha256") == producer.sha256_file(producer.TYPED_FIVE.SCRIPT_PATH),
        "rows": len(raw.get("rows", [])) == len(rerun.get("rows", [])) == 12,
        "result_digest": raw.get("result_digest") == rerun.get("result_digest"),
        "prefix_order": raw.get("config", {}).get("prefix_order") in {"diagonal", "lexicographic", "reverse_lexicographic"},
        "batch_specs": raw.get("config", {}).get("batch_specs") == expected_labels and all([batch["label"] for row in raw.get("rows", []) for batch in row.get("batches", [])] .count(label) == 12 for label in expected_labels),
        "expected_exactness_recorded": expected_exact == (summary.get("all_full_exact") is True),
        "exactness_reproduced": summary.get("all_full_exact") == rerun.get("summary", {}).get("all_full_exact") and summary.get("all_balanced_exact") == rerun.get("summary", {}).get("all_balanced_exact"),
        "batch_prefix_reuse": summary.get("all_batch_prefix_reuse") is True,
        "memory_reduction": summary.get("all_memory_reductions") is True,
        "direct_reference_exact": summary.get("all_full_direct_reference_exact") is True,
        "relation_bindings": summary.get("all_relation_bindings") is True,
        "relation_exact": (summary.get("all_full_relation_targets_exact") is True) == expected_exact,
        "descent_exact": (summary.get("all_full_supported_descent_targets_exact") is True) == expected_exact,
        "breakthrough_false": summary.get("breakthrough_claim") is False,
        "promotion_false": summary.get("algorithm_promotion_gate") is False,
    }
    checks["valid"] = all(checks.values())
    output_path.write_text(json.dumps({"protocol": "EXP-ECDLP-COORD-EXPANSION-001-typed-tt-streaming-batch-accounting-preflight-v1-verifier", "checks": checks, "valid": checks["valid"]}, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    return 0 if checks["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
