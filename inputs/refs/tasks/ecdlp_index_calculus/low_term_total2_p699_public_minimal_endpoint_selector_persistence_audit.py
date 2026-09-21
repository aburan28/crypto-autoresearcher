#!/usr/bin/env python3
"""P699 public minimal-endpoint selector and persistence audit.

P698 found a verified three-form endpoint closure above rho.  This audit learns
public selector descriptors from those three forms, applies them to calibration
and adjacent source surfaces, and separates public full-selector charge from
best rank-closing subset charge.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable

import low_term_total2_p693_endpoint_column_source_support_scout as p693
import low_term_total2_p697_endpoint_event_factor_rank_audit as p697
import low_term_total2_p698_minimal_endpoint_subset_cost_audit as p698


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P698 = STATE_DIR / "low_term_total2_p698_minimal_endpoint_subset_cost_audit_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p699_public_minimal_endpoint_selector_persistence_audit_probe.json"
DEFAULT_SURFACES = [
    (
        "P658_calibration",
        STATE_DIR / "low_term_total2_order9887_p658_phase3_right207_salt207_postquiet_source_22330_22342_probe.json",
        STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p658_order9887_phase3_right207_salt207_postquiet_22330_22342_density_gate_probe.json",
    ),
    (
        "P659_adjacent",
        STATE_DIR / "low_term_total2_order9887_p659_salt204_right206_anchor11_right208_source_22343_22355_probe.json",
        STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p659_order9887_salt204_right206_anchor11_right208_22343_22355_density_gate_probe.json",
    ),
    (
        "P660_exact_P658_repeat",
        STATE_DIR / "low_term_total2_order9887_p660_exact_p658_salt204_right206_anchor11_right208_source_22417_22423_probe.json",
        STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p660_order9887_exact_p658_salt204_right206_anchor11_right208_22417_22423_density_gate_probe.json",
    ),
    (
        "P661_adjacent",
        STATE_DIR / "low_term_total2_order9887_p661_right207_salt207_p659_branch_source_22356_22368_probe.json",
        STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p661_order9887_right207_salt207_p659_branch_22356_22368_density_gate_probe.json",
    ),
]


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def float_value(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def support_key(values: list[Any]) -> str:
    return ",".join(str(int_value(value)) for value in values)


def row_salt(row_key: str) -> str:
    if ":salt" not in row_key:
        return "unknown"
    return "salt" + row_key.rsplit(":salt", 1)[1]


def record_features(record: dict[str, Any]) -> dict[str, str]:
    return {
        "coeff_support": support_key(record.get("coeff_support") or []),
        "leaf_index": str(int_value(record.get("leaf_index"))),
        "leaf_scout": f"{int_value(record.get('leaf_index'))}|{int_value(record.get('scout_pos'))}",
        "leaf_scout_coeff": (
            f"{int_value(record.get('leaf_index'))}|{int_value(record.get('scout_pos'))}|"
            f"{support_key(record.get('coeff_support') or [])}"
        ),
        "row_salt": row_salt(str(record.get("row_key"))),
        "scout_pos": str(int_value(record.get("scout_pos"))),
        "term_support": support_key(record.get("term_support") or []),
    }


def parse_surface(raw: str) -> tuple[str, Path, Path]:
    parts = raw.split("|")
    if len(parts) != 3:
        raise ValueError("--surface must look like NAME|SOURCE|PRODUCT")
    return parts[0], Path(parts[1]), Path(parts[2])


def existing_surfaces(args: argparse.Namespace) -> list[tuple[str, Path, Path]]:
    surfaces = [parse_surface(raw) for raw in (args.surface or [])] if args.surface else list(DEFAULT_SURFACES)
    return [(name, source, product) for name, source, product in surfaces if source.exists() and product.exists()]


def surface_args(args: argparse.Namespace, source: Path, product: Path) -> SimpleNamespace:
    return SimpleNamespace(
        certificate=args.certificate,
        max_cases=args.max_cases,
        max_endpoint_leaves=args.max_endpoint_leaves,
        product=str(product),
        sample_limit=args.sample_limit,
        source=str(source),
        target=args.target,
    )


def collect_surface_records(
    args: argparse.Namespace,
    source: Path,
    product: Path,
    priority_columns: set[int],
) -> tuple[Any, dict[str, Any], list[dict[str, Any]]]:
    local_args = surface_args(args, source, product)
    verifier, row_contexts, context_cache_entry_count, missing_source_case_count = p697.build_row_contexts(local_args)
    mutation = p697.collect_mutation_records(
        verifier,
        row_contexts,
        priority_columns,
        int_value(args.max_endpoint_leaves),
    )
    endpoint_coeff_records = p697.unique_records(mutation["endpoint_coeff_records"])
    for index, record in enumerate(endpoint_coeff_records):
        record["_endpoint_form_index"] = index
        record["_public_features"] = record_features(record)
    meta = {
        "context_cache_entry_count": context_cache_entry_count,
        "endpoint_coeff_unique_form_count": len(endpoint_coeff_records),
        "endpoint_leaf_count": mutation["endpoint_leaf_count"],
        "endpoint_leaf_hit_root_count": mutation["endpoint_leaf_hit_root_count"],
        "missing_source_case_count": missing_source_case_count,
        "priority_coeff_event_counts": {
            str(column): mutation["priority_coeff_counts"][column] for column in sorted(priority_columns)
        },
        "priority_leaf_counts": {
            str(column): mutation["priority_leaf_counts"][column] for column in sorted(priority_columns)
        },
        "scanned_endpoint_leaf_count": mutation["scanned_endpoint_leaf_count"],
    }
    return verifier, meta, endpoint_coeff_records


def train_records_from_p698(
    p698_payload: dict[str, Any],
    calibration_records: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    minimal = ((p698_payload.get("subset_search") or {}).get("minimal_verified_subset") or {})
    indices = [int_value(index) for index in minimal.get("form_indices") or []]
    return [calibration_records[index] for index in indices if 0 <= index < len(calibration_records)]


def make_selectors(train_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    feature_sets: dict[str, set[str]] = {
        "coeff_support": set(),
        "leaf_index": set(),
        "leaf_scout": set(),
        "leaf_scout_coeff": set(),
        "scout_pos": set(),
        "term_support": set(),
    }
    for record in train_records:
        features = record.get("_public_features") or record_features(record)
        for key in feature_sets:
            feature_sets[key].add(str(features.get(key)))
    coeff_supports = feature_sets["coeff_support"]
    leaf_scouts = feature_sets["leaf_scout"]
    leaf_indices = feature_sets["leaf_index"]
    scout_positions = feature_sets["scout_pos"]
    return [
        {
            "name": "exact_leaf_scout_coeff",
            "rule": "leaf_index, scout_pos, and coeff_support match the P698 verified subset",
            "match": lambda record, allowed=feature_sets["leaf_scout_coeff"]: (
                (record.get("_public_features") or record_features(record))["leaf_scout_coeff"] in allowed
            ),
        },
        {
            "name": "leaf_scout",
            "rule": "leaf_index and scout_pos match the P698 verified subset",
            "match": lambda record, allowed=leaf_scouts: (
                (record.get("_public_features") or record_features(record))["leaf_scout"] in allowed
            ),
        },
        {
            "name": "coeff_support",
            "rule": "coeff_support shape matches the P698 verified subset",
            "match": lambda record, allowed=coeff_supports: (
                (record.get("_public_features") or record_features(record))["coeff_support"] in allowed
            ),
        },
        {
            "name": "leaf_index",
            "rule": "leaf_index matches the P698 verified subset",
            "match": lambda record, allowed=leaf_indices: (
                (record.get("_public_features") or record_features(record))["leaf_index"] in allowed
            ),
        },
        {
            "name": "scout_pos",
            "rule": "scout_pos matches the P698 verified subset",
            "match": lambda record, allowed=scout_positions: (
                (record.get("_public_features") or record_features(record))["scout_pos"] in allowed
            ),
        },
        {
            "name": "endpoint_support_size_le3_hits15",
            "rule": "support has column 15 and support size at most 3",
            "match": lambda record: (
                15 in {int_value(value) for value in record.get("coeff_support") or []}
                and len(record.get("coeff_support") or []) <= 3
            ),
        },
        {
            "name": "endpoint_support_size_le2",
            "rule": "support size at most 2 and support touches a priority column",
            "match": lambda record: (
                len(record.get("coeff_support") or []) <= 2
                and bool(set(int_value(value) for value in record.get("coeff_support") or []) & {0, 15})
            ),
        },
    ]


def evaluate_records(
    name: str,
    records: list[dict[str, Any]],
    verifier: Any,
    target: str,
    base: list[dict[str, Any]],
    base_state: dict[str, Any],
    priority_columns: set[int],
    sample_limit: int,
    max_subset_records: int,
) -> dict[str, Any]:
    selected_cost = p698.scan_cost(records)
    union = p697.union_derive(verifier, records)
    cert = p697.pseudo_certificate(name, records, target, union)
    full_eval = p697.evaluate_candidate(
        name,
        base,
        base_state,
        cert,
        priority_columns,
        sample_limit,
    )
    full_eval.update(
        {
            "selected_form_count": len(records),
            "selected_unique_leaf_scan_count": selected_cost["unique_leaf_scan_count"],
            "selected_unique_leaf_scan_ops_over_rho": selected_cost["unique_leaf_scan_ops_over_rho"],
            "union_derived_secret": union.get("union_derived_secret"),
            "union_public_key_verified": bool(union.get("union_public_key_verified")),
            "union_rank": int_value(union.get("union_rank")),
            "union_relation_count": int_value(union.get("union_relation_count")),
        }
    )
    subset_search = None
    if 2 <= len(records) <= max_subset_records:
        subset_search = p698.subset_search(
            verifier,
            records,
            target,
            base_state,
            priority_columns,
            sample_limit,
        )
    return {
        "full_selector_evaluation": full_eval,
        "selected_form_samples": [p697.compact_event_sample(record) for record in records[:sample_limit]],
        "subset_search": subset_search,
    }


def compact_subset(subset: dict[str, Any] | None) -> dict[str, Any] | None:
    if not subset:
        return None
    return {
        "form_count": int_value(subset.get("form_count")),
        "form_indices": subset.get("form_indices") or [],
        "new_missing_touch_relation_count": int_value(subset.get("new_missing_touch_relation_count")),
        "newly_derivable_priority_columns": subset.get("newly_derivable_priority_columns") or [],
        "rank_after": int_value(subset.get("rank_after")),
        "rank_gain": int_value(subset.get("rank_gain")),
        "union_derived_secret": subset.get("union_derived_secret"),
        "union_public_key_verified": bool(subset.get("union_public_key_verified")),
        "unique_factor_relation_gain": int_value(subset.get("unique_factor_relation_gain")),
        "unique_leaf_scan_ops_over_rho": subset.get("unique_leaf_scan_ops_over_rho"),
    }


def summarize_selector_result(result: dict[str, Any]) -> dict[str, Any]:
    full_eval = result["full_selector_evaluation"]
    subset_search = result.get("subset_search") or {}
    return {
        "full_rank_after": int_value(full_eval.get("rank_after")),
        "full_rank_gain": int_value(full_eval.get("rank_gain")),
        "full_selected_form_count": int_value(full_eval.get("selected_form_count")),
        "full_selected_ops_over_rho": full_eval.get("selected_unique_leaf_scan_ops_over_rho"),
        "full_union_public_key_verified": bool(full_eval.get("union_public_key_verified")),
        "minimal_rank_closing_subset": compact_subset(subset_search.get("minimal_rank_closing_subset")),
        "minimal_verified_subset": compact_subset(subset_search.get("minimal_verified_subset")),
    }


def determine_claim(summary: dict[str, Any]) -> str:
    if summary["public_below_rho_full_rank_selector_count"]:
        return "P699_PUBLIC_SELECTOR_BELOW_RHO_FULL_RANK"
    if summary["adjacent_full_rank_selector_count"]:
        return "P699_ENDPOINT_CLOSURE_PERSISTS_ADJACENT_ABOVE_RHO"
    if summary["best_subset_below_rho_count"]:
        return "P699_ORACLE_SUBSET_BELOW_RHO_PUBLIC_SELECTOR_STILL_ABOVE"
    if summary["calibration_full_rank_selector_count"]:
        return "P699_CALIBRATION_SELECTOR_FULL_RANK_ONLY"
    return "NEGATIVE_RESULT_P699_PUBLIC_ENDPOINT_SELECTORS_NO_RANK_CLOSURE"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    priority_columns = p693.parse_columns(args.priority_columns)
    surfaces = existing_surfaces(args)
    base, excluded_candidates, bank_meta = p697.base_bank(
        [Path(path) for path in (args.certificate or [str(path) for path in p697.p690.DEFAULT_CERTIFICATE_PATHS])]
    )
    base_state = p697.bank_state(base)
    p698_payload = load_json(Path(args.p698))
    surface_reports = []
    selector_summaries = []
    selectors = None
    training_records = []

    for surface_index, (surface_name, source, product) in enumerate(surfaces):
        verifier, surface_meta, records = collect_surface_records(args, source, product, priority_columns)
        if surface_index == 0:
            training_records = train_records_from_p698(p698_payload, records)
            selectors = make_selectors(training_records)
        if selectors is None:
            selectors = make_selectors([])
        selector_reports = []
        for selector in selectors:
            match: Callable[[dict[str, Any]], bool] = selector["match"]
            selected = [record for record in records if match(record)]
            if not selected:
                selector_reports.append(
                    {
                        "name": selector["name"],
                        "rule": selector["rule"],
                        "selected_form_count": 0,
                    }
                )
                continue
            evaluation = evaluate_records(
                selector["name"],
                selected,
                verifier,
                args.target,
                base,
                base_state,
                priority_columns,
                int_value(args.sample_limit, 12),
                int_value(args.max_subset_records, 18),
            )
            report = {
                "name": selector["name"],
                "rule": selector["rule"],
                **summarize_selector_result(evaluation),
                "selected_form_count": len(selected),
            }
            selector_reports.append(report)
            selector_summaries.append({"surface": surface_name, **report})
        surface_reports.append(
            {
                "endpoint_record_samples": [
                    p697.compact_event_sample(record) for record in records[: int_value(args.sample_limit, 12)]
                ],
                "product": str(product),
                "selector_reports": selector_reports,
                "source": str(source),
                "surface": surface_name,
                "surface_meta": surface_meta,
            }
        )

    public_below_rho = [
        row
        for row in selector_summaries
        if int_value(row.get("full_rank_after")) >= int_value(base_state["factor_count"])
        and bool(row.get("full_union_public_key_verified"))
        and float_value(row.get("full_selected_ops_over_rho"), 999.0) <= 1.0
    ]
    calibration_full_rank = [
        row
        for row in selector_summaries
        if row["surface"] == surfaces[0][0]
        and int_value(row.get("full_rank_after")) >= int_value(base_state["factor_count"])
    ]
    adjacent_full_rank = [
        row
        for row in selector_summaries
        if row["surface"] != surfaces[0][0]
        and int_value(row.get("full_rank_after")) >= int_value(base_state["factor_count"])
    ]
    best_subset_below_rho = []
    for row in selector_summaries:
        for key in ("minimal_rank_closing_subset", "minimal_verified_subset"):
            subset = row.get(key)
            if subset and float_value(subset.get("unique_leaf_scan_ops_over_rho"), 999.0) <= 1.0:
                best_subset_below_rho.append({"selector": row["name"], "surface": row["surface"], "subset_kind": key, **subset})
    summary = {
        "adjacent_full_rank_selector_count": len(adjacent_full_rank),
        "base_factor_variable_count": int_value(base_state["factor_count"]),
        "base_missing_columns": base_state["missing_columns"],
        "base_rank": int_value(base_state["rank"]),
        "base_unique_factor_relation_count": len(base_state["unique"]),
        "best_subset_below_rho_count": len(best_subset_below_rho),
        "calibration_full_rank_selector_count": len(calibration_full_rank),
        "excluded_p690_candidate_count": len(excluded_candidates),
        "public_below_rho_full_rank_selector_count": len(public_below_rho),
        "surface_count": len(surfaces),
        "training_record_count": len(training_records),
    }
    claim_status = determine_claim(summary)
    return {
        "artifacts": {
            "base_certificates": bank_meta["paths"],
            "p698": str(Path(args.p698)),
        },
        "claim_status": claim_status,
        "created_at": p697.p696.now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: selectors are public descriptors over already reconstructed row/leaf/scout/form surfaces.",
            "Public selector charge counts every selected unique leaf scan; best-subset charge is reported separately as oracle/generator-steering evidence.",
            "A full-rank selector above rho is an index-calculus precursor, not a faster-than-rho individual-log algorithm.",
        ],
        "method": "p699_public_minimal_endpoint_selector_persistence_audit",
        "parameters": {
            "max_cases": int_value(args.max_cases),
            "max_endpoint_leaves": int_value(args.max_endpoint_leaves),
            "max_subset_records": int_value(args.max_subset_records),
            "priority_columns": sorted(priority_columns),
            "target": args.target,
        },
        "schema": "ecdlp.low_term_total2_p699_public_minimal_endpoint_selector_persistence_audit.v1",
        "selector_summaries": selector_summaries,
        "strong_public_below_rho_examples": public_below_rho[: int_value(args.sample_limit, 12)],
        "subset_below_rho_examples": best_subset_below_rho[: int_value(args.sample_limit, 12)],
        "summary": summary,
        "surface_reports": surface_reports,
        "training_records": [p697.compact_event_sample(record) for record in training_records],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", default="67.a1@9803")
    parser.add_argument("--priority-columns", default="0,15")
    parser.add_argument("--p698", default=str(DEFAULT_P698))
    parser.add_argument("--surface", action="append", default=None, help="Surface as NAME|SOURCE|PRODUCT.")
    parser.add_argument("--certificate", action="append", default=None, help="Base certificate artifact to include.")
    parser.add_argument("--max-cases", type=int, default=0)
    parser.add_argument("--max-endpoint-leaves", type=int, default=0)
    parser.add_argument("--max-subset-records", type=int, default=18)
    parser.add_argument("--sample-limit", type=int, default=12)
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    print(json.dumps({"claim_status": payload["claim_status"], "summary": payload["summary"]}, indent=2, sort_keys=True))
    print(json.dumps({"selector_summaries": payload["selector_summaries"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
