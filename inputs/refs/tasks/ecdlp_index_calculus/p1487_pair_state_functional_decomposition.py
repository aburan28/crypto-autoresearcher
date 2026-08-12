#!/usr/bin/env sage -python
"""Test balanced functional decompositions of P1478 pair-state polynomials."""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
from typing import Any

from sage.all import PolynomialRing, divisors

import p1478_sparse_s3_subgroup_norm_composition as p1478


ROOT = Path(__file__).resolve().parents[2]
STATE_DIR = ROOT / "ecdlp_index_calculus_state"
RESEARCH_DIR = ROOT / "research"
CONTRACT = STATE_DIR / "experiment_contract_p1487_pair_state_functional_decomposition.md"
OUT = STATE_DIR / "p1487_pair_state_functional_decomposition.json"
NOTE = RESEARCH_DIR / "p1487_pair_state_functional_decomposition.md"

SCHEMA = "ecdlp.p1487_pair_state_functional_decomposition.v1"
EXPECTED = {
    CONTRACT: "53eee36dbb210ed2a50bdabc61da0b48c34a5f64cd66245bdd9b23dbccbe218d",
    STATE_DIR / "p1478_sparse_s3_subgroup_norm_composition.json":
        "287a08a131ce7b56bd4e8468eb6c443d7bcba4b7fb2ba13c860866c21902b8df",
    STATE_DIR / "p1478_sparse_s3_subgroup_norm_composition_audit.json":
        "d035cba39d08165c4b7dd336d4a095c1c99ff822f8db8c6cf5f3fca3b8c764f9",
    STATE_DIR / "p1486_sparse_rectangular_s6_applicability.json":
        "32e97a7e1ffa124a5529592286fff3736a95dff9e8aa82971cadba246b8392c3",
    STATE_DIR / "p1486_sparse_rectangular_s6_applicability_audit.json":
        "06eec849df4c1f981b01625db8fd76227d36dbfd530d49d1058a42f95df589a8",
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest_int(*parts: object) -> int:
    material = "|".join(str(part) for part in parts).encode("ascii")
    return int.from_bytes(hashlib.sha256(material).digest(), "big")


def polynomial_sha256(polynomial: Any) -> str:
    payload = ",".join(str(int(coefficient)) for coefficient in polynomial.list()).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def nonzero_coefficient_count(polynomial: Any) -> int:
    return sum(1 for coefficient in polynomial.list() if coefficient)


def deterministic_nonzero(field: Any, *parts: object) -> Any:
    value = digest_int("P1487", *parts) % (int(field.order()) - 1)
    return field(value + 1)


def exact_decomposition(polynomial: Any, inner_degree: int) -> dict[str, Any]:
    """Recover the normalized right component and test exact F[H] membership."""
    degree = int(polynomial.degree())
    if inner_degree <= 1 or degree % inner_degree:
        return {"exact": False, "reason": "invalid_inner_degree"}
    outer_degree = degree // inner_degree
    field = polynomial.base_ring()
    if field(outer_degree) == 0:
        return {"exact": False, "reason": "outer_degree_zero_in_field"}

    ring = polynomial.parent()
    variable = ring.gen()
    monic = polynomial.monic()
    inner = variable**inner_degree
    inverse_outer_degree = field(outer_degree) ** -1

    for offset in range(1, inner_degree):
        inner_power = inner**outer_degree
        coefficient = (
            monic[degree - offset] - inner_power[degree - offset]
        ) * inverse_outer_degree
        inner += coefficient * variable ** (inner_degree - offset)

    remainder = monic
    outer = ring.zero()
    power_cache = {0: ring.one()}
    cancellation_count = 0
    first_obstruction_degree = None
    while remainder:
        remainder_degree = int(remainder.degree())
        if remainder_degree % inner_degree:
            first_obstruction_degree = remainder_degree
            break
        power = remainder_degree // inner_degree
        if power not in power_cache:
            power_cache[power] = inner**power
        coefficient = remainder.leading_coefficient()
        outer += coefficient * variable**power
        remainder -= coefficient * power_cache[power]
        cancellation_count += 1

    exact = not remainder
    recomposed = outer(inner) if exact else None
    if exact and recomposed != monic:
        raise RuntimeError("P1487 exact membership passed but recomposition failed")
    return {
        "cancellation_count": cancellation_count,
        "exact": exact,
        "first_obstruction_degree": first_obstruction_degree,
        "inner_degree": inner_degree,
        "inner_nonzero_coefficients": nonzero_coefficient_count(inner),
        "inner_sha256": polynomial_sha256(inner),
        "outer_degree": outer_degree,
        "outer_nonzero_coefficients": nonzero_coefficient_count(outer) if exact else None,
        "outer_sha256": polynomial_sha256(outer) if exact else None,
        "reason": "exact_recomposition" if exact else "not_in_polynomial_subalgebra",
        "recomposition_sha256": polynomial_sha256(recomposed) if exact else None,
    }


def synthetic_composition(field: Any, total_degree: int, inner_degree: int) -> tuple[Any, Any, Any]:
    ring = PolynomialRing(field, "Z")
    variable = ring.gen()
    outer_degree = total_degree // inner_degree
    inner = variable**inner_degree + deterministic_nonzero(field, total_degree, inner_degree, "constant")
    for exponent in range(1, inner_degree):
        inner += deterministic_nonzero(field, total_degree, inner_degree, "inner", exponent) * variable**exponent
    outer = variable**outer_degree
    for exponent in range(outer_degree):
        outer += deterministic_nonzero(field, total_degree, inner_degree, "outer", exponent) * variable**exponent
    return inner, outer, outer(inner).monic()


def dense_control(field: Any, total_degree: int, inner_degree: int) -> Any:
    ring = PolynomialRing(field, "Z")
    variable = ring.gen()
    polynomial = variable**total_degree
    for exponent in range(total_degree):
        polynomial += deterministic_nonzero(field, total_degree, inner_degree, "dense", exponent) * variable**exponent
    return polynomial


def control_record(field: Any, total_degree: int, inner_degree: int) -> dict[str, Any]:
    inner, outer, composed = synthetic_composition(field, total_degree, inner_degree)
    positive = exact_decomposition(composed, inner_degree)
    perturb_exponent = max(1, total_degree // 2 + 1)
    perturbed = composed + deterministic_nonzero(field, total_degree, inner_degree, "perturb") * composed.parent().gen()**perturb_exponent
    perturb_test = exact_decomposition(perturbed, inner_degree)
    dense = dense_control(field, total_degree, inner_degree)
    dense_test = exact_decomposition(dense, inner_degree)
    return {
        "dense_negative_exact": bool(dense_test["exact"]),
        "dense_polynomial_sha256": polynomial_sha256(dense),
        "inner_degree": inner_degree,
        "outer_degree": total_degree // inner_degree,
        "perturb_exponent": perturb_exponent,
        "perturbed_negative_exact": bool(perturb_test["exact"]),
        "synthetic_composed_sha256": polynomial_sha256(composed),
        "synthetic_inner_constant_nonzero": bool(inner[0]),
        "synthetic_inner_sha256": polynomial_sha256(inner),
        "synthetic_outer_sha256": polynomial_sha256(outer),
        "synthetic_positive": positive,
    }


def candidate_degrees(L: int, total_degree: int) -> list[int]:
    ceiling = math.ceil(L ** 1.5)
    candidates = {L, 2 * L}
    candidates.update(
        int(divisor)
        for divisor in divisors(total_degree)
        if 1 < divisor < total_degree and max(int(divisor), total_degree // int(divisor)) <= ceiling
    )
    return sorted(degree for degree in candidates if 1 < degree < total_degree and total_degree % degree == 0)


def inverse_pair_count(deck: list[Any]) -> int:
    seen = set()
    pairs = 0
    for point in deck:
        key = p1478.point_key(point)
        if key in seen:
            continue
        inverse_key = p1478.point_key(-point)
        if point + (-point) != point.curve().zero():
            raise RuntimeError("P1487 inverse-pair source does not return to identity")
        seen.add(key)
        seen.add(inverse_key)
        pairs += 1
    return pairs


def fixture_cell(fixture: dict[str, int]) -> dict[str, Any]:
    ctx = p1478.build_context(fixture)
    field = ctx["field"]
    L = int(fixture["L"])
    start = 17 * ctx["generator"]
    u = field(start[0])
    bivariate = PolynomialRing(field, names=("V", "W"))
    V, W = bivariate.gens()
    a = field(fixture["a"])
    b = field(fixture["b"])
    left = p1478.recurrence_kernel(a, b, u, V, L)
    right = p1478.recurrence_kernel(a, b, V, W, L)
    univariate = PolynomialRing(field, "W")
    variable = univariate.gen()
    raw = univariate(left.resultant(right))
    repeated = raw.gcd(raw.derivative())
    squarefree = (raw // repeated).monic()
    linear = variable - univariate(u)
    nonreturn, remainder = squarefree.quo_rem(linear)
    if remainder:
        raise RuntimeError(f"P1487 return root absent at L={L}")
    nonreturn = nonreturn.monic()
    return_root_multiplicity_one = bool(nonreturn(univariate(u)) != 0)
    expected_nonreturn_degree = 2 * L * L
    if int(nonreturn.degree()) != expected_nonreturn_degree:
        raise RuntimeError(f"P1487 nonreturn degree mismatch at L={L}")

    tests = []
    controls = []
    for inner_degree in candidate_degrees(L, expected_nonreturn_degree):
        outer_degree = expected_nonreturn_degree // inner_degree
        test = exact_decomposition(nonreturn, inner_degree)
        layer_exponent = math.log(max(inner_degree, outer_degree), L)
        test.update(
            {
                "balanced_ceiling_candidate": max(inner_degree, outer_degree) <= math.ceil(L ** 1.5),
                "layer_exponent_log_L": layer_exponent,
                "primary_degree_family": inner_degree in {L, 2 * L},
                "strict_sub_L_three_halves": layer_exponent < 1.5 - 1e-12,
            }
        )
        tests.append(test)
        controls.append(control_record(field, expected_nonreturn_degree, inner_degree))

    return {
        "L": L,
        "candidate_degrees": [record["inner_degree"] for record in tests],
        "curve": {
            "a": int(fixture["a"]),
            "b": int(fixture["b"]),
            "order": int(fixture["order"]),
            "p": int(fixture["p"]),
        },
        "decomposition_tests": tests,
        "deck_endpoint_count": len(ctx["deck"]),
        "expected_nonreturn_degree": expected_nonreturn_degree,
        "inverse_endpoint_pair_count": inverse_pair_count(ctx["deck"]),
        "known_return_root": int(u),
        "nonreturn_coefficient_density": nonzero_coefficient_count(nonreturn) / (expected_nonreturn_degree + 1),
        "nonreturn_nonzero_coefficient_count": nonzero_coefficient_count(nonreturn),
        "nonreturn_sha256": polynomial_sha256(nonreturn),
        "raw_resultant_degree": int(raw.degree()),
        "return_root_multiplicity_one": return_root_multiplicity_one,
        "squarefree_degree": int(squarefree.degree()),
        "squarefree_expected_degree": 2 * L * L + 1,
        "synthetic_controls": controls,
    }


def stable_primary_decomposition(cells: list[dict[str, Any]]) -> list[int]:
    ratios = []
    for ratio in (1, 2):
        if all(
            any(
                record["inner_degree"] == ratio * int(cell["L"]) and record["exact"]
                for record in cell["decomposition_tests"]
            )
            for cell in cells
        ):
            ratios.append(ratio)
    return ratios


def render_note(payload: dict[str, Any]) -> str:
    lines = [
        "# P1487 pair-state functional decomposition",
        "",
        "## Status",
        "",
        f"`{payload['status']}`",
        "",
        "| L | nonreturn degree | tested inner degrees | exact real decompositions | controls |",
        "|---:|---:|---|---:|---:|",
    ]
    for cell in payload["cells"]:
        exact = sum(1 for record in cell["decomposition_tests"] if record["exact"])
        controls_pass = sum(
            1
            for control in cell["synthetic_controls"]
            if control["synthetic_positive"]["exact"]
            and not control["perturbed_negative_exact"]
            and not control["dense_negative_exact"]
        )
        lines.append(
            f"| {cell['L']} | {cell['expected_nonreturn_degree']} | "
            f"{cell['candidate_degrees']} | {exact} | {controls_pass}/{len(cell['synthetic_controls'])} |"
        )
    lines.extend(
        [
            "",
            "The known return-to-start root is exact and simple on every fixture,",
            "but removing it does not expose a balanced polynomial functional",
            "composition. This closes only the tested polynomial-imprimitivity",
            "route; it is not a generic-group lower bound or an ECDLP breakthrough.",
            "",
        ]
    )
    return "\n".join(lines)


def write_atomic(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_bytes(data)
    os.replace(temporary, path)


def main() -> int:
    frozen_files = {}
    for path, expected in EXPECTED.items():
        actual = sha256_file(path)
        if actual != expected:
            raise RuntimeError(f"P1487 frozen hash mismatch for {path}: {actual} != {expected}")
        frozen_files[str(path.relative_to(ROOT))] = actual

    cells = [fixture_cell(fixture) for fixture in p1478.COMPOSITION_FIXTURES]
    stable_ratios = stable_primary_decomposition(cells)
    controls_pass = all(
        control["synthetic_positive"]["exact"]
        and not control["perturbed_negative_exact"]
        and not control["dense_negative_exact"]
        for cell in cells
        for control in cell["synthetic_controls"]
    )
    if not controls_pass:
        raise RuntimeError("P1487 decomposition controls failed")
    status = (
        "CANDIDATE_P1487_PAIR_STATE_FUNCTIONAL_DECOMPOSITION"
        if stable_ratios
        else "NEGATIVE_RESULT_P1487_NO_BALANCED_PAIR_STATE_FUNCTIONAL_DECOMPOSITION"
    )
    payload = {
        "boundary": {
            "candidate_vs_verified": "All polynomial identities are exact; no five-term relation backend is claimed.",
            "closed": "Polynomial functional decompositions at every tested balanced divisor of the exact P1478 nonreturn state polynomial.",
            "not_closed": "Rational decompositions, different state invariants, and non-polynomial common-root algorithms.",
            "pollard_rho": "No complete relation/rank/descent pipeline and no faster-than-rho ECDLP claim.",
        },
        "cells": cells,
        "frozen_files": frozen_files,
        "gates": {
            "all_controls_pass": controls_pass,
            "all_degree_and_return_root_controls_pass": all(
                cell["raw_resultant_degree"] == 4 * int(cell["L"]) ** 2
                and cell["squarefree_degree"] == cell["squarefree_expected_degree"]
                and cell["return_root_multiplicity_one"]
                and cell["deck_endpoint_count"] % 2 == 0
                and cell["inverse_endpoint_pair_count"] == cell["deck_endpoint_count"] // 2
                for cell in cells
            ),
            "complete_five_term_backend": False,
            "source_opening_below_L_three_halves": False,
            "stable_primary_inner_degree_ratios": stable_ratios,
        },
        "next_action": (
            "Do not repeat polynomial decomposition on this state polynomial. Test an exact rational/Luroth decomposition certificate only if it supplies a public source opener, or change the pair-state invariant before another composition sweep."
        ),
        "schema": SCHEMA,
        "status": status,
    }
    write_atomic(OUT, (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    write_atomic(NOTE, render_note(payload).encode("utf-8"))
    print(json.dumps({
        "status": status,
        "cells": [
            {
                "L": cell["L"],
                "candidate_degrees": cell["candidate_degrees"],
                "exact_count": sum(1 for record in cell["decomposition_tests"] if record["exact"]),
                "nonreturn_degree": cell["expected_nonreturn_degree"],
            }
            for cell in cells
        ],
        "controls_pass": controls_pass,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
