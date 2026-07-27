#!/usr/bin/env python3
"""P834 generator-threshold audit for P833 public rule-list leaves."""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P833_SCRIPT = TASK_DIR / "low_term_total2_p833_public_rule_list_audit.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P826_PROBE = STATE_DIR / "low_term_total2_p826_frozen_shared_pilot_validation_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p834_rule_leaf_generator_threshold_audit_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p834_rule_leaf_generator_threshold_audit.md"
SCHEMA = "ecdlp.low_term_total2_p834_rule_leaf_generator_threshold_audit.v1"


def load_p833() -> Any:
    spec = importlib.util.spec_from_file_location("ecdlp_p833_for_p834", P833_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import P833 helpers from {P833_SCRIPT}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(float(numerator) / float(denominator), 8)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def csv_floats(raw: str) -> list[float]:
    return [float(part.strip()) for part in str(raw).split(",") if part.strip()]


def csv_ints(raw: str) -> list[int]:
    return [int(part.strip()) for part in str(raw).split(",") if part.strip()]


def row_uid(row: dict[str, Any]) -> str:
    return f"{row['context_id']}::{row['row_key']}"


def parse_clause(raw: str) -> tuple[str, ...]:
    return tuple(part.strip() for part in raw.split("&&") if part.strip())


def clause_name(clause: tuple[str, ...]) -> str:
    return " && ".join(clause)


def clause_kind(clause: tuple[str, ...]) -> str:
    support_count = sum(1 for tag in clause if tag.startswith("support_"))
    seed_count = sum(1 for tag in clause if tag.startswith("seed_"))
    if support_count and not seed_count:
        return "support_only"
    if seed_count and not support_count:
        return "seed_only"
    if support_count and seed_count:
        return "mixed_seed_support"
    return "other"


def row_matches_clause(row: dict[str, Any], clause: tuple[str, ...]) -> bool:
    tags = set(row["tags"])
    return all(tag in tags for tag in clause)


def totals_with_rates(p830: Any, rows: list[dict[str, Any]]) -> dict[str, Any]:
    totals = p830.row_totals(rows)
    return {
        **totals,
        "recovered_rho_per_online": ratio(totals["recovered_rho_baseline"], totals["online_group_additions"]),
        "recovered_row_rate": ratio(totals["recovered_row_count"], totals["row_count"]),
    }


def depth_minima(raw: str, default: int) -> dict[int, int]:
    out: dict[int, int] = {}
    for part in str(raw).split(","):
        part = part.strip()
        if not part:
            continue
        depth, value = part.split(":", 1)
        out[int(depth)] = int(value)
    out[-1] = int(default)
    return out


def reconstruct_p833_best(p833: Any, p830: Any, rows: list[dict[str, Any]], fixed_cost: int, field_weight: int, args: argparse.Namespace) -> dict[str, Any]:
    top_ks = csv_ints(args.top_ks)
    p832 = p833.load_p832()
    p831 = p832.load_p831()
    p832_global = p832.evaluate_stable_cross_validated(
        p830,
        rows,
        fixed_cost,
        field_weight,
        top_ks,
        int(args.min_stable_rows_per_namespace),
        int(args.min_stable_total_rows),
        int(args.support_prior_online),
        bool(args.require_recovered_each_namespace),
        None,
    )
    p831_oracle = p831.evaluate_oracle_upper(
        p830,
        rows,
        fixed_cost,
        field_weight,
        top_ks,
        int(args.min_conjunction_rows),
    )
    policy_results = []
    global_depths = p833.csv_depths(args.rule_depths)
    group_depths = p833.csv_depths(args.group_rule_depths)
    min_ns = depth_minima(args.min_rule_rows_per_namespace_by_depth, int(args.min_rule_rows_per_namespace))
    min_total = depth_minima(args.min_rule_total_rows_by_depth, int(args.min_rule_total_rows))
    group_min_ns = depth_minima(args.group_min_rule_rows_per_namespace_by_depth, int(args.group_min_rule_rows_per_namespace))
    group_min_total = depth_minima(args.group_min_rule_total_rows_by_depth, int(args.group_min_rule_total_rows))
    for score_mode in str(args.score_modes).split(","):
        score_mode = score_mode.strip()
        if not score_mode:
            continue
        policy_results.extend(
            p833.evaluate_rule_list_cross_validated(
                p830,
                rows,
                fixed_cost,
                field_weight,
                top_ks,
                global_depths,
                min_ns,
                min_total,
                int(args.support_prior_online),
                bool(args.require_recovered_each_namespace),
                int(args.max_rule_candidates),
                score_mode,
                None,
            )
        )
        policy_results.extend(
            p833.evaluate_rule_list_cross_validated(
                p830,
                rows,
                fixed_cost,
                field_weight,
                top_ks,
                group_depths,
                group_min_ns,
                group_min_total,
                int(args.support_prior_online),
                bool(args.require_recovered_each_namespace),
                int(args.max_group_rule_candidates),
                score_mode,
                "group_key",
            )
        )
    policy_results.sort(
        key=lambda item: (
            item["charge_model"]["post_hit_total_cost_over_recovered_rho"] or 10**9,
            -item["selected_pilot_only"]["recovered_row_count"],
            item["policy"]["kind"],
            item["policy"]["top_k_per_slice"],
        )
    )
    return {
        "best_public_rule_list": policy_results[0] if policy_results else None,
        "p831_oracle_ceiling_best": p831_oracle[0] if p831_oracle else None,
        "p832_public_stabilized_best": p832_global[0] if p832_global else None,
    }


def selected_rows_from_best(p833_best: dict[str, Any], pilot_rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    selected: dict[str, dict[str, Any]] = {}
    attribution: dict[str, dict[str, Any]] = {}
    for diagnostic in p833_best["diagnostics"]:
        namespace = diagnostic["heldout_namespace"]
        clauses = [parse_clause(raw) for raw in diagnostic["selected_rules"]]
        test_rows = [row for row in pilot_rows if row["base_namespace"] == namespace]
        for row in test_rows:
            matching = [clause for clause in clauses if row_matches_clause(row, clause)]
            if not matching:
                continue
            uid = row_uid(row)
            selected[uid] = row
            if uid not in attribution:
                first = matching[0]
                attribution[uid] = {
                    "clause": list(first),
                    "clause_kind": clause_kind(first),
                    "heldout_namespace": namespace,
                    "matching_clause_count": len(matching),
                    "matching_clause_kinds": sorted({clause_kind(clause) for clause in matching}),
                    "rule_name": clause_name(first),
                }
    return list(selected.values()), [{**attribution[row_uid(row)], "row": row} for row in selected.values()]


def eligible_uids(attributions: list[dict[str, Any]], mode: str) -> set[str]:
    out = set()
    for item in attributions:
        uid = row_uid(item["row"])
        kinds = set(item["matching_clause_kinds"])
        first_kind = item["clause_kind"]
        if mode == "support_only_first" and first_kind == "support_only":
            out.add(uid)
        elif mode == "support_any" and "support_only" in kinds:
            out.add(uid)
        elif mode == "support_or_mixed_any" and ({"support_only", "mixed_seed_support"} & kinds):
            out.add(uid)
        elif mode == "all_selected":
            out.add(uid)
    return out


def adjusted_model(
    p830: Any,
    base_rows: list[dict[str, Any]],
    selected_rows: list[dict[str, Any]],
    eligible: set[str],
    speedup: float,
    fixed_cost: int,
    field_weight: int,
) -> dict[str, Any]:
    base = p830.row_totals(base_rows)
    selected = p830.row_totals(selected_rows)
    eligible_rows = [row for row in selected_rows if row_uid(row) in eligible]
    ineligible_rows = [row for row in selected_rows if row_uid(row) not in eligible]
    eligible_totals = p830.row_totals(eligible_rows)
    ineligible_totals = p830.row_totals(ineligible_rows)
    adjusted_eligible_online = int(math.ceil(int(eligible_totals["online_group_additions"]) / float(speedup)))
    total_online = int(base["online_group_additions"]) + int(ineligible_totals["online_group_additions"]) + adjusted_eligible_online
    scoring_cost = int(field_weight) * (int(base["scored_form_count"]) + int(selected["scored_form_count"])) * 4
    recovered_rho = int(base["recovered_rho_baseline"]) + int(selected["recovered_rho_baseline"])
    recovered_rows = int(base["recovered_row_count"]) + int(selected["recovered_row_count"])
    row_count = int(base["row_count"]) + int(selected["row_count"])
    rho_baseline = int(base["rho_baseline"]) + int(selected["rho_baseline"])
    total_cost = int(fixed_cost) + int(total_online) + int(scoring_cost)
    return {
        "adjusted_eligible_online_group_additions": adjusted_eligible_online,
        "eligible_online_group_additions": int(eligible_totals["online_group_additions"]),
        "eligible_recovered_rho_baseline": int(eligible_totals["recovered_rho_baseline"]),
        "eligible_recovered_row_count": int(eligible_totals["recovered_row_count"]),
        "eligible_row_count": int(eligible_totals["row_count"]),
        "fixed_cost": int(fixed_cost),
        "ineligible_online_group_additions": int(ineligible_totals["online_group_additions"]),
        "online_group_additions": int(total_online),
        "post_hit_total_cost": int(total_cost),
        "post_hit_total_cost_over_recovered_rho": ratio(total_cost, recovered_rho),
        "recovered_rho_baseline": int(recovered_rho),
        "recovered_row_count": int(recovered_rows),
        "rho_baseline": int(rho_baseline),
        "row_count": int(row_count),
        "scored_form_count": int(base["scored_form_count"]) + int(selected["scored_form_count"]),
        "scoring_field_weighted_cost": int(scoring_cost),
        "speedup": float(speedup),
    }


def required_speedup_for_threshold(
    p830: Any,
    base_rows: list[dict[str, Any]],
    selected_rows: list[dict[str, Any]],
    eligible: set[str],
    fixed_cost: int,
    field_weight: int,
    target_ratio: float,
) -> dict[str, Any]:
    base = p830.row_totals(base_rows)
    selected = p830.row_totals(selected_rows)
    eligible_rows = [row for row in selected_rows if row_uid(row) in eligible]
    ineligible_rows = [row for row in selected_rows if row_uid(row) not in eligible]
    eligible_totals = p830.row_totals(eligible_rows)
    ineligible_totals = p830.row_totals(ineligible_rows)
    recovered_rho = int(base["recovered_rho_baseline"]) + int(selected["recovered_rho_baseline"])
    scoring_cost = int(field_weight) * (int(base["scored_form_count"]) + int(selected["scored_form_count"])) * 4
    target_total_cost = float(target_ratio) * float(recovered_rho)
    fixed_and_ineligible = (
        int(fixed_cost)
        + int(base["online_group_additions"])
        + int(ineligible_totals["online_group_additions"])
        + int(scoring_cost)
    )
    allowed_eligible_online = target_total_cost - float(fixed_and_ineligible)
    eligible_online = int(eligible_totals["online_group_additions"])
    if eligible_online <= 0:
        required = None
        feasible = False
    elif allowed_eligible_online <= 0:
        required = None
        feasible = False
    else:
        required = max(1.0, float(eligible_online) / float(allowed_eligible_online))
        feasible = True
    return {
        "eligible_online_group_additions": eligible_online,
        "feasible_by_speeding_eligible_only": feasible,
        "fixed_and_ineligible_cost": int(fixed_and_ineligible),
        "recovered_rho_baseline": int(recovered_rho),
        "required_speedup": None if required is None else round(required, 8),
        "target_ratio": float(target_ratio),
        "target_total_cost": round(target_total_cost, 8),
    }


def per_rule_attribution(p830: Any, attributions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows_by_rule: dict[str, list[dict[str, Any]]] = defaultdict(list)
    meta_by_rule: dict[str, dict[str, Any]] = {}
    for item in attributions:
        rows_by_rule[item["rule_name"]].append(item["row"])
        meta_by_rule[item["rule_name"]] = {
            "clause": item["clause"],
            "clause_kind": item["clause_kind"],
            "rule_name": item["rule_name"],
        }
    out = []
    for name, rows in rows_by_rule.items():
        out.append({**meta_by_rule[name], **totals_with_rates(p830, rows)})
    out.sort(
        key=lambda item: (
            int(item["recovered_row_count"]),
            int(item["recovered_rho_baseline"]),
            -int(item["online_group_additions"]),
            item["rule_name"],
        ),
        reverse=True,
    )
    return out


def determine_claim(full_model: dict[str, Any], p833_model: dict[str, Any], threshold_models: dict[str, Any]) -> str:
    p826_ratio = float(full_model["post_hit_total_cost_over_recovered_rho"] or 10**9)
    p833_ratio = float(p833_model["post_hit_total_cost_over_recovered_rho"] or 10**9)
    all_selected = threshold_models["all_selected"]["required_speedups"]["beat_p826"]["required_speedup"]
    support_any = threshold_models["support_any"]["required_speedups"]["beat_p826"]["required_speedup"]
    if p833_ratio < p826_ratio:
        return "P834_P833_ALREADY_BEATS_P826"
    if all_selected is not None and float(all_selected) <= 2.0:
        return "P834_LOW_DIRECT_GENERATION_SPEEDUP_WOULD_BEAT_P826"
    if support_any is not None and float(support_any) <= 2.0:
        return "P834_SUPPORT_LEAF_DIRECT_GENERATION_WOULD_BEAT_P826_AT_LOW_SPEEDUP"
    if all_selected is not None:
        return "P834_GENERATOR_THRESHOLD_MAP_ONLY"
    return "NEGATIVE_RESULT_P834_SELECTED_LEAF_SPEEDUP_CANNOT_BEAT_P826"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p833 = load_p833()
    p832 = p833.load_p832()
    p831 = p832.load_p831()
    p830 = p831.load_p830()
    rows, build_meta = p830.build_rows(args)
    fixed = p830.find_p826_fixed_cost(args.p826_probe, int(args.field_weight))
    fixed_cost = int(fixed["fixed_cost"])
    field_weight = int(args.field_weight)
    p833_reconstructed = reconstruct_p833_best(p833, p830, rows, fixed_cost, field_weight, args)
    p833_best = p833_reconstructed["best_public_rule_list"]
    if p833_best is None:
        raise RuntimeError("P834 could not reconstruct P833 best public rule-list result")

    pilot_rows = [row for row in rows if row["category"] == "pilot_only"]
    base_rows = [row for row in rows if row["category"] != "pilot_only"]
    selected_rows, attributions = selected_rows_from_best(p833_best, pilot_rows)
    selected_totals = p830.row_totals(selected_rows)
    if int(selected_totals["row_count"]) != int(p833_best["selected_pilot_only"]["row_count"]):
        raise RuntimeError(
            f"selected-row reconstruction mismatch: {selected_totals['row_count']} != {p833_best['selected_pilot_only']['row_count']}"
        )

    full_model = p830.charged_model(pilot_rows, base_rows, fixed_cost, field_weight)
    p833_measured = p830.charged_model(selected_rows, base_rows, fixed_cost, field_weight)
    speedups = csv_floats(args.speedups)
    eligible_modes = ["support_only_first", "support_any", "support_or_mixed_any", "all_selected"]
    threshold_models: dict[str, Any] = {}
    for mode in eligible_modes:
        eligible = eligible_uids(attributions, mode)
        models = [
            adjusted_model(p830, base_rows, selected_rows, eligible, speedup, fixed_cost, field_weight)
            for speedup in speedups
        ]
        threshold_models[mode] = {
            "eligible_totals": totals_with_rates(p830, [row for row in selected_rows if row_uid(row) in eligible]),
            "models_by_speedup": models,
            "required_speedups": {
                "beat_p826": required_speedup_for_threshold(
                    p830,
                    base_rows,
                    selected_rows,
                    eligible,
                    fixed_cost,
                    field_weight,
                    float(full_model["post_hit_total_cost_over_recovered_rho"]),
                ),
                "beat_rho": required_speedup_for_threshold(
                    p830,
                    base_rows,
                    selected_rows,
                    eligible,
                    fixed_cost,
                    field_weight,
                    1.0,
                ),
            },
        }

    claim_status = determine_claim(full_model, p833_measured, threshold_models)
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p826_probe": str(args.p826_probe),
            "p830_script": str(p831.P830_SCRIPT),
            "p831_script": str(p832.P831_SCRIPT),
            "p832_script": str(p833.P832_SCRIPT),
            "p833_script": str(P833_SCRIPT),
            "script": str(Path(__file__)),
        },
        "build_meta": build_meta,
        "claim_status": claim_status,
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "generator_threshold": {
            "attribution_by_first_rule": per_rule_attribution(p830, attributions),
            "p831_oracle_ceiling_best": p833_reconstructed["p831_oracle_ceiling_best"],
            "p832_public_stabilized_best": p833_reconstructed["p832_public_stabilized_best"],
            "p833_measured_best": p833_measured,
            "p833_public_rule_list_best": p833_best,
            "threshold_models": threshold_models,
        },
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "THRESHOLD-AUDIT: P834 does not implement a new row generator; it computes required cost reductions for P833 rule leaves.",
            "MODEL-BOUND: cost uses P826 fixed cost plus measured base rows, measured selected rows, and counterfactual eligible-row online speedups.",
            "PUBLIC RULES: all selected leaves are public seed/support tag predicates learned without held-out labels.",
            "NO DEPLOYED-CURVE CLAIM: this is not a faster-than-rho deployed ECDLP algorithm.",
        ],
        "method": "p834_rule_leaf_generator_threshold_audit",
        "parameters": {
            "fixed_cost": fixed,
            "speedups": speedups,
        },
        "red_team_handoff": {
            "assumptions": [
                "Only row online additions for eligible P833-selected pilot rows are sped up in counterfactual models.",
                "Base continuation/duplicate rows and scoring-field work remain charged.",
                "Recovered-rho denominator is held fixed to P833 measured recovery.",
            ],
            "failure_modes": [
                "A threshold speedup is not a measured generator.",
                "Support-modulus predicates may still require expensive row construction not represented by simple online scaling.",
                "The broad leaves may hide namespace artifacts rather than structural support schedules.",
            ],
            "next_concrete_action_if_promising": (
                "Implement P835 as an actual support-schedule generator for the P833 support-only leaves and measure row "
                "construction cost directly instead of applying a speedup counterfactual."
            ),
        },
        "row_population": {
            "category_totals": p830.totals_by_category(rows),
            "full_p826_reconstructed_charge_model": full_model,
            "selected_pilot_reconstruction": totals_with_rates(p830, selected_rows),
        },
        "schema": SCHEMA,
    }


