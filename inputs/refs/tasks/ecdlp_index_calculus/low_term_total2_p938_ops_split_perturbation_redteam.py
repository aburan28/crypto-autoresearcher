#!/usr/bin/env python3
"""P938 split perturbation red-team for the P936/P937 ops rule."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import low_term_total2_p908_p907_public_rowset_dedup_rank_cost as p908
import low_term_total2_p930_inner_cv_oracle_distillation_audit as p930


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p938_ops_split_perturbation_redteam.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p938_ops_split_perturbation_redteam_probe.json"
P937_SOURCE = STATE_DIR / "low_term_total2_p937_ops_leave_one_repeat_redteam_probe.json"
SCHEMA = "ecdlp.low_term_total2_p938_ops_split_perturbation_redteam.v1"
P935_BASE = "p935_repeat2_switch_rank_min1_reproduced"
P936_CONTROL = "p936_ops_high_singleton_window_count_gain_control"
P937_LOO = "loo_repeat1_ops_high_singleton_window_count_gain"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def int_value(value: Any, default: int = 0) -> int:
    return p908.int_value(value, default)


def selected_ops_rule(item: dict[str, Any]) -> str:
    metadata = item.get("selector_metadata") or {}
    selected = metadata.get("selected_ops_candidate") or {}
    return str(selected.get("rule_name") or "")


def source_window(item: dict[str, Any]) -> str:
    return str(item.get("heldout_source_window"))


def window_start(window: str) -> int:
    try:
        return int(window.split("_", 1)[0])
    except (TypeError, ValueError):
        return 10**12


def window_bucket(window: str) -> int:
    start = window_start(window)
    if start >= 10**12:
        return start
    return start // 8


def by_window(items: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {source_window(item): item for item in items}


def cloned_with_guard(
    item: dict[str, Any],
    guard_name: str,
    rule: str,
    train_rules: Counter[str],
    selected_source: str,
) -> dict[str, Any]:
    return {
        **item,
        "selector_metadata": {
            **(item.get("selector_metadata") or {}),
            "guard": guard_name,
            "guard_rule_name": rule,
            "guard_rule_train_count": train_rules.get(rule, 0),
            "guard_train_rules": dict(train_rules),
            "guard_selected_source": selected_source,
        },
    }


def apply_train_rule_gate(
    base_by: dict[str, dict[str, Any]],
    p936_by: dict[str, dict[str, Any]],
    windows: list[str],
    train_for_window: Callable[[str], set[str]],
    name: str,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    out: list[dict[str, Any]] = []
    decisions: list[dict[str, Any]] = []
    for window in windows:
        train_windows = train_for_window(window)
        train_rules = Counter(
            selected_ops_rule(p936_by[train_window])
            for train_window in train_windows
            if train_window in p936_by and selected_ops_rule(p936_by[train_window])
        )
        rule = selected_ops_rule(p936_by.get(window) or {})
        accepted = bool(rule) and train_rules.get(rule, 0) > 0
        selected = p936_by[window] if accepted else base_by[window]
        selected_source = "p936_ops" if accepted else "p935_base"
        selected = cloned_with_guard(selected, name, rule, train_rules, selected_source)
        support = selected.get("heldout_support") or {}
        decisions.append(
            {
                "accepted": accepted,
                "guard_rule_name": rule,
                "guard_rule_train_count": train_rules.get(rule, 0),
                "heldout_false_indices": support.get("false_selected_indices"),
                "heldout_recovered_positive_indices": support.get("recovered_positive_indices"),
                "heldout_source_window": window,
                "selected_source": selected_source,
                "train_windows": sorted(train_windows, key=lambda item: (window_start(item), item)),
            }
        )
        out.append(selected)
    return out, {"decisions": decisions, "name": name}


def split_test_summary(
    items: list[dict[str, Any]],
    test_windows: set[str],
    target_rank: int,
    p919_cost: int,
) -> dict[str, Any]:
    test_items = [item for item in items if source_window(item) in test_windows]
    return p930.summarize(test_items, target_rank, p919_cost)


def contiguous_halves(windows: list[str]) -> tuple[set[str], set[str]]:
    numeric = sorted(windows, key=lambda item: (window_start(item), item))
    midpoint = len(numeric) // 2
    return set(numeric[:midpoint]), set(numeric[midpoint:])


def contiguous_fold_map(windows: list[str], fold_count: int) -> dict[str, int]:
    numeric = sorted(windows, key=lambda item: (window_start(item), item))
    return {window: min((index * fold_count) // len(numeric), fold_count - 1) for index, window in enumerate(numeric)}


def make_mod_cv(
    base_by: dict[str, dict[str, Any]],
    p936_by: dict[str, dict[str, Any]],
    windows: list[str],
    modulus: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    name = f"bucket_mod{modulus}_cv_train_other_buckets"
    return apply_train_rule_gate(
        base_by,
        p936_by,
        windows,
        lambda window: {other for other in windows if window_bucket(other) % modulus != window_bucket(window) % modulus},
        name,
    )


def make_contiguous_cv(
    base_by: dict[str, dict[str, Any]],
    p936_by: dict[str, dict[str, Any]],
    windows: list[str],
    fold_count: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    folds = contiguous_fold_map(windows, fold_count)
    name = f"contiguous_{fold_count}fold_cv_train_other_folds"
    items, details = apply_train_rule_gate(
        base_by,
        p936_by,
        windows,
        lambda window: {other for other in windows if folds[other] != folds[window]},
        name,
    )
    details["folds"] = {window: folds[window] for window in sorted(windows, key=lambda item: (window_start(item), item))}
    return items, details


def make_directional(
    base_by: dict[str, dict[str, Any]],
    p936_by: dict[str, dict[str, Any]],
    windows: list[str],
    direction: str,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if direction == "past":
        name = "rolling_train_past_only"
        return apply_train_rule_gate(
            base_by,
            p936_by,
            windows,
            lambda window: {other for other in windows if window_start(other) < window_start(window)},
            name,
        )
    if direction == "future":
        name = "rolling_train_future_only"
        return apply_train_rule_gate(
            base_by,
            p936_by,
            windows,
            lambda window: {other for other in windows if window_start(other) > window_start(window)},
            name,
        )
    raise ValueError(f"unknown direction {direction}")


def determine_claim(summaries: dict[str, dict[str, Any]]) -> str:
    p936 = summaries.get(P936_CONTROL) or {}
    p936_rec = int_value(p936.get("heldout_recovered_positive_count"))
    positives = []
    for name, summary in summaries.items():
        if name in {P935_BASE, P936_CONTROL, P937_LOO, "oracle_cost_ceiling_upper_bound"}:
            continue
        if (
            int_value(summary.get("heldout_recovered_positive_count")) == p936_rec
            and int_value(summary.get("heldout_false_selected_count")) == 0
            and int_value(summary.get("p903_pass_count")) == int_value(summary.get("source_window_count"))
        ):
            positives.append(name)
    if positives:
        if any(name.startswith("rolling_train_past") for name in positives):
            return "P938_DIRECTIONAL_SPLIT_OPS_SIGNAL_STABLE_TO_PAST_TRAINING"
        return "P938_SPLIT_PERTURBATION_OPS_SIGNAL_PARTIAL_STABILITY"
    if any(
        name not in {P935_BASE, P936_CONTROL, P937_LOO, "oracle_cost_ceiling_upper_bound"}
        and int_value(summary.get("heldout_recovered_positive_count"))
        > int_value((summaries.get(P935_BASE) or {}).get("heldout_recovered_positive_count"))
        for name, summary in summaries.items()
    ):
        return "NEGATIVE_RESULT_P938_SPLIT_GAINS_BUT_FAILS_FULL_GATE"
    return "NEGATIVE_RESULT_P938_SPLIT_PERTURBATION_COLLAPSES_TO_P935"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p937 = load_json(args.p937_source)
    target_rank = int_value((p937.get("parameters") or {}).get("target_rank"), 6)
    p919_cost = int_value((p937.get("parameters") or {}).get("p919_cost_ops"))
    second = (p937.get("summary") or {}).get("second_holdout") or {}
    base_items = list(second.get(P935_BASE) or [])
    p936_items = list(second.get(P936_CONTROL) or [])
    p937_items = list(second.get(P937_LOO) or [])
    oracle_items = list(second.get("oracle_cost_ceiling_upper_bound") or [])
    windows = sorted([source_window(item) for item in base_items], key=lambda item: (window_start(item), item))
    base_by = by_window(base_items)
    p936_by = by_window(p936_items)
    low_half, high_half = contiguous_halves(windows)

    strategy_items: dict[str, list[dict[str, Any]]] = {
        P935_BASE: base_items,
        P936_CONTROL: p936_items,
        P937_LOO: p937_items,
        "oracle_cost_ceiling_upper_bound": oracle_items,
    }
    details: dict[str, Any] = {
        "window_order_numeric": windows,
        "ops_rule_windows": {
            window: selected_ops_rule(p936_by[window])
            for window in windows
            if selected_ops_rule(p936_by[window])
        },
    }

    for modulus in (2, 3, 4, 5):
        name = f"bucket_mod{modulus}_cv_train_other_buckets"
        items, split_details = make_mod_cv(base_by, p936_by, windows, modulus)
        strategy_items[name] = items
        details[name] = split_details

    for fold_count in (2, 3, 4):
        name = f"contiguous_{fold_count}fold_cv_train_other_folds"
        items, split_details = make_contiguous_cv(base_by, p936_by, windows, fold_count)
        strategy_items[name] = items
        details[name] = split_details

    for direction in ("past", "future"):
        items, split_details = make_directional(base_by, p936_by, windows, direction)
        name = split_details["name"]
        strategy_items[name] = items
        details[name] = split_details

    for name, train_windows, test_windows in (
        ("numeric_low_train_high_test", low_half, high_half),
        ("numeric_high_train_low_test", high_half, low_half),
    ):
        items, split_details = apply_train_rule_gate(
            base_by,
            p936_by,
            windows,
            lambda _window, train_windows=train_windows: set(train_windows),
            name,
        )
        strategy_items[name] = items
        details[name] = {
            **split_details,
            "test_only_summary": split_test_summary(items, test_windows, target_rank, p919_cost),
            "test_windows": sorted(test_windows, key=lambda item: (window_start(item), item)),
            "train_windows": sorted(train_windows, key=lambda item: (window_start(item), item)),
        }

    summaries = {name: p930.summarize(items, target_rank, p919_cost) for name, items in strategy_items.items()}
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p937_source": str(args.p937_source),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(summaries),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "ARCHIVE-SCOUT: this scores frozen P936/P937 rows; no fresh 1160+ compatible replay is claimed.",
            "P903-BLIND-FIT: inherits P936/P937 rule choices, which removed P903 and current outer heldout labels.",
            "TRAIN-RULE-SPLIT: ops acceptance uses train-side public rule names only, then scores on the target split.",
            "SPLIT-DEPENDENCE-TEST: success or failure is interpreted per split family, not as a universal selector theorem.",
            "THIN-COHERENCE-SIGNAL: the ops rule appears in exactly two source windows.",
            "RANK-SIGNAL-NOT-DESCENT: rank 6 is not full factor rank or individual-log descent.",
            "POLLARD-RHO BOUNDARY: this is an index-calculus selector audit, not a complete faster-than-rho ECDLP algorithm.",
        ],
        "method": "p938_ops_split_perturbation_redteam",
        "parameters": {
            "p937_claim": p937.get("claim_status"),
            "p935_base": P935_BASE,
            "p936_control": P936_CONTROL,
            "p937_loo": P937_LOO,
            "target_rank": target_rank,
            "p919_cost_ops": p919_cost,
        },
        "schema": SCHEMA,
        "split_details": details,
        "summary": {
            "second_holdout": strategy_items,
            "strategy_summaries": summaries,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--p937-source", type=Path, default=P937_SOURCE)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    summaries = (payload.get("summary") or {}).get("strategy_summaries") or {}
    report_names = [
        P935_BASE,
        P936_CONTROL,
        P937_LOO,
        "bucket_mod2_cv_train_other_buckets",
        "bucket_mod3_cv_train_other_buckets",
        "contiguous_2fold_cv_train_other_folds",
        "rolling_train_past_only",
        "rolling_train_future_only",
    ]
    parts = []
    for name in report_names:
        summary = summaries.get(name) or {}
        parts.append(
            "{name}:rec={rec}/{pos},false={false},p903_pass={passes}/{total}".format(
                name=name,
                rec=summary.get("heldout_recovered_positive_count"),
                pos=summary.get("heldout_positive_count"),
                false=summary.get("heldout_false_selected_count"),
                passes=summary.get("p903_pass_count"),
                total=summary.get("source_window_count"),
            )
        )
    print(f"claim={payload['claim_status']} " + " | ".join(parts) + f" out={args.out}")


if __name__ == "__main__":
    main()
