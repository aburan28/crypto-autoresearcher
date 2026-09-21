#!/usr/bin/env python3
"""P771 public selector over P769/P770 width-amortization arms."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P769_SUMMARY = STATE_DIR / "low_term_total2_p769_frozen_trim8_width_stress_summary.json"
DEFAULT_P770_SUMMARY = STATE_DIR / "low_term_total2_p770_width_amortization_cost_miss_sweep_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p771_public_width_amortization_selector_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p771_public_width_amortization_selector.md"
SCHEMA = "ecdlp.low_term_total2_p771_public_width_amortization_selector.v1"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def weight2_total(item: dict[str, Any]) -> float:
    return float(item["public_selector_sparse_policy"]["weight2_cost"]["total_unit_cost_over_selected_rho"])


def public_max_weight(item: dict[str, Any]) -> float:
    return float(item["public_selector_sparse_policy"].get("max_field_op_weight_below_selected_rho") or 0.0)


def factor_bucket(item: dict[str, Any]) -> str:
    return f"fb{int(item['factor_base_size'])}"


def group_key(item: dict[str, Any]) -> str:
    return f"{factor_bucket(item)}|{item['target']}"


def candidate_from_case(item: dict[str, Any], arm: str, source: str) -> dict[str, Any]:
    sparse = item["public_selector_sparse_policy"]
    support = item["selected_relation_support_stats"]
    candidate = {
        "active_column_count": support["active_column_count"],
        "arm": arm,
        "candidate_id": f"{factor_bucket(item)}_{arm}_{item['target']}",
        "case": item["case"],
        "exported_factor_count": item["selected_exported_factor_count"],
        "factor_base_size": item["factor_base_size"],
        "factor_bucket": factor_bucket(item),
        "failure_class": item["failure_class"],
        "group_key": group_key(item),
        "mismatch_count": sparse["mismatch_count"],
        "policy": sparse["policy"],
        "public_max_field_op_weight_below_selected_rho": public_max_weight(item),
        "public_weight2_total_over_selected_rho": weight2_total(item),
        "rank": sparse["rank"],
        "recovered_count": sparse["recovered_count"],
        "scanned_count": item["scanned_count"],
        "selected_count": item["selected_count"],
        "source": source,
        "target": item["target"],
    }
    candidate["capacity_ok"] = (
        int(candidate["exported_factor_count"]) == int(candidate["factor_base_size"])
        and int(candidate["active_column_count"]) == int(candidate["factor_base_size"])
    )
    candidate["recovery_ok"] = (
        int(candidate["rank"]) == int(candidate["factor_base_size"])
        and int(candidate["recovered_count"]) == int(candidate["selected_count"])
        and int(candidate["mismatch_count"]) == 0
    )
    candidate["strict_pass"] = candidate["failure_class"] == "pass"
    return candidate


def load_candidates(args: argparse.Namespace) -> dict[str, list[dict[str, Any]]]:
    groups: dict[str, list[dict[str, Any]]] = {}
    p769 = load_json(args.p769_summary)
    p770 = load_json(args.p770_summary)
    for item in p769["summary"]["case_summaries"]:
        if int(item["factor_base_size"]) not in {96, 112}:
            continue
        candidate = candidate_from_case(item, "s768", "p769")
        groups.setdefault(candidate["group_key"], []).append(candidate)
    for item in p770["summary"]["case_summaries"]:
        candidate = candidate_from_case(item, str(item["amortization_arm"]), "p770")
        groups.setdefault(candidate["group_key"], []).append(candidate)
    for candidates in groups.values():
        candidates.sort(key=lambda item: (item["arm"], item["candidate_id"]))
    return dict(sorted(groups.items()))


def select_candidate(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    return sorted(
        candidates,
        key=lambda item: (
            item["public_weight2_total_over_selected_rho"],
            -item["public_max_field_op_weight_below_selected_rho"],
            item["selected_count"],
            item["candidate_id"],
        ),
    )[0]


def fixed_baselines(groups: dict[str, list[dict[str, Any]]]) -> dict[str, dict[str, Any]]:
    baselines = {}
    for name, preferred_arm in (
        ("fixed_s768", "s768"),
        ("fixed_s896_with_s768_controls", "s896"),
        ("fixed_s1024_with_s768_controls", "s1024"),
    ):
        selected = []
        for candidates in groups.values():
            by_arm = {item["arm"]: item for item in candidates}
            selected.append(by_arm.get(preferred_arm) or by_arm["s768"])
        baselines[name] = summarize_candidates(selected)
    return baselines


def summarize_candidates(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    count = len(candidates)
    weights = [item["public_weight2_total_over_selected_rho"] for item in candidates]
    arm_counts = Counter(item["arm"] for item in candidates)
    return {
        "arm_counts": {key: arm_counts[key] for key in sorted(arm_counts)},
        "case_count": count,
        "capacity_ok_count": sum(1 for item in candidates if item["capacity_ok"]),
        "max_weight2": max(weights) if weights else None,
        "min_weight2": min(weights) if weights else None,
        "recovery_ok_count": sum(1 for item in candidates if item["recovery_ok"]),
        "strict_pass_count": sum(1 for item in candidates if item["strict_pass"]),
    }


def group_summaries(selected_groups: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for group in selected_groups:
        candidate = group["selected_candidate"]
        bucket_key = str(candidate[key])
        bucket = out.setdefault(
            bucket_key,
            {
                "case_count": 0,
                "capacity_ok_count": 0,
                "recovery_ok_count": 0,
                "selector_gap_count": 0,
                "strict_pass_count": 0,
            },
        )
        bucket["case_count"] += 1
        bucket["capacity_ok_count"] += int(candidate["capacity_ok"])
        bucket["recovery_ok_count"] += int(candidate["recovery_ok"])
        bucket["selector_gap_count"] += int(group["selector_gap"])
        bucket["strict_pass_count"] += int(candidate["strict_pass"])
    return out


def determine_claim(summary: dict[str, Any], args: argparse.Namespace) -> str:
    total = int(summary["group_count"])
    selected_pass = int(summary["selected_strict_pass_count"])
    recovery = int(summary["selected_recovery_ok_count"])
    gaps = int(summary["selector_gap_count"])
    capacity = int(summary["selected_capacity_ok_count"])
    best_fixed = int(summary["best_fixed_baseline_pass_count"])
    if total and selected_pass == total:
        return "P771_PUBLIC_WIDTH_AMORTIZATION_SELECTOR_ALL_CASE_SIGNAL"
    if (
        selected_pass >= int(args.primary_threshold)
        and recovery == total
        and capacity == total
        and gaps == 0
        and selected_pass > best_fixed
    ):
        return "P771_PUBLIC_WIDTH_AMORTIZATION_SELECTOR_PRIMARY_SIGNAL"
    if selected_pass > int(summary["fixed_baselines"]["fixed_s768"]["strict_pass_count"]) and recovery == total and gaps == 0:
        return "P771_PUBLIC_WIDTH_AMORTIZATION_SELECTOR_USEFUL_SIGNAL"
    if recovery == total and capacity == total:
        return "P771_PUBLIC_WIDTH_AMORTIZATION_SELECTOR_RECOVERY_OK_COST_NEGATIVE"
    if capacity < total:
        return "P771_PUBLIC_WIDTH_AMORTIZATION_SELECTOR_CAPACITY_REGRESSION"
    return "NEGATIVE_RESULT_P771_PUBLIC_WIDTH_AMORTIZATION_SELECTOR"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    groups = load_candidates(args)
    selected_groups = []
    for key, candidates in groups.items():
        selected = select_candidate(candidates)
        any_pass = any(item["strict_pass"] for item in candidates)
        best_public = min(item["public_weight2_total_over_selected_rho"] for item in candidates)
        best_oracle_pass = min(
            (item["public_weight2_total_over_selected_rho"] for item in candidates if item["strict_pass"]),
            default=None,
        )
        selected_groups.append(
            {
                "candidate_count": len(candidates),
                "candidates": candidates,
                "group_key": key,
                "has_oracle_pass": any_pass,
                "oracle_best_pass_weight2": best_oracle_pass,
                "public_best_weight2": best_public,
                "selected_candidate": selected,
                "selector_gap": bool(any_pass and not selected["strict_pass"]),
            }
        )
    selected = [group["selected_candidate"] for group in selected_groups]
    fixed = fixed_baselines(groups)
    best_fixed = max(item["strict_pass_count"] for item in fixed.values())
    unresolved = [
        group
        for group in selected_groups
        if not group["has_oracle_pass"]
    ]
    summary = {
        "best_fixed_baseline_pass_count": best_fixed,
        "fixed_baselines": fixed,
        "group_count": len(selected_groups),
        "selected_arm_summaries": group_summaries(selected_groups, "arm"),
        "selected_capacity_ok_count": sum(1 for item in selected if item["capacity_ok"]),
        "selected_factor_summaries": group_summaries(selected_groups, "factor_bucket"),
        "selected_groups": selected_groups,
        "selected_recovery_ok_count": sum(1 for item in selected if item["recovery_ok"]),
        "selected_strict_pass_count": sum(1 for item in selected if item["strict_pass"]),
        "selector_gap_count": sum(1 for group in selected_groups if group["selector_gap"]),
        "unresolved_group_count": len(unresolved),
        "unresolved_groups": [
            {
                "group_key": group["group_key"],
                "selected_candidate": group["selected_candidate"]["candidate_id"],
                "selected_weight2": group["selected_candidate"]["public_weight2_total_over_selected_rho"],
            }
            for group in unresolved
        ],
    }
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p769_summary": str(args.p769_summary),
            "p770_summary": str(args.p770_summary),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(summary, args),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "REPLAY-AUDIT: this selects among saved P769/P770 candidates and does not recollect relations.",
            "PUBLIC-SELECTION: selected-count choice uses public cost/rank/row features before verification.",
            "PRIVATE-VERIFY-ONLY: failure class, recovered count, and mismatches are used only after selection.",
            "FIXED-ARM-COMPARISON: s896/s1024 fixed baselines fall back to s768 for P769 passing controls that were not rerun in P770.",
            "NO DEPLOYED-CURVE CLAIM: no large-prime scaling or production-key relevance is implied.",
        ],
        "method": "p771_public_width_amortization_selector",
        "parameters": {
            "primary_threshold": args.primary_threshold,
            "selector": "min_public_weight2_then_public_margin_then_lower_selected_count",
        },
        "schema": SCHEMA,
        "summary": summary,
    }


def summary_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    slim_groups = []
    for group in payload["summary"]["selected_groups"]:
        selected = group["selected_candidate"]
        slim_groups.append(
            {
                "candidate_count": group["candidate_count"],
                "candidate_public_weight2": {
                    item["arm"]: item["public_weight2_total_over_selected_rho"]
                    for item in group["candidates"]
                },
                "candidate_strict_pass": {
                    item["arm"]: item["strict_pass"]
                    for item in group["candidates"]
                },
                "group_key": group["group_key"],
                "has_oracle_pass": group["has_oracle_pass"],
                "oracle_best_pass_weight2": group["oracle_best_pass_weight2"],
                "public_best_weight2": group["public_best_weight2"],
                "selected_arm": selected["arm"],
                "selected_capacity_ok": selected["capacity_ok"],
                "selected_candidate": selected["candidate_id"],
                "selected_factor_bucket": selected["factor_bucket"],
                "selected_policy": selected["policy"],
                "selected_recovery_ok": selected["recovery_ok"],
                "selected_strict_pass": selected["strict_pass"],
                "selected_target": selected["target"],
                "selected_weight2": selected["public_weight2_total_over_selected_rho"],
                "selector_gap": group["selector_gap"],
            }
        )
    summary = dict(payload["summary"])
    summary["selected_groups"] = slim_groups
    return {
        "schema": f"{SCHEMA}.summary",
        "artifacts": payload["artifacts"],
        "claim_status": payload["claim_status"],
        "created_at": payload["created_at"],
        "honesty_boundary": payload["honesty_boundary"],
        "method": payload["method"],
        "parameters": payload["parameters"],
        "summary": summary,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p769-summary", type=Path, default=DEFAULT_P769_SUMMARY)
    parser.add_argument("--p770-summary", type=Path, default=DEFAULT_P770_SUMMARY)
    parser.add_argument("--primary-threshold", type=int, default=13)
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
                "best_fixed_baseline_pass_count": summary["summary"]["best_fixed_baseline_pass_count"],
                "claim_status": summary["claim_status"],
                "fixed_baselines": summary["summary"]["fixed_baselines"],
                "selected_arm_summaries": summary["summary"]["selected_arm_summaries"],
                "selected_strict_pass_count": summary["summary"]["selected_strict_pass_count"],
                "selector_gap_count": summary["summary"]["selector_gap_count"],
                "unresolved_groups": summary["summary"]["unresolved_groups"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
