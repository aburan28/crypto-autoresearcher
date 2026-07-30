#!/usr/bin/env python3
"""P962 fixed-public public-selector frontier."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
TASK_DIR = Path(__file__).resolve().parent
for candidate in (REPO_ROOT, TASK_DIR):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

import low_term_total2_p959_fixed_public_rematerialization_audit as p959  # noqa: E402
import low_term_total2_p961_fixed_public_hybrid_cost_squeeze as p961  # noqa: E402
import low_term_total2_public_prefix_shared_leaf_repair_probe as repair_probe  # noqa: E402


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p962_fixed_public_selector_frontier.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p962_fixed_public_selector_frontier_probe.json"
SCHEMA = "ecdlp.low_term_total2_p962_fixed_public_selector_frontier.v1"
DEFAULT_SELECTORS = ",".join(
    [
        "mode_hybrid_support_monic_b_perrow1",
        "mode_hybrid_support_monic_b_perrow2",
        "mode_hybrid_support_monic_b_perrow3",
        "mode_hybrid_support_monic_b_total2",
        "mode_hybrid_support_monic_b_total3",
        "mode_hybrid_support_monic_b_total4",
        "mode_hybrid_support_monic_b_total5",
        "mode_cost_hybrid_support_monic_b_total2",
        "mode_cost_hybrid_support_monic_b_total3",
        "mode_cost_hybrid_support_monic_b_total4",
        "mode_cost_hybrid_support_monic_b_total5",
        "mode_low_term_support_perrow1",
        "mode_low_term_support_perrow2",
        "mode_low_term_support_total2",
        "mode_low_term_support_total3",
        "mode_low_term_support_total4",
        "mode_low_term_support_total5",
        "mode_low_term_support_total6",
        "mode_cost_low_term_support_total2",
        "mode_cost_low_term_support_total3",
        "mode_cost_low_term_support_total4",
        "mode_cost_low_term_support_total5",
        "mode_low_term_span_perrow1",
        "mode_low_term_span_perrow2",
        "mode_low_term_span_total3",
        "mode_low_term_span_total4",
        "mode_low_term_span_total5",
        "mode_low_term_span_total6",
        "mode_double_pair_first_perrow2",
        "mode_double_pair_first_total4",
        "mode_cost_double_pair_first_total2",
        "mode_cost_double_pair_first_total3",
        "mode_cost_double_pair_first_total4",
        "mode_hybrid_double_monic_b_perrow2",
        "mode_low_monic_b_perrow2",
        "mode_low_monic_c_perrow2",
        "mode_hash_leaf_total4",
    ]
)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def parse_csv(raw: str) -> list[str]:
    return [item.strip() for item in raw.split(",") if item.strip()]


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def float_value(value: Any, default: float = 10**18) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def result_sort_key(row: dict[str, Any]) -> tuple[Any, ...]:
    return (
        not bool(row.get("public_key_verified")),
        -int_value(row.get("rank")),
        not bool(row.get("below_rho")),
        float_value(row.get("ops_over_rho")),
        -int_value(row.get("relation_count")),
        row.get("selector") or "",
        row.get("row_pair_key") or "",
    )


def compact_result(row: dict[str, Any], pair: dict[str, Any], selector: str, pair_index: int) -> dict[str, Any]:
    return {
        "below_rho": bool(row.get("below_rho")),
        "derived_secret": row.get("derived_secret"),
        "generic_rho_steps": row.get("generic_rho_steps"),
        "ops": row.get("ops"),
        "ops_over_rho": row.get("ops_over_rho"),
        "pair_index": pair_index,
        "public_key_verified": bool(row.get("public_key_verified")),
        "rank": row.get("rank"),
        "relation_count": row.get("relation_count"),
        "row_pair_key": "+".join(str(key).split(":")[-1] for key in pair.get("row_keys") or []),
        "row_results": row.get("row_results") or [],
        "row_keys": pair.get("row_keys") or [],
        "selected_leaf_count": row.get("selected_leaf_count"),
        "selected_row_count": row.get("selected_row_count"),
        "selector": selector,
        "source_support_count": int(pair.get("source_support_count") or 0),
        "unique_form_count": row.get("unique_form_count"),
    }


def summarize(results: list[dict[str, Any]], pair_count: int, selectors: list[str]) -> dict[str, Any]:
    verified_rank4 = [
        row
        for row in results
        if row.get("public_key_verified") and int_value(row.get("rank")) >= 4 and row.get("derived_secret") is not None
    ]
    verified_rank4_below = [row for row in verified_rank4 if row.get("below_rho")]
    below_verified_any_rank = [
        row
        for row in results
        if row.get("public_key_verified") and row.get("derived_secret") is not None and row.get("below_rho")
    ]
    best_verified_rank4 = sorted(verified_rank4, key=result_sort_key)[:1]
    best_below_verified = sorted(below_verified_any_rank, key=result_sort_key)[:1]
    claim = (
        "P962_PUBLIC_SELECTOR_FRONTIER_RANK4_BELOW_RHO"
        if verified_rank4_below
        else "P962_PUBLIC_SELECTOR_FRONTIER_RANK4_STILL_ABOVE_RHO"
        if verified_rank4
        else "NEGATIVE_RESULT_P962_PUBLIC_SELECTOR_FRONTIER_NO_RANK4"
    )
    selector_success_counts: dict[str, int] = {}
    for row in verified_rank4_below:
        selector = str(row.get("selector"))
        selector_success_counts[selector] = selector_success_counts.get(selector, 0) + 1
    return {
        "best_below_verified_any_rank": best_below_verified[0] if best_below_verified else None,
        "best_verified_rank4": best_verified_rank4[0] if best_verified_rank4 else None,
        "claim_status": claim,
        "pair_count": pair_count,
        "public_below_rho_verified_any_rank_count": len(below_verified_any_rank),
        "public_below_rho_verified_rank4_count": len(verified_rank4_below),
        "public_verified_rank4_count": len(verified_rank4),
        "result_count": len(results),
        "selector_count": len(selectors),
        "selector_rank4_below_counts": dict(sorted(selector_success_counts.items())),
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    cases, pairs = p959.source_row_pairs(Path(args.state_dir), int(args.post_min), args.target)
    if int(args.max_row_pairs) > 0:
        pairs = pairs[: int(args.max_row_pairs)]
    selectors = parse_csv(args.selectors)
    source_path = p959.choose_source(cases, int(args.fixed_transfer))
    source = p959.p957.load_json(source_path)
    params = repair_probe.source_parameters(source)
    verifier, records, config_source, specs_by_target = repair_probe.build_specs(params)
    results = []
    materialization_errors = []
    public_values = set()
    for pair_index, pair in enumerate(pairs):
        materialized = p961.build_materialized(verifier, records, config_source, specs_by_target, pair, source, args)
        for public in p961.public_values_for(materialized):
            public_values.add(tuple(int(value) for value in public))
        for error in materialized.get("errors") or []:
            materialization_errors.append({"pair_index": pair_index, "error": error, "row_keys": pair.get("row_keys") or []})
        for selector in selectors:
            try:
                result = p961.public_selector_result(
                    verifier,
                    materialized,
                    pair,
                    str(pair["target"]),
                    selector,
                    int(args.residue_modulus),
                )
            except Exception as exc:  # pragma: no cover - preserved in artifact for research triage
                materialization_errors.append(
                    {
                        "error": repr(exc),
                        "pair_index": pair_index,
                        "row_keys": pair.get("row_keys") or [],
                        "selector": selector,
                    }
                )
                continue
            results.append(compact_result(result, pair, selector, pair_index))
    results.sort(key=result_sort_key)
    summary = summarize(results, len(pairs), selectors)
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p961_script": str(Path(p961.__file__)),
            "script": str(Path(__file__)),
            "source": str(source_path),
        },
        "claim_status": summary["claim_status"],
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "FIXED-PUBLIC: all row pairs are rematerialized under one fixed transfer challenge.",
            "PUBLIC-SELECTOR: selector decisions use public leaf features and fixed caps only.",
            "COMPONENT-SIGNAL-NOT-END-TO-END: this is a fixed-public selector frontier, not full relation collection or target descent.",
        ],
        "materialization": {
            "errors": materialization_errors,
            "fixed_challenge_seed": f"{repair_probe.probe_args_from_source(source).seed}:shared-transfer:{int(args.fixed_transfer)}:{args.target}",
            "public_values": [list(value) for value in sorted(public_values)],
        },
        "method": "p962_fixed_public_selector_frontier",
        "parameters": {
            "fixed_transfer": int(args.fixed_transfer),
            "max_row_pairs": int(args.max_row_pairs),
            "post_min": int(args.post_min),
            "selectors": selectors,
            "target": args.target,
            "top_k": int(args.top_k),
        },
        "results": results,
        "schema": SCHEMA,
        "source_selected_case_count": len(cases),
        "summary": summary,
        "top_results": results[: int(args.top_result_limit)],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", type=Path, default=STATE_DIR)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--target", default=p959.p957.DEFAULT_TARGET)
    parser.add_argument("--post-min", type=int, default=p959.p957.DEFAULT_POST_MIN)
    parser.add_argument("--fixed-transfer", type=int, default=p959.DEFAULT_FIXED_TRANSFER)
    parser.add_argument("--selectors", default=DEFAULT_SELECTORS)
    parser.add_argument("--top-k", type=int, default=4)
    parser.add_argument("--residue-modulus", type=int, default=p959.DEFAULT_RESIDUE_MODULUS)
    parser.add_argument("--max-row-pairs", type=int, default=0, help="0 means all unique P957 row pairs")
    parser.add_argument("--top-result-limit", type=int, default=32)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    summary = payload["summary"]
    best = summary.get("best_verified_rank4") or {}
    print(
        f"claim={payload['claim_status']} "
        f"pairs={summary['pair_count']} "
        f"selectors={summary['selector_count']} "
        f"results={summary['result_count']} "
        f"verified_rank4={summary['public_verified_rank4_count']} "
        f"below_rank4={summary['public_below_rho_verified_rank4_count']} "
        f"below_verified_any={summary['public_below_rho_verified_any_rank_count']} "
        f"best_rank4_selector={best.get('selector')} "
        f"best_rank4_ops_over_rho={best.get('ops_over_rho')} "
        f"out={args.out}"
    )


if __name__ == "__main__":
    main()
