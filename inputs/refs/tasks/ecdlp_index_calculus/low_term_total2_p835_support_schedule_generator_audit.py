#!/usr/bin/env python3
"""P835 exact support-schedule audit for P833 public support leaves."""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P834_SCRIPT = TASK_DIR / "low_term_total2_p834_rule_leaf_generator_threshold_audit.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P826_PROBE = STATE_DIR / "low_term_total2_p826_frozen_shared_pilot_validation_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p835_support_schedule_generator_audit_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p835_support_schedule_generator_audit.md"
SCHEMA = "ecdlp.low_term_total2_p835_support_schedule_generator_audit.v1"


def load_p834() -> Any:
    spec = importlib.util.spec_from_file_location("ecdlp_p834_for_p835", P834_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import P834 helpers from {P834_SCRIPT}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(float(numerator) / float(denominator), 8)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def support_tags_for_pair(left: int, right: int) -> set[str]:
    left = int(left)
    right = int(right)
    support_sum = left + right
    support_span = abs(right - left)
    tags = set()
    for modulus in (2, 4, 8, 16):
        tags.add(f"support_sum_mod{modulus}={support_sum % modulus}")
    for modulus in (2, 4, 8):
        tags.add(f"support_left_mod{modulus}={left % modulus}")
        tags.add(f"support_right_mod{modulus}={right % modulus}")
        tags.add(f"support_span_mod{modulus}={support_span % modulus}")
    tags.add(f"support_parity={left % 2},{right % 2}")
    tags.add(f"support_span_bucket8={support_span // 8}")
    tags.add(f"support_span_bucket16={support_span // 16}")
    tags.add(f"support_low_bucket16={min(left, right) // 16}")
    tags.add(f"support_high_bucket16={max(left, right) // 16}")
    return tags


def support_pair_set(factor_base_size: int, clause: tuple[str, ...]) -> set[tuple[int, int]]:
    pairs = set()
    for left in range(int(factor_base_size)):
        for right in range(left + 1, int(factor_base_size)):
            tags = support_tags_for_pair(left, right)
            if all(tag in tags for tag in clause):
                pairs.add((left, right))
    return pairs


def support_schedule_stats(factor_base_size: int, clauses: list[tuple[str, ...]]) -> dict[str, Any]:
    all_pair_count = int(factor_base_size) * (int(factor_base_size) - 1) // 2
    union_pairs: set[tuple[int, int]] = set()
    clause_stats = []
    for clause in clauses:
        pairs = support_pair_set(int(factor_base_size), clause)
        union_pairs.update(pairs)
        clause_stats.append(
            {
                "clause": list(clause),
                "matching_pair_count": len(pairs),
                "rule_name": " && ".join(clause),
                "schedule_fraction": ratio(len(pairs), all_pair_count),
                "schedule_speedup": ratio(all_pair_count, len(pairs)),
            }
        )
    return {
        "all_pair_count": all_pair_count,
        "factor_base_size": int(factor_base_size),
        "support_clause_count": len(clauses),
        "support_clauses": clause_stats,
        "union_pair_count": len(union_pairs),
        "union_schedule_fraction": ratio(len(union_pairs), all_pair_count),
        "union_schedule_speedup": ratio(all_pair_count, len(union_pairs)),
    }


def factor_base_size_for_group(group_key: str, rows: list[dict[str, Any]]) -> int:
    match = re.search(r"fb(\d+)", str(group_key))
    if match:
        return int(match.group(1))
    group_rows = [row for row in rows if row.get("group_key") == group_key]
    max_support = max(
        [int(row.get("support_left") or 0) for row in group_rows]
        + [int(row.get("support_right") or 0) for row in group_rows]
        + [0]
    )
    if max_support <= 0:
        raise ValueError(f"cannot infer factor-base size for group_key={group_key!r}")
    return max_support + 1


def schedule_key(namespace: str, stratify_by: str, slice_label: str, group_key: str) -> str:
    return f"{namespace}::{stratify_by}::{slice_label}::{group_key}"


def diagnostic_rows(pilot_rows: list[dict[str, Any]], diagnostic: dict[str, Any]) -> list[dict[str, Any]]:
    namespace = str(diagnostic["heldout_namespace"])
    stratify_by = str(diagnostic.get("stratify_by") or "none")
    slice_label = str(diagnostic.get("slice_label") or "all")
    rows = [row for row in pilot_rows if row["base_namespace"] == namespace]
    if stratify_by != "none" and slice_label != "all":
        rows = [row for row in rows if str(row.get(stratify_by)) == slice_label]
    return rows


def support_only_clauses(p834: Any, diagnostic: dict[str, Any]) -> list[tuple[str, ...]]:
    out = []
    for raw in diagnostic["selected_rules"]:
        clause = p834.parse_clause(raw)
        if p834.clause_kind(clause) == "support_only":
            out.append(clause)
    return out


def selected_rows_with_attribution(
    p834: Any,
    p833_best: dict[str, Any],
    pilot_rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, dict[str, Any]]]:
    selected: dict[str, dict[str, Any]] = {}
    attribution: dict[str, dict[str, Any]] = {}
    schedules: dict[str, dict[str, Any]] = {}
    for diagnostic_index, diagnostic in enumerate(p833_best["diagnostics"]):
        namespace = str(diagnostic["heldout_namespace"])
        stratify_by = str(diagnostic.get("stratify_by") or "none")
        slice_label = str(diagnostic.get("slice_label") or "all")
        clauses = [p834.parse_clause(raw) for raw in diagnostic["selected_rules"]]
        support_clauses = [clause for clause in clauses if p834.clause_kind(clause) == "support_only"]
        test_rows = diagnostic_rows(pilot_rows, diagnostic)
        for group_key in sorted({str(row["group_key"]) for row in test_rows}):
            fb_size = factor_base_size_for_group(group_key, test_rows)
            key = schedule_key(namespace, stratify_by, slice_label, group_key)
            schedules[key] = {
                **support_schedule_stats(fb_size, support_clauses),
                "diagnostic_index": int(diagnostic_index),
                "heldout_namespace": namespace,
                "slice_label": slice_label,
                "stratify_by": stratify_by,
                "group_key": group_key,
            }
        for row in test_rows:
            matching = [clause for clause in clauses if p834.row_matches_clause(row, clause)]
            if not matching:
                continue
            uid = p834.row_uid(row)
            selected[uid] = row
            if uid in attribution:
                continue
            first = matching[0]
            row_support_clauses = [clause for clause in matching if p834.clause_kind(clause) == "support_only"]
            key = schedule_key(namespace, stratify_by, slice_label, str(row["group_key"]))
            attribution[uid] = {
                "clause": list(first),
                "clause_kind": p834.clause_kind(first),
                "heldout_namespace": namespace,
                "matching_clause_count": len(matching),
                "matching_clause_kinds": sorted({p834.clause_kind(clause) for clause in matching}),
                "rule_name": p834.clause_name(first),
                "slice_label": slice_label,
                "stratify_by": stratify_by,
                "support_only_matching_clauses": [list(clause) for clause in row_support_clauses],
                "support_schedule_key": key,
                "row": row,
            }
    return list(selected.values()), list(attribution.values()), schedules


