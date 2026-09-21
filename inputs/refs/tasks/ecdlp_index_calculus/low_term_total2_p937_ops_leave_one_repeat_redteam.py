#!/usr/bin/env python3
"""P937 leave-one repeat red-team for the P936 ops switch guard."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p908_p907_public_rowset_dedup_rank_cost as p908
import low_term_total2_p930_inner_cv_oracle_distillation_audit as p930


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p937_ops_leave_one_repeat_redteam.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p937_ops_leave_one_repeat_redteam_probe.json"
P936_SOURCE = STATE_DIR / "low_term_total2_p936_ops_switch_guard_probe.json"
SCHEMA = "ecdlp.low_term_total2_p937_ops_leave_one_repeat_redteam.v1"
P936_STRATEGY = "ops_high_singleton_window_count_gain"
P935_BASE = "p935_repeat2_switch_rank_min1_reproduced"


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


def guarded_items(
    base_items: list[dict[str, Any]],
    p936_items: list[dict[str, Any]],
    repeat_threshold: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    base_by_window = {str(item.get("heldout_source_window")): item for item in base_items}
    p936_by_window = {str(item.get("heldout_source_window")): item for item in p936_items}
    rule_by_window = {window: selected_ops_rule(item) for window, item in p936_by_window.items()}
    out: list[dict[str, Any]] = []
    decisions: list[dict[str, Any]] = []
    for window in sorted(base_by_window):
        rule = rule_by_window.get(window, "")
        other_counts = Counter(
            other_rule
            for other_window, other_rule in rule_by_window.items()
            if other_window != window and other_rule
        )
        accepted = bool(rule) and other_counts[rule] >= repeat_threshold
        selected = p936_by_window[window] if accepted else base_by_window[window]
        selected = {
            **selected,
            "selector_metadata": {
                **(selected.get("selector_metadata") or {}),
                "guard": "leave_one_exact_ops_rule_repeat",
                "guard_repeat_threshold": repeat_threshold,
                "guard_rule_name": rule,
                "guard_rule_other_window_count": other_counts.get(rule, 0),
                "guard_selected_source": "p936_ops" if accepted else "p935_base",
            },
        }
        support = selected.get("heldout_support") or {}
        decisions.append(
            {
                "accepted": accepted,
                "guard_rule_name": rule,
                "guard_rule_other_window_count": other_counts.get(rule, 0),
                "heldout_false_indices": support.get("false_selected_indices"),
                "heldout_recovered_positive_indices": support.get("recovered_positive_indices"),
                "heldout_source_window": window,
                "selected_source": "p936_ops" if accepted else "p935_base",
            }
        )
        out.append(selected)
    return out, {
        "decisions": decisions,
        "repeat_threshold": repeat_threshold,
        "rule_counts_all_windows": dict(Counter(rule for rule in rule_by_window.values() if rule)),
    }


def batch_items(
    base_items: list[dict[str, Any]],
    p936_items: list[dict[str, Any]],
    train_windows: set[str],
    name: str,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    base_by_window = {str(item.get("heldout_source_window")): item for item in base_items}
    p936_by_window = {str(item.get("heldout_source_window")): item for item in p936_items}
    allowed = {
        selected_ops_rule(item)
        for window, item in p936_by_window.items()
        if window in train_windows and selected_ops_rule(item)
    }
    out: list[dict[str, Any]] = []
    decisions: list[dict[str, Any]] = []
    for window in sorted(base_by_window):
        rule = selected_ops_rule(p936_by_window.get(window) or {})
        accepted = bool(rule) and rule in allowed
        selected = p936_by_window[window] if accepted else base_by_window[window]
        selected = {
            **selected,
            "selector_metadata": {
                **(selected.get("selector_metadata") or {}),
                "guard": name,
                "guard_allowed_rules": sorted(allowed),
                "guard_rule_name": rule,
                "guard_selected_source": "p936_ops" if accepted else "p935_base",
            },
        }
        support = selected.get("heldout_support") or {}
        decisions.append(
            {
                "accepted": accepted,
                "guard_rule_name": rule,
                "heldout_false_indices": support.get("false_selected_indices"),
                "heldout_recovered_positive_indices": support.get("recovered_positive_indices"),
                "heldout_source_window": window,
                "selected_source": "p936_ops" if accepted else "p935_base",
            }
        )
        out.append(selected)
    return out, {"allowed_rules": sorted(allowed), "decisions": decisions, "train_windows": sorted(train_windows)}


def determine_claim(summaries: dict[str, dict[str, Any]]) -> str:
    p936 = summaries.get("p936_ops_high_singleton_window_count_gain_control") or {}
    p936_rec = int_value(p936.get("heldout_recovered_positive_count"))
    for name, summary in summaries.items():
        if not name.startswith("loo_repeat"):
            continue
        if (
            int_value(summary.get("heldout_recovered_positive_count")) == p936_rec
            and int_value(summary.get("heldout_false_selected_count")) == 0
            and int_value(summary.get("p903_pass_count")) == int_value(summary.get("source_window_count"))
        ):
            return "P937_LOO_REPEAT_OPS_GUARD_STABLE"
    if any(
        name.startswith("loo_repeat")
        and int_value(summary.get("heldout_recovered_positive_count")) > int_value((summaries.get(P935_BASE) or {}).get("heldout_recovered_positive_count"))
        for name, summary in summaries.items()
    ):
        return "NEGATIVE_RESULT_P937_LOO_REPEAT_GAINS_BUT_DOES_NOT_MATCH_P936"
    return "NEGATIVE_RESULT_P937_LOO_REPEAT_OPS_GUARD_COLLAPSES_TO_P935"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p936 = load_json(args.p936_source)
    target_rank = int_value((p936.get("parameters") or {}).get("target_rank"), 6)
    p919_cost = int_value(((p936.get("policy_controls") or {}).get("p919") or {}).get("charged_candidate_cost_ops"))
    second = (p936.get("summary") or {}).get("second_holdout") or {}
    base_items = list(second.get(P935_BASE) or [])
    p936_items = list(second.get(P936_STRATEGY) or [])
    windows = sorted(str(item.get("heldout_source_window")) for item in base_items)
    midpoint = len(windows) // 2
    first_half = set(windows[:midpoint])
    second_half = set(windows[midpoint:])
    strategy_items: dict[str, list[dict[str, Any]]] = {
        P935_BASE: base_items,
        "p936_ops_high_singleton_window_count_gain_control": p936_items,
        "oracle_cost_ceiling_upper_bound": list(second.get("oracle_cost_ceiling_upper_bound") or []),
    }
    guard_details: dict[str, Any] = {}
    for threshold in (1, 2):
        name = f"loo_repeat{threshold}_{P936_STRATEGY}"
        items, details = guarded_items(base_items, p936_items, threshold)
        strategy_items[name] = items
        guard_details[name] = details
    for name, train_windows in (
        ("batch_first_half_trains_second_half", first_half),
        ("batch_second_half_trains_first_half", second_half),
    ):
        items, details = batch_items(base_items, p936_items, train_windows, name)
        strategy_items[name] = items
        guard_details[name] = details
    summaries = {name: p930.summarize(items, target_rank, p919_cost) for name, items in strategy_items.items()}
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p936_source": str(args.p936_source),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(summaries),
        "created_at": now_iso(),
        "guard_details": guard_details,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "ARCHIVE-SCOUT: this scores archived rows from P936; no fresh 1160+ compatible row window is claimed.",
            "P903-BLIND-FIT: inherits P936 choices, which removed P903 and current outer heldout labels.",
            "LEAVE-ONE-PUBLIC-REPEAT: target-window ops switch is accepted only if another window selected the same ops rule.",
            "THIN-COHERENCE-SIGNAL: repeat-1 success but repeat-2 failure means the support rests on two-window evidence.",
            "BATCH-SPLIT-DIAGNOSTIC: half-split training is a stress test, not a final fresh replay.",
            "RANK-SIGNAL-NOT-DESCENT: rank 6 is not full factor rank or individual-log descent.",
            "POLLARD-RHO BOUNDARY: this is an index-calculus selector audit, not a complete faster-than-rho ECDLP algorithm.",
        ],
        "method": "p937_ops_leave_one_repeat_redteam",
        "parameters": {
            "p936_claim": p936.get("claim_status"),
            "p936_strategy": P936_STRATEGY,
            "p935_base": P935_BASE,
            "target_rank": target_rank,
            "p919_cost_ops": p919_cost,
        },
        "schema": SCHEMA,
        "summary": {
            "second_holdout": strategy_items,
            "strategy_summaries": summaries,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--p936-source", type=Path, default=P936_SOURCE)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    summaries = (payload.get("summary") or {}).get("strategy_summaries") or {}
    parts = []
    for name in [
        P935_BASE,
        "p936_ops_high_singleton_window_count_gain_control",
        f"loo_repeat1_{P936_STRATEGY}",
        f"loo_repeat2_{P936_STRATEGY}",
        "batch_first_half_trains_second_half",
        "batch_second_half_trains_first_half",
    ]:
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
    print("claim={claim} {parts} out={out}".format(
        claim=payload.get("claim_status"),
        parts=" | ".join(parts),
        out=args.out,
    ))


if __name__ == "__main__":
    main()
