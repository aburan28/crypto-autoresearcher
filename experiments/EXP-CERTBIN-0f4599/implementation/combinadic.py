"""Twin stars-and-bars counters and subspace helpers for EXP-CERTBIN-0f4599."""
from __future__ import annotations


def binom_path_a(n: int, k: int) -> int:
    if k < 0 or n < k:
        return 0
    k = min(k, n - k)
    num = 1
    den = 1
    for i in range(k):
        num *= n - i
        den *= i + 1
    return num // den


def stars_and_bars_c(B: int, m: int) -> int:
    """C(B + m - 1, m) — unordered m-multisets of a B-set."""
    return binom_path_a(B + m - 1, m)


def stars_and_bars_c_loop(B: int, m: int) -> int:
    """Independent path: nested nondecreasing loops for m = 3 only."""
    if m != 3:
        raise ValueError("loop twin is defined for m=3")
    c = 0
    for i in range(B):
        for j in range(i, B):
            for _k in range(j, B):
                c += 1
    return c


def c_agree(B: int, m: int = 3) -> tuple[int, int, bool]:
    a = stars_and_bars_c(B, m)
    b = stars_and_bars_c_loop(B, m) if m == 3 else stars_and_bars_c(B, m)
    return a, b, a == b


def rank_span(vectors: list[int], n: int) -> int:
    rows = list(vectors)
    rank = 0
    used = [False] * len(rows)
    for col in range(n):
        piv = None
        for i, v in enumerate(rows):
            if used[i]:
                continue
            if (v >> col) & 1:
                piv = i
                break
        if piv is None:
            continue
        used[piv] = True
        rank += 1
        pv = rows[piv]
        for i, v in enumerate(rows):
            if i != piv and ((v >> col) & 1):
                rows[i] ^= pv
    return rank


def span_list(basis: list[int], n: int) -> list[int]:
    out = [0]
    for b in basis:
        out.extend([v ^ b for v in list(out)])
    return sorted(set(out))


def dim_intersection(basis_v: list[int], basis_w: list[int], n: int) -> int:
    dv = rank_span(basis_v, n)
    dw = rank_span(basis_w, n)
    ds = rank_span(list(basis_v) + list(basis_w), n)
    return dv + dw - ds


class XorShift64:
    def __init__(self, seed: int) -> None:
        self.s = seed & 0xFFFFFFFFFFFFFFFF
        if self.s == 0:
            self.s = 0x9E3779B97F4A7C15

    def u64(self) -> int:
        x = self.s
        x ^= (x << 13) & 0xFFFFFFFFFFFFFFFF
        x ^= x >> 7
        x ^= (x << 17) & 0xFFFFFFFFFFFFFFFF
        self.s = x & 0xFFFFFFFFFFFFFFFF
        return self.s

    def bits(self, n: int) -> int:
        mask = (1 << n) - 1
        return self.u64() & mask


def random_basis(n: int, ell: int, rng: XorShift64) -> list[int]:
    basis: list[int] = []
    guard = 0
    while len(basis) < ell and guard < 10_000:
        guard += 1
        v = rng.bits(n)
        if v == 0:
            continue
        if rank_span(basis + [v], n) == len(basis) + 1:
            basis.append(v)
    if len(basis) != ell:
        raise RuntimeError("failed to sample full-rank basis")
    return basis
