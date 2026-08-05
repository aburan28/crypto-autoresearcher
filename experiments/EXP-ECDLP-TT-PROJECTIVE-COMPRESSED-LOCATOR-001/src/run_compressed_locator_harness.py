#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[3]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "src"))
BASE_SOURCE = REPO_ROOT / "experiments" / "EXP-ECDLP-TT-PROJECTIVE-TARGET-STREAM-001" / "src" / "run_target_stream_harness.py"
INPUT_SOURCE = REPO_ROOT / "experiments" / "EXP-ECDLP-TT-PROJECTIVE-TARGET-STREAM-001" / "src" / "rank_batch_relation_input.py"
LOCATOR_SOURCE = SCRIPT_PATH.with_name("compressed_projective_shared_sign_locator.py")


def load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BASE = load("compressed_locator_base_runner", BASE_SOURCE)
INPUT = load("compressed_locator_relation_input", INPUT_SOURCE)
PROJECTIVE = load("compressed_locator_projective", LOCATOR_SOURCE)
FRESH = BASE.FRESH
ORBIT = BASE.ORBIT
AFFINE = BASE.AFFINE
FRESH_SEEDS = [int(os.environ.get("FRESH_SEED", "86420"))]
FIELD_BITS = int(os.environ.get("FIELD_BITS", "16"))
FAMILIES = ["source_prf_x", "random_x"]
BUDGETS = ["96", "full"]
INVERSION_WEIGHTS = [10, 50, 100, 200]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_fixture(value: dict[str, Any]) -> dict[str, Any]:
    return BASE.canonical_fixture(value)


def charge_row(row: dict[str, Any]) -> dict[str, int]:
    return BASE.charge_row(row)


def weighted_cost(vector: dict[str, int], weight: int) -> int:
    return BASE.weighted_cost(vector, weight)


def downstream(row: dict[str, Any]) -> dict[str, Any]:
    return BASE.downstream(row)


def main() -> int:
    cases = []
    with tempfile.TemporaryDirectory(prefix="tt-projective-compressed-") as temp:
        root = Path(temp)
        for seed in FRESH_SEEDS:
            fixture = canonical_fixture(FRESH.run_experiment([FIELD_BITS], seed, FAMILIES, 0.5, 32))
            instance = fixture["instances"][0]
            factor_size = len(next(item for item in instance["families"] if item["family"] == FAMILIES[0])["factor_base"]["points"])
            relation_target_count = 3 * factor_size + 1
            fixture_path = root / f"fixture-{seed}.json"
            fixture_path.write_text(json.dumps(fixture, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
            relation_path = root / f"relation-{seed}.json"
            relation_input = INPUT.write_fixture_record(relation_path, fixture_path, instance["curve"]["id"], FAMILIES, relation_target_count)
            candidate = PROJECTIVE.run([relation_path], fixture_path, FAMILIES, BUDGETS)
            candidate["protocol"] = "EXP-ECDLP-TT-PROJECTIVE-COMPRESSED-LOCATOR-001-candidate-v1"
            candidate["source"].update({"harness_source_sha256": sha256(SCRIPT_PATH), "locator_sha256": sha256(LOCATOR_SOURCE), "input_source_sha256": sha256(INPUT_SOURCE)})
            candidate["config"].update({"field_bits": FIELD_BITS, "relation_target_count": relation_target_count, "selection_uses_targets": False, "selection_uses_relations": False})
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
                weighted[family] = {str(weight): {"compressed": weighted_cost(full["charged_cost"], weight), "naive_orbit": weighted_cost(naive_cost, weight), "original_affine": weighted_cost(affine_cost, weight)} for weight in INVERSION_WEIGHTS}
                weighted[family]["prefix_fraction"] = PROJECTIVE.PREFIX_FRACTION
                downstream_rows[family] = [downstream(item) for item in row["budgets"]]
            rho = BASE.BASE.rho_for_fixture(fixture, relation_input)
            cases.append({"seed": seed, "curve_id": instance["curve"]["id"], "curve": {"p": instance["curve"]["p"], "q": instance["curve"]["q"], "dimensions": [instance["progression_size"], instance["transverse_size"]]}, "relation_target_count": relation_target_count, "candidate": candidate, "comparisons": {family: {"naive_orbit_full": naive_rows[family], "original_full": affine_rows[family]} for family in FAMILIES}, "weighted_costs": weighted, "downstream": downstream_rows, "rho": rho})
    all_full = all(case["candidate"]["summary"].get("full_budget_exact") for case in cases)
    all_witnesses = all(case["candidate"]["summary"].get("full_budget_witnesses_valid") for case in cases)
    all_rho = all(case["rho"]["all_solved"] for case in cases)
    prefix_rows = [item for case in cases for row in case["candidate"]["rows"] for item in row["budgets"]]
    weighted_cells = sum(all(case["weighted_costs"][family][str(weight)]["compressed"] < case["weighted_costs"][family][str(weight)]["naive_orbit"] and case["weighted_costs"][family][str(weight)]["compressed"] < case["weighted_costs"][family][str(weight)]["original_affine"] for weight in INVERSION_WEIGHTS) for case in cases for family in FAMILIES)
    output = {"valid": bool(all_full and all_witnesses and all_rho), "protocol": "EXP-ECDLP-TT-PROJECTIVE-COMPRESSED-LOCATOR-001-harness-generator-v1", "inputs": {"seeds": FRESH_SEEDS, "field_bits": FIELD_BITS, "families": FAMILIES, "budgets": BUDGETS, "relation_target_multiplier": 3, "prefix_fraction": PROJECTIVE.PREFIX_FRACTION, "selector": PROJECTIVE.SELECTOR, "target_cache_mode": "streaming-one-target-at-a-time"}, "cases": cases, "summary": {"all_full_budget_exact": all_full, "all_full_budget_witnesses_valid": all_witnesses, "all_rho_solved": all_rho, "weighted_advantage_cells": weighted_cells, "weighted_total_cells": len(cases) * len(FAMILIES), "selected_prefix_counts": sorted({item.get("selected_prefix_count") for item in prefix_rows}), "full_prefix_counts": sorted({item.get("full_prefix_count") for item in prefix_rows}), "prefix_fraction": PROJECTIVE.PREFIX_FRACTION, "total_rho_group_operations": sum(case["rho"]["total_group_operations"] for case in cases), "boundary": f"One fresh {FIELD_BITS}-bit source-only half-prefix projective locator with exact full-prefix oracle comparison; no generic ECDLP or exponent claim."}}
    print(json.dumps(output, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
