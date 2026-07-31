#!/usr/bin/env python3
"""P777 merged frozen-trim12 factor-first cost audit."""

from __future__ import annotations

import argparse
import importlib.util
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P764_SCRIPT = TASK_DIR / "low_term_total2_p764_widened_factor_basis_cost_validation.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P763_SUMMARY = STATE_DIR / "low_term_total2_p763_factor_base_limit_extension_smoke_summary.json"
DEFAULT_P774_PROBE = STATE_DIR / "low_term_total2_p774_public_budget_selector_all_groups_probe.json"
DEFAULT_P775_PROBE = STATE_DIR / "low_term_total2_p775_public_budget_selector_holdout_transfer_probe.json"
DEFAULT_P776_PROBE = STATE_DIR / "low_term_total2_p776_large_holdout_trim12_vs_selector_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p777_merged_trim12_factor_first_cost_audit_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p777_merged_trim12_factor_first_cost_audit.md"
SCHEMA = "ecdlp.low_term_total2_p777_merged_trim12_factor_first_cost_audit.v1"

FROZEN_DELTA = -12
TARGET_SELECTED_COUNT = 1024
SUPPLEMENTAL_CASES = [
    {
        "arm": "fb96_s1024_dm12",
        "budget": 54,
        "factor_base_size": 96,
        "label": "fb96_s1024_dm12_67a9803",
        "pool_count": 1152,
        "seed_count": 1152,
        "seed_prefix": "ecdlp-p777-fb96-s1024-dm12-67a9803-v1",
        "selected_count": 1024,
        "target": "67.a1@9803",
    }
]


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


def case_string(cases: list[dict[str, Any]]) -> str:
    return ",".join(
        "|".join(
            [
                str(case["label"]),
                str(case["target"]),
                str(case["budget"]),
                str(case["factor_base_size"]),
                str(case["selected_count"]),
                str(case["seed_count"]),
                str(case["pool_count"]),
                str(case["seed_prefix"]),
                str(case["arm"]),
            ]
        )
        for case in cases
    )


def group_key(item: dict[str, Any]) -> str:
    return f"fb{int(item['factor_base_size'])}|{item['target']}"


def cost_for_weight(sparse: dict[str, Any], weight: int = 2) -> dict[str, Any]:
    for cost in sparse.get("costs_by_field_weight") or []:
        if int(cost.get("field_op_weight") or 0) == weight:
            return cost
    return {}


def sparse(item: dict[str, Any]) -> dict[str, Any]:
    return item["public_selector_sparse_policy"]


def strict_pass(item: dict[str, Any]) -> bool:
    return item.get("failure_class") == "pass"


def recovery_ok(item: dict[str, Any]) -> bool:
    sp = sparse(item)
    solve = sp.get("solve") or {}
    substitution = sp.get("substitution") or {}
    return bool(
        item.get("public_selector_recovery_ok")
        and int(solve.get("rank") or 0) == int(item["factor_base_size"])
        and int(substitution.get("recovered_count") or 0) == int(item["selected_count"])
        and int(substitution.get("mismatch_count") or 0) == 0
    )


def capacity_ok(item: dict[str, Any]) -> bool:
    support = item.get("selected_relation_support_stats") or {}
    return (
        int(item.get("selected_exported_factor_count") or 0) == int(item["factor_base_size"])
        and int(support.get("active_column_count") or 0) == int(item["factor_base_size"])
    )


def selected_count_ok(item: dict[str, Any]) -> bool:
    return int(item.get("selected_count") or 0) == TARGET_SELECTED_COUNT


