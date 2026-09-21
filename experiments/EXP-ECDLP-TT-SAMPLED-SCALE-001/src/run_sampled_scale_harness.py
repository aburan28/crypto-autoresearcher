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


FIXTURE_PATH = REPO_ROOT / "experiments" / "EXP-ECDLP-COORD-EXPANSION-001" / "development" / "TYPED-ADAPTIVE-FRESH-SEED-FIXTURE-V1" / "RUN-001" / "raw-result.json"
SCALE_SRC = REPO_ROOT / "experiments" / "EXP-ECDLP-COORD-EXPANSION-001" / "src"
LOCATOR_SOURCE = SCALE_SRC / "typed_tt_sampled_locator.py"
INPUT_SOURCE = SCRIPT_PATH.with_name("typed_tt_sampled_relation_input.py")

CURVE_ID = "recursive-toy-p16267-a10934-b358-q16057"
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


INPUT = _load("sampled_scale_relation_input", INPUT_SOURCE)
LOCATOR = _load("sampled_scale_locator", LOCATOR_SOURCE)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _rho_rows(relation_input: dict[str, Any], fixture: dict[str, Any]) -> list[dict[str, Any]]:
    instance = next(item for item in fixture["instances"] if item["curve"]["id"] == CURVE_ID)
    curve_record = instance["curve"]
    rows = []
    for row in relation_input["rows"]:
        curve = EllipticCurve(curve_record["p"], curve_record["a"], curve_record["b"])
        generator = tuple(curve_record["generator"])
        target_results = []
        total_ops = 0
        all_solved = True
        for target in row["shared_candidate"]["transcripts"]:
            q_point = tuple(target["target"])
            inst = ECDLPInstance(
                p=curve_record["p"],
                a=curve_record["a"],
                b=curve_record["b"],
                P=generator,
                Q=q_point,
                n=curve_record["q"],
                k=int(target["scalar"]),
                field_bits=int(curve_record["p"]).bit_length(),
                seed=int(target["scalar"]) ^ 0xC0FFEE,
            )
            result = rho.solve(inst)
            direct_valid = result.solved and curve.mul(int(result.k), generator) == q_point
            all_solved = all_solved and direct_valid
            total_ops += result.total_group_operations
            target_results.append({
                "target_index": target["target_index"],
                "label": target["label"],
                "solved": bool(result.solved),
                "recovered_k": result.k,
                "direct_certificate_valid": bool(direct_valid),
                "group_operations": result.group_operations,
                "total_group_operations": result.total_group_operations,
                "iterations": result.iterations,
            })
        rows.append({
            "family": row["family"],
            "target_count": len(target_results),
            "all_solved": all_solved,
            "total_group_operations": total_ops,
            "targets": target_results,
        })
    return rows


def main() -> int:
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory(prefix="tt-sampled-scale-") as temp:
        relation_path = Path(temp) / "relation-input.json"
        relation_input = INPUT.write_fixture_record(
            relation_path, FIXTURE_PATH, CURVE_ID, FAMILIES
        )
        candidate = LOCATOR.run(
            [relation_path], FIXTURE_PATH, FAMILIES, BUDGETS
        )
        rho_rows = _rho_rows(relation_input, fixture)
    rho_summary = {
        "rows": len(rho_rows),
        "all_solved": all(row["all_solved"] for row in rho_rows),
        "total_group_operations": sum(row["total_group_operations"] for row in rho_rows),
        "by_family": rho_rows,
    }
    candidate_summary = candidate["summary"]
    valid = bool(
        candidate_summary["full_budget_exact"]
        and candidate_summary["full_budget_witnesses_valid"]
        and rho_summary["all_solved"]
    )
    output = {
        "valid": valid,
        "protocol": "EXP-ECDLP-TT-SAMPLED-SCALE-001-harness-generator-v1",
        "input": {
            "fixture": str(FIXTURE_PATH.relative_to(REPO_ROOT)),
            "fixture_sha256": _sha256(FIXTURE_PATH),
            "curve_id": CURVE_ID,
            "families": FAMILIES,
            "budgets": BUDGETS,
        },
        "candidate": candidate,
        "rho": rho_summary,
        "summary": {
            "full_budget_exact": candidate_summary["full_budget_exact"],
            "full_budget_witnesses_valid": candidate_summary["full_budget_witnesses_valid"],
            "rho_all_solved": rho_summary["all_solved"],
            "subfull_exact_budgets": candidate_summary["subfull_exact_budgets"],
            "boundary": "Fresh p16267 fixed-curve sampled locator plus matched toy Pollard-rho certificates; no generic ECDLP or exponent claim.",
        },
    }
    print(json.dumps(output, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
