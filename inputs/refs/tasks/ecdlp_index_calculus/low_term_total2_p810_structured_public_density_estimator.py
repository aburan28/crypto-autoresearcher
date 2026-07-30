#!/usr/bin/env python3
"""P810 structured public density estimator for support-rank transfer."""

from __future__ import annotations

import argparse
import importlib.util
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P806_SCRIPT = TASK_DIR / "low_term_total2_p806_public_feature_classifier.py"
P807_SCRIPT = TASK_DIR / "low_term_total2_p807_richer_public_feature_classifier.py"
P808_SCRIPT = TASK_DIR / "low_term_total2_p808_requested_support_invariant_miner.py"
P809_SCRIPT = TASK_DIR / "low_term_total2_p809_public_rank_proxy_audit.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P777_SUMMARY = STATE_DIR / "low_term_total2_p777_merged_trim12_factor_first_cost_audit_summary.json"
DEFAULT_P786_SUMMARY = STATE_DIR / "low_term_total2_p786_public_coordinate_bridge_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p810_structured_public_density_estimator_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p810_structured_public_density_estimator.md"
SCHEMA = "ecdlp.low_term_total2_p810_structured_public_density_estimator.v1"


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


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(float(numerator) / float(denominator), 8)


def csv_ints(text: str) -> list[int]:
    return [int(item.strip()) for item in text.split(",") if item.strip()]


def csv_strings(text: str) -> list[str]:
    return [item.strip() for item in text.split(",") if item.strip()]


def stat(values: list[float]) -> dict[str, Any]:
    if not values:
        return {"count": 0, "max": None, "mean": None, "min": None}
    return {"count": len(values), "max": max(values), "mean": round(mean(values), 8), "min": min(values)}


def canonical_support(support: tuple[int, int]) -> tuple[int, int]:
    left, right = int(support[0]), int(support[1])
    return (left, right) if left <= right else (right, left)


def rank_bin(rank: float, universe: int, bins: int) -> int:
    if universe <= 0:
        return 0
    return max(0, min(int(bins) - 1, int((float(rank) - 1.0) * int(bins) / float(universe))))


def numeric_bin(value: float, values: list[float], bins: int) -> int:
    if not values:
        return 0
    lo = min(values)
    hi = max(values)
    if hi == lo:
        return 0
    return max(0, min(int(bins) - 1, int((float(value) - lo) * int(bins) / (hi - lo + 1e-12))))


def count_bin(value: float) -> str:
    value = int(value)
    if value <= 0:
        return "0"
    if value <= 8:
        return str(value)
    power = 1 << (value.bit_length() - 1)
    return f"{power}+"


def overlap_stats(selected: set[tuple[int, int]], exact: set[tuple[int, int]]) -> dict[str, Any]:
    overlap = len(selected & exact)
    union = len(selected | exact)
    return {
        "exact_count": len(exact),
        "jaccard_with_exact_rank": ratio(overlap, union),
        "overlap_count": overlap,
        "overlap_over_exact_rank": ratio(overlap, len(exact)),
        "selected_count": len(selected),
    }


def context_id(namespace: str, group_key: str) -> str:
    return f"{namespace}::{group_key}"


def transfer_protocol(source: dict[str, Any], target: dict[str, Any]) -> str:
    if source["namespace"] == target["namespace"] and source["group_key"] != target["group_key"]:
        return "single_source_same_namespace_cross_target"
    if source["namespace"] != target["namespace"] and source["group_key"] == target["group_key"]:
        return "single_source_cross_namespace_same_target"
    if source["namespace"] != target["namespace"] and source["group_key"] != target["group_key"]:
        return "single_source_cross_namespace_cross_target"
    return "same_context_upper_bound"


