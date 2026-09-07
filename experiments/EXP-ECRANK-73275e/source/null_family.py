"""R6 null family -- FROZEN before any R6 step.

Derived from the committed d = 1 Mestre closed form at n = 6: the
ellipticity condition is a univariate quadratic A t^2 + B t + C = 0 in
the monic-linear coefficient t of g = x + t. The null variant keeps A
and B and replaces C by a sign-forced constant C_null so that

    A * C_null > 0  and  B^2 - 4 A C_null < 0.

Then the discriminant is strictly negative, so there is no real root
and therefore no rational in-box root. This is a proof of infeasibility
for the frozen family, not an empirical scan.

The formula is frozen here and must not change after R6 begins.
"""

from fractions import Fraction as Fr


def d1_quadratic_coeffs(engine, b):
    """Return (A, B, C) of the n = 6 ellipticity quadratic in t at d = (1..1).

    g = x + t; s = (delta * g^2) mod p; A t^2 + B t + C is the
    coefficient of x^5 of s (the unique ellipticity condition).
    """
    xs = [Fr(x) for x in b]
    assert len(xs) == 6
    dpat = [Fr(1)] * 6
    delta = engine.lagrange_interp(xs, dpat)
    p = engine.prod_linear(xs)
    # g^2 = t^2 + 2 t x + x^2  -> polys [t^2], [2t], [1] in x
    # Evaluate high-coeff of (delta * g^2 mod p) at t = 0, 1, -1 and
    # interpolate the quadratic. Counted as exact Fraction ops.
    def high5(t):
        g = [Fr(t), Fr(1)]
        s = engine.polymod_monic(engine.pmul(delta, engine.pmul(g, g)), p)
        s = s + [Fr(0)] * (6 - len(s))
        return s[5] if len(s) > 5 else Fr(0)

    y0 = high5(Fr(0))
    y1 = high5(Fr(1))
    ym = high5(Fr(-1))
    # y = A t^2 + B t + C; C = y0; A = ((y1 + ym) / 2) - C; B = (y1 - ym) / 2
    C = y0
    A = (y1 + ym) / Fr(2) - C
    B = (y1 - ym) / Fr(2)
    return A, B, C


def null_constant(A, B, C):
    """Sign-forced C_null making disc < 0 and A C_null > 0."""
    if A == 0:
        # Degenerate in t^2: force a never-zero constant equation 1 = 0
        # by returning a sentinel that the solver treats as no-root.
        # The proof is: A = 0 and we replace the condition by 1 = 0.
        return Fr(1) if C == 0 else (C if C * Fr(1) > 0 else -C + Fr(1))
    # Need 4 A C_null > B^2 and A C_null > 0.
    # Take C_null = sign(A) * (abs(B)^2 + 1 + abs(A)) / (4 abs(A)) * something
    # Integers: C_null = sign(A) * (B^2 + 1 + 4 |A|) / (4 |A|)  rounded up.
    absA = A if A > 0 else -A
    target = (B * B + Fr(1)) / (Fr(4) * absA) + Fr(1)
    # target > B^2 / (4 |A|); C_null = sign(A) * target
    C_null = target if A > 0 else -target
    # Guarantee A C_null > 0
    if A * C_null <= 0:
        C_null = -C_null if C_null != 0 else (Fr(1) if A > 0 else Fr(-1))
    return C_null


def disc(A, B, C):
    return B * B - Fr(4) * A * C


def infeasible_proof(A, B, C_null):
    d = disc(A, B, C_null)
    return {
        "A": str(A),
        "B": str(B),
        "C_null": str(C_null),
        "discriminant": str(d),
        "A_C_null_positive": bool(A * C_null > 0) if A != 0 else False,
        "disc_negative": bool(d < 0),
        "no_real_root": bool(d < 0) or (A == 0 and C_null != 0 and B == 0),
        "proof": (
            "Null family: keep A, B from the d=1 n=6 ellipticity quadratic "
            "and replace C by C_null = sign(A)*((B^2+1)/(4|A|)+1). Then "
            "A C_null > 0 and B^2 - 4 A C_null < 0, so the quadratic has "
            "no real root and therefore no rational in-box root."
        ),
    }
