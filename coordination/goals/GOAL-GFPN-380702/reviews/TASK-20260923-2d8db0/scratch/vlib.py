#!/usr/bin/env python3
"""Validator's independent instrument for TASK-20260923-2d8db0 (EXP-GFPN-726eb2 review).

Written from scratch in this review session. Imports NOTHING from the producer's
experiments/EXP-GFPN-726eb2/implementation/ (gfpn_arith.py, gfpn_audit.py, ...)
and calls no PARI function for any VERIFICATION step.

Two independent field/curve implementations:
  PRIMARY   F_{p^5} = F_p[z]/(z^5 - 3) via python-flint (FLINT fq_default, the
            modulus passed explicitly), with an AFFINE group law for the general
            Weierstrass form y^2 = x^3 + a2 x^2 + a4 x + a6 written here.
  SECONDARY F_{p^5} as 5-tuples of Python ints (schoolbook multiplication with
            z^5 = 3, written here), with a HOMOGENEOUS-PROJECTIVE group law for the
            short Weierstrass form y^2 = x^3 + A x + B written here.
Different field code, different coordinates, different curve model where a
double-odd model is involved, so a bug has to be duplicated to survive both.

Also here: an ECPP (Goldwasser-Kilian / Atkin-Morain) chain checker for PARI's
primecert row format [N, t, s, a4, [x, y]], written from the theorem statement;
a Pratt (Lucas) primality prover for small primes; division polynomials.
"""
import math, os, random

# VLIB_P overrides the characteristic ONLY for the toy self-tests in dev/ (brute-forceable
# fields); every audit computation runs with the default p = 2^64 - 2^32 + 1.
P_GOLD = int(os.environ.get("VLIB_P", 2**64 - 2**32 + 1))
Q_GOLD = P_GOLD**5