def exact_schedule_adjusted_model(
    p830: Any,
    base_rows: list[dict[str, Any]],
    selected_rows: list[dict[str, Any]],
    attributions: list[dict[str, Any]],
    schedules: dict[str, dict[str, Any]],
    fixed_cost: int,
    field_weight: int,
) -> dict[str, Any]:
    attrs_by_uid = {f"{item['row']['context_id']}::{item['row']['row_key']}": item for item in attributions}
    eligible_by_schedule: dict[str, list[dict[str, Any]]] = defaultdict(list)
    ineligible_rows = []
    non_pair_rows = []
    for row in selected_rows:
        uid = f"{row['context_id']}::{row['row_key']}"
        item = attrs_by_uid.get(uid)
        if item is None:
            ineligible_rows.append(row)
            continue
        schedule = schedules.get(str(item["support_schedule_key"]))
        speedup = None if schedule is None else schedule.get("union_schedule_speedup")
        has_support_clause = bool(item.get("support_only_matching_clauses"))
        is_pair = int(row["support_left"]) != int(row["support_right"])
        if has_support_clause and is_pair and speedup is not None and float(speedup) > 0.0:
            eligible_by_schedule[str(item["support_schedule_key"])].append(row)
        else:
            ineligible_rows.append(row)
            if has_support_clause and not is_pair:
                non_pair_rows.append(row)

    base = p830.row_totals(base_rows)
    selected = p830.row_totals(selected_rows)
    ineligible = p830.row_totals(ineligible_rows)
    adjusted_components = []
    adjusted_eligible_online = 0
    eligible_online = 0
    eligible_recovered_rho = 0
    eligible_recovered_rows = 0
    eligible_row_count = 0
    for key, rows in sorted(eligible_by_schedule.items()):
        totals = p830.row_totals(rows)
        speedup = float(schedules[key]["union_schedule_speedup"])
        adjusted_online = int(math.ceil(int(totals["online_group_additions"]) / speedup))
        adjusted_eligible_online += adjusted_online
        eligible_online += int(totals["online_group_additions"])
        eligible_recovered_rho += int(totals["recovered_rho_baseline"])
        eligible_recovered_rows += int(totals["recovered_row_count"])
        eligible_row_count += int(totals["row_count"])
        adjusted_components.append(
            {
                "adjusted_online_group_additions": adjusted_online,
                "realized_schedule_speedup": ratio(int(totals["online_group_additions"]), adjusted_online),
                "schedule": schedules[key],
                **totals,
            }
        )

    total_online = int(base["online_group_additions"]) + int(ineligible["online_group_additions"]) + int(adjusted_eligible_online)
    scoring_cost = int(field_weight) * (int(base["scored_form_count"]) + int(selected["scored_form_count"])) * 4
    recovered_rho = int(base["recovered_rho_baseline"]) + int(selected["recovered_rho_baseline"])
    recovered_rows = int(base["recovered_row_count"]) + int(selected["recovered_row_count"])
    row_count = int(base["row_count"]) + int(selected["row_count"])
    rho_baseline = int(base["rho_baseline"]) + int(selected["rho_baseline"])
    total_cost = int(fixed_cost) + int(total_online) + int(scoring_cost)
    return {
        "adjusted_components": adjusted_components,
        "adjusted_eligible_online_group_additions": int(adjusted_eligible_online),
        "eligible_online_group_additions": int(eligible_online),
        "eligible_realized_schedule_speedup": ratio(eligible_online, adjusted_eligible_online),
        "eligible_recovered_rho_baseline": int(eligible_recovered_rho),
        "eligible_recovered_row_count": int(eligible_recovered_rows),
        "eligible_row_count": int(eligible_row_count),
        "fixed_cost": int(fixed_cost),
        "ineligible_online_group_additions": int(ineligible["online_group_additions"]),
        "non_pair_support_tagged_row_count": int(len(non_pair_rows)),
        "online_group_additions": int(total_online),
        "post_hit_total_cost": int(total_cost),
        "post_hit_total_cost_over_recovered_rho": ratio(total_cost, recovered_rho),
        "recovered_rho_baseline": int(recovered_rho),
        "recovered_row_count": int(recovered_rows),
        "rho_baseline": int(rho_baseline),
        "row_count": int(row_count),
        "scored_form_count": int(base["scored_form_count"]) + int(selected["scored_form_count"]),
        "scoring_field_weighted_cost": int(scoring_cost),
    }


