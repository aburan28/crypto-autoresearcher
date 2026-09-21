#!/usr/bin/env sage -python
"""Certify the low-dimensional quotient obstruction for the frozen simple Prym."""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
from typing import Any

from sage.all import NumberField, PolynomialRing, QQ, ZZ


ROOT = Path(__file__).resolve().parents[2]
STATE_DIR = ROOT / "ecdlp_index_calculus_state"
RESEARCH_DIR = ROOT / "research"
CONTRACT = STATE_DIR / "experiment_contract_p1498_simple_prym_quotient_obstruction.md"
PO58 = ROOT / "experiments/ecdlp_isogeny/po_transfer_058_cover_reconstruct.json"
PO58_AUDIT = ROOT / "experiments/ecdlp_isogeny/po_transfer_058_independent_verify.json"
PO59 = ROOT / "experiments/ecdlp_isogeny/po_transfer_059_deck_character_predicate.json"
P1497 = STATE_DIR / "p1497_exception_complete_quadratic_divisor.json"
P1497_AUDIT = STATE_DIR / "p1497_exception_complete_quadratic_divisor_audit.json"
OUT = STATE_DIR / "p1498_simple_prym_quotient_obstruction.json"
NOTE = RESEARCH_DIR / "p1498_simple_prym_quotient_obstruction.md"

