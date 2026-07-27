#!/usr/bin/env python3
"""P750 prospective prefix collection with counted modular linear algebra.

P749 replayed P748 forms by prefix and found below-rho many-target
group-addition costs before linear algebra. This probe prospectively enforces
those budgets during collection and counts modular RREF operations.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P746_SCRIPT = TASK_DIR / "low_term_total2_p746_incremental_walk_online_cost.py"
P748_SCRIPT = TASK_DIR / "low_term_total2_p748_setup_amortization_matrix_bridge.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P749_SUMMARY = STATE_DIR / "low_term_total2_p749_prefix_budget_matrix_crossover_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p750_prospective_prefix_linear_algebra_charge_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_order11779_p750_prospective_prefix_linear_algebra_charge.md"
SCHEMA = "ecdlp.low_term_total2_p750_prospective_prefix_linear_algebra_charge.v1"


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


def seed_labels(count: int) -> list[str]:
    return [f"t{index:02d}" for index in range(count)]


def parse_target_budgets(raw: str) -> dict[str, int]:
    out: dict[str, int] = {}
    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue
        target, sep, budget = item.partition("=")
        if not sep:
            raise argparse.ArgumentTypeError(f"target budget must be target=budget, got {item!r}")
        out[target.strip()] = int(budget)
    return out


def target_budgets_from_p749(path: Path) -> dict[str, int]:
    payload = load_json(path)
    out: dict[str, int] = {}
    for summary in ((payload.get("summary") or {}).get("target_summaries") or []):
        budget_row = summary.get("earliest_full_recovery_budget") or {}
        target = summary.get("target")
        if target and budget_row.get("budget") is not None:
            out[str(target)] = int(budget_row["budget"])
    return out


def build_augmented_rows(rows: list[dict[str, Any]], order: int) -> tuple[list[list[int]], list[str], dict[str, int], int]:
    challenge_ids = sorted({row["matrix_challenge_id"] for row in rows})
    challenge_index = {challenge_id: index for index, challenge_id in enumerate(challenge_ids)}
    factor_count = max((len(form["coeffs"]) - 1 for row in rows for form in row.get("forms") or []), default=0)
    nvars = len(challenge_ids) + factor_count
    augmented: list[list[int]] = []
    for row in rows:
        challenge_col = challenge_index[row["matrix_challenge_id"]]
        for form in row.get("forms") or []:
            coeffs = [int(value) % order for value in form["coeffs"]]
            matrix_row = [0] * nvars
            matrix_row[challenge_col] = coeffs[0]
            for factor_index in range(factor_count):
                matrix_row[len(challenge_ids) + factor_index] = coeffs[1 + factor_index]
            augmented.append(matrix_row + [int(form["rhs"]) % order])
    return augmented, challenge_ids, challenge_index, factor_count


def counted_rref_augmented(rows: list[list[int]], modulus: int) -> dict[str, Any]:
    if not rows:
        return {
            "consistent": True,
            "operation_counts": empty_ops(0, 0),
            "pivot_cols": [],
            "rank": 0,
            "reduced": [],
        }
    reduced = [[value % modulus for value in row] for row in rows]
    nvars = len(reduced[0]) - 1
    row_count = len(reduced)
    width = nvars + 1
    pivot_cols: list[int] = []
    pivot_row = 0
    ops = empty_ops(row_count, width)
    for col in range(nvars):
        pivot = None
        for row in range(pivot_row, row_count):
            ops["pivot_tests"] += 1
            if reduced[row][col] % modulus:
                pivot = row
                break
        if pivot is None:
            continue
        reduced[pivot_row], reduced[pivot] = reduced[pivot], reduced[pivot_row]
        inv = pow(reduced[pivot_row][col] % modulus, -1, modulus)
        ops["field_inversions"] += 1
        reduced[pivot_row] = [(value * inv) % modulus for value in reduced[pivot_row]]
        ops["field_multiplications"] += width
        ops["normalized_cells"] += width

        for row in range(row_count):
            if row == pivot_row:
                continue
            factor = reduced[row][col] % modulus
            if not factor:
                continue
            reduced[row] = [
                (reduced[row][idx] - factor * reduced[pivot_row][idx]) % modulus
                for idx in range(width)
            ]
            ops["field_multiplications"] += width
            ops["field_additions"] += width
            ops["eliminated_cells"] += width
            ops["row_eliminations"] += 1

        pivot_cols.append(col)
        pivot_row += 1
        if pivot_row == row_count:
            break

    consistent = True
    for row in reduced:
        if all(row[col] % modulus == 0 for col in range(nvars)) and row[-1] % modulus:
            consistent = False
            break
    ops["total_field_ops"] = ops["field_inversions"] + ops["field_multiplications"] + ops["field_additions"]
    return {
        "consistent": consistent,
        "operation_counts": ops,
        "pivot_cols": pivot_cols,
        "rank": len(pivot_cols),
        "reduced": reduced,
    }


def empty_ops(row_count: int, width: int) -> dict[str, int]:
    return {
        "eliminated_cells": 0,
        "field_additions": 0,
        "field_inversions": 0,
        "field_multiplications": 0,
        "matrix_row_count": row_count,
        "matrix_width": width,
        "normalized_cells": 0,
        "pivot_tests": 0,
        "row_eliminations": 0,
        "total_field_ops": 0,
    }


def solved_variables(reduced: list[list[int]], pivot_cols: list[int], nvars: int, modulus: int) -> dict[int, int]:
    free_cols = set(range(nvars)) - set(pivot_cols)
    solved: dict[int, int] = {}
    for row_index, col in enumerate(pivot_cols):
        if all(reduced[row_index][free_col] % modulus == 0 for free_col in free_cols):
            solved[col] = reduced[row_index][-1] % modulus
    return solved


def counted_matrix_summary(p748: Any, rows: list[dict[str, Any]], order: int) -> dict[str, Any]:
    base = p748.matrix_summary(rows, order)
    augmented, challenge_ids, challenge_index, factor_count = build_augmented_rows(rows, order)
    rref = counted_rref_augmented(augmented, order)
    nvars = len(challenge_ids) + factor_count
    expected = {row["matrix_challenge_id"]: int(row["_expected_secret"]) for row in rows}
    solved = solved_variables(rref["reduced"], rref["pivot_cols"], nvars, order) if rref["consistent"] else {}
    matched = 0
    for challenge_id, col in challenge_index.items():
        if col in solved and solved[col] == expected[challenge_id]:
            matched += 1
    base["counted_rref"] = {
        "consistent": rref["consistent"],
        "operation_counts": rref["operation_counts"],
        "rank": rref["rank"],
        "secret_match_count_from_counted_rref": matched,
    }
    return base


def collect_target_rows(
    p746: Any,
    p748: Any,
    relprobe: Any,
    target: str,
    budget: int,
    seed_count: int,
    factor_base_size: int,
    width: int,
    mode: str,
    seed_prefix: str,
    max_relations: int,
    max_subsets: int,
) -> tuple[list[dict[str, Any]], int]:
    verifier, record, inv = p746.load_target(relprobe, target)
    rows = []
    for seed_label in seed_labels(seed_count):
        full_seed = f"{seed_prefix}:{seed_label}:fb{factor_base_size}:w{width}:{mode}"
        rows.append(
            p748.scan_export_walk(
                p746,
                relprobe,
                verifier,
                record,
                inv,
                target,
                factor_base_size,
                width,
                mode,
                seed_label,
                full_seed,
                budget,
                min(24, budget),
                max_relations,
                max_subsets,
            )
        )
    return rows, int(inv["base_order"])


def strip_private(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: strip_private(inner) for key, inner in value.items() if not str(key).startswith("_")}
    if isinstance(value, list):
        return [strip_private(item) for item in value]
    return value


def cost_report(rows: list[dict[str, Any]], matrix: dict[str, Any], order: int, budget: int) -> dict[str, Any]:
    if not rows:
        return {}
    rho = int(rows[0]["generic_rho_steps"])
    setup = int(rows[0]["cost_model"]["subset_group_additions"])
    online_total = sum(int(row["cost_model"]["collection_online_group_additions"]) for row in rows)
    group_total = setup + online_total
    solved = int(matrix.get("secret_match_count") or 0)
    baseline = solved * rho
    field_ops = int(((matrix.get("counted_rref") or {}).get("operation_counts") or {}).get("total_field_ops") or 0)
    return {
        "budget": budget,
        "group_addition_cost": group_total,
        "group_addition_cost_over_matrix_solved_rho": ratio(group_total, baseline),
        "linear_algebra_field_ops": field_ops,
        "linear_algebra_field_ops_over_matrix_solved_rho_unit_model": ratio(field_ops, baseline),
        "matrix_solved_rho_baseline": baseline,
        "rho": rho,
        "setup_group_additions": setup,
        "total_unit_cost_group_additions_plus_field_ops": group_total + field_ops,
        "total_unit_cost_over_matrix_solved_rho": ratio(group_total + field_ops, baseline),
    }


def sweep_reports(
    p748: Any,
    rows: list[dict[str, Any]],
    order: int,
    budget: int,
    challenge_counts: list[int],
) -> list[dict[str, Any]]:
    out = []
    for count in challenge_counts:
        subset = rows[: min(count, len(rows))]
        matrix = counted_matrix_summary(p748, subset, order)
        costs = cost_report(subset, matrix, order, budget)
        out.append(
            {
                "challenge_count": len(subset),
                "cost_summary": costs,
                "matrix_summary": {
                    "counted_rref": matrix["counted_rref"],
                    "factor_relation_rank": matrix.get("factor_relation_rank"),
                    "form_count": matrix.get("form_count"),
                    "raw_coefficient_rank": matrix.get("raw_coefficient_rank"),
                    "secret_match_count": matrix.get("secret_match_count"),
                    "secret_solved_count": matrix.get("secret_solved_count"),
                    "variable_count": matrix.get("variable_count"),
                },
            }
        )
    return out


def summarize_target(
    p748: Any,
    target: str,
    rows: list[dict[str, Any]],
    order: int,
    budget: int,
    challenge_counts: list[int],
) -> dict[str, Any]:
    matrix = counted_matrix_summary(p748, rows, order)
    costs = cost_report(rows, matrix, order, budget)
    sweep = sweep_reports(p748, rows, order, budget, challenge_counts)
    return {
        "budget": budget,
        "challenge_count": len(rows),
        "cost_summary": costs,
        "matrix_summary": matrix,
        "prospective_reproduction": {
            "factor_rank_full": int(matrix.get("factor_relation_rank") or 0) >= int(matrix.get("factor_count") or 0),
            "full_secret_recovery": int(matrix.get("secret_match_count") or 0) == len(rows),
            "group_addition_below_rho": (costs.get("group_addition_cost_over_matrix_solved_rho") or 10**18) < 1.0,
            "unit_cost_below_rho": (costs.get("total_unit_cost_over_matrix_solved_rho") or 10**18) < 1.0,
        },
        "relation_stats": {
            "accepted_forms": sum(len(row.get("forms") or []) for row in rows),
            "accepted_forms_per_challenge": stat([len(row.get("forms") or []) for row in rows]),
        },
        "sweep": sweep,
        "target": target,
    }


def determine_claim(target_summaries: list[dict[str, Any]]) -> str:
    all_full = all(summary["prospective_reproduction"]["full_secret_recovery"] for summary in target_summaries)
    all_group = all(summary["prospective_reproduction"]["group_addition_below_rho"] for summary in target_summaries)
    any_unit = any(summary["prospective_reproduction"]["unit_cost_below_rho"] for summary in target_summaries)
    if all_full and all_group and any_unit:
        return "P750_PROSPECTIVE_PREFIX_FULL_RECOVERY_WITH_LA_UNIT_WIN"
    if all_full and all_group:
        return "P750_PROSPECTIVE_PREFIX_GROUP_BELOW_RHO_LA_UNIT_COST_NEGATIVE"
    if all_full:
        return "P750_PROSPECTIVE_PREFIX_FULL_RECOVERY_GROUP_COST_NEGATIVE"
    return "NEGATIVE_RESULT_P750_PROSPECTIVE_PREFIX_REPLAY_NOT_REPRODUCED"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p746 = load_module("ecdlp_p746_incremental_walk", P746_SCRIPT)
    p748 = load_module("ecdlp_p748_matrix_bridge", P748_SCRIPT)
    relprobe = p746.load_relation_probe_module()
    target_budgets = parse_target_budgets(args.target_budgets) if args.target_budgets else target_budgets_from_p749(args.p749_summary)
    if not target_budgets:
        raise RuntimeError("no target budgets provided or found in P749 summary")
    challenge_counts = [int(item) for item in args.challenge_counts.split(",") if item.strip()]
    target_summaries = []
    raw_results: dict[str, list[dict[str, Any]]] = {}
    for target, budget in target_budgets.items():
        rows, order = collect_target_rows(
            p746,
            p748,
            relprobe,
            target,
            budget,
            args.seed_count,
            args.factor_base_size,
            args.width,
            args.walk_mode,
            args.seed_prefix,
            args.max_relations,
            args.max_subsets,
        )
        raw_results[target] = [strip_private(row) for row in rows]
        target_summaries.append(summarize_target(p748, target, rows, order, budget, challenge_counts))
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p749_summary": str(args.p749_summary),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(target_summaries),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "PROSPECTIVE-PREFIX: collection is rerun with the fixed public budget, not replayed from longer scans.",
            "LINEAR-ALGEBRA-COUNTED: RREF field inversions, multiplications, and additions are counted under a simple dense elimination model.",
            "UNIT-COST MODEL-BOUND: group additions plus field ops is a conservative unit model, not a calibrated deployment cost model.",
            "MANY-TARGET MODEL: target-specific factor-base setup is shared across many synthetic public keys.",
        ],
        "method": "p750_prospective_prefix_linear_algebra_charge",
        "parameters": {
            "challenge_counts": challenge_counts,
            "factor_base_size": args.factor_base_size,
            "max_relations": args.max_relations,
            "max_subsets": args.max_subsets,
            "p749_summary": str(args.p749_summary),
            "seed_count": args.seed_count,
            "seed_prefix": args.seed_prefix,
            "target_budgets": target_budgets,
            "walk_mode": args.walk_mode,
            "width": args.width,
        },
        "results": raw_results,
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
    parser.add_argument("--p749-summary", type=Path, default=DEFAULT_P749_SUMMARY)
    parser.add_argument("--target-budgets", default="")
    parser.add_argument("--seed-count", type=int, default=256)
    parser.add_argument("--seed-prefix", default="ecdlp-p746-scheduled-seed-extension-v1")
    parser.add_argument("--factor-base-size", type=int, default=48)
    parser.add_argument("--width", type=int, default=2)
    parser.add_argument("--walk-mode", default="hash6")
    parser.add_argument("--max-relations", type=int, default=96)
    parser.add_argument("--max-subsets", type=int, default=25000)
    parser.add_argument("--challenge-counts", default="32,64,96,128,160,192,224,256")
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
                        "budget": item["budget"],
                        "cost": item["cost_summary"],
                        "matrix": {
                            "field_ops": item["matrix_summary"]["counted_rref"]["operation_counts"]["total_field_ops"],
                            "forms": item["matrix_summary"]["form_count"],
                            "rank": item["matrix_summary"]["raw_coefficient_rank"],
                            "secrets": item["matrix_summary"]["secret_match_count"],
                        },
                        "reproduction": item["prospective_reproduction"],
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
