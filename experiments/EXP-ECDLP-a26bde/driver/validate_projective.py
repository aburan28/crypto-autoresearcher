"""Validate the division-free projective formulas in padic.py against
harness/toycurve.py's exact-field EllipticCurve.add/.mul over real F_p, for
several actual primes and hundreds of random point pairs, BEFORE the
formulas are used for any Z/p^K Z computation (per the task's Stage-1
prerequisite). Prints a pass/fail summary; nonzero exit on any mismatch.
"""
import random
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
from harness.toycurve import EllipticCurve  # noqa: E402

sys.path.insert(0, os.path.dirname(__file__))
from padic import padd, pdbl, pmul, O_PROJ, is_identity  # noqa: E402


def to_proj(pt):
    if pt is None:
        return O_PROJ
    x, y = pt
    return (x, y, 1)


def proj_eq(E, P, Q):
    """Compare two projective points for equality as points on E/F_p (both
    reduced mod p, the field prime — this validator runs with N=p, not a
    prime power, so ordinary field inversion always works away from O)."""
    p = E.p
    if is_identity(P) and is_identity(Q):
        return True
    if is_identity(P) or is_identity(Q):
        return False
    X1, Y1, Z1 = P
    X2, Y2, Z2 = Q
    # cross-multiply rather than invert, so O-adjacent comparisons stay exact
    return (X1 * Z2 - X2 * Z1) % p == 0 and (Y1 * Z2 - Y2 * Z1) % p == 0


def main():
    random.seed(90210)
    primes_and_curves = []
    for p, a, b in [(1009, 2, 3), (10007, -5, 7), (100003, 1, 1),
                    (7919, 3, 11), (65537, -1, 4)]:
        E = EllipticCurve(p, a, b)
        primes_and_curves.append(E)

    total, mismatches = 0, []
    for E in primes_and_curves:
        p, a = E.p, E.a
        pts = []
        while len(pts) < 60:
            x = random.randrange(p)
            R = E.lift_x(x)
            if R is not None:
                pts.append(R)

        # doubling check
        for R in pts:
            got = pdbl(to_proj(R), a, p)
            want = to_proj(E.add(R, R))
            total += 1
            if not proj_eq(E, got, want):
                mismatches.append(("dbl", p, R, got, want))

        # addition check, random pairs (200 per curve)
        for _ in range(200):
            R1 = random.choice(pts)
            R2 = random.choice(pts)
            got = padd(to_proj(R1), to_proj(R2), a, p)
            want = to_proj(E.add(R1, R2))
            total += 1
            if not proj_eq(E, got, want):
                mismatches.append(("add", p, R1, R2, got, want))

        # scalar multiplication check (double-and-add ladder end to end)
        for _ in range(60):
            R = random.choice(pts)
            k = random.randrange(1, 5000)
            got = pmul(k, to_proj(R), a, p)
            want = to_proj(E.mul(k, R))
            total += 1
            if not proj_eq(E, got, want):
                mismatches.append(("mul", p, k, R, got, want))

        # negation-sum case explicitly: R + (-R) must be O
        for R in pts[:10]:
            negR = E.negate(R)
            got = padd(to_proj(R), to_proj(negR), a, p)
            total += 1
            if not is_identity(got):
                mismatches.append(("negsum", p, R, got))

        # identity-involving cases
        for R in pts[:5]:
            got1 = padd(O_PROJ, to_proj(R), a, p)
            got2 = padd(to_proj(R), O_PROJ, a, p)
            total += 2
            if not proj_eq(E, got1, to_proj(R)):
                mismatches.append(("O+R", p, R, got1))
            if not proj_eq(E, got2, to_proj(R)):
                mismatches.append(("R+O", p, R, got2))

    print(f"total comparisons: {total}")
    print(f"mismatches: {len(mismatches)}")
    if mismatches:
        for m in mismatches[:20]:
            print("MISMATCH:", m)
        sys.exit(1)
    print("PASS: division-free projective formulas agree with "
          "harness/toycurve.py on every comparison.")


if __name__ == "__main__":
    main()
