#!/usr/bin/env python3
"""P797 selected-line hit generator audit."""

from __future__ import annotations

import argparse
import importlib.util
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P796_SCRIPT = TASK_DIR / "low_term_total2_p796_support_line_amortization_audit.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P777_SUMMARY = STATE_DIR / "low_term_total2_p777_merged_trim12_factor_first_cost_audit_summary.json"
DEFAULT_P786_SUMMARY = STATE_DIR / "low_term_total2_p786_public_coordinate_bridge_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p797_selected_line_hit_generator_audit_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p797_selected_line_hit_generator_audit.md"
SCHEMA = "ecdlp.low_term_total2_p797_selected_line_hit_generator_audit.v1"
DEFAULT_BUDGETS = "32,128,512"
DEFAULT_EVAL_NAMESPACES = "supportlinevalid-v1,supportlinevalid-v2,supportlinevalid-v3,supportlinevalid-v4"
DEFAULT_POLICY_TRAIN_NAMESPACES = "supportlinevalid-v1,supportlinevalid-v2"
DEFAULT_POLICY_TEST_NAMESPACES = "supportlinevalid-v3,supportlinevalid-v4"


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


def seed_int(seed_label: str) -> int:
    text = str(seed_label)
    digits = "".join(ch for ch in text if ch.isdigit())
    return int(digits or 0)


def row_online(rows_meta: dict[str, dict[str, Any]], row_keys: set[str]) -> int:
    return sum(int(rows_meta[key]["online_group_additions"]) for key in row_keys)


def row_rho(rows_meta: dict[str, dict[str, Any]], row_keys: set[str]) -> int:
    return sum(int(rows_meta[key]["generic_rho_steps"]) for key in row_keys)


def train_cost(
    trained: dict[tuple[int, int, int, int], dict[str, Any]],
    train_prepared: dict[str, Any],
) -> dict[str, int]:
    calibration_row_keys = {item["calibration_row_key"] for item in trained.values()}
    calibration_online = row_online(train_prepared["rows_meta"], calibration_row_keys)
    population_online = sum(int(item["online_group_additions"]) for item in train_prepared["rows_meta"].values())
    calibration_field_ops = sum(int((item.get("field_ops") or {}).get("total_field_ops") or 0) for item in trained.values())
    return {
        "calibration_field_ops": calibration_field_ops,
        "calibration_online_group_additions": calibration_online,
        "calibration_row_count": len(calibration_row_keys),
        "population_online_group_additions": population_online,
    }


def line_and_support_hits(
    p793: Any,
    records: list[dict[str, Any]],
    order: int,
    selected_lines: set[tuple[int, int, int, int]],
    selected_supports: set[tuple[int, int]],
) -> tuple[set[str], set[str]]:
    line_rows = set()
    support_rows = set()
    for record in records:
        parts = p793.line_parts(record, order)
        if parts is None:
            continue
        line_key = tuple(int(value) for value in parts["line_key"])
        support = tuple(int(value) for value in line_key[:2])
        if line_key in selected_lines:
            line_rows.add(str(record["row_key"]))
        if support in selected_supports:
            support_rows.add(str(record["row_key"]))
    return line_rows, support_rows


def row_feature_table(
    p793: Any,
    eval_prepared_by_namespace: dict[str, dict[str, dict[str, Any]]],
    trained_by_target: dict[str, dict[tuple[int, int, int, int], dict[str, Any]]],
) -> list[dict[str, Any]]:
    rows = []
    for namespace, prepared_by_target in eval_prepared_by_namespace.items():
        for group_key, prepared in prepared_by_target.items():
            trained = trained_by_target[group_key]
            selected_lines = set(trained)
            selected_supports = {tuple(int(value) for value in key[:2]) for key in selected_lines}
            line_rows, support_rows = line_and_support_hits(
                p793,
                prepared["records"],
                int(prepared["order"]),
                selected_lines,
                selected_supports,
            )
            for row_key, meta in prepared["rows_meta"].items():
                rows.append(
                    {
                        "dest_group_key": group_key,
                        "dest_target": prepared["dest_target"],
                        "generic_rho_steps": int(meta["generic_rho_steps"]),
                        "line_hit": row_key in line_rows,
                        "namespace": namespace,
                        "online_group_additions": int(meta["online_group_additions"]),
                        "replica": int(meta["replica"]),
                        "row_index": int(meta["row_index"]),
                        "row_key": row_key,
                        "seed_int": seed_int(str(meta["seed_label"])),
                        "seed_label": str(meta["seed_label"]),
                        "support_hit": row_key in support_rows,
                    }
                )
    return rows


