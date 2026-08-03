#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve()
PRODUCER_PATH = SCRIPT_PATH.with_name("typed_tt_rowspace_scale_probe.py")


def load_producer():
    spec = importlib.util.spec_from_file_location("typed_tt_rowspace_scale_verify", PRODUCER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load row-space scale probe")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit("usage: verifier raw-result.json verification.json")
    raw_path, output_path = map(Path, sys.argv[1:])
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    producer = load_producer()
    input_path = raw_path.with_name("input-fixture.json")
    config = raw["config"]
    rerun = producer.run(input_path, config["families"], config["sample_limit"], config["target_budget_factor"], config["max_prefixes"])
    summary = raw.get("summary", {})
    checks = {
        "protocol": raw.get("protocol") == "EXP-ECDLP-COORD-EXPANSION-001-typed-tt-rowspace-scale-probe-v1",
        "producer_hash": raw.get("source", {}).get("producer_sha256") == producer.sha256_file(PRODUCER_PATH),
        "rowspace_hash": raw.get("source", {}).get("rowspace_sha256") == producer.sha256_file(producer.ROWSPACE_SOURCE),
        "input_hash": raw.get("source", {}).get("input_sha256") == producer.sha256_file(input_path),
        "result_digest": raw.get("result_digest") == rerun.get("result_digest"),
        "row_count": len(raw.get("rows", [])) == 4,
        "sample_mismatch_observed": summary.get("all_sample_matches") is False and summary.get("max_sample_mismatches", 0) > 0,
        "prefix_budget_bound": summary.get("all_prefix_bounded") is True,
        "no_promotion": summary.get("breakthrough_claim") is False and summary.get("algorithm_promotion_gate") is False,
    }
    checks["valid"] = all(checks.values())
    output_path.write_text(json.dumps({"protocol": "EXP-ECDLP-COORD-EXPANSION-001-typed-tt-rowspace-scale-probe-v1-verifier", "checks": checks, "valid": checks["valid"]}, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    return 0 if checks["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
