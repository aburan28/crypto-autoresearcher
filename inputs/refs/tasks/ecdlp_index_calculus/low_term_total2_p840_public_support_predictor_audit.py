#!/usr/bin/env python3
"""P840 explicit public support-pair predictor audit after P839."""

from __future__ import annotations

import argparse
import importlib.util
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P799_SCRIPT = TASK_DIR / "low_term_total2_p799_exact_support_pair_constructive_generator.py"
P835_SCRIPT = TASK_DIR / "low_term_total2_p835_support_schedule_generator_audit.py"
P837_SCRIPT = TASK_DIR / "low_term_total2_p837_schedule_direct_constructor_audit.py"
P838_SCRIPT = TASK_DIR / "low_term_total2_p838_support_forcing_seed_material_audit.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P777_SUMMARY = STATE_DIR / "low_term_total2_p777_merged_trim12_factor_first_cost_audit_summary.json"
DEFAULT_P786_SUMMARY = STATE_DIR / "low_term_total2_p786_public_coordinate_bridge_summary.json"
DEFAULT_P837_SUMMARY = STATE_DIR / "low_term_total2_p837_schedule_direct_constructor_audit_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p840_public_support_predictor_audit_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p840_public_support_predictor_audit.md"
SCHEMA = "ecdlp.low_term_total2_p840_public_support_predictor_audit.v1"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {name} from {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(float(numerator) / float(denominator), 8)


def csv_ints(raw: str) -> list[int]:
    return [int(part.strip()) for part in str(raw).split(",") if part.strip()]


def slug(value: str) -> str:
    text = "".join(ch if ch.isalnum() else "_" for ch in str(value))
    return "_".join(part for part in text.split("_") if part)


def clause_name(clause: tuple[str, ...]) -> str:
    return "_AND_".join(slug(tag) for tag in clause) or "empty"


def plans_for_supports(group_key: str, supports: list[tuple[int, int]], tag_prefix: str) -> list[dict[str, Any]]:
    return [
        {
            "group_key": group_key,
            "intended_line": None,
            "intended_support": tuple(int(part) for part in support),
            "tag": f"{tag_prefix}_pair_{support[0]}_{support[1]}",
        }
        for support in supports
    ]


def neutral_plans(group_key: str, count: int, tag_prefix: str) -> list[dict[str, Any]]:
    return [
        {
            "group_key": group_key,
            "intended_line": None,
            "intended_support": None,
            "tag": f"{tag_prefix}_neutral_{index:03d}",
        }
        for index in range(int(count))
    ]


def support_matches_clause(p835: Any, support: tuple[int, int], clause: tuple[str, ...]) -> bool:
    tags = p835.support_tags_for_pair(int(support[0]), int(support[1]))
    return all(tag in tags for tag in clause)


def target_breakdown(policy: dict[str, Any], support_meta: list[dict[str, Any]]) -> list[dict[str, Any]]:
    breakdown = []
    for meta, target_result in zip(support_meta, policy.get("target_results") or []):
        aggregate = target_result["aggregate"]
        breakdown.append(
            {
                "generated_rows": int(aggregate["generated_row_count"]),
                "group_key": meta["group_key"],
                "intended_support_hits": int(aggregate["intended_support_hit_row_count"]),
                "predictor_pair_count": int(meta["predictor_pair_count"]),
                "recovered_rows": int(aggregate["recovered_row_count"]),
                "selected_support_count": int(meta["selected_support_count"]),
                "selected_support_hits": int(aggregate["selected_support_hit_row_count"]),
                "trained_match_count": int(meta["trained_match_count"]),
            }
        )
    return breakdown


def aggregate_policy_results(items: list[dict[str, Any]], policy_name: str) -> dict[str, Any]:
    totals = Counter()
    controls = []
    for item in items:
        aggregate = item["aggregate"]
        for key, value in aggregate.items():
            if isinstance(value, int):
                totals[key] += value
        controls.append(int(aggregate.get("max_control_recovered_row_count") or 0))
    generated_rows = int(totals["generated_row_count"])
    recovered_rho = int(totals["recovered_rho_baseline"])
    return {
        "aggregate": {
            **dict(totals),
            "generated_once_train_total_unit_cost_over_recovered_rho": ratio(
                int(totals["generated_once_train_total_unit_cost"]),
                recovered_rho,
            ),
            "intended_support_hit_rate": ratio(int(totals["intended_support_hit_row_count"]), generated_rows),
            "max_control_recovered_row_count": max(controls, default=0),
            "primary_minus_max_control_recovered_rows": int(totals["recovered_row_count"]) - max(controls, default=0),
            "selected_line_hit_rate": ratio(int(totals["selected_line_hit_row_count"]), generated_rows),
            "selected_support_hit_rate": ratio(int(totals["selected_support_hit_row_count"]), generated_rows),
            "target_count": len(items),
        },
        "policy": {
            "kind": policy_name,
            "name": policy_name,
        },
        "target_results": items,
    }


def compact_policy(policy: dict[str, Any], support_meta: list[dict[str, Any]]) -> dict[str, Any]:
    aggregate = policy["aggregate"]
    keep = [
        "generated_once_train_total_unit_cost",
        "generated_once_train_total_unit_cost_over_recovered_rho",
        "generated_online_group_additions",
        "generated_row_count",
        "generated_row_rho_baseline",
        "intended_support_hit_rate",
        "intended_support_hit_row_count",
        "max_control_recovered_row_count",
        "primary_minus_max_control_recovered_rows",
        "recovered_rho_baseline",
        "recovered_row_count",
        "scored_form_count",
        "selected_line_hit_rate",
        "selected_support_hit_rate",
        "selected_support_hit_row_count",
        "target_count",
    ]
    return {
        "aggregate": {key: aggregate.get(key) for key in keep},
        "policy": policy["policy"],
        "policy_claim": policy.get("policy_claim"),
        "target_breakdown": target_breakdown(policy, support_meta),
    }


def classify_policy(item: dict[str, Any], controls: dict[str, dict[str, Any]]) -> str:
    aggregate = item["aggregate"]
    intended_hits = int(aggregate["intended_support_hit_row_count"])
    recovered = int(aggregate["recovered_row_count"])
    control_intended = max(
        int((controls.get("neutral") or {}).get("aggregate", {}).get("intended_support_hit_row_count") or 0),
        int((controls.get("rotated") or {}).get("aggregate", {}).get("intended_support_hit_row_count") or 0),
    )
    control_recovered = max(
        int((controls.get("neutral") or {}).get("aggregate", {}).get("recovered_row_count") or 0),
        int((controls.get("rotated") or {}).get("aggregate", {}).get("recovered_row_count") or 0),
    )
    if intended_hits > control_intended and recovered >= control_recovered:
        return "public_predictor_support_and_recovery_signal"
    if intended_hits > control_intended:
        return "public_predictor_support_lift_with_recovery_loss"
    if recovered > control_recovered:
        return "public_predictor_recovery_enrichment_without_support_lift"
    return "does_not_beat_controls"


def determine_claim(results: list[dict[str, Any]]) -> str:
    claims = [
        policy["policy_claim"]
        for result in results
        for policy in result["policy_results"]
        if policy["policy"]["name"].startswith("predictor_")
    ]
    if "public_predictor_support_and_recovery_signal" in claims:
        return "P840_PUBLIC_PREDICTOR_SUPPORT_AND_RECOVERY_SIGNAL"
    if "public_predictor_support_lift_with_recovery_loss" in claims:
        return "P840_PUBLIC_PREDICTOR_SUPPORT_LIFT_WITH_RECOVERY_LOSS"
    if "public_predictor_recovery_enrichment_without_support_lift" in claims:
        return "P840_PUBLIC_PREDICTOR_RECOVERY_ENRICHMENT_ONLY"
    return "NEGATIVE_RESULT_P840_PUBLIC_PREDICTORS_DO_NOT_BEAT_CONTROLS"


def rank_clauses(
    p835: Any,
    clauses: list[tuple[str, ...]],
    required: list[str],
    base_groups: dict[str, Any],
    ranked_by_group: dict[str, list[tuple[int, int]]],
    max_items_per_target: int,
) -> list[dict[str, Any]]:
    ranked_top_count = max(4 * int(max_items_per_target), int(max_items_per_target))
    scored = []
    for clause_index, clause in enumerate(clauses):
        total_pairs = 0
        total_trained_matches = 0
        total_top_matches = 0
        per_group = []
        for group_key in required:
            fb_size = int(base_groups[group_key]["factor_base_size"])
            pairs = sorted(p835.support_pair_set(fb_size, clause))
            pair_set = set(pairs)
            ranked = ranked_by_group[group_key]
            trained_matches = [support for support in ranked if support in pair_set]
            top_matches = [support for support in ranked[:ranked_top_count] if support in pair_set]
            total_pairs += len(pairs)
            total_trained_matches += len(trained_matches)
            total_top_matches += len(top_matches)
            per_group.append(
                {
                    "factor_base_size": fb_size,
                    "group_key": group_key,
                    "predictor_pair_count": len(pairs),
                    "schedule_fraction": ratio(len(pairs), fb_size * (fb_size - 1) // 2),
                    "top_ranked_match_count": len(top_matches),
                    "trained_match_count": len(trained_matches),
                }
            )
        scored.append(
            {
                "clause": list(clause),
                "clause_index": int(clause_index),
                "name": clause_name(clause),
                "per_group": per_group,
                "total_predictor_pair_count": int(total_pairs),
                "total_top_ranked_match_count": int(total_top_matches),
                "total_trained_match_count": int(total_trained_matches),
                "trained_match_density": ratio(total_trained_matches, total_pairs),
            }
        )
    return sorted(
        scored,
        key=lambda item: (
            int(item["total_top_ranked_match_count"]),
            float(item["trained_match_density"] or 0.0),
            int(item["total_trained_match_count"]),
            -int(item["total_predictor_pair_count"]),
            -int(item["clause_index"]),
        ),
        reverse=True,
    )


def positive_schedule_specs(p838: Any, p837_summary: dict[str, Any]) -> list[dict[str, Any]]:
    specs = p838.positive_schedule_specs(p837_summary)
    if specs:
        return specs
    out = []
    for result in p837_summary["direct_constructor"]["schedule_results"]:
        out.append(
            {
                "best_p837_policy": "none",
                "clauses": [tuple(clause) for clause in result["clauses"]],
                "schedule_name": result["schedule_name"],
                "source_name": "trained",
            }
        )
    return out


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p799 = load_module("ecdlp_p799_for_p840", P799_SCRIPT)
    p835 = load_module("ecdlp_p835_for_p840", P835_SCRIPT)
    p837 = load_module("ecdlp_p837_for_p840", P837_SCRIPT)
    p838 = load_module("ecdlp_p838_for_p840", P838_SCRIPT)
    p798 = p799.load_module("ecdlp_p798_for_p840", p799.P798_SCRIPT)
    p797 = p798.load_module("ecdlp_p797_for_p840", p798.P797_SCRIPT)
    p796 = p797.load_module("ecdlp_p796_for_p840", p797.P796_SCRIPT)
    p795 = p796.load_module("ecdlp_p795_for_p840", p796.P795_SCRIPT)
    p794 = p795.load_module("ecdlp_p794_for_p840", p795.P794_SCRIPT)
    p793 = p794.load_module("ecdlp_p793_for_p840", p794.P793_SCRIPT)
    p792 = p793.load_module("ecdlp_p792_for_p840", p793.P792_SCRIPT)
    p789 = p792.load_module("ecdlp_p789_for_p840", p792.P789_SCRIPT)
    p788 = p789.load_module("ecdlp_p788_for_p840", p789.P788_SCRIPT)
    p787 = p788.load_module("ecdlp_p787_for_p840", p788.P787_SCRIPT)
    p786 = p787.load_module("ecdlp_p786_for_p840", p787.P786_SCRIPT)
    p784 = p786.load_module("ecdlp_p784_for_p840", p786.P784_SCRIPT)
    p782 = p784.load_module("ecdlp_p782_for_p840", p784.P782_SCRIPT)
    p780 = p782.load_module("ecdlp_p780_for_p840", p782.P780_SCRIPT)
    stack = p780.load_stack()
    p746 = stack["p746"]
    p748 = stack["p748"]
    relprobe = stack["relprobe"]
    p837_summary = load_json(args.p837_summary)
    specs = positive_schedule_specs(p838, p837_summary)[: int(args.max_schedules)]
    frozen_pairs = p788.selected_frozen_pairs(p787, args.p786_summary)
    required = sorted({item["dest_group_key"] for item in frozen_pairs})
    base_groups = p784.normalized_groups(args.p777_summary, required)
    train_args = p795.namespace_args(args, args.train_seed_namespace, int(args.train_replicas))
    print(f"preparing train namespace {args.train_seed_namespace}", flush=True)
    train_prepared = {
        key: p794.prepare_target(p793, p792, p789, p787, p784, stack, base_groups[key], train_args)
        for key in required
    }
    budgets = csv_ints(args.budgets)
    schedule_results = []
    all_policy_results = []
    for budget in budgets:
        print(f"scoring budget {budget}", flush=True)
        trained_by_group = {
            key: p794.selected_calibrations(train_prepared[key]["all_calibrated"], int(budget))
            for key in required
        }
        ranked_by_group = {
            key: p837.ranked_supports_from_trained(trained_by_group[key])
            for key in required
        }
        for spec in specs:
            schedule_name = str(spec["schedule_name"])
            clauses = [tuple(clause) for clause in spec["clauses"]]
            clause_scores = rank_clauses(
                p835,
                clauses,
                required,
                base_groups,
                ranked_by_group,
                int(args.max_items_per_target),
            )[: int(args.max_clauses_per_schedule)]
            for clause_score in clause_scores:
                clause = tuple(clause_score["clause"])
                target_results: dict[str, list[dict[str, Any]]] = {
                    "neutral": [],
                    "predictor_public": [],
                    "predictor_trained": [],
                    "rotated": [],
                }
                support_meta = []
                for group_key in required:
                    fb_size = int(base_groups[group_key]["factor_base_size"])
                    predictor_pairs = sorted(p835.support_pair_set(fb_size, clause))
                    predictor_pair_set = set(predictor_pairs)
                    trained = trained_by_group[group_key]
                    ranked = ranked_by_group[group_key]
                    trained_matches = [
                        support
                        for support in ranked
                        if support in predictor_pair_set and support_matches_clause(p835, support, clause)
                    ]
                    public_supports = p837.stable_sample(
                        predictor_pairs,
                        int(args.max_items_per_target),
                        f"{schedule_name}:{group_key}:{clause_score['name']}:public:{budget}",
                    )
                    trained_supports = trained_matches[: int(args.max_items_per_target)] or public_supports
                    public_supports = public_supports[: len(trained_supports)]
                    rotated_supports = p837.rotated_supports(trained_supports, fb_size)[: len(trained_supports)]
                    tag_base = f"p840_{slug(schedule_name)}_{clause_score['name']}_{slug(group_key)}"
                    policies = {
                        "neutral": neutral_plans(group_key, len(trained_supports), f"{tag_base}_neutral"),
                        "predictor_public": plans_for_supports(
                            group_key,
                            public_supports,
                            f"{tag_base}_public",
                        ),
                        "predictor_trained": plans_for_supports(
                            group_key,
                            trained_supports,
                            f"{tag_base}_trained",
                        ),
                        "rotated": plans_for_supports(
                            group_key,
                            rotated_supports,
                            f"{tag_base}_rotated",
                        ),
                    }
                    support_meta.append(
                        {
                            "factor_base_size": fb_size,
                            "group_key": group_key,
                            "predictor_pair_count": len(predictor_pairs),
                            "public_support_count": len(public_supports),
                            "rotated_support_count": len(rotated_supports),
                            "schedule_fraction": ratio(len(predictor_pairs), fb_size * (fb_size - 1) // 2),
                            "selected_support_count": len(trained_supports),
                            "trained_match_count": len(trained_matches),
                        }
                    )
                    case = p784.case_from_group(
                        base_groups[group_key],
                        p784.TRIM12_DELTA,
                        str(args.generator_namespace),
                        "p840",
                        p784.DEST_SEED_COUNT,
                        p784.DEST_POOL_COUNT,
                    )
                    for policy_name, plans in policies.items():
                        rows, order = p799.collect_rows_for_policy(
                            p746,
                            p748,
                            relprobe,
                            str(base_groups[group_key]["target"]),
                            case,
                            plans,
                            f"p840_{policy_name}_{clause_score['name']}",
                            args,
                        )
                        target_results[policy_name].append(
                            p799.evaluate_generated_policy(
                                p797,
                                p793,
                                p792,
                                p789,
                                train_prepared[group_key],
                                trained,
                                rows,
                                order,
                                str(base_groups[group_key]["target"]),
                                f"p840_{policy_name}_{clause_score['name']}",
                                args,
                            )
                        )
                policy_results = []
                for policy_name, items in target_results.items():
                    item = aggregate_policy_results(items, policy_name)
                    item["budget"] = int(budget)
                    item["clause"] = list(clause)
                    item["clause_name"] = clause_score["name"]
                    item["schedule_name"] = schedule_name
                    policy_results.append(item)
                by_name = {item["policy"]["name"]: item for item in policy_results}
                for item in policy_results:
                    if item["policy"]["name"] in {"predictor_public", "predictor_trained"}:
                        item["policy_claim"] = classify_policy(item, by_name)
                    else:
                        item["policy_claim"] = "predictor_control"
                    all_policy_results.append(item)
                policy_results.sort(
                    key=lambda item: (
                        item["aggregate"]["recovered_row_count"],
                        item["aggregate"]["intended_support_hit_row_count"],
                        -(item["aggregate"]["generated_once_train_total_unit_cost_over_recovered_rho"] or 10**9),
                        item["policy"]["name"],
                    ),
                    reverse=True,
                )
                schedule_results.append(
                    {
                        "budget": int(budget),
                        "clause": list(clause),
                        "clause_name": clause_score["name"],
                        "clause_score": clause_score,
                        "policy_results": policy_results,
                        "schedule_name": schedule_name,
                        "source_name": spec["source_name"],
                        "support_meta": support_meta,
                    }
                )
    claim_status = determine_claim(schedule_results)
    predictor_policies = [
        item
        for item in all_policy_results
        if item["policy"]["name"] in {"predictor_public", "predictor_trained"}
    ]
    best_policy = None
    if predictor_policies:
        best_policy = max(
            predictor_policies,
            key=lambda item: (
                int(item["aggregate"]["recovered_row_count"]),
                int(item["aggregate"]["intended_support_hit_row_count"]),
                -(item["aggregate"]["generated_once_train_total_unit_cost_over_recovered_rho"] or 10**9),
                item["policy"]["name"],
            ),
        )
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p799_script": str(P799_SCRIPT),
            "p835_script": str(P835_SCRIPT),
            "p837_script": str(P837_SCRIPT),
            "p837_summary": str(args.p837_summary),
            "p838_script": str(P838_SCRIPT),
            "script": str(Path(__file__)),
        },
        "claim_status": claim_status,
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "PUBLIC-PREDICTOR AUDIT: P840 chooses support predicates before generated rows are observed.",
            "CONTROL-BOUND: predictor policies must beat neutral and rotated support controls.",
            "PREFIX-BOUNDARY: support pairs still seed the row generator; the tested change is public predicate selection, not a new algebraic constructor.",
            "POLLARD-RHO BOUNDARY: this is a relation-generation subproblem and not a complete faster-than-rho ECDLP algorithm.",
            "NO DEPLOYED-CURVE CLAIM: no production-key relevance or deployed-prime break is implied.",
        ],
        "method": "p840_public_support_predictor_audit",
        "parameters": {
            "budgets": budgets,
            "field_weight": int(args.field_weight),
            "generator_namespace": str(args.generator_namespace),
            "max_clauses_per_schedule": int(args.max_clauses_per_schedule),
            "max_items_per_target": int(args.max_items_per_target),
            "max_schedules": int(args.max_schedules),
            "seeds_per_prefix": int(args.seeds_per_prefix),
            "train_replicas": int(args.train_replicas),
            "train_seed_namespace": str(args.train_seed_namespace),
        },
        "public_support_predictor": {
            "best_predictor_policy": best_policy,
            "schedule_results": schedule_results,
        },
        "red_team_handoff": {
            "assumptions": [
                "Calibration-ranked support overlap is allowed as a pre-generation public predictor score.",
                "Individual support clauses are narrower and more falsifiable than full schedule unions.",
                "Rotated supports are the relevant control for pair-shaped generator salting.",
            ],
            "failure_modes": [
                "A public predictor can preserve recovered rows without increasing exact intended-support hits.",
                "Clause ranking may overfit calibration supports and fail on fresh schedules.",
                "Even a positive relation-generation signal still needs rank and target-descent integration.",
            ],
            "next_concrete_action": (
                "If a predictor beats controls, replicate across generator namespaces and integrate its measured rate into the P836/P826 residual-gap model; "
                "otherwise move to public slice predictors from the quotient/slice branch."
            ),
        },
        "schema": SCHEMA,
    }


