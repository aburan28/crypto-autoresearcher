#!/usr/bin/env python3
"""Stage-0 Kronecker-versus-kernel certificate for EXP-CSIDH-72413d.

Four primes at p = 47. No class-group action and no security level.
"""

from __future__ import annotations

import argparse
import json
from math import gcd
from pathlib import Path

EXPERIMENT_ID = "EXP-CSIDH-72413d"
RUN_ID = "RUN-CSIDH-92d9d9"
P = 47
PRIMES = (3, 5, 7, 11)


def legendre(value: int) -> int:
    value %= P
    if value == 0:
        return 0
    symbol = pow(value, (P - 1) // 2, P)
    return -1 if symbol == P - 1 else 1


def kronecker_split(prime: int) -> bool:
    residue = (-P) % prime
    return pow(residue, (prime - 1) // 2, prime) == 1


def kronecker_by_reciprocity(prime: int) -> bool:
    sign = (P - 1) * (prime - 1) // 4
    reciprocity = pow(prime, (P - 1) // 2, P)
    if reciprocity == P - 1:
        reciprocity = -1
    if sign % 2 == 1:
        reciprocity = -reciprocity
    minus = -1 if ((prime - 1) // 2) % 2 == 1 else 1
    return minus * reciprocity == 1


# Polynomials are coefficient lists, constant term first.
def trim(poly: list) -> list:
    while len(poly) > 1 and poly[-1] == 0:
        poly.pop()
    return poly or [0]


def deg(poly: list) -> int:
    trim(poly)
    return len(poly) - 1 if poly != [0] else -1


def padd(left: list, right: list) -> list:
    size = max(len(left), len(right))
    out = [(left[i] if i < len(left) else 0) + (right[i] if i < len(right) else 0) for i in range(size)]
    return trim([(item % P) for item in out])


def psub(left: list, right: list) -> list:
    return padd(left, [(-item) % P for item in right])


def pmul(left: list, right: list) -> list:
    out = [0] * (len(left) + len(right) - 1)
    for i, left_item in enumerate(left):
        for j, right_item in enumerate(right):
            out[i + j] = (out[i + j] + left_item * right_item) % P
    return trim(out)


def pscale(poly: list, scalar: int) -> list:
    return trim([(scalar * item) % P for item in poly])


def monic(poly: list) -> list:
    trim(poly)
    if poly == [0]:
        return poly
    inverse = pow(poly[-1], P - 2, P)
    return pscale(poly, inverse)


def pmod(left: list, right: list) -> list:
    left = trim(left[:])
    right = trim(right[:])
    if right == [0]:
        raise ZeroDivisionError
    while deg(left) >= deg(right) and left != [0]:
        factor = left[-1] * pow(right[-1], P - 2, P) % P
        shift = deg(left) - deg(right)
        left = psub(left, pmul(pscale(right, factor), [0] * shift + [1]))
    return trim(left)


def pdiv(left: list, right: list) -> list:
    quotient = [0] * (deg(left) - deg(right) + 1)
    rest = trim(left[:])
    while deg(rest) >= deg(right) and rest != [0]:
        factor = rest[-1] * pow(right[-1], P - 2, P) % P
        shift = deg(rest) - deg(right)
        quotient[shift] = factor
        rest = psub(rest, pmul(pscale(right, factor), [0] * shift + [1]))
    return trim(quotient)


def pgcd(left: list, right: list) -> list:
    while right != [0]:
        left, right = right, pmod(left, right)
    return monic(left)


def pderiv(poly: list) -> list:
    return trim([((index * item) % P) for index, item in enumerate(poly) if index > 0] or [0]) or [0]


def ppowmod(base: list, exp: int, modulus: list) -> list:
    result = [1]
    current = pmod(base, modulus)
    while exp:
        if exp & 1:
            result = pmod(pmul(result, current), modulus)
        current = pmod(pmul(current, current), modulus)
        exp >>= 1
    return result


def nullspace(matrix: list) -> list:
    size = len(matrix)
    reduced = [row[:] for row in matrix]
    pivot_row = [-1] * size
    row = 0
    for col in range(size):
        pivot = None
        for index in range(row, size):
            if reduced[index][col] % P != 0:
                pivot = index
                break
        if pivot is None:
            continue
        reduced[row], reduced[pivot] = reduced[pivot], reduced[row]
        inverse = pow(reduced[row][col], P - 2, P)
        reduced[row] = [(value * inverse) % P for value in reduced[row]]
        for index in range(size):
            if index == row or reduced[index][col] % P == 0:
                continue
            factor = reduced[index][col]
            reduced[index] = [
                (reduced[index][col_index] - factor * reduced[row][col_index]) % P for col_index in range(size)
            ]
        pivot_row[col] = row
        row += 1
    basis = []
    for col in range(size):
        if pivot_row[col] != -1:
            continue
        vector = [0] * size
        vector[col] = 1
        for pivot_col, source in enumerate(pivot_row):
            if source != -1:
                vector[pivot_col] = (-reduced[source][col]) % P
        basis.append(vector)
    return basis


def equal_degree(poly: list, degree: int) -> list:
    # Berlekamp. Powers of x leave products of equal-degree irreducibles unsplit.
    poly = monic(poly)
    if deg(poly) == degree:
        return [poly]
    if deg(poly) < degree or deg(poly) % degree != 0:
        return [poly]
    size = deg(poly)
    matrix = [[0] * size for _ in range(size)]
    for column in range(size):
        powered = ppowmod([0, 1], column * P, poly)
        for row, coeff in enumerate(powered):
            matrix[row][column] = coeff % P
        matrix[column][column] = (matrix[column][column] - 1) % P
    factors = [poly]
    for vector in nullspace(matrix):
        separator = trim(vector[:])
        if deg(separator) <= 0:
            continue
        refined = []
        for factor in factors:
            if deg(factor) <= degree:
                refined.append(factor)
                continue
            residual = factor
            for scalar in range(P):
                if deg(residual) <= degree:
                    break
                piece = pgcd(psub(pmod(separator, residual), [scalar]), residual)
                if deg(piece) == deg(residual):
                    break
                if deg(piece) > 0:
                    refined.append(monic(piece))
                    residual = monic(pdiv(residual, piece))
            if deg(residual) > 0:
                refined.append(monic(residual))
        factors = refined
        if all(deg(factor) == degree for factor in factors):
            break
    return factors


def irreducible_factors(poly: list) -> list:
    poly = monic(pgcd(poly, psub(poly, pmul(pderiv(poly), [0])))) if False else poly
    derivative = pderiv(poly)
    common = pgcd(poly, derivative)
    if deg(common) > 0:
        poly = pdiv(poly, common)
    poly = monic(poly)
    factors = []
    power = [0, 1]
    remaining = poly
    degree = 0
    while deg(remaining) > 0:
        degree += 1
        power = ppowmod(power, P, remaining)
        group = pgcd(psub(power, [0, 1]), remaining)
        if deg(group) > 0:
            factors.extend(equal_degree(monic(group), degree))
            remaining = monic(pdiv(remaining, group))
            power = pmod(power, remaining)
        if degree > deg(poly):
            break
    return factors


def factor_ok() -> bool:
    quadratic = [1, 0, 1]
    if irreducible_factors(quadratic) != [[1, 0, 1]]:
        return False
    split = irreducible_factors(psub([0, 0, 1], [1]))
    roots = sorted(item[0] for item in split)
    return roots == [1, P - 1] and len(split) == 2


class YPoly:
    def __init__(self, yexp: int, poly: list):
        self.yexp = yexp
        self.poly = trim(poly[:])


def y_reduce(value: YPoly, curve: list) -> YPoly:
    poly = value.poly
    yexp = value.yexp
    while yexp >= 2:
        poly = pmul(poly, curve)
        yexp -= 2
    return YPoly(yexp, poly)


def y_mul(left: YPoly, right: YPoly, curve: list) -> YPoly:
    return YPoly(left.yexp + right.yexp, pmul(left.poly, right.poly))


def y_scale(value: YPoly, scalar: int) -> YPoly:
    return YPoly(value.yexp, pscale(value.poly, scalar))


def y_sub(left: YPoly, right: YPoly, curve: list) -> YPoly:
    del curve
    if left.yexp != right.yexp:
        raise RuntimeError("division-polynomial parity mismatch")
    return YPoly(left.yexp, psub(left.poly, right.poly))


def y_pow(value: YPoly, exp: int, curve: list) -> YPoly:
    result = YPoly(0, [1])
    current = value
    while exp:
        if exp & 1:
            result = y_mul(result, current, curve)
        current = y_mul(current, current, curve)
        exp >>= 1
    return result


def division_polynomial(short_a: int, short_b: int, index: int) -> list:
    curve = [short_b % P, short_a % P, 0, 1]
    psi = {
        0: YPoly(0, [0]),
        1: YPoly(0, [1]),
        2: YPoly(1, [2]),
        3: YPoly(0, [(-short_a * short_a) % P, (12 * short_b) % P, (6 * short_a) % P, 0, 3]),
        4: YPoly(1, pscale(
            [
                (-8 * short_b * short_b - short_a ** 3) % P,
                (-4 * short_a * short_b) % P,
                (-5 * short_a * short_a) % P,
                (20 * short_b) % P,
                (5 * short_a) % P,
                0,
                1,
            ],
            4,
        )),
    }
    for current in range(5, index + 1):
        if current % 2 == 1:
            half = current // 2
            left = y_reduce(y_mul(psi[half + 2], y_pow(psi[half], 3, curve), curve), curve)
            right = y_reduce(y_mul(psi[half - 1], y_pow(psi[half + 1], 3, curve), curve), curve)
            psi[current] = y_reduce(y_sub(left, right, curve), curve)
        else:
            half = current // 2
            bracket_left = y_mul(psi[half + 2], y_pow(psi[half - 1], 2, curve), curve)
            bracket_right = y_mul(psi[half - 2], y_pow(psi[half + 1], 2, curve), curve)
            bracket = y_sub(bracket_left, bracket_right, curve)
            product = y_mul(psi[half], bracket, curve)
            if product.yexp < 1:
                raise RuntimeError("missing y in an even division polynomial")
            product.yexp -= 1
            psi[current] = y_scale(y_reduce(product, curve), pow(2, P - 2, P))
    result = y_reduce(psi[index], curve)
    if result.yexp != 0:
        raise RuntimeError("odd division polynomial retained y")
    return result.poly


def division_ok(short_a: int, short_b: int) -> bool:
    for prime in PRIMES:
        poly = division_polynomial(short_a, short_b, prime)
        if deg(poly) != (prime * prime - 1) // 2 or poly[-1] % P != prime % P:
            return False
    return True


class Ext:
    def __init__(self, modulus: list):
        self.mod = monic(modulus)
        self.degree = deg(self.mod)
        self.order = pow(P, self.degree)

    def norm(self, value: list) -> list:
        return trim(pmod(value, self.mod))

    def add(self, left: list, right: list) -> list:
        return self.norm(padd(left, right))

    def sub(self, left: list, right: list) -> list:
        return self.norm(psub(left, right))

    def mul(self, left: list, right: list) -> list:
        return self.norm(pmul(left, right))

    def scale(self, value: list, scalar: int) -> list:
        return self.norm(pscale(value, scalar))

    def pow(self, value: list, exp: int) -> list:
        result = [1]
        current = self.norm(value)
        while exp:
            if exp & 1:
                result = self.mul(result, current)
            current = self.mul(current, current)
            exp >>= 1
        return result

    def to_prime(self, value: list) -> int | None:
        return in_prime_field(self.norm(value))

    def is_zero(self, value: list) -> bool:
        return self.norm(value) == [0]

    def const(self, scalar: int) -> list:
        return [scalar % P]

    def inv(self, value: list) -> list:
        if self.is_zero(value):
            raise ZeroDivisionError
        return self.pow(value, self.order - 2)

    def is_square(self, value: list) -> bool:
        value = self.norm(value)
        if value == [0]:
            return True
        return self.pow(value, (self.order - 1) // 2) == [1]

    def sqrt(self, value: list) -> list:
        value = self.norm(value)
        if value == [0]:
            return [0]
        if self.order % 4 == 3:
            return self.pow(value, (self.order + 1) // 4)
        order_minus = self.order - 1
        qq, ss = order_minus, 0
        while qq % 2 == 0:
            qq //= 2
            ss += 1
        nonresidue = [2]
        while self.is_square(nonresidue):
            nonresidue = self.add(nonresidue, [1])
        mm, cc, tt, rr = ss, self.pow(nonresidue, qq), self.pow(value, qq), self.pow(value, (qq + 1) // 2)
        while tt != [1]:
            ii, trial = 0, tt
            while trial != [1]:
                trial = self.mul(trial, trial)
                ii += 1
            bb = self.pow(cc, 1 << (mm - ii - 1))
            mm, cc, tt, rr = ii, self.mul(bb, bb), self.mul(tt, self.mul(bb, bb)), self.mul(rr, bb)
        return rr


def ec_add(field, short_a: int, left, right):
    if left is None:
        return right
    if right is None:
        return left
    x1, y1 = left
    x2, y2 = right
    if field.is_zero(field.sub(x1, x2)) and field.is_zero(field.add(y1, y2)):
        return None
    if field.is_zero(field.sub(x1, x2)) and field.is_zero(field.sub(y1, y2)):
        if field.is_zero(y1):
            return None
        slope = field.mul(
            field.add(field.scale(field.mul(x1, x1), 3), field.const(short_a)),
            field.inv(field.scale(y1, 2)),
        )
    else:
        slope = field.mul(field.sub(y2, y1), field.inv(field.sub(x2, x1)))
    x3 = field.sub(field.sub(field.mul(slope, slope), x1), x2)
    y3 = field.sub(field.mul(slope, field.sub(x1, x3)), y1)
    return x3, y3


def ec_mul(field: Ext, short_a: int, scalar: int, point):
    result = None
    current = point
    while scalar:
        if scalar & 1:
            result = ec_add(field, short_a, result, current)
        current = ec_add(field, short_a, current, current)
        scalar >>= 1
    return result


def short_point_count(short_a: int, short_b: int) -> int:
    count = 1
    for x_value in range(P):
        symbol = legendre((x_value ** 3 + short_a * x_value + short_b) % P)
        count += 1 if symbol == 0 else (2 if symbol == 1 else 0)
    return count


def montgomery_point_count(coefficient: int) -> int:
    count = 1
    for x_value in range(P):
        symbol = legendre((x_value ** 3 + coefficient * x_value * x_value + x_value) % P)
        count += 1 if symbol == 0 else (2 if symbol == 1 else 0)
    return count


def to_short(coefficient: int) -> tuple[int, int]:
    shift = coefficient * pow(3, P - 2, P) % P
    short_a = (3 * shift * shift - 2 * coefficient * shift + 1) % P
    short_b = (-shift ** 3 + coefficient * shift * shift - shift) % P
    return short_a, short_b


def fourth_power(value: int) -> bool:
    value %= P
    if value == 0:
        return False
    group = gcd(4, P - 1)
    return pow(value, (P - 1) // group, P) == 1


def montgomery_shape(short_a: int, short_b: int) -> bool:
    if (4 * short_a ** 3 + 27 * short_b ** 2) % P == 0:
        return False
    for root in range(P):
        if (root ** 3 + short_a * root + short_b) % P != 0:
            continue
        beta = (3 * root * root + short_a) % P
        if beta != 0 and fourth_power(beta):
            return True
    return False


def in_prime_field(value: list) -> int | None:
    trimmed = trim(value[:])
    if len(trimmed) > 1:
        return None
    return trimmed[0] % P


class Quad:
    def __init__(self, base: Ext, rhs: list):
        self.base = base
        self.rhs = base.norm(rhs)
        self.order = base.order * base.order

    def const(self, scalar: int):
        return (self.base.const(scalar), self.base.const(0))

    def embed(self, value: list):
        return (self.base.norm(value), self.base.const(0))

    def is_zero(self, value) -> bool:
        left, right = value
        return self.base.is_zero(left) and self.base.is_zero(right)

    def add(self, left, right):
        return (self.base.add(left[0], right[0]), self.base.add(left[1], right[1]))

    def sub(self, left, right):
        return (self.base.sub(left[0], right[0]), self.base.sub(left[1], right[1]))

    def scale(self, value, scalar: int):
        return (self.base.scale(value[0], scalar), self.base.scale(value[1], scalar))

    def mul(self, left, right):
        real = self.base.add(self.base.mul(left[0], right[0]), self.base.mul(self.base.mul(left[1], right[1]), self.rhs))
        imag = self.base.add(self.base.mul(left[0], right[1]), self.base.mul(left[1], right[0]))
        return real, imag

    def pow(self, value, exp: int):
        result = self.const(1)
        current = value
        while exp:
            if exp & 1:
                result = self.mul(result, current)
            current = self.mul(current, current)
            exp >>= 1
        return result

    def inv(self, value):
        if self.is_zero(value):
            raise ZeroDivisionError
        return self.pow(value, self.order - 2)

    def to_prime(self, value) -> int | None:
        if not self.base.is_zero(value[1]):
            return None
        return in_prime_field(value[0])


def velu(field, short_a: int, short_b: int, point, prime: int):
    reps = []
    current = point
    for _ in range((prime - 1) // 2):
        if current is None:
            return None
        reps.append(current)
        current = ec_add(field, short_a, current, point)
    total_t = field.const(0)
    total_w = field.const(0)
    for x_value, y_value in reps:
        t_value = field.add(field.scale(field.mul(x_value, x_value), 6), field.const(2 * short_a))
        u_value = field.scale(field.mul(y_value, y_value), 4)
        w_value = field.add(u_value, field.mul(x_value, t_value))
        total_t = field.add(total_t, t_value)
        total_w = field.add(total_w, w_value)
    prime_t = field.to_prime(total_t)
    prime_w = field.to_prime(total_w)
    if prime_t is None or prime_w is None:
        return None
    return (short_a - 5 * prime_t) % P, (short_b - 7 * prime_w) % P


def curve_singular_short(short_a: int, short_b: int) -> bool:
    return (4 * pow(short_a, 3, P) + 27 * pow(short_b, 2, P)) % P == 0


def kernel_quotient(short_a: int, short_b: int, prime: int, domain_count: int):
    if curve_singular_short(short_a, short_b):
        return False
    poly = division_polynomial(short_a, short_b, prime)
    for factor in irreducible_factors(poly):
        if deg(factor) < 1 or ((prime - 1) // 2) % deg(factor) != 0:
            continue
        base = Ext(factor)
        x_value = [0, 1]
        rhs = base.add(
            base.add(base.mul(base.mul(x_value, x_value), x_value), base.scale(x_value, short_a)),
            base.const(short_b),
        )
        if base.is_zero(rhs):
            continue
        if base.is_square(rhs):
            arenas = [(base, (x_value, base.sqrt(rhs)))]
        else:
            quad = Quad(base, rhs)
            arenas = [(quad, (quad.embed(x_value), (base.const(0), base.const(1))))]
        for field, point in arenas:
            if ec_mul(field, short_a, prime, point) is not None:
                continue
            codomain = velu(field, short_a, short_b, point, prime)
            if codomain is None:
                continue
            image_a, image_b = codomain
            if short_point_count(image_a, image_b) != domain_count:
                continue
            if domain_count == P + 1 and montgomery_shape(image_a, image_b):
                return True
    return False


def singular(coefficient: int) -> bool:
    return (coefficient * coefficient - 4) % P == 0


def smallest(supersingular: bool) -> int | None:
    for coefficient in range(1, P - 1):
        if singular(coefficient):
            continue
        matches = montgomery_point_count(coefficient) == P + 1
        if matches == supersingular:
            return coefficient
    return None


def census() -> dict:
    split = [prime for prime in PRIMES if kronecker_split(prime)]
    symbols_agree = all(kronecker_split(prime) == kronecker_by_reciprocity(prime) for prime in PRIMES)
    chosen = smallest(True)
    ordinary = smallest(False)
    singular_a, singular_b = to_short(2)
    singular_refused = curve_singular_short(singular_a, singular_b) and kernel_quotient(singular_a, singular_b, 3, P + 1) is False
    counts_match = False
    division_good = False
    velu_good = False
    edge = None
    if chosen is not None:
        short_a, short_b = to_short(chosen)
        counts_match = montgomery_point_count(chosen) == short_point_count(short_a, short_b) == P + 1
        division_good = division_ok(short_a, short_b)
        velu_good = prime_velu_preserves_count(short_a, short_b)
        edge = [prime for prime in PRIMES if kernel_quotient(short_a, short_b, prime, P + 1)]
    difference = None if edge is None else len(set(split).symmetric_difference(edge))
    planted_ok = bool(
        symbols_agree
        and factor_ok()
        and singular_refused
        and ordinary is not None
        and chosen is not None
        and chosen != ordinary
        and counts_match
        and division_good
        and velu_good
        and edge is not None
    )
    matrix_holds = planted_ok and difference == 0
    return {
        "attack_claimed": False,
        "beyond_matrix": planted_ok and not matrix_holds,
        "curve_A": chosen,
        "edge": edge,
        "experiment_id": EXPERIMENT_ID,
        "matrix_holds": matrix_holds,
        "ordinary_A": ordinary,
        "planted_ok": planted_ok,
        "prime": P,
        "run_id": RUN_ID,
        "split": split,
        "symmetric_difference": difference,
    }


def prime_velu_preserves_count(short_a: int, short_b: int) -> bool:
    count = short_point_count(short_a, short_b)
    if count % 3 != 0:
        return False
    cofactor = count // 3
    for x_value in range(P):
        rhs = (x_value ** 3 + short_a * x_value + short_b) % P
        if legendre(rhs) != 1:
            continue
        y_value = pow(rhs, (P + 1) // 4, P)
        point = ([x_value], [y_value])
        field = Ext([P - 1, 1])  # z + (P-1) = z - 1, a dummy linear field isomorphic to F_p via z=1
        # The dummy modulus z-1 collapses every element to its evaluation at 1, which is wrong.
        break
    # Prime-field Vélu, copied from the checked formula, without an extension.
    def add(left, right):
        if left is None:
            return right
        if right is None:
            return left
        x1, y1 = left
        x2, y2 = right
        if x1 == x2 and (y1 + y2) % P == 0:
            return None
        if left == right:
            slope = (3 * x1 * x1 + short_a) * pow(2 * y1, P - 2, P) % P
        else:
            slope = (y2 - y1) * pow((x2 - x1) % P, P - 2, P) % P
        x3 = (slope * slope - x1 - x2) % P
        y3 = (slope * (x1 - x3) - y1) % P
        return x3, y3

    def mul(scalar, point):
        result = None
        current = point
        while scalar:
            if scalar & 1:
                result = add(result, current)
            current = add(current, current)
            scalar >>= 1
        return result

    for x_value in range(P):
        rhs = (x_value ** 3 + short_a * x_value + short_b) % P
        if legendre(rhs) != 1:
            continue
        y_value = pow(rhs, (P + 1) // 4, P)
        image = mul(cofactor, (x_value, y_value))
        if image is None or mul(3, image) is not None:
            continue
        reps = []
        current = image
        for _ in range(1):
            reps.append(current)
            current = add(current, image)
        total_t = 0
        total_w = 0
        for xq, yq in reps:
            t_value = (6 * xq * xq + 2 * short_a) % P
            w_value = (4 * yq * yq + xq * t_value) % P
            total_t = (total_t + t_value) % P
            total_w = (total_w + w_value) % P
        image_a = (short_a - 5 * total_t) % P
        image_b = (short_b - 7 * total_w) % P
        return short_point_count(image_a, image_b) == count
    return False


def write_outputs(run_dir: Path, result: dict) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "raw-result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (run_dir / "manifest.yaml").write_text(
        "run:\n"
        f"  experiment_id: {EXPERIMENT_ID}\n"
        f"  run_id: {RUN_ID}\n"
        "  attack_claimed: false\n"
        "  metrics:\n"
        f"    planted_ok: {str(result['planted_ok']).lower()}\n"
        f"    matrix_holds: {str(result['matrix_holds']).lower()}\n"
        f"    beyond_matrix: {str(result['beyond_matrix']).lower()}\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trial-plan", required=True)
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args()
    write_outputs(Path(args.run_dir), census())


if __name__ == "__main__":
    main()
