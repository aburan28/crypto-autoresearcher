#!/usr/bin/env python3
"""P766 targeted public budget-trim sweep for widened factor bases."""

from __future__ import annotations

import argparse
import importlib.util
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P765_SCRIPT = TASK_DIR / "low_term_total2_p765_widened_amortization_trim_validation.py"
P764_SCRIPT = TASK_DIR / "low_term_total2_p764_widened_factor_basis_cost_validation.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P765_SUMMARY = STATE_DIR / "low_term_total2_p765_widened_amortization_trim_validation_summary.json"
DEFAULT_P764_SUMMARY = STATE_DIR / "low_term_total2_p764_widened_factor_basis_cost_validation_summary.json"
DEFAULT_P763_SUMMARY = STATE_DIR / "low_term_total2_p763_factor_base_limit_extension_smoke_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p766_targeted_public_trim_sweep_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p766_targeted_public_trim_sweep.md"
SCHEMA = "ecdlp.low_term_total2_p766_targeted_public_trim_sweep.v1"


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


def previous_trim_control(path: Path) -> dict[str, Any]:
    payload = load_json(path)
    summary = payload.get("summary") or {}
    trim = (summary.get("variant_summaries") or {}).get("s768_trim4") or {}
    return {
        "claim_status": payload.get("claim_status"),
        "s768_trim4_case_count": trim.get("case_count"),
        "s768_trim4_strict_pass_count": trim.get("strict_pass_count"),
        "strict_pass_case_count": summary.get("strict_pass_case_count"),
    }


def class_counts(case_summaries: list[dict[str, Any]]) -> dict[str, int]:
    counts = Counter(str(item["failure_class"]) for item in case_summaries)
    return {key: counts[key] for key in sorted(counts)}


