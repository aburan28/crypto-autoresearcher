"""Independently replay the frozen geometric kernel census from its raw rows."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

from sage.all import EllipticCurve, GF, classical_modular_polynomial

ARMS = {"target": (1, 6, 22), "null": (2, 3, 10)}
PRIMES = (3, 5, 7)


def check_element_receipt(value, receipt):
    field, element, embedding = value.as_finite_field_element()
    degree = int(field.degree())
    assert receipt["closure_text"] == str(value)
    assert receipt["minimal_polynomial"] == str(value.minpoly())
    assert receipt["finite_subfield_degree"] == degree
    assert receipt["finite_subfield_modulus"] == (
        str(field.modulus()) if degree > 1 else None
    )
    assert receipt["finite_subfield_element"] == str(element)
    assert receipt["generator_image_in_closure"] == str(embedding(field.gen()))


def check_arm(closure, name, raw):
    a, b, expected_discriminant = ARMS[name]
    curve = EllipticCurve(closure, [a, b])
    assert (4 * a**3 + 27 * b**2) % 53 == expected_discriminant != 0
    assert raw["discriminant_factor_mod_53"] == expected_discriminant
    check_element_receipt(curve.j_invariant(), raw["source_j"])
    recorded = raw["rows"]
    assert len(recorded) == 18
    assert Counter(row["ell"] for row in recorded) == {3: 4, 5: 6, 7: 8}
    actual = {}
    all_j = []
    for ell in PRIMES:
        isogenies = list(curve.isogenies_prime_degree(ell))
        assert len(isogenies) == ell + 1
        modular_polynomial = classical_modular_polynomial(ell)
        for isogeny in isogenies:
            polynomial = isogeny.kernel_polynomial().monic()
            j = isogeny.codomain().j_invariant()
            key = (ell, str(polynomial))
            assert key not in actual
            assert int(polynomial.degree()) == (ell - 1) // 2
            assert int(isogeny.degree()) == ell
            assert polynomial.leading_coefficient() == 1
            assert modular_polynomial(curve.j_invariant(), j) == 0
            actual[key] = (polynomial, j)
            all_j.append(j)
    assert len(actual) == len(recorded)
    seen = set()
    for row in recorded:
        key = (row["ell"], row["kernel_polynomial"])
        assert key in actual and key not in seen
        seen.add(key)
        polynomial, j = actual[key]
        assert row["arm"] == name
        assert row["isogeny_degree"] == key[0]
        assert row["kernel_degree"] == int(polynomial.degree())
        assert row["kernel_monic"] is True
        assert row["modular_relation_zero"] is True
        coefficients = polynomial.list()
        assert len(row["kernel_coefficients"]) == len(coefficients)
        for value, receipt in zip(coefficients, row["kernel_coefficients"]):
            check_element_receipt(value, receipt)
        check_element_receipt(j, row["codomain_j"])
    assert raw["counts_by_degree"] == {str(ell): ell + 1 for ell in PRIMES}
    assert raw["S"] == sum(row["kernel_degree"] for row in recorded)
    assert raw["J"] == len(set(all_j))
    assert all(raw["checks"].values())
    collision_classes = {}
    for row in recorded:
        collision_classes.setdefault(row["codomain_j"]["closure_text"], []).append(
            {"ell": row["ell"], "kernel_polynomial": row["kernel_polynomial"]}
        )
    assert raw["codomain_collision_classes"] == collision_classes


def check(run_dir: Path):
    data = json.loads((run_dir / "raw-result.json").read_text(encoding="utf-8"))
    assert data["experiment_id"] == "EXP-SSIQ-dcb6d6"
    assert data["run_id"] == "RUN-SSIQ-9fe433"
    assert data["field"]["base"] == "GF(53)"
    assert data["degrees"] == list(PRIMES)
    closure = GF(53).algebraic_closure()
    for name in ARMS:
        check_arm(closure, name, data["arms"][name])
    assert data["all_checks_pass"] is True
    target = data["arms"]["target"]
    base = max(1, target["J"])
    assert data["target_threshold_base"] == base
    if target["S"] >= 4 * base:
        reading = "positive"
    elif target["S"] <= 3 * base:
        reading = "negative"
    else:
        reading = "inconclusive"
    assert data["reading_row"] == reading


if __name__ == "__main__":
    check(Path(sys.argv[1]))
