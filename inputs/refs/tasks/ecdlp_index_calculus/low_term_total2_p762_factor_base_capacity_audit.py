#!/usr/bin/env python3
"""P762 factor-base capacity audit for the P761 rank plateau."""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P760_SCRIPT = TASK_DIR / "low_term_total2_p760_public_sparse_policy_selector.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P761_SUMMARY = STATE_DIR / "low_term_total2_p761_selector_scaling_stress_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p762_factor_base_capacity_audit_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p762_factor_base_capacity_audit.md"
SCHEMA = "ecdlp.low_term_total2_p762_factor_base_capacity_audit.v1"


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


def csv_ints(raw: str) -> list[int]:
    return [int(item.strip()) for item in raw.split(",") if item.strip()]


def csv_strings(raw: str) -> list[str]:
    return [item.strip() for item in raw.split(",") if item.strip()]


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


def entropy_from_counts(counts: Counter[int]) -> float:
    total = sum(counts.values())
    if total <= 0:
        return 0.0
    entropy = 0.0
    for count in counts.values():
        p = count / total
        entropy -= p * math.log2(p)
    return round(entropy, 8)


def parse_cases(raw: str) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue
        parts = item.split("|")
        if len(parts) != 6:
            raise argparse.ArgumentTypeError(
                "cases must be label|target|budget|requested_factor_base_size|seed_prefix|arm entries"
            )
        label, target, budget, requested_factor_base_size, seed_prefix, arm = (
            part.strip() for part in parts
        )
        cases.append(
            {
                "arm": arm,
                "budget": int(budget),
                "label": label,
                "requested_factor_base_size": int(requested_factor_base_size),
                "seed_prefix": seed_prefix,
                "target": target,
            }
        )
    if not cases:
        raise argparse.ArgumentTypeError("at least one case is required")
    return cases


def factor_count_for_rows(rows: list[dict[str, Any]]) -> int:
    return max((len(form.get("coeffs") or []) - 1 for row in rows for form in row.get("forms") or []), default=0)


def row_observation(row: dict[str, Any]) -> dict[str, Any]:
    factor_counts = [len(form.get("coeffs") or []) - 1 for form in row.get("forms") or []]
    tail_nonzero_forms = 0
    for form in row.get("forms") or []:
        coeffs = [int(value) for value in (form.get("coeffs") or [])]
        if any(value for value in coeffs[49:]):
            tail_nonzero_forms += 1
    return {
        "accepted_mixed_relations": int(row.get("accepted_mixed_relations") or 0),
        "actual_factor_base_size": int(row.get("factor_base_size") or 0),
        "decomposition_hits": int(row.get("decomposition_hits") or 0),
        "form_count": len(row.get("forms") or []),
        "max_form_factor_count": max(factor_counts, default=0),
        "mixed_wide_relation_rank": int(row.get("mixed_wide_relation_rank") or 0),
        "seed_label": row.get("seed_label"),
        "tail_nonzero_forms_ge_48": tail_nonzero_forms,
    }


def source_counts(relations: list[dict[str, Any]]) -> dict[str, int]:
    counts = Counter(str(relation.get("source") or "") for relation in relations)
    return {key: counts[key] for key in sorted(counts)}


def relation_support_stats(relations: list[dict[str, Any]], order: int) -> dict[str, Any]:
    active_columns: set[int] = set()
    column_counts: Counter[int] = Counter()
    support_sizes: list[int] = []
    tail_relation_count = 0
    for relation in relations:
        coeffs = [int(value) % order for value in relation.get("coeffs") or []]
        support = [index for index, value in enumerate(coeffs) if value]
        if any(index >= 48 for index in support):
            tail_relation_count += 1
        support_sizes.append(len(support))
        for index in support:
            active_columns.add(index)
            column_counts[index] += 1
    return {
        "active_column_count": len(active_columns),
        "active_columns_ge_48": sum(1 for index in active_columns if index >= 48),
        "column_support_entropy": entropy_from_counts(column_counts),
        "max_active_column": max(active_columns) if active_columns else None,
        "relation_count": len(relations),
        "relation_source_counts": source_counts(relations),
        "support_size": stat(support_sizes),
        "tail_relation_count_ge_48": tail_relation_count,
    }


def solve_policy_results(
    p752: Any,
    p760: Any,
    selected_rows: list[dict[str, Any]],
    scanned_rows: list[dict[str, Any]],
    relations: list[dict[str, Any]],
    factor_count: int,
    sparse_policies: list[str],
    order: int,
    substitution_ops_per_selected: int,
) -> list[dict[str, Any]]:
    results = []
    for sparse_policy in sparse_policies:
        ordered = p752.order_relations(relations, sparse_policy)
        solve = p752.sparse_incremental_solve(ordered, factor_count, order)
        cost = p760.public_operation_costs(
            selected_rows,
            scanned_rows,
            solve,
            2,
            substitution_ops_per_selected,
        )
        results.append(
            {
                "full_rank_exported_factor_count": bool(solve["full_rank"]),
                "operation_counts": solve["operation_counts"],
                "policy": sparse_policy,
                "rank": int(solve["rank"]),
                "scanned_to_full_rank": solve["scanned_to_full_rank"],
                "weight2_total_over_selected_rho": cost.get("total_unit_cost_over_selected_rho"),
            }
        )
    return results


