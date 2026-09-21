"""
selftest_isogeny.py -- brute-force toy-scale end-to-end validation of the isogeny
kernel-finding + Velu codomain construction: for a small prime p, search curves,
run neighbors(), and independently confirm (by BRUTE-FORCE point counting, not by
the driver's own order-finder) that every returned neighbor really has the same
#E(F_p) as the source curve.
Run: python3 -m driver.selftest_isogeny
"""
import random
from . import curve, isogeny, fp


def brute_order(a, b, p):
    """O(p) exact point count via the Legendre-symbol identity
    #E(F_p) = p + 1 + sum_x legendre(x^3+ax+b, p) -- independent of, and much faster
    than, the O(p^2) (x,y) double loop, still a full brute-force (no group-theoretic
    shortcuts, no BSGS) cross-check of the driver's own order/isogeny machinery."""
    s = 0
    for x in range(p):
        s += fp.legendre((x ** 3 + a * x + b) % p, p)
    return p + 1 + s


def run():
    print("=== selftest_isogeny ===")
    p = 2003
    rng = random.Random(11)
    found_any = {2: 0, 3: 0, 5: 0, 7: 0}
    checked_curves = 0
    for a in range(1, 40):
        for b in range(1, 40):
            if (4 * a ** 3 + 27 * b * b) % p == 0:
                continue
            N = brute_order(a, b, p)
            checked_curves += 1
            nbrs = isogeny.neighbors(a, b, p, N, rng, ells=(2, 3, 5, 7))
            for ell, a2, b2 in nbrs:
                N2 = brute_order(a2, b2, p)
                assert N2 == N, (
                    f"TRACE NOT PRESERVED: source a={a},b={b},N={N} "
                    f"-> ell={ell} codomain a={a2},b={b2},N2={N2}"
                )
                found_any[ell] += 1
            if checked_curves >= 25 and all(v > 0 for v in found_any.values()):
                break
        if checked_curves >= 25 and all(v > 0 for v in found_any.values()):
            break
    print(f"  checked {checked_curves} source curves; neighbor counts by ell: {found_any}")
    assert all(v > 0 for v in found_any.values()), (
        f"did not exercise every ell in {{2,3,5,7}} within the search budget: {found_any}"
    )
    print("  every returned neighbor's order independently brute-force verified to match source")
    print("ALL ISOGENY SELFTESTS PASSED")


if __name__ == "__main__":
    run()
