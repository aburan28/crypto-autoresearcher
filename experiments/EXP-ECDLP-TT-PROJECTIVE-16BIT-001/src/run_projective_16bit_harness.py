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
BASE_RUNNER = REPO_ROOT / "experiments" / "EXP-ECDLP-TT-PROJECTIVE-SHARED-SIGN-001" / "src" / "run_projective_shared_sign_harness.py"


def load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BASE = load("projective_16bit_base_runner", BASE_RUNNER)
FRESH = BASE.FRESH
INPUT = BASE.INPUT
PROJECTIVE = BASE.PROJECTIVE
ORBIT = BASE.ORBIT
AFFINE = BASE.AFFINE
FRESH_SEEDS = [97531, 86420]
FIELD_BITS = 16
FAMILIES = ["source_prf_x", "random_x"]
BUDGETS = ["64", "96", "full"]
INVERSION_WEIGHTS = [10, 50, 100, 200]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def charge_row(row: dict[str, Any]) -> dict[str, int]:
    vectors = [row.get(name, {}) for name in ["candidate_source_ops", "candidate_advice_build_ops", "candidate_reconstruction_ops", "candidate_witness_ops", "candidate_relation_matrix_ops"]]
    keys = {key for vector in vectors for key in vector}
    return {key: sum(int(vector.get(key, 0)) for vector in vectors) for key in sorted(keys)}


def weighted_cost(vector: dict[str, Any], inversion_weight: int) -> int:
    return int(vector.get("field_multiplications", 0)) + inversion_weight * int(vector.get("field_inversions", 0))


def canonical_fixture(value: dict[str, Any]) -> dict[str, Any]:
    def normalize(item: Any) -> Any:
        if isinstance(item, dict):
            return {key: normalize(child) for key, child in item.items() if key not in {"wall_seconds", "total_wall_seconds"}}
        if isinstance(item, list):
            return [normalize(child) for child in item]
        return item
    return normalize(value)


def rho_for_fixture(fixture: dict[str, Any], relation_input: dict[str, Any]) -> dict[str, Any]:
    from harness import rho
    from harness.toycurve import ECDLPInstance, EllipticCurve

    instance = fixture["instances"][0]
    curve_record = instance["curve"]
    curve = EllipticCurve(curve_record["p"], curve_record["a"], curve_record["b"])
    generator = tuple(curve_record["generator"])
    by_family = []
    for row in relation_input["rows"]:
        target_results = []
        total_ops = 0
        all_solved = True
        for target in row["shared_candidate"]["transcripts"]:
            q_point = tuple(target["target"])
            instance_for_rho = ECDLPInstance(
                p=curve_record["p"], a=curve_record["a"], b=curve_record["b"], P=generator,
                Q=q_point, n=curve_record["q"], k=int(target["scalar"]), field_bits=FIELD_BITS,
                seed=int(target["scalar"]) ^ 0xC0FFEE,
            )
            result = rho.solve(instance_for_rho)
            direct_valid = result.solved and curve.mul(int(result.k), generator) == q_point
            all_solved = all_solved and bool(direct_valid)
            total_ops += result.total_group_operations
            target_results.append({"target_index": target["target_index"], "label": target["label"], "solved": bool(result.solved), "recovered_k": result.k, "direct_certificate_valid": bool(direct_valid), "group_operations": result.group_operations, "total_group_operations": result.total_group_operations, "iterations": result.iterations})
        by_family.append({"family": row["family"], "target_count": len(target_results), "all_solved": all_solved, "total_group_operations": total_ops, "targets": target_results})
    return {"curve_id": curve_record["id"], "p": curve_record["p"], "q": curve_record["q"], "rows": len(by_family), "all_solved": all(item["all_solved"] for item in by_family), "total_group_operations": sum(item["total_group_operations"] for item in by_family), "by_family": by_family}


def downstream_summary(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "budget_label": row["budget_label"],
        "candidate_rank": row["candidate_rank"],
        "rowspace_rank": row["rowspace_rank"],
        "relation_equation_count": len(row.get("relation_equations", [])),
        "candidate_relation_matrix_ops": row.get("candidate_relation_matrix_ops", {}),
        "candidate_witness_ops": row.get("candidate_witness_ops", {}),
        "candidate_lift_queries": row.get("candidate_lift_queries", 0),
        "target_count": row.get("target_count", 0),
    }


