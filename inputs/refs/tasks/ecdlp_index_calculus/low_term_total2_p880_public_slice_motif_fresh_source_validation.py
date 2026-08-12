#!/usr/bin/env python3
"""P880 fresh-source validation for the P842 public slice motif.

P842 found a small exact-factor motif that preserved heldout selected roots below
rho on the original low-term total-2 signature source.  This script freezes that
motif and applies it to later expanded leaf-rescue signature summaries.
"""

from __future__ import annotations

import argparse
import json
import traceback
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any

import low_term_total2_p842_public_slice_motif_compression_audit as p842


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P842_SOURCE = STATE_DIR / "low_term_total2_p842_public_slice_motif_compression_audit_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p880_public_slice_motif_fresh_source_validation_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p880_public_slice_motif_fresh_source_validation.md"
DEFAULT_FRESH_SOURCES = [
    STATE_DIR / "low_term_total2_expanded_leaf_rescue_232_247_summary.json",
    STATE_DIR / "low_term_total2_expanded_leaf_rescue_248_263_summary.json",
    STATE_DIR / "low_term_total2_expanded_leaf_rescue_264_279_summary.json",
    STATE_DIR / "low_term_total2_expanded_leaf_rescue_280_295_summary.json",
    STATE_DIR / "low_term_total2_expanded_leaf_rescue_296_311_summary.json",
]
SCHEMA = "ecdlp.low_term_total2_p880_public_slice_motif_fresh_source_validation.v1"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(float(numerator) / float(denominator), 8)


def extended_metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    base = p842.metrics_for(rows)
    selections = [row["selection"] for row in rows]
    chosen_nonzero = [item for item in selections if int(item.get("chosen_count") or 0) > 0]
    preserving_nonzero = [
        item
        for item in chosen_nonzero
        if item.get("preserves_selected_root_pairs")
    ]
    preserving_below_nonzero = [
        item
        for item in preserving_nonzero
        if item.get("public_slice_motif_beats_rho")
    ]
    preserving_below_recovered = [
        item
        for item in preserving_below_nonzero
        if int(item.get("original_selected_root_pair_count") or 0) > 0
        and int(item.get("selected_root_pair_count") or 0) > 0
    ]
    ratios = [
        float(item["public_slice_motif_ops_over_rho"])
        for item in preserving_below_nonzero
        if item.get("public_slice_motif_ops_over_rho") is not None
    ]
    recovered_ratios = [
        float(item["public_slice_motif_ops_over_rho"])
        for item in preserving_below_recovered
        if item.get("public_slice_motif_ops_over_rho") is not None
    ]
    base.update(
        {
            "chosen_nonzero_count": len(chosen_nonzero),
            "chosen_nonzero_rate": ratio(len(chosen_nonzero), len(selections)),
            "preserving_below_rho_nonzero_count": len(preserving_below_nonzero),
            "preserving_below_rho_recovered_count": len(preserving_below_recovered),
            "preserving_below_rho_recovered_mean_ops_over_rho": round(mean(recovered_ratios), 8)
            if recovered_ratios
            else None,
            "preserving_below_rho_recovered_min_ops_over_rho": round(min(recovered_ratios), 8)
            if recovered_ratios
            else None,
            "preserving_below_rho_recovered_max_ops_over_rho": round(max(recovered_ratios), 8)
            if recovered_ratios
            else None,
            "preserving_nonzero_count": len(preserving_nonzero),
            "preserving_nonzero_rate": ratio(len(preserving_nonzero), len(selections)),
            "preserving_below_rho_nonzero_mean_ops_over_rho": round(mean(ratios), 8) if ratios else None,
            "preserving_below_rho_nonzero_min_ops_over_rho": round(min(ratios), 8) if ratios else None,
            "preserving_below_rho_nonzero_max_ops_over_rho": round(max(ratios), 8) if ratios else None,
            "total_chosen_slices": sum(int(item.get("chosen_count") or 0) for item in selections),
        }
    )
    return base


def source_summary(path: Path) -> dict[str, Any]:
    payload = load_json(path)
    positives = [case for case in payload.get("positive_cases") or [] if isinstance(case, dict)]
    transfers = [
        int(case["transfer_index"])
        for case in positives
        if isinstance(case.get("transfer_index"), int)
    ]
    return {
        "path": str(path),
        "positive_case_count": len(positives),
        "schema": payload.get("schema"),
        "source": payload.get("source"),
        "transfer_range": [min(transfers), max(transfers)] if transfers else None,
    }


def deep_tuple(value: Any) -> Any:
    if isinstance(value, list):
        return tuple(deep_tuple(item) for item in value)
    return value


