#!/usr/bin/env python3
"""P804 fresh validation for target-once setup support-pair pre-hit recovery."""

from __future__ import annotations

import argparse
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P802_SCRIPT = TASK_DIR / "low_term_total2_p802_prehit_support_pair_heldout_scaling.py"
P803_SCRIPT = TASK_DIR / "low_term_total2_p803_prehit_support_setup_amortization.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P777_SUMMARY = STATE_DIR / "low_term_total2_p777_merged_trim12_factor_first_cost_audit_summary.json"
DEFAULT_P786_SUMMARY = STATE_DIR / "low_term_total2_p786_public_coordinate_bridge_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p804_target_once_setup_fresh_validation_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p804_target_once_setup_fresh_validation.md"
DEFAULT_CONSTRUCTOR_NAMESPACES = "prehitpair-p804-fresh-v5,prehitpair-p804-fresh-v6,prehitpair-p804-fresh-v7"
SCHEMA = "ecdlp.low_term_total2_p804_target_once_setup_fresh_validation.v1"
REQUESTED = "requested_support_prehit"
ROTATED = "rotated_support_prehit"
ALL_PAIR = "all_pair_first_hit_control"


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


def int_value(row: dict[str, Any], key: str) -> int:
    return int(row.get(key) or 0)


def best_item_by_model(items: list[dict[str, Any]], policy_name: str, model: str) -> dict[str, Any] | None:
    viable = [
        item
        for item in items
        if item["policy"]["name"] == policy_name
        and item["cost_models"][model]["cost_over_recovered_rho"] is not None
    ]
    if not viable:
        return None
    return min(viable, key=lambda row: row["cost_models"][model]["cost_over_recovered_rho"])


def peer_items(items: list[dict[str, Any]], support_budget: int, trial_budget: int) -> dict[str, dict[str, Any]]:
    return {
        item["policy"]["name"]: item
        for item in items
        if int(item["support_budget"]) == int(support_budget)
        and int(item["trial_budget"]) == int(trial_budget)
    }


def compact_item(item: dict[str, Any] | None, model: str = "target_once_setup") -> dict[str, Any] | None:
    if item is None:
        return None
    cost_model = item["cost_models"][model]
    return {
        "cost": cost_model["cost"],
        "cost_over_recovered_rho": cost_model["cost_over_recovered_rho"],
        "generated_row_count": item["generated_row_count"],
        "hit_row_count": item["hit_row_count"],
        "hit_row_rate_over_generated": item["hit_row_rate_over_generated"],
        "max_control_recovered_row_count": item["max_control_recovered_row_count"],
        "policy": item["policy"]["name"],
        "recovered_rho_baseline": item["recovered_rho_baseline"],
        "recovered_row_count": item["recovered_row_count"],
        "support_budget": item["support_budget"],
        "targeted_support_count": item["targeted_support_count"],
        "trial_budget": item["trial_budget"],
    }


def compact_grid_item(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "cost_models": item["cost_models"],
        "generated_row_count": item["generated_row_count"],
        "hit_row_count": item["hit_row_count"],
        "hit_row_rate_over_generated": item["hit_row_rate_over_generated"],
        "max_control_recovered_row_count": item["max_control_recovered_row_count"],
        "policy": item["policy"],
        "policy_claim": item["policy_claim"],
        "recovered_rho_baseline": item["recovered_rho_baseline"],
        "recovered_row_count": item["recovered_row_count"],
        "support_budget": item["support_budget"],
        "targeted_setup_group_additions": item["targeted_setup_group_additions"],
        "targeted_support_count": item["targeted_support_count"],
        "trial_budget": item["trial_budget"],
    }