def choose_seed_exact(rows: list[dict[str, Any]], top_k: int) -> dict[str, Any]:
    stats: dict[int, Counter] = defaultdict(Counter)
    for row in rows:
        item = stats[int(row["seed_int"])]
        item["rows"] += 1
        item["hits"] += int(bool(row["line_hit"]))
    ranked = sorted(
        stats.items(),
        key=lambda item: (
            ratio(item[1]["hits"], item[1]["rows"]) or 0.0,
            item[1]["hits"],
            -item[0],
        ),
        reverse=True,
    )
    selected = {seed for seed, _counts in ranked[: min(top_k, len(ranked))]}
    return {
        "description": f"top {top_k} seed labels by train line-hit rate",
        "kind": "public_seed",
        "name": f"seed_exact_top{top_k}",
        "selected_seed_ints": sorted(selected),
        "selector": {"type": "seed_exact", "values": sorted(selected)},
    }


def choose_seed_mod(rows: list[dict[str, Any]], modulus: int, take: int) -> dict[str, Any]:
    stats: dict[int, Counter] = defaultdict(Counter)
    for row in rows:
        residue = int(row["seed_int"]) % int(modulus)
        item = stats[residue]
        item["rows"] += 1
        item["hits"] += int(bool(row["line_hit"]))
    ranked = sorted(
        stats.items(),
        key=lambda item: (
            ratio(item[1]["hits"], item[1]["rows"]) or 0.0,
            item[1]["hits"],
            -item[0],
        ),
        reverse=True,
    )
    selected = {residue for residue, _counts in ranked[: min(take, len(ranked))]}
    return {
        "description": f"top {take}/{modulus} seed residues by train line-hit rate",
        "kind": "public_seed",
        "name": f"seed_mod{modulus}_top{take}",
        "selected_residues": sorted(selected),
        "selector": {"modulus": int(modulus), "type": "seed_mod", "values": sorted(selected)},
    }


def row_selected_by_policy(row: dict[str, Any], policy: dict[str, Any]) -> bool:
    selector = policy.get("selector") or {}
    selector_type = selector.get("type")
    if selector_type == "line_oracle":
        return bool(row["line_hit"])
    if selector_type == "support_oracle":
        return bool(row["support_hit"])
    if selector_type == "seed_exact":
        return int(row["seed_int"]) in set(int(value) for value in selector.get("values") or [])
    if selector_type == "seed_mod":
        modulus = int(selector["modulus"])
        return int(row["seed_int"]) % modulus in set(int(value) for value in selector.get("values") or [])
    raise ValueError(f"unknown selector type: {selector_type}")


def score_subset(
    p793: Any,
    prepared: dict[str, Any],
    trained: dict[tuple[int, int, int, int], dict[str, Any]],
    row_keys: set[str],
    field_weight: int,
    control_count: int,
) -> dict[str, Any]:
    rows_meta = {key: value for key, value in prepared["rows_meta"].items() if key in row_keys}
    records = [record for record in prepared["records"] if record["row_key"] in row_keys]
    primary = p793.score_records(records, rows_meta, trained, set(), int(prepared["order"]), int(field_weight))
    controls = []
    for control_index in range(int(control_count)):
        control_calibrated = p793.rotate_calibrations(trained, control_index + 1)
        control = p793.score_records(records, rows_meta, control_calibrated, set(), int(prepared["order"]), int(field_weight))
        controls.append({"control_index": control_index, "recovered_row_count": int(control["recovered_row_count"])})
    return {
        "control_recovered_counts": controls,
        "generated_online_group_additions": row_online(prepared["rows_meta"], row_keys),
        "generated_row_count": len(row_keys),
        "generated_row_rho_baseline": row_rho(prepared["rows_meta"], row_keys),
        "max_control_recovered_row_count": max((item["recovered_row_count"] for item in controls), default=0),
        "primary": primary,
        "scoring_field_ops": int((primary.get("scoring_field_ops") or {}).get("total_field_ops") or 0),
    }


