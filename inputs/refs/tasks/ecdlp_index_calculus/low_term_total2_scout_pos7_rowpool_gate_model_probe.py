#!/usr/bin/env python3
"""Re-account row-pool gate models for the direct leaf-65 scout-7 kernel.

The direct leaf-65 probe showed a constructive below-rho ledger, but charging
row-pool setup for every context pushed validation just above rho.  This probe
does not claim a new implementation.  It quantifies the exact pre-row-pool gate
needed by recharging the same accepted stream under explicit gate models:

* current_all_context_rowpool: the existing row-pool charged leaf-65 model;
* selected_root_context_rowpool: charge row-pool only when leaf 65 has a
  selected row-side root hit;
* selected_root_attempt_once_rowpool: charge at most one row-pool op per source
  attempt if either row context has a selected root hit;
* affine_match_context_rowpool: a post-affine lower-bound diagnostic, invalid
  as a pre-row-pool gate.

This is a work-order probe for a measured source generator or algebraic
root-hit test, not a completed speedup.
"""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


MODELS = (
    "constructive_leaf65_kernel",
    "current_all_context_rowpool",
    "selected_root_context_rowpool",
    "selected_root_attempt_once_rowpool",
    "affine_match_context_rowpool_lower_bound",
)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(float(numerator) / float(denominator), 8)


def context_rowpool_sum(contexts: list[dict[str, Any]], predicate: str) -> int:
    total = 0
    for context in contexts:
        if predicate == "all":
            total += int_value(context.get("row_pool_ops"))
        elif predicate == "selected_root" and int_value(context.get("selected_hit_roots")) > 0:
            total += int_value(context.get("row_pool_ops"))
        elif predicate == "affine_match" and int_value(context.get("affine_match_count")) > 0:
            total += int_value(context.get("row_pool_ops"))
    return total


def attempt_model_ops(attempt: dict[str, Any]) -> dict[str, int]:
    contexts = [row for row in attempt.get("context_rows") or [] if isinstance(row, dict)]
    constructive = int_value((attempt.get("model_ops") or {}).get("constructive_leaf65_kernel"))
    all_rowpool = context_rowpool_sum(contexts, "all")
    selected_root_rowpool = context_rowpool_sum(contexts, "selected_root")
    affine_rowpool = context_rowpool_sum(contexts, "affine_match")
    root_attempt_once = 1 if any(int_value(row.get("selected_hit_roots")) > 0 for row in contexts) else 0
    return {
        "affine_match_context_rowpool_lower_bound": constructive + affine_rowpool,
        "constructive_leaf65_kernel": constructive,
        "current_all_context_rowpool": constructive + all_rowpool,
        "selected_root_attempt_once_rowpool": constructive + root_attempt_once,
        "selected_root_context_rowpool": constructive + selected_root_rowpool,
    }


def recharge_group(group: dict[str, Any]) -> dict[str, Any]:
    attempts: list[dict[str, Any]] = []
    model_ops = {model: 0 for model in MODELS}
    for attempt in group.get("attempts") or []:
        if not isinstance(attempt, dict):
            continue
        charged = attempt_model_ops(attempt)
        for model, ops in charged.items():
            model_ops[model] += int(ops)
        attempts.append(
            {
                "accepted": bool(attempt.get("accepted")),
                "model_ops": charged,
                "rank_gain": attempt.get("rank_gain"),
                "root_context_count": sum(
                    1 for row in attempt.get("context_rows") or [] if int_value(row.get("selected_hit_roots")) > 0
                ),
                "affine_match_context_count": sum(
                    1 for row in attempt.get("context_rows") or [] if int_value(row.get("affine_match_count")) > 0
                ),
                "row_context_count": len(attempt.get("context_rows") or []),
                "transfer_index": int_value(attempt.get("transfer_index")),
            }
        )
    rho = int_value(group.get("rho"))
    return {
        "attempt_count": len(attempts),
        "attempts": attempts,
        "has_accepted_stop": bool(group.get("has_accepted_stop")),
        "has_rank_gain_stop": bool(group.get("has_rank_gain_stop")),
        "model_ops": model_ops,
        "model_ops_over_rho": {model: ratio(ops, rho) for model, ops in model_ops.items()},
        "rho": rho,
        "source_path": group.get("source_path"),
        "stop_transfer_index": int_value((group.get("stop") or {}).get("transfer_index")),
        "window": group.get("window"),
        "window_start": int_value(group.get("window_start")),
    }


