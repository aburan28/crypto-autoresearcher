#!/usr/bin/env python3
"""P761 scaling stress for the P760 public sparse-policy selector."""

from __future__ import annotations

import argparse
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P760_SCRIPT = TASK_DIR / "low_term_total2_p760_public_sparse_policy_selector.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P760_SUMMARY = STATE_DIR / "low_term_total2_p760_public_sparse_policy_selector_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p761_selector_scaling_stress_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p761_selector_scaling_stress.md"
SCHEMA = "ecdlp.low_term_total2_p761_selector_scaling_stress.v1"


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


def parse_cases(raw: str) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue
        parts = item.split("|")
        if len(parts) != 9:
            raise argparse.ArgumentTypeError(
                "cases must be label|target|budget|factor_base_size|selected_count|seed_count|pool_count|seed_prefix|arm entries"
            )
        label, target, budget, factor_base_size, selected_count, seed_count, pool_count, seed_prefix, arm = (
            part.strip() for part in parts
        )
        cases.append(
            {
                "arm": arm,
                "budget": int(budget),
                "factor_base_size": int(factor_base_size),
                "label": label,
                "pool_count": int(pool_count),
                "seed_count": int(seed_count),
                "seed_prefix": seed_prefix,
                "selected_count": int(selected_count),
                "target": target,
            }
        )
    if not cases:
        raise argparse.ArgumentTypeError("at least one case is required")
    return cases


def slim_case(p760: Any, item: dict[str, Any]) -> dict[str, Any]:
    base = p760.slim_case(item)
    base.update(
        {
            "arm": item["arm"],
            "factor_base_size": item["factor_base_size"],
            "failure_class": item["failure_class"],
            "pool_count": item["pool_count"],
            "seed_count": item["seed_count"],
            "selected_target_count": item["selected_target_count"],
        }
    )
    return base


def classify_case(item: dict[str, Any]) -> str:
    selected = int(item["selected_count"])
    target_selected = int(item["selected_target_count"])
    factor_base_size = int(item["factor_base_size"])
    chosen = item["public_selector_sparse_policy"]
    oracle = item["oracle_best_sparse_policy"]
    zero_forms = item["selected_feature_stats"]["zero_form_rows"]
    if selected != target_selected or zero_forms:
        return "row_budget_failure"
    if (
        chosen["solve"]["rank"] < factor_base_size
        or chosen["substitution"]["recovered_count"] != target_selected
        or chosen["substitution"]["mismatch_count"] != 0
    ):
        return "rank_or_recovery_failure"
    if item["oracle_best_pass_weight2_below_rho"] and not item["public_selector_pass_weight2_below_rho"]:
        return "selector_gap"
    if not item["public_selector_pass_weight2_below_rho"]:
        return "scaling_cost_failure"
    return "pass"


