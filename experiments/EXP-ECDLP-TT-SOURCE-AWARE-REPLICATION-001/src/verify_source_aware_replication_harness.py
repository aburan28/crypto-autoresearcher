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

BASE_SOURCE = REPO_ROOT / "experiments" / "EXP-ECDLP-TT-SAMPLED-REPLICATION-001" / "src" / "run_fresh_replication_harness.py"
SELECTOR_SOURCE = SCRIPT_PATH.with_name("source_aware_suffix_selector.py")


def _load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BASE = _load("fresh_replication_base_for_source_aware_verifier", BASE_SOURCE)
SELECTOR = _load("source_aware_suffix_selector_verifier", SELECTOR_SOURCE)
FRESH = BASE.FRESH
INPUT = BASE.INPUT
LOCATOR = BASE.LOCATOR
FRESH_SEEDS = BASE.FRESH_SEEDS
FAMILIES = BASE.FAMILIES
BUDGETS = ["32", "64", "full"]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_fixture(value: dict[str, Any]) -> dict[str, Any]:
    def normalize(item: Any) -> Any:
        if isinstance(item, dict):
            return {
                key: normalize(child)
                for key, child in item.items()
                if key not in {"wall_seconds", "total_wall_seconds"}
            }
        if isinstance(item, list):
            return [normalize(child) for child in item]
        return item

    return normalize(value)


def _selector_order(curve_record: dict[str, Any], family: dict[str, Any]) -> dict[str, Any]:
    curve = LOCATOR.TF.Curve(curve_record["p"], curve_record["a"], curve_record["b"])
    r_points = [LOCATOR.TF.point_from_json(value) for value in family["factor_base"]["points"]]
    ops = LOCATOR.TF.Ops()
    suffix_points = []
    for left in r_points:
        for right in r_points:
            suffix_points.append(curve.add(left, right, ops))
    order = SELECTOR.order_from_suffix_points(suffix_points)
    return {
        "name": SELECTOR.SELECTOR_NAME,
        "definition": SELECTOR.SELECTOR_DEFINITION,
        "order": order,
        "order_digest": hashlib.sha256(json.dumps(order, separators=(",", ":")).encode("ascii")).hexdigest(),
        "suffix_points_digest": hashlib.sha256(json.dumps(suffix_points, separators=(",", ":")).encode("ascii")).hexdigest(),
        "construction_ops": LOCATOR.TF.asdict(ops),
        "source_only": True,
        "target_independent": True,
        "relation_input_independent": True,
    }


def _indices(hit: dict[str, Any]) -> tuple[int, ...]:
    return tuple(int(value) for value in hit["indices"])


def _witness_valid(curve: Any, a_points: list[Any], r_points: list[Any], indices: tuple[int, ...], target: Any) -> bool:
    if len(indices) != 5 or not (0 <= indices[0] < len(a_points)) or any(not (0 <= index < len(r_points)) for index in indices[1:]):
        return False
    total = a_points[indices[0]]
    for index in indices[1:]:
        total = curve.add(total, r_points[index])
    return total == target


def _verify_candidate(case: dict[str, Any], fixture_path: Path, relation_path: Path, fixture: dict[str, Any], relation_input: dict[str, Any], selector_orders: dict[str, dict[str, Any]]) -> dict[str, bool]:
    candidate = case["candidate"]
    curve_record = fixture["instances"][0]["curve"]
    curve_id = curve_record["id"]
    checks = {
        "protocol": candidate.get("protocol") == "EXP-ECDLP-TT-SOURCE-AWARE-REPLICATION-001-candidate-v1",
        "selector_hash": candidate.get("source", {}).get("selector_sha256") == _sha256(SELECTOR_SOURCE),
        "base_locator_hash": candidate.get("source", {}).get("base_locator_sha256") == _sha256(BASE.LOCATOR_SOURCE),
        "relation_hash": candidate.get("source", {}).get("relation_input_sha256") == [_sha256(relation_path)],
        "fixture_hash": candidate.get("source", {}).get("fixture_sha256") == _sha256(fixture_path),
        "config": candidate.get("config", {}).get("budgets") == BUDGETS and candidate.get("config", {}).get("locator") == SELECTOR.SELECTOR_NAME and candidate.get("config", {}).get("selection_uses_targets") is False and candidate.get("config", {}).get("selection_uses_relations") is False,
        "rows": {(row.get("curve_id"), row.get("family")) for row in candidate.get("rows", [])} == {(curve_id, family) for family in FAMILIES},
        "full": candidate.get("summary", {}).get("full_budget_exact") is True,
        "full_witnesses": candidate.get("summary", {}).get("full_budget_witnesses_valid") is True,
        "no_promotion": candidate.get("summary", {}).get("breakthrough_claim") is False and candidate.get("summary", {}).get("algorithm_promotion_gate") is False,
        "selector_records": True,
        "support_and_witnesses": True,
    }
    expected_records = selector_orders
    for family, expected in expected_records.items():
        observed = candidate.get("selector_records", {}).get(family)
        checks["selector_records"] = checks["selector_records"] and observed == expected
    instance = fixture["instances"][0]
    families_by_name = {item["family"]: item for item in instance["families"]}
    relation_by_name = {item["family"]: item for item in relation_input["rows"]}
    curve = LOCATOR.TF.Curve(curve_record["p"], curve_record["a"], curve_record["b"])
    for row in candidate.get("rows", []):
        family = row["family"]
        family_record = families_by_name[family]
        a_points = [LOCATOR.TF.point_from_json(point) for point in family_record["progression"]["points"]]
        r_points = [LOCATOR.TF.point_from_json(point) for point in family_record["factor_base"]["points"]]
        expected_targets = relation_by_name[family]["shared_candidate"]["transcripts"]
        for budget in row.get("budgets", []):
            checks["support_and_witnesses"] = checks["support_and_witnesses"] and budget.get("total_false_positives") == 0
            for target_index, target_record in enumerate(budget.get("target_records", [])):
                candidate_hits = {_indices(hit) for hit in target_record.get("candidate_hits", [])}
                candidate_a = {item[0] for item in candidate_hits}
                baseline_a = {int(hit["a_index"]) for hit in expected_targets[target_index]["baseline_hits"]}
                if budget.get("all_support_exact"):
                    checks["support_and_witnesses"] = checks["support_and_witnesses"] and candidate_a == baseline_a
                target = tuple(target_record["target"])
                checks["support_and_witnesses"] = checks["support_and_witnesses"] and all(_witness_valid(curve, a_points, r_points, indices, target) for indices in candidate_hits)
                if target_record.get("held_out_supported") and budget.get("all_held_out_support_exact"):
                    expected = expected_targets[target_index].get("expected_witness")
                    expected_indices = (int(expected["a_index"]), *[int(value) for value in expected["r_witness"]])
                    checks["support_and_witnesses"] = checks["support_and_witnesses"] and expected_indices in candidate_hits
    return checks


