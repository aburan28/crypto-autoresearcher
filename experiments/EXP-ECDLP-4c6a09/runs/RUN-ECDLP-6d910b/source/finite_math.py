#!/usr/bin/env python3
"""Counted public short-Weierstrass arithmetic and modular relation algebra."""
import itertools
from collections import Counter

class Curve:
    def __init__(self, p, a, b):
        self.p, self.a, self.b = p, a % p, b % p
        self.count = Counter()

    def mult_field(self, a, b):
        self.count['field_multiplications'] += 1
        return a * b % self.p

    def inv(self, a):
        self.count['field_inversions'] += 1
        return pow(a, -1, self.p)

    def on_curve(self, point):
        return point is None or (point[1] ** 2 - point[0] ** 3 - self.a * point[0] - self.b) % self.p == 0

    def neg(self, point):
        return None if point is None else (point[0], -point[1] % self.p)

    def add(self, u, v):
        self.count['group_calls'] += 1
        if u is None:
            self.count['identity_returns'] += 1
            return v
        if v is None:
            self.count['identity_returns'] += 1
            return u
        x, y = u
        xx, yy = v
        if x == xx:
            if (y + yy) % self.p == 0:
                self.count['inverse_returns'] += 1
                return None
            assert y == yy
            self.count['doublings'] += 1
            numerator = (self.mult_field(3, self.mult_field(x, x)) + self.a) % self.p
            denominator = self.mult_field(2, y)
        else:
            self.count['additions'] += 1
            numerator, denominator = (yy - y) % self.p, (xx - x) % self.p
        slope = self.mult_field(numerator, self.inv(denominator))
        xxx = (self.mult_field(slope, slope) - x - xx) % self.p
        yyy = (self.mult_field(slope, x - xxx) - y) % self.p
        return xxx, yyy

    def mul(self, point, n):
        self.count['scalar_multiplications'] += 1
        if n < 0:
            return self.mul(self.neg(point), -n)
        out = None
        while n:
            if n & 1:
                out = self.add(out, point)
            n >>= 1
            if n:
                point = self.add(point, point)
        return out

    def combination(self, points, coefficients):
        out = None
        for p, c in zip(points, coefficients, strict=True):
            if c:
                out = self.add(out, self.mul(p, c))
        return out

def gray_vectors(dimension, bound):
    """One adjacent radix digit changes per step, with zero as the first digit."""
    digits = [0] + [z for j in range(1, bound + 1) for z in (j, -j)]
    indices, directions = [0] * dimension, [1] * dimension
    yield tuple(0 for _ in range(dimension)), None
    while True:
        j = dimension - 1
        while j >= 0 and not 0 <= indices[j] + directions[j] < len(digits):
            directions[j] = -directions[j]
            j -= 1
        if j < 0:
            return
        old = digits[indices[j]]
        indices[j] += directions[j]
        yield tuple(digits[x] for x in indices), (j, digits[indices[j]] - old)

def grid_points(ec, seeds, bound):
    differences = sorted({delta for _, change in gray_vectors(1, bound) if change
                          for delta in (change[1], -change[1])})
    steps = [{d: ec.mul(point, d) for d in differences} for point in seeds]
    current = None
    for coefficients, change in gray_vectors(len(seeds), bound):
        if change:
            j, delta = change
            current = ec.add(current, steps[j][delta])
        yield coefficients, current

class Relations:
    """RREF over a prime field, including the right-hand side. No oracle logs."""
    def __init__(self, modulus, dimension):
        self.modulus, self.dimension = modulus, dimension
        self.rows = {}
        self.count = Counter()

    @property
    def rank(self):
        return len(self.rows)

    def _subtract(self, a, b, factor):
        self.count['scalar_field_multiplications'] += len(a)
        return [(x - factor * y) % self.modulus for x, y in zip(a, b, strict=True)]

    def add(self, vector, rhs):
        assert len(vector) == self.dimension
        row = [x % self.modulus for x in vector] + [rhs % self.modulus]
        for pivot in sorted(self.rows):
            if row[pivot]:
                row = self._subtract(row, self.rows[pivot], row[pivot])
        pivot = next((j for j, v in enumerate(row[:-1]) if v), None)
        if pivot is None:
            if row[-1]:
                raise ValueError('Inconsistent relation system')
            self.count['dependent_equations'] += 1
            return False
        scale = pow(row[pivot], -1, self.modulus)
        self.count['scalar_field_inversions'] += 1
        self.count['scalar_field_multiplications'] += len(row)
        row = [x * scale % self.modulus for x in row]
        for p, previous in list(self.rows.items()):
            if previous[pivot]:
                self.rows[p] = self._subtract(previous, row, previous[pivot])
        self.rows[pivot] = row
        self.count['independent_equations'] += 1
        return True

    def value(self, vector):
        """Return the uniquely implied value of a linear functional, or None."""
        row = [x % self.modulus for x in vector] + [0]
        for pivot in sorted(self.rows):
            if row[pivot]:
                row = self._subtract(row, self.rows[pivot], row[pivot])
        return -row[-1] % self.modulus if not any(row[:-1]) else None

    def with_target(self):
        out = Relations(self.modulus, self.dimension + 1)
        for row in self.rows.values():
            out.add(row[:-1] + [0], row[-1])
        out.count.clear()
        return out

def split_coefficients(coefficients, known):
    unknown = [c for i, c in enumerate(coefficients) if i not in known]
    constant = sum(c * known[i] for i, c in enumerate(coefficients) if i in known)
    return unknown, constant

def self_controls():
    ec = Curve(101, 2, 3)
    points = [None] + [(x, y) for x in range(101) for y in range(101)
                       if (y*y - x*x*x - 2*x - 3) % 101 == 0]
    for p in points:
        assert ec.on_curve(ec.add(p, ec.neg(p)))
        assert ec.add(p, ec.neg(p)) is None
        assert ec.mul(p, 2) == ec.add(p, p)
    # A factor-base equation alone and a target equation alone do not fix q.
    system = Relations(101, 2)
    assert system.add([2, -1], 7)
    assert system.value([0, 1]) is None
    assert not system.add([4, -2], 14)
    assert system.add([1, 0], 11)
    assert system.value([0, 1]) == 15
    contradiction = False
    try:
        system.add([0, 0], 1)
    except ValueError:
        contradiction = True
    assert contradiction
    for dim in range(1, 5):
        for bound in (1, 2, 4):
            vectors = [v for v, _ in gray_vectors(dim, bound)]
            assert len(set(vectors)) == len(vectors) == (2 * bound + 1) ** dim
            assert set(vectors) == set(itertools.product(range(-bound, bound + 1), repeat=dim))
            assert all(sum(a != b for a, b in zip(u, v)) == 1 for u, v in zip(vectors, vectors[1:]))
    return {'passed': True, 'finite_curve': {'p': 101, 'A': 2, 'B': 3, 'point_count': len(points)},
            'checks': ['inverse and doubling on every small-curve point', 'Gray box equals full Cartesian box',
                       'rank-deficient target equation cannot recover scalar', 'dependent relation adds no rank',
                       'two independent equations recover correct scalar', 'contradictory relation is rejected']}
