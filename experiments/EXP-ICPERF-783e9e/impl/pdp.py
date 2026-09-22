"""Build and solve real Weil-descended point-decomposition problems over F_2.

E: y^2 + x y = x^3 + a2 x^2 + a6 over K = F_{2^n}, ordinary.
V: an F_2-subspace of K of dimension l.  Factor base F_V = {P : x(P) in V}.
PDP: given R, find x_1..x_m in V with S_{m+1}(x_1,...,x_m, x(R)) = 0.

Descent: x_i = sum_j v_ij b_j with v_ij in F_2 and b_j a basis of V.  Because
every Frobenius power z -> z^(2^k) is F_2-LINEAR, a monomial x^e contributes
Boolean degree equal to the Hamming weight of e, not e -- which is why S_3
descends to a purely QUADRATIC Boolean system and higher S_{m+1} do not.

Solved in Sage's BooleanPolynomialRing (PolyBoRi), so field equations v^2 = v
are implicit and the Groebner basis is over the Boolean quotient ring.
"""
import time
from sage.all import (GF, EllipticCurve, PolynomialRing, BooleanPolynomialRing,
                      Matrix, set_random_seed, vector, Ideal)


def curve(n, seed=1):
    set_random_seed(seed)
    K = GF(2 ** n, 'a')
    while True:
        a2, a6 = K.random_element(), K.random_element()
        if a6 == 0:
            continue
        E = EllipticCurve(K, [1, a2, 0, 0, a6])
        if E.trace_of_frobenius() % 2 != 0:      # ordinary
            return K, E, a6


def semaev(m, K, a6):
    """S_{m+1} as a polynomial in m+1 variables over K, by resultants from S_3."""
    names = [f"X{i}" for i in range(m + 1)]
    if m == 2:
        R = PolynomialRing(K, names)
        X = R.gens()
        return R, X[0]**2*X[1]**2 + X[0]**2*X[2]**2 + X[1]**2*X[2]**2 + X[0]*X[1]*X[2] + a6
    # S_{m+1}(X0..Xm) = Res_T( S_m(X0..X_{m-2}, T), S_3(X_{m-1}, Xm, T) )
    Rprev, Sprev = semaev(m - 1, K, a6)
    R = PolynomialRing(K, names + ["T"])
    X = R.gens()
    T = X[-1]
    sub_prev = Sprev(*(list(X[0:m - 1]) + [T]))
    s3 = X[m - 1]**2*X[m]**2 + X[m - 1]**2*T**2 + X[m]**2*T**2 + X[m - 1]*X[m]*T + a6
    res = sub_prev.resultant(s3, T)
    Rout = PolynomialRing(K, names)
    return Rout, Rout(res)


def subspace_basis(K, n, l, seed=1, stable=False):
    """An F_2-basis of an l-dimensional subspace of K."""
    set_random_seed(seed)
    if stable:                                   # Frobenius-closure of one element
        while True:
            v = K.random_element()
            gens, w = [], v
            for _ in range(n):
                gens.append(w); w = w ** 2
            M = Matrix(GF(2), [x._vector_() for x in gens]).echelon_form()
            rows = [r for r in M.rows() if any(r)]
            if len(rows) == l:
                return [K(list(r)) for r in rows]
    Vs = K.vector_space(GF(2), map=False) if False else None
    while True:
        b = [K.random_element() for _ in range(l)]
        M = Matrix(GF(2), [x._vector_() for x in b])
        if M.rank() == l:
            return b


def descend(S, basis, xR, m, n):
    """Substitute x_i = sum_j v_ij b_j and split into n Boolean equations.

    Kept MULTILINEAR throughout.  The naive route -- substitute into S_{m+1} and
    expand in a polynomial ring over K, then reduce v^k -> v -- passes through
    intermediate polynomials of total degree m * 2^(m-1) (32 at m = 4), which is
    where a straightforward implementation dies.  Instead:

      * every Frobenius power z -> z^(2^j) is F_2-LINEAR, so x_i^(2^j) is a
        linear form in the Boolean variables with coefficients in K, computed
        once per (i, j);
      * a K-monomial x_i^e is the product of those linear forms over the set
        bits of e, so its Boolean degree is the Hamming weight of e;
      * products are taken in the multilinear algebra directly (v * v = v), so
        nothing ever exceeds Boolean degree m(m-1).

    A term is a dict {frozenset(variable indices): coefficient in K}.
    """
    l = len(basis)
    K = basis[0].parent()
    names = [f"v{i}_{j}" for i in range(m) for j in range(l)]

    def mul(A, C):
        out = {}
        for sa, ca in A.items():
            for sc, cc in C.items():
                s = sa | sc                    # v * v = v
                v = ca * cc
                if v:
                    out[s] = out.get(s, K(0)) + v
        return {k: v for k, v in out.items() if v}

    exps_all = [mo.exponents()[0] for mo in S.monomials()]
    maxbit = max(1, max(max(e[i] for e in exps_all) for i in range(m)).bit_length())

    lin = [{frozenset([i * l + j]): basis[j] for j in range(l)} for i in range(m)]
    pw = []
    for i in range(m):
        row, cur = [], lin[i]
        for _ in range(maxbit):
            row.append(cur)
            cur = {s: c * c for s, c in cur.items()}    # squaring is F_2-linear
        pw.append(row)

    acc = {}
    for exps, coef in zip(exps_all, S.coefficients()):
        eR = exps[m] if len(exps) > m else 0
        term = {frozenset(): coef * (xR ** eR if eR else K(1))}
        for i in range(m):
            e, j = exps[i], 0
            while e and term:
                if e & 1:
                    term = mul(term, pw[i][j])
                e >>= 1
                j += 1
            if not term:
                break
        for s, c in term.items():
            acc[s] = acc.get(s, K(0)) + c

    B = BooleanPolynomialRing(m * l, names)
    BV = B.gens()
    eqs = [B(0)] * n
    for s, c in acc.items():
        if not c:
            continue
        bm = B(1)
        for idx in sorted(s):
            bm *= BV[idx]
        cv = c._vector_()
        for t in range(n):
            if cv[t]:
                eqs[t] += bm
    return B, [e for e in eqs if e != 0]
