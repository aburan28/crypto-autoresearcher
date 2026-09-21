#!/usr/bin/env python3
"""P769 frozen-trim8 width stress for widened public trims."""

from __future__ import annotations

import argparse
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P768_SCRIPT = TASK_DIR / "low_term_total2_p768_frozen_trim8_extension_sweep.py"
P764_SCRIPT = TASK_DIR / "low_term_total2_p764_widened_factor_basis_cost_validation.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P760_SUMMARY = STATE_DIR / "low_term_total2_p760_public_sparse_policy_selector_summary.json"
DEFAULT_P763_SUMMARY = STATE_DIR / "low_term_total2_p763_factor_base_limit_extension_smoke_summary.json"
DEFAULT_P767_SUMMARY = STATE_DIR / "low_term_total2_p767_disjoint_seed_target_extension_holdout_summary.json"
DEFAULT_P768_SUMMARY = STATE_DIR / "low_term_total2_p768_frozen_trim8_extension_sweep_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p769_frozen_trim8_width_stress_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p769_frozen_trim8_width_stress.md"
SCHEMA = "ecdlp.low_term_total2_p769_frozen_trim8_width_stress.v1"


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


def prior_control(path: Path) -> dict[str, Any]:
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


def determine_claim(p768: Any, case_summaries: list[dict[str, Any]], args: argparse.Namespace) -> str:
    total = len(case_summaries)
    strict = sum(1 for item in case_summaries if item["failure_class"] == "pass")
    recovery_ok = sum(1 for item in case_summaries if item["public_selector_recovery_ok"])
    gaps = sum(1 for item in case_summaries if item["failure_class"] == "selector_gap")
    capacity = sum(1 for item in case_summaries if item["failure_class"] == "capacity_or_support_failure")
    factors = p768.group_summaries(case_summaries, "factor_bucket")
    factor_min = min((summary["strict_pass_count"] for summary in factors.values()), default=0)
    factor_max = max((summary["strict_pass_count"] for summary in factors.values()), default=0)
    if total and strict == total:
        return "P769_FROZEN_TRIM8_WIDTH_STRESS_ALL_CASE_SIGNAL"
    if (
        strict >= int(args.primary_threshold)
        and factor_min >= int(args.factor_threshold)
        and recovery_ok == total
        and gaps == 0
        and capacity == 0
    ):
        return "P769_FROZEN_TRIM8_WIDTH_STRESS_PRIMARY_SIGNAL"
    if factor_max >= int(args.factor_majority_threshold) and recovery_ok == total and gaps == 0 and capacity == 0:
        return "P769_FROZEN_TRIM8_WIDTH_STRESS_USEFUL_SIGNAL"
    if recovery_ok == total and capacity == 0:
        return "P769_FROZEN_TRIM8_WIDTH_STRESS_RECOVERY_OK_COST_NEGATIVE"
    if capacity:
        return "P769_FROZEN_TRIM8_WIDTH_STRESS_CAPACITY_REGRESSION"
    return "NEGATIVE_RESULT_P769_FROZEN_TRIM8_WIDTH_STRESS"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p768 = load_module("ecdlp_p768_frozen_trim8_extension_sweep", P768_SCRIPT)
    payload = p768.analyze(args)
    case_summaries = payload["summary"]["case_summaries"]
    payload.update(
        {
            "artifacts": {
                "contract": str(DEFAULT_CONTRACT),
                "p760_summary": str(args.p760_summary),
                "p763_summary": str(args.p763_summary),
                "p767_summary": str(args.p767_summary),
                "p768_summary": str(args.p768_summary),
                "script": str(Path(__file__)),
            },
            "claim_status": determine_claim(p768, case_summaries, args),
            "created_at": now_iso(),
            "honesty_boundary": [
                "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
                "WIDTH-STRESS: requested factor-base sizes are 96 and 112, beyond the P768 fb64/fb80 signal.",
                "FROZEN-RULE: only trim8 is tested, using fresh P769 seed prefixes.",
                "TARGET-EXTENSION: seven non-11779 target/order samples are included.",
                "WIDENED-FACTOR-BASIS: requested fb96/fb112 must be exported and active before cost interpretation.",
                "PUBLIC-SELECTION: sparse policy is selected from public full-rank solve cost before substitution verification.",
                "PRIVATE-VERIFY-ONLY: expected secrets are used only after public policy selection to verify recovery and mismatches.",
                "SCANNED-POOL-CHARGED: replacement policies pay group cost for all scanned candidate rows.",
                "SPARSE-WEIGHT MODEL: field-operation weights are accounting stress tests, not calibrated hardware timings.",
                "NO DEPLOYED-CURVE CLAIM: no large-prime scaling or production-key relevance is implied.",
            ],
            "method": "p769_frozen_trim8_width_stress",
            "p768_control": prior_control(args.p768_summary),
            "schema": SCHEMA,
        }
    )
    return payload


def summary_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    p764 = load_module("ecdlp_p764_summary_for_p769", P764_SCRIPT)
    return {
        "schema": f"{SCHEMA}.summary",
        "artifacts": payload["artifacts"],
        "claim_status": payload["claim_status"],
        "created_at": payload["created_at"],
        "honesty_boundary": payload["honesty_boundary"],
        "method": payload["method"],
        "p760_control": payload["p760_control"],
        "p767_control": payload["p767_control"],
        "p768_control": payload["p768_control"],
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
        ("67.a1@9803", 66, "67a9803"),
        ("22050.cf1@10531", 66, "22050"),
        ("114224.v1@9341", 64, "114224"),
        ("21175.bc1@8089", 58, "21175"),
        ("23232.cr1@8467", 60, "23232a8467"),
        ("23232.cr1@9643", 64, "23232b9643"),
        ("67.a1@11923", 72, "67b11923"),
    ]
    entries = []
    for factor_base_size in (96, 112):
        for target, budget, tag in targets:
            actual_budget = max(1, budget - 8)
            entries.append(
                f"fb{factor_base_size}_trim8_{tag}|{target}|{actual_budget}|{factor_base_size}|768|896|896|ecdlp-p769-fb{factor_base_size}-trim8-{tag}-v1|fb{factor_base_size}_trim8"
            )
    return ",".join(entries)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", default=default_cases())
    parser.add_argument("--p760-summary", type=Path, default=DEFAULT_P760_SUMMARY)
    parser.add_argument("--p763-summary", type=Path, default=DEFAULT_P763_SUMMARY)
    parser.add_argument("--p767-summary", type=Path, default=DEFAULT_P767_SUMMARY)
    parser.add_argument("--p768-summary", type=Path, default=DEFAULT_P768_SUMMARY)
    parser.add_argument("--row-policy", default="sequential_min_forms_ge_1")
    parser.add_argument("--sparse-policies", default="natural,support_asc,support_span_asc,pivot_low,pivot_high,coefficient_weight_asc")
    parser.add_argument("--width", type=int, default=2)
    parser.add_argument("--walk-mode", default="hash6")
    parser.add_argument("--max-relations", type=int, default=96)
    parser.add_argument("--max-subsets", type=int, default=25000)
    parser.add_argument("--field-weights", default="1,2")
    parser.add_argument("--public-substitution-ops-per-selected", type=int, default=6)
    parser.add_argument("--primary-threshold", type=int, default=12)
    parser.add_argument("--factor-threshold", type=int, default=6)
    parser.add_argument("--factor-majority-threshold", type=int, default=4)
    parser.add_argument("--new-extension-threshold", type=int, default=3)
    parser.add_argument("--arm-threshold", type=int, default=6)
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
                "target_factor_coverage": summary["summary"]["target_factor_coverage"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
