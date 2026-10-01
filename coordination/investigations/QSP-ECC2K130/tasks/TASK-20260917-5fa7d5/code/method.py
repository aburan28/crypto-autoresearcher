"""The structural method for counting roots of L = X^(2^n') - lambda(X) in F_(2^n).

DERIVATION (all over GF(2), so - is +):

Let K = F_(2^n), sigma: x -> x^2 the Frobenius.  For x in K,
   x^(2^n') = lambda(x)                                     (*)
Apply sigma^n' to (*).  lambda has GF(2) coefficients, so
   lambda(y)^(2^m) = lambda(y^(2^m)),
hence x^(2^(2n')) = lambda(x)^(2^n') = lambda(x^(2^n')) = lambda(lambda(x)).
By induction, any x in K satisfying (*) satisfies
   x^(2^(k n')) = lambda^(k)(x)     for all k >= 1,
where lambda^(k) is the k-fold composite.  For x in K, x^(2^n) = x, so
x^(2^m) = x^(2^(m mod n)).  Choose k with k n' = e (mod n), e small.  Then every
root of (*) in K is a root of the ORDINARY polynomial

   P(X) = lambda^(k)(X) + X^(2^e),      deg P = d^k    (d = deg lambda, d^k > 2^e)

Hence  S := {x in K : (*)}  is contained in RootsInK(P).  Now
   g := gcd(P(X), X^(2^n) + X)
is squarefree and its roots are exactly RootsInK(P), and
   G := gcd(X^(2^n') + lambda(X), g)
    = gcd((X^(2^n') mod g) + lambda(X), g)
is squarefree with root set exactly S.  Therefore N(lambda) = deg G, and G
itself is the (squarefree) polynomial whose roots are precisely S.

For n = 131, n' = 33:  33*4 = 132 = 1 (mod 131), so k = 4, e = 1,
   P(X) = lambda(lambda(lambda(lambda(X)))) + X^2,   deg P = d^4 <= 2401.
"""
from gf2poly import (deg, clmul, sqr, polymod, polygcd, compose, frob_pow_mod,
                     is_irreducible, poly_str)

def choose_k(n, nprime, max_e=1):
    """smallest k>=1 with (k*nprime mod n) <= max_e"""
    for k in range(1, 4 * n + 2):
        if (k * nprime) % n <= max_e:
            return k, (k * nprime) % n
    raise ValueError('no k')

def superset_poly(lam, k, e):
    """lambda^(k)(X) + X^(2^e)"""
    c = lam
    for _ in range(k - 1):
        c = compose(lam, c)     # lambda(c(X))
    return c ^ (1 << (1 << e))

def count_roots(lam, n, nprime, f=None, k=None, e=None, want_G=False):
    """Number of distinct roots in F_(2^n) of X^(2^nprime) + lam(X).
    f (the field polynomial) is NOT needed -- the count is intrinsic."""
    if k is None:
        k, e = choose_k(n, nprime)
    P = superset_poly(lam, k, e)
    assert P != 0
    g = polygcd(P, frob_pow_mod(n, P) ^ 2)        # gcd(P, X^(2^n)+X)
    if deg(g) <= 0:
        return (0, g if want_G else None) if want_G else 0
    B = frob_pow_mod(nprime, g)                   # X^(2^nprime) mod g
    G = polygcd(g, B ^ polymod(lam, g))
    N = deg(G)
    if N < 0:
        N = 0
    return (N, G) if want_G else N

def brute_count(lam, n, f):
    """Brute force over every element of F_(2^n) = F_2[z]/(f). Returns sorted root list."""
    roots = []
    for x in range(1 << n):
        y = x
        for _ in range(nprime_cache[0]):
            y = polymod(sqr(y), f)
        if y == polymod(compose_eval(lam, x, f), f):
            roots.append(x)
    return roots

def compose_eval(lam, x, f):
    """lam(x) in F_2[z]/(f), Horner."""
    r = 0
    for i in range(lam.bit_length() - 1, -1, -1):
        r = polymod(clmul(r, x), f)
        if (lam >> i) & 1:
            r ^= 1
    return r

nprime_cache = [0]

def brute_roots(lam, n, nprime, f):
    nprime_cache[0] = nprime
    return brute_count(lam, n, f)