def arm_summaries(case_summaries: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for item in case_summaries:
        arm = str(item["arm"])
        bucket = out.setdefault(
            arm,
            {
                "case_count": 0,
                "failure_classes": {},
                "oracle_best_pass_count": 0,
                "public_selector_gap_count": 0,
                "public_selector_pass_count": 0,
                "public_selector_recovery_ok_count": 0,
            },
        )
        bucket["case_count"] += 1
        bucket["oracle_best_pass_count"] += int(bool(item["oracle_best_pass_weight2_below_rho"]))
        bucket["public_selector_gap_count"] += int(
            bool(item["oracle_best_pass_weight2_below_rho"] and not item["public_selector_pass_weight2_below_rho"])
        )
        bucket["public_selector_pass_count"] += int(bool(item["public_selector_pass_weight2_below_rho"]))
        bucket["public_selector_recovery_ok_count"] += int(bool(item["public_selector_recovery_ok"]))
        failures = bucket["failure_classes"]
        failures[item["failure_class"]] = failures.get(item["failure_class"], 0) + 1
    return out


def determine_claim(case_summaries: list[dict[str, Any]], args: argparse.Namespace) -> str:
    total = len(case_summaries)
    cost_pass_count = sum(1 for item in case_summaries if item["public_selector_pass_weight2_below_rho"])
    strict_pass_count = sum(1 for item in case_summaries if item["failure_class"] == "pass")
    recovery_ok = sum(1 for item in case_summaries if item["public_selector_recovery_ok"])
    gaps = sum(1 for item in case_summaries if item["failure_class"] == "selector_gap")
    rank_or_recovery_failures = sum(
        1 for item in case_summaries if item["failure_class"] == "rank_or_recovery_failure"
    )
    arms = arm_summaries(case_summaries)
    arm_min_strict_pass = min(
        (summary["failure_classes"].get("pass", 0) for summary in arms.values()), default=0
    )
    if total and strict_pass_count == total:
        return "P761_SELECTOR_SCALING_STRESS_ALL_CASE_SIGNAL"
    if (
        strict_pass_count >= int(args.primary_threshold)
        and arm_min_strict_pass >= int(args.arm_threshold)
        and gaps == 0
    ):
        return "P761_SELECTOR_SCALING_STRESS_PRIMARY_SIGNAL"
    if rank_or_recovery_failures and cost_pass_count == total and gaps == 0:
        return "P761_SELECTOR_SCALING_RANK_RECOVERY_NEGATIVE_COST_SIGNAL"
    if recovery_ok == total and gaps <= 1:
        return "P761_SELECTOR_SCALING_RECOVERY_OK_COST_MARGIN_NEGATIVE"
    if gaps > 1:
        return "P761_SELECTOR_SCALING_SELECTOR_GAP"
    return "NEGATIVE_RESULT_P761_SELECTOR_SCALING_STRESS"


def p760_control(path: Path) -> dict[str, Any]:
    payload = load_json(path)
    return {
        "claim_status": payload.get("claim_status"),
        "oracle_best_pass_count": ((payload.get("summary") or {}).get("oracle_best_pass_count")),
        "public_selector_gap_count": ((payload.get("summary") or {}).get("public_selector_gap_count")),
        "public_selector_pass_count": ((payload.get("summary") or {}).get("public_selector_pass_count")),
        "public_selector_recovery_ok_count": ((payload.get("summary") or {}).get("public_selector_recovery_ok_count")),
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p760 = load_module("ecdlp_p760_public_sparse_policy_selector", P760_SCRIPT)
    p755 = p760.load_module("ecdlp_p755_public_selector", p760.P755_SCRIPT)
    p746 = p755.load_module("ecdlp_p746_incremental_walk", p755.P746_SCRIPT)
    p748 = p755.load_module("ecdlp_p748_matrix_bridge", p755.P748_SCRIPT)
    p750 = p755.load_module("ecdlp_p750_prospective_prefix", p755.P750_SCRIPT)
    p751 = p755.load_module("ecdlp_p751_factor_first", p755.P751_SCRIPT)
    p752 = p755.load_module("ecdlp_p752_sparse_factor_basis", p755.P752_SCRIPT)
    relprobe = p746.load_relation_probe_module()
    cases = parse_cases(args.cases)
    sparse_policies = p760.csv_strings(args.sparse_policies)
    field_weights = p760.csv_ints(args.field_weights)
    if 2 not in field_weights:
        field_weights.append(2)
        field_weights = sorted(set(field_weights))

    case_summaries: list[dict[str, Any]] = []
    raw_results: dict[str, list[dict[str, Any]]] = {}
    for case in cases:
        case_args = SimpleNamespace(
            factor_base_size=case["factor_base_size"],
            field_weights=field_weights,
            max_relations=args.max_relations,
            max_subsets=args.max_subsets,
            pool_count=case["pool_count"],
            public_substitution_ops_per_selected=args.public_substitution_ops_per_selected,
            row_policy=args.row_policy,
            seed_count=case["seed_count"],
            selected_count=case["selected_count"],
            sparse_policies=sparse_policies,
            walk_mode=args.walk_mode,
            width=args.width,
        )
        p760_case = {
            "budget": case["budget"],
            "label": case["label"],
            "role": case["arm"],
            "seed_prefix": case["seed_prefix"],
            "target": case["target"],
        }
        summary, rows = p760.evaluate_case(
            p755,
            p748,
            p750,
            p751,
            p752,
            p746,
            relprobe,
            p760_case,
            case_args,
            sparse_policies,
            field_weights,
        )
        summary.update(
            {
                "arm": case["arm"],
                "factor_base_size": case["factor_base_size"],
                "pool_count": case["pool_count"],
                "seed_count": case["seed_count"],
                "selected_target_count": case["selected_count"],
            }
        )
        summary["failure_class"] = classify_case(summary)
        case_summaries.append(summary)
        raw_results[str(case["label"])] = [p750.strip_private(row) for row in rows]

    arms = arm_summaries(case_summaries)
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p760_summary": str(args.p760_summary),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(case_summaries, args),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "SCALING-STRESS: this deliberately changes selected count or factor-base dimension relative to P760.",
            "PUBLIC-SELECTION: sparse policy remains the exact P760 public full-rank solve-cost selector.",
            "PRIVATE-VERIFY-ONLY: expected secrets are used only after public policy selection to verify recovery and mismatches.",
            "SCANNED-POOL-CHARGED: replacement policies pay group cost for all scanned candidate rows.",
            "SPARSE-WEIGHT MODEL: field-operation weights are accounting stress tests, not calibrated hardware timings.",
            "NO DEPLOYED-CURVE CLAIM: no large-prime scaling or production-key relevance is implied.",
        ],
        "method": "p761_selector_scaling_stress",
        "parameters": {
            "arm_threshold": args.arm_threshold,
            "cases": cases,
            "field_weights": field_weights,
            "max_relations": args.max_relations,
            "max_subsets": args.max_subsets,
            "primary_threshold": args.primary_threshold,
            "public_substitution_ops_per_selected": args.public_substitution_ops_per_selected,
            "row_policy": args.row_policy,
            "sparse_policies": sparse_policies,
            "walk_mode": args.walk_mode,
            "width": args.width,
        },
        "p760_control": p760_control(args.p760_summary),
        "results": raw_results,
        "schema": SCHEMA,
        "summary": {
            "arm_summaries": arms,
            "case_count": len(case_summaries),
            "case_summaries": case_summaries,
            "oracle_best_pass_count": sum(1 for item in case_summaries if item["oracle_best_pass_weight2_below_rho"]),
            "public_selector_gap_count": sum(1 for item in case_summaries if item["failure_class"] == "selector_gap"),
            "public_selector_pass_count": sum(1 for item in case_summaries if item["public_selector_pass_weight2_below_rho"]),
            "public_selector_recovery_ok_count": sum(1 for item in case_summaries if item["public_selector_recovery_ok"]),
            "strict_pass_case_count": sum(1 for item in case_summaries if item["failure_class"] == "pass"),
        },
    }


