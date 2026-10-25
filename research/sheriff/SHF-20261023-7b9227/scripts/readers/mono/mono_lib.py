"""Independent re-derivation library for the Semaev summation cover (sheriff case 3,
reader validator-breakthrough).  Written from the definitions only; shares no code with
any producer artifact.  Run under /opt/conda-sage/envs/sage/bin/sage -python.

Conventions.  E: y^2 = f(x) = x^3 + a x + b over F_p.  S_3 is the classical summation
polynomial; S_m for m >= 4 is built by the resultant recursion
    S_m(X_1..X_m) = Res_X( S_3(X_1, X_2, X), S_{m-1}(X_3..X_m, X) ).
Both facts are re-verified numerically against the defining property in
check_definitions() before anything else uses them.
"""
from sage.all import (GF, PolynomialRing, EllipticCurve, ZZ, QQ, Integer, prod, randint,
                      set_random_seed, legendre_symbol, factor, gcd, PermutationGroup,
                      Permutation, SymmetricGroup, libgap, vector, matrix, binomial)
import itertools, collections, json, time


# --------------------------------------------------------------------------- S_3
def S3_expr(a, b, X1, X2, X3):
    """Semaev S_3 for y^2 = x^3 + a x + b, as an expression in any commutative ring."""
    return ((X1 - X2) ** 2 * X3 ** 2
            - 2 * ((X1 + X2) * (X1 * X2 + a) + 2 * b) * X3
            + ((X1 * X2 - a) ** 2 - 4 * b * (X1 + X2)))


def symbolic_S(m, a, b, base):
    """S_m(X_1..X_m) as a multivariate polynomial over `base` (a field or ZZ), built by the
    resultant recursion from S_3.  Variables X1..Xm."""
    R = PolynomialRing(base, ['X%d' % i for i in range(1, m + 1)] + ['Z'])
    X = R.gens()[:m]
    Z = R.gens()[m]
    if m == 2:
        return R, X[0] - X[1]
    if m == 3:
        return R, S3_expr(a, b, X[0], X[1], X[2])
    # S_m = Res_Z( S_3(X1, X2, Z), S_{m-1}(X3..Xm, Z) )
    Rprev, Sprev = symbolic_S(m - 1, a, b, base)
    # map Sprev's variables X1..X_{m-2} -> X3..Xm, X_{m-1} -> Z, and its dummy Z -> Z
    imgs = list(X[2:]) + [Z] + [Z]
    assert len(imgs) == Rprev.ngens()
    Sprev_shift = Sprev(*imgs)
    A = S3_expr(a, b, X[0], X[1], Z)
    res = A.resultant(Sprev_shift, Z)
    return R, res


