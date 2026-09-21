#!/usr/bin/env python3
"""
THE ADMISSIBILITY CONDITION on a Mestre 6-tuple, and generators for it.

Mestre's construction needs deg_x r = 4: y^2 = r(x,T) is a genus-1 quartic
only then.  For a general 6-tuple deg_x r = 5 and the object is a genus-2
QUINTIC, to which none of the rank-11 reasoning applies.  This is NOT
automatic, and it is not stated in H-ECQ-8b600d: measured over 10694 tuples in
RUN-ECQTUP-416e78-002, only 127 (1.2%) satisfy it.

Measured form of the condition (RUN-ECQTUP-416e78-003; the coefficient was
FITTED from two tuples and then verified exactly on further tuples, and the
final admissibility test used by the scan is the direct symbolic one --
`MestreFamily(...).deg_x_r == 4` -- never this formula alone):

    [x^5 T^2] r  =  (24/5) P5 - 2 P2 P3

with P_k the k-th power sum of the roots of q CENTRED at their mean.  Every
other coefficient of x^5 in r vanishes identically, so

    ADMISSIBLE  <=>  12 P5(centred roots)  =  5 P2 P3(centred roots).

Written over the integers with c_i = 6 a_i - sum(a): 12 * sum c_i^5 =
5 * (sum c_i^2)(sum c_i^3), with sum c_i = 0.

Because the condition is stated in POWER SUMS OF THE ROOTS, it is computable
from q's coefficients alone and does NOT need the roots to be rational.  That
is what makes the null ladder possible: a q with k rational roots and
(6-k)/2 irreducible quadratic factors can be made admissible too, giving a
family of the SAME shape, the SAME surface degree and comparable coefficient
content but only 2k rational sections.
"""
from fractions import Fraction as F
from math import isqrt


def power_sums_from_rootdata(roots, quads, kmax=5):
    """P_1..P_kmax of the full root multiset.

    roots: rational roots.  quads: (s, n) meaning x^2 - s x + n.
    """
    P = [F(0)] * (kmax + 1)
    for a in roots:
        a = F(a)
        v = F(1)
        for k in range(1, kmax + 1):
            v *= a
            P[k] += v
    for s, n in quads:
        s, n = F(s), F(n)
        # p_k of the two roots of x^2 - s x + n, by Newton: p_k = s p_{k-1} - n p_{k-2}
        pk2, pk1 = F(2), s          # p_0 = 2, p_1 = s
        for k in range(1, kmax + 1):
            if k == 1:
                P[1] += s
                continue
            pk = s * pk1 - n * pk2
            P[k] += pk
            pk2, pk1 = pk1, pk
    return P


def centred_power_sums(roots, quads):
    """P_2, P_3, P_5 of the roots translated so that their sum is 0."""
    P = power_sums_from_rootdata(roots, quads, 5)
    m = P[1] / 6
    # translate: use binomial expansion of sum (a_i - m)^k
    from math import comb
    C = [F(0)] * 6
    P0 = [F(6)] + [P[k] for k in range(1, 6)]
    for k in range(6):
        C[k] = sum(F(comb(k, j)) * P0[k - j] * (-m) ** j for j in range(k + 1))
    return C[2], C[3], C[5]


def phi(roots, quads):
    """0 exactly when deg_x r = 4 (the admissibility condition)."""
    p2, p3, p5 = centred_power_sums(roots, quads)
    return 12 * p5 - 5 * p2 * p3


def content_p2(roots, quads):
    """The coefficient-content statistic the null ladder is MATCHED on:
    P_2 of the centred roots.  Scale-covariant of weight 2, translation
    invariant -- the natural size of a tuple."""
    p2, _, _ = centred_power_sums(roots, quads)
    return p2


def phi_int(a):
    """Integer form for six integers: 12 sum c^5 - 5 (sum c^2)(sum c^3),
    c_i = 6 a_i - sum a.  Zero exactly when phi is."""
    s = sum(a)
    c = [6 * x - s for x in a]
    s2 = sum(x * x for x in c)
    s3 = sum(x ** 3 for x in c)
    s5 = sum(x ** 5 for x in c)
    return 12 * s5 - 5 * s2 * s3


def is_square(n):
    if n < 0:
        return False
    r = isqrt(n)
    return r * r == n


def solve_quadratic_int(A, B, C):
    """Integer roots of A n^2 + B n + C = 0 (A may be 0)."""
    out = []
    if A == 0:
        if B != 0 and C % B == 0:
            out.append(-C // B)
        return out
    D = B * B - 4 * A * C
    if not is_square(D):
        return out
    r = isqrt(D)
    for num in (-B + r, -B - r):
        if num % (2 * A) == 0:
            out.append(num // (2 * A))
    return sorted(set(out))


def solve_last_n(roots, quads_fixed, s_last):
    """Integer n making (roots, quads_fixed + [(s_last, n)]) admissible.

    phi is a polynomial of degree <= 2 in n, so it is recovered exactly from
    three evaluations and solved in integers.
    """
    def ev(n):
        return phi(roots, list(quads_fixed) + [(s_last, n)])
    f0, f1, f2 = ev(0), ev(1), ev(2)
    A = (f2 - 2 * f1 + f0) / 2
    B = f1 - f0 - A
    C = f0
    if A.denominator != 1 or B.denominator != 1 or C.denominator != 1:
        den = 1
        for z in (A, B, C):
            den = den * z.denominator // _g(den, z.denominator)
        A, B, C = A * den, B * den, C * den
    return solve_quadratic_int(int(A), int(B), int(C))


def _g(a, b):
    while b:
        a, b = b, a % b
    return a


def quad_is_irreducible(s, n):
    """x^2 - s x + n irreducible over Q."""
    return not is_square(s * s - 4 * n)


def power_sums_from_poly(q_asc, kmax=5):
    """Power sums of the roots of a monic degree-n polynomial given ascending
    coefficients, by Newton's identities.  Needs no rationality of the roots."""
    n = len(q_asc) - 1
    e = [F(0)] * (n + 1)
    e[0] = F(1)
    for k in range(1, n + 1):
        e[k] = F(-1) ** k * F(q_asc[n - k])
    p = [F(n)] + [F(0)] * kmax   # p_0 = n
    for k in range(1, kmax + 1):
        s = F(0)
        for i in range(1, min(k - 1, n) + 1):
            s += F(-1) ** (i - 1) * e[i] * p[k - i]
        if k <= n:
            s += F(-1) ** (k - 1) * F(k) * e[k]
        p[k] = s
    return p


def centred_content_from_poly(q_asc):
    """(P2, P3, P5) of the roots translated to sum 0, and phi, from q alone."""
    from math import comb
    p = power_sums_from_poly(q_asc, 5)
    n = len(q_asc) - 1
    m = p[1] / n
    P0 = [F(n)] + [p[k] for k in range(1, 6)]
    C = [sum(F(comb(k, j)) * P0[k - j] * (-m) ** j for j in range(k + 1))
         for k in range(6)]
    return C[2], C[3], C[5], 12 * C[5] - 5 * C[2] * C[3]
