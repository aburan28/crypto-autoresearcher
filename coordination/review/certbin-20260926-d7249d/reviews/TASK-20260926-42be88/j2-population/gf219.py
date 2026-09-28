"""Validator's own GF(2^19), curve, S_3 and descent code (TASK-20260926-42be88, J2).

Written from experiments/EXP-CERTBIN-060020/specification.yaml text only.
Imports nothing from crypto_autoresearcher or experiments/*/impl or verifier.

Field: F_2[t]/(t^19 + t^5 + t^2 + t + 1); element <-> 19-bit int, bit j = coeff of t^j.
"""
import hashlib
import json

import numpy as np

N_DEG = 19
F_POLY = (1 << 19) | (1 << 5) | (1 << 2) | (1 << 1) | 1  # 524327
ORD = (1 << 19) - 1  # 524287, multiplicative group order
A_CURVE = 46693
B_CURVE = 306147
Q_ORDER = 261823
P_PT = (82737, 282850)
Q_PT = (510336, 243234)
K_Q = 5170
L_DIM = 10
NV = 20


# ---------------------------------------------------------------- polynomial arithmetic over GF(2) (ints)
def clmul(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        a <<= 1
        b >>= 1
    return r


def pmod(a, m):
    dm = m.bit_length() - 1
    while a and a.bit_length() - 1 >= dm:
        a ^= m << (a.bit_length() - 1 - dm)
    return a


def pgcd(a, b):
    while b:
        a, b = b, pmod(a, b)
    return a


def mulmod(a, b, m=F_POLY):
    return pmod(clmul(a, b), m)


def powmod_t_2i(i, m):
    """t^(2^i) mod m by repeated squaring."""
    x = 2
    for _ in range(i):
        x = mulmod(x, x, m)
    return x


def irreducibility_rabin(m):
    """m of degree n: irreducible iff t^(2^n) = t mod m and gcd(t^(2^(n/p)) - t, m) = 1 for primes p | n.
    Also returns the full-strength check gcd(t^(2^i) - t, m) = 1 for i = 1..floor(n/2)."""
    n = m.bit_length() - 1
    top = powmod_t_2i(n, m) == 2
    gcds = {}
    for i in range(1, n // 2 + 1):
        g = pgcd(m, powmod_t_2i(i, m) ^ 2)
        gcds[i] = g
    ok = top and all(g == 1 for g in gcds.values())
    return ok, top, gcds


# ---------------------------------------------------------------- log / antilog tables (t is a generator: 2^19-1 prime)
def is_prime(n):
    if n < 2:
        return False
    i = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += 1
    return True


def build_tables():
    exp = np.zeros(2 * ORD + 2, dtype=np.int64)
    x = 1
    for i in range(ORD):
        exp[i] = x
        x <<= 1
        if x >> 19:
            x ^= F_POLY
    assert x == 1, "t^(2^19-1) != 1"
    exp[ORD:2 * ORD] = exp[:ORD]
    log = np.full(1 << 19, -1, dtype=np.int64)
    log[exp[:ORD]] = np.arange(ORD, dtype=np.int64)
    return exp, log


EXP, LOG = build_tables()
EXP_L = EXP.tolist()
LOG_L = LOG.tolist()


def fmul(a, b):
    if a == 0 or b == 0:
        return 0
    return EXP_L[LOG_L[a] + LOG_L[b]]


def finv(a):
    assert a != 0
    return EXP_L[(ORD - LOG_L[a]) % ORD]


def fsq(a):
    return fmul(a, a)


def fpow(a, e):
    if a == 0:
        return 0 if e else 1
    return EXP_L[(LOG_L[a] * e) % ORD]


def trace_direct(z):
    s = 0
    y = z
    for _ in range(N_DEG):
        s ^= y
        y = fsq(y)
    assert s in (0, 1)
    return s


TAU = [trace_direct(1 << j) for j in range(N_DEG)]
TAU_MASK = sum(1 << j for j in range(N_DEG) if TAU[j])


def tr(z):
    return bin(z & TAU_MASK).count("1") & 1


def halftrace(w):
    s = 0
    y = w
    for i in range(N_DEG):
        if i % 2 == 0:
            s ^= y
        y = fsq(y)
    return s


# ---------------------------------------------------------------- vectorized field ops
def vmul(a, b):
    a = np.asarray(a, dtype=np.int64)
    b = np.asarray(b, dtype=np.int64)
    out = EXP[(LOG[a] + LOG[b]) % ORD]
    out = np.where((a == 0) | (b == 0), 0, out)
    return out


def vmulc(a, c):
    a = np.asarray(a, dtype=np.int64)
    if c == 0:
        return np.zeros_like(a)
    out = EXP[(LOG[a] + LOG_L[c]) % ORD]
    return np.where(a == 0, 0, out)


def vsq(a):
    a = np.asarray(a, dtype=np.int64)
    out = EXP[(2 * LOG[a]) % ORD]
    return np.where(a == 0, 0, out)


def vtr(z):
    z = np.asarray(z, dtype=np.int64) & TAU_MASK
    return (np.bitwise_count(z.astype(np.uint64)) & 1).astype(np.int64)


# ---------------------------------------------------------------- curve Y^2 + XY = X^3 + A X^2 + B
O = None


def on_curve(P):
    if P is None:
        return True
    x, y = P
    return (fsq(y) ^ fmul(x, y)) == (fmul(fsq(x), x) ^ fmul(A_CURVE, fsq(x)) ^ B_CURVE)


def pneg(P):
    if P is None:
        return None
    x, y = P
    return (x, x ^ y)


def padd(P1, P2):
    if P1 is None:
        return P2
    if P2 is None:
        return P1
    x1, y1 = P1
    x2, y2 = P2
    if x1 == x2:
        if y1 == y2:
            return pdbl(P1)
        return None  # P2 = -P1
    lam = fmul(y1 ^ y2, finv(x1 ^ x2))
    x3 = fsq(lam) ^ lam ^ x1 ^ x2 ^ A_CURVE
    y3 = fmul(lam, x1 ^ x3) ^ x3 ^ y1
    return (x3, y3)


def pdbl(P):
    if P is None:
        return None
    x1, y1 = P
    if x1 == 0:
        return None
    lam = x1 ^ fmul(y1, finv(x1))
    x3 = fsq(lam) ^ lam ^ A_CURVE
    y3 = fsq(x1) ^ fmul(lam, x3) ^ x3
    return (x3, y3)


def smul(k, P):
    R = None
    for bit in bin(k)[2:] if k > 0 else "":
        R = pdbl(R)
        if bit == "1":
            R = padd(R, P)
    return R


def lift_x(x):
    """Return a point with x-coordinate x, or None if x is a twist x-coordinate."""
    if x == 0:
        # y^2 = B
        return (0, fpow(B_CURVE, 1 << 18))
    w = x ^ A_CURVE ^ fmul(B_CURVE, finv(fsq(x)))
    if tr(w) != 0:
        return None
    z = halftrace(w)
    assert fsq(z) ^ z == w
    P = (x, fmul(x, z))
    assert on_curve(P)
    return P


# ---------------------------------------------------------------- S_3 and descent
def S3(x1, x2, x3):
    u = fmul(x1, x2) ^ fmul(x1, x3) ^ fmul(x2, x3)
    return fsq(u) ^ fmul(fmul(x1, x2), x3) ^ B_CURVE


# V x V grid for x_1 (v_0..v_9) and x_2 (v_10..v_19); assignment integer v = x1 + 1024*x2
_V = np.arange(1 << L_DIM, dtype=np.int64)
GX1 = np.tile(_V, 1 << L_DIM)          # index v -> x1 = v & 1023
GX2 = np.repeat(_V, 1 << L_DIM)        # x2 = v >> 10
GP12 = vmul(GX1, GX2)
GS12 = GX1 ^ GX2


def s3_grid(xR):
    """S_3(x1, x2, xR) for every v in [0, 2^20), v = x1 + 1024 x2."""
    u = GP12 ^ vmulc(GS12, xR)
    return vsq(u) ^ vmulc(GP12, xR) ^ B_CURVE


def s_bruteforce(xR, want_solutions=False):
    vals = s3_grid(xR)
    z = np.flatnonzero(vals == 0)
    return (int(z.size), [int(v) for v in z]) if want_solutions else int(z.size)


def s_quadratic(xR):
    """Second route: for each x1 in V solve S_3 = 0 as a quadratic in x2 over F_{2^19}; count roots in V.
    S_3 = (x1+xR)^2 x2^2 + (x1 xR) x2 + (x1^2 xR^2 + B)."""
    cnt = 0
    sols = []
    for x1 in range(1 << L_DIM):
        a = fsq(x1 ^ xR)
        b = fmul(x1, xR)
        c = fsq(fmul(x1, xR)) ^ B_CURVE
        roots = []
        if a == 0:
            # linear: b x2 = c
            if b != 0:
                roots = [fmul(c, finv(b))]
            elif c == 0:
                raise RuntimeError("degenerate identically-zero quadratic")
        elif b == 0:
            roots = [fpow(fmul(c, finv(a)), 1 << 18)]  # sqrt
        else:
            # x2 = (b/a) z ; z^2 + z = c a / b^2
            w = fmul(fmul(c, a), finv(fsq(b)))
            if tr(w) == 0:
                z0 = halftrace(w)
                k = fmul(b, finv(a))
                roots = [fmul(k, z0), fmul(k, z0 ^ 1)]
        for r in roots:
            assert fmul(a, fsq(r)) ^ fmul(b, r) ^ c == 0
            if r < (1 << L_DIM):
                cnt += 1
                sols.append(x1 + (r << L_DIM))
    return cnt, sorted(sols)


# monomial order mu_order(2, 20): degree ascending then ascending sorted index tuple
MONO2 = [()] + [(i,) for i in range(NV)] + [(i, j) for i in range(NV) for j in range(i + 1, NV)]
assert len(MONO2) == 211


def x_of_bits(bits10):
    return bits10


def descend_E(xR):
    """Own descent by Moebius interpolation: evaluate S_3 at the 211 assignments of weight <= 2,
    recover the multilinear coefficients of each bit k. Returns 19 x 211 uint8 matrix.
    (Degree <= 2 is verified separately by evaluation at random points.)"""
    vals = {}
    for mono in MONO2:
        v = 0
        for i in mono:
            v |= 1 << i
        vals[mono] = S3(v & 1023, v >> 10, xR)
    coef = {}
    for mono in MONO2:
        c = 0
        # sum over subsets T of mono
        if len(mono) == 0:
            c = vals[()]
        elif len(mono) == 1:
            c = vals[mono] ^ vals[()]
        else:
            i, j = mono
            c = vals[mono] ^ vals[(i,)] ^ vals[(j,)] ^ vals[()]
        coef[mono] = c
    E = np.zeros((N_DEG, 211), dtype=np.uint8)
    for col, mono in enumerate(MONO2):
        c = coef[mono]
        for k in range(N_DEG):
            E[k, col] = (c >> k) & 1
    return E


def eval_E_at(E, v):
    """Evaluate the 19 Boolean equations of E at assignment integer v; return the 19-bit int of values."""
    bits = [(v >> i) & 1 for i in range(NV)]
    mv = np.array([1] + bits + [bits[i] & bits[j] for i in range(NV) for j in range(i + 1, NV)], dtype=np.uint8)
    vals = (E.astype(np.int64) @ mv.astype(np.int64)) & 1
    return int(sum(int(vals[k]) << k for k in range(N_DEG)))


# ---------------------------------------------------------------- E_hex codec
def E_to_hex(E):
    out = []
    for k in range(E.shape[0]):
        x = 0
        for j in np.flatnonzero(E[k]):
            x |= 1 << int(j)
        out.append(format(x, "x"))
    return out


def hex_to_E(hx):
    E = np.zeros((len(hx), 211), dtype=np.uint8)
    for k, h in enumerate(hx):
        x = int(h, 16)
        assert x >> 211 == 0
        for j in range(211):
            E[k, j] = (x >> j) & 1
    return E


def E_sha256(hx):
    return hashlib.sha256(json.dumps(hx, separators=(",", ":")).encode()).hexdigest()


# ---------------------------------------------------------------- bit-sliced exhaustive s over 2^20 for a 19 x 211 system
def _build_truth_tables():
    idx = np.arange(1 << NV, dtype=np.uint32)
    lin = []
    for i in range(NV):
        b = ((idx >> i) & 1).astype(np.uint8)
        lin.append(np.packbits(b, bitorder="little").view(np.uint64))
    ones = np.full(lin[0].shape, np.uint64(0xFFFFFFFFFFFFFFFF), dtype=np.uint64)
    T = [ones] + lin + [lin[i] & lin[j] for i in range(NV) for j in range(i + 1, NV)]
    return np.stack(T)


TT = None


def s_system(E, want_solutions=False):
    global TT
    if TT is None:
        TT = _build_truth_tables()
    acc = np.zeros(TT.shape[1], dtype=np.uint64)
    for k in range(E.shape[0]):
        cols = np.flatnonzero(E[k])
        if cols.size == 0:
            continue
        acc |= np.bitwise_xor.reduce(TT[cols], axis=0)
    zeros = ~acc
    s = int(np.bitwise_count(zeros).sum())
    if not want_solutions:
        return s
    bits = np.unpackbits(zeros.view(np.uint8), bitorder="little")
    return s, [int(v) for v in np.flatnonzero(bits)]