def aggregate_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(row["protocol"], int(row["support_budget"]))].append(row)
    out = []
    for (protocol, budget), items in sorted(grouped.items()):
        out.append(
            {
                "jaccard_with_exact_rank": stat([float(item["jaccard_with_exact_rank"] or 0.0) for item in items]),
                "overlap_count": stat([float(item["overlap_count"]) for item in items]),
                "overlap_over_exact_rank": stat([float(item["overlap_over_exact_rank"] or 0.0) for item in items]),
                "protocol": protocol,
                "support_budget": int(budget),
            }
        )
    return out


def best_row(rows: list[dict[str, Any]], support_budget: int | None = None, protocols: set[str] | None = None) -> dict[str, Any] | None:
    candidates = rows
    if support_budget is not None:
        candidates = [row for row in candidates if int(row["support_budget"]) == int(support_budget)]
    if protocols is not None:
        candidates = [row for row in candidates if row["protocol"] in protocols]
    if not candidates:
        return None
    return max(
        candidates,
        key=lambda row: (
            float(row["overlap_over_exact_rank"] or 0.0),
            float(row["jaccard_with_exact_rank"] or 0.0),
            int(row["overlap_count"]),
        ),
    )


def best_aggregate(rows: list[dict[str, Any]], support_budget: int, protocols: set[str]) -> dict[str, Any] | None:
    candidates = [
        row
        for row in aggregate_rows(rows)
        if int(row["support_budget"]) == int(support_budget) and row["protocol"] in protocols
    ]
    if not candidates:
        return None
    return max(
        candidates,
        key=lambda row: (
            float(row["overlap_over_exact_rank"]["min"] or 0.0),
            float(row["overlap_over_exact_rank"]["mean"] or 0.0),
        ),
    )


def determine_claim(rows: list[dict[str, Any]], promote_budget: int) -> str:
    holdout_protocols = {
        "single_source_same_namespace_cross_target",
        "single_source_cross_namespace_same_target",
        "single_source_cross_namespace_cross_target",
        "leave_one_context_out",
    }
    best = best_aggregate(rows, promote_budget, holdout_protocols)
    if best is None:
        return "NEGATIVE_RESULT_P810_NO_TRANSFER_ROWS"
    min_overlap = float(best["overlap_over_exact_rank"]["min"] or 0.0)
    max_overlap = float(best["overlap_over_exact_rank"]["max"] or 0.0)
    if min_overlap >= 0.80:
        return "P810_PUBLIC_DENSITY_ESTIMATOR_READY_FOR_CHARGED_SCAN"
    if max_overlap >= 0.80:
        return "P810_PARTIAL_PUBLIC_DENSITY_TRANSFER_SIGNAL"
    return "NEGATIVE_RESULT_P810_PUBLIC_DENSITY_ESTIMATOR_FAILS_TRACE_RANK"


def public_density_features(
    p809: Any,
    p801: Any,
    p746: Any,
    relprobe: Any,
    context: dict[str, Any],
    args: argparse.Namespace,
) -> dict[tuple[int, int], tuple[str, ...]]:
    all_pairs = [canonical_support(support) for support in context["all_pairs"]]
    base_features = {canonical_support(support): tuple(features) for support, features in context["features_by_support"].items()}
    score_maps = p809.public_static_scores(p801, context)
    score_maps.update(p809.cheap_prehit_scores(p746, p801, relprobe, context, args))
    rank_maps = {name: p809.rank_map_from_scores(scores) for name, scores in score_maps.items()}
    feature_out: dict[tuple[int, int], tuple[str, ...]] = {}
    bins = int(args.density_feature_bins)
    threshold_budgets = csv_ints(args.support_budgets)
    for support in all_pairs:
        features = list(base_features[support])
        for name, scores in sorted(score_maps.items()):
            rank = rank_maps[name][support]
            values = list(scores.values())
            features.append(f"{name}:rank_bin={rank_bin(rank, len(all_pairs), bins)}")
            features.append(f"{name}:value_bin={numeric_bin(float(scores[support]), values, bins)}")
            for budget in threshold_budgets:
                features.append(f"{name}:top{budget}={int(rank <= int(budget))}")
            if name.startswith("cheap_prehit"):
                features.append(f"{name}:count_bin={count_bin(float(scores[support]))}")
        feature_out[support] = tuple(features)
    return feature_out


