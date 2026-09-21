#!/usr/bin/env python3
"""Exact dependency-free polynomial arithmetic for the outer translator.

Multivariate polynomials use canonical sparse dictionaries whose monomials are
tuples of non-negative exponents.  Univariate polynomials use canonical dense
tuples in ascending coefficient order.  All coefficients live in ``F_p``.

The optional :class:`OperationCounter` counts coefficient operations actually
executed by this implementation.  Integer bookkeeping, exponent comparisons,
dictionary probes, and monomial-index arithmetic are deliberately not field
operations.
"""
from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from functools import lru_cache
from types import MappingProxyType
from typing import Any


Monomial = tuple[int, ...]
UniPolynomial = tuple[int, ...]
F4_DENOMINATOR_POWER = 4
OPERATION_RECORD_SCHEMA = "fp-polynomial-operations-v1"


def _exact_int(value: Any, label: str, minimum: int | None = None) -> int:
    if type(value) is not int:
        raise TypeError(f"{label} must be an exact integer")
    if minimum is not None and value < minimum:
        raise ValueError(f"{label} must be at least {minimum}")
    return value


@lru_cache(maxsize=None)
def _is_prime(value: int) -> bool:
    if value < 2:
        return False
    if value in (2, 3):
        return True
    if value % 2 == 0:
        return False
    divisor = 3
    while divisor * divisor <= value:
        if value % divisor == 0:
            return False
        divisor += 2
    return True


def _validate_modulus(p: int) -> int:
    _exact_int(p, "p", 2)
    if not _is_prime(p):
        raise ValueError("p must be prime")
    return p


@dataclass
class OperationCounter:
    """Executed finite-field coefficient operations.

    Subtractions and negations count as coefficient additions.  Calls to
    :func:`fp_inverse` count both the explicit zero test and the inversion.
    ``to_record`` contains only JSON-native scalar values.
    """

    coefficient_additions: int = 0
    coefficient_multiplications: int = 0
    coefficient_inversions: int = 0
    coefficient_zero_tests: int = 0

    def __post_init__(self) -> None:
        for name in (
            "coefficient_additions",
            "coefficient_multiplications",
            "coefficient_inversions",
            "coefficient_zero_tests",
        ):
            _exact_int(getattr(self, name), name, 0)

    def copy(self) -> OperationCounter:
        return OperationCounter(
            self.coefficient_additions,
            self.coefficient_multiplications,
            self.coefficient_inversions,
            self.coefficient_zero_tests,
        )

    def delta_from(self, earlier: OperationCounter) -> OperationCounter:
        if not isinstance(earlier, OperationCounter):
            raise TypeError("earlier must be an OperationCounter")
        values = (
            self.coefficient_additions - earlier.coefficient_additions,
            self.coefficient_multiplications
            - earlier.coefficient_multiplications,
            self.coefficient_inversions - earlier.coefficient_inversions,
            self.coefficient_zero_tests - earlier.coefficient_zero_tests,
        )
        if any(value < 0 for value in values):
            raise ValueError("earlier counter is not a snapshot of this counter")
        return OperationCounter(*values)

    def add(self, other: OperationCounter) -> None:
        if not isinstance(other, OperationCounter):
            raise TypeError("other must be an OperationCounter")
        self.coefficient_additions += other.coefficient_additions
        self.coefficient_multiplications += other.coefficient_multiplications
        self.coefficient_inversions += other.coefficient_inversions
        self.coefficient_zero_tests += other.coefficient_zero_tests

    def reset(self) -> None:
        self.coefficient_additions = 0
        self.coefficient_multiplications = 0
        self.coefficient_inversions = 0
        self.coefficient_zero_tests = 0

    def to_record(self) -> dict[str, int | str]:
        return {
            "schema": OPERATION_RECORD_SCHEMA,
            "coefficient_additions": self.coefficient_additions,
            "coefficient_multiplications": self.coefficient_multiplications,
            "coefficient_inversions": self.coefficient_inversions,
            "coefficient_zero_tests": self.coefficient_zero_tests,
        }


def _validate_counter(counter: OperationCounter | None) -> None:
    if counter is not None and not isinstance(counter, OperationCounter):
        raise TypeError("counter must be an OperationCounter or None")


def fp_add(
    left: int,
    right: int,
    p: int,
    counter: OperationCounter | None = None,
) -> int:
    _validate_modulus(p)
    _validate_counter(counter)
    _exact_int(left, "left")
    _exact_int(right, "right")
    if counter is not None:
        counter.coefficient_additions += 1
    return (left + right) % p


def fp_subtract(
    left: int,
    right: int,
    p: int,
    counter: OperationCounter | None = None,
) -> int:
    _validate_modulus(p)
    _validate_counter(counter)
    _exact_int(left, "left")
    _exact_int(right, "right")
    if counter is not None:
        counter.coefficient_additions += 1
    return (left - right) % p


def fp_multiply(
    left: int,
    right: int,
    p: int,
    counter: OperationCounter | None = None,
) -> int:
    _validate_modulus(p)
    _validate_counter(counter)
    _exact_int(left, "left")
    _exact_int(right, "right")
    if counter is not None:
        counter.coefficient_multiplications += 1
    return (left * right) % p


def fp_is_zero(
    value: int,
    p: int,
    counter: OperationCounter | None = None,
) -> bool:
    _validate_modulus(p)
    _validate_counter(counter)
    _exact_int(value, "value")
    if counter is not None:
        counter.coefficient_zero_tests += 1
    return value % p == 0


def fp_inverse(
    value: int,
    p: int,
    counter: OperationCounter | None = None,
) -> int:
    _validate_modulus(p)
    _validate_counter(counter)
    _exact_int(value, "value")
    reduced = value % p
    if fp_is_zero(reduced, p, counter):
        raise ZeroDivisionError("zero has no inverse in F_p")
    if counter is not None:
        counter.coefficient_inversions += 1
    return pow(reduced, -1, p)


def fp_power(
    value: int,
    exponent: int,
    p: int,
    counter: OperationCounter | None = None,
) -> int:
    _validate_modulus(p)
    _exact_int(value, "value")
    _exact_int(exponent, "exponent", 0)
    result = 1
    base = value % p
    remaining = exponent
    while remaining:
        if remaining & 1:
            result = fp_multiply(result, base, p, counter)
        remaining >>= 1
        if remaining:
            base = fp_multiply(base, base, p, counter)
    return result


