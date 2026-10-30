#!/usr/bin/env python3
"""J2 independent, deterministic F2 algebra; no producer imports or dependencies."""
import hashlib
import json
import platform
from pathlib import Path

HERE = Path(__file__).resolve().parent
INPUT = HERE.parents[1] / 'blind-statements.json'
spec = json.loads(INPUT.read_text())

def degree(a):
    return a.bit_length() - 1

def pmul(a, b):
    z = 0
    while b:
        if b & 1:
            z ^= a
        a <<= 1
        b >>= 1
    return z

def pmod(a, b):
    assert b
    while degree(a) >= degree(b):
        a ^= b << (degree(a) - degree(b))
    return a

def pgcd(a, b):
    while b:
        a, b = b, pmod(a, b)
    return a

def ppow(a, n, modulus):
    out = 1
    while n:
        if n & 1:
            out = pmod(pmul(out, a), modulus)
        a = pmod(pmul(a, a), modulus)
        n >>= 1
    return out

def prime_divisors(n):
    out = []
    d = 2
    while d * d <= n:
        if n % d == 0:
            out.append(d)
            while n % d == 0:
                n //= d
        d += 1
    if n > 1:
        out.append(n)
    return out

def irreducibility(a):
    n = degree(a)
    x = pmod(2, a)
    residues = {str(i): ppow(2, 1 << i, a) for i in range(n + 1)}
    gcds = {str(q): pgcd(a, residues[str(n // q)] ^ x) for q in prime_divisors(n)}
    # Independent exhaustive trial division by every monic polynomial up to n/2.
    divisors = []
    tested = 0
    for d in range(1, n // 2 + 1):
        for low in range(1 << d):
            candidate = (1 << d) | low
            tested += 1
            if pmod(a, candidate) == 0:
                divisors.append(candidate)
    rabin = residues[str(n)] == x and all(g == 1 for g in gcds.values())
    exhaustive = not divisors
    assert rabin == exhaustive
    return {'degree': n, 'bitmask': a, 'frobenius_residues': residues,
            'rabin_gcd_by_prime_divisor': gcds, 'rabin_irreducible': rabin,
            'trial_divisor_count': tested, 'proper_monic_divisors': divisors,
            'exhaustive_irreducible': exhaustive}

def madd(a, b):
    return [x ^ y for x, y in zip(a, b)]

def identity(n):
    return [1 << i for i in range(n)]

def apply_matrix(cols, x):
    out = 0
    i = 0
    while x:
        if x & 1:
            out ^= cols[i]
        x >>= 1
        i += 1
    return out

def compose(a, b):
    return [apply_matrix(a, col) for col in b]

def mpow(a, n):
    out = identity(len(a))
    while n:
        if n & 1:
            out = compose(out, a)
        a = compose(a, a)
        n >>= 1
    return out

def peval_matrix(poly, matrix):
    n = len(matrix)
    out = [0] * n
    term = identity(n)
    while poly:
        if poly & 1:
            out = madd(out, term)
        term = compose(matrix, term)
        poly >>= 1
    return out

def rank(vectors):
    basis = {}
    for v in vectors:
        while v:
            d = degree(v)
            if d in basis:
                v ^= basis[d]
            else:
                basis[d] = v
                break
    return len(basis)

def matrix_minpoly(matrix):
    n = len(matrix)
    basis = {}
    power = identity(n)
    for i in range(n + 1):
        v = sum(col << (n * j) for j, col in enumerate(power))
        relation = 1 << i
        while v:
            d = degree(v)
            if d not in basis:
                basis[d] = (v, relation)
                break
            v ^= basis[d][0]
            relation ^= basis[d][1]
        if not v:
            assert peval_matrix(relation, matrix) == [0] * n
            return {'bitmask': relation, 'degree': i,
                    'independent_prior_powers': len(basis)}
        power = compose(matrix, power)
    raise AssertionError('Cayley-Hamilton degree bound not met')

def kernel_basis(cols):
    n = len(cols)
    rows = [sum(((cols[j] >> i) & 1) << j for j in range(n)) for i in range(n)]
    pivots = []
    for j in range(n):
        pivot = next((i for i in range(len(pivots), n) if rows[i] & (1 << j)), None)
        if pivot is None:
            continue
        k = len(pivots)
        rows[k], rows[pivot] = rows[pivot], rows[k]
        for i in range(n):
            if i != k and rows[i] & (1 << j):
                rows[i] ^= rows[k]
        pivots.append(j)
    out = []
    for j in range(n):
        if j not in pivots:
            v = 1 << j
            for i, p in enumerate(pivots):
                if rows[i] & (1 << j):
                    v |= 1 << p
            assert apply_matrix(cols, v) == 0
            out.append(v)
    assert rank(out) == n - len(pivots)
    return out

def frobenius(modulus):
    return [pmod(1 << (2 * j), modulus) for j in range(degree(modulus))]

def orbit(matrix, element, length):
    out = []
    for _ in range(length):
        out.append(element)
        element = apply_matrix(matrix, element)
    return out

polys = {name: sum(1 << e for e in exps) for name, exps in spec['polynomials'].items()}
product = pmul(pmul(polys['factor1'], polys['factor8a']), polys['factor8b'])
pair_product = pmul(polys['factor8a'], polys['factor8b'])
assert pair_product == (1 << 17) - 1
assert product == (1 << 17) | 1
modulus = spec['archived_polynomial_basis_modulus_bitmask']
matrix = frobenius(modulus)
assert mpow(matrix, 17) == identity(17)
assert matrix != identity(17)
minpoly = matrix_minpoly(matrix)
assert minpoly['bitmask'] == product
subspaces = {}
combined = []
for name, poly in polys.items():
    evaluated = peval_matrix(poly, matrix)
    basis = kernel_basis(evaluated)
    invariant = all(apply_matrix(evaluated, apply_matrix(matrix, v)) == 0 for v in basis)
    subspaces[name] = {'dimension': len(basis), 'basis_bitmasks': basis,
                       'frobenius_invariant': invariant, 'evaluation_rank': rank(evaluated)}
    combined.extend(basis)
assert rank(combined) == 17

reducible = (1 << 8) | 1
bad_matrix = frobenius(reducible)
gf2_matrix = frobenius(2)  # F2[X]/(X), a concrete GF(2).
result = {
    'purpose': 'Independent deterministic algebra calculation from blind statements only',
    'python': platform.python_version(),
    'input_sha256': hashlib.sha256(INPUT.read_bytes()).hexdigest(),
    'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    'polynomials_bitmask': polys,
    'product_bitmask': product,
    'degree8_pair_product_bitmask': pair_product,
    'product_exponents': [i for i in range(18) if product & (1 << i)],
    'degree8_factor_tests': {k: irreducibility(v) for k, v in polys.items() if degree(v) == 8},
    'archived_modulus_test': irreducibility(modulus),
    'archived_frobenius': {
        'basis': ['x^' + str(i) for i in range(17)],
        'columns_bitmask': matrix,
        'rows_bitmask': [sum(((matrix[j] >> i) & 1) << j for j in range(17)) for i in range(17)],
        'rank': rank(matrix),
        'power17_is_identity': mpow(matrix, 17) == identity(17),
        'power1_is_identity': matrix == identity(17),
        'exact_order': next(k for k in range(1, 18) if mpow(matrix, k) == identity(17)),
        'minimal_polynomial': minpoly,
        'orbits': {str(v): {'values': orbit(matrix, v, 17),
                           'span_rank': rank(orbit(matrix, v, 17)),
                           'trace': apply_matrix(peval_matrix((1 << 17) - 1, matrix), v)}
                   for v in [1, 2, 3]},
        'factor_kernel_subspaces': subspaces,
        'combined_kernel_basis_rank': rank(combined)
    },
    'negative_controls': {
        'X8_plus_1': {
            'irreducibility': irreducibility(reducible),
            'equals_X_plus_1_power8': ppow(3, 8, 1 << 9) == reducible,
            'frobenius_rank': rank(bad_matrix),
            'frobenius_minimal_polynomial': matrix_minpoly(bad_matrix),
            'frobenius_power17_is_identity': mpow(bad_matrix, 17) == identity(8)
        },
        'GF2': {
            'dimension': 1,
            'frobenius_columns_bitmask': gf2_matrix,
            'frobenius_power17_is_identity': mpow(gf2_matrix, 17) == identity(1),
            'frobenius_exact_order': 1,
            'frobenius_minimal_polynomial': matrix_minpoly(gf2_matrix),
            'degree17_claim_holds': matrix_minpoly(gf2_matrix)['bitmask'] == product
        }
    }
}
assert result['archived_modulus_test']['rabin_irreducible']
assert all(t['rabin_irreducible'] for t in result['degree8_factor_tests'].values())
assert not result['negative_controls']['X8_plus_1']['irreducibility']['rabin_irreducible']
assert result['negative_controls']['X8_plus_1']['equals_X_plus_1_power8']
assert not result['negative_controls']['GF2']['degree17_claim_holds']
print(json.dumps(result, indent=2, sort_keys=True))
