#!/usr/bin/env python3
"""P885 no-retraining rank-companion widening of the P882 public gate."""

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
import low_term_total2_p883_p882_gate_no_retraining_replication as p883


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p885_p882_rank_companion_gate.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p885_p882_rank_companion_gate_probe.json"
DEFAULT_P842_SOURCE = STATE_DIR / "low_term_total2_p842_public_slice_motif_compression_audit_probe.json"
DEFAULT_P882_SOURCE = STATE_DIR / "low_term_total2_p882_public_post_motif_pairing_gate_probe.json"
DEFAULT_P884_SOURCE = STATE_DIR / "low_term_total2_p884_p882_gate_cap_sensitivity_probe.json"
DEFAULT_CALIBRATION_SOURCES = [
    STATE_DIR / "low_term_total2_expanded_leaf_rescue_472_487_summary.json",
]
DEFAULT_VALIDATION_SOURCES = [
    STATE_DIR / "low_term_total2_expanded_leaf_rescue_552_567_summary.json",
    STATE_DIR / "low_term_total2_expanded_leaf_rescue_568_583_summary.json",
    STATE_DIR / "low_term_total2_expanded_leaf_rescue_584_599_summary.json",
    STATE_DIR / "low_term_total2_expanded_leaf_rescue_600_615_summary.json",
    STATE_DIR / "low_term_total2_expanded_leaf_rescue_616_623_summary.json",
]
SCHEMA = "ecdlp.low_term_total2_p885_p882_rank_companion_gate.v1"


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


def p885_gate() -> dict[str, Any]:
    predicates = [
        {"kind": "target_eq", "value": "22050.cf1@11731"},
        {"kind": "fixed_value_eq", "value": 10907},
        {"kind": "leaf_contains", "value": 90},
        {"kind": "monomials_lte", "value": 38},
    ]
    return {
        "calibration": {
            "calibration_artifact": str(DEFAULT_P884_SOURCE),
            "missed_companion_row": "22050.cf1@11731:uniform:256:salt164",
            "missed_companion_selected_factor_monomials": 38,
            "p882_selected_row": "22050.cf1@11731:uniform:256:salt165",
            "transfer_index": 480,
        },
        "name": p882.gate_name(predicates),
        "predicates": predicates,
    }


def source_positive_counts(sources: list[Path]) -> list[dict[str, Any]]:
    return p883.source_positive_counts(sources)


def evaluate_sources(
    ps: Any,
    sources: list[Path],
    motif_set: dict[str, Any],
    max_cases_per_source: int,
    max_factor_degree: int,
) -> list[dict[str, Any]]:
    return [
        p881.evaluate_source(
            ps,
            source,
            motif_set,
            int(max_cases_per_source),
            int(max_factor_degree),
        )
        for source in sources
    ]


def rows_from_results(source_results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        row
        for result in source_results
        if not result.get("error")
        for row in result.get("recovered_rows") or []
        if not row.get("context_missing")
    ]


def gate_report(ps: Any, source_results: list[dict[str, Any]], gate: dict[str, Any]) -> dict[str, Any]:
    gated_results = p882.filter_source_results(source_results, gate)
    gated_contexts = p881.aggregate_contexts(ps, gated_results)
    gated_summary = p881.aggregate_metrics(gated_results, gated_contexts)
    return {
        "context_groups": gated_contexts,
        "gate": gate,
        "row_summary": p882.summarize_gate_rows(rows_from_results(gated_results)),
        "source_results": p881.strip_internal_source_results(gated_results),
        "summary": gated_summary,
    }


def baseline_report(ps: Any, source_results: list[dict[str, Any]]) -> dict[str, Any]:
    contexts = p881.aggregate_contexts(ps, source_results)
    return {
        "context_groups": contexts,
        "source_results": p881.strip_internal_source_results(source_results),
        "summary": p881.aggregate_metrics(source_results, contexts),
    }


