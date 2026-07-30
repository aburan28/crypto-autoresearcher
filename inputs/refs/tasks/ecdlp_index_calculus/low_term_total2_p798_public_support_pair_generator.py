#!/usr/bin/env python3
"""P798 public support-pair generator search."""

from __future__ import annotations

import argparse
import importlib.util
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P797_SCRIPT = TASK_DIR / "low_term_total2_p797_selected_line_hit_generator_audit.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P777_SUMMARY = STATE_DIR / "low_term_total2_p777_merged_trim12_factor_first_cost_audit_summary.json"
DEFAULT_P786_SUMMARY = STATE_DIR / "low_term_total2_p786_public_coordinate_bridge_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p798_public_support_pair_generator_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p798_public_support_pair_generator.md"
SCHEMA = "ecdlp.low_term_total2_p798_public_support_pair_generator.v1"
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
    digits = "".join(ch for ch in str(seed_label) if ch.isdigit())
    return int(digits or 0)


def tuple_text(values: tuple[int, ...] | list[int]) -> str:
    return ",".join(str(int(value)) for value in values)


def add_mod_literals(literals: set[str], prefix: str, value: int, moduli: list[int]) -> None:
    for modulus in moduli:
        literals.add(f"{prefix}_mod_{modulus}={int(value) % int(modulus)}")


def add_bucket_literals(literals: set[str], prefix: str, value: int, widths: list[int]) -> None:
    for width in widths:
        literals.add(f"{prefix}_bucket_{width}={int(value) // int(width)}")


def selected_public_sets(
    trained_by_target: dict[str, dict[tuple[int, int, int, int], dict[str, Any]]],
) -> dict[str, dict[str, Any]]:
    selectors: dict[str, dict[str, Any]] = {}
    for group_key, trained in trained_by_target.items():
        lines = {tuple(int(value) for value in key) for key in trained}
        supports = {tuple(int(value) for value in key[:2]) for key in lines}
        endpoints = sorted({part for support in supports for part in support})
        gaps = sorted({abs(int(support[1]) - int(support[0])) for support in supports})
        selectors[group_key] = {
            "endpoints": endpoints,
            "gaps": gaps,
            "line_ratio_mod": {
                str(modulus): sorted({int(line[3]) % modulus for line in lines if int(line[2]) == 1})
                for modulus in [8, 16, 32, 64]
            },
            "line_count": len(lines),
            "support_count": len(supports),
            "support_sum_mod": {
                str(modulus): sorted({(int(support[0]) + int(support[1])) % modulus for support in supports})
                for modulus in [8, 16, 32, 64]
            },
            "supports": [list(support) for support in sorted(supports)],
        }
    return selectors


