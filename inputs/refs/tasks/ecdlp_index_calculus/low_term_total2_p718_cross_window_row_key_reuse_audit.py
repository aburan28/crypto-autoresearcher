#!/usr/bin/env python3
"""P718 audit for cross-window row-key reuse in P716/P717 two-by-two rel2 hits."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p709_source_replay_no_archive_oracle as p709
import low_term_total2_p716_rel2_source_generation_enrichment as p716
import low_term_total2_p717_two_by_two_rel2_source_cost_compression as p717


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P709 = STATE_DIR / "low_term_total2_p709_source_replay_no_archive_oracle_probe.json"
DEFAULT_P716 = STATE_DIR / "low_term_total2_p716_rel2_source_generation_enrichment_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p718_cross_window_row_key_reuse_audit_probe.json"

COMPONENT_KEYS = [
    "selected_signed_pair_ops",
    "row_pool_ops",
    "selected_leaf_product_ops",
    "selected_hit_root_ops",
    "selected_leaf_check_ops",
    "selected_hit_event_ops",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def int_value(value: Any, default: int = 0) -> int:
    return p716.int_value(value, default)


def float_value(value: Any, default: float = 0.0) -> float:
    return p716.float_value(value, default)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def stable_fingerprint(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(float(numerator) / float(denominator), 8)


def compact_scout(scout: dict[str, Any]) -> dict[str, Any]:
    return {
        "distinct_unsigned_indices": int_value(scout.get("distinct_unsigned_indices")),
        "left_pos": int_value(scout.get("left_pos")),
        "left_x": int_value(scout.get("left_x")),
        "right_pos": int_value(scout.get("right_pos")),
        "right_x": int_value(scout.get("right_x")),
        "s3_c0": int_value(scout.get("s3_c0")),
        "s3_c1": int_value(scout.get("s3_c1")),
        "s3_c2": int_value(scout.get("s3_c2")),
        "s3_discriminant": int_value(scout.get("s3_discriminant")),
        "s3_root_product": int_value(scout.get("s3_root_product")),
        "s3_root_sum": int_value(scout.get("s3_root_sum")),
        "s3_vertex": int_value(scout.get("s3_vertex")),
        "scout_pos": int_value(scout.get("scout_pos")),
        "signed_terms": [[int_value(index), int_value(sign)] for index, sign in scout.get("signed_terms") or []],
        "unsigned_indices": [int_value(index) for index in scout.get("unsigned_indices") or []],
        "x_gap": int_value(scout.get("x_gap")),
        "x_sum": int_value(scout.get("x_sum")),
    }


def signed_pair_core_fingerprint(built: dict[str, Any]) -> str:
    return stable_fingerprint(
        {
            "challenge_seed": built.get("challenge_seed"),
            "scout_seed_prefix": built.get("scout_seed_prefix"),
            "signed_pair_limit": int_value(built.get("signed_pair_limit")),
            "signed_pair_selection_mode": built.get("signed_pair_selection_mode"),
            "selected_signed_pair_count": int_value(built.get("selected_signed_pair_count")),
            "scouts": [compact_scout(scout) for scout in built.get("scouts") or []],
            "target": built.get("target"),
        }
    )


def row_x_values(built: dict[str, Any]) -> set[int]:
    return {int_value(row.get("x")) for row in built.get("rows") or []}


def cost_parts(row: dict[str, Any]) -> dict[str, int]:
    parts = row.get("cost_parts") or {}
    return {key: int_value(parts.get(key)) for key in COMPONENT_KEYS}


def reconstructed_ops(row: dict[str, Any]) -> int:
    parts = row.get("cost_parts") or {}
    return int_value(parts.get("reconstructed_preassociation_filter_ops"))


def sum_component(rows: list[dict[str, Any]], component: str) -> int:
    return sum(cost_parts(row).get(component, 0) for row in rows)


def source_model(
    name: str,
    source_ops: int,
    rho: int,
    fallback_over_rho: float,
    source_window_count: int,
    admissibility: str,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source_over_rho = ratio(source_ops, rho)
    total_over_rho = round(float_value(source_over_rho) + fallback_over_rho, 8)
    return {
        "admissibility": admissibility,
        "beats_rho_marginal": bool(total_over_rho < source_window_count),
        "model": name,
        "source_charge_ops": source_ops,
        "source_charge_over_rho": source_over_rho,
        "source_plus_fallback_over_rho": total_over_rho,
        "vs_independent_rho_over_rho": source_window_count,
        **(extra or {}),
    }


def group_rows(rows: list[dict[str, Any]], key: str) -> dict[str, list[dict[str, Any]]]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        groups.setdefault(str(row.get(key)), []).append(row)
    return groups


def group_rows_by_tuple(rows: list[dict[str, Any]], keys: list[str]) -> dict[str, list[dict[str, Any]]]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        groups.setdefault(json.dumps([row.get(key) for key in keys], sort_keys=True), []).append(row)
    return groups


def charge_component_once(rows: list[dict[str, Any]], group_key: str, component: str) -> int:
    rest = sum(reconstructed_ops(row) - cost_parts(row).get(component, 0) for row in rows)
    grouped = group_rows(rows, group_key)
    charged = sum(min(cost_parts(row).get(component, 0) for row in members) for members in grouped.values())
    return rest + charged


def charge_full_once_by_groups(groups: dict[str, list[dict[str, Any]]]) -> int:
    return sum(min(reconstructed_ops(row) for row in members) for members in groups.values())


def compact_row_sample(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "attempt_index": row.get("attempt_index"),
        "challenge_seed": row.get("challenge_seed"),
        "cost_parts": row.get("cost_parts"),
        "hit": row.get("hit"),
        "row_key": row.get("row_key"),
        "row_pool_fingerprint": row.get("row_pool_fingerprint"),
        "row_seed_prefix": row.get("row_seed_prefix"),
        "scout_seed_prefix": row.get("scout_seed_prefix"),
        "selected_leaf_indices": row.get("selected_leaf_indices"),
        "selected_leaf_signature_keys": row.get("selected_leaf_signature_keys"),
        "source": row.get("source"),
        "window_start": row.get("window_start"),
    }


def reconstruct_rows(args: argparse.Namespace) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    build_args = argparse.Namespace(
        max_transfer=args.max_transfer,
        min_transfer=args.min_transfer,
        p709=args.p709,
        source_pattern=args.source_pattern,
        target=args.target,
        thresholds="0.544,0.568,0.616,1.0",
    )
    reports, metadata = p716.build_window_reports(build_args)
    policy = p716.SourcePolicy("two_by_two_any_cost_le_1p0", "two_by_two_any", 1.0)
    rows: list[dict[str, Any]] = []
    attempts: list[dict[str, Any]] = []
    for report in reports:
        accepted = [row for row in report["candidates"] if p716.policy_accepts(policy, row)]
        accepted.sort(key=p716.row_sort_key)
        if not accepted:
            continue
        candidate = accepted[0]
        source = metadata["source_cache"][str(candidate["source"])]
        verifier, contexts, product_factor, max_relations = p709.direct_source.timing_probe.selected_contexts_from_source_case(
            source,
            candidate["source_case"],
        )
        direct_rows, direct_ops, rho, row_profiles = p709.direct_source.timing_probe.direct_witness_rows(
            verifier,
            contexts,
        )
        built_by_row = {str(context["row_key"]): context["built"] for context in contexts}
        direct_union = p709.direct_source.direct_witness_probe.union_derive(
            verifier,
            direct_rows,
            built_by_row,
            "_scan",
        )
        attempt_index = len(attempts)
        attempt = {
            "attempt_index": attempt_index,
            "direct_ops": direct_ops,
            "direct_ops_over_rho": p709.direct_source.ratio(direct_ops, rho),
            "hit": bool(direct_union.get("union_public_key_verified")),
            "rank": int_value(direct_union.get("union_rank")),
            "rho": rho,
            "row": p716.sample_row(candidate, None),
            "source": str(candidate["source"]),
            "window_end": report["window_end"],
            "window_start": report["window_start"],
        }
        attempts.append(attempt)
        for context_index, (context, profile) in enumerate(zip(contexts, row_profiles)):
            built = context["built"]
            row_xs = row_x_values(built)
            scan = profile.get("scan") or {}
            parts = profile.get("cost_parts") or {}
            row = {
                "attempt_index": attempt_index,
                "challenge_seed": profile.get("challenge_seed"),
                "context_index": context_index,
                "cost_parts": parts,
                "hit": attempt["hit"],
                "rank": attempt["rank"],
                "reconstructed_preassociation_filter_ops": int_value(
                    parts.get("reconstructed_preassociation_filter_ops"),
                    int_value(scan.get("preassociation_filter_ops")),
                ),
                "rho": rho,
                "row_key": profile.get("row_key"),
                "row_pool_fingerprint": profile.get("row_pool_fingerprint"),
                "row_pool_x_count": len(row_xs),
                "row_seed_prefix": profile.get("row_seed_prefix"),
                "row_x_fingerprint": stable_fingerprint(sorted(row_xs)),
                "row_x_values": row_xs,
                "scan_relation_count": int_value(scan.get("relation_count")),
                "scout_seed_prefix": profile.get("scout_seed_prefix"),
                "selected_leaf_indices": [int_value(value) for value in profile.get("selected_leaf_indices") or []],
                "selected_leaf_signature_keys": [
                    str(value) for value in profile.get("selected_leaf_signature_keys") or []
                ],
                "selected_leaf_signature_tuple": json.dumps(
                    [str(value) for value in profile.get("selected_leaf_signature_keys") or []],
                    sort_keys=True,
                    separators=(",", ":"),
                ),
                "signed_pair_core_fingerprint": signed_pair_core_fingerprint(built),
                "source": str(candidate["source"]),
                "source_case_selector": {
                    "selector": candidate["source_case"].get("selector"),
                    "source_policy": candidate["source_case"].get("source_policy"),
                    "source_row_index": int_value(candidate["source_case"].get("source_row_index")),
                    "top_k": int_value(candidate["source_case"].get("top_k")),
                    "transfer_index": int_value(candidate["source_case"].get("transfer_index")),
                },
                "window_start": report["window_start"],
            }
            rows.append(row)
    meta = {
        "attempt_count": len(attempts),
        "candidate_window_count": sum(1 for report in reports if report["candidates"]),
        "hit_count": sum(1 for attempt in attempts if attempt["hit"]),
        "max_relations": max((int_value(attempt.get("max_relations")) for attempt in attempts), default=0),
        "product_factor": max((int_value(attempt.get("product_factor")) for attempt in attempts), default=0),
        "source_window_count": len(reports),
    }
    return rows, meta


def row_key_group_report(row_key: str, members: list[dict[str, Any]]) -> dict[str, Any]:
    row_x_union = set().union(*(member["row_x_values"] for member in members)) if members else set()
    member_count = len(members)
    challenge_count = len({member.get("challenge_seed") for member in members})
    row_pool_count = len({member.get("row_pool_fingerprint") for member in members})
    signed_core_count = len({member.get("signed_pair_core_fingerprint") for member in members})
    leaf_tuple_count = len({member.get("selected_leaf_signature_tuple") for member in members})
    scout_seed_count = len({member.get("scout_seed_prefix") for member in members})
    full_transferable = (
        member_count > 0
        and row_pool_count == 1
        and signed_core_count == 1
        and leaf_tuple_count == 1
        and challenge_count == 1
    )
    row_pool_exact_reusable = row_pool_count == 1 and member_count > 1
    signed_core_exact_reusable = signed_core_count == 1 and member_count > 1
    leaf_signature_exact_reusable = leaf_tuple_count == 1 and member_count > 1
    return {
        "challenge_seed_count": challenge_count,
        "component_ops_sum": {
            key: sum_component(members, key)
            for key in COMPONENT_KEYS
        },
        "full_row_key_transferable_under_fingerprints": full_transferable,
        "hit_context_count": sum(1 for member in members if member.get("hit")),
        "leaf_signature_exact_reusable": leaf_signature_exact_reusable,
        "member_count": member_count,
        "reconstructed_ops_sum": sum(reconstructed_ops(member) for member in members),
        "row_key": row_key,
        "row_pool_exact_reusable": row_pool_exact_reusable,
        "row_pool_fingerprint_count": row_pool_count,
        "row_pool_x_intersection_count": (
            len(set.intersection(*(member["row_x_values"] for member in members))) if member_count > 1 else len(row_x_union)
        ),
        "row_pool_x_union_count": len(row_x_union),
        "row_seed_prefix_count": len({member.get("row_seed_prefix") for member in members}),
        "sample": compact_row_sample(members[0]) if members else {},
        "scout_seed_prefix_count": scout_seed_count,
        "selected_leaf_signature_key_count": len(
            {key for member in members for key in member.get("selected_leaf_signature_keys") or []}
        ),
        "selected_leaf_signature_tuple_count": leaf_tuple_count,
        "signed_pair_core_exact_reusable": signed_core_exact_reusable,
        "signed_pair_core_fingerprint_count": signed_core_count,
        "source_count": len({member.get("source") for member in members}),
        "window_starts": sorted({int_value(member.get("window_start")) for member in members}),
    }


def signed_pair_core_group_report(core_key: str, members: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "attempt_indices": sorted({int_value(member.get("attempt_index")) for member in members}),
        "challenge_seed_count": len({member.get("challenge_seed") for member in members}),
        "component_ops_sum": {key: sum_component(members, key) for key in COMPONENT_KEYS},
        "core_fingerprint": core_key,
        "member_count": len(members),
        "reconstructed_ops_sum": sum(reconstructed_ops(member) for member in members),
        "row_keys": sorted({str(member.get("row_key")) for member in members}),
        "row_pool_fingerprint_count": len({member.get("row_pool_fingerprint") for member in members}),
        "sample": compact_row_sample(members[0]) if members else {},
        "selected_leaf_signature_tuple_count": len({member.get("selected_leaf_signature_tuple") for member in members}),
        "source_count": len({member.get("source") for member in members}),
        "window_starts": sorted({int_value(member.get("window_start")) for member in members}),
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p709_payload = load_json(Path(args.p709))
    factor_charge = float_value((p709_payload.get("parameters") or {}).get("factor_bank_charge_over_rho"), 0.992)
    rows, meta = reconstruct_rows(args)
    rhos = sorted({int_value(row.get("rho")) for row in rows if int_value(row.get("rho"))})
    rho = rhos[0] if len(rhos) == 1 else max(rhos, default=0)
    hit_count = int_value(meta.get("hit_count"))
    fallback_over_rho = float_value(meta["source_window_count"] - hit_count)
    independent_ops = sum(reconstructed_ops(row) for row in rows)
    exact_materialization_groups = group_rows_by_tuple(
        rows,
        ["row_pool_fingerprint", "signed_pair_core_fingerprint", "selected_leaf_signature_tuple"],
    )
    row_key_groups = group_rows(rows, "row_key")
    row_key_group_reports = [
        row_key_group_report(row_key, members)
        for row_key, members in sorted(row_key_groups.items(), key=lambda item: (-len(item[1]), item[0]))
    ]
    signed_pair_core_groups = group_rows(rows, "signed_pair_core_fingerprint")
    signed_pair_core_group_reports = [
        signed_pair_core_group_report(core_key, members)
        for core_key, members in sorted(signed_pair_core_groups.items(), key=lambda item: (-len(item[1]), item[0]))
    ]
    row_key_full_transferable_count = sum(
        1 for report in row_key_group_reports if report["full_row_key_transferable_under_fingerprints"]
    )
    exact_materialization_ops = charge_full_once_by_groups(exact_materialization_groups)
    exact_row_pool_ops = charge_component_once(rows, "row_pool_fingerprint", "row_pool_ops")
    exact_signed_core_ops = charge_component_once(rows, "signed_pair_core_fingerprint", "selected_signed_pair_ops")
    row_seed_row_pool_ops = charge_component_once(rows, "row_seed_prefix", "row_pool_ops")
    row_key_signed_pair_lower_bound_ops = charge_component_once(rows, "row_key", "selected_signed_pair_ops")
    row_key_full_lower_bound_ops = charge_full_once_by_groups(row_key_groups)
    models = [
        source_model(
            "independent_direct",
            independent_ops,
            rho,
            fallback_over_rho,
            meta["source_window_count"],
            "verified_individual_replay",
            {"group_count": len(rows)},
        ),
        source_model(
            "exact_materialization_reuse",
            exact_materialization_ops,
            rho,
            fallback_over_rho,
            meta["source_window_count"],
            "admissible_only_for_identical_row_pool_signed_core_and_leaf_tuple",
            {"group_count": len(exact_materialization_groups)},
        ),
        source_model(
            "exact_row_pool_fingerprint_reuse",
            exact_row_pool_ops,
            rho,
            fallback_over_rho,
            meta["source_window_count"],
            "replay_compatible_exact_row_pool_fingerprint",
            {"group_count": len(group_rows(rows, "row_pool_fingerprint"))},
        ),
        source_model(
            "exact_signed_pair_core_reuse",
            exact_signed_core_ops,
            rho,
            fallback_over_rho,
            meta["source_window_count"],
            "component_reuse_candidate_exact_scout_signed_pair_fingerprint_needs_shared_scanner",
            {"group_count": len(signed_pair_core_groups)},
        ),
        source_model(
            "row_seed_prefix_row_pool_reuse",
            row_seed_row_pool_ops,
            rho,
            fallback_over_rho,
            meta["source_window_count"],
            "heuristic_row_seed_prefix_reuse_not_exact_materialization",
            {"group_count": len(group_rows(rows, "row_seed_prefix"))},
        ),
        source_model(
            "row_key_signed_pair_full_reuse_lower_bound",
            row_key_signed_pair_lower_bound_ops,
            rho,
            fallback_over_rho,
            meta["source_window_count"],
            "optimistic_lower_bound_not_verified_signed_pair_core_changes",
            {"group_count": len(row_key_groups)},
        ),
        source_model(
            "global_row_key_full_reuse_lower_bound",
            row_key_full_lower_bound_ops,
            rho,
            fallback_over_rho,
            meta["source_window_count"],
            "optimistic_lower_bound_not_verified",
            {"group_count": len(row_key_groups)},
        ),
    ]
    strict_admissible_models = [
        model
        for model in models
        if model["model"]
        in {
            "exact_materialization_reuse",
            "exact_row_pool_fingerprint_reuse",
        }
    ]
    component_candidate_models = [
        model for model in models if model["model"] in {"exact_signed_pair_core_reuse"}
    ]
    lower_bound_models = [
        model
        for model in models
        if model["model"] in {"row_key_signed_pair_full_reuse_lower_bound", "global_row_key_full_reuse_lower_bound"}
    ]
    if any(model["beats_rho_marginal"] for model in strict_admissible_models):
        claim_status = "P718_ADMISSIBLE_FULL_MATERIALIZATION_REUSE_BEATS_RHO"
    elif any(model["beats_rho_marginal"] for model in component_candidate_models):
        claim_status = "P718_SIGNED_PAIR_CORE_REUSE_BEATS_RHO_BUT_ROWKEY_CROSSWINDOW_NEGATIVE"
    elif row_key_full_transferable_count:
        claim_status = "P718_PARTIAL_ROW_KEY_TRANSFERABILITY_NEEDS_REPLAY"
    elif any(model["beats_rho_marginal"] for model in lower_bound_models):
        claim_status = "NEGATIVE_RESULT_P718_ROW_KEY_LABEL_NOT_TRANSFERABLE_LOWER_BOUND_ONLY"
    else:
        claim_status = "NEGATIVE_RESULT_P718_NO_ROW_KEY_REUSE_ADVANTAGE"
    component_totals = {key: sum_component(rows, key) for key in COMPONENT_KEYS}
    summary = {
        "attempt_count": meta["attempt_count"],
        "component_reuse_candidate_beats_rho_count": sum(
            1 for model in component_candidate_models if model["beats_rho_marginal"]
        ),
        "component_ops": component_totals,
        "component_ops_over_rho": {key: ratio(value, rho) for key, value in component_totals.items()},
        "exact_materialization_group_count": len(exact_materialization_groups),
        "factor_bank_charge_over_rho": factor_charge,
        "fallback_charge_over_rho": fallback_over_rho,
        "hit_count": hit_count,
        "independent_source_charge_ops": independent_ops,
        "independent_source_charge_over_rho": ratio(independent_ops, rho),
        "new_bank_source_threshold_over_rho": round(hit_count - factor_charge, 8),
        "rho": rho,
        "rho_baseline_over_rho": meta["source_window_count"],
        "row_context_count": len(rows),
        "row_key_count": len(row_key_groups),
        "row_key_full_transferable_group_count": row_key_full_transferable_count,
        "row_key_groups_with_all_distinct_materializations": sum(
            1
            for report in row_key_group_reports
            if report["member_count"]
            == report["challenge_seed_count"]
            == report["row_pool_fingerprint_count"]
            == report["signed_pair_core_fingerprint_count"]
            == report["selected_leaf_signature_tuple_count"]
        ),
        "row_pool_fingerprint_count": len(group_rows(rows, "row_pool_fingerprint")),
        "row_seed_prefix_count": len(group_rows(rows, "row_seed_prefix")),
        "scout_seed_prefix_count": len(group_rows(rows, "scout_seed_prefix")),
        "selected_leaf_signature_tuple_count": len(group_rows(rows, "selected_leaf_signature_tuple")),
        "signed_pair_core_fingerprint_count": len(group_rows(rows, "signed_pair_core_fingerprint")),
        "source_threshold_over_rho": hit_count,
        "source_window_count": meta["source_window_count"],
        "strict_admissible_model_beats_rho_count": sum(
            1 for model in strict_admissible_models if model["beats_rho_marginal"]
        ),
        "unique_rhos": rhos,
    }
    return {
        "artifacts": {
            "p709": str(Path(args.p709)),
            "p716": str(Path(args.p716)),
            "p717": str(p717.DEFAULT_OUT),
        },
        "claim_status": claim_status,
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: archived source-generator stress rows outside the P709 source map, not live fresh harvesting.",
            "A repeated row_key is treated as reusable only if materialized row-pool, signed-pair/scout, and selected leaf-signature fingerprints also match.",
            "Row-key signed-pair and full-row-key reuse models are lower bounds unless a replay primitive proves cross-window transferability.",
            "NO DEPLOYED-CURVE CLAIM: sparse linear algebra, target descent, and large-prime scaling remain open.",
        ],
        "method": "p718_cross_window_row_key_reuse_audit",
        "parameters": {
            "max_transfer": int_value(args.max_transfer),
            "min_transfer": int_value(args.min_transfer),
            "policy": "two_by_two_any_cost_le_1p0:budget1",
            "source_pattern": args.source_pattern,
            "target": args.target,
        },
        "reuse_models": models,
        "row_key_group_reports": row_key_group_reports,
        "schema": "ecdlp.low_term_total2_p718_cross_window_row_key_reuse_audit.v1",
        "signed_pair_core_group_reports": signed_pair_core_group_reports,
        "summary": summary,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-transfer", type=int, default=20807)
    parser.add_argument("--min-transfer", type=int, default=20232)
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    parser.add_argument("--p709", default=str(DEFAULT_P709))
    parser.add_argument("--p716", default=str(DEFAULT_P716))
    parser.add_argument("--source-pattern", default=p716.p712.SOURCE_PATTERN)
    parser.add_argument("--target", default="67.a1@9803")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    print(json.dumps({"claim_status": payload["claim_status"], "summary": payload["summary"]}, indent=2, sort_keys=True))
    print(json.dumps({"reuse_models": payload["reuse_models"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
