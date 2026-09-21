"""
selftest_divpoly.py -- brute-force toy-scale validation of division polynomials
(psi_3, psi_5, psi_7) against directly-enumerated torsion points.
Run: python3 -m driver.selftest_divpoly
"""
import random
from . import curve, divpoly, fp


def brute_points(a, b, p):
    pts = []
    for x in range(p):
        rhs = (x ** 3 + a * x + b) % p
        for y in range(p):
            if (y * y) % p == rhs:
                pts.append((x, y))
    return pts


def check_ell(ell, a, b, p, verbose=True):
    N = len(brute_points(a, b, p)) + 1  # +1 for O
    if N % ell != 0:
        return None  # no rational ell-torsion subgroup to test against here
    pts = brute_points(a, b, p)
    torsion_xs = set()
    for P in pts:
        if curve.scalar_mul(ell, P, a, p) is None:
            torsion_xs.add(P[0])
    if not torsion_xs:
        return None
    poly = divpoly.torsion_poly(ell, a, b, p)
    ok = True
    for x in torsion_xs:
        val = divpoly.peval(poly, x, p)
        if val != 0:
            ok = False
            if verbose:
                print(f"    MISMATCH ell={ell} x={x}: psi_ell(x)={val} (expected 0)")
    if verbose:
        print(f"    ell={ell}: {len(torsion_xs)} rational torsion x-coords, all roots of psi_ell: {ok}")
    return ok


def run():
    print("=== selftest_divpoly ===")
    p = 10007
    tested = {2: False, 3: False, 5: False, 7: False}
    for a in range(1, 60):
        for b in range(1, 60):
            if (4 * a ** 3 + 27 * b * b) % p == 0:
                continue
            for ell in (2, 3, 5, 7):
                if tested[ell]:
                    continue
                r = check_ell(ell, a, b, p, verbose=False)
                if r is not None:
                    assert r, f"division polynomial mismatch for ell={ell}, a={a}, b={b}"
                    tested[ell] = True
                    print(f"  ell={ell}: verified against brute-force torsion points (a={a},b={b})")
            if all(tested.values()):
                break
        if all(tested.values()):
            break
    assert all(tested.values()), f"could not find toy curves exercising all ell in this search range: {tested}"
    print("ALL DIVPOLY SELFTESTS PASSED")


if __name__ == "__main__":
    run()