def best_policy_by_rank(results: list[dict[str, Any]]) -> dict[str, Any]:
    if not results:
        return {}
    return max(
        results,
        key=lambda item: (
            int(item["rank"]),
            1 if item["full_rank_exported_factor_count"] else 0,
            -float(item["weight2_total_over_selected_rho"] or 10**18),
            item["policy"],
        ),
    )


def evaluate_selected_count(
    p755: Any,
    p748: Any,
    p752: Any,
    p760: Any,
    rows: list[dict[str, Any]],
    selected_count: int,
    pool_count: int,
    row_policy: str,
    sparse_policies: list[str],
    order: int,
    substitution_ops_per_selected: int,
) -> dict[str, Any]:
    selection = p755.select_rows(rows, selected_count, pool_count, row_policy)
    selected_rows = selection["selected_rows"]
    scanned_rows = selection["scanned_rows"]
    exported_factor_count = factor_count_for_rows(selected_rows)
    relations = p752.annotated_relations(
        p748.factor_eliminated_relations(selected_rows, order, exported_factor_count),
        order,
    )
    policy_results = solve_policy_results(
        p752,
        p760,
        selected_rows,
        scanned_rows,
        relations,
        exported_factor_count,
        sparse_policies,
        order,
        substitution_ops_per_selected,
    )
    return {
        "best_policy_by_rank": best_policy_by_rank(policy_results),
        "dropped_from_scanned": selection["dropped_from_scanned"][:24],
        "exported_factor_count": exported_factor_count,
        "policy_results": policy_results,
        "relation_support_stats": relation_support_stats(relations, order),
        "scanned_count": len(scanned_rows),
        "scanned_seed_max": selection["scanned_seed_max"],
        "selected_count": len(selected_rows),
        "selected_feature_stats": p760.selected_feature_stats(p755, selected_rows),
        "selected_seed_sample": selection["selected_seed_labels"][:12],
        "target_selected_count": selected_count,
    }


def classify_case(case_summary: dict[str, Any]) -> str:
    requested = int(case_summary["requested_factor_base_size"])
    max_exported = int(case_summary["max_exported_factor_count"])
    max_rank = int(case_summary["max_sparse_rank"])
    support_ge_48 = int(case_summary["max_active_columns_ge_48"])
    actual_max = int(case_summary["actual_factor_base_size"]["max"] or 0)
    if requested > 48 and actual_max <= 48 and max_exported <= 48 and max_rank <= 48 and support_ge_48 == 0:
        return "capacity_bound_at_48"
    if max_exported > 48 or max_rank > 48 or support_ge_48 > 0:
        return "rank_expansion_signal"
    if max_exported >= requested and max_rank < max_exported:
        return "relation_rank_failure"
    if requested == max_exported and max_rank == max_exported:
        return "baseline_full_rank"
    return "inconclusive"


def evaluate_case(
    p755: Any,
    p748: Any,
    p750: Any,
    p752: Any,
    p760: Any,
    p746: Any,
    relprobe: Any,
    case: dict[str, Any],
    args: argparse.Namespace,
    selected_counts: list[int],
    sparse_policies: list[str],
) -> dict[str, Any]:
    rows, order = p750.collect_target_rows(
        p746,
        p748,
        relprobe,
        case["target"],
        int(case["budget"]),
        int(args.seed_count),
        int(case["requested_factor_base_size"]),
        int(args.width),
        str(args.walk_mode),
        str(case["seed_prefix"]),
        int(args.max_relations),
        int(args.max_subsets),
    )
    row_observations = [row_observation(row) for row in rows]
    selected_evaluations = [
        evaluate_selected_count(
            p755,
            p748,
            p752,
            p760,
            rows,
            selected_count,
            int(args.pool_count),
            str(args.row_policy),
            sparse_policies,
            order,
            int(args.public_substitution_ops_per_selected),
        )
        for selected_count in selected_counts
        if selected_count <= int(args.pool_count)
    ]
    max_active_columns_ge_48 = max(
        (item["relation_support_stats"]["active_columns_ge_48"] for item in selected_evaluations),
        default=0,
    )
    summary = {
        "actual_factor_base_size": stat([item["actual_factor_base_size"] for item in row_observations]),
        "arm": case["arm"],
        "base_order": order,
        "budget": int(case["budget"]),
        "case": case["label"],
        "generic_rho_steps": int(rows[0]["generic_rho_steps"]) if rows else None,
        "max_active_columns_ge_48": max_active_columns_ge_48,
        "max_exported_factor_count": max((item["exported_factor_count"] for item in selected_evaluations), default=0),
        "max_sparse_rank": max(
            (
                result["rank"]
                for item in selected_evaluations
                for result in item["policy_results"]
            ),
            default=0,
        ),
        "requested_factor_base_size": int(case["requested_factor_base_size"]),
        "row_observations": row_observations,
        "rows_collected": len(rows),
        "seed_prefix": case["seed_prefix"],
        "selected_evaluations": selected_evaluations,
        "target": case["target"],
    }
    summary["failure_class"] = classify_case(summary)
    return summary


