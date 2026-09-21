#!/usr/bin/env python3
"""P838 support-forcing seed-material audit for P837-positive schedules."""

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
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P777_SUMMARY = STATE_DIR / "low_term_total2_p777_merged_trim12_factor_first_cost_audit_summary.json"
DEFAULT_P786_SUMMARY = STATE_DIR / "low_term_total2_p786_public_coordinate_bridge_summary.json"
DEFAULT_P837_SUMMARY = STATE_DIR / "low_term_total2_p837_schedule_direct_constructor_audit_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p838_support_forcing_seed_material_audit_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p838_support_forcing_seed_material_audit.md"
SCHEMA = "ecdlp.low_term_total2_p838_support_forcing_seed_material_audit.v1"


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


def csv_strings(raw: str) -> list[str]:
    return [part.strip() for part in str(raw).split(",") if part.strip()]


def slug(value: str) -> str:
    text = "".join(ch if ch.isalnum() else "_" for ch in str(value))
    return "_".join(part for part in text.split("_") if part)


def parse_clause(raw: str) -> tuple[str, ...]:
    return tuple(part.strip() for part in str(raw).split("&&") if part.strip())


def support_tags_for(p835: Any, support: tuple[int, int]) -> set[str]:
    return p835.support_tags_for_pair(int(support[0]), int(support[1]))


def support_matches_any_clause(p835: Any, support: tuple[int, int], clauses: list[tuple[str, ...]]) -> bool:
    tags = support_tags_for(p835, support)
    return any(all(tag in tags for tag in clause) for clause in clauses)


def matching_clause_name(p835: Any, support: tuple[int, int], clauses: list[tuple[str, ...]]) -> str:
    tags = support_tags_for(p835, support)
    for clause in clauses:
        if all(tag in tags for tag in clause):
            return "_".join(slug(tag) for tag in clause)
    return "no_clause"


def encode_tag(
    p835: Any,
    support: tuple[int, int],
    encoding: str,
    schedule_name: str,
    group_key: str,
    source_name: str,
    clauses: list[tuple[str, ...]],
) -> str:
    left, right = int(support[0]), int(support[1])
    span = abs(right - left)
    support_sum = left + right
    base = f"{slug(schedule_name)}_{slug(source_name)}"
    if encoding == "plain":
        return f"{base}_pair_{left}_{right}"
    if encoding == "repeat":
        return f"{base}_pair_{left}_{right}_again_{left}_{right}_sum_{support_sum}"
    if encoding == "mods":
        return (
            f"{base}_l{left}_r{right}_s{support_sum}_d{span}_"
            f"lm{left % 8}_rm{right % 8}_sm{support_sum % 16}_dm{span % 16}"
        )
    if encoding == "clause":
        return f"{base}_{matching_clause_name(p835, support, clauses)}_l{left}_r{right}"
    if encoding == "group":
        return f"{base}_{slug(group_key)}_l{left}_r{right}_sum{support_sum}_span{span}"
    raise ValueError(f"unknown encoding {encoding!r}")


def encoded_plans(
    p835: Any,
    group_key: str,
    supports: list[tuple[int, int]],
    encoding: str,
    schedule_name: str,
    source_name: str,
    clauses: list[tuple[str, ...]],
) -> list[dict[str, Any]]:
    return [
        {
            "group_key": group_key,
            "intended_line": None,
            "intended_support": tuple(int(part) for part in support),
            "tag": encode_tag(p835, support, encoding, schedule_name, group_key, source_name, clauses),
        }
        for support in supports
    ]


def neutral_plans(count: int, encoding: str, schedule_name: str, group_key: str, source_name: str) -> list[dict[str, Any]]:
    base = f"neutral_{slug(schedule_name)}_{slug(group_key)}_{slug(source_name)}_{slug(encoding)}"
    return [
        {
            "group_key": group_key,
            "intended_line": None,
            "intended_support": None,
            "tag": f"{base}_{index:03d}",
        }
        for index in range(int(count))
    ]


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
        "encoding": item.get("encoding"),
        "policy": item["policy"],
        "policy_claim": item.get("policy_claim"),
        "schedule_name": item.get("schedule_name"),
        "source_name": item.get("source_name"),
    }


def aggregate_policy_results(items: list[dict[str, Any]], policy_name: str) -> dict[str, Any]:
    totals = Counter()
    for item in items:
        aggregate = item["aggregate"]
        for key, value in aggregate.items():
            if isinstance(value, int):
                totals[key] += value
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
            "primary_minus_max_control_recovered_rows": int(totals["recovered_row_count"])
            - int(totals.get("max_control_recovered_row_count") or 0),
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


