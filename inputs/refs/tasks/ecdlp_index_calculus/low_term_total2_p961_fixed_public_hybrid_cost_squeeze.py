#!/usr/bin/env python3
"""P961 fixed-public hybrid cost-squeeze audit."""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
TASK_DIR = Path(__file__).resolve().parent
for candidate in (REPO_ROOT, TASK_DIR):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

import frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_shared_challenge_direct_witness_probe as direct_witness_probe  # noqa: E402
import frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_shared_challenge_salt_neighborhood_loto_leaf_public_probe as leaf_public_probe  # noqa: E402
import frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_shared_challenge_salt_neighborhood_loto_leaf_trim_probe as leaf_trim_probe  # noqa: E402
import low_term_total2_p959_fixed_public_rematerialization_audit as p959  # noqa: E402
import low_term_total2_public_prefix_shared_leaf_repair_probe as repair_probe  # noqa: E402


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p961_fixed_public_hybrid_cost_squeeze.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p961_fixed_public_hybrid_cost_squeeze_probe.json"
SCHEMA = "ecdlp.low_term_total2_p961_fixed_public_hybrid_cost_squeeze.v1"
DEFAULT_ROW_KEYS = ",".join(
    [
        "67.a1@9803:uniform:256:salt203",
        "67.a1@9803:uniform:256:salt205",
    ]
)
DEFAULT_SELECTORS = ",".join(
    [
        "mode_hybrid_support_monic_b_perrow1",
        "mode_hybrid_support_monic_b_perrow2",
        "mode_hybrid_support_monic_b_total2",
        "mode_hybrid_support_monic_b_total3",
        "mode_hybrid_support_monic_b_total4",
        "mode_cost_hybrid_support_monic_b_total2",
        "mode_cost_hybrid_support_monic_b_total3",
        "mode_cost_hybrid_support_monic_b_total4",
        "mode_hybrid_double_monic_b_perrow2",
        "mode_low_term_support_perrow2",
    ]
)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def parse_csv(raw: str) -> list[str]:
    return [item.strip() for item in raw.split(",") if item.strip()]


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def float_value(value: Any, default: float = 10**18) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def event_key(event: dict[str, Any]) -> tuple[tuple[int, ...], int]:
    coeffs, rhs, _terms = event["form"]
    return tuple(int(value) for value in coeffs), int(rhs)


def source_and_pair(args: argparse.Namespace) -> tuple[Path, dict[str, Any], list[dict[str, Any]]]:
    cases, pairs = p959.source_row_pairs(Path(args.state_dir), int(args.post_min), args.target)
    wanted = tuple(sorted(parse_csv(args.row_keys)))
    for pair in pairs:
        if tuple(sorted(str(key) for key in pair.get("row_keys") or [])) == wanted:
            source_path = p959.choose_source(cases, int(args.fixed_transfer))
            return source_path, pair, cases
    raise ValueError(f"row pair not found in P957 source pairs: {wanted!r}")


def build_materialized(
    verifier: Any,
    records: list[dict[str, Any]],
    config_source: dict[str, Any],
    specs_by_target: dict[str, dict[str, dict[str, Any]]],
    pair: dict[str, Any],
    source: dict[str, Any],
    args: argparse.Namespace,
) -> dict[str, Any]:
    probe_args = repair_probe.probe_args_from_source(source)
    selected_rows, built_by_row, components_by_row, local_args_by_row, feature_rows_by_row, errors = (
        leaf_trim_probe.scan_selected_rows(
            verifier,
            records,
            config_source,
            specs_by_target.get(str(pair["target"]), {}),
            [str(key) for key in pair.get("row_keys") or []],
            int(args.fixed_transfer),
            int(args.top_k),
            probe_args,
        )
    )
    return {
        "built_by_row": built_by_row,
        "components_by_row": components_by_row,
        "errors": errors,
        "feature_rows_by_row": feature_rows_by_row,
        "local_args_by_row": local_args_by_row,
        "probe_args": probe_args,
        "selected_rows": selected_rows,
    }


