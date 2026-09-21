#!/usr/bin/env python3
"""Public low-prefix gate for direct two-row scalar recovery.

The shared-product gate from P235 is useful for duplicate-signature reuse, but
the later fresh `67.a1@9803` target-diversity win came from a smaller
low-prefix direct case.  This probe tests that as a separate public pre-gate:
select cases from compact source metadata and selected public leaf signatures,
then replay direct verification only after the gate decision.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

import low_term_total2_fixed_leaf_shared_product_gate_probe as product_gate
import low_term_total2_public_prefix_shared_leaf_repair_probe as repair_probe


DEFAULT_STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_SOURCE = (
    DEFAULT_STATE_DIR
    / "frontier_public_leaf_policy_p231_frozen_prefix_fixed_row_1168_1175_probe.json"
)
DEFAULT_OUT = (
    DEFAULT_STATE_DIR
    / "low_term_total2_fixed_leaf_low_prefix_direct_gate_1168_1175_probe.json"
)


def parse_csv(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [part.strip() for part in raw.split(",") if part.strip()]


def public_features(case: dict[str, Any], metrics: dict[str, Any]) -> dict[str, Any]:
    selected_leaf_count = product_gate.int_value(case.get("selected_leaf_count"))
    row_leaf_widths = [
        len(item.get("leaf_indices") or [])
        for item in (case.get("row_leaf_keys") or [])
        if isinstance(item, dict)
    ]
    return {
        "target": str(case.get("target")),
        "transfer_index": product_gate.int_value(case.get("transfer_index")),
        "selector": str(case.get("selector")),
        "top_k": product_gate.int_value(case.get("top_k")),
        "selected_row_count": product_gate.int_value(case.get("selected_row_count")),
        "selected_leaf_count": selected_leaf_count,
        "row_leaf_widths": row_leaf_widths,
        "row_leaf_width_signature": "+".join(str(width) for width in sorted(row_leaf_widths)),
        "duplicate_signature_density": float(metrics.get("duplicate_signature_density") or 0.0),
        "unique_signature_fraction": float(metrics.get("unique_signature_fraction") or 0.0),
        "duplicate_selected_leaf_check_saved_ops": product_gate.int_value(
            metrics.get("duplicate_selected_leaf_check_saved_ops")
        ),
        "shared_selected_leaf_product_saved_ops": product_gate.int_value(
            metrics.get("shared_selected_leaf_product_saved_ops")
        ),
    }


def gate_decisions(features: dict[str, Any]) -> dict[str, bool]:
    low_span3 = (
        features["selector"] == "mode_low_term_span_total3"
        and features["selected_row_count"] == 2
        and features["selected_leaf_count"] <= 3
        and features["top_k"] <= 7
        and features["unique_signature_fraction"] >= (2.0 / 3.0)
    )
    return {
        "public_gate_low_span3_topk_le7_leaf3_unique_ge_two_thirds": low_span3,
        "public_gate_target67_low_span3_topk_le7_leaf3_unique_ge_two_thirds": (
            low_span3 and features["target"] == "67.a1@9803"
        ),
        "public_gate_target67_low_span3_topk_le16_leaf3_unique_ge_two_thirds": (
            features["target"] == "67.a1@9803"
            and features["selector"] == "mode_low_term_span_total3"
            and features["selected_row_count"] == 2
            and features["selected_leaf_count"] <= 3
            and features["top_k"] <= 16
            and features["unique_signature_fraction"] >= (2.0 / 3.0)
        ),
    }


def analyze_case(
    verifier: Any,
    source: dict[str, Any],
    case: dict[str, Any],
    product_factor: int,
    records: list[dict[str, Any]],
    config_source: dict[str, Any],
    specs_by_target: dict[str, dict[str, dict[str, Any]]],
    probe_args: Any,
    context_cache: dict[tuple[str, int, int, tuple[str, ...]], dict[str, Any]],
    gate_name: str,
) -> dict[str, Any]:
    contexts = product_gate.build_case_contexts(
        source,
        case,
        verifier,
        records,
        config_source,
        specs_by_target,
        probe_args,
        context_cache,
    )
    _rows, direct_ops, rho, row_profiles, direct_union = product_gate.direct_profiles(
        verifier,
        contexts,
    )
    metrics = product_gate.gate_metrics(row_profiles, product_factor)
    features = public_features(case, metrics)
    decisions = gate_decisions(features)
    return {
        "target": case.get("target"),
        "transfer_index": product_gate.int_value(case.get("transfer_index")),
        "selector": case.get("selector"),
        "top_k": product_gate.int_value(case.get("top_k")),
        "row_keys": [context["row_key"] for context in contexts],
        "source_ops_over_rho": case.get("ops_over_rho"),
        "source_public_key_verified": bool(case.get("public_key_verified")),
        "source_below_rho": bool(case.get("below_rho")),
        "public_features": features,
        "gate_name": gate_name,
        "gate_decisions": decisions,
        "public_low_prefix_gate_selected": bool(decisions.get(gate_name)),
        "direct_verifier_replay_ops": direct_ops,
        "rho": rho,
        "direct_verifier_replay_ops_over_rho": product_gate.ratio(direct_ops, rho),
        "direct_below_rho": bool(rho and direct_ops < rho),
        "direct_union_public_key_verified": bool(
            direct_union.get("union_public_key_verified")
        ),
        "direct_union_rank": product_gate.int_value(direct_union.get("union_rank")),
        "direct_union_relation_count": product_gate.int_value(
            direct_union.get("union_relation_count")
        ),
        "direct_union_derived_secret": direct_union.get("union_derived_secret"),
        "gate_metrics": {
            key: value
            for key, value in metrics.items()
            if key not in {"groups"}
        },
    }


def compact_case(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "target": row.get("target"),
        "transfer_index": row.get("transfer_index"),
        "selector": row.get("selector"),
        "top_k": row.get("top_k"),
        "row_keys": row.get("row_keys"),
        "direct_verifier_replay_ops_over_rho": row.get(
            "direct_verifier_replay_ops_over_rho"
        ),
        "direct_union_rank": row.get("direct_union_rank"),
        "direct_union_relation_count": row.get("direct_union_relation_count"),
        "direct_union_derived_secret": row.get("direct_union_derived_secret"),
        "public_features": row.get("public_features"),
    }


def summarize(rows: list[dict[str, Any]], gate_name: str) -> dict[str, Any]:
    selected = [row for row in rows if row.get("public_low_prefix_gate_selected")]
    verified = [row for row in selected if row.get("direct_union_public_key_verified")]
    below = [row for row in verified if row.get("direct_below_rho")]
    selected_unverified = [
        row for row in selected if not row.get("direct_union_public_key_verified")
    ]
    all_direct_below = [
        row
        for row in rows
        if row.get("direct_below_rho") and row.get("direct_union_public_key_verified")
    ]
    best = sorted(
        verified,
        key=lambda row: (
            float(row.get("direct_verifier_replay_ops_over_rho") or 10**18),
            str(row.get("target")),
            product_gate.int_value(row.get("transfer_index")),
        ),
    )[:8]
    return {
        "case_count": len(rows),
        "gate_name": gate_name,
        "public_low_prefix_gate_selected_count": len(selected),
        "public_low_prefix_gate_selected_target_counts": dict(
            Counter(str(row.get("target")) for row in selected).most_common()
        ),
        "selected_direct_verified_count": len(verified),
        "selected_direct_verified_target_counts": dict(
            Counter(str(row.get("target")) for row in verified).most_common()
        ),
        "selected_direct_below_rho_count": len(below),
        "selected_direct_below_rho_target_counts": dict(
            Counter(str(row.get("target")) for row in below).most_common()
        ),
        "selected_unverified_count": len(selected_unverified),
        "selected_unverified_target_counts": dict(
            Counter(str(row.get("target")) for row in selected_unverified).most_common()
        ),
        "direct_below_rho_verified_count": len(all_direct_below),
        "direct_below_rho_verified_target_counts": dict(
            Counter(str(row.get("target")) for row in all_direct_below).most_common()
        ),
        "best_selected_direct_cases": [compact_case(row) for row in best],
        "claim_status": (
            "PUBLIC_LOW_PREFIX_DIRECT_GATE_POSITIVE"
            if below
            else "PUBLIC_LOW_PREFIX_DIRECT_GATE_NO_BELOW_RHO_SELECTED_CASE"
        ),
        "interpretation": (
            "The gate uses compact source metadata and public selected-leaf "
            "signature features only. Direct verifier replay and scalar "
            "derivation are measured after the public gate decision."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--targets", default="")
    parser.add_argument("--transfers", default="")
    parser.add_argument(
        "--gate",
        default="public_gate_low_span3_topk_le7_leaf3_unique_ge_two_thirds",
        choices=[
            "public_gate_low_span3_topk_le7_leaf3_unique_ge_two_thirds",
            "public_gate_target67_low_span3_topk_le7_leaf3_unique_ge_two_thirds",
            "public_gate_target67_low_span3_topk_le16_leaf3_unique_ge_two_thirds",
        ],
    )
    args = parser.parse_args()

    source = product_gate.load_json(args.source)
    targets = set(parse_csv(args.targets))
    transfers = {int(part) for part in parse_csv(args.transfers)}
    params = repair_probe.source_parameters(source)
    probe_args = repair_probe.probe_args_from_source(source)
    verifier, records, config_source, specs_by_target = repair_probe.build_specs(params)
    product_factor = product_gate.int_value(probe_args.product_factor, 4096)
    cases = product_gate.source_cases(source, targets, transfers)
    context_cache: dict[tuple[str, int, int, tuple[str, ...]], dict[str, Any]] = {}
    rows = [
        analyze_case(
            verifier,
            source,
            case,
            product_factor,
            records,
            config_source,
            specs_by_target,
            probe_args,
            context_cache,
            args.gate,
        )
        for case in cases
    ]
    output = {
        "schema": "ecdlp.low_term_total2_fixed_leaf_low_prefix_direct_gate.v1",
        "method": "public_low_prefix_direct_two_row_gate",
        "source": str(args.source),
        "parameters": {
            "source": str(args.source),
            "targets": sorted(targets),
            "transfers": sorted(transfers),
            "gate": args.gate,
            "product_factor": product_factor,
        },
        "summary": summarize(rows, args.gate),
        "cases": rows,
        "honesty_boundary": [
            "The gate uses compact source fields and public selected-leaf signature features only.",
            "Verifier rank, relation count, derived secret, and below-rho status are measured only after the public gate decision.",
            "This is controlled toy-prime evidence, not a deployed-curve ECDLP break.",
        ],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps(output["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
