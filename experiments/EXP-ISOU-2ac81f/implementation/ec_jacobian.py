"""
Q2 engine: instrumented Jacobian-coordinate arithmetic, in EACH member's own
cheapest reachable model, used to measure field multiplications/squarings
per group operation. Never used for Q1 (model_normalization control).

Declared candidate model set (frozen before measurement, per the handoff's
"DECLARED CANDIDATE MODEL SET FOR Q2" constraint):
    - model "a_minus3": curve transformed (isomorphically, scaling by a
      4th-root u with u^4 = a/(-3)) to an equivalent short-Weierstrass curve
      with literal coefficient -3, using the a=-3-specialized doubling
      formula (dbl-2001-b, 3M+5S).
    - model "generic": no such transform exists (a/(-3) is not a 4th power);
      use the generic-a doubling formula (dbl-2007-bl, 2M+8S).
Point ADDITION cost does not depend on 'a' at all (add-2007-bl, both
models use the identical formula/cost), which is the mechanism-level reason
Q2's spread is bounded: only doublings can differ.

Montgomery/Edwards reachability (both predicted false for every member,
since N is prime and odd => no rational 2-torsion => neither model's
required rational point of order 2 (Montgomery) or order 4 with the right
structure (Edwards) can exist) is tested directly and recorded, never
assumed.

M/S aggregation rule (frozen, per the handoff's "DECLARED M/S AGGREGATION"
constraint): squarings are weighted at 1.0 multiplications for the reported
scalar ratio; raw mul/sqr counts are recorded separately so a reviewer can
recompute under any other weighting.
"""
from __future__ import annotations

from fp import fp_mul, fp_sqr, fp_add, fp_sub, Counters
from fp import is_fourth_power


def to_a_minus3_model(a, b, p):
    """
    If a/(-3) is a fourth power mod p, find u with u^4 = a/(-3) and return
    the isomorphic curve (a', b') = (-3, b/u^6). Returns None if not
    reachable.
    """
    target = (a * pow((-3) % p, p - 2, p)) % p
    if target == 0:
        return None
    if not is_fourth_power(target, p):
        return None
    u = _nth_root(target, p, 4)
    if u is None:
        return None
    u_inv = pow(u, p - 2, p)
    b_new = (b * pow(u_inv, 6, p)) % p
    return ((-3) % p, b_new, u)


