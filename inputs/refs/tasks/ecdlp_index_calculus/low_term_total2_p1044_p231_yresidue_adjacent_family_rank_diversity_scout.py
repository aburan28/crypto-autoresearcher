#!/usr/bin/env python3
"""P1044 y-residue adjacent-family factor-rank diversity scout."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p1005_p231_context_safe_early_stop_order as p1005
import low_term_total2_p1007_p231_expanded_source_policy_compatibility as p1007
import low_term_total2_p1022_p231_leaf19_rank_guard_12376 as p1022
import low_term_total2_p1023_p231_leaf19_relation_bank_audit as p1023
import low_term_total2_p1033_p231_leaf8_factor_label_extraction_scout as p1033
import low_term_total2_p1035_p231_leaf8_exact_tail_supply_expansion as p1035
import low_term_total2_p1036_p231_adjacent_family_supply_scout as p1036
import low_term_total2_p1038_p231_guarded_structural_family_supply_search as p1038
import low_term_total2_p1039_p231_strict_leaf8_route_validation as p1039
import low_term_total2_p1041_p231_yresidue_strict_route_validation as p1041
import low_term_total2_p1043_p231_yresidue_relation_rank_audit as p1043


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1044_p231_yresidue_adjacent_family_rank_diversity_scout.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1044_p231_yresidue_adjacent_family_rank_diversity_scout_probe.json"
SCHEMA = "ecdlp.low_term_total2_p1044_p231_yresidue_adjacent_family_rank_diversity_scout.v1"
ORDER = p1033.ORDER
SIGNAL_WINDOW = p1039.SIGNAL_WINDOW
DEFAULT_START = "12504_12511"
DEFAULT_MAX_WINDOWS = 64
BASE_SIGNATURE = ((8, 11777), (11, 11777))
BASE_RESIDUAL = 5459


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def int_value(value: Any, default: int = 0) -> int:
    return p1023.int_value(value, default)


def vector_from_signature(signature: tuple[tuple[int, int], ...], columns: list[int]) -> list[int]:
    values = dict(signature)
    return [int_value(values.get(column)) % ORDER for column in columns]


def rank_with_base(signature: tuple[tuple[int, int], ...], residuals: set[int]) -> dict[str, Any]:
    columns = sorted({factor for factor, _coeff in BASE_SIGNATURE} | {factor for factor, _coeff in signature})
    base_row = vector_from_signature(BASE_SIGNATURE, columns)
    sig_row = vector_from_signature(signature, columns)
    factor_rank = p1043.mod_rank([base_row, sig_row], ORDER)
    augmented_consistent = False
    augmented_rank = None
    if len(residuals) == 1:
        residual = next(iter(residuals))
        augmented_rank = p1043.mod_rank([[*base_row, BASE_RESIDUAL], [*sig_row, residual]], ORDER)
        augmented_consistent = augmented_rank == factor_rank
    return {
        "augmented_consistent_with_base": augmented_consistent,
        "augmented_rank_with_base": augmented_rank,
        "factor_rank_with_base": factor_rank,
        "rank_gain_over_base": factor_rank > 1,
    }


def form_signature(form: dict[str, Any], factor_count: int) -> tuple[tuple[int, int], ...]:
    return tuple(p1033.nonzero_factor_entries(form, factor_count))


def residual_for_form(form: dict[str, Any], scalar: int) -> int:
    q = p1036.q_coeff(form)
    rhs = int_value(form.get("rhs")) % ORDER
    return (rhs - q * scalar) % ORDER


def family_key(form: dict[str, Any]) -> tuple[Any, ...]:
    return (p1036.terms_tuple(form), p1036.tail_support_tuple(form))


def passes_p1044_filter(form: dict[str, Any]) -> bool:
    return p1036.is_repeated_two_tail(form) and p1038.passes_guard(form) and p1041.passes_y_filter(form)


def prediction_key(record: dict[str, Any]) -> tuple[Any, ...]:
    return (
        record["pool"],
        record["view"],
        record["window"],
        record["public_fingerprint"],
        tuple(record["family_terms"]),
        tuple(record["family_tail"]),
        tuple(record["q_pair"]),
        tuple(record["rhs_pair"]),
        record["predicted_target"],
        tuple(tuple(item) for item in record["factor_signature"]),
    )


def collect_predictions(forms: list[dict[str, Any]], factor_count: int, windows: list[str], pool: str, view: str) -> dict[str, Any]:
    window_set = set(windows)
    grouped: dict[tuple[str, str, str], list[tuple[int, dict[str, Any]]]] = defaultdict(list)
    for index, form in enumerate(forms):
        if p1036.form_window(form) not in window_set or not passes_p1044_filter(form):
            continue
        for spec in p1036.object_specs():
            key = (
                p1036.public_key(form),
                p1036.form_window(form),
                p1038.json_key((spec["name"], spec["key_fn"](form))),
            )
            grouped[key].append((index, form))

    records_by_key: dict[tuple[Any, ...], dict[str, Any]] = {}
    group_count = len(grouped)
    q_diverse_group_count = 0
    no_prediction_q_diverse_group_count = 0
    for (_public, _window, _object_key), group in grouped.items():
        q_values = sorted({p1036.q_coeff(form) for _index, form in group})
        if len(group) < 2 or len(q_values) < 2:
            continue
        q_diverse_group_count += 1
        any_prediction = False
        for left_offset, (_left_index, left) in enumerate(group):
            for _right_index, right in group[left_offset + 1 :]:
                predicted = p1033.derive_target_from_pair(left, right, factor_count)
                if predicted is None:
                    continue
                any_prediction = True
                source_secrets = sorted(
                    {
                        int_value(value) % ORDER
                        for value in (left.get("source_secret"), right.get("source_secret"))
                        if value is not None
                    }
                )
                verified = bool(source_secrets and all(predicted == secret for secret in source_secrets))
                q_pair = sorted([p1036.q_coeff(left), p1036.q_coeff(right)])
                rhs_pair = sorted([int_value(left.get("rhs")) % ORDER, int_value(right.get("rhs")) % ORDER])
                signature = form_signature(left, factor_count)
                residuals = [residual_for_form(left, predicted), residual_for_form(right, predicted)]
                terms, tail = family_key(left)
                record = {
                    "factor_signature": [list(item) for item in signature],
                    "family_tail": list(tail),
                    "family_terms": list(terms),
                    "model_count": 1,
                    "models": [],
                    "pool": pool,
                    "predicted_target": predicted,
                    "public_fingerprint": p1036.public_key(left),
                    "q_pair": q_pair,
                    "residuals": residuals,
                    "residuals_agree_within_pair": len(set(residuals)) == 1,
                    "rhs_pair": rhs_pair,
                    "source_secrets": source_secrets,
                    "toy_secret_verified": verified,
                    "view": view,
                    "window": p1036.form_window(left),
                }
                key = prediction_key(record)
                if key not in records_by_key:
                    records_by_key[key] = record
                    records_by_key[key]["models"] = set()
                records_by_key[key]["models"].add("dedup_object")
        if not any_prediction:
            no_prediction_q_diverse_group_count += 1

    records = []
    for record in records_by_key.values():
        record["models"] = sorted(record["models"])
        record["model_count"] = len(record["models"])
        records.append(record)
    true_count = sum(1 for item in records if item["toy_secret_verified"])
    false_count = sum(1 for item in records if not item["toy_secret_verified"])
    return {
        "eligible_form_count": sum(len(group) for group in grouped.values()),
        "false_count": false_count,
        "group_count": group_count,
        "no_prediction_q_diverse_group_count": no_prediction_q_diverse_group_count,
        "prediction_count": len(records),
        "q_diverse_group_count": q_diverse_group_count,
        "records": sorted(records, key=lambda item: (item["pool"], item["view"], item["window"], item["public_fingerprint"], item["predicted_target"])),
        "true_count": true_count,
    }


def evaluate_pool(
    pool: dict[str, Any],
    forward_by_window: dict[str, list[dict[str, Any]]],
    windows: list[str],
) -> dict[str, Any]:
    rows = p1039.selected_rows_for_pool(forward_by_window, windows, pool["predicate"])
    evaluations = []
    for compressed in (False, True):
        view = "compressed" if compressed else "raw"
        forms, meta = reconstruct_by_window(forward_by_window, windows, pool["predicate"], compressed)
        factor_count = max([max(0, len(form.get("coeffs") or []) - 1) for form in forms] or [0])
        result = collect_predictions(forms, factor_count, windows, pool["name"], view)
        result["meta"] = meta
        result["view"] = view
        evaluations.append(result)
    return {
        "description": pool["description"],
        "evaluations": evaluations,
        "name": pool["name"],
        "row_count": len(rows),
    }


def reconstruct_by_window(
    by_window: dict[str, list[dict[str, Any]]],
    windows: list[str],
    predicate: p1035.RowPredicate,
    compressed: bool,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    all_forms: list[dict[str, Any]] = []
    raw_row_count = 0
    input_row_count = 0
    reconstructed_case_count = 0
    reconstruction_error_count = 0
    raw_form_count = 0
    for window in windows:
        rows = p1039.selected_rows_for_pool(by_window, [window], predicate)
        forms, meta = p1036.reconstruct_pool(rows, compressed)
        all_forms.extend(forms)
        raw_row_count += int_value(meta.get("raw_row_count"))
        input_row_count += int_value(meta.get("input_row_count"))
        reconstructed_case_count += int_value(meta.get("reconstructed_case_count"))
        reconstruction_error_count += int_value(meta.get("reconstruction_error_count"))
        raw_form_count += int_value(meta.get("form_count"))
    return all_forms, {
        "compressed": compressed,
        "form_count": raw_form_count,
        "input_row_count": input_row_count,
        "raw_row_count": raw_row_count,
        "reconstructed_case_count": reconstructed_case_count,
        "reconstruction_error_count": reconstruction_error_count,
        "unique_form_count": len(p1023.unique_forms(all_forms)),
    }


def aggregate_signature_summaries(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_signature: dict[tuple[tuple[int, int], ...], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        signature = tuple((int_value(index), int_value(coeff) % ORDER) for index, coeff in record["factor_signature"])
        by_signature[signature].append(record)

    summaries = []
    for signature, items in sorted(by_signature.items()):
        residuals = {
            item["residuals"][0]
            for item in items
            if item["residuals_agree_within_pair"] and item.get("residuals")
        }
        rank_info = rank_with_base(signature, residuals)
        true_count = sum(1 for item in items if item["toy_secret_verified"])
        false_count = sum(1 for item in items if not item["toy_secret_verified"])
        families = sorted({(tuple(item["family_terms"]), tuple(item["family_tail"])) for item in items})
        pools = sorted({item["pool"] for item in items})
        windows = sorted({item["window"] for item in items})
        summaries.append(
            {
                "augmented_consistent_with_base": rank_info["augmented_consistent_with_base"],
                "augmented_rank_with_base": rank_info["augmented_rank_with_base"],
                "candidate_success": bool(
                    signature != BASE_SIGNATURE
                    and true_count > 0
                    and false_count == 0
                    and len(residuals) == 1
                    and rank_info["rank_gain_over_base"]
                    and rank_info["augmented_consistent_with_base"]
                ),
                "factor_rank_with_base": rank_info["factor_rank_with_base"],
                "factor_signature": [list(item) for item in signature],
                "false_count": false_count,
                "families": [
                    {"tail": list(tail), "terms": list(terms)}
                    for terms, tail in families[:16]
                ],
                "is_base_signature": signature == BASE_SIGNATURE,
                "pools": pools,
                "rank_gain_over_base": rank_info["rank_gain_over_base"],
                "residuals": sorted(residuals),
                "true_count": true_count,
                "unique_family_count": len(families),
                "unique_public_count": len({item["public_fingerprint"] for item in items}),
                "unique_window_count": len(windows),
                "witness_count": len(items),
            }
        )
    summaries.sort(
        key=lambda item: (
            not item["candidate_success"],
            item["false_count"],
            not item["rank_gain_over_base"],
            -item["true_count"],
            item["factor_signature"],
        )
    )
    return summaries


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    windows = p1038.discover_forward_windows(args.start_window, args.max_windows)
    forward_by_window, forward_exists = p1035.load_rows(windows, args.targets, args.min_source_rank)
    pool_results = [evaluate_pool(pool, forward_by_window, windows) for pool in p1035.pool_specs()]
    compressed_records = [
        record
        for pool in pool_results
        for evaluation in pool["evaluations"]
        if evaluation["view"] == "compressed"
        for record in evaluation["records"]
    ]
    raw_records = [
        record
        for pool in pool_results
        for evaluation in pool["evaluations"]
        if evaluation["view"] == "raw"
        for record in evaluation["records"]
    ]
    signature_summaries = aggregate_signature_summaries(compressed_records)
    candidate_summaries = [item for item in signature_summaries if item["candidate_success"]]
    if candidate_summaries:
        claim = "P1044_ADJACENT_YRESIDUE_RANK_DIVERSITY_CANDIDATE"
        taxonomy = "OBSERVATION"
    elif any(item["rank_gain_over_base"] and item["true_count"] for item in signature_summaries):
        claim = "NEGATIVE_RESULT_P1044_INDEPENDENT_SIGNATURES_NOT_CLEAN"
        taxonomy = "NEGATIVE RESULT"
    else:
        claim = "NEGATIVE_RESULT_P1044_NO_INDEPENDENT_YRESIDUE_SIGNATURE"
        taxonomy = "NEGATIVE RESULT"

    source_hashes = {
        window: p1005.sha256_file(p1007.expanded_source_path(window))
        for window in windows
        if p1007.expanded_source_path(window).exists()
    }
    return {
        "artifacts": {
            "contract": str(args.contract),
            "script": str(Path(__file__)),
        },
        "artifact_hashes": {
            "contract_sha256": p1005.sha256_file(Path(args.contract)),
            "script_sha256": p1005.sha256_file(Path(__file__)),
            "source_sha256": source_hashes,
        },
        "claim_status": claim,
        "claim_taxonomy": taxonomy,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime p231 ECDLP harness only.",
            "SCOUT: adjacent-family candidates are post-P1043 and require frozen holdout validation.",
            "PUBLIC-FILTER: y mod 11 in {2,7} and public repeated-two-tail metadata are used before scoring labels.",
            "COMPRESSED-PRIMARY: signature claims are based on row-signature-compressed records; raw records are diagnostic.",
            "INDEX-CALCULUS PRECURSOR: rank-diversity candidates are not sparse linear algebra closure.",
            "RHO BOUNDARY: Pollard rho remains the one-target scalar-search baseline.",
        ],
        "parameters": {
            "base_residual": BASE_RESIDUAL,
            "base_signature": [list(item) for item in BASE_SIGNATURE],
            "forward_windows": windows,
            "max_windows": args.max_windows,
            "min_source_rank": args.min_source_rank,
            "start_window": args.start_window,
            "targets": [target.strip() for target in args.targets.split(",") if target.strip()],
            "y_allowed": sorted(p1041.Y_ALLOWED),
            "y_modulus": p1041.Y_MODULUS,
        },
        "pool_results": [
            {
                "description": pool["description"],
                "evaluations": [
                    {key: value for key, value in evaluation.items() if key != "records"}
                    for evaluation in pool["evaluations"]
                ],
                "name": pool["name"],
                "row_count": pool["row_count"],
            }
            for pool in pool_results
        ],
        "raw_diagnostic_summary": {
            "false_count": sum(1 for record in raw_records if not record["toy_secret_verified"]),
            "prediction_count": len(raw_records),
            "true_count": sum(1 for record in raw_records if record["toy_secret_verified"]),
            "unique_factor_signature_count": len(
                {
                    tuple((int_value(index), int_value(coeff) % ORDER) for index, coeff in record["factor_signature"])
                    for record in raw_records
                }
            ),
        },
        "schema": SCHEMA,
        "signature_summaries": signature_summaries[:128],
        "source": {
            "forward_exists": forward_exists,
        },
        "summary": {
            "candidate_count": len(candidate_summaries),
            "claim_status": claim,
            "compressed_false_count": sum(1 for record in compressed_records if not record["toy_secret_verified"]),
            "compressed_prediction_count": len(compressed_records),
            "compressed_true_count": sum(1 for record in compressed_records if record["toy_secret_verified"]),
            "independent_signature_count": sum(1 for item in signature_summaries if item["rank_gain_over_base"]),
            "top_candidates": candidate_summaries[:16],
            "unique_compressed_factor_signature_count": len(signature_summaries),
        },
        "timestamp": now_iso(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT), help="Experiment contract path")
    parser.add_argument("--max-windows", type=int, default=DEFAULT_MAX_WINDOWS, help="Maximum forward windows to scan")
    parser.add_argument("--min-source-rank", type=int, default=0, help="Minimum source rank for expanded row loading")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output JSON path")
    parser.add_argument("--start-window", default=DEFAULT_START, help="First forward window to scan")
    parser.add_argument("--targets", default=p1022.DEFAULT_TARGET, help="Comma-separated target filter")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    summary = payload["summary"]
    print(
        "claim={claim} windows={first}..{last} compressed_pred={pred} compressed_false={false} signatures={sigs} independent={ind} candidates={cand} out={out}".format(
            claim=payload["claim_status"],
            first=payload["parameters"]["forward_windows"][0] if payload["parameters"]["forward_windows"] else "none",
            last=payload["parameters"]["forward_windows"][-1] if payload["parameters"]["forward_windows"] else "none",
            pred=summary["compressed_prediction_count"],
            false=summary["compressed_false_count"],
            sigs=summary["unique_compressed_factor_signature_count"],
            ind=summary["independent_signature_count"],
            cand=summary["candidate_count"],
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