def determine_claim(p885_summary: dict[str, Any], baseline_summary: dict[str, Any]) -> str:
    if int_value(p885_summary.get("motif_below_rho_verified_context_count")) > 0:
        return "P885_RANK_COMPANION_GATE_CLOSES_VALIDATION_CONTEXT_BELOW_RHO"
    if int_value(p885_summary.get("target_context_verified_count")) > 0:
        return "P885_RANK_COMPANION_GATE_SELECTS_VALIDATION_CLOSURE_ABOVE_MOTIF_COST"
    if int_value(p885_summary.get("matrix_rank_sum")) > 0:
        return "P885_RANK_COMPANION_GATE_SELECTS_VALIDATION_RANK_WITHOUT_CLOSURE"
    if int_value(p885_summary.get("recovered_row_count")) > 0:
        return "P885_RANK_COMPANION_GATE_SELECTS_VALIDATION_ROWS_WITHOUT_RANK"
    if int_value(baseline_summary.get("target_context_verified_count")) > 0:
        return "NEGATIVE_RESULT_P885_GATE_MISSES_BASELINE_VALIDATION_CLOSURE"
    if int_value(baseline_summary.get("recovered_row_count")) > 0:
        return "NEGATIVE_RESULT_P885_GATE_SELECTS_NO_VALIDATION_ROWS"
    return "NEGATIVE_RESULT_P885_NO_VALIDATION_MOTIF_RECOVERED_ROWS"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p842_payload = load_json(args.p842_source)
    p882_payload = load_json(args.p882_source)
    p884_payload = load_json(args.p884_source) if args.p884_source.exists() else None
    motif_set = p880.normalize_motif_set(p842_payload["selected_policy"]["motif_set"])
    ps = p842.load_module("ecdlp_public_slice_for_p885", p842.PUBLIC_SLICE_SCRIPT)

    calibration_sources = [Path(path) for path in (args.calibration_source or DEFAULT_CALIBRATION_SOURCES)]
    validation_sources = [Path(path) for path in (args.validation_source or DEFAULT_VALIDATION_SOURCES)]
    calibration_sources = calibration_sources[: int(args.max_calibration_sources)]
    validation_sources = validation_sources[: int(args.max_validation_sources)]

    calibration_results = evaluate_sources(
        ps,
        calibration_sources,
        motif_set,
        int(args.max_cases_per_source),
        int(args.max_factor_degree),
    )
    validation_results = evaluate_sources(
        ps,
        validation_sources,
        motif_set,
        int(args.max_cases_per_source),
        int(args.max_factor_degree),
    )

    exact_p882_gate = p882_payload["selected_gate"]
    rank_companion_gate = p885_gate()

    calibration_baseline = baseline_report(ps, calibration_results)
    validation_baseline = baseline_report(ps, validation_results)
    calibration_gates = {
        "p882_exact": gate_report(ps, calibration_results, exact_p882_gate),
        "p885_rank_companion_m38": gate_report(ps, calibration_results, rank_companion_gate),
    }
    validation_gates = {
        "p882_exact": gate_report(ps, validation_results, exact_p882_gate),
        "p885_rank_companion_m38": gate_report(ps, validation_results, rank_companion_gate),
    }
    p885_validation_summary = validation_gates["p885_rank_companion_m38"]["summary"]
    claim_status = determine_claim(p885_validation_summary, validation_baseline["summary"])

    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p842_source": str(args.p842_source),
            "p882_source": str(args.p882_source),
            "p884_source": str(args.p884_source),
            "script": str(Path(__file__)),
        },
        "calibration": {
            "baseline_all_recovered": calibration_baseline,
            "gate_reports": calibration_gates,
            "sources": source_positive_counts(calibration_sources),
        },
        "claim_status": claim_status,
        "created_at": now_iso(),
        "gate_derivation": {
            "exact_p882_gate": {
                "name": exact_p882_gate.get("name"),
                "predicates": exact_p882_gate.get("predicates") or [],
                "training_stats": exact_p882_gate.get("training_stats"),
            },
            "p884_claim_status": (p884_payload or {}).get("claim_status"),
            "p884_gated_summary": ((p884_payload or {}).get("gated") or {}).get("summary"),
            "rank_companion_gate": rank_companion_gate,
        },
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP FFE quotient harness only.",
            "NO-RETRAINING: the P885 threshold is fixed from P884 calibration before validation sources are scored.",
            "PUBLIC-FEATURE BOUNDARY: gate predicates use only public row/motif fields.",
            "SELECTED-ROW COST: motif ops/rho is not full public enumeration cost.",
            "POST-SELECTION VERIFIER AUDIT: verifier rank/closure is measured after selection.",
            "POLLARD-RHO BOUNDARY: this is not a complete general faster-than-rho ECDLP algorithm.",
        ],
        "method": "p885_p882_rank_companion_gate",
        "parameters": {
            "calibration_source_count": len(calibration_sources),
            "max_cases_per_source": int(args.max_cases_per_source),
            "max_factor_degree": int(args.max_factor_degree),
            "validation_source_count": len(validation_sources),
        },
        "red_team_handoff": {
            "assumptions": [
                "The monomial cap widening from 32 to 38 is fixed by P884 calibration and is not tuned on validation labels.",
                "Selecting both rank-positive rows in a compatible context is useful relation-selection evidence even if selected-row motif cost is above rho.",
                "Later validation sources are disjoint from the P884 calibration source.",
            ],
            "failure_modes": [
                "The widened cap may select only the known calibration closure and fail on later sources.",
                "It may select rank-positive singletons but miss independent companion forms.",
                "Even verifier-closed selected contexts may remain above rho under motif selected-row accounting.",
            ],
            "next_concrete_action": (
                "If P885 selects validation closures, add public companion scoring and full enumeration cost accounting; "
                "if it only selects rank, broaden the companion rule by transfer-local public row-pair features."
            ),
        },
        "schema": SCHEMA,
        "validation": {
            "baseline_all_recovered": validation_baseline,
            "gate_reports": validation_gates,
            "sources": source_positive_counts(validation_sources),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p842-source", type=Path, default=DEFAULT_P842_SOURCE)
    parser.add_argument("--p882-source", type=Path, default=DEFAULT_P882_SOURCE)
    parser.add_argument("--p884-source", type=Path, default=DEFAULT_P884_SOURCE)
    parser.add_argument("--calibration-source", type=Path, action="append")
    parser.add_argument("--validation-source", type=Path, action="append")
    parser.add_argument("--max-calibration-sources", type=int, default=len(DEFAULT_CALIBRATION_SOURCES))
    parser.add_argument("--max-validation-sources", type=int, default=len(DEFAULT_VALIDATION_SOURCES))
    parser.add_argument("--max-cases-per-source", type=int, default=0)
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
                "calibration": {
                    "baseline_summary": payload["calibration"]["baseline_all_recovered"]["summary"],
                    "p882_exact_summary": payload["calibration"]["gate_reports"]["p882_exact"]["summary"],
                    "p885_summary": payload["calibration"]["gate_reports"]["p885_rank_companion_m38"]["summary"],
                },
                "claim_status": payload["claim_status"],
                "parameters": payload["parameters"],
                "validation": {
                    "baseline_summary": payload["validation"]["baseline_all_recovered"]["summary"],
                    "p882_exact_summary": payload["validation"]["gate_reports"]["p882_exact"]["summary"],
                    "p885_summary": payload["validation"]["gate_reports"]["p885_rank_companion_m38"]["summary"],
                },
            },
            indent=2,
            sort_keys=True,
        )
    )
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