def slim_case(item: dict[str, Any], source: str) -> dict[str, Any]:
    sp = sparse(item)
    cost = cost_for_weight(sp, 2)
    support = item.get("selected_relation_support_stats") or {}
    solve = sp.get("solve") or {}
    substitution = sp.get("substitution") or {}
    return {
        "active_column_count": support.get("active_column_count"),
        "budget": item.get("budget"),
        "case": item.get("case"),
        "capacity_ok": capacity_ok(item),
        "factor_bucket": f"fb{int(item['factor_base_size'])}",
        "factor_base_size": item.get("factor_base_size"),
        "factor_first_field_ops": cost.get("sparse_factor_first_field_ops"),
        "factor_relation_count": sp.get("factor_relation_count"),
        "failure_class": item.get("failure_class"),
        "generic_rho_steps": item.get("generic_rho_steps"),
        "group_key": group_key(item),
        "mismatch_count": substitution.get("mismatch_count"),
        "policy": sp.get("sparse_policy"),
        "rank": solve.get("rank"),
        "recovered_count": substitution.get("recovered_count"),
        "recovery_ok": recovery_ok(item),
        "scanned_count": item.get("scanned_count"),
        "scan_group_additions": cost.get("candidate_scan_group_addition_cost"),
        "selected_count": item.get("selected_count"),
        "selected_count_ok": selected_count_ok(item),
        "selected_rho_baseline": cost.get("selected_rho_baseline"),
        "solve_field_ops": cost.get("sparse_solve_field_ops"),
        "source": source,
        "strict_pass": strict_pass(item),
        "substitution_field_ops": cost.get("substitution_field_ops"),
        "target": item.get("target"),
        "total_unit_cost": cost.get("total_unit_cost_group_additions_plus_weighted_field_ops"),
        "weight2_over_selected_rho": cost.get("total_unit_cost_over_selected_rho"),
        "weighted_sparse_field_ops": cost.get("weighted_sparse_field_ops"),
    }


def frozen_trim12_cases_from_probe(path: Path, source: str) -> list[dict[str, Any]]:
    payload = load_json(path)
    cases = ((payload.get("p764_payload") or {}).get("summary") or {}).get("case_summaries") or []
    out = []
    for item in cases:
        if int(item.get("selected_count") or 0) != TARGET_SELECTED_COUNT:
            continue
        if int(item.get("factor_base_size") or 0) not in (96, 112):
            continue
        if "_dm12_" not in str(item.get("case") or ""):
            continue
        out.append(slim_case(item, source))
    return out


def run_supplemental(args: argparse.Namespace) -> dict[str, Any]:
    if not SUPPLEMENTAL_CASES:
        return {}
    p764 = load_module("ecdlp_p764_for_p777", P764_SCRIPT)
    p764_args = argparse.Namespace(
        arm_threshold=1,
        cases=case_string(SUPPLEMENTAL_CASES),
        field_weights=args.field_weights,
        max_relations=args.max_relations,
        max_subsets=args.max_subsets,
        p763_summary=args.p763_summary,
        primary_threshold=1,
        public_substitution_ops_per_selected=args.public_substitution_ops_per_selected,
        row_policy=args.row_policy,
        sparse_policies=args.sparse_policies,
        walk_mode=args.walk_mode,
        width=args.width,
    )
    return p764.analyze(p764_args)


def stat(values: list[float]) -> dict[str, Any]:
    if not values:
        return {"count": 0, "max": None, "mean": None, "min": None}
    return {
        "count": len(values),
        "max": max(values),
        "mean": round(mean(values), 8),
        "min": min(values),
    }