class SparsePolynomial:
    """Canonical sparse multivariate polynomial over ``F_p``."""

    __slots__ = ("p", "nvars", "_terms")

    def __init__(
        self,
        p: int,
        nvars: int,
        terms: Mapping[Sequence[int], int] | None = None,
        *,
        counter: OperationCounter | None = None,
    ) -> None:
        self.p = _validate_modulus(p)
        self.nvars = _exact_int(nvars, "nvars", 0)
        _validate_counter(counter)
        if terms is None:
            terms = {}
        if not isinstance(terms, Mapping):
            raise TypeError("terms must be a mapping from monomials to coefficients")
        canonical: dict[Monomial, int] = {}
        for raw_monomial, raw_coefficient in terms.items():
            monomial = tuple(raw_monomial)
            if len(monomial) != self.nvars:
                raise ValueError(
                    f"monomial dimension {len(monomial)} does not match {self.nvars}"
                )
            for index, exponent in enumerate(monomial):
                _exact_int(exponent, f"monomial[{index}]", 0)
            _exact_int(raw_coefficient, "coefficient")
            coefficient = raw_coefficient % self.p
            if not fp_is_zero(coefficient, self.p, counter):
                canonical[monomial] = coefficient
        self._terms = canonical

    @classmethod
    def _from_canonical(
        cls,
        p: int,
        nvars: int,
        terms: Mapping[Monomial, int],
    ) -> SparsePolynomial:
        result = object.__new__(cls)
        result.p = p
        result.nvars = nvars
        result._terms = dict(terms)
        return result

    @classmethod
    def zero(cls, p: int, nvars: int) -> SparsePolynomial:
        return cls(p, nvars)

    @classmethod
    def constant(
        cls,
        p: int,
        nvars: int,
        value: int,
        *,
        counter: OperationCounter | None = None,
    ) -> SparsePolynomial:
        return cls(p, nvars, {(0,) * nvars: value}, counter=counter)

    @classmethod
    def variable(
        cls,
        p: int,
        nvars: int,
        variable: int,
        *,
        counter: OperationCounter | None = None,
    ) -> SparsePolynomial:
        _exact_int(variable, "variable", 0)
        if variable >= nvars:
            raise IndexError("variable index is outside the polynomial dimension")
        monomial = [0] * nvars
        monomial[variable] = 1
        return cls(p, nvars, {tuple(monomial): 1}, counter=counter)

    @property
    def terms(self) -> Mapping[Monomial, int]:
        return MappingProxyType(self._terms)

    def sorted_terms(self) -> tuple[tuple[Monomial, int], ...]:
        return tuple(sorted(self._terms.items()))

    def coefficient(self, monomial: Sequence[int]) -> int:
        key = tuple(monomial)
        if len(key) != self.nvars:
            raise ValueError("monomial dimension mismatch")
        return self._terms.get(key, 0)

    def is_zero(self) -> bool:
        return not self._terms

    def is_one(self) -> bool:
        return self._terms == {(0,) * self.nvars: 1}

    def term_count(self) -> int:
        return len(self._terms)

    def degree(self, variable: int | None = None) -> int:
        if not self._terms:
            return -1
        if variable is None:
            return max(sum(monomial) for monomial in self._terms)
        _exact_int(variable, "variable", 0)
        if variable >= self.nvars:
            raise IndexError("variable index is outside the polynomial dimension")
        return max(monomial[variable] for monomial in self._terms)

    def degrees(self) -> tuple[int, ...]:
        return tuple(self.degree(variable) for variable in range(self.nvars))

    def dense_coefficient_count(self) -> int:
        if not self._terms:
            return 0
        count = 1
        for degree in self.degrees():
            count *= degree + 1
        return count

    def density(self) -> float:
        dense = self.dense_coefficient_count()
        return 0.0 if dense == 0 else len(self._terms) / dense

    def to_record(self) -> dict[str, Any]:
        return {
            "p": self.p,
            "nvars": self.nvars,
            "terms": [
                {"exponents": list(monomial), "coefficient": coefficient}
                for monomial, coefficient in self.sorted_terms()
            ],
        }

    def _check_compatible(self, other: SparsePolynomial) -> None:
        if not isinstance(other, SparsePolynomial):
            raise TypeError("other must be a SparsePolynomial")
        if self.p != other.p:
            raise ValueError("polynomial modulus mismatch")
        if self.nvars != other.nvars:
            raise ValueError("polynomial dimension mismatch")

    def add(
        self,
        other: SparsePolynomial,
        counter: OperationCounter | None = None,
    ) -> SparsePolynomial:
        self._check_compatible(other)
        _validate_counter(counter)
        output = dict(self._terms)
        for monomial, coefficient in other._terms.items():
            if monomial not in output:
                output[monomial] = coefficient
                continue
            combined = fp_add(output[monomial], coefficient, self.p, counter)
            if fp_is_zero(combined, self.p, counter):
                del output[monomial]
            else:
                output[monomial] = combined
        return self._from_canonical(self.p, self.nvars, output)

    def subtract(
        self,
        other: SparsePolynomial,
        counter: OperationCounter | None = None,
    ) -> SparsePolynomial:
        self._check_compatible(other)
        _validate_counter(counter)
        output = dict(self._terms)
        for monomial, coefficient in other._terms.items():
            if monomial not in output:
                output[monomial] = fp_subtract(0, coefficient, self.p, counter)
                continue
            combined = fp_subtract(output[monomial], coefficient, self.p, counter)
            if fp_is_zero(combined, self.p, counter):
                del output[monomial]
            else:
                output[monomial] = combined
        return self._from_canonical(self.p, self.nvars, output)

    def multiply(
        self,
        other: SparsePolynomial,
        counter: OperationCounter | None = None,
    ) -> SparsePolynomial:
        self._check_compatible(other)
        _validate_counter(counter)
        if not self._terms or not other._terms:
            return self._from_canonical(self.p, self.nvars, {})
        output: dict[Monomial, int] = {}
        for left_monomial, left_coefficient in self._terms.items():
            for right_monomial, right_coefficient in other._terms.items():
                monomial = tuple(
                    left_monomial[index] + right_monomial[index]
                    for index in range(self.nvars)
                )
                product = fp_multiply(
                    left_coefficient,
                    right_coefficient,
                    self.p,
                    counter,
                )
                if monomial not in output:
                    output[monomial] = product
                    continue
                combined = fp_add(output[monomial], product, self.p, counter)
                if fp_is_zero(combined, self.p, counter):
                    del output[monomial]
                else:
                    output[monomial] = combined
        return self._from_canonical(self.p, self.nvars, output)

    def power(
        self,
        exponent: int,
        counter: OperationCounter | None = None,
    ) -> SparsePolynomial:
        _exact_int(exponent, "exponent", 0)
        _validate_counter(counter)
        if exponent == 0:
            return self.constant(self.p, self.nvars, 1, counter=counter)
        if exponent == 1:
            return self._from_canonical(self.p, self.nvars, self._terms)
        result = self.constant(self.p, self.nvars, 1, counter=counter)
        base = self
        remaining = exponent
        while remaining:
            if remaining & 1:
                result = result.multiply(base, counter)
            remaining >>= 1
            if remaining:
                base = base.multiply(base, counter)
        return result

    def scale(
        self,
        scalar: int,
        counter: OperationCounter | None = None,
    ) -> SparsePolynomial:
        _exact_int(scalar, "scalar")
        _validate_counter(counter)
        reduced = scalar % self.p
        if fp_is_zero(reduced, self.p, counter) or not self._terms:
            return self._from_canonical(self.p, self.nvars, {})
        output = {
            monomial: fp_multiply(coefficient, reduced, self.p, counter)
            for monomial, coefficient in self._terms.items()
        }
        return self._from_canonical(self.p, self.nvars, output)

    def shift_monomials(self, shifts: Sequence[int]) -> SparsePolynomial:
        shift_tuple = tuple(shifts)
        if len(shift_tuple) != self.nvars:
            raise ValueError("shift dimension mismatch")
        for index, shift in enumerate(shift_tuple):
            _exact_int(shift, f"shifts[{index}]", 0)
        output = {
            tuple(monomial[index] + shift_tuple[index] for index in range(self.nvars)):
            coefficient
            for monomial, coefficient in self._terms.items()
        }
        return self._from_canonical(self.p, self.nvars, output)

    def evaluate_one_variable(
        self,
        variable: int,
        value: int,
        counter: OperationCounter | None = None,
    ) -> SparsePolynomial:
        _exact_int(variable, "variable", 0)
        _exact_int(value, "value")
        _validate_counter(counter)
        if variable >= self.nvars:
            raise IndexError("variable index is outside the polynomial dimension")
        output_nvars = self.nvars - 1
        if not self._terms:
            return self._from_canonical(self.p, output_nvars, {})
        maximum_exponent = max(monomial[variable] for monomial in self._terms)
        powers = [1]
        reduced_value = value % self.p
        for _ in range(maximum_exponent):
            powers.append(fp_multiply(powers[-1], reduced_value, self.p, counter))
        output: dict[Monomial, int] = {}
        for monomial, coefficient in self._terms.items():
            exponent = monomial[variable]
            evaluated = coefficient
            if exponent:
                evaluated = fp_multiply(
                    coefficient,
                    powers[exponent],
                    self.p,
                    counter,
                )
                if fp_is_zero(evaluated, self.p, counter):
                    continue
            projected = monomial[:variable] + monomial[variable + 1 :]
            if projected not in output:
                output[projected] = evaluated
                continue
            combined = fp_add(output[projected], evaluated, self.p, counter)
            if fp_is_zero(combined, self.p, counter):
                del output[projected]
            else:
                output[projected] = combined
        return self._from_canonical(self.p, output_nvars, output)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SparsePolynomial):
            return NotImplemented
        return (
            self.p == other.p
            and self.nvars == other.nvars
            and self._terms == other._terms
        )

    def __repr__(self) -> str:
        return (
            f"SparsePolynomial(p={self.p}, nvars={self.nvars}, "
            f"terms={dict(self.sorted_terms())!r})"
        )