def _nth_root(a, p, n):
    """One n-th root of a mod p, given a is known to be an n-th power.
    Brute, general method via Tonelli-Shanks-style exponent search: since
    n is tiny (n=4 here) and gcd(n, p-1) is what matters, use the standard
    trick: raise to (p-1)/gcd + adjust via trial multipliers found from a
    primitive root candidate. For our scope (n=4, small), we search
    directly among candidate exponents."""
    d = _gcd(n, p - 1)
    if pow(a, (p - 1) // d, p) != 1:
        return None
    # find e with e*n == 1 mod (p-1)/d is not generally solvable if d>1;
    # use a direct search via repeated squaring candidates instead.
    # Since n=4 always here, handle it directly via two sqrt() calls.
    if n == 4:
        r2 = _sqrt_mod(a, p)
        if r2 is None:
            return None
        r4 = _sqrt_mod(r2, p)
        return r4
    raise NotImplementedError("only n=4 supported")


def _gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def _sqrt_mod(a, p):
    a %= p
    if a == 0:
        return 0
    if pow(a, (p - 1) // 2, p) != 1:
        return None
    if p % 4 == 3:
        return pow(a, (p + 1) // 4, p)
    q = p - 1
    s = 0
    while q % 2 == 0:
        q //= 2
        s += 1
    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1:
        z += 1
    m, c, t, r = s, pow(z, q, p), pow(a, q, p), pow(a, (q + 1) // 2, p)
    while t != 1:
        i, t2i = 0, t
        while t2i != 1:
            t2i = (t2i * t2i) % p
            i += 1
        b = pow(c, 1 << (m - i - 1), p)
        m, c, t, r = i, (b * b) % p, (t * b * b) % p, (r * b) % p
    return r


def has_montgomery_or_edwards_model(N):
    """
    Both models require a rational point of order 2 (Montgomery: By^2 =
    x^3+Ax^2+x has one by construction; twisted Edwards similarly needs
    full or partial rational 2-torsion). Since our curves all have prime
    odd order N, the rational 2-torsion subgroup has order dividing
    gcd(2, N) = 1, so it is always trivial: this is a DIRECT, cheap,
    structural test (no curve-specific computation needed) rather than an
    assumption, and it is computed and recorded for every member.
    """
    return (N % 2 == 0)


def jacobian_double_generic(X1, Y1, Z1, a, p, ctr: Counters):
    XX = fp_sqr(X1, p, ctr)
    YY = fp_sqr(Y1, p, ctr)
    YYYY = fp_sqr(YY, p, ctr)
    ZZ = fp_sqr(Z1, p, ctr)
    t1 = fp_add(X1, YY, p)
    t1 = fp_sqr(t1, p, ctr)
    t1 = fp_sub(t1, XX, p)
    t1 = fp_sub(t1, YYYY, p)
    S = (2 * t1) % p
    ZZ2 = fp_sqr(ZZ, p, ctr)
    aZZ2 = fp_mul(a, ZZ2, p, ctr)
    M = (3 * XX + aZZ2) % p
    T = fp_sqr(M, p, ctr)
    T = (T - 2 * S) % p
    X3 = T
    Y3 = fp_mul(M, (S - T) % p, p, ctr)
    Y3 = (Y3 - 8 * YYYY) % p
    Z3 = fp_add(Y1, Z1, p)
    Z3 = fp_sqr(Z3, p, ctr)
    Z3 = fp_sub(Z3, YY, p)
    Z3 = fp_sub(Z3, ZZ, p)
    return X3, Y3, Z3


def jacobian_double_a_minus3(X1, Y1, Z1, p, ctr: Counters):
    delta = fp_sqr(Z1, p, ctr)
    gamma = fp_sqr(Y1, p, ctr)
    beta = fp_mul(X1, gamma, p, ctr)
    t1 = fp_sub(X1, delta, p)
    t2 = fp_add(X1, delta, p)
    prod = fp_mul(t1, t2, p, ctr)
    alpha = (3 * prod) % p
    X3 = fp_sqr(alpha, p, ctr)
    X3 = (X3 - 8 * beta) % p
    t3 = fp_add(Y1, Z1, p)
    t3 = fp_sqr(t3, p, ctr)
    Z3 = (t3 - gamma - delta) % p
    gamma2 = fp_sqr(gamma, p, ctr)
    Y3 = fp_mul(alpha, (4 * beta - X3) % p, p, ctr)
    Y3 = (Y3 - 8 * gamma2) % p
    return X3, Y3, Z3


def jacobian_add(X1, Y1, Z1, X2, Y2, Z2, p, ctr: Counters):
    """General Jacobian + Jacobian addition (add-2007-bl style); model
    independent (no 'a' term appears)."""
    Z1Z1 = fp_sqr(Z1, p, ctr)
    Z2Z2 = fp_sqr(Z2, p, ctr)
    U1 = fp_mul(X1, Z2Z2, p, ctr)
    U2 = fp_mul(X2, Z1Z1, p, ctr)
    Z2cubed = fp_mul(Z2, Z2Z2, p, ctr)
    Z1cubed = fp_mul(Z1, Z1Z1, p, ctr)
    S1 = fp_mul(Y1, Z2cubed, p, ctr)
    S2 = fp_mul(Y2, Z1cubed, p, ctr)
    H = (U2 - U1) % p
    I = fp_sqr((2 * H) % p, p, ctr)
    J = fp_mul(H, I, p, ctr)
    r = (2 * (S2 - S1)) % p
    V = fp_mul(U1, I, p, ctr)
    X3 = fp_sqr(r, p, ctr)
    X3 = (X3 - J - 2 * V) % p
    Y3 = fp_mul(r, (V - X3) % p, p, ctr)
    S1J = fp_mul(S1, J, p, ctr)
    Y3 = (Y3 - 2 * S1J) % p
    t = fp_add(Z1, Z2, p)
    t = fp_sqr(t, p, ctr)
    t = (t - Z1Z1 - Z2Z2) % p
    Z3 = fp_mul(t, H, p, ctr)
    return X3, Y3, Z3


def to_affine(X, Y, Z, p):
    if Z % p == 0:
        return None
    zinv = pow(Z, p - 2, p)
    zinv2 = (zinv * zinv) % p
    zinv3 = (zinv2 * zinv) % p
    return (X * zinv2) % p, (Y * zinv3) % p