def bucket_counts(cases: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for item in cases:
        bucket_key = str(item[key])
        bucket = out.setdefault(
            bucket_key,
            {
                "capacity_ok_count": 0,
                "case_count": 0,
                "recovery_ok_count": 0,
                "selected_count_ok_count": 0,
                "strict_pass_count": 0,
            },
        )
        bucket["case_count"] += 1
        bucket["capacity_ok_count"] += int(item["capacity_ok"])
        bucket["recovery_ok_count"] += int(item["recovery_ok"])
        bucket["selected_count_ok_count"] += int(item["selected_count_ok"])
        bucket["strict_pass_count"] += int(item["strict_pass"])
    return out


def aggregate_cost(cases: list[dict[str, Any]]) -> dict[str, Any]:
    scan = sum(int(item.get("scan_group_additions") or 0) for item in cases)
    field = sum(int(item.get("factor_first_field_ops") or 0) for item in cases)
    weighted_field = sum(int(item.get("weighted_sparse_field_ops") or 0) for item in cases)
    solve = sum(int(item.get("solve_field_ops") or 0) for item in cases)
    sub = sum(int(item.get("substitution_field_ops") or 0) for item in cases)
    total = sum(int(item.get("total_unit_cost") or 0) for item in cases)
    rho = sum(int(item.get("selected_rho_baseline") or 0) for item in cases)
    return {
        "aggregate_weight2_total_over_selected_rho": round(total / rho, 8) if rho else None,
        "scan_group_additions": scan,
        "selected_rho_baseline": rho,
        "sparse_factor_first_field_ops": field,
        "sparse_solve_field_ops": solve,
        "substitution_field_ops": sub,
        "total_unit_cost": total,
        "weighted_sparse_field_ops": weighted_field,
    }


def duplicate_groups(cases: list[dict[str, Any]]) -> dict[str, int]:
    counts = Counter(item["group_key"] for item in cases)
    return {key: count for key, count in sorted(counts.items()) if count > 1}


def expected_groups(cases: list[dict[str, Any]]) -> list[str]:
    targets = sorted({str(item["target"]) for item in cases})
    return [f"{fb}|{target}" for target in targets for fb in ("fb96", "fb112")]


def determine_claim(summary: dict[str, Any]) -> str:
    total = int(summary["normalized_group_count"])
    strict_count = int(summary["strict_pass_count"])
    recovery_count = int(summary["recovery_ok_count"])
    capacity_count = int(summary["capacity_ok_count"])
    selected_count = int(summary["selected_count_ok_count"])
    missing = int(summary["missing_group_count"])
    aggregate = summary["aggregate_cost"]["aggregate_weight2_total_over_selected_rho"]
    if (
        total
        and missing == 0
        and strict_count == total
        and recovery_count == total
        and capacity_count == total
        and selected_count == total
        and aggregate is not None
        and float(aggregate) < 1.0
    ):
        return "P777_MERGED_TRIM12_FACTOR_FIRST_ALL_GROUP_SIGNAL"
    if (
        total
        and missing == 0
        and strict_count >= max(1, total - 1)
        and recovery_count == total
        and capacity_count == total
        and selected_count == total
        and aggregate is not None
        and float(aggregate) < 1.0
    ):
        return "P777_MERGED_TRIM12_FACTOR_FIRST_USEFUL_SIGNAL"
    if missing:
        return "P777_MERGED_TRIM12_MISSING_NORMALIZED_GROUP"
    if selected_count < total:
        return "P777_MERGED_TRIM12_SELECTED_COUNT_REGRESSION"
    if recovery_count == total and capacity_count == total:
        return "P777_MERGED_TRIM12_RECOVERY_OK_COST_NEGATIVE"
    return "NEGATIVE_RESULT_P777_MERGED_TRIM12_FACTOR_FIRST_COST_AUDIT"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    reused = []
    source_paths = {
        "p774": args.p774_probe,
        "p775": args.p775_probe,
        "p776": args.p776_probe,
    }
    for source, path in source_paths.items():
        reused.extend(frozen_trim12_cases_from_probe(path, source))
    supplemental_payload = run_supplemental(args)
    supplemental_cases = [
        slim_case(item, "p777_supplemental")
        for item in (((supplemental_payload.get("summary") or {}).get("case_summaries")) or [])
    ]
    all_cases = sorted(reused + supplemental_cases, key=lambda item: item["group_key"])
    groups = sorted({item["group_key"] for item in all_cases})
    expected = expected_groups(all_cases)
    missing = sorted(set(expected) - set(groups))
    duplicates = duplicate_groups(all_cases)
    weights = [
        float(item["weight2_over_selected_rho"])
        for item in all_cases
        if item.get("weight2_over_selected_rho") is not None
    ]
    summary = {
        "aggregate_cost": aggregate_cost(all_cases),
        "capacity_ok_count": sum(1 for item in all_cases if item["capacity_ok"]),
        "duplicate_groups": duplicates,
        "expected_group_count": len(expected),
        "factor_summaries": bucket_counts(all_cases, "factor_bucket"),
        "max_weight2_group": max(all_cases, key=lambda item: item["weight2_over_selected_rho"] or -1),
        "missing_group_count": len(missing),
        "missing_groups": missing,
        "normalized_cases": all_cases,
        "normalized_group_count": len(groups),
        "recovery_ok_count": sum(1 for item in all_cases if item["recovery_ok"]),
        "reused_case_count": len(reused),
        "selected_count_ok_count": sum(1 for item in all_cases if item["selected_count_ok"]),
        "source_summaries": bucket_counts(all_cases, "source"),
        "strict_pass_count": sum(1 for item in all_cases if item["strict_pass"]),
        "supplemental_case_count": len(supplemental_cases),
        "target_summaries": bucket_counts(all_cases, "target"),
        "weight2_over_selected_rho_stats": stat(weights),
    }
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p774_probe": str(args.p774_probe),
            "p775_probe": str(args.p775_probe),
            "p776_probe": str(args.p776_probe),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(summary),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "MERGED-AUDIT: most cases are reused from P774/P775/P776 fresh seed artifacts; only the missing normalized fb96|67.a1@9803 case is freshly collected in P777.",
            "FROZEN-PUBLIC-BUDGET: all normalized cases use selected count 1024 and budget delta -12.",
            "FACTOR-FIRST-CHARGED: cost includes scanned candidate group additions plus sparse factor-first solve and substitution field operations at weight 2.",
            "PRIVATE-VERIFY-ONLY: expected secrets are used only after public sparse-policy selection to verify recovery and mismatches.",
            "SPARSE-WEIGHT MODEL: field-operation weights are accounting stress tests, not calibrated hardware timings.",
            "NO DEPLOYED-CURVE CLAIM: no large-prime scaling, target descent, or production-key relevance is implied.",
        ],
        "method": "p777_merged_trim12_factor_first_cost_audit",
        "parameters": {
            "field_weights": [int(item) for item in args.field_weights.split(",") if item.strip()],
            "frozen_delta": FROZEN_DELTA,
            "max_relations": args.max_relations,
            "max_subsets": args.max_subsets,
            "public_substitution_ops_per_selected": args.public_substitution_ops_per_selected,
            "row_policy": args.row_policy,
            "selected_count": TARGET_SELECTED_COUNT,
            "sparse_policies": [item.strip() for item in args.sparse_policies.split(",") if item.strip()],
            "supplemental_cases": SUPPLEMENTAL_CASES,
            "walk_mode": args.walk_mode,
            "width": args.width,
        },
        "p777_supplemental_payload": supplemental_payload,
        "schema": SCHEMA,
        "summary": summary,
    }