def row_feature_table(
    p793: Any,
    eval_prepared_by_namespace: dict[str, dict[str, dict[str, Any]]],
    trained_by_target: dict[str, dict[tuple[int, int, int, int], dict[str, Any]]],
) -> list[dict[str, Any]]:
    rows = []
    for namespace, prepared_by_target in eval_prepared_by_namespace.items():
        for group_key, prepared in prepared_by_target.items():
            trained = trained_by_target[group_key]
            selected_lines = {tuple(int(value) for value in key) for key in trained}
            selected_supports = {tuple(int(value) for value in key[:2]) for key in selected_lines}
            line_rows, support_rows = p797.line_and_support_hits(
                p793,
                prepared["records"],
                int(prepared["order"]),
                selected_lines,
                selected_supports,
            )
            form_features: dict[str, dict[str, Any]] = defaultdict(
                lambda: {
                    "endpoints": set(),
                    "gaps": set(),
                    "line_ratio_mod": defaultdict(set),
                    "literals": set(),
                    "support_pairs": set(),
                    "support_sum_mod": defaultdict(set),
                    "two_factor_form_count": 0,
                }
            )
            for record in prepared["records"]:
                row_key = str(record["row_key"])
                support = tuple(int(value) for value in record["support"])
                item = form_features[row_key]
                item["support_pairs"].add(support)
                item["endpoints"].update(support)
                item["two_factor_form_count"] += 1
                literals: set[str] = item["literals"]
                if len(support) == 2:
                    gap = abs(support[1] - support[0])
                    support_sum = support[0] + support[1]
                    item["gaps"].add(gap)
                    add_mod_literals(literals, "support_gap", gap, [3, 5, 7, 8, 16])
                    add_mod_literals(literals, "support_sum", support_sum, [3, 5, 7, 8, 16])
                    add_bucket_literals(literals, "support_min", min(support), [8, 16])
                    add_bucket_literals(literals, "support_max", max(support), [8, 16])
                    add_bucket_literals(literals, "support_gap", gap, [4, 8])
                    for modulus in [8, 16, 32, 64]:
                        item["support_sum_mod"][modulus].add(support_sum % modulus)
                coeffs = [int(value) for value in record["factor_coeffs"]]
                add_mod_literals(literals, "factor_coeff_sum", sum(coeffs), [3, 5, 7, 8, 16])
                literals.add(f"factor_coeff_parity={tuple_text([value % 2 for value in coeffs])}")
                add_mod_literals(literals, "q_coeff", int(record["q_coeff"]), [3, 5, 7, 8, 16])
                add_mod_literals(literals, "form_index", int(record["form_index"]), [2, 4, 8])
                parts = p793.line_parts(record, int(prepared["order"]))
                if parts is not None:
                    line_key = tuple(int(value) for value in parts["line_key"])
                    if int(line_key[2]) == 1:
                        for modulus in [8, 16, 32, 64]:
                            residue = int(line_key[3]) % modulus
                            item["line_ratio_mod"][modulus].add(residue)
                            literals.add(f"line_ratio_mod_{modulus}={residue}")
                    else:
                        literals.add("line_ratio_vertical=true")
            for row_key, meta in prepared["rows_meta"].items():
                seed_value = seed_int(str(meta["seed_label"]))
                literals = set(form_features[row_key]["literals"])
                add_mod_literals(literals, "seed_index", seed_value, [4, 8, 16, 32])
                add_mod_literals(literals, "row_index", int(meta["row_index"]), [4, 8, 16, 32])
                add_mod_literals(literals, "replica", int(meta["replica"]), [2, 4])
                form_count = int(form_features[row_key]["two_factor_form_count"])
                add_bucket_literals(literals, "two_factor_form_count", form_count, [1, 2, 4])
                rows.append(
                    {
                        "dest_group_key": group_key,
                        "dest_target": prepared["dest_target"],
                        "endpoints": sorted(int(value) for value in form_features[row_key]["endpoints"]),
                        "gaps": sorted(int(value) for value in form_features[row_key]["gaps"]),
                        "generic_rho_steps": int(meta["generic_rho_steps"]),
                        "line_hit": row_key in line_rows,
                        "line_ratio_mod": {
                            str(modulus): sorted(int(value) for value in residues)
                            for modulus, residues in form_features[row_key]["line_ratio_mod"].items()
                        },
                        "literals": sorted(literals),
                        "namespace": namespace,
                        "online_group_additions": int(meta["online_group_additions"]),
                        "replica": int(meta["replica"]),
                        "row_index": int(meta["row_index"]),
                        "row_key": row_key,
                        "seed_int": seed_value,
                        "seed_label": str(meta["seed_label"]),
                        "support_hit": row_key in support_rows,
                        "support_pairs": [list(support) for support in sorted(form_features[row_key]["support_pairs"])],
                        "support_sum_mod": {
                            str(modulus): sorted(int(value) for value in residues)
                            for modulus, residues in form_features[row_key]["support_sum_mod"].items()
                        },
                        "two_factor_form_count": form_count,
                    }
                )
    return rows


def target_selector(policy: dict[str, Any], group_key: str) -> dict[str, Any]:
    return (policy.get("selector_by_target") or {}).get(group_key) or {}


