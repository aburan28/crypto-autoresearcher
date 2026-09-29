"""Exact local-section arithmetic; deliberately has no group-oracle dependency.

Recovery consumes only the field, curve constant and normalized coefficients.
A coordinator of the computation may compare its output to a separate oracle.
"""
from collections import Counter
from itertools import product


class Field:
    def __init__(self, p):
        self.p = p
        self.counts = Counter(addition=0, multiplication=0, inversion=0, equality=0)

    def add(self, a, b):
        self.counts['addition'] += 1
        return (a + b) % self.p

    def sub(self, a, b):
        return self.add(a, -b)

    def mul(self, a, b):
        self.counts['multiplication'] += 1
        return (a * b) % self.p

    def eq(self, a, b):
        self.counts['equality'] += 1
        return a == b

    def inv(self, a):
        if self.eq(a % self.p, 0):
            raise ArithmeticError('incidence division by zero')
        self.counts['inversion'] += 1
        r = pow(a, -1, self.p)
        if not self.eq(self.mul(a, r), 1):
            raise ArithmeticError('incidence inverse verification')
        return r

    def power(self, a, exponent):
        result = 1
        for _ in range(exponent):
            result = self.mul(result, a)
        return result


def trim(poly, field):
    values = list(poly) or [0]
    while len(values) > 1 and field.eq(values[-1], 0):
        values.pop()
    return values


def padd(a, b, field, precision=None):
    n = max(len(a), len(b)) if precision is None else precision
    return [field.add(a[i] if i < len(a) else 0, b[i] if i < len(b) else 0)
            for i in range(n)]


def scale(a, scalar, field):
    return [field.mul(scalar, x) for x in a]


def psub(a, b, field, precision=None):
    return padd(a, scale(b, -1, field), field, precision)


def pmul(a, b, field, precision=None):
    n = len(a) + len(b) - 1 if precision is None else precision
    result = [0] * n
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            if i + j < n:
                result[i + j] = field.add(result[i + j], field.mul(x, y))
    return result


def evaluate(poly, x, field):
    value = 0
    for coefficient in reversed(poly):
        value = field.add(field.mul(value, x), coefficient)
    return value


def divide_linear(poly, root, field):
    """Synthetic division with exact remainder; retain each actual quotient."""
    poly = trim(poly, field)
    if len(poly) < 2:
        raise ValueError('cannot divide constant by a linear polynomial')
    quotient = [0] * (len(poly) - 1)
    quotient[-1] = poly[-1]
    for j in range(len(quotient) - 2, -1, -1):
        quotient[j] = field.add(poly[j + 1], field.mul(root, quotient[j + 1]))
    remainder = field.add(poly[0], field.mul(root, quotient[0]))
    return trim(quotient, field), remainder


def factor_rational(poly, field):
    residual = trim(poly, field)
    roots, divisions = [], []
    for root in range(field.p):
        multiplicity = 0
        while len(residual) > 1 and field.eq(evaluate(residual, root, field), 0):
            before = residual[:]
            residual, remainder = divide_linear(residual, root, field)
            divisions.append({'root': root, 'dividend': before,
                              'quotient': residual[:], 'remainder': remainder})
            if not field.eq(remainder, 0):
                raise ArithmeticError('inconsistent rational-root division')
            multiplicity += 1
        if multiplicity:
            roots.append((root, multiplicity))
    return roots, residual, divisions


def rhs(x, constant, field):
    return field.add(field.add(field.power(x, 3), x), constant)


def membership(point, constant, field):
    if point is None:
        return True
    if len(point) != 2 or any(type(x) is not int or not 0 <= x < field.p for x in point):
        return False
    return field.eq(field.mul(point[1], point[1]), rhs(point[0], constant, field))


def enumerate_points(constant, field):
    return [None] + [(a, b) for a in range(field.p) for b in range(field.p)
                     if membership((a, b), constant, field)]


def normalize(coefficients, field):
    if len(coefficients) != 4 or any(type(x) is not int or not 0 <= x < field.p for x in coefficients):
        raise ValueError('four canonical residues required')
    pivot = next((x for x in coefficients if not field.eq(x, 0)), None)
    if pivot is None:
        raise ValueError('zero projective vector')
    inverse = field.inv(pivot)
    return tuple(field.mul(x, inverse) for x in coefficients)


def sections(field):
    # Each first-nonzero chart is generated once; final order is global lexicographic.
    rows = []
    for k in range(4):
        rows.extend((0,) * k + (1,) + suffix
                    for suffix in product(range(field.p), repeat=3-k))
    yield from sorted(rows)


def chart(point):
    return 'O' if point is None else ('Y0' if point[1] == 0 else 'Ynonzero')


