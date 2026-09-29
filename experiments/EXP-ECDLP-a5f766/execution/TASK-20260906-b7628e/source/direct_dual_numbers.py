"""Implementation D: direct dual-number arithmetic over F_p[eps]/eps^2.

No closed-form jet formula appears here; F = x^2 * A^{-1} is evaluated with
pair operations only. This module must not import coefficient_reference.
"""


class Dual:
    __slots__ = ("a", "b", "p")

    def __init__(self, a, b, p):
        self.p = p
        self.a = a % p
        self.b = b % p

    def __add__(self, other):
        return Dual(self.a + other.a, self.b + other.b, self.p)

    def __sub__(self, other):
        return Dual(self.a - other.a, self.b - other.b, self.p)

    def __mul__(self, other):
        return Dual(self.a * other.a,
                    self.a * other.b + self.b * other.a, self.p)

    def scale(self, k):
        return Dual(self.a * k, self.b * k, self.p)

    def pow_int(self, n):
        result = Dual(1, 0, self.p)
        base = self
        while n:
            if n & 1:
                result = result * base
            base = base * base
            n >>= 1
        return result

    def inverse(self):
        if self.a % self.p == 0:
            raise ZeroDivisionError("dual inverse requires invertible a0")
        a_inv = pow(self.a, -1, self.p)
        return Dual(a_inv, -(a_inv * a_inv) * self.b, self.p)

    def __eq__(self, other):
        return self.p == other.p and self.a == other.a and self.b == other.b

    def __repr__(self):
        return f"Dual({self.a},{self.b},p={self.p})"

    def to_tuple(self):
        return (self.a, self.b)


def gauge_action(p, u0, v, coeffs):
    """Active model action u = u0*(1+v*eps): x'=u^2 x, y'=u^3 y, A'=u^4 A, B'=u^6 B."""
    x0, x1, y0, y1, A0, A1, B0, B1 = coeffs
    u = Dual(u0, u0 * v, p)
    u2 = u.pow_int(2)
    u3 = u.pow_int(3)
    u4 = u.pow_int(4)
    u6 = u.pow_int(6)
    x = u2 * Dual(x0, x1, p)
    y = u3 * Dual(y0, y1, p)
    A = u4 * Dual(A0, A1, p)
    B = u6 * Dual(B0, B1, p)
    return (x.a, x.b, y.a, y.b, A.a, A.b, B.a, B.b)


def pullback(p, c, coeffs):
    """Parameter pullback eps -> c*eps on every first-order coefficient."""
    x0, x1, y0, y1, A0, A1, B0, B1 = coeffs
    return (x0, c * x1, y0, c * y1, A0, c * A1, B0, c * B1)


def F_jet(p, coeffs):
    """F = x^2/A by direct dual arithmetic; returns (F0, F1)."""
    x0, x1, _y0, _y1, A0, A1, _B0, _B1 = coeffs
    x = Dual(x0, x1, p)
    A = Dual(A0, A1, p)
    F = x.pow_int(2) * A.inverse()
    return (F.a, F.b)
