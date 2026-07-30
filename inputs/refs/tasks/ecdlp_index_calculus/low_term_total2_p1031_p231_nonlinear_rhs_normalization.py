#!/usr/bin/env python3
"""P1031 nonlinear RHS-normalization audit for P1030 quotient scopes."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p1005_p231_context_safe_early_stop_order as p1005
import low_term_total2_p1007_p231_expanded_source_policy_compatibility as p1007
import low_term_total2_p1022_p231_leaf19_rank_guard_12376 as p1022
import low_term_total2_p1023_p231_leaf19_relation_bank_audit as p1023
import low_term_total2_p1025_p231_consistency_filtered_quotient_scheduler as p1025
import low_term_total2_p1026_p231_affine_rhs_obstruction_audit as p1026
import low_term_total2_p1030_p231_representation_change_audit as p1030
import low_term_total2_target_eliminated_factor_relation_bank as factor_bank


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1031_p231_nonlinear_rhs_normalization.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1031_p231_nonlinear_rhs_normalization_probe.json"
SCHEMA = "ecdlp.low_term_total2_p1031_p231_nonlinear_rhs_normalization.v1"
ORDER = p1026.ORDER


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def int_value(value: Any, default: int = 0) -> int:
    return p1023.int_value(value, default)


def json_key(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def inv_or_zero(value: int) -> int:
    value %= ORDER
    if not value:
        return 0
    return pow(value, -1, ORDER)


def legendre(value: int) -> int:
    value %= ORDER
    if not value:
        return 0
    symbol = pow(value, (ORDER - 1) // 2, ORDER)
    return -1 if symbol == ORDER - 1 else symbol


def scaled(row: dict[str, Any], value: int) -> int:
    return p1030.scaled(row, value)


def public_xy(row: dict[str, Any]) -> tuple[int, int]:
    return p1030.public_xy(row)


def q_values(row: dict[str, Any]) -> tuple[int, int]:
    q = row.get("q_coeffs") or [0, 0]
    return int_value(q[0]) % ORDER, int_value(q[1]) % ORDER


def factor_coeffs(row: dict[str, Any], factor_count: int) -> list[int]:
    return p1030.factor_coeffs(row, factor_count)


def rhs_values(relations: list[dict[str, Any]]) -> list[int]:
    return p1030.rhs_values(relations)


def matrix_summary(rows: list[list[int]], rhs: list[int]) -> dict[str, Any]:
    return p1030.matrix_summary(rows, rhs)


def rank_mod(rows: list[list[int]]) -> int:
    return p1030.rank_mod(rows)


def support_moments(row: dict[str, Any]) -> list[int]:
    coeffs = row.get("canonical_coeffs") or []
    support = [index for index, value in enumerate(coeffs) if int_value(value) % ORDER]
    moment1 = sum((index + 1) * int_value(coeffs[index]) for index in support)
    moment2 = sum((index + 1) * (index + 1) * int_value(coeffs[index]) for index in support)
    support_product = 1
    for index in support:
        support_product = (support_product * (index + 1)) % ORDER
    return [len(support), moment1 % ORDER, moment2 % ORDER, support_product % ORDER]


def nonlinear_models() -> list[dict[str, Any]]:
    return [
        {
            "description": "Quotient ratios, inverse terms, and quotient squares.",
            "diagnostic_only": False,
            "name": "q_ratio_power",
            "feature_fn": lambda row: q_ratio_power(row),
        },
        {
            "description": "Public quadratic coordinates [1, x, y, x^2, xy, y^2].",
            "diagnostic_only": False,
            "name": "public_quadratic",
            "feature_fn": lambda row: public_quadratic(row),
        },
        {
            "description": "Public rational/Kummer-like coordinates using x/y and y/x.",
            "diagnostic_only": False,
            "name": "public_rational_kummer",
            "feature_fn": lambda row: public_rational_kummer(row),
        },
        {
            "description": "Salt quadratic coordinates and min/max/gap products.",
            "diagnostic_only": False,
            "name": "salt_quadratic",
            "feature_fn": lambda row: salt_quadratic(row),
        },
        {
            "description": "Quotient-salt nonlinear interactions.",
            "diagnostic_only": False,
            "name": "q_salt_nonlinear",
            "feature_fn": lambda row: q_salt_nonlinear(row),
        },
        {
            "description": "Quadratic public-quotient interactions.",
            "diagnostic_only": False,
            "name": "q_public_quadratic",
            "feature_fn": lambda row: q_public_quadratic(row),
        },
        {
            "description": "Legendre/character features of public, quotient, and salt terms.",
            "diagnostic_only": False,
            "name": "character_features",
            "feature_fn": lambda row: character_features(row),
        },
        {
            "description": "Support moments of the canonical factor vector; diagnostic only.",
            "diagnostic_only": True,
            "name": "support_moments_diagnostic",
            "feature_fn": lambda row: [scaled(row, value) for value in support_moments(row)],
        },
    ]


def q_ratio_power(row: dict[str, Any]) -> list[int]:
    ql, qr = q_values(row)
    qsum = (ql + qr) % ORDER
    qdiff = (qr - ql) % ORDER
    values = [
        1,
        ql,
        qr,
        qsum,
        qdiff,
        (ql * ql) % ORDER,
        (qr * qr) % ORDER,
        (ql * qr) % ORDER,
        ql * inv_or_zero(qr),
        qr * inv_or_zero(ql),
        qsum * inv_or_zero(qdiff),
        qdiff * inv_or_zero(qsum),
    ]
    return [scaled(row, value) for value in values]


def public_quadratic(row: dict[str, Any]) -> list[int]:
    x, y = public_xy(row)
    values = [1, x, y, x * x, x * y, y * y, x + y, x - y]
    return [scaled(row, value) for value in values]


def public_rational_kummer(row: dict[str, Any]) -> list[int]:
    x, y = public_xy(row)
    values = [
        1,
        inv_or_zero(x),
        inv_or_zero(y),
        x * inv_or_zero(y),
        y * inv_or_zero(x),
        (x + y) * inv_or_zero((x - y) % ORDER),
        (x - y) * inv_or_zero((x + y) % ORDER),
    ]
    return [scaled(row, value) for value in values]


def salt_quadratic(row: dict[str, Any]) -> list[int]:
    smin = int_value(row.get("salt_min"))
    smax = int_value(row.get("salt_max"))
    gap = int_value(row.get("salt_gap"))
    ssum = int_value(row.get("salt_sum"))
    values = [1, smin, smax, gap, ssum, smin * smin, smax * smax, gap * gap, smin * smax]
    return [scaled(row, value) for value in values]


def q_salt_nonlinear(row: dict[str, Any]) -> list[int]:
    ql, qr = q_values(row)
    qsum = (ql + qr) % ORDER
    qdiff = (qr - ql) % ORDER
    gap = int_value(row.get("salt_gap"))
    smin = int_value(row.get("salt_min"))
    smax = int_value(row.get("salt_max"))
    values = [
        qsum * gap,
        qdiff * gap,
        qsum * gap * gap,
        qdiff * gap * gap,
        ql * smin,
        qr * smax,
        ql * inv_or_zero((gap + 1) % ORDER),
        qr * inv_or_zero((gap + 1) % ORDER),
    ]
    return [scaled(row, value) for value in values]


def q_public_quadratic(row: dict[str, Any]) -> list[int]:
    ql, qr = q_values(row)
    qsum = (ql + qr) % ORDER
    qdiff = (qr - ql) % ORDER
    x, y = public_xy(row)
    values = [
        qsum * x,
        qsum * y,
        qdiff * x,
        qdiff * y,
        qsum * x * x,
        qsum * x * y,
        qsum * y * y,
        qdiff * x * x,
        qdiff * x * y,
        qdiff * y * y,
    ]
    return [scaled(row, value) for value in values]


def character_features(row: dict[str, Any]) -> list[int]:
    ql, qr = q_values(row)
    x, y = public_xy(row)
    gap = int_value(row.get("salt_gap"))
    values = [
        legendre(ql),
        legendre(qr),
        legendre((ql + qr) % ORDER),
        legendre((qr - ql) % ORDER),
        legendre(x),
        legendre(y),
        legendre((x * y) % ORDER),
        legendre(gap),
    ]
    return [scaled(row, value) for value in values]


def model_matrix(relations: list[dict[str, Any]], model: dict[str, Any], factor_count: int) -> tuple[list[list[int]], list[list[int]], list[int]]:
    rows = []
    context_rows = []
    rhs = rhs_values(relations)
    for relation in relations:
        factors = factor_coeffs(relation, factor_count)
        context = [int_value(value) % ORDER for value in model["feature_fn"](relation)]
        rows.append([*factors, *context])
        context_rows.append(context)
    return rows, context_rows, rhs


def summarize_lifted_model(relations: list[dict[str, Any]], model: dict[str, Any], factor_count: int) -> dict[str, Any]:
    rows, context_rows, rhs = model_matrix(relations, model, factor_count)
    matrix = matrix_summary(rows, rhs)
    factor_rank = rank_mod([factor_coeffs(row, factor_count) for row in relations])
    context_rank = rank_mod(context_rows)
    factor_component_rank = max(0, matrix["coefficient_rank"] - context_rank)
    heldout = p1030.heldout_public_check(relations, rows, rhs)
    primary_success = bool(
        not model["diagnostic_only"]
        and matrix["matrix_consistent"]
        and factor_component_rank > 0
        and heldout["heldout_tested"] > 0
        and heldout["heldout_passed"] == heldout["heldout_tested"]
    )
    diagnostic_success = bool(
        model["diagnostic_only"]
        and matrix["matrix_consistent"]
        and factor_component_rank > 0
    )
    return {
        "context_column_count": len(context_rows[0]) if context_rows else 0,
        "context_rank": context_rank,
        "description": model["description"],
        "diagnostic_only": bool(model["diagnostic_only"]),
        "diagnostic_success": diagnostic_success,
        "factor_component_rank": factor_component_rank,
        "factor_rank": factor_rank,
        "heldout": heldout,
        "matrix": matrix,
        "model": model["name"],
        "primary_success": primary_success,
    }


def solve_feature_model(features: list[list[int]], rhs: list[int]) -> list[int] | None:
    if not features:
        return None
    return factor_bank.solve_mod(features, rhs, ORDER)


def predict(features: list[int], coeffs: list[int]) -> int:
    return sum((value % ORDER) * (coeffs[index] % ORDER) for index, value in enumerate(features)) % ORDER


def cluster_rhs_normalizers(relations: list[dict[str, Any]], scope: str) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for relation in relations:
        grouped[json_key(relation.get("canonical_coeffs") or [])].append(relation)
    out = []
    for key, group in sorted(grouped.items()):
        publics = sorted({str(row.get("public_fingerprint")) for row in group})
        rhs = rhs_values(group)
        if len(group) < 2 or len(set(rhs)) < 2:
            continue
        for model in nonlinear_models():
            features = [[int_value(value) % ORDER for value in model["feature_fn"](row)] for row in group]
            coeffs = solve_feature_model(features, rhs)
            exact = bool(coeffs is not None and all(predict(features[index], coeffs) == rhs[index] % ORDER for index in range(len(rhs))))
            loo_tested = 0
            loo_passed = 0
            loo_skipped = 0
            for public in publics:
                train = [index for index, row in enumerate(group) if str(row.get("public_fingerprint")) != public]
                heldout = [index for index, row in enumerate(group) if str(row.get("public_fingerprint")) == public]
                if not train or not heldout:
                    continue
                train_coeffs = solve_feature_model([features[index] for index in train], [rhs[index] for index in train])
                if train_coeffs is None:
                    loo_skipped += len(heldout)
                    continue
                for index in heldout:
                    loo_tested += 1
                    if predict(features[index], train_coeffs) == rhs[index] % ORDER:
                        loo_passed += 1
            viable = bool(
                not model["diagnostic_only"]
                and exact
                and loo_tested > 0
                and loo_passed == loo_tested
                and len(publics) >= 2
            )
            out.append(
                {
                    "coefficient_key": key,
                    "diagnostic_only": bool(model["diagnostic_only"]),
                    "distinct_public_count": len(publics),
                    "distinct_publics": publics,
                    "exact_fit": exact,
                    "feature_count": len(features[0]) if features else 0,
                    "loo_passed": loo_passed,
                    "loo_skipped": loo_skipped,
                    "loo_tested": loo_tested,
                    "model": model["name"],
                    "sample_count": len(group),
                    "scope": scope,
                    "viable_normalizer": viable,
                }
            )
    out.sort(
        key=lambda item: (
            0 if item.get("viable_normalizer") else 1,
            0 if item.get("exact_fit") else 1,
            -int_value(item.get("loo_passed")),
            -int_value(item.get("sample_count")),
            str(item.get("model")),
        )
    )
    return out


def summarize_scope(scope: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    relations, reconstruction = p1030.rows_for_scope(rows)
    factor_count = reconstruction["factor_count"]
    baseline_rows = [factor_coeffs(row, factor_count) for row in relations]
    baseline = matrix_summary(baseline_rows, rhs_values(relations)) if factor_count else matrix_summary([], [])
    models = [summarize_lifted_model(relations, model, factor_count) for model in nonlinear_models()] if factor_count else []
    clusters = cluster_rhs_normalizers(relations, scope)
    primary_models = [model for model in models if model.get("primary_success")]
    diagnostic_models = [model for model in models if model.get("diagnostic_success")]
    viable_clusters = [cluster for cluster in clusters if cluster.get("viable_normalizer")]
    return {
        "baseline": baseline,
        "cluster_normalizer_count": len(clusters),
        "cluster_normalizers": clusters[:24],
        "diagnostic_model_count": len(diagnostic_models),
        "diagnostic_models": diagnostic_models,
        "factor_count": factor_count,
        "lifted_model_summaries": models,
        "primary_model_count": len(primary_models),
        "primary_models": primary_models,
        "reconstruction": reconstruction,
        "relation_count": len(relations),
        "scope": scope,
        "viable_cluster_count": len(viable_clusters),
        "viable_clusters": viable_clusters,
    }


def determine_claim(scopes: list[dict[str, Any]]) -> str:
    if any(scope["reconstruction"]["reconstruction_error_count"] for scope in scopes):
        return "NEGATIVE_RESULT_P1031_RECONSTRUCTION_ERRORS"
    if any(scope["baseline"]["coefficient_rank"] != 2 or scope["baseline"]["augmented_rank"] != 3 for scope in scopes):
        return "NEGATIVE_RESULT_P1031_BASELINE_CONTROL_MISMATCH"
    if any(scope["primary_model_count"] for scope in scopes):
        return "P1031_NONLINEAR_LIFTED_REPRESENTATION_SIGNAL"
    if any(scope["viable_cluster_count"] for scope in scopes):
        return "P1031_NONLINEAR_CLUSTER_RHS_NORMALIZER_SIGNAL"
    if any(scope["diagnostic_model_count"] for scope in scopes):
        return "P1031_DIAGNOSTIC_SUPPORT_NONLINEAR_SIGNAL_ONLY"
    return "NEGATIVE_RESULT_P1031_NONLINEAR_RHS_NORMALIZERS_NO_PROMOTION"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    scope_rows, exists = p1030.build_scopes(args)
    scope_summaries = [summarize_scope(scope, rows) for scope, rows in scope_rows.items()]
    claim = determine_claim(scope_summaries)
    all_windows = [
        *p1022.POSITIVE_CALIBRATION_WINDOWS,
        *p1022.VALIDATION_WINDOWS,
        *p1022.NEGATIVE_CALIBRATION_WINDOWS,
        *p1025.FRESH_WINDOWS,
    ]
    source_hashes = {
        window: p1005.sha256_file(p1007.expanded_source_path(window))
        for window in all_windows
        if p1007.expanded_source_path(window).exists()
    }
    return {
        "artifacts": {
            "contract": str(args.contract),
            "script": str(Path(__file__)),
        },
        "artifact_hashes": {
            "contract_sha256": p1005.sha256_file(Path(args.contract)),
            "p1030_dependency_sha256": p1005.sha256_file(Path(p1030.__file__)),
            "script_sha256": p1005.sha256_file(Path(__file__)),
            "source_sha256": source_hashes,
        },
        "claim_status": claim,
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P1031_") else "NEGATIVE RESULT",
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime p231 ECDLP harness only.",
            "MODEL-BOUND: P1031 tests a finite nonlinear feature catalog, not all nonlinear representations.",
            "INDEX-CALCULUS PRECURSOR: RHS normalization is not sparse linear algebra closure or target descent.",
            "RHO BOUNDARY: Pollard rho remains the one-target baseline.",
        ],
        "parameters": {
            "fresh_windows": p1025.FRESH_WINDOWS,
            "min_source_rank": args.min_source_rank,
            "models": [model["name"] for model in nonlinear_models()],
            "negative_calibration_windows": p1022.NEGATIVE_CALIBRATION_WINDOWS,
            "scopes": list(scope_rows),
            "targets": [target.strip() for target in args.targets.split(",") if target.strip()],
        },
        "schema": SCHEMA,
        "source": {"exists": exists},
        "summary": {
            "claim_status": claim,
            "diagnostic_model_count": sum(int_value(scope.get("diagnostic_model_count")) for scope in scope_summaries),
            "primary_model_count": sum(int_value(scope.get("primary_model_count")) for scope in scope_summaries),
            "scope_count": len(scope_summaries),
            "scope_summaries": [
                {
                    "baseline": scope["baseline"],
                    "cluster_normalizer_count": scope["cluster_normalizer_count"],
                    "diagnostic_model_count": scope["diagnostic_model_count"],
                    "fresh_false_count": scope["reconstruction"]["selection"]["fresh_false_count"],
                    "fresh_positive_count": scope["reconstruction"]["selection"]["fresh_positive_count"],
                    "primary_model_count": scope["primary_model_count"],
                    "relation_count": scope["relation_count"],
                    "scope": scope["scope"],
                    "selected_count": scope["reconstruction"]["selection"]["selected_count"],
                    "viable_cluster_count": scope["viable_cluster_count"],
                }
                for scope in scope_summaries
            ],
            "viable_cluster_count": sum(int_value(scope.get("viable_cluster_count")) for scope in scope_summaries),
        },
        "scopes": scope_summaries,
        "timestamp": now_iso(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT), help="Experiment contract path")
    parser.add_argument("--min-source-rank", type=int, default=2, help="Minimum source rank for builder labels")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output JSON path")
    parser.add_argument("--targets", default=p1022.DEFAULT_TARGET, help="Comma-separated target filter")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    bits = []
    for scope in payload["summary"]["scope_summaries"]:
        baseline = scope["baseline"]
        bits.append(
            "{scope}:rel={rel} rank={rank}/{aug} primary={primary} clusters={clusters}".format(
                scope=scope["scope"],
                rel=scope["relation_count"],
                rank=baseline["coefficient_rank"],
                aug=baseline["augmented_rank"],
                primary=scope["primary_model_count"],
                clusters=scope["viable_cluster_count"],
            )
        )
    print(
        "claim={claim} primary={primary} viable_clusters={clusters} out={out} {bits}".format(
            claim=payload["claim_status"],
            primary=payload["summary"]["primary_model_count"],
            clusters=payload["summary"]["viable_cluster_count"],
            out=args.out,
            bits="; ".join(bits),
        )
    )


if __name__ == "__main__":
    main()
