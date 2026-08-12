#!/usr/bin/env python3
"""P813 unsupervised public multiplicity sieve for post-hit ECDLP rows."""

from __future__ import annotations

import argparse
import importlib.util
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P812_SCRIPT = TASK_DIR / "low_term_total2_p812_posthit_public_row_quality_sieve.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P777_SUMMARY = STATE_DIR / "low_term_total2_p777_merged_trim12_factor_first_cost_audit_summary.json"
DEFAULT_P786_SUMMARY = STATE_DIR / "low_term_total2_p786_public_coordinate_bridge_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p813_unsupervised_public_multiplicity_sieve_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p813_unsupervised_public_multiplicity_sieve.md"
SCHEMA = "ecdlp.low_term_total2_p813_unsupervised_public_multiplicity_sieve.v1"


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


def csv_ints(text: str) -> list[int]:
    return [int(item.strip()) for item in text.split(",") if item.strip()]


def csv_strings(text: str) -> list[str]:
    return [item.strip() for item in text.split(",") if item.strip()]


def scan_all_pair_rows_p813(
    p812: Any,
    p805: Any,
    p801: Any,
    p746: Any,
    p748: Any,
    relprobe: Any,
    context: dict[str, Any],
    trial_budget: int,
    args: argparse.Namespace,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    verifier = context["verifier"]
    ainvs = context["ainvs"]
    p = int(context["p"])
    order = int(context["order"])
    factor_base = context["factor_base"]
    supports_by_policy = {(p812.POOL_SUPPORT_BUDGET, p812.ALL_PAIR): p801.all_support_pairs(len(factor_base))}
    point_policy, support_policy_stats = p801.build_point_policy_map(verifier, factor_base, ainvs, p, supports_by_policy)
    rows = []
    for seed_label in p812.seed_labels(int(args.scan_seed_count)):
        full_seed = (
            f"ecdlp-p813-{context['namespace']}-{p812.slug(context['target'])}:"
            f"{seed_label}:fb{context['factor_base_size']}:w2:{args.walk_mode}"
        )
        challenge, secret = relprobe.make_challenge(verifier, context["inv"], ainvs, full_seed, context["factor_base_size"])
        base = verifier.point_from_json(challenge["base"])
        public = verifier.point_from_json(challenge["public"])
        scanned = p805.scan_seed_grid(
            p801,
            p746,
            p748,
            verifier,
            challenge,
            secret,
            base,
            public,
            ainvs,
            p,
            order,
            context["target"],
            len(factor_base),
            seed_label,
            full_seed,
            [p812.POOL_SUPPORT_BUDGET],
            [int(trial_budget)],
            point_policy,
            support_policy_stats,
            args,
        )
        rows.append(scanned[(p812.POOL_SUPPORT_BUDGET, int(trial_budget), p812.ALL_PAIR)])
    stats = support_policy_stats[(p812.POOL_SUPPORT_BUDGET, p812.ALL_PAIR)]
    return rows, {
        "targeted_setup_group_additions": int(stats["targeted_setup_group_additions"]),
        "targeted_support_count": int(stats["targeted_support_count"]),
        "targeted_unique_point_count": int(stats["targeted_unique_point_count"]),
        "targeted_point_collision_count": int(stats["targeted_point_collision_count"]),
    }


def record_info(p812: Any, p793: Any, record: dict[str, Any] | None, order: int, factor_base_size: int, bins: int) -> dict[str, Any]:
    if record is None:
        return {
            "axis_ratio": ("none", -1, -1),
            "line_key": ("none",),
            "q_mod": -1,
            "ratio_bin": -1,
            "ratio_mod": -1,
            "span_bin": -1,
            "support": ("none",),
        }
    support = tuple(int(index) for index in record["support"])
    left, right = support
    span = abs(left - right)
    parts = p793.line_parts(record, int(order))
    if parts is None:
        line_key = ("none",)
        axis = -1
        ratio_value = -1
    else:
        line_key = tuple(int(value) for value in parts["line_key"])
        axis = int(line_key[2])
        ratio_value = int(line_key[3])
    return {
        "axis_ratio": (axis, ratio_value % 16, p812.bounded_bin(ratio_value, int(order), int(bins)) if ratio_value >= 0 else -1),
        "line_key": line_key,
        "q_mod": int(record["q_coeff"]) % 16,
        "ratio_bin": p812.bounded_bin(ratio_value, int(order), int(bins)) if ratio_value >= 0 else -1,
        "ratio_mod": ratio_value % 16 if ratio_value >= 0 else -1,
        "span_bin": p812.index_bin(span, int(factor_base_size), int(bins)),
        "support": support,
    }


def multiplicity_scores_for_context(p812: Any, p793: Any, context: dict[str, Any], args: argparse.Namespace) -> dict[str, dict[str, float]]:
    records_by_row = p812.row_record_index(context["prepared"]["records"])
    infos = {}
    for example in context["examples"]:
        row_key = str(example["row_key"])
        records = records_by_row.get(row_key) or []
        infos[row_key] = record_info(
            p812,
            p793,
            records[0] if records else None,
            int(context["order"]),
            int(context["factor_base_size"]),
            int(args.feature_bins),
        )
    line_counts = Counter(info["line_key"] for info in infos.values())
    support_counts = Counter(info["support"] for info in infos.values())
    ratio_counts = Counter((info["ratio_bin"], info["ratio_mod"]) for info in infos.values())
    axis_ratio_counts = Counter(info["axis_ratio"] for info in infos.values())
    span_counts = Counter(info["span_bin"] for info in infos.values())
    q_counts = Counter(info["q_mod"] for info in infos.values())
    scores = {
        "line_multiplicity_high": {},
        "line_multiplicity_low": {},
        "support_multiplicity_high": {},
        "support_multiplicity_low": {},
        "ratio_bucket_multiplicity_high": {},
        "axis_ratio_multiplicity_high": {},
        "span_bucket_multiplicity_high": {},
        "collision_neighborhood_high": {},
        "collision_neighborhood_low": {},
    }
    for row_key, info in infos.items():
        line = int(line_counts[info["line_key"]])
        support = int(support_counts[info["support"]])
        ratio = int(ratio_counts[(info["ratio_bin"], info["ratio_mod"])])
        axis_ratio = int(axis_ratio_counts[info["axis_ratio"]])
        span = int(span_counts[info["span_bin"]])
        qmod = int(q_counts[info["q_mod"]])
        neighborhood = (4 * line) + (3 * support) + (2 * ratio) + axis_ratio + span + qmod
        scores["line_multiplicity_high"][row_key] = float(line)
        scores["line_multiplicity_low"][row_key] = -float(line)
        scores["support_multiplicity_high"][row_key] = float(support)
        scores["support_multiplicity_low"][row_key] = -float(support)
        scores["ratio_bucket_multiplicity_high"][row_key] = float(ratio)
        scores["axis_ratio_multiplicity_high"][row_key] = float(axis_ratio)
        scores["span_bucket_multiplicity_high"][row_key] = float(span)
        scores["collision_neighborhood_high"][row_key] = float(neighborhood)
        scores["collision_neighborhood_low"][row_key] = -float(neighborhood)
    return scores


def top_by_score(scores: dict[str, float], top_k: int) -> set[str]:
    ranked = sorted(scores.items(), key=lambda item: (-float(item[1]), item[0]))
    return {row_key for row_key, _score in ranked[: max(0, min(int(top_k), len(ranked)))]}


def selected_sets(
    p812: Any,
    p793: Any,
    policy_name: str,
    top_k: int,
    contexts: dict[str, dict[str, Any]],
    args: argparse.Namespace,
) -> tuple[dict[str, set[str]], list[dict[str, Any]]]:
    selected = {}
    diagnostics = []
    for cid, context in sorted(contexts.items()):
        examples = context["examples"]
        if policy_name == "all_pool":
            row_keys = {str(example["row_key"]) for example in examples}
            scores = {}
        elif policy_name == "hash_control":
            row_keys = p812.top_row_keys_by_hash(examples, cid, int(top_k))
            scores = {}
        else:
            scores_by_policy = multiplicity_scores_for_context(p812, p793, context, args)
            scores = scores_by_policy[policy_name]
            row_keys = top_by_score(scores, int(top_k))
        selected[cid] = row_keys
        labels = {str(example["row_key"]) for example in examples if example["label"]}
        score_values = list(scores.values())
        diagnostics.append(
            {
                "context_id": cid,
                "label_hits": len(row_keys & labels),
                "max_score": None if not score_values else max(score_values),
                "mean_score": None if not score_values else round(sum(score_values) / len(score_values), 8),
                "min_score": None if not score_values else min(score_values),
                "policy": policy_name,
                "selected_count": len(row_keys),
                "top_k": None if policy_name == "all_pool" else int(top_k),
            }
        )
    return selected, diagnostics


def best_by_post_hit(results: list[dict[str, Any]], kinds: set[str]) -> dict[str, Any] | None:
    candidates = [
        item
        for item in results
        if item["policy"]["kind"] in kinds
        and item["aggregate"]["post_hit_scan_once_train_total_unit_cost_over_recovered_rho"] is not None
    ]
    if not candidates:
        return None
    return min(candidates, key=lambda item: item["aggregate"]["post_hit_scan_once_train_total_unit_cost_over_recovered_rho"])


def best_by_selected_only(results: list[dict[str, Any]], kinds: set[str]) -> dict[str, Any] | None:
    candidates = [
        item
        for item in results
        if item["policy"]["kind"] in kinds
        and item["aggregate"]["selected_only_once_train_total_unit_cost_over_recovered_rho"] is not None
    ]
    if not candidates:
        return None
    return min(candidates, key=lambda item: item["aggregate"]["selected_only_once_train_total_unit_cost_over_recovered_rho"])


def determine_policy_claim(item: dict[str, Any], all_pool: dict[str, Any] | None, best_hash: dict[str, Any] | None) -> str:
    aggregate = item["aggregate"]
    kind = item["policy"]["kind"]
    recovered = int(aggregate["recovered_row_count"])
    if recovered <= int(aggregate["max_control_recovered_row_count"]):
        return "does_not_beat_rotated_line_controls"
    post_hit = aggregate["post_hit_scan_once_train_total_unit_cost_over_recovered_rho"]
    selected_only = aggregate["selected_only_once_train_total_unit_cost_over_recovered_rho"]
    if kind == "unsupervised_public_multiplicity" and post_hit is not None and post_hit < 1.0:
        return "unsupervised_public_multiplicity_below_rho"
    if kind == "unsupervised_public_multiplicity" and all_pool is not None:
        pool_ratio = all_pool["aggregate"]["post_hit_scan_once_train_total_unit_cost_over_recovered_rho"]
        hash_recovered = 0 if best_hash is None else int(best_hash["aggregate"]["recovered_row_count"])
        if post_hit is not None and pool_ratio is not None and post_hit < pool_ratio and recovered > hash_recovered:
            return "unsupervised_public_multiplicity_improves_all_pool"
    if kind == "unsupervised_public_multiplicity" and selected_only is not None and selected_only < 1.0:
        return "selected_only_multiplicity_signal_scan_dominated"
    if kind == "hash_control":
        return "hash_control_boundary"
    if kind == "all_pool":
        return "all_pool_boundary"
    return "multiplicity_boundary"


def determine_claim(results: list[dict[str, Any]]) -> str:
    claims = {str(item.get("policy_claim")) for item in results}
    if "unsupervised_public_multiplicity_below_rho" in claims:
        return "P813_UNSUPERVISED_PUBLIC_MULTIPLICITY_BELOW_RHO"
    if "unsupervised_public_multiplicity_improves_all_pool" in claims:
        return "P813_UNSUPERVISED_PUBLIC_MULTIPLICITY_IMPROVES_ALL_POOL"
    if "selected_only_multiplicity_signal_scan_dominated" in claims:
        return "P813_SELECTED_ONLY_MULTIPLICITY_SIGNAL_SCAN_DOMINATED"
    return "NEGATIVE_RESULT_P813_UNSUPERVISED_PUBLIC_MULTIPLICITY_SIEVE_FAILS"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p812 = load_module("ecdlp_p812_for_p813", P812_SCRIPT)
    p805 = p812.load_module("ecdlp_p805_for_p813", p812.P805_SCRIPT)
    p806 = p812.load_module("ecdlp_p806_for_p813", p812.P806_SCRIPT)
    p807 = p812.load_module("ecdlp_p807_for_p813", p812.P807_SCRIPT)
    p808 = p812.load_module("ecdlp_p808_for_p813", p812.P808_SCRIPT)
    p807.configure_p807(p806)
    p812.configure_p805(p805)

    modules = p808.load_research_stack(p806)
    p801 = modules["p801"]
    p800 = p801.load_module("ecdlp_p800_for_p813", p801.P800_SCRIPT)
    p799 = p800.load_module("ecdlp_p799_for_p813", p800.P799_SCRIPT)
    p798 = p799.load_module("ecdlp_p798_for_p813", p799.P798_SCRIPT)
    p797 = p798.load_module("ecdlp_p797_for_p813", p798.P797_SCRIPT)
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
    namespaces = csv_strings(args.constructor_namespaces)
    top_ks = csv_ints(args.top_ks)
    calibration_budget = int(args.calibration_budget)
    trial_budget = int(args.trial_budget)

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

    contexts = {}
    context_diagnostics = []
    for namespace in namespaces:
        for group_key in required:
            print(f"building P813 all-pair context namespace={namespace} group={group_key}", flush=True)
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
            rows, setup_stats = scan_all_pair_rows_p813(
                p812,
                p805,
                p801,
                p746,
                p748,
                relprobe,
                context,
                trial_budget,
                args,
            )
            prepared_context = p812.prepare_context(
                p793,
                p792,
                p789,
                p797,
                rows,
                int(context["order"]),
                str(context["target"]),
                group_key,
                namespace,
                trained_by_group[group_key],
                setup_stats,
                int(context["factor_base_size"]),
                args,
            )
            prepared_context["factor_base_size"] = int(context["factor_base_size"])
            contexts[prepared_context["context_id"]] = prepared_context
            context_diagnostics.append(
                {
                    "context_id": prepared_context["context_id"],
                    "group_key": group_key,
                    "namespace": namespace,
                    "pool_recovered_label_count": prepared_context["pool_recovered_label_count"],
                    "pool_row_count": prepared_context["pool_row_count"],
                    "target": str(context["target"]),
                    **setup_stats,
                }
            )

    policy_results = []
    selection_diagnostics = []
    policies = [("all_pool", 0), *[("hash_control", top_k) for top_k in top_ks]]
    multiplicity_policies = [
        "line_multiplicity_high",
        "line_multiplicity_low",
        "support_multiplicity_high",
        "support_multiplicity_low",
        "ratio_bucket_multiplicity_high",
        "axis_ratio_multiplicity_high",
        "span_bucket_multiplicity_high",
        "collision_neighborhood_high",
        "collision_neighborhood_low",
    ]
    policies.extend((policy, top_k) for policy in multiplicity_policies for top_k in top_ks)
    for policy_name, top_k in policies:
        print(f"scoring P813 policy={policy_name} top_k={top_k}", flush=True)
        selected, diagnostics = selected_sets(p812, p793, policy_name, int(top_k), contexts, args)
        selection_diagnostics.extend(diagnostics)
        if policy_name == "all_pool":
            policy = {"kind": "all_pool", "name": "all_pool", "top_k": None}
        elif policy_name == "hash_control":
            policy = {"kind": "hash_control", "name": f"hash_top{top_k}", "top_k": int(top_k)}
        else:
            policy = {"kind": "unsupervised_public_multiplicity", "name": f"{policy_name}_top{top_k}", "top_k": int(top_k)}
        policy_results.append(
            p812.aggregate_policy(
                p797,
                p793,
                policy,
                selected,
                contexts,
                trained_by_group,
                train_prepared,
                args,
            )
        )

    all_pool = next((item for item in policy_results if item["policy"]["kind"] == "all_pool"), None)
    best_hash = best_by_post_hit(policy_results, {"hash_control"})
    for item in policy_results:
        item["policy_claim"] = determine_policy_claim(item, all_pool, best_hash)

    best_unsup_post = best_by_post_hit(policy_results, {"unsupervised_public_multiplicity"})
    best_unsup_selected = best_by_selected_only(policy_results, {"unsupervised_public_multiplicity"})
    summary = {
        "all_pool": None if all_pool is None else p812.compact_policy_result(all_pool),
        "best_hash_control": None if best_hash is None else p812.compact_policy_result(best_hash),
        "best_unsupervised_by_post_hit": None if best_unsup_post is None else p812.compact_policy_result(best_unsup_post),
        "best_unsupervised_by_selected_only": None if best_unsup_selected is None else p812.compact_policy_result(best_unsup_selected),
        "calibration_budget": calibration_budget,
        "constructor_namespaces": namespaces,
        "context_diagnostics": context_diagnostics,
        "multiplicity_policies": multiplicity_policies,
        "policy_results": policy_results,
        "scan_seed_count": int(args.scan_seed_count),
        "selection_diagnostics": selection_diagnostics,
        "target_groups": required,
        "top_ks": top_ks,
        "train_seed_namespace": args.train_seed_namespace,
        "trial_budget": trial_budget,
    }
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p777_summary": str(args.p777_summary),
            "p786_summary": str(args.p786_summary),
            "p812_script": str(P812_SCRIPT),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(policy_results),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "UNSUPERVISED PUBLIC MULTIPLICITY: row ranks use only same-context public line/support/bucket multiplicities after all-pair hits.",
            "SCAN-CHARGED: the primary metric charges the full all-pair post-hit scan, not just selected row scoring.",
            "NO LABEL TRAINING: recovered-row labels are used only for evaluation, not for selecting rows.",
            "NO DEPLOYED-CURVE CLAIM: no large-prime scaling, production-key relevance, or complete faster-than-rho ECDLP algorithm is implied.",
        ],
        "method": "p813_unsupervised_public_multiplicity_sieve",
        "parameters": {
            "calibration_budget": calibration_budget,
            "constructor_namespaces": namespaces,
            "control_count": int(args.control_count),
            "feature_bins": int(args.feature_bins),
            "field_weight": int(args.field_weight),
            "max_relations": int(args.max_relations),
            "max_subsets": int(args.max_subsets),
            "min_line_rows": int(args.min_line_rows),
            "row_policy": args.row_policy,
            "scan_seed_count": int(args.scan_seed_count),
            "sparse_policies": args.sparse_policies,
            "top_ks": top_ks,
            "train_replicas": int(args.train_replicas),
            "train_seed_namespace": args.train_seed_namespace,
            "trial_budget": trial_budget,
            "walk_mode": args.walk_mode,
            "width": int(args.width),
        },
        "schema": SCHEMA,
        "summary": summary,
    }