def per_rule_schedule_table(
    p834: Any,
    attributions: list[dict[str, Any]],
    schedules: dict[str, dict[str, Any]],
    p830: Any,
) -> list[dict[str, Any]]:
    rows_by_rule: dict[str, list[dict[str, Any]]] = defaultdict(list)
    keys_by_rule: dict[str, set[str]] = defaultdict(set)
    clauses_by_rule: dict[str, list[str]] = {}
    for item in attributions:
        if "support_only" not in set(item["matching_clause_kinds"]):
            continue
        row = item["row"]
        for clause_raw in item["support_only_matching_clauses"]:
            clause = tuple(clause_raw)
            name = p834.clause_name(clause)
            if p834.row_matches_clause(row, clause):
                rows_by_rule[name].append(row)
                keys_by_rule[name].add(str(item["support_schedule_key"]))
                clauses_by_rule[name] = list(clause)
    out = []
    for name, rows in rows_by_rule.items():
        schedule_speedups = [
            float(schedules[key]["union_schedule_speedup"])
            for key in sorted(keys_by_rule[name])
            if schedules[key].get("union_schedule_speedup") is not None
        ]
        totals = p830.row_totals(rows)
        out.append(
            {
                "clause": clauses_by_rule[name],
                "max_slice_union_schedule_speedup": round(max(schedule_speedups), 8) if schedule_speedups else None,
                "min_slice_union_schedule_speedup": round(min(schedule_speedups), 8) if schedule_speedups else None,
                "rule_name": name,
                "slice_group_count": len(keys_by_rule[name]),
                **totals,
                "recovered_rho_per_online": ratio(totals["recovered_rho_baseline"], totals["online_group_additions"]),
            }
        )
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


