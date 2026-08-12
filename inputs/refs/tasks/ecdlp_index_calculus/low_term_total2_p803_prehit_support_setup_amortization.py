#!/usr/bin/env python3
"""P803 setup amortization audit for P802 pre-hit support pairs."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P802_PROBE = STATE_DIR / "low_term_total2_p802_prehit_support_pair_heldout_scaling_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p803_prehit_support_setup_amortization_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p803_prehit_support_setup_amortization.md"
SCHEMA = "ecdlp.low_term_total2_p803_prehit_support_setup_amortization.v1"
REQUESTED = "requested_support_prehit"
ROTATED = "rotated_support_prehit"
ALL_PAIR = "all_pair_first_hit_control"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(float(numerator) / float(denominator), 8)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def int_value(row: dict[str, Any], key: str) -> int:
    return int(row.get(key) or 0)


def group_once_sum(target_results: list[dict[str, Any]], key: str) -> int:
    values: dict[str, int] = {}
    for result in target_results:
        group_key = str(result.get("group_key"))
        aggregate = result["aggregate"]
        values[group_key] = max(values.get(group_key, 0), int_value(aggregate, key))
    return sum(values.values())


def cost_models(item: dict[str, Any], field_weight: int) -> dict[str, Any]:
    aggregate = item["aggregate"]
    target_results = item.get("target_results") or []
    recovered_rho = int_value(aggregate, "recovered_rho_baseline")
    generated_online = int_value(aggregate, "generated_online_group_additions")
    scoring_field = int_value(aggregate, "scoring_field_ops")
    conservative_total = int_value(aggregate, "generated_once_train_total_unit_cost")
    target_once_train_online = group_once_sum(target_results, "train_calibration_online_group_additions")
    target_once_train_field = group_once_sum(target_results, "train_calibration_field_ops")
    target_once_setup = group_once_sum(target_results, "targeted_setup_group_additions")
    online_after_setup_total = generated_online + int(field_weight) * scoring_field
    target_once_total = (
        generated_online
        + int(field_weight) * scoring_field
        + target_once_train_online
        + target_once_setup
        + int(field_weight) * target_once_train_field
    )
    return {
        "conservative_repeated": {
            "cost": conservative_total,
            "cost_over_recovered_rho": ratio(conservative_total, recovered_rho),
        },
        "online_after_setup": {
            "cost": online_after_setup_total,
            "cost_over_recovered_rho": ratio(online_after_setup_total, recovered_rho),
        },
        "target_once_setup": {
            "cost": target_once_total,
            "cost_over_recovered_rho": ratio(target_once_total, recovered_rho),
            "target_once_setup_group_additions": target_once_setup,
            "target_once_train_calibration_field_ops": target_once_train_field,
            "target_once_train_calibration_online_group_additions": target_once_train_online,
        },
    }


def enrich_grid_item(item: dict[str, Any], field_weight: int) -> dict[str, Any]:
    aggregate = item["aggregate"]
    return {
        "cost_models": cost_models(item, field_weight),
        "generated_row_count": int_value(aggregate, "generated_row_count"),
        "hit_row_count": int_value(aggregate, "hit_row_count"),
        "hit_row_rate_over_generated": aggregate.get("hit_row_rate_over_generated"),
        "max_control_recovered_row_count": int_value(aggregate, "max_control_recovered_row_count"),
        "policy": item["policy"],
        "policy_claim": item.get("policy_claim"),
        "recovered_rho_baseline": int_value(aggregate, "recovered_rho_baseline"),
        "recovered_row_count": int_value(aggregate, "recovered_row_count"),
        "support_budget": int(item["support_budget"]),
        "targeted_setup_group_additions": int_value(aggregate, "targeted_setup_group_additions"),
        "targeted_support_count": int_value(aggregate, "targeted_support_count"),
        "trial_budget": int(item["trial_budget"]),
    }


def best_by_model(items: list[dict[str, Any]], policy_name: str, model: str) -> dict[str, Any] | None:
    viable = [
        item
        for item in items
        if item["policy"]["name"] == policy_name
        and item["cost_models"][model]["cost_over_recovered_rho"] is not None
    ]
    if not viable:
        return None
    best = min(viable, key=lambda row: row["cost_models"][model]["cost_over_recovered_rho"])
    return compact_item(best, model)


def compact_item(item: dict[str, Any], model: str = "target_once_setup") -> dict[str, Any]:
    return {
        "cost": item["cost_models"][model]["cost"],
        "cost_over_recovered_rho": item["cost_models"][model]["cost_over_recovered_rho"],
        "generated_row_count": item["generated_row_count"],
        "hit_row_count": item["hit_row_count"],
        "hit_row_rate_over_generated": item["hit_row_rate_over_generated"],
        "policy": item["policy"]["name"],
        "recovered_row_count": item["recovered_row_count"],
        "recovered_rho_baseline": item["recovered_rho_baseline"],
        "support_budget": item["support_budget"],
        "targeted_support_count": item["targeted_support_count"],
        "trial_budget": item["trial_budget"],
    }


def peer_items(items: list[dict[str, Any]], support_budget: int, trial_budget: int) -> dict[str, dict[str, Any]]:
    return {
        item["policy"]["name"]: item
        for item in items
        if int(item["support_budget"]) == int(support_budget)
        and int(item["trial_budget"]) == int(trial_budget)
    }


def compression_summary(items: list[dict[str, Any]]) -> dict[str, Any]:
    requested = [item for item in items if item["policy"]["name"] == REQUESTED]
    max_recovered = max((item["recovered_row_count"] for item in requested), default=0)
    full_recovery = [item for item in requested if item["recovered_row_count"] == max_recovered]
    min_support = min((item["support_budget"] for item in full_recovery), default=None)
    best_full = min(
        full_recovery,
        key=lambda item: item["cost_models"]["target_once_setup"]["cost_over_recovered_rho"] or 10**18,
        default=None,
    )
    all_pair_peers = []
    if best_full is not None:
        peers = peer_items(items, best_full["support_budget"], best_full["trial_budget"])
        all_pair = peers.get(ALL_PAIR)
        if all_pair is not None:
            all_pair_peers.append(all_pair)
    best_full_setup = None if best_full is None else best_full["cost_models"]["target_once_setup"]["target_once_setup_group_additions"]
    all_pair_setup = None
    compression_factor = None
    if all_pair_peers:
        all_pair_setup = all_pair_peers[0]["cost_models"]["target_once_setup"]["target_once_setup_group_additions"]
        compression_factor = ratio(all_pair_setup, best_full_setup)
    return {
        "all_pair_target_once_setup_at_best_full_recovery": all_pair_setup,
        "best_full_recovery_requested": None if best_full is None else compact_item(best_full),
        "max_requested_recovered_row_count": max_recovered,
        "min_support_budget_preserving_max_recovery": min_support,
        "setup_compression_factor_vs_all_pair": compression_factor,
        "target_once_setup_at_best_full_recovery": best_full_setup,
    }


def model_claim(items: list[dict[str, Any]]) -> str:
    best_requested = best_by_model(items, REQUESTED, "target_once_setup")
    if best_requested is None:
        return "NEGATIVE_RESULT_P803_NO_REQUESTED_SUPPORT_ROWS"
    peers = peer_items(items, best_requested["support_budget"], best_requested["trial_budget"])
    rotated = peers.get(ROTATED)
    all_pair = peers.get(ALL_PAIR)
    peer_max = max(
        int(rotated["recovered_row_count"]) if rotated else 0,
        int(all_pair["recovered_row_count"]) if all_pair else 0,
    )
    if (
        best_requested["cost_over_recovered_rho"] is not None
        and best_requested["cost_over_recovered_rho"] < 1.0
        and best_requested["recovered_row_count"] > peer_max
    ):
        return "P803_TARGET_ONCE_SETUP_BELOW_RHO_SIGNAL"
    online_best = best_by_model(items, REQUESTED, "online_after_setup")
    if online_best and online_best["cost_over_recovered_rho"] is not None and online_best["cost_over_recovered_rho"] < 1.0:
        return "P803_ONLINE_AFTER_SETUP_BELOW_RHO_BOUNDARY"
    return "NEGATIVE_RESULT_P803_SETUP_AMORTIZATION_NO_BELOW_RHO"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p802 = load_json(args.p802_probe)
    field_weight = int(((p802.get("parameters") or {}).get("field_weight")) or args.field_weight)
    raw_items = (p802.get("summary") or {}).get("grid_results") or []
    items = [enrich_grid_item(item, field_weight) for item in raw_items]
    best_requested_target_once = best_by_model(items, REQUESTED, "target_once_setup")
    peers = {}
    if best_requested_target_once is not None:
        peers = peer_items(items, best_requested_target_once["support_budget"], best_requested_target_once["trial_budget"])
    summary = {
        "best_by_model": {
            "conservative_repeated": best_by_model(items, REQUESTED, "conservative_repeated"),
            "online_after_setup": best_by_model(items, REQUESTED, "online_after_setup"),
            "target_once_setup": best_requested_target_once,
        },
        "best_target_once_peers": {
            name: compact_item(item)
            for name, item in sorted(peers.items())
        },
        "compression": compression_summary(items),
        "field_weight": field_weight,
        "grid_results": items,
        "input_claim_status": p802.get("claim_status"),
    }
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p802_probe": str(args.p802_probe),
            "script": str(Path(__file__)),
        },
        "claim_status": model_claim(items),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness inherited from P802.",
            "POST-HOC COST AUDIT: P803 re-audits existing P802 rows; it does not add fresh constructor namespaces.",
            "TARGET-ONCE MODEL: training calibration and support point-sum setup are charged once per target across held-out namespaces.",
            "ONLINE-AFTER-SETUP is diagnostic and not a one-shot ECDLP claim by itself.",
            "NO DEPLOYED-CURVE CLAIM: no large-prime scaling, production-key relevance, or complete faster-than-rho ECDLP algorithm is implied.",
        ],
        "method": "p803_prehit_support_setup_amortization",
        "parameters": {
            "field_weight": field_weight,
        },
        "schema": SCHEMA,
        "summary": summary,
    }


def compact_summary(payload: dict[str, Any]) -> dict[str, Any]:
    grid_compact = []
    for item in payload["summary"]["grid_results"]:
        grid_compact.append(
            {
                "cost_models": item["cost_models"],
                "generated_row_count": item["generated_row_count"],
                "hit_row_count": item["hit_row_count"],
                "policy": item["policy"],
                "recovered_row_count": item["recovered_row_count"],
                "support_budget": item["support_budget"],
                "trial_budget": item["trial_budget"],
            }
        )
    return {
        **payload,
        "schema": f"{SCHEMA}.summary",
        "summary": {
            **payload["summary"],
            "grid_results": grid_compact,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p802-probe", type=Path, default=DEFAULT_P802_PROBE)
    parser.add_argument("--field-weight", type=int, default=2)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--summary-out", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    summary_out = args.summary_out or args.out.with_name(args.out.stem.replace("_probe", "_summary") + args.out.suffix)
    summary = compact_summary(payload)
    write_json(summary_out, summary)
    print(f"wrote {args.out}")
    print(f"wrote {summary_out}")
    print(
        json.dumps(
            {
                "best_by_model": summary["summary"]["best_by_model"],
                "claim_status": summary["claim_status"],
                "compression": summary["summary"]["compression"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
