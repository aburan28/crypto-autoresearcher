#!/usr/bin/env python3
"""Resolve the IDEA-056 shared-module review gate from frozen evidence."""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
STATE = ROOT / "ecdlp_index_calculus_state"
RESEARCH = ROOT / "research"
CONTRACT = STATE / "experiment_contract_p1502_block_krylov_shared_module_review.md"
P1478 = STATE / "p1478_sparse_s3_subgroup_norm_composition.json"
P1478_AUDIT = STATE / "p1478_sparse_s3_subgroup_norm_composition_audit.json"
P1490 = STATE / "p1490_rational_lift_selector_norm.json"
P1490_AUDIT = STATE / "p1490_rational_lift_selector_norm_audit.json"
P1491 = STATE / "p1491_pointwise_selector_subresultant.json"
P1491_AUDIT = STATE / "p1491_pointwise_selector_subresultant_audit.json"
P1493 = STATE / "p1493_pair_support_resultant_reporter.json"
P1493_AUDIT = STATE / "p1493_pair_support_resultant_reporter_audit.json"
IDEA = Path(
    "/Volumes/Volume/crypto-autoresearcher/ideas/"
    "ECDLP-IDEA-056_block_krylov_transition_intersection_extractor_hypothesis.md"
)
IDEA_CONTRACT = Path(
    "/Volumes/Volume/crypto-autoresearcher/ideas/contracts/"
    "ECDLP-EXP-CONTRACT-056_transition_intersection_preflight.yaml"
)
DERIVATION = Path(
    "/Volumes/Volume/crypto-autoresearcher/ideas/artifacts/"
    "ECDLP-IDEA-056/shared_module_identity.md"
)
FOCUS_QUEUE = Path(
    "/Volumes/Volume/crypto-autoresearcher/focus/archive/focus_queue_idea056_active.json"
)
FOCUS_PLAN = Path(
    "/Volumes/Volume/crypto-autoresearcher/focus/archive/focus_plan_idea056_active.json"
)
OUT = STATE / "p1502_block_krylov_shared_module_review.json"
NOTE = RESEARCH / "p1502_block_krylov_shared_module_review.md"

SCHEMA = "ecdlp.p1502_block_krylov_shared_module_review.v1"
EXPECTED = {
    CONTRACT: "02c804a77408ba295dac59e3440af275c17375c4ef876d8102d633f31874471e",
    P1478: "287a08a131ce7b56bd4e8468eb6c443d7bcba4b7fb2ba13c860866c21902b8df",
    P1478_AUDIT: "d035cba39d08165c4b7dd336d4a095c1c99ff822f8db8c6cf5f3fca3b8c764f9",
    P1490: "1fbb457f642dab18cab43c69bf694f9a41b68c6ecefa365d7432e1ac7107cbab",
    P1490_AUDIT: "da5b6d4b194d9c03a29622ac03fe3e8c6dae33f1e99c788c46b82fb38f85fa7a",
    P1491: "26fc025c2de2c8ce331bacc8e556d47557159eea755fbc4e86d87da2d1d483be",
    P1491_AUDIT: "31b1c95e09addd661e693d88fbdce2e1589fec47c7752e20b69f0bd7e0db6bc4",
    P1493: "cdfe2470ec5a9f231688b1d61d4bba5fb11dcb587982f892b21eee36b0e5ecf7",
    P1493_AUDIT: "ab75dff4153657b55a12fd371fe56e0b029f984319d1a185c5a118274a179e49",
    IDEA: "ee3f30d9d19a07774ed0ffd66b51186db4f3f46f24286bbce48f7292345f2394",
    IDEA_CONTRACT: "be8658b6df67763722dcabc91e3289edfb9a3c4bb3bf5ef895c3c2f1f7304c03",
    DERIVATION: "d56eace0426df249cd58e2cdde86aec3862c2648a950af672fce86f62ee7ea29",
    FOCUS_QUEUE: "5bf3feabac82da1e247ff0e8767154ba442d8245fcab0e2c1107b18468b9108b",
    FOCUS_PLAN: "d12cee157e41f7f3a4d55e46d87f534bfbce1c357131176b9fff545e1d3d27f1",
}


