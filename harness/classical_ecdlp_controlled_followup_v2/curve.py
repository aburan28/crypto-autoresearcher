"""Small public-input affine arithmetic with an explicit operation ledger.

No discrete-log table or scalar ordering is available in this module. Field
inversion is counted as one inversion plus its Euclidean integer iterations;
its bit cost is not represented by one unit of machine time.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TypeAlias

Point: TypeAlias = tuple[int, int] | None


@dataclass
class Counter:
    counts: dict[str, int] = field(default_factory=dict)

    def tick(self, name: str, amount: int = 1) -> None:
        self.counts[name] = self.counts.get(name, 0) + amount

    def snapshot(self) -> dict[str, int]:
        return dict(sorted(self.counts.items()))


class Field:
    def __init__(self, p: int, counter: Counter):
        self.p, self.counter = p, counter

    def reduce(self, x: int) -> int:
        self.counter.tick("field_reduce")
        return x % self.p

    def add(self, x: int, y: int) -> int:
        self.counter.tick("field_add")
        return self.reduce(x + y)

    def sub(self, x: int, y: int) -> int:
        self.counter.tick("field_sub")
        return self.reduce(x - y)

    def neg(self, x: int) -> int:
        self.counter.tick("field_neg")
        return self.reduce(-x)

    def mul(self, x: int, y: int) -> int:
        self.counter.tick("field_mul")
        return self.reduce(x * y)

    def square(self, x: int) -> int:
        self.counter.tick("field_square")
        return self.reduce(x * x)

    def equal(self, x: int, y: int) -> bool:
        self.counter.tick("field_equal")
        return x == y

    def inverse(self, x: int) -> int:
        self.counter.tick("field_inverse")
        x = self.reduce(x)
        if self.equal(x, 0):
            self.counter.tick("exception_zero_inverse")
            raise ZeroDivisionError("zero field inverse")
        # Extended Euclid: recorded separately from field operation counts.
        old_r, rem, old_t, coeff = self.p, x, 0, 1
        while rem:
            self.counter.tick("inverse_euclid_iteration")
            quotient = old_r // rem
            old_r, rem = rem, old_r - quotient * rem
            old_t, coeff = coeff, old_t - quotient * coeff
        if old_r != 1:
            self.counter.tick("exception_noninvertible")
            raise ValueError("field modulus/input does not admit inverse")
        return self.reduce(old_t)

    def power(self, x: int, exponent: int) -> int:
        if exponent < 0:
            raise ValueError("negative exponent")
        self.counter.tick("field_power_call")
        value, factor = 1, self.reduce(x)
        while exponent:
            self.counter.tick("power_bit")
            if exponent & 1:
                value = self.mul(value, factor)
            exponent >>= 1
            if exponent:
                factor = self.square(factor)
        return value


class Curve:
    def __init__(self, p: int, a: int, b: int, counter: Counter | None = None):
        if p <= 3 or p % 2 == 0:
            raise ValueError("public characteristic must be odd and greater than 3")
        self.p, self.a, self.b = p, a % p, b % p
        self.counter = counter if counter is not None else Counter()
        self.f = Field(p, self.counter)

    def canonical(self, point: Point) -> bool:
        return point is None or (
            isinstance(point, tuple) and len(point) == 2
            and all(type(v) is int and 0 <= v < self.p for v in point)
        )

    def contains(self, point: Point) -> bool:
        self.counter.tick("point_membership_call")
        if not self.canonical(point):
            self.counter.tick("exception_noncanonical_point")
            return False
        if point is None:
            return True
        x, y = point
        rhs = self.f.add(self.f.add(self.f.mul(self.f.square(x), x), self.f.mul(self.a, x)), self.b)
        return self.f.equal(self.f.square(y), rhs)

    def equal(self, left: Point, right: Point) -> bool:
        self.counter.tick("point_equal")
        if left is None or right is None:
            return left is right
        return self.f.equal(left[0], right[0]) and self.f.equal(left[1], right[1])

    def negate(self, point: Point) -> Point:
        self.counter.tick("point_negate")
        return None if point is None else (point[0], self.f.neg(point[1]))

    def add_with_slope(self, left: Point, right: Point) -> tuple[Point, int]:
        """Return sum and normalized line coefficient, sharing one slope.

        Identity/vertical additions have coefficient zero, including order-two
        tangents. Inputs are checked at public constructor boundaries.
        """
        self.counter.tick("group_add_call")
        if left is None or right is None:
            self.counter.tick("exception_identity_addition")
            return (right if left is None else left), 0
        x1, y1 = left
        x2, y2 = right
        if self.f.equal(x1, x2):
            if self.f.equal(self.f.add(y1, y2), 0):
                self.counter.tick("exception_vertical_addition")
                return None, 0
            if not self.f.equal(y1, y2):
                raise ValueError("invalid same-abscissa inputs")
            self.counter.tick("group_double_nonvertical")
            numerator = self.f.add(self.f.mul(3, self.f.square(x1)), self.a)
            denominator = self.f.mul(2, y1)
        else:
            self.counter.tick("group_add_nonvertical")
            numerator = self.f.sub(y2, y1)
            denominator = self.f.sub(x2, x1)
        slope = self.f.mul(numerator, self.f.inverse(denominator))
        x3 = self.f.sub(self.f.sub(self.f.square(slope), x1), x2)
        y3 = self.f.sub(self.f.mul(slope, self.f.sub(x1, x3)), y1)
        return (x3, y3), slope

    def add(self, left: Point, right: Point) -> Point:
        return self.add_with_slope(left, right)[0]

    def multiply(self, point: Point, scalar: int) -> Point:
        """Public binary multiplication, including its final verification cost."""
        self.counter.tick("scalar_multiply_call")
        if scalar < 0:
            return self.multiply(self.negate(point), -scalar)
        result = None
        for bit in bin(scalar)[2:]:
            self.counter.tick("scalar_multiply_bit")
            result = self.add(result, result)
            if bit == "1":
                result = self.add(result, point)
        return result


def point_json(point: Point) -> list[int] | None:
    return None if point is None else list(point)


def point_from_json(value: object) -> Point:
    if value is None:
        return None
    if not isinstance(value, list) or len(value) != 2 or any(type(v) is not int for v in value):
        raise ValueError("point must be null or two integer coordinates")
    return value[0], value[1]


def certify_public_parameters(p: int, a: int, b: int, r: int) -> dict[str, int]:
    """Tiny-fixture certification, separate from evaluator asymptotic bounds.

    Trial division is deliberately explicit and separately charged. This is
    not proposed as an efficient general-purpose input certification routine.
    """
    counter = Counter()
    for value in (p, r):
        if type(value) is not int or value < 2:
            raise ValueError("nonprime public parameter")
        divisor = 2
        while divisor * divisor <= value:
            counter.tick("certification_trial_division")
            if value % divisor == 0:
                raise ValueError("nonprime public parameter")
            divisor += 1
    if p <= 3 or p % 4 != 3 or r <= 2 or r % 2 != 1 or r == p:
        raise ValueError("unsupported public domain")
    counter.tick("certification_discriminant_check")
    if (4 * a**3 + 27 * b**2) % p == 0:
        raise ValueError("singular curve")
    return counter.snapshot()
