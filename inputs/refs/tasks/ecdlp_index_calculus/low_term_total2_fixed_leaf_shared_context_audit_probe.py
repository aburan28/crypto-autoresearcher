#!/usr/bin/env python3
"""Audit shared selected-leaf context for a fixed compact-leaf pair.

The P231 frozen-prefix stress run left a narrow target-diversity boundary:
``67.a1@9803`` at transfer 1166 derives the scalar with two public rows and a
fixed compact leaf selector, but the direct selected-leaf ledger costs 130
operations against Pollard rho 125.

This probe replays that exact verifier path and then asks a local graph
question: if the two rows select identical public leaf signatures, what work is
duplicated by treating them as separate row scans?  Direct replay is measured by
the existing verifier scanner.  Any shared selected-leaf product/batch charge is
MODEL-BOUND until a timed shared-product kernel is implemented.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from math import ceil
from pathlib import Path
from typing import Any

import frontier_signed_eval_cover_association_probe as association_probe
import frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_shared_challenge_direct_witness_probe as direct_witness_probe
import frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_shared_challenge_salt_neighborhood_low_term_total2_ffe_hit_stream_probe as hit_stream_probe
import low_term_total2_public_prefix_shared_leaf_repair_probe as repair_probe
import low_term_total2_guarded_shared_preassociation_timing_probe as timing_probe
import public_factor_forward_safe_multiblock_zero_extra_relation_rank_probe as rank_probe


DEFAULT_STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_SOURCE = (
    DEFAULT_STATE_DIR
    / "frontier_public_leaf_policy_p231_frozen_prefix_fixed_row_1160_1167_probe.json"
)
DEFAULT_OUT = (
    DEFAULT_STATE_DIR
    / "low_term_total2_fixed_leaf_shared_context_audit_67_1166_probe.json"
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


def ratio(numerator: int, denominator: int) -> float | None:
    if denominator <= 0:
        return None
    return round(int(numerator) / int(denominator), 8)


def find_source_case(
    source: dict[str, Any],
    target: str,
    transfer_index: int,
    selector: str,
    top_k: int | None,
) -> dict[str, Any]:
    matches = []
    for policy_name, result in (source.get("policies") or {}).items():
        if not isinstance(result, dict):
            continue
        row_selector = (result.get("row_selector") or {}).get("selector")
        for row in result.get("stress_leaf_results") or []:
            if not isinstance(row, dict):
                continue
            if str(row.get("target")) != target:
                continue
            if int_value(row.get("transfer_index")) != transfer_index:
                continue
            if str(row.get("selector")) != selector:
                continue
            if top_k is not None and int_value(row.get("top_k")) != top_k:
                continue
            matches.append(
                {
                    **row,
                    "source_policy": policy_name,
                    "row_selector": row.get("row_selector") or row_selector,
                }
            )
    if not matches:
        raise ValueError(
            f"no source case for target={target!r} transfer={transfer_index} "
            f"selector={selector!r} top_k={top_k!r}"
        )
    matches.sort(
        key=lambda row: (
            not bool(row.get("public_key_verified")),
            not bool(row.get("source_verified")),
            float(row.get("ops_over_rho") or 10**18),
            str(row.get("source_policy")),
        )
    )
    return matches[0]


def leaf_signature(leaf: dict[str, Any]) -> dict[str, Any]:
    return {
        "key": [int_value(part) for part in leaf.get("key") or []],
        "poly": [int_value(part) for part in leaf.get("poly") or []],
        "scout_positions": [int_value(pos) for pos in leaf.get("scout_positions") or []],
    }


def signature_key(signature: dict[str, Any]) -> str:
    return json.dumps(signature, sort_keys=True, separators=(",", ":"))


def normalized_event(event: dict[str, Any]) -> dict[str, Any]:
    return {
        "candidate_pos": int_value(event.get("candidate_pos")),
        "factor_support": [int_value(part) for part in event.get("factor_support") or []],
        "leaf_index": int_value(event.get("leaf_index")),
        "term_shape": str(event.get("term_shape") or ""),
        "terms": [int_value(part) for part in event.get("terms") or []],
    }


def event_shape_key(row: dict[str, Any]) -> str:
    events = [normalized_event(event) for event in row.get("event_summaries") or []]
    events.sort(
        key=lambda event: (
            event["leaf_index"],
            event["candidate_pos"],
            event["term_shape"],
            event["terms"],
            event["factor_support"],
        )
    )
    return json.dumps(events, sort_keys=True, separators=(",", ":"))


def row_pool_fingerprint(rows: list[dict[str, Any]]) -> str:
    payload = [
        {"trial": int_value(row.get("trial")), "x": int_value(row.get("x"))}
        for row in rows
    ]
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def row_x_set(rows: list[dict[str, Any]]) -> set[int]:
    return {int_value(row.get("x")) for row in rows}


def cost_parts(built: dict[str, Any], scan: dict[str, Any], local_args: Any) -> dict[str, Any]:
    selected_leaf_count = int_value(scan.get("selected_leaf_count"))
    selected_hit_roots = int_value(scan.get("selected_hit_roots"))
    selected_hit_events = int_value(scan.get("selected_hit_events"))
    signed_pair_ops = int_value(built.get("selected_signed_pair_count"))
    row_pool_ops = ceil(int_value(built.get("row_pool")) / max(1, int_value(local_args.row_factor, 1)))
    product_ops = ceil(selected_leaf_count / max(1, int_value(local_args.product_factor, 1)))
    root_ops = selected_hit_roots
    leaf_check_ops = selected_leaf_count
    event_ops = 2 * selected_hit_events
    total = signed_pair_ops + row_pool_ops + product_ops + root_ops + leaf_check_ops + event_ops
    return {
        "selected_signed_pair_ops": signed_pair_ops,
        "row_pool_ops": row_pool_ops,
        "selected_leaf_product_ops": product_ops,
        "selected_hit_root_ops": root_ops,
        "selected_leaf_check_ops": leaf_check_ops,
        "selected_hit_event_ops": event_ops,
        "reconstructed_preassociation_filter_ops": total,
        "matches_scanner_preassociation_filter_ops": total
        == int_value(scan.get("preassociation_filter_ops")),
    }


def row_profile(
    row_key: str,
    selected_leaf_indices: list[int],
    built: dict[str, Any],
    components: dict[str, Any],
    scan: dict[str, Any],
    local_args: Any,
) -> dict[str, Any]:
    p = int_value(built.get("p"))
    leaf_profiles = []
    for leaf_index in selected_leaf_indices:
        leaf = components["leaves"][int(leaf_index)]
        signature = leaf_signature(leaf)
        roots = association_probe.roots_in_hit_set(
            leaf.get("poly") or [],
            components.get("hit_roots") or [],
            p,
        )
        leaf_profiles.append(
            {
                "leaf_index": int(leaf_index),
                "signature": signature,
                "signature_key": signature_key(signature),
                "true_hit_roots": [int(root) for root in roots],
            }
        )
    return {
        "row_key": row_key,
        "challenge_seed": built.get("challenge_seed"),
        "row_seed_prefix": built.get("row_seed_prefix"),
        "scout_seed_prefix": built.get("scout_seed_prefix"),
        "row_pool": int_value(built.get("row_pool")),
        "scheduled_row_count": int_value(built.get("scheduled_row_count")),
        "generic_rho_steps": int_value(built.get("generic_rho_steps")),
        "row_pool_fingerprint": row_pool_fingerprint(built.get("rows") or []),
        "row_x_count": len(row_x_set(built.get("rows") or [])),
        "selected_leaf_indices": selected_leaf_indices,
        "selected_leaf_signatures": [row["signature"] for row in leaf_profiles],
        "selected_leaf_signature_keys": [row["signature_key"] for row in leaf_profiles],
        "leaf_root_profiles": leaf_profiles,
        "scan": repair_probe.compact_scan(scan),
        "event_summaries": scan.get("event_summaries") or [],
        "cost_parts": cost_parts(built, scan, local_args),
    }


def event_shape_profile(rows: list[dict[str, Any]]) -> dict[str, Any]:
    groups: dict[str, dict[str, Any]] = {}
    total_events = 0
    for row in rows:
        key = event_shape_key(row)
        event_count = int_value(row.get("selected_hit_events"))
        total_events += event_count
        groups.setdefault(
            key,
            {"normalized_events": json.loads(key), "row_keys": [], "event_counts": []},
        )
        groups[key]["row_keys"].append(row.get("row_key"))
        groups[key]["event_counts"].append(event_count)
    max_event_charge = sum(max(group["event_counts"]) for group in groups.values())
    return {
        "shape_group_count": len(groups),
        "row_selected_hit_events": total_events,
        "current_event_ops": 2 * total_events,
        "shape_max_event_ops": 2 * max_event_charge,
        "shape_max_event_saved_ops": max(0, 2 * total_events - 2 * max_event_charge),
        "groups": [
            {
                "normalized_events": group["normalized_events"],
                "row_keys": group["row_keys"],
                "event_counts": group["event_counts"],
                "max_event_count": max(group["event_counts"]),
            }
            for group in groups.values()
        ],
        "ignored_row_specific_fields": [
            "original_trial",
            "q_coeff",
            "relation_index",
            "rhs",
            "scheduled_trial",
        ],
    }


def selected_leaf_sharing_profile(row_profiles: list[dict[str, Any]], product_factor: int) -> dict[str, Any]:
    groups: dict[str, dict[str, Any]] = {}
    direct_leaf_checks = 0
    direct_product_ops = 0
    direct_root_ops = 0
    for row in row_profiles:
        scan = row.get("scan") or {}
        selected_count = int_value(scan.get("selected_leaf_count"))
        direct_leaf_checks += selected_count
        direct_product_ops += ceil(selected_count / max(1, product_factor))
        direct_root_ops += int_value(scan.get("selected_hit_roots"))
        for leaf in row.get("leaf_root_profiles") or []:
            key = str(leaf.get("signature_key"))
            group = groups.setdefault(
                key,
                {
                    "signature": leaf.get("signature"),
                    "row_leafs": [],
                    "root_values": set(),
                },
            )
            group["row_leafs"].append(
                {
                    "row_key": row.get("row_key"),
                    "leaf_index": int_value(leaf.get("leaf_index")),
                    "true_hit_roots": [int(root) for root in leaf.get("true_hit_roots") or []],
                }
            )
            group["root_values"].update(int(root) for root in leaf.get("true_hit_roots") or [])
    unique_signature_count = len(groups)
    shared_product_ops = ceil(unique_signature_count / max(1, product_factor)) if groups else 0
    shared_root_charge = sum(len(group["root_values"]) for group in groups.values())
    compact_groups = []
    for key, group in sorted(groups.items()):
        compact_groups.append(
            {
                "signature_key": key,
                "signature": group["signature"],
                "row_leafs": group["row_leafs"],
                "row_leaf_count": len(group["row_leafs"]),
                "unique_true_hit_roots": sorted(int(root) for root in group["root_values"]),
            }
        )
    return {
        "direct_selected_leaf_check_ops": direct_leaf_checks,
        "unique_selected_leaf_signature_count": unique_signature_count,
        "duplicate_selected_leaf_check_saved_ops": max(0, direct_leaf_checks - unique_signature_count),
        "direct_selected_leaf_product_ops": direct_product_ops,
        "shared_selected_leaf_product_ops": shared_product_ops,
        "shared_selected_leaf_product_saved_ops": max(0, direct_product_ops - shared_product_ops),
        "direct_selected_hit_root_ops": direct_root_ops,
        "shared_signature_root_charge": shared_root_charge,
        "shared_signature_root_saved_ops": max(0, direct_root_ops - shared_root_charge),
        "all_selected_leaf_signatures_shared_across_two_rows": bool(
            len(row_profiles) == 2
            and all(len(group["row_leafs"]) == 2 for group in groups.values())
            and unique_signature_count
            == min(len(row.get("selected_leaf_signature_keys") or []) for row in row_profiles)
        ),
        "groups": compact_groups,
    }


def row_pool_overlap(row_profiles: list[dict[str, Any]], built_by_row: dict[str, dict[str, Any]], row_factor: int) -> dict[str, Any]:
    row_sets = [
        row_x_set((built_by_row.get(str(profile.get("row_key"))) or {}).get("rows") or [])
        for profile in row_profiles
    ]
    row_pool_ops_sum = sum(
        ceil(
            len((built_by_row.get(str(profile.get("row_key"))) or {}).get("rows") or [])
            / max(1, row_factor)
        )
        for profile in row_profiles
    )
    if not row_sets:
        union_count = 0
        shared_x_count = 0
    else:
        union = set().union(*row_sets)
        union_count = len(union)
        shared_x_count = len(set.intersection(*row_sets)) if len(row_sets) > 1 else len(union)
    dedup_ops = ceil(union_count / max(1, row_factor)) if union_count else 0
    fingerprints = {str(row.get("row_pool_fingerprint")) for row in row_profiles}
    return {
        "row_pool_ops_sum": row_pool_ops_sum,
        "exact_row_pool_fingerprint_match": len(fingerprints) == 1 and bool(row_profiles),
        "row_pool_once_saved_ops": max(0, row_pool_ops_sum - max(1, row_pool_ops_sum // max(1, len(row_profiles)))),
        "dedup_x_union_count": union_count,
        "dedup_x_row_pool_ops": dedup_ops,
        "dedup_x_row_pool_saved_ops": max(0, row_pool_ops_sum - dedup_ops),
        "shared_x_count": shared_x_count,
    }


def roots_in_field(poly: list[int], p: int) -> list[int]:
    return [
        value
        for value in range(max(0, p))
        if association_probe.polyops.poly_eval(poly, value, p) == 0
    ]


def shared_signature_pair_association(
    contexts: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    cover_states = []
    signature_roots: dict[str, dict[str, Any]] = {}
    occurrence_count = 0
    for context in contexts:
        built = context["built"]
        components = context["components"]
        cover_states.append(
            {
                "context": context,
                "hits_by_scout": association_probe.empty_hits(built["scouts"]),
                "selected_hit_roots": set(),
                "x_matches": 0,
            }
        )
        for leaf_index in sorted(context["selected_leaf_indices"]):
            leaf = components["leaves"][leaf_index]
            signature = leaf_signature(leaf)
            key = signature_key(signature)
            if key not in signature_roots:
                signature_roots[key] = {
                    "signature": signature,
                    "roots": roots_in_field([int_value(part) for part in leaf.get("poly") or []], int_value(built["p"])),
                    "occurrences": [],
                }
            signature_roots[key]["occurrences"].append(
                {"row_key": context["row_key"], "leaf_index": int(leaf_index)}
            )
            occurrence_count += 1

    by_row_leaf = {
        (str(context["row_key"]), int(leaf_index)): (
            context,
            context["components"]["leaves"][int(leaf_index)],
        )
        for context in contexts
        for leaf_index in sorted(context["selected_leaf_indices"])
    }
    state_by_row = {str(state["context"]["row_key"]): state for state in cover_states}
    for group in signature_roots.values():
        roots = [int(root) for root in group["roots"]]
        for occurrence in group["occurrences"]:
            row_key = str(occurrence["row_key"])
            context, leaf = by_row_leaf[(row_key, int(occurrence["leaf_index"]))]
            components = context["components"]
            hit_set = {int(root) for root in components.get("hit_roots") or []}
            row_roots = [root for root in roots if root in hit_set]
            state = state_by_row[row_key]
            state["selected_hit_roots"].update(row_roots)
            state["x_matches"] += association_probe.add_leaf_hits(
                state["hits_by_scout"],
                leaf,
                row_roots,
                components["rows_by_x"],
            )

    covers = []
    for state in cover_states:
        components = state["context"]["components"]
        hits_by_scout = association_probe.finalize_hits(
            state["hits_by_scout"],
            components["row_order"],
        )
        covers.append(
            {
                "hits_by_scout": hits_by_scout,
                "row_hit_count": association_probe.row_hit_counts(hits_by_scout),
                "leaf_gcd_checks": len(signature_roots),
                "leaf_gcd_hits": sum(
                    1
                    for group in signature_roots.values()
                    if any(
                        int(root) in {int(hit) for hit in components.get("hit_roots") or []}
                        for root in group["roots"]
                    )
                ),
                "leaf_gcd_degree_work": 0,
                "leaf_gcd_root_output_degree": len(state["selected_hit_roots"]),
                "leaf_gcd_x_matches": int_value(state["x_matches"]),
                "selected_hit_root_values": len(state["selected_hit_roots"]),
            }
        )
    profile = {
        "unique_selected_leaf_signature_count": len(signature_roots),
        "selected_leaf_occurrence_count": occurrence_count,
        "shared_signature_saved_leaf_computations": max(0, occurrence_count - len(signature_roots)),
        "signature_root_groups": [
            {
                "signature": row["signature"],
                "root_count": len(row["roots"]),
                "roots": [int(root) for root in row["roots"]],
                "occurrences": row["occurrences"],
            }
            for row in signature_roots.values()
        ],
    }
    return covers, profile


def shared_signature_scanner_profile(
    verifier: Any,
    contexts: list[dict[str, Any]],
    max_relations: int,
) -> dict[str, Any]:
    direct_covers = timing_probe.direct_selected_pair_association(contexts)
    shared_covers, signature_profile = shared_signature_pair_association(contexts)
    direct_rows = timing_probe.direct_selected_pair_scan(verifier, contexts, max_relations)
    shared_rows = [
        timing_probe.scan_from_cover(verifier, context, cover, max_relations)
        for context, cover in zip(contexts, shared_covers, strict=True)
    ]
    first_built = contexts[0]["built"] if contexts else {}
    direct_union = rank_probe.union_derive(verifier, direct_rows, first_built)
    shared_union = rank_probe.union_derive(verifier, shared_rows, first_built)
    return {
        **signature_profile,
        "shared_signature_cover_matches_direct_selected_cover": timing_probe.covers_match(
            direct_covers,
            shared_covers,
        ),
        "shared_signature_union_public_key_verified": bool(
            shared_union.get("union_public_key_verified")
        ),
        "shared_signature_union_rank": int_value(shared_union.get("union_rank")),
        "shared_signature_union_relation_count": int_value(
            shared_union.get("union_relation_count")
        ),
        "shared_signature_union_derived_secret": shared_union.get("union_derived_secret"),
        "direct_union_public_key_verified": bool(direct_union.get("union_public_key_verified")),
        "direct_union_rank": int_value(direct_union.get("union_rank")),
        "direct_union_relation_count": int_value(direct_union.get("union_relation_count")),
        "direct_union_derived_secret": direct_union.get("union_derived_secret"),
        "direct_covers": [timing_probe.normalized_cover(cover) for cover in direct_covers],
        "shared_signature_covers": [
            timing_probe.normalized_cover(cover) for cover in shared_covers
        ],
        "claim_boundary": (
            "The shared-signature cover builder computes each selected public leaf "
            "signature once and replays roots into each row context. It validates "
            "duplicate selected-leaf computation sharing, but the product/batch "
            "one-op ledger still needs a timed implementation."
        ),
    }


def scenario(name: str, baseline: int, rho: int, savings: dict[str, int], validation: str) -> dict[str, Any]:
    saved = sum(max(0, int_value(value)) for value in savings.values())
    ops = baseline - saved
    return {
        "name": name,
        "ops": ops,
        "ops_over_rho": ratio(ops, rho),
        "saved_ops": saved,
        "savings": savings,
        "validation": validation,
        "beats_rho": bool(rho > 0 and ops < rho),
        "at_or_below_rho": bool(rho > 0 and ops <= rho),
        "extra_savings_needed_below_rho": max(0, ops - rho + 1) if rho > 0 else None,
    }


def summarize(
    source_case: dict[str, Any],
    union: dict[str, Any],
    direct_ops: int,
    rho: int,
    sharing: dict[str, Any],
    scanner: dict[str, Any],
    event_profile: dict[str, Any],
    pool_profile: dict[str, Any],
    scenarios: list[dict[str, Any]],
) -> dict[str, Any]:
    by_name = {row["name"]: row for row in scenarios}
    product_once = by_name["shared_leaf_checks_plus_product_once"]
    leaf_only = by_name["shared_leaf_checks_only"]
    status = "FIXED_LEAF_SHARED_CONTEXT_AUDIT_NEEDS_REVIEW"
    direct_below = bool(rho > 0 and direct_ops < rho)
    target_gap_closed = bool(
        union.get("union_public_key_verified")
        and not direct_below
        and product_once["beats_rho"]
    )
    scanner_matches = bool(scanner.get("shared_signature_cover_matches_direct_selected_cover"))
    if bool(union.get("union_public_key_verified")) and direct_below:
        status = "DIRECT_VERIFIER_BACKED_BELOW_RHO_CONTROL_RECONFIRMED"
    elif target_gap_closed and scanner_matches:
        status = "SCANNER_BACKED_SHARED_LEAF_AND_MODEL_BOUND_PRODUCT_CLOSE_TARGET_DIVERSITY_GAP"
    elif target_gap_closed:
        status = "MODEL_BOUND_SHARED_SELECTED_LEAF_PRODUCT_CLOSES_TARGET_DIVERSITY_GAP"
    elif bool(union.get("union_public_key_verified")) and leaf_only["at_or_below_rho"]:
        status = "SHARED_SELECTED_LEAF_CHECKS_REACH_RHO_EXACTLY"
    shared_all = bool(sharing.get("all_selected_leaf_signatures_shared_across_two_rows"))
    if shared_all:
        interpretation = (
            "Direct verifier replay reproduces the fixed compact-leaf scalar recovery. "
            "The selected leaf signatures are identical across the two rows, so "
            "duplicate leaf checks reach rho exactly on the target-diversity near "
            "miss; additionally charging the selected-leaf product/batch once "
            "crosses below rho.  That product-once step is MODEL-BOUND and needs "
            "a timed shared-product scanner before promotion beyond a local "
            "optimization work order."
        )
    else:
        interpretation = (
            "Direct verifier replay reproduces the fixed compact-leaf scalar recovery. "
            "The selected leaves are not all identical across the two rows, but the "
            "audit still reports duplicate exact leaf signatures and the MODEL-BOUND "
            "cross-row selected-leaf product/batch charge over the union of public "
            "leaf signatures.  The product-once step needs a timed shared-product "
            "scanner before promotion beyond a local optimization work order."
        )
    return {
        "status": status,
        "claim_status": "TOY-EVIDENCE / MODEL-BOUND SHARED SELECTED-LEAF PRODUCT / NOT A DEPLOYABLE ECDLP BREAK",
        "target": source_case.get("target"),
        "transfer_index": int_value(source_case.get("transfer_index")),
        "selector": source_case.get("selector"),
        "top_k": int_value(source_case.get("top_k")),
        "rho": rho,
        "source_ops_over_rho": source_case.get("ops_over_rho"),
        "direct_verifier_replay_ops": direct_ops,
        "direct_verifier_replay_ops_over_rho": ratio(direct_ops, rho),
        "direct_union_public_key_verified": bool(union.get("union_public_key_verified")),
        "direct_union_rank": int_value(union.get("union_rank")),
        "direct_union_relation_count": int_value(union.get("union_relation_count")),
        "direct_union_derived_secret": union.get("union_derived_secret"),
        "all_selected_leaf_signatures_shared_across_two_rows": bool(
            sharing.get("all_selected_leaf_signatures_shared_across_two_rows")
        ),
        "shared_signature_cover_matches_direct_selected_cover": scanner_matches,
        "shared_signature_union_public_key_verified": bool(
            scanner.get("shared_signature_union_public_key_verified")
        ),
        "shared_signature_saved_leaf_computations": int_value(
            scanner.get("shared_signature_saved_leaf_computations")
        ),
        "duplicate_selected_leaf_check_saved_ops": int_value(
            sharing.get("duplicate_selected_leaf_check_saved_ops")
        ),
        "shared_selected_leaf_product_saved_ops": int_value(
            sharing.get("shared_selected_leaf_product_saved_ops")
        ),
        "event_shape_max_saved_ops": int_value(event_profile.get("shape_max_event_saved_ops")),
        "dedup_x_row_pool_saved_ops": int_value(pool_profile.get("dedup_x_row_pool_saved_ops")),
        "leaf_checks_only_ops": leaf_only["ops"],
        "leaf_checks_only_ops_over_rho": leaf_only["ops_over_rho"],
        "leaf_checks_plus_product_once_ops": product_once["ops"],
        "leaf_checks_plus_product_once_ops_over_rho": product_once["ops_over_rho"],
        "interpretation": interpretation,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--target", default="67.a1@9803")
    parser.add_argument("--transfer-index", type=int, default=1166)
    parser.add_argument("--selector", default="mode_low_term_span_total10")
    parser.add_argument("--top-k", type=int, default=16)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    source = load_json(args.source)
    source_case = find_source_case(
        source,
        args.target,
        int(args.transfer_index),
        args.selector,
        args.top_k,
    )
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

    row_profiles = []
    rows_for_union = []
    built_for_union = {}
    direct_rows = []
    timing_contexts = []
    direct_ops = 0
    rho = 0
    for item in hit_stream_probe.unique_row_leaf_keys(source_case):
        row_key = str(item["row_key"])
        selected = {int_value(leaf) for leaf in item.get("leaf_indices") or []}
        built = context["built_by_row"][row_key]
        components = context["components_by_row"][row_key]
        local_args = context["local_args_by_row"][row_key]
        scan = direct_witness_probe.scan_selected(
            verifier,
            built,
            components,
            selected,
            local_args,
        )
        direct_ops += int_value(scan.get("preassociation_filter_ops"))
        rho = max(rho, int_value(built.get("generic_rho_steps")))
        rows_for_union.append({"row_key": row_key, "_fixed_leaf": scan})
        built_for_union[row_key] = built
        direct_rows.append({"row_key": row_key, **repair_probe.compact_scan(scan)})
        timing_contexts.append(
            {
                "row_key": row_key,
                "built": built,
                "components": components,
                "selected_leaf_indices": selected,
            }
        )
        row_profiles.append(
            row_profile(
                row_key,
                sorted(selected),
                built,
                components,
                scan,
                local_args,
            )
        )
    union = direct_witness_probe.union_derive(
        verifier,
        rows_for_union,
        built_for_union,
        "_fixed_leaf",
    )
    product_factor = int_value(probe_args.product_factor, 4096)
    row_factor = int_value(probe_args.row_factor, 512)
    sharing = selected_leaf_sharing_profile(row_profiles, product_factor)
    scanner = shared_signature_scanner_profile(
        verifier,
        timing_contexts,
        int_value(probe_args.max_relations, 96),
    )
    event_profile = event_shape_profile(direct_rows)
    pool_profile = row_pool_overlap(row_profiles, built_for_union, row_factor)
    scenarios = [
        scenario("direct_verifier_replay", direct_ops, rho, {}, "measured"),
        scenario(
            "shared_leaf_checks_only",
            direct_ops,
            rho,
            {"duplicate_selected_leaf_checks": int_value(sharing.get("duplicate_selected_leaf_check_saved_ops"))},
            "model_bound_identical_selected_leaf_signatures",
        ),
        scenario(
            "shared_leaf_checks_plus_product_once",
            direct_ops,
            rho,
            {
                "duplicate_selected_leaf_checks": int_value(
                    sharing.get("duplicate_selected_leaf_check_saved_ops")
                ),
                "selected_leaf_product_once": int_value(
                    sharing.get("shared_selected_leaf_product_saved_ops")
                ),
            },
            "model_bound_cross_row_selected_leaf_product_batch",
        ),
        scenario(
            "leaf_product_plus_event_shape_max",
            direct_ops,
            rho,
            {
                "duplicate_selected_leaf_checks": int_value(
                    sharing.get("duplicate_selected_leaf_check_saved_ops")
                ),
                "selected_leaf_product_once": int_value(
                    sharing.get("shared_selected_leaf_product_saved_ops")
                ),
                "event_shape_max": int_value(event_profile.get("shape_max_event_saved_ops")),
            },
            "model_bound_product_once_plus_event_shape_normalization",
        ),
        scenario(
            "leaf_product_plus_dedup_x_row_pool",
            direct_ops,
            rho,
            {
                "duplicate_selected_leaf_checks": int_value(
                    sharing.get("duplicate_selected_leaf_check_saved_ops")
                ),
                "selected_leaf_product_once": int_value(
                    sharing.get("shared_selected_leaf_product_saved_ops")
                ),
                "dedup_x_row_pool": int_value(pool_profile.get("dedup_x_row_pool_saved_ops")),
            },
            "deduplicated_x_union_row_pool_charge",
        ),
    ]
    output = {
        "schema": "ecdlp.low_term_total2_fixed_leaf_shared_context_audit.v1",
        "method": "fixed_compact_leaf_pair_shared_selected_leaf_context_audit",
        "parameters": {
            "source": str(args.source),
            "target": args.target,
            "transfer_index": args.transfer_index,
            "selector": args.selector,
            "top_k": args.top_k,
            "out": str(args.out),
            "product_factor": product_factor,
            "row_factor": row_factor,
        },
        "source_case": source_case,
        "summary": summarize(
            source_case,
            union,
            direct_ops,
            rho,
            sharing,
            scanner,
            event_profile,
            pool_profile,
            scenarios,
        ),
        "selected_leaf_sharing_profile": sharing,
        "shared_signature_scanner_profile": scanner,
        "event_shape_profile": event_profile,
        "row_pool_overlap": pool_profile,
        "row_profiles": row_profiles,
        "direct_rows": direct_rows,
        "direct_union": union,
        "scenarios": scenarios,
        "honesty_boundary": [
            "Direct verifier replay is measured by the existing selected-leaf scanner.",
            "Duplicate selected-leaf check savings require identical selected leaf signatures and are model-bound until implemented as a shared scanner path.",
            "Selected-leaf product-once savings are a ledger-level work order over identical selected leaf signatures, not a timed wall-clock-to-rho result.",
            "This is controlled toy-prime evidence for a local graph/index-calculus optimization, not a deployed-curve ECDLP break.",
        ],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps(output["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
