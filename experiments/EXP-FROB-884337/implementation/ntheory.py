"""Field and curve arithmetic for EXP-FROB-884337.

F_343 = F_7[z] / (z^3 + a z^2 + b z + c), with the monic irreducible of
least (a, b, c) in lexicographic order. Elements are integers
c0 + 7 c1 + 49 c2. This module does not score the claim.
"""

from __future__ import annotations

P = 7
EXT = 343  # 7**3
NORM_EXP = (EXT - 1) // (P - 1)  # 57


def _digits(u: int) -> list[int]:
    return [u % P, (u // P) % P, (u // (P * P)) % P]


def _pack(c0: int, c1: int, c2: int) -> int:
    return (c0 % P) + P * (c1 % P) + (P * P) * (c2 % P)


def irreducible() -> tuple[int, int, int]:
    """Least monic cubic with no root. A cubic over a field is irreducible then."""
    for a in range(P):
        for b in range(P):
            for c in range(P):
                if all((x * x * x + a * x * x + b * x + c) % P != 0 for x in range(P)):
                    return (a, b, c)
    raise RuntimeError("no irreducible cubic over F_7")


POLY = irreducible()


def fadd(u: int, v: int) -> int:
    cu, cv = _digits(u), _digits(v)
    return _pack(cu[0] + cv[0], cu[1] + cv[1], cu[2] + cv[2])


def fsub(u: int, v: int) -> int:
    cu, cv = _digits(u), _digits(v)
    return _pack(cu[0] - cv[0], cu[1] - cv[1], cu[2] - cv[2])


def fneg(u: int) -> int:
    return fsub(0, u)


def fmul(u: int, v: int) -> int:
    a, b, c = POLY
    cu, cv = _digits(u), _digits(v)
    prod = [0, 0, 0, 0, 0]
    for i in range(3):
        for j in range(3):
            prod[i + j] = (prod[i + j] + cu[i] * cv[j]) % P
    # z^4 = (a^2 - b) z^2 + (a b - c) z + a c, from z^3 = -a z^2 - b z - c.
    k4 = prod[4]
    prod[0] = (prod[0] + k4 * (a * c)) % P
    prod[1] = (prod[1] + k4 * (a * b - c)) % P
    prod[2] = (prod[2] + k4 * (a * a - b)) % P
    k3 = prod[3]
    prod[0] = (prod[0] + k3 * (-c)) % P
    prod[1] = (prod[1] + k3 * (-b)) % P
    prod[2] = (prod[2] + k3 * (-a)) % P
    return _pack(prod[0], prod[1], prod[2])


def fpow(u: int, n: int) -> int:
    result = 1
    base = u
    e = n
    while e:
        if e & 1:
            result = fmul(result, base)
        base = fmul(base, base)
        e >>= 1
    return result


def finv(u: int) -> int:
    if u == 0:
        raise ZeroDivisionError("inverse of zero")
    return fpow(u, EXT - 2)


def in_subfield(u: int) -> bool:
    return u < P


def norm(u: int) -> int:
    """Field norm F_343 -> F_7. Zero maps to zero. A subfield element maps to its cube."""
    if u == 0:
        return 0
    return fpow(u, NORM_EXP)


def curve_rhs(x: int) -> int:
    # x^3 + x + 1
    return fadd(fadd(fmul(fmul(x, x), x), x), 1)


def discriminant() -> int:
    # 4 A^3 + 27 B^2 with A = B = 1, reduced mod 7.
    return (4 + 27) % P


def affine_points() -> list[tuple[int, int]]:
    pts: list[tuple[int, int]] = []
    for x in range(EXT):
        rhs = curve_rhs(x)
        for y in range(EXT):
            if fmul(y, y) == rhs:
                pts.append((x, y))
    pts.sort()
    return pts


def add(p: tuple[int, int] | None, q: tuple[int, int] | None) -> tuple[int, int] | None:
    if p is None:
        return q
    if q is None:
        return p
    x1, y1 = p
    x2, y2 = q
    if x1 == x2:
        if fadd(y1, y2) == 0:
            return None
        lam = fmul(fadd(fmul(3, fmul(x1, x1)), 1), finv(fmul(2, y1)))
    else:
        lam = fmul(fsub(y2, y1), finv(fsub(x2, x1)))
    x3 = fsub(fsub(fmul(lam, lam), x1), x2)
    y3 = fsub(fmul(lam, fsub(x1, x3)), y1)
    return (x3, y3)


def branching(points: list[tuple[int, int]], label) -> dict:
    """(L, b) from IDEA-20260802-002.

    b is the mean, over ordered pairs of image labels, of the number of
    distinct labels of A+B. Sums equal to the point at infinity are omitted
    from that set. Two summation orders are accumulated and must match.
    """
    fibres: dict = {}
    for pt in points:
        fibres.setdefault(label(pt), []).append(pt)
    image = list(fibres)
    k = len(image)
    if k == 0:
        return {
            "n_points": 0,
            "n_image": 0,
            "b_num": 0,
            "b_den": 0,
            "b_num_swapped": 0,
            "max_fanout": 0,
            "loops_agree": True,
        }
    total = 0
    total_swap = 0
    max_fan = 0
    for s in image:
        for t in image:
            vals: set = set()
            vals_swap: set = set()
            for left in fibres[s]:
                for right in fibres[t]:
                    sum_ab = add(left, right)
                    if sum_ab is not None:
                        vals.add(label(sum_ab))
                    sum_ba = add(right, left)
                    if sum_ba is not None:
                        vals_swap.add(label(sum_ba))
            total += len(vals)
            total_swap += len(vals_swap)
            if len(vals) > max_fan:
                max_fan = len(vals)
    return {
        "n_points": len(points),
        "n_image": k,
        "b_num": total,
        "b_den": k * k,
        "b_num_swapped": total_swap,
        "max_fanout": max_fan,
        "loops_agree": total == total_swap,
    }
