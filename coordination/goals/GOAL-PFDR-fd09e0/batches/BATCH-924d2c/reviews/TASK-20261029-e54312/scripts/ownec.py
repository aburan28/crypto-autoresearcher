"""Reviewer-written arithmetic for TASK-20261029-e54312 (J2a seeds, J2b recount).

Imports nothing from experiments/EXP-PFDR-bb0d26 (no run.py, check.py, vendor/curve.py or labelsum.c).
Shared with the producer only by necessity: the seeding convention, read from run.py (_rng, gap/null/plant
builders) and vendor/curve.py (generate_prime_order_curve, random_point, lift_x) for RNG consumption order:

  curve stream : random.Random(int(sha256("crypto_autoresearcher.index_calculus.curve|<bits>|<seed>"), big-endian))
                 p = next prime >= (randrange(2^(bits-1), 2^bits) | 1), redrawn until p has <bits> bits;
                 then repeat: a = randrange(1, p), b = randrange(1, p); skip if singular (no further draw);
                 P = random point (below); accept iff the order certification passes (see accept_order).
  random point : repeat x = randrange(p) until x^3 + a x + b is 0 or a square; y = the smaller root;
                 one rng.random() draw: P = (x, y) if < 0.5 else (x, -y).
  job streams  : random.Random(int(sha256("EXP-PFDR-bb0d26|" + "|".join(labels)), big-endian)) with labels
                 (gap, block, cell, c), (null, block, cell, c, k) and (plant, block, cell, c).

Everything else here (primality, Jacobi symbol, Cipolla square roots, affine and Jacobian group law,
baby-step giant-step order search, label-set builders, pair-sum counters) is written independently.
"""
from __future__ import annotations

import hashlib
import itertools
import math
import random

EXP = "EXP-PFDR-bb0d26"
SEED_BLOCK = {"main": 8_100_000, "rep": 8_200_000, "selftest": 8_900_000}


# ------------------------------------------------------------------ number theory
def is_prime(n: int) -> bool:
    if n < 2:
        return False
    for q in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % q == 0:
            return n == q
    d, s = n - 1, 0
    while not d & 1:
        d >>= 1
        s += 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):   # deterministic for n < 3.3e24
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def jacobi(a: int, n: int) -> int:
    """Jacobi symbol (a/n), n odd positive (binary algorithm with reciprocity)."""
    a %= n
    t = 1
    while a:
        while a % 2 == 0:
            a //= 2
            if n % 8 in (3, 5):
                t = -t
        a, n = n, a
        if a % 4 == 3 and n % 4 == 3:
            t = -t
        a %= n
    return t if n == 1 else 0


def cipolla_sqrt(a: int, p: int) -> int:
    """A square root of the quadratic residue a mod odd prime p (Cipolla), canonicalised to the smaller one."""
    a %= p
    if a == 0:
        return 0
    t = 0
    while True:
        w = (t * t - a) % p
        if w and jacobi(w, p) == -1:
            break
        t += 1
    # (t + sqrt(w))^((p+1)/2) in F_p[sqrt(w)]
    e = (p + 1) // 2
    r0, r1 = 1, 0
    b0, b1 = t, 1
    while e:
        if e & 1:
            r0, r1 = (r0 * b0 + r1 * b1 % p * w) % p, (r0 * b1 + r1 * b0) % p
        b0, b1 = (b0 * b0 + b1 * b1 % p * w) % p, (2 * b0 * b1) % p
        e >>= 1
    assert r1 == 0 and r0 * r0 % p == a
    return min(r0, p - r0)