def public_values_for(materialized: dict[str, Any]) -> list[list[int]]:
    values = {
        tuple(int(value) for value in built.get("public") or [])
        for built in (materialized.get("built_by_row") or {}).values()
        if built.get("public")
    }
    return [list(value) for value in sorted(values)]


def scan_from_leaves(
    verifier: Any,
    materialized: dict[str, Any],
    pair: dict[str, Any],
    leaves_by_row: dict[str, set[int]],
    label: str,
    selector_kind: str,
) -> dict[str, Any]:
    public_rows = []
    events = []
    built_by_row = materialized["built_by_row"]
    components_by_row = materialized["components_by_row"]
    local_args_by_row = materialized["local_args_by_row"]
    for row in materialized["selected_rows"]:
        key = leaf_trim_probe.row_key(row)
        leaves = set(int(leaf) for leaf in leaves_by_row.get(key, set()))
        if not leaves:
            continue
        scan = direct_witness_probe.scan_selected(
            verifier,
            built_by_row[key],
            components_by_row[key],
            leaves,
            local_args_by_row[key],
        )
        for event in scan.get("relation_events") or []:
            coeffs, rhs, terms = event["form"]
            events.append(
                {
                    "form": (
                        tuple(int(value) for value in coeffs),
                        int(rhs),
                        [int(value) for value in terms],
                    ),
                    "leaf_index": event.get("leaf_index"),
                    "row_key": key,
                }
            )
        public_rows.append(
            {
                **row,
                "public_leaf_indices": sorted(leaves),
                "ranked_prefix": direct_witness_probe.compact_scan(scan),
                "_public_leaf": scan,
            }
        )
    union = direct_witness_probe.union_derive(verifier, public_rows, built_by_row, "_public_leaf")
    generic_rho = max((int(row.get("generic_rho_steps") or 0) for row in materialized["selected_rows"]), default=0)
    ops = sum(int((row.get("ranked_prefix") or {}).get("preassociation_filter_ops") or 0) for row in public_rows)
    unique_events = {event_key(event) for event in events}
    row_summaries = []
    for row in public_rows:
        row_summaries.append(
            {
                "leaf_indices": row.get("public_leaf_indices") or [],
                "ops": int((row.get("ranked_prefix") or {}).get("preassociation_filter_ops") or 0),
                "rank": int((row.get("ranked_prefix") or {}).get("rank") or 0),
                "relation_count": int((row.get("ranked_prefix") or {}).get("relation_count") or 0),
                "row_key": row.get("row_key"),
            }
        )
        row.pop("_public_leaf", None)
    return {
        "below_rho": bool(generic_rho and ops < generic_rho),
        "derived_secret": union.get("union_derived_secret"),
        "generic_rho_steps": generic_rho,
        "label": label,
        "ops": ops,
        "ops_over_rho": round(ops / max(1, generic_rho), 8) if generic_rho else None,
        "public_key_verified": bool(union.get("union_public_key_verified")),
        "rank": int(union.get("union_rank") or 0),
        "relation_count": int(union.get("union_relation_count") or 0),
        "row_keys": list(pair.get("row_keys") or []),
        "row_results": row_summaries,
        "selected_leaf_count": sum(len(leaves) for leaves in leaves_by_row.values()),
        "selected_row_count": len(public_rows),
        "selector_kind": selector_kind,
        "unique_form_count": len(unique_events),
    }


def public_selector_result(
    verifier: Any,
    materialized: dict[str, Any],
    pair: dict[str, Any],
    target: str,
    selector: str,
    residue_modulus: int,
) -> dict[str, Any]:
    spec = p959.selector_spec(selector)
    leaves_by_row = leaf_public_probe.select_public_leaves_by_row(
        materialized["selected_rows"],
        materialized["feature_rows_by_row"],
        target,
        p959.empty_profiles(),
        spec,
        residue_modulus,
    )
    return scan_from_leaves(verifier, materialized, pair, leaves_by_row, selector, "public")


