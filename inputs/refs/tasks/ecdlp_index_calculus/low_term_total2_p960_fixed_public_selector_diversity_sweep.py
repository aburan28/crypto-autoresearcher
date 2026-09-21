#!/usr/bin/env python3
"""P960 fixed-public selector-diversity sweep."""

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


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p960_fixed_public_selector_diversity_sweep.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p960_fixed_public_selector_diversity_sweep_probe.json"
SCHEMA = "ecdlp.low_term_total2_p960_fixed_public_selector_diversity_sweep.v1"
DEFAULT_SELECTORS = ",".join(
    [
        "mode_low_term_span_perrow2",
        "mode_low_term_span_total6",
        "mode_low_term_support_perrow2",
        "mode_low_term_support_total6",
        "mode_hybrid_support_monic_b_perrow2",
    ]
)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def parse_csv(raw: str) -> list[str]:
    return [item.strip() for item in raw.split(",") if item.strip()]


def float_value(value: Any, default: float = 10**18) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def selector_args(args: argparse.Namespace, selector: str) -> argparse.Namespace:
    return argparse.Namespace(
        contract=args.contract,
        fixed_transfer=args.fixed_transfer,
        max_row_pairs=args.max_row_pairs,
        out=args.out,
        post_min=args.post_min,
        residue_modulus=args.residue_modulus,
        selector=selector,
        state_dir=args.state_dir,
        target=args.target,
        top_k=args.top_k,
    )


def compact_selector_result(payload: dict[str, Any]) -> dict[str, Any]:
    row_results = payload.get("row_pair_results") or []
    return {
        "accumulation": {
            "final_cumulative_ops_over_rho": (payload.get("accumulation") or {}).get("cumulative_ops_over_rho"),
            "final_rank": (payload.get("accumulation") or {}).get("final_rank"),
            "first_public_key_verified_at": (payload.get("accumulation") or {}).get("first_public_key_verified_at"),
            "first_rank_gt3_at": (payload.get("accumulation") or {}).get("first_rank_gt3_at"),
            "unique_form_count": (payload.get("accumulation") or {}).get("unique_form_count"),
        },
        "claim_status": payload.get("claim_status"),
        "parameters": payload.get("parameters") or {},
        "summary": payload.get("summary") or {},
        "top_row_pair_results": row_results[:8],
    }


def summarize(selector_results: list[dict[str, Any]]) -> dict[str, Any]:
    summaries = [row.get("summary") or {} for row in selector_results]
    best = max(
        selector_results,
        key=lambda row: (
            int_value((row.get("summary") or {}).get("final_rank")),
            int_value((row.get("summary") or {}).get("unique_form_count")),
            -float_value((row.get("summary") or {}).get("final_cumulative_ops_over_rho")),
        ),
        default={},
    )
    rank_gt3 = [
        row
        for row in selector_results
        if (row.get("summary") or {}).get("first_rank_gt3_at")
    ]
    below_rho_rank_gt3 = [
        row
        for row in rank_gt3
        if float_value(((row.get("summary") or {}).get("first_rank_gt3_at") or {}).get("cumulative_ops_over_rho"))
        <= 1.0
    ]
    claim = (
        "P960_SELECTOR_DIVERSITY_RANK_GT3_BELOW_RHO"
        if below_rho_rank_gt3
        else "P960_SELECTOR_DIVERSITY_RANK_GROWS_AFTER_RHO"
        if rank_gt3
        else "NEGATIVE_RESULT_P960_SELECTOR_DIVERSITY_NO_RANK_GT3"
    )
    return {
        "best_final_cumulative_ops_over_rho": (best.get("summary") or {}).get("final_cumulative_ops_over_rho"),
        "best_final_rank": (best.get("summary") or {}).get("final_rank"),
        "best_selector": (best.get("parameters") or {}).get("selector"),
        "best_unique_form_count": (best.get("summary") or {}).get("unique_form_count"),
        "claim_status": claim,
        "rank_gt3_below_rho_selector_count": len(below_rho_rank_gt3),
        "rank_gt3_selector_count": len(rank_gt3),
        "selector_count": len(selector_results),
        "selectors": [
            {
                "below_rho_row_pairs": summary.get("below_rho_row_pair_count"),
                "final_rank": summary.get("final_rank"),
                "final_ops_over_rho": summary.get("final_cumulative_ops_over_rho"),
                "first_rank_gt3_at": summary.get("first_rank_gt3_at"),
                "selector": (row.get("parameters") or {}).get("selector"),
                "unique_forms": summary.get("unique_form_count"),
                "verified_row_pairs": summary.get("verified_row_pair_count"),
            }
            for row, summary in zip(selector_results, summaries)
        ],
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    selector_results = []
    for selector in parse_csv(args.selectors):
        payload = p959.analyze(selector_args(args, selector))
        selector_results.append(compact_selector_result(payload))
    summary = summarize(selector_results)
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p959_script": str(Path(p959.__file__)),
            "script": str(Path(__file__)),
        },
        "claim_status": summary["claim_status"],
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "FIXED-PUBLIC: every selector is tested under the same fixed transfer challenge.",
            "PUBLIC-SELECTOR: leaves are recomputed under the fixed seed; archived leaf indices are not reused.",
            "COMPONENT-SIGNAL-NOT-END-TO-END: this is selector/rank-growth evidence, not deployed-curve complexity.",
        ],
        "method": "p960_fixed_public_selector_diversity_sweep",
        "parameters": {
            "fixed_transfer": int(args.fixed_transfer),
            "max_row_pairs": int(args.max_row_pairs),
            "post_min": int(args.post_min),
            "selectors": parse_csv(args.selectors),
            "target": args.target,
            "top_k": int(args.top_k),
        },
        "schema": SCHEMA,
        "selector_results": selector_results,
        "summary": summary,
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
    parser.add_argument("--max-row-pairs", type=int, default=0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    summary = payload["summary"]
    print(
        f"claim={payload['claim_status']} "
        f"selectors={summary['selector_count']} "
        f"best_selector={summary['best_selector']} "
        f"best_rank={summary['best_final_rank']} "
        f"best_unique_forms={summary['best_unique_form_count']} "
        f"rank_gt3={summary['rank_gt3_selector_count']} "
        f"rank_gt3_below_rho={summary['rank_gt3_below_rho_selector_count']} "
        f"out={args.out}"
    )


if __name__ == "__main__":
    main()
