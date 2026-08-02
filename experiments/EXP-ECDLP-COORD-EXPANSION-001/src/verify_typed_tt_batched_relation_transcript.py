#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
PRODUCER_PATH = SCRIPT_PATH.with_name("typed_tt_batched_relation_transcript.py")
BATCH_PATH = SCRIPT_PATH.with_name("typed_tt_batched_source_sum.py")


def load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")).hexdigest()


def verify(raw_path: Path, output_path: Path, input_path: Path) -> dict[str, Any]:
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    checks = {
        "protocol": raw.get("protocol") == "EXP-ECDLP-COORD-EXPANSION-001-typed-tt-batched-relation-transcript-v1",
        "producer_hash": raw.get("source", {}).get("producer_sha256") == sha256_file(PRODUCER_PATH),
        "batch_hash": raw.get("source", {}).get("batch_source_sha256") == sha256_file(BATCH_PATH),
        "input_hash": raw.get("source", {}).get("input_sha256") == sha256_file(input_path),
        "rows": len(raw.get("rows", [])) == 4,
        "witnesses": raw.get("summary", {}).get("all_witnesses_valid") is True,
        "support": raw.get("summary", {}).get("all_supports_match") is True,
        "direct_exact": raw.get("summary", {}).get("all_direct_reference_exact") is True,
        "rowspace_rank": raw.get("summary", {}).get("all_same_rowspace_rank") is True,
        "relation_rank": raw.get("summary", {}).get("all_same_relation_rank") is True,
        "held_out_coverage": raw.get("summary", {}).get("all_held_out_supported_coverage") is True,
        "diagnostic_solution": raw.get("summary", {}).get("all_diagnostic_solution_matches") is True,
        "source_saving": raw.get("summary", {}).get("all_strict_source_add_saving") is True,
        "no_promotion": raw.get("summary", {}).get("breakthrough_claim") is False and raw.get("summary", {}).get("algorithm_promotion_gate") is False,
        "result_digest": False,
    }
    normalized = [{key: value for key, value in row.items() if key != "wall_seconds"} for row in raw.get("rows", [])]
    checks["result_digest"] = raw.get("result_digest") == digest(normalized)
    checks["row_controls"] = True
    for row in raw.get("rows", []):
        shared = row.get("shared_candidate", {})
        control = row.get("target_separated_control", {})
        checks["row_controls"] = checks["row_controls"] and shared.get("all_candidate_witnesses_valid") is True and control.get("all_candidate_witnesses_valid") is True
        checks["row_controls"] = checks["row_controls"] and shared.get("all_supports_match") is True and control.get("all_supports_match") is True
        checks["row_controls"] = checks["row_controls"] and row.get("same_relation_rank") is True
        checks["row_controls"] = checks["row_controls"] and shared.get("candidate_full_rank") is True
        checks["row_controls"] = checks["row_controls"] and row.get("shared_diagnostic_solution_match") is True and row.get("control_diagnostic_solution_match") is True
    checks["valid"] = all(checks.values())
    receipt = {
        "protocol": "EXP-ECDLP-COORD-EXPANSION-001-typed-tt-batched-relation-transcript-v1-verifier",
        "checks": checks,
        "valid": checks["valid"],
    }
    output_path.write_text(json.dumps(receipt, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    if len(sys.argv) != 4:
        raise SystemExit("usage: verify_typed_tt_batched_relation_transcript.py RAW OUTPUT INPUT")
    receipt = verify(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))
    print(json.dumps(receipt, sort_keys=True, separators=(",", ":")))
    return 0 if receipt["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