# ------------------------------------------------------------------ group law (own)
class EC:
    """y^2 = x^3 + a x + b over F_p; points are (x, y) tuples or None for the point at infinity."""

    def __init__(self, p: int, a: int, b: int):
        self.p, self.a, self.b = p, a % p, b % p

    def f(self, x: int) -> int:
        return (pow(x, 3, self.p) + self.a * x + self.b) % self.p

    def on(self, P) -> bool:
        return P is None or (P[1] * P[1] - self.f(P[0])) % self.p == 0

    def neg(self, P):
        return None if P is None else (P[0], (self.p - P[1]) % self.p)

    def add(self, P, Q):
        if P is None:
            return Q
        if Q is None:
            return P
        p = self.p
        (x1, y1), (x2, y2) = P, Q
        if x1 == x2:
            if (y1 + y2) % p == 0:
                return None
            num, den = (3 * x1 * x1 + self.a) % p, (2 * y1) % p
        else:
            num, den = (y2 - y1) % p, (x2 - x1) % p
        lam = num * pow(den, p - 2, p) % p                 # Fermat inverse (vendor uses pow(., -1, p))
        x3 = (lam * lam - x1 - x2) % p
        return (x3, (lam * (x1 - x3) - y1) % p)

    # Jacobian coordinates for scalar multiplication (independent of the affine path above)
    def _jdbl(self, X, Y, Z):
        p = self.p
        if Z == 0 or Y == 0:
            return (1, 1, 0)
        YY = Y * Y % p
        S = 4 * X * YY % p
        M = (3 * X * X + self.a * pow(Z, 4, p)) % p
        X3 = (M * M - 2 * S) % p
        Y3 = (M * (S - X3) - 8 * YY * YY) % p
        return (X3, Y3, 2 * Y * Z % p)

    def _jadd(self, A, B):
        p = self.p
        X1, Y1, Z1 = A
        X2, Y2, Z2 = B
        if Z1 == 0:
            return B
        if Z2 == 0:
            return A
        Z1Z1, Z2Z2 = Z1 * Z1 % p, Z2 * Z2 % p
        U1, U2 = X1 * Z2Z2 % p, X2 * Z1Z1 % p
        S1, S2 = Y1 * Z2 * Z2Z2 % p, Y2 * Z1 * Z1Z1 % p
        if U1 == U2:
            return self._jdbl(X1, Y1, Z1) if S1 == S2 else (1, 1, 0)
        H, R = (U2 - U1) % p, (S2 - S1) % p
        HH = H * H % p
        HHH = H * HH % p
        X3 = (R * R - HHH - 2 * U1 * HH) % p
        Y3 = (R * (U1 * HH - X3) - S1 * HHH) % p
        return (X3, Y3, Z1 * Z2 * H % p)

    def mul(self, k: int, P):
        """k P by left-to-right double-and-add in Jacobian coordinates."""
        if P is None or k == 0:
            return None
        if k < 0:
            return self.mul(-k, self.neg(P))
        J = (P[0], P[1], 1)
        R = (1, 1, 0)
        for bit in bin(k)[2:]:
            R = self._jdbl(*R)
            if bit == "1":
                R = self._jadd(R, J)
        X, Y, Z = R
        if Z == 0:
            return None
        zi = pow(Z, self.p - 2, self.p)
        return (X * zi * zi % self.p, Y * zi * zi * zi % self.p)

    def in_L(self, x: int) -> bool:
        fx = self.f(x)
        return fx != 0 and jacobi(fx, self.p) == 1

    def random_point(self, rng: random.Random):
        """RNG consumption as vendor curve.random_point (see module docstring)."""
        p = self.p
        while True:
            x = rng.randrange(p)
            fx = self.f(x)
            if fx == 0:
                y = 0
            elif jacobi(fx, p) == 1:
                y = cipolla_sqrt(fx, p)
            else:
                continue
            return (x, y) if rng.random() < 0.5 else (x, (p - y) % p)


def bsgs_hits(E: EC, P, lo: int, hi: int) -> list[int]:
    """Every m in [lo, hi] with m P = O (own baby-step giant-step)."""
    width = hi - lo + 1
    s = math.isqrt(width) + 1
    table: dict = {}
    R = None
    for j in range(s):                      # j P, j = 0 .. s-1
        table.setdefault(R, []).append(j)
        R = E.add(R, P)
    step = E.neg(E.mul(s, P))               # -s P
    G = E.neg(E.mul(lo, P))                 # -(lo + i s) P, i = 0, 1, ...
    hits = []
    i = 0
    while lo + i * s <= hi:
        for j in table.get(G, []):
            m = lo + i * s + j
            if lo <= m <= hi:
                hits.append(m)
        G = E.add(G, step)
        i += 1
    return sorted(set(hits))


def seeded(label: str) -> random.Random:
    return random.Random(int.from_bytes(hashlib.sha256(label.encode()).digest(), "big"))


def job_rng(*labels) -> random.Random:
    return seeded("|".join(map(str, (EXP,) + labels)))


def regenerate_curve(bits: int, seed: int):
    """(p, a, b, N, candidates_tried) following the generator's stream; acceptance decided by own BSGS.
    Acceptance rule reproduced: the unique m in [p+1-2isqrt(p)-2, p+1+2isqrt(p)+2] with mP = O exists,
    m != p, m > 4 isqrt(p) + 4 and m is prime."""
    rng = seeded(f"crypto_autoresearcher.index_calculus.curve|{bits}|{seed}")
    while True:
        c = rng.randrange(1 << (bits - 1), 1 << bits) | 1
        while not is_prime(c):
            c += 1
        if c.bit_length() == bits:
            p = c
            break
    lo = p + 1 - 2 * math.isqrt(p) - 2
    hi = p + 1 + 2 * math.isqrt(p) + 2
    tried = 0
    while True:
        a, b = rng.randrange(1, p), rng.randrange(1, p)
        if (4 * a ** 3 + 27 * b ** 2) % p == 0:
            continue
        tried += 1
        E = EC(p, a, b)
        P = E.random_point(rng)
        hits = bsgs_hits(E, P, lo, hi)
        if len(hits) != 1:
            continue
        m = hits[0]
        if m == p or m <= 4 * math.isqrt(p) + 4 or not is_prime(m):
            continue
        return p, a, b, m, tried