def compression_summary(items: list[dict[str, Any]]) -> dict[str, Any]:
    requested = [item for item in items if item["policy"]["name"] == REQUESTED]
    max_recovered = max((int(item["recovered_row_count"]) for item in requested), default=0)
    full_recovery = [item for item in requested if int(item["recovered_row_count"]) == max_recovered]
    min_support = min((int(item["support_budget"]) for item in full_recovery), default=None)
    best_full = min(
        full_recovery,
        key=lambda item: item["cost_models"]["target_once_setup"]["cost_over_recovered_rho"] or 10**18,
        default=None,
    )
    best_full_setup = None
    all_pair_setup = None
    compression_factor = None
    if best_full is not None:
        best_full_setup = best_full["cost_models"]["target_once_setup"]["target_once_setup_group_additions"]
        peers = peer_items(items, best_full["support_budget"], best_full["trial_budget"])
        all_pair = peers.get(ALL_PAIR)
        if all_pair is not None:
            all_pair_setup = all_pair["cost_models"]["target_once_setup"]["target_once_setup_group_additions"]
            compression_factor = ratio(all_pair_setup, best_full_setup)
    return {
        "all_pair_target_once_setup_at_best_full_recovery": all_pair_setup,
        "best_full_recovery_requested": compact_item(best_full),
        "max_requested_recovered_row_count": max_recovered,
        "min_support_budget_preserving_max_recovery": min_support,
        "setup_compression_factor_vs_all_pair": compression_factor,
        "target_once_setup_at_best_full_recovery": best_full_setup,
    }


