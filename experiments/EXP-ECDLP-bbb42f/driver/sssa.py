"""
Smart / Satoh-Araki / Semaev (SSSA) polynomial-time discrete-log algorithm
for anomalous curves (N == p), via the p-adic formal-group logarithm at
precision p^2. This is the E1 special-curve solver used by
specification.yaml's CTRL-PLANTED-PATH.

Method (standard construction; see e.g. Smart, "The discrete logarithm
problem on elliptic curves of trace one", 1999): lift E, P, Q from F_p to
Z/p^2Z (same integer coefficients/coordinates, Hensel-lift the y-coordinate
to satisfy the curve equation mod p^2). Since N = p, [p]P and [p]Q reduce to
the identity mod p, i.e. they lie in the kernel of reduction (the formal
group); their formal parameter t = -X/Y (projective, see projective_ecc.py
-- affine coordinates cannot represent this point without a non-invertible
denominator, which is exactly why projective coordinates are used here) is
then O(p), so t^2 = O(p^2) = 0 mod p^2 and the formal-group logarithm is
just the identity at this precision: log(t) = t + O(t^2) = t (mod p^2).
Because log is linear to this precision, k = log([p]Q)/log([p]P) mod p.
"""
from __future__ import annotations
from .projective_ecc import proj_scalar_mult, from_affine


def hensel_lift_y(x: int, y: int, a: int, b: int, p: int) -> int:
    """Lift y (a square root of x^3+ax+b mod p) to y~ mod p^2 satisfying
    y~^2 = x^3+ax+b (mod p^2). Requires y != 0 mod p."""
    if y % p == 0:
        raise ValueError("cannot Hensel-lift a 2-torsion point (y=0)")
    rhs = (x**3 + a * x + b)
    diff = rhs - y * y
    assert diff % p == 0, "y is not a valid square root of x^3+ax+b mod p"
    t = ((diff // p) * pow(2 * y, -1, p)) % p
    y_lift = (y + p * t) % (p * p)
    return y_lift


def formal_log_of_pP(x: int, y: int, a: int, b: int, p: int):
    """Returns (t, s) where t = formal parameter of [p]P mod p^2 (an
    integer in [0, p^2) that must be divisible by p), and s = t // p mod p
    (the linearized log value used for the SSSA ratio)."""
    n = p * p
    y_lift = hensel_lift_y(x, y, a, b, p)
    Pp = from_affine((x % n, y_lift), n)
    Rp = proj_scalar_mult(p, Pp, a % n, n)
    X, Y, Z = Rp
    if Y % p == 0:
        raise RuntimeError("degenerate lift: Y([p]P) not a unit mod p; resample the point")
    t = (-X * pow(Y, -1, n)) % n
    if t % p != 0:
        raise RuntimeError(
            f"[p]P did not reduce to the identity mod p (t mod p = {t % p} != 0); "
            "this indicates N != p for this curve or an arithmetic error, not a valid SSSA instance"
        )
    s = (t // p) % p
    return t, s


def sssa_solve(x_P: int, y_P: int, x_Q: int, y_Q: int, a: int, b: int, p: int):
    """Solve Q = [k]P on an anomalous curve (N = p). Returns (k, diagnostics)."""
    t_P, s_P = formal_log_of_pP(x_P, y_P, a, b, p)
    t_Q, s_Q = formal_log_of_pP(x_Q, y_Q, a, b, p)
    if s_P == 0:
        raise RuntimeError("s_P == 0 mod p; degenerate instance, resample P")
    k = (s_Q * pow(s_P, -1, p)) % p
    return k, {"t_P": t_P, "s_P": s_P, "t_Q": t_Q, "s_Q": s_Q}
