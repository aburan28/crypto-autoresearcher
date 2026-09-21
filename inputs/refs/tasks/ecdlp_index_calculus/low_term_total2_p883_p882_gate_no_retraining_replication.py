#!/usr/bin/env python3
"""P883 no-retraining replication of the frozen P882 public gate."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p842_public_slice_motif_compression_audit as p842
import low_term_total2_p880_public_slice_motif_fresh_source_validation as p880
import low_term_total2_p881_public_slice_motif_rank_descent_audit as p881
import low_term_total2_p882_public_post_motif_pairing_gate as p882


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p883_p882_gate_no_retraining_replication.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p883_p882_gate_no_retraining_replication_probe.json"
DEFAULT_P842_SOURCE = STATE_DIR / "low_term_total2_p842_public_slice_motif_compression_audit_probe.json"
DEFAULT_P882_SOURCE = STATE_DIR / "low_term_total2_p882_public_post_motif_pairing_gate_probe.json"
DEFAULT_REPLICATION_SOURCES = [
    STATE_DIR / "low_term_total2_expanded_leaf_rescue_472_487_summary.json",
    STATE_DIR / "low_term_total2_expanded_leaf_rescue_488_503_summary.json",
    STATE_DIR / "low_term_total2_expanded_leaf_rescue_504_519_summary.json",
    STATE_DIR / "low_term_total2_expanded_leaf_rescue_520_535_summary.json",
    STATE_DIR / "low_term_total2_expanded_leaf_rescue_536_551_summary.json",
]
SCHEMA = "ecdlp.low_term_total2_p883_p882_gate_no_retraining_replication.v1"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def int_value(value: Any, default: int = 0) -> int:
    return p882.int_value(value, default)


def determine_claim(gated_summary: dict[str, Any], baseline_summary: dict[str, Any]) -> str:
    if int_value(gated_summary.get("recovered_row_count")) == 0:
        if int_value(baseline_summary.get("recovered_row_count")) > 0:
            return "NEGATIVE_RESULT_P883_FROZEN_P882_GATE_SELECTS_NO_ROWS"
        return "NEGATIVE_RESULT_P883_NO_REPLICATION_MOTIF_RECOVERED_ROWS"
    if int_value(gated_summary.get("motif_below_rho_verified_context_count")) > 0:
        return "P883_FROZEN_P882_GATE_REPLICATES_CONTEXT_CLOSURE_BELOW_RHO"
    if int_value(gated_summary.get("row_motif_below_rho_public_key_verified_count")) > 0:
        return "P883_FROZEN_P882_GATE_REPLICATES_ROW_CLOSURE_BELOW_RHO"
    if int_value(gated_summary.get("target_context_verified_count")) > 0:
        return "P883_FROZEN_P882_GATE_REPLICATES_CONTEXT_CLOSURE_ABOVE_MOTIF_COST"
    if int_value(gated_summary.get("matrix_rank_sum")) > 0:
        return "P883_FROZEN_P882_GATE_REPLICATES_RANK_WITHOUT_CLOSURE"
    return "NEGATIVE_RESULT_P883_FROZEN_P882_GATE_NO_REPLICATION_RANK"


def source_positive_counts(sources: list[Path]) -> list[dict[str, Any]]:
    out = []
    for source in sources:
        payload = load_json(source)
        cases = [case for case in payload.get("positive_cases") or [] if isinstance(case, dict)]
        transfers = [int_value(case.get("transfer_index")) for case in cases if case.get("transfer_index") is not None]
        out.append(
            {
                "path": str(source),
                "positive_case_count": len(cases),
                "transfer_range": [min(transfers), max(transfers)] if transfers else None,
            }
        )
    return out


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p842_payload = load_json(args.p842_source)
    p882_payload = load_json(args.p882_source)
    frozen_gate = p882_payload["selected_gate"]
    motif_set = p880.normalize_motif_set(p842_payload["selected_policy"]["motif_set"])
    ps = p842.load_module("ecdlp_public_slice_for_p883", p842.PUBLIC_SLICE_SCRIPT)
    sources = args.signature_source or DEFAULT_REPLICATION_SOURCES
    sources = [Path(path) for path in sources[: int(args.max_sources)]]

    replication_results = [
        p881.evaluate_source(
            ps,
            source,
            motif_set,
            int(args.max_cases_per_source),
            int(args.max_factor_degree),
        )
        for source in sources
    ]
    baseline_contexts = p881.aggregate_contexts(ps, replication_results)
    baseline_summary = p881.aggregate_metrics(replication_results, baseline_contexts)
    gated_results = p882.filter_source_results(replication_results, frozen_gate)
    gated_contexts = p881.aggregate_contexts(ps, gated_results)
    gated_summary = p881.aggregate_metrics(gated_results, gated_contexts)
    gated_rows = [
        row
        for result in gated_results
        if not result.get("error")
        for row in result.get("recovered_rows") or []
        if not row.get("context_missing")
    ]
    claim_status = determine_claim(gated_summary, baseline_summary)
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p842_source": str(args.p842_source),
            "p882_source": str(args.p882_source),
            "script": str(Path(__file__)),
        },
        "baseline_all_recovered": {
            "context_groups": baseline_contexts,
            "summary": baseline_summary,
        },
        "claim_status": claim_status,
        "created_at": now_iso(),
        "frozen_gate": {
            "name": frozen_gate.get("name"),
            "predicates": frozen_gate.get("predicates") or [],
            "p882_training_stats": frozen_gate.get("training_stats"),
        },
        "gated": {
            "context_groups": gated_contexts,
            "row_summary": p882.summarize_gate_rows(gated_rows),
            "source_results": p881.strip_internal_source_results(gated_results),
            "summary": gated_summary,
        },
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP FFE quotient harness only.",
            "NO-RETRAINING: the gate predicates are loaded from P882.",
            "SELECTED-ROW COST: motif ops/rho is not full public enumeration cost.",
            "POST-SELECTION VERIFIER AUDIT: verifier rank/closure is measured after selection.",
            "POLLARD-RHO BOUNDARY: this is not a complete general faster-than-rho ECDLP algorithm.",
        ],
        "method": "p883_p882_gate_no_retraining_replication",
        "parameters": {
            "max_cases_per_source": int(args.max_cases_per_source),
            "max_factor_degree": int(args.max_factor_degree),
            "replication_source_count": len(sources),
        },
        "red_team_handoff": {
            "assumptions": [
                "The P882 gate is frozen and not adapted to replication labels.",
                "Selected-row motif cost is useful for continuity with P880-P882 but not final full-cost accounting.",
                "Verifier closure after selection is evidence for relation quality, not a complete deployed-scale attack.",
            ],
            "failure_modes": [
                "The gate can select rank-positive rows without enough independent forms for public-key closure.",
                "The signal may be target-local to 22050.cf1@11731.",
                "Full public source enumeration may erase the selected-row below-rho margin.",
            ],
            "next_concrete_action": (
                "If P883 is closure-positive, build P884 full public-enumeration cost accounting for the frozen motif+gate; "
                "if not, broaden the gate using rank-positive labels and validate on later windows."
            ),
        },
        "replication_sources": source_positive_counts(sources),
        "schema": SCHEMA,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p842-source", type=Path, default=DEFAULT_P842_SOURCE)
    parser.add_argument("--p882-source", type=Path, default=DEFAULT_P882_SOURCE)
    parser.add_argument("--signature-source", type=Path, action="append")
    parser.add_argument("--max-sources", type=int, default=len(DEFAULT_REPLICATION_SOURCES))
    parser.add_argument("--max-cases-per-source", type=int, default=24)
    parser.add_argument("--max-factor-degree", type=int, default=1)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    print(
        json.dumps(
            {
                "baseline_summary": payload["baseline_all_recovered"]["summary"],
                "claim_status": payload["claim_status"],
                "frozen_gate": payload["frozen_gate"],
                "gated_summary": payload["gated"]["summary"],
                "parameters": payload["parameters"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
