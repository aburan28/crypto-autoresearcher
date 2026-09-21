#!/usr/bin/env python3
"""P752 sparse factor-basis selection for P751 factor-first linear algebra."""

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
P751_SCRIPT = TASK_DIR / "low_term_total2_p751_factor_first_linear_algebra.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P750 = STATE_DIR / "low_term_total2_p750_prospective_prefix_linear_algebra_charge_probe.json"
DEFAULT_P751 = STATE_DIR / "low_term_total2_p751_factor_first_linear_algebra_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p752_sparse_factor_basis_selection_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_order11779_p752_sparse_factor_basis_selection.md"
SCHEMA = "ecdlp.low_term_total2_p752_sparse_factor_basis_selection.v1"


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


def relation_features(relation: dict[str, Any], order: int) -> dict[str, Any]:
    coeffs = [int(value) % order for value in relation["coeffs"]]
    support = [index for index, value in enumerate(coeffs) if value % order]
    weights = [min(coeffs[index], order - coeffs[index]) for index in support]
    return {
        "coefficient_weight": sum(weights),
        "max_support": max(support) if support else -1,
        "min_support": min(support) if support else 10**9,
        "rhs_weight": min(int(relation["rhs"]) % order, order - (int(relation["rhs"]) % order)),
        "source": str(relation.get("source") or ""),
        "span": (max(support) - min(support)) if support else 0,
        "support": support,
        "support_size": len(support),
    }


def annotated_relations(relations: list[dict[str, Any]], order: int) -> list[dict[str, Any]]:
    out = []
    for index, relation in enumerate(relations):
        copied = dict(relation)
        copied["_index"] = index
        copied["_features"] = relation_features(relation, order)
        out.append(copied)
    return out


def order_relations(relations: list[dict[str, Any]], policy: str) -> list[dict[str, Any]]:
    def key(rel: dict[str, Any]) -> tuple[Any, ...]:
        features = rel["_features"]
        base = (
            int(features["support_size"]),
            int(features["span"]),
            int(features["coefficient_weight"]),
            int(features["rhs_weight"]),
            str(rel.get("challenge_id") or ""),
            int(rel["_index"]),
        )
        if policy == "natural":
            return (int(rel["_index"]),)
        if policy == "support_asc":
            return base
        if policy == "support_span_asc":
            return (features["support_size"], features["span"], features["min_support"], features["coefficient_weight"], rel["_index"])
        if policy == "pivot_low":
            return (features["min_support"], features["support_size"], features["span"], features["coefficient_weight"], rel["_index"])
        if policy == "pivot_high":
            return (-int(features["max_support"]), features["support_size"], features["span"], features["coefficient_weight"], rel["_index"])
        if policy == "coefficient_weight_asc":
            return (features["coefficient_weight"], features["support_size"], features["span"], rel["_index"])
        raise ValueError(f"unknown sparse policy {policy!r}")
    return sorted(relations, key=key)


def sparse_ops() -> dict[str, int]:
    return {
        "basis_rows_added": 0,
        "candidate_rows_scanned": 0,
        "field_additions": 0,
        "field_inversions": 0,
        "field_multiplications": 0,
        "max_row_nnz": 0,
        "normalized_nonzeros": 0,
        "row_eliminations": 0,
        "total_field_ops": 0,
    }


def row_from_relation(relation: dict[str, Any], order: int, factor_count: int) -> dict[int, int]:
    row: dict[int, int] = {}
    for index, value in enumerate(relation["coeffs"]):
        value = int(value) % order
        if value:
            row[index] = value
    rhs = int(relation["rhs"]) % order
    if rhs:
        row[factor_count] = rhs
    return row


def sparse_row_eliminate(row: dict[int, int], pivot_row: dict[int, int], factor: int, order: int, ops: dict[str, int]) -> dict[int, int]:
    out = dict(row)
    for col, value in pivot_row.items():
        new_value = (out.get(col, 0) - factor * value) % order
        ops["field_multiplications"] += 1
        ops["field_additions"] += 1
        if new_value:
            out[col] = new_value
        elif col in out:
            del out[col]
    ops["row_eliminations"] += 1
    ops["max_row_nnz"] = max(ops["max_row_nnz"], len(out))
    return out


