"""F_{2^19} and the binary curve, written from the specification text alone.

F_{2^19} = F_2[t]/(t^19 + t^5 + t^2 + t + 1); an element is a 19-bit integer,
bit j = coefficient of t^j (blind-inputs.json field.encoding).
E: Y^2 + XY = X^3 + A X^2 + B over F_{2^19} (specification object.curve).

TASK-20260926-f0736e.  numpy only; nothing from crypto_autoresearcher.
"""
import numpy as np

N = 19
MOD = (1 << 19) | (1 << 5) | (1 << 2) | (1 << 1) | 1  # 524327
MASK = (1 << N) - 1
ORDER_MULT = (1 << N) - 1  # 524287


def clmul(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        a <<= 1
        b >>= 1
    return r


def polymod(a, m):
    dm = m.bit_length() - 1
    while a.bit_length() - 1 >= dm and a:
        a ^= m << (a.bit_length() - 1 - dm)
    return a


def mul(a, b):
    return polymod(clmul(a, b), MOD)


def sq(a):
    return mul(a, a)


def power(a, e):
    r = 1
    while e:
        if e & 1:
            r = mul(r, a)
        a = mul(a, a)
        e >>= 1
    return r


def inv(a):
    if a == 0:
        raise ZeroDivisionError("inverse of 0 in F_{2^19}")
    return power(a, ORDER_MULT - 1)


def poly_gcd(a, b):
    while b:
        a, b = b, polymod(a, b)
    return a


def irreducibility_report(f=MOD):
    """Rabin/Ben-Or style: t^{2^n} = t mod f and gcd(t^{2^i} - t, f) = 1 for
    i = 1..floor(n/2)."""
    n = f.bit_length() - 1
    x = 2  # the polynomial t
    cur = x
    gcds = {}
    for i in range(1, n + 1):
        cur = polymod(clmul(cur, cur), f)  # t^{2^i}
        if i <= n // 2:
            gcds[i] = poly_gcd(f, cur ^ x)
    frob_ok = (cur == x)
    ok = frob_ok and all(g == 1 for g in gcds.values())
    return {"t^(2^n) == t mod f": frob_ok,
            "gcd(t^(2^i)-t, f) for i=1..%d" % (n // 2): {str(k): v for k, v in gcds.items()},
            "irreducible": ok}


# Trace: Tr(y) = sum_{i<19} y^{2^i}; linear, so Tr(y) = parity(y & TAU_MASK).
def _trace_scalar(y):
    s = 0
    z = y
    for _ in range(N):
        s ^= z
        z = sq(z)
    assert s in (0, 1), s
    return s


TAU = [_trace_scalar(1 << j) for j in range(N)]
TAU_MASK = sum(1 << j for j in range(N) if TAU[j])


def tr(y):
    return bin(y & TAU_MASK).count("1") & 1


def half_trace(y):
    """For odd n: HT(y) = sum_{i=0}^{(n-1)/2} y^{4^i}; HT^2 + HT = y + Tr(y)."""
    s = 0
    z = y
    for _ in range((N - 1) // 2 + 1):
        s ^= z
        z = sq(sq(z))
    return s


def sqrt(y):
    return power(y, 1 << (N - 1))


# ---- vectorised arithmetic via log/antilog tables (t generates F^*: 2^19 - 1
# is prime, and t != 1) -------------------------------------------------------
_EXP = None
_LOG = None


def tables():
    global _EXP, _LOG
    if _EXP is None:
        exp = np.zeros(2 * ORDER_MULT, dtype=np.int64)
        x = 1
        for i in range(ORDER_MULT):
            exp[i] = x
            x <<= 1
            if x >> N:
                x ^= MOD
        assert x == 1, "t does not have order 2^19 - 1"
        exp[ORDER_MULT:] = exp[:ORDER_MULT]
        log = np.full(1 << N, -1, dtype=np.int64)
        log[exp[:ORDER_MULT]] = np.arange(ORDER_MULT)
        assert (log[1:] >= 0).all()
        _EXP, _LOG = exp, log
    return _EXP, _LOG


def vmul(a, b):
    exp, log = tables()
    a = np.asarray(a, dtype=np.int64)
    b = np.asarray(b, dtype=np.int64)
    z = (a == 0) | (b == 0)
    la = np.where(z, 0, log[np.where(z, 1, a)])
    lb = np.where(z, 0, log[np.where(z, 1, b)])
    r = exp[(la + lb) % ORDER_MULT]
    return np.where(z, 0, r)


def vsq(a):
    return vmul(a, a)


def vinv(a):
    exp, log = tables()
    a = np.asarray(a, dtype=np.int64)
    if (a == 0).any():
        raise ZeroDivisionError
    return exp[(-log[a]) % ORDER_MULT]


def vtr(y):
    y = np.asarray(y, dtype=np.int64)
    return (np.bitwise_count((y & TAU_MASK).astype(np.uint64)) & 1).astype(np.int64)


def vhalf_trace(y):
    y = np.asarray(y, dtype=np.int64)
    s = np.zeros_like(y)
    z = y.copy()
    for _ in range((N - 1) // 2 + 1):
        s ^= z
        z = vsq(vsq(z))
    return s


# ---- curve ------------------------------------------------------------------
class Curve:
    def __init__(self, A, B):
        self.A = A
        self.B = B

    def on_curve(self, P):
        if P is None:
            return True
        x, y = P
        return (sq(y) ^ mul(x, y)) == (mul(sq(x), x) ^ mul(self.A, sq(x)) ^ self.B)

    def neg(self, P):
        if P is None:
            return None
        x, y = P
        return (x, x ^ y)

    def add(self, P, Q):
        if P is None:
            return Q
        if Q is None:
            return P
        x1, y1 = P
        x2, y2 = Q
        if x1 == x2:
            if y1 == y2 and x1 != 0:
                return self.dbl(P)
            return None  # Q = -P (including the 2-torsion point x = 0)
        lam = mul(y1 ^ y2, inv(x1 ^ x2))
        x3 = sq(lam) ^ lam ^ x1 ^ x2 ^ self.A
        y3 = mul(lam, x1 ^ x3) ^ x3 ^ y1
        return (x3, y3)

    def dbl(self, P):
        if P is None:
            return None
        x1, y1 = P
        if x1 == 0:
            return None
        lam = x1 ^ mul(y1, inv(x1))
        x3 = sq(lam) ^ lam ^ self.A
        y3 = sq(x1) ^ mul(lam ^ 1, x3)
        return (x3, y3)

    def smul(self, k, P):
        R = None
        Q = P
        while k:
            if k & 1:
                R = self.add(R, Q)
            Q = self.dbl(Q)
            k >>= 1
        return R

    def lift(self, x):
        """Return a point with x-coordinate x, or None if none exists."""
        if x == 0:
            return (0, sqrt(self.B))
        rhs = x ^ self.A ^ mul(self.B, inv(sq(x)))  # z^2 + z = x + A + B/x^2
        if tr(rhs):
            return None
        z = half_trace(rhs)
        return (x, mul(x, z))


def S3(x1, x2, x3, B):
    """S_3(x1,x2,x3) = (x1x2 + x1x3 + x2x3)^2 + x1x2x3 + B (KN-TECH-b18366)."""
    u = mul(x1, x2) ^ mul(x1, x3) ^ mul(x2, x3)
    return sq(u) ^ mul(mul(x1, x2), x3) ^ B
