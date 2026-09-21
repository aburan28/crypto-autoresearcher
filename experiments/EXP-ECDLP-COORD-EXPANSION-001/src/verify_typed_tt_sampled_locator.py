#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
PRODUCER_PATH = SCRIPT_PATH.with_name("typed_tt_sampled_locator.py")
BATCH_PATH = SCRIPT_PATH.with_name("typed_tt_batched_source_sum.py")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")).hexdigest()


def verify(raw_path: Path, output_path: Path, relation_input: Path, fixture: Path) -> dict[str, Any]:
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    expected_rows = {
        ("recursive-toy-p947-a659-b11-q971", "random_x"),
        ("recursive-toy-p947-a659-b11-q971", "source_prf_x"),
        ("recursive-toy-p947-a659-b11-q971", "x_interval"),
        ("recursive-toy-p947-a659-b11-q971", "rational_union"),
        ("recursive-toy-p4027-a2225-b3340-q4129", "random_x"),
        ("recursive-toy-p4027-a2225-b3340-q4129", "source_prf_x"),
        ("recursive-toy-p4027-a2225-b3340-q4129", "x_interval"),
        ("recursive-toy-p4027-a2225-b3340-q4129", "rational_union"),
    }
    checks = {
        "protocol": raw.get("protocol") == "EXP-ECDLP-COORD-EXPANSION-001-typed-tt-sampled-locator-v1",
        "producer_hash": raw.get("source", {}).get("producer_sha256") == sha256_file(PRODUCER_PATH),
        "batch_hash": raw.get("source", {}).get("batch_source_sha256") == sha256_file(BATCH_PATH),
        "relation_input_hash": raw.get("source", {}).get("relation_input_sha256") == [sha256_file(relation_input)],
        "fixture_hash": raw.get("source", {}).get("fixture_sha256") == sha256_file(fixture),
        "rows": {(row.get("curve_id"), row.get("family")) for row in raw.get("rows", [])} == expected_rows,
        "full_budget": raw.get("summary", {}).get("full_budget_exact") is True,
        "full_witnesses": raw.get("summary", {}).get("full_budget_witnesses_valid") is True,
        "rank_negative_control": raw.get("summary", {}).get("known_p4027_source_prf_rank_deficient") is True,
        "no_promotion": raw.get("summary", {}).get("breakthrough_claim") is False and raw.get("summary", {}).get("algorithm_promotion_gate") is False,
        "result_digest": False,
        "budget_structure": True,
    }
    normalized = [{key: value for key, value in row.items()} for row in raw.get("rows", [])]
    checks["result_digest"] = raw.get("result_digest") == digest(normalized)
    for row in raw.get("rows", []):
        budgets = row.get("budgets", [])
        checks["budget_structure"] = checks["budget_structure"] and bool(budgets) and budgets[-1].get("budget_label") == "full"
        full = budgets[-1] if budgets else {}
        checks["budget_structure"] = checks["budget_structure"] and full.get("all_support_exact") is True
        checks["budget_structure"] = checks["budget_structure"] and full.get("all_candidate_witnesses_valid") is True
        checks["budget_structure"] = checks["budget_structure"] and full.get("candidate_predicted_entries") == full.get("full_predicted_entries")
        for budget in budgets:
            checks["budget_structure"] = checks["budget_structure"] and budget.get("total_false_positives") == 0
            checks["budget_structure"] = checks["budget_structure"] and budget.get("candidate_predicted_entries", 0) <= budget.get("full_predicted_entries", -1)
            checks["budget_structure"] = checks["budget_structure"] and all(item.get("candidate_witnesses_valid") is True for item in budget.get("target_records", []))
    checks["valid"] = all(checks.values())
    receipt = {
        "protocol": "EXP-ECDLP-COORD-EXPANSION-001-typed-tt-sampled-locator-v1-verifier",
        "checks": checks,
        "valid": checks["valid"],
        "boundary": "Full-budget replay and budgeted projected-support audit only; no generic ECDLP or exponent claim.",
    }
    output_path.write_text(json.dumps(receipt, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    if len(sys.argv) != 5:
        raise SystemExit("usage: verify_typed_tt_sampled_locator.py RAW OUTPUT RELATION_INPUT FIXTURE")
    receipt = verify(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4]))
    print(json.dumps(receipt, sort_keys=True, separators=(",", ":")))
    return 0 if receipt["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
