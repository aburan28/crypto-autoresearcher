"""
Smart-Araki-Satoh-Semaev anomalous-curve DLP algorithm (Smart 1999, "The
discrete logarithm problem on elliptic curves of trace one"). Given
E/F_p: y^2 = x^3+ax+b with N = #E(F_p) == p (anomalous), and P, Q in
E(F_p)\{O} with Q = kP, this recovers k in POLYNOMIAL time via the additive
p-adic elliptic logarithm on the formal group of E over Z/p^2Z.

METHOD (standard, textbook -- e.g. Blake-Seroussi-Smart chapter on
anomalous curves; Silverman "Advanced Topics", exercises on formal groups):
  1. Hensel-lift each affine point (x, y) in F_p to (x, y~) mod p^2, with
     y~ == y (mod p) and y~^2 == x^3+ax+b (mod p^2) -- solved by one
     Newton step since 2y is invertible mod p (y != 0 for a nonzero point
     on a curve with N odd... here N == p, and p is odd for every curve in
     this experiment's scope, so no 2-torsion complication arises: y == 0
     would force order 2 | N, impossible since N=p is odd prime > 2, hence
     y != 0 for every nonzero point).
  2. Compute [p]P~ using the SAME curve equation, arithmetic mod p^2
     throughout (double-and-add), NOT reducing to a formal "infinity"
     symbol at any point -- since P has order exactly p in E(F_p), [p]P~
     mod p^2 is a well-defined AFFINE point (X, Y) with X == 0 (mod p)
     (a standard fact about the kernel of reduction on the formal group).
  3. elog(P) := (X // p) * modinv(Y, p) mod p  -- the additive logarithm
     on the formal group (isomorphic to (Z/pZ, +)), a standard closed
     formula for this algorithm.
  4. k = elog(Q) * modinv(elog(P), p) mod p.

Every step here is elementary modular arithmetic (Python's native
arbitrary-precision integers); no external p-adic library is used or
needed at these bit sizes.
"""
from __future__ import annotations


class SmartASSError(Exception):
    pass


def _hensel_lift_y(x, y, a, b, p, p2):
    """Given (x, y) satisfying y^2 = x^3+ax+b (mod p), lift y to y~ mod p^2
    with y~^2 == x^3+ax+b (mod p^2), using one Newton step."""
    f = (x * x * x + a * x + b) % p2
    if y == 0:
        raise SmartASSError("Hensel lift requires y != 0 (2-torsion point)")
    inv_2y = pow((2 * y) % p, -1, p)
    diff = (f - y * y) % p2
    diff_over_p = (diff // p) % p  # diff is guaranteed divisible by p since y^2==f mod p
    if (f - y * y) % p != 0:
        raise SmartASSError("input point does not satisfy curve equation mod p")
    t = (diff_over_p * inv_2y) % p
    y_lifted = (y + p * t) % p2
    if (y_lifted * y_lifted - f) % p2 != 0:
        raise SmartASSError("Hensel lift failed self-check")
    return y_lifted


def _add_mod(P, Qp, a, modulus):
    """Affine EC addition mod `modulus` (not necessarily prime; inversions
    via pow(x,-1,modulus) will raise ValueError if x is not invertible,
    surfaced to the caller as a defect rather than silently producing a
    wrong point)."""
    if P is None:
        return Qp
    if Qp is None:
        return P
    x1, y1 = P
    x2, y2 = Qp
    if x1 == x2 and (y1 + y2) % modulus == 0:
        return None
    if x1 == x2 and y1 == y2:
        lam = ((3 * x1 * x1 + a) * pow((2 * y1) % modulus, -1, modulus)) % modulus
    else:
        lam = ((y2 - y1) * pow((x2 - x1) % modulus, -1, modulus)) % modulus
    x3 = (lam * lam - x1 - x2) % modulus
    y3 = (lam * (x1 - x3) - y1) % modulus
    return (x3, y3)


def _scalar_mul_mod(k, P, a, modulus):
    if k == 0 or P is None:
        return None
    R = None
    Qp = P
    while k:
        if k & 1:
            R = _add_mod(R, Qp, a, modulus)
        Qp = _add_mod(Qp, Qp, a, modulus)
        k >>= 1
    return R


def elliptic_log(P, a, b, p):
    """elog(P) for P on the anomalous curve E/F_p (N = p). Returns an
    integer mod p."""
    p2 = p * p
    x, y = P
    y_lift = _hensel_lift_y(x, y, a, b, p, p2)
    P_lift = (x % p2, y_lift)
    a2 = a % p2
    b2 = b % p2
    pP = _scalar_mul_mod(p, P_lift, a2, p2)
    if pP is None:
        raise SmartASSError("[p]P~ reduced to O mod p^2 exactly (unlucky lift); retry with a different lift")
    X, Y = pP
    if X % p != 0:
        raise SmartASSError(f"[p]P~ x-coordinate not == 0 mod p as expected: X mod p = {X % p}")
    x_over_p = (X // p) % p
    y_mod_p = Y % p
    if y_mod_p == 0:
        raise SmartASSError("[p]P~ y-coordinate == 0 mod p (degenerate)")
    inv_y = pow(y_mod_p, -1, p)
    return (x_over_p * inv_y) % p


def solve_anomalous_dlp(P, Q, a, b, p):
    """Q = kP on anomalous E/F_p (N == p). Returns k mod p."""
    elog_p = elliptic_log(P, a, b, p)
    elog_q = elliptic_log(Q, a, b, p)
    if elog_p == 0:
        raise SmartASSError("elog(P) == 0 (P generates a subgroup this method cannot invert)")
    inv = pow(elog_p, -1, p)
    return (elog_q * inv) % p
