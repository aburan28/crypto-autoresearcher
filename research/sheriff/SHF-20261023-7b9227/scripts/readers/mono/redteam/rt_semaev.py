"""Independent Semaev-polynomial toolkit for the red-team falsification runs.

Written for the sheriff case on GOAL-MONO-001 / KN-FIND-bdcd60.  Nothing here
uses the product formula under test: S_3 comes from the chord law, S_m from the
FORMAL Sylvester resultant recursion S_m = Res_X(S_3(x_1,x_2,X), S_{m-1}(x_3..,X)).
The fibre polynomial F(T) = S_m(x_1..x_{m-1}, T) is computed symbolically in T
(no interpolation), so a leading-coefficient drop at special values cannot
corrupt it.  Runs under `sage -python`.
"""
from sage.all import GF, PolynomialRing, matrix, EllipticCurve
import random


def S3_coeffs(x1, x2, a, b):
    """[c0, c1, c2]: S_3(x1, x2, X) as a polynomial in X (formal degree 2).
    From x3 = lambda^2 - x1 - x2 with lambda = (y2-y1)/(x2-x1):
    (x1-x2)^2 (x1+x2+x3) - f(x1) - f(x2) = -2 y1 y2; square, divide by (x1-x2)^2."""
    c2 = (x1 - x2) ** 2
    c1 = -2 * ((x1 + x2) * (x1 * x2 + a) + 2 * b)
    c0 = (x1 * x2 - a) ** 2 - 4 * b * (x1 + x2)
    return [c0, c1, c2]


def res22(A, B):
    """Formal resultant of two quadratics [c0,c1,c2] (Bezout form; valid when a2 or b2 = 0)."""
    a0, a1, a2 = A
    b0, b1, b2 = B
    return (a2 * b0 - a0 * b2) ** 2 - (a2 * b1 - a1 * b2) * (a1 * b0 - a0 * b1)


def res_formal(R, A, B, da, db):
    """Formal Sylvester resultant over the ring R: A of formal degree da, B of formal
    degree db, low->high coefficient lists.  Matrix size fixed by formal degrees."""
    A = [R(c) for c in A] + [R(0)] * (da + 1 - len(A))
    B = [R(c) for c in B] + [R(0)] * (db + 1 - len(B))
    n = da + db
    M = matrix(R, n, n)
    for i in range(db):
        for j in range(da + 1):
            M[i, i + j] = A[da - j]
    for i in range(da):
        for j in range(db + 1):
            M[db + i, i + j] = B[db - j]
    return M.det()


def coeffs(P, deg):
    """Low->high coefficient list of a univariate polynomial P, padded to length deg+1."""
    c = P.list()
    base = P.parent().base_ring()
    return (c + [base(0)] * (deg + 1 - len(c)))[: deg + 1]


def fibre_poly(m, xs, a, b, Fk):
    """F(T) = S_m(x_1..x_{m-1}, T) in Fk[T] by the formal resultant recursion.
    Supported m: 3..6."""
    assert len(xs) == m - 1 and 3 <= m <= 6
    RT = PolynomialRing(Fk, 'T')
    T = RT.gen()
    a, b = Fk(a), Fk(b)
    xs = [Fk(x) for x in xs]
    if m == 3:
        c = S3_coeffs(xs[0], xs[1], a, b)
        return c[0] + c[1] * T + c[2] * T ** 2
    RX = PolynomialRing(RT, 'X')
    X = RX.gen()
    # inner = S_{m-1}(x_3, ..., x_{m-1}, T, X) as an element of Fk[T][X]
    rest = xs[2:]
    if m == 4:
        # S_3(x_3, T, X)
        c = S3_coeffs(RX(rest[0]), RX(T), RX(a), RX(b))
        inner = c[0] + c[1] * X + c[2] * X ** 2
    elif m == 5:
        # S_4(x_3, x_4, T, X) = Res_Y( S_3(x_3, x_4, Y), S_3(T, X, Y) )
        RY = PolynomialRing(RX, 'Y')
        A = [RY(c) for c in S3_coeffs(rest[0], rest[1], a, b)]
        B = S3_coeffs(RY(RX(T)), RY(X), RY(a), RY(b))  # coefficients in Y
        inner = RX(res22(A, B))
    else:  # m == 6
        # S_5(x_3, x_4, x_5, T, X) = Res_Y( S_3(x_3, x_4, Y), S_4(x_5, T, X, Y) )
        # S_4(x_5, T, X, Y) = Res_Z( S_3(x_5, T, Z), S_3(X, Y, Z) )
        RY = PolynomialRing(RX, 'Y')
        RZ = PolynomialRing(RY, 'Z')
        Y = RY.gen()
        Az = S3_coeffs(RZ(RY(RX(rest[2]))), RZ(RY(RX(T))), RZ(a), RZ(b))
        Bz = S3_coeffs(RZ(RY(X)), RZ(Y), RZ(a), RZ(b))
        S4_in_Y = RY(res22(Az, Bz))  # polynomial in Y over Fk[T][X], formal degree 4
        Ay = [RY(c) for c in S3_coeffs(rest[0], rest[1], a, b)]
        inner = RX(res_formal(RY, Ay, coeffs(S4_in_Y, 4), 2, 4))
    A_outer = [RX(c) for c in S3_coeffs(xs[0], xs[1], a, b)]
    F = res_formal(RX, A_outer, coeffs(inner, 2 ** (m - 3)), 2, 2 ** (m - 3))
    # F is a constant polynomial in X with coefficient in Fk[T]
    return RT(F.constant_coefficient()) if F.degree() <= 0 else None


