#!/usr/bin/env sage -python
"""Test ordinary algebraic transfers into trace-zero Frobenius directions."""

from __future__ import annotations

import hashlib
import json
import math
import os
import resource
import time
from pathlib import Path
from typing import Any

from sage.all import (
    EllipticCurve,
    GF,
    Matrix,
    PolynomialRing,
    identity_matrix,
    is_prime,
    vector,
)


ROOT = Path(__file__).resolve().parents[2]
STATE_DIR = ROOT / "ecdlp_index_calculus_state"
RESEARCH_DIR = ROOT / "research"
CONTRACT = STATE_DIR / "experiment_contract_p1501_ordinary_trace_zero_transfer_obstruction.md"
P1496 = STATE_DIR / "p1496_root_free_quadratic_divisor.json"
TRANSFER_SIEVE = ROOT / "experiments/ecdlp_isogeny/non_generic_transfer_sieve_result.json"
CANDIDATE_NOTE = ROOT / "research/candidate_algorithms.md"
IDEA009 = Path(
    "/Volumes/Volume/crypto-autoresearcher/ideas/"
    "ECDLP-IDEA-009_nonequivariant_trace_zero_transfer_hypothesis.md"
)
FOCUS_QUEUE = Path(
    "/Volumes/Volume/crypto-autoresearcher/focus/archive/"
    "focus_queue_p1501_active.json"
)
FOCUS_PLAN = Path(
    "/Volumes/Volume/crypto-autoresearcher/focus/archive/"
    "focus_plan_p1501_active.json"
)
OUT = STATE_DIR / "p1501_ordinary_trace_zero_transfer_obstruction.json"
NOTE = RESEARCH_DIR / "p1501_ordinary_trace_zero_transfer_obstruction.md"

