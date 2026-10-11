#!/usr/bin/env python3
"""Independent (pure Python) arithmetic for EXP-GFPN-726eb2 certificate re-verification.

F_{p^5} = F_p[z]/(z^5 - 3), p = 2^64 - 2^32 + 1 (both frozen notes state this modulus).
Short Weierstrass curves y^2 = x^3 + a x + b over F_{p^5}, affine arithmetic.
An ECPP (Atkin-Morain) certificate verifier for PARI's primecert() output format.

Nothing here calls PARI; this is the "code independent of the solver" that
docs/claims-and-verification.md requires for re-verification.
"""
import math

P = 2**64 - 2**32 + 1
Q = P**5

# ---------------------------------------------------------------- F_{p^5}
class Fq:
    """Elements are 5-tuples of ints mod P: c0 + c1 z + ... + c4 z^4, z^5 = 3."""
    __slots__ = ("c",)
    def __init__(self, c):
        if isinstance(c, int):
            c = (c % P, 0, 0, 0, 0)
        self.c = tuple(x % P for x in c)
    def __eq__(self, o): return self.c == Fq.lift(o).c
    def __hash__(self): return hash(self.c)
    @staticmethod
    def lift(o): return o if isinstance(o, Fq) else Fq(o)
    def __add__(self, o): o = Fq.lift(o); return Fq(tuple(a + b for a, b in zip(self.c, o.c)))
    def __sub__(self, o): o = Fq.lift(o); return Fq(tuple(a - b for a, b in zip(self.c, o.c)))
    def __neg__(self): return Fq(tuple(-a for a in self.c))
    __radd__ = __add__
    def __rsub__(self, o): return Fq.lift(o) - self
    def __mul__(self, o):
        o = Fq.lift(o); a, b = self.c, o.c
        r = [0] * 9
        for i in range(5):
            if a[i]:
                for j in range(5):
                    r[i + j] += a[i] * b[j]
        # z^5 = 3, z^6 = 3z, ... z^8 = 3 z^3
        return Fq((r[0] + 3 * r[5], r[1] + 3 * r[6], r[2] + 3 * r[7], r[3] + 3 * r[8], r[4]))
    __rmul__ = __mul__
    def is_zero(self): return all(x == 0 for x in self.c)
    def __pow__(self, e):
        r, b = Fq(1), self
        e = int(e)
        if e < 0:
            b = b.inv(); e = -e
        while e:
            if e & 1: r = r * b
            b = b * b; e >>= 1
        return r
    def inv(self):
        # F_q^* has order q-1
        return self ** (Q - 2)
    def __truediv__(self, o): return self * Fq.lift(o).inv()
    def is_square(self):
        if self.is_zero(): return True
        return (self ** ((Q - 1) // 2)) == Fq(1)
    def sqrt(self):
        """Tonelli-Shanks in F_q (q-1 = 2^s * t)."""
        if self.is_zero(): return Fq(0)
        if not self.is_square(): return None
        s, t = 0, Q - 1
        while t % 2 == 0: s += 1; t //= 2
        # find non-residue: z itself? test small candidates
        for cand in [Fq((0, 1, 0, 0, 0)), Fq((1, 1, 0, 0, 0)), Fq(2), Fq(3), Fq(5), Fq(7), Fq((2, 1, 0, 0, 0))]:
            if not cand.is_square(): nr = cand; break
        c = nr ** t
        r = self ** ((t + 1) // 2)
        x = self ** t
        m = s
        while not x == Fq(1):
            # find least i with x^(2^i) = 1
            i, y = 0, x
            while not y == Fq(1):
                y = y * y; i += 1
            b = c ** (2 ** (m - i - 1))
            r = r * b; c = b * b; x = x * c; m = i
        assert r * r == self
        return r
    def __repr__(self):
        return "Fq" + str(self.c)

# ---------------------------------------------------------------- curve over F_q
INF = None

def on_curve(a, b, Pt):
    if Pt is INF: return True
    x, y = Pt
    return y * y == x * x * x + a * x + b

def ec_add(a, Pt, Qt):
    if Pt is INF: return Qt
    if Qt is INF: return Pt
    x1, y1 = Pt; x2, y2 = Qt
    if x1 == x2:
        if (y1 + y2).is_zero(): return INF
        lam = (3 * x1 * x1 + a) / (2 * y1)
    else:
        lam = (y2 - y1) / (x2 - x1)
    x3 = lam * lam - x1 - x2
    y3 = lam * (x1 - x3) - y1
    return (x3, y3)

def ec_mul(a, k, Pt):
    """Double-and-add with affine coordinates (inversions via q-2 power: slow but independent)."""
    R = INF
    for bit in bin(int(k))[2:]:
        R = ec_add(a, R, R)
        if bit == "1": R = ec_add(a, R, Pt)
    return R

# ------------------------------------------------ projective (Jacobian) for speed, same math
def jac_add(a, P1, P2):
    if P1 is INF: return P2
    if P2 is INF: return P1
    X1, Y1, Z1 = P1; X2, Y2, Z2 = P2
    Z1Z1 = Z1 * Z1; Z2Z2 = Z2 * Z2
    U1 = X1 * Z2Z2; U2 = X2 * Z1Z1
    S1 = Y1 * Z2 * Z2Z2; S2 = Y2 * Z1 * Z1Z1
    if U1 == U2:
        if not S1 == S2: return INF
        return jac_dbl(a, P1)
    H = U2 - U1; R = S2 - S1
    HH = H * H; HHH = HH * H
    V = U1 * HH
    X3 = R * R - HHH - 2 * V
    Y3 = R * (V - X3) - S1 * HHH
    Z3 = Z1 * Z2 * H
    return (X3, Y3, Z3)

def jac_dbl(a, P1):
    if P1 is INF: return INF
    X1, Y1, Z1 = P1
    if Y1.is_zero(): return INF
    XX = X1 * X1; YY = Y1 * Y1; YYYY = YY * YY; ZZ = Z1 * Z1
    S = 2 * ((X1 + YY) * (X1 + YY) - XX - YYYY)
    M = 3 * XX + a * ZZ * ZZ
    X3 = M * M - 2 * S
    Y3 = M * (S - X3) - 8 * YYYY
    Z3 = (Y1 + Z1) * (Y1 + Z1) - YY - ZZ
    return (X3, Y3, Z3)

def jac_mul(a, k, Pt):
    if Pt is INF: return INF
    R = INF; B = (Pt[0], Pt[1], Fq(1))
    for bit in bin(int(k))[2:]:
        R = jac_dbl(a, R)
        if bit == "1": R = jac_add(a, R, B)
    return R

def jac_to_affine(Pt):
    if Pt is INF: return INF
    X, Y, Z = Pt
    if Z.is_zero(): return INF
    zi = Z.inv(); zi2 = zi * zi
    return (X * zi2, Y * zi2 * zi)

def mul(a, k, Pt):
    return jac_to_affine(jac_mul(a, k, Pt))

# ---------------------------------------------------------------- integer helpers
def isqrt(n): return math.isqrt(n)

def hasse_interval(q):
    s = isqrt(4 * q)  # floor(2 sqrt q); 4q = 4 p^5 is not a perfect square
    return q + 1 - s, q + 1 + s

def multiples_in_hasse(q, N):
    lo, hi = hasse_interval(q)
    return [k * N for k in range(lo // N, hi // N + 2) if lo <= k * N <= hi]

def small_primes(B):
    sieve = bytearray([1]) * (B + 1); sieve[0:2] = b"\x00\x00"
    for i in range(2, isqrt(B) + 1):
        if sieve[i]: sieve[i*i::i] = bytearray(len(sieve[i*i::i]))
    return [i for i in range(B + 1) if sieve[i]]

def miller_rabin(n, bases=(2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)):
    if n < 2: return False
    for sp in bases:
        if n % sp == 0: return n == sp
    d, s = n - 1, 0
    while d % 2 == 0: d //= 2; s += 1
    for a in bases:
        x = pow(a, d, n)
        if x in (1, n - 1): continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1: break
        else: return False
    return True

# ---------------------------------------------------------------- ECPP verifier (PARI primecert format)
def _ec_mod_n_mul(k, Pt, a, n):
    """Scalar multiplication on y^2 = x^3 + a x + b over Z/nZ, projective (X:Y:Z).
    Returns (X, Y, Z) with Z possibly non-invertible; caller inspects gcd(Z, n)."""
    def add(P1, P2):
        if P1 is None: return P2
        if P2 is None: return P1
        X1, Y1, Z1 = P1; X2, Y2, Z2 = P2
        U1 = X1 * Z2 % n; U2 = X2 * Z1 % n
        S1 = Y1 * Z2 % n; S2 = Y2 * Z1 % n
        if U1 == U2:
            if (S1 + S2) % n == 0: return None
            return dbl(P1)
        H = (U2 - U1) % n; R = (S2 - S1) % n
        W = Z1 * Z2 % n
        HH = H * H % n; HHH = HH * H % n
        V = U1 * HH % n
        A = (R * R * W - HHH - 2 * V) % n
        X3 = H * A % n
        Y3 = (R * (V - A) - S1 * HHH) % n
        Z3 = HHH * W % n
        return (X3, Y3, Z3)
    def dbl(P1):
        if P1 is None: return None
        X1, Y1, Z1 = P1
        if Y1 % n == 0: return None
        W = (a * Z1 * Z1 + 3 * X1 * X1) % n
        S = Y1 * Z1 % n
        B = X1 * Y1 * S % n
        H = (W * W - 8 * B) % n
        X3 = 2 * H * S % n
        Y3 = (W * (4 * B - H) - 8 * Y1 * Y1 * S * S) % n
        Z3 = 8 * S * S * S % n
        return (X3, Y3, Z3)
    R = None
    for bit in bin(int(k))[2:]:
        R = dbl(R)
        if bit == "1": R = add(R, Pt)
    return R

def verify_ecpp(cert, small_prime_bound=2**64):
    """Verify a PARI primecert() certificate (list of [N, t, s, a, P] rows) with
    the Atkin-Goldwasser-Kilian-Morain criterion.  Returns (ok, detail)."""
    detail = []
    if isinstance(cert, int):
        # PARI returns a small prime as the certificate itself (or 0/1 style); treat as trial-division proof
        return (cert < small_prime_bound and _trial_prime(cert)), [f"terminal small prime {cert}"]
    prev_q = None
    for row in cert:
        N, t, s, a, Pt = int(row[0]), int(row[1]), int(row[2]), int(row[3]), [int(row[4][0]), int(row[4][1])]
        if prev_q is not None and N != prev_q:
            return False, detail + [f"chain break: expected {prev_q}, row has {N}"]
        m = N + 1 - t
        if m % s != 0: return False, detail + [f"s does not divide m at N={N}"]
        qn = m // s
        # Hasse bound sanity on t
        if t * t > 4 * N: return False, detail + [f"|t| > 2 sqrt(N) at N={N}"]
        # q > (N^{1/4} + 1)^2
        r4 = _iroot4(N)
        if not (qn > (r4 + 1) ** 2): return False, detail + [f"q not > (N^(1/4)+1)^2 at N={N}"]
        x, y = Pt
        b = (y * y - x * x * x - a * x) % N
        disc = (4 * a * a * a + 27 * b * b) % N
        if math.gcd(disc, N) != 1: return False, detail + [f"singular curve mod N={N}"]
        if math.gcd(N, 6) != 1: return False, detail + [f"N shares factor with 6: {N}"]
        # [m]P = O and [s]P != O (with Z-coordinate gcd checks)
        sP = _ec_mod_n_mul(s, (x, y, 1), a, N)
        if sP is None: return False, detail + [f"[s]P = O at N={N}"]
        g = math.gcd(sP[2], N)
        if g != 1: return False, detail + [f"gcd(Z([s]P), N) = {g} at N={N}"]
        mP = _ec_mod_n_mul(qn, sP, a, N)
        if mP is not None and math.gcd(mP[2], N) == 1:
            return False, detail + [f"[m]P != O at N={N}"]
        detail.append(f"N={N.bit_length()}-bit ok, q={qn.bit_length()}-bit")
        prev_q = qn
    # terminal prime must be verified by trial division
    if prev_q is None: return False, ["empty certificate"]
    if prev_q >= small_prime_bound or not _trial_prime(prev_q):
        return False, detail + [f"terminal q={prev_q} not verified by trial division"]
    detail.append(f"terminal prime {prev_q} verified by trial division")
    return True, detail

def _iroot4(n):
    r = isqrt(isqrt(n))
    while (r + 1) ** 4 <= n: r += 1
    while r ** 4 > n: r -= 1
    return r

def _trial_prime(n):
    """Terminal-prime check for q <= 2^64: trial division below 2^40, otherwise
    deterministic Miller-Rabin with the first 13 prime bases, proven correct for
    all n < 3,317,044,064,679,887,385,961,981 > 2^64 (Sorenson-Webster 2015)."""
    if n < 2: return False
    if n < 2**40:
        i = 2
        while i * i <= n:
            if n % i == 0: return False
            i += 1
        return True
    assert n < 3317044064679887385961981
    return miller_rabin(n, bases=(2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41))

if __name__ == "__main__":
    # self-test: field axioms and curve group law on random elements
    import random
    random.seed(1)
    a = Fq([random.randrange(P) for _ in range(5)]); b = Fq([random.randrange(P) for _ in range(5)])
    c = Fq([random.randrange(P) for _ in range(5)])
    assert (a * b) * c == a * (b * c) and a * (b + c) == a * b + a * c
    assert (a * a.inv()) == Fq(1)
    assert (a ** (Q - 1)) == Fq(1)
    s = (a * a).sqrt(); assert s == a or s == -a
    print("gfpn_arith self-test ok")
