#!/usr/bin/env python3
"""P775 public budget-selector holdout transfer stress."""

from __future__ import annotations

import argparse
import importlib.util
import json
from collections import Counter
from datetime import datetime, timezone
from math import inf
from pathlib import Path
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P764_SCRIPT = TASK_DIR / "low_term_total2_p764_widened_factor_basis_cost_validation.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_FRONTIER = STATE_DIR / "frontier_targets.json"
DEFAULT_P763_SUMMARY = STATE_DIR / "low_term_total2_p763_factor_base_limit_extension_smoke_summary.json"
DEFAULT_P774_SUMMARY = STATE_DIR / "low_term_total2_p774_public_budget_selector_all_groups_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p775_public_budget_selector_holdout_transfer_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p775_public_budget_selector_holdout_transfer.md"
SCHEMA = "ecdlp.low_term_total2_p775_public_budget_selector_holdout_transfer.v1"

HOLDOUT_TARGETS = [
    "67.a1@9829",
    "114224.v1@9613",
    "21175.bc1@8467",
    "22050.cf1@10321",
]
BASE_BUDGETS = {
    "67.a1@9829": 66,
    "114224.v1@9613": 64,
    "21175.bc1@8467": 60,
    "22050.cf1@10321": 66,
}
TARGET_TAGS = {
    "67.a1@9829": "67a9829",
    "114224.v1@9613": "114224v9613",
    "21175.bc1@8467": "21175b8467",
    "22050.cf1@10321": "22050c10321",
}
P774_CALIBRATION_TARGETS = {
    "114224.v1@9341",
    "21175.bc1@8089",
    "22050.cf1@10531",
    "23232.cr1@8467",
    "23232.cr1@9643",
    "67.a1@11923",
    "67.a1@9803",
}


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


def target_records(path: Path) -> dict[str, dict[str, Any]]:
    payload = load_json(path)
    return {
        str(item["target"]): item
        for item in payload.get("candidates") or []
    }


def holdout_metadata(path: Path) -> list[dict[str, Any]]:
    records = target_records(path)
    out = []
    for target in HOLDOUT_TARGETS:
        item = records.get(target)
        if not item:
            raise RuntimeError(f"missing holdout target {target} in {path}")
        if item.get("precomputed_target"):
            raise RuntimeError(f"holdout target {target} is precomputed")
        if item.get("known_success_target"):
            raise RuntimeError(f"holdout target {target} is a known success")
        if int(item.get("base_order") or 0) == 11779:
            raise RuntimeError(f"holdout target {target} has excluded base order 11779")
        if target in P774_CALIBRATION_TARGETS:
            raise RuntimeError(f"holdout target {target} is in P774 calibration set")
        out.append(
            {
                "base_order": item.get("base_order"),
                "base_budget": BASE_BUDGETS[target],
                "generic_rho_steps": item.get("generic_rho_steps"),
                "priority_score": item.get("priority_score"),
                "reasons": item.get("reasons") or [],
                "target": target,
                "verifier_invariant_score": item.get("verifier_invariant_score"),
            }
        )
    return out


def default_cases(frontier: Path, deltas: list[int]) -> str:
    entries = []
    for meta in holdout_metadata(frontier):
        target = meta["target"]
        tag = TARGET_TAGS[target]
        for factor_base_size in (96, 112):
            factor_bucket = f"fb{factor_base_size}"
            for delta in deltas:
                budget = max(1, int(meta["base_budget"]) + int(delta))
                dtag = delta_tag(int(delta))
                label = f"{factor_bucket}_s1024_{dtag}_{tag}"
                entries.append(
                    "|".join(
                        [
                            label,
                            target,
                            str(budget),
                            str(factor_base_size),
                            "1024",
                            "1152",
                            "1152",
                            f"ecdlp-p775-{factor_bucket}-s1024-{dtag}-{tag}-v1",
                            f"{factor_bucket}_s1024_{dtag}",
                        ]
                    )
                )
    return ",".join(entries)


def weight_cost(item: dict[str, Any], key: str = "costs_by_field_weight", weight: int = 2) -> dict[str, Any]:
    for cost in item.get(key) or []:
        if int(cost.get("field_op_weight") or 0) == weight:
            return cost
    return {}


def selected_sparse(item: dict[str, Any]) -> dict[str, Any]:
    return item["public_selector_sparse_policy"]


def weight2_total(item: dict[str, Any]) -> float | None:
    value = weight_cost(item).get("total_unit_cost_over_selected_rho")
    return float(value) if value is not None else None


