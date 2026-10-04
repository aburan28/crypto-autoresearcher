"""Dual S_3 / resultant routes for EXP-SATIC-ba99a8. No Sage/Magma.

Route school: S3 = (xy+xz+yz)^2 + xyz + B  (left-to-right products).
Route expand: S3(a,b,X) = (a+b)^2 X^2 + (ab) X + (ab)^2 + B  (idea formula).
Amazon Bedrock is not selected.
"""
from __future__ import annotations

from gf2n import Field


def s3_school(F: Field, x: int, y: int, z: int, B: int) -> int:
    xy = F.mul(x, y)
    xz = F.mul(x, z)
    yz = F.mul(y, z)
    return F.sqr(xy ^ xz ^ yz) ^ F.mul(xy, z) ^ B


def s3_expand(F: Field, a: int, b: int, x: int, B: int) -> int:
    """KN-TECH-b18366 / IDEA-20260930-c5466b rearranged S_3(a,b,X)."""
    s = a ^ b
    p = F.mul(a, b)
    return F.mul(F.sqr(s), F.sqr(x)) ^ F.mul(p, x) ^ F.sqr(p) ^ B


def quad_coeffs_s3(F: Field, a: int, b: int, B: int) -> tuple[int, int, int]:
    """S_3(a,b,X) = A X^2 + Lin X + C."""
    s = a ^ b
    p = F.mul(a, b)
    return F.sqr(s), p, F.sqr(p) ^ B


def quad_roots(F: Field, A: int, lin: int, C: int) -> tuple[int, int] | None:
    """Roots of A X^2 + lin X + C over F_{2^n}, n odd. None if no roots."""
    if A == 0:
        if lin == 0:
            return (0, 0) if C == 0 else None
        r = F.mul(C, F.inv(lin))
        return (r, r)
    invA = F.inv(A)
    b = F.mul(lin, invA)
    c = F.mul(C, invA)
    if b == 0:
        r = F.sqrt(c)
        return (r, r)
    rhs = F.mul(c, F.inv(F.sqr(b)))
    if F.trace(rhs) != 0:
        return None
    z = F.half_trace(rhs)
    r0 = F.mul(b, z)
    r1 = F.mul(b, z ^ 1)
    return (r0, r1)


def det2(F: Field, a: int, b: int, c: int, d: int) -> int:
    return F.mul(a, d) ^ F.mul(b, c)


def det3(
    F: Field,
    a11: int, a12: int, a13: int,
    a21: int, a22: int, a23: int,
    a31: int, a32: int, a33: int,
) -> int:
    return (
        F.mul(a11, det2(F, a22, a23, a32, a33))
        ^ F.mul(a12, det2(F, a21, a23, a31, a33))
        ^ F.mul(a13, det2(F, a21, a22, a31, a32))
    )


def det4(F: Field, m: list[list[int]]) -> int:
    s = 0
    for j in range(4):
        minor = [[m[r][c] for c in range(4) if c != j] for r in range(1, 4)]
        s ^= F.mul(m[0][j], det3(F, *minor[0], *minor[1], *minor[2]))
    return s


def resultant_sylvester(F: Field, f: tuple[int, int, int], g: tuple[int, int, int]) -> int:
    a2, a1, a0 = f
    b2, b1, b0 = g
    m = [
        [a2, a1, a0, 0],
        [0, a2, a1, a0],
        [b2, b1, b0, 0],
        [0, b2, b1, b0],
    ]
    return det4(F, m)


def product_side(F: Field, a: int, x2: int, x3: int, x_r: int, B: int) -> int | None:
    """(a+x_R)^4 S3(x2,x3,u+) S3(x2,x3,u-) with u from G = S3(X,a,x_R)."""
    g = quad_coeffs_s3(F, a, x_r, B)
    roots = quad_roots(F, *g)
    if roots is None:
        return None
    u_plus, u_minus = roots
    lc = a ^ x_r
    pre = F.sqr(F.sqr(lc))
    gp = s3_expand(F, x2, x3, u_plus, B)
    gm = s3_expand(F, x2, x3, u_minus, B)
    return F.mul(pre, F.mul(gp, gm))


def identity_pair(
    F: Field, a: int, x2: int, x3: int, x_r: int, B: int
) -> dict[str, int | bool | None]:
    f = quad_coeffs_s3(F, x2, x3, B)
    g = quad_coeffs_s3(F, a, x_r, B)
    syl = resultant_sylvester(F, f, g)
    prod = product_side(F, a, x2, x3, x_r, B)
    school_at = None
    if prod is not None:
        # Cross-check S3 school vs expand at the two roots.
        roots = quad_roots(F, *g)
        assert roots is not None
        s_ok = True
        for u in roots:
            if s3_school(F, x2, x3, u, B) != s3_expand(F, x2, x3, u, B):
                s_ok = False
        school_at = s_ok
    agree = prod is not None and syl == prod
    return {
        "sylvester": syl,
        "product": prod,
        "agree": agree,
        "school_expand_agree": school_at,
        "degenerate_a_eq_xr": a == x_r,
    }