def classify_schedule_policy(item: dict[str, Any], controls: dict[str, dict[str, Any]]) -> str:
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
        return "intended_support_hit_lift_with_recovery_preserved"
    if intended_hits > control_intended:
        return "intended_support_hit_lift_only"
    if recovered > control_recovered:
        return "recovery_enrichment_without_intended_lift"
    return "does_not_beat_controls"


def positive_schedule_specs(p837_summary: dict[str, Any]) -> list[dict[str, Any]]:
    specs = []
    for result in p837_summary["direct_constructor"]["schedule_results"]:
        positives = [
            item
            for item in result["policy_results"]
            if item.get("policy_claim") == "schedule_salted_enrichment_cost_boundary"
        ]
        if not positives:
            continue
        best = min(
            positives,
            key=lambda item: (
                item["aggregate"]["generated_once_train_total_unit_cost_over_recovered_rho"] or 10**9,
                -int(item["aggregate"]["recovered_row_count"]),
                item["policy"]["name"],
            ),
        )
        source_name = "union" if "union" in best["policy"]["name"] else "trained"
        specs.append(
            {
                "best_p837_policy": best["policy"]["name"],
                "clauses": [tuple(clause) for clause in result["clauses"]],
                "schedule_name": result["schedule_name"],
                "source_name": source_name,
            }
        )
    return specs


