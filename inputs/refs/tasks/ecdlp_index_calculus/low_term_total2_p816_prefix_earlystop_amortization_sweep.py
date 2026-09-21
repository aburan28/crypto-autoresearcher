#!/usr/bin/env python3
"""P816 prefix-length and early-stop amortization sweep for ECDLP gates."""

from __future__ import annotations

import argparse
import importlib.util
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P815_SCRIPT = TASK_DIR / "low_term_total2_p815_gated_continuation_budget_sweep.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P777_SUMMARY = STATE_DIR / "low_term_total2_p777_merged_trim12_factor_first_cost_audit_summary.json"
DEFAULT_P786_SUMMARY = STATE_DIR / "low_term_total2_p786_public_coordinate_bridge_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p816_prefix_earlystop_amortization_sweep_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p816_prefix_earlystop_amortization_sweep.md"
SCHEMA = "ecdlp.low_term_total2_p816_prefix_earlystop_amortization_sweep.v1"
PREFIX_POLICY = "prefix_all_pair"
SPAN_POLICY = "prefix_span_top"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {name} from {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def csv_floats(text: str) -> list[float]:
    return [float(item.strip()) for item in text.split(",") if item.strip()]


def threshold_suffix(value: float) -> str:
    return f"{int(round(float(value) * 100)):03d}"


def prefix_span_concentration(p815: Any, stats: dict[str, Any], top_span_bins: int) -> dict[str, Any]:
    top_spans = p815.top_keys(stats["span_counts"], int(top_span_bins))
    top_hits = sum(int(stats["span_counts"][key]) for key in top_spans)
    total = int(stats["record_count"])
    return {
        "span_concentration": p815.ratio(top_hits, total),
        "top_span_bins": sorted(int(key) for key in top_spans),
        "top_span_hit_count": int(top_hits),
        "total_prefix_record_count": total,
    }


def policy_prefix_count(item: dict[str, Any]) -> int:
    return int(item["policy"].get("prefix_seed_count") or 0)


def policy_continuation_budget(item: dict[str, Any]) -> int:
    return int(item["policy"].get("continuation_budget") or 0)


def policy_key(item: dict[str, Any]) -> tuple[int, int]:
    return (policy_prefix_count(item), policy_continuation_budget(item))


def best_result(results: list[dict[str, Any]], kinds: set[str]) -> dict[str, Any] | None:
    candidates = [
        item
        for item in results
        if item["policy"]["kind"] in kinds
        and item["aggregate"]["post_hit_scan_once_train_total_unit_cost_over_recovered_rho"] is not None
    ]
    if not candidates:
        return None
    return min(candidates, key=lambda item: item["aggregate"]["post_hit_scan_once_train_total_unit_cost_over_recovered_rho"])


def compact_policy_result(p815: Any, p812: Any, item: dict[str, Any] | None) -> dict[str, Any] | None:
    return None if item is None else p815.compact_policy_result(p812, item)


def determine_policy_claim(
    item: dict[str, Any],
    full_pool_by_key: dict[tuple[int, int], dict[str, Any]],
    best_hash_by_key: dict[tuple[int, int], dict[str, Any] | None],
) -> str:
    aggregate = item["aggregate"]
    kind = item["policy"]["kind"]
    recovered = int(aggregate["recovered_row_count"])
    if recovered <= int(aggregate["max_control_recovered_row_count"]):
        return "does_not_beat_rotated_line_controls"
    ratio_value = aggregate["post_hit_scan_once_train_total_unit_cost_over_recovered_rho"]
    if kind in {"adaptive_prefix_gate", "early_stop_gate"} and ratio_value is not None and ratio_value < 1.0:
        return f"{kind}_below_rho"
    key = policy_key(item)
    if kind in {"adaptive_prefix_gate", "early_stop_gate"} and key in full_pool_by_key:
        full_pool = full_pool_by_key[key]
        best_hash = best_hash_by_key.get(key)
        full_ratio = full_pool["aggregate"]["post_hit_scan_once_train_total_unit_cost_over_recovered_rho"]
        hash_recovered = 0 if best_hash is None else int(best_hash["aggregate"]["recovered_row_count"])
        if ratio_value is not None and full_ratio is not None and ratio_value < full_ratio and recovered > hash_recovered:
            return f"{kind}_improves_same_prefix_full_pool"
    if kind == "hash_control":
        return "hash_control_boundary"
    if kind == "full_pool":
        return "full_pool_boundary"
    return "adaptive_boundary"


def determine_claim(results: list[dict[str, Any]]) -> str:
    claims = {str(item.get("policy_claim")) for item in results}
    if "early_stop_gate_below_rho" in claims:
        return "P816_EARLY_STOP_GATE_BELOW_RHO"
    if "adaptive_prefix_gate_below_rho" in claims:
        return "P816_PREFIX_GATE_BELOW_RHO"
    if "early_stop_gate_improves_same_prefix_full_pool" in claims:
        return "P816_EARLY_STOP_IMPROVES_SAME_PREFIX_FULL_POOL"
    if "adaptive_prefix_gate_improves_same_prefix_full_pool" in claims:
        return "P816_PREFIX_GATE_IMPROVES_SAME_PREFIX_FULL_POOL"
    return "NEGATIVE_RESULT_P816_PREFIX_EARLYSTOP_FAILS"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p815 = load_module("ecdlp_p815_for_p816", P815_SCRIPT)
    p812 = p815.load_module("ecdlp_p812_for_p816", p815.P812_SCRIPT)
    p805 = p812.load_module("ecdlp_p805_for_p816", p812.P805_SCRIPT)
    p806 = p812.load_module("ecdlp_p806_for_p816", p812.P806_SCRIPT)
    p807 = p812.load_module("ecdlp_p807_for_p816", p812.P807_SCRIPT)
    p808 = p812.load_module("ecdlp_p808_for_p816", p812.P808_SCRIPT)
    p807.configure_p807(p806)

    modules = p808.load_research_stack(p806)
    p801 = modules["p801"]
    p800 = p801.load_module("ecdlp_p800_for_p816", p801.P800_SCRIPT)
    p799 = p800.load_module("ecdlp_p799_for_p816", p800.P799_SCRIPT)
    p798 = p799.load_module("ecdlp_p798_for_p816", p799.P798_SCRIPT)
    p797 = p798.load_module("ecdlp_p797_for_p816", p798.P797_SCRIPT)
    p784 = modules["p784"]
    p787 = modules["p787"]
    p788 = modules["p788"]
    p794 = modules["p794"]
    p795 = modules["p795"]
    p793 = modules["p793"]
    p792 = modules["p792"]
    p789 = modules["p789"]
    stack = modules["stack"]
    p746 = stack["p746"]
    p748 = stack["p748"]
    relprobe = stack["relprobe"]

    frozen_pairs = p788.selected_frozen_pairs(p787, args.p786_summary)
    required = sorted({item["dest_group_key"] for item in frozen_pairs})
    base_groups = p784.normalized_groups(args.p777_summary, required)
    namespaces = p815.csv_strings(args.constructor_namespaces)
    calibration_budget = int(args.calibration_budget)
    prefix_counts = sorted({int(value) for value in p815.csv_ints(args.prefix_seed_counts)})
    continuation_budgets = sorted({int(value) for value in p815.csv_ints(args.continuation_budgets)})
    early_thresholds = sorted({float(value) for value in csv_floats(args.early_stop_span_thresholds)})
    scan_seed_count = int(args.scan_seed_count)
    prefix_trial_budget = int(args.prefix_trial_budget)
    if not prefix_counts:
        raise ValueError("--prefix-seed-counts must include at least one value")
    if not continuation_budgets:
        raise ValueError("--continuation-budgets must include at least one value")
    if max(prefix_counts) >= scan_seed_count:
        raise ValueError("--scan-seed-count must exceed every prefix seed count")

    train_args = p795.namespace_args(args, args.train_seed_namespace, int(args.train_replicas))
    train_prepared = {}
    for group_key in required:
        print(f"preparing train namespace {args.train_seed_namespace} group={group_key}", flush=True)
        train_prepared[group_key] = p794.prepare_target(
            p793,
            p792,
            p789,
            p787,
            p784,
            stack,
            base_groups[group_key],
            train_args,
        )
    trained_by_group = {
        group_key: p794.selected_calibrations(train_prepared[group_key]["all_calibrated"], calibration_budget)
        for group_key in required
    }

    contexts_by_policy: dict[tuple[str, int, int], dict[str, dict[str, Any]]] = defaultdict(dict)
    context_diagnostics = []
    support_diagnostics = []
    for namespace in namespaces:
        for group_key in required:
            print(f"building P816 base context namespace={namespace} group={group_key}", flush=True)
            context = p806.build_public_context(
                p801,
                p746,
                relprobe,
                base_groups[group_key],
                {calibration_budget: trained_by_group[group_key]},
                [calibration_budget],
                namespace,
                args,
            )
            base_context_id = p812.context_id(namespace, group_key)
            context["context_id"] = base_context_id
            all_pairs = p801.all_support_pairs(int(context["factor_base_size"]))
            max_prefix_count = max(prefix_counts)
            prefix_rows_by_policy, prefix_stats = p815.scan_seed_range(
                p812,
                p805,
                p801,
                p746,
                p748,
                relprobe,
                context,
                {(0, PREFIX_POLICY): all_pairs},
                (PREFIX_POLICY,),
                0,
                max_prefix_count,
                [prefix_trial_budget],
                args,
            )
            max_prefix_rows = prefix_rows_by_policy[(PREFIX_POLICY, prefix_trial_budget)]
            prefix_setup_stats = prefix_stats[(0, PREFIX_POLICY)]
            setup_stats = {
                "targeted_setup_group_additions": int(prefix_setup_stats["targeted_setup_group_additions"]),
                "targeted_support_count": int(prefix_setup_stats["targeted_support_count"]),
                "targeted_unique_point_count": int(prefix_setup_stats["targeted_unique_point_count"]),
                "targeted_point_collision_count": int(prefix_setup_stats["targeted_point_collision_count"]),
            }
            for prefix_count in prefix_counts:
                continuation_count = scan_seed_count - int(prefix_count)
                prefix_rows = max_prefix_rows[: int(prefix_count)]
                stats = p815.prefix_support_stats(
                    p812,
                    p793,
                    p792,
                    p789,
                    prefix_rows,
                    int(context["order"]),
                    str(context["target"]),
                    int(context["factor_base_size"]),
                    int(args.feature_bins),
                )
                span_info = prefix_span_concentration(p815, stats, int(args.top_span_bins))
                support_sets, support_rows = p815.support_sets_from_prefix(p812, p801, context, prefix_rows, stats, args)
                policy_names = tuple(sorted(support_sets))
                continuation_rows_by_policy, _continuation_stats = p815.scan_seed_range(
                    p812,
                    p805,
                    p801,
                    p746,
                    p748,
                    relprobe,
                    context,
                    {(0, name): supports for name, supports in support_sets.items()},
                    policy_names,
                    int(prefix_count),
                    continuation_count,
                    continuation_budgets,
                    args,
                )
                passed_thresholds = [
                    threshold
                    for threshold in early_thresholds
                    if (span_info["span_concentration"] is not None and float(span_info["span_concentration"]) >= threshold)
                ]
                context_diagnostics.append(
                    {
                        **span_info,
                        "context_id": base_context_id,
                        "continuation_budgets": continuation_budgets,
                        "continuation_seed_count": continuation_count,
                        "early_stop_span_thresholds": early_thresholds,
                        "group_key": group_key,
                        "namespace": namespace,
                        "passed_early_stop_thresholds": passed_thresholds,
                        "prefix_seed_count": int(prefix_count),
                        "prefix_trial_budget": prefix_trial_budget,
                        "target": str(context["target"]),
                        "targeted_setup_group_additions": int(prefix_setup_stats["targeted_setup_group_additions"]),
                    }
                )
                for row in support_rows:
                    support_diagnostics.append(
                        {
                            **row,
                            "context_id": base_context_id,
                            "group_key": group_key,
                            "namespace": namespace,
                            "prefix_seed_count": int(prefix_count),
                            "span_concentration": span_info["span_concentration"],
                        }
                    )
                for threshold in early_thresholds:
                    gate_name = f"prefix_span_top_gate_ge{threshold_suffix(threshold)}"
                    gate_pass = threshold in passed_thresholds
                    support_diagnostics.append(
                        {
                            "context_id": base_context_id,
                            "early_stop_threshold": threshold,
                            "gate_pass": gate_pass,
                            "group_key": group_key,
                            "namespace": namespace,
                            "policy": gate_name,
                            "prefix_record_count": int(stats["record_count"]),
                            "prefix_row_count": len(prefix_rows),
                            "prefix_seed_count": int(prefix_count),
                            "selected_support_count": len(support_sets[SPAN_POLICY]) if gate_pass else 0,
                            "span_concentration": span_info["span_concentration"],
                        }
                    )
                for budget in continuation_budgets:
                    for policy_name in policy_names:
                        continuation_rows = continuation_rows_by_policy[(policy_name, int(budget))]
                        budget_namespace = f"{namespace}:p{prefix_count}:b{budget}"
                        prepared_context = p815.prepare_combined_policy_context(
                            p812,
                            p793,
                            p792,
                            p789,
                            p797,
                            prefix_rows,
                            continuation_rows,
                            int(context["order"]),
                            str(context["target"]),
                            group_key,
                            budget_namespace,
                            trained_by_group[group_key],
                            setup_stats,
                            int(context["factor_base_size"]),
                            args,
                        )
                        prepared_context["base_namespace"] = namespace
                        prepared_context["continuation_budget"] = int(budget)
                        prepared_context["prefix_seed_count"] = int(prefix_count)
                        prepared_context["span_concentration"] = span_info["span_concentration"]
                        contexts_by_policy[(policy_name, int(prefix_count), int(budget))][
                            prepared_context["context_id"]
                        ] = prepared_context
                    for threshold in early_thresholds:
                        gate_name = f"prefix_span_top_gate_ge{threshold_suffix(threshold)}"
                        continuation_rows = (
                            continuation_rows_by_policy[(SPAN_POLICY, int(budget))]
                            if threshold in passed_thresholds
                            else []
                        )
                        budget_namespace = f"{namespace}:p{prefix_count}:b{budget}:g{threshold_suffix(threshold)}"
                        prepared_context = p815.prepare_combined_policy_context(
                            p812,
                            p793,
                            p792,
                            p789,
                            p797,
                            prefix_rows,
                            continuation_rows,
                            int(context["order"]),
                            str(context["target"]),
                            group_key,
                            budget_namespace,
                            trained_by_group[group_key],
                            setup_stats,
                            int(context["factor_base_size"]),
                            args,
                        )
                        prepared_context["base_namespace"] = namespace
                        prepared_context["continuation_budget"] = int(budget)
                        prepared_context["early_stop_threshold"] = float(threshold)
                        prepared_context["gate_pass"] = threshold in passed_thresholds
                        prepared_context["prefix_seed_count"] = int(prefix_count)
                        prepared_context["span_concentration"] = span_info["span_concentration"]
                        contexts_by_policy[(gate_name, int(prefix_count), int(budget))][
                            prepared_context["context_id"]
                        ] = prepared_context

    policy_results = []
    for (policy_name, prefix_count, budget), contexts in sorted(contexts_by_policy.items()):
        print(f"scoring P816 policy={policy_name} prefix={prefix_count} continuation_budget={budget}", flush=True)
        if policy_name == "continuation_all_pair":
            kind = "full_pool"
        elif policy_name.startswith("hash_support"):
            kind = "hash_control"
        elif policy_name.startswith("prefix_span_top_gate"):
            kind = "early_stop_gate"
        else:
            kind = "adaptive_prefix_gate"
        policy = {
            "continuation_budget": int(budget),
            "kind": kind,
            "name": policy_name,
            "prefix_seed_count": int(prefix_count),
            "top_k": None,
        }
        policy_results.append(p815.aggregate_policy(p812, p797, p793, policy, contexts, trained_by_group, train_prepared, args))

    full_pool_by_key = {
        policy_key(item): item
        for item in policy_results
        if item["policy"]["name"] == "continuation_all_pair"
    }
    keys = sorted({(prefix, budget) for _name, prefix, budget in contexts_by_policy})
    best_hash_by_key = {
        key: best_result([item for item in policy_results if policy_key(item) == key], {"hash_control"})
        for key in keys
    }
    best_adaptive_by_key = {
        key: best_result([item for item in policy_results if policy_key(item) == key], {"adaptive_prefix_gate"})
        for key in keys
    }
    best_early_by_key = {
        key: best_result([item for item in policy_results if policy_key(item) == key], {"early_stop_gate"})
        for key in keys
    }
    for item in policy_results:
        item["policy_claim"] = determine_policy_claim(item, full_pool_by_key, best_hash_by_key)

    best_adaptive = best_result(policy_results, {"adaptive_prefix_gate"})
    best_early = best_result(policy_results, {"early_stop_gate"})
    best_hash = best_result(policy_results, {"hash_control"})
    full_pool = best_result(policy_results, {"full_pool"})

    def compact_by_key(items: dict[tuple[int, int], dict[str, Any] | None]) -> dict[str, dict[str, Any] | None]:
        return {
            f"p{prefix}_b{budget}": compact_policy_result(p815, p812, item)
            for (prefix, budget), item in sorted(items.items())
        }

    summary = {
        "best_adaptive_prefix_gate": compact_policy_result(p815, p812, best_adaptive),
        "best_adaptive_prefix_gate_by_prefix_budget": compact_by_key(best_adaptive_by_key),
        "best_early_stop_gate": compact_policy_result(p815, p812, best_early),
        "best_early_stop_gate_by_prefix_budget": compact_by_key(best_early_by_key),
        "best_hash_control": compact_policy_result(p815, p812, best_hash),
        "best_hash_control_by_prefix_budget": compact_by_key(best_hash_by_key),
        "calibration_budget": calibration_budget,
        "constructor_namespaces": namespaces,
        "context_diagnostics": context_diagnostics,
        "continuation_budgets": continuation_budgets,
        "early_stop_span_thresholds": early_thresholds,
        "full_pool": compact_policy_result(p815, p812, full_pool),
        "full_pool_by_prefix_budget": compact_by_key(full_pool_by_key),
        "policy_results": policy_results,
        "prefix_seed_counts": prefix_counts,
        "prefix_trial_budget": prefix_trial_budget,
        "scan_seed_count": scan_seed_count,
        "support_diagnostics": support_diagnostics,
        "target_groups": required,
        "train_seed_namespace": args.train_seed_namespace,
    }
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p777_summary": str(args.p777_summary),
            "p786_summary": str(args.p786_summary),
            "p815_script": str(P815_SCRIPT),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(policy_results),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "PREFIX SWEEP: prefix rows use all-pair post-hit scanning and are charged for every policy.",
            "EARLY STOP: skipped contexts retain prefix rows and prefix costs but do not scan continuation rows.",
            "PUBLIC GATE: early-stop decisions use only prefix span-bin concentration, not recovered-row labels.",
            "SCAN-CHARGED: reported costs include prefix and continuation online scan cost plus target-once calibration and all-pair prefix setup.",
            "NO DEPLOYED-CURVE CLAIM: no large-prime scaling, production-key relevance, or complete faster-than-rho ECDLP algorithm is implied.",
        ],
        "method": "p816_prefix_earlystop_amortization_sweep",
        "parameters": {
            "calibration_budget": calibration_budget,
            "continuation_budgets": continuation_budgets,
            "constructor_namespaces": namespaces,
            "control_count": int(args.control_count),
            "early_stop_span_thresholds": early_thresholds,
            "feature_bins": int(args.feature_bins),
            "field_weight": int(args.field_weight),
            "max_relations": int(args.max_relations),
            "max_subsets": int(args.max_subsets),
            "min_line_rows": int(args.min_line_rows),
            "prefix_seed_counts": prefix_counts,
            "prefix_trial_budget": prefix_trial_budget,
            "row_policy": args.row_policy,
            "scan_seed_count": scan_seed_count,
            "sparse_policies": args.sparse_policies,
            "support_budgets": p815.csv_ints(args.support_budgets),
            "top_endpoint_bins": int(args.top_endpoint_bins),
            "top_span_bins": int(args.top_span_bins),
            "train_replicas": int(args.train_replicas),
            "train_seed_namespace": args.train_seed_namespace,
            "walk_mode": args.walk_mode,
            "width": int(args.width),
        },
        "schema": SCHEMA,
        "summary": summary,
    }


