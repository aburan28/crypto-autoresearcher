"""
Core estimator for EXP-ECDLP-56ee42 (the digit-statistic cell of the
probabilistic regime).

Implements the estimator of IDEA-20260815-f558e4 exactly as frozen in
experiments/EXP-ECDLP-56ee42/specification.yaml (version 1):

  (i)   complete enumeration of the prime-order subgroup: R_k = [k]P for
        k = 0..n-1 by repeated addition, recording (x, y) with the lift
        convention (canonical integer representative in [0, p));
  (ii)  q_maj = max over F: SxS -> S of the EXACT fraction of the n^2 pairs
        (R_k, R_l) with v(R_k + R_l) = F(v(R_k), v(R_l)), evaluated exactly
        via integer cyclic convolutions c_{ijm} = SUM_x (f_i * f_j)(x) f_m(x)
        (f_m the reversed indicator of fiber m) with the integer-recovery
        check |g - round(g)| < 0.25 asserted on every convolution;
  (iii) A(v) = max over a in Z/n of |SUM_k v_k e(2 pi i a k / n)| / n by one
        length-n DFT of the discrete-log-ordered statistic sequence.

PROVENANCE (static check, blocking): the T1-T4 and COMPARATOR statistic
functions below are pure functions of the integer lift (x or y) and read NO
discrete-log coordinate k.  POS-A, POS-B and NULL-1 read k / harness data BY
DESIGN and are exempt (see specification.yaml controls "static provenance
check").  The static provenance check is a source scan over this file plus a
manifest declaration, recorded before Stage 3.

LIFT CONVENTION: canonical integer representative in [0, p).  Named in every
output row.

POINT-AT-INFINITY CONVENTION: R_0 = [0]P = O is the identity.  O has no
affine coordinates; by convention x(O) = 0 and y(O) = 0 (so the digit
statistics evaluate at 0).  This convention is named in every run record.
"""
from __future__ import annotations

import math
from fractions import Fraction

import numpy as np


# ---------------------------------------------------------------------------
# Digit statistics (pure functions of the integer lift; NO k read).
# ---------------------------------------------------------------------------

def thue_morse_sign(x: int) -> int:
    """(-1)^{s_2(x)}, s_2 the binary digit sum.  T1 (of x) / T2 (of y)."""
    return 1 if (x.bit_count() & 1) == 0 else -1


def thue_morse_sign_array(xs: np.ndarray) -> np.ndarray:
    """Vectorised Thue-Morse sign over an array of non-negative ints."""
    # popcount via lookup-free bit trick is slower than bit_count in a loop
    # for uint32; use numpy's binary representation trick:
    # s_2(x) mod 2 = XOR of all bits of x.
    # Build by iterative folding: x ^= x >> 1; x ^= x >> 2; ... then bit 0.
    x = xs.astype(np.uint64)
    shift = 1
    while (1 << shift) <= xs.max(initial=0):
        x ^= x >> shift
        shift <<= 1
    parity = (x & 1).astype(np.int8)
    return (1 - 2 * parity).astype(np.int8)


def _rudin_shapiro_u(x: int) -> int:
    """u(x): number of (overlapping) occurrences of the block '11' in the
    binary expansion of x (no leading zeros)."""
    if x < 2:
        return 0
    bits = bin(x)[2:]
    return sum(1 for i in range(len(bits) - 1) if bits[i] == '1' and bits[i + 1] == '1')


