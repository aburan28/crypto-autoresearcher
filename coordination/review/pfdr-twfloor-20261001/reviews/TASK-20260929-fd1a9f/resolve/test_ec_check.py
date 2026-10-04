"""Self-test of ec_check.py against brute force on small curves (own code only)."""
import random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ec_check as C

def brute_points(p, a, b):
    pts = [None]
    for x in range(p):
        r = (x * x * x + a * x + b) % p
        for y in range(p):
            if y * y % p == r:
                pts.append((x, y))
    return pts

rng = random.Random(12345)
n_ok = 0
for p in (97, 101, 103, 107, 109, 113, 127, 131, 1009, 1013):
    for trial in range(6):
        a, b = rng.randrange(p), rng.randrange(p)
        if (4 * a ** 3 + 27 * b * b) % p == 0:
            continue
        E = C.Curve(p, a, b)
        pts = brute_points(p, a, b)
        n = len(pts)
        assert all(E.on(P) for P in pts)
        # group law sanity: P + (-P) = O, associativity on a sample, n*P = O
        for P in pts[1:6]:
            assert E.add(P, E.neg(P)) is None
            assert E.mul(n, P) is None
            Q1, Q2 = pts[rng.randrange(1, n)], pts[rng.randrange(1, n)]
            assert E.add(E.add(P, Q1), Q2) == E.add(P, E.add(Q1, Q2))
        if C.is_prime_trial(n) and C.is_prime_mr(n) and n > 3:
            P = pts[1]
            for _ in range(5):
                k = rng.randrange(1, n)
                Q = E.mul(k, P)
                assert C.bsgs(E, P, Q, n) == k
                n_ok += 1
# primality cross-check on a range
for x in range(2, 20000):
    assert C.is_prime_trial(x) == C.is_prime_mr(x), x
# large known primes / composites
for x, v in ((2147483647, True), (4294967291, True), (4294967295, False), (3215031751, False), (3825123056546413051, False)):
    assert C.is_prime_mr(x) == v, x
    if x < 2**33:
        assert C.is_prime_trial(x) == v, x
print("ec_check self-test passed; bsgs logs checked:", n_ok)
