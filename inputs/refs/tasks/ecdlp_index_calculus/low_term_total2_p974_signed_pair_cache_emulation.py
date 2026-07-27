#!/usr/bin/env python3
"""P974 signed-pair/scout cache emulation."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p974_signed_pair_cache_emulation.md"
DEFAULT_P973 = STATE_DIR / "low_term_total2_p973_adjacent_source_charge_decomposition_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p974_signed_pair_cache_emulation_probe.json"
SCHEMA = "ecdlp.low_term_total2_p974_signed_pair_cache_emulation.v1"
COMPONENT_KEYS = [
    "selected_signed_pair_ops",
    "row_pool_prescan_ops",
    "product_leaf_ops",
    "selected_hit_root_ops",
    "selected_leaf_ops",
    "selected_hit_event_verification_ops",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


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


def component_totals(groups: list[dict[str, Any]]) -> dict[str, int]:
    totals = {component: 0 for component in COMPONENT_KEYS}
    for group in groups:
        breakdown = group.get("breakdown") or {}
        for component in COMPONENT_KEYS:
            totals[component] += int_value(breakdown.get(component))
    totals["total_ops"] = sum(totals[component] for component in COMPONENT_KEYS)
    totals["source_non_event_ops"] = totals["total_ops"] - totals["selected_hit_event_verification_ops"]
    return totals


def cache_plan(groups: list[dict[str, Any]], source_rho: int) -> dict[str, Any]:
    totals = component_totals(groups)
    charged_fingerprints: set[str] = set()
    rows = []
    cached_total = 0
    cached_component_totals = {component: 0 for component in COMPONENT_KEYS}
    cache_entries = []
    for group in groups:
        breakdown = group.get("breakdown") or {}
        fingerprint = str(group.get("scout_fingerprint") or "")
        signed_pair_ops = int_value(breakdown.get("selected_signed_pair_ops"))
        charge_signed_pair = fingerprint not in charged_fingerprints
        if charge_signed_pair:
            charged_fingerprints.add(fingerprint)
            cache_entries.append(
                {
                    "charged_ops": signed_pair_ops,
                    "fingerprint": fingerprint,
                    "row_short_first_charge": group.get("row_short"),
                    "selected_limit": breakdown.get("selected_limit"),
                }
            )
        row_specific = {
            component: int_value(breakdown.get(component))
            for component in COMPONENT_KEYS
            if component != "selected_signed_pair_ops"
        }
        cached_breakdown = {
            "selected_signed_pair_ops": signed_pair_ops if charge_signed_pair else 0,
            **row_specific,
        }
        cached_breakdown["total_ops"] = sum(cached_breakdown[component] for component in COMPONENT_KEYS)
        cached_breakdown["source_non_event_ops"] = (
            cached_breakdown["total_ops"] - cached_breakdown["selected_hit_event_verification_ops"]
        )
        for component in COMPONENT_KEYS:
            cached_component_totals[component] += cached_breakdown[component]
        cached_total += cached_breakdown["total_ops"]
        rows.append(
            {
                "added_signatures": group.get("added_signatures") or [],
                "cached_breakdown": cached_breakdown,
                "cache_hit": not charge_signed_pair,
                "cache_key": fingerprint,
                "original_breakdown": breakdown,
                "row_short": group.get("row_short"),
                "saved_signed_pair_ops": 0 if charge_signed_pair else signed_pair_ops,
            }
        )
    cached_component_totals["total_ops"] = cached_total
    cached_component_totals["source_non_event_ops"] = (
        cached_total - cached_component_totals["selected_hit_event_verification_ops"]
    )
    saved = totals["total_ops"] - cached_total
    return {
        "cache_entry_count": len(cache_entries),
        "cache_entries": cache_entries,
        "cached_component_totals": cached_component_totals,
        "cached_total_ops": cached_total,
        "cached_total_ops_below_source_rho": bool(cached_total < source_rho),
        "cached_total_ops_over_source_rho": round(cached_total / max(1, source_rho), 8),
        "cache_rows": rows,
        "fully_charged_component_totals": totals,
        "fully_charged_total_ops": totals["total_ops"],
        "source_rho": source_rho,
        "signed_pair_saved_ops": saved,
    }


def portfolio(name: str, groups: list[dict[str, Any]], candidate_count: int, source_rho: int) -> dict[str, Any]:
    plan = cache_plan(groups, source_rho)
    return {
        "amortized_cached_ops_per_candidate": round(plan["cached_total_ops"] / max(1, candidate_count), 8),
        "candidate_count": candidate_count,
        "group_count": len(groups),
        "name": name,
        **plan,
    }


def p973_positive_controls(p973: dict[str, Any]) -> dict[str, Any]:
    summary = p973.get("summary") or {}
    all_portfolio = summary.get("all_rank4_portfolio") or {}
    event_portfolio = summary.get("event_count_rank4_portfolio") or {}
    return {
        "all_signed_pair_bound_is_116": int_value(all_portfolio.get("signed_pair_reuse_total_ops")) == 116,
        "component_match_count_is_6": int_value(summary.get("component_match_count")) == 6,
        "event_signed_pair_bound_is_90": int_value(event_portfolio.get("signed_pair_reuse_total_ops")) == 90,
        "one_shot_signed_pair_below_is_0": int_value(summary.get("single_selected_signed_pair_reuse_below_rho_count")) == 0,
        "rank4_candidate_count_is_6": int_value(summary.get("rank4_candidate_count")) == 6,
        "scout_fingerprint_count_is_1": int_value(summary.get("scout_fingerprint_count")) == 1,
    }


def one_shot_controls(p973: dict[str, Any]) -> dict[str, Any]:
    rows = p973.get("rank4_candidate_breakdowns") or []
    signed_pair_below = [
        row
        for row in rows
        if (row.get("one_shot_after_selected_signed_pair_reuse") or {}).get("below_rho")
    ]
    full_cache_below = [
        row
        for row in rows
        if (row.get("one_shot_after_full_non_event_cache") or {}).get("below_rho")
    ]
    return {
        "full_non_event_cache_below_rho_count": len(full_cache_below),
        "full_non_event_cache_below_rho_signatures": [row.get("added_signature") for row in full_cache_below],
        "selected_signed_pair_cache_below_rho_count": len(signed_pair_below),
        "selected_signed_pair_cache_below_rho_signatures": [row.get("added_signature") for row in signed_pair_below],
    }


def summarize(
    controls: dict[str, Any],
    all_rank4: dict[str, Any],
    event_rank4: dict[str, Any],
    one_shot: dict[str, Any],
) -> dict[str, Any]:
    control_pass = all(bool(value) for value in controls.values())
    batch_pass = bool(all_rank4["cached_total_ops_below_source_rho"] and event_rank4["cached_total_ops_below_source_rho"])
    no_one_shot = int_value(one_shot.get("selected_signed_pair_cache_below_rho_count")) == 0
    claim = (
        "P974_SIGNED_PAIR_CACHE_EMULATION_BATCH_SOURCE_BELOW_RHO_NOT_ONE_SHOT"
        if control_pass and batch_pass and no_one_shot
        else "NEGATIVE_RESULT_P974_SIGNED_PAIR_CACHE_EMULATION_FAILS_CONTROLS"
        if not control_pass
        else "NEGATIVE_RESULT_P974_SIGNED_PAIR_CACHE_NOT_ENOUGH_FOR_BATCH_SOURCE_BOUND"
        if not batch_pass
        else "P974_SIGNED_PAIR_CACHE_EMULATION_ONE_SHOT_CANDIDATE_REQUIRES_VERIFIER_REPLAY"
    )
    return {
        "all_rank4_cached_total_ops": all_rank4["cached_total_ops"],
        "all_rank4_cached_total_ops_below_source_rho": all_rank4["cached_total_ops_below_source_rho"],
        "claim_status": claim,
        "event_rank4_cached_total_ops": event_rank4["cached_total_ops"],
        "event_rank4_cached_total_ops_below_source_rho": event_rank4["cached_total_ops_below_source_rho"],
        "full_non_event_cache_below_rho_count": one_shot["full_non_event_cache_below_rho_count"],
        "one_shot_signed_pair_cache_below_rho_count": one_shot["selected_signed_pair_cache_below_rho_count"],
        "positive_control_pass": control_pass,
        "signed_pair_cache_entry_count_all": all_rank4["cache_entry_count"],
        "signed_pair_cache_entry_count_event": event_rank4["cache_entry_count"],
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p973 = load_json(Path(args.p973))
    source_rho = int_value(((p973.get("summary") or {}).get("all_rank4_portfolio") or {}).get("source_rho"))
    if not source_rho:
        raise ValueError("P973 source rho missing")
    groups = p973.get("group_breakdowns") or {}
    all_groups = groups.get("all_rank4") or []
    event_groups = groups.get("event_count_ge4_rank4") or []
    all_candidate_count = int_value((p973.get("summary") or {}).get("rank4_candidate_count"))
    event_candidate_count = int_value(((p973.get("summary") or {}).get("event_count_rank4_portfolio") or {}).get("candidate_count"))
    controls = p973_positive_controls(p973)
    one_shot = one_shot_controls(p973)
    all_rank4 = portfolio("all_rank4", all_groups, all_candidate_count, source_rho)
    event_rank4 = portfolio("event_count_ge4_rank4", event_groups, event_candidate_count, source_rho)
    summary = summarize(controls, all_rank4, event_rank4, one_shot)
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p973_result": str(args.p973),
            "script": str(Path(__file__)),
        },
        "cache_model": "selected_signed_pair_scouts_charged_once_per_public_fingerprint",
        "claim_status": summary["claim_status"],
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "CACHE-EMULATION: this charges P973 component ledgers under a cache model; it is not a new verifier backend.",
            "ROW-SPECIFIC-COSTS-CHARGED: row-pool prescan, product leaf, hit-root, leaf, and candidate-event verification costs remain fully charged.",
            "BATCH-SOURCE-NOT-ONE-SHOT: below-rho source portfolios are batch source-generation bounds, not complete individual ECDLP solves.",
            "NO-SPARSE-LINALG-OR-TARGET-DESCENT: this does not perform matrix solving or individual logarithm descent.",
        ],
        "method": "p974_signed_pair_cache_emulation",
        "parameters": {
            "p973": str(args.p973),
            "source_rho": source_rho,
        },
        "portfolios": {
            "all_rank4": all_rank4,
            "event_count_ge4_rank4": event_rank4,
        },
        "positive_controls": controls,
        "schema": SCHEMA,
        "summary": summary,
        "one_shot_controls": one_shot,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--p973", type=Path, default=DEFAULT_P973)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    summary = payload["summary"]
    all_rank4 = payload["portfolios"]["all_rank4"]
    event_rank4 = payload["portfolios"]["event_count_ge4_rank4"]
    print(
        f"claim={payload['claim_status']} "
        f"controls={summary['positive_control_pass']} "
        f"all_cached_ops={summary['all_rank4_cached_total_ops']} "
        f"event_cached_ops={summary['event_rank4_cached_total_ops']} "
        f"all_cache_entries={summary['signed_pair_cache_entry_count_all']} "
        f"event_cache_entries={summary['signed_pair_cache_entry_count_event']} "
        f"all_amortized={all_rank4['amortized_cached_ops_per_candidate']} "
        f"event_amortized={event_rank4['amortized_cached_ops_per_candidate']} "
        f"one_shot_signed_pair_below={summary['one_shot_signed_pair_cache_below_rho_count']} "
        f"out={args.out}"
    )


if __name__ == "__main__":
    main()