def public_weight2_total(item: dict[str, Any]) -> float | None:
    value = weight_cost(item, "public_costs_by_field_weight").get("total_unit_cost_over_selected_rho")
    return float(value) if value is not None else None


def group_key(item: dict[str, Any]) -> str:
    return f"fb{int(item['factor_base_size'])}|{item['target']}"


def factor_bucket(item: dict[str, Any]) -> str:
    return f"fb{int(item['factor_base_size'])}"


def budget_delta(item: dict[str, Any]) -> int:
    return int(item["budget"]) - int(BASE_BUDGETS[str(item["target"])])


def sparse_gap(item: dict[str, Any]) -> bool:
    return bool(item["oracle_best_pass_weight2_below_rho"] and not item["public_selector_pass_weight2_below_rho"])


def capacity_ok(item: dict[str, Any]) -> bool:
    support = item.get("selected_relation_support_stats") or {}
    return (
        int(item.get("selected_exported_factor_count") or 0) == int(item["factor_base_size"])
        and int(support.get("active_column_count") or 0) == int(item["factor_base_size"])
    )


def recovery_ok(item: dict[str, Any]) -> bool:
    sparse = selected_sparse(item)
    return bool(
        item["public_selector_recovery_ok"]
        and int((sparse.get("solve") or {}).get("rank") or 0) == int(item["factor_base_size"])
        and int((sparse.get("substitution") or {}).get("recovered_count") or 0) == int(item["selected_count"])
        and int((sparse.get("substitution") or {}).get("mismatch_count") or 0) == 0
    )


def strict_pass(item: dict[str, Any]) -> bool:
    return item.get("failure_class") == "pass"


