#!/usr/bin/env python3
"""Classical mirror of the two EXP-CSIDH-906d0e circuit algorithms.

Every function here mirrors, step for step, the frozen algorithms of
Circuit-F and Circuit-I in experiments/EXP-CSIDH-906d0e/specification.yaml,
using unbounded Python integers. run.py compares circuit output values
against this mirror; check.py re-derives reading rows from it. The mirror
is also the reference for the --self-test machinery check at other
discriminants. It states no width and no security claim.
"""
from __future__ import annotations

from math import gcd


def enumerate_reduced_forms(disc: int) -> list[tuple[int, int, int]]:
    """Reduced positive-definite forms (a, b, c), b^2 - 4ac = disc.

    Convention: -a < b <= a <= c, b >= 0 when |b| = a or a = c, lexicographic
    output order by (a, b, c).
    """
    if disc >= 0:
        raise ValueError("discriminant must be negative")
    out = []
    a = 1
    while a * a <= -disc // 3 + 1:
        for b in range(-a + 1, a + 1):
            num = b * b - disc
            if num % (4 * a):
                continue
            c = num // (4 * a)
            if c < a:
                continue
            if abs(b) == a or a == c:
                if b < 0:
                    continue
            out.append((a, b, c))
        a += 1
    out.sort()
    return out


def is_reduced(a: int, b: int, c: int) -> bool:
    if not (-a < b <= a <= c):
        return False
    if (abs(b) == a or a == c) and b < 0:
        return False
    return True


def gauss_reduce(a: int, b: int, c: int, disc: int) -> tuple[int, int, int]:
    """Gauss reduction, mirroring the frozen 8-iteration circuit loop.

    The circuit unrolls exactly 8 idempotent iterations; the mirror runs
    the same steps (raising if 8 do not suffice, matching the refusal).
    """
    a_, b_, c_ = a, b, c
    for _ in range(8):
        if not is_reduced(a_, b_, c_):
            # b <- b mod 2a into (-a, a]
            r = b_ % (2 * a_)
            if r > a_:
                r -= 2 * a_
            b_ = r
            c_ = (b_ * b_ - disc) // (4 * a_)
            if a_ > c_:
                a_, c_ = c_, a_
                b_ = -b_
            if a_ == c_ and b_ < 0:
                b_ = -b_
    if not is_reduced(a_, b_, c_):
        raise ValueError("not reduced after 8 iterations")
    return a_, b_, c_


def validate_forms(f1: tuple[int, int, int], f2: tuple[int, int, int], disc: int) -> bool:
    """Parity and discriminant equations for both forms; b odd, disc match."""
    for (a, b, c) in (f1, f2):
        if b % 2 == 0:
            return False
        if b * b - 4 * a * c != disc:
            return False
        if a <= 0:
            return False
    return True


def compose_dirichlet(f1: tuple[int, int, int], f2: tuple[int, int, int],
                      disc: int) -> tuple[int, int, int]:
    """Circuit-F's algorithm classically: T-fix, gcd=1, CRT, reduce.

    Raises ValueError where the circuit raises a refusal flag.
    """
    if not validate_forms(f1, f2, disc):
        raise ValueError("input validation refusal")
    (a1, b1, c1) = f1
    (a2, b2, c2) = f2
    # (ii) unimodularity fix: replace the first form by an equivalent one
    # until gcd(a1, a2) = 1, at most 3 times. The CRT congruence
    # b1 = b2 (mod 2) holds structurally because both b's are odd.
    for _ in range(3):
        if gcd(a1, a2) == 1:
            break
        a1, b1, c1 = a1 + b1 + c1, b1 + 2 * c1, c1
    if gcd(a1, a2) != 1:
        raise ValueError("unimodularity refusal")
    # (iv) CRT: B = b1 mod 2a1, B = b2 mod 2a2
    m1 = 2 * a1
    # B = b1 + m1 * t, t = ((b2 - b1)/2) * inv(a1) mod a2
    half = (b2 - b1) // 2
    inv = pow(a1, -1, a2)
    t = (half % a2) * inv % a2
    bmid = b1 + m1 * t
    amid = a1 * a2
    cmid = (bmid * bmid - disc) // (4 * amid)
    if (bmid * bmid - disc) % (4 * amid):
        raise ValueError("non-integral composite")
    return gauss_reduce(amid, bmid, cmid, disc)


def ideal_generators(f1: tuple[int, int, int], f2: tuple[int, int, int],
                    disc: int) -> tuple[list[tuple[int, int]], int, int]:
    """Circuit-I steps (i)-(iii): ring products of the two ideals.

    omega^2 = omega + (disc - 1) / 4. Returns the four product generators
    as (constant, omega) coordinate pairs plus m1, m2.
    """
    if not validate_forms(f1, f2, disc):
        raise ValueError("input validation refusal")
    (a1, b1, c1) = f1
    (a2, b2, c2) = f2
    m1 = (-b1 - 1) // 2
    m2 = (-b2 - 1) // 2
    omega_const = (disc - 1) // 4  # omega^2 = omega + omega_const
    gens = [
        (a1 * a2, 0),
        (a1 * m2 - omega_const * 0, a1),  # (a1,0)*(m2,1)
        (a2 * m1, a2),                   # (m1,1)*(a2,0)
        (m1 * m2 + omega_const, m1 + m2 + 1),  # (m1,1)*(m2,1)
    ]
    # ring product (x1,y1)*(x2,y2) = (x1x2 + omega_const*y1y2, x1y2+x2y1+y1y2)
    # (a1,0)*(m2,1): (a1*m2, a1*1) -- no omega_const term since y1 = 0
    return gens, m1, m2


