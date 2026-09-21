#!/usr/bin/env python3
"""P949 exact-surface relation-envelope regeneration.

P948 showed that existing verifier-equation artifacts attach to P947 rows only
by loose row key, not exact transfer/surface identity.  This probe replays the
27 P947 selected surfaces under their exact transfer challenge seeds and emits
the verifier forms needed for relation-rank checks.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
TASK_DIR = Path(__file__).resolve().parent
for candidate in (REPO_ROOT, TASK_DIR):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from tasks.ecdlp_index_calculus.low_term_total2_p942_hash_context_discriminator import (  # noqa: E402
    int_value,
    load_json,
    now_iso,
    write_json,
    window_start,
)
from tasks.ecdlp_index_calculus.low_term_total2_p947_chronology_rank_descent_audit import (  # noqa: E402
    modular_rank,
)
from tasks.ecdlp_index_calculus.low_term_total2_p948_verifier_equation_attachment_audit import (  # noqa: E402
    parse_challenge_seed,
    selected_p947_rows,
)

import public_factor_forward_safe_multiblock_zero_extra_relation_rank_probe as zero_extra_probe  # noqa: E402
import relation_probe  # noqa: E402


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p949_exact_surface_relation_envelope_regeneration.md"
DEFAULT_CONFIG_SOURCE = STATE_DIR / "frontier_signed_eval_cover_row_schedule_filter_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p949_exact_surface_relation_envelope_regeneration_probe.json"
SCHEMA = "ecdlp.low_term_total2_p949_exact_surface_relation_envelope_regeneration.v1"


def selected_sort_key(row: dict[str, Any]) -> tuple[Any, ...]:
    return (
        window_start(str(row.get("window"))),
        int_value(row.get("transfer_index")),
        str(row.get("row_key")),
        str(row.get("hash")),
    )


def compact_selected(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "b_coeff": row.get("b_coeff"),
        "c_coeff": row.get("c_coeff"),
        "constant": row.get("constant"),
        "hash": row.get("hash"),
        "p947_challenge_seed": parse_challenge_seed(row.get("surface_id")),
        "policy": row.get("policy"),
        "ratio": row.get("ratio"),
        "row_key": row.get("row_key"),
        "source_artifact": row.get("artifact"),
        "surface_id": row.get("surface_id"),
        "target": row.get("target"),
        "target_prime": row.get("target_prime"),
        "transfer_index": row.get("transfer_index"),
        "window": row.get("window"),
    }


def coefficient_payload(row: dict[str, Any]) -> dict[str, Any]:
    coeffs = row.get("selected_factor_coefficients") or {}
    return {
        "constant": coeffs.get("constant"),
        "b_coeff": coeffs.get("b_coeff"),
        "c_coeff": coeffs.get("c_coeff"),
        "term_count": coeffs.get("term_count"),
    }


def find_source_policy_row(selected: dict[str, Any]) -> tuple[dict[str, Any] | None, str | None]:
    artifact = Path(str(selected.get("artifact") or ""))
    if not artifact.exists():
        return None, f"source artifact missing: {artifact}"
    payload = load_json(artifact)
    policy = str(selected.get("policy") or "")
    policy_rows = (payload.get("policy_rows") or {}).get(policy) or []
    surface_matches = [
        row
        for row in policy_rows
        if isinstance(row, dict) and str(row.get("surface_id")) == str(selected.get("surface_id"))
    ]
    if len(surface_matches) == 1:
        return surface_matches[0], None
    fallback_matches = [
        row
        for row in policy_rows
        if isinstance(row, dict)
        and str(row.get("row_key")) == str(selected.get("row_key"))
        and int_value(row.get("transfer_index"), -1) == int_value(selected.get("transfer_index"), -2)
        and str(row.get("selected_factor_hash")) == str(selected.get("hash"))
    ]
    if len(fallback_matches) == 1:
        return fallback_matches[0], None
    return (
        None,
        (
            f"expected one source row for surface_id={selected.get('surface_id')!r}; "
            f"surface_matches={len(surface_matches)} fallback_matches={len(fallback_matches)}"
        ),
    )


def source_leaf_indices(source: dict[str, Any]) -> list[int]:
    leaves = source.get("factor_zero_leaf_indices")
    if leaves is None:
        leaves = source.get("selected_leaf_indices")
    return sorted({int(leaf) for leaf in (leaves or [])})


def compact_form(index: int, event: dict[str, Any]) -> dict[str, Any]:
    coeffs, rhs, terms = event["form"]
    return {
        "form_index": index,
        "coeffs": [int(coeff) for coeff in coeffs],
        "rhs": int(rhs),
        "terms": [int(term) for term in terms],
    }


def strip_private(row: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in row.items() if not key.startswith("_")}


def unique_event_forms(rows: list[dict[str, Any]]) -> list[tuple[list[int], int, list[int]]]:
    forms: list[tuple[list[int], int, list[int]]] = []
    seen: set[tuple[tuple[int, ...], int]] = set()
    for row in rows:
        for event in row.get("_events") or []:
            coeffs, rhs, terms = event["form"]
            coeff_list = [int(coeff) for coeff in coeffs]
            key = (tuple(coeff_list), int(rhs))
            if key in seen:
                continue
            seen.add(key)
            forms.append((coeff_list, int(rhs), [int(term) for term in terms]))
    return forms


def challenge_group_key(
    verifier: Any,
    result: dict[str, Any],
    built: dict[str, Any],
) -> str:
    public = verifier.point_to_json(built["public"]) if built and not built.get("error") else None
    payload = {
        "challenge_seed": result.get("challenge_seed"),
        "public": public,
        "target": result.get("target"),
    }
    return json.dumps(payload, sort_keys=True)


def materialized_public_payload(verifier: Any, built: dict[str, Any]) -> dict[str, Any]:
    if not built or built.get("error"):
        return {}
    return {
        "base_order": int(built.get("order") or 0),
        "curve_prime": int(built.get("p") or 0),
        "generic_rho_steps": int(built.get("generic_rho_steps") or 0),
        "base_point": verifier.point_to_json(built["base"]),
        "public_key": verifier.point_to_json(built["public"]),
    }


def materialize_selected_row(
    verifier: Any,
    records: list[dict[str, Any]],
    config_source: dict[str, Any],
    args: argparse.Namespace,
    selected: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    source, source_error = find_source_policy_row(selected)
    challenge_seed = parse_challenge_seed(selected.get("surface_id"))
    selected_payload = compact_selected(selected)
    if source_error or source is None:
        return {
            **selected_payload,
            "error": source_error,
            "materialized": False,
            "source_recovered": False,
        }, None
    leaves = source_leaf_indices(source)
    if not challenge_seed:
        return {
            **selected_payload,
            "error": "missing P947 challenge seed in surface_id",
            "materialized": False,
            "source_recovered": True,
            "source_factor_zero_leaf_indices": leaves,
        }, None
    if not leaves:
        return {
            **selected_payload,
            "error": "missing factor_zero_leaf_indices in source policy row",
            "materialized": False,
            "source_recovered": True,
            "source_factor_zero_leaf_indices": leaves,
        }, None

    result, built = zero_extra_probe.materialize_row(
        verifier,
        records,
        config_source,
        args,
        str(selected.get("target")),
        str(selected.get("row_key")),
        challenge_seed,
        set(leaves),
    )
    linear_forms = [
        compact_form(index, event)
        for index, event in enumerate(result.get("_events") or [])
    ]
    public_payload = materialized_public_payload(verifier, built)
    verifier_challenge_seed = result.get("challenge_seed")
    materialized = not result.get("error")
    out = {
        **selected_payload,
        **{key: value for key, value in result.items() if not key.startswith("_")},
        **public_payload,
        "challenge_seed_matches_p947": verifier_challenge_seed == challenge_seed,
        "linear_form_count": len(linear_forms),
        "linear_forms": linear_forms,
        "materialized": materialized,
        "p947_challenge_seed": challenge_seed,
        "source_challenge_seed": source.get("challenge_seed"),
        "source_factor_zero_leaf_indices": leaves,
        "source_recovered": True,
        "source_selected_factor_coefficients": coefficient_payload(source),
        "source_selected_factor_hash": source.get("selected_factor_hash"),
        "verifier_challenge_seed": verifier_challenge_seed,
        "_events": result.get("_events") or [],
    }
    return out, built


def group_union_report(
    verifier: Any,
    key: str,
    raw_rows: list[dict[str, Any]],
    built: dict[str, Any],
) -> dict[str, Any]:
    forms = unique_event_forms(raw_rows)
    order = int(built.get("order") or 0)
    union = {
        "union_relation_count": len(forms),
        "union_rank": 0,
        "union_derived": False,
        "union_public_key_verified": False,
        "union_derived_secret": None,
    }
    if forms:
        union = zero_extra_probe.union_derive(verifier, raw_rows, built)
    matrix_rank = modular_rank([form[0] for form in forms], order) if forms and order else {
        "rank": 0,
        "row_count": len(forms),
        "column_count": 0,
        "nonunit_pivot_obstruction_count": 0,
    }
    parsed_key = json.loads(key)
    return {
        "base_order": order,
        "challenge_seed": parsed_key.get("challenge_seed"),
        "row_count": len(raw_rows),
        "row_keys": sorted({str(row.get("row_key")) for row in raw_rows}),
        "target": parsed_key.get("target"),
        "transfer_indices": sorted({int_value(row.get("transfer_index")) for row in raw_rows}),
        "unique_form_count": len(forms),
        "modular_form_rank": matrix_rank,
        **union,
    }


def determine_claim(summary: dict[str, Any]) -> str:
    if int_value(summary.get("source_error_count")):
        return "NEGATIVE_RESULT_P949_SOURCE_RECOVERY_INCOMPLETE"
    if int_value(summary.get("materialization_error_count")):
        return "NEGATIVE_RESULT_P949_EXACT_REPLAY_BUILD_ERRORS"
    if int_value(summary.get("unique_verifier_form_count")) == 0:
        return "NEGATIVE_RESULT_P949_EXACT_SURFACE_REPLAY_NO_VERIFIER_FORMS"
    if int_value(summary.get("union_public_key_verified_group_count")):
        return "P949_EXACT_SURFACE_RELATION_ENVELOPES_DERIVE_TRANSFER_SCALAR"
    if int_value(summary.get("max_union_rank")):
        return "P949_EXACT_SURFACE_VERIFIER_FORMS_RANK_WITHOUT_DERIVATION"
    return "P949_EXACT_SURFACE_VERIFIER_FORMS_MATERIALIZED_NO_RANK"


def summarize(rows: list[dict[str, Any]], challenge_groups: list[dict[str, Any]]) -> dict[str, Any]:
    materialized = [row for row in rows if row.get("materialized")]
    form_rows = [row for row in materialized if int_value(row.get("linear_form_count")) > 0]
    unique_forms = {
        (tuple(form.get("coeffs") or []), int_value(form.get("rhs")))
        for row in rows
        for form in row.get("linear_forms") or []
    }
    summary = {
        "selected_row_count": len(rows),
        "source_recovered_count": sum(1 for row in rows if row.get("source_recovered")),
        "source_error_count": sum(1 for row in rows if not row.get("source_recovered")),
        "exact_leaf_count": sum(len(row.get("source_factor_zero_leaf_indices") or []) for row in rows),
        "materialized_row_count": len(materialized),
        "materialization_error_count": sum(1 for row in rows if row.get("source_recovered") and row.get("error")),
        "rows_with_verifier_forms": len(form_rows),
        "linear_form_count": sum(int_value(row.get("linear_form_count")) for row in rows),
        "unique_verifier_form_count": len(unique_forms),
        "challenge_group_count": len(challenge_groups),
        "groups_with_forms": sum(1 for group in challenge_groups if int_value(group.get("unique_form_count")) > 0),
        "union_public_key_verified_group_count": sum(
            1 for group in challenge_groups if group.get("union_public_key_verified")
        ),
        "max_union_rank": max((int_value(group.get("union_rank")) for group in challenge_groups), default=0),
        "max_modular_form_rank": max(
            (int_value((group.get("modular_form_rank") or {}).get("rank")) for group in challenge_groups),
            default=0,
        ),
        "row_public_key_verified_count": sum(1 for row in rows if row.get("row_public_key_verified")),
        "challenge_seed_mismatch_count": sum(
            1 for row in materialized if not row.get("challenge_seed_matches_p947")
        ),
        "transfer_counts": dict(Counter(str(row.get("transfer_index")) for row in rows).most_common()),
        "row_key_count": len({str(row.get("row_key")) for row in rows}),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "ARCHIVE-SCOUT: rows are selected from existing P947/P948 archive artifacts.",
            "EXACT-SURFACE-REPLAY: the replay uses exact P947 surface_id seeds and source factor_zero_leaf_indices.",
            "RANK-NOT-ASYMPTOTIC: verifier-form rank is a component signal, not a complete index-calculus algorithm.",
            "POLLARD-RHO BOUNDARY: no faster-than-rho deployment claim follows without relation generation, linear algebra, and target descent beating rho end to end.",
        ],
    }
    summary["claim_status"] = determine_claim(summary)
    return summary


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    selected_rows = sorted(selected_p947_rows(), key=selected_sort_key)
    if args.limit is not None:
        selected_rows = selected_rows[: args.limit]
    config_source = load_json(args.config_source)
    verifier = relation_probe.load_verifier_module()
    records = verifier.load_records()

    output_rows: list[dict[str, Any]] = []
    raw_rows_by_group: dict[str, list[dict[str, Any]]] = defaultdict(list)
    built_by_group: dict[str, dict[str, Any]] = {}
    for selected in selected_rows:
        try:
            row, built = materialize_selected_row(verifier, records, config_source, args, selected)
        except Exception as exc:  # noqa: BLE001 - row-level audit should continue.
            row = {
                **compact_selected(selected),
                "error": f"{type(exc).__name__}: {exc}",
                "materialized": False,
                "source_recovered": False,
            }
            built = None
        if built and not built.get("error") and row.get("materialized"):
            key = challenge_group_key(verifier, row, built)
            raw_rows_by_group[key].append(row)
            built_by_group.setdefault(key, built)
        output_rows.append(strip_private(row))

    challenge_groups = [
        group_union_report(verifier, key, rows, built_by_group[key])
        for key, rows in sorted(raw_rows_by_group.items())
    ]
    summary = summarize(output_rows, challenge_groups)
    return {
        "artifacts": {
            "contract": str(args.contract),
            "script": str(Path(__file__)),
        },
        "challenge_groups": challenge_groups,
        "claim_status": summary["claim_status"],
        "created_at": now_iso(),
        "method": "p949_exact_surface_relation_envelope_regeneration",
        "parameters": {
            "config_source": str(args.config_source),
            "filter_mode": args.filter_mode,
            "limit": args.limit,
            "max_relations": args.max_relations,
            "row_pool": args.row_pool,
            "scout_limit": args.scout_limit,
            "scout_mode": args.scout_mode,
            "scout_order": args.scout_order,
            "seed": args.seed,
            "selected_limit": args.selected_limit,
        },
        "rows": output_rows,
        "schema": SCHEMA,
        "summary": summary,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--config-source", type=Path, default=DEFAULT_CONFIG_SOURCE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--filter-mode", default="low_term_span")
    parser.add_argument("--row-pool", type=int, default=512)
    parser.add_argument("--row-count", type=int, default=128)
    parser.add_argument("--scout-limit", type=int, default=192)
    parser.add_argument("--scout-mode", default="s3_coeff_spread")
    parser.add_argument("--scout-order", default="eval_cover_hits_high")
    parser.add_argument("--selected-limit", type=int, default=64)
    parser.add_argument("--factor-base-size", type=int, default=16)
    parser.add_argument("--max-relations", type=int, default=96)
    parser.add_argument("--min-distinct-indices", type=int, default=4)
    parser.add_argument("--min-unsigned-distinct-indices", type=int, default=2)
    parser.add_argument("--allow-combined-coefficients", dest="require_unit_coefficients", action="store_false")
    parser.set_defaults(require_unit_coefficients=True)
    parser.add_argument("--row-factor", type=int, default=512)
    parser.add_argument("--product-factor", type=int, default=4096)
    parser.add_argument("--seed", default="ecdlp-frontier-signed-dual-sieve-v1")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    summary = payload["summary"]
    print(
        f"claim={payload['claim_status']} "
        f"selected={summary['selected_row_count']} "
        f"source={summary['source_recovered_count']} "
        f"materialized={summary['materialized_row_count']} "
        f"form_rows={summary['rows_with_verifier_forms']} "
        f"forms={summary['unique_verifier_form_count']} "
        f"groups={summary['challenge_group_count']} "
        f"verified_groups={summary['union_public_key_verified_group_count']} "
        f"max_rank={summary['max_union_rank']} "
        f"out={args.out}"
    )


if __name__ == "__main__":
    main()