def sparse_add(
    left: SparsePolynomial,
    right: SparsePolynomial,
    counter: OperationCounter | None = None,
) -> SparsePolynomial:
    return left.add(right, counter)


def sparse_subtract(
    left: SparsePolynomial,
    right: SparsePolynomial,
    counter: OperationCounter | None = None,
) -> SparsePolynomial:
    return left.subtract(right, counter)


def sparse_multiply(
    left: SparsePolynomial,
    right: SparsePolynomial,
    counter: OperationCounter | None = None,
) -> SparsePolynomial:
    return left.multiply(right, counter)


def sparse_power(
    polynomial: SparsePolynomial,
    exponent: int,
    counter: OperationCounter | None = None,
) -> SparsePolynomial:
    return polynomial.power(exponent, counter)


def sparse_scale(
    polynomial: SparsePolynomial,
    scalar: int,
    counter: OperationCounter | None = None,
) -> SparsePolynomial:
    return polynomial.scale(scalar, counter)


def sparse_evaluate_one_variable(
    polynomial: SparsePolynomial,
    variable: int,
    value: int,
    counter: OperationCounter | None = None,
) -> SparsePolynomial:
    return polynomial.evaluate_one_variable(variable, value, counter)


def univariate_trim(
    coefficients: Iterable[int],
    p: int,
    counter: OperationCounter | None = None,
) -> UniPolynomial:
    _validate_modulus(p)
    _validate_counter(counter)
    values: list[int] = []
    for index, coefficient in enumerate(coefficients):
        _exact_int(coefficient, f"coefficients[{index}]")
        values.append(coefficient % p)
    if not values:
        return (0,)
    while len(values) > 1:
        if not fp_is_zero(values[-1], p, counter):
            break
        values.pop()
    return tuple(values)


def _univariate_is_zero(
    polynomial: UniPolynomial,
    p: int,
    counter: OperationCounter | None,
) -> bool:
    return len(polynomial) == 1 and fp_is_zero(polynomial[0], p, counter)


def univariate_add(
    left: Iterable[int],
    right: Iterable[int],
    p: int,
    counter: OperationCounter | None = None,
) -> UniPolynomial:
    lhs = univariate_trim(left, p, counter)
    rhs = univariate_trim(right, p, counter)
    overlap = min(len(lhs), len(rhs))
    output = [
        fp_add(lhs[index], rhs[index], p, counter) for index in range(overlap)
    ]
    if len(lhs) > overlap:
        output.extend(lhs[overlap:])
    elif len(rhs) > overlap:
        output.extend(rhs[overlap:])
    return univariate_trim(output, p, counter)


def univariate_subtract(
    left: Iterable[int],
    right: Iterable[int],
    p: int,
    counter: OperationCounter | None = None,
) -> UniPolynomial:
    lhs = univariate_trim(left, p, counter)
    rhs = univariate_trim(right, p, counter)
    overlap = min(len(lhs), len(rhs))
    output = [
        fp_subtract(lhs[index], rhs[index], p, counter)
        for index in range(overlap)
    ]
    if len(lhs) > overlap:
        output.extend(lhs[overlap:])
    else:
        output.extend(
            fp_subtract(0, rhs[index], p, counter)
            for index in range(overlap, len(rhs))
        )
    return univariate_trim(output, p, counter)


