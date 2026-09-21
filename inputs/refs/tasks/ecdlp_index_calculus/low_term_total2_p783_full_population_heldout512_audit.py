#!/usr/bin/env python3
"""P783 full-population held-out512 audit using the P782 evaluator."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P782_SCRIPT = TASK_DIR / "low_term_total2_p782_heldout_scaling_stress.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P777_SUMMARY = STATE_DIR / "low_term_total2_p777_merged_trim12_factor_first_cost_audit_summary.json"
DEFAULT_P779_SUMMARY = STATE_DIR / "low_term_total2_p779_prospective_public_trim10_exception_rule_summary.json"
DEFAULT_P781_SUMMARY = STATE_DIR / "low_term_total2_p781_full_population_heldout_descent_audit_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p783_full_population_heldout512_audit_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p783_full_population_heldout512_audit.md"
SCHEMA = "ecdlp.low_term_total2_p783_full_population_heldout512_audit.v1"


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {name} from {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def full_population_groups(path: Path) -> list[str]:
    payload = load_json(path)
    normalized = ((payload.get("summary") or {}).get("normalized_cases")) or []
    groups = sorted({str(item.get("group_key") or f"fb{int(item['factor_base_size'])}|{item['target']}") for item in normalized})
    if len(groups) != 36:
        raise ValueError(f"expected 36 normalized groups from {path}, got {len(groups)}")
    return groups


def determine_claim(summary: dict[str, Any]) -> str:
    total = int(summary["selected_group_count"])
    if total != 36:
        return "NEGATIVE_RESULT_P783_NOT_FULL_POPULATION"
    selected_agg = summary["selected_aggregate_cost"]["aggregate_weight2_total_over_selected_rho"]
    max_selected = summary["selected_weight2_stats"]["max"]
    checkpoint_costs = summary["checkpoint_aggregate_costs"]
    all_checkpoint_ok = all(
        item["case_count"] == total
        and item["heldout_recovery_ok_count"] == total
        and item["mismatch_count"] == 0
        and item["marginal_total_unit_cost_over_heldout_rho"] is not None
        and float(item["marginal_total_unit_cost_over_heldout_rho"]) < 1.0
        and item["combined_total_unit_cost_over_recovered_rho"] is not None
        and float(item["combined_total_unit_cost_over_recovered_rho"]) < 1.0
        for item in checkpoint_costs.values()
    )
    if (
        int(summary["selected_strict_pass_count"]) == total
        and int(summary["selected_recovery_ok_count"]) == total
        and int(summary["selected_capacity_ok_count"]) == total
        and int(summary["public_sparse_selector_gap_count"]) == 0
        and selected_agg is not None
        and float(selected_agg) < 1.0
        and max_selected is not None
        and float(max_selected) < 1.0
        and all_checkpoint_ok
    ):
        return "P783_FULL_POPULATION_HELDOUT512_SIGNAL"
    if (
        int(summary["selected_recovery_ok_count"]) == total
        and int(summary["selected_capacity_ok_count"]) == total
        and selected_agg is not None
        and float(selected_agg) < 1.0
    ):
        return "P783_FULL_POPULATION_SELECTED_SIGNAL_HELDOUT512_OPEN"
    if any(item["mismatch_count"] for item in checkpoint_costs.values()):
        return "NEGATIVE_RESULT_P783_HELDOUT512_MISMATCH"
    return "NEGATIVE_RESULT_P783_FULL_POPULATION_HELDOUT512_AUDIT"


def factor_target_summaries(cases: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for item in cases:
        bucket_key = str(item[key])
        bucket = out.setdefault(
            bucket_key,
            {
                "case_count": 0,
                "heldout512_mismatch_count": 0,
                "heldout512_recovered_count": 0,
                "heldout512_target_count": 0,
                "selected_strict_pass_count": 0,
            },
        )
        checkpoint = item["heldout_checkpoints"]["512"]
        bucket["case_count"] += 1
        bucket["heldout512_mismatch_count"] += int(checkpoint["mismatch_count"])
        bucket["heldout512_recovered_count"] += int(checkpoint["recovered_count"])
        bucket["heldout512_target_count"] += int(checkpoint["target_count"])
        bucket["selected_strict_pass_count"] += int(item["selected_strict_pass"])
    return out


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p782 = load_module("ecdlp_p782_for_p783", P782_SCRIPT)
    groups = full_population_groups(args.p777_summary)
    p782_args = argparse.Namespace(
        field_weights=args.field_weights,
        groups=",".join(groups),
        max_relations=args.max_relations,
        max_subsets=args.max_subsets,
        out=args.out,
        p777_summary=args.p777_summary,
        p779_summary=args.p779_summary,
        p781_summary=args.p781_summary,
        public_substitution_ops_per_selected=args.public_substitution_ops_per_selected,
        row_policy=args.row_policy,
        seed_namespace=args.seed_namespace,
        sparse_policies=args.sparse_policies,
        summary_out=args.summary_out,
        walk_mode=args.walk_mode,
        width=args.width,
    )
    payload = p782.analyze(p782_args)
    summary = payload["summary"]
    summary["full_population_group_count"] = len(groups)
    summary["factor_population_summaries"] = factor_target_summaries(summary["selected_cases"], "factor_bucket")
    summary["target_population_summaries"] = factor_target_summaries(summary["selected_cases"], "target")
    payload.update(
        {
            "artifacts": {
                "contract": str(DEFAULT_CONTRACT),
                "p777_summary": str(args.p777_summary),
                "p779_summary": str(args.p779_summary),
                "p781_summary": str(args.p781_summary),
                "script": str(Path(__file__)),
                "shared_scaling_evaluator": str(P782_SCRIPT),
            },
            "claim_status": determine_claim(summary),
            "honesty_boundary": [
                "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
                "FULL-POPULATION: P783 applies the P782 held-out512 scaling proxy to all 36 normalized fb96/fb112 groups.",
                "FRESH-PROSPECTIVE: all rows use fresh P783 seed prefixes through the shared P782 evaluator.",
                "PUBLIC-THRESHOLD: trim10 exception collection is triggered only by public trim12 weight-2 cost.",
                "HELDOUT-SCALING-PROXY: held-out rows are excluded from the factor solve, but remain same-distribution synthetic rows, not arbitrary cryptographic-size target descent.",
                "PRIVATE-VERIFY-ONLY: expected secrets verify selected and held-out substitution after public choices are made.",
                "NO DEPLOYED-CURVE CLAIM: no large-prime scaling, production-key relevance, or complete faster-than-rho ECDLP algorithm is implied.",
            ],
            "method": "p783_full_population_heldout512_audit",
            "schema": SCHEMA,
            "summary": summary,
        }
    )
    payload["parameters"]["seed_namespace"] = args.seed_namespace
    payload["parameters"]["full_population_group_count"] = len(groups)
    return payload


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
    parser.add_argument("--p777-summary", type=Path, default=DEFAULT_P777_SUMMARY)
    parser.add_argument("--p779-summary", type=Path, default=DEFAULT_P779_SUMMARY)
    parser.add_argument("--p781-summary", type=Path, default=DEFAULT_P781_SUMMARY)
    parser.add_argument("--seed-namespace", default="full512-v1")
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
                "checkpoint_aggregate_costs": summary["summary"]["checkpoint_aggregate_costs"],
                "claim_status": summary["claim_status"],
                "flagged_group_count": summary["summary"]["flagged_group_count"],
                "fresh_trim10_case_count": summary["summary"]["fresh_trim10_case_count"],
                "fresh_trim12_case_count": summary["summary"]["fresh_trim12_case_count"],
                "full_population_group_count": summary["summary"]["full_population_group_count"],
                "heldout_available_min": summary["summary"]["heldout_available_min"],
                "selected_aggregate_weight2": summary["summary"]["selected_aggregate_cost"][
                    "aggregate_weight2_total_over_selected_rho"
                ],
                "selected_delta_counts": summary["summary"]["selected_delta_counts"],
                "selected_group_count": summary["summary"]["selected_group_count"],
                "selected_strict_pass_count": summary["summary"]["selected_strict_pass_count"],
                "selected_weight2_max": summary["summary"]["selected_weight2_stats"]["max"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
