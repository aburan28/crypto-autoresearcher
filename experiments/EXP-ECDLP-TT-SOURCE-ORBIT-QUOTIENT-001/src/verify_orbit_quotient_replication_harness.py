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
INPUT_SOURCE = REPO_ROOT / "experiments" / "EXP-ECDLP-TT-SAMPLED-SCALE-001" / "src" / "typed_tt_sampled_relation_input.py"
LOCATOR_SOURCE = SCRIPT_PATH.with_name("orbit_quotient_locator.py")
GENERATOR_SOURCE = SCRIPT_PATH.with_name("run_orbit_quotient_replication_harness.py")


def load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BASE = load("orbit_quotient_verifier_base", BASE_SOURCE)
INPUT = load("orbit_quotient_verifier_input", INPUT_SOURCE)
LOCATOR = load("orbit_quotient_verifier_locator", LOCATOR_SOURCE)
FRESH = BASE.FRESH
FRESH_SEEDS = BASE.FRESH_SEEDS
FAMILIES = BASE.FAMILIES
BUDGETS = ["4", "8", "full"]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_fixture(value: dict[str, Any]) -> dict[str, Any]:
    def normalize(item: Any) -> Any:
        if isinstance(item, dict):
            return {key: normalize(child) for key, child in item.items() if key not in {"wall_seconds", "total_wall_seconds"}}
        if isinstance(item, list):
            return [normalize(child) for child in item]
        return item
    return normalize(value)


def verify_case(case: dict[str, Any], fixture: dict[str, Any], fixture_path: Path, relation_path: Path) -> dict[str, bool]:
    candidate = case["candidate"]
    curve_id = fixture["instances"][0]["curve"]["id"]
    relation_input = INPUT.write_fixture_record(relation_path, fixture_path, curve_id, FAMILIES)
    checks = {
        "protocol": candidate.get("protocol") == "EXP-ECDLP-TT-SOURCE-ORBIT-QUOTIENT-001-candidate-v1",
        "generator_hash": candidate.get("source", {}).get("harness_source_sha256") == sha256(GENERATOR_SOURCE),
        "locator_hash": candidate.get("source", {}).get("locator_sha256") == sha256(LOCATOR_SOURCE),
        "relation_hash": candidate.get("source", {}).get("relation_input_sha256") == [sha256(relation_path)],
        "fixture_hash": candidate.get("source", {}).get("fixture_sha256") == sha256(fixture_path),
        "config": candidate.get("config", {}).get("budgets") == BUDGETS and candidate.get("config", {}).get("selection_uses_targets") is False and candidate.get("config", {}).get("selection_uses_relations") is False,
        "rows": {(row.get("curve_id"), row.get("family")) for row in candidate.get("rows", [])} == {(curve_id, family) for family in FAMILIES},
        "full": candidate.get("summary", {}).get("full_budget_exact") is True,
        "witnesses": candidate.get("summary", {}).get("full_budget_witnesses_valid") is True,
        "no_promotion": candidate.get("summary", {}).get("breakthrough_claim") is False and candidate.get("summary", {}).get("algorithm_promotion_gate") is False,
        "rho": case.get("rho", {}).get("all_solved") is True,
        "support_and_witnesses": True,
    }
    instance = fixture["instances"][0]
    families = {item["family"]: item for item in instance["families"]}
    transcripts = {row["family"]: row["shared_candidate"]["transcripts"] for row in relation_input["rows"]}
    curve_record = instance["curve"]
    curve = LOCATOR.TF.Curve(curve_record["p"], curve_record["a"], curve_record["b"])
    for row in candidate.get("rows", []):
        family = row["family"]
        a_points = [LOCATOR.TF.point_from_json(value) for value in families[family]["progression"]["points"]]
        r_points = [LOCATOR.TF.point_from_json(value) for value in families[family]["factor_base"]["points"]]
        for budget in row.get("budgets", []):
            checks["support_and_witnesses"] = checks["support_and_witnesses"] and budget.get("total_false_positives") == 0 and budget.get("total_lift_false_quotient_zeros") >= 0
            for target_index, record in enumerate(budget.get("target_records", [])):
                hits = {tuple(int(value) for value in item["indices"]) for item in record.get("candidate_hits", [])}
                expected_a = {int(item["a_index"]) for item in transcripts[family][target_index]["baseline_hits"]}
                if budget.get("all_support_exact"):
                    checks["support_and_witnesses"] = checks["support_and_witnesses"] and {item[0] for item in hits} == expected_a
                target = tuple(record["target"])
                checks["support_and_witnesses"] = checks["support_and_witnesses"] and all(LOCATOR.valid_witness(curve, a_points, r_points, indices, target, LOCATOR.TF.Ops()) for indices in hits)
    return checks


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: verify_orbit_quotient_replication_harness.py GENERATOR_RAW_RESULT")
    raw_path = Path(sys.argv[1]).resolve()
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    checks = {
        "generator_valid": raw.get("valid") is True,
        "inputs": raw.get("inputs", {}).get("seeds") == FRESH_SEEDS and raw.get("inputs", {}).get("budgets") == BUDGETS and raw.get("inputs", {}).get("families") == FAMILIES,
        "case_count": len(raw.get("cases", [])) == len(FRESH_SEEDS),
    }
    with tempfile.TemporaryDirectory(prefix="tt-orbit-quotient-verify-") as temp:
        root = Path(temp)
        for seed, case in zip(FRESH_SEEDS, raw.get("cases", [])):
            fixture = canonical_fixture(FRESH.run_experiment([14], seed, FAMILIES, 0.5, 32))
            fixture_path = root / f"fixture-{seed}.json"
            fixture_path.write_text(json.dumps(fixture, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
            relation_path = root / f"relation-{seed}.json"
            result = verify_case(case, fixture, fixture_path, relation_path)
            for name, value in result.items():
                checks[f"{seed}_{name}"] = value
            checks[f"{seed}_curve_match"] = case.get("curve_id") == fixture["instances"][0]["curve"]["id"]
    checks["valid"] = all(checks.values())
    output = {
        "valid": checks["valid"],
        "protocol": "EXP-ECDLP-TT-SOURCE-ORBIT-QUOTIENT-001-harness-verifier-v1",
        "input": {"sha256": sha256(raw_path), "path": str(raw_path)},
        "checks": checks,
        "summary": {"accepted_subfull_budgets": raw.get("summary", {}).get("accepted_subfull_budgets"), "boundary": "Independent fixture regeneration, source/orbit hash checks, lifted witness validation, and matched rho receipt checks; no generic ECDLP or exponent claim."},
    }
    print(json.dumps(output, sort_keys=True, separators=(",", ":")))
    return 0 if output["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