def determine_claim(results: list[dict[str, Any]]) -> str:
    claims = [policy["policy_claim"] for result in results for policy in result["policy_results"]]
    if "intended_support_hit_lift_with_recovery_preserved" in claims:
        return "P838_PREFIX_ENCODING_IMPROVES_INTENDED_SUPPORT_HITS"
    if "intended_support_hit_lift_only" in claims:
        return "P838_PREFIX_ENCODING_INTENDED_HIT_LIFT_WITH_RECOVERY_LOSS"
    if "recovery_enrichment_without_intended_lift" in claims:
        return "P838_RECOVERY_ENRICHMENT_WITHOUT_SUPPORT_FORCING"
    return "NEGATIVE_RESULT_P838_PREFIX_ENCODINGS_DO_NOT_FORCE_SUPPORT"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p799 = load_module("ecdlp_p799_for_p838", P799_SCRIPT)
    p835 = load_module("ecdlp_p835_for_p838", P835_SCRIPT)
    p837 = load_module("ecdlp_p837_for_p838", P837_SCRIPT)
    p798 = p799.load_module("ecdlp_p798_for_p838", p799.P798_SCRIPT)
    p797 = p798.load_module("ecdlp_p797_for_p838", p798.P797_SCRIPT)
    p796 = p797.load_module("ecdlp_p796_for_p838", p797.P796_SCRIPT)
    p795 = p796.load_module("ecdlp_p795_for_p838", p796.P795_SCRIPT)
    p794 = p795.load_module("ecdlp_p794_for_p838", p795.P794_SCRIPT)
    p793 = p794.load_module("ecdlp_p793_for_p838", p794.P793_SCRIPT)
    p792 = p793.load_module("ecdlp_p792_for_p838", p793.P792_SCRIPT)
    p789 = p792.load_module("ecdlp_p789_for_p838", p792.P789_SCRIPT)
    p788 = p789.load_module("ecdlp_p788_for_p838", p789.P788_SCRIPT)
    p787 = p788.load_module("ecdlp_p787_for_p838", p788.P787_SCRIPT)
    p786 = p787.load_module("ecdlp_p786_for_p838", p787.P786_SCRIPT)
    p784 = p786.load_module("ecdlp_p784_for_p838", p786.P784_SCRIPT)
    p782 = p784.load_module("ecdlp_p782_for_p838", p784.P782_SCRIPT)
    p780 = p782.load_module("ecdlp_p780_for_p838", p782.P780_SCRIPT)
    stack = p780.load_stack()
    p746 = stack["p746"]
    p748 = stack["p748"]
    relprobe = stack["relprobe"]
    p837_summary = load_json(args.p837_summary)
    specs = positive_schedule_specs(p837_summary)
    selected_specs = specs[: int(args.max_schedules)]
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
    encodings = csv_strings(args.encodings)
    all_policy_results = []
    schedule_results = []
    for budget in budgets:
        print(f"scoring budget {budget}", flush=True)
        for spec in selected_specs:
            schedule_name = str(spec["schedule_name"])
            clauses = [tuple(clause) for clause in spec["clauses"]]
            source_name = str(spec["source_name"])
            for encoding in encodings:
                target_results: dict[str, list[dict[str, Any]]] = {
                    "neutral": [],
                    "rotated": [],
                    "schedule": [],
                }
                support_meta = []
                for group_key in required:
                    trained = p794.selected_calibrations(train_prepared[group_key]["all_calibrated"], int(budget))
                    ranked = p837.ranked_supports_from_trained(trained)
                    fb_size = int(base_groups[group_key]["factor_base_size"])
                    schedule_pairs = p837.schedule_union_pairs(p835, fb_size, clauses)
                    trained_schedule = [
                        support
                        for support in ranked
                        if support_matches_any_clause(p835, support, clauses)
                    ][: int(args.max_items_per_target)]
                    union_sample = p837.stable_sample(
                        schedule_pairs,
                        int(args.max_items_per_target),
                        f"{schedule_name}:{group_key}:{encoding}:union:{budget}",
                    )
                    supports = union_sample if source_name == "union" else trained_schedule
                    if not supports:
                        supports = union_sample
                    rotated = p837.rotated_supports(supports, fb_size)[: len(supports)]
                    case = p784.case_from_group(
                        base_groups[group_key],
                        p784.TRIM12_DELTA,
                        str(args.generator_namespace),
                        "p838",
                        p784.DEST_SEED_COUNT,
                        p784.DEST_POOL_COUNT,
                    )
                    policies = {
                        "neutral": neutral_plans(len(supports), encoding, schedule_name, group_key, source_name),
                        "rotated": encoded_plans(
                            p835,
                            group_key,
                            rotated,
                            encoding,
                            schedule_name,
                            f"rotated_{source_name}",
                            clauses,
                        ),
                        "schedule": encoded_plans(
                            p835,
                            group_key,
                            supports,
                            encoding,
                            schedule_name,
                            source_name,
                            clauses,
                        ),
                    }
                    support_meta.append(
                        {
                            "encoding": encoding,
                            "factor_base_size": fb_size,
                            "group_key": group_key,
                            "rotated_support_count": len(rotated),
                            "schedule_pair_count": len(schedule_pairs),
                            "schedule_union_fraction": ratio(len(schedule_pairs), fb_size * (fb_size - 1) // 2),
                            "selected_support_count": len(supports),
                            "source_name": source_name,
                            "trained_schedule_support_count": len(trained_schedule),
                            "union_sample_count": len(union_sample),
                        }
                    )
                    for policy_name, plans in policies.items():
                        rows, order = p799.collect_rows_for_policy(
                            p746,
                            p748,
                            relprobe,
                            str(base_groups[group_key]["target"]),
                            case,
                            plans,
                            f"p838_{policy_name}_{encoding}_{source_name}",
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
                                f"p838_{policy_name}_{encoding}_{source_name}",
                                args,
                            )
                        )
                policy_results = []
                for policy_name, items in target_results.items():
                    item = aggregate_policy_results(items, policy_name)
                    item["budget"] = int(budget)
                    item["encoding"] = encoding
                    item["schedule_name"] = schedule_name
                    item["source_name"] = source_name
                    policy_results.append(item)
                by_name = {item["policy"]["name"]: item for item in policy_results}
                for item in policy_results:
                    if item["policy"]["name"] == "schedule":
                        item["policy_claim"] = classify_schedule_policy(item, by_name)
                    elif item["policy"]["name"] in {"neutral", "rotated"}:
                        item["policy_claim"] = "prefix_control"
                    all_policy_results.append(item)
                policy_results.sort(
                    key=lambda item: (
                        item["aggregate"]["intended_support_hit_rate"] or 0.0,
                        item["aggregate"]["recovered_row_count"],
                        -(item["aggregate"]["generated_once_train_total_unit_cost_over_recovered_rho"] or 10**9),
                        item["policy"]["name"],
                    ),
                    reverse=True,
                )
                schedule_results.append(
                    {
                        "budget": int(budget),
                        "clauses": [list(clause) for clause in clauses],
                        "encoding": encoding,
                        "policy_results": policy_results,
                        "schedule_name": schedule_name,
                        "source_name": source_name,
                        "support_meta": support_meta,
                    }
                )
    schedule_policies = [item for item in all_policy_results if item["policy"]["name"] == "schedule"]
    best_intended = None
    if schedule_policies:
        best_intended = max(
            schedule_policies,
            key=lambda item: (
                int(item["aggregate"]["intended_support_hit_row_count"]),
                int(item["aggregate"]["recovered_row_count"]),
                -(item["aggregate"]["generated_once_train_total_unit_cost_over_recovered_rho"] or 10**9),
                item.get("schedule_name") or "",
                item.get("encoding") or "",
            ),
        )
    claim_status = determine_claim(schedule_results)
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p777_summary": str(args.p777_summary),
            "p786_summary": str(args.p786_summary),
            "p799_script": str(P799_SCRIPT),
            "p835_script": str(P835_SCRIPT),
            "p837_script": str(P837_SCRIPT),
            "p837_summary": str(args.p837_summary),
            "script": str(Path(__file__)),
        },
        "claim_status": claim_status,
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "SUPPORT-FORCING AUDIT: P838 tests whether prefix encodings increase exact intended-support hits, not only recovered-row enrichment.",
            "PREFIX-SALTING ONLY: this still changes deterministic seed material; it is not a proof of algebraic support construction.",
            "CONTROL-BOUND: intended-support hit lift must beat neutral and rotated controls.",
            "POLLARD-RHO BOUNDARY: generated-policy metrics are micro-generator evidence and not a complete faster-than-rho ECDLP algorithm.",
            "NO DEPLOYED-CURVE CLAIM: no production-key relevance or deployed-prime break is implied.",
        ],
        "method": "p838_support_forcing_seed_material_audit",
        "parameters": {
            "budgets": budgets,
            "control_count": int(args.control_count),
            "encodings": encodings,
            "field_weight": int(args.field_weight),
            "generator_namespace": str(args.generator_namespace),
            "max_items_per_target": int(args.max_items_per_target),
            "max_schedules": int(args.max_schedules),
            "seeds_per_prefix": int(args.seeds_per_prefix),
            "train_replicas": int(args.train_replicas),
            "train_seed_namespace": str(args.train_seed_namespace),
        },
        "red_team_handoff": {
            "assumptions": [
                "Exact intended-support hits are the correct first signal for a support-forcing constructor.",
                "Rotated supports preserve rough support-pair shape while breaking exact schedule targets.",
                "Positive P837 schedules are the right first search space for stronger seed material.",
            ],
            "failure_modes": [
                "Prefix encodings can correlate with trained support hits without forcing the intended support.",
                "A small sample can miss rare exact-support hits.",
                "An intended-support hit lift still needs integration into P836/P826 held-out accounting before any stronger claim.",
            ],
            "next_concrete_action": (
                "If an encoding improves intended-support hits, expand it across all P836 schedules and replace prefix salting "
                "with an explicit support-form construction attempt."
            ),
        },
        "schema": SCHEMA,
        "support_forcing": {
            "best_intended_support_policy": best_intended,
            "positive_schedule_specs": [
                {
                    "best_p837_policy": spec["best_p837_policy"],
                    "clauses": [list(clause) for clause in spec["clauses"]],
                    "schedule_name": spec["schedule_name"],
                    "source_name": spec["source_name"],
                }
                for spec in selected_specs
            ],
            "schedule_results": schedule_results,
        },
    }


