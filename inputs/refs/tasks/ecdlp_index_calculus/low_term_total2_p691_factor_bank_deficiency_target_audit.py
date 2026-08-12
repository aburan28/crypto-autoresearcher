#!/usr/bin/env python3
"""P691 deficiency-target audit for the order-9887 factor bank."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Any

import low_term_total2_p639_right208_salt208_recurrence_scout as p639
import low_term_total2_p678_right208_salt208_public_selector_audit as p678
import low_term_total2_p690_false_rank_certificate_factor_audit as p690
import low_term_total2_target_eliminated_factor_relation_bank as factor_bank


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_OUT = STATE_DIR / "low_term_total2_p691_factor_bank_deficiency_target_audit_probe.json"
ORDER = p690.ORDER


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


def stat(values: list[int | float]) -> dict[str, Any]:
    if not values:
        return {"count": 0, "max": None, "mean": None, "min": None}
    return {"count": len(values), "max": max(values), "mean": round(mean(values), 8), "min": min(values)}


def rref_mod(matrix: list[list[int]], modulus: int) -> tuple[list[list[int]], list[int]]:
    rows = [[value % modulus for value in row] for row in matrix if any(value % modulus for value in row)]
    if not rows:
        return [], []
    row_count = len(rows)
    col_count = len(rows[0])
    rank = 0
    pivots: list[int] = []
    for col in range(col_count):
        pivot = None
        for row in range(rank, row_count):
            if rows[row][col] % modulus:
                pivot = row
                break
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        inv = pow(rows[rank][col] % modulus, -1, modulus)
        rows[rank] = [(value * inv) % modulus for value in rows[rank]]
        for row in range(row_count):
            if row == rank:
                continue
            factor = rows[row][col] % modulus
            if factor:
                rows[row] = [(rows[row][idx] - factor * rows[rank][idx]) % modulus for idx in range(col_count)]
        pivots.append(col)
        rank += 1
        if rank == row_count:
            break
    return rows[:rank], pivots


def nullspace_basis(matrix: list[list[int]], modulus: int) -> list[list[int]]:
    if not matrix:
        return []
    col_count = len(matrix[0])
    rref, pivots = rref_mod(matrix, modulus)
    pivot_set = set(pivots)
    basis: list[list[int]] = []
    for free_col in range(col_count):
        if free_col in pivot_set:
            continue
        vector = [0] * col_count
        vector[free_col] = 1
        for row_idx, pivot_col in enumerate(pivots):
            vector[pivot_col] = (-rref[row_idx][free_col]) % modulus
        basis.append(vector)
    return basis


def selected(cert: dict[str, Any]) -> dict[str, Any]:
    value = cert.get("selected")
    return value if isinstance(value, dict) else {}


def cert_feature(cert: dict[str, Any]) -> dict[str, Any]:
    row = selected(cert)
    selector = str(row.get("selector") or "")
    match = p639.SELECTOR_RE.search(selector)
    mode = selector.split("__", 1)[0]
    feature = {
        "artifact": cert.get("_artifact"),
        "artifact_offset": int_value(cert.get("_artifact_offset")),
        "direct_ops_over_rho": float_value(row.get("direct_ops_over_rho")),
        "forms_count": int_value(cert.get("forms_count")),
        "rank": int_value(cert.get("rank")),
        "selector": selector,
        "selector_mode": mode,
        "target": row.get("target"),
        "top_k": int_value(row.get("top_k")),
        "transfer_index": int_value(row.get("transfer_index")),
    }
    if match:
        transfer = int(match.group("transfer"))
        left = int(match.group("salt_left"))
        right = int(match.group("salt_right"))
        anchor = int(match.group("right_anchor"))
        left_leaf = int(match.group("left_leaf"))
        right_leaf = int(match.group("right_leaf"))
        top_k = int(match.group("top_k"))
        feature.update(
            {
                "leaf_signature": f"L{left_leaf:02d}_R{right_leaf:02d}-{top_k}",
                "right_anchor_token": f"anchor{anchor}",
                "row_pair": f"salt{left}_salt{right}",
                "salt_left_token": f"salt{left}",
                "salt_right_token": f"salt{right}",
                "transfer_mod7": transfer % 7,
                "transfer_mod12": transfer % 12,
            }
        )
    else:
        feature.update(
            {
                "leaf_signature": "unparsed",
                "right_anchor_token": "unparsed",
                "row_pair": "unparsed",
                "salt_left_token": "unparsed",
                "salt_right_token": "unparsed",
                "transfer_mod7": "unparsed",
                "transfer_mod12": "unparsed",
            }
        )
    support = cert.get("selected_term_support")
    if isinstance(support, list):
        feature["selected_term_support"] = ",".join(str(int_value(item)) for item in support)
    else:
        feature["selected_term_support"] = "none"
    feature["mode_anchor_row_pair"] = (
        f"{feature['selector_mode']}|{feature['right_anchor_token']}|{feature['row_pair']}"
    )
    feature["mode_leaf"] = f"{feature['selector_mode']}|{feature['leaf_signature']}"
    return feature


def relation_key(relation: dict[str, Any], factor_count: int) -> tuple[tuple[int, ...], int]:
    coeffs = factor_bank.pad([int_value(value) % ORDER for value in relation["canonical_coeffs"]], factor_count)
    return tuple(coeffs), int_value(relation["canonical_rhs"]) % ORDER


def collect_relations(certificates: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], int]:
    factor_count = 0
    for cert in certificates:
        forms = [form for form in (cert.get("forms") or []) if isinstance(form, dict)]
        factor_count = max(
            factor_count,
            max([max(0, len(form.get("coeffs") or []) - 1) for form in forms] or [0]),
        )
    raw: list[dict[str, Any]] = []
    unique_by_key: dict[tuple[tuple[int, ...], int], dict[str, Any]] = {}
    for cert in certificates:
        feature = cert_feature(cert)
        for relation in factor_bank.target_eliminated_rows(cert):
            if relation.get("relation_status") != "TARGET_ELIMINATED_FACTOR_RELATION":
                continue
            key = relation_key(relation, factor_count)
            coeffs, rhs = key
            support = [idx for idx, coeff in enumerate(coeffs) if coeff % ORDER]
            record = {
                "canonical_coeffs": list(coeffs),
                "canonical_rhs": rhs,
                "feature": feature,
                "factor_support": support,
                "factor_support_size": len(support),
                "key": f"{','.join(str(value) for value in coeffs)}|{rhs}",
                "pair": relation.get("pair"),
            }
            raw.append(record)
            if key not in unique_by_key:
                unique_by_key[key] = dict(record)
                unique_by_key[key]["multiplicity"] = 0
                unique_by_key[key]["example_features"] = []
            unique_by_key[key]["multiplicity"] += 1
            if len(unique_by_key[key]["example_features"]) < 8:
                unique_by_key[key]["example_features"].append(feature)
    return raw, list(unique_by_key.values()), factor_count


def derive_columns(matrix: list[list[int]], rhs: list[int], factor_count: int) -> tuple[list[dict[str, Any]], list[int]]:
    columns: list[dict[str, Any]] = []
    missing: list[int] = []
    for index in range(factor_count):
        derived = factor_bank.derive_variable(matrix, rhs, index, ORDER)
        row = {
            "column": index,
            "derivable": bool(derived.get("derivable")),
            "value": derived.get("value"),
            "combination_row_count": derived.get("combination_row_count"),
        }
        columns.append(row)
        if not row["derivable"]:
            missing.append(index)
    return columns, missing


def summarize_columns(unique_relations: list[dict[str, Any]], missing_columns: set[int], basis: list[list[int]]) -> list[dict[str, Any]]:
    out = []
    for column in range(len(unique_relations[0]["canonical_coeffs"]) if unique_relations else 0):
        supporting = [row for row in unique_relations if int_value(row["canonical_coeffs"][column]) % ORDER]
        multiplicity = sum(int_value(row.get("multiplicity")) for row in supporting)
        out.append(
            {
                "column": column,
                "is_missing_derivable_column": column in missing_columns,
                "nullspace_values": [basis_row[column] for basis_row in basis],
                "support_multiplicity": multiplicity,
                "unique_relation_support_count": len(supporting),
                "unique_relation_support_density": len(supporting) / max(1, len(unique_relations)),
            }
        )
    return out


def feature_buckets(raw_relations: list[dict[str, Any]], missing_columns: set[int]) -> list[dict[str, Any]]:
    fields = [
        "selector_mode",
        "right_anchor_token",
        "row_pair",
        "mode_anchor_row_pair",
        "mode_leaf",
        "leaf_signature",
        "selected_term_support",
        "transfer_mod7",
        "transfer_mod12",
    ]
    buckets: dict[tuple[str, str], dict[str, Any]] = {}
    for relation in raw_relations:
        support = set(relation["factor_support"])
        touches_missing = bool(support & missing_columns)
        key_unique = relation["key"]
        feature = relation["feature"]
        for field in fields:
            value = str(feature.get(field))
            key = (field, value)
            row = buckets.setdefault(
                key,
                {
                    "cert_artifact_offsets": set(),
                    "direct_ops_over_rho_values": [],
                    "field": field,
                    "missing_touch_relation_count": 0,
                    "missing_touch_unique_keys": set(),
                    "relation_count": 0,
                    "unique_keys": set(),
                    "value": value,
                },
            )
            row["relation_count"] += 1
            row["unique_keys"].add(key_unique)
            row["cert_artifact_offsets"].add(
                f"{feature.get('artifact')}:{feature.get('artifact_offset')}"
            )
            row["direct_ops_over_rho_values"].append(float_value(feature.get("direct_ops_over_rho")))
            if touches_missing:
                row["missing_touch_relation_count"] += 1
                row["missing_touch_unique_keys"].add(key_unique)
    out = []
    for row in buckets.values():
        relation_count = int_value(row["relation_count"])
        missing_count = int_value(row["missing_touch_relation_count"])
        if relation_count < 3:
            continue
        out.append(
            {
                "certificate_count": len(row["cert_artifact_offsets"]),
                "direct_ops_over_rho": stat(row["direct_ops_over_rho_values"]),
                "field": row["field"],
                "missing_touch_density": missing_count / max(1, relation_count),
                "missing_touch_relation_count": missing_count,
                "missing_touch_unique_relation_count": len(row["missing_touch_unique_keys"]),
                "relation_count": relation_count,
                "unique_relation_count": len(row["unique_keys"]),
                "value": row["value"],
            }
        )
    out.sort(
        key=lambda item: (
            -float(item["missing_touch_density"]),
            -int(item["missing_touch_unique_relation_count"]),
            -int(item["certificate_count"]),
            str(item["field"]),
            str(item["value"]),
        )
    )
    return out


def determine_claim(summary: dict[str, Any]) -> str:
    if summary["rank"] != 14 or summary["deficiency"] != 2:
        return "P691_FACTOR_BANK_BASELINE_MISMATCH"
    compact = [
        item
        for item in summary["top_missing_touch_feature_buckets"]
        if item["missing_touch_density"] >= 0.75 and item["certificate_count"] >= 2
    ]
    if compact:
        return "P691_MISSING_DIRECTIONS_LOCALIZED_WITH_PUBLIC_FEATURE_ENRICHMENT"
    if summary["missing_touch_unique_relation_count"]:
        return "P691_MISSING_DIRECTIONS_LOCALIZED_BUT_FEATURES_BROAD"
    return "NEGATIVE_RESULT_P691_NO_MISSING_DIRECTION_RELATION_SUPPORT"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--certificate", action="append", default=None, help="Certificate artifact to include.")
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    paths = [Path(path) for path in (args.certificate or [str(path) for path in p690.DEFAULT_CERTIFICATE_PATHS])]
    certificates = factor_bank.load_certificates(paths)
    candidates, _missing = p690.find_candidates(certificates)
    candidate_keys = {p690.selected_key(cert) for cert in candidates}
    base = [cert for cert in certificates if p690.selected_key(cert) not in candidate_keys]
    raw_relations, unique_relations, factor_count = collect_relations(base)
    matrix = [relation["canonical_coeffs"] for relation in unique_relations]
    rhs = [int_value(relation["canonical_rhs"]) % ORDER for relation in unique_relations]
    rank = factor_bank.rank_mod(matrix, ORDER)
    augmented_rank = factor_bank.rank_mod([row + [rhs[index]] for index, row in enumerate(matrix)], ORDER)
    columns, missing_columns = derive_columns(matrix, rhs, factor_count)
    missing_set = set(missing_columns)
    basis = nullspace_basis(matrix, ORDER)
    missing_touch_relations = [row for row in unique_relations if set(row["factor_support"]) & missing_set]
    missing_touch_raw = [row for row in raw_relations if set(row["factor_support"]) & missing_set]
    column_summaries = summarize_columns(unique_relations, missing_set, basis)
    top_buckets = feature_buckets(raw_relations, missing_set)[:40]
    summary = {
        "augmented_rank": augmented_rank,
        "base_certificate_count": len(base),
        "candidate_excluded_count": len(candidates),
        "deficiency": max(0, factor_count - rank),
        "derivable_column_count": sum(1 for column in columns if column["derivable"]),
        "factor_variable_count": factor_count,
        "missing_columns": missing_columns,
        "missing_touch_raw_relation_count": len(missing_touch_raw),
        "missing_touch_unique_relation_count": len(missing_touch_relations),
        "nullity": len(basis),
        "nullspace_support_columns": sorted({idx for vector in basis for idx, value in enumerate(vector) if value % ORDER}),
        "rank": rank,
        "raw_relation_count": len(raw_relations),
        "top_missing_touch_feature_buckets": top_buckets[:12],
        "unique_relation_count": len(unique_relations),
    }
    claim_status = determine_claim(summary)
    payload = {
        "schema": "ecdlp.low_term_total2_p691_factor_bank_deficiency_target_audit.v1",
        "created_at": p678.utc_now(),
        "method": "p691_factor_bank_deficiency_target_audit",
        "claim_status": claim_status,
        "artifacts": {"certificates": [str(path) for path in paths]},
        "parameters": {
            "base_rule": "all listed direct certificate artifacts excluding exact P690 candidate selected rows",
            "feature_fields": [
                "selector_mode",
                "right_anchor_token",
                "row_pair",
                "mode_anchor_row_pair",
                "mode_leaf",
                "leaf_signature",
                "selected_term_support",
                "transfer_mod7",
                "transfer_mod12",
            ],
            "order": ORDER,
        },
        "summary": summary,
        "columns": columns,
        "column_summaries": column_summaries,
        "nullspace_basis": basis,
        "top_missing_touch_feature_buckets": top_buckets,
        "missing_touch_relation_examples": [
            {
                "canonical_coeffs": row["canonical_coeffs"],
                "canonical_rhs": row["canonical_rhs"],
                "factor_support": row["factor_support"],
                "feature": row["feature"],
                "multiplicity": row.get("multiplicity"),
            }
            for row in missing_touch_relations[:24]
        ],
        "honesty_boundary": [
            "This audit localizes the current factor-bank deficiency but does not generate new independent relations.",
            "Feature enrichment is measured over existing toy-prime certificates and may not predict fresh rows.",
            "Non-derivable columns are representation-specific to the current order-9887 factor namespace.",
            "A useful feature bucket is a work order for source generation, not a faster-than-rho claim.",
        ],
    }
    Path(args.out).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "claim_status": claim_status,
                "summary": summary,
                "top_missing_touch_feature_buckets": top_buckets[:5],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
