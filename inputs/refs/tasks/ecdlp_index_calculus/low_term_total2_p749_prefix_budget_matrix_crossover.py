#!/usr/bin/env python3
"""P749 prefix-budget crossover replay for P748 matrix forms.

P748 solved all 256 challenge secrets per target from full 128-trial selected
policy streams, but stayed slightly above rho before linear algebra. This probe
replays the saved verifier-backed forms by public trial prefix to find the
smallest fixed budget that preserves matrix recovery.
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
DEFAULT_P748 = STATE_DIR / "low_term_total2_p748_setup_amortization_matrix_bridge_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p749_prefix_budget_matrix_crossover_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_order11779_p749_prefix_budget_matrix_crossover.md"
SCHEMA = "ecdlp.low_term_total2_p749_prefix_budget_matrix_crossover.v1"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


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


def parse_csv_ints(raw: str) -> list[int]:
    return [int(item.strip()) for item in raw.split(",") if item.strip()]


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


def add_expected_secrets(p746: Any, relprobe: Any, rows_by_target: dict[str, list[dict[str, Any]]]) -> dict[str, list[dict[str, Any]]]:
    out: dict[str, list[dict[str, Any]]] = {}
    for target, rows in rows_by_target.items():
        _verifier, _record, inv = p746.load_target(relprobe, target)
        label = str(inv["label"])
        p = int(inv["p"])
        order = int(inv["base_order"])
        target_rows: list[dict[str, Any]] = []
        for row in rows:
            copied = dict(row)
            copied["_expected_secret"] = int(relprobe.deterministic_secret(label, p, order, copied["seed"]))
            target_rows.append(copied)
        out[target] = target_rows
    return out


def prefix_rows(rows: list[dict[str, Any]], budget: int) -> list[dict[str, Any]]:
    filtered: list[dict[str, Any]] = []
    for row in rows:
        copied = dict(row)
        copied["forms"] = [form for form in row.get("forms") or [] if int(form.get("trial") or 0) <= budget]
        filtered.append(copied)
    return filtered


def budget_online_group_additions(bit_length: int, delta_setup: int, budget: int) -> int:
    return (2 * bit_length) + 1 + delta_setup + max(0, budget - 1)


def analyze_budget(p748: Any, rows: list[dict[str, Any]], budget: int, order: int) -> dict[str, Any]:
    filtered = prefix_rows(rows, budget)
    matrix = p748.matrix_summary(filtered, order)
    if not rows:
        return {"budget": budget, "matrix_summary": matrix}
    rho = int(rows[0]["generic_rho_steps"])
    setup = int(rows[0]["cost_model"]["subset_group_additions"])
    delta_setup = int(rows[0]["cost_model"]["delta_setup_group_additions"])
    bit_length = max(1, order.bit_length())
    per_challenge_online = budget_online_group_additions(bit_length, delta_setup, budget)
    total = setup + len(rows) * per_challenge_online
    solved = int(matrix.get("secret_match_count") or 0)
    return {
        "budget": budget,
        "cost_summary": {
            "budget_online_group_additions_per_challenge": per_challenge_online,
            "fixed_budget_total_group_additions": total,
            "fixed_budget_total_over_matrix_solved_rho": ratio(total, solved * rho),
            "linear_algebra_cost_charged": False,
            "matrix_solved_rho_baseline": solved * rho,
            "rho": rho,
            "setup_group_additions": setup,
        },
        "matrix_summary": matrix,
        "relation_stats": {
            "accepted_forms": sum(len(row.get("forms") or []) for row in filtered),
            "accepted_forms_per_challenge": stat([len(row.get("forms") or []) for row in filtered]),
        },
    }


def target_budget_summary(target: str, rows: list[dict[str, Any]], budgets: list[int], p748: Any, order: int) -> dict[str, Any]:
    budget_rows = [analyze_budget(p748, rows, budget, order) for budget in budgets]
    full_secret_count = len(rows)
    full_rank_budget_rows = [
        row
        for row in budget_rows
        if int(row["matrix_summary"].get("secret_match_count") or 0) == full_secret_count
        and int(row["matrix_summary"].get("factor_relation_rank") or 0) >= int(row["matrix_summary"].get("factor_count") or 0)
    ]
    below_rho_rows = [
        row
        for row in budget_rows
        if (row["cost_summary"].get("fixed_budget_total_over_matrix_solved_rho") or 10**18) < 1.0
    ]
    best_by_ratio = min(
        [row for row in budget_rows if row["cost_summary"].get("fixed_budget_total_over_matrix_solved_rho") is not None],
        key=lambda row: row["cost_summary"]["fixed_budget_total_over_matrix_solved_rho"],
        default=None,
    )
    return {
        "best_budget_by_group_cost_ratio": best_by_ratio,
        "budget_rows": budget_rows,
        "earliest_below_rho_budget": below_rho_rows[0] if below_rho_rows else None,
        "earliest_full_recovery_budget": full_rank_budget_rows[0] if full_rank_budget_rows else None,
        "full_secret_count": full_secret_count,
        "target": target,
    }


def determine_claim(target_summaries: list[dict[str, Any]]) -> str:
    all_targets_below = all(summary.get("earliest_below_rho_budget") for summary in target_summaries)
    all_targets_full_below = all(
        summary.get("earliest_full_recovery_budget")
        and (summary["earliest_full_recovery_budget"]["cost_summary"].get("fixed_budget_total_over_matrix_solved_rho") or 10**18)
        < 1.0
        for summary in target_summaries
    )
    if all_targets_full_below:
        return "P749_PREFIX_MATRIX_FULL_RECOVERY_BELOW_RHO_SIGNAL_LA_UNCHARGED"
    if all_targets_below:
        return "P749_PREFIX_MATRIX_PARTIAL_BELOW_RHO_SIGNAL_LA_UNCHARGED"
    return "NEGATIVE_RESULT_P749_PREFIX_BUDGET_ABOVE_RHO"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p746 = load_module("ecdlp_p746_incremental_walk", P746_SCRIPT)
    p748 = load_module("ecdlp_p748_matrix_bridge", P748_SCRIPT)
    relprobe = p746.load_relation_probe_module()
    p748_payload = load_json(args.p748_probe)
    rows_by_target = add_expected_secrets(p746, relprobe, p748_payload["results"])
    budgets = parse_csv_ints(args.budgets)
    target_summaries: list[dict[str, Any]] = []
    for target, rows in rows_by_target.items():
        _verifier, _record, inv = p746.load_target(relprobe, target)
        target_summaries.append(target_budget_summary(target, rows, budgets, p748, int(inv["base_order"])))
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p748_probe": str(args.p748_probe),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(target_summaries),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "REPLAY-BOUND: replays P748 verifier-backed forms and charges only forms at or before each public prefix budget.",
            "LINEAR-ALGEBRA-UNCHARGED: matrix rank cost is reported as a field-op proxy, not charged against rho.",
            "MANY-TARGET MODEL: solves many synthetic public keys sharing one target factor base; not a single-target ECDLP break.",
            "NO DEPLOYED-CURVE CLAIM: no large-prime scaling or sparse-linear-algebra implementation is implied.",
        ],
        "method": "p749_prefix_budget_matrix_crossover",
        "parameters": {
            "budgets": budgets,
            "p748_probe": str(args.p748_probe),
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
    parser.add_argument("--p748-probe", type=Path, default=DEFAULT_P748)
    parser.add_argument("--budgets", default="24,32,40,48,56,64,72,80,88,96,104,112,120,128")
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
                        "best_budget": (item.get("best_budget_by_group_cost_ratio") or {}).get("budget"),
                        "best_ratio": ((item.get("best_budget_by_group_cost_ratio") or {}).get("cost_summary") or {}).get(
                            "fixed_budget_total_over_matrix_solved_rho"
                        ),
                        "earliest_below_rho_budget": (item.get("earliest_below_rho_budget") or {}).get("budget"),
                        "earliest_full_recovery_budget": (item.get("earliest_full_recovery_budget") or {}).get("budget"),
                        "full_secret_count": item.get("full_secret_count"),
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