def normalize_lattice(gens: list[tuple[int, int]]) -> tuple[int, int, int]:
    """Circuit-I step (iv): content k, h1, M from the four generators.

    Mirrors the ext-gcd column reduction: h3 = gcd of omega coordinates,
    column combinations isolate one omega-column and zero-columns,
    h1 = gcd of the constant coordinates of the zero-columns. Raises when
    h3 != k or the lattice is degenerate.
    """
    xs = [g[0] for g in gens]
    ys = [g[1] for g in gens]
    k = 0
    for v in xs + ys:
        k = gcd(k, v)
    h3 = 0
    for v in ys:
        h3 = gcd(h3, v)
    if h3 == 0:
        raise ValueError("degenerate lattice")
    if h3 != k:
        raise ValueError("h3 != k refusal")
    # column reduction, mirroring the two ext-gcd combinations:
    # (s,t) on columns 2,3 then on (g, y4). Columns: c1 (y=0 always),
    # c2, c3, c4.
    c1, c2, c3, c4 = gens
    g23 = gcd(ys[1], ys[2])
    # ext-gcd coefficients for (a1, a2)
    s, t = _ext_gcd(ys[1], ys[2])
    cA = (s * c2[0] + t * c3[0], s * c2[1] + t * c3[1])
    cB = ((ys[2] // g23) * c2[0] - (ys[1] // g23) * c3[0],
          (ys[2] // g23) * c2[1] - (ys[1] // g23) * c3[1])
    s2, t2 = _ext_gcd(g23, ys[3])
    cW = (s2 * cA[0] + t2 * c4[0], s2 * cA[1] + t2 * c4[1])
    cC = ((ys[3] // gcd(g23, ys[3])) * cA[0] - (g23 // gcd(g23, ys[3])) * c4[0],
          (ys[3] // gcd(g23, ys[3])) * cA[1] - (g23 // gcd(g23, ys[3])) * c4[1])
    h1 = gcd(gcd(c1[0], cB[0]), cC[0])
    if h1 == 0:
        raise ValueError("degenerate h1")
    A = h1 // k
    if h1 % k:
        raise ValueError("h1 not divisible by k")
    M = (cW[0] // k) % A
    if cW[0] % k:
        raise ValueError("omega column not divisible by k")
    return A, M, h1


def compose_ideals(f1: tuple[int, int, int], f2: tuple[int, int, int],
                  disc: int) -> tuple[int, int, int]:
    """Circuit-I's algorithm classically: ring products, lattice, reduce."""
    gens, _m1, _m2 = ideal_generators(f1, f2, disc)
    A, M, _h1 = normalize_lattice(gens)
    b = -2 * M - 1
    c = (b * b - disc) // (4 * A)
    if (b * b - disc) % (4 * A):
        raise ValueError("non-integral form")
    return gauss_reduce(A, b, c, disc)


def _ext_gcd(a: int, b: int) -> tuple[int, int]:
    """Bezout (s, t) with s*a + t*b = gcd(a, b) >= 0; mirrors circuit ext_gcd."""
    old_r, r = abs(a), abs(b)
    old_s, s = 1, 0
    old_t, t = 0, 1
    while r != 0:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_s, s = s, old_s - q * s
        old_t, t = t, old_t - q * t
    if old_r < 0:
        old_s, old_t = -old_s, -old_t
    if b < 0:
        old_t = -old_t
    return old_s, old_t


def group_table_check(forms: list[tuple[int, int, int]], disc: int) -> bool:
    """Both compositions agree wherever the frozen algorithm composes.

    Pairs the frozen unimodular algorithm refuses (gcd(a1, a2) stays
    above 1 after three equivalent-form replacements) are skipped: the
    frozen cell never scores them. On every composable pair the two
    classical paths must agree, the principal form must act as the
    identity on composable pairs, and composable composition must be
    associative wherever all three products are composable.
    """
    n = len(forms)
    ident = None
    for i, f in enumerate(forms):
        if f == (1, 1, (1 - disc) // 4):
            ident = i
            break
    if ident is None:
        return False
    composable: set[tuple[int, int]] = set()
    for i, f in enumerate(forms):
        for j, g in enumerate(forms):
            try:
                cf = compose_dirichlet(f, g, disc)
                ci = compose_ideals(f, g, disc)
            except ValueError:
                continue
            if cf != ci:
                return False
            composable.add((i, j))
    if not composable:
        return False
    for (i, j) in composable:
        # principal identity on composable pairs
        if i == ident and compose_dirichlet(forms[i], forms[j], disc) != forms[j]:
            return False
        if j == ident and compose_dirichlet(forms[i], forms[j], disc) != forms[i]:
            return False
    for (i, j) in composable:
        ij = compose_dirichlet(forms[i], forms[j], disc)
        k = forms.index(ij)
        for l in range(n):
            if (k, l) not in composable or (j, l) not in composable:
                continue
            jl = compose_dirichlet(forms[j], forms[l], disc)
            m = forms.index(jl)
            if (i, m) not in composable:
                continue
            if compose_dirichlet(forms[k], forms[l], disc) != compose_dirichlet(forms[i], forms[m], disc):
                return False
    return True