def summary_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    p815 = load_module("ecdlp_p815_summary_for_p816", P815_SCRIPT)
    p812 = p815.load_module("ecdlp_p812_summary_for_p816", p815.P812_SCRIPT)
    summary = payload["summary"]
    return {
        **payload,
        "schema": f"{SCHEMA}.summary",
        "summary": {
            **summary,
            "policy_results": [p815.compact_policy_result(p812, item) for item in summary["policy_results"]],
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p777-summary", type=Path, default=DEFAULT_P777_SUMMARY)
    parser.add_argument("--p786-summary", type=Path, default=DEFAULT_P786_SUMMARY)
    parser.add_argument("--train-seed-namespace", default="supportline20-v1")
    parser.add_argument("--constructor-namespaces", default="posthit-p814-adapt-v26,posthit-p814-adapt-v27,posthit-p814-adapt-v28")
    parser.add_argument("--calibration-budget", type=int, default=256)
    parser.add_argument("--prefix-seed-counts", default="4,8,16,32")
    parser.add_argument("--prefix-trial-budget", type=int, default=256)
    parser.add_argument("--continuation-budgets", default="16,32,64")
    parser.add_argument("--early-stop-span-thresholds", default="0.5,0.625,0.75")
    parser.add_argument("--support-budgets", default="128,256,512")
    parser.add_argument("--scan-seed-count", type=int, default=128)
    parser.add_argument("--top-span-bins", type=int, default=2)
    parser.add_argument("--top-endpoint-bins", type=int, default=4)
    parser.add_argument("--train-replicas", type=int, default=20)
    parser.add_argument("--control-count", type=int, default=8)
    parser.add_argument("--feature-bins", type=int, default=8)
    parser.add_argument("--field-weight", type=int, default=2)
    parser.add_argument("--min-line-rows", type=int, default=2)
    parser.add_argument("--row-policy", default="sequential_min_forms_ge_1")
    parser.add_argument("--sparse-policies", default="natural,support_asc,support_span_asc,pivot_low,pivot_high,coefficient_weight_asc")
    parser.add_argument("--width", type=int, default=2)
    parser.add_argument("--walk-mode", default="hash6")
    parser.add_argument("--max-relations", type=int, default=96)
    parser.add_argument("--max-subsets", type=int, default=25000)
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
                "best_adaptive_prefix_gate": summary["summary"]["best_adaptive_prefix_gate"],
                "best_early_stop_gate": summary["summary"]["best_early_stop_gate"],
                "best_hash_control": summary["summary"]["best_hash_control"],
                "claim_status": summary["claim_status"],
                "full_pool": summary["summary"]["full_pool"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