def sparse_incremental_solve(relations: list[dict[str, Any]], factor_count: int, order: int) -> dict[str, Any]:
    basis: dict[int, dict[int, int]] = {}
    ops = sparse_ops()
    inconsistent_zero_rows = 0
    scanned_to_full_rank = None
    for relation in relations:
        ops["candidate_rows_scanned"] += 1
        row = row_from_relation(relation, order, factor_count)
        ops["max_row_nnz"] = max(ops["max_row_nnz"], len(row))
        for pivot in sorted(basis):
            factor = row.get(pivot, 0)
            if factor:
                row = sparse_row_eliminate(row, basis[pivot], factor, order, ops)
        pivot = next((col for col in sorted(row) if col < factor_count and row[col] % order), None)
        if pivot is None:
            if row.get(factor_count, 0) % order:
                inconsistent_zero_rows += 1
            continue
        inv = pow(row[pivot] % order, -1, order)
        ops["field_inversions"] += 1
        for col in list(row):
            row[col] = (row[col] * inv) % order
            ops["field_multiplications"] += 1
            if row[col] == 0:
                del row[col]
        ops["normalized_nonzeros"] += len(row)
        for existing_pivot, existing in list(basis.items()):
            factor = existing.get(pivot, 0)
            if factor:
                basis[existing_pivot] = sparse_row_eliminate(existing, row, factor, order, ops)
        basis[pivot] = row
        ops["basis_rows_added"] += 1
        if len(basis) == factor_count:
            scanned_to_full_rank = ops["candidate_rows_scanned"]
            break
    ops["total_field_ops"] = ops["field_inversions"] + ops["field_multiplications"] + ops["field_additions"]
    return {
        "basis": basis,
        "factor_values": {pivot: row.get(factor_count, 0) % order for pivot, row in basis.items()},
        "full_rank": len(basis) == factor_count,
        "inconsistent_zero_rows": inconsistent_zero_rows,
        "operation_counts": ops,
        "rank": len(basis),
        "scanned_to_full_rank": scanned_to_full_rank,
    }


def target_cost_summary(
    rows: list[dict[str, Any]],
    baseline: dict[str, Any],
    solve: dict[str, Any],
    substitution: dict[str, Any],
) -> dict[str, Any]:
    rho = int(rows[0]["generic_rho_steps"]) if rows else 0
    setup = int(rows[0]["cost_model"]["subset_group_additions"]) if rows else 0
    group_total = setup + sum(int(row["cost_model"]["collection_online_group_additions"]) for row in rows)
    recovered = int(substitution["recovered_count"])
    baseline_rho = recovered * rho
    solve_ops = int(solve["operation_counts"]["total_field_ops"])
    substitution_ops = int(substitution["operation_counts"]["total_field_ops"])
    total_field_ops = solve_ops + substitution_ops
    p751_field_ops = int((baseline.get("cost_summary") or {}).get("factor_first_field_ops") or 0)
    return {
        "group_addition_cost": group_total,
        "group_addition_cost_over_recovered_rho": ratio(group_total, baseline_rho),
        "p751_factor_first_field_ops": p751_field_ops,
        "recovered_rho_baseline": baseline_rho,
        "rho": rho,
        "sparse_factor_first_field_ops": total_field_ops,
        "sparse_factor_first_field_ops_over_p751": ratio(total_field_ops, p751_field_ops),
        "sparse_solve_field_ops": solve_ops,
        "substitution_field_ops": substitution_ops,
        "total_unit_cost_group_additions_plus_field_ops": group_total + total_field_ops,
        "total_unit_cost_over_recovered_rho": ratio(group_total + total_field_ops, baseline_rho),
    }


def evaluate_policy(
    p751: Any,
    policy: str,
    relations: list[dict[str, Any]],
    rows: list[dict[str, Any]],
    baseline: dict[str, Any],
    factor_count: int,
    order: int,
) -> dict[str, Any]:
    ordered = order_relations(relations, policy)
    solve = sparse_incremental_solve(ordered, factor_count, order)
    substitution = p751.substitution_recovery(rows, solve["factor_values"], order) if solve["full_rank"] else {
        "mismatch_count": len(rows),
        "operation_counts": {"total_field_ops": 0},
        "recovered_count": 0,
        "recovered_sample": [],
    }
    return {
        "cost_summary": target_cost_summary(rows, baseline, solve, substitution),
        "policy": policy,
        "solve": {
            "full_rank": solve["full_rank"],
            "operation_counts": solve["operation_counts"],
            "rank": solve["rank"],
            "scanned_to_full_rank": solve["scanned_to_full_rank"],
        },
        "substitution": substitution,
    }


