"""
curve.py -- short Weierstrass curve E: y^2 = x^3 + a*x + b over F_p (p > 3 prime),
affine-coordinate group law, and a Hasse-interval BSGS order-finding routine that
determines #E(F_p) exactly for a curve of prime order without Schoof/SEA.

Point representation: either None (point at infinity O) or a tuple (x, y) of ints
in [0, p).
"""
import math
from . import fp

O = None  # point at infinity


def on_curve(P, a, b, p):
    if P is None:
        return True
    x, y = P
    return (y * y - (x * x * x + a * x + b)) % p == 0


def neg(P, p):
    if P is None:
        return None
    x, y = P
    return (x, (-y) % p)


def add(P, Q, a, p):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2:
        if (y1 + y2) % p == 0:
            return None
        # doubling
        lam = ((3 * x1 * x1 + a) * fp.inv(2 * y1, p)) % p
    else:
        lam = ((y2 - y1) * fp.inv((x2 - x1) % p, p)) % p
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return (x3, y3)


def scalar_mul(k, P, a, p):
    if k < 0:
        return scalar_mul(-k, neg(P, p), a, p)
    R = None
    Q = P
    while k > 0:
        if k & 1:
            R = add(R, Q, a, p)
        Q = add(Q, Q, a, p)
        k >>= 1
    return R


def random_point(a, b, p, rng):
    """Random affine point on E via random x, rejection on non-residue."""
    while True:
        x = rng.randrange(p)
        rhs = (x * x * x + a * x + b) % p
        y = fp.sqrt_mod(rhs, p)
        if y is not None:
            return (x, y)


def isqrt(n):
    return math.isqrt(n)


def hasse_interval(p):
    s = isqrt(4 * p)
    while (s + 1) * (s + 1) <= 4 * p:
        s += 1
    lo = p + 1 - s
    hi = p + 1 + s
    return lo, hi


def _bsgs_order_in_interval(P, a, p, lo, hi, Qbase):
    """Find m in [lo,hi] with m*P = O, given Qbase = (something)*P already added in caller.
    Standard baby-step giant-step over an interval of width W=hi-lo:
      We search k in [0, W] such that (lo)*P + k*P = O, i.e. k*P = -(lo*P).
    Returns m = lo+k or None if not found in the interval.
    """
    W = hi - lo
    m = math.isqrt(W)
    m = max(m, 1) + 1
    # baby steps: j*P for j in [0,m]
    target = neg(scalar_mul(lo, P, a, p), p)  # want k*P = target
    baby = {}
    cur = None
    for j in range(m + 1):
        baby[cur] = j
        cur = add(cur, P, a, p)
    mP = scalar_mul(m, P, a, p)
    # giant steps: target - i*m*P for i in [0, W//m + 1]
    gamma = target
    for i in range(W // m + 2):
        if gamma in baby:
            k = i * m + baby[gamma]
            if 0 <= k <= W:
                return lo + k
        gamma = add(gamma, neg(mP, p), a, p)
    return None


def find_curve_order(a, b, p, rng, tries=6, agreement_needed=3):
    """Determine #E(F_p) exactly via the standard 'Hasse interval + BSGS on one point'
    trick (no Schoof/SEA needed).

    For a random point P, BSGS finds m in the Hasse interval [lo,hi] with m*P = O.
    By Lagrange, ord(P) | #E(F_p), and #E(F_p) itself lies in the Hasse interval
    (Hasse's theorem), so #E(F_p) is *a* valid witness m. m is the UNIQUE such witness
    whenever ord(P) exceeds the interval width W=hi-lo (only one multiple of ord(P) can
    fit in a window narrower than ord(P) itself) -- true for essentially all random
    points, since W = O(sqrt(p)) while ord(P) is typically Theta(p). We do NOT assume
    ord(P) == m (that need not hold if E(F_p) is non-cyclic); we instead require
    independent random points to agree on m, which is robust regardless of group
    structure and only fails if multiple random points coincidentally have anomalously
    small order (probability negligible at 40+ bit scale, and self-inconsistent
    agreement is itself checked, not assumed).

    Returns N (int) or None if it could not be pinned down within `tries` attempts.
    """
    lo, hi = hasse_interval(p)
    candidates = []
    for _ in range(tries):
        P = random_point(a, b, p, rng)
        m = _bsgs_order_in_interval(P, a, p, lo, hi, None)
        if m is None or m == 0:
            continue
        if scalar_mul(m, P, a, p) is not None:
            continue  # sanity: BSGS witness must itself satisfy m*P=O
        candidates.append(m)
        from collections import Counter
        c = Counter(candidates)
        val, cnt = c.most_common(1)[0]
        if cnt >= agreement_needed:
            return val
    return None


def _small_prime_factors(n):
    n = abs(n)
    factors = set()
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.add(d)
            n //= d
        d += 1
    if n > 1:
        factors.add(n)
    return factors
