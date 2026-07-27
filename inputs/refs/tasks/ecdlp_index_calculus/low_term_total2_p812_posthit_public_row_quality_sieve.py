#!/usr/bin/env python3
"""P812 post-hit public row-quality sieve for all-pair ECDLP rows."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P805_SCRIPT = TASK_DIR / "low_term_total2_p805_public_support_selector_pressure.py"
P806_SCRIPT = TASK_DIR / "low_term_total2_p806_public_feature_classifier.py"
P807_SCRIPT = TASK_DIR / "low_term_total2_p807_richer_public_feature_classifier.py"
P808_SCRIPT = TASK_DIR / "low_term_total2_p808_requested_support_invariant_miner.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P777_SUMMARY = STATE_DIR / "low_term_total2_p777_merged_trim12_factor_first_cost_audit_summary.json"
DEFAULT_P786_SUMMARY = STATE_DIR / "low_term_total2_p786_public_coordinate_bridge_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p812_posthit_public_row_quality_sieve_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p812_posthit_public_row_quality_sieve.md"
SCHEMA = "ecdlp.low_term_total2_p812_posthit_public_row_quality_sieve.v1"

ALL_PAIR = "all_pair_first_hit_control"
POOL_SUPPORT_BUDGET = 0


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


def seed_labels(count: int) -> list[str]:
    return [f"t{index:04d}" for index in range(int(count))]


def slug(value: str) -> str:
    text = "".join(ch if ch.isalnum() else "_" for ch in str(value))
    return "_".join(part for part in text.split("_") if part)


def stat(values: list[float]) -> dict[str, Any]:
    if not values:
        return {"count": 0, "max": None, "mean": None, "min": None}
    return {"count": len(values), "max": max(values), "mean": round(mean(values), 8), "min": min(values)}


def bounded_bin(value: int, modulus: int, bins: int) -> int:
    if modulus <= 0:
        return 0
    return max(0, min(int(bins) - 1, int(value) * int(bins) // int(modulus)))


def index_bin(value: int, size: int, bins: int) -> int:
    return bounded_bin(int(value), max(1, int(size)), int(bins))


def count_bin(value: int) -> str:
    value = int(value)
    if value <= 0:
        return "0"
    if value <= 8:
        return str(value)
    power = 1 << (value.bit_length() - 1)
    return f"{power}+"


def stable_hash_score(*parts: Any) -> int:
    text = "|".join(str(part) for part in parts)
    return int.from_bytes(hashlib.blake2b(text.encode("utf-8"), digest_size=8).digest(), "big")


def policy_kind(policy_name: str) -> str:
    if policy_name == ALL_PAIR:
        return "all_pair_first_hit_pool"
    return "unknown_policy"


def configure_p805(p805: Any) -> None:
    p805.POLICY_NAMES = (ALL_PAIR,)
    p805.PUBLIC_POLICIES = ()
    p805.policy_kind = policy_kind


def scan_all_pair_rows(
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
    supports_by_policy = {(POOL_SUPPORT_BUDGET, ALL_PAIR): p801.all_support_pairs(len(factor_base))}
    point_policy, support_policy_stats = p801.build_point_policy_map(verifier, factor_base, ainvs, p, supports_by_policy)
    rows = []
    for seed_label in seed_labels(int(args.scan_seed_count)):
        full_seed = (
            f"ecdlp-p812-{context['namespace']}-{slug(context['target'])}:"
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
            [POOL_SUPPORT_BUDGET],
            [int(trial_budget)],
            point_policy,
            support_policy_stats,
            args,
        )
        rows.append(scanned[(POOL_SUPPORT_BUDGET, int(trial_budget), ALL_PAIR)])
    stats = support_policy_stats[(POOL_SUPPORT_BUDGET, ALL_PAIR)]
    return rows, {
        "targeted_setup_group_additions": int(stats["targeted_setup_group_additions"]),
        "targeted_support_count": int(stats["targeted_support_count"]),
        "targeted_unique_point_count": int(stats["targeted_unique_point_count"]),
        "targeted_point_collision_count": int(stats["targeted_point_collision_count"]),
    }


def first_form(row: dict[str, Any]) -> dict[str, Any] | None:
    forms = row.get("forms") or []
    return forms[0] if forms else None


def row_record_index(records: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    by_key: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        by_key[str(record["row_key"])].append(record)
    for items in by_key.values():
        items.sort(key=lambda item: int(item["form_index"]))
    return dict(by_key)


def recovered_row_keys(p793: Any, records: list[dict[str, Any]], trained: dict[tuple[int, int, int, int], dict[str, Any]], order: int) -> set[str]:
    recovered = set()
    for record in records:
        parts = p793.line_parts(record, int(order))
        if parts is None or parts["line_key"] not in trained:
            continue
        line_value = int(trained[parts["line_key"]]["line_value"])
        known_sum = (int(parts["scale"]) * line_value) % int(order)
        try:
            secret = ((int(record["rhs"]) - known_sum) * pow(int(record["q_coeff"]), -1, int(order))) % int(order)
        except ValueError:
            continue
        if secret == int(record["expected_secret"]):
            recovered.add(str(record["row_key"]))
    return recovered


def row_public_features(
    p793: Any,
    row_key: str,
    row: dict[str, Any],
    records_by_row: dict[str, list[dict[str, Any]]],
    rows_meta: dict[str, dict[str, Any]],
    order: int,
    factor_base_size: int,
    bins: int,
) -> tuple[str, ...]:
    meta = rows_meta[row_key]
    seed_label = str(meta.get("seed_label") or "")
    seed_digits = "".join(ch for ch in seed_label if ch.isdigit())
    seed_index = int(seed_digits or 0)
    form = first_form(row) or {}
    trial = int(form.get("trial") or row.get("scanned_trials") or 0)
    features = [
        f"seed_mod4={seed_index % 4}",
        f"seed_mod8={seed_index % 8}",
        f"seed_mod16={seed_index % 16}",
        f"seed_bin={index_bin(seed_index, max(1, int(meta.get('row_index') or 0) + 1), bins)}",
        f"trial_bin={index_bin(trial, max(1, int(row.get('configured_trials') or trial or 1)), bins)}",
        f"trial_mod8={trial % 8}",
        f"trial_count_bin={count_bin(trial)}",
        f"online_cost_bin={count_bin(int((row.get('cost_model') or {}).get('collection_online_group_additions') or 0))}",
        f"zero_b={int(row.get('zero_b_hits') or 0)}",
        f"targeted_point_hits={int(row.get('targeted_point_hits') or 0)}",
    ]
    records = records_by_row.get(row_key) or []
    features.append(f"form_record_count_bin={count_bin(len(records))}")
    if not records:
        features.append("record_present=0")
        return tuple(features)
    record = records[0]
    support = tuple(int(index) for index in record["support"])
    left, right = support
    span = abs(left - right)
    parts = p793.line_parts(record, int(order))
    line_key = None if parts is None else tuple(int(value) for value in parts["line_key"])
    scale = 0 if parts is None else int(parts["scale"]) % int(order)
    q_coeff = int(record["q_coeff"]) % int(order)
    rhs = int(record["rhs"]) % int(order)
    c1, c2 = [int(value) % int(order) for value in record["factor_coeffs"]]
    terms = [int(value) % int(order) for value in (form.get("terms") or [])]
    features.extend(
        [
            "record_present=1",
            f"left_bin={index_bin(left, factor_base_size, bins)}",
            f"right_bin={index_bin(right, factor_base_size, bins)}",
            f"span_bin={index_bin(span, factor_base_size, bins)}",
            f"support_sum_mod16={(left + right) % 16}",
            f"support_span_mod8={span % 8}",
            f"line_axis={0 if line_key is None else line_key[2]}",
            f"line_ratio_bin={0 if line_key is None else bounded_bin(line_key[3], order, bins)}",
            f"line_ratio_mod16={0 if line_key is None else line_key[3] % 16}",
            f"scale_bin={bounded_bin(scale, order, bins)}",
            f"scale_mod16={scale % 16}",
            f"q_coeff_bin={bounded_bin(q_coeff, order, bins)}",
            f"q_coeff_mod16={q_coeff % 16}",
            f"rhs_bin={bounded_bin(rhs, order, bins)}",
            f"rhs_mod16={rhs % 16}",
            f"factor_c1_bin={bounded_bin(c1, order, bins)}",
            f"factor_c2_bin={bounded_bin(c2, order, bins)}",
            f"factor_c1_mod16={c1 % 16}",
            f"factor_c2_mod16={c2 % 16}",
            f"factor_sum_mod16={(c1 + c2) % 16}",
            f"a_mod16={int(form.get('a') or 0) % 16}",
            f"b_mod16={int(form.get('b') or 0) % 16}",
        ]
    )
    for index, term in enumerate(terms[:2]):
        features.append(f"term{index}_mod16={term % 16}")
        features.append(f"term{index}_bin={bounded_bin(term, order, bins)}")
    return tuple(features)


def train_logodds_model(examples: list[dict[str, Any]], smoothing: float) -> dict[str, Any]:
    counts: dict[str, Counter] = defaultdict(Counter)
    totals = Counter()
    for example in examples:
        bucket = "positive" if example["label"] else "negative"
        totals[bucket] += 1
        for feature in example["features"]:
            counts[feature][bucket] += 1
    positive = int(totals["positive"])
    negative = int(totals["negative"])
    base = math.log((positive + smoothing) / (negative + smoothing))
    weights = {
        feature: math.log((counter["positive"] + smoothing) / (counter["negative"] + smoothing))
        for feature, counter in counts.items()
    }
    ranked = sorted(weights.items(), key=lambda item: item[1])
    return {
        "base_log_odds": base,
        "feature_count": len(weights),
        "negative_examples": negative,
        "positive_examples": positive,
        "smoothing": float(smoothing),
        "top_negative_features": [{"feature": key, "weight": round(value, 8)} for key, value in ranked[:8]],
        "top_positive_features": [{"feature": key, "weight": round(value, 8)} for key, value in reversed(ranked[-8:])],
        "weights": weights,
    }


def score_example(example: dict[str, Any], model: dict[str, Any]) -> float:
    score = float(model["base_log_odds"])
    weights = model["weights"]
    for feature in example["features"]:
        score += float(weights.get(feature, 0.0))
    return score


def top_row_keys_by_model(examples: list[dict[str, Any]], model: dict[str, Any], count: int) -> set[str]:
    ranked = sorted(examples, key=lambda item: (-score_example(item, model), item["row_key"]))
    return {str(item["row_key"]) for item in ranked[: max(0, min(int(count), len(ranked)))]}


def top_row_keys_by_hash(examples: list[dict[str, Any]], context_id: str, count: int) -> set[str]:
    ranked = sorted(examples, key=lambda item: (stable_hash_score(context_id, item["row_key"]), item["row_key"]))
    return {str(item["row_key"]) for item in ranked[: max(0, min(int(count), len(ranked)))]}


def context_id(namespace: str, group_key: str) -> str:
    return f"{namespace}::{group_key}"


def prepare_context(
    p793: Any,
    p792: Any,
    p789: Any,
    p797: Any,
    rows: list[dict[str, Any]],
    order: int,
    target: str,
    group_key: str,
    namespace: str,
    trained: dict[tuple[int, int, int, int], dict[str, Any]],
    setup_stats: dict[str, Any],
    factor_base_size: int,
    args: argparse.Namespace,
) -> dict[str, Any]:
    records, rows_meta = p792.collect_form_records(p789, [(0, rows, int(order))], str(target))
    records_by_row = row_record_index(records)
    recovered = recovered_row_keys(p793, records, trained, int(order))
    examples = []
    for row_index, row in enumerate(rows):
        row_key = f"{target}:0:{row_index}"
        if row_key not in rows_meta:
            continue
        examples.append(
            {
                "context_id": context_id(namespace, group_key),
                "features": row_public_features(
                    p793,
                    row_key,
                    row,
                    records_by_row,
                    rows_meta,
                    int(order),
                    int(factor_base_size),
                    int(args.feature_bins),
                ),
                "group_key": group_key,
                "label": row_key in recovered,
                "namespace": namespace,
                "row_key": row_key,
                "target": str(target),
            }
        )
    row_keys = set(rows_meta)
    pool_online = p797.row_online(rows_meta, row_keys)
    pool_rho = p797.row_rho(rows_meta, row_keys)
    return {
        "context_id": context_id(namespace, group_key),
        "examples": examples,
        "group_key": group_key,
        "namespace": namespace,
        "order": int(order),
        "pool_online_group_additions": pool_online,
        "pool_recovered_label_count": len(recovered),
        "pool_rho_baseline": pool_rho,
        "pool_row_count": len(row_keys),
        "prepared": {
            "dest_target": str(target),
            "order": int(order),
            "records": records,
            "row_count": len(rows_meta),
            "rows_meta": rows_meta,
        },
        "setup_stats": setup_stats,
        "target": str(target),
    }


def score_context_rows(
    p797: Any,
    p793: Any,
    context: dict[str, Any],
    trained: dict[tuple[int, int, int, int], dict[str, Any]],
    row_keys: set[str],
    args: argparse.Namespace,
) -> dict[str, Any]:
    return p797.score_subset(
        p793,
        context["prepared"],
        trained,
        row_keys,
        int(args.field_weight),
        int(args.control_count),
    )


def group_once_sum(items: list[dict[str, Any]], key: str) -> int:
    values: dict[str, int] = {}
    for item in items:
        group_key = str(item["group_key"])
        values[group_key] = max(values.get(group_key, 0), int(item[key]))
    return sum(values.values())


def aggregate_policy(
    p797: Any,
    p793: Any,
    policy: dict[str, Any],
    selected_by_context: dict[str, set[str]],
    contexts: dict[str, dict[str, Any]],
    trained_by_group: dict[str, dict[tuple[int, int, int, int], dict[str, Any]]],
    train_prepared_by_group: dict[str, dict[str, Any]],
    args: argparse.Namespace,
) -> dict[str, Any]:
    totals = Counter()
    context_results = []
    control_sum = 0
    for cid, context in sorted(contexts.items()):
        row_keys = selected_by_context.get(cid, set())
        scored = score_context_rows(
            p797,
            p793,
            context,
            trained_by_group[context["group_key"]],
            row_keys,
            args,
        )
        primary = scored["primary"]
        control_sum += int(scored["max_control_recovered_row_count"])
        for key in [
            "covered_target_count",
            "recovered_row_count",
            "recovered_rho_baseline",
            "scored_form_count",
            "target_row_mismatch_count",
        ]:
            totals[key] += int(primary.get(key) or 0)
        totals["selected_online_group_additions"] += int(scored["generated_online_group_additions"])
        totals["selected_row_count"] += int(scored["generated_row_count"])
        totals["selected_row_rho_baseline"] += int(scored["generated_row_rho_baseline"])
        totals["scoring_field_ops"] += int(scored["scoring_field_ops"])
        totals["pool_online_group_additions"] += int(context["pool_online_group_additions"])
        totals["pool_rho_baseline"] += int(context["pool_rho_baseline"])
        totals["pool_row_count"] += int(context["pool_row_count"])
        context_results.append(
            {
                "context_id": cid,
                "covered_target_count": int(primary.get("covered_target_count") or 0),
                "group_key": context["group_key"],
                "namespace": context["namespace"],
                "pool_row_count": int(context["pool_row_count"]),
                "recovered_row_count": int(primary.get("recovered_row_count") or 0),
                "selected_row_count": int(scored["generated_row_count"]),
                "target": context["target"],
                "targeted_setup_group_additions": int(context["setup_stats"]["targeted_setup_group_additions"]),
            }
        )

    train_costs = {
        group_key: p797.train_cost(trained, train_prepared_by_group[group_key])
        for group_key, trained in trained_by_group.items()
    }
    setup_items = [
        {
            "group_key": context["group_key"],
            "targeted_setup_group_additions": int(context["setup_stats"]["targeted_setup_group_additions"]),
        }
        for context in contexts.values()
    ]
    target_once_train_online = sum(int(cost["calibration_online_group_additions"]) for cost in train_costs.values())
    target_once_train_field = sum(int(cost["calibration_field_ops"]) for cost in train_costs.values())
    target_once_setup = group_once_sum(setup_items, "targeted_setup_group_additions")
    scoring_field = int(totals["scoring_field_ops"])
    field_weight = int(args.field_weight)
    recovered_rho = int(totals["recovered_rho_baseline"])
    selected_only_total = (
        target_once_train_online
        + target_once_setup
        + int(totals["selected_online_group_additions"])
        + field_weight * (target_once_train_field + scoring_field)
    )
    post_hit_total = (
        target_once_train_online
        + target_once_setup
        + int(totals["pool_online_group_additions"])
        + field_weight * (target_once_train_field + scoring_field)
    )
    aggregate = {
        **dict(totals),
        "context_count": len(contexts),
        "max_control_recovered_row_count": control_sum,
        "post_hit_scan_once_train_total_unit_cost": post_hit_total,
        "post_hit_scan_once_train_total_unit_cost_over_recovered_rho": ratio(post_hit_total, recovered_rho),
        "primary_minus_control_recovered_rows": int(totals["recovered_row_count"]) - control_sum,
        "recovered_row_rate_over_pool": ratio(int(totals["recovered_row_count"]), int(totals["pool_row_count"])),
        "recovered_row_rate_over_selected": ratio(int(totals["recovered_row_count"]), int(totals["selected_row_count"])),
        "selected_only_once_train_total_unit_cost": selected_only_total,
        "selected_only_once_train_total_unit_cost_over_recovered_rho": ratio(selected_only_total, recovered_rho),
        "selected_row_rate_over_pool": ratio(int(totals["selected_row_count"]), int(totals["pool_row_count"])),
        "target_once_setup_group_additions": target_once_setup,
        "target_once_train_calibration_field_ops": target_once_train_field,
        "target_once_train_calibration_online_group_additions": target_once_train_online,
    }
    return {
        "aggregate": aggregate,
        "context_results": context_results,
        "policy": policy,
    }


def build_selected_sets(
    policy_name: str,
    top_k: int,
    contexts: dict[str, dict[str, Any]],
    smoothing: float,
) -> tuple[dict[str, set[str]], list[dict[str, Any]]]:
    selected: dict[str, set[str]] = {}
    model_rows = []
    for cid, context in sorted(contexts.items()):
        examples = context["examples"]
        if policy_name == "all_pool":
            selected[cid] = {str(example["row_key"]) for example in examples}
            continue
        if policy_name == "hash_control":
            selected[cid] = top_row_keys_by_hash(examples, cid, top_k)
            continue
        if policy_name == "loco_logodds":
            train_examples = [
                example
                for other_id, other in sorted(contexts.items())
                if other_id != cid
                for example in other["examples"]
            ]
        elif policy_name == "same_context_upper":
            train_examples = examples
        else:
            raise ValueError(f"unknown policy {policy_name!r}")
        model = train_logodds_model(train_examples, smoothing)
        selected[cid] = top_row_keys_by_model(examples, model, top_k)
        model_rows.append(
            {
                "context_id": cid,
                "feature_count": int(model["feature_count"]),
                "negative_examples": int(model["negative_examples"]),
                "policy": policy_name,
                "positive_examples": int(model["positive_examples"]),
                "top_k": int(top_k),
                "top_positive_features": model["top_positive_features"],
            }
        )
    return selected, model_rows


def compact_policy_result(item: dict[str, Any]) -> dict[str, Any]:
    aggregate = item["aggregate"]
    return {
        "aggregate": {
            "covered_target_count": aggregate["covered_target_count"],
            "max_control_recovered_row_count": aggregate["max_control_recovered_row_count"],
            "pool_row_count": aggregate["pool_row_count"],
            "post_hit_scan_once_train_total_unit_cost_over_recovered_rho": aggregate[
                "post_hit_scan_once_train_total_unit_cost_over_recovered_rho"
            ],
            "primary_minus_control_recovered_rows": aggregate["primary_minus_control_recovered_rows"],
            "recovered_row_count": aggregate["recovered_row_count"],
            "recovered_row_rate_over_pool": aggregate["recovered_row_rate_over_pool"],
            "recovered_row_rate_over_selected": aggregate["recovered_row_rate_over_selected"],
            "recovered_rho_baseline": aggregate["recovered_rho_baseline"],
            "selected_only_once_train_total_unit_cost_over_recovered_rho": aggregate[
                "selected_only_once_train_total_unit_cost_over_recovered_rho"
            ],
            "selected_row_count": aggregate["selected_row_count"],
            "selected_row_rate_over_pool": aggregate["selected_row_rate_over_pool"],
        },
        "policy": item["policy"],
        "policy_claim": item.get("policy_claim"),
    }


def best_result(results: list[dict[str, Any]], kinds: set[str]) -> dict[str, Any] | None:
    candidates = [
        item
        for item in results
        if item["policy"]["kind"] in kinds
        and item["aggregate"]["post_hit_scan_once_train_total_unit_cost_over_recovered_rho"] is not None
    ]
    if not candidates:
        return None
    return min(candidates, key=lambda item: item["aggregate"]["post_hit_scan_once_train_total_unit_cost_over_recovered_rho"])


def determine_policy_claim(item: dict[str, Any], all_pool: dict[str, Any] | None, best_hash: dict[str, Any] | None) -> str:
    aggregate = item["aggregate"]
    kind = item["policy"]["kind"]
    recovered = int(aggregate["recovered_row_count"])
    if recovered <= int(aggregate["max_control_recovered_row_count"]):
        return "does_not_beat_rotated_line_controls"
    post_hit = aggregate["post_hit_scan_once_train_total_unit_cost_over_recovered_rho"]
    if kind == "loco_public_row_quality" and post_hit is not None and post_hit < 1.0:
        return "heldout_public_row_quality_below_rho"
    if kind == "loco_public_row_quality" and all_pool is not None:
        pool_ratio = all_pool["aggregate"]["post_hit_scan_once_train_total_unit_cost_over_recovered_rho"]
        hash_recovered = 0 if best_hash is None else int(best_hash["aggregate"]["recovered_row_count"])
        if pool_ratio is not None and post_hit is not None and post_hit < pool_ratio and recovered > hash_recovered:
            return "heldout_public_row_quality_improves_all_pair_boundary"
    if kind == "same_context_upper" and post_hit is not None and post_hit < 1.0:
        return "same_context_row_quality_upper_below_rho"
    if kind == "hash_control":
        return "hash_control_boundary"
    if kind == "all_pool":
        return "all_pool_boundary"
    return "row_quality_boundary"


def determine_claim(results: list[dict[str, Any]]) -> str:
    claims = {str(item.get("policy_claim")) for item in results}
    if "heldout_public_row_quality_below_rho" in claims:
        return "P812_HELDOUT_PUBLIC_ROW_QUALITY_SIEVE_BELOW_RHO"
    if "heldout_public_row_quality_improves_all_pair_boundary" in claims:
        return "P812_HELDOUT_PUBLIC_ROW_QUALITY_SIEVE_IMPROVES_ALL_PAIR_BOUNDARY"
    if "same_context_row_quality_upper_below_rho" in claims:
        return "P812_SAME_CONTEXT_ROW_QUALITY_UPPER_ONLY"
    return "NEGATIVE_RESULT_P812_POSTHIT_PUBLIC_ROW_QUALITY_SIEVE_FAILS"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p805 = load_module("ecdlp_p805_for_p812", P805_SCRIPT)
    p806 = load_module("ecdlp_p806_for_p812", P806_SCRIPT)
    p807 = load_module("ecdlp_p807_for_p812", P807_SCRIPT)
    p808 = load_module("ecdlp_p808_for_p812", P808_SCRIPT)
    p807.configure_p807(p806)
    configure_p805(p805)

    modules = p808.load_research_stack(p806)
    p801 = modules["p801"]
    p800 = p801.load_module("ecdlp_p800_for_p812", p801.P800_SCRIPT)
    p799 = p800.load_module("ecdlp_p799_for_p812", p800.P799_SCRIPT)
    p798 = p799.load_module("ecdlp_p798_for_p812", p799.P798_SCRIPT)
    p797 = p798.load_module("ecdlp_p797_for_p812", p798.P797_SCRIPT)
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
            print(f"building P812 all-pair context namespace={namespace} group={group_key}", flush=True)
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
            rows, setup_stats = scan_all_pair_rows(
                p805,
                p801,
                p746,
                p748,
                relprobe,
                context,
                trial_budget,
                args,
            )
            prepared_context = prepare_context(
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
    model_rows = []
    policies_to_run = [("all_pool", 0), *[("hash_control", top_k) for top_k in top_ks]]
    policies_to_run.extend(("loco_logodds", top_k) for top_k in top_ks)
    policies_to_run.extend(("same_context_upper", top_k) for top_k in top_ks)
    for policy_name, top_k in policies_to_run:
        print(f"scoring P812 policy={policy_name} top_k={top_k}", flush=True)
        selected, rows = build_selected_sets(policy_name, int(top_k), contexts, float(args.logodds_smoothing))
        model_rows.extend(rows)
        if policy_name == "all_pool":
            policy = {"kind": "all_pool", "name": "all_pool", "top_k": None}
        elif policy_name == "hash_control":
            policy = {"kind": "hash_control", "name": f"hash_top{top_k}", "top_k": int(top_k)}
        elif policy_name == "loco_logodds":
            policy = {"kind": "loco_public_row_quality", "name": f"loco_public_row_quality_top{top_k}", "top_k": int(top_k)}
        else:
            policy = {"kind": "same_context_upper", "name": f"same_context_upper_top{top_k}", "top_k": int(top_k)}
        policy_results.append(
            aggregate_policy(
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
    best_hash = best_result(policy_results, {"hash_control"})
    for item in policy_results:
        item["policy_claim"] = determine_policy_claim(item, all_pool, best_hash)

    summary = {
        "all_pool": None if all_pool is None else compact_policy_result(all_pool),
        "best_hash_control": None if best_hash is None else compact_policy_result(best_hash),
        "best_heldout_public_row_quality": (
            None
            if best_result(policy_results, {"loco_public_row_quality"}) is None
            else compact_policy_result(best_result(policy_results, {"loco_public_row_quality"}))
        ),
        "best_same_context_upper": (
            None
            if best_result(policy_results, {"same_context_upper"}) is None
            else compact_policy_result(best_result(policy_results, {"same_context_upper"}))
        ),
        "calibration_budget": calibration_budget,
        "constructor_namespaces": namespaces,
        "context_diagnostics": context_diagnostics,
        "model_rows": model_rows,
        "policy_results": policy_results,
        "scan_seed_count": int(args.scan_seed_count),
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
            "p805_script": str(P805_SCRIPT),
            "p806_script": str(P806_SCRIPT),
            "p807_script": str(P807_SCRIPT),
            "p808_script": str(P808_SCRIPT),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(policy_results),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "POST-HIT PUBLIC SIEVE: row-quality features are used only after a broad all-pair hit stream is collected.",
            "SCAN-CHARGED: the primary metric charges the full all-pair post-hit scan, not just selected row scoring.",
            "HELD-OUT MODEL: the main public row-quality policy trains on other contexts and selects rows in the held-out context.",
            "SAME-CONTEXT UPPER BOUND: same-context row-quality models use labels from the evaluated context and are diagnostic only.",
            "NO DEPLOYED-CURVE CLAIM: no large-prime scaling, production-key relevance, or complete faster-than-rho ECDLP algorithm is implied.",
        ],
        "method": "p812_posthit_public_row_quality_sieve",
        "parameters": {
            "calibration_budget": calibration_budget,
            "constructor_namespaces": namespaces,
            "control_count": int(args.control_count),
            "feature_bins": int(args.feature_bins),
            "field_weight": int(args.field_weight),
            "logodds_smoothing": float(args.logodds_smoothing),
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
    summary = payload["summary"]
    return {
        **payload,
        "schema": f"{SCHEMA}.summary",
        "summary": {
            **summary,
            "model_rows": [
                {key: value for key, value in row.items() if key != "top_positive_features"}
                for row in summary["model_rows"]
            ],
            "policy_results": [compact_policy_result(item) for item in summary["policy_results"]],
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p777-summary", type=Path, default=DEFAULT_P777_SUMMARY)
    parser.add_argument("--p786-summary", type=Path, default=DEFAULT_P786_SUMMARY)
    parser.add_argument("--train-seed-namespace", default="supportline20-v1")
    parser.add_argument("--constructor-namespaces", default="posthit-p812-rowqual-v20,posthit-p812-rowqual-v21,posthit-p812-rowqual-v22")
    parser.add_argument("--calibration-budget", type=int, default=256)
    parser.add_argument("--trial-budget", type=int, default=256)
    parser.add_argument("--top-ks", default="16,32,64,96,128")
    parser.add_argument("--train-replicas", type=int, default=20)
    parser.add_argument("--scan-seed-count", type=int, default=128)
    parser.add_argument("--control-count", type=int, default=8)
    parser.add_argument("--feature-bins", type=int, default=8)
    parser.add_argument("--field-weight", type=int, default=2)
    parser.add_argument("--logodds-smoothing", type=float, default=1.0)
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
                "best_heldout_public_row_quality": summary["summary"]["best_heldout_public_row_quality"],
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
