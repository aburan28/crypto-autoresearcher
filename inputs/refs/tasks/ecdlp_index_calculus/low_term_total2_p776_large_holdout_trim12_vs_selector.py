#!/usr/bin/env python3
"""P776 large holdout comparison: frozen trim12 vs public budget selector."""

from __future__ import annotations

import argparse
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P775_SCRIPT = TASK_DIR / "low_term_total2_p775_public_budget_selector_holdout_transfer.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_FRONTIER = STATE_DIR / "frontier_targets.json"
DEFAULT_P763_SUMMARY = STATE_DIR / "low_term_total2_p763_factor_base_limit_extension_smoke_summary.json"
DEFAULT_P774_SUMMARY = STATE_DIR / "low_term_total2_p774_public_budget_selector_all_groups_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p776_large_holdout_trim12_vs_selector_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p776_large_holdout_trim12_vs_selector.md"
SCHEMA = "ecdlp.low_term_total2_p776_large_holdout_trim12_vs_selector.v1"

HOLDOUT_TARGETS = [
    "67.a1@9151",
    "114224.v1@9421",
    "23232.cr1@8431",
    "67.a1@9377",
    "21175.bc1@8219",
    "114224.v1@9649",
    "23232.cr1@9277",
]
BASE_BUDGETS = {
    "67.a1@9151": 64,
    "114224.v1@9421": 64,
    "23232.cr1@8431": 60,
    "67.a1@9377": 64,
    "21175.bc1@8219": 58,
    "114224.v1@9649": 64,
    "23232.cr1@9277": 64,
}
TARGET_TAGS = {
    "67.a1@9151": "67a9151",
    "114224.v1@9421": "114224v9421",
    "23232.cr1@8431": "23232c8431",
    "67.a1@9377": "67a9377",
    "21175.bc1@8219": "21175b8219",
    "114224.v1@9649": "114224v9649",
    "23232.cr1@9277": "23232c9277",
}
PRIOR_TARGETS = {
    "114224.v1@9341",
    "21175.bc1@8089",
    "22050.cf1@10531",
    "23232.cr1@8467",
    "23232.cr1@9643",
    "67.a1@11923",
    "67.a1@9803",
    "67.a1@9829",
    "114224.v1@9613",
    "21175.bc1@8467",
    "22050.cf1@10321",
}
FROZEN_DELTA = -12


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


def configure_p775(p775: Any) -> None:
    p775.HOLDOUT_TARGETS = list(HOLDOUT_TARGETS)
    p775.BASE_BUDGETS = dict(BASE_BUDGETS)
    p775.TARGET_TAGS = dict(TARGET_TAGS)
    p775.P774_CALIBRATION_TARGETS = set(PRIOR_TARGETS)
    p775.DEFAULT_CONTRACT = DEFAULT_CONTRACT
    p775.DEFAULT_OUT = DEFAULT_OUT


def case_by_group_delta(p775: Any, payload: dict[str, Any]) -> dict[str, dict[int, dict[str, Any]]]:
    out: dict[str, dict[int, dict[str, Any]]] = {}
    cases = ((payload.get("p764_payload") or {}).get("summary") or {}).get("case_summaries") or []
    for item in cases:
        out.setdefault(p775.group_key(item), {})[p775.budget_delta(item)] = item
    return out