def selected_by_public_policy(row: dict[str, Any], policy: dict[str, Any]) -> bool:
    selector_type = policy.get("selector_type")
    group_key = str(row["dest_group_key"])
    selector = target_selector(policy, group_key)
    supports = {tuple(int(value) for value in support) for support in row["support_pairs"]}
    endpoints = {int(value) for value in row["endpoints"]}
    gaps = {int(value) for value in row["gaps"]}
    if selector_type == "exact_line":
        return bool(row["line_hit"])
    if selector_type == "exact_support_pair":
        selected = {tuple(int(value) for value in support) for support in selector.get("supports") or []}
        return bool(supports & selected)
    if selector_type == "endpoint_both":
        selected = {int(value) for value in selector.get("endpoints") or []}
        return any(set(support) <= selected for support in supports)
    if selector_type == "endpoint_one":
        selected = {int(value) for value in selector.get("endpoints") or []}
        return bool(endpoints & selected)
    if selector_type == "gap_exact":
        selected = {int(value) for value in selector.get("gaps") or []}
        return bool(gaps & selected)
    if selector_type == "support_sum_mod":
        modulus = str(policy["modulus"])
        selected = {int(value) for value in selector.get("support_sum_mod", {}).get(modulus) or []}
        return bool({int(value) for value in row["support_sum_mod"].get(modulus, [])} & selected)
    if selector_type == "line_ratio_mod":
        modulus = str(policy["modulus"])
        selected = {int(value) for value in selector.get("line_ratio_mod", {}).get(modulus) or []}
        return bool({int(value) for value in row["line_ratio_mod"].get(modulus, [])} & selected)
    if selector_type == "literal_any":
        selected = set(str(value) for value in policy.get("selected_literals") or [])
        return bool(set(row["literals"]) & selected)
    raise ValueError(f"unknown selector_type: {selector_type}")


def choose_literal_policy(rows: list[dict[str, Any]], top_k: int, min_rows: int) -> dict[str, Any]:
    stats: dict[str, Counter] = defaultdict(Counter)
    for row in rows:
        for literal in row["literals"]:
            stats[literal]["rows"] += 1
            stats[literal]["hits"] += int(bool(row["support_hit"]))
    ranked = sorted(
        [
            (literal, counts)
            for literal, counts in stats.items()
            if int(counts["rows"]) >= int(min_rows)
        ],
        key=lambda item: (
            ratio(item[1]["hits"], item[1]["rows"]) or 0.0,
            item[1]["hits"],
            -item[1]["rows"],
            item[0],
        ),
        reverse=True,
    )
    selected = [literal for literal, _counts in ranked[: min(int(top_k), len(ranked))]]
    return {
        "description": f"top {top_k} coarse public row/form literals by policy-train support-hit rate",
        "kind": "learned_public_literal",
        "name": f"coarse_literal_top{top_k}",
        "selected_literal_count": len(selected),
        "selected_literals": selected,
        "selector_type": "literal_any",
    }


def base_policies(selector_by_target: dict[str, dict[str, Any]], literal_train_rows: list[dict[str, Any]], args: argparse.Namespace) -> list[dict[str, Any]]:
    compact_selector = {
        group_key: {
            "endpoints": selector["endpoints"],
            "gaps": selector["gaps"],
            "line_ratio_mod": selector["line_ratio_mod"],
            "support_count": selector["support_count"],
            "support_sum_mod": selector["support_sum_mod"],
            "supports": selector["supports"],
        }
        for group_key, selector in selector_by_target.items()
    }
    policies = [
        {
            "description": "positive control: exact selected line membership after form extraction",
            "kind": "exact_oracle_control",
            "name": "exact_line_control",
            "selector_by_target": compact_selector,
            "selector_type": "exact_line",
        },
        {
            "description": "model policy: generator emits rows containing trained public support pairs",
            "kind": "support_pair_generator_model",
            "name": "exact_support_pair_model",
            "selector_by_target": compact_selector,
            "selector_type": "exact_support_pair",
        },
        {
            "description": "public support-shape policy: rows whose form endpoints are both in trained support endpoints",
            "kind": "public_support_shape",
            "name": "endpoint_union_both",
            "selector_by_target": compact_selector,
            "selector_type": "endpoint_both",
        },
        {
            "description": "public support-shape policy: rows with at least one trained support endpoint",
            "kind": "public_support_shape",
            "name": "endpoint_union_one",
            "selector_by_target": compact_selector,
            "selector_type": "endpoint_one",
        },
        {
            "description": "public support-shape policy: rows with a trained exact support gap",
            "kind": "public_support_shape",
            "name": "support_gap_exact",
            "selector_by_target": compact_selector,
            "selector_type": "gap_exact",
        },
    ]
    for modulus in csv_ints(args.support_sum_moduli):
        policies.append(
            {
                "description": f"public support-shape policy: support sum residue modulo {modulus}",
                "kind": "public_support_shape",
                "modulus": int(modulus),
                "name": f"support_sum_mod{modulus}",
                "selector_by_target": compact_selector,
                "selector_type": "support_sum_mod",
            }
        )
    for modulus in csv_ints(args.line_ratio_moduli):
        policies.append(
            {
                "description": f"public support-shape policy: line coefficient-ratio residue modulo {modulus}",
                "kind": "public_support_shape",
                "modulus": int(modulus),
                "name": f"line_ratio_mod{modulus}",
                "selector_by_target": compact_selector,
                "selector_type": "line_ratio_mod",
            }
        )
    policies.extend(
        choose_literal_policy(literal_train_rows, top_k, int(args.literal_min_rows))
        for top_k in csv_ints(args.literal_top_ks)
    )
    return policies


