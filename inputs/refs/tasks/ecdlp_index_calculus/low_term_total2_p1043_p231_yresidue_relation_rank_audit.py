#!/usr/bin/env python3
"""P1043 rank audit for y-residue-filtered true relation witnesses."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p1005_p231_context_safe_early_stop_order as p1005
import low_term_total2_p1023_p231_leaf19_relation_bank_audit as p1023
import low_term_total2_p1033_p231_leaf8_factor_label_extraction_scout as p1033


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1043_p231_yresidue_relation_rank_audit.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1043_p231_yresidue_relation_rank_audit_probe.json"
DEFAULT_INPUTS = [
    STATE_DIR / "low_term_total2_p1038_p231_guarded_structural_family_supply_search_probe.json",
    STATE_DIR / "low_term_total2_p1041_p231_yresidue_strict_route_validation_probe.json",
    STATE_DIR / "low_term_total2_p1042_p231_yresidue_second_holdout_validation_probe.json",
]
SCHEMA = "ecdlp.low_term_total2_p1043_p231_yresidue_relation_rank_audit.v1"
ORDER = p1033.ORDER
PRIMARY_POOL = "p1029_leaf8_scout"
STRICT_TERMS = (8, 8, 11, 11)
STRICT_TAIL = (9, 12)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def int_value(value: Any, default: int = 0) -> int:
    return p1023.int_value(value, default)


def mod_rank(rows: list[list[int]], modulus: int = ORDER) -> int:
    matrix = [[value % modulus for value in row] for row in rows if any(value % modulus for value in row)]
    if not matrix:
        return 0
    rank = 0
    col_count = len(matrix[0])
    for col in range(col_count):
        pivot = None
        for row in range(rank, len(matrix)):
            if matrix[row][col] % modulus:
                pivot = row
                break
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        inv = pow(matrix[rank][col] % modulus, -1, modulus)
        matrix[rank] = [(value * inv) % modulus for value in matrix[rank]]
        for row in range(len(matrix)):
            if row == rank:
                continue
            factor = matrix[row][col] % modulus
            if factor:
                matrix[row] = [(a - factor * b) % modulus for a, b in zip(matrix[row], matrix[rank])]
        rank += 1
        if rank == len(matrix):
            break
    return rank


def prediction_group_key(artifact: str, group: dict[str, Any], prediction: dict[str, Any]) -> tuple[Any, ...]:
    left = prediction.get("left") or {}
    right = prediction.get("right") or {}
    q_pair = tuple(sorted([int_value(left.get("q_coeff")) % ORDER, int_value(right.get("q_coeff")) % ORDER]))
    rhs_pair = tuple(sorted([int_value(left.get("rhs")) % ORDER, int_value(right.get("rhs")) % ORDER]))
    return (
        artifact,
        str(group.get("window") or left.get("window") or ""),
        str(group.get("public_fingerprint") or left.get("public_fingerprint") or ""),
        tuple(int_value(item) for item in (group.get("family") or {}).get("terms") or left.get("terms") or []),
        tuple(int_value(item) for item in (group.get("family") or {}).get("tail_support") or left.get("tail_support") or []),
        q_pair,
        rhs_pair,
        int_value(prediction.get("predicted_target")) % ORDER,
    )


def factor_signature(form: dict[str, Any]) -> tuple[tuple[int, int], ...]:
    return tuple(
        sorted(
            (int_value(index), int_value(coeff) % ORDER)
            for index, coeff in (form.get("nonzero_factors") or [])
        )
    )


def form_key(form: dict[str, Any]) -> tuple[Any, ...]:
    return (
        str(form.get("window") or ""),
        str(form.get("public_fingerprint") or ""),
        int_value(form.get("q_coeff")) % ORDER,
        int_value(form.get("rhs")) % ORDER,
        factor_signature(form),
    )


def load_true_witness_groups(path: Path) -> list[dict[str, Any]]:
    artifact = path.stem
    payload = json.loads(path.read_text(encoding="utf-8"))
    groups_by_key: dict[tuple[Any, ...], dict[str, Any]] = {}
    for pool_result in payload.get("pool_results") or []:
        if pool_result.get("name") != PRIMARY_POOL:
            continue
        for evaluation in pool_result.get("evaluations") or []:
            if evaluation.get("label") != f"{PRIMARY_POOL}_forward_compressed":
                continue
            for object_result in evaluation.get("object_results") or []:
                for group in object_result.get("groups") or []:
                    family = group.get("family") or {}
                    terms = tuple(int_value(item) for item in family.get("terms") or [])
                    tail = tuple(int_value(item) for item in family.get("tail_support") or [])
                    if terms != STRICT_TERMS or tail != STRICT_TAIL:
                        continue
                    for prediction in group.get("predictions") or []:
                        if not prediction.get("toy_secret_verified"):
                            continue
                        key = prediction_group_key(artifact, group, prediction)
                        if key not in groups_by_key:
                            groups_by_key[key] = {
                                "artifact": artifact,
                                "models": set(),
                                "prediction": prediction,
                                "public_fingerprint": key[2],
                                "window": key[1],
                            }
                        groups_by_key[key]["models"].add(str(object_result.get("model") or ""))
    groups = []
    for group in groups_by_key.values():
        group["models"] = sorted(group["models"])
        groups.append(group)
    return sorted(groups, key=lambda item: (item["artifact"], item["window"], item["public_fingerprint"]))


def derive_scalar_from_pair(left: dict[str, Any], right: dict[str, Any]) -> int | None:
    return p1033.derive_target_from_pair(left, right, max_factor_index([left, right]))


def max_factor_index(forms: list[dict[str, Any]]) -> int:
    return max([index for form in forms for index, _coeff in factor_signature(form)] or [0])


def residual_for_form(form: dict[str, Any], scalar: int) -> int:
    q = int_value(form.get("q_coeff")) % ORDER
    rhs = int_value(form.get("rhs")) % ORDER
    return (rhs - q * scalar) % ORDER


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    input_paths = [Path(item) for item in args.inputs.split(",") if item.strip()]
    witness_groups = []
    for path in input_paths:
        witness_groups.extend(load_true_witness_groups(path))

    unique_forms: dict[tuple[Any, ...], dict[str, Any]] = {}
    rows = []
    augmented_rows = []
    local_target_names = []
    factor_columns = sorted(
        {
            index
            for group in witness_groups
            for side in ("left", "right")
            for index, _coeff in factor_signature(group["prediction"].get(side) or {})
        }
    )
    factor_col_index = {factor: idx for idx, factor in enumerate(factor_columns)}
    target_col_index: dict[tuple[str, str], int] = {}
    residual_by_group = []

    for group in witness_groups:
        prediction = group["prediction"]
        left = prediction.get("left") or {}
        right = prediction.get("right") or {}
        scalar = int_value(prediction.get("predicted_target")) % ORDER
        target_key = (group["window"], group["public_fingerprint"])
        if target_key not in target_col_index:
            target_col_index[target_key] = len(target_col_index)
            local_target_names.append({"public_fingerprint": group["public_fingerprint"], "window": group["window"]})
        target_index = target_col_index[target_key]
        group_residuals = []
        for form in (left, right):
            unique_forms[form_key(form)] = form
            row = [0] * (len(target_col_index) + len(factor_columns))
            # Target columns can grow as new groups are seen; pad previous rows below.
            row[target_index] = int_value(form.get("q_coeff")) % ORDER
            for factor, coeff in factor_signature(form):
                row[len(target_col_index) + factor_col_index[factor]] = coeff % ORDER
            rows.append(row)
            augmented_rows.append([*row, int_value(form.get("rhs")) % ORDER])
            group_residuals.append(residual_for_form(form, scalar))
        residual_by_group.append(
            {
                "artifact": group["artifact"],
                "derived_scalar": scalar,
                "factor_signature": [list(item) for item in factor_signature(left)],
                "models": group["models"],
                "public_fingerprint": group["public_fingerprint"],
                "residuals": group_residuals,
                "residuals_agree_within_pair": len(set(group_residuals)) == 1,
                "source_secrets": prediction.get("source_secrets") or [],
                "window": group["window"],
            }
        )

    # Rows were built while target columns grew; normalize width after the fact.
    final_width = len(target_col_index) + len(factor_columns)
    normalized_rows = []
    normalized_augmented = []
    for row, aug in zip(rows, augmented_rows):
        rhs = aug[-1]
        if len(row) < final_width:
            factor_part = row[-len(factor_columns) :] if factor_columns else []
            target_part = row[: len(row) - len(factor_columns)] if factor_columns else row
            row = target_part + [0] * (len(target_col_index) - len(target_part)) + factor_part
        normalized_rows.append(row)
        normalized_augmented.append([*row, rhs])

    factor_rows = []
    for form in unique_forms.values():
        row = [0] * len(factor_columns)
        for factor, coeff in factor_signature(form):
            row[factor_col_index[factor]] = coeff % ORDER
        factor_rows.append(row)

    unique_residual_values = sorted({tuple(item["residuals"]) for item in residual_by_group})
    unique_single_residuals = sorted({item["residuals"][0] for item in residual_by_group if item["residuals"]})
    unique_factor_signatures = sorted({factor_signature(form) for form in unique_forms.values()})
    coefficient_rank = mod_rank(normalized_rows)
    augmented_rank = mod_rank(normalized_augmented)
    factor_rank = mod_rank(factor_rows)
    globally_consistent = augmented_rank == coefficient_rank
    factor_residual_consistent = len(unique_single_residuals) <= 1

    if globally_consistent and factor_rank > 1 and len(unique_factor_signatures) > 1:
        claim = "P1043_SHARED_FACTOR_RELATION_RANK_SIGNAL"
        taxonomy = "OBSERVATION"
    elif not globally_consistent or not factor_residual_consistent:
        claim = "NEGATIVE_RESULT_P1043_LOCAL_SCALARS_NOT_GLOBAL_FACTOR_CONSISTENT"
        taxonomy = "NEGATIVE RESULT"
    else:
        claim = "NEGATIVE_RESULT_P1043_SINGLE_FACTOR_DIRECTION_ONLY"
        taxonomy = "NEGATIVE RESULT"

    return {
        "artifacts": {
            "contract": str(args.contract),
            "inputs": [str(path) for path in input_paths],
            "script": str(Path(__file__)),
        },
        "artifact_hashes": {
            "contract_sha256": p1005.sha256_file(Path(args.contract)),
            "input_sha256": {str(path): p1005.sha256_file(path) for path in input_paths},
            "script_sha256": p1005.sha256_file(Path(__file__)),
        },
        "claim_status": claim,
        "claim_taxonomy": taxonomy,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime p231 ECDLP harness only.",
            "RANK-AUDIT: tests relation-row structure; it does not generate new witnesses.",
            "LOCAL-TARGETS: target variables are local to each public/window witness group.",
            "SHARED-FACTOR-CHECK: factor columns are shared by index, so inconsistent residuals block global relation pooling.",
            "INDEX-CALCULUS PRECURSOR: scalar predictions alone are not sparse linear algebra closure.",
            "RHO BOUNDARY: Pollard rho remains the one-target scalar-search baseline.",
        ],
        "parameters": {
            "factor_columns": factor_columns,
            "modulus": ORDER,
            "primary_pool": PRIMARY_POOL,
            "strict_tail": list(STRICT_TAIL),
            "strict_terms": list(STRICT_TERMS),
        },
        "residual_by_group": residual_by_group,
        "schema": SCHEMA,
        "summary": {
            "augmented_rank": augmented_rank,
            "claim_status": claim,
            "coefficient_rank": coefficient_rank,
            "factor_column_count": len(factor_columns),
            "factor_columns": factor_columns,
            "factor_rank": factor_rank,
            "factor_residual_consistent": factor_residual_consistent,
            "globally_consistent": globally_consistent,
            "local_target_count": len(target_col_index),
            "unique_factor_signature_count": len(unique_factor_signatures),
            "unique_factor_signatures": [[list(item) for item in signature] for signature in unique_factor_signatures],
            "unique_form_count": len(unique_forms),
            "unique_public_count": len({item["public_fingerprint"] for item in witness_groups}),
            "unique_single_residuals": unique_single_residuals,
            "unique_witness_group_count": len(witness_groups),
        },
        "timestamp": now_iso(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT), help="Experiment contract path")
    parser.add_argument(
        "--inputs",
        default=",".join(str(path) for path in DEFAULT_INPUTS),
        help="Comma-separated input probe paths",
    )
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output JSON path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    summary = payload["summary"]
    print(
        "claim={claim} witnesses={witnesses} forms={forms} coeff_rank={coeff_rank} augmented_rank={aug_rank} factor_rank={factor_rank} residuals={residuals} out={out}".format(
            claim=payload["claim_status"],
            witnesses=summary["unique_witness_group_count"],
            forms=summary["unique_form_count"],
            coeff_rank=summary["coefficient_rank"],
            aug_rank=summary["augmented_rank"],
            factor_rank=summary["factor_rank"],
            residuals=",".join(str(item) for item in summary["unique_single_residuals"]),
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