def evaluate_policy(
    p793: Any,
    policy: dict[str, Any],
    row_table: list[dict[str, Any]],
    eval_prepared_by_namespace: dict[str, dict[str, dict[str, Any]]],
    train_prepared_by_target: dict[str, dict[str, Any]],
    trained_by_target: dict[str, dict[tuple[int, int, int, int], dict[str, Any]]],
    namespaces: list[str],
    field_weight: int,
    control_count: int,
) -> dict[str, Any]:
    selected_by_ns_target: dict[tuple[str, str], set[str]] = defaultdict(set)
    selected_rows = [
        row
        for row in row_table
        if row["namespace"] in namespaces and row_selected_by_policy(row, policy)
    ]
    for row in selected_rows:
        selected_by_ns_target[(row["namespace"], row["dest_group_key"])].add(str(row["row_key"]))

    target_once_costs = {
        group_key: train_cost(trained, train_prepared_by_target[group_key])
        for group_key, trained in trained_by_target.items()
    }
    totals = Counter()
    target_count = len(trained_by_target)
    controls = []
    namespace_details = []
    for namespace in namespaces:
        ns_totals = Counter()
        for group_key, prepared in eval_prepared_by_namespace[namespace].items():
            row_keys = selected_by_ns_target[(namespace, group_key)]
            scored = score_subset(
                p793,
                prepared,
                trained_by_target[group_key],
                row_keys,
                field_weight,
                control_count,
            )
            primary = scored["primary"]
            for key in [
                "covered_target_count",
                "recovered_row_count",
                "recovered_rho_baseline",
                "scored_form_count",
                "target_row_mismatch_count",
            ]:
                ns_totals[key] += int(primary.get(key) or 0)
                totals[key] += int(primary.get(key) or 0)
            ns_totals["generated_online_group_additions"] += int(scored["generated_online_group_additions"])
            ns_totals["generated_row_count"] += int(scored["generated_row_count"])
            ns_totals["generated_row_rho_baseline"] += int(scored["generated_row_rho_baseline"])
            ns_totals["scoring_field_ops"] += int(scored["scoring_field_ops"])
            totals["generated_online_group_additions"] += int(scored["generated_online_group_additions"])
            totals["generated_row_count"] += int(scored["generated_row_count"])
            totals["generated_row_rho_baseline"] += int(scored["generated_row_rho_baseline"])
            totals["scoring_field_ops"] += int(scored["scoring_field_ops"])
            controls.append(int(scored["max_control_recovered_row_count"]))
        namespace_details.append({"aggregate": dict(ns_totals), "namespace": namespace})

    train_online = sum(cost["calibration_online_group_additions"] for cost in target_once_costs.values())
    train_field_ops = sum(cost["calibration_field_ops"] for cost in target_once_costs.values())
    train_population_online = sum(cost["population_online_group_additions"] for cost in target_once_costs.values())
    eval_population_online = 0
    eval_population_rho = 0
    for namespace in namespaces:
        for prepared in eval_prepared_by_namespace[namespace].values():
            eval_population_online += sum(int(item["online_group_additions"]) for item in prepared["rows_meta"].values())
            eval_population_rho += sum(int(item["generic_rho_steps"]) for item in prepared["rows_meta"].values())
    generated_total = (
        train_online
        + int(totals["generated_online_group_additions"])
        + int(field_weight) * (train_field_ops + int(totals["scoring_field_ops"]))
    )
    full_total = (
        train_online
        + train_population_online
        + eval_population_online
        + int(field_weight) * (train_field_ops + int(totals["scoring_field_ops"]))
    )
    recovered_rho = int(totals["recovered_rho_baseline"])
    return {
        "aggregate": {
            **dict(totals),
            "eval_namespace_count": len(namespaces),
            "eval_population_online_group_additions": eval_population_online,
            "eval_population_rho_baseline": eval_population_rho,
            "full_population_once_train_total_unit_cost": full_total,
            "full_population_once_train_total_unit_cost_over_recovered_rho": ratio(full_total, recovered_rho),
            "generated_once_train_total_unit_cost": generated_total,
            "generated_once_train_total_unit_cost_over_generated_row_rho": ratio(generated_total, int(totals["generated_row_rho_baseline"])),
            "generated_once_train_total_unit_cost_over_recovered_rho": ratio(generated_total, recovered_rho),
            "max_control_recovered_row_count": max(controls, default=0),
            "primary_minus_max_control_recovered_rows": int(totals["recovered_row_count"]) - max(controls, default=0),
            "recovered_row_rate_over_generated": ratio(int(totals["recovered_row_count"]), int(totals["generated_row_count"])),
            "selected_row_rate_over_population": ratio(int(totals["generated_row_count"]), len(namespaces) * target_count * int(next(iter(eval_prepared_by_namespace[namespaces[0]].values()))["row_count"])),
            "target_count": target_count,
            "train_calibration_field_ops": train_field_ops,
            "train_calibration_online_group_additions": train_online,
            "train_population_online_group_additions": train_population_online,
        },
        "namespace_details": namespace_details,
        "policy": policy,
    }


