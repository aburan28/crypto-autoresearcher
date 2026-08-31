"""Pure-Python F_p arithmetic and elliptic-curve group law helpers.
Identical in content to EXP-MONO-c819ba's fields.py (unchanged arithmetic
core; this contract's own domain/seeds are carried in seed.py/curve.py)."""


def legendre(a: int, p: int) -> int:
    a %= p
    if a == 0:
        return 0
    r = pow(a, (p - 1) // 2, p)
    return -1 if r == p - 1 else r


def build_sqrt_table(p: int):
    """table[q] = smallest a in [0,p) with a*a % p == q, for every QR q (incl. 0)."""
    table = {}
    for a in range(0, (p + 1) // 2 + 1):
        q = (a * a) % p
        if q not in table:
            table[q] = a
    return table


def ec_add(P, Q, A, p):
    """Standard affine chord-and-tangent addition on y^2 = x^3 + A x + B over F_p.
    P, Q are None (point at infinity) or (x, y) int pairs. B does not appear."""
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2:
        if (y1 + y2) % p == 0:
            return None
        lam = ((3 * x1 * x1 + A) * pow(2 * y1, p - 2, p)) % p
    else:
        lam = ((y2 - y1) * pow((x2 - x1) % p, p - 2, p)) % p
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return (x3, y3)


def ec_neg(P, p):
    if P is None:
        return None
    x, y = P
    return (x, (-y) % p)


def ec_scal(k, P, A, p):
    """Double-and-add scalar multiplication."""
    if k < 0:
        return ec_scal(-k, ec_neg(P, p), A, p)
    R = None
    Q = P
    while k > 0:
        if k & 1:
            R = ec_add(R, Q, A, p)
        Q = ec_add(Q, Q, A, p)
        k >>= 1
    return R


def factorize(n: int):
    """Trial-division factorization; n is at most a few thousand here."""
    factors = []
    d = 2
    m = n
    while d * d <= m:
        if m % d == 0:
            e = 0
            while m % d == 0:
                m //= d
                e += 1
            factors.append((d, e))
        d += 1 if d == 2 else 2
    if m > 1:
        factors.append((m, 1))
    return factors
