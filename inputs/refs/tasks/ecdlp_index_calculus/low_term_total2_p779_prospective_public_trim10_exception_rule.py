#!/usr/bin/env python3
"""P779 prospective fresh-seed replay of the P778 public trim10 exception rule."""

from __future__ import annotations

import argparse
import importlib.util
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P764_SCRIPT = TASK_DIR / "low_term_total2_p764_widened_factor_basis_cost_validation.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P763_SUMMARY = STATE_DIR / "low_term_total2_p763_factor_base_limit_extension_smoke_summary.json"
DEFAULT_P777_SUMMARY = STATE_DIR / "low_term_total2_p777_merged_trim12_factor_first_cost_audit_summary.json"
DEFAULT_P778_SUMMARY = STATE_DIR / "low_term_total2_p778_public_trim10_exception_rule_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p779_prospective_public_trim10_exception_rule_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p779_prospective_public_trim10_exception_rule.md"
SCHEMA = "ecdlp.low_term_total2_p779_prospective_public_trim10_exception_rule.v1"

TARGET_SELECTED_COUNT = 1024
TARGET_SEED_COUNT = 1152
TARGET_POOL_COUNT = 1152
TRIM12_DELTA = -12
TRIM10_DELTA = -10
PUBLIC_WEIGHT2_THRESHOLD = 1.0


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


def slug(value: str) -> str:
    text = "".join(ch if ch.isalnum() else "_" for ch in value)
    return "_".join(part for part in text.split("_") if part)


def delta_tag(delta: int) -> str:
    return f"dm{abs(delta)}" if delta < 0 else f"dp{delta}"


def group_key(item: dict[str, Any]) -> str:
    return f"fb{int(item['factor_base_size'])}|{item['target']}"


def factor_bucket(item: dict[str, Any]) -> str:
    return f"fb{int(item['factor_base_size'])}"


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


def budget_delta_from_case(item: dict[str, Any]) -> int | None:
    name = str(item.get("case") or "")
    if "_dm12_" in name:
        return TRIM12_DELTA
    if "_dm10_" in name:
        return TRIM10_DELTA
    return None


def fresh_case_from_group(item: dict[str, Any], delta: int, budget: int | None = None) -> dict[str, Any]:
    fb = factor_bucket(item)
    dtag = delta_tag(delta)
    target = str(item["target"])
    target_slug = slug(target)
    return {
        "arm": f"{fb}_s1024_{dtag}",
        "budget": int(item["budget"] if budget is None else budget),
        "factor_base_size": int(item["factor_base_size"]),
        "label": f"{fb}_s1024_{dtag}_{target_slug}",
        "pool_count": TARGET_POOL_COUNT,
        "seed_count": TARGET_SEED_COUNT,
        "seed_prefix": f"ecdlp-p779-{fb}-s1024-{dtag}-{target_slug}-v1",
        "selected_count": TARGET_SELECTED_COUNT,
        "source_group_key": str(item.get("group_key") or group_key(item)),
        "target": target,
    }


def trim12_cases_from_p777(path: Path) -> list[dict[str, Any]]:
    payload = load_json(path)
    normalized = ((payload.get("summary") or {}).get("normalized_cases")) or []
    cases = []
    seen: set[str] = set()
    for item in sorted(normalized, key=lambda value: str(value.get("group_key") or "")):
        key = str(item.get("group_key") or group_key(item))
        if key in seen:
            raise ValueError(f"duplicate normalized group {key!r} in {path}")
        seen.add(key)
        if int(item.get("selected_count") or 0) != TARGET_SELECTED_COUNT:
            raise ValueError(f"unexpected selected count for {key}: {item.get('selected_count')}")
        if int(item.get("factor_base_size") or 0) not in (96, 112):
            raise ValueError(f"unexpected factor size for {key}: {item.get('factor_base_size')}")
        cases.append(fresh_case_from_group(item, TRIM12_DELTA))
    if not cases:
        raise ValueError(f"no P777 normalized cases found in {path}")
    return cases