def baseline_leaves(public_results: list[dict[str, Any]], baseline_selector: str) -> dict[str, set[int]]:
    for result in public_results:
        if result.get("label") != baseline_selector:
            continue
        return {
            str(row["row_key"]): {int(leaf) for leaf in row.get("leaf_indices") or []}
            for row in result.get("row_results") or []
        }
    return {}


def oracle_subset_results(
    verifier: Any,
    materialized: dict[str, Any],
    pair: dict[str, Any],
    base_leaves: dict[str, set[int]],
    limit: int,
) -> list[dict[str, Any]]:
    leaf_items = [
        (row_key, leaf)
        for row_key, leaves in sorted(base_leaves.items())
        for leaf in sorted(int(leaf) for leaf in leaves)
    ]
    results = []
    for size in range(1, len(leaf_items) + 1):
        for subset in itertools.combinations(leaf_items, size):
            leaves_by_row: dict[str, set[int]] = {}
            for row_key, leaf in subset:
                leaves_by_row.setdefault(row_key, set()).add(int(leaf))
            if not leaves_by_row:
                continue
            label = ";".join(f"{row_key.split(':')[-1]}:{leaf}" for row_key, leaf in subset)
            results.append(scan_from_leaves(verifier, materialized, pair, leaves_by_row, label, "oracle_subset"))
    results.sort(
        key=lambda row: (
            not bool(row.get("public_key_verified")),
            -int_value(row.get("rank")),
            float_value(row.get("ops_over_rho")),
            int_value(row.get("selected_leaf_count")),
            row.get("label") or "",
        )
    )
    return results[: max(0, int(limit))]


