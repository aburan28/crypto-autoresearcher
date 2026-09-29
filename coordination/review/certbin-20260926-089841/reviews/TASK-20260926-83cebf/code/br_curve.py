"""The curve E: Y^2 + XY = X^3 + A X^2 + B over F_2^17 and the summation
polynomial S_3, from the statement (EXP-CERTBIN-4e92d7 object.curve,
object.summation_polynomial; KN-TECH-b18366). Point arithmetic is the
standard affine chord-and-tangent law for this curve shape; S_3 is verified
against it in the self-test rather than assumed.
"""
from br_field import add, mul, sqr, inv, div, trace, half_trace

INF = None


def on_curve(P, A, B):
    if P is INF:
        return True
    x, y = P
    return (sqr(y) ^ mul(x, y)) == (mul(sqr(x), x) ^ mul(A, sqr(x)) ^ B)


def neg(P):
    if P is INF:
        return INF
    x, y = P
    return (x, x ^ y)


def padd(P, Q, A, B):
    if P is INF:
        return Q
    if Q is INF:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2:
        if y2 == (x1 ^ y1):
            # Q = -P (this includes the 2-torsion point x = 0)
            return INF
        # otherwise Q = P: doubling (x1 != 0 here)
        assert y1 == y2
        lam = x1 ^ div(y1, x1)
        x3 = sqr(lam) ^ lam ^ A
        y3 = sqr(x1) ^ mul(lam ^ 1, x3)
        return (x3, y3)
    lam = div(y1 ^ y2, x1 ^ x2)
    x3 = sqr(lam) ^ lam ^ x1 ^ x2 ^ A
    y3 = mul(lam, x1 ^ x3) ^ x3 ^ y1
    return (x3, y3)


def lift_x(x, A, B, sign=0):
    """A point with x-coordinate x, or None. For x != 0: y = x z with
    z^2 + z = x + A + B / x^2 (solvable iff the trace is 0)."""
    if x == 0:
        # y^2 = B -> y = sqrt(B) = B^{2^16}
        y = B
        for _ in range(16):
            y = sqr(y)
        return (0, y)
    c = x ^ A ^ div(B, sqr(x))
    if trace(c) != 0:
        return None
    z = half_trace(c) ^ (sign & 1)
    return (x, mul(x, z))


def S3(x1, x2, x3, B):
    """S_3(x1, x2, x3) = (x1 x2 + x1 x3 + x2 x3)^2 + x1 x2 x3 + B."""
    u = mul(x1, x2) ^ mul(x1, x3) ^ mul(x2, x3)
    return sqr(u) ^ mul(mul(x1, x2), x3) ^ B
