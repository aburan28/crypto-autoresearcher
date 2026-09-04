#!/usr/bin/env python3
"""R3 (TASK-20260904-ed0e8f, red team): is H-TOP (HEUR-001) checked at m = 4?

The package checked m = 2 (by hand) and m = 3 (sympy resultant) and recorded
'm = 4 (S_5) was not attempted'.  H-PFDR-4148b8 quantifies H-TOP over ALL
m >= 2, so m = 4 is the first unchecked case of a load-bearing heuristic.

Cheap decisive test.  S_5 has per-variable degree 2^3 = 8 in each of
x_1..x_4, so the ONLY monomial of total degree 32 with every exponent <= 8 is
x_1^8 x_2^8 x_3^8 x_4^8.  Therefore H-TOP at m = 4 reduces to:
   (i)  deg_{(x_1..x_4)} S_5 = 32, and
   (ii) the coefficient of x_1^8 x_2^8 x_3^8 x_4^8 is a nonzero constant.
Both are read off a ONE-VARIABLE specialisation: put x_k = c_k t and read the
leading term in t.  With per-variable degree <= 8 the t^32 coefficient equals
coeff(8,8,8,8) * prod c_k^8, so dividing by prod c_k^8 recovers the
coefficient itself.  Repeating over several random c and several random
(a, b, x_R) tests both that it is nonzero and that it does not depend on the
curve or the target.

Also re-derives the per-variable degree by a second specialisation, and
re-does the same test at m = 3 as a positive control (expect c = 1).
"""
import json
import random
import sys
import sympy as sp

t, T, U = sp.symbols("t T U")


def S3(x1, x2, x3, a, b):
    return sp.expand((x1 - x2) ** 2 * x3 ** 2
                     - 2 * ((x1 + x2) * (x1 * x2 + a) + 2 * b) * x3
                     + (x1 * x2 - a) ** 2 - 4 * b * (x1 + x2))


def S4(x1, x2, x3, V, a, b):
    """S_4(x1, x2, x3, V) = Res_U(S_3(x1, x2, U), S_3(x3, V, U))."""
    f = sp.Poly(S3(x1, x2, U, a, b), U)
    g = sp.Poly(S3(x3, V, U, a, b), U)
    return sp.expand(sp.resultant(f, g))


def S5(x1, x2, x3, x4, V, a, b):
    """S_5(x1, x2, x3, x4, V) = Res_T(S_3(x1, x2, T), S_4(x3, x4, V, T))."""
    f = sp.Poly(S3(x1, x2, T, a, b), T)
    g = sp.Poly(sp.expand(S4(x3, x4, V, T, a, b)), T)
    return sp.expand(sp.resultant(f, g))


def main():
    rng = random.Random(4148)
    out = {"m3_control": [], "m4": [], "m4_per_variable_degree": []}

    # ---- m = 3 positive control: coefficient of x1^4 x2^4 x3^4 in S_4
    for trial in range(3):
        a, b, xR = (rng.randrange(1, 500) for _ in range(3))
        c = [rng.randrange(2, 30) for _ in range(3)]
        poly = sp.Poly(S4(c[0] * t, c[1] * t, c[2] * t, xR, a, b), t)
        d = poly.degree()
        lead = poly.LC()
        out["m3_control"].append(
            {"a": a, "b": b, "x_R": xR, "c": c, "deg_t": int(d),
             "lead": int(lead),
             "coeff_4_4_4": sp.Rational(int(lead),
                                        c[0] ** 4 * c[1] ** 4 * c[2] ** 4)
             if d == 12 else None})

    # ---- m = 4: coefficient of x1^8 x2^8 x3^8 x4^8 in S_5
    for trial in range(3):
        a, b, xR = (rng.randrange(1, 500) for _ in range(3))
        c = [rng.randrange(2, 12) for _ in range(4)]
        poly = sp.Poly(S5(c[0] * t, c[1] * t, c[2] * t, c[3] * t, xR, a, b), t)
        d = poly.degree()
        lead = poly.LC()
        denom = c[0] ** 8 * c[1] ** 8 * c[2] ** 8 * c[3] ** 8
        out["m4"].append(
            {"a": a, "b": b, "x_R": xR, "c": c, "deg_t": int(d),
             "lead_is_zero": lead == 0,
             "coeff_8_8_8_8": str(sp.Rational(int(lead), denom)) if d == 32 else None,
             "lead": str(lead)})

    # ---- m = 4 per-variable degree: specialise x2, x3, x4 to constants
    for trial in range(2):
        a, b, xR = (rng.randrange(1, 500) for _ in range(3))
        v = [rng.randrange(2, 30) for _ in range(3)]
        poly = sp.Poly(S5(t, v[0], v[1], v[2], xR, a, b), t)
        out["m4_per_variable_degree"].append(
            {"a": a, "b": b, "x_R": xR, "others": v, "deg_x1": int(poly.degree())})

    json.dump(out, sys.stdout, indent=1, default=str)


if __name__ == "__main__":
    main()