def determine_claim(items: list[dict[str, Any]]) -> str:
    best_requested = best_item_by_model(items, REQUESTED, "target_once_setup")
    if best_requested is None:
        return "NEGATIVE_RESULT_P804_NO_REQUESTED_SUPPORT_ROWS"
    peers = peer_items(items, best_requested["support_budget"], best_requested["trial_budget"])
    rotated = peers.get(ROTATED)
    all_pair = peers.get(ALL_PAIR)
    peer_max = max(
        int(rotated["recovered_row_count"]) if rotated else 0,
        int(all_pair["recovered_row_count"]) if all_pair else 0,
    )
    line_control = int(best_requested.get("max_control_recovered_row_count") or 0)
    best_ratio = best_requested["cost_models"]["target_once_setup"]["cost_over_recovered_rho"]
    if (
        best_ratio is not None
        and best_ratio < 1.0
        and int(best_requested["recovered_row_count"]) > peer_max
        and int(best_requested["recovered_row_count"]) > line_control
    ):
        return "P804_FRESH_TARGET_ONCE_SETUP_BELOW_RHO_REPLICATES"
    online_best = best_item_by_model(items, REQUESTED, "online_after_setup")
    online_ratio = None if online_best is None else online_best["cost_models"]["online_after_setup"]["cost_over_recovered_rho"]
    if online_ratio is not None and online_ratio < 1.0:
        return "P804_FRESH_ONLINE_AFTER_SETUP_BELOW_RHO_BOUNDARY"
    return "NEGATIVE_RESULT_P804_FRESH_TARGET_ONCE_SETUP_NO_BELOW_RHO"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p802 = load_module("ecdlp_p802_for_p804", P802_SCRIPT)
    p803 = load_module("ecdlp_p803_for_p804", P803_SCRIPT)
    fresh_payload = p802.analyze(args)
    field_weight = int(((fresh_payload.get("parameters") or {}).get("field_weight")) or args.field_weight)
    raw_grid = (fresh_payload.get("summary") or {}).get("grid_results") or []
    enriched_items = [p803.enrich_grid_item(item, field_weight) for item in raw_grid]
    best_requested = best_item_by_model(enriched_items, REQUESTED, "target_once_setup")
    best_peers = {}
    if best_requested is not None:
        best_peers = peer_items(enriched_items, best_requested["support_budget"], best_requested["trial_budget"])
    summary = {
        "best_by_model": {
            "conservative_repeated": compact_item(best_item_by_model(enriched_items, REQUESTED, "conservative_repeated"), "conservative_repeated"),
            "online_after_setup": compact_item(best_item_by_model(enriched_items, REQUESTED, "online_after_setup"), "online_after_setup"),
            "target_once_setup": compact_item(best_requested, "target_once_setup"),
        },
        "best_target_once_peers": {
            name: compact_item(item, "target_once_setup")
            for name, item in sorted(best_peers.items())
        },
        "compression": compression_summary(enriched_items),
        "constructor_namespaces": csv_strings(args.constructor_namespaces),
        "field_weight": field_weight,
        "fresh_scan_claim_status": fresh_payload.get("claim_status"),
        "grid_results": enriched_items,
        "monotonicity": (fresh_payload.get("summary") or {}).get("monotonicity"),
        "scan_seed_count": args.scan_seed_count,
        "support_budgets": csv_ints(args.support_budgets),
        "train_seed_namespace": args.train_seed_namespace,
        "trial_budgets": csv_ints(args.trial_budgets),
    }
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p777_summary": str(args.p777_summary),
            "p786_summary": str(args.p786_summary),
            "p802_script": str(P802_SCRIPT),
            "p803_script": str(P803_SCRIPT),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(enriched_items),
        "created_at": now_iso(),
        "fresh_scan": fresh_payload,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "FRESH PROTOCOL: constructor namespaces and challenge seeds are generated by P804, not loaded from the P802 artifact.",
            "TARGET-ONCE MODEL: training calibration and support point-sum setup are charged once per target across fresh held-out namespaces.",
            "CONTROL-BOUND: rotated support-pair and all-pair controls must remain below requested recovery at the selected grid.",
            "NO DEPLOYED-CURVE CLAIM: no large-prime scaling, production-key relevance, or complete faster-than-rho ECDLP algorithm is implied.",
        ],
        "method": "p804_target_once_setup_fresh_validation",
        "parameters": {
            "constructor_namespaces": csv_strings(args.constructor_namespaces),
            "control_count": args.control_count,
            "field_weight": args.field_weight,
            "max_relations": args.max_relations,
            "max_subsets": args.max_subsets,
            "min_line_rows": args.min_line_rows,
            "row_policy": args.row_policy,
            "scan_seed_count": args.scan_seed_count,
            "sparse_policies": args.sparse_policies,
            "support_budgets": csv_ints(args.support_budgets),
            "train_replicas": args.train_replicas,
            "train_seed_namespace": args.train_seed_namespace,
            "trial_budgets": csv_ints(args.trial_budgets),
            "walk_mode": args.walk_mode,
            "width": args.width,
        },
        "schema": SCHEMA,
        "summary": summary,
    }


def summary_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        **{key: value for key, value in payload.items() if key != "fresh_scan"},
        "schema": f"{SCHEMA}.summary",
        "summary": {
            **payload["summary"],
            "grid_results": [compact_grid_item(item) for item in payload["summary"]["grid_results"]],
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p777-summary", type=Path, default=DEFAULT_P777_SUMMARY)
    parser.add_argument("--p786-summary", type=Path, default=DEFAULT_P786_SUMMARY)
    parser.add_argument("--train-seed-namespace", default="supportline20-v1")
    parser.add_argument("--constructor-namespaces", default=DEFAULT_CONSTRUCTOR_NAMESPACES)
    parser.add_argument("--support-budgets", default="128,256,512")
    parser.add_argument("--trial-budgets", default="128,256,512")
    parser.add_argument("--train-replicas", type=int, default=20)
    parser.add_argument("--scan-seed-count", type=int, default=128)
    parser.add_argument("--control-count", type=int, default=8)
    parser.add_argument("--field-weight", type=int, default=2)
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
                "best_by_model": summary["summary"]["best_by_model"],
                "claim_status": summary["claim_status"],
                "compression": summary["summary"]["compression"],
                "fresh_scan_claim_status": summary["summary"]["fresh_scan_claim_status"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