def compact(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def write_atomic(path: Path, data: bytes) -> None:
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    temporary.write_bytes(data)
    os.replace(temporary, path)


def all_checks(payload: dict[str, Any]) -> bool:
    checks = payload.get("checks", {})
    return bool(checks) and all(checks.values())


def render_note(payload: dict[str, Any]) -> str:
    lines = [
        "# P1502 Block-Krylov Shared-Module Review",
        "",
        f"Status: `{payload['status']}`",
        "",
        "| L | r | module dim | min block-state traffic | symbolic degree | A3 sources |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for record in payload["fixture_records"]:
        lines.append(
            f"| {record['L']} | {record['selector_degree_r']} | {record['module_dimension']} | "
            f"{record['minimum_block_krylov_state_traffic']} | {record['symbolic_squarefree_degree']} | "
            f"{record['triple_source_count']} |"
        )
    lines.extend([
        "",
        "## Decision",
        "",
        payload["interpretation"],
        "",
        "The exact fixed-query kernel/source identity is retained as a positive control. "
        "The review rejection is about mechanism novelty and complete cost, not correctness.",
        "",
        "## Next Action",
        "",
        payload["next_action"],
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    hashes = {display_path(path): sha256_file(path) for path in EXPECTED}
    hash_gates = {
        display_path(path): hashes[display_path(path)] == expected
        for path, expected in EXPECTED.items()
    }
    if not all(hash_gates.values()):
        raise RuntimeError(f"P1502 frozen hash mismatch: {hash_gates}")

    p1478 = json.loads(P1478.read_text(encoding="ascii"))
    p1478_audit = json.loads(P1478_AUDIT.read_text(encoding="ascii"))
    p1490 = json.loads(P1490.read_text(encoding="ascii"))
    p1490_audit = json.loads(P1490_AUDIT.read_text(encoding="ascii"))
    p1491 = json.loads(P1491.read_text(encoding="ascii"))
    p1491_audit = json.loads(P1491_AUDIT.read_text(encoding="ascii"))
    p1493 = json.loads(P1493.read_text(encoding="ascii"))
    p1493_audit = json.loads(P1493_AUDIT.read_text(encoding="ascii"))
    focus = json.loads(FOCUS_PLAN.read_text(encoding="ascii"))

    active = [item["id"] for item in focus["critical_experiments"]]
    structures = {cell["L"]: cell for cell in p1491["structure_cells"]}
    candidates = {cell["L"]: cell for cell in p1491["candidate_generation_cells"]}
    compositions: dict[int, dict[str, Any]] = {}
    for cell in p1490["composition_cells"]:
        compositions.setdefault(cell["L"], cell)

    fixture_records = []
    for L in sorted(structures):
        structure = structures[L]
        candidate = candidates[L]
        composition = compositions[L]
        r = int(structure["selector_degree_r"])
        module_dimension = 2 * r
        block_records = []
        for block in sorted({1, 2, 4, 8, module_dimension}):
            effective = min(block, module_dimension)
            iterations = math.ceil(module_dimension / effective)
            state_fields = module_dimension * effective
            block_records.append({
                "block_size": effective,
                "minimum_iterations_for_generic_degree": iterations,
                "state_field_elements_per_iteration": state_fields,
                "total_state_field_elements": iterations * state_fields,
            })
        fixture_records.append({
            "L": L,
            "selector_degree_r": r,
            "one_transition_degree": int(composition["one_transition_degree"]),
            "module_dimension": module_dimension,
            "module_dimension_matches_norm_degree": (
                structure["bidegree"] == [module_dimension, module_dimension]
                and composition["one_transition_degree"] == module_dimension
            ),
            "block_records": block_records,
            "minimum_block_krylov_state_traffic": min(
                record["total_state_field_elements"] for record in block_records
            ),
            "quadratic_state_traffic_floor": module_dimension**2,
            "direct_gcd_asymptotic": "soft-O(r)",
            "fixed_query_zero_and_source_exact": all(
                cell["zero_decision_mismatch_count"] == 0
                and cell["all_requested_sources_open"]
                for cell in p1491["pointwise_cells"]
                if cell["L"] == L
            ),
            "symbolic_raw_degree": int(composition["raw_resultant"]["degree"]),
            "symbolic_squarefree_degree": int(composition["squarefree_resultant"]["degree"]),
            "symbolic_nonreturn_degree": int(composition["nonreturn_resultant"]["degree"]),
            "symbolic_coefficients_dense": (
                composition["raw_resultant"]["coefficient_density"] == 1.0
                and composition["nonreturn_resultant"]["coefficient_density"] == 1.0
            ),
            "triple_source_count": int(candidate["triple_source_count"]),
            "exact_campaign_q_exponent": float(
                candidate["exact_support_strategy"]["complete_q_exponent"]
            ),
            "pollard_rho_q_exponent": float(
                candidate["exact_support_strategy"]["pollard_rho_q_exponent"]
            ),
        })

    predecessor_checks = {
        "p1478": all_checks(p1478_audit),
        "p1490": all_checks(p1490_audit),
        "p1491": all_checks(p1491_audit),
        "p1493": all_checks(p1493_audit),
    }
    gates = {
        "frozen_hashes_exact": all(hash_gates.values()),
        "idea056_is_sole_active_focus": active == ["ECDLP-IDEA-056"],
        "predecessor_audits_pass": all(predecessor_checks.values()),
        "one_transition_primitive_exact": p1478["gates"]["one_transition_all_exact"],
        "quotient_module_fully_defined": True,
        "common_state_iff_identity_exact": True,
        "source_lift_already_exact_in_p1491": p1491["gates"]["pointwise_zero_and_source_operator_exact"],
        "all_module_dimensions_equal_2r": all(
            record["module_dimension_matches_norm_degree"] for record in fixture_records
        ),
        "all_symbolic_degrees_equal_2r2_plus_1": all(
            record["symbolic_squarefree_degree"]
            == 2 * record["selector_degree_r"] ** 2 + 1
            for record in fixture_records
        ),
        "all_symbolic_nonreturn_polynomials_dense": all(
            record["symbolic_coefficients_dense"] for record in fixture_records
        ),
        "block_krylov_beats_direct_gcd": False,
        "mechanism_distinct_from_p1491": False,
        "complete_candidate_supply_below_r_to_three_halves": False,
        "complete_campaign_below_pollard_rho": False,
        "phase1_scaling_contract_approved": False,
        "generic_shoup_breakthrough": False,
    }
    required_true = [
        "frozen_hashes_exact",
        "idea056_is_sole_active_focus",
        "predecessor_audits_pass",
        "one_transition_primitive_exact",
        "quotient_module_fully_defined",
        "common_state_iff_identity_exact",
        "source_lift_already_exact_in_p1491",
        "all_module_dimensions_equal_2r",
        "all_symbolic_degrees_equal_2r2_plus_1",
        "all_symbolic_nonreturn_polynomials_dense",
    ]
    required_false = [
        "block_krylov_beats_direct_gcd",
        "mechanism_distinct_from_p1491",
        "complete_candidate_supply_below_r_to_three_halves",
        "complete_campaign_below_pollard_rho",
        "phase1_scaling_contract_approved",
        "generic_shoup_breakthrough",
    ]
    if not all(gates[name] for name in required_true) or any(
        gates[name] for name in required_false
    ):
        raise RuntimeError(f"P1502 review gate inconsistency: {gates}")

    payload = {
        "schema": SCHEMA,
        "status": "NEGATIVE_RESULT_P1502_IDEA056_DUPLICATE_FIXED_QUERY_AND_COST_NEGATIVE_BATCH",
        "claim_status": "EXACT SHARED-MODULE IDENTITY / FIXED-QUERY POSITIVE / MECHANISM-DISTINCTNESS AND COMPLETE-COST NEGATIVE / NO BREAKTHROUGH",
        "source": display_path(Path(__file__).resolve()),
        "source_sha256": sha256_file(Path(__file__).resolve()),
        "contract": display_path(CONTRACT),
        "contract_sha256": hashes[display_path(CONTRACT)],
        "frozen_hashes": hashes,
        "hash_gates": hash_gates,
        "focus_active_ids": active,
        "shared_module": {
            "module": "A_(u,r)=F_p[V]/(N_r(u,V))",
            "M1": "multiplication by V",
            "M2": "multiplication by N_r(V,w), equivalently N_r(M1,w)",
            "query_dependence": "M2 depends on supplied w",
            "biconditional": "ker(M2)!=0 iff gcd(N_r(u,V),N_r(V,w))!=1 iff resultant=0",
            "source_lift": "common factor, selector endpoint gcds, sign lifts, complete EC replay",
            "fixed_query_equivalent_to_p1491": True,
        },
        "fixture_records": fixture_records,
        "predecessor_checks": predecessor_checks,
        "cost_boundary": {
            "explicit_vector_matvec_io": "Omega(r) field elements",
            "generic_complete_block_krylov_state_traffic": "Omega(r^2) field elements for every block size",
            "direct_half_gcd": "soft-O(r) field operations with source polynomial",
            "symbolic_batch": "dense squarefree degree 2r^2+1",
            "exact_candidate_campaign": "Theta(r^3)=Theta(q^(3/5))",
            "rho": "Theta(q^(1/2))",
            "lower_bound_scope": "explicit-vector block-Krylov on the declared quotient module; not all conceivable structured algorithms",
        },
        "gates": gates,
        "interpretation": (
            "IDEA-056's missing shared module can be defined exactly, and its kernel/source biconditional is valid. That fixed-query object is precisely P1491's independently audited resultant/gcd, where direct half-GCD is soft-linear and dominates explicit block Krylov. Keeping the query symbolic recreates the dense degree-2r^2+1 composition, while fixed queries leave the complete Theta(q^(3/5)) candidate-supply floor unchanged. The review-required scaling contract is therefore rejected as duplicate and cost-negative under its declared mechanism."
        ),
        "limitations": [
            "The rejection is scoped to the rational-selector norm and the quotient module explicitly derivable from IDEA-056.",
            "It does not prove a lower bound for a genuinely different target-independent sparse module or compressed source-labelled batch representation.",
            "The fixed-query gcd and source lift remain reusable positives if a new factor-base geometry supplies subquadratic complete candidates.",
            "No rho or Shoup-bound improvement is claimed.",
        ],
        "next_action": (
            "Close IDEA-056 without running Phase 2. Promote the representation-changing IDEA-059 derivation gate: require a concrete elliptic-syzygy Cremona map, inverse, and saturated mixed-volume certificate before any multi-size toric campaign."
        ),
    }
    write_atomic(OUT, (compact(payload) + "\n").encode("ascii"))
    write_atomic(NOTE, render_note(payload).encode("ascii"))
    print(compact({
        "status": payload["status"],
        "fixtures": len(fixture_records),
        "phase1_approved": False,
        "out": str(OUT),
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
