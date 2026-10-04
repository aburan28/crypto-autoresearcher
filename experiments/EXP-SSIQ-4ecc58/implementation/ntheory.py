"""Integer / matrix arithmetic for EXP-SSIQ-4ecc58 (ordered-key holonomy census).

No Magma/Sage. No Bedrock. Not an attack. Quaternion order of B_{p,infinity}
and GL_2(Z/N) matrices only.
"""
from __future__ import annotations

from typing import Iterable


def miller_rabin(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if a >= n:
            continue
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def next_prime_3mod4(lo: int) -> int:
    n = lo if lo % 2 else lo + 1
    while True:
        if n % 4 == 3 and miller_rabin(n):
            return n
        n += 2


def integer_nth_root(n: int, k: int) -> int:
    if n < 0 or k < 1:
        raise ValueError("nth_root domain")
    if n < 2:
        return n
    x = 1 << ((n.bit_length() + k - 1) // k)
    while True:
        y = ((k - 1) * x + n // pow(x, k - 1)) // k
        if y >= x:
            return x
        x = y


def nrd_half(A: int, B: int, C: int, D: int, p: int) -> int:
    """Reduced norm of (A + B i + C j + D k)/2."""
    s = A * A + B * B + p * (C * C + D * D)
    if s % 4:
        return -1
    return s // 4


def is_smooth_23(n: int, max_sum: int = 8) -> tuple[int, int] | None:
    if n <= 0:
        return None
    a = 0
    while n % 2 == 0:
        n //= 2
        a += 1
    b = 0
    while n % 3 == 0:
        n //= 3
        b += 1
    if n != 1 or a + b > max_sum:
        return None
    return a, b


def enumerate_order_elements(p: int, max_sum: int = 12, coord: int = 4) -> list[tuple[int, int, int, int, int]]:
    """Elements of O = Z<1,i,(1+j)/2,(i+k)/2> with Nrd in {2^a 3^b : 0 < a+b <= max_sum}.

    Represent α = (A+Bi+Cj+Dk)/2 with A≡C, B≡D (mod 2).
    Returns list of (A,B,C,D,nrd).
    """
    out: list[tuple[int, int, int, int, int]] = []
    seen: set[tuple[int, int, int, int]] = set()
    for C in range(-coord, coord + 1):
        for D in range(-coord, coord + 1):
            for A in range(-coord * 2, coord * 2 + 1):
                if (A - C) % 2:
                    continue
                for B in range(-coord * 2, coord * 2 + 1):
                    if (B - D) % 2:
                        continue
                    key = (A, B, C, D)
                    if key in seen:
                        continue
                    nrd = nrd_half(A, B, C, D, p)
                    if nrd < 1:
                        continue
                    if is_smooth_23(nrd, max_sum) is None:
                        continue
                    seen.add(key)
                    out.append((A, B, C, D, nrd))
    return out


def enumerate_spine_elements(p: int, max_sum: int = 12, coord: int = 4) -> list[tuple[int, int, int, int, int]]:
    """Z[j] = Z[sqrt(-p)] slice: B=D=0."""
    return [t for t in enumerate_order_elements(p, max_sum, coord) if t[1] == 0 and t[3] == 0]


# --- GL_2(Z/N) matrices as (a,b,c,d) meaning [[a,b],[c,d]] ---

Mat = tuple[int, int, int, int]


def mmod(m: Mat, n: int) -> Mat:
    return (m[0] % n, m[1] % n, m[2] % n, m[3] % n)


def mmul(x: Mat, y: Mat, n: int) -> Mat:
    a, b, c, d = x
    e, f, g, h = y
    return mmod((a * e + b * g, a * f + b * h, c * e + d * g, c * f + d * h), n)


def mdet(m: Mat, n: int) -> int:
    return (m[0] * m[3] - m[1] * m[2]) % n


def minv(m: Mat, n: int) -> Mat | None:
    det = mdet(m, n)
    try:
        invd = pow(det, -1, n)
    except ValueError:
        return None
    a, b, c, d = m
    return mmod((d * invd, (-b) * invd, (-c) * invd, a * invd), n)


def mid(n: int) -> Mat:
    return (1 % n, 0, 0, 1 % n)


def split_ij(n: int, p: int) -> tuple[Mat, Mat] | None:
    """i^2 = -I, j^2 = -p I, ij = -ji, over Z/n (n odd)."""
    if n % 2 == 0:
        return None
    i_mat: Mat = (0, (-1) % n, 1 % n, 0)
    target = (-p) % n
    for a in range(n):
        for b in range(n):
            if (a * a + b * b) % n == target:
                j_mat: Mat = mmod((a, b, b, (-a) % n), n)
                # anticommute: i j + j i = 0
                s = mmul(i_mat, j_mat, n)
                t = mmul(j_mat, i_mat, n)
                zero = mmod((s[0] + t[0], s[1] + t[1], s[2] + t[2], s[3] + t[3]), n)
                if zero != (0, 0, 0, 0):
                    continue
                jj = mmul(j_mat, j_mat, n)
                if jj != mmod(((-p) % n, 0, 0, (-p) % n), n):
                    continue
                ii = mmul(i_mat, i_mat, n)
                if ii != mmod(((-1) % n, 0, 0, (-1) % n), n):
                    continue
                return i_mat, j_mat
    return None


def quat_to_mat(A: int, B: int, C: int, D: int, n: int, i_mat: Mat, j_mat: Mat) -> Mat | None:
    """Map (A+Bi+Cj+Dk)/2 using 2^{-1} mod n (n odd)."""
    try:
        inv2 = pow(2, -1, n)
    except ValueError:
        return None
    k_mat = mmul(i_mat, j_mat, n)
    acc = mmod((A % n, 0, 0, A % n), n)
    # add B * i
    bi = mmod((B * i_mat[0], B * i_mat[1], B * i_mat[2], B * i_mat[3]), n)
    acc = mmod((acc[0] + bi[0], acc[1] + bi[1], acc[2] + bi[2], acc[3] + bi[3]), n)
    cj = mmod((C * j_mat[0], C * j_mat[1], C * j_mat[2], C * j_mat[3]), n)
    acc = mmod((acc[0] + cj[0], acc[1] + cj[1], acc[2] + cj[2], acc[3] + cj[3]), n)
    dk = mmod((D * k_mat[0], D * k_mat[1], D * k_mat[2], D * k_mat[3]), n)
    acc = mmod((acc[0] + dk[0], acc[1] + dk[1], acc[2] + dk[2], acc[3] + dk[3]), n)
    return mmod((acc[0] * inv2, acc[1] * inv2, acc[2] * inv2, acc[3] * inv2), n)


def gl2_order(n: int) -> int:
    # |GL_2(F_q)| = (q^2-1)(q^2-q) for prime n
    if not miller_rabin(n):
        return -1
    return (n * n - 1) * (n * n - n)


def sl2_order(n: int) -> int:
    if not miller_rabin(n):
        return -1
    return n * (n - 1) * (n + 1)


def det_group_S(n: int, S: Iterable[int]) -> set[int]:
    gens = {s % n for s in S if s % n != 0}
    out = {1 % n}
    changed = True
    while changed:
        changed = False
        nxt = set(out)
        for g in out:
            for s in gens:
                v = (g * s) % n
                if v not in nxt:
                    nxt.add(v)
                    changed = True
        out = nxt
    return out