def _verify_rho(case: dict[str, Any], fixture: dict[str, Any], relation_input: dict[str, Any]) -> dict[str, bool]:
    curve_record = fixture["instances"][0]["curve"]
    curve = LOCATOR.TF.Curve(curve_record["p"], curve_record["a"], curve_record["b"])
    generator = LOCATOR.TF.point_from_json(curve_record["generator"])
    by_family = {row["family"]: row for row in case["rho"].get("by_family", [])}
    inputs = {row["family"]: row for row in relation_input["rows"]}
    checks = {
        "families": set(by_family) == set(FAMILIES),
        "counts": True,
        "certificates": True,
        "all_solved": case["rho"].get("all_solved") is True,
    }
    for family in FAMILIES:
        expected = inputs[family]["shared_candidate"]["transcripts"]
        observed = by_family.get(family, {}).get("targets", [])
        checks["counts"] = checks["counts"] and len(expected) == len(observed)
        for target, result in zip(expected, observed):
            recovered = result.get("recovered_k")
            checks["certificates"] = checks["certificates"] and isinstance(recovered, int) and curve.mul(recovered, generator) == tuple(target["target"])
            checks["certificates"] = checks["certificates"] and result.get("direct_certificate_valid") is True
    return checks


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: verify_source_aware_replication_harness.py GENERATOR_RAW_RESULT")
    generator_raw_path = Path(sys.argv[1]).resolve()
    raw = json.loads(generator_raw_path.read_text(encoding="utf-8"))
    checks: dict[str, bool] = {
        "generator_valid": raw.get("valid") is True,
        "inputs": raw.get("inputs", {}).get("seeds") == FRESH_SEEDS and raw.get("inputs", {}).get("budgets") == BUDGETS and raw.get("inputs", {}).get("selector") == SELECTOR.SELECTOR_NAME,
        "case_count": len(raw.get("cases", [])) == len(FRESH_SEEDS),
    }
    with tempfile.TemporaryDirectory(prefix="tt-source-aware-replication-verify-") as temp:
        temp_root = Path(temp)
        for seed, case in zip(FRESH_SEEDS, raw.get("cases", [])):
            fixture = _canonical_fixture(FRESH.run_experiment([14], seed, FAMILIES, 0.5, 32))
            fixture_path = temp_root / f"fixture-{seed}.json"
            fixture_path.write_text(json.dumps(fixture, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
            curve_id = fixture["instances"][0]["curve"]["id"]
            relation_path = temp_root / f"relation-{seed}.json"
            relation_input = INPUT.write_fixture_record(relation_path, fixture_path, curve_id, FAMILIES)
            instance = fixture["instances"][0]
            selector_orders = {
                family["family"]: _selector_order(instance["curve"], family)
                for family in instance["families"]
            }
            candidate_checks = _verify_candidate(case, fixture_path, relation_path, fixture, relation_input, selector_orders)
            rho_checks = _verify_rho(case, fixture, relation_input)
            for name, value in candidate_checks.items():
                checks[f"{seed}_candidate_{name}"] = value
            for name, value in rho_checks.items():
                checks[f"{seed}_rho_{name}"] = value
            checks[f"{seed}_curve_match"] = case.get("curve_id") == curve_id
    checks["valid"] = all(checks.values())
    output = {
        "valid": checks["valid"],
        "protocol": "EXP-ECDLP-TT-SOURCE-AWARE-REPLICATION-001-harness-verifier-v1",
        "input": {"sha256": _sha256(generator_raw_path), "path": str(generator_raw_path)},
        "checks": checks,
        "summary": {
            "accepted_subfull_budgets": raw.get("summary", {}).get("accepted_subfull_budgets"),
            "boundary": "Independent source-only selector regeneration, support/witness checks, and direct rho certificate verification for two fresh 14-bit toy curves; no generic ECDLP or exponent claim.",
        },
    }
    print(json.dumps(output, sort_keys=True, separators=(",", ":")))
    return 0 if output["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
