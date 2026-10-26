"""Separate norm, point and dense-kernel consumer; no producer imports."""
from collections import Counter


def trim(values, p):
    values = [int(v) % p for v in values]
    while len(values) > 1 and not values[-1]:
        values.pop()
    return values or [0]


def multiply(left, right, p):
    result = [0] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            result[i+j] = (result[i+j] + a*b) % p
    return trim(result, p)


def subtract(left, right, p):
    return trim([(left[i] if i < len(left) else 0) -
                 (right[i] if i < len(right) else 0)
                 for i in range(max(len(left), len(right)))], p)


def remainder(left, right, p):
    value = trim(left, p)
    inverse = pow(right[-1], -1, p)
    while value != [0] and len(value) >= len(right):
        shift, scale = len(value)-len(right), value[-1]*inverse % p
        for j, coefficient in enumerate(right):
            value[j+shift] = (value[j+shift]-scale*coefficient) % p
        value = trim(value, p)
    return value


def gcd(left, right, p):
    while right != [0]:
        left, right = right, remainder(left, right, p)
    return trim([c*pow(left[-1], -1, p) for c in left], p)


def modular_power(base, exponent, modulus, p):
    answer = [1]
    while exponent:
        if exponent & 1:
            answer = remainder(multiply(answer, base, p), modulus, p)
        base = remainder(multiply(base, base, p), modulus, p)
        exponent //= 2
    return answer


