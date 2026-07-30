#!/usr/bin/env python3
"""P767 disjoint-seed target-extension holdout for widened public trims."""

from __future__ import annotations

import argparse
import importlib.util
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P764_SCRIPT = TASK_DIR / "low_term_total2_p764_widened_factor_basis_cost_validation.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P766_SUMMARY = STATE_DIR / "low_term_total2_p766_targeted_public_trim_sweep_summary.json"
DEFAULT_P763_SUMMARY = STATE_DIR / "low_term_total2_p763_factor_base_limit_extension_smoke_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p767_disjoint_seed_target_extension_holdout_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p767_disjoint_seed_target_extension_holdout.md"
SCHEMA = "ecdlp.low_term_total2_p767_disjoint_seed_target_extension_holdout.v1"


BASE_BUDGETS = {
    "67.a1@9803": 66,
    "21175.bc1@8089": 58,
    "23232.cr1@9643": 64,
    "22050.cf1@10531": 66,
    "114224.v1@9341": 64,
}
EXTENSION_TARGETS = {"22050.cf1@10531", "114224.v1@9341"}


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


def p766_control(path: Path) -> dict[str, Any]:
    payload = load_json(path)
    summary = payload.get("summary") or {}
    return {
        "case_count": summary.get("case_count"),
        "claim_status": payload.get("claim_status"),
        "public_selector_gap_count": summary.get("public_selector_gap_count"),
        "public_selector_pass_count": summary.get("public_selector_pass_count"),
        "public_selector_recovery_ok_count": summary.get("public_selector_recovery_ok_count"),
        "strict_pass_case_count": summary.get("strict_pass_case_count"),
    }


def case_metadata(cases: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    out = {}
    for case in cases:
        target = str(case["target"])
        arm = str(case["arm"])
        parts = arm.split("_", 1)
        variant = parts[1] if len(parts) == 2 else arm
        base_budget = BASE_BUDGETS.get(target, int(case["budget"]))
        out[case["label"]] = {
            "base_budget": base_budget,
            "budget_delta": int(case["budget"]) - int(base_budget),
            "factor_bucket": f"fb{case['factor_base_size']}",
            "target_role": "extension" if target in EXTENSION_TARGETS else "original",
            "variant": variant,
        }
    return out


def add_metadata(case_summaries: list[dict[str, Any]], metadata: dict[str, dict[str, Any]]) -> None:
    for item in case_summaries:
        item.update(metadata.get(str(item["case"]), {}))


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


def class_counts(case_summaries: list[dict[str, Any]]) -> dict[str, int]:
    counts = Counter(str(item["failure_class"]) for item in case_summaries)
    return {key: counts[key] for key in sorted(counts)}


def target_factor_coverage(case_summaries: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    out: dict[str, dict[str, int]] = {}
    for item in case_summaries:
        target = str(item["target"])
        factor = str(item["factor_bucket"])
        bucket = out.setdefault(target, {})
        bucket[factor] = bucket.get(factor, 0) + int(item["failure_class"] == "pass")
    return out


def determine_claim(case_summaries: list[dict[str, Any]], args: argparse.Namespace) -> str:
    total = len(case_summaries)
    strict = sum(1 for item in case_summaries if item["failure_class"] == "pass")
    recovery_ok = sum(1 for item in case_summaries if item["public_selector_recovery_ok"])
    gaps = sum(1 for item in case_summaries if item["failure_class"] == "selector_gap")
    capacity = sum(1 for item in case_summaries if item["failure_class"] == "capacity_or_support_failure")
    extension = [item for item in case_summaries if item.get("target_role") == "extension"]
    extension_pass = sum(1 for item in extension if item["failure_class"] == "pass")
    coverage = target_factor_coverage(case_summaries)
    target_factor_ok = all(
        counts.get("fb64", 0) > 0 and counts.get("fb80", 0) > 0
        for counts in coverage.values()
    )
    if total and strict == total:
        return "P767_DISJOINT_TARGET_EXTENSION_ALL_CASE_SIGNAL"
    if (
        strict >= int(args.primary_threshold)
        and extension_pass >= int(args.extension_threshold)
        and recovery_ok == total
        and gaps == 0
        and capacity == 0
    ):
        return "P767_DISJOINT_TARGET_EXTENSION_PRIMARY_SIGNAL"
    if strict / max(1, total) > 0.70 and target_factor_ok and recovery_ok == total and capacity == 0:
        return "P767_DISJOINT_TARGET_EXTENSION_USEFUL_HOLDOUT_SIGNAL"
    if recovery_ok == total and capacity == 0:
        return "P767_DISJOINT_TARGET_EXTENSION_RECOVERY_OK_COST_NEGATIVE"
    if capacity:
        return "P767_DISJOINT_TARGET_EXTENSION_CAPACITY_REGRESSION"
    return "NEGATIVE_RESULT_P767_DISJOINT_TARGET_EXTENSION_HOLDOUT"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p764 = load_module("ecdlp_p764_widened_factor_basis_cost_validation", P764_SCRIPT)
    cases = p764.parse_cases(args.cases)
    p764_args = argparse.Namespace(
        arm_threshold=args.arm_threshold,
        cases=args.cases,
        field_weights=args.field_weights,
        max_relations=args.max_relations,
        max_subsets=args.max_subsets,
        p763_summary=args.p763_summary,
        primary_threshold=args.primary_threshold,
        public_substitution_ops_per_selected=args.public_substitution_ops_per_selected,
        row_policy=args.row_policy,
        sparse_policies=args.sparse_policies,
        walk_mode=args.walk_mode,
        width=args.width,
    )
    p764_payload = p764.analyze(p764_args)
    case_summaries = p764_payload["summary"]["case_summaries"]
    add_metadata(case_summaries, case_metadata(cases))
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p763_summary": str(args.p763_summary),
            "p766_summary": str(args.p766_summary),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(case_summaries, args),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "HOLDOUT: fresh P767 seed prefixes and extension targets are used.",
            "WIDENED-FACTOR-BASIS: P763 factor-base-limit propagation is active; requested fb64/fb80 must be exported.",
            "PUBLIC-SELECTION: sparse policy is selected from public full-rank solve cost before substitution verification.",
            "PRIVATE-VERIFY-ONLY: expected secrets are used only after public policy selection to verify recovery and mismatches.",
            "SCANNED-POOL-CHARGED: replacement policies pay group cost for all scanned candidate rows.",
            "SPARSE-WEIGHT MODEL: field-operation weights are accounting stress tests, not calibrated hardware timings.",
            "NO DEPLOYED-CURVE CLAIM: no large-prime scaling or production-key relevance is implied.",
        ],
        "method": "p767_disjoint_seed_target_extension_holdout",
        "p766_control": p766_control(args.p766_summary),
        "parameters": {
            "arm_threshold": args.arm_threshold,
            "cases": cases,
            "extension_threshold": args.extension_threshold,
            "field_weights": p764.load_module("ecdlp_p760_for_p767", p764.P760_SCRIPT).csv_ints(args.field_weights),
            "max_relations": args.max_relations,
            "max_subsets": args.max_subsets,
            "primary_threshold": args.primary_threshold,
            "public_substitution_ops_per_selected": args.public_substitution_ops_per_selected,
            "row_policy": args.row_policy,
            "sparse_policies": p764.load_module("ecdlp_p760_for_p767_sparse", p764.P760_SCRIPT).csv_strings(args.sparse_policies),
            "walk_mode": args.walk_mode,
            "width": args.width,
        },
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
            "role_summaries": group_summaries(case_summaries, "target_role"),
            "strict_pass_case_count": sum(1 for item in case_summaries if item["failure_class"] == "pass"),
            "target_factor_coverage": target_factor_coverage(case_summaries),
            "target_summaries": group_summaries(case_summaries, "target"),
            "variant_summaries": group_summaries(case_summaries, "variant"),
        },
    }


