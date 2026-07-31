#!/usr/bin/env python3
"""P773 focused budget stress for unresolved fb112/23232.cr1@8467."""

from __future__ import annotations

import argparse
import importlib.util
import json
from datetime import datetime, timezone
from math import inf
from pathlib import Path
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P764_SCRIPT = TASK_DIR / "low_term_total2_p764_widened_factor_basis_cost_validation.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P763_SUMMARY = STATE_DIR / "low_term_total2_p763_factor_base_limit_extension_smoke_summary.json"
DEFAULT_P772_SUMMARY = STATE_DIR / "low_term_total2_p772_prospective_width_amortization_selector_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p773_unresolved_fb112_budget_stress_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p773_unresolved_fb112_budget_stress.md"
SCHEMA = "ecdlp.low_term_total2_p773_unresolved_fb112_budget_stress.v1"

TARGET = "23232.cr1@8467"
TARGET_TAG = "23232a8467"
BASE_BUDGET = 60


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


def csv_ints(text: str) -> list[int]:
    return [int(item.strip()) for item in text.split(",") if item.strip()]


def delta_tag(delta: int) -> str:
    return f"dm{abs(delta)}" if delta < 0 else f"dp{delta}"


def default_cases(deltas: list[int] | None = None) -> str:
    entries = []
    for delta in deltas or [-12, -10, -8, -6, -4]:
        budget = max(1, BASE_BUDGET + int(delta))
        tag = delta_tag(int(delta))
        entries.append(
            "|".join(
                [
                    f"fb112_s1024_{tag}_{TARGET_TAG}",
                    TARGET,
                    str(budget),
                    "112",
                    "1024",
                    "1152",
                    "1152",
                    f"ecdlp-p773-fb112-s1024-{tag}-{TARGET_TAG}-v1",
                    f"fb112_s1024_{tag}",
                ]
            )
        )
    return ",".join(entries)


def weight_cost(item: dict[str, Any], key: str = "costs_by_field_weight", weight: int = 2) -> dict[str, Any]:
    for cost in item.get(key) or []:
        if int(cost.get("field_op_weight") or 0) == weight:
            return cost
    return {}


def weight2_total(item: dict[str, Any]) -> float | None:
    value = weight_cost(item).get("total_unit_cost_over_selected_rho")
    return float(value) if value is not None else None


def public_weight2_total(item: dict[str, Any]) -> float | None:
    value = weight_cost(item, "public_costs_by_field_weight").get("total_unit_cost_over_selected_rho")
    return float(value) if value is not None else None


def budget_delta(item: dict[str, Any]) -> int:
    return int(item["budget"]) - BASE_BUDGET


def sparse_gap(item: dict[str, Any]) -> bool:
    return bool(item["oracle_best_pass_weight2_below_rho"] and not item["public_selector_pass_weight2_below_rho"])


def capacity_ok(item: dict[str, Any]) -> bool:
    support = item.get("selected_relation_support_stats") or {}
    return (
        int(item.get("selected_exported_factor_count") or 0) == int(item["factor_base_size"])
        and int(support.get("active_column_count") or 0) == int(item["factor_base_size"])
    )


def recovery_ok(item: dict[str, Any]) -> bool:
    sparse = item["public_selector_sparse_policy"]
    return bool(
        item["public_selector_recovery_ok"]
        and int((sparse.get("solve") or {}).get("rank") or 0) == int(item["factor_base_size"])
        and int((sparse.get("substitution") or {}).get("recovered_count") or 0) == int(item["selected_count"])
        and int((sparse.get("substitution") or {}).get("mismatch_count") or 0) == 0
    )


def strict_pass(item: dict[str, Any]) -> bool:
    return item.get("failure_class") == "pass"


def selected_sparse(item: dict[str, Any]) -> dict[str, Any]:
    return item["public_selector_sparse_policy"]


def policy_costs(item: dict[str, Any]) -> list[dict[str, Any]]:
    out = []
    for policy in item.get("sparse_policy_evaluations") or []:
        solve_ops = ((policy.get("solve") or {}).get("operation_counts") or {}).get("total_field_ops")
        weight2 = weight_cost(policy)
        public_weight2 = weight_cost(policy, "public_costs_by_field_weight")
        out.append(
            {
                "mismatch_count": (policy.get("substitution") or {}).get("mismatch_count"),
                "policy": policy.get("sparse_policy"),
                "public_weight2_total_over_selected_rho": public_weight2.get("total_unit_cost_over_selected_rho"),
                "rank": (policy.get("solve") or {}).get("rank"),
                "recovered_count": (policy.get("substitution") or {}).get("recovered_count"),
                "solve_field_ops": solve_ops,
                "success": policy.get("success"),
                "verified_weight2_total_over_selected_rho": weight2.get("total_unit_cost_over_selected_rho"),
            }
        )
    return sorted(
        out,
        key=lambda item: (
            item["public_weight2_total_over_selected_rho"]
            if item["public_weight2_total_over_selected_rho"] is not None
            else inf,
            item["policy"] or "",
        ),
    )