def univariate_multiply(
    left: Iterable[int],
    right: Iterable[int],
    p: int,
    counter: OperationCounter | None = None,
) -> UniPolynomial:
    lhs = univariate_trim(left, p, counter)
    rhs = univariate_trim(right, p, counter)
    lhs_terms = [
        (index, coefficient)
        for index, coefficient in enumerate(lhs)
        if not fp_is_zero(coefficient, p, counter)
    ]
    rhs_terms = [
        (index, coefficient)
        for index, coefficient in enumerate(rhs)
        if not fp_is_zero(coefficient, p, counter)
    ]
    if not lhs_terms or not rhs_terms:
        return (0,)
    output: dict[int, int] = {}
    for left_degree, left_coefficient in lhs_terms:
        for right_degree, right_coefficient in rhs_terms:
            degree = left_degree + right_degree
            product = fp_multiply(
                left_coefficient,
                right_coefficient,
                p,
                counter,
            )
            if degree not in output:
                output[degree] = product
                continue
            combined = fp_add(output[degree], product, p, counter)
            if fp_is_zero(combined, p, counter):
                del output[degree]
            else:
                output[degree] = combined
    if not output:
        return (0,)
    dense = [0] * (max(output) + 1)
    for degree, coefficient in output.items():
        dense[degree] = coefficient
    return univariate_trim(dense, p, counter)


def univariate_divmod(
    dividend: Iterable[int],
    divisor: Iterable[int],
    p: int,
    counter: OperationCounter | None = None,
) -> tuple[UniPolynomial, UniPolynomial]:
    numerator = univariate_trim(dividend, p, counter)
    denominator = univariate_trim(divisor, p, counter)
    if _univariate_is_zero(denominator, p, counter):
        raise ZeroDivisionError("polynomial division by zero")
    if _univariate_is_zero(numerator, p, counter):
        return (0,), (0,)
    if len(numerator) < len(denominator):
        return (0,), numerator
    quotient = [0] * (len(numerator) - len(denominator) + 1)
    remainder = list(numerator)
    inverse_lead = fp_inverse(denominator[-1], p, counter)
    while len(remainder) >= len(denominator):
        canonical_remainder = univariate_trim(remainder, p, counter)
        if _univariate_is_zero(canonical_remainder, p, counter):
            remainder = [0]
            break
        remainder = list(canonical_remainder)
        if len(remainder) < len(denominator):
            break
        shift = len(remainder) - len(denominator)
        coefficient = fp_multiply(remainder[-1], inverse_lead, p, counter)
        quotient[shift] = coefficient
        for index, divisor_coefficient in enumerate(denominator):
            product = fp_multiply(coefficient, divisor_coefficient, p, counter)
            target = index + shift
            remainder[target] = fp_subtract(
                remainder[target],
                product,
                p,
                counter,
            )
        remainder = list(univariate_trim(remainder, p, counter))
    return (
        univariate_trim(quotient, p, counter),
        univariate_trim(remainder, p, counter),
    )


def univariate_mod(
    dividend: Iterable[int],
    modulus: Iterable[int],
    p: int,
    counter: OperationCounter | None = None,
) -> UniPolynomial:
    return univariate_divmod(dividend, modulus, p, counter)[1]


def univariate_monic(
    polynomial: Iterable[int],
    p: int,
    counter: OperationCounter | None = None,
) -> UniPolynomial:
    canonical = univariate_trim(polynomial, p, counter)
    if _univariate_is_zero(canonical, p, counter):
        return (0,)
    inverse_lead = fp_inverse(canonical[-1], p, counter)
    return univariate_trim(
        (
            fp_multiply(coefficient, inverse_lead, p, counter)
            for coefficient in canonical
        ),
        p,
        counter,
    )


def univariate_gcd(
    left: Iterable[int],
    right: Iterable[int],
    p: int,
    counter: OperationCounter | None = None,
) -> UniPolynomial:
    lhs = univariate_trim(left, p, counter)
    rhs = univariate_trim(right, p, counter)
    while not _univariate_is_zero(rhs, p, counter):
        lhs, rhs = rhs, univariate_mod(lhs, rhs, p, counter)
    return univariate_monic(lhs, p, counter)


def univariate_evaluate(
    polynomial: Iterable[int],
    value: int,
    p: int,
    counter: OperationCounter | None = None,
) -> int:
    canonical = univariate_trim(polynomial, p, counter)
    _exact_int(value, "value")
    accumulator = 0
    reduced_value = value % p
    for coefficient in reversed(canonical):
        accumulator = fp_multiply(accumulator, reduced_value, p, counter)
        accumulator = fp_add(accumulator, coefficient, p, counter)
    return accumulator


def univariate_product_from_roots(
    roots: Iterable[int],
    p: int,
    counter: OperationCounter | None = None,
) -> UniPolynomial:
    _validate_modulus(p)
    product: UniPolynomial = (1,)
    for index, root in enumerate(roots):
        _exact_int(root, f"roots[{index}]")
        constant = fp_subtract(0, root % p, p, counter)
        product = univariate_multiply(product, (constant, 1), p, counter)
    return product


def _canonical_disclosed_roots(
    roots: Iterable[int],
    p: int,
    *,
    require_distinct: bool,
) -> tuple[int, ...]:
    canonical: list[int] = []
    seen: set[int] = set()
    for index, root in enumerate(roots):
        _exact_int(root, f"roots[{index}]")
        reduced = root % p
        if require_distinct and reduced in seen:
            raise ValueError("disclosed roots must be distinct in F_p")
        seen.add(reduced)
        canonical.append(reduced)
    return tuple(canonical)


def univariate_roots_from_disclosed(
    polynomial: Iterable[int],
    disclosed_roots: Iterable[int],
    p: int,
    counter: OperationCounter | None = None,
) -> tuple[int, ...]:
    canonical = univariate_trim(polynomial, p, counter)
    roots = _canonical_disclosed_roots(
        disclosed_roots,
        p,
        require_distinct=True,
    )
    extracted: list[int] = []
    for root in roots:
        value = univariate_evaluate(canonical, root, p, counter)
        if fp_is_zero(value, p, counter):
            extracted.append(root)
    return tuple(extracted)


def univariate_scalar_ratio(
    left: Iterable[int],
    right: Iterable[int],
    p: int,
    counter: OperationCounter | None = None,
) -> int | None:
    lhs = univariate_trim(left, p, counter)
    rhs = univariate_trim(right, p, counter)
    lhs_zero = _univariate_is_zero(lhs, p, counter)
    rhs_zero = _univariate_is_zero(rhs, p, counter)
    if lhs_zero or rhs_zero:
        return 1 if lhs_zero and rhs_zero else None
    if len(lhs) != len(rhs):
        return None
    ratio = fp_multiply(lhs[-1], fp_inverse(rhs[-1], p, counter), p, counter)
    for left_coefficient, right_coefficient in zip(lhs, rhs):
        expected = fp_multiply(ratio, right_coefficient, p, counter)
        difference = fp_subtract(left_coefficient, expected, p, counter)
        if not fp_is_zero(difference, p, counter):
            return None
    return ratio