def build_examples(args: argparse.Namespace) -> tuple[Any, Any, dict[str, Any], dict[tuple[str, str], dict[str, Any]], dict[str, dict[str, Any]]]:
    p806 = load_module("ecdlp_p806_for_p810", P806_SCRIPT)
    p807 = load_module("ecdlp_p807_for_p810", P807_SCRIPT)
    p808 = load_module("ecdlp_p808_for_p810", P808_SCRIPT)
    p809 = load_module("ecdlp_p809_for_p810", P809_SCRIPT)
    p807.configure_p807(p806)
    modules = p808.load_research_stack(p806)
    p801 = modules["p801"]
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
    relprobe = stack["relprobe"]

    frozen_pairs = p788.selected_frozen_pairs(p787, args.p786_summary)
    required = sorted({item["dest_group_key"] for item in frozen_pairs})
    base_groups = p784.normalized_groups(args.p777_summary, required)
    support_budgets = csv_ints(args.support_budgets)
    namespaces = csv_strings(args.constructor_namespaces)
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
    trained_by_group_support = {
        group_key: {
            int(budget): p794.selected_calibrations(train_prepared[group_key]["all_calibrated"], int(budget))
            for budget in support_budgets
        }
        for group_key in required
    }

    contexts = {}
    examples = {}
    for namespace in namespaces:
        for group_key in required:
            print(f"building density context namespace={namespace} group={group_key}", flush=True)
            context = p806.build_public_context(
                p801,
                p746,
                relprobe,
                base_groups[group_key],
                trained_by_group_support[group_key],
                support_budgets,
                namespace,
                args,
            )
            all_pairs = [p808.canonical_support(support) for support in context["all_pairs"]]
            _trace_features, grouped = p808.build_trace_features(
                all_pairs,
                train_prepared[group_key]["all_calibrated"],
                int(context["order"]),
                int(args.feature_bins),
            )
            exact_keys = p809.exact_support_rank_keys(p808, grouped, all_pairs)
            features_by_support = public_density_features(p809, p801, p746, relprobe, context, args)
            cid = context_id(namespace, group_key)
            contexts[(namespace, group_key)] = {
                "all_pairs": all_pairs,
                "exact_keys": exact_keys,
                "factor_base_size": int(context["factor_base_size"]),
                "group_key": group_key,
                "namespace": namespace,
                "target": str(context["target"]),
            }
            examples[cid] = {
                "all_pairs": all_pairs,
                "features_by_support": features_by_support,
                "group_key": group_key,
                "namespace": namespace,
                "target": str(context["target"]),
            }
    helper = {
        "p808": p808,
        "p809": p809,
        "required": required,
        "support_budgets": support_budgets,
        "namespaces": namespaces,
    }
    return p808, p809, helper, contexts, examples