def slim_case(item: dict[str, Any]) -> dict[str, Any]:
    sparse = selected_sparse(item)
    weight2 = weight_cost(sparse)
    public_weight2 = weight_cost(sparse, "public_costs_by_field_weight")
    support = item.get("selected_relation_support_stats") or {}
    solve = sparse.get("solve") or {}
    substitution = sparse.get("substitution") or {}
    solve_ops = solve.get("operation_counts") or {}
    return {
        "active_column_count": support.get("active_column_count"),
        "budget": item["budget"],
        "budget_delta": budget_delta(item),
        "case": item["case"],
        "capacity_ok": capacity_ok(item),
        "exported_factor_count": item.get("selected_exported_factor_count"),
        "factor_relation_count": sparse.get("factor_relation_count"),
        "failure_class": item.get("failure_class"),
        "generic_rho_steps": item.get("generic_rho_steps"),
        "group_addition_cost_over_selected_rho": weight2.get("group_addition_cost_over_selected_rho"),
        "max_field_op_weight_below_selected_rho": sparse.get("max_field_op_weight_below_selected_rho"),
        "mismatch_count": substitution.get("mismatch_count"),
        "oracle_best_policy": ((item.get("oracle_best_sparse_policy") or {}).get("sparse_policy")),
        "oracle_best_weight2_total_over_selected_rho": weight2_total(item.get("oracle_best_sparse_policy") or {}),
        "oracle_pass": bool(item.get("oracle_best_pass_weight2_below_rho")),
        "policy_costs": policy_costs(item),
        "public_max_field_op_weight_below_selected_rho": sparse.get("public_max_field_op_weight_below_selected_rho"),
        "public_policy": sparse.get("sparse_policy"),
        "public_selector_gap": sparse_gap(item),
        "public_weight2_total_over_selected_rho": public_weight2.get("total_unit_cost_over_selected_rho"),
        "rank": solve.get("rank"),
        "recovered_count": substitution.get("recovered_count"),
        "recovery_ok": recovery_ok(item),
        "scanned_count": item.get("scanned_count"),
        "selected_count": item.get("selected_count"),
        "solve_field_ops": solve_ops.get("total_field_ops"),
        "strict_pass": strict_pass(item),
        "substitution_field_ops": (substitution.get("operation_counts") or {}).get("total_field_ops"),
        "target": item.get("target"),
        "verified_weight2_slack": round(1.0 - float(weight2.get("total_unit_cost_over_selected_rho")), 8)
        if weight2.get("total_unit_cost_over_selected_rho") is not None
        else None,
        "verified_weight2_total_over_selected_rho": weight2.get("total_unit_cost_over_selected_rho"),
    }


def select_budget_case(cases: list[dict[str, Any]]) -> dict[str, Any]:
    return min(
        cases,
        key=lambda item: (
            public_weight2_total(selected_sparse(item)) or inf,
            -(float(selected_sparse(item).get("public_max_field_op_weight_below_selected_rho") or 0.0)),
            budget_delta(item),
            item["case"],
        ),
    )


def best_verified_case(cases: list[dict[str, Any]]) -> dict[str, Any]:
    return min(
        cases,
        key=lambda item: (
            weight2_total(selected_sparse(item)) or inf,
            0 if recovery_ok(item) else 1,
            budget_delta(item),
            item["case"],
        ),
    )


def p772_control(path: Path) -> dict[str, Any]:
    payload = load_json(path)
    group = None
    for item in (((payload.get("summary") or {}).get("selected_groups")) or []):
        if item.get("group_key") == f"fb112|{TARGET}":
            group = item
            break
    return {
        "claim_status": payload.get("claim_status"),
        "group": group,
        "selected_strict_pass_count": ((payload.get("summary") or {}).get("selected_strict_pass_count")),
        "selector_gap_count": ((payload.get("summary") or {}).get("selector_gap_count")),
    }


