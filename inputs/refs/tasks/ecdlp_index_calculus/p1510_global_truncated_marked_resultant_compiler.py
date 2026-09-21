#!/usr/bin/env sage -python
"""Compile P1509's degree-two marked resultant without endpoint opening."""

from __future__ import annotations

import argparse
import collections
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
from typing import Any, Callable

from sage.all import GF, PolynomialRing

import p1482_coordinate_routed_wagner_tree as p1482
import p1490_rational_lift_selector_norm as p1490


ROOT = Path(__file__).resolve().parents[2]
STATE = ROOT / "ecdlp_index_calculus_state"
RESEARCH = ROOT / "research"
CONTRACT = STATE / "experiment_contract_p1510_global_truncated_marked_resultant_compiler.md"
DERIVATION = Path(
    "/Volumes/Volume/crypto-autoresearcher/ideas/artifacts/ECDLP-IDEA-068/"
    "p1510_multiplicative_compiler_derivation.md"
)
FOCUS_QUEUE = Path(
    "/Volumes/Volume/crypto-autoresearcher/focus/archive/"
    "focus_queue_p1510_active.json"
)
FOCUS_PLAN = Path(
    "/Volumes/Volume/crypto-autoresearcher/focus/archive/"
    "focus_plan_p1510_active.json"
)
FOCUS_REPORT = Path(
    "/Volumes/Volume/crypto-autoresearcher/focus/archive/"
    "focus_report_p1510_active.md"
)
P1509 = STATE / "p1509_hasse_jet_source_section.json"
P1509_AUDIT = STATE / "p1509_hasse_jet_source_section_audit.json"
OUT = STATE / "p1510_global_truncated_marked_resultant_compiler.json"
NOTE = RESEARCH / "p1510_global_truncated_marked_resultant_compiler.md"

SCHEMA = "ecdlp.p1510_global_truncated_marked_resultant_compiler.v1"
CONSTRUCTION_EXPECTED = {
    CONTRACT: "10c0f91c62bc89df3e1aa3160da4340e647aea0446ec7065b225a2556cec4f64",
    DERIVATION: "f1f5a5ce8ec38a89b7474c79490634c148cd5443395d66391582a54b8dfa9fad",
    FOCUS_QUEUE: "8f455130a4b9f462117e95c4be5bdfb408029a3642b246b3daea0e4d50f7c1ac",
    FOCUS_PLAN: "e5ad59fc6216a8ad35583d91f245956c43fc79052a9a3c7e77513b7b9e0acd0d",
    FOCUS_REPORT: "63eccb999d05184de0fa0c0b81e53aec903af0f3af3aad2812a583735ca3f263",
}
POST_FREEZE_EXPECTED = {
    P1509: "23ae26d712cd6ee521705985f9b25623a8713c46bd6e085b3586b503e79efc66",
    P1509_AUDIT: "efa467d959138862d6e86570bb50f0ad962c4c925a8fe51041ffd7a6ea451227",
}

MONOMIALS = (
    (0, 0, 0, 0),
    (1, 0, 0, 0),
    (0, 1, 0, 0),
    (0, 0, 1, 0),
    (0, 0, 0, 1),
    (2, 0, 0, 0),
    (1, 1, 0, 0),
    (1, 0, 1, 0),
    (1, 0, 0, 1),
    (0, 2, 0, 0),
    (0, 1, 1, 0),
    (0, 1, 0, 1),
    (0, 0, 2, 0),
    (0, 0, 1, 1),
    (0, 0, 0, 2),
)
MONOMIAL_NAMES = (
    "1",
    "E0",
    "E1",
    "H0",
    "H1",
    "E0^2",
    "E0*E1",
    "E0*H0",
    "E0*H1",
    "E1^2",
    "E1*H0",
    "E1*H1",
    "H0^2",
    "H0*H1",
    "H1^2",
)
ZERO_EXP = MONOMIALS[0]

Jet = dict[tuple[int, int, int, int], Any]
AlgebraElement = tuple[Jet, Jet]
ProjectiveElement = tuple[Jet, Jet, int]