def eval_model(
    p808: Any,
    p809: Any,
    model: dict[str, Any],
    target_example: dict[str, Any],
    target_context: dict[str, Any],
    budget: int,
) -> dict[str, Any]:
    exact = p809.top_by_sort_key(target_context["exact_keys"], int(budget))
    selected = p808.select_model_supports({**target_example, "requested": exact}, model, int(budget))
    return overlap_stats(selected, exact)


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    if int(args.width) != 2:
        raise ValueError("P810 estimates width-2 support-pair ranks; use --width 2")
    p808, p809, helper, contexts, examples = build_examples(args)
    support_budgets = helper["support_budgets"]
    rows = []
    model_rows = []
    for budget in support_budgets:
        exact_by_context = {
            cid: p809.top_by_sort_key(contexts[(example["namespace"], example["group_key"])]["exact_keys"], int(budget))
            for cid, example in examples.items()
        }
        for source_id, source_example in sorted(examples.items()):
            source_context = contexts[(source_example["namespace"], source_example["group_key"])]
            source_exact = exact_by_context[source_id]
            source_train = {**source_example, "requested": source_exact}
            model = p808.train_logodds_model([source_train], float(args.logodds_smoothing))
            model_rows.append(
                {
                    "feature_count": model["feature_count"],
                    "model": "single_source_logodds",
                    "negative_examples": model["negative_examples"],
                    "positive_examples": model["positive_examples"],
                    "source_context": source_id,
                    "support_budget": int(budget),
                    "top_positive_features": model["top_positive_features"],
                }
            )
            for target_id, target_example in sorted(examples.items()):
                target_context = contexts[(target_example["namespace"], target_example["group_key"])]
                protocol = transfer_protocol(source_context, target_context)
                result = eval_model(p808, p809, model, target_example, target_context, int(budget))
                rows.append(
                    {
                        **result,
                        "protocol": protocol,
                        "source_context": source_id,
                        "source_group_key": source_context["group_key"],
                        "source_namespace": source_context["namespace"],
                        "source_target": source_context["target"],
                        "support_budget": int(budget),
                        "target_context": target_id,
                        "target_group_key": target_context["group_key"],
                        "target_namespace": target_context["namespace"],
                        "target_target": target_context["target"],
                    }
                )

        for target_id, target_example in sorted(examples.items()):
            train_examples = [
                {**example, "requested": exact_by_context[cid]}
                for cid, example in sorted(examples.items())
                if cid != target_id
            ]
            model = p808.train_logodds_model(train_examples, float(args.logodds_smoothing))
            target_context = contexts[(target_example["namespace"], target_example["group_key"])]
            result = eval_model(p808, p809, model, target_example, target_context, int(budget))
            rows.append(
                {
                    **result,
                    "protocol": "leave_one_context_out",
                    "source_context": "all_except_target",
                    "source_group_key": "mixed",
                    "source_namespace": "mixed",
                    "source_target": "mixed",
                    "support_budget": int(budget),
                    "target_context": target_id,
                    "target_group_key": target_context["group_key"],
                    "target_namespace": target_context["namespace"],
                    "target_target": target_context["target"],
                }
            )
            model_rows.append(
                {
                    "feature_count": model["feature_count"],
                    "model": "leave_one_context_out",
                    "negative_examples": model["negative_examples"],
                    "positive_examples": model["positive_examples"],
                    "source_context": f"all_except::{target_id}",
                    "support_budget": int(budget),
                    "top_positive_features": model["top_positive_features"],
                }
            )

    promote_budget = int(args.promote_support_budget)
    holdout_protocols = {
        "single_source_same_namespace_cross_target",
        "single_source_cross_namespace_same_target",
        "single_source_cross_namespace_cross_target",
        "leave_one_context_out",
    }
    summary = {
        "aggregate_rows": aggregate_rows(rows),
        "best_holdout_row": best_row(rows, promote_budget, holdout_protocols),
        "best_holdout_aggregate": best_aggregate(rows, promote_budget, holdout_protocols),
        "best_same_context_upper": best_row(rows, promote_budget, {"same_context_upper_bound"}),
        "constructor_namespaces": helper["namespaces"],
        "model_rows": model_rows,
        "promote_support_budget": promote_budget,
        "rows": rows,
        "support_budgets": support_budgets,
        "target_groups": helper["required"],
        "train_seed_namespace": args.train_seed_namespace,
    }
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p777_summary": str(args.p777_summary),
            "p786_summary": str(args.p786_summary),
            "p806_script": str(P806_SCRIPT),
            "p807_script": str(P807_SCRIPT),
            "p808_script": str(P808_SCRIPT),
            "p809_script": str(P809_SCRIPT),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(rows, promote_budget),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "SUPERVISED PUBLIC-FEATURE ESTIMATOR: calibration rank labels are used for source-context training and held-out evaluation, but not as held-out proxy inputs.",
            "PUBLIC FEATURES ONLY AT EVALUATION: held-out scoring uses P807 public geometry features and P809 cheap public pre-hit histogram features.",
            "SUPPORT-RANK ONLY: P810 measures top-k support-rank transfer; it does not claim recovered rows or a faster-than-rho solver.",
            "PROMOTION GATE: a held-out model must recover at least 80 percent of exact top-256 supports before any charged row-recovery scan is promoted.",
            "NO DEPLOYED-CURVE CLAIM: no large-prime scaling, production-key relevance, or complete faster-than-rho ECDLP algorithm is implied.",
        ],
        "method": "p810_structured_public_density_estimator",
        "parameters": {
            "constructor_namespaces": helper["namespaces"],
            "density_feature_bins": int(args.density_feature_bins),
            "feature_bins": int(args.feature_bins),
            "logodds_smoothing": float(args.logodds_smoothing),
            "min_line_rows": int(args.min_line_rows),
            "promote_support_budget": promote_budget,
            "proxy_seed_count": int(args.proxy_seed_count),
            "proxy_trial_budget": int(args.proxy_trial_budget),
            "row_policy": args.row_policy,
            "sparse_policies": args.sparse_policies,
            "support_budgets": support_budgets,
            "train_replicas": int(args.train_replicas),
            "train_seed_namespace": args.train_seed_namespace,
            "walk_mode": args.walk_mode,
            "width": int(args.width),
        },
        "schema": SCHEMA,
        "summary": summary,
    }