def summary_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    p760 = load_module("ecdlp_p760_public_sparse_policy_selector_for_summary", P760_SCRIPT)
    return {
        "schema": f"{SCHEMA}.summary",
        "artifacts": payload["artifacts"],
        "claim_status": payload["claim_status"],
        "created_at": payload["created_at"],
        "honesty_boundary": payload["honesty_boundary"],
        "method": payload["method"],
        "p760_control": payload["p760_control"],
        "parameters": payload["parameters"],
        "summary": {
            "arm_summaries": payload["summary"]["arm_summaries"],
            "case_count": payload["summary"]["case_count"],
            "case_summaries": [slim_case(p760, item) for item in payload["summary"]["case_summaries"]],
            "oracle_best_pass_count": payload["summary"]["oracle_best_pass_count"],
            "public_selector_gap_count": payload["summary"]["public_selector_gap_count"],
            "public_selector_pass_count": payload["summary"]["public_selector_pass_count"],
            "public_selector_recovery_ok_count": payload["summary"]["public_selector_recovery_ok_count"],
            "strict_pass_case_count": payload["summary"]["strict_pass_case_count"],
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
    for target, budget, tag in targets:
        entries.append(
            f"batch768_fb48_{tag}|{target}|{budget}|48|768|896|896|ecdlp-p761-batch768-fb48-{tag}-v1|batch768_fb48"
        )
    for target, budget, tag in targets:
        entries.append(
            f"fb64_batch640_{tag}|{target}|{budget}|64|640|768|768|ecdlp-p761-fb64-batch640-{tag}-v1|fb64_batch640"
        )
    return ",".join(entries)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", default=default_cases())
    parser.add_argument("--p760-summary", type=Path, default=DEFAULT_P760_SUMMARY)
    parser.add_argument("--row-policy", default="sequential_min_forms_ge_1")
    parser.add_argument("--sparse-policies", default="natural,support_asc,support_span_asc,pivot_low,pivot_high,coefficient_weight_asc")
    parser.add_argument("--width", type=int, default=2)
    parser.add_argument("--walk-mode", default="hash6")
    parser.add_argument("--max-relations", type=int, default=96)
    parser.add_argument("--max-subsets", type=int, default=25000)
    parser.add_argument("--field-weights", default="1,2")
    parser.add_argument("--public-substitution-ops-per-selected", type=int, default=6)
    parser.add_argument("--primary-threshold", type=int, default=10)
    parser.add_argument("--arm-threshold", type=int, default=5)
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
                "arm_summaries": summary["summary"]["arm_summaries"],
                "claim_status": summary["claim_status"],
                "oracle_best_pass_count": summary["summary"]["oracle_best_pass_count"],
                "public_selector_gap_count": summary["summary"]["public_selector_gap_count"],
                "public_selector_pass_count": summary["summary"]["public_selector_pass_count"],
                "public_selector_recovery_ok_count": summary["summary"]["public_selector_recovery_ok_count"],
                "strict_pass_case_count": summary["summary"]["strict_pass_case_count"],
                "cases": [
                    {
                        "arm": item["arm"],
                        "case": item["case"],
                        "failure_class": item["failure_class"],
                        "policy": item["public_selector_sparse_policy"]["policy"],
                        "target": item["target"],
                        "verified_weight2": item["public_selector_sparse_policy"]["weight2_cost"].get("total_unit_cost_over_selected_rho"),
                    }
                    for item in summary["summary"]["case_summaries"]
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