def summary_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    p812 = load_module("ecdlp_p812_summary_for_p813", P812_SCRIPT)
    summary = payload["summary"]
    return {
        **payload,
        "schema": f"{SCHEMA}.summary",
        "summary": {
            **summary,
            "policy_results": [p812.compact_policy_result(item) for item in summary["policy_results"]],
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p777-summary", type=Path, default=DEFAULT_P777_SUMMARY)
    parser.add_argument("--p786-summary", type=Path, default=DEFAULT_P786_SUMMARY)
    parser.add_argument("--train-seed-namespace", default="supportline20-v1")
    parser.add_argument("--constructor-namespaces", default="posthit-p813-mult-v23,posthit-p813-mult-v24,posthit-p813-mult-v25")
    parser.add_argument("--calibration-budget", type=int, default=256)
    parser.add_argument("--trial-budget", type=int, default=256)
    parser.add_argument("--top-ks", default="16,32,64,96,128")
    parser.add_argument("--train-replicas", type=int, default=20)
    parser.add_argument("--scan-seed-count", type=int, default=128)
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
                "all_pool": summary["summary"]["all_pool"],
                "best_hash_control": summary["summary"]["best_hash_control"],
                "best_unsupervised_by_post_hit": summary["summary"]["best_unsupervised_by_post_hit"],
                "best_unsupervised_by_selected_only": summary["summary"]["best_unsupervised_by_selected_only"],
                "claim_status": summary["claim_status"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
