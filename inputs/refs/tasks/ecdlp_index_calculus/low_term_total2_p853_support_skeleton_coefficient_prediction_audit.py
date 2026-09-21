#!/usr/bin/env python3
"""P853 support-skeleton coefficient prediction audit.

P852 found repeated support and term skeletons across transfers, but no exact
coefficient-vector reuse.  This audit tests the natural narrower hypothesis:
the public support skeleton predicts the non-anchor coefficients, while the
anchor coefficient at index 0 remains transfer-dependent.

Prediction is leave-one-challenge-group-out within each repeated support
signature.  No rank is aggregated across transfers.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p852_transfer_invariant_relation_signature_audit as p852


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P850 = STATE_DIR / "low_term_total2_p850_split_lane_fresh_disjoint_validation_probe.json"
DEFAULT_P851 = STATE_DIR / "low_term_total2_p851_relation_matrix_rank_growth_audit_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p853_support_skeleton_coefficient_prediction_audit_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p853_support_skeleton_coefficient_prediction_audit.md"
SCHEMA = "ecdlp.low_term_total2_p853_support_skeleton_coefficient_prediction_audit.v1"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def majority(values: list[Any]) -> Any:
    counts = Counter(values)
    if not counts:
        return None
    return sorted(counts.items(), key=lambda item: (-item[1], str(item[0])))[0][0]


def safe_ratio(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return round(numerator / denominator, 8)


def group_id(group: tuple[str, int, str]) -> str:
    return f"{group[0]}|transfer={group[1]}|{group[2]}"


def collect_samples(args: argparse.Namespace) -> tuple[dict[tuple[str, tuple[int, ...]], list[dict[str, Any]]], list[dict[str, Any]]]:
    group_forms, errors = p852.reconstruct_group_forms(args)
    samples_by_support: dict[tuple[str, tuple[int, ...]], list[dict[str, Any]]] = defaultdict(list)
    for group, payload in group_forms.items():
        target = str(payload["target"])
        meta = payload.get("meta") or {}
        for form in payload["forms"].values():
            support = tuple(int(item) for item in form["support"])
            coeffs = tuple(int(item) for item in form["coeffs"])
            coeff_values = tuple(coeffs[index] for index in support)
            samples_by_support[(target, support)].append(
                {
                    "below_rho": bool(meta.get("below_rho")),
                    "coeff_values": coeff_values,
                    "group": group,
                    "group_id": group_id(group),
                    "hidden_false_group": bool(meta.get("hidden_false_candidate_count")),
                    "rhs": int(form["rhs"]),
                    "support": support,
                    "target": target,
                    "terms": tuple(int(term) for term in form["terms"]),
                }
            )
    return samples_by_support, errors


def evaluate_support(target: str, support: tuple[int, ...], samples: list[dict[str, Any]]) -> dict[str, Any]:
    group_ids = {sample["group_id"] for sample in samples}
    anchor_positions = [index for index, coeff_index in enumerate(support) if coeff_index == 0]
    non_anchor_positions = [index for index, coeff_index in enumerate(support) if coeff_index != 0]
    repeated = len(group_ids) >= 2
    coeff_columns = list(zip(*(sample["coeff_values"] for sample in samples)))
    unique_counts = [len(set(column)) for column in coeff_columns]
    stable_positions = [index for index, count in enumerate(unique_counts) if count == 1]
    variable_positions = [index for index, count in enumerate(unique_counts) if count > 1]

    counters = Counter()
    for sample in samples:
        train = [other for other in samples if other["group_id"] != sample["group_id"]]
        if not train:
            continue
        counters["loto_sample_count"] += 1
        predicted_full = tuple(majority([other["coeff_values"][pos] for other in train]) for pos in range(len(support)))
        if predicted_full == sample["coeff_values"]:
            counters["full_vector_correct"] += 1
        predicted_non_anchor = tuple(predicted_full[pos] for pos in non_anchor_positions)
        observed_non_anchor = tuple(sample["coeff_values"][pos] for pos in non_anchor_positions)
        if predicted_non_anchor == observed_non_anchor:
            counters["non_anchor_vector_correct"] += 1
        predicted_anchor = tuple(predicted_full[pos] for pos in anchor_positions)
        observed_anchor = tuple(sample["coeff_values"][pos] for pos in anchor_positions)
        if predicted_anchor == observed_anchor:
            counters["anchor_vector_correct"] += 1
        for pos in anchor_positions:
            counters["anchor_coeff_total"] += 1
            if predicted_full[pos] == sample["coeff_values"][pos]:
                counters["anchor_coeff_correct"] += 1
        for pos in non_anchor_positions:
            counters["non_anchor_coeff_total"] += 1
            if predicted_full[pos] == sample["coeff_values"][pos]:
                counters["non_anchor_coeff_correct"] += 1

    representative_non_anchor = []
    for pos in non_anchor_positions:
        representative_non_anchor.append(
            {
                "coefficient_index": support[pos],
                "coefficient_value": samples[0]["coeff_values"][pos],
                "unique_value_count": unique_counts[pos],
            }
        )
    return {
        "anchor_coeff_loto_accuracy": safe_ratio(counters["anchor_coeff_correct"], counters["anchor_coeff_total"]),
        "anchor_position_count": len(anchor_positions),
        "anchor_positions": [support[pos] for pos in anchor_positions],
        "anchor_unique_value_count": max((unique_counts[pos] for pos in anchor_positions), default=0),
        "below_rho_group_count": len({sample["group_id"] for sample in samples if sample["below_rho"]}),
        "form_count": len(samples),
        "full_vector_loto_accuracy": safe_ratio(counters["full_vector_correct"], counters["loto_sample_count"]),
        "group_count": len(group_ids),
        "hidden_false_group_count": len({sample["group_id"] for sample in samples if sample["hidden_false_group"]}),
        "loto_sample_count": counters["loto_sample_count"],
        "non_anchor_coeff_loto_accuracy": safe_ratio(
            counters["non_anchor_coeff_correct"],
            counters["non_anchor_coeff_total"],
        ),
        "non_anchor_position_count": len(non_anchor_positions),
        "non_anchor_vector_loto_accuracy": safe_ratio(
            counters["non_anchor_vector_correct"],
            counters["loto_sample_count"],
        ),
        "representative_non_anchor_coefficients": representative_non_anchor,
        "repeated": repeated,
        "stable_position_count": len(stable_positions),
        "support": list(support),
        "supports_anchor_index_zero": bool(anchor_positions),
        "target": target,
        "term_signatures": [
            {"count": count, "terms": list(terms)}
            for terms, count in Counter(sample["terms"] for sample in samples).most_common(5)
        ],
        "variable_position_count": len(variable_positions),
        "variable_positions": [support[pos] for pos in variable_positions],
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    samples_by_support, errors = collect_samples(args)
    support_rows = []
    for (target, support), samples in samples_by_support.items():
        row = evaluate_support(target, support, samples)
        if row["repeated"]:
            support_rows.append(row)
    support_rows = sorted(
        support_rows,
        key=lambda row: (-row["group_count"], -row["form_count"], row["target"], row["support"]),
    )
    claim = determine_claim(support_rows, errors)
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p850_source": str(args.p850),
            "p851_source": str(args.p851),
            "script": str(Path(__file__)),
        },
        "claim_status": claim,
        "created_at": now_iso(),
        "errors": errors,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP FFE quotient harness only.",
            "PREDICTION BOUNDARY: leave-one-challenge-group-out prediction is performed within repeated support signatures already discovered by P852.",
            "ANCHOR BOUNDARY: the coefficient at index 0 remains transfer-dependent and is reported separately from non-anchor coefficients.",
            "NO-CROSS-TRANSFER-RANK-MIXING: repeated coefficient skeletons are not combined into a global linear system.",
            "POLLARD-RHO BOUNDARY: this is coefficient-structure evidence for an index-calculus precursor, not a complete faster-than-rho ECDLP algorithm.",
        ],
        "method": "p853_support_skeleton_coefficient_prediction_audit",
        "parameters": {
            "anchor_coefficient_index": 0,
            "prediction_protocol": "leave-one-challenge-group-out majority within each repeated support signature",
        },
        "red_team_handoff": {
            "assumptions": [
                "Coefficient index 0 is the structurally separate anchor coefficient and may remain transfer-dependent.",
                "A stable non-anchor coefficient tail is useful for designing a reusable relation skeleton generator.",
                "P852 repeated support signatures are public enough to be the conditioning variable for this audit.",
            ],
            "failure_modes": [
                "The stable non-anchor tail may be a toy factor-base artifact.",
                "The anchor coefficient may remain unpredictable and dominate target descent.",
                "A support skeleton generator may not reduce relation collection cost after full charging.",
            ],
            "next_concrete_action": (
                "Build P854 to model the anchor coefficient for the top support skeletons using public row context, transfer index, "
                "term signature, and candidate factor features; compare against majority, random, and per-target modular baselines."
            ),
            "status": "HYPOTHESIS" if claim.startswith("P853_") else "NEGATIVE RESULT",
        },
        "schema": SCHEMA,
        "summary": summarize(support_rows, errors),
        "support_predictions": support_rows,
    }


def determine_claim(rows: list[dict[str, Any]], errors: list[dict[str, Any]]) -> str:
    if errors:
        return "NEGATIVE_RESULT_P853_RECONSTRUCTION_ERRORS"
    if not rows:
        return "NEGATIVE_RESULT_P853_NO_REPEATED_SUPPORTS"
    non_anchor_totals = [row for row in rows if row.get("non_anchor_coeff_loto_accuracy") is not None]
    anchor_totals = [row for row in rows if row.get("anchor_coeff_loto_accuracy") is not None]
    if (
        non_anchor_totals
        and all(row["non_anchor_coeff_loto_accuracy"] == 1.0 for row in non_anchor_totals)
        and any((row.get("anchor_coeff_loto_accuracy") or 0.0) < 0.5 for row in anchor_totals)
    ):
        return "P853_SUPPORT_SKELETON_PREDICTS_NONANCHOR_COEFFICIENTS_ONLY"
    if non_anchor_totals and any(row["non_anchor_coeff_loto_accuracy"] > 0.5 for row in non_anchor_totals):
        return "P853_SUPPORT_SKELETON_PARTIALLY_PREDICTS_COEFFICIENTS"
    return "NEGATIVE_RESULT_P853_SUPPORT_SKELETON_COEFFICIENT_PREDICTION_NOT_FOUND"


def summarize(rows: list[dict[str, Any]], errors: list[dict[str, Any]]) -> dict[str, Any]:
    loto_samples = sum(int(row.get("loto_sample_count") or 0) for row in rows)
    non_anchor_correct = 0
    non_anchor_total = 0
    anchor_correct = 0
    anchor_total = 0
    full_correct = 0
    non_anchor_vector_correct = 0
    for row in rows:
        samples = int(row.get("loto_sample_count") or 0)
        if row.get("full_vector_loto_accuracy") is not None:
            full_correct += round(row["full_vector_loto_accuracy"] * samples)
        if row.get("non_anchor_vector_loto_accuracy") is not None:
            non_anchor_vector_correct += round(row["non_anchor_vector_loto_accuracy"] * samples)
        non_anchor_total += samples * int(row.get("non_anchor_position_count") or 0)
        anchor_total += samples * int(row.get("anchor_position_count") or 0)
        if row.get("non_anchor_coeff_loto_accuracy") is not None:
            non_anchor_correct += round(row["non_anchor_coeff_loto_accuracy"] * samples * int(row.get("non_anchor_position_count") or 0))
        if row.get("anchor_coeff_loto_accuracy") is not None:
            anchor_correct += round(row["anchor_coeff_loto_accuracy"] * samples * int(row.get("anchor_position_count") or 0))
    return {
        "anchor_coeff_loto_accuracy": safe_ratio(anchor_correct, anchor_total),
        "error_count": len(errors),
        "full_vector_loto_accuracy": safe_ratio(full_correct, loto_samples),
        "loto_sample_count": loto_samples,
        "non_anchor_coeff_loto_accuracy": safe_ratio(non_anchor_correct, non_anchor_total),
        "non_anchor_vector_loto_accuracy": safe_ratio(non_anchor_vector_correct, loto_samples),
        "repeated_support_count": len(rows),
        "supports_with_anchor_index_zero": sum(1 for row in rows if row.get("supports_anchor_index_zero")),
        "supports_with_all_non_anchor_coefficients_predicted": sum(
            1 for row in rows if row.get("non_anchor_coeff_loto_accuracy") == 1.0
        ),
        "supports_with_full_vector_predicted": sum(
            1 for row in rows if row.get("full_vector_loto_accuracy") == 1.0
        ),
        "supports_with_variable_anchor_only": sum(
            1
            for row in rows
            if row.get("variable_positions") == [0]
            and row.get("non_anchor_coeff_loto_accuracy") == 1.0
        ),
        "claim_status": determine_claim(rows, errors),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p850", type=Path, default=DEFAULT_P850)
    parser.add_argument("--p851", type=Path, default=DEFAULT_P851)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
