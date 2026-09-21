#!/usr/bin/env python3
"""Replay and time a shared selected-leaf product scanner.

P233 validated that the `67.a1@9803@1166` target-diversity gap closes if the
two fixed compact-leaf rows share duplicate selected-leaf work and charge the
selected-leaf product/batch over the union of public leaf signatures once.
This probe implements that missing local scanner shape:

* build one product tree from the unique selected public leaf signatures;
* for each row, gcd the shared selected-leaf product with the row hit
  polynomial;
* associate hit roots back through the selected-product tree;
* verify the emitted cover and scalar derivation match the direct selected-leaf
  scanner.

The rho comparison remains an operation ledger, not wall-clock-to-rho
calibration.  The timing result only checks that the shared-product scanner is a
real replay path rather than a purely symbolic saving.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import frontier_signed_eval_cover_association_probe as association_probe
import frontier_signed_eval_cover_product_gcd_probe as product_gcd_probe
import frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_shared_challenge_direct_witness_probe as direct_witness_probe
import frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_shared_challenge_salt_neighborhood_low_term_total2_ffe_hit_stream_probe as hit_stream_probe
import low_term_total2_fixed_leaf_shared_context_audit_probe as context_probe
import low_term_total2_guarded_shared_preassociation_timing_probe as timing_probe
import low_term_total2_public_prefix_shared_leaf_repair_probe as repair_probe
import public_factor_forward_safe_multiblock_zero_extra_relation_rank_probe as rank_probe


DEFAULT_STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_SOURCE = (
    DEFAULT_STATE_DIR
    / "frontier_public_leaf_policy_p231_frozen_prefix_fixed_row_1160_1167_probe.json"
)
DEFAULT_OUT = (
    DEFAULT_STATE_DIR
    / "low_term_total2_fixed_leaf_shared_product_timing_67_1166_probe.json"
)


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


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def selected_contexts_from_source_case(
    source: dict[str, Any],
    source_case: dict[str, Any],
) -> tuple[Any, list[dict[str, Any]], int, int]:
    params = repair_probe.source_parameters(source)
    probe_args = repair_probe.probe_args_from_source(source)
    verifier, records, config_source, specs_by_target = repair_probe.build_specs(params)
    context_cache: dict[tuple[str, int, int, tuple[str, ...]], dict[str, Any]] = {}
    context = hit_stream_probe.scan_case_context(
        verifier,
        records,
        config_source,
        specs_by_target,
        source_case,
        probe_args,
        context_cache,
    )
    contexts = []
    for item in hit_stream_probe.unique_row_leaf_keys(source_case):
        row_key = str(item["row_key"])
        selected = {int_value(leaf) for leaf in item.get("leaf_indices") or []}
        contexts.append(
            {
                "row_key": row_key,
                "selected_leaf_indices": selected,
                "built": context["built_by_row"][row_key],
                "components": context["components_by_row"][row_key],
                "local_args": context["local_args_by_row"][row_key],
            }
        )
    return verifier, contexts, int_value(probe_args.product_factor, 4096), int_value(probe_args.max_relations, 96)


def selected_signature_tree(contexts: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any]]:
    signatures: dict[str, dict[str, Any]] = {}
    for context in contexts:
        for leaf_index in sorted(context["selected_leaf_indices"]):
            leaf = context["components"]["leaves"][int(leaf_index)]
            signature = context_probe.leaf_signature(leaf)
            key = context_probe.signature_key(signature)
            entry = signatures.setdefault(
                key,
                {
                    "signature_key": key,
                    "signature": signature,
                    "poly": [int_value(part) for part in leaf.get("poly") or []],
                    "occurrences": [],
                },
            )
            entry["occurrences"].append(
                {"row_key": context["row_key"], "leaf_index": int(leaf_index)}
            )
    p = int_value(contexts[0]["built"].get("p")) if contexts else 0
    leaves = [
        {
            "key": key,
            "poly": row["poly"],
            "scout_positions": [],
        }
        for key, row in sorted(signatures.items())
    ]
    tree = product_gcd_probe.build_product_tree(leaves, p)
    stats = product_gcd_probe.tree_stats(tree)
    profile = {
        "unique_selected_leaf_signature_count": len(signatures),
        "selected_leaf_occurrence_count": sum(len(row["occurrences"]) for row in signatures.values()),
        "shared_product_saved_leaf_computations": max(
            0,
            sum(len(row["occurrences"]) for row in signatures.values()) - len(signatures),
        ),
        "selected_product_degree": max(0, len(tree.get("poly") or []) - 1),
        "selected_product_tree_nodes": stats["nodes"],
        "selected_product_tree_sum_degrees": stats["sum_degrees"],
        "signature_groups": [
            {
                "signature_key": key,
                "signature": row["signature"],
                "occurrences": row["occurrences"],
            }
            for key, row in sorted(signatures.items())
        ],
    }
    return tree, profile


def associate_signature_root(
    root: int,
    node: dict[str, Any],
    p: int,
    stats: dict[str, int],
) -> list[str]:
    if node.get("key") is not None:
        stats["leaf_hits"] += 1
        return [str(node["key"])]
    out: list[str] = []
    for child_name in ("left", "right"):
        child = node.get(child_name)
        if child is None:
            continue
        stats["node_evals"] += 1
        stats["degree_eval_cost"] += max(0, len(child.get("poly") or []) - 1)
        if association_probe.polyops.poly_eval(child["poly"], int(root), p) == 0:
            out.extend(associate_signature_root(root, child, p, stats))
    return out


def row_signature_leafs(context: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    out: dict[str, list[dict[str, Any]]] = {}
    for leaf_index in sorted(context["selected_leaf_indices"]):
        leaf = context["components"]["leaves"][int(leaf_index)]
        key = context_probe.signature_key(context_probe.leaf_signature(leaf))
        out.setdefault(key, []).append(leaf)
    return out


def shared_product_pair_association(contexts: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if not contexts:
        return [], {}
    p = int_value(contexts[0]["built"].get("p"))
    tree, profile = selected_signature_tree(contexts)
    covers = []
    row_profiles = []
    for context in contexts:
        components = context["components"]
        selected_by_signature = row_signature_leafs(context)
        gcd_poly = association_probe.polyops.poly_gcd(
            tree["poly"],
            components["hit_poly"],
            p,
        )
        hit_roots = association_probe.roots_in_hit_set(
            gcd_poly,
            components["hit_roots"],
            p,
        )
        hits_by_scout = association_probe.empty_hits(context["built"]["scouts"])
        selected_hit_roots: set[int] = set()
        association_stats = {"node_evals": 0, "degree_eval_cost": 0, "leaf_hits": 0}
        x_matches = 0
        for root in hit_roots:
            signature_keys = associate_signature_root(int(root), tree, p, association_stats)
            matched = False
            for key in signature_keys:
                for leaf in selected_by_signature.get(key, []):
                    if association_probe.polyops.poly_eval(leaf["poly"], int(root), p) != 0:
                        continue
                    x_matches += association_probe.add_leaf_hits(
                        hits_by_scout,
                        leaf,
                        [int(root)],
                        components["rows_by_x"],
                    )
                    matched = True
            if matched:
                selected_hit_roots.add(int(root))
        hits_by_scout = association_probe.finalize_hits(
            hits_by_scout,
            components["row_order"],
        )
        covers.append(
            {
                "hits_by_scout": hits_by_scout,
                "row_hit_count": association_probe.row_hit_counts(hits_by_scout),
                "shared_product_gcd_checks": 1,
                "shared_product_gcd_degree": max(0, len(gcd_poly) - 1),
                "hit_root_values": len(hit_roots),
                "selected_hit_root_values": len(selected_hit_roots),
                "leaf_gcd_checks": len(profile.get("signature_groups") or []),
                "leaf_gcd_hits": association_stats["leaf_hits"],
                "leaf_gcd_degree_work": association_stats["degree_eval_cost"],
                "leaf_gcd_root_output_degree": len(selected_hit_roots),
                "leaf_gcd_x_matches": x_matches,
                "association_node_evals": association_stats["node_evals"],
                "association_degree_eval_cost": association_stats["degree_eval_cost"],
                "association_leaf_hits": association_stats["leaf_hits"],
            }
        )
        row_profiles.append(
            {
                "row_key": context["row_key"],
                "shared_product_gcd_degree": max(0, len(gcd_poly) - 1),
                "hit_root_values": len(hit_roots),
                "selected_hit_root_values": len(selected_hit_roots),
                "x_matches": x_matches,
                **association_stats,
            }
        )
    profile["row_shared_product_profiles"] = row_profiles
    profile["row_shared_product_gcd_checks"] = len(contexts)
    return covers, profile


def scan_from_covers(
    verifier: Any,
    contexts: list[dict[str, Any]],
    covers: list[dict[str, Any]],
    max_relations: int,
) -> list[dict[str, Any]]:
    return [
        timing_probe.scan_from_cover(verifier, context, cover, max_relations)
        for context, cover in zip(contexts, covers, strict=True)
    ]


def direct_witness_rows(verifier: Any, contexts: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int, int, list[dict[str, Any]]]:
    rows = []
    direct_ops = 0
    rho = 0
    profiles = []
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
        rows.append({"row_key": context["row_key"], "_scan": scan})
        profiles.append(
            context_probe.row_profile(
                str(context["row_key"]),
                sorted(context["selected_leaf_indices"]),
                context["built"],
                context["components"],
                scan,
                context["local_args"],
            )
        )
    return rows, direct_ops, rho, profiles


def summarize(
    source_case: dict[str, Any],
    direct_union: dict[str, Any],
    shared_union: dict[str, Any],
    direct_ops: int,
    rho: int,
    sharing_profile: dict[str, Any],
    product_profile: dict[str, Any],
    direct_covers: list[dict[str, Any]],
    shared_covers: list[dict[str, Any]],
    timings: dict[str, Any],
) -> dict[str, Any]:
    covers_match = timing_probe.covers_match(direct_covers, shared_covers)
    product_saved = int_value(sharing_profile.get("shared_selected_leaf_product_saved_ops"))
    duplicate_saved = int_value(sharing_profile.get("duplicate_selected_leaf_check_saved_ops"))
    shared_product_ops = direct_ops - duplicate_saved - product_saved
    status = "SHARED_PRODUCT_TIMING_NEEDS_REVIEW"
    if covers_match and bool(shared_union.get("union_public_key_verified")) and shared_product_ops < rho:
        status = "TIMED_SHARED_PRODUCT_SCANNER_REPRODUCES_BELOW_RHO_LEDGER"
    elif covers_match and bool(shared_union.get("union_public_key_verified")):
        status = "TIMED_SHARED_PRODUCT_SCANNER_REPRODUCES_SCALAR_DERIVATION"
    return {
        "status": status,
        "claim_status": "TOY-EVIDENCE / REPLAY-BACKED SHARED SELECTED-PRODUCT SCANNER / LEDGER-BOUND RHO COMPARISON / NOT A DEPLOYABLE ECDLP BREAK",
        "target": source_case.get("target"),
        "transfer_index": int_value(source_case.get("transfer_index")),
        "selector": source_case.get("selector"),
        "top_k": int_value(source_case.get("top_k")),
        "rho": rho,
        "direct_verifier_replay_ops": direct_ops,
        "direct_verifier_replay_ops_over_rho": ratio(direct_ops, rho),
        "direct_union_public_key_verified": bool(direct_union.get("union_public_key_verified")),
        "direct_union_rank": int_value(direct_union.get("union_rank")),
        "direct_union_relation_count": int_value(direct_union.get("union_relation_count")),
        "direct_union_derived_secret": direct_union.get("union_derived_secret"),
        "shared_product_cover_matches_direct_selected_cover": covers_match,
        "shared_product_union_public_key_verified": bool(shared_union.get("union_public_key_verified")),
        "shared_product_union_rank": int_value(shared_union.get("union_rank")),
        "shared_product_union_relation_count": int_value(shared_union.get("union_relation_count")),
        "shared_product_union_derived_secret": shared_union.get("union_derived_secret"),
        "unique_selected_leaf_signature_count": int_value(
            product_profile.get("unique_selected_leaf_signature_count")
        ),
        "selected_leaf_occurrence_count": int_value(
            product_profile.get("selected_leaf_occurrence_count")
        ),
        "duplicate_selected_leaf_check_saved_ops": duplicate_saved,
        "shared_selected_leaf_product_saved_ops": product_saved,
        "shared_product_ledger_ops": shared_product_ops,
        "shared_product_ledger_ops_over_rho": ratio(shared_product_ops, rho),
        "shared_product_ledger_beats_rho": bool(shared_product_ops < rho),
        "direct_association_wall_ms_min": timings["direct_association"]["wall_ms_min"],
        "shared_product_association_wall_ms_min": timings["shared_product_association"]["wall_ms_min"],
        "shared_product_vs_direct_association_wall_ms_min_speedup": ratio(
            timings["direct_association"]["wall_ms_min"],
            max(1e-12, timings["shared_product_association"]["wall_ms_min"]),
        ),
        "direct_scan_wall_ms_min": timings["direct_scan"]["wall_ms_min"],
        "shared_product_scan_wall_ms_min": timings["shared_product_scan"]["wall_ms_min"],
        "shared_product_vs_direct_scan_wall_ms_min_speedup": ratio(
            timings["direct_scan"]["wall_ms_min"],
            max(1e-12, timings["shared_product_scan"]["wall_ms_min"]),
        ),
        "interpretation": (
            "The selected-product scanner is a real replay path: it builds the "
            "unique selected-leaf product once, intersects it with each row hit "
            "polynomial, and emits the same cover and scalar derivation as the "
            "direct selected-leaf scanner.  The rho comparison is still the local "
            "operation ledger, not wall-clock-to-rho calibration."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--target", default="67.a1@9803")
    parser.add_argument("--transfer-index", type=int, default=1166)
    parser.add_argument("--selector", default="mode_low_term_span_total10")
    parser.add_argument("--top-k", type=int, default=16)
    parser.add_argument("--timing-repeats", type=int, default=25)
    parser.add_argument("--timing-inner", type=int, default=50)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    source = load_json(args.source)
    source_case = context_probe.find_source_case(
        source,
        args.target,
        int(args.transfer_index),
        args.selector,
        args.top_k,
    )
    verifier, contexts, product_factor, max_relations = selected_contexts_from_source_case(
        source,
        source_case,
    )
    direct_rows_for_union, direct_ops, rho, row_profiles = direct_witness_rows(
        verifier,
        contexts,
    )
    built_by_row = {str(context["row_key"]): context["built"] for context in contexts}
    direct_union = direct_witness_probe.union_derive(
        verifier,
        direct_rows_for_union,
        built_by_row,
        "_scan",
    )
    sharing_profile = context_probe.selected_leaf_sharing_profile(row_profiles, product_factor)
    direct_covers, direct_association_timing = timing_probe.time_call(
        lambda: timing_probe.direct_selected_pair_association(contexts),
        args.timing_repeats,
        args.timing_inner,
    )
    shared_result, shared_association_timing = timing_probe.time_call(
        lambda: shared_product_pair_association(contexts),
        args.timing_repeats,
        args.timing_inner,
    )
    shared_covers, product_profile = shared_result
    direct_scan_rows, direct_scan_timing = timing_probe.time_call(
        lambda: timing_probe.direct_selected_pair_scan(verifier, contexts, max_relations),
        args.timing_repeats,
        max(1, args.timing_inner // 10),
    )
    shared_scan_rows, shared_scan_timing = timing_probe.time_call(
        lambda: scan_from_covers(verifier, contexts, shared_product_pair_association(contexts)[0], max_relations),
        args.timing_repeats,
        max(1, args.timing_inner // 10),
    )
    first_built = contexts[0]["built"] if contexts else {}
    shared_union = rank_probe.union_derive(verifier, shared_scan_rows, first_built)
    direct_scan_union = rank_probe.union_derive(verifier, direct_scan_rows, first_built)
    timings = {
        "direct_association": direct_association_timing,
        "shared_product_association": shared_association_timing,
        "direct_scan": direct_scan_timing,
        "shared_product_scan": shared_scan_timing,
    }
    output = {
        "schema": "ecdlp.low_term_total2_fixed_leaf_shared_product_timing.v1",
        "method": "timed_shared_selected_leaf_product_scanner",
        "parameters": {
            "source": str(args.source),
            "target": args.target,
            "transfer_index": args.transfer_index,
            "selector": args.selector,
            "top_k": args.top_k,
            "timing_repeats": args.timing_repeats,
            "timing_inner": args.timing_inner,
            "product_factor": product_factor,
            "out": str(args.out),
        },
        "source_case": source_case,
        "summary": summarize(
            source_case,
            direct_union,
            shared_union,
            direct_ops,
            rho,
            sharing_profile,
            product_profile,
            direct_covers,
            shared_covers,
            timings,
        ),
        "selected_leaf_sharing_profile": sharing_profile,
        "shared_product_profile": product_profile,
        "timings": timings,
        "direct_covers": [timing_probe.normalized_cover(cover) for cover in direct_covers],
        "shared_product_covers": [
            timing_probe.normalized_cover(cover) for cover in shared_covers
        ],
        "direct_scan_union": direct_scan_union,
        "shared_product_union": shared_union,
        "direct_scan_rows": rank_probe.strip_private_rows(direct_scan_rows),
        "shared_product_scan_rows": rank_probe.strip_private_rows(shared_scan_rows),
        "honesty_boundary": [
            "The shared-product scanner is replay-backed and cover-checked against the direct selected-leaf scanner.",
            "The operation count still uses the local selected-leaf product_factor ledger; wall-clock timings are reported only as implementation evidence.",
            "This is controlled toy-prime evidence for a local graph/index-calculus optimization, not a deployed-curve ECDLP break.",
        ],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps(output["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
