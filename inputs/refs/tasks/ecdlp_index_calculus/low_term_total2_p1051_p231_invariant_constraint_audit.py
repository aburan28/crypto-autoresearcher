#!/usr/bin/env python3
"""P1051 low-degree invariant-constraint audit after P1050."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import low_term_total2_p1005_p231_context_safe_early_stop_order as p1005
import low_term_total2_p1045_p231_yresidue_representation_change_rank_scout as p1045
import low_term_total2_p1047_p231_fresh_row_representation_validation as p1047
import low_term_total2_p1048_p231_coefficient_transform_representation_audit as p1048
import low_term_total2_p1050_p231_nonlinear_two_feature_transform_audit as p1050


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1051_p231_invariant_constraint_audit.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1051_p231_invariant_constraint_audit_probe.json"
DEFAULT_P1050_INPUT = STATE_DIR / "low_term_total2_p1050_p231_nonlinear_two_feature_transform_audit_probe.json"
DEFAULT_INPUTS = p1045.DEFAULT_INPUTS
SCHEMA = "ecdlp.low_term_total2_p1051_p231_invariant_constraint_audit.v1"
ORDER = p1045.ORDER
DEFAULT_START = "12504_12511"
DEFAULT_MAX_WINDOWS = 64
DEFAULT_TRIALS = 64

MonomialFn = Callable[[dict[str, int]], int]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def stable_seed(text: str) -> int:
    return int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:16], 16)


def serializable_counter(counter: Counter[Any]) -> dict[str, int]:
    return {str(key): int(value) for key, value in sorted(counter.items(), key=lambda item: str(item[0]))}


def inv_or_zero(value: int) -> int:
    value %= ORDER
    if value == 0:
        return 0
    return pow(value, ORDER - 2, ORDER)


def public_xy_for_row(row: dict[str, Any], public_xy_override: dict[str, tuple[int, int]] | None = None) -> tuple[int, int]:
    public = p1045.public_key_value(row["form"])
    if public_xy_override and public in public_xy_override:
        x, y = public_xy_override[public]
        return x % ORDER, y % ORDER
    return p1048.feature_x(row["form"]) % ORDER, p1048.feature_y(row["form"]) % ORDER


def qrhs_for_row(row: dict[str, Any], qrhs_override: dict[str, tuple[int, int]] | None = None) -> tuple[int, int]:
    identity = row["identity"]
    if qrhs_override and identity in qrhs_override:
        q, rhs = qrhs_override[identity]
        return q % ORDER, rhs % ORDER
    return p1045.q_coeff_value(row["form"]) % ORDER, p1045.int_value(row["form"].get("rhs")) % ORDER


def point_features(
    row: dict[str, Any],
    public_xy_override: dict[str, tuple[int, int]] | None = None,
    qrhs_override: dict[str, tuple[int, int]] | None = None,
) -> dict[str, int]:
    x, y = public_xy_for_row(row, public_xy_override)
    q, rhs = qrhs_for_row(row, qrhs_override)
    return {
        "one": 1,
        "disc": (x * x - 4 * y) % ORDER,
        "kummer": (x + inv_or_zero(x)) % ORDER,
        "norm": (x * y) % ORDER,
        "q": q,
        "residual": p1045.int_value(row["residual"]) % ORDER,
        "rhs": rhs,
        "trace": (x + y) % ORDER,
        "x": x,
        "x_mod_11": x % 11,
        "y": y,
        "y_mod_5": y % 5,
        "y_over_x": (y * inv_or_zero(x)) % ORDER,
        "y_over_x_plus_1": (y * inv_or_zero(x + 1)) % ORDER,
    }


def monomial(name: str, fn: MonomialFn) -> tuple[str, MonomialFn]:
    return name, fn


def template_specs() -> list[dict[str, Any]]:
    def v(name: str) -> MonomialFn:
        return lambda features: features[name] % ORDER

    def mul(left: str, right: str) -> MonomialFn:
        return lambda features: (features[left] * features[right]) % ORDER

    def square(name: str) -> MonomialFn:
        return lambda features: (features[name] * features[name]) % ORDER

    return [
        {
            "description": "Diagnostic scalar-derived residual identity; positive control only.",
            "diagnostic_control": True,
            "monomials": [
                monomial("1", v("one")),
                monomial("residual", v("residual")),
            ],
            "name": "residual_constant_sanity",
            "promotable": False,
        },
        {
            "description": "Diagnostic row-source-only affine/quadratic identity; excludes public coordinates.",
            "diagnostic_control": True,
            "monomials": [
                monomial("1", v("one")),
                monomial("q", v("q")),
                monomial("rhs", v("rhs")),
                monomial("q2", square("q")),
                monomial("rhs2", square("rhs")),
                monomial("q_rhs", mul("q", "rhs")),
            ],
            "name": "source_only_quadratic",
            "promotable": False,
        },
        {
            "description": "Affine identity over public coordinates and public row source coefficients.",
            "diagnostic_control": False,
            "monomials": [
                monomial("1", v("one")),
                monomial("x", v("x")),
                monomial("y", v("y")),
                monomial("q", v("q")),
                monomial("rhs", v("rhs")),
            ],
            "name": "affine_public_source",
            "promotable": True,
        },
        {
            "description": "Quadratic public-coordinate terms with affine row source coefficients.",
            "diagnostic_control": False,
            "monomials": [
                monomial("1", v("one")),
                monomial("x", v("x")),
                monomial("y", v("y")),
                monomial("q", v("q")),
                monomial("rhs", v("rhs")),
                monomial("x2", square("x")),
                monomial("y2", square("y")),
                monomial("xy", mul("x", "y")),
            ],
            "name": "public_quadratic_source_affine",
            "promotable": True,
        },
        {
            "description": "Bilinear coupling between public coordinates and row source coefficients.",
            "diagnostic_control": False,
            "monomials": [
                monomial("1", v("one")),
                monomial("x", v("x")),
                monomial("y", v("y")),
                monomial("q", v("q")),
                monomial("rhs", v("rhs")),
                monomial("x_q", mul("x", "q")),
                monomial("y_q", mul("y", "q")),
                monomial("x_rhs", mul("x", "rhs")),
                monomial("y_rhs", mul("y", "rhs")),
            ],
            "name": "public_source_bilinear",
            "promotable": True,
        },
        {
            "description": "Rational/Kummer public features coupled to row source coefficients.",
            "diagnostic_control": False,
            "monomials": [
                monomial("1", v("one")),
                monomial("y_over_x", v("y_over_x")),
                monomial("y_over_x_plus_1", v("y_over_x_plus_1")),
                monomial("kummer", v("kummer")),
                monomial("q", v("q")),
                monomial("rhs", v("rhs")),
                monomial("y_over_x_q", mul("y_over_x", "q")),
                monomial("y_over_x_plus_1_q", mul("y_over_x_plus_1", "q")),
                monomial("kummer_q", mul("kummer", "q")),
            ],
            "name": "rational_public_source",
            "promotable": True,
        },
        {
            "description": "Trace/norm/discriminant public features coupled to row source coefficients.",
            "diagnostic_control": False,
            "monomials": [
                monomial("1", v("one")),
                monomial("trace", v("trace")),
                monomial("norm", v("norm")),
                monomial("disc", v("disc")),
                monomial("q", v("q")),
                monomial("rhs", v("rhs")),
                monomial("trace_q", mul("trace", "q")),
                monomial("norm_q", mul("norm", "q")),
                monomial("disc_q", mul("disc", "q")),
            ],
            "name": "trace_norm_disc_source",
            "promotable": True,
        },
        {
            "description": "Small public residue features coupled to row source coefficients.",
            "diagnostic_control": False,
            "monomials": [
                monomial("1", v("one")),
                monomial("x_mod_11", v("x_mod_11")),
                monomial("y_mod_5", v("y_mod_5")),
                monomial("q", v("q")),
                monomial("rhs", v("rhs")),
                monomial("x_mod_11_q", mul("x_mod_11", "q")),
                monomial("y_mod_5_q", mul("y_mod_5", "q")),
            ],
            "name": "small_residue_source",
            "promotable": True,
        },
    ]


def matrix_for_template(
    spec: dict[str, Any],
    rows: list[dict[str, Any]],
    public_xy_override: dict[str, tuple[int, int]] | None = None,
    qrhs_override: dict[str, tuple[int, int]] | None = None,
) -> list[list[int]]:
    matrix = []
    for row in rows:
        features = point_features(row, public_xy_override, qrhs_override)
        matrix.append([fn(features) % ORDER for _name, fn in spec["monomials"]])
    return matrix


def rank_mod(matrix: list[list[int]]) -> int:
    if not matrix:
        return 0
    work = [[value % ORDER for value in row] for row in matrix]
    height = len(work)
    width = len(work[0]) if work else 0
    rank = 0
    for col in range(width):
        pivot = None
        for row in range(rank, height):
            if work[row][col] % ORDER:
                pivot = row
                break
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        inv = pow(work[rank][col] % ORDER, -1, ORDER)
        work[rank] = [(value * inv) % ORDER for value in work[rank]]
        for row in range(height):
            if row == rank:
                continue
            factor = work[row][col] % ORDER
            if factor:
                work[row] = [(left - factor * right) % ORDER for left, right in zip(work[row], work[rank])]
        rank += 1
        if rank == height:
            break
    return rank


def rref_with_pivots(matrix: list[list[int]]) -> tuple[list[list[int]], list[int]]:
    if not matrix:
        return [], []
    work = [[value % ORDER for value in row] for row in matrix]
    height = len(work)
    width = len(work[0])
    pivots: list[int] = []
    rank = 0
    for col in range(width):
        pivot = None
        for row in range(rank, height):
            if work[row][col] % ORDER:
                pivot = row
                break
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        inv = pow(work[rank][col] % ORDER, -1, ORDER)
        work[rank] = [(value * inv) % ORDER for value in work[rank]]
        for row in range(height):
            if row == rank:
                continue
            factor = work[row][col] % ORDER
            if factor:
                work[row] = [(left - factor * right) % ORDER for left, right in zip(work[row], work[rank])]
        pivots.append(col)
        rank += 1
        if rank == height:
            break
    return work, pivots


def nullspace_basis(matrix: list[list[int]], width: int) -> list[list[int]]:
    if width == 0:
        return []
    if not matrix:
        return [[1 if idx == free else 0 for idx in range(width)] for free in range(width)]
    rref, pivots = rref_with_pivots(matrix)
    pivot_set = set(pivots)
    free_cols = [col for col in range(width) if col not in pivot_set]
    basis = []
    for free in free_cols:
        vector = [0] * width
        vector[free] = 1
        for pivot_row, pivot_col in enumerate(pivots):
            vector[pivot_col] = (-rref[pivot_row][free]) % ORDER
        basis.append(vector)
    return basis


def support_size(vector: list[int]) -> int:
    return sum(1 for value in vector if value % ORDER)


def compact_identity_vector(spec: dict[str, Any], basis: list[list[int]]) -> dict[str, Any] | None:
    if not basis:
        return None
    chosen = min(basis, key=lambda vector: (support_size(vector), vector))
    return {
        "coefficients": [
            {"coeff": int(coeff % ORDER), "monomial": name}
            for (name, _fn), coeff in zip(spec["monomials"], chosen)
            if coeff % ORDER
        ],
        "support_size": support_size(chosen),
    }


def summarize_template(
    spec: dict[str, Any],
    train_rows: list[dict[str, Any]],
    validation_rows: list[dict[str, Any]],
    compressed_false_count: int,
    public_xy_override: dict[str, tuple[int, int]] | None = None,
    qrhs_override: dict[str, tuple[int, int]] | None = None,
) -> dict[str, Any]:
    train_matrix = matrix_for_template(spec, train_rows, public_xy_override, qrhs_override)
    validation_matrix = matrix_for_template(spec, validation_rows, public_xy_override, qrhs_override)
    combined_matrix = train_matrix + validation_matrix
    monomial_count = len(spec["monomials"])
    train_rank = rank_mod(train_matrix)
    combined_rank = rank_mod(combined_matrix)
    validation_rank = rank_mod(validation_matrix)
    train_nullity = monomial_count - train_rank
    combined_nullity = monomial_count - combined_rank
    overdetermined_train = len(train_rows) > monomial_count
    overdetermined_combined = len(combined_matrix) > monomial_count
    candidate = bool(
        spec["promotable"]
        and overdetermined_train
        and overdetermined_combined
        and validation_rows
        and train_nullity > 0
        and combined_nullity > 0
        and compressed_false_count == 0
    )
    diagnostic_success = bool(
        spec["diagnostic_control"]
        and overdetermined_train
        and train_nullity > 0
        and combined_nullity > 0
        and compressed_false_count == 0
    )
    return {
        "candidate_success_predicate": candidate,
        "combined_nullity": combined_nullity,
        "combined_rank": combined_rank,
        "description": spec["description"],
        "diagnostic_control": bool(spec["diagnostic_control"]),
        "diagnostic_success_predicate": diagnostic_success,
        "identity_hint": compact_identity_vector(spec, nullspace_basis(combined_matrix, monomial_count)),
        "monomial_count": monomial_count,
        "monomials": [name for name, _fn in spec["monomials"]],
        "name": spec["name"],
        "overdetermined_combined": overdetermined_combined,
        "overdetermined_train": overdetermined_train,
        "promotable": bool(spec["promotable"]),
        "train_nullity": train_nullity,
        "train_rank": train_rank,
        "train_rows": len(train_rows),
        "validation_rank": validation_rank,
        "validation_rows": len(validation_rows),
    }


def observed_public_xy(rows: list[dict[str, Any]]) -> tuple[list[str], list[tuple[int, int]]]:
    publics = sorted({p1045.public_key_value(row["form"]) for row in rows})
    pairs = []
    for public in publics:
        row = next(item for item in rows if p1045.public_key_value(item["form"]) == public)
        pairs.append(public_xy_for_row(row))
    return publics, pairs


def observed_qrhs(rows: list[dict[str, Any]]) -> tuple[list[str], list[tuple[int, int]]]:
    identities = [row["identity"] for row in rows]
    return identities, [qrhs_for_row(row) for row in rows]


def control_maps(
    rows: list[dict[str, Any]],
    template_name: str,
    index: int,
) -> dict[str, tuple[dict[str, tuple[int, int]] | None, dict[str, tuple[int, int]] | None]]:
    publics, public_pairs = observed_public_xy(rows)
    identities, qrhs_pairs = observed_qrhs(rows)
    rng = random.Random(stable_seed(f"{SCHEMA}:{template_name}:controls:{index}"))

    shuffled_public = list(public_pairs)
    rng.shuffle(shuffled_public)

    xs = [item[0] for item in public_pairs]
    ys = [item[1] for item in public_pairs]
    matched_public = [(rng.choice(xs), rng.choice(ys)) for _ in publics]
    full_public = [(rng.randrange(1, ORDER), rng.randrange(1, ORDER)) for _ in publics]

    shuffled_qrhs = list(qrhs_pairs)
    rng.shuffle(shuffled_qrhs)
    full_qrhs = [(rng.randrange(1, ORDER), rng.randrange(1, ORDER)) for _ in identities]

    return {
        "full_random_public": (dict(zip(publics, full_public)), None),
        "full_random_qrhs": (None, dict(zip(identities, full_qrhs))),
        "matched_random_public": (dict(zip(publics, matched_public)), None),
        "shuffled_public": (dict(zip(publics, shuffled_public)), None),
        "shuffled_qrhs": (None, dict(zip(identities, shuffled_qrhs))),
    }


def control_analysis(
    spec: dict[str, Any],
    train_rows: list[dict[str, Any]],
    validation_rows: list[dict[str, Any]],
    compressed_false_count: int,
    observed: dict[str, Any],
    trials: int,
) -> dict[str, Any]:
    all_rows = train_rows + validation_rows
    results: dict[str, list[dict[str, Any]]] = {
        "full_random_public": [],
        "full_random_qrhs": [],
        "matched_random_public": [],
        "shuffled_public": [],
        "shuffled_qrhs": [],
    }
    for index in range(trials):
        for name, (public_map, qrhs_map) in control_maps(all_rows, spec["name"], index).items():
            results[name].append(
                summarize_template(
                    spec,
                    train_rows,
                    validation_rows,
                    compressed_false_count,
                    public_map,
                    qrhs_map,
                )
            )

    observed_nullity = int(observed["combined_nullity"])

    def summarize(items: list[dict[str, Any]]) -> dict[str, Any]:
        candidate_like = [item for item in items if item["candidate_success_predicate"]]
        nullity_ge = [
            item
            for item in candidate_like
            if int(item["combined_nullity"]) >= observed_nullity
        ]
        return {
            "candidate_like_count": len(candidate_like),
            "combined_nullity_ge_observed_count": len(nullity_ge),
            "combined_nullity_histogram": serializable_counter(Counter(item["combined_nullity"] for item in items)),
            "trial_count": trials,
        }

    return {name: summarize(items) for name, items in results.items()}


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    input_paths = [Path(item) for item in args.inputs.split(",") if item.strip()]
    strict_records, strict_form_rows, strict_meta = p1045.load_artifact_records(input_paths)
    broad_records, broad_meta = p1047.rematerialize_broad_pairs(args)
    factor_count = max(p1045.int_value(strict_meta["factor_count"]), p1045.int_value(broad_meta["factor_count"]))
    train_rows = p1047.rows_from_form_items(strict_form_rows, factor_count, "p1045_strict_train")
    train_ids = {row["identity"] for row in train_rows}
    broad_rows_all = p1047.rows_from_prediction_pairs(broad_records, factor_count, "p1051_broad_validation")
    validation_rows = [row for row in broad_rows_all if row["identity"] not in train_ids]
    p1047.assign_ordinals(train_rows + validation_rows)

    compressed_false_count = sum(1 for record in broad_records if not record["toy_secret_verified"])
    compressed_true_count = sum(1 for record in broad_records if record["toy_secret_verified"])
    compressed_prediction_count = len(broad_records)

    model_results = []
    for spec in template_specs():
        observed = summarize_template(spec, train_rows, validation_rows, compressed_false_count)
        controls = control_analysis(spec, train_rows, validation_rows, compressed_false_count, observed, args.trials)
        strict_pass = bool(
            observed["candidate_success_predicate"]
            and all(control["combined_nullity_ge_observed_count"] == 0 for control in controls.values())
        )
        model_results.append(
            {
                "control_analysis": controls,
                "model": observed,
                "strict_validation_pass": strict_pass,
            }
        )
    model_results.sort(
        key=lambda item: (
            not item["strict_validation_pass"],
            not item["model"]["candidate_success_predicate"],
            item["control_analysis"]["matched_random_public"]["combined_nullity_ge_observed_count"],
            item["control_analysis"]["shuffled_qrhs"]["combined_nullity_ge_observed_count"],
            -item["model"]["combined_nullity"],
            item["model"]["name"],
        )
    )

    p1050_payload = json.loads(Path(args.p1050_input).read_text(encoding="utf-8")) if Path(args.p1050_input).exists() else {}
    promotable_results = [item for item in model_results if item["model"]["promotable"]]
    public_candidates = [item for item in promotable_results if item["model"]["candidate_success_predicate"]]
    strict_passes = [item for item in promotable_results if item["strict_validation_pass"]]
    diagnostic_results = [item for item in model_results if item["model"]["diagnostic_control"]]
    sanity = next(
        (item for item in diagnostic_results if item["model"]["name"] == "residual_constant_sanity"),
        None,
    )
    matched_reproduced = [
        item
        for item in public_candidates
        if item["control_analysis"]["matched_random_public"]["combined_nullity_ge_observed_count"] > 0
    ]
    full_public_reproduced = [
        item
        for item in public_candidates
        if item["control_analysis"]["full_random_public"]["combined_nullity_ge_observed_count"] > 0
    ]
    shuffled_public_reproduced = [
        item
        for item in public_candidates
        if item["control_analysis"]["shuffled_public"]["combined_nullity_ge_observed_count"] > 0
    ]
    shuffled_qrhs_reproduced = [
        item
        for item in public_candidates
        if item["control_analysis"]["shuffled_qrhs"]["combined_nullity_ge_observed_count"] > 0
    ]
    full_qrhs_reproduced = [
        item
        for item in public_candidates
        if item["control_analysis"]["full_random_qrhs"]["combined_nullity_ge_observed_count"] > 0
    ]

    sanity_ok = bool(sanity and sanity["model"]["diagnostic_success_predicate"])
    if not sanity_ok:
        claim = "P1051_SANITY_CONTROL_FAILED"
        taxonomy = "OPEN"
    elif strict_passes:
        claim = "P1051_LOW_DEGREE_INVARIANT_SIGNAL"
        taxonomy = "OBSERVATION"
    elif public_candidates and len(matched_reproduced) == len(public_candidates):
        claim = "NEGATIVE_RESULT_P1051_IDENTITIES_MATCH_MATCHED_RANDOM_PUBLIC_NULL"
        taxonomy = "NEGATIVE RESULT"
    elif public_candidates and len(shuffled_qrhs_reproduced) == len(public_candidates):
        claim = "NEGATIVE_RESULT_P1051_IDENTITIES_MATCH_SHUFFLED_QRHS_NULL"
        taxonomy = "NEGATIVE RESULT"
    elif public_candidates:
        claim = "NEGATIVE_RESULT_P1051_IDENTITIES_NOT_STRICTLY_VALIDATED"
        taxonomy = "NEGATIVE RESULT"
    else:
        claim = "NEGATIVE_RESULT_P1051_NO_OVERDETERMINED_PUBLIC_IDENTITIES"
        taxonomy = "NEGATIVE RESULT"

    windows = broad_meta["windows"]
    source_hashes = {
        window: p1005.sha256_file(p1047.p1044.p1007.expanded_source_path(window))
        for window in windows
        if p1047.p1044.p1007.expanded_source_path(window).exists()
    }
    return {
        "artifacts": {
            "contract": str(args.contract),
            "inputs": [str(path) for path in input_paths],
            "p1050_input": str(args.p1050_input),
            "script": str(Path(__file__)),
        },
        "artifact_hashes": {
            "contract_sha256": p1005.sha256_file(Path(args.contract)),
            "input_sha256": {str(path): p1005.sha256_file(path) for path in input_paths},
            "p1050_input_sha256": p1005.sha256_file(Path(args.p1050_input)) if Path(args.p1050_input).exists() else None,
            "script_sha256": p1005.sha256_file(Path(__file__)),
            "source_sha256": source_hashes,
        },
        "claim_status": claim,
        "claim_taxonomy": taxonomy,
        "diagnostic_controls": diagnostic_results,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime p231 ECDLP harness only.",
            "LOW-DEGREE-CATALOG: this tests a small monomial template catalog, not all possible invariants.",
            "NO-SECRET-PROMOTION: residual-derived sanity identities are excluded from promotion.",
            "OVERDETERMINED: train and combined row counts must exceed monomial count for promotable identities.",
            "NULL-CONTROLS: matched public-coordinate and row-coefficient controls are promotion blockers.",
            "INDEX-CALCULUS PRECURSOR: a pass would still require relation collection, sparse linear algebra, and target descent.",
            "RHO BOUNDARY: Pollard rho remains the one-target scalar-search baseline.",
        ],
        "model_results": model_results,
        "parameters": {
            "base_residual": p1045.BASE_RESIDUAL,
            "base_signature": [list(item) for item in p1045.BASE_SIGNATURE],
            "factor_count": factor_count,
            "max_windows": args.max_windows,
            "min_source_rank": args.min_source_rank,
            "modulus": ORDER,
            "start_window": args.start_window,
            "targets": [target.strip() for target in args.targets.split(",") if target.strip()],
            "trials": args.trials,
            "windows": windows,
        },
        "p1050_claim_status": p1050_payload.get("claim_status"),
        "rematerialized_broad_summary": {
            "all_base_rows": len(broad_rows_all),
            "broad_only_validation_rows": len(validation_rows),
            "compressed_false_count": compressed_false_count,
            "compressed_prediction_count": compressed_prediction_count,
            "compressed_true_count": compressed_true_count,
            "forward_exists_count": sum(1 for value in broad_meta["forward_exists"].values() if value),
            "pool_summaries": broad_meta["pool_summaries"],
            "unique_broad_public_count": len({p1045.public_key_value(row["form"]) for row in broad_rows_all}),
            "unique_validation_public_count": len({p1045.public_key_value(row["form"]) for row in validation_rows}),
        },
        "schema": SCHEMA,
        "strict_train_summary": {
            "input_paths": [str(path) for path in input_paths],
            "strict_pair_count": len(strict_records),
            "train_rows": len(train_rows),
            "unique_train_public_count": len({p1045.public_key_value(row["form"]) for row in train_rows}),
        },
        "summary": {
            "claim_status": claim,
            "compressed_false_count": compressed_false_count,
            "compressed_prediction_count": compressed_prediction_count,
            "compressed_true_count": compressed_true_count,
            "diagnostic_control_count": len(diagnostic_results),
            "full_public_reproduced_candidate_count": len(full_public_reproduced),
            "full_qrhs_reproduced_candidate_count": len(full_qrhs_reproduced),
            "matched_public_reproduced_candidate_count": len(matched_reproduced),
            "promotable_candidate_count": len(public_candidates),
            "promotable_template_count": len(promotable_results),
            "sanity_control_ok": sanity_ok,
            "shuffled_public_reproduced_candidate_count": len(shuffled_public_reproduced),
            "shuffled_qrhs_reproduced_candidate_count": len(shuffled_qrhs_reproduced),
            "strict_validation_pass_count": len(strict_passes),
            "strict_validation_pass_models": [item["model"]["name"] for item in strict_passes],
            "tested_model_count": len(model_results),
            "train_rows": len(train_rows),
            "validation_rows": len(validation_rows),
        },
        "timestamp": now_iso(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT), help="Experiment contract path")
    parser.add_argument(
        "--inputs",
        default=",".join(str(path) for path in DEFAULT_INPUTS),
        help="Comma-separated persisted strict witness probe paths for train rows",
    )
    parser.add_argument("--max-windows", type=int, default=DEFAULT_MAX_WINDOWS, help="Rematerialization window count")
    parser.add_argument("--min-source-rank", type=int, default=0, help="Minimum source rank for expanded row loading")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output JSON path")
    parser.add_argument("--p1050-input", default=str(DEFAULT_P1050_INPUT), help="P1050 nonlinear two-feature probe path")
    parser.add_argument("--start-window", default=DEFAULT_START, help="First forward window to rematerialize")
    parser.add_argument("--targets", default=p1047.p1044.p1022.DEFAULT_TARGET, help="Comma-separated target filter")
    parser.add_argument("--trials", type=int, default=DEFAULT_TRIALS, help="Controls per model")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    summary = payload["summary"]
    print(
        "claim={claim} train_rows={train} validation_rows={validation} compressed_pred={pred} compressed_false={false} promotable_candidates={candidates} matched_public={matched} shuffled_qrhs={shuffled_qrhs} strict_pass={passes} sanity={sanity} out={out}".format(
            claim=payload["claim_status"],
            train=summary["train_rows"],
            validation=summary["validation_rows"],
            pred=summary["compressed_prediction_count"],
            false=summary["compressed_false_count"],
            candidates=summary["promotable_candidate_count"],
            matched=summary["matched_public_reproduced_candidate_count"],
            shuffled_qrhs=summary["shuffled_qrhs_reproduced_candidate_count"],
            passes=summary["strict_validation_pass_count"],
            sanity=summary["sanity_control_ok"],
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
