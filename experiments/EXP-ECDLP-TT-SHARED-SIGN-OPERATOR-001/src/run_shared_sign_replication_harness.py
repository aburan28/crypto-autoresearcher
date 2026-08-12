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
LOCATOR_SOURCE = SCRIPT_PATH.with_name("shared_sign_locator.py")
REFERENCE_RAW = REPO_ROOT / "experiments" / "EXP-ECDLP-TT-SOURCE-ORBIT-QUOTIENT-001" / "runs" / "RUN-TT-SOURCE-ORBIT-QUOTIENT-001" / "raw-result.json"


def load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BASE = load("shared_sign_fresh_base", BASE_SOURCE)
INPUT = load("shared_sign_relation_input", INPUT_SOURCE)
LOCATOR = load("shared_sign_locator", LOCATOR_SOURCE)
FRESH = BASE.FRESH
FRESH_SEEDS = BASE.FRESH_SEEDS
FAMILIES = BASE.FAMILIES
BUDGETS = ["32", "44", "full"]


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


def reference_summary(reference: dict[str, Any], curve_id: str, family: str) -> dict[str, Any]:
    case = next(item for item in reference["cases"] if item["curve_id"] == curve_id)
    candidate_row = next(item for item in case["candidate"]["rows"] if item["family"] == family)
    baseline_row = next(item for item in case["baseline"]["rows"] if item["family"] == family)
    return {"naive_orbit_full": candidate_row["budgets"][-1], "original_full": baseline_row}


def main() -> int:
    reference = json.loads(REFERENCE_RAW.read_text(encoding="utf-8"))
    cases = []
    with tempfile.TemporaryDirectory(prefix="tt-shared-sign-replication-") as temp:
        root = Path(temp)
        for seed in FRESH_SEEDS:
            fixture = canonical_fixture(FRESH.run_experiment([14], seed, FAMILIES, 0.5, 32))
            fixture_path = root / f"fixture-{seed}.json"
            fixture_path.write_text(json.dumps(fixture, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
            curve_id = fixture["instances"][0]["curve"]["id"]
            relation_path = root / f"relation-{seed}.json"
            relation_input = INPUT.write_fixture_record(relation_path, fixture_path, curve_id, FAMILIES)
            candidate = LOCATOR.run([relation_path], fixture_path, FAMILIES, BUDGETS)
            candidate["protocol"] = "EXP-ECDLP-TT-SHARED-SIGN-OPERATOR-001-candidate-v1"
            candidate["source"]["harness_source_sha256"] = sha256(SCRIPT_PATH)
            candidate["source"]["base_harness_sha256"] = sha256(BASE_SOURCE)
            candidate["source"]["locator_sha256"] = sha256(LOCATOR_SOURCE)
            candidate["config"].update({"budgets": BUDGETS, "selection_uses_targets": False, "selection_uses_relations": False})
            comparisons = {family: reference_summary(reference, curve_id, family) for family in FAMILIES}
            rho_result = BASE._rho_for_fixture(fixture, relation_input)
            instance = fixture["instances"][0]
            cases.append({"seed": seed, "curve_id": curve_id, "curve": {"p": instance["curve"]["p"], "q": instance["curve"]["q"], "dimensions": [instance["progression_size"], instance["transverse_size"]]}, "candidate": candidate, "comparisons": comparisons, "rho": rho_result})
    all_full = all(case["candidate"]["summary"]["full_budget_exact"] for case in cases)
    all_witnesses = all(case["candidate"]["summary"]["full_budget_witnesses_valid"] for case in cases)
    all_rho = all(case["rho"]["all_solved"] for case in cases)
    accepted = {case["curve_id"]: {row["family"]: [item["budget_label"] for item in row["budgets"][:-1] if item["all_support_exact"] and item["all_held_out_support_exact"] and item["candidate_full_rank"]] for row in case["candidate"]["rows"]} for case in cases}
    output = {"valid": bool(all_full and all_witnesses and all_rho), "protocol": "EXP-ECDLP-TT-SHARED-SIGN-OPERATOR-001-harness-generator-v1", "inputs": {"seeds": FRESH_SEEDS, "field_bits": 14, "families": FAMILIES, "budgets": BUDGETS, "held_out_targets": 32, "reference_raw_sha256": sha256(REFERENCE_RAW)}, "cases": cases, "summary": {"all_full_budget_exact": all_full, "all_full_budget_witnesses_valid": all_witnesses, "all_rho_solved": all_rho, "accepted_subfull_budgets": accepted, "total_rho_group_operations": sum(case["rho"]["total_group_operations"] for case in cases), "boundary": "Two fresh 14-bit paired shared-sign source-state replications with exact lift and committed naive/original comparators; no generic ECDLP or exponent claim."}}
    print(json.dumps(output, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
