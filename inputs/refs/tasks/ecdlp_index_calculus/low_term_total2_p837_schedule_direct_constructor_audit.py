#!/usr/bin/env python3
"""P837 direct-constructor audit for P836 support schedules."""

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
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P777_SUMMARY = STATE_DIR / "low_term_total2_p777_merged_trim12_factor_first_cost_audit_summary.json"
DEFAULT_P786_SUMMARY = STATE_DIR / "low_term_total2_p786_public_coordinate_bridge_summary.json"
DEFAULT_P836_SUMMARY = STATE_DIR / "low_term_total2_p836_schedule_constrained_rule_list_audit_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p837_schedule_direct_constructor_audit_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p837_schedule_direct_constructor_audit.md"
SCHEMA = "ecdlp.low_term_total2_p837_schedule_direct_constructor_audit.v1"


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


def parse_clause(raw: str) -> tuple[str, ...]:
    return tuple(part.strip() for part in str(raw).split("&&") if part.strip())


def support_matches_clause(p835: Any, support: tuple[int, int], clause: tuple[str, ...]) -> bool:
    tags = p835.support_tags_for_pair(int(support[0]), int(support[1]))
    return all(tag in tags for tag in clause)


def support_matches_any_clause(p835: Any, support: tuple[int, int], clauses: list[tuple[str, ...]]) -> bool:
    return any(support_matches_clause(p835, support, clause) for clause in clauses)


def ranked_supports_from_trained(trained: dict[tuple[int, int, int, int], dict[str, Any]]) -> list[tuple[int, int]]:
    scores: dict[tuple[int, int], Counter] = {}
    for line_key, value in trained.items():
        support = tuple(int(part) for part in line_key[:2])
        item = scores.setdefault(support, Counter())
        item["line_count"] += 1
        item["candidate_row_count"] += int(value.get("candidate_row_count") or 0)
        item["candidate_form_count"] += int(value.get("candidate_form_count") or 0)
    return sorted(
        scores,
        key=lambda support: (
            scores[support]["candidate_row_count"],
            scores[support]["candidate_form_count"],
            scores[support]["line_count"],
            -sum(support),
            tuple(-part for part in support),
        ),
        reverse=True,
    )


def stable_sample(items: list[tuple[int, int]], count: int, salt: str) -> list[tuple[int, int]]:
    salt_value = sum((index + 1) * ord(ch) for index, ch in enumerate(str(salt)))
    ranked = sorted(
        set(tuple(int(part) for part in item) for item in items),
        key=lambda pair: (
            (pair[0] * 1_315_423_911 + pair[1] * 2_654_435_761 + salt_value) % 1_000_000_007,
            pair[0],
            pair[1],
        ),
    )
    return ranked[: int(count)]


def schedule_union_pairs(p835: Any, factor_base_size: int, clauses: list[tuple[str, ...]]) -> list[tuple[int, int]]:
    pairs: set[tuple[int, int]] = set()
    for clause in clauses:
        pairs.update(p835.support_pair_set(int(factor_base_size), clause))
    return sorted(pairs)


def rotated_supports(supports: list[tuple[int, int]], factor_base_size: int) -> list[tuple[int, int]]:
    out = []
    fb = int(factor_base_size)
    for left, right in supports:
        shifted = tuple(sorted(((int(left) + 1) % fb, (int(right) + 3) % fb)))
        if shifted[0] != shifted[1]:
            out.append((int(shifted[0]), int(shifted[1])))
    return sorted(set(out))


def plans_for_supports(group_key: str, supports: list[tuple[int, int]], tag_prefix: str) -> list[dict[str, Any]]:
    return [
        {
            "group_key": group_key,
            "intended_line": None,
            "intended_support": tuple(int(part) for part in support),
            "tag": f"{tag_prefix}_{support[0]}_{support[1]}",
        }
        for support in supports
    ]


def neutral_plans(group_key: str, count: int, tag_prefix: str) -> list[dict[str, Any]]:
    return [
        {
            "group_key": group_key,
            "intended_line": None,
            "intended_support": None,
            "tag": f"{tag_prefix}_{index:03d}",
        }
        for index in range(int(count))
    ]


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


def compact_policy(item: dict[str, Any]) -> dict[str, Any]:
    aggregate = item["aggregate"]
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
        "target_count",
    ]
    return {
        "aggregate": {key: aggregate.get(key) for key in keep},
        "policy": item["policy"],
        "policy_claim": item.get("policy_claim"),
    }