def determine_claim(summary: dict[str, Any]) -> str:
    total = int(summary["case_count"])
    if summary["budget_selected_strict_pass"] and summary["public_sparse_selector_gap_count"] == 0:
        return "P773_UNRESOLVED_FB112_PUBLIC_BUDGET_PRIMARY_SIGNAL"
    if summary["strict_pass_count"] and summary["budget_selector_gap"]:
        return "P773_UNRESOLVED_FB112_PUBLIC_BUDGET_SELECTOR_GAP"
    if summary["strict_pass_count"]:
        return "P773_UNRESOLVED_FB112_FIRST_PASS_SIGNAL"
    if summary["capacity_ok_count"] < total:
        return "P773_UNRESOLVED_FB112_CAPACITY_REGRESSION"
    if summary["recovery_ok_count"] == total:
        return "P773_UNRESOLVED_FB112_RECOVERY_OK_COST_NEGATIVE"
    return "NEGATIVE_RESULT_P773_UNRESOLVED_FB112_BUDGET_STRESS"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p764 = load_module("ecdlp_p764_for_p773", P764_SCRIPT)
    deltas = csv_ints(args.budget_deltas)
    p764_args = argparse.Namespace(
        arm_threshold=1,
        cases=args.cases or default_cases(deltas),
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
    p764_payload = p764.analyze(p764_args)
    cases = p764_payload["summary"]["case_summaries"]
    selected = select_budget_case(cases)
    best = best_verified_case(cases)
    slim_cases = [slim_case(item) for item in sorted(cases, key=lambda item: budget_delta(item))]
    pass_cases = [item for item in cases if strict_pass(item)]
    summary = {
        "best_verified_case": best["case"],
        "best_verified_delta": budget_delta(best),
        "best_verified_strict_pass": strict_pass(best),
        "best_verified_weight2": weight2_total(selected_sparse(best)),
        "budget_deltas": deltas,
        "budget_selected_case": selected["case"],
        "budget_selected_delta": budget_delta(selected),
        "budget_selected_policy": selected_sparse(selected).get("sparse_policy"),
        "budget_selected_public_weight2": public_weight2_total(selected_sparse(selected)),
        "budget_selected_recovery_ok": recovery_ok(selected),
        "budget_selected_strict_pass": strict_pass(selected),
        "budget_selected_verified_weight2": weight2_total(selected_sparse(selected)),
        "budget_selector_gap": bool(pass_cases and not strict_pass(selected)),
        "capacity_ok_count": sum(1 for item in cases if capacity_ok(item)),
        "case_count": len(cases),
        "case_summaries": slim_cases,
        "min_pass_delta": min((budget_delta(item) for item in pass_cases), default=None),
        "min_pass_weight2": min((weight2_total(selected_sparse(item)) for item in pass_cases), default=None),
        "public_sparse_selector_gap_count": sum(1 for item in cases if sparse_gap(item)),
        "recovery_ok_count": sum(1 for item in cases if recovery_ok(item)),
        "strict_pass_count": len(pass_cases),
        "target": TARGET,
    }
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p772_summary": str(args.p772_summary),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(summary),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "FOCUSED-STRESS: only the persistent P772 miss fb112|23232.cr1@8467 is tested.",
            "BUDGET-STRESS: selected count, factor-base size, row policy, and sparse-policy set are fixed while row budget changes.",
            "PUBLIC-SELECTION: sparse policy and budget candidate are selected from public cost features before substitution verification.",
            "PRIVATE-VERIFY-ONLY: expected secrets are used only after public selection to verify recovery and mismatches.",
            "SCANNED-POOL-CHARGED: replacement policies pay group cost for all scanned candidate rows.",
            "SPARSE-WEIGHT MODEL: field-operation weights are accounting stress tests, not calibrated hardware timings.",
            "NO DEPLOYED-CURVE CLAIM: no large-prime scaling or production-key relevance is implied.",
        ],
        "method": "p773_unresolved_fb112_budget_stress",
        "p772_control": p772_control(args.p772_summary),
        "p764_payload": p764_payload,
        "parameters": {
            "base_budget": BASE_BUDGET,
            "budget_deltas": deltas,
            "factor_base_size": 112,
            "field_weights": csv_ints(args.field_weights),
            "max_relations": args.max_relations,
            "max_subsets": args.max_subsets,
            "pool_count": 1152,
            "public_substitution_ops_per_selected": args.public_substitution_ops_per_selected,
            "row_policy": args.row_policy,
            "seed_count": 1152,
            "selected_count": 1024,
            "sparse_policies": [item.strip() for item in args.sparse_policies.split(",") if item.strip()],
            "target": TARGET,
            "walk_mode": args.walk_mode,
            "width": args.width,
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
        "p772_control": payload["p772_control"],
        "parameters": payload["parameters"],
        "summary": payload["summary"],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--budget-deltas", default="-12,-10,-8,-6,-4")
    parser.add_argument("--cases", default="")
    parser.add_argument("--p763-summary", type=Path, default=DEFAULT_P763_SUMMARY)
    parser.add_argument("--p772-summary", type=Path, default=DEFAULT_P772_SUMMARY)
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
                "best_verified_delta": summary["summary"]["best_verified_delta"],
                "best_verified_strict_pass": summary["summary"]["best_verified_strict_pass"],
                "best_verified_weight2": summary["summary"]["best_verified_weight2"],
                "budget_selected_delta": summary["summary"]["budget_selected_delta"],
                "budget_selected_strict_pass": summary["summary"]["budget_selected_strict_pass"],
                "budget_selected_verified_weight2": summary["summary"]["budget_selected_verified_weight2"],
                "budget_selector_gap": summary["summary"]["budget_selector_gap"],
                "capacity_ok_count": summary["summary"]["capacity_ok_count"],
                "case_count": summary["summary"]["case_count"],
                "claim_status": summary["claim_status"],
                "public_sparse_selector_gap_count": summary["summary"]["public_sparse_selector_gap_count"],
                "recovery_ok_count": summary["summary"]["recovery_ok_count"],
                "strict_pass_count": summary["summary"]["strict_pass_count"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