# ------------------------------------------------------------------ builders (own, seeding convention shared)
def half_box_size(r: int, T: int) -> int:
    return ((2 * T + 1) ** r - 1) // 2


def least_T(r: int, n: int) -> int:
    need = -(-102 * n // 100) + 8           # ceil(1.02 n) + 8, exact
    T = 0
    while half_box_size(r, T) < need:
        T += 1
    return T


def half_box(r: int, T: int):
    for v in itertools.product(range(-T, T + 1), repeat=r):
        nz = next((e for e in v if e), 0)
        if nz > 0:
            yield v


def build_gap(E: EC, r: int, n: int, rng, record_collisions: bool = False):
    pts = [E.random_point(rng) for _ in range(r)]
    T = least_T(r, n)
    mult = []
    for P in pts:                            # k P for k in [-T, T] by repeated own affine addition
        row = {0: None}
        Q = None
        for k in range(1, T + 1):
            Q = E.add(Q, P)
            row[k] = Q
            row[-k] = E.neg(Q)
        mult.append(row)
    labels, first_vec, seen = [], {}, {}
    enumerated = dup = inf = 0
    first = last = None
    collisions, infinities, collected = [], [], []
    for v in half_box(r, T):
        enumerated += 1
        Q = None
        for row, ci in zip(mult, v):
            Q = E.add(Q, row[ci])
        if Q is None:
            inf += 1
            if record_collisions:
                infinities.append(list(v))
            continue
        x = Q[0]
        if x in seen:
            dup += 1
            if record_collisions:
                collisions.append({"vector": list(v), "earlier_vector": list(seen[x][0]),
                                   "same_point": Q == seen[x][1]})
            continue
        seen[x] = (v, Q)
        labels.append(x)
        collected.append(v)
        if first is None:
            first = list(v)
        last = list(v)
        if len(labels) == n:
            break
    meta = {"T": T, "enumerated": enumerated, "duplicate_skips": dup, "infinity_skips": inf,
            "first": first, "last": last}
    extra = {"points": pts, "collisions": collisions, "infinities": infinities, "vectors": collected}
    return (labels if len(labels) == n else None), meta, extra


def build_null(E: EC, n: int, rng) -> list[int]:
    out, seen = [], set()
    while len(out) < n:
        x = rng.randrange(E.p)
        if x in seen:
            continue
        if not E.in_L(x):
            continue
        seen.add(x)
        out.append(x)
    return out


class PrefixCounter:
    """Incremental exact C of a growing label set (pure Python dict; independent of any kernel)."""

    def __init__(self, p: int):
        self.p, self.xs, self.cnt, self.C = p, [], {}, 0

    def add(self, x: int):
        p, cnt = self.p, self.cnt
        for y in self.xs:
            s = x + y
            if s >= p:
                s -= p
            k = cnt.get(s, 0)
            self.C += k
            cnt[s] = k + 1
        self.xs.append(x)


def build_plant(E: EC, n: int, rng, null_C: list[int]):
    """Planted label AP; m chosen by a linear scan over prefixes (the driver uses a bisection)."""
    p, m_cap = E.p, n // 2
    x0 = rng.randrange(p)
    w = rng.randrange(1, p)
    ap, k = [], 0
    while len(ap) < m_cap:
        x = (x0 + k * w) % p
        if E.in_L(x):
            ap.append(x)
        k += 1
    thr = 0.30 * (sum(null_C) / len(null_C))          # same float expression as the frozen rule
    pc = PrefixCounter(p)
    internal_at = {}
    m = None
    for i, x in enumerate(ap):
        pc.add(x)
        mm = i + 1
        if mm >= 4:
            internal_at[mm] = pc.C
            if pc.C >= thr:
                m = mm
                break
    feasible = m is not None
    if not feasible:
        m = m_cap
    internal = internal_at[m]
    labels = ap[:m]
    used = set(labels)
    while len(labels) < n:
        x = rng.randrange(p)
        if x in used or not E.in_L(x):
            continue
        used.add(x)
        labels.append(x)
    exact_thr_cmp = (200 * internal >= 3 * sum(null_C))   # internal >= 0.3 * mean, exact rational
    return labels, {"m": m, "internal": internal, "feasible": feasible, "m_cap": m_cap, "x0": x0, "w": w,
                    "thr_float": thr, "exact_threshold_agrees": (exact_thr_cmp == (internal >= thr))}


def dict_count(labels: list[int], p: int) -> tuple[int, int]:
    mult = {}
    n = len(labels)
    for i in range(n):
        xi = labels[i]
        for j in range(i + 1, n):
            s = xi + labels[j]
            if s >= p:
                s -= p
            mult[s] = mult.get(s, 0) + 1
    return sum(m * (m - 1) // 2 for m in mult.values()), len(mult)


def set_digest(labels) -> str:
    return hashlib.sha256((",".join(map(str, labels))).encode()).hexdigest()