def summary_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    threshold = payload["generator_threshold"]
    compact_threshold_models = {}
    for mode, model in threshold["threshold_models"].items():
        compact_threshold_models[mode] = {
            "eligible_totals": model["eligible_totals"],
            "required_speedups": model["required_speedups"],
            "speedup_crossings": [
                item
                for item in model["models_by_speedup"]
                if item["speedup"] in (1.0, 1.5, 2.0, 3.0, 4.0, 8.0, 16.0)
            ],
        }
    return {
        **payload,
        "generator_threshold": {
            "attribution_by_first_rule": threshold["attribution_by_first_rule"],
            "p831_oracle_ceiling_best": threshold["p831_oracle_ceiling_best"],
            "p832_public_stabilized_best": threshold["p832_public_stabilized_best"],
            "p833_measured_best": threshold["p833_measured_best"],
            "p833_public_rule_list_best": threshold["p833_public_rule_list_best"],
            "threshold_models": compact_threshold_models,
        },
        "schema": f"{SCHEMA}.summary",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p826-probe", type=Path, default=DEFAULT_P826_PROBE)
    parser.add_argument("--p777-summary", type=Path, default=STATE_DIR / "low_term_total2_p777_merged_trim12_factor_first_cost_audit_summary.json")
    parser.add_argument("--p786-summary", type=Path, default=STATE_DIR / "low_term_total2_p786_public_coordinate_bridge_summary.json")
    parser.add_argument("--train-seed-namespace", default="supportline20-v1")
    parser.add_argument("--train-constructor-namespaces", default="")
    parser.add_argument("--test-constructor-namespaces", default="posthit-p826-fresh-v32,posthit-p826-fresh-v33,posthit-p826-fresh-v34")
    parser.add_argument("--loo-constructor-namespaces", default="")
    parser.add_argument("--skip-loo", action="store_true", default=True)
    parser.add_argument("--calibration-budget", type=int, default=256)
    parser.add_argument("--prefix-seed-counts", default="8")
    parser.add_argument("--prefix-trial-budget", type=int, default=256)
    parser.add_argument("--average-continuation-budgets", default="64")
    parser.add_argument("--pilot-budgets", default="16")
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
    parser.add_argument("--top-ks", default="1,2,4,8,16,32")
    parser.add_argument("--min-conjunction-rows", type=int, default=8)
    parser.add_argument("--min-stable-rows-per-namespace", type=int, default=4)
    parser.add_argument("--min-stable-total-rows", type=int, default=8)
    parser.add_argument("--min-rule-rows-per-namespace", type=int, default=4)
    parser.add_argument("--min-rule-rows-per-namespace-by-depth", default="1:12,2:4,3:2")
    parser.add_argument("--min-rule-total-rows", type=int, default=8)
    parser.add_argument("--min-rule-total-rows-by-depth", default="1:24,2:8,3:4")
    parser.add_argument("--group-min-rule-rows-per-namespace", type=int, default=1)
    parser.add_argument("--group-min-rule-rows-per-namespace-by-depth", default="1:4,2:1,3:1")
    parser.add_argument("--group-min-rule-total-rows", type=int, default=2)
    parser.add_argument("--group-min-rule-total-rows-by-depth", default="1:8,2:2,3:2")
    parser.add_argument("--rule-depths", default="1,2,3")
    parser.add_argument("--group-rule-depths", default="1,2,3")
    parser.add_argument("--score-modes", default="density_first,recall_first")
    parser.add_argument("--support-prior-online", type=int, default=64)
    parser.add_argument("--require-recovered-each-namespace", action="store_true")
    parser.add_argument("--max-rule-candidates", type=int, default=4000)
    parser.add_argument("--max-group-rule-candidates", type=int, default=2500)
    parser.add_argument("--speedups", default="1,1.25,1.5,2,3,4,8,16,32")
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
                "claim_status": summary["claim_status"],
                "full_p826_reconstructed_charge_model": summary["row_population"]["full_p826_reconstructed_charge_model"],
                "p833_measured_best": summary["generator_threshold"]["p833_measured_best"],
                "threshold_models": {
                    key: value["required_speedups"]
                    for key, value in summary["generator_threshold"]["threshold_models"].items()
                },
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