def class_counts(case_summaries: list[dict[str, Any]]) -> dict[str, int]:
    counts = Counter(str(item["failure_class"]) for item in case_summaries)
    return {key: counts[key] for key in sorted(counts)}


def determine_claim(case_summaries: list[dict[str, Any]]) -> str:
    requested_wide = [item for item in case_summaries if int(item["requested_factor_base_size"]) > 48]
    if any(item["failure_class"] == "rank_expansion_signal" for item in requested_wide):
        return "P762_FACTOR_BASE_RANK_EXPANSION_SIGNAL"
    if requested_wide and all(item["failure_class"] == "capacity_bound_at_48" for item in requested_wide):
        return "P762_FACTOR_BASE_CAPACITY_BOUND_SIGNAL"
    if any(item["failure_class"] == "capacity_bound_at_48" for item in requested_wide):
        return "P762_FACTOR_BASE_CAPACITY_MIXED_SIGNAL"
    return "NEGATIVE_RESULT_P762_FACTOR_BASE_CAPACITY_AUDIT"


def p761_control(path: Path) -> dict[str, Any]:
    payload = load_json(path)
    summary = payload.get("summary") or {}
    return {
        "claim_status": payload.get("claim_status"),
        "public_selector_gap_count": summary.get("public_selector_gap_count"),
        "public_selector_pass_count": summary.get("public_selector_pass_count"),
        "public_selector_recovery_ok_count": summary.get("public_selector_recovery_ok_count"),
        "strict_pass_case_count": summary.get("strict_pass_case_count"),
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p760 = load_module("ecdlp_p760_public_sparse_policy_selector", P760_SCRIPT)
    p755 = p760.load_module("ecdlp_p755_public_selector", p760.P755_SCRIPT)
    p746 = p755.load_module("ecdlp_p746_incremental_walk", p755.P746_SCRIPT)
    p748 = p755.load_module("ecdlp_p748_matrix_bridge", p755.P748_SCRIPT)
    p750 = p755.load_module("ecdlp_p750_prospective_prefix", p755.P750_SCRIPT)
    p752 = p755.load_module("ecdlp_p752_sparse_factor_basis", p755.P752_SCRIPT)
    relprobe = p746.load_relation_probe_module()
    cases = parse_cases(args.cases)
    selected_counts = csv_ints(args.selected_counts)
    sparse_policies = csv_strings(args.sparse_policies)
    case_summaries = [
        evaluate_case(
            p755,
            p748,
            p750,
            p752,
            p760,
            p746,
            relprobe,
            case,
            args,
            selected_counts,
            sparse_policies,
        )
        for case in cases
    ]
    wide_cases = [item for item in case_summaries if int(item["requested_factor_base_size"]) > 48]
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p761_summary": str(args.p761_summary),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(case_summaries),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "CAPACITY-AUDIT: this tests whether requested wider factor bases are actually exported.",
            "PUBLIC-DIAGNOSTIC: no expected secrets are used in the capacity or rank measurements.",
            "RANK-BOUNDARY: below-rho costs are not interpreted as index-calculus progress unless exported factor count and rank both expand.",
            "NO DEPLOYED-CURVE CLAIM: no large-prime scaling or production-key relevance is implied.",
        ],
        "method": "p762_factor_base_capacity_audit",
        "p761_control": p761_control(args.p761_summary),
        "parameters": {
            "cases": cases,
            "max_relations": args.max_relations,
            "max_subsets": args.max_subsets,
            "pool_count": args.pool_count,
            "public_substitution_ops_per_selected": args.public_substitution_ops_per_selected,
            "row_policy": args.row_policy,
            "seed_count": args.seed_count,
            "selected_counts": selected_counts,
            "sparse_policies": sparse_policies,
            "walk_mode": args.walk_mode,
            "width": args.width,
        },
        "schema": SCHEMA,
        "summary": {
            "case_count": len(case_summaries),
            "case_summaries": case_summaries,
            "capacity_bound_wide_case_count": sum(
                1 for item in wide_cases if item["failure_class"] == "capacity_bound_at_48"
            ),
            "class_counts": class_counts(case_summaries),
            "max_exported_factor_count": max((item["max_exported_factor_count"] for item in case_summaries), default=0),
            "max_sparse_rank": max((item["max_sparse_rank"] for item in case_summaries), default=0),
            "rank_expansion_case_count": sum(
                1 for item in wide_cases if item["failure_class"] == "rank_expansion_signal"
            ),
            "wide_case_count": len(wide_cases),
        },
    }


