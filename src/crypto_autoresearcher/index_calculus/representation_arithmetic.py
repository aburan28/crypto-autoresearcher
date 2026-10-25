"""Exact toy elliptic-curve arithmetic; deliberately not production crypto.

The finite-field implementation uses affine formulas. The lift implementation
uses the independent Renes--Costello--Batina projective addition formulas,
Algorithm 1, https://hyperelliptic.org/EFD/g1p/auto-shortw-projective.html.
Lifts are restricted to curves with prime order over F_p, p >= 11, and
precision 2..4. These restrictions make the formulas complete on reduction and
make log_E(t) == t modulo p**precision on the formal kernel.
"""

from dataclasses import dataclass
from functools import cached_property
from math import isqrt

Point = tuple[int, int] | None
Projective = tuple[int, int, int]
IDENTITY: Projective = (0, 1, 0)


def is_prime(n: int) -> bool:
    """Trial division is appropriate only for the small experimental fields."""
    return n >= 2 and all(n % d for d in range(2, isqrt(n) + 1))


@dataclass(frozen=True)
class Curve:
    p: int
    a: int
    b: int

    def __post_init__(self):
        if not is_prime(self.p) or self.p < 11 or self.p > 10000:
            raise ValueError("Use a prime field with 11 <= p <= 10000")
        object.__setattr__(self, "a", self.a % self.p)
        object.__setattr__(self, "b", self.b % self.p)
        if (4 * self.a**3 + 27 * self.b**2) % self.p == 0:
            raise ValueError("Singular curve")

    def contains(self, point: Point) -> bool:
        if point is None:
            return True
        x, y = point
        return (y*y - x*x*x - self.a*x - self.b) % self.p == 0

    def neg(self, point: Point) -> Point:
        return None if point is None else (point[0], -point[1] % self.p)

    def add(self, left: Point, right: Point) -> Point:
        if left is None:
            return right
        if right is None:
            return left
        x, y = left
        u, v = right
        if x == u:
            if (y + v) % self.p == 0:
                return None
            slope = (3*x*x + self.a) * pow(2*y, -1, self.p) % self.p
        else:
            slope = (v-y) * pow(u-x, -1, self.p) % self.p
        z = (slope*slope - x-u) % self.p
        return z, (slope*(x-z)-y) % self.p

    def mul(self, scalar: int, point: Point) -> Point:
        if scalar < 0:
            return self.mul(-scalar, self.neg(point))
        result = None
        while scalar:
            if scalar & 1:
                result = self.add(result, point)
            point = self.add(point, point)
            scalar >>= 1
        return result

    @cached_property
    def points(self) -> tuple[Point, ...]:
        roots: dict[int, list[int]] = {}
        for y in range(self.p):
            roots.setdefault(y*y % self.p, []).append(y)
        return (None,) + tuple(
            (x, y) for x in range(self.p)
            for y in roots.get((x*x*x + self.a*x + self.b) % self.p, ())
        )

    @property
    def order(self) -> int:
        return len(self.points)

    @property
    def generator(self) -> Point:
        if not is_prime(self.order):
            raise ValueError("This experiment requires a prime-order curve")
        return self.points[1]

    def scaled(self, u: int) -> "Curve":
        if u % self.p == 0:
            raise ValueError("An isomorphism requires u != 0")
        return Curve(self.p, self.a * pow(u, 4, self.p),
                     self.b * pow(u, 6, self.p))

    def transport(self, point: Point, u: int) -> Point:
        if u % self.p == 0:
            raise ValueError("An isomorphism requires u != 0")
        return None if point is None else (
            point[0] * u*u % self.p, point[1] * u*u*u % self.p
        )


def ordinary_curve(p: int = 1019) -> Curve:
    for b in range(1, p):
        try:
            curve = Curve(p, 2, b)
        except ValueError:
            continue
        if curve.order != p and is_prime(curve.order):
            return curve
    raise ValueError("No ordinary prime-order fixture found")


