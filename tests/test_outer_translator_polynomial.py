from __future__ import annotations

import importlib.util
import json
import random
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ENGINE_PATH = (
    REPO_ROOT
    / "experiments"
    / "EXP-ECDLP-OUTER-TRANSLATOR-001"
    / "src"
    / "polynomial_engine.py"
)
SPEC = importlib.util.spec_from_file_location(
    "outer_translator_polynomial_engine",
    ENGINE_PATH,
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load polynomial engine: {ENGINE_PATH}")
ENGINE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = ENGINE
SPEC.loader.exec_module(ENGINE)

try:
    import sympy  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - exercised on dependency-free hosts
    sympy = None


def sparse_value(polynomial: object, values: tuple[int, ...]) -> int:
    if len(values) != polynomial.nvars:
        raise ValueError("evaluation dimension mismatch")
    total = 0
    for monomial, coefficient in polynomial.terms.items():
        term = coefficient
        for value, exponent in zip(values, monomial):
            term = term * pow(value, exponent, polynomial.p) % polynomial.p
        total = (total + term) % polynomial.p
    return total


def scalar_f3(x1: int, x2: int, x3: int, a: int, b: int, p: int) -> int:
    return (
        (x1 - x2) ** 2 * x3**2
        - 2 * ((x1 + x2) * (x1 * x2 + a) + 2 * b) * x3
        + (x1 * x2 - a) ** 2
        - 4 * b * (x1 + x2)
    ) % p


def scalar_f3_coefficients(
    x1: int,
    x2: int,
    a: int,
    b: int,
    p: int,
) -> tuple[int, int, int]:
    return (
        (x1 - x2) ** 2 % p,
        (-2 * ((x1 + x2) * (x1 * x2 + a) + 2 * b)) % p,
        ((x1 * x2 - a) ** 2 - 4 * b * (x1 + x2)) % p,
    )


def scalar_quadratic_resultant(
    left: tuple[int, int, int],
    right: tuple[int, int, int],
    p: int,
) -> int:
    a2, a1, a0 = left
    b2, b1, b0 = right
    return (
        (a2 * b0 - a0 * b2) ** 2
        - (a2 * b1 - a1 * b2) * (a1 * b0 - a0 * b1)
    ) % p


class OperationCounterTests(unittest.TestCase):
    def test_counter_counts_executed_field_operations_and_serializes(self) -> None:
        counter = ENGINE.OperationCounter()
        self.assertEqual(ENGINE.fp_add(6, 4, 7, counter), 3)
        self.assertEqual(ENGINE.fp_multiply(5, 3, 7, counter), 1)
        self.assertEqual(ENGINE.fp_inverse(3, 7, counter), 5)
        self.assertTrue(ENGINE.fp_is_zero(14, 7, counter))
        self.assertEqual(
            counter.to_record(),
            {
                "schema": "fp-polynomial-operations-v1",
                "coefficient_additions": 1,
                "coefficient_multiplications": 1,
                "coefficient_inversions": 1,
                "coefficient_zero_tests": 2,
            },
        )
        json.dumps(counter.to_record(), sort_keys=True, allow_nan=False)

        snapshot = counter.copy()
        ENGINE.fp_subtract(1, 2, 7, counter)
        self.assertEqual(
            counter.delta_from(snapshot).to_record()["coefficient_additions"],
            1,
        )

    def test_runtime_source_has_no_sympy_dependency(self) -> None:
        source = ENGINE_PATH.read_text(encoding="utf-8")
        self.assertNotIn("import sympy", source)
        self.assertNotIn("from sympy", source)


class SparsePolynomialTests(unittest.TestCase):
    def test_canonical_add_subtract_multiply_power_scale_and_evaluate(self) -> None:
        p = 7
        x_plus_2y = ENGINE.SparsePolynomial(
            p,
            2,
            {(1, 0): 1, (0, 1): 2, (0, 0): p},
        )
        x_minus_2y = ENGINE.SparsePolynomial(
            p,
            2,
            {(1, 0): 1, (0, 1): -2},
        )
        self.assertNotIn((0, 0), x_plus_2y.terms)

        summed = x_plus_2y.add(x_minus_2y)
        self.assertEqual(summed.terms, {(1, 0): 2})
        self.assertEqual(summed.subtract(x_minus_2y), x_plus_2y)

        product = x_plus_2y.multiply(x_minus_2y)
        squared = x_plus_2y.power(2)
        scaled = squared.scale(3)
        for x_value in range(p):
            for y_value in range(p):
                left = (x_value + 2 * y_value) % p
                right = (x_value - 2 * y_value) % p
                self.assertEqual(sparse_value(product, (x_value, y_value)), left * right % p)
                self.assertEqual(sparse_value(squared, (x_value, y_value)), left**2 % p)
                self.assertEqual(sparse_value(scaled, (x_value, y_value)), 3 * left**2 % p)

        at_x_3 = squared.evaluate_one_variable(0, 3)
        self.assertEqual(at_x_3.nvars, 1)
        for y_value in range(p):
            self.assertEqual(
                sparse_value(at_x_3, (y_value,)),
                sparse_value(squared, (3, y_value)),
            )

    def test_dimension_and_modulus_mismatches_are_rejected(self) -> None:
        left = ENGINE.SparsePolynomial.variable(7, 2, 0)
        wrong_dimension = ENGINE.SparsePolynomial.variable(7, 1, 0)
        wrong_modulus = ENGINE.SparsePolynomial.variable(11, 2, 0)
        with self.assertRaises(ValueError):
            left.add(wrong_dimension)
        with self.assertRaises(ValueError):
            left.multiply(wrong_modulus)
        with self.assertRaises(ValueError):
            ENGINE.SparsePolynomial(7, 2, {(1,): 1})
        with self.assertRaises(IndexError):
            left.evaluate_one_variable(2, 1)
        with self.assertRaises(ValueError):
            ENGINE.SparsePolynomial(15, 1, {(0,): 1})


class UnivariatePolynomialTests(unittest.TestCase):
    def test_seeded_small_prime_division_and_evaluation_identities(self) -> None:
        rng = random.Random(0xD2F4C3)
        for p in (5, 7, 11, 13, 17):
            for trial in range(20):
                numerator = tuple(rng.randrange(p) for _ in range(rng.randrange(1, 7)))
                divisor = [rng.randrange(p) for _ in range(rng.randrange(1, 5))]
                divisor[-1] = rng.randrange(1, p)
                quotient, remainder = ENGINE.univariate_divmod(numerator, divisor, p)
                rebuilt = ENGINE.univariate_add(
                    ENGINE.univariate_multiply(quotient, divisor, p),
                    remainder,
                    p,
                )
                self.assertEqual(rebuilt, ENGINE.univariate_trim(numerator, p))
                if remainder != (0,):
                    self.assertLess(len(remainder), len(ENGINE.univariate_trim(divisor, p)))
                for value in (0, 1, rng.randrange(p)):
                    expected = sum(
                        coefficient * pow(value, degree, p)
                        for degree, coefficient in enumerate(numerator)
                    ) % p
                    self.assertEqual(
                        ENGINE.univariate_evaluate(numerator, value, p),
                        expected,
                        msg=f"p={p} trial={trial}",
                    )

    def test_product_gcd_and_disclosed_root_extraction(self) -> None:
        rng = random.Random(0x600DCAFE)
        for p in (7, 11, 17, 19):
            roots = tuple(rng.sample(range(p), 4))
            selected = roots[::2]
            m2 = ENGINE.univariate_product_from_roots(roots, p)
            selected_polynomial = ENGINE.univariate_product_from_roots(selected, p)
            common = ENGINE.univariate_gcd(m2, selected_polynomial, p)
            self.assertEqual(common, selected_polynomial)
            self.assertEqual(
                ENGINE.univariate_roots_from_disclosed(common, roots, p),
                selected,
            )
            for root in roots:
                self.assertEqual(ENGINE.univariate_evaluate(m2, root, p), 0)
            with self.assertRaises(ValueError):
                ENGINE.univariate_roots_from_disclosed(common, (roots[0], roots[0] + p), p)


class SemaevConstructionTests(unittest.TestCase):
    def test_f3_and_f4_match_independent_scalar_identities(self) -> None:
        rng = random.Random(0xF3F4001)
        for p in (5, 7, 11, 17):
            a = rng.randrange(p)
            b = rng.randrange(p)
            x_q = rng.randrange(p)
            f3 = ENGINE.semaev_f3(p, a, b)
            f4_fixed = ENGINE.semaev_f4_fixed_x(p, a, b, x_q)
            self.assertTrue(all(degree <= 2 for degree in f3.degrees()))
            self.assertTrue(all(degree <= 4 for degree in f4_fixed.degrees()))
            for _ in range(12):
                u, v, w = (rng.randrange(p) for _ in range(3))
                self.assertEqual(
                    sparse_value(f3, (u, v, w)),
                    scalar_f3(u, v, w, a, b, p),
                )
                expected_f4 = scalar_quadratic_resultant(
                    scalar_f3_coefficients(u, v, a, b, p),
                    scalar_f3_coefficients(w, x_q, a, b, p),
                    p,
                )
                self.assertEqual(sparse_value(f4_fixed, (u, v, w)), expected_f4)

    def test_generic_f4_specializes_exactly_and_has_coordinate_degree_four(self) -> None:
        p, a, b, x_q = 17, 2, 3, 9
        generic = ENGINE.semaev_f4(p, a, b)
        fixed = ENGINE.semaev_f4_fixed_x(p, a, b, x_q)
        self.assertTrue(all(degree <= 4 for degree in generic.degrees()))
        self.assertEqual(generic.evaluate_one_variable(3, x_q), fixed)

    @unittest.skipIf(sympy is None, "SymPy is an optional development oracle")
    def test_optional_sympy_resultant_oracle(self) -> None:
        p, a, b = 101, 2, 3
        u, v, w, x, z = sympy.symbols("u v w x z")

        def symbolic_f3(first: object, second: object, third: object) -> object:
            return (
                (first - second) ** 2 * third**2
                - 2 * ((first + second) * (first * second + a) + 2 * b) * third
                + (first * second - a) ** 2
                - 4 * b * (first + second)
            )

        oracle = sympy.Poly(
            sympy.resultant(symbolic_f3(u, v, z), symbolic_f3(w, x, z), z),
            u,
            v,
            w,
            x,
            modulus=p,
        )
        oracle_terms = {
            tuple(monomial): int(coefficient) % p
            for monomial, coefficient in oracle.terms()
            if int(coefficient) % p
        }
        self.assertEqual(dict(ENGINE.semaev_f4(p, a, b).terms), oracle_terms)


class SourceSubstitutionTests(unittest.TestCase):
    def test_all_source_maps_match_direct_products_up_to_exact_scalar(self) -> None:
        rng = random.Random(0x5012CE)
        branch_parameters = (
            ("identity", {}),
            ("square", {"c": 4}),
            ("mobius", {"d": 5, "e": 3}),
        )
        for p in (7, 11, 17, 19):
            a, b, x_q = (rng.randrange(p) for _ in range(3))
            f4_fixed = ENGINE.semaev_f4_fixed_x(p, a, b, x_q)
            roots = tuple(
                value
                for value in range(p)
                if value != (-3) % p
            )[: min(3, p - 1)]
            for kind, parameters in branch_parameters:
                with self.subTest(p=p, kind=kind):
                    substituted = ENGINE.substitute_source_map(
                        f4_fixed,
                        kind,
                        **parameters,
                    )
                    expected_t_degree = 8 if kind == "square" else 4
                    self.assertLessEqual(substituted.degree(0), expected_t_degree)
                    self.assertLessEqual(substituted.degree(1), 4)
                    self.assertLessEqual(substituted.degree(2), 4)

                    source_product = ENGINE.source_root_elimination(substituted, roots)
                    mapped_roots = ENGINE.source_map_values(
                        p,
                        kind,
                        roots,
                        **parameters,
                    )
                    direct_product = ENGINE.direct_factor_root_product(
                        f4_fixed,
                        mapped_roots,
                    )
                    scalar = ENGINE.source_denominator_scalar(
                        p,
                        kind,
                        roots,
                        **parameters,
                    )
                    self.assertNotEqual(scalar, 0)
                    self.assertEqual(source_product, direct_product.scale(scalar))
                    self.assertTrue(
                        ENGINE.sparse_equal_up_to_scalar(
                            source_product,
                            direct_product,
                        )
                    )
                    self.assertEqual(
                        ENGINE.normalize_sparse(source_product),
                        ENGINE.normalize_sparse(direct_product),
                    )
                    if not direct_product.is_zero():
                        self.assertEqual(
                            ENGINE.sparse_scalar_ratio(source_product, direct_product),
                            scalar,
                        )

    def test_mobius_source_pole_is_rejected(self) -> None:
        p = 11
        f4_fixed = ENGINE.semaev_f4_fixed_x(p, 2, 3, 4)
        pole = (-5) % p
        with self.assertRaises(ZeroDivisionError):
            ENGINE.source_map_value(p, "mobius", pole, d=2, e=5)
        with self.assertRaises(ZeroDivisionError):
            ENGINE.source_denominator_scalar(
                p,
                "mobius",
                (1, pole),
                d=2,
                e=5,
            )
        substituted = ENGINE.substitute_mobius_source(f4_fixed, d=2, e=5)
        self.assertLessEqual(substituted.degree(0), 4)


class RootProductControlTests(unittest.TestCase):
    def test_d2_root_product_modulus_and_gcd_have_exact_disclosed_roots(self) -> None:
        p = 11
        roots = (1, 2, 9)
        # G(V,W)=V+W, so a disclosed V root is compatible exactly when -V is
        # another disclosed W root.
        polynomial_vw = ENGINE.SparsePolynomial(
            p,
            2,
            {(1, 0): 1, (0, 1): 1},
        )
        m2 = ENGINE.build_m2(roots, p)
        remainder = ENGINE.s4_root_product_mod_m2(
            polynomial_vw,
            roots,
            m2=m2,
        )
        common, extracted = ENGINE.gcd_roots_against_m2(
            remainder,
            m2,
            roots,
            p,
        )
        expected = tuple(
            value for value in roots if any((value + other) % p == 0 for other in roots)
        )
        self.assertEqual(extracted, expected)
        for value in roots:
            direct = 1
            for other in roots:
                direct = direct * (value + other) % p
            self.assertEqual(ENGINE.univariate_evaluate(remainder, value, p), direct)

    def test_s3_positive_control_matches_direct_seeded_enumeration(self) -> None:
        rng = random.Random(0x53C0DE)
        for p in (7, 11, 13, 17):
            a, b, x_q = (rng.randrange(p) for _ in range(3))
            roots = tuple(rng.sample(range(p), min(5, p)))
            counter = ENGINE.OperationCounter()
            result = ENGINE.s3_positive_control(p, a, b, x_q, roots, counter)
            expected = tuple(
                v
                for v in roots
                if v == x_q % p
                or any(scalar_f3(v, w, x_q, a, b, p) == 0 for w in roots)
            )
            self.assertEqual(result.compatible_roots, expected)
            self.assertEqual(
                ENGINE.univariate_roots_from_disclosed(result.gcd, roots, p),
                expected,
            )
            self.assertEqual(
                ENGINE.s3_identity_corrected_root_product_mod_m2(
                    result.relation_polynomial,
                    x_q,
                    roots,
                    m2=result.m2,
                ),
                result.root_product_remainder,
            )
            json.dumps(result.to_record(), sort_keys=True, allow_nan=False)
            operation_record = counter.to_record()
            self.assertGreater(operation_record["coefficient_additions"], 0)
            self.assertGreater(operation_record["coefficient_multiplications"], 0)
            self.assertGreater(operation_record["coefficient_inversions"], 0)
            self.assertGreater(operation_record["coefficient_zero_tests"], 0)

    def test_s3_identity_factor_adds_target_x_without_finite_partner(self) -> None:
        p = 11
        a = 1
        b = 6
        x_q = 3
        roots = (x_q,)
        relation = ENGINE.semaev_f3_fixed_x(p, a, b, x_q)
        m2 = ENGINE.build_m2(roots, p)
        finite = ENGINE.s3_root_product_mod_m2(relation, roots, m2=m2)
        _, finite_roots = ENGINE.gcd_roots_against_m2(
            finite, m2, roots, p
        )
        corrected = ENGINE.s3_identity_corrected_root_product_mod_m2(
            relation, x_q, roots, m2=m2
        )
        _, corrected_roots = ENGINE.gcd_roots_against_m2(
            corrected, m2, roots, p
        )
        self.assertEqual(finite_roots, ())
        self.assertEqual(corrected_roots, roots)


if __name__ == "__main__":
    unittest.main()