def summary_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    compact_results = []
    for result in payload["support_forcing"]["schedule_results"]:
        compact_results.append(
            {
                "budget": result["budget"],
                "clauses": result["clauses"],
                "encoding": result["encoding"],
                "policy_results": [compact_policy(item) for item in result["policy_results"]],
                "schedule_name": result["schedule_name"],
                "source_name": result["source_name"],
                "support_meta": result["support_meta"],
            }
        )
    best = payload["support_forcing"]["best_intended_support_policy"]
    return {
        **payload,
        "schema": f"{SCHEMA}.summary",
        "support_forcing": {
            "best_intended_support_policy": None if best is None else compact_policy(best),
            "positive_schedule_specs": payload["support_forcing"]["positive_schedule_specs"],
            "schedule_results": compact_results,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p777-summary", type=Path, default=DEFAULT_P777_SUMMARY)
    parser.add_argument("--p786-summary", type=Path, default=STATE_DIR / "low_term_total2_p786_public_coordinate_bridge_summary.json")
    parser.add_argument("--p837-summary", type=Path, default=DEFAULT_P837_SUMMARY)
    parser.add_argument("--train-seed-namespace", default="supportline20-v1")
    parser.add_argument("--generator-namespace", default="p838-support-forcing-v1")
    parser.add_argument("--train-replicas", type=int, default=20)
    parser.add_argument("--control-count", type=int, default=8)
    parser.add_argument("--field-weight", type=int, default=2)
    parser.add_argument("--min-line-rows", type=int, default=2)
    parser.add_argument("--budgets", default="128")
    parser.add_argument("--encodings", default="plain,repeat,mods,clause,group")
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
                "best_intended_support_policy": summary["support_forcing"]["best_intended_support_policy"],
                "claim_status": summary["claim_status"],
                "positive_schedule_specs": summary["support_forcing"]["positive_schedule_specs"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
