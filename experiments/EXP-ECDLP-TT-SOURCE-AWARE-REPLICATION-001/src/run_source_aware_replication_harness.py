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


BASE = _load("fresh_replication_base_for_source_aware", BASE_SOURCE)
SELECTOR = _load("source_aware_suffix_selector", SELECTOR_SOURCE)
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


def _run_candidate(relation_paths: list[Path], fixture_path: Path, fixture: dict[str, Any], selector_orders: dict[tuple[int, int], dict[str, Any]]) -> dict[str, Any]:
    original = LOCATOR.sampled_columns

    def source_columns(b_size: int, budget: int, seed: int) -> list[int]:
        record = selector_orders[(b_size, int(seed))]
        order = record["order"]
        return order if budget >= b_size * b_size else order[:budget]

    LOCATOR.sampled_columns = source_columns
    try:
        candidate = LOCATOR.run(relation_paths, fixture_path, FAMILIES, BUDGETS)
    finally:
        LOCATOR.sampled_columns = original
    candidate["protocol"] = "EXP-ECDLP-TT-SOURCE-AWARE-REPLICATION-001-candidate-v1"
    candidate["source"]["selector_sha256"] = _sha256(SELECTOR_SOURCE)
    candidate["source"]["base_locator_sha256"] = _sha256(BASE.LOCATOR_SOURCE)
    candidate["config"].update({
        "budgets": BUDGETS,
        "locator": SELECTOR.SELECTOR_NAME,
        "selector_definition": SELECTOR.SELECTOR_DEFINITION,
        "selection_uses_targets": False,
        "selection_uses_relations": False,
        "selector_source_only": True,
    })
    instance = fixture["instances"][0]
    candidate["selector_records"] = {
        family: selector_orders[(
            len(next(item for item in instance["families"] if item["family"] == family)["factor_base"]["points"]),
            next(item for item in instance["families"] if item["family"] == family)["run_seed"] ^ 0x5A17C0DE,
        )]
        for family in FAMILIES
    }
    return candidate


def main() -> int:
    cases = []
    with tempfile.TemporaryDirectory(prefix="tt-source-aware-replication-") as temp:
        temp_root = Path(temp)
        for seed in FRESH_SEEDS:
            fixture = _canonical_fixture(FRESH.run_experiment([14], seed, FAMILIES, 0.5, 32))
            fixture_path = temp_root / f"fixture-{seed}.json"
            fixture_path.write_text(json.dumps(fixture, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
            curve_id = fixture["instances"][0]["curve"]["id"]
            relation_path = temp_root / f"relation-{seed}.json"
            relation_input = INPUT.write_fixture_record(relation_path, fixture_path, curve_id, FAMILIES)
            instance = fixture["instances"][0]
            selector_orders = {
                (len(item["factor_base"]["points"]), item["run_seed"] ^ 0x5A17C0DE): _selector_order(instance["curve"], item)
                for item in instance["families"]
            }
            candidate = _run_candidate([relation_path], fixture_path, fixture, selector_orders)
            rho_result = BASE._rho_for_fixture(fixture, relation_input)
            cases.append({
                "seed": seed,
                "curve_id": curve_id,
                "curve": {
                    "p": instance["curve"]["p"],
                    "q": instance["curve"]["q"],
                    "dimensions": [instance["progression_size"], instance["transverse_size"]],
                },
                "candidate": candidate,
                "rho": rho_result,
            })
    all_full = all(case["candidate"]["summary"]["full_budget_exact"] for case in cases)
    all_witnesses = all(case["candidate"]["summary"]["full_budget_witnesses_valid"] for case in cases)
    all_rho = all(case["rho"]["all_solved"] for case in cases)
    accepted = {
        case["curve_id"]: {
            row["family"]: [
                budget["budget_label"]
                for budget in row["budgets"][:-1]
                if budget["all_support_exact"]
                and budget["all_held_out_support_exact"]
                and budget["candidate_full_rank"]
            ]
            for row in case["candidate"]["rows"]
        }
        for case in cases
    }
    output = {
        "valid": bool(all_full and all_witnesses and all_rho),
        "protocol": "EXP-ECDLP-TT-SOURCE-AWARE-REPLICATION-001-harness-generator-v1",
        "inputs": {
            "seeds": FRESH_SEEDS,
            "field_bits": 14,
            "families": FAMILIES,
            "budgets": BUDGETS,
            "occupancy_lambda": 0.5,
            "held_out_targets": 32,
            "selector": SELECTOR.SELECTOR_NAME,
        },
        "cases": cases,
        "summary": {
            "all_full_budget_exact": all_full,
            "all_full_budget_witnesses_valid": all_witnesses,
            "all_rho_solved": all_rho,
            "accepted_subfull_budgets": accepted,
            "total_rho_group_operations": sum(case["rho"]["total_group_operations"] for case in cases),
            "boundary": "Two fresh 14-bit fixed-curve source-aware suffix-order replications with matched toy Pollard-rho certificates; no generic ECDLP or exponent claim.",
        },
    }
    print(json.dumps(output, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