def policy_claim(item: dict[str, Any], controls: dict[str, dict[str, Any]]) -> str:
    aggregate = item["aggregate"]
    recovered = int(aggregate["recovered_row_count"])
    if int(aggregate["generated_row_count"]) == 0:
        return "no_generated_rows"
    control_recovered = max(
        int((controls.get("neutral_salted") or {}).get("aggregate", {}).get("recovered_row_count") or 0),
        int((controls.get("rotated_schedule_salted") or {}).get("aggregate", {}).get("recovered_row_count") or 0),
    )
    ratio_value = aggregate["generated_once_train_total_unit_cost_over_recovered_rho"] or 10**9
    if recovered > control_recovered and float(ratio_value) < 1.0:
        return "schedule_salted_below_rho_beats_controls"
    if recovered > control_recovered:
        return "schedule_salted_enrichment_cost_boundary"
    if item["policy"]["name"] in {"neutral_salted", "rotated_schedule_salted"}:
        return "prefix_control"
    return "does_not_beat_prefix_controls"


def residual_gap(summary: dict[str, Any]) -> dict[str, Any]:
    row_population = summary["row_population"]
    p826_ratio = float(row_population["full_p826_reconstructed_charge_model"]["post_hit_total_cost_over_recovered_rho"])
    p836_model = row_population["p835_schedule_adjusted_model"]
    best = summary["schedule_constrained_rule_list"]["best_schedule_constrained"]["schedule_adjusted_charge_model"]
    target_total = p826_ratio * float(best["recovered_rho_baseline"])
    return {
        "p826_cost_over_rho": p826_ratio,
        "p836_cost_over_rho": best["post_hit_total_cost_over_recovered_rho"],
        "p836_total_cost": int(best["post_hit_total_cost"]),
        "p836_recovered_rho_baseline": int(best["recovered_rho_baseline"]),
        "p836_to_p826_gap_cost_units": round(float(best["post_hit_total_cost"]) - target_total, 8),
        "p836_to_p826_gap_ratio": round(
            float(best["post_hit_total_cost_over_recovered_rho"]) - p826_ratio,
            8,
        ),
        "p835_cost_over_rho": p836_model["post_hit_total_cost_over_recovered_rho"],
    }


