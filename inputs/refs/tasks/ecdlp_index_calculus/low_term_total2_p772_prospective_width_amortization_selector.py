#!/usr/bin/env python3
"""P772 prospective public selector over fresh width-amortization arms."""

from __future__ import annotations

import argparse
import importlib.util
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P770_SCRIPT = TASK_DIR / "low_term_total2_p770_width_amortization_cost_miss_sweep.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P760_SUMMARY = STATE_DIR / "low_term_total2_p760_public_sparse_policy_selector_summary.json"
DEFAULT_P763_SUMMARY = STATE_DIR / "low_term_total2_p763_factor_base_limit_extension_smoke_summary.json"
DEFAULT_P767_SUMMARY = STATE_DIR / "low_term_total2_p767_disjoint_seed_target_extension_holdout_summary.json"
DEFAULT_P768_SUMMARY = STATE_DIR / "low_term_total2_p768_frozen_trim8_extension_sweep_summary.json"
DEFAULT_P769_SUMMARY = STATE_DIR / "low_term_total2_p769_frozen_trim8_width_stress_summary.json"
DEFAULT_P771_SUMMARY = STATE_DIR / "low_term_total2_p771_public_width_amortization_selector_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p772_prospective_width_amortization_selector_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p772_prospective_width_amortization_selector.md"
SCHEMA = "ecdlp.low_term_total2_p772_prospective_width_amortization_selector.v1"


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


def weight2_total(p770: Any, item: dict[str, Any]) -> float:
    return float(p770.weight2_total(item["public_selector_sparse_policy"]))


def public_max_weight(item: dict[str, Any]) -> float:
    return float(item["public_selector_sparse_policy"].get("max_field_op_weight_below_selected_rho") or 0.0)


def factor_bucket(item: dict[str, Any]) -> str:
    return f"fb{int(item['factor_base_size'])}"


def group_key(item: dict[str, Any]) -> str:
    return f"{factor_bucket(item)}|{item['target']}"


