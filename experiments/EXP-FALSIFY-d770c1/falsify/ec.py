"""Short-Weierstrass curve arithmetic and Semaev summation polynomials over F_p."""

from . import fp


# --------------------------------------------------------------------- curve
def nonsingular(a, b, p):
    return (4 * a * a * a + 27 * b * b) % p != 0


def add_points(P, Q, a, p):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if P == Q:
        lam = (3 * x1 * x1 + a) * pow(2 * y1, p - 2, p) % p
    else:
        lam = (y2 - y1) * pow(x2 - x1, p - 2, p) % p
    x3 = (lam * lam - x1 - x2) % p
    return (x3, (lam * (x1 - x3) - y1) % p)


def negate(P, p):
    return None if P is None else (P[0], (-P[1]) % p)


def affine_points(a, b, p):
    """All affine points, by trial over y.  Toy scale only."""
    sq = {}
    for y in range(p):
        sq.setdefault(y * y % p, []).append(y)
    pts = []
    for x in range(p):
        r = (x * x * x + a * x + b) % p
        for y in sq.get(r, ()):
            pts.append((x, y))
    return pts


# ------------------------------------------------------------------- Semaev
def S3_in(u, v, a, b, p):
    """S3(u, v, X) as a quadratic in X, coefficients low degree first."""
    c2 = (u - v) ** 2 % p
    c1 = -2 * (((u + v) * ((u * v + a) % p)) % p + 2 * b) % p
    c0 = ((u * v - a) ** 2 - 4 * b * (u + v)) % p
    return fp.norm([c0, c1, c2], p)


def S3(x1, x2, x3, a, b, p):
    c = S3_in(x1, x2, a, b, p)
    return sum(ci * pow(x3, i, p) for i, ci in enumerate(c)) % p


def S4(x1, x2, x3, x4, a, b, p):
    """S4 = Res_X( S3(x1,x2,X), S3(x3,x4,X) ), or None on a degree drop.

    A degree drop happens exactly when x1 == x2 or x3 == x4, where the leading
    coefficient (u-v)^2 vanishes.  Returning None rather than a differently
    normalised resultant is what keeps interpolation honest.
    """
    f = S3_in(x1, x2, a, b, p)
    g = S3_in(x3, x4, a, b, p)
    if fp.deg(f) != 2 or fp.deg(g) != 2:
        return None
    return fp.resultant(f, g, p)


def S4_in(x1, x2, x3, a, b, p):
    """S4(x1, x2, x3, X) as a quartic in X, or None if any node degenerates."""
    xs, ys = list(range(5)), []
    for X in xs:
        v = S4(x1, x2, x3, X, a, b, p)
        if v is None:
            return None
        ys.append(v)
    return fp.interpolate(xs, ys, p)


def S5(x1, x2, x3, x4, x5, a, b, p):
    """S5 = Res_X( S4(x1,x2,x3,X), S3(x4,x5,X) ), or None on a degree drop."""
    f = S4_in(x1, x2, x3, a, b, p)
    if f is None:
        return None
    g = S3_in(x4, x5, a, b, p)
    if fp.deg(f) != 4 or fp.deg(g) != 2:
        return None
    return fp.resultant(f, g, p)


def summation_fibre(m, others, a, b, p):
    """The specialised summation polynomial as a univariate poly in x_1.

    `others` supplies x_2 ... x_m.  Returns None if any interpolation node
    degenerates, so that every returned polynomial comes from one consistent
    normalisation.  Degree is 2^(m-2) when defined.
    """
    if m == 4:
        nodes, ev = list(range(5)), lambda X: S4(X, *others, a, b, p)
    elif m == 5:
        nodes, ev = list(range(9)), lambda X: S5(X, *others, a, b, p)
    else:
        raise ValueError("m must be 4 or 5")
    ys = []
    for X in nodes:
        v = ev(X)
        if v is None:
            return None
        ys.append(v)
    return fp.interpolate(nodes, ys, p)