def summary_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        **payload,
        "schema": f"{SCHEMA}.summary",
        "summary": {
            **payload["summary"],
            "model_rows": [
                {
                    key: value
                    for key, value in row.items()
                    if key != "top_positive_features"
                }
                for row in payload["summary"]["model_rows"]
            ],
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p777-summary", type=Path, default=DEFAULT_P777_SUMMARY)
    parser.add_argument("--p786-summary", type=Path, default=DEFAULT_P786_SUMMARY)
    parser.add_argument("--train-seed-namespace", default="supportline20-v1")
    parser.add_argument("--constructor-namespaces", default="prehitpair-p807-rich-v14,prehitpair-p807-rich-v15,prehitpair-p807-rich-v16")
    parser.add_argument("--support-budgets", default="128,256,512")
    parser.add_argument("--promote-support-budget", type=int, default=256)
    parser.add_argument("--train-replicas", type=int, default=20)
    parser.add_argument("--feature-bins", type=int, default=8)
    parser.add_argument("--density-feature-bins", type=int, default=8)
    parser.add_argument("--proxy-seed-count", type=int, default=32)
    parser.add_argument("--proxy-trial-budget", type=int, default=64)
    parser.add_argument("--logodds-smoothing", type=float, default=1.0)
    parser.add_argument("--min-line-rows", type=int, default=2)
    parser.add_argument("--row-policy", default="sequential_min_forms_ge_1")
    parser.add_argument("--sparse-policies", default="natural,support_asc,support_span_asc,pivot_low,pivot_high,coefficient_weight_asc")
    parser.add_argument("--width", type=int, default=2)
    parser.add_argument("--walk-mode", default="hash6")
    parser.add_argument("--max-relations", type=int, default=96)
    parser.add_argument("--max-subsets", type=int, default=25000)
    parser.add_argument("--control-count", type=int, default=8)
    parser.add_argument("--field-weight", type=int, default=2)
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
                "best_holdout_aggregate": summary["summary"]["best_holdout_aggregate"],
                "best_holdout_row": summary["summary"]["best_holdout_row"],
                "best_same_context_upper": summary["summary"]["best_same_context_upper"],
                "claim_status": summary["claim_status"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
