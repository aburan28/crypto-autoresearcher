#!/usr/bin/env python3
"""Search public leaf-prefix repairs for low-term total-2 source near misses.

The fixed expanded-leaf source gate can emit source-verified row pairs whose
current selected leaves do not derive the public key.  This diagnostic asks a
strictly local repair question:

* can a public leaf prefix on the same row pair derive the scalar?
* if both rows use the same selected leaf polynomials, does sharing the leaf
  prefix once close the Pollard-rho gap?

The shared-prefix accounting is model-bound.  It charges the existing direct
row scans exactly, then subtracts only duplicate selected-leaf checks when the
selected leaf polynomials are identical across rows.  It does not claim a full
solver or a deployed shared kernel.
"""

from __future__ import annotations

import argparse
import json
from argparse import Namespace
from collections import Counter
from pathlib import Path
from typing import Any

import frontier_signed_eval_cover_preassociation_filter_probe as prefilter_probe
import frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_shared_challenge_direct_witness_probe as direct_witness_probe
import frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_shared_challenge_salt_neighborhood_compress_probe as compress_probe
import frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_shared_challenge_salt_neighborhood_loto_leaf_trim_probe as leaf_trim_probe
import frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_shared_challenge_salt_neighborhood_low_term_total2_ffe_hit_stream_probe as hit_stream_probe
import frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_shared_challenge_salt_neighborhood_transfer_probe as transfer_probe
import relation_probe


