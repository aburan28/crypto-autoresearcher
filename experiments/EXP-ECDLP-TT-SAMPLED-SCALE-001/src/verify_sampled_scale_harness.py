#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import tempfile
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[3]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "src"))

from harness.toycurve import EllipticCurve  # noqa: E402


FIXTURE_PATH = REPO_ROOT / "experiments" / "EXP-ECDLP-COORD-EXPANSION-001" / "development" / "TYPED-ADAPTIVE-FRESH-SEED-FIXTURE-V1" / "RUN-001" / "raw-result.json"
SCALE_SRC = REPO_ROOT / "experiments" / "EXP-ECDLP-COORD-EXPANSION-001" / "src"
LOCATOR_SOURCE = SCALE_SRC / "typed_tt_sampled_locator.py"
INPUT_SOURCE = SCRIPT_PATH.with_name("typed_tt_sampled_relation_input.py")

CURVE_ID = "recursive-toy-p16267-a10934-b358-q16057"
FAMILIES = ["random_x", "source_prf_x", "x_interval", "rational_union"]
BUDGETS = ["8", "16", "32", "64", "full"]


def _load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


INPUT = _load("sampled_scale_verifier_input", INPUT_SOURCE)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _hit_indices(hit: dict[str, Any]) -> tuple[int, ...]:
    if "indices" in hit:
        return tuple(int(value) for value in hit["indices"])
    return (int(hit["a_index"]), *[int(value) for value in hit["r_witness"]])


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")).hexdigest()


def _verify_candidate(candidate: dict[str, Any], relation_path: Path, fixture_path: Path) -> dict[str, bool]:
    checks: dict[str, bool] = {
        "protocol": candidate.get("protocol") == "EXP-ECDLP-COORD-EXPANSION-001-typed-tt-sampled-locator-v1",
        "producer_hash": candidate.get("source", {}).get("producer_sha256") == _sha256(LOCATOR_SOURCE),
        "relation_input_hash": candidate.get("source", {}).get("relation_input_sha256") == [_sha256(relation_path)],
        "fixture_hash": candidate.get("source", {}).get("fixture_sha256") == _sha256(fixture_path),
        "config": candidate.get("config", {}).get("budgets") == BUDGETS,
        "rows": {(row.get("curve_id"), row.get("family")) for row in candidate.get("rows", [])}
        == {(CURVE_ID, family) for family in FAMILIES},
        "full_budget": candidate.get("summary", {}).get("full_budget_exact") is True,
        "full_witnesses": candidate.get("summary", {}).get("full_budget_witnesses_valid") is True,
        "no_promotion": candidate.get("summary", {}).get("breakthrough_claim") is False
        and candidate.get("summary", {}).get("algorithm_promotion_gate") is False,
        "result_digest": False,
        "row_checks": True,
    }
    normalized = [{key: value for key, value in row.items()} for row in candidate.get("rows", [])]
    checks["result_digest"] = candidate.get("result_digest") == _digest(normalized)
    for row in candidate.get("rows", []):
        budgets = row.get("budgets", [])
        checks["row_checks"] = checks["row_checks"] and [item.get("budget_label") for item in budgets] == BUDGETS
        full = budgets[-1] if budgets else {}
        checks["row_checks"] = checks["row_checks"] and full.get("all_support_exact") is True
        checks["row_checks"] = checks["row_checks"] and full.get("all_held_out_support_exact") is True
        checks["row_checks"] = checks["row_checks"] and full.get("all_candidate_witnesses_valid") is True
        checks["row_checks"] = checks["row_checks"] and full.get("candidate_predicted_entries") == full.get("full_predicted_entries")
        checks["row_checks"] = checks["row_checks"] and all(
            budget.get("total_false_positives") == 0
            and all(item.get("candidate_witnesses_valid") is True for item in budget.get("target_records", []))
            for budget in budgets
        )
    return checks


def _verify_rho(raw: dict[str, Any], relation_input: dict[str, Any], fixture: dict[str, Any]) -> dict[str, bool]:
    instance = next(item for item in fixture["instances"] if item["curve"]["id"] == CURVE_ID)
    curve_record = instance["curve"]
    curve = EllipticCurve(curve_record["p"], curve_record["a"], curve_record["b"])
    by_family = {row["family"]: row for row in raw.get("rho", {}).get("by_family", [])}
    checks = {"rows": set(by_family) == set(FAMILIES), "direct_certificates": True, "counts": True}
    input_by_family = {row["family"]: row for row in relation_input["rows"]}
    for family in FAMILIES:
        reported = by_family.get(family, {})
        expected_targets = input_by_family[family]["shared_candidate"]["transcripts"]
        reported_targets = reported.get("targets", [])
        checks["counts"] = checks["counts"] and len(reported_targets) == len(expected_targets)
        for target, result in zip(expected_targets, reported_targets):
            recovered = result.get("recovered_k")
            point = tuple(target["target"])
            checks["direct_certificates"] = checks["direct_certificates"] and isinstance(recovered, int) and curve.mul(recovered, tuple(curve_record["generator"])) == point
            checks["direct_certificates"] = checks["direct_certificates"] and result.get("direct_certificate_valid") is True
    checks["all_solved"] = raw.get("rho", {}).get("all_solved") is True
    return checks


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: verify_sampled_scale_harness.py GENERATOR_RAW_RESULT")
    generator_raw_path = Path(sys.argv[1]).resolve()
    raw = json.loads(generator_raw_path.read_text(encoding="utf-8"))
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory(prefix="tt-sampled-scale-verify-") as temp:
        relation_path = Path(temp) / "relation-input.json"
        relation_input = INPUT.write_fixture_record(relation_path, FIXTURE_PATH, CURVE_ID, FAMILIES)
        candidate_checks = _verify_candidate(raw.get("candidate", {}), relation_path, FIXTURE_PATH)
        rho_checks = _verify_rho(raw, relation_input, fixture)
    checks = {**candidate_checks, **{f"rho_{key}": value for key, value in rho_checks.items()}}
    checks["generator_valid"] = raw.get("valid") is True
    checks["valid"] = all(checks.values())
    output = {
        "valid": checks["valid"],
        "protocol": "EXP-ECDLP-TT-SAMPLED-SCALE-001-harness-verifier-v1",
        "input": {"sha256": _sha256(generator_raw_path), "path": str(generator_raw_path)},
        "checks": checks,
        "summary": {
            "boundary": "Independent structural support/rank and direct rho certificate verification for a fresh p16267 toy run; no generic ECDLP or exponent claim.",
            "subfull_exact_budgets": raw.get("summary", {}).get("subfull_exact_budgets"),
        },
    }
    print(json.dumps(output, sort_keys=True, separators=(",", ":")))
    return 0 if output["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