def determine_claim(schedule_results: list[dict[str, Any]], gap: dict[str, Any]) -> str:
    claims = [item["policy_claim"] for result in schedule_results for item in result["policy_results"]]
    if "schedule_salted_below_rho_beats_controls" in claims:
        return "P837_SCHEDULE_SALTED_DIRECT_GENERATOR_BELOW_RHO_SIGNAL"
    if "schedule_salted_enrichment_cost_boundary" in claims:
        return "P837_SCHEDULE_SALTED_DIRECT_GENERATOR_ENRICHMENT_BOUNDARY"
    return "NEGATIVE_RESULT_P837_PREFIX_SALTING_DOES_NOT_CLOSE_DIRECT_CONSTRUCTOR_GAP"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p799 = load_module("ecdlp_p799_for_p837", P799_SCRIPT)
    p835 = load_module("ecdlp_p835_for_p837", P835_SCRIPT)
    p798 = p799.load_module("ecdlp_p798_for_p837", p799.P798_SCRIPT)
    p797 = p798.load_module("ecdlp_p797_for_p837", p798.P797_SCRIPT)
    p796 = p797.load_module("ecdlp_p796_for_p837", p797.P796_SCRIPT)
    p795 = p796.load_module("ecdlp_p795_for_p837", p796.P795_SCRIPT)
    p794 = p795.load_module("ecdlp_p794_for_p837", p795.P794_SCRIPT)
    p793 = p794.load_module("ecdlp_p793_for_p837", p794.P793_SCRIPT)
    p792 = p793.load_module("ecdlp_p792_for_p837", p793.P792_SCRIPT)
    p789 = p792.load_module("ecdlp_p789_for_p837", p792.P789_SCRIPT)
    p788 = p789.load_module("ecdlp_p788_for_p837", p789.P788_SCRIPT)
    p787 = p788.load_module("ecdlp_p787_for_p837", p788.P787_SCRIPT)
    p786 = p787.load_module("ecdlp_p786_for_p837", p787.P786_SCRIPT)
    p784 = p786.load_module("ecdlp_p784_for_p837", p786.P784_SCRIPT)
    p782 = p784.load_module("ecdlp_p782_for_p837", p784.P782_SCRIPT)
    p780 = p782.load_module("ecdlp_p780_for_p837", p782.P780_SCRIPT)
    stack = p780.load_stack()
    p746 = stack["p746"]
    p748 = stack["p748"]
    relprobe = stack["relprobe"]
    p836 = load_json(args.p836_summary)
    best = p836["schedule_constrained_rule_list"]["best_schedule_constrained"]
    diagnostics = best["diagnostics"]
    gap = residual_gap(p836)
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
        for diagnostic in diagnostics:
            schedule_name = str(diagnostic["heldout_namespace"])
            clauses = [parse_clause(raw) for raw in diagnostic["selected_rules"]]
            target_policy_results: dict[str, list[dict[str, Any]]] = {
                "neutral_salted": [],
                "rotated_schedule_salted": [],
                "schedule_salted": [],
                "schedule_union_salted": [],
            }
            schedule_meta = []
            for group_key in required:
                trained = p794.selected_calibrations(train_prepared[group_key]["all_calibrated"], int(budget))
                ranked = ranked_supports_from_trained(trained)
                fb_size = int(base_groups[group_key]["factor_base_size"])
                schedule_pairs = schedule_union_pairs(p835, fb_size, clauses)
                trained_schedule = [
                    support
                    for support in ranked
                    if support_matches_any_clause(p835, support, clauses)
                ][: int(args.max_items_per_target)]
                union_sample = stable_sample(
                    schedule_pairs,
                    int(args.max_items_per_target),
                    f"{schedule_name}:{group_key}:union:{budget}",
                )
                if not trained_schedule:
                    trained_schedule = union_sample
                rotated = rotated_supports(trained_schedule, fb_size)[: len(trained_schedule)]
                case = p784.case_from_group(
                    base_groups[group_key],
                    p784.TRIM12_DELTA,
                    str(args.generator_namespace),
                    "p837",
                    p784.DEST_SEED_COUNT,
                    p784.DEST_POOL_COUNT,
                )
                policies = {
                    "neutral_salted": neutral_plans(group_key, len(trained_schedule), f"neutral_{slug(schedule_name)}"),
                    "rotated_schedule_salted": plans_for_supports(
                        group_key,
                        rotated,
                        f"rot_{slug(schedule_name)}",
                    ),
                    "schedule_salted": plans_for_supports(
                        group_key,
                        trained_schedule,
                        f"sch_{slug(schedule_name)}",
                    ),
                    "schedule_union_salted": plans_for_supports(
                        group_key,
                        union_sample,
                        f"uni_{slug(schedule_name)}",
                    ),
                }
                schedule_meta.append(
                    {
                        "budget": int(budget),
                        "factor_base_size": fb_size,
                        "group_key": group_key,
                        "schedule_pair_count": len(schedule_pairs),
                        "schedule_union_fraction": ratio(len(schedule_pairs), fb_size * (fb_size - 1) // 2),
                        "selected_trained_schedule_support_count": len(trained_schedule),
                        "union_sample_count": len(union_sample),
                    }
                )
                for policy_name, plans in policies.items():
                    if not plans:
                        continue
                    rows, order = p799.collect_rows_for_policy(
                        p746,
                        p748,
                        relprobe,
                        str(base_groups[group_key]["target"]),
                        case,
                        plans,
                        policy_name,
                        args,
                    )
                    target_policy_results[policy_name].append(
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
                            policy_name,
                            args,
                        )
                    )
            policy_results = []
            for policy_name, items in target_policy_results.items():
                if not items:
                    continue
                policy_results.append(aggregate_policy_results(items, policy_name))
            by_name = {item["policy"]["name"]: item for item in policy_results}
            for item in policy_results:
                item["budget"] = int(budget)
                item["schedule_name"] = schedule_name
                item["policy_claim"] = policy_claim(item, by_name)
                all_policy_results.append(item)
            policy_results.sort(
                key=lambda item: (
                    item["aggregate"]["generated_once_train_total_unit_cost_over_recovered_rho"] or 10**9,
                    -int(item["aggregate"]["recovered_row_count"]),
                    item["policy"]["name"],
                )
            )
            schedule_results.append(
                {
                    "budget": int(budget),
                    "clauses": [list(clause) for clause in clauses],
                    "policy_results": policy_results,
                    "schedule_meta": schedule_meta,
                    "schedule_name": schedule_name,
                }
            )
    best_generated = None
    viable = [
        item
        for item in all_policy_results
        if item["aggregate"]["generated_once_train_total_unit_cost_over_recovered_rho"] is not None
    ]
    if viable:
        best_generated = min(
            viable,
            key=lambda item: (
                item["aggregate"]["generated_once_train_total_unit_cost_over_recovered_rho"],
                -int(item["aggregate"]["recovered_row_count"]),
                item["policy"]["name"],
            ),
        )
    claim_status = determine_claim(schedule_results, gap)
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p777_summary": str(args.p777_summary),
            "p786_summary": str(args.p786_summary),
            "p799_script": str(P799_SCRIPT),
            "p835_script": str(P835_SCRIPT),
            "p836_summary": str(args.p836_summary),
            "script": str(Path(__file__)),
        },
        "claim_status": claim_status,
        "created_at": now_iso(),
        "direct_constructor": {
            "best_generated": best_generated,
            "p836_residual_gap": gap,
            "schedule_results": schedule_results,
        },
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "DIRECT-CONSTRUCTOR MICRO-AUDIT: P837 runs real P799 prefix-salted row generation for sampled support pairs satisfying P836 public schedules.",
            "PREFIX-SALTING ONLY: intended support pairs are encoded in deterministic public seed prefixes; this is not yet an algebraic generator that forces support membership.",
            "CONTROL-BOUND: neutral and rotated schedule prefixes are charged as controls.",
            "POLLARD-RHO BOUNDARY: generated-policy cost/rho is a micro-generator metric and is not a complete faster-than-rho ECDLP algorithm.",
            "NO DEPLOYED-CURVE CLAIM: no production-key relevance or deployed-prime break is implied.",
        ],
        "method": "p837_schedule_direct_constructor_audit",
        "parameters": {
            "budgets": budgets,
            "control_count": int(args.control_count),
            "field_weight": int(args.field_weight),
            "generator_namespace": str(args.generator_namespace),
            "max_items_per_target": int(args.max_items_per_target),
            "max_relations": int(args.max_relations),
            "max_subsets": int(args.max_subsets),
            "seeds_per_prefix": int(args.seeds_per_prefix),
            "train_replicas": int(args.train_replicas),
            "train_seed_namespace": str(args.train_seed_namespace),
            "walk_mode": str(args.walk_mode),
            "width": int(args.width),
        },
        "red_team_handoff": {
            "assumptions": [
                "Prefix salting can expose whether P836 support schedules are useful to the existing row generator.",
                "Trained support-pair overlap is public calibration data, not held-out recovery labels.",
                "P836 residual-gap accounting remains separate from generated-policy micro-benchmark ratios.",
            ],
            "failure_modes": [
                "Prefix salting may not actually force support membership.",
                "Small support-pair samples can miss rare schedule hits.",
                "A positive generated micro-benchmark still needs integration into the P826/P836 held-out charge model.",
            ],
            "next_concrete_action": (
                "If schedule_salted beats controls, expand pair samples and integrate the measured generated_online rate "
                "into the P836 held-out accounting; otherwise test stronger seed material that actually constructs desired support forms."
            ),
        },
        "schema": SCHEMA,
    }