def determine_claim(full_model: dict[str, Any], p833_model: dict[str, Any], schedule_model: dict[str, Any]) -> str:
    p826_ratio = float(full_model["post_hit_total_cost_over_recovered_rho"] or 10**9)
    p833_ratio = float(p833_model["post_hit_total_cost_over_recovered_rho"] or 10**9)
    schedule_ratio = float(schedule_model["post_hit_total_cost_over_recovered_rho"] or 10**9)
    if schedule_ratio < 1.0:
        return "P835_SUPPORT_SCHEDULE_ENUMERATION_BELOW_RHO_MODEL_SIGNAL"
    if schedule_ratio < p826_ratio:
        return "P835_SUPPORT_SCHEDULE_ENUMERATION_BEATS_P826_MODEL"
    if schedule_ratio < p833_ratio:
        return "P835_SUPPORT_SCHEDULE_ENUMERATION_IMPROVES_P833_BUT_NOT_P826"
    return "NEGATIVE_RESULT_P835_SUPPORT_SCHEDULE_UNION_TOO_BROAD"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p834 = load_p834()
    p833 = p834.load_p833()
    p832 = p833.load_p832()
    p831 = p832.load_p831()
    p830 = p831.load_p830()
    rows, build_meta = p830.build_rows(args)
    fixed = p830.find_p826_fixed_cost(args.p826_probe, int(args.field_weight))
    fixed_cost = int(fixed["fixed_cost"])
    field_weight = int(args.field_weight)
    p833_reconstructed = p834.reconstruct_p833_best(p833, p830, rows, fixed_cost, field_weight, args)
    p833_best = p833_reconstructed["best_public_rule_list"]
    if p833_best is None:
        raise RuntimeError("P835 could not reconstruct P833 best public rule-list result")

    pilot_rows = [row for row in rows if row["category"] == "pilot_only"]
    base_rows = [row for row in rows if row["category"] != "pilot_only"]
    selected_rows, attributions, schedules = selected_rows_with_attribution(p834, p833_best, pilot_rows)
    selected_totals = p830.row_totals(selected_rows)
    expected_rows = int(p833_best["selected_pilot_only"]["row_count"])
    if int(selected_totals["row_count"]) != expected_rows:
        raise RuntimeError(f"selected-row reconstruction mismatch: {selected_totals['row_count']} != {expected_rows}")

    full_model = p830.charged_model(pilot_rows, base_rows, fixed_cost, field_weight)
    p833_measured = p830.charged_model(selected_rows, base_rows, fixed_cost, field_weight)
    support_any = p834.eligible_uids(attributions, "support_any")
    p834_support_any_requirement = p834.required_speedup_for_threshold(
        p830,
        base_rows,
        selected_rows,
        support_any,
        fixed_cost,
        field_weight,
        float(full_model["post_hit_total_cost_over_recovered_rho"]),
    )
    schedule_model = exact_schedule_adjusted_model(
        p830,
        base_rows,
        selected_rows,
        attributions,
        schedules,
        fixed_cost,
        field_weight,
    )
    required = p834_support_any_requirement["required_speedup"]
    realized = schedule_model["eligible_realized_schedule_speedup"]
    passes_threshold = required is not None and realized is not None and float(realized) >= float(required)
    claim_status = determine_claim(full_model, p833_measured, schedule_model)
    schedule_summaries = sorted(
        schedules.values(),
        key=lambda item: (
            item["heldout_namespace"],
            item["slice_label"],
            item["group_key"],
        ),
    )
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p826_probe": str(args.p826_probe),
            "p830_script": str(p831.P830_SCRIPT),
            "p831_script": str(p832.P831_SCRIPT),
            "p832_script": str(p833.P832_SCRIPT),
            "p833_script": str(p834.P833_SCRIPT),
            "p834_script": str(P834_SCRIPT),
            "script": str(Path(__file__)),
        },
        "build_meta": build_meta,
        "claim_status": claim_status,
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "MODEL-BOUND: support leaves are converted into exact support-pair schedule fractions, then row online additions are scaled by those public schedule fractions.",
            "NOT A DIRECT CONSTRUCTOR: P835 does not yet alter the row-construction walk; it tests whether the selected public support leaves are narrow enough to justify a direct generator.",
            "PUBLIC RULES: schedules are derived only from P833 held-out public support tag predicates.",
            "POLLARD-RHO BOUNDARY: below-P826 or below-rho ratios here are generator-model signals until direct construction, sparse linear algebra, and target descent are measured.",
            "NO DEPLOYED-CURVE CLAIM: this is not a faster-than-rho deployed ECDLP algorithm.",
        ],
        "method": "p835_support_schedule_generator_audit",
        "parameters": {
            "fixed_cost": fixed,
            "p834_support_any_required_speedup_to_beat_p826": required,
            "passes_p834_support_any_threshold": bool(passes_threshold),
        },
        "red_team_handoff": {
            "assumptions": [
                "A direct row generator for a public support schedule would reduce eligible-row online additions in proportion to the exact support-pair schedule fraction.",
                "Recovered-rho denominator and scoring-field work remain the same as P833 measured rows.",
                "Support schedules are enumerated over unordered factor-base index pairs using P830 tag semantics.",
            ],
            "failure_modes": [
                "Enumeration speedup may not translate to row-construction speedup if the walk cost is not dominated by support-pair search.",
                "Broad union leaves can overlap enough that individual 2X or 4X rules collapse to a weaker union schedule.",
                "Rows whose first support is not a valid pair cannot be generated by a support-pair schedule even if their public tags match.",
            ],
            "next_concrete_action_if_promising": (
                "Wire the support schedule into the P799/P800 row-construction path and charge generated_online_group_additions directly."
            ),
        },
        "row_population": {
            "category_totals": p830.totals_by_category(rows),
            "full_p826_reconstructed_charge_model": full_model,
            "p833_measured_best": p833_measured,
            "selected_pilot_reconstruction": p834.totals_with_rates(p830, selected_rows),
        },
        "schema": SCHEMA,
        "support_schedule_generator": {
            "p831_oracle_ceiling_best": p833_reconstructed["p831_oracle_ceiling_best"],
            "p832_public_stabilized_best": p833_reconstructed["p832_public_stabilized_best"],
            "p833_public_rule_list_best": p833_best,
            "p834_support_any_requirement": p834_support_any_requirement,
            "per_rule_schedule_table": per_rule_schedule_table(p834, attributions, schedules, p830),
            "schedule_adjusted_model": schedule_model,
            "schedule_summaries": schedule_summaries,
        },
    }


