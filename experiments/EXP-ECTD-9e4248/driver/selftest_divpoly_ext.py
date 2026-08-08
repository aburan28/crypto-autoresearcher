"""
selftest_divpoly_ext.py -- validate divpoly_ext.py's general recursion against the
already-validated reused/divpoly.py psi_5/psi_7 values, plus standard degree checks,
before it is trusted by any real run.

Run: python3 -m driver.selftest_divpoly_ext   (from experiments/EXP-ECTD-9e4248/)
"""
import random

from .reused import divpoly as dp
from . import divpoly_ext as dpx


def test_agrees_with_reused_psi5_psi7():
    rng = random.Random(20260807)
    for trial in range(20):
        p = 10007 + trial * 2  # small-ish primes-ish, doesn't need to be prime for pure poly arithmetic,
        # but use an actual small prime for realism
        while True:
            from .reused import fp
            if fp.is_probable_prime(p):
                break
            p += 1
        a = rng.randrange(p)
        b = rng.randrange(p)
        if (4 * a ** 3 + 27 * b * b) % p == 0:
            continue
        ref = dp.division_polys(a, b, p)
        mine, _ = dpx.build_division_polys(a, b, p, 7)
        for n in (5, 7):
            assert mine[n].parity == ref[n].parity, f"parity mismatch n={n} p={p}"
            assert mine[n].coeffs == ref[n].coeffs, f"coeff mismatch n={n} p={p}\n{mine[n].coeffs}\n{ref[n].coeffs}"
    print("  psi_5/psi_7 agree with reused/divpoly.py on 20 random small curves: OK")


def test_degrees():
    from .reused import fp
    p = 100003
    rng = random.Random(7)
    a = rng.randrange(p)
    b = rng.randrange(p)
    psis, _ = dpx.build_division_polys(a, b, p, 31)
    for n in range(1, 32):
        P = psis[n]
        deg = len(P.coeffs) - 1
        while deg > 0 and P.coeffs[deg] == 0:
            deg -= 1
        if n % 2 == 1:
            expect = (n * n - 1) // 2
        else:
            expect = (n * n - 4) // 2
        assert deg == expect, f"n={n} deg={deg} expect={expect}"
    print("  degree formula holds for n=1..31: OK")


def test_torsion_poly_general_matches_torsion_poly_for_small_ell():
    from .reused import fp, divpoly as rdp
    p = 100003
    rng = random.Random(11)
    a = rng.randrange(p)
    b = rng.randrange(p)
    for ell in (3, 5, 7):
        ref = rdp.torsion_poly(ell, a, b, p)
        mine = dpx.torsion_poly_general(ell, a, b, p)
        assert ref == mine, f"ell={ell} mismatch"
    print("  torsion_poly_general matches reused torsion_poly for ell=3,5,7: OK")


if __name__ == "__main__":
    print("test_agrees_with_reused_psi5_psi7:")
    test_agrees_with_reused_psi5_psi7()
    print("test_degrees:")
    test_degrees()
    print("test_torsion_poly_general_matches_torsion_poly_for_small_ell:")
    test_torsion_poly_general_matches_torsion_poly_for_small_ell()
    print("ALL selftest_divpoly_ext PASSED")
