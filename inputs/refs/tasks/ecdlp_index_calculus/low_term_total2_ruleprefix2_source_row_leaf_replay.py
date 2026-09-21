#!/usr/bin/env python3
"""Replay exact source-row leaf selections from the null-vector source scorer.

The generic nullspace scout reranks leaves by prefix rules.  This helper takes
rows emitted by ``low_term_total2_ruleprefix2_null_vector_source_row_scorer.py``
and replays the exact ``row_leaf_keys`` that produced the pre-replay
below-rho/null/free signal.

It is still only a bounded replay experiment: candidate certificates must pass
the usual rank, repair-bank, and family-holdout gates before any promotion.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import low_term_total2_nullspace_asymmetric_leaf_scout as null_scout
import low_term_total2_public_prefix_shared_leaf_repair_probe as repair_probe
import low_term_total2_ruleprefix2_null_vector_source_row_scorer as source_scorer
import low_term_total2_target_eliminated_factor_relation_bank as factor_bank


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def int_value(value: Any, default: int = 0) -> int:
    return factor_bank.int_value(value, default)


def parse_csv(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [item.strip() for item in raw.split(",") if item.strip()]


def row_leaf_map(row_leaf_keys: list[dict[str, Any]]) -> dict[str, set[int]]:
    out: dict[str, set[int]] = {}
    for item in row_leaf_keys:
        if not isinstance(item, dict):
            continue
        row_key = str(item.get("row_key"))
        leaves = {int_value(leaf) for leaf in item.get("leaf_indices") or []}
        if row_key and leaves:
            out.setdefault(row_key, set()).update(leaves)
    return out


def profiles_for_selection(
    context: dict[str, Any],
    selected: dict[str, set[int]],
    null_vector: list[int],
    order: int,
    free_column: int,
) -> dict[str, list[dict[str, Any]]]:
    profiles: dict[str, list[dict[str, Any]]] = {}
    for row_key, leaves in selected.items():
        row_context = source_scorer.row_context(context, row_key)
        profiles[row_key] = [
            null_scout.leaf_null_profile(row_context, int(leaf), null_vector, order, free_column)
            for leaf in sorted(leaves)
        ]
    return profiles


def select_rows(scorer: dict[str, Any], args: argparse.Namespace) -> list[dict[str, Any]]:
    statuses = set(parse_csv(args.statuses))
    rows = scorer.get("rows") if isinstance(scorer.get("rows"), list) else []
    selected = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        if statuses and str(row.get("signal_status")) not in statuses:
            continue
        if int_value(row.get("signal_score")) < int_value(args.min_signal_score):
            continue
        if not row.get("row_leaf_keys"):
            continue
        selected.append(row)
    selected.sort(
        key=lambda row: (
            -int_value(row.get("signal_score")),
            str(row.get("source_label")),
            int_value(row.get("transfer_index")),
            str(row.get("selector")),
        )
    )
    return selected[: max(0, int_value(args.max_rows))]


def compact_source_row(row: dict[str, Any]) -> dict[str, Any]:
    keep = (
        "source_label",
        "source_path",
        "transfer_index",
        "target",
        "top_k",
        "source_policy",
        "row_selector",
        "selector",
        "signal_score",
        "signal_status",
        "ops_over_rho",
        "projection_signed",
        "free_term_count",
        "row_leaf_keys",
    )
    return {key: row.get(key) for key in keep}


def main() -> None:
    args = parse_args()
    scorer = load_json(args.scorer)
    selected_rows = select_rows(scorer, args)
    null_vector = source_scorer.parse_null_vector(args.null_vector)
    frontier_paths = null_scout.resolve_frontier_paths(args.frontier_certificates, args.frontier_list_source)
    null_basis, factor_count = null_scout.frontier_nullspace(frontier_paths, int_value(args.order, 11779))
    source_cache: dict[str, dict[str, Any]] = {}
    runtime_cache: dict[str, tuple[Any, list[dict[str, Any]], dict[str, Any], dict[str, dict[str, dict[str, Any]]], argparse.Namespace]] = {}
    context_caches: dict[str, dict[tuple[str, int, int, tuple[str, ...]], dict[str, Any]]] = {}
    results = []
    errors = []
    pairs = []

    for index, row in enumerate(selected_rows):
        source_path = str(row.get("source_path"))
        try:
            source = source_cache.get(source_path)
            if source is None:
                source = load_json(Path(source_path))
                source_cache[source_path] = source
            runtime = runtime_cache.get(source_path)
            if runtime is None:
                params = repair_probe.source_parameters(source)
                probe_args = repair_probe.probe_args_from_source(source)
                verifier, records, config_source, specs_by_target = repair_probe.build_specs(params)
                runtime = (verifier, records, config_source, specs_by_target, probe_args)
                runtime_cache[source_path] = runtime
            verifier, records, config_source, specs_by_target, probe_args = runtime
            context_cache = context_caches.setdefault(source_path, {})
            pair = {
                "row_keys": row.get("row_keys") or sorted(row_leaf_map(row.get("row_leaf_keys") or [])),
                "row_selector": row.get("row_selector"),
                "source_policy": row.get("source_policy"),
                "target": row.get("target"),
                "top_k": int_value(row.get("top_k")),
                "transfer_index": int_value(row.get("transfer_index")),
            }
            pairs.append(pair)
            context = source_scorer.build_context(
                verifier,
                records,
                config_source,
                specs_by_target,
                probe_args,
                pair,
                context_cache,
            )
            selected = row_leaf_map(row.get("row_leaf_keys") or [])
            selected_profiles = profiles_for_selection(
                context,
                selected,
                null_vector,
                int_value(args.order, 11779),
                int_value(args.free_column, 6),
            )
            label = f"source_row_exact:{index}:{row.get('source_label')}:{row.get('selector')}"
            result = null_scout.evaluate_selection(
                verifier,
                context,
                pair,
                label,
                selected,
                selected_profiles,
                null_basis,
                factor_count,
                int_value(args.order, 11779),
            )
            if result:
                result["source_row_signal"] = compact_source_row(row)
                results.append(result)
        except Exception as error:
            errors.append({"error": str(error), "source_row": compact_source_row(row)})

    results.sort(
        key=lambda result: (
            -int_value((result.get("projection_status_counts") or {}).get("NONZERO_NULLSPACE_PROJECTION")),
            not bool(result.get("union_public_key_verified")),
            float(result.get("direct_ops_over_rho") or 10**9),
            str(result.get("label")),
        )
    )
    summary = null_scout.summarize(results, pairs)
    certificates = []
    seen_certificates: set[str] = set()
    for result in results:
        cert = result.pop("_candidate_certificate", None)
        if not isinstance(cert, dict):
            continue
        if not result.get("union_public_key_verified"):
            continue
        if not int_value((result.get("projection_status_counts") or {}).get("NONZERO_NULLSPACE_PROJECTION")):
            continue
        key = json.dumps(cert.get("forms") or [], sort_keys=True, separators=(",", ":"))
        if key in seen_certificates:
            continue
        seen_certificates.add(key)
        cert["_artifact_offset"] = len(certificates)
        certificates.append(cert)
    summary["candidate_certificate_count"] = len(certificates)
    payload = {
        "artifacts": {
            "frontier_certificates": [str(path) for path in frontier_paths],
            "frontier_list_source": str(args.frontier_list_source),
            "scorer": str(args.scorer),
        },
        "certificates": certificates,
        "claim_status": summary["claim_status"],
        "errors": errors[:100],
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: exact source-row leaf replay is a scheduling experiment, not target descent.",
            "NO SPEEDUP CLAIM: positive replay requires rank, repair-bank, family-holdout, source-cost, sparse-LA, and fresh-target gates.",
        ],
        "parameters": {
            "free_column": int_value(args.free_column, 6),
            "max_rows": int_value(args.max_rows),
            "min_signal_score": int_value(args.min_signal_score),
            "null_vector": null_vector,
            "order": int_value(args.order, 11779),
            "statuses": parse_csv(args.statuses),
        },
        "schema": "ecdlp.low_term_total2_ruleprefix2_source_row_leaf_replay.v1",
        "selected_source_rows": [compact_source_row(row) for row in selected_rows],
        "results": results[:120],
        "summary": summary,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scorer", required=True, type=Path)
    parser.add_argument("--frontier-certificates", default="")
    parser.add_argument(
        "--frontier-list-source",
        type=Path,
        default=null_scout.DEFAULT_FRONTIER_LIST_SOURCE,
    )
    parser.add_argument("--statuses", default="BELOW_RHO_NULL_FREE_SIGNAL")
    parser.add_argument("--min-signal-score", type=int, default=13)
    parser.add_argument("--max-rows", type=int, default=12)
    parser.add_argument("--order", type=int, default=11779)
    parser.add_argument("--free-column", type=int, default=6)
    parser.add_argument("--null-vector", default="1,1,11778,1,1,11778,1,0,0,0,0,0,0,0,0,0")
    parser.add_argument("--out", required=True, type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    main()