# =============================================================================
# integer utilities (no external code)
# =============================================================================
def iroot(n, k):
    """floor(n^(1/k)) exactly."""
    if n < 0: raise ValueError
    if n < 2: return n
    x = 1 << ((n.bit_length() + k - 1) // k)
    while True:
        y = ((k - 1) * x + n // x**(k - 1)) // k
        if y >= x: break
        x = y
    while x**k > n: x -= 1
    while (x + 1)**k <= n: x += 1
    return x

SMALL_PRIMES = []
def _sieve(B):
    s = bytearray([1]) * (B + 1); s[0:2] = b"\x00\x00"
    for i in range(2, math.isqrt(B) + 1):
        if s[i]: s[i*i::i] = bytearray(len(s[i*i::i]))
    return [i for i in range(B + 1) if s[i]]
SMALL_PRIMES = _sieve(200000)

def is_probable_prime(n, rounds=20):
    """Miller-Rabin with random bases: used ONLY to steer factorisation, never as a proof."""
    if n < 2: return False
    for sp in SMALL_PRIMES[:50]:
        if n % sp == 0: return n == sp
    d, s = n - 1, 0
    while d % 2 == 0: d //= 2; s += 1
    rng = random.Random(n)
    for _ in range(rounds):
        a = rng.randrange(2, n - 1)
        x = pow(a, d, n)
        if x in (1, n - 1): continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1: break
        else: return False
    return True

def pollard_brent(n, max_iter=400000, seed=1):
    if n % 2 == 0: return 2
    rng = random.Random(seed)
    for _attempt in range(8):
        y, c, m = rng.randrange(1, n), rng.randrange(1, n), 128
        g = r = q = 1; x = ys = 0; it = 0
        while g == 1 and it < max_iter:
            x = y
            for _ in range(r): y = (y * y + c) % n
            k = 0
            while k < r and g == 1:
                ys = y
                for _ in range(min(m, r - k)):
                    y = (y * y + c) % n; q = q * abs(x - y) % n
                g = math.gcd(q, n); k += m
            r *= 2; it += r
        if g == n:
            g = 1
            while g == 1:
                ys = (ys * ys + c) % n; g = math.gcd(abs(x - ys), n)
        if 1 < g < n: return g
    return None

def factor_small(n, rho_iter=400000):
    """Full factorisation for moderate n (steering only; every prime is then PROVED separately).
    Returns dict prime->exponent, or raises if a piece cannot be split."""
    f = {}
    for sp in SMALL_PRIMES:
        if sp * sp > n: break
        while n % sp == 0: f[sp] = f.get(sp, 0) + 1; n //= sp
    stack = [n] if n > 1 else []
    while stack:
        m = stack.pop()
        if m == 1: continue
        if is_probable_prime(m): f[m] = f.get(m, 0) + 1; continue
        g = pollard_brent(m, rho_iter)
        if g is None: raise RuntimeError(f"could not split {m}")
        stack += [g, m // g]
    return f

def pratt(n, _depth=0):
    """Pratt / Lucas primality proof: n prime iff some a has a^(n-1)=1 and a^((n-1)/r)!=1
    for every prime r | n-1. Recursively proves the factors of n-1. Returns a certificate
    dict (verifiable by pratt_check) or None if n is not proved prime."""
    if n < 2: return None
    if n < 10**6:
        return {"n": n, "trial_division": all(n % d for d in range(2, math.isqrt(n) + 1))} if all(n % d for d in range(2, math.isqrt(n) + 1)) else None
    if not is_probable_prime(n): return None
    fac = factor_small(n - 1)
    subs = {}
    for r in fac:
        c = pratt(r, _depth + 1)
        if c is None: return None
        subs[r] = c
    for a in range(2, 2000):
        if pow(a, n - 1, n) != 1: return None      # Fermat witness: n composite
        if all(pow(a, (n - 1) // r, n) != 1 for r in fac):
            return {"n": n, "witness": a, "n_minus_1": {str(r): e for r, e in fac.items()}, "sub": {str(r): subs[r] for r in fac}}
    return None

def pratt_check(cert):
    """Re-check a Pratt certificate without trusting how it was built."""
    n = cert["n"]
    if "trial_division" in cert:
        return n >= 2 and all(n % d for d in range(2, math.isqrt(n) + 1))
    a = cert["witness"]; fac = {int(r): e for r, e in cert["n_minus_1"].items()}
    prod = 1
    for r, e in fac.items(): prod *= r**e
    if prod != n - 1: return False
    if pow(a, n - 1, n) != 1: return False
    for r in fac:
        if pow(a, (n - 1) // r, n) == 1: return False
        if not pratt_check(cert["sub"][str(r)]): return False
    return True

# =============================================================================
# ECPP chain checker (PARI primecert row format), written from the theorem:
#   Let N > 1, gcd(N,6)=1, E: y^2 = x^3 + a x + b over Z/NZ with gcd(4a^3+27b^2, N)=1,
#   m, s integers, s | m, q = m/s prime with q > (N^{1/4}+1)^2, and P in E(Z/NZ) such
#   that [s]P is a genuine affine point and [q]([s]P) = O, every intermediate
#   operation being valid modulo N (all required inverses exist). Then N is prime.
# Affine arithmetic mod N; any non-invertible denominator => reject.
# =============================================================================
class NotInvertible(Exception):
    pass

def _inv(a, N):
    a %= N
    g = math.gcd(a, N)
    if g != 1: raise NotInvertible(g)
    return pow(a, -1, N)

def _add_modN(P1, P2, a, N):
    if P1 is None: return P2
    if P2 is None: return P1
    x1, y1 = P1; x2, y2 = P2
    if (x1 - x2) % N == 0:
        if (y1 + y2) % N == 0: return None
        if (y1 - y2) % N != 0: raise NotInvertible("x equal, y neither equal nor opposite")
        lam = (3 * x1 * x1 + a) * _inv(2 * y1, N) % N
    else:
        lam = (y2 - y1) * _inv(x2 - x1, N) % N
    x3 = (lam * lam - x1 - x2) % N
    y3 = (lam * (x1 - x3) - y1) % N
    return (x3, y3)

def _mul_modN(k, P, a, N):
    R = None
    for bit in bin(k)[2:]:
        R = _add_modN(R, R, a, N)
        if bit == "1": R = _add_modN(R, P, a, N)
    return R

def ecpp_check(cert, target):
    """Returns (ok, log). cert = list of rows [N, t, s, a4, [x, y]] (PARI primecert)."""
    log = []
    if not isinstance(cert, list) or not cert: return False, ["empty or non-list certificate"]
    expect = target
    for k, row in enumerate(cert):
        try:
            N, t, s, a, pt = int(row[0]), int(row[1]), int(row[2]), int(row[3]), row[4]
            x, y = int(pt[0]) % N, int(pt[1]) % N
        except Exception as e:
            return False, log + [f"row {k}: malformed ({e})"]
        if N != expect: return False, log + [f"row {k}: N != expected {expect}"]
        if N < 5 or math.gcd(N, 6) != 1: return False, log + [f"row {k}: gcd(N,6) != 1"]
        m = N + 1 - t
        if s <= 0 or m % s: return False, log + [f"row {k}: s does not divide m = N+1-t"]
        q = m // s
        # q > (N^{1/4}+1)^2, established with a sufficient integer condition
        u = iroot(N, 4)                     # N^{1/4} < u+1
        if not q >= (u + 2)**2:
            return False, log + [f"row {k}: size condition q > (N^(1/4)+1)^2 not established"]
        b = (y * y - x * x * x - a * x) % N
        if math.gcd((4 * a**3 + 27 * b * b) % N, N) != 1:
            return False, log + [f"row {k}: singular curve / gcd(disc,N) != 1"]
        try:
            S = _mul_modN(s, (x, y), a, N)
            if S is None: return False, log + [f"row {k}: [s]P = O"]
            T = _mul_modN(q, S, a, N)
        except NotInvertible as e:
            return False, log + [f"row {k}: non-invertible denominator ({e})"]
        if T is not None: return False, log + [f"row {k}: [q]([s]P) != O"]
        log.append(f"row {k}: N {N.bit_length()} bits ok -> q {q.bit_length()} bits")
        expect = q
    pc = pratt(expect)
    if pc is None or not pratt_check(pc):
        return False, log + [f"terminal q = {expect} not proved prime (Pratt)"]
    log.append(f"terminal q = {expect} ({expect.bit_length()} bits) proved prime by Pratt certificate")
    return True, log

# =============================================================================
# PRIMARY: FLINT field + affine general-Weierstrass group law
# =============================================================================
import flint
_Rp = flint.fmpz_mod_poly_ctx(P_GOLD)
_X = _Rp.gen()
MODULUS = _X**5 - 3
F = flint.fq_default_ctx(modulus=MODULUS, var="z")
Z = F.gen()
PX = flint.fq_default_poly_ctx(F)
XP = PX.gen()

def fe(c):
    """F element from coefficient list [c0..c4] (c0 + c1 z + ...) or int."""
    if isinstance(c, int): return F(c)
    return F([int(v) % P_GOLD for v in c])

def coeffs(a):
    l = [int(v) for v in a.to_list()]
    return l + [0] * (5 - len(l))

def is_sq(a):
    """Euler's criterion in F_q, computed here (not FLINT's is_square)."""
    if a == 0: return True
    r = a ** ((Q_GOLD - 1) // 2)
    if r == F(1): return True
    if r == F(-1): return False
    raise ArithmeticError("Euler criterion returned neither 1 nor -1")

class Curve:
    """y^2 = x^3 + a2 x^2 + a4 x + a6 over F (a1 = a3 = 0). Points: (x, y) or None = O."""
    def __init__(self, a2, a4, a6):
        self.a2, self.a4, self.a6 = F(a2) if isinstance(a2, int) else a2, F(a4) if isinstance(a4, int) else a4, F(a6) if isinstance(a6, int) else a6
    def rhs(self, x):
        return ((x + self.a2) * x + self.a4) * x + self.a6
    def on(self, P):
        return P is None or P[1] * P[1] == self.rhs(P[0])
    def add(self, P1, P2):
        if P1 is None: return P2
        if P2 is None: return P1
        x1, y1 = P1; x2, y2 = P2
        if x1 == x2:
            if y1 + y2 == 0: return None
            lam = (3 * x1 * x1 + 2 * self.a2 * x1 + self.a4) / (2 * y1)
        else:
            lam = (y2 - y1) / (x2 - x1)
        x3 = lam * lam - self.a2 - x1 - x2
        return (x3, lam * (x1 - x3) - y1)
    def mul(self, k, P):
        if k < 0: raise ValueError
        R = None
        for bit in bin(k)[2:]:
            R = self.add(R, R)
            if bit == "1": R = self.add(R, P)
        return R
    def random_point(self, rng):
        while True:
            x = fe([rng.randrange(P_GOLD) for _ in range(5)])
            r = self.rhs(x)
            if r == 0: continue
            if is_sq(r):
                y = r.sqrt()
                assert y * y == r
                if rng.randrange(2): y = -y
                return (x, y)

def pt_json(P):
    return None if P is None else [coeffs(P[0]), coeffs(P[1])]

# ---------------------------------------------------------------- division polynomials
def divpoly(A, B, n, memo=None):
    """f_n in F[x] for y^2 = x^3 + A x + B, with psi_n = f_n (n odd), psi_n = 2y f_n (n even)."""
    if memo is None: memo = {}
    if n in memo: return memo[n]
    x = XP
    if n == 0: r = PX(0)
    elif n == 1 or n == 2: r = PX(1)
    elif n == 3: r = 3 * x**4 + 6 * A * x**2 + 12 * B * x - A * A
    elif n == 4: r = 2 * (x**6 + 5 * A * x**4 + 20 * B * x**3 - 5 * A * A * x**2 - 4 * A * B * x - 8 * B * B - A**3)
    else:
        f = x**3 + A * x + B
        F2x16 = 16 * f * f
        m = n // 2
        g = lambda k: divpoly(A, B, k, memo)
        if n % 2 == 1:
            if m % 2 == 0: r = F2x16 * g(m + 2) * g(m)**3 - g(m - 1) * g(m + 1)**3
            else:          r = g(m + 2) * g(m)**3 - F2x16 * g(m - 1) * g(m + 1)**3
        else:
            r = g(m) * (g(m + 2) * g(m - 1)**2 - g(m - 2) * g(m + 1)**2)
    memo[n] = r
    return r

def rational_l_torsion_x(A, B, l, memo):
    """x-coordinates in F_q of F_q-rational points of exact order l (l odd prime) on
    y^2 = x^3 + A x + B: roots of gcd(x^q - x, psi_l) whose rhs is a square."""
    f = divpoly(A, B, l, memo).monic()
    h = XP.pow_mod(Q_GOLD, f)
    g = (h - XP).gcd(f)
    out = []
    if g.degree() <= 0: return out
    for r, _mult in g.roots():
        v = r**3 + A * r + B
        if is_sq(v): out.append(r)
    return out

def cubic_roots(A, B):
    f = XP**3 + A * XP + B
    h = XP.pow_mod(Q_GOLD, f)
    g = (h - XP).gcd(f)
    return [] if g.degree() <= 0 else [r for r, _ in g.roots()]

# =============================================================================
# SECONDARY: pure-Python F_{p^5} (5-tuples) + projective short-Weierstrass law
# =============================================================================
class PF:
    """Pure-Python element of F_p[z]/(z^5-3)."""
    __slots__ = ("c",)
    p = P_GOLD
    def __init__(self, c):
        if isinstance(c, int): c = [c, 0, 0, 0, 0]
        self.c = tuple(v % P_GOLD for v in c)
    def __add__(s, o): return PF([a + b for a, b in zip(s.c, o.c)])
    def __sub__(s, o): return PF([a - b for a, b in zip(s.c, o.c)])
    def __neg__(s): return PF([-a for a in s.c])
    def __mul__(s, o):
        if isinstance(o, int): return PF([a * o for a in s.c])
        a, b = s.c, o.c
        t = [0] * 9
        for i in range(5):
            ai = a[i]
            if ai:
                for j in range(5): t[i + j] += ai * b[j]
        return PF([t[0] + 3 * t[5], t[1] + 3 * t[6], t[2] + 3 * t[7], t[3] + 3 * t[8], t[4]])
    __rmul__ = __mul__
    def __eq__(s, o): return s.c == o.c
    def iszero(s): return not any(s.c)
    def __pow__(s, e):
        r, b = PF(1), s
        while e:
            if e & 1: r = r * b
            b = b * b; e >>= 1
        return r
    def inv(s): return s ** (Q_GOLD - 2)

def pf_from(a):
    return PF(coeffs(a))

class ProjCurve:
    """y^2 = x^3 + A x + B, homogeneous projective (X:Y:Z), O = (0:1:0)."""
    def __init__(self, A, B): self.A, self.B = A, B
    O = (PF(0), PF(1), PF(0))
    def is_O(self, P): return P[2].iszero()
    def on(self, P):
        X, Y, Zc = P
        return (Y * Y * Zc) == (X * X * X + self.A * X * Zc * Zc + self.B * Zc * Zc * Zc)
    def dbl(self, P):
        X, Y, Zc = P
        if Zc.iszero() or Y.iszero(): return self.O
        w = self.A * Zc * Zc + X * X * 3
        s = Y * Zc
        B_ = X * Y * s
        h = w * w - B_ * 8
        X3 = h * s * 2
        Y3 = w * (B_ * 4 - h) - Y * Y * s * s * 8
        Z3 = s * s * s * 8
        return (X3, Y3, Z3)
    def add(self, P, Q):
        if P[2].iszero(): return Q
        if Q[2].iszero(): return P
        X1, Y1, Z1 = P; X2, Y2, Z2 = Q
        u1 = Y2 * Z1; u2 = Y1 * Z2
        v1 = X2 * Z1; v2 = X1 * Z2
        if v1 == v2:
            if u1 == u2: return self.dbl(P)
            return self.O
        u = u1 - u2; v = v1 - v2; w = Z1 * Z2
        vv = v * v; vvv = vv * v; r = vv * v2
        A_ = u * u * w - vvv - r * 2
        return (v * A_, u * (r - A_) - vvv * u2, vvv * w)
    def mul(self, k, P):
        R = self.O
        for bit in bin(k)[2:]:
            R = self.dbl(R)
            if bit == "1": R = self.add(R, P)
        return R