def compare_trim12(p775: Any, payload: dict[str, Any]) -> dict[str, Any]:
    groups = payload["summary"]["selected_groups"]
    by_group = case_by_group_delta(p775, payload)
    comparisons = []
    selector_strict_not_trim12 = 0
    trim12_strict_not_selector = 0
    selector_weight2_better = 0
    trim12_weight2_better = 0
    same_budget_count = 0
    both_strict = 0
    both_fail = 0
    for group in groups:
        key = group["group_key"]
        selected = group["selected_candidate"]
        trim12_raw = by_group[key][FROZEN_DELTA]
        trim12 = p775.slim_candidate(trim12_raw)
        selected_w = selected["verified_weight2"]
        trim12_w = trim12["verified_weight2"]
        selected_strict = bool(selected["strict_pass"])
        trim12_strict = bool(trim12["strict_pass"])
        selector_strict_not_trim12 += int(selected_strict and not trim12_strict)
        trim12_strict_not_selector += int(trim12_strict and not selected_strict)
        both_strict += int(selected_strict and trim12_strict)
        both_fail += int((not selected_strict) and (not trim12_strict))
        same_budget_count += int(int(selected["budget_delta"]) == FROZEN_DELTA)
        selector_weight2_better += int(
            selected_w is not None and trim12_w is not None and float(selected_w) < float(trim12_w)
        )
        trim12_weight2_better += int(
            selected_w is not None and trim12_w is not None and float(trim12_w) < float(selected_w)
        )
        comparisons.append(
            {
                "group_key": key,
                "selector_budget_delta": selected["budget_delta"],
                "selector_policy": selected["public_policy"],
                "selector_strict_pass": selected_strict,
                "selector_verified_weight2": selected_w,
                "target": selected["target"],
                "trim12_policy": trim12["public_policy"],
                "trim12_strict_pass": trim12_strict,
                "trim12_verified_weight2": trim12_w,
                "weight2_delta_selector_minus_trim12": round(float(selected_w) - float(trim12_w), 8)
                if selected_w is not None and trim12_w is not None
                else None,
            }
        )
    return {
        "both_fail_count": both_fail,
        "both_strict_pass_count": both_strict,
        "comparison_groups": comparisons,
        "frozen_delta": FROZEN_DELTA,
        "same_budget_count": same_budget_count,
        "selector_strict_not_trim12_count": selector_strict_not_trim12,
        "selector_weight2_better_count": selector_weight2_better,
        "trim12_strict_not_selector_count": trim12_strict_not_selector,
        "trim12_weight2_better_count": trim12_weight2_better,
    }


def determine_claim(summary: dict[str, Any], comparison: dict[str, Any]) -> str:
    total = int(summary["group_count"])
    selected_pass = int(summary["selected_strict_pass_count"])
    recovery = int(summary["selected_recovery_ok_count"])
    capacity = int(summary["selected_capacity_ok_count"])
    sparse_gaps = int(summary["candidate_sparse_selector_gap_count"])
    budget_gaps = int(summary["budget_selector_gap_count"])
    trim12_pass = int((summary["budget_delta_baselines"].get("delta_-12") or {}).get("strict_pass_count") or 0)
    if (
        selected_pass == total
        and trim12_pass == total
        and recovery == total
        and capacity == total
        and sparse_gaps == 0
        and budget_gaps == 0
    ):
        return "P776_SELECTOR_CLEAN_BUT_TRIM12_FULL_HOLDOUT_SIGNAL"
    if (
        selected_pass == total
        and trim12_pass < total
        and recovery == total
        and capacity == total
        and sparse_gaps == 0
        and budget_gaps == 0
    ):
        return "P776_PUBLIC_SELECTOR_BEATS_TRIM12_HOLDOUT_SIGNAL"
    if trim12_pass == total and selected_pass < total:
        return "P776_FROZEN_TRIM12_BEATS_SELECTOR_REGRESSION"
    if budget_gaps:
        return "P776_PUBLIC_SELECTOR_BUDGET_GAP"
    if sparse_gaps:
        return "P776_PUBLIC_SELECTOR_SPARSE_GAP"
    if selected_pass >= max(1, total - 1) and recovery == total and capacity == total:
        return "P776_LARGE_HOLDOUT_USEFUL_SIGNAL"
    if recovery == total:
        return "P776_LARGE_HOLDOUT_RECOVERY_OK_COST_NEGATIVE"
    return "NEGATIVE_RESULT_P776_LARGE_HOLDOUT_TRIM12_VS_SELECTOR"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p775 = load_module("ecdlp_p775_for_p776", P775_SCRIPT)
    configure_p775(p775)
    p775_args = argparse.Namespace(
        budget_deltas=args.budget_deltas,
        cases=args.cases,
        field_weights=args.field_weights,
        frontier_targets=args.frontier_targets,
        max_relations=args.max_relations,
        max_subsets=args.max_subsets,
        p763_summary=args.p763_summary,
        p774_summary=args.p774_summary,
        public_substitution_ops_per_selected=args.public_substitution_ops_per_selected,
        row_policy=args.row_policy,
        sparse_policies=args.sparse_policies,
        walk_mode=args.walk_mode,
        width=args.width,
    )
    payload = p775.analyze(p775_args)
    comparison = compare_trim12(p775, payload)
    payload["artifacts"]["contract"] = str(DEFAULT_CONTRACT)
    payload["artifacts"]["script"] = str(Path(__file__))
    payload["claim_status"] = determine_claim(payload["summary"], comparison)
    payload["created_at"] = now_iso()
    payload["honesty_boundary"] = [
        "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
        "LARGE-HOLDOUT: targets are remaining non-precomputed frontier candidates outside P772/P774 and P775 sets.",
        "PUBLIC-SELECTION: sparse policy and budget candidate are selected from public cost features before substitution verification.",
        "FROZEN-TRIM12-BASELINE: selector value is judged against a public fixed delta -12 rule.",
        "PRIVATE-VERIFY-ONLY: expected secrets are used only after public selection to verify recovery and mismatches.",
        "SCANNED-POOL-CHARGED: replacement policies pay group cost for all scanned candidate rows.",
        "SPARSE-WEIGHT MODEL: field-operation weights are accounting stress tests, not calibrated hardware timings.",
        "NO DEPLOYED-CURVE CLAIM: no large-prime scaling or production-key relevance is implied.",
    ]
    payload["method"] = "p776_large_holdout_trim12_vs_selector"
    payload["parameters"]["base_budget_rationale"] = (
        "public schedule matched to nearest prior P774/P775 target/order rho bands before verification"
    )
    payload["parameters"]["frozen_delta"] = FROZEN_DELTA
    payload["parameters"]["prior_excluded_targets"] = sorted(PRIOR_TARGETS)
    payload["schema"] = SCHEMA
    payload["summary"]["trim12_comparison"] = comparison
    return payload