def summary_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    compact_results = []
    for result in payload["public_support_predictor"]["schedule_results"]:
        compact_results.append(
            {
                "budget": result["budget"],
                "clause": result["clause"],
                "clause_name": result["clause_name"],
                "clause_score": result["clause_score"],
                "policy_results": [
                    compact_policy(item, result["support_meta"])
                    for item in result["policy_results"]
                ],
                "schedule_name": result["schedule_name"],
                "source_name": result["source_name"],
                "support_meta": result["support_meta"],
            }
        )
    best = payload["public_support_predictor"]["best_predictor_policy"]
    best_compact = None
    if best is not None:
        matching = next(
            result
            for result in payload["public_support_predictor"]["schedule_results"]
            if result["schedule_name"] == best["schedule_name"] and result["clause_name"] == best["clause_name"]
        )
        best_compact = compact_policy(best, matching["support_meta"])
        best_compact["clause_name"] = best["clause_name"]
        best_compact["schedule_name"] = best["schedule_name"]
    return {
        **payload,
        "schema": f"{SCHEMA}.summary",
        "public_support_predictor": {
            "best_predictor_policy": best_compact,
            "schedule_results": compact_results,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p777-summary", type=Path, default=DEFAULT_P777_SUMMARY)
    parser.add_argument("--p786-summary", type=Path, default=DEFAULT_P786_SUMMARY)
    parser.add_argument("--p837-summary", type=Path, default=DEFAULT_P837_SUMMARY)
    parser.add_argument("--train-seed-namespace", default="supportline20-v1")
    parser.add_argument("--generator-namespace", default="p840-public-support-predictor-v1")
    parser.add_argument("--train-replicas", type=int, default=20)
    parser.add_argument("--control-count", type=int, default=8)
    parser.add_argument("--field-weight", type=int, default=2)
    parser.add_argument("--min-line-rows", type=int, default=2)
    parser.add_argument("--budgets", default="128")
    parser.add_argument("--max-clauses-per-schedule", type=int, default=2)
    parser.add_argument("--max-items-per-target", type=int, default=12)
    parser.add_argument("--max-schedules", type=int, default=2)
    parser.add_argument("--seeds-per-prefix", type=int, default=3)
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
                "best_predictor_policy": summary["public_support_predictor"]["best_predictor_policy"],
                "claim_status": summary["claim_status"],
                "schedule_results": [
                    {
                        "clause_name": item["clause_name"],
                        "policies": [
                            {
                                "claim": policy["policy_claim"],
                                "intended": policy["aggregate"]["intended_support_hit_row_count"],
                                "name": policy["policy"]["name"],
                                "ratio": policy["aggregate"]["generated_once_train_total_unit_cost_over_recovered_rho"],
                                "recovered": policy["aggregate"]["recovered_row_count"],
                            }
                            for policy in item["policy_results"]
                        ],
                        "schedule_name": item["schedule_name"],
                    }
                    for item in summary["public_support_predictor"]["schedule_results"]
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