def group_summaries(case_summaries: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for item in case_summaries:
        group = str(item[key])
        bucket = out.setdefault(
            group,
            {
                "case_count": 0,
                "failure_classes": {},
                "oracle_best_pass_count": 0,
                "public_selector_gap_count": 0,
                "public_selector_pass_count": 0,
                "public_selector_recovery_ok_count": 0,
                "strict_pass_count": 0,
            },
        )
        bucket["case_count"] += 1
        bucket["oracle_best_pass_count"] += int(bool(item["oracle_best_pass_weight2_below_rho"]))
        bucket["public_selector_gap_count"] += int(
            bool(item["oracle_best_pass_weight2_below_rho"] and not item["public_selector_pass_weight2_below_rho"])
        )
        bucket["public_selector_pass_count"] += int(bool(item["public_selector_pass_weight2_below_rho"]))
        bucket["public_selector_recovery_ok_count"] += int(bool(item["public_selector_recovery_ok"]))
        bucket["strict_pass_count"] += int(item["failure_class"] == "pass")
        failures = bucket["failure_classes"]
        failures[item["failure_class"]] = failures.get(item["failure_class"], 0) + 1
    return out


def determine_claim(case_summaries: list[dict[str, Any]], args: argparse.Namespace, prior: dict[str, Any]) -> str:
    total = len(case_summaries)
    strict = sum(1 for item in case_summaries if item["failure_class"] == "pass")
    recovery_ok = sum(1 for item in case_summaries if item["public_selector_recovery_ok"])
    gaps = sum(1 for item in case_summaries if item["failure_class"] == "selector_gap")
    capacity = sum(1 for item in case_summaries if item["failure_class"] == "capacity_or_support_failure")
    factor_min = min((summary["strict_pass_count"] for summary in group_summaries(case_summaries, "factor_bucket").values()), default=0)
    trim_best = max((summary["strict_pass_count"] for summary in group_summaries(case_summaries, "variant").values()), default=0)
    prior_trim_pass = int(prior.get("s768_trim4_strict_pass_count") or 0)
    prior_trim_count = int(prior.get("s768_trim4_case_count") or 1)
    improved_trim = trim_best * prior_trim_count > prior_trim_pass * 6
    if total and strict == total:
        return "P766_TARGETED_PUBLIC_TRIM_ALL_CASE_SIGNAL"
    if (
        strict >= int(args.primary_threshold)
        and factor_min >= int(args.factor_threshold)
        and recovery_ok == total
        and gaps == 0
        and capacity == 0
    ):
        return "P766_TARGETED_PUBLIC_TRIM_PRIMARY_SIGNAL"
    if improved_trim and recovery_ok == total and gaps <= 1 and capacity == 0:
        return "P766_TARGETED_PUBLIC_TRIM_IMPROVEMENT_SIGNAL"
    if recovery_ok == total and capacity == 0:
        return "P766_TARGETED_PUBLIC_TRIM_RECOVERY_OK_COST_NEGATIVE"
    if capacity:
        return "P766_TARGETED_PUBLIC_TRIM_CAPACITY_REGRESSION"
    return "NEGATIVE_RESULT_P766_TARGETED_PUBLIC_TRIM_SWEEP"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p765 = load_module("ecdlp_p765_widened_amortization_trim_validation", P765_SCRIPT)
    p764 = load_module("ecdlp_p764_for_p766_summary", P764_SCRIPT)
    p765_args = argparse.Namespace(
        arm_threshold=args.arm_threshold,
        cases=args.cases,
        factor_threshold=args.factor_threshold,
        field_weights=args.field_weights,
        max_relations=args.max_relations,
        max_subsets=args.max_subsets,
        p763_summary=args.p763_summary,
        p764_summary=args.p764_summary,
        primary_threshold=args.primary_threshold,
        public_substitution_ops_per_selected=args.public_substitution_ops_per_selected,
        row_policy=args.row_policy,
        sparse_policies=args.sparse_policies,
        walk_mode=args.walk_mode,
        width=args.width,
    )
    p765_payload = p765.analyze(p765_args)
    case_summaries = p765_payload["summary"]["case_summaries"]
    prior = previous_trim_control(args.p765_summary)
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p763_summary": str(args.p763_summary),
            "p764_summary": str(args.p764_summary),
            "p765_summary": str(args.p765_summary),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(case_summaries, args, prior),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "WIDENED-FACTOR-BASIS: P763 factor-base-limit propagation is active; requested fb64/fb80 must be exported.",
            "PUBLIC-SELECTION: sparse policy is selected from public full-rank solve cost before substitution verification.",
            "PRIVATE-VERIFY-ONLY: expected secrets are used only after public policy selection to verify recovery and mismatches.",
            "SCANNED-POOL-CHARGED: replacement policies pay group cost for all scanned candidate rows.",
            "SPARSE-WEIGHT MODEL: field-operation weights are accounting stress tests, not calibrated hardware timings.",
            "NO DEPLOYED-CURVE CLAIM: no large-prime scaling or production-key relevance is implied.",
        ],
        "method": "p766_targeted_public_trim_sweep",
        "p765_control": prior,
        "parameters": p765_payload["parameters"],
        "schema": SCHEMA,
        "summary": {
            "arm_summaries": group_summaries(case_summaries, "arm"),
            "case_count": len(case_summaries),
            "case_summaries": case_summaries,
            "class_counts": class_counts(case_summaries),
            "factor_summaries": group_summaries(case_summaries, "factor_bucket"),
            "oracle_best_pass_count": sum(1 for item in case_summaries if item["oracle_best_pass_weight2_below_rho"]),
            "public_selector_gap_count": sum(1 for item in case_summaries if item["failure_class"] == "selector_gap"),
            "public_selector_pass_count": sum(1 for item in case_summaries if item["public_selector_pass_weight2_below_rho"]),
            "public_selector_recovery_ok_count": sum(1 for item in case_summaries if item["public_selector_recovery_ok"]),
            "strict_pass_case_count": sum(1 for item in case_summaries if item["failure_class"] == "pass"),
            "variant_summaries": group_summaries(case_summaries, "variant"),
        },
    }


