#!/usr/bin/env python3
"""P854 anchor-coefficient public baseline audit.

P853 isolated the remaining coefficient problem: support skeletons predict the
non-anchor coefficients, but the coefficient at index 0 remains variable.  This
audit tests simple public baselines for that anchor coefficient under
leave-one-challenge-group-out validation.

This is intentionally a negative-control audit for anchor modeling.  If these
baselines fail, the next step should add richer row/candidate context rather
than retesting majority, transfer, or RHS-only predictors.
"""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p852_transfer_invariant_relation_signature_audit as p852


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P850 = STATE_DIR / "low_term_total2_p850_split_lane_fresh_disjoint_validation_probe.json"
DEFAULT_P851 = STATE_DIR / "low_term_total2_p851_relation_matrix_rank_growth_audit_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p854_anchor_coefficient_public_baseline_audit_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p854_anchor_coefficient_public_baseline_audit.md"
SCHEMA = "ecdlp.low_term_total2_p854_anchor_coefficient_public_baseline_audit.v1"


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


def infer_modulus(samples: list[dict[str, Any]]) -> int | None:
    values = [value for sample in samples for value in sample["coeff_values"]]
    if not values:
        return None
    return max(values) + 1


def inv_mod(value: int, modulus: int) -> int | None:
    if math.gcd(value, modulus) != 1:
        return None
    return pow(value % modulus, -1, modulus)


def fit_affine_predictor(train: list[dict[str, Any]], x_key: str, modulus: int | None) -> tuple[int, int] | None:
    if not train or not modulus:
        return None
    candidates: set[tuple[int, int]] = set()
    # Constant model is included as a degenerate affine candidate.
    for sample in train:
        candidates.add((0, sample["anchor"] % modulus))
    for i, first in enumerate(train):
        for second in train[i + 1 :]:
            dx = (int(first[x_key]) - int(second[x_key])) % modulus
            dy = (int(first["anchor"]) - int(second["anchor"])) % modulus
            inv = inv_mod(dx, modulus)
            if inv is None:
                continue
            a = (dy * inv) % modulus
            b = (int(first["anchor"]) - a * int(first[x_key])) % modulus
            candidates.add((a, b))
    if not candidates:
        return None
    return sorted(
        candidates,
        key=lambda ab: (
            -sum(1 for sample in train if (ab[0] * int(sample[x_key]) + ab[1]) % modulus == sample["anchor"] % modulus),
            ab[0],
            ab[1],
        ),
    )[0]


def collect_samples(args: argparse.Namespace) -> tuple[dict[tuple[str, tuple[int, ...]], list[dict[str, Any]]], list[dict[str, Any]]]:
    group_forms, errors = p852.reconstruct_group_forms(args)
    samples_by_support: dict[tuple[str, tuple[int, ...]], list[dict[str, Any]]] = defaultdict(list)
    for group, payload in group_forms.items():
        target = str(payload["target"])
        meta = payload.get("meta") or {}
        for form in payload["forms"].values():
            support = tuple(int(item) for item in form["support"])
            if 0 not in support:
                continue
            coeffs = tuple(int(item) for item in form["coeffs"])
            coeff_values = tuple(coeffs[index] for index in support)
            anchor = coeffs[0]
            samples_by_support[(target, support)].append(
                {
                    "anchor": int(anchor),
                    "below_rho": bool(meta.get("below_rho")),
                    "coeff_values": coeff_values,
                    "group": group,
                    "group_id": f"{group[0]}|transfer={group[1]}|{group[2]}",
                    "hidden_false_group": bool(meta.get("hidden_false_candidate_count")),
                    "rhs": int(form["rhs"]),
                    "support": support,
                    "target": target,
                    "terms": tuple(int(term) for term in form["terms"]),
                    "transfer_index": int(group[1]),
                }
            )
    return samples_by_support, errors


