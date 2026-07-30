#!/usr/bin/env python3
"""P751 factor-first linear algebra for P750 prospective forms."""

from __future__ import annotations

import argparse
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P746_SCRIPT = TASK_DIR / "low_term_total2_p746_incremental_walk_online_cost.py"
P748_SCRIPT = TASK_DIR / "low_term_total2_p748_setup_amortization_matrix_bridge.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P750 = STATE_DIR / "low_term_total2_p750_prospective_prefix_linear_algebra_charge_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p751_factor_first_linear_algebra_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_order11779_p751_factor_first_linear_algebra.md"
SCHEMA = "ecdlp.low_term_total2_p751_factor_first_linear_algebra.v1"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {name} from {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(float(numerator) / float(denominator), 8)


def stat(values: list[int | float]) -> dict[str, Any]:
    if not values:
        return {"count": 0, "max": None, "mean": None, "median": None, "min": None}
    return {
        "count": len(values),
        "max": max(values),
        "mean": round(mean(values), 8),
        "median": median(values),
        "min": min(values),
    }


def empty_ops(width: int) -> dict[str, int]:
    return {
        "basis_rows_added": 0,
        "candidate_rows_scanned": 0,
        "eliminated_cells": 0,
        "field_additions": 0,
        "field_inversions": 0,
        "field_multiplications": 0,
        "normalized_cells": 0,
        "row_eliminations": 0,
        "total_field_ops": 0,
        "width": width,
    }


def add_row_ops(ops: dict[str, int], width: int) -> None:
    ops["field_multiplications"] += width
    ops["field_additions"] += width
    ops["eliminated_cells"] += width
    ops["row_eliminations"] += 1


def finish_ops(ops: dict[str, int]) -> dict[str, int]:
    ops["total_field_ops"] = ops["field_inversions"] + ops["field_multiplications"] + ops["field_additions"]
    return ops


def incremental_factor_solve(relations: list[dict[str, Any]], factor_count: int, order: int) -> dict[str, Any]:
    width = factor_count + 1
    basis: dict[int, list[int]] = {}
    ops = empty_ops(width)
    inconsistent_zero_rows = 0
    scanned_to_full_rank = None
    for relation in relations:
        ops["candidate_rows_scanned"] += 1
        row = [int(value) % order for value in relation["coeffs"]] + [int(relation["rhs"]) % order]
        for pivot in sorted(basis):
            factor = row[pivot] % order
            if factor:
                base = basis[pivot]
                row = [(row[index] - factor * base[index]) % order for index in range(width)]
                add_row_ops(ops, width)
        pivot = next((index for index in range(factor_count) if row[index] % order), None)
        if pivot is None:
            if row[-1] % order:
                inconsistent_zero_rows += 1
            continue
        inv = pow(row[pivot] % order, -1, order)
        row = [(value * inv) % order for value in row]
        ops["field_inversions"] += 1
        ops["field_multiplications"] += width
        ops["normalized_cells"] += width
        for existing_pivot, existing in list(basis.items()):
            factor = existing[pivot] % order
            if factor:
                basis[existing_pivot] = [
                    (existing[index] - factor * row[index]) % order
                    for index in range(width)
                ]
                add_row_ops(ops, width)
        basis[pivot] = row
        ops["basis_rows_added"] += 1
        if len(basis) == factor_count:
            scanned_to_full_rank = ops["candidate_rows_scanned"]
            break
    values = {pivot: row[-1] % order for pivot, row in basis.items()}
    return {
        "basis": basis,
        "factor_values": values,
        "full_rank": len(basis) == factor_count,
        "inconsistent_zero_rows": inconsistent_zero_rows,
        "operation_counts": finish_ops(ops),
        "rank": len(basis),
        "scanned_to_full_rank": scanned_to_full_rank,
    }


def add_expected_secrets(p746: Any, relprobe: Any, rows_by_target: dict[str, list[dict[str, Any]]]) -> dict[str, list[dict[str, Any]]]:
    out: dict[str, list[dict[str, Any]]] = {}
    for target, rows in rows_by_target.items():
        _verifier, _record, inv = p746.load_target(relprobe, target)
        label = str(inv["label"])
        p = int(inv["p"])
        order = int(inv["base_order"])
        copied_rows = []
        for row in rows:
            copied = dict(row)
            copied["_expected_secret"] = int(relprobe.deterministic_secret(label, p, order, copied["seed"]))
            copied_rows.append(copied)
        out[target] = copied_rows
    return out


def substitution_recovery(rows: list[dict[str, Any]], factor_values: dict[int, int], order: int) -> dict[str, Any]:
    recovered = []
    ops = {
        "field_additions": 0,
        "field_inversions": 0,
        "field_multiplications": 0,
        "relations_considered": 0,
        "total_field_ops": 0,
    }
    for row in rows:
        found = None
        for form in row.get("forms") or []:
            ops["relations_considered"] += 1
            coeffs = [int(value) % order for value in form["coeffs"]]
            b = coeffs[0] % order
            if not b:
                continue
            acc = int(form["rhs"]) % order
            for factor_index, factor_value in factor_values.items():
                coeff = coeffs[1 + factor_index] % order
                if coeff:
                    acc = (acc - coeff * factor_value) % order
                    ops["field_multiplications"] += 1
                    ops["field_additions"] += 1
            secret = (acc * pow(b, -1, order)) % order
            ops["field_inversions"] += 1
            ops["field_multiplications"] += 1
            found = {
                "matches_expected": secret == int(row["_expected_secret"]),
                "recovered_secret": int(secret),
                "seed_label": row["seed_label"],
                "target": row["target"],
            }
            break
        if found is None:
            found = {
                "matches_expected": False,
                "recovered_secret": None,
                "seed_label": row["seed_label"],
                "target": row["target"],
            }
        recovered.append(found)
    ops["total_field_ops"] = ops["field_inversions"] + ops["field_multiplications"] + ops["field_additions"]
    return {
        "mismatch_count": sum(1 for item in recovered if not item["matches_expected"]),
        "operation_counts": ops,
        "recovered_count": sum(1 for item in recovered if item["matches_expected"]),
        "recovered_sample": recovered[:12],
    }


def target_cost_summary(
    rows: list[dict[str, Any]],
    dense_summary: dict[str, Any],
    factor_solve: dict[str, Any],
    substitution: dict[str, Any],
) -> dict[str, Any]:
    rho = int(rows[0]["generic_rho_steps"]) if rows else 0
    setup = int(rows[0]["cost_model"]["subset_group_additions"]) if rows else 0
    group_total = setup + sum(int(row["cost_model"]["collection_online_group_additions"]) for row in rows)
    recovered = int(substitution["recovered_count"])
    baseline = recovered * rho
    factor_ops = int(factor_solve["operation_counts"]["total_field_ops"])
    sub_ops = int(substitution["operation_counts"]["total_field_ops"])
    field_ops = factor_ops + sub_ops
    dense_ops = int(((dense_summary.get("cost_summary") or {}).get("linear_algebra_field_ops")) or 0)
    return {
        "dense_p750_field_ops": dense_ops,
        "factor_first_field_ops": field_ops,
        "factor_first_field_ops_over_dense": ratio(field_ops, dense_ops),
        "factor_solve_field_ops": factor_ops,
        "group_addition_cost": group_total,
        "group_addition_cost_over_recovered_rho": ratio(group_total, baseline),
        "recovered_rho_baseline": baseline,
        "rho": rho,
        "setup_group_additions": setup,
        "substitution_field_ops": sub_ops,
        "total_unit_cost_group_additions_plus_field_ops": group_total + field_ops,
        "total_unit_cost_over_recovered_rho": ratio(group_total + field_ops, baseline),
    }


def target_summary(p748: Any, target: str, rows: list[dict[str, Any]], dense_summary: dict[str, Any], order: int) -> dict[str, Any]:
    factor_count = max((len(form["coeffs"]) - 1 for row in rows for form in row.get("forms") or []), default=0)
    factor_relations = p748.factor_eliminated_relations(rows, order, factor_count)
    factor_solve = incremental_factor_solve(factor_relations, factor_count, order)
    substitution = substitution_recovery(rows, factor_solve["factor_values"], order) if factor_solve["full_rank"] else {
        "mismatch_count": len(rows),
        "operation_counts": {"total_field_ops": 0},
        "recovered_count": 0,
        "recovered_sample": [],
    }
    return {
        "cost_summary": target_cost_summary(rows, dense_summary, factor_solve, substitution),
        "factor_relation_count": len(factor_relations),
        "factor_solve": {
            "full_rank": factor_solve["full_rank"],
            "operation_counts": factor_solve["operation_counts"],
            "rank": factor_solve["rank"],
            "scanned_to_full_rank": factor_solve["scanned_to_full_rank"],
        },
        "factor_variable_count": factor_count,
        "substitution_recovery": substitution,
        "target": target,
    }


def determine_claim(target_summaries: list[dict[str, Any]]) -> str:
    all_recovered = all(summary["substitution_recovery"]["mismatch_count"] == 0 for summary in target_summaries)
    all_reduced = all((summary["cost_summary"].get("factor_first_field_ops_over_dense") or 10**18) <= 0.1 for summary in target_summaries)
    any_unit = any((summary["cost_summary"].get("total_unit_cost_over_recovered_rho") or 10**18) < 1.0 for summary in target_summaries)
    if all_recovered and any_unit:
        return "P751_FACTOR_FIRST_UNIT_COST_BELOW_RHO_SIGNAL"
    if all_recovered and all_reduced:
        return "P751_FACTOR_FIRST_RECOVERS_ALL_DENSE_LA_REDUCED_UNIT_COST_ABOVE_RHO"
    if all_recovered:
        return "P751_FACTOR_FIRST_RECOVERS_ALL_BUT_LA_REDUCTION_WEAK"
    return "NEGATIVE_RESULT_P751_FACTOR_FIRST_SUBSTITUTION_FAILED"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p746 = load_module("ecdlp_p746_incremental_walk", P746_SCRIPT)
    p748 = load_module("ecdlp_p748_matrix_bridge", P748_SCRIPT)
    relprobe = p746.load_relation_probe_module()
    p750 = load_json(args.p750_probe)
    rows_by_target = add_expected_secrets(p746, relprobe, p750["results"])
    dense_by_target = {
        summary["target"]: summary
        for summary in ((p750.get("summary") or {}).get("target_summaries") or [])
    }
    target_summaries = []
    for target, rows in rows_by_target.items():
        _verifier, _record, inv = p746.load_target(relprobe, target)
        target_summaries.append(target_summary(p748, target, rows, dense_by_target.get(target, {}), int(inv["base_order"])))
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p750_probe": str(args.p750_probe),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(target_summaries),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MANY-TARGET MODEL: factor variables are solved from a batch sharing one target factor base.",
            "FACTOR-FIRST MODEL-BOUND: uses target-eliminated equations from the same prospective batch, then substitutes.",
            "UNIT-COST MODEL-BOUND: field ops plus group additions are a conservative accounting model, not calibrated deployment cost.",
            "NO DEPLOYED-CURVE CLAIM: no large-prime scaling or production-key relevance is implied.",
        ],
        "method": "p751_factor_first_linear_algebra",
        "parameters": {
            "p750_probe": str(args.p750_probe),
        },
        "schema": SCHEMA,
        "summary": {
            "target_summaries": target_summaries,
        },
    }


def summary_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": f"{SCHEMA}.summary",
        "created_at": payload["created_at"],
        "claim_status": payload["claim_status"],
        "honesty_boundary": payload["honesty_boundary"],
        "method": payload["method"],
        "parameters": payload["parameters"],
        "summary": payload["summary"],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p750-probe", type=Path, default=DEFAULT_P750)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--summary-out", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    summary_out = args.summary_out or args.out.with_name(args.out.stem.replace("_probe", "_summary") + args.out.suffix)
    summary = summary_from_payload(payload)
    write_json(summary_out, summary)
    print(f"wrote {args.out}")
    print(f"wrote {summary_out}")
    print(
        json.dumps(
            {
                "claim_status": summary["claim_status"],
                "targets": [
                    {
                        "cost": item["cost_summary"],
                        "factor_relation_count": item["factor_relation_count"],
                        "factor_rank": item["factor_solve"]["rank"],
                        "recovered": item["substitution_recovery"]["recovered_count"],
                        "target": item["target"],
                    }
                    for item in summary["summary"]["target_summaries"]
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
