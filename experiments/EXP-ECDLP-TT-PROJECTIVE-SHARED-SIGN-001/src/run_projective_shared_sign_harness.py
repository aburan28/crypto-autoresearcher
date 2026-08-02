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
PROJECTIVE_SOURCE = SCRIPT_PATH.with_name("projective_shared_sign_locator.py")
ORBIT_SOURCE = REPO_ROOT / "experiments" / "EXP-ECDLP-TT-SOURCE-ORBIT-QUOTIENT-001" / "src" / "orbit_quotient_locator.py"
AFFINE_SOURCE = REPO_ROOT / "experiments" / "EXP-ECDLP-COORD-EXPANSION-001" / "src" / "typed_tt_sampled_locator.py"


def load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BASE = load("projective_shared_sign_fresh_base", BASE_SOURCE)
INPUT = load("projective_shared_sign_relation_input", INPUT_SOURCE)
PROJECTIVE = load("projective_shared_sign_locator", PROJECTIVE_SOURCE)
ORBIT = load("projective_shared_sign_affine_orbit", ORBIT_SOURCE)
AFFINE = load("projective_shared_sign_affine_full", AFFINE_SOURCE)
FRESH = BASE.FRESH
FAMILIES = BASE.FAMILIES
FRESH_SEEDS = [271828, 161803, 424242]
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


def rows_by_family(result: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {row["family"]: row["budgets"][-1] for row in result["rows"]}


def main() -> int:
    cases = []
    with tempfile.TemporaryDirectory(prefix="tt-projective-shared-sign-") as temp:
        root = Path(temp)
        for seed in FRESH_SEEDS:
            fixture = canonical_fixture(FRESH.run_experiment([14], seed, FAMILIES, 0.5, 32))
            fixture_path = root / f"fixture-{seed}.json"
            fixture_path.write_text(json.dumps(fixture, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
            curve_id = fixture["instances"][0]["curve"]["id"]
            relation_path = root / f"relation-{seed}.json"
            relation_input = INPUT.write_fixture_record(relation_path, fixture_path, curve_id, FAMILIES)
            candidate = PROJECTIVE.run([relation_path], fixture_path, FAMILIES, BUDGETS)
            candidate["protocol"] = "EXP-ECDLP-TT-PROJECTIVE-SHARED-SIGN-001-candidate-v1"
            candidate["source"].update({
                "harness_source_sha256": sha256(SCRIPT_PATH),
                "locator_sha256": sha256(PROJECTIVE_SOURCE),
                "projective_locator_sha256": sha256(PROJECTIVE_SOURCE),
                "orbit_comparator_source_sha256": sha256(ORBIT_SOURCE),
                "affine_comparator_source_sha256": sha256(AFFINE_SOURCE),
            })
            candidate["config"].update({"budgets": BUDGETS, "selection_uses_targets": False, "selection_uses_relations": False})
            naive = ORBIT.run([relation_path], fixture_path, FAMILIES, ["full"])
            affine = AFFINE.run([relation_path], fixture_path, FAMILIES, ["full"])
            comparisons = {
                family: {"naive_orbit_full": rows_by_family(naive)[family], "original_full": rows_by_family(affine)[family]}
                for family in FAMILIES
            }
            rho_result = BASE._rho_for_fixture(fixture, relation_input)
            instance = fixture["instances"][0]
            cases.append({
                "seed": seed,
                "curve_id": curve_id,
                "curve": {"p": instance["curve"]["p"], "q": instance["curve"]["q"], "dimensions": [instance["progression_size"], instance["transverse_size"]]},
                "candidate": candidate,
                "comparisons": comparisons,
                "rho": rho_result,
            })
    all_full = all(case["candidate"]["summary"]["full_budget_exact"] for case in cases)
    all_witnesses = all(case["candidate"]["summary"]["full_budget_witnesses_valid"] for case in cases)
    all_rho = all(case["rho"]["all_solved"] for case in cases)
    accepted = {
        case["curve_id"]: {
            row["family"]: [item["budget_label"] for item in row["budgets"][:-1] if item["all_support_exact"] and item["all_held_out_support_exact"] and item["candidate_full_rank"]]
            for row in case["candidate"]["rows"]
        }
        for case in cases
    }
    output = {
        "valid": bool(all_full and all_witnesses and all_rho),
        "protocol": "EXP-ECDLP-TT-PROJECTIVE-SHARED-SIGN-001-harness-generator-v1",
        "inputs": {"seeds": FRESH_SEEDS, "field_bits": 14, "families": FAMILIES, "budgets": BUDGETS, "occupancy_lambda": 0.5, "held_out_targets": 32, "predicate_scale": "source-state Z^12 per paired homogeneous predicate"},
        "cases": cases,
        "summary": {"all_full_budget_exact": all_full, "all_full_budget_witnesses_valid": all_witnesses, "all_rho_solved": all_rho, "accepted_subfull_budgets": accepted, "total_rho_group_operations": sum(case["rho"]["total_group_operations"] for case in cases), "boundary": "Three fresh 14-bit shared-Z projective source-state replications with independent affine/orbit comparators and exact lift; no generic ECDLP or exponent claim."},
    }
    print(json.dumps(output, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
