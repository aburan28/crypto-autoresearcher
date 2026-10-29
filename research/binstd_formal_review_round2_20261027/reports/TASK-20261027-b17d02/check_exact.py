#!/usr/bin/env python3
"""Blind deterministic exact arithmetic. No repository inputs or dependencies."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STATEMENT = Path('/var/tmp/binstd-round2-blind-20261027/statement.json')
EXPECTED_HASH = '2bbf336b088ff099546bcc3b5f3612f439ba2b7aa69a5007c6d02fcdb590f664'


def polynomial(exponents):
    assert len(set(exponents)) == len(exponents)
    return sum(1 << e for e in exponents)


def degree(a):
    return a.bit_length() - 1


def display(a):
    if not a:
        return '0'
    return '+'.join('1' if k == 0 else 'X' if k == 1 else f'X^{k}'
                    for k in reversed(range(a.bit_length())) if (a >> k) & 1)


def multiply(a, b):
    result = 0
    while b:
        if b & 1:
            result ^= a
        a <<= 1
        b >>= 1
    return result


def remainder(a, b):
    assert b
    while degree(a) >= degree(b):
        a ^= b << (degree(a) - degree(b))
    return a


def exhaustive_divisors(f, name):
    """Every monic positive-degree polynomial through floor(deg(f)/2)."""
    records = []
    divisors = []
    for d in range(1, degree(f) // 2 + 1):
        for low in range(1 << d):
            candidate = (1 << d) | low
            r = remainder(f, candidate)
            records.append({'divisor_degree': d, 'divisor_mask': candidate,
                            'remainder_mask': r})
            if r == 0:
                divisors.append(candidate)
            print(f'DIVISION {name} divisor={candidate:#x} remainder={r:#x}')
    result = {'polynomial_mask': f, 'polynomial': display(f),
              'tested_monic_divisors': len(records), 'divisors': divisors,
              'irreducible': not divisors, 'records': records}
    print(f'IRREDUCIBILITY {name} tested={len(records)} '
          f'irreducible={not divisors} divisors={divisors}')
    return result


def apply(columns, v):
    result = 0
    for i, column in enumerate(columns):
        if (v >> i) & 1:
            result ^= column
    return result


def compose(left, right):
    return tuple(apply(left, column) for column in right)


def identity(n):
    return tuple(1 << j for j in range(n))


def flatten(columns, n):
    return sum(column << (n * j) for j, column in enumerate(columns))


def first_power_dependence(columns):
    """Gaussian elimination of I,F,F^2,..., with exact dependency tracking."""
    n = len(columns)
    pivots = {}
    power = identity(n)
    records = []
    for k in range(n + 1):
        vector = flatten(power, n)
        coefficients = 1 << k
        while vector:
            leading = vector.bit_length() - 1
            if leading in pivots:
                previous, previous_coefficients = pivots[leading]
                vector ^= previous
                coefficients ^= previous_coefficients
            else:
                pivots[leading] = (vector, coefficients)
                break
        records.append({'exponent': k, 'rank': len(pivots),
                        'dependent': vector == 0})
        print(f'MATRIX_POWER n={n} exponent={k} rank={len(pivots)} '
              f'dependent={vector == 0}')
        if vector == 0:
            assert degree(coefficients) == k
            return coefficients, records
        power = compose(columns, power)
    raise AssertionError('Cayley-Hamilton degree bound unexpectedly exceeded')


def matrix_order_up_to(columns, bound):
    result = identity(len(columns))
    for k in range(1, bound + 1):
        result = compose(columns, result)
        if result == identity(len(columns)):
            return k
    return None


def vector_rank(vectors):
    pivots = {}
    for vector in vectors:
        while vector:
            leading = degree(vector)
            if leading in pivots:
                vector ^= pivots[leading]
            else:
                pivots[leading] = vector
                break
    return len(pivots)


def expected_rejection(name, predicate):
    try:
        assert predicate, name
    except AssertionError:
        print(f'NEGATIVE_CONTROL {name}: EXPECTED ASSERTION FAILURE')
        return 'expected assertion failure; false target rejected'
    raise AssertionError(f'Negative control escaped rejection: {name}')


def main():
    raw = STATEMENT.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    assert digest == EXPECTED_HASH
    statement = json.loads(raw)
    assert statement['field_characteristic'] == 2
    assert statement['degree'] == 17
    print('STATEMENT_SHA256', digest)
    print('METHOD exact integer bitmasks for F2[X]; no randomness or timings')
    factors = {name: polynomial(exponents)
               for name, exponents in statement['polynomials'].items()}
    for name, f in factors.items():
        print('POLYNOMIAL', name, hex(f), display(f))
    degree16_product = multiply(factors['factor8a'], factors['factor8b'])
    print('DEGREE16_PRODUCT', hex(degree16_product), display(degree16_product))
    assert degree16_product == (1 << 17) - 1
    product = multiply(factors['factor1'], degree16_product)
    print('PRODUCT', hex(product), display(product))
    assert product == (1 << 17) | 1
    factor_results = {name: exhaustive_divisors(factors[name], name)
                      for name in ('factor8a', 'factor8b')}
    assert all(result['irreducible'] for result in factor_results.values())
    false_polynomial = (1 << 8) | 1
    false_factor = exhaustive_divisors(false_polynomial, 'false_X8_plus_1')
    false_factor['target_rejection'] = expected_rejection(
        'X^8+1 is irreducible', false_factor['irreducible'])
    factor_power = 1
    for _ in range(8):
        factor_power = multiply(factor_power, 3)
    assert factor_power == false_polynomial
    print('FALSE_FACTOR_WITNESS (X+1)^8 = X^8+1')

    modulus = statement['archived_polynomial_basis_modulus_bitmask']
    modulus_result = exhaustive_divisors(modulus, 'archived_modulus')
    assert modulus_result['irreducible']
    n = degree(modulus)
    assert n == 17
    columns = tuple(remainder(multiply(1 << j, 1 << j), modulus)
                    for j in range(n))
    print('ARCHIVED_FROBENIUS_COLUMNS', json.dumps(list(columns)))
    minpoly, ranks = first_power_dependence(columns)
    order = matrix_order_up_to(columns, 17)
    print('ARCHIVED_ORDER', order)
    print('ARCHIVED_MINPOLY', hex(minpoly), display(minpoly))
    assert order == 17
    assert minpoly == (1 << 17) | 1
    # Independent explicit normal-vector certificate, found from a fixed list.
    normal = None
    normal_orbit = None
    for candidate in range(1, 256):
        orbit = []
        current = candidate
        for _ in range(n):
            orbit.append(current)
            current = apply(columns, current)
        if vector_rank(orbit) == n:
            normal, normal_orbit = candidate, orbit
            assert current == candidate
            break
    assert normal is not None
    print('NORMAL_VECTOR', normal, 'ORBIT', json.dumps(normal_orbit), 'RANK', n)

    gf2_columns = (1,)
    gf2_minpoly, gf2_ranks = first_power_dependence(gf2_columns)
    gf2_order = matrix_order_up_to(gf2_columns, 17)
    assert gf2_order == 1 and gf2_minpoly == 3
    print('GF2_ORDER', gf2_order)
    print('GF2_MINPOLY', hex(gf2_minpoly), display(gf2_minpoly))
    false_order_result = expected_rejection('GF(2) Frobenius has order 17',
                                           gf2_order == 17)
    false_minpoly_result = expected_rejection(
        'GF(2) Frobenius has minimal polynomial X^17+1',
        gf2_minpoly == (1 << 17) | 1)
    # X^17+1 still annihilates identity, so annihilation alone is insufficient.
    assert sum((product >> k) & 1 for k in range(18)) % 2 == 0
    print('GF2_TARGET_POLYNOMIAL_ANNIHILATES True; MINIMALITY_FALSE')

    results = {
        'statement_sha256': digest,
        'arithmetic': 'exact F2 bitmask arithmetic and Gaussian elimination',
        'product_mask': product, 'product_polynomial': display(product),
        'factors': factor_results,
        'negative_reducibility_control': false_factor,
        'archived_quotient': {
            'modulus': modulus_result, 'frobenius_columns': list(columns),
            'order': order, 'minimal_polynomial_mask': minpoly,
            'matrix_power_rank_records': ranks,
            'normal_vector': normal, 'normal_orbit': normal_orbit,
            'normal_orbit_rank': n,
        },
        'negative_GF2_control': {
            'frobenius_columns': list(gf2_columns), 'order': gf2_order,
            'minimal_polynomial_mask': gf2_minpoly,
            'matrix_power_rank_records': gf2_ranks,
            'wrong_order_assertion': false_order_result,
            'wrong_minpoly_assertion': false_minpoly_result,
            'target_degree17_polynomial_annihilates': True,
        },
        'all_required_exact_checks_passed': True,
    }
    (ROOT / 'results.json').write_text(json.dumps(results, indent=2) + '\n')
    print('ALL_REQUIRED_EXACT_CHECKS_PASSED True')


if __name__ == '__main__':
    main()
