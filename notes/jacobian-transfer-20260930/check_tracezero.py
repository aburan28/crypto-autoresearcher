#!/usr/bin/env python3
"""Exact arithmetic checks for a scoped Koblitz Weil-restriction derivation.

This checks polynomial identities, not map construction or DLP performance.
Simplicity labels come from Diem--Naumann Theorem 4 / Corollary 21.
"""
import hashlib
import json
import platform
import sys


def trim(p):
    p = list(p)
    while len(p) > 1 and p[-1] == 0:
        p.pop()
    return p


def mul(p, q):
    r = [0] * (len(p) + len(q) - 1)
    for i, a in enumerate(p):
        for j, b in enumerate(q):
            r[i + j] += a * b
    return trim(r)


def exact_div(p, q):
    p, q = trim(p), trim(q)
    assert q[-1] == 1
    result = [0] * (len(p) - len(q) + 1)
    while len(p) >= len(q) and p != [0]:
        offset = len(p) - len(q)
        result[offset] = p[-1]
        for i, a in enumerate(q):
            p[i + offset] -= result[offset] * a
        p = trim(p)
    assert p == [0], p
    return trim(result)


def trace(mu, n):
    a, b = 2, mu
    if n == 0:
        return a
    for _ in range(1, n):
        a, b = b, mu * b - 2 * a
    return b


def weil_polynomial(mu, n):
    p = [0] * (2 * n + 1)
    p[0], p[n], p[2 * n] = 2 ** n, -trace(mu, n), 1
    return p


def divisors(n):
    return [d for d in range(1, n + 1) if n % d == 0]


def primitive_blocks(mu, n):
    blocks = {}
    for d in divisors(n):
        p = weil_polynomial(mu, d)
        for e in divisors(d)[:-1]:
            p = exact_div(p, blocks[e])
        blocks[d] = p
    product = [1]
    for p in blocks.values():
        product = mul(product, p)
    assert product == weil_polynomial(mu, n)
    return blocks


def qmul(mu, x, y):
    # Integers in Q(alpha), with alpha^2 = mu*alpha - 2.
    a, b = x
    c, d = y
    return (a * c - 2 * b * d, a * d + b * c + mu * b * d)


def qconj(mu, x):
    a, b = x
    return (a + mu * b, -b)


def qneg(x):
    return (-x[0], -x[1])


def quadratic_norm_poly(mu, f):
    c = [qconj(mu, a) for a in f]
    result = [(0, 0)] * (2 * len(f) - 1)
    for i, x in enumerate(f):
        for j, y in enumerate(c):
            a, b = qmul(mu, x, y)
            result[i + j] = (result[i + j][0] + a,
                             result[i + j][1] + b)
    assert all(b == 0 for a, b in result)
    return [a for a, b in result]


def degree_seven_factors(mu):
    # Quadratic-residue Gaussian period s=(-1+sqrt(-7))/2.
    alpha = (0, 1)
    a2 = qmul(mu, alpha, alpha)
    a3 = qmul(mu, a2, alpha)
    s = (-(mu + 1) // 2, 1)
    sbar = qconj(mu, s)
    f = [qneg(a3), qmul(mu, a2, sbar),
         qneg(qmul(mu, alpha, s)), (1, 0)]
    h = [qneg(a3), qmul(mu, a2, s),
         qneg(qmul(mu, alpha, sbar)), (1, 0)]
    return [quadratic_norm_poly(mu, f), quadratic_norm_poly(mu, h)]


def row(mu, n):
    blocks = primitive_blocks(mu, n)
    f = exact_div(weil_polynomial(mu, n), weil_polynomial(mu, 1))
    base_order, extension_order = 3 - mu, 2 ** n + 1 - trace(mu, n)
    assert sum(f) * base_order == extension_order
    tracezero_dimension = n - 1
    primitive_degrees = [len(p) - 1 for d, p in blocks.items() if d > 1]
    # Q(sqrt(-7)) is contained in Q(zeta_d) iff 7 divides d here.
    simple_dims = []
    for d, p in blocks.items():
        if d == 1:
            continue
        dim = (len(p) - 1) // 2
        simple_dims.extend([dim // 2, dim // 2] if d % 7 == 0 else [dim])
    assert sum(simple_dims) == tracezero_dimension
    # Direct polynomial coefficients in Q(alpha) for alpha^n.
    alpha_power = (1, 0)
    for _ in range(n):
        alpha_power = qmul(mu, alpha_power, (0, 1))
    assert alpha_power[1] != 0
    item = {
        'mu': mu, 'extension_degree': n,
        'base_curve_order': base_order, 'extension_curve_order': extension_order,
        'trace_n': trace(mu, n), 'tracezero_order': sum(f),
        'tracezero_dimension': tracezero_dimension,
        'tracezero_weil_polynomial_degree': len(f) - 1,
        'primitive_block_degrees': primitive_degrees,
        'simple_component_dimensions_from_published_theorem': simple_dims,
        'irreducibility_computed_by_factorization': False,
        'alpha_power_coefficients': alpha_power,
        'tracezero_weil_coefficients_ascending': f,
        'polynomial_sha256': hashlib.sha256(json.dumps(f).encode()).hexdigest(),
    }
    if n > 2:
        # If this entire trace-zero variety were a genus-(n-1) Jacobian.
        power_trace_one = -f[-2]
        power_trace_two = f[-2] ** 2 - 2 * f[-3]
        assert power_trace_one == -mu
        assert power_trace_two == -trace(mu, 2)
        count2, count4 = 3 - power_trace_one, 5 - power_trace_two
        item['hypothetical_exact_dimension_jacobian_counts'] = {
            'over_F2': count2, 'over_F4': count4,
            'degree_two_closed_points': (count4 - count2) // 2,
            'fails_point_inclusion': count4 < count2,
        }
    if n == 7:
        factors = degree_seven_factors(mu)
        assert mul(*factors) == f
        item['exceptional_control_factors_ascending'] = factors
    return item


def main():
    rows = [row(mu, n) for n in (7, 31, 51, 53, 83, 131) for mu in (-1, 1)]
    document = {
        'kind': 'exact_arithmetic_diagnostic',
        'scope': 'standard binary Koblitz families; no exact challenge UID asserted',
        'python': platform.python_version(),
        'independent_review': False, 'dlp_runs': 0, 'map_constructions': 0,
        'checks': ['exact quotient and primitive-block product identities',
                   'point-order identity at T=1',
                   'nonrational alpha-power coefficient',
                   'degree-7 control: explicit two-factor product'],
        'rows': rows,
    }
    json.dump(document, sys.stdout, indent=2)
    print()


if __name__ == '__main__':
    main()