def determine_claim(target_summaries: list[dict[str, Any]]) -> str:
    all_recovered = all(summary["best_policy"]["substitution"]["mismatch_count"] == 0 for summary in target_summaries)
    all_reduced = all((summary["best_policy"]["cost_summary"].get("sparse_factor_first_field_ops_over_p751") or 10**18) <= 0.2 for summary in target_summaries)
    all_unit = all((summary["best_policy"]["cost_summary"].get("total_unit_cost_over_recovered_rho") or 10**18) < 1.0 for summary in target_summaries)
    any_unit = any((summary["best_policy"]["cost_summary"].get("total_unit_cost_over_recovered_rho") or 10**18) < 1.0 for summary in target_summaries)
    if all_recovered and all_unit:
        return "P752_SPARSE_FACTOR_BASIS_UNIT_COST_BELOW_RHO_SIGNAL"
    if all_recovered and any_unit:
        return "P752_SPARSE_FACTOR_BASIS_PARTIAL_UNIT_COST_BELOW_RHO_SIGNAL"
    if all_recovered and all_reduced:
        return "P752_SPARSE_FACTOR_BASIS_REDUCES_LA_UNIT_COST_ABOVE_RHO"
    if all_recovered:
        return "P752_SPARSE_FACTOR_BASIS_RECOVERS_ALL_REDUCTION_WEAK"
    return "NEGATIVE_RESULT_P752_SPARSE_FACTOR_BASIS_FAILED"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p746 = load_module("ecdlp_p746_incremental_walk", P746_SCRIPT)
    p748 = load_module("ecdlp_p748_matrix_bridge", P748_SCRIPT)
    p751 = load_module("ecdlp_p751_factor_first", P751_SCRIPT)
    relprobe = p746.load_relation_probe_module()
    p750 = load_json(args.p750_probe)
    p751_summary = load_json(args.p751_summary)
    rows_by_target = p751.add_expected_secrets(p746, relprobe, p750["results"])
    baseline_by_target = {
        item["target"]: item
        for item in ((p751_summary.get("summary") or {}).get("target_summaries") or [])
    }
    policies = [item.strip() for item in args.policies.split(",") if item.strip()]
    target_summaries = []
    for target, rows in rows_by_target.items():
        _verifier, _record, inv = p746.load_target(relprobe, target)
        order = int(inv["base_order"])
        factor_count = max((len(form["coeffs"]) - 1 for row in rows for form in row.get("forms") or []), default=0)
        relations = annotated_relations(p748.factor_eliminated_relations(rows, order, factor_count), order)
        evaluations = [
            evaluate_policy(p751, policy, relations, rows, baseline_by_target.get(target, {}), factor_count, order)
            for policy in policies
        ]
        successful = [item for item in evaluations if item["substitution"]["mismatch_count"] == 0]
        best = min(
            successful or evaluations,
            key=lambda item: (
                item["cost_summary"].get("total_unit_cost_over_recovered_rho") or 10**18,
                item["cost_summary"].get("sparse_factor_first_field_ops") or 10**18,
                item["policy"],
            ),
        )
        target_summaries.append(
            {
                "best_policy": best,
                "factor_relation_count": len(relations),
                "factor_variable_count": factor_count,
                "policy_evaluations": evaluations,
                "target": target,
            }
        )
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p750_probe": str(args.p750_probe),
            "p751_summary": str(args.p751_summary),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(target_summaries),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "PUBLIC-SPARSE-FEATURES: static policies use only factor-equation support and coefficient features.",
            "SPARSE-COUNT MODEL: field ops count only nonzero row updates, not dense cells.",
            "MANY-TARGET MODEL: factor variables are solved from a batch sharing one target factor base.",
            "NO DEPLOYED-CURVE CLAIM: no large-prime scaling or production-key relevance is implied.",
        ],
        "method": "p752_sparse_factor_basis_selection",
        "parameters": {
            "p750_probe": str(args.p750_probe),
            "p751_summary": str(args.p751_summary),
            "policies": policies,
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
    parser.add_argument("--p751-summary", type=Path, default=DEFAULT_P751)
    parser.add_argument("--policies", default="natural,support_asc,support_span_asc,pivot_low,pivot_high,coefficient_weight_asc")
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
                        "best_policy": item["best_policy"]["policy"],
                        "cost": item["best_policy"]["cost_summary"],
                        "factor_relation_count": item["factor_relation_count"],
                        "rank": item["best_policy"]["solve"]["rank"],
                        "recovered": item["best_policy"]["substitution"]["recovered_count"],
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