class Lift:
    """A nested, reproducible section into E(Z/p^N Z), not a homomorphism.

    Curve coefficients are fixed integer lifts, independently of the points.
    Point x coordinates use x + p*x_shift. The y coordinate is Hensel lifted
    from the original sign. Varying either shift changes only public choices.
    """

    def __init__(self, curve: Curve, precision=3, curve_shift=0, x_shift=0):
        if precision not in (2, 3, 4):
            raise ValueError("Formal-log truncation supports precision 2, 3, 4")
        if not is_prime(curve.order):
            raise ValueError("Complete lift arithmetic requires prime-order reduction")
        self.curve = curve
        self.p = curve.p
        self.precision = precision
        self.modulus = self.p**precision
        self.a = curve.a + self.p*curve_shift
        self.b = curve.b + self.p*(2*curve_shift+1)
        self.x_shift = x_shift

    def add(self, left: Projective, right: Projective) -> Projective:
        """RCB Algorithm 1 in ordinary projective coordinates (X:Y:Z)."""
        x, y, z = left
        u, v, w = right
        m, a, b3 = self.modulus, self.a, 3*self.b
        t0, t1, t2 = x*u % m, y*v % m, z*w % m
        t3 = ((x+y)*(u+v)-t0-t1) % m
        t4 = ((x+z)*(u+w)-t0-t2) % m
        t5 = ((y+z)*(v+w)-t1-t2) % m
        zz = (a*t4+b3*t2) % m
        xx = (t1-zz) % m
        zz = (t1+zz) % m
        yy = xx*zz % m
        t1 = (3*t0+a*t2) % m
        t4 = (b3*t4+a*(t0-a*t2)) % m
        yy = (yy+t1*t4) % m
        xx = (t3*xx-t5*t4) % m
        zz = (t5*zz+t3*t1) % m
        return xx, yy, zz

    def neg(self, point: Projective) -> Projective:
        x, y, z = point
        return x, -y % self.modulus, z

    def mul(self, scalar: int, point: Projective) -> Projective:
        if scalar < 0:
            return self.mul(-scalar, self.neg(point))
        result = IDENTITY
        while scalar:
            if scalar & 1:
                result = self.add(result, point)
            point = self.add(point, point)
            scalar >>= 1
        return result

    def equal(self, left: Projective, right: Projective) -> bool:
        # Primitivity is essential over a ring: the zero triple is not a point.
        self.validate(left)
        self.validate(right)
        return all((left[i]*right[j]-left[j]*right[i]) % self.modulus == 0
                   for i, j in ((0, 1), (0, 2), (1, 2)))

    def validate(self, point: Projective):
        x, y, z = point
        if all(c % self.p == 0 for c in point):
            raise ArithmeticError("Non-primitive projective triple")
        if (y*y*z-x*x*x-self.a*x*z*z-self.b*z*z*z) % self.modulus:
            raise ArithmeticError("Point left the lifted curve")

    def reduce(self, point: Projective) -> Point:
        self.validate(point)
        x, y, z = (c % self.p for c in point)
        if z == 0:
            if x != 0:
                raise ArithmeticError("Invalid point at infinity")
            return None
        return x * pow(z, -1, self.p) % self.p, y * pow(z, -1, self.p) % self.p

    def point(self, point: Point) -> Projective:
        if point is None:
            return IDENTITY
        if not self.curve.contains(point):
            raise ValueError("Point does not belong to the reduction curve")
        x, y = point
        x += self.p*self.x_shift
        rhs = x*x*x+self.a*x+self.b
        for exponent in range(2, self.precision+1):
            modulus = self.p**exponent
            y = (y-(y*y-rhs)*pow(2*y, -1, modulus)) % modulus
        result = x % self.modulus, y, 1
        self.validate(result)
        return result

    def torsion_point(self, point: Point) -> Projective:
        """Public prime-to-p splitting: a valid homomorphic lift with zero log."""
        r = self.curve.order
        if r == self.p:
            raise ValueError("Prime-to-p torsion splitting requires r != p")
        kernel_exponent = self.p**(self.precision-1)
        multiplier = kernel_exponent * pow(kernel_exponent, -1, r)
        return self.mul(multiplier, self.point(point))

    def formal_log(self, point: Projective) -> int:
        """Return log_E(-X/Y) mod p^N, only for points reducing to O.

        For short Weierstrass models log(t)=t+(2a/5)t^5+..., so t suffices
        at the supported N <= 4 and p >= 11. No division by a non-unit Z.
        """
        if self.reduce(point) is not None:
            raise ValueError("Formal log requires reduction to the identity")
        x, y, _ = point
        value = -x * pow(y, -1, self.modulus) % self.modulus
        if value % self.p:
            raise ArithmeticError("Formal parameter is outside p Z_p")
        return value

    def normalized_log(self, point: Projective) -> int:
        return self.formal_log(point) // self.p

    def first_digit(self, point: Point, torsion=False) -> int:
        section = self.torsion_point if torsion else self.point
        killed = self.mul(self.curve.order, section(point))
        return self.normalized_log(killed) % self.p


def solve_mod(rows: list[list[int]], values: list[int], modulus: int,
              columns: int | None = None) -> tuple[list[int] | None, int]:
    """Gaussian elimination over F_modulus, including inconsistency detection."""
    if not is_prime(modulus):
        raise ValueError("Elimination requires a prime modulus")
    if len(rows) != len(values):
        raise ValueError("Row/value count mismatch")
    width = columns if columns is not None else (len(rows[0]) if rows else 0)
    if any(len(row) != width for row in rows):
        raise ValueError("Ragged matrix")
    matrix = [[v % modulus for v in row]+[value % modulus]
              for row, value in zip(rows, values)]
    pivots = []
    for col in range(width):
        pivot = next((i for i in range(len(pivots), len(matrix))
                      if matrix[i][col]), None)
        if pivot is None:
            continue
        row = len(pivots)
        matrix[row], matrix[pivot] = matrix[pivot], matrix[row]
        inv = pow(matrix[row][col], -1, modulus)
        matrix[row] = [v*inv % modulus for v in matrix[row]]
        for i in range(len(matrix)):
            if i != row:
                multiple = matrix[i][col]
                matrix[i] = [(v-multiple*w) % modulus
                             for v, w in zip(matrix[i], matrix[row])]
        pivots.append(col)
    if any(not any(row[:width]) and row[-1] for row in matrix):
        return None, len(pivots)
    result = [0]*width
    for row, col in enumerate(pivots):
        result[col] = matrix[row][-1]
    return result, len(pivots)