def irreducible(q, p):
    degree = len(q)-1
    if degree == 1:
        return True
    # Rabin's test, with explicit distinct prime divisors of degree.
    divisors, residual, factor = [], degree, 2
    while factor*factor <= residual:
        if residual % factor == 0:
            divisors.append(factor)
            while residual % factor == 0:
                residual //= factor
        factor += 1
    if residual > 1:
        divisors.append(residual)
    x = [0, 1]
    for ell in divisors:
        h = subtract(modular_power(x, p**(degree//ell), q, p), x, p)
        if len(gcd(q, h, p)) != 1:
            return False
    return remainder(subtract(modular_power(x, p**degree, q, p), x, p), q, p) == [0]


def evaluate(poly, value, p):
    result = 0
    for coefficient in reversed(poly):
        result = (result*value+coefficient) % p
    return result


class Jacobian:
    def __init__(self, p, a, r):
        self.p, self.a, self.r = p, a, r
        self.zero = (1, 1, 0)

    def double(self, P):
        x, y, z = P
        p = self.p
        if not z or not y:
            return self.zero
        xx, yy, zz = x*x % p, y*y % p, z*z % p
        s = 2*((x+yy)**2-xx-yy*yy) % p
        m = (3*xx+self.a*zz*zz) % p
        u = (m*m-2*s) % p
        return u, (m*(s-u)-8*yy*yy) % p, 2*y*z % p

    def add(self, P, Q):
        x, y, z = P
        u, v, w = Q
        p = self.p
        if not z:
            return Q
        if not w:
            return P
        x1, x2 = x*w*w % p, u*z*z % p
        y1, y2 = y*w*w*w % p, v*z*z*z % p
        if x1 == x2:
            return self.double(P) if y1 == y2 else self.zero
        h, rr = (x2-x1) % p, (y2-y1) % p
        h2, h3 = h*h % p, h*h*h % p
        q = x1*h2 % p
        s = (rr*rr-h3-2*q) % p
        return s, (rr*(q-s)-y1*h3) % p, h*z*w % p

    def mul(self, scalar, point):
        result = self.zero
        for bit in bin(scalar % self.r)[2:]:
            result = self.double(result)
            if bit == "1":
                result = self.add(result, point)
        return result

    def check_row(self, row, points):
        result = self.zero
        for key, coefficient in row.items():
            x, y = points[key]
            result = self.add(result, self.mul(coefficient, (x, y, 1)))
        if result[2] != 0:
            raise AssertionError("Point-sum certificate refuted")


def check_divisor(case, p, a, b, r):
    A, B = case["A"], case["B"]
    if len(B) != 1 or B[0] % p == 0:
        raise ValueError("This consumer checks nonzero constant y coefficient")
    norm = subtract(multiply(A, A, p),
                    [c*(B[0]*B[0] % p) % p for c in [b % p, a % p, 0, 1]], p)
    assert norm == case["norm"]
    assert len(norm)-1 == case["pole_order"]
    product, expected, unresolved = [case["norm_unit"]], [], []
    factors_seen = set()
    for factor in case["norm_factors"]:
        q, power = factor["coefficients"], factor["multiplicity"]
        assert tuple(q) not in factors_seen
        factors_seen.add(tuple(q))
        assert len(q)-1 == factor["degree"] and power >= 1
        assert irreducible(q, p)
        for _ in range(power):
            product = multiply(product, q, p)
        if len(q) != 2:
            unresolved.append((tuple(q), power))
            continue
        x = -q[0]*pow(q[1], -1, p) % p
        y = -evaluate(A, x, p)*pow(B[0], -1, p) % p
        assert y and (y*y-x*x*x-a*x-b) % p == 0
        # Conjugate factor A-yB is nonzero at this point: norm multiplicity
        # equals local multiplicity of A+yB, also for repeated zeros.
        assert (evaluate(A, x, p)-y*B[0]) % p
        expected.append((x, y, power))
    assert product == norm
    observed = sorted((z["point"][0], z["point"][1], z["multiplicity"])
                      for z in case["zeros"])
    assert sorted(expected) == observed
    assert sorted(unresolved) == sorted((tuple(z["norm_factor"]), z["exponent"])
                                        for z in case["unresolved"])
    assert case["rational_degree"] == sum(e for _, _, e in expected)
    assert case["fully_rational"] == (not unresolved)
    row, points, signs = {}, {}, {}
    for x, y, multiplicity in expected:
        key, sign = str(x), 1 if y < p-y else -1
        row[key] = row.get(key, 0)+sign*multiplicity
        points[key] = (x, min(y, p-y))
        signs.setdefault(key, [0, 0])[sign < 0] += multiplicity
    row = {k: c for k, c in row.items() if c}
    assert row == case["row"]
    assert sum(min(values) for values in signs.values()) == case["inverse_pairs"]
    zeros = Counter({(x, y): multiplicity for x, y, multiplicity in expected})
    assert all(zeros[tuple(point)] >= count for point, count in
               Counter(tuple(P) for P in case.get("declared_anchors", [])).items())
    if case["fully_rational"]:
        Jacobian(p, a, r).check_row(row, points)
    return points


def rank(matrix, modulus):
    # Fraction-free forward elimination; deliberately no sparse reducer.
    values = [[int(c) % modulus for c in row] for row in matrix]
    height, width = 0, len(values[0]) if values else 0
    for column in range(width):
        at = next((i for i in range(height, len(values)) if values[i][column]), None)
        if at is None:
            continue
        values[height], values[at] = values[at], values[height]
        pivot = values[height][column]
        for i in range(height+1, len(values)):
            factor = values[i][column]
            if factor:
                values[i] = [(pivot*u-factor*v) % modulus
                             for u, v in zip(values[i], values[height])]
        height += 1
        if height == len(values):
            break
    return height


def nullspace(matrix, width, modulus):
    # A dense RREF oracle, separate from the streaming pivot/DAG algorithm.
    values = [[int(c) % modulus for c in row] for row in matrix]
    pivots, height = [], 0
    for column in range(width):
        at = next((i for i in range(height, len(values)) if values[i][column]), None)
        if at is None:
            continue
        values[height], values[at] = values[at], values[height]
        inverse = pow(values[height][column], -1, modulus)
        values[height] = [inverse*c % modulus for c in values[height]]
        for i in range(len(values)):
            if i != height and values[i][column]:
                factor = values[i][column]
                values[i] = [(u-factor*v) % modulus
                             for u, v in zip(values[i], values[height])]
        pivots.append(column)
        height += 1
        if height == len(values):
            break
    basis = []
    for free in range(width):
        if free in pivots:
            continue
        vector = [0]*width
        vector[free] = 1
        for i, pivot in enumerate(pivots):
            vector[pivot] = -values[i][free] % modulus
        basis.append(vector)
    return basis


def check_graph(rows, base, certificate, modulus, points=None, curve=None):
    base = set(base)
    columns = sorted({key for row in rows for key in row})
    outside = [key for key in columns if key not in base]
    inside = [key for key in columns if key in base]
    A = [[row.get(key, 0) for row in rows] for key in outside]
    D = [[row.get(key, 0) for key in columns] for row in rows]
    dense = nullspace(A, len(rows), modulus)
    assert rank(A, modulus) == certificate["outside_rank"]
    assert len(dense) == certificate["kernel_dimension"]
    assert len(certificate["witnesses"]) == len(certificate["cancelled_rows"])
    assert len(certificate["output_nodes"]) == len(certificate["witnesses"])
    # Independently evaluate the serialized arithmetic expression, rather
    # than trusting the producer's heap-based witness expansion.
    dag_vectors = []
    for at, node in enumerate(certificate["dag"]):
        vector = [0]*len(rows)
        if "input" in node:
            assert 0 <= node["input"] < len(rows)
            vector[node["input"]] = 1
        else:
            for factor, child in node["terms"]:
                assert 0 <= child < at
                vector = [(a+factor*b) % modulus
                          for a, b in zip(vector, dag_vectors[child])]
        dag_vectors.append(vector)
    for node, witness in zip(certificate["output_nodes"], certificate["witnesses"]):
        expected = [int(witness.get(i, witness.get(str(i), 0))) for i in range(len(rows))]
        assert dag_vectors[node] == expected
    witnesses, projected = [], []
    for coefficients, claimed in zip(certificate["witnesses"], certificate["cancelled_rows"]):
        coefficients = {int(i): int(c) for i, c in coefficients.items()}
        assert all(sum(c*rows[i].get(key, 0) for i, c in coefficients.items()) % modulus == 0
                   for key in outside)
        actual = {key: sum(c*rows[i].get(key, 0) for i, c in coefficients.items()) % modulus
                  for key in inside}
        actual = {key: c for key, c in actual.items() if c}
        assert actual == claimed
        witnesses.append([coefficients.get(i, 0) for i in range(len(rows))])
        projected.append([actual.get(key, 0) for key in inside])
        if points is not None:
            Jacobian(*curve).check_row(actual, points)
    assert len(witnesses) == len(dense)
    assert rank(witnesses, modulus) == len(dense)
    final_rank = rank(projected, modulus)
    assert final_rank == rank(D, modulus)-rank(A, modulus)
    return {"input_rows": len(rows), "all_rank": rank(D, modulus),
            "outside_rank": rank(A, modulus), "kernel_dimension": len(dense),
            "cancelled_rank": final_rank, "zero_outputs": sum(not any(x) for x in projected),
            "independent_dense_kernel_agrees": True}
