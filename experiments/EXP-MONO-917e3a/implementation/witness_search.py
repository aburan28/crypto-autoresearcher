"""
EXP-MONO-917e3a Stage 1: explicit freeness witnesses for the translation
action of V = F_2^{m-1}/<diag> on the 2^{m-2} sign-class roots of the m-th
Semaev summation polynomial, at m=4 and m=5.

A witness is one curve E/F_p and one tuple of m-1 non-2-torsion points such
that all 2^{m-2} signed-sum x-coordinates (sign classes with eps_1=+1 fixed)
are pairwise distinct. Existence of one witness rigorously proves the
underlying polynomial identity ("no nonempty signed subset sum of generic
points lies in E[2]") is not identically zero, which is the exact generic
non-vanishing statement H-MONO-93bc4d's mechanism requires -- this is a
standard, non-heuristic proof technique, not a statistical sample.
"""
import itertools


def point_add(p, A, B, P, Q):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if P == Q:
        if y1 % p == 0:
            return None
        lam = (3 * x1 * x1 + A) * pow(2 * y1, -1, p) % p
    else:
        if (x2 - x1) % p == 0:
            return None
        lam = (y2 - y1) * pow((x2 - x1) % p, -1, p) % p
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return (x3, y3)


def neg(p, P):
    if P is None:
        return None
    x, y = P
    return (x, (-y) % p)


def find_points(p, A, B, n, xstart=2):
    pts = []
    x = xstart
    while len(pts) < n:
        rhs = (x**3 + A * x + B) % p
        found = None
        for y in range(1, p):  # skip y=0 (2-torsion)
            if (y * y) % p == rhs:
                found = (x, y)
                break
        if found:
            pts.append(found)
        x += 1
        if x > p * 3:
            return None
    return pts


def witness_check(p, A, B, m, xstart=2):
    npts = m - 1
    pts = find_points(p, A, B, npts, xstart)
    if pts is None:
        return None, None, False
    roots = {}
    for signs in itertools.product([1, -1], repeat=npts - 1):
        eps = (1,) + signs
        acc = None
        for e, pt in zip(eps, pts):
            term = pt if e == 1 else neg(p, pt)
            acc = point_add(p, A, B, acc, term)
        x_coord = acc[0] if acc is not None else "INF"
        roots[eps] = x_coord
    xs = list(roots.values())
    distinct = len(set(xs)) == len(xs)
    return pts, roots, distinct


if __name__ == "__main__":
    results = []

    for p, A, B, xstart in [(101, 2, 3, 2), (211, 5, 7, 2)]:
        pts, roots, distinct = witness_check(p, A, B, 4, xstart)
        print(f"m=4 p={p} A={A} B={B}: points={pts} distinct={distinct}")
        results.append(dict(m=4, p=p, A=A, B=B, points=pts,
                             roots={str(k): v for k, v in roots.items()},
                             all_distinct=distinct))

    # m=5: first attempt (disclosed collision, not a counterexample)
    pts, roots, distinct = witness_check(101, 2, 3, 5, xstart=2)
    print(f"m=5 p=101 A=2 B=3 xstart=2 (first attempt): distinct={distinct}")
    results.append(dict(m=5, p=101, A=2, B=3, xstart=2, points=pts,
                         roots={str(k): v for k, v in roots.items()},
                         all_distinct=distinct, note="disclosed collision, not a counterexample"))

    # m=5: clean witness
    pts, roots, distinct = witness_check(101, 2, 3, 5, xstart=17)
    print(f"m=5 p=101 A=2 B=3 xstart=17 (clean witness): distinct={distinct}")
    results.append(dict(m=5, p=101, A=2, B=3, xstart=17, points=pts,
                         roots={str(k): v for k, v in roots.items()},
                         all_distinct=distinct))

    for r in results:
        if r["m"] == 4:
            assert r["all_distinct"], "m=4 witness must be clean"
    assert any(r["m"] == 5 and r["all_distinct"] for r in results), "at least one clean m=5 witness required"
    print("\nAll required witnesses confirmed.")
