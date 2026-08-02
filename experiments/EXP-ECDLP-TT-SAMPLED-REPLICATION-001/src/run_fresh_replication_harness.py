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

from harness import rho  # noqa: E402
from harness.toycurve import ECDLPInstance, EllipticCurve  # noqa: E402


COORD_SRC = REPO_ROOT / "experiments" / "EXP-ECDLP-COORD-EXPANSION-001" / "src"
FRESH_SOURCE = COORD_SRC / "typed_five_ec.py"
LOCATOR_SOURCE = COORD_SRC / "typed_tt_sampled_locator.py"
INPUT_SOURCE = REPO_ROOT / "experiments" / "EXP-ECDLP-TT-SAMPLED-SCALE-001" / "src" / "typed_tt_sampled_relation_input.py"
FRESH_SEEDS = [271828, 161803]
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


FRESH = _load("fresh_typed_five_ec_replication", FRESH_SOURCE)
INPUT = _load("fresh_replication_relation_input", INPUT_SOURCE)
LOCATOR = _load("fresh_replication_sampled_locator", LOCATOR_SOURCE)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_fixture(value: dict[str, Any]) -> dict[str, Any]:
    # Wall time is runner metadata, not part of the deterministic fixture.
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


def _rho_for_fixture(fixture: dict[str, Any], relation_input: dict[str, Any]) -> dict[str, Any]:
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
                p=curve_record["p"], a=curve_record["a"], b=curve_record["b"],
                P=generator, Q=q_point, n=curve_record["q"],
                k=int(target["scalar"]), field_bits=14,
                seed=int(target["scalar"]) ^ 0xC0FFEE,
            )
            result = rho.solve(instance_for_rho)
            direct_valid = result.solved and curve.mul(int(result.k), generator) == q_point
            all_solved = all_solved and bool(direct_valid)
            total_ops += result.total_group_operations
            target_results.append({
                "target_index": target["target_index"], "label": target["label"],
                "solved": bool(result.solved), "recovered_k": result.k,
                "direct_certificate_valid": bool(direct_valid),
                "group_operations": result.group_operations,
                "total_group_operations": result.total_group_operations,
                "iterations": result.iterations,
            })
        by_family.append({
            "family": row["family"], "target_count": len(target_results),
            "all_solved": all_solved, "total_group_operations": total_ops,
            "targets": target_results,
        })
    return {
        "curve_id": curve_record["id"], "p": curve_record["p"], "q": curve_record["q"],
        "rows": len(by_family), "all_solved": all(item["all_solved"] for item in by_family),
        "total_group_operations": sum(item["total_group_operations"] for item in by_family),
        "by_family": by_family,
    }


def main() -> int:
    cases = []
    with tempfile.TemporaryDirectory(prefix="tt-sampled-replication-") as temp:
        temp_root = Path(temp)
        for seed in FRESH_SEEDS:
            fixture = _canonical_fixture(FRESH.run_experiment([14], seed, FAMILIES, 0.5, 32))
            fixture_path = temp_root / f"fixture-{seed}.json"
            fixture_path.write_text(
                json.dumps(fixture, sort_keys=True, separators=(",", ":")) + "\n",
                encoding="utf-8",
            )
            curve_id = fixture["instances"][0]["curve"]["id"]
            relation_path = temp_root / f"relation-{seed}.json"
            relation_input = INPUT.write_fixture_record(
                relation_path, fixture_path, curve_id, FAMILIES
            )
            candidate = LOCATOR.run([relation_path], fixture_path, FAMILIES, BUDGETS)
            rho_result = _rho_for_fixture(fixture, relation_input)
            cases.append({
                "seed": seed,
                "curve_id": curve_id,
                "curve": {
                    "p": fixture["instances"][0]["curve"]["p"],
                    "q": fixture["instances"][0]["curve"]["q"],
                    "dimensions": [fixture["instances"][0]["progression_size"], fixture["instances"][0]["transverse_size"]],
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
        "protocol": "EXP-ECDLP-TT-SAMPLED-REPLICATION-001-harness-generator-v1",
        "inputs": {"seeds": FRESH_SEEDS, "field_bits": 14, "families": FAMILIES, "budgets": BUDGETS, "occupancy_lambda": 0.5, "held_out_targets": 32},
        "cases": cases,
        "summary": {
            "all_full_budget_exact": all_full,
            "all_full_budget_witnesses_valid": all_witnesses,
            "all_rho_solved": all_rho,
            "accepted_subfull_budgets": accepted,
            "total_rho_group_operations": sum(case["rho"]["total_group_operations"] for case in cases),
            "boundary": "Two fresh 14-bit fixed-curve sampled locator replications with matched toy Pollard-rho certificates; no generic ECDLP or exponent claim.",
        },
    }
    print(json.dumps(output, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