def evaluate_support(target: str, support: tuple[int, ...], samples: list[dict[str, Any]]) -> dict[str, Any]:
    group_ids = {sample["group_id"] for sample in samples}
    if len(group_ids) < 2:
        return {}
    modulus = infer_modulus(samples)
    counters = Counter()
    predictor_counts: dict[str, Counter[str]] = defaultdict(Counter)
    for sample in samples:
        train = [other for other in samples if other["group_id"] != sample["group_id"]]
        if not train:
            continue
        counters["loto_sample_count"] += 1
        predictors: dict[str, int | None] = {
            "support_majority": majority([other["anchor"] for other in train]),
            "support_terms_majority": majority(
                [other["anchor"] for other in train if other["terms"] == sample["terms"]]
            ),
            "nearest_transfer_same_support": nearest_transfer_anchor(sample, train),
            "rhs_identity": sample["rhs"],
        }
        if modulus:
            predictors["rhs_neg_mod"] = (-sample["rhs"]) % modulus
            affine_rhs = fit_affine_predictor(train, "rhs", modulus)
            affine_transfer = fit_affine_predictor(train, "transfer_index", modulus)
            predictors["best_affine_rhs_mod"] = (
                (affine_rhs[0] * sample["rhs"] + affine_rhs[1]) % modulus if affine_rhs else None
            )
            predictors["best_affine_transfer_mod"] = (
                (affine_transfer[0] * sample["transfer_index"] + affine_transfer[1]) % modulus
                if affine_transfer
                else None
            )
        for name, predicted in predictors.items():
            if predicted is None:
                continue
            predictor_counts[name]["total"] += 1
            if int(predicted) == sample["anchor"]:
                predictor_counts[name]["correct"] += 1
    anchors = [sample["anchor"] for sample in samples]
    return {
        "anchor_unique_count": len(set(anchors)),
        "below_rho_group_count": len({sample["group_id"] for sample in samples if sample["below_rho"]}),
        "form_count": len(samples),
        "group_count": len(group_ids),
        "hidden_false_group_count": len({sample["group_id"] for sample in samples if sample["hidden_false_group"]}),
        "loto_sample_count": counters["loto_sample_count"],
        "modulus_inferred": modulus,
        "predictor_accuracy": {
            name: {
                "correct": counts["correct"],
                "total": counts["total"],
                "accuracy": safe_ratio(counts["correct"], counts["total"]),
            }
            for name, counts in sorted(predictor_counts.items())
        },
        "support": list(support),
        "target": target,
        "term_signature_count": len({sample["terms"] for sample in samples}),
    }


def nearest_transfer_anchor(sample: dict[str, Any], train: list[dict[str, Any]]) -> int | None:
    if not train:
        return None
    closest = sorted(
        train,
        key=lambda other: (
            abs(int(other["transfer_index"]) - int(sample["transfer_index"])),
            str(other["group_id"]),
            int(other["anchor"]),
        ),
    )[0]
    return int(closest["anchor"])


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    samples_by_support, errors = collect_samples(args)
    support_rows = []
    for (target, support), samples in samples_by_support.items():
        row = evaluate_support(target, support, samples)
        if row:
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
            "BASELINE-SCOPE: predictors use support, term signature, transfer index, and RHS only; richer row/candidate features are not tested.",
            "NEGATIVE-CONTROL BOUNDARY: failure of these baselines does not rule out anchor predictability from richer public context.",
            "NO-CROSS-TRANSFER-RANK-MIXING: anchor predictions are scored only as held-out coefficient guesses, not as aggregated rank.",
            "POLLARD-RHO BOUNDARY: this is an anchor-coefficient diagnostic, not a complete faster-than-rho ECDLP algorithm.",
        ],
        "method": "p854_anchor_coefficient_public_baseline_audit",
        "parameters": {
            "prediction_protocol": "leave-one-challenge-group-out inside repeated support signatures",
            "predictors": [
                "support_majority",
                "support_terms_majority",
                "nearest_transfer_same_support",
                "rhs_identity",
                "rhs_neg_mod",
                "best_affine_rhs_mod",
                "best_affine_transfer_mod",
            ],
        },
        "red_team_handoff": {
            "assumptions": [
                "Support, term signature, transfer index, and RHS are reasonable cheap public baselines for anchor prediction.",
                "A failed baseline audit should route P855 toward richer row/candidate features instead of repeating these predictors.",
            ],
            "failure_modes": [
                "A richer public context feature may predict anchors even though these baselines fail.",
                "The inferred modulus heuristic should be replaced with verifier-provided order for any promoted anchor model.",
                "Anchor prediction may be unnecessary if target descent can consume variable-anchor skeletons directly.",
            ],
            "next_concrete_action": (
                "Build P855 to attach row/candidate public features to each anchor sample and test feature-conditioned anchor buckets "
                "or normalization, while keeping P854 predictors as negative controls."
            ),
            "status": "NEGATIVE RESULT" if claim.startswith("NEGATIVE_RESULT") else "HYPOTHESIS",
        },
        "schema": SCHEMA,
        "summary": summarize(support_rows, errors),
        "support_anchor_predictions": support_rows,
    }


