#!/usr/bin/env python3
"""P778 replay audit for a minimal public trim10 exception rule."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P774_PROBE = STATE_DIR / "low_term_total2_p774_public_budget_selector_all_groups_probe.json"
DEFAULT_P775_PROBE = STATE_DIR / "low_term_total2_p775_public_budget_selector_holdout_transfer_probe.json"
DEFAULT_P776_PROBE = STATE_DIR / "low_term_total2_p776_large_holdout_trim12_vs_selector_probe.json"
DEFAULT_P777_PROBE = STATE_DIR / "low_term_total2_p777_merged_trim12_factor_first_cost_audit_probe.json"
DEFAULT_P777_SUMMARY = STATE_DIR / "low_term_total2_p777_merged_trim12_factor_first_cost_audit_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p778_public_trim10_exception_rule_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p778_public_trim10_exception_rule.md"
SCHEMA = "ecdlp.low_term_total2_p778_public_trim10_exception_rule.v1"

TARGET_SELECTED_COUNT = 1024
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


def group_key(item: dict[str, Any]) -> str:
    return f"fb{int(item['factor_base_size'])}|{item['target']}"


def cost_for_weight(sparse: dict[str, Any], key: str = "costs_by_field_weight", weight: int = 2) -> dict[str, Any]:
    for cost in sparse.get(key) or []:
        if int(cost.get("field_op_weight") or 0) == weight:
            return cost
    return {}


def sparse(item: dict[str, Any]) -> dict[str, Any]:
    return item["public_selector_sparse_policy"]


def budget_delta_from_case(item: dict[str, Any]) -> int | None:
    name = str(item.get("case") or "")
    if "_dm12_" in name:
        return -12
    if "_dm10_" in name:
        return -10
    if "_dm8_" in name:
        return -8
    if "_dm6_" in name:
        return -6
    if "_dm4_" in name:
        return -4
    return None


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
        "factor_bucket": f"fb{int(item['factor_base_size'])}",
        "factor_base_size": item.get("factor_base_size"),
        "factor_first_field_ops": verified.get("sparse_factor_first_field_ops"),
        "failure_class": item.get("failure_class"),
        "generic_rho_steps": item.get("generic_rho_steps"),
        "group_key": group_key(item),
        "mismatch_count": substitution.get("mismatch_count"),
        "policy": sp.get("sparse_policy"),
        "public_safe_field_weight": sp.get("public_max_field_op_weight_below_selected_rho")
        or sp.get("max_field_op_weight_below_selected_rho"),
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


def cases_from_probe(path: Path, source: str) -> list[dict[str, Any]]:
    payload = load_json(path)
    cases = ((payload.get("p764_payload") or {}).get("summary") or {}).get("case_summaries") or []
    out = []
    for item in cases:
        if int(item.get("selected_count") or 0) != TARGET_SELECTED_COUNT:
            continue
        if int(item.get("factor_base_size") or 0) not in (96, 112):
            continue
        delta = budget_delta_from_case(item)
        if delta not in (TRIM12_DELTA, TRIM10_DELTA):
            continue
        out.append(slim_candidate(item, source))
    return out


def supplemental_cases_from_p777(path: Path) -> list[dict[str, Any]]:
    payload = load_json(path)
    cases = ((payload.get("p777_supplemental_payload") or {}).get("summary") or {}).get("case_summaries") or []
    return [slim_candidate(item, "p777_supplemental") for item in cases]


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


def determine_claim(summary: dict[str, Any]) -> str:
    total = int(summary["selected_group_count"])
    strict = int(summary["strict_pass_count"])
    recovery = int(summary["recovery_ok_count"])
    capacity = int(summary["capacity_ok_count"])
    selected = int(summary["selected_count_ok_count"])
    missing = int(summary["missing_switch_candidate_count"])
    aggregate_value = summary["aggregate_cost"]["aggregate_weight2_total_over_selected_rho"]
    max_weight = summary["weight2_over_selected_rho_stats"]["max"]
    if (
        total
        and strict == total
        and recovery == total
        and capacity == total
        and selected == total
        and missing == 0
        and aggregate_value is not None
        and float(aggregate_value) < 1.0
        and max_weight is not None
        and float(max_weight) < 1.0
    ):
        return "P778_PUBLIC_TRIM10_EXCEPTION_ALL_GROUP_SIGNAL"
    if (
        total
        and strict >= max(1, total - 1)
        and recovery == total
        and capacity == total
        and selected == total
        and missing == 0
        and aggregate_value is not None
        and float(aggregate_value) < 1.0
    ):
        return "P778_PUBLIC_TRIM10_EXCEPTION_USEFUL_SIGNAL"
    if missing:
        return "P778_PUBLIC_TRIM10_EXCEPTION_MISSING_SWITCH"
    if recovery == total and capacity == total:
        return "P778_PUBLIC_TRIM10_EXCEPTION_RECOVERY_OK_COST_NEGATIVE"
    return "NEGATIVE_RESULT_P778_PUBLIC_TRIM10_EXCEPTION_RULE"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p777_summary = load_json(args.p777_summary)
    p777_aggregate = ((p777_summary.get("summary") or {}).get("aggregate_cost")) or {}
    p777_weight2 = p777_aggregate.get("aggregate_weight2_total_over_selected_rho")
    candidates: dict[tuple[str, int], dict[str, Any]] = {}
    for source, path in {
        "p774": args.p774_probe,
        "p775": args.p775_probe,
        "p776": args.p776_probe,
    }.items():
        for item in cases_from_probe(path, source):
            candidates[(item["group_key"], int(item["budget_delta"]))] = item
    for item in supplemental_cases_from_p777(args.p777_probe):
        candidates[(item["group_key"], int(item["budget_delta"]))] = item
    base_groups = sorted({item["group_key"] for item in (p777_summary.get("summary") or {}).get("normalized_cases") or []})
    selected_cases = []
    flagged_groups = []
    missing_switches = []
    for group in base_groups:
        trim12 = candidates.get((group, TRIM12_DELTA))
        if not trim12:
            missing_switches.append({"group_key": group, "missing": "trim12"})
            continue
        flag = float(trim12["public_weight2_over_selected_rho"]) >= PUBLIC_WEIGHT2_THRESHOLD
        if flag:
            flagged_groups.append(
                {
                    "group_key": group,
                    "public_weight2_over_selected_rho": trim12["public_weight2_over_selected_rho"],
                    "trim12_case": trim12["case"],
                }
            )
            chosen = candidates.get((group, TRIM10_DELTA))
            if not chosen:
                missing_switches.append({"group_key": group, "missing": "trim10"})
                chosen = trim12
        else:
            chosen = trim12
        chosen = dict(chosen)
        chosen["exception_flag"] = flag
        chosen["rule_selected_delta"] = int(chosen["budget_delta"])
        selected_cases.append(chosen)
    selected_cases = sorted(selected_cases, key=lambda item: item["group_key"])
    weights = [
        float(item["weight2_over_selected_rho"])
        for item in selected_cases
        if item.get("weight2_over_selected_rho") is not None
    ]
    aggregate_cost = aggregate(selected_cases)
    improvement = None
    if p777_weight2 is not None and aggregate_cost["aggregate_weight2_total_over_selected_rho"] is not None:
        improvement = round(float(p777_weight2) - float(aggregate_cost["aggregate_weight2_total_over_selected_rho"]), 8)
    delta_counts = Counter(str(item["rule_selected_delta"]) for item in selected_cases)
    summary = {
        "aggregate_cost": aggregate_cost,
        "baseline_p777_aggregate_weight2_total_over_selected_rho": p777_weight2,
        "capacity_ok_count": sum(1 for item in selected_cases if item["capacity_ok"]),
        "delta_counts": {key: delta_counts[key] for key in sorted(delta_counts, key=lambda value: int(value))},
        "factor_summaries": bucket_counts(selected_cases, "factor_bucket"),
        "flagged_group_count": len(flagged_groups),
        "flagged_groups": flagged_groups,
        "missing_switch_candidate_count": len(missing_switches),
        "missing_switch_candidates": missing_switches,
        "public_threshold": PUBLIC_WEIGHT2_THRESHOLD,
        "p777_aggregate_improvement": improvement,
        "recovery_ok_count": sum(1 for item in selected_cases if item["recovery_ok"]),
        "selected_cases": selected_cases,
        "selected_count_ok_count": sum(1 for item in selected_cases if item["selected_count_ok"]),
        "selected_group_count": len(selected_cases),
        "source_summaries": bucket_counts(selected_cases, "source"),
        "strict_pass_count": sum(1 for item in selected_cases if item["strict_pass"]),
        "switched_group_count": sum(1 for item in selected_cases if item["rule_selected_delta"] == TRIM10_DELTA),
        "target_summaries": bucket_counts(selected_cases, "target"),
        "weight2_over_selected_rho_stats": stat(weights),
    }
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p774_probe": str(args.p774_probe),
            "p775_probe": str(args.p775_probe),
            "p776_probe": str(args.p776_probe),
            "p777_probe": str(args.p777_probe),
            "p777_summary": str(args.p777_summary),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(summary),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "REPLAY-AUDIT: P778 selects among existing P774/P775/P776/P777 candidate artifacts; no new relation collection is performed.",
            "PUBLIC-THRESHOLD: switch rule depends only on public trim12 weight-2 estimate before recovery verification.",
            "PRIVATE-VERIFY-ONLY: expected secrets are used only in source artifacts after public sparse-policy selection to verify recovery and mismatches.",
            "FACTOR-FIRST-CHARGED: cost includes scanned candidate group additions plus sparse factor-first solve and substitution field operations at weight 2.",
            "NO DEPLOYED-CURVE CLAIM: no large-prime scaling, target descent, or production-key relevance is implied.",
        ],
        "method": "p778_public_trim10_exception_rule",
        "parameters": {
            "default_delta": TRIM12_DELTA,
            "exception_delta": TRIM10_DELTA,
            "public_weight2_threshold": PUBLIC_WEIGHT2_THRESHOLD,
            "selected_count": TARGET_SELECTED_COUNT,
        },
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
    parser.add_argument("--p774-probe", type=Path, default=DEFAULT_P774_PROBE)
    parser.add_argument("--p775-probe", type=Path, default=DEFAULT_P775_PROBE)
    parser.add_argument("--p776-probe", type=Path, default=DEFAULT_P776_PROBE)
    parser.add_argument("--p777-probe", type=Path, default=DEFAULT_P777_PROBE)
    parser.add_argument("--p777-summary", type=Path, default=DEFAULT_P777_SUMMARY)
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
                "aggregate_weight2_total_over_selected_rho": summary["summary"]["aggregate_cost"]["aggregate_weight2_total_over_selected_rho"],
                "claim_status": summary["claim_status"],
                "delta_counts": summary["summary"]["delta_counts"],
                "flagged_group_count": summary["summary"]["flagged_group_count"],
                "max_weight2": summary["summary"]["weight2_over_selected_rho_stats"]["max"],
                "missing_switch_candidate_count": summary["summary"]["missing_switch_candidate_count"],
                "p777_aggregate_improvement": summary["summary"]["p777_aggregate_improvement"],
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