def main() -> int:
    cases = []
    with tempfile.TemporaryDirectory(prefix="tt-projective-16bit-") as temp:
        root = Path(temp)
        for seed in FRESH_SEEDS:
            fixture = canonical_fixture(FRESH.run_experiment([FIELD_BITS], seed, FAMILIES, 0.5, 32))
            fixture_path = root / f"fixture-{seed}.json"
            fixture_path.write_text(json.dumps(fixture, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
            curve_id = fixture["instances"][0]["curve"]["id"]
            relation_path = root / f"relation-{seed}.json"
            relation_input = INPUT.write_fixture_record(relation_path, fixture_path, curve_id, FAMILIES)
            candidate = PROJECTIVE.run([relation_path], fixture_path, FAMILIES, BUDGETS)
            candidate["protocol"] = "EXP-ECDLP-TT-PROJECTIVE-16BIT-001-candidate-v1"
            candidate["source"].update({"harness_source_sha256": sha256(SCRIPT_PATH), "projective_locator_sha256": sha256(BASE.PROJECTIVE_SOURCE), "locator_sha256": sha256(BASE.PROJECTIVE_SOURCE)})
            candidate["config"].update({"budgets": BUDGETS, "field_bits": FIELD_BITS, "selection_uses_targets": False, "selection_uses_relations": False})
            naive = ORBIT.run([relation_path], fixture_path, FAMILIES, ["full"])
            affine = AFFINE.run([relation_path], fixture_path, FAMILIES, ["full"])
            naive_rows = {row["family"]: row["budgets"][-1] for row in naive["rows"]}
            affine_rows = {row["family"]: row["budgets"][-1] for row in affine["rows"]}
            weighted = {}
            downstream = {}
            for row in candidate["rows"]:
                family = row["family"]
                projective_full = next(item for item in row["budgets"] if item["budget_label"] == "full")
                projective_cost = projective_full["charged_cost"]
                naive_cost = naive_rows[family].get("charged_cost", charge_row(naive_rows[family]))
                affine_cost = charge_row(affine_rows[family])
                weighted[family] = {
                    str(weight): {"projective": weighted_cost(projective_cost, weight), "naive_orbit": weighted_cost(naive_cost, weight), "original_affine": weighted_cost(affine_cost, weight)}
                    for weight in INVERSION_WEIGHTS
                }
                weighted[family]["memory_bytes"] = {"projective": projective_full["candidate_advice"]["source_orbit_cache_bytes"], "naive_orbit": naive_rows[family]["candidate_advice"].get("source_orbit_cache_bytes", 0), "original_affine": affine_rows[family]["candidate_advice"].get("source_cache_peak_bytes", 0)}
                downstream[family] = [downstream_summary(item) for item in row["budgets"]]
            rho_result = rho_for_fixture(fixture, relation_input)
            instance = fixture["instances"][0]
            cases.append({"seed": seed, "curve_id": curve_id, "curve": {"p": instance["curve"]["p"], "q": instance["curve"]["q"], "dimensions": [instance["progression_size"], instance["transverse_size"]]}, "candidate": candidate, "comparisons": {family: {"naive_orbit_full": naive_rows[family], "original_full": affine_rows[family]} for family in FAMILIES}, "weighted_costs": weighted, "downstream": downstream, "rho": rho_result})
    all_full = all(case["candidate"]["summary"]["all_full_budget_exact"] if "all_full_budget_exact" in case["candidate"]["summary"] else case["candidate"]["summary"].get("full_budget_exact") for case in cases)
    all_witnesses = all(case["candidate"]["summary"].get("full_budget_witnesses_valid") for case in cases)
    all_rho = all(case["rho"]["all_solved"] for case in cases)
    accepted = {case["curve_id"]: {row["family"]: [item["budget_label"] for item in row["budgets"][:-1] if item["all_support_exact"] and item["all_held_out_support_exact"] and item["candidate_full_rank"]] for row in case["candidate"]["rows"]} for case in cases}
    weighted_advantage_cells = 0
    for case in cases:
        for family in FAMILIES:
            weighted_advantage_cells += all(case["weighted_costs"][family][str(weight)]["projective"] < case["weighted_costs"][family][str(weight)]["naive_orbit"] and case["weighted_costs"][family][str(weight)]["projective"] < case["weighted_costs"][family][str(weight)]["original_affine"] for weight in INVERSION_WEIGHTS)
    output = {"valid": bool(all_full and all_witnesses and all_rho), "protocol": "EXP-ECDLP-TT-PROJECTIVE-16BIT-001-harness-generator-v1", "inputs": {"seeds": FRESH_SEEDS, "field_bits": FIELD_BITS, "families": FAMILIES, "budgets": BUDGETS, "inversion_weights": INVERSION_WEIGHTS, "occupancy_lambda": 0.5, "held_out_targets": 32}, "cases": cases, "summary": {"all_full_budget_exact": all_full, "all_full_budget_witnesses_valid": all_witnesses, "all_rho_solved": all_rho, "accepted_subfull_budgets": accepted, "weighted_advantage_cells": weighted_advantage_cells, "weighted_total_cells": len(cases) * len(FAMILIES), "total_rho_group_operations": sum(case["rho"]["total_group_operations"] for case in cases), "boundary": "Two fresh 16-bit projective shared-sign replications with weighted arithmetic, relation/rank accounting, independent affine comparators, and matched rho; no generic ECDLP or exponent claim."}}
    print(json.dumps(output, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