def cycle_type(FT):
    """Factor pattern over the base field as a sorted tuple of degrees; None if not
    squarefree or zero."""
    if FT.is_zero():
        return None
    degs = []
    for g, e in FT.factor():
        if e != 1:
            return None
        degs.append(g.degree())
    return tuple(sorted(degs))


def chi(v):
    return 1 if v.is_square() else -1


def random_point(E, rng):
    while True:
        x = E.base_field().random_element()
        pts = E.lift_x(x, all=True)
        if pts:
            return rng.choice(pts)


def defining_property_selftest(p, a, b, ms=(3, 4, 5, 6), trials=40, seed=1):
    """S_m(x(P_1),...,x(P_m)) = 0 whenever P_1 + ... + P_m = O, P_i from the group law;
    and S_m(x(P_1..P_{m-1}), t) != 0 for a random t that is not of the form
    x(sum eps_i P_i) (checked via the group law only as a filter)."""
    rng = random.Random(seed)
    Fp = GF(p)
    E = EllipticCurve(Fp, [a, b])
    out = {}
    for m in ms:
        zero_ok = zero_tot = nz_ok = nz_tot = 0
        for _ in range(trials):
            P = [random_point(E, rng) for _ in range(m - 1)]
            Pm = -sum(P[1:], P[0])
            if Pm.is_zero():
                continue
            xs = [Q[0] for Q in P]
            FT = fibre_poly(m, xs, a, b, Fp)
            zero_tot += 1
            if FT(Pm[0]) == 0:
                zero_ok += 1
            # a random t avoiding the sign-sum x-coordinates
            import itertools
            avoid = set()
            for eps in itertools.product([1, -1], repeat=m - 2):
                S = P[0]
                for e, Q in zip(eps, P[1:]):
                    S = S + (Q if e == 1 else -Q)
                if not S.is_zero():
                    avoid.add(S[0])
            t = Fp.random_element()
            while t in avoid:
                t = Fp.random_element()
            nz_tot += 1
            if FT(t) != 0:
                nz_ok += 1
        out[m] = {'sum_zero_gives_root': f'{zero_ok}/{zero_tot}', 'nonroot_t_nonzero': f'{nz_ok}/{nz_tot}'}
    return out


def selftest_resultants(p=101, seed=3):
    rng = random.Random(seed)
    Fp = GF(p)
    bad = 0
    for _ in range(200):
        A = [Fp(rng.randrange(p)) for _ in range(3)]
        B = [Fp(rng.randrange(p)) for _ in range(3)]
        if res22(A, B) != res_formal(Fp, A, B, 2, 2):
            bad += 1
    return bad


if __name__ == '__main__':
    import json, sys, time
    t0 = time.time()
    rep = {'res22_vs_sylvester_mismatches': selftest_resultants()}
    for (p, a, b) in [(1009, 2, 3), (10007, 0, 1), (1013, 5, 0), (13, 1, 1)]:
        rep[f'defining_property_p{p}_a{a}_b{b}'] = defining_property_selftest(p, a, b, trials=25, seed=p)
    rep['seconds'] = round(time.time() - t0, 1)
    print(json.dumps(rep, indent=1))
    if len(sys.argv) > 1:
        json.dump(rep, open(sys.argv[1], 'w'), indent=1)