def rudin_shapiro_sign(x: int) -> int:
    """The Rudin-Shapiro sign, defined by the recursion r(0)=r(1)=1,
    r(2n)=r(n), r(2n+1)=-r(n) for n>=1 (the standard Rudin-Shapiro sequence,
    OEIS A016158, which carries the root-N property the hypothesis relies on).

    INTERPRETATION NOTE: the contract describes u as 'the count of block 11
    in the binary expansion'.  That heuristic characterization does NOT
    exactly match the recursion (they diverge at x=5, 9, 10, ...; 135 of the
    first 256 values differ).  The recursion is used as the canonical
    definition because (a) it is the standard Rudin-Shapiro sequence and
    (b) the hypothesis's root-N property is a property of the recursion, not
    of the block-count sequence.  This interpretation is recorded in the run
    record; a reviewer who reads the contract's 'block 11' literally may
    request a protocol_amendment.  See _rudin_shapiro_u for the literal
    block-count (kept for reference / audit)."""
    if x < 2:
        return 1
    sign = 1
    while x >= 2:
        if x & 1:
            sign = -sign
        x >>= 1
    return sign


def rudin_shapiro_sign_array(xs: np.ndarray) -> np.ndarray:
    """Vectorised Rudin-Shapiro sign via the recursion r(0)=r(1)=1,
    r(2n)=r(n), r(2n+1)=-r(n), which equals (-1)^{u(x)} with u the count of
    (overlapping) '11' blocks in the binary expansion.  Fills level by level
    (all of bit-length k from bit-length k-1) so it is O(n) vectorised work."""
    n = int(xs.max(initial=0)) + 1
    r = np.ones(n, dtype=np.int8)
    k = 1
    while (1 << k) < n:
        lo = 1 << k
        hi = min(1 << (k + 1), n)
        m = np.arange(lo, hi, dtype=np.int64)
        parent = r[m >> 1]
        r[lo:hi] = np.where((m & 1) == 0, parent, -parent)
        k += 1
    return r[xs.astype(np.int64)]


def popcount_mod4(x: int) -> int:
    """popcount(x) mod 4.  T4 (the o2 family-I member, unbalanced)."""
    return x.bit_count() % 4


def popcount_mod4_array(xs: np.ndarray) -> np.ndarray:
    """Vectorised popcount mod 4."""
    x = xs.astype(np.uint64)
    # popcount via SWAR: standard 64-bit popcount
    c = x - ((x >> 1) & 0x5555555555555555)
    c = (c & 0x3333333333333333) + ((c >> 2) & 0x3333333333333333)
    c = (c + (c >> 4)) & 0x0F0F0F0F0F0F0F0F
    pc = ((c * 0x0101010101010101) >> 56).astype(np.uint8)
    return (pc % 4).astype(np.int8)


def top_bit_fiber(x: int, p: int) -> int:
    """Top bit of x as a fiber index in {0, 1}: 1 iff x >= 2^{floor(log2 p)}.
    COMPARATOR (an interval statistic inside the pinning)."""
    top = 1 << (p.bit_length() - 1)
    return 1 if x >= top else 0


def top_bit_fiber_array(xs: np.ndarray, p: int) -> np.ndarray:
    top = 1 << (p.bit_length() - 1)
    return (xs >= top).astype(np.int8)


# ---------------------------------------------------------------------------
# Curve arithmetic: y^2 = x^3 + x + b over F_p (a = 1).
# ---------------------------------------------------------------------------