def run_p764(args: argparse.Namespace, cases: list[dict[str, Any]], module_name: str) -> dict[str, Any]:
    if not cases:
        return {}
    p764 = load_module(module_name, P764_SCRIPT)
    p764_args = argparse.Namespace(
        arm_threshold=1,
        cases=case_string(cases),
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


def cost_for_weight(sparse: dict[str, Any], key: str = "costs_by_field_weight", weight: int = 2) -> dict[str, Any]:
    for cost in sparse.get(key) or []:
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


def sparse_selector_gap(item: dict[str, Any]) -> bool:
    return bool(item.get("oracle_best_pass_weight2_below_rho") and not item.get("public_selector_pass_weight2_below_rho"))


def slim_candidate(item: dict[str, Any], source: str) -> dict[str, Any]:
    sp = sparse(item)
    verified = cost_for_weight(sp, "costs_by_field_weight", 2)
    public = cost_for_weight(sp, "public_costs_by_field_weight", 2)
    support = item.get("selected_relation_support_stats") or {}
    solve = sp.get("solve") or {}
    substitution = sp.get("substitution") or {}
    public_weight2 = public.get("total_unit_cost_over_selected_rho")
    if public_weight2 is None:
        public_weight2 = verified.get("total_unit_cost_over_selected_rho")
    return {
        "active_column_count": support.get("active_column_count"),
        "budget": item.get("budget"),
        "budget_delta": budget_delta_from_case(item),
        "capacity_ok": capacity_ok(item),
        "case": item.get("case"),
        "factor_bucket": factor_bucket(item),
        "factor_base_size": item.get("factor_base_size"),
        "factor_first_field_ops": verified.get("sparse_factor_first_field_ops"),
        "failure_class": item.get("failure_class"),
        "generic_rho_steps": item.get("generic_rho_steps"),
        "group_key": group_key(item),
        "mismatch_count": substitution.get("mismatch_count"),
        "policy": sp.get("sparse_policy"),
        "public_safe_field_weight": sp.get("public_max_field_op_weight_below_selected_rho")
        or sp.get("max_field_op_weight_below_selected_rho"),
        "public_sparse_selector_gap": sparse_selector_gap(item),
        "public_weight2_missing": not bool(public),
        "public_weight2_over_selected_rho": public_weight2,
        "rank": solve.get("rank"),
        "recovered_count": substitution.get("recovered_count"),
        "recovery_ok": recovery_ok(item),
        "scan_group_additions": verified.get("candidate_scan_group_addition_cost"),
        "scanned_count": item.get("scanned_count"),
        "selected_count": item.get("selected_count"),
        "selected_count_ok": selected_count_ok(item),
        "selected_rho_baseline": verified.get("selected_rho_baseline"),
        "solve_field_ops": verified.get("sparse_solve_field_ops"),
        "source": source,
        "strict_pass": strict_pass(item),
        "substitution_field_ops": verified.get("substitution_field_ops"),
        "target": item.get("target"),
        "total_unit_cost": verified.get("total_unit_cost_group_additions_plus_weighted_field_ops"),
        "weight2_over_selected_rho": verified.get("total_unit_cost_over_selected_rho"),
        "weighted_sparse_field_ops": verified.get("weighted_sparse_field_ops"),
    }


def payload_cases(payload: dict[str, Any], source: str) -> list[dict[str, Any]]:
    cases = ((payload.get("summary") or {}).get("case_summaries")) or []
    return [slim_candidate(item, source) for item in cases]


def aggregate(cases: list[dict[str, Any]]) -> dict[str, Any]:
    total = sum(int(item.get("total_unit_cost") or 0) for item in cases)
    rho = sum(int(item.get("selected_rho_baseline") or 0) for item in cases)
    return {
        "aggregate_weight2_total_over_selected_rho": round(total / rho, 8) if rho else None,
        "scan_group_additions": sum(int(item.get("scan_group_additions") or 0) for item in cases),
        "selected_rho_baseline": rho,
        "sparse_factor_first_field_ops": sum(int(item.get("factor_first_field_ops") or 0) for item in cases),
        "sparse_solve_field_ops": sum(int(item.get("solve_field_ops") or 0) for item in cases),
        "substitution_field_ops": sum(int(item.get("substitution_field_ops") or 0) for item in cases),
        "total_unit_cost": total,
        "weighted_sparse_field_ops": sum(int(item.get("weighted_sparse_field_ops") or 0) for item in cases),
    }


def stat(values: list[float]) -> dict[str, Any]:
    if not values:
        return {"count": 0, "max": None, "mean": None, "min": None}
    return {"count": len(values), "max": max(values), "mean": round(mean(values), 8), "min": min(values)}


def bucket_counts(cases: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for item in cases:
        bucket_key = str(item[key])
        bucket = out.setdefault(
            bucket_key,
            {
                "case_count": 0,
                "capacity_ok_count": 0,
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


def p778_control(path: Path) -> dict[str, Any]:
    payload = load_json(path)
    summary = payload.get("summary") or {}
    return {
        "aggregate_weight2_total_over_selected_rho": (summary.get("aggregate_cost") or {}).get(
            "aggregate_weight2_total_over_selected_rho"
        ),
        "claim_status": payload.get("claim_status"),
        "flagged_group_count": summary.get("flagged_group_count"),
        "selected_group_count": summary.get("selected_group_count"),
        "strict_pass_count": summary.get("strict_pass_count"),
        "switched_group_count": summary.get("switched_group_count"),
    }


def determine_claim(summary: dict[str, Any]) -> str:
    base = int(summary["base_group_count"])
    selected = int(summary["selected_group_count"])
    strict = int(summary["strict_pass_count"])
    recovery = int(summary["recovery_ok_count"])
    capacity = int(summary["capacity_ok_count"])
    selected_count = int(summary["selected_count_ok_count"])
    missing_trim12 = int(summary["missing_trim12_group_count"])
    missing_switch = int(summary["missing_switch_candidate_count"])
    aggregate_value = summary["aggregate_cost"]["aggregate_weight2_total_over_selected_rho"]
    max_weight = summary["weight2_over_selected_rho_stats"]["max"]
    if (
        base
        and selected == base
        and missing_trim12 == 0
        and missing_switch == 0
        and strict == base
        and recovery == base
        and capacity == base
        and selected_count == base
        and aggregate_value is not None
        and float(aggregate_value) < 1.0
        and max_weight is not None
        and float(max_weight) < 1.0
    ):
        return "P779_PROSPECTIVE_TRIM10_EXCEPTION_ALL_GROUP_SIGNAL"
    if (
        base
        and selected == base
        and missing_trim12 == 0
        and missing_switch == 0
        and strict >= max(1, base - 1)
        and recovery == base
        and capacity == base
        and selected_count == base
        and aggregate_value is not None
        and float(aggregate_value) < 1.0
    ):
        return "P779_PROSPECTIVE_TRIM10_EXCEPTION_USEFUL_SIGNAL"
    if missing_trim12:
        return "P779_PROSPECTIVE_TRIM10_EXCEPTION_MISSING_TRIM12"
    if missing_switch:
        return "P779_PROSPECTIVE_TRIM10_EXCEPTION_MISSING_SWITCH"
    if selected_count < selected:
        return "P779_PROSPECTIVE_TRIM10_EXCEPTION_SELECTED_COUNT_REGRESSION"
    if recovery == selected and capacity == selected:
        return "P779_PROSPECTIVE_TRIM10_EXCEPTION_RECOVERY_OK_COST_NEGATIVE"
    return "NEGATIVE_RESULT_P779_PROSPECTIVE_TRIM10_EXCEPTION_RULE"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    trim12_case_defs = trim12_cases_from_p777(args.p777_summary)
    base_groups = sorted(str(item["source_group_key"]) for item in trim12_case_defs)
    trim12_payload = run_p764(args, trim12_case_defs, "ecdlp_p764_for_p779_trim12")
    trim12_cases = payload_cases(trim12_payload, "p779_trim12")
    trim12_by_group = {item["group_key"]: item for item in trim12_cases}
    missing_trim12 = [group for group in base_groups if group not in trim12_by_group]

    flagged_groups = []
    trim10_case_defs = []
    for group in base_groups:
        trim12 = trim12_by_group.get(group)
        if not trim12:
            continue
        public_weight = trim12.get("public_weight2_over_selected_rho")
        flag = public_weight is not None and float(public_weight) >= PUBLIC_WEIGHT2_THRESHOLD
        if flag:
            flagged_groups.append(
                {
                    "group_key": group,
                    "public_weight2_over_selected_rho": public_weight,
                    "trim12_case": trim12.get("case"),
                    "trim12_weight2_over_selected_rho": trim12.get("weight2_over_selected_rho"),
                }
            )
            trim10_case_defs.append(fresh_case_from_group(trim12, TRIM10_DELTA, budget=int(trim12["budget"]) + 2))

    trim10_payload = run_p764(args, trim10_case_defs, "ecdlp_p764_for_p779_trim10") if trim10_case_defs else {}
    trim10_cases = payload_cases(trim10_payload, "p779_trim10") if trim10_payload else []
    trim10_by_group = {item["group_key"]: item for item in trim10_cases}

    selected_cases = []
    missing_switches = []
    for group in base_groups:
        trim12 = trim12_by_group.get(group)
        if not trim12:
            continue
        flag = any(item["group_key"] == group for item in flagged_groups)
        chosen = trim12
        if flag:
            chosen = trim10_by_group.get(group) or trim12
            if group not in trim10_by_group:
                missing_switches.append({"group_key": group, "missing": "trim10"})
        chosen = dict(chosen)
        chosen["exception_flag"] = flag
        chosen["rule_selected_delta"] = int(chosen["budget_delta"]) if chosen.get("budget_delta") is not None else None
        selected_cases.append(chosen)

    selected_cases = sorted(selected_cases, key=lambda item: item["group_key"])
    weights = [
        float(item["weight2_over_selected_rho"])
        for item in selected_cases
        if item.get("weight2_over_selected_rho") is not None
    ]
    delta_counts = Counter(str(item["rule_selected_delta"]) for item in selected_cases)
    summary = {
        "aggregate_cost": aggregate(selected_cases),
        "base_group_count": len(base_groups),
        "base_groups": base_groups,
        "capacity_ok_count": sum(1 for item in selected_cases if item["capacity_ok"]),
        "delta_counts": {key: delta_counts[key] for key in sorted(delta_counts, key=lambda value: int(value))},
        "factor_summaries": bucket_counts(selected_cases, "factor_bucket"),
        "flagged_group_count": len(flagged_groups),
        "flagged_groups": flagged_groups,
        "fresh_trim10_case_count": len(trim10_cases),
        "fresh_trim12_case_count": len(trim12_cases),
        "missing_switch_candidate_count": len(missing_switches),
        "missing_switch_candidates": missing_switches,
        "missing_trim12_group_count": len(missing_trim12),
        "missing_trim12_groups": missing_trim12,
        "p778_control": p778_control(args.p778_summary),
        "public_sparse_selector_gap_count": sum(1 for item in selected_cases if item["public_sparse_selector_gap"]),
        "public_threshold": PUBLIC_WEIGHT2_THRESHOLD,
        "recovery_ok_count": sum(1 for item in selected_cases if item["recovery_ok"]),
        "selected_cases": selected_cases,
        "selected_count_ok_count": sum(1 for item in selected_cases if item["selected_count_ok"]),
        "selected_group_count": len(selected_cases),
        "source_summaries": bucket_counts(selected_cases, "source"),
        "strict_pass_count": sum(1 for item in selected_cases if item["strict_pass"]),
        "switched_group_count": sum(1 for item in selected_cases if item["rule_selected_delta"] == TRIM10_DELTA),
        "target_summaries": bucket_counts(selected_cases, "target"),
        "trim10_case_defs": trim10_case_defs,
        "trim12_case_defs": trim12_case_defs,
        "weight2_over_selected_rho_stats": stat(weights),
    }
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p763_summary": str(args.p763_summary),
            "p777_summary": str(args.p777_summary),
            "p778_summary": str(args.p778_summary),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(summary),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "FRESH-PROSPECTIVE: P779 recollects relation rows under fresh P779 seed prefixes rather than selecting among P774-P778 saved rows.",
            "PUBLIC-THRESHOLD: trim10 exception collection is triggered only by the public trim12 weight-2 estimate crossing the preregistered threshold.",
            "PRIVATE-VERIFY-ONLY: expected secrets are used only after public sparse-policy and exception selection to verify recovery and mismatches.",
            "FACTOR-FIRST-CHARGED: cost includes scanned candidate group additions plus sparse factor-first solve and substitution field operations at weight 2.",
            "NO DEPLOYED-CURVE CLAIM: no large-prime scaling, target descent, or production-key relevance is implied.",
        ],
        "method": "p779_prospective_public_trim10_exception_rule",
        "parameters": {
            "default_delta": TRIM12_DELTA,
            "exception_delta": TRIM10_DELTA,
            "field_weights": [int(item) for item in args.field_weights.split(",") if item.strip()],
            "max_relations": args.max_relations,
            "max_subsets": args.max_subsets,
            "public_substitution_ops_per_selected": args.public_substitution_ops_per_selected,
            "public_weight2_threshold": PUBLIC_WEIGHT2_THRESHOLD,
            "row_policy": args.row_policy,
            "selected_count": TARGET_SELECTED_COUNT,
            "seed_count": TARGET_SEED_COUNT,
            "sparse_policies": [item.strip() for item in args.sparse_policies.split(",") if item.strip()],
            "walk_mode": args.walk_mode,
            "width": args.width,
        },
        "schema": SCHEMA,
        "summary": summary,
        "trim10_payload": trim10_payload,
        "trim12_payload": trim12_payload,
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
    parser.add_argument("--p777-summary", type=Path, default=DEFAULT_P777_SUMMARY)
    parser.add_argument("--p778-summary", type=Path, default=DEFAULT_P778_SUMMARY)
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
    print(f"wrote {args.out}")
    print(f"wrote {summary_out}")
    print(
        json.dumps(
            {
                "aggregate_weight2_total_over_selected_rho": summary["summary"]["aggregate_cost"][
                    "aggregate_weight2_total_over_selected_rho"
                ],
                "claim_status": summary["claim_status"],
                "delta_counts": summary["summary"]["delta_counts"],
                "flagged_group_count": summary["summary"]["flagged_group_count"],
                "fresh_trim10_case_count": summary["summary"]["fresh_trim10_case_count"],
                "fresh_trim12_case_count": summary["summary"]["fresh_trim12_case_count"],
                "max_weight2": summary["summary"]["weight2_over_selected_rho_stats"]["max"],
                "missing_switch_candidate_count": summary["summary"]["missing_switch_candidate_count"],
                "missing_trim12_group_count": summary["summary"]["missing_trim12_group_count"],
                "public_sparse_selector_gap_count": summary["summary"]["public_sparse_selector_gap_count"],
                "recovery_ok_count": summary["summary"]["recovery_ok_count"],
                "selected_group_count": summary["summary"]["selected_group_count"],
                "strict_pass_count": summary["summary"]["strict_pass_count"],
                "switched_group_count": summary["summary"]["switched_group_count"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
