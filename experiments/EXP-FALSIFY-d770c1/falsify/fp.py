"""Dense univariate polynomial arithmetic and factorisation over F_p.

Pure standard library on purpose. No computer-algebra system is installed in
this harness (no sympy, sage, pari, flint), which is precisely why every
`proof_status: derivation` finding in the corpus is unchecked machine-wise.
This module is the minimum needed to check those claims arithmetically.

Polynomials are coefficient lists, low degree first, normalised so the last
entry is nonzero.  The zero polynomial is [].
"""


def norm(a, p):
    a = [c % p for c in a]
    while a and a[-1] == 0:
        a.pop()
    return a


def deg(a):
    return len(a) - 1


def add(a, b, p):
    n = max(len(a), len(b))
    return norm([(a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0)
                 for i in range(n)], p)


def sub(a, b, p):
    n = max(len(a), len(b))
    return norm([(a[i] if i < len(a) else 0) - (b[i] if i < len(b) else 0)
                 for i in range(n)], p)


def mul(a, b, p):
    if not a or not b:
        return []
    r = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b):
                r[i + j] += x * y
    return norm(r, p)


def divmod_(a, b, p):
    a = a[:]
    db = deg(b)
    inv = pow(b[-1], p - 2, p)
    q = [0] * max(0, deg(a) - db + 1)
    while a and deg(a) >= db:
        d = deg(a) - db
        c = a[-1] * inv % p
        q[d] = c
        for i, y in enumerate(b):
            a[i + d] = (a[i + d] - c * y) % p
        a = norm(a, p)
    return norm(q, p), a


def gcd(a, b, p):
    a, b = norm(a[:], p), norm(b[:], p)
    while b:
        a, b = b, divmod_(a, b, p)[1]
    if a:
        inv = pow(a[-1], p - 2, p)
        a = norm([c * inv for c in a], p)
    return a


def powmod(base, e, f, p):
    r, b = [1], divmod_(base, f, p)[1]
    while e:
        if e & 1:
            r = divmod_(mul(r, b, p), f, p)[1]
        b = divmod_(mul(b, b, p), f, p)[1]
        e >>= 1
    return r


def deriv(a, p):
    return norm([i * a[i] for i in range(1, len(a))], p)


def monic(a, p):
    inv = pow(a[-1], p - 2, p)
    return norm([c * inv for c in a], p)


def is_squarefree(f, p):
    return deg(gcd(f, deriv(f, p), p)) == 0


def factor_pattern(f, p):
    """Sorted multiset of irreducible-factor degrees of a squarefree f.

    Distinct-degree factorisation.  This is all a Galois-shape test needs: the
    *degrees* of the irreducible factors, not the factors themselves.
    """
    f = monic(f, p)
    pat, d, h, fs = [], 1, [0, 1], f
    while deg(fs) >= 2 * d:
        h = powmod(h, p, fs, p)
        g = gcd(sub(h, [0, 1], p), fs, p)
        if deg(g) > 0:
            pat += [d] * (deg(g) // d)
            fs = divmod_(fs, g, p)[0]
            if deg(fs) > 0:
                h = divmod_(h, fs, p)[1]
        d += 1
    if deg(fs) > 0:
        pat.append(deg(fs))
    return sorted(pat)


def det(M, p):
    """Determinant over F_p by Gaussian elimination."""
    M = [row[:] for row in M]
    n, d = len(M), 1
    for c in range(n):
        piv = next((r for r in range(c, n) if M[r][c] % p), None)
        if piv is None:
            return 0
        if piv != c:
            M[c], M[piv] = M[piv], M[c]
            d = -d
        d = d * M[c][c] % p
        inv = pow(M[c][c], p - 2, p)
        for r in range(c + 1, n):
            if M[r][c]:
                fct = M[r][c] * inv % p
                for k in range(c, n):
                    M[r][k] = (M[r][k] - fct * M[c][k]) % p
    return d % p


def resultant(f, g, p):
    """Resultant of f and g via the Sylvester determinant.

    CAUTION, and this caution is the whole point of RUN-FALSIFY-d770c1-001:
    the Sylvester matrix size is fixed by the NOMINAL degrees of f and g.  If a
    caller specialises parameters so that a leading coefficient vanishes, the
    matrix silently shrinks and the value returned is no longer comparable with
    values at neighbouring specialisations.  Interpolating across a mixture of
    the two normalisations produces a polynomial that is not the object under
    study.  Callers must assert full degree; see semaev.py.
    """
    df, dg = deg(f), deg(g)
    n = df + dg
    M = [[0] * n for _ in range(n)]
    for i in range(dg):
        for j, c in enumerate(reversed(f)):
            M[i][i + j] = c
    for i in range(df):
        for j, c in enumerate(reversed(g)):
            M[dg + i][i + j] = c
    return det(M, p)


def interpolate(xs, ys, p):
    """Lagrange interpolation through the given points over F_p."""
    poly = []
    for i, xi in enumerate(xs):
        num, den = [1], 1
        for j, xj in enumerate(xs):
            if i != j:
                num = mul(num, [(-xj) % p, 1], p)
                den = den * (xi - xj) % p
        c = ys[i] * pow(den, p - 2, p) % p
        poly = add(poly, norm([c * t for t in num], p), p)
    return norm(poly, p)