def local_basis(point, constant, field, arm='B'):
    """Through t^4 using recurrences, including the c-dependent Eprime O chart."""
    if arm not in ('B', 'I') or not membership(point, constant, field):
        raise ValueError('invalid chart point or arm')
    one, t = [1, 0, 0, 0, 0], [0, 1, 0, 0, 0]
    mul = lambda a, b: pmul(a, b, field, 5)
    sub = lambda a, b: psub(a, b, field, 5)
    if point is None:
        u = [0] * 5
        for k in range(1, 5):
            u2 = mul(u, u)
            residual = sub(sub(sub(mul(t, t), u), mul(u2, u)),
                           scale(mul(u2, u2), constant, field))
            u[k] = residual[k]  # derivative of residual wrt u_k is -1.
        w = mul(u, u)
        if arm == 'I':
            residual = sub(sub(sub(mul(t, t), u), mul(u, w)),
                           scale(mul(w, w), constant, field))
        else:
            residual = sub(sub(sub(mul(t, t), u), mul(mul(u, u), u)),
                           scale(mul(mul(u, u), mul(u, u)), constant, field))
        if any(not field.eq(x, 0) for x in residual):
            raise ArithmeticError('O recurrence residual')
        return [w, u, t, one]
    a, b = point
    if not field.eq(b, 0):
        x, y = [a, 1, 0, 0, 0], [b, 0, 0, 0, 0]
        inverse = field.inv(field.mul(2, b))
        for k in range(1, 5):
            residual = sub(sub(sub(mul(y, y), mul(mul(x, x), x)), x),
                           [constant, 0, 0, 0, 0])
            y[k] = field.mul(field.sub(0, residual[k]), inverse)
    else:
        x, y = [a, 0, 0, 0, 0], t
        inverse = field.inv(field.add(field.mul(3, field.mul(a, a)), 1))
        for k in range(1, 5):
            residual = sub(sub(sub(mul(y, y), mul(mul(x, x), x)), x),
                           [constant, 0, 0, 0, 0])
            x[k] = field.mul(residual[k], inverse)
    z = mul(x, x)
    residual = sub(sub(sub(mul(y, y), mul(x, z)), x), [constant, 0, 0, 0, 0])
    if any(not field.eq(v, 0) for v in residual):
        raise ArithmeticError('finite recurrence residual')
    return [one, x, y, z]


def section_series(coefficients, basis, field):
    result = [0] * 5
    for coefficient, vector in zip(coefficients, basis):
        result = padd(result, scale(vector, coefficient, field), field, 5)
    return result


def order_of(series, field):
    for j, coefficient in enumerate(series):
        if not field.eq(coefficient, 0):
            return j
    raise ArithmeticError('nonzero section vanishes through t^4')


def jet_matrix(divisor, points, constant, field, arm='B'):
    if len(divisor) != 4 or tuple(sorted(divisor)) != tuple(divisor):
        raise ValueError('divisor must be a sorted four-index list')
    rows = []
    for index, multiplicity in sorted(Counter(divisor).items()):
        if type(index) is not int or not 0 <= index < len(points):
            raise ValueError('invalid point index')
        basis = local_basis(points[index], constant, field, arm)
        rows.extend([basis[column][j] for column in range(4)]
                    for j in range(multiplicity))
    return rows


def rank_kernel(matrix, field):
    a = [list(row) for row in matrix]
    pivots = []
    for col in range(4):
        pivot = next((r for r in range(len(pivots), 4) if not field.eq(a[r][col], 0)), None)
        if pivot is None:
            continue
        row = len(pivots)
        a[row], a[pivot] = a[pivot], a[row]
        a[row] = scale(a[row], field.inv(a[row][col]), field)
        for r in range(4):
            if r != row:
                factor = a[r][col]
                a[r] = [field.sub(a[r][j], field.mul(factor, a[row][j])) for j in range(4)]
        pivots.append(col)
    kernel = []
    for free in (j for j in range(4) if j not in pivots):
        vector = [0] * 4
        vector[free] = 1
        for row, pivot in enumerate(pivots):
            vector[pivot] = field.sub(0, a[row][free])
        kernel.append(list(normalize(vector, field)))
    return {'rank': len(pivots), 'rref': a, 'kernel_basis': kernel,
            'unique_section': kernel[0] if len(kernel) == 1 else None}


