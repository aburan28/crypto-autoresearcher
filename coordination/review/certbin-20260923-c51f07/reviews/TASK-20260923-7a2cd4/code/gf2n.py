"""F_{2^17} = F_2[t]/(t^17 + t^3 + 1), written from the text of
experiments/EXP-CERTBIN-4e92d7/specification.yaml `object.field` alone.

Element <-> 17-bit integer, bit j = coefficient of t^j.

Two independent multiplication routes are provided and cross-checked by the
self-tests:
  * mul()  : carry-less schoolbook product followed by polynomial reduction;
  * vmul() : numpy log/exp tables with base t (t generates F_{2^17}^* because
             2^17 - 1 = 131071 is prime and t != 1; the self-test verifies
             that the table visits every nonzero element exactly once).
"""
import numpy as np

N = 17
MOD = (1 << 17) | (1 << 3) | 1          # t^17 + t^3 + 1
ORDER = (1 << N) - 1                    # |F^*| = 131071
SIZE = 1 << N


# ----------------------------------------------------------------- F_2[t] --
def clmul(a: int, b: int) -> int:
    """Carry-less product in F_2[t] (no reduction)."""
    r = 0
    while b:
        if b & 1:
            r ^= a
        a <<= 1
        b >>= 1
    return r


def polymod(a: int, m: int) -> int:
    """a mod m in F_2[t]."""
    dm = m.bit_length() - 1
    while a and a.bit_length() - 1 >= dm:
        a ^= m << (a.bit_length() - 1 - dm)
    return a


def polygcd(a: int, b: int) -> int:
    while b:
        a, b = b, polymod(a, b)
    return a


def polydivides(d: int, a: int) -> bool:
    return polymod(a, d) == 0


# ------------------------------------------------------------ scalar field --
def mul(a: int, b: int) -> int:
    return polymod(clmul(a, b), MOD)


def sq(a: int) -> int:
    return mul(a, a)


def power(a: int, e: int) -> int:
    r = 1
    while e:
        if e & 1:
            r = mul(r, a)
        a = mul(a, a)
        e >>= 1
    return r


def inv(a: int) -> int:
    if a == 0:
        raise ZeroDivisionError("inverse of 0 in F_2^17")
    return power(a, ORDER - 1)          # a^(2^17 - 2)


def sqrt(a: int) -> int:
    return power(a, 1 << (N - 1))       # a^(2^16) is the unique square root


def trace(a: int) -> int:
    """Absolute trace to F_2: sum_{i<17} a^(2^i). Returns 0 or 1."""
    s, x = 0, a
    for _ in range(N):
        s ^= x
        x = sq(x)
    if s not in (0, 1):
        raise AssertionError("trace not in F_2 -- field arithmetic is broken")
    return s


def half_trace(c: int) -> int:
    """H(c) = sum_{i=0}^{(n-1)/2} c^(4^i); for n odd, H(c)^2 + H(c) = c + Tr(c)."""
    h, x = 0, c
    for _ in range((N - 1) // 2 + 1):
        h ^= x
        x = sq(sq(x))
    return h


# ---------------------------------------------------------- vector (numpy) --
def _build_tables():
    exp = np.zeros(2 * ORDER, dtype=np.int64)
    log = np.full(SIZE, -1, dtype=np.int64)
    x = 1
    for i in range(ORDER):
        exp[i] = x
        if log[x] != -1:
            raise AssertionError("t is not a generator: repeated power")
        log[x] = i
        x = mul(x, 2)                   # multiply by t
    if x != 1:
        raise AssertionError("t^(2^17-1) != 1")
    exp[ORDER:] = exp[:ORDER]
    return exp, log


EXP, LOG = _build_tables()


def vmul(a, b):
    a = np.asarray(a, dtype=np.int64)
    b = np.asarray(b, dtype=np.int64)
    zero = (a == 0) | (b == 0)
    la = np.where(a == 0, 0, LOG[np.where(a == 0, 1, a)])
    lb = np.where(b == 0, 0, LOG[np.where(b == 0, 1, b)])
    out = EXP[la + lb]
    return np.where(zero, 0, out)


def vsq(a):
    return vmul(a, a)


def vinv(a):
    a = np.asarray(a, dtype=np.int64)
    if np.any(a == 0):
        raise ZeroDivisionError("vector inverse of 0")
    return EXP[(ORDER - LOG[a]) % ORDER]


def trace_mask() -> int:
    """bit j = Tr(t^j); then Tr(x) = parity(x & mask) by F_2-linearity."""
    m = 0
    for j in range(N):
        if trace(1 << j):
            m |= 1 << j
    return m


TMASK = trace_mask()


def vtrace(a):
    a = np.asarray(a, dtype=np.int64)
    return (np.bitwise_count((a & TMASK).astype(np.uint64)) & 1).astype(np.int64)
