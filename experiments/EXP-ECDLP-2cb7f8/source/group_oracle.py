"""Independent chord/tangent oracle. No incidence imports, inputs or relation tables.

Only explicit function calls perform finite computations. No import-time case runs.
"""
from collections import Counter
from itertools import combinations_with_replacement, product
from math import factorial


class Oracle:
    def __init__(self, p, curve_constant):
        self.p, self.b = p, curve_constant
        self.counts = Counter(addition=0, multiplication=0, inversion=0, equality=0)

    def addf(self, a, b):
        self.counts['addition'] += 1
        return (a + b) % self.p

    def subf(self, a, b):
        return self.addf(a, -b)

    def mulf(self, a, b):
        self.counts['multiplication'] += 1
        return (a * b) % self.p

    def eq(self, a, b):
        self.counts['equality'] += 1
        return a == b

    def inv(self, a):
        if self.eq(a % self.p, 0):
            raise ArithmeticError('group oracle division by zero')
        self.counts['inversion'] += 1
        value = pow(a, -1, self.p)
        if not self.eq(self.mulf(a, value), 1):
            raise ArithmeticError('group oracle inverse verification')
        return value

    def contains(self, point):
        if point is None:
            return True
        x, y = point
        if any(type(v) is not int or not 0 <= v < self.p for v in point):
            return False
        rhs = self.addf(self.addf(self.mulf(self.mulf(x, x), x), x), self.b)
        return self.eq(self.mulf(y, y), rhs)

    def points(self):
        return [None] + [(x, y) for x in range(self.p) for y in range(self.p)
                         if self.contains((x, y))]

    def neg(self, point):
        return None if point is None else (point[0], self.subf(0, point[1]))

    def add(self, left, right):
        if left is None:
            return right
        if right is None:
            return left
        x, y = left
        u, v = right
        if self.eq(x, u):
            if self.eq(self.addf(y, v), 0):
                return None
            numerator = self.addf(self.mulf(3, self.mulf(x, x)), 1)
            denominator = self.mulf(2, y)
        else:
            numerator, denominator = self.subf(v, y), self.subf(u, x)
        slope = self.mulf(numerator, self.inv(denominator))
        rx = self.subf(self.subf(self.mulf(slope, slope), x), u)
        ry = self.subf(self.mulf(slope, self.subf(x, rx)), y)
        return rx, ry

    def sum4(self, points):
        if len(points) != 4:
            raise ValueError('oracle requires four points')
        return self.add(self.add(self.add(points[0], points[1]), points[2]), points[3])

    def audit(self, points):
        failures = []
        for i, a in enumerate(points):
            if not self.contains(a) or self.add(None, a) != a or self.add(a, None) != a:
                failures.append({'kind': 'membership_identity', 'point': i})
            if self.add(a, self.neg(a)) is not None:
                failures.append({'kind': 'inverse', 'point': i})
        # Check closure before the independent all-triple associativity test.
        point_set = set(points)
        for i, j in product(range(len(points)), repeat=2):
            if self.add(points[i], points[j]) not in point_set:
                failures.append({'kind': 'closure', 'indices': [i, j]})
        for i, j, k in product(range(len(points)), repeat=3):
            left = self.add(self.add(points[i], points[j]), points[k])
            right = self.add(points[i], self.add(points[j], points[k]))
            if left != right:
                failures.append({'kind': 'associativity', 'indices': [i, j, k],
                                 'left': left, 'right': right})
        return {'passed': not failures, 'failures': failures,
                'associativity_triples': len(points) ** 3}

    def divisors(self, points):
        for indices in combinations_with_replacement(range(len(points)), 4):
            result = self.sum4([points[i] for i in indices])
            yield indices, result

    def ordered_histogram(self, points):
        lookup = {point: i for i, point in enumerate(points)}
        histogram = Counter()
        for i, j, k in product(range(len(points)), repeat=3):
            fourth = self.neg(self.add(self.add(points[i], points[j]), points[k]))
            histogram[tuple(sorted((i, j, k, lookup[fourth])))] += 1
        return histogram


def orbit_weight(divisor):
    denominator = 1
    for multiplicity in Counter(divisor).values():
        denominator *= factorial(multiplicity)
    return factorial(4) // denominator
