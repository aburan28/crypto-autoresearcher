#!/usr/bin/env python3
"""P755 public row-quality selector for the P754 67.a1@11789 boundary."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P746_SCRIPT = TASK_DIR / "low_term_total2_p746_incremental_walk_online_cost.py"
P748_SCRIPT = TASK_DIR / "low_term_total2_p748_setup_amortization_matrix_bridge.py"
P750_SCRIPT = TASK_DIR / "low_term_total2_p750_prospective_prefix_linear_algebra_charge.py"
P751_SCRIPT = TASK_DIR / "low_term_total2_p751_factor_first_linear_algebra.py"
P752_SCRIPT = TASK_DIR / "low_term_total2_p752_sparse_factor_basis_selection.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_OUT = STATE_DIR / "low_term_total2_p755_public_row_quality_selector_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_order11779_p755_public_row_quality_selector.md"
SCHEMA = "ecdlp.low_term_total2_p755_public_row_quality_selector.v1"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


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


def csv_ints(text: str) -> list[int]:
    return [int(item.strip()) for item in text.split(",") if item.strip()]


def csv_strings(text: str) -> list[str]:
    return [item.strip() for item in text.split(",") if item.strip()]


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(float(numerator) / float(denominator), 8)


def row_index(row: dict[str, Any]) -> int:
    label = str(row.get("seed_label") or row.get("seed") or "")
    match = re.search(r"(\d+)$", label)
    return int(match.group(1)) if match else 10**9


def sorted_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(rows, key=lambda row: (row_index(row), str(row.get("seed_label") or "")))


def form_count(row: dict[str, Any]) -> int:
    return len(row.get("forms") or [])


def public_feature(row: dict[str, Any]) -> dict[str, Any]:
    forms = row.get("forms") or []
    trials = [int(form.get("trial") or 0) for form in forms]
    return {
        "accepted_mixed_relations": int(row.get("accepted_mixed_relations") or form_count(row)),
        "decomposition_hits": int(row.get("decomposition_hits") or 0),
        "derived": bool(row.get("derived")),
        "first_form_trial": min(trials) if trials else None,
        "form_count": form_count(row),
        "last_form_trial": max(trials) if trials else None,
        "mixed_wide_relation_rank": int(row.get("mixed_wide_relation_rank") or 0),
        "observed_decomposition_rate": float(row.get("observed_decomposition_rate") or 0.0),
        "seed_index": row_index(row),
        "seed_label": row.get("seed_label"),
        "zero_b_skips": int(row.get("zero_b_skips") or 0),
    }


def select_rows(rows: list[dict[str, Any]], selected_count: int, pool_count: int, policy: str) -> dict[str, Any]:
    ordered = sorted_rows(rows)
    pool = ordered[: min(pool_count, len(ordered))]
    if policy == "prefix":
        selected = pool[: min(selected_count, len(pool))]
        scanned = selected
    elif policy.startswith("sequential_min_forms_ge_"):
        threshold = int(policy.rsplit("_", 1)[-1])
        selected = []
        last_index = -1
        for index, row in enumerate(pool):
            if form_count(row) >= threshold:
                selected.append(row)
                last_index = index
                if len(selected) == selected_count:
                    break
        scanned = pool[: last_index + 1] if last_index >= 0 else pool
    elif policy == "top_forms_rank":
        scanned = pool
        selected = sorted(
            pool,
            key=lambda row: (
                -form_count(row),
                -int(row.get("mixed_wide_relation_rank") or 0),
                -int(row.get("decomposition_hits") or 0),
                row_index(row),
            ),
        )[: min(selected_count, len(pool))]
        selected = sorted_rows(selected)
    elif policy == "top_rank_forms":
        scanned = pool
        selected = sorted(
            pool,
            key=lambda row: (
                -int(row.get("mixed_wide_relation_rank") or 0),
                -form_count(row),
                -int(row.get("decomposition_hits") or 0),
                row_index(row),
            ),
        )[: min(selected_count, len(pool))]
        selected = sorted_rows(selected)
    else:
        raise ValueError(f"unknown row selection policy {policy!r}")
    selected_ids = {row.get("seed_label") for row in selected}
    scanned_ids = {row.get("seed_label") for row in scanned}
    return {
        "dropped_from_scanned": [row.get("seed_label") for row in scanned if row.get("seed_label") not in selected_ids],
        "policy": policy,
        "pool_count": len(pool),
        "scanned_rows": scanned,
        "scanned_seed_max": max((row_index(row) for row in scanned), default=None),
        "selected_rows": selected,
        "selected_seed_labels": [row.get("seed_label") for row in selected],
        "unscanned_selected_gap": sorted(selected_ids - scanned_ids),
    }


def operation_costs(
    selected_rows: list[dict[str, Any]],
    scanned_rows: list[dict[str, Any]],
    solve: dict[str, Any],
    substitution: dict[str, Any],
    field_weight: int,
) -> dict[str, Any]:
    rho = int(selected_rows[0]["generic_rho_steps"]) if selected_rows else 0
    setup = int(selected_rows[0]["cost_model"]["subset_group_additions"]) if selected_rows else 0
    group_total = setup + sum(int(row["cost_model"]["collection_online_group_additions"]) for row in scanned_rows)
    selected_count = len(selected_rows)
    recovered = int(substitution["recovered_count"])
    solve_ops = int(solve["operation_counts"]["total_field_ops"])
    substitution_ops = int(substitution["operation_counts"].get("total_field_ops", 0))
    field_ops = solve_ops + substitution_ops
    selected_rho = selected_count * rho
    recovered_rho = recovered * rho
    weighted_field_ops = field_weight * field_ops
    total = group_total + weighted_field_ops
    return {
        "candidate_scan_group_addition_cost": group_total,
        "field_op_weight": field_weight,
        "group_addition_cost_over_selected_rho": ratio(group_total, selected_rho),
        "recovered_rho_baseline": recovered_rho,
        "rho": rho,
        "scanned_challenge_count": len(scanned_rows),
        "selected_challenge_count": selected_count,
        "selected_rho_baseline": selected_rho,
        "sparse_factor_first_field_ops": field_ops,
        "sparse_solve_field_ops": solve_ops,
        "substitution_field_ops": substitution_ops,
        "total_unit_cost_group_additions_plus_weighted_field_ops": total,
        "total_unit_cost_over_recovered_rho": ratio(total, recovered_rho),
        "total_unit_cost_over_selected_rho": ratio(total, selected_rho),
        "weighted_sparse_field_ops": weighted_field_ops,
    }


def safe_weight_threshold(
    selected_rows: list[dict[str, Any]],
    scanned_rows: list[dict[str, Any]],
    solve: dict[str, Any],
    substitution: dict[str, Any],
) -> float | None:
    rho = int(selected_rows[0]["generic_rho_steps"]) if selected_rows else 0
    setup = int(selected_rows[0]["cost_model"]["subset_group_additions"]) if selected_rows else 0
    group_total = setup + sum(int(row["cost_model"]["collection_online_group_additions"]) for row in scanned_rows)
    field_ops = int(solve["operation_counts"]["total_field_ops"]) + int(substitution["operation_counts"].get("total_field_ops", 0))
    if field_ops <= 0:
        return None
    return round((len(selected_rows) * rho - group_total) / field_ops, 8)


def evaluate_sparse_policy(
    p748: Any,
    p751: Any,
    p752: Any,
    selected_rows: list[dict[str, Any]],
    scanned_rows: list[dict[str, Any]],
    sparse_policy: str,
    field_weights: list[int],
    order: int,
) -> dict[str, Any]:
    factor_count = max((len(form["coeffs"]) - 1 for row in selected_rows for form in row.get("forms") or []), default=0)
    relations = p752.annotated_relations(p748.factor_eliminated_relations(selected_rows, order, factor_count), order)
    solve = p752.sparse_incremental_solve(p752.order_relations(relations, sparse_policy), factor_count, order)
    substitution = p751.substitution_recovery(selected_rows, solve["factor_values"], order) if solve["full_rank"] else {
        "mismatch_count": len(selected_rows),
        "operation_counts": {"total_field_ops": 0},
        "recovered_count": 0,
        "recovered_sample": [],
    }
    success = bool(solve["full_rank"] and substitution["mismatch_count"] == 0 and substitution["recovered_count"] == len(selected_rows))
    return {
        "costs_by_field_weight": [
            operation_costs(selected_rows, scanned_rows, solve, substitution, weight)
            for weight in field_weights
        ],
        "factor_relation_count": len(relations),
        "factor_variable_count": factor_count,
        "max_field_op_weight_below_selected_rho": safe_weight_threshold(selected_rows, scanned_rows, solve, substitution) if success else None,
        "sparse_policy": sparse_policy,
        "solve": {
            "full_rank": solve["full_rank"],
            "operation_counts": solve["operation_counts"],
            "rank": solve["rank"],
            "scanned_to_full_rank": solve["scanned_to_full_rank"],
        },
        "substitution": {
            "mismatch_count": substitution["mismatch_count"],
            "operation_counts": substitution["operation_counts"],
            "recovered_count": substitution["recovered_count"],
        },
        "success": success,
    }


def best_for_weight(evaluations: list[dict[str, Any]], weight: int) -> dict[str, Any]:
    def key(item: dict[str, Any]) -> tuple[Any, ...]:
        cost = next(cost for cost in item["costs_by_field_weight"] if cost["field_op_weight"] == weight)
        return (
            0 if item["success"] else 1,
            cost.get("total_unit_cost_over_selected_rho") or 10**18,
            item["substitution"]["mismatch_count"],
            item["sparse_policy"],
        )

    best = min(evaluations, key=key)
    return {
        "cost": next(cost for cost in best["costs_by_field_weight"] if cost["field_op_weight"] == weight),
        "factor_relation_count": best["factor_relation_count"],
        "policy": best["sparse_policy"],
        "rank": best["solve"]["rank"],
        "recovered_count": best["substitution"]["recovered_count"],
        "success": best["success"],
    }


def evaluate_selection(
    p748: Any,
    p751: Any,
    p752: Any,
    rows: list[dict[str, Any]],
    selected_count: int,
    pool_count: int,
    row_policy: str,
    sparse_policies: list[str],
    field_weights: list[int],
    order: int,
) -> dict[str, Any]:
    selection = select_rows(rows, selected_count, pool_count, row_policy)
    selected_rows = selection["selected_rows"]
    scanned_rows = selection["scanned_rows"]
    evaluations = [
        evaluate_sparse_policy(p748, p751, p752, selected_rows, scanned_rows, sparse_policy, field_weights, order)
        for sparse_policy in sparse_policies
        if selected_rows
    ]
    best_by_weight = {str(weight): best_for_weight(evaluations, weight) for weight in field_weights} if evaluations else {}
    successful = [item for item in evaluations if item["success"]]
    max_weight = max(
        (item["max_field_op_weight_below_selected_rho"] for item in successful if item["max_field_op_weight_below_selected_rho"] is not None),
        default=None,
    )
    weight2 = best_by_weight.get("2")
    return {
        "best_by_field_weight": best_by_weight,
        "dropped_from_scanned": selection["dropped_from_scanned"][:24],
        "max_field_op_weight_below_selected_rho": max_weight,
        "pool_count": selection["pool_count"],
        "row_policy": row_policy,
        "scanned_count": len(scanned_rows),
        "scanned_seed_max": selection["scanned_seed_max"],
        "selected_count": len(selected_rows),
        "selected_seed_sample": selection["selected_seed_labels"][:12],
        "success_weight2_below_rho": bool(
            weight2
            and weight2["success"]
            and (weight2["cost"].get("total_unit_cost_over_selected_rho") or 10**18) < 1.0
        ),
    }


def mismatch_diagnostic(
    p748: Any,
    p751: Any,
    p752: Any,
    rows: list[dict[str, Any]],
    prefix: int,
    sparse_policy: str,
    order: int,
) -> dict[str, Any]:
    selected = sorted_rows(rows)[:prefix]
    factor_count = max((len(form["coeffs"]) - 1 for row in selected for form in row.get("forms") or []), default=0)
    relations = p752.annotated_relations(p748.factor_eliminated_relations(selected, order, factor_count), order)
    solve = p752.sparse_incremental_solve(p752.order_relations(relations, sparse_policy), factor_count, order)
    mismatches = []
    for row in selected:
        recovered = None
        for form in row.get("forms") or []:
            coeffs = [int(value) % order for value in form["coeffs"]]
            b = coeffs[0] % order
            if not b:
                continue
            acc = int(form["rhs"]) % order
            for factor_index, factor_value in solve["factor_values"].items():
                coeff = coeffs[1 + factor_index] % order
                if coeff:
                    acc = (acc - coeff * factor_value) % order
            recovered = (acc * pow(b, -1, order)) % order
            break
        if recovered != int(row["_expected_secret"]):
            feature = public_feature(row)
            feature.update({"expected_secret": int(row["_expected_secret"]), "recovered_secret": recovered})
            mismatches.append(feature)
    return {
        "boundary": "PRIVATE-DIAGNOSTIC: expected secrets identify the bad row; selector policies below do not use expected secrets.",
        "mismatch_count": len(mismatches),
        "mismatches": mismatches,
        "prefix": prefix,
        "sparse_policy": sparse_policy,
    }


def determine_claim(evaluations: list[dict[str, Any]]) -> str:
    any_win = any(item["success_weight2_below_rho"] for item in evaluations)
    any_full_improved = any(
        item["max_field_op_weight_below_selected_rho"] is not None and item["max_field_op_weight_below_selected_rho"] > 1.71614477
        for item in evaluations
    )
    if any_win:
        return "P755_PUBLIC_ROW_SELECTOR_WEIGHT2_BELOW_RHO_SIGNAL"
    if any_full_improved:
        return "P755_PUBLIC_ROW_SELECTOR_IMPROVES_HEADROOM_WEIGHT2_NEGATIVE"
    return "NEGATIVE_RESULT_P755_PUBLIC_ROW_SELECTOR_NO_WEIGHT2_WIN"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p746 = load_module("ecdlp_p746_incremental_walk", P746_SCRIPT)
    p748 = load_module("ecdlp_p748_matrix_bridge", P748_SCRIPT)
    p750 = load_module("ecdlp_p750_prospective_prefix", P750_SCRIPT)
    p751 = load_module("ecdlp_p751_factor_first", P751_SCRIPT)
    p752 = load_module("ecdlp_p752_sparse_factor_basis", P752_SCRIPT)
    relprobe = p746.load_relation_probe_module()
    rows, order = p750.collect_target_rows(
        p746,
        p748,
        relprobe,
        args.target,
        args.budget,
        args.seed_count,
        args.factor_base_size,
        args.width,
        args.walk_mode,
        args.seed_prefix,
        args.max_relations,
        args.max_subsets,
    )
    row_policies = csv_strings(args.row_policies)
    sparse_policies = csv_strings(args.sparse_policies)
    field_weights = csv_ints(args.field_weights)
    selected_counts = csv_ints(args.selected_counts)
    pool_counts = csv_ints(args.pool_counts)
    evaluations = []
    for selected_count in selected_counts:
        for pool_count in pool_counts:
            if pool_count < selected_count:
                continue
            for row_policy in row_policies:
                if row_policy == "prefix" and pool_count != selected_count:
                    continue
                evaluations.append(
                    evaluate_selection(
                        p748,
                        p751,
                        p752,
                        rows,
                        selected_count,
                        pool_count,
                        row_policy,
                        sparse_policies,
                        field_weights,
                        order,
                    )
                )
    best_weight2 = min(
        evaluations,
        key=lambda item: (
            0 if item["best_by_field_weight"].get("2", {}).get("success") else 1,
            item["best_by_field_weight"].get("2", {}).get("cost", {}).get("total_unit_cost_over_selected_rho") or 10**18,
            item["row_policy"],
            item["selected_count"],
        ),
    )
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(evaluations),
        "created_at": now_iso(),
        "diagnostics": {
            "mismatch_prefix_448_support_asc": mismatch_diagnostic(p748, p751, p752, rows, 448, "support_asc", order),
        },
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled order-11779 ECDLP harness only.",
            "PRIVATE-DIAGNOSTIC-SEPARATED: mismatch localization uses expected secrets, but selector policies use only public row features.",
            "SCANNED-POOL-CHARGED: replacement policies pay group cost for all scanned candidate rows.",
            "SPARSE-WEIGHT MODEL: field-operation weights are accounting stress tests, not calibrated hardware timings.",
            "NO DEPLOYED-CURVE CLAIM: no large-prime scaling or production-key relevance is implied.",
        ],
        "method": "p755_public_row_quality_selector",
        "parameters": {
            "budget": args.budget,
            "factor_base_size": args.factor_base_size,
            "field_weights": field_weights,
            "max_relations": args.max_relations,
            "max_subsets": args.max_subsets,
            "pool_counts": pool_counts,
            "row_policies": row_policies,
            "seed_count": args.seed_count,
            "selected_counts": selected_counts,
            "sparse_policies": sparse_policies,
            "target": args.target,
            "walk_mode": args.walk_mode,
            "width": args.width,
        },
        "results": {
            args.target: [p750.strip_private(row) for row in rows],
        },
        "schema": SCHEMA,
        "summary": {
            "best_weight2": best_weight2,
            "evaluation_count": len(evaluations),
            "selector_evaluations": evaluations,
            "target": args.target,
        },
    }


def slim_evaluation(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "best_by_field_weight": item["best_by_field_weight"],
        "dropped_from_scanned": item["dropped_from_scanned"],
        "max_field_op_weight_below_selected_rho": item["max_field_op_weight_below_selected_rho"],
        "pool_count": item["pool_count"],
        "row_policy": item["row_policy"],
        "scanned_count": item["scanned_count"],
        "scanned_seed_max": item["scanned_seed_max"],
        "selected_count": item["selected_count"],
        "success_weight2_below_rho": item["success_weight2_below_rho"],
    }


def summary_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    evaluations = payload["summary"]["selector_evaluations"]
    top = sorted(
        evaluations,
        key=lambda item: (
            0 if item["best_by_field_weight"].get("2", {}).get("success") else 1,
            item["best_by_field_weight"].get("2", {}).get("cost", {}).get("total_unit_cost_over_selected_rho") or 10**18,
            item["row_policy"],
            item["selected_count"],
        ),
    )[:20]
    return {
        "schema": f"{SCHEMA}.summary",
        "created_at": payload["created_at"],
        "claim_status": payload["claim_status"],
        "diagnostics": payload["diagnostics"],
        "honesty_boundary": payload["honesty_boundary"],
        "method": payload["method"],
        "parameters": payload["parameters"],
        "summary": {
            "best_weight2": slim_evaluation(payload["summary"]["best_weight2"]),
            "evaluation_count": payload["summary"]["evaluation_count"],
            "target": payload["summary"]["target"],
            "top_selector_evaluations": [slim_evaluation(item) for item in top],
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", default="67.a1@11789")
    parser.add_argument("--budget", type=int, default=80)
    parser.add_argument("--seed-count", type=int, default=640)
    parser.add_argument("--seed-prefix", default="ecdlp-p746-scheduled-seed-extension-v1")
    parser.add_argument("--factor-base-size", type=int, default=48)
    parser.add_argument("--width", type=int, default=2)
    parser.add_argument("--walk-mode", default="hash6")
    parser.add_argument("--max-relations", type=int, default=96)
    parser.add_argument("--max-subsets", type=int, default=25000)
    parser.add_argument("--selected-counts", default="416,448,512")
    parser.add_argument("--pool-counts", default="416,448,512,576,640")
    parser.add_argument("--row-policies", default="prefix,sequential_min_forms_ge_1,sequential_min_forms_ge_2,sequential_min_forms_ge_3,sequential_min_forms_ge_4,top_forms_rank,top_rank_forms")
    parser.add_argument("--sparse-policies", default="support_asc,support_span_asc,coefficient_weight_asc,natural")
    parser.add_argument("--field-weights", default="1,2")
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
                "best_weight2": {
                    "row_policy": summary["summary"]["best_weight2"]["row_policy"],
                    "selected_count": summary["summary"]["best_weight2"]["selected_count"],
                    "scanned_count": summary["summary"]["best_weight2"]["scanned_count"],
                    "weight2": summary["summary"]["best_weight2"]["best_by_field_weight"]["2"]["cost"],
                    "weight2_success": summary["summary"]["best_weight2"]["success_weight2_below_rho"],
                },
                "claim_status": summary["claim_status"],
                "diagnostic_mismatches": summary["diagnostics"]["mismatch_prefix_448_support_asc"]["mismatches"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
