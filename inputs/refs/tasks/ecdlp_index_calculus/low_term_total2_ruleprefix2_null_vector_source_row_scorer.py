#!/usr/bin/env python3
"""Score source rows for ruleprefix2 null-vector preservation before replay.

The source-enrichment diagnostics found that many public leaves can be
verified or below rho without preserving the residual nullspace direction used
by the ruleprefix2 replay gate.  This scorer inspects the selected leaves in
source rows directly and ranks rows that combine:

* below-rho public source evidence;
* nonzero projection onto the configured null vector;
* explicit contact with the free column.

It does not export relation certificates and does not promote anything by
itself.  It is a source-generation diagnostic for deciding what to replay next.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_shared_challenge_salt_neighborhood_low_term_total2_ffe_hit_stream_probe as hit_stream_probe
import low_term_total2_nullspace_asymmetric_leaf_scout as null_scout
import low_term_total2_public_prefix_shared_leaf_repair_probe as repair_probe
import low_term_total2_ruleprefix2_source_enrichment_diagnostic as enrich
import low_term_total2_target_eliminated_factor_relation_bank as factor_bank
import low_term_total2_nullspace_projection_obstruction_scout as obstruction


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def int_value(value: Any, default: int = 0) -> int:
    return factor_bank.int_value(value, default)


def float_value(value: Any) -> float | None:
    return enrich.float_value(value)


def parse_csv(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [item.strip() for item in raw.split(",") if item.strip()]


def parse_int_csv(raw: str | None) -> set[int]:
    return {int(item) for item in parse_csv(raw)}


def parse_null_vector(raw: str) -> list[int]:
    return [int(item.strip()) for item in str(raw).split(",") if item.strip()]


def source_label(path: Path) -> str:
    return enrich.window_from_source(path) or path.stem


def source_policy_summary(source: dict[str, Any], policy_name: str) -> dict[str, Any]:
    for row in (source.get("summary") or {}).get("policy_summaries") or []:
        if isinstance(row, dict) and str(row.get("policy")) == str(policy_name):
            return row
    return {}


def source_enrichment_score(policy: dict[str, Any]) -> int:
    row = {
        "stress_leaf_below_rho": int_value(policy.get("stress_leaf_below_rho")),
        "stress_leaf_best_ops_over_rho": float_value(policy.get("stress_leaf_best_ops_over_rho")),
        "stress_leaf_verified": int_value(policy.get("stress_leaf_verified")),
        "stress_row_below_rho": int_value(policy.get("stress_row_below_rho")),
        "stress_row_verified": int_value(policy.get("stress_row_verified")),
    }
    return enrich.enrichment_score(row)


def row_context(context: dict[str, Any], row_key: str) -> dict[str, Any]:
    return {
        "built": context["built_by_row"][row_key],
        "components": context["components_by_row"][row_key],
    }


def selected_leaf_profiles(
    context: dict[str, Any],
    source_row: dict[str, Any],
    null_vector: list[int],
    order: int,
    free_column: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    profiles: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for item in source_row.get("row_leaf_keys") or []:
        if not isinstance(item, dict):
            continue
        row_key = str(item.get("row_key"))
        try:
            ctx = row_context(context, row_key)
        except KeyError as error:
            errors.append({"error": f"missing row context: {error}", "row_key": row_key})
            continue
        for leaf_index in item.get("leaf_indices") or []:
            try:
                profile = null_scout.leaf_null_profile(
                    ctx,
                    int_value(leaf_index),
                    null_vector,
                    order,
                    free_column,
                )
                profile["row_key"] = row_key
                profiles.append(profile)
            except Exception as error:  # Preserve bad leaf references for audit.
                errors.append(
                    {
                        "error": str(error),
                        "leaf_index": int_value(leaf_index),
                        "row_key": row_key,
                    }
                )
    return profiles, errors


def aggregate_profiles(
    profiles: list[dict[str, Any]],
    *,
    order: int,
    free_column: int,
) -> dict[str, Any]:
    projection_mod = 0
    support: set[int] = set()
    null_support: set[int] = set()
    free_term_count = 0
    free_minus_opposite = 0
    signed_charge = 0
    for profile in profiles:
        projection_mod = (projection_mod + (int_value(profile.get("projection_signed")) % order)) % order
        support.update(int_value(item) for item in profile.get("support") or [])
        null_support.update(int_value(item) for item in profile.get("null_support") or [])
        free_term_count += int_value(profile.get("free_term_count"))
        free_minus_opposite += int_value(profile.get("free_minus_opposite_term_count"))
        signed_charge += int_value(profile.get("signed_charge"))
    projection_signed = obstruction.signed(projection_mod, order)
    return {
        "abs_projection_signed": abs(projection_signed),
        "free_minus_opposite_term_count": free_minus_opposite,
        "free_term_count": free_term_count,
        "has_nonzero_projection": projection_signed != 0,
        "leaf_count": len(profiles),
        "null_support": sorted(null_support),
        "null_support_size": len(null_support),
        "projection_signed": projection_signed,
        "signed_charge": signed_charge,
        "support": sorted(support),
        "support_size": len(support),
        "touches_free_column": free_column in support or free_term_count > 0,
    }


def source_row_score(row: dict[str, Any]) -> int:
    score = 0
    if row.get("below_rho"):
        score += 3
    if row.get("has_nonzero_projection"):
        score += 3
    if row.get("touches_free_column"):
        score += 3
    if int_value(row.get("free_term_count")) > 1:
        score += 1
    if int_value(row.get("rank")) > 0:
        score += 1
    if row.get("public_key_verified"):
        score += 2
    if float_value(row.get("ops_over_rho")) is not None and float(row["ops_over_rho"]) <= 0.7:
        score += 1
    if int_value(row.get("source_enrichment_score")) >= 4:
        score += 1
    return score


def status(row: dict[str, Any]) -> str:
    if row.get("below_rho") and row.get("has_nonzero_projection") and row.get("touches_free_column"):
        return "BELOW_RHO_NULL_FREE_SIGNAL"
    if row.get("below_rho") and row.get("has_nonzero_projection"):
        return "BELOW_RHO_NULL_NONZERO_NO_FREE"
    if row.get("below_rho") and row.get("touches_free_column"):
        return "BELOW_RHO_FREE_ZERO_PROJECTION"
    if row.get("below_rho"):
        return "BELOW_RHO_NO_NULL_SIGNAL"
    if row.get("has_nonzero_projection") and row.get("touches_free_column"):
        return "NULL_FREE_ABOVE_RHO_SIGNAL"
    return "NO_SIGNAL"


def compact_profile(profile: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "row_key",
        "leaf_index",
        "projection_signed",
        "abs_projection_signed",
        "free_term_count",
        "free_minus_opposite_term_count",
        "null_support",
        "support",
        "signed_charge",
    )
    return {key: profile.get(key) for key in keys}


def compact_row(row: dict[str, Any], profile_limit: int) -> dict[str, Any]:
    keys = (
        "source_label",
        "transfer_index",
        "target",
        "top_k",
        "source_policy",
        "row_selector",
        "row_keys",
        "row_leaf_keys",
        "selector",
        "ops_over_rho",
        "below_rho",
        "public_key_verified",
        "rank",
        "relation_count",
        "signal_status",
        "signal_score",
        "source_enrichment_score",
        "projection_signed",
        "abs_projection_signed",
        "free_term_count",
        "free_minus_opposite_term_count",
        "has_nonzero_projection",
        "touches_free_column",
        "null_support",
        "support",
        "source_path",
    )
    out = {key: row.get(key) for key in keys}
    out["leaf_profiles"] = [compact_profile(profile) for profile in row.get("leaf_profiles", [])[:profile_limit]]
    return out


def build_context(
    verifier: Any,
    records: list[dict[str, Any]],
    config_source: dict[str, Any],
    specs_by_target: dict[str, dict[str, dict[str, Any]]],
    probe_args: argparse.Namespace,
    pair: dict[str, Any],
    context_cache: dict[tuple[str, int, int, tuple[str, ...]], dict[str, Any]],
) -> dict[str, Any]:
    seed_case = {
        "target": pair["target"],
        "transfer_index": pair["transfer_index"],
        "top_k": pair["top_k"],
        "row_leaf_keys": [{"row_key": row_key, "leaf_indices": [0]} for row_key in pair["row_keys"]],
    }
    return hit_stream_probe.scan_case_context(
        verifier,
        records,
        config_source,
        specs_by_target,
        seed_case,
        probe_args,
        context_cache,
    )


def score_source(
    source_path: Path,
    args: argparse.Namespace,
    null_vector: list[int],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    source = enrich.load_json(source_path)
    params = repair_probe.source_parameters(source)
    probe_args = repair_probe.probe_args_from_source(source)
    verifier, records, config_source, specs_by_target = repair_probe.build_specs(params)
    targets = set(parse_csv(args.targets))
    transfers = parse_int_csv(args.transfers)
    pairs = repair_probe.iter_source_pairs(source, targets, transfers)
    if args.max_pairs_per_source >= 0:
        pairs = pairs[: args.max_pairs_per_source]
    context_cache: dict[tuple[str, int, int, tuple[str, ...]], dict[str, Any]] = {}
    rows: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for pair in pairs:
        try:
            context = build_context(
                verifier,
                records,
                config_source,
                specs_by_target,
                probe_args,
                pair,
                context_cache,
            )
        except Exception as error:
            errors.append(
                {
                    "error": str(error),
                    "source_path": str(source_path),
                    "target": pair.get("target"),
                    "top_k": pair.get("top_k"),
                    "transfer_index": pair.get("transfer_index"),
                }
            )
            continue
        policy_summary = source_policy_summary(source, str(pair.get("source_policy")))
        enrichment_score = source_enrichment_score(policy_summary)
        for source_row in pair.get("source_rows") or []:
            profiles, profile_errors = selected_leaf_profiles(
                context,
                source_row,
                null_vector,
                int_value(args.order, 11779),
                int_value(args.free_column, 6),
            )
            aggregate = aggregate_profiles(
                profiles,
                order=int_value(args.order, 11779),
                free_column=int_value(args.free_column, 6),
            )
            row = {
                **aggregate,
                "below_rho": bool(source_row.get("below_rho")),
                "ops_over_rho": source_row.get("ops_over_rho"),
                "public_key_verified": bool(source_row.get("public_key_verified")),
                "rank": int_value(source_row.get("rank")),
                "relation_count": int_value(source_row.get("relation_count")),
                "row_selector": pair.get("row_selector"),
                "row_keys": pair.get("row_keys") or [],
                "row_leaf_keys": source_row.get("row_leaf_keys") or [],
                "selector": source_row.get("selector"),
                "source_enrichment_score": enrichment_score,
                "source_label": source_label(source_path),
                "source_path": str(source_path),
                "source_policy": pair.get("source_policy"),
                "target": pair.get("target"),
                "top_k": int_value(pair.get("top_k")),
                "transfer_index": int_value(pair.get("transfer_index")),
                "leaf_profiles": profiles,
            }
            row["signal_score"] = source_row_score(row)
            row["signal_status"] = status(row)
            rows.append(row)
            for error in profile_errors:
                errors.append({**error, "source_path": str(source_path), "source_label": source_label(source_path)})
    return rows, errors


def summarize(rows: list[dict[str, Any]], errors: list[dict[str, Any]]) -> dict[str, Any]:
    statuses = Counter(str(row.get("signal_status")) for row in rows)
    below_null_free = statuses.get("BELOW_RHO_NULL_FREE_SIGNAL", 0)
    return {
        "below_rho_null_free_signal_count": below_null_free,
        "error_count": len(errors),
        "max_signal_score": max((int_value(row.get("signal_score")) for row in rows), default=None),
        "source_count": len({row.get("source_path") for row in rows}),
        "source_row_count": len(rows),
        "status_counts": dict(sorted(statuses.items())),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-glob", required=True)
    parser.add_argument("--targets", default="22050.cf1@11731")
    parser.add_argument("--transfers", default="")
    parser.add_argument("--order", type=int, default=11779)
    parser.add_argument("--free-column", type=int, default=6)
    parser.add_argument("--null-vector", default="1,1,11778,1,1,11778,1,0,0,0,0,0,0,0,0,0")
    parser.add_argument("--max-pairs-per-source", type=int, default=16)
    parser.add_argument("--profile-limit", type=int, default=6)
    parser.add_argument("--top-limit", type=int, default=80)
    parser.add_argument("--out", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    null_vector = parse_null_vector(args.null_vector)
    rows: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    missing_sources: list[str] = []
    for source_path in enrich.parse_paths(args.source_glob):
        if not source_path.exists():
            missing_sources.append(str(source_path))
            continue
        source_rows, source_errors = score_source(source_path, args, null_vector)
        rows.extend(source_rows)
        errors.extend(source_errors)
    rows.sort(
        key=lambda row: (
            -int_value(row.get("signal_score")),
            row.get("signal_status") != "BELOW_RHO_NULL_FREE_SIGNAL",
            -int_value(row.get("source_enrichment_score")),
            -int_value(row.get("rank")),
            float(row.get("ops_over_rho") if row.get("ops_over_rho") is not None else 10**9),
            str(row.get("source_label")),
            int_value(row.get("transfer_index")),
            str(row.get("selector")),
        )
    )
    payload = {
        "schema": "ecdlp.low_term_total2_ruleprefix2_null_vector_source_row_scorer.v1",
        "created_at": now_iso(),
        "honesty_boundary": {
            "HEURISTIC": True,
            "TOY_EVIDENCE": True,
            "MODEL_BOUND": True,
            "pre_replay_source_rows_only": True,
            "not_a_relation_certificate": True,
            "not_target_descent": True,
            "not_faster_than_rho_claim": True,
        },
        "inputs": {
            "free_column": args.free_column,
            "max_pairs_per_source": args.max_pairs_per_source,
            "missing_sources": missing_sources,
            "null_vector": null_vector,
            "order": args.order,
            "source_glob": args.source_glob,
            "targets": parse_csv(args.targets),
            "transfers": sorted(parse_int_csv(args.transfers)),
        },
        "summary": summarize(rows, errors),
        "top_rows": [compact_row(row, args.profile_limit) for row in rows[: args.top_limit]],
        "rows": [compact_row(row, args.profile_limit) for row in rows],
        "errors": errors[:200],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    print(json.dumps({"top_rows": payload["top_rows"][:5]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