def split_groups(groups: list[dict[str, Any]], calibration_end: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    return (
        [group for group in groups if int_value(group.get("window_start")) <= calibration_end],
        [group for group in groups if int_value(group.get("window_start")) > calibration_end],
    )


def summarize(groups: list[dict[str, Any]]) -> dict[str, Any]:
    accepted = [group for group in groups if group.get("has_accepted_stop")]
    rank_hits = [group for group in groups if group.get("has_rank_gain_stop")]
    false_accepts = [group for group in accepted if not group.get("has_rank_gain_stop")]
    rho = max([int_value(group.get("rho")) for group in groups if int_value(group.get("rho")) > 0] or [0])
    model_summaries: dict[str, Any] = {}
    current_ops = sum(int_value(group.get("model_ops", {}).get("current_all_context_rowpool")) for group in groups)
    for model in MODELS:
        ops = sum(int_value(group.get("model_ops", {}).get(model)) for group in groups)
        model_summaries[model] = {
            "cost_per_rank_gain_stop_over_rho": ratio(ops, rho * len(rank_hits)) if rank_hits and rho else None,
            "ops": ops,
            "ops_over_rho": ratio(ops, rho),
            "ops_saved_vs_current": current_ops - ops,
            "saved_fraction_vs_current": ratio(current_ops - ops, current_ops) if current_ops else None,
        }
    return {
        "accepted_stop_count": len(accepted),
        "attempt_count": sum(int_value(group.get("attempt_count")) for group in groups),
        "false_accept_count": len(false_accepts),
        "group_count": len(groups),
        "model_summaries": model_summaries,
        "precision": ratio(len(rank_hits), len(accepted)) if accepted else None,
        "rank_gain_stop_count": len(rank_hits),
        "stop_transfers": [int_value(group.get("stop_transfer_index")) for group in accepted],
    }


def claim_status(validation_summary: dict[str, Any]) -> str:
    rank_hits = int_value(validation_summary.get("rank_gain_stop_count"))
    if rank_hits <= 0:
        return "SCOUT_POS7_ROWPOOL_GATE_MODEL_MISSES_VALIDATION"
    models = validation_summary.get("model_summaries") if isinstance(validation_summary.get("model_summaries"), dict) else {}
    current = (models.get("current_all_context_rowpool") or {}).get("cost_per_rank_gain_stop_over_rho")
    root_gate = (models.get("selected_root_context_rowpool") or {}).get("cost_per_rank_gain_stop_over_rho")
    attempt_gate = (models.get("selected_root_attempt_once_rowpool") or {}).get("cost_per_rank_gain_stop_over_rho")
    if current is not None and float(current) < 1.0:
        return "SCOUT_POS7_ROWPOOL_GATE_MODEL_CURRENT_ALREADY_BELOW_RHO"
    if root_gate is not None and float(root_gate) < 1.0:
        return "SCOUT_POS7_ROWPOOL_GATE_MODEL_SELECTED_ROOT_GATE_BELOW_RHO_WORK_ORDER"
    if attempt_gate is not None and float(attempt_gate) < 1.0:
        return "SCOUT_POS7_ROWPOOL_GATE_MODEL_ATTEMPT_ROOT_GATE_BELOW_RHO_WORK_ORDER"
    return "SCOUT_POS7_ROWPOOL_GATE_MODEL_ROOT_GATE_STILL_ABOVE_RHO"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--direct-kernel", required=True)
    parser.add_argument("--calibration-end", type=int, default=4064)
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    direct_path = Path(args.direct_kernel)
    direct = load_json(direct_path)
    groups = [recharge_group(group) for group in direct.get("groups") or [] if isinstance(group, dict)]
    calibration, validation = split_groups(groups, args.calibration_end)
    summary = {
        "calibration": summarize(calibration),
        "validation": summarize(validation),
    }
    payload = {
        "artifacts": {
            "direct_kernel": str(direct_path),
        },
        "claim_status": claim_status(summary["validation"]),
        "created_at": now_iso(),
        "gate_model_definitions": {
            "affine_match_context_rowpool_lower_bound": "Charges row-pool only for contexts with affine candidate equality; invalid as a pre-row-pool gate because affine equality is known after candidate testing.",
            "constructive_leaf65_kernel": "Original constructive branch ledger from the direct kernel artifact; omits row-pool setup.",
            "current_all_context_rowpool": "Constructive ledger plus one row-pool charge for every context; reproduces current rowpool_charged_leaf65_kernel.",
            "selected_root_attempt_once_rowpool": "Constructive ledger plus at most one row-pool charge per attempted source case if any row context has a selected leaf-65 root hit.",
            "selected_root_context_rowpool": "Constructive ledger plus row-pool charge only for contexts where leaf 65 has at least one selected row-side root hit.",
        },
        "groups": groups,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: this reuses the direct leaf-65 artifact and does not implement the pre-row-pool root-hit test.",
            "The selected-root gate is a source-generator/algebraic-test work order; it is not a measured implementation.",
            "The affine-match gate is a post-candidate lower bound and cannot be used as a pre-row-pool claim.",
        ],
        "parameters": {
            "calibration_end": args.calibration_end,
        },
        "schema": "ecdlp.low_term_total2_scout_pos7_rowpool_gate_model_probe.v1",
        "summary": summary,
    }
    write_json(Path(args.out), payload)
    print(
        json.dumps(
            {
                "claim_status": payload["claim_status"],
                "summary": payload["summary"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