def univariate_equal_up_to_scalar(
    left: Iterable[int],
    right: Iterable[int],
    p: int,
    counter: OperationCounter | None = None,
) -> bool:
    return univariate_scalar_ratio(left, right, p, counter) is not None


def sparse_from_univariate(
    polynomial: Iterable[int],
    p: int,
    *,
    nvars: int = 1,
    variable: int = 0,
    counter: OperationCounter | None = None,
) -> SparsePolynomial:
    _exact_int(nvars, "nvars", 1)
    _exact_int(variable, "variable", 0)
    if variable >= nvars:
        raise IndexError("variable index is outside the polynomial dimension")
    canonical = univariate_trim(polynomial, p, counter)
    terms: dict[Monomial, int] = {}
    for degree, coefficient in enumerate(canonical):
        monomial = [0] * nvars
        monomial[variable] = degree
        terms[tuple(monomial)] = coefficient
    return SparsePolynomial(p, nvars, terms, counter=counter)


def sparse_to_univariate(polynomial: SparsePolynomial) -> UniPolynomial:
    if not isinstance(polynomial, SparsePolynomial):
        raise TypeError("polynomial must be a SparsePolynomial")
    if polynomial.nvars != 1:
        raise ValueError("polynomial must have exactly one variable")
    if polynomial.is_zero():
        return (0,)
    coefficients = [0] * (polynomial.degree(0) + 1)
    for monomial, coefficient in polynomial.terms.items():
        coefficients[monomial[0]] = coefficient
    return tuple(coefficients)


def normalize_sparse(
    polynomial: SparsePolynomial,
    counter: OperationCounter | None = None,
) -> SparsePolynomial:
    if not isinstance(polynomial, SparsePolynomial):
        raise TypeError("polynomial must be a SparsePolynomial")
    if polynomial.is_zero():
        return SparsePolynomial.zero(polynomial.p, polynomial.nvars)
    leading_monomial = max(polynomial.terms)
    inverse = fp_inverse(polynomial.terms[leading_monomial], polynomial.p, counter)
    return polynomial.scale(inverse, counter)


def sparse_scalar_ratio(
    left: SparsePolynomial,
    right: SparsePolynomial,
    counter: OperationCounter | None = None,
) -> int | None:
    left._check_compatible(right)
    if left.is_zero() or right.is_zero():
        return 1 if left.is_zero() and right.is_zero() else None
    if set(left.terms) != set(right.terms):
        return None
    leading_monomial = max(left.terms)
    ratio = fp_multiply(
        left.terms[leading_monomial],
        fp_inverse(right.terms[leading_monomial], left.p, counter),
        left.p,
        counter,
    )
    for monomial, left_coefficient in left.terms.items():
        expected = fp_multiply(ratio, right.terms[monomial], left.p, counter)
        difference = fp_subtract(left_coefficient, expected, left.p, counter)
        if not fp_is_zero(difference, left.p, counter):
            return None
    return ratio


def sparse_equal_up_to_scalar(
    left: SparsePolynomial,
    right: SparsePolynomial,
    counter: OperationCounter | None = None,
) -> bool:
    return sparse_scalar_ratio(left, right, counter) is not None


def _f3_quadratic_coefficients(
    x1: SparsePolynomial,
    x2: SparsePolynomial,
    a: int,
    b: int,
    counter: OperationCounter | None,
) -> tuple[SparsePolynomial, SparsePolynomial, SparsePolynomial]:
    x1._check_compatible(x2)
    p = x1.p
    _exact_int(a, "a")
    _exact_int(b, "b")
    constant_a = SparsePolynomial.constant(p, x1.nvars, a, counter=counter)
    two_b = fp_multiply(2, b, p, counter)
    four_b = fp_multiply(4, b, p, counter)
    sum_x = x1.add(x2, counter)
    difference_x = x1.subtract(x2, counter)
    product_x = x1.multiply(x2, counter)
    coefficient_2 = difference_x.power(2, counter)
    inner = product_x.add(constant_a, counter)
    middle = sum_x.multiply(inner, counter).add(
        SparsePolynomial.constant(p, x1.nvars, two_b, counter=counter),
        counter,
    )
    coefficient_1 = middle.scale(-2, counter)
    product_minus_a = product_x.subtract(constant_a, counter)
    coefficient_0 = product_minus_a.power(2, counter).subtract(
        sum_x.scale(four_b, counter),
        counter,
    )
    return coefficient_2, coefficient_1, coefficient_0


def semaev_f3_from_polynomials(
    x1: SparsePolynomial,
    x2: SparsePolynomial,
    x3: SparsePolynomial,
    a: int,
    b: int,
    counter: OperationCounter | None = None,
) -> SparsePolynomial:
    x1._check_compatible(x2)
    x1._check_compatible(x3)
    coefficient_2, coefficient_1, coefficient_0 = _f3_quadratic_coefficients(
        x1,
        x2,
        a,
        b,
        counter,
    )
    return (
        coefficient_2.multiply(x3.power(2, counter), counter)
        .add(coefficient_1.multiply(x3, counter), counter)
        .add(coefficient_0, counter)
    )


def semaev_f3(
    p: int,
    a: int,
    b: int,
    counter: OperationCounter | None = None,
) -> SparsePolynomial:
    variables = [
        SparsePolynomial.variable(p, 3, index, counter=counter) for index in range(3)
    ]
    return semaev_f3_from_polynomials(
        variables[0], variables[1], variables[2], a, b, counter
    )


def semaev_f3_fixed_x(
    p: int,
    a: int,
    b: int,
    x_q: int,
    counter: OperationCounter | None = None,
) -> SparsePolynomial:
    first = SparsePolynomial.variable(p, 2, 0, counter=counter)
    second = SparsePolynomial.variable(p, 2, 1, counter=counter)
    fixed = SparsePolynomial.constant(p, 2, x_q, counter=counter)
    return semaev_f3_from_polynomials(first, second, fixed, a, b, counter)


def quadratic_resultant(
    a2: SparsePolynomial,
    a1: SparsePolynomial,
    a0: SparsePolynomial,
    b2: SparsePolynomial,
    b1: SparsePolynomial,
    b0: SparsePolynomial,
    counter: OperationCounter | None = None,
) -> SparsePolynomial:
    """Return the exact resultant of two quadratics in the eliminated variable."""

    polynomials = (a2, a1, a0, b2, b1, b0)
    for polynomial in polynomials[1:]:
        polynomials[0]._check_compatible(polynomial)
    first_minor = a2.multiply(b0, counter).subtract(
        a0.multiply(b2, counter),
        counter,
    )
    second_minor = a2.multiply(b1, counter).subtract(
        a1.multiply(b2, counter),
        counter,
    )
    third_minor = a1.multiply(b0, counter).subtract(
        a0.multiply(b1, counter),
        counter,
    )
    return first_minor.power(2, counter).subtract(
        second_minor.multiply(third_minor, counter),
        counter,
    )