SCHEMA = "ecdlp.p1498_simple_prym_quotient_obstruction.v1"
EXPECTED = {
    CONTRACT: "e9ac82d2d4f412056eb56ad3ea9d676ec24810456cf60b969619ea3d65c1a3ed",
    PO58: "34b0b0ebf7994d93c44a6d8ce8d95807ecf64e42cebdac62f63e43b16eec613c",
    PO58_AUDIT: "aca92f0a07ec9d5f7f2f5232087c248abff706f97907c97d05b45ef93d58ff14",
    PO59: "6a4973fc4420a0e5f82dc83b60353dc7b1977e694408c565b854298857200534",
    P1497: "3da79142512eadbd2ec968ae9bdad29d97b5c6030ecd6305d7cd99e4bdaf6ad3",
    P1497_AUDIT: "965a08b8cb6b933e3caccb3e11fa432dcd479d0344cd2ae820540f2b71b218cc",
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return digest(path.read_bytes())


def write_atomic(path: Path, data: bytes) -> None:
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    temporary.write_bytes(data)
    os.replace(temporary, path)


def nonrational_coefficients(polynomial: Any) -> bool:
    for coefficient in polynomial.list():
        coordinates = list(coefficient.list())
        if any(value for value in coordinates[1:]):
            return True
    return False


def render_note(payload: dict[str, Any]) -> str:
    primary = payload["primary_cell"]
    lines = [
        "# P1498 Simple-Prym Quotient Obstruction",
        "",
        f"Status: `{payload['status']}`",
        "",
        "## Exact Boundary",
        "",
        (
            "The frozen cover has `Jac(X) ~ E x P`, where `P` is a base-field-simple "
            "three-dimensional Prym. A nonzero homomorphism out of `P` therefore has "
            "finite kernel and three-dimensional image."
        ),
        "",
        "| quantity | value |",
        "|---|---:|",
        f"| cover genus | {primary['cover_genus']} |",
        f"| Prym dimension | {primary['prym_dimension']} |",
        f"| Prym order | {primary['prym_order']} |",
        f"| P1497 p271 graph records | {primary['candidate_count_M']} |",
        f"| uniform full-Prym collision expectation | {primary['actual_prym_expected_collision_pairs']:.8f} |",
        f"| candidate count / sqrt(E order) | {primary['candidate_over_rho_scale']:.4f} |",
        "",
        "The two degree-three `Q(omega)` character factors are conjugate halves of "
        "the six-dimensional Frobenius module, not separate base-field abelian "
        "quotients. Every base-field quotient of image dimension at most two kills "
        "the Prym and retains only the elliptic aggregate component already tested by PO73.",
        "",
        "## Scope",
        "",
        payload["scope"],
        "",
        "## Next Action",
        "",
        payload["next_action"],
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    hashes = {str(path.relative_to(ROOT)): sha256_file(path) for path in EXPECTED}
    hash_gates = {
        str(path.relative_to(ROOT)): hashes[str(path.relative_to(ROOT))] == expected
        for path, expected in EXPECTED.items()
    }
    if not all(hash_gates.values()):
        raise RuntimeError(f"P1498 frozen hash mismatch: {hash_gates}")
    po58 = json.loads(PO58.read_text(encoding="ascii"))
    po58_audit = json.loads(PO58_AUDIT.read_text(encoding="ascii"))
    po59 = json.loads(PO59.read_text(encoding="ascii"))
    p1497 = json.loads(P1497.read_text(encoding="ascii"))
    p1497_audit = json.loads(P1497_AUDIT.read_text(encoding="ascii"))
    if not all(po58["correctness_gates"].values()):
        raise RuntimeError("P1498 requires the exact PO58 cover certificate")
    if not all(po58_audit["gates"].values()):
        raise RuntimeError("P1498 requires the verified PO58 audit")
    if not p1497_audit.get("verified") or p1497_audit.get("passed_checks") != 12:
        raise RuntimeError("P1498 requires the verified P1497 negative")

    U_ring = PolynomialRing(ZZ, "U")
    U = U_ring.gen()
    prym_data = po58["jacobian_split"]
    chi = U_ring(prym_data["prym_frobenius_polynomial"])
    chi_q = PolynomialRing(QQ, "U")(chi)
    irreducible = bool(chi_q.is_irreducible())
    prym_dimension = int(chi.degree() // 2)
    prym_order = int(chi(1))

    T_ring = PolynomialRing(QQ, "t")
    omega_field = NumberField(T_ring.gen() ** 2 + T_ring.gen() + 1, "omega")
    omega = omega_field.gen()
    character_ring = PolynomialRing(omega_field, "U")
    chi_character = character_ring(chi)
    factors = [factor.monic() for factor, multiplicity in chi_character.factor() for _ in range(multiplicity)]
    character_degrees = sorted(int(factor.degree()) for factor in factors)
    conjugation = omega_field.hom([omega**2], omega_field)
    conjugate_first = character_ring([conjugation(value) for value in factors[0].list()]).monic()
    character_conjugate_pair = len(factors) == 2 and conjugate_first == factors[1]
    character_nonrational = all(nonrational_coefficients(factor) for factor in factors)

    cover_genus = int(po58["cover_object"]["riemann_hurwitz_genus"])
    elliptic_dimension = 1
    dimension_split_exact = cover_genus == elliptic_dimension + prym_dimension == 4
    norm_pullback_exact = (
        prym_data["statement"]
        == "pi^*: Jac(E)->Jac(C), Nm_pi: Jac(C)->Jac(E), Nm_pi o pi^*=[3]"
        and "3-torsion" in prym_data["isogeny"]
    )
    simple_kernel_table = [
        {
            "requested_image_dimension": dimension,
            "nonzero_prym_homomorphism_possible": dimension == prym_dimension,
            "reason": (
                "zero map only" if dimension < prym_dimension else "finite connected kernel and image isogenous to P"
            ),
        }
        for dimension in range(prym_dimension + 1)
    ]
    no_low_prym_quotient = irreducible and all(
        not row["nonzero_prym_homomorphism_possible"]
        for row in simple_kernel_table
        if row["requested_image_dimension"] in (1, 2)
    )
    low_jacobian_quotient_factors_through_e = no_low_prym_quotient and dimension_split_exact

    synthetic_elliptic_factors = [U**2 + trace * U + 271 for trace in (1, 2, 4)]
    synthetic_product = U_ring.one()
    for factor in synthetic_elliptic_factors:
        synthetic_product *= factor
    synthetic_factor_degrees = sorted(int(factor.degree()) for factor, _ in synthetic_product.factor())
    elliptic_ring = PolynomialRing(ZZ, "T")
    elliptic_polynomial = elliptic_ring(po58["frobenius"]["elliptic_l_polynomial"])
    synthetic_controls = {
        "reducible_degree_six_rejected_as_simple": bool(not PolynomialRing(QQ, "U")(synthetic_product).is_irreducible()),
        "three_elliptic_factors_expose_dimension_one_quotients": synthetic_factor_degrees == [2, 2, 2],
        "real_elliptic_factor_visible": bool(
            elliptic_polynomial.degree() == 2 and int(elliptic_polynomial[2]) == 271
        ),
    }

    p = int(po58["parameters"]["p"])
    order_e = int(po58["parameters"]["order"])
    p1497_271 = next(record for record in p1497["field_records"] if int(record["p"]) == p)
    candidate_count = int(p1497_271["graph_record_count"])
    collision_models = []
    for dimension in (1, 2, 3):
        label_space = p**dimension
        collision_models.append({
            "dimension": dimension,
            "label_space_model": int(label_space),
            "expected_pairs_for_actual_M": float(candidate_count * (candidate_count - 1) / (2 * label_space)),
            "theta_p_candidate_collision_exponent": int(2 - dimension),
        })
    actual_prym_expected = candidate_count * (candidate_count - 1) / (2 * prym_order)
    primary_cell = {
        "p": p,
        "elliptic_order": order_e,
        "cover_genus": cover_genus,
        "elliptic_dimension": elliptic_dimension,
        "prym_dimension": prym_dimension,
        "prym_order": prym_order,
        "prym_order_matches_frozen": prym_order == int(prym_data["prym_order"]),
        "candidate_count_M": candidate_count,
        "actual_prym_expected_collision_pairs": float(actual_prym_expected),
        "actual_prym_any_collision_union_bound": float(min(1.0, actual_prym_expected)),
        "candidate_over_rho_scale": float(candidate_count / math.sqrt(order_e)),
        "collision_models": collision_models,
    }
    arithmetic_exact = (
        irreducible
        and prym_dimension == 3
        and prym_order == int(prym_data["prym_order"])
        and dimension_split_exact
        and norm_pullback_exact
        and character_degrees == [3, 3]
        and character_conjugate_pair
        and character_nonrational
    )
    controls_exact = all(synthetic_controls.values())
    collision_hostile = (
        collision_models[-1]["theta_p_candidate_collision_exponent"] == -1
        and actual_prym_expected < 0.01
        and candidate_count > math.sqrt(order_e)
    )
    scoped_negative = (
        arithmetic_exact
        and controls_exact
        and no_low_prym_quotient
        and low_jacobian_quotient_factors_through_e
        and collision_hostile
    )
    status = (
        "NEGATIVE_RESULT_P1498_SIMPLE_PRYM_NO_LOW_DIMENSIONAL_QUOTIENT"
        if scoped_negative
        else "REVIEW_REQUIRED_P1498_PRYM_QUOTIENT_CERTIFICATE"
    )
    scope = (
        "This closes base-field homomorphic abelian quotients of the frozen PO58 Prym in dimensions one and two. It does not close nonhomomorphic character resultants, extension-field maps, a different cyclic cover, or an auxiliary variety whose Prym is not simple."
    )
    payload = {
        "schema": SCHEMA,
        "status": status,
        "claim_status": "RESTRICTED SIMPLE-PRYM THEOREM / APPLICABILITY NEGATIVE / NO GENERIC BREAKTHROUGH",
        "source": str(Path(__file__).resolve()),
        "source_sha256": sha256_file(Path(__file__).resolve()),
        "contract": str(CONTRACT),
        "contract_sha256": sha256_file(CONTRACT),
        "frozen_hashes": hashes,
        "hash_gates": hash_gates,
        "primary_cell": primary_cell,
        "prym_polynomial": {
            "polynomial": str(chi),
            "degree": int(chi.degree()),
            "irreducible_over_Q": irreducible,
            "order_at_one": prym_order,
            "character_factor_degrees_over_Q_omega": character_degrees,
            "character_factors": [str(factor) for factor in factors],
            "character_factors_are_conjugate": bool(character_conjugate_pair),
            "character_factors_have_nonrational_coefficients": bool(character_nonrational),
        },
        "theorem_certificate": {
            "jacobian_dimension_split_exact": bool(dimension_split_exact),
            "norm_pullback_three_exact": bool(norm_pullback_exact),
            "simple_kernel_image_table": simple_kernel_table,
            "no_nonzero_prym_image_dimension_one_or_two": bool(no_low_prym_quotient),
            "all_low_dimensional_jacobian_quotients_factor_through_E": bool(low_jacobian_quotient_factors_through_e),
            "elliptic_component_is_pushforward_aggregate": True,
        },
        "synthetic_controls": synthetic_controls,
        "po59_boundary": {
            "status": po59["status"],
            "passing_scalar_features": len(po59["passing_features"]),
            "full_prym_coordinates_were_not_tested": "full Prym divisor-class coordinates" in po59["limitations"][2],
            "interpretation": "PO59 scalar summaries are a separate post-candidate negative; P1498 closes only homomorphic low-dimensional quotients.",
        },
        "gates": {
            "all_hashes_match": all(hash_gates.values()),
            "frozen_arithmetic_exact": bool(arithmetic_exact),
            "synthetic_controls_exact": bool(controls_exact),
            "no_low_dimensional_prym_quotient": bool(no_low_prym_quotient),
            "low_dimensional_jacobian_quotient_is_aggregate_only": bool(low_jacobian_quotient_factors_through_e),
            "full_prym_label_collision_hostile": bool(collision_hostile),
            "generic_shoup_breakthrough": False,
            "beats_pollard_rho": False,
        },
        "scope": scope,
        "references": [
            "https://www.jmilne.org/math/CourseNotes/AV110.pdf",
            "https://arxiv.org/abs/2003.07774",
            "https://doi.org/10.1007/s10711-021-00671-6",
        ],
        "next_action": (
            "Do not implement full Prym coordinates or a base-field dimension-one/two homomorphic projector on this cover. P1499 should test a nonhomomorphic cross-anchor deck-character resultant with an exact cheap evaluator, same-pushforward nulls, and a hard stop if its coefficient state or collision label has dimension at least two."
        ),
    }
    write_atomic(OUT, (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    write_atomic(NOTE, render_note(payload).encode("utf-8"))
    print(json.dumps({
        "status": status,
        "gates": payload["gates"],
        "prym": payload["prym_polynomial"],
        "primary": primary_cell,
    }, indent=2, sort_keys=True))
    return 0 if scoped_negative else 1


if __name__ == "__main__":
    raise SystemExit(main())