def summary_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    compact_schedule_results = []
    for item in payload["direct_constructor"]["schedule_results"]:
        compact_schedule_results.append(
            {
                "budget": item["budget"],
                "clauses": item["clauses"],
                "policy_results": [compact_policy(policy) for policy in item["policy_results"]],
                "schedule_meta": item["schedule_meta"],
                "schedule_name": item["schedule_name"],
            }
        )
    best = payload["direct_constructor"]["best_generated"]
    return {
        **payload,
        "direct_constructor": {
            "best_generated": None if best is None else compact_policy(best),
            "p836_residual_gap": payload["direct_constructor"]["p836_residual_gap"],
            "schedule_results": compact_schedule_results,
        },
        "schema": f"{SCHEMA}.summary",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p777-summary", type=Path, default=DEFAULT_P777_SUMMARY)
    parser.add_argument("--p786-summary", type=Path, default=DEFAULT_P786_SUMMARY)
    parser.add_argument("--p836-summary", type=Path, default=DEFAULT_P836_SUMMARY)
    parser.add_argument("--train-seed-namespace", default="supportline20-v1")
    parser.add_argument("--generator-namespace", default="p837-schedule-direct-v1")
    parser.add_argument("--train-replicas", type=int, default=20)
    parser.add_argument("--control-count", type=int, default=8)
    parser.add_argument("--field-weight", type=int, default=2)
    parser.add_argument("--min-line-rows", type=int, default=2)
    parser.add_argument("--budgets", default="128")
    parser.add_argument("--max-items-per-target", type=int, default=8)
    parser.add_argument("--seeds-per-prefix", type=int, default=2)
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
                "best_generated": summary["direct_constructor"]["best_generated"],
                "claim_status": summary["claim_status"],
                "p836_residual_gap": summary["direct_constructor"]["p836_residual_gap"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
