#!/usr/bin/env python3
"""P903 relaxed public-family grid validation after P901/P902."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p901_frozen_direct_generator_validation as p901


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p903_relaxed_family_grid_validation.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p903_relaxed_family_grid_validation_probe.json"
TRAIN_SOURCES = p901.DEFAULT_SOURCES
VALIDATION_SOURCES = [
    STATE_DIR / "frontier_public_leaf_policy_low_term_total2_fixed_row_1024_1031_expanded_probe.json",
    STATE_DIR / "frontier_public_leaf_policy_low_term_total2_fixed_row_1032_1039_expanded_probe.json",
    STATE_DIR / "frontier_public_leaf_policy_low_term_total2_fixed_row_1040_1047_expanded_probe.json",
    STATE_DIR / "frontier_public_leaf_policy_low_term_total2_fixed_row_1048_1055_expanded_probe.json",
    STATE_DIR / "frontier_public_leaf_policy_low_term_total2_fixed_row_1056_1063_expanded_probe.json",
    STATE_DIR / "frontier_public_leaf_policy_low_term_total2_fixed_row_1064_1071_expanded_probe.json",
    STATE_DIR / "frontier_public_leaf_policy_low_term_total2_fixed_row_1072_1079_expanded_probe.json",
    STATE_DIR / "frontier_public_leaf_policy_low_term_total2_fixed_row_1080_1087_expanded_probe.json",
    STATE_DIR / "frontier_public_leaf_policy_low_term_total2_fixed_row_1088_1095_expanded_probe.json",
    STATE_DIR / "frontier_public_leaf_policy_low_term_total2_fixed_row_1096_1103_expanded_probe.json",
]
SCHEMA = "ecdlp.low_term_total2_p903_relaxed_family_grid_validation.v1"
TARGET = p901.TARGET
POLICY = p901.POLICY
STRICT_TARGET_OPS = p901.STRICT_TARGET_OPS
MARGIN_TARGET_OPS = p901.MARGIN_TARGET_OPS
RHO_ESTIMATE = STRICT_TARGET_OPS + 1

LEAF_SETS = [
    ("leaf8", ["8/8"]),
    ("leaf19", ["19/19"]),
    ("leaf79", ["79/79"]),
    ("leaf90", ["90/90"]),
    ("leaf8_or_19", ["8/8", "19/19"]),
    ("leaf79_or_90", ["79/79", "90/90"]),
    ("any_leaf", ["8/8", "19/19", "79/79", "90/90"]),
]
TOP_K_SETS = [
    ("any_topk", None),
    ("top4", [4]),
    ("top7", [7]),
    ("top12", [12]),
    ("top16", [16]),
    ("top4_or_7", [4, 7]),
    ("top12_or_16", [12, 16]),
    ("any_declared_topk", [4, 7, 12, 16]),
]
GROUP_SETS = [
    ("any_group", None),
    ("low_term", ["low_term"]),
    ("low_leaf", ["low_leaf"]),
    ("hybrid", ["hybrid"]),
    ("low_leaf_or_hybrid", ["low_leaf", "hybrid"]),
]
SOURCE_OPS_THRESHOLDS = [0.0, 0.63, 0.66, 0.69, 0.70, 0.73]
SALT_GAP_THRESHOLDS = [0, 4, 6, 8]
DIRECT_ORDERS = ("artifact", "source_ops_desc_artifact", "salt_gap_desc_artifact")


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def int_value(value: Any, default: int = 0) -> int:
    return p901.int_value(value, default)


def float_value(value: Any, default: float = 0.0) -> float:
    return p901.float_value(value, default)


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    return p901.ratio(numerator, denominator)


def leaf_signature(case: dict[str, Any]) -> str:
    return p901.leaf_signature(case)


def row_salts(case: dict[str, Any]) -> list[int]:
    return [
        p901.p900.row_salt(str(row.get("row_key")))
        for row in case.get("row_leaf_keys") or []
    ]


def salt_gap(case: dict[str, Any]) -> int | None:
    salts = row_salts(case)
    if len(salts) != 2:
        return None
    return abs(int(salts[0]) - int(salts[1]))


def source_case_key(case: dict[str, Any]) -> tuple[Any, ...]:
    return (
        str(case.get("split")),
        int_value(case.get("global_stream_ordinal")),
        str(case.get("selector")),
    )


def load_split_cases(sources: list[Path], split: str, global_start: int) -> tuple[list[dict[str, Any]], int, dict[str, int]]:
    cases: list[dict[str, Any]] = []
    counts: dict[str, int] = {}
    global_ord = global_start
    split_ord = 0
    for source in sources:
        source_cases = p901.p899.cases_for_expanded_source(source)
        counts[str(source)] = len(source_cases)
        for case in source_cases:
            case["split"] = split
            case["split_stream_ordinal"] = split_ord
            case["global_stream_ordinal"] = global_ord
            case["source_stream_ordinal"] = split_ord
            cases.append(case)
            split_ord += 1
            global_ord += 1
    return cases, global_ord, counts


def compact_case(case: dict[str, Any]) -> dict[str, Any]:
    salts = row_salts(case)
    return {
        "global_stream_ordinal": int_value(case.get("global_stream_ordinal")),
        "leaf_signature": leaf_signature(case),
        "ops_over_rho": case.get("ops_over_rho"),
        "policy": case.get("policy"),
        "public_key_verified": bool(case.get("public_key_verified")),
        "rank": case.get("rank"),
        "relation_count": case.get("relation_count"),
        "row_leaf_keys": case.get("row_leaf_keys") or [],
        "row_salts": salts,
        "row_selector": case.get("row_selector"),
        "salt_gap": salt_gap(case),
        "selector": case.get("selector"),
        "selector_group": p901.p900.selector_group(str(case.get("selector"))),
        "source": case.get("source"),
        "source_index": int_value(case.get("source_index")),
        "source_verified": bool(case.get("source_verified")),
        "split": case.get("split"),
        "split_stream_ordinal": int_value(case.get("split_stream_ordinal")),
        "target": case.get("target"),
        "top_k": int_value(case.get("top_k")),
        "transfer_index": int_value(case.get("transfer_index")),
    }


def compact_eval(item: dict[str, Any]) -> dict[str, Any]:
    case = item.get("case") or {}
    return {
        "baseline_motif_ops": item.get("baseline_motif_ops"),
        "candidate_search_factor_work": item.get("candidate_search_factor_work"),
        "candidate_search_motif_ops": item.get("candidate_search_motif_ops"),
        "case": compact_case(case),
        "concrete_union_dedup_ops": item.get("concrete_union_dedup_ops"),
        "concrete_union_dedup_ops_over_rho": item.get("concrete_union_dedup_ops_over_rho"),
        "duplicate_factor_count": item.get("duplicate_factor_count"),
        "duplicate_factor_work_saved": item.get("duplicate_factor_work_saved"),
        "errors": item.get("errors") or [],
        "fixed_overhead_charged": item.get("fixed_overhead_charged"),
        "generator_case_cost_ops": item.get("generator_case_cost_ops"),
        "public_key_verified": bool(case.get("public_key_verified")),
        "reconstructed": bool(item.get("reconstructed")),
        "rho_estimate": item.get("rho_estimate"),
        "row_count": item.get("row_count"),
        "row_factor_work_sum": item.get("row_factor_work_sum"),
        "shared_leaf_work": item.get("shared_leaf_work"),
        "strict_below_rho": bool(item.get("strict_below_rho")),
        "strict_below_rho_margin_ops": item.get("strict_below_rho_margin_ops"),
        "strict_below_rho_target_ops": item.get("strict_below_rho_target_ops"),
        "unique_factor_count": item.get("unique_factor_count"),
        "unique_factor_work": item.get("unique_factor_work"),
    }


def evaluate_source_cases(cases: list[dict[str, Any]], max_factor_degree: int) -> list[dict[str, Any]]:
    ps = p901.p899.p897.p893.p842.load_module(
        "ecdlp_public_slice_for_p903",
        p901.p899.p897.p893.p842.PUBLIC_SLICE_SCRIPT,
    )
    records_by_case = p901.p899.load_records_by_case(ps, cases, int(max_factor_degree))
    evaluated: list[dict[str, Any]] = []
    for case_index, case in enumerate(cases):
        local_records = p901.p899.local_records_for_case(records_by_case, case_index, case)
        item = p901.p899.p897.evaluate_case_policy(ps, local_records, case, POLICY)
        item_case = item.setdefault("case", {})
        for key in (
            "global_stream_ordinal",
            "split",
            "split_stream_ordinal",
            "source",
            "source_index",
            "source_stream_ordinal",
            "target",
        ):
            item_case[key] = case.get(key)
        item["generator_case_cost_ops"] = p901.source_case_cost(item)
        evaluated.append(compact_eval(item))
    return evaluated


def frozen_spec() -> dict[str, Any]:
    return {
        "leaf_signatures": ["19/19"],
        "name": "p901_frozen_leaf19_top4_low_leaf_or_hybrid_source_ops_ge_0p70_gap_ge_0",
        "salt_gap_min": 0,
        "selector_groups": ["low_leaf", "hybrid"],
        "source_ops_min": 0.70,
        "top_ks": [4],
    }


def make_specs() -> list[dict[str, Any]]:
    specs: list[dict[str, Any]] = [frozen_spec()]
    for leaf_name, leaves in LEAF_SETS:
        for top_name, top_ks in TOP_K_SETS:
            for group_name, groups in GROUP_SETS:
                for source_ops_min in SOURCE_OPS_THRESHOLDS:
                    for gap_min in SALT_GAP_THRESHOLDS:
                        name = (
                            f"{leaf_name}_{top_name}_{group_name}_"
                            f"opsge{str(source_ops_min).replace('.', 'p')}_gapge{gap_min}"
                        )
                        specs.append(
                            {
                                "leaf_signatures": leaves,
                                "name": name,
                                "salt_gap_min": gap_min,
                                "selector_groups": groups,
                                "source_ops_min": source_ops_min,
                                "top_ks": top_ks,
                            }
                        )
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for spec in specs:
        key = json.dumps(spec, sort_keys=True)
        if key not in seen:
            seen.add(key)
            out.append(spec)
    return out


def matches(row: dict[str, Any], spec: dict[str, Any]) -> bool:
    case = row.get("case") or {}
    if str(case.get("target")) != TARGET:
        return False
    leaves = set(spec.get("leaf_signatures") or [])
    if leaves and case.get("leaf_signature") not in leaves:
        return False
    top_ks = spec.get("top_ks")
    if top_ks is not None and int_value(case.get("top_k")) not in {int_value(v) for v in top_ks}:
        return False
    groups = spec.get("selector_groups")
    if groups is not None and case.get("selector_group") not in set(groups):
        return False
    if float_value(case.get("ops_over_rho")) < float_value(spec.get("source_ops_min")):
        return False
    if int_value(case.get("salt_gap"), -1) < int_value(spec.get("salt_gap_min")):
        return False
    return True


def is_good(row: dict[str, Any]) -> bool:
    return bool(row.get("strict_below_rho") and row.get("public_key_verified"))


def row_set_key(row: dict[str, Any]) -> tuple[Any, ...]:
    case = row.get("case") or {}
    return (
        int_value(case.get("transfer_index")),
        tuple(
            (
                str(row_leaf.get("row_key")),
                tuple(int_value(leaf) for leaf in row_leaf.get("leaf_indices") or []),
            )
            for row_leaf in case.get("row_leaf_keys") or []
        ),
    )


def compact_stop(row: dict[str, Any] | None, total_cost: int | None = None) -> dict[str, Any] | None:
    if row is None:
        return None
    case = row.get("case") or {}
    return {
        "concrete_union_dedup_ops": row.get("concrete_union_dedup_ops"),
        "concrete_union_dedup_ops_over_rho": row.get("concrete_union_dedup_ops_over_rho"),
        "generator_case_cost_ops": row.get("generator_case_cost_ops"),
        "global_stream_ordinal": case.get("global_stream_ordinal"),
        "leaf_signature": case.get("leaf_signature"),
        "ops_over_rho": case.get("ops_over_rho"),
        "public_key_verified": row.get("public_key_verified"),
        "rank": case.get("rank"),
        "relation_count": case.get("relation_count"),
        "rho_estimate": row.get("rho_estimate"),
        "row_leaf_keys": case.get("row_leaf_keys"),
        "row_salts": case.get("row_salts"),
        "salt_gap": case.get("salt_gap"),
        "selector": case.get("selector"),
        "selector_group": case.get("selector_group"),
        "split": case.get("split"),
        "split_stream_ordinal": case.get("split_stream_ordinal"),
        "strict_below_rho": row.get("strict_below_rho"),
        "strict_below_rho_margin_ops": row.get("strict_below_rho_margin_ops"),
        "top_k": case.get("top_k"),
        "total_cost_ops": total_cost,
        "total_cost_over_rho": ratio(total_cost, RHO_ESTIMATE) if total_cost is not None else None,
        "transfer_index": case.get("transfer_index"),
    }


def direct_sort_key(row: dict[str, Any], order: str) -> tuple[Any, ...]:
    case = row.get("case") or {}
    if order == "artifact":
        return (int_value(case.get("global_stream_ordinal")), str(case.get("selector")))
    if order == "source_ops_desc_artifact":
        return (
            -float_value(case.get("ops_over_rho")),
            int_value(case.get("global_stream_ordinal")),
            str(case.get("selector")),
        )
    if order == "salt_gap_desc_artifact":
        return (
            -int_value(case.get("salt_gap"), -1),
            int_value(case.get("global_stream_ordinal")),
            str(case.get("selector")),
        )
    raise ValueError(f"unknown direct order {order!r}")


def evaluate_direct(rows: list[dict[str, Any]], spec: dict[str, Any], split: str | None, order: str) -> dict[str, Any]:
    selected = [
        row
        for row in rows
        if (split is None or (row.get("case") or {}).get("split") == split) and matches(row, spec)
    ]
    ordered = sorted(selected, key=lambda row: direct_sort_key(row, order))
    generation_cost = 0
    remat_cost = 0
    false_before_first_good = 0
    first_selected = ordered[0] if ordered else None
    first_strict = None
    first_good = None
    first_good_total = None
    distinct_good: dict[tuple[Any, ...], dict[str, Any]] = {}
    second_distinct_good = None
    second_distinct_total = None
    for row in ordered:
        generation_cost += 1
        remat_cost += int_value(row.get("generator_case_cost_ops"), 1)
        total = generation_cost + remat_cost
        if row.get("strict_below_rho") and first_strict is None:
            first_strict = row
        if is_good(row):
            key = row_set_key(row)
            if key not in distinct_good:
                distinct_good[key] = row
                if len(distinct_good) == 2:
                    second_distinct_good = row
                    second_distinct_total = total
            if first_good is None:
                first_good = row
                first_good_total = total
        elif first_good is None:
            false_before_first_good += 1
    total_cost = generation_cost + remat_cost
    return {
        "distinct_good_row_set_count": len(distinct_good),
        "false_before_first_good": false_before_first_good,
        "first_good_stop": compact_stop(first_good, first_good_total),
        "first_selected": compact_stop(first_selected),
        "first_strict_stop": compact_stop(first_strict),
        "generation_cost_ops": generation_cost,
        "margin_pass": bool(first_good and first_good_total is not None and first_good_total <= MARGIN_TARGET_OPS),
        "mode": f"direct_{order}",
        "order": order,
        "public_key_verified_count": len([row for row in selected if row.get("public_key_verified")]),
        "rematerialization_cost_ops": remat_cost,
        "second_distinct_good_stop": compact_stop(second_distinct_good, second_distinct_total),
        "selected_count": len(selected),
        "strict_boundary_pass": bool(first_good and first_good_total is not None and first_good_total <= STRICT_TARGET_OPS),
        "strict_count": len([row for row in selected if row.get("strict_below_rho")]),
        "total_cost_ops": total_cost,
        "total_cost_over_rho": ratio(total_cost, RHO_ESTIMATE),
        "verified_strict_count": len([row for row in selected if is_good(row)]),
    }


def evaluate_artifact(rows: list[dict[str, Any]], spec: dict[str, Any], split: str | None) -> dict[str, Any]:
    ordered = sorted(
        [row for row in rows if split is None or (row.get("case") or {}).get("split") == split],
        key=lambda row: (
            int_value((row.get("case") or {}).get("global_stream_ordinal")),
            str((row.get("case") or {}).get("selector")),
        ),
    )
    screen_cost = 0
    remat_cost = 0
    selected_before_first_good = 0
    false_before_first_good = 0
    first_selected = None
    first_good = None
    first_good_total = None
    for row in ordered:
        screen_cost += 1
        if not matches(row, spec):
            continue
        selected_before_first_good += 1
        remat_cost += int_value(row.get("generator_case_cost_ops"), 1)
        total = screen_cost + remat_cost
        if first_selected is None:
            first_selected = row
        if is_good(row):
            first_good = row
            first_good_total = total
            break
        false_before_first_good += 1
    total_cost = screen_cost + remat_cost
    return {
        "false_before_first_good": false_before_first_good,
        "first_good_stop": compact_stop(first_good, first_good_total),
        "first_selected": compact_stop(first_selected),
        "margin_pass": bool(first_good and first_good_total is not None and first_good_total <= MARGIN_TARGET_OPS),
        "mode": "artifact_order_control",
        "rematerialization_cost_ops": remat_cost,
        "screen_cost_ops": screen_cost,
        "selected_before_first_good": selected_before_first_good,
        "strict_boundary_pass": bool(first_good and first_good_total is not None and first_good_total <= STRICT_TARGET_OPS),
        "total_cost_ops": total_cost,
        "total_cost_over_rho": ratio(total_cost, RHO_ESTIMATE),
    }


def best_direct(directs: list[dict[str, Any]]) -> dict[str, Any]:
    with_good = [item for item in directs if item.get("first_good_stop")]
    if with_good:
        return min(with_good, key=lambda item: int_value((item.get("first_good_stop") or {}).get("total_cost_ops"), 10**12))
    return min(directs, key=lambda item: int_value(item.get("selected_count"), 10**12))


def evaluate_spec(rows: list[dict[str, Any]], spec: dict[str, Any]) -> dict[str, Any]:
    direct_train = [evaluate_direct(rows, spec, "train", order) for order in DIRECT_ORDERS]
    direct_validation = [evaluate_direct(rows, spec, "validation", order) for order in DIRECT_ORDERS]
    direct_combined = [evaluate_direct(rows, spec, None, order) for order in DIRECT_ORDERS]
    return {
        "artifact_combined": evaluate_artifact(rows, spec, None),
        "artifact_train": evaluate_artifact(rows, spec, "train"),
        "artifact_validation": evaluate_artifact(rows, spec, "validation"),
        "best_combined_direct": best_direct(direct_combined),
        "best_train_direct": best_direct(direct_train),
        "best_validation_direct": best_direct(direct_validation),
        "direct_combined_orders": direct_combined,
        "direct_train_orders": direct_train,
        "direct_validation_orders": direct_validation,
        "spec": spec,
    }


def spec_is_success(item: dict[str, Any]) -> bool:
    train = item.get("best_train_direct") or {}
    validation = item.get("best_validation_direct") or {}
    combined = item.get("best_combined_direct") or {}
    return bool(
        train.get("margin_pass")
        and validation.get("margin_pass")
        and int_value(combined.get("distinct_good_row_set_count")) >= 2
    )


def spec_has_validation_signal(item: dict[str, Any]) -> bool:
    validation = item.get("best_validation_direct") or {}
    return bool(validation.get("first_good_stop"))


def spec_has_train_control(item: dict[str, Any]) -> bool:
    train = item.get("best_train_direct") or {}
    return bool(train.get("first_good_stop"))


def rank_spec(item: dict[str, Any]) -> tuple[int, int, int, int, str]:
    validation = item.get("best_validation_direct") or {}
    train = item.get("best_train_direct") or {}
    combined = item.get("best_combined_direct") or {}
    first_validation = validation.get("first_good_stop") or {}
    first_train = train.get("first_good_stop") or {}
    return (
        0 if validation.get("margin_pass") else 1,
        0 if validation.get("first_good_stop") else 1,
        int_value(first_validation.get("total_cost_ops"), 10**9),
        -int_value(combined.get("distinct_good_row_set_count")),
        str((item.get("spec") or {}).get("name")),
    )


def determine_claim(evaluated_specs: list[dict[str, Any]]) -> str:
    if any(spec_is_success(item) for item in evaluated_specs):
        return "P903_RELAXED_PUBLIC_GRID_VALIDATION_PASS_NEEDS_FRESH_FREEZE"
    if any(
        spec_has_validation_signal(item)
        and (item.get("best_validation_direct") or {}).get("margin_pass")
        for item in evaluated_specs
    ):
        return "P903_RELAXED_PUBLIC_GRID_VALIDATION_MARGIN_SIGNAL_NEEDS_DIVERSITY"
    if any(spec_has_validation_signal(item) for item in evaluated_specs):
        return "P903_RELAXED_PUBLIC_GRID_VALIDATION_SIGNAL_COST_NEGATIVE"
    if any(spec_has_train_control(item) for item in evaluated_specs):
        return "NEGATIVE_RESULT_P903_RELAXED_GRID_TRAIN_ONLY"
    return "NEGATIVE_RESULT_P903_RELAXED_GRID_NO_STRICT_SIGNAL"


def summarize_cases(rows: list[dict[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for split in ("train", "validation"):
        split_rows = [row for row in rows if (row.get("case") or {}).get("split") == split]
        out[split] = {
            "case_count": len(split_rows),
            "public_key_verified_count": len([row for row in split_rows if row.get("public_key_verified")]),
            "strict_count": len([row for row in split_rows if row.get("strict_below_rho")]),
            "verified_strict_count": len([row for row in split_rows if is_good(row)]),
        }
    return out


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    train_cases, next_global, train_counts = load_split_cases(TRAIN_SOURCES, "train", 0)
    validation_cases, _next_global, validation_counts = load_split_cases(
        VALIDATION_SOURCES,
        "validation",
        next_global,
    )
    cases = train_cases + validation_cases
    evaluated_cases = evaluate_source_cases(cases, int(args.max_factor_degree))
    specs = make_specs()
    evaluated_specs = [evaluate_spec(evaluated_cases, spec) for spec in specs]
    successes = sorted([item for item in evaluated_specs if spec_is_success(item)], key=rank_spec)
    validation_signals = sorted([item for item in evaluated_specs if spec_has_validation_signal(item)], key=rank_spec)
    frozen = next(
        item for item in evaluated_specs if (item.get("spec") or {}).get("name") == frozen_spec()["name"]
    )
    claim_status = determine_claim(evaluated_specs)
    return {
        "artifacts": {
            "contract": str(args.contract),
            "script": str(Path(__file__)),
        },
        "claim_status": claim_status,
        "created_at": now_iso(),
        "evaluated_cases": evaluated_cases,
        "evaluated_specs": evaluated_specs,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "PUBLIC-GRID SCOUT: public source metadata defines the grid; future windows must freeze any promoted spec.",
            "DIRECT-GENERATOR ASSUMPTION: direct-family accounting assumes direct enumeration of selected public families.",
            "RANK/DESCENT BOUNDARY: relation equations, target-eliminated rank, and individual-log descent remain open.",
            "POLLARD-RHO BOUNDARY: this is not a complete general faster-than-rho ECDLP algorithm.",
        ],
        "method": "p903_relaxed_family_grid_validation",
        "parameters": {
            "direct_orders": list(DIRECT_ORDERS),
            "leaf_sets": LEAF_SETS,
            "margin_target_ops": MARGIN_TARGET_OPS,
            "max_factor_degree": int(args.max_factor_degree),
            "policy": POLICY,
            "rho_estimate": RHO_ESTIMATE,
            "salt_gap_thresholds": SALT_GAP_THRESHOLDS,
            "source_ops_thresholds": SOURCE_OPS_THRESHOLDS,
            "spec_count": len(specs),
            "strict_target_ops": STRICT_TARGET_OPS,
            "target": TARGET,
            "top_k_sets": TOP_K_SETS,
        },
        "rank_descent_obligations": {
            "can_promote_to_descent": False,
            "factor_relation_rank_computed": False,
            "individual_log_descent_integrated": False,
            "obligation": (
                "Freeze any promoted public family on later windows, export relation certificates, "
                "compute target-eliminated factor rank, and test individual-log descent."
            ),
            "relation_equations_exported": False,
            "target_eliminated_rank_integrated": False,
        },
        "schema": SCHEMA,
        "source_paths": {
            "train": [str(path) for path in TRAIN_SOURCES],
            "validation": [str(path) for path in VALIDATION_SOURCES],
        },
        "summary": {
            "best_success_specs": successes[:10],
            "best_validation_signal_specs": validation_signals[:10],
            "case_summary": summarize_cases(evaluated_cases),
            "frozen_control": frozen,
            "source_case_count_by_path": {
                "train": train_counts,
                "validation": validation_counts,
            },
            "success_spec_count": len(successes),
            "validation_signal_spec_count": len(validation_signals),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-factor-degree", type=int, default=1)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    print(
        json.dumps(
            {
                "claim_status": payload["claim_status"],
                "parameters": {
                    "spec_count": payload["parameters"]["spec_count"],
                    "source_case_count": len(payload["evaluated_cases"]),
                    "target": payload["parameters"]["target"],
                },
                "summary": {
                    "case_summary": payload["summary"]["case_summary"],
                    "frozen_control": {
                        "best_train_direct": payload["summary"]["frozen_control"]["best_train_direct"],
                        "best_validation_direct": payload["summary"]["frozen_control"]["best_validation_direct"],
                        "spec": payload["summary"]["frozen_control"]["spec"],
                    },
                    "success_spec_count": payload["summary"]["success_spec_count"],
                    "validation_signal_spec_count": payload["summary"]["validation_signal_spec_count"],
                    "best_success_specs": [
                        {
                            "best_combined_direct": item["best_combined_direct"],
                            "best_train_direct": item["best_train_direct"],
                            "best_validation_direct": item["best_validation_direct"],
                            "spec": item["spec"],
                        }
                        for item in payload["summary"]["best_success_specs"][:3]
                    ],
                    "best_validation_signal_specs": [
                        {
                            "best_train_direct": item["best_train_direct"],
                            "best_validation_direct": item["best_validation_direct"],
                            "spec": item["spec"],
                        }
                        for item in payload["summary"]["best_validation_signal_specs"][:3]
                    ],
                },
            },
            indent=2,
            sort_keys=True,
        )
    )
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