def select_budget_candidate(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    return min(
        candidates,
        key=lambda item: (
            public_weight2_total(selected_sparse(item)) or inf,
            -(float(selected_sparse(item).get("public_max_field_op_weight_below_selected_rho") or 0.0)),
            budget_delta(item),
            item["case"],
        ),
    )


def slim_candidate(item: dict[str, Any]) -> dict[str, Any]:
    sparse = selected_sparse(item)
    weight2 = weight_cost(sparse)
    public_weight2 = weight_cost(sparse, "public_costs_by_field_weight")
    support = item.get("selected_relation_support_stats") or {}
    solve = sparse.get("solve") or {}
    substitution = sparse.get("substitution") or {}
    return {
        "active_column_count": support.get("active_column_count"),
        "arm": item.get("arm"),
        "budget": item["budget"],
        "budget_delta": budget_delta(item),
        "capacity_ok": capacity_ok(item),
        "case": item["case"],
        "exported_factor_count": item.get("selected_exported_factor_count"),
        "factor_bucket": factor_bucket(item),
        "failure_class": item.get("failure_class"),
        "group_key": group_key(item),
        "max_field_op_weight_below_selected_rho": sparse.get("max_field_op_weight_below_selected_rho"),
        "mismatch_count": substitution.get("mismatch_count"),
        "oracle_best_policy": ((item.get("oracle_best_sparse_policy") or {}).get("sparse_policy")),
        "oracle_best_weight2": weight2_total(item.get("oracle_best_sparse_policy") or {}),
        "oracle_pass": bool(item.get("oracle_best_pass_weight2_below_rho")),
        "public_policy": sparse.get("sparse_policy"),
        "public_sparse_selector_gap": sparse_gap(item),
        "public_weight2": public_weight2.get("total_unit_cost_over_selected_rho"),
        "rank": solve.get("rank"),
        "recovered_count": substitution.get("recovered_count"),
        "recovery_ok": recovery_ok(item),
        "scanned_count": item.get("scanned_count"),
        "selected_count": item.get("selected_count"),
        "solve_field_ops": (solve.get("operation_counts") or {}).get("total_field_ops"),
        "strict_pass": strict_pass(item),
        "substitution_field_ops": (substitution.get("operation_counts") or {}).get("total_field_ops"),
        "target": item.get("target"),
        "verified_weight2": weight2.get("total_unit_cost_over_selected_rho"),
    }


def summarize_candidates(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    weights = [weight2_total(selected_sparse(item)) for item in candidates]
    weights = [float(value) for value in weights if value is not None]
    deltas = Counter(str(budget_delta(item)) for item in candidates)
    return {
        "capacity_ok_count": sum(1 for item in candidates if capacity_ok(item)),
        "case_count": len(candidates),
        "delta_counts": {key: deltas[key] for key in sorted(deltas, key=lambda value: int(value))},
        "max_weight2": max(weights) if weights else None,
        "min_weight2": min(weights) if weights else None,
        "recovery_ok_count": sum(1 for item in candidates if recovery_ok(item)),
        "sparse_gap_count": sum(1 for item in candidates if sparse_gap(item)),
        "strict_pass_count": sum(1 for item in candidates if strict_pass(item)),
    }


def fixed_delta_baselines(groups: dict[str, list[dict[str, Any]]], deltas: list[int]) -> dict[str, dict[str, Any]]:
    out = {}
    for delta in deltas:
        selected = []
        for candidates in groups.values():
            by_delta = {budget_delta(item): item for item in candidates}
            selected.append(by_delta[delta])
        out[f"delta_{delta}"] = summarize_candidates(selected)
    return out


def bucket_summary(selected_groups: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for group in selected_groups:
        selected = group["selected_candidate"]
        bucket_key = str(selected[key])
        bucket = out.setdefault(
            bucket_key,
            {
                "budget_gap_count": 0,
                "capacity_ok_count": 0,
                "case_count": 0,
                "recovery_ok_count": 0,
                "strict_pass_count": 0,
            },
        )
        bucket["budget_gap_count"] += int(group["budget_selector_gap"])
        bucket["capacity_ok_count"] += int(selected["capacity_ok"])
        bucket["case_count"] += 1
        bucket["recovery_ok_count"] += int(selected["recovery_ok"])
        bucket["strict_pass_count"] += int(selected["strict_pass"])
    return out


def p774_control(path: Path) -> dict[str, Any]:
    payload = load_json(path)
    summary = payload.get("summary") or {}
    return {
        "budget_selector_gap_count": summary.get("budget_selector_gap_count"),
        "candidate_sparse_selector_gap_count": summary.get("candidate_sparse_selector_gap_count"),
        "claim_status": payload.get("claim_status"),
        "group_count": summary.get("group_count"),
        "selected_strict_pass_count": summary.get("selected_strict_pass_count"),
        "selected_weight2_max": summary.get("selected_weight2_max"),
        "selected_weight2_min": summary.get("selected_weight2_min"),
    }


def determine_claim(summary: dict[str, Any]) -> str:
    total = int(summary["group_count"])
    selected_pass = int(summary["selected_strict_pass_count"])
    recovery = int(summary["selected_recovery_ok_count"])
    capacity = int(summary["selected_capacity_ok_count"])
    sparse_gaps = int(summary["candidate_sparse_selector_gap_count"])
    budget_gaps = int(summary["budget_selector_gap_count"])
    if selected_pass == total and recovery == total and capacity == total and sparse_gaps == 0 and budget_gaps == 0:
        return "P775_PUBLIC_BUDGET_SELECTOR_HOLDOUT_ALL_GROUP_SIGNAL"
    if budget_gaps:
        return "P775_PUBLIC_BUDGET_SELECTOR_HOLDOUT_BUDGET_GAP"
    if sparse_gaps:
        return "P775_PUBLIC_BUDGET_SELECTOR_HOLDOUT_SPARSE_GAP"
    if selected_pass >= max(1, total - 2) and recovery == total and capacity == total:
        return "P775_PUBLIC_BUDGET_SELECTOR_HOLDOUT_USEFUL_SIGNAL"
    if capacity < total:
        return "P775_PUBLIC_BUDGET_SELECTOR_HOLDOUT_CAPACITY_REGRESSION"
    if recovery == total:
        return "P775_PUBLIC_BUDGET_SELECTOR_HOLDOUT_RECOVERY_OK_COST_NEGATIVE"
    return "NEGATIVE_RESULT_P775_PUBLIC_BUDGET_SELECTOR_HOLDOUT_TRANSFER"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p764 = load_module("ecdlp_p764_for_p775", P764_SCRIPT)
    deltas = csv_ints(args.budget_deltas)
    cases_text = args.cases or default_cases(args.frontier_targets, deltas)
    p764_args = argparse.Namespace(
        arm_threshold=1,
        cases=cases_text,
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
    groups: dict[str, list[dict[str, Any]]] = {}
    for item in cases:
        groups.setdefault(group_key(item), []).append(item)
    groups = dict(sorted(groups.items()))
    selected_groups = []
    for key, candidates in groups.items():
        selected = select_budget_candidate(candidates)
        any_pass = any(strict_pass(item) for item in candidates)
        pass_weights = [
            weight2_total(selected_sparse(item))
            for item in candidates
            if strict_pass(item) and weight2_total(selected_sparse(item)) is not None
        ]
        selected_groups.append(
            {
                "budget_selector_gap": bool(any_pass and not strict_pass(selected)),
                "candidate_count": len(candidates),
                "candidate_deltas": {
                    str(budget_delta(item)): {
                        "public_policy": selected_sparse(item).get("sparse_policy"),
                        "public_weight2": public_weight2_total(selected_sparse(item)),
                        "strict_pass": strict_pass(item),
                        "verified_weight2": weight2_total(selected_sparse(item)),
                    }
                    for item in sorted(candidates, key=budget_delta)
                },
                "group_key": key,
                "has_passing_budget": any_pass,
                "oracle_best_pass_weight2": min(pass_weights) if pass_weights else None,
                "public_best_weight2": min(
                    public_weight2_total(selected_sparse(item)) or inf for item in candidates
                ),
                "selected_candidate": slim_candidate(selected),
            }
        )
    selected = [group["selected_candidate"] for group in selected_groups]
    selected_weights = [float(item["verified_weight2"]) for item in selected if item["verified_weight2"] is not None]
    summary = {
        "budget_delta_baselines": fixed_delta_baselines(groups, deltas),
        "budget_selector_gap_count": sum(1 for group in selected_groups if group["budget_selector_gap"]),
        "candidate_case_count": len(cases),
        "candidate_sparse_selector_gap_count": sum(1 for item in cases if sparse_gap(item)),
        "delta_summaries": {
            f"delta_{delta}": summarize_candidates([item for item in cases if budget_delta(item) == delta])
            for delta in deltas
        },
        "factor_summaries": bucket_summary(selected_groups, "factor_bucket"),
        "frontier_holdout_targets": holdout_metadata(args.frontier_targets),
        "group_count": len(selected_groups),
        "selected_capacity_ok_count": sum(1 for item in selected if item["capacity_ok"]),
        "selected_delta_counts": dict(sorted(Counter(str(item["budget_delta"]) for item in selected).items(), key=lambda pair: int(pair[0]))),
        "selected_groups": selected_groups,
        "selected_recovery_ok_count": sum(1 for item in selected if item["recovery_ok"]),
        "selected_strict_pass_count": sum(1 for item in selected if item["strict_pass"]),
        "selected_weight2_max": max(selected_weights) if selected_weights else None,
        "selected_weight2_min": min(selected_weights) if selected_weights else None,
        "target_summaries": bucket_summary(selected_groups, "target"),
        "unresolved_selected_groups": [
            {
                "group_key": group["group_key"],
                "selected_delta": group["selected_candidate"]["budget_delta"],
                "selected_weight2": group["selected_candidate"]["verified_weight2"],
            }
            for group in selected_groups
            if not group["selected_candidate"]["strict_pass"]
        ],
    }
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "frontier_targets": str(args.frontier_targets),
            "p774_summary": str(args.p774_summary),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(summary),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "HOLDOUT-TRANSFER: targets are non-precomputed frontier candidates outside the P772/P774 calibration set.",
            "PUBLIC-SELECTION: sparse policy and budget candidate are selected from public cost features before substitution verification.",
            "PRIVATE-VERIFY-ONLY: expected secrets are used only after public selection to verify recovery and mismatches.",
            "SCANNED-POOL-CHARGED: replacement policies pay group cost for all scanned candidate rows.",
            "SPARSE-WEIGHT MODEL: field-operation weights are accounting stress tests, not calibrated hardware timings.",
            "NO DEPLOYED-CURVE CLAIM: no large-prime scaling or production-key relevance is implied.",
        ],
        "method": "p775_public_budget_selector_holdout_transfer",
        "p764_payload": p764_payload,
        "p774_control": p774_control(args.p774_summary),
        "parameters": {
            "budget_deltas": deltas,
            "case_count": len(cases),
            "factor_base_sizes": [96, 112],
            "field_weights": csv_ints(args.field_weights),
            "holdout_targets": HOLDOUT_TARGETS,
            "max_relations": args.max_relations,
            "max_subsets": args.max_subsets,
            "public_substitution_ops_per_selected": args.public_substitution_ops_per_selected,
            "row_policy": args.row_policy,
            "seed_count": 1152,
            "selected_count": 1024,
            "sparse_policies": [item.strip() for item in args.sparse_policies.split(",") if item.strip()],
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
                "unresolved_selected_groups": summary["summary"]["unresolved_selected_groups"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