def summary_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    schedule = payload["support_schedule_generator"]
    adjusted = schedule["schedule_adjusted_model"]
    return {
        **payload,
        "schema": f"{SCHEMA}.summary",
        "support_schedule_generator": {
            "p831_oracle_ceiling_best": schedule["p831_oracle_ceiling_best"],
            "p832_public_stabilized_best": schedule["p832_public_stabilized_best"],
            "p833_public_rule_list_best": schedule["p833_public_rule_list_best"],
            "p834_support_any_requirement": schedule["p834_support_any_requirement"],
            "per_rule_schedule_table": schedule["per_rule_schedule_table"],
            "schedule_adjusted_model": {
                key: value
                for key, value in adjusted.items()
                if key != "adjusted_components"
            },
            "schedule_adjusted_components": adjusted["adjusted_components"],
            "schedule_summaries": schedule["schedule_summaries"],
        },
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
    schedule = summary["support_schedule_generator"]
    print(f"wrote {args.out}")
    print(f"wrote {summary_out}")
    print(
        json.dumps(
            {
                "claim_status": summary["claim_status"],
                "full_p826_reconstructed_charge_model": summary["row_population"]["full_p826_reconstructed_charge_model"],
                "p833_measured_best": summary["row_population"]["p833_measured_best"],
                "p834_support_any_requirement": schedule["p834_support_any_requirement"],
                "schedule_adjusted_model": schedule["schedule_adjusted_model"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
