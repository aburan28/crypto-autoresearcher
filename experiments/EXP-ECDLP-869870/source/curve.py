"""Toy prime-order short-Weierstrass curve arithmetic for the EXP-ECDLP-869870
curve arm: vectorised affine arithmetic over F_p (p < 2^25, so int64 products
never overflow), point counting by the Euler criterion, curve search, full
group enumeration [i]P by block addition, and the r-adding walk on real points.

This module is the WALK side. The certificate verifier (verify_certificate.py)
shares no code with it.
"""
from __future__ import annotations

import hashlib
import math

import numpy as np

import instrument as I


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    for q in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % q == 0:
            return n == q
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2; s += 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):   # deterministic below 3.3e24
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


class Field:
    def __init__(self, p: int):
        assert p < (1 << 25)
        self.p = p

    def mul(self, a, b):
        return (a * b) % self.p

    def powv(self, base: np.ndarray, e: int) -> np.ndarray:
        r = np.ones_like(base); b = base % self.p
        while e:
            if e & 1:
                r = (r * b) % self.p
            b = (b * b) % self.p
            e >>= 1
        return r

    def inv(self, a: np.ndarray) -> np.ndarray:
        return self.powv(a, self.p - 2)

    def legendre(self, v: np.ndarray) -> np.ndarray:
        """1 for QR, p-1 for non-residue, 0 for zero."""
        return self.powv(v, (self.p - 1) // 2)


def count_points(p: int, a: int, b: int, chunk: int = 1 << 22) -> int:
    F = Field(p); total = p + 1
    for lo in range(0, p, chunk):
        x = np.arange(lo, min(p, lo + chunk), dtype=np.int64)
        rhs = (x * x % p * x + a * x + b) % p
        l = F.legendre(rhs)
        total += int((l == 1).sum()) - int((l == p - 1).sum())
    return total


def sqrt_mod(v: int, p: int) -> int:
    assert p % 4 == 3
    r = pow(v, (p + 1) // 4, p)
    assert r * r % p == v % p
    return r


class Curve:
    def __init__(self, p: int, a: int, b: int):
        self.p, self.a, self.b = p, a, b
        self.F = Field(p)
        assert (4 * a ** 3 + 27 * b ** 2) % p != 0

    def on_curve(self, x: int, y: int) -> bool:
        p = self.p
        return (y * y - (x * x * x + self.a * x + self.b)) % p == 0

    def add_vec(self, x1, y1, i1, x2, y2, i2):
        """Vectorised affine addition with infinity flags. Returns (x, y, inf)."""
        p = self.p
        same_x = (x1 == x2)
        dbl = same_x & (y1 == y2) & ~i1 & ~i2
        neg = same_x & (y1 != y2) & ~i1 & ~i2
        neg |= same_x & (y1 == y2) & (y1 == 0) & ~i1 & ~i2   # doubling a 2-torsion point (absent on odd-order curves)
        den = np.where(dbl, (2 * y1) % p, (x2 - x1) % p)
        den = np.where(den == 0, 1, den)
        num = np.where(dbl, (3 * x1 * x1 % p + self.a) % p, (y2 - y1) % p)
        lam = (num * self.F.inv(den)) % p
        x3 = (lam * lam - x1 - x2) % p
        y3 = (lam * (x1 - x3) - y1) % p
        # infinity handling
        x3 = np.where(i1, x2, np.where(i2, x1, x3))
        y3 = np.where(i1, y2, np.where(i2, y1, y3))
        inf = (i1 & i2) | neg
        x3 = np.where(inf, 0, x3); y3 = np.where(inf, 0, y3)
        return x3, y3, inf

    def mul_vec(self, k: np.ndarray, x: np.ndarray, y: np.ndarray):
        """Vectorised double-and-add [k]P for per-element scalars (walk side)."""
        k = k.astype(np.int64).copy()
        rx = np.zeros_like(x); ry = np.zeros_like(y); ri = np.ones(x.shape, dtype=bool)
        bx = x.copy(); by = y.copy(); bi = np.zeros(x.shape, dtype=bool)
        nbits = int(k.max()).bit_length() if k.size else 0
        for _ in range(nbits):
            bit = (k & 1) == 1
            ax, ay, ai = self.add_vec(rx, ry, ri, bx, by, bi)
            rx = np.where(bit, ax, rx); ry = np.where(bit, ay, ry); ri = np.where(bit, ai, ri)
            bx, by, bi = self.add_vec(bx, by, bi, bx, by, bi)
            k >>= 1
        return rx, ry, ri

    def add_pt(self, P, Q):
        """Scalar (Python int) affine addition; None = infinity."""
        if P is None: return Q
        if Q is None: return P
        p = self.p
        if P[0] == Q[0]:
            if (P[1] + Q[1]) % p == 0: return None
            lam = (3 * P[0] * P[0] + self.a) * pow(2 * P[1], -1, p) % p
        else:
            lam = (Q[1] - P[1]) * pow(Q[0] - P[0], -1, p) % p
        x3 = (lam * lam - P[0] - Q[0]) % p
        return (x3, (lam * (P[0] - x3) - P[1]) % p)

    def mul_pt(self, k: int, P):
        R = None; B = P
        while k:
            if k & 1: R = self.add_pt(R, B)
            B = self.add_pt(B, B); k >>= 1
        return R


def curve_id(p: int, a: int, b: int) -> str:
    return "TOY-P24-" + hashlib.sha256(f"{p}:{a}:{b}".encode()).hexdigest()[:8]


def search_curve(seed: int, target_log2: int = 24, max_candidates: int = 2000) -> dict:
    """Seeded search: p prime = 3 mod 4 near 2^target_log2, small (a, b), #E prime.
    Returns the curve record with the point-counting log."""
    rng = np.random.default_rng(seed)
    log_ = []
    p = None
    while p is None:
        cand = int(rng.integers(1 << target_log2, (1 << target_log2) + (1 << 18)))
        cand |= 3
        if cand % 4 == 3 and is_prime(cand):
            p = cand
    for tries in range(max_candidates):
        a = int(rng.integers(1, 1 << 10)); b = int(rng.integers(1, 1 << 10))
        if (4 * a ** 3 + 27 * b ** 2) % p == 0:
            continue
        n = count_points(p, a, b)
        log_.append({"a": a, "b": b, "order": n, "prime": is_prime(n)})
        if is_prime(n):
            E = Curve(p, a, b)
            # base point
            while True:
                x = int(rng.integers(0, p)); rhs = (x ** 3 + a * x + b) % p
                if pow(rhs, (p - 1) // 2, p) == 1:
                    y = sqrt_mod(rhs, p); break
            P = (x, y)
            assert E.on_curve(*P)
            assert E.mul_pt(n, P) is None, "[N]P != O"
            return {"p": p, "a": a, "b": b, "N": n, "P": [x, y], "curve_id": curve_id(p, a, b),
                    "hasse_ok": abs(n - p - 1) <= 2 * math.isqrt(p) + 1,
                    "search_seed": seed, "candidates_tried": tries + 1, "search_log": log_,
                    "point_counting": "Euler-criterion sum over all x in F_p (vectorised, chunked), #E = p + 1 + sum chi(x^3 + a x + b)",
                    "verification": {"N_prime": True, "[N]P_is_infinity_pure_python": True, "P_on_curve": True}}
    raise RuntimeError("no prime-order curve found")


def enumerate_group(E: Curve, P, N: int, B: int = 4096):
    """xs[i], ys[i] = coordinates of [i]P for i in [0, N); index 0 is the point
    at infinity (flag). Block method: [k]P + [jB]P vectorised over k."""
    xs = np.zeros(N, dtype=np.int64); ys = np.zeros(N, dtype=np.int64)
    base = [None]
    for k in range(1, B):
        base.append(E.add_pt(base[-1], P))
    bx = np.array([0] + [q[0] for q in base[1:]], dtype=np.int64)
    by = np.array([0] + [q[1] for q in base[1:]], dtype=np.int64)
    bi = np.zeros(B, dtype=bool); bi[0] = True
    SB = E.mul_pt(B, P)
    J = None  # [jB]P
    nblocks = (N + B - 1) // B
    for j in range(nblocks):
        lo = j * B; hi = min(N, lo + B)
        if J is None:
            xs[lo:hi] = bx[: hi - lo]; ys[lo:hi] = by[: hi - lo]
        else:
            jx = np.full(B, J[0], dtype=np.int64); jy = np.full(B, J[1], dtype=np.int64); ji = np.zeros(B, dtype=bool)
            x3, y3, i3 = E.add_vec(bx, by, bi, jx, jy, ji)
            assert not i3[: hi - lo].any() or (lo == 0)
            xs[lo:hi] = x3[: hi - lo]; ys[lo:hi] = y3[: hi - lo]
        J = E.add_pt(J, SB)
    return xs, ys


def index_lookup_table(xs, ys, p):
    keys = xs * p + ys
    order = np.argsort(keys, kind="stable")
    return keys[order], order


def lookup_index(sorted_keys, order, x, y, p):
    k = x * p + y
    pos = np.searchsorted(sorted_keys, k)
    pos = np.minimum(pos, sorted_keys.size - 1)
    found = sorted_keys[pos] == k
    return np.where(found, order[pos], -1), found


def walk_scalars(seed: int, r_walk: int, N: int) -> np.ndarray:
    """Seeded known scalars m_j in [1, N) for the r-adding steps; stream 700 + seed
    (executor choice: the contract names 'seeded known m_j', not the stream)."""
    rng = np.random.default_rng(700 + seed)
    return rng.integers(1, N, size=r_walk, dtype=np.int64)


def step_index_fn(xs: np.ndarray, K: int, r_walk: int) -> np.ndarray:
    """j(X) = hash(x(X)) mod r_walk over the enumerated group."""
    h = I.mix64(xs.astype(np.uint64) ^ np.uint64(K))
    return ((h >> np.uint64(32)) % np.uint64(r_walk)).astype(np.int64)


def online_walks_real(E: Curve, P, N: int, xs, ys, sorted_keys, order, K, K2, thr, cap, r_walk, m, rng, M):
    """M online walks on REAL points: target Q_i = [k_i]P, start Q_i + [c_i]P,
    r-adding steps X <- X + M_{j(x(X))} accumulating s; stop at the first DP or
    at cap. Returns terminal index (via lookup), reached, length, and the
    certificate inputs. Group ops: one per step; restart scalar mults counted
    separately."""
    k_true = rng.integers(1, N, size=M, dtype=np.int64)
    c = rng.integers(0, N, size=M, dtype=np.int64)
    Px = np.full(M, P[0], dtype=np.int64); Py = np.full(M, P[1], dtype=np.int64)
    Qx, Qy, Qi = E.mul_vec(k_true, Px, Py)
    Rx, Ry, Ri = E.mul_vec(c, Px, Py)
    x, y, inf = E.add_vec(Qx, Qy, Qi, Rx, Ry, Ri)
    Mx = np.array([E.mul_pt(int(mj), P)[0] for mj in m], dtype=np.int64)
    My = np.array([E.mul_pt(int(mj), P)[1] for mj in m], dtype=np.int64)
    s = np.zeros(M, dtype=np.int64); d = np.zeros(M, dtype=np.int64)
    active = ~(I.is_dp_fn(x, K2, thr) & ~inf)
    ops = 0
    for step in range(1, cap + 1):
        idx = np.flatnonzero(active)
        if idx.size == 0:
            break
        j = step_index_fn(x[idx], K, r_walk)
        nx, ny, ni = E.add_vec(x[idx], y[idx], inf[idx], Mx[j], My[j], np.zeros(idx.size, dtype=bool))
        ops += idx.size
        x[idx] = nx; y[idx] = ny; inf[idx] = ni
        s[idx] = (s[idx] + m[j]) % N
        d[idx] = step
        active[idx] = ~(I.is_dp_fn(nx, K2, thr) & ~ni)
    reached = ~active
    term, found = lookup_index(sorted_keys, order, x, y, E.p)
    term = np.where(reached & found, term, 0)
    length = np.where(reached, d, cap)
    start_idx, _ = lookup_index(sorted_keys, order, *E.add_vec(Qx, Qy, Qi, Rx, Ry, Ri)[:2], E.p)
    return term, reached, length, {"k_true": k_true, "c": c, "s": s, "Q": np.stack([Qx, Qy], 1),
                                   "start_index": start_idx, "online_group_ops": int(ops),
                                   "restart_scalar_mults": int(2 * M), "restart_note": "Q_i = [k_i]P (instance) and [c_i]P (randomisation) by vectorised double-and-add; counted separately, excluded from L",
                                   "lookups": int(M), "walks_hit_infinity": int(inf.sum())}
