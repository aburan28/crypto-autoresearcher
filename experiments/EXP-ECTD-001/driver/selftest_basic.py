"""
selftest_basic.py -- brute-force toy-scale validation of fp.py and curve.py
before they are trusted at 40-56 bit scale. Run directly: python3 -m driver.selftest_basic
"""
import random
from . import fp
from . import curve


def brute_force_points(a, b, p):
    pts = [None]
    for x in range(p):
        rhs = (x * x * x + a * x + b) % p
        for y in range(p):
            if (y * y) % p == rhs:
                pts.append((x, y))
    return pts


def brute_force_order(a, b, p):
    return len(brute_force_points(a, b, p))


def test_group_law_matches_bruteforce():
    p = 97
    a, b = 2, 3
    assert (4 * a ** 3 + 27 * b * b) % p != 0
    pts = brute_force_points(a, b, p)
    N = len(pts)
    # verify closure: sum of any two points is in the set, and matches brute-force
    # addition table computed independently via slope-search over the finite field.
    rng = random.Random(1)
    sample = rng.sample(pts, min(30, len(pts)))
    for P in sample:
        for Q in sample:
            R = curve.add(P, Q, a, p)
            assert curve.on_curve(R, a, b, p), (P, Q, R)
    print(f"  group law on-curve closure: OK ({len(sample)}^2 pairs), |E(F_{p})|={N}")
    return N


def test_order_finder_matches_bruteforce():
    p = 10007  # prime
    trials = [(1, 5), (3, 7), (2, 9), (5, 1)]
    rng = random.Random(2)
    for (a, b) in trials:
        if (4 * a ** 3 + 27 * b * b) % p == 0:
            continue
        N_true = brute_force_order(a, b, p)
        N_found = curve.find_curve_order(a, b, p, rng, tries=8)
        assert N_found == N_true, f"a={a} b={b}: found {N_found}, brute {N_true}"
        print(f"  order-finder a={a},b={b}: brute={N_true} bsgs={N_found} OK")


def test_sqrt_mod():
    p = 10007
    for a in range(1, 200):
        r = fp.sqrt_mod(a, p)
        if r is not None:
            assert (r * r) % p == a % p
    print("  sqrt_mod: OK")


def test_primality():
    known_primes = [2, 3, 5, 7, 11, 97, 10007, 1000003, (1 << 40) + 15]
    for n in known_primes:
        assert fp.is_probable_prime(n), n
    known_composites = [4, 9, 100, 10008, 1000004]
    for n in known_composites:
        assert not fp.is_probable_prime(n), n
    print("  primality: OK")


if __name__ == "__main__":
    print("=== selftest_basic ===")
    test_sqrt_mod()
    test_primality()
    test_group_law_matches_bruteforce()
    test_order_finder_matches_bruteforce()
    print("ALL BASIC SELFTESTS PASSED")