def score_subset(
    p797: Any,
    p793: Any,
    prepared: dict[str, Any],
    trained: dict[tuple[int, int, int, int], dict[str, Any]],
    row_keys: set[str],
    field_weight: int,
    control_count: int,
) -> dict[str, Any]:
    return p797.score_subset(p793, prepared, trained, row_keys, field_weight, control_count)


def evaluate_policy(
    p797: Any,
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
        if row["namespace"] in namespaces and selected_by_public_policy(row, policy)
    ]
    for row in selected_rows:
        selected_by_ns_target[(row["namespace"], row["dest_group_key"])].add(str(row["row_key"]))

    target_once_costs = {
        group_key: p797.train_cost(trained, train_prepared_by_target[group_key])
        for group_key, trained in trained_by_target.items()
    }
    totals = Counter()
    controls = []
    namespace_details = []
    for namespace in namespaces:
        ns_totals = Counter()
        for group_key, prepared in eval_prepared_by_namespace[namespace].items():
            row_keys = selected_by_ns_target[(namespace, group_key)]
            scored = score_subset(
                p797,
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
            for key in ["generated_online_group_additions", "generated_row_count", "generated_row_rho_baseline", "scoring_field_ops"]:
                ns_totals[key] += int(scored[key])
                totals[key] += int(scored[key])
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
    scan_total = (
        train_online
        + eval_population_online
        + int(field_weight) * (train_field_ops + int(totals["scoring_field_ops"]))
    )
    recovered_rho = int(totals["recovered_rho_baseline"])
    target_count = len(trained_by_target)
    row_count = 0
    if namespaces:
        sample_target = next(iter(eval_prepared_by_namespace[namespaces[0]].values()))
        row_count = len(namespaces) * target_count * int(sample_target["row_count"])
    return {
        "aggregate": {
            **dict(totals),
            "eval_namespace_count": len(namespaces),
            "eval_population_online_group_additions": eval_population_online,
            "eval_population_rho_baseline": eval_population_rho,
            "generated_once_train_total_unit_cost": generated_total,
            "generated_once_train_total_unit_cost_over_generated_row_rho": ratio(
                generated_total,
                int(totals["generated_row_rho_baseline"]),
            ),
            "generated_once_train_total_unit_cost_over_recovered_rho": ratio(generated_total, recovered_rho),
            "max_control_recovered_row_count": max(controls, default=0),
            "primary_minus_max_control_recovered_rows": int(totals["recovered_row_count"]) - max(controls, default=0),
            "recovered_row_rate_over_generated": ratio(int(totals["recovered_row_count"]), int(totals["generated_row_count"])),
            "scan_once_train_total_unit_cost": scan_total,
            "scan_once_train_total_unit_cost_over_recovered_rho": ratio(scan_total, recovered_rho),
            "selected_row_rate_over_population": ratio(int(totals["generated_row_count"]), row_count),
            "target_count": target_count,
            "train_calibration_field_ops": train_field_ops,
            "train_calibration_online_group_additions": train_online,
            "train_population_online_group_additions": train_population_online,
        },
        "namespace_details": namespace_details,
        "policy": compact_policy(policy),
    }


def compact_policy(policy: dict[str, Any]) -> dict[str, Any]:
    compact = {key: value for key, value in policy.items() if key != "selector_by_target"}
    if "selector_by_target" in policy:
        compact["selector_by_target_summary"] = {
            group_key: {
                "endpoint_count": len(selector.get("endpoints") or []),
                "gap_count": len(selector.get("gaps") or []),
                "line_ratio_mod_counts": {
                    modulus: len(values)
                    for modulus, values in (selector.get("line_ratio_mod") or {}).items()
                },
                "support_count": len(selector.get("supports") or []),
                "support_sum_mod_counts": {
                    modulus: len(values)
                    for modulus, values in (selector.get("support_sum_mod") or {}).items()
                },
                "support_sample": (selector.get("supports") or [])[:8],
            }
            for group_key, selector in policy["selector_by_target"].items()
        }
    if "selected_literals" in compact:
        compact["selected_literal_sample"] = compact["selected_literals"][:20]
        compact.pop("selected_literals", None)
    return compact


def determine_policy_claim(result: dict[str, Any]) -> str:
    aggregate = result["aggregate"]
    policy = result["policy"]
    if int(aggregate["generated_row_count"]) == 0:
        return "no_generated_rows"
    if int(aggregate["recovered_row_count"]) <= int(aggregate["max_control_recovered_row_count"]):
        return "does_not_beat_controls"
    generated_ratio = aggregate["generated_once_train_total_unit_cost_over_recovered_rho"] or 10**9
    train_charged_ratio = aggregate.get("policy_train_charged_generated_total_unit_cost_over_recovered_rho")
    selected_rate = aggregate["selected_row_rate_over_population"] or 1.0
    broad_selector = float(selected_rate) >= 0.90
    if (
        policy["kind"] == "learned_public_literal"
        and generated_ratio < 1.0
        and (train_charged_ratio or 10**9) < 1.0
        and not broad_selector
    ):
        return "learned_public_literal_train_charged_below_rho"
    if policy["kind"] == "learned_public_literal" and generated_ratio < 1.0 and not broad_selector:
        return "learned_public_literal_generated_below_rho"
    if policy["kind"] == "learned_public_literal" and generated_ratio < 1.0:
        return "learned_public_literal_broad_or_uncharged_boundary"
    if policy["kind"] == "public_support_shape" and generated_ratio < 1.0 and not broad_selector:
        return "public_support_shape_generated_below_rho"
    if policy["kind"] == "public_support_shape" and generated_ratio < 1.0:
        return "public_support_shape_broad_population_boundary"
    if policy["kind"] == "support_pair_generator_model" and generated_ratio < 1.0:
        return "support_pair_generator_model_below_rho"
    if policy["kind"] == "exact_oracle_control" and generated_ratio < 1.0:
        return "exact_line_control_below_rho"
    return "cost_boundary"


def determine_claim(summary: dict[str, Any]) -> str:
    claims = [
        item["policy_claim"]
        for budget_result in summary["budget_results"]
        for item in budget_result["policy_results"]
    ]
    if "learned_public_literal_train_charged_below_rho" in claims:
        return "P798_PUBLIC_COARSE_GENERATOR_TRAIN_CHARGED_BELOW_RHO_SIGNAL"
    if "learned_public_literal_generated_below_rho" in claims:
        return "P798_PUBLIC_COARSE_GENERATOR_GENERATED_BELOW_RHO_SIGNAL"
    if "public_support_shape_generated_below_rho" in claims:
        return "P798_PUBLIC_SUPPORT_SHAPE_GENERATOR_SIGNAL"
    if (
        "support_pair_generator_model_below_rho" in claims
        and (
            "learned_public_literal_broad_or_uncharged_boundary" in claims
            or "public_support_shape_broad_population_boundary" in claims
        )
    ):
        return "P798_SUPPORT_PAIR_MODEL_WITH_BROAD_PUBLIC_BOUNDARY_SIGNAL"
    if "support_pair_generator_model_below_rho" in claims:
        return "P798_SUPPORT_PAIR_CONDITIONED_GENERATOR_MODEL_SIGNAL"
    if "exact_line_control_below_rho" in claims:
        return "P798_EXACT_LINE_CONTROL_ONLY"
    return "NEGATIVE_RESULT_P798_PUBLIC_SUPPORT_PAIR_GENERATOR_NO_BELOW_RHO"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    global p797
    p797 = load_module("ecdlp_p797_for_p798", P797_SCRIPT)
    p796 = p797.load_module("ecdlp_p796_for_p798", p797.P796_SCRIPT)
    p795 = p796.load_module("ecdlp_p795_for_p798", p796.P795_SCRIPT)
    p794 = p795.load_module("ecdlp_p794_for_p798", p795.P794_SCRIPT)
    p793 = p794.load_module("ecdlp_p793_for_p798", p794.P793_SCRIPT)
    p792 = p793.load_module("ecdlp_p792_for_p798", p793.P792_SCRIPT)
    p789 = p792.load_module("ecdlp_p789_for_p798", p792.P789_SCRIPT)
    p788 = p789.load_module("ecdlp_p788_for_p798", p789.P788_SCRIPT)
    p787 = p788.load_module("ecdlp_p787_for_p798", p788.P787_SCRIPT)
    p786 = p787.load_module("ecdlp_p786_for_p798", p787.P786_SCRIPT)
    p784 = p786.load_module("ecdlp_p784_for_p798", p786.P784_SCRIPT)
    p782 = p784.load_module("ecdlp_p782_for_p798", p784.P782_SCRIPT)
    p780 = p782.load_module("ecdlp_p780_for_p798", p782.P780_SCRIPT)
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
        selector_by_target = selected_public_sets(trained_by_target)
        row_table = row_feature_table(p793, eval_prepared_by_namespace, trained_by_target)
        literal_train_rows = [row for row in row_table if row["namespace"] in policy_train_namespaces]
        policies = base_policies(selector_by_target, literal_train_rows, args)
        policy_results = []
        for policy in policies:
            namespaces = policy_test_namespaces if policy["kind"] == "learned_public_literal" else eval_namespaces
            scored = evaluate_policy(
                p797,
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
            if policy["kind"] == "learned_public_literal":
                train_scored = evaluate_policy(
                    p797,
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
                train_scan_online = int(train_scored["aggregate"]["eval_population_online_group_additions"])
                train_charged_total = int(scored["aggregate"]["generated_once_train_total_unit_cost"]) + train_scan_online
                scored["aggregate"]["policy_train_scan_online_group_additions"] = train_scan_online
                scored["aggregate"]["policy_train_charged_generated_total_unit_cost"] = train_charged_total
                scored["aggregate"]["policy_train_charged_generated_total_unit_cost_over_recovered_rho"] = ratio(
                    train_charged_total,
                    int(scored["aggregate"]["recovered_rho_baseline"]),
                )
                scored["policy_train_aggregate"] = train_scored["aggregate"]
                scored["policy_train_namespaces"] = policy_train_namespaces
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
        best_non_exact = min(
            [
                item
                for item in policy_results
                if item["policy"]["kind"] not in {"exact_oracle_control", "support_pair_generator_model"}
                and item["aggregate"]["generated_once_train_total_unit_cost_over_recovered_rho"] is not None
            ],
            key=lambda item: item["aggregate"]["generated_once_train_total_unit_cost_over_recovered_rho"],
            default=None,
        )
        budget_results.append(
            {
                "best_generated": best_result_compact(best_generated),
                "best_non_exact_generated": best_result_compact(best_non_exact),
                "budget": int(budget),
                "policy_results": policy_results,
            }
        )

    best_support_pair_model = min(
        [
            item
            for item in all_policy_results
            if item["policy"]["kind"] == "support_pair_generator_model"
            and item["aggregate"]["generated_once_train_total_unit_cost_over_recovered_rho"] is not None
        ],
        key=lambda item: item["aggregate"]["generated_once_train_total_unit_cost_over_recovered_rho"],
        default=None,
    )
    best_public_non_exact = min(
        [
            item
            for item in all_policy_results
            if item["policy"]["kind"] not in {"exact_oracle_control", "support_pair_generator_model"}
            and item["aggregate"]["generated_once_train_total_unit_cost_over_recovered_rho"] is not None
        ],
        key=lambda item: item["aggregate"]["generated_once_train_total_unit_cost_over_recovered_rho"],
        default=None,
    )
    summary = {
        "best_public_non_exact_generated": best_result_compact(best_public_non_exact),
        "best_support_pair_model": best_result_compact(best_support_pair_model),
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
            "p797_script": str(P797_SCRIPT),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(summary),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "MODEL-GENERATOR: exact support-pair policies assume rows can be generated or filtered by support pair without full population scan.",
            "PUBLIC-SHAPE-POLICIES: broader support-shape selectors are public but still require a constructive generator for deployment relevance.",
            "LEARNED-POLICIES: coarse literals are trained on held-out namespaces and tested on separate namespaces, but remain toy evidence.",
            "NO DEPLOYED-CURVE CLAIM: no large-prime scaling, production-key relevance, or complete faster-than-rho ECDLP algorithm is implied.",
        ],
        "method": "p798_public_support_pair_generator",
        "parameters": {
            "budgets": budgets,
            "control_count": args.control_count,
            "eval_namespaces": eval_namespaces,
            "eval_replicas": args.eval_replicas,
            "field_weight": args.field_weight,
            "line_ratio_moduli": csv_ints(args.line_ratio_moduli),
            "literal_min_rows": args.literal_min_rows,
            "literal_top_ks": csv_ints(args.literal_top_ks),
            "max_relations": args.max_relations,
            "max_subsets": args.max_subsets,
            "min_line_rows": args.min_line_rows,
            "policy_test_namespaces": policy_test_namespaces,
            "policy_train_namespaces": policy_train_namespaces,
            "row_policy": args.row_policy,
            "sparse_policies": csv_strings(args.sparse_policies),
            "support_sum_moduli": csv_ints(args.support_sum_moduli),
            "train_replicas": args.train_replicas,
            "train_seed_namespace": args.train_seed_namespace,
            "walk_mode": args.walk_mode,
            "width": args.width,
        },
        "schema": SCHEMA,
        "summary": summary,
    }


def best_result_compact(item: dict[str, Any] | None) -> dict[str, Any] | None:
    if item is None:
        return None
    aggregate = item["aggregate"]
    return {
        "budget": item.get("budget"),
        "generated_once_train_total_unit_cost_over_recovered_rho": aggregate["generated_once_train_total_unit_cost_over_recovered_rho"],
        "generated_row_count": aggregate["generated_row_count"],
        "max_control_recovered_row_count": aggregate["max_control_recovered_row_count"],
        "policy": item["policy"]["name"],
        "policy_claim": item["policy_claim"],
        "recovered_row_count": aggregate["recovered_row_count"],
        "scan_once_train_total_unit_cost_over_recovered_rho": aggregate["scan_once_train_total_unit_cost_over_recovered_rho"],
        "selected_row_rate_over_population": aggregate["selected_row_rate_over_population"],
        "train_charged_ratio": aggregate.get("policy_train_charged_generated_total_unit_cost_over_recovered_rho"),
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
                        "scan_once_train_total_unit_cost_over_recovered_rho": aggregate["scan_once_train_total_unit_cost_over_recovered_rho"],
                        "selected_row_rate_over_population": aggregate["selected_row_rate_over_population"],
                    },
                    "policy": policy_result["policy"],
                    "policy_claim": policy_result["policy_claim"],
                }
            )
        compact_budget_results.append(
            {
                "best_generated": budget_result["best_generated"],
                "best_non_exact_generated": budget_result["best_non_exact_generated"],
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
    parser.add_argument("--support-sum-moduli", default="8,16,32")
    parser.add_argument("--line-ratio-moduli", default="16,32,64")
    parser.add_argument("--literal-top-ks", default="8,16,32,64")
    parser.add_argument("--literal-min-rows", type=int, default=20)
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
                "best_public_non_exact_generated": summary["summary"]["best_public_non_exact_generated"],
                "best_support_pair_model": summary["summary"]["best_support_pair_model"],
                "budget_best": [
                    {
                        "best": item["best_generated"],
                        "best_non_exact": item["best_non_exact_generated"],
                        "budget": item["budget"],
                    }
                    for item in summary["summary"]["budget_results"]
                ],
                "claim_status": summary["claim_status"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