def recover(coefficients, constant, field):
    """No points table or relation input: derive support solely by polynomial division."""
    c = tuple(coefficients)
    if normalize(c, field) != c:
        raise ValueError('section is not normalized')
    c0, c1, c2, c3 = c
    h = trim([c0, c1, c3], field)
    supports, nonsplit, witnesses = [], [], []
    if not field.eq(c2, 0):
        polynomial = trim(psub(pmul(h, h, field),
                               scale([constant, 1, 0, 1], field.mul(c2, c2), field), field), field)
        degree = len(polynomial) - 1
        required_degree = 4 if not field.eq(c3, 0) else 3
        if degree != required_degree:
            raise ArithmeticError('unexpected elimination degree')
        roots, residual, divisions = factor_rational(polynomial, field)
        inverse = field.inv(c2)
        for a, e in roots:
            b = field.mul(field.sub(0, evaluate(h, a, field)), inverse)
            supports.append(((a, b), e))
        infinity_multiplicity = 4 - degree
        unresolved_degree = len(residual) - 1
        grammar_branch = 'c2_nonzero_c3_nonzero' if c3 else 'c2_nonzero_c3_zero'
    else:
        polynomial = h
        degree = len(h) - 1
        roots, residual, divisions = factor_rational(h, field)
        unresolved_degree = 2 * (len(residual) - 1)
        for a, e in roots:
            value = rhs(a, constant, field)
            ys = [b for b in range(field.p) if field.eq(field.mul(b, b), value)]
            witnesses.append({'x': a, 'rhs': value, 'roots_y': ys,
                              'squares': sorted({field.mul(b, b) for b in range(field.p)})})
            if not ys:
                unresolved_degree += 2 * e
                nonsplit.append({'x': a, 'root_multiplicity': e, 'unresolved_degree': 2 * e})
            elif ys == [0]:
                supports.append(((a, 0), 2 * e))
            elif len(ys) == 2:
                supports.extend(((a, b), e) for b in ys)
            else:
                raise ArithmeticError('invalid square-root branch cardinality')
        infinity_multiplicity = 4 - 2 * degree
        grammar_branch = 'c2_zero_h_degree_' + str(degree)
    O_series = section_series(c, local_basis(None, constant, field), field)
    O_order = order_of(O_series, field)
    if O_order != infinity_multiplicity:
        raise ArithmeticError('infinity jet and pole-deficit mismatch: ' + repr((c, O_series, infinity_multiplicity)))
    if infinity_multiplicity:
        supports.append((None, infinity_multiplicity))
    rational_degree = sum(e for _, e in supports)
    if rational_degree + unresolved_degree != 4:
        raise ArithmeticError('section degree is not exhausted')
    multiplicities = []
    for point, multiplicity in supports:
        if not membership(point, constant, field):
            raise ArithmeticError('recovered point fails original curve membership')
        series_b = section_series(c, local_basis(point, constant, field, 'B'), field)
        series_i = section_series(c, local_basis(point, constant, field, 'I'), field)
        actual_b, actual_i = order_of(series_b, field), order_of(series_i, field)
        multiplicities.append({'point': encode_point(point), 'multiplicity': multiplicity,
                               'B_series': series_b, 'I_series': series_i,
                               'B_order': actual_b, 'I_order': actual_i})
        if actual_b != multiplicity or actual_i != multiplicity:
            raise ArithmeticError('root/division and local jet multiplicity mismatch')
    sorted_points = sorted((point for point, e in supports for _ in range(e)), key=point_key)
    return {'coefficients': list(c), 'grammar_branch': grammar_branch,
            'polynomial': polynomial, 'polynomial_degree': degree,
            'residual_polynomial': residual, 'rational_roots': roots,
            'divisions': divisions, 'nonsplit_roots': nonsplit,
            'square_witnesses': witnesses, 'local_multiplicities': multiplicities,
            'O_multiplicity': infinity_multiplicity, 'O_series': O_series, 'O_order': O_order,
            'rational_degree': rational_degree,
            'unresolved_degree': unresolved_degree, 'admissible': unresolved_degree == 0,
            'recovered_divisor_points': [encode_point(p) for p in sorted_points]
                if unresolved_degree == 0 else None}


def encode_point(point):
    return {'infinity': True} if point is None else {'infinity': False, 'x': point[0], 'y': point[1]}


def decode_point(point):
    return None if point == {'infinity': True} else (point['x'], point['y'])


def point_key(point):
    return (-1, -1) if point is None else point


def projective_residuals(vector, constant, field):
    if (len(vector) != 4 or any(type(x) is not int or not 0 <= x < field.p for x in vector)
            or all(field.eq(x, 0) for x in vector)):
        raise ValueError('nonzero projective point required')
    a, x, y, z = vector
    q1 = field.sub(field.mul(a, z), field.mul(x, x))
    q2 = field.sub(field.sub(field.sub(field.mul(y, y), field.mul(x, z)), field.mul(a, x)),
                   field.mul(constant, field.mul(a, a)))
    return [q1, q2]


def projective_inverse(vector, constant, field):
    residuals = projective_residuals(vector, constant, field)
    if any(not field.eq(x, 0) for x in residuals):
        raise ValueError('projective curve membership failed: ' + repr(residuals))
    a, x, y, z = vector
    if field.eq(a, 0):
        if not field.eq(x, 0) or not field.eq(y, 0) or field.eq(z, 0):
            raise ValueError('invalid O chart')
        return None
    inverse = field.inv(a)
    point = (field.mul(x, inverse), field.mul(y, inverse))
    if not membership(point, constant, field):
        raise ArithmeticError('projective inverse fails original curve membership')
    return point