def determine_claim(rows: list[dict[str, Any]], errors: list[dict[str, Any]]) -> str:
    if errors:
        return "NEGATIVE_RESULT_P854_RECONSTRUCTION_ERRORS"
    if not rows:
        return "NEGATIVE_RESULT_P854_NO_REPEATED_SUPPORTS"
    summary = summarize(rows, errors)
    best = max(
        (
            value or 0.0
            for key, value in summary.items()
            if key.endswith("_accuracy") and key != "best_predictor_accuracy"
        ),
        default=0.0,
    )
    if best == 0.0:
        return "NEGATIVE_RESULT_P854_ANCHOR_PUBLIC_BASELINES_FAIL"
    if best < 0.1:
        return "NEGATIVE_RESULT_P854_ANCHOR_PUBLIC_BASELINES_NEAR_ZERO"
    return "P854_ANCHOR_PUBLIC_BASELINES_HAVE_PARTIAL_SIGNAL"


def summarize(rows: list[dict[str, Any]], errors: list[dict[str, Any]]) -> dict[str, Any]:
    totals: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        for name, payload in (row.get("predictor_accuracy") or {}).items():
            totals[name]["correct"] += int(payload.get("correct") or 0)
            totals[name]["total"] += int(payload.get("total") or 0)
    accuracies = {
        f"{name}_accuracy": safe_ratio(counts["correct"], counts["total"])
        for name, counts in sorted(totals.items())
    }
    best_name = None
    best_accuracy = None
    for name, accuracy in accuracies.items():
        if accuracy is None:
            continue
        if best_accuracy is None or accuracy > best_accuracy:
            best_name = name.replace("_accuracy", "")
            best_accuracy = accuracy
    return {
        **accuracies,
        "anchor_unique_count_total": sum(int(row.get("anchor_unique_count") or 0) for row in rows),
        "best_predictor": best_name,
        "best_predictor_accuracy": best_accuracy,
        "claim_status": determine_claim_no_recurse(rows, errors, best_accuracy),
        "error_count": len(errors),
        "loto_sample_count": sum(int(row.get("loto_sample_count") or 0) for row in rows),
        "repeated_support_count": len(rows),
    }


def determine_claim_no_recurse(
    rows: list[dict[str, Any]],
    errors: list[dict[str, Any]],
    best_accuracy: float | None,
) -> str:
    if errors:
        return "NEGATIVE_RESULT_P854_RECONSTRUCTION_ERRORS"
    if not rows:
        return "NEGATIVE_RESULT_P854_NO_REPEATED_SUPPORTS"
    best = best_accuracy or 0.0
    if best == 0.0:
        return "NEGATIVE_RESULT_P854_ANCHOR_PUBLIC_BASELINES_FAIL"
    if best < 0.1:
        return "NEGATIVE_RESULT_P854_ANCHOR_PUBLIC_BASELINES_NEAR_ZERO"
    return "P854_ANCHOR_PUBLIC_BASELINES_HAVE_PARTIAL_SIGNAL"


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