def candidate_from_case(p770: Any, item: dict[str, Any]) -> dict[str, Any]:
    sparse = item["public_selector_sparse_policy"]
    support = item["selected_relation_support_stats"]
    candidate = {
        "active_column_count": support["active_column_count"],
        "arm": str(item["amortization_arm"]),
        "candidate_id": f"{factor_bucket(item)}_{item['amortization_arm']}_{item['target']}",
        "case": item["case"],
        "exported_factor_count": item["selected_exported_factor_count"],
        "factor_base_size": item["factor_base_size"],
        "factor_bucket": factor_bucket(item),
        "failure_class": item["failure_class"],
        "group_key": group_key(item),
        "mismatch_count": sparse["substitution"]["mismatch_count"],
        "policy": sparse["sparse_policy"],
        "public_max_field_op_weight_below_selected_rho": public_max_weight(item),
        "public_weight2_total_over_selected_rho": weight2_total(p770, item),
        "rank": sparse["solve"]["rank"],
        "recovered_count": sparse["substitution"]["recovered_count"],
        "scanned_count": item["scanned_count"],
        "selected_count": item["selected_count"],
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


def summarize_candidates(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    weights = [item["public_weight2_total_over_selected_rho"] for item in candidates]
    arm_counts = Counter(item["arm"] for item in candidates)
    return {
        "arm_counts": {key: arm_counts[key] for key in sorted(arm_counts)},
        "case_count": len(candidates),
        "capacity_ok_count": sum(1 for item in candidates if item["capacity_ok"]),
        "max_weight2": max(weights) if weights else None,
        "min_weight2": min(weights) if weights else None,
        "recovery_ok_count": sum(1 for item in candidates if item["recovery_ok"]),
        "strict_pass_count": sum(1 for item in candidates if item["strict_pass"]),
    }


def fixed_baselines(groups: dict[str, list[dict[str, Any]]]) -> dict[str, dict[str, Any]]:
    out = {}
    for arm in ("s768", "s896", "s1024"):
        selected = []
        for candidates in groups.values():
            by_arm = {item["arm"]: item for item in candidates}
            selected.append(by_arm[arm])
        out[f"fixed_{arm}"] = summarize_candidates(selected)
    return out


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


def prior_control(path: Path) -> dict[str, Any]:
    payload = load_json(path)
    summary = payload.get("summary") or {}
    return {
        "best_fixed_baseline_pass_count": summary.get("best_fixed_baseline_pass_count"),
        "claim_status": payload.get("claim_status"),
        "group_count": summary.get("group_count"),
        "selected_strict_pass_count": summary.get("selected_strict_pass_count"),
        "selector_gap_count": summary.get("selector_gap_count"),
    }


def determine_claim(summary: dict[str, Any], args: argparse.Namespace) -> str:
    total = int(summary["group_count"])
    selected_pass = int(summary["selected_strict_pass_count"])
    recovery = int(summary["selected_recovery_ok_count"])
    capacity = int(summary["selected_capacity_ok_count"])
    gaps = int(summary["selector_gap_count"])
    best_fixed = int(summary["best_fixed_baseline_pass_count"])
    if total and selected_pass == total:
        return "P772_PROSPECTIVE_WIDTH_AMORTIZATION_SELECTOR_ALL_CASE_SIGNAL"
    if (
        selected_pass >= int(args.primary_threshold)
        and recovery == total
        and capacity == total
        and gaps == 0
        and selected_pass > best_fixed
    ):
        return "P772_PROSPECTIVE_WIDTH_AMORTIZATION_SELECTOR_PRIMARY_SIGNAL"
    if selected_pass > int(summary["fixed_baselines"]["fixed_s768"]["strict_pass_count"]) and recovery == total and capacity == total and gaps == 0:
        return "P772_PROSPECTIVE_WIDTH_AMORTIZATION_SELECTOR_USEFUL_SIGNAL"
    if recovery == total and capacity == total:
        return "P772_PROSPECTIVE_WIDTH_AMORTIZATION_SELECTOR_RECOVERY_OK_COST_NEGATIVE"
    if capacity < total:
        return "P772_PROSPECTIVE_WIDTH_AMORTIZATION_SELECTOR_CAPACITY_REGRESSION"
    return "NEGATIVE_RESULT_P772_PROSPECTIVE_WIDTH_AMORTIZATION_SELECTOR"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p770 = load_module("ecdlp_p770_width_amortization_cost_miss_sweep", P770_SCRIPT)
    candidate_payload = p770.analyze(args)
    groups: dict[str, list[dict[str, Any]]] = {}
    for item in candidate_payload["summary"]["case_summaries"]:
        candidate = candidate_from_case(p770, item)
        groups.setdefault(candidate["group_key"], []).append(candidate)
    groups = dict(sorted(groups.items()))
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
    unresolved = [group for group in selected_groups if not group["has_oracle_pass"]]
    summary = {
        "best_fixed_baseline_pass_count": best_fixed,
        "candidate_arm_summaries": {
            arm: summarize_candidates([item for candidates in groups.values() for item in candidates if item["arm"] == arm])
            for arm in ("s768", "s896", "s1024")
        },
        "candidate_case_count": sum(len(candidates) for candidates in groups.values()),
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
            "p771_summary": str(args.p771_summary),
            "script": str(Path(__file__)),
        },
        "candidate_payload": candidate_payload,
        "claim_status": determine_claim(summary, args),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "PROSPECTIVE-COLLECTION: all s768/s896/s1024 candidates use fresh P772 seed prefixes.",
            "PUBLIC-SELECTION: selected-count choice uses public cost/rank/row features before verification.",
            "PRIVATE-VERIFY-ONLY: failure class, recovered count, and mismatches are used only after selection.",
            "WIDENED-FACTOR-BASIS: requested fb96/fb112 must be exported and active before cost interpretation.",
            "NO DEPLOYED-CURVE CLAIM: no large-prime scaling or production-key relevance is implied.",
        ],
        "method": "p772_prospective_width_amortization_selector",
        "p771_control": prior_control(args.p771_summary),
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
        "p771_control": payload["p771_control"],
        "parameters": payload["parameters"],
        "summary": summary,
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
    arms = [
        ("s768", 768, 896, 896),
        ("s896", 896, 1024, 1024),
        ("s1024", 1024, 1152, 1152),
    ]
    entries = []
    for arm, selected, seed_count, pool_count in arms:
        for factor_base_size in (96, 112):
            for target, budget, tag in targets:
                actual_budget = max(1, budget - 8)
                entries.append(
                    f"fb{factor_base_size}_{arm}_{tag}|{target}|{actual_budget}|{factor_base_size}|{selected}|{seed_count}|{pool_count}|ecdlp-p772-fb{factor_base_size}-{arm}-trim8-{tag}-v1|fb{factor_base_size}_{arm}"
                )
    return ",".join(entries)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", default=default_cases())
    parser.add_argument("--p760-summary", type=Path, default=DEFAULT_P760_SUMMARY)
    parser.add_argument("--p763-summary", type=Path, default=DEFAULT_P763_SUMMARY)
    parser.add_argument("--p767-summary", type=Path, default=DEFAULT_P767_SUMMARY)
    parser.add_argument("--p768-summary", type=Path, default=DEFAULT_P768_SUMMARY)
    parser.add_argument("--p769-summary", type=Path, default=DEFAULT_P769_SUMMARY)
    parser.add_argument("--p771-summary", type=Path, default=DEFAULT_P771_SUMMARY)
    parser.add_argument("--row-policy", default="sequential_min_forms_ge_1")
    parser.add_argument("--sparse-policies", default="natural,support_asc,support_span_asc,pivot_low,pivot_high,coefficient_weight_asc")
    parser.add_argument("--width", type=int, default=2)
    parser.add_argument("--walk-mode", default="hash6")
    parser.add_argument("--max-relations", type=int, default=96)
    parser.add_argument("--max-subsets", type=int, default=25000)
    parser.add_argument("--field-weights", default="1,2")
    parser.add_argument("--public-substitution-ops-per-selected", type=int, default=6)
    parser.add_argument("--primary-threshold", type=int, default=13)
    parser.add_argument("--arm-threshold", type=int, default=4)
    parser.add_argument("--arm-useful-threshold", type=int, default=4)
    parser.add_argument("--factor-threshold", type=int, default=6)
    parser.add_argument("--factor-majority-threshold", type=int, default=4)
    parser.add_argument("--new-extension-threshold", type=int, default=3)
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
                "candidate_arm_summaries": summary["summary"]["candidate_arm_summaries"],
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