def summary_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": f"{SCHEMA}.summary",
        "artifacts": payload["artifacts"],
        "claim_status": payload["claim_status"],
        "created_at": payload["created_at"],
        "honesty_boundary": payload["honesty_boundary"],
        "method": payload["method"],
        "p774_control": payload["p774_control"],
        "parameters": payload["parameters"],
        "summary": payload["summary"],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--budget-deltas", default="-12,-10,-8,-6")
    parser.add_argument("--cases", default="")
    parser.add_argument("--frontier-targets", type=Path, default=DEFAULT_FRONTIER)
    parser.add_argument("--p763-summary", type=Path, default=DEFAULT_P763_SUMMARY)
    parser.add_argument("--p774-summary", type=Path, default=DEFAULT_P774_SUMMARY)
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
    trim12 = summary["summary"]["budget_delta_baselines"]["delta_-12"]
    comparison = summary["summary"]["trim12_comparison"]
    print(f"wrote {args.out}")
    print(f"wrote {summary_out}")
    print(
        json.dumps(
            {
                "budget_selector_gap_count": summary["summary"]["budget_selector_gap_count"],
                "candidate_case_count": summary["summary"]["candidate_case_count"],
                "candidate_sparse_selector_gap_count": summary["summary"]["candidate_sparse_selector_gap_count"],
                "claim_status": summary["claim_status"],
                "group_count": summary["summary"]["group_count"],
                "selected_delta_counts": summary["summary"]["selected_delta_counts"],
                "selected_strict_pass_count": summary["summary"]["selected_strict_pass_count"],
                "selected_weight2_max": summary["summary"]["selected_weight2_max"],
                "selected_weight2_min": summary["summary"]["selected_weight2_min"],
                "selector_strict_not_trim12_count": comparison["selector_strict_not_trim12_count"],
                "selector_weight2_better_count": comparison["selector_weight2_better_count"],
                "trim12_strict_pass_count": trim12["strict_pass_count"],
                "trim12_strict_not_selector_count": comparison["trim12_strict_not_selector_count"],
                "unresolved_selected_groups": summary["summary"]["unresolved_selected_groups"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