def _assert_f4_degree_bound(polynomial: SparsePolynomial) -> None:
    if any(degree > 4 for degree in polynomial.degrees()):
        raise AssertionError("constructed f4 exceeds degree four in a coordinate")


def semaev_f4(
    p: int,
    a: int,
    b: int,
    counter: OperationCounter | None = None,
) -> SparsePolynomial:
    u, v, w, x = (
        SparsePolynomial.variable(p, 4, index, counter=counter) for index in range(4)
    )
    left = _f3_quadratic_coefficients(u, v, a, b, counter)
    right = _f3_quadratic_coefficients(w, x, a, b, counter)
    result = quadratic_resultant(*left, *right, counter=counter)
    _assert_f4_degree_bound(result)
    return result


def semaev_f4_fixed_x(
    p: int,
    a: int,
    b: int,
    x_q: int,
    counter: OperationCounter | None = None,
) -> SparsePolynomial:
    u = SparsePolynomial.variable(p, 3, 0, counter=counter)
    v = SparsePolynomial.variable(p, 3, 1, counter=counter)
    w = SparsePolynomial.variable(p, 3, 2, counter=counter)
    fixed = SparsePolynomial.constant(p, 3, x_q, counter=counter)
    left = _f3_quadratic_coefficients(u, v, a, b, counter)
    right = _f3_quadratic_coefficients(w, fixed, a, b, counter)
    result = quadratic_resultant(*left, *right, counter=counter)
    _assert_f4_degree_bound(result)
    return result


def _normalize_source_kind(kind: str) -> str:
    if not isinstance(kind, str):
        raise TypeError("source-map kind must be a string")
    aliases = {
        "identity": "identity",
        "x_interval": "identity",
        "square": "square",
        "square_map": "square",
        "mobius": "mobius",
        "rational": "mobius",
        "rational_union": "mobius",
    }
    try:
        return aliases[kind]
    except KeyError as error:
        raise ValueError(f"unknown source-map kind: {kind}") from error


def source_map_polynomials(
    p: int,
    kind: str,
    *,
    c: int = 0,
    d: int = 0,
    e: int = 0,
    counter: OperationCounter | None = None,
) -> tuple[UniPolynomial, UniPolynomial]:
    """Return ``(numerator, denominator)`` for a disclosed source map."""

    _validate_modulus(p)
    normalized = _normalize_source_kind(kind)
    _exact_int(c, "c")
    _exact_int(d, "d")
    _exact_int(e, "e")
    if normalized == "identity":
        return (0, 1), (1,)
    if normalized == "square":
        return univariate_trim((c, 0, 1), p, counter), (1,)
    return (
        univariate_trim((d, 1), p, counter),
        univariate_trim((e, 1), p, counter),
    )


def source_map_value(
    p: int,
    kind: str,
    t: int,
    *,
    c: int = 0,
    d: int = 0,
    e: int = 0,
    counter: OperationCounter | None = None,
) -> int:
    numerator, denominator = source_map_polynomials(
        p,
        kind,
        c=c,
        d=d,
        e=e,
        counter=counter,
    )
    numerator_value = univariate_evaluate(numerator, t, p, counter)
    if denominator == (1,):
        return numerator_value
    denominator_value = univariate_evaluate(denominator, t, p, counter)
    inverse = fp_inverse(denominator_value, p, counter)
    return fp_multiply(numerator_value, inverse, p, counter)


def source_map_values(
    p: int,
    kind: str,
    roots: Iterable[int],
    *,
    c: int = 0,
    d: int = 0,
    e: int = 0,
    counter: OperationCounter | None = None,
) -> tuple[int, ...]:
    values: list[int] = []
    for index, root in enumerate(roots):
        _exact_int(root, f"roots[{index}]")
        values.append(
            source_map_value(
                p,
                kind,
                root,
                c=c,
                d=d,
                e=e,
                counter=counter,
            )
        )
    return tuple(values)


def source_denominator_scalar(
    p: int,
    kind: str,
    roots: Iterable[int],
    *,
    c: int = 0,
    d: int = 0,
    e: int = 0,
    counter: OperationCounter | None = None,
) -> int:
    """Return ``product(D(t)^4)`` and reject a source pole."""

    _, denominator = source_map_polynomials(
        p,
        kind,
        c=c,
        d=d,
        e=e,
        counter=counter,
    )
    canonical_roots = _canonical_disclosed_roots(
        roots,
        p,
        require_distinct=True,
    )
    if denominator == (1,):
        return 1
    scalar = 1
    for root in canonical_roots:
        value = univariate_evaluate(denominator, root, p, counter)
        if fp_is_zero(value, p, counter):
            raise ZeroDivisionError(f"source root {root} is a pole of the source map")
        fourth_power = fp_power(value, F4_DENOMINATOR_POWER, p, counter)
        scalar = fp_multiply(scalar, fourth_power, p, counter)
    return scalar


def _sparse_power_table(
    base: SparsePolynomial,
    maximum: int,
    counter: OperationCounter | None,
) -> tuple[SparsePolynomial, ...]:
    one = SparsePolynomial.constant(base.p, base.nvars, 1, counter=counter)
    powers = [one]
    if base.is_one():
        powers.extend(one for _ in range(maximum))
        return tuple(powers)
    for _ in range(maximum):
        powers.append(powers[-1].multiply(base, counter))
    return tuple(powers)


def _multiply_unless_one(
    left: SparsePolynomial,
    right: SparsePolynomial,
    counter: OperationCounter | None,
) -> SparsePolynomial:
    if left.is_one():
        return SparsePolynomial._from_canonical(right.p, right.nvars, right.terms)
    if right.is_one():
        return SparsePolynomial._from_canonical(left.p, left.nvars, left.terms)
    return left.multiply(right, counter)


