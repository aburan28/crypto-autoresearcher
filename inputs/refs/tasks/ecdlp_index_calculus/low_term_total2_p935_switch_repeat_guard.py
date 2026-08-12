#!/usr/bin/env python3
"""P935 public repeat guard over P934 replacement switch choices."""

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
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p935_switch_repeat_guard.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p935_switch_repeat_guard_probe.json"
P934_SOURCE = STATE_DIR / "low_term_total2_p934_replacement_switch_contrast_probe.json"
SCHEMA = "ecdlp.low_term_total2_p935_switch_repeat_guard.v1"
BASE_SWITCH_STRATEGIES = (
    "switch_rank_min1",
    "switch_rank_min2",
    "switch_cost_not_worse_rank_min1",
    "switch_inner_not_worse_rank_min1",
    "switch_pareto_rank_min1",
)
REPEAT_THRESHOLDS = (2, 3)


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


def switch_rule_name(item: dict[str, Any]) -> str:
    metadata = item.get("selector_metadata") or {}
    chosen = metadata.get("chosen_switch_candidate") or {}
    return str(chosen.get("rule_name") or "")


def guarded_items(
    first_items: list[dict[str, Any]],
    switch_items: list[dict[str, Any]],
    threshold: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    switch_by_window = {str(item.get("heldout_source_window")): item for item in switch_items}
    first_by_window = {str(item.get("heldout_source_window")): item for item in first_items}
    counts = Counter(switch_rule_name(item) for item in switch_items if switch_rule_name(item))
    out: list[dict[str, Any]] = []
    decisions: list[dict[str, Any]] = []
    for window in sorted(first_by_window):
        switch_item = switch_by_window.get(window) or {}
        rule_name = switch_rule_name(switch_item)
        accepted = bool(rule_name) and counts[rule_name] >= threshold
        selected = switch_item if accepted else first_by_window[window]
        selected = {
            **selected,
            "selector_metadata": {
                **(selected.get("selector_metadata") or {}),
                "guard": "exact_switch_rule_repeat",
                "guard_threshold": threshold,
                "guard_rule_name": rule_name,
                "guard_rule_repeat_count": counts.get(rule_name, 0),
                "guard_selected_source": "switch" if accepted else "p932_first",
            },
        }
        out.append(selected)
        support = selected.get("heldout_support") or {}
        decisions.append(
            {
                "accepted": accepted,
                "guard_rule_name": rule_name,
                "guard_rule_repeat_count": counts.get(rule_name, 0),
                "heldout_false_indices": support.get("false_selected_indices"),
                "heldout_recovered_positive_indices": support.get("recovered_positive_indices"),
                "heldout_source_window": window,
                "selected_source": "switch" if accepted else "p932_first",
            }
        )
    return out, {
        "decisions": decisions,
        "rule_counts": dict(counts),
        "threshold": threshold,
    }


def determine_claim(summaries: dict[str, dict[str, Any]]) -> str:
    first = summaries.get("p932_loo_token_rank_min2_reproduced") or {}
    first_rec = int_value(first.get("heldout_recovered_positive_count"))
    for name, summary in summaries.items():
        if not name.startswith("repeat"):
            continue
        if (
            int_value(summary.get("heldout_recovered_positive_count")) > first_rec
            and int_value(summary.get("heldout_false_selected_count")) == 0
            and int_value(summary.get("p903_pass_count")) == int_value(summary.get("source_window_count"))
        ):
            return "P935_REPEAT_GUARD_SWITCH_SUPPORT_GAIN"
    if any(
        name.startswith("repeat")
        and int_value(summary.get("heldout_recovered_positive_count")) > first_rec
        for name, summary in summaries.items()
    ):
        return "NEGATIVE_RESULT_P935_REPEAT_GUARD_GAINS_SUPPORT_BUT_FAILS_GATE"
    return "NEGATIVE_RESULT_P935_REPEAT_GUARD_DOES_NOT_BEAT_P932"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p934 = load_json(args.p934_source)
    target_rank = int_value((p934.get("parameters") or {}).get("target_rank"), 6)
    p919_cost = int_value(((p934.get("policy_controls") or {}).get("p919") or {}).get("charged_candidate_cost_ops"))
    second = (p934.get("summary") or {}).get("second_holdout") or {}
    first_items = list(second.get("p932_loo_token_rank_min2_reproduced") or [])
    strategy_items: dict[str, list[dict[str, Any]]] = {
        "seed_only_control": list(second.get("seed_only_control") or []),
        "p932_loo_token_rank_min2_reproduced": first_items,
        "p934_switch_rank_min1_control": list(second.get("switch_rank_min1") or []),
        "oracle_cost_ceiling_upper_bound": list(second.get("oracle_cost_ceiling_upper_bound") or []),
    }
    guard_details: dict[str, Any] = {}
    for base in BASE_SWITCH_STRATEGIES:
        switch_items = list(second.get(base) or [])
        if not switch_items:
            continue
        for threshold in REPEAT_THRESHOLDS:
            name = f"repeat{threshold}_{base}"
            items, details = guarded_items(first_items, switch_items, threshold)
            strategy_items[name] = items
            guard_details[name] = details
    summaries = {name: p930.summarize(items, target_rank, p919_cost) for name, items in strategy_items.items()}
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p934_source": str(args.p934_source),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(summaries),
        "created_at": now_iso(),
        "guard_details": guard_details,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "ARCHIVE-SCOUT: this scores archived rows from P934; no fresh 1160+ compatible row window is claimed.",
            "P903-BLIND-FIT: inherits P934 nested switch choices, which removed P903 and current outer heldout labels.",
            "PUBLIC-COHERENCE-GUARD: exact switch rule repeat counts use public rule names across the batch, not heldout labels.",
            "BATCH-TRANSDUCTIVE: this guard assumes a batch of source windows is available; single fresh-window behavior is unproved.",
            "SUPPORT-NOT-COST: a support gain is not promoted unless exact P903-restored policy remains below P919.",
            "RANK-SIGNAL-NOT-DESCENT: rank 6 is not full factor rank or individual-log descent.",
            "POLLARD-RHO BOUNDARY: this is an index-calculus selector audit, not a complete faster-than-rho ECDLP algorithm.",
        ],
        "method": "p935_switch_repeat_guard",
        "parameters": {
            "base_switch_strategies": list(BASE_SWITCH_STRATEGIES),
            "p934_claim": p934.get("claim_status"),
            "repeat_thresholds": list(REPEAT_THRESHOLDS),
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
    parser.add_argument("--p934-source", type=Path, default=P934_SOURCE)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    summaries = (payload.get("summary") or {}).get("strategy_summaries") or {}
    parts = []
    for name in [
        "p932_loo_token_rank_min2_reproduced",
        "p934_switch_rank_min1_control",
        "repeat2_switch_rank_min1",
        "repeat3_switch_rank_min1",
        "oracle_cost_ceiling_upper_bound",
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
