#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve()
PRODUCER_PATH = SCRIPT_PATH.with_name("typed_tt_adversarial_order_control_preflight.py")


def load_producer():
    spec = importlib.util.spec_from_file_location("typed_tt_adversarial_order_control_verify", PRODUCER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load order-control producer")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    if len(sys.argv) != 4:
        raise SystemExit("usage: verifier raw-result.json input.json verification.json")
    raw_path, input_path, output_path = map(Path, sys.argv[1:])
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    producer = load_producer()
    mode = raw["config"]["prefix_order"]
    families = raw["config"]["families"]
    rerun = producer.run(input_path, families, mode)
    checks = {
        "protocol": raw.get("protocol") == "EXP-ECDLP-COORD-EXPANSION-001-typed-tt-adversarial-order-control-preflight-v1",
        "input_hash": raw.get("source", {}).get("input_sha256") == rerun.get("source", {}).get("input_sha256"),
        "order": mode in {"lexicographic", "reverse_lexicographic"},
        "row_count": len(raw.get("rows", [])) == len(rerun.get("rows", [])) == 12,
        "result_digest": raw.get("result_digest") == rerun.get("result_digest"),
        "adaptive": raw.get("summary", {}).get("all_adaptive") is True,
        "exactness_recorded": raw.get("summary", {}).get("all_exact_validation") == rerun.get("summary", {}).get("all_exact_validation"),
        "query_counts": raw.get("summary", {}).get("all_construction_query_counts_match") is True,
        "non_enumerative_construction": raw.get("summary", {}).get("all_source_paths_non_enumerative") is True,
        "breakthrough_false": raw.get("summary", {}).get("breakthrough_claim") is False,
        "promotion_false": raw.get("summary", {}).get("algorithm_promotion_gate") is False,
    }
    checks["valid"] = all(checks.values())
    output_path.write_text(json.dumps({"protocol": "EXP-ECDLP-COORD-EXPANSION-001-typed-tt-adversarial-order-control-preflight-v1-verifier", "checks": checks, "valid": checks["valid"]}, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    return 0 if checks["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