def substitute_source_map(
    f4_fixed: SparsePolynomial,
    kind: str,
    *,
    c: int = 0,
    d: int = 0,
    e: int = 0,
    counter: OperationCounter | None = None,
) -> SparsePolynomial:
    """Return ``D(T)^4 f4(N(T)/D(T), V, W, xQ)``.

    ``f4_fixed`` must have variable order ``(U,V,W)``.  The returned variable
    order is ``(T,V,W)``.
    """

    if not isinstance(f4_fixed, SparsePolynomial):
        raise TypeError("f4_fixed must be a SparsePolynomial")
    if f4_fixed.nvars != 3:
        raise ValueError("f4_fixed must have variables (U,V,W)")
    if f4_fixed.degree(0) > F4_DENOMINATOR_POWER:
        raise ValueError("source substitution requires degree at most four in U")
    numerator, denominator = source_map_polynomials(
        f4_fixed.p,
        kind,
        c=c,
        d=d,
        e=e,
        counter=counter,
    )
    numerator_sparse = sparse_from_univariate(
        numerator,
        f4_fixed.p,
        nvars=3,
        variable=0,
        counter=counter,
    )
    denominator_sparse = sparse_from_univariate(
        denominator,
        f4_fixed.p,
        nvars=3,
        variable=0,
        counter=counter,
    )
    numerator_powers = _sparse_power_table(
        numerator_sparse,
        F4_DENOMINATOR_POWER,
        counter,
    )
    denominator_powers = _sparse_power_table(
        denominator_sparse,
        F4_DENOMINATOR_POWER,
        counter,
    )
    result = SparsePolynomial.zero(f4_fixed.p, 3)
    for (u_degree, v_degree, w_degree), coefficient in f4_fixed.terms.items():
        component = _multiply_unless_one(
            numerator_powers[u_degree],
            denominator_powers[F4_DENOMINATOR_POWER - u_degree],
            counter,
        )
        component = component.shift_monomials((0, v_degree, w_degree))
        component = component.scale(coefficient, counter)
        result = result.add(component, counter)
    return result


def substitute_identity_source(
    f4_fixed: SparsePolynomial,
    counter: OperationCounter | None = None,
) -> SparsePolynomial:
    return substitute_source_map(f4_fixed, "identity", counter=counter)


def substitute_square_source(
    f4_fixed: SparsePolynomial,
    c: int,
    counter: OperationCounter | None = None,
) -> SparsePolynomial:
    return substitute_source_map(f4_fixed, "square", c=c, counter=counter)


def substitute_mobius_source(
    f4_fixed: SparsePolynomial,
    d: int,
    e: int,
    counter: OperationCounter | None = None,
) -> SparsePolynomial:
    return substitute_source_map(f4_fixed, "mobius", d=d, e=e, counter=counter)


def eliminate_source_roots(
    source_polynomial: SparsePolynomial,
    source_roots: Iterable[int],
    counter: OperationCounter | None = None,
) -> SparsePolynomial:
    """Evaluate the first variable at each distinct source root and multiply."""

    if not isinstance(source_polynomial, SparsePolynomial):
        raise TypeError("source_polynomial must be a SparsePolynomial")
    if source_polynomial.nvars < 1:
        raise ValueError("source_polynomial must have an evaluation variable")
    roots = _canonical_disclosed_roots(
        source_roots,
        source_polynomial.p,
        require_distinct=True,
    )
    product = SparsePolynomial.constant(
        source_polynomial.p,
        source_polynomial.nvars - 1,
        1,
        counter=counter,
    )
    for root in roots:
        evaluated = source_polynomial.evaluate_one_variable(0, root, counter)
        product = product.multiply(evaluated, counter)
    return product


def source_root_elimination(
    source_polynomial: SparsePolynomial,
    source_roots: Iterable[int],
    counter: OperationCounter | None = None,
) -> SparsePolynomial:
    """Named integration entry point for accepted-source product evaluation."""

    return eliminate_source_roots(source_polynomial, source_roots, counter)


def direct_fixed_x_product(
    f4_fixed: SparsePolynomial,
    fixed_x_roots: Iterable[int],
    counter: OperationCounter | None = None,
) -> SparsePolynomial:
    """Return ``product_u f4(u,V,W,xQ)`` with multiplicity preserved."""

    if not isinstance(f4_fixed, SparsePolynomial):
        raise TypeError("f4_fixed must be a SparsePolynomial")
    if f4_fixed.nvars != 3:
        raise ValueError("f4_fixed must have variables (U,V,W)")
    product = SparsePolynomial.constant(f4_fixed.p, 2, 1, counter=counter)
    for index, root in enumerate(fixed_x_roots):
        _exact_int(root, f"fixed_x_roots[{index}]")
        evaluated = f4_fixed.evaluate_one_variable(0, root, counter)
        product = product.multiply(evaluated, counter)
    return product


def direct_factor_root_product(
    f4_fixed: SparsePolynomial,
    factor_x_roots: Iterable[int],
    counter: OperationCounter | None = None,
) -> SparsePolynomial:
    """Named integration entry point for the direct fixed-factor-x product."""

    return direct_fixed_x_product(f4_fixed, factor_x_roots, counter)


def build_m2(
    d2_roots: Iterable[int],
    p: int,
    counter: OperationCounter | None = None,
) -> UniPolynomial:
    """Build the monic ``M2(V)=product(V-r)`` from distinct D2 x-roots."""

    roots = _canonical_disclosed_roots(d2_roots, p, require_distinct=True)
    return univariate_product_from_roots(roots, p, counter)


def d2_root_product_mod_m2(
    polynomial_vw: SparsePolynomial,
    d2_roots: Iterable[int],
    *,
    m2: Iterable[int] | None = None,
    counter: OperationCounter | None = None,
) -> UniPolynomial:
    """Return ``product_w polynomial_vw(V,w) mod M2(V)``.

    The disclosed D2 roots must be distinct.  If ``m2`` is omitted, the monic
    root polynomial is built from those roots.  Reduction after every factor is
    exact and bounds the live degree; it is not an optimized product tree.
    """

    if not isinstance(polynomial_vw, SparsePolynomial):
        raise TypeError("polynomial_vw must be a SparsePolynomial")
    if polynomial_vw.nvars != 2:
        raise ValueError("polynomial_vw must have variables (V,W)")
    roots = _canonical_disclosed_roots(
        d2_roots,
        polynomial_vw.p,
        require_distinct=True,
    )
    modulus = (
        univariate_product_from_roots(roots, polynomial_vw.p, counter)
        if m2 is None
        else univariate_trim(m2, polynomial_vw.p, counter)
    )
    if _univariate_is_zero(modulus, polynomial_vw.p, counter):
        raise ZeroDivisionError("M2 must be nonzero")
    product: UniPolynomial = (1,)
    for root in roots:
        factor = sparse_to_univariate(
            polynomial_vw.evaluate_one_variable(1, root, counter)
        )
        product = univariate_mod(
            univariate_multiply(product, factor, polynomial_vw.p, counter),
            modulus,
            polynomial_vw.p,
            counter,
        )
    return univariate_mod(product, modulus, polynomial_vw.p, counter)