def summary_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    p764 = load_module("ecdlp_p764_summary_for_p767", P764_SCRIPT)
    return {
        "schema": f"{SCHEMA}.summary",
        "artifacts": payload["artifacts"],
        "claim_status": payload["claim_status"],
        "created_at": payload["created_at"],
        "honesty_boundary": payload["honesty_boundary"],
        "method": payload["method"],
        "p766_control": payload["p766_control"],
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
                    target_role=item.get("target_role"),
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
            "role_summaries": payload["summary"]["role_summaries"],
            "strict_pass_case_count": payload["summary"]["strict_pass_case_count"],
            "target_factor_coverage": payload["summary"]["target_factor_coverage"],
            "target_summaries": payload["summary"]["target_summaries"],
            "variant_summaries": payload["summary"]["variant_summaries"],
        },
    }


def default_cases() -> str:
    targets = [
        ("67.a1@9803", 66, "67"),
        ("21175.bc1@8089", 58, "21175"),
        ("23232.cr1@9643", 64, "23232b"),
        ("22050.cf1@10531", 66, "22050"),
        ("114224.v1@9341", 64, "114224"),
    ]
    variants = [
        ("trim4", 768, 896, 896, -4),
        ("trim8", 768, 896, 896, -8),
    ]
    entries = []
    for factor_base_size in (64, 80):
        for variant, selected, seed_count, pool_count, budget_delta in variants:
            for target, budget, tag in targets:
                actual_budget = max(1, budget + budget_delta)
                entries.append(
                    f"fb{factor_base_size}_{variant}_{tag}|{target}|{actual_budget}|{factor_base_size}|{selected}|{seed_count}|{pool_count}|ecdlp-p767-fb{factor_base_size}-{variant}-{tag}-v1|fb{factor_base_size}_{variant}"
                )
    return ",".join(entries)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", default=default_cases())
    parser.add_argument("--p763-summary", type=Path, default=DEFAULT_P763_SUMMARY)
    parser.add_argument("--p766-summary", type=Path, default=DEFAULT_P766_SUMMARY)
    parser.add_argument("--row-policy", default="sequential_min_forms_ge_1")
    parser.add_argument("--sparse-policies", default="natural,support_asc,support_span_asc,pivot_low,pivot_high,coefficient_weight_asc")
    parser.add_argument("--width", type=int, default=2)
    parser.add_argument("--walk-mode", default="hash6")
    parser.add_argument("--max-relations", type=int, default=96)
    parser.add_argument("--max-subsets", type=int, default=25000)
    parser.add_argument("--field-weights", default="1,2")
    parser.add_argument("--public-substitution-ops-per-selected", type=int, default=6)
    parser.add_argument("--primary-threshold", type=int, default=16)
    parser.add_argument("--extension-threshold", type=int, default=6)
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
                "role_summaries": summary["summary"]["role_summaries"],
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