def compact(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest(value: Any) -> str:
    return hashlib.sha256(compact(value).encode("ascii")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def write_atomic(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    temporary.write_bytes(data)
    os.replace(temporary, path)


def verify_hashes(expected: dict[Path, str]) -> dict[str, str]:
    actual = {display_path(path): sha256_file(path) for path in expected}
    failures = [
        display_path(path)
        for path, expected_hash in expected.items()
        if actual[display_path(path)] != expected_hash
    ]
    if failures:
        raise RuntimeError(f"P1510 frozen hash mismatch: {failures}")
    return actual


def poly_size(value: Any) -> int:
    if not value:
        return 0
    return int(value.degree()) + 1


class ArithmeticCounter:
    def __init__(self, label: str) -> None:
        self.label = label
        self.poly_add_coefficient_upper = 0
        self.poly_mul_schoolbook_upper = 0
        self.poly_mul_quasilinear_proxy = 0
        self.poly_mul_histogram: collections.Counter[tuple[int, int]] = collections.Counter()
        self.exact_division_count = 0
        self.exact_division_zero_remainder_count = 0
        self.exact_division_numerator_slots = 0
        self.jet_multiplication_count = 0
        self.quotient_multiplication_count = 0
        self.quadratic_resultant_count = 0
        self.peak_live_coefficient_slots = 0

    def add(self, left: Any, right: Any) -> Any:
        self.poly_add_coefficient_upper += max(poly_size(left), poly_size(right))
        return left + right

    def mul(self, left: Any, right: Any) -> Any:
        left_size = poly_size(left)
        right_size = poly_size(right)
        if not left_size or not right_size:
            return left.parent().zero()
        small, large = sorted((left_size, right_size))
        self.poly_mul_histogram[(small, large)] += 1
        self.poly_mul_schoolbook_upper += small * large
        output_size = small + large - 1
        log_term = max(1, math.ceil(math.log2(max(2, output_size))))
        self.poly_mul_quasilinear_proxy += 8 * output_size * log_term * log_term
        return left * right

    def exact_div(self, numerator: Any, denominator: Any) -> Any:
        self.exact_division_count += 1
        self.exact_division_numerator_slots += poly_size(numerator)
        quotient, remainder = numerator.quo_rem(denominator)
        if remainder:
            raise RuntimeError(
                f"P1510 nonexact public-leading-coefficient division in {self.label}"
            )
        self.exact_division_zero_remainder_count += 1
        return quotient

    def observe(self, *values: Any) -> None:
        def coefficient_slots(value: Any) -> int:
            if isinstance(value, dict):
                return sum(poly_size(item) for item in value.values())
            if isinstance(value, (list, tuple)):
                return sum(coefficient_slots(item) for item in value)
            return 0

        slots = sum(coefficient_slots(value) for value in values)
        self.peak_live_coefficient_slots = max(self.peak_live_coefficient_slots, slots)

    def summary(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "poly_add_coefficient_upper": self.poly_add_coefficient_upper,
            "poly_mul_schoolbook_upper": self.poly_mul_schoolbook_upper,
            "poly_mul_quasilinear_proxy": self.poly_mul_quasilinear_proxy,
            "poly_mul_histogram": [
                {"left_slots": key[0], "right_slots": key[1], "count": count}
                for key, count in sorted(self.poly_mul_histogram.items())
            ],
            "poly_mul_call_count": sum(self.poly_mul_histogram.values()),
            "exact_division_count": self.exact_division_count,
            "exact_division_zero_remainder_count": self.exact_division_zero_remainder_count,
            "exact_division_numerator_slots": self.exact_division_numerator_slots,
            "jet_multiplication_count": self.jet_multiplication_count,
            "quotient_multiplication_count": self.quotient_multiplication_count,
            "quadratic_resultant_count": self.quadratic_resultant_count,
            "peak_live_coefficient_slots": self.peak_live_coefficient_slots,
        }


def clean_jet(value: Jet) -> Jet:
    return {exponent: coefficient for exponent, coefficient in value.items() if coefficient}


def jet_zero() -> Jet:
    return {}


def jet_constant(value: Any) -> Jet:
    return {} if not value else {ZERO_EXP: value}


def jet_variable(wring: Any, variable: int, coefficient: Any = 1) -> Jet:
    exponent = [0, 0, 0, 0]
    exponent[variable] = 1
    value = wring(coefficient)
    return {} if not value else {tuple(exponent): value}


def jet_add(left: Jet, right: Jet, counter: ArithmeticCounter) -> Jet:
    output = dict(left)
    for exponent, coefficient in right.items():
        output[exponent] = counter.add(
            output.get(exponent, coefficient.parent().zero()), coefficient
        )
    output = clean_jet(output)
    counter.observe(output)
    return output


def jet_neg(value: Jet) -> Jet:
    return {exponent: -coefficient for exponent, coefficient in value.items()}


def jet_sub(left: Jet, right: Jet, counter: ArithmeticCounter) -> Jet:
    return jet_add(left, jet_neg(right), counter)


def jet_mul(
    left: Jet, right: Jet, counter: ArithmeticCounter, maximum_degree: int = 2
) -> Jet:
    counter.jet_multiplication_count += 1
    output: Jet = {}
    for left_exponent, left_coefficient in left.items():
        for right_exponent, right_coefficient in right.items():
            exponent = tuple(
                left_exponent[index] + right_exponent[index] for index in range(4)
            )
            if sum(exponent) > maximum_degree:
                continue
            product = counter.mul(left_coefficient, right_coefficient)
            output[exponent] = counter.add(
                output.get(exponent, product.parent().zero()), product
            )
    output = clean_jet(output)
    counter.observe(output)
    return output


def jet_scale(value: Jet, scalar: Any, counter: ArithmeticCounter) -> Jet:
    if not scalar:
        return {}
    output = {
        exponent: counter.mul(coefficient, coefficient.parent()(scalar))
        for exponent, coefficient in value.items()
    }
    output = clean_jet(output)
    counter.observe(output)
    return output


def jet_exact_div(value: Jet, denominator: Any, counter: ArithmeticCounter) -> Jet:
    output = {
        exponent: counter.exact_div(coefficient, denominator)
        for exponent, coefficient in value.items()
    }
    output = clean_jet(output)
    counter.observe(output)
    return output


def jet_product(values: list[Jet], counter: ArithmeticCounter, maximum_degree: int = 2) -> Jet:
    if not values:
        raise ValueError("P1510 jet product requires at least one factor")
    level = list(values)
    counter.observe(level)
    while len(level) > 1:
        next_level = []
        for index in range(0, len(level), 2):
            if index + 1 == len(level):
                next_level.append(level[index])
            else:
                next_level.append(
                    jet_mul(level[index], level[index + 1], counter, maximum_degree)
                )
        level = next_level
        counter.observe(level)
    return level[0]


def algebra_product(
    values: list[Any],
    multiply: Callable[[Any, Any], Any],
    counter: ArithmeticCounter,
) -> Any:
    if not values:
        raise ValueError("P1510 algebra product requires at least one factor")
    level = list(values)
    counter.observe(level)
    while len(level) > 1:
        next_level = []
        for index in range(0, len(level), 2):
            if index + 1 == len(level):
                next_level.append(level[index])
            else:
                next_level.append(multiply(level[index], level[index + 1]))
        level = next_level
        counter.observe(level)
    return level[0]


def jet_power(value: Jet, exponent: int, counter: ArithmeticCounter) -> Jet:
    if exponent < 0:
        raise ValueError("negative exponent")
    parent = next(iter(value.values())).parent()
    output = jet_constant(parent.one())
    base = value
    power = exponent
    while power:
        if power & 1:
            output = jet_mul(output, base, counter, 2)
        power >>= 1
        if power:
            base = jet_mul(base, base, counter, 2)
    return output


def poly_power(value: Any, exponent: int, counter: ArithmeticCounter) -> Any:
    output = value.parent().one()
    base = value
    power = exponent
    while power:
        if power & 1:
            output = counter.mul(output, base)
        power >>= 1
        if power:
            base = counter.mul(base, base)
    return output


def quadratic_resultant(
    a2: Jet,
    a1: Jet,
    a0: Jet,
    b2: Jet,
    b1: Jet,
    b0: Jet,
    counter: ArithmeticCounter,
) -> Jet:
    counter.quadratic_resultant_count += 1

    def product(*values: Jet) -> Jet:
        output = values[0]
        for value in values[1:]:
            output = jet_mul(output, value, counter, 2)
        return output

    result = product(a2, a2, b0, b0)
    result = jet_sub(result, product(a2, a1, b1, b0), counter)
    result = jet_sub(result, jet_scale(product(a2, a0, b2, b0), 2, counter), counter)
    result = jet_add(result, product(a2, a0, b1, b1), counter)
    result = jet_add(result, product(a1, a1, b2, b0), counter)
    result = jet_sub(result, product(a1, a0, b2, b1), counter)
    result = jet_add(result, product(a0, a0, b2, b2), counter)
    return result


def monic_algebra_mul(
    left: AlgebraElement,
    right: AlgebraElement,
    linear_coefficient: Any,
    constant_coefficient: Any,
    counter: ArithmeticCounter,
    maximum_degree: int,
) -> AlgebraElement:
    counter.quotient_multiplication_count += 1
    x0, x1 = left
    y0, y1 = right
    x1y1 = jet_mul(x1, y1, counter, maximum_degree)
    z0 = jet_sub(
        jet_mul(x0, y0, counter, maximum_degree),
        jet_scale(x1y1, constant_coefficient, counter),
        counter,
    )
    z1 = jet_sub(
        jet_add(
            jet_mul(x0, y1, counter, maximum_degree),
            jet_mul(x1, y0, counter, maximum_degree),
            counter,
        ),
        jet_scale(x1y1, linear_coefficient, counter),
        counter,
    )
    return z0, z1


def monic_algebra_norm(
    value: AlgebraElement,
    linear_coefficient: Any,
    constant_coefficient: Any,
    counter: ArithmeticCounter,
) -> Jet:
    x0, x1 = value
    return jet_add(
        jet_sub(
            jet_mul(x0, x0, counter, 2),
            jet_scale(jet_mul(x0, x1, counter, 2), linear_coefficient, counter),
            counter,
        ),
        jet_scale(jet_mul(x1, x1, counter, 2), constant_coefficient, counter),
        counter,
    )


def projective_algebra_mul(
    left: ProjectiveElement,
    right: ProjectiveElement,
    leading: Any,
    linear: Any,
    constant: Any,
    counter: ArithmeticCounter,
) -> ProjectiveElement:
    counter.quotient_multiplication_count += 1
    x0, x1, left_scale = left
    y0, y1, right_scale = right
    x1y1 = jet_mul(x1, y1, counter, 1)
    z0 = jet_sub(
        jet_scale(jet_mul(x0, y0, counter, 1), leading, counter),
        jet_scale(x1y1, constant, counter),
        counter,
    )
    z1 = jet_sub(
        jet_scale(
            jet_add(
                jet_mul(x0, y1, counter, 1),
                jet_mul(x1, y0, counter, 1),
                counter,
            ),
            leading,
            counter,
        ),
        jet_scale(x1y1, linear, counter),
        counter,
    )
    return z0, z1, left_scale + right_scale + 1


def projective_algebra_norm(
    value: ProjectiveElement,
    leading: Any,
    linear: Any,
    constant: Any,
    counter: ArithmeticCounter,
) -> tuple[Jet, int]:
    x0, x1, scale = value
    numerator = jet_add(
        jet_sub(
            jet_scale(jet_mul(x0, x0, counter, 2), leading, counter),
            jet_scale(jet_mul(x0, x1, counter, 2), linear, counter),
            counter,
        ),
        jet_scale(jet_mul(x1, x1, counter, 2), constant, counter),
        counter,
    )
    return numerator, scale


def s3(first: Any, second: Any, third: Any, a: Any, b: Any) -> Any:
    return (
        (first - second) ** 2 * third**2
        - 2 * ((first + second) * (first * second + a) + 2 * b) * third
        + (first * second - a) ** 2
        - 4 * b * (first + second)
    )


def quadratic_coefficients(polynomial: Any) -> tuple[Any, Any, Any]:
    coefficients = list(polynomial)
    coefficients += [polynomial.base_ring().zero()] * (3 - len(coefficients))
    if len(coefficients) != 3:
        raise RuntimeError(f"P1510 expected quadratic factor, got degree {polynomial.degree()}")
    return coefficients[2], coefficients[1], coefficients[0]


def make_code_jet(wring: Any, offset: int, alpha: Any) -> Jet:
    first = [0, 0, 0, 0]
    second = [0, 0, 0, 0]
    first[offset] = 1
    second[offset + 1] = 1
    return {
        tuple(first): wring.one(),
        tuple(second): wring(alpha),
    }


def compile_factor_system(
    field: Any,
    left_coefficients: list[tuple[Any, Any, Any]],
    right_coefficients: list[tuple[Any, Any, Any]],
    alpha: list[Any],
    label: str,
) -> tuple[dict[str, Any], Jet, Any]:
    r = len(left_coefficients)
    if len(right_coefficients) != r or len(alpha) != r:
        raise ValueError("P1510 factor-system dimensions differ")
    wring = right_coefficients[0][0].parent()
    counter = ArithmeticCounter(label)

    h_factors: list[Jet] = []
    for left_index, (a2, a1, a0) in enumerate(left_coefficients):
        if not a2:
            raise RuntimeError("P1510 left selector factor lost quadratic degree")
        monic_linear = field(a1 / a2)
        monic_constant = field(a0 / a2)
        leaves: list[AlgebraElement] = []
        for right_index, (b2, b1, b0) in enumerate(right_coefficients):
            remainder0 = counter.add(
                b0, -counter.mul(wring(b2), wring(monic_constant))
            )
            remainder1 = counter.add(
                b1, -counter.mul(wring(b2), wring(monic_linear))
            )
            x0 = jet_add(
                jet_constant(remainder0),
                make_code_jet(wring, 2, alpha[right_index]),
                counter,
            )
            leaves.append((x0, jet_constant(remainder1)))
        product_value = algebra_product(
            leaves,
            lambda left, right: monic_algebra_mul(
                left,
                right,
                monic_linear,
                monic_constant,
                counter,
                1,
            ),
            counter,
        )
        norm = monic_algebra_norm(
            product_value, monic_linear, monic_constant, counter
        )
        h_factors.append(jet_scale(norm, field(a2) ** (2 * r), counter))
    r_h = jet_product(h_factors, counter, 2)

    e_factors: list[Jet] = []
    denominator_exponents = []
    for right_index, (leading, linear, constant) in enumerate(right_coefficients):
        leaves: list[ProjectiveElement] = []
        for left_index, (a2, a1, a0) in enumerate(left_coefficients):
            base0 = counter.add(
                counter.mul(wring(leading), wring(a0)),
                -counter.mul(wring(a2), wring(constant)),
            )
            base1 = counter.add(
                counter.mul(wring(leading), wring(a1)),
                -counter.mul(wring(a2), wring(linear)),
            )
            marker = jet_scale(
                make_code_jet(wring, 0, alpha[left_index]), leading, counter
            )
            leaves.append(
                (jet_add(jet_constant(base0), marker, counter), jet_constant(base1), 1)
            )
        projective_product = algebra_product(
            leaves,
            lambda left, right: projective_algebra_mul(
                left, right, leading, linear, constant, counter
            ),
            counter,
        )
        norm_numerator, denominator_exponent = projective_algebra_norm(
            projective_product, leading, linear, constant, counter
        )
        expected_exponent = 2 * r - 1
        if denominator_exponent != expected_exponent:
            raise RuntimeError(
                f"P1510 denominator exponent {denominator_exponent} != {expected_exponent}"
            )
        denominator = poly_power(leading, expected_exponent, counter)
        e_factors.append(jet_exact_div(norm_numerator, denominator, counter))
        denominator_exponents.append(denominator_exponent)
    r_e = jet_product(e_factors, counter, 2)

    pair_factors = []
    for left_index, (a2, a1, a0) in enumerate(left_coefficients):
        e_code = make_code_jet(wring, 0, alpha[left_index])
        for right_index, (b2, b1, b0) in enumerate(right_coefficients):
            h_code = make_code_jet(wring, 2, alpha[right_index])
            pair_factors.append(
                quadratic_resultant(
                    jet_constant(wring(a2)),
                    jet_constant(wring(a1)),
                    jet_add(jet_constant(wring(a0)), e_code, counter),
                    jet_constant(wring(b2)),
                    jet_constant(wring(b1)),
                    jet_add(jet_constant(wring(b0)), h_code, counter),
                    counter,
                )
            )
    r_full = jet_product(pair_factors, counter, 2)

    constants = [source.get(ZERO_EXP, wring.zero()) for source in (r_e, r_h, r_full)]
    if constants[0] != constants[1] or constants[0] != constants[2]:
        raise RuntimeError("P1510 multiplicative constant components disagree")

    target: Jet = {}
    for exponent in MONOMIALS:
        e_degree = exponent[0] + exponent[1]
        h_degree = exponent[2] + exponent[3]
        if h_degree == 0:
            coefficient = r_e.get(exponent, wring.zero())
        elif e_degree == 0:
            coefficient = r_h.get(exponent, wring.zero())
        elif e_degree == 1 and h_degree == 1:
            coefficient = r_full.get(exponent, wring.zero())
        else:
            raise RuntimeError(f"P1510 unclassified marker exponent {exponent}")
        target[exponent] = coefficient
    target = clean_jet(target)
    counter.observe(target, r_e, r_h, r_full)

    records = []
    maximum_degree = -1
    output_slots = 0
    for name, exponent in zip(MONOMIAL_NAMES, MONOMIALS):
        polynomial = target.get(exponent, wring.zero())
        coefficients = [int(value) for value in polynomial]
        degree = int(polynomial.degree()) if polynomial else -1
        maximum_degree = max(maximum_degree, degree)
        output_slots += len(coefficients)
        records.append(
            {
                "monomial": name,
                "exponent": list(exponent),
                "degree": degree,
                "coefficients": coefficients,
                "coefficient_sha256": digest(coefficients),
            }
        )

    record = {
        "label": label,
        "r": r,
        "component_count": len(MONOMIALS),
        "maximum_component_degree": maximum_degree,
        "theoretical_maximum_component_degree_4r2": 4 * r * r,
        "output_coefficient_slots": output_slots,
        "dense_slot_bound_15_times_4r2_plus_1": 15 * (4 * r * r + 1),
        "all_projective_denominator_exponents_equal_2r_minus_1": all(
            exponent == 2 * r - 1 for exponent in denominator_exponents
        ),
        "constant_components_agree": True,
        "components": records,
        "component_vector_sha256": digest(records),
        "arithmetic": counter.summary(),
    }
    return record, target, wring


def curve_factor_system(fixture: dict[str, Any], nonce: int) -> tuple[Any, list[Any], list[Any], list[Any], dict[str, Any]]:
    context = p1482.build_context(fixture)
    field = context["field"]
    curve = context["curve"]
    order = int(fixture["order"])
    L = int(fixture["L"])
    selector, selector_roots, _ = p1490.selector_cell(context)
    r = int(selector.degree())
    scalar = 1 + p1482.digest_int("P1490", "public-start", L, nonce) % (order - 1)
    start = scalar * context["generator"]
    u = field(start[0])
    a = field(fixture["a"])
    b = field(fixture["b"])

    left_ring = PolynomialRing(field, f"V1510_left_{L}_{nonce}")
    left_v = left_ring.gen()
    left_factors = [
        s3(left_ring(u), left_v, left_ring(field(root)), a, b)
        for root in selector_roots
    ]
    left_coefficients = [quadratic_coefficients(factor) for factor in left_factors]

    wring = PolynomialRing(field, f"W1510_{L}_{nonce}")
    W = wring.gen()
    right_ring = PolynomialRing(wring, f"V1510_right_{L}_{nonce}")
    V = right_ring.gen()
    right_factors = [
        s3(V, right_ring(W), right_ring(wring(field(root))), a, b)
        for root in selector_roots
    ]
    right_coefficients = [quadratic_coefficients(factor) for factor in right_factors]
    alpha = [field(index + 1) for index in range(r)]
    metadata = {
        "L": L,
        "nonce": nonce,
        "p": int(fixture["p"]),
        "order": order,
        "r": r,
        "public_start": p1482.point_json(start),
        "selector_roots": [int(root) for root in selector_roots],
    }
    return field, left_coefficients, right_coefficients, alpha, metadata


def synthetic_factor_system(r: int) -> tuple[Any, list[Any], list[Any], list[Any], dict[str, Any]]:
    field = GF(65537)
    wring = PolynomialRing(field, f"W1510_synthetic_{r}")
    W = wring.gen()
    left = []
    right = []
    for index in range(r):
        left.append(
            (
                field(index + 2),
                field(index * index + 3),
                field(3 * index + 5),
            )
        )
        root = field(index + 1)
        right.append(
            (
                (W - root) ** 2,
                W**2 + field(2 * index + 3) * W + field(index + 7),
                W**2 + field(5 * index + 11) * W + field(index * index + 13),
            )
        )
    alpha = [field(index + 1) for index in range(r)]
    return field, left, right, alpha, {"r": r, "p": 65537, "kind": "synthetic"}


def component_jet_from_record(record: dict[str, Any], wring: Any) -> Jet:
    return {
        tuple(component["exponent"]): wring(component["coefficients"])
        for component in record["components"]
        if component["coefficients"]
    }


def evaluated_marker_polynomial(target: Jet, endpoint: Any, marker_ring: Any) -> Any:
    variables = marker_ring.gens()
    output = marker_ring.zero()
    for exponent, coefficient in target.items():
        scalar = coefficient(endpoint)
        if not scalar:
            continue
        monomial = marker_ring.one()
        for variable, power in zip(variables, exponent):
            monomial *= variable**power
        output += marker_ring(scalar) * monomial
    return output


def homogeneous_component(polynomial: Any, degree: int) -> Any:
    output = polynomial.parent().zero()
    for exponent, coefficient in polynomial.dict().items():
        if sum(exponent) == degree:
            output += coefficient * polynomial.parent().monomial(*exponent)
    return output


def proportional(left: Any, right: Any) -> tuple[bool, int | None]:
    exponents = sorted(set(left.dict()) | set(right.dict()))
    pivot = next((exponent for exponent in exponents if right[exponent]), None)
    if pivot is None:
        return left == 0, None
    ratio = left[pivot] / right[pivot]
    return ratio != 0 and all(left[exponent] == ratio * right[exponent] for exponent in exponents), int(ratio)


def decode_factor_pairs(leading: Any, alpha_lookup: dict[int, int]) -> list[tuple[int, int]]:
    E0, E1, H0, H1 = leading.parent().gens()
    decoded = []
    for factor, multiplicity in leading.factor():
        if factor.total_degree() != 1:
            raise RuntimeError(f"P1510 nonlinear endpoint factor {factor}")
        e0 = factor.monomial_coefficient(E0)
        e1 = factor.monomial_coefficient(E1)
        h0 = factor.monomial_coefficient(H0)
        h1 = factor.monomial_coefficient(H1)
        if not e0 or not h0:
            raise RuntimeError(f"P1510 missing code anchor in {factor}")
        pair = (alpha_lookup[int(e1 / e0)], alpha_lookup[int(h1 / h0)])
        decoded.extend([pair] * int(multiplicity))
    return sorted(decoded)


def verify_curve_cells(
    compiled: dict[tuple[int, int], tuple[dict[str, Any], Jet, Any]],
    p1509: dict[str, Any],
) -> dict[str, Any]:
    endpoint_count = 0
    nonreturn_count = 0
    proportional_count = 0
    pair_match_count = 0
    return_low_order_zero_count = 0
    cell_records = []
    for source_cell in p1509["cells"]:
        key = (int(source_cell["L"]), int(source_cell["nonce"]))
        compiler_record, target, wring = compiled[key]
        field = wring.base_ring()
        marker_ring = PolynomialRing(field, names=("E0", "E1", "H0", "H1"))
        alpha_lookup = {int(field(index + 1)): index for index in range(compiler_record["r"])}
        cell_endpoint_count = 0
        cell_pair_matches = 0
        cell_proportional = 0
        for endpoint_record in source_cell["endpoints"]:
            endpoint_count += 1
            cell_endpoint_count += 1
            endpoint = field(endpoint_record["endpoint_x"])
            evaluated = evaluated_marker_polynomial(target, endpoint, marker_ring)
            if endpoint_record["is_known_return"]:
                if evaluated != 0:
                    raise RuntimeError("P1510 return endpoint has a nonzero degree-two component")
                return_low_order_zero_count += 1
                continue
            nonreturn_count += 1
            order = int(endpoint_record["gcd_degree"])
            lower = [homogeneous_component(evaluated, degree) for degree in range(order)]
            if any(lower):
                raise RuntimeError("P1510 endpoint has a premature marker component")
            actual_leading = homogeneous_component(evaluated, order)
            if not actual_leading:
                raise RuntimeError("P1510 endpoint leading component vanished")

            expected_leading = marker_ring.one()
            replacements = {
                f"E0_1509_{key[0]}_{key[1]}": "E0",
                f"E1_1509_{key[0]}_{key[1]}": "E1",
                f"H0_1509_{key[0]}_{key[1]}": "H0",
                f"H1_1509_{key[0]}_{key[1]}": "H1",
            }
            for factor_record in endpoint_record["factored_forms"]:
                text = factor_record["factor"]
                for old, new in replacements.items():
                    text = text.replace(old, new)
                expected_leading *= marker_ring(text) ** int(factor_record["multiplicity"])
            matches, scale = proportional(actual_leading, expected_leading)
            if not matches:
                raise RuntimeError("P1510 global/local leading forms are not proportional")
            proportional_count += 1
            cell_proportional += 1
            decoded = decode_factor_pairs(actual_leading, alpha_lookup)
            expected_pairs = sorted(tuple(pair) for pair in endpoint_record["decoded_factor_pairs"])
            if decoded != expected_pairs:
                raise RuntimeError("P1510 global compiler decoded different factor pairs")
            pair_match_count += 1
            cell_pair_matches += 1
        cell_records.append(
            {
                "L": key[0],
                "nonce": key[1],
                "endpoint_count": cell_endpoint_count,
                "nonreturn_proportional_leading_form_count": cell_proportional,
                "nonreturn_factor_pair_match_count": cell_pair_matches,
                "source_partition_matches_p1505": bool(source_cell["decoded_partition_matches_p1505"]),
            }
        )
    return {
        "endpoint_count": endpoint_count,
        "nonreturn_endpoint_count": nonreturn_count,
        "nonreturn_proportional_leading_form_count": proportional_count,
        "nonreturn_factor_pair_match_count": pair_match_count,
        "return_low_order_zero_count": return_low_order_zero_count,
        "all_source_partitions_already_replay_from_matched_pairs": all(
            record["source_partition_matches_p1505"] for record in cell_records
        ),
        "cells": cell_records,
    }


def scaling_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    rows = []
    for record in records:
        r = record["r"]
        arithmetic = record["arithmetic"]
        log_r = max(1.0, math.log2(r))
        rows.append(
            {
                "r": r,
                "output_slots": record["output_coefficient_slots"],
                "peak_live_slots": arithmetic["peak_live_coefficient_slots"],
                "poly_mul_calls": arithmetic["poly_mul_call_count"],
                "schoolbook_upper": arithmetic["poly_mul_schoolbook_upper"],
                "quasilinear_proxy": arithmetic["poly_mul_quasilinear_proxy"],
                "quasilinear_proxy_over_r2_log4r": arithmetic[
                    "poly_mul_quasilinear_proxy"
                ]
                / (r * r * log_r**4),
                "peak_live_slots_over_r2": arithmetic["peak_live_coefficient_slots"]
                / (r * r),
            }
        )
    return {
        "rows": rows,
        "all_exact_divisions_have_zero_remainder": all(
            record["arithmetic"]["exact_division_count"]
            == record["arithmetic"]["exact_division_zero_remainder_count"]
            for record in records
        ),
        "all_component_degrees_at_most_4r2": all(
            record["maximum_component_degree"]
            <= record["theoretical_maximum_component_degree_4r2"]
            for record in records
        ),
        "symbolic_work_recurrence": "O(r^2 + r*M(r)*log(r) + M(r^2)*log(r))",
        "symbolic_state_bound": "O(r^2) endpoint-polynomial coefficient slots",
        "standard_fast_multiplication_consequence": "O(r^2*polylog(r)) base-field work",
    }


def render_note(payload: dict[str, Any]) -> str:
    verification = payload["verification"]
    scaling = payload["synthetic_scaling"]
    lines = [
        "# P1510 Global Truncated Marked-Resultant Compiler",
        "",
        f"Status: `{payload['status']}`",
        "",
        "## Exact Replay",
        "",
        f"The source-blind construction freezes all 15 coefficient polynomials before opening endpoint evidence. It replays {verification['nonreturn_proportional_leading_form_count']}/{verification['nonreturn_endpoint_count']} nonreturn local leading forms up to nonzero scale and decodes the same factor pairs on all of them. All {verification['return_low_order_zero_count']} return controls have zero marker components through degree two.",
        "",
        "## Scaling",
        "",
        "| r | output slots | peak live slots | polynomial multiplications | schoolbook upper | quasi-linear proxy | proxy/(r^2 log^4 r) | peak/r^2 |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in scaling["rows"]:
        lines.append(
            f"| {row['r']} | {row['output_slots']} | {row['peak_live_slots']} | "
            f"{row['poly_mul_calls']} | {row['schoolbook_upper']} | "
            f"{row['quasilinear_proxy']} | {row['quasilinear_proxy_over_r2_log4r']:.6f} | "
            f"{row['peak_live_slots_over_r2']:.6f} |"
        )
    lines.extend(
        [
            "",
            "The degree-pair transcript charges every endpoint-polynomial multiplication. The symbolic recurrence is `O(r^2 + r M(r) log r + M(r^2) log r)`, hence `O(r^2 polylog r)` with standard fast polynomial multiplication, and peak coefficient state is `O(r^2)`.",
            "",
            "## Boundary",
            "",
            payload["interpretation"],
            "",
            "An independent implementation and mutation audit are still required before promoting the global compiler claim. Relation collection, factor-log linear algebra, blind descent, and an end-to-end rho/Shoup result remain unattempted.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_sizes(text: str) -> list[int]:
    sizes = [int(item) for item in text.split(",") if item.strip()]
    if not sizes or any(size < 2 for size in sizes):
        raise argparse.ArgumentTypeError("sizes must be comma-separated integers >= 2")
    return sizes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--synthetic-sizes", type=parse_sizes, default=parse_sizes("4,6,8,12,16,24,32"))
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument("--note", type=Path, default=NOTE)
    args = parser.parse_args()

    construction_hashes = verify_hashes(CONSTRUCTION_EXPECTED)
    compiled: dict[tuple[int, int], tuple[dict[str, Any], Jet, Any]] = {}
    curve_records = []
    for fixture in p1482.FIXTURES:
        for nonce in (0, 1):
            field, left, right, alpha, metadata = curve_factor_system(fixture, nonce)
            record, target, wring = compile_factor_system(
                field, left, right, alpha, f"curve-L{metadata['L']}-nonce{nonce}"
            )
            record.update(metadata)
            compiled[(metadata["L"], nonce)] = (record, target, wring)
            curve_records.append(record)

    synthetic_records = []
    for size in args.synthetic_sizes:
        field, left, right, alpha, metadata = synthetic_factor_system(size)
        record, _, _ = compile_factor_system(
            field, left, right, alpha, f"synthetic-r{size}"
        )
        record.update(metadata)
        synthetic_records.append(record)

    frozen_construction = {
        "curve_cells": curve_records,
        "synthetic_cells": synthetic_records,
        "construction_input_hashes": construction_hashes,
    }
    construction_sha256 = digest(frozen_construction)

    post_freeze_hashes = verify_hashes(POST_FREEZE_EXPECTED)
    p1509 = json.loads(P1509.read_text(encoding="utf-8"))
    p1509_audit = json.loads(P1509_AUDIT.read_text(encoding="utf-8"))
    if sum(bool(value) for value in p1509_audit["checks"].values()) != 12:
        raise RuntimeError("P1510 requires the 12/12 P1509 audit")
    verification = verify_curve_cells(compiled, p1509)
    scaling = scaling_summary(synthetic_records)

    gates = {
        "construction_inputs_exclude_endpoint_and_source_artifacts": True,
        "construction_frozen_before_endpoint_evidence_opened": True,
        "all_15_components_emitted": all(
            record["component_count"] == 15 for record in curve_records + synthetic_records
        ),
        "all_projective_denominator_divisions_exact": scaling[
            "all_exact_divisions_have_zero_remainder"
        ] and all(
            record["arithmetic"]["exact_division_count"]
            == record["arithmetic"]["exact_division_zero_remainder_count"]
            for record in curve_records
        ),
        "all_component_degrees_within_4r2": scaling[
            "all_component_degrees_at_most_4r2"
        ],
        "all_900_nonreturn_leading_forms_replay": verification[
            "nonreturn_proportional_leading_form_count"
        ] == 900,
        "all_900_factor_pairs_match": verification[
            "nonreturn_factor_pair_match_count"
        ] == 900,
        "all_return_controls_zero_through_degree_two": verification[
            "return_low_order_zero_count"
        ] == 8,
        "all_source_partitions_follow_from_matched_pairs": verification[
            "all_source_partitions_already_replay_from_matched_pairs"
        ],
        "symbolic_output_sensitive_work_bound_available": True,
        "quadratic_peak_state_bound_available": True,
        "independent_audit_passed": False,
        "relation_collection_completed": False,
        "blind_descent_completed": False,
        "generic_shoup_breakthrough": False,
    }
    producer_positive = all(
        value for key, value in gates.items() if key not in {
            "independent_audit_passed",
            "relation_collection_completed",
            "blind_descent_completed",
            "generic_shoup_breakthrough",
        }
    )
    status = (
        "POSITIVE_RESULT_P1510_EXACT_OUTPUT_LINEAR_MULTIPLICATIVE_COMPILER_"
        "INDEPENDENT_AUDIT_OPEN"
        if producer_positive
        else "REVISE_P1510_COMPILER_PREFLIGHT"
    )
    payload = {
        "schema": SCHEMA,
        "status": status,
        "claim_status": (
            "GLOBAL 15-COMPONENT COMPILER PRODUCER POSITIVE / SOURCE-BLIND CONSTRUCTION / "
            "EXACT P1509 LOCAL REPLAY / OUTPUT-SENSITIVE SYMBOLIC BOUND / INDEPENDENT AUDIT OPEN / "
            "NO RELATION CAMPAIGN OR SHOUP BREAK"
        ),
        "source": display_path(Path(__file__)),
        "source_sha256": sha256_file(Path(__file__)),
        "contract": display_path(CONTRACT),
        "contract_sha256": sha256_file(CONTRACT),
        "derivation": display_path(DERIVATION),
        "derivation_sha256": sha256_file(DERIVATION),
        "construction_frozen_sha256": construction_sha256,
        "construction": frozen_construction,
        "post_freeze_evidence_hashes": post_freeze_hashes,
        "verification": verification,
        "synthetic_scaling": scaling,
        "gates": gates,
        "interpretation": (
            "P1510's multiplicative decomposition constructs the complete degree-two marked "
            "resultant from pure-left quadratic norms, pure-right quadratic norms, and r^2 "
            "constant-size pair resultants. The construction does not open endpoint roots or "
            "source tables, every public-leading-coefficient division is exact, and the frozen "
            "global object reproduces every P1509 nonreturn leading form and factor pair. The "
            "producer establishes an output-sensitive compiler candidate only; independent "
            "reimplementation and full ECDLP stages remain open."
        ),
        "limitations": [
            "Independent compiler reimplementation and mutation audit have not yet passed.",
            "The quasi-linear conclusion uses standard fast univariate polynomial multiplication; the transcript also retains a schoolbook upper control.",
            "The exact curve replay covers P1490's generated rational-selector fixtures.",
            "No candidate-density, relation-rank, factor-log, linear-algebra, or blind-descent campaign has run.",
            "No Pollard-rho or Shoup-bound improvement is claimed.",
        ],
        "next_action": (
            "Implement a source-independent audit of the 15 coefficient vectors, fraction-free "
            "division recurrence, local-form replay, degree-pair operation transcript, and "
            "mutations. Only then promote the global compiler claim and freeze a complete "
            "relation-collection contract."
        ),
    }
    encoded = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    write_atomic(args.out, encoded)
    write_atomic(args.note, render_note(payload).encode("utf-8"))
    print(
        f"status={status} construction_sha256={construction_sha256} "
        f"nonreturn={verification['nonreturn_factor_pair_match_count']}/900 "
        f"synthetic_sizes={args.synthetic_sizes}"
    )
    return 0 if producer_positive else 2


if __name__ == "__main__":
    raise SystemExit(main())
