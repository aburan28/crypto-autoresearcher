"""F_p / EC / polynomial arithmetic and operation counting."""

import random

import fixtures
import polyfp
from fparith import INF, Curve, Fp, OpCounter
from verify import VCurve

P = 32801  # L = 8 fixture prime


def naive_mul(p, a, b):
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] = (out[i + j] + x * y) % p
    return polyfp.trim(out)


def test_inverse_and_counts():
    F = Fp(P)
    for x in (1, 2, 12345, P - 1):
        assert F.inv(x) * x % P == 1
    assert F.c.inv == 4 and F.c.gcd_steps > 4 and F.c.mul == 0


def test_pow_counts_and_values():
    F = Fp(P)
    assert F.pow(3, 0) == 1 and F.pow(3, 1) == 3
    F.c = OpCounter()
    e = 1000
    assert F.pow(7, e) == pow(7, e, P)
    # left-to-right: (bitlen - 1) squarings + (popcount - 1) multiplies
    assert F.c.mul == (e.bit_length() - 1) + (bin(e).count("1") - 1)


def test_sqrt_both_branches():
    for p in (P, 1048609, 33554593, 10007):  # 10007 = 3 mod 4
        F = Fp(p)
        for x in range(2, 60):
            if F.is_square(x):
                r = F.sqrt(x)
                assert r * r % p == x


def test_curve_group_law_matches_verifier():
    fx = fixtures.fixture(8, 1)
    F = Fp(fx["p"])
    E = Curve(F, fx["a"], fx["b"])
    V = VCurve(fx["p"], fx["a"], fx["b"])
    G = tuple(fx["G"])
    assert E.on_curve(G)
    assert E.mul(fx["N"], G) is INF and V.mul(fx["N"], G) is None
    rng = random.Random(1)
    for _ in range(200):
        k1, k2 = rng.randrange(fx["N"]), rng.randrange(fx["N"])
        P1, P2 = E.mul(k1, G), E.mul(k2, G)
        assert E.add(P1, P2) == V.mul((k1 + k2) % fx["N"], G)
        assert E.add(P1, P1) == V.add(V.mul(k1, G), V.mul(k1, G))
    assert E.add(G, E.neg(G)) is INF


def test_rem_prem_and_counts():
    rng = random.Random(2)
    F = Fp(P)
    for _ in range(50):
        da, db = rng.randrange(8, 40), rng.randrange(1, 9)
        a = [rng.randrange(P) for _ in range(da)] + [rng.randrange(1, P)]
        b = [rng.randrange(P) for _ in range(db)] + [rng.randrange(1, P)]
        before = F.c.mul
        r = polyfp.rem(F, a, b)
        # count bound: (da - db + 1) quotient mults + db per non-zero quotient coefficient
        assert F.c.mul - before <= (da - db + 1) * (db + 1)
        assert polyfp.deg(r) < db
        a_minus_r = polyfp.trim([(x - (r[i] if i < len(r) else 0)) % P for i, x in enumerate(a)])
        assert polyfp.rem(Fp(P), a_minus_r, b) == []
        pr = polyfp.prem(F, a, b)
        s = pow(b[-1], da - db + 1, P)
        assert pr == polyfp.trim([c * s % P for c in r])


def _gcd_deg(p, a, b):
    a, b = polyfp.trim(list(a)), polyfp.trim(list(b))
    while b:
        a, b = b, polyfp.rem(Fp(p), a, b)
    return polyfp.deg(a)


def test_subresultant_prs_gcd_degree():
    rng = random.Random(3)
    F = Fp(P)
    for trial in range(200):
        k = rng.randrange(0, 4)
        common = [rng.randrange(P) for _ in range(k)]
        ra = [rng.randrange(P) for _ in range(rng.randrange(5, 30))]
        rb = [rng.randrange(P) for _ in range(rng.randrange(1, 8))]
        A = polyfp.from_roots(F, common + ra)
        B = polyfp.from_roots(F, common + rb)
        res = polyfp.subresultant_prs(F, A, B)
        assert res["deg_gcd"] == _gcd_deg(P, A, B)
        # gcd vanishes at every common root
        for c in common:
            assert polyfp.evaluate(Fp(P), res["gcd"], c) == 0


def test_subresultant_prs_matches_sylvester_resultant_zero():
    """deg_gcd == 0 iff the resultant (Sylvester determinant mod p) is non-zero."""
    rng = random.Random(4)
    F = Fp(101)
    for _ in range(100):
        A = [rng.randrange(101) for _ in range(6)] + [1]
        B = [rng.randrange(101) for _ in range(3)] + [1]
        res = polyfp.subresultant_prs(F, A, B)
        assert (res["deg_gcd"] == 0) == (_sylvester_det(A, B, 101) != 0)


def _sylvester_det(A, B, p):
    m, n = len(A) - 1, len(B) - 1
    N = m + n
    M = []
    for i in range(n):
        M.append([0] * i + list(reversed(A)) + [0] * (N - m - 1 - i))
    for i in range(m):
        M.append([0] * i + list(reversed(B)) + [0] * (N - n - 1 - i))
    det = 1
    for c in range(N):
        piv = next((r for r in range(c, N) if M[r][c] % p), None)
        if piv is None:
            return 0
        if piv != c:
            M[c], M[piv] = M[piv], M[c]
            det = -det
        det = det * M[c][c] % p
        inv = pow(M[c][c], -1, p)
        for r in range(c + 1, N):
            f = M[r][c] * inv % p
            M[r] = [(x - f * y) % p for x, y in zip(M[r], M[c])]
    return det % p


def test_from_roots_count():
    F = Fp(P)
    roots = list(range(1, 21))
    poly = polyfp.from_roots(F, roots)
    assert F.c.mul == sum(range(1, 21))
    assert all(polyfp.evaluate(Fp(P), poly, r) == 0 for r in roots)
    assert naive_mul(P, [P - 1, 1], [P - 2, 1]) == polyfp.from_roots(Fp(P), [1, 2])
