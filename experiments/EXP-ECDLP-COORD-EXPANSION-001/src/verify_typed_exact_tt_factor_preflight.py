#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
PRODUCER_PATH = SCRIPT_PATH.with_name("typed_exact_tt_factor_preflight.py")


def load_producer() -> Any:
    spec = importlib.util.spec_from_file_location("typed_exact_tt_factor_preflight_verify", PRODUCER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load exact TT producer")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_result(raw: dict[str, Any], input_path: Path) -> dict[str, Any]:
    checks = {
        "protocol": raw.get("protocol") == "EXP-ECDLP-COORD-EXPANSION-001-typed-exact-tt-factor-preflight-v1",
        "input_hash": raw.get("source", {}).get("input_sha256") == load_producer().sha256_file(input_path),
        "config": raw.get("config", {}).get("source_tuple_enumeration") is True,
        "enumerative_boundary": all(row.get("enumerative_diagnostic") is True for row in raw.get("rows", [])),
        "rows": len(raw.get("rows", [])) == 12,
        "reconstruction": raw.get("summary", {}).get("all_reconstructed") is True,
        "promotion_false": raw.get("summary", {}).get("algorithm_promotion_gate") is False,
        "breakthrough_false": raw.get("summary", {}).get("breakthrough_claim") is False,
    }
    producer = load_producer()
    rerun = producer.run(input_path, raw.get("config", {}).get("families", []))
    checks["producer_rerun_exact"] = rerun["result_digest"] == raw.get("result_digest")
    checks["mutation_rejected"] = producer.factor_matrix([[1, 0], [0, 1]], 101, {"field_inversions": 0, "field_multiplications": 0, "field_subtractions": 0})[2] == 2
    checks["valid"] = all(checks.values())
    return {"protocol": "EXP-ECDLP-COORD-EXPANSION-001-typed-exact-tt-factor-preflight-v1-verifier", "checks": checks, "valid": checks["valid"]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("result", type=Path)
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    raw = json.loads(args.result.read_text(encoding="utf-8"))
    print(json.dumps(check_result(raw, args.input), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
