"""Small exact statistics helpers (no scipy)."""
import math
from collections import Counter


def _log_binom_pmf(k, n, p):
    if p <= 0.0:
        return 0.0 if k == 0 else -math.inf
    if p >= 1.0:
        return 0.0 if k == n else -math.inf
    return (math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)
            + k * math.log(p) + (n - k) * math.log1p(-p))


def binom_cdf(k, n, p):
    """P(X <= k)."""
    if k < 0:
        return 0.0
    if k >= n:
        return 1.0
    return min(1.0, sum(math.exp(_log_binom_pmf(i, n, p)) for i in range(0, k + 1)))


def binom_sf(k, n, p):
    """P(X >= k)."""
    if k <= 0:
        return 1.0
    if k > n:
        return 0.0
    return min(1.0, sum(math.exp(_log_binom_pmf(i, n, p)) for i in range(k, n + 1)))


def _bisect(f, lo, hi, it=64):
    for _ in range(it):
        mid = (lo + hi) / 2
        if f(mid):
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def clopper_pearson(x, n, alpha=0.05):
    if n == 0:
        return None
    lo = 0.0 if x == 0 else _bisect(lambda p: binom_sf(x, n, p) >= alpha / 2, 0.0, 1.0)
    hi = 1.0 if x == n else _bisect(lambda p: binom_cdf(x, n, p) <= alpha / 2, 0.0, 1.0)
    return [lo, hi]


def wilson(x, n, z=1.959963984540054):
    if n == 0:
        return None
    ph = x / n
    den = 1 + z * z / n
    cen = (ph + z * z / (2 * n)) / den
    half = z * math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / den
    return [max(0.0, cen - half), min(1.0, cen + half)]


def binom_two_sided_interval(n, p, level=0.999):
    """Smallest lo, largest hi with P(X < lo) <= a/2 and P(X > hi) <= a/2."""
    a = (1 - level) / 2
    lo = 0
    while lo <= n and binom_cdf(lo, n, p) <= a:
        lo += 1
    hi = n
    while hi >= 0 and binom_sf(hi, n, p) <= a:
        hi -= 1
    return lo, hi


def entropy_bits(labels):
    c = Counter(labels)
    n = sum(c.values())
    if n == 0:
        return None, 0, 0, 0
    h = -sum((v / n) * math.log2(v / n) for v in c.values())
    return h, len(c), n, max(c.values())


def binary_entropy(p):
    if p <= 0 or p >= 1:
        return 0.0
    return -(p * math.log2(p) + (1 - p) * math.log2(1 - p))


def median(xs):
    xs = sorted(xs)
    n = len(xs)
    if n == 0:
        return None
    return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2


def mann_whitney(a, b):
    """Two-sided Mann-Whitney U with normal approximation and tie correction
    (descriptive)."""
    n1, n2 = len(a), len(b)
    if n1 == 0 or n2 == 0:
        return None
    allv = sorted([(v, 0) for v in a] + [(v, 1) for v in b])
    ranks = [0.0] * len(allv)
    i = 0
    ties = 0.0
    while i < len(allv):
        j = i
        while j + 1 < len(allv) and allv[j + 1][0] == allv[i][0]:
            j += 1
        r = (i + j) / 2 + 1
        for k in range(i, j + 1):
            ranks[k] = r
        t = j - i + 1
        ties += t ** 3 - t
        i = j + 1
    R1 = sum(r for r, (v, g) in zip(ranks, allv) if g == 0)
    U1 = R1 - n1 * (n1 + 1) / 2
    N = n1 + n2
    mu = n1 * n2 / 2
    var = n1 * n2 / 12 * ((N + 1) - ties / (N * (N - 1))) if N > 1 else 0
    if var <= 0:
        return {"U": U1, "n1": n1, "n2": n2, "z": None, "p_value": 1.0}
    z = (U1 - mu) / math.sqrt(var)
    p = math.erfc(abs(z) / math.sqrt(2))
    return {"U": U1, "n1": n1, "n2": n2, "z": z, "p_value": p}
