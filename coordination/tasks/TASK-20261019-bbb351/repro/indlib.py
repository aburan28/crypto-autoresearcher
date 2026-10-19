"""Validator-owned arithmetic for EXP-CMFB-cea1d2. Written from the frozen specification text only; it imports
nothing from experiments/EXP-CMFB-cea1d2/implementation. Used by the ind_*.py scripts in this directory."""
import json, math, random
from math import comb, isqrt
import numpy as np

RUNS = '/home/user/crypto-autoresearcher/experiments/EXP-CMFB-cea1d2/runs'
RID = {'t1': 'RUN-CMFB-2373be', 't2': 'RUN-CMFB-5905c0', 't3': 'RUN-CMFB-66b0fe', 't4': 'RUN-CMFB-3dc120',
       't5': 'RUN-CMFB-42a578', 't6': 'RUN-CMFB-e13f0e', 't7': 'RUN-CMFB-c71d35', 't8': 'RUN-CMFB-2010d3'}
CELLS = {'C16': (2 ** 14, 2 ** 18), 'C20': (2 ** 18, 2 ** 22), 'C24': (2 ** 22, 2 ** 25)}
CELL_CODE = {'C16': 16, 'C18': 18, 'C20': 20, 'C24': 24}
ARM_CODE = {'FAM': 1, 'N-A': 2, 'N-B': 3, 'N-B-ctrl': 4}


def load(t):
    return json.load(open(f'{RUNS}/{RID[t]}/raw-result.json'))


# ---- primes by trial division (independent of Miller-Rabin)
_SMALL = None


def _primes_to(n):
    s = bytearray([1]) * (n + 1)
    s[0:2] = b'\x00\x00'
    for i in range(2, isqrt(n) + 1):
        if s[i]:
            s[i * i::i] = bytearray(len(s[i * i::i]))
    return [i for i in range(n + 1) if s[i]]


def is_prime(n):
    global _SMALL
    if _SMALL is None:
        _SMALL = _primes_to(7000)  # covers sqrt(2^25 + 2^13)
    if n < 2:
        return False
    for q in _SMALL:
        if q * q > n:
            return True
        if n % q == 0:
            return n == q
    raise ValueError('n too large for trial division table')


def cube_base(N):
    B = 1
    while B ** 3 < 6 * N:
        B += 1
    return B


# ---- elliptic curve y^2 = x^3 + A x + B over F_p, affine, python ints
def add(P, Q, A, p):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2:
        if (y1 + y2) % p == 0:
            return None
        lam = (3 * x1 * x1 + A) * pow(2 * y1, -1, p) % p
    else:
        lam = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (lam * lam - x1 - x2) % p
    return (x3, (lam * (x1 - x3) - y1) % p)


def mul(k, P, A, p):
    k %= 10 ** 30  # never negative here
    R = None
    Q = P
    while k:
        if k & 1:
            R = add(R, Q, A, p)
        Q = add(Q, Q, A, p)
        k >>= 1
    return R


def legendre(a, p):
    r = pow(a % p, (p - 1) // 2, p)
    return 0 if r == 0 else (1 if r == 1 else -1)


def sqrt_mod(n, p):
    """Cipolla (independent of Tonelli-Shanks): returns the smaller root of a residue n."""
    n %= p
    if n == 0:
        return 0
    if p % 4 == 3:
        r = pow(n, (p + 1) // 4, p)
    else:
        a = 1
        while legendre(a * a - n, p) != -1:
            a += 1
        w2 = (a * a - n) % p

        def fmul(u, v):
            return ((u[0] * v[0] + u[1] * v[1] * w2) % p, (u[0] * v[1] + u[1] * v[0]) % p)
        res, base, e = (1, 0), (a, 1), (p + 1) // 2
        while e:
            if e & 1:
                res = fmul(res, base)
            base = fmul(base, base)
            e >>= 1
        r = res[0]
    assert r * r % p == n
    return min(r, p - r)


def small_x_points(A, B, p, count):
    pts, x = [], 0
    while len(pts) < count:
        f = (x * x * x + A * x + B) % p
        if f != 0 and pow(f, (p - 1) // 2, p) == 1:
            pts.append((x, sqrt_mod(f, p)))
        x += 1
    return pts, x


def squarefree_list(limit=60):
    L = [1, -1]
    for n in range(2, limit + 1):
        if all(n % (q * q) for q in range(2, isqrt(n) + 1)):
            L += [n, -n]
    return L


# ---- independent m=3 coverage counters
def cov_prefix_scatter(labels, N):
    """Coverage by enumerating every multiset i<=j<=k with k = max index: pairs (i<=j) in j-major order,
    the triples with max index k use the prefix of pairs with j<=k. Returns (coverage, enumerated)."""
    l = np.asarray(labels, dtype=np.int64)
    B = len(l)
    pairs = np.concatenate([(l[:j + 1] + l[j]) % N for j in range(B)])  # block j has j+1 pairs
    seen = np.zeros(N, dtype=bool)
    enum = 0
    off = 0
    for k in range(B):
        off += k + 1  # pairs with j <= k : (k+1)(k+2)/2
        seen[(pairs[:off] + l[k]) % N] = True
        enum += off
    return int(seen.sum()), enum


def cov_fft_support(labels, N):
    """Coverage as |supp(1_S * 1_S * 1_S)| over Z_N (ordered triples; the support equals the multiset support).
    Linear convolutions by FFT folded mod N. Different algorithm from any enumeration."""
    M = 1
    while M < 2 * N:
        M *= 2
    ind = np.zeros(N)
    ind[np.asarray(labels, dtype=np.int64) % N] = 1.0
    F = np.fft.rfft(ind, M)
    c2 = np.fft.irfft(F * F, M)[:2 * N]
    s2 = np.zeros(N)
    s2 += (c2[:N] > 0.5)
    s2 += (c2[N:2 * N] > 0.5) if 2 * N - N > 0 else 0
    s2 = (s2 > 0).astype(float)
    F2 = np.fft.rfft(s2, M)
    c3 = np.fft.irfft(F2 * F, M)[:2 * N]
    s3 = (c3[:N] > 0.5) | (c3[N:2 * N] > 0.5)
    return int(s3.sum())


def histogram_stats(labels, N):
    """Full histogram by bincount over all sums i<=j<=k: (total, nonzero, collisions, max)."""
    l = np.asarray(labels, dtype=np.int64)
    B = len(l)
    pairs = np.concatenate([(l[:j + 1] + l[j]) % N for j in range(B)])
    h = np.zeros(N, dtype=np.int64)
    off = 0
    for k in range(B):
        off += k + 1
        h += np.bincount((pairs[:off] + l[k]) % N, minlength=N)
    return int(h.sum()), int(np.count_nonzero(h)), int((h * (h - 1) // 2).sum()), int(h.max())


def rand_labels(N, B, cell, arm, member, stream, seed=7005):
    """Recipe of the spec 'random_base_generation' + the docstring it points to (rng_streams)."""
    g = np.random.Generator(np.random.PCG64(np.random.SeedSequence(
        [seed, CELL_CODE[cell], ARM_CODE[arm], member, stream])))
    half = (N - 1) // 2
    chosen, seen_c, need = [], set(), B
    while need > 0:
        for c in g.integers(1, half + 1, size=need):
            c = int(c)
            if c not in seen_c:
                seen_c.add(c)
                chosen.append(c)
        need = B - len(chosen)
    signs = g.integers(0, 2, size=B)
    return [c if int(s) == 0 else N - c for c, s in zip(chosen, signs)]