def s3_root_product_mod_m2(
    f3_vw_xq: SparsePolynomial,
    d2_roots: Iterable[int],
    *,
    m2: Iterable[int] | None = None,
    counter: OperationCounter | None = None,
) -> UniPolynomial:
    """Return the S3 control product ``product_w f3(V,w,xQ) mod M2``."""

    return d2_root_product_mod_m2(
        f3_vw_xq,
        d2_roots,
        m2=m2,
        counter=counter,
    )


def s3_identity_corrected_root_product_mod_m2(
    f3_vw_xq: SparsePolynomial,
    x_q: int,
    d2_roots: Iterable[int],
    *,
    m2: Iterable[int] | None = None,
    counter: OperationCounter | None = None,
) -> UniPolynomial:
    """Include the missing ``D2`` identity half in the affine S3 control.

    The ordinary root product ranges only over finite D2 x-orbits.  For an
    affine target ``Q``, the valid route ``Q=A+O`` contributes the additional
    factor ``V-x(Q)``.  Multiplying by it is harmless when ``x(Q)`` is not an
    M2 root and exact when it is.  The all-identity target has no x-coordinate
    and remains a caller-level special case.
    """

    if not isinstance(f3_vw_xq, SparsePolynomial):
        raise TypeError("f3_vw_xq must be a SparsePolynomial")
    _exact_int(x_q, "x_q")
    roots = _canonical_disclosed_roots(
        d2_roots,
        f3_vw_xq.p,
        require_distinct=True,
    )
    modulus = (
        build_m2(roots, f3_vw_xq.p, counter)
        if m2 is None
        else univariate_trim(m2, f3_vw_xq.p, counter)
    )
    finite_product = s3_root_product_mod_m2(
        f3_vw_xq,
        roots,
        m2=modulus,
        counter=counter,
    )
    identity_factor = ((-x_q) % f3_vw_xq.p, 1)
    return univariate_mod(
        univariate_multiply(
            finite_product,
            identity_factor,
            f3_vw_xq.p,
            counter,
        ),
        modulus,
        f3_vw_xq.p,
        counter,
    )


def s4_root_product_mod_m2(
    combined_g_vw: SparsePolynomial,
    d2_roots: Iterable[int],
    *,
    m2: Iterable[int] | None = None,
    counter: OperationCounter | None = None,
) -> UniPolynomial:
    """Return the S4 product ``product_w G_Q(V,w) mod M2``."""

    return d2_root_product_mod_m2(
        combined_g_vw,
        d2_roots,
        m2=m2,
        counter=counter,
    )


def gcd_roots_against_m2(
    root_product_remainder: Iterable[int],
    m2: Iterable[int],
    disclosed_d2_roots: Iterable[int],
    p: int,
    counter: OperationCounter | None = None,
) -> tuple[UniPolynomial, tuple[int, ...]]:
    """Return ``(monic_gcd, disclosed roots of that gcd)``."""

    common = univariate_gcd(root_product_remainder, m2, p, counter)
    roots = univariate_roots_from_disclosed(
        common,
        disclosed_d2_roots,
        p,
        counter,
    )
    return common, roots


@dataclass(frozen=True)
class S3PositiveControlResult:
    relation_polynomial: SparsePolynomial
    m2: UniPolynomial
    root_product_remainder: UniPolynomial
    gcd: UniPolynomial
    compatible_roots: tuple[int, ...]

    def to_record(self) -> dict[str, Any]:
        return {
            "schema": "s3-positive-control-v1",
            "relation_polynomial": self.relation_polynomial.to_record(),
            "m2": list(self.m2),
            "root_product_remainder": list(self.root_product_remainder),
            "gcd": list(self.gcd),
            "compatible_roots": list(self.compatible_roots),
        }


def s3_positive_control(
    p: int,
    a: int,
    b: int,
    x_q: int,
    d2_roots: Iterable[int],
    counter: OperationCounter | None = None,
) -> S3PositiveControlResult:
    """Compute the contract's exact S3 root-product/gcd positive control."""

    roots = _canonical_disclosed_roots(d2_roots, p, require_distinct=True)
    relation = semaev_f3_fixed_x(p, a, b, x_q, counter)
    m2 = build_m2(roots, p, counter)
    remainder = s3_identity_corrected_root_product_mod_m2(
        relation,
        x_q,
        roots,
        m2=m2,
        counter=counter,
    )
    common, compatible = gcd_roots_against_m2(
        remainder,
        m2,
        roots,
        p,
        counter,
    )
    return S3PositiveControlResult(
        relation_polynomial=relation,
        m2=m2,
        root_product_remainder=remainder,
        gcd=common,
        compatible_roots=compatible,
    )


# Short constructor aliases keep experiment call sites readable.
build_f3 = semaev_f3
build_f3_fixed_x = semaev_f3_fixed_x
build_f4 = semaev_f4
build_f4_fixed_x = semaev_f4_fixed_x


__all__ = [
    "F4_DENOMINATOR_POWER",
    "Monomial",
    "OperationCounter",
    "S3PositiveControlResult",
    "SparsePolynomial",
    "UniPolynomial",
    "build_m2",
    "build_f3",
    "build_f3_fixed_x",
    "build_f4",
    "build_f4_fixed_x",
    "d2_root_product_mod_m2",
    "direct_factor_root_product",
    "direct_fixed_x_product",
    "eliminate_source_roots",
    "fp_add",
    "fp_inverse",
    "fp_is_zero",
    "fp_multiply",
    "fp_power",
    "fp_subtract",
    "gcd_roots_against_m2",
    "normalize_sparse",
    "quadratic_resultant",
    "s3_root_product_mod_m2",
    "s3_positive_control",
    "semaev_f3",
    "semaev_f3_fixed_x",
    "semaev_f3_from_polynomials",
    "semaev_f4",
    "semaev_f4_fixed_x",
    "source_denominator_scalar",
    "source_map_polynomials",
    "source_map_value",
    "source_map_values",
    "source_root_elimination",
    "sparse_add",
    "sparse_equal_up_to_scalar",
    "sparse_evaluate_one_variable",
    "sparse_from_univariate",
    "sparse_multiply",
    "sparse_power",
    "sparse_scalar_ratio",
    "sparse_scale",
    "sparse_subtract",
    "sparse_to_univariate",
    "substitute_identity_source",
    "substitute_mobius_source",
    "substitute_source_map",
    "substitute_square_source",
    "s4_root_product_mod_m2",
    "univariate_add",
    "univariate_divmod",
    "univariate_equal_up_to_scalar",
    "univariate_evaluate",
    "univariate_gcd",
    "univariate_mod",
    "univariate_monic",
    "univariate_multiply",
    "univariate_product_from_roots",
    "univariate_roots_from_disclosed",
    "univariate_scalar_ratio",
    "univariate_subtract",
    "univariate_trim",
]
