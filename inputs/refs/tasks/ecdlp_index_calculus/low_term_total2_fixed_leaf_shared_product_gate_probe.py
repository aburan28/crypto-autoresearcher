#!/usr/bin/env python3
"""Public duplicate-signature gate for the shared selected-product scanner.

P234 showed that the selected-product scanner helps the `67.a1@9803@1166`
target-diversity repair, but is not a universal wall-clock replacement.  This
probe turns that into a public pre-gate: inspect only the selected public leaf
signatures and run the shared-product scanner when duplicate signature density
predicts enough work reuse.

The gate is public because it uses selected leaf signatures reconstructed from
row envelopes and fixed leaf selectors; it does not use relation rank, derived
secret, or public-key verification to decide whether to invoke the scanner.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

import frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_shared_challenge_direct_witness_probe as direct_witness_probe
import frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_shared_challenge_salt_neighborhood_low_term_total2_ffe_hit_stream_probe as hit_stream_probe
import low_term_total2_fixed_leaf_shared_context_audit_probe as context_probe
import low_term_total2_fixed_leaf_shared_product_timing_probe as product_timing_probe
import low_term_total2_public_prefix_shared_leaf_repair_probe as repair_probe


DEFAULT_STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_SOURCE = (
    DEFAULT_STATE_DIR
    / "frontier_public_leaf_policy_p231_frozen_prefix_fixed_row_1168_1175_probe.json"
)
DEFAULT_OUT = (
    DEFAULT_STATE_DIR
    / "low_term_total2_fixed_leaf_shared_product_gate_1168_1175_probe.json"
)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


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


def source_cases(source: dict[str, Any], targets: set[str], transfers: set[int]) -> list[dict[str, Any]]:
    cases = []
    for policy_name, result in (source.get("policies") or {}).items():
        if not isinstance(result, dict):
            continue
        row_selector = (result.get("row_selector") or {}).get("selector")
        for row in result.get("stress_leaf_results") or []:
            if not isinstance(row, dict) or not row.get("source_verified"):
                continue
            target = str(row.get("target"))
            transfer = int_value(row.get("transfer_index"))
            if targets and target not in targets:
                continue
            if transfers and transfer not in transfers:
                continue
            row_leaf_keys = hit_stream_probe.unique_row_leaf_keys(row)
            if len(row_leaf_keys) != 2:
                continue
            cases.append(
                {
                    **row,
                    "source_policy": policy_name,
                    "row_selector": row.get("row_selector") or row_selector,
                    "row_leaf_keys": row_leaf_keys,
                }
            )
    cases.sort(
        key=lambda row: (
            str(row.get("target")),
            int_value(row.get("transfer_index")),
            str(row.get("selector")),
            int_value(row.get("top_k")),
            json.dumps(row.get("row_leaf_keys") or [], sort_keys=True),
        )
    )
    return cases


def build_case_contexts(
    source: dict[str, Any],
    case: dict[str, Any],
    verifier: Any,
    records: list[dict[str, Any]],
    config_source: dict[str, Any],
    specs_by_target: dict[str, dict[str, dict[str, Any]]],
    probe_args: Any,
    context_cache: dict[tuple[str, int, int, tuple[str, ...]], dict[str, Any]],
) -> list[dict[str, Any]]:
    context = hit_stream_probe.scan_case_context(
        verifier,
        records,
        config_source,
        specs_by_target,
        case,
        probe_args,
        context_cache,
    )
    contexts = []
    for item in hit_stream_probe.unique_row_leaf_keys(case):
        row_key = str(item["row_key"])
        selected = {int_value(leaf) for leaf in item.get("leaf_indices") or []}
        if row_key not in context["built_by_row"]:
            continue
        contexts.append(
            {
                "row_key": row_key,
                "selected_leaf_indices": selected,
                "built": context["built_by_row"][row_key],
                "components": context["components_by_row"][row_key],
                "local_args": context["local_args_by_row"][row_key],
            }
        )
    return contexts


def direct_profiles(verifier: Any, contexts: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int, int, list[dict[str, Any]], dict[str, Any]]:
    direct_rows_for_union = []
    built_by_row = {}
    row_profiles = []
    direct_ops = 0
    rho = 0
    for context in contexts:
        scan = direct_witness_probe.scan_selected(
            verifier,
            context["built"],
            context["components"],
            context["selected_leaf_indices"],
            context["local_args"],
        )
        direct_ops += int_value(scan.get("preassociation_filter_ops"))
        rho = max(rho, int_value(context["built"].get("generic_rho_steps")))
        direct_rows_for_union.append({"row_key": context["row_key"], "_scan": scan})
        built_by_row[str(context["row_key"])] = context["built"]
        row_profiles.append(
            context_probe.row_profile(
                str(context["row_key"]),
                sorted(context["selected_leaf_indices"]),
                context["built"],
                context["components"],
                scan,
                context["local_args"],
            )
        )
    union = direct_witness_probe.union_derive(
        verifier,
        direct_rows_for_union,
        built_by_row,
        "_scan",
    )
    return direct_rows_for_union, direct_ops, rho, row_profiles, union


def gate_metrics(row_profiles: list[dict[str, Any]], product_factor: int) -> dict[str, Any]:
    sharing = context_probe.selected_leaf_sharing_profile(row_profiles, product_factor)
    occurrence_count = int_value(sharing.get("direct_selected_leaf_check_ops"))
    unique_count = int_value(sharing.get("unique_selected_leaf_signature_count"))
    duplicate_saved = int_value(sharing.get("duplicate_selected_leaf_check_saved_ops"))
    product_saved = int_value(sharing.get("shared_selected_leaf_product_saved_ops"))
    return {
        **sharing,
        "duplicate_signature_density": ratio(duplicate_saved, occurrence_count) or 0.0,
        "unique_signature_fraction": ratio(unique_count, occurrence_count) or 0.0,
        "public_gate_duplicate_ge5_product_ge1": bool(
            duplicate_saved >= 5 and product_saved >= 1
        ),
        "public_gate_duplicate_density_ge_half_product_ge1": bool(
            occurrence_count > 0
            and duplicate_saved * 2 >= occurrence_count
            and product_saved >= 1
        ),
        "public_gate_all_rows_share_selected_signatures": bool(
            sharing.get("all_selected_leaf_signatures_shared_across_two_rows")
        ),
    }


def analyze_case(
    verifier: Any,
    source: dict[str, Any],
    case: dict[str, Any],
    product_factor: int,
    max_relations: int,
    records: list[dict[str, Any]],
    config_source: dict[str, Any],
    specs_by_target: dict[str, dict[str, dict[str, Any]]],
    probe_args: Any,
    context_cache: dict[tuple[str, int, int, tuple[str, ...]], dict[str, Any]],
    gate_name: str,
) -> dict[str, Any]:
    contexts = build_case_contexts(
        source,
        case,
        verifier,
        records,
        config_source,
        specs_by_target,
        probe_args,
        context_cache,
    )
    _rows, direct_ops, rho, row_profiles, direct_union = direct_profiles(verifier, contexts)
    metrics = gate_metrics(row_profiles, product_factor)
    gated = bool(metrics.get(gate_name))
    out = {
        "target": case.get("target"),
        "transfer_index": int_value(case.get("transfer_index")),
        "selector": case.get("selector"),
        "top_k": int_value(case.get("top_k")),
        "row_keys": [context["row_key"] for context in contexts],
        "source_ops_over_rho": case.get("ops_over_rho"),
        "source_public_key_verified": bool(case.get("public_key_verified")),
        "source_below_rho": bool(case.get("below_rho")),
        "direct_verifier_replay_ops": direct_ops,
        "rho": rho,
        "direct_verifier_replay_ops_over_rho": ratio(direct_ops, rho),
        "direct_below_rho": bool(rho and direct_ops < rho),
        "direct_union_public_key_verified": bool(direct_union.get("union_public_key_verified")),
        "direct_union_rank": int_value(direct_union.get("union_rank")),
        "direct_union_relation_count": int_value(direct_union.get("union_relation_count")),
        "direct_union_derived_secret": direct_union.get("union_derived_secret"),
        "public_product_gate_selected": gated,
        "gate_name": gate_name,
        "gate_metrics": {
            key: value
            for key, value in metrics.items()
            if key != "groups"
        },
    }
    if not gated:
        return out

    direct_covers = product_timing_probe.timing_probe.direct_selected_pair_association(contexts)
    shared_covers, product_profile = product_timing_probe.shared_product_pair_association(contexts)
    shared_scan_rows = product_timing_probe.scan_from_covers(
        verifier,
        contexts,
        shared_covers,
        max_relations,
    )
    first_built = contexts[0]["built"] if contexts else {}
    shared_union = product_timing_probe.rank_probe.union_derive(
        verifier,
        shared_scan_rows,
        first_built,
    )
    product_saved = int_value(metrics.get("shared_selected_leaf_product_saved_ops"))
    duplicate_saved = int_value(metrics.get("duplicate_selected_leaf_check_saved_ops"))
    shared_product_ops = direct_ops - duplicate_saved - product_saved
    out.update(
        {
            "shared_product_cover_matches_direct_selected_cover": product_timing_probe.timing_probe.covers_match(
                direct_covers,
                shared_covers,
            ),
            "shared_product_union_public_key_verified": bool(
                shared_union.get("union_public_key_verified")
            ),
            "shared_product_union_rank": int_value(shared_union.get("union_rank")),
            "shared_product_union_relation_count": int_value(
                shared_union.get("union_relation_count")
            ),
            "shared_product_union_derived_secret": shared_union.get("union_derived_secret"),
            "shared_product_ledger_ops": shared_product_ops,
            "shared_product_ledger_ops_over_rho": ratio(shared_product_ops, rho),
            "shared_product_ledger_beats_rho": bool(rho and shared_product_ops < rho),
            "shared_product_profile": {
                key: value
                for key, value in product_profile.items()
                if key not in {"signature_groups"}
            },
        }
    )
    return out


def summarize(rows: list[dict[str, Any]], gate_name: str) -> dict[str, Any]:
    selected = [row for row in rows if row.get("public_product_gate_selected")]
    verified = [row for row in selected if row.get("shared_product_union_public_key_verified")]
    below = [row for row in verified if row.get("shared_product_ledger_beats_rho")]
    direct_below = [row for row in rows if row.get("direct_below_rho") and row.get("direct_union_public_key_verified")]
    target_counts = Counter(str(row.get("target")) for row in selected)
    verified_target_counts = Counter(str(row.get("target")) for row in verified)
    below_target_counts = Counter(str(row.get("target")) for row in below)
    best = sorted(
        verified,
        key=lambda row: (
            float(row.get("shared_product_ledger_ops_over_rho") or 10**18),
            float(row.get("direct_verifier_replay_ops_over_rho") or 10**18),
            str(row.get("target")),
            int_value(row.get("transfer_index")),
        ),
    )[:8]
    return {
        "case_count": len(rows),
        "gate_name": gate_name,
        "public_product_gate_selected_count": len(selected),
        "public_product_gate_selected_target_counts": dict(target_counts.most_common()),
        "selected_shared_product_verified_count": len(verified),
        "selected_shared_product_verified_target_counts": dict(
            verified_target_counts.most_common()
        ),
        "selected_shared_product_below_rho_count": len(below),
        "selected_shared_product_below_rho_target_counts": dict(
            below_target_counts.most_common()
        ),
        "direct_below_rho_verified_count": len(direct_below),
        "direct_below_rho_verified_target_counts": dict(
            Counter(str(row.get("target")) for row in direct_below).most_common()
        ),
        "gate_false_positive_count": len(selected) - len(verified),
        "gate_verified_above_rho_count": len(verified) - len(below),
        "best_selected_shared_product_cases": [
            {
                "target": row.get("target"),
                "transfer_index": row.get("transfer_index"),
                "selector": row.get("selector"),
                "top_k": row.get("top_k"),
                "row_keys": row.get("row_keys"),
                "direct_verifier_replay_ops_over_rho": row.get(
                    "direct_verifier_replay_ops_over_rho"
                ),
                "shared_product_ledger_ops_over_rho": row.get(
                    "shared_product_ledger_ops_over_rho"
                ),
                "direct_union_rank": row.get("direct_union_rank"),
                "direct_union_relation_count": row.get("direct_union_relation_count"),
                "shared_product_union_rank": row.get("shared_product_union_rank"),
                "shared_product_union_relation_count": row.get(
                    "shared_product_union_relation_count"
                ),
                "duplicate_signature_density": (row.get("gate_metrics") or {}).get(
                    "duplicate_signature_density"
                ),
                "duplicate_selected_leaf_check_saved_ops": (
                    row.get("gate_metrics") or {}
                ).get("duplicate_selected_leaf_check_saved_ops"),
                "shared_selected_leaf_product_saved_ops": (
                    row.get("gate_metrics") or {}
                ).get("shared_selected_leaf_product_saved_ops"),
            }
            for row in best
        ],
        "claim_status": (
            "PUBLIC_GATE_VALIDATION_POSITIVE"
            if below
            else "PUBLIC_GATE_VALIDATION_NO_BELOW_RHO_SELECTED_CASE"
        ),
        "interpretation": (
            "The gate uses only public selected-leaf signature duplication before "
            "invoking the shared-product scanner.  Shared-product rho comparisons "
            "are operation-ledger comparisons; verifier replay checks scalar "
            "derivation after the public gate selects a case."
        ),
    }


def parse_csv(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [part.strip() for part in raw.split(",") if part.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--targets", default="")
    parser.add_argument("--transfers", default="")
    parser.add_argument(
        "--gate",
        default="public_gate_duplicate_ge5_product_ge1",
        choices=[
            "public_gate_duplicate_ge5_product_ge1",
            "public_gate_duplicate_density_ge_half_product_ge1",
            "public_gate_all_rows_share_selected_signatures",
        ],
    )
    args = parser.parse_args()

    source = load_json(args.source)
    targets = set(parse_csv(args.targets))
    transfers = {int(part) for part in parse_csv(args.transfers)}
    params = repair_probe.source_parameters(source)
    probe_args = repair_probe.probe_args_from_source(source)
    verifier, records, config_source, specs_by_target = repair_probe.build_specs(params)
    product_factor = int_value(probe_args.product_factor, 4096)
    max_relations = int_value(probe_args.max_relations, 96)
    cases = source_cases(source, targets, transfers)
    context_cache: dict[tuple[str, int, int, tuple[str, ...]], dict[str, Any]] = {}
    rows = [
        analyze_case(
            verifier,
            source,
            case,
            product_factor,
            max_relations,
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
        "schema": "ecdlp.low_term_total2_fixed_leaf_shared_product_gate.v1",
        "method": "public_duplicate_selected_leaf_signature_gate_for_shared_product_scanner",
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
            "The gate uses public selected-leaf signature duplication only.",
            "Verifier rank, relation count, derived secret, and below-rho status are measured only after the public gate decision.",
            "Shared-product cost is an operation ledger and not a wall-clock-to-rho calibration.",
            "This is controlled toy-prime evidence, not a deployed-curve ECDLP break.",
        ],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps(output["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