SCHEMA = "ecdlp.p1501_ordinary_trace_zero_transfer_obstruction.v1"
BOUNDED_DEGREES = (2, 3, 4, 5, 7, 8, 11, 13, 16)
EXPECTED = {
    CONTRACT: "d85f75536ea5ebe5a3c181fc67390de8bd4347ce2f0f2abb1d532adc1acfb3df",
    P1496: "f568a711118263a53905d9f76d32f5bcfc6ce209fd7103583c7e80e0fa2917b5",
    TRANSFER_SIEVE: "60221622884d1e0c96830719da5f6ba1e642a1332d025d82484919ca7d459804",
    CANDIDATE_NOTE: "7d56c7dc205f6813910965f682c79396b8ed6df992dcd6127adbea3da7e1261a",
    IDEA009: "7fabf5c4fa94353908eb4e1dbf61dfab9b768ce28f8f391b25e69ff994f8e240",
    FOCUS_QUEUE: "8bf8fb2f52c49fad63d59faf6a4d1b364840f5b46795ab8389001bfe1440f5fe",
    FOCUS_PLAN: "a63d5dbef8e82447d8907bf82317021ffcdfd728bbc8aab9a53c68db2ff394e3",
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


def raw_matrix(matrix: Any) -> list[list[int]]:
    return [[int(value) for value in row] for row in matrix.rows()]


def raw_vector(value: Any) -> list[int]:
    return [int(item) for item in value]


def trace_operator(frobenius: Any, degree: int) -> Any:
    ring = frobenius.base_ring()
    total = Matrix(ring, 2, 2, 0)
    power = identity_matrix(ring, 2)
    for _ in range(degree):
        total += power
        power *= frobenius
    return total


def centralizer_operator(frobenius: Any) -> Any:
    ring = frobenius.base_ring()
    basis = []
    for row in range(2):
        for column in range(2):
            matrix = Matrix(ring, 2, 2, 0)
            matrix[row, column] = 1
            basis.append(matrix)
    columns = []
    for matrix in basis:
        commutator = matrix * frobenius - frobenius * matrix
        columns.append(vector(ring, commutator.list()))
    return Matrix(ring, columns).transpose()


def candidate_record(
    *,
    name: str,
    family: str,
    matrix: Any,
    frobenius: Any,
    rational_basis: Any,
    degree: int,
    order: int,
    evaluator: str,
    public_evaluator: bool,
    algebraic_correspondence: bool,
    hidden_scalar_reads: bool,
    construction_work_lower: int,
) -> dict[str, Any]:
    image = matrix * rational_basis
    trace = trace_operator(frobenius, degree)
    traced_image = trace * image
    nonzero = not image.is_zero()
    commutes = matrix * frobenius == frobenius * matrix
    below_rho = degree < math.sqrt(order) and construction_work_lower < math.sqrt(order)
    promotable = (
        nonzero
        and traced_image.is_zero()
        and public_evaluator
        and not hidden_scalar_reads
        and below_rho
        and (not algebraic_correspondence or commutes)
    )
    return {
        "name": name,
        "family": family,
        "matrix": raw_matrix(matrix),
        "extension_degree": int(degree),
        "trace_operator": raw_matrix(trace),
        "rational_line_image": raw_vector(image),
        "traced_image": raw_vector(traced_image),
        "scalar_compatible": True,
        "nonzero_on_rational_line": bool(nonzero),
        "injective_on_rational_prime_line": bool(nonzero),
        "trace_zero": bool(traced_image.is_zero()),
        "commutes_with_frobenius": bool(commutes),
        "evaluator": evaluator,
        "public_evaluator": bool(public_evaluator),
        "algebraic_correspondence": bool(algebraic_correspondence),
        "hidden_scalar_reads": bool(hidden_scalar_reads),
        "construction_work_lower_bound": int(construction_work_lower),
        "extension_degree_over_sqrt_order": float(degree / math.sqrt(order)),
        "extension_degree_exponent_log_order": float(math.log(degree) / math.log(order)),
        "below_rho_extension_and_construction_gate": bool(below_rho),
        "promotable": bool(promotable),
    }


def render_note(payload: dict[str, Any]) -> str:
    lines = [
        "# P1501 Ordinary Trace-Zero Transfer Obstruction",
        "",
        f"Status: `{payload['status']}`",
        "",
        "| p | N | ord_N(p) | ord/sqrt(N) | centralizer dim | promotable |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for record in payload["field_records"]:
        lines.append(
            "| {p} | {order} | {degree} | {ratio:.6f} | {dimension} | {promotable} |".format(
                p=record["p"],
                order=record["order"],
                degree=record["minimum_nonrational_trace_zero_degree"],
                ratio=record["minimum_nonrational_degree_over_rho"],
                dimension=record["centralizer"]["dimension"],
                promotable=str(record["any_promotable_candidate"]).lower(),
            )
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        payload["interpretation"],
        "",
        "The large-degree inclusion and oracle off-diagonal controls are valid "
        "trace-zero transfers but fail the charged applicability gates. They are "
        "not ECDLP algorithms.",
        "",
        "## Next Action",
        "",
        payload["next_action"],
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    started = time.time()
    hashes = {display_path(path): sha256_file(path) for path in EXPECTED}
    hash_gates = {
        display_path(path): hashes[display_path(path)] == expected
        for path, expected in EXPECTED.items()
    }
    if not all(hash_gates.values()):
        raise RuntimeError(f"P1501 frozen hash mismatch: {hash_gates}")
    p1496 = json.loads(P1496.read_text(encoding="ascii"))
    focus_plan = json.loads(FOCUS_PLAN.read_text(encoding="ascii"))
    active_focus = [
        record["id"]
        for record in focus_plan["critical_experiments"]
        if record["status"] == "active"
    ]
    if active_focus != ["P1501"]:
        raise RuntimeError(f"P1501 is not the sole active focus lane: {active_focus}")

    field_records = []
    any_promotable = False
    all_field_arithmetic = True
    all_module_arithmetic = True
    all_controls = True
    holdout_count = 0
    for prior in p1496["field_records"]:
        p = int(prior["p"])
        order = int(prior["order"])
        holdout = bool(prior["holdout"])
        holdout_count += int(holdout)
        field = GF(p)
        curve = EllipticCurve(
            field, [field(prior["curve"]["a"]), field(prior["curve"]["b"])]
        )
        generator = curve(tuple(prior["generator"]))
        curve_order = int(curve.cardinality())
        trace = p + 1 - curve_order
        module = GF(order)
        p_mod = module(p)
        frobenius = Matrix(module, [[1, 0], [0, p_mod]])
        rational_basis = vector(module, [1, 0])
        nonrational_basis = vector(module, [0, 1])
        polynomial_ring = PolynomialRing(module, f"p1501_X_{p}")
        X = polynomial_ring.gen()
        expected_characteristic = X**2 - module(trace) * X + module(p)
        factor_characteristic = (X - 1) * (X - p_mod)
        actual_characteristic = polynomial_ring(frobenius.charpoly())
        characteristic_exact = (
            actual_characteristic == expected_characteristic == factor_characteristic
        )
        field_exact = (
            curve_order == order
            and order in (283, 487, 797, 1021)
            and is_prime(order)
            and int(generator.order()) == order
            and trace % p != 0
            and p_mod != 1
            and characteristic_exact
        )

        centralizer = centralizer_operator(frobenius)
        centralizer_kernel = centralizer.right_kernel()
        centralizer_basis = sorted(
            (tuple(int(value) for value in item) for item in centralizer_kernel.basis())
        )
        centralizer_exact = (
            int(centralizer.rank()) == 2
            and int(centralizer_kernel.dimension()) == 2
            and all(item[1] == 0 and item[2] == 0 for item in centralizer_basis)
        )

        nonrational_degree = int(p_mod.multiplicative_order())
        nonrational_trace = trace_operator(frobenius, nonrational_degree)
        first_nonrational_zero = next(
            degree
            for degree in range(1, nonrational_degree + 1)
            if (trace_operator(frobenius, degree) * nonrational_basis).is_zero()
        )
        bounded_trace_exact = all(
            trace_operator(frobenius, degree) * rational_basis
            == module(degree) * rational_basis
            and not (trace_operator(frobenius, degree) * rational_basis).is_zero()
            for degree in BOUNDED_DEGREES
        )
        minimum_degree_exact = (
            first_nonrational_zero == nonrational_degree
            and (nonrational_trace * nonrational_basis).is_zero()
            and nonrational_degree > math.sqrt(order)
        )

        candidates = []
        for degree in BOUNDED_DEGREES:
            for scalar in (1, 2, 3, 5):
                candidates.append(candidate_record(
                    name=f"scalar_{scalar}_k{degree}",
                    family="scalar_inclusion",
                    matrix=module(scalar) * identity_matrix(module, 2),
                    frobenius=frobenius,
                    rational_basis=rational_basis,
                    degree=degree,
                    order=order,
                    evaluator="public_scalar_multiplication",
                    public_evaluator=True,
                    algebraic_correspondence=True,
                    hidden_scalar_reads=False,
                    construction_work_lower=1,
                ))
            for exponent in (1, 2, 3):
                candidates.append(candidate_record(
                    name=f"frobenius_power_{exponent}_k{degree}",
                    family="frobenius_power",
                    matrix=frobenius**exponent,
                    frobenius=frobenius,
                    rational_basis=rational_basis,
                    degree=degree,
                    order=order,
                    evaluator="public_frobenius",
                    public_evaluator=True,
                    algebraic_correspondence=True,
                    hidden_scalar_reads=False,
                    construction_work_lower=exponent,
                ))
            for left, right in ((1, 1), (1, -1), (2, 1), (1, 2)):
                candidates.append(candidate_record(
                    name=f"frobenius_polynomial_{left}_{right}_k{degree}",
                    family="frobenius_polynomial",
                    matrix=module(left) * identity_matrix(module, 2)
                    + module(right) * frobenius,
                    frobenius=frobenius,
                    rational_basis=rational_basis,
                    degree=degree,
                    order=order,
                    evaluator="public_frobenius_polynomial",
                    public_evaluator=True,
                    algebraic_correspondence=True,
                    hidden_scalar_reads=False,
                    construction_work_lower=2,
                ))
            for exponent in (0, 1, 2):
                candidates.append(candidate_record(
                    name=f"frobenius_coboundary_{exponent}_k{degree}",
                    family="frobenius_coboundary",
                    matrix=frobenius**exponent - frobenius ** (exponent + 1),
                    frobenius=frobenius,
                    rational_basis=rational_basis,
                    degree=degree,
                    order=order,
                    evaluator="public_frobenius_difference",
                    public_evaluator=True,
                    algebraic_correspondence=True,
                    hidden_scalar_reads=False,
                    construction_work_lower=2,
                ))

        large_degree_inclusion = candidate_record(
            name="large_degree_inclusion_kN",
            family="large_degree_control",
            matrix=identity_matrix(module, 2),
            frobenius=frobenius,
            rational_basis=rational_basis,
            degree=order,
            order=order,
            evaluator="public_inclusion",
            public_evaluator=True,
            algebraic_correspondence=True,
            hidden_scalar_reads=False,
            construction_work_lower=order,
        )
        oracle_matrix = Matrix(module, [[0, 0], [1, 0]])
        oracle_transfer = candidate_record(
            name="oracle_offdiagonal_eigenline_transfer",
            family="oracle_control",
            matrix=oracle_matrix,
            frobenius=frobenius,
            rational_basis=rational_basis,
            degree=nonrational_degree,
            order=order,
            evaluator="module_oracle_without_algebraic_map",
            public_evaluator=False,
            algebraic_correspondence=False,
            hidden_scalar_reads=False,
            construction_work_lower=nonrational_degree,
        )
        hidden_scalar_exact = all(
            oracle_matrix * (module(scalar) * rational_basis)
            == module(scalar) * nonrational_basis
            for scalar in range(order)
        )
        hidden_scalar_transfer = candidate_record(
            name="hidden_scalar_table_transfer",
            family="hidden_scalar_control",
            matrix=oracle_matrix,
            frobenius=frobenius,
            rational_basis=rational_basis,
            degree=nonrational_degree,
            order=order,
            evaluator="read_discrete_log_then_scale_nonrational_basis",
            public_evaluator=False,
            algebraic_correspondence=False,
            hidden_scalar_reads=True,
            construction_work_lower=order,
        )
        candidates.extend([
            large_degree_inclusion,
            oracle_transfer,
            hidden_scalar_transfer,
        ])

        coboundaries = [
            record for record in candidates if record["family"] == "frobenius_coboundary"
        ]
        bounded_nonzero = [
            record
            for record in candidates
            if record["extension_degree"] in BOUNDED_DEGREES
            and record["family"] != "frobenius_coboundary"
        ]
        mutated_frobenius = Matrix(frobenius)
        mutated_frobenius[1, 1] += 1
        mutated_trace = Matrix(nonrational_trace)
        mutated_trace[1, 1] += 1
        controls = {
            "bounded_inclusion_never_trace_zero": all(
                not record["trace_zero"]
                for record in bounded_nonzero
                if record["nonzero_on_rational_line"]
            ),
            "coboundaries_trace_zero_and_kill_rational_line": all(
                record["trace_zero"] and not record["nonzero_on_rational_line"]
                for record in coboundaries
            ),
            "oracle_nonzero_trace_zero": (
                oracle_transfer["nonzero_on_rational_line"]
                and oracle_transfer["trace_zero"]
            ),
            "oracle_fails_frobenius_commutation": not oracle_transfer[
                "commutes_with_frobenius"
            ],
            "hidden_scalar_table_exact": bool(hidden_scalar_exact),
            "hidden_scalar_control_rejected": (
                hidden_scalar_transfer["hidden_scalar_reads"]
                and not hidden_scalar_transfer["promotable"]
            ),
            "large_degree_inclusion_is_trace_zero": (
                large_degree_inclusion["nonzero_on_rational_line"]
                and large_degree_inclusion["trace_zero"]
            ),
            "large_degree_inclusion_fails_rho_gate": not large_degree_inclusion[
                "below_rho_extension_and_construction_gate"
            ],
            "frobenius_mutation_detected": (
                polynomial_ring(mutated_frobenius.charpoly())
                != expected_characteristic
            ),
            "trace_mutation_detected": not (
                mutated_trace * nonrational_basis
            ).is_zero(),
        }
        controls_exact = all(controls.values())
        module_exact = (
            centralizer_exact
            and bounded_trace_exact
            and minimum_degree_exact
            and controls_exact
        )
        field_promotable = any(record["promotable"] for record in candidates)
        any_promotable |= field_promotable
        all_field_arithmetic &= field_exact
        all_module_arithmetic &= module_exact
        all_controls &= controls_exact
        field_records.append({
            "p": p,
            "order": order,
            "holdout": holdout,
            "curve": dict(prior["curve"]),
            "generator": list(prior["generator"]),
            "curve_trace": trace,
            "ordinary": trace % p != 0,
            "frobenius_characteristic_polynomial": str(expected_characteristic),
            "frobenius_matrix": raw_matrix(frobenius),
            "curve_and_module_exact": bool(field_exact),
            "centralizer": {
                "operator": raw_matrix(centralizer),
                "rank": int(centralizer.rank()),
                "dimension": int(centralizer_kernel.dimension()),
                "basis": [list(item) for item in centralizer_basis],
                "offdiagonal_entries_forced_zero": bool(centralizer_exact),
                "preserves_rational_line": bool(centralizer_exact),
            },
            "bounded_degrees": list(BOUNDED_DEGREES),
            "bounded_rational_trace_exact": bool(bounded_trace_exact),
            "minimum_nonrational_trace_zero_degree": nonrational_degree,
            "minimum_nonrational_degree_over_rho": float(
                nonrational_degree / math.sqrt(order)
            ),
            "minimum_nonrational_degree_exponent": float(
                math.log(nonrational_degree) / math.log(order)
            ),
            "minimum_nonrational_trace_zero_exact": bool(minimum_degree_exact),
            "candidate_records": candidates,
            "candidate_family_counts": {
                family: sum(record["family"] == family for record in candidates)
                for family in sorted({record["family"] for record in candidates})
            },
            "controls": controls,
            "all_controls_exact": bool(controls_exact),
            "any_promotable_candidate": bool(field_promotable),
        })

    theorem_certificate = {
        "domain": "ordinary elliptic curves over Fp; algebraic maps and divisor correspondences into Res_{Fp^k/Fp}(E)",
        "morphism_origin_rule": "A morphism from an elliptic curve to an abelian variety sending O to 0 is a homomorphism.",
        "correspondence_rule": "A divisor correspondence induces a homomorphism on Jacobians.",
        "weil_restriction_adjunction": "Hom_Fp(E,Res(E)) equals End_Fp^k(E).",
        "ordinary_endomorphism_rule": "The geometric endomorphism algebra of an ordinary elliptic curve is commutative and every element commutes with Frobenius.",
        "module_consequence": "Every algebraic candidate preserves the Frobenius-fixed rational N-line; for 1<=k<N its trace-zero image on that line is zero.",
        "arithmetically_instantiated_on_all_fields": bool(
            all_field_arithmetic and all_module_arithmetic
        ),
    }
    correctness = (
        all(hash_gates.values())
        and all_field_arithmetic
        and all_module_arithmetic
        and all_controls
        and holdout_count == 1
    )
    if not correctness:
        status = "REVIEW_REQUIRED_P1501_FROBENIUS_TRACE_CERTIFICATE_MISMATCH"
        interpretation = (
            "At least one frozen hash, curve, Frobenius module, centralizer, trace, "
            "or control gate failed. No transfer conclusion is licensed."
        )
    elif any_promotable:
        status = "MIXED_RESULT_P1501_PUBLIC_TRACE_ZERO_TRANSFER_FOUND"
        interpretation = (
            "At least one frozen non-oracle candidate clears the bounded transfer "
            "gates. A separately contracted decomposition test is justified, not a breakthrough."
        )
    else:
        status = "NEGATIVE_RESULT_P1501_ORDINARY_ALGEBRAIC_TRACE_ZERO_TRANSFER_OBSTRUCTED"
        interpretation = (
            "On every frozen ordinary curve, algebraic maps and correspondences preserve "
            "the rational Frobenius line. Bounded-degree candidates either have nonzero "
            "trace or kill that line. The first nonrational trace-zero degree and the "
            "k=N inclusion control are already above the rho scale, while the off-diagonal "
            "transfer requires an oracle or hidden scalar."
        )
    payload = {
        "schema": SCHEMA,
        "status": status,
        "claim_status": "SCOPED ORDINARY ALGEBRAIC-TRANSFER OBSTRUCTION / NO GENERIC BREAKTHROUGH",
        "source": str(Path(__file__).resolve()),
        "source_sha256": sha256_file(Path(__file__).resolve()),
        "contract": str(CONTRACT),
        "contract_sha256": sha256_file(CONTRACT),
        "frozen_hashes": hashes,
        "hash_gates": hash_gates,
        "focus": {
            "active_lanes": active_focus,
            "max_active": int(focus_plan["max_active"]),
            "plan_sha256_internal": focus_plan["plan_sha256"],
        },
        "theorem_certificate": theorem_certificate,
        "field_records": field_records,
        "summary": {
            "field_count": len(field_records),
            "holdout_count": holdout_count,
            "all_field_arithmetic_exact": bool(all_field_arithmetic),
            "all_module_arithmetic_exact": bool(all_module_arithmetic),
            "all_controls_exact": bool(all_controls),
            "minimum_nonrational_degrees": [
                record["minimum_nonrational_trace_zero_degree"]
                for record in field_records
            ],
            "minimum_nonrational_degree_over_rho": [
                record["minimum_nonrational_degree_over_rho"]
                for record in field_records
            ],
            "any_promotable_candidate": bool(any_promotable),
        },
        "gates": {
            "all_frozen_hashes_exact": bool(all(hash_gates.values())),
            "all_curve_and_module_arithmetic_exact": bool(
                all_field_arithmetic and all_module_arithmetic
            ),
            "all_positive_and_negative_controls_exact": bool(all_controls),
            "bounded_public_trace_zero_transfer_found": bool(any_promotable),
            "trace_zero_decomposition_experiment_justified": bool(any_promotable),
            "p1500_nonsimple_prym_lane_unchanged": True,
            "generic_shoup_breakthrough": False,
            "beats_pollard_rho": False,
        },
        "interpretation": interpretation,
        "next_action": (
            "If negative, close ordinary algebraic trace-zero transfers on this frozen "
            "catalog and move the active focus slot to P1500's nonsimple-Prym cover census. "
            "Any future nonalgebraic transfer must provide an explicit point evaluator and "
            "full relation-to-target-descent cost below rho."
        ),
        "limitations": [
            "The theorem gate covers ordinary algebraic maps and divisor correspondences, not arbitrary nonalgebraic point algorithms.",
            "The four fields are toy-scale frozen cells; arithmetic agreement is not crypto-scale validation.",
            "The oracle off-diagonal and hidden-scalar controls validate instrumentation only.",
            "A negative does not close nonordinary curves, different abelian targets, growing-degree maps with proved sub-rho evaluation, or P1500.",
        ],
        "peak_rss_raw": int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss),
        "wall_seconds": float(time.time() - started),
    }
    write_atomic(
        OUT, (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    )
    write_atomic(NOTE, render_note(payload).encode("utf-8"))
    print(json.dumps({
        "status": status,
        "summary": payload["summary"],
        "gates": payload["gates"],
        "fields": [
            {
                "p": record["p"],
                "N": record["order"],
                "ord_N_p": record["minimum_nonrational_trace_zero_degree"],
                "over_rho": record["minimum_nonrational_degree_over_rho"],
                "promotable": record["any_promotable_candidate"],
            }
            for record in field_records
        ],
    }, indent=2, sort_keys=True))
    return 1 if status.startswith("REVIEW_REQUIRED") else 0


if __name__ == "__main__":
    raise SystemExit(main())
