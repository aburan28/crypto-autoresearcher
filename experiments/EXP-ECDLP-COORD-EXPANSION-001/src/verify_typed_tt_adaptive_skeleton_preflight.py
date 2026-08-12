#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
PRODUCER_PATH = SCRIPT_PATH.with_name("typed_tt_adaptive_skeleton_preflight.py")


def load() -> Any:
    spec = importlib.util.spec_from_file_location("typed_tt_adaptive_verify", PRODUCER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load adaptive producer")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check(raw: dict[str, Any], input_path: Path) -> dict[str, Any]:
    producer = load()
    checks = {
        "protocol": raw.get("protocol") == "EXP-ECDLP-COORD-EXPANSION-001-typed-tt-adaptive-skeleton-preflight-v1",
        "input_hash": raw.get("source", {}).get("input_sha256") == producer.sha256_file(input_path),
        "no_rank_budget": raw.get("config", {}).get("rank_budget_input") is False,
        "adaptive": raw.get("summary", {}).get("all_adaptive") is True,
        "non_enumerative_construction": raw.get("summary", {}).get("all_source_paths_non_enumerative") is True,
        "query_counts": raw.get("summary", {}).get("all_construction_query_counts_match") is True,
        "exact_validation": raw.get("summary", {}).get("all_exact_validation") is True,
        "promotion_false": raw.get("summary", {}).get("algorithm_promotion_gate") is False,
        "breakthrough_false": raw.get("summary", {}).get("breakthrough_claim") is False,
        "rows": len(raw.get("rows", [])) == 12,
    }
    rerun = producer.run(input_path, raw.get("config", {}).get("families", []))
    checks["producer_rerun_exact"] = rerun["result_digest"] == raw.get("result_digest")
    checks["valid"] = all(checks.values())
    return {"protocol": "EXP-ECDLP-COORD-EXPANSION-001-typed-tt-adaptive-skeleton-preflight-v1-verifier", "checks": checks, "valid": checks["valid"]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("result", type=Path)
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    raw = json.loads(args.result.read_text(encoding="utf-8"))
    print(json.dumps(check(raw, args.input), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