# --------------------------------------------------------------------------- fibres
class Cover:
    """The cover T -> S_m(x_1..x_{m-1}, T) over a fixed curve y^2 = x^3 + a x + b / F_p."""

    def __init__(self, p, a, b, mmax=5):
        self.p = p
        self.F = GF(p)
        self.a = self.F(a)
        self.b = self.F(b)
        self.disc = 4 * self.a ** 3 + 27 * self.b ** 2
        self.singular = (self.disc == 0)
        self.E = None if self.singular else EllipticCurve(self.F, [self.a, self.b])
        self.PT = PolynomialRing(self.F, 'T')
        self.T = self.PT.gen()
        # polynomials with coefficients in F_p[T]
        self.PTX = PolynomialRing(self.PT, 'X')
        self.X = self.PTX.gen()
        self._S4 = None
        if mmax >= 5:
            # symbolic S_4 over F_p, used to build S_5(a1..a4, T) by one resultant
            R4, S4 = symbolic_S(4, self.a, self.b, self.F)
            self._S4 = (R4, S4)

    def f(self, x):
        return x ** 3 + self.a * x + self.b

    def chi(self, x):
        v = self.f(x)
        if v == 0:
            return 0
        return 1 if v.is_square() else -1

    def fibre_poly(self, m, xs):
        """F(T) = S_m(xs[0], .., xs[m-2], T) in F_p[T] (xs are F_p elements, len m-1)."""
        assert len(xs) == m - 1
        T = self.T
        if m == 3:
            return S3_expr(self.a, self.b, self.F(xs[0]), self.F(xs[1]), T)
        if m == 4:
            X = self.X
            A = S3_expr(self.a, self.b, self.F(xs[0]), self.F(xs[1]), X)       # in F_p[T][X]
            B = S3_expr(self.a, self.b, self.F(xs[2]), T, X)                   # in F_p[T][X]
            return self.PTX(A).resultant(self.PTX(B))
        if m == 5:
            R4, S4 = self._S4
            X = self.X
            A = self.PTX(S3_expr(self.a, self.b, self.F(xs[0]), self.F(xs[1]), X))
            # S_4(x3, x4, T, X): substitute into the symbolic S_4
            B4 = S4(self.F(xs[2]), self.F(xs[3]), T, X, 0)   # last arg is dummy Z
            return A.resultant(self.PTX(B4))
        raise ValueError("m not supported")

    def cycle_type(self, Fpoly):
        """Degree pattern of the factorisation over F_p (sorted tuple)."""
        return tuple(sorted([int(g.degree()) for g, e in Fpoly.factor() for _ in range(e)]))

    def classify(self, m, xs):
        """Returns (status, chi-tuple, cycle type, predicted cycle type).
        status: 'f_zero' | 'degree_drop' | 'not_squarefree' | 'ok'."""
        chis = tuple(self.chi(self.F(x)) for x in xs)
        if 0 in chis:
            return ('f_zero', chis, None, None)
        if len(set(xs)) < len(xs):
            # x_i = x_j: P_i = +-P_j, so two sign classes give the same point sum and the true
            # fibre is non-squarefree or of lower degree; also the specialised resultant is
            # not the specialised S_m when x_1 = x_2.  Excluded by the statement's hypothesis.
            return ('repeated_x', chis, None, None)
        Fp = self.fibre_poly(m, xs)
        d = 2 ** (m - 2)
        if Fp.degree() != d:
            return ('degree_drop', chis, None, None)
        if gcd(Fp, Fp.derivative()).degree() != 0:
            return ('not_squarefree', chis, None, None)
        ct = self.cycle_type(Fp)
        pred = tuple([1] * d) if len(set(chis)) == 1 else tuple([2] * (d // 2))
        return ('ok', chis, ct, pred)


# --------------------------------------------------------------------------- root formula
def point_sum_x(E2, pts, signs):
    Q = E2(0)
    for P, s in zip(pts, signs):
        Q = Q + (P if s == 1 else -P)
    if Q.is_zero():
        return None
    return Q[0]


def labelled_root_check(cov, m, xs, rng_seed=None):
    """Over F_{p^2}: compute r_[eps] = x(P_1 + sum eps_i P_i) for all sign classes, check
    they are exactly the roots of F(T), and that Frobenius (p-th power) maps r_[eps] to
    r_[chi * eps].  Returns dict with booleans.  Requires f(x_i) != 0 for all i."""
    p = cov.p
    F2 = GF(p ** 2, 'w')
    E2 = EllipticCurve(F2, [F2(cov.a), F2(cov.b)])
    xs = [F2(cov.F(x)) for x in xs]
    if len(set(xs)) < len(xs):
        return {'skipped': 'repeated_x'}
    pts = []
    chis = []
    for x in xs:
        fx = x ** 3 + F2(cov.a) * x + F2(cov.b)
        if fx == 0:
            return {'skipped': 'f_zero'}
        y = fx.sqrt()
        pts.append(E2(x, y))
        chis.append(1 if fx ** ((p - 1) // 2) == 1 else -1)
    n = m - 1
    classes = {}
    for eps in itertools.product([1, -1], repeat=n):
        if eps[0] != 1:
            continue  # representative with eps_1 = +1
        r = point_sum_x(E2, pts, eps)
        classes[eps] = r
    if any(r is None for r in classes.values()):
        return {'skipped': 'root_at_infinity'}
    roots = list(classes.values())
    Fpoly = cov.fibre_poly(m, [cov.F(x) for x in xs])
    PT2 = PolynomialRing(F2, 'T')
    Fp2 = PT2(Fpoly)
    distinct = (len(set(roots)) == len(roots))
    vanish = all(Fp2(r) == 0 for r in roots)
    full_degree = (Fpoly.degree() == 2 ** (m - 2))
    # product formula up to scalar
    prodpoly = prod(PT2.gen() - r for r in roots)
    lc = Fp2.leading_coefficient() if full_degree else None
    product_ok = full_degree and (Fp2 == lc * prodpoly)
    # Frobenius rule, labelled: phi(r_eps) = r_{chi*eps} (normalise class rep eps_1 = +1)
    frob_ok = True
    for eps, r in classes.items():
        img = tuple(c * e for c, e in zip(chis, eps))
        if img[0] == -1:
            img = tuple(-e for e in img)
        if r ** p != classes[img]:
            frob_ok = False
    return {'distinct': distinct, 'vanish': vanish, 'full_degree': full_degree,
            'product_ok': product_ok, 'frob_labelled_ok': frob_ok,
            'chis': chis}


# --------------------------------------------------------------------------- group model
def symmetric_base_group(m):
    """The claimed symmetric-base group as a permutation group on V = {+-1}^{m-1}/{+-1},
    realised on points 1..2^{m-2}, together with the extra points 2^{m-2}+1..2^{m-2}+m-1
    carrying the S_{m-1} quotient action (so joint cycle types can be read off).
    Generators: translations by e_i (i = 2..m-1) and the coordinate permutations (1 2),
    (1 2 .. m-1).  Returns (G_joint, nV)."""
    n = m - 1
    reps = [eps for eps in itertools.product([1, -1], repeat=n) if eps[0] == 1]
    idx = {eps: i + 1 for i, eps in enumerate(reps)}

    def norm(eps):
        return eps if eps[0] == 1 else tuple(-e for e in eps)
    nV = len(reps)
    gens = []
    for j in range(1, n):  # translation by e_j, j = 2..n (0-based j = 1..n-1)
        perm = [0] * (nV + n)
        for eps in reps:
            img = list(eps)
            img[j] = -img[j]
            perm[idx[eps] - 1] = idx[norm(tuple(img))]
        for k in range(n):
            perm[nV + k] = nV + k + 1
        gens.append(perm)
    # coordinate permutations
    for sigma in ([1, 0] + list(range(2, n)), list(range(1, n)) + [0]):
        if n == 2 and sigma == [1, 0]:
            pass
        perm = [0] * (nV + n)
        for eps in reps:
            img = tuple(eps[sigma[i]] for i in range(n))  # (sigma eps)_i = eps_{sigma(i)}
            perm[idx[eps] - 1] = idx[norm(img)]
        for k in range(n):
            # point nV+1+k (coordinate k) -> coordinate sigma^{-1}(k) ... any faithful choice
            perm[nV + k] = nV + 1 + sigma.index(k)
        gens.append(perm)
    perms = [Permutation(g) for g in gens]
    G = PermutationGroup(perms)
    # perms[:n-1] are the translations, perms[n-1:] the coordinate permutations
    return G, nV, perms


def joint_cycle_distribution(G, nV):
    """Counts of (cycle type on V, cycle type on the coordinate points) over G."""
    cnt = collections.Counter()
    npts = G.degree()
    for g in G:
        tup = g.tuple()
        # cycle type on points 1..nV and on nV+1..npts
        def ct(points):
            seen = set(); out = []
            for s in points:
                if s in seen:
                    continue
                l = 0; x = s
                while x not in seen:
                    seen.add(x); x = tup[x - 1]; l += 1
                out.append(l)
            return tuple(sorted(out))
        cnt[(ct(range(1, nV + 1)), ct(range(nV + 1, npts + 1)))] += 1
    return cnt


def v_only_distribution(G, nV):
    cnt = collections.Counter()
    for (cv, cs), k in joint_cycle_distribution(G, nV).items():
        cnt[cv] += k
    return cnt


def agl32():
    """AGL(3,2) as a permutation group on the 8 vectors of F_2^3 (built by hand: translations
    plus the generators of GL(3,2)), since this libgap has no AGL function."""
    from sage.all import GL, GF, vector, PermutationGroup
    pts = [vector(GF(2), [i & 1, (i >> 1) & 1, (i >> 2) & 1]) for i in range(8)]
    idx = {tuple(v): i + 1 for i, v in enumerate(pts)}
    gens = []
    t = vector(GF(2), [1, 0, 0])
    gens.append([idx[tuple(v + t)] for v in pts])
    for M in GL(3, GF(2)).gens():
        gens.append([idx[tuple(M * v)] for v in pts])
    G = PermutationGroup(gens)
    assert G.order() == 1344
    return G