def determine_policy_claim(result: dict[str, Any]) -> str:
    aggregate = result["aggregate"]
    policy = result["policy"]
    if int(aggregate["generated_row_count"]) == 0:
        return "no_generated_rows"
    if int(aggregate["recovered_row_count"]) <= int(aggregate["max_control_recovered_row_count"]):
        return "does_not_beat_controls"
    if policy["kind"] == "public_seed" and (aggregate["generated_once_train_total_unit_cost_over_recovered_rho"] or 10**9) < 1.0:
        return "public_seed_below_rho"
    if policy["kind"] == "support_oracle" and (aggregate["generated_once_train_total_unit_cost_over_recovered_rho"] or 10**9) < 1.0:
        return "support_oracle_below_rho"
    if policy["kind"] == "line_oracle" and (aggregate["generated_once_train_total_unit_cost_over_recovered_rho"] or 10**9) < 1.0:
        return "line_oracle_below_rho"
    return "cost_boundary"


def determine_claim(summary: dict[str, Any]) -> str:
    claims = [
        item["policy_claim"]
        for budget_result in summary["budget_results"]
        for item in budget_result["policy_results"]
    ]
    if "public_seed_below_rho" in claims:
        return "P797_PUBLIC_SEED_LINE_HIT_GENERATOR_BELOW_RHO_SIGNAL"
    if "support_oracle_below_rho" in claims:
        return "P797_SUPPORT_PAIR_GENERATOR_TARGET_SIGNAL"
    if "line_oracle_below_rho" in claims:
        return "P797_SELECTED_LINE_GENERATOR_UPPER_BOUND_SIGNAL"
    return "NEGATIVE_RESULT_P797_SELECTED_LINE_GENERATOR_AUDIT_NO_BELOW_RHO"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p796 = load_module("ecdlp_p796_for_p797", P796_SCRIPT)
    p795 = p796.load_module("ecdlp_p795_for_p797", p796.P795_SCRIPT)
    p794 = p795.load_module("ecdlp_p794_for_p797", p795.P794_SCRIPT)
    p793 = p794.load_module("ecdlp_p793_for_p797", p794.P793_SCRIPT)
    p792 = p793.load_module("ecdlp_p792_for_p797", p793.P792_SCRIPT)
    p789 = p792.load_module("ecdlp_p789_for_p797", p792.P789_SCRIPT)
    p788 = p789.load_module("ecdlp_p788_for_p797", p789.P788_SCRIPT)
    p787 = p788.load_module("ecdlp_p787_for_p797", p788.P787_SCRIPT)
    p786 = p787.load_module("ecdlp_p786_for_p797", p787.P786_SCRIPT)
    p784 = p786.load_module("ecdlp_p784_for_p797", p786.P784_SCRIPT)
    p782 = p784.load_module("ecdlp_p782_for_p797", p784.P782_SCRIPT)
    p780 = p782.load_module("ecdlp_p780_for_p797", p782.P780_SCRIPT)
    stack = p780.load_stack()
    frozen_pairs = p788.selected_frozen_pairs(p787, args.p786_summary)
    required = sorted({item["dest_group_key"] for item in frozen_pairs})
    base_groups = p784.normalized_groups(args.p777_summary, required)
    budgets = csv_ints(args.budgets)
    eval_namespaces = csv_strings(args.eval_seed_namespaces)
    policy_train_namespaces = csv_strings(args.policy_train_namespaces)
    policy_test_namespaces = csv_strings(args.policy_test_namespaces)
    train_args = p795.namespace_args(args, args.train_seed_namespace, int(args.train_replicas))
    print(f"preparing train namespace {args.train_seed_namespace}", flush=True)
    train_prepared = {
        key: p794.prepare_target(p793, p792, p789, p787, p784, stack, base_groups[key], train_args)
        for key in required
    }
    eval_prepared_by_namespace = {}
    for namespace in eval_namespaces:
        print(f"preparing eval namespace {namespace}", flush=True)
        eval_args = p795.namespace_args(args, namespace, int(args.eval_replicas))
        eval_prepared_by_namespace[namespace] = {
            key: p794.prepare_target(p793, p792, p789, p787, p784, stack, base_groups[key], eval_args)
            for key in required
        }

    budget_results = []
    all_policy_results = []
    for budget in budgets:
        print(f"scoring budget {budget}", flush=True)
        trained_by_target = {
            key: p794.selected_calibrations(prepared["all_calibrated"], int(budget))
            for key, prepared in train_prepared.items()
        }
        row_table = row_feature_table(p793, eval_prepared_by_namespace, trained_by_target)
        policy_train_rows = [row for row in row_table if row["namespace"] in policy_train_namespaces]
        policies = [
            {
                "description": "oracle emits only rows containing an exact frozen selected line key",
                "kind": "line_oracle",
                "name": "exact_line_oracle",
                "selector": {"type": "line_oracle"},
            },
            {
                "description": "oracle emits rows containing a frozen selected support pair, ignoring coefficient ratio",
                "kind": "support_oracle",
                "name": "support_pair_oracle",
                "selector": {"type": "support_oracle"},
            },
        ]
        policies.extend(choose_seed_exact(policy_train_rows, top_k) for top_k in csv_ints(args.seed_exact_top_ks))
        for modulus in csv_ints(args.seed_moduli):
            for take in sorted({1, max(1, modulus // 4), max(1, modulus // 2)}):
                policies.append(choose_seed_mod(policy_train_rows, modulus, take))
        policy_results = []
        for policy in policies:
            namespaces = eval_namespaces if policy["kind"] in {"line_oracle", "support_oracle"} else policy_test_namespaces
            scored = evaluate_policy(
                p793,
                policy,
                row_table,
                eval_prepared_by_namespace,
                train_prepared,
                trained_by_target,
                namespaces,
                int(args.field_weight),
                int(args.control_count),
            )
            if policy["kind"] == "public_seed":
                train_scored = evaluate_policy(
                    p793,
                    policy,
                    row_table,
                    eval_prepared_by_namespace,
                    train_prepared,
                    trained_by_target,
                    policy_train_namespaces,
                    int(args.field_weight),
                    int(args.control_count),
                )
                scored["policy_train_aggregate"] = train_scored["aggregate"]
                scored["policy_train_namespaces"] = policy_train_namespaces
                train_scan_online = int(train_scored["aggregate"]["eval_population_online_group_additions"])
                train_charged_total = int(scored["aggregate"]["generated_once_train_total_unit_cost"]) + train_scan_online
                scored["aggregate"]["policy_train_scan_online_group_additions"] = train_scan_online
                scored["aggregate"]["policy_train_charged_generated_total_unit_cost"] = train_charged_total
                scored["aggregate"]["policy_train_charged_generated_total_unit_cost_over_recovered_rho"] = ratio(
                    train_charged_total,
                    int(scored["aggregate"]["recovered_rho_baseline"]),
                )
            scored["budget"] = int(budget)
            scored["policy_claim"] = determine_policy_claim(scored)
            policy_results.append(scored)
            all_policy_results.append(scored)
        best_generated = min(
            [
                item
                for item in policy_results
                if item["aggregate"]["generated_once_train_total_unit_cost_over_recovered_rho"] is not None
            ],
            key=lambda item: item["aggregate"]["generated_once_train_total_unit_cost_over_recovered_rho"],
            default=None,
        )
        budget_results.append(
            {
                "best_generated": {
                    "generated_once_train_total_unit_cost_over_recovered_rho": best_generated["aggregate"]["generated_once_train_total_unit_cost_over_recovered_rho"],
                    "policy": best_generated["policy"]["name"],
                    "policy_claim": best_generated["policy_claim"],
                    "recovered_row_count": best_generated["aggregate"]["recovered_row_count"],
                }
                if best_generated
                else None,
                "budget": int(budget),
                "policy_results": policy_results,
            }
        )

    best_public = min(
        [
            item
            for item in all_policy_results
            if item["policy"]["kind"] == "public_seed"
            and item["aggregate"]["generated_once_train_total_unit_cost_over_recovered_rho"] is not None
        ],
        key=lambda item: item["aggregate"]["generated_once_train_total_unit_cost_over_recovered_rho"],
        default=None,
    )
    best_oracle = min(
        [
            item
            for item in all_policy_results
            if item["policy"]["kind"] != "public_seed"
            and item["aggregate"]["generated_once_train_total_unit_cost_over_recovered_rho"] is not None
        ],
        key=lambda item: item["aggregate"]["generated_once_train_total_unit_cost_over_recovered_rho"],
        default=None,
    )
    summary = {
        "best_oracle_generated": {
            "budget": best_oracle["budget"],
            "generated_once_train_total_unit_cost_over_recovered_rho": best_oracle["aggregate"]["generated_once_train_total_unit_cost_over_recovered_rho"],
            "policy": best_oracle["policy"]["name"],
            "policy_claim": best_oracle["policy_claim"],
            "recovered_row_count": best_oracle["aggregate"]["recovered_row_count"],
        }
        if best_oracle
        else None,
        "best_public_seed_generated": {
            "budget": best_public["budget"],
            "generated_once_train_total_unit_cost_over_recovered_rho": best_public["aggregate"]["generated_once_train_total_unit_cost_over_recovered_rho"],
            "policy": best_public["policy"]["name"],
            "policy_claim": best_public["policy_claim"],
            "recovered_row_count": best_public["aggregate"]["recovered_row_count"],
            "train_charged_ratio": best_public["aggregate"].get("policy_train_charged_generated_total_unit_cost_over_recovered_rho"),
        }
        if best_public
        else None,
        "budget_results": budget_results,
        "eval_namespaces": eval_namespaces,
        "policy_test_namespaces": policy_test_namespaces,
        "policy_train_namespaces": policy_train_namespaces,
        "train_seed_namespace": args.train_seed_namespace,
    }
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p777_summary": str(args.p777_summary),
            "p786_summary": str(args.p786_summary),
            "p796_script": str(P796_SCRIPT),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(summary),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "ORACLE-POLICIES: exact-line and support-pair policies assume membership can be generated without scanning; they are upper bounds, not algorithms.",
            "PUBLIC-SEED-POLICIES: seed-label filters are train/test public preselectors but may still require a separate discovery scan.",
            "FROZEN-SELECTOR: support-line keys and values are selected from train data and not re-ranked on policy-test outcomes.",
            "NO DEPLOYED-CURVE CLAIM: no large-prime scaling, production-key relevance, or complete faster-than-rho ECDLP algorithm is implied.",
        ],
        "method": "p797_selected_line_hit_generator_audit",
        "parameters": {
            "budgets": budgets,
            "control_count": args.control_count,
            "eval_namespaces": eval_namespaces,
            "eval_replicas": args.eval_replicas,
            "field_weight": args.field_weight,
            "max_relations": args.max_relations,
            "max_subsets": args.max_subsets,
            "min_line_rows": args.min_line_rows,
            "policy_test_namespaces": policy_test_namespaces,
            "policy_train_namespaces": policy_train_namespaces,
            "row_policy": args.row_policy,
            "seed_exact_top_ks": csv_ints(args.seed_exact_top_ks),
            "seed_moduli": csv_ints(args.seed_moduli),
            "sparse_policies": csv_strings(args.sparse_policies),
            "train_replicas": args.train_replicas,
            "train_seed_namespace": args.train_seed_namespace,
            "walk_mode": args.walk_mode,
            "width": args.width,
        },
        "schema": SCHEMA,
        "summary": summary,
    }


def summary_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    summary = payload["summary"]
    compact_budget_results = []
    for budget_result in summary["budget_results"]:
        compact_policies = []
        for policy_result in budget_result["policy_results"]:
            aggregate = policy_result["aggregate"]
            compact_policies.append(
                {
                    "aggregate": {
                        "generated_once_train_total_unit_cost_over_recovered_rho": aggregate["generated_once_train_total_unit_cost_over_recovered_rho"],
                        "generated_row_count": aggregate["generated_row_count"],
                        "max_control_recovered_row_count": aggregate["max_control_recovered_row_count"],
                        "policy_train_charged_generated_total_unit_cost_over_recovered_rho": aggregate.get("policy_train_charged_generated_total_unit_cost_over_recovered_rho"),
                        "primary_minus_max_control_recovered_rows": aggregate["primary_minus_max_control_recovered_rows"],
                        "recovered_row_count": aggregate["recovered_row_count"],
                        "recovered_row_rate_over_generated": aggregate["recovered_row_rate_over_generated"],
                        "selected_row_rate_over_population": aggregate["selected_row_rate_over_population"],
                    },
                    "policy": policy_result["policy"],
                    "policy_claim": policy_result["policy_claim"],
                }
            )
        compact_budget_results.append(
            {
                "best_generated": budget_result["best_generated"],
                "budget": budget_result["budget"],
                "policy_results": compact_policies,
            }
        )
    compact_summary = {
        **summary,
        "budget_results": compact_budget_results,
    }
    return {
        "artifacts": payload["artifacts"],
        "claim_status": payload["claim_status"],
        "created_at": payload["created_at"],
        "honesty_boundary": payload["honesty_boundary"],
        "method": payload["method"],
        "parameters": payload["parameters"],
        "schema": f"{SCHEMA}.summary",
        "summary": compact_summary,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p777-summary", type=Path, default=DEFAULT_P777_SUMMARY)
    parser.add_argument("--p786-summary", type=Path, default=DEFAULT_P786_SUMMARY)
    parser.add_argument("--train-seed-namespace", default="supportline20-v1")
    parser.add_argument("--eval-seed-namespaces", default=DEFAULT_EVAL_NAMESPACES)
    parser.add_argument("--policy-train-namespaces", default=DEFAULT_POLICY_TRAIN_NAMESPACES)
    parser.add_argument("--policy-test-namespaces", default=DEFAULT_POLICY_TEST_NAMESPACES)
    parser.add_argument("--train-replicas", type=int, default=20)
    parser.add_argument("--eval-replicas", type=int, default=20)
    parser.add_argument("--control-count", type=int, default=8)
    parser.add_argument("--field-weight", type=int, default=2)
    parser.add_argument("--min-line-rows", type=int, default=2)
    parser.add_argument("--budgets", default=DEFAULT_BUDGETS)
    parser.add_argument("--seed-exact-top-ks", default="8,16,32,64")
    parser.add_argument("--seed-moduli", default="4,8,16,32")
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
                "best_oracle_generated": summary["summary"]["best_oracle_generated"],
                "best_public_seed_generated": summary["summary"]["best_public_seed_generated"],
                "claim_status": summary["claim_status"],
                "budget_best": [
                    {
                        "best": item["best_generated"],
                        "budget": item["budget"],
                    }
                    for item in summary["summary"]["budget_results"]
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