def best_public(results: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not results:
        return None
    ranked = sorted(
        results,
        key=lambda row: (
            not bool(row.get("public_key_verified")),
            -int_value(row.get("rank")),
            float_value(row.get("ops_over_rho")),
            int_value(row.get("selected_leaf_count")),
            row.get("label") or "",
        ),
    )
    return ranked[0]


def summarize(public_results: list[dict[str, Any]], oracle_results: list[dict[str, Any]], expected_secret: int) -> dict[str, Any]:
    public_successes = [
        row
        for row in public_results
        if row.get("public_key_verified")
        and int_value(row.get("rank")) >= 4
        and row.get("derived_secret") == expected_secret
        and bool(row.get("below_rho"))
    ]
    public_verified_rank4 = [
        row
        for row in public_results
        if row.get("public_key_verified")
        and int_value(row.get("rank")) >= 4
        and row.get("derived_secret") == expected_secret
    ]
    oracle_successes = [
        row
        for row in oracle_results
        if row.get("public_key_verified")
        and int_value(row.get("rank")) >= 4
        and row.get("derived_secret") == expected_secret
        and bool(row.get("below_rho"))
    ]
    best = best_public(public_results)
    claim = (
        "P961_PUBLIC_HYBRID_COST_SQUEEZE_BELOW_RHO"
        if public_successes
        else "P961_ORACLE_SUBSET_BELOW_RHO_PUBLIC_OPEN"
        if oracle_successes
        else "NEGATIVE_RESULT_P961_PUBLIC_HYBRID_COST_SQUEEZE_NO_BELOW_RHO"
    )
    return {
        "best_public_selector": best.get("label") if best else None,
        "best_public_ops_over_rho": best.get("ops_over_rho") if best else None,
        "best_public_rank": best.get("rank") if best else None,
        "claim_status": claim,
        "oracle_below_rho_rank4_verified_count": len(oracle_successes),
        "public_below_rho_rank4_verified_count": len(public_successes),
        "public_result_count": len(public_results),
        "public_verified_rank4_count": len(public_verified_rank4),
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    source_path, pair, cases = source_and_pair(args)
    source = p959.p957.load_json(source_path)
    params = repair_probe.source_parameters(source)
    verifier, records, config_source, specs_by_target = repair_probe.build_specs(params)
    materialized = build_materialized(verifier, records, config_source, specs_by_target, pair, source, args)
    public_results = [
        public_selector_result(
            verifier,
            materialized,
            pair,
            str(pair["target"]),
            selector,
            int(args.residue_modulus),
        )
        for selector in parse_csv(args.selectors)
    ]
    base_leaves = baseline_leaves(public_results, args.baseline_selector)
    oracle_results = oracle_subset_results(
        verifier,
        materialized,
        pair,
        base_leaves,
        int(args.oracle_result_limit),
    )
    summary = summarize(public_results, oracle_results, int(args.expected_secret))
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p959_script": str(Path(p959.__file__)),
            "script": str(Path(__file__)),
            "source": str(source_path),
        },
        "claim_status": summary["claim_status"],
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "FIXED-PUBLIC: every tested selector uses the P960 fixed transfer challenge.",
            "PUBLIC-SELECTOR: public selector variants are promotable only if they beat rho without oracle leaves.",
            "ORACLE-SUBSET-DIAGNOSTIC: subset minimization is a predictor-design target, not a promoted algorithm.",
            "COMPONENT-SIGNAL-NOT-END-TO-END: this tests one fixed-public relation certificate, not full relation collection or target descent.",
        ],
        "materialization": {
            "errors": materialized.get("errors") or [],
            "fixed_challenge_seed": f"{materialized['probe_args'].seed}:shared-transfer:{int(args.fixed_transfer)}:{args.target}",
            "public_values": public_values_for(materialized),
            "selected_row_count": len(materialized["selected_rows"]),
        },
        "method": "p961_fixed_public_hybrid_cost_squeeze",
        "oracle_subset_results": oracle_results,
        "parameters": {
            "baseline_selector": args.baseline_selector,
            "expected_secret": int(args.expected_secret),
            "fixed_transfer": int(args.fixed_transfer),
            "post_min": int(args.post_min),
            "row_keys": parse_csv(args.row_keys),
            "selectors": parse_csv(args.selectors),
            "target": args.target,
            "top_k": int(args.top_k),
        },
        "public_results": public_results,
        "schema": SCHEMA,
        "source_selected_case_count": len(cases),
        "summary": summary,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", type=Path, default=STATE_DIR)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--target", default=p959.p957.DEFAULT_TARGET)
    parser.add_argument("--post-min", type=int, default=p959.p957.DEFAULT_POST_MIN)
    parser.add_argument("--fixed-transfer", type=int, default=p959.DEFAULT_FIXED_TRANSFER)
    parser.add_argument("--row-keys", default=DEFAULT_ROW_KEYS)
    parser.add_argument("--selectors", default=DEFAULT_SELECTORS)
    parser.add_argument("--baseline-selector", default="mode_hybrid_support_monic_b_perrow2")
    parser.add_argument("--expected-secret", type=int, default=2351)
    parser.add_argument("--top-k", type=int, default=4)
    parser.add_argument("--residue-modulus", type=int, default=p959.DEFAULT_RESIDUE_MODULUS)
    parser.add_argument("--oracle-result-limit", type=int, default=12)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    summary = payload["summary"]
    print(
        f"claim={payload['claim_status']} "
        f"public_results={summary['public_result_count']} "
        f"public_verified_rank4={summary['public_verified_rank4_count']} "
        f"public_below_rho_rank4={summary['public_below_rho_rank4_verified_count']} "
        f"oracle_below_rho_rank4={summary['oracle_below_rho_rank4_verified_count']} "
        f"best_public={summary['best_public_selector']} "
        f"best_public_rank={summary['best_public_rank']} "
        f"best_public_ops_over_rho={summary['best_public_ops_over_rho']} "
        f"out={args.out}"
    )


if __name__ == "__main__":
    main()