def summary_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    p764 = load_module("ecdlp_p764_summary_for_p766", P764_SCRIPT)
    return {
        "schema": f"{SCHEMA}.summary",
        "artifacts": payload["artifacts"],
        "claim_status": payload["claim_status"],
        "created_at": payload["created_at"],
        "honesty_boundary": payload["honesty_boundary"],
        "method": payload["method"],
        "p765_control": payload["p765_control"],
        "parameters": payload["parameters"],
        "summary": {
            "arm_summaries": payload["summary"]["arm_summaries"],
            "case_count": payload["summary"]["case_count"],
            "case_summaries": [
                dict(
                    p764.slim_case(item),
                    base_budget=item.get("base_budget"),
                    budget_delta=item.get("budget_delta"),
                    factor_bucket=item.get("factor_bucket"),
                    variant=item.get("variant"),
                )
                for item in payload["summary"]["case_summaries"]
            ],
            "class_counts": payload["summary"]["class_counts"],
            "factor_summaries": payload["summary"]["factor_summaries"],
            "oracle_best_pass_count": payload["summary"]["oracle_best_pass_count"],
            "public_selector_gap_count": payload["summary"]["public_selector_gap_count"],
            "public_selector_pass_count": payload["summary"]["public_selector_pass_count"],
            "public_selector_recovery_ok_count": payload["summary"]["public_selector_recovery_ok_count"],
            "strict_pass_case_count": payload["summary"]["strict_pass_case_count"],
            "variant_summaries": payload["summary"]["variant_summaries"],
        },
    }


def default_cases() -> str:
    targets = [
        ("67.a1@9803", 66, "67"),
        ("21175.bc1@8089", 58, "21175"),
        ("23232.cr1@9643", 64, "23232b"),
    ]
    variants = [
        ("trim4", 768, 896, 896, -4),
        ("trim6", 768, 896, 896, -6),
        ("trim8", 768, 896, 896, -8),
    ]
    entries = []
    for factor_base_size in (64, 80):
        for variant, selected, seed_count, pool_count, budget_delta in variants:
            for target, budget, tag in targets:
                actual_budget = max(1, budget + budget_delta)
                entries.append(
                    f"fb{factor_base_size}_{variant}_{tag}|{target}|{actual_budget}|{factor_base_size}|{selected}|{seed_count}|{pool_count}|ecdlp-p766-fb{factor_base_size}-{variant}-{tag}-v1|fb{factor_base_size}_{variant}"
                )
    return ",".join(entries)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", default=default_cases())
    parser.add_argument("--p763-summary", type=Path, default=DEFAULT_P763_SUMMARY)
    parser.add_argument("--p764-summary", type=Path, default=DEFAULT_P764_SUMMARY)
    parser.add_argument("--p765-summary", type=Path, default=DEFAULT_P765_SUMMARY)
    parser.add_argument("--row-policy", default="sequential_min_forms_ge_1")
    parser.add_argument("--sparse-policies", default="natural,support_asc,support_span_asc,pivot_low,pivot_high,coefficient_weight_asc")
    parser.add_argument("--width", type=int, default=2)
    parser.add_argument("--walk-mode", default="hash6")
    parser.add_argument("--max-relations", type=int, default=96)
    parser.add_argument("--max-subsets", type=int, default=25000)
    parser.add_argument("--field-weights", default="1,2")
    parser.add_argument("--public-substitution-ops-per-selected", type=int, default=6)
    parser.add_argument("--primary-threshold", type=int, default=15)
    parser.add_argument("--factor-threshold", type=int, default=7)
    parser.add_argument("--arm-threshold", type=int, default=2)
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
                "class_counts": summary["summary"]["class_counts"],
                "factor_summaries": summary["summary"]["factor_summaries"],
                "public_selector_gap_count": summary["summary"]["public_selector_gap_count"],
                "public_selector_pass_count": summary["summary"]["public_selector_pass_count"],
                "public_selector_recovery_ok_count": summary["summary"]["public_selector_recovery_ok_count"],
                "strict_pass_case_count": summary["summary"]["strict_pass_case_count"],
                "variant_summaries": summary["summary"]["variant_summaries"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