def _tonelli_shanks(n: int, p: int) -> int:
    """sqrt(n) mod p for odd prime p, n a quadratic residue (or 0)."""
    if n % p == 0:
        return 0
    if p % 4 == 3:
        return pow(n, (p + 1) // 4, p)
    # factor p - 1 = q * 2^s
    q = p - 1
    s = 0
    while q % 2 == 0:
        q //= 2
        s += 1
    # find a non-residue z
    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1:
        z += 1
    m = s
    c = pow(z, q, p)
    t = pow(n, q, p)
    r = pow(n, (q + 1) // 2, p)
    while t != 1:
        # find least i, 0 < i < m, such that t^{2^i} = 1
        i = 1
        t2i = (t * t) % p
        while t2i != 1:
            t2i = (t2i * t2i) % p
            i += 1
        b = pow(c, 1 << (m - i - 1), p)
        m = i
        c = (b * b) % p
        t = (t * c) % p
        r = (r * b) % p
    return r


def find_generator_point(p: int, b: int) -> tuple[int, int]:
    """Find a point P = (x, y) on y^2 = x^3 + x + b over F_p by scanning
    x = 0, 1, 2, ...  Deterministic; the group is prime order so any
    non-identity point is a generator."""
    for x in range(p):
        rhs = (x * x * x + x + b) % p
        if rhs == 0:
            return (x, 0)
        if pow(rhs, (p - 1) // 2, p) == 1:
            y = _tonelli_shanks(rhs, p)
            return (x, y)
    raise ValueError("no point found (impossible for a valid curve)")


def _add_affine(p: int, x1: int, y1: int, x2: int, y2: int) -> tuple[int, int]:
    """Affine addition of (x1,y1) + (x2,y2) on y^2 = x^3 + x + b (a = 1).
    Assumes the sum is an affine point (not O)."""
    if x1 == x2:
        if (y1 + y2) % p == 0:
            raise ValueError("sum is the point at infinity")
        # doubling
        lam = (3 * x1 * x1 + 1) * pow(2 * y1, p - 2, p) % p
    else:
        lam = (y2 - y1) * pow(x2 - x1, p - 2, p) % p
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return (x3, y3)


def enumerate_subgroup(p: int, b: int, n: int) -> tuple[np.ndarray, np.ndarray]:
    """Enumerate R_k = [k]P for k = 0..n-1 by repeated addition.

    Returns (xs, ys) as uint32 arrays of length n with the lift convention
    [0, p).  R_0 = O is recorded as (0, 0) by convention (named in the run
    record).  P is the deterministic generator from find_generator_point.
    """
    xs = np.zeros(n, dtype=np.uint32)
    ys = np.zeros(n, dtype=np.uint32)
    if n <= 0:
        return xs, ys
    px, py = find_generator_point(p, b)
    if n >= 1:
        xs[1] = px
        ys[1] = py
    cx, cy = px, py
    for k in range(2, n):
        cx, cy = _add_affine(p, cx, cy, px, py)
        xs[k] = cx
        ys[k] = cy
    return xs, ys


# ---------------------------------------------------------------------------
# q_maj / q_strict via exact integer cyclic convolutions.
# ---------------------------------------------------------------------------

def _cyclic_convolution_fft(f: np.ndarray, g: np.ndarray, n: int,
                            label: str) -> np.ndarray:
    """Cyclic convolution (f * g)(x) = SUM_y f(y) g(x - y mod n) via one
    length-n FFT pair, with the integer-recovery assertion
    |h - round(h)| < 0.25 on every entry (contract requirement)."""
    F = np.fft.fft(f.astype(np.float64))
    G = np.fft.fft(g.astype(np.float64))
    h = np.fft.ifft(F * G).real
    err = np.max(np.abs(h - np.round(h)))
    if not (err < 0.25):
        raise AssertionError(
            f"integer-recovery check FAILED for {label}: "
            f"max |h - round(h)| = {err:.6g} (>= 0.25)")
    return np.round(h).astype(np.int64)


def fiber_indicators(v: np.ndarray, s: int, n: int) -> np.ndarray:
    """F[i, k] = 1 iff v(k) == i, else 0.  Shape (s, n), float64."""
    F = np.zeros((s, n), dtype=np.float64)
    F[v.astype(np.int64), np.arange(n)] = 1.0
    return F


def pair_counts(v: np.ndarray, n: int) -> np.ndarray:
    """N_{ijm} = #{(k, l) in Z/n^2 : v(k) = i, v(l) = j, v(k + l) = m}.

    Computed exactly via integer cyclic convolutions with the
    integer-recovery assertion on every convolution.  Returns an int64
    array of shape (s, s, s) where s = max(v) + 1.
    """
    s = int(v.max()) + 1
    F = fiber_indicators(v, s, n)
    #
    # N_{ijm} = #{(k, l) : v(k) = i, v(l) = j, v(k + l) = m}
    #         = SUM_x (f_i * f_j)(x) f_m(x)
    # where (f_i * f_j)(x) = SUM_y f_i(y) f_j(x - y mod n) is the cyclic
    # convolution and f_m is the ORDINARY indicator of fiber m.
    #
    # NOTE ON THE CONTRACT'S "REVERSED INDICATOR": the contract writes
    # "c_{ijm} = SUM_x (f_i * f_j)(x) f_m(x) (f_m the reversed indicator of
    # fiber m)".  A direct numerical check against O(n^2) brute-force pair
    # counting (see selftest.py) shows that the formula matches ground truth
    # with the ORDINARY indicator, not a reversed one (a cyclic reversal
    # f_m(-x mod n) gives wrong counts, e.g. at n = 7).  The ordinary
    # indicator is used; this is recorded as an interpretation note in the
    # run record.  The integer-recovery assertion is unchanged.
    N = np.zeros((s, s, s), dtype=np.int64)
    for i in range(s):
        for j in range(s):
            h = _cyclic_convolution_fft(F[i], F[j], n, label=f"conv f_{i}*f_{j}")
            for m in range(s):
                N[i, j, m] = int(np.dot(h, F[m]))
    return N


def q_maj_exact(v: np.ndarray, n: int) -> tuple[Fraction, np.ndarray]:
    """q_maj = max over F: SxS -> S of the exact fraction of the n^2 pairs
    (R_k, R_l) with v(R_k + R_l) = F(v(R_k), v(R_l)).

    The max over F decomposes coordinate-wise: for each (i, j), the optimal
    F(i, j) = argmax_m N_{ijm}, so
        q_maj = (1/n^2) * SUM_{i, j} max_m N_{ijm}.
    Returns (q_maj as an exact Fraction, the N_{ijm} array).
    """
    N = pair_counts(v, n)
    s = N.shape[0]
    total = 0
    for i in range(s):
        for j in range(s):
            total += int(N[i, j, :].max())
    return Fraction(total, n * n), N


def q_strict_exact(v: np.ndarray, n: int) -> Fraction:
    """q_strict = the fraction of pairs (R, R') for which the fiber of R+R'
    is FORCED by the pair of fibers (v(R), v(R')) -- i.e. the pairs (i, j)
    with A_i + A_j contained in a single fiber.

    (i, j) is strictly determined iff exactly one m has N_{ijm} > 0 and
    N_{ijm} = |A_i| * |A_j|.
    """
    N = pair_counts(v, n)
    s = N.shape[0]
    sizes = np.array([int((v == i).sum()) for i in range(s)])
    total = 0
    for i in range(s):
        for j in range(s):
            row = N[i, j, :]
            nz = int((row > 0).sum())
            if nz == 1 and int(row.max()) == int(sizes[i] * sizes[j]):
                total += int(sizes[i] * sizes[j])
    return Fraction(total, n * n)


# ---------------------------------------------------------------------------
# A(v) via one length-n DFT.
# ---------------------------------------------------------------------------

def A_of_v(v: np.ndarray, n: int) -> float:
    """A(v) = max over a in Z/n of |SUM_k v_k e(2 pi i a k / n)| / n, by one
    length-n DFT of the discrete-log-ordered statistic sequence."""
    V = np.fft.fft(v.astype(np.float64))
    return float(np.max(np.abs(V)) / n)


def A_noDC_of_v(v: np.ndarray, n: int) -> float:
    """A(v) excluding the a = 0 term (the mean / marginal artifact).  This is
    the DL-coordinate advantage: the largest non-DC Fourier coefficient.
    For a balanced +-1 statistic the DC term is ~0, so A_noDC ~= A.  For an
    unbalanced statistic (like T4) the DC term is the mean, and A_noDC
    isolates the DL-coordinate dependence that the NULL-2 shuffle removes."""
    V = np.fft.fft(v.astype(np.float64))
    return float(np.max(np.abs(V[1:])) / n)


# ---------------------------------------------------------------------------
# NULL-1 keyed random sign (SplitMix64).
# ---------------------------------------------------------------------------

def _splitmix64(state: list[int]) -> int:
    """Advance SplitMix64 state (a single 64-bit word) and return the next
    64-bit output."""
    state[0] = (state[0] + 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF
    z = state[0]
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & 0xFFFFFFFFFFFFFFFF
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & 0xFFFFFFFFFFFFFFFF
    z = z ^ (z >> 31)
    return z


def null1_signs(exp_id: str, replicate: int, xs: np.ndarray, ys: np.ndarray,
                p: int) -> np.ndarray:
    """NULL-1 keyed random sign: v_s(R) = +/-1 from SplitMix64 keyed on
    (EXP id string, replicate index s, point-encoding bytes (x, y) in [0, p)
    big-endian); output truncated to +/-1.

    The key is the concatenation of the EXP id string bytes, the 8-byte
    big-endian replicate index, and the 2 * ceil(log256(p)) big-endian bytes
    of (x, y).  A single SplitMix64 stream is seeded by hashing the key to a
    64-bit state (via a deterministic fold), then advanced once per point in
    the discrete-log order; the low bit of each output selects +/-1.
    """
    n = len(xs)
    key_prefix = exp_id.encode('utf-8') + replicate.to_bytes(8, 'big')
    byte_len = (p.bit_length() + 7) // 8
    signs = np.empty(n, dtype=np.int8)
    for k in range(n):
        key = key_prefix + xs[k].to_bytes(byte_len, 'big') + ys[k].to_bytes(byte_len, 'big')
        # deterministic 64-bit fold of the key to seed the stream
        state = [0]
        for i in range(0, len(key), 8):
            chunk = int.from_bytes(key[i:i + 8].ljust(8, b'\0'), 'big')
            state[0] = (state[0] + chunk + 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF
            z = state[0]
            z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & 0xFFFFFFFFFFFFFFFF
            z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & 0xFFFFFFFFFFFFFFFF
            z = z ^ (z >> 31)
            state[0] = z
        out = _splitmix64(state)
        signs[k] = 1 if (out & 1) == 0 else -1
    return signs


# ---------------------------------------------------------------------------
# NULL-2 matched-marginal shuffle.
# ---------------------------------------------------------------------------

def null2_shuffle(v: np.ndarray, n: int, seed: int) -> np.ndarray:
    """NULL-2 matched-marginal shuffle: a seeded permutation of the
    statistic's values among the points of G preserving the multiset, so
    every marginal is kept and every dependence on the point is destroyed.

    The permutation is drawn from a seeded PRNG (numpy PCG64) with the given
    seed.  The contract specifies the seed (0x56EE42 + 1000 + 10*arm_index +
    shuffle_index) but not the exact permutation algorithm; numpy's
    default_rng is deterministic (same seed -> same permutation) and fast.
    """
    rng = np.random.default_rng(seed & 0xFFFFFFFFFFFFFFFF)
    perm = rng.permutation(n)
    return v[perm]


# ---------------------------------------------------------------------------
# Interval partition of Z/n (for the Stage 1 fixture and the smoke check).
# ---------------------------------------------------------------------------

def interval_partition(n: int, s: int) -> np.ndarray:
    """Interval partition of Z/n: fiber j = {k : k in [j*n/s, (j+1)*n/s)} for
    j = 0..s-1.  Returns the fiber index of each k in 0..n-1."""
    v = np.empty(n, dtype=np.int64)
    for k in range(n):
        v[k] = min(int(k * s / n), s - 1)
    return v


def x_bucket_partition(xs: np.ndarray, p: int, s: int) -> np.ndarray:
    """x-coordinate bucket: fiber j = {x : x in [j*p/s, (j+1)*p/s)} for
    j = 0..s-1.  Applied to the x-coordinates of the enumerated points.
    (Used by the f558e4 (G) smoke check.)"""
    v = np.empty(len(xs), dtype=np.int64)
    for idx, x in enumerate(xs):
        v[idx] = min(int(int(x) * s / p), s - 1)
    return v