DEFAULT_STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_SOURCE = (
    DEFAULT_STATE_DIR
    / "frontier_public_leaf_policy_low_term_total2_fixed_row_1152_1159_expanded_probe.json"
)
DEFAULT_OUT = (
    DEFAULT_STATE_DIR
    / "low_term_total2_public_prefix_shared_leaf_repair_1152_1159_probe.json"
)
DEFAULT_MODES = (
    "low_leaf_index",
    "low_term_support",
    "low_term_span",
    "low_monic_b",
    "low_monic_c",
    "hybrid_support_monic_b",
    "double_pair_first",
    "high_shape_concentration",
    "pool_order",
    "hash_leaf",
)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def parse_csv(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [part.strip() for part in raw.split(",") if part.strip()]


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def ratio(numerator: int, denominator: int) -> float | None:
    if not denominator:
        return None
    return round(numerator / denominator, 8)


def probe_args_from_source(source: dict[str, Any]) -> Namespace:
    params = source.get("parameters") or {}
    return Namespace(
        row_pool=int_value(params.get("row_pool"), 512),
        row_count=128,
        scout_limit=int_value(params.get("scout_limit"), 192),
        scout_mode=str(params.get("scout_mode") or "s3_coeff_spread"),
        scout_order=str(params.get("scout_order") or "eval_cover_hits_high"),
        selected_limit=int_value(params.get("selected_limit"), 64),
        factor_base_size=int_value(params.get("factor_base_size"), 16),
        max_relations=96,
        min_distinct_indices=4,
        min_unsigned_distinct_indices=2,
        require_unit_coefficients=True,
        row_factor=512,
        product_factor=4096,
        seed=str(params.get("seed") or "ecdlp-frontier-signed-dual-sieve-v1"),
    )


def source_parameters(source: dict[str, Any]) -> dict[str, Any]:
    params = source.get("parameters")
    if not isinstance(params, dict):
        raise ValueError("source artifact has no parameters object")
    return params


def build_specs(params: dict[str, Any]) -> tuple[Any, list[dict[str, Any]], dict[str, Any], dict[str, dict[str, dict[str, Any]]]]:
    verifier = relation_probe.load_verifier_module()
    records = verifier.load_records()
    bank = load_json(Path(params["bank_source"]))
    config_source = load_json(Path(params["config_source"]))
    direct_source = load_json(Path(params["direct_source"]))
    transfer_source = load_json(Path(params["transfer_source"]))
    transfer_params = transfer_source.get("parameters") if isinstance(transfer_source, dict) else {}
    radius = int_value(params.get("radius"), int_value((transfer_params or {}).get("radius"), 4))
    bank_rows = {
        compress_probe.row_key(row): row
        for row in bank.get("bank_rows") or []
        if isinstance(row, dict) and compress_probe.row_key(row)
    }
    specs_by_target = leaf_trim_probe.specs_by_target_and_key(
        transfer_probe.witness_specs(direct_source, bank_rows, radius)
    )
    return verifier, records, config_source, specs_by_target


def iter_source_pairs(
    source: dict[str, Any],
    targets: set[str],
    transfers: set[int],
) -> list[dict[str, Any]]:
    pairs: dict[tuple[str, int, int, tuple[str, ...]], dict[str, Any]] = {}
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
            rows = hit_stream_probe.unique_row_leaf_keys(row)
            if len(rows) != 2:
                continue
            row_keys = tuple(sorted(str(item["row_key"]) for item in rows))
            key = (target, transfer, int_value(row.get("top_k")), row_keys)
            entry = pairs.setdefault(
                key,
                {
                    "target": target,
                    "transfer_index": transfer,
                    "top_k": int_value(row.get("top_k")),
                    "row_keys": list(row_keys),
                    "source_policy": str(policy_name),
                    "row_selector": row.get("row_selector") or row_selector,
                    "source_rows": [],
                },
            )
            entry["source_rows"].append(
                {
                    "selector": row.get("selector"),
                    "ops_over_rho": row.get("ops_over_rho"),
                    "rank": row.get("rank"),
                    "relation_count": row.get("relation_count"),
                    "public_key_verified": bool(row.get("public_key_verified")),
                    "below_rho": bool(row.get("below_rho")),
                    "row_leaf_keys": rows,
                }
            )
    return sorted(
        pairs.values(),
        key=lambda row: (
            str(row["target"]),
            int(row["transfer_index"]),
            int(row["top_k"]),
            tuple(row["row_keys"]),
        ),
    )


def ranked_leaf_indices(
    feature_rows: list[dict[str, Any]],
    mode: str,
    seed: str,
) -> list[int]:
    ranked = sorted(feature_rows, key=lambda row: prefilter_probe.score_key(row, mode, seed))
    return [int(row["leaf_index"]) for row in ranked if row.get("leaf_index") is not None]


def selected_leaf_fingerprints(
    context: dict[str, Any],
    row_keys: list[str],
    leaf_indices: list[int],
) -> dict[str, Any]:
    per_leaf: dict[str, list[dict[str, Any]]] = {}
    identical = True
    for leaf_index in leaf_indices:
        rows = []
        for row_key in row_keys:
            components = context["components_by_row"].get(row_key)
            if not components or leaf_index >= len(components.get("leaves") or []):
                identical = False
                rows.append({"row_key": row_key, "leaf_index": leaf_index, "error": "missing_leaf"})
                continue
            leaf = components["leaves"][leaf_index]
            rows.append(
                {
                    "row_key": row_key,
                    "leaf_index": leaf_index,
                    "poly": [int(coeff) for coeff in leaf.get("poly") or []],
                    "scout_positions": [int(pos) for pos in leaf.get("scout_positions") or []],
                }
            )
        polys = {tuple(row.get("poly") or []) for row in rows if "poly" in row}
        if len(polys) != 1 or len(rows) != len(row_keys):
            identical = False
        per_leaf[str(leaf_index)] = rows
    return {
        "identical_selected_leaf_polynomials": identical,
        "selected_leaf_polynomials": per_leaf,
    }


def compact_scan(scan: dict[str, Any]) -> dict[str, Any]:
    keep = (
        "selected_leaf_indices",
        "selected_leaf_count",
        "selected_hit_roots",
        "selected_hit_events",
        "candidate_verifications",
        "relation_count",
        "rank",
        "row_public_key_verified",
        "derived_secret",
        "preassociation_filter_ops",
        "preassociation_filter_ops_over_rho",
    )
    return {key: scan.get(key) for key in keep}


def evaluate_selection(
    verifier: Any,
    records: list[dict[str, Any]],
    config_source: dict[str, Any],
    specs_by_target: dict[str, dict[str, dict[str, Any]]],
    args: Namespace,
    context_cache: dict[tuple[str, int, int, tuple[str, ...]], dict[str, Any]],
    pair: dict[str, Any],
    label: str,
    row_leaf_map: dict[str, set[int]],
) -> dict[str, Any] | None:
    case = {
        "target": pair["target"],
        "transfer_index": pair["transfer_index"],
        "top_k": pair["top_k"],
        "row_leaf_keys": [
            {"row_key": row_key, "leaf_indices": sorted(leaves)}
            for row_key, leaves in sorted(row_leaf_map.items())
        ],
    }
    context = hit_stream_probe.scan_case_context(
        verifier,
        records,
        config_source,
        specs_by_target,
        case,
        args,
        context_cache,
    )
    rows_for_union = []
    built_for_union = {}
    row_results = []
    direct_ops = 0
    generic_rho = 0
    for item in hit_stream_probe.unique_row_leaf_keys(case):
        row_key = str(item["row_key"])
        if row_key not in context["built_by_row"]:
            return None
        scan = direct_witness_probe.scan_selected(
            verifier,
            context["built_by_row"][row_key],
            context["components_by_row"][row_key],
            {int(leaf) for leaf in item["leaf_indices"]},
            context["local_args_by_row"][row_key],
        )
        rows_for_union.append({"row_key": row_key, "_scan": scan})
        built_for_union[row_key] = context["built_by_row"][row_key]
        direct_ops += int_value(scan.get("preassociation_filter_ops"))
        generic_rho = max(generic_rho, int_value(context["built_by_row"][row_key].get("generic_rho_steps")))
        row_results.append({"row_key": row_key, **compact_scan(scan)})
    union = direct_witness_probe.union_derive(verifier, rows_for_union, built_for_union, "_scan")
    selected_lists = [tuple(sorted(leaves)) for leaves in row_leaf_map.values()]
    same_leaf_indices = bool(selected_lists and len(set(selected_lists)) == 1)
    fingerprint = selected_leaf_fingerprints(
        context,
        sorted(row_leaf_map),
        list(selected_lists[0]) if same_leaf_indices else [],
    )
    shared_leaf_saving = 0
    if same_leaf_indices and fingerprint["identical_selected_leaf_polynomials"]:
        shared_leaf_saving = len(selected_lists[0]) * max(0, len(selected_lists) - 1)
    shared_ops = direct_ops - shared_leaf_saving
    return {
        "label": label,
        "target": pair["target"],
        "transfer_index": int(pair["transfer_index"]),
        "top_k": int(pair["top_k"]),
        "row_keys": sorted(row_leaf_map),
        "selected_leaf_indices_by_row": {
            row_key: sorted(leaves) for row_key, leaves in sorted(row_leaf_map.items())
        },
        "same_leaf_indices": same_leaf_indices,
        "identical_selected_leaf_polynomials": bool(
            fingerprint["identical_selected_leaf_polynomials"]
        ),
        "selected_leaf_polynomials": fingerprint["selected_leaf_polynomials"],
        "direct_ops": direct_ops,
        "generic_rho_steps": generic_rho,
        "direct_ops_over_rho": ratio(direct_ops, generic_rho),
        "direct_below_rho": bool(direct_ops < generic_rho),
        "shared_leaf_saving_ops": shared_leaf_saving,
        "shared_leaf_prefix_ops": shared_ops,
        "shared_leaf_prefix_ops_over_rho": ratio(shared_ops, generic_rho),
        "shared_leaf_prefix_below_rho": bool(shared_ops < generic_rho),
        "union_public_key_verified": bool(union.get("union_public_key_verified")),
        "union_derived_secret": union.get("union_derived_secret"),
        "union_rank": int_value(union.get("union_rank")),
        "union_relation_count": int_value(union.get("union_relation_count")),
        "row_results": row_results,
        "claim_boundary": (
            "Direct verifier replay is measured. Shared-prefix cost is MODEL-BOUND "
            "and only subtracts duplicate selected-leaf checks when row leaf "
            "polynomials are identical."
        ),
    }


def scalar_group_key(row: dict[str, Any]) -> tuple[Any, ...]:
    return (
        str(row.get("target")),
        int_value(row.get("transfer_index")),
        tuple(str(key) for key in row.get("row_keys") or []),
        str(row.get("union_derived_secret")),
    )


def unique_by_scalar_group(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    best: dict[tuple[Any, ...], dict[str, Any]] = {}
    for row in rows:
        key = scalar_group_key(row)
        old = best.get(key)
        if old is None or (
            float(row.get("direct_ops_over_rho") or 10**18),
            float(row.get("shared_leaf_prefix_ops_over_rho") or 10**18),
            str(row.get("label")),
        ) < (
            float(old.get("direct_ops_over_rho") or 10**18),
            float(old.get("shared_leaf_prefix_ops_over_rho") or 10**18),
            str(old.get("label")),
        ):
            best[key] = row
    return sorted(
        best.values(),
        key=lambda row: (
            str(row.get("target")),
            int_value(row.get("transfer_index")),
            tuple(str(key) for key in row.get("row_keys") or []),
            str(row.get("union_derived_secret")),
        ),
    )


def summarize(results: list[dict[str, Any]], pairs: list[dict[str, Any]], modes: list[str]) -> dict[str, Any]:
    verified = [row for row in results if row.get("union_public_key_verified")]
    direct_below = [row for row in verified if row.get("direct_below_rho")]
    shared_below = [row for row in verified if row.get("shared_leaf_prefix_below_rho")]
    unique_verified = unique_by_scalar_group(verified)
    unique_direct_below = unique_by_scalar_group(direct_below)
    unique_shared_below = unique_by_scalar_group(shared_below)
    best_direct = sorted(
        unique_verified,
        key=lambda row: (
            float(row.get("direct_ops_over_rho") or 10**18),
            str(row.get("label")),
        ),
    )[:8]
    best_shared = sorted(
        unique_shared_below,
        key=lambda row: (
            float(row.get("shared_leaf_prefix_ops_over_rho") or 10**18),
            float(row.get("direct_ops_over_rho") or 10**18),
            str(row.get("label")),
        ),
    )[:8]
    return {
        "pair_count": len(pairs),
        "tested_selection_count": len(results),
        "mode_count": len(modes),
        "verified_selection_count": len(verified),
        "direct_below_rho_verified_count": len(direct_below),
        "shared_leaf_prefix_below_rho_verified_count": len(shared_below),
        "unique_verified_scalar_group_count": len(unique_verified),
        "unique_direct_below_rho_scalar_group_count": len(unique_direct_below),
        "unique_shared_leaf_prefix_below_rho_scalar_group_count": len(unique_shared_below),
        "unique_direct_below_target_counts": dict(
            Counter(str(row.get("target")) for row in unique_direct_below).most_common()
        ),
        "unique_shared_below_target_counts": dict(
            Counter(str(row.get("target")) for row in unique_shared_below).most_common()
        ),
        "raw_shared_below_target_counts": dict(
            Counter(str(row.get("target")) for row in shared_below).most_common()
        ),
        "best_direct_verified": [
            {
                key: row.get(key)
                for key in (
                    "label",
                    "target",
                    "transfer_index",
                    "row_keys",
                    "direct_ops",
                    "generic_rho_steps",
                    "direct_ops_over_rho",
                    "union_derived_secret",
                    "union_rank",
                    "union_relation_count",
                )
            }
            for row in best_direct
        ],
        "best_shared_leaf_prefix_verified": [
            {
                key: row.get(key)
                for key in (
                    "label",
                    "target",
                    "transfer_index",
                    "row_keys",
                    "direct_ops",
                    "shared_leaf_saving_ops",
                    "shared_leaf_prefix_ops",
                    "generic_rho_steps",
                    "shared_leaf_prefix_ops_over_rho",
                    "union_derived_secret",
                    "union_rank",
                    "union_relation_count",
                )
            }
            for row in best_shared
        ],
        "claim_status": (
            "MODEL-BOUND POSITIVE SIGNAL if shared_leaf_prefix_below_rho_verified_count > 0; "
            "direct verifier-backed scalar recovery is measured, while shared-prefix "
            "reuse is a conservative cost model requiring a measured kernel replay."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--targets", default="")
    parser.add_argument("--transfers", default="")
    parser.add_argument("--modes", default=",".join(DEFAULT_MODES))
    parser.add_argument("--max-prefix", type=int, default=12)
    parser.add_argument("--include-leaf0-plus", action="store_true")
    args = parser.parse_args()

    source = load_json(args.source)
    params = source_parameters(source)
    probe_args = probe_args_from_source(source)
    targets = set(parse_csv(args.targets))
    transfers = {int(part) for part in parse_csv(args.transfers)}
    modes = parse_csv(args.modes) or list(DEFAULT_MODES)
    verifier, records, config_source, specs_by_target = build_specs(params)
    pairs = iter_source_pairs(source, targets, transfers)
    context_cache: dict[tuple[str, int, int, tuple[str, ...]], dict[str, Any]] = {}
    results: list[dict[str, Any]] = []

    for pair in pairs:
        seed_case = {
            "target": pair["target"],
            "transfer_index": pair["transfer_index"],
            "top_k": pair["top_k"],
            "row_leaf_keys": [{"row_key": row_key, "leaf_indices": [0]} for row_key in pair["row_keys"]],
        }
        context = hit_stream_probe.scan_case_context(
            verifier,
            records,
            config_source,
            specs_by_target,
            seed_case,
            probe_args,
            context_cache,
        )
        for mode in modes:
            rankings: dict[str, list[int]] = {}
            for row_key in pair["row_keys"]:
                feature_rows = context["feature_rows_by_row"].get(row_key, [])
                try:
                    rankings[row_key] = ranked_leaf_indices(
                        feature_rows,
                        mode,
                        f"{probe_args.seed}:{pair['target']}:{mode}",
                    )
                except ValueError:
                    rankings = {}
                    break
            if len(rankings) != len(pair["row_keys"]):
                continue
            for prefix in range(1, max(1, args.max_prefix) + 1):
                row_leaf_map = {
                    row_key: set(rankings[row_key][:prefix]) for row_key in pair["row_keys"]
                }
                result = evaluate_selection(
                    verifier,
                    records,
                    config_source,
                    specs_by_target,
                    probe_args,
                    context_cache,
                    pair,
                    f"{mode}:prefix{prefix}",
                    row_leaf_map,
                )
                if result:
                    results.append(result)
                if args.include_leaf0_plus:
                    row_leaf_map = {
                        row_key: set([0] + rankings[row_key][:prefix])
                        for row_key in pair["row_keys"]
                    }
                    result = evaluate_selection(
                        verifier,
                        records,
                        config_source,
                        specs_by_target,
                        probe_args,
                        context_cache,
                        pair,
                        f"{mode}:leaf0_plus{prefix}",
                        row_leaf_map,
                    )
                    if result:
                        results.append(result)

    output = {
        "schema": "ecdlp_low_term_total2_public_prefix_shared_leaf_repair_probe_v1",
        "method": "public_prefix_scalar_repair_with_model_bound_shared_leaf_prefix_accounting",
        "source": str(args.source),
        "parameters": {
            "source": str(args.source),
            "targets": sorted(targets),
            "transfers": sorted(transfers),
            "modes": modes,
            "max_prefix": int(args.max_prefix),
            "include_leaf0_plus": bool(args.include_leaf0_plus),
            "cost_model": (
                "direct_ops are verifier-replayed preassociation_filter_ops; "
                "shared_leaf_prefix_ops subtract duplicate selected-leaf checks "
                "only for identical selected leaf polynomials across rows"
            ),
        },
        "source_pairs": pairs,
        "results": results,
        "summary": summarize(results, pairs, modes),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps(output["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