def summary_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": f"{SCHEMA}.summary",
        "artifacts": payload["artifacts"],
        "claim_status": payload["claim_status"],
        "created_at": payload["created_at"],
        "honesty_boundary": payload["honesty_boundary"],
        "method": payload["method"],
        "parameters": payload["parameters"],
        "summary": payload["summary"],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p763-summary", type=Path, default=DEFAULT_P763_SUMMARY)
    parser.add_argument("--p774-probe", type=Path, default=DEFAULT_P774_PROBE)
    parser.add_argument("--p775-probe", type=Path, default=DEFAULT_P775_PROBE)
    parser.add_argument("--p776-probe", type=Path, default=DEFAULT_P776_PROBE)
    parser.add_argument("--row-policy", default="sequential_min_forms_ge_1")
    parser.add_argument("--sparse-policies", default="natural,support_asc,support_span_asc,pivot_low,pivot_high,coefficient_weight_asc")
    parser.add_argument("--width", type=int, default=2)
    parser.add_argument("--walk-mode", default="hash6")
    parser.add_argument("--max-relations", type=int, default=96)
    parser.add_argument("--max-subsets", type=int, default=25000)
    parser.add_argument("--field-weights", default="1,2")
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
    agg = summary["summary"]["aggregate_cost"]
    print(f"wrote {args.out}")
    print(f"wrote {summary_out}")
    print(
        json.dumps(
            {
                "aggregate_weight2_total_over_selected_rho": agg["aggregate_weight2_total_over_selected_rho"],
                "capacity_ok_count": summary["summary"]["capacity_ok_count"],
                "claim_status": summary["claim_status"],
                "expected_group_count": summary["summary"]["expected_group_count"],
                "max_weight2": summary["summary"]["weight2_over_selected_rho_stats"]["max"],
                "missing_group_count": summary["summary"]["missing_group_count"],
                "normalized_group_count": summary["summary"]["normalized_group_count"],
                "recovery_ok_count": summary["summary"]["recovery_ok_count"],
                "reused_case_count": summary["summary"]["reused_case_count"],
                "selected_count_ok_count": summary["summary"]["selected_count_ok_count"],
                "strict_pass_count": summary["summary"]["strict_pass_count"],
                "supplemental_case_count": summary["summary"]["supplemental_case_count"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