def normalize_motif_set(motif_set: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(motif_set)
    normalized["motifs"] = [deep_tuple(value) for value in motif_set.get("motifs") or []]
    return normalized


def compact_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    compacted = []
    for row in rows:
        selection = row["selection"]
        compacted.append(
            {
                "row_key": row.get("row_key"),
                "surface_id": row.get("surface_id"),
                "target": row.get("target"),
                "transfer_index": row.get("transfer_index"),
                "selection": {
                    "chosen_count": selection.get("chosen_count"),
                    "missing_selected_root_pairs": selection.get("missing_selected_root_pairs"),
                    "motif_policy": selection.get("motif_policy"),
                    "original_selected_root_pair_count": selection.get("original_selected_root_pair_count"),
                    "preserves_selected_root_pairs": selection.get("preserves_selected_root_pairs"),
                    "public_slice_motif_beats_rho": selection.get("public_slice_motif_beats_rho"),
                    "public_slice_motif_ops": selection.get("public_slice_motif_ops"),
                    "public_slice_motif_ops_over_rho": selection.get("public_slice_motif_ops_over_rho"),
                    "recovered_root_count": selection.get("recovered_root_count"),
                    "selected_root_pair_count": selection.get("selected_root_pair_count"),
                    "chosen_slices": selection.get("chosen_slices"),
                },
            }
        )
    return compacted


def evaluate_source(
    ps: Any,
    source_path: Path,
    motif_set: dict[str, Any],
    max_cases_per_source: int,
    max_factor_degree: int,
) -> dict[str, Any]:
    ps_args = p842.public_slice_args(ps)
    ps_args.signature_source = source_path
    ps_args.max_cases = int(max_cases_per_source)
    ps_args.max_factor_degree = int(max_factor_degree)
    source_info = source_summary(source_path)

    print(f"materializing {source_path} max_cases={ps_args.max_cases}", flush=True)
    try:
        surface_records, case_results = p842.materialize_surface_records(ps, ps_args)
        surface_records = [
            record
            for record in surface_records
            if isinstance(record, dict) and record.get("surface_id")
        ]
        records_by_id = {str(record["surface_id"]): record for record in surface_records}
        surface_ids = sorted(
            records_by_id,
            key=lambda surface_id: (
                p842.transfer_index(records_by_id[surface_id]),
                str(records_by_id[surface_id].get("target")),
                surface_id,
            ),
        )
        candidates_by_id = {
            surface_id: ps.build_public_candidates(records_by_id[surface_id], int(max_factor_degree))
            for surface_id in surface_ids
        }
        rows = p842.evaluate_motif_policy(ps, records_by_id, candidates_by_id, motif_set, surface_ids)
        metrics = extended_metrics(rows)
        return {
            "case_result_count": len(case_results or []),
            "error": None,
            "metrics": metrics,
            "rows": compact_rows(rows),
            "source": source_info,
            "surface_count": len(surface_ids),
            "transfer_range": [
                min(p842.transfer_index(records_by_id[surface_id]) for surface_id in surface_ids),
                max(p842.transfer_index(records_by_id[surface_id]) for surface_id in surface_ids),
            ]
            if surface_ids
            else None,
        }
    except Exception as exc:  # noqa: BLE001 - recorded as experiment evidence.
        return {
            "case_result_count": 0,
            "error": f"{type(exc).__name__}: {exc}",
            "error_traceback": traceback.format_exc().splitlines(),
            "metrics": extended_metrics([]),
            "rows": [],
            "source": source_info,
            "surface_count": 0,
            "transfer_range": None,
        }


def aggregate_metrics(source_results: list[dict[str, Any]]) -> dict[str, Any]:
    rows = [
        row
        for result in source_results
        if not result.get("error")
        for row in result.get("rows") or []
    ]
    selections = [row["selection"] for row in rows]
    ratios = [
        float(item["public_slice_motif_ops_over_rho"])
        for item in selections
        if item.get("public_slice_motif_ops_over_rho") is not None
    ]
    preserving = [item for item in selections if item.get("preserves_selected_root_pairs")]
    below = [item for item in selections if item.get("public_slice_motif_beats_rho")]
    preserving_below = [
        item
        for item in selections
        if item.get("preserves_selected_root_pairs") and item.get("public_slice_motif_beats_rho")
    ]
    chosen_nonzero = [item for item in selections if int(item.get("chosen_count") or 0) > 0]
    preserving_below_nonzero = [
        item
        for item in chosen_nonzero
        if item.get("preserves_selected_root_pairs") and item.get("public_slice_motif_beats_rho")
    ]
    preserving_below_recovered = [
        item
        for item in preserving_below_nonzero
        if int(item.get("original_selected_root_pair_count") or 0) > 0
        and int(item.get("selected_root_pair_count") or 0) > 0
    ]
    compatible = [result for result in source_results if not result.get("error") and int(result.get("surface_count") or 0) > 0]
    errors = [result for result in source_results if result.get("error")]
    return {
        "below_rho_count": len(below),
        "chosen_nonzero_count": len(chosen_nonzero),
        "compatible_source_count": len(compatible),
        "error_source_count": len(errors),
        "max_ops_over_rho": round(max(ratios), 8) if ratios else None,
        "mean_ops_over_rho": round(mean(ratios), 8) if ratios else None,
        "min_ops_over_rho": round(min(ratios), 8) if ratios else None,
        "preserving_below_rho_count": len(preserving_below),
        "preserving_below_rho_nonzero_count": len(preserving_below_nonzero),
        "preserving_below_rho_recovered_count": len(preserving_below_recovered),
        "preserving_count": len(preserving),
        "source_count": len(source_results),
        "surface_count": len(rows),
        "total_chosen_slices": sum(int(item.get("chosen_count") or 0) for item in selections),
    }


def determine_claim(aggregate: dict[str, Any]) -> str:
    if int(aggregate["compatible_source_count"]) == 0:
        return "NEGATIVE_RESULT_P880_NO_COMPATIBLE_FRESH_SLICE_MATERIALIZATION"
    if int(aggregate["preserving_below_rho_recovered_count"]) > 0:
        return "P880_FROZEN_PUBLIC_SLICE_MOTIF_REPLICATES_ON_FRESH_SOURCES"
    if int(aggregate["preserving_below_rho_count"]) > 0:
        return "P880_FROZEN_PUBLIC_SLICE_MOTIF_PRESERVES_BELOW_RHO_WITH_ZERO_SLICE_EDGE"
    if int(aggregate["preserving_count"]) > 0:
        return "P880_FROZEN_PUBLIC_SLICE_MOTIF_PRESERVES_ONLY_ABOVE_RHO"
    if int(aggregate["below_rho_count"]) > 0:
        return "NEGATIVE_RESULT_P880_FROZEN_PUBLIC_SLICE_MOTIF_CHEAP_BUT_MISSES_ROOTS"
    return "NEGATIVE_RESULT_P880_FROZEN_PUBLIC_SLICE_MOTIF_NO_FRESH_SIGNAL"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p842_payload = load_json(args.p842_source)
    selected_policy = p842_payload["selected_policy"]
    motif_set = normalize_motif_set(selected_policy["motif_set"])
    ps = p842.load_module("ecdlp_public_slice_for_p880", p842.PUBLIC_SLICE_SCRIPT)

    source_paths = args.signature_source or DEFAULT_FRESH_SOURCES
    source_paths = [Path(path) for path in source_paths[: int(args.max_sources)]]
    source_results = [
        evaluate_source(
            ps,
            source_path,
            motif_set,
            int(args.max_cases_per_source),
            int(args.max_factor_degree),
        )
        for source_path in source_paths
    ]
    aggregate = aggregate_metrics(source_results)
    claim_status = determine_claim(aggregate)
    return {
        "aggregate_metrics": aggregate,
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p842_source": str(args.p842_source),
            "script": str(Path(__file__)),
        },
        "claim_status": claim_status,
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP FFE quotient harness only.",
            "MOTIF-FROZEN: the motif set is copied from P842 and not retrained on fresh labels.",
            "FRESH-SOURCE BOUNDARY: fresh sources are later expanded leaf-rescue summaries, not a deployment-scale curve family.",
            "PUBLIC-SELECTION BOUNDARY: selection uses public factor signatures, not selected-leaf labels.",
            "POLLARD-RHO BOUNDARY: this is relation-generation evidence, not a complete faster-than-rho ECDLP algorithm.",
        ],
        "method": "p880_public_slice_motif_fresh_source_validation",
        "parameters": {
            "fresh_source_count": len(source_paths),
            "max_cases_per_source": int(args.max_cases_per_source),
            "max_factor_degree": int(args.max_factor_degree),
        },
        "p842_positive_control": {
            "claim_status": p842_payload.get("claim_status"),
            "selected_policy": selected_policy,
        },
        "red_team_handoff": {
            "assumptions": [
                "P842 exact-factor motifs are a meaningful public proxy for slice-quadratic choices.",
                "Expanded leaf-rescue summaries can be rematerialized through the same public slice backend.",
                "Preserving-below-rho surfaces are the correct promotion metric, not raw cheap misses.",
            ],
            "failure_modes": [
                "The frozen motif may be overfit to transfers 32..69.",
                "Fresh summaries may contain different row/leaf structures that the P842 backend cannot materialize.",
                "Cheap below-rho rows can be zero-slice misses and must not be promoted.",
            ],
            "next_concrete_action": (
                "If P880 is positive, replicate on later disjoint windows and add residual-gap accounting; "
                "if it is negative, broaden the public predictor or implement a true bivariate factor backend."
            ),
        },
        "schema": SCHEMA,
        "source_results": source_results,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p842-source", type=Path, default=DEFAULT_P842_SOURCE)
    parser.add_argument("--signature-source", type=Path, action="append")
    parser.add_argument("--max-sources", type=int, default=len(DEFAULT_FRESH_SOURCES))
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
                "aggregate_metrics": payload["aggregate_metrics"],
                "claim_status": payload["claim_status"],
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
