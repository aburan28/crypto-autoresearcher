#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[3]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "src"))

PREVIOUS_SOURCE = REPO_ROOT / "experiments" / "EXP-ECDLP-TT-SOURCE-AWARE-REPLICATION-001" / "src" / "run_source_aware_replication_harness.py"
SELECTOR_SOURCE = SCRIPT_PATH.with_name("compositional_suffix_selector.py")


def _load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BASE = _load("source_aware_runner_for_orbit_replication", PREVIOUS_SOURCE)
SELECTOR = _load("compositional_suffix_selector", SELECTOR_SOURCE)
BASE.SELECTOR = SELECTOR
BASE.SELECTOR_SOURCE = SELECTOR_SOURCE


def main() -> int:
    cases = []
    with __import__("tempfile").TemporaryDirectory(prefix="tt-source-orbit-replication-") as temp:
        temp_root = Path(temp)
        for seed in BASE.FRESH_SEEDS:
            fixture = BASE._canonical_fixture(BASE.FRESH.run_experiment([14], seed, BASE.FAMILIES, 0.5, 32))
            fixture_path = temp_root / f"fixture-{seed}.json"
            fixture_path.write_text(json.dumps(fixture, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
            instance = fixture["instances"][0]
            curve_id = instance["curve"]["id"]
            relation_path = temp_root / f"relation-{seed}.json"
            relation_input = BASE.INPUT.write_fixture_record(relation_path, fixture_path, curve_id, BASE.FAMILIES)
            selector_orders = {
                (len(item["factor_base"]["points"]), item["run_seed"] ^ 0x5A17C0DE): BASE._selector_order(instance["curve"], item)
                for item in instance["families"]
            }
            candidate = BASE._run_candidate([relation_path], fixture_path, fixture, selector_orders)
            candidate["protocol"] = "EXP-ECDLP-TT-SOURCE-ORBIT-REPLICATION-001-candidate-v1"
            rho_result = BASE.BASE._rho_for_fixture(fixture, relation_input)
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
        "protocol": "EXP-ECDLP-TT-SOURCE-ORBIT-REPLICATION-001-harness-generator-v1",
        "inputs": {"seeds": BASE.FRESH_SEEDS, "field_bits": 14, "families": BASE.FAMILIES, "budgets": BASE.BUDGETS, "occupancy_lambda": 0.5, "held_out_targets": 32, "selector": SELECTOR.SELECTOR_NAME},
        "cases": cases,
        "summary": {
            "all_full_budget_exact": all_full,
            "all_full_budget_witnesses_valid": all_witnesses,
            "all_rho_solved": all_rho,
            "accepted_subfull_budgets": accepted,
            "total_rho_group_operations": sum(case["rho"]["total_group_operations"] for case in cases),
            "boundary": "Two fresh 14-bit fixed-curve source pair-sum orbit-order replications with matched toy Pollard-rho certificates; no generic ECDLP or exponent claim.",
        },
    }
    print(json.dumps(output, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

