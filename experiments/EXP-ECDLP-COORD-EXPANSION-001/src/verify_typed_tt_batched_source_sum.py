#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
PRODUCER_PATH = SCRIPT_PATH.with_name("typed_tt_batched_source_sum.py")
ROWSPACE_PATH = SCRIPT_PATH.with_name("typed_tt_rowspace_witness_locator.py")
SCALE_PATH = SCRIPT_PATH.with_name("typed_tt_rowspace_scale_probe.py")


def load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


PRODUCER = load("typed_tt_batched_source_sum_verifier", PRODUCER_PATH)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")).hexdigest()


def verify(raw_path: Path, output_path: Path, input_path: Path) -> dict[str, Any]:
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    checks: dict[str, bool] = {
        "protocol": raw.get("protocol") == "EXP-ECDLP-COORD-EXPANSION-001-typed-tt-batched-source-sum-v1",
        "producer_hash": raw.get("source", {}).get("producer_sha256") == sha256_file(PRODUCER_PATH),
        "rowspace_hash": raw.get("source", {}).get("rowspace_sha256") == sha256_file(ROWSPACE_PATH),
        "scale_hash": raw.get("source", {}).get("scale_probe_sha256") == sha256_file(SCALE_PATH),
        "input_hash": raw.get("source", {}).get("input_sha256") == sha256_file(input_path),
        "no_promotion": raw.get("summary", {}).get("breakthrough_claim") is False and raw.get("summary", {}).get("algorithm_promotion_gate") is False,
        "rows": len(raw.get("rows", [])) == 4,
        "same_rank": raw.get("summary", {}).get("all_same_rank") is True,
        "same_targets": raw.get("summary", {}).get("all_same_target_stream") is True,
        "shared_direct_exact": raw.get("summary", {}).get("all_shared_direct_reference_exact") is True,
        "control_direct_exact": raw.get("summary", {}).get("all_control_direct_reference_exact") is True,
        "source_saving": raw.get("summary", {}).get("shared_source_add_saving_observed") is True,
        "x_interval_control": False,
        "width_protocol": True,
        "result_digest": False,
    }
    normalized = [{key: value for key, value in row.items() if key != "wall_seconds"} for row in raw.get("rows", [])]
    checks["result_digest"] = raw.get("result_digest") == digest(normalized)
    expected_widths = [1, 2, 4, 8, 15]
    for row in raw.get("rows", []):
        separated = row.get("separated_control", {})
        shared = row.get("shared_candidate", {})
        checks["width_protocol"] = checks["width_protocol"] and [item.get("width") for item in shared.get("batches", [])] == expected_widths and [item.get("width") for item in separated.get("batches", [])] == expected_widths
        for control, candidate in zip(separated.get("batches", []), shared.get("batches", [])):
            checks["width_protocol"] = checks["width_protocol"] and candidate.get("source_ops", {}).get("point_add_calls", 0) <= control.get("source_ops", {}).get("point_add_calls", 0)
            if candidate.get("width", 0) > 1:
                checks["source_saving"] = checks["source_saving"] and candidate.get("source_ops", {}).get("point_add_calls", 0) < control.get("source_ops", {}).get("point_add_calls", 0)
        if row.get("family") == "x_interval":
            checks["x_interval_control"] = shared.get("all_sample_matches") is True
    checks["valid"] = all(checks.values())
    receipt = {
        "protocol": "EXP-ECDLP-COORD-EXPANSION-001-typed-tt-batched-source-sum-v1-verifier",
        "checks": checks,
        "valid": checks["valid"],
    }
    output_path.write_text(json.dumps(receipt, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    if len(sys.argv) != 4:
        raise SystemExit("usage: verify_typed_tt_batched_source_sum.py RAW OUTPUT INPUT")
    receipt = verify(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))
    print(json.dumps(receipt, sort_keys=True, separators=(",", ":")))
    return 0 if receipt["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
