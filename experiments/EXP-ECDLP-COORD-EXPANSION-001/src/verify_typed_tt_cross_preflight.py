#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
PRODUCER_PATH = SCRIPT_PATH.with_name("typed_tt_cross_preflight.py")


def load() -> Any:
    spec = importlib.util.spec_from_file_location("typed_tt_cross_preflight_verify", PRODUCER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load cross producer")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check(raw: dict[str, Any], input_path: Path, rank_path: Path) -> dict[str, Any]:
    producer = load()
    checks = {
        "protocol": raw.get("protocol") == "EXP-ECDLP-COORD-EXPANSION-001-typed-tt-cross-preflight-v1",
        "input_hash": raw.get("source", {}).get("input_sha256") == producer.sha256_file(input_path),
        "rank_hash": raw.get("source", {}).get("rank_oracle_sha256") == producer.sha256_file(rank_path),
        "non_enumerative": raw.get("config", {}).get("source_tuple_enumeration") is False and raw.get("summary", {}).get("all_non_enumerative") is True,
        "promotion_false": raw.get("summary", {}).get("algorithm_promotion_gate") is False,
        "breakthrough_false": raw.get("summary", {}).get("breakthrough_claim") is False,
        "negative_failure_observed": raw.get("summary", {}).get("all_holdouts_exact") is False and raw.get("summary", {}).get("all_rows_have_cross_failure") is True,
        "full_query_observed": raw.get("summary", {}).get("query_work_below_full_tensor") is False,
        "rows": len(raw.get("rows", [])) == 12,
    }
    rerun = producer.run(input_path, rank_path, raw.get("config", {}).get("families", []))
    checks["producer_rerun_exact"] = rerun["result_digest"] == raw.get("result_digest")
    checks["valid"] = all(checks.values())
    return {"protocol": "EXP-ECDLP-COORD-EXPANSION-001-typed-tt-cross-preflight-v1-verifier", "checks": checks, "valid": checks["valid"]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("result", type=Path)
    parser.add_argument("input", type=Path)
    parser.add_argument("rank_oracle", type=Path)
    args = parser.parse_args()
    raw = json.loads(args.result.read_text(encoding="utf-8"))
    print(json.dumps(check(raw, args.input, args.rank_oracle), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
