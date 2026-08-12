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
BASE_SOURCE = REPO_ROOT / "experiments" / "EXP-ECDLP-TT-PROJECTIVE-16BIT-001" / "src" / "run_projective_16bit_harness.py"
INPUT_SOURCE = SCRIPT_PATH.with_name("rank_batch_relation_input.py")
PROJECTIVE_SOURCE = REPO_ROOT / "experiments" / "EXP-ECDLP-TT-PROJECTIVE-SHARED-SIGN-001" / "src" / "projective_shared_sign_locator.py"


def load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BASE = load("rank_completion_projective_16bit_base", BASE_SOURCE)
INPUT = load("rank_completion_relation_input", INPUT_SOURCE)
FRESH = BASE.FRESH
PROJECTIVE = BASE.PROJECTIVE
ORBIT = BASE.ORBIT
AFFINE = BASE.AFFINE
FRESH_SEEDS = [97531]
FIELD_BITS = 16
FAMILIES = ["source_prf_x", "random_x"]
BUDGETS = ["96", "full"]
INVERSION_WEIGHTS = [10, 50, 100, 200]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_fixture(value: dict[str, Any]) -> dict[str, Any]:
    return BASE.canonical_fixture(value)


def charge_row(row: dict[str, Any]) -> dict[str, int]:
    return BASE.charge_row(row)


def weighted_cost(vector: dict[str, Any], weight: int) -> int:
    return BASE.weighted_cost(vector, weight)


def downstream(row: dict[str, Any]) -> dict[str, Any]:
    return BASE.downstream_summary(row)


def main() -> int:
    cases = []
    with tempfile.TemporaryDirectory(prefix="tt-projective-rank-completion-") as temp:
        root = Path(temp)
        for seed in FRESH_SEEDS:
            fixture = canonical_fixture(FRESH.run_experiment([FIELD_BITS], seed, FAMILIES, 0.5, 32))
            instance = fixture["instances"][0]
            factor_size = len(next(item for item in instance["families"] if item["family"] == FAMILIES[0])["factor_base"]["points"])
            relation_target_count = 2 * factor_size + 1
            fixture_path = root / f"fixture-{seed}.json"
            fixture_path.write_text(json.dumps(fixture, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
            relation_path = root / f"relation-{seed}.json"
            relation_input = INPUT.write_fixture_record(relation_path, fixture_path, instance["curve"]["id"], FAMILIES, relation_target_count)
            candidate = PROJECTIVE.run([relation_path], fixture_path, FAMILIES, BUDGETS)
            candidate["protocol"] = "EXP-ECDLP-TT-PROJECTIVE-RANK-COMPLETION-001-candidate-v1"
            candidate["source"].update({"harness_source_sha256": sha256(SCRIPT_PATH), "locator_sha256": sha256(PROJECTIVE_SOURCE), "rank_input_sha256": sha256(INPUT_SOURCE)})
            candidate["config"].update({"budgets": BUDGETS, "field_bits": FIELD_BITS, "relation_target_count": relation_target_count, "selection_uses_targets": False, "selection_uses_relations": False})
            naive = ORBIT.run([relation_path], fixture_path, FAMILIES, ["full"])
            affine = AFFINE.run([relation_path], fixture_path, FAMILIES, ["full"])
            naive_rows = {row["family"]: row["budgets"][-1] for row in naive["rows"]}
            affine_rows = {row["family"]: row["budgets"][-1] for row in affine["rows"]}
            weighted = {}
            downstream_rows = {}
            for row in candidate["rows"]:
                family = row["family"]
                full = next(item for item in row["budgets"] if item["budget_label"] == "full")
                naive_cost = naive_rows[family].get("charged_cost", charge_row(naive_rows[family]))
                affine_cost = charge_row(affine_rows[family])
                weighted[family] = {str(weight): {"projective": weighted_cost(full["charged_cost"], weight), "naive_orbit": weighted_cost(naive_cost, weight), "original_affine": weighted_cost(affine_cost, weight)} for weight in INVERSION_WEIGHTS}
                weighted[family]["memory_bytes"] = {"projective": full["candidate_advice"]["source_orbit_cache_bytes"], "naive_orbit": naive_rows[family]["candidate_advice"].get("source_orbit_cache_bytes", 0), "original_affine": affine_rows[family]["candidate_advice"].get("source_cache_peak_bytes", 0)}
                downstream_rows[family] = [downstream(item) for item in row["budgets"]]
            rho = BASE.rho_for_fixture(fixture, relation_input)
            cases.append({"seed": seed, "curve_id": instance["curve"]["id"], "curve": {"p": instance["curve"]["p"], "q": instance["curve"]["q"], "dimensions": [instance["progression_size"], instance["transverse_size"]]}, "relation_target_count": relation_target_count, "candidate": candidate, "comparisons": {family: {"naive_orbit_full": naive_rows[family], "original_full": affine_rows[family]} for family in FAMILIES}, "weighted_costs": weighted, "downstream": downstream_rows, "rho": rho})
    all_full = all(case["candidate"]["summary"].get("full_budget_exact") for case in cases)
    all_witnesses = all(case["candidate"]["summary"].get("full_budget_witnesses_valid") for case in cases)
    all_rho = all(case["rho"]["all_solved"] for case in cases)
    accepted = {case["curve_id"]: {row["family"]: [item["budget_label"] for item in row["budgets"][:-1] if item["all_support_exact"] and item["all_held_out_support_exact"] and item["candidate_full_rank"]] for row in case["candidate"]["rows"]} for case in cases}
    rank_summary = {
        case["curve_id"]: {
            row["family"]: {
                "full_rank": next(item for item in row["budgets"] if item["budget_label"] == "full")["candidate_rank"],
                "target_dimension": 15,
            }
            for row in case["candidate"]["rows"]
        }
        for case in cases
    }
    weighted_cells = sum(all(case["weighted_costs"][family][str(weight)]["projective"] < case["weighted_costs"][family][str(weight)]["naive_orbit"] and case["weighted_costs"][family][str(weight)]["projective"] < case["weighted_costs"][family][str(weight)]["original_affine"] for weight in INVERSION_WEIGHTS) for case in cases for family in FAMILIES)
    output = {"valid": bool(all_full and all_witnesses and all_rho), "protocol": "EXP-ECDLP-TT-PROJECTIVE-RANK-COMPLETION-001-harness-generator-v1", "inputs": {"seeds": FRESH_SEEDS, "field_bits": FIELD_BITS, "families": FAMILIES, "budgets": BUDGETS, "relation_target_multiplier": 2, "inversion_weights": INVERSION_WEIGHTS}, "cases": cases, "summary": {"all_full_budget_exact": all_full, "all_full_budget_witnesses_valid": all_witnesses, "all_rho_solved": all_rho, "accepted_subfull_budgets": accepted, "rank_summary": rank_summary, "weighted_advantage_cells": weighted_cells, "weighted_total_cells": len(cases) * len(FAMILIES), "total_rho_group_operations": sum(case["rho"]["total_group_operations"] for case in cases), "boundary": "One fresh 16-bit expanded-target projective rank-completion control with exact support, weighted comparators, relation/rank accounting, and matched rho; no generic ECDLP or exponent claim."}}
    print(json.dumps(output, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
