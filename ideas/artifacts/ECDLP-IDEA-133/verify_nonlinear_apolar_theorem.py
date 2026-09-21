#!/usr/bin/env python3
"""Audit the immutable P1514 receipt's corrected scope without leaving this repo."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
from pathlib import Path
from typing import Any, Callable


HERE = Path(__file__).resolve().parent
REPOSITORY = HERE.parents[2]
THEOREM = HERE / "nonlinear_apolar_operation_theorem.md"
THEOREM_V2 = HERE / "nonlinear_apolar_operation_theorem_v2.md"
CORRECTION = HERE / "nonlinear_apolar_operation_theorem_audit_v2.md"
HYPOTHESIS = (
    REPOSITORY
    / "ideas/deferred/ECDLP-IDEA-133_target_local_nonlinear_apolar_flat_extension_hypothesis.md"
)
DEFAULT_OUTPUT = HERE / "nonlinear_apolar_operation_theorem_audit_v2.json"
EXPECTED_THEOREM_SHA256 = (
    "4093e48132d96706db1155c44a8ab0f82de5ae997885df56b6ba1074022f297e"
)
EXPECTED_THEOREM_V2_SHA256 = (
    "b97666d65119c90eb7c63ac9df3be650af1b1e42854f613d1b39dc1eb68c50b2"
)
SIZES = (4, 6, 8, 12, 16, 24, 32, 48, 64)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_inside_repository(path: Path) -> Path:
    resolved = path.resolve()
    if not resolved.is_relative_to(REPOSITORY):
        raise ValueError(f"path escapes repository boundary: {resolved}")
    return resolved


def write_atomic(path: Path, data: bytes) -> None:
    target = require_inside_repository(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(f".{target.name}.{os.getpid()}.tmp")
    temporary.write_bytes(data)
    os.replace(temporary, target)


def corrected_claims() -> dict[str, Any]:
    return {
        "mitm_materialized": {
            "precomputation_time_b_exponent": 3,
            "reusable_state_b_exponent": 3,
            "relation_campaign_time_b_exponent": 3,
        },
        "mitm_streamed": {
            "per_query_time_b_exponent": 3,
            "working_memory_b_exponent": 2,
            "relation_campaign_time_b_exponent": 4,
        },
        "direct_source_enumeration_precomputed": {
            "one_time_b_exponent": 5,
            "reusable_state_b_exponent": 5,
        },
        "direct_source_enumeration_rescanned": {
            "per_query_time_b_exponent": 5,
            "relation_campaign_time_b_exponent": 6,
        },
        "dense_macaulay": {
            "cutoff": "k=5B-3",
            "cutoff_status": "sufficient_theorem_guaranteed_not_compulsory_minimum",
            "frozen_instantiation_coordinate_exponent_b": 5,
        },
        "nonreduced_source_recovery": (
            "joint_primary_decomposition_and_nilpotent_local_algebra_required"
        ),
    }


def validate_claims(claims: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    expected = corrected_claims()
    for key, value in expected.items():
        if claims.get(key) != value:
            errors.append(key)
    return errors


def mutation_receipts() -> list[dict[str, Any]]:
    baseline = corrected_claims()
    mutations: list[tuple[str, Callable[[dict[str, Any]], None]]] = [
        (
            "reusable_mitm_charged_as_streamed_campaign",
            lambda data: data["mitm_materialized"].update(
                relation_campaign_time_b_exponent=4
            ),
        ),
        (
            "streamed_mitm_charged_as_reusable_campaign",
            lambda data: data["mitm_streamed"].update(
                relation_campaign_time_b_exponent=3
            ),
        ),
        (
            "streamed_mitm_uses_b3_memory",
            lambda data: data["mitm_streamed"].update(working_memory_b_exponent=3),
        ),
        (
            "direct_enumeration_is_always_b5_per_target",
            lambda data: data["direct_source_enumeration_rescanned"].update(
                relation_campaign_time_b_exponent=5
            ),
        ),
        (
            "sufficient_cutoff_is_compulsory_minimum",
            lambda data: data["dense_macaulay"].update(
                cutoff_status="compulsory_minimum"
            ),
        ),
        (
            "early_stabilization_is_closed",
            lambda data: data["dense_macaulay"].update(
                cutoff_status="universal_lower_bound"
            ),
        ),
        (
            "joint_eigenvalues_recover_nonreduced_multiplicity",
            lambda data: data.update(
                nonreduced_source_recovery="joint_eigenvalues_only"
            ),
        ),
    ]
    receipts: list[dict[str, Any]] = []
    for mutation_id, mutate in mutations:
        candidate = copy.deepcopy(baseline)
        mutate(candidate)
        errors = validate_claims(candidate)
        receipts.append(
            {"id": mutation_id, "rejected": bool(errors), "errors": errors}
        )
    return receipts


def cost_cells() -> list[dict[str, int | float]]:
    rows: list[dict[str, int | float]] = []
    for factor_base_size in SIZES:
        b = factor_base_size
        columns = math.comb(5 * b + 2, 5)
        rows.append(
            {
                "b": b,
                "n_proxy": b**5,
                "rho_proxy": b**2.5,
                "mitm_materialized_precomputation_time": b**3,
                "mitm_materialized_state": b**3,
                "mitm_materialized_relation_campaign_time": b**3,
                "mitm_streamed_working_memory": b**2,
                "mitm_per_query_time": b**3,
                "mitm_relation_campaign_time": b**4,
                "direct_precomputed_state": b**5,
                "direct_rescanned_campaign_time": b**6,
                "sufficient_macaulay_cutoff": 5 * b - 3,
                "frozen_sufficient_cutoff_columns": columns,
            }
        )
    return rows


def build_payload() -> dict[str, Any]:
    theorem = THEOREM.read_text(encoding="utf-8")
    theorem_v2 = THEOREM_V2.read_text(encoding="utf-8")
    correction = CORRECTION.read_text(encoding="utf-8")
    hypothesis = HYPOTHESIS.read_text(encoding="utf-8")
    theorem_ws = " ".join(theorem.split())
    theorem_v2_ws = " ".join(theorem_v2.split())
    correction_ws = " ".join(correction.split())
    mutations = mutation_receipts()
    checks = {
        "receipt_hash_exact": sha256(THEOREM) == EXPECTED_THEOREM_SHA256,
        "receipt_v2_hash_exact": sha256(THEOREM_V2) == EXPECTED_THEOREM_V2_SHA256,
        "receipt_preserved_overbroad_macaulay_wording": (
            "through at least degree" in theorem_ws
            and "coordinate count is therefore at least" in theorem_ws
        ),
        "receipt_preserved_mitm_conflation_for_audit": (
            "Materializing or scanning the larger deck costs" in theorem
        ),
        "receipt_v2_preserves_partial_correction": (
            "sufficient Macaulay degree" in theorem_v2_ws
            and "memory conclusion is now conditional on materialization" in theorem_v2_ws
        ),
        "correction_marks_sufficient_not_minimum": (
            "sufficient cutoff" in correction_ws
            and "does not make `5B-3` a compulsory minimum" in correction_ws
        ),
        "correction_separates_mitm_memory": (
            "streamed" in correction_ws and "Theta(B^2)" in correction_ws
        ),
        "correction_records_direct_reuse_tradeoff": (
            "Theta(B^6)" in correction_ws and "precomputed" in correction_ws
        ),
        "correction_separates_reusable_and_streamed_campaign_time": (
            "Theta(B^3)` total campaign time" in correction_ws
            and "Theta(B^4)=Theta(N^0.8)" in correction_ws
        ),
        "correction_requires_primary_nilpotent_data": (
            "joint primary decomposition" in correction_ws
            and "nilpotent local algebra" in correction_ws
        ),
        "hypothesis_keeps_adaptive_routes_open": (
            "Adaptive early stabilization" in hypothesis
            and "sparse or multihomogeneous" in hypothesis
        ),
        "hypothesis_keeps_idea_deferred": (
            "State: `deferred_" in hypothesis
        ),
        "all_scope_mutations_rejected": all(item["rejected"] for item in mutations),
    }
    status = (
        "SCOPE_CORRECTION_CONFIRMED_PRODUCER_RECEIPT_SUPERSEDED"
        if all(checks.values())
        else "SCOPE_CORRECTION_AUDIT_FAILED"
    )
    return {
        "schema": "crypto_autoresearcher.ecdlp.idea133.p1514_scope_audit.v2",
        "status": status,
        "claim_boundary": {
            "idea_state": "deferred",
            "experiment_run": False,
            "breakthrough_claim": False,
            "constant_density_and_output_rank": "heuristic_model_bound_controls",
            "closed_dense_route": (
                "frozen_theorem_guaranteed_instantiation_at_sufficient_cutoff_k_5B_minus_3"
            ),
            "open_routes": [
                "adaptive_early_stabilization",
                "smaller_fiber_specific_cutoff",
                "sparse_or_multihomogeneous_macaulay",
                "structured_target_local_moment_oracle",
            ],
        },
        "repository_relative_inputs": [
            str(THEOREM.relative_to(REPOSITORY)),
            str(THEOREM_V2.relative_to(REPOSITORY)),
            str(CORRECTION.relative_to(REPOSITORY)),
            str(HYPOTHESIS.relative_to(REPOSITORY)),
        ],
        "receipt_sha256": sha256(THEOREM),
        "receipt_v2_sha256": sha256(THEOREM_V2),
        "corrected_claims": corrected_claims(),
        "cost_cells": cost_cells(),
        "mutation_receipts": mutations,
        "checks": checks,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="write the V2 JSON receipt")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    encoded = json.dumps(payload, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    if args.write:
        write_atomic(args.output, encoded)
    print(encoded.decode("utf-8"), end="")
    return 0 if payload["status"].endswith("SUPERSEDED") else 1


if __name__ == "__main__":
    raise SystemExit(main())