def slim_selected_evaluation(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "best_policy_by_rank": item["best_policy_by_rank"],
        "exported_factor_count": item["exported_factor_count"],
        "relation_support_stats": item["relation_support_stats"],
        "scanned_count": item["scanned_count"],
        "selected_count": item["selected_count"],
        "target_selected_count": item["target_selected_count"],
        "zero_form_selected_rows": item["selected_feature_stats"]["zero_form_rows"],
    }


def slim_case(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "actual_factor_base_size": item["actual_factor_base_size"],
        "arm": item["arm"],
        "base_order": item["base_order"],
        "budget": item["budget"],
        "case": item["case"],
        "failure_class": item["failure_class"],
        "generic_rho_steps": item["generic_rho_steps"],
        "max_active_columns_ge_48": item["max_active_columns_ge_48"],
        "max_exported_factor_count": item["max_exported_factor_count"],
        "max_sparse_rank": item["max_sparse_rank"],
        "requested_factor_base_size": item["requested_factor_base_size"],
        "rows_collected": item["rows_collected"],
        "selected_evaluations": [slim_selected_evaluation(selected) for selected in item["selected_evaluations"]],
        "target": item["target"],
    }


def summary_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": f"{SCHEMA}.summary",
        "artifacts": payload["artifacts"],
        "claim_status": payload["claim_status"],
        "created_at": payload["created_at"],
        "honesty_boundary": payload["honesty_boundary"],
        "method": payload["method"],
        "p761_control": payload["p761_control"],
        "parameters": payload["parameters"],
        "summary": {
            "capacity_bound_wide_case_count": payload["summary"]["capacity_bound_wide_case_count"],
            "case_count": payload["summary"]["case_count"],
            "case_summaries": [slim_case(item) for item in payload["summary"]["case_summaries"]],
            "class_counts": payload["summary"]["class_counts"],
            "max_exported_factor_count": payload["summary"]["max_exported_factor_count"],
            "max_sparse_rank": payload["summary"]["max_sparse_rank"],
            "rank_expansion_case_count": payload["summary"]["rank_expansion_case_count"],
            "wide_case_count": payload["summary"]["wide_case_count"],
        },
    }


def default_cases() -> str:
    targets = [
        ("67.a1@9803", 66, "67"),
        ("22050.cf1@10531", 66, "22050"),
        ("114224.v1@9341", 64, "114224"),
        ("21175.bc1@8089", 58, "21175"),
        ("23232.cr1@8467", 60, "23232a"),
        ("23232.cr1@9643", 64, "23232b"),
        ("67.a1@11923", 72, "67b"),
    ]
    entries = []
    for requested in (48, 64, 80):
        for target, budget, tag in targets:
            entries.append(
                f"fb{requested}_{tag}|{target}|{budget}|{requested}|ecdlp-p762-fb{requested}-{tag}-v1|fb{requested}"
            )
    return ",".join(entries)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", default=default_cases())
    parser.add_argument("--p761-summary", type=Path, default=DEFAULT_P761_SUMMARY)
    parser.add_argument("--seed-count", type=int, default=256)
    parser.add_argument("--selected-counts", default="64,128,192")
    parser.add_argument("--pool-count", type=int, default=256)
    parser.add_argument("--row-policy", default="sequential_min_forms_ge_1")
    parser.add_argument("--sparse-policies", default="natural,support_asc,support_span_asc,pivot_low,pivot_high,coefficient_weight_asc")
    parser.add_argument("--width", type=int, default=2)
    parser.add_argument("--walk-mode", default="hash6")
    parser.add_argument("--max-relations", type=int, default=96)
    parser.add_argument("--max-subsets", type=int, default=25000)
    parser.add_argument("--public-substitution-ops-per-selected", type=int, default=6)
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
                "capacity_bound_wide_case_count": summary["summary"]["capacity_bound_wide_case_count"],
                "claim_status": summary["claim_status"],
                "class_counts": summary["summary"]["class_counts"],
                "max_exported_factor_count": summary["summary"]["max_exported_factor_count"],
                "max_sparse_rank": summary["summary"]["max_sparse_rank"],
                "rank_expansion_case_count": summary["summary"]["rank_expansion_case_count"],
                "wide_case_count": summary["summary"]["wide_case_count"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
